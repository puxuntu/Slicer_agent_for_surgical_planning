# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLVolumeThresholdWidget.ui

- Owner class: `qMRMLVolumeThresholdWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLVolumeThresholdWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLVolumeThresholdWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLVolumeThresholdWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:20: #include "qMRMLVolumeThresholdWidget.h"`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:22: #include "ui_qMRMLVolumeThresholdWidget.h"`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:28: class qMRMLVolumeThresholdWidgetPrivate`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:30: , public Ui_qMRMLVolumeThresholdWidget`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:32: Q_DECLARE_PUBLIC(qMRMLVolumeThresholdWidget);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:38: qMRMLVolumeThresholdWidgetPrivate(qMRMLVolumeThresholdWidget& object);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:48: qMRMLVolumeThresholdWidgetPrivate::qMRMLVolumeThresholdWidgetPrivate(qMRMLVolumeThresholdWidget& object)`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:54: void qMRMLVolumeThresholdWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:56: Q_Q(qMRMLVolumeThresholdWidget);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:63: q->setAutoThreshold(qMRMLVolumeThresholdWidget::Off);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:74: bool qMRMLVolumeThresholdWidgetPrivate::blockSignals(bool block)`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:82: void qMRMLVolumeThresholdWidgetPrivate::setRange(double min, double max)`
- API footprints: `GetApplyThreshold`, `SetApplyThreshold`, `SetAutoThreshold`, `StartModify`

## widget: ThresholdLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Threshold:  | ThresholdLabel | QLabel
- Text: Threshold: 
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.h`

## widget: AutoManualComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `QComboBox`
- Search text: AutoManualComboBox | QComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:67: this->connect(this->AutoManualComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setAutoThreshold(int)));`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:173: return static_cast<ControlMode>(d->AutoManualComboBox->currentIndex());`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:180: return d->AutoManualComboBox->currentIndex() == qMRMLVolumeThresholdWidget::Off;`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:306: d->AutoManualComboBox->setCurrentIndex(index);`
- Connected slots/functions: `setAutoThreshold`

## widget: VolumeThresholdRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkRangeWidget`
- Search text: VolumeThresholdRangeWidget | ctkRangeWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:60: this->VolumeThresholdRangeWidget->minimumSpinBox()->setDecimalsOption(ctkDoubleSpinBox::DecimalsByKey | ctkDoubleSpinBox::DecimalsByShortcuts);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:61: this->VolumeThresholdRangeWidget->maximumSpinBox()->setDecimalsOption(ctkDoubleSpinBox::DecimalsByKey | ctkDoubleSpinBox::DecimalsByShortcuts);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:65: this->connect(this->VolumeThresholdRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(setThreshold(double, double)));`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:77: this->VolumeThresholdRangeWidget->blockSignals(block);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:85: this->VolumeThresholdRangeWidget->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:92: this->VolumeThresholdRangeWidget->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:99: this->VolumeThresholdRangeWidget->setSingleStep(singleStep);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:232: return d->VolumeThresholdRangeWidget->minimumValue();`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:239: return d->VolumeThresholdRangeWidget->maximumValue();`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:246: return d->VolumeThresholdRangeWidget->minimum();`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:253: return d->VolumeThresholdRangeWidget->maximum();`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:274: d->VolumeThresholdRangeWidget->setMinimum(min);`
- Connected slots/functions: `setThreshold`
- API footprints: `EndModify`, `GetAutoThreshold`, `GetLowerThreshold`, `GetUpperThreshold`, `SetLowerThreshold`, `SetUpperThreshold`, `StartModify`

## widget: RangeButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | RangeButton | QToolButton
- Text: ...
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:69: this->RangeButton->setMenu(this->OptionsMenu);`
  - `Libs/MRML/Widgets/qMRMLVolumeThresholdWidget.cxx:70: this->RangeButton->setPopupMode(QToolButton::InstantPopup);`
- Key UI properties: {"checkable": "true"}
