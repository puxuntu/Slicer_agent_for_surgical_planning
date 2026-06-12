# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLWindowLevelWidget.ui

- Owner class: `qMRMLWindowLevelWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLWindowLevelWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLWindowLevelWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLWindowLevelWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:21: #include "qMRMLWindowLevelWidget.h"`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:22: #include "ui_qMRMLWindowLevelWidget.h"`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:28: class qMRMLWindowLevelWidgetPrivate`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:30: , public Ui_qMRMLWindowLevelWidget`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:32: Q_DECLARE_PUBLIC(qMRMLWindowLevelWidget);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:38: qMRMLWindowLevelWidgetPrivate(qMRMLWindowLevelWidget& object);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:39: ~qMRMLWindowLevelWidgetPrivate() override;`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:49: qMRMLWindowLevelWidgetPrivate::qMRMLWindowLevelWidgetPrivate(qMRMLWindowLevelWidget& object)`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:55: qMRMLWindowLevelWidgetPrivate::~qMRMLWindowLevelWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:58: void qMRMLWindowLevelWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:60: Q_Q(qMRMLWindowLevelWidget);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:65: q->setAutoWindowLevel(qMRMLWindowLevelWidget::Auto);`
- API footprints: `EndModify`, `GetAutoWindowLevel`, `GetLevel`, `SetAutoWindowLevel`, `StartModify`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Window/Level: | label | QLabel
- Text: Window/Level:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`

## widget: AutoManualComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: AutoManualComboBox | QComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:77: QObject::connect(this->AutoManualComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setAutoWindowLevel(int)));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:154: bool blocked = d->AutoManualComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:155: if (d->AutoManualComboBox->currentIndex() != autoWindowLevel)`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:157: d->AutoManualComboBox->setCurrentIndex(autoWindowLevel);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:159: d->AutoManualComboBox->blockSignals(blocked);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:209: switch (d->AutoManualComboBox->currentIndex())`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:435: case 1: d->AutoManualComboBox->setCurrentIndex(qMRMLWindowLevelWidget::Auto); break;`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:437: if (d->AutoManualComboBox->currentIndex() == qMRMLWindowLevelWidget::Auto)`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:439: d->AutoManualComboBox->setCurrentIndex(qMRMLWindowLevelWidget::Manual);`
- Connected slots/functions: `setAutoWindowLevel`
- API footprints: `EndModify`, `GetAutoWindowLevel`, `SetAutoWindowLevel`, `StartModify`

## widget: WindowSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: WindowSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:69: QObject::connect(this->WindowSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setWindow(double)));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:88: this->WindowSpinBox->blockSignals(block);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:100: this->WindowSpinBox->setRange(0, max - min);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:111: this->WindowSpinBox->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:127: this->WindowSpinBox->setSingleStep(singleStep);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:171: d->WindowSpinBox->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:182: d->WindowSpinBox->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:425: d->WindowSpinBox->setValue(window);`
- Connected slots/functions: `setWindow`
- API footprints: `GetLevel`

## widget: MinSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: MinSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:72: QObject::connect(this->MinSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setMinimumValue(double)));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:74: this->MinSpinBox->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:90: this->MinSpinBox->blockSignals(block);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:102: this->MinSpinBox->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:113: this->MinSpinBox->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:129: this->MinSpinBox->setSingleStep(singleStep);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:173: d->MinSpinBox->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:180: d->MinSpinBox->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:428: d->MinSpinBox->setValue(windowLevelMin);`
- Connected slots/functions: `setMinimumValue`

## widget: WindowLevelRangeSlider

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDoubleRangeSlider`
- Search text: WindowLevelRangeSlider | ctkDoubleRangeSlider
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:67: QObject::connect(this->WindowLevelRangeSlider, SIGNAL(valuesChanged(double, double)), q, SLOT(setMinMaxRangeValue(double, double)));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:87: this->WindowLevelRangeSlider->blockSignals(block);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:99: this->WindowLevelRangeSlider->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:124: double sliderMinimumStep = qMax(this->WindowLevelRangeSlider->maximum() / std::numeric_limits<double>::max(), std::numeric_limits<double>::epsilon());`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:125: this->WindowLevelRangeSlider->setSingleStep(qMax(singleStep, sliderMinimumStep));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:170: d->WindowLevelRangeSlider->setSymmetricMoves(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:179: d->WindowLevelRangeSlider->setSymmetricMoves(true);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:279: double min = d->WindowLevelRangeSlider->minimumValue();`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:280: double max = d->WindowLevelRangeSlider->maximumValue();`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:290: double min = d->WindowLevelRangeSlider->minimumValue();`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:299: double max = d->WindowLevelRangeSlider->maximumValue();`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:308: double min = d->WindowLevelRangeSlider->minimum();`
- Connected slots/functions: `setMinMaxRangeValue`

## widget: MaxSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: MaxSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:73: QObject::connect(this->MaxSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setMaximumValue(double)));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:75: this->MaxSpinBox->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:91: this->MaxSpinBox->blockSignals(block);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:103: this->MaxSpinBox->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:114: this->MaxSpinBox->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:130: this->MaxSpinBox->setSingleStep(singleStep);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:174: d->MaxSpinBox->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:181: d->MaxSpinBox->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:429: d->MaxSpinBox->setValue(windowLevelMax);`
- Connected slots/functions: `setMaximumValue`

## widget: LevelSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: LevelSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:70: QObject::connect(this->LevelSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setLevel(double)));`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:89: this->LevelSpinBox->blockSignals(block);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:101: this->LevelSpinBox->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:112: this->LevelSpinBox->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:128: this->LevelSpinBox->setSingleStep(singleStep);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:172: d->LevelSpinBox->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:183: d->LevelSpinBox->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:426: d->LevelSpinBox->setValue(level);`
- Connected slots/functions: `setLevel`
- API footprints: `GetWindow`

## widget: RangeButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | RangeButton | QToolButton
- Text: ...
- Implementation candidates: `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx`, `Libs/MRML/Widgets/qMRMLWindowLevelWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:79: this->RangeButton->setMenu(this->OptionsMenu);`
  - `Libs/MRML/Widgets/qMRMLWindowLevelWidget.cxx:80: this->RangeButton->setPopupMode(QToolButton::InstantPopup);`
- Key UI properties: {"checkable": "true"}
