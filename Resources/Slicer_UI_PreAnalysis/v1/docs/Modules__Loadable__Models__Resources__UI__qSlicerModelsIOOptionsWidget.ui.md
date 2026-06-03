# Slicer UI Analysis: Modules/Loadable/Models/Resources/UI/qSlicerModelsIOOptionsWidget.ui

- Owner class: `qSlicerModelsIOOptionsWidget`
- UI file: `Modules/Loadable/Models/Resources/UI/qSlicerModelsIOOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerModelsIOOptionsWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerModelsIOOptionsWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:26: #include "qSlicerModelsIOOptionsWidget.h"`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:27: #include "ui_qSlicerModelsIOOptionsWidget.h"`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:34: class qSlicerModelsIOOptionsWidgetPrivate`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:36: , public Ui_qSlicerModelsIOOptionsWidget`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:42: qSlicerModelsIOOptionsWidget::qSlicerModelsIOOptionsWidget(QWidget* parentWidget)`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:43: : Superclass(new qSlicerModelsIOOptionsWidgetPrivate, parentWidget)`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:45: Q_D(qSlicerModelsIOOptionsWidget);`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:52: qSlicerModelsIOOptionsWidget::~qSlicerModelsIOOptionsWidget() = default;`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:55: void qSlicerModelsIOOptionsWidget::updateProperties()`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:57: Q_D(qSlicerModelsIOOptionsWidget);`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.h:21: #ifndef __qSlicerModelsIOOptionsWidget_h`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.h:22: #define __qSlicerModelsIOOptionsWidget_h`
- API footprints: `vtkMRMLStorageNode::GetCoordinateSystemTypeFromString`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Coordinate system: | label | QLabel
- Text: Coordinate system:
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.h`

## widget: coordinateSystemComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Use LPS (left-posterior-superior) for better compatibility with most software (this is the default). Use RAS (right-anterior-superior) for better compatibility with earlier Slicer versions. If coordinate system is defined in the file then that is used and this choice is ignored. | coordinateSystemComboBox | QComboBox
- Tooltip: Use LPS (left-posterior-superior) for better compatibility with most software (this is the default). Use RAS (right-anterior-superior) for better compatibility with earlier Slicer versions. If coordinate system is defined in the file then that is used and this choice is ignored.
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:48: connect(d->coordinateSystemComboBox, SIGNAL(currentIndexChanged(int)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Models/qSlicerModelsIOOptionsWidget.cxx:58: d->Properties["coordinateSystem"] = vtkMRMLStorageNode::GetCoordinateSystemTypeFromString(d->coordinateSystemComboBox->currentText().toLatin1().constData());`
- Connected slots/functions: `updateProperties`
- API footprints: `vtkMRMLStorageNode::GetCoordinateSystemTypeFromString`
