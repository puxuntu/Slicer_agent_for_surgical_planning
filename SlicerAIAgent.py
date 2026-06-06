"""Compatibility entry point for the SlicerAIAgent scripted module."""

from SlicerAIAgentLib.app import (
    SlicerAIAgent,
    SlicerAIAgentLogic,
    SlicerAIAgentWidget,
    SlicerAIAgentTest,
)

__all__ = [
    'SlicerAIAgent',
    'SlicerAIAgentLogic',
    'SlicerAIAgentWidget',
    'SlicerAIAgentTest',
]
