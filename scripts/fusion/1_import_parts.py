# execute_code body. Imports one batch of per-part STEPs into the "claude" design.
# Run it repeatedly, moving START:STOP along (about 15 parts per call keeps it under the ~30 s MCP timeout).
import json
INDEX = "/ABSOLUTE/PATH/TO/parts/index.json"
START, STOP, TAG = 0, 15, "1"

claude_doc = app.activeDocument
assert claude_doc.name == "claude", claude_doc.name
idx = json.load(open(INDEX))
tbm = adsk.fusion.TemporaryBRepManager.get()
temps = []
for part in idx[START:STOP]:
    opts = app.importManager.createSTEPImportOptions(part["file"])
    nd = app.importManager.importToNewDocument(opts)
    d2 = adsk.fusion.Design.cast(nd.products.itemByProductType("DesignProductType"))
    bodies = list(d2.rootComponent.bRepBodies) + [b for oc in d2.rootComponent.allOccurrences for b in oc.component.bRepBodies]
    temps += [tbm.copy(b) for b in bodies]
    nd.close(False)                       # never save the temporary import docs
claude_doc.activate()
dd = adsk.fusion.Design.cast(app.activeProduct)
base = dd.rootComponent.features.baseFeatures.add()
base.startEdit()
for t in temps:
    dd.rootComponent.bRepBodies.add(t, base)
base.finishEdit()
base.name = "import batch %s" % TAG
(len(temps), dd.rootComponent.bRepBodies.count, sum(p["solids"] for p in idx))
