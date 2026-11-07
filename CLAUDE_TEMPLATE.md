# CLAUDE.md template: copy into a new project as `CLAUDE.md`

## Fusion 360 (MCP server `fusion360`)
- Only edit the Fusion document named **`claude`**. Every `execute_code` call starts with `assert app.activeDocument.name == "claude"`.
- Never call `delete_all`. Never open, edit or close the user's other documents.
- Import, name, colour and material scripts: `<kit>/scripts/fusion/`. Follow the order in `<kit>/WORKFLOW.md`.
- Delete thread features before deleting bodies. Import in batches of about 15 parts. Add threads last. Save before and after adding threads.
- After building, take a `render_view` and look at it before reporting.

## Modelling
- Source of truth: build123d in `.venv`. Every version is a frozen folder `vNNN/`; changes go in a new version.
- Each version reports mass per part, interference, clearance and overall size, with pass or fail against the limits.
- Don't install packages without asking.

## Working with the user
- Build one configuration, get approval, then build the variants.
- Report measured numbers. When something failed or was skipped, say so.
