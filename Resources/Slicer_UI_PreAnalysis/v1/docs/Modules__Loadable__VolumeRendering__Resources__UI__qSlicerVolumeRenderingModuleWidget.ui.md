# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qSlicerVolumeRenderingModuleWidget.ui

- Owner class: `qSlicerVolumeRenderingModuleWidget`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qSlicerVolumeRenderingModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerVolumeRenderingModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerVolumeRenderingModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:22: #include "qSlicerVolumeRenderingModuleWidget.h"`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:23: #include "ui_qSlicerVolumeRenderingModuleWidget.h"`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:55: class qSlicerVolumeRenderingModuleWidgetPrivate : public Ui_qSlicerVolumeRenderingModuleWidget`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:57: Q_DECLARE_PUBLIC(qSlicerVolumeRenderingModuleWidget);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:60: qSlicerVolumeRenderingModuleWidget* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:63: qSlicerVolumeRenderingModuleWidgetPrivate(qSlicerVolumeRenderingModuleWidget& object);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:64: virtual ~qSlicerVolumeRenderingModuleWidgetPrivate();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:66: virtual void setupUi(qSlicerVolumeRenderingModuleWidget*);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:79: // qSlicerVolumeRenderingModuleWidgetPrivate methods`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:82: qSlicerVolumeRenderingModuleWidgetPrivate::qSlicerVolumeRenderingModuleWidgetPrivate(qSlicerVolumeRenderingModuleWidget& object)`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:89: qSlicerVolumeRenderingModuleWidgetPrivate::~qSlicerVolumeRenderingModuleWidgetPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:92: void qSlicerVolumeRenderingModuleWidgetPrivate::setupUi(qSlicerVolumeRenderingModuleWidget* q)`
- API footprints: `vtkMRMLDisplayableNode::SafeDownCast`, `vtkMRMLMarkupsROINode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`, `vtkMRMLVolumePropertyNode::SafeDownCast`, `vtkMRMLVolumeRenderingDisplayNode::SafeDownCast`

## widget: ResizableFrame_2

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame_2 | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: VolumeNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: VolumeNodeSelector | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:96: QObject::connect(this->VolumeNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onCurrentMRMLVolumeNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:277: return vtkMRMLVolumeNode::SafeDownCast(d->VolumeNodeSelector->currentNode());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:284: d->VolumeNodeSelector->setCurrentNode(volumeNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:732: this->onCurrentMRMLVolumeNodeChanged(d->VolumeNodeSelector->currentNode());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:946: d->VolumeNodeSelector->setCurrentNode(displayableNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:977: d->VolumeNodeSelector->setCurrentNode(displayableNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1000: d->VolumeNodeSelector->setCurrentNode(displayableNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1154: if (!d->VolumeNodeSelector->currentNode())`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1156: vtkMRMLNode* node = d->VolumeNodeSelector->findFirstNodeByClass("vtkMRMLVolumeNode");`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1159: d->VolumeNodeSelector->setCurrentNode(node);`
- Connected slots/functions: `onCurrentMRMLVolumeNodeChanged`
- API footprints: `GetName`, `GetPresetByName`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}

## widget: InputsCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Inputs | InputsCollapsibleButton | ctkCollapsibleButton
- Text: Inputs
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:173: this->InputsCollapsibleButton->setCollapsed(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:174: this->InputsCollapsibleButton->setEnabled(false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:377: d->InputsCollapsibleButton->setEnabled(displayNode != nullptr);`
- Key UI properties: {"checked": "false"}

## widget: ROINodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: ROI: | ROINodeLabel | QLabel
- Text: ROI:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: ROINodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ROINodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:99: QObject::connect(this->ROINodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onCurrentMRMLROINodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:399: bool wasBlocking = d->ROINodeComboBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:400: d->ROINodeComboBox->setCurrentNode(roiNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:401: d->ROINodeComboBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:678: return vtkMRMLDisplayableNode::SafeDownCast(d->ROINodeComboBox->currentNode());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:685: return vtkMRMLMarkupsROINode::SafeDownCast(d->ROINodeComboBox->currentNode());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:692: d->ROINodeComboBox->setCurrentNode(roiNode);`
- Connected slots/functions: `onCurrentMRMLROINodeChanged`
- API footprints: `GetID`, `SetAndObserveROINodeID`, `vtkMRMLDisplayableNode::SafeDownCast`, `vtkMRMLMarkupsROINode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLMarkupsROINode"]}

## widget: VolumePropertyNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Property: | VolumePropertyNodeLabel | QLabel
- Text: Property:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: VolumePropertyNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: VolumePropertyNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:100: QObject::connect(this->VolumePropertyNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onCurrentMRMLVolumePropertyNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:101: QObject::connect(this->VolumePropertyNodeComboBox, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), q, SLOT(onNewVolumePropertyAdded(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:153: QObject::connect(this->VolumePropertyNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this->PresetComboBox, SLOT(setMRMLVolumePropertyNode(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:390: d->VolumePropertyNodeComboBox->setCurrentNode(volumePropertyNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:614: return vtkMRMLVolumePropertyNode::SafeDownCast(d->VolumePropertyNodeComboBox->currentNode());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:622: d->VolumePropertyNodeComboBox->setCurrentNode(volumePropertyNode);`
- Connected slots/functions: `onCurrentMRMLVolumePropertyNodeChanged`, `onNewVolumePropertyAdded`, `setMRMLVolumePropertyNode`
- API footprints: `GetID`, `SetAndObserveVolumePropertyNodeID`, `vtkMRMLVolumePropertyNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumePropertyNode"]}

## widget: ViewNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View: | ViewNodeLabel | QLabel
- Text: View:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: ViewCheckableNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLDisplayNodeViewComboBox`
- Search text: ViewCheckableNodeComboBox | qMRMLDisplayNodeViewComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:183: this->ViewCheckableNodeComboBox->setNodeTypes(QStringList(QString("vtkMRMLViewNode")));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:243: for (vtkMRMLAbstractViewNode* const viewNode : this->ViewCheckableNodeComboBox->checkedViewNodes())`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:311: d->ViewCheckableNodeComboBox->setMRMLDisplayNode(displayNode);`
- API footprints: `AddViewNodeID`, `GetID`

## widget: DisplayCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display | DisplayCollapsibleButton | ctkCollapsibleButton
- Text: Display
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:404: d->DisplayCollapsibleButton->setEnabled(displayNode != nullptr);`

## widget: CropLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | CropLabel_2 | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: VisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: VisibilityCheckBox | ctkCheckBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:98: QObject::connect(this->VisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(onVisibilityChanged(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:374: d->VisibilityCheckBox->setChecked(displayNode ? displayNode->GetVisibility() : false);`
- Connected slots/functions: `onVisibilityChanged`
- API footprints: `GetName`, `GetVisibility`, `SetVisibility`

## widget: PresetComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerVolumeRenderingPresetComboBox`
- Search text: PresetComboBox | qSlicerVolumeRenderingPresetComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:31: #include "qSlicerVolumeRenderingPresetComboBox.h"`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:143: this->PresetComboBox->setMRMLScene(volumeRenderingLogic->GetPresetsScene());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:144: this->PresetComboBox->setCurrentNode(nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:146: QObject::connect(this->PresetComboBox, SIGNAL(presetOffsetChanged(double, double, bool)), this->VolumePropertyNodeWidget, SLOT(moveAllPoints(double, double, bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:153: QObject::connect(this->VolumePropertyNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this->PresetComboBox, SLOT(setMRMLVolumePropertyNode(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:318: bool wasBlocking = d->PresetComboBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:319: d->PresetComboBox->setCurrentNode(presetNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:320: d->PresetComboBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:408: d->PresetComboBox->setEnabled(volumePropertyNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:409: wasBlocking = d->PresetComboBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:410: d->PresetComboBox->setCurrentNode(volumePropertyNode ? vtkSlicerVolumeRenderingLogic::SafeDownCast(this->logic())->GetPresetByName(volumePropertyNode->GetName()) : nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:411: d->PresetComboBox->blockSignals(wasBlocking);`
- Connected slots/functions: `moveAllPoints`, `setMRMLVolumePropertyNode`
- API footprints: `GetCroppingEnabled`, `GetName`, `GetPresetByName`, `GetPresetsScene`, `GetUseLinearRamp`

## widget: CropLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Crop: | CropLabel | QLabel
- Text: Crop:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: ROICropCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable | ROICropCheckBox | QCheckBox
- Text: Enable
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:104: QObject::connect(this->ROICropCheckBox, SIGNAL(toggled(bool)), q, SLOT(onCropToggled(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:412: d->ROICropCheckBox->setChecked(roiNode && displayNode ? displayNode->GetCroppingEnabled() : false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:413: d->ROICropCheckBox->setEnabled(displayNode != nullptr);        // ROI can be created on request if display node is set`
- Connected slots/functions: `onCropToggled`
- API footprints: `CreateROINode`, `GetCroppingEnabled`, `GetName`, `GetPresetByName`, `SetCroppingEnabled`

## widget: ROICropDisplayCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: Display ROI | ROICropDisplayCheckBox | ctkCheckBox
- Text: Display ROI
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:105: QObject::connect(this->ROICropDisplayCheckBox, SIGNAL(toggled(bool)), q, SLOT(onROICropDisplayCheckBoxToggled(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:414: d->ROICropDisplayCheckBox->setEnabled(displayNode != nullptr); // ROI can be created on request if display node is set`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:539: QSignalBlocker blocker(d->ROICropDisplayCheckBox);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:540: d->ROICropDisplayCheckBox->setChecked(roiVisible);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:867: void qSlicerVolumeRenderingModuleWidget::onROICropDisplayCheckBoxToggled(bool toggle)`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h:94: void onROICropDisplayCheckBoxToggled(bool toggle);`
- Connected slots/functions: `onROICropDisplayCheckBoxToggled`
- API footprints: `CreateROINode`, `EndModify`, `GetCroppingEnabled`, `GetDisplayVisibility`, `GetNthDisplayNode`, `GetNumberOfDisplayNodes`, `SetCroppingEnabled`, `SetDisplayVisibility`, `StartModify`

## widget: ROIFitPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Fit to Volume | ROIFitPushButton | QPushButton
- Text: Fit to Volume
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:106: QObject::connect(this->ROIFitPushButton, SIGNAL(clicked()), q, SLOT(fitROIToVolume()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:415: d->ROIFitPushButton->setEnabled(roiNode != nullptr);`
- Connected slots/functions: `fitROIToVolume`
- API footprints: `FitROIToVolume`, `GetMarkupsROINode`, `GetRadiusXYZ`, `GetXYZ`

## widget: RenderingMethodLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Rendering: | RenderingMethodLabel | QLabel
- Text: Rendering:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: RenderingMethodComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: RenderingMethodComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:114: this->RenderingMethodComboBox->addItem(QString::fromStdString(it->first), QString::fromStdString(it->second));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:116: QObject::connect(this->RenderingMethodComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onCurrentRenderingMethodChanged(int)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:416: d->RenderingMethodComboBox->setEnabled(displayNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:435: d->RenderingMethodComboBox->setCurrentIndex(d->RenderingMethodComboBox->findData(currentRenderingMethod));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:720: QString renderingClassName = d->RenderingMethodComboBox->itemData(index).toString();`
- Connected slots/functions: `onCurrentRenderingMethodChanged`
- API footprints: `ChangeVolumeRenderingMethod`, `GetClassName`, `GetGPUMemorySize`, `GetVolumeRenderingQuality`

## widget: CollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Key UI properties: {"checked": "false"}

## widget: ClippingBlankVoxelValueAutoCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Auto | ClippingBlankVoxelValueAutoCheckBox | QCheckBox
- Text: Auto
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:163: QObject::connect(this->ClippingBlankVoxelValueAutoCheckBox, SIGNAL(toggled(bool)), q, SLOT(setClippingBlankVoxelValueAuto(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:492: wasBlocking = d->ClippingBlankVoxelValueAutoCheckBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:493: d->ClippingBlankVoxelValueAutoCheckBox->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:494: d->ClippingBlankVoxelValueAutoCheckBox->setChecked(displayNode ? displayNode->GetAutoClippingBlankVoxelValue() : false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:495: d->ClippingBlankVoxelValueAutoCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setClippingBlankVoxelValueAuto`
- API footprints: `GetAutoClippingBlankVoxelValue`, `SetAutoClippingBlankVoxelValue`

## widget: ClippingSoftEdgeLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Soft edge: | ClippingSoftEdgeLabel | QLabel
- Text: Soft edge:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:487: d->ClippingSoftEdgeLabel->setEnabled(clipNode != nullptr);`
- API footprints: `GetClippingSoftEdgeVoxels`

## widget: ClippingLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Clipping: | ClippingLabel | QLabel
- Text: Clipping:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:481: d->ClippingLabel->setEnabled(clipNode != nullptr);`
- API footprints: `GetClipping`

## widget: ClipNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Clip node: | ClipNodeLabel | QLabel
- Text: Clip node:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: ClippingBlankVoxelValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Blank value: | ClippingBlankVoxelValueLabel | QLabel
- Text: Blank value:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:498: d->ClippingBlankVoxelValueLabel->setEnabled(clipNode != nullptr);`
- API footprints: `GetAutoClippingBlankVoxelValue`, `GetClippingBlankVoxelValue`

## widget: ClippingSoftEdgeSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: ClippingSoftEdgeSlider | qMRMLSliderWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:161: QObject::connect(this->ClippingSoftEdgeSlider, SIGNAL(valueChanged(double)), q, SLOT(setSoftEdgeVoxels(double)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:486: wasBlocking = d->ClippingSoftEdgeSlider->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:488: d->ClippingSoftEdgeSlider->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:489: d->ClippingSoftEdgeSlider->setValue(displayNode ? displayNode->GetClippingSoftEdgeVoxels() : 0.0);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:490: d->ClippingSoftEdgeSlider->blockSignals(wasBlocking);`
- Connected slots/functions: `setSoftEdgeVoxels`
- API footprints: `GetClippingSoftEdgeVoxels`, `SetClippingSoftEdgeVoxels`

## widget: ClipNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ClipNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:159: QObject::connect(this->ClipNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setMRMLClipNode(vtkMRMLNode*)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:471: wasBlocking = d->ClipNodeSelector->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:472: d->ClipNodeSelector->setCurrentNode(clipNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:473: d->ClipNodeSelector->blockSignals(wasBlocking);`
- Connected slots/functions: `setMRMLClipNode`
- API footprints: `GetClipNode`, `GetID`, `SetAndObserveClipNodeID`
- Key UI properties: {"nodeTypes": ["vtkMRMLClipNode"]}

## widget: ClippingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: ClippingCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:160: QObject::connect(this->ClippingCheckBox, SIGNAL(toggled(bool)), q, SLOT(setClippingEnabled(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:476: d->ClippingCheckBox->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:480: wasBlocking = d->ClippingCheckBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:482: d->ClippingCheckBox->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:483: d->ClippingCheckBox->setChecked(displayNode ? displayNode->GetClipping() : false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:484: d->ClippingCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setClippingEnabled`
- API footprints: `GetClipping`, `SetClipping`

## widget: ClippingBlankVoxelValueSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: ClippingBlankVoxelValueSlider | qMRMLSliderWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:164: QObject::connect(this->ClippingBlankVoxelValueSlider, SIGNAL(valueChanged(double)), q, SLOT(setClippingBlankVoxelValue(double)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:497: wasBlocking = d->ClippingBlankVoxelValueSlider->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:499: d->ClippingBlankVoxelValueSlider->setEnabled(displayNode != nullptr && !displayNode->GetAutoClippingBlankVoxelValue());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:500: d->ClippingBlankVoxelValueSlider->setValue(displayNode ? displayNode->GetClippingBlankVoxelValue() : 0.0);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:501: d->ClippingBlankVoxelValueSlider->blockSignals(wasBlocking);`
- Connected slots/functions: `setClippingBlankVoxelValue`
- API footprints: `GetAutoClippingBlankVoxelValue`, `GetClippingBlankVoxelValue`, `SetClippingBlankVoxelValue`

## widget: MRMLClipNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLClipNodeWidget`
- Search text: MRMLClipNodeWidget | qMRMLClipNodeWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:475: wasBlocking = d->MRMLClipNodeWidget->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:477: d->MRMLClipNodeWidget->setMRMLClipNode(clipNode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:478: d->MRMLClipNodeWidget->blockSignals(wasBlocking);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1099: d->MRMLClipNodeWidget->setMRMLClipNode(clipNode);`
- API footprints: `GetID`, `SetAndObserveClipNodeID`

## widget: ClippingInfoLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: ClippingInfoLabel | QLabel
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:167: this->ClippingInfoLabel->setVisible(false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:524: d->ClippingInfoLabel->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:525: d->ClippingInfoLabel->setText(message);`

## widget: ClippingExpandInfoButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ClippingExpandInfoButton | QToolButton
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:166: QObject::connect(this->ClippingExpandInfoButton, SIGNAL(clicked()), q, SLOT(updateWidgetFromMRML()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:526: d->ClippingExpandInfoButton->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:527: d->ClippingExpandInfoButton->setIcon(clippingInfoIcon);`
- Connected slots/functions: `updateWidgetFromMRML`
- API footprints: `GetAutoClippingBlankVoxelValue`, `GetAutoReleaseGraphicsResources`, `GetClassName`, `GetClipNode`, `GetClipping`, `GetClippingSoftEdgeVoxels`, `GetCroppingEnabled`, `GetExpectedFPS`, `GetFirstViewNode`, `GetFollowVolumeDisplayNode`, `GetGPUMemorySize`, `GetIgnoreVolumeDisplayNodeThreshold`, `GetMarkupsROINode`, `GetName`, `GetNumberOfIndependentComponents`, `GetPresetByName`, `GetScene`, `GetVisibility`, `GetVolumePropertyNode`, `GetVolumeRenderingQuality`, `vtkMRMLDisplayableNode::DisplayModifiedEvent`, `vtkMRMLViewNode::Adaptive`, `vtkMRMLVolumePropertyNode::EffectiveRangeModified`
- Key UI properties: {"checkable": "true"}

## widget: AdvancedCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced... | AdvancedCollapsibleButton | ctkCollapsibleButton
- Text: Advanced...
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:175: this->AdvancedCollapsibleButton->setCollapsed(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:176: this->AdvancedCollapsibleButton->setEnabled(false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:405: d->AdvancedCollapsibleButton->setEnabled(displayNode != nullptr);`
- Key UI properties: {"checked": "true"}

## widget: AdvancedTabWidget

- Confidence: `linked_to_code`
- Widget/action class: `QTabWidget`
- Search text: AdvancedTabWidget | QTabWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:180: this->AdvancedTabWidget->setCurrentWidget(this->VolumePropertyTab);`

## widget: TechniquesTab

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: TechniquesTab | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: MemorySizeLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: GPU memory size: | MemorySizeLabel | QLabel
- Text: GPU memory size:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:124: this->MemorySizeLabel->hide();`

## widget: MemorySizeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerGPUMemoryComboBox`
- Search text: Amount of memory allocated for volume rendering on the graphic card. "Default" can be modified in the settings. | MemorySizeComboBox | qSlicerGPUMemoryComboBox
- Tooltip: Amount of memory allocated for volume rendering on the graphic card. "Default" can be modified in the settings.
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:125: this->MemorySizeComboBox->hide();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:127: QObject::connect(this->MemorySizeComboBox, SIGNAL(editTextChanged(QString)), q, SLOT(onCurrentMemorySizeChanged()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:128: QObject::connect(this->MemorySizeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onCurrentMemorySizeChanged()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:436: d->MemorySizeComboBox->setCurrentGPUMemory(firstViewNode ? firstViewNode->GetGPUMemorySize() : 0);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:744: int gpuMemorySize = d->MemorySizeComboBox->currentGPUMemoryInMB();`
- Connected slots/functions: `onCurrentMemorySizeChanged`
- API footprints: `GetAutoReleaseGraphicsResources`, `GetClassName`, `GetGPUMemorySize`, `GetID`, `GetNodesByClass`, `GetScene`, `GetVolumeRenderingQuality`, `IsDisplayableInView`, `SetGPUMemorySize`, `vtkMRMLViewNode::SafeDownCast`, `vtkMRMLViewNode::VolumeRenderingQuality_Last`

## widget: QualityControlLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Quality: | QualityControlLabel | QLabel
- Text: Quality:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: QualityControlComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: QualityControlComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:132: this->QualityControlComboBox->addItem(vtkMRMLViewNode::GetVolumeRenderingQualityAsString(qualityIndex));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:134: QObject::connect(this->QualityControlComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onCurrentQualityControlChanged(int)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:437: d->QualityControlComboBox->setCurrentIndex(firstViewNode ? firstViewNode->GetVolumeRenderingQuality() : -1);`
- Connected slots/functions: `onCurrentQualityControlChanged`
- API footprints: `GetAutoReleaseGraphicsResources`, `GetGPUMemorySize`, `GetID`, `GetNodesByClass`, `GetScene`, `GetVolumeRenderingQuality`, `IsDisplayableInView`, `SetVolumeRenderingQuality`, `vtkMRMLViewNode::GetVolumeRenderingQualityAsString`, `vtkMRMLViewNode::SafeDownCast`, `vtkMRMLViewNode::VolumeRenderingQuality_Last`

## widget: FramerateLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Interactive speed: | FramerateLabel | QLabel
- Text: Interactive speed:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: FramerateSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: FramerateSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:136: QObject::connect(this->FramerateSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onCurrentFramerateChanged(double)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:442: d->FramerateSliderWidget->setValue(firstViewNode->GetExpectedFPS());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:444: d->FramerateSliderWidget->setEnabled(firstViewNode && firstViewNode->GetVolumeRenderingQuality() == vtkMRMLViewNode::Adaptive);`
- Connected slots/functions: `onCurrentFramerateChanged`
- API footprints: `GetExpectedFPS`, `GetID`, `GetNodesByClass`, `GetScene`, `GetVolumeRenderingQuality`, `IsDisplayableInView`, `SetExpectedFPS`, `vtkMRMLViewNode::Adaptive`, `vtkMRMLViewNode::SafeDownCast`

## widget: AdvancedGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: AdvancedGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: RenderingMethodStackedWidget

- Confidence: `linked_to_code`
- Widget/action class: `QStackedWidget`
- Search text: RenderingMethodStackedWidget | QStackedWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:118: this->RenderingMethodStackedWidget->addWidget(new QWidget());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:354: d->RenderingMethodStackedWidget->addWidget(widget);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:450: d->RenderingMethodStackedWidget->setCurrentWidget(renderingMethodWidget);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:456: d->RenderingMethodStackedWidget->setCurrentIndex(0);`

## widget: FramerateLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Auto-release resources: | FramerateLabel_2 | QLabel
- Text: Auto-release resources:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: AutoReleaseGraphicsResourcesCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Immediately unload volumes from graphics memory when not visible. Reduces memory usage but makes toggling volume visibility slower. | AutoReleaseGraphicsResourcesCheckBox | QCheckBox
- Tooltip: Immediately unload volumes from graphics memory when not visible. Reduces memory usage but makes toggling volume visibility slower.
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:138: QObject::connect(this->AutoReleaseGraphicsResourcesCheckBox, SIGNAL(toggled(bool)), q, SLOT(onAutoReleaseGraphicsResourcesCheckBoxToggled(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:438: d->AutoReleaseGraphicsResourcesCheckBox->setChecked(firstViewNode ? firstViewNode->GetAutoReleaseGraphicsResources() : false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:782: void qSlicerVolumeRenderingModuleWidget::onAutoReleaseGraphicsResourcesCheckBoxToggled(bool autoRelease)`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h:84: void onAutoReleaseGraphicsResourcesCheckBoxToggled(bool autoRelease);`
- Connected slots/functions: `onAutoReleaseGraphicsResourcesCheckBoxToggled`
- API footprints: `GetAutoReleaseGraphicsResources`, `GetGPUMemorySize`, `GetID`, `GetNodesByClass`, `GetScene`, `GetVolumeRenderingQuality`, `IsDisplayableInView`, `SetAutoReleaseGraphicsResources`, `vtkMRMLViewNode::SafeDownCast`

## widget: VolumePropertyTab

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: VolumePropertyTab | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:180: this->AdvancedTabWidget->setCurrentWidget(this->VolumePropertyTab);`

## widget: SynchronizeScalarDisplayNodeButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckablePushButton`
- Search text: Synchronize with Volumes module | SynchronizeScalarDisplayNodeButton | ctkCheckablePushButton
- Text: Synchronize with Volumes module
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:155: QObject::connect(this->SynchronizeScalarDisplayNodeButton, SIGNAL(clicked()), q, SLOT(synchronizeScalarDisplayNode()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:156: QObject::connect(this->SynchronizeScalarDisplayNodeButton, SIGNAL(toggled(bool)), q, SLOT(setFollowVolumeDisplayNode(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:460: d->SynchronizeScalarDisplayNodeButton->setEnabled(displayNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:464: d->SynchronizeScalarDisplayNodeButton->setCheckState(Qt::Checked);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:466: d->SynchronizeScalarDisplayNodeButton->setChecked(follow);`
- Connected slots/functions: `setFollowVolumeDisplayNode`, `synchronizeScalarDisplayNode`
- API footprints: `CopyDisplayToVolumeRenderingDisplayNode`, `GetFollowVolumeDisplayNode`, `GetIgnoreVolumeDisplayNodeThreshold`, `SetFollowVolumeDisplayNode`

## widget: IgnoreVolumesThresholdCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Ignore threshold | Don't use threshold values. Set opacity ramp from the Window/Level range instead. | IgnoreVolumesThresholdCheckBox | QCheckBox
- Text: Ignore threshold
- Tooltip: Don't use threshold values. Set opacity ramp from the Window/Level range instead.
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:157: QObject::connect(this->IgnoreVolumesThresholdCheckBox, SIGNAL(toggled(bool)), q, SLOT(setIgnoreVolumesThreshold(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:239: displayNode->SetIgnoreVolumeDisplayNodeThreshold(this->IgnoreVolumesThresholdCheckBox->isChecked());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:467: d->IgnoreVolumesThresholdCheckBox->setChecked(displayNode ? displayNode->GetIgnoreVolumeDisplayNodeThreshold() != 0 : false);`
- Connected slots/functions: `setIgnoreVolumesThreshold`
- API footprints: `GetClipNode`, `GetIgnoreVolumeDisplayNodeThreshold`, `SetIgnoreVolumeDisplayNodeThreshold`

## widget: ExpandSynchronizeWithVolumesButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkExpandButton`
- Search text: ExpandSynchronizeWithVolumesButton | ctkExpandButton
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:178: this->ExpandSynchronizeWithVolumesButton->setChecked(false);`
- Key UI properties: {"checked": "true"}

## widget: VolumePropertyNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLVolumePropertyNodeWidget`
- Search text: VolumePropertyNodeWidget | qMRMLVolumePropertyNodeWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:146: QObject::connect(this->PresetComboBox, SIGNAL(presetOffsetChanged(double, double, bool)), this->VolumePropertyNodeWidget, SLOT(moveAllPoints(double, double, bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:148: this->VolumePropertyNodeWidget->setThreshold(!volumeRenderingLogic->GetUseLinearRamp());`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:149: QObject::connect(this->VolumePropertyNodeWidget, SIGNAL(thresholdChanged(bool)), q, SLOT(onThresholdChanged(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:150: QObject::connect(this->VolumePropertyNodeWidget, SIGNAL(chartsExtentChanged()), q, SLOT(onChartsExtentChanged()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:151: QObject::connect(this->VolumePropertyNodeWidget, SIGNAL(componentChanged(int)), q, SLOT(onEffectiveRangeModified()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:422: d->VolumePropertyNodeWidget->setComponentCount(qMin(numberOfComponents, VTK_MAX_VRCOMP));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:425: d->VolumePropertyNodeWidget->setEnabled(volumePropertyNode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1046: d->VolumePropertyNodeWidget->chartsExtent(effectiveRange);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1074: int component = d->VolumePropertyNodeWidget->currentComponent();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1081: bool wasBlocking = d->VolumePropertyNodeWidget->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1082: d->VolumePropertyNodeWidget->setChartsExtent(effectiveRange[0], effectiveRange[1]);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:1083: d->VolumePropertyNodeWidget->blockSignals(wasBlocking);`
- Connected slots/functions: `moveAllPoints`, `onChartsExtentChanged`, `onEffectiveRangeModified`, `onThresholdChanged`
- API footprints: `CalculateEffectiveRange`, `DisableModifiedEventOn`, `GetDisableModifiedEvent`, `GetEffectiveRange`, `GetNumberOfIndependentComponents`, `GetUseLinearRamp`, `SetDisableModifiedEvent`, `SetEffectiveRange`, `SetUseLinearRamp`

## widget: ROITab

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: ROITab | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`

## widget: MarkupsROIWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLMarkupsROIWidget`
- Search text: MarkupsROIWidget | qMRMLMarkupsROIWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:170: this->MarkupsROIWidget->setVisible(false);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:428: d->MarkupsROIWidget->setMRMLMarkupsNode(markupsROINode);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:429: d->MarkupsROIWidget->setVisible(markupsROINode != nullptr);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:584: (d->MarkupsROIWidget->mrmlROINode() != this->mrmlMarkupsROINode() //`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:585: || d->MarkupsROIWidget->mrmlROINode() != markupsROINode))`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:592: if (markupsROINode && d->MarkupsROIWidget->mrmlROINode())`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:597: d->MarkupsROIWidget->mrmlROINode()->GetXYZ(xyz);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:598: d->MarkupsROIWidget->mrmlROINode()->GetRadiusXYZ(rxyz);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:606: d->MarkupsROIWidget->setExtent(bounds[0], bounds[3], bounds[1], bounds[4], bounds[2], bounds[5]);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingModuleWidget.cxx:890: vtkMRMLDisplayableNode* roiNode = d->MarkupsROIWidget->mrmlROINode();`
- API footprints: `GetMarkupsROINode`, `GetRadiusXYZ`, `GetXYZ`
