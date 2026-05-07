# Repository Guidelines

## Project Structure & Module Organization

This repository is a 3D Slicer scripted extension. The main module entry point is `SlicerAIAgent.py`, which defines the Slicer module, widget, logic, and runtime orchestration. Supporting Python modules live in `SlicerAIAgentLib/`, including LLM access, retrieval tools, code validation, safe execution, conversation storage, and Slicer code templates.

Tests are in `Testing/SlicerAIAgentTest.py`. UI and packaged resources live under `Resources/`: `Resources/UI/` for Qt Designer `.ui` files, `Resources/Icons/` for extension icons, `Resources/Prompts/` for prompt text, and `Resources/Info/` for version metadata. `scripts/build_rag.py` supports building the local retrieval index.

## Build, Test, and Development Commands

- `cmake -S . -B build -DSlicer_DIR=/path/to/Slicer-build`: configure the extension against a local Slicer build.
- `cmake --build build`: build/package the scripted module resources.
- `python scripts/build_rag.py`: build or refresh the retrieval index when knowledge-base resources are present.
- Run tests from Slicer's Python console:

```python
import unittest
suite = unittest.TestLoader().loadTestsFromName("SlicerAIAgentTest")
unittest.TextTestRunner(verbosity=2).run(suite)
```

Install dependencies into Slicer's Python environment using `requirements.txt`; CMake also installs listed packages during extension setup.

## Coding Style & Naming Conventions

Use Python with 4-space indentation. Follow the existing Slicer `ScriptedLoadableModule` style: module/widget/logic/test classes use `SlicerAIAgent*` names, while helper modules in `SlicerAIAgentLib/` use PascalCase filenames matching their primary class or responsibility. Prefer explicit imports and small helper functions. Keep generated runtime artifacts and caches out of version control.

## Testing Guidelines

Tests use Python `unittest` plus Slicer's `ScriptedLoadableModuleTest`. Add new tests to `Testing/SlicerAIAgentTest.py` using `test_*` methods, and clear the MRML scene between tests when scene state is involved. Cover validator, executor, tool, and storage behavior for changes that affect generated code execution or user data.

## Commit & Pull Request Guidelines

Recent history uses conventional-style prefixes such as `chore:` and `docs:`. Keep commit messages short and imperative, for example `chore: bump version to 0.1.4` or `docs: update RAG architecture notes`.

Pull requests should include a concise description, test evidence from Slicer or CMake, linked issues when applicable, and screenshots or recordings for UI changes. Note any new dependencies, model/provider behavior changes, or migration steps.

## Security & Configuration Tips

Do not commit API keys, local model caches, generated debug logs, or retrieval indexes. Keep code-execution changes conservative: update `CodeValidator.py` and `SafeExecutor.py` together when changing allowed operations, rollback behavior, or blocked APIs.
