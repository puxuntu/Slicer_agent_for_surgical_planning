# Slicer UI Analysis: Modules/Loadable/SubjectHierarchy/Resources/UI/qSlicerSubjectHierarchySettingsPanel.ui

- Owner class: `qSlicerSubjectHierarchySettingsPanel`
- UI file: `Modules/Loadable/SubjectHierarchy/Resources/UI/qSlicerSubjectHierarchySettingsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSubjectHierarchySettingsPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSubjectHierarchySettingsPanel | ctkSettingsPanel
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:28: #include "qSlicerSubjectHierarchySettingsPanel.h"`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:29: #include "ui_qSlicerSubjectHierarchySettingsPanel.h"`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:32: // qSlicerSubjectHierarchySettingsPanelPrivate`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:35: class qSlicerSubjectHierarchySettingsPanelPrivate : public Ui_qSlicerSubjectHierarchySettingsPanel`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:37: Q_DECLARE_PUBLIC(qSlicerSubjectHierarchySettingsPanel);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:40: qSlicerSubjectHierarchySettingsPanel* const q_ptr;`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:43: qSlicerSubjectHierarchySettingsPanelPrivate(qSlicerSubjectHierarchySettingsPanel& object);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:48: // qSlicerSubjectHierarchySettingsPanelPrivate methods`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:51: qSlicerSubjectHierarchySettingsPanelPrivate::qSlicerSubjectHierarchySettingsPanelPrivate(qSlicerSubjectHierarchySettingsPanel& object)`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:57: void qSlicerSubjectHierarchySettingsPanelPrivate::init()`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:59: Q_Q(qSlicerSubjectHierarchySettingsPanel);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:77: qSlicerSubjectHierarchySettingsPanel::tr("Enable/disable automatic subject hierarchy children deletion"),`

## widget: OperationGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: OperationGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: AutoDeleteSubjectHierarchyChildrenEnabledLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Automatically delete subject hierarchy children: | Delete whole branch under the deleted item from subject hierarchy. | AutoDeleteSubjectHierarchyChildrenEnabledLabel | QLabel
- Text: Automatically delete subject hierarchy children:
- Tooltip: Delete whole branch under the deleted item from subject hierarchy.
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: AutoDeleteSubjectHierarchyChildrenEnabledCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text:   | Automatically delete subject hierarchy children for nodes removed from the scene. | AutoDeleteSubjectHierarchyChildrenEnabledCheckBox | QCheckBox
- Text:  
- Tooltip: Automatically delete subject hierarchy children for nodes removed from the scene.
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:64: this->AutoDeleteSubjectHierarchyChildrenEnabledCheckBox->setChecked(false);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:74: this->AutoDeleteSubjectHierarchyChildrenEnabledCheckBox,`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:112: QObject::connect(this->AutoDeleteSubjectHierarchyChildrenEnabledCheckBox, SIGNAL(toggled(bool)), q, SLOT(setAutoDeleteSubjectHierarchyChildrenEnabled(bool)));`
- Connected slots/functions: `setAutoDeleteSubjectHierarchyChildrenEnabled`

## widget: DisplayGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: DisplayGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: StudyDateTagLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text:   Study date: | StudyDateTagLabel | QLabel
- Text:   Study date:
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: PatientBirthDateTagLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text:   Birth date: | PatientBirthDateTagLabel | QLabel
- Text:   Birth date:
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: PatientIDTagCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: PatientIDTagCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:66: this->PatientIDTagCheckBox->setChecked(true);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:81: this->PatientIDTagCheckBox,`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:114: QObject::connect(this->PatientIDTagCheckBox, SIGNAL(toggled(bool)), q, SLOT(setDisplayPatientIDEnabled(bool)));`
- Connected slots/functions: `setDisplayPatientIDEnabled`

## widget: PatientBirthDateTagCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: PatientBirthDateTagCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:67: this->PatientBirthDateTagCheckBox->setChecked(false);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:87: this->PatientBirthDateTagCheckBox,`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:115: QObject::connect(this->PatientBirthDateTagCheckBox, SIGNAL(toggled(bool)), q, SLOT(setDisplayPatientBirthDateEnabled(bool)));`
- Connected slots/functions: `setDisplayPatientBirthDateEnabled`

## widget: StudyIDTagCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: StudyIDTagCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:68: this->StudyIDTagCheckBox->setChecked(false);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:93: this->StudyIDTagCheckBox,`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:116: QObject::connect(this->StudyIDTagCheckBox, SIGNAL(toggled(bool)), q, SLOT(setDisplayStudyIDEnabled(bool)));`
- Connected slots/functions: `setDisplayStudyIDEnabled`

## widget: PatientTagsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Patient tags in item name: | PatientTagsLabel | QLabel
- Text: Patient tags in item name:
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: StudyTagsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Study tags in item name: | StudyTagsLabel | QLabel
- Text: Study tags in item name:
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: StudyDateTagCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: StudyDateTagCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:69: this->StudyDateTagCheckBox->setChecked(true);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:99: this->StudyDateTagCheckBox,`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:117: QObject::connect(this->StudyDateTagCheckBox, SIGNAL(toggled(bool)), q, SLOT(setDisplayStudyDateEnabled(bool)));`
- Connected slots/functions: `setDisplayStudyDateEnabled`

## widget: PatientIDTagLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: ID: | PatientIDTagLabel | QLabel
- Text: ID:
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: StudyIDTagLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: ID: | StudyIDTagLabel | QLabel
- Text: ID:
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: UseTerminologyLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use standard terminology: | If enabled, double-clicking the color column opens the terminology selector. Otherwise the color can be edited via simple color selector. True by default. | UseTerminologyLabel | QLabel
- Text: Use standard terminology:
- Tooltip: If enabled, double-clicking the color column opens the terminology selector. Otherwise the color can be edited via simple color selector. True by default.
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`

## widget: UseTerminologyCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: If enabled, double-clicking the color column opens the terminology selector. Otherwise the color can be edited via simple color selector. True by default. | UseTerminologyCheckBox | QCheckBox
- Tooltip: If enabled, double-clicking the color column opens the terminology selector. Otherwise the color can be edited via simple color selector. True by default.
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:70: this->UseTerminologyCheckBox->setChecked(true);`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:105: this->UseTerminologyCheckBox,`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchySettingsPanel.cxx:118: QObject::connect(this->UseTerminologyCheckBox, SIGNAL(toggled(bool)), q, SLOT(setUseTerminology(bool)));`
- Connected slots/functions: `setUseTerminology`
- Key UI properties: {"checked": "true"}
