#!/usr/bin/env python3
"""Build a source release without local runtime state or repository metadata."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "red-team-tracker.zip"

FILES = [
    ".gitignore", ".nojekyll", "COMMUNITY_SETUP.md", "README.md",
    "base_tasks.json", "build_web.py", "build_xlsx.py", "community.html", "details_data.py",
    "firestore.rules", "guides_data.py", "index.html", "merge.py",
    "package_release.py", "questions.html", "requirements.txt", "requirements.lock", "resources.html",
    "roadmap.xlsx", "run.sh", "server.py", "tasks_data.py",
]
FILES.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT / "screenshots").glob("*.jpg")))
FILES.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT / "tests").glob("test_*.py")))

FORBIDDEN_NAMES = {".secret_key", "tracker.db", "tracker.db-wal", "tracker.db-shm"}

def main():
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("missing release files: " + ", ".join(missing))
    if any(Path(name).name in FORBIDDEN_NAMES for name in FILES):
        raise SystemExit("release allowlist contains a forbidden runtime file")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in FILES:
            archive.write(ROOT / name, Path("red-team-tracker") / name)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes, {len(FILES)} files)")

if __name__ == "__main__":
    main()
