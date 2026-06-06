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

        # Row 1: Source selector + Refresh button
        sourceLayout = qt.QHBoxLayout()
        sourceLabel = qt.QLabel("Source:")
        sourceLayout.addWidget(sourceLabel)

        self._sourceSelector = qt.QComboBox()
        self._sourceSelector.setToolTip("Select the extension source to browse")
        self._sourceSelector.setMinimumWidth(200)
        self._sourceSelector.addItems(["Extension Manager", "Additional Module Paths", "Loaded Modules"])
        sourceLayout.addWidget(self._sourceSelector, 1)

        self._refreshExtensionsButton = qt.QPushButton("Refresh")
        self._refreshExtensionsButton.setToolTip("Re-scan extensions from the selected source")
        self._refreshExtensionsButton.setMaximumWidth(80)
        sourceLayout.addWidget(self._refreshExtensionsButton)

        cliLayout.addLayout(sourceLayout)

        # Row 2: Extension selector (populated based on source)
        extLayout = qt.QHBoxLayout()
        extLabel = qt.QLabel("Extension:")
        extLayout.addWidget(extLabel)

        self._extensionSelector = qt.QComboBox()
        self._extensionSelector.setToolTip("Select an extension from the chosen source")
        self._extensionSelector.setMinimumWidth(200)
        extLayout.addWidget(self._extensionSelector, 1)

        cliLayout.addLayout(extLayout)

        # Store extension data separately (keyed by label text)
        self._extensionDataMap = {}
        self._discoveredExtensions = []

        # Row 3: Analyze & Generate button
        self._analyzeGenerateButton = qt.QPushButton("Analyze & Generate CLI")
        self._analyzeGenerateButton.setToolTip(
            "Analyze the selected extension and generate operation CLI tools"
        )
        self._analyzeGenerateButton.setEnabled(False)
        cliLayout.addWidget(self._analyzeGenerateButton)

        # Row 4: Progress display
        self._cliProgressDisplay = qt.QTextEdit()
        self._cliProgressDisplay.setReadOnly(True)
        self._cliProgressDisplay.setMaximumHeight(150)
        self._cliProgressDisplay.setFont(qt.QFont("Monospace", 9))
        self._cliProgressDisplay.setPlaceholderText("Progress will appear here...")
        cliLayout.addWidget(self._cliProgressDisplay)

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

        # Row 7: Action buttons
        actionLayout = qt.QHBoxLayout()
        self._testCliButton = qt.QPushButton("Test CLI")
        self._testCliButton.setToolTip("Validate generated templates with CodeValidator")
        self._testCliButton.setEnabled(False)
        actionLayout.addWidget(self._testCliButton)

        self._deleteCliButton = qt.QPushButton("Delete CLI")
        self._deleteCliButton.setToolTip("Remove the generated CLI files")
        self._deleteCliButton.setEnabled(False)
        actionLayout.addWidget(self._deleteCliButton)

        self._reviseCliButton = qt.QPushButton("Revise with LLM")
        self._reviseCliButton.setToolTip("Fix failed validation using LLM revision")
        self._reviseCliButton.setEnabled(False)
        actionLayout.addWidget(self._reviseCliButton)

        cliLayout.addLayout(actionLayout)

        # Internal state
        self._cliGeneratorRunning = False

        # Connect signals
        self._refreshExtensionsButton.clicked.connect(self._onRefreshExtensionsClicked)
        self._sourceSelector.currentIndexChanged.connect(self._onSourceSelectionChanged)
        self._extensionSelector.currentIndexChanged.connect(self._onExtensionSelectionChanged)
        self._analyzeGenerateButton.clicked.connect(self._onAnalyzeGenerateClicked)
        self._testCliButton.clicked.connect(self._onTestCliClicked)
        self._deleteCliButton.clicked.connect(self._onDeleteCliClicked)
        self._reviseCliButton.clicked.connect(self._onReviseCliClicked)

        # Populate initial extension list
        self._onRefreshExtensionsClicked()

    def _onRefreshExtensionsClicked(self):
        """Re-scan extensions from all sources and populate based on current source selection."""
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import discover_installed_extensions
            self._discoveredExtensions = discover_installed_extensions()
        except Exception:
            self._discoveredExtensions = []

        self._populateExtensionSelector()

    def _onSourceSelectionChanged(self, index):
        """When the source combo changes, repopulate the extension list."""
        self._populateExtensionSelector()

    # Map from source combo label to source_type tag in discovered extensions
    _SOURCE_TYPE_MAP = {
        "Extension Manager": "extension_manager",
        "Additional Module Paths": "additional_paths",
        "Loaded Modules": "loaded_modules",
    }

    def _populateExtensionSelector(self):
        """Populate the extension combo box based on the selected source."""
        self._extensionSelector.clear()
        self._extensionDataMap.clear()

        source_label = self._sourceSelector.currentText
        source_type = self._SOURCE_TYPE_MAP.get(source_label, "")
        if not source_type:
            return

        module_dir = SLICER_AI_AGENT_ROOT
        cookbook_dir = os.path.join(module_dir, "Resources", "extensions_cookbook")

        for ext in self._discoveredExtensions:
            if ext.get("source_type") != source_type:
                continue

            name = ext["name"]
            label = name
            # Check for cookbook
            has_cookbook = (
                os.path.isfile(os.path.join(cookbook_dir, f"{name}.md"))
                or os.path.isfile(os.path.join(cookbook_dir, f"Slicer{name}.md"))
            )
            if has_cookbook:
                label += " [has cookbook]"
            else:
                label += " [no cookbook]"
            if ext.get("cli_status"):
                label += f" [{ext['cli_status']}]"
            if not ext.get("has_python"):
                label += " (no Python)"
            self._extensionDataMap[label] = {
                "type": "installed",
                "name": name,
                "path": ext.get("source_path", ext.get("install_path", "")),
                "source_type": ext.get("source_type", ""),
            }
            self._extensionSelector.addItem(label)

        # Enable the button if a valid selection exists after population
        has_selection = self._extensionSelector.currentIndex >= 0
        self._analyzeGenerateButton.setEnabled(has_selection and not self._cliGeneratorRunning)

    def _onExtensionSelectionChanged(self, index):
        """Enable/disable the Analyze button based on selection."""
        has_selection = index >= 0
        self._analyzeGenerateButton.setEnabled(has_selection and not self._cliGeneratorRunning)

    def _onAnalyzeGenerateClicked(self):
        """Start the analysis pipeline in a background thread."""
        data = self._getSelectedExtensionData()
        if not data:
            return

        ext_name = data["name"]
        source_path = data["path"]

        if not source_path or not os.path.isdir(source_path):
            self._cliProgressDisplay.append(f"Error: Source path not found: {source_path}")
            return

        # Cookbook is required for CLI generation
        module_dir = SLICER_AI_AGENT_ROOT
        cookbook_dir = os.path.join(module_dir, "Resources", "extensions_cookbook")
        has_cookbook = (
            os.path.isfile(os.path.join(cookbook_dir, f"{ext_name}.md"))
            or os.path.isfile(os.path.join(cookbook_dir, f"Slicer{ext_name}.md"))
        )
        if not has_cookbook:
            self._cliProgressDisplay.append(
                f"Error: No cookbook found for '{ext_name}'. "
                f"Create one at Resources/extensions_cookbook/{ext_name}.md first."
            )
            return

        if self._cliGeneratorRunning:
            return

        self._cliGeneratorRunning = True
        self._analyzeGenerateButton.setEnabled(False)
        self._cliStatusLabel.setText("Analyzing...")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: orange;")
        self._cliProgressDisplay.clear()
        self._cliResultGroup.setVisible(False)
        self._reviseCliButton.setEnabled(False)

        self._cliProgressDisplay.append(f"Starting analysis of '{ext_name}'...")
        self._cliProgressDisplay.append(f"Source: {source_path}")

        # Run in background thread
        import threading

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
                        },
                    ))
                    try:
                        return response_queue.get(timeout=30)
                    except queue.Empty:
                        return {"error": "Timeout waiting for main-thread live API probe"}

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
                    live_probe_executor=_run_live_probe_on_main_thread,
                )

                result = analyzer.analyze_and_generate(
                    extension_name=ext_name,
                    source_path=source_path,
                    force_overwrite=False,
                )
                self._streamQueue.put(('cli_complete', result))

            except Exception as e:
                import traceback
                self._streamQueue.put(('cli_error', f"{e}\n{traceback.format_exc()}"))

        thread = threading.Thread(target=_run_analysis, daemon=True)
        thread.start()

    def _onTestCliClicked(self):
        """Validate generated templates with CodeValidator."""
        data = self._getSelectedExtensionData()
        if not data:
            return

        ext_name = data["name"]
        from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir
        cli_dir = os.path.join(get_cli_base_dir(), ext_name)
        if not os.path.isdir(cli_dir):
            self._cliProgressDisplay.append(f"No CLI directory found for {ext_name}")
            return

        # Load generators to find template files
        gen_path = os.path.join(cli_dir, "code_generators.json")
        if not os.path.isfile(gen_path):
            self._cliProgressDisplay.append("No code_generators.json found")
            return

        with open(gen_path, "r") as f:
            generators = json.load(f)

        from SlicerAIAgentLib.CodeValidator import CodeValidator
        validator = CodeValidator()
        from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer

        self._cliProgressDisplay.append("Running validation tests...")
        all_pass = True

        for gen in generators:
            tpl_file = gen.get("template_file", "")
            tpl_path = os.path.join(cli_dir, tpl_file)
            if not os.path.isfile(tpl_path):
                self._cliProgressDisplay.append(f"  SKIP: {tpl_file} not found")
                continue

            with open(tpl_path, "r") as f:
                content = f.read()

            sample = content.replace(
                "{vol_lookup}",
                "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
            )
            sample = ExtensionCLIAnalyzer._fill_remaining_placeholders(sample)
            result = validator.validate(sample)
            if "SLICER_OP_GENERATION_FAILED" in sample:
                result["valid"] = False
                result["reason"] = (
                    "Slicer-op template generation failed due to insufficient retrieval evidence"
                )

            status = "PASS" if result.get("valid", True) else "FAIL"
            self._cliProgressDisplay.append(f"  {tpl_file}: {status}")
            if not result.get("valid", True):
                all_pass = False
                self._cliProgressDisplay.append(f"    Error: {result.get('reason', 'unknown')}")
            for w in result.get("warnings", []):
                self._cliProgressDisplay.append(f"    Warning: {w}")

        if all_pass:
            self._cliStatusLabel.setText("Validated")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: green;")
            self._reviseCliButton.setEnabled(False)
        else:
            self._cliStatusLabel.setText("Validation Failed")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")
            self._reviseCliButton.setEnabled(True)

    def _onDeleteCliClicked(self):
        """Delete the CLI for the selected extension."""
        data = self._getSelectedExtensionData()
        if not data:
            return

        ext_name = data["name"]

        # Confirm
        reply = qt.QMessageBox.question(
            None, "Delete CLI",
            f"Delete the generated CLI for '{ext_name}'?",
            qt.QMessageBox.Yes | qt.QMessageBox.No,
        )
        if reply != qt.QMessageBox.Yes:
            return

        from SlicerAIAgentLib.ExtensionCLILoader import delete_cli
        if delete_cli(ext_name):
            self._cliProgressDisplay.append(f"Deleted CLI for '{ext_name}'")
            self._cliStatusLabel.setText("Ready")
            self._cliStatusLabel.setStyleSheet("font-weight: bold;")
            self._cliResultGroup.setVisible(False)
            self._testCliButton.setEnabled(False)
            self._deleteCliButton.setEnabled(False)
            self._reviseCliButton.setEnabled(False)
            self._onRefreshExtensionsClicked()
        else:
            self._cliProgressDisplay.append(f"No CLI found for '{ext_name}'")

    def _onReviseCliClicked(self):
        """Revise failed templates using LLM feedback."""
        data = self._getSelectedExtensionData()
        if not data:
            return

        ext_name = data["name"]
        source_path = data.get("path", "")

        if self._cliGeneratorRunning:
            return

        self._cliGeneratorRunning = True
        self._cliStatusLabel.setText("Revising...")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: orange;")
        self._reviseCliButton.setEnabled(False)

        # Collect errors from the progress display
        progress_text = self._cliProgressDisplay.toPlainText()
        errors = [
            line.strip() for line in progress_text.split("\n")
            if "Error:" in line or "FAIL" in line
        ]

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

    def _autoReviseCli(self, generation_result):
        """Automatically trigger LLM revision after generation validation fails."""
        data = self._getSelectedExtensionData()
        if not data:
            self._reviseCliButton.setEnabled(True)
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
        current_text = self._extensionSelector.currentText
        if not current_text:
            return None
        return self._extensionDataMap.get(current_text)
