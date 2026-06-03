# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsExtensionsPanel.ui

- Owner class: `qSlicerSettingsExtensionsPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsExtensionsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsExtensionsPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsExtensionsPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:30: #include "qSlicerSettingsExtensionsPanel.h"`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:31: #include "ui_qSlicerSettingsExtensionsPanel.h"`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:34: // qSlicerSettingsExtensionsPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:37: class qSlicerSettingsExtensionsPanelPrivate : public Ui_qSlicerSettingsExtensionsPanel`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:39: Q_DECLARE_PUBLIC(qSlicerSettingsExtensionsPanel);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:42: qSlicerSettingsExtensionsPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:45: qSlicerSettingsExtensionsPanelPrivate(qSlicerSettingsExtensionsPanel& object);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:50: // qSlicerSettingsExtensionsPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:53: qSlicerSettingsExtensionsPanelPrivate::qSlicerSettingsExtensionsPanelPrivate(qSlicerSettingsExtensionsPanel& object)`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:59: void qSlicerSettingsExtensionsPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:61: Q_Q(qSlicerSettingsExtensionsPanel);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:94: qSlicerSettingsExtensionsPanel::tr("Enable/Disable extensions manager"),`

## widget: ExtensionsManagerEnabledLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable Extensions Manager: | ExtensionsManagerEnabledLabel | QLabel
- Text: Enable Extensions Manager:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: ExtensionsManagerEnabledCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Hide Extensions Manager from the application user interface. Automatic updates are performed even if the Extensions Manager is disabled. | ExtensionsManagerEnabledCheckBox | QCheckBox
- Tooltip: Hide Extensions Manager from the application user interface. Automatic updates are performed even if the Extensions Manager is disabled.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:68: this->ExtensionsManagerEnabledCheckBox->setChecked(true);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:91: this->ExtensionsManagerEnabledCheckBox,`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:127: QObject::connect(this->ExtensionsManagerEnabledCheckBox, SIGNAL(toggled(bool)), q, SLOT(onExtensionsManagerEnabled(bool)));`
- Connected slots/functions: `onExtensionsManagerEnabled`
- Key UI properties: {"checked": "true"}

## widget: AutoUpdateCheckLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Automatically check for updates: | AutoUpdateCheckLabel | QLabel
- Text: Automatically check for updates:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: AutoUpdateCheckCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Periodically check the extensions server for updates | AutoUpdateCheckCheckBox | QCheckBox
- Tooltip: Periodically check the extensions server for updates
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:82: this->AutoUpdateCheckCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:113: "Extensions/AutoUpdateCheck", this->AutoUpdateCheckCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)), qSlicerSettingsExtensionsPanel::tr("Automatic update check"));`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:134: QObject::connect(this->AutoUpdateCheckCheckBox, SIGNAL(toggled(bool)), app->extensionsManagerModel(), SLOT(setAutoUpdateCheck(bool)));`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:175: QSignalBlocker blocker1(d->AutoUpdateCheckCheckBox);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:178: d->AutoUpdateCheckCheckBox->setChecked(app->extensionsManagerModel()->autoUpdateCheck());`
- Connected slots/functions: `setAutoUpdateCheck`
- Key UI properties: {"checked": "false"}

## widget: AutoUpdateInstallLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Automatically install updates: | AutoUpdateInstallLabel | QLabel
- Text: Automatically install updates:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: AutoUpdateInstallCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: If updates are found then install them automatically | AutoUpdateInstallCheckBox | QCheckBox
- Tooltip: If updates are found then install them automatically
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:83: this->AutoUpdateInstallCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:115: "Extensions/AutoUpdateInstall", this->AutoUpdateInstallCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)), qSlicerSettingsExtensionsPanel::tr("Automatic update install"));`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:135: QObject::connect(this->AutoUpdateInstallCheckBox, SIGNAL(toggled(bool)), app->extensionsManagerModel(), SLOT(setAutoUpdateInstall(bool)));`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:176: QSignalBlocker blocker2(d->AutoUpdateInstallCheckBox);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:179: d->AutoUpdateInstallCheckBox->setChecked(app->extensionsManagerModel()->autoUpdateInstall());`
- Connected slots/functions: `setAutoUpdateInstall`
- Key UI properties: {"checked": "false"}

## widget: ExtensionsServerUrlLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Extensions server URL: | ExtensionsServerUrlLabel | QLabel
- Text: Extensions server URL:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: ExtensionsServerUrlLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: ExtensionsServerUrlLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:71: this->ExtensionsServerUrlLineEdit->setText("https://slicer-packages.kitware.com");`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:98: this->ExtensionsServerUrlLineEdit,`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:128: QObject::connect(this->ExtensionsServerUrlLineEdit, SIGNAL(textChanged(QString)), q, SIGNAL(extensionsServerUrlChanged(QString)));`

## widget: ExtensionsFrontendServerUrlLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Extensions frontend server URL: | ExtensionsFrontendServerUrlLabel | QLabel
- Text: Extensions frontend server URL:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: ExtensionsFrontendServerUrlLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: ExtensionsFrontendServerUrlLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:72: this->ExtensionsFrontendServerUrlLineEdit->setText("https://extensions.slicer.org");`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:105: this->ExtensionsFrontendServerUrlLineEdit,`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:129: QObject::connect(this->ExtensionsFrontendServerUrlLineEdit, SIGNAL(textChanged(QString)), q, SIGNAL(extensionsFrontendServerUrlChanged(QString)));`

## widget: ExtensionsInstallPathLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Extensions installation path: | ExtensionsInstallPathLabel | QLabel
- Text: Extensions installation path:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: ExtensionsInstallPathButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDirectoryButton`
- Search text: ExtensionsInstallPathButton | ctkDirectoryButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:78: this->ExtensionsInstallPathButton->setDirectory(app->defaultExtensionsInstallPath());`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:80: this->ExtensionsInstallPathButton->setDisabled(true);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:122: qSlicerRelativePathMapper* relativePathMapper = new qSlicerRelativePathMapper(this->ExtensionsInstallPathButton, "directory", SIGNAL(directoryChanged(QString)));`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:130: QObject::connect(this->ExtensionsInstallPathButton, SIGNAL(directoryChanged(QString)), q, SLOT(onExtensionsPathChanged(QString)));`
- Connected slots/functions: `onExtensionsPathChanged`

## widget: OpenExtensionsManagerPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Open Extensions Manager... | OpenExtensionsManagerPushButton | QPushButton
- Text: Open Extensions Manager...
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:87: this->OpenExtensionsManagerPushButton->setVisible(extensionsManagerEnabled);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:131: QObject::connect(this->OpenExtensionsManagerPushButton, SIGNAL(clicked()), app, SLOT(openExtensionsManagerDialog()));`
- Connected slots/functions: `openExtensionsManagerDialog`

## widget: OpenExtensionsCatalogWebsitePushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Open Extensions Catalog website... | Open Extensions Catalog website in the default web browser. Useful for downloading extension packages for offline use. | OpenExtensionsCatalogWebsitePushButton | QPushButton
- Text: Open Extensions Catalog website...
- Tooltip: Open Extensions Catalog website in the default web browser. Useful for downloading extension packages for offline use.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:132: QObject::connect(this->OpenExtensionsCatalogWebsitePushButton, SIGNAL(clicked()), app, SLOT(openExtensionsCatalogWebsite()));`
- Connected slots/functions: `openExtensionsCatalogWebsite`

## widget: AutoUpdateInstallLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Automatically install dependencies: | AutoUpdateInstallLabel_2 | QLabel
- Text: Automatically install dependencies:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`

## widget: AutoInstallDependenciesCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Automatically install required additional extensions when installing an extension | AutoInstallDependenciesCheckBox | QCheckBox
- Tooltip: Automatically install required additional extensions when installing an extension
- Implementation candidates: `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx`, `Base/QTGUI/qSlicerSettingsExtensionsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:84: this->AutoInstallDependenciesCheckBox->setChecked(true);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:117: this->AutoInstallDependenciesCheckBox,`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:136: QObject::connect(this->AutoInstallDependenciesCheckBox, SIGNAL(toggled(bool)), app->extensionsManagerModel(), SLOT(setAutoInstallDependencies(bool)));`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:177: QSignalBlocker blocker3(d->AutoInstallDependenciesCheckBox);`
  - `Base/QTGUI/qSlicerSettingsExtensionsPanel.cxx:180: d->AutoInstallDependenciesCheckBox->setChecked(app->extensionsManagerModel()->autoInstallDependencies());`
- Connected slots/functions: `setAutoInstallDependencies`
- Key UI properties: {"checked": "true"}
