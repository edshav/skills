#!/usr/bin/env python3
"""Repo consistency check: skill folders, marketplace entries, install lines, evals JSON."""
import json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
errors = []
market = json.loads((root / ".claude-plugin/marketplace.json").read_text())
readme = (root / "README.md").read_text()
plugin_of = {}  # skill dir -> plugin name
for p in market["plugins"]:
    if f"/plugin install {p['name']} --marketplace edshav/skills" not in readme:
        errors.append(f"README.md: no '/plugin install {p['name']} --marketplace edshav/skills' line")
    # shortcut: skill paths resolve from the repo root, true while every local plugin has source "./"
    for s in p.get("skills", []):
        d = s.removeprefix("./").rstrip("/")
        if not (root / d / "SKILL.md").is_file():
            errors.append(f"marketplace.json: plugin {p['name']} points at {s}, which has no SKILL.md")
        plugin_of[d] = p["name"]

for skill in sorted(root.glob("*/SKILL.md")):
    d = skill.parent.name
    for f in ("README.md", "LICENSE"):
        if not (skill.parent / f).is_file():
            errors.append(f"{d}/: missing {f}")
    parts = skill.read_text().split("---", 2)
    m = len(parts) == 3 and re.search(r"^name:\s*['\"]?([^'\"\s]+)", parts[1], re.M)
    if not m or m.group(1) != d:
        errors.append(f"{d}/SKILL.md: frontmatter name should be {d}")
    if d not in plugin_of:
        errors.append(f"{d}/: no plugin entry in .claude-plugin/marketplace.json")

for ev in sorted(root.glob("*/evals/*.json")):
    try:
        json.loads(ev.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"{ev.relative_to(root)}: invalid JSON: {e}")

print("\n".join(errors) or "ok")
sys.exit(1 if errors else 0)
