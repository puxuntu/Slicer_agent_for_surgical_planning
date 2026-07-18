from .common import *


class AnalyzerSchemasMixin:
    def _generate_workflow_schemas(
        self, extension_name: str, workflow_graph: Dict, logic_analysis: Dict,
    ) -> List[Dict]:
        """Generate tool schema for an interactive workflow extension."""
        steps = workflow_graph.get("steps", [])
        # Filter out removed/invalid steps
        valid_types = CANONICAL_OPERATION_TYPES
        steps = [
            s for s in steps
            if _operation_type_for_step(s) in valid_types
        ]
        step_ids = [s["step_id"] for s in steps]

        # Build enum of step IDs for the schema
        step_enum = step_ids

        # Build descriptions for each step
        step_descriptions = []
        for s in steps:
            desc = f"'{s['step_id']}': {s['description']}"
            operation_type = _operation_type_for_step(s)
            if operation_type == "user_interaction":
                desc += f" (interactive: {s.get('interaction_type', 'unknown')})"
            elif s.get("is_optional"):
                desc += " (optional)"
            step_descriptions.append(desc)

        schema = {
            "type": "function",
            "function": {
                "name": extension_name,
                "description": (
                    f"Guided interactive workflow for {extension_name}. "
                    f"Execute steps in order. Interactive steps require user 3D interaction. "
                    f"Steps: {'; '.join(step_descriptions[:10])}"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_step": {
                            "type": "string",
                            "enum": step_enum,
                            "description": "Which workflow step to execute",
                        },
                        "user_action": {
                            "type": "string",
                            "enum": ["start", "proceed", "skip", "cancel", "choice_made"],
                            "description": (
                                "Action: 'start' to begin a step, 'proceed' after user "
                                "completes interaction, 'skip' for optional steps, "
                                "'cancel' to abort workflow, 'choice_made' for user_choice steps"
                            ),
                        },
                        "choice_value": {
                            "type": ["string", "object"],
                            "description": (
                                "Value selected by the user for user_choice steps. "
                                "Required when user_action is 'choice_made'. A "
                                "multi-selection step takes a JSON object mapping "
                                "each parameter_name to its value."
                            ),
                        },
                    },
                    "required": ["workflow_step", "user_action"],
                },
            },
        }

        self.on_progress(
            "generate", "Generate Schemas And Templates",
            f"Generated interactive workflow schema with {len(steps)} steps"
        )
        return [schema]

    def _stage6_generate_schemas(
        self,
        extension_name: str,
        stage_map: Dict,
        logic_analysis: Dict,
        node_lifecycle: Optional[Dict] = None,
        cross_stage_map: Optional[Dict] = None,
        workflow_graph: Optional[Dict] = None,
    ) -> List[Dict]:
        """Generate OpenAI function-calling tool schemas."""
        self.on_progress("generate", "Generate Schemas And Templates", "Building tool definitions...")

        # Interactive workflow schema generation
        if workflow_graph:
            return self._generate_workflow_schemas(extension_name, workflow_graph, logic_analysis)

        stages = stage_map.get("stages", [])
        if not stages:
            raise RuntimeError("No stages identified — cannot generate tool schemas")

        # Determine which params are internal (output nodes, cross-stage inputs)
        internal_params = set()
        if node_lifecycle:
            for key, info in node_lifecycle.items():
                if info.get("param_role") == "output":
                    internal_params.add(key.split(":", 1)[1])
        if cross_stage_map:
            for k, stage_map_entry in cross_stage_map.items():
                if isinstance(k, str) and k.startswith("_"):
                    continue
                internal_params.update(stage_map_entry.keys())

        # Build context for LLM — only include user-facing params
        stages_desc = []
        for s in stages:
            methods_desc = []
            for m in s.get("method_details", []):
                params_desc = []
                for p in m.get("parameters", []):
                    pname = p.get("name", "")
                    ptype = p.get("type", "")
                    # Skip params the template handles internally
                    if pname in internal_params:
                        params_desc.append(
                            f"    {pname}: {ptype} (INTERNAL — template creates this)"
                        )
                    elif "vtkMRML" in ptype:
                        # Input node from user (e.g., inputVolume)
                        params_desc.append(
                            f"    {pname}: {ptype} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                        )
                    elif "progress" in pname.lower() or pname == "qd":
                        params_desc.append(
                            f"    {pname}: {ptype} (INTERNAL — auto-filled by template)"
                        )
                    else:
                        params_desc.append(
                            f"    {pname}: {ptype} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                        )
                methods_desc.append(
                    f"  Method: {m['name']}\n"
                    f"  Purpose: {m.get('purpose', '')}\n"
                    f"  Parameters:\n" + "\n".join(params_desc)
                )
            stages_desc.append(
                f"Stage: {s['stage_name']}\n"
                f"Methods:\n" + "\n".join(methods_desc)
            )

        # Determine if we need a stage parameter (multiple stages) or single tool
        has_multiple_stages = len(stages) > 1

        # Reference schema format — minimal, only user-facing params
        example_schema = textwrap.dedent("""\
{
  "type": "function",
  "function": {
    "name": "GenericExtensionWorkflow",
    "description": "...",
    "parameters": {
      "type": "object",
      "properties": {
        "stage": {"type": "string", "enum": ["segmentation", "planning", "full"], "description": "..."},
        "volume_node_name": {"type": "string", "description": "..."}
      },
      "required": ["stage"]
    }
  }
}""")

        prompt = textwrap.dedent(f"""\
Generate an OpenAI function-calling tool schema for a Slicer extension named "{extension_name}".

Extension stages:
{chr(10).join(stages_desc)}

{'The extension has multiple stages, so include a "stage" enum parameter.' if has_multiple_stages else 'The extension has a single stage, so no "stage" parameter is needed.'}""")

        prompt += textwrap.dedent("""\

IMPORTANT RULES:
- Do NOT include parameters marked as "INTERNAL" — the code template handles these automatically.
- Do NOT include any vtkMRML node parameters — the template creates/resolves them internally.
- Only include parameters that the LLM caller needs to provide: the "stage" enum, "volume_node_name", and any user-configurable options (thresholds, text prompts, flags, etc.).
- Boolean parameters with defaults should be optional with the default value.
- Filesystem paths (model_path, download_dir, output_path, etc.) MUST be optional — the template auto-discovers them. Do NOT mark them as required.
- The "required" list should be MINIMAL — only include what the LLM can reasonably fill from the user's request (e.g., text prompts). Never require paths, callbacks, or internal config.
- For text-prompted segmentation tools, include "text_prompts" (or similar) as required since the LLM derives it from the user's request (e.g., "segment the spine" → ["spine"]).

Also add an optional "volume_node_name" string parameter if the extension operates on a CT/volume input.

Reference schema format:
{example_schema}

Return a JSON array containing exactly one tool schema object.
The tool name should be based on the extension name (CamelCase, no spaces).
The description should explain what the tool does and when to use it.

Return ONLY the JSON array, no markdown fences.""")

        response = self._call_llm(prompt, call_class="generation")
        schemas = self._parse_json_response(response)

        if isinstance(schemas, dict):
            schemas = [schemas]
        if not isinstance(schemas, list) or not schemas:
            raise RuntimeError(f"Invalid tool schema response: {str(response)[:300]}")

        # Validate schema structure
        for schema in schemas:
            if "function" not in schema:
                schema["function"] = schema
            if "type" not in schema:
                schema["type"] = "function"

        # Post-process: strip any remaining vtkMRML output params from schema
        # and demote filesystem path params from required
        _path_param_patterns = ("path", "dir", "directory", "folder")
        for schema in schemas:
            func = schema.get("function", {})
            params_obj = func.get("parameters", {})
            props = params_obj.get("properties", {})
            required = params_obj.get("required", [])

            to_remove = []
            for pname, pdef in props.items():
                ptype = pdef.get("type", "")
                desc = pdef.get("description", "")
                # Remove vtkMRML node params and progress/booleans the template handles
                if "vtkMRML" in str(ptype) or "vtkMRML" in desc:
                    to_remove.append(pname)
                elif pname in internal_params:
                    to_remove.append(pname)
                # Demote filesystem path params from required → optional
                elif pname.lower() != "volume_node_name":
                    plower = pname.lower()
                    if any(pat in plower for pat in _path_param_patterns):
                        if pname in required:
                            required.remove(pname)

            for pname in to_remove:
                del props[pname]
                if pname in required:
                    required.remove(pname)

            if required:
                params_obj["required"] = required
            elif "required" in params_obj and not required:
                del params_obj["required"]

        self.on_progress(
            "generate", "Generate Schemas And Templates",
            f"Generated {len(schemas)} tool schema(s): "
            f"{[s.get('function', {}).get('name', '?') for s in schemas]}"
        )

        return schemas

    # ================================================================
    # generate: Code Template Generation (LLM + internal review)
    # ================================================================
