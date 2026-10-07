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
#: -> [callable(widget, layout, extension_name) -> None, ...], in _PANEL_MODULES
#: order.
#:
#: A LIST, not one builder. Two modules may legitimately claim the same
#: procedure -- one scoring its runs while another prepares its input -- and a
#: dict of one made the later import silently erase the earlier, so an analysis
#: panel simply did not exist and the section showed the other tool as if that
#: were all there was. Nothing raised: an overwrite is a legal dict assignment,
#: and which panel survived depended on the order of a tuple in this file.
#:
#: No shipped procedure claims two today, which is exactly why the property is
#: pinned by ``scripts/check_longbone_analysis.py`` against SYNTHETIC builders:
#: an invariant that nothing currently exercises is the one that rots.
EXPERIMENT_PANELS = {}


def register_experiment_panel(extension_name):
    """Register a builder for one extension's Experiments content.

    Appends, so several modules can contribute to one procedure's section. A
    builder already registered under the same module and qualified name is
    REPLACED in place rather than appended beside itself, so re-importing a
    panel module (Slicer's Reload) does not stack duplicates of it.
    """
    def _register(builder):
        builders = EXPERIMENT_PANELS.setdefault(str(extension_name), [])
        identity = (getattr(builder, "__module__", ""),
                    getattr(builder, "__qualname__", getattr(builder, "__name__", "")))
        for index, existing in enumerate(builders):
            if (getattr(existing, "__module__", ""),
                    getattr(existing, "__qualname__",
                            getattr(existing, "__name__", ""))) == identity:
                builders[index] = builder
                return builder
        builders.append(builder)
        return builder
    return _register


#: Modules under ``SlicerAIAgentLib/experiments/`` that register a panel.
#: Imported when the section is built rather than at module import: a broken or
#: dependency-missing analysis then costs its own extension's panel and nothing
#: else, instead of taking the whole widget down at Slicer startup.
_PANEL_MODULES = ("zygomatic_panel", "orbital_panel", "shoulder_panel",
                  "cranial_panel", "pelvic_panel", "longbone_panel",
                  "pedicle_panel", "mandible_panel")

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


def _panelSeparator():
    """A rule between two panels that claim the same procedure.

    Without it, the analysis button and the dataset-preparation button read as
    one form with two unrelated halves.
    """
    line = qt.QFrame()
    line.setFrameShape(qt.QFrame.HLine)
    line.setFrameShadow(qt.QFrame.Sunken)
    return line


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
        # -- which is REPLACED wholesale rather than emptied. See
        # _clearExperimentContent for why that distinction is load-bearing.
        self._experimentsOuterLayout = outer
        self._experimentContent = None
        self._experimentContentLayout = None
        self._newExperimentContent()

        self._experimentSelector.currentIndexChanged.connect(
            self._onExperimentExtensionChanged)
        self._populateExperimentSelector()
        self._setupUserStudySection()

    def _setupUserStudySection(self):
        """The user-study subsection, below the per-extension content.

        Built like a panel module -- imported here, fail-soft -- so a broken
        study evaluation costs that subsection and nothing else. It is the LAST
        child of the group, and ``_newExperimentContent`` inserts each
        replacement content container above it.
        """
        self._userStudyGroup = None
        try:
            from SlicerAIAgentLib.experiments.user_study_panel import build_section
            self._userStudyGroup = build_section(self, self._experimentsOuterLayout)
        except Exception as exc:
            logger.warning("User-study section failed to load", exc_info=True)
            error = qt.QLabel(f"The user-study evaluation failed to load: {exc}")
            error.setWordWrap(True)
            error.setStyleSheet("color: #b00;")
            self._experimentsOuterLayout.addWidget(error)
            self._userStudyGroup = error

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
        builders = EXPERIMENT_PANELS.get(extension) or []
        if not builders:
            # No analysis defined for this procedure yet. Say so rather than
            # leaving a blank gap, which reads as a panel that failed to load.
            hint = qt.QLabel(f"No analysis defined for {extension} yet.")
            hint.setWordWrap(True)
            hint.setStyleSheet("color: gray; font-style: italic;")
            self._experimentContentLayout.addWidget(hint)
            return
        for position, builder in enumerate(builders):
            if position:
                self._experimentContentLayout.addWidget(_panelSeparator())
            try:
                builder(self, self._experimentContentLayout, extension)
            except Exception as exc:
                # A broken analysis must not take the module panel down with it
                # -- nor its neighbours: the content is NOT cleared here, since
                # a later builder failing would then delete an earlier one's
                # working panel. The failure is reported in its own place and
                # the loop goes on.
                logger.warning("Experiments panel %s for %s failed: %s",
                               getattr(builder, "__module__", "?"), extension,
                               exc, exc_info=True)
                error = qt.QLabel(f"This analysis failed to load: {exc}")
                error.setWordWrap(True)
                error.setStyleSheet("color: #b00;")
                self._experimentContentLayout.addWidget(error)

    def _newExperimentContent(self):
        """A fresh, empty container for one extension's panels."""
        content = qt.QWidget()
        layout = qt.QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        # Above the user-study subsection when it exists, so replacing the
        # per-extension content on a selector change never moves it below.
        anchor = getattr(self, "_userStudyGroup", None)
        index = self._experimentsOuterLayout.indexOf(anchor) if anchor is not None else -1
        if index >= 0:
            self._experimentsOuterLayout.insertWidget(index, content)
        else:
            self._experimentsOuterLayout.addWidget(content)
        self._experimentContent = content
        self._experimentContentLayout = layout

    def _clearExperimentContent(self):
        """Destroy the current extension's panels before building the next.

        The whole CONTAINER is replaced, rather than its layout emptied one
        widget at a time, and that is a crash fix rather than a tidy-up.

        Emptying it meant ``takeAt(0)`` then ``setParent(None)`` then
        ``deleteLater()`` on each child. Those last two must not both happen. A
        parented QWidget is owned by C++; ``setParent(None)`` hands ownership to
        the PythonQt wrapper, and that wrapper is dropped on the next loop
        iteration -- so Python deletes the C++ object, and the queued
        DeferredDelete event then fires on a freed pointer. Slicer exits, with no
        traceback, on every change of the extension selector.

        Replacing the container avoids the question entirely: the old one keeps
        its parent, so Qt owns the single delete, and every widget and nested
        LAYOUT below it goes with it. The emptying loop could not do the second
        part anyway -- ``item.widget()`` is None for a nested layout, so a
        builder that added one (a row of buttons, a form) leaked it, still
        parented and still connected, to fire its slots against the next
        panel's state.

        ``hide()`` before the delete because DeferredDelete is processed on the
        next event-loop turn, and until then a removed-but-live widget still
        paints at its old geometry underneath the panel being built.
        """
        outer = getattr(self, "_experimentsOuterLayout", None)
        if outer is None:
            return
        old = getattr(self, "_experimentContent", None)
        if old is not None:
            outer.removeWidget(old)          # out of the layout; parent intact
            old.hide()
            old.deleteLater()
        self._newExperimentContent()
