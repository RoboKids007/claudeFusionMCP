# execute_code body. Adds modelled ISO threads to screw/bolt bodies. Run LAST, after saving.
# A thread goes on the largest cylinder whose radius matches a known size; unhealthy threads are deleted and reported.
PREFIXES = ("screw_", "bolt_")                                        # body-name prefixes to thread
SIZES = {0.15: "M3x0.5", 0.2: "M4x0.7", 0.25: "M5x0.8", 0.3: "M6x1"}  # radius in cm -> designation
SAVE_LABEL = "threads added"

from collections import Counter
d = adsk.fusion.Design.cast(app.activeProduct)
assert app.activeDocument.name == "claude", app.activeDocument.name
root = d.rootComponent
tf = root.features.threadFeatures
done, fails = [], []
for b in list(root.bRepBodies):
    if not b.name.startswith(PREFIXES):
        continue
    faces = [(f, round(f.geometry.radius, 3)) for f in b.faces
             if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and round(f.geometry.radius, 3) in SIZES]
    if not faces:
        fails.append(b.name); continue
    f, r = max(faces, key=lambda t: t[0].area)
    try:
        info = tf.createThreadInfo(False, "ISO Metric profile", SIZES[r], "6g")
        inp = tf.createInput(f, info)
        inp.isModeled = True
        inp.isFullLength = True
        t = tf.add(inp)
        if t.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            t.deleteMe(); fails.append(b.name)
        else:
            done.append(SIZES[r])
    except Exception:
        fails.append(b.name)
ok = app.activeDocument.save(SAVE_LABEL)
(Counter(done), fails, ok)
