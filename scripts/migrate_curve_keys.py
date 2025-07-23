#!/usr/bin/env python3
"""
Migrate the repo from old combined-key format to
per-resource keys (<paper>-label / <paper>-gpu).

• Updates data/curves.json
• Rewrites any *.py / *.md / *.rst / *.ipynb that refer to old keys
  (Dragut-2019-label, Stiennon2021-label, …).

Run once from repo root:

    python scripts/migrate_curve_keys.py
"""
from __future__ import annotations
import json, re, shutil, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[1]
CURVES = ROOT / "data" / "curves.json"

# ---------------------------------------------------------------------
# Part 1: normalise curves.json
# ---------------------------------------------------------------------
with CURVES.open() as f:
    curves = json.load(f)

out: dict[str, dict] = {}
obsolete: set[str]   = set()

for key, block in curves.items():
    # already resource-split → copy
    if "-label" in key or "-gpu" in key:
        out[key] = block
        continue

    # split combined entries into two resources if possible
    base = re.sub(r"[-_ ]?20\d\d.*", "2021", key) if "Stiennon" in key else key
    if "label_curve" in block:
        out[f"{base}-label"] = {
            "label_curve": block["label_curve"],
            "rmse": block.get("rmse"),
            "ci_low": block.get("ci_low"),
            "ci_high": block.get("ci_high"),
            "cost_per_unit": block.get("cost_per_unit", 0.02),
        }
    if "gpu_curve" in block:
        out[f"{base}-gpu"] = {
            "gpu_curve": block["gpu_curve"],
            "rmse": block.get("rmse"),
            "ci_low": block.get("ci_low"),
            "ci_high": block.get("ci_high"),
            "cost_per_unit": block.get("cost_per_unit", 1.40),
        }
    obsolete.add(key)

if obsolete:
    bak = CURVES.with_suffix(".bak")
    shutil.copy(CURVES, bak)
    CURVES.write_text(json.dumps(out, indent=2))
    print(f"✓ curves.json updated → backup at {bak.name}")
else:
    print("✓ curves.json already uses per-resource keys")

# ---------------------------------------------------------------------
# Part 2: rewrite hard-coded keys in code / docs
# ---------------------------------------------------------------------
PATTERNS = {
    r"Dragut-2019-label[-_]?phone?":      "Dragut-2019-label",
    r"Dragut-2019-label":                 "Dragut-2019-label",
    r"Stiennon2021-label\"":             "Stiennon2021-label-label\"",
    r"Stiennon2021-label\b":             "Stiennon2021-label-label",
}

FILES = list(ROOT.rglob("*.py")) + \
        list(ROOT.rglob("*.md")) + \
        list(ROOT.rglob("*.rst")) + \
        list(ROOT.rglob("*.ipynb"))

subs_total = 0
for path in FILES:
    txt = path.read_text(encoding="utf-8")
    new = txt
    for pat, repl in PATTERNS.items():
        new = re.sub(pat, repl, new)
    if new != txt:
        path.write_text(new, encoding="utf-8")
        subs_total += 1
        print(f"· patched {path.relative_to(ROOT)}")

if subs_total:
    print(f"✓ {subs_total} files patched")
else:
    print("✓ no hard-coded keys to fix")
