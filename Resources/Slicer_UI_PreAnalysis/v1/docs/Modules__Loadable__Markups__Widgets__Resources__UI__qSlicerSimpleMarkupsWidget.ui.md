# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qSlicerSimpleMarkupsWidget.ui

- Owner class: `qSlicerSimpleMarkupsWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qSlicerSimpleMarkupsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSimpleMarkupsWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSimpleMarkupsWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:22: #include "qSlicerSimpleMarkupsWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:23: #include "ui_qSlicerSimpleMarkupsWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:53: class qSlicerSimpleMarkupsWidgetPrivate : public Ui_qSlicerSimpleMarkupsWidget`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:55: Q_DECLARE_PUBLIC(qSlicerSimpleMarkupsWidget);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:58: qSlicerSimpleMarkupsWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:61: qSlicerSimpleMarkupsWidgetPrivate(qSlicerSimpleMarkupsWidget& object);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:62: ~qSlicerSimpleMarkupsWidgetPrivate();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:63: virtual void setupUi(qSlicerSimpleMarkupsWidget*);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:85: qSlicerSimpleMarkupsWidgetPrivate::qSlicerSimpleMarkupsWidgetPrivate(qSlicerSimpleMarkupsWidget& object)`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:99: qSlicerSimpleMarkupsWidgetPrivate::~qSlicerSimpleMarkupsWidgetPrivate() = default;`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:102: void qSlicerSimpleMarkupsWidgetPrivate::setupUi(qSlicerSimpleMarkupsWidget* widget)`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:104: this->Ui_qSlicerSimpleMarkupsWidget::setupUi(widget);`
- API footprints: `vtkMRMLMarkupsNode::SafeDownCast`

## widget: MarkupsNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MarkupsNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:181: connect(d->MarkupsNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onMarkupsNodeChanged()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:182: connect(d->MarkupsNodeComboBox, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), this, SLOT(onMarkupsNodeAdded(vtkMRMLNode*)));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:209: return d->MarkupsNodeComboBox->currentNode();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:232: bool wasBlocked = d->MarkupsNodeComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:233: d->MarkupsNodeComboBox->setCurrentNode(currentMarkupsNode);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:234: d->MarkupsNodeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:270: d->MarkupsNodeComboBox->setBaseName(newNodeBaseName);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:319: return d->MarkupsNodeComboBox->isVisible();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:326: d->MarkupsNodeComboBox->setVisible(visible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:437: vtkMRMLMarkupsNode* currentMarkupsNode = vtkMRMLMarkupsNode::SafeDownCast(d->MarkupsNodeComboBox->currentNode());`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:462: d->MarkupsNodeComboBox->setCurrentNode(newMarkupsNode);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:494: vtkMRMLMarkupsNode* currentNode = vtkMRMLMarkupsNode::SafeDownCast(d->MarkupsNodeComboBox->currentNode());`
- Connected slots/functions: `onMarkupsNodeAdded`, `onMarkupsNodeChanged`
- API footprints: `AddNewDisplayNodeForMarkupsNode`, `GetDisplayNode`, `vtkMRMLMarkupsNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLMarkupsFiducialNode"]}

## widget: MarkupsPlaceWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerMarkupsPlaceWidget`
- Search text: MarkupsPlaceWidget | qSlicerMarkupsPlaceWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:183: connect(d->MarkupsPlaceWidget, SIGNAL(activeMarkupsPlaceModeChanged(bool)), this, SIGNAL(activeMarkupsPlaceModeChanged(bool)));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:236: d->MarkupsPlaceWidget->setCurrentNode(currentMarkupsNode);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:256: return d->MarkupsPlaceWidget->interactionNode();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:263: d->MarkupsPlaceWidget->setInteractionNode(interactionNode);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:277: d->MarkupsPlaceWidget->setDefaultNodeColor(color);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:284: return d->MarkupsPlaceWidget->defaultNodeColor();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:333: return d->MarkupsPlaceWidget->isVisible();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:340: d->MarkupsPlaceWidget->setVisible(visible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:354: d->MarkupsPlaceWidget->setNodeColor(color);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:361: return d->MarkupsPlaceWidget->nodeColor();`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:423: d->MarkupsPlaceWidget->setCurrentNodeActive(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:430: d->MarkupsPlaceWidget->setPlaceModeEnabled(place);`
- API footprints: `ResetNthControlPointPosition`, `vtkMRMLMarkupsNode::PositionPreview`

## widget: MarkupsControlPointsTableWidget

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: MarkupsControlPointsTableWidget | QTableWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:112: this->MarkupsControlPointsTableWidget->setHorizontalHeaderLabels(QStringList() << q->tr("Label") << q->tr("R") //: right`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:117: this->MarkupsControlPointsTableWidget->horizontalHeader()->setSectionResizeMode(CONTROL_POINT_LABEL_COLUMN, QHeaderView::Stretch);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:118: this->MarkupsControlPointsTableWidget->horizontalHeader()->setSectionResizeMode(CONTROL_POINT_X_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:119: this->MarkupsControlPointsTableWidget->horizontalHeader()->setSectionResizeMode(CONTROL_POINT_Y_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:120: this->MarkupsControlPointsTableWidget->horizontalHeader()->setSectionResizeMode(CONTROL_POINT_Z_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:121: this->MarkupsControlPointsTableWidget->horizontalHeader()->setSectionResizeMode(CONTROL_POINT_STATE_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:124: QTableWidgetItem* positionHeader = this->MarkupsControlPointsTableWidget->horizontalHeaderItem(CONTROL_POINT_STATE_COLUMN);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:131: this->MarkupsControlPointsTableWidget->setColumnHidden(CONTROL_POINT_STATE_COLUMN, !this->PositionStatusColumnVisible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:185: d->MarkupsControlPointsTableWidget->setColumnCount(CONTROL_POINT_COLUMNS);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:189: d->MarkupsControlPointsTableWidget->setWordWrap(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:190: d->MarkupsControlPointsTableWidget->verticalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:192: d->MarkupsControlPointsTableWidget->setContextMenuPolicy(Qt::CustomContextMenu);`
- Connected slots/functions: `onMarkupsControlPointClicked`, `onMarkupsControlPointEdited`, `onMarkupsControlPointSelected`, `onMarkupsControlPointsTableContextMenu`
- API footprints: `EndModify`, `GetID`, `GetNthControlPointLabel`, `GetNthControlPointPosition`, `GetNumberOfControlPoints`, `JumpSlicesToNthPointInMarkup`, `RemoveNthControlPoint`, `ResetNthControlPointPosition`, `RestoreNthControlPointPosition`, `SetNthControlPointLabel`, `SetNthControlPointPosition`, `SetNthControlPointPositionMissing`, `StartModify`, `SwapControlPoints`, `UnsetNthControlPointPosition`, `vtkMRMLMarkupsNode::PositionDefined`, `vtkMRMLMarkupsNode::PositionMissing`, `vtkMRMLMarkupsNode::PositionPreview`, `vtkMRMLMarkupsNode::PositionUndefined`, `vtkMRMLMarkupsNode::SafeDownCast`
