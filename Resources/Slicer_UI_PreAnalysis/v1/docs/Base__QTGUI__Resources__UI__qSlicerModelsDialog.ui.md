# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerModelsDialog.ui

- Owner class: `qSlicerModelsDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerModelsDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerModelsDialog

- Confidence: `linked_to_code`
- Widget/action class: `QDialog`
- Search text: qSlicerModelsDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerModelsDialog.cxx`, `Base/QTGUI/qSlicerModelsDialog.h`, `Base/QTGUI/qSlicerModelsDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModelsDialog.cxx:28: #include "qSlicerModelsDialog_p.h"`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:36: qSlicerModelsDialogPrivate::qSlicerModelsDialogPrivate(qSlicerModelsDialog& object, QWidget* _parentWidget)`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:43: qSlicerModelsDialogPrivate::~qSlicerModelsDialogPrivate() = default;`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:46: void qSlicerModelsDialogPrivate::init()`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:56: void qSlicerModelsDialogPrivate::openAddModelFileDialog()`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:58: Q_Q(qSlicerModelsDialog);`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:61: this->SelectedFiles = QFileDialog::getOpenFileNames(this, qSlicerModelsDialog::tr("Select Model file(s)"), "", filters.join(", "));`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:70: void qSlicerModelsDialogPrivate::openAddModelDirectoryDialog()`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:72: Q_Q(qSlicerModelsDialog);`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:74: QString modelDirectory = QFileDialog::getExistingDirectory(this, qSlicerModelsDialog::tr("Select a Model directory"), "", QFileDialog::ReadOnly);`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:86: qSlicerModelsDialog::qSlicerModelsDialog(QObject* _parent)`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:88: , d_ptr(new qSlicerModelsDialogPrivate(*this, nullptr))`

## widget: AddModelToolButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Add Model file(s) | AddModelToolButton | QToolButton
- Text: Add Model file(s)
- Implementation candidates: `Base/QTGUI/qSlicerModelsDialog.cxx`, `Base/QTGUI/qSlicerModelsDialog.h`, `Base/QTGUI/qSlicerModelsDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModelsDialog.cxx:49: this->AddModelToolButton->setIcon(this->style()->standardIcon(QStyle::SP_FileIcon));`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:51: connect(this->AddModelToolButton, SIGNAL(clicked()), this, SLOT(openAddModelFileDialog()));`
- Connected slots/functions: `openAddModelFileDialog`
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonTextUnderIcon"}

## widget: AddModelDirectoryToolButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Add Model directory | AddModelDirectoryToolButton | QToolButton
- Text: Add Model directory
- Implementation candidates: `Base/QTGUI/qSlicerModelsDialog.cxx`, `Base/QTGUI/qSlicerModelsDialog.h`, `Base/QTGUI/qSlicerModelsDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModelsDialog.cxx:50: this->AddModelDirectoryToolButton->setIcon(this->style()->standardIcon(QStyle::SP_DirIcon));`
  - `Base/QTGUI/qSlicerModelsDialog.cxx:52: connect(this->AddModelDirectoryToolButton, SIGNAL(clicked()), this, SLOT(openAddModelDirectoryDialog()));`
- Connected slots/functions: `openAddModelDirectoryDialog`
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonTextUnderIcon"}
