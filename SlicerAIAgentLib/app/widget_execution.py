from .widget_send import WidgetSendMixin
from .widget_execution_flow import WidgetExecutionFlowMixin
from .widget_correction import WidgetCorrectionMixin
from .widget_reporting import WidgetReportingMixin


class WidgetExecutionMixin(
    WidgetSendMixin,
    WidgetExecutionFlowMixin,
    WidgetCorrectionMixin,
    WidgetReportingMixin,
):
    pass
