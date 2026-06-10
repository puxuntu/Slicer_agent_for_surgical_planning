from __future__ import annotations

from .cache import *


def get_workflow_choice(ext_name: str, parameter_name: str) -> Optional[Any]:
    """Retrieve a stored user_choice value for a workflow."""
    return _workflow_choices.get(ext_name, {}).get(parameter_name)


def get_all_workflow_choices(ext_name: str) -> Dict[str, Any]:
    """Retrieve all stored user_choice values for a workflow."""
    return dict(_workflow_choices.get(ext_name, {}))


def get_all_cli_manifests() -> List[Dict]:
    """Return all extension CLI manifests (for UI display)."""
    _ensure_cache()
    results = []
    for ext_name, ext_data in _cli_cache.items():
        manifest = ext_data["manifest"].copy()
        manifest["cli_dir"] = ext_data["dir"]
        results.append(manifest)

    # Also scan for non-validated CLIs
    base_dir = get_cli_base_dir()
    if os.path.isdir(base_dir):
        for entry in os.listdir(base_dir):
            if entry in _cli_cache:
                continue
            ext_dir = os.path.join(base_dir, entry)
            manifest_path = os.path.join(ext_dir, "manifest.json")
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        m = json.load(f)
                    m["cli_dir"] = ext_dir
                    results.append(m)
                except Exception:
                    pass
    return results


def delete_cli(extension_name: str) -> bool:
    """Delete an extension CLI directory."""
    import shutil

    base_dir = get_cli_base_dir()
    ext_dir = os.path.join(base_dir, extension_name)
    if os.path.isdir(ext_dir):
        shutil.rmtree(ext_dir)
        invalidate_cache()
        logger.info("Deleted extension CLI: %s", extension_name)
        return True
    return False


def discover_installed_extensions() -> List[Dict]:
    """
    Discover Slicer extensions from the Extension Manager, additional module
    paths, and loaded scripted modules.

    Returns a list of dicts with:
    - name: extension display name
    - module_name: Python module name
    - install_path: file system path to the extension root
    - source_path: file system path usable for source analysis
    - has_python: whether the extension has Python modules
    - cli_status: 'validated', 'draft', 'failed', or None
    """
    results = []
    seen = set()

    def _add(name, install_path, source_path, source_type="extension_manager"):
        if name in seen:
            return
        seen.add(name)

        has_python = False
        if os.path.isdir(source_path):
            for root, _dirs, files in os.walk(source_path):
                if any(f.endswith(".py") for f in files):
                    has_python = True
                break

        cli_status = None
        cli_dir = os.path.join(get_cli_base_dir(), name)
        manifest_path = os.path.join(cli_dir, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    m = json.load(f)
                cli_status = m.get("status")
                if cli_status == "validated" and m.get("manifest_version") != 2:
                    cli_status = "needs_regeneration"
            except Exception:
                pass

        results.append({
            "name": name,
            "module_name": name,
            "install_path": install_path,
            "source_path": source_path,
            "has_python": has_python,
            "cli_status": cli_status,
            "source_type": source_type,
        })

    # 1. Extensions installed via Extension Manager
    try:
        em = slicer.app.extensionsManagerModel()
        for ext_name in em.installedExtensions:
            install_path = em.extensionInstallPath(ext_name)
            _add(ext_name, install_path, install_path)
    except Exception as e:
        logger.warning("Failed to scan Extension Manager: %s", e)

    # 2. Additional module paths (loaded via Edit > Application Settings > Modules)
    try:
        settings = slicer.app.revisionUserSettings()
        raw_value = settings.value("Modules/AdditionalPaths")
        if raw_value is None:
            additionalPaths = []
        elif isinstance(raw_value, str):
            additionalPaths = [raw_value]
        elif isinstance(raw_value, (list, tuple)):
            additionalPaths = list(raw_value)
        else:
            additionalPaths = []

        # Convert relative paths to absolute
        absolute_paths = []
        for p in additionalPaths:
            abs_p = slicer.app.toSlicerHomeAbsolutePath(p)
            absolute_paths.append(abs_p)

        for mod_path in absolute_paths:
            if not os.path.isdir(mod_path):
                continue
            # Each additional path may point to a module directory directly,
            # or to a parent containing multiple module directories.
            if any(f.endswith(".py") for f in os.listdir(mod_path)):
                ext_name = os.path.basename(mod_path)
                _add(ext_name, mod_path, mod_path, source_type="additional_paths")
            else:
                # Scan subdirectories for extension-like folders
                for entry in os.listdir(mod_path):
                    subdir = os.path.join(mod_path, entry)
                    if not os.path.isdir(subdir):
                        continue
                    for f in os.listdir(subdir):
                        if f.endswith(".py"):
                            _add(entry, subdir, subdir, source_type="additional_paths")
                            break
    except Exception as e:
        logger.warning("Failed to scan additional module paths: %s", e)

    # 3. Loaded scripted modules (fallback — catches everything that's loaded)
    try:
        loaded_modules = slicer.util.moduleNames()
        for module_name in loaded_modules:
            if module_name in seen:
                continue
            try:
                mod_path = slicer.util.modulePath(module_name)
                if not mod_path or not os.path.isfile(mod_path):
                    continue
                module_dir = os.path.dirname(mod_path)
                parent_dir = os.path.dirname(module_dir)
                _add(module_name, parent_dir, module_dir, source_type="loaded_modules")
            except Exception:
                continue
    except Exception as e:
        logger.warning("Failed to scan loaded modules: %s", e)

    return results


def save_cli_package(
    extension_name: str,
    manifest: Dict,
    tool_schemas: List[Dict],
    code_generators: List[Dict],
    templates: Dict[str, str],
    prompt_fragment: str,
    generation_log_entry: Optional[Dict] = None,
) -> str:
    """
    Save a complete extension CLI package to disk.

    Args:
        extension_name: Name for the CLI directory
        manifest: Manifest dict (will be written as manifest.json)
        tool_schemas: List of OpenAI tool schema dicts
        code_generators: List of generator metadata dicts
        templates: Dict mapping template_file names to template content strings
        prompt_fragment: Markdown prompt fragment
        generation_log_entry: Optional entry to append to generation_log.json

    Returns:
        Path to the created CLI directory
    """
    # Validate extension name (prevent path traversal)
    if not extension_name or not extension_name.strip():
        raise ValueError("Extension name must not be empty.")
    if any(ch in extension_name for ch in ("/", "\\", "\x00")):
        raise ValueError(f"Invalid extension name '{extension_name}': contains path separators.")
    if ".." in extension_name:
        raise ValueError(f"Invalid extension name '{extension_name}': contains '..' traversal.")
    extension_name = extension_name.strip()

    base_dir = get_cli_base_dir()
    os.makedirs(base_dir, exist_ok=True)

    ext_dir = os.path.join(base_dir, extension_name)
    os.makedirs(ext_dir, exist_ok=True)
    os.makedirs(os.path.join(ext_dir, "templates"), exist_ok=True)

    # Write manifest
    with open(os.path.join(ext_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Write tool schemas
    with open(os.path.join(ext_dir, "tool_schemas.json"), "w", encoding="utf-8") as f:
        json.dump(tool_schemas, f, indent=2, ensure_ascii=False)

    # Write code generators
    with open(os.path.join(ext_dir, "code_generators.json"), "w", encoding="utf-8") as f:
        json.dump(code_generators, f, indent=2, ensure_ascii=False)

    # Write templates
    for tpl_name, tpl_content in templates.items():
        if tpl_name in ("workflow.json", "workflow_metadata.json", "workflow_contract.json"):
            # Workflow graph/metadata go at CLI root, not in templates/
            tpl_path = os.path.join(ext_dir, tpl_name)
        else:
            # tpl_name may already include "templates/" prefix — strip it
            clean_name = tpl_name.removeprefix("templates/")
            tpl_path = os.path.join(ext_dir, "templates", clean_name)
        os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
        with open(tpl_path, "w", encoding="utf-8") as f:
            f.write(tpl_content)

    # Write prompt fragment
    with open(os.path.join(ext_dir, "prompt_fragment.md"), "w", encoding="utf-8") as f:
        f.write(prompt_fragment)

    # Append generation log entry
    if generation_log_entry:
        log_path = os.path.join(ext_dir, "generation_log.json")
        log_entries = []
        if os.path.isfile(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    log_entries = json.load(f)
            except Exception:
                pass
        log_entries.append(generation_log_entry)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)

    # Invalidate cache so the new CLI is picked up
    invalidate_cache()

    logger.info("Saved extension CLI package: %s", ext_dir)
    return ext_dir
