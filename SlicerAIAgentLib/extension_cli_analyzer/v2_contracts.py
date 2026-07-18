from .common import *
from .phases import PIPELINE_VERSION


class AnalyzerV2ContractsMixin:
    """Build and validate the strict v2 workflow contract.

    The contract is the generation source of truth.  Runtime files such as
    workflow.json and code_generators.json are projections of this structure.
    """

    def _build_workflow_contract_v2(
        self,
        extension_name: str,
        scan_result: Dict,
        cookbook_path: str,
        logic_analysis: Dict,
        workflow_graph: Dict,
    ) -> Dict:
        metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        parameter_bindings = metadata.get("parameter_bindings", {}) or {}
        operation_models = metadata.get("operation_model", {}) or {}

        steps = []
        for index, step in enumerate(workflow_graph.get("steps", []) or []):
            step_id = step.get("step_id") or f"cb_step_{index + 1}"
            operation_type = _operation_type_for_step(step)
            operations = []
            for op_index, so in enumerate(step.get("sub_operations", []) or []):
                if not isinstance(so, dict):
                    continue
                op_type = _text_or_empty(so.get("op_type"))
                operations.append({
                    "operation_id": f"{step_id}_op_{op_index + 1}",
                    "operation_type": op_type,
                    "intent": _text_or_empty(so.get("operation_intent")),
                    "description": _text_or_empty(so.get("description")),
                    "extension_method_hint": _text_or_empty(so.get("extension_method_hint")),
                    "extension_function_hint": _text_or_empty(so.get("extension_function_hint")),
                    "slicer_op_category": _text_or_empty(so.get("slicer_op_category")),
                    "slicer_api_keywords": _text_list(so.get("slicer_api_keywords", [])),
                    "parameter_name": _text_or_empty(so.get("parameter_name")),
                    "node_class": _text_or_empty(so.get("node_class")),
                    "confidence": _text_or_empty(so.get("confidence")),
                    "required": not bool(so.get("is_optional")),
                })

            parameter_roles = {}
            for role, binding in parameter_bindings.items():
                if not isinstance(binding, dict):
                    continue
                methods = set(_text_list(binding.get("methods", [])))
                step_methods = set(_text_list(step.get("methods", [])))
                method_name = _text_or_empty(step.get("method_name"))
                if method_name:
                    step_methods.add(method_name)
                if not methods.intersection(step_methods) and role not in json.dumps(step):
                    continue
                parameter_roles[role] = {
                    "role": role,
                    "node_class": _text_or_empty(binding.get("node_class")),
                    "value_types": _text_list(binding.get("value_types", [])),
                    "accesses": _text_list(binding.get("accesses", [])),
                    "keywords": _text_list(binding.get("keywords", [])),
                }

            interaction = {}
            if operation_type == "user_interaction" or any(
                op.get("operation_type") == "user_interaction" for op in operations
            ):
                descriptor = step.get("interaction_descriptor") or {}
                node_class = (
                    step.get("node_class")
                    or descriptor.get("node_class")
                    or next((op.get("node_class") for op in operations if op.get("operation_type") == "user_interaction"), "")
                )
                interaction = {
                    "interaction_kind": _text_or_empty(step.get("interaction_kind") or descriptor.get("interaction_kind")),
                    "interaction_type": _derive_interaction_type(node_class),
                    "node_class": _text_or_empty(node_class),
                    "placement_instructions": _text_or_empty(
                        step.get("placement_instructions") or descriptor.get("placement_instructions")
                    ),
                    "interaction_owner": _text_or_empty(step.get("interaction_owner") or descriptor.get("interaction_owner")),
                    "placement_starter_method": _text_or_empty(
                        step.get("placement_starter_method") or descriptor.get("placement_starter_method")
                    ),
                    "created_node_source": _text_or_empty(step.get("created_node_source") or descriptor.get("created_node_source")),
                }

            steps.append({
                "step_id": step_id,
                "index": index,
                "description": _text_or_empty(step.get("description")),
                "operation_type": operation_type,
                "depends_on": _text_list(step.get("depends_on", [])),
                "is_optional": bool(step.get("is_optional", False)),
                "method_name": _text_or_empty(step.get("method_name")),
                "extension_function_name": _text_or_empty(step.get("extension_function_name")),
                "operations": operations,
                "parameter_roles": parameter_roles,
                "interaction": interaction,
                "operation_model": step.get("operation_model") or operation_models.get(step_id, {}),
                "template_contract": {
                    "template_file": step.get("code_template", ""),
                    "pre_template_file": step.get("pre_template", ""),
                    "post_template_file": step.get("post_template", ""),
                    # A review_op is a pure human checkpoint -- no code ever runs, so
                    # a template is not merely optional but structurally absent.
                    "required": (operation_type in CANONICAL_OPERATION_TYPES
                                 and operation_type != "review_op"),
                    "allow_instruction_only": bool(
                        operation_type == "user_interaction"
                        and interaction
                        and interaction.get("interaction_kind")
                        in ("view_adjustment", "module_tool_interaction")
                    ),
                },
            })

        contract = {
            "schema_version": 2,
            "pipeline_version": PIPELINE_VERSION,
            "extension_name": extension_name,
            "extension_module_name": os.path.splitext(
                os.path.basename(scan_result.get("entry_module", ""))
            )[0],
            # logic_class is None (not merely absent) for a wizard-style module.
            "logic_class_name": (scan_result.get("logic_class") or {}).get("class_name", ""),
            "source_path": scan_result.get("source_path", ""),
            "cookbook_file": os.path.basename(cookbook_path or ""),
            "steps": steps,
            "metadata_refs": {
                "parameter_bindings": sorted(parameter_bindings.keys()),
                "operation_model_steps": sorted(operation_models.keys()),
            },
        }
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["workflow_contract_version"] = 2
            self._workflow_metadata["workflow_contract_summary"] = {
                "step_count": len(steps),
                "operation_types": sorted({
                    step.get("operation_type", "")
                    for step in steps
                    if step.get("operation_type")
                }),
            }
        return contract

    @staticmethod
    def _workflow_contract_to_json(contract: Dict) -> str:
        return json.dumps(contract or {}, indent=2, ensure_ascii=False)

    def _canonicalize_workflow_graph_v2(self, workflow_graph: Dict) -> Dict:
        clean = dict(workflow_graph or {})
        clean_steps = []
        for step in clean.get("steps", []) or []:
            if not isinstance(step, dict):
                continue
            item = dict(step)
            operation_type = _operation_type_for_step(item)
            item["operation_type"] = operation_type
            item.pop("op_type", None)
            item.pop("step_type", None)
            clean_steps.append(item)
        clean["schema_version"] = 2
        clean["steps"] = clean_steps
        return clean

    def _canonicalize_generators_v2(self, generators: List[Dict]) -> List[Dict]:
        canonical = []
        for gen in generators or []:
            item = dict(gen)
            operation_type = _text_or_empty(item.get("operation_type") or item.get("op_type") or item.get("step_type"))
            item["operation_type"] = operation_type
            item.pop("op_type", None)
            item.pop("step_type", None)
            canonical.append(item)
        return canonical
