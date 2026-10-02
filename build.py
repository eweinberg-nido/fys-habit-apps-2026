#!/usr/bin/env python3
"""
Scans the teacher/block folders and writes apps.js, the manifest that
index.html reads. Run this again whenever apps are added or removed:

    python3 build.py

Folder layout:  <teacher>/<block>/<student-names>.html
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Folder name -> name shown on the site, in display order.
TEACHERS = {
    "seavey": "Mr. Seavey",
    "cade": "Ms. Cade",
    "kim": "Ms. Kim",
}

LOGO_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

CATEGORIES_FILE = "categories.MD"

# Students picked their own category labels, so the wording varies a lot
# ("Procrastinating", "get started on homework", "Doomscrool."). Each rule maps
# keywords found in a label onto one standard topic. A label can match several
# topics. Topics appear on the site in this order.
TOPICS = [
    ("procrastination", "Procrastination & Motivation", ["procrastinat", "procastinat", "get started", "motivat"]),
    ("screen-time", "Screen Time & Doomscrolling", ["screen", "doom", "scroll", "phone"]),
    ("focus", "Focus & Distraction", ["focus", "distract", "concentrat"]),
    ("studying", "Studying & Homework", ["study", "homework"]),
    ("time-management", "Time Management & Organization", ["time man", "organiz", "organis", "organz", "organize", "planner"]),
    ("sleep", "Sleep", ["sleep"]),
    ("food", "Healthy Eating", ["food", "eating", "nutrition"]),
]


def read_title(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def split_title(title):
    """'FocusFlow - Mindful Focus Workspace' -> ('FocusFlow', 'Mindful Focus Workspace')"""
    for sep in (" - ", " | ", " – ", " — ", ": "):
        if sep in title:
            name, tagline = title.split(sep, 1)
            return name.strip(), tagline.strip()
    return title, ""


def student_names(stem):
    """'agustina-beatrix-ryo' -> 'Agustina, Beatrix & Ryo'"""
    names = [p.capitalize() for p in re.split(r"[-_]+", stem) if p]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " & " + names[-1]


def load_categories():
    """categories.MD rows: <student label> TAB <drive link> TAB <file slug>.
    Returns {slug: [student labels]}."""
    path = ROOT / CATEGORIES_FILE
    labels = {}
    if not path.is_file():
        return labels
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in line.split("\t")]
        if len(cols) < 2 or not cols[0]:
            continue
        slug = cols[-1].lower()
        labels.setdefault(slug, []).append(cols[0].rstrip(" ."))
    return labels


def match_topics(labels):
    text = " ".join(labels).lower()
    return [tid for tid, _, words in TOPICS if any(w in text for w in words)]


def find_logo():
    # Prefer a file named exactly logo.<ext>; otherwise any image with "logo" in its name.
    for ext in LOGO_EXTS:
        if (ROOT / ("logo" + ext)).is_file():
            return "logo" + ext
    for p in sorted(ROOT.iterdir()):
        if p.is_file() and p.suffix.lower() in LOGO_EXTS and "logo" in p.name.lower():
            return p.name
    return None


def main():
    folders = [d.name for d in ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")]
    order = list(TEACHERS) + sorted(f for f in folders if f not in TEACHERS)

    categories = load_categories()
    seen = set()
    classes = []
    total = 0
    for slug in order:
        tdir = ROOT / slug
        if slug not in TEACHERS and not any(tdir.glob("*/*.html")):
            continue  # skip unrelated folders
        blocks = []
        if tdir.is_dir():
            for bdir in sorted(d for d in tdir.iterdir() if d.is_dir()):
                apps = []
                for f in sorted(bdir.glob("*.html")):
                    name, tagline = split_title(read_title(f))
                    labels = categories.get(f.stem.lower(), [])
                    topics = match_topics(labels)
                    seen.add(f.stem.lower())
                    if not labels:
                        print(f"  note: {f.stem} has no category in {CATEGORIES_FILE}")
                    elif not topics:
                        print(f"  note: {f.stem} label {labels!r} matched no topic -- add a keyword to TOPICS")
                    apps.append({
                        "name": name or student_names(f.stem),
                        "tagline": tagline,
                        "students": student_names(f.stem),
                        "path": f.relative_to(ROOT).as_posix(),
                        "topics": topics,
                        "studentLabel": "; ".join(labels),
                    })
                if apps:
                    blocks.append({"block": bdir.name, "apps": apps})
                    total += len(apps)
        classes.append({
            "id": slug,
            "teacher": TEACHERS.get(slug, slug.capitalize()),
            "blocks": blocks,
        })

    for slug in sorted(set(categories) - seen):
        print(f"  note: {slug} is in {CATEGORIES_FILE} but has no HTML file yet")

    data = {
        "logo": find_logo(),
        "topics": [{"id": tid, "name": name} for tid, name, _ in TOPICS],
        "classes": classes,
    }
    out = ROOT / "apps.js"
    out.write_text(
        "// Generated by build.py -- do not edit by hand.\n"
        "window.GALLERY = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {out.name}: {total} apps, logo = {data['logo'] or 'none found'}")


if __name__ == "__main__":
    main()
