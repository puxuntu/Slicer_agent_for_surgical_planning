# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsPlaneWidget.ui

- Owner class: `qMRMLMarkupsPlaneWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsPlaneWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsPlaneWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsPlaneWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:23: #include "qMRMLMarkupsPlaneWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:24: #include "ui_qMRMLMarkupsPlaneWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:34: class qMRMLMarkupsPlaneWidgetPrivate : public Ui_qMRMLMarkupsPlaneWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:37: qMRMLMarkupsPlaneWidgetPrivate(qMRMLMarkupsPlaneWidget& object);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:38: void setupUi(qMRMLMarkupsPlaneWidget* widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:43: qMRMLMarkupsPlaneWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:46: Q_DECLARE_PUBLIC(qMRMLMarkupsPlaneWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:50: qMRMLMarkupsPlaneWidgetPrivate::qMRMLMarkupsPlaneWidgetPrivate(qMRMLMarkupsPlaneWidget& widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:56: void qMRMLMarkupsPlaneWidgetPrivate::setupUi(qMRMLMarkupsPlaneWidget* widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:58: Q_Q(qMRMLMarkupsPlaneWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:60: this->Ui_qMRMLMarkupsPlaneWidget::setupUi(widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:86: QObject::connect(this->normalVisibilityCheckBox, &QCheckBox::checkStateChanged, q, &qMRMLMarkupsPlaneWidget::onNormalVisibilityCheckBoxChanged);`
- Connected slots/functions: `checkStateChanged`, `onNormalVisibilityCheckBoxChanged`
- API footprints: `GetDisplayNode`, `SetNormalVisibility`, `vtkMRMLMarkupsPlaneDisplayNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::PlaneType3Points`, `vtkMRMLMarkupsPlaneNode::PlaneTypePlaneFit`, `vtkMRMLMarkupsPlaneNode::PlaneTypePointNormal`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`

## widget: planeSettingsCollapseButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Plane settings | planeSettingsCollapseButton | ctkCollapsibleButton
- Text: Plane settings
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: label_10

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Type | label_10 | QLabel
- Text: Type
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: planeTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: planeTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:62: this->planeTypeComboBox->clear();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:65: this->planeTypeComboBox->addItem(this->planeTypeName(planeType), planeType);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:74: QObject::connect(this->planeTypeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onPlaneTypeIndexChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:161: bool wasBlocked = d->planeTypeComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:162: d->planeTypeComboBox->setCurrentIndex(d->planeTypeComboBox->findData(planeNode->GetPlaneType()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:163: d->planeTypeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:225: planeNode->SetPlaneType(d->planeTypeComboBox->currentData().toInt());`
- Connected slots/functions: `onPlaneTypeIndexChanged`
- API footprints: `GetPlaneType`, `SetPlaneType`, `vtkMRMLMarkupsPlaneNode::PlaneType_Last`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Size mode: | label | QLabel
- Text: Size mode:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:740: QTableWidgetItem* labelItem = new QTableWidgetItem(QString::fromStdString(controlPointLabel));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:763: d->MarkupsControlPointsTableWidget->setItem(i, CONTROL_POINT_LABEL_COLUMN, labelItem);`
- API footprints: `GetNthControlPointPosition`

## widget: planeSizeModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: planeSizeModeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:68: this->planeSizeModeComboBox->clear();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:71: this->planeSizeModeComboBox->addItem(vtkMRMLMarkupsPlaneNode::GetSizeModeAsString(sizeMode), sizeMode);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:75: QObject::connect(this->planeSizeModeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onPlaneSizeModeIndexChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:165: wasBlocked = d->planeSizeModeComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:166: d->planeSizeModeComboBox->setCurrentIndex(d->planeSizeModeComboBox->findData(planeNode->GetSizeMode()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:167: d->planeSizeModeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:237: planeNode->SetSizeMode(d->planeSizeModeComboBox->currentData().toInt());`
- Connected slots/functions: `onPlaneSizeModeIndexChanged`
- API footprints: `GetSize`, `GetSizeMode`, `SetSizeMode`, `vtkMRMLMarkupsPlaneNode::GetSizeModeAsString`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeMode_Last`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Size: | label_2 | QLabel
- Text: Size:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X: | label_3 | QLabel
- Text: X:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: sizeXSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: sizeXSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:77: QObject::connect(this->sizeXSpinBox, SIGNAL(valueChanged(double)), q, SLOT(onPlaneSizeSpinBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:171: wasBlocked = d->sizeXSpinBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:172: d->sizeXSpinBox->setValue(size[0]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:173: d->sizeXSpinBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:174: d->sizeXSpinBox->setEnabled(planeNode->GetSizeMode() != vtkMRMLMarkupsPlaneNode::SizeModeAuto);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:249: planeNode->SetSize(d->sizeXSpinBox->value(), d->sizeYSpinBox->value());`
- Connected slots/functions: `onPlaneSizeSpinBoxChanged`
- API footprints: `GetSize`, `GetSizeMode`, `SetSize`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeModeAuto`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y: | label_4 | QLabel
- Text: Y:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: sizeYSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: sizeYSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:78: QObject::connect(this->sizeYSpinBox, SIGNAL(valueChanged(double)), q, SLOT(onPlaneSizeSpinBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:176: wasBlocked = d->sizeYSpinBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:177: d->sizeYSpinBox->setValue(size[1]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:178: d->sizeYSpinBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:179: d->sizeYSpinBox->setEnabled(planeNode->GetSizeMode() != vtkMRMLMarkupsPlaneNode::SizeModeAuto);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:249: planeNode->SetSize(d->sizeXSpinBox->value(), d->sizeYSpinBox->value());`
- Connected slots/functions: `onPlaneSizeSpinBoxChanged`
- API footprints: `GetPlaneBounds`, `GetSizeMode`, `SetSize`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeModeAuto`

## widget: label_7

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Bounds: | label_7 | QLabel
- Text: Bounds:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: label_9

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X max: | label_9 | QLabel
- Text: X max:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: boundsXMinSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: boundsXMinSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:80: QObject::connect(this->boundsXMinSpinBox, SIGNAL(valueChanged(double)), q, SLOT(onPlaneBoundsSpinBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:183: wasBlocked = d->boundsXMinSpinBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:184: d->boundsXMinSpinBox->setValue(bounds[0]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:185: d->boundsXMinSpinBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:186: d->boundsXMinSpinBox->setEnabled(planeNode->GetSizeMode() != vtkMRMLMarkupsPlaneNode::SizeModeAuto);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:261: double xMin = std::min(d->boundsXMinSpinBox->value(), d->boundsXMaxSpinBox->value());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:262: double xMax = std::max(d->boundsXMinSpinBox->value(), d->boundsXMaxSpinBox->value());`
- Connected slots/functions: `onPlaneBoundsSpinBoxChanged`
- API footprints: `GetPlaneBounds`, `GetSizeMode`, `SetPlaneBounds`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeModeAuto`

## widget: boundsXMaxSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: boundsXMaxSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:81: QObject::connect(this->boundsXMaxSpinBox, SIGNAL(valueChanged(double)), q, SLOT(onPlaneBoundsSpinBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:188: wasBlocked = d->boundsXMaxSpinBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:189: d->boundsXMaxSpinBox->setValue(bounds[1]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:190: d->boundsXMaxSpinBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:191: d->boundsXMaxSpinBox->setEnabled(planeNode->GetSizeMode() != vtkMRMLMarkupsPlaneNode::SizeModeAuto);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:261: double xMin = std::min(d->boundsXMinSpinBox->value(), d->boundsXMaxSpinBox->value());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:262: double xMax = std::max(d->boundsXMinSpinBox->value(), d->boundsXMaxSpinBox->value());`
- Connected slots/functions: `onPlaneBoundsSpinBoxChanged`
- API footprints: `GetSizeMode`, `SetPlaneBounds`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeModeAuto`

## widget: label_8

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X min: | label_8 | QLabel
- Text: X min:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: label_12

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y min: | label_12 | QLabel
- Text: Y min:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: boundsYMinSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: boundsYMinSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:82: QObject::connect(this->boundsYMinSpinBox, SIGNAL(valueChanged(double)), q, SLOT(onPlaneBoundsSpinBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:193: wasBlocked = d->boundsYMinSpinBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:194: d->boundsYMinSpinBox->setValue(bounds[2]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:195: d->boundsYMinSpinBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:196: d->boundsYMinSpinBox->setEnabled(planeNode->GetSizeMode() != vtkMRMLMarkupsPlaneNode::SizeModeAuto);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:263: double yMin = std::min(d->boundsYMinSpinBox->value(), d->boundsYMaxSpinBox->value());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:264: double yMax = std::max(d->boundsYMinSpinBox->value(), d->boundsYMaxSpinBox->value());`
- Connected slots/functions: `onPlaneBoundsSpinBoxChanged`
- API footprints: `GetSizeMode`, `SetPlaneBounds`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeModeAuto`

## widget: boundsYMaxSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: boundsYMaxSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:83: QObject::connect(this->boundsYMaxSpinBox, SIGNAL(valueChanged(double)), q, SLOT(onPlaneBoundsSpinBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:198: wasBlocked = d->boundsYMaxSpinBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:199: d->boundsYMaxSpinBox->setValue(bounds[3]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:200: d->boundsYMaxSpinBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:201: d->boundsYMaxSpinBox->setEnabled(planeNode->GetSizeMode() != vtkMRMLMarkupsPlaneNode::SizeModeAuto);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:263: double yMin = std::min(d->boundsYMinSpinBox->value(), d->boundsYMaxSpinBox->value());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:264: double yMax = std::max(d->boundsYMinSpinBox->value(), d->boundsYMaxSpinBox->value());`
- Connected slots/functions: `onPlaneBoundsSpinBoxChanged`
- API footprints: `GetDisplayNode`, `GetSizeMode`, `SetPlaneBounds`, `vtkMRMLMarkupsPlaneDisplayNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SizeModeAuto`

## widget: label_13

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y max: | label_13 | QLabel
- Text: Y max:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Normal: | label_5 | QLabel
- Text: Normal:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: normalVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: normalVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:86: QObject::connect(this->normalVisibilityCheckBox, &QCheckBox::checkStateChanged, q, &qMRMLMarkupsPlaneWidget::onNormalVisibilityCheckBoxChanged);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:88: QObject::connect(this->normalVisibilityCheckBox, SIGNAL(stateChanged(int)), q, SLOT(onNormalVisibilityCheckBoxChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:206: wasBlocked = d->normalVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:207: d->normalVisibilityCheckBox->setChecked(planeDisplayNode->GetNormalVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:208: d->normalVisibilityCheckBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:284: displayNode->SetNormalVisibility(d->normalVisibilityCheckBox->checkState() == Qt::Checked);`
- Connected slots/functions: `checkStateChanged`, `onNormalVisibilityCheckBoxChanged`
- API footprints: `GetDisplayNode`, `GetNormalVisibility`, `SetNormalVisibility`, `vtkMRMLMarkupsPlaneDisplayNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`

## widget: label_6

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | label_6 | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`

## widget: normalOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: normalOpacitySlider | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:90: QObject::connect(this->normalOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(onNormalOpacitySliderChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:210: wasBlocked = d->normalOpacitySlider->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:211: d->normalOpacitySlider->setValue(planeDisplayNode->GetNormalOpacity());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:212: d->normalOpacitySlider->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:303: displayNode->SetNormalOpacity(d->normalOpacitySlider->value());`
- Connected slots/functions: `onNormalOpacitySliderChanged`
- API footprints: `GetDisplayNode`, `GetNormalOpacity`, `SetNormalOpacity`, `vtkMRMLMarkupsPlaneDisplayNode::SafeDownCast`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`

## widget: flipPlaneNormalButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Flip normal | Reverse direction of the plane normal | flipPlaneNormalButton | QPushButton
- Text: Flip normal
- Tooltip: Reverse direction of the plane normal
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsPlaneWidget.cxx:91: QObject::connect(this->flipPlaneNormalButton, SIGNAL(clicked()), q, SLOT(onFlipPlaneNormalButtonClicked()));`
- Connected slots/functions: `onFlipPlaneNormalButtonClicked`
- API footprints: `FlipNormal`, `vtkMRMLMarkupsPlaneNode::SafeDownCast`
