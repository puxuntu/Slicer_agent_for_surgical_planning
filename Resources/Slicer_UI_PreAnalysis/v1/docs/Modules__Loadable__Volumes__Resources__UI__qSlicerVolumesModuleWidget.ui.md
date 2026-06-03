# Slicer UI Analysis: Modules/Loadable/Volumes/Resources/UI/qSlicerVolumesModuleWidget.ui

- Owner class: `qSlicerVolumesModuleWidget`
- UI file: `Modules/Loadable/Volumes/Resources/UI/qSlicerVolumesModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerVolumesModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerVolumesModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:43: #include "qSlicerVolumesModuleWidget.h"`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:44: #include "ui_qSlicerVolumesModuleWidget.h"`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:49: class qSlicerVolumesModuleWidgetPrivate : public Ui_qSlicerVolumesModuleWidget`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:55: qSlicerVolumesModuleWidget::qSlicerVolumesModuleWidget(QWidget* _parent)`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:57: , d_ptr(new qSlicerVolumesModuleWidgetPrivate)`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:62: qSlicerVolumesModuleWidget::~qSlicerVolumesModuleWidget() = default;`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:65: void qSlicerVolumesModuleWidget::setup()`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:67: Q_D(qSlicerVolumesModuleWidget);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:85: void qSlicerVolumesModuleWidget::nodeSelectionChanged(vtkMRMLNode* node)`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:92: void qSlicerVolumesModuleWidget::updateWidgetFromMRML()`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:94: Q_D(qSlicerVolumesModuleWidget);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:145: void qSlicerVolumesModuleWidget::convertVolume()`
- API footprints: `vtkMRMLVolumeNode::SafeDownCast`

## widget: ResizableFrame_2

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame_2 | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`

## widget: ActiveVolumeNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: ActiveVolumeNodeSelector | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:71: QObject::connect(d->ActiveVolumeNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->MRMLVolumeInfoWidget, SLOT(setVolumeNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:73: QObject::connect(d->ActiveVolumeNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->VolumeDisplayWidget, SLOT(setMRMLVolumeNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:75: QObject::connect(d->ActiveVolumeNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(nodeSelectionChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:96: vtkMRMLVolumeNode* currentVolumeNode = vtkMRMLVolumeNode::SafeDownCast(d->ActiveVolumeNodeSelector->currentNode());`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:149: vtkMRMLVolumeNode* currentVolume = vtkMRMLVolumeNode::SafeDownCast(d->ActiveVolumeNodeSelector->currentNode());`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:203: d->ActiveVolumeNodeSelector->setCurrentNode(targetVolumeNode);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:216: d->ActiveVolumeNodeSelector->setCurrentNode(node);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:228: d->ActiveVolumeNodeSelector->setCurrentNode(displayableNode);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:244: vtkMRMLVolumeNode* currentVolume = vtkMRMLVolumeNode::SafeDownCast(d->ActiveVolumeNodeSelector->currentNode());`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:277: if (!d->ActiveVolumeNodeSelector->currentNode())`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:279: vtkMRMLNode* node = d->ActiveVolumeNodeSelector->findFirstNodeByClass("vtkMRMLVolumeNode");`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:282: d->ActiveVolumeNodeSelector->setCurrentNode(node);`
- Connected slots/functions: `nodeSelectionChanged`, `setMRMLVolumeNode`, `setVolumeNode`
- API footprints: `RemoveNode`, `vtkMRMLScalarVolumeNode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}

## widget: InfoCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Volume Information | InfoCollapsibleButton | ctkCollapsibleButton
- Text: Volume Information
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:110: d->InfoCollapsibleButton->setEnabled(currentVolumeNode);`
- Key UI properties: {"checked": "false"}

## widget: MRMLVolumeInfoWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLVolumeInfoWidget`
- Search text: MRMLVolumeInfoWidget | qMRMLVolumeInfoWidget
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:71: QObject::connect(d->ActiveVolumeNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->MRMLVolumeInfoWidget, SLOT(setVolumeNode(vtkMRMLNode*)));`
- Connected slots/functions: `setVolumeNode`

## widget: ConvertVolumeFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: ConvertVolumeFrame | QFrame
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:80: d->ConvertVolumeFrame->setVisible(false);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:141: d->ConvertVolumeFrame->setVisible(convertVolumeSectionVisible);`

## widget: ConvertVolumeLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Convert to LabelMap: | ConvertVolumeLabel | QLabel
- Text: Convert to LabelMap:
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:125: d->ConvertVolumeLabel->setText(tr("Convert to label map:"));`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:131: d->ConvertVolumeLabel->setText(tr("Convert to scalar volume:"));`

## widget: ConvertVolumeTargetSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ConvertVolumeTargetSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:137: d->ConvertVolumeTargetSelector->setBaseName(QString("%1_Label").arg(currentVolumeNode->GetName()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:138: d->ConvertVolumeTargetSelector->setNodeTypes(convertTargetNodeTypes);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:164: vtkMRMLVolumeNode* targetVolumeNode = vtkMRMLVolumeNode::SafeDownCast(d->ConvertVolumeTargetSelector->currentNode());`
- API footprints: `GetName`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLLabelMapVolumeNode"]}

## widget: ConvertVolumeButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Convert | ConvertVolumeButton | QPushButton
- Text: Convert
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:81: QObject::connect(d->ConvertVolumeButton, SIGNAL(clicked()), this, SLOT(convertVolume()));`
- Connected slots/functions: `convertVolume`
- API footprints: `AddNode`, `CreateLabelVolumeFromVolume`, `CreateScalarVolumeFromVolume`, `Delete`, `GetAttribute`, `GetAttributeNames`, `GetDescription`, `GetHideFromEditors`, `GetName`, `GetSaveWithScene`, `GetSelectable`, `GetSingletonTag`, `RemoveNode`, `SetAttribute`, `SetDescription`, `SetHideFromEditors`, `SetName`, `SetSaveWithScene`, `SetSelectable`, `SetSingletonTag`, `vtkMRMLLabelMapVolumeNode::New`, `vtkMRMLLabelMapVolumeNode::SafeDownCast`, `vtkMRMLScalarVolumeNode::New`, `vtkMRMLScalarVolumeNode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`

## widget: DisplayCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display | DisplayCollapsibleButton | ctkCollapsibleButton
- Text: Display
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:111: d->DisplayCollapsibleButton->setEnabled(currentVolumeNode);`

## widget: VolumeDisplayWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerVolumeDisplayWidget`
- Search text: VolumeDisplayWidget | qSlicerVolumeDisplayWidget
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:73: QObject::connect(d->ActiveVolumeNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->VolumeDisplayWidget, SLOT(setMRMLVolumeNode(vtkMRMLNode*)));`
- Connected slots/functions: `setMRMLVolumeNode`

## widget: ColorLegendCollapsibleButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Color Legend | ColorLegendCollapsibleButton | ctkCollapsibleButton
- Text: Color Legend
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:77: QObject::connect(d->ColorLegendCollapsibleButton, SIGNAL(contentsCollapsed(bool)), this, SLOT(colorLegendCollapsibleButtonCollapsed(bool)));`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:107: d->ColorLegendCollapsibleButton->setCollapsed(true);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:112: d->ColorLegendCollapsibleButton->setEnabled(currentVolumeNode);`
- Connected slots/functions: `colorLegendCollapsibleButtonCollapsed`
- API footprints: `GetMRMLApplicationLogic`, `PauseRender`, `ResumeRender`, `SetVisibility`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"checked": "false"}

## widget: ColorLegendDisplayNodeWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLColorLegendDisplayNodeWidget`
- Search text: ColorLegendDisplayNodeWidget | qMRMLColorLegendDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:104: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(colorLegendNode);`
  - `Modules/Loadable/Volumes/qSlicerVolumesModuleWidget.cxx:266: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(colorLegendNode);`
