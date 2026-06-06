from .common import *

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
