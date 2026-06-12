# Slicer UI Analysis: Modules/Loadable/Sequences/Widgets/Resources/UI/qMRMLSequenceEditWidget.ui

- Owner class: `qMRMLSequenceEditWidget`
- UI file: `Modules/Loadable/Sequences/Widgets/Resources/UI/qMRMLSequenceEditWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSequenceEditWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLSequenceEditWidget | QWidget
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:19: #include "qMRMLSequenceEditWidget.h"`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:20: #include "ui_qMRMLSequenceEditWidget.h"`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:43: class qMRMLSequenceEditWidgetPrivate : public Ui_qMRMLSequenceEditWidget`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:45: Q_DECLARE_PUBLIC(qMRMLSequenceEditWidget);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:48: qMRMLSequenceEditWidget* const q_ptr;`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:51: qMRMLSequenceEditWidgetPrivate(qMRMLSequenceEditWidget& object);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:73: // qMRMLSequenceEditWidgetPrivate methods`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:76: qMRMLSequenceEditWidgetPrivate::qMRMLSequenceEditWidgetPrivate(qMRMLSequenceEditWidget& object)`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:83: void qMRMLSequenceEditWidgetPrivate::init()`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:85: Q_Q(qMRMLSequenceEditWidget);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:121: void qMRMLSequenceEditWidgetPrivate::addNodeToCandidateNodes(vtkMRMLNode* node)`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:123: Q_Q(qMRMLSequenceEditWidget);`
- API footprints: `GetHideFromEditors`, `GetID`, `GetIndexType`, `IsBatchProcessing`, `vtkMRMLSequenceNode::NumericIndex`, `vtkMRMLSequenceNode::SafeDownCast`

## widget: GroupBox_Sequence

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: GroupBox_Sequence | QGroupBox
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`

## widget: label_IndexName

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Name: | label_IndexName | QLabel
- Text: Name:
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:139: d->label_IndexName->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:145: d->label_IndexName->setText(sequenceNode->GetIndexName().c_str());`
- API footprints: `GetIndexName`

## widget: LineEdit_IndexName

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: time | LineEdit_IndexName | QLineEdit
- Text: time
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:108: QObject::connect(this->LineEdit_IndexName, SIGNAL(textEdited(const QString&)), q, SLOT(onIndexNameEdited()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:309: d->LineEdit_IndexName->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:336: d->LineEdit_IndexName->setText(QString::fromStdString(d->SequenceNode->GetIndexName()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:553: d->SequenceNode->SetIndexName(d->LineEdit_IndexName->text().toStdString().c_str());`
- Connected slots/functions: `onIndexNameEdited`
- API footprints: `GetIndexName`, `GetIndexTypeAsString`, `GetIndexUnit`, `SetIndexName`

## widget: Label_IndexUnit

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Unit: | Label_IndexUnit | QLabel
- Text: Unit:
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`

## widget: LineEdit_IndexUnit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: s | LineEdit_IndexUnit | QLineEdit
- Text: s
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:109: QObject::connect(this->LineEdit_IndexUnit, SIGNAL(textEdited(const QString&)), q, SLOT(onIndexUnitEdited()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:310: d->LineEdit_IndexUnit->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:337: d->LineEdit_IndexUnit->setText(QString::fromStdString(d->SequenceNode->GetIndexUnit()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:564: d->SequenceNode->SetIndexUnit(d->LineEdit_IndexUnit->text().toStdString().c_str());`
- Connected slots/functions: `onIndexUnitEdited`
- API footprints: `GetIndexName`, `GetIndexTypeAsString`, `GetIndexUnit`, `SetIndexUnit`

## widget: label_IndexType

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Type: | label_IndexType | QLabel
- Text: Type:
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`

## widget: ComboBox_IndexType

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_IndexType | ctkComboBox
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:88: if (this->ComboBox_IndexType->count() == 0)`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:92: this->ComboBox_IndexType->addItem(vtkMRMLSequenceNode::GetIndexTypeAsString(indexType).c_str());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:110: QObject::connect(this->ComboBox_IndexType, SIGNAL(currentIndexChanged(const QString&)), q, SLOT(onIndexTypeEdited(QString)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:311: d->ComboBox_IndexType->setCurrentIndex(-1);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:338: d->ComboBox_IndexType->setCurrentIndex(d->ComboBox_IndexType->findText(QString::fromStdString(d->SequenceNode->GetIndexTypeAsString())));`
- Connected slots/functions: `onIndexTypeEdited`
- API footprints: `GetIndexName`, `GetIndexTypeAsString`, `GetIndexUnit`, `SetIndexTypeFromString`, `vtkMRMLSequenceNode::GetIndexTypeAsString`, `vtkMRMLSequenceNode::NumberOfIndexTypes`

## widget: GroupBox_SequenceNodes

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: GroupBox_SequenceNodes | QGroupBox
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`

## widget: TableWidget_DataNodes

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: TableWidget_DataNodes | QTableWidget
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:96: this->TableWidget_DataNodes->setColumnWidth(DATA_NODE_VALUE_COLUMN, 30);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:97: this->TableWidget_DataNodes->setColumnWidth(DATA_NODE_NAME_COLUMN, 100);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:111: QObject::connect(this->TableWidget_DataNodes, SIGNAL(cellChanged(int, int)), q, SLOT(onDataNodeEdited(int, int)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:233: QModelIndex modelIndex = this->TableWidget_DataNodes->model()->index(itemNumber, 0);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:234: this->TableWidget_DataNodes->scrollTo(modelIndex);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:235: this->TableWidget_DataNodes->setCurrentIndex(modelIndex);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:312: d->TableWidget_DataNodes->clear();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:313: d->TableWidget_DataNodes->setRowCount(0);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:314: d->TableWidget_DataNodes->setColumnCount(0);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:341: d->TableWidget_DataNodes->clear();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:342: d->TableWidget_DataNodes->setRowCount(d->SequenceNode->GetNumberOfDataNodes());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:343: d->TableWidget_DataNodes->setColumnCount(DATA_NODE_NUMBER_OF_COLUMNS);`
- Connected slots/functions: `onDataNodeEdited`
- API footprints: `GetDataNodeAtValue`, `GetID`, `GetIndexName`, `GetName`, `GetNthIndexValue`, `GetNumberOfDataNodes`, `SetName`, `UpdateIndexValue`

## widget: ExpandButton_DataNodes

- Confidence: `linked_to_slot`
- Widget/action class: `ctkExpandButton`
- Search text: ExpandButton_DataNodes | ctkExpandButton
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:102: QObject::connect(this->ExpandButton_DataNodes, SIGNAL(toggled(bool)), q, SLOT(setCandidateNodesSectionVisible(bool)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:115: this->ExpandButton_DataNodes->setChecked(false);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:756: QSignalBlocker blocker(d->ExpandButton_DataNodes);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:757: d->ExpandButton_DataNodes->setChecked(show);`
- Connected slots/functions: `setCandidateNodesSectionVisible`
- Key UI properties: {"checked": "true"}

## widget: GroupBox_CandidateNodes

- Confidence: `linked_to_code`
- Widget/action class: `QGroupBox`
- Search text: GroupBox_CandidateNodes | QGroupBox
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:759: d->GroupBox_CandidateNodes->setVisible(show);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:770: return d->GroupBox_CandidateNodes->isVisible();`

## widget: PushButton_AddCandidateNode

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Add to sequence items | PushButton_AddCandidateNode | QPushButton
- Tooltip: Add to sequence items
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:99: this->PushButton_AddCandidateNode->setIcon(QApplication::style()->standardIcon(QStyle::SP_ArrowLeft));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:112: QObject::connect(this->PushButton_AddCandidateNode, SIGNAL(clicked()), q, SLOT(onAddDataNodeButtonClicked()));`
- Connected slots/functions: `onAddDataNodeButtonClicked`
- API footprints: `GetNodeByID`, `GetScene`

## widget: DoubleSpinBox_IndexValueAutoIncrement

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Increment index by this much after adding a data node | DoubleSpinBox_IndexValueAutoIncrement | ctkDoubleSpinBox
- Tooltip: Increment index by this much after adding a data node
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:332: d->DoubleSpinBox_IndexValueAutoIncrement->setVisible(numericIndex);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:680: double incrementValue = d->DoubleSpinBox_IndexValueAutoIncrement->value();`
- API footprints: `GetIndexType`, `vtkMRMLSequenceNode::NumericIndex`

## widget: Label_UseNodeNameAsIndexValue

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Use node name: | Use node name as index value | Label_UseNodeNameAsIndexValue | QLabel
- Text: Use node name:
- Tooltip: Use node name as index value
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:333: d->Label_UseNodeNameAsIndexValue->setVisible(!numericIndex);`

## widget: Label_AutoAdvanceDataSelection

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Auto-advance: | If enabled then after the selected node is added to the sequence items the selection moves to the next item | Label_AutoAdvanceDataSelection | QLabel
- Text: Auto-advance:
- Tooltip: If enabled then after the selected node is added to the sequence items the selection moves to the next item
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`

## widget: CheckBox_AutoAdvanceDataSelection

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: If enabled then after the selected node is added to the sequence items the selection moves to the next item | CheckBox_AutoAdvanceDataSelection | QCheckBox
- Tooltip: If enabled then after the selected node is added to the sequence items the selection moves to the next item
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:642: if (d->CheckBox_AutoAdvanceDataSelection->checkState() == Qt::Checked)`
- Key UI properties: {"checked": "true"}

## widget: Label_IndexIncrement

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Index increment: | Increment index by this much after adding a data node | Label_IndexIncrement | QLabel
- Text: Index increment:
- Tooltip: Increment index by this much after adding a data node
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:331: d->Label_IndexIncrement->setVisible(numericIndex);`
- API footprints: `GetIndexType`, `vtkMRMLSequenceNode::NumericIndex`

## widget: Label_IndexValue

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Index value: | Label_IndexValue | QLabel
- Text: Index value:
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`

## widget: CheckBox_UseNodeNameAsIndexValue

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Use node name as index value | CheckBox_UseNodeNameAsIndexValue | QCheckBox
- Tooltip: Use node name as index value
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:334: d->CheckBox_UseNodeNameAsIndexValue->setVisible(!numericIndex);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:658: && d->CheckBox_UseNodeNameAsIndexValue->isChecked())`
- API footprints: `GetIndexName`, `GetIndexType`, `vtkMRMLSequenceNode::NumericIndex`
- Key UI properties: {"checked": "true"}

## widget: LineEdit_NewCandidateNodeIndexValue

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: 0 | LineEdit_NewCandidateNodeIndexValue | QLineEdit
- Text: 0
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:106: QObject::connect(LineEdit_NewCandidateNodeIndexValue, SIGNAL(returnPressed()), q, SLOT(onAddDataNodeButtonClicked()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:290: d->LineEdit_NewCandidateNodeIndexValue->setText("0");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:294: d->LineEdit_NewCandidateNodeIndexValue->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:615: std::string currentIndexValue = d->LineEdit_NewCandidateNodeIndexValue->text().toStdString();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:675: QString oldIndexValue = d->LineEdit_NewCandidateNodeIndexValue->text();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:682: d->LineEdit_NewCandidateNodeIndexValue->setText(newIndexValue);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:736: d->LineEdit_NewCandidateNodeIndexValue->setText(item->text());`
- Connected slots/functions: `onAddDataNodeButtonClicked`
- API footprints: `GetIndexType`, `GetNodeByID`, `GetScene`, `vtkMRMLSequenceNode::NumericIndex`

## widget: ListWidget_CandidateNodes

- Confidence: `linked_to_api`
- Widget/action class: `QListWidget`
- Search text: ListWidget_CandidateNodes | QListWidget
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:104: QObject::connect(this->ListWidget_CandidateNodes, SIGNAL(itemClicked(QListWidgetItem*)), q, SLOT(candidateNodeItemClicked(QListWidgetItem*)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:105: QObject::connect(this->ListWidget_CandidateNodes, SIGNAL(itemDoubleClicked(QListWidgetItem*)), q, SLOT(candidateNodeItemDoubleClicked(QListWidgetItem*)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:131: this->ListWidget_CandidateNodes->addItem(qlwi);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:170: this->ListWidget_CandidateNodes->setCurrentRow(-1);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:174: int rowCount = this->ListWidget_CandidateNodes->count();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:177: QListWidgetItem* item = this->ListWidget_CandidateNodes->item(row);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:184: this->ListWidget_CandidateNodes->setCurrentItem(item);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:190: this->ListWidget_CandidateNodes->setCurrentRow(-1);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:315: d->ListWidget_CandidateNodes->clear();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:386: d->ListWidget_CandidateNodes->clear();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:408: d->ListWidget_CandidateNodes->clear();`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:586: QList<QListWidgetItem*> selectedItems = d->ListWidget_CandidateNodes->selectedItems();`
- Connected slots/functions: `candidateNodeItemClicked`, `candidateNodeItemDoubleClicked`
- API footprints: `GetID`, `GetIndexType`, `GetName`, `vtkMRMLSequenceNode::NumericIndex`

## widget: PushButton_RemoveDataNode

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: PushButton_RemoveDataNode | QPushButton
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:100: this->PushButton_RemoveDataNode->setIcon(QIcon(":/Icons/DataNodeDelete.png"));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:113: QObject::connect(this->PushButton_RemoveDataNode, SIGNAL(clicked()), q, SLOT(onRemoveDataNodeButtonClicked()));`
- Connected slots/functions: `onRemoveDataNodeButtonClicked`
- API footprints: `EndModify`, `GetNthIndexValue`, `RemoveDataNodeAtValue`, `StartModify`

## widget: Label_DataNodeType

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Node type: | Label_DataNodeType | QLabel
- Text: Node type:
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:308: d->Label_DataNodeTypeValue->setText("-");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:328: d->Label_DataNodeTypeValue->setText(nodeType);`
- API footprints: `GetIndexType`, `vtkMRMLSequenceNode::NumericIndex`

## widget: Label_DataNodeTypeValue

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: - | Label_DataNodeTypeValue | QLabel
- Text: -
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:308: d->Label_DataNodeTypeValue->setText("-");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceEditWidget.cxx:328: d->Label_DataNodeTypeValue->setText(nodeType);`
- API footprints: `GetIndexType`, `vtkMRMLSequenceNode::NumericIndex`
