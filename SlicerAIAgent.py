"""Compatibility entry point for the SlicerAIAgent scripted module."""

from slicer.ScriptedLoadableModule import ScriptedLoadableModule

from SlicerAIAgentLib.app import module as _module
from SlicerAIAgentLib.app import (
    SlicerAIAgentLogic,
    SlicerAIAgentWidget,
    SlicerAIAgentTest,
)


class SlicerAIAgent(ScriptedLoadableModule):
    """Declared literally here, rather than re-exported from
    SlicerAIAgentLib.app, because Slicer's drag-and-drop module scan
    (ExtensionWizardLib/ModuleInfo.py) reads this file with ast.parse and
    looks for a top-level class named after the file whose base list holds
    the bare name ScriptedLoadableModule -- an import is invisible to it,
    so dropping this folder onto Slicer offered no reader. The runtime
    factory imports instead and was always satisfied, which is why adding
    the path by hand worked either way. The metadata itself stays in
    SlicerAIAgentLib/app/module.py, the one place it is defined.
    """

    __init__ = _module.SlicerAIAgent.__init__


__all__ = [
    'SlicerAIAgent',
    'SlicerAIAgentLogic',
    'SlicerAIAgentWidget',
    'SlicerAIAgentTest',
]
