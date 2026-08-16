# Prompts

Every prompt this project sends to an LLM lives in this directory as Markdown — never as a string
literal in Python. A prompt is an experimental variable of this system: it has to be editable,
diffable and citable without touching code, and a paper has to be able to point at the exact file.

`SlicerAIAgentLib/PromptLibrary.py` is the only module that reads this directory. Files are
re-read when their mtime changes, so an edit takes effect on the next call — no Slicer restart.

Placeholders are `{{UPPER_SNAKE}}` (doubled braces, so ordinary Markdown/JSON braces in the prompt
need no escaping). An unfilled placeholder collapses to an empty string.

## Files

| File | Used by | When |
|---|---|---|
| `system_prompt.md` | `LLMClient._buildSystemPrompt` | The full coding agent: general Slicer requests, and self-correction |
| `workflow_router_prompt.md` | `WorkflowRouter` | The opening turn, to pick which guided workflow the request means |
| `baseline_pure_llm_prompt.md` | `BaselineRunner.pure_llm_system_prompt` | Baseline 1 — pure LLM, no tools |
| `baseline_online_only_prompt.md` | `BaselineRunner.online_only_addendum` | Baseline 2 — online agent with the generated CLI ablated |
| `extension_cli_analyzer_prompt.md` | `ExtensionCLIAnalyzer` | Offline CLI generation pipeline |
| `voice_command_prompt.md` | `voice.commands.build_fallback_prompts` | Voice control, second tier — only when the deterministic matcher is uncertain about an utterance |
| `template_revision_prompt.md` | `TemplateReviser.revision_system_prompt` | The ✎ Revise button — rewriting ONE step's template from the user's description of what it should have done |

Baseline 3 (Claude Code + Slicer skill over MCP) has **no prompt file here**: its context and
prompt management live entirely on the Claude Code side, and this runtime only executes the code
that arrives.

## Which prompt runs when

A request arrives:

1. **A generated-CLI workflow is already running** → `WorkflowIntentResolver` (a small inline
   JSON prompt, no file) maps the message to an allowed workflow action. No system prompt.
2. **No workflow running, and the request names a planning procedure** → `workflow_router_prompt.md`.
   One tool-free call, ~6 KB, whose entire job is choosing the workflow. On a match the runtime
   dispatches step 1 and the LLM leaves the loop; every later step is driven by the runtime, not
   by a prompt. This replaced a ~140 KB full agent turn whose only output was the same choice.
3. **Anything else** (general Slicer request, or the router declined) → `system_prompt.md`, plus
   dense-retrieval snippets, the scene, and the extension CLI sections. Unchanged.
4. **Generated code failed at runtime** → self-correction reuses `system_prompt.md` in full, plus
   the failed code, the error, the original tool trajectory and live API evidence. Deliberately
   *not* short: repair is the one place that needs the whole history and the search tools.
5. **Generated code RAN and did the wrong thing** → `template_revision_prompt.md`, when the user
   presses ✎ and says so. Nothing automatic reaches this one: a step that raises nothing produces
   no signal, so the trigger is a person. It is scoped to the step on screen and rewrites that
   step's `.tpl`, so unlike (4) it works on the template with its placeholders intact rather than
   on the filled code.

## Dynamic content appended at runtime

`_buildSystemPrompt` appends these to `system_prompt.md` — they are not in the file:

- `## PLATFORM INFORMATION`, `## ROLE-COMPOSED AGENT PROTOCOL`, `## REQUIRED OUTPUT FORMAT`
- `## RELEVANT KNOWLEDGE BASE SNIPPETS` — dense pre-retrieval results
- `## CURRENT SLICER SCENE` — the MRML scene summary
- `## EXTENSION CLI TOOLS`, `## EXTENSION SOURCE CODE`, `## COOKBOOK-GUIDED WORKFLOW` — suppressed
  when `llm_client.suppress_extension_cli` is set (the online-only baseline's ablation)
- `## ACTIVE WORKFLOW` — the running workflow's state fragment

## Fallbacks

Every load has a minimal built-in fallback, so a missing or corrupt file degrades the run instead
of crashing it. Fallbacks live next to their loader (`BaselineRunner._PURE_LLM_FALLBACK`,
`WorkflowRouter._FALLBACK_ROUTER_PROMPT`, `LLMClient._getFallbackSystemPrompt`,
`voice.commands._FALLBACK_PROMPT`, `TemplateReviser._REVISION_FALLBACK`) and are the only
prompt text in Python — they exist to survive a missing file, not to be edited.
