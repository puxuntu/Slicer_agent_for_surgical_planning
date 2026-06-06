from .common import *
from .logic_core import LogicCoreMixin
from .logic_scene import LogicSceneMixin
from .logic_index import LogicIndexMixin


class SlicerAIAgentLogic(
    LogicCoreMixin,
    LogicSceneMixin,
    LogicIndexMixin,
    ScriptedLoadableModuleLogic,
):
    """Business logic for SlicerAIAgent."""
    pass
