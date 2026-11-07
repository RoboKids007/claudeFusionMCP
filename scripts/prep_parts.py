"""Split an assembly STEP into one STEP per labelled part, coloured by name rules, plus index.json for the Fusion import.

usage: python prep_parts.py model.step out_dir/
Edit PAL and RULES for your project: the first rule whose prefix matches a part label wins.
Needs build123d (pip install build123d).
"""
import json
import re
import sys
from pathlib import Path

from build123d import Color, Compound, export_step, import_step

PAL = {"grey": (0.55, 0.56, 0.58), "dark": (0.13, 0.14, 0.15), "accent": (1.00, 0.42, 0.06),
       "teal": (0.00, 0.36, 0.40), "white": (0.94, 0.94, 0.92), "black": (0.05, 0.05, 0.05)}
RULES = [("screw_", "grey"), ("plate_", "dark"), ("armour_", "teal"), ("weapon_", "accent"), ("tyre_", "black")]
DEFAULT = "dark"

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for f in out.glob("*.step"):
    f.unlink()
asm = import_step(str(src))
idx, unmatched = [], set()
for i, c in enumerate(asm.children):
    label = c.label or f"part{i}"
    col = next((cc for pre, cc in RULES if label.startswith(pre)), None)
    if col is None:
        unmatched.add(label)
        col = DEFAULT
    name = re.sub(r"[^A-Za-z0-9_.-]", "_", label)
    f = (out / f"{i:02d}_{name}.step").resolve()
    c.color = Color(*PAL[col])
    try:
        export_step(c, str(f))
    except RuntimeError:
        export_step(Compound(c.solids()), str(f))
    idx.append({"file": str(f), "name": name, "rgb": list(PAL[col]), "solids": len(c.solids())})
(out / "index.json").write_text(json.dumps(idx, indent=1))
print(f"{len(idx)} parts, {sum(p['solids'] for p in idx)} solids; unmatched labels: {sorted(unmatched)}")
