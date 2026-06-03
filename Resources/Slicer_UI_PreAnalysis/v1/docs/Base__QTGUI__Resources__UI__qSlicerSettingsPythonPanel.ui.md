# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsPythonPanel.ui

- Owner class: `qSlicerSettingsPythonPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsPythonPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsPythonPanel

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsPythonPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:30: #include "qSlicerSettingsPythonPanel.h"`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:31: #include "ui_qSlicerSettingsPythonPanel.h"`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:34: // qSlicerSettingsPythonPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:37: class qSlicerSettingsPythonPanelPrivate : public Ui_qSlicerSettingsPythonPanel`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:39: Q_DECLARE_PUBLIC(qSlicerSettingsPythonPanel);`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:42: qSlicerSettingsPythonPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:45: qSlicerSettingsPythonPanelPrivate(qSlicerSettingsPythonPanel& object);`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:52: // qSlicerSettingsPythonPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:55: qSlicerSettingsPythonPanelPrivate::qSlicerSettingsPythonPanelPrivate(qSlicerSettingsPythonPanel& object)`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:61: void qSlicerSettingsPythonPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:63: Q_Q(qSlicerSettingsPythonPanel);`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:69: qWarning() << "qSlicerSettingsPythonPanelPrivate requires a python console";`
- Connected slots/functions: `consoleLogLevelChanged`, `currentTextChanged`, `onConsoleLogLevelChanged`

## widget: GeneralGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: GeneralGroupBox | QGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`

## widget: EditorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Editor for .py files: | EditorLabel | QLabel
- Text: Editor for .py files:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`

## widget: EditorPathLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `ctkPathLineEdit`
- Search text: Select an executable for editing .py files. If left empty then the default program associated with .py files will be launched. | EditorPathLineEdit | ctkPathLineEdit
- Tooltip: Select an executable for editing .py files. If left empty then the default program associated with .py files will be launched.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:96: this->EditorPathLineEdit,`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:171: if (!d->EditorPathLineEdit->currentPath().isEmpty())`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:173: d->EditorPathLineEdit->addCurrentPathToHistory();`

## widget: ShellDisplayGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: ShellDisplayGroupBox | QGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`

## widget: DockableWindowLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Display in dockable window: | DockableWindowLabel | QLabel
- Text: Display in dockable window:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`

## widget: DockableWindowCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCheckBox`
- Search text: Display Python console in a window that can be placed inside the main window. If disabled then the Python Console is displayed as an independent window. | DockableWindowCheckBox | ctkCheckBox
- Tooltip: Display Python console in a window that can be placed inside the main window. If disabled then the Python Console is displayed as an independent window.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:102: this->DockableWindowCheckBox,`
- Key UI properties: {"checked": "true"}

## widget: PromptFontLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Font: | PromptFontLabel | QLabel
- Text: Font:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`

## widget: ConsoleFontButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkFontButton`
- Search text: ConsoleFontButton | ctkFontButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:75: this->ConsoleFontButton->setCurrentFont(this->PythonConsole->shellFont());`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:88: QObject::connect(this->ConsoleFontButton, SIGNAL(currentFontChanged(QFont)), q, SLOT(onFontChanged(QFont)));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:108: q->registerProperty("Python/Font", this->ConsoleFontButton, "currentFont", SIGNAL(currentFontChanged(QFont)));`
- Connected slots/functions: `onFontChanged`

## widget: LogLevelLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Log level: | LogLevelLabel | QLabel
- Text: Log level:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`

## widget: ConsoleLogLevelComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `QComboBox`
- Search text: Log messages at this level and above are displayed in the Python console. | ConsoleLogLevelComboBox | QComboBox
- Tooltip: Log messages at this level and above are displayed in the Python console.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsPythonPanel.cxx`, `Base/QTGUI/qSlicerSettingsPythonPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:77: this->ConsoleLogLevelComboBox->addItem(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::None));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:78: this->ConsoleLogLevelComboBox->addItem(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::Error));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:79: this->ConsoleLogLevelComboBox->addItem(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::Warning));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:80: this->ConsoleLogLevelComboBox->addItem(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::Info));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:81: this->ConsoleLogLevelComboBox->addItem(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::Debug));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:82: this->ConsoleLogLevelComboBox->setCurrentText(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::Warning));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:89: QObject::connect(this->ConsoleLogLevelComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsPythonPanel::onConsoleLogLevelChanged);`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:111: QObject::connect(this->ConsoleLogLevelComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsPythonPanel::consoleLogLevelChanged);`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:150: return d->ConsoleLogLevelComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:157: int selectedIndex = d->ConsoleLogLevelComboBox->findText(text);`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:161: selectedIndex = d->ConsoleLogLevelComboBox->findText(ctkErrorLogLevel::logLevelAsString(ctkErrorLogLevel::Warning));`
  - `Base/QTGUI/qSlicerSettingsPythonPanel.cxx:164: d->ConsoleLogLevelComboBox->setCurrentIndex(selectedIndex);`
- Connected slots/functions: `consoleLogLevelChanged`, `currentTextChanged`, `onConsoleLogLevelChanged`
