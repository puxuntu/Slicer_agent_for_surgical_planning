from .common import *


class AnalyzerContractsMixin:
    def test_ExtensionCLIAnalyzerContracts(self):
        """Test generic workflow-generation validation contracts."""
        from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
        from SlicerAIAgentLib.CodeValidator import CodeValidator

        analyzer = ExtensionCLIAnalyzer(
            llm_client=None,
            code_validator=CodeValidator(),
        )

        # API repair acceptance must depend on valid Python, not on imports.
        analyzer._call_llm = lambda prompt: "node.SetVisibility(True)"
        repaired = analyzer._revise_template_for_api(
            "templates/step.py.tpl",
            "node.ToggleVisibility()",
            [{"chain": "node.ToggleVisibility", "error": "missing"}],
        )
        self.assertEqual(repaired, "node.SetVisibility(True)")

        # Live API probe failures remain blocking through validation.
        validation = analyzer._stage9_validate(
            {"templates/step.py.tpl": "x = 1"},
            [{"template_file": "templates/step.py.tpl", "step_type": "automated"}],
            logic_analysis=None,
            api_probe_result={
                "unresolved_failures": [
                    {
                        "template": "templates/step.py.tpl",
                        "chain": "slicer.app.badApi",
                        "error": "API call does not exist",
                    }
                ]
            },
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("Unresolved live API probe failure" in e for e in validation["errors"]))

        # Known invalid Slicer API aliases must be blocking even if a live
        # probe was not run against the final revised template.
        validation = analyzer._stage9_validate(
            {"templates/slice.py.tpl": "sliceNode.SetSliceVisibility(False)\n"},
            [{
                "template_file": "templates/slice.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Toggle slice visibility in 3D",
                    "slicer_op_category": "layout_slice_view",
                    "confidence": "high",
                }],
                "operation_model": {
                    "invokes_slicer_api": True,
                    "implementation_uses_slicer_api": True,
                },
            }],
            logic_analysis=None,
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("SetSliceVisibility does not exist" in e for e in validation["errors"]))

        # Method dependency metadata must include node-reference reads, not just
        # scalar GetParameter reads, so runtime guards can validate geometry.
        source = """
class Logic:
    def runGeometry(self):
        p = self.getParameterNode()
        p.GetNodeReference("modelNode")
        self.helper()
    def helper(self):
        p = self.getParameterNode()
        float(p.GetParameter("spacing"))
    def initializeCentroid(self):
        p = self.getParameterNode()
        p.SetParameter("centroidX", "0.0")
"""
        roles = analyzer._extract_parameter_roles_from_source(source)
        deps = analyzer._extract_parameter_method_dependencies(source, roles)
        self.assertIn("modelNode", deps["runGeometry"].get("node_roles", []))
        self.assertIn("spacing", deps["runGeometry"].get("parameter_roles", []))
        self.assertNotIn("initializeCentroid", deps)

        # Node-reference requirements are based on actual use sites, including
        # parameter guards and references created by the method itself.
        conditional_source = """
class Logic:
    def run(self):
        parameterNode = self.getParameterNode()
        enabled = parameterNode.GetParameter("enableRepair") == "True"
        repairPlane = parameterNode.GetNodeReference("repairPlane")
        nestedPlane = parameterNode.GetNodeReference("nestedPlane")
        requiredModel = parameterNode.GetNodeReference("requiredModel")
        guardedModel = parameterNode.GetNodeReference("guardedModel")
        conditionallyCreated = parameterNode.GetNodeReference("conditionallyCreated")
        if enabled:
            repairPlane.GetID()
            if parameterNode.GetParameter("mode") == "advanced":
                nestedPlane.GetID()
            parameterNode.SetNodeReferenceID("conditionallyCreated", "node-id")
        if guardedModel:
            guardedModel.GetID()
        conditionallyCreated.GetID()
        requiredModel.GetID()
        self.createdHelper()
    def createdHelper(self):
        parameterNode = self.getParameterNode()
        parameterNode.SetNodeReferenceID("createdPlane", "node-id")
        createdPlane = parameterNode.GetNodeReference("createdPlane")
        createdPlane.GetID()
"""
        conditional_roles = analyzer._extract_parameter_roles_from_source(conditional_source)
        conditional_deps = analyzer._extract_parameter_method_dependencies(
            conditional_source, conditional_roles
        )
        requirements = conditional_deps["run"]["node_requirements"]
        self.assertEqual(requirements["requiredModel"]["requirement"], "required")
        self.assertEqual(requirements["conditionallyCreated"]["requirement"], "required")
        self.assertEqual(requirements["guardedModel"]["requirement"], "optional_unknown")
        self.assertEqual(requirements["createdPlane"]["requirement"], "produced_by_method")
        self.assertEqual(requirements["repairPlane"], {
            "requirement": "conditional",
            "conditions": [{
                "parameter": "enableRepair",
                "operator": "equals",
                "value": "True",
            }],
            "condition_groups": [[{
                "parameter": "enableRepair",
                "operator": "equals",
                "value": "True",
            }]],
        })
        self.assertEqual(requirements["nestedPlane"]["condition_groups"], [[
            {
                "parameter": "mode",
                "operator": "equals",
                "value": "advanced",
            },
            {
                "parameter": "enableRepair",
                "operator": "equals",
                "value": "True",
            },
        ]])

        # Runtime preconditions skip a false-gated missing reference and enforce
        # the same reference when its source-derived condition becomes true.
        from SlicerAIAgentLib.ExtensionCLILoader import _WorkflowContext, _build_runtime_prelude
        runtime_ctx = _WorkflowContext(
            ext_name="Generic",
            ext_dir="",
            tool_name="Generic",
            workflow_graph={},
            target_step={"step_id": "cb_step_1", "method_name": "conditionalOnly"},
            target_gen={"method_name": "conditionalOnly"},
            arguments={},
            user_action="start",
            done=set(),
            metadata={
                "extension_module_name": "GenericExtension",
                "logic_class_name": "GenericLogic",
                "parameter_bindings": {
                    "enableRepair": {
                        "role": "enableRepair",
                        "accesses": ["parameter_read"],
                        "value_types": ["bool"],
                    },
                    "repairPlane": {
                        "role": "repairPlane",
                        "accesses": ["node_reference_read"],
                        "node_class": "vtkMRMLMarkupsPlaneNode",
                    },
                },
                "parameter_method_dependencies": {
                    "conditionalOnly": {
                        "parameter_roles": ["enableRepair"],
                        "node_roles": ["repairPlane"],
                        "node_requirements": {
                            "repairPlane": requirements["repairPlane"],
                        },
                    },
                },
            },
        )

        class _FakeParameterNode:
            def __init__(self):
                self.enabled = "False"

            def GetParameter(self, role):
                return self.enabled if role == "enableRepair" else ""

            def GetNodeReference(self, role):
                return None

        class _FakeLogic:
            def __init__(self):
                self.parameterNode = _FakeParameterNode()

            def getParameterNode(self):
                return self.parameterNode

        runtime_namespace = {"_generic_logic": _FakeLogic()}
        exec(_build_runtime_prelude(runtime_ctx), runtime_namespace)
        runtime_namespace["_workflow_validate_method_preconditions"]()
        runtime_namespace["_generic_logic"].parameterNode.enabled = "True"
        with self.assertRaisesRegex(RuntimeError, "Missing conditional node reference"):
            runtime_namespace["_workflow_validate_method_preconditions"]()

        required_metadata = dict(runtime_ctx.metadata)
        required_metadata["parameter_bindings"] = {
            "requiredModel": {
                "role": "requiredModel",
                "accesses": ["node_reference_read"],
                "node_class": "vtkMRMLModelNode",
            },
        }
        required_metadata["parameter_method_dependencies"] = {
            "requiredOnly": {
                "node_roles": ["requiredModel"],
                "node_requirements": {
                    "requiredModel": {
                        "requirement": "required",
                        "conditions": [],
                        "condition_groups": [],
                    },
                },
            },
        }
        required_ctx = _WorkflowContext(
            "Generic", "", "Generic", {},
            {"step_id": "cb_step_2", "method_name": "requiredOnly"},
            {"method_name": "requiredOnly"}, {}, "start", set(), required_metadata,
        )
        required_namespace = {"_generic_logic": _FakeLogic()}
        exec(_build_runtime_prelude(required_ctx), required_namespace)
        with self.assertRaisesRegex(RuntimeError, "Missing required node reference"):
            required_namespace["_workflow_validate_method_preconditions"]()

        # Metadata generated before requirement classification is treated as
        # unknown instead of incorrectly requiring every transitive read.
        legacy_metadata = dict(required_metadata)
        legacy_metadata["parameter_method_dependencies"] = {
            "legacy": {"node_roles": ["requiredModel"]},
        }
        legacy_ctx = _WorkflowContext(
            "Generic", "", "Generic", {},
            {"step_id": "cb_step_3", "method_name": "legacy"},
            {"method_name": "legacy"}, {}, "start", set(), legacy_metadata,
        )
        legacy_namespace = {"_generic_logic": _FakeLogic()}
        exec(_build_runtime_prelude(legacy_ctx), legacy_namespace)
        legacy_namespace["_workflow_validate_method_preconditions"]()

        # Placeholder scanning ignores braces inside strings/f-strings.
        placeholders = analyzer._find_template_placeholders(
            "print(f'{value}')\n{vol_lookup}\nnode = {node_name: None}\n"
        )
        self.assertEqual(
            placeholders,
            [
                {"name": "node_name", "has_default": True},
                {"name": "vol_lookup", "has_default": False},
            ],
        )

        # Module/panel phrases in user-facing cookbooks are UI-location context,
        # not instructions to leave the SlicerAIAgent module.
        from SlicerAIAgentLib.CookbookParser import CookbookDef, CookbookStep
        cookbook = CookbookDef(
            extension_name="GenericExtension",
            source_file="cookbook.md",
            steps=[CookbookStep(
                step_number=1,
                title="Display",
                description=(
                    "In the Markups module's Display > Advanced panel, configure "
                    "View to show in both View 1 and Red."
                ),
            )],
        )
        stage_map = analyzer._build_stage_map_from_decomposition(
            {
                "steps": [{
                    "step_number": 1,
                    "sub_operations": [
                        {
                            "op_type": "slicer_op",
                            "description": "Switch to Markups module",
                            "slicer_op_category": "module_switching",
                            "slicer_api_keywords": ["selectModule", "Markups"],
                            "evidence_type": "slicer_core",
                            "confidence": "high",
                        },
                        {
                            "op_type": "slicer_op",
                            "description": "Configure display View to show in View 1 and Red",
                            "slicer_op_category": "markups_display",
                            "slicer_api_keywords": ["AddViewNodeID", "View"],
                            "evidence_type": "slicer_core",
                            "confidence": "high",
                        },
                    ],
                }]
            },
            cookbook,
            {"methods": []},
        )
        sub_ops = stage_map["stages"][0]["sub_operations"]
        self.assertEqual(len(sub_ops), 1)
        self.assertEqual(sub_ops[0]["slicer_op_category"], "markups_display")
        self.assertFalse(any(so.get("slicer_op_category") == "module_switching" for so in sub_ops))

        # Unbound open-ended user choices produce a validation warning.
        validation = analyzer._stage9_validate(
            {},
            [{
                "step_type": "user_choice",
                "param_signature": {"workflow_step": "cb_step_1"},
                "description": "Select the input model node",
                "choice_descriptor": {
                    "question": "Which model should be used?",
                    "choices": [],
                    "parameter_name": "inputModel",
                },
            }],
        )
        self.assertTrue(any("no source-derived parameter binding" in w for w in validation["warnings"]))

        # Closed-form choices can bind to non-node extension parameters.
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fp:
            fp.write(
                "class GenericLogic:\n"
                "    def updateParameterNodeFromGUI(self):\n"
                "        parameterNode.SetParameter('rightSideLegFibula', 'True')\n"
                "    def transform(self):\n"
                "        parameterNode.GetParameter('rightSideLegFibula')\n"
            )
            source_path = fp.name
        try:
            metadata = analyzer._build_workflow_metadata(
                {"entry_module": source_path, "logic_class": {"class_name": "GenericLogic"}},
                {},
                {
                    "steps": [{
                        "step_id": "cb_step_1",
                        "step_type": "user_choice",
                        "op_type": "user_choice",
                        "description": "If the source side is right, choose right.",
                        "choice_info": {
                            "question": "Is this the right side?",
                            "choices": [{"label": "Yes", "value": True}, {"label": "No", "value": False}],
                            "parameter_name": "right_side",
                        },
                        "sub_operations": [{"op_type": "user_choice"}],
                    }]
                },
            )
            self.assertEqual(
                metadata["choice_bindings"]["cb_step_1"]["parameter_name"],
                "rightSideLegFibula",
            )
        finally:
            os.unlink(source_path)

        # Scalar parameter-node defaults are inferred from UI widgets and
        # transitive helper-method reads before automated extension calls.
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fp:
            fp.write(
                "class GenericLogic:\n"
                "    def updateParameterNodeFromGUI(self):\n"
                "        parameterNode.SetParameter('initialSpace', str(self.ui.initialSpinBox.value))\n"
                "    def generate(self):\n"
                "        self.transform()\n"
                "    def transform(self):\n"
                "        initialSpace = float(parameterNode.GetParameter('initialSpace'))\n"
            )
            source_path = fp.name
        with tempfile.NamedTemporaryFile("w", suffix=".ui", delete=False) as fp:
            fp.write(
                "<ui><widget class=\"ctkDoubleSpinBox\" name=\"initialSpinBox\">"
                "<property name=\"value\"><double>1.5</double></property>"
                "</widget></ui>"
            )
            ui_path = fp.name
        try:
            metadata = analyzer._build_workflow_metadata(
                {
                    "entry_module": source_path,
                    "ui_files": [ui_path],
                    "logic_class": {"class_name": "GenericLogic"},
                },
                {},
                {"steps": []},
            )
            self.assertEqual(
                metadata["parameter_defaults"]["initialSpace"]["value"],
                "1.5",
            )
            self.assertEqual(
                metadata["parameter_method_dependencies"]["generate"]["parameter_roles"],
                ["initialSpace"],
            )
            analyzer._workflow_metadata = metadata
            validation = analyzer._stage9_validate(
                {"templates/cb_step_scalar.py.tpl": "logic.generate()\n"},
                [{
                    "template_file": "templates/cb_step_scalar.py.tpl",
                    "step_type": "automated",
                    "op_type": "extension_op",
                    "operation_model": {
                        "step_type": "automated",
                        "op_types": ["extension_op"],
                        "invokes_extension_method": True,
                    },
                    "sub_operations": [{
                        "op_type": "extension_op",
                        "description": "Generate result.",
                        "extension_method_hint": "generate",
                    }],
                }],
                logic_analysis={"methods": [{"name": "generate", "parameters": []}]},
            )
            self.assertTrue(validation["valid"], validation.get("errors"))
        finally:
            os.unlink(source_path)
            os.unlink(ui_path)

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fp:
            fp.write(
                "class GenericLogic:\n"
                "    def generate(self):\n"
                "        initialSpace = float(parameterNode.GetParameter('initialSpace'))\n"
            )
            source_path = fp.name
        try:
            metadata = analyzer._build_workflow_metadata(
                {"entry_module": source_path, "logic_class": {"class_name": "GenericLogic"}},
                {},
                {"steps": []},
            )
            metadata["parameter_defaults"].pop("initialSpace", None)
            analyzer._workflow_metadata = metadata
            validation = analyzer._stage9_validate(
                {"templates/cb_step_scalar_missing.py.tpl": "logic.generate()\n"},
                [{
                    "template_file": "templates/cb_step_scalar_missing.py.tpl",
                    "step_type": "automated",
                    "op_type": "extension_op",
                    "operation_model": {
                        "step_type": "automated",
                        "op_types": ["extension_op"],
                        "invokes_extension_method": True,
                    },
                    "sub_operations": [{
                        "op_type": "extension_op",
                        "description": "Generate result.",
                        "extension_method_hint": "generate",
                    }],
                }],
                logic_analysis={"methods": [{"name": "generate", "parameters": []}]},
            )
            self.assertFalse(validation["valid"])
            self.assertTrue(any("depends on scalar parameter 'initialSpace'" in e for e in validation["errors"]))
        finally:
            os.unlink(source_path)

        # Slicer API code cannot hide in an extension_op without an extension method.
        validation = analyzer._stage9_validate(
            {"templates/cb_step_1.py.tpl": "slicer.app.layoutManager().setLayout(1)"},
            [{
                "template_file": "templates/cb_step_1.py.tpl",
                "step_type": "automated",
                "op_type": "extension_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["extension_op"],
                    "invokes_extension_method": False,
                    "invokes_slicer_api": False,
                },
                "sub_operations": [{
                    "op_type": "extension_op",
                    "description": "Change a Slicer view",
                    "extension_method_hint": None,
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("extension_op without an extension method" in e for e in validation["errors"]))

        # Destructive operations require an explicit contract.
        validation = analyzer._stage9_validate(
            {"templates/cb_step_2.py.tpl": "displayNode.RemoveAllViewNodeIDs()"},
            [{
                "template_file": "templates/cb_step_2.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                },
                "sub_operations": [{"op_type": "slicer_op", "description": "Set display views"}],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("destructive operations" in e for e in validation["errors"]))

        # Display view-list resets are allowed only when followed by explicit scoped view IDs.
        # Slice-view targets also require class-specific 2D/slice visibility handling.
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2b.py.tpl": (
                    "displayNode.RemoveAllViewNodeIDs()\n"
                    "displayNode.AddViewNodeID('vtkMRMLViewNode1')\n"
                    "displayNode.AddViewNodeID('vtkMRMLSliceNodeRed')\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2b.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["view_display_scope"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Set markup display views",
                    "slicer_op_category": "markups_display",
                    "node_class": "vtkMRMLMarkupsDisplayNode",
                    "slicer_api_keywords": ["Display", "View", "Red"],
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("Markups display step targets a slice view" in e for e in validation["errors"]))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2c.py.tpl": (
                    "displayNode.SetVisibility(True)\n"
                    "displayNode.SetSliceProjection(True)\n"
                    "displayNode.RemoveAllViewNodeIDs()\n"
                    "displayNode.AddViewNodeID('vtkMRMLViewNode1')\n"
                    "displayNode.AddViewNodeID('vtkMRMLSliceNodeRed')\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2c.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["view_display_scope"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Set markup display views",
                    "slicer_op_category": "markups_display",
                    "node_class": "vtkMRMLMarkupsDisplayNode",
                    "slicer_api_keywords": ["Display", "View", "Red"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2d.py.tpl": (
                    "modelDisplayNode.SetVisibility(True)\n"
                    "modelDisplayNode.RemoveAllViewNodeIDs()\n"
                    "modelDisplayNode.AddViewNodeID('vtkMRMLSliceNodeRed')\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2d.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["view_display_scope"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Show model in Red slice view",
                    "slicer_op_category": "node_display",
                    "node_class": "vtkMRMLModelNode",
                    "slicer_api_keywords": ["Display", "Red"],
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("Model display step targets a slice view" in e for e in validation["errors"]))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2e.py.tpl": (
                    "modelDisplayNode.SetVisibility(True)\n"
                    "modelDisplayNode.SetVisibility2D(True)\n"
                    "modelDisplayNode.RemoveAllViewNodeIDs()\n"
                    "modelDisplayNode.AddViewNodeID('vtkMRMLSliceNodeRed')\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2e.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["view_display_scope"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Show model in Red slice view",
                    "slicer_op_category": "node_display",
                    "node_class": "vtkMRMLModelNode",
                    "slicer_api_keywords": ["Display", "Red"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        # Automated display-view operations must not switch the active Slicer module.
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2b_module.py.tpl": (
                    "slicer.util.selectModule('Markups')\n"
                    "displayNode.AddViewNodeID('vtkMRMLViewNode1')\n"
                    "displayNode.AddViewNodeID('vtkMRMLSliceNodeRed')\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2b_module.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "allow_module_switch": False,
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Configure Markups display View to show in View 1 and Red",
                    "slicer_op_category": "markups_display",
                    "slicer_api_keywords": ["Display", "View"],
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("switches the active Slicer module" in e for e in validation["errors"]))

        # Explicit module-switch steps may still use selectModule.
        validation = analyzer._stage9_validate(
            {"templates/cb_step_2b_explicit_module.py.tpl": "slicer.util.selectModule('Markups')\n"},
            [{
                "template_file": "templates/cb_step_2b_explicit_module.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "allow_module_switch": True,
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Switch to the Markups module",
                    "slicer_op_category": "module_switching",
                    "slicer_api_keywords": ["selectModule"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        # Runtime prelude is generated for defaults even when the user has not answered a choice.
        from SlicerAIAgentLib.ExtensionCLILoader import _WorkflowContext, _build_choice_prelude
        ctx = _WorkflowContext(
            ext_name="Generic",
            ext_dir="",
            tool_name="Generic",
            workflow_graph={},
            target_step={"step_id": "cb_step_1"},
            target_gen=None,
            arguments={},
            user_action="start",
            done=set(),
            metadata={
                "extension_module_name": "GenericExtension",
                "logic_class_name": "GenericLogic",
                "parameter_bindings": {
                    "initialSpace": {
                        "role": "initialSpace",
                        "accesses": ["parameter_read"],
                        "value_types": ["float"],
                    }
                },
                "parameter_defaults": {
                    "initialSpace": {
                        "value": "1.5",
                        "value_type": "float",
                        "source": "ui_widget_default",
                    }
                },
            },
        )
        prelude = _build_choice_prelude(ctx)
        self.assertIn("_workflow_defaults", prelude)
        self.assertIn("parameterNode.SetParameter(_role", prelude)

        # Fallback node resolution must not use a different Markups class than metadata expects.
        analyzer._workflow_metadata = {
            "parameter_bindings": {
                "fibulaLine": {
                    "role": "fibulaLine",
                    "node_class": "vtkMRMLMarkupsLineNode",
                }
            }
        }
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_node_class.py.tpl": (
                    "role = 'fibulaLine'\n"
                    "nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsCurveNode')\n"
                )
            },
            [{
                "template_file": "templates/cb_step_node_class.py.tpl",
                "step_type": "automated",
                "op_type": "extension_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["extension_op"],
                    "invokes_extension_method": True,
                },
                "sub_operations": [{
                    "op_type": "extension_op",
                    "description": "Resolve fibula line.",
                    "extension_method_hint": "centerLine",
                }],
            }],
            logic_analysis={"methods": [{"name": "centerLine", "parameters": []}]},
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("metadata expects vtkMRMLMarkupsLineNode" in e for e in validation["errors"]))

        # Slice intersection visibility must visibly refresh slice views when
        # implemented through direct slice display-node setters.
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2c.py.tpl": (
                    "sliceDisplayNodes = slicer.util.getNodesByClass('vtkMRMLSliceDisplayNode')\n"
                    "for sliceDisplayNode in sliceDisplayNodes:\n"
                    "    sliceDisplayNode.SetIntersectingSlicesVisibility(True)\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2c.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["slice_intersection_visibility"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Toggle on slice intersection visibility.",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["crosshair"],
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("Slice intersection visibility step must use" in e for e in validation["errors"]))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2c_refresh.py.tpl": (
                    "sliceDisplayNodes = slicer.util.getNodesByClass('vtkMRMLSliceDisplayNode')\n"
                    "for sliceDisplayNode in sliceDisplayNodes:\n"
                    "    sliceDisplayNode.SetIntersectingSlicesVisibility(True)\n"
                    "sliceNodes = slicer.util.getNodesByClass('vtkMRMLSliceNode')\n"
                    "for sliceNode in sliceNodes:\n"
                    "    sliceNode.Modified()\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2c_refresh.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["slice_intersection_visibility"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Toggle on slice intersection visibility.",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["slice intersection visibility"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2c_app_logic.py.tpl": (
                    "appLogic = slicer.app.applicationLogic()\n"
                    "appLogic.SetIntersectingSlicesEnabled("
                    "appLogic.IntersectingSlicesVisibility, True)\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2c_app_logic.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["slice_intersection_visibility"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Turn on slice intersection visibility.",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["slice intersection visibility"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2c_crosshair.py.tpl": (
                    "crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')\n"
                    "crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowBasic)\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2c_crosshair.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                    "operation_intents": ["slice_intersection_visibility"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Turn on slice intersection visibility.",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["slice intersection visibility"],
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("crosshair visibility APIs" in e for e in validation["errors"]))

        # Final-state Slicer operations must not invert current state.
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2c_state.py.tpl": (
                    "appLogic = slicer.app.applicationLogic()\n"
                    "currentVisibility = appLogic.GetIntersectingSlicesEnabled(None)\n"
                    "appLogic.SetIntersectingSlicesEnabled(None, not currentVisibility)\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2c_state.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Toggle on slice intersection visibility.",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["visibility"],
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("Final-state operation requests" in e for e in validation["errors"]))

        # Per-template API evidence can validate new Slicer API footprints
        # without adding category-specific validator hints.
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_2d.py.tpl": (
                    "controller = slicer.app.applicationLogic()\n"
                    "controller.SetNewSlicerApiVariant(True)\n"
                )
            },
            [{
                "template_file": "templates/cb_step_2d.py.tpl",
                "step_type": "automated",
                "op_type": "slicer_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["slicer_op"],
                    "invokes_slicer_api": True,
                },
                "api_evidence": {
                    "accepted_footprints": ["SetNewSlicerApiVariant"],
                    "api_chains": ["controller.SetNewSlicerApiVariant"],
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Use a newly discovered Slicer API variant.",
                    "slicer_op_category": "unknown_future_category",
                    "slicer_api_keywords": ["not_in_template"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        evidence = analyzer._build_template_api_evidence(
            (
                "nodes = slicer.util.getNodesByClass('vtkMRMLSliceDisplayNode')\n"
                "for node in nodes:\n"
                "    node.SetIntersectingSlicesVisibility(True)\n"
            ),
            {
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Toggle slice intersections",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["crosshair"],
                }]
            },
        )
        self.assertIn("SetIntersectingSlicesVisibility", evidence["accepted_footprints"])
        self.assertIn("vtkMRMLSliceDisplayNode", evidence["accepted_footprints"])

        # Extension-owned interactions must not create a second Markups node.
        validation = analyzer._stage9_validate(
            {"templates/cb_step_3_pre.py.tpl": "node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', 'L')"},
            [{
                "pre_template_file": "templates/cb_step_3_pre.py.tpl",
                "step_type": "interactive",
                "interaction_descriptor": {
                    "node_class": "vtkMRMLMarkupsLineNode",
                    "interaction_owner": "previous_extension_method",
                    "placement_starter_method": "addLine",
                },
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("pre-template creates a new Markups node" in e for e in validation["errors"]))

        # Repeat groups cannot call the same placement starter in both start and interaction steps.
        contract = analyzer._validate_generator_contracts([
            {
                "step_type": "automated",
                "param_signature": {"workflow_step": "cb_step_4"},
                "interaction_descriptor": {"placement_starter_method": "addPlane"},
            },
            {
                "step_type": "mixed",
                "param_signature": {"workflow_step": "cb_step_5"},
                "repeat_group": {
                    "group_id": "repeat_cb_step_4_cb_step_5",
                    "start_step": "cb_step_4",
                    "interaction_step": "cb_step_5",
                },
                "interaction_descriptor": {
                    "node_class": "vtkMRMLMarkupsPlaneNode",
                    "interaction_owner": "extension_method",
                    "placement_starter_method": "addPlane",
                },
            },
        ])
        self.assertTrue(any("both call placement starter" in e for e in contract["errors"]))

        # Normalization removes duplicate repeat starter ownership before templates are built.
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fp:
            fp.write(
                "def setCustomLayout():\n"
                "    slicer.app.layoutManager().setLayout(123)\n"
            )
            module_source = fp.name
        try:
            analyzer._placement_starter_methods = {"addPlane": {"node_classes": ["vtkMRMLMarkupsPlaneNode"]}}
            workflow_graph = {
                "steps": [
                    {
                        "step_id": "cb_step_1",
                        "step_type": "user_choice",
                        "op_type": "user_choice",
                        "description": "How many planes are needed?",
                        "choice_info": {
                            "question": "How many planes?",
                            "parameter_name": "number_of_planes",
                            "choices": [],
                        },
                        "sub_operations": [{"op_type": "user_choice"}],
                    },
                    {
                        "step_id": "cb_step_2",
                        "step_type": "automated",
                        "op_type": "extension_op",
                        "description": "Click Add plane.",
                        "method_name": "addPlane",
                        "sub_operations": [{
                            "op_type": "extension_op",
                            "description": "Add a plane.",
                            "extension_method_hint": "addPlane",
                        }],
                    },
                    {
                        "step_id": "cb_step_3",
                        "step_type": "mixed",
                        "op_type": "mixed",
                        "description": "Repeat adding and placing a plane for each requested plane.",
                        "sub_operations": [
                            {
                                "op_type": "extension_op",
                                "description": "Add a plane.",
                                "extension_method_hint": "addPlane",
                            },
                            {
                                "op_type": "user_interaction",
                                "description": "Place the plane.",
                                "node_class": "vtkMRMLMarkupsPlaneNode",
                                "interaction_kind": "markup_placement",
                            },
                        ],
                    },
                    {
                        "step_id": "cb_step_4",
                        "step_type": "automated",
                        "op_type": "extension_op",
                        "description": "Restore the custom layout.",
                        "sub_operations": [{
                            "op_type": "extension_op",
                            "description": "Restore the custom layout.",
                            "extension_method_hint": None,
                        }],
                    },
                ]
            }
            repeat_group = {
                "group_id": "repeat_cb_step_1_cb_step_2_cb_step_3",
                "count_parameter": "number_of_planes",
                "count_step": "cb_step_1",
                "start_step": "cb_step_2",
                "interaction_step": "cb_step_3",
            }
            for step in workflow_graph["steps"][:3]:
                step["repeat_group"] = repeat_group
            metadata = {
                "repeat_groups": {repeat_group["group_id"]: repeat_group},
                "choice_bindings": {},
                "interaction_bindings": {},
                "parameter_bindings": {},
            }
            analyzer._normalize_workflow_contracts(
                workflow_graph,
                metadata,
                {"entry_module": module_source, "logic_class": {"class_name": "GenericLogic"}},
                {"methods": []},
            )
            interaction_step = workflow_graph["steps"][2]
            self.assertEqual(interaction_step["step_type"], "interactive")
            self.assertEqual(interaction_step["interaction_owner"], "previous_extension_method")
            self.assertFalse(any(
                so.get("extension_method_hint") == "addPlane"
                for so in interaction_step["sub_operations"]
            ))
            layout_step = workflow_graph["steps"][3]
            self.assertEqual(layout_step["extension_function_name"], "setCustomLayout")
            self.assertEqual(
                layout_step["sub_operations"][0]["extension_function_hint"],
                "setCustomLayout",
            )
        finally:
            os.unlink(module_source)

        # Placement starters remain bound across intervening Slicer configuration steps.
        analyzer._placement_starter_methods = {
            "addCurve": {
                "node_classes": ["vtkMRMLMarkupsCurveNode"],
                "starts_markup_placement": True,
                "placement_mode": "single",
            }
        }
        workflow_graph = {
            "steps": [
                {
                    "step_id": "cb_step_10",
                    "step_type": "automated",
                    "op_type": "extension_op",
                    "description": "Click Add curve.",
                    "method_name": "addCurve",
                    "sub_operations": [{
                        "op_type": "extension_op",
                        "description": "Click Add curve.",
                        "extension_method_hint": "addCurve",
                    }],
                },
                {
                    "step_id": "cb_step_11",
                    "step_type": "automated",
                    "op_type": "slicer_op",
                    "description": "Show the active curve in the desired views.",
                    "sub_operations": [{
                        "op_type": "slicer_op",
                        "description": "Show the active curve in the desired views.",
                    }],
                },
                {
                    "step_id": "cb_step_12",
                    "step_type": "interactive",
                    "op_type": "user_interaction",
                    "description": "Manually draw the curve.",
                    "node_class": "vtkMRMLMarkupsCurveNode",
                    "interaction_kind": "markup_placement",
                    "sub_operations": [{
                        "op_type": "user_interaction",
                        "description": "Manually draw the curve.",
                        "node_class": "vtkMRMLMarkupsCurveNode",
                        "interaction_kind": "markup_placement",
                    }],
                },
            ]
        }
        metadata = {
            "repeat_groups": {},
            "choice_bindings": {},
            "interaction_bindings": {},
            "parameter_bindings": {},
        }
        analyzer._normalize_workflow_contracts(
            workflow_graph,
            metadata,
            {"entry_module": "", "logic_class": {"class_name": "GenericLogic"}},
            {"methods": []},
        )
        interaction_step = workflow_graph["steps"][2]
        self.assertEqual(interaction_step["interaction_owner"], "previous_extension_method")
        self.assertEqual(interaction_step["placement_starter_method"], "addCurve")
        self.assertEqual(interaction_step["placement_starter_step_id"], "cb_step_10")
        self.assertEqual(
            metadata["interaction_policies"]["cb_step_12"]["placement_binding_reason"],
            "recent_same_node_class_placement_starter",
        )

        # Placement-starter classification records source-derived placement mode.
        placement_source = """
class GenericLogic:
    def addPlane(self):
        node = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
        slicer.mrmlScene.AddNode(node)
        slicer.modules.markups.logic().SetActiveListID(node)
        interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        interactionNode.SwitchToSinglePlaceMode()

    def addPoint(self):
        node = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
        slicer.mrmlScene.AddNode(node)
        slicer.modules.markups.logic().SetActiveListID(node)
        interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        interactionNode.SwitchToPersistentPlaceMode()
"""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fp:
            fp.write(placement_source)
            placement_file = fp.name
        try:
            starters = analyzer._classify_placement_starter_methods({
                "_logic_file": placement_file,
                "methods": [{"name": "addPlane"}, {"name": "addPoint"}],
            })
            self.assertEqual(starters["addPlane"]["placement_mode"], "single")
            self.assertEqual(starters["addPoint"]["placement_mode"], "persistent")
            self.assertTrue(starters["addPlane"]["starts_markup_placement"])
        finally:
            os.unlink(placement_file)

        # Extension-owned repeated interactions preserve the starter's placement mode.
        analyzer._placement_starter_methods = {
            "addPlane": {
                "node_classes": ["vtkMRMLMarkupsPlaneNode"],
                "starts_markup_placement": True,
                "placement_mode": "single",
            }
        }
        repeat_group = {
            "group_id": "repeat_count_add_place",
            "count_step": "cb_step_1",
            "start_step": "cb_step_2",
            "interaction_step": "cb_step_3",
        }
        repeated_step = {
            "step_id": "cb_step_3",
            "description": "Place a plane. Repeat for each requested plane.",
            "node_class": "vtkMRMLMarkupsPlaneNode",
            "interaction_type": "plane",
            "interaction_owner": "previous_extension_method",
            "placement_starter_method": "addPlane",
            "repeat_group": repeat_group,
            "sub_operations": [{
                "op_type": "user_interaction",
                "node_class": "vtkMRMLMarkupsPlaneNode",
                "placement_instructions": "Place a plane. Repeat for each requested plane.",
            }],
        }
        analyzer._normalize_repeat_interaction_instructions(repeated_step)
        pre_tpl = analyzer._generate_existing_placement_pre_template(
            "GenericExtension",
            repeated_step,
            "addPlane",
        )
        self.assertNotIn("SwitchToPersistentPlaceMode", pre_tpl)
        self.assertNotIn("SwitchToSinglePlaceMode", pre_tpl)
        self.assertNotIn("SetActiveListID", pre_tpl)
        self.assertIn("Place this plane, then click Done.", pre_tpl)

        validation = analyzer._stage9_validate(
            {"templates/cb_step_3_pre.py.tpl": pre_tpl},
            [{
                "pre_template_file": "templates/cb_step_3_pre.py.tpl",
                "step_type": "interactive",
                "param_signature": {"workflow_step": "cb_step_3"},
                "repeat_group": repeat_group,
                "interaction_descriptor": {
                    "node_class": "vtkMRMLMarkupsPlaneNode",
                    "interaction_owner": "previous_extension_method",
                    "placement_starter_method": "addPlane",
                    "repeat_group": repeat_group,
                },
            }],
        )
        self.assertTrue(validation["valid"], validation["errors"])

        bad_validation = analyzer._stage9_validate(
            {
                "templates/cb_step_3_pre.py.tpl": (
                    "interactionNode = slicer.mrmlScene.GetNodeByID('vtkMRMLInteractionNodeSingleton')\n"
                    "interactionNode.SwitchToPersistentPlaceMode()\n"
                    "print('Repeat for each requested plane')\n"
                )
            },
            [{
                "pre_template_file": "templates/cb_step_3_pre.py.tpl",
                "step_type": "interactive",
                "param_signature": {"workflow_step": "cb_step_3"},
                "repeat_group": repeat_group,
                "interaction_descriptor": {
                    "node_class": "vtkMRMLMarkupsPlaneNode",
                    "interaction_owner": "previous_extension_method",
                    "placement_starter_method": "addPlane",
                    "repeat_group": repeat_group,
                },
            }],
        )
        self.assertFalse(bad_validation["valid"])
        self.assertTrue(any("enters Markups placement mode" in e for e in bad_validation["errors"]))
        self.assertTrue(any("persistent placement mode" in e for e in bad_validation["errors"]))

        # Runtime-created repeated markup placement uses one item per Done.
        runtime_step = {
            "step_id": "cb_step_6",
            "description": "Place one point for each requested item.",
            "node_class": "vtkMRMLMarkupsFiducialNode",
            "interaction_type": "fiducial",
            "interaction_owner": "runtime_template",
            "repeat_group": {
                "group_id": "repeat_count_place",
                "count_step": "cb_step_4",
                "start_step": "cb_step_6",
                "interaction_step": "cb_step_6",
            },
        }
        runtime_tpl = analyzer._generate_pre_interaction_template(
            "GenericExtension",
            runtime_step,
            "GenericLogic",
            "GenericExtension",
        )
        self.assertIn("SwitchToSinglePlaceMode", runtime_tpl)
        self.assertNotIn("SwitchToPersistentPlaceMode", runtime_tpl)

        contract = analyzer._validate_generator_contracts([{
            "step_type": "interactive",
            "param_signature": {"workflow_step": "cb_step_6"},
            "repeat_group": runtime_step["repeat_group"],
            "interaction_descriptor": {
                "node_class": "vtkMRMLMarkupsFiducialNode",
                "placement_instructions": "Repeat for each requested point.",
                "repeat_group": runtime_step["repeat_group"],
            },
        }])
        self.assertTrue(any("one item per Done" in e for e in contract["errors"]))

        # Generation-time UI guidance is distinct from cookbook text and repeat-aware.
        guidance_graph = {
            "steps": [
                {
                    "step_id": "cb_step_16",
                    "step_type": "user_choice",
                    "description": "Set how many cut planes to create.",
                    "choice_info": {
                        "question": "How many mandibular cutting planes would you like to create?",
                        "choices": [],
                        "parameter_name": "numberOfCutPlanes",
                        "default_value": "1",
                    },
                },
                {
                    "step_id": "cb_step_18",
                    "step_type": "interactive",
                    "description": "Place cut plane. Repeat for each requested plane.",
                    "node_class": "vtkMRMLMarkupsPlaneNode",
                    "interaction_type": "plane",
                    "repeat_group": {
                        "group_id": "repeat_cut_planes",
                        "count_step": "cb_step_16",
                        "start_step": "cb_step_17",
                        "interaction_step": "cb_step_18",
                    },
                    "sub_operations": [{
                        "op_type": "user_interaction",
                        "node_class": "vtkMRMLMarkupsPlaneNode",
                    }],
                },
            ],
            "step_count": 2,
        }
        analyzer._synthesize_workflow_ui_guidance(
            guidance_graph,
            {},
            {"logic_class": {"class_name": "GenericLogic"}},
            {"methods": []},
        )
        choice_guidance = guidance_graph["steps"][0]["ui_guidance"]
        self.assertEqual(choice_guidance["input_label"], "Number of cutting planes")
        repeat_guidance = guidance_graph["steps"][1]["ui_guidance"]
        self.assertIn("cutting plane", repeat_guidance["title"].lower())
        self.assertIn("click Done", repeat_guidance["instruction"])
        self.assertNotIn("Repeat for each", repeat_guidance["instruction"])

        # Invalid LLM guidance falls back deterministically.
        analyzer.llm_client = object()
        analyzer._call_llm = lambda prompt: "not json"
        fallback_graph = {
            "steps": [{
                "step_id": "cb_step_1",
                "step_type": "interactive",
                "description": "Draw the contour.",
                "node_class": "vtkMRMLMarkupsCurveNode",
                "sub_operations": [{"op_type": "user_interaction", "node_class": "vtkMRMLMarkupsCurveNode"}],
            }]
        }
        analyzer._synthesize_workflow_ui_guidance(
            fallback_graph,
            {},
            {"logic_class": {"class_name": "GenericLogic"}},
            {"methods": []},
        )
        self.assertEqual(fallback_graph["steps"][0]["ui_guidance"]["title"], "Draw curve")

        # Loader results carry generated guidance and repeat progress.
        from SlicerAIAgentLib.ExtensionCLILoader import (
            _WorkflowContext,
            _handle_interactive_start,
            _handle_user_choice_step,
            _workflow_repeat_state,
        )
        _workflow_repeat_state.clear()
        loader_step = {
            "step_id": "cb_step_18",
            "step_type": "interactive",
            "description": "Raw cookbook placement text.",
            "ui_guidance": repeat_guidance,
            "repeat_group": guidance_graph["steps"][1]["repeat_group"],
        }
        loader_gen = {
            "step_type": "interactive",
            "pre_template_file": "",
            "post_template_file": "",
            "interaction_descriptor": {
                "node_class": "vtkMRMLMarkupsPlaneNode",
                "placement_instructions": "Raw placement instructions.",
                "ui_guidance": repeat_guidance,
                "repeat_group": guidance_graph["steps"][1]["repeat_group"],
            },
            "repeat_group": guidance_graph["steps"][1]["repeat_group"],
        }
        _workflow_repeat_state["GenericExtension"] = {
            "repeat_cut_planes": {"target": 3, "completed": 1}
        }
        ctx = _WorkflowContext(
            "GenericExtension", tempfile.gettempdir(), "GenericExtension",
            {"steps": [loader_step]}, loader_step, loader_gen,
            {"workflow_step": "cb_step_18", "user_action": "start"},
            "start", set(), {},
        )
        loader_result = _handle_interactive_start(ctx)
        self.assertEqual(loader_result["ui_guidance"]["title"], repeat_guidance["title"])
        self.assertEqual(loader_result["repeat_progress"]["current"], 2)
        self.assertEqual(loader_result["repeat_progress"]["total"], 3)

        choice_step = guidance_graph["steps"][0]
        choice_gen = {
            "step_type": "user_choice",
            "choice_descriptor": {
                "question": choice_step["choice_info"]["question"],
                "choices": [],
                "parameter_name": "numberOfCutPlanes",
                "default_value": "1",
                "ui_guidance": choice_guidance,
            },
        }
        choice_ctx = _WorkflowContext(
            "GenericExtension", tempfile.gettempdir(), "GenericExtension",
            {"steps": [choice_step]}, choice_step, choice_gen,
            {"workflow_step": "cb_step_16", "user_action": "start"},
            "start", set(), {},
        )
        choice_result = _handle_user_choice_step(choice_ctx)
        self.assertEqual(choice_result["ui_guidance"]["input_label"], "Number of cutting planes")

        # Acronym-heavy extension layout helpers still match custom-layout cookbook text.
        layout_source = """
def addBRPLayout():
    layoutNode = slicer.mrmlScene.GetSingletonNode('vtkMRMLLayoutNodeSingleton', 'vtkMRMLLayoutNode')
    layoutNode.AddLayoutDescription(slicer.BRPLayoutId, '<layout/>')

def setBRPLayout():
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.BRPLayoutId)
"""
        layout_tree = ast.parse(layout_source)
        layout_inventory = {}
        for node in layout_tree.body:
            if isinstance(node, ast.FunctionDef):
                layout_inventory[node.name] = {
                    "name": node.name,
                    "effects": analyzer._infer_callable_effects(
                        node,
                        ast.get_source_segment(layout_source, node) or "",
                    ),
                }
        self.assertEqual(layout_inventory["addBRPLayout"]["effects"], ["layout_register"])
        self.assertEqual(layout_inventory["setBRPLayout"]["effects"], ["layout_activate"])
        self.assertEqual(
            analyzer._match_extension_function(
                "Restore the BoneReconstructionPlanner custom layout registered by the extension.",
                ["setBRPLayout"],
            ),
            "setBRPLayout",
        )
        self.assertEqual(
            analyzer._match_extension_function(
                "Change the layout to BoneReconstructionPlanner.",
                ["addBRPLayout", "setBRPLayout"],
                layout_inventory,
            ),
            "setBRPLayout",
        )
        self.assertIsNone(
            analyzer._match_extension_function(
                "Restore the BoneReconstructionPlanner custom layout registered by the extension.",
                ["addBRPLayout"],
                layout_inventory,
            )
        )

        analyzer._workflow_metadata = {
            "extension_callable_inventory": {
                "module_functions": ["addBRPLayout", "setBRPLayout"],
                "module_function_effects": {
                    "addBRPLayout": ["layout_register"],
                    "setBRPLayout": ["layout_activate"],
                },
            }
        }
        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_layout_bad.py.tpl": (
                    "from BoneReconstructionPlanner import addBRPLayout\n"
                    "addBRPLayout()\n"
                )
            },
            [{
                "template_file": "templates/cb_step_layout_bad.py.tpl",
                "step_type": "automated",
                "op_type": "extension_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["extension_op"],
                    "invokes_extension_function": True,
                    "operation_intents": ["layout_activate"],
                },
                "sub_operations": [{
                    "op_type": "extension_op",
                    "description": "Change the layout to BoneReconstructionPlanner.",
                    "extension_function_hint": "addBRPLayout",
                }],
            }],
        )
        self.assertFalse(validation["valid"])
        self.assertTrue(any("Layout activation step" in e for e in validation["errors"]))

        validation = analyzer._stage9_validate(
            {
                "templates/cb_step_layout_good.py.tpl": (
                    "from BoneReconstructionPlanner import setBRPLayout\n"
                    "setBRPLayout()\n"
                )
            },
            [{
                "template_file": "templates/cb_step_layout_good.py.tpl",
                "step_type": "automated",
                "op_type": "extension_op",
                "operation_model": {
                    "step_type": "automated",
                    "op_types": ["extension_op"],
                    "invokes_extension_function": True,
                    "operation_intents": ["layout_activate"],
                },
                "sub_operations": [{
                    "op_type": "extension_op",
                    "description": "Change the layout to BoneReconstructionPlanner.",
                    "extension_function_hint": "setBRPLayout",
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))
        analyzer._workflow_metadata = {}

        # Template repairs synchronize extension-function evidence back to generator contracts.
        analyzer._workflow_metadata = {
            "extension_callable_inventory": {
                "module_functions": ["setBRPLayout"],
            }
        }
        workflow_graph = {
            "steps": [{
                "step_id": "cb_step_9",
                "step_type": "automated",
                "op_type": "extension_op",
                "description": "Restore custom layout.",
                "sub_operations": [{
                    "op_type": "extension_op",
                    "description": "Restore custom layout.",
                    "extension_method_hint": None,
                }],
            }]
        }
        generators = [{
            "template_file": "templates/cb_step_9.py.tpl",
            "step_type": "automated",
            "op_type": "extension_op",
            "param_signature": {"workflow_step": "cb_step_9"},
            "sub_operations": [{
                "op_type": "extension_op",
                "description": "Restore custom layout.",
                "extension_method_hint": None,
            }],
        }]
        analyzer._sync_template_contracts(
            {
                "templates/cb_step_9.py.tpl": (
                    "from GenericExtension import setBRPLayout\n"
                    "setBRPLayout()\n"
                )
            },
            generators,
            workflow_graph=workflow_graph,
        )
        self.assertEqual(generators[0]["extension_function_name"], "setBRPLayout")
        self.assertTrue(generators[0]["operation_model"]["invokes_extension_function"])
        self.assertEqual(
            workflow_graph["steps"][0]["sub_operations"][0]["extension_function_hint"],
            "setBRPLayout",
        )

        syntax_issues = analyzer._syntax_check_templates({
            "templates/good.py.tpl": "x = {value: 1}\n",
            "templates/bad.py.tpl": "if True print('bad')\n",
        })
        self.assertEqual(len(syntax_issues), 1)
        self.assertEqual(syntax_issues[0]["template"], "templates/bad.py.tpl")

        # Implementation-level Slicer scaffolding is allowed when explicitly modeled.
        validation = analyzer._stage9_validate(
            {"templates/cb_step_6_pre.py.tpl": "slicer.mrmlScene.GetNodeByID('vtkMRMLInteractionNodeSingleton')"},
            [{
                "pre_template_file": "templates/cb_step_6_pre.py.tpl",
                "step_type": "interactive",
                "operation_model": {
                    "step_type": "interactive",
                    "op_types": ["user_interaction"],
                    "invokes_slicer_api": False,
                    "implementation_uses_slicer_api": True,
                },
                "interaction_descriptor": {
                    "node_class": "vtkMRMLMarkupsPlaneNode",
                    "interaction_owner": "previous_extension_method",
                    "placement_starter_method": "addPlane",
                },
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

        # Previous-step-owned repeat interactions can reference the starter without being treated as a second call.
        contract = analyzer._validate_generator_contracts([
            {
                "step_type": "automated",
                "param_signature": {"workflow_step": "cb_step_7"},
                "sub_operations": [{
                    "op_type": "extension_op",
                    "extension_method_hint": "addPlane",
                }],
            },
            {
                "step_type": "interactive",
                "param_signature": {"workflow_step": "cb_step_8"},
                "repeat_group": {
                    "group_id": "repeat_cb_step_7_cb_step_8",
                    "start_step": "cb_step_7",
                    "interaction_step": "cb_step_8",
                },
                "interaction_descriptor": {
                    "node_class": "vtkMRMLMarkupsPlaneNode",
                    "interaction_owner": "previous_extension_method",
                    "placement_starter_method": "addPlane",
                },
            },
        ])
        self.assertFalse(contract["errors"], contract["errors"])

        # Multi-line cookbook descriptions must not create bare indented Python text.
        multiline_step = dict(repeated_step)
        multiline_step["description"] = (
            "Place the fibular cut plane.\n"
            "This can be translated and rotated in slice views."
        )
        multiline_tpl = analyzer._generate_existing_placement_pre_template(
            "GenericExtension",
            multiline_step,
            "addPlane",
        )
        ast.parse(analyzer._fill_remaining_placeholders(multiline_tpl))
        self.assertIn("# This can be translated", multiline_tpl)

        # Sanitization repairs LLM-revised templates with split raw headers.
        sanitized = analyzer._sanitize_templates({
            "templates/cb_step_18_pre.py.tpl": (
                "# --- GenericExtension: Place the fibular cut plane.\n"
                "  This can be translated and rotated in slice views. (Setup) ---\n"
                "import slicer\n"
            )
        })
        ast.parse(sanitized["templates/cb_step_18_pre.py.tpl"])
        self.assertIn(
            "# This can be translated and rotated",
            sanitized["templates/cb_step_18_pre.py.tpl"],
        )

        # Placeholder filling for validation preserves braces inside Python strings/f-strings.
        filled = analyzer._fill_remaining_placeholders(
            "for ref_name in ['Mandible']:\n"
            "    print(f'Missing {ref_name}')\n"
            "threshold = {threshold: 1.0}\n"
        )
        self.assertIn("{ref_name}", filled)
        self.assertIn("threshold = 1.0", filled)
        ast.parse(filled)

        # Semantic validation recognizes tuple-unpacked loop variables.
        semantic = analyzer._semantic_validate(
            "required_refs = [('a', 'b', 1)]\n"
            "for ref_name, param_name, default_value in required_refs:\n"
            "    print(f'{ref_name}: {param_name}={default_value}')\n",
            {"methods": []},
        )
        self.assertFalse(semantic["errors"], semantic["errors"])

        self.delayDisplay("ExtensionCLIAnalyzer contract tests passed")
