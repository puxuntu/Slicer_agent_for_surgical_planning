# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerActionsDialog.ui

- Owner class: `qSlicerActionsDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerActionsDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerActionsDialog

- Confidence: `linked_to_code`
- Widget/action class: `QDialog`
- Search text: qSlicerActionsDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerActionsDialog.cxx`, `Base/QTGUI/qSlicerActionsDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerActionsDialog.cxx:31: #include "qSlicerActionsDialog.h"`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:33: #include "ui_qSlicerActionsDialog.h"`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:36: class qSlicerActionsDialogPrivate : public Ui_qSlicerActionsDialog`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:38: Q_DECLARE_PUBLIC(qSlicerActionsDialog);`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:41: qSlicerActionsDialog* const q_ptr;`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:44: qSlicerActionsDialogPrivate(qSlicerActionsDialog& object);`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:53: qSlicerActionsDialogPrivate::qSlicerActionsDialogPrivate(qSlicerActionsDialog& object)`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:62: void qSlicerActionsDialogPrivate::init()`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:64: Q_Q(qSlicerActionsDialog);`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:72: QString shortcutsUrl = QString(qSlicerActionsDialog::tr("%1/user_guide/user_interface.html#mouse-keyboard-shortcuts")).arg(app->documentationBaseUrl());`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:80: qSlicerActionsDialog::qSlicerActionsDialog(QWidget* parentWidget)`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:82: , d_ptr(new qSlicerActionsDialogPrivate(*this))`

## widget: tabWidget

- Confidence: `linked_to_code`
- Widget/action class: `QTabWidget`
- Search text: tabWidget | QTabWidget
- Implementation candidates: `Base/QTGUI/qSlicerActionsDialog.cxx`, `Base/QTGUI/qSlicerActionsDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerActionsDialog.cxx:75: this->tabWidget->setTabEnabled(this->tabWidget->indexOf(this->WikiTab), false);`

## widget: ActionsTab

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: ActionsTab | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerActionsDialog.cxx`, `Base/QTGUI/qSlicerActionsDialog.h`

## widget: ActionsWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkActionsWidget`
- Search text: ActionsWidget | ctkActionsWidget
- Implementation candidates: `Base/QTGUI/qSlicerActionsDialog.cxx`, `Base/QTGUI/qSlicerActionsDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerActionsDialog.cxx:95: d->ActionsWidget->addAction(action, group);`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:102: d->ActionsWidget->addActions(actions, group);`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:109: d->ActionsWidget->clear();`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:116: d->ActionsWidget->setActionsWithNoShortcutVisible(visible);`
  - `Base/QTGUI/qSlicerActionsDialog.cxx:123: d->ActionsWidget->setMenuActionsVisible(visible);`

## widget: WikiTab

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: WikiTab | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerActionsDialog.cxx`, `Base/QTGUI/qSlicerActionsDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerActionsDialog.cxx:75: this->tabWidget->setTabEnabled(this->tabWidget->indexOf(this->WikiTab), false);`

## widget: buttonBox

- Confidence: `ui_only`
- Widget/action class: `QDialogButtonBox`
- Search text: buttonBox | QDialogButtonBox
- Implementation candidates: `Base/QTGUI/qSlicerActionsDialog.cxx`, `Base/QTGUI/qSlicerActionsDialog.h`
