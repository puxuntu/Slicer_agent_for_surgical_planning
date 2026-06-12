# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsAngleMeasurementsWidget.ui

- Owner class: `qMRMLMarkupsAngleMeasurementsWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsAngleMeasurementsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsAngleMeasurementsWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsAngleMeasurementsWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:21: #include "qMRMLMarkupsAngleMeasurementsWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:22: #include "ui_qMRMLMarkupsAngleMeasurementsWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:32: class qMRMLMarkupsAngleMeasurementsWidget;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:35: class qMRMLMarkupsAngleMeasurementsWidgetPrivate : public Ui_qMRMLMarkupsAngleMeasurementsWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:39: qMRMLMarkupsAngleMeasurementsWidgetPrivate(qMRMLMarkupsAngleMeasurementsWidget& widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:40: void setupUi(qMRMLMarkupsAngleMeasurementsWidget* widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:43: qMRMLMarkupsAngleMeasurementsWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:46: Q_DECLARE_PUBLIC(qMRMLMarkupsAngleMeasurementsWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:50: qMRMLMarkupsAngleMeasurementsWidgetPrivate::qMRMLMarkupsAngleMeasurementsWidgetPrivate(qMRMLMarkupsAngleMeasurementsWidget& widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:56: void qMRMLMarkupsAngleMeasurementsWidgetPrivate::setupUi(qMRMLMarkupsAngleMeasurementsWidget* widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:58: Q_Q(qMRMLMarkupsAngleMeasurementsWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:60: this->Ui_qMRMLMarkupsAngleMeasurementsWidget::setupUi(widget);`
- API footprints: `vtkMRMLMarkupsAngleNode::SafeDownCast`

## widget: angleMeasurementModeCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Angle Settings | angleMeasurementModeCollapsibleButton | ctkCollapsibleButton
- Text: Angle Settings
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.h`
- Key UI properties: {"checked": "false"}

## widget: label_8

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Measurement mode: | label_8 | QLabel
- Text: Measurement mode:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.h`

## widget: angleMeasurementModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: <html><head/><body><p>- Minimal: minimal non-oriented angle, between [0..180)<br/>- Oriented signed: oriented angle [-180..180), using rotation axis in right-hand rule<br/>- Oriented positive: oriented angle [0..360), using rotation axis in right-hand rule</p></body></html> | angleMeasurementModeComboBox | QComboBox
- Tooltip: <html><head/><body><p>- Minimal: minimal non-oriented angle, between [0..180)<br/>- Oriented signed: oriented angle [-180..180), using rotation axis in right-hand rule<br/>- Oriented positive: oriented angle [0..360), using rotation axis in right-hand rule</p></body></html>
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:62: QObject::connect(this->angleMeasurementModeComboBox, SIGNAL(currentIndexChanged(int)), q_ptr, SLOT(onAngleMeasurementModeChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:103: d_ptr->angleMeasurementModeComboBox->setCurrentIndex(angleNode->GetAngleMeasurementMode());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:116: markupsAngleNode->SetAngleMeasurementMode(d_ptr->angleMeasurementModeComboBox->currentIndex());`
- Connected slots/functions: `onAngleMeasurementModeChanged`
- API footprints: `GetAngleMeasurementMode`, `SetAngleMeasurementMode`, `vtkMRMLMarkupsAngleNode::Minimal`, `vtkMRMLMarkupsAngleNode::SafeDownCast`

## widget: label_9

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Rotation axis: | label_9 | QLabel
- Text: Rotation axis:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.h`

## widget: rotationAxisCoordinatesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: Rotation axis direction in RAS coordinate system. Used for defining direction in oriented angle modes using right hand rule. | rotationAxisCoordinatesWidget | qMRMLCoordinatesWidget
- Tooltip: Rotation axis direction in RAS coordinate system. Used for defining direction in oriented angle modes using right hand rule.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:63: QObject::connect(this->rotationAxisCoordinatesWidget, SIGNAL(coordinatesChanged(double*)), q_ptr, SLOT(onRotationAxisChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:99: bool wasBlocked = d_ptr->rotationAxisCoordinatesWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:100: d_ptr->rotationAxisCoordinatesWidget->setCoordinates(axisVector);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:101: d_ptr->rotationAxisCoordinatesWidget->setEnabled(angleNode->GetAngleMeasurementMode() != vtkMRMLMarkupsAngleNode::Minimal);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:102: d_ptr->rotationAxisCoordinatesWidget->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsAngleMeasurementsWidget.cxx:127: markupsAngleNode->SetOrientationRotationAxis(const_cast<double*>(d_ptr->rotationAxisCoordinatesWidget->coordinates()));`
- Connected slots/functions: `onRotationAxisChanged`
- API footprints: `GetAngleMeasurementMode`, `GetOrientationRotationAxis`, `SetOrientationRotationAxis`, `vtkMRMLMarkupsAngleNode::Minimal`, `vtkMRMLMarkupsAngleNode::SafeDownCast`
