# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLTableViewControllerWidget.ui

- Owner class: `qMRMLTableViewControllerWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLTableViewControllerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLTableViewControllerWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkPopupWidget`
- Search text: qMRMLTableViewControllerWidget | ctkPopupWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:41: #include "qMRMLTableViewControllerWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:52: // qMRMLTableViewControllerWidgetPrivate methods`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:55: qMRMLTableViewControllerWidgetPrivate::qMRMLTableViewControllerWidgetPrivate(qMRMLTableViewControllerWidget& object)`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:66: qMRMLTableViewControllerWidgetPrivate::~qMRMLTableViewControllerWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:69: void qMRMLTableViewControllerWidgetPrivate::setupPopupUi()`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:71: Q_Q(qMRMLTableViewControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:75: this->Ui_qMRMLTableViewControllerWidget::setupUi(this->PopupWidget);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:83: this->CopyAction->setToolTip(qMRMLTableViewControllerWidget::tr("Copy"));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:90: this->PasteAction->setToolTip(qMRMLTableViewControllerWidget::tr("Paste"));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:97: this->PlotAction->setToolTip(qMRMLTableViewControllerWidget::tr("Generate an Interactive Plot based on user-selection of the columns of the table."));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:127: void qMRMLTableViewControllerWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:136: void qMRMLTableViewControllerWidgetPrivate::onTableNodeSelected(vtkMRMLNode* node)`
- API footprints: `vtkMRMLTableViewNode::SafeDownCast`

## widget: tableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: tableComboBox | qMRMLNodeComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:101: this->connect(this->tableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onTableNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:121: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->tableComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:351: d->tableComboBox->setCurrentNodeID(tableNode ? tableNode->GetID() : nullptr);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:407: bool tableBlockSignals = d->tableComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:412: d->tableComboBox->blockSignals(tableBlockSignals);`
- Connected slots/functions: `onTableNodeSelected`, `setMRMLScene`
- API footprints: `GetID`, `GetPointer`, `SetTableNodeID`, `vtkMRMLScene::EndBatchProcessEvent`, `vtkMRMLTableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTableNode"]}

## widget: LockTableButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Allow table editing | LockTableButton | QPushButton
- Tooltip: Allow table editing
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:103: this->connect(this->LockTableButton, SIGNAL(clicked()), SLOT(onLockTableButtonClicked()));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:159: void qMRMLTableViewControllerWidgetPrivate::onLockTableButtonClicked()`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:163: qWarning("qMRMLTableViewControllerWidgetPrivate::onLockTableButtonClicked failed: tableNode is invalid");`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:356: d->LockTableButton->setEnabled(validNode);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:368: d->LockTableButton->setIcon(QIcon(":Icons/Medium/SlicerLock.png"));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:369: d->LockTableButton->setToolTip(tr("Click to unlock this table so that values can be modified"));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:373: d->LockTableButton->setIcon(QIcon(":Icons/Medium/SlicerUnlock.png"));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:374: d->LockTableButton->setToolTip(tr("Click to lock this table to prevent modification of the values in the user interface"));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h:75: void onLockTableButtonClicked();`
- Connected slots/functions: `onLockTableButtonClicked`
- API footprints: `GetLocked`, `SetLocked`
- Key UI properties: {"checkable": "false"}

## widget: CopyButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | Copy | CopyButton | QToolButton
- Text: ...
- Tooltip: Copy
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:113: this->CopyButton->setDefaultAction(this->CopyAction);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:357: d->CopyButton->setEnabled(validNode);`

## widget: PasteButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | Paste | PasteButton | QToolButton
- Text: ...
- Tooltip: Paste
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:115: this->PasteButton->setDefaultAction(this->PasteAction);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:358: d->PasteButton->setEnabled(editableNode);`

## widget: PlotButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Generate an Interactive Plot based on user-selection of the columns of the table. | PlotButton | QToolButton
- Tooltip: Generate an Interactive Plot based on user-selection of the columns of the table.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:117: this->PlotButton->setDefaultAction(this->PlotAction);`

## widget: EditControlsFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: EditControlsFrame | QFrame
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:359: d->EditControlsFrame->setEnabled(editableNode);`

## widget: ColumnInsertButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Add column | ColumnInsertButton | QToolButton
- Text: ...
- Tooltip: Add column
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:105: this->connect(this->ColumnInsertButton, SIGNAL(clicked()), SLOT(insertColumn()));`
- Connected slots/functions: `insertColumn`

## widget: ColumnDeleteButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Delete column | ColumnDeleteButton | QToolButton
- Text: ...
- Tooltip: Delete column
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:106: this->connect(this->ColumnDeleteButton, SIGNAL(clicked()), SLOT(deleteColumn()));`
- Connected slots/functions: `deleteColumn`

## widget: LockFirstColumnButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Lock first column | LockFirstColumnButton | QToolButton
- Text: ...
- Tooltip: Lock first column
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:110: this->connect(this->LockFirstColumnButton, SIGNAL(toggled(bool)), SLOT(setFirstColumnLocked(bool)));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:384: if (tableNode->GetUseFirstColumnAsRowHeader() != d->LockFirstColumnButton->isChecked())`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:386: bool wasBlocked = d->LockFirstColumnButton->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:387: d->LockFirstColumnButton->setChecked(tableNode->GetUseFirstColumnAsRowHeader());`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:388: d->LockFirstColumnButton->blockSignals(wasBlocked);`
- Connected slots/functions: `setFirstColumnLocked`
- API footprints: `GetUseFirstColumnAsRowHeader`
- Key UI properties: {"checkable": "true"}

## widget: RowInsertButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Add row | RowInsertButton | QToolButton
- Text: ...
- Tooltip: Add row
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:107: this->connect(this->RowInsertButton, SIGNAL(clicked()), SLOT(insertRow()));`
- Connected slots/functions: `insertRow`

## widget: RowDeleteButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Delete row | RowDeleteButton | QToolButton
- Text: ...
- Tooltip: Delete row
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:108: this->connect(this->RowDeleteButton, SIGNAL(clicked()), SLOT(deleteRow()));`
- Connected slots/functions: `deleteRow`

## widget: LockFirstRowButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Lock first row | LockFirstRowButton | QToolButton
- Text: ...
- Tooltip: Lock first row
- Implementation candidates: `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLTableViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:109: this->connect(this->LockFirstRowButton, SIGNAL(toggled(bool)), SLOT(setFirstRowLocked(bool)));`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:377: if (tableNode->GetUseColumnTitleAsColumnHeader() != d->LockFirstRowButton->isChecked())`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:379: bool wasBlocked = d->LockFirstRowButton->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:380: d->LockFirstRowButton->setChecked(tableNode->GetUseColumnTitleAsColumnHeader());`
  - `Libs/MRML/Widgets/qMRMLTableViewControllerWidget.cxx:381: d->LockFirstRowButton->blockSignals(wasBlocked);`
- Connected slots/functions: `setFirstRowLocked`
- API footprints: `GetUseColumnTitleAsColumnHeader`
- Key UI properties: {"checkable": "true", "checked": "true"}
