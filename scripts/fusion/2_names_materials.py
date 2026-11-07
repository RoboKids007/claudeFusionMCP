# execute_code body. Names bodies from index.json, gives them flat colours, and sets a per-part material whose
# density makes Fusion's mass equal your budget. MASS_G maps part name -> grams (fill it from your report).
import json, re
INDEX = "/ABSOLUTE/PATH/TO/parts/index.json"
MASS_G = {}            # e.g. {"plate_top": 61.2, "screw_M3_x12": 9.8}; empty = colours and names only
PREFIX = "proj_"

d = adsk.fusion.Design.cast(app.activeProduct)
assert app.activeDocument.name == "claude", app.activeDocument.name
root = d.rootComponent
idx = json.load(open(INDEX))
names = []
for p in idx:
    names += [p["name"]] if p["solids"] == 1 else ["%s_%d" % (p["name"], k + 1) for k in range(p["solids"])]
for b, n in zip(list(root.bRepBodies), names):
    b.name = n
rgb = {p["name"]: p["rgb"] for p in idx}

def flat(c):
    r, g, b = [int(round(v * 255)) for v in c]
    nm = "MCP_%d_%d_%d_255" % (r, g, b)
    a = d.appearances.itemByName(nm)
    if a is None:
        a = d.appearances.add(nm)
        a.color = adsk.core.Color.create(r, g, b, 255)
    return a

groups = {}
for b in root.bRepBodies:
    p = b.name if b.name in rgb else re.sub(r"_\d+$", "", b.name)
    groups.setdefault(p, []).append(b)
lib = [L for L in app.materialLibraries if L.name == "Fusion Material Library"][0]
seed = lib.materials.itemByName("Steel")
no_mass = []
for part, bl in groups.items():
    if part in rgb:
        for b in bl:
            b.appearance = flat(rgb[part])
    if part not in MASS_G:
        no_mass.append(part); continue
    vol = sum(b.volume for b in bl)                      # cm^3
    mat = d.materials.itemByName(PREFIX + part) or d.materials.addByCopy(seed, PREFIX + part)
    for prop in mat.materialProperties:
        if "Density" in prop.name:
            prop.value = MASS_G[part] / vol * 1000.0     # g/cm^3 -> kg/m^3
    for b in bl:
        b.material = mat
(len(groups), len(no_mass), round(sum(b.physicalProperties.mass for b in root.bRepBodies) * 1000, 1))
