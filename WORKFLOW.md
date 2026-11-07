# Workflow: code-first CAD → Fusion via MCP

## The pipeline
```
model.py (build123d)  ->  model.step  +  report.md (mass per part)
        |
prep_parts.py         ->  parts/NN_<label>.step  +  parts/index.json (name, rgb, solid count)
        |
Fusion via MCP execute_code:
   0_clear_design.py      threads first, then the timeline
   1_import_parts.py      batches of about 15 parts per call
   2_names_materials.py   names, flat colours, density = report mass / volume
   save                   "vNNN <description>"
   3_add_threads.py       modelled ISO threads, LAST
   save                   "vNNN + threads"
   render_view            check it yourself before reporting to the user
```

Each file in `scripts/fusion/` is the body of one `execute_code` call. Before sending one, edit the constants at the top (paths, batch range). `app`, `design` and `adsk` are already defined inside `execute_code`.

## Rules learned the hard way
1. **One document.** Every script starts with `assert app.activeDocument.name == "claude"`. Never call `delete_all`, and never open the user's other designs.
2. **Delete threads before anything else.** Deleting bodies that carry modelled threads made Fusion recompute and hang; we had about 46 threads at the time. Clear `threadFeatures` first, then the timeline.
3. **Don't edit inside an import base feature.** Deleting one body there removed 75. Clear the whole thing and re-import.
4. **Import in batches of about 14–18 parts per call** to stay under the roughly 30 s MCP call timeout.
5. **Import method:** `importToNewDocument` → `TemporaryBRepManager.copy(body)` → `newdoc.close(False)` → `claude_doc.activate()` → add the bodies inside a `baseFeatures.add()` edit.
6. **Body order is stable.** Rename bodies by zipping with `index.json`, expanding parts with more than one solid to `name_1`, `name_2`, and so on.
7. **Mass matches your budget.** Copy the library "Steel" material per part and set its density to `mass_g / volume_cm3` (Fusion's density unit is kg/m³, so multiply by 1000). Fusion's mass then equals your spreadsheet.
8. **Flat appearances** (`design.appearances.add(name)` plus `.color`) are fast and reliable. Copying a library appearance and editing its colour properties is slow and sometimes ignored.
9. **Threads go last, are each wrapped in `try`, and are health-checked.** If a thread isn't healthy, delete it and list the body as failed. Countersunk screws sometimes fail; tell the user rather than hide it.
10. **Save between stages** with descriptive labels, so a crash costs one stage, not the session.
11. **Keep helper scripts in the repo**, not in temp or scratch folders, because those get wiped.
12. **Version folders are frozen.** New ideas go in `vNNN+1`, and the old one stays reproducible.
