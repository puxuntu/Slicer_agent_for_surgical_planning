# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsGeneralPanel.ui

- Owner class: `qSlicerSettingsGeneralPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsGeneralPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsGeneralPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsGeneralPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:38: #include "qSlicerSettingsGeneralPanel.h"`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:39: #include "ui_qSlicerSettingsGeneralPanel.h"`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:48: // qSlicerSettingsGeneralPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:51: class qSlicerSettingsGeneralPanelPrivate : public Ui_qSlicerSettingsGeneralPanel`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:53: Q_DECLARE_PUBLIC(qSlicerSettingsGeneralPanel);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:56: qSlicerSettingsGeneralPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:59: qSlicerSettingsGeneralPanelPrivate(qSlicerSettingsGeneralPanel& object);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:64: // qSlicerSettingsGeneralPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:67: qSlicerSettingsGeneralPanelPrivate::qSlicerSettingsGeneralPanelPrivate(qSlicerSettingsGeneralPanel& object)`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:73: void qSlicerSettingsGeneralPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:75: Q_Q(qSlicerSettingsGeneralPanel);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:110: qSlicerSettingsGeneralPanel::tr("Application update server URL"));`

## widget: DefaultScenePathLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default scene location: | Directory where scenes are saved to by default | DefaultScenePathLabel | QLabel
- Text: Default scene location:
- Tooltip: Directory where scenes are saved to by default
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: DefaultScenePathButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDirectoryButton`
- Search text: DefaultScenePathButton | ctkDirectoryButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:149: this->DefaultScenePathButton->setDirectory(qSlicerCoreApplication::application()->defaultScenePath());`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:150: qSlicerRelativePathMapper* relativePathMapper = new qSlicerRelativePathMapper(this->DefaultScenePathButton,`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:154: QObject::connect(this->DefaultScenePathButton, SIGNAL(directoryChanged(QString)), q, SLOT(setDefaultScenePath(QString)));`
- Connected slots/functions: `setDefaultScenePath`

## widget: ShowSplashScreenLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Disable splash screen: | ShowSplashScreenLabel | QLabel
- Text: Disable splash screen:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: ShowSplashScreenCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: ShowSplashScreenCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:160: q->registerProperty("no-splash", this->ShowSplashScreenCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`

## widget: LanguageComboBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkLanguageComboBox`
- Search text: LanguageComboBox | ctkLanguageComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:83: this->LanguageComboBox->setVisible(internationalizationEnabled);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:88: this->LanguageComboBox->setCountryFlagsVisible(false);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:89: this->LanguageComboBox->setDefaultLanguage("en");`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:90: this->LanguageComboBox->setDirectories(qSlicerCoreApplication::translationFolders());`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:94: this->LanguageComboBox->setVisible(false);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:190: this->LanguageComboBox,`

## widget: LanguageLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Language | LanguageLabel | QLabel
- Text: Language
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:82: this->LanguageLabel->setVisible(internationalizationEnabled);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:93: this->LanguageLabel->setVisible(false);`

## widget: ConfirmRestartLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Confirm on restart: | ConfirmRestartLabel | QLabel
- Text: Confirm on restart:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: ConfirmRestartCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: ConfirmRestartCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:162: ctkBooleanMapper* restartMapper = new ctkBooleanMapper(this->ConfirmRestartCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
- Key UI properties: {"checked": "true"}

## widget: ConfirmExitLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Confirm on exit: | ConfirmExitLabel | QLabel
- Text: Confirm on exit:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: ConfirmExitCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: ConfirmExitCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:167: ctkBooleanMapper* exitMapper = new ctkBooleanMapper(this->ConfirmExitCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
- Key UI properties: {"checked": "true"}

## widget: ConfirmSceneCloseLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Confirm on scene close: | ConfirmSceneCloseLabel | QLabel
- Text: Confirm on scene close:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: ConfirmSceneCloseCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: ConfirmSceneCloseCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:172: ctkBooleanMapper* sceneCloseMapper = new ctkBooleanMapper(this->ConfirmSceneCloseCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
- Key UI properties: {"checked": "true"}

## widget: DocumentationBaseURLLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Documentation base URL: | DocumentationBaseURLLabel | QLabel
- Text: Documentation base URL:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: DocumentationBaseURLLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: Specify documentation location.
Available placeholders: {language}, {version}.
Default: https://slicer.readthedocs.io/{language}/{version} | DocumentationBaseURLLineEdit | QLineEdit
- Tooltip: Specify documentation location.
Available placeholders: {language}, {version}.
Default: https://slicer.readthedocs.io/{language}/{version}
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:157: this->DocumentationBaseURLLineEdit->setText("https://slicer.readthedocs.io/en/{version}");`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:178: this->DocumentationBaseURLLineEdit,`

## widget: NumOfRecentlyLoadedFiles

- Confidence: `linked_to_code`
- Widget/action class: `QSpinBox`
- Search text: NumOfRecentlyLoadedFiles | QSpinBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:196: this->NumOfRecentlyLoadedFiles,`

## widget: NumOfRecentlyLoadedFilesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Max. number of 'Recent' menu items: | NumOfRecentlyLoadedFilesLabel | QLabel
- Text: Max. number of 'Recent' menu items:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: SlicerRCFileLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Application startup script: | Python script that is executed after the application is started | SlicerRCFileLabel | QLabel
- Text: Application startup script:
- Tooltip: Python script that is executed after the application is started
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:143: this->SlicerRCFileLabel->setVisible(false);`

## widget: SlicerRCFileValueLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: SlicerRCFileValueLabel | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:133: this->SlicerRCFileValueLabel->setText(slicerrcFileNameVar.toString());`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:140: this->SlicerRCFileValueLabel->setVisible(false);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:144: this->SlicerRCFileValueLabel->setVisible(false);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:243: QString slicerRcFileName = d->SlicerRCFileValueLabel->text();`

## widget: SlicerRCFileOpenButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Open Slicer resource file | SlicerRCFileOpenButton | QPushButton
- Tooltip: Open Slicer resource file
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:134: this->SlicerRCFileOpenButton->setIcon(QIcon(":Icons/Go.png"));`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:135: QObject::connect(this->SlicerRCFileOpenButton, SIGNAL(clicked()), q, SLOT(openSlicerRCFile()));`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:139: this->SlicerRCFileOpenButton->setVisible(false);`
- Connected slots/functions: `openSlicerRCFile`

## widget: DocumentationBaseURLLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Module documentation URL: | DocumentationBaseURLLabel_2 | QLabel
- Text: Module documentation URL:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: ModuleDocumentationURLLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: Specify URL for module documentation.
Available placeholders: {documentationbaseurl}, {lowercasemodulename}.
Default: {documentationbaseurl}/user_guide/modules/{lowercasemodulename}.html | ModuleDocumentationURLLineEdit | QLineEdit
- Tooltip: Specify URL for module documentation.
Available placeholders: {documentationbaseurl}, {lowercasemodulename}.
Default: {documentationbaseurl}/user_guide/modules/{lowercasemodulename}.html
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:158: this->ModuleDocumentationURLLineEdit->setText("{documentationbaseurl}/user_guide/modules/{lowercasemodulename}.html");`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:184: this->ModuleDocumentationURLLineEdit,`

## widget: ApplicationAutoUpdateCheckLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Automatically check for updates: | ApplicationAutoUpdateCheckLabel | QLabel
- Text: Automatically check for updates:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:121: this->ApplicationAutoUpdateCheckLabel->setVisible(applicationUpdateEnabled);`

## widget: ApplicationAutoUpdateCheckCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Periodically check for available application updates | ApplicationAutoUpdateCheckCheckBox | QCheckBox
- Tooltip: Periodically check for available application updates
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:104: q->registerProperty("ApplicationUpdate/AutoUpdateCheck", this->ApplicationAutoUpdateCheckCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:117: QObject::connect(this->ApplicationAutoUpdateCheckCheckBox, SIGNAL(toggled(bool)), app->applicationUpdateManager(), SLOT(setAutoUpdateCheck(bool)));`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:122: this->ApplicationAutoUpdateCheckCheckBox->setVisible(applicationUpdateEnabled);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:292: QSignalBlocker blocker1(d->ApplicationAutoUpdateCheckCheckBox);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:293: d->ApplicationAutoUpdateCheckCheckBox->setChecked(app->applicationUpdateManager()->autoUpdateCheck());`
- Connected slots/functions: `setAutoUpdateCheck`
- Key UI properties: {"checked": "true"}

## widget: ApplicationUpdateServerURLLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Update server URL: | ApplicationUpdateServerURLLabel | QLabel
- Text: Update server URL:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:123: this->ApplicationUpdateServerURLLabel->setVisible(applicationUpdateEnabled);`

## widget: ApplicationUpdateServerURLLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: Address of the server that provides information on latest available application version. | ApplicationUpdateServerURLLineEdit | QLineEdit
- Tooltip: Address of the server that provides information on latest available application version.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:102: this->ApplicationUpdateServerURLLineEdit->setText("https://download.slicer.org");`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:107: this->ApplicationUpdateServerURLLineEdit,`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:124: this->ApplicationUpdateServerURLLineEdit->setVisible(applicationUpdateEnabled);`

## widget: MaxFileNameLengthLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Maximum filename length: | MaxFileNameLengthLabel | QLabel
- Text: Maximum filename length:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`

## widget: MaximumFileNameLengthSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `QSpinBox`
- Search text: Limit the maximum length of filenames. For compatibility with Windows systems, a low value such as 50 is recommended. Set a higher value to allow using longer filenames that match long node names. | MaximumFileNameLengthSpinBox | QSpinBox
- Tooltip: Limit the maximum length of filenames. For compatibility with Windows systems, a low value such as 50 is recommended. Set a higher value to allow using longer filenames that match long node names.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx`, `Base/QTGUI/qSlicerSettingsGeneralPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:205: this->MaximumFileNameLengthSpinBox->setValue(50);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:208: this->MaximumFileNameLengthSpinBox->setValue(1000);`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:212: "ioManager/MaximumFileNameLength", this->MaximumFileNameLengthSpinBox, /*no tr*/ "value", SIGNAL(valueChanged(int)), qSlicerSettingsGeneralPanel::tr("Max. filename length"));`
  - `Base/QTGUI/qSlicerSettingsGeneralPanel.cxx:215: QObject::connect(this->MaximumFileNameLengthSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setMaximumFileNameLength(int)));`
- Connected slots/functions: `setMaximumFileNameLength`
