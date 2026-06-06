from .common import *
from .setup import SkillToolSetupMixin
from .dispatch_search import SkillToolDispatchSearchMixin
from .readfile import SkillToolReadFileMixin
from .symbols import SkillToolSymbolsMixin


class SkillToolExecutor(
    SkillToolSetupMixin,
    SkillToolDispatchSearchMixin,
    SkillToolReadFileMixin,
    SkillToolSymbolsMixin,
):
    """Executes tool calls for searching the Slicer skill."""
    pass
