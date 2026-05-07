# SlicerAIAgent

SlicerAIAgent is a 3D Slicer scripted extension that turns natural-language requests into executable Slicer Python workflows. It retrieves relevant Slicer API knowledge, plans the task, generates Python code, validates it, executes it inside Slicer, verifies observable scene changes, and attempts self-correction when something fails.

The project is an active research/prototype system. It is intended for rapid experimentation with agentic medical-imaging workflows, not unsupervised clinical use.

## What It Does

- Accepts plain-language Slicer tasks such as loading sample data, segmenting volumes, creating models, changing display settings, or running visualization workflows.
- Uses local Slicer knowledge resources through dense retrieval and tool-based search.
- Produces a structured `agent_plan` before executable code.
- Runs generated code automatically after validation.
- Records debug artifacts, timing data, role traces, generated code, and parsed plans under `logs/YYYYMMDD_HHMMSS_turnN/`.
- Supports Kimi/Moonshot, DeepSeek, and Claude-style providers through the `LLMClient` provider settings.

Example prompt:

```text
Load the example CT chest volume, threshold it from -200 to 1000, reconstruct the 3D shape, cut it with a random plane, color the two parts differently, and displace one part.
```

## Repository Layout

```text
SlicerAIAgent.py                 Main Slicer module, UI, orchestration, verification
SlicerAIAgentLib/
  LLMClient.py                   Provider API client, tool loop, agent_plan parsing
  SkillTools.py                  FindFile, SearchSymbol, Grep, ReadFile, VectorSearch
  SkillIndexer.py                Dense retrieval index builder/search backend
  CodeValidator.py               AST-based safety validation
  SafeExecutor.py                Main-thread Slicer Python execution and rollback
  ConversationStore.py           Persistent conversation history
  SlicerCodeTemplates.py         Common Slicer code snippets
Resources/
  UI/                            Qt Designer UI
  Icons/                         Extension icon
  Prompts/                       System prompt assets
Testing/SlicerAIAgentTest.py     Slicer unittest suite
scripts/build_rag.py             Dense retrieval index builder
AGENTS.md                        Contributor guide
```

Runtime logs, generated code, prompt debug files, and retrieval indexes are intentionally ignored by git.

## Agent Pipeline

SlicerAIAgent uses a role-composed single-agent pipeline. The roles are represented in prompts, logs, and the status UI, but they do not require separate LLM calls for each role.

1. **Observer** captures the user request and current MRML scene context.
2. **Retriever** uses dense pre-retrieval and optional tools (`FindFile`, `SearchSymbol`, `Grep`, `ReadFile`, `VectorSearch`) to ground important API choices.
3. **Planner** emits a required `agent_plan` JSON block with `task_summary`, `overall_confidence`, `steps`, `risk_level`, `requires_confirmation`, and `unverified_assumptions`.
4. **Programmer** emits one complete Python code block.
5. **Safety Critic** validates the plan and code before execution, blocks dangerous imports/functions, and requests confirmation for destructive operations.
6. **Executor** runs code in Slicer's Python environment on the Qt main thread.
7. **Verifier** checks optional machine-checkable expectations from the plan against before/after scene snapshots.
8. **Repairer** performs isolated self-correction when validation, execution, or verification fails.

The status label shows the active role, for example `Retriever: Searching...`, `Safety Critic: Validating code...`, or `Verifier: Verifying scene...`.

## Structured Plans and Verification

Every executable answer must contain:

````text
```agent_plan
{ ... valid JSON ... }
```

```python
# complete executable code
```
````

The `expected_scene_change` field is optional. It is only for simple deterministic checks, not a full proof of correctness. Supported check types include:

- `node_count_delta`
- `node_exists`
- `node_modified`
- `node_has_display`
- `node_name_matches`
- `layout_changed`
- `selection_changed`
- `module_entered`
- `property_true`
- `not_checked`

Unsupported checks are skipped with warnings rather than forcing unnecessary correction.

## Security Model

Generated code is treated as untrusted until it passes validation.

The validator blocks modules such as `os`, `subprocess`, `sys`, `socket`, `urllib`, `ctypes`, and `pickle`. It also blocks calls such as `eval`, `exec`, `compile`, `open`, `getattr`, `globals`, and related dynamic/runtime escape hatches.

Allowed modules include common Slicer workflow modules such as `slicer`, `vtk`, `qt`, `ctk`, `SampleData`, `numpy`, `SimpleITK`, `math`, `random`, `json`, and `re`.

Potentially destructive operations such as node removal, scene clearing, saving, writing, deleting, or exporting are flagged for confirmation. On execution failure, `SafeExecutor` attempts to roll back the MRML scene and remove nodes created by the failed attempt.

## Installation

1. Open 3D Slicer.
2. Go to **Edit > Application Settings > Modules**.
3. Add this repository root to **Additional module paths**.
4. Restart Slicer.
5. Open **Modules > AI > Slicer AI Agent**.

Dependencies listed in `requirements.txt` are installed by CMake during extension setup. For local development, install them into Slicer's Python environment rather than the system Python.

## Provider Configuration

Open the module settings panel and select a provider/model:

- **Kimi/Moonshot**: default base URL `https://api.moonshot.cn/v1`, default model `kimi-k2.5`
- **DeepSeek**: configured through the provider selector and model list
- **Claude**: supports native Anthropic-style requests when the base URL points to `api.anthropic.com`; third-party OpenAI-compatible Claude proxies are treated as OpenAI-compatible APIs

Enter an API key, save settings, and use **Test** to verify the connection.

## Retrieval Index

Dense retrieval is optional but recommended. It requires the local Slicer knowledge base at:

```text
Resources/Skills/slicer-skill-full/
```

Build or refresh the FAISS/ONNX retrieval index with:

```bash
python scripts/build_rag.py
```

The index is written to:

```text
Resources/Code_RAG/v1/
```

If the skill directory or index is missing, the agent falls back to tool-based search where possible.

## Running Tests

Tests must run inside a live 3D Slicer Python environment:

```python
import unittest
suite = unittest.TestLoader().loadTestsFromName("SlicerAIAgentTest")
unittest.TextTestRunner(verbosity=2).run(suite)
```

For syntax-only checks outside Slicer:

```bash
python3 -m py_compile SlicerAIAgent.py SlicerAIAgentLib/LLMClient.py SlicerAIAgentLib/CodeValidator.py
```

Full runtime behavior still requires Slicer because modules such as `slicer`, `vtk`, `qt`, and MRML scene APIs are not available in normal Python.

## Debug Artifacts

Each run creates a timestamped folder:

```text
logs/YYYYMMDD_HHMMSS_turnN/
```

Common files:

- `1_agent_plan.json` — parsed structured plan
- `1_code.txt` — generated executable code
- `1_first_prompt_debug.txt` — initial prompt/messages
- `1_last_prompt_debug.txt` — final generation prompt/messages
- `1_performance_log.txt` — retrieval, tool, token, validation, and execution timing
- `1_role_trace.json` — role-composed pipeline events
- `1_thinking_history.txt` — model reasoning/progress text when available

Correction attempts use suffixes such as `1_correction_1_code.txt` and `1_correction_1_agent_plan.json`.

## Development Notes

Useful commands:

```bash
cmake -S . -B build -DSlicer_DIR=/path/to/Slicer-build
cmake --build build
python scripts/build_rag.py
python3 -m py_compile SlicerAIAgent.py SlicerAIAgentLib/*.py
```

Keep generated logs, retrieval indexes, caches, API keys, and local skill data out of version control. See `AGENTS.md` for contributor guidelines.

## Current Limitations

- Generated code can still be semantically wrong even if syntax validation passes.
- Scene verification is intentionally lightweight and only checks supported deterministic expectations.
- Complex prompts may still consume many tool rounds and tokens.
- Runtime tests require an interactive Slicer environment.
- The system is a research prototype and should not be used as an autonomous clinical decision-making tool.

## Related Work

- [3D Slicer](https://www.slicer.org/)
- [slicer-skill](https://github.com/pieper/slicer-skill)
- [SlicerClaw](https://github.com/jumbojing/slicerClaw)
- [mcp-slicer](https://github.com/zhaoyouj/mcp-slicer)
- [SlicerDeveloperAgent](https://github.com/muratmaga/SlicerDeveloperAgent)
- [SlicerChat: Building a Local Chatbot for 3D Slicer](https://arxiv.org/abs/2407.11987)

## License

This project is released under the MIT License. See `LICENSE` for details.
