from .config import LLMClientConfigMixin
from .transport import LLMClientTransportMixin
from .history import LLMClientHistoryMixin
from .chat import LLMClientChatMixin
from .tools import LLMClientToolsMixin
from .utils import LLMClientUtilsMixin


class LLMClient(
    LLMClientConfigMixin,
    LLMClientTransportMixin,
    LLMClientHistoryMixin,
    LLMClientChatMixin,
    LLMClientToolsMixin,
    LLMClientUtilsMixin,
):
    pass
