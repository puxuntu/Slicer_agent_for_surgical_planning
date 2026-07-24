from .common import *

# CJK fullwidth ASCII range (U+FF01–U+FF5E) → ASCII (U+0021–U+007E)
_FULLWIDTH_TO_ASCII = str.maketrans(
    {chr(i): chr(i - 0xFEE0) for i in range(0xFF01, 0xFF5F)}
)

_GETATTR_LITERAL_RE = _re.compile(
    r'\bgetattr\s*\(\s*([^,]+?)\s*,\s*([\'"])([A-Za-z_]\w*)\2\s*\)'
)
# Matches setattr(obj, 'attr', <simple_value>) where the value has no
# nested parentheses.  Complex expressions like setattr(o, 'a', f(x))
# are left for the auto-revise LLM to handle.
_SETATTR_LITERAL_RE = _re.compile(
    r'\bsetattr\s*\(\s*([^,]+?)\s*,\s*([\'"])([A-Za-z_]\w*)\2\s*,\s*([^)]+?)\s*\)'
)


class AnalyzerTemplateHelpersMixin:
    # Cap on chains listed in generation prompts; the omission note keeps the
    # truncation visible to the LLM instead of silently implying completeness.
    _PROVEN_CHAIN_PROMPT_LIMIT = 250

    @staticmethod
    def _collect_source_api_chains(*sources) -> List[str]:
        """Extract `slicer.*` attribute/call chains observed in source code.

        These chains are evidence-backed: the extension (or a grounded
        snippet) actually uses them, so a generated template may use them
        without inventing APIs. Intermediate calls are marked with `()`
        (e.g. ``slicer.app.layoutManager().setLayout``).
        """
        chains = set()
        for source in sources:
            if isinstance(source, dict):
                source = source.get("code") or source.get("template") or ""
            if not source or not isinstance(source, str):
                continue
            try:
                tree = ast.parse(textwrap.dedent(source))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Attribute):
                    continue
                parts = []
                cur = node
                while True:
                    if isinstance(cur, ast.Attribute):
                        parts.append(cur.attr)
                        cur = cur.value
                    elif isinstance(cur, ast.Call):
                        func = cur.func
                        if isinstance(func, ast.Attribute):
                            parts.append(func.attr + "()")
                            cur = func.value
                        else:
                            parts = []
                            break
                    elif isinstance(cur, ast.Name):
                        parts.append(cur.id)
                        break
                    else:
                        parts = []
                        break
                if parts and parts[-1] == "slicer" and len(parts) >= 3:
                    chains.add(".".join(reversed(parts)))
        return sorted(chains)

    @staticmethod
    def _collect_extension_runtime_constants(*sources) -> List[str]:
        """Extension-defined runtime attributes: `slicer.X = <value>` at import.

        These are extension-registered constants (custom layout IDs, singleton
        tags, ...) that EXIST at runtime once the extension is loaded — the
        evidence-backed way to reference extension artifacts instead of
        fabricating names or IDs.
        """
        constants = {}
        for source in sources:
            if not source or not isinstance(source, str):
                continue
            try:
                tree = ast.parse(textwrap.dedent(source))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                for target in node.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "slicer"
                    ):
                        try:
                            preview = ast.unparse(node.value)[:60]
                        except Exception:
                            value = node.value
                            if isinstance(value, ast.Constant):
                                preview = repr(value.value)[:60]
                            elif hasattr(ast, "Num") and isinstance(value, ast.Num):
                                preview = repr(value.n)[:60]
                            elif hasattr(ast, "Str") and isinstance(value, ast.Str):
                                preview = repr(value.s)[:60]
                            else:
                                preview = "..."
                        constants[f"slicer.{target.attr}"] = preview
        return [f"{name} = {value}" for name, value in sorted(constants.items())]

    def _evidence_source_texts(self) -> List[str]:
        """All extension source texts usable as API evidence.

        The FULL entry module is included (not just the Logic class): module-
        level code is where extensions register layouts, set slicer.<Const>
        attributes, and define helper functions.
        """
        sources = []
        logic_analysis = getattr(self, "_last_logic_analysis", None) or {}
        logic_file = logic_analysis.get("_logic_file", "")
        if logic_file and os.path.isfile(logic_file):
            try:
                with open(logic_file, "r", encoding="utf-8", errors="ignore") as f:
                    sources.append(f.read())
            except Exception:
                pass
        if not sources and logic_analysis.get("_logic_source"):
            sources.append(logic_analysis["_logic_source"])
        sources.extend((getattr(self, "_slicer_op_templates", {}) or {}).values())
        return sources

    def _proven_api_chain_block(self) -> str:
        """Prompt section constraining state-changing Slicer calls to evidence.

        Evidence-first generation: instead of generate→probe→repair, the
        generator is told up front which API chains are evidence-backed and
        must emit a MISSING_EVIDENCE sentinel (a blocking validator signal
        that routes to re-grounding) when the needed API is not evidenced.
        """
        chains = getattr(self, "_proven_api_chains", None)
        if chains is None:
            sources = self._evidence_source_texts()
            chains = self._collect_source_api_chains(*sources)
            self._proven_api_chains = chains
            self._extension_runtime_constants = (
                self._collect_extension_runtime_constants(*sources)
            )
        if not chains:
            return ""
        shown = chains[: self._PROVEN_CHAIN_PROMPT_LIMIT]
        note = (
            ""
            if len(chains) <= self._PROVEN_CHAIN_PROMPT_LIMIT
            else f"\n(... {len(chains) - len(shown)} more evidenced chains omitted)"
        )
        # Core-UI method-name evidence is a SEPARATE subsection: these are bare
        # method names (not slicer.* chains) and must not loosen the chain-only
        # rule for slicer.* receivers.
        ui_subsection = ""
        ui_methods = self._core_ui_evidence_methods()
        if ui_methods:
            ui_subsection = (
                "\n\nCORE-UI EVIDENCED SLICER METHOD NAMES (from Slicer core UI "
                "analysis — method names only, receiver class NOT proven here; "
                "verify the receiver from the cited implementation evidence "
                "before use):\n"
                + "\n".join(f"- {name}" for name in ui_methods)
            )
        constants = getattr(self, "_extension_runtime_constants", None) or []
        if constants:
            ui_subsection += (
                "\n\nEXTENSION-DEFINED RUNTIME CONSTANTS (the extension sets "
                "these `slicer.<Name>` attributes at module import — they exist "
                "at runtime once the extension is loaded; reference them instead "
                "of fabricating names, IDs, or values):\n"
                + "\n".join(f"- {item}" for item in constants[:20])
            )
        return (
            "\nEVIDENCE-BACKED SLICER API CHAINS (observed in the extension's own "
            "source or grounded snippets — safe to use):\n"
            + "\n".join(f"- {chain}" for chain in shown)
            + note
            + ui_subsection
            + "\n\nFor STATE-CHANGING calls on `slicer.*` receivers, use only chains "
            "evidenced above, in the supplied method source, or in the provided "
            "evidence context. If the operation requires a Slicer API that is not "
            "evidenced, output a single line `# MISSING_EVIDENCE: <describe the "
            "missing API>` instead of inventing a call.\n"
        )

    def _core_ui_evidence_methods(self) -> List[str]:
        """Method names evidenced by core-UI controls matching the cookbook.

        Computed once per run from the cookbook step descriptions against the
        UI pre-analysis index; empty when artifacts are absent. Cached on
        self._ui_evidence_methods (reset together with _proven_api_chains).
        """
        methods = getattr(self, "_ui_evidence_methods", None)
        if methods is not None:
            return methods
        methods = []
        try:
            from ..UIControlIndex import get_index
            index = get_index()
            cookbook = getattr(self, "_cookbook_def", None)
            steps = getattr(cookbook, "steps", None) if cookbook is not None else None
            if index is not None and steps:
                query = " ".join(
                    str(getattr(step, "description", "") or "") for step in steps
                )
                names = set()
                for match in index.match(query, top_k=10):
                    names.update(match.get("record", {}).get("api_footprints") or [])
                methods = sorted(names)[:40]
        except Exception:
            logger.debug("Core-UI evidence method lookup failed", exc_info=True)
        self._ui_evidence_methods = methods
        return methods

    @staticmethod
    def _is_markup_node_class(node_class: str) -> bool:
        """Return True for MRML Markups nodes that support placement/control points."""
        return _text_or_empty(node_class).startswith("vtkMRMLMarkups")

    @staticmethod
    def _python_comment_block(text: str, prefix: str = "# ") -> List[str]:
        """Convert arbitrary multi-line text into valid Python comment lines."""
        lines = []
        for raw_line in _text_or_empty(text).splitlines() or [""]:
            line = raw_line.strip()
            lines.append(f"{prefix}{line}" if line else prefix.rstrip())
        return lines

    def _template_header_lines(self, extension_name: str, step: Dict, phase: str = "") -> List[str]:
        """Return a Python-safe multi-line template header for a workflow step."""
        step_id = step.get("step_id", "")
        description = step.get("description", step_id)
        suffix = f" ({phase})" if phase else ""
        header_text = f"--- {extension_name}: {description}{suffix} ---"
        return self._python_comment_block(header_text)

    @staticmethod
    def _emit_module_enter_precondition(module_name: str) -> List[str]:
        """Emit Python lines that ensure the extension's Slicer module is active.

        Why: extension logic methods assume module.enter() has run (parameter
        node init, observers, UI bindings). The agent runtime imports the
        Logic class and calls methods directly, bypassing the module widget
        lifecycle, so enter() never fires. slicer.util.selectModule() triggers
        the full lifecycle (instantiate widget, call enter()). The guard is
        idempotent — cheap name check skips the call when already active.
        """
        if not module_name:
            return []
        return [
            "# precondition:begin",
            "# Ensure the extension module is active so module.enter() has run.",
            "_active_module_name = slicer.util.selectedModule()",
            f"if _active_module_name != {module_name!r}:",
            "    try:",
            f"        slicer.util.selectModule({module_name!r})",
            "    except Exception as _module_enter_error:",
            f"        print(f\"Warning: could not activate module {module_name!r}: {{_module_enter_error}}\")",
            "# precondition:end",
            "",
        ]

    def _inject_module_enter_precondition(self, code: str, module_name: str) -> str:
        """Insert the shared lifecycle precondition after imports."""
        if not code or "# precondition:begin" in code or not module_name:
            return code
        lines = code.splitlines()
        if not any(line.strip() == "import slicer" for line in lines):
            lines.insert(0, "import slicer")
        insert_at = 0
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")) or not stripped or stripped.startswith("#"):
                insert_at = index + 1
                continue
            break
        block = self._emit_module_enter_precondition(module_name)
        return "\n".join(lines[:insert_at] + block + lines[insert_at:]).rstrip() + "\n"

    @staticmethod
    def _repair_multiline_comment_headers(code: str) -> str:
        """Prefix accidentally split template-header continuation lines as comments."""
        repaired = []
        in_header = False
        for line in _text_or_empty(code).splitlines():
            stripped = line.strip()
            if stripped.startswith("# ---") and not stripped.endswith("---"):
                in_header = True
                repaired.append(line)
                continue
            if in_header:
                if stripped and not stripped.startswith("#"):
                    indent = line[:len(line) - len(line.lstrip())]
                    repaired.append(f"{indent}# {stripped}")
                else:
                    repaired.append(line)
                if stripped.endswith("---"):
                    in_header = False
                continue
            repaired.append(line)
        if code.endswith("\n"):
            return "\n".join(repaired) + "\n"
        return "\n".join(repaired)

    @staticmethod
    def _placement_mode_from_source(source: str) -> str:
        """Infer the placement mode a source snippet explicitly enters."""
        source = source or ""
        if "SwitchToSinglePlaceMode" in source:
            return "single"
        if "SwitchToPersistentPlaceMode" in source:
            return "persistent"
        if "StartPlaceMode" in source or "SetPlaceModeEnabled" in source:
            return "unknown"
        return "none"

    def _placement_starter_info(self, method_name: str) -> Dict:
        """Return source-derived placement-starter metadata for a method."""
        if not method_name:
            return {}
        return self._placement_starter_methods.get(method_name) or {}

    @staticmethod
    def _is_repeat_interaction_step(step: Dict) -> bool:
        """Return True when this interaction step is controlled by a repeat group."""
        repeat_group = step.get("repeat_group") or {}
        return bool(
            repeat_group
            and repeat_group.get("interaction_step")
            and repeat_group.get("interaction_step") == step.get("step_id")
        )

    def _interaction_object_name(self, step: Dict) -> str:
        """Return a short generic object name for user-facing placement text."""
        interaction_type = _text_or_empty(step.get("interaction_type", "")).lower()
        if interaction_type and interaction_type != "unknown":
            return interaction_type
        node_class = self._step_interaction_node_class(step)
        mapping = {
            "vtkMRMLMarkupsPlaneNode": "plane",
            "vtkMRMLMarkupsCurveNode": "curve",
            "vtkMRMLMarkupsLineNode": "line",
            "vtkMRMLMarkupsFiducialNode": "point",
        }
        return mapping.get(node_class, "placement")

    def _normalize_repeat_interaction_instructions(self, step: Dict) -> None:
        """Make repeated interaction steps describe one runtime iteration only."""
        if not self._is_repeat_interaction_step(step):
            return
        object_name = self._interaction_object_name(step)
        if object_name == "placement":
            instruction = "Complete this placement, then click Done."
        else:
            instruction = f"Place this {object_name}, then click Done."
        step["placement_instructions"] = instruction
        for so in step.get("sub_operations", []) or []:
            if so.get("op_type") == "user_interaction":
                so["placement_instructions"] = instruction

    def _interaction_instructions_for_template(self, step: Dict) -> str:
        """Return user-facing instructions with repeat semantics applied."""
        if self._is_repeat_interaction_step(step):
            object_name = self._interaction_object_name(step)
            if object_name == "placement":
                return "Complete this placement, then click Done."
            return f"Place this {object_name}, then click Done."
        return self._sanitize_interaction_instruction(
            step.get("placement_instructions"),
            fallback=step.get("description", ""),
        )

    @staticmethod
    def _sanitize_interaction_instruction(value: Any, fallback: str = "") -> str:
        """Return safe user-facing interaction text.

        LLM decomposition can leave optional instruction fields as None or the
        literal string "None". Emitting that directly produces bad workflow UI
        text such as "Please None"; fall back to the cookbook step text instead.
        """
        text = _text_or_empty(value).strip()
        if text.lower() in {"", "none", "null", "n/a", "na", "undefined"}:
            text = _text_or_empty(fallback).strip()
        if text.lower() in {"", "none", "null", "n/a", "na", "undefined"}:
            text = "Complete this interaction, then click Done."
        return text

    # Number/quantifier words that name a control-point count in placement
    # instructions (e.g. "place one point", "select a landmark").
    _POINT_COUNT_WORDS = {
        "a": 1, "an": 1, "one": 1, "single": 1, "two": 2, "three": 3,
        "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10,
    }

    def _expected_interaction_point_count(self, step: Dict) -> Optional[int]:
        """Infer how many control points a placement step expects the user to add.

        Driven purely by the step's own natural-language fields so it stays
        general across extensions: returns the integer count when the text
        unambiguously names one (e.g. "select a point", "place one point",
        "click two landmarks"), or None when the count is unbounded / unknown
        (e.g. "draw a curve", "add points").
        """
        ui_guidance = step.get("ui_guidance") or {}
        texts = [
            step.get("description"),
            step.get("placement_instructions"),
            ui_guidance.get("instruction"),
            ui_guidance.get("title"),
        ]
        for so in step.get("sub_operations", []) or []:
            if isinstance(so, dict):
                texts.append(so.get("description"))
                texts.append(so.get("placement_instructions"))
        blob = " ".join(_text_or_empty(t) for t in texts).lower()
        if not blob.strip():
            return None
        # A quantified reference to a point/fiducial/landmark/marker, allowing up
        # to two adjective words in between (e.g. "one glenoid center point").
        m = _re.search(
            r"\b(a|an|one|single|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
            r"(?:\w+\s+){0,2}?(point|fiducial|landmark|marker)(s?)\b",
            blob,
        )
        if not m:
            return None
        token = m.group(1)
        count = self._POINT_COUNT_WORDS.get(token)
        if count is None:
            try:
                count = int(token)
            except ValueError:
                return None
        noun_is_plural = bool(m.group(3))
        # "a/one point" (singular noun) == 1; an article "a" in front of a plural
        # noun ("a few points") is ambiguous, so don't claim a count.
        if count == 1 and noun_is_plural:
            return None
        return count

    # Markups classes with a fixed, small required control-point count: placement
    # completes deterministically (ROI box = 2 corners, line = 2, angle = 3), so
    # single place mode is correct — Slicer auto-exits to view-transform once the
    # required points are placed, matching the native Markups create-button UX.
    # Open-ended markups (curve, fiducial list) stay persistent so the user keeps
    # clicking until Done.
    _FIXED_POINT_MARKUP_CLASSES = frozenset({
        "vtkMRMLMarkupsROINode",
        "vtkMRMLMarkupsLineNode",
        "vtkMRMLMarkupsAngleNode",
    })

    def _markup_uses_single_place_mode(self, node_class: str) -> bool:
        return _text_or_empty(node_class) in self._FIXED_POINT_MARKUP_CLASSES

    def _placement_mode_policy(self, step: Dict, starter_info: Optional[Dict] = None) -> Dict:
        """Decide how generated code should enter Markups placement mode."""
        owner = step.get("interaction_owner", "")
        starter_info = starter_info or {}
        # An ADJUST-existing-markup step (Stage 4 set creates_node False +
        # requires_place_mode False) drags the handles of a markup a prior step
        # already fully created. It must NOT enter placement mode (that re-places the
        # control points = a NEW box); it just enables the markup's interaction
        # handles so the user can resize it. Highest priority — checked before the
        # extension-starter / repeat branches.
        if step.get("creates_node") is False and step.get("requires_place_mode") is False:
            return {
                "should_set_active_list": True,
                "should_enter_placement_mode": False,
                "placement_mode": None,
                "enable_handles": True,
                "reason": "adjust_existing_markup_no_placement",
            }
        # A step that expects exactly one control point — or places a fixed-count
        # markup (ROI/line/angle) — should use single place mode so Slicer
        # auto-exits after the required clicks instead of letting the user keep
        # adding points. Derived from the step's own text/node class, so it stays
        # general across extensions (never keyed on a specific step id).
        wants_single_point = (
            self._expected_interaction_point_count(step) == 1
            or self._markup_uses_single_place_mode(step.get("node_class", ""))
        )
        if owner in ("extension_method", "previous_extension_method"):
            if starter_info.get("starts_markup_placement"):
                return {
                    "should_set_active_list": False,
                    "should_enter_placement_mode": False,
                    "placement_mode": None,
                    "reason": "extension_starter_already_controls_placement",
                }
            use_single = self._is_repeat_interaction_step(step) or wants_single_point
            return {
                "should_set_active_list": True,
                "should_enter_placement_mode": True,
                "placement_mode": "single" if use_single else "persistent",
                "reason": "extension_starter_did_not_enter_placement",
            }
        if self._is_repeat_interaction_step(step):
            return {
                "should_set_active_list": True,
                "should_enter_placement_mode": True,
                "placement_mode": "single",
                "reason": "repeat_group_one_item_per_runtime_iteration",
            }
        return {
            "should_set_active_list": True,
            "should_enter_placement_mode": True,
            "placement_mode": "single" if wants_single_point else "persistent",
            "reason": "single_point_step" if wants_single_point else "runtime_template_controls_placement",
        }

    @staticmethod
    def _placement_mode_code(policy: Dict) -> List[str]:
        """Return Python lines that enter the policy-selected placement mode."""
        if not policy.get("should_enter_placement_mode"):
            return []
        mode = policy.get("placement_mode")
        if mode == "single":
            return ["    interactionNode.SwitchToSinglePlaceMode()"]
        return ["    interactionNode.SwitchToPersistentPlaceMode()"]

    def _generate_existing_placement_pre_template(
        self, extension_name, step, starter_method,
    ) -> str:
        """Reuse the markup node created by the previous placement-starter step."""
        step_id = step.get("step_id", "")
        node_class = step.get("node_class", "vtkMRMLMarkupsFiducialNode")
        instructions = self._interaction_instructions_for_template(step)
        node_var = f"_{extension_name.lower()}_{step_id}_id"
        starter_info = self._placement_starter_info(starter_method)
        policy = self._placement_mode_policy(step, starter_info)

        lines = [
            *self._template_header_lines(extension_name, step, "Setup"),
            "import slicer",
            "from SlicerAIAgentLib.workflow_state import remember_interaction_node",
            "",
            (f"# Reuse the markup node created by {starter_method}() in the previous step."
             if starter_method
             else "# Reuse the markup node created by a previous step (do not create a duplicate)."),
            f"nodes = slicer.mrmlScene.GetNodesByClass(\"{node_class}\")",
            "node = None",
            "for i in range(nodes.GetNumberOfItems() - 1, -1, -1):",
            "    candidate = nodes.GetItemAsObject(i)",
            "    if candidate is not None:",
            "        node = candidate",
            "        break",
            "if node is None:",
            f"    raise RuntimeError(\"No {node_class} found from previous placement step.\")",
            "",
            "# A node made by a plain AddNewNodeByClass has no display node, so it",
            "# is neither visible nor interactive — create one before placement.",
            "displayNode = node.GetDisplayNode()",
            "if displayNode is None:",
            "    node.CreateDefaultDisplayNodes()",
            "    displayNode = node.GetDisplayNode()",
            "if displayNode is not None:",
            "    displayNode.SetVisibility(True)",
        ]
        if policy.get("enable_handles"):
            # Adjust an existing markup: turn on its interaction handles so the user
            # can DRAG the boundaries, and do NOT enter placement mode (which would
            # re-place the control points = draw a new box). Guarded — not every
            # markup display node exposes every handle setter.
            lines.extend([
                "# Enable interaction handles for adjusting the existing markup.",
                "if displayNode is not None:",
                "    try:",
                "        displayNode.SetHandlesInteractive(True)",
                "        displayNode.SetTranslationHandleVisibility(True)",
                "        displayNode.SetScaleHandleVisibility(True)",
                "        displayNode.SetRotationHandleVisibility(True)",
                "    except Exception:",
                "        pass",
            ])
        if policy.get("should_set_active_list"):
            lines.append("slicer.modules.markups.logic().SetActiveListID(node)")
        if policy.get("should_enter_placement_mode"):
            lines.extend([
                "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
                "if interactionNode is not None:",
                *self._placement_mode_code(policy),
            ])
        lines.extend([
            f"{node_var} = node.GetID()",
            (
                "remember_interaction_node("
                f"_workflow_runtime_extension, _workflow_runtime_id, \"{step_id}\", "
                f"{node_var}, _workflow_runtime_repeat_index)"
            ),
            "",
            f"print(\"[{extension_name}] Please {self._sanitize_interaction_instruction(instructions, fallback=step.get('description', ''))}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
        ])
        return "\n".join(lines) + "\n"

    def _generate_view_adjustment_pre_template(self, extension_name, step) -> str:
        """Generate setup for interactions that do not create markups nodes."""
        step_id = step.get("step_id", "")
        instructions = self._sanitize_interaction_instruction(
            step.get("placement_instructions"),
            fallback=step.get("description", ""),
        )
        lines = [
            *self._template_header_lines(extension_name, step, "Setup"),
            "import slicer",
            "",
            "# This step is a view adjustment, not a Markups placement.",
            f"print(\"[{extension_name}] Please {instructions}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_view_adjustment_post_template(self, extension_name, step) -> str:
        """Generate completion code for non-markup interactions."""
        step_id = step.get("step_id", "")
        lines = [
            *self._template_header_lines(extension_name, step, "Done"),
            "import slicer",
            "",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "if interactionNode is not None:",
            "    interactionNode.SwitchToViewTransformMode()",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' view adjustment completed.\")",
        ]
        return "\n".join(lines) + "\n"

    def _module_tool_interaction_preamble(self, step) -> str:
        """Return the CREATION-FREE code that re-binds the active module tool/effect
        just before the user interacts with it, delegated to the module's session
        driver (via the step's recorded ``module_context``). Empty when the module
        has no interactive-tool driver — then the pre-template is a plain wait."""
        module = _text_or_empty(step.get("module_context"))
        if not module:
            return ""
        try:
            from .module_sessions import driver_for_module
            driver = driver_for_module(module)
        except Exception:
            driver = None
        if driver is None:
            return ""
        try:
            return driver.interaction_preamble(
                active_effect=_text_or_empty(step.get("module_tool_context")) or None,
            ) or ""
        except Exception:
            return ""

    def _generate_module_tool_interaction_pre_template(self, extension_name, step) -> str:
        """Pre-template for a module_tool_interaction step: the user interacts
        DIRECTLY with an already-active module tool/effect (e.g. clicking an island
        in a slice view while the Segment Editor's Islands 'Keep selected island'
        effect is active). It re-asserts the tool is bound to its target, then waits
        for the user — it creates NO Markups node and enters NO placement mode, so
        the active effect (not a fiducial) consumes the clicks. Mirrors the
        view_adjustment pre-template's node-less wait, plus the tool re-bind."""
        instructions = self._sanitize_interaction_instruction(
            step.get("placement_instructions"),
            fallback=step.get("description", ""),
        )
        preamble = self._module_tool_interaction_preamble(step)
        lines = [
            *self._template_header_lines(extension_name, step, "Setup"),
            "import slicer",
            "",
            "# In-tool interaction: the active module tool/effect consumes the view",
            "# clicks itself; do NOT create a Markups node or enter placement mode.",
        ]
        if preamble:
            lines.extend(["", preamble.rstrip("\n"), ""])
        lines.extend([
            f"print(\"[{extension_name}] Please {instructions}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
        ])
        return "\n".join(lines) + "\n"

    def _generate_module_tool_interaction_post_template(self, extension_name, step) -> str:
        """Completion code for a module_tool_interaction step. The active effect
        already committed the edit on each slice-view click, so there is no node to
        resolve and no placement mode to exit — just report completion."""
        step_id = step.get("step_id", "")
        lines = [
            *self._template_header_lines(extension_name, step, "Done"),
            "import slicer",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' in-tool interaction completed.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_pre_interaction_template(
        self, extension_name, step, logic_class_name, module_name,
    ) -> str:
        """Generate the pre-interaction template for an interactive step."""
        interaction_type = step.get("interaction_type", "unknown")
        node_class = step.get("node_class", "vtkMRMLMarkupsFiducialNode")
        instructions = self._interaction_instructions_for_template(step)
        node_name = step["step_id"].replace("_", " ").title()
        min_points = step.get("min_control_points", 0)
        policy = self._placement_mode_policy(step)

        lines = [
            *self._template_header_lines(extension_name, step, "Setup"),
            "import slicer",
            "from SlicerAIAgentLib.workflow_state import remember_interaction_node",
            "",
            "# Create the markup node for user interaction",
            f"node = slicer.mrmlScene.AddNewNodeByClass(\"{node_class}\", \"{node_name}\")",
            "displayNode = node.GetDisplayNode()",
            "if displayNode is not None:",
            "    displayNode.SetVisibility(True)",
            "",
            f"print(\"[{extension_name}] Please {instructions}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
            "",
            "# Enter placement mode",
        ]
        if policy.get("should_set_active_list"):
            lines.append("slicer.modules.markups.logic().SetActiveListID(node)")
        if policy.get("should_enter_placement_mode"):
            lines.extend([
                "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
                "if interactionNode is not None:",
                *self._placement_mode_code(policy),
            ])
        lines.extend([
            "",
            f"_{extension_name.lower()}_{step['step_id']}_id = node.GetID()",
            (
                "remember_interaction_node("
                f"_workflow_runtime_extension, _workflow_runtime_id, \"{step['step_id']}\", "
                f"_{extension_name.lower()}_{step['step_id']}_id, _workflow_runtime_repeat_index)"
            ),
        ])

        return "\n".join(lines) + "\n"

    def _generate_post_interaction_template(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> str:
        """Generate the post-interaction template for an interactive step."""
        # Try LLM-assisted generation first
        llm_template = self._generate_post_interaction_template_llm(
            extension_name, step, logic_class_name, module_name, logic_analysis,
        )
        if llm_template:
            return llm_template

        # Fallback: static template
        min_points = step.get("min_control_points", 0)
        node_var = f"_{extension_name.lower()}_{step['step_id']}_id"

        lines = [
            *self._template_header_lines(extension_name, step, "Process"),
            "import slicer",
            "from SlicerAIAgentLib.workflow_state import resolve_interaction_node",
            "",
            (
                "node = resolve_interaction_node("
                f"_workflow_runtime_extension, _workflow_runtime_id, \"{step['step_id']}\", "
                f"\"{step.get('node_class', '')}\", _workflow_runtime_repeat_index)"
            ),
            "if node is None:",
            f"    node = slicer.mrmlScene.GetNodeByID({node_var})",
            "if node is None:",
            f"    raise RuntimeError(\"Node not found for step '{step['step_id']}'\")",
            "",
        ]

        if min_points > 0:
            lines += [
                "# Validate user input",
                "numPoints = node.GetNumberOfControlPoints()",
                f"if numPoints < {min_points}:",
                f"    raise RuntimeError(\"Need at least {min_points} control points, got %d. Please add more.\" % numPoints)",
                "",
            ]

        if step.get("reactive_chains"):
            for chain in step["reactive_chains"]:
                lines.append(f"# Reactive chain: {chain.get('recompute_description', '')}")

        parameter_role = (
            step.get("parameter_role")
            or (step.get("interaction_binding") or {}).get("parameter_name", "")
        )
        if parameter_role:
            lines += [
                "# Store the placed node on the extension parameter node for later steps",
                f"from {module_name} import {logic_class_name}",
                *self._emit_module_enter_precondition(module_name),
                "try:",
                f"    logic = _{extension_name.lower()}_logic",
                "except NameError:",
                f"    logic = {logic_class_name}()",
                "parameterNode = logic.getParameterNode()",
                f"parameterNode.SetNodeReferenceID(\"{parameter_role}\", node.GetID())",
                f"_{extension_name.lower()}_logic = logic",
                "",
            ]

        lines += [
            "# Exit placement mode",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "interactionNode.SwitchToViewTransformMode()",
            "",
            f"print(\"[{extension_name}] Step '{step['step_id']}' processed with %d control points.\" % node.GetNumberOfControlPoints())",
        ]

        return "\n".join(lines) + "\n"

    def _generate_post_interaction_template_llm(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> Optional[str]:
        """Use LLM to generate a post-interaction template that calls the logic method."""
        method_name = step.get("method_name", "")
        if not method_name:
            return None

        # Gather method info
        method_info = None
        for m in logic_analysis.get("methods", []):
            if m.get("name") == method_name:
                method_info = m
                break

        # Get method source
        logic_file = logic_analysis.get("_logic_file", "")
        method_source = self._extract_method_source(logic_file, method_name) or ""

        if not method_source and not method_info:
            return None

        # Method source sent in full (no truncation)
        # if len(method_source) > 5000:
        #     method_source = method_source[:5000] + "\n# ... [truncated]"

        # Build parameter / state info
        params_desc = ""
        if method_info:
            params = method_info.get("parameters", [])
            if params:
                params_desc = "Parameters:\n" + "\n".join(
                    f"  - {p.get('name')}: {p.get('type', '?')} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                    for p in params
                )
            state_reads = method_info.get("state_reads", [])
            state_writes = method_info.get("state_writes", [])
            if state_reads:
                params_desc += f"\nState reads: {', '.join(state_reads)}"
            if state_writes:
                params_desc += f"\nState writes: {', '.join(state_writes)}"

        node_class = step.get("node_class", "vtkMRMLMarkupsFiducialNode")
        node_var = f"_{extension_name.lower()}_{step['step_id']}_id"
        min_points = step.get("min_control_points", 0)

        ui_context = ""

        proven_block = self._proven_api_chain_block()
        prompt = textwrap.dedent(f"""\
            Generate a Python code snippet for a 3D Slicer extension workflow step.
            This is the POST-INTERACTION part — the user has finished placing control points on a {node_class}.

            Extension: {extension_name}
            Logic class: `{logic_class_name}` (import from `{module_name}`)
            Step: {step.get('step_id', '')}
            Method to call: `{method_name}()`
            {ui_context}

            {params_desc}

            Method source code:
            ```python
            {method_source}
            ```
            {proven_block}

            Context: The user just placed control points on a markup node. The node ID is stored in workflow runtime state and may also be available in variable `{node_var}` as a fallback.
            Parameter-node role for this interaction, if any: `{step.get('parameter_role') or (step.get('interaction_binding') or {}).get('parameter_name', '')}`.

            The code must:
            1. Import the logic class from `{module_name}`
            2. Import `resolve_interaction_node` from `SlicerAIAgentLib.workflow_state`, then retrieve the markup node with:
               `node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "{step.get('step_id', '')}", "{node_class}", _workflow_runtime_repeat_index)`.
               If that returns None, fall back to `slicer.mrmlScene.GetNodeByID({node_var})`.
            3. Validate the user placed enough control points ({min_points} minimum)
            4. Do not emit module lifecycle setup; the generator adds the shared lifecycle precondition deterministically.
            5. Reuse the existing logic instance `_{extension_name.lower()}_logic` if it exists in `dir()`, otherwise create a new `{logic_class_name}()`
            6. Set up any required state on the logic instance BEFORE calling the method (e.g., if the method reads `self.inputMarkupNode`, assign the retrieved node to it)
            7. Call the method `{method_name}()` with correct arguments — pass the markup node if the method expects it
            8. Exit placement mode: `interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")` then `interactionNode.SwitchToViewTransformMode()`
            9. Store the logic instance as `_{extension_name.lower()}_logic` for subsequent steps
            10. Print a completion message with the number of control points
            11. If a non-empty parameter-node role is listed above, call `logic.getParameterNode().SetNodeReferenceID(role, node.GetID())` before later steps need that node.

            IMPORTANT restrictions:
            - Do NOT use `dir()`, `eval()`, `exec()`, `globals()`, or `locals()` — these are blocked in the execution sandbox.
            - Use `try/except NameError` to check if a variable exists, NOT `if 'var' in dir()`.
            - Do NOT use curly brace template placeholders. Write actual source-derived Python values. Do not invent or hardcode node names.
            - Escape all braces in f-strings and .format() calls by doubling them: use doubled-braces for literal braces in output strings.
            - Use ONLY the parameter/reference role names listed in the supplied parameter metadata. NEVER invent a role name (for example from a helper-method name); a role that is not listed does not exist.
            - Do NOT pre-set state the called method or its helper methods create or derive internally; set only the inputs the method reads.
            - Never call a method on the direct result of an API that can return None (GetNodeReference, GetItemDataNode, GetDisplayNode, ...) without first checking the result for None.
            - Return ONLY raw Python code. Do NOT wrap it in markdown fences (```python ... ```).""")

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt, call_class="generation", attempt=_attempt)
                response = self._strip_markdown_fences(response) if response else None
                if not response or "import" not in response:
                    break
                # Validate syntax immediately — retry once on failure
                import ast as _ast
                try:
                    _ast.parse(response)
                    return self._inject_module_enter_precondition(response, module_name)
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        logger.info(
                            "LLM post-interaction template for step %s had syntax error: %s. Retrying...",
                            step.get("step_id", "?"), e,
                        )
                        prompt += (
                            f"\n\nYour previous output had a syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        logger.warning(
                            "LLM post-interaction template for step %s still has syntax error after retry: %s",
                            step.get("step_id", "?"), e,
                        )
                        return self._inject_module_enter_precondition(response, module_name)
        except Exception:
            logger.debug("LLM post-interaction template generation failed", exc_info=True)
        return None

    @staticmethod
    def _sanitize_templates(templates: Dict[str, str]) -> Dict[str, str]:
        """Post-generation sanitization of code templates.

        Fixes common LLM output issues that would cause verify_repair validation
        failures:
        1. Null bytes in generated code
        2. Blocked module imports (sys, os, subprocess, etc.)
        3. Trailing whitespace / mixed line endings
        4. Unexpected indentation (LLM returns indented blocks)
        5. Empty method calls like ``logic.()`` from null method hints
        6. Multi-line Python comment headers accidentally split by raw descriptions

        This runs before verify_repair validation and is also applied to LLM review
        and revision outputs, so cheap syntax repairs do not require another
        LLM pass.
        """
        import ast as _ast
        import textwrap as _textwrap

        class _QualifyBareSlicerClasses(_ast.NodeTransformer):
            def __init__(self):
                self.changed = False

            def visit_Name(self, node):
                if (
                    isinstance(node.ctx, _ast.Load)
                    and node.id.startswith("vtkMRML")
                ):
                    self.changed = True
                    return _ast.copy_location(
                        _ast.Attribute(
                            value=_ast.Name(id="slicer", ctx=_ast.Load()),
                            attr=node.id,
                            ctx=node.ctx,
                        ),
                        node,
                    )
                return node

        # Blocked imports — mirror CodeValidator's list
        _BLOCKED_MODULES = {
            "os", "sys", "subprocess", "socket", "shutil",
            "pathlib", "signal", "ctypes", "multiprocessing",
        }
        _BLOCKED_IMPORT_RE = _re.compile(
            r'^(\s*)import\s+(' + "|".join(_BLOCKED_MODULES) + r')\b.*$',
            _re.MULTILINE,
        )
        _BLOCKED_FROM_IMPORT_RE = _re.compile(
            r'^(\s*)from\s+(' + "|".join(_BLOCKED_MODULES) + r')\s+import\b.*$',
            _re.MULTILINE,
        )
        # Empty method call pattern: logic.() or result = logic.()
        _EMPTY_METHOD_CALL_RE = _re.compile(
            r'(\w+)\.\(\)',
        )

        sanitized = {}
        fixes_applied = 0
        for key, code in templates.items():
            if not isinstance(code, str) or not code.strip():
                sanitized[key] = code
                continue

            # Skip non-code entries (workflow.json, etc.)
            if not key.endswith(".py.tpl"):
                sanitized[key] = code
                continue

            original = code

            # 1. Strip null bytes
            code = code.replace("\x00", "")

            # 1b. Normalize CJK fullwidth ASCII characters (U+FF01–U+FF5E)
            # Multilingual LLMs occasionally emit fullwidth variants like
            # ｜ (U+FF5C) instead of |, （ instead of (, etc.
            code = code.translate(_FULLWIDTH_TO_ASCII)

            # 2. Normalize line endings
            code = code.replace("\r\n", "\n").replace("\r", "\n")

            # 3. Repair comment headers split by multi-line descriptions
            code = ExtensionCLIAnalyzer._repair_multiline_comment_headers(code)

            # 4. Remove blocked module imports
            code = _BLOCKED_FROM_IMPORT_RE.sub(
                lambda m: f"{m.group(1)}# [removed blocked import: {m.group(0).strip()}]",
                code,
            )
            code = _BLOCKED_IMPORT_RE.sub(
                lambda m: f"{m.group(1)}# [removed blocked import: {m.group(0).strip()}]",
                code,
            )

            # 4b. Replace getattr(obj, 'attr') / setattr(obj, 'attr', value)
            # with obj.attr / obj.attr = value when the attribute is a string
            # literal containing a valid Python identifier.  The CodeValidator
            # blocks getattr/setattr entirely; this rewrite is safe only when
            # the attribute name is a compile-time constant.
            code = _GETATTR_LITERAL_RE.sub(lambda m: f"{m.group(1).strip()}.{m.group(3)}", code)
            code = _SETATTR_LITERAL_RE.sub(
                lambda m: f"{m.group(1).strip()}.{m.group(3)} = {m.group(4).strip()}", code,
            )

            # 5. Fix indentation: try ast.parse, on failure try dedent
            try:
                _ast.parse(code)
            except (SyntaxError, IndentationError) as e:
                if "indent" in str(e).lower() or "unexpected" in str(e).lower():
                    dedented = _textwrap.dedent(code)
                    try:
                        _ast.parse(dedented)
                        code = dedented
                        logger.info(
                            "[generate] Fixed indentation in '%s' via dedent",
                            key,
                        )
                    except (SyntaxError, IndentationError):
                        # dedent didn't help — leave for revision
                        pass

            # 6. Fix empty method calls: logic.() → # logic.<no method available>()
            if _EMPTY_METHOD_CALL_RE.search(code):
                def _fix_empty_call(m):
                    var = m.group(1)
                    # Only fix if it looks like a method call on a logic/object var
                    if var in ("logic", "_logic", "result"):
                        return f"# {var}.<method>()  # method name not available"
                    return m.group(0)
                code = _EMPTY_METHOD_CALL_RE.sub(_fix_empty_call, code)

            # 6b. Python templates must qualify Slicer MRML classes through the
            # slicer module.  LLMs sometimes emit C++-style bare class names
            # such as vtkMRMLSliceNode.EnumValue, which are undefined at
            # runtime.
            try:
                tree = _ast.parse(code)
                qualifier = _QualifyBareSlicerClasses()
                fixed_tree = qualifier.visit(tree)
                if qualifier.changed:
                    _ast.fix_missing_locations(fixed_tree)
                    qualified_code = _ast.unparse(fixed_tree)
                    code = qualified_code
            except (SyntaxError, IndentationError):
                pass

            # 7. Detect stub templates (only pass + comments/print)
            _stripped = [
                l.strip() for l in code.split('\n')
                if l.strip() and not l.strip().startswith('#')
            ]
            _non_trivial = [
                l for l in _stripped
                if l != 'pass' and not l.startswith('print(')
            ]
            if not _non_trivial:
                fixes_applied += 1
                logger.warning(
                    "[generate] Template '%s' appears to be a stub "
                    "(only pass/comments). Consider regenerating.",
                    key,
                )

            if code != original:
                fixes_applied += 1
                logger.info(
                    "[generate] Sanitized template '%s'",
                    key,
                )

            sanitized[key] = code

        if fixes_applied:
            logger.info(
                "[generate] Sanitization fixed %d/%d templates",
                fixes_applied, len(templates),
            )

        return sanitized

    # ================================================================
    # verify_repair: Live API Probing
    # ================================================================
