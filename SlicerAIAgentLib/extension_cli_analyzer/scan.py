from .common import *


class AnalyzerScanMixin:
    def _stage1_scan(self, source_path: str) -> Dict:
        """Scan extension source tree, parse AST, find Logic class."""
        self.on_progress("discover", "Discover Source And Cookbook", "Scanning extension files...")

        if not os.path.isdir(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")

        # Walk and collect Python and .ui files
        py_files = []
        ui_files = []
        for root, dirs, files in os.walk(source_path):
            # Skip hidden dirs, __pycache__, build dirs
            dirs[:] = [d for d in dirs if not d.startswith((".", "__")) and d != "build"]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
                elif f.endswith(".ui"):
                    ui_files.append(os.path.join(root, f))

        self.on_progress(
            "discover", "Discover Source And Cookbook",
            f"Found {len(py_files)} Python files"
        )

        # Parse each file's AST
        file_inventory = {}
        logic_candidates = []
        widget_candidates = []
        # Extensions using the modern slicer.parameterNodeWrapper expose their
        # parameter node as a typed class whose node references are PROPERTIES
        # (e.g. paramNode.orbitLm), not the classic GetNodeReference/SetNodeReferenceID
        # VTK methods. Detecting these lets later stages generate property access
        # and reject the classic API (which does not exist on a wrapper).
        parameter_node_wrappers = []

        for fpath in py_files:
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            classes = []
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = [self._ast_name(b) for b in node.bases]
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    classes.append({
                        "name": node.name,
                        "bases": bases,
                        "methods": methods,
                        "line": node.lineno,
                    })
                    # Detect a parameterNodeWrapper parameter-node class and
                    # capture its annotated fields ({field_name: type_string}).
                    decorators = [self._ast_name(d) for d in getattr(node, "decorator_list", [])]
                    if any(
                        d == "parameterNodeWrapper" or d.endswith(".parameterNodeWrapper")
                        for d in decorators
                    ):
                        fields = {}
                        for stmt in node.body:
                            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                                type_str = self._annotation_node_class(stmt.annotation)
                                if type_str:
                                    fields[stmt.target.id] = type_str
                        parameter_node_wrappers.append({
                            "file": fpath,
                            "class_name": node.name,
                            "fields": fields,
                            "line": node.lineno,
                        })
                    # Detect Logic class
                    is_logic = (
                        "ScriptedLoadableModuleLogic" in bases
                        or node.name.endswith("Logic")
                    )
                    if is_logic:
                        logic_candidates.append({
                            "file": fpath,
                            "class_name": node.name,
                            "methods": methods,
                            "bases": bases,
                            "line": node.lineno,
                        })
                    # Detect Widget class
                    is_widget = (
                        "ScriptedLoadableModuleWidget" in bases
                        or node.name.endswith("Widget")
                    )
                    if is_widget:
                        widget_candidates.append({
                            "file": fpath,
                            "class_name": node.name,
                            "methods": methods,
                            "bases": bases,
                            "line": node.lineno,
                        })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)

            file_inventory[fpath] = {
                "classes": classes,
                "functions": functions,
            }

        # Pick best Logic candidate (prefer ScriptedLoadableModuleLogic subclass,
        # then prefer one with "process" or "run" methods)
        logic_class = None
        if logic_candidates:
            scored = []
            for cand in logic_candidates:
                score = 0
                # Strong preference for the Slicer-standard base class
                if "ScriptedLoadableModuleLogic" in cand["bases"]:
                    score += 100
                # Preference for classes with more methods (likely the main logic, not a helper)
                score += min(len(cand["methods"]), 20)
                for m in cand["methods"]:
                    if m.startswith(("process", "run", "compute", "execute")):
                        score += 10
                    if m.startswith("__init__"):
                        score += 1
                scored.append((score, cand))
            scored.sort(key=lambda x: x[0], reverse=True)
            logic_class = scored[0][1]

        # Pick best Widget candidate (prefer ScriptedLoadableModuleWidget subclass)
        widget_class = None
        if widget_candidates:
            # The widget MUST come from the same module file as the chosen logic
            # class — they are one module. An extension repo can bundle several
            # modules (e.g. PlateRegistration + MirrorOrbitRecon); picking a
            # sibling module's widget yields the wrong button→handler
            # connections, which silently breaks handler-invocation generation.
            logic_file = logic_class["file"] if logic_class else None
            scored_w = []
            for cand in widget_candidates:
                score = 0
                if "ScriptedLoadableModuleWidget" in cand["bases"]:
                    score += 100
                score += min(len(cand["methods"]), 20)
                if "setup" in cand["methods"]:
                    score += 50
                if logic_file and cand["file"] == logic_file:
                    score += 500
                scored_w.append((score, cand))
            scored_w.sort(key=lambda x: x[0], reverse=True)
            widget_class = scored_w[0][1]

        # The parameter-node wrapper relevant to the selected logic class is the
        # one defined in the same module file (an extension repo may bundle
        # several modules, each with its own wrapper). Fall back to any wrapper.
        parameter_node_wrapper = None
        if parameter_node_wrappers:
            logic_file = logic_class["file"] if logic_class else None
            same_file = [w for w in parameter_node_wrappers if w["file"] == logic_file]
            parameter_node_wrapper = (same_file or parameter_node_wrappers)[0]

        # Map qMRMLSegmentsTableView widgets to the parameterNodeWrapper field the
        # extension binds them to (via setSegmentationNode/ID), so a generated
        # segments-table step can target the exact segmentation rather than just
        # the node class (e.g. fractureSegmentsTable -> OutputFracSeg).
        wrapper_fields = set((parameter_node_wrapper or {}).get("fields") or {})
        segments_table_bindings = self._scan_segments_table_bindings(py_files, wrapper_fields)

        # Find the entry point module (the main module file)
        entry_module = None
        if logic_class:
            entry_module = logic_class["file"]

        self.on_progress(
            "discover", "Discover Source And Cookbook",
            f"Logic class: {logic_class['class_name'] if logic_class else 'None'} "
            f"in {os.path.basename(entry_module) if entry_module else 'N/A'}"
            f", Widget class: {widget_class['class_name'] if widget_class else 'None'}"
            f", UI files: {len(ui_files)}"
        )

        return {
            "source_path": source_path,
            "py_files": py_files,
            "ui_files": ui_files,
            "file_inventory": file_inventory,
            "logic_class": logic_class,
            "widget_class": widget_class,
            "entry_module": entry_module,
            "parameter_node_wrapper": parameter_node_wrapper,
            "parameter_node_wrappers": parameter_node_wrappers,
            "segments_table_bindings": segments_table_bindings,
        }

    @staticmethod
    def _scan_segments_table_bindings(py_files: List[str], wrapper_fields) -> Dict[str, str]:
        """Map ``widget_name -> parameterNodeWrapper field`` for qMRMLSegmentsTableView
        widgets the extension binds via ``self.ui.<widget>.setSegmentationNode(<arg>)``
        (or ``setSegmentationNodeID(<arg>.GetID())``), where ``<arg>`` resolves to a
        wrapper field (directly, through a same-function local, or via either side of
        an assignment). Lets a segments-table step target the exact segmentation
        (e.g. the fractures one) instead of the first node of the class. Generic:
        keyed on the wrapper field set, no extension/step-specific strings.
        """
        fields = set(wrapper_fields or [])
        bindings: Dict[str, str] = {}
        if not fields:
            return bindings

        def _dotted(node) -> str:
            parts = []
            cur = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
                return ".".join(reversed(parts))
            return ""

        def _field_of(node) -> str:
            # e.g. self._parameterNode.OutputFracSeg -> "OutputFracSeg"
            if isinstance(node, ast.Attribute) and node.attr in fields:
                return node.attr
            return ""

        for fpath in py_files:
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read())
            except Exception:
                continue
            for func in ast.walk(tree):
                if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                local_field: Dict[str, str] = {}   # dotted local/attr expr -> field
                ui_alias: Dict[str, str] = {}      # dotted local -> widget name
                for stmt in ast.walk(func):
                    if not isinstance(stmt, ast.Assign):
                        continue
                    rhs = stmt.value
                    rfield = _field_of(rhs)
                    rdot = _dotted(rhs)
                    for tgt in stmt.targets:
                        tdot = _dotted(tgt)
                        if rfield and tdot:                       # local = paramNode.Field
                            local_field[tdot] = rfield
                        tfield = _field_of(tgt)
                        if tfield and rdot:                       # paramNode.Field = local
                            local_field[rdot] = tfield
                        if (isinstance(rhs, ast.Attribute)
                                and _dotted(getattr(rhs, "value", None)) == "self.ui"
                                and tdot):                        # tbl = self.ui.<widget>
                            ui_alias[tdot] = rhs.attr

                def _resolve_arg_field(arg) -> str:
                    direct = _field_of(arg) or local_field.get(_dotted(arg), "")
                    if direct:
                        return direct
                    # setSegmentationNodeID(<expr>.GetID())
                    if (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute)
                            and arg.func.attr == "GetID"):
                        inner = arg.func.value
                        return _field_of(inner) or local_field.get(_dotted(inner), "")
                    return ""

                for call in ast.walk(func):
                    if not isinstance(call, ast.Call):
                        continue
                    fn = call.func
                    if not (isinstance(fn, ast.Attribute)
                            and fn.attr in ("setSegmentationNode", "setSegmentationNodeID")):
                        continue
                    recv = fn.value
                    widget = ""
                    if (isinstance(recv, ast.Attribute)
                            and _dotted(getattr(recv, "value", None)) == "self.ui"):
                        widget = recv.attr                        # self.ui.<widget>.setSegmentationNode
                    else:
                        widget = ui_alias.get(_dotted(recv), "")  # aliased local
                    if not widget or not call.args:
                        continue
                    field = _resolve_arg_field(call.args[0])
                    if field:
                        bindings.setdefault(widget, field)
        return bindings

    @staticmethod
    def _annotation_node_class(annotation) -> str:
        """Return the node-class string from a parameterNodeWrapper field annotation.

        Unwraps ``Optional[X]`` / ``Union[X, None]`` / ``Annotated[X, ...]`` and
        string annotations. Returns "" for non-node (scalar) types so callers can
        keep only node-reference fields.
        """
        if annotation is None:
            return ""
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Attribute):
            return annotation.attr
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            return annotation.value
        if isinstance(annotation, ast.Subscript):
            sl = annotation.slice
            if hasattr(ast, "Index") and isinstance(sl, ast.Index):  # py<3.9
                sl = sl.value
            if isinstance(sl, ast.Tuple) and sl.elts:
                return ExtensionCLIAnalyzer._annotation_node_class(sl.elts[0])
            return ExtensionCLIAnalyzer._annotation_node_class(sl)
        return ""

    @staticmethod
    def _ast_name(node) -> str:
        """Extract a readable name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{ExtensionCLIAnalyzer._ast_name(node.value)}.{node.attr}"
        if isinstance(node, ast.Constant):
            return str(node.value)
        return ""

    # ================================================================
    # .ui File Parsing (Qt Designer XML)
    # ================================================================

    def _parse_ui_file(self, ui_path: str) -> Optional[Dict]:
        """Parse a Qt .ui file and extract sections and buttons."""
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(ui_path)
        except ET.ParseError:
            logger.debug("Failed to parse .ui file: %s", ui_path)
            return None

        root = tree.getroot()
        sections = []
        # Find all collapsible sections and their button children
        for widget in root.iter("widget"):
            widget_class = widget.get("class", "")
            if widget_class in ("ctkCollapsibleButton", "ctkCollapsibleGroupBox"):
                section_name = ""
                # Find the text property
                for prop in widget.findall("property"):
                    if prop.get("name") == "text":
                        string_el = prop.find("string")
                        if string_el is not None and string_el.text:
                            section_name = string_el.text.strip()
                if not section_name:
                    section_name = widget_class

                buttons = self._extract_buttons_from_widget(widget)
                if buttons:
                    sections.append({
                        "name": section_name,
                        "buttons": buttons,
                    })

        # If no collapsible sections found, look for top-level buttons
        if not sections:
            all_buttons = []
            for widget in root.iter("widget"):
                wc = widget.get("class", "")
                if wc in ("QPushButton", "ctkCheckablePushButton"):
                    btn = self._parse_button_widget(widget)
                    if btn:
                        all_buttons.append(btn)
            if all_buttons:
                sections.append({"name": "Buttons", "buttons": all_buttons})

        return {"sections": sections} if sections else None

    def _extract_buttons_from_widget(self, parent_widget) -> List[Dict]:
        """Extract buttons from a UI widget element, recursing into all nested layouts/frames."""
        buttons = []
        for child in parent_widget:
            if child.tag == "widget":
                wc = child.get("class", "")
                if wc in ("QPushButton", "ctkCheckablePushButton"):
                    btn = self._parse_button_widget(child)
                    if btn:
                        buttons.append(btn)
                else:
                    # Recurse into any non-button widget (QFrame, QGroupBox, etc.)
                    buttons.extend(self._extract_buttons_from_widget(child))
            elif child.tag == "layout":
                buttons.extend(self._extract_buttons_from_widget(child))
            elif child.tag == "item":
                buttons.extend(self._extract_buttons_from_widget(child))
        return buttons

    @staticmethod
    def _parse_button_widget(widget_el) -> Optional[Dict]:
        """Parse a single button widget element."""
        name = widget_el.get("name", "")
        label = ""
        for prop in widget_el.findall("property"):
            if prop.get("name") == "text":
                string_el = prop.find("string")
                if string_el is not None and string_el.text:
                    label = string_el.text.strip()
        if name:
            return {"widget_name": name, "label": label}
        return None

    def _extract_ui_widget_inventory(self, ui_files: List[str]) -> Dict[str, Dict]:
        """Extract a lightweight widget inventory from Qt Designer .ui files.

        This is intentionally generic: it records widget names, Qt classes, and
        simple string/list properties such as qMRMLNodeComboBox nodeTypes.  Later
        stages can use this as evidence for parameter-node bindings without the
        cookbook author knowing API details.
        """
        import xml.etree.ElementTree as ET

        widgets: Dict[str, Dict] = {}
        for ui_path in ui_files or []:
            try:
                root = ET.parse(ui_path).getroot()
            except Exception:
                continue
            for widget in root.iter("widget"):
                name = widget.get("name", "")
                if not name:
                    continue
                info = {
                    "class": widget.get("class", ""),
                    "properties": {},
                    "ui_file": os.path.basename(ui_path),
                }
                for prop in widget.findall("property"):
                    pname = prop.get("name", "")
                    if not pname:
                        continue
                    value = self._parse_ui_property_value(prop)
                    if value is not None:
                        info["properties"][pname] = value
                widgets[name] = info
        return widgets

    @staticmethod
    def _parse_ui_property_value(prop) -> Optional[Any]:
        """Return a simple Python value for common Qt Designer property tags."""
        for tag in ("string", "cstring", "enum", "set"):
            el = prop.find(tag)
            if el is not None:
                return el.text or ""
        bool_el = prop.find("bool")
        if bool_el is not None:
            return str(bool_el.text or "").strip().lower() == "true"
        for tag in ("number", "int", "uint"):
            el = prop.find(tag)
            if el is not None:
                try:
                    return int(str(el.text or "0").strip())
                except ValueError:
                    return el.text or ""
        for tag in ("double", "float"):
            el = prop.find(tag)
            if el is not None:
                try:
                    return float(str(el.text or "0").strip())
                except ValueError:
                    return el.text or ""
        return None

    # ================================================================
    # Widget Signal Connection Extraction (AST)
    # ================================================================

    def _extract_widget_connections(self, widget_source: str) -> List[Dict]:
        """Extract widget signal→handler→logic_method mappings from Widget source.

        This intentionally covers more than push-button clicks.  Many Slicer
        scripted extensions persist checkbox/toolbutton/spinbox changes through
        a shared updateParameterNodeFromGUI handler, and those controls are
        workflow operations even when no Logic method is called directly.
        """
        try:
            tree = ast.parse(widget_source)
        except SyntaxError:
            return []

        connections = []
        # Scan every widget class in the source. Signal connections may be wired in
        # setup() or in a helper it delegates to (e.g. _buildGui, setupUi), so discovery
        # is class-wide rather than restricted to the setup() method.
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                connections.extend(self._find_clicked_connections(node))

        return connections

    def _find_clicked_connections(self, class_node) -> List[Dict]:
        """Find common Qt signal connect(self.XXX) patterns across the widget class.

        Scans every method of the class rather than only setup(), so connections wired
        in a helper that setup() delegates to (e.g. _buildGui, setupUi) are still found.
        Duplicate connections (the same control re-wired in more than one method) are
        collapsed on (button, signal, handler).
        """
        connections = []
        seen = set()
        # Build handler→logic_method map from all methods in the class
        handler_logic_map = {}
        for item in class_node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                logic_calls = self._find_logic_calls_in_method(item)
                if logic_calls:
                    handler_logic_map[item.name] = logic_calls

        _SUPPORTED_SIGNALS = {
            "clicked", "toggled", "stateChanged", "valueChanged",
            "currentTextChanged", "currentIndexChanged", "textActivated",
            "checkBoxToggled", "currentNodeChanged",
        }

        for method_node in class_node.body:
            if not isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for stmt in ast.walk(method_node):
                if not isinstance(stmt, ast.Call):
                    continue
                func = stmt.func
                if not isinstance(func, ast.Attribute):
                    continue
                if func.attr != "connect":
                    continue

                button_name = ""
                handler_name = ""
                signal_name = ""

                # Pattern 1: something.clicked.connect(self.handlerMethod)
                # Also supports stateChanged/valueChanged/currentTextChanged/etc.
                receiver = func.value
                if isinstance(receiver, ast.Attribute) and receiver.attr in _SUPPORTED_SIGNALS:
                    button_name = self._get_attribute_chain(receiver.value)
                    signal_name = receiver.attr
                    if stmt.args:
                        arg = stmt.args[0]
                        if isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name):
                            if arg.value.id == "self":
                                handler_name = arg.attr

                # Pattern 2: something.connect('clicked(bool)', self.handlerMethod)
                #            something.connect("stateChanged(int)", self.handlerMethod)
                if not button_name and stmt.args:
                    first_arg = stmt.args[0]
                    if (isinstance(first_arg, ast.Constant)
                            and isinstance(first_arg.value, str)
                            and any(sig in first_arg.value for sig in _SUPPORTED_SIGNALS)):
                        button_name = self._get_attribute_chain(func.value)
                        signal_name = first_arg.value
                        if len(stmt.args) > 1:
                            second_arg = stmt.args[1]
                            if isinstance(second_arg, ast.Attribute) and isinstance(second_arg.value, ast.Name):
                                if second_arg.value.id == "self":
                                    handler_name = second_arg.attr

                if button_name and handler_name:
                    bare_name = button_name.split(".")[-1] if button_name else ""
                    key = (bare_name, signal_name, handler_name)
                    if key in seen:
                        continue
                    seen.add(key)
                    logic_methods = handler_logic_map.get(handler_name, [])
                    connections.append({
                        "button_widget_name": bare_name,
                        "signal": signal_name,
                        "handler_method": handler_name,
                        "logic_methods": logic_methods,
                    })

        return connections

    @staticmethod
    def _get_attribute_chain(node) -> str:
        """Build dotted name from chained attribute access (e.g. self.buttonName)."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = ExtensionCLIAnalyzer._get_attribute_chain(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""

    def _find_logic_calls_in_method(self, method_node) -> List[str]:
        """Find self.logic.XXX() calls in a method body."""
        calls = []
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                func = node.func
                if (isinstance(func, ast.Attribute)
                        and isinstance(func.value, ast.Attribute)):
                    if (func.value.attr == "logic"
                            and isinstance(func.value.value, ast.Name)
                            and func.value.value.id == "self"):
                        calls.append(func.attr)
        return calls

    # ================================================================
    # Stage 3: Logic Class Analysis (LLM)
    # ================================================================
