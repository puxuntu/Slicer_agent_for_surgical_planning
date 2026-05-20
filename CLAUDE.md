# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SlicerAIAgent is a 3D Slicer scripted extension that embeds an AI-powered agent. Users type natural-language requests, and the system generates, validates, and auto-executes Python code within Slicer's scene. It implements a role-composed agent pipeline: dense vector retrieval → autonomous tool calling → structured planning → AST-based security validation → safe execution → automatic self-correction.

## Build & Test Commands

```bash
# Configure against a local Slicer build
cmake -S . -B build -DSlicer_DIR=/path/to/Slicer-build
cmake --build build

# Build/refresh the FAISS vector index (requires knowledge base in Resources/Skills/slicer-skill-full/)
python scripts/build_rag.py
```

Tests run from **within Slicer's Python console** (they import `slicer`, `vtk`, `qt`, `ctk`):

```python
import unittest
suite = unittest.TestLoader().loadTestsFromName("SlicerAIAgentTest")
unittest.TextTestRunner(verbosity=2).run(suite)
```

## Architecture

### Entry Point and Module Structure

- `SlicerAIAgent.py` — Slicer ScriptedLoadableModule with three classes: `SlicerAIAgent` (module metadata), `SlicerAIAgentWidget` (Qt UI, streaming, tool loop orchestration, execution, self-correction), and `SlicerAIAgentLogic` (LLM client management, skill path resolution).
- `SlicerAIAgentLib/` — Core library package with all supporting modules.
- `Resources/` — UI files, icons, system prompt, knowledge base, FAISS vector index, and generated extension CLI tools.

### Agent Pipeline (runtime flow)

1. **User input** → `SlicerAIAgentWidget` sends prompt to background thread.
2. **Pre-Retrieval** — `LLMClient.decomposeQuery()` breaks complex prompts into sub-queries; `VectorRetriever` searches FAISS index (`SkillIndexer.py`).
3. **Tool-Calling Loop** — LLM has five tools (`SearchSymbol`, `Grep`, `ReadFile`, `VectorSearch`, `GenerateSegmentationCode`) plus dynamically loaded extension CLI tools. `SkillToolExecutor` dispatches via ripgrep/tree-sitter.
4. **Plan + Code Generation** — LLM outputs `agent_plan` JSON then a Python code block.
5. **Validation** — `CodeValidator` performs AST-based security checks (blocked modules/functions, destructive op detection).
6. **Execution** — `SafeExecutor` runs code in Slicer's `__main__` namespace via `qt.QTimer.singleShot()` on the Qt main thread. Scene rollback on failure.
7. **Self-Correction** — Isolated retry loop (up to 5 attempts) via `chatWithToolsIsolated()`, which does not pollute user conversation history.

### Threading Model

HTTP I/O runs in a background `threading.Thread`. Events are marshaled to Qt main thread via a `queue.Queue` polled every 50ms by a `QTimer`. All MRML scene access and UI updates must happen on the Qt main thread.

### Key Library Modules (`SlicerAIAgentLib/`)

| Module | Role |
|--------|------|
| `LLMClient.py` | HTTP client for OpenAI-compatible APIs (Kimi, DeepSeek, Claude, OpenAI, Qwen). Streaming, tool calling, token tracking, query decomposition, history compression. |
| `SkillTools.py` | Tool executor — ripgrep search, tree-sitter AST slicing, file reading, vector search, VoxTell segmentation code generation. |
| `SkillIndexer.py` | Dense retrieval: chunking, ONNX embedding (jina-embeddings-v2-base-code), FAISS indexing, incremental rebuild. |
| `ExtensionCLIAnalyzer.py` | 8-stage LLM pipeline for analyzing Slicer extensions and generating tool schemas + code templates. |
| `ExtensionCLILoader.py` | Auto-discovery and dynamic loading of extension CLI tools from `Resources/extension_CLI/*/`. |
| `SafeExecutor.py` | Sandboxed execution in Slicer's `__main__` namespace, stdout/stderr capture, VTK error interception, timeout, scene rollback. |
| `SceneTools.py` | Structured MRML scene introspection (`buildSceneSummary`, `getNodeProperties`). |
| `CodeValidator.py` | AST-based security validation: blocked modules/functions, allowed modules, destructive operation detection. |
| `ConversationStore.py` | Conversation history persistence (in-memory + Slicer settings + JSON export). |
| `SlicerCodeTemplates.py` | Reusable code patterns for common Slicer operations. |

### Extension CLI Pipeline

`ExtensionCLIAnalyzer.py` analyzes third-party Slicer extension source code via LLM and generates tool schemas + code templates under `Resources/extension_CLI/`. At runtime, `ExtensionCLILoader.py` discovers and loads these as additional LLM tools.

## Coding Conventions

- 4-space indentation. PascalCase filenames matching primary class/responsibility.
- Module/widget/logic/test classes use `SlicerAIAgent*` naming per Slicer's `ScriptedLoadableModule` pattern.
- Commit messages use conventional prefixes: `feat:`, `fix:`, `chore:`, `docs:`.
- Do not commit API keys, model caches, debug logs, or retrieval indexes.

## Security Considerations

When modifying execution behavior, update `CodeValidator.py` and `SafeExecutor.py` together. Code execution runs in Slicer's `__main__` namespace with blocked imports (`os`, `subprocess`, `sys`, `socket`, etc.) and blocked functions (`eval`, `exec`, `open`, `getattr`, etc.).
