#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Red Team Mastery Tracker — backend (Flask + SQLite, login accounts).

Owns identity and persistence so users can be managed centrally:
  * real accounts (username + scrypt-hashed password), server-enforced admin flag
  * per-account progress, shared admin-managed config (tasks / trophies / challenges)
  * admin dashboard endpoints to create / delete / reset / rename / (de)promote users
    and set passwords — the browser never decides who is admin

Security notes:
  * passwords hashed with werkzeug scrypt; never stored or returned in plaintext
  * session cookie: HttpOnly + SameSite=Lax (+ Secure when RTT_SECURE=1 behind TLS)
  * CSRF: state-changing /api calls require the X-CSRF-Token issued at login/state
  * server-side authorization on every admin/self action; login throttling
  * binds to 127.0.0.1 by default — do NOT expose without TLS + RTT_SECURE=1

Run:      ./run.sh                      (or  .venv/bin/python server.py)
CLI:      server.py --create-admin U P
          server.py --set-password U P
          server.py --list-users
          server.py --import-legacy rt-tracker-all.json   (from the app's "Export ALL")
Env:      RTT_HOST RTT_PORT RTT_DB RTT_SECURE RTT_SESSION_HOURS RTT_ADMIN_USER RTT_ADMIN_PASS
"""
import os, re, json, time, sqlite3, secrets, argparse, logging
from collections import OrderedDict
from functools import wraps
from datetime import datetime, timezone, timedelta
from flask import Flask, request, session, jsonify, g, send_from_directory, abort

APP_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.environ.get("RTT_DB", os.path.join(APP_DIR, "tracker.db"))
SECRET_FP = os.path.join(APP_DIR, ".secret_key")
MAX_BODY  = 4 * 1024 * 1024          # 4 MB cap on request bodies
USER_RE   = re.compile(r"^[A-Za-z0-9_.\-]{2,32}$")
MIN_PW    = 6
MAX_PW    = 1024

# ---- login throttle (in-memory; process-local, bounded) ----
_FAILS = OrderedDict()               # key (scope, ip, user) -> [timestamps]
_WINDOW, _MAXFAIL, _MAXFAIL_IP = 300, 8, 40
_MAX_THROTTLE_KEYS = 10_000
SECURITY_LOG = logging.getLogger("rtt.security")
if not SECURITY_LOG.handlers:
    _security_handler = logging.StreamHandler()
    _security_handler.setFormatter(logging.Formatter("%(message)s"))
    SECURITY_LOG.addHandler(_security_handler)
SECURITY_LOG.setLevel(logging.INFO)
SECURITY_LOG.propagate = False

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _as_int(value, default=0, low=None, high=None):
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        number = default
    if low is not None: number = max(low, number)
    if high is not None: number = min(high, number)
    return number

def audit(event, outcome="ok", **fields):
    """Emit a redacted, structured security event without credentials or tokens."""
    record = {"ts": now_iso(), "event": event, "outcome": outcome}
    record.update({k: v for k, v in fields.items() if v is not None})
    SECURITY_LOG.info("%s", json.dumps(record, ensure_ascii=True, separators=(",", ":")))

# ---------------------------------------------------------------- db
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      username      TEXT UNIQUE NOT NULL COLLATE NOCASE,
      password_hash TEXT NOT NULL,
      is_admin      INTEGER NOT NULL DEFAULT 0,
      avatar        TEXT NOT NULL DEFAULT '🎯',
      created_at    TEXT NOT NULL,
      progress      TEXT NOT NULL DEFAULT '{}',
      auth_version  INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS config(
      id   INTEGER PRIMARY KEY CHECK(id=1),
      data TEXT NOT NULL
    );
    """)
    cols = {r[1] for r in con.execute("PRAGMA table_info(users)")}
    if "auth_version" not in cols:
        con.execute("ALTER TABLE users ADD COLUMN auth_version INTEGER NOT NULL DEFAULT 1")
    if con.execute("SELECT COUNT(*) FROM config").fetchone()[0] == 0:
        con.execute("INSERT INTO config(id,data) VALUES(1,?)", (json.dumps(_empty_config()),))
    con.commit(); con.close()

def _empty_config():
    return {"overrides": {}, "customTasks": [], "deleted": [],
            "customTrophies": [], "challenges": []}

def normalize_config(cfg):
    if not isinstance(cfg, dict):
        return _empty_config()

    def text(value, default="", limit=300):
        return (value if isinstance(value, str) else default)[:limit]

    def safe_id(value):
        return re.sub(r"[^A-Za-z0-9_.\-]", "_", text(value, "", 64))

    overrides = {}
    raw_overrides = cfg.get("overrides")
    if isinstance(raw_overrides, dict):
        for task_id, value in list(raw_overrides.items())[:1000]:
            if not isinstance(value, dict): continue
            tid = safe_id(str(task_id))
            if not tid: continue
            record = {}
            for key, limit in (("phase",100),("track",100),("cat",100),("title",300)):
                if isinstance(value.get(key), str): record[key] = text(value[key], "", limit)
            if "diff" in value: record["diff"] = _as_int(value.get("diff"), 1, 1, 5)
            if "xp" in value: record["xp"] = _as_int(value.get("xp"), 0, 0, 1_000_000)
            overrides[tid] = record

    custom_tasks = []
    if isinstance(cfg.get("customTasks"), list):
        for value in cfg["customTasks"][:1000]:
            if not isinstance(value, dict): continue
            tid = safe_id(value.get("id"))
            if not tid: continue
            custom_tasks.append({
                "id": tid, "phase": text(value.get("phase"), "Custom", 100),
                "track": text(value.get("track"), "Core", 100),
                "cat": text(value.get("cat"), "Learn", 100),
                "title": text(value.get("title"), "Untitled", 300),
                "diff": _as_int(value.get("diff"), 1, 1, 5),
                "xp": _as_int(value.get("xp"), 0, 0, 1_000_000),
            })

    trophies = []
    if isinstance(cfg.get("customTrophies"), list):
        for value in cfg["customTrophies"][:1000]:
            if not isinstance(value, dict): continue
            tid = safe_id(value.get("id"))
            if not tid: continue
            rule = value.get("rule") if isinstance(value.get("rule"), dict) else {"type": "manual"}
            rtype = rule.get("type") if rule.get("type") in {"manual","xp","level","tasks","phase","ids","all"} else "manual"
            if rtype == "ids": rvalue = [safe_id(x) for x in rule.get("value", [])[:500]] if isinstance(rule.get("value"), list) else []
            elif rtype == "phase": rvalue = text(rule.get("value"), "", 100)
            else: rvalue = _as_int(rule.get("value"), 0, 0, 10_000_000)
            tier = value.get("tier") if value.get("tier") in {"bronze","silver","gold","platinum"} else "bronze"
            trophies.append({
                "id": tid, "ico": text(value.get("ico"), "🏅", 8),
                "name": text(value.get("name"), "Trophy", 100),
                "desc": text(value.get("desc"), "", 300),
                "tier": tier,
                "rule": {"type": rtype, "value": rvalue},
                "challenge": bool(value.get("challenge")),
            })

    challenges = []
    if isinstance(cfg.get("challenges"), list):
        for value in cfg["challenges"][:1000]:
            if not isinstance(value, dict): continue
            cid = safe_id(value.get("id"))
            if not cid: continue
            goal_type = "count" if value.get("goalType") == "count" else "tasks"
            task_ids = ([safe_id(x) for x in value.get("taskIds", [])[:500]]
                        if isinstance(value.get("taskIds"), list) else [])
            challenges.append({
                "id": cid, "name": text(value.get("name"), "Challenge", 100),
                "desc": text(value.get("desc"), "", 300), "goalType": goal_type,
                "taskIds": [x for x in task_ids if x],
                "count": _as_int(value.get("count"), 0, 0, 10_000),
                "xp": _as_int(value.get("xp"), 0, 0, 1_000_000),
                "trophyId": safe_id(value.get("trophyId")),
                "startedAt": _as_int(value.get("startedAt"), 0, 0),
                "days": _as_int(value.get("days"), 7, 1, 365),
                "active": bool(value.get("active")),
            })

    return {
        "overrides": overrides,
        "customTasks": custom_tasks,
        "deleted": [safe_id(str(x)) for x in (cfg.get("deleted") or [])][:1000]
                   if isinstance(cfg.get("deleted"), list) else [],
        "customTrophies": trophies,
        "challenges": challenges,
    }

def load_config(con):
    row = con.execute("SELECT data FROM config WHERE id=1").fetchone()
    try:
        cfg = json.loads(row["data"]) if row else {}
    except Exception:
        cfg = {}
    return normalize_config(cfg)

# ---------------------------------------------------------------- auth helpers
def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    row = get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not row or session.get("auth_version") != row["auth_version"]:
        session.clear()
        return None
    return row

def login_required(fn):
    @wraps(fn)
    def w(*a, **k):
        if not current_user():
            return jsonify(error="auth required"), 401
        return fn(*a, **k)
    return w

def admin_required(fn):
    @wraps(fn)
    def w(*a, **k):
        u = current_user()
        if not u:
            return jsonify(error="auth required"), 401
        if not u["is_admin"]:
            return jsonify(error="admin required"), 403
        return fn(*a, **k)
    return w

def _public_trophy_count(progress):
    raw_shown = progress.get("trophyShown")
    raw_granted = progress.get("granted")
    shown = {str(x) for x in raw_shown} if isinstance(raw_shown, list) else set()
    granted = ({str(k) for k, v in raw_granted.items() if v}
               if isinstance(raw_granted, dict) else set())
    return len(shown | granted)

def public_user(row, tasks=None, include_progress=False):
    d = {"id": row["id"], "name": row["username"], "username": row["username"],
         "avatar": row["avatar"], "isAdmin": bool(row["is_admin"])}
    prog = {}
    try:
        prog = json.loads(row["progress"] or "{}")
    except Exception:
        prog = {}
    if not isinstance(prog, dict):
        prog = {}
    d["trophyCount"] = _public_trophy_count(prog)
    if include_progress:
        d["progress"] = prog
    if tasks is not None:                            # F0d: authoritative per-user stats
        d["stats"] = compute_stats(prog, tasks)
    return d

def _failure_hits(key, now):
    hits = [x for x in _FAILS.get(key, []) if now - x < _WINDOW]
    if hits:
        _FAILS[key] = hits
        _FAILS.move_to_end(key)
    else:
        _FAILS.pop(key, None)
    return hits

def _prune_failures(now):
    while _FAILS:
        key, hits = next(iter(_FAILS.items()))
        if hits and now - hits[-1] < _WINDOW:
            break
        _FAILS.pop(key, None)
    while len(_FAILS) > _MAX_THROTTLE_KEYS:
        _FAILS.popitem(last=False)

def throttled(ip, user):
    t = time.time(); uname = (user or "").lower()
    _prune_failures(t)
    return (len(_failure_hits(("account", ip, uname), t)) >= _MAXFAIL or
            len(_failure_hits(("ip", ip, "*"), t)) >= _MAXFAIL_IP)

def note_fail(ip, user):
    t = time.time(); uname = (user or "").lower()
    for key in (("account", ip, uname), ("ip", ip, "*")):
        hits = _failure_hits(key, t)
        hits.append(t); _FAILS[key] = hits; _FAILS.move_to_end(key)
    _prune_failures(t)

def clear_fail(ip, user):
    _FAILS.pop(("account", ip, (user or "").lower()), None)

def valid_json_text(s, limit=MAX_BODY):
    if not isinstance(s, (dict, list)):
        return None
    t = json.dumps(s, ensure_ascii=False)
    if len(t.encode("utf-8")) > limit:
        return None
    return t

def json_object():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}

# ---------------------------------------------------------------- XP authority (F0)
# The server is the SOLE authority for XP/level and challenge awards. It reads task XP
# from config (never from the request), whitelists which progress fields a user may write,
# and computes the same leveling curve the client uses for offline mode.
try:
    from tasks_data import TASKS as _BUILTIN_TUPLES, RANKS as _RANKS, LEVEL_BASE as _LB, LEVEL_STEP as _LS
except Exception:                                    # degrade, don't crash, if the module moves
    _BUILTIN_TUPLES, _RANKS, _LB, _LS = [], [(1, "Initiate")], 200, 55

_LEAGUES = [(1,"Beginner"),(4,"Novice"),(8,"Skilled"),(12,"Advanced"),
            (16,"Expert"),(20,"Master"),(24,"Pro"),(28,"Legend")]
MIN_TS  = 1577836800000          # 2020-01-01 in epoch ms — reject anything older
SKEW_MS = 5 * 60 * 1000          # tolerate 5 min of clock skew on "now"
PROGRESS_MAX = int(os.environ.get("RTT_PROGRESS_MAX", str(1024 * 1024)))   # per-account cap (F0f)
WRITABLE_SELF = ("done","collapsed","achShown","trophyShown","personal","evidence","activity")
# server-owned, NEVER writable by a self PUT: bonusXp, granted, challengesDone, xp, level

def xp_for_diff(d):
    d = _as_int(d, 1, 1, 5);  return 50*d + 25*d*(d-1)

def cum_xp(L):
    c = 0
    for i in range(2, L+1): c += _LB + _LS*(i-1)
    return c

def level_from_xp(xp):
    L = 1
    while cum_xp(L+1) <= xp: L += 1
    return L

def rank_for(level):
    r = _RANKS[0][1]
    for lvl, name in _RANKS:
        if level >= lvl: r = name
        else: break
    return r

def league_for(level):
    n = _LEAGUES[0][1]
    for lvl, name in _LEAGUES:
        if level >= lvl: n = name
    return n

def effective_tasks(cfg):
    """Roadmap tasks the admin config actually exposes: builtins − deleted + overrides + custom."""
    deleted = set(cfg.get("deleted") or [])
    overrides = cfg.get("overrides") or {}
    tasks = {}
    for t in _BUILTIN_TUPLES:                        # (id, phase, track, cat, title, diff, xp)
        if t[0] in deleted: continue
        tasks[t[0]] = {"xp": int(t[6]), "diff": int(t[5]), "phase": t[1]}
    for tid, ov in overrides.items():
        if tid in tasks and isinstance(ov, dict):
            if "xp" in ov:   tasks[tid]["xp"]   = _as_int(ov["xp"], tasks[tid]["xp"], 0, 1_000_000)
            if "diff" in ov: tasks[tid]["diff"] = _as_int(ov["diff"], tasks[tid]["diff"], 1, 5)
            if isinstance(ov.get("phase"), str): tasks[tid]["phase"] = ov["phase"][:100]
    for ct in (cfg.get("customTasks") or []):
        raw_tid = ct.get("id")
        tid = str(raw_tid)[:64] if raw_tid else ""
        if tid and tid not in deleted:
            phase = ct.get("phase") if isinstance(ct.get("phase"), str) else "Custom"
            tasks[tid] = {"xp": _as_int(ct.get("xp"), 0, 0, 1_000_000),
                          "diff": _as_int(ct.get("diff"), 1, 1, 5), "phase": phase[:100]}
    return tasks

def _personal_xp_map(progress):
    return {p.get("id"): xp_for_diff(p.get("diff"))
            for p in (progress.get("personal") or [])
            if isinstance(p, dict) and p.get("id")}

def compute_stats(progress, tasks):
    """Authoritative {xp, level, rank, league, rmDone, rmTotal} from stored (trusted) progress."""
    done = progress.get("done") if isinstance(progress.get("done"), dict) else {}
    pmap = _personal_xp_map(progress)
    xp = 0
    for tid in done:
        if tid in tasks:   xp += tasks[tid]["xp"]
        elif tid in pmap:  xp += pmap[tid]
    xp += _as_int(progress.get("bonusXp"), 0, 0, 10_000_000)
    lvl = level_from_xp(xp)
    rm_done = sum(1 for tid in done if tid in tasks)
    return {"xp": xp, "level": lvl, "rank": rank_for(lvl), "league": league_for(lvl),
            "rmDone": rm_done, "rmTotal": len(tasks)}

def _bound_map(m, limit):     return dict(list(m.items())[:limit]) if isinstance(m, dict) else {}
def _bound_list(x, limit):    return x[:limit] if isinstance(x, list) else []

def sanitize_self_progress(stored, client, tasks, now_ms):
    """Merge only whitelisted fields from the client onto stored; server-owned fields survive.
    Fake task ids, forged timestamps, and self-awarded XP are dropped here."""
    out = dict(stored) if isinstance(stored, dict) else {}
    if not isinstance(out.get("granted"), dict): out["granted"] = {}
    if not isinstance(out.get("challengesDone"), dict): out["challengesDone"] = {}
    out["bonusXp"] = _as_int(out.get("bonusXp"), 0, 0, 10_000_000)
    # personal first — done validation references personal ids; xp is recomputed, never trusted
    if isinstance(client.get("personal"), list):
        clean = []
        for p in client["personal"][:500]:
            if not isinstance(p, dict) or not p.get("id"): continue
            d = _as_int(p.get("diff"), 1, 1, 5)
            created_at = _as_int(p.get("createdAt"), now_ms, MIN_TS, now_ms + SKEW_MS)
            clean.append({"id": str(p["id"])[:64], "title": str(p.get("title") or "")[:300],
                          "cat": str(p.get("cat") or "Personal")[:60], "diff": d,
                          "xp": xp_for_diff(d), "createdAt": created_at})
        out["personal"] = clean
    pids = {p["id"] for p in out.get("personal", []) if isinstance(p, dict) and p.get("id")}
    if isinstance(client.get("done"), dict):
        cd = {}
        for tid, ts in client["done"].items():
            if tid not in tasks and tid not in pids:      # only real / own tasks
                continue
            try: ts = int(ts)
            except (TypeError, ValueError): continue
            if ts < MIN_TS or ts > now_ms + SKEW_MS:      # no forged past/future
                continue
            cd[tid] = ts
        out["done"] = cd
    if isinstance(client.get("collapsed"), dict):  out["collapsed"]   = _bound_map(client["collapsed"], 200)
    if isinstance(client.get("achShown"), list):   out["achShown"]    = _bound_list(client["achShown"], 200)
    if isinstance(client.get("trophyShown"), list):out["trophyShown"] = _bound_list(client["trophyShown"], 500)
    if isinstance(client.get("evidence"), dict):   out["evidence"]    = _bound_map(client["evidence"], 500)
    if isinstance(client.get("activity"), dict):   out["activity"]    = _bound_map(client["activity"], 400)
    if "_primed" in client:                        out["_primed"]     = bool(client["_primed"])
    return out

def _completed_in_window(progress, start, end, tasks):
    done = progress.get("done") if isinstance(progress.get("done"), dict) else {}
    pids = {p.get("id") for p in (progress.get("personal") or []) if isinstance(p, dict)}
    return sum(1 for tid, ts in done.items()
               if (tid in tasks or tid in pids) and isinstance(ts, int) and start <= ts <= end)

def evaluate_challenges(progress, cfg, tasks, now_ms):
    """Award bonus XP + trophies for met challenges — server-side, idempotent (no double-award)."""
    done = progress.get("done") if isinstance(progress.get("done"), dict) else {}
    if not isinstance(progress.get("challengesDone"), dict): progress["challengesDone"] = {}
    if not isinstance(progress.get("granted"), dict): progress["granted"] = {}
    cd = progress["challengesDone"]
    granted = progress["granted"]
    awarded = []
    for c in (cfg.get("challenges") or []):
        raw_cid = c.get("id")
        cid = str(raw_cid)[:64] if raw_cid is not None else ""
        if not c.get("active") or not cid or cid in cd: continue
        start = _as_int(c.get("startedAt"), 0, 0, now_ms + SKEW_MS)
        end = start + _as_int(c.get("days"), 7, 1, 365) * 86400000
        if now_ms > end: continue
        if c.get("goalType") == "count":
            need = _as_int(c.get("count"), 0, 0, 10_000)
            met = need > 0 and _completed_in_window(progress, start, end, tasks) >= need
        else:
            ids = c.get("taskIds") if isinstance(c.get("taskIds"), list) else []
            met = len(ids) > 0 and all(i in done for i in ids)
        if met:
            cd[cid] = now_ms
            current_bonus = _as_int(progress.get("bonusXp"), 0, 0, 10_000_000)
            progress["bonusXp"] = min(10_000_000, current_bonus + _as_int(c.get("xp"), 0, 0, 1_000_000))
            if c.get("trophyId"): granted[str(c["trophyId"])[:64]] = True
            awarded.append(str(c.get("name") or cid)[:200])
    return awarded

# ---------------------------------------------------------------- app
def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.update(
        MAX_CONTENT_LENGTH=MAX_BODY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=(os.environ.get("RTT_SECURE") == "1"),
        PERMANENT_SESSION_LIFETIME=timedelta(
            hours=max(1, int(os.environ.get("RTT_SESSION_HOURS", "12")))),
        SECRET_KEY=_load_secret(),
    )

    @app.after_request
    def sec_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        if app.config["SESSION_COOKIE_SECURE"]:
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return resp

    @app.errorhandler(413)
    def too_large(e):                                # F0f: oversized body -> JSON 413
        return jsonify(error="payload too large"), 413

    @app.before_request
    def csrf_guard():
        p = request.path
        if p.startswith("/api/") and p != "/api/login" and request.method not in ("GET", "HEAD", "OPTIONS"):
            if request.headers.get("X-CSRF-Token", "") != session.get("csrf", "\0"):
                return jsonify(error="bad csrf token"), 403

    @app.teardown_appcontext
    def close_db(exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # ---- static ----
    @app.get("/")
    def index():
        resp = send_from_directory(APP_DIR, "index.html")
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.get("/health")
    def health():
        return jsonify(ok=True)

    # ---- auth ----
    @app.post("/api/login")
    def login():
        ip = request.remote_addr or "?"
        data = json_object()
        raw_username = data.get("username")
        username = raw_username.strip() if isinstance(raw_username, str) else ""
        password = data.get("password")
        if not isinstance(password, str) or len(password) > MAX_PW:
            audit("login", "denied", ip=ip, username=username[:32], reason="invalid_length")
            return jsonify(error="invalid username or password"), 401
        if throttled(ip, username):
            audit("login", "throttled", ip=ip, username=username[:32])
            return jsonify(error="too many attempts, wait a few minutes"), 429
        row = get_db().execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        from werkzeug.security import check_password_hash
        if not row or not check_password_hash(row["password_hash"], password):
            note_fail(ip, username)
            audit("login", "denied", ip=ip, username=username[:32])
            return jsonify(error="invalid username or password"), 401
        clear_fail(ip, username)
        session.clear()
        session["uid"] = row["id"]
        session["auth_version"] = row["auth_version"]
        session["csrf"] = secrets.token_urlsafe(32)
        session.permanent = True
        audit("login", actor_id=row["id"], ip=ip)
        return jsonify(me=_me(row), csrf=session["csrf"])

    @app.post("/api/logout")
    @login_required
    def logout():
        actor = session.get("uid")
        session.clear()
        audit("logout", actor_id=actor, ip=request.remote_addr)
        return jsonify(ok=True)

    @app.get("/api/state")
    @login_required
    def state():
        con = get_db(); me = current_user()
        cfg = load_config(con); tasks = effective_tasks(cfg); now = int(time.time() * 1000)
        # evaluate the caller's challenges on read too, so awards apply even without a fresh PUT
        try: mprog = json.loads(me["progress"] or "{}")
        except Exception: mprog = {}
        if not isinstance(mprog, dict):
            mprog = {}
        if evaluate_challenges(mprog, cfg, tasks, now):
            con.execute("UPDATE users SET progress=? WHERE id=?",
                        (json.dumps(mprog, ensure_ascii=False), me["id"])); con.commit()
            me = current_user()
        may_manage = bool(me["is_admin"])
        users = {str(r["id"]): public_user(
                    r, tasks, include_progress=(may_manage or r["id"] == me["id"]))
                 for r in con.execute("SELECT * FROM users ORDER BY id")}
        return jsonify(me={**_me(me), "stats": compute_stats(mprog, tasks)},
                       users=users, config=cfg, csrf=session.get("csrf"))

    # ---- self ----
    @app.put("/api/me/progress")
    @login_required
    def me_progress():
        client = json_object().get("progress")
        if not isinstance(client, dict):
            return jsonify(error="invalid progress payload"), 400
        con = get_db(); me = current_user()
        try: stored = json.loads(me["progress"] or "{}")
        except Exception: stored = {}
        cfg = load_config(con); tasks = effective_tasks(cfg); now = int(time.time() * 1000)
        merged = sanitize_self_progress(stored, client, tasks, now)       # F0b/F0c: whitelist + validate
        awarded = evaluate_challenges(merged, cfg, tasks, now)            # F0e: server-side awards
        txt = json.dumps(merged, ensure_ascii=False)
        if len(txt.encode("utf-8")) > PROGRESS_MAX:                       # F0f
            return jsonify(error="progress too large"), 413
        con.execute("UPDATE users SET progress=? WHERE id=?", (txt, me["id"])); con.commit()
        return jsonify(ok=True, stats=compute_stats(merged, tasks), awarded=awarded,  # F0d: authoritative
                       server={"bonusXp": merged.get("bonusXp", 0), "granted": merged.get("granted", {}),
                               "challengesDone": merged.get("challengesDone", {})})

    @app.put("/api/me/avatar")
    @login_required
    def me_avatar():
        raw = json_object().get("avatar")
        av = (raw if isinstance(raw, str) and raw else "🎯")[:8]
        get_db().execute("UPDATE users SET avatar=? WHERE id=?", (av, session["uid"]))
        get_db().commit()
        return jsonify(ok=True)

    @app.post("/api/me/password")
    @login_required
    def me_password():
        from werkzeug.security import check_password_hash, generate_password_hash
        d = json_object()
        me = current_user()
        old = d.get("old")
        if not isinstance(old, str) or not check_password_hash(me["password_hash"], old):
            return jsonify(error="current password is wrong"), 403
        new = d.get("new")
        if not isinstance(new, str) or not (MIN_PW <= len(new) <= MAX_PW):
            return jsonify(error=f"new password must be {MIN_PW}-{MAX_PW} chars"), 400
        get_db().execute("UPDATE users SET password_hash=?, auth_version=auth_version+1 WHERE id=?",
                         (generate_password_hash(new), me["id"]))
        get_db().commit()
        audit("password_change", actor_id=me["id"], target_id=me["id"], ip=request.remote_addr)
        session.clear()
        return jsonify(ok=True, relogin=True)

    # ---- shared config (admin) ----
    @app.put("/api/config")
    @admin_required
    def put_config():
        d = json_object()
        cfg = _empty_config()
        for k in cfg:
            if k in d:
                cfg[k] = d[k]
        cfg = normalize_config(cfg)
        txt = valid_json_text(cfg)
        if txt is None:
            return jsonify(error="config too large / invalid"), 400
        get_db().execute("UPDATE config SET data=? WHERE id=1", (txt,))
        get_db().commit()
        audit("config_update", actor_id=session.get("uid"), ip=request.remote_addr)
        return jsonify(ok=True)

    # ---- admin user management ----
    @app.post("/api/admin/users")
    @admin_required
    def admin_create():
        from werkzeug.security import generate_password_hash
        d = json_object()
        raw_username = d.get("username")
        username = raw_username.strip() if isinstance(raw_username, str) else ""
        password = d.get("password")
        if not USER_RE.match(username):
            return jsonify(error="username must be 2-32 chars: letters, digits, . _ -"), 400
        if not isinstance(password, str) or not (MIN_PW <= len(password) <= MAX_PW):
            return jsonify(error=f"password must be {MIN_PW}-{MAX_PW} chars"), 400
        con = get_db()
        if con.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            return jsonify(error="username already exists"), 409
        raw_avatar = d.get("avatar")
        avatar = (raw_avatar if isinstance(raw_avatar, str) and raw_avatar else "🎯")[:8]
        con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,?,?,?,?)",
                    (username, generate_password_hash(password), 1 if d.get("is_admin") else 0,
                     avatar, now_iso(), "{}"))
        con.commit()
        audit("user_create", actor_id=session.get("uid"), target=username,
              admin=bool(d.get("is_admin")), ip=request.remote_addr)
        return jsonify(ok=True)

    @app.delete("/api/admin/users/<int:uid>")
    @admin_required
    def admin_delete(uid):
        con = get_db(); me = current_user()
        if uid == me["id"]:
            return jsonify(error="you cannot delete your own account"), 400
        if _is_last_admin(con, uid):
            return jsonify(error="cannot delete the last admin"), 400
        con.execute("DELETE FROM users WHERE id=?", (uid,)); con.commit()
        audit("user_delete", actor_id=me["id"], target_id=uid, ip=request.remote_addr)
        return jsonify(ok=True)

    @app.post("/api/admin/users/<int:uid>/reset")
    @admin_required
    def admin_reset(uid):
        get_db().execute("UPDATE users SET progress='{}' WHERE id=?", (uid,))
        get_db().commit()
        audit("progress_reset", actor_id=session.get("uid"), target_id=uid, ip=request.remote_addr)
        return jsonify(ok=True)

    @app.post("/api/admin/users/<int:uid>/password")
    @admin_required
    def admin_setpw(uid):
        from werkzeug.security import generate_password_hash
        pw = json_object().get("password")
        if not isinstance(pw, str) or not (MIN_PW <= len(pw) <= MAX_PW):
            return jsonify(error=f"password must be {MIN_PW}-{MAX_PW} chars"), 400
        r = get_db().execute("UPDATE users SET password_hash=?, auth_version=auth_version+1 WHERE id=?",
                             (generate_password_hash(pw), uid))
        get_db().commit()
        if r.rowcount:
            audit("password_reset", actor_id=session.get("uid"), target_id=uid, ip=request.remote_addr)
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    @app.post("/api/admin/users/<int:uid>/admin")
    @admin_required
    def admin_setrole(uid):
        want = bool(json_object().get("is_admin"))
        con = get_db()
        if not want and _is_last_admin(con, uid):
            return jsonify(error="cannot demote the last admin"), 400
        r = con.execute("UPDATE users SET is_admin=? WHERE id=?", (1 if want else 0, uid))
        con.commit()
        if r.rowcount:
            audit("role_change", actor_id=session.get("uid"), target_id=uid,
                  admin=want, ip=request.remote_addr)
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    @app.post("/api/admin/users/<int:uid>/rename")
    @admin_required
    def admin_rename(uid):
        raw = json_object().get("username")
        new = raw.strip() if isinstance(raw, str) else ""
        if not USER_RE.match(new):
            return jsonify(error="invalid username"), 400
        con = get_db()
        if con.execute("SELECT 1 FROM users WHERE username=? AND id<>?", (new, uid)).fetchone():
            return jsonify(error="username already exists"), 409
        r = con.execute("UPDATE users SET username=? WHERE id=?", (new, uid)); con.commit()
        if r.rowcount:
            audit("user_rename", actor_id=session.get("uid"), target_id=uid, ip=request.remote_addr)
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    @app.put("/api/admin/users/<int:uid>/progress")
    @admin_required
    def admin_progress(uid):
        progress = json_object().get("progress")
        if not isinstance(progress, dict):
            return jsonify(error="invalid progress payload"), 400
        txt = valid_json_text(progress)
        if txt is None:
            return jsonify(error="invalid progress payload"), 400
        r = get_db().execute("UPDATE users SET progress=? WHERE id=?", (txt, uid))
        get_db().commit()
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    # ---- admin bulk ----
    @app.get("/api/admin/export")
    @admin_required
    def admin_export():
        con = get_db()
        users = [dict(r) for r in con.execute("SELECT * FROM users ORDER BY id")]
        audit("admin_export", actor_id=session.get("uid"), ip=request.remote_addr)
        return jsonify(version=2, exported_at=now_iso(), users=users, config=load_config(con))

    @app.post("/api/admin/wipe")
    @admin_required
    def admin_wipe():
        con = get_db(); me = current_user()
        con.execute("DELETE FROM users WHERE id<>?", (me["id"],))
        con.execute("UPDATE users SET progress='{}' WHERE id=?", (me["id"],))
        con.execute("UPDATE config SET data=? WHERE id=1", (json.dumps(_empty_config()),))
        con.commit()
        audit("admin_wipe", actor_id=me["id"], ip=request.remote_addr)
        return jsonify(ok=True)

    @app.post("/api/admin/import-legacy")
    @admin_required
    def admin_import_legacy():
        """Seed accounts + config from the browser app's 'Export ALL' (rt-tracker-all.json).
        Accounts start non-admin with unknown random passwords until an admin explicitly
        sets each password. Existing usernames are skipped."""
        from werkzeug.security import generate_password_hash
        d = json_object()
        con = get_db(); created = 0
        legacy_users = d.get("users")
        if not isinstance(legacy_users, dict):
            return jsonify(error="invalid legacy users"), 400
        for u in legacy_users.values():
            if not isinstance(u, dict):
                continue
            raw_name = u.get("name")
            safe_name = raw_name if isinstance(raw_name, str) else "user"
            name = re.sub(r"[^A-Za-z0-9_.\-]", "_", safe_name)[:32] or "user"
            if len(name) < 2:
                name = ("u_" + name)[:32]
            if con.execute("SELECT 1 FROM users WHERE username=?", (name,)).fetchone():
                continue
            imported_progress = u.get("progress")
            if not isinstance(imported_progress, dict):
                imported_progress = {}
            prog = json.dumps(imported_progress, ensure_ascii=False)
            disabled_password = secrets.token_urlsafe(32)
            raw_avatar = u.get("avatar")
            avatar = (raw_avatar if isinstance(raw_avatar, str) and raw_avatar else "🎯")[:8]
            con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,?,?,?,?)",
                        (name, generate_password_hash(disabled_password), 0,
                         avatar, now_iso(), prog))
            created += 1
        cfg = {k: d.get(k) for k in _empty_config() if k in d}
        if cfg:
            merged = normalize_config(cfg)
            con.execute("UPDATE config SET data=? WHERE id=1", (json.dumps(merged, ensure_ascii=False),))
        con.commit()
        audit("legacy_import", actor_id=session.get("uid"), created=created, ip=request.remote_addr)
        return jsonify(ok=True, created=created,
                       note="imported accounts are disabled until an admin sets each password")

    return app

def _me(row):
    return {"id": row["id"], "username": row["username"],
            "isAdmin": bool(row["is_admin"]), "avatar": row["avatar"]}

def _is_last_admin(con, uid):
    r = con.execute("SELECT is_admin FROM users WHERE id=?", (uid,)).fetchone()
    if not r or not r["is_admin"]:
        return False
    return con.execute("SELECT COUNT(*) FROM users WHERE is_admin=1").fetchone()[0] <= 1

def _load_secret():
    if os.path.exists(SECRET_FP):
        return open(SECRET_FP, "rb").read()
    key = secrets.token_bytes(32)
    with open(SECRET_FP, "wb") as f:
        f.write(key)
    try:
        os.chmod(SECRET_FP, 0o600)
    except OSError:
        pass
    return key

# ---------------------------------------------------------------- seeding / cli
def seed_admin_if_empty():
    con = sqlite3.connect(DB_PATH)
    n = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if n == 0:
        from werkzeug.security import generate_password_hash
        user = os.environ.get("RTT_ADMIN_USER", "admin")
        pw   = os.environ.get("RTT_ADMIN_PASS") or secrets.token_urlsafe(9)
        con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,1,?,?,?)",
                    (user, generate_password_hash(pw), "👑", now_iso(), "{}"))
        con.commit()
        print("=" * 60)
        print(" First run — created admin account:")
        print(f"   username: {user}")
        print(f"   password: {pw}")
        print(" Log in, then change it (top bar ▸ your name ▸ password),")
        print(" or set RTT_ADMIN_USER / RTT_ADMIN_PASS before first run.")
        print("=" * 60)
    con.close()

def cli_create_admin(u, p):
    from werkzeug.security import generate_password_hash
    if not USER_RE.match(u) or not (MIN_PW <= len(p) <= MAX_PW):
        raise SystemExit("invalid username or password length")
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,1,?,?,?)",
                    (u, generate_password_hash(p), "👑", now_iso(), "{}"))
        con.commit(); print(f"created admin '{u}'")
    except sqlite3.IntegrityError:
        print(f"user '{u}' already exists — use --set-password")
    con.close()

def cli_set_password(u, p):
    from werkzeug.security import generate_password_hash
    if not (MIN_PW <= len(p) <= MAX_PW):
        raise SystemExit(f"password must be {MIN_PW}-{MAX_PW} chars")
    con = sqlite3.connect(DB_PATH)
    r = con.execute("UPDATE users SET password_hash=?, auth_version=auth_version+1 WHERE username=?",
                    (generate_password_hash(p), u))
    con.commit(); print(f"updated {r.rowcount} user(s)"); con.close()

def cli_list_users():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    for r in con.execute("SELECT id,username,is_admin,created_at FROM users ORDER BY id"):
        print(f"  #{r['id']:<3} {r['username']:<20} {'admin' if r['is_admin'] else 'user':<6} {r['created_at']}")
    con.close()

def cli_import_legacy(path):
    from werkzeug.security import generate_password_hash
    d = json.load(open(path, encoding="utf-8"))
    legacy_users = d.get("users") if isinstance(d, dict) else None
    if not isinstance(legacy_users, dict):
        raise SystemExit("invalid legacy users")
    con = sqlite3.connect(DB_PATH); made = 0
    for u in legacy_users.values():
        if not isinstance(u, dict):
            continue
        raw_name = u.get("name")
        safe_name = raw_name if isinstance(raw_name, str) else "user"
        name = re.sub(r"[^A-Za-z0-9_.\-]", "_", safe_name)[:32] or "user"
        if len(name) < 2:
            name = ("u_" + name)[:32]
        try:
            disabled_password = secrets.token_urlsafe(32)
            raw_avatar = u.get("avatar")
            avatar = (raw_avatar if isinstance(raw_avatar, str) and raw_avatar else "🎯")[:8]
            progress = u.get("progress") if isinstance(u.get("progress"), dict) else {}
            con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,?,?,?,?)",
                        (name, generate_password_hash(disabled_password), 0,
                         avatar, now_iso(), json.dumps(progress)))
            made += 1
        except sqlite3.IntegrityError:
            print(f"  skip existing '{name}'")
    cfg = {k: d.get(k) for k in _empty_config() if k in d}
    if cfg:
        merged = normalize_config(cfg)
        con.execute("UPDATE config SET data=? WHERE id=1", (json.dumps(merged),))
    con.commit(); con.close()
    print(f"imported {made} disabled account(s); set each password with --set-password")

def main():
    ap = argparse.ArgumentParser(description="Red Team Mastery Tracker backend")
    ap.add_argument("--create-admin", nargs=2, metavar=("USER", "PASS"))
    ap.add_argument("--set-password", nargs=2, metavar=("USER", "PASS"))
    ap.add_argument("--import-legacy", metavar="FILE")
    ap.add_argument("--list-users", action="store_true")
    ap.add_argument("--host", default=os.environ.get("RTT_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("RTT_PORT", "8000")))
    args = ap.parse_args()

    init_db()
    if args.create_admin:  return cli_create_admin(*args.create_admin)
    if args.set_password:  return cli_set_password(*args.set_password)
    if args.import_legacy: return cli_import_legacy(args.import_legacy)
    if args.list_users:    return cli_list_users()

    seed_admin_if_empty()
    app = create_app()
    print(f"Red Team Tracker on http://{args.host}:{args.port}  (db: {DB_PATH})")
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
