"""
Unit tests for SlicerAIAgent extension.

Run these tests from Slicer's Python console:
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('SlicerAIAgentTest')
    unittest.TextTestRunner(verbosity=2).run(suite)
"""

import os
import sys
import unittest
import tempfile
import shutil

import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SlicerAIAgentTest(ScriptedLoadableModuleTest):
    """
    Comprehensive test suite for SlicerAIAgent.
    """

    def setUp(self):
        """Setup for each test - clear the scene."""
        slicer.mrmlScene.Clear(0)

    def tearDown(self):
        """Cleanup after each test."""
        pass

    def runTest(self):
        """Run all tests."""
        self.setUp()
        self.test_ModuleImport()
        self.tearDown()
        
        self.setUp()
        self.test_LLMClient()
        self.tearDown()
        
        self.setUp()
        self.test_CodeValidator()
        self.tearDown()

        self.setUp()
        self.test_ExtensionCLIAnalyzerContracts()
        self.tearDown()

        self.setUp()
        self.test_TurnRouterWorkflowRoutes()
        self.tearDown()

        self.setUp()
        self.test_WorkflowRuntimeStateTransitions()
        self.tearDown()

        self.setUp()
        self.test_NodeChoiceResolverContracts()
        self.tearDown()
        
        self.setUp()
        self.test_SafeExecutor()
        self.tearDown()
        
        self.setUp()
        self.test_SkillPath()
        self.tearDown()
        
        self.setUp()
        self.test_ConversationStore()
        self.tearDown()
        
        self.setUp()
        self.test_SlicerCodeTemplates()
        self.tearDown()
        
        self.setUp()
        self.test_SkillIndexer()
        self.tearDown()
        
        self.setUp()
        self.test_Integration()
        self.tearDown()
        
        self.setUp()
        self.test_GenerateSegmentationCode()
        self.tearDown()

    def test_ModuleImport(self):
        """Test that all module components can be imported."""
        try:
            from SlicerAIAgentLib import (
                LLMClient,
                SkillTools,
                SkillIndexer,
                CodeValidator,
                SafeExecutor,
                ConversationStore,
                SlicerCodeTemplates,
                TurnRouter,
                WorkflowRuntime,
                NodeChoiceResolver,
            )
            self.delayDisplay("All module components imported successfully")
        except Exception as e:
            self.delayDisplay(f"Module import failed: {e}")
            raise

    def test_LLMClient(self):
        """Test LLMClient functionality."""
        from SlicerAIAgentLib import LLMClient

        client = LLMClient()

        # Test defaults
        self.assertEqual(client.model, "kimi-k2.5")
        self.assertIsNone(client.timeout)

        # Test API key management
        client.setApiKey("test_key")
        self.assertEqual(client.api_key, "test_key")

        # Test model selection and legacy normalization
        client.setModel("moonshot-v1-8k")
        self.assertEqual(client.model, "moonshot-v1-8k")
        client.setModel("kimi-latest")
        self.assertEqual(client.model, "kimi-k2.5")

        # Test DeepSeek model support
        client.setModel("deepseek-v4-pro")
        self.assertEqual(client.model, "deepseek-v4-pro")
        self.assertTrue(client._supportsThinking())
        client.setModel("deepseek-v4-flash")
        self.assertEqual(client.model, "deepseek-v4-flash")
        self.assertTrue(client._supportsThinking())

        # Test conversation history
        client.clearHistory()
        self.assertEqual(len(client.conversation_history), 0)

        # Test history management
        client.conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there", "reasoning_content": "Thinking..."},
        ]
        self.assertEqual(len(client.getHistory()), 2)

        client.clearHistory()
        self.assertEqual(len(client.getHistory()), 0)

        # Test code extraction
        message_with_code = """
Here's some code:
```python
x = 1 + 1
print(x)
```
More text.
"""
        code = client._extractCode(message_with_code)
        self.assertIsNotNone(code)
        self.assertIn("x = 1 + 1", code)

        # Test SSE parsing helpers
        done_chunk = client._parseStreamChunk("[DONE]")
        self.assertTrue(done_chunk["done"])

        reasoning_chunk = client._parseStreamChunk('{\"choices\":[{\"delta\":{\"reasoning_content\":\"step 1\"}}]}')
        self.assertEqual(reasoning_chunk["reasoning_content"], "step 1")
        self.assertEqual(reasoning_chunk["content"], "")

        content_chunk = client._parseStreamChunk('{\"choices\":[{\"delta\":{\"content\":\"final answer\"}},\"usage\":{\"total_tokens\":12}}]')
        self.assertEqual(content_chunk["content"], "final answer")

        # Test response assembly
        response = client._buildResponse("answer", "reasoning", {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}, {})
        self.assertEqual(response["message"], "answer")
        self.assertEqual(response["reasoning_content"], "reasoning")
        self.assertEqual(response["tokens"], 15)

        # Test stats
        stats = client.getStats()
        self.assertIn("total_tokens", stats)
        self.assertIn("total_cost", stats)

        # Test system prompt building with context
        context = {
            "skill_path": "C:/test/skill",
            "skill_mode": "full",
            "api_hints": ["Use slicer.util.loadVolume() for loading", "Use SampleData for examples"],
            "scene": {"node_counts": {"Volume": 1}, "sample_node_names": ["MRHead"]}
        }
        prompt = client._buildSystemPrompt(context)
        self.assertIn("CURRENT SLICER SCENE", prompt)
        self.assertIn("SKILL LOCATION", prompt)
        self.assertIn("loadVolume", prompt)

        self.delayDisplay("LLMClient tests passed")

    def test_CodeValidator(self):
        """Test CodeValidator functionality."""
        from SlicerAIAgentLib import CodeValidator
        
        validator = CodeValidator()
        
        # Test safe code
        safe_code = "volume = slicer.util.loadVolume('test.nrrd')"
        result = validator.validate(safe_code)
        self.assertTrue(result["valid"], f"Safe code should pass: {result.get('reason')}")
        
        # Test empty code
        result = validator.validate("")
        self.assertFalse(result["valid"])
        self.assertIn("Empty", result["reason"])
        
        # Test syntax error
        bad_syntax = "def broken("
        result = validator.validate(bad_syntax)
        self.assertFalse(result["valid"])
        self.assertIn("Syntax", result["reason"])
        
        # Test blocked import
        blocked_import = "import os"
        result = validator.validate(blocked_import)
        self.assertFalse(result["valid"])
        self.assertIn("Blocked", result["reason"])
        
        # Test blocked function
        blocked_func = "eval('1+1')"
        result = validator.validate(blocked_func)
        self.assertFalse(result["valid"])
        self.assertIn("Blocked", result["reason"])

        # Traceback is used by correction/debug wrappers and should not warn.
        result = validator.validate("import traceback\nmessage = traceback.format_exc()\n")
        self.assertTrue(result["valid"], result.get("reason"))
        self.assertFalse(result["warnings"], result["warnings"])
        
        # Test destructive operation detection
        destructive_code = "slicer.mrmlScene.RemoveNode(node)"
        result = validator.validate(destructive_code)
        self.assertTrue(result["requires_confirmation"])
        self.assertTrue(len(result["destructive_ops"]) > 0)
        
        self.delayDisplay("CodeValidator tests passed")

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
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Set markup display views",
                    "slicer_op_category": "markups_display",
                    "slicer_api_keywords": ["Display", "View"],
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

        # Slice intersection visibility may be implemented through slice display nodes,
        # not only through vtkMRMLCrosshairNode.
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
                },
                "sub_operations": [{
                    "op_type": "slicer_op",
                    "description": "Toggle on slice intersection visibility.",
                    "slicer_op_category": "crosshair",
                    "slicer_api_keywords": ["crosshair"],
                }],
            }],
        )
        self.assertTrue(validation["valid"], validation.get("errors"))

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
            "addCurve": {"node_classes": ["vtkMRMLMarkupsCurveNode"]}
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

        # Acronym-heavy extension layout helpers still match custom-layout cookbook text.
        self.assertEqual(
            analyzer._match_extension_function(
                "Restore the BoneReconstructionPlanner custom layout registered by the extension.",
                ["setBRPLayout"],
            ),
            "setBRPLayout",
        )

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

        self.delayDisplay("ExtensionCLIAnalyzer contract tests passed")

    def test_TurnRouterWorkflowRoutes(self):
        """Test routing split between traditional and generated CLI workflow turns."""
        from SlicerAIAgentLib.TurnRouter import (
            ROUTE_TRADITIONAL,
            ROUTE_WORKFLOW_CONFLICT,
            ROUTE_WORKFLOW_CONTROL,
            TurnRouter,
        )

        self.assertEqual(
            TurnRouter.classify("load a volume", {"active": False}).route_type,
            ROUTE_TRADITIONAL,
        )

        active = {
            "active": True,
            "current_step": "cb_step_18",
            "status": "waiting_for_user",
        }
        done_route = TurnRouter.classify("done", active)
        self.assertEqual(done_route.route_type, ROUTE_WORKFLOW_CONTROL)
        self.assertEqual(done_route.action, "proceed")
        self.assertEqual(done_route.step_id, "cb_step_18")

        step_route = TurnRouter.classify("Proceed with workflow step 'cb_step_12'", active)
        self.assertEqual(step_route.route_type, ROUTE_WORKFLOW_CONTROL)
        self.assertEqual(step_route.action, "start")
        self.assertEqual(step_route.step_id, "cb_step_12")

        choice_route = TurnRouter.classify(
            "2",
            {
                "active": True,
                "current_step": "cb_step_1",
                "status": "waiting_for_choice",
            },
        )
        self.assertEqual(choice_route.route_type, ROUTE_WORKFLOW_CONTROL)
        self.assertEqual(choice_route.action, "choice_made")

        conflict = TurnRouter.classify("segment this CT first", active)
        self.assertEqual(conflict.route_type, ROUTE_WORKFLOW_CONFLICT)

    def test_WorkflowRuntimeStateTransitions(self):
        """Test deterministic workflow runtime state updates without Slicer execution."""
        from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime, WorkflowSession

        runtime = WorkflowRuntime()
        runtime.session = WorkflowSession(
            extension_name="FakeExtension",
            tool_name="FakeExtension",
            workflow_id="fake_1",
            current_step="cb_step_1",
        )

        wait_result = runtime.handle_execution_result(
            {"type": "interactive", "step_id": "cb_step_1"},
            {"success": True},
        )
        self.assertEqual(wait_result["step_id"], "cb_step_1")
        self.assertEqual(runtime.session.status, "waiting_for_user")
        self.assertEqual(runtime.session.current_step, "cb_step_1")

        count = runtime.queue_traditional_prompt("show me the loaded nodes")
        self.assertEqual(count, 1)
        self.assertEqual(runtime.pop_queued_prompts(), ["show me the loaded nodes"])

    def test_NodeChoiceResolverContracts(self):
        """Test narrow LLM node-choice resolver validation behavior."""
        from SlicerAIAgentLib.NodeChoiceResolver import NodeChoiceResolver

        class FakeClient:
            api_key = "test"

        resolver = NodeChoiceResolver(FakeClient())
        step_info = {
            "type": "user_choice",
            "question": "Which scalar volume is the Mandible Volume?",
            "choices": [],
            "node_class": "vtkMRMLScalarVolumeNode",
        }
        candidates = [
            {"id": "vtkMRMLScalarVolumeNode1", "name": "CTFibula"},
            {"id": "vtkMRMLScalarVolumeNode2", "name": "CTMandible"},
        ]
        self.assertTrue(resolver.should_resolve(step_info, candidates))
        parsed = resolver._extract_json(
            "```json\n"
            "{\"selected_node_id\":\"vtkMRMLScalarVolumeNode2\","
            "\"selected_node_name\":\"CTMandible\",\"confidence\":0.91,"
            "\"reason\":\"matches mandible\"}\n"
            "```"
        )
        self.assertEqual(parsed["selected_node_name"], "CTMandible")
        self.assertEqual(resolver._coerce_confidence("1.5"), 1.0)
        self.assertEqual(resolver._coerce_confidence("bad"), 0.0)

    def test_SafeExecutor(self):
        """Test SafeExecutor functionality."""
        from SlicerAIAgentLib import SafeExecutor
        
        executor = SafeExecutor()
        
        # Test simple execution
        code = "result = 2 + 2"
        result = executor.execute(code)
        self.assertTrue(result["success"], f"Simple code should execute: {result.get('error')}")
        
        # Test output capture
        code = "print('Hello, World!')"
        result = executor.execute(code)
        self.assertTrue(result["success"])
        self.assertIn("Hello, World!", result["output"])
        
        # Test exception handling
        code = "raise ValueError('Test error')"
        result = executor.execute(code)
        self.assertFalse(result["success"])
        self.assertIn("Test error", result["error"])
        self.assertIsNotNone(result["traceback"])
        
        # Test globals
        executor.addGlobal("test_var", 42)
        code = "print(test_var)"
        result = executor.execute(code)
        self.assertTrue(result["success"])
        self.assertIn("42", result["output"])
        
        # Test history
        self.assertTrue(len(executor.getHistory()) > 0)
        executor.clearHistory()
        self.assertEqual(len(executor.getHistory()), 0)
        
        self.delayDisplay("SafeExecutor tests passed")

    def test_ProgressBarFilter(self):
        """Test SafeExecutor progress bar filtering."""
        from SlicerAIAgentLib.SafeExecutor import SafeExecutor
        
        # Test 1: Strip tqdm lines
        noisy = (
            "0%| | 0/25 [00:00<?, ?it/s] 4%|4 | 1/25 [00:39<15:44, 39.35s/it]\n"
            "100%|##########| 25/25 [13:27<00:00, 32.28s/it]\n"
        )
        self.assertEqual(SafeExecutor._filter_progress_bars(noisy), "")
        
        # Test 2: Strip checkpoint loading lines
        shards = (
            "Loading checkpoint shards: 0%| | 0/2 [00:00<?, ?it/s] "
            "Loading checkpoint shards: 100%|##########| 2/2 [00:35<00:00, 17.65s/it]\n"
        )
        self.assertEqual(SafeExecutor._filter_progress_bars(shards), "")
        
        # Test 3: Preserve real errors
        mixed = (
            "0%| | 0/25 [00:00<?, ?it/s]\n"
            "[VTK ERROR] Invalid segment\n"
            "Loading checkpoint shards: 50%|##### | 1/2 [00:22<00:22, 22.69s/it]\n"
            "RuntimeError: model not found\n"
        )
        filtered = SafeExecutor._filter_progress_bars(mixed)
        self.assertIn("[VTK ERROR] Invalid segment", filtered)
        self.assertIn("RuntimeError: model not found", filtered)
        self.assertNotIn("0%|", filtered)
        self.assertNotIn("Loading checkpoint shards", filtered)
        
        # Test 4: Empty input
        self.assertEqual(SafeExecutor._filter_progress_bars(""), "")
        self.assertEqual(SafeExecutor._filter_progress_bars(None), None)
        
        self.delayDisplay("Progress bar filter tests passed")

    def test_SkillPath(self):
        """Test skill path resolution and mode detection in logic."""
        from SlicerAIAgent import SlicerAIAgentLogic
        
        logic = SlicerAIAgentLogic()
        
        self.assertIsNotNone(logic.skill_path)
        self.assertTrue(os.path.exists(logic.skill_path) or logic.skill_mode == "unknown")
        self.assertIn(logic.skill_mode, ["full", "lightweight", "web", "unknown"])
        
        logic.cleanup()
        self.delayDisplay("Skill path tests passed")

    def test_ConversationStore(self):
        """Test ConversationStore functionality."""
        from SlicerAIAgentLib import ConversationStore
        
        store = ConversationStore()
        store.clearAll()
        
        # Test adding exchanges (with reasoning_content)
        store.addExchange("Hello", {"message": "Hi", "reasoning_content": "Thinking about greeting", "tokens": 10, "cost": 0.001})
        store.addExchange("How are you?", {"message": "I'm good", "tokens": 15, "cost": 0.0015})

        # Test retrieval
        current = store.getCurrentSession()
        self.assertEqual(len(current), 2)
        self.assertEqual(current[0].get("reasoning_content"), "Thinking about greeting")
        self.assertEqual(current[1].get("reasoning_content"), "")
        
        # Test stats
        stats = store.getStats()
        self.assertEqual(stats["current_session_exchanges"], 2)
        self.assertEqual(stats["current_session_tokens"], 25)
        
        # Test search
        results = store.search("Hello")
        self.assertEqual(len(results), 1)
        
        # Test export/import with temp directory
        temp_dir = tempfile.mkdtemp()
        try:
            export_path = os.path.join(temp_dir, "test_conversation.json")
            store.exportSession(export_path)
            self.assertTrue(os.path.exists(export_path))
            
            store.clearAll()
            self.assertEqual(len(store.getAllConversations()), 0)
            
            store.importSession(export_path)
            self.assertTrue(len(store.getAllConversations()) > 0)
        finally:
            shutil.rmtree(temp_dir)
        
        # Test new session
        old_session = store.current_session_id
        store.newSession()
        self.assertNotEqual(store.current_session_id, old_session)
        
        self.delayDisplay("ConversationStore tests passed")

    def test_SlicerCodeTemplates(self):
        """Test SlicerCodeTemplates functionality."""
        from SlicerAIAgentLib import SlicerCodeTemplates
        
        # Test getting specific template
        template = SlicerCodeTemplates.getTemplate("load_volume")
        self.assertIsNotNone(template)
        self.assertIn("code", template)
        
        # Test getting all templates
        all_templates = SlicerCodeTemplates.getAllTemplates()
        self.assertTrue(len(all_templates) > 0)
        
        # Test finding by tag
        results = SlicerCodeTemplates.findByTag("volume")
        self.assertTrue(len(results) > 0)
        
        # Test finding by keyword
        results = SlicerCodeTemplates.findByKeyword("load")
        self.assertTrue(len(results) > 0)
        
        # Test formatting for prompt
        formatted = SlicerCodeTemplates.formatForPrompt(results[:2])
        self.assertIn("```python", formatted)
        
        self.delayDisplay("SlicerCodeTemplates tests passed")

    def test_GenerateSegmentationCode(self):
        """Test the GenerateSegmentationCode tool."""
        from SlicerAIAgentLib import SkillTools
        
        tools = SkillTools.SkillTools()
        
        # Test 1: Basic organ segmentation — passes through arbitrary prompts
        result = tools.execute("GenerateSegmentationCode", {"prompt": "segment the liver and spleen"})
        self.assertNotIn("error", result, f"Tool returned error: {result.get('error')}")
        self.assertEqual(result["tool"], "GenerateSegmentationCode")
        self.assertIn("liver", result["extracted_targets"])
        self.assertIn("spleen", result["extracted_targets"])
        self.assertIn("code", result)
        self.assertIn("VoxTell", result["code"])
        self.assertIn("runSegmentation", result["code"])
        self.assertIn("explanation", result)
        self.assertIn("requirements", result)
        
        # Test 2: Arbitrary anatomical terms (no keyword filtering)
        result = tools.execute("GenerateSegmentationCode", {"prompt": "find the hippocampus and amygdala"})
        self.assertIn("hippocampus", result["extracted_targets"])
        self.assertIn("amygdala", result["extracted_targets"])
        self.assertIn("runSegmentation", result["code"])
        
        # Test 3: Custom volume node name and output name
        result = tools.execute(
            "GenerateSegmentationCode",
            {
                "prompt": "segment the aorta",
                "volume_node_name": "CTChest",
                "output_segmentation_name": "AortaSeg",
            }
        )
        self.assertIn("CTChest", result["code"])
        self.assertIn("AortaSeg", result["code"])
        self.assertIn("aorta", result["extracted_targets"])
        
        # Test 4: No recognizable anatomical targets (fallback)
        result = tools.execute("GenerateSegmentationCode", {"prompt": "do something vague"})
        self.assertEqual(result["extracted_targets"], ["structure of interest"])
        self.assertIn("runSegmentation", result["code"])
        
        # Test 5: Verify GPU detection, widget-based logic access, offline mode, model check
        result = tools.execute("GenerateSegmentationCode", {"prompt": "segment kidneys"})
        self.assertIn("torch.cuda.is_available()", result["code"])
        self.assertIn("8_000_000_000", result["code"])
        self.assertIn("useGpu=use_gpu", result["code"])
        self.assertIn("widgetRepresentation().self()", result["code"])
        self.assertIn("_voxtell_widget.logic", result["code"])
        self.assertIn("isModelInstalled", result["code"])
        self.assertNotIn("slicer.modules.voxtell.logic()", result["code"])
        self.assertNotIn("import os", result["code"])
        
        # Test 6: Tool spec includes the new tool
        spec = tools.getToolsSpec()
        tool_names = [t["function"]["name"] for t in spec]
        self.assertIn("GenerateSegmentationCode", tool_names)
        
        self.delayDisplay("GenerateSegmentationCode tests passed")

    def test_Integration(self):
        """Integration test of multiple components."""
        from SlicerAIAgent import SlicerAIAgentLogic
        from SlicerAIAgentLib import (
            LLMClient,
            CodeValidator,
            SafeExecutor,
        )
        
        # Create components
        client = LLMClient()
        logic = SlicerAIAgentLogic()
        validator = CodeValidator()
        executor = SafeExecutor()
        
        # Test workflow: component initialization and basic operations
        prompt = "load a volume"
        self.assertIsNotNone(logic.skill_path)
        
        # Test code validation
        test_code = "volume = slicer.util.loadVolume('/path/to/volume.nrrd')"
        validation = validator.validate(test_code)
        self.assertTrue(validation["valid"])
        
        # Test execution
        result = executor.execute("x = 5 + 10")
        self.assertTrue(result["success"])
        
        self.delayDisplay("Integration tests passed")


class SlicerAIAgentLogicTest(unittest.TestCase):
    """Tests for the SlicerAIAgentLogic class."""

    def setUp(self):
        """Setup for each test."""
        from SlicerAIAgent import SlicerAIAgentLogic
        self.logic = SlicerAIAgentLogic()

    def tearDown(self):
        """Cleanup after each test."""
        if self.logic:
            self.logic.cleanup()

    def test_api_key_management(self):
        """Test API key setting."""
        self.logic.setApiKey("test_key")
        self.assertTrue(self.logic.hasApiKey())
        
        self.logic.setApiKey("")
        self.assertFalse(self.logic.hasApiKey())

    def test_model_setting(self):
        """Test model setting."""
        self.logic.setModel("moonshot-v1-32k")
        self.assertEqual(self.logic.llmClient.model, "moonshot-v1-32k")

        self.logic.setModel("kimi-latest")
        self.assertEqual(self.logic.llmClient.model, "kimi-k2.5")

        self.logic.setModel("deepseek-v4-pro")
        self.assertEqual(self.logic.llmClient.model, "deepseek-v4-pro")
        self.assertTrue(self.logic.llmClient._supportsThinking())

    def test_conversation_clear(self):
        """Test conversation clearing."""
        self.logic.clearConversation()
        # Should not raise

    def test_workflow_control_turn_detection(self):
        """Test dense pre-retrieval skip detection for workflow control turns."""
        active_context = {
            "workflow_state": (
                "### Active Workflow: BoneReconstructionPlanner\n"
                "- Current step: cb_step_18\n"
            )
        }
        self.assertTrue(
            self.logic._isWorkflowControlTurn(
                "Proceed with workflow step 'cb_step_18'",
                active_context,
            )
        )
        self.assertTrue(self.logic._isWorkflowControlTurn("done", active_context))
        self.assertTrue(self.logic._isWorkflowControlTurn("skip", active_context))
        self.assertFalse(
            self.logic._isWorkflowControlTurn(
                "Why did the cut plane placement fail?",
                active_context,
            )
        )
        self.assertFalse(
            self.logic._isWorkflowControlTurn(
                "Proceed with workflow step 'cb_step_18'",
                {},
            )
        )


# For running outside Slicer's test framework
if __name__ == "__main__":
    unittest.main()
