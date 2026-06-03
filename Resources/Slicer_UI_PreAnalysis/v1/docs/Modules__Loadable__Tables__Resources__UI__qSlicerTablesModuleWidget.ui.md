# Slicer UI Analysis: Modules/Loadable/Tables/Resources/UI/qSlicerTablesModuleWidget.ui

- Owner class: `qSlicerTablesModuleWidget`
- UI file: `Modules/Loadable/Tables/Resources/UI/qSlicerTablesModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTablesModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerTablesModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:32: #include "qSlicerTablesModuleWidget.h"`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:33: #include "ui_qSlicerTablesModuleWidget.h"`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:53: class qSlicerTablesModuleWidgetPrivate : public Ui_qSlicerTablesModuleWidget`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:55: Q_DECLARE_PUBLIC(qSlicerTablesModuleWidget);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:58: qSlicerTablesModuleWidget* const q_ptr;`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:61: qSlicerTablesModuleWidgetPrivate(qSlicerTablesModuleWidget& object);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:74: qSlicerTablesModuleWidgetPrivate::qSlicerTablesModuleWidgetPrivate(qSlicerTablesModuleWidget& object)`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:83: vtkSlicerTablesLogic* qSlicerTablesModuleWidgetPrivate::logic() const`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:85: Q_Q(const qSlicerTablesModuleWidget);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:90: vtkTable* qSlicerTablesModuleWidgetPrivate::table() const`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:100: qSlicerTablesModuleWidget::qSlicerTablesModuleWidget(QWidget* _parentWidget)`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:102: , d_ptr(new qSlicerTablesModuleWidgetPrivate(*this))`
- API footprints: `GetPointer`, `vtkMRMLTableNode::SafeDownCast`

## widget: TableNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: TableNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:140: this->connect(d->TableNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onNodeSelected(vtkMRMLNode*)));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:162: this->connect(d->TableNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->NewColumnPropertiesWidget, SLOT(setMRMLTableNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:251: d->TableNodeSelector->setCurrentNode(tableNode);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:263: d->TableNodeSelector->setCurrentNode(node);`
- Connected slots/functions: `onNodeSelected`, `setMRMLTableNode`
- API footprints: `vtkMRMLTableNode::GetDefaultColumnName`, `vtkMRMLTableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTableNode"]}

## widget: LockTableButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Allow table editing | LockTableButton | QPushButton
- Tooltip: Allow table editing
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:142: this->connect(d->LockTableButton, SIGNAL(clicked()), SLOT(onLockTableButtonClicked()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:196: d->LockTableButton->setEnabled(validNode);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:208: d->LockTableButton->setIcon(QIcon(":Icons/Medium/SlicerLock.png"));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:209: d->LockTableButton->setToolTip(tr("Click to unlock this table so that values can be modified"));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:213: d->LockTableButton->setIcon(QIcon(":Icons/Medium/SlicerUnlock.png"));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:214: d->LockTableButton->setToolTip(tr("Click to lock this table to prevent modification of the values in the user interface"));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:233: void qSlicerTablesModuleWidget::onLockTableButtonClicked()`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h:58: void onLockTableButtonClicked();`
- Connected slots/functions: `onLockTableButtonClicked`
- API footprints: `GetLocked`, `SetLocked`
- Key UI properties: {"checkable": "false"}

## widget: DisplayEditCollapsibleWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Edit | DisplayEditCollapsibleWidget | ctkCollapsibleButton
- Text: Edit
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:195: d->DisplayEditCollapsibleWidget->setEnabled(validNode);`
- API footprints: `GetLocked`
- Key UI properties: {"checked": "true"}

## widget: CopyButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | Copy | CopyButton | QToolButton
- Text: ...
- Tooltip: Copy
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:152: d->CopyButton->setDefaultAction(d->CopyAction);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:197: d->CopyButton->setEnabled(validNode);`

## widget: PasteButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | Paste | PasteButton | QToolButton
- Text: ...
- Tooltip: Paste
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:154: d->PasteButton->setDefaultAction(d->PasteAction);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:198: d->PasteButton->setEnabled(editableNode);`

## widget: EditControlsFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: EditControlsFrame | QFrame
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:199: d->EditControlsFrame->setEnabled(editableNode);`

## widget: PlotButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Generate an Interactive Plot based on user-selection of the columns of the table. The First (from left to right) Column will be used as X-Axis and each additional Column will be plotted in the same Chart as Y-Axis. | PlotButton | QToolButton
- Tooltip: Generate an Interactive Plot based on user-selection of the columns of the table. The First (from left to right) Column will be used as X-Axis and each additional Column will be plotted in the same Chart as Y-Axis.
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:156: d->PlotButton->setDefaultAction(d->PlotAction);`

## widget: ColumnInsertButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Add column | ColumnInsertButton | QToolButton
- Text: ...
- Tooltip: Add column
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:144: this->connect(d->ColumnInsertButton, SIGNAL(clicked()), d->TableView, SLOT(insertColumn()));`
- Connected slots/functions: `insertColumn`

## widget: ColumnDeleteButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Delete column | ColumnDeleteButton | QToolButton
- Text: ...
- Tooltip: Delete column
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:145: this->connect(d->ColumnDeleteButton, SIGNAL(clicked()), d->TableView, SLOT(deleteColumn()));`
- Connected slots/functions: `deleteColumn`

## widget: LockFirstColumnButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Lock first column | LockFirstColumnButton | QToolButton
- Text: ...
- Tooltip: Lock first column
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:149: this->connect(d->LockFirstColumnButton, SIGNAL(toggled(bool)), d->TableView, SLOT(setFirstColumnLocked(bool)));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:224: if (d->MRMLTableNode->GetUseFirstColumnAsRowHeader() != d->LockFirstColumnButton->isChecked())`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:226: bool wasBlocked = d->LockFirstColumnButton->blockSignals(true);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:227: d->LockFirstColumnButton->setChecked(d->MRMLTableNode->GetUseFirstColumnAsRowHeader());`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:228: d->LockFirstColumnButton->blockSignals(wasBlocked);`
- Connected slots/functions: `setFirstColumnLocked`
- API footprints: `GetUseFirstColumnAsRowHeader`
- Key UI properties: {"checkable": "true"}

## widget: RowInsertButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Add row | RowInsertButton | QToolButton
- Text: ...
- Tooltip: Add row
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:146: this->connect(d->RowInsertButton, SIGNAL(clicked()), d->TableView, SLOT(insertRow()));`
- Connected slots/functions: `insertRow`

## widget: RowDeleteButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: ... | Delete row | RowDeleteButton | QToolButton
- Text: ...
- Tooltip: Delete row
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:147: this->connect(d->RowDeleteButton, SIGNAL(clicked()), d->TableView, SLOT(deleteRow()));`
- Connected slots/functions: `deleteRow`

## widget: LockFirstRowButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Lock first row | LockFirstRowButton | QToolButton
- Text: ...
- Tooltip: Lock first row
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:148: this->connect(d->LockFirstRowButton, SIGNAL(toggled(bool)), d->TableView, SLOT(setFirstRowLocked(bool)));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:217: if (d->MRMLTableNode->GetUseColumnTitleAsColumnHeader() != d->LockFirstRowButton->isChecked())`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:219: bool wasBlocked = d->LockFirstRowButton->blockSignals(true);`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:220: d->LockFirstRowButton->setChecked(d->MRMLTableNode->GetUseColumnTitleAsColumnHeader());`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:221: d->LockFirstRowButton->blockSignals(wasBlocked);`
- Connected slots/functions: `setFirstRowLocked`
- API footprints: `GetUseColumnTitleAsColumnHeader`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: TableView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLTableView`
- Search text: TableView | qMRMLTableView
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:144: this->connect(d->ColumnInsertButton, SIGNAL(clicked()), d->TableView, SLOT(insertColumn()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:145: this->connect(d->ColumnDeleteButton, SIGNAL(clicked()), d->TableView, SLOT(deleteColumn()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:146: this->connect(d->RowInsertButton, SIGNAL(clicked()), d->TableView, SLOT(insertRow()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:147: this->connect(d->RowDeleteButton, SIGNAL(clicked()), d->TableView, SLOT(deleteRow()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:148: this->connect(d->LockFirstRowButton, SIGNAL(toggled(bool)), d->TableView, SLOT(setFirstRowLocked(bool)));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:149: this->connect(d->LockFirstColumnButton, SIGNAL(toggled(bool)), d->TableView, SLOT(setFirstColumnLocked(bool)));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:153: this->connect(d->CopyAction, SIGNAL(triggered()), d->TableView, SLOT(copySelection()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:155: this->connect(d->PasteAction, SIGNAL(triggered()), d->TableView, SLOT(pasteSelection()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:157: this->connect(d->PlotAction, SIGNAL(triggered()), d->TableView, SLOT(plotSelection()));`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:159: d->SelectedColumnPropertiesWidget->setSelectionFromMRMLTableView(d->TableView);`
- Connected slots/functions: `copySelection`, `deleteColumn`, `deleteRow`, `insertColumn`, `insertRow`, `pasteSelection`, `plotSelection`, `setFirstColumnLocked`, `setFirstRowLocked`
- API footprints: `vtkMRMLTableNode::GetDefaultColumnName`

## widget: SelectedColumnPropertiesCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Column properties | SelectedColumnPropertiesCollapsibleButton | ctkCollapsibleButton
- Text: Column properties
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`

## widget: SelectedColumnPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerTableColumnPropertiesWidget`
- Search text: SelectedColumnPropertiesWidget | qSlicerTableColumnPropertiesWidget
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:159: d->SelectedColumnPropertiesWidget->setSelectionFromMRMLTableView(d->TableView);`
- API footprints: `vtkMRMLTableNode::GetDefaultColumnName`

## widget: NewColumnPropertiesCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: New column defaults | NewColumnPropertiesCollapsibleButton | ctkCollapsibleButton
- Text: New column defaults
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`

## widget: NewColumnPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerTableColumnPropertiesWidget`
- Search text: NewColumnPropertiesWidget | qSlicerTableColumnPropertiesWidget
- Implementation candidates: `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx`, `Modules/Loadable/Tables/qSlicerTablesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:161: d->NewColumnPropertiesWidget->setMRMLTableColumnName(vtkMRMLTableNode::GetDefaultColumnName());`
  - `Modules/Loadable/Tables/qSlicerTablesModuleWidget.cxx:162: this->connect(d->TableNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->NewColumnPropertiesWidget, SLOT(setMRMLTableNode(vtkMRMLNode*)));`
- Connected slots/functions: `setMRMLTableNode`
- API footprints: `vtkMRMLTableNode::GetDefaultColumnName`
