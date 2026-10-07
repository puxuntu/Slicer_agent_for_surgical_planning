# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

> **Scope rule for this file:** architecture, and invariants that are easy to get wrong. Not a
> changelog. Nearly every rule below exists because its failure mode is a *plausible wrong result or
> a silently skipped step*, never an exception — the reasoning behind each one is in git history and
> in the `scripts/check_*.py` that enforces it.

## Project Overview

SlicerAIAgent is a 3D Slicer scripted extension embedding an AI agent. A natural-language request is
routed to a **generated CLI workflow** — a procedure compiled offline from a third-party extension's
source plus its written cookbook — which then drives the scene step by step. Runtime pipeline:
route → dispatch a validated template per step → AST security validation → execute in Slicer's
`__main__` → self-correct on failure.

## Build & Test

```bash
cmake -S . -B build -DSlicer_DIR=/path/to/Slicer-build
cmake --build build

python scripts/build_rag.py                     # FAISS index (needs Resources/Skills/slicer-skill-full/)
python scripts/collect_runs.py                  # cross-condition table -> logs/runs_index.csv
python scripts/collect_runs.py --step cb_step_9 # one step under every condition
```

Dependencies are in `requirements.txt` (`httpx`, `numpy`, `jsonschema` explicit; `faiss-cpu`,
`onnxruntime`, `transformers` auto-installed at runtime). CMake installs them into Slicer's Python.

Unit tests import `slicer`/`vtk`/`qt`/`ctk`, so they run **inside Slicer's Python console**:

```python
import unittest
suite = unittest.TestLoader().loadTestsFromName("SlicerAIAgentTest")
unittest.TextTestRunner(verbosity=2).run(suite)
```

Tests live in `Testing/SlicerAIAgentTest.py` and inline at the bottom of `SlicerAIAgent.py`
(`SlicerAIAgentLogicTest`). Clear the MRML scene between tests that touch scene state.

### Checkers that run outside Slicer

Each `scripts/check_*.py` stubs or avoids `slicer`/`qt`/`vtk`, so it is runnable on every change.

| script | guards |
|---|---|
| `check_planning_recorder.py` | user-study instrument: partition totality, duplicate deliveries, vendored copies identical. **Run before every study session.** |
| `check_voice_commands.py` | voice matcher over fixed cases + every option of every shipped package |
| `check_runtime_reset.py` | run 2 starts where run 1 started (the `__main__` residue ledger) |
| `check_template_revision.py` | Revise: template ownership, install gate, restore; every template validates against itself |
| `check_template_write_back.py` | placeholders inside string literals; the write-back's placeholder guard |
| `check_prelude_boundary.py` | write-back cuts the injected prelude at its own end marker |
| `check_handler_drive.py` | the CLI emitter agrees with its own validator (handler arity) |
| `check_placement_starter.py` | a placement the extension armed is not re-armed by the runtime |
| `check_range_choice_fill.py` | a range the user chose reaches the step that spends it |
| `check_multi_select_choice.py` | a multi-answer control is not rendered as a one-of-N dropdown; selector defaults |
| `check_place_mode_polarity.py` | the place-point button is a toggle; view steps release the mouse on open |
| `check_toggle_state_binding.py` | a checkbox read as `checkState == qt.Qt.Checked` is still a bound control |
| `check_orbital_analysis.py` | orbital surface distance, improvement pairing, in-place `scene.mrml` splicer |
| `check_rsa_analysis.py` | shoulder angles, NRRD reader, density integral vs the logged score, both cone denominators |
| `check_cranial_analysis.py` | DSC/HD95/bDSC; the cropped metric window reproduces the full volume bit for bit |
| `check_pelvic_analysis.py` | reduction error read from the recorded transform; a **stale** record must be refused |
| `check_longbone_analysis.py` | the rigid residual over 64 runs; the wrong ground truth must fail abutment |
| `check_pedicle_analysis.py` | screw-in-pedicle grading: frame bridge, half-voxel debias, graded span |
| `check_mandible_analysis.py` | fibula vs *predicted* healthy mandible; partially-welded cut models, contour scan |
| `check_user_study_eval.py` | user-study evaluation: folder discovery, performed order, `cases=` hand-off, Run set + Interaction sheets |

## Architecture

### Entry point and structure

- `SlicerAIAgent.py` (~3600 lines) — `SlicerAIAgent` (metadata), `SlicerAIAgentWidget` (Qt UI,
  streaming queue, execution dispatch, self-correction, CLI generator UI), `SlicerAIAgentLogic`
  (LLM client, tool dispatch, scene context, snapshot/verification, background streaming).
- `SlicerAIAgentLib/` — the library; `app/widget_*.py` are Qt mixins composed into the widget.
- `Resources/Skills/slicer-skill-full/` — submodule, the Slicer knowledge base (clone `--recursive`).
- `Resources/Code_RAG/` — FAISS index + ONNX embedding model, built by `scripts/build_rag.py`.
- `Resources/extension_CLI/<Ext>/` — `manifest.json`, `code_generators.json`, `workflow.json`,
  `step_instructions.json`, `prompt_fragment.md`, `templates/*.tpl` (`{placeholder}` syntax).
- `Resources/Prompts/*.md` — every prompt.

| Module | Role |
|---|---|
| `LLMClient.py` | OpenAI-compatible **and** native Anthropic APIs. Streaming, tool calling, token tracking, query decomposition, system-prompt assembly. |
| `WorkflowRouter.py` | First-turn router: one tool-free call over a compact workflow catalog. |
| `WorkflowOrchestrator.py` / `WorkflowRuntime` | Step state machine: dispatch, interaction completion, repeat blocks, checkpoints, cancellation. |
| `ExtensionCLIAnalyzer.py` | 11-stage LLM pipeline generating schemas, templates and the workflow graph from an extension's source. |
| `ExtensionCLILoader.py` | Discovery and dynamic load of generated packages; `dispatch_workflow_step()`. |
| `SafeExecutor.py` | Execution in `__main__`: output capture, VTK error interception, timeout, scene rollback, introduced-globals ledger. |
| `CodeValidator.py` | AST security validation: blocked/allowed modules, blocked functions, destructive-op detection. |
| `InteractionManager.py` | Markup node creation, placement mode, VTK observers with debounce timers. |
| `TemplateReviser.py` | Revise core (Qt-free): template ownership, install gate, reply parsing, snapshot-before-write. |
| `BaselineRunner.py` / `BaselineMCPServer.py` | Baseline harness core and its MCP transports. |
| `PlanningRecorder.py` | User-study instrument. **Vendored byte-identical in five places**; the one implementation of `save_scene_flat`. |
| `RunLog.py` | Run-folder naming, fail-soft artifact writers, `RunManifest`, `build_run_statistics()`. |
| `PromptLibrary.py` | The only reader of `Resources/Prompts/`. |
| `SkillTools.py` / `SkillIndexer.py` | ripgrep + tree-sitter tool executor; chunking, ONNX embedding, FAISS. |
| `voice/` | Qt-free voice half (`audio`, `asr_client`, `tts_client`, `grammar`, `commands`); Qt half is `app/widget_voice.py`. |
| `experiments/` | Per-procedure analysis (Qt-free numerics + `_panel.py` Qt half). |

### Threading

HTTP I/O runs on a background thread; events reach the Qt main thread through `_streamQueue`, polled
every 50 ms by a `QTimer`. **All MRML and UI access is on the Qt main thread.**

Draining that queue pumps the Qt event loop, and so does executing template code — so any handler
reachable from the drain needs a re-entrancy guard or a `QTimer.singleShot(0, ...)` deferral.

### Guided-only runtime

`WorkflowRouter.GUIDED_ONLY_MODE = True` makes the router's decision final: on a match the workflow
starts; on anything else `_refuseUnsupportedRequest` shows a **modal** (not a chat line — the request
is over) and the traditional search-and-generate turn is never reached. `= False` restores it.

The claim under test is that a validated, offline-analysed procedure drives the scene; a silent
fallback to improvised code is an unmeasured escape hatch and an unreviewed code path.

Seven causes reach the refusal and only two are about the request — the rest mean the install is
unconfigured (`no_api_key`, `no_workflows`, `no_client`, `router_disabled`) or a package is broken
(`start_failed`, `no_first_step`), so `_lastRouterRejection` records the cause and `_refusalMessage`
gives each its own remedy. Consequences: queueing is gone (a deferred request would promise a reply
that can never come); refusals are logged to `logs/refused_pipeline_<stamp>/`; a refusal raised
*during* a run gets no folder (it would repoint `_currentLogDir`) and becomes an event of that run.

### A run must start where the first run started

`_prepareCleanRuntime` returns the process to a freshly-launched state and runs **on the way in**
(from `_applyRouterDecision` before `start_for_extension`, and from `_resetGuidedSession` so the two
cannot drift). Entry is the only point every run passes through. Nothing raises when this is wrong —
the workflow just behaves differently on run 2 — so the state is **enumerated explicitly**:

- **`__main__` residue.** Templates reach their extension through `try: logic = _<ext>_logic` /
  `except NameError: ...` and pass node IDs as `_<ext>_<step>_id`. That namespace's lifetime is the
  **process**, so run 2 reused run 1's logic object with its stale node attributes, and a guard like
  `if self.fullBoneNode is not None:` read "already done" while the scene said otherwise. The
  extension's own scene-close reset cannot reach it — that resets `widget.logic`, and the templates
  hold a second, independent instance. `SafeExecutor` keeps a **class-level** ledger (one `__main__`
  per process) of names its `exec` calls introduced, diffed on the main thread, and
  `clearIntroducedGlobals()` unbinds exactly those.
- **"this module is entered" lives in two places** — `_invisiblyEnteredModules` and
  `WorkflowRuntime._entered_modules` (the second gates the wizard-page probe).
- **`_lastSliceFitLayout`** skips the slice fit when run 2 opens on run 1's layout; its `"__unset__"`
  sentinel is what makes a fresh launch always fit.
- **`_lastCorrectionError`** is quoted into the next repair prompt.

It runs **after** `orchestrator.cancel_workflow`, never before — that call reads the state this
empties (the interaction manager's created-node list, which it uses to *delete* those nodes).

`RESET_EXTENSION_MODULE_ON_START` rebuilds the driven extension's widget via
`slicer.util.reloadScriptedModule` — the only generic way to clear what the runtime cannot enumerate,
including the state of its Qt controls (which matters because the runtime drives those controls
precisely because the handlers read them at click time). Gated on `hasattr(slicer.modules, …)`,
never fatal.

### The extension's lifecycle is the runtime's responsibility

A generated step carries a `# precondition:begin … selectModule('<Ext>') … precondition:end` block
whose only purpose is to fire the extension's `enter()`. `_prepareGeneratedStepCode` **strips** it and
calls `_ensureModuleEnteredInvisibly()` instead: entering for real makes the extension the active
module, and SafeExecutor's restore then fires its `exit()`, which hides plane handles and locks planes
— breaking every later interactive step.

`enter()` is not one-off initialisation; it is the extension **binding itself to the current scene**.
Slicer's own recovery from a scene close is `onSceneEndClose: if self.parent.isEntered: …`, and
`isEntered` is False by construction here — so the cache is **per scene, not per session**.
`_invalidateInvisibleModuleEntries()` clears it on `onSceneEndClose`, and `_moduleWidgetNeedsReentry()`
re-enters when a cached module looks unbound, keyed on the shape Slicer's module template mandates
(`_parameterNode` absent or stale), never on an extension's identity, failing open.

### Exiting a guided workflow

One Exit button at the right end of the replay row `[back][progress][fwd][run-from-here][balance][exit]`
— anchored to the row's right edge, icon-only (a text label can force the module panel wider), and
**not** driven by `_updateReplayControls`: available whenever the panel is up. The Cancel it replaced
was a workflow *action* through the runtime, so it was hidden exactly where a user most needs a way
out (a completed run, a step with no controls, the panel a dispatch error leaves behind).

`_resetGuidedSession()` is a **local** reset — it never asks the runtime for permission, and the
runtime's own `cancelled` result and `onSceneEndClose` funnel through it. Three ordering rules:

- `_clearCompletedWorkflowState(clear_replay=True)` runs **while `runtime.session` is still
  non-None** — `clear_checkpoints()` is a no-op once it is None, and it restores the live scene from
  the hidden `vtkMRMLSceneViewNode` snapshots and deletes them.
- `reset_workflow_state(None)` clears the mirrors for **all** extensions; a per-extension reset would
  leave the next procedure inheriting this one's completions, choices and loop counters.
- **`_guidedSessionEpoch`** fences work in flight. A self-correction round trip is a thread and
  auto-advance is a `singleShot`; neither can be cancelled, so each captures the epoch and
  `_guidedSessionAlive()` drops it on mismatch — otherwise a repair lands after Exit and executes into
  a scene the user has left.

Exit **closes the scene** (`EXIT_CLOSES_SCENE`) on both answers, and the dialog asks for that deletion
in those words. Leaving it up is unsafe: the next procedure loads its own data, so a scene holding the
last run's nodes offers them to any step that looks a node up by name — and closing the scene is the
only thing that reliably re-binds the driven extension. Three fences: it runs **last** and **after
`runtime.session = None`** (so its `EndCloseEvent` does not re-enter the teardown); it is withdrawn
when a requested save did not land (`_saveRunStatistics` returns a **positive** check — the `.mrml`
exists *and* a node was written — because nothing in that path raises); and `close_scene` is a separate
parameter from `reason`, since `_askExitChoice` falls back to a full exit when the dialog could not be
*shown*, and an assumed answer may close a panel but not discard a scene. Voice never closes it —
push-to-talk is Space, a modal stands the key filter down, and Space activates a message box's default
button, so saying "no, cancel" would confirm the exit.

Exit refuses while a baseline run, a stream, or a revision is in flight.

**Saving is a separate decision**: *Exit and save* / *Exit without saving* / *Cancel*, because a Yes/No
dialog welds two independent decisions together and saving writes hundreds of megabytes. The answer is
read back as a **button role**, never identity or position — Qt reorders by platform and PythonQt can
return a fresh wrapper, so `clickedButton() is save` may be False for the button just clicked.
"Without saving" **deletes** the run folder (artifacts are written incrementally; there is no "don't
write it"), gated on a containment check on the **resolved** path, with `_releaseRunLogDir()` first
because the writers `makedirs(exist_ok=True)`.

The save blocks the main thread behind a modal progress dialog calling `processEvents()`, which is why
`_resetGuidedSession` opens with a `_guidedExitInProgress` guard.

### Agent pipeline (non-guided path)

Reached only with `GUIDED_ONLY_MODE = False`; self-correction uses the same assembly and is always live.

1. `onSendButtonClicked()` → background `_backgroundStream()`.
2. `decomposeQuery()` splits the prompt; `VectorRetriever` searches FAISS.
3. Tool loop — `Grep`, `ReadFile`, `VectorSearch`, `GetNodeProperties` plus the dynamic CLI tools,
   dispatched in parallel. `SearchSymbol` and `GenerateSegmentationCode` are *implemented but
   registered in no schema* — wire them in or treat them as dead code; **do not describe them as
   available**.
4. `agent_plan` JSON (with `expected_scene_change`) then a fenced Python block.
5. `CodeValidator` AST checks.
6. `SafeExecutor.execute()` in `__main__` on the main thread; scene rollback on failure.
7. `verifySceneAgainstPlan()` compares before/after snapshots. Checks: `node_exists`,
   `node_count_delta`, `node_modified`, `node_has_display`, `node_has_content`, `node_name_matches`,
   `layout_changed`, `selection_changed`, `module_entered`, `property_true`, `not_checked`.
8. Self-correction — isolated retry loop (up to 5) via `chatWithToolsIsolated()`, which does not write
   `conversation_history`.

### Prompts

**Every prompt is a file in `Resources/Prompts/*.md`, never a Python string** — a prompt is an
experimental variable, so it must be editable, diffable and citable without touching code.
`PromptLibrary.py` is the only reader; the only prompt text left in Python is a one-line fallback per
loader.

| purpose | file |
|---|---|
| opening turn | `workflow_router_prompt.md` — ~6 KB, tool-free, temperature 0, thinking off, no retrieval |
| general request | `system_prompt.md`, assembled by `_buildSystemPrompt()` |
| self-correction | same assembly, deliberately long — repair needs the whole trajectory |
| a step that ran and misbehaved | `template_revision_prompt.md`, scoped to one step |
| baselines | `baseline_pure_llm_prompt.md`, `baseline_online_only_prompt.md` |
| voice tier 2 | `voice_command_prompt.md` |

The router replaced a **140,611-character** system prompt that existed to emit one tool call. Its
catalog is built from the workflow graphs: name, step count, and seven step descriptions **spread
evenly across** the procedure — the head names the inputs, the tail names the goal, which is what
separates nine procedures that all open with the same Segment Editor boilerplate. Unknown name,
confidence < 0.6, `null`, a malformed reply or an API failure all return False. The prompt says a
refusal is the intended outcome for an uncovered request — telling the model a `null` falls through to
a coding agent that no longer exists biases it toward over-matching.

Two independent ablation flags:

| flag | CLI fragments | `ext:` source | cookbook | used by |
|---|---|---|---|---|
| *(none)* | yes | yes | yes | normal turns |
| `suppress_cli_tool_fragments` | no | yes | no | self-correction during a workflow |
| `suppress_extension_cli` | no | no | no | online-only baseline |

A repair inside a workflow already strips the CLI tool *schemas*, so it strips their *descriptions*
too — ~42 KB per turn describing tools that are not there, and inviting a call that arrives as text and
parses to no code. The `ext:` paths stay: searching the extension's source is what a repair needs.

## Generated CLI pipeline

`ExtensionCLIAnalyzer.py` analyses an extension's source and generates tool schemas, templates and a
workflow graph under `Resources/extension_CLI/`. A package that fails validation is auto-revised by
`_autoReviseCli`; one that validates but *behaves* wrongly is fixed at runtime by Revise.

**Do not hand-patch `Resources/extension_CLI/*`.** Fix the generator; the user regenerates. Fixes must
be generic mechanisms, verified against a second cookbook extension — never extension-specific rules.

> **The two mirrors.** `WorkflowRuntime` and `extension_cli_loader.choice_helpers` deliberately keep
> parallel copies of the node-class readers, `_NONSPECIFIC_NODE_CLASSES`, the family predicates and
> `_MULTI_SELECT_WIDGET_CLASSES`. The loader's half is baked into the code a step *executes*, the
> runtime's half into what the panel *shows*. **Teach both, always.**

**Placeholder closure is enforced in TWO independent places** — `validation_contracts` per template,
and `contract_audit._final_package_audit` over the shipped artifacts as the authoritative final gate
(so a template rewritten later cannot ship on a stale verdict). Carving a rule out of only the first
gives a package whose every step validates and which the second then stamps `validation_failed` — and
`status` is what the loader cache and `build_extension_catalog()` gate on, so the procedure **silently
disappears from the router's catalog**. Hence `_bound_choice_placeholders(gen)` lives once, in
`validation_semantics`, and both gates call it. `_fill_remaining_placeholders` fills from a real option
rather than `""`, or validation would check `segmentOrbits("")`, which the extension rejects by design.

### Where a `user_choice`'s answer goes

Two binding channels, and an extension may use either:

1. **The parameter node** — `SetParameter("role", …)`, surfaced as `choice_bindings[step]`.
2. **The control itself** — the handler reads it at click time
   (`self.logic.segmentOrbits(self._currentSide())`). No parameter role, so for those extensions the
   channel was empty: the answer was recorded and reached nothing, and the run used the factory
   default. `scan._scan_value_controls` recovers the control's **items**, the **reader** mapping state
   to value (a ternary/if-else return over a literal comparison), and the **consumers**
   `(method, arg_index)`; `_widget_state_choice_binding` names the parameter against the AST signature.

Three silent failures:

- **The options are the control's own, not the cookbook's paraphrase.** The orbital panel asks for the
  fractured *side* but offers "Red box" / "Blue box" — deliberately, because the boxes are drawn over
  the orbits and picking a colour is unambiguous where "left" is not.
- **The index→value map inverts without a symptom.** Item 0 is the RED box = the patient's **right**
  orbit, so an authored `[Left=left, Right=right]` list picks the healthy side. The run completes and
  reports success, on the wrong orbit. Only the extension's own reader knows the mapping.
- **A `.ui` file is evidence only if the widget loads it** (`_scan_ui_is_live`; vacuously true when
  there is no `.ui`, so wizard modules skip the demotion path). A module that moved to building its
  panel in code keeps the file, which then describes a GUI that does not exist while still parsing and
  still carrying matching widget names.

At runtime the answer travels **twice, deliberately**: `_build_format_kwargs` merges it into the fill
kwargs (so `{side}` resolves — that is what makes the step correct), and
`_build_widget_state_choice_materialization_code` drives the extension's own control to the matching
option (so the panel shows it, the connected handler fires, and a later step reading the control
agrees). They cannot disagree — same recorded value, same scanned option list. A missing **item**
raises; a missing **widget** only warns.

### A range choice reaches its consumer by name

A `range` choice records `[lo, hi]` under the `parameter_name` the decomposition invented; the step
that spends it asks for a placeholder. The names never come from the same place — the Segment Editor
driver builds its Threshold-apply block from the **effect** alone, so it can only write the generic
`{threshold_min: 150.0}`. `_build_format_kwargs` is the bridge.

The marker word can sit **anywhere** in the name (`thresholdRange`, `threshold_range_reference`), so
`_range_alias_words` drops it wherever it appears and offers every remaining word as a concept.
Stripping only a *trailing* marker emitted no alias for a marker in the middle, and both Apply steps
thresholded at the placeholder's hard-coded 150-3000, overwriting the segment the range step had just
committed — the user sets the slider, sees the mask they asked for, and meets a different one two steps
later. Aliases **overwrite**, so the most recent range wins, which keeps consecutive threshold cycles
correct and makes a replay truncation put the earlier one back.

### One question, several answers

A `ctkCheckableComboBox` is indistinguishable from a plain combo in how it is filled or read
(`addItems` in, `checkedIndexes()` out, and it *is* a QComboBox subclass), so the whole mechanism rests
on its **Qt class** — `_MULTI_SELECT_WIDGET_CLASSES`, in both mirrors. Three places had to learn it,
each failing silently alone: the **scan** (control absent from the page inventory, so the step shipped
as a free-text box); the **label pairing** (a page building `fields = [(lText, self.lSelector), …]` and
laying it out in a loop has no literal cell — the **pair literal itself** is the pairing, read last so
a real layout call wins, and only for a 2-element literal with exactly one known label and one known
combo); and the **runtime**, which would render a dropdown that works, commits, and instruments one
level out of however many were ticked.

`_reconcile_multi_choice` fires on a **lone** match when the control is multi-select, but only when it
is the step's *only* quote — one match against several means the scan missed the others, and rebuilding
on that ships a form asking one of the step's questions and never the rest.

The emitted drive sets every row Checked or Unchecked **explicitly** (so a replay re-drive replaces
rather than accumulates), identifies the control by **class as well as item set** (a plain sibling
listing the same options must never be the one ticked), and **re-reads `checkedIndexes()`** — a control
showing tick boxes while reporting nothing ticked is exactly the miss to catch. `findChildren` matches
`className()` **exactly**, so the checkable class must be named in the search list.

**Voice accumulates and does not auto-confirm**: one utterance names one option, so the form must not
commit the moment every selector holds something. Such a step is committed by saying "done".

### A selector starts where its source control starts

A GUI control answers its own question before anyone touches it, and that answer is binding:
`doStepProcessing` writes `sSelector.currentText` on exit whether or not the dropdown was opened. So
`_combo_default_option` carries the scanned startup option into `default_value` and the panel
pre-selects it, adding **no** placeholder row.

This is not "pre-select item 0": a page may open on a **prompt** whose handler rebuilds geometry, so a
pre-selected value would silently move something an earlier iteration fixed. One rule separates them —
the prompt row is already dropped from `options`, so a default **not among its own options** is
withheld; likewise a checkable combo and one with `live_items`.

The default comes from `setCurrentText` / `setCurrentIndex` (including PythonQt's
`combo.currentIndex = 2` spelling) with a **literal** argument, first write wins; absent that, item 0.
The panel's two readers of "answered" must agree: the **voice** gate reads the current **text**, never
`currentIndex <= 0`, which called a defaulted selector unanswered forever.

### A checkbox the extension reads as a comparison

```python
if self.ui.showOriginalMandibleCheckBox.checked:                   # attribute test
if self.ui.generateFibulaPlanesButton.checkState == qt.Qt.Checked: # COMPARISON
```

The second is what a control whose state is not a bool requires. A `Compare` node is not an `Attribute`
chain, so the scan returned nothing — no `ui_parameter_binding`, so the deterministic emitter never
fired, so the step fell through to free-form generation, which guessed `'true'` against an extension
comparing `== "True"`. The parameter was set, the read was False forever, and the symptom surfaced two
steps later looking like a different feature.

- **Polarity is read, or nothing is recorded.** `_widget_state_test` handles the attribute test, `not`
  of one, and the comparison in either operand order with `==`/`!=`/`is`/`is not`, deciding ON from the
  compared value. Anything undecidable (`PartiallyChecked`, a variable, a `BoolOp`) records **no**
  binding — a guessed polarity clears the box the cookbook asked to tick. Admitted only for two-state
  properties (`checked`, `checkState`, `visible`, `enabled`), so it never invents boolean semantics for
  `currentIndex == 0`.
- **The ON/OFF strings come from the source** (`true_value`/`false_value`), merged onto **one** role
  entry per (role, access, property) — the if/else branches are two `SetParameter` calls and downstream
  reads `roles[0]`, so appending the else branch as a second dict dropped every `false_value`.
- **The control is driven on the property the source uses.** A second scan reads the extension writing
  its own control from the parameter, which pairs widget with role independently *and* states the exact
  write form. Not cosmetic: `ctkCheckablePushButton`'s indicator is separate from the button's checked
  state, so `checked = True` raises nothing and ticks nothing — and an unticked control is a **ratchet**,
  since every sibling wired on `stateChanged` re-runs `updateParameterNodeFromGUI` and writes the
  parameter back to `"False"`.

Enforced again at validation (`_validate_parameter_state_spelling`), because free-form generation,
self-correction and Revise also write templates. Wired into the **per-template** gate only, where the
error is named and repairable — a rule living only in the late gate stamps `validation_failed` on a
package whose every step validated.

### A toggled button is clicked twice

"Place a control point" ARMS placement and, clicked again, ENDS it; both emitted
`setPlaceModeEnabled(True)`. Invisible where it is made (re-enabling an enabled place widget raises
nothing), it surfaces on a **later** step and reads as a different bug: the loop's next iteration opens
on "rotate the red slice" and every attempt drops another control point.

Polarity comes from the step's recorded `target_value`, falling back to `_infer_final_state_intent` over
the step text (which knows "inactivate", the cookbook's own word — not a prefixed spelling of
"activate", since every true pattern is space-anchored). **Both** routes to the widget carry it. The
disabling form also switches the interaction node to view-transform mode.

`_reconcile_wizard_placement` defers to the extension's own widget only when the button before it
**armed** that widget. And the view-adjustment **pre**-template releases the mouse, which the post
already did — applying it only on Done is the same fix one step too late to help the person doing the
adjusting. A `module_tool_interaction` step must **not** release it: there the extension's tool is
holding the clicks on purpose.

### A node class is a lookup key, not prose

`node_class` goes straight to `getNodesByClass` and `nodeTypes`, but it arrives from an LLM
decomposition, which sometimes writes `"vtkMRMLVolumeNode (CT scalar volume)"`. As a key that matches
nothing, and the symptom points away from the cause: the pick step's tree is empty and `WorkflowInputs`
reports the scene as missing a CT already loaded.

- **A gate keyed on an exact class name must first ask whether that name is reachable.** The sole-node
  auto-select requires `GetClassName() == node_class` so it never chooses between siblings — but against
  an **abstract** class that is unsatisfiable, and it contradicted the manual path, which accepts the
  node via `IsA`. It now runs only when `_nodeClassIsInstantiable()`, answered from the scene's registry
  (`IsNodeClassRegistered`) and cached. Read-only deliberately: `CreateNodeByClass` answers the same
  question but dereferences its null result when a default node is registered, so it can **segfault**.
- **Allow-lists derived from LLM prose must be normalized at construction**, or they authorize whatever
  contaminated them. `allowed_node_classes` was built from each logic parameter's `type` field and
  admitted anything `startswith("vtkMRML")`, after which the `references unknown node_class` check
  validated the gloss against itself.
- **Both runtime readers must normalize.** Fixing only `WorkflowRuntime` fixes what the panel *shows*
  and leaves what it *executes* broken — the loader's copy is baked into emitted code as `IsA(<class>)`.
  `stage4._normalized_node_class` (in the normalizer, so the repair costs no re-ask) and
  `WorkflowRuntime.normalize_node_class` both reduce a decorated value to its class token; the runtime
  half keeps shipped packages working and warns so they still get regenerated.

### A fix applied once and thrown away every run

Self-correction repairs a step at runtime and `_persistGeneratedTemplateRepair` writes it back into the
`.tpl`. When that refuses, nothing tells anyone: the step self-corrects, advances, discards the fix, and
does it again forever. Two causes, both firing:

- **A placeholder inside a string literal is never filled.** The filler masks string literals before
  substituting (deliberately — a template's prose must survive filling), so
  `"{curve_name_keyword: mandible}"` searches for the brace text itself. The blanket
  unresolved-placeholder rule cannot catch it because it carries a **default** — exactly what makes a
  placeholder safe at dispatch, everywhere except inside a string.
  `TemplateReviser.inert_placeholders()` measures it with the loader's own filler and
  `_validate_placeholder_reachability` refuses it. The discriminator is the string token's **prefix**,
  asked of Python and never a regex: `f"role '{role}'"` is how every generated template reports an
  error, so flagging f-string interpolation would refuse the common case to catch the rare one. Over
  181 shipped templates it reports exactly two.
- **The guard measured the wrong thing.** Refusing a template with placeholders is right (the corrected
  code is *filled*, so persisting it freezes this run's `{side}` into the package) but it used a raw
  brace scan, which matches every f-string interpolation. The precondition block every step carries ends
  in one, so the guard fired on **82 of 181** templates, of which only **13** contain anything the
  filler looks up. It now asks `fillable_placeholder_names()`.

## Runtime features

### Interactive workflows and the replay stepper

`InteractionManager` creates markup nodes and manages observers; analyzer stages 4.5-4.9 detect
interactive patterns, classify them into phases, build the graph and generate split templates (pre-
interaction setup + post-interaction processing). Manifest `workflow_type` is `"simple"` or
`"interactive"`; interactive packages ship `workflow.json`.

**Back / Forward / Run from here.** `WorkflowRuntime` records a `WorkflowCheckpoint` per completed step
(and per loop decision) holding the replay action/args, a `repeat_states` snapshot, the completed/choices
prefix, guidance text, `before_node_ids`/`created_node_ids`, `layout_before`, and a full before-step
`vtkMRMLSceneViewNode`.

**Back/Forward recover the full scene without ever deleting a node**: `_restore_to_view()` copies every
stored node's properties onto its live match by ID, hides nodes that did not exist yet, and restores the
layout. Slicer's own `RestoreScene` is unusable — `removeNodes=False` aborts when later nodes are
present, `removeNodes=True` deletes and recreates (dropping display nodes). The live state is snapshotted
on first Back so Forward returns to it exactly.

**Run from here** commits via `rewind_to_checkpoint(preview_index)`, truncates the session and the
module-global mirrors to that prefix, then re-dispatches with `action="start"`.

### Voice control

**One microphone button arms the feature; the SPACE BAR gates capture.** Hold, speak, release — nothing
is transmitted unless somebody is holding the key, which removes the energy detector's whole failure
class and is a stronger privacy property than any matching discipline. The always-on mode remains behind
`voicePushToTalk`.

The key is a setting (`voicePttKey`, F4/F8 offered) because bare Space is `qMRMLSegmentEditorWidget`'s
"swap the last two effects", live whenever Segment Editor is entered. **Ctrl+Shift+Space (markups Place
mode) is never intercepted** — the filter compares modifier bits, not just the key.

The key is taken over **only while armed** and given back on every teardown path. Five gates per event,
each a defect if missing: focus is not a text entry (Slicer's Python console is a `QTextEdit`); no modal
is up; the main window is active; modifiers match exactly; a session is armed. Two Qt traps:
**auto-repeat is swallowed only while we own the hold** (returning True unconditionally ate every repeat
of a key we had *declined*), and **`QEvent.ShortcutOverride` must be accepted**, since Qt resolves
shortcuts before delivering key events. `_held` is the real state, not `isAutoRepeat()`.
`WindowDeactivate` ends a hold — the release is not guaranteed to arrive.

**The key hook has two implementations and picks one at arm time, by proof.** The correct one is an
application-wide event filter (a `QShortcut` has no release signal, and push-to-talk is *defined* by the
release). PythonQt cannot always dispatch a C++ virtual to a Python override, and a filter never called
presents as "the key does nothing" — so arming sends one synthetic event through it and falls back to
polling the OS key state at 30 ms.

Four things stop a mis-recognition driving the scene:

1. **The matcher declines by default** — an utterance resolves only against the closed vocabulary the
   step on screen offers, and anything below `ACCEPT_SCORE` (0.62) is `ACTION_NONE`. Fixed verbs match
   the **whole** utterance, never a substring ("we're done with the previous patient" would advance a
   step). Free text needs a "set"/"enter" lead-in.
2. **The mic is muted while the app speaks** — the words just spoken are precisely those most likely to
   match the step's labels. Pressing the key **cuts the announcement and unmutes**, or push-to-talk
   would sit behind twenty seconds of speech. In always-on mode the unmute is on the speak thread, not
   the queue handler, since Exit drains `_streamQueue` wholesale.
3. **Every committing action is announced, naming the label and not the value** ("Selecting Red box.").
   It is enqueued before the action is applied but synthesis is a network round trip, so it makes a
   mis-hearing audible when it happens; it is **not** a veto. Naming the label is what makes it work —
   a surgeon who said "left" hears "Selecting Blue box" and can act on the mismatch.
4. An optional **confirm mode**, which *is* a veto. The step it was resolved against is stored with it,
   since the workflow can move on while the user decides.

Vocabulary hardening is kept even under push-to-talk: "ready" and "go ahead" are absent from the advance
vocabulary, "right"/"ok"/"okay" from the confirm vocabulary — "right" is also the *value* of an option
on the orbital step, so accepting it as assent would let a surgeon correcting the side confirm the wrong
one.

**A positional pick is matched as a WHOLE utterance, never by finding an ordinal in a sentence.** The
ordinal branch is reached exactly when label matching failed — the state ordinary conversation is in —
so "just a second" selected option two, which on the orbital step is the other side of the head. Token
filtering does not rescue the loose form, so `_ordinal_index` is a lookup against an enumerated phrase
table and nothing else. Nothing is lost: every label is read aloud, so saying it is always safer.

`match_score` scores over a cross product of spellings (verbatim, carrier words removed, numerals spelled
out, number words digitised), and `_match_score_one` **takes the max of its heuristics** rather than
returning from the first that fires — token overlap is weakest and fires most often.

**`grammar.py` mirrors the panel's render branch and must change with it.** `_family_for_state` takes
`_renderWorkflowChoices`' branches in the panel's order, not alphabetically — a segments-table step also
carries a `node_class`, a range step also a `parameter_name`. And the choice value is **what the button
would send, not what the artifact declares**: the render loop coerces a Yes/No *label* to `True`/`False`
regardless of the declared value, so reading `choices[i]["value"]` would make speaking and clicking
disagree — and on a repeat block the string never equals the boolean `exit_value`, so the loop could not
exit.

**Every action goes through the widget method the mouse would have called** and never through
`WorkflowRuntime.run_step`: each shortcut loses something (interaction cleanup, the threshold commit
later steps depend on, the extension's own control being driven first so its handler fires).

**An idle hot microphone does not talk to the router** — with no workflow there is no closed vocabulary,
so every sentence would become a routing call and a modal refusal. A spoken request must open like one
and be at least three words.

**Nothing the microphone hears is written to disk by default** (`VOICE_LOG_TRANSCRIPTS = False`) — run
folders are copied, shared and attached to papers, and most of what a theatre microphone transcribes is
conversation about a patient. Artifacts record durations, byte counts, language and the resolved
**action**; audio bytes are never persisted.

**A failure streak stops the session** — a wrong region or bad key fails every utterance identically and
the status line lives in a collapsed group, so three consecutive failures raise a dialog naming the three
settings.

**Two tiers, and the second is only for the uncertain, not the empty.** A sentence matching *nothing* is
more likely conversation than a paraphrase; an *ambiguous* result is a question for the surgeon, not a
coin flip. The fallback is offered the step's options as the only candidates and must return an
**index**, so the model can rename an option but never introduce one. `resolve_llm` exists beside
`resolve` because tier 2 is an HTTP round trip that would freeze Slicer on the panel's thread, and its
answer is re-checked against the live `current_step`.

**Three fences, not interchangeable.** `_guidedSessionEpoch` (captured per *utterance*) retires work
against an exited workflow; `_voiceSessionSeq` is a **microphone** session token (`stop()` emits a final
state handled up to 50 ms later, by which time the button may be back on); `_voiceHandlingTranscript` is
a **re-entrancy** guard, since both draining the queue and applying a command pump the event loop.

**Speech is announced once per step OCCURRENCE, not per repaint** — `_voiceAnnounceKey` is
`(workflow_id, step_id, len(completed_instances), family, status)`. Automated steps are never spoken, and
a node-pick step about to auto-answer itself is deliberately silent.

**API.** `qwen3-asr-flash` / `qwen3-tts-flash` over DashScope's *native* multimodal endpoint via `urllib`
— not `httpx`, which is in `requirements.txt` but imported by no project code and unproven inside
Slicer. The OpenAI-compatible mode **does not exist for ASR in the US region** and model ids are
region-suffixed, so a wrong region is a 404 that reads like a bad key. Speech-out derives its endpoint
from the speech-in region; the speech key is its own QSettings entry; `voiceRegion` is applied **before**
the other voice settings because its handler rewrites the model list and endpoint. `sounddevice` is the
only binary wheel, installed on first listen and degrading to a named reason. TTS audio returns as a
**URL** with no documented container request, so bytes are sniffed and `audio_format` reported.

### Revise — rewriting a step's template at runtime

**A generated step can pass every check and still be wrong, and the only detector is a person.** It runs,
raises nothing, and reconstructs the wrong orbit or leaves a node the next step cannot find.
Self-correction fires on a raised error, static validation sees valid code, the api-probe sees the method
exists. So: step Back to it, press Revise, say what should have happened, press Send.

It replaced a "Repair Generated CLI" button that took free-form sentences, asked an LLM which of 27 steps
each meant, and repaired blind — untestable without re-running the whole procedure. Pointing at the step
removes the classification and lets the revision be given the dispatched code, what it printed, the live
scene, the answers already given, and the step's previous revisions. That button was also the only
trigger of the live-execution validation gate, which is therefore gone; packages are validated
**statically only**.

**The TEMPLATE is rewritten, not the filled code** — which is what makes this stronger than the
write-back beside it. What replaces that guard is **placeholder closure**: a revision may drop a
placeholder and re-default one it has, but may not introduce a name the original lacked (a new bare
`{name}` raises `KeyError` inside the loader, and the symptom is a step that silently never executes).

Four install checks:

- **Placeholder closure** over `fillable_placeholder_names()`, not a brace scan — a raw scan matches
  every f-string interpolation, and f-strings are how every generated template reports an error. The
  defaulted form `{name: default}` is not an escape hatch: it is the same six characters as a dict
  literal `{key: 1}`, which the filler also replaces.
- **The filler, run for real.** `unfillable_placeholders()` calls `templates._fill_template` itself
  rather than re-deriving its rules; a drifted copy would answer confidently about a different string.
  A survivor is split by asking **Python**: inside a real STRING token it is an interpolation; outside
  one it is trapped by an unbalanced apostrophe, typically in a prose comment.
- **Syntax and CodeValidator**, both on a `sample_fill()`ed copy.
- **Scope.** `parse_reply` resolves the model's paths against the step's own template list and drops
  anything else. A reply whose `templates` key is misspelled is a *correctable* error, never a
  fall-through to the single-block shape — that would install the JSON document as the template, and
  nothing downstream would object (a JSON object is a valid Python dict literal: it parses, imports
  nothing, has no placeholders). The step would raise nothing, print nothing and do nothing.

**The reply must be FENCED** — `_runToolLoop` ends a round only when `_extractCode` finds a fenced block,
so a prompt asking for bare JSON produces a loop that can never accept a correct answer. Rejections are
fed back verbatim with `MAX_ROUNDS` (3) attempts; the checks are deterministic, so the retry message is
evidence rather than an opinion. The call is `chatWithToolsIsolated` with CLI schemas **stripped by
identity**.

**The original is kept, and the promise is checked.** `versions/revision_<ts>/` is the package BEFORE the
write — deliberately not `repair_NNN`, which archives the *result*. `snapshot_package_version` returns
`None` on failure, so `apply_revision` refuses to write when the snapshot did not land. Records go to
`debug/revision_<ts>/` and `debug/revisions.json` (under `debug/`, which survives a regeneration), plus a
copy in the run folder.

Three traps:

- **The header strip must not be greedy.** Each rewrite prepends `# [revised] …` and the model
  reproduces one; stripping "the header and every comment after it" ate the `# precondition:begin …`
  block on the second revision — the only marker for firing `enter()`, whose absence breaks every later
  interactive step and raises nothing. Continuation lines are enumerated instead.
- **The header is validated too**, because it is written after validation: the surgeon's sentence goes
  into a comment above executable code, so an unbalanced apostrophe would swallow the placeholder below
  — the exact defect the validator refuses in the model's output, entering through the door beside it.
- **The loader cache is NOT invalidated.** Template content is opened fresh per dispatch, and
  `invalidate_cache()` mid-run re-reads every manifest and would drop any package failing the status
  gate — possibly the one the surgeon is standing in.

**The revised step is re-run automatically and the scene is put back first.** Three states reach it and
only one has a committed checkpoint: *scrubbed back* and *completed and left behind* go through
`_rerunFromCheckpoint`; **standing in it** has none (checkpoints are recorded on completion), which is
what `rollback_failed_step` is for — it restores from the *pending* checkpoint and keeps it so the retry
starts identical. Never re-dispatch on top of the existing scene: a PRE template creating a node would
create a second, after which the POST template's "last node of this class" picks the wrong one. The
re-run is deferred with `singleShot(0, …)` because it is reached from inside `_drainStreamQueue`.

**A template returned verbatim is not written.** The agent is asked for every template the step owns, so
it echoes back the ones it did not touch; writing those would stamp a header on them and report untouched
files as revised. Bodies are compared with headers stripped; *every* template unchanged is an **error**
naming them, not a silent success.

**Mutual exclusivity with baseline mode is two-directional.** Each toggle disengages the other and
refuses while the other is busy, and each Send-restore is guarded on the other's flag. One-directional
fails silently: with both armed the panel repaints Send purple (revise's sync runs last) while
`onSendButtonClicked` still routes to baseline (which precedes revise in the MRO), so a button reading
"Revise step" starts a baseline whose first act deletes every downstream node. Revise is disabled while a
baseline runs (it has repointed `_currentLogDir`); Exit and the replay controls refuse during a revision;
the reply carries `_guidedSessionEpoch`. Exit tears the mode down **before** `_prepareCleanRuntime`,
which clears `_reviseActive` as a raw attribute write.

The glyph is **text**, not a `:/Icons/` resource — `qt.QIcon` on an unregistered path returns a NULL icon
rather than raising, rendering as an empty button. It carries U+FE0E so Windows font fallback does not
draw a colour cartoon hand. It is **visible from panel build**, disabled with the reason in its tooltip,
because a hidden button reads as a missing feature. Its stylesheet needs an explicit `:disabled` rule — a
stylesheet `color` REPLACES the palette for every state, and this button is disabled most of its life.

### Baseline comparison harness

Step **Back** to a step and click the **balance** button. Three alternative code producers:

- **`pure_llm`** — one `chatIsolated` call, minimal prompt + scene summary. No retrieval, tools,
  knowledge base, CLI or history.
- **`online_only`** — `chatWithToolsIsolated` with pre-retrieval and the search tools, CLI ablated:
  schemas stripped **by identity**, `suppress_extension_cli` short-circuits the CLI/`ext:`/cookbook
  sections.
- **`claude_code`** — code arrives over MCP from an external Claude Code session running the
  `slicer-skill` skill. `BaselineMCPBridge` **attaches to the skill's own `slicer-mcp-server.py`**,
  swapping *only* `execute_python` while armed and restoring **by identity** (skipped if the user
  re-pasted the script). Not pasted means arming is refused with instructions, never a silent
  substitution; the transport is in every run record.

All three share the tail of the real pipeline (CodeValidator → SafeExecutor → completion), so only the
producer differs. They deliberately do **not** get plan validation, `ApiSanityChecker`, or
self-correction — those are properties of the system under test.

**The context boundary.** A baseline gets everything describing the **task and the world** — what a
surgeon in front of the running application has — and nothing produced by the **offline analysis**, which
is the artefact under test. `TASK_STEP_KEYS` is the ALLOW-list (`step_id`, `operation_type`,
`description`), so a field added to `workflow.json` later defaults to withheld; `WITHHELD_STEP_KEYS`
names the other side explicitly so the ablation is legible in review. `build_step_brief()` adds the
clinical guidance from `step_instructions.json` (the words the panel shows), position in the procedure,
completed steps, values and nodes already chosen, and a lookahead marked *context only*.

`step_context` is computed **once**, in `_beginBaselineRun`, for every mode — so the three cannot drift
apart by construction. The two prompt-driven modes have it injected; Claude Code reads the same bytes
from `MCPConnection/current_step.md`, because without it that session would be the only condition
working from the user's sentence alone.

Condition-specific generosity, so a failure is a failure of the *approach*: pure LLM gets the
CodeValidator blocked list verbatim and full properties of up to 14 relevant nodes up front (it has no
tools to ask mid-turn); online-only keeps the raw `ext:<Name>/` source trees searchable and advertised
with a recipe for deriving an API from source, at 16 tool rounds, since cutting it off mid-search would
measure the budget instead of the approach.

**The generated code is unreachable, by enforcement not convention.** The prompt is user-typed,
`TASK_STEP_KEYS` carries no template, the CLI sections and schemas are dropped, the isolated chats never
read history, and the rewind deletes the step's own output. The one channel that was *open* was the
search tools — `ReadFile("../../extension_CLI/<Ext>/templates/<step>.tpl")` would have returned the
answer. `_DENIED_SUBTREES` refuses any path resolving inside `Resources/extension_CLI`,
`Resources/Prompts`, `SlicerAIAgentLib` or `logs`, checked on the **resolved** path. Claude Code is
fenced by its `--add-dir` set.

**Nothing from after the stepped-back step reaches a baseline.** Rewinding truncates `completed_steps`,
both mirrors, `repeat_states`, `last_result` and the checkpoint list, and deletes downstream nodes —
*before* the step context, scene read and node-property read. The one deliberate exception is the
**lookahead** (`BASELINE_LOOKAHEAD_STEPS`, default 3): upcoming step *descriptions* marked "context only",
which is cookbook prose and what a surgeon sees on the next page. Note it is **more than the pipeline
has** — the pipeline dispatches with no lookahead at all — so it favours the baselines. Set it to `0` for
a strict ablation.

**Conditions tested back-to-back on one step are isolated**, self-healingly: each successful baseline
re-creates the step's checkpoint and captures its before-snapshot *after* the rewind. A **failed** attempt
used to break this, so `rollback_failed_step()` does on failure what `_record_checkpoint` does on success
and **keeps** the pending checkpoint. The pipeline is untouched — its pending checkpoint survives
self-correction, so it is already self-healing and it is the system under test. The one exception is
`PedicleScrewPlanner`, the only wizard extension, where downstream nodes are deliberately kept (deleting
them hangs its cached-Python-ref `onEntry`) — conditions tested on it are *not* isolated and should be
reported separately.

**Which steps are comparable.** `CODE_STEP_OPERATION_TYPES` is an **allow-list**, so a type added later
defaults to not-comparable: `extension_op` and `slicer_op` qualify; `user_choice` (the user picks a value
later steps read), `user_interaction` (no producer stands in for a hand), `branch_op` (the answer, not
the code, decides the next step) and `review_op` (no template at all) do not. Across the nine cookbook
extensions that is 106 of 184 steps (58%).

**The prompt is never authored by the panel** — the box is only ever *emptied*. The prompt is the
independent variable of the comparison.

**Stepping resets the arm** (`_resetBaselineForNavigation()`), so neither the previous step's mode nor its
prompt follows the user along the timeline; it returns False during a run and the caller abandons the
navigation. The button is **hidden outright** on a non-comparable step, safe only because the arm cannot
outlive the step: Back/Forward reset it and `_updateBaselineControls` auto-disarms on an auto-advance onto
a non-comparable step. **`_baselineActive`** is the toggle intent; **`_baselineEngaged()`** is that intent
resolved against the step in view, and engagement drives visibility, the input gate, Send's caption and
Send's routing.

**Input gating.** While a workflow runs, `promptInput` and `sendButton` are off — and switched back on by
baseline mode, the one mode that needs them. `_guidedWorkflowOwnsInput()` is the predicate and
`_setSendEnabled()` the single funnel every *enabling* call site goes through, so no stray
`setEnabled(True)` defeats the gate (disabling sites are left direct — disabling is always safe).

**Debug-view isolation.** `_debugContext` is which buffer is *displayed*, `_debugWriteContext` which
receives new content. They may diverge — when a baseline finishes and auto-advance hands back, the
pipeline's output accumulates invisibly and reappears complete when the baseline row closes.

## Logs and artifacts

`RunLog.py` owns run-folder naming and artifact writing (Qt-free, fail-soft — a logging failure must never
abort the run being logged).

```
logs/ZygomaticImplantPlanner_baoyawen_pipeline_20260803_154954/
     \_____________________/\_______/\________/\_____________/
          procedure          subject condition      when
```

**Procedure first, timestamp last**, because analysis is per procedure and per subject — the four
conditions on one patient are the unit of comparison, and a leading timestamp scatters that grouping. A
name sort is therefore **not** chronological; sort on the trailing stamp. The **subject** is derived from
the folder the scene's data came from and is **omitted entirely** when undeterminable — a placeholder
would silently merge two patients' runs.

`_sceneSubjectName` takes the most common parent folder of the storage nodes' files, and a count alone is
not enough: opening any module needing the colour logic loads ~20 colour tables from
`<slicerHome>/share/…/ColorFiles`, beating a case folder 20 to 2 (observed, as a run folder named
`…_ColorFiles_pipeline_…`). It depends on which modules the session touched, so it is intermittent and its
symptom is a plausible name. Two filters, either sufficient: only **user data** votes (`_isUserDataNode`
— not `HideFromEditors`, `SaveWithScene`; every colour node sets `HideFromEditors`), and
**application-owned directories are excluded** (`slicerHome`, `extensionsInstallPath`, our `logs/`,
Slicer's temp, the DICOM database), compared as paths not by `startswith`. The name is fixed at workflow
**start**, so a mislabelled run stays mislabelled — and the experiments analysis pairs a run with
`Dataset/<subject>`, so that is not only cosmetic.

Other names: `task_pipeline_turnN_<stamp>`, `refused_pipeline_<stamp>`, and a flat
`…_<condition>_<step>_a<n>_<stamp>` for a baseline. **One run folder per workflow, one subfolder per
step**; step folders are zero-padded purely so they sort, and the true unpadded `step_id` is in
`step.json` and the manifest.

A run folder has exactly **two children**, so which one a reader wants is answerable from the name:

```
logs/<run>/
  runtime/                   everything written while the run executes
    run_manifest.json        condition, subject + source path, prompt, model, router cost, per-step
                             status/seconds/errors, totals. Rewritten on every mutation, so a
                             session killed mid-workflow still leaves a usable record.
    role_trace.json
    00_router/               messages_sent.txt, reply.txt, call.json
    cb_step_01/
      step.json  code.py  agent_plan.json  execution.json  output.txt
      role_trace.json  timing.txt  thinking.txt
      correction_1/          attempt.json, first_prompt.txt, code.py, response.json
      revision_1/            request.txt, messages_sent.txt, reply.txt, revision.json
  Statistic/                 written at Exit
    timing.txt
    scene/                   scene.mrml + one flat file per node
```

`_currentLogDir` is the *runtime* dir (so every writer is unchanged); `_currentRunRoot` holds both and is
what "Exit without saving" deletes. `_artifactDir()` is the single funnel; `_setStepLogContext(step_id)`
opens a step's folder and repoints the LLM client's prompt dumps. A baseline parks the pipeline's folder,
manifest, step context **and role trace**, so the step it auto-advances to neither logs inside the
baseline's folder nor inherits its events. A baseline folder also holds `prompt.txt`, `messages_sent.*`
(the **exact** payload the condition received) and `step_context.json`.

**No `thinking.txt` in a clean guided run is correct.** The routing call is deliberately non-thinking, and
dispatched steps call no model at all, so reasoning appears only on self-correction or in a baseline
folder. `00_router/call.json` records the flags and states this.

Three earlier defects this layout replaced, all of which cost data: every step wrote plan, role trace and
timing to the **same three filenames** (a 33-step run retained only the last step's); correction artifacts
were keyed by attempt number alone (two steps failing on attempt 0 overwrote each other); and the pipeline
persisted **no execution result at all**, leaving the system under test the least-instrumented condition.

### Saving a flat scene

**`saveScene(<dir>)` cannot produce a flat folder** — a directory routes to
`SaveSceneToSlicerDataBundleDirectory`, which builds `Data/` and `private/`. And **`saveScene("….mrml")`
writes the XML and NOTHING else** — it is `SetURL` + `SetRootDirectory` + `Commit()`, which serialises node
*elements* but never asks a storage node to write its data, so the result names files that do not exist
and Slicer only reports it when the scene is *opened*.

`save_scene_flat()` (in `PlanningRecorder.py`; `_saveSceneFlat` delegates) reproduces
`qSlicerSaveDataDialogPrivate`: skip non-storable / `HideFromEditors` / `!SaveWithScene`,
`AddDefaultStorageNode()` and skip anything needing none, skip `fileWriterFileType == "NoFile"`, name each
file `<sanitised name>.<GetDefaultWriteFileExtension()>`, and write the **nodes first, the scene last**.
Same-named nodes are de-duplicated.

**The scene is written several teardown steps AFTER the Exit click**, so "what you saw is what is
saved" has to be made true rather than assumed. Between the click and the write, `_resetGuidedSession`
leaves placement mode, drops the threshold preview, lets the interaction manager delete what it
created, and clears the replay timeline (which restores the live scene when the user was
mid-preview). Today all of those *remove nodes* rather than flip visibility on a survivor, so the
round trip is faithful — by the absence of a counter-example, not by construction.

`_capturePresentationState()` at step 0b records every display node's visibility before any of that
runs, and `_restorePresentationState()` re-applies it immediately before `_saveRunStatistics`. It is
a **guard**: a no-op on the common path, skipping any node the teardown deleted (re-creating one
would save geometry the run no longer has), touching visibility only so a teardown that legitimately
changes a colour or an opacity is left alone, and **logging a warning** when it does restore
something — a teardown step that quietly changes what the surgeon left on screen is worth knowing
about, not worth silently correcting on every run. The failure it forecloses is invisible: a reopened
scene showing something that was hidden reads as a planning mistake, and the saved file is the only
record either way.

The guard preserves the state at Exit; it does not decide what that state should be. That is
`SAVE_HIDDEN_NODE_PREFIXES`, applied by `_applySaveVisibilityPolicy` **immediately after** the
restore and before the write — and the order is the point: the restore undoes what the teardown
changed by *accident*, the policy applies what the study decided *on purpose*, so running them the
other way round would put the hidden nodes back.

**A procedure may declare which of its nodes are working aids rather than results.** The mechanism is
generic (prefix match over `vtkMRMLDisplayableNode`, live scene, save time only); the table is one
line per procedure and a procedure absent from it has nothing hidden, which is what every one of them
did before this existed. BoneReconstructionPlanner leaves two families behind, one per view, and
**no node in a saved scene is restricted to a 3D view** (`viewNodeRef` is unset everywhere), so each
lands on top of the bone the other view is for:

- `Transformed Mandible <n>` / `Transformed Mandible Segment <n>` — the mandible registered **onto the
  fibula** to work out where to cut. A planning aid, drawn over the fibula.
- `Mandible <n>` / `Mandible Segment <n>` — **whole-mandible surfaces**, not pieces: `Mandible <n>` is
  a point-for-point copy of `decimatedMandible` (identical vertex count; BRP makes one per cut as
  dynamic-modeler input). A 2-segment plan stacks four of them on the remnant and a 3-segment plan
  six, all coincident — so they z-fight, and the more segments a plan has the worse it looks, which is
  why the fault reads as "this case is broken" rather than as something every case does.

What survives is what the view is for: `Resected mandible` (the remnant, ~4.5 k points against ~8 k)
and `Transformed Fibula Segment <n>` (the graft). Two spellings carry that distinction and both are
load-bearing — the key is `"Transformed Mandible"` and not `"Transformed"`, or the graft would go; and
`"Mandible "` carries a **trailing space**, without which it would also match `MandibleSegmentation`,
`mandibularCurve` and `decimatedMandible`. None of these families is hidden by BRP itself and all are
recreated on every plan update, so a hide applied by hand during a session does not survive to the
save — which is what this table exists to make unnecessary.

**`_clearMaximizedViewForSave` un-maximizes, and needs no table** — an operator can double-click a
view in any procedure. Slicer records that as a `MaximizedView` reference on the layout node, and it
sits ON TOP of `currentViewArrangement`: the scene records the procedure's own layout and still opens
as a single panel. The saved arrangement therefore looks correct to anyone inspecting the file, which
is what makes it hard to see — three of the 37 saved BRP runs were in that state with the layout id
reading 101 in every one of them. Both accessors are fetched with `getattr`, so a Slicer whose
`vtkMRMLLayoutNode` lacks them is left alone rather than crashed at Exit.

Every mutation is undone in a `finally`: storage file names, scene URL and root directory, and —
critically — `SetStorableNodesModifiedSinceRead()`. Writing a storable node stamps its `StoredTime`, which
clears `GetModifiedSinceRead()` scene-wide; without the restore the surgeon's own segmentations show as
"Not Modified" in File ▸ Save Data, quitting raises no unsaved-data warning, and the only copy on disk is
the one inside `logs/`. Slicer's own MRB writer does this restore; the directory writer does not.

A user `vtkMRMLColorTableNode` needs its own storage node — it serialises `numcolors` but not the colours.

### Two clocks

Per-step `seconds` is SafeExecutor time — *machine* time, not how long the step took. So `open_step()`
stamps `opened_epoch` and `finish_step()` stamps `completed_epoch`, giving **wall** (screen to screen),
**exec** (accumulated across pre+post templates, repair retries and loop iterations) and **wait** =
wall − exec, attributed to *the surgeon* on `HUMAN_IN_LOOP_TYPES` and to *runtime overhead* on the
automated two. The total is anchored to the **Send click**, not `started_epoch` (stamped only once the
router answered).

`manifest["timeline"]` records a row per step *visit* and per replay review; `steps` holds the aggregate
that `collect_runs.py` reads. A replay row's time is **taken out of** the step on screen, or a review lands
in a `user_choice` step's `wall` and — since `exec` does not move — prints as think time on a step nobody
was thinking about.

Five invariants, each producing a plausible number rather than an error when wrong:

- **A step is measured per *visit*.** Within one visit the clock must *not* restart, or a choice step's
  think time and an interaction step's placement time are erased. But a step can be **re-visited** — a
  repeat block re-dispatches every member with `start` (6 of 9 workflows have multi-step bodies), and so
  do the replay stepper and baseline harness. Spanning that makes each body step cover the whole loop:
  spans overlap, their sum exceeds the run, and a neighbour's hand time prints as an automated step's
  overhead. `open_step` banks the closed span and starts a new one **only on `action="start"`**.
- **A step entering a wait is not a step completing.** The execution recorder stamps every execution as a
  completion, before the runtime has decided; `reopen_step()` retracts that on the entering-wait branch.
- **The no-code path only completes a step that actually moved on** (`next_step` or
  `workflow_completed`) — it is also reached by a step entering a wait.
- **Exit seals whatever was still open.** A span is live only if no `completed_epoch` landed *since* it
  opened — `finish_step` deliberately leaves `span_opened_epoch` in place so a re-visit can bank it, so
  its presence alone is not "still running".
- **`build_run_statistics()` is a pure function of the manifest**, and its five-way split is never clamped
  — a negative residual prints as `[!] clocks inconsistent`, the only evidence a reader has that the two
  clocks disagree.

The scene is saved **after** the replay timeline is torn down, so the hidden `vtkMRMLSceneViewNode` per
step is already gone. Both halves are fail-soft and independent.

**The aggregate view is derived, not written.** `scripts/collect_runs.py` walks `logs/*/runtime/` (falling
back to the run root for pre-split runs) and emits one row per (run, step) across **all four** conditions.
It replaced an append-only `baseline_runs.jsonl` that duplicated the per-run record byte for byte and
covered only the three baselines — a second live writer of the same facts can drift from the first; a
derivation cannot.

## Experiments panel

Per-procedure analysis of runs under `Experiments/<Extension>/`. `experiments/<name>.py` holds the
numerics (Qt-free, so it runs and is checkable outside Slicer) and `<name>_panel.py` the button;
`@register_experiment_panel("<Extension>")` registers, `_PANEL_MODULES` lists what to import.

**`EXPERIMENT_PANELS` maps a procedure to a LIST of builders.** A dict of one made the later import
silently erase the earlier — nothing raised, and which panel survived depended on tuple order.
Registration appends (replacing in place on reload, keyed on `__module__` + `__qualname__`), and a failing
builder no longer calls `_clearExperimentContent()`, which would delete an earlier panel's widgets because
a later one raised. No shipped procedure claims two today, which is why `check_longbone_analysis.py` §10
pins the property against *synthetic* builders: an invariant nothing exercises is the one that rots.

`run_timing.py` is shared — what a run folder looks like and what its `Statistic/timing.txt` says are
properties of `RunLog`, not of a procedure. It parses the **rendered report** rather than the manifest,
deliberately: the report is what `Statistic/` guarantees and what a reader compares against, so a case
whose manifest was lost still yields a row. Every field is an explicit regex, so a rephrased line leaves a
blank cell instead of a wrong number.

**Every reader goes through `run_timing.resolve_experiment_dir()`; nobody joins `EXPERIMENT_DIR` by
hand.** Each module declares the flat spelling `Experiments/<Ext>`, but the collection is grouped into
tiers (`1_Quanti_Eva`, `2_Quali_Eva`, `3_User_Study`) whose names are the study's to choose — the first
has already been renamed once, from `1_QuantitativeEvaluation`. When a hand-joined path misses, **nothing
raises**: `discover_cases()` returns `[]`, every panel prints "No cases found", and every real-data
section of every `check_*_analysis.py` hits its `if not results: SKIP` guard and the checker reports a
pass. All eight procedures were in exactly that state, and the checkers were green throughout.

So the resolver searches for the **extension's own folder**, which cannot be renamed without breaking far
more than this: flat first (an untouched checkout is unaffected), then **one** level of tier, in name
order. One level only — a full walk descends into the runs themselves, tens of gigabytes, and could match
a folder inside somebody's saved scene. Nothing matches on the tier's *name*, which is the whole point.
Two tiers holding the same procedure is logged rather than resolved silently: one of them is a copy, and
scoring the wrong one yields a complete, plausible workbook off stale data. `experiment_dir_label()` is
the same resolution rendered for a panel's own prose, so "no cases found under …" never names a folder
the analysis is not reading. `check_longbone_analysis.py` §11 pins all of it against a synthetic tree,
including that no module has grown a hand-join back.

| module | scores | needs Slicer |
|---|---|---|
| `zygomatic.py` | relative BIC against the surgeon's STL paths | no |
| `orbital.py` | symmetric surface distance vs the surgeon's label, plus a colour map | **yes** |
| `shoulder.py` | the four measures of Li et al. (IJCARS 2022;17:1017-1027) + the t1/t2/t3 split | no |
| `cranial.py` | DSC / HD95 / bDSC of AutoImplant 2021 (Li et al., MedIA 88 (2023) 102865) | no |
| `pelvic.py` | reduction error **read** from each run's recorded annotation transform | no |
| `longbone.py` | the rigid residual `E = G · P^-1` over both kinds of case | no |
| `pedicle.py` | Gertzbein-Robbins grade and the millimetres behind it | no |
| `mandible.py` | fibula vs a **predicted** healthy mandible segment (Guo et al. §4.2 / Nakao) | no |

### The user-study evaluation

The **User study** subsection (`user_study.py` + `user_study_panel.py`, last child of the Experiments
group) scores `Experiments/3_User_Study/Results/【arm】procedure【participant】/` folders into
`Quanti_Quali_Eva/<the folder's own name>.xlsx` -- one workbook per folder, so the count follows the
folders and a new participant needs no code. It **re-derives no metric**: each procedure's
`build_report` takes an optional `cases=` run set (built by `run_timing.discover_runs` from the two
explicit folders, since runs and `Dataset/<procedure>/` are not siblings here), and the evaluation only
adds a *Run set* sheet (what was scored) and an *Interaction* sheet (the recorder's own numbers, the one
measurement both arms share -- the Timing sheet is built for the guided arm's steps).

- **The procedure comes from the run folder names** (`<Extension>_<subject>_<condition>_<stamp>`), never
  from the display name, which is the study's prose; `ANALYSES` maps extension → module + the panels'
  defaults. A run filed under the wrong arm (its condition disagrees) is reported, not scored silently.
- **Runs are listed in the order performed** (by the folder's stamp), not by name: the first case of
  each arm is where the learning happens.
- **It writes only the workbook**, with one deliberate exception: orbital runs with `write_scenes=False`
  (same numbers, no colour maps spliced into the runs, no scene close), while mandible keeps its cache of
  each run's predicted ground truth in `Statistic/analysis/`.

### Rules that recur across these modules

Each yields a believable number instead of a failure when got wrong:

- **Prove the coordinate frame; never assume it.** An LPS/RAS mix-up mirrors anatomy to the far side of
  the head, where it still intersects bone and still produces a distance. In `shoulder.py` the flip is
  *exactly invariant* for every angle (the transform is orthogonal), so only the density integral notices
  — and it notices by reading a flawless **1.000**, because the mirrored path leaves the CT array and
  numerator and denominator become the same out-of-bounds sentinel. Hence three independent guards there,
  `_frame_gap_mm` in `orbital.py`, and a per-case measured frame in `longbone.py`.
- **One meshing pipeline for every surface compared**, at one smoothing setting — a distance between
  surfaces built by different rules measures the rules. `orbital.py` routes the ground truth through a
  segmentation node rather than meshing its label map directly, so it takes the *same* conversion.
- **Report a percentile, not a maximum.** Marching cubes can always produce one stray vertex, which moves
  the maximum arbitrarily and the 95th percentile not at all. On `cranial.py` quote the **median** HD95
  (2.1 mm), not the mean (8.0): the outliers are one-directional — on one case *none* of the prediction is
  >20 mm from the truth while 67% of the truth has no prediction within 20 mm, i.e. accurate wherever it
  exists and covering a fraction of the defect. HD95 pools both directions; `gt_covered_2mm_pct` and
  `implant_on_gt_2mm_pct` separate them, and are the paper's own feasibility criteria.
- **Never pool two populations.** `shoulder.py` reports `delta (planned)` and `delta (BEST EFFORT)`
  separately — when nothing in the cone keeps the screw inside the bone the planner returns the
  deepest-reaching candidate, never optimised for density, and that is half the screws.
- **Report both denominators when two are defensible**, rather than picking silently: `shoulder.py`'s
  full cone vs the half actually searched (plus the sweep at 2x resolution, since the denominator is a
  maximum over a grid); `cranial.py`'s `t = 10` **voxels** (published) vs a fixed 5 mm band;
  `pedicle.py`'s perpendicular caliper vs the chord through the axis.
- **Measure the tool's geometry, do not assume it.** `shoulder.py` reads cone half-angle, height and
  radius from the saved model because all three are spin boxes the surgeon can change — the shipped
  half-angle is **22.5°**, half the paper's α. The cone *axis* is the middle peg's direction, never fitted
  from the cone: that base is a 180° half-disc, so a centroid fit is 5.5 mm off-axis.
- **Fix the colour scale** (`COLOR_MAX_MM`). Auto-ranging renders a 0.5 mm case and a 4 mm case with the
  same spread of colour, so the one thing a map is for stops working.
- **Pair the result with where it started.** 0.8 mm is excellent on an orbit that was 4 mm out and
  unremarkable on one that was 1 mm out — `orbital.py`'s IMPROVEMENT block (which is why it also scores
  the *fractured* segmentation) and `longbone.py`'s `initial_*` / `residual_fraction`.
- **A read number beats an estimated one — but it can be stale.** `pelvic.py` reads the recorded
  transform instead of re-deriving it by ICP (which agreed to 0.009-0.034°), and the check script asserts
  statically that no `kabsch`/SVD has grown back. The hazard is a ground truth re-annotated after the
  record was written — which happened, 5.83° where the record says 2.25° — so `transform_verified` judges
  the record against the **files** while `record_consistent` judges it against itself. `verify=False`
  leaves the second **blank rather than True**: a blank and a failure must not print the same.
- **State which point a displacement is measured at.** One case's Left Ilium is 1.74 mm out at its
  centroid and **6.13 mm** at its worst surface point, because 2.25° moves the far end of an ilium far
  more than its centre. `point_error_*` is the figure to quote.
- **Do not compute what the data cannot support; name the blank.** `mandible.py` omits Nakao's `Er` (it
  needs a located midline, the step Guo et al. call unreliable); `pedicle.py` omits pedicle-axis deviation
  (the axis would come from the trajectory it judges), facet violation and cortical/cancellous contact;
  `longbone.py` leaves the clinical split blank on annotated cases, since the obvious shaft-axis estimate
  disagrees with the recorded axis by a median of 6.5° — larger than most residual rotations it would
  decompose. A circular number that looks like a measurement is worse than a blank column.
- **Pair by geometry, not by file name.** `zygomatic.py` pairs implants by entry point (`1.stl` belongs
  with `Implant_3`) with a `MAX_ENTRY_MATCH_MM` ceiling, since the assignment is total. `shoulder.py`
  pairs within `ENTRY_PAIR_TOLERANCE_MM`, which is what makes its comparison *paired*: the hand plan
  reuses the pipeline's baseplate pose (0.000000 mm apart on every screw), so one cone serves both sides
  and `delta_gain` is a meaningful subtraction. `pedicle.py` takes the screw's **side** from its entry
  relative to the vertebra centroid — the extension's helper calls index 1 "left" without looking at a
  coordinate, so on both saved runs every screw named `_L` is on the patient's RIGHT, and since
  medial/lateral are defined against the midline the name would invert the safety distinction.
- **Reproducing the tool's own arithmetic is the evidence the input was read correctly.**
  `shoulder.py`'s `score_reproduced` equals the score the run printed at the time, bit for bit — which
  matters because the extension stores none of these numbers. `zygomatic.py` keeps `planner_bic_score`
  distinct from the physical `bic_score` the comparison divides. `mandible.py` reproduces the shipped
  `repair()`'s graft bounds exactly.
- **Take geometry from the table, the mesh only as a witness.** `shoulder.py` reads the manual trajectory
  from the TSV, not the `.vtk`: that mesh is the screw cylinder, overhanging its entry by 3 mm and 3.1 mm
  in radius, so neither its extreme vertex nor its cap centroid is the trajectory's start.
- **A step in no phase is named, not dropped.** `PHASE_STEPS` maps steps to t1/t2/t3 plus t0 and
  t_refine, which sum into the total and into none of the three — charging post-plan dragging to
  "automatic planning" overstated t3 by 8.3 s, and a renumbered workflow would make the phases silently
  shrink.

### Slicer-side and I/O constraints

- **`numpy_to_vtk` defaults to `deep=0`**, making the VTK array a *view* on the numpy buffer. No VTK object
  may outlive what owns its memory; `check_orbital_analysis.py` enforces `deep=1` at the AST level, since
  there is no VTK outside Slicer to test against.
- **A Slicer plane-cut model is PARTIALLY welded** — geometrically closed, topologically open — so
  `vtkPolyDataToImageStencil` over-fills a resected mandible by **4%** and under-fills a cut fibula segment
  by **38%**, both as plausible volumes; the inflated mandible made the completion network predict a 45 cm³
  blob where correct input gives 19 cm³. `mandible.py` uses **ray parity** (each triangle independent) for
  the metrics *and* the network's input, swept along all three axes and unioned: a ray with an odd crossing
  count is skipped, so a genuine hole costs the columns through it until another axis recovers them. The
  union matches VTK's own stencil to 0.001 cm³.
- **Crop before meshing** — a ground truth on the full CT grid is 31-142x wasted work and exhausts memory.
- **Hand `_write_error_scene` the nodes to write**, never `getNodesByClass` — that also returns Slicer's
  built-in colour tables, some pointing into the application's own installation. And it checks each file is
  **on disk** before splicing: a scene must never be edited to point at a file whose write was assumed.
- **The `scene.mrml` splice is XML surgery**, not load-modify-save (the scene carries a 40 MB CT). The
  original is copied to `scene.mrml.orig` **once**; every spliced id carries `ID_MARKER` so a re-run
  *replaces* rather than stacks; the rewrite uses a `(?![0-9])` lookahead, without which `…ModelNode1`
  would be rewritten inside `…ModelNode10`; references are followed only into `_SPLICEABLE_TAGS`, since a
  display node also references its *view*.
- **Storage file names in `scene.mrml` are URL-escaped**, and every model this procedure saves has spaces
  in its name — joining `fileName` verbatim gives a path that does not exist, and the only symptom is a
  scene reporting no pieces at all. Roles come from the subject-hierarchy **folder**, never the file name.
- **`volume_io.read_nrrd` cannot read a segmentation with overlapping segments** — that is **4-D**, and its
  `list` axis of LAYERS is the first of `sizes:` and therefore the **last** array index, so `array[layer]`
  is in bounds, the right dtype, and a slab of the volume instead of a layer. A segment is addressed by
  `(layer, label value)`. `segmentation_io.py` ignores `Segment<N>_Extent` (it is the *tight* box, so a
  truncated read looks exactly like a correct one), scans in slabs with a one-plane halo, and takes
  centroids from per-axis marginal counts — `np.nonzero` over a half-full 32 MB slab costs 380 MB.
- **Segments are resolved by NAME.** One `.seg.nrrd` holds several; reading it as non-zero scores against
  the whole skull and reports a DSC near 0.2 that reads like a pipeline failure rather than a coding error.
- **Spacing is the COLUMN NORM of IJK→RAS, not of its inverse.** The inverse gives voxels-per-mm, scaling
  every distance by ~2.6x and leaving DSC untouched — so only HD95 shows it, and only against a reference.
- **The metric window is a crop, and the crop is exact** — both surfaces lie inside `bbox(gt | pred)`, and
  a margin ≥ `t` reproduces the border predicate exactly. 32 minutes uncropped, 5 cropped, proven bit for
  bit rather than taken on trust.
- **ITK conventions are all three wrong-way-round** (from-parent, LPS, centre of rotation folded in), each
  undone explicitly. Slicer's Python has no `h5py`, so `read_itk_affine` locates the twelve doubles by
  their *properties* and requires **exactly one** match; the recovered pose is not trusted until it equals
  what the 7 annotated runs recorded independently (to 6e-14). Composition order comes from `scene.mrml`,
  never from file names.

`orbital.py` and `cranial.py` share the dangerous code (meshing, distance filter, write gate, splicer) by
**import, not copy** — they edit a saved run in place. Only the colour table and model node are
re-implemented, because orbital's bake in a 3 mm ceiling and a cranial map on that scale is red everywhere.

The orbital panel **refuses while a guided workflow is open** and confirms before starting, because it
builds each case's models in the main scene and therefore closes whatever is open.

## The user-study instrument

`PlanningRecorder.py` measures a planning session from Slicer's own input events, and **the same file runs
in both arms**. `RunLog`'s three clocks divide a step between the machine and "the user", which is as far
as a step clock can see: a `user_interaction` step's `wait` covers reading, deciding, dragging and the
pause before Done, and a learning curve is made of the difference between those. The comparison arm — the
extension's own GUI, driven by hand — has no steps at all.

**Seven states, disjoint, summing to the session's wall clock**, in this precedence: `away` (Slicer not
active) > `compute` (main thread blocked) > `view_3d` / `view_2d` / `panel` / `other` (inside a burst of
input landing there) > `idle`.

**`panel` is THIS extension's panel and `other` is the rest of Slicer.** Matching `panel` by class name
counted every module's frame (they all carry `qSlicerWidget`), so a participant who opened Volumes had
those clicks booked as operating the procedure's own panel — flattering the comparison arm exactly where a
learning curve should show hunting through modules falling away. The owning widget is passed in;
`_widget_is_inside` asks Qt's `isAncestorOf` first (no identity comparison — PythonQt hands out fresh
wrappers) and walks the chain for the root itself, which `isAncestorOf` excludes.

Totality is what makes the split checkable rather than a set of overlapping estimates, and
`render_interaction_sections` **prints a warning** when the seven do not sum.

**Span reconstruction is a pure function of the recorded event list** (`partition()`). The filter appends
`(kind, time, target)` and nothing else; every rule lives in `snapshot()`. So it is testable outside Slicer
and revisitable against sessions already recorded — which is why `interaction.json` keeps the spans beside
the aggregate.

Five constants are judgement calls, three failing silently:

- **`BLOCK_THRESHOLD_S = 0.5` is generous on purpose.** Shorter and it reclassifies *stuttery interaction*
  as computation: dragging a cut plane re-clips on a 50 ms coalescing timer, so the main thread is
  repeatedly busy while the person is plainly still dragging.
- **A heartbeat gap is CUT at every input delivery**, and only stretches with nothing delivered in them are
  the machine's. Delivering an event IS the main thread turning over. One rule answers both cases: a click
  starting a four-second computation leaves one four-second stretch; a drag whose render blocks in bursts
  contributes no compute. The all-or-nothing verdict it replaced failed in the direction that mattered — a
  gap runs to the first tick *after* the block, and on Windows the timer message arrives only once the
  queue is empty, so everything queued during the block flushes into that sliver. One click before and one
  release after handed a whole computation back to the person: a real unaided run reported **0.0 s** of
  algorithm time for a procedure the guided arm measured at **24.8 s**. Both edges are open. A busy-cursor
  stretch is never cut this way.
- **A busy cursor makes a live heartbeat count as compute** — several study extensions drive a progress
  dialog, which keeps timers alive. Only `overrideCursor` is used, never "a modal is up": a progress dialog
  and a confirmation dialog are both modal and the second is a person deciding.
- **`BURST_PAD_S = 0.25`** — without it an isolated click is one zero-duration event, so a step answered
  with one button press reads as 100% idle, and the comparison arm is mostly button presses. A burst also
  ends on a **target change**.
- **Hover is not recorded** (`RECORD_HOVER = False`) — parking the pointer over the 3D view while thinking
  is thinking.

**Target resolution.** `classify_widget` matches `className()` by **substring up the parent chain** —
Slicer nests views several layers deep and the receiver is whichever layer holds focus, so an exact list
would go wrong on the next release, as "every click is `other`". The name is read three ways for the same
reason.

**The chain alone is not enough, and the failure is exactly that.** Qt delivers a mouse event to the
`QWidgetWindow` FIRST, and a window's parents are windows, so the chain from the first delivery cannot
reach the view — once repeat deliveries were suppressed, that first one was kept and the whole
3D/slice/panel split sat at zero while the total rose. `_resolve_target` asks the chain and then, only when
it answered nothing, the widget under the **pointer** (`QApplication.widgetAt`). `_upgrade_target` lets a
later delivery correct an `other` already counted, rewriting the recorded EVENT as well as the counter,
since the event's target is what the time attribution reads. Motion is the larger half — moves are not
deduplicated, so a drag filed under `other` moves seconds rather than units.

**One physical event reaches an application-wide filter MORE THAN ONCE, and both consequences are
defects.** Slicer's VTK views re-dispatch, so one press-and-drag counted several clicks — visible. The other
was not: the button state was a **counter**, so N deliveries of one press against one release left it stuck
at N−1 for the session, and `_on_move` gates on it — from the first duplicated press onward every *hover*
was recorded as a drag, absorbing idle time into 3D-view interaction, which is precisely the quantity a
learning curve is made of. Two independent fixes: `_is_duplicate_delivery` counts a physically identical
event once (via Qt's `timestamp()`, which two deliveries share and two real clicks never do; falling back
to identical type/button/position inside 50 ms), and `_read_button_mask` takes the held-button set from the
event's own `buttons()`. Suppressions are counted and printed when non-zero.

**The heartbeat is a SPAN extended in place, not one event per tick** — at 10 Hz the points alone would be
36,000 entries an hour. The panel's status line calls **`live_summary()`** (counters only, O(1)) and never
`snapshot()`, which re-derives the whole partition: an hour in that would be the recorder charging the
participant compute time for the act of watching the clock.

**Clicks are counted only while the Slicer main window is active** — the gate is for time, since alt-tabbing
is `away` and its minutes must not land in `idle`.

### Pausing

**A pause is REMOVED FROM THE SESSION, not bucketed inside it.** `Pause` / `Resume` is one button in both
arms (the comparison arm's recorder panel, and beside the agent's live readout), and it exists for the
interruption a study session cannot avoid — a question, a phone call, the next participant arriving —
which would otherwise land in `idle` and read as the person thinking about the task. So `partition()`
subtracts the pauses from the **session** before deriving anything, `wall_seconds` is the elapsed clock
**minus** the pauses, and the seven states still sum to it. The raw clock survives as `elapsed_seconds`
beside `paused_seconds` and `pause_count`, so the two reconcile and the report states the difference
rather than quietly shortening a trial.

Three ways to get it wrong, each a plausible number and not an error:

- **A pause manufactures `compute`.** Pausing stops the heartbeat, so every pause leaves a gap with
  nothing delivered in it — the exact signature of a blocked main thread. Clipping the *result* against
  the session is not enough either: the stretch runs from the last tick before the pause to the first
  after the resume, so its two ends survive the clip as slivers of up to a heartbeat each, and a session
  paused twenty times accumulates seconds of compute out of nothing but the operator's thumb. The gap is
  therefore cut in `_blocked_from_ticks` **before** the threshold is applied.
- **A pause lands in `idle`.** `idle` is the partition's remainder and `totals_in_windows`' remainder, so
  anything not explicitly removed ends up there. Hence `totals_in_windows` takes `paused` too — the
  per-step tables are the caller that would otherwise report a coffee break as thinking time.
- **The held-button mask survives the pause.** A button pressed before and released after leaves the mask
  stuck, and `_on_move` gates on it, so every later hover is recorded as a drag — the same defect
  duplicate deliveries used to cause. `pause()` clears the mask, the open alive span and the last pointer
  position; `resume()` re-states the focus, since a `WindowDeactivate` swallowed by the pause would leave
  the time after it credited to the session.

Everything else follows from those: the filter declines every event while paused (including the click on
Resume), `live_summary()` reports the **active** elapsed so the on-screen clock freezes rather than
counting time the report will not contain, `stop()` closes an open pause at the stop, and the per-step
TIME table grows a **`paused` column when and only when the run had one**, so its rows keep summing to the
step's wall clock and an uninterrupted run's report is byte-for-byte what it was before. Pausing is never
undone implicitly — typing in the prompt box does not resume the guided arm, because
`_armInteractionRecordingOnInput` only starts a recorder that is not *running* and a paused one is — which
is why both readouts say PAUSED in capitals.

### Guided arm

**Armed by the FIRST KEYSTROKE, stopped by Exit, then cleared.** It used to start at the router's decision,
several seconds later — but reading the panel, deciding and typing are all part of the trial, and the
comparison arm's **Start** button covers exactly that. Measuring the two arms from different points is the
one thing that makes their totals incomparable.

Three supports: `_startInteractionRecording` is **idempotent** (reached from the keystroke *and* from
`_applyRouterDecision`, which remains the fallback for a spoken request); `_prepareCleanRuntime` no longer
drops a **running** recorder, leaving the leak it guarded to `cleanup`; and `_stopInteractionRecording`
**drops** the recorder after snapshotting it, so the finished request's figures do not sit in the live
counter while the next is composed.

The recorded window is **longer** than `TOTAL RUN TIME` (anchored to Send), and the report prints the
difference and why — a reader who adds the seven states up and finds more than the total is owed the reason.

`_markInteractionStep` sits beside `manifest.open_step`; `_stopInteractionRecording` is **step 1b of
`_resetGuidedSession`**, before the teardown, since the scene write alone is tens of seconds and charging it
to the participant would put a minute of "idle" on every run. The snapshot goes into `manifest["interaction"]`
there, before `_saveRunStatistics` reads it, because `build_run_statistics` is a pure function of the
manifest. Per-step attribution is `by_label`, keyed on step id, so a loop iteration or replay re-run
**accumulates** — matching `steps[]`, not `timeline`.

**A Settings checkbox (`showInteractionCounter`) puts a live readout at the foot of the panel** — at the
**bottom of the whole panel, not inside Settings**, because Settings is collapsed for almost all of a
session and a counter that collapses with it cannot be watched. It works with **no workflow running**,
owning a **preview** recorder written nowhere, because a checkbox showing nothing until a procedure starts
looks broken at exactly the moment somebody is verifying the instrument. `_syncInteractionCounter`
guarantees there is never more than one: two application-wide filters would each see every click and
**double** every number in the run's record, silently, in the arm the study compares against.

### Comparison arm

`addRecorderPanel(self, "<Procedure>")` in `setup()` and `stopRecorderPanel(self)` in `cleanup()` is the
entire diff in each study extension (under `../External_extensions`). The section **inserts itself at index
0** of the module panel, so it is the first thing the operator sees and where the call sits does not matter
— an instrument that has to be scrolled for is one found un-started at the end of a session. The study's
extension list lives in exactly one place, `check_planning_recorder.py::STUDY_EXTENSIONS`; one dropped from
the study is **reverted**, never left instrumented, since a drifted copy records happily and produces
numbers the other arm cannot be compared with.

**Nothing reaches `logs/` until Save.** Start only *names* the folder (from the subject and clock at the
start, so the stamp says when the trial began), Stop only stops the hooks, `write_all` creates and writes
everything — so an abandoned trial leaves no folder to find and delete. The cost is said out loud: a
forgotten Save loses the whole trial. So `PlanningRunRecord.unsaved` is a property the panel reads, the
status line says **NOT SAVED** in those words, starting a new run over a finished unsaved one **asks
first**, and a teardown with an unsaved run logs a warning rather than quietly writing one.

**Closing the scene ends the trial and does not zero it.** The case is gone, so continuing would charge the
next case's minutes to this trial — and the guided arm already ends on `EndCloseEvent`, so without this the
comparison arm would be the only one whose clock ran across two cases. It **stops** rather than resets:
nothing is written before Save, so zeroing here would destroy a trial held only in memory, at the one moment
nobody is watching the panel. Counters return to zero on the next **Start**. The observer is removed in
`shutdown()` — a VTK observer holding a bound method keeps the panel alive and fires into a torn-down one
after a reload.

**Both arms write into the SAME `logs/` — the agent's own, which the recorder finds for itself.** Two arms
in two directories is a comparison nobody can run, and its only symptom is a folder that does not fill up.
`resolve_logs_root()` tries the `SlicerAIAgent/studyLogRoot` setting, then the **installed** agent module's
directory, then `agent_checkout_root()`, and only then a different directory — labelled `NO AGENT FOUND` in
the panel, because that is the one answer meaning the arms will split. `agent_checkout_root` searches for
the directory holding **`SlicerAIAgent.py`**, never for a folder called `Slicer_agent`, and **every**
candidate is confirmed by that file's presence, so a checkout cloned under another name still resolves.

The scene is written *first* inside `write_all` so the manifest and report can name what landed, and its
failure is not fatal. The run folder is `logs/<Procedure>_<subject>_manual_<stamp>/` with the guided arm's
two children and the same file names, so `collect_runs.py` and the analyses read both arms with no special
case. `steps` is present and **empty on purpose**, so a reader sees this arm has no step structure rather
than wondering whether the field failed to write. The token `manual` is declared in **both**
`RunLog.CONDITION_MANUAL` and `PlanningRecorder.CONDITION_MANUAL` (the vendored file cannot import the
library), and a mismatch would put the two arms in folders no analysis pairs up.

**`PlanningRecorder.py` is VENDORED, byte-identical, in five places**, because the comparison arm has to keep
recording on a machine where the agent is not installed. It is also the **one** implementation of
`save_scene_flat`, since every detail of that function is a saved scene that silently does not reload.
`check_planning_recorder.py` asserts the copies are identical, proves the partition, and refuses the two
wirings that both parse: a `def cleanup` nested inside `setup` (never runs, so the filter outlives the
session) and a bare statement in a class body (runs at import with no `self`).

### The per-step split

**The guided report splits all four targets PER STEP**, in two tables — where the TIME went and where the
CLICKS landed — over each step's **own visit windows**, from `timeline` intersected with `interaction.spans`
and `interaction.input_events`. **Not `by_label`**: a label window runs from one step being marked to the
NEXT, so the labels tile the whole recording (gaps and the wait for Exit included) while a step's wall clock
does not — reading those against the wall inflated every row, 7x on the last step, under a header claiming
they summed. `away` is a column for the same reason. Two tables because twelve columns do not fit; neither
repeats `type`, listed directly above. The clicks table shows `wheel` and **not** `drags` — a drag is a
gesture, tallied only at its release into the run-level counters.

That split is the pipeline's distinguishing detail and the one thing the comparison arm cannot say: which
step the surgeon spent their 3D time in, and which step they spent hunting elsewhere in Slicer.

`collect_runs.py` carries it into the comparison table for both arms (`wall_seconds`, `active_seconds`,
`compute_seconds`, `idle_seconds`, `away_seconds`, `clicks`, `clicks_3d`, `clicks_2d`, `clicks_panel`,
`clicks_other`), empty for runs recorded before the instrument existed. The fourth click column is there
because without it the three named ones look like they should sum to `clicks` and do not.

## Coding conventions

- 4-space indentation; PascalCase filenames matching the primary class/responsibility.
- Module/widget/logic/test classes use `SlicerAIAgent*` per Slicer's `ScriptedLoadableModule` pattern.
- Commit messages use conventional prefixes: `feat:`, `fix:`, `chore:`, `docs:`.
- Do not commit API keys, model caches, debug logs, or retrieval indexes.
- **Do not hand-patch `Resources/extension_CLI/*`** — fix the generator and regenerate.
- Every prompt is a file under `Resources/Prompts/`, never a Python string literal.
- After changing anything in `SlicerAIAgentLib/`, **restart Slicer once**; the module Reload button alone
  does not pick up library changes.

## Security

When modifying execution behaviour, update `CodeValidator.py` and `SafeExecutor.py` **together**. Code runs
in Slicer's `__main__` with blocked imports (`os`, `subprocess`, `sys`, `socket`, …) and blocked functions
(`eval`, `exec`, `open`, `getattr`, …). `CodeValidator` maintains `blocked_modules`, `blocked_functions` and
`allowed_modules`. SafeExecutor intercepts VTK C++ errors by temporarily replacing the global
`vtkOutputWindow`.

Prompts that describe the blocked lists **render them from the validator** rather than restating them — a
prompt describing a list that has since changed teaches a rule the executor does not enforce.
