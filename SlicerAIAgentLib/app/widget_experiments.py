"""The Experiments panel: per-extension analysis of a procedure's runs.

One collapsible section between "Extension CLI Generator" and "Debug", holding
an extension selector and, below it, whatever analysis that particular procedure
needs. The analyses are deliberately NOT written here: what is worth measuring
differs per procedure (implant angles for one, resection-plane error for
another), so each gets its own builder and this file only owns the frame that
holds it.

Adding one is a single registration -- no edit to this module's UI code:

    from SlicerAIAgentLib.app.widget_experiments import register_experiment_panel

    @register_experiment_panel("ZygomaticImplantPlanner")
    def _zygoma_panel(widget, layout, extension):
        layout.addWidget(qt.QPushButton("Compute implant angles"))

The builder is handed the SlicerAIAgentWidget (so it can reach the run logs,
the scene and the logic), an empty QVBoxLayout to fill, and the extension name.
It is called on every selection change and its widgets are destroyed on the
next one, so it must build from scratch rather than cache widgets.
"""

from .common import *


#: extension name (as in manifest.json, e.g. "ZygomaticImplantPlanner")
#: -> callable(widget, layout, extension_name) -> None
EXPERIMENT_PANELS = {}


def register_experiment_panel(extension_name):
    """Register the builder for one extension's Experiments content."""
    def _register(builder):
        EXPERIMENT_PANELS[str(extension_name)] = builder
        return builder
    return _register


#: Modules under ``SlicerAIAgentLib/experiments/`` that register a panel.
#: Imported when the section is built rather than at module import: a broken or
#: dependency-missing analysis then costs its own extension's panel and nothing
#: else, instead of taking the whole widget down at Slicer startup.
_PANEL_MODULES = ("zygomatic_panel", "orbital_panel", "shoulder_panel",
                  "cranial_panel", "dicom_panel")

_panels_loaded = False


def _loadExperimentPanels():
    global _panels_loaded
    if _panels_loaded:
        return
    _panels_loaded = True
    import importlib
    for name in _PANEL_MODULES:
        try:
            importlib.import_module("SlicerAIAgentLib.experiments." + name)
        except Exception:
            logger.warning("Experiments panel %s failed to load", name, exc_info=True)


class WidgetExperimentsMixin:
    def _setupExperiments(self):
        """Build the Experiments section, below the CLI generator and above Debug."""
        _loadExperimentPanels()
        self._experimentsGroup = ctk.ctkCollapsibleGroupBox()
        self._experimentsGroup.title = "Experiments"
        self._experimentsGroup.collapsed = True
        self._insertExperimentsGroup()

        outer = qt.QVBoxLayout(self._experimentsGroup)

        # Selector row -- populated from the same list as the CLI generator's
        # (_cookbookExtensionEntries), so the two panels always offer the same
        # procedures. No Refresh of its own: the CLI generator's re-scan
        # repopulates this selector too, and nothing else here can go stale.
        row = qt.QHBoxLayout()
        row.addWidget(qt.QLabel("Extension:"))
        self._experimentSelector = qt.QComboBox()
        self._experimentSelector.setToolTip(
            "Select the procedure whose runs you want to analyse."
        )
        self._experimentSelector.setMinimumWidth(0)
        row.addWidget(self._experimentSelector, 1)
        outer.addLayout(row)

        # Everything below the selector is owned by the per-extension builder and
        # rebuilt from scratch on each change, so it lives in its own container
        # whose layout can be emptied without touching the selector row.
        self._experimentContent = qt.QWidget()
        self._experimentContentLayout = qt.QVBoxLayout(self._experimentContent)
        self._experimentContentLayout.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._experimentContent)

        self._experimentSelector.currentIndexChanged.connect(
            self._onExperimentExtensionChanged)
        self._populateExperimentSelector()

    def _insertExperimentsGroup(self):
        """Place the group after the CLI generator and before Debug.

        Three fallbacks, because the position is cosmetic but a failure to insert
        at all is not: the section would simply never appear.
        """
        try:
            anchor = getattr(self, "_cliGeneratorGroup", None)
            if anchor is not None and anchor.parent() is not None:
                layout = anchor.parent().layout()
                if layout is not None:
                    layout.insertWidget(layout.indexOf(anchor) + 1, self._experimentsGroup)
                    return
            debug = self.ui.findChild(ctk.ctkCollapsibleGroupBox, "debugGroupBox")
            if debug is not None and debug.parent() is not None:
                layout = debug.parent().layout()
                if layout is not None:
                    layout.insertWidget(layout.indexOf(debug), self._experimentsGroup)
                    return
        except Exception:
            logger.debug("Experiments group placement failed", exc_info=True)
        self.layout.addWidget(self._experimentsGroup)

    def _populateExperimentSelector(self):
        """Fill the selector from the shared cookbook-extension list."""
        selector = getattr(self, "_experimentSelector", None)
        if selector is None:
            return
        previous = selector.currentText
        # Repopulating fires currentIndexChanged repeatedly; each one would
        # rebuild the content panel against a half-filled combo.
        selector.blockSignals(True)
        try:
            selector.clear()
            self._experimentDataMap = {}
            for label, data in self._cookbookExtensionEntries():
                self._experimentDataMap[label] = data
                selector.addItem(label)
            # Keep the user on the extension they were looking at across a
            # Refresh, unless it is gone.
            if previous:
                index = selector.findText(previous)
                if index >= 0:
                    selector.setCurrentIndex(index)
        finally:
            selector.blockSignals(False)
        self._onExperimentExtensionChanged(selector.currentIndex)

    def _selectedExperimentExtension(self):
        """Name of the extension the Experiments panel is showing, or ""."""
        selector = getattr(self, "_experimentSelector", None)
        if selector is None or selector.currentIndex < 0:
            return ""
        data = getattr(self, "_experimentDataMap", {}).get(selector.currentText) or {}
        return data.get("name", "")

    def _onExperimentExtensionChanged(self, index):
        self._clearExperimentContent()
        extension = self._selectedExperimentExtension()
        if not extension:
            return
        builder = EXPERIMENT_PANELS.get(extension)
        if builder is None:
            # No analysis defined for this procedure yet. Say so rather than
            # leaving a blank gap, which reads as a panel that failed to load.
            hint = qt.QLabel(f"No analysis defined for {extension} yet.")
            hint.setWordWrap(True)
            hint.setStyleSheet("color: gray; font-style: italic;")
            self._experimentContentLayout.addWidget(hint)
            return
        try:
            builder(self, self._experimentContentLayout, extension)
        except Exception as exc:
            # A broken analysis must not take the module panel down with it.
            logger.warning("Experiments panel for %s failed: %s", extension, exc,
                           exc_info=True)
            self._clearExperimentContent()
            error = qt.QLabel(f"This analysis failed to load: {exc}")
            error.setWordWrap(True)
            error.setStyleSheet("color: #b00;")
            self._experimentContentLayout.addWidget(error)

    def _clearExperimentContent(self):
        """Destroy the current extension's widgets before building the next."""
        layout = getattr(self, "_experimentContentLayout", None)
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
