# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SlicerAIAgent is a 3D Slicer scripted extension that embeds an AI-powered agent. Users type natural-language requests, and the system generates, validates, and auto-executes Python code within Slicer's scene. Pipeline: dense vector retrieval → autonomous tool calling → structured planning → AST-based security validation → safe execution → automatic self-correction.

## Build & Test Commands

```bash
# Configure against a local Slicer build
cmake -S . -B build -DSlicer_DIR=/path/to/Slicer-build
cmake --build build

# Build/refresh the FAISS vector index (requires knowledge base in Resources/Skills/slicer-skill-full/)
python scripts/build_rag.py

# Comparison table across all four conditions, derived from logs/
python scripts/collect_runs.py                  # summary + logs/runs_index.csv
python scripts/collect_runs.py --step cb_step_9 # one step under every condition

# Voice matcher: fixed cases + every option of every shipped package. Runs
# OUTSIDE Slicer (the matcher is Qt-free), so it is checkable on every change.
python scripts/check_voice_commands.py

# "Run 2 starts where run 1 started": the __main__ residue ledger that keeps a
# second guided run in one Slicer process from inheriting the first one's
# objects. Stubs slicer/qt/vtk, so it also runs outside Slicer.
python scripts/check_runtime_reset.py

# OrbitalFractureReconstruction experiment analysis: the surface-distance
# statistics, the improvement pairing, and the MRML splicer that edits a run's
# saved scene.mrml in place (backup, idempotency, id collisions).
python scripts/check_orbital_analysis.py

# ReverseShoulderArthroplasty experiment analysis. That module is Slicer-free,
# so this runs the WHOLE thing against the two real saved runs: the angles, the
# NRRD reader, the bone-density integral against the score the planner logged at
# the time, both cone denominators, and the t1/t2/t3 phase split.
python scripts/check_rsa_analysis.py

# CranialImplantPlanning DSC/HD95/bDSC. Runs the metrics against real cases and
# proves the cropped metric window reproduces a full-volume computation bit for
# bit -- a 5x speed-up that would otherwise be a silent approximation.
python scripts/check_cranial_analysis.py            # 3 cases
python scripts/check_cranial_analysis.py --cases 10 # more

# PelvicFracturePlanning reduction error, which is READ out of each run's
# recorded annotation transform rather than estimated. The whole analysis runs
# outside Slicer, and the section that matters builds a STALE record -- a
# ground truth moved one way, a record saying another -- and requires it to be
# refused: an internally perfect record written before its ground truth was last
# saved is the one way a read number can be wrong, and it happened here.
python scripts/check_pelvic_analysis.py

# The ✍ Revise core: which template a step owns, whether a rewritten one may be
# installed, and whether the original comes back. Sweeps every shipped package
# and requires each of its 172 templates to validate against ITSELF -- a rule
# that rejects a working template would reject the model's faithful rewrite too.
python scripts/check_template_revision.py

# The generated-CLI emitter must agree with its OWN validator. The handler-drive
# template and the api proof both read the scanned handler arity, so a call the
# emitter writes and the prover then blocks is unrepairable by construction --
# no rung can rewrite code the generator just produced. Also cross-checks every
# shipped [source drive] template against the installed extension's source.
python scripts/check_handler_drive.py

# A placement the EXTENSION armed must not be re-armed by the runtime. Slicer's
# module template puts GUI actions on the widget, so the handler behind "click
# Manually separate" is what creates the markup, points the active list at it and
# observes the click -- a generated interaction step that creates its own node
# steals the click and the extension's follow-on behaviour never happens, silently.
python scripts/check_placement_starter.py

# A self-correction is fixed against the DISPATCHED code -- prelude included --
# so persisting it back into the .tpl means cutting the prelude off first. The
# boundary is an explicit end marker emitted by the prelude itself, because the
# old "scan for the template's import slicer" heuristic silently failed for any
# template lacking one, and the write-back then refused on every run: the step
# self-corrected, advanced, threw the fix away, and did it again next run.
python scripts/check_prelude_boundary.py

# A range the user chose must reach the step that consumes it. The range step and
# the step that spends it are named INDEPENDENTLY -- the Segment Editor driver
# builds its Threshold-apply block from the effect alone, so it can only write the
# generic {threshold_min}, while the choice carries whatever parameter_name the
# decomposition invented. When the bridge misses, nothing raises: the placeholder
# default silently overwrites the mask the range step just committed.
python scripts/check_range_choice_fill.py
```

Dependencies are in `requirements.txt` — `httpx`, `numpy`, `jsonschema` are explicit; `faiss-cpu`, `onnxruntime`, `transformers` are auto-installed at runtime. CMake installs these into Slicer's Python environment during extension setup.

Tests run from **within Slicer's Python console** (they import `slicer`, `vtk`, `qt`, `ctk`):

```python
import unittest
# Run all tests
suite = unittest.TestLoader().loadTestsFromName("SlicerAIAgentTest")
unittest.TextTestRunner(verbosity=2).run(suite)

# Run a single test
suite = unittest.TestLoader().loadTestsFromName("SlicerAIAgentTest.SlicerAIAgentTest.test_CodeValidator")
unittest.TextTestRunner(verbosity=2).run(suite)
```

Tests live in `Testing/SlicerAIAgentTest.py` and also inline at the bottom of `SlicerAIAgent.py` (class `SlicerAIAgentLogicTest`). Clear the MRML scene between tests when scene state is involved.

## Architecture

### Guided-only runtime

**Every request either enters a generated-CLI workflow or is refused.** `WorkflowRouter.GUIDED_ONLY_MODE`
(True) makes the router's decision final: on a match the workflow starts, and on anything else
`_refuseUnsupportedRequest` shows a modal saying why and hands the prompt back — the traditional
search-and-generate turn below it in `onSendButtonClicked` is never reached. The point is that the
system's claim is that a validated, offline-analysed procedure drives the scene; a silent fallback to
improvised code was both an unmeasured escape hatch in every evaluation and an unreviewed code path in
a surgical context. `GUIDED_ONLY_MODE = False` restores the fall-through in one line.

The refusal is a **dialog**, not a chat line, because it *ends* the request: a chat line inside the
collapsed Debug group would leave the user waiting for a scene that is never going to change. Seven
causes reach it and only two are about the request — the rest mean the install is unconfigured
(`no_api_key`, `no_workflows`, `no_client`, `router_disabled`) or a package is broken (`start_failed`,
`no_first_step`), so `_handleWorkflowRouterTurnIfNeeded` records the cause in `_lastRouterRejection`
and `_refusalMessage` gives each its own remedy. The full agent turn used to paper over all seven
identically, which is exactly why they now have to be told apart. A near miss reports the workflow the
router named (`RouterDecision.rejected_extension`) and its confidence, so "say it the way the procedure
says it" is actionable; the dialog's detail pane lists every installed workflow.

Consequences elsewhere: **queueing is gone** — `ROUTE_WORKFLOW_CONFLICT` used to defer a request until
the workflow ended and then replay it as a traditional turn, which would now promise an answer that
never comes, so it is refused immediately instead (and `_flushQueuedWorkflowPrompts`, the one path that
could start a turn with no user click, is inert). **Refusals are logged**: `logs/refused_pipeline_<stamp>/`
with the `00_router/` call and a manifest sealed `refused`, because the declined routing call used to be
flushed by the very turn that no longer exists — the most common outcome would otherwise be the only
unlogged one. A refusal raised *during* a workflow gets no folder (it would repoint the running run's
`_currentLogDir`) and is recorded as an event of the run it interrupted. **Self-correction and the three
baselines are untouched**: both are scoped to a step of a workflow that already started, which is not
what this flag is about.

### Exiting a guided workflow

**One Exit button, at the right end of the replay row, replaces the per-step Cancel button.** The row
reads `[◀] [progress] [▶] [▷ run from here] [⚖] [✕ exit]`, so Exit sits immediately right of "Run from
here" whenever the baseline toggle is hidden — which it is on every step the pipeline does not answer
with generated code. Anchored to the row's right edge rather than to a neighbour, so it does not shift
as ⚖ appears and disappears, and icon-only like the rest of that row (a text label adds its width to
the row's minimum and can force the module panel wider — see `_applyWidthSafeLabels`). Unlike the
stepper buttons it is **not** driven by `_updateReplayControls`: it is available whenever the panel is
up, including where replay is not. Cancel was a
workflow *action* (`user_action="cancel"` through the runtime), so it only worked where the runtime
could take an action and was hidden exactly where a user most needs a way out — a completed run, a step
with no controls, the panel a dispatch error leaves behind. `_resetGuidedSession()` is a **local** reset
instead: it never asks the runtime for permission, so it works in all of those states, and it is what
the runtime's own `cancelled` result and `onSceneEndClose` now funnel through, so the ways a session can
end cannot drift apart. Closing the scene matters especially: with no traditional turn left, a session
still marked active would keep the prompt box and Send switched off with no escape.

The teardown order is load-bearing, and each step of it is commented in
`widget_workflow.py::_resetGuidedSession`. The three that are easy to get wrong:

- `_clearCompletedWorkflowState(clear_replay=True)` runs **while `runtime.session` is still non-None** —
  `clear_checkpoints()` is a no-op once it is None, and it is what restores the live scene if the user
  was mid-replay-preview and deletes the hidden `vtkMRMLSceneViewNode` snapshots.
- `reset_workflow_state(**None**)` clears the module-global mirrors for **all** extensions.
  `start_for_extension` only resets its own, so a per-extension reset here would leave the *next*
  procedure inheriting this one's completions, choices and loop counters.
- **`_guidedSessionEpoch`** fences work already in flight. A self-correction round-trip is a background
  thread and the auto-advance is a `QTimer.singleShot`; neither can be cancelled, so each captures the
  epoch and `_guidedSessionAlive()` drops it when it no longer matches. Without it a repair can land
  half a minute after Exit and execute code into a scene the user has left.

Exit **closes the scene** (`EXIT_CLOSES_SCENE`), on both answers. It used not to, on the principle
that closing a panel is not consent to delete data; the principle stands and the dialog now asks for
the deletion in those words. What changed is that leaving the scene up was itself unsafe: the next
procedure loads its own data, so a scene still holding the last run's nodes offers them to any step
that looks a node up by name, and — see the extension-lifecycle section below — closing the scene is
the only thing that reliably re-binds the driven extension. "Remember to close the scene" was a
manual step whose omission silently changed the next run, which is the definition of a step that
should not be manual. `_closeSceneOnExit` is `Clear(0)` + `SetURL("")`, i.e.
`qSlicerMainWindow::on_FileCloseSceneAction_triggered` minus its `confirmCloseScene()` prompt — not
reproduced, because a second modal asking what the Exit dialog just asked is how a confirmation stops
being read.

Three fences on that, each guarding a different way it could destroy something the user did not agree
to lose. It runs **last** (the save writes the scene, `clear_checkpoints` restores from its sceneview
snapshots, and the interaction/threshold teardown removes observers from nodes that must still
exist) and **after `runtime.session = None`**, so the `EndCloseEvent` it fires reaches `onSceneEndClose`
and does the one thing wanted there — dropping the entered-module cache — without re-entering the
teardown. It is withdrawn when a requested save did not land: `_saveRunStatistics` now returns a
**positive** check (the `.mrml` exists *and* a node was written) rather than "nothing raised", because
nothing in that path raises — a node that cannot be written appends its name to a human-readable
note. And a `close_scene` parameter carries the distinction `reason` cannot: `_askExitChoice` falls
back to a full exit when the dialog could not be *shown*, and an assumed answer is enough to close a
panel but not to discard a scene. Voice never closes it either (`ACTION_EXIT` passes
`close_scene=False`) — routing voice through the dialog was rejected because the push-to-talk key is
Space, a modal stands the key filter down, and Space activates a `QMessageBox`'s default button, so
trying to say "no, cancel" would confirm the exit.

Exit refuses (and changes nothing) while a baseline run or a stream is in flight, since tearing the
session out from under either would orphan its record.

### A run must start where the first run started

**`_prepareCleanRuntime` returns the process to a freshly-launched state, and it runs on the way IN.**
Called from `_applyRouterDecision` before `start_for_extension` (and again from `_resetGuidedSession`,
so the two can never drift apart). Entry is the only point every run passes through — the previous one
may have ended in a cancel, a scene close, a module Reload, or not ended at all — and it is placed
before `_beginWorkflowRouterTurn`, which creates the run folder and manifest that this clears.

The failure it exists for is silent by construction: nothing raises, the workflow simply behaves
differently on the second run than on the first, so the state is **enumerated explicitly** rather than
discovered. The worst of it, and what motivated the method:

> Every generated template reaches its extension through `try: logic = _<ext>_logic` /
> `except NameError: logic = <Ext>Logic()`, and hands node IDs forward the same way
> (`_<ext>_<step>_id`). That is the intended channel from step N to step N+1 — but the namespace it
> lives in is `__main__`, whose lifetime is the **process**, so it was also an unintended channel from
> run 1 to run 2. A freshly launched Slicer takes the `except NameError` branch; a second run in the
> same session did not, reusing the previous run's logic object with its stale node attributes. An
> extension guard like `if self.fullBoneNode is not None:` then reads "that stage is already done"
> while the scene says otherwise, and the step reveals, skips or recomputes against a patient's data
> that is no longer there. Note the extension's own scene-close reset cannot reach it: that resets
> `widget.logic`, and the templates hold a **second, independent** instance — so an extension whose
> reset looks correct in review still leaks under this runtime.

`SafeExecutor` therefore keeps a ledger of the names its `exec` calls introduced into `__main__`,
diffed around each call **on the main thread** (so it can only ever contain names our own code bound —
the user cannot type into the console while the main thread is inside `exec`), and
`clearIntroducedGlobals()` unbinds exactly those. It is **class-level**: `__main__` is one dict per
process, so the ledger of what we put in it has to be one too — more than one `SafeExecutor` is
built per session (the runtime's own, and the CLI generation api-probe's) and they all write to the
same namespace. A name that merely *predates* us, or one a step rebound, is never removed.

The rest of the method is the same shape — state whose natural lifetime is the process while the thing
it describes has the lifetime of a run. The ones that are not obvious: **"this module is entered" is
held in two independent places** (`_invisiblyEnteredModules` and `WorkflowRuntime._entered_modules`,
the second of which gates the wizard-page probe, so on run 2 it answered True where a fresh launch
answers False); `_lastSliceFitLayout` **skips** the slice fit when run 2 opens on the layout run 1
ended on, its `"__unset__"` sentinel being exactly what makes a fresh launch always fit; and
`_lastCorrectionError` is quoted into the next repair prompt. `_prepareCleanRuntime` runs **after**
`orchestrator.cancel_workflow`, never before — that call reads the state this empties (its workflow
entry, and the interaction manager's created-node list, which it uses to *delete* those nodes), so
clearing first would turn it into a silent no-op and change what Exit does to the scene.

**`RESET_EXTENSION_MODULE_ON_START` rebuilds the driven extension's module widget**
(`slicer.util.reloadScriptedModule`, which is what Slicer's own Reload button runs: re-import,
`cleanup()`, new widget through `setup()`). It is the only generic way to clear what the runtime
cannot enumerate — the extension's own widget/logic attributes, and the state of its Qt controls,
which matters because the runtime drives those controls precisely *because* the extension's handlers
read them at click time, so a combobox left on run 1's answer is an answer run 2 never gave. Gated on
`hasattr(slicer.modules, name.lower())`: the CLI package name is the module name by convention, not by
guarantee, and `reloadScriptedModule` fails on a C++ module with an unrelated-looking path error.
Never fatal — a module that will not reload leaves the previous widget in place, which is exactly the
old behaviour.

`python scripts/check_runtime_reset.py` proves the core of this outside Slicer (it stubs
`slicer`/`qt`/`vtk`), including the bug and its fix as a two-line `exec`.

**The extension's own lifecycle is the runtime's responsibility, because the runtime bypasses it.**
A generated step carries a `# precondition:begin … selectModule('<Ext>') … precondition:end` block
whose only purpose is to fire the extension's `enter()`. `_prepareGeneratedStepCode` **strips** it and
calls `_ensureModuleEnteredInvisibly()` instead: entering for real would make the extension the active
module, and SafeExecutor's restore would then fire its `exit()`, which hides plane handles and locks
planes (BoneReconstructionPlanner) — breaking every later interactive step. So `enter()` is fired on
the widget directly and the module is never made active.

That has a consequence the cache originally got wrong. `enter()` is not one-off initialisation; it is
the extension **binding itself to the current scene** — parameter node, selectors, markup observers.
Slicer's own recovery from a scene close is `onSceneEndClose: if self.parent.isEntered:
self.initializeParameterNode()`, and `isEntered` is False *by construction* here. So after
File ▸ Close Scene the extension is permanently unbound, and a cache that said "entered once per
session" made the next run drive its handlers with `self._parameterNode is None` —
`'NoneType' object has no attribute 'inputFiducials'` at the first `extension_op` step. It is generic
to Slicer's module template, not to one extension (3 of the 7 cookbook extensions are template-shaped).

The cache is therefore **per scene, not per session**: `_invalidateInvisibleModuleEntries()` clears it
on `onSceneEndClose`, and `_ensureModuleEnteredInvisibly` additionally re-enters when a cached module
*looks* unbound — `_moduleWidgetNeedsReentry()` keys on the shape the module template mandates
(`_parameterNode` absent, or pointing at a node no longer in the scene), never on an extension's
identity, and fails open. Re-entry recovers the binding correctly rather than merely avoiding the
crash: `initializeParameterNode()` ends in `_onInputsChanged()`, which reads the selector widgets the
earlier `user_choice` steps already drove, so the recovered parameter node holds the nodes the user
actually picked.

### Voice control

**One microphone button above Send arms the feature; the SPACE BAR gates capture.** Hold Space,
speak, release — the key is the detector, and nothing is transmitted unless somebody is holding it
down. That removes an entire class of failure the energy detector has (a sentence chopped at a pause
because the speaker's level sat close to the threshold, or never triggered because it sat under it)
and is a stronger privacy property than any amount of matching discipline.

**The original always-on mode is still there**, behind `voicePushToTalk` in Settings, for hands-free
use where a key is not reachable — it keeps the energy detector, the room calibration and the
adaptive floor. Everything below applies to both.

**Space is the one talk key Slicer already uses**, so the binding is a setting (`voicePttKey`) with
F4 and F8 offered beside it — both verified unbound anywhere in Slicer 5.10. Bare Space is
`qMRMLSegmentEditorWidget`'s "swap the last two effects", live whenever Segment Editor is entered,
which several cookbook steps do. While voice is armed on Space that toggle stops working, silently;
choosing F4 avoids the collision entirely. **Ctrl+Shift+Space (markups Place mode) is never
intercepted** whatever the setting, because the filter compares the modifier bits and not just the
key — matching on the key alone would break control-point placement application-wide.

The key is taken over **only while a session is armed**, and given back on every teardown path: it is
a global hook, so leaking it would keep stealing the key from the rest of Slicer. Five gates decide
each event, and each one is a defect if it is missing: focus is not a text entry (the prompt box is
directly under the button, and Slicer's Python console is a `QTextEdit`); no modal or popup is up
(the Exit-confirmation dialog is modal and Space activates its default button); the main window is
active; the modifiers match exactly; and a session is actually armed.

Two Qt details the first implementation got wrong. **Auto-repeat is swallowed only while we own the
hold** — returning True unconditionally ate every repeat of a key we had *declined*, so holding Space
in the prompt box typed one space and then went dead. And **`QEvent.ShortcutOverride` must be
accepted**, because Qt resolves shortcuts before it delivers key events: a KeyPress-only filter loses
to any existing `QShortcut` on the same key, which is exactly Segment Editor's Space. A `_held`
boolean is the real state rather than `isAutoRepeat()`, since Windows repeats KeyPress only while X11
can synthesise release/press pairs. `WindowDeactivate` ends a hold, because the release is not
guaranteed to arrive — alt-tabbing mid-utterance would otherwise leave the microphone open.

**The key hook has two implementations and picks one at arm time, by proof.** The correct one is an
application-wide `QObject` event filter (a `QShortcut` cannot be used: Qt has no release signal, and
push-to-talk is *defined* by the release). But PythonQt cannot always dispatch a C++ virtual to a
Python override, and a filter that is never called presents as "the key does nothing", which is
indistinguishable from a dozen other faults. So arming sends one synthetic key event through the
filter and checks it was seen; if it was not, the hook falls back to polling the OS key state at
30 ms. `_voice_debug` says which is live.

Four things stop a mis-recognition from driving the scene:

1. **The matcher declines by default.** An utterance resolves only against the *closed vocabulary the
   step on screen actually offers* — its own option labels, the live node/segment names, the fixed
   verbs — and anything below `ACCEPT_SCORE` (0.62) becomes `ACTION_NONE`. Fixed verbs match the
   **whole** utterance, never a substring, because "we're done with the previous patient" containing
   the word "done" would otherwise advance a step. Free text is the one family where a bare sentence
   is never taken: it needs a "set" / "enter" lead-in, or a free-text step would record whatever the
   recogniser produced as the parameter value.
2. **The mic is muted while the app speaks.** Synthesized guidance goes out of the speakers and
   straight back into the input, and the words the app just spoke are precisely the words most likely
   to match the step's own labels. Pressing the key **cuts the announcement and unmutes** — without
   that barge-in, push-to-talk would sit behind up to twenty seconds of speech and the key would
   start a recording of silence. In the always-on mode the **unmute happens on the speak thread, not
   in the queue handler** — Exit drains `_streamQueue` wholesale, so a `voice_speech_done` event in
   flight when the user exits is never delivered and the microphone would stay muted for the rest of
   the session.
3. **Every committing action is announced, naming the label and not the value** ("Selecting Red
   box."). Be precise about what that buys: the line is *enqueued* before the action is applied, but
   synthesis is a network round trip, so it is heard a second or so after the scene has already
   changed. It makes a mis-hearing audible at the moment it happens instead of three steps later; it
   is **not** a veto. Naming the label is what makes it work at all — a surgeon who said "left" hears
   "Selecting Blue box" and can act on the mismatch, which is exactly where the orbital step's label
   and value deliberately differ.
4. An optional **confirm mode**, which *is* a veto: it arms the action and waits for "yes". The step
   the command was resolved against is stored with it, because the workflow can move on while the
   user is deciding and a later "yes" would otherwise commit a value the new step never offered.

Push-to-talk removes the worst of the residual risk that the hot mic carried — a bare "next" or
"done" said to a colleague no longer reaches the matcher at all, because nobody was holding the key.
The vocabulary hardening earned under the always-on design is kept, both because that mode is still
selectable and because a mis-recognition inside a held key is still possible: "ready" and "go ahead"
are absent from the advance vocabulary, and "right"/"ok"/"okay" from the confirm vocabulary — "right"
is also the *value* of an option on the orbital step, so accepting it as assent would let a surgeon
correcting the side confirm the wrong one instead.

**Every action goes through the widget method the mouse would have called** — `_onWorkflowDoneClicked`,
`_commitWorkflowChoice`, `_onWorkflowRangeSelected` — and never through `WorkflowRuntime.run_step`.
A second, unreviewed way to drive the runtime is exactly what a guided-only runtime exists to
prevent, and each of the three shortcuts loses something: `_onWorkflowDoneClicked` also runs
`_interactionManager.cleanup()`; `_onWorkflowRangeSelected` also runs `_commitThresholdToSegment`
(the segment write later steps depend on) and `_clearThresholdPreview`; and the scalar slider,
segment-name picker and multi-choice form each drive the **extension's own** control first so its
connected handler fires.

**`grammar.py` is a mirror of the panel's render branch and must be changed with it.**
`_family_for_state` takes `_renderWorkflowChoices`' branches in the panel's order, not alphabetically
— a segments-table step also carries a `node_class`, a range step also carries a `parameter_name`, so
only the panel's order lands on the control the user is looking at. And the choice value is
**what the button would send, not what the artifact declares**: the render loop coerces a Yes/No
*label* to `True`/`False` regardless of the declared value, so the panel state's `"true"` string and
PedicleScrewPlanner `cb_step_14`'s `"done"` both leave as booleans. Reading `choices[i]["value"]`
straight out of the state would make speaking and clicking disagree, and on a repeat block the string
never equals the boolean `exit_value`, so the loop could not exit.

**A positional pick is matched as a WHOLE utterance, never by finding an ordinal in a sentence.**
This is the single most dangerous path in the feature and it took two attempts to get right. The
ordinal branch is reached exactly when label matching has failed — which is the state ordinary
conversation is in — so "just a second" selected option two, and on the orbital step option two is
the other side of the head. Token filtering does not rescue the loose form: "just a second" and "that
was the last one" both survive a stopword filter and both contain a perfectly good ordinal. So
`_ordinal_index` is a lookup against an enumerated phrase table ("the first one", "option two", "the
last one", …) and nothing else. Nothing is lost — every option's label is read aloud in the prompt,
so saying the label is always available and always safer.

Two scoring rules underneath it. `match_score` scores over a small cross product of spellings —
verbatim, carrier words removed, numerals spelled out, number words digitised — because "the blue one
please" only reaches its label once the filler is gone, and "fragment one" only beats "Fragment 2"
once the numeral forms line up. And `_match_score_one` **takes the max of its heuristics** rather than
returning from the first that fires: token overlap is the weakest signal and fires most often, so an
early return there hid a much stronger character-level match.

**An idle hot microphone does not talk to the router.** With no workflow running there is no closed
vocabulary to match against, so every sentence would become a routing LLM call and, on a non-match
under `GUIDED_ONLY_MODE`, a modal refusal. A spoken request must open like one ("plan …", "start …")
and be at least three words; everything else is reported and dropped.

**Nothing the microphone hears is written to disk by default.** `VOICE_LOG_TRANSCRIPTS` is False, and
that is a privacy decision rather than a performance one: run folders are copied, shared and attached
to papers, and most of what an always-on theatre microphone transcribes is conversation about a
patient. The ASR artifact and `role_trace.json` both record durations, byte counts, detected language
and the resolved **action** — enough to evidence what the feature did — and withhold the utterance.
Audio bytes are never persisted at all. Flip the constant for an evaluation that needs the text.

**A failure streak stops the session.** A wrong region, a bad key or a model id that does not exist
there fails *every* utterance identically, and the status line it writes lives in a collapsed group —
so the symptom would be a microphone that looks alive and never acts. Three consecutive failures stop
listening and raise a dialog naming the three settings to check.

**Two tiers, and the second is only for the uncertain, not for the empty.** A sentence that matched
*nothing* is far more likely to be conversation than a paraphrase, so sending it to a model mostly
buys a confident-sounding wrong answer. An *ambiguous* result does not go to the model either — two
options fitting equally well is a question for the surgeon, not a coin flip delegated to a second
opinion. The fallback (`Resources/Prompts/voice_command_prompt.md`, one small call over the low-level
request path like `WorkflowRouter._call`, so it writes no `conversation_history`) is offered the
step's options as the only candidates and must return an **index** — the value that reaches the
runtime is read out of the grammar by that index, so the model can rename an option but never
introduce one. The tiers run on **different threads**, which is why `resolve_llm` exists beside
`resolve`: tier 1 is pure computation and belongs beside the panel it reads, tier 2 is an HTTP round
trip that would freeze Slicer there, and its answer is re-checked against the live `current_step`
before it is applied because the workflow can move on while the model is answering.

**Three fences, and they are not interchangeable.** `_guidedSessionEpoch` (captured per *utterance*,
not at listen time, so a sentence spoken after one workflow ends and another begins belongs to the
one it was spoken in) retires work against an exited workflow. `_voiceSessionSeq` is a **microphone**
session token: `MicListener.stop()` emits a final `stopped` state that lands in `_streamQueue` and is
handled up to 50 ms later, by which time the user may have clicked the button back on — without the
token that stale event tears down the session that just started, and the mic appears to refuse to
stay on. And `_voiceHandlingTranscript` is a **re-entrancy** guard: `_drainStreamQueue` pumps the Qt
event loop, and so does applying a command (`_runWorkflowStepDirect` executes template code), so a
second utterance arriving mid-dispatch would be handled *inside* the first and dispatch the step
twice. It is parked and replayed at top level instead.

**Speech is announced once per step OCCURRENCE, not per repaint.** `_updateWorkflowPanel` runs
several times per opening and a repeat block re-visits the same step id, so `_voiceAnnounceKey` uses
`(workflow_id, step_id, len(completed_instances), family, status)` — the same key shape the sole-node
auto-select uses, for the same reason. Automated steps are never spoken (they are dispatched and gone
before a sentence could finish), and a node-pick step that is about to auto-answer itself is
deliberately silent — the prompt would be answered by the runtime before the user finished hearing it.

**The API.** `qwen3-asr-flash` and `qwen3-tts-flash` over DashScope's *native* multimodal-generation
endpoint, via `urllib` — not `httpx`, which is in `requirements.txt` but imported by no project code
and unproven inside Slicer's Python. The OpenAI-compatible mode **does not exist for ASR in the US
region**, and model ids are region-suffixed (`qwen3-asr-flash-us`), so the region selector is not
cosmetic: getting it wrong is a 404 that reads like a bad key. Speech-out derives its endpoint from
the speech-in region so one key cannot be paired with a mismatched host. The speech key is its own
QSettings entry — the agent's `apiKey` is only a DashScope key when the user happens to have selected
provider "Qwen", and even then it points at the *chat* endpoint. `voiceRegion` is applied **before**
the other voice settings in `_loadVoiceSettings`, because its change handler rewrites the model list
and the endpoint — the same ordering trap `loadSettings` already has with provider/baseUrl.

`sounddevice` is the only binary wheel the project adds, installed at runtime on first listen and
degrading to a named reason rather than an ImportError; `audio.py` imports cleanly with no backend
present. TTS audio comes back as a **URL**, not inline, and there is no documented way to request a
container, so the bytes are sniffed and `SpeechResult.audio_format` is reported — WAV decodes with
the stdlib `wave` module, anything else needs a codec that is deliberately never auto-installed.

Captured audio is **never persisted**: the artifact writers record duration and byte counts, because
run folders are copied, shared and analysed and patient-room speech must not travel with them.

### Revising a step's template at runtime (the ✍ button)

**A generated step can pass every check and still be wrong, and the only detector is a person.**
It runs, raises nothing, and reconstructs the wrong orbit, shows the curve in the wrong view, or
leaves a node the next step cannot find. Self-correction cannot see it (it fires on a raised error),
static validation cannot see it (the code is valid), and the api-probe cannot see it (the method
exists). So the trigger is a **button next to the microphone**: step to the step with ◀, press ✍,
say what should have happened, press Send. `SlicerAIAgentLib/TemplateReviser.py` is the Qt-free
core and `app/widget_revise.py` the Qt half, splitting the same way `BaselineRunner` /
`widget_baseline` do — and for the same reason, `scripts/check_template_revision.py`.

This **replaced** the "Function-level errors" box and its `Repair Generated CLI` button. That path
took free-form sentences in the generator panel, asked an LLM which of 27 steps each one meant
(`_map_description_to_step`), and repaired blind; the fix could not be tried without re-running the
whole procedure. Pointing at the step instead removes the classification entirely — and, because
the step is *open*, lets the revision be given things a whole-package repair has no access to: the
code that was actually dispatched (template filled with this run's real values), what it printed,
the live scene, the answers the user already gave, and the previous revisions of the same step. The
deleted button was also the only trigger of the **live-execution validation gate**
(`live_validate_templates` → `repair_live_failures`), which is therefore gone too; generated
packages are now validated statically only, and `manifest["live_validation"]` is no longer written.

**The TEMPLATE is rewritten, not the filled code — which is what makes this stronger than the
write-back it sits beside.** `_persistGeneratedTemplateRepair` persists a runtime self-correction by
escaping every brace and saving the *filled* code, so it must refuse any template carrying a
placeholder: freezing this run's `{side}` into the package would make every later run reconstruct
whichever side this one happened to pick. A revision edits the template source, so it has no such
limit. What replaces that guard is **placeholder closure**: the revised template may drop a
placeholder and may re-default one it already has, but may not introduce a name the original lacked.
The original demonstrably fills at dispatch, so its placeholder set *is* what the runtime can supply
here; a new bare `{name}` raises `KeyError` inside the loader, and the symptom is a step that
silently never executes rather than an error anyone reads.

Four checks decide whether a rewrite may be installed, and three of them exist because the failure is
otherwise invisible:

- **Placeholder closure**, above — measured over `fillable_placeholder_names()`, not over a brace
  scan. A raw scan also matches every **f-string interpolation** (`print(f"failed: {exc}")`), which
  the loader is right to leave alone because it sits inside a real string literal; counting those as
  placeholders would refuse any revision that adds an f-string, and f-strings are how every generated
  template reports an error. Note the defaulted form `{name: default}` is *not* an escape hatch: it
  is the same six characters as the dict literal `{key: 1}`, which the filler also replaces with the
  default (`d = {key: 1}` fills to `d = 1`). Refusing both readings with one message is the only rule
  that is not a coin flip — a name nothing can fill is a constant in disguise anyway.
- **The filler, run for real.** `unfillable_placeholders()` calls `templates._fill_template` itself
  with sample values and looks for `{name}` survivors, rather than re-deriving its rules: a copy would
  have to reproduce both the mask regex *and* its containment test (the filler checks only where a
  placeholder BEGINS, over a buffer in which every `{{` has been swapped for a longer sentinel), and a
  copy that drifted would answer confidently about a different string than the loader processes. A
  survivor is then split by asking **Python**: inside a real STRING token it is an interpolation,
  outside one it is trapped — by an *unbalanced* apostrophe, typically one in a prose comment, which
  opens a mask span running to the next quote anywhere in the file. Counting apostrophes would have
  been a proxy that rejects `node.SetName('Result')`, i.e. most correct answers.
- **Syntax and CodeValidator**, both on a `sample_fill()`ed copy — a template is not valid Python
  until its placeholders are substituted.
- **Scope.** `parse_reply` resolves the model's paths against the step's own template list and drops
  anything else, so a model that decides to also fix step 14 cannot. A JSON reply whose `templates`
  key is misspelled is a *correctable* error, never a fall-through to the single-block shape: that
  shape would install the JSON document itself as the template, and nothing downstream would object —
  a JSON object is a valid Python dict-literal expression, so it parses, imports nothing, and has no
  placeholders to close. The step would then raise nothing, print nothing and do nothing, i.e. the one
  feature whose job is to fix silently-wrong steps would have manufactured one.

**The reply must be FENCED, and that is a correctness constraint rather than a formatting
preference.** `llm_client._runToolLoop` ends a round only when `_extractCode` finds a fenced block.
A prompt asking for bare JSON therefore produces a loop that can never accept a correct answer: it
burns all `TOOL_ROUNDS`, gets a hard-coded "you did not produce code" nudge each time, then a forced
final call demanding an `agent_plan` + `python` pair — which `parse_reply` reports as ambiguous, and
the retry ladder repeats the whole thing. So the prompt mandates a single ` ```json ` block and says
why, and `check_template_revision.py` asserts both.

A rejection is fed back verbatim and the agent gets `MAX_ROUNDS` (3) attempts; the checks are
deterministic, so the retry message is evidence rather than an opinion. The call is
`chatWithToolsIsolated` with the built-in search tools and the generated-CLI schemas **stripped by
identity** — the same shape self-correction uses, so a revision can read the extension's source
through `ext:` before it writes a call but cannot dispatch a workflow step while deciding.

**The original is kept, and the promise is checked rather than assumed.** `versions/revision_<ts>/`
is the package BEFORE the write — the direction `runtime_fix_<ts>` uses, and deliberately not
`repair_NNN`, which archives the *result*; putting a pre-image under that prefix would make
`versions/` mean two opposite things. `cli_artifacts.snapshot_package_version` has no logger and
returns `None` on failure, so `apply_revision` refuses to write at all when the snapshot did not
land: "the original is saved" must not be a claim resting on a call whose result was never read. The
round's request, reply, messages, per-template before/after and unified diff go to
`debug/revision_<ts>/`, every revision is indexed in `debug/revisions.json` (under `debug/`, which
survives a regeneration, not at the package root, which is wiped by one), and the run folder gets its
own copy under `<step>/revision_<n>/` so a run stays self-contained.

Three traps that cost a bug each:

- **The header strip must not be greedy.** Each rewrite prepends `# [revised] …` naming its backup,
  and the model is shown the template *with* that header, so it reproduces one. Stripping "the
  header and every comment line after it" ate the `# precondition:begin … precondition:end` block on
  the second revision of a step — the runtime's only marker for firing the extension's `enter()`,
  whose absence breaks every later interactive step and raises nothing. The continuation lines are
  enumerated instead.
- **The header is validated too, because it is written after validation.** It carries the surgeon's
  own sentence into a comment at the top of an executable template, so "the model shouldn't be on
  the left orbit" would put an unbalanced apostrophe above the code and swallow the placeholder
  below — the exact defect the validator refuses in the model's output, entering through the door
  beside it. `_header_safe` strips quote characters, and `apply_revision` re-measures the assembled
  file against the body and refuses to write that template if the header trapped anything.
- **The loader cache is NOT invalidated.** Template *content* is opened fresh on every dispatch, so
  the next ▷ already picks the rewrite up; and `invalidate_cache()` mid-run re-reads every manifest
  and drops any package failing the status gate — possibly the one the surgeon is standing in.
- **Eligibility is memoised per (package, step).** It reads two JSON files and is consulted from
  `_guidedWorkflowOwnsInput`, which every `_setSendEnabled` calls — roughly eight reads per repaint
  while armed. Safe to cache because a revision rewrites template content, never the generator's
  step→file mapping; the template *text* is re-read on every run and is not cached.

**Shared seams with the baseline harness, copied rather than approximated**: the mixin sits ahead of
`WidgetSendMixin` in the MRO and overrides Send with one `if not engaged: super()` guard;
`_guidedWorkflowOwnsInput` learns about it or the guided workflow keeps the box switched off and the
mode looks dead; intent (`_reviseActive`) and engagement (`_reviseEngaged`) stay two things, and busy
is always engaged so the row cannot vanish under a running revision; the debug write context moves
for the duration and is handed back on every exit path. The two modes are **mutually exclusive in
both directions** — each toggle disengages the other and refuses while the other is busy, and each
one's Send-restore is guarded on the other's flag. One-directional exclusivity is not enough and
fails silently: with both armed, the panel repaints Send purple (revise's sync runs last) while
`onSendButtonClicked` still routes to baseline (which precedes revise in the MRO), so a button
reading "Revise step" starts a baseline whose first act is a rewind that deletes every downstream
node. ✍ is also disabled while a baseline runs, because that run has repointed `_currentLogDir` and
`_currentRunManifest` at its own folder and a revision started underneath it would file its record
against the wrong run. Exit and the three replay controls refuse while a revision is in flight, and
the reply carries `_guidedSessionEpoch` so one that lands after Exit is dropped instead of writing a
template for a procedure nobody is in. Exit tears the mode down **before** `_prepareCleanRuntime`,
which clears `_reviseActive` as a raw attribute write — after that the self-healing repaint path
finds nothing to heal and the status row is left parked above the prompt box.

**The revised step is re-run automatically, and the scene is always put back first.** A step can be
revised from three states and only one of them has a committed checkpoint, so there are three ways in:
*scrubbed back to it* (`preview_index` set) and *completed and left behind* (its last checkpoint —
last, because a repeat block re-visits a step) both go through `_rerunFromCheckpoint`; **standing in
it** — an interactive step waiting for Done, or one that just ran — has no committed checkpoint,
because those are recorded on completion. That case is what `rollback_failed_step` is for: it
restores from the *pending* checkpoint, the scene view and node set captured when the step opened, and
deliberately keeps it so the retry starts from the identical state. Named for the failure it was
written for, but this is the same situation — an attempt being thrown away and tried again. Without
it, revising the step you are standing in dead-ended in "no scene state to restore" with ▷ greyed out,
which is the state a real run landed in.

Never re-dispatch on top of the existing scene: a PRE template that creates a node would create a
second one, after which the POST template's "last node of this class" picks the wrong one. That is
silently wrong, which is worse than losing an in-progress manual adjustment on a step the user is
re-running anyway. The re-run is deferred with `QTimer.singleShot(0, …)` because it is reached from
inside `_drainStreamQueue` and executing template code pumps the Qt event loop — the 50 ms drain timer
would otherwise fire again and handle a second event inside this one. `_rerunFromCheckpoint`'s own
confirmation still stands: it asks before a rewind that would delete nodes the workflow did not create.

**A template the agent returns verbatim is not written.** It is asked for the complete file for every
template the step owns, so it routinely echoes back the one it did not touch; writing that would stamp
a header on it and report an untouched file as revised (a real run produced exactly that, with an
"identical to the original" warning attached). `apply_revision` compares bodies with both headers
stripped, skips the unchanged ones, and says so — and when every template comes back unchanged that is
an error naming them, not a silent success.

Three things about the button itself. ✍ is **text**, not a `:/Icons/` resource: `qt.QIcon` on an
unregistered path returns a NULL icon rather than raising, which renders as an empty button — the
same reason the baseline toggle is a bare "⚖". It carries U+FE0E (variation selector-15) so Windows
font fallback does not reach Segoe UI Emoji and draw a colour cartoon hand among monochrome glyphs.
And it is **visible from panel build**, disabled with the reason in its tooltip, because
`_updateReviseControls` runs only on a workflow-panel repaint: a button that starts hidden did not
exist at all until a procedure started, which reads as a missing feature rather than an unavailable
one.

Its stylesheet needs an explicit `:disabled` rule, and that is not decoration: a stylesheet `color`
REPLACES the widget's palette for every state, so a red glyph stays vivid red while the button is
unclickable — and this button spends most of its life disabled (no procedure running, a step with no
template, a baseline or a revision in flight).

### Entry Point and Module Structure

- `SlicerAIAgent.py` (~3600 lines) — Contains three Slicer-standard classes plus the bulk of runtime logic:
  - `SlicerAIAgent` — Module metadata.
  - `SlicerAIAgentWidget` — Qt UI, streaming queue, tool loop orchestration, execution dispatch, self-correction, and Extension CLI generator UI.
  - `SlicerAIAgentLogic` — LLM client management, tool dispatch (`_executeTool`), scene context building, code execution, scene snapshot/verification, vector index warmup, and the background streaming entry point.
- `SlicerAIAgentLib/` — Core library package with all supporting modules.
- `Resources/` — UI files, icons, system prompt, knowledge base, FAISS vector index, and generated extension CLI tools.
  - `Resources/Skills/slicer-skill-full/` — Git submodule containing the full Slicer knowledge base (source, extensions, dependencies, project-week docs). Gitignored from the main repo; clone with `--recursive` or init manually.
  - `Resources/Code_RAG/` — FAISS vector index + ONNX embedding model (`jina-embeddings-v2-base-code` under `models/`). Generated by `scripts/build_rag.py`.
  - `Resources/extension_CLI/` — Per-extension directories with `manifest.json`, `code_generators.json`, `prompt_fragment.md`, and `templates/*.tpl` files. Template syntax uses `{placeholder}` variables substituted at runtime.

### Agent Pipeline (runtime flow)

1. **User input** → `SlicerAIAgentWidget.onSendButtonClicked()` → background thread via `_backgroundStream()`.
2. **Pre-Retrieval** — `LLMClient.decomposeQuery()` breaks complex prompts into sub-queries; `VectorRetriever` searches FAISS index (`SkillIndexer.py`).
3. **Tool-Calling Loop** — LLM has **four** built-in tools (`Grep`, `ReadFile`, `VectorSearch` from `get_skill_tools()`, plus `GetNodeProperties` from `get_scene_tools()`) alongside the dynamically loaded extension CLI tools. `SkillToolExecutor` dispatches via ripgrep/tree-sitter. Multiple tool calls execute in parallel via `ThreadPoolExecutor`. `SearchSymbol` is *implemented* (`skill_tools/symbols.py`, dispatchable, memoized) but **not registered in any tool schema**, so the model is never offered it — confirmed in `messages_sent.json` of an online-only baseline, which lists exactly four. `GenerateSegmentationCode` is likewise unregistered. Either wire them into `get_skill_tools()` or treat them as dead code; do not describe them as available.
4. **Plan + Code Generation** — LLM outputs `agent_plan` JSON (with `expected_scene_change` checks) then a Python code block. Tool loop terminates when executable code is detected.
5. **Validation** — `CodeValidator` performs AST-based security checks (blocked modules/functions, destructive op detection).
6. **Execution** — `SafeExecutor.execute()` runs code in Slicer's `__main__` namespace via `qt.QTimer.singleShot()` on the Qt main thread. Scene rollback on failure.
7. **Scene Verification** — If `agent_plan` includes `expected_scene_change`, `SlicerAIAgentLogic.verifySceneAgainstPlan()` compares before/after scene snapshots and triggers self-correction if expectations aren't met.
8. **Self-Correction** — Isolated retry loop (up to 5 attempts) via `chatWithToolsIsolated()`, which does not pollute user conversation history.

### Threading Model

HTTP I/O runs in a background `threading.Thread`. Events are marshaled to Qt main thread via a `queue.Queue` (`_streamQueue`) polled every 50ms by a `QTimer`. All MRML scene access and UI updates must happen on the Qt main thread. Vector index warmup also runs in a background thread on startup.

### Prompt & Context Management

**Every prompt lives in `Resources/Prompts/*.md`, never as a Python string.** A prompt is an
experimental variable of this system, so it must be editable, diffable and citable without touching
code. `SlicerAIAgentLib/PromptLibrary.py` is the only module that reads that directory (mtime-aware
cache, so an edit applies on the next call; `{{PLACEHOLDER}}` substitution via `render()`). The only
prompt text left in Python is a one-line fallback per loader, for surviving a missing file.
`Resources/Prompts/README.md` is the index. Five prompt paths, each sized to its job:

**1. Opening turn → `workflow_router_prompt.md` (~6 KB, one tool-free call).**
Once a generated-CLI workflow starts, every step is dispatched by `WorkflowRuntime` — the LLM is out
of the loop. So the only decision it makes on turn 1 is *which workflow the request means*. Making
that decision through the full agent turn cost **140,611 characters** of system prompt (33 KB manual
+ 72 KB retrieval snippets, including whole markdown files + 41 KB of CLI fragments + scene) to emit
one tool call. `WorkflowRouter` does it with ~6,200: the router prompt plus a catalog built from the
workflow graphs (name, step count, seven step descriptions **spread evenly across** the procedure —
the head names the inputs, the tail names the goal, which is what separates nine procedures that all
open with the same Segment Editor boilerplate). Temperature 0, thinking off, no tools, no retrieval,
no `conversation_history` write. On a match it calls `start_for_extension()` + `_runWorkflowStepDirect()`.
Unknown name, confidence < `DEFAULT_CONFIDENCE_THRESHOLD` (0.6), `null`, a malformed reply or an API
failure all return False. Under `GUIDED_ONLY_MODE` (see "Guided-only runtime") that False is a
**refusal**, not a fall-through — so the router prompt says so in those words: telling the model that
a `null` is handled by a coding agent that no longer exists is a false statement about the
consequence of its own decision, which is exactly the kind of thing that biases it toward
over-matching. It is told instead that a refusal is the intended outcome for an uncovered request and
that its named near miss is shown to the user. `ROUTER_ENABLED = False` restores the pre-router
behaviour in one line (and under guided-only means every request is refused, which the dialog says).

**2. General Slicer requests → `system_prompt.md`, unchanged.** Reached only with
`GUIDED_ONLY_MODE = False`; self-correction (path 3) uses the same assembly and is always live. `_buildSystemPrompt()` assembles it
from the template + platform info + role protocol + output format + `## RELEVANT KNOWLEDGE BASE
SNIPPETS` (dense pre-retrieval) + `## CURRENT SLICER SCENE` + the extension CLI sections +
`## ACTIVE WORKFLOW`. Extension source is searchable via the `ext:` prefix (`ext:VoxTell/`).

**3. Self-correction → deliberately long.** Repair needs the whole history: the full system prompt,
the original user prompt, the prior tool trajectory, the failed plan + code, the error, live
`ApiSanityChecker` attribute evidence, core-UI control evidence, the workflow state, and the search
tools. Kept as-is except for one fix: a repair inside a running workflow already strips the generated
CLI tool *schemas* from its tool list (`_filtered_repair_tools`), so `suppress_cli_tool_fragments`
now also strips their *descriptions* — ~42 KB per correction turn spent describing tools that are not
there, and inviting a call that arrives as text and parses to no code. The `ext:` source paths stay:
searching the extension's own source is exactly what a repair needs. Two independent ablation flags:

| flag | CLI tool fragments | `ext:` source paths | cookbook block | used by |
|---|---|---|---|---|
| *(none)* | ✅ | ✅ | ✅ | normal turns |
| `suppress_cli_tool_fragments` | ❌ | ✅ | ❌ | self-correction during a workflow |
| `suppress_extension_cli` | ❌ | ❌ | ❌ | online-only baseline |

**4. A step that RAN and misbehaved → `template_revision_prompt.md`.** The counterpart to path 3,
and the division is what each one can be given: self-correction repairs the *filled code* of a step
that raised, so it needs the whole trajectory; a revision rewrites the *template* of a step that did
not raise, so it is scoped to one step and carries that step's template source, its dispatched code,
its output, the live scene and the user's own description. It is offered the same search tools with
the CLI schemas stripped, and the validator's blocked lists are rendered into the prompt rather than
restated in it — a prompt describing a blocked list that has since changed teaches a rule the
executor does not enforce. See "Revising a step's template at runtime".

**5. Baselines → see "Baseline prompt & context" below.**

### Dual API Support

`LLMClient` handles both OpenAI-compatible APIs and native Anthropic Messages API:
- OpenAI-compatible: Kimi, DeepSeek, OpenAI, Qwen — standard chat completions with streaming.
- Anthropic native: Claude — message conversion (`_convertMessagesForClaude`, `_convertToolsForClaude`), response normalization (`_normalizeClaudeResponse`), extended thinking support.

### Scene Verification System

`SlicerAIAgentLogic` includes a scene snapshot/verification subsystem:
- `buildSceneSnapshot()` captures all MRML node states before execution.
- `verifySceneAgainstPlan()` checks `expected_scene_change` entries from the agent plan.
- Supported check types: `node_exists`, `node_count_delta`, `node_modified`, `node_has_display`, `node_has_content`, `node_name_matches`, `layout_changed`, `selection_changed`, `module_entered`, `property_true`, `not_checked`.

### Key Library Modules (`SlicerAIAgentLib/`)

| Module | Role |
|--------|------|
| `LLMClient.py` | HTTP client for OpenAI-compatible and Anthropic native APIs. Streaming, tool calling, token tracking, query decomposition, history compression, system prompt assembly. |
| `SkillTools.py` | Tool executor — ripgrep search (`_grep_rg_aggregate`), tree-sitter AST slicing (`_slice_by_ast_boundary`), smart file reading (`_readfile` with markdown heading slices and test-method slices), vector search. |
| `SkillIndexer.py` | Dense retrieval: chunking (AST-aware for Python/C++, heading-based for Markdown), ONNX embedding (jina-embeddings-v2-base-code), FAISS indexing, incremental rebuild. |
| `ExtensionCLIAnalyzer.py` | 11-stage LLM pipeline (8 original + 3 interactive stages 4.5–4.9) for analyzing Slicer extensions and generating tool schemas, code templates, and workflow graphs. |
| `ExtensionCLILoader.py` | Auto-discovery and dynamic loading of extension CLI tools from `Resources/extension_CLI/*/`. Includes `dispatch_workflow_step()` for interactive workflows. |
| `SafeExecutor.py` | Sandboxed execution in Slicer's `__main__` namespace, stdout/stderr capture, VTK error interception (`vtkOutputWindow` swap), timeout, scene rollback. |
| `SceneTools.py` | Structured MRML scene introspection (`buildSceneSummary`, `getNodeProperties`). |
| `CodeValidator.py` | AST-based security validation via `CodeAnalysisVisitor`: blocked modules/functions, allowed modules, destructive operation detection. |
| `ConversationStore.py` | Conversation history persistence (in-memory + Slicer settings + JSON export). |
| `SlicerCodeTemplates.py` | Reusable code patterns for common Slicer operations. |
| `InteractionManager.py` | Low-level Slicer 3D interaction: markup node creation, placement mode entry/exit, VTK observer management with debounce timers. |
| `WorkflowOrchestrator.py` | Runtime state machine for guided interactive workflows: step execution, interaction completion, workflow cancellation, prompt fragment generation. |
| `PromptLibrary.py` | The only reader of `Resources/Prompts/`. mtime-aware cache, `{{PLACEHOLDER}}` rendering, per-file fallback. |
| `RunLog.py` | Run-folder naming (`<stamp>_<condition>_<procedure>[_<step>][_a<n>]`), fail-soft artifact writers, `RunManifest`. |
| `TemplateReviser.py` | The ✍ Revise core, Qt-free: which template files a step owns, whether a rewritten one may be installed (placeholder closure, the filler's string mask, syntax, CodeValidator), reply parsing, and the snapshot-before-write apply/restore. |
| `WorkflowRouter.py` | Fast first-turn router: one tool-free call over a compact workflow catalog, deciding which guided workflow a request means (or none). |
| `voice/` | Voice control, Qt-free half: `audio` (always-on capture with energy VAD, playback), `asr_client` / `tts_client` (qwen3-asr-flash / qwen3-tts-flash over DashScope), `grammar` (the step reduced to the utterances it accepts), `commands` (transcript → one action). The Qt half is `app/widget_voice.py`. |

### Extension CLI Pipeline

`ExtensionCLIAnalyzer.py` analyzes third-party Slicer extension source code via LLM and generates tool schemas + code templates under `Resources/extension_CLI/`. The Widget includes a generator UI (`_setupExtensionCLIGenerator`) for analyzing and generating CLI tools (in parallel, one tab per extension), deleting them, and editing per-step clinical instructions. It no longer offers a repair action: a package that fails validation is auto-revised by `_autoReviseCli` on the spot, and a step that validates but *behaves* wrongly is fixed at runtime by ✍ Revise, on the step in front of the user. At runtime, `ExtensionCLILoader.py` discovers and loads these as additional LLM tools. Extension source code is exposed to the LLM via the `ext:` path prefix.

### Where a user_choice's answer goes

**An extension keeps a GUI setting in one of two places, and both are binding
channels.** The long-standing one is the **parameter node** —
`parameterNode.SetParameter("role", …)`, found by
`parameter_metadata._extract_parameter_roles_from_source`, surfaced as
`choice_bindings[step]` and applied by
`choice_helpers._build_choice_parameter_update_code`. The other is the **control
itself**: the handler reads it at click time
(`self.logic.segmentOrbits(self._currentSide())`, where `_currentSide` returns
`"right" if self.sideComboBox.currentIndex == 0 else "left"`). Such a setting has no
parameter role, so for those extensions the whole channel was empty — the answer was
recorded in `_workflow_choices` and reached nothing, and the run proceeded on
whatever the control's factory default was. `scan._scan_value_controls` recovers the
second channel from the widget class's own AST: the control's **items**, the
**reader** that maps its state to a value (restricted to a ternary/if-else return
over a literal comparison — anything else yields no map and the item text is the
value), and the **consumers** `(method, arg_index)` that pass the reader's result
into a logic call. `_widget_state_choice_binding` names the parameter that
`arg_index` fills against the AST signature, so the result is the same
`choice_bindings` shape the parameter-node branch produces, plus
`bound_choice_parameters[method]` for the template layer.

Three facts about that path are load-bearing, because each fails *silently*:

- **The options are the control's own, not the cookbook's paraphrase**
  (`stage4._reconcile_value_control_choices`, gated on a scanned item list so
  checkboxes and Yes/No `branch_op`s are untouched). The orbital panel asks for the
  fractured *side* but offers "Red box" / "Blue box" — deliberately, because the two
  coloured boxes are drawn over the orbits and picking a colour is unambiguous where
  "left" is not. A generated panel offering Left/Right asks a different question from
  the one the surgeon is looking at.
- **The index→value map inverts without a symptom.** That control's item 0 is the RED
  box, which is the patient's **right** orbit, so an authored `[Left=left,
  Right=right]` list selects the healthy side. The run completes, segments (with the
  models swapped — fracture V-Net on the healthy half), reconstructs and reports
  success, on the wrong orbit. Only the extension's own reader knows the mapping.
- **A `.ui` file is evidence only if the widget loads it** (`scan._scan_ui_is_live`,
  vacuously true when there is no `.ui` at all — otherwise a wizard module, whose
  controls live on page classes, would enter the demotion path). Slicer's module
  template ships one, and a module that later moved to building its panel in code
  keeps the file: it then describes a GUI that does not exist while still parsing and
  still carrying matching widget names. Orbital's stale file declares `sideComboBox`
  with `[Left-sided fracture, Right-sided fracture]` — the opposite index order from
  the real control — and names three node selectors (`inputSelector`,
  `boundingBoxSelector`, `fullBoneSelector`) that the widget does not have.
  `_scan_widget_attr_universe` + `stage4._drop_unloaded_ui_widget_class` discard a Qt
  class that exists only in an unloaded file, returning the step to inference from
  `node_class`.

**The generator could not express the binding, so it invented one.** Rule "Do NOT use
curly brace template placeholders" plus a blanket unresolved-placeholder error (which
permitted only `{vol_lookup}`) left a required argument with no legal source, and the
model reached for `side = logic._side` — the attribute the method *assigns from that
very argument*, so always unset on the first run. The prompt now requires the
placeholder, and the validators permit it **and require it** — a template calling the
method without it is a blocking error, since the argument must then have come from
somewhere else.

**Placeholder closure is enforced in TWO independent places**, and fixing one is not
fixing it: `validation_contracts` checks each template as it is validated, and
`contract_audit._final_package_audit` re-checks the shipped artifacts as the
authoritative final gate (deliberately, so a template rewritten by verify_repair or
revision cannot ship on a stale verdict). Carving the rule out of only the first one
produces a package whose every step validates and which is then stamped
`validation_failed` by the second — and `status` is what `extension_cli_loader/cache.py`
and therefore `WorkflowRouter.build_extension_catalog()` gate on, so the whole
procedure silently disappears from the router's catalog and every request for it is
refused. Hence `_bound_choice_placeholders(gen)` lives once, in `validation_semantics`,
and both gates call it.
`validation_semantics._fill_remaining_placeholders` (now an instance method, so every
call site benefits) fills such a placeholder from a real option rather than `""`;
otherwise `_stage9_validate` would syntax- and security-check `segmentOrbits("")`,
which the extension rejects by design, read that as a broken template, and hand a
correct one to the repair ladder.

At runtime the answer travels **twice, deliberately**. `_build_format_kwargs` already
merges recorded choices into the fill kwargs, so `{side}` resolves to the answer —
that is what makes the step correct. `_build_widget_state_choice_materialization_code`
additionally drives the extension's own control to the matching option (resolved
`.ui.<name>` → `self.<name>` → objectName, mirroring the generator's
`_resolve_qt_control_lines`), so the panel shows what the user chose, any connected
handler fires, and a later step that reads the control agrees. They cannot disagree —
both resolve the same recorded value through the same scanned option list. A missing
*item* raises (the installed extension differs from the analysed source, so the
recorded value may address a different option than the user saw); a missing widget
only warns, since the template's own binding still carries the value.

**A range choice reaches its consumer by NAME, and the two names are chosen
independently.** A `user_choice` step with `value_kind == "range"` records `[lo, hi]`
under the `parameter_name` the decomposition invented; the step that spends it asks
for a placeholder. Those never come from the same place: the Segment Editor session
driver builds its Threshold-apply block from the EFFECT alone
(`module_sessions._effect_operation_block`), so all it can write is the generic
`{threshold_min: 150.0}` / `{threshold_max: 3000.0}`. `_build_format_kwargs` is the
bridge, and it must reduce the recorded name to the concept the driver used.

The marker word can sit **anywhere** in that name -- `thresholdRange`,
`referenceThresholdRange`, `threshold_range_reference` are all names the
decomposition produces for the same thing -- so `_range_alias_words` drops it
wherever it appears and offers every remaining word as a concept, rather than
stripping a trailing marker and taking the stem's last word. That earlier rule
covered exactly the marker-last spellings and silently covered nothing else:
LongBoneFractureReduction's `threshold_range_reference` has the marker in the
middle, so no alias was emitted at all and both its Apply steps thresholded at the
placeholder's hard-coded 150-3000 -- overwriting the segment the range step had
just committed. **Nothing raises.** The user sets the slider, sees the mask they
asked for, and meets a different one two steps later, after Islands has already
been pointed at it. The aliases OVERWRITE so the most-recently-recorded range wins,
which is what keeps consecutive threshold cycles (reference, then moving) correct
and what makes a replay truncation put the earlier one back.
`scripts/check_range_choice_fill.py` holds this over every shipped package: for each
`*_min`/`*_max` placeholder, the nearest preceding range choice must fill it, proven
by filling the real template with the real loader.

### A node class is a lookup key, not prose

`node_class` goes straight to `getNodesByClass` and to `qMRMLSubjectHierarchyTreeView.nodeTypes`,
but it arrives from an LLM decomposition, which sometimes writes it decorated:
`"vtkMRMLVolumeNode (CT scalar volume)"` — a real class plus a helpful gloss. As a key
that matches nothing, and the symptom points away from the cause: the pick step's tree
comes up empty, and `WorkflowInputs` reports the scene as missing a CT the surgeon has
already loaded. It also inverts that module's fail-open promise — an unnameable demand
is not positive evidence, but it *is* a requirement no scene can satisfy, so under
`GUIDED_ONLY_MODE` the procedure becomes unreachable.

**A gate keyed on an exact class name must first ask whether that name is reachable.**
The sole-node auto-select (`_autoSelectableSoleNode`, gate F) refuses to commit unless
`node.GetClassName() == node_class`, so that it never chooses between siblings — a
labelmap is a `vtkMRMLScalarVolumeNode` subclass and must not auto-answer a
"source volume" step. Against an ABSTRACT class that comparison is not selective, it
is unsatisfiable: no node's `GetClassName()` is ever `vtkMRMLVolumeNode`, so the step
sat waiting for a click on the single candidate it already had. It also contradicted
the manual path, which accepts that node via `IsA` (`_nodeTreeValidCurrentNode`) — the
same node was valid or not depending on who selected it. The gate now runs only when
`_nodeClassIsInstantiable(node_class)`, answered from the scene's own registry
(`IsNodeClassRegistered`; a class is registered by handing the scene an instance, so
an abstract one never appears) and cached per class. Read-only deliberately: probing
with `CreateNodeByClass` answers the same question but `vtkMRMLScene::CreateNodeByClass`
dereferences its null result when a default node is registered for the class, so it can
segfault Slicer. Sibling protection is untouched — there the class is concrete.

The stage-4 allow-list is what should have caught it and is exactly what let it
through: `_stage4_semantic_context` built `allowed_node_classes` from each logic
parameter's **`type`**, which the logic-annotation prompt asks the model to fill with
"types/descriptions", and admitted anything passing `startswith("vtkMRML")`. The gloss
entered the allow-list, after which the `references unknown node_class` check
validated it against itself. Allow-lists derived from LLM prose have to be normalized
at the point of construction, or they authorize whatever contaminated them.

Both sides now reduce a decorated value to its class token — deterministic, since the
name has a fixed lexical shape: `stage4._normalized_node_class` (in the *normalizer*,
which runs before validation, so the repair costs no re-ask) and
`WorkflowRuntime.normalize_node_class`. The runtime half is what lets an already-shipped
package keep working; it warns and names the artifact so the package still gets
regenerated.

**There are TWO runtime readers of `node_class`, in the two mirrors this codebase
deliberately keeps** (`WorkflowRuntime._node_class_from_step_meta` and
`extension_cli_loader.choice_helpers._node_class_for_choice`, which already mirror
`_NONSPECIFIC_NODE_CLASSES` and the family predicates for the same reason). Normalizing
only the runtime one fixes what the panel *shows* and leaves what it *executes* broken:
the loader's copy is baked into emitted code as `IsA(<class>)` and
`GetNodesByClass(<class>)`, so the picked node resolves to None and the step fails into
self-correction — which then spends attempts rediscovering that the string is not a
class name. Every reader in both mirrors goes through a normalizer, including the
alias channel and the `parameterNodeWrapper` input guard.

### Interactive Workflow System

For extensions requiring user 3D interaction (drawing curves, positioning planes, placing fiducials), the system supports guided interactive workflows:

- **`InteractionManager.py`** — Low-level Slicer interaction: creates markup nodes, enters placement mode, manages VTK observers with debounce timers.
- **`WorkflowOrchestrator.py`** — Runtime state machine managing workflow steps (`WorkflowStep`, `WorkflowState`). Tracks progress across interactive and automated steps.
- **ExtensionCLIAnalyzer Stages 4.5–4.9** — Auto-detects interactive patterns in extension source (AST scan for markup nodes, observers, placement mode calls), classifies them into workflow phases via LLM, builds a workflow graph, and generates split templates (pre-interaction setup + post-interaction processing).
- **Widget workflow UI** — `_setupWorkflowUI()` adds a "Waiting for your interaction..." banner with Done/Cancel buttons. `_enterWorkflowWait()` / `_onWorkflowDoneClicked()` manage the wait-complete-advance cycle.
- **Manifest `workflow_type` field** — `"simple"` (existing behavior) vs `"interactive"` (new). Interactive extensions include `workflow.json` describing the step graph.
- **System prompt `INTERACTIVE WORKFLOWS` section** — Instructs the LLM on the step protocol (call tool → relay instructions → wait for user → advance).

### Workflow Replay Stepper

An in-memory, per-step history of a generated-CLI workflow run, driven by three buttons around the progress bar: **Back**, **Forward**, and **Run from here**.

- **`WorkflowRuntime.py`** — Records a `WorkflowCheckpoint` per completed step (and per loop continue/exit decision), holding the replay action/args, a `repeat_states` snapshot, the completed/choices prefix, the step's guidance text, `before_node_ids`/`created_node_ids`, the `layout_before`, and a full before-step `vtkMRMLSceneViewNode` (`sceneview_node_id`). **Back/Forward** recover the *full* scene state at a step without ever deleting a node: `_restore_to_view()` copies every stored node's properties onto its matching live node by ID (`_restore_scene_properties` — recovers baseline-node display like the loaded segmentation, transforms, slice/view nodes, colors), hides nodes that didn't exist yet (`_hide_nodes_after`), and restores the layout (`_set_layout`). Slicer's own `RestoreScene` is unusable here — `removeNodes=False` aborts when later nodes are present, and `removeNodes=True` deletes+recreates (which drops display nodes); the property-copy avoids both. The live state is snapshotted on first Back so Forward returns to it exactly; `preview_index` tracks position. **Run from here** commits via `rewind_to_checkpoint(preview_index)` → `_commit_node_state` (property-restore the before-step state, delete the downstream `created_node_ids`), truncates the `WorkflowSession` + `extension_cli_loader` module-global mirrors to that prefix, then re-dispatches with `action="start"` through the normal `_runWorkflowStepDirect` → `handle_execution_result` → auto-advance loop; loop resume reuses `_repeat_transition_after_completion` / `_handle_pending_repeat_decision`.
- **`extension_cli_loader/workflow_state.py`** — `truncate_workflow_completions`, `set_workflow_choices`, `get_workflow_choices`, `set_all_workflow_repeat_states` overwrite the per-extension mirror dicts to a rewind prefix. `SlicerAIAgentLib/workflow_state.py` adds `prune_missing_interaction_nodes`.
- **`app/widget_replay.py`** (`WidgetReplayMixin`) — `_setupReplayControls` wraps the existing `_workflowProgressBar` in a row with native-icon `QToolButton`s (`:/Icons/pqVcrBack24.png` / `pqVcrForward24.png` / `pqVcrPlay24.png`, text fallback). Stepping back updates the green-box guidance labels (`_workflowActionLabel`/`_workflowInstructionLabel`) via `_updateWorkflowPanel`'s direct-dict path. Recorded live, kept after completion, torn down on cancel or when a new workflow starts.

### Baseline Comparison Harness

Manual, per-step evaluation of the runtime pipeline against three alternative code producers. After a workflow has been run, step **Back** to a step and click the **⚖ Baseline** button (4th control in the replay row, right of "Run from here"); a section opens below it.

- **`BaselineRunner.py`** — Qt-free core: mode metadata, prompt construction, tool ablation, JSON records. Three modes:
  - `pure_llm` — one `LLMClient.chatIsolated` call with a minimal system prompt + the MRML scene summary. No retrieval, no tools, no knowledge base, no CLI, no conversation history.
  - `online_only` — `chatWithToolsIsolated` with dense pre-retrieval and the built-in search tools, but the generated extension CLI ablated: `strip_generated_cli_tools()` removes CLI schemas *by identity* (from `get_dynamic_extension_tools()`, not by name pattern) and `LLMClient.suppress_extension_cli` short-circuits the CLI/`ext:`/cookbook sections of `_buildSystemPrompt`.
  - `claude_code` — code arrives over MCP from an external Claude Code session running the `slicer-skill` skill.
- **`BaselineMCPServer.py`** — two transports; the panel uses **`BaselineMCPBridge`**.
  - `BaselineMCPBridge` (default) **attaches to the skill's own `slicer-mcp-server.py`**, which the user pastes into Slicer's Python console exactly as the skill documents (its MCP config section and `--add-dir` unchanged). It finds `TOOL_HANDLERS` / `mcpLogic` in `__main__`; while armed it swaps *only* `execute_python` for a wrapper and restores the original on disarm — every other tool is untouched, armed or not. Restoration is by identity and is skipped if the user re-pasted the script, so a stale handler can never clobber a fresh registry. Not pasted ⇒ arming is refused with instructions, never a silent substitution: the transport is recorded in every run record (`"transport"`).
  - `BaselineMCPServer` (fallback, unused by the panel) — a self-hosted endpoint on port 2027 with the same tool surface, for when the console script cannot be used. Selecting it is a deliberate deviation from the skill's documented setup.

  Under either transport, `execute_python` routes the code through the agent's CodeValidator + `SafeExecutor.execute()` *synchronously* (so the real stdout/stderr goes back to Claude Code) and advances the step on the next event-loop turn. A failed attempt stays armed so the external agent can iterate; every attempt is recorded separately.
- **`app/widget_baseline.py`** (`WidgetBaselineMixin`) — run orchestration, and a UI that **reuses the existing prompt box and Send button** rather than adding a second pair. The ⚖ button toggles *baseline mode*: one selector row appears above the input row, Send's caption follows the selector (`send_label` in `BASELINE_MODES`) and turns amber, and `onSendButtonClicked` / `onPromptTextChanged` are overridden in the mixin (which precedes `WidgetExecutionMixin` in the MRO, so `super()` reaches `WidgetSendMixin` when baseline mode is off). In Claude Code mode Send arms the MCP endpoint and, while armed, becomes "Stop waiting". Generated code goes to the usual Debug ▸ Generated Code view.
  `_prepareReplayRewind` (extracted from `_rerunFromCheckpoint`) restores the exact pre-step scene, then `WorkflowRuntime.begin_external_step()` opens the step *without* dispatching its CLI template — recording a replay checkpoint as `run_step` would — and `handle_execution_result()` completes it and auto-advances.

All three conditions share the tail of the real pipeline (CodeValidator → SafeExecutor → WorkflowRuntime completion), so only the code producer differs. They deliberately do **not** get plan validation, `ApiSanityChecker`, or the self-correction loop — those are properties of the system under test.

**Baseline prompt & context.** The goal is that each baseline is given every chance to solve the
step, so a failure is a failure of the *approach* and not of the harness. What separates "generous"
from "cheating" is not how much text a condition gets but **where the text came from**: a baseline
gets everything that describes the **task and the world** — the same things a surgeon standing in
front of the running application has — and nothing that is a product of the **offline analysis**,
which is the artefact under test. `BaselineRunner.TASK_STEP_KEYS` is the ALLOW-list (`step_id`,
`operation_type`, `description`), so a field added to `workflow.json` later defaults to withheld;
`WITHHELD_STEP_KEYS` names the other side explicitly (`extension_method_hint`,
`ui_parameter_binding`, `widget_name`, `value_property`, `operation_model`, `node_roles`, …) so the
ablation is legible in review rather than implicit in the code. `build_step_brief()` renders the
allowed side: the step's own cookbook description, its clinical guidance from `step_instructions.json`
(title / simple / detailed — the same words the panel shows the surgeon), where it sits in the
procedure, the steps already completed, the values and nodes the user already chose, and a
`BASELINE_LOOKAHEAD_STEPS`-step lookahead marked *context only*. Every run record carries the full `step_context` and a
`generation.prompt_chars`, so a reader can verify what the condition knew and compare context sizes
across conditions directly.

- **Pure LLM** — `baseline_pure_llm_prompt.md`. Comprehensive *situationally*, empty *technically*.
  It gets the output contract, the execution environment (`__main__` level, no `self`, what is
  pre-imported), the CodeValidator blocked list verbatim (so a rejection measures the model and not
  a rule it was never told), how to reach a scripted module's widget/logic from Python in general
  terms, the live scene, and — because it has no tools and cannot call `GetNodeProperties` mid-turn
  like the pipeline can — full properties of up to 14 relevant data nodes pushed up front
  (`_baselineNodeDetails`). What it does not get is any Slicer API answer: the code still comes from
  the model's own knowledge, in one shot.
- **Online only** — `baseline_online_only_prompt.md`, appended to the CLI-suppressed production
  prompt. The ablation is of the **analysis**, not of the code base: ablating the CLI must not
  silently also ablate the extension source, or the condition is not what it claims to be. So the
  raw `ext:<Name>/` source trees stay searchable and are advertised (`extension_source_roots_block()`
  — module name and path only, no logic-class shortcut, no workflow graph), with a concrete recipe
  for deriving an extension's API from source: find the module → grep the `.ui` label for the
  objectName → follow the `connect()` to the handler → check for `parameterNodeWrapper` → confirm
  the signature with `ReadFile`. Tool budget is raised to 16 rounds
  (`BASELINE_ONLINE_TOOL_ROUNDS`) because this condition's whole thesis is "can it find the API by
  searching?", and cutting it off mid-search would measure the budget instead of the approach.
- **Claude Code** — its *prompt* is authored on the Claude Code side, but its **task brief is not
  optional**: arming a step writes `render_step_brief_document()` to `MCPConnection/current_step.md`,
  and `MCPConnection/CLAUDE.md` tells that session to read it first. Without it Claude Code would be
  the only condition working from the user's sentence alone while the other two get ~1.8 KB of task
  context injected — a comparison of briefings rather than of approaches. Identical text, identical
  `TASK_STEP_KEYS` allow-list; only the delivery differs, because that session takes its prompt
  elsewhere. It needs no extra MCP tool (the skill's surface stays as it ships) and no `--add-dir`
  (the file lands in its own workspace). A copy goes to the run folder so what it was told is
  auditable. The live scene is deliberately *not* in the file — Claude Code pulls it with
  `list_nodes` / `get_node_properties`, which is fresher than a snapshot.

**Context parity across the three.** `step_context` is computed **once**, in `_beginBaselineRun`, for
every mode — so the three conditions cannot drift apart by construction. The two prompt-driven modes
have it injected into their messages; Claude Code reads the same bytes from a file.

**Conditions tested back-to-back on one step are isolated from each other.** Running pure LLM,
then stepping Back and running online-only, then Claude Code, gives all three the *identical*
pre-step scene. The mechanism is self-healing: each successful baseline re-creates the step's
checkpoint, and its before-snapshot is captured *after* the rewind, so it is the same pre-step
state the previous condition saw. A **failed** attempt used to break this — the pending
checkpoint is discarded, so whatever the attempt half-built belonged to no checkpoint and no
later rewind could remove it, silently handing the next condition the previous one's debris.
`WorkflowRuntime.rollback_failed_step()` closes that: on failure it does what
`_record_checkpoint` does on success — diffs the live scene against the snapshot taken when the
step opened, deletes what appeared, restores properties and layout, and **keeps** the pending
checkpoint so a retry reuses the identical starting state. Called from every baseline failure
path (`_rollbackFailedBaselineStep`), including the Claude Code still-armed retry. The pipeline
is deliberately untouched: its pending checkpoint survives across self-correction attempts, so
it is already self-healing, and it is the system under test.
The one real exception is `PedicleScrewPlanner` — the only wizard extension, where downstream
nodes are deliberately kept (deleting them hangs its cached-Python-ref `onEntry`), so
conditions tested on it are *not* isolated and should be reported separately.

**Nothing from after the stepped-back step reaches a baseline.** Rewinding to step N truncates
`completed_steps`, the choices mirror, the completions mirror, `repeat_states`, `last_result` and the
checkpoint list to the step-N prefix, and deletes the downstream nodes — and it happens *before*
`_baselineStepContext`, the scene read and the node-property read, so all three see only pre-N state.
No result object (`_currentWorkflowStepInfo`, `last_result`, `currentCode`, `conversation_history`)
is ever passed into a baseline message, and `next_step` goes only to `step.json` in the log.

The one deliberate exception is the **lookahead**: `BASELINE_LOOKAHEAD_STEPS` (default 3) upcoming
step *descriptions*, marked "context only — do NOT do them". It is cookbook prose — no code, no step
ids, no metadata — and it is what a surgeon reading the written procedure sees on the next page; it
helps a condition leave the scene in a state the procedure can continue from. Note it is **more than
the pipeline has**: the pipeline dispatches its template with no lookahead at all. So it favours the
baselines, in the spirit of giving each condition every chance. Set it to `0` for a strict
no-forward-information ablation — nothing else needs to change.

**Which steps are comparable.** A baseline substitutes a *code producer*, so the step must be one the pipeline answers with executable code. Of the six canonical operation types (`extension_cli_analyzer.common.CANONICAL_OPERATION_TYPES`) exactly two qualify — `WorkflowRuntime.CODE_STEP_OPERATION_TYPES`, an **allow-list** so a type added later defaults to not-comparable:

| type | comparable | why not |
|---|---|---|
| `extension_op` | ✅ | — |
| `slicer_op` | ✅ | — |
| `user_choice` | ❌ | user picks a value/node; no code, and the pick is what later steps read via `_workflow_choices` |
| `user_interaction` | ❌ | the surgeon acts in the 3D view; no producer can stand in for a hand |
| `branch_op` | ❌ | the answer, not the code, decides the next step |
| `review_op` | ❌ | human review checkpoint — has no template at all |

Across the nine cookbook extensions that is 106 of 184 steps (58%). `external_step_eligibility(step_id)` returns `(ok, reason)`.

**The prompt is never authored by the panel.** The box is only ever *emptied*, never pre-filled: the prompt is the independent variable of the comparison, so it is the user's to write for every step and every condition.

**The generated code is unreachable, by enforcement not by convention.** A baseline runs on a step the
pipeline has already answered, so the obvious way to corrupt the comparison is for a baseline to read the
template the pipeline used. Every channel is closed: the prompt is user-typed; `TASK_STEP_KEYS` is an
allow-list carrying no template; `suppress_extension_cli` drops the CLI prompt sections; the CLI tool
schemas are stripped by identity; the isolated chat calls never read `conversation_history`; and the
rewind deletes the step's own output from the scene before the baseline runs. The one channel that was
*open* was the online-only condition's search tools — `SkillToolExecutor._resolve_path` accepted absolute
paths as-is and joined relative ones without normalising, so `ReadFile("../../extension_CLI/<Ext>/templates/<step>.tpl")`
would have returned the answer. `_DENIED_SUBTREES` (`skill_tools/setup.py`) now refuses any path resolving
inside `Resources/extension_CLI`, `Resources/Prompts`, `SlicerAIAgentLib` or `logs`, checked on the
**resolved** path so neither an absolute path nor a `../` traversal gets through. Nothing legitimate reads
those through this executor: the knowledge base is `skill_path`, extension source is `extra_roots`, and the
CLI generation pipeline uses its own file access. The Claude Code condition is fenced the same way, by
scoping its `--add-dir` set (see `MCPConnection/CLAUDE.md`).

**Stepping resets the arm.** `_resetBaselineForNavigation()` runs before Back / Forward / Run-from-here: it leaves baseline mode and empties the prompt box, so each step is judged on its own and neither the previous step's mode nor its prompt text follows the user along the timeline. The user re-arms with ⚖ on the step they land on (possible only where the ⚖ button is enabled, i.e. a comparable step). It returns False while a run is in flight, and the caller abandons the navigation — stepping out from under an executing baseline would orphan its checkpoint and its record.

The ⚖ button is **hidden outright** on a step whose operation type cannot be compared — there is nothing to offer there. That is only safe because the arm can never outlive the step it was set on: Back/Forward reset it, and `_updateBaselineControls` also auto-disarms (and clears the box) when the workflow *auto-advances* onto a non-comparable step after a run. Without that invariant a hidden-but-armed toggle would be unreachable. During a run the icon stays visible-but-disabled so the row cannot vanish under an executing baseline.

Two separate notions still drive the rest: **`_baselineActive`** is the toggle intent, while **`_baselineEngaged()`** is that intent resolved against the step in view (`active and eligible`, plus always-true while a run is in flight). Engagement — not the raw toggle — drives the selector row's visibility, the prompt/Send gate (`_guidedWorkflowOwnsInput`), Send's caption, and Send's routing. The button is `setCheckable(True)` so the armed state is legible.

**Input gating** (`WidgetStreamingMixin`, "Free-text input availability"). Once a generated-CLI workflow is running, every step is dispatched by the runtime and driven from the workflow panel's own controls, so `promptInput` and `sendButton` are switched off for the duration — and switched back on by baseline mode, which is exactly the mode that needs them. `_guidedWorkflowOwnsInput()` is the predicate (`has_active_workflow() and not _baselineActive`); `_setSendEnabled()` is the single funnel every *enabling* call site goes through, so no stray `setEnabled(True)` can defeat the gate (the `setEnabled(False)` sites are left direct — disabling is always safe). `_refreshInputAvailability()` re-applies it and is called from `_updateBaselineControls`, which runs on every `_updateWorkflowPanel`. Escape hatch when a workflow is stuck: the panel's **Exit** button (right end of the replay row) resets the session and returns the input row — the only escape now that there is no traditional turn, which is why it is visible unconditionally while the panel is up and why `onSceneEndClose` triggers the same reset.

**Debug-view isolation** (`WidgetStreamingMixin`, "Debug-view contexts"). The Debug section's two pages are shared by the pipeline and each baseline, but their content never mixes. Two pointers do it: `_debugContext` (which buffer is *displayed* — the ⚖ toggle and the baseline selector move it) and `_debugWriteContext` (which buffer new content is *written to* — the producer currently running moves it). `_chatEntriesHtml` plus the two widgets always hold the displayed buffer; the others are parked in `_debugBuffers` and swapped by `_switchDebugContext`. Every chat append goes through `_debugWriteEntries()` and every code write through `_setGeneratedCode()`, so the two pointers may diverge: when a baseline run finishes and auto-advance hands back to the pipeline, the pipeline's output accumulates invisibly in the `pipeline` buffer and reappears complete the moment the baseline row is closed. Baseline reasoning is committed permanently (the pipeline's streaming entry hides it after `thinking_done`); the online-only tool loop commits one entry per reasoning round via the `baseline_thinking` queue event.

Records land in the run's own folder as `baseline_<step>_<mode>_a<attempt>_<HHMMSS>.json`. The
cross-condition table is built on demand by `scripts/collect_runs.py` (see "Debug Artifacts"), not
written a second time at runtime.

### Experiments panel

Per-procedure analysis of the runs kept under `Experiments/<Extension>/`, behind a selector in the
Experiments section. `SlicerAIAgentLib/experiments/<name>.py` holds the numerics (Qt-free, so it runs
and is checkable outside Slicer) and `<name>_panel.py` the button; a module registers itself with
`@register_experiment_panel("<Extension>")`, and `_PANEL_MODULES` lists what to import.

`run_timing.py` is shared by all of them: what a run folder looks like (`discover_cases`) and what
its `Statistic/timing.txt` says (`parse_timing`, `parse_timing_steps`, `timing_sheet`) are properties
of `RunLog`, not of a procedure. It is parsed from the **rendered report** rather than from
`run_manifest.json`, deliberately — the report is what `Statistic/` guarantees and what a reader
compares against, so a case whose manifest was lost still yields a row. The cost is a dependency on
that report's wording, which is why every field is an explicit regex: a report that rephrases a line
leaves a blank cell instead of a wrong number.

`zygomatic.py` scores relative BIC against the surgeon's STL paths. Three things it enforces rather
than assumes, because all three fail *silently* rather than loudly:

- Paths are paired with their manual counterpart **by entry point**, never by file name — on the
  current data set `1.stl` belongs with `Implant_3` and `4.stl` with `Implant_1`. The STLs under
  `Dataset/<subject>/` may therefore be named anything; renaming them changes no number. The
  assignment is total, so a `MAX_ENTRY_MATCH_MM` ceiling rejects a rod too far from the entry to be
  the same implant — without it, a case folder holding an STL that is not an implant would have one
  scored against it.
- `geometry_io.resolve_frame` proves the paths and the bone are in one coordinate frame before
  anything is scored. An LPS/RAS mix-up mirrors a path onto the other side of the head, where it
  still intersects bone and still produces a BIC number, just a meaningless one.
- The **physical** BIC (`bic_score`, over the drawn segment, used for both sides of the comparison)
  is kept distinct from the **planner's own** score (`planner_bic_score`), which is taken over the
  candidate vector *before* the tip is pulled back by `safetyMargin` and clips its projection
  instead of excluding out-of-segment points. Reproducing the latter exactly is the evidence that
  the bone cloud was reconstructed correctly, and it is never what the comparison divides.

`orbital.py` scores **symmetric surface distance** against the surgeon's ground truth
(`Dataset/<subject>/<subject>_Label.nii.gz`, the correct orbital volume on the fractured side) and
writes a colour map of it. Two comparisons per case, and the second is not padding: the pipeline's
`OFR_Reconstructed_Seg`, *and* the `OFR_Fractured_Seg` it started from. A 0.8 mm reconstruction error
is excellent on an orbit that was 4 mm out and unremarkable on one that was 1 mm out, so the
`IMPROVEMENT` block pairs them and the claim rests on the pair, never on the reconstruction figure
alone.

Four things it enforces rather than assumes:

- **One meshing pipeline for all three surfaces**, at one `SURFACE_SMOOTHING`. A distance between two
  surfaces built by different rules measures the rules. This is also why the ground truth is routed
  through a segmentation node rather than meshed directly from its label map — so it goes through the
  *same* conversion as the two it is compared against.
- **The frames are proved, not assumed** (`_frame_gap_mm` against `FRAME_TOLERANCE_MM`). The ground
  truth is stored on the full CT grid and the run's segmentations on the cropped one; both resolve to
  the same anatomy in RAS, so no resampling is needed — but an LPS/RAS mix-up mirrors one orbit onto
  the other side of the head, which still yields a plausible distance. The two scales (a few mm of
  real anatomical difference, tens of mm for a mirrored frame) cannot be confused.
- **`hd95` leads, not the maximum.** Marching cubes can always produce one stray vertex at the edge of
  a label map, and it moves the maximum by an arbitrary amount and the 95th percentile not at all.
  Both are reported; only the percentile is safe to quote.
- **The colour scale is fixed at 0–`COLOR_MAX_MM`**, not auto-ranged. An auto range renders a 0.5 mm
  case and a 4 mm case with the identical spread of colour, so the one thing a map is for — comparing
  cases by eye — silently stops working.

Unlike `zygomatic.py` this module **needs Slicer**: reading a `.seg.nrrd` and a `.nii.gz`, meshing
them identically, and writing a scene a surgeon can open are all Slicer's own machinery. Everything
that does not need it is kept out of the Slicer-only functions (`slicer`/`vtk` are imported lazily,
inside the functions that mesh and render), so the statistics, the improvement pairing, case
discovery and the MRML splicer are all importable and checked by
`scripts/check_orbital_analysis.py`.

**`slicer.util.saveScene("….mrml")` writes the scene XML and NOTHING else.** For a `.mrml` suffix it
routes to `qSlicerSceneWriter::writeToMRML`, which is `SetURL` + `SetRootDirectory` +
`vtkMRMLScene::Commit()` — and `Commit` serialises the node *elements* but never asks a storage node
to write its data. (Same fact, same reason, as `_saveSceneFlat` writing its nodes first and the scene
last.) Assuming otherwise produces a scene whose storage nodes name files that do not exist, and
Slicer reports it only when the scene is *opened*: `vtkMRMLStorableNode::UpdateScene failed: Failed to
read node … using storage node …`. So `_write_error_scene` writes each node with
`slicer.util.saveNode` and then checks the file is **on disk**, and the splice below happens only on
a True from it — a scene must never be edited to point at a file whose write was assumed. A user
`vtkMRMLColorTableNode` needs its own storage node for the same reason: it serialises `numcolors`
into the XML but not the colours.

**The error maps are written into the run's own `Statistic/scene/`, and the run's `scene.mrml` is
edited in place.** That is the one operation here that can damage existing data, so: the original is
copied to `scene.mrml.orig` **once** (a second copy taken later would preserve a splice, not the run);
every spliced element's MRML id carries `ID_MARKER`, which is what makes a re-run *replace* its
previous output instead of stacking a second copy; and the splice is XML surgery rather than
load-modify-save, because the run's scene carries the 40 MB CT and every node the procedure made, and
rewriting all of it 30 times to add two models is both slow and a far larger blast radius.
`_renamed_id` strips the trailing digits and appends the marker, so a new id cannot collide with a
Slicer-generated one — and the rewrite uses a `(?![0-9])` lookahead, without which
`vtkMRMLModelNode1` would be rewritten inside `vtkMRMLModelNode10`. The splicer follows a node's
references only into `_SPLICEABLE_TAGS`: a display node also references its *view*, and following
that would splice a second `View` node into a scene that already has one.

**Three Slicer-side constraints, each of which crashed the application or silently skipped work
when broken.** `numpy_to_vtk` defaults to `deep=0`, which makes the VTK array a *view* on the numpy
buffer -- no VTK object may outlive what owns its memory, and `scripts/check_orbital_analysis.py`
enforces `deep=1` at the AST level because there is no VTK outside Slicer to test against. The
ground truth is **cropped to its labelled bounding box before meshing**: it arrives on the full CT
grid, so meshing all of it is 31-142x wasted work and exhausts memory on the largest case. And
`_write_error_scene` is handed the nodes to write rather than asking the scene, since
`getNodesByClass("vtkMRMLColorTableNode")` also returns Slicer's built-in colour tables -- some of
which point into the application's own installation.

The panel **refuses while a guided workflow is open** and confirms before starting, because the
analysis builds each case's models in the main scene — the only way to save a scene Slicer is certain
to reopen — and therefore closes whatever is open.

`shoulder.py` scores the four measures of Li et al. (IJCARS 2022;17:1017-1027) — θ₁, θ₂ (each long
screw against the middle peg), θ₃ (the two screws against each other), and **δ**, the chosen path's
bone-density integral over the largest integral anywhere in its cone once the screw-exposure
constraint is dropped — plus the run's time split into the paper's t1/t2/t3.

**Two plans are scored, not one.** Beside the pipeline's `Path_Screw*` each case carries the
surgeon's own `Manual_Screw_Model_*` and an `RSA_ManualPlanResults.tsv`, and the workbook's leading
block pairs them per baseplate hole. What makes that a *paired* comparison rather than two separately
normalised numbers is that the hand plan reuses the pipeline's baseplate pose: the two trajectories
leave the same point along the same axis — measured at 0.000000 mm apart on every screw of every
saved case — so `_cone_denominators` builds **one** cone per hole and both sides divide by it.
`delta_gain` is then a subtraction that means something, and the pairing is enforced
(`ENTRY_PAIR_TOLERANCE_MM`) rather than assumed from the digit in the file name. The manual geometry
comes from the **table**, not the mesh: `Manual_Screw_Model_*.vtk` is the screw cylinder, which
overhangs its entry by 3 mm and is 3.1 mm in radius, so neither its extreme vertex nor its cap
centroid is the trajectory's start — the mesh is read only as a witness that its axis agrees with the
row (`mesh_agreement_deg`). Note the result splits by `selection`: on the 14 `planned` screws the
pipeline is denser 11 times, on the 6 `BEST EFFORT` screws only once — which is what should happen,
since a best-effort trajectory was aimed by depth and not by density at all.

**Every number is recomputed, because the extension stores none of them.** `RSA_PlanResults.tsv`
carries endpoints and a status but no score; `quality_index` is identically 1.000 (`path_optimizer.py`
assigns `stability_score` and `max_hu` the same value); and δ's *denominator* is never computed at
all — the optimizer `continue`s past a rejected candidate **before** scoring it, so the integral of
the paths it turned down does not exist anywhere. That makes reproducing the planner's arithmetic
exactly the whole job, and the evidence that it was reproduced is `score_reproduced`: the recomputed
integral equals the `Stability score` the run printed at the time, bit for bit (5098 and 4855 on the
two reference runs). The planner's stdout is truncated near 10 KB, so screw 2 usually has no witness
— a blank there is a missing witness, not a disagreement.

Four things it enforces rather than assumes:

- **The LPS→RAS flip cannot be validated by the angles.** Slicer writes models in LPS, the CT is
  indexed from RAS, and `geometry_io.read_vtk_points` converts nothing (its docstring says RAS and is
  wrong). But `lps_to_ras` is orthogonal, so every dot product — and therefore all three angles — is
  *exactly* invariant under the mirror: θ comes out perfect either way. Only δ notices, and it
  notices by reading **1.000**: the mirrored path leaves the CT array, every sample takes the
  out-of-bounds sentinel, and numerator and denominator become the same large negative number, i.e. a
  flawless score for a plan that is not in the patient. Three independent guards, none redundant —
  `tsv_max_gap_mm` (the plan table is written in RAS and is an independent witness),
  `samples_in_bounds` (below which no ratio is reported at all), and a δ > 1 flag.
- **There are two denominators and they answer different questions.** `path_generator.py` drops every
  azimuth pointing at the other screw's hole, so the planner searches *half* the cone. That is an
  anti-crossing rule, not the exposure constraint δ ablates, so `delta` divides by the **full** cone
  (the paper's "entire conical space") and `delta_searched` by the half read out of the run's own
  saved `Cone_Region` model. Both are reported. The sweep is also repeated at 2× resolution, because
  the denominator is a maximum over a grid and a reader is entitled to ask whether δ is an artefact
  of it.
- **The summary never pools the two populations.** When nothing in the cone keeps the whole screw
  inside the bone the planner returns the deepest-reaching candidate instead — tie-broken by
  protrusion, and only then by density — so that screw's δ scores a trajectory that was never
  optimised for density. Half the screws of the two reference runs are such rows. `delta (planned)`
  and `delta (BEST EFFORT)` are therefore separate summary rows and the panel's headline quotes the
  first; a pooled mean would answer neither question and would drift with the proportion of
  best-effort screws in the cohort.
- **The cone's geometry is measured, not assumed.** Half-angle, height and radius come from the saved
  `Cone_Region` model and the lengths from the drawn tubes, because all three are spin boxes the
  surgeon can change — a run made at a different setting must be scored against the cone it actually
  had. Note the shipped half-angle is **22.5°**, i.e. half the paper's α; θ₁/θ₂ are bounded by it,
  not by 45. The *axis* is the middle peg's direction and is never fitted from the cone: that base is
  a 180° half-disc, so its centroid is 5.5 mm off-axis and a centroid fit yields 23.5°.
- **A step in no timing phase is named, not dropped.** `PHASE_STEPS` maps cookbook steps to
  t1 (bone reconstruction) / t2 (the reference point *and* the baseplate pose — this version picks
  one fiducial, and `onPositionBaseplate` reads control point 0 only, so the pose replaces the paper's
  missing p2–p4) / t3 (`cb_step_20` **alone**, which runs the whole cone search) plus t0 and
  t_refine, which sum into the total and into none of the three. Charging the post-plan dragging of
  steps 21–23 to "automatic planning" would have overstated t3 by 8.3 s on one reference run. A
  renumbered workflow would otherwise make the phases silently shrink.

Unlike `orbital.py` this module needs **no Slicer at all** — it is arithmetic over point sets and one
CT array, so `volume_io.py` reads the saved `.nrrd` itself (gzip, and the LPS flip in both the
direction vectors and the origin) and `scripts/check_rsa_analysis.py` runs the *entire* analysis, δ
included, against the real runs outside Slicer. Given that the failure above produces a perfect-looking
number rather than an error, that is not a convenience. The panel writes only the workbook: it builds
nothing in the scene, so unlike the orbital one it needs no confirmation and no scene-close warning.

`cranial.py` scores the three metrics of the **AutoImplant 2021 challenge** (Li et al., *Medical
Image Analysis* 88 (2023) 102865, §3.3) — DSC, HD95 in mm, and **bDSC**, Dice restricted to the part
of each implant lying within `t` of the *defective* skull, which is the transition where the fit is
decided. Every measure is voxelwise and exact: the ground truth and the prediction share a byte-
identical grid in all 100 cases, so nothing is resampled and no binary mask is ever interpolated.

Four things it enforces rather than assumes, each of which yields a plausible number rather than an
error when got wrong:

- **Segments are resolved by NAME.** `Cranial Implant Result.seg.nrrd` is ONE shared labelmap holding
  `Skull` = 1 *and* `Implant` = 2. Reading it as non-zero scores the ground truth against the whole
  skull — 320 k voxels against 2.1 M — and reports a DSC near 0.2 that reads like a pipeline failure
  rather than a coding error. `volume_io.read_nrrd` deliberately drops every `key:=value` line, so
  `segment_label_values()` parses the segment table itself.
- **The defective skull is that same file's `Skull` segment**, not `Cranial_Segmentation.seg.nrrd`.
  The latter is the COMPLETE skull, thresholded from the CT *before* the defect was cut: 87–99 % of
  every ground-truth implant lies inside it, so banding against it would put the whole implant in the
  border and turn bDSC into DSC. The `Skull` segment's intersection with the ground truth is exactly
  0 voxels in 100/100 cases, which is what makes it the right object — and the check script asserts it.
- **Spacing is the COLUMN NORM of IJK→RAS**, not of its inverse. The inverse gives voxels-per-mm,
  which scales every distance by ~2.6× on this data and leaves DSC (dimensionless) untouched — so
  only HD95 shows it, and only against a reference. It put HD95 at 3–12 mm against the paper's
  1.3–7.4; corrected it is 1.4–3.7. In-plane spacing also varies per case (0.38–0.61 mm) while slices
  are always 0.75 mm, so no voxel volume is ever assumed.
- **The metric window is a crop, and the crop is exact.** Both surfaces lie inside
  `bbox(gt | pred)`, so surface distances are unchanged; and any voxel within `t` of the skull has its
  nearest skull voxel within `t`, so a margin ≥ `t` reproduces the border predicate exactly. Uncropped
  the batch takes 32 minutes, cropped 5 — and `check_cranial_analysis.py` proves the two agree bit for
  bit on real cases rather than taking the argument on trust.

`t` is reported **twice**, for the reason `shoulder.py` reports two cone denominators: `bdsc` uses the
paper's `t = 10` **voxels** and is the published metric, while `bdsc_mm` uses a fixed 5 mm band —
10 voxels is 3.8 mm in-plane on the finest case and 7.5 mm through-plane on every case, so the
physical size of the band moves with the acquisition. Both are reported; neither is picked silently.

**Quote the MEDIAN HD95, not the mean, and read the two one-directional shares beside it.** On this
cohort the median is 2.1 mm and the mean 8.0, with a maximum of 137 mm — and the outliers are not
noise or a stray component (every mask is a single connected component). They are one-directional: on
A0061, *none* of the predicted surface is more than 20 mm from the truth while 67 % of the truth has
no prediction within 20 mm. The implant is accurate wherever it exists and simply covers a fraction of
a much larger defect. HD95 pools both directions, so it reports that as one large number and cannot
say which way it went; `gt_covered_2mm_pct` (completeness) and `implant_on_gt_2mm_pct` (false-positive
area) can, and they are the paper's own two feasibility criteria measured on the surface. This is why
the table carries more than three columns, and why the summary reports median, p25 and p75 rather than
mean alone.

The error map follows `orbital.py` and **imports its machinery rather than copying it** — the meshing
pipeline, the distance filter, the write gate and the `scene.mrml` splicer are the most dangerous code
in the package (they edit a saved run in place) and a second copy would be a second thing to keep
correct. Only the colour table and the model node are re-implemented, because orbital's bake in its
own 3 mm ceiling and a cranial map on that scale is red almost everywhere (`COLOR_MAX_MM = 5.0`).
The map colours the **predicted** implant by its distance to the ground truth — the question a reader
brings to a cranioplasty map is "where is the implant I produced wrong", not "which part of the truth
did it miss" — which is why the prediction is passed to `_surface_distances` first. `map_hd95_mm` is
the same figure recomputed from those smoothed meshes and is carried in the table beside the voxel
`hd95_mm`, so the picture and the number can be seen to agree instead of being trusted to.

`pelvic.py` scores how far a planned fracture reduction is from the surgeon's, and it **reads that
number rather than measuring it**. Each run saved three things into its own `Statistic/scene/`:
`Fragment Reduction*.seg.nrrd` (where the pipeline put every bone), `Ground truth*.seg.nrrd` (where
they belong), and `Ground truth*.transforms.json` — **the per-piece rigid transform between them,
recorded when the annotation was saved**. That transform *is* the reduction error, so
`displacement_mm` and `rotation_deg` come straight out of it.

The first version of this module recovered the same transform by ICP between the two segmentations.
It agreed with the record to **0.009–0.034°**, which is a good reason to believe both and no reason
to keep spending a hundred iterations per piece re-deriving a number that is written down. The
estimator is gone, and `check_pelvic_analysis.py` asserts statically that no `kabsch` /
`rigid_register` / SVD has grown back — a fitting step added later would agree with the record to a
hundredth of a degree, so nothing else would notice the claim had stopped being true.

**Reading a number instead of measuring one has exactly one hazard, and it is not hypothetical.** A
record measures whatever was on disk *when it was written*; ICP measured whatever is on disk now. A
ground truth re-annotated afterwards leaves the record silently stale — which happened here: an
earlier ground truth gave 5.83° where the record says 2.25°. So the segmentations are still read,
and `transform_residual_mm` applies the recorded matrix to the reduction's own surface and measures
how far it lands from the ground truth's (0.14–0.24 mm on the saved runs — the two grids' sampling).
Two verdicts, and they are not interchangeable: **`record_consistent`** judges the record against
*itself* (the matrix is a proper rotation, its stated angle and axis are the ones it encodes, it
carries `centroid_reduced_mm` onto `centroid_annotated_mm`) and catches a malformed file;
**`transform_verified`** judges it against the *files* and is the only thing that catches a stale one.
The check script builds a deliberately stale case — a ground truth moved one way, an internally
perfect record saying another — and requires it to be refused. `verify=False` (a panel checkbox)
skips the segmentations entirely and finishes in milliseconds, reporting identical displacement and
rotation and leaving the second verdict **blank rather than True**: a blank and a failure must not
print the same.

**`displacement_mm` is measured at ONE point and `point_error_*` is not.** A rigid body's
displacement depends on which point you pick: case 0001's Left Ilium is 1.74 mm out at its reference
centroid and **6.13 mm** out at its worst surface point, because 2.25° of rotation moves the far end
of an ilium far more than its centre. `point_error_*` applies the recorded matrix to every surface
point — arithmetic, not estimation — and is the figure to quote. `surface_*` is the symmetric
distance between the two surfaces *as they stand* and is smaller again, because a point that slid
**along** the surface still has a near neighbour on it. No Dice: for a rigid piece, overlap is a
function of the same pose error the record states directly.

Pieces are paired by NAME. The record names **fewer** pieces than the reduction moves — the surgeon
only corrected some — so the rest are listed as unannotated rather than dropped, and a ground-truth
segment with no recorded transform is reported too.

`segmentation_io.py` is the Slicer-free reader this needs, and `volume_io.read_nrrd` could not be it:
a segmentation with overlapping segments is **4-D**, and its `list` axis of LAYERS is the first of
`sizes:` and therefore the **last** array index. `array[layer]` is in bounds, is the right dtype, and
returns a slab of the volume instead of a layer of it — after which every segment comes back nearly
empty. A segment is addressed by the pair `(layer, label value)`: case 0001's `Right Ilium` and
`Left Ilium` are both label 2, in different layers. `Segment<N>_Extent` is deliberately **unused** —
cropping to it would be a large speed-up, and the extent is the segment's *tight* box, so foreground
on its faces is expected and a truncated read looks exactly like a correct one. Everything is scanned
in slabs with a one-plane halo instead (peak memory is a slab, not the 912 MB a case-0001 file
unpacks to), and the centroid comes from per-axis marginal counts rather than `np.nonzero`, which
over a half-full 32 MB slab would itself cost 380 MB.

`canonical_step_id` moved from `shoulder.py` into `run_timing.py` when this became the second phase
split to need it — the run folder zero-pads step ids so they sort and the timing report does not, so
reconciling the two belongs beside the report, not in any one procedure.

### Debug Artifacts

`SlicerAIAgentLib/RunLog.py` owns run-folder naming and artifact writing (Qt-free, fail-soft — a
logging failure must never abort the run being logged). The folder name is the only thing visible in
a file browser, so it carries the five facts a reader needs before opening anything:

```
logs/ZygomaticImplantPlanner_baoyawen_pipeline_20260803_154954/
     ZygomaticImplantPlanner_baoyawen_pureLLM_cb_step_08_a1_20260803_155230/
     \_____________________/\_______/\______/\__________/\_/\_____________/
          procedure          subject condition   step  attempt    when
```

**Procedure first, timestamp last**, because analysis is per procedure and per subject — the four
conditions run on one patient are the unit of comparison, and a leading timestamp scatters exactly
that grouping through the listing. A name sort is therefore no longer chronological; sort on the
trailing stamp (or on `started` in the manifest) for that. The **subject** is the input data set,
derived from the folder the scene's data was loaded out of, and omitted entirely when it cannot be
determined — a placeholder would silently merge two patients' runs.

`_sceneSubjectName` takes the most common parent folder of the storage nodes' files, and a count
alone is not enough. Opening any module that needs the colour logic makes
`vtkMRMLColorLogic::AddDefaultColorNodes` load ~20 colour tables out of
`<slicerHome>/share/…/ColorFiles`, each a storable node with a storage node and a file name, which
beats a case folder holding one volume and one markup 20 to 2 — observed, as a run folder named
`ZygomaticImplantPlanner_ColorFiles_pipeline_…`. Whether it happens depends on which modules the
session has touched, so it is intermittent, and its symptom is a plausible name rather than an
error. Two filters, either sufficient alone: only nodes that are the **user's data** vote
(`_isUserDataNode` — not `HideFromEditors`, `SaveWithScene`; the same predicate `_saveSceneFlat`
uses for File ▸ Save Data, and every colour node sets `HideFromEditors` in its constructor), and
**application-owned directories are excluded** — `slicerHome` and `extensionsInstallPath` alongside
our own `logs/`, Slicer's temp and the DICOM database, compared as paths rather than by `startswith`
so a sibling is not caught by a prefix. The name is fixed when `_createRunLogDir` opens the folder at
workflow **start**, not at Exit, so a mislabelled run stays mislabelled — and since the experiments
analysis pairs a run with `Dataset/<subject>`, that is not only cosmetic.

A general, non-workflow turn is `task_pipeline_turnN_<stamp>`; a request the router
refused under `GUIDED_ONLY_MODE` is `refused_pipeline_<stamp>`, holding the `00_router/` call that
declined it and a manifest sealed `refused` with the cause.

**One run folder per workflow, one subfolder per step.** Chat turns that drive an already-active
workflow ("done", a choice) keep writing into the same run folder rather than each opening a new
one. Step folders are zero-padded (`cb_step_08`) purely so they sort in run order — the true,
unpadded `step_id` is always in `step.json` and in the manifest.

**A run folder has exactly two children**, so which one a reader wants is answerable from the
name: `runtime/` is everything written while the run executes, `Statistic/` is the report and the
scene it produced. `_currentLogDir` is the *runtime* dir (so every writer is unchanged) and
`_currentRunRoot` is the folder holding both — that is what `Statistic/` hangs off, and what
"Exit without saving" deletes.

```
logs/ZygomaticImplantPlanner_Case01_pipeline_20260804_122026/
 runtime/
  run_manifest.json        condition + label, subject + its source path, prompt,
                           model, router cost, per-step
                           status/seconds/errors, totals. Rewritten on every mutation,
                           so a session killed mid-workflow still leaves a usable record.
  role_trace.json          the whole run's events
  00_router/               the routing call: messages_sent.txt, reply.txt, call.json
  cb_step_01/
    step.json              step id, operation type, description, origin, next step
    code.py                the code this step executed
    agent_plan.json
    execution.json         success, seconds, error, scene_delta   <- NEW
    output.txt             raw stdout / stderr                    <- NEW
    role_trace.json        only this step's slice of the trace
    timing.txt             per-step performance breakdown
    thinking.txt           reasoning for this step
    correction_1/          attempt.json, first_prompt.txt, code.py, agent_plan.json,
                           response.json — nested under the step it repairs
    revision_1/            request.txt, messages_sent.txt, reply.txt, revision.json
                           — one per ✍ Revise of this step. The package keeps its
                           own copy (plus the before/after and the diff) under
                           <ext>/debug/revision_<ts>/, because the two answer
                           different questions: why THIS run's step 12 differs
                           from the shipped template, versus what has ever been
                           asked of this package.
  cb_step_02/ …
 Statistic/                written at Exit — see below
```

A baseline folder is flat (it is one step by construction) and additionally holds `prompt.txt`,
`messages_sent.txt` / `.json` (the **exact** payload the condition received, so a reviewer can
confirm no offline-analysis artefact reached it), `step_context.json`, and the
`baseline_<step>_<mode>_a<n>_<time>.json` record.

**`logs/<run>/Statistic/` — what pressing Exit leaves behind.** A run folder stays self-contained, so
copying or deleting one takes its statistics with it:

```
logs/ZygomaticImplantPlanner_Case01_pipeline_20260804_101200/
  Statistic/
    timing.txt
    scene/
      scene.mrml
      Cranial_Segmentation.seg.nrrd
      SkullModel.vtk
      SymmetryPlane.mrk.json
      ImplantPath_1.mrk.json …
```

**The scene folder is flat, matching File ▸ Save Data with every row pointed at one directory.**
`slicer.util.saveScene(<dir>)` cannot produce that: a directory path routes to
`qSlicerSceneWriter::writeToDirectory` → `SaveSceneToSlicerDataBundleDirectory`, which builds `Data/`
and `private/` subfolders. `_saveSceneFlat()` reproduces `qSlicerSaveDataDialogPrivate` instead —
skip non-storable / `HideFromEditors` / `!SaveWithScene` nodes, `AddDefaultStorageNode()` and skip
anything that needs none (it lives in the scene), skip `fileWriterFileType == "NoFile"`, name each
file `<sanitised node name>.<GetDefaultWriteFileExtension()>` (so a segmentation lands as
`.seg.nrrd` and a markup as `.mrk.json`, exactly as the dialog shows), and write the **nodes first,
the scene last** so the `.mrml` records the paths just written. Same-named nodes are de-duplicated
rather than silently overwriting each other.

Every mutation it makes to the live scene is undone in a `finally`: storage-node file names, the
scene URL and root directory, and — critically — `SetStorableNodesModifiedSinceRead()`. Writing a
storable node stamps its `StoredTime`, which clears `GetModifiedSinceRead()` scene-wide; without the
restore the surgeon's own segmentations would show as "Not Modified" and unchecked in File ▸ Save
Data, quitting Slicer would raise no unsaved-data warning, and the only copy on disk would be the one
inside `logs/`. Slicer's own MRB writer does the same restore for the same reason
(`qSlicerSceneWriter::writeToMRB`); the directory writer does not.

**Two clocks, because one is not enough.** The manifest's per-step `seconds` is the time SafeExecutor
spent running that step's code — *machine* time. It is not how long the step took: a `user_choice`
step whose code runs in 8 ms sits on screen for as long as the surgeon takes to pick a node, and a
`user_interaction` step is almost entirely hand time. So `RunManifest.open_step()` stamps
`opened_epoch` when the step appears and `finish_step()` stamps `completed_epoch` when the workflow
moves past it, giving three columns per step: **wall** (screen to screen), **exec** (accumulated
across pre+post templates, repair retries and loop iterations — so `exec_seconds_total`, not the last
run's duration), and **wait** = wall − exec, attributed to *the surgeon* on the four
`HUMAN_IN_LOOP_TYPES` and to *runtime overhead* on the automated two. The total is anchored to the
**Send click** (`send_clicked_epoch`), not to the manifest's own `started_epoch`, which is stamped
only once the router has answered — several seconds the surgeon sat through would otherwise vanish;
it decomposes into startup / inside the steps / between steps / **reviewing the replay timeline** /
waiting for Exit, which sum to it.

**One table, in the order things happened.** `manifest["timeline"]` records a row per step *visit*
and a row per replay review, and the report renders that — so a run that stepped back from step 20
and re-ran from step 10 shows steps 1–20, a `<< step back` row, then steps 10 onward again. `steps`
still holds the aggregate (`scripts/collect_runs.py` reads it) and the report falls back to it for
manifests written before the timeline existed. A replay row's time is **taken out of** the step that
was on screen (`suspend_step_span` banks its span and closes its row), or a review lands in a
`user_choice` step's `wall` and — since `exec` does not move — prints as think time on a step nobody
was thinking about.

Five invariants that are easy to get wrong, each enforced in code because getting one wrong produces
a plausible number rather than an error:

- **A step is measured per *visit*, not first-open-to-last-completion.** Within one visit
  (`start` → `choice_made`/`proceed`) the clock must *not* restart, or a choice step's think time and
  an interaction step's placement time — the whole point — are erased. But a step can be **re-visited**:
  a repeat block re-arms its body and re-dispatches every member with `start` (6 of the 9 workflows
  have multi-step loop bodies), and the replay stepper and baseline harness re-run steps the same way.
  Spanning that would make each body step cover the *whole loop* including its siblings — per-step
  spans overlap, their sum exceeds the run they are reported against, and a neighbouring interaction's
  hand time prints as an automated step's overhead. So `open_step` banks the closed span and starts a
  new one **only on `action="start"`**, and `wall_seconds` is their sum.
- **A step entering a wait is not a step completing.** An interactive step runs its PRE template on
  `start`, and the execution recorder stamps every execution as a completion — it runs before the
  runtime has decided. `reopen_step()` retracts that stamp on the confirmed entering-wait branch, so
  the real completion lands when the POST template runs after Done.
- **The no-code path only completes a step that actually moved on** (`next_step` or
  `workflow_completed`), since it is also reached by a step entering a wait.
- **Exit seals whatever was still open** (`_seal_open_spans`, called from `finish()`), so a run
  abandoned mid-step or mid-preview still has every interval as a row and the table still sums.
  A span is live only if no `completed_epoch` has landed *since* it opened — `finish_step`
  deliberately leaves `span_opened_epoch` in place so a re-visit can bank it, so its mere presence
  is not "still running"; treating it as such rewrote every completed step's wall to
  first-open→Exit.
- **`build_run_statistics()` is a pure function of the manifest**, so the same report can be
  re-derived later from `run_manifest.json` alone; and its five-way split is never clamped — a
  negative residual prints as `[!] clocks inconsistent` rather than being hidden, because that
  residual is the only evidence a reader has that the two clocks disagree.

Writing the report also closed a gap it depended on: steps that produce no code never left `running`
in the manifest — four steps of a completed 27-step run were recorded that way.

The scene is saved **after** the replay timeline is torn down, so the one hidden
`vtkMRMLSceneViewNode` per step is already gone — otherwise the folder would carry a full copy of
every intermediate state. Both halves are fail-soft and independent: a scene that cannot be saved
still produces the report, with the failure recorded *in* it. Only the Exit button triggers this;
the other two callers of `_resetGuidedSession` are a runtime cancel and a scene close, and on the
latter there is no scene left to save.

**Saving is the user's choice, not a consequence of exiting.** The confirmation offers three
outcomes — *Exit and save* / *Exit without saving* / *Cancel* — because "leave the panel" and "keep
the record" are independent decisions, and a Yes/No dialog welds them together: saving writes a full
scene copy, hundreds of megabytes and tens of seconds on a segmented CT, which a user abandoning a
mis-started run has no reason to sit through. `_resetGuidedSession(save=…)` gates the write *and*
the progress dialog; `save=None` derives it from `reason`, so the two non-Exit callers are unchanged.

**"Without saving" DELETES the run folder**, because a run's artifacts are written *incrementally as
it executes* — there is no "don't write it" to choose, only a removal. `_discardRunLogDirs()` takes
`_sessionLogDirs` (the pipeline's folder plus any baseline folders opened off its steps; reset by
`_createRunLogDir(new_session=True)` at the router's workflow-start, so a `refused_pipeline_*` folder
written between two runs is never swept up). `rmtree` is the only irreversible thing in the module,
so it is gated on a **containment check on the resolved path** — a direct child of this extension's
own `logs/`, nothing else — rather than on the caller having passed the right thing.
`_releaseRunLogDir()` runs first: `LLMClient._debugPath` and `RunManifest.write` both
`os.makedirs(exist_ok=True)`, so one later write would re-create the folder just removed. The answer is read back as a **button role**, never as
button identity or position: Qt reorders by platform convention, and PythonQt can return a fresh
wrapper for the same `QAbstractButton`, so `clickedButton() is save` may be False for the button
just clicked. The dialog is shown even when nothing is at risk, because saving is the main thing
Exit does on a *finished* run.

The save is slow and blocks the Qt main thread, so it runs behind a modal progress dialog
(`_beginExitProgress`). That dialog calls `slicer.app.processEvents()` to paint, which is why
`_resetGuidedSession` opens with a `_guidedExitInProgress` guard — without it a scene close delivered
during the pump would start a second teardown through half-dismantled state.

**The aggregate view is derived, not written.** `scripts/collect_runs.py` walks `logs/*/runtime/`
(falling back to the run root for pre-split runs, so no run silently drops out) and emits one
row per (run, step) across **all four** conditions — `--step cb_step_9` prints that step under every
condition side by side; `logs/runs_index.csv` is the full table. This replaced
`logs/baseline_runs.jsonl`, an append-only file that duplicated the per-run record byte for byte and
covered only the three baselines: a "whole session in one file" that silently omitted the system
under test invites analysing whichever conditions are convenient, and a second live writer of the
same facts can drift from the first. A derivation cannot.

Three prior defects this replaced, all of which cost data:
- Every step of a workflow wrote its plan, role trace and timing to the **same three filenames** in
  one folder, so a 33-step run retained only the last step's.
- Correction artifacts were keyed by attempt number alone (`1_correction_0_…`), so two steps each
  failing on attempt 0 overwrote each other.
- The pipeline persisted **no execution result at all** — success, stdout, errors and scene delta
  reached only the role trace, which the next step then overwrote. That left the system under test
  the least-instrumented of the four conditions.

`_artifactDir()` is the single funnel every writer goes through; `_setStepLogContext(step_id)` opens
a step's folder and repoints the LLM client's prompt dumps into it. A baseline parks the pipeline's
folder, manifest, step context **and role trace** (`_restorePipelineLogDir`) so the step it
auto-advances to — dispatched by the *pipeline* — neither logs inside the baseline's folder nor
inherits its events.

**No `thinking.txt` in a clean guided run is correct, not a bug.** The routing call is deliberately
non-thinking (`thinking=False`, `reasoning_effort="low"`, `temperature=0`) — a 9-way classification
against a fixed JSON schema does not need reasoning tokens, and thinking would slow the one turn
this path exists to speed up. After it, the dispatched steps are deterministic template execution
and call no model at all. So reasoning only appears when self-correction fires, or in an
`onlineOnly` / `pureLLM` baseline folder. `00_router/call.json` records the flags and states this,
so the absence is answerable from the artifacts alone.

## Coding Conventions

- 4-space indentation. PascalCase filenames matching primary class/responsibility.
- Module/widget/logic/test classes use `SlicerAIAgent*` naming per Slicer's `ScriptedLoadableModule` pattern.
- Commit messages use conventional prefixes: `feat:`, `fix:`, `chore:`, `docs:`.
- Do not commit API keys, model caches, debug logs, or retrieval indexes.

## Security Considerations

When modifying execution behavior, update `CodeValidator.py` and `SafeExecutor.py` together. Code execution runs in Slicer's `__main__` namespace with blocked imports (`os`, `subprocess`, `sys`, `socket`, etc.) and blocked functions (`eval`, `exec`, `open`, `getattr`, etc.). The `CodeValidator` maintains three sets: `blocked_modules`, `blocked_functions`, and `allowed_modules`. SafeExecutor intercepts VTK C++ errors by temporarily replacing the global `vtkOutputWindow`.
