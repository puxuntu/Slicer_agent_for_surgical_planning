"""Per-extension analyses behind the Experiments panel.

Each module here owns ONE procedure's summary: how to find its runs, what to
measure, and what the spreadsheet columns mean. The panel that hosts them
(``app/widget_experiments.py``) knows none of that -- a module registers itself
with ``@register_experiment_panel("<ExtensionName>")`` and is handed a layout to
fill.

The numerics live in Qt-free modules so they can be run and checked without
Slicer; only the panel half imports ``qt``.
"""
