# Slicer UI Analysis: Modules/Loadable/Segmentations/Resources/UI/qSlicerSegmentationsIOOptionsWidget.ui

- Owner class: `qSlicerSegmentationsIOOptionsWidget`
- UI file: `Modules/Loadable/Segmentations/Resources/UI/qSlicerSegmentationsIOOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSegmentationsIOOptionsWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSegmentationsIOOptionsWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:37: #include "qSlicerSegmentationsIOOptionsWidget.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:38: #include "ui_qSlicerSegmentationsIOOptionsWidget.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:41: class qSlicerSegmentationsIOOptionsWidgetPrivate`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:43: , public Ui_qSlicerSegmentationsIOOptionsWidget`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:49: qSlicerSegmentationsIOOptionsWidget::qSlicerSegmentationsIOOptionsWidget(QWidget* parentWidget)`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:50: : qSlicerIOOptionsWidget(new qSlicerSegmentationsIOOptionsWidgetPrivate, parentWidget)`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:52: Q_D(qSlicerSegmentationsIOOptionsWidget);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:70: qSlicerSegmentationsIOOptionsWidget::~qSlicerSegmentationsIOOptionsWidget() = default;`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:73: void qSlicerSegmentationsIOOptionsWidget::updateProperties()`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:75: Q_D(qSlicerSegmentationsIOOptionsWidget);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.h:21: #ifndef __qSlicerSegmentationsIOOptionsWidget_h`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.h:22: #define __qSlicerSegmentationsIOOptionsWidget_h`

## widget: AutoOpacitiesCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Automatic Segment Opacities | Automatically set opacities of the segments based on which contains which, so that no segment obscures another | AutoOpacitiesCheckBox | QCheckBox
- Text: Automatic Segment Opacities
- Tooltip: Automatically set opacities of the segments based on which contains which, so that no segment obscures another
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:61: d->AutoOpacitiesCheckBox->setChecked(autoOpacities);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:65: connect(d->AutoOpacitiesCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:77: d->Properties["autoOpacities"] = d->AutoOpacitiesCheckBox->isChecked();`
- Connected slots/functions: `updateProperties`
- Key UI properties: {"checked": "true"}

## widget: ColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color node: | ColorLabel | QLabel
- Text: Color node:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.h`

## widget: ColorNodeSelector

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: Color table node used to display this volume. | ColorNodeSelector | qMRMLColorTableComboBox
- Tooltip: Color table node used to display this volume.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:66: connect(d->ColorNodeSelector, SIGNAL(currentNodeIDChanged(QString)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsIOOptionsWidget.cxx:78: d->Properties["colorNodeID"] = d->ColorNodeSelector->currentNodeID();`
- Connected slots/functions: `updateProperties`
- Key UI properties: {"nodeTypes": ["vtkMRMLColorTableNode"]}
