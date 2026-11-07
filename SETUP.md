# Setup: Fusion 360 MCP for Claude Code (macOS)

Tested on macOS (Apple Silicon) with Fusion Personal (free licence), Claude Code 2.1, uv 0.12 and server commit `19b9f1e`.

```
Claude Code ⇄ (stdio MCP) ⇄ fusion360-mcp-server ⇄ (TCP localhost:9876) ⇄ Fusion360MCP add-in ⇄ Fusion main thread
```

## 0. Prerequisites
- **Autodesk Fusion**. The Personal licence works: scripts and add-ins are allowed. Personal limits how many documents can be editable at once, so give Claude one dedicated document.
- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Claude Code**: `claude --version`
- Optional, for code-first modelling: Python 3.11+ with `build123d` in a venv:
  ```bash
  uv venv .venv && uv pip install --python .venv build123d
  ```

## 1. Get the server and review it
```bash
mkdir -p ~/tools && cd ~/tools
git clone https://github.com/faust-machines/fusion360-mcp-server
cd fusion360-mcp-server
git log -1 --format='%H %cd'      # note the commit you reviewed
```

Before you install it, check that:
- it only talks to localhost;
- it makes no outbound network calls;
- you're OK with `execute_code`, which runs arbitrary Python inside Fusion.

Claude can do this review for you. Ask it to "clone and review this MCP server before installing".

## 2. Install the Fusion add-in
```bash
ADDINS="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
mkdir -p "$ADDINS"
cp -R addon "$ADDINS/Fusion360MCP"
```
On Windows, copy it to `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\Fusion360MCP` instead.

Then, in Fusion:
1. Press **Shift+S** and open the **Add-Ins** tab.
2. If **Fusion360MCP** isn't listed:
   - tick **"From device"** under *Source*, because the default filter shows only Fusion's built-in add-ins;
   - or click **+** → *Script or add-in from device* and pick the folder. In the Mac file picker, press **Cmd+Shift+G** and paste the path, because `Library` is hidden.
3. Switch on **Run**, and tick **Run on startup** if you want it every time.
4. **Check:** the TEXT COMMANDS window shows `[MCP] Server listening on localhost:9876`. From a terminal:
   ```bash
   nc -z localhost 9876 && echo open
   ```

## 3. Register the server with Claude Code (user scope)
Run this in a normal terminal. Inside Claude Code, prefix it with `!`.
```bash
claude mcp add -s user fusion360 -- uv run --directory ~/tools/fusion360-mcp-server fusion360-mcp-server --mode socket
claude mcp list        # fusion360 should show as connected
```
- **Use `-s user`.** Without it, the server is registered only for the folder you ran the command in. That was our first mistake: we ran it from `~` and the project session never saw the tools.
- **Prefer the PyPI release?** Register it like this instead:
  ```bash
  claude mcp add -s user fusion360 -- uvx fusion360-mcp-server --mode socket
  ```
- **Expect a block if Claude tries this itself.** Claude Code's safety check stops it installing third-party code or changing its own MCP config without you. Run these two steps yourself.

## 4. Restart and verify
1. Restart Claude Code with `/restart` or by quitting and relaunching.
2. Ask Claude to call `ping`. It should return `{"ok": true, "status": "pong"}`.
3. In Fusion, create a new empty design and save it as **`claude`**. This is the only document Claude may edit.
4. Ask Claude to run `get_scene_info` and confirm the active document is `claude`.

## 5. Uninstall
```bash
claude mcp remove -s user fusion360
rm -rf "$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Fusion360MCP"
```
Stop the add-in in Fusion first: **Shift+S** → Add-Ins → Fusion360MCP → Stop.

## Troubleshooting
| Symptom | Fix |
|---|---|
| No `mcp__fusion360__*` tools in Claude | Registered in the wrong scope or folder. Re-add with `-s user`, then restart Claude Code. |
| `ping` fails or times out | The add-in isn't running. Shift+S → Run, then check port 9876. |
| A call dies at about 30 s | Split the work into smaller batches (see WORKFLOW.md). |
| Fusion hangs on delete | Thread features are being recomputed. Kill and restart Fusion, then delete the threads before the bodies next time. |
| An edit landed in the wrong design | Every script must start with `assert app.activeDocument.name == "claude"`. |

**Security:** the socket has no authentication. Never bind it to `0.0.0.0` on a network you don't trust.
