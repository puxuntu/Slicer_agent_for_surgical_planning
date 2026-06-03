# Slicer UI Analysis: Modules/Loadable/Texts/Widgets/Resources/UI/qMRMLTextWidget.ui

- Owner class: `qMRMLTextWidget`
- UI file: `Modules/Loadable/Texts/Widgets/Resources/UI/qMRMLTextWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLTextWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qMRMLTextWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx`, `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:22: #include "qMRMLTextWidget.h"`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:23: #include "ui_qMRMLTextWidget.h"`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:35: class qMRMLTextWidgetPrivate : public Ui_qMRMLTextWidget`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:37: Q_DECLARE_PUBLIC(qMRMLTextWidget);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:40: qMRMLTextWidget* const q_ptr;`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:43: qMRMLTextWidgetPrivate(qMRMLTextWidget& object);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:44: ~qMRMLTextWidgetPrivate();`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:45: virtual void setupUi(qMRMLTextWidget*);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:60: qMRMLTextWidgetPrivate::qMRMLTextWidgetPrivate(qMRMLTextWidget& object)`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:69: qMRMLTextWidgetPrivate::~qMRMLTextWidgetPrivate() = default;`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:72: void qMRMLTextWidgetPrivate::setupUi(qMRMLTextWidget* widget)`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:74: this->Ui_qMRMLTextWidget::setupUi(widget);`
- API footprints: `vtkMRMLTextNode::SafeDownCast`

## widget: TextEdit

- Confidence: `linked_to_api`
- Widget/action class: `QTextEdit`
- Search text: TextEdit | QTextEdit
- Implementation candidates: `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx`, `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:48: bool TextEditModified;`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:62: , TextEditModified(false)`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:120: connect(d->TextEdit, SIGNAL(textChanged()), this, SLOT(onTextEditChanged()));`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:186: d->TextEdit->setReadOnly(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:194: d->TextEdit->setReadOnly(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:202: d->TextEdit->setReadOnly(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:210: d->TextEdit->setReadOnly(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:220: bool wasBlocking = d->TextEdit->blockSignals(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:223: d->TextEdit->setReadOnly(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:224: d->TextEdit->setText("");`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:232: int position = d->TextEdit->textCursor().position();`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:238: d->TextEdit->setText(text.c_str());`
- Connected slots/functions: `onTextEditChanged`
- API footprints: `GetText`, `SetText`

## widget: EditButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Edit | EditButton | QPushButton
- Text: Edit
- Implementation candidates: `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx`, `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:121: connect(d->EditButton, SIGNAL(clicked()), this, SLOT(startEdits()));`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:187: d->EditButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:195: d->EditButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:203: d->EditButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:211: d->EditButton->setVisible(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:216: d->EditButton->setEnabled(!editing);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:226: d->EditButton->setEnabled(false);`
- Connected slots/functions: `startEdits`

## widget: CancelButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Cancel | CancelButton | QPushButton
- Text: Cancel
- Implementation candidates: `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx`, `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:122: connect(d->CancelButton, SIGNAL(clicked()), this, SLOT(cancelEdits()));`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:188: d->CancelButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:196: d->CancelButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:204: d->CancelButton->setVisible(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:212: d->CancelButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:217: d->CancelButton->setEnabled(editing);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:227: d->CancelButton->setEnabled(false);`
- Connected slots/functions: `cancelEdits`

## widget: SaveButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Save | SaveButton | QPushButton
- Text: Save
- Implementation candidates: `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx`, `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:123: connect(d->SaveButton, SIGNAL(clicked()), this, SLOT(saveEdits()));`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:189: d->SaveButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:197: d->SaveButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:205: d->SaveButton->setVisible(true);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:213: d->SaveButton->setVisible(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:218: d->SaveButton->setEnabled(editing);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:228: d->SaveButton->setEnabled(false);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:249: d->SaveButton->setToolTip("The original text has been modified since editing was started");`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:251: d->SaveButton->setIcon(warningIcon);`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:252: d->SaveButton->setIconSize(QSize(12, 12));`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:256: d->SaveButton->setToolTip("The original text has been modified since editing was started");`
  - `Modules/Loadable/Texts/Widgets/qMRMLTextWidget.cxx:257: d->SaveButton->setIcon(QIcon());`
- Connected slots/functions: `saveEdits`
