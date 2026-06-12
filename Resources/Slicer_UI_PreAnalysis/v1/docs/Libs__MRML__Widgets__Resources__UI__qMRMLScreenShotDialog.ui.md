# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLScreenShotDialog.ui

- Owner class: `qMRMLScreenShotDialog`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLScreenShotDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLScreenShotDialog

- Confidence: `linked_to_api`
- Widget/action class: `QDialog`
- Search text: qMRMLScreenShotDialog | QDialog
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:33: #include "qMRMLScreenShotDialog.h"`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:38: #include "ui_qMRMLScreenShotDialog.h"`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:50: class qMRMLScreenShotDialogPrivate : public Ui_qMRMLScreenShotDialog`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:52: Q_DECLARE_PUBLIC(qMRMLScreenShotDialog);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:55: qMRMLScreenShotDialog* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:58: qMRMLScreenShotDialogPrivate(qMRMLScreenShotDialog& object);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:75: qMRMLScreenShotDialogPrivate::qMRMLScreenShotDialogPrivate(qMRMLScreenShotDialog& object)`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:78: qRegisterMetaType<qMRMLScreenShotDialog::WidgetType>("qMRMLScreenShotDialog::WidgetType");`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:81: this->LastWidgetType = qMRMLScreenShotDialog::FullLayout;`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:85: void qMRMLScreenShotDialogPrivate::setupUi(QDialog* dialog)`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:87: Q_Q(qMRMLScreenShotDialog);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:89: this->Ui_qMRMLScreenShotDialog::setupUi(dialog);`
- Connected slots/functions: `idClicked`, `setLastWidgetType`
- API footprints: `GetPointer`

## widget: groupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox | QGroupBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`

## widget: fullLayoutRadio

- Confidence: `linked_to_slot`
- Widget/action class: `QRadioButton`
- Search text: Full layout | fullLayoutRadio | QRadioButton
- Text: Full layout
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:92: this->WidgetTypeGroup->addButton(this->fullLayoutRadio, qMRMLScreenShotDialog::FullLayout);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:122: this->fullLayoutRadio->setEnabled(state);`
- Connected slots/functions: `grabScreenShot`
- Declared UI connections: `clicked() -> qMRMLScreenShotDialog.grabScreenShot()`
- Key UI properties: {"checked": "true"}

## widget: threeDViewRadio

- Confidence: `linked_to_slot`
- Widget/action class: `QRadioButton`
- Search text: 3D View | threeDViewRadio | QRadioButton
- Text: 3D View
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:93: this->WidgetTypeGroup->addButton(this->threeDViewRadio, qMRMLScreenShotDialog::ThreeD);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:118: this->threeDViewRadio->setEnabled(state);`
- Connected slots/functions: `grabScreenShot`
- Declared UI connections: `clicked() -> qMRMLScreenShotDialog.grabScreenShot()`
- Key UI properties: {"checked": "false"}

## widget: redSliceViewRadio

- Confidence: `linked_to_slot`
- Widget/action class: `QRadioButton`
- Search text: Red Slice View | redSliceViewRadio | QRadioButton
- Text: Red Slice View
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:94: this->WidgetTypeGroup->addButton(this->redSliceViewRadio, qMRMLScreenShotDialog::Red);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:119: this->redSliceViewRadio->setEnabled(state);`
- Connected slots/functions: `grabScreenShot`
- Declared UI connections: `clicked() -> qMRMLScreenShotDialog.grabScreenShot()`

## widget: yellowSliceViewRadio

- Confidence: `linked_to_slot`
- Widget/action class: `QRadioButton`
- Search text: Yellow Slice View | yellowSliceViewRadio | QRadioButton
- Text: Yellow Slice View
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:95: this->WidgetTypeGroup->addButton(this->yellowSliceViewRadio, qMRMLScreenShotDialog::Yellow);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:120: this->yellowSliceViewRadio->setEnabled(state);`
- Connected slots/functions: `grabScreenShot`
- Declared UI connections: `clicked() -> qMRMLScreenShotDialog.grabScreenShot()`

## widget: greenSliceViewRadio

- Confidence: `linked_to_slot`
- Widget/action class: `QRadioButton`
- Search text: Green Slice View | greenSliceViewRadio | QRadioButton
- Text: Green Slice View
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:96: this->WidgetTypeGroup->addButton(this->greenSliceViewRadio, qMRMLScreenShotDialog::Green);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:121: this->greenSliceViewRadio->setEnabled(state);`
- Connected slots/functions: `grabScreenShot`
- Declared UI connections: `clicked() -> qMRMLScreenShotDialog.grabScreenShot()`

## widget: ScreenshotWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkThumbnailLabel`
- Search text: ScreenshotWidget | ctkThumbnailLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:243: d->ScreenshotWidget->setPixmap(QPixmap::fromImage(qimage));`

## widget: scaleFactorLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Scale factor: | scaleFactorLabel | QLabel
- Text: Scale factor:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:258: d->scaleFactorLabel->setVisible(state);`

## widget: scaleFactorSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Adjust the Magnification factor. | scaleFactorSpinBox | ctkDoubleSpinBox
- Tooltip: Adjust the Magnification factor.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:123: this->scaleFactorSpinBox->setEnabled(state);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:225: d->scaleFactorSpinBox->setValue(newScaleFactor);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:232: return d->scaleFactorSpinBox->value();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:257: d->scaleFactorSpinBox->setVisible(state);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:265: return d->scaleFactorSpinBox->isVisible();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:353: double scaleFactor = d->scaleFactorSpinBox->value();`
- Connected slots/functions: `grabScreenShot`
- Declared UI connections: `valueChanged(double) -> qMRMLScreenShotDialog.grabScreenShot()`

## widget: saveAsButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Save As... | saveAsButton | QPushButton
- Text: Save As...
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:100: QObject::connect(this->saveAsButton, SIGNAL(clicked()), q, SLOT(saveAs()));`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:272: d->saveAsButton->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:276: bool qMRMLScreenShotDialog::saveAsButtonVisibility() const`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:279: return d->saveAsButton->isVisible();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.h:45: Q_PROPERTY(bool saveAsButtonVisibility READ saveAsButtonVisibility WRITE setSaveAsButtonVisibility)`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.h:86: bool saveAsButtonVisibility() const;`
- Connected slots/functions: `saveAs`

## widget: nameEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: nameEdit | QLineEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:166: d->nameEdit->setText(newName);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:167: d->nameEdit->setFocus();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:168: d->nameEdit->selectAll();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:172: QString qMRMLScreenShotDialog::nameEdit() const`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:175: return d->nameEdit->text();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:290: d->nameEdit->clear();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:427: QString name = nameEdit();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.h:42: Q_PROPERTY(QString nameEdit READ nameEdit WRITE setNameEdit)`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.h:66: QString nameEdit() const;`

## widget: nameLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Name: | nameLabel | QLabel
- Text: Name:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`

## widget: buttonBox

- Confidence: `linked_to_slot`
- Widget/action class: `QDialogButtonBox`
- Search text: Save snapshot via File Save. Edit in Annotations module. | buttonBox | QDialogButtonBox
- Tooltip: Save snapshot via File Save. Edit in Annotations module.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Connected slots/functions: `accept`, `reject`
- Declared UI connections: `rejected() -> qMRMLScreenShotDialog.reject()`; `accepted() -> qMRMLScreenShotDialog.accept()`

## widget: groupBox_2

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_2 | QGroupBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`

## widget: descriptionTextEdit

- Confidence: `linked_to_code`
- Widget/action class: `QTextEdit`
- Search text: descriptionTextEdit | QTextEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx`, `Libs/MRML/Widgets/qMRMLScreenShotDialog.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:182: d->descriptionTextEdit->setPlainText(newDescription);`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:189: return d->descriptionTextEdit->toPlainText();`
  - `Libs/MRML/Widgets/qMRMLScreenShotDialog.cxx:287: d->descriptionTextEdit->clear();`
