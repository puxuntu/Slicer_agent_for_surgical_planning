# Runbook — Claude Code + Slicer skill baseline

Run **one step** of a guided procedure with an external Claude Code session instead of the
pipeline, and compare.

---

## A. One-time setup — already done

`.mcp.json` and `.claude/settings.json` are in this folder. Nothing to configure.

**First launch only:** run `claude` here once and **accept the workspace trust dialog** (the
directory grants don't apply until you do) and the MCP server prompt.

Check: `claude mcp list` → `slicer ✔ Connected` (once Slicer is running).

---

## B. Every Slicer session

1. Open Slicer → **SlicerAIAgent** module. Set the API key if not saved.
2. Load your patient data.
3. Type your request → **Send**. e.g. *"plan a zygomatic implant"*.
4. Let the pipeline run **past** the step you want to test.

You never paste anything into the Python console — the MCP server starts itself in step C2.

---

## C. Run the baseline on one step

1. **Back** (◀) to your target step.
2. Click **⚖**. *(Hidden = that step isn't `extension_op`/`slicer_op`; pick another.)*
3. Select **"3. Claude Code + Slicer skill (MCP)"** — this starts the MCP server.
4. Press **"Arm this step"**. Leave the prompt box empty.
5. **Now** start Claude Code — not before:
   ```sh
   cd C:/Users/20152/Desktop/slicer-skill/SlicerAgent/Slicer_agent/MCPConnection
   claude
   ```
   > ⚠️ **Order matters.** Claude Code connects to MCP servers *at startup*. Launched before
   > step 3, it finds port 2026 dead, retries 3× and marks `slicer` **failed for the whole
   > session** — no tools, and starting the server afterwards does not help.
   > Already have a session open? Run **`/mcp`** → retry `slicer`, or just restart `claude`.
6. Type your prompt for the step. Claude Code reads `current_step.md`, inspects the scene,
   reads the extension source, then calls `execute_python` once.
7. **Success** → step completes, workflow auto-advances.
   **Failure** → stays armed; fix and call again.
   **Abandon** → press **"Stop waiting"**.

---

## D. Collect

```sh
python scripts/collect_runs.py --step cb_step_8
```

Results in `logs/<stamp>_claudeCode_<Extension>_<step>_a<attempt>/`.

---

## Watch out

- **Arming is destructive and has no undo** — it deletes the pipeline's own result for that
  step and everything after it.
- **`execute_python` is not a scratchpad** — *any* successful call completes the step. A stray
  `print()` ends the run. Scene inspection (`list_nodes`, `get_node_properties`, `screenshot`)
  is safe.
- **A failed attempt is rolled back automatically** — whatever it half-built is removed and the
  scene returns to its pre-step state, so the next attempt (or the next baseline on that step)
  starts clean. Just re-arm. *(Exception: PedicleScrewPlanner, where downstream nodes are kept
  by design.)*

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Claude Code says *"the slicer MCP tools aren't present"* | it started before the server — **`/mcp` → retry `slicer`**, or restart `claude`. The step stays armed; no need to re-arm |
| Claude Code says nothing is listening on 2026 | check from a terminal: `claude mcp list` → `slicer ✔ Connected`. If that passes, its own probe was wrong/stale — use `/mcp` |
| ⚖ missing | step isn't `extension_op`/`slicer_op` — pick another |
| *"could not start … automatically"* + *"not found"* | `git submodule update --init` |
| *"could not start … automatically"* + Python error | port 2026 busy, or paste the script by hand to see the traceback |
| `claude mcp list` → `✘ Failed to connect` | Slicer not running, or step C3 not done yet |
| Claude Code can't read extension source | trust dialog not accepted — relaunch (**A**) |
| Step advanced after a trivial command | a probe through `execute_python` — rewind and re-arm |
| Comparing conditions on one step | Back → ⚖ → pick → run, repeat. Each rewind restores the identical pre-step state, so the order you test in doesn't matter |

Stop the server: `mcpLogic.stop()` in Slicer's Python console.
Start it by hand instead: paste `Resources/Skills/slicer-skill-full/slicer-mcp-server.py` there.
