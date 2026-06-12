# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsROIWidget.ui

- Owner class: `qMRMLMarkupsROIWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsROIWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsROIWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsROIWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:24: #include "qMRMLMarkupsROIWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:25: #include "ui_qMRMLMarkupsROIWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:41: class qMRMLMarkupsROIWidgetPrivate : public Ui_qMRMLMarkupsROIWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:45: qMRMLMarkupsROIWidgetPrivate(qMRMLMarkupsROIWidget& widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:46: void setupUi(qMRMLMarkupsROIWidget* widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:52: qMRMLMarkupsROIWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:55: Q_DECLARE_PUBLIC(qMRMLMarkupsROIWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:59: qMRMLMarkupsROIWidgetPrivate::qMRMLMarkupsROIWidgetPrivate(qMRMLMarkupsROIWidget& widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:67: void qMRMLMarkupsROIWidgetPrivate::setupUi(qMRMLMarkupsROIWidget* widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:69: Q_Q(qMRMLMarkupsROIWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:71: this->Ui_qMRMLMarkupsROIWidget::setupUi(widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:90: // qMRMLMarkupsROIWidget methods`
- API footprints: `vtkMRMLMarkupsROINode::SafeDownCast`

## widget: roiSettingsCollapseButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: ROI Settings | roiSettingsCollapseButton | ctkCollapsibleButton
- Text: ROI Settings
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`

## widget: label_10

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: ROI type: | label_10 | QLabel
- Text: ROI type:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`

## widget: roiTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: roiTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:73: this->roiTypeComboBox->clear();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:76: this->roiTypeComboBox->addItem(vtkMRMLMarkupsROINode::GetROITypeAsString(roiType), roiType);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:79: QObject::connect(this->roiTypeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onROITypeParameterChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:257: roiNode->SetROIType(d->roiTypeComboBox->currentData().toInt());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:340: bool wasBlocked = d->roiTypeComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:341: d->roiTypeComboBox->setCurrentIndex(d->roiTypeComboBox->findData(roiNode->GetROIType()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:342: d->roiTypeComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onROITypeParameterChanged`
- API footprints: `GetROIType`, `SetROIType`, `vtkMRMLMarkupsROINode::GetROITypeAsString`, `vtkMRMLMarkupsROINode::ROIType_Last`, `vtkMRMLMarkupsROINode::SafeDownCast`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Inside out: | label | QLabel
- Text: Inside out:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:740: QTableWidgetItem* labelItem = new QTableWidgetItem(QString::fromStdString(controlPointLabel));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:763: d->MarkupsControlPointsTableWidget->setItem(i, CONTROL_POINT_LABEL_COLUMN, labelItem);`
- API footprints: `GetNthControlPointPosition`

## widget: insideOutCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: insideOutCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:80: QObject::connect(this->insideOutCheckBox, SIGNAL(toggled(bool)), q, SLOT(setInsideOut(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:344: wasBlocked = d->insideOutCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:345: d->insideOutCheckBox->setChecked(roiNode->GetInsideOut());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:346: d->insideOutCheckBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setInsideOut`
- API footprints: `GetInsideOut`, `SetInsideOut`, `vtkMRMLMarkupsROINode::SafeDownCast`

## widget: LRRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: L-R Range: | LRRangeLabel | QLabel
- Text: L-R Range:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`

## widget: LRRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: LRRangeWidget | qMRMLRangeWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:83: QObject::connect(this->LRRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(updateROI()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:127: d->LRRangeWidget->setRange(minLR, maxLR);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:206: d->LRRangeWidget->values(bounds[0], bounds[1]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:308: d->LRRangeWidget->setTracking(interactive);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:329: d->LRRangeWidget->setRange(qMin(bounds[0], d->LRRangeWidget->minimum()), qMax(bounds[3], d->LRRangeWidget->maximum()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:334: d->LRRangeWidget->setValues(bounds[0], bounds[3]);`
- Connected slots/functions: `updateROI`
- API footprints: `SetRadiusXYZ`, `SetXYZ`, `vtkMRMLMarkupsROINode::SafeDownCast`

## widget: PARangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: P-A Range: | PARangeLabel | QLabel
- Text: P-A Range:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`

## widget: PARangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: PARangeWidget | qMRMLRangeWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:84: QObject::connect(this->PARangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(updateROI()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:128: d->PARangeWidget->setRange(minPA, maxPA);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:207: d->PARangeWidget->values(bounds[2], bounds[3]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:309: d->PARangeWidget->setTracking(interactive);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:330: d->PARangeWidget->setRange(qMin(bounds[1], d->PARangeWidget->minimum()), qMax(bounds[4], d->PARangeWidget->maximum()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:335: d->PARangeWidget->setValues(bounds[1], bounds[4]);`
- Connected slots/functions: `updateROI`
- API footprints: `SetRadiusXYZ`, `SetXYZ`, `vtkMRMLMarkupsROINode::SafeDownCast`

## widget: ISRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: ISRangeWidget | qMRMLRangeWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:85: QObject::connect(this->ISRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(updateROI()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:129: d->ISRangeWidget->setRange(minIS, maxIS);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:193: // ISRangeWidget->setValues()).`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:208: d->ISRangeWidget->values(bounds[4], bounds[5]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:310: d->ISRangeWidget->setTracking(interactive);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:331: d->ISRangeWidget->setRange(qMin(bounds[2], d->ISRangeWidget->minimum()), qMax(bounds[5], d->ISRangeWidget->maximum()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:336: d->ISRangeWidget->setValues(bounds[2], bounds[5]);`
- Connected slots/functions: `updateROI`
- API footprints: `SetRadiusXYZ`, `SetXYZ`, `vtkMRMLMarkupsROINode::SafeDownCast`

## widget: ISRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: I-S Range: | ISRangeLabel | QLabel
- Text: I-S Range:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`

## widget: DisplayClippingBoxButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: DisplayClippingBoxButton | QToolButton
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:81: QObject::connect(this->DisplayClippingBoxButton, SIGNAL(toggled(bool)), q, SLOT(setDisplayClippingBox(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:242: d->DisplayClippingBoxButton->setChecked(roiNode->GetDisplayVisibility());`
- Connected slots/functions: `setDisplayClippingBox`
- API footprints: `EndModify`, `GetDisplayVisibility`, `GetNthDisplayNode`, `GetNumberOfDisplayNodes`, `SetDisplayVisibility`, `StartModify`, `vtkMRMLMarkupsROINode::SafeDownCast`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: DisplayClippingBoxLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Display ROI | DisplayClippingBoxLabel | QLabel
- Text: Display ROI
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`

## widget: InteractiveModeCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Interactive Mode | InteractiveModeCheckBox | QCheckBox
- Text: Interactive Mode
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:82: QObject::connect(this->InteractiveModeCheckBox, SIGNAL(toggled(bool)), q, SLOT(setInteractiveMode(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsROIWidget.cxx:311: d->InteractiveModeCheckBox->setChecked(interactive);`
- Connected slots/functions: `setInteractiveMode`
- API footprints: `CreateDefaultDisplayNodes`, `GetDisplayNode`, `SetHandlesInteractive`, `vtkMRMLMarkupsROIDisplayNode::SafeDownCast`, `vtkMRMLMarkupsROINode::SafeDownCast`
- Key UI properties: {"checked": "true"}
