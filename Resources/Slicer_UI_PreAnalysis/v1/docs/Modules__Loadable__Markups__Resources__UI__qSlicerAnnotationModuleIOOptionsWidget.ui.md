# Slicer UI Analysis: Modules/Loadable/Markups/Resources/UI/qSlicerAnnotationModuleIOOptionsWidget.ui

- Owner class: `qSlicerAnnotationModuleIOOptionsWidget`
- UI file: `Modules/Loadable/Markups/Resources/UI/qSlicerAnnotationModuleIOOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerAnnotationModuleIOOptionsWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerAnnotationModuleIOOptionsWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:33: #include "ui_qSlicerAnnotationModuleIOOptionsWidget.h"`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:38: , public Ui_qSlicerAnnotationModuleIOOptionsWidget`

## widget: NameLineEdit

- Confidence: `linked_to_slot`
- Widget/action class: `QLineEdit`
- Search text: NameLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:64: connect(d->NameLineEdit, SIGNAL(textChanged(QString)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:86: if (!d->NameLineEdit->text().isEmpty())`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:88: QStringList names = d->NameLineEdit->text().split(';');`
- Connected slots/functions: `updateProperties`

## widget: FiducialRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Fiducial | FiducialRadioButton | QRadioButton
- Text: Fiducial
- Implementation candidates: `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:54: this->FileTypeButtonGroup->addButton(d->FiducialRadioButton);`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:66: connect(d->FiducialRadioButton, SIGNAL(toggled(bool)),`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:74: d->FiducialRadioButton->setChecked(true);`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:99: d->Properties["fiducial"] = d->FiducialRadioButton->isChecked();`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:138: activeButton = d->FiducialRadioButton;`
- Key UI properties: {"checked": "true"}

## widget: RulerRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Ruler | RulerRadioButton | QRadioButton
- Text: Ruler
- Implementation candidates: `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:55: this->FileTypeButtonGroup->addButton(d->RulerRadioButton);`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:68: connect(d->RulerRadioButton, SIGNAL(toggled(bool)),`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:100: d->Properties["ruler"] = d->RulerRadioButton->isChecked();`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:142: activeButton = d->RulerRadioButton;`

## widget: ROIRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: ROI | ROIRadioButton | QRadioButton
- Text: ROI
- Implementation candidates: `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:56: this->FileTypeButtonGroup->addButton(d->ROIRadioButton);`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:70: connect(d->ROIRadioButton, SIGNAL(toggled(bool)),`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:101: d->Properties["roi"] = d->ROIRadioButton->isChecked();`
  - `Modules/Loadable/Markups/qSlicerAnnotationsIOOptionsWidget.cxx:146: activeButton = d->ROIRadioButton;`
