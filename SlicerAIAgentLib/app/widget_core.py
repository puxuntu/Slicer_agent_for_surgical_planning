from .common import *
from .logic import SlicerAIAgentLogic


class WidgetCoreMixin:
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        uiFilePath = os.path.join(SLICER_AI_AGENT_ROOT, 'Resources', 'UI', 'SlicerAIAgent.ui')
        if os.path.exists(uiFilePath):
            self.ui = slicer.util.loadUI(uiFilePath)
            self.layout.addWidget(self.ui)
            self._connectUIWidgets()
            self.setupConnections()
        else:
            self.setupUIProgrammatically()

        self.logic = SlicerAIAgentLogic()
        self.loadSettings()

        # Extension CLI Generator UI (insert after Settings, before Conversation History)
        self._setupExtensionCLIGenerator()

        # Interactive workflow UI
        self._setupWorkflowUI()

        # Keep the module from forcing the panel wider when first opened.
        self._relaxContentWidth()

        self._streamPollTimer = qt.QTimer()
        self._streamPollTimer.setInterval(50)
        self._streamPollTimer.timeout.connect(self._drainStreamQueue)
        self._streamPollTimer.start()

        # Index status: one-time console log only (no UI label)
        self._indexStatusTimer = None
        self._updateIndexStatus()

        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        logger.info("SlicerAIAgent widget setup complete")

    def _relaxContentWidth(self):
        """Stop the agent from widening Slicer's module panel when opened.

        Slicer sizes the panel to the module's content width on show. Several
        agent widgets report a wide preferred/minimum width — the long
        model-name combo, the chat/code QTabWidget, the prompt box, the CLI
        fields — and, crucially, a collapsed ctkCollapsibleGroupBox still
        propagates its children's WIDTH (it collapses height only), so even the
        hidden Settings / Debug / Extension-CLI fields push the panel wide.

        Setting every field widget's HORIZONTAL size policy to ``Ignored`` makes
        each one demand no width of its own and simply fill whatever width the
        panel already has. The only remaining width floor is the (small, fixed)
        labels and buttons, so opening the agent leaves the panel at the user's
        width — matching other modules. Vertical behaviour is left untouched.
        """
        root = getattr(self, "ui", None)
        if root is None:
            return
        try:
            import slicer
            targets = []
            for class_name in ("QComboBox", "QTextEdit", "QLineEdit", "QTabWidget", "QPlainTextEdit"):
                targets += list(slicer.util.findChildren(root, className=class_name) or [])
            for widget in targets:
                try:
                    vertical = widget.sizePolicy().verticalPolicy()
                    widget.setMinimumWidth(0)
                    widget.setSizePolicy(qt.QSizePolicy.Ignored, vertical)
                except Exception:
                    pass
        except Exception:
            logger.debug("relax content width failed", exc_info=True)

    def _connectUIWidgets(self):
        self.providerSelector = self.ui.findChild(qt.QComboBox, "providerSelector")
        self.modelSelector = self.ui.findChild(qt.QComboBox, "modelSelector")
        self.baseUrlInput = self.ui.findChild(qt.QLineEdit, "baseUrlInput")
        self.apiKeyInput = self.ui.findChild(qt.QLineEdit, "apiKeyInput")
        self.saveSettingsButton = self.ui.findChild(qt.QPushButton, "saveSettingsButton")
        self.testConnectionButton = self.ui.findChild(qt.QPushButton, "testConnectionButton")
        self.chatHistory = self.ui.findChild(qt.QTextEdit, "chatHistory")
        self.codeDisplay = self.ui.findChild(qt.QTextEdit, "codeDisplay")
        self._workflowUserFrame = self.ui.findChild(qt.QFrame, "workflowUserFrame")
        self._workflowTitleLabel = self.ui.findChild(qt.QLabel, "workflowTitleLabel")
        self._workflowStatusLabel = self.ui.findChild(qt.QLabel, "workflowStatusLabel")
        self._workflowProgressBar = self.ui.findChild(qt.QProgressBar, "workflowProgressBar")
        self._workflowStepLabel = self.ui.findChild(qt.QLabel, "workflowStepLabel")
        self._workflowActionLabel = self.ui.findChild(qt.QLabel, "workflowActionLabel")
        self._workflowInstructionLabel = self.ui.findChild(qt.QLabel, "workflowInstructionLabel")
        self._workflowDoneButton = self.ui.findChild(qt.QPushButton, "workflowDoneButton")
        self._workflowSkipButton = self.ui.findChild(qt.QPushButton, "workflowSkipButton")
        self._workflowCancelButton = self.ui.findChild(qt.QPushButton, "workflowCancelButton")
        self._workflowChoiceContainer = self.ui.findChild(qt.QWidget, "workflowChoiceContainer")
        self._workflowChoiceLayout = (
            self._workflowChoiceContainer.layout()
            if self._workflowChoiceContainer is not None
            else self.ui.findChild(qt.QHBoxLayout, "workflowChoiceLayout")
        )
        # Note: executeButton and copyButton removed - code is auto-executed
        self.clearChatButton = self.ui.findChild(qt.QPushButton, "clearChatButton")
        self.promptInput = self.ui.findChild(qt.QTextEdit, "promptInput")
        self.sendButton = self.ui.findChild(qt.QPushButton, "sendButton")
        self.statusLabel = self.ui.findChild(qt.QLabel, "statusLabel")
        self.tokenLabel = self.ui.findChild(qt.QLabel, "tokenLabel")
        self.thinkingTimerLabel = self.ui.findChild(qt.QLabel, "thinkingTimerLabel")
        # Vector index status label — hidden, only console logging is used
        self.indexStatusLabel = self.ui.findChild(qt.QLabel, "indexStatusLabel")
        if self.indexStatusLabel:
            self.indexStatusLabel.setVisible(False)
        else:
            self._injectIndexStatusLabel()

    def setupUIProgrammatically(self):
        self.ui = ctk.ctkCollapsibleButton()
        self.ui.text = "Slicer AI Agent"
        self.layout.addWidget(self.ui)

        mainLayout = qt.QVBoxLayout(self.ui)

        settingsGroup = ctk.ctkCollapsibleGroupBox()
        settingsGroup.title = "Settings"
        settingsGroup.collapsed = True
        mainLayout.addWidget(settingsGroup)

        settingsLayout = qt.QFormLayout(settingsGroup)

        # Row 1: Provider + Model
        providerModelLayout = qt.QHBoxLayout()
        self.providerSelector = qt.QComboBox()
        self.providerSelector.addItems(["Kimi", "DeepSeek", "Claude", "OpenAI", "Qwen"])
        self.providerSelector.setToolTip("Select AI provider")
        providerModelLayout.addWidget(self.providerSelector)

        self.modelSelector = qt.QComboBox()
        self.modelSelector.setEditable(True)
        self.modelSelector.setToolTip("Select or type a model name")
        providerModelLayout.addWidget(self.modelSelector)
        settingsLayout.addRow("Provider / Model:", providerModelLayout)

        # Row 2: Base URL
        self.baseUrlInput = qt.QLineEdit()
        self.baseUrlInput.setPlaceholderText("API base URL")
        settingsLayout.addRow("Base URL:", self.baseUrlInput)

        # Row 3: API Key + Test button
        apiKeyLayout = qt.QHBoxLayout()
        self.apiKeyInput = qt.QLineEdit()
        self.apiKeyInput.setEchoMode(qt.QLineEdit.Password)
        self.apiKeyInput.setPlaceholderText("Enter your API key")
        apiKeyLayout.addWidget(self.apiKeyInput)

        self.testConnectionButton = qt.QPushButton("Test")
        self.testConnectionButton.setToolTip("Test API connection")
        apiKeyLayout.addWidget(self.testConnectionButton)
        settingsLayout.addRow("API Key:", apiKeyLayout)

        # Row 4: Save Settings
        self.saveSettingsButton = qt.QPushButton("Save Settings")
        settingsLayout.addRow(self.saveSettingsButton)

        chatLabel = qt.QLabel("Conversation:")
        mainLayout.addWidget(chatLabel)

        self.chatHistory = qt.QTextEdit()
        self.chatHistory.setReadOnly(True)
        self.chatHistory.setMinimumHeight(300)
        mainLayout.addWidget(self.chatHistory)

        codeLabel = qt.QLabel("Generated Code:")
        mainLayout.addWidget(codeLabel)

        self.codeDisplay = qt.QTextEdit()
        self.codeDisplay.setReadOnly(True)
        self.codeDisplay.setMinimumHeight(150)
        self.codeDisplay.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace;")
        mainLayout.addWidget(self.codeDisplay)

        codeButtonLayout = qt.QHBoxLayout()
        self.executeButton = qt.QPushButton("Execute Code")
        self.executeButton.setEnabled(False)
        self.copyButton = qt.QPushButton("Copy to Clipboard")
        self.clearChatButton = qt.QPushButton("Clear Chat")
        codeButtonLayout.addWidget(self.executeButton)
        codeButtonLayout.addWidget(self.copyButton)
        codeButtonLayout.addWidget(self.clearChatButton)
        mainLayout.addLayout(codeButtonLayout)

        inputLayout = qt.QHBoxLayout()
        self.promptInput = qt.QTextEdit()
        self.promptInput.setPlaceholderText("Type your request here... (e.g., 'Load a sample volume and create a volume rendering')")
        self.promptInput.setMaximumHeight(80)
        self.sendButton = qt.QPushButton("Send")
        self.sendButton.setMinimumHeight(80)
        inputLayout.addWidget(self.promptInput, stretch=1)
        inputLayout.addWidget(self.sendButton)
        mainLayout.addLayout(inputLayout)

        statusTimerLayout = qt.QHBoxLayout()
        self.statusLabel = qt.QLabel("Ready")
        self.thinkingTimerLabel = qt.QLabel("")
        self.thinkingTimerLabel.setStyleSheet("color: #666; font-size: 11px;")
        self.thinkingTimerLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        statusTimerLayout.addWidget(self.statusLabel, stretch=1)
        statusTimerLayout.addWidget(self.thinkingTimerLabel)
        mainLayout.addLayout(statusTimerLayout)

        self.tokenLabel = qt.QLabel("Tokens: 0 | Cost: $0.000")
        mainLayout.addWidget(self.tokenLabel)

        self.setupConnections()

    def setupConnections(self):
        if hasattr(self, 'sendButton') and self.sendButton is not None:
            self.sendButton.clicked.connect(self.onSendButtonClicked)
        if hasattr(self, 'promptInput') and self.promptInput is not None:
            self.promptInput.textChanged.connect(self.onPromptTextChanged)
            # Add Ctrl+Enter shortcut for sending
            self.sendShortcut = qt.QShortcut(qt.QKeySequence("Ctrl+Return"), self.promptInput)
            self.sendShortcut.connect('activated()', self.onSendButtonClicked)
        # Note: Button connections removed - code is auto-executed

        # Thinking timer
        self._thinkingTimer = qt.QTimer()
        self._thinkingTimer.setInterval(100)
        self._thinkingTimer.timeout.connect(self._updateThinkingTimer)
        self._thinkingStartTime = None
        if hasattr(self, 'clearChatButton') and self.clearChatButton is not None:
            self.clearChatButton.clicked.connect(self.onClearChatButtonClicked)
        if hasattr(self, 'saveSettingsButton') and self.saveSettingsButton is not None:
            self.saveSettingsButton.clicked.connect(self.onSaveSettings)
        if hasattr(self, 'testConnectionButton') and self.testConnectionButton is not None:
            self.testConnectionButton.clicked.connect(self.onTestConnection)
        if hasattr(self, 'providerSelector') and self.providerSelector is not None:
            self.providerSelector.currentTextChanged.connect(self.onProviderChanged)

    def disconnect(self):
        self.removeObservers()
        try:
            if hasattr(self, 'sendButton') and self.sendButton is not None:
                self.sendButton.clicked.disconnect()
            if hasattr(self, 'promptInput') and self.promptInput is not None:
                self.promptInput.textChanged.disconnect()
            if hasattr(self, 'sendShortcut') and self.sendShortcut is not None:
                self.sendShortcut.disconnect()
            if hasattr(self, 'clearChatButton') and self.clearChatButton is not None:
                self.clearChatButton.clicked.disconnect()
        except RuntimeError:
            pass

    def cleanup(self):
        self.disconnect()
        if self._streamPollTimer:
            self._streamPollTimer.stop()
        if hasattr(self, '_indexStatusTimer') and self._indexStatusTimer:
            self._indexStatusTimer.stop()
        if self.logic:
            self.logic.cleanup()
        logger.info("SlicerAIAgent widget cleaned up")

    def _injectIndexStatusLabel(self):
        """No-op: index status is logged to console only, not shown in UI."""
        self.indexStatusLabel = None

    def _updateIndexStatus(self):
        """Log vector index status to console only; no UI indicator."""
        if not self.logic:
            logger.info("Vector index status: Not initialized")
            return

        status = self.logic.get_index_status()
        if status != "Ready":
            logger.info(f"Vector index status: {status} — pre-retrieval will be skipped. Run 'python scripts/build_rag.py' to build the index.")
