# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLROIWidget.ui

- Owner class: `qMRMLROIWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLROIWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLROIWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLROIWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:24: #include "qMRMLROIWidget.h"`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:25: #include "ui_qMRMLROIWidget.h"`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:31: class qMRMLROIWidgetPrivate : public Ui_qMRMLROIWidget`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:33: Q_DECLARE_PUBLIC(qMRMLROIWidget);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:36: qMRMLROIWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:39: qMRMLROIWidgetPrivate(qMRMLROIWidget& object);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:45: qMRMLROIWidgetPrivate::qMRMLROIWidgetPrivate(qMRMLROIWidget& object)`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:52: void qMRMLROIWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:54: Q_Q(qMRMLROIWidget);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:65: // qMRMLROIWidget methods`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:68: qMRMLROIWidget::qMRMLROIWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:70: , d_ptr(new qMRMLROIWidgetPrivate(*this))`
- API footprints: `SetInteractiveMode`, `SetVisibility`, `vtkMRMLROINode::SafeDownCast`

## widget: LRRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: L-R Range: | LRRangeLabel | QLabel
- Text: L-R Range:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`

## widget: LRRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: LRRangeWidget | qMRMLRangeWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:58: QObject::connect(this->LRRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(updateROI()));`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:116: d->LRRangeWidget->setTracking(interactive);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:130: d->LRRangeWidget->setValues(bounds[0], bounds[3]);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:139: d->LRRangeWidget->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:163: d->LRRangeWidget->values(bounds[0], bounds[1]);`
- Connected slots/functions: `updateROI`
- API footprints: `EndModify`, `GetInteractiveMode`, `SetRadiusXYZ`, `SetXYZ`, `StartModify`

## widget: PARangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: P-A Range: | PARangeLabel | QLabel
- Text: P-A Range:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`

## widget: PARangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: PARangeWidget | qMRMLRangeWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:59: QObject::connect(this->PARangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(updateROI()));`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:117: d->PARangeWidget->setTracking(interactive);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:131: d->PARangeWidget->setValues(bounds[1], bounds[4]);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:140: d->PARangeWidget->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:164: d->PARangeWidget->values(bounds[2], bounds[3]);`
- Connected slots/functions: `updateROI`
- API footprints: `EndModify`, `GetInteractiveMode`, `SetRadiusXYZ`, `SetXYZ`, `StartModify`

## widget: ISRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: I-S Range: | ISRangeLabel | QLabel
- Text: I-S Range:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`

## widget: ISRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: ISRangeWidget | qMRMLRangeWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:60: QObject::connect(this->ISRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(updateROI()));`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:118: d->ISRangeWidget->setTracking(interactive);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:132: d->ISRangeWidget->setValues(bounds[2], bounds[5]);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:141: d->ISRangeWidget->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:165: d->ISRangeWidget->values(bounds[4], bounds[5]);`
- Connected slots/functions: `updateROI`
- API footprints: `EndModify`, `SetRadiusXYZ`, `SetXYZ`, `StartModify`

## widget: DisplayClippingBoxButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: DisplayClippingBoxButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:56: QObject::connect(this->DisplayClippingBoxButton, SIGNAL(toggled(bool)), q, SLOT(setDisplayClippingBox(bool)));`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:112: d->DisplayClippingBoxButton->setChecked(d->ROINode->GetVisibility());`
- Connected slots/functions: `setDisplayClippingBox`
- API footprints: `GetVisibility`, `SetVisibility`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: DisplayClippingBoxLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Display Clipping box | DisplayClippingBoxLabel | QLabel
- Text: Display Clipping box
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`

## widget: InteractiveModeCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Interactive Mode | InteractiveModeCheckBox | QCheckBox
- Text: Interactive Mode
- Implementation candidates: `Libs/MRML/Widgets/qMRMLROIWidget.cxx`, `Libs/MRML/Widgets/qMRMLROIWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:57: QObject::connect(this->InteractiveModeCheckBox, SIGNAL(toggled(bool)), q, SLOT(setInteractiveMode(bool)));`
  - `Libs/MRML/Widgets/qMRMLROIWidget.cxx:119: d->InteractiveModeCheckBox->setChecked(interactive);`
- Connected slots/functions: `setInteractiveMode`
- API footprints: `SetInteractiveMode`
- Key UI properties: {"checked": "true"}
