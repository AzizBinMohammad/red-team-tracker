# -*- coding: utf-8 -*-
"""Merge base tasks + authored details -> tasks_full.json (single source for both outputs)."""
import json, os

base = json.load(open("base_tasks.json"))
details = {}
if os.path.exists("details.json"):
    details = json.load(open("details.json"))

full = []
for t in base:
    d = details.get(t["id"], {})
    full.append({
        **t,
        "why": d.get("why", ""),
        "how": d.get("how", []),
        "tools": d.get("tools", []),
        "resources": d.get("resources", []),
        "doneWhen": d.get("doneWhen", ""),
        "pitfall": d.get("pitfall", ""),
    })

json.dump(full, open("tasks_full.json", "w"), ensure_ascii=False, indent=1)
have = sum(1 for t in full if t["why"])
print(f"tasks_full.json: {len(full)} tasks, {have} with authored detail")
