# Driving a live 3D Slicer over MCP

This workspace is used to perform **one step** of a surgical-planning procedure inside a
**running** 3D Slicer, by writing Python and executing it through the MCP `execute_python`
tool. The user will type the step's request as the prompt; everything below is the standing
context for doing it well.

Take the task seriously and use everything available. If an API is uncertain, **read the
extension's source** (paths below) rather than guessing — you have the whole source tree and
the running application, so a wrong API call is a choice, not a limitation.

---

## FIRST: read `./current_step.md`

The runtime writes that file into this workspace each time a step is armed. It tells you which
procedure and which step you are performing, what the earlier steps already did, which values
and nodes the user has already chosen, and what comes next (context only).

**Read it before anything else, every time**, and check that its step id matches the request
you were given — it is rewritten on each arm, so an unmatched id means you are looking at a
stale brief and should ask rather than guess.

That file is the *same* brief the other conditions in this comparison receive automatically.
Working from the user's sentence alone would leave you with strictly less task context than
they have, which is not the comparison anyone wants to run.

---

## Launch setup (required)

Paths in this file are relative to **this workspace** (`MCPConnection/`), which sits inside
`Slicer_agent/`. The skill and the extension sources are *outside* the workspace, so reading
them needs an access grant — naming a path here is an instruction, not a permission.

That grant is already in place, in `.claude/settings.json` beside this file:

```json
{
  "permissions": {
    "additionalDirectories": [
      "C:/0APP_install/slicer/3D Slicer 5.10.0/slicer.org/Extensions-34045",
      "C:/Users/20152/Desktop/slicer-skill/SlicerAgent/External_extensions",
      "C:/Users/20152/Desktop/slicer-skill/SlicerAgent/Slicer_agent/Resources/Skills/slicer-skill-full"
    ]
  }
}
```

So the session just starts with:

```sh
cd .../Slicer_agent/MCPConnection && claude
```

`additionalDirectories` requires **absolute** paths (relative ones are not supported), which is
why those are absolute while the paths in the rest of this file are relative. On a different
machine, regenerate the third entry from **Slicer's own Python console** — *not* through
`execute_python`, for the reason in the next section:

```python
print(slicer.app.extensionsInstallPath)   # -> the Extensions-NNNNN directory
```

Equivalent one-off alternatives, if you ever need them: `claude --add-dir <path>` at launch,
or `/add-dir <path>` inside a running session.

The MCP server script ships with the skill:

    ../Resources/Skills/slicer-skill-full/slicer-mcp-server.py

The SlicerAIAgent panel runs it for you — unmodified, in Slicer's `__main__` — as soon as the
operator selects the Claude Code baseline, so nobody has to paste it into the Python console.
It listens on port 2026 and is registered for this workspace in `.mcp.json`.

If the `slicer` MCP tools are missing from your session, the most likely cause is that this
session **started before the server did** — Claude Code connects to MCP servers at startup, and
a server that was down then is marked failed for the whole session. Tell the operator to run
`/mcp` and retry `slicer` (or restart the session); the armed step survives, so you can fire
straight away afterwards. Do not try to start the server yourself, and do not conclude from a
shell probe that Slicer is down — check `/mcp` first.

---

## The execution contract

MCP tools against the live application: `list_nodes`, `get_node_properties`,
`execute_python`, `screenshot`, `load_sample_data`.

`execute_python` is the only way to affect the scene. While a step is armed:

- Your code is validated (see the rejection list below) and then executed **synchronously**
  in Slicer's `__main__`, and the real stdout/stderr comes back to you.
- **On success the step is marked complete and the workflow advances.** One successful call
  ends your turn on that step — so send the *complete* step, not a fragment.
- **On failure nothing advances and the step stays armed.** Read the error, fix it, call
  `execute_python` again. Iterating is expected; every attempt is recorded separately.

### `execute_python` is not a scratchpad

There is no separate "run this to look around" mode: **any** call that succeeds ends the step,
including a one-line probe. So never use it to explore — `print(slicer.app.extensionsInstallPath)`
or `print(dir(logic))` would succeed, advance the workflow, and end your turn with the step
recorded as done by a print statement.

Gather what you need the safe way instead:

- **the scene** — `list_nodes`, `get_node_properties`, `screenshot` (read-only, never advance)
- **the API** — read the extension's source from disk (paths below)
- **anything else** — ask the user to run it in Slicer's own Python console

Then send the complete step in **one** `execute_python` call.

Do not ask the user to run the step's code for you, and do not stop at proposing code — when
you have the whole step, call the tool.

---

## Code that is REJECTED before it runs

Static analysis rejects the code outright if it uses any of these. A rejection is not a
failed attempt at the task — it is a wasted one, so read this list once and stay inside it.

**Blocked modules:** `os`, `subprocess`, `sys`, `socket`, `urllib`, `urllib2`, `http`,
`ftplib`, `telnetlib`, `ctypes`, `mmap`, `resource`, `signal`, `pty`, `pickle`, `cPickle`,
`shelve`, `marshal`, `imp`

**Blocked functions:** `eval`, `exec`, `compile`, `execfile`, `__import__`, `open`, `file`,
`input`, `raw_input`, `getattr`, `setattr`, `delattr`, `globals`, `locals`, `vars`, `dir`

`getattr`/`vars`/`dir` being blocked means **reflective probing is unavailable** — write the
direct call you have verified from source. `hasattr` *is* allowed, as is `isinstance`.

**Allowed imports:** `slicer`, `vtk`, `qt`, `ctk`, `numpy`, `SampleData`, `SimpleITK`,
`math`, `random`, `datetime`, `collections`, `itertools`, `functools`, `json`, `re`,
`string`, `copy`, `typing`, `enum`, `statistics`, `csv`, `io`, `struct`, `traceback`,
plus anything whose name starts with `slicer`/`vtk` or contains a dot
(e.g. `BRPLib.helperFunctions`).

---

## Execution environment

- Code runs at **module level in `__main__`** — never write `self` or `cls`. Get what you
  need through local variables (`logic = widget.logic`).
- `slicer`, `vtk`, `qt`, `ctk` are **already imported**. Do not import them.
- `slicer.mrmlScene` is the live scene, `slicer.modules` every loaded module.
- Volume arrays are KJI-ordered; call `slicer.util.arrayFromVolumeModified()` after writing one.
- Slicer works in RAS internally.
- Do not change the layout or switch the active module unless the step asks for it.

---

## Start by looking at the live scene

Earlier steps of this procedure have already run and their results are in the scene. Before
writing anything:

1. `list_nodes` — what exists, and its exact ids/names.
2. `get_node_properties` on the nodes the step concerns — dimensions, spacing, segment names,
   control points, transforms. Refer to nodes by **id** (`slicer.mrmlScene.GetNodeByID(...)`);
   names are not unique.
3. `screenshot` when the step is geometric and you want to confirm the state you are acting on,
   or the result afterwards.

---

## Where the extension source is

The planning extensions are **not** inside the skill directory. Read them here:

| Extension | Source |
|---|---|
| CranialImplantPlanning, LongBoneFractureReduction, OrbitalFractureReconstruction, PelvicFracturePlanning, ReverseShoulderArthroplasty, ZygomaticImplantPlanner | `../../External_extensions/<Name>/` |
| PedicleScrewPlanner | `../../External_extensions/PedicleScrewSimulator/PedicleScrewPlanner/` |
| BoneReconstructionPlanner, SlicerOrbitSurgerySim | `<extensionsInstallPath>/<Name>/lib/Slicer-5.10/qt-scripted-modules/` |

Those last two also have checkouts under `../../External_extensions/` (`SlicerBoneReconstructionPlanner/`,
`SlicerOrbitSurgerySim/`), but **read the installed copy**: that is what Slicer actually loaded,
and the checkouts are not guaranteed to match it. They currently agree for
`BoneReconstructionPlanner.py` and `PlateRegistration.py` but **differ for `MirrorOrbitRecon.py`**,
so the checkout would teach you an API the running application does not have.

### Recipe: drive an extension from Python

When the step says to fill in a section, click a button or tick a checkbox, derive the
equivalent call from that extension's own source — do not recall it:

1. **Find the module.** Grep the source tree for `class .*Widget` and `class .*Logic`.
2. **Find the control.** The step quotes the visible label. Grep the `.ui` file(s) for that
   label to get the widget's `objectName`; grep the widget class for that objectName.
3. **Follow the connection.** `connect("clicked()", self.onX)` leads to the handler. Read it:
   drive the **logic method** when the handler is a thin wrapper, drive the **handler** when
   the real work (gathering widget values, ordering calls) lives in the handler.
4. **Check the parameter-node style.** Grep for `parameterNodeWrapper`. If present, node
   references are typed **properties** (`paramNode.inputVolume = node`); if absent, they are
   `GetNodeReference` / `SetNodeReferenceID` / `SetParameter` / `GetParameter`.
5. **Confirm the signature** before calling it. A method name you recall but have not seen in
   this extension's source is an assumption, not evidence.

Live objects are reachable as:

```python
widget = slicer.modules.<modulename>.widgetRepresentation().self()
logic  = widget.logic
```

and `.ui`-file children as `widget.ui.<objectName>`.

---

## The Slicer knowledge base

For core Slicer API (not extension-specific), use the skill at:

    ../Resources/Skills/slicer-skill-full

`SKILL.md` there explains its search strategy. Search roots:

- `../Resources/Skills/slicer-skill-full/slicer-source/` — Slicer source + script repository
- `../Resources/Skills/slicer-skill-full/slicer-extensions/` — extension catalogue (metadata for
  ~490 extensions; **not** the source of the ones above)
- `../Resources/Skills/slicer-skill-full/slicer-dependencies/` — VTK, ITK, CTK
- `../Resources/Skills/slicer-skill-full/slicer-projectweek/` — NA-MIC Project Week materials

`slicer-discourse/` is referenced by the skill but **is not present in this checkout**. Do not
search it. All skill data lives in that one shared directory — do not clone repositories into
this workspace. If the repos are not set up, run `setup.sh` from inside the skill directory:

```sh
cd ../Resources/Skills/slicer-skill-full && ./setup.sh
```

---

## Scope

- Perform **exactly the step the user describes** — not the earlier steps (already done, their
  results are in the scene) and not the later ones.
- Do not restart or re-run the procedure, and do not batch several steps into one call.
- Do not ask clarifying questions when you can answer them by inspecting the scene or the
  source. Produce the code.
- If you genuinely cannot determine an API after reading the source, make your best
  evidence-backed attempt and say what you were unsure of — an attempt is a result.

### Out of bounds

Do **not** read, and do not let a search wander into, the agent's own implementation:

- `../Resources/extension_CLI/` — generated per-step templates, workflow graphs, tool schemas
- `../SlicerAIAgentLib/`, `../Resources/Prompts/` — the agent's runtime and prompts
- `../logs/` — prior runs, which contain the code every earlier step executed

Those are the system this session is being compared against; the generated template for the
very step you are performing lives in the first one. Reading it would answer the question
instead of doing the work.

`.claude/settings.json` backs this with `deny` rules rather than leaving it to good manners.
Those rules cover the `Read` tool **and** the file commands Claude Code recognises in Bash
(`cat`, `head`, `tail`, `sed`) — which matters, because read-only Bash commands otherwise run
without a prompt in every mode and are *not* bounded by the working directory. They do not
cover a subprocess that opens files itself (a Python or Node script), so the instruction above
is still doing real work: do not write one to get around this.
