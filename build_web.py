# -*- coding: utf-8 -*-
"""Generate a self-contained local web app (index.html) from tasks_data.TASKS.

Features:
  * XP, levels, operator ranks (from tasks_data) + friendly LEAGUE tiers
    (Beginner -> Legend).
  * Multiple local user profiles (switchable) with per-profile progress.
    The old single-user save (rt_tracker_v1) is migrated into a default
    admin profile the first time this v2 app runs.
  * Personal tasks: any user can add their own tasks; XP auto-scales with
    a 1-5 difficulty (harder = more XP).
  * Achievements (small badges) AND Trophies (a tiered milestone case).
  * Weekly challenges: admin picks roadmap tasks (or "any N this week"),
    sets a bonus-XP reward and a trophy; any profile that meets the goal
    inside the window is awarded automatically.
  * Admin panel (soft PIN gate, local-only): manage profiles, tasks/XP,
    trophies, challenges, and full data export/import.

Everything runs client-side in localStorage. No backend, no internet.
The admin PIN is a convenience gate for a shared machine, NOT real
access control.
"""
import json
from tasks_data import TASKS, RANKS, LEVEL_BASE, LEVEL_STEP

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

tasks_json = json.dumps([
    {"id": t[0], "phase": t[1], "track": t[2], "cat": t[3],
     "title": t[4], "diff": t[5], "xp": t[6]}
    for t in TASKS
])
ranks_json = json.dumps(RANKS)

# ---- Per-task GUIDES (beginner + pro), merged from three sources -------------
# Pro variant reuses the authored detail in details_data.DETAILS where present,
# otherwise guides_data.PRO; beginner variant comes from guides_data.BEGINNER.
try:
    from guides_data import BEGINNER as _BEGINNER, PRO as _PRO
except Exception:
    _BEGINNER, _PRO = {}, {}
try:
    from details_data import DETAILS as _DETAILS
except Exception:
    _DETAILS = {}

def _details_to_pro(d):
    return {
        "overview": d.get("why", ""),
        "steps": d.get("how", []),
        "tools": d.get("tools", []),
        "resources": d.get("resources", []),
        "doneWhen": d.get("doneWhen", ""),
        "pitfall": d.get("pitfall", ""),
    }

GUIDES = {}
for _t in TASKS:
    _id = _t[0]
    _pro = _PRO.get(_id) or (_details_to_pro(_DETAILS[_id]) if _id in _DETAILS else None)
    GUIDES[_id] = {"beginner": _BEGINNER.get(_id), "pro": _pro}
guides_json = json.dumps(GUIDES, ensure_ascii=False)

_have_beg = sum(1 for g in GUIDES.values() if g["beginner"])
_have_pro = sum(1 for g in GUIDES.values() if g["pro"])
print(f"GUIDES: {len(GUIDES)} tasks | beginner authored: {_have_beg} | pro authored: {_have_pro}")

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Red Team Mastery Tracker</title>
<style>
:root{
  --bg:#0b0f14; --panel:#111823; --panel2:#0e1520; --line:#1e2a3a;
  --txt:#c9d6e5; --muted:#6b7d95; --accent:#2f81f7; --accent2:#7aa2f7;
  --green:#2ea043; --greenb:#3fb950; --amber:#d29922; --red:#f85149;
  --gold:#e3b341; --purple:#a371f7; --shadow:0 8px 30px rgba(0,0,0,.5);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:radial-gradient(1200px 600px at 80% -10%, #12233b 0%, var(--bg) 55%) fixed;
  color:var(--txt); font-family:ui-monospace,"JetBrains Mono","SFMono-Regular",Menlo,Consolas,monospace;
  font-size:14px; line-height:1.5; padding-bottom:80px;
}
a{color:var(--accent2)}
.wrap{max-width:1120px;margin:0 auto;padding:22px 18px}
.mono{font-variant-numeric:tabular-nums}
.spacer{flex:1}

/* ---- top bar / profiles ---- */
.topbar{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.profile{display:flex;align-items:center;gap:9px;background:var(--panel);border:1px solid var(--line);
  border-radius:30px;padding:5px 14px 5px 6px}
.pav{width:30px;height:30px;border-radius:50%;background:#13233c;display:grid;place-items:center;font-size:16px}
.pinfo{display:flex;flex-direction:column;line-height:1.15}
.pinfo b{color:#fff;font-size:12.5px}
.pinfo small{color:var(--muted);font-size:10px}

/* ---- header / hero ---- */
.hero{background:linear-gradient(160deg,var(--panel),var(--panel2));border:1px solid var(--line);
  border-radius:16px;padding:20px 22px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;background:
  repeating-linear-gradient(90deg,transparent 0 38px,rgba(47,129,247,.04) 38px 39px);pointer-events:none}
.title{font-size:19px;font-weight:700;letter-spacing:.5px;color:#fff}
.title .b{color:var(--accent)}
.subtitle{color:var(--muted);font-size:12px;margin-top:2px}
.heroGrid{display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin-top:16px}
.levelBadge{display:flex;align-items:center;gap:14px}
.lvlRing{--p:0;width:78px;height:78px;border-radius:50%;flex:0 0 78px;
  background:conic-gradient(var(--accent) calc(var(--p)*1%), #1b2636 0);
  display:grid;place-items:center;position:relative}
.lvlRing::after{content:"";position:absolute;inset:6px;border-radius:50%;background:var(--panel)}
.lvlNum{position:relative;text-align:center;line-height:1}
.lvlNum b{font-size:26px;color:#fff;display:block}
.lvlNum span{font-size:8.5px;color:var(--muted);letter-spacing:1px}
.rankName{font-size:16px;font-weight:700;color:var(--gold)}
.rankSub{font-size:11px;color:var(--muted)}
.leaguePill{display:inline-block;margin-top:6px;font-size:10px;letter-spacing:1px;text-transform:uppercase;
  border:1px solid var(--muted);border-radius:20px;padding:1px 9px;color:var(--muted)}
.xpbarWrap{flex:1 1 260px;min-width:240px}
.xpbarTop{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-bottom:5px}
.xpbar{height:12px;border-radius:8px;background:#0a121d;border:1px solid var(--line);overflow:hidden}
.xpbar>i{display:block;height:100%;width:0;border-radius:8px;
  background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .6s cubic-bezier(.2,.8,.2,1)}

/* ---- stat cards ---- */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card .k{font-size:10.5px;color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.card .v{font-size:24px;font-weight:700;color:#fff;margin-top:4px}
.card .v small{font-size:13px;color:var(--muted);font-weight:400}
.card.good .v{color:var(--greenb)} .card.gold .v{color:var(--gold)}

/* ---- toolbar ---- */
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:22px 0 10px}
.toolbar input[type=search],select{background:var(--panel);color:var(--txt);border:1px solid var(--line);
  border-radius:9px;padding:8px 11px;font-family:inherit;font-size:13px;outline:none}
.toolbar input[type=search]{flex:1 1 220px;min-width:180px}
.toolbar input[type=search]:focus,select:focus{border-color:var(--accent)}
.btn{background:var(--panel);color:var(--txt);border:1px solid var(--line);border-radius:9px;
  padding:8px 12px;font-family:inherit;font-size:12.5px;cursor:pointer}
.btn:hover{border-color:var(--accent);color:#fff}
.btn.danger:hover{border-color:var(--red);color:var(--red)}
.btn.mini{padding:3px 7px;font-size:11px}

/* ---- phase sections ---- */
.phase{margin-top:18px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--panel2)}
.phaseHead{display:flex;align-items:center;gap:12px;padding:13px 16px;cursor:pointer;background:var(--panel);
  border-bottom:1px solid var(--line)}
.phaseHead:hover{background:#131c28}
.phaseHead .caret{color:var(--muted);transition:transform .2s;font-size:11px}
.phase.collapsed .caret{transform:rotate(-90deg)}
.phase.collapsed .phaseBody{display:none}
.phaseHead h3{margin:0;font-size:14px;color:#fff;letter-spacing:.3px}
.phaseHead .pmeta{color:var(--muted);font-size:11.5px}
.pbar{flex:1;max-width:220px;height:7px;border-radius:6px;background:#0a121d;border:1px solid var(--line);overflow:hidden}
.pbar>i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--greenb));width:0;transition:width .5s}
.phaseBody{padding:8px 10px}

/* ---- task rows ---- */
.task{display:flex;align-items:flex-start;gap:12px;padding:11px 12px;border-radius:10px;margin:4px 2px;
  border:1px solid transparent;transition:background .15s,border-color .15s;flex-wrap:wrap}

/* ---------------- Beginner/Pro mode + per-task guides ---------------- */
.modeToggle.on{border-color:var(--gold);color:var(--gold);background:#1a150a}
.gBtn{margin-left:2px;background:transparent;border:1px solid var(--line);color:var(--muted);
  border-radius:20px;font-size:10px;padding:2px 9px;cursor:pointer;font-family:inherit;transition:.15s}
.gBtn:hover{border-color:var(--accent2);color:var(--accent2)}
.gBtn.on{border-color:var(--accent2);color:#fff;background:#12233b}
.taskGuide{flex-basis:100%;width:100%;margin-top:8px}
.guideBody{background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--accent2);
  border-radius:9px;padding:12px 14px;font-size:13px}
.guideBody .gOver{margin:.1em 0 .7em;color:var(--txt)}
.guideBody .gSec{margin:.55em 0}
.guideBody h5{margin:.2em 0 .35em;font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);font-weight:700}
.guideBody ol{margin:.2em 0;padding-left:1.25em}
.guideBody ol li{margin:.2em 0}
.gtools{display:flex;flex-wrap:wrap;gap:5px}
.gtool{font-size:11px;padding:2px 8px;border-radius:6px;background:#0c1830;border:1px solid #22406a;color:var(--accent2)}
.gres{display:flex;flex-wrap:wrap;gap:5px 14px}
.gres a{font-size:12px}.gres .gnolink{font-size:12px;color:var(--muted)}
.guideBody .gDone{border-top:1px dashed var(--line);padding-top:.5em}
.guideBody .gDone h5{color:var(--greenb)} .guideBody .gDone p{color:#9fe0ad;margin:.2em 0}
.guideBody .gPit h5{color:var(--amber)} .guideBody .gPit p{color:#e6c98a;margin:.2em 0}
.gEmpty{color:var(--muted);font-style:italic}
/* Beginner "what to do next" home panel */
#beginnerHome{background:linear-gradient(180deg,#12233b 0%,var(--panel) 70%);border:1px solid #22406a;
  border-radius:14px;padding:16px 18px;margin:4px 2px 16px;box-shadow:var(--shadow)}
.bnHead{display:flex;align-items:center;gap:12px;margin-bottom:10px;flex-wrap:wrap}
.bnTag{font-weight:700;letter-spacing:.5px;color:var(--gold)}
.bnProg{color:var(--muted);font-size:12px}.bnProg b{color:var(--txt)}
.bnNext{background:var(--panel2);border:1px solid var(--line);border-radius:11px;padding:14px}
.bnNextTop{display:flex;align-items:center;gap:9px;margin-bottom:4px}
.bnLbl{font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:var(--accent2);font-weight:700}
.bnTitle{font-size:15px;font-weight:600;margin:.15em 0 .7em;color:#fff}
.bnActions{display:flex;align-items:center;gap:12px;margin-top:10px}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.btn.primary:hover{background:#3b8dff}
.bnXp{color:var(--gold);font-weight:700;font-size:13px}
.bnDone{background:#0d1f11;border:1px solid #1c3a22;color:#9fe0ad;border-radius:11px;padding:14px}
.bnNote{color:var(--muted);font-size:12px;margin-top:12px;line-height:1.6}
/* In beginner mode, quiet the pro-only chrome */
body.beginner #challengeWrap{display:none}
.task:hover{background:#0f1824;border-color:var(--line)}
.task.done{opacity:.62}
.task.done .ttitle{text-decoration:line-through;text-decoration-color:var(--muted)}
.chk{flex:0 0 22px;width:22px;height:22px;border-radius:6px;border:2px solid var(--line);cursor:pointer;
  display:grid;place-items:center;margin-top:1px;background:#0a121d;transition:all .15s}
.chk:hover{border-color:var(--accent)}
.task.done .chk{background:var(--green);border-color:var(--greenb)}
.chk svg{opacity:0;transition:opacity .15s}
.task.done .chk svg{opacity:1}
.tbody{flex:1;min-width:0}
.ttitle{color:var(--txt);font-size:13.5px}
.tmeta{display:flex;gap:7px;flex-wrap:wrap;margin-top:6px;align-items:center}
.chip{font-size:10px;padding:2px 7px;border-radius:20px;border:1px solid var(--line);color:var(--muted);
  letter-spacing:.4px;text-transform:uppercase;white-space:nowrap}
.chip.id{color:var(--accent2);border-color:#22406a}
.chip.id.met{color:var(--greenb);border-color:#1c3a22;background:#0d1f11}
.chip.cat{color:#cdb4ff;border-color:#3a2d5c}
.chip.track{color:#93c5fd}
.diff{color:var(--gold);font-size:11px;letter-spacing:1px}
.xpTag{flex:0 0 auto;align-self:center;font-weight:700;color:var(--gold);font-size:13px;
  background:#1a1608;border:1px solid #3a2f0e;border-radius:8px;padding:5px 10px;white-space:nowrap}
.task.done .xpTag{color:var(--greenb);background:#0d1f11;border-color:#1c3a22}
.delMy{align-self:center;margin-left:2px}

/* ---- personal add form ---- */
.autoXp{background:#1a1608;border:1px solid #3a2f0e;border-radius:8px;padding:6px 8px;color:var(--gold);
  font-weight:700;font-size:12.5px;text-align:center}
.empty{color:var(--muted);font-size:12px;padding:10px 4px}
.myAdd input[type=range]{width:100%;accent-color:var(--accent)}

/* ---- achievements ---- */
.achWrap{margin-top:26px}
.achGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-top:10px}
.ach{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:12px 13px;display:flex;gap:11px;align-items:center;opacity:.45;filter:grayscale(1)}
.ach.unlocked{opacity:1;filter:none;border-color:#2c3f57}
.ach .ico{font-size:22px}
.ach .an{font-size:12.5px;font-weight:700;color:#fff}
.ach .ad{font-size:10.5px;color:var(--muted)}

/* ---- trophy case ---- */
.trophyGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-top:12px}
.trophy{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:16px 12px;text-align:center;opacity:.5;filter:grayscale(.9)}
.trophy.won{opacity:1;filter:none;border-color:var(--tc)}
.trophy .tico{font-size:34px;line-height:1}
.trophy.won .tico{filter:drop-shadow(0 0 10px var(--tc))}
.trophy .tn{font-size:12px;font-weight:700;color:#fff;margin-top:8px}
.trophy .td{font-size:10px;color:var(--muted);margin-top:3px}
.trophy .tier{display:inline-block;margin-top:8px;font-size:9px;letter-spacing:1px;text-transform:uppercase;
  color:var(--tc);border:1px solid var(--tc);border-radius:20px;padding:1px 8px}
.trophy .ribbon{position:absolute;top:8px;right:9px;font-size:11px;color:var(--tc)}

/* ---- weekly challenges ---- */
.challenge{display:flex;gap:14px;align-items:flex-start;background:linear-gradient(160deg,#161f16,#0e1520);
  border:1px solid #2b3a26;border-left:3px solid var(--greenb);border-radius:12px;padding:14px 16px;margin-top:10px}
.challenge.done{border-left-color:var(--gold);opacity:.9}
.challenge.expired{border-left-color:var(--red);opacity:.75}
.chIco{font-size:30px;line-height:1}
.chBody{flex:1;min-width:0}
.chTop{display:flex;justify-content:space-between;gap:10px;align-items:center}
.chTop b{color:#fff;font-size:14px}
.chStatus{font-size:11px;color:var(--muted);white-space:nowrap}
.chDesc{color:var(--muted);font-size:12px;margin:3px 0 8px}
.chBar{height:7px;border-radius:6px;background:#0a121d;border:1px solid var(--line);overflow:hidden}
.chBar>i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--greenb));transition:width .5s}
.chMeta{font-size:11.5px;color:var(--muted);margin-top:7px}
.chMeta b{color:var(--gold)}
.chTasks{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}

h2.sec{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin:30px 0 4px;font-weight:700}

/* ---- modal ---- */
.overlay{position:fixed;inset:0;background:rgba(3,6,10,.72);backdrop-filter:blur(3px);z-index:100;
  display:grid;place-items:start center;padding:40px 16px;overflow:auto}
.modal{background:linear-gradient(160deg,var(--panel),var(--panel2));border:1px solid var(--line);
  border-radius:16px;box-shadow:var(--shadow);width:100%;max-width:860px;padding:20px 22px}
.modal .mhead{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.modal h3{margin:0;color:#fff;font-size:16px}
.modal .x{margin-left:auto;cursor:pointer;color:var(--muted);border:1px solid var(--line);border-radius:8px;padding:4px 10px}
.modal .x:hover{color:var(--red);border-color:var(--red)}
.modal input[type=text],.modal input[type=number],.modal input[type=password],.modal select{
  background:#0a121d;color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:6px 9px;
  font-family:inherit;font-size:12.5px;width:100%;outline:none}
.modal input:focus,.modal select:focus{border-color:var(--accent)}
.tabs{display:flex;gap:6px;margin:12px 0;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:10px}
.tab{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 11px;cursor:pointer;
  font-size:12px;color:var(--txt)}
.tab.active{border-color:var(--accent);color:#fff;background:#13233c}
.note{font-size:11px;color:var(--muted);background:#0e1520;border:1px solid var(--line);border-left:3px solid var(--amber);
  border-radius:8px;padding:8px 11px;margin:8px 0}
.fbox{background:#0e1520;border:1px solid var(--line);border-radius:10px;padding:12px;margin-bottom:8px}
.row{display:flex;gap:8px;flex-wrap:wrap}
.field{display:flex;flex-direction:column;gap:4px;margin:4px 0;flex:1;min-width:90px}
.field label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.badgePill{font-size:9px;letter-spacing:.5px;text-transform:uppercase;color:var(--accent2);
  border:1px solid #22406a;border-radius:20px;padding:1px 7px;margin-left:4px}
.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{text-align:left;color:var(--muted);font-weight:600;font-size:10px;text-transform:uppercase;
  letter-spacing:.5px;padding:6px 8px;border-bottom:1px solid var(--line)}
.tbl td{padding:6px 8px;border-bottom:1px solid #16202e;vertical-align:middle}
.tbl tr:hover td{background:#0f1824}

/* ---- leaderboard / profile menu ---- */
.lb{display:flex;flex-direction:column;gap:6px;margin-top:6px}
.lbRow{display:flex;align-items:center;gap:12px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
.lbRow.me{border-color:var(--accent)}
.lbPos{width:26px;text-align:center;font-weight:700;color:var(--muted)}
.lbAv{font-size:20px}
.lbName{flex:1;min-width:0}
.lbName b{color:#fff}
.lbName small{display:block;color:var(--muted);font-size:10.5px}
.lbStat{text-align:right;font-size:11px;color:var(--muted)}
.lbStat b{color:var(--gold);font-size:14px}

/* ---- toast ---- */
#toasts{position:fixed;right:18px;bottom:18px;display:flex;flex-direction:column;gap:10px;z-index:200}
.toast{background:linear-gradient(160deg,#15233a,#0e1826);border:1px solid var(--accent);border-radius:12px;
  padding:13px 16px;box-shadow:var(--shadow);min-width:240px;animation:pop .35s ease, fade .4s ease 3.4s forwards}
.toast .tt{font-weight:700;color:#fff;font-size:13px}
.toast .ts{color:var(--accent2);font-size:11.5px;margin-top:2px}
.toast.level{border-color:var(--gold)} .toast.level .ts{color:var(--gold)}
.toast.ach{border-color:var(--purple)} .toast.ach .ts{color:var(--purple)}
.toast.trophy{border-color:var(--gold)} .toast.trophy .ts{color:var(--gold)}
@keyframes pop{from{transform:translateY(14px) scale(.96);opacity:0}to{transform:none;opacity:1}}
@keyframes fade{to{opacity:0;transform:translateX(20px)}}
.footer{margin-top:34px;color:var(--muted);font-size:11px;text-align:center}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr)}.pbar{display:none}}
</style>
</head>
<body>
<div class="wrap">

  <div class="topbar">
    <div class="profile" id="profileChip">
      <span class="pav" id="pavatar">🎯</span>
      <span class="pinfo"><b id="pname">Operator</b><small id="prole">Lvl 1 · Initiate</small></span>
    </div>
    <button class="btn" id="switchUser">Switch profile ▾</button>
    <span class="spacer"></span>
    <button class="btn modeToggle" id="modeToggle" title="Toggle Beginner / Pro view">🎯 Pro</button>
    <a class="btn" href="resources.html" title="Curated learning resources">📚 Resources</a>
    <button class="btn" id="btnLeaders">🏆 Leaderboard</button>
    <button class="btn" id="btnAdmin">⚙ Admin</button>
  </div>

  <div class="hero">
    <div class="title"><span class="b">//</span> RED TEAM MASTERY <span class="b">TRACKER</span></div>
    <div class="subtitle">Intermediate pentester &rarr; elite adversary-emulation operator &nbsp;|&nbsp; authorized labs only</div>
    <div class="heroGrid">
      <div class="levelBadge">
        <div class="lvlRing" id="lvlRing"><div class="lvlNum"><b id="lvlNum">1</b><span>LEVEL</span></div></div>
        <div>
          <div class="rankName" id="rankName">Initiate</div>
          <div class="rankSub" id="rankSub">next rank at level 5</div>
          <span class="leaguePill" id="leaguePill">Beginner</span>
        </div>
      </div>
      <div class="xpbarWrap">
        <div class="xpbarTop"><span id="xpIntoTxt">0 XP</span><span id="xpNextTxt">/ next level</span></div>
        <div class="xpbar"><i id="xpFill"></i></div>
        <div class="xpbarTop" style="margin-top:6px"><span id="xpTotalTxt"></span><span id="pctTxt"></span></div>
      </div>
    </div>
  </div>

  <div class="stats">
    <div class="card good"><div class="k">Roadmap Done</div><div class="v"><span id="sDone">0</span> <small>/ <span id="sTotal">0</span></small></div></div>
    <div class="card gold"><div class="k">XP Earned</div><div class="v mono" id="sXp">0</div></div>
    <div class="card"><div class="k">Total XP Pool</div><div class="v mono" id="sPool">0</div></div>
    <div class="card"><div class="k">Completion</div><div class="v" id="sPct">0%</div></div>
  </div>

  <div id="beginnerHome" hidden></div>

  <div id="challengeWrap"></div>

  <div class="toolbar">
    <input type="search" id="q" placeholder="/ search tasks...">
    <select id="fPhase"></select>
    <select id="fTrack"></select>
    <select id="fCat"></select>
    <select id="fStatus">
      <option value="">All statuses</option>
      <option value="open">Open</option>
      <option value="done">Done</option>
    </select>
    <span class="spacer"></span>
    <button class="btn" id="expandAll">Expand all</button>
    <button class="btn" id="export">Export backup</button>
    <button class="btn" id="importBtn">Import</button>
    <input type="file" id="importFile" accept="application/json" style="display:none">
    <button class="btn danger" id="reset">Reset</button>
  </div>

  <div id="myTasksWrap"></div>
  <div id="phases"></div>

  <div class="achWrap">
    <h2 class="sec">Trophy Case</h2>
    <div class="trophyGrid" id="trophyGrid"></div>
  </div>

  <div class="achWrap">
    <h2 class="sec">Achievements</h2>
    <div class="achGrid" id="achGrid"></div>
  </div>

  <div class="footer">
    Progress saved locally in your browser (localStorage) &middot; export a JSON backup regularly &middot;
    admin PIN is a local convenience gate, not real access control
  </div>
</div>
<div id="toasts"></div>

<script>
const BUILTIN_TASKS = __TASKS_JSON__;
const RANKS = __RANKS_JSON__;
const GUIDES = __GUIDES_JSON__;

// ===================== Beginner/Pro mode + per-task guides =====================
const FOUNDATION_PHASES = ["Phase 1","Phase 2"];   // shown in Beginner mode
let UIMODE = (function(){ try{ return localStorage.getItem("rt-mode")==="beginner"?"beginner":"pro"; }catch(e){ return "pro"; } })();
function guideFor(id){ const g=GUIDES[id]; if(!g) return null; return g[UIMODE] || g.pro || g.beginner || null; }
function setMode(m){
  UIMODE = (m==="beginner") ? "beginner" : "pro";
  try{ localStorage.setItem("rt-mode", UIMODE); }catch(e){}
  document.body.classList.toggle("beginner", UIMODE==="beginner");
  syncModeBtn(); renderAll();
}
function syncModeBtn(){
  const b=document.getElementById("modeToggle"); if(!b) return;
  b.textContent = UIMODE==="beginner" ? "🎓 Beginner" : "🎯 Pro";
  b.classList.toggle("on", UIMODE==="beginner");
  b.title = UIMODE==="beginner" ? "Guided view — foundation phases only. Click for the full Pro roadmap."
                                : "Full roadmap. Click for the simplified guided Beginner view.";
}
function guideHtml(id){
  const g=guideFor(id);
  if(!g) return `<div class="guideBody"><div class="gEmpty">No guide authored for this task yet.</div></div>`;
  const li =a=>(a||[]).map(x=>`<li>${escapeHtml(x)}</li>`).join("");
  const chips=a=>(a||[]).map(x=>`<span class="gtool">${escapeHtml(x)}</span>`).join("");
  const res =a=>(a||[]).map(r=> (r&&r.url)
      ? `<a href="${escapeAttr(r.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(r.name)}</a>`
      : `<span class="gnolink">${escapeHtml(r?r.name:"")}</span>`).join("");
  return `<div class="guideBody">
    ${g.overview?`<p class="gOver">${escapeHtml(g.overview)}</p>`:""}
    ${g.steps&&g.steps.length?`<div class="gSec"><h5>Steps</h5><ol>${li(g.steps)}</ol></div>`:""}
    ${g.tools&&g.tools.length?`<div class="gSec"><h5>Tools</h5><div class="gtools">${chips(g.tools)}</div></div>`:""}
    ${g.resources&&g.resources.length?`<div class="gSec"><h5>Resources</h5><div class="gres">${res(g.resources)}</div></div>`:""}
    ${g.doneWhen?`<div class="gSec gDone"><h5>✓ Done when</h5><p>${escapeHtml(g.doneWhen)}</p></div>`:""}
    ${g.pitfall?`<div class="gSec gPit"><h5>⚠ Pitfall</h5><p>${escapeHtml(g.pitfall)}</p></div>`:""}
  </div>`;
}
function renderBeginnerHome(){
  const host=document.getElementById("beginnerHome"); if(!host) return;
  if(UIMODE!=="beginner"){ host.innerHTML=""; host.hidden=true; return; }
  host.hidden=false;
  const found=TASKS.filter(t=>FOUNDATION_PHASES.includes(t.phase));
  const next=found.find(t=>!state.done[t.id]);
  const doneN=found.filter(t=>state.done[t.id]).length;
  const pct=found.length?Math.round(doneN/found.length*100):0;
  let html=`<div class="bnHead"><span class="bnTag">🎓 Beginner path</span>
      <span class="bnProg"><b>${doneN}</b> / ${found.length} foundation tasks · ${pct}%</span></div>`;
  if(next){
    html+=`<div class="bnNext">
        <div class="bnNextTop"><span class="bnLbl">What to do next</span><span class="chip id">${next.id}</span>
          <span class="diff" title="difficulty ${next.diff}/5">${"★".repeat(next.diff)}${"☆".repeat(5-next.diff)}</span></div>
        <div class="bnTitle">${escapeHtml(next.title)}</div>
        ${guideHtml(next.id)}
        <div class="bnActions"><button class="btn primary" data-bndone="${next.id}">✓ Mark done &amp; continue</button>
          <span class="bnXp">＋${next.xp} XP</span></div>
      </div>`;
  } else {
    html+=`<div class="bnDone">🎉 You've completed every foundation task. Switch to <b>Pro mode</b> (top bar) to take on the full ${TASKS.length}-task roadmap.</div>`;
  }
  html+=`<div class="bnNote">Beginner mode shows only the foundation phases (Phase&nbsp;1 &amp; 2) with a step-by-step guide on each task. When you're ready, switch to <b>Pro mode</b> for all ${TASKS.length} tasks and every phase.</div>`;
  host.innerHTML=html;
  const b=host.querySelector("[data-bndone]"); if(b) b.onclick=()=>toggleTask(b.getAttribute("data-bndone"));
}
const LEVEL_BASE = __LEVEL_BASE__, LEVEL_STEP = __LEVEL_STEP__;
const KEY="rt_tracker_v2", OLDKEY="rt_tracker_v1";
const PHASE_ORDER = ["Phase 1","Phase 2","Phase 3","Phase 4","Phase 5","Phase 6","Tracks","Capstone"];
const PHASE_LABEL = {
  "Phase 1":"Phase 1 — Foundations retune + gap gate",
  "Phase 2":"Phase 2 — AD & identity attack chains",
  "Phase 3":"Phase 3 — Offensive dev & C2 tradecraft",
  "Phase 4":"Phase 4 — Evasion, maldev & detection-aware ops",
  "Phase 5":"Phase 5 — Cloud, hybrid identity & full-scope",
  "Phase 6":"Phase 6 — Adversary emulation & leadership",
  "Tracks":"Parallel Tracks (run continuously)",
  "Capstone":"Capstones (independence tests)"
};
const AVATARS=["🎯","🥷","👻","🐉","🦂","🐺","🦅","🕶️","💀","🧠","⚔️","🛡️"];
const TIERS={bronze:{n:"Bronze",c:"#c08457"},silver:{n:"Silver",c:"#c6cfdb"},
  gold:{n:"Gold",c:"#e3b341"},platinum:{n:"Platinum",c:"#7ee0d6"}};
const LEAGUES=[
  {min:1, name:"Beginner",     c:"#8b9bb0"},
  {min:4, name:"Novice",       c:"#63b3a8"},
  {min:8, name:"Skilled",      c:"#4f9df0"},
  {min:12,name:"Advanced",     c:"#7aa2f7"},
  {min:16,name:"Expert",       c:"#a371f7"},
  {min:20,name:"Master",       c:"#e3b341"},
  {min:24,name:"Pro",          c:"#f0883e"},
  {min:28,name:"Legend",       c:"#f85149"}
];
const BUILTIN_TROPHIES=[
  {id:"t-cadet",  ico:"🥉", name:"Operator Cadet",   desc:"Reach level 5",            tier:"bronze",   rule:{type:"level",value:5}},
  {id:"t-journey",ico:"⚙️", name:"Journeyman",       desc:"Reach level 10",           tier:"silver",   rule:{type:"level",value:10}},
  {id:"t-emu",    ico:"🎭", name:"Adversary Emulator",desc:"Reach level 15",          tier:"silver",   rule:{type:"level",value:15}},
  {id:"t-senior", ico:"🎖️", name:"Senior Red Teamer", desc:"Reach level 20",          tier:"gold",     rule:{type:"level",value:20}},
  {id:"t-lead",   ico:"🧭", name:"Red Team Lead",     desc:"Reach level 25",           tier:"gold",     rule:{type:"level",value:25}},
  {id:"t-elite",  ico:"👑", name:"Elite Specialist",  desc:"Reach level 30 (max rank)",tier:"platinum", rule:{type:"level",value:30}},
  {id:"t-xp5",    ico:"⚡", name:"Charged",           desc:"Earn 5,000 XP",            tier:"bronze",   rule:{type:"xp",value:5000}},
  {id:"t-xp15",   ico:"🔋", name:"Powerhouse",        desc:"Earn 15,000 XP",           tier:"silver",   rule:{type:"xp",value:15000}},
  {id:"t-crown",  ico:"🎓", name:"Triple Crown",      desc:"Pass CRTP, CRTO and CRTL", tier:"gold",     rule:{type:"ids",value:["P2-15","P3-14","P6-07"]}},
  {id:"t-caps",   ico:"🏆", name:"Capstone Master",   desc:"Clear every capstone",     tier:"platinum", rule:{type:"ids",value:["CAP-1","CAP-2","CAP-3","CAP-4","CAP-5A","CAP-5B"]}},
  {id:"t-100",    ico:"🌌", name:"Grandmaster",       desc:"Complete 100% of roadmap", tier:"platinum", rule:{type:"all"}}
];

// ================= data layer =================
function uid(){ return "u"+Date.now().toString(36)+Math.random().toString(36).slice(2,6); }
function blankProgress(){ return {done:{},collapsed:{},achShown:[],trophyShown:[],granted:{},
  personal:[],bonusXp:0,challengesDone:{},_primed:false}; }
function normProg(p){
  p=p||{}; p.done=p.done||{}; p.collapsed=p.collapsed||{}; p.achShown=p.achShown||[];
  p.trophyShown=p.trophyShown||[]; p.granted=p.granted||{}; p.personal=p.personal||[];
  p.bonusXp=p.bonusXp||0; p.challengesDone=p.challengesDone||{}; return p;
}
function seed(){
  let old=null; try{ old=JSON.parse(localStorage.getItem(OLDKEY)); }catch(e){}
  const id=uid(); const p=blankProgress();
  if(old){ p.done=old.done||{}; p.collapsed=old.collapsed||{}; p.achShown=old.achShown||[]; }
  const db={users:{},currentUser:id,settings:{adminPin:"1337"},overrides:{},customTasks:[],
    deleted:[],customTrophies:[],challenges:[]};
  db.users[id]={id,name:"Operator",avatar:"🎯",isAdmin:true,createdAt:Date.now(),progress:p};
  return db;
}
function normalizeDB(d){
  d.settings=d.settings||{}; if(!d.settings.adminPin) d.settings.adminPin="1337";
  d.overrides=d.overrides||{}; d.customTasks=d.customTasks||[]; d.deleted=d.deleted||[];
  d.customTrophies=d.customTrophies||[]; d.challenges=d.challenges||[]; d.users=d.users||{};
  for(const u of Object.values(d.users)){ u.progress=normProg(u.progress);
    if(!u.avatar)u.avatar="🎯"; if(u.isAdmin===undefined)u.isAdmin=false; }
  if(!d.users[d.currentUser]) d.currentUser=Object.keys(d.users)[0];
  return d;
}
function loadDB(){
  let d=null; try{ d=JSON.parse(localStorage.getItem(KEY)); }catch(e){}
  if(d&&d.users&&Object.keys(d.users).length) return normalizeDB(d);
  const s=seed(); localStorage.setItem(KEY,JSON.stringify(s)); return s;
}
let DB=null, state=null;
let SERVER=false, ME=null, CSRF=null;   // server mode: login accounts via Flask backend
let SRVSTATS=null;                       // F0: server-authoritative {xp,level,rank,league,...} for me
function cur(){ return DB.users[DB.currentUser]; }
function reselect(){ state=cur().progress; }

// ---- server API + mode-aware persistence -------------------------------
// Offline (opened as a file / plain static host): everything lives in localStorage.
// Server (served by server.py): identity + progress + shared config live in SQLite;
// admin status is enforced server-side and the client never decides it.
async function api(method,path,body){
  const opt={method,headers:{"Accept":"application/json"}};
  if(body!==undefined){ opt.headers["Content-Type"]="application/json"; opt.body=JSON.stringify(body); }
  if(method!=="GET" && CSRF) opt.headers["X-CSRF-Token"]=CSRF;
  let r; try{ r=await fetch(path,opt); }catch(e){ return {ok:false,status:0,j:{error:"network error"}}; }
  let j={}; try{ j=await r.json(); }catch(e){}
  return {ok:r.ok,status:r.status,j};
}
const _q={};
function persistProgress(){ if(!SERVER){ localStorage.setItem(KEY,JSON.stringify(DB)); return; }
  // F0: server is the XP/awards authority — apply what it returns (authoritative stats + server-owned fields)
  SRVSTATS=null;                    // show optimistic JS calc until the server confirms
  clearTimeout(_q["me"]); _q["me"]=setTimeout(async ()=>{
    const r=await api("PUT","/api/me/progress",{progress:state});
    if(!r.ok){ toast("task","Sync failed",(r.j&&r.j.error)||("HTTP "+r.status)); return; }
    applyServerSelf(r.j);
  },350); }
function applyServerSelf(j){
  if(j && j.server){ const s=j.server;
    state.bonusXp=s.bonusXp||0; state.granted=s.granted||{}; state.challengesDone=s.challengesDone||{}; }
  if(j && j.stats) SRVSTATS=j.stats;
  (j&&j.awarded||[]).forEach(name=>setTimeout(()=>toast("trophy","🏆 Challenge complete!",name),300));
  renderAll();
}
function persistConfig(){ if(!SERVER){ localStorage.setItem(KEY,JSON.stringify(DB)); return; }
  api("PUT","/api/config",{overrides:DB.overrides,customTasks:DB.customTasks,deleted:DB.deleted,
    customTrophies:DB.customTrophies,challenges:DB.challenges})
    .then(r=>{ if(!r.ok) toast("task","Config sync failed",(r.j&&r.j.error)||""); }); }
function persistUser(uid){ if(!SERVER){ localStorage.setItem(KEY,JSON.stringify(DB)); return; }
  api("PUT","/api/admin/users/"+uid+"/progress",{progress:DB.users[uid].progress})
    .then(r=>{ if(!r.ok) toast("task","Save failed",(r.j&&r.j.error)||""); }); }
function save(){ persistProgress(); }                         // own progress (gameplay)
function commitConfig(){ persistConfig(); rebuildTasks(); reselect(); renderAll(); adminRender(); }
function commitUser(uid){ persistUser(uid); renderAll(); adminRender(); }
function downloadJson(name,obj){ const blob=new Blob([JSON.stringify(obj,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob); const a=document.createElement("a"); a.href=url; a.download=name; a.click(); URL.revokeObjectURL(url); }

// effective (shared) roadmap tasks = builtins - deleted + overrides + admin custom
let TASKS=[];
function rebuildTasks(){
  const del=new Set(DB.deleted);
  const base=BUILTIN_TASKS.filter(t=>!del.has(t.id)).map(t=>Object.assign({},t,DB.overrides[t.id]||{}));
  TASKS=base.concat(DB.customTasks.filter(t=>!del.has(t.id)));
}

// ================= leveling =================
function cumXp(L){ let c=0; for(let i=2;i<=L;i++) c += LEVEL_BASE + LEVEL_STEP*(i-1); return c; }
function levelFromXp(xp){ let L=1; while(cumXp(L+1)<=xp) L++; return L; }
function rankFor(level){ let r=RANKS[0][1], nextLvl=null;
  for(let i=0;i<RANKS.length;i++){ if(level>=RANKS[i][0]) r=RANKS[i][1];
    else { nextLvl=RANKS[i][0]; break; } }
  return {rank:r, nextLvl}; }
function leagueFor(level){ let g=LEAGUES[0]; for(const l of LEAGUES){ if(level>=l.min) g=l; } return g; }

// ================= per-profile math =================
function personalOf(p){ return p.personal||[]; }
function findTask(id){ return TASKS.find(x=>x.id===id) || personalOf(state).find(x=>x.id===id); }
function roadmapXp(p){ return TASKS.reduce((s,t)=> s + (p.done[t.id]? t.xp:0), 0); }
function personalXp(p){ return personalOf(p).reduce((s,t)=> s + (p.done[t.id]? t.xp:0), 0); }
function xpOf(p){ return roadmapXp(p) + personalXp(p) + (p.bonusXp||0); }
function poolOf(p){ return TASKS.reduce((s,t)=>s+t.xp,0) + personalOf(p).reduce((s,t)=>s+t.xp,0); }
function rmDone(p){ return TASKS.filter(t=>p.done[t.id]).length; }
function personalDone(p){ return personalOf(p).filter(t=>p.done[t.id]).length; }
function doneOf(p){ return rmDone(p)+personalDone(p); }
function earnedXp(){ return xpOf(state); }
function totalXp(){ return poolOf(state); }
function doneCount(){ return doneOf(state); }
function xpForDiff(d){ d=Math.max(1,Math.min(5, d|0)); return 50*d + 25*d*(d-1); } // 50,150,300,500,750

// ================= achievements =================
const ACH = [
  {id:"first",   ico:"🩸", n:"First Blood",         d:"Complete your first task",            test:s=>doneCount()>=1},
  {id:"p1",      ico:"🧱", n:"Foundations Set",      d:"Finish every Phase 1 task",           test:s=>phaseDone("Phase 1")},
  {id:"crtp",    ico:"🏰", n:"AD Operator",          d:"Pass CRTP (P2-15)",                   test:s=>!!state.done["P2-15"]},
  {id:"crto",    ico:"🥷", n:"C2 Operator",          d:"Pass CRTO (P3-14)",                   test:s=>!!state.done["P3-14"]},
  {id:"edr",     ico:"👻", n:"Ghost in the Machine", d:"Beat a real EDR in lab (P4-12)",      test:s=>!!state.done["P4-12"]},
  {id:"cloud",   ico:"☁️", n:"Boundary Breaker",     d:"Own a hybrid cloud lab (P5-10)",      test:s=>!!state.done["P5-10"]},
  {id:"xp10k",   ico:"⚡", n:"10k Club",             d:"Earn 10,000 XP",                      test:s=>earnedXp()>=10000},
  {id:"cap1",    ico:"🎯", n:"Lone Operator",        d:"Clear Capstone 1",                    test:s=>!!state.done["CAP-1"]},
  {id:"purple",  ico:"🟣", n:"Purple Heart",         d:"Run a full purple-team cycle (TR-07)",test:s=>!!state.done["TR-07"]},
  {id:"apt",     ico:"🐉", n:"APT Emulator",         d:"Finish a named-APT emulation (CAP-5A)",test:s=>!!state.done["CAP-5A"]},
  {id:"lvl20",   ico:"🎖️", n:"Senior Red Teamer",    d:"Reach level 20",                      test:s=>levelFromXp(earnedXp())>=20},
  {id:"elite",   ico:"👑", n:"Elite",                d:"Complete 100% of the roadmap",        test:s=>TASKS.length>0 && rmDone(state)===TASKS.length},
];
function phaseDone(ph){ const ts=TASKS.filter(t=>t.phase===ph); return ts.length>0 && ts.every(t=>state.done[t.id]); }

// ================= trophies =================
function allTrophies(){ return BUILTIN_TROPHIES.concat(DB.customTrophies||[]); }
function ctxOf(p){ const xp=xpOf(p); return {xp, level:levelFromXp(xp), done:doneOf(p),
  rmDone:rmDone(p), rmTotal:TASKS.length}; }
// F0: prefer server-authoritative per-user stats when present; fall back to the JS calc (offline)
function userStats(u){
  if(SERVER && u && u.stats) return {xp:u.stats.xp, level:u.stats.level, done:u.stats.rmDone,
    rmDone:u.stats.rmDone, rmTotal:u.stats.rmTotal};
  return ctxOf((u&&u.progress)||{done:{}});
}
function phaseDoneP(p,ph){ const ts=TASKS.filter(t=>t.phase===ph); return ts.length>0 && ts.every(t=>p.done[t.id]); }
function trophyEarnedP(p,tr){
  if(p.granted && p.granted[tr.id]) return true;
  const r=tr.rule||{type:"manual"}, c=ctxOf(p);
  switch(r.type){
    case "level": return c.level>=r.value;
    case "xp":    return c.xp>=r.value;
    case "tasks": return c.done>=r.value;
    case "phase": return phaseDoneP(p,r.value);
    case "ids":   return (r.value||[]).length>0 && (r.value||[]).every(id=>!!p.done[id]);
    case "all":   return c.rmTotal>0 && c.rmDone===c.rmTotal;
    default:      return false;
  }
}
function trophyEarned(tr){ return trophyEarnedP(state,tr); }
function trophyCount(p){ return allTrophies().filter(t=>trophyEarnedP(p,t)).length; }
function primeAll(){
  rebuildTasks();
  for(const u of Object.values(DB.users)){
    const p=u.progress; if(p._primed) continue;
    allTrophies().forEach(t=>{ if(trophyEarnedP(p,t) && !p.trophyShown.includes(t.id)) p.trophyShown.push(t.id); });
    p._primed=true;
  }
  // F0: priming only suppresses local toasts — persist offline; in server mode it stays local
  // (so it never fires a load-time PUT that would clobber the authoritative SRVSTATS).
  if(!SERVER) save();
}

// ================= weekly challenges =================
function activeChallenges(){ return (DB.challenges||[]).filter(c=>c.active); }
function chalWindow(c){ const start=c.startedAt||0, end=start+(c.days||7)*86400000;
  return {start,end,left:end-Date.now(),expired:Date.now()>end}; }
function completedInWindow(p,start,end){ let n=0; const all=TASKS.concat(personalOf(p));
  for(const t of all){ const ts=p.done[t.id]; if(ts && ts>=start && ts<=end) n++; } return n; }
function chalProgress(c,p){
  if(c.goalType==="count"){ const w=chalWindow(c); return {have:Math.min(completedInWindow(p,w.start,w.end),c.count), need:c.count}; }
  const ids=c.taskIds||[]; return {have:ids.filter(id=>p.done[id]).length, need:ids.length};
}
function chalMet(c,p){ const pr=chalProgress(c,p); return pr.need>0 && pr.have>=pr.need; }
function timeLeft(ms){ if(ms<=0) return "0h"; const h=Math.floor(ms/3600000);
  if(h>=24) return Math.floor(h/24)+"d "+(h%24)+"h"; return h+"h"; }
function checkChallenges(){
  if(SERVER) return;               // F0: awards are server-authoritative; client only displays them
  let awarded=false;
  for(const c of activeChallenges()){
    if(state.challengesDone && state.challengesDone[c.id]) continue;
    const w=chalWindow(c); if(w.expired) continue;
    if(chalMet(c,state)){
      state.challengesDone=state.challengesDone||{}; state.challengesDone[c.id]=Date.now();
      state.bonusXp=(state.bonusXp||0)+(c.xp||0);
      if(c.trophyId){ state.granted[c.trophyId]=true;
        if(!state.trophyShown.includes(c.trophyId)) state.trophyShown.push(c.trophyId); }
      save(); awarded=true;
      const tn=(allTrophies().find(t=>t.id===c.trophyId)||{}).name||"trophy";
      setTimeout(()=>toast("trophy","🏆 Challenge complete!", c.name+" · +"+(c.xp||0)+" XP · "+tn), 600);
    }
  }
  if(awarded) renderAll();
}
function renderChallenges(){
  const host=$("#challengeWrap"); const cs=activeChallenges();
  if(!cs.length){ host.innerHTML=""; return; }
  host.innerHTML='<h2 class="sec">Weekly Challenges</h2>'+cs.map(c=>{
    const w=chalWindow(c), pr=chalProgress(c,state), done=state.challengesDone&&state.challengesDone[c.id];
    const pct=pr.need?Math.min(100,pr.have/pr.need*100):0;
    const troph=allTrophies().find(t=>t.id===c.trophyId);
    const status = done ? '<span style="color:var(--greenb)">✓ Completed</span>'
      : (w.expired ? '<span style="color:var(--red)">Expired</span>' : timeLeft(w.left)+" left");
    const cls="challenge"+(done?" done":(w.expired?" expired":""));
    return `<div class="${cls}">
      <div class="chIco">${troph?troph.ico:"🎯"}</div>
      <div class="chBody">
        <div class="chTop"><b>${escapeHtml(c.name)}</b><span class="chStatus">${status}</span></div>
        <div class="chDesc">${escapeHtml(c.desc||"")}</div>
        <div class="chBar"><i style="width:${pct}%"></i></div>
        <div class="chMeta">${pr.have}/${pr.need} ${c.goalType==="count"?"tasks this window":"objectives"} · reward <b>+${c.xp||0} XP</b>${troph?" · 🏆 "+escapeHtml(troph.name):""}</div>
        ${c.goalType==="tasks"&&(c.taskIds||[]).length?`<div class="chTasks">${c.taskIds.map(id=>`<span class="chip id${state.done[id]?" met":""}">${id}</span>`).join("")}</div>`:""}
      </div></div>`;
  }).join("");
}

// ================= rendering =================
const $=s=>document.querySelector(s);
function escapeHtml(s){return (""+s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function escapeAttr(s){return (""+s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function fillSelect(sel, label, values){
  sel.innerHTML = '<option value="">'+label+'</option>' + values.map(v=>`<option value="${escapeAttr(v)}">${escapeHtml(v)}</option>`).join('');
}
function uniq(k){ return [...new Set(TASKS.map(t=>t[k]))]; }
function phaseList(){ const s=[...PHASE_ORDER]; TASKS.forEach(t=>{ if(!s.includes(t.phase)) s.push(t.phase); });
  return s.filter(p=>TASKS.some(t=>t.phase===p)); }
function checkSvg(){return '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';}

function renderHeader(){
  // F0: in server mode display the server-authoritative xp/level once known; JS calc is offline/optimistic
  const auth = (SERVER && SRVSTATS) ? SRVSTATS : null;
  const xp = auth ? auth.xp : earnedXp();
  const pool=totalXp(), L = auth ? auth.level : levelFromXp(xp);
  const {rank,nextLvl}=rankFor(L); const lg=leagueFor(L);
  const base=cumXp(L), next=cumXp(L+1), into=xp-base, span=next-base;
  const pct = span>0 ? Math.min(100, into/span*100) : 100;
  $("#lvlNum").textContent=L;
  $("#lvlRing").style.setProperty("--p", pct.toFixed(1));
  $("#rankName").textContent=rank;
  $("#rankSub").textContent = nextLvl ? ("next rank at level "+nextLvl) : "max rank reached";
  const lp=$("#leaguePill"); lp.textContent=lg.name; lp.style.color=lg.c; lp.style.borderColor=lg.c;
  $("#xpFill").style.width=pct+"%";
  $("#xpIntoTxt").textContent = into.toLocaleString()+" / "+span.toLocaleString()+" XP";
  $("#xpNextTxt").textContent = "level "+(L+1);
  $("#xpTotalTxt").textContent = xp.toLocaleString()+" XP earned";
  $("#pctTxt").textContent = (pool?Math.round(xp/pool*100):0)+"% of pool";
  $("#sDone").textContent=rmDone(state); $("#sTotal").textContent=TASKS.length;
  $("#sXp").textContent=xp.toLocaleString(); $("#sPool").textContent=pool.toLocaleString();
  $("#sPct").textContent=(TASKS.length?Math.round(rmDone(state)/TASKS.length*100):0)+"%";
  const u=cur();
  $("#pname").textContent=u.name; $("#pavatar").textContent=u.avatar||"🎯";
  $("#prole").textContent="Lvl "+L+" · "+lg.name+(u.isAdmin?" · admin":"");
}

function passFilter(t){
  const q=$("#q").value.trim().toLowerCase();
  if(q && !(t.title.toLowerCase().includes(q)||t.id.toLowerCase().includes(q))) return false;
  if($("#fPhase").value && t.phase!==$("#fPhase").value) return false;
  if($("#fTrack").value && t.track!==$("#fTrack").value) return false;
  if($("#fCat").value && t.cat!==$("#fCat").value) return false;
  const st=$("#fStatus").value;
  if(st==="open" && state.done[t.id]) return false;
  if(st==="done" && !state.done[t.id]) return false;
  return true;
}

function renderMyTasks(){
  const host=$("#myTasksWrap"); const list=personalOf(state);
  const rows=list.map(t=>{ const d=!!state.done[t.id];
    return `<div class="task${d?" done":""}">
      <div class="chk" data-id="${t.id}" role="checkbox" aria-checked="${d}" tabindex="0">${checkSvg()}</div>
      <div class="tbody"><div class="ttitle">${escapeHtml(t.title)}</div>
        <div class="tmeta"><span class="chip cat">${escapeHtml(t.cat||"Personal")}</span>
          <span class="diff" title="difficulty ${t.diff}/5">${"★".repeat(t.diff)}${"☆".repeat(5-t.diff)}</span></div></div>
      <div class="xpTag">${t.xp} XP</div>
      <button class="btn mini danger delMy" data-id="${t.id}" title="delete task">✕</button></div>`;
  }).join("");
  const doneN=list.filter(t=>state.done[t.id]).length;
  host.innerHTML=`<div class="phase"><div class="phaseHead" style="cursor:default">
      <span style="font-size:16px">📝</span><h3>My Tasks — your own grind</h3>
      <span class="pmeta">${doneN}/${list.length} done · XP scales with difficulty</span>
      <span class="spacer" style="flex:1"></span></div>
    <div class="phaseBody">
      <div class="fbox myAdd">
        <div class="row">
          <div class="field" style="flex:2"><label>Task</label><input type="text" id="myTitle" placeholder="e.g. Own vulnhub box 'Kioptrix 1' unassisted"></div>
          <div class="field" style="max-width:150px"><label>Category</label><input type="text" id="myCat" placeholder="Personal"></div>
          <div class="field" style="max-width:200px"><label>Difficulty <span id="myDiffLbl">3 ★</span></label><input type="range" id="myDiff" min="1" max="5" value="3"></div>
          <div class="field" style="max-width:96px"><label>Reward</label><div class="autoXp" id="myXp">300 XP</div></div>
          <div class="field" style="max-width:90px;align-self:flex-end"><button class="btn" id="myAddBtn">＋ Add</button></div>
        </div>
      </div>
      <div id="myList">${rows||'<div class="empty">No personal tasks yet — add one above. Harder difficulty = more XP.</div>'}</div>
    </div></div>`;
  const diff=$("#myDiff");
  const upd=()=>{ const d=+diff.value; $("#myDiffLbl").textContent=d+" ★"; $("#myXp").textContent=xpForDiff(d)+" XP"; };
  diff.oninput=upd; upd();
  $("#myAddBtn").onclick=addPersonal;
  $("#myTitle").onkeydown=e=>{ if(e.key==="Enter") addPersonal(); };
  host.querySelectorAll(".chk").forEach(c=>{ const tog=()=>toggleTask(c.dataset.id);
    c.onclick=tog; c.onkeydown=e=>{ if(e.key===" "||e.key==="Enter"){e.preventDefault();tog();} }; });
  host.querySelectorAll(".delMy").forEach(b=>b.onclick=()=>delPersonal(b.dataset.id));
}
function addPersonal(){
  const title=($("#myTitle").value||"").trim(); if(!title){ $("#myTitle").focus(); return; }
  const cat=($("#myCat").value||"").trim()||"Personal";
  const d=Math.max(1,Math.min(5, +$("#myDiff").value||3));
  const id="MY-"+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
  state.personal=personalOf(state); state.personal.push({id,title,cat,diff:d,xp:xpForDiff(d),createdAt:Date.now()});
  save(); renderAll(); toast("task","Task added","+"+xpForDiff(d)+" XP when you complete it");
}
function delPersonal(id){
  if(!confirm("Delete this personal task?")) return;
  state.personal=personalOf(state).filter(t=>t.id!==id); delete state.done[id]; save(); renderAll();
}

function renderPhases(){
  const host=$("#phases"); host.innerHTML="";
  const filtering = $("#q").value||$("#fPhase").value||$("#fTrack").value||$("#fCat").value||$("#fStatus").value;
  for(const ph of phaseList()){
    if(UIMODE==="beginner" && !FOUNDATION_PHASES.includes(ph)) continue;   // Beginner mode: foundation phases only
    const all=TASKS.filter(t=>t.phase===ph);
    if(!all.length) continue;
    const shown=all.filter(passFilter);
    if(!shown.length && filtering) continue;
    const done=all.filter(t=>state.done[t.id]).length;
    const xpDone=all.filter(t=>state.done[t.id]).reduce((s,t)=>s+t.xp,0);
    const xpTot=all.reduce((s,t)=>s+t.xp,0);
    const pct = all.length? done/all.length*100 : 0;
    const collapsed = state.collapsed[ph];
    const sec=document.createElement("div");
    sec.className="phase"+(collapsed?" collapsed":"");
    sec.innerHTML=`
      <div class="phaseHead" data-ph="${escapeAttr(ph)}">
        <span class="caret">▶</span>
        <h3>${escapeHtml(PHASE_LABEL[ph]||ph)}</h3>
        <span class="pmeta">${done}/${all.length} · ${xpDone.toLocaleString()}/${xpTot.toLocaleString()} XP</span>
        <span class="spacer" style="flex:1"></span>
        <div class="pbar"><i style="width:${pct}%"></i></div>
      </div>
      <div class="phaseBody"></div>`;
    const body=sec.querySelector(".phaseBody");
    for(const t of shown){
      const d=!!state.done[t.id];
      const row=document.createElement("div");
      row.className="task"+(d?" done":"");
      const hasGuide=!!guideFor(t.id);
      row.innerHTML=`
        <div class="chk" data-id="${t.id}" role="checkbox" aria-checked="${d}" tabindex="0">${checkSvg()}</div>
        <div class="tbody">
          <div class="ttitle">${escapeHtml(t.title)}</div>
          <div class="tmeta">
            <span class="chip id">${t.id}</span>
            <span class="chip cat">${escapeHtml(t.cat)}</span>
            <span class="chip track">${escapeHtml(t.track)}</span>
            <span class="diff" title="difficulty ${t.diff}/5">${"★".repeat(t.diff)}${"☆".repeat(5-t.diff)}</span>
            ${hasGuide?`<button class="gBtn" data-guide="${t.id}" aria-expanded="false">📖 Guide</button>`:""}
          </div>
        </div>
        <div class="xpTag">${t.xp} XP</div>
        <div class="taskGuide" data-gid="${t.id}" hidden></div>`;
      body.appendChild(row);
    }
    host.appendChild(sec);
  }
  bindRows();
}
function bindRows(){
  document.querySelectorAll("#phases .phaseHead").forEach(h=>{
    if(!h.dataset.ph) return;
    h.onclick=()=>{ const ph=h.dataset.ph; state.collapsed[ph]=!state.collapsed[ph]; save();
      h.parentElement.classList.toggle("collapsed"); };
  });
  document.querySelectorAll("#phases .chk").forEach(c=>{
    const toggle=()=>toggleTask(c.dataset.id);
    c.onclick=toggle;
    c.onkeydown=e=>{ if(e.key===" "||e.key==="Enter"){e.preventDefault();toggle();} };
  });
  document.querySelectorAll("#phases .gBtn").forEach(b=>{
    b.onclick=()=>{
      const id=b.getAttribute("data-guide");
      const row=b.closest(".task");
      const drawer=row && row.querySelector('.taskGuide[data-gid="'+id+'"]');
      if(!drawer) return;
      const open=drawer.hasAttribute("hidden");
      if(open){ if(!drawer.dataset.filled){ drawer.innerHTML=guideHtml(id); drawer.dataset.filled="1"; } drawer.removeAttribute("hidden"); }
      else drawer.setAttribute("hidden","");
      b.setAttribute("aria-expanded", open?"true":"false");
      b.classList.toggle("on", open);
    };
  });
}

function toggleTask(id){
  const t=findTask(id); if(!t) return;
  const before=levelFromXp(earnedXp());
  const wasDone=!!state.done[id];
  if(wasDone) delete state.done[id]; else state.done[id]=Date.now();
  save();
  const after=levelFromXp(earnedXp());
  renderAll();
  if(!wasDone){
    toast("task","＋ "+t.xp+" XP", (t.id||"task")+" complete");
    if(after>before) setTimeout(()=>toast("level","LEVEL UP → "+after, rankFor(after).rank+" · "+leagueFor(after).name),350);
    checkNewAch(); checkNewTrophies(); checkChallenges();   // checkChallenges no-ops in server mode
  }
}

function renderAch(){
  const g=$("#achGrid"); g.innerHTML="";
  for(const a of ACH){
    const un=a.test(state);
    const el=document.createElement("div");
    el.className="ach"+(un?" unlocked":"");
    el.innerHTML=`<div class="ico">${a.ico}</div><div><div class="an">${a.n}</div><div class="ad">${a.d}</div></div>`;
    g.appendChild(el);
  }
}
function checkNewAch(){
  for(const a of ACH){
    if(a.test(state) && !state.achShown.includes(a.id)){
      state.achShown.push(a.id); save();
      setTimeout(()=>toast("ach", a.ico+"  "+a.n, "Achievement unlocked"), 700);
    }
  }
}

function renderTrophies(){
  const g=$("#trophyGrid"); g.innerHTML="";
  for(const t of allTrophies()){
    const won=trophyEarned(t); const tc=(TIERS[t.tier]||TIERS.bronze).c;
    const el=document.createElement("div");
    el.className="trophy"+(won?" won":""); el.style.setProperty("--tc",tc);
    el.innerHTML=`<div class="ribbon">${won?"★":"🔒"}</div><div class="tico">${t.ico}</div>
      <div class="tn">${escapeHtml(t.name)}</div><div class="td">${escapeHtml(t.desc||"")}</div>
      <div class="tier">${(TIERS[t.tier]||{}).n||t.tier||""}</div>`;
    g.appendChild(el);
  }
}
function checkNewTrophies(){
  for(const t of allTrophies()){
    if(trophyEarnedP(state,t) && !state.trophyShown.includes(t.id)){
      state.trophyShown.push(t.id); save();
      setTimeout(()=>toast("trophy", t.ico+"  "+t.name, "Trophy unlocked · "+((TIERS[t.tier]||{}).n||"")), 900);
    }
  }
}

function toast(kind,tt,ts){
  const d=document.createElement("div"); d.className="toast "+kind;
  d.innerHTML=`<div class="tt">${tt}</div><div class="ts">${ts}</div>`;
  $("#toasts").appendChild(d); setTimeout(()=>d.remove(),4000);
}

// ================= modals =================
function closeModal(){ const o=document.getElementById("ov"); if(o) o.remove(); }
function modal(inner){
  closeModal();
  const ov=document.createElement("div"); ov.className="overlay"; ov.id="ov";
  ov.innerHTML='<div class="modal">'+inner+'</div>';
  ov.addEventListener("click",e=>{ if(e.target===ov) closeModal(); });
  document.body.appendChild(ov); return ov;
}
document.addEventListener("keydown",e=>{ if(e.key==="Escape") closeModal(); });

function addUser(name,avatar,isAdmin){
  const id=uid(); const p=blankProgress(); p._primed=true;
  DB.users[id]={id,name,avatar:avatar||AVATARS[Object.keys(DB.users).length%AVATARS.length],
    isAdmin:!!isAdmin,createdAt:Date.now(),progress:p};
  save(); return id;
}

function openUserMenu(){
  const rows=Object.values(DB.users).map(u=>{ const c=userStats(u);
    return `<div class="lbRow ${u.id===DB.currentUser?"me":""}" data-act="switch" data-id="${u.id}" style="cursor:pointer">
      <span class="lbAv">${u.avatar||"🎯"}</span>
      <div class="lbName"><b>${escapeHtml(u.name)}</b><small>Lvl ${c.level} · ${leagueFor(c.level).name}${u.isAdmin?" · admin":""}</small></div>
      <div class="lbStat"><b>${c.xp.toLocaleString()}</b> XP</div></div>`;
  }).join("");
  const ov=modal(`<div class="mhead"><h3>👥 Profiles</h3><span class="x" data-act="close">✕</span></div>
    <div class="lb">${rows}</div>
    <div class="row" style="margin-top:12px">
      <button class="btn" data-act="addUser">＋ Add profile</button>
      <button class="btn" data-act="close">Close</button></div>
    <div class="note">Switching profiles is open to anyone on this machine. Destructive actions (delete, reset, task/trophy edits) live behind the ⚙ Admin PIN.</div>`);
  ov.addEventListener("click",e=>{
    const a=e.target.closest("[data-act]"); if(!a) return; const act=a.dataset.act;
    if(act==="close") return closeModal();
    if(act==="switch"){ DB.currentUser=a.dataset.id; reselect(); save(); closeModal(); renderAll();
      checkChallenges(); toast("task","Switched profile",cur().name); }
    if(act==="addUser"){ const n=(prompt("New profile name:")||"").trim(); if(!n) return;
      DB.currentUser=addUser(n); reselect(); closeModal(); renderAll(); toast("task","Profile created",n); }
  });
}

function openLeaderboard(){
  const arr=Object.values(DB.users).map(u=>({u,c:userStats(u),tr:trophyCount(u.progress)}))
    .sort((a,b)=>b.c.xp-a.c.xp);
  const medal=i=> i===0?"🥇":i===1?"🥈":i===2?"🥉":("#"+(i+1));
  const rows=arr.map((r,i)=>`<div class="lbRow ${r.u.id===DB.currentUser?"me":""}">
    <span class="lbPos">${medal(i)}</span><span class="lbAv">${r.u.avatar||"🎯"}</span>
    <div class="lbName"><b>${escapeHtml(r.u.name)}</b><small>Lvl ${r.c.level} · ${rankFor(r.c.level).rank} · ${leagueFor(r.c.level).name}</small></div>
    <div class="lbStat"><b>${r.c.xp.toLocaleString()}</b> XP<br>${r.c.rmDone}/${r.c.rmTotal} · 🏆${r.tr}</div></div>`).join("");
  const ov=modal(`<div class="mhead"><h3>🏆 Leaderboard</h3><span class="x" data-act="close">✕</span></div>
    <div class="lb">${rows}</div>`);
  ov.addEventListener("click",e=>{ if(e.target.closest("[data-act=close]")) closeModal(); });
}

// ================= admin panel =================
let adminUnlocked=false, adminTab="users", editTask=null;
function openAdmin(){
  if(SERVER){
    if(!ME || !ME.isAdmin){ toast("task","Admins only","your account is not an admin"); return; }
    adminTab="users"; editTask=null; return adminRender();     // server enforces admin; no PIN
  }
  if(!adminUnlocked){
    const pin=prompt("Enter admin PIN (default 1337):");
    if(pin===null) return;
    if(pin!==DB.settings.adminPin){ toast("task","Access denied","wrong PIN"); return; }
    adminUnlocked=true;
  }
  adminRender();
}
function adminBody(){
  if(adminTab==="users") return adminUsers();
  if(adminTab==="tasks") return adminTasks();
  if(adminTab==="trophies") return adminTrophies();
  if(adminTab==="challenges") return adminChallenges();
  return adminData();
}
function adminRender(){
  const labels={users:"👥 Profiles",tasks:"🗂 Tasks",trophies:"🏆 Trophies",challenges:"📅 Challenges",data:"💾 Data"};
  const tabs=["users","tasks","trophies","challenges","data"];
  const badge = SERVER ? '<span class="badgePill">server · accounts</span>' : '<span class="badgePill">local · soft-gated</span>';
  const note = SERVER
    ? 'You are signed in as an admin. Changes here are written to the server database and enforced server-side.'
    : 'This panel and its PIN live only in this browser — a convenience gate for a shared machine, <b>not real access control</b>. Anyone with devtools can bypass it.';
  const inner=`<div class="mhead"><h3>⚙ Admin Panel</h3>${badge}
      <span class="x" data-act="close">✕</span></div>
    <div class="note">${note}</div>
    <div class="tabs">${tabs.map(t=>`<button class="tab ${adminTab===t?"active":""}" data-act="tab" data-tab="${t}">${labels[t]}</button>`).join("")}</div>
    <div id="adminBody">${adminBody()}</div>`;
  let ov=document.getElementById("ov");
  if(ov){ ov.querySelector(".modal").innerHTML=inner; }
  else{ ov=modal(inner); ov.addEventListener("click",onAdminClick); }
  if(adminTab==="data"){
    if(SERVER){ const f=document.getElementById("importLegacyFile"); if(f) f.onchange=importLegacyHandler; }
    else{ const f=document.getElementById("importAllFile"); if(f) f.onchange=importAllHandler; }
  }
}

function adminUsers(){
  const rows=Object.values(DB.users).map(u=>{ const c=userStats(u);
    const isMe = u.id===DB.currentUser;
    const acts = SERVER
      ? `<button class="btn mini" data-act="urename" data-id="${u.id}">Rename</button>
         <button class="btn mini" data-act="upw" data-id="${u.id}">Set password</button>
         <button class="btn mini" data-act="uadmin" data-id="${u.id}">${u.isAdmin?"Revoke admin":"Make admin"}</button>
         <button class="btn mini" data-act="ureset" data-id="${u.id}">Reset</button>
         <button class="btn mini danger" data-act="udel" data-id="${u.id}">Delete</button>`
      : `<button class="btn mini" data-act="uswitch" data-id="${u.id}">Switch</button>
         <button class="btn mini" data-act="urename" data-id="${u.id}">Rename</button>
         <button class="btn mini" data-act="uadmin" data-id="${u.id}">${u.isAdmin?"Revoke admin":"Make admin"}</button>
         <button class="btn mini" data-act="ureset" data-id="${u.id}">Reset</button>
         <button class="btn mini danger" data-act="udel" data-id="${u.id}">Delete</button>`;
    return `<tr>
      <td>${u.avatar||"🎯"} <b>${escapeHtml(u.name)}</b>${isMe?' <span class="badgePill">you</span>':""}</td>
      <td>${u.isAdmin?"✓":""}</td>
      <td class="mono">${c.level}</td><td class="mono">${c.xp.toLocaleString()}</td>
      <td class="mono">${c.rmDone}/${c.rmTotal}</td><td class="mono">${trophyCount(u.progress)}</td>
      <td>${acts}</td></tr>`;
  }).join("");
  const addForm = SERVER
    ? `<div class="fbox" style="margin-top:12px"><b style="font-size:12px;color:#fff">Create account</b><div class="row" style="margin-top:6px">
        <div class="field" style="flex:2"><label>Username</label><input type="text" id="newUserName" placeholder="trainee-01"></div>
        <div class="field"><label>Password</label><input type="password" id="newUserPass" autocomplete="new-password"></div>
        <div class="field" style="max-width:80px"><label>Emoji</label><input type="text" id="newUserAv" maxlength="4" placeholder="🥷"></div>
        <div class="field" style="max-width:70px"><label>Admin?</label><input type="checkbox" id="newUserAdmin" style="width:auto"></div>
        <div class="field" style="max-width:100px;align-self:flex-end"><button class="btn" data-act="uadd">＋ Create</button></div>
      </div></div>`
    : `<div class="fbox" style="margin-top:12px"><div class="row">
        <div class="field" style="flex:2"><label>New profile name</label><input type="text" id="newUserName" placeholder="e.g. Trainee-01"></div>
        <div class="field" style="max-width:80px"><label>Emoji</label><input type="text" id="newUserAv" maxlength="4" placeholder="🥷"></div>
        <div class="field" style="max-width:90px"><label>Admin?</label><input type="checkbox" id="newUserAdmin" style="width:auto"></div>
        <div class="field" style="max-width:110px;align-self:flex-end"><button class="btn" data-act="uadd">＋ Add profile</button></div>
      </div></div>`;
  return `<table class="tbl"><tr><th>${SERVER?"Account":"Profile"}</th><th>Admin</th><th>Lvl</th><th>XP</th><th>Roadmap</th><th>🏆</th><th>Actions</th></tr>${rows}</table>${addForm}`;
}

function taskForm(){
  const t=editTask?TASKS.find(x=>x.id===editTask):null;
  const phs=[...new Set(TASKS.map(x=>x.phase))];
  return `<div class="fbox">
    <div class="row">
      <div class="field" style="max-width:130px"><label>ID</label><input type="text" id="tfId" value="${t?escapeAttr(t.id):""}" ${t?"readonly":""} placeholder="P1-14"></div>
      <div class="field" style="flex:2"><label>Title</label><input type="text" id="tfTitle" value="${t?escapeAttr(t.title):""}"></div>
    </div>
    <div class="row">
      <div class="field"><label>Phase</label><input type="text" id="tfPhase" list="phaseOpts" value="${t?escapeAttr(t.phase):"Phase 1"}"></div>
      <div class="field"><label>Track</label><input type="text" id="tfTrack" value="${t?escapeAttr(t.track):"Core"}"></div>
      <div class="field"><label>Category</label><input type="text" id="tfCat" value="${t?escapeAttr(t.cat):"Learn"}"></div>
      <div class="field" style="max-width:90px"><label>Diff 1-5</label><input type="number" id="tfDiff" min="1" max="5" value="${t?t.diff:3}"></div>
      <div class="field" style="max-width:100px"><label>XP</label><input type="number" id="tfXp" min="0" value="${t?t.xp:100}"></div>
    </div>
    <datalist id="phaseOpts">${phs.map(p=>`<option value="${escapeAttr(p)}">`).join("")}</datalist>
    <div class="row" style="margin-top:4px">
      <button class="btn" data-act="tsave">${t?"Save changes":"＋ Add task"}</button>
      ${t?'<button class="btn" data-act="tcancel">Cancel edit</button>':""}
    </div></div>`;
}
function adminTasks(){
  const rows=TASKS.map(t=>{ const isC=DB.customTasks.some(x=>x.id===t.id); const ov=!!DB.overrides[t.id];
    return `<tr>
      <td class="mono">${t.id}${isC?' <span class="badgePill">custom</span>':(ov?' <span class="badgePill">edited</span>':"")}</td>
      <td>${escapeHtml(t.title)}</td><td>${escapeHtml(t.phase)}</td><td class="mono">${t.diff}★</td><td class="mono">${t.xp}</td>
      <td><button class="btn mini" data-act="tedit" data-id="${t.id}">Edit</button>
      <button class="btn mini danger" data-act="tdel" data-id="${t.id}">Delete</button></td></tr>`;
  }).join("");
  return taskForm()+
    `<div class="row" style="margin:8px 0"><span class="spacer"></span>
      <button class="btn mini" data-act="trestore">Restore built-in defaults</button></div>
    <div style="max-height:360px;overflow:auto"><table class="tbl">
      <tr><th>ID</th><th>Title</th><th>Phase</th><th>Diff</th><th>XP</th><th></th></tr>${rows}</table></div>`;
}

function ruleText(r){ r=r||{type:"manual"};
  switch(r.type){ case "xp":return "XP ≥ "+r.value; case "level":return "Lvl ≥ "+r.value;
    case "tasks":return "Tasks ≥ "+r.value; case "phase":return escapeHtml(r.value)+" done";
    case "ids":return (r.value||[]).join(","); case "all":return "100% roadmap"; default:return "manual grant"; } }
function adminTrophies(){
  const list=allTrophies().map(t=>{ const isC=(DB.customTrophies||[]).some(x=>x.id===t.id);
    const c=(TIERS[t.tier]||{}).c||"#888";
    return `<tr>
      <td>${t.ico} <b>${escapeHtml(t.name)}</b>${isC?' <span class="badgePill">custom</span>':""}</td>
      <td>${escapeHtml(t.desc||"")}</td>
      <td style="color:${c}">${(TIERS[t.tier]||{}).n||t.tier||""}</td>
      <td class="mono">${ruleText(t.rule)}</td>
      <td>${trophyEarned(t)?"✓":""}</td>
      <td>${isC?`<button class="btn mini danger" data-act="trophdel" data-id="${t.id}">Delete</button>`:""}</td></tr>`;
  }).join("");
  const uopts=Object.values(DB.users).map(u=>`<option value="${u.id}">${escapeHtml(u.name)}</option>`).join("");
  const topts=allTrophies().map(t=>`<option value="${t.id}">${escapeHtml(t.name)}</option>`).join("");
  return `<div class="fbox">
    <div class="row">
      <div class="field" style="max-width:70px"><label>Icon</label><input type="text" id="trIco" maxlength="4" value="🏅"></div>
      <div class="field"><label>Name</label><input type="text" id="trName"></div>
      <div class="field" style="flex:2"><label>Description</label><input type="text" id="trDesc"></div>
    </div>
    <div class="row">
      <div class="field"><label>Tier</label><select id="trTier"><option value="bronze">Bronze</option><option value="silver">Silver</option><option value="gold" selected>Gold</option><option value="platinum">Platinum</option></select></div>
      <div class="field"><label>Rule</label><select id="trType">
        <option value="manual">Manual grant only</option>
        <option value="xp">XP ≥</option><option value="level">Level ≥</option>
        <option value="tasks">Tasks done ≥</option><option value="phase">Phase complete</option>
        <option value="all">100% roadmap</option></select></div>
      <div class="field"><label>Value (number, or Phase name)</label><input type="text" id="trVal" placeholder="e.g. 10000  or  Phase 2"></div>
      <div class="field" style="max-width:120px;align-self:flex-end"><button class="btn" data-act="trophadd">＋ Add trophy</button></div>
    </div></div>
    <div style="max-height:260px;overflow:auto"><table class="tbl">
      <tr><th>Trophy</th><th>Description</th><th>Tier</th><th>Rule</th><th>You</th><th></th></tr>${list}</table></div>
    <div class="fbox" style="margin-top:12px"><b style="font-size:12px;color:#fff">Grant / revoke to a profile</b>
      <div class="row" style="margin-top:6px">
        <div class="field"><label>Profile</label><select id="grUser">${uopts}</select></div>
        <div class="field"><label>Trophy</label><select id="grTroph">${topts}</select></div>
        <div class="field" style="max-width:90px;align-self:flex-end"><button class="btn" data-act="grgrant">Grant</button></div>
        <div class="field" style="max-width:90px;align-self:flex-end"><button class="btn" data-act="grrevoke">Revoke</button></div>
      </div>
      <div class="note">Grant forces a trophy onto a profile regardless of its rule; Revoke clears a manual grant (rule-based trophies still show if the profile qualifies).</div></div>`;
}

function adminChallenges(){
  const rows=(DB.challenges||[]).map(c=>{ const w=chalWindow(c); const troph=allTrophies().find(t=>t.id===c.trophyId);
    return `<tr>
      <td><b>${escapeHtml(c.name)}</b><br><small style="color:var(--muted)">${escapeHtml(c.desc||"")}</small></td>
      <td>${c.goalType==="count"?("any "+c.count):((c.taskIds||[]).length+" tasks")}<br><small style="color:var(--muted)">${c.days||7}d window</small></td>
      <td class="mono">+${c.xp||0}</td>
      <td>${troph?troph.ico+" "+escapeHtml(troph.name):"—"}</td>
      <td>${c.active?(w.expired?'<span style="color:var(--red)">expired</span>':'<span style="color:var(--greenb)">active</span>'):"off"}</td>
      <td>
        <button class="btn mini" data-act="chtoggle" data-id="${c.id}">${c.active?"Disable":"Enable"}</button>
        <button class="btn mini" data-act="chrestart" data-id="${c.id}">Restart</button>
        <button class="btn mini danger" data-act="chdel" data-id="${c.id}">Delete</button></td></tr>`;
  }).join("");
  return `<div class="fbox">
    <div class="row">
      <div class="field" style="flex:2"><label>Challenge name</label><input type="text" id="chName" placeholder="Kerberoast Week"></div>
      <div class="field" style="max-width:120px"><label>Duration (days)</label><input type="number" id="chDays" value="7" min="1"></div>
    </div>
    <div class="field"><label>Description</label><input type="text" id="chDesc" placeholder="Complete the AD credential-access tasks this week"></div>
    <div class="row">
      <div class="field"><label>Goal type</label><select id="chType">
        <option value="tasks">Specific roadmap tasks</option>
        <option value="count">Any N tasks in the window</option></select></div>
      <div class="field" style="flex:2"><label>Task IDs (comma-sep) — for "specific"</label><input type="text" id="chIds" placeholder="P2-01, P2-02, P2-11"></div>
      <div class="field" style="max-width:120px"><label>N (for "any N")</label><input type="number" id="chCount" value="5" min="1"></div>
    </div>
    <div class="row">
      <div class="field" style="max-width:120px"><label>Reward XP</label><input type="number" id="chXp" value="500" min="0"></div>
      <div class="field" style="max-width:70px"><label>Trophy icon</label><input type="text" id="chTico" value="🏅" maxlength="4"></div>
      <div class="field"><label>Trophy name</label><input type="text" id="chTname" placeholder="Kerberoast Champion"></div>
      <div class="field"><label>Tier</label><select id="chTier"><option value="bronze">Bronze</option><option value="silver">Silver</option><option value="gold" selected>Gold</option><option value="platinum">Platinum</option></select></div>
      <div class="field" style="max-width:150px;align-self:flex-end"><button class="btn" data-act="chadd">＋ Create challenge</button></div>
    </div>
    <div class="note">A challenge auto-creates its trophy and awards it plus the bonus XP to any profile that meets the goal inside the time window. "Restart" resets the clock so everyone can earn it again.</div></div>
    <table class="tbl"><tr><th>Challenge</th><th>Goal</th><th>XP</th><th>Trophy</th><th>State</th><th></th></tr>${rows}</table>`;
}

function adminData(){
  if(SERVER){
    return `<div class="fbox"><b style="font-size:12px;color:#fff">Change your password</b><div class="row" style="margin-top:6px">
        <div class="field"><label>Current</label><input type="password" id="pwOld" autocomplete="current-password"></div>
        <div class="field"><label>New</label><input type="password" id="pwNew" autocomplete="new-password"></div>
        <div class="field" style="max-width:150px;align-self:flex-end"><button class="btn" data-act="chpw">Update password</button></div>
      </div></div>
      <div class="row" style="margin-top:12px">
        <button class="btn" data-act="exportAll">⬇ Export full server backup</button>
        <button class="btn" data-act="importLegacy">⬆ Import legacy (browser Export ALL)</button>
        <input type="file" id="importLegacyFile" accept="application/json" style="display:none">
        <span class="spacer"></span>
        <button class="btn danger" data-act="wipe">Wipe other accounts + config</button>
      </div>
      <div class="note">Export writes every account (incl. password hashes) + shared config to one JSON file — sensitive, keep it safe. Import legacy seeds accounts from the old browser "Export ALL" (each profile's temporary password = its username; set real ones afterward). Wipe deletes all <b>other</b> accounts, clears shared config, and resets your own progress.</div>`;
  }
  return `<div class="fbox"><div class="row">
      <div class="field"><label>Change admin PIN</label><input type="text" id="newPin" placeholder="new PIN"></div>
      <div class="field" style="max-width:120px;align-self:flex-end"><button class="btn" data-act="setpin">Update PIN</button></div>
    </div></div>
    <div class="row" style="margin-top:12px">
      <button class="btn" data-act="exportAll">⬇ Export ALL data</button>
      <button class="btn" data-act="importAll">⬆ Import ALL data</button>
      <input type="file" id="importAllFile" accept="application/json" style="display:none">
      <span class="spacer"></span>
      <button class="btn danger" data-act="wipe">Wipe everything</button>
    </div>
    <div class="note">Export ALL writes every profile, task edit, trophy, and challenge to one JSON file — your full backup. Import ALL replaces everything. The per-profile toolbar Export/Import only moves the current profile's progress.</div>`;
}

function saveTask(){
  const g=id=>document.getElementById(id);
  const idv=(g("tfId").value||"").trim();
  const rec={ phase:(g("tfPhase").value||"").trim()||"Phase 1", track:(g("tfTrack").value||"").trim()||"Core",
    cat:(g("tfCat").value||"").trim()||"Learn", title:(g("tfTitle").value||"").trim(),
    diff:Math.max(1,Math.min(5,parseInt(g("tfDiff").value)||3)), xp:Math.max(0,parseInt(g("tfXp").value)||0) };
  if(!rec.title){ alert("Title required"); return; }
  if(editTask){
    const custom=DB.customTasks.find(x=>x.id===editTask);
    if(custom) Object.assign(custom,rec); else DB.overrides[editTask]=rec;
    editTask=null;
  }else{
    if(!idv){ alert("ID required"); return; }
    if(TASKS.some(x=>x.id===idv)||BUILTIN_TASKS.some(x=>x.id===idv)){ alert("ID already exists"); return; }
    DB.customTasks.push(Object.assign({id:idv},rec));
  }
  commitConfig();
}
function addTrophy(){
  const g=id=>document.getElementById(id);
  const name=(g("trName").value||"").trim(); if(!name){ alert("Name required"); return; }
  const type=g("trType").value; const raw=(g("trVal").value||"").trim(); let rule={type};
  if(type==="xp"||type==="level"||type==="tasks"){ rule.value=parseInt(raw)||0; }
  else if(type==="phase"){ if(!raw){ alert("Enter a phase name (e.g. Phase 2)"); return; } rule.value=raw; }
  const tid="c"+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
  DB.customTrophies.push({id:tid,ico:(g("trIco").value||"🏅").trim()||"🏅",name,
    desc:(g("trDesc").value||"").trim(),tier:g("trTier").value,rule});
  commitConfig();
}
function addChallenge(){
  const g=id=>document.getElementById(id);
  const name=(g("chName").value||"").trim(); if(!name){ alert("Name required"); return; }
  const type=g("chType").value; let taskIds=[], count=0;
  if(type==="tasks"){
    taskIds=(g("chIds").value||"").split(",").map(s=>s.trim()).filter(Boolean);
    if(!taskIds.length){ alert("Enter at least one task ID"); return; }
    const valid=new Set(TASKS.map(t=>t.id)); const bad=taskIds.filter(i=>!valid.has(i));
    if(bad.length){ alert("Unknown task IDs: "+bad.join(", ")); return; }
  }else{ count=Math.max(1,parseInt(g("chCount").value)||5); }
  const tid="ch"+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
  const trophyId="cht"+tid;
  DB.customTrophies.push({id:trophyId,ico:(g("chTico").value||"🏅").trim()||"🏅",
    name:(g("chTname").value||name).trim(),desc:"Challenge: "+name,tier:g("chTier").value,
    rule:{type:"manual"},challenge:true});
  DB.challenges=DB.challenges||[];
  DB.challenges.push({id:tid,name,desc:(g("chDesc").value||"").trim(),goalType:type,taskIds,count,
    xp:Math.max(0,parseInt(g("chXp").value)||0),trophyId,startedAt:Date.now(),
    days:Math.max(1,parseInt(g("chDays").value)||7),active:true});
  commitConfig(); checkChallenges();
}
function exportAll(){
  const blob=new Blob([JSON.stringify(DB,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob); const a=document.createElement("a");
  a.href=url; a.download="rt-tracker-all.json"; a.click(); URL.revokeObjectURL(url);
  toast("task","Full backup exported","rt-tracker-all.json");
}
function importAllHandler(e){
  const file=e.target.files[0]; if(!file) return;
  const r=new FileReader();
  r.onload=()=>{ try{ const d=JSON.parse(r.result); if(!d.users) throw 0;
      DB=normalizeDB(d); localStorage.setItem(KEY,JSON.stringify(DB));
      reselect(); rebuildTasks(); primeAll(); adminUnlocked=false; closeModal(); renderAll();
      toast("task","All data imported","every profile restored"); }
    catch(err){ alert("Invalid backup file"); } };
  r.readAsText(file);
}
function importLegacyHandler(e){          // server mode: seed accounts from browser "Export ALL"
  const file=e.target.files[0]; if(!file) return;
  const r=new FileReader();
  r.onload=async ()=>{ let d; try{ d=JSON.parse(r.result); }catch(err){ alert("Invalid file"); return; }
    if(!d.users){ alert("Not a tracker backup (no users)"); return; }
    const res=await api("POST","/api/admin/import-legacy",d);
    if(!res.ok){ toast("task","Import failed",(res.j&&res.j.error)||("HTTP "+res.status)); return; }
    await refreshState(); adminRender();
    toast("task","Imported "+(res.j.created||0)+" account(s)","temp password = username"); };
  r.readAsText(file);
}

async function onAdminClick(e){
  const a=e.target.closest("[data-act]"); if(!a) return;
  const act=a.dataset.act, id=a.dataset.id;
  const g=x=>document.getElementById(x);
  const rerender=()=>{ persistConfig(); rebuildTasks(); reselect(); renderAll(); adminRender(); };  // offline: whole-DB write
  const fail=res=>toast("task","Failed",(res.j&&res.j.error)||("HTTP "+res.status));
  const done=async res=>{ if(!res.ok) return fail(res); await refreshState(); adminRender(); };
  switch(act){
    case "close": return closeModal();
    case "tab": adminTab=a.dataset.tab; editTask=null; return adminRender();
    case "tedit": editTask=id; return adminRender();
    case "tcancel": editTask=null; return adminRender();

    // ---- profiles / accounts ----
    case "uswitch":                                   // offline only (no switching with login accounts)
      if(SERVER) return;
      DB.currentUser=id; reselect(); save(); renderAll(); checkChallenges(); return adminRender();
    case "urename":
      if(SERVER){ const n=(prompt("New username:",DB.users[id].name)||"").trim(); if(!n) return;
        return done(await api("POST","/api/admin/users/"+id+"/rename",{username:n})); }
      { const n=(prompt("Rename profile:",DB.users[id].name)||"").trim(); if(n){ DB.users[id].name=n; rerender(); } return; }
    case "uadmin":
      if(SERVER) return done(await api("POST","/api/admin/users/"+id+"/admin",{is_admin:!DB.users[id].isAdmin}));
      DB.users[id].isAdmin=!DB.users[id].isAdmin; return rerender();
    case "upw":                                       // server only: set another user's password
      if(!SERVER) return;
      { const p=prompt("New password for "+DB.users[id].name+" (min 6 chars):"); if(!p) return;
        const r=await api("POST","/api/admin/users/"+id+"/password",{password:p});
        return r.ok?toast("task","Password set",DB.users[id].name):fail(r); }
    case "ureset":
      if(SERVER){ if(!confirm("Reset progress for "+DB.users[id].name+"?")) return;
        return done(await api("POST","/api/admin/users/"+id+"/reset")); }
      if(confirm("Reset ALL progress for "+DB.users[id].name+"?")){
        DB.users[id].progress=blankProgress(); DB.users[id].progress._primed=true; rerender(); } return;
    case "udel":
      if(SERVER){ if(!confirm("Delete account "+DB.users[id].name+" and its progress?")) return;
        return done(await api("DELETE","/api/admin/users/"+id)); }
      { if(Object.keys(DB.users).length<=1){ alert("Cannot delete the only profile."); return; }
        if(!confirm("Delete profile "+DB.users[id].name+" and its progress?")) return;
        delete DB.users[id]; if(DB.currentUser===id) DB.currentUser=Object.keys(DB.users)[0];
        reselect(); return rerender(); }
    case "uadd":
      if(SERVER){ const n=(g("newUserName").value||"").trim(), p=(g("newUserPass").value||"");
        if(!n||!p){ alert("Username and password required"); return; }
        return done(await api("POST","/api/admin/users",
          {username:n,password:p,is_admin:g("newUserAdmin").checked,avatar:(g("newUserAv").value||"").trim()})); }
      { const n=(g("newUserName").value||"").trim(); if(!n){ alert("Name required"); return; }
        addUser(n,(g("newUserAv").value||"").trim(),g("newUserAdmin").checked); return rerender(); }

    // ---- tasks (shared config) ----
    case "tsave": return saveTask();
    case "tdel": {
        if(!confirm("Delete task "+id+"? Built-ins can be restored later.")) return;
        if(DB.customTasks.some(x=>x.id===id)) DB.customTasks=DB.customTasks.filter(x=>x.id!==id);
        else if(!DB.deleted.includes(id)) DB.deleted.push(id);
        delete DB.overrides[id]; if(editTask===id) editTask=null; return commitConfig(); }
    case "trestore": if(confirm("Restore built-in tasks and discard all edits/deletions? Custom tasks are kept.")){
        DB.deleted=DB.deleted.filter(x=>DB.customTasks.some(c=>c.id===x)); DB.overrides={}; editTask=null; commitConfig(); } return;

    // ---- trophies ----
    case "trophadd": return addTrophy();
    case "trophdel": DB.customTrophies=(DB.customTrophies||[]).filter(x=>x.id!==id); return commitConfig();
    case "grgrant": { const uu=g("grUser").value, tt=g("grTroph").value;
        DB.users[uu].progress.granted[tt]=true;
        if(!DB.users[uu].progress.trophyShown.includes(tt)) DB.users[uu].progress.trophyShown.push(tt);
        toast("task","Trophy granted",DB.users[uu].name); return commitUser(uu); }
    case "grrevoke": { const uu=g("grUser").value, tt=g("grTroph").value;
        delete DB.users[uu].progress.granted[tt]; return commitUser(uu); }

    // ---- challenges ----
    case "chadd": return addChallenge();
    case "chdel": { const c=(DB.challenges||[]).find(x=>x.id===id);
        if(c&&c.trophyId) DB.customTrophies=(DB.customTrophies||[]).filter(t=>t.id!==c.trophyId);
        DB.challenges=(DB.challenges||[]).filter(x=>x.id!==id); return commitConfig(); }
    case "chtoggle": { const c=(DB.challenges||[]).find(x=>x.id===id); if(c) c.active=!c.active; return commitConfig(); }
    case "chrestart": { const c=(DB.challenges||[]).find(x=>x.id===id); if(!c) return;
        c.startedAt=Date.now();
        if(SERVER){ persistConfig();
          for(const [uidk,u] of Object.entries(DB.users)){
            if(u.progress.challengesDone && u.progress.challengesDone[id]){ delete u.progress.challengesDone[id]; persistUser(uidk); } }
          rebuildTasks(); renderAll(); adminRender(); return; }
        for(const u of Object.values(DB.users)){ if(u.progress.challengesDone) delete u.progress.challengesDone[id]; }
        return commitConfig(); }

    // ---- data ----
    case "setpin": { if(SERVER) return; const p=(g("newPin").value||"").trim();
        if(p){ DB.settings.adminPin=p; save(); toast("task","PIN updated",""); } return; }
    case "chpw": { if(!SERVER) return; const r=await api("POST","/api/me/password",{old:g("pwOld").value,new:g("pwNew").value});
        return r.ok?toast("task","Password updated",""):fail(r); }
    case "exportAll":
        if(SERVER){ const r=await api("GET","/api/admin/export"); if(!r.ok) return fail(r);
          downloadJson("rt-tracker-server-backup.json",r.j); return toast("task","Full server backup exported",""); }
        return exportAll();
    case "importLegacy": if(SERVER) g("importLegacyFile").click(); return;
    case "importAll": if(!SERVER) g("importAllFile").click(); return;
    case "wipe":
        if(SERVER){ if(!confirm("WIPE all OTHER accounts, clear shared config, and reset YOUR own progress? This cannot be undone.")) return;
          const r=await api("POST","/api/admin/wipe"); if(!r.ok) return fail(r);
          await refreshState(); adminRender(); return toast("task","Wiped","other accounts removed"); }
        if(confirm("WIPE everything — all profiles, edits, trophies, challenges? This cannot be undone.")){
          localStorage.removeItem(KEY); localStorage.removeItem(OLDKEY);
          DB=loadDB(); reselect(); rebuildTasks(); primeAll(); adminUnlocked=false; closeModal(); renderAll(); } return;
  }
}

// ================= toolbar =================
function refreshFilters(){
  const keep={p:$("#fPhase").value,t:$("#fTrack").value,c:$("#fCat").value};
  fillSelect($("#fPhase"),"All phases", phaseList());
  fillSelect($("#fTrack"),"All tracks", uniq("track"));
  fillSelect($("#fCat"),"All categories", uniq("cat"));
  if(phaseList().includes(keep.p)) $("#fPhase").value=keep.p;
  if(uniq("track").includes(keep.t)) $("#fTrack").value=keep.t;
  if(uniq("cat").includes(keep.c)) $("#fCat").value=keep.c;
}
function initTopbar(){
  $("#switchUser").onclick=openUserMenu;
  $("#profileChip").onclick=openUserMenu;
  $("#btnLeaders").onclick=openLeaderboard;
  $("#btnAdmin").onclick=openAdmin;
}
function initToolbar(){
  ["#q","#fPhase","#fTrack","#fCat","#fStatus"].forEach(s=>$(s).addEventListener("input",renderPhases));
  $("#expandAll").onclick=()=>{ const ps=phaseList(); const anyC=ps.some(p=>state.collapsed[p]);
    ps.forEach(p=>state.collapsed[p]=!anyC); save(); renderPhases();
    $("#expandAll").textContent=anyC?"Collapse all":"Expand all"; };
  $("#export").onclick=()=>{
    const blob=new Blob([JSON.stringify(state,null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob); const a=document.createElement("a");
    a.href=url; a.download="rt-progress-"+cur().name.replace(/[^a-z0-9_-]+/gi,"_")+".json"; a.click(); URL.revokeObjectURL(url);
    toast("task","Backup exported",cur().name+"'s progress");
  };
  $("#importBtn").onclick=()=>$("#importFile").click();
  $("#importFile").onchange=e=>{ const f=e.target.files[0]; if(!f) return;
    const r=new FileReader(); r.onload=()=>{ try{ const s=JSON.parse(r.result);
        const p=normProg({done:s.done,collapsed:s.collapsed,achShown:s.achShown,trophyShown:s.trophyShown,
          granted:s.granted,personal:s.personal,bonusXp:s.bonusXp,challengesDone:s.challengesDone});
        p._primed=true; cur().progress=p; reselect(); save(); renderAll();
        toast("task","Backup imported","progress restored"); }
      catch(err){ toast("task","Import failed","invalid file"); } };
    r.readAsText(f); };
  $("#reset").onclick=()=>{ if(confirm("Reset ALL progress for "+cur().name+"? Export a backup first if unsure.")){
    cur().progress=blankProgress(); cur().progress._primed=true; reselect(); save(); renderAll(); } };
}

function renderAll(){
  rebuildTasks(); refreshFilters();
  renderHeader(); renderBeginnerHome(); renderChallenges(); renderMyTasks(); renderPhases(); renderTrophies(); renderAch();
}

// ================= boot =================
function initMode(){
  document.body.classList.toggle("beginner", UIMODE==="beginner");
  const b=document.getElementById("modeToggle");
  if(b) b.onclick=()=>setMode(UIMODE==="beginner"?"pro":"beginner");
  syncModeBtn();
}
function startApp(){
  rebuildTasks(); primeAll(); initTopbar(); initToolbar(); applyModeUI(); initMode(); renderAll(); checkChallenges();
}
function applyModeUI(){
  if(SERVER){
    $("#switchUser").textContent="Log out";
    $("#switchUser").onclick=doLogout;
    $("#profileChip").onclick=openAccountMenu;
  }
}
function applyServerState(s){
  ME=s.me; CSRF=s.csrf; SRVSTATS=(s.me&&s.me.stats)||null;   // F0: authoritative stats for me
  DB={ users:{}, currentUser:String(s.me.id), settings:{},
       overrides:(s.config&&s.config.overrides)||{}, customTasks:(s.config&&s.config.customTasks)||[],
       deleted:(s.config&&s.config.deleted)||[], customTrophies:(s.config&&s.config.customTrophies)||[],
       challenges:(s.config&&s.config.challenges)||[] };
  for(const [idk,u] of Object.entries(s.users||{})){
    DB.users[idk]={ id:idk, name:u.name, avatar:u.avatar, isAdmin:u.isAdmin,
                    stats:u.stats||null, progress:normProg(u.progress||{}) };   // F0: per-user authoritative stats
  }
  reselect();
}
async function refreshState(){ const r=await api("GET","/api/state");
  if(r.ok){ applyServerState(r.j); rebuildTasks(); renderAll(); } return r.ok; }
async function doLogout(){ await api("POST","/api/logout"); location.reload(); }
function openAccountMenu(){
  const ov=modal(`<div class="mhead"><h3>${cur().avatar||"👤"} ${escapeHtml(cur().name)}</h3><span class="x" data-act="close">✕</span></div>
    <div class="fbox"><b style="font-size:12px;color:#fff">Change your password</b>
      <div class="field"><label>Current password</label><input type="password" id="pwOld" autocomplete="current-password"></div>
      <div class="field"><label>New password</label><input type="password" id="pwNew" autocomplete="new-password"></div>
      <div class="row" style="margin-top:6px"><button class="btn" data-act="chpw">Update password</button></div></div>
    <div class="row"><button class="btn danger" data-act="logout">Log out</button><button class="btn" data-act="close">Close</button></div>`);
  ov.addEventListener("click",async e=>{
    const a=e.target.closest("[data-act]"); if(!a) return; const act=a.dataset.act;
    if(act==="close") return closeModal();
    if(act==="logout") return doLogout();
    if(act==="chpw"){ const r=await api("POST","/api/me/password",{old:$("#pwOld").value,new:$("#pwNew").value});
      if(!r.ok) toast("task","Failed",(r.j&&r.j.error)||""); else { closeModal(); toast("task","Password updated",""); } }
  });
}
function showLogin(msg){
  const ov=document.createElement("div"); ov.className="overlay"; ov.id="loginOv";
  ov.innerHTML=`<div class="modal" style="max-width:390px">
    <div class="mhead"><h3>🔐 Red Team Tracker — Sign in</h3></div>
    <div class="note" id="loginErr" style="border-left-color:var(--red);${msg?"":"display:none"}">${msg?escapeHtml(msg):""}</div>
    <div class="field"><label>Username</label><input type="text" id="loginUser" autocomplete="username"></div>
    <div class="field"><label>Password</label><input type="password" id="loginPass" autocomplete="current-password"></div>
    <div class="row" style="margin-top:10px"><button class="btn" id="loginBtn" style="flex:1">Sign in</button></div>
    <div class="note" style="border-left-color:var(--muted)">First run? The admin username &amp; password were printed in the server console.</div>
  </div>`;
  document.body.appendChild(ov);
  const submit=async ()=>{
    const r=await api("POST","/api/login",{username:$("#loginUser").value.trim(),password:$("#loginPass").value});
    if(!r.ok){ const e=$("#loginErr"); e.style.display=""; e.textContent=(r.j&&r.j.error)||"Login failed"; return; }
    CSRF=r.j.csrf; ov.remove();
    const st=await api("GET","/api/state"); if(st.ok){ applyServerState(st.j); startApp(); }
  };
  $("#loginBtn").onclick=submit;
  $("#loginPass").onkeydown=e=>{ if(e.key==="Enter") submit(); };
  $("#loginUser").focus();
}
async function boot(){
  let r; try{ r=await fetch("/api/state",{headers:{"Accept":"application/json"}}); }catch(e){ r=null; }
  if(r && r.status===401){ SERVER=true; showLogin(); return; }
  if(r && r.ok){ let s=null; try{ s=await r.json(); }catch(e){}
    if(s && s.me){ SERVER=true; applyServerState(s); startApp(); return; } }
  SERVER=false; DB=loadDB(); reselect(); startApp();     // offline localStorage mode
}
boot();
</script>
</body>
</html>
"""

html = (TEMPLATE
        .replace("__TASKS_JSON__", tasks_json)
        .replace("__RANKS_JSON__", ranks_json)
        .replace("__GUIDES_JSON__", guides_json)
        .replace("__LEVEL_BASE__", str(LEVEL_BASE))
        .replace("__LEVEL_STEP__", str(LEVEL_STEP)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote", OUT, "(", len(html), "bytes )")
