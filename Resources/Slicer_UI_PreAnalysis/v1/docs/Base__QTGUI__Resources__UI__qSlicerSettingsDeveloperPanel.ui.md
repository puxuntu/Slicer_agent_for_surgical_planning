# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsDeveloperPanel.ui

- Owner class: `qSlicerSettingsDeveloperPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsDeveloperPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsDeveloperPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsDeveloperPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:28: #include "qSlicerSettingsDeveloperPanel.h"`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:29: #include "ui_qSlicerSettingsDeveloperPanel.h"`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:32: // qSlicerSettingsDeveloperPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:35: class qSlicerSettingsDeveloperPanelPrivate : public Ui_qSlicerSettingsDeveloperPanel`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:37: Q_DECLARE_PUBLIC(qSlicerSettingsDeveloperPanel);`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:40: qSlicerSettingsDeveloperPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:43: qSlicerSettingsDeveloperPanelPrivate(qSlicerSettingsDeveloperPanel& object);`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:48: // qSlicerSettingsDeveloperPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:51: qSlicerSettingsDeveloperPanelPrivate::qSlicerSettingsDeveloperPanelPrivate(qSlicerSettingsDeveloperPanel& object)`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:57: void qSlicerSettingsDeveloperPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:59: Q_Q(qSlicerSettingsDeveloperPanel);`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:77: qSlicerSettingsDeveloperPanel::tr("Enable/Disable developer mode"),`

## widget: DeveloperModeEnabledLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable developer mode: | DeveloperModeEnabledLabel | QLabel
- Text: Enable developer mode:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`

## widget: DeveloperModeEnabledCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Run the application in developer mode: testing modules are shown in the module list, Reload&Test section is shown in scripted modules user interface, CLI module input and output files are not deleted after module execution | DeveloperModeEnabledCheckBox | QCheckBox
- Tooltip: Run the application in developer mode: testing modules are shown in the module list, Reload&Test section is shown in scripted modules user interface, CLI module input and output files are not deleted after module execution
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:64: this->DeveloperModeEnabledCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:74: this->DeveloperModeEnabledCheckBox,`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:101: QObject::connect(this->DeveloperModeEnabledCheckBox, SIGNAL(toggled(bool)), q, SLOT(enableDeveloperMode(bool)));`
- Connected slots/functions: `enableDeveloperMode`

## widget: QtTestingEnabledLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Enable QtTesting: | QtTestingEnabledLabel | QLabel
- Text: Enable QtTesting:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:69: this->QtTestingEnabledLabel->hide();`

## widget: QtTestingEnabledCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: QtTestingEnabledCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:66: this->QtTestingEnabledCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:68: this->QtTestingEnabledCheckBox->hide();`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:94: this->QtTestingEnabledCheckBox,`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:103: QObject::connect(this->QtTestingEnabledCheckBox, SIGNAL(toggled(bool)), q, SLOT(enableQtTesting(bool)));`
- Connected slots/functions: `enableQtTesting`

## widget: SelfTestMessageDelayLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Self-test message delay: | SelfTestMessageDelayLabel | QLabel
- Text: Self-test message delay:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`

## widget: SelfTestMessageDelaySlider

- Confidence: `linked_to_code`
- Widget/action class: `ctkSliderWidget`
- Search text: Time to wait before resuming self-test execution and hiding messages displayed to the user | SelfTestMessageDelaySlider | ctkSliderWidget
- Tooltip: Time to wait before resuming self-test execution and hiding messages displayed to the user
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:65: this->SelfTestMessageDelaySlider->setValue(750);`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:88: this->SelfTestMessageDelaySlider,`

## widget: QtDesignerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Qt Designer: | QtDesignerLabel | QLabel
- Text: Qt Designer:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`

## widget: QtDesignerButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: launch | QtDesignerButton | QPushButton
- Text: launch
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:105: QObject::connect(this->QtDesignerButton, SIGNAL(clicked()), qSlicerApplication::application(), SLOT(launchDesigner()));`
- Connected slots/functions: `launchDesigner`

## widget: DeveloperModeEnabledLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Preserve CLI module data files: | DeveloperModeEnabledLabel_2 | QLabel
- Text: Preserve CLI module data files:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`

## widget: PreserveCLIModuleDataFilesCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Preserve input and data files created during CLI module execution | PreserveCLIModuleDataFilesCheckBox | QCheckBox
- Tooltip: Preserve input and data files created during CLI module execution
- Implementation candidates: `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx`, `Base/QTGUI/qSlicerSettingsDeveloperPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:81: this->PreserveCLIModuleDataFilesCheckBox,`
  - `Base/QTGUI/qSlicerSettingsDeveloperPanel.cxx:102: QObject::connect(this->PreserveCLIModuleDataFilesCheckBox, SIGNAL(toggled(bool)), q, SLOT(preserveCLIModuleDataFiles(bool)));`
- Connected slots/functions: `preserveCLIModuleDataFiles`
