from .common import *


class WidgetCLIMixin:
    def _setupExtensionCLIGenerator(self):
        """Set up the Extension CLI Generator collapsible UI section."""
        # Create collapsible group box
        self._cliGeneratorGroup = ctk.ctkCollapsibleGroupBox()
        self._cliGeneratorGroup.title = "Extension CLI Generator"
        self._cliGeneratorGroup.collapsed = True
        # Insert after Settings, before Conversation History
        settingsGroup = self.ui.findChild(ctk.ctkCollapsibleGroupBox, "settingsGroupBox")
        if settingsGroup:
            parentLayout = settingsGroup.parent().layout()
            idx = parentLayout.indexOf(settingsGroup)
            parentLayout.insertWidget(idx + 1, self._cliGeneratorGroup)
        else:
            self.layout.insertWidget(1, self._cliGeneratorGroup)

        cliLayout = qt.QVBoxLayout(self._cliGeneratorGroup)

        # Row 1: Extension selector (only extensions that have a cookbook) + Refresh.
        # Sources (Extension Manager / Additional Module Paths / Loaded Modules) are
        # merged and de-duplicated — the user picks a single extension directly.
        extLayout = qt.QHBoxLayout()
        extLabel = qt.QLabel("Extension:")
        extLayout.addWidget(extLabel)

        # A checkable LIST, not a combo: Analyze & Generate runs every TICKED
        # extension, in parallel. The single-extension action (the
        # step-instruction editor) acts on the HIGHLIGHTED row instead, so one
        # widget carries both meanings without a second selector to keep in
        # sync -- tick what to build, highlight what to work on.
        self._extensionSelector = qt.QListWidget()
        self._extensionSelector.setToolTip(
            "Tick one or more extensions to generate CLIs for -- Analyze & Generate "
            "runs them in parallel. The highlighted row is the one the "
            "step-instruction editor acts on. Only extensions that have a cookbook "
            "file (Resources/extensions_cookbook/<name>.md) are listed."
        )
        self._extensionSelector.setSelectionMode(qt.QAbstractItemView.SingleSelection)
        # Tall enough to show a few without scrolling, short enough that the
        # collapsed group does not dominate the module panel.
        self._extensionSelector.setMaximumHeight(120)
        self._extensionSelector.setMinimumWidth(0)
        extLayout.addWidget(self._extensionSelector, 1)

        self._refreshExtensionsButton = qt.QPushButton("Refresh")
        self._refreshExtensionsButton.setToolTip("Re-scan installed extensions for cookbooks")
        self._refreshExtensionsButton.setMaximumWidth(80)
        extLayout.addWidget(self._refreshExtensionsButton)

        cliLayout.addLayout(extLayout)

        # Store extension data separately (keyed by label text)
        self._extensionDataMap = {}
        self._discoveredExtensions = []

        # Row 3: Analyze & Generate button
        # "&&", not "&": Qt reads a single ampersand in a button label as a
        # mnemonic marker -- it swallows the character and underlines the next
        # one, rendering this as "Analyze _Generate CLI".
        self._analyzeGenerateButton = qt.QPushButton(self.ANALYZE_BUTTON_TEXT)
        self._analyzeGenerateButton.setToolTip(
            "Analyze the selected extension and generate operation CLI tools"
        )
        self._analyzeGenerateButton.setEnabled(False)
        cliLayout.addWidget(self._analyzeGenerateButton)

        # Row 4: Progress -- ONE TAB PER EXTENSION. Parallel runs interleave
        # their output, so a single pane would produce a log in which no run's
        # story is readable; a tab each keeps every run's phases in order.
        # `_cliProgressDisplay` still exists and still points at a real editor
        # (the visible tab) so the single-extension flows -- auto-revision,
        # instruction regeneration -- keep writing where the user is looking.
        self._cliProgressTabs = qt.QTabWidget()
        self._cliProgressTabs.setMaximumHeight(170)
        self._cliProgressTabs.setDocumentMode(True)
        cliLayout.addWidget(self._cliProgressTabs)
        self._cliProgressPanes = {}
        self._cliProgressDisplay = self._cliProgressPane(self.CLI_DEFAULT_TAB)
        self._cliProgressTabs.currentChanged.connect(
            lambda unused_index: self._syncCliProgressDisplay())

        # Row 5: Status indicator
        self._cliStatusLabel = qt.QLabel("Ready")
        self._cliStatusLabel.setStyleSheet("font-weight: bold;")
        cliLayout.addWidget(self._cliStatusLabel)

        # Row 6: Result group (hidden until generation completes)
        self._cliResultGroup = qt.QGroupBox("Result")
        self._cliResultGroup.setVisible(False)
        resultLayout = qt.QVBoxLayout(self._cliResultGroup)

        self._cliResultSummary = qt.QLabel("")
        self._cliResultSummary.setWordWrap(True)
        resultLayout.addWidget(self._cliResultSummary)

        cliLayout.addWidget(self._cliResultGroup)

        # A step that runs without raising but behaves wrongly is no longer
        # reported here. It is fixed where it is SEEN: the ✎ Revise button above
        # Send, during the guided run, against the step on screen (see
        # app/widget_revise.py). A description typed into this panel had to be
        # mapped back to a step by an LLM guess, and the fix could not be tried
        # until the whole procedure was run again.

        # Row 7: Per-step instruction editor (clinical simple/detailed text).
        instrGroup = ctk.ctkCollapsibleGroupBox()
        instrGroup.title = "Step instructions"
        instrGroup.collapsed = True
        instrLayout = qt.QVBoxLayout(instrGroup)
        instrLayout.addWidget(qt.QLabel("Step:"))
        self._stepInstrStepCombo = qt.QComboBox()
        instrLayout.addWidget(self._stepInstrStepCombo)
        instrLayout.addWidget(qt.QLabel("Title:"))
        self._stepInstrTitle = qt.QLineEdit()
        instrLayout.addWidget(self._stepInstrTitle)
        instrLayout.addWidget(qt.QLabel("Simple (terse — behind 'Show brief'):"))
        self._stepInstrSimple = qt.QTextEdit()
        self._stepInstrSimple.setMaximumHeight(50)
        instrLayout.addWidget(self._stepInstrSimple)
        instrLayout.addWidget(qt.QLabel("Detailed (clinical — shown by default):"))
        self._stepInstrDetailed = qt.QTextEdit()
        self._stepInstrDetailed.setMaximumHeight(90)
        instrLayout.addWidget(self._stepInstrDetailed)
        # Per-step button-label overrides (fixed-default buttons only: the
        # Done/Confirm/Set advance button and literal choice options). Rebuilt
        # per selected step; node/segment pickers use live scene names and get
        # no field. Stored in step_instructions.json under the step's "buttons".
        instrLayout.addWidget(qt.QLabel("Button labels (blank = default):"))
        self._stepInstrButtonsContainer = qt.QWidget()
        self._stepInstrButtonsForm = qt.QFormLayout(self._stepInstrButtonsContainer)
        self._stepInstrButtonsForm.setContentsMargins(0, 0, 0, 0)
        instrLayout.addWidget(self._stepInstrButtonsContainer)
        self._stepInstrButtonFields = {}
        instrButtons = qt.QHBoxLayout()
        self._stepInstrSaveButton = qt.QPushButton("Save step")
        self._stepInstrSaveButton.setToolTip("Save this step's instructions (marks it as checked)")
        self._regenInstructionsButton = qt.QPushButton("Regenerate instructions")
        self._regenInstructionsButton.setToolTip("Regenerate all step instructions with the LLM (keeps edited steps)")
        instrButtons.addWidget(self._stepInstrSaveButton)
        instrButtons.addWidget(self._regenInstructionsButton)
        instrButtons.addStretch(1)
        instrLayout.addLayout(instrButtons)
        cliLayout.addWidget(instrGroup)

        # Internal state
        self._cliGeneratorRunning = False

        # Connect signals
        self._refreshExtensionsButton.clicked.connect(self._onRefreshExtensionsClicked)
        self._extensionSelector.currentRowChanged.connect(self._onExtensionSelectionChanged)
        self._extensionSelector.currentRowChanged.connect(self._populateStepInstructionCombo)
        # Ticking a box changes what Analyze & Generate would build, so the
        # button's caption has to follow it.
        self._extensionSelector.itemChanged.connect(
            lambda unused_item: self._refreshAnalyzeButtonCaption())
        self._analyzeGenerateButton.clicked.connect(self._onAnalyzeGenerateClicked)
        self._stepInstrStepCombo.currentIndexChanged.connect(self._onStepInstrStepChanged)
        self._stepInstrSaveButton.clicked.connect(self._onSaveStepInstructions)
        self._regenInstructionsButton.clicked.connect(self._onRegenerateInstructions)

        # Populate initial extension list
        self._onRefreshExtensionsClicked()

    def _onRefreshExtensionsClicked(self):
        """Re-scan installed extensions (all sources) and repopulate the list."""
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import discover_installed_extensions
            self._discoveredExtensions = discover_installed_extensions()
        except Exception:
            self._discoveredExtensions = []

        self._populateExtensionSelector()
        # The Experiments panel lists the same procedures, so one Refresh serves
        # both. Guarded: this runs once during _setupExtensionCLIGenerator, which
        # is before _setupExperiments has built anything.
        if getattr(self, "_experimentSelector", None) is not None:
            self._populateExperimentSelector()

    @staticmethod
    def _extension_has_cookbook(name):
        """True when a cookbook file exists for the extension name."""
        if not name:
            return False
        cookbook_dir = os.path.join(
            SLICER_AI_AGENT_ROOT, "Resources", "extensions_cookbook"
        )
        return (
            os.path.isfile(os.path.join(cookbook_dir, f"{name}.md"))
            or os.path.isfile(os.path.join(cookbook_dir, f"Slicer{name}.md"))
        )

    def _cookbookExtensionEntries(self):
        """Ordered ``(label, data)`` for every discovered extension with a cookbook.

        The three discovery sources (Extension Manager / Additional Module Paths /
        Loaded Modules) are merged and de-duplicated by extension name — the only
        filter the user sees is "has a cookbook". When the same extension is found
        in more than one source, the record with a usable Python source path wins
        (so Analyze & Generate can read the source).

        Shared with the Experiments panel, which lists exactly the same
        procedures: two independently-built lists would drift the moment one of
        these filters changed.
        """
        best_by_name = {}
        for ext in self._discoveredExtensions:
            name = ext.get("name")
            if not self._extension_has_cookbook(name):
                continue
            path = ext.get("source_path") or ext.get("install_path") or ""
            usable = bool(ext.get("has_python")) and bool(path) and os.path.isdir(path)
            prev = best_by_name.get(name)
            if prev is None or (usable and not prev[1]):
                best_by_name[name] = (ext, usable)

        entries = []
        for name in sorted(best_by_name):
            ext, _usable = best_by_name[name]
            label = name
            status = ext.get("cli_status") or ""
            if status:
                # Collapse the "with warnings" variant into a plain "Validated"
                # badge; other statuses (draft, failed, ...) show as-is.
                display_status = (
                    "Validated"
                    if status in ("validated", "validated_with_warnings")
                    else status
                )
                label += f" [{display_status}]"
            entries.append((label, {
                "type": "installed",
                "name": name,
                "path": ext.get("source_path", ext.get("install_path", "")),
                "source_type": ext.get("source_type", ""),
                "cli_status": status,
            }))
        return entries

    # ── selector accessors ───────────────────────────────────────────────
    # The widget is a QListWidget, whose API differs from the QComboBox this
    # replaced (currentRow vs currentIndex, item(i).text() vs itemText(i)).
    # Every reader goes through these, so the widget type is stated once.

    def _extensionItemCount(self):
        try:
            return int(self._extensionSelector.count)
        except TypeError:                       # PythonQt exposes it as a method
            return int(self._extensionSelector.count())

    def _extensionItemText(self, index):
        item = self._extensionSelector.item(index)
        return item.text() if item is not None else ""

    def _currentExtensionLabel(self):
        item = self._extensionSelector.currentItem()
        return item.text() if item is not None else ""

    def _setCurrentExtensionIndex(self, index):
        self._extensionSelector.setCurrentRow(int(index))

    def _checkedExtensionLabels(self):
        """Ticked rows, in list order.

        Falls back to the highlighted row when nothing is ticked: clicking
        Analyze & Generate with a row selected and no boxes ticked should build
        that one, not refuse. Ticking is how you ask for MORE than one, never a
        precondition for asking for one.
        """
        labels = []
        for index in range(self._extensionItemCount()):
            item = self._extensionSelector.item(index)
            if item is not None and item.checkState() == qt.Qt.Checked:
                labels.append(item.text())
        if not labels:
            current = self._currentExtensionLabel()
            if current:
                labels.append(current)
        return labels

    def _populateExtensionSelector(self):
        """Populate the extension list with installed extensions that have a
        cookbook file, preserving what was ticked and highlighted."""
        ticked = set(self._checkedExtensionLabels()) if self._extensionItemCount() else set()
        current = self._currentExtensionLabel()
        # Repopulating fires currentRowChanged per removal; each one would
        # rebuild the step-instruction editor against a half-filled list.
        self._extensionSelector.blockSignals(True)
        try:
            self._extensionSelector.clear()
            self._extensionDataMap.clear()
            for label, data in self._cookbookExtensionEntries():
                self._extensionDataMap[label] = data
                item = qt.QListWidgetItem(label)
                item.setFlags(item.flags() | qt.Qt.ItemIsUserCheckable)
                item.setCheckState(qt.Qt.Checked if label in ticked else qt.Qt.Unchecked)
                self._extensionSelector.addItem(item)
            index = 0
            for position in range(self._extensionItemCount()):
                if self._extensionItemText(position) == current:
                    index = position
                    break
            if self._extensionItemCount():
                self._setCurrentExtensionIndex(index)
        finally:
            self._extensionSelector.blockSignals(False)
        self._onExtensionSelectionChanged(self._extensionSelector.currentRow)
        self._populateStepInstructionCombo()

        # Enable the button if a valid selection exists after population
        has_work = bool(self._checkedExtensionLabels())
        self._analyzeGenerateButton.setEnabled(has_work and not self._cliGeneratorRunning)
        self._refreshAnalyzeButtonCaption()

    def _onExtensionSelectionChanged(self, index):
        """Enable/disable the Analyze button from what would actually be built.

        Keyed on `_checkedExtensionLabels()`, not on the highlighted row: with
        nothing highlighted but boxes ticked there IS work to do, and the button
        has to offer it.
        """
        has_work = bool(self._checkedExtensionLabels())
        self._analyzeGenerateButton.setEnabled(has_work and not self._cliGeneratorRunning)
        self._refreshAnalyzeButtonCaption()

    # ── progress tabs ────────────────────────────────────────────────────
    #: Tab used by everything that is not a per-extension generation run.
    CLI_DEFAULT_TAB = "Log"

    #: The ampersand is DOUBLED because Qt treats a single one in a button label
    #: as a mnemonic marker: "Analyze & Generate" renders as "Analyze _Generate".
    #: Defined once so the constructor and the count suffix cannot drift.
    ANALYZE_BUTTON_TEXT = "Analyze && Generate CLI"

    #: How many extensions may generate at once. Each is one background thread
    #: doing HTTP + file IO, so the cap is about the API and the machine, not
    #: about correctness -- the queue below runs the rest as slots free up.
    CLI_MAX_PARALLEL = 4

    def _cliProgressPane(self, name):
        """The read-only editor for ``name``, creating its tab on first use."""
        pane = self._cliProgressPanes.get(name)
        if pane is not None:
            return pane
        pane = qt.QTextEdit()
        pane.setReadOnly(True)
        pane.setFont(qt.QFont("Monospace", 9))
        pane.setPlaceholderText("Progress will appear here...")
        self._cliProgressPanes[name] = pane
        self._cliProgressTabs.addTab(pane, name)
        return pane

    def _syncCliProgressDisplay(self):
        """Point `_cliProgressDisplay` at the visible tab.

        The single-extension flows append to it directly; without this they
        would write into whichever pane happened to be created first, which
        after a batch is somebody else's tab.
        """
        pane = self._cliProgressTabs.currentWidget()
        if pane is not None:
            self._cliProgressDisplay = pane

    def _cliLog(self, name, message):
        """Append to ONE extension's tab, whatever is on screen."""
        try:
            self._cliProgressPane(name or self.CLI_DEFAULT_TAB).append(message)
        except Exception:
            logger.debug("CLI progress append failed", exc_info=True)

    def _showCliTab(self, name):
        pane = self._cliProgressPanes.get(name)
        if pane is not None:
            self._cliProgressTabs.setCurrentWidget(pane)

    def _resetCliProgressTabs(self, names):
        """One empty tab per extension about to run, plus the default log."""
        for name in list(self._cliProgressPanes):
            if name == self.CLI_DEFAULT_TAB:
                continue
            pane = self._cliProgressPanes.pop(name)
            index = self._cliProgressTabs.indexOf(pane)
            if index >= 0:
                self._cliProgressTabs.removeTab(index)
            pane.deleteLater()
        for name in names:
            self._cliProgressPane(name).clear()
        if names:
            self._showCliTab(names[0])
        self._syncCliProgressDisplay()

    def _refreshAnalyzeButtonCaption(self):
        """Say how many will be built, so a stray tick is visible before it runs."""
        button = getattr(self, "_analyzeGenerateButton", None)
        if button is None:
            return
        try:
            count = len(self._checkedExtensionLabels())
        except Exception:
            return
        button.setText(self.ANALYZE_BUTTON_TEXT
                       if count <= 1 else
                       "%s  (%d extensions)" % (self.ANALYZE_BUTTON_TEXT, count))

    # ── batch state ──────────────────────────────────────────────────────
    def _cliBatchActive(self):
        return bool(getattr(self, "_cliBatch", None))

    def _cliBatchFinish(self, name, ok, note=""):
        """Record one extension's outcome and, when the last one lands, wrap up.

        Called from BOTH the completion and the error path, so the batch cannot
        be left permanently 'running' by a failure -- which would keep the
        button disabled with no way back short of a Slicer restart.
        """
        batch = getattr(self, "_cliBatch", None) or {}
        if name in batch:
            batch[name] = {"ok": bool(ok), "note": note}
        self._cliLaunchQueuedGenerations()
        if any(state is None for state in batch.values()):
            return
        done = [n for n, st in batch.items() if st and st.get("ok")]
        failed = [n for n, st in batch.items() if st and not st.get("ok")]
        self._cliBatch = {}
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)
        self._refreshAnalyzeButtonCaption()
        if len(batch) > 1:
            summary = "%d of %d generated" % (len(done), len(batch))
            if failed:
                summary += " -- failed: " + ", ".join(sorted(failed))
            self._cliStatusLabel.setText(summary)
            self._cliStatusLabel.setStyleSheet(
                "font-weight: bold; color: %s;" % ("red" if failed else "green"))
            self._cliLog(self.CLI_DEFAULT_TAB, summary)

    def _cliLaunchQueuedGenerations(self):
        """Start queued extensions as running slots free up."""
        queued = getattr(self, "_cliQueue", None) or []
        running = len([n for n, st in (getattr(self, "_cliBatch", None) or {}).items()
                       if st is None and n in getattr(self, "_cliStarted", set())])
        while queued and running < self.CLI_MAX_PARALLEL:
            name, source_path = queued.pop(0)
            self._startCliGeneration(name, source_path)
            running += 1

    def _onAnalyzeGenerateClicked(self):
        """Generate a CLI for every ticked extension, in parallel."""
        if self._cliBatchActive():
            return

        labels = self._checkedExtensionLabels()
        runnable, skipped = [], []
        for label in labels:
            data = self._extensionDataMap.get(label) or {}
            name = data.get("name") or ""
            source_path = data.get("path") or ""
            if not name:
                continue
            if not source_path or not os.path.isdir(source_path):
                skipped.append("%s: source path not found (%s)" % (name, source_path))
                continue
            if not self._extension_has_cookbook(name):
                skipped.append(
                    "%s: no cookbook -- create Resources/extensions_cookbook/%s.md"
                    % (name, name))
                continue
            runnable.append((name, source_path))

        for note in skipped:
            self._cliLog(self.CLI_DEFAULT_TAB, "Skipped -- " + note)
        if not runnable:
            self._cliStatusLabel.setText("Nothing to generate")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")
            if not skipped:
                self._cliLog(self.CLI_DEFAULT_TAB,
                             "Tick at least one extension, or select a row.")
            return

        # ONE confirmation for the whole batch, naming exactly which extensions
        # would be rebuilt. Asking per extension turns a 5-extension run into 5
        # dialogs, which is how a user stops reading them.
        from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir
        existing = [name for name, unused in runnable
                    if os.path.isfile(os.path.join(get_cli_base_dir(), name,
                                                   "manifest.json"))]
        if existing:
            reply = qt.QMessageBox.question(
                None, "Regenerate CLI",
                "A CLI already exists for:\n  %s\n\n"
                "Regenerate from scratch? The existing package is deleted first "
                "and restored automatically if a run fails.\n"
                "To fix ONE step's behaviour instead, run the procedure and use "
                "the ✎ Revise button above Send on that step."
                % "\n  ".join(existing),
                qt.QMessageBox.Yes | qt.QMessageBox.No,
            )
            if reply != qt.QMessageBox.Yes:
                return

        names = [name for name, unused in runnable]
        self._cliBatch = {name: None for name in names}
        self._cliStarted = set()
        self._cliQueue = list(runnable)
        self._cliGeneratorRunning = True
        self._analyzeGenerateButton.setEnabled(False)
        self._cliResultGroup.setVisible(False)
        self._resetCliProgressTabs(names)
        self._cliStatusLabel.setText(
            "Analyzing..." if len(names) == 1
            else "Analyzing %d extensions..." % len(names))
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: orange;")
        if len(names) > 1:
            self._cliLog(self.CLI_DEFAULT_TAB,
                         "Generating %d CLI(s), up to %d at a time: %s"
                         % (len(names), self.CLI_MAX_PARALLEL, ", ".join(names)))
        self._cliLaunchQueuedGenerations()

    def _startCliGeneration(self, ext_name, source_path):
        """Run ONE extension's generation on its own background thread."""
        import threading

        self._cliStarted.add(ext_name)
        self._cliLog(ext_name, "Starting analysis of '%s'..." % ext_name)
        self._cliLog(ext_name, "Source: %s" % source_path)

        def _run_analysis():
            try:
                from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
                from SlicerAIAgentLib.CodeValidator import CodeValidator

                def _run_live_probe_on_main_thread(probe_code):
                    response_queue = queue.Queue(maxsize=1)
                    self._streamQueue.put((
                        'cli_probe_request',
                        {
                            'probe_code': probe_code,
                            'response_queue': response_queue,
                            'extension': ext_name,
                        },
                    ))
                    try:
                        # Probes execute on the Qt main thread and therefore
                        # SERIALIZE across parallel runs: with N generations in
                        # flight a probe can wait behind N-1 others, so the
                        # budget scales with the cap rather than being a fixed
                        # 30 s that only ever held for a single run.
                        return response_queue.get(
                            timeout=30 * max(1, self.CLI_MAX_PARALLEL))
                    except queue.Empty:
                        return {"error": "Timeout waiting for main-thread live API probe"}

                analyzer = ExtensionCLIAnalyzer(
                    llm_client=self.logic.llmClient,
                    output_base_dir=os.path.join(
                        SLICER_AI_AGENT_ROOT, "Resources", "extension_CLI"
                    ),
                    code_validator=CodeValidator(),
                    on_progress=lambda n, s, d: self._streamQueue.put(
                        ('cli_progress', {'stage': n, 'name': s, 'detail': d,
                                          'extension': ext_name})
                    ),
                    on_error=lambda e: self._streamQueue.put(
                        ('cli_error', {'error': e, 'extension': ext_name})),
                    live_probe_executor=_run_live_probe_on_main_thread,
                )

                # Clicking Analyze & Generate on an extension that already has
                # a CLI is an explicit regeneration: the previous package is
                # deleted first (and restored if this run fails).
                result = analyzer.analyze_and_generate(
                    extension_name=ext_name,
                    source_path=source_path,
                    force_overwrite=True,
                )
                if isinstance(result, dict):
                    result.setdefault("extension_name", ext_name)
                self._streamQueue.put(('cli_complete', result))

            except Exception as e:
                import traceback
                self._streamQueue.put((
                    'cli_error',
                    {'error': "%s\n%s" % (e, traceback.format_exc()),
                     'extension': ext_name},
                ))

        threading.Thread(target=_run_analysis, daemon=True).start()

    def _autoReviseCli(self, generation_result):
        """Automatically trigger LLM revision after generation validation fails."""
        data = self._getSelectedExtensionData()
        if not data:
            return

        ext_name = data["name"]
        source_path = data.get("path", "")
        self._cliGeneratorRunning = True
        self._cliStatusLabel.setText("Auto-revising...")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: orange;")

        # Extract validation errors
        val_result = generation_result.get("validation_result", {})
        errors = val_result.get("errors", [])
        if not errors:
            error = val_result.get("reason", "Unknown validation error")
            errors = [error]

        import threading

        def _run_revision():
            try:
                from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
                from SlicerAIAgentLib.CodeValidator import CodeValidator

                analyzer = ExtensionCLIAnalyzer(
                    llm_client=self.logic.llmClient,
                    output_base_dir=os.path.join(
                        SLICER_AI_AGENT_ROOT, "Resources", "extension_CLI"
                    ),
                    code_validator=CodeValidator(),
                    on_progress=lambda n, s, d: self._streamQueue.put(
                        ('cli_progress', {'stage': n, 'name': s, 'detail': d})
                    ),
                    on_error=lambda e: self._streamQueue.put(('cli_error', e)),
                )

                result = analyzer.revise(
                    ext_name,
                    errors,
                    source_path=source_path,
                    logic_analysis=generation_result.get("logic_analysis"),
                    api_probe_result=generation_result.get("api_probe_result"),
                )
                self._streamQueue.put(('cli_revision_complete', result))

            except Exception as e:
                self._streamQueue.put(('cli_error', str(e)))

        thread = threading.Thread(target=_run_revision, daemon=True)
        thread.start()

    def _getSelectedExtensionData(self):
        """Get the data dict for the currently selected extension."""
        current_text = self._currentExtensionLabel()
        if not current_text:
            return None
        return self._extensionDataMap.get(current_text)

    # ----------------------------- per-step instruction editor -----------------

    def _selectedExtCliDir(self):
        """Resolve the selected extension's CLI directory, or None."""
        data = self._getSelectedExtensionData()
        name = data.get("name") if data else None
        if not name:
            return None
        from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir
        cli_dir = os.path.join(get_cli_base_dir(), name)
        return cli_dir if os.path.isdir(cli_dir) else None

    def _loadStepInstructionsFile(self):
        """Load the extension's step_instructions.json -> {step_id: {...}}, or {}."""
        cli_dir = self._selectedExtCliDir()
        if not cli_dir:
            return {}
        path = os.path.join(cli_dir, "step_instructions.json")
        if not os.path.isfile(path):
            # Older packages wrote it under templates/ — fall back so the editor
            # shows the real instructions instead of the description fallback.
            legacy = os.path.join(cli_dir, "templates", "step_instructions.json")
            if os.path.isfile(legacy):
                path = legacy
        if not os.path.isfile(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return (json.load(f) or {}).get("steps", {}) or {}
        except Exception:
            return {}

    def _populateStepInstructionCombo(self, *args):
        """Fill the step dropdown from the selected extension's workflow.json."""
        combo = getattr(self, "_stepInstrStepCombo", None)
        if combo is None:
            return
        combo.blockSignals(True)
        combo.clear()
        cli_dir = self._selectedExtCliDir()
        if cli_dir:
            wf_path = os.path.join(cli_dir, "workflow.json")
            if os.path.isfile(wf_path):
                try:
                    with open(wf_path, "r", encoding="utf-8") as f:
                        graph = json.load(f)
                    for step in graph.get("steps", []) or []:
                        sid = step.get("step_id", "")
                        if not sid:
                            continue
                        title = (step.get("ui_guidance", {}) or {}).get("title", "") or step.get("description", "")
                        combo.addItem(f"{sid} — {str(title)[:40]}", sid)
                except Exception:
                    logger.debug("Failed to populate step instruction combo", exc_info=True)
        combo.blockSignals(False)
        self._onStepInstrStepChanged()

    def _onStepInstrStepChanged(self, *args):
        """Load the selected step's instructions into the editor fields."""
        combo = getattr(self, "_stepInstrStepCombo", None)
        if combo is None or combo.count == 0:
            return
        step_id = combo.itemData(combo.currentIndex)
        steps = self._loadStepInstructionsFile()
        entry = steps.get(step_id, {}) or {}
        # Fall back to workflow.json ui_guidance when no saved instruction yet.
        if not entry:
            cli_dir = self._selectedExtCliDir()
            if cli_dir:
                try:
                    with open(os.path.join(cli_dir, "workflow.json"), "r", encoding="utf-8") as f:
                        for step in (json.load(f).get("steps", []) or []):
                            if step.get("step_id") == step_id:
                                g = step.get("ui_guidance", {}) or {}
                                entry = {"title": g.get("title", ""),
                                         "simple": g.get("instruction", "") or step.get("description", ""),
                                         "detailed": step.get("description", "")}
                                break
                except Exception:
                    pass
        self._stepInstrTitle.setText(str(entry.get("title", "")))
        self._stepInstrSimple.setPlainText(str(entry.get("simple", "")))
        self._stepInstrDetailed.setPlainText(str(entry.get("detailed", "")))
        self._rebuildStepInstrButtonFields(step_id, entry)

    def _workflowStepById(self, step_id):
        """Return the selected extension's workflow.json step dict (read-only)."""
        cli_dir = self._selectedExtCliDir()
        if not cli_dir or not step_id:
            return {}
        try:
            with open(os.path.join(cli_dir, "workflow.json"), "r", encoding="utf-8") as f:
                for step in (json.load(f).get("steps", []) or []):
                    if step.get("step_id") == step_id:
                        return step
        except Exception:
            logger.debug("Failed to read workflow step for button editor", exc_info=True)
        return {}

    def _editorStepButtonSpec(self, step):
        """Which fixed-default buttons a step shows, for the label editor.

        Returns ``{"primary": <default or None>, "choices": [(value, label)...],
        "note": <str>}``. Read-only heuristic over the workflow.json step. Only
        the fixed-default buttons are editable: the single advance button
        (Done / Confirm / Set) and literal choice options. Node/segment pickers
        render live scene names and get no field (``note`` explains why).
        """
        step = step or {}
        subops = step.get("sub_operations") or []
        subop = subops[0] if subops and isinstance(subops[0], dict) else {}
        op_type = (step.get("operation_type")
                   or (step.get("operation_model", {}) or {}).get("step_type") or "")
        ui_g = step.get("ui_guidance", {}) or {}
        ci = step.get("choice_info", {}) or {}
        literal = ci.get("choices") or subop.get("choices") or []
        value_kind = str(subop.get("value_kind") or ci.get("value_kind") or "").lower()
        interaction_kind = str(subop.get("interaction_kind") or "").lower()
        is_interactive = (op_type in ("interactive", "mixed")
                          or (interaction_kind and interaction_kind not in ("none", "")))
        spec = {"primary": None, "choices": [], "note": ""}
        if literal:
            for ch in literal:
                if not isinstance(ch, dict):
                    continue
                val = ch.get("value", ch.get("label"))
                lbl = ch.get("label") or ch.get("value") or "Choice"
                spec["choices"].append((str(val), str(lbl)))
            if spec["choices"]:
                return spec
        if is_interactive:
            spec["primary"] = ui_g.get("done_label") or "Done"
            return spec
        if op_type in ("user_choice", "branch"):
            if value_kind == "node" or value_kind.startswith("segment"):
                spec["note"] = ("This step selects a live scene item — its button "
                                "text is the node/segment name and can't be preset.")
            elif value_kind in ("range", "scalar"):
                spec["primary"] = "Confirm"
            else:
                spec["primary"] = "Set"
            return spec
        spec["note"] = "This step runs automatically — it has no button."
        return spec

    def _rebuildStepInstrButtonFields(self, step_id, entry):
        """Rebuild the per-step button-label edit fields for the selected step."""
        form = getattr(self, "_stepInstrButtonsForm", None)
        if form is None:
            return
        while form.count():
            item = form.takeAt(0)
            widget = item.widget() if item else None
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._stepInstrButtonFields = {}
        spec = self._editorStepButtonSpec(self._workflowStepById(step_id))
        saved = entry.get("buttons", {}) if isinstance(entry.get("buttons"), dict) else {}
        saved_choices = saved.get("choices", {}) if isinstance(saved.get("choices"), dict) else {}
        added = False
        if spec.get("primary"):
            edit = qt.QLineEdit()
            edit.setText(str(saved.get("primary", "")))
            edit.setPlaceholderText(f"default: {spec['primary']}")
            form.addRow("Advance button:", edit)
            self._stepInstrButtonFields["primary"] = edit
            added = True
        for value, default_label in spec.get("choices", []):
            edit = qt.QLineEdit()
            edit.setText(str(saved_choices.get(value, "")))
            edit.setPlaceholderText(f"default: {default_label}")
            form.addRow(f"Option '{default_label[:24]}':", edit)
            self._stepInstrButtonFields[f"choice:{value}"] = edit
            added = True
        if not added:
            note = qt.QLabel(spec.get("note") or "This step has no editable button.")
            note.setWordWrap(True)
            note.setStyleSheet("color: gray; font-style: italic;")
            form.addRow(note)

    def _collectStepInstrButtonOverrides(self):
        """Gather the current button-label fields into a ``buttons`` dict (or {})."""
        buttons = {}
        fields = getattr(self, "_stepInstrButtonFields", {}) or {}
        primary_edit = fields.get("primary")
        if primary_edit is not None:
            val = primary_edit.text.strip()
            if val:
                buttons["primary"] = val
        choice_overrides = {}
        for key, edit in fields.items():
            if not key.startswith("choice:"):
                continue
            val = edit.text.strip()
            if val:
                choice_overrides[key[len("choice:"):]] = val
        if choice_overrides:
            buttons["choices"] = choice_overrides
        return buttons

    def _onSaveStepInstructions(self):
        """Write the edited step back to step_instructions.json (edited=true)."""
        combo = getattr(self, "_stepInstrStepCombo", None)
        cli_dir = self._selectedExtCliDir()
        if combo is None or combo.count == 0 or not cli_dir:
            return
        step_id = combo.itemData(combo.currentIndex)
        # Always write to the canonical root location; seed from whichever copy
        # exists (root, or a legacy templates/ copy) so an edit migrates it.
        path = os.path.join(cli_dir, "step_instructions.json")
        read_path = path
        if not os.path.isfile(read_path):
            legacy = os.path.join(cli_dir, "templates", "step_instructions.json")
            if os.path.isfile(legacy):
                read_path = legacy
        doc = {"version": 1, "steps": {}}
        if os.path.isfile(read_path):
            try:
                with open(read_path, "r", encoding="utf-8") as f:
                    doc = json.load(f) or doc
            except Exception:
                pass
        new_entry = {
            "title": self._stepInstrTitle.text.strip(),
            "simple": self._stepInstrSimple.toPlainText().strip(),
            "detailed": self._stepInstrDetailed.toPlainText().strip(),
            "edited": True,
        }
        buttons = self._collectStepInstrButtonOverrides()
        if buttons:
            new_entry["buttons"] = buttons
        doc.setdefault("steps", {})[step_id] = new_entry
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2)
            from SlicerAIAgentLib.ExtensionCLILoader import invalidate_cache
            invalidate_cache()
            self._cliStatusLabel.setText(f"Saved instructions for {step_id}")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: green;")
        except Exception as exc:
            self._cliStatusLabel.setText(f"Save failed: {exc}")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")

    def _onRegenerateInstructions(self):
        """Regenerate all step instructions off-thread (keeps user-edited steps)."""
        data = self._getSelectedExtensionData()
        ext_name = data.get("name") if data else None
        cli_dir = self._selectedExtCliDir()
        if not ext_name or not cli_dir:
            return
        if not (self.logic and self.logic.llmClient):
            self._cliStatusLabel.setText("Configure an API key first")
            return
        self._cliStatusLabel.setText("Regenerating instructions...")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: orange;")

        def _run():
            try:
                from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
                from SlicerAIAgentLib.CodeValidator import CodeValidator
                from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir, invalidate_cache
                with open(os.path.join(cli_dir, "workflow.json"), "r", encoding="utf-8") as f:
                    wf = json.load(f)
                md = {}
                md_path = os.path.join(cli_dir, "workflow_metadata.json")
                if os.path.isfile(md_path):
                    with open(md_path, "r", encoding="utf-8") as f:
                        md = json.load(f)
                ipath = os.path.join(cli_dir, "step_instructions.json")
                existing = {}
                if os.path.isfile(ipath):
                    with open(ipath, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                analyzer = ExtensionCLIAnalyzer(
                    llm_client=self.logic.llmClient,
                    output_base_dir=get_cli_base_dir(),
                    code_validator=CodeValidator(),
                )
                result = analyzer.generate_step_instructions(
                    wf, md, {"module_name": ext_name}, {}, cookbook_def=None, existing=existing,
                )
                # Preserve per-step button-label overrides: they are user-authored
                # UI text the generation pipeline does not manage, so carry them
                # over from the pre-regen file instead of dropping them.
                ex_steps = (existing or {}).get("steps", {}) or {}
                for sid, sdata in (result.get("steps", {}) or {}).items():
                    if not isinstance(sdata, dict):
                        continue
                    btns = (ex_steps.get(sid, {}) or {}).get("buttons")
                    if btns:
                        sdata["buttons"] = btns
                with open(ipath, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
                invalidate_cache()
                self._streamQueue.put(('cli_instructions_regenerated', {"ext": ext_name}))
            except Exception as exc:
                self._streamQueue.put(('cli_error', str(exc)))

        threading.Thread(target=_run, daemon=True).start()

    def _handleInstructionsRegenerated(self, payload):
        """Main-thread completion of a regenerate: refresh editor + status."""
        self._cliStatusLabel.setText("Instructions regenerated ✓")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: green;")
        self._onStepInstrStepChanged()
