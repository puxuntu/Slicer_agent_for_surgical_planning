from .common import *


class WorkflowTestsMixin:
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

        skip_route = TurnRouter.classify("skip", active)
        self.assertEqual(skip_route.route_type, ROUTE_WORKFLOW_CONTROL)
        self.assertEqual(skip_route.action, "skip")
        self.assertEqual(skip_route.step_id, "cb_step_18")

        cancel_route = TurnRouter.classify("cancel", active)
        self.assertEqual(cancel_route.route_type, ROUTE_WORKFLOW_CONTROL)
        self.assertEqual(cancel_route.action, "cancel")
        self.assertEqual(cancel_route.step_id, "cb_step_18")

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

    def test_WorkflowRuntimeUiStateMapping(self):
        """Test compact workflow UI state for progress and controls."""
        import importlib
        wf_mod = importlib.import_module("SlicerAIAgentLib.WorkflowRuntime")
        WorkflowRuntime = wf_mod.WorkflowRuntime
        WorkflowSession = wf_mod.WorkflowSession

        graph = {
            "step_count": 4,
            "steps": [
                {"step_id": "cb_step_1", "step_type": "automated", "description": "Load data"},
                {
                    "step_id": "cb_step_2",
                    "step_type": "interactive",
                    "description": "Cookbook says click the old plane instructions.",
                    "is_optional": True,
                    "ui_guidance": {
                        "title": "Place cutting plane",
                        "instruction": "Position this cutting plane, then click Done.",
                        "done_label": "Plane placed",
                        "object_label": "cutting plane",
                    },
                },
                {
                    "step_id": "cb_step_3",
                    "step_type": "user_choice",
                    "description": "Choose count",
                    "choice_info": {
                        "choices": [
                            {"label": "One", "value": "1"},
                            {"label": "Two", "value": "2"},
                        ],
                    },
                },
                {
                    "step_id": "cb_step_16",
                    "step_type": "user_choice",
                    "description": "Choose cut plane count",
                    "choice_info": {
                        "question": "How many mandibular cut planes would you like to create?",
                        "choices": [],
                        "parameter_name": "numberOfCutPlanes",
                        "default_value": "1",
                    },
                    "ui_guidance": {
                        "title": "Choose cutting plane count",
                        "instruction": "Enter the number of cutting planes.",
                        "input_label": "Number of cutting planes",
                        "choice_label": "Number of cutting planes",
                    },
                },
            ],
        }
        original_get_workflow_graph = wf_mod.get_workflow_graph
        wf_mod.get_workflow_graph = lambda extension_name: graph
        try:
            runtime = WorkflowRuntime()
            runtime.session = WorkflowSession(
                extension_name="FakeExtension",
                tool_name="FakeExtension",
                workflow_id="fake_ui_1",
                current_step="cb_step_1",
            )

            automated = runtime.state_for_ui({"type": "automated", "step_id": "cb_step_1"})
            self.assertEqual(automated["total_steps"], 4)
            self.assertEqual(automated["current_index"], 1)
            self.assertFalse(automated["can_done"])

            runtime.session.status = "waiting_for_user"
            runtime.session.current_step = "cb_step_2"
            interactive = runtime.state_for_ui({
                "type": "interactive",
                "step_id": "cb_step_2",
                "interaction_instructions": "Hold Shift and move mouse in a view.",
                "repeat_progress": {"current": 2, "total": 3},
            })
            self.assertEqual(interactive["status"], "Waiting for your interaction")
            self.assertTrue(interactive["can_done"])
            self.assertTrue(interactive["can_skip"])
            self.assertEqual(interactive["description"], "Place cutting plane")
            self.assertIn("Position this cutting plane", interactive["instructions"])
            self.assertEqual(interactive["done_label"], "Plane placed")
            self.assertEqual(interactive["repeat_progress"]["current"], 2)

            runtime.session.status = "waiting_for_choice"
            runtime.session.current_step = "cb_step_3"
            choice = runtime.state_for_ui({
                "type": "user_choice",
                "step_id": "cb_step_3",
                "question": "How many planes?",
                "instruction": "Ask the user, then call FakeExtension with user_action='choice_made'.",
            })
            self.assertEqual(choice["status"], "Waiting for your choice")
            self.assertEqual(choice["description"], "How many planes?")
            self.assertEqual(choice["instructions"], "")
            self.assertFalse(choice["can_done"])
            self.assertEqual(choice["choices"][1]["value"], "2")

            compact_choice = runtime.state_for_ui({
                "type": "user_choice",
                "step_id": "cb_step_99",
                "question": "Use right side leg?",
                "instruction": (
                    "Ask the user: 'Use right side leg?'\n"
                    "Options:\n"
                    "  1. Yes\n"
                    "  2. No\n"
                    "Wait for the user's response."
                ),
            })
            self.assertEqual(compact_choice["choices"][0]["label"], "Yes")
            self.assertEqual(compact_choice["choices"][0]["value"], "true")
            self.assertEqual(compact_choice["choices"][1]["value"], "false")

            runtime.session.current_step = "cb_step_16"
            count_choice = runtime.state_for_ui({
                "type": "user_choice",
                "step_id": "cb_step_16",
                "question": "How many mandibular cut planes would you like to create?",
                "default_value": "1",
                "parameter_name": "numberOfCutPlanes",
            })
            self.assertEqual(count_choice["choices"], [])
            self.assertTrue(count_choice["needs_choice_input"])
            self.assertEqual(count_choice["default_value"], "1")
            self.assertEqual(count_choice["description"], "Choose cutting plane count")
            self.assertEqual(count_choice["input_label"], "Number of cutting planes")

            runtime.session.status = "completed"
            runtime.session.current_step = None
            runtime.session.completed_steps = ["cb_step_1", "cb_step_2", "cb_step_3"]
            completed = runtime.state_for_ui({"workflow_completed": True})
            self.assertEqual(completed["status"], "Completed")
            self.assertEqual(completed["completed_steps"], 3)
            self.assertFalse(completed["can_cancel"])
        finally:
            wf_mod.get_workflow_graph = original_get_workflow_graph

    def test_WorkflowWidgetClearsStaleMarkers(self):
        """Test stale workflow tool results are cleared after a workflow turn."""
        from SlicerAIAgent import SlicerAIAgentWidget

        class FakeLogic:
            pass

        interactive_step = {
            "tool": "BoneReconstructionPlanner",
            "step_id": "cb_step_10",
            "type": "interactive",
        }
        same_cached_step = dict(interactive_step)

        widget = object.__new__(SlicerAIAgentWidget)
        widget.logic = FakeLogic()
        widget.logic._lastInteractiveStep = interactive_step
        widget.logic._lastWorkflowStep = same_cached_step
        widget._currentWorkflowStepInfo = interactive_step
        widget._waitingForUser = True
        widget._autoAdvanceWorkflowStep = {"step_id": "cb_step_11"}
        widget._activeWorkflowId = "BoneReconstructionPlanner_1"
        widget._taskWorkflowPanelActive = True

        self.assertTrue(widget._sameWorkflowStepMarker(interactive_step, same_cached_step))

        widget._clearWorkflowResultMarkers()
        self.assertIsNone(widget.logic._lastInteractiveStep)
        self.assertIsNone(widget.logic._lastWorkflowStep)

        widget.logic._lastInteractiveStep = interactive_step
        widget.logic._lastWorkflowStep = same_cached_step
        widget._clearCompletedWorkflowState()
        self.assertIsNone(widget.logic._lastInteractiveStep)
        self.assertIsNone(widget.logic._lastWorkflowStep)
        self.assertIsNone(widget._currentWorkflowStepInfo)
        self.assertFalse(widget._waitingForUser)
        self.assertIsNone(widget._autoAdvanceWorkflowStep)
        self.assertIsNone(widget._activeWorkflowId)
        self.assertFalse(widget._taskWorkflowPanelActive)

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
