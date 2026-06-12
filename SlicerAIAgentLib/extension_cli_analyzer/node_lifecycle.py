from .common import *


class AnalyzerNodeLifecycleMixin:
    @staticmethod
    def _infer_stage_name(methods: List[str], index: int, total: int) -> str:
        """Infer a semantic name for a cookbook step from method names."""
        names_lower = " ".join(m.lower() for m in methods)
        if "seg" in names_lower:
            return "segmentation"
        if "plan" in names_lower or "reduc" in names_lower or "screw" in names_lower:
            return "planning"
        if "regist" in names_lower or "align" in names_lower:
            return "registration"
        if "detect" in names_lower or "find" in names_lower:
            return "detection"
        if "mesh" in names_lower or "model" in names_lower or "generat" in names_lower:
            return "generation"
        if "visual" in names_lower or "render" in names_lower or "display" in names_lower:
            return "visualization"
        if total == 1:
            return "full"
        return f"step_{index + 1}"

    @staticmethod
    def _get_call_name(node) -> str:
        """Get the dotted name of a Call node's function."""
        parts = []
        current = node.func if isinstance(node, ast.Call) else node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def _stage4_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Determine node creation mode and param role for each vtkMRML parameter."""
        self.on_progress("generate", "Generate Schemas And Templates", "Determining node creation patterns via AST...")

        node_lifecycle = {}
        methods = logic_analysis.get("methods", [])
        logic_file = logic_analysis.get("_logic_file", "")

        for method in methods:
            mname = method["name"]
            params = method.get("parameters", [])
            all_param_names = {p.get("name", "") for p in params}
            method_source = self._extract_method_source(logic_file, mname)
            method_source = textwrap.dedent(method_source or "")

            visitor = _AddNodeVisitor(all_param_names)
            try:
                tree = ast.parse(method_source)
                visitor.visit(tree)
            except SyntaxError:
                logger.warning("Could not parse method %s for lifecycle analysis", mname)

            for p in params:
                ptype = p.get("type", "")
                pname = p.get("name", "")
                if "vtkMRML" not in ptype:
                    continue
                is_output = (
                    "output" in pname.lower()
                    or "result" in pname.lower()
                    or "out" in pname.lower()
                )
                if not is_output:
                    continue

                key = f"{mname}:{pname}"
                if pname in visitor.params_added_to_scene:
                    create_mode = "CreateNodeByClass"
                    reason = f"AST: method passes '{pname}' to AddNode()"
                elif visitor.has_addnewnodebyclass:
                    create_mode = "AddNewNodeByClass"
                    reason = "AST: method uses AddNewNodeByClass for internal nodes"
                else:
                    create_mode = "AddNewNodeByClass"
                    reason = "AST: no AddNode() call targets this parameter"

                node_lifecycle[key] = {
                    "create_mode": create_mode,
                    "reason": reason,
                    "node_class": ptype,
                    "param_role": "output",
                }

        if not node_lifecycle:
            self.on_progress(
                "generate", "Generate Schemas And Templates",
                "Asking LLM about node creation patterns..."
            )
            node_lifecycle = self._llm_node_lifecycle(logic_analysis)

        self.on_progress(
            "generate", "Generate Schemas And Templates",
            f"Analyzed {len(node_lifecycle)} output nodes via AST"
        )
        return node_lifecycle

    def _llm_node_lifecycle(self, logic_analysis: Dict) -> Dict:
        """Use LLM to determine node lifecycle for ambiguous cases."""
        methods = logic_analysis.get("methods", [])
        method_summaries = []
        for m in methods:
            params_str = ", ".join(
                f"{p['name']}: {p['type']}"
                for p in m.get("parameters", [])
            )
            method_summaries.append(
                f"  {m['name']}({params_str})\n"
                f"    adds_output_to_scene: {m.get('adds_output_to_scene', 'unknown')}\n"
                f"    calls_addnode: {m.get('calls_addnode', 'unknown')}"
            )

        prompt = textwrap.dedent(f"""\
For each method below, determine whether its output node parameters should be created
with CreateNodeByClass (creates WITHOUT adding to scene) or AddNewNodeByClass (creates AND adds).

Rules:
- If the method calls slicer.mrmlScene.AddNode() on the parameter, use CreateNodeByClass.
- If the method does not add to scene itself, use AddNewNodeByClass.
- When unsure, default to CreateNodeByClass.

Methods:
{chr(10).join(method_summaries)}

Return JSON:
{{
  "nodes": [
    {{"method": "method_name", "param": "param_name", "node_class": "vtkMRML...Node", "create_mode": "CreateNodeByClass" or "AddNewNodeByClass", "reason": "why"}}
  ]
}}""")

        response = self._call_llm(prompt, call_class="analysis")
        parsed = self._parse_json_response(response)
        if not parsed:
            return {}

        result = {}
        for node in parsed.get("nodes", []):
            key = f"{node['method']}:{node['param']}"
            result[key] = {
                "create_mode": node.get("create_mode", "CreateNodeByClass"),
                "reason": node.get("reason", ""),
                "node_class": node.get("node_class", ""),
            }
        return result
