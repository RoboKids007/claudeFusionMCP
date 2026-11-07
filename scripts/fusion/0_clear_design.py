# execute_code body. Clears the "claude" design safely: thread features FIRST (deleting threaded bodies can hang Fusion),
# then every timeline item, newest first. Run it once; if it times out, run it again.
d = adsk.fusion.Design.cast(app.activeProduct)
assert app.activeDocument.name == "claude", app.activeDocument.name
root = d.rootComponent
tf = root.features.threadFeatures
for i in range(tf.count - 1, -1, -1):
    tf.item(i).deleteMe()
tl = d.timeline
for i in range(tl.count - 1, -1, -1):
    ent = tl.item(i).entity
    if ent is not None:
        ent.deleteMe()
(tl.count, root.bRepBodies.count)
