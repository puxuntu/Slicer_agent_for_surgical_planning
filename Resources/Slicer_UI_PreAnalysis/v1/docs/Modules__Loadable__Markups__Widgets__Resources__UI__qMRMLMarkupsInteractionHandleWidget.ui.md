# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsInteractionHandleWidget.ui

- Owner class: `qMRMLMarkupsInteractionHandleWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsInteractionHandleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsInteractionHandleWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLMarkupsInteractionHandleWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:25: #include "qMRMLMarkupsInteractionHandleWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:26: #include "ui_qMRMLMarkupsInteractionHandleWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:33: class qMRMLMarkupsInteractionHandleWidgetPrivate : public Ui_qMRMLMarkupsInteractionHandleWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:35: Q_DECLARE_PUBLIC(qMRMLMarkupsInteractionHandleWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:38: qMRMLMarkupsInteractionHandleWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:41: qMRMLMarkupsInteractionHandleWidgetPrivate(qMRMLMarkupsInteractionHandleWidget& object);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:48: qMRMLMarkupsInteractionHandleWidgetPrivate::qMRMLMarkupsInteractionHandleWidgetPrivate(qMRMLMarkupsInteractionHandleWidget& object)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:55: void qMRMLMarkupsInteractionHandleWidgetPrivate::init()`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:57: Q_Q(qMRMLMarkupsInteractionHandleWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:98: // qMRMLMarkupsInteractionHandleWidget methods`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:101: qMRMLMarkupsInteractionHandleWidget::qMRMLMarkupsInteractionHandleWidget(QWidget* _parent)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:103: , d_ptr(new qMRMLMarkupsInteractionHandleWidgetPrivate(*this))`

## widget: translationEnableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable translation: | translationEnableLabel | QLabel
- Text: Enable translation:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`

## widget: yLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Y | yLabel | QLabel
- Text: Y
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:80: this->yLabel->hide();`

## widget: translateYCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateYCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:64: QObject::connect(this->translateYCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:84: this->translateYCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:138: d->translateYCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:185: wasBlocking = d->translateYCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:186: d->translateYCheckBox->setChecked(translationHandleAxes[1]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:187: d->translateYCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:265: d->translateXCheckBox->isChecked(), d->translateYCheckBox->isChecked(), d->translateZCheckBox->isChecked(), d->translateViewPlaneCheckBox->isChecked()`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: scaleZCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleZCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:75: QObject::connect(this->scaleZCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:93: this->scaleZCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:149: d->scaleZCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:162: d->scaleZCheckBox->setEnabled(canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:235: wasBlocking = d->scaleZCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:236: d->scaleZCheckBox->setChecked(scaleHandleAxes[2] && canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:237: d->scaleZCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:274: bool scaleHandleAxes[4] = { d->scaleXCheckBox->isChecked(), d->scaleYCheckBox->isChecked(), d->scaleZCheckBox->isChecked(), d->scaleViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: rotateZCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateZCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:70: QObject::connect(this->rotateZCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:89: this->rotateZCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:144: d->rotateZCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:212: wasBlocking = d->rotateZCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:213: d->rotateZCheckBox->setChecked(rotationHandleAxes[2]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:214: d->rotateZCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:270: bool rotationHandleAxes[4] = { d->rotateXCheckBox->isChecked(), d->rotateYCheckBox->isChecked(), d->rotateZCheckBox->isChecked(), d->rotateViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: scaleXCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleXCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:73: QObject::connect(this->scaleXCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:91: this->scaleXCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:147: d->scaleXCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:160: d->scaleXCheckBox->setEnabled(canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:227: wasBlocking = d->scaleXCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:228: d->scaleXCheckBox->setChecked(scaleHandleAxes[0] && canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:229: d->scaleXCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:274: bool scaleHandleAxes[4] = { d->scaleXCheckBox->isChecked(), d->scaleYCheckBox->isChecked(), d->scaleZCheckBox->isChecked(), d->scaleViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetCanDisplayScaleHandles`, `GetScaleHandleComponentVisibility`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: xLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: X | xLabel | QLabel
- Text: X
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:79: this->xLabel->hide();`

## widget: zLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Z | zLabel | QLabel
- Text: Z
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:81: this->zLabel->hide();`

## widget: scaleVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:72: QObject::connect(this->scaleVisibilityCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:146: d->scaleVisibilityCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:159: d->scaleVisibilityCheckBox->setEnabled(canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:222: wasBlocking = d->scaleVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:223: d->scaleVisibilityCheckBox->setChecked(d->DisplayNode->GetScaleHandleVisibility() && canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:224: d->scaleVisibilityCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:276: d->DisplayNode->SetScaleHandleVisibility(d->scaleVisibilityCheckBox->isChecked());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetCanDisplayScaleHandles`, `GetScaleHandleComponentVisibility`, `GetScaleHandleVisibility`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Size: | label_2 | QLabel
- Text: Size:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`

## widget: moreOptionsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: More options... | moreOptionsCheckBox | QPushButton
- Text: More options...
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Connected slots/functions: `setVisible`
- Declared UI connections: `toggled(bool) -> translateXCheckBox.setVisible(bool)`; `toggled(bool) -> scaleViewPlaneCheckBox.setVisible(bool)`; `toggled(bool) -> scaleZCheckBox.setVisible(bool)`; `toggled(bool) -> scaleYCheckBox.setVisible(bool)`; `toggled(bool) -> scaleXCheckBox.setVisible(bool)`; `toggled(bool) -> rotateZCheckBox.setVisible(bool)`
- Key UI properties: {"checkable": "true"}

## widget: overallVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: overallVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:61: QObject::connect(this->overallVisibilityCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:135: d->overallVisibilityCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:170: wasBlocking = d->overallVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:171: d->overallVisibilityCheckBox->setChecked(d->DisplayNode->GetHandlesInteractive());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:172: d->overallVisibilityCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:262: d->DisplayNode->SetHandlesInteractive(d->overallVisibilityCheckBox->isChecked());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetHandlesInteractive`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: scaleViewPlaneCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleViewPlaneCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:76: QObject::connect(this->scaleViewPlaneCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:94: this->scaleViewPlaneCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:163: d->scaleViewPlaneCheckBox->setEnabled(canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:239: wasBlocking = d->scaleViewPlaneCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:240: d->scaleViewPlaneCheckBox->setChecked(scaleHandleAxes[3] && canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:241: d->scaleViewPlaneCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:274: bool scaleHandleAxes[4] = { d->scaleXCheckBox->isChecked(), d->scaleYCheckBox->isChecked(), d->scaleZCheckBox->isChecked(), d->scaleViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: interactionHandleScaleSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: interactionHandleScaleSlider | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:77: QObject::connect(this->interactionHandleScaleSlider, SIGNAL(valueChanged(double)), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:150: d->interactionHandleScaleSlider->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:243: wasBlocking = d->interactionHandleScaleSlider->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:244: if (d->DisplayNode->GetInteractionHandleScale() > d->interactionHandleScaleSlider->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:246: d->interactionHandleScaleSlider->setMaximum(d->DisplayNode->GetInteractionHandleScale());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:248: d->interactionHandleScaleSlider->setValue(d->DisplayNode->GetInteractionHandleScale());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:249: wasBlocking = d->interactionHandleScaleSlider->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:278: d->DisplayNode->SetInteractionHandleScale(d->interactionHandleScaleSlider->value());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetInteractionHandleScale`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: rotateYCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateYCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:69: QObject::connect(this->rotateYCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:88: this->rotateYCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:143: d->rotateYCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:208: wasBlocking = d->rotateYCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:209: d->rotateYCheckBox->setChecked(rotationHandleAxes[1]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:210: d->rotateYCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:270: bool rotationHandleAxes[4] = { d->rotateXCheckBox->isChecked(), d->rotateYCheckBox->isChecked(), d->rotateZCheckBox->isChecked(), d->rotateViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Visibility: | label | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:740: QTableWidgetItem* labelItem = new QTableWidgetItem(QString::fromStdString(controlPointLabel));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:763: d->MarkupsControlPointsTableWidget->setItem(i, CONTROL_POINT_LABEL_COLUMN, labelItem);`
- API footprints: `GetNthControlPointPosition`

## widget: translateZCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateZCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:65: QObject::connect(this->translateZCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:85: this->translateZCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:139: d->translateZCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:189: wasBlocking = d->translateZCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:190: d->translateZCheckBox->setChecked(translationHandleAxes[2]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:191: d->translateZCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:265: d->translateXCheckBox->isChecked(), d->translateYCheckBox->isChecked(), d->translateZCheckBox->isChecked(), d->translateViewPlaneCheckBox->isChecked()`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: translateVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:62: QObject::connect(this->translateVisibilityCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:136: d->translateVisibilityCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:176: wasBlocking = d->translateVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:177: d->translateVisibilityCheckBox->setChecked(d->DisplayNode->GetTranslationHandleVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:178: d->translateVisibilityCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:268: d->DisplayNode->SetTranslationHandleVisibility(d->translateVisibilityCheckBox->isChecked());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetTranslationHandleComponentVisibility`, `GetTranslationHandleVisibility`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: viewPlaneLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: View plane | viewPlaneLabel | QLabel
- Text: View plane
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:82: this->viewPlaneLabel->hide();`

## widget: translateViewPlaneCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateViewPlaneCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:66: QObject::connect(this->translateViewPlaneCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:86: this->translateViewPlaneCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:140: d->translateViewPlaneCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:193: wasBlocking = d->translateViewPlaneCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:194: d->translateViewPlaneCheckBox->setChecked(translationHandleAxes[3]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:195: d->translateViewPlaneCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:265: d->translateXCheckBox->isChecked(), d->translateYCheckBox->isChecked(), d->translateZCheckBox->isChecked(), d->translateViewPlaneCheckBox->isChecked()`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: rotateXCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateXCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:68: QObject::connect(this->rotateXCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:87: this->rotateXCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:142: d->rotateXCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:204: wasBlocking = d->rotateXCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:205: d->rotateXCheckBox->setChecked(rotationHandleAxes[0]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:206: d->rotateXCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:270: bool rotationHandleAxes[4] = { d->rotateXCheckBox->isChecked(), d->rotateYCheckBox->isChecked(), d->rotateZCheckBox->isChecked(), d->rotateViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetRotationHandleComponentVisibility`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: scaleEnableLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Enable scaling: | scaleEnableLabel | QLabel
- Text: Enable scaling:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:164: d->scaleEnableLabel->setEnabled(canDisplayScaleHandles);`

## widget: translateXCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateXCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:63: QObject::connect(this->translateXCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:83: this->translateXCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:137: d->translateXCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:181: wasBlocking = d->translateXCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:182: d->translateXCheckBox->setChecked(translationHandleAxes[0]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:183: d->translateXCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:265: d->translateXCheckBox->isChecked(), d->translateYCheckBox->isChecked(), d->translateZCheckBox->isChecked(), d->translateViewPlaneCheckBox->isChecked()`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetTranslationHandleComponentVisibility`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: rotateEnableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable rotation: | rotateEnableLabel | QLabel
- Text: Enable rotation:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`

## widget: rotateVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:67: QObject::connect(this->rotateVisibilityCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:141: d->rotateVisibilityCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:199: wasBlocking = d->rotateVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:200: d->rotateVisibilityCheckBox->setChecked(d->DisplayNode->GetRotationHandleVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:201: d->rotateVisibilityCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:272: d->DisplayNode->SetRotationHandleVisibility(d->rotateVisibilityCheckBox->isChecked());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetRotationHandleComponentVisibility`, `GetRotationHandleVisibility`, `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: scaleYCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleYCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:74: QObject::connect(this->scaleYCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:92: this->scaleYCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:148: d->scaleYCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:161: d->scaleYCheckBox->setEnabled(canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:231: wasBlocking = d->scaleYCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:232: d->scaleYCheckBox->setChecked(scaleHandleAxes[1] && canDisplayScaleHandles);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:233: d->scaleYCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:274: bool scaleHandleAxes[4] = { d->scaleXCheckBox->isChecked(), d->scaleYCheckBox->isChecked(), d->scaleZCheckBox->isChecked(), d->scaleViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`

## widget: rotateViewPlaneCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateViewPlaneCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:71: QObject::connect(this->rotateViewPlaneCheckBox, SIGNAL(clicked()), q, SLOT(updateMRMLFromWidget()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:90: this->rotateViewPlaneCheckBox->hide();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:145: d->rotateViewPlaneCheckBox->setEnabled(d->DisplayNode != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:216: wasBlocking = d->rotateViewPlaneCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:217: d->rotateViewPlaneCheckBox->setChecked(rotationHandleAxes[3]);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:218: d->rotateViewPlaneCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsInteractionHandleWidget.cxx:270: bool rotationHandleAxes[4] = { d->rotateXCheckBox->isChecked(), d->rotateYCheckBox->isChecked(), d->rotateZCheckBox->isChecked(), d->rotateViewPlaneCheckBox->isChecked() };`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `SetHandlesInteractive`, `SetInteractionHandleScale`, `SetRotationHandleComponentVisibility`, `SetRotationHandleVisibility`, `SetScaleHandleComponentVisibility`, `SetScaleHandleVisibility`, `SetTranslationHandleComponentVisibility`, `SetTranslationHandleVisibility`
