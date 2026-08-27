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
Env:      RTT_HOST RTT_PORT RTT_DB RTT_SECURE RTT_ADMIN_USER RTT_ADMIN_PASS
"""
import os, re, json, time, sqlite3, secrets, argparse
from functools import wraps
from datetime import datetime, timezone
from flask import Flask, request, session, jsonify, g, send_from_directory, abort

APP_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.environ.get("RTT_DB", os.path.join(APP_DIR, "tracker.db"))
SECRET_FP = os.path.join(APP_DIR, ".secret_key")
MAX_BODY  = 4 * 1024 * 1024          # 4 MB cap on request bodies
USER_RE   = re.compile(r"^[A-Za-z0-9_.\-]{2,32}$")
MIN_PW    = 6

# ---- login throttle (in-memory; process-local) ----
_FAILS = {}                          # key (ip, user) -> [timestamps]
_WINDOW, _MAXFAIL = 300, 8

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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
      progress      TEXT NOT NULL DEFAULT '{}'
    );
    CREATE TABLE IF NOT EXISTS config(
      id   INTEGER PRIMARY KEY CHECK(id=1),
      data TEXT NOT NULL
    );
    """)
    if con.execute("SELECT COUNT(*) FROM config").fetchone()[0] == 0:
        con.execute("INSERT INTO config(id,data) VALUES(1,?)", (json.dumps(_empty_config()),))
    con.commit(); con.close()

def _empty_config():
    return {"overrides": {}, "customTasks": [], "deleted": [],
            "customTrophies": [], "challenges": []}

def load_config(con):
    row = con.execute("SELECT data FROM config WHERE id=1").fetchone()
    try:
        cfg = json.loads(row["data"]) if row else {}
    except Exception:
        cfg = {}
    base = _empty_config(); base.update(cfg or {}); return base

# ---------------------------------------------------------------- auth helpers
def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

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

def public_user(row, include_progress=True):
    d = {"id": row["id"], "name": row["username"], "username": row["username"],
         "avatar": row["avatar"], "isAdmin": bool(row["is_admin"])}
    if include_progress:
        try:
            d["progress"] = json.loads(row["progress"] or "{}")
        except Exception:
            d["progress"] = {}
    return d

def throttled(ip, user):
    k = (ip, (user or "").lower()); t = time.time()
    hits = [x for x in _FAILS.get(k, []) if t - x < _WINDOW]
    _FAILS[k] = hits
    return len(hits) >= _MAXFAIL

def note_fail(ip, user):
    k = (ip, (user or "").lower())
    _FAILS.setdefault(k, []).append(time.time())

def clear_fail(ip, user):
    _FAILS.pop((ip, (user or "").lower()), None)

def valid_json_text(s, limit=MAX_BODY):
    if not isinstance(s, (dict, list)):
        return None
    t = json.dumps(s, ensure_ascii=False)
    if len(t.encode("utf-8")) > limit:
        return None
    return t

# ---------------------------------------------------------------- app
def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.update(
        MAX_CONTENT_LENGTH=MAX_BODY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=(os.environ.get("RTT_SECURE") == "1"),
        SECRET_KEY=_load_secret(),
    )

    @app.after_request
    def sec_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

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
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if throttled(ip, username):
            return jsonify(error="too many attempts, wait a few minutes"), 429
        row = get_db().execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        from werkzeug.security import check_password_hash
        if not row or not check_password_hash(row["password_hash"], password):
            note_fail(ip, username)
            return jsonify(error="invalid username or password"), 401
        clear_fail(ip, username)
        session.clear()
        session["uid"] = row["id"]
        session["csrf"] = secrets.token_urlsafe(32)
        session.permanent = True
        return jsonify(me=_me(row), csrf=session["csrf"])

    @app.post("/api/logout")
    @login_required
    def logout():
        session.clear()
        return jsonify(ok=True)

    @app.get("/api/state")
    @login_required
    def state():
        con = get_db(); me = current_user()
        users = {str(r["id"]): public_user(r) for r in con.execute("SELECT * FROM users ORDER BY id")}
        return jsonify(me=_me(me), users=users, config=load_config(con), csrf=session.get("csrf"))

    # ---- self ----
    @app.put("/api/me/progress")
    @login_required
    def me_progress():
        data = request.get_json(silent=True) or {}
        txt = valid_json_text(data.get("progress"))
        if txt is None:
            return jsonify(error="invalid progress payload"), 400
        get_db().execute("UPDATE users SET progress=? WHERE id=?", (txt, session["uid"]))
        get_db().commit()
        return jsonify(ok=True)

    @app.put("/api/me/avatar")
    @login_required
    def me_avatar():
        av = ((request.get_json(silent=True) or {}).get("avatar") or "🎯")[:8]
        get_db().execute("UPDATE users SET avatar=? WHERE id=?", (av, session["uid"]))
        get_db().commit()
        return jsonify(ok=True)

    @app.post("/api/me/password")
    @login_required
    def me_password():
        from werkzeug.security import check_password_hash, generate_password_hash
        d = request.get_json(silent=True) or {}
        me = current_user()
        if not check_password_hash(me["password_hash"], d.get("old") or ""):
            return jsonify(error="current password is wrong"), 403
        new = d.get("new") or ""
        if len(new) < MIN_PW:
            return jsonify(error=f"new password must be >= {MIN_PW} chars"), 400
        get_db().execute("UPDATE users SET password_hash=? WHERE id=?",
                         (generate_password_hash(new), me["id"]))
        get_db().commit()
        return jsonify(ok=True)

    # ---- shared config (admin) ----
    @app.put("/api/config")
    @admin_required
    def put_config():
        d = request.get_json(silent=True) or {}
        cfg = _empty_config()
        for k in cfg:
            if k in d:
                cfg[k] = d[k]
        txt = valid_json_text(cfg)
        if txt is None:
            return jsonify(error="config too large / invalid"), 400
        get_db().execute("UPDATE config SET data=? WHERE id=1", (txt,))
        get_db().commit()
        return jsonify(ok=True)

    # ---- admin user management ----
    @app.post("/api/admin/users")
    @admin_required
    def admin_create():
        from werkzeug.security import generate_password_hash
        d = request.get_json(silent=True) or {}
        username = (d.get("username") or "").strip()
        password = d.get("password") or ""
        if not USER_RE.match(username):
            return jsonify(error="username must be 2-32 chars: letters, digits, . _ -"), 400
        if len(password) < MIN_PW:
            return jsonify(error=f"password must be >= {MIN_PW} chars"), 400
        con = get_db()
        if con.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            return jsonify(error="username already exists"), 409
        con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,?,?,?,?)",
                    (username, generate_password_hash(password), 1 if d.get("is_admin") else 0,
                     (d.get("avatar") or "🎯")[:8], now_iso(), "{}"))
        con.commit()
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
        return jsonify(ok=True)

    @app.post("/api/admin/users/<int:uid>/reset")
    @admin_required
    def admin_reset(uid):
        get_db().execute("UPDATE users SET progress='{}' WHERE id=?", (uid,))
        get_db().commit()
        return jsonify(ok=True)

    @app.post("/api/admin/users/<int:uid>/password")
    @admin_required
    def admin_setpw(uid):
        from werkzeug.security import generate_password_hash
        pw = (request.get_json(silent=True) or {}).get("password") or ""
        if len(pw) < MIN_PW:
            return jsonify(error=f"password must be >= {MIN_PW} chars"), 400
        r = get_db().execute("UPDATE users SET password_hash=? WHERE id=?",
                             (generate_password_hash(pw), uid))
        get_db().commit()
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    @app.post("/api/admin/users/<int:uid>/admin")
    @admin_required
    def admin_setrole(uid):
        want = bool((request.get_json(silent=True) or {}).get("is_admin"))
        con = get_db()
        if not want and _is_last_admin(con, uid):
            return jsonify(error="cannot demote the last admin"), 400
        r = con.execute("UPDATE users SET is_admin=? WHERE id=?", (1 if want else 0, uid))
        con.commit()
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    @app.post("/api/admin/users/<int:uid>/rename")
    @admin_required
    def admin_rename(uid):
        new = ((request.get_json(silent=True) or {}).get("username") or "").strip()
        if not USER_RE.match(new):
            return jsonify(error="invalid username"), 400
        con = get_db()
        if con.execute("SELECT 1 FROM users WHERE username=? AND id<>?", (new, uid)).fetchone():
            return jsonify(error="username already exists"), 409
        r = con.execute("UPDATE users SET username=? WHERE id=?", (new, uid)); con.commit()
        return jsonify(ok=True) if r.rowcount else (jsonify(error="no such user"), 404)

    @app.put("/api/admin/users/<int:uid>/progress")
    @admin_required
    def admin_progress(uid):
        txt = valid_json_text((request.get_json(silent=True) or {}).get("progress"))
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
        return jsonify(version=2, exported_at=now_iso(), users=users, config=load_config(con))

    @app.post("/api/admin/wipe")
    @admin_required
    def admin_wipe():
        con = get_db(); me = current_user()
        con.execute("DELETE FROM users WHERE id<>?", (me["id"],))
        con.execute("UPDATE users SET progress='{}' WHERE id=?", (me["id"],))
        con.execute("UPDATE config SET data=? WHERE id=1", (json.dumps(_empty_config()),))
        con.commit()
        return jsonify(ok=True)

    @app.post("/api/admin/import-legacy")
    @admin_required
    def admin_import_legacy():
        """Seed accounts + config from the browser app's 'Export ALL' (rt-tracker-all.json).
        Each old profile becomes an account whose password defaults to its username
        (admins must reset these). Existing usernames are skipped."""
        from werkzeug.security import generate_password_hash
        d = request.get_json(silent=True) or {}
        con = get_db(); created = 0
        for u in (d.get("users") or {}).values():
            name = re.sub(r"[^A-Za-z0-9_.\-]", "_", (u.get("name") or "user"))[:32] or "user"
            if len(name) < 2:
                name = ("u_" + name)[:32]
            if con.execute("SELECT 1 FROM users WHERE username=?", (name,)).fetchone():
                continue
            prog = json.dumps(u.get("progress") or {}, ensure_ascii=False)
            con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,?,?,?,?)",
                        (name, generate_password_hash(name), 1 if u.get("isAdmin") else 0,
                         (u.get("avatar") or "🎯")[:8], now_iso(), prog))
            created += 1
        cfg = {k: d.get(k) for k in _empty_config() if k in d}
        if cfg:
            merged = _empty_config(); merged.update(cfg)
            con.execute("UPDATE config SET data=? WHERE id=1", (json.dumps(merged, ensure_ascii=False),))
        con.commit()
        return jsonify(ok=True, created=created,
                       note="imported profiles use their username as a temporary password")

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
    con = sqlite3.connect(DB_PATH)
    r = con.execute("UPDATE users SET password_hash=? WHERE username=?", (generate_password_hash(p), u))
    con.commit(); print(f"updated {r.rowcount} user(s)"); con.close()

def cli_list_users():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
    for r in con.execute("SELECT id,username,is_admin,created_at FROM users ORDER BY id"):
        print(f"  #{r['id']:<3} {r['username']:<20} {'admin' if r['is_admin'] else 'user':<6} {r['created_at']}")
    con.close()

def cli_import_legacy(path):
    from werkzeug.security import generate_password_hash
    d = json.load(open(path, encoding="utf-8"))
    con = sqlite3.connect(DB_PATH); made = 0
    for u in (d.get("users") or {}).values():
        name = re.sub(r"[^A-Za-z0-9_.\-]", "_", (u.get("name") or "user"))[:32] or "user"
        try:
            con.execute("INSERT INTO users(username,password_hash,is_admin,avatar,created_at,progress) VALUES(?,?,?,?,?,?)",
                        (name, generate_password_hash(name), 1 if u.get("isAdmin") else 0,
                         (u.get("avatar") or "🎯")[:8], now_iso(), json.dumps(u.get("progress") or {})))
            made += 1
        except sqlite3.IntegrityError:
            print(f"  skip existing '{name}'")
    cfg = {k: d.get(k) for k in _empty_config() if k in d}
    if cfg:
        merged = _empty_config(); merged.update(cfg)
        con.execute("UPDATE config SET data=? WHERE id=1", (json.dumps(merged),))
    con.commit(); con.close()
    print(f"imported {made} account(s); temp password = username")

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
