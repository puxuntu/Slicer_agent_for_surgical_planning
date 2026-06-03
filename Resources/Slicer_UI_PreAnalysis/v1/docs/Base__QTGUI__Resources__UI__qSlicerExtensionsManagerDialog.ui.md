# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerExtensionsManagerDialog.ui

- Owner class: `qSlicerExtensionsManagerDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerExtensionsManagerDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerExtensionsManagerDialog

- Confidence: `linked_to_code`
- Widget/action class: `QDialog`
- Search text: qSlicerExtensionsManagerDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx`, `Base/QTGUI/qSlicerExtensionsManagerDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:27: #include "qSlicerExtensionsManagerDialog.h"`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:30: #include "ui_qSlicerExtensionsManagerDialog.h"`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:33: class qSlicerExtensionsManagerDialogPrivate : public Ui_qSlicerExtensionsManagerDialog`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:35: Q_DECLARE_PUBLIC(qSlicerExtensionsManagerDialog);`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:38: qSlicerExtensionsManagerDialog* const q_ptr;`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:41: qSlicerExtensionsManagerDialogPrivate(qSlicerExtensionsManagerDialog& object);`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:53: qSlicerExtensionsManagerDialogPrivate::qSlicerExtensionsManagerDialogPrivate(qSlicerExtensionsManagerDialog& object)`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:60: void qSlicerExtensionsManagerDialogPrivate::init()`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:62: Q_Q(qSlicerExtensionsManagerDialog);`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:69: restartButton->setText(qSlicerExtensionsManagerDialog::tr("Restart"));`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:92: void qSlicerExtensionsManagerDialogPrivate::updateButtons()`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:94: Q_Q(qSlicerExtensionsManagerDialog);`

## widget: ExtensionsManagerWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerExtensionsManagerWidget`
- Search text: ExtensionsManagerWidget | qSlicerExtensionsManagerWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx`, `Base/QTGUI/qSlicerExtensionsManagerDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:66: QObject::connect(this->ExtensionsManagerWidget, SIGNAL(inBatchProcessing(bool)), q, SLOT(onBatchProcessingChanged()));`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:87: QObject::connect(extensionsPanel, SIGNAL(extensionsServerUrlChanged(QString)), this->ExtensionsManagerWidget, SLOT(refreshInstallWidget()));`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:105: bool isInBatchMode = this->ExtensionsManagerWidget->isInBatchProcessing();`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:130: return d->ExtensionsManagerWidget->extensionsManagerModel();`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:145: d->ExtensionsManagerWidget->setExtensionsManagerModel(model);`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:194: if (d->ExtensionsManagerWidget->confirmClose())`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:208: if (d->ExtensionsManagerWidget->confirmClose())`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:218: if (d->ExtensionsManagerWidget->confirmClose())`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:228: d->ExtensionsManagerWidget->setFocusToSearchBox();`
- Connected slots/functions: `onBatchProcessingChanged`, `refreshInstallWidget`

## widget: RestartRequestedLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: <font color="red">* Restart requested</font> | RestartRequestedLabel | QLabel
- Text: <font color="red">* Restart requested</font>
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx`, `Base/QTGUI/qSlicerExtensionsManagerDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:74: // keeping track of settings will allow us to display the "RestartRequestedLabel"`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:172: d->RestartRequestedLabel->setVisible(value);`

## widget: ButtonBox

- Confidence: `linked_to_code`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx`, `Base/QTGUI/qSlicerExtensionsManagerDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:68: QPushButton* restartButton = this->ButtonBox->button(QDialogButtonBox::Ok);`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:107: this->ButtonBox->setEnabled(!isInBatchMode);`
  - `Base/QTGUI/qSlicerExtensionsManagerDialog.cxx:173: d->ButtonBox->button(QDialogButtonBox::Ok)->setEnabled(value);`
