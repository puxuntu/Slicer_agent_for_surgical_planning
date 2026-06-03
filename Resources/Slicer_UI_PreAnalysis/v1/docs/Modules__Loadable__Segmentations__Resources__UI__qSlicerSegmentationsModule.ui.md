# Slicer UI Analysis: Modules/Loadable/Segmentations/Resources/UI/qSlicerSegmentationsModule.ui

- Owner class: `qSlicerSegmentationsModule`
- UI file: `Modules/Loadable/Segmentations/Resources/UI/qSlicerSegmentationsModule.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSegmentationsModule

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSegmentationsModule | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:22: #include "qSlicerSegmentationsModule.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:23: #include "qSlicerSegmentationsModuleWidget.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:71: class qSlicerSegmentationsModulePrivate`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:74: qSlicerSegmentationsModulePrivate();`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:78: // qSlicerSegmentationsModulePrivate methods`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:81: qSlicerSegmentationsModulePrivate::qSlicerSegmentationsModulePrivate() = default;`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:84: // qSlicerSegmentationsModule methods`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:87: qSlicerSegmentationsModule::qSlicerSegmentationsModule(QObject* _parent)`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:89: , d_ptr(new qSlicerSegmentationsModulePrivate)`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:94: qSlicerSegmentationsModule::~qSlicerSegmentationsModule() = default;`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:97: QString qSlicerSegmentationsModule::helpText() const`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx:109: QString qSlicerSegmentationsModule::acknowledgementText() const`
- API footprints: `IsBatchProcessing`, `vtkMRMLScene::SafeDownCast`, `vtkMRMLSegmentationNode::SafeDownCast`, `vtkMRMLSubjectHierarchyNode::GetSubjectHierarchyNode`

## widget: ResizableFrame_2

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame_2 | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: MRMLNodeSelector_Segmentation

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: MRMLNodeSelector_Segmentation | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:185: if (!d->MRMLNodeSelector_Segmentation->currentNode())`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:187: vtkMRMLNode* node = d->MRMLNodeSelector_Segmentation->findFirstNodeByClass("vtkMRMLSegmentationNode");`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:190: d->MRMLNodeSelector_Segmentation->setCurrentNode(node);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:194: this->onSegmentationNodeChanged(d->MRMLNodeSelector_Segmentation->currentNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:210: vtkMRMLSegmentationNode* segmentationNode = vtkMRMLSegmentationNode::SafeDownCast(d->MRMLNodeSelector_Segmentation->currentNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:289: vtkMRMLSegmentationNode* currentSegmentationNode = vtkMRMLSegmentationNode::SafeDownCast(d->MRMLNodeSelector_Segmentation->currentNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:317: d->MRMLNodeSelector_Segmentation->setNodeTypeLabel(segmentationNodeLabel, "vtkMRMLSegmentationNode");`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:323: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onSegmentationNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:324: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->SegmentsTableView, SLOT(setSegmentationNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:325: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->SegmentsTableView_Current, SLOT(setSegmentationNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:326: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->RepresentationsListView, SLOT(setSegmentationNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:346: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->ExportToFilesWidget, SLOT(setSegmentationNode(vtkMRMLNode*)));`
- Connected slots/functions: `onSegmentationNodeChanged`, `setSegmentationNode`
- API footprints: `CreateDefaultDisplayNodes`, `GetNumberOfSegments`, `GetSegmentation`, `IsBatchProcessing`, `vtkMRMLDisplayableNode::DisplayModifiedEvent`, `vtkMRMLNode::ReferenceAddedEvent`, `vtkMRMLNode::ReferenceModifiedEvent`, `vtkMRMLSegmentationNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSegmentationNode"]}

## widget: label_ReferenceVolumeName

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: label_ReferenceVolumeName | QLabel
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1175: d->label_ReferenceVolumeName->setVisible(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1176: d->label_ReferenceVolumeName->setText(referenceVolumeNode->GetName());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1183: d->label_ReferenceVolumeName->setVisible(false);`
- API footprints: `GetName`

## widget: label_ReferenceVolumeText

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text:  Source geometry: | Node that was used for setting the segmentation geometry (origin, spacing, axis directions, and default extent) | label_ReferenceVolumeText | QLabel
- Text:  Source geometry:
- Tooltip: Node that was used for setting the segmentation geometry (origin, spacing, axis directions, and default extent)
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1174: d->label_ReferenceVolumeText->setVisible(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1182: d->label_ReferenceVolumeText->setVisible(false);`
- API footprints: `GetName`

## widget: ResizableFrame

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: pushButton_AddSegment

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Add segment | Add empty segment | pushButton_AddSegment | QPushButton
- Text: Add segment
- Tooltip: Add empty segment
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:329: connect(d->pushButton_AddSegment, SIGNAL(clicked()), this, SLOT(onAddSegment()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:423: d->pushButton_AddSegment->setEnabled(d->SegmentationNode != nullptr);`
- Connected slots/functions: `onAddSegment`
- API footprints: `AddEmptySegment`, `GetNthSegment`, `GetNumberOfSegments`, `GetSegment`, `GetSegmentation`, `GetTerminology`, `SetTerminology`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: pushButton_RemoveSelected

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Remove selected | Remove selected segment | pushButton_RemoveSelected | QPushButton
- Text: Remove selected
- Tooltip: Remove selected segment
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:331: connect(d->pushButton_RemoveSelected, SIGNAL(clicked()), this, SLOT(onRemoveSelectedSegments()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:427: d->pushButton_RemoveSelected->setEnabled(selectedSegmentIds.count() > 0);`
- Connected slots/functions: `onRemoveSelectedSegments`
- API footprints: `GetSegmentation`, `RemoveSegment`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: show3DButton

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLSegmentationShow3DButton`
- Search text: show3DButton | qMRMLSegmentationShow3DButton
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:250: d->show3DButton->setSegmentationNode(d->SegmentationNode);`

## widget: toolButton_Edit

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Go to Segment Editor module | toolButton_Edit | QToolButton
- Text: ...
- Tooltip: Go to Segment Editor module
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:330: connect(d->toolButton_Edit, SIGNAL(clicked()), this, SLOT(onEditSegmentation()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:426: d->toolButton_Edit->setEnabled(d->SegmentationNode != nullptr);`
- Connected slots/functions: `onEditSegmentation`
- API footprints: `vtkMRMLSegmentationNode::SafeDownCast`

## widget: SegmentsTableView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSegmentsTableView`
- Search text: SegmentsTableView | qMRMLSegmentsTableView
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:31: #include "qMRMLSegmentsTableView.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:280: vtkMRMLSegmentationNode* otherSegmentationNode = vtkMRMLSegmentationNode::SafeDownCast(d->SegmentsTableView_Other->segmentationNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:324: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->SegmentsTableView, SLOT(setSegmentationNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:325: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->SegmentsTableView_Current, SLOT(setSegmentationNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:328: connect(d->SegmentsTableView, SIGNAL(selectionChanged(QItemSelection, QItemSelection)), this, SLOT(onSegmentSelectionChanged(QItemSelection, QItemSelection)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:357: d->SegmentsTableView_Current->setSelectionMode(QAbstractItemView::ExtendedSelection);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:358: d->SegmentsTableView_Current->setHeaderVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:359: d->SegmentsTableView_Current->setVisibilityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:360: d->SegmentsTableView_Current->setColorColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:361: d->SegmentsTableView_Current->setOpacityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:362: d->SegmentsTableView_Current->setStatusColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:364: d->SegmentsTableView_Other->setSelectionMode(QAbstractItemView::ExtendedSelection);`
- Connected slots/functions: `onSegmentSelectionChanged`, `setSegmentationNode`
- API footprints: `AddEmptySegment`, `CreateDefaultDisplayNodes`, `GetSegmentation`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: CollapsibleButton_Display

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display | Display settings for the segmentation (all segments) | CollapsibleButton_Display | ctkCollapsibleButton
- Text: Display
- Tooltip: Display settings for the segmentation (all segments)
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: SegmentationDisplayNodeWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLSegmentationDisplayNodeWidget`
- Search text: SegmentationDisplayNodeWidget | qMRMLSegmentationDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:247: d->SegmentationDisplayNodeWidget->setSegmentationNode(d->SegmentationNode);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:248: d->SegmentationDisplayNodeWidget->updateWidgetFromMRML();`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:404: d->SegmentationDisplayNodeWidget->setSegmentationNode(segmentationNode);`

## widget: CollapsibleButton_Representations

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Representations | List of representations to see available and existing ones, and creating or updating them | CollapsibleButton_Representations | ctkCollapsibleButton
- Text: Representations
- Tooltip: List of representations to see available and existing ones, and creating or updating them
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: RepresentationsListView

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSegmentationRepresentationsListView`
- Search text: RepresentationsListView | qMRMLSegmentationRepresentationsListView
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:32: #include "qMRMLSegmentationRepresentationsListView.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:305: d->RepresentationsListView->setMinimumHeight(108);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:326: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->RepresentationsListView, SLOT(setSegmentationNode(vtkMRMLNode*)));`
- Connected slots/functions: `setSegmentationNode`

## widget: CollapsibleButton_CopyMoveSegment

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Copy/move segments | CollapsibleButton_CopyMoveSegment | ctkCollapsibleButton
- Text: Copy/move segments
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Key UI properties: {"checked": "false"}

## widget: label_CurrentSegmentation_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Current segmentation | label_CurrentSegmentation_2 | QLabel
- Text: Current segmentation
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: SegmentsTableView_Current

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSegmentsTableView`
- Search text: SegmentsTableView_Current | qMRMLSegmentsTableView
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:325: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->SegmentsTableView_Current, SLOT(setSegmentationNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:357: d->SegmentsTableView_Current->setSelectionMode(QAbstractItemView::ExtendedSelection);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:358: d->SegmentsTableView_Current->setHeaderVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:359: d->SegmentsTableView_Current->setVisibilityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:360: d->SegmentsTableView_Current->setColorColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:361: d->SegmentsTableView_Current->setOpacityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:362: d->SegmentsTableView_Current->setStatusColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:822: selectedSegmentIds = d->SegmentsTableView_Current->selectedSegmentIDs();`
- Connected slots/functions: `setSegmentationNode`
- API footprints: `CreateDefaultDisplayNodes`, `GetSegmentation`

## widget: toolButton_MoveFromCurrentSegmentation

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: > | Move from current segmentation to other Segmentation node | toolButton_MoveFromCurrentSegmentation | QToolButton
- Text: >
- Tooltip: Move from current segmentation to other Segmentation node
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:274: d->toolButton_MoveFromCurrentSegmentation->setEnabled(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:292: d->toolButton_MoveFromCurrentSegmentation->setEnabled(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:348: connect(d->toolButton_MoveFromCurrentSegmentation, SIGNAL(clicked()), this, SLOT(onMoveFromCurrentSegmentation()));`
- Connected slots/functions: `onMoveFromCurrentSegmentation`
- API footprints: `GetNumberOfSegments`, `GetSegmentation`

## widget: toolButton_CopyFromCurrentSegmentation

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: +> | Copy from current segmentation to other node (Segmentation node for copy and Model or Labelmap node for import/export) | toolButton_CopyFromCurrentSegmentation | QToolButton
- Text: +>
- Tooltip: Copy from current segmentation to other node (Segmentation node for copy and Model or Labelmap node for import/export)
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:275: d->toolButton_CopyFromCurrentSegmentation->setEnabled(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:293: d->toolButton_CopyFromCurrentSegmentation->setEnabled(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:349: connect(d->toolButton_CopyFromCurrentSegmentation, SIGNAL(clicked()), this, SLOT(onCopyFromCurrentSegmentation()));`
- Connected slots/functions: `onCopyFromCurrentSegmentation`

## widget: toolButton_CopyToCurrentSegmentation

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: <+ | Copy to current segmentation from other node (Segmentation node for copy and Model or Labelmap node for import/export) | toolButton_CopyToCurrentSegmentation | QToolButton
- Text: <+
- Tooltip: Copy to current segmentation from other node (Segmentation node for copy and Model or Labelmap node for import/export)
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:276: d->toolButton_CopyToCurrentSegmentation->setEnabled(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:284: d->toolButton_CopyToCurrentSegmentation->setEnabled(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:350: connect(d->toolButton_CopyToCurrentSegmentation, SIGNAL(clicked()), this, SLOT(onCopyToCurrentSegmentation()));`
- Connected slots/functions: `onCopyToCurrentSegmentation`

## widget: toolButton_MoveToCurrentSegmentation

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: < | Move to current segmentation from other Segmentation node | toolButton_MoveToCurrentSegmentation | QToolButton
- Text: <
- Tooltip: Move to current segmentation from other Segmentation node
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:277: d->toolButton_MoveToCurrentSegmentation->setEnabled(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:285: d->toolButton_MoveToCurrentSegmentation->setEnabled(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:351: connect(d->toolButton_MoveToCurrentSegmentation, SIGNAL(clicked()), this, SLOT(onMoveToCurrentSegmentation()));`
- Connected slots/functions: `onMoveToCurrentSegmentation`

## widget: MRMLNodeComboBox_OtherSegmentationOrRepresentationNode

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select Segmentation node to copy/move segments to/from. | MRMLNodeComboBox_OtherSegmentationOrRepresentationNode | qMRMLNodeComboBox
- Tooltip: Select Segmentation node to copy/move segments to/from.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:244: d->MRMLNodeComboBox_OtherSegmentationOrRepresentationNode->sortFilterProxyModel()->setHiddenNodeIDs(hiddenNodeIDs);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:318: d->MRMLNodeComboBox_OtherSegmentationOrRepresentationNode->setNodeTypeLabel(segmentationNodeLabel, "vtkMRMLSegmentationNode");`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:333: connect(d->MRMLNodeComboBox_OtherSegmentationOrRepresentationNode, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(setOtherSegmentationOrRepresentationNode(vtkMRMLNode*)));`
- Connected slots/functions: `setOtherSegmentationOrRepresentationNode`
- API footprints: `GetID`, `vtkMRMLSegmentationNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSegmentationNode"]}

## widget: SegmentsTableView_Other

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSegmentsTableView`
- Search text: SegmentsTableView_Other | qMRMLSegmentsTableView
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:280: vtkMRMLSegmentationNode* otherSegmentationNode = vtkMRMLSegmentationNode::SafeDownCast(d->SegmentsTableView_Other->segmentationNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:364: d->SegmentsTableView_Other->setSelectionMode(QAbstractItemView::ExtendedSelection);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:365: d->SegmentsTableView_Other->setHeaderVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:366: d->SegmentsTableView_Other->setVisibilityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:367: d->SegmentsTableView_Other->setColorColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:368: d->SegmentsTableView_Other->setOpacityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:369: d->SegmentsTableView_Other->setStatusColumnVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:556: d->SegmentsTableView_Other->setSegmentationNode(segmentationNode);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:806: vtkMRMLSegmentationNode* otherSegmentationNode = vtkMRMLSegmentationNode::SafeDownCast(d->SegmentsTableView_Other->segmentationNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:829: selectedSegmentIds = d->SegmentsTableView_Other->selectedSegmentIDs();`
- API footprints: `CreateDefaultDisplayNodes`, `GetSegmentation`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: CollapsibleButton_ImportExportSegment

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Export/import models and labelmaps | CollapsibleButton_ImportExportSegment | ctkCollapsibleButton
- Text: Export/import models and labelmaps
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:307: d->ImportExportOperationButtonGroup = new QButtonGroup(d->CollapsibleButton_ImportExportSegment);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:311: d->ImportExportTypeButtonGroup = new QButtonGroup(d->CollapsibleButton_ImportExportSegment);`
- Key UI properties: {"checked": "true"}

## widget: SubjectHierarchyComboBox_ImportExport

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyComboBox`
- Search text: SubjectHierarchyComboBox_ImportExport | qMRMLSubjectHierarchyComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:642: d->SubjectHierarchyComboBox_ImportExport->setDefaultText(tr("Export to new labelmap"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:650: d->SubjectHierarchyComboBox_ImportExport->setDefaultText(tr("Export models to new folder"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:660: d->SubjectHierarchyComboBox_ImportExport->setNodeTypes(nodeTypes);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:661: d->SubjectHierarchyComboBox_ImportExport->setLevelFilter(levelFilter);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:715: d->SubjectHierarchyComboBox_ImportExport->clearSelection();`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:911: vtkIdType selectedItem = d->SubjectHierarchyComboBox_ImportExport->currentItem();`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1025: vtkIdType selectedItem = d->SubjectHierarchyComboBox_ImportExport->currentItem();`
- API footprints: `vtkMRMLSubjectHierarchyConstants::GetDICOMLevelStudy`, `vtkMRMLSubjectHierarchyConstants::GetSubjectHierarchyLevelFolder`, `vtkMRMLSubjectHierarchyNode::INVALID_ITEM_ID`

## widget: pushButton_ClearSelection

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Clear selection indicating that a new node should be created | pushButton_ClearSelection | QPushButton
- Tooltip: Clear selection indicating that a new node should be created
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:340: connect(d->pushButton_ClearSelection, SIGNAL(clicked()), this, SLOT(onImportExportClearSelection()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:632: d->pushButton_ClearSelection->setVisible(d->radioButton_Export->isChecked());`
- Connected slots/functions: `onImportExportClearSelection`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Operation: | label | QLabel
- Text: Operation:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:88: /// Model/labelmap buttons`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:264: // Update source volume label and combobox for export`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:315: // Define node type labels`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:594: d->label_SegmentCountValue->setText(QString::fromStdString(segmentCountSS.str()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:605: d->label_LayerCountValue->setText(QString::fromStdString(layerCountSS.str()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:616: d->label_ImportExportType->setText(tr("Output type:"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:617: d->label_ImportExportNode->setText(tr("Output node:"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:619: d->label_TerminologyContext->setVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:624: d->label_ImportExportType->setText(tr("Input type:"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:625: d->label_ImportExportNode->setText(tr("Input node:"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:627: d->label_TerminologyContext->setVisible(d->radioButton_Labelmap->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:634: // Type: labelmap/model`
- API footprints: `CreateDefaultDisplayNodes`, `CreateNodeByClass`, `GetItemDataNode`, `GetName`, `GetNodeReference`, `GetNumberOfLayers`, `GetNumberOfSegments`, `GetScene`, `GetSegment`, `GetSegmentation`, `ImportLabelmapToSegmentationNodeWithTerminology`, `vtkMRMLLabelMapVolumeNode::SafeDownCast`, `vtkMRMLModelNode::SafeDownCast`, `vtkMRMLSegmentationNode::GetReferenceImageGeometryReferenceRole`, `vtkMRMLSubjectHierarchyNode::INVALID_ITEM_ID`

## widget: radioButton_Labelmap

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Labelmap | radioButton_Labelmap | QRadioButton
- Text: Labelmap
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:312: d->ImportExportTypeButtonGroup->addButton(d->radioButton_Labelmap);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:372: d->radioButton_Labelmap->setChecked(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:627: d->label_TerminologyContext->setVisible(d->radioButton_Labelmap->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:628: d->ComboBox_TerminologyContext->setVisible(d->radioButton_Labelmap->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:631: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setEnabled(d->radioButton_Labelmap->isChecked() && d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:637: if (d->radioButton_Labelmap->isChecked())`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:663: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setEnabled(d->radioButton_Labelmap->isChecked() && d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:923: if (d->radioButton_Labelmap->isChecked() && !labelmapNode)`
- API footprints: `GetItemDataNode`, `vtkMRMLLabelMapVolumeNode::SafeDownCast`
- Key UI properties: {"checked": "true"}

## widget: radioButton_Model

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Models | radioButton_Model | QRadioButton
- Text: Models
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:313: d->ImportExportTypeButtonGroup->addButton(d->radioButton_Model);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:949: if (d->radioButton_Model->isChecked() && !folderItem)`
- API footprints: `GetName`

## widget: label_ImportExportType

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Type: | label_ImportExportType | QLabel
- Text: Type:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:616: d->label_ImportExportType->setText(tr("Output type:"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:624: d->label_ImportExportType->setText(tr("Input type:"));`

## widget: label_ImportExportNode

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Output: | label_ImportExportNode | QLabel
- Text: Output:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:617: d->label_ImportExportNode->setText(tr("Output node:"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:625: d->label_ImportExportNode->setText(tr("Input node:"));`

## widget: PushButton_ImportExport

- Confidence: `linked_to_slot`
- Widget/action class: `ctkPushButton`
- Search text: Apply | PushButton_ImportExport | ctkPushButton
- Text: Apply
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:339: connect(d->PushButton_ImportExport, SIGNAL(clicked()), this, SLOT(onImportExportApply()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:618: d->PushButton_ImportExport->setText(tr("Export"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:626: d->PushButton_ImportExport->setText(tr("Import"));`
- Connected slots/functions: `onImportExportApply`

## widget: radioButton_Export

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Export | radioButton_Export | QRadioButton
- Text: Export
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:308: d->ImportExportOperationButtonGroup->addButton(d->radioButton_Export);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:371: d->radioButton_Export->setChecked(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:614: if (d->radioButton_Export->isChecked())`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:630: d->ComboBox_ExportedSegments->setEnabled(d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:631: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setEnabled(d->radioButton_Labelmap->isChecked() && d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:632: d->pushButton_ClearSelection->setVisible(d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:640: if (d->radioButton_Export->isChecked())`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:647: if (d->radioButton_Export->isChecked())`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:663: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setEnabled(d->radioButton_Labelmap->isChecked() && d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:701: if (d->radioButton_Export->isChecked())`

## widget: radioButton_Import

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Import | radioButton_Import | QRadioButton
- Text: Import
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:309: d->ImportExportOperationButtonGroup->addButton(d->radioButton_Import);`

## widget: CollapsibleGroupBox_ImporExportAdvanced

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_ImporExportAdvanced | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Exported segments: | label_4 | QLabel
- Text: Exported segments:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: ComboBox_ExportedSegments

- Confidence: `linked_to_code`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_ExportedSegments | ctkComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:630: d->ComboBox_ExportedSegments->setEnabled(d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:869: if (d->ComboBox_ExportedSegments->currentIndex() == 0)`

## widget: label_6

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Reference volume: | Exported labelmap geometry will match this volume's geometry | label_6 | QLabel
- Text: Reference volume:
- Tooltip: Exported labelmap geometry will match this volume's geometry
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: MRMLNodeComboBox_ExportLabelmapReferenceVolume

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Exported labelmap geometry will match this volume's geometry | MRMLNodeComboBox_ExportLabelmapReferenceVolume | qMRMLNodeComboBox
- Tooltip: Exported labelmap geometry will match this volume's geometry
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:319: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setNodeTypeLabel(tr("Volume"), "vtkMRMLVolumeNode");`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:631: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setEnabled(d->radioButton_Labelmap->isChecked() && d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:663: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setEnabled(d->radioButton_Labelmap->isChecked() && d->radioButton_Export->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:881: vtkMRMLVolumeNode* referenceVolumeNode = vtkMRMLVolumeNode::SafeDownCast(d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->currentNode());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1178: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setCurrentNode(referenceVolumeNode);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1184: d->MRMLNodeComboBox_ExportLabelmapReferenceVolume->setCurrentNode(nullptr);`
- API footprints: `GetName`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}

## widget: UseColorTableValuesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use color table values: | UseColorTableValuesLabel | QLabel
- Text: Use color table values:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: UseColorTableValuesCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: UseColorTableValuesCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:342: connect(d->UseColorTableValuesCheckBox, SIGNAL(clicked()), this, SLOT(updateExportColorWidgets()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:672: d->ColorTableNodeSelector->setEnabled(d->UseColorTableValuesCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:958: if (d->UseColorTableValuesCheckBox->isChecked())`
- Connected slots/functions: `updateExportColorWidgets`
- API footprints: `GetLabelmapConversionColorTableNode`, `vtkMRMLColorTableNode::SafeDownCast`

## widget: ColorTableNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ColorTableNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:320: d->ColorTableNodeSelector->setNodeTypeLabel(tr("Color Table"), "vtkMRMLColorTableNode");`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:343: connect(d->ColorTableNodeSelector, SIGNAL(currentNodeIDChanged(const QString&)), this, SLOT(onExportColorTableChanged()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:671: QSignalBlocker blocker1(d->ColorTableNodeSelector);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:672: d->ColorTableNodeSelector->setEnabled(d->UseColorTableValuesCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:680: QSignalBlocker blocker2(d->ColorTableNodeSelector);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:681: d->ColorTableNodeSelector->setCurrentNode(exportColorTableNode);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:693: std::string currentNodeID = d->ColorTableNodeSelector->currentNodeID().toStdString();`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:960: colorTableNode = vtkMRMLColorTableNode::SafeDownCast(d->ColorTableNodeSelector->currentNode());`
- Connected slots/functions: `onExportColorTableChanged`
- API footprints: `SetLabelmapConversionColorTableNodeID`, `vtkMRMLColorTableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLColorTableNode"]}

## widget: ComboBox_TerminologyContext

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: Labels of the imported labelmap will be mapped to terminology entries of this context | ComboBox_TerminologyContext | ctkComboBox
- Tooltip: Labels of the imported labelmap will be mapped to terminology entries of this context
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:119: this->ComboBox_TerminologyContext->clear();`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:132: this->ComboBox_TerminologyContext->addItem(termIt->c_str());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:620: d->ComboBox_TerminologyContext->setVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:628: d->ComboBox_TerminologyContext->setVisible(d->radioButton_Labelmap->isChecked());`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:1041: d->ComboBox_TerminologyContext->currentText() == d->ComboBox_TerminologyContext->defaultText() ? "" : d->ComboBox_TerminologyContext->currentText().toUtf8().constData());`
- API footprints: `ImportLabelmapToSegmentationNodeWithTerminology`

## widget: label_TerminologyContext

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Terminology context: | label_TerminologyContext | QLabel
- Text: Terminology context:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:619: d->label_TerminologyContext->setVisible(false);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:627: d->label_TerminologyContext->setVisible(d->radioButton_Labelmap->isChecked());`

## widget: CollapsibleButton_ExportToFiles

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Export to files | CollapsibleButton_ExportToFiles | ctkCollapsibleButton
- Text: Export to files
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: ExportToFilesWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSegmentationFileExportWidget`
- Search text: ExportToFilesWidget | qMRMLSegmentationFileExportWidget
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:345: d->ExportToFilesWidget->setSettingsKey("ExportSegmentsToFiles");`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:346: connect(d->MRMLNodeSelector_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->ExportToFilesWidget, SLOT(setSegmentationNode(vtkMRMLNode*)));`
- Connected slots/functions: `setSegmentationNode`

## widget: CollapsibleButton_BinaryLabelmapLayers

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Binary labelmap layers | CollapsibleButton_BinaryLabelmapLayers | ctkCollapsibleButton
- Text: Binary labelmap layers
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:353: connect(d->CollapsibleButton_BinaryLabelmapLayers, SIGNAL(contentsCollapsed(bool)), this, SLOT(updateLayerWidgets()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:580: if (d->CollapsibleButton_BinaryLabelmapLayers->collapsed())`
- Connected slots/functions: `updateLayerWidgets`
- API footprints: `GetNumberOfLayers`, `GetNumberOfSegments`, `GetSegmentation`

## widget: label_LayerCountText

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of layers: | label_LayerCountText | QLabel
- Text: Number of layers:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: label_LayerCountValue

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | label_LayerCountValue | QLabel
- Text: 0
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:605: d->label_LayerCountValue->setText(QString::fromStdString(layerCountSS.str()));`
- API footprints: `GetNumberOfLayers`, `GetSegmentation`

## widget: label_OverwriteSegmentsText

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Force collapse to single layer: | Forcing all segments to a single layer will modify overlapping segments. Regions where multiple segments overlap will be assigned to the segment closest to the end of the segment list. | label_OverwriteSegmentsText | QLabel
- Text: Force collapse to single layer:
- Tooltip: Forcing all segments to a single layer will modify overlapping segments. Regions where multiple segments overlap will be assigned to the segment closest to the end of the segment list.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: label_SegmentCountText

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of segments: | label_SegmentCountText | QLabel
- Text: Number of segments:
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`

## widget: pushButton_CollapseLayers

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Collapse labelmap layers | Minimize the number of layers by moving segments to shared layers to minimize memory usage. Contents of segments are not modified unless there are overlapping segments and collapsing to a single layer is forced. | pushButton_CollapseLayers | QPushButton
- Text: Collapse labelmap layers
- Tooltip: Minimize the number of layers by moving segments to shared layers to minimize memory usage. Contents of segments are not modified unless there are overlapping segments and collapsing to a single layer is forced.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:354: connect(d->pushButton_CollapseLayers, SIGNAL(clicked()), this, SLOT(collapseLabelmapLayers()));`
- Connected slots/functions: `collapseLabelmapLayers`

## widget: label_SegmentCountValue

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | label_SegmentCountValue | QLabel
- Text: 0
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:594: d->label_SegmentCountValue->setText(QString::fromStdString(segmentCountSS.str()));`
- API footprints: `GetNumberOfSegments`, `GetSegmentation`

## widget: checkBox_OverwriteSegments

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: checkBox_OverwriteSegments | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModule.h`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsModuleWidget.cxx:571: bool forceToSingleLayer = d->checkBox_OverwriteSegments->isChecked();`
