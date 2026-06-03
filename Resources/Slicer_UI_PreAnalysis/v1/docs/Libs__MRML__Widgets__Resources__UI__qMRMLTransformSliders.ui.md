# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLTransformSliders.ui

- Owner class: `qMRMLTransformSliders`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLTransformSliders.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLTransformSliders

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLTransformSliders | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:21: #include "qMRMLTransformSliders.h"`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:22: #include "ui_qMRMLTransformSliders.h"`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:38: class qMRMLTransformSlidersPrivate : public Ui_qMRMLTransformSliders`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:41: qMRMLTransformSlidersPrivate()`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:53: qMRMLTransformSliders::qMRMLTransformSliders(QWidget* slidersParent)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:55: , d_ptr(new qMRMLTransformSlidersPrivate)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:57: Q_D(qMRMLTransformSliders);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:70: this->setCoordinateReference(qMRMLTransformSliders::GLOBAL);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:71: this->setTypeOfTransform(qMRMLTransformSliders::TRANSLATION);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:90: qMRMLTransformSliders::~qMRMLTransformSliders() = default;`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:93: void qMRMLTransformSliders::setCoordinateReference(CoordinateReferenceType _coordinateReference)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:95: Q_D(qMRMLTransformSliders);`
- API footprints: `GetMatrix`, `GetPointer`, `vtkMRMLTransformNode::SafeDownCast`

## widget: SlidersGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: SlidersGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:275: d->SlidersGroupBox->setTitle(_title);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:282: return d->SlidersGroupBox->title();`

## widget: LRLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: LR | Left-Right | LRLabel | QLabel
- Text: LR
- Tooltip: Left-Right
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:399: return d->LRLabel->text();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:417: void qMRMLTransformSliders::setLRLabel(const QString& label)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:420: d->LRLabel->setText(label);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.h:48: Q_PROPERTY(QString LRLabel READ lrLabel WRITE setLRLabel)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.h:125: void setLRLabel(const QString& label);`

## widget: LRSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: L<-->R | LRSlider | qMRMLLinearTransformSlider
- Tooltip: L<-->R
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:63: d->LRSlider->spinBox()->setDecimalsOption(decimalsOptions);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:66: d->LRSlider->setSynchronizeSiblings(ctkSliderWidget::SynchronizeDecimals);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:73: this->connect(d->LRSlider, SIGNAL(valueChanged(double)), SLOT(onLRSliderPositionChanged(double)));`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:83: this->connect(d->LRSlider, SIGNAL(decimalsChanged(int)), SIGNAL(decimalsChanged(int)));`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:107: blocked = d->LRSlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:108: d->LRSlider->reset();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:109: d->LRSlider->blockSignals(blocked);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:122: d->LRSlider->setCoordinateReference(ref);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:134: qMRMLLinearTransformSlider::CoordinateReferenceType ref = d->LRSlider->coordinateReference();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:149: d->LRSlider->setTypeOfTransform(qMRMLLinearTransformSlider::TRANSLATION_LR);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:155: d->LRSlider->setTypeOfTransform(qMRMLLinearTransformSlider::ROTATION_LR);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:191: bool blocked = d->LRSlider->blockSignals(true);`
- Connected slots/functions: `onLRSliderPositionChanged`
- API footprints: `vtkMRMLTransformableNode::TransformModifiedEvent`

## widget: PALabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: PA | Posterior-Anterior | PALabel | QLabel
- Text: PA
- Tooltip: Posterior-Anterior
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:406: return d->PALabel->text();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:424: void qMRMLTransformSliders::setPALabel(const QString& label)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:427: d->PALabel->setText(label);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.h:49: Q_PROPERTY(QString PALabel READ paLabel WRITE setPALabel)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.h:126: void setPALabel(const QString& label);`

## widget: PASlider

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: P<-->A | PASlider | qMRMLLinearTransformSlider
- Tooltip: P<-->A
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:64: d->PASlider->spinBox()->setDecimalsOption(decimalsOptions);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:67: d->PASlider->setSynchronizeSiblings(ctkSliderWidget::SynchronizeDecimals);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:74: this->connect(d->PASlider, SIGNAL(valueChanged(double)), SLOT(onPASliderPositionChanged(double)));`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:110: blocked = d->PASlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:111: d->PASlider->reset();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:112: d->PASlider->blockSignals(blocked);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:123: d->PASlider->setCoordinateReference(ref);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:150: d->PASlider->setTypeOfTransform(qMRMLLinearTransformSlider::TRANSLATION_PA);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:156: d->PASlider->setTypeOfTransform(qMRMLLinearTransformSlider::ROTATION_PA);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:194: blocked = d->PASlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:195: d->PASlider->reset();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:196: d->PASlider->blockSignals(blocked);`
- Connected slots/functions: `onPASliderPositionChanged`

## widget: ISLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: IS | Inferior-Superior | ISLabel | QLabel
- Text: IS
- Tooltip: Inferior-Superior
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:413: return d->ISLabel->text();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:431: void qMRMLTransformSliders::setISLabel(const QString& label)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:434: d->ISLabel->setText(label);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.h:50: Q_PROPERTY(QString ISLabel READ isLabel WRITE setISLabel)`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.h:127: void setISLabel(const QString& label);`

## widget: ISSlider

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: I<-->S | ISSlider | qMRMLLinearTransformSlider
- Tooltip: I<-->S
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:65: d->ISSlider->spinBox()->setDecimalsOption(decimalsOptions);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:68: d->ISSlider->setSynchronizeSiblings(ctkSliderWidget::SynchronizeDecimals);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:75: this->connect(d->ISSlider, SIGNAL(valueChanged(double)), SLOT(onISSliderPositionChanged(double)));`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:113: blocked = d->ISSlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:114: d->ISSlider->reset();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:115: d->ISSlider->blockSignals(blocked);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:124: d->ISSlider->setCoordinateReference(ref);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:151: d->ISSlider->setTypeOfTransform(qMRMLLinearTransformSlider::TRANSLATION_IS);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:157: d->ISSlider->setTypeOfTransform(qMRMLLinearTransformSlider::ROTATION_IS);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:197: blocked = d->ISSlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:198: d->ISSlider->reset();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:199: d->ISSlider->blockSignals(blocked);`
- Connected slots/functions: `onISSliderPositionChanged`

## widget: MinMaxWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: MinMaxWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:367: d->MinMaxWidget->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:374: return d->MinMaxWidget->isVisibleTo(const_cast<qMRMLTransformSliders*>(this));`

## widget: MinLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Min | MinLabel | QLabel
- Text: Min
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`

## widget: MinValueSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSpinBox`
- Search text: MinValueSpinBox | qMRMLSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:77: this->connect(d->MinValueSpinBox, SIGNAL(valueChanged(double)), SLOT(onMinimumChanged(double)));`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:80: this->onMinimumChanged(d->MinValueSpinBox->value());`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:304: return d->MinValueSpinBox->value();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:318: d->MinValueSpinBox->setValue(min);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:335: d->MinValueSpinBox->setValue(min);`
- Connected slots/functions: `onMinimumChanged`

## widget: MaxLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Max | MaxLabel | QLabel
- Text: Max
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`

## widget: MaxValueSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSpinBox`
- Search text: MaxValueSpinBox | qMRMLSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTransformSliders.cxx`, `Libs/MRML/Widgets/qMRMLTransformSliders.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:78: this->connect(d->MaxValueSpinBox, SIGNAL(valueChanged(double)), SLOT(onMaximumChanged(double)));`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:81: this->onMaximumChanged(d->MaxValueSpinBox->value());`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:311: return d->MaxValueSpinBox->value();`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:325: d->MaxValueSpinBox->setValue(max);`
  - `Libs/MRML/Widgets/qMRMLTransformSliders.cxx:336: d->MaxValueSpinBox->setValue(max);`
- Connected slots/functions: `onMaximumChanged`
