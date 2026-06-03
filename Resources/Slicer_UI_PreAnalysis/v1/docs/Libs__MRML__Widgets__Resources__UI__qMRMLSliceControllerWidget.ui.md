# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLSliceControllerWidget.ui

- Owner class: `qMRMLSliceControllerWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLSliceControllerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSliceControllerWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkPopupWidget`
- Search text: qMRMLSliceControllerWidget | ctkPopupWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:44: #include "qMRMLSliceControllerWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:73: qMRMLSliceControllerWidgetPrivate::qMRMLSliceControllerWidgetPrivate(qMRMLSliceControllerWidget& object)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:112: qMRMLSliceControllerWidgetPrivate::~qMRMLSliceControllerWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:115: void qMRMLSliceControllerWidgetPrivate::setColor(QColor barColor)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:121: void qMRMLSliceControllerWidgetPrivate::setupPopupUi()`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:123: Q_Q(qMRMLSliceControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:126: this->Ui_qMRMLSliceControllerWidget::setupUi(this->PopupWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:172: this->connect(this->SliceOrientationSelector, &QComboBox::currentTextChanged, q, &qMRMLSliceControllerWidget::setSliceOrientation);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:287: void qMRMLSliceControllerWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:289: Q_Q(qMRMLSliceControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:327: this->SliceOffsetSlider->setToolTip(qMRMLSliceControllerWidget::tr("Slice distance from RAS origin"));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:373: void qMRMLSliceControllerWidgetPrivate::updateSliceOffsetSliderVisibility()`
- Connected slots/functions: `currentTextChanged`, `mappedInt`, `setOrientationMarkerSize`, `setOrientationMarkerType`, `setRulerColor`, `setRulerType`, `setSlabReconstructionType`, `setSliceOrientation`
- API footprints: `EndSliceNodeInteraction`, `GetBackgroundLayer`, `GetBackgroundVolumeID`, `GetFieldOfView`, `GetForegroundLayer`, `GetLayoutName`, `GetMRMLApplicationLogic`, `GetNextItemAsObject`, `GetNodesByClass`, `GetPointer`, `GetSliceNode`, `GetVolumeNode`, `InitTraversal`, `IsBatchProcessing`, `SetOrientation`, `SetOrientationMarkerSize`, `SetOrientationMarkerType`, `SetRulerColor`, `SetRulerType`, `SetSlabReconstructionType`, `SetSliceResolutionMode`, `StartSliceNodeInteraction`, `vtkMRMLScalarVolumeDisplayNode::SafeDownCast`, `vtkMRMLSegmentationNode::SafeDownCast`, `vtkMRMLSliceCompositeNode::Add`, `vtkMRMLSliceCompositeNode::Alpha`, `vtkMRMLSliceCompositeNode::ReverseAlpha`, `vtkMRMLSliceCompositeNode::Subtract`, `vtkMRMLSliceLogic::ModifiedEvent`, `vtkMRMLSliceNode::OrientationFlag`

## widget: LabelMapVisibilityButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: LabelMapVisibilityButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:277: this->LabelMapVisibilityButton->setDefaultAction(this->actionLabelMapVisibility);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:278: this->LabelMapVisibilityButton->setMenu(this->LabelMapMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:597: this->LabelMapMenu = new QMenu(tr("LabelMap"), this->LabelMapVisibilityButton);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::MenuButtonPopup"}

## widget: LabelMapComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select the label map | LabelMapComboBox | qMRMLNodeComboBox
- Tooltip: Select the label map
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:152: // int volumeSelectorMinWidth = this->LabelMapComboBox->fontMetrics().horizontalAdvance("Xxxxxxxx") + 20;`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:154: // this->LabelMapComboBox->setMinimumWidth(volumeSelectorMinWidth);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:231: this->connect(this->LabelMapComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onLabelMapNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:234: this->connect(this->LabelMapComboBox, SIGNAL(nodeActivated(vtkMRMLNode*)), SLOT(onLabelMapNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:235: // this->connect(this->LabelMapComboBox, SIGNAL(currentNodeChanged(bool)),`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:237: this->connect(this->LabelMapComboBox, SIGNAL(currentNodeChanged(bool)), this->actionLabelMapOutline, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:258: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->LabelMapComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:918: wasBlocked = this->LabelMapComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:919: this->LabelMapComboBox->setCurrentNode(q->mrmlScene()->GetNodeByID(this->MRMLSliceCompositeNode->GetLabelVolumeID()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:920: this->LabelMapComboBox->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1514: bool labelmapBlockSignals = d->LabelMapComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1523: d->LabelMapComboBox->blockSignals(labelmapBlockSignals);`
- Connected slots/functions: `onLabelMapNodeSelected`, `setEnabled`, `setMRMLScene`
- API footprints: `EndSliceCompositeNodeInteraction`, `GetID`, `GetLabelVolumeID`, `GetNodeByID`, `SetLabelVolumeID`, `SetMRMLScene`, `StartSliceCompositeNodeInteraction`, `vtkMRMLScene::EndBatchProcessEvent`, `vtkMRMLScene::SceneImportedEvent`, `vtkMRMLSliceCompositeNode::LabelVolumeFlag`
- Key UI properties: {"nodeTypes": ["vtkMRMLLabelMapVolumeNode"]}

## widget: SegmentationOutlineButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: SegmentationOutlineButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:280: this->SegmentationOutlineButton->setDefaultAction(this->actionSegmentationOutlineFill);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1082: this->SegmentationOutlineButton->setIcon(outlineFillIcon);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1087: this->SegmentationOutlineButton->setIcon(fillIcon);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1092: this->SegmentationOutlineButton->setIcon(outlineIcon);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2724: d->SegmentationOutlineButton->setVisible(visible);`

## widget: SegmentationVisibilityButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: SegmentationVisibilityButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:274: this->SegmentationVisibilityButton->setDefaultAction(this->actionSegmentationVisibility);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:275: this->SegmentationVisibilityButton->setMenu(this->SegmentationMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:588: this->SegmentationMenu = new QMenu(tr("Segmentation"), this->SegmentationVisibilityButton);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1044: this->SegmentationVisibilityButton->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1045: this->SegmentationVisibilityButton->setChecked(!displayNode->GetVisibility());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1046: this->SegmentationVisibilityButton->blockSignals(false);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2722: d->SegmentationVisibilityButton->setVisible(visible);`
- API footprints: `GetVisibility`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::MenuButtonPopup"}

## widget: LabelMapOutlineButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: LabelMapOutlineButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:281: this->LabelMapOutlineButton->setDefaultAction(this->actionLabelMapOutline);`

## widget: ForegroundOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: ForegroundOpacitySlider | ctkSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:130: this->ForegroundOpacitySlider->spinBox()->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:133: this->ForegroundOpacitySlider->slider()->setOrientation(Qt::Vertical);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:144: popupLayout->addWidget(this->ForegroundOpacitySlider->spinBox(), 3, 2);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:145: this->connect(this->MoreButton, SIGNAL(toggled(bool)), this->ForegroundOpacitySlider->spinBox(), SLOT(setVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:146: this->connect(this->ForegroundComboBox, SIGNAL(currentNodeChanged(bool)), this->ForegroundOpacitySlider->spinBox(), SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:214: this->connect(this->ForegroundOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(setForegroundOpacity(double)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:663: this->ForegroundOpacitySlider->setEnabled(enableVisibility && hasForeground);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:926: this->ForegroundOpacitySlider->setValue(this->MRMLSliceCompositeNode->GetForegroundOpacity());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2004: if (hide && d->ForegroundOpacitySlider->value() != 0.)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2006: d->LastForegroundOpacity = d->ForegroundOpacitySlider->value();`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2008: d->ForegroundOpacitySlider->setValue(hide ? 0. : d->LastForegroundOpacity);`
- Connected slots/functions: `setEnabled`, `setForegroundOpacity`, `setVisible`
- API footprints: `EndSliceCompositeNodeInteraction`, `GetForegroundOpacity`, `GetPointer`, `SetForegroundOpacity`, `StartSliceCompositeNodeInteraction`, `vtkMRMLSliceCompositeNode::ForegroundOpacityFlag`

## widget: LabelMapOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: LabelMapOpacitySlider | ctkSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:129: this->LabelMapOpacitySlider->spinBox()->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:213: this->connect(this->LabelMapOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(setLabelMapOpacity(double)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:598: QWidgetAction* opacityAction = new QWidgetAction(this->LabelMapOpacitySlider);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:599: opacityAction->setDefaultWidget(this->LabelMapOpacitySlider->slider());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:666: this->LabelMapOpacitySlider->setEnabled(enableVisibility && hasLabelMap);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:923: this->LabelMapOpacitySlider->setValue(this->MRMLSliceCompositeNode->GetLabelOpacity());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1997: d->LabelMapOpacitySlider->setValue(hide ? 0. : d->LastLabelMapOpacity);`
- Connected slots/functions: `setLabelMapOpacity`
- API footprints: `EndSliceCompositeNodeInteraction`, `GetLabelOpacity`, `GetPointer`, `SetLabelOpacity`, `StartSliceCompositeNodeInteraction`, `vtkMRMLSliceCompositeNode::LabelOpacityFlag`

## widget: ForegroundComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select the foreground | ForegroundComboBox | qMRMLNodeComboBox
- Tooltip: Select the foreground
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:146: this->connect(this->ForegroundComboBox, SIGNAL(currentNodeChanged(bool)), this->ForegroundOpacitySlider->spinBox(), SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:156: // this->ForegroundComboBox->setMinimumWidth(volumeSelectorMinWidth);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:240: this->connect(this->ForegroundComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onForegroundLayerNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:243: this->connect(this->ForegroundComboBox, SIGNAL(nodeActivated(vtkMRMLNode*)), SLOT(onForegroundLayerNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:244: // this->connect(this->ForegroundComboBox, SIGNAL(currentNodeChanged(bool)),`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:246: this->connect(this->ForegroundComboBox, SIGNAL(currentNodeChanged(bool)), this->actionForegroundInterpolation, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:259: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->ForegroundComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:904: wasBlocked = this->ForegroundComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:905: this->ForegroundComboBox->setCurrentNode(q->mrmlScene()->GetNodeByID(this->MRMLSliceCompositeNode->GetForegroundVolumeID()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:906: this->ForegroundComboBox->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1513: bool foregroundBlockSignals = d->ForegroundComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1522: d->ForegroundComboBox->blockSignals(foregroundBlockSignals);`
- Connected slots/functions: `onForegroundLayerNodeSelected`, `setEnabled`, `setMRMLScene`
- API footprints: `EndSliceCompositeNodeInteraction`, `GetForegroundVolumeID`, `GetID`, `GetNodeByID`, `SetForegroundVolumeID`, `SetMRMLScene`, `StartSliceCompositeNodeInteraction`, `vtkMRMLScene::EndBatchProcessEvent`, `vtkMRMLScene::SceneImportedEvent`, `vtkMRMLSliceCompositeNode::ForegroundVolumeFlag`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}

## widget: ForegroundInterpolationButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ForegroundInterpolationButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:282: this->ForegroundInterpolationButton->setDefaultAction(this->actionForegroundInterpolation);`

## widget: SegmentationOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SegmentationOpacitySlider | ctkSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:128: this->SegmentationOpacitySlider->spinBox()->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:212: this->connect(this->SegmentationOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(setSegmentationOpacity(double)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:589: QWidgetAction* opacityAction = new QWidgetAction(this->SegmentationOpacitySlider);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:590: opacityAction->setDefaultWidget(this->SegmentationOpacitySlider->slider());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1007: this->SegmentationOpacitySlider->setEnabled(segmentationNode && segmentationNode->GetDisplayNodeID());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1036: this->SegmentationOpacitySlider->setEnabled(displayNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1049: this->SegmentationOpacitySlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1050: this->SegmentationOpacitySlider->setValue(displayNode->GetOpacity());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1051: this->SegmentationOpacitySlider->blockSignals(false);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2723: d->SegmentationOpacitySlider->setVisible(visible);`
- Connected slots/functions: `setSegmentationOpacity`
- API footprints: `GetDisplayNodeID`, `GetOpacity`, `SetOpacity`

## widget: SegmentSelectorWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSegmentSelectorWidget`
- Search text: SegmentSelectorWidget | qMRMLSegmentSelectorWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:224: this->connect(this->SegmentSelectorWidget, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onSegmentationNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:225: // this->connect(this->SegmentSelectorWidget, SIGNAL(currentNodeChanged(bool)),`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:227: this->connect(this->SegmentSelectorWidget, SIGNAL(currentNodeChanged(bool)), this->actionSegmentationOutlineFill, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:228: this->connect(this->SegmentSelectorWidget, SIGNAL(segmentSelectionChanged(QStringList)), this, SLOT(onSegmentVisibilitySelectionChanged(QStringList)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:257: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->SegmentSelectorWidget, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1027: if (!segmentationNode || segmentationNode != this->SegmentSelectorWidget->currentNode())`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1064: this->SegmentSelectorWidget->setSelectedSegmentIDs(visibleSegmentIDs);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1292: vtkMRMLSegmentationNode* segmentationNode = vtkMRMLSegmentationNode::SafeDownCast(this->SegmentSelectorWidget->currentNode());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1429: vtkMRMLSegmentationNode* segmentationNode = vtkMRMLSegmentationNode::SafeDownCast(this->SegmentSelectorWidget->currentNode());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1443: QStringList segmentIdsInSegmentSelectorWidget(this->SegmentSelectorWidget->segmentIDs());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1448: if (!segmentIdsInSegmentSelectorWidget.contains(segmentID))`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1517: // bool segmentationBlockSignals = d->SegmentSelectorWidget->blockSignals(true);`
- Connected slots/functions: `onSegmentVisibilitySelectionChanged`, `onSegmentationNodeSelected`, `setEnabled`, `setMRMLScene`
- API footprints: `GetDisplayNode`, `GetDisplayNodeID`, `GetFirstNode`, `GetSegmentIDs`, `GetSegmentVisibility`, `GetSegmentation`, `SetMRMLScene`, `SetSegmentVisibility`, `vtkMRMLDisplayableNode::DisplayModifiedEvent`, `vtkMRMLScene::EndBatchProcessEvent`, `vtkMRMLScene::SceneImportedEvent`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: BackgroundOpacitySlider

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSliderWidget`
- Search text: BackgroundOpacitySlider | ctkSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:131: this->BackgroundOpacitySlider->spinBox()->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:134: this->BackgroundOpacitySlider->slider()->setOrientation(Qt::Vertical);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:136: this->BackgroundOpacitySlider->popup()->setHideDelay(400);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:138: this->BackgroundOpacitySlider->popup()->setAlignment(Qt::AlignBottom | Qt::AlignLeft);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:141: this->BackgroundOpacitySlider->popup()->setFixedHeight(popupHeight);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:215: this->connect(this->BackgroundOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(setBackgroundOpacity(double)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:660: this->BackgroundOpacitySlider->setEnabled(false);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2015: if (hide && d->BackgroundOpacitySlider->value() != 0.)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2017: d->LastBackgroundOpacity = 1. - d->BackgroundOpacitySlider->value();`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2019: d->BackgroundOpacitySlider->setValue(hide ? 0. : d->LastBackgroundOpacity);`
- Connected slots/functions: `setBackgroundOpacity`

## widget: BackgroundInterpolationButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: BackgroundInterpolationButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:283: this->BackgroundInterpolationButton->setDefaultAction(this->actionBackgroundInterpolation);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::DelayedPopup"}

## widget: BackgroundComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select the background | BackgroundComboBox | qMRMLNodeComboBox
- Tooltip: Select the background
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:155: // this->BackgroundComboBox->setMinimumWidth(volumeSelectorMinWidth);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:165: this->connect(this->MoreButton, SIGNAL(toggled(bool)), q, SLOT(moveBackgroundComboBox(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:249: this->connect(this->BackgroundComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onBackgroundLayerNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:252: this->connect(this->BackgroundComboBox, SIGNAL(nodeActivated(vtkMRMLNode*)), SLOT(onBackgroundLayerNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:253: // this->connect(this->BackgroundComboBox, SIGNAL(currentNodeChanged(bool)),`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:255: this->connect(this->BackgroundComboBox, SIGNAL(currentNodeChanged(bool)), this->actionBackgroundInterpolation, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:260: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->BackgroundComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:911: wasBlocked = this->BackgroundComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:912: this->BackgroundComboBox->setCurrentNode(q->mrmlScene()->GetNodeByID(this->MRMLSliceCompositeNode->GetBackgroundVolumeID()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:913: this->BackgroundComboBox->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1512: bool backgroundBlockSignals = d->BackgroundComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1521: d->BackgroundComboBox->blockSignals(backgroundBlockSignals);`
- Connected slots/functions: `moveBackgroundComboBox`, `onBackgroundLayerNodeSelected`, `setEnabled`, `setMRMLScene`
- API footprints: `EndSliceCompositeNodeInteraction`, `GetBackgroundVolumeID`, `GetID`, `GetNodeByID`, `SetBackgroundVolumeID`, `SetMRMLScene`, `StartSliceCompositeNodeInteraction`, `vtkMRMLScene::EndBatchProcessEvent`, `vtkMRMLScene::SceneImportedEvent`, `vtkMRMLSliceCompositeNode::BackgroundVolumeFlag`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}

## widget: LabelMapIconLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: LabelMapIconLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`

## widget: ForegroundIconLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: ForegroundIconLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`

## widget: BackgroundIconLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: BackgroundIconLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`

## widget: MoreButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkExpandButton`
- Search text: MoreButton | ctkExpandButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:145: this->connect(this->MoreButton, SIGNAL(toggled(bool)), this->ForegroundOpacitySlider->spinBox(), SLOT(setVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:165: this->connect(this->MoreButton, SIGNAL(toggled(bool)), q, SLOT(moveBackgroundComboBox(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:166: this->connect(this->MoreButton, SIGNAL(toggled(bool)), q, SLOT(updateSegmentationControlsVisibility()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:364: this->MoreButton->setChecked(false);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1934: void qMRMLSliceControllerWidget::setMoreButtonVisible(bool visible)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1937: d->MoreButton->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1941: bool qMRMLSliceControllerWidget::isMoreButtonVisible() const`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1944: return d->MoreButton->isVisibleTo(const_cast<qMRMLSliceControllerWidget*>(this));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2705: bool popupVisible = d->MoreButton->isChecked();`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h:61: Q_PROPERTY(bool moreButtonVisibility READ isMoreButtonVisible WRITE setMoreButtonVisible)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h:202: /// Set the visibility of the MoreButton which allows to show the advanced`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h:204: void setMoreButtonVisible(bool visible);`
- Connected slots/functions: `moveBackgroundComboBox`, `setVisible`, `updateSegmentationControlsVisibility`
- API footprints: `GetFirstNode`
- Key UI properties: {"checked": "true"}

## widget: SliceFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: SliceFrame | QFrame
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1959: d->SliceFrame->layout()->addWidget(d->BackgroundComboBox);`

## widget: SliceLinkButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Link slice views. Synchronizes properties of all slice views in the same view group. | SliceLinkButton | QToolButton
- Tooltip: Link slice views. Synchronizes properties of all slice views in the same view group.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:169: this->connect(this->SliceLinkButton, SIGNAL(clicked(bool)), q, SLOT(setSliceLink(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:400: QMenu* linkedMenu = new QMenu(tr("Linked"), this->SliceLinkButton);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:407: this->SliceLinkButton->setMenu(linkedMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:885: this->SliceLinkButton->setChecked(this->MRMLSliceCompositeNode->GetLinkedControl());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:891: this->SliceLinkButton->setIcon(QIcon(":Icons/HotLinkOn.png"));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:895: this->SliceLinkButton->setIcon(QIcon(":Icons/LinkOn.png"));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:900: this->SliceLinkButton->setIcon(QIcon(":Icons/LinkOff.png"));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1891: //         d->SliceLinkButton->isChecked());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1892: return d->MRMLSliceCompositeNode ? d->MRMLSliceCompositeNode->GetLinkedControl() : d->SliceLinkButton->isChecked();`
- Connected slots/functions: `setSliceLink`
- API footprints: `Delete`, `GetHotLinkedControl`, `GetLinkedControl`, `GetNextItemAsObject`, `GetNodesByClass`, `InitTraversal`, `SetLinkedControl`, `vtkMRMLSliceCompositeNode::SafeDownCast`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: SliceVisibilityButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Toggle slice visibility in the 3D view. | SliceVisibilityButton | QToolButton
- Tooltip: Toggle slice visibility in the 3D view.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:263: this->SliceVisibilityButton->setDefaultAction(this->actionShow_in_3D);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:269: this->SliceVisibilityButton->setMenu(this->SliceModelMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:492: this->SliceModelMenu = new QMenu(tr("Slice model mode"), this->SliceVisibilityButton);`
- Key UI properties: {"checkable": "true", "checked": "false", "popupMode": "QToolButton::ToolButtonPopupMode::MenuButtonPopup"}

## widget: SliceOrientationSelector

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: Slice orientation (Axial, Sagittal, Coronal, Reformat). | SliceOrientationSelector | ctkComboBox
- Tooltip: Slice orientation (Axial, Sagittal, Coronal, Reformat).
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:153: // this->SliceOrientationSelector->setMinimumWidth(volumeSelectorMinWidth);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:172: this->connect(this->SliceOrientationSelector, &QComboBox::currentTextChanged, q, &qMRMLSliceControllerWidget::setSliceOrientation);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:683: void qMRMLSliceControllerWidgetPrivate::updateSliceOrientationSelector(vtkMRMLSliceNode* sliceNode, QComboBox* sliceOrientationSelector)`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:740: Self::updateSliceOrientationSelector(sliceNode, this->SliceOrientationSelector);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1833: return d->SliceOrientationSelector->currentText();`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h:107: static void updateSliceOrientationSelector(vtkMRMLSliceNode* sliceNode, QComboBox* sliceOrientationSelector);`
- Connected slots/functions: `currentTextChanged`, `setSliceOrientation`
- API footprints: `EndSliceNodeInteraction`, `GetLayoutLabel`, `SetOrientation`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::OrientationFlag`

## widget: ShowReformatWidgetToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Show reformat widget in 3D view | ShowReformatWidgetToolButton | QToolButton
- Tooltip: Show reformat widget in 3D view
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:264: this->ShowReformatWidgetToolButton->setDefaultAction(this->actionShow_reformat_widget);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:414: QMenu* reformatMenu = new QMenu(tr("Reformat"), this->ShowReformatWidgetToolButton);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:421: this->ShowReformatWidgetToolButton->setMenu(reformatMenu);`
- Key UI properties: {"checkable": "true"}

## widget: SliceCompositeButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: SliceCompositeButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:267: this->SliceCompositeButton->setMenu(this->CompositingMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:428: this->CompositingMenu = new QMenu(tr("Compositing"), this->SliceCompositeButton);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::InstantPopup"}

## widget: SliceSpacingButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Slice spacing may be set automatically or manually by the user or context | SliceSpacingButton | QToolButton
- Tooltip: Slice spacing may be set automatically or manually by the user or context
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:268: this->SliceSpacingButton->setMenu(this->SliceSpacingMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:450: this->SliceSpacingMenu = new QMenu(tr("Slice spacing mode"), this->SliceSpacingButton);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:778: this->SliceSpacingButton->setIcon(sliceNode->GetSliceSpacingMode() == vtkMRMLSliceNode::AutomaticSliceSpacingMode ? QIcon(":/Icons/SlicerAutomaticSliceSpacing.png")`
- API footprints: `GetSliceSpacingMode`, `vtkMRMLSliceNode::AutomaticSliceSpacingMode`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::InstantPopup"}

## widget: SliceRotateToVolumePlaneButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: SliceRotateToVolumePlaneButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:270: this->SliceRotateToVolumePlaneButton->setDefaultAction(this->actionRotate_to_volume_plane);`

## widget: OrientationMarkerButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Show orientation marker | OrientationMarkerButton | QToolButton
- Tooltip: Show orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1335: this->OrientationMarkerButton->setMenu(orientationMarkerMenu);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::InstantPopup"}

## widget: RulerButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: ... | RulerButton | QToolButton
- Text: ...
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1371: this->RulerButton->setMenu(rulerMenu);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::InstantPopup"}

## widget: EnableSlabReconstructionButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Enable Thick Slab Reconstruction (TSR). TSR is used to merge contiguous slices within a certain range. | EnableSlabReconstructionButton | QToolButton
- Tooltip: Enable Thick Slab Reconstruction (TSR). TSR is used to merge contiguous slices within a certain range.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:266: this->EnableSlabReconstructionButton->setMenu(this->SlabReconstructionMenu);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1381: this->SlabReconstructionMenu = new QMenu(tr("Thick slab reconstruction"), this->EnableSlabReconstructionButton);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1391: QMenu* slabReconstructionThicknessMenu = new QMenu(tr("Slab thickness"), this->EnableSlabReconstructionButton);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::InstantPopup"}

## widget: SliceMoreOptionButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Advanced options | SliceMoreOptionButton | QToolButton
- Tooltip: Advanced options
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:271: this->SliceMoreOptionButton->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:606: QMenu* advancedMenu = new QMenu(tr("Advanced"), this->SliceMoreOptionButton);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:613: this->SliceMoreOptionButton->setMenu(advancedMenu);`
- Key UI properties: {"popupMode": "QToolButton::ToolButtonPopupMode::InstantPopup"}

## widget: DynamicSpacer

- Confidence: `linked_to_code`
- Widget/action class: `ctkDynamicSpacer`
- Search text: DynamicSpacer | ctkDynamicSpacer
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:36: #include <ctkDynamicSpacer.h>`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:318: this->SliderSpacer = new ctkDynamicSpacer(q);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h:54: class ctkDynamicSpacer;`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h:173: ctkDynamicSpacer* SliderSpacer;`

## widget: SegmentationIconLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: SegmentationIconLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2721: d->SegmentationIconLabel->setVisible(visible);`

## action: actionHotLinked

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Hot linked | Set linking behavior to hot linked controls. When on, Slice interactions affect other slices immediately. When off, Slice interactions affect other slices after the interaction completes. | actionHotLinked
- Text: Hot linked
- Tooltip: Set linking behavior to hot linked controls. When on, Slice interactions affect other slices immediately. When off, Slice interactions affect other slices after the interaction completes.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:403: linkedMenu->addAction(this->actionHotLinked);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:405: QObject::connect(this->actionHotLinked, SIGNAL(toggled(bool)), q, SLOT(setHotLinked(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:886: this->actionHotLinked->setChecked(this->MRMLSliceCompositeNode->GetHotLinkedControl());`
- Connected slots/functions: `setHotLinked`
- API footprints: `Delete`, `GetHotLinkedControl`, `GetLinkedControl`, `GetNextItemAsObject`, `GetNodesByClass`, `InitTraversal`, `SetHotLinkedControl`, `vtkMRMLSliceCompositeNode::SafeDownCast`
- Key UI properties: {"checkable": "true"}

## action: actionFit_to_window

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Fit to window | Reset field of view. Adjusts the slice view's field of view to match the extent of lowest volume layer (background, then foreground, then label). | actionFit_to_window
- Text: Fit to window
- Tooltip: Reset field of view. Adjusts the slice view's field of view to match the extent of lowest volume layer (background, then foreground, then label).
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:176: QObject::connect(this->actionFit_to_window, SIGNAL(triggered()), q, SLOT(fitSliceToBackground()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:315: this->FitToWindowToolButton->setDefaultAction(this->actionFit_to_window);`
- Connected slots/functions: `fitSliceToBackground`
- API footprints: `EndSliceNodeInteraction`, `FitSliceToBackground`, `StartSliceNodeInteraction`, `UpdateMatrices`, `vtkMRMLSliceNode::FieldOfViewFlag`, `vtkMRMLSliceNode::ResetFieldOfViewFlag`

## action: actionRotate_to_volume_plane

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Rotate to volume plane | Rotate to volume plane | actionRotate_to_volume_plane
- Text: Rotate to volume plane
- Tooltip: Rotate to volume plane
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:177: QObject::connect(this->actionRotate_to_volume_plane, SIGNAL(triggered()), q, SLOT(rotateSliceToLowestVolumeAxes()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:270: this->SliceRotateToVolumePlaneButton->setDefaultAction(this->actionRotate_to_volume_plane);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:609: advancedMenu->addAction(this->actionRotate_to_volume_plane);`
- Connected slots/functions: `rotateSliceToLowestVolumeAxes`
- API footprints: `EndSliceNodeInteraction`, `GetPointer`, `RotateSliceToLowestVolumeAxes`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::RotateToBackgroundVolumePlaneFlag`

## action: actionLabelMapOutline

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Hide labelmap outlines | Toggle between showing label map volume with regions outlined or filled. | actionLabelMapOutline
- Text: Hide labelmap outlines
- Tooltip: Toggle between showing label map volume with regions outlined or filled.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:219: QObject::connect(this->actionLabelMapOutline, SIGNAL(toggled(bool)), q, SLOT(showLabelOutline(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:237: this->connect(this->LabelMapComboBox, SIGNAL(currentNodeChanged(bool)), this->actionLabelMapOutline, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:281: this->LabelMapOutlineButton->setDefaultAction(this->actionLabelMapOutline);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:669: this->actionLabelMapOutline->setEnabled(hasLabelMap);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:756: this->actionLabelMapOutline->setChecked(showOutline);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:757: this->actionLabelMapOutline->setText(showOutline ? tr("Hide label volume outlines") : tr("Show label volume outlines"));`
- Connected slots/functions: `setEnabled`, `showLabelOutline`
- API footprints: `EndSliceNodeInteraction`, `GetPointer`, `GetUseLabelOutline`, `GetWidgetVisible`, `SetUseLabelOutline`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::LabelOutlineFlag`
- Key UI properties: {"checkable": "true"}

## action: actionShow_reformat_widget

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Show reformat widget | actionShow_reformat_widget
- Text: Show reformat widget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:178: QObject::connect(this->actionShow_reformat_widget, SIGNAL(triggered(bool)), q, SLOT(showReformatWidget(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:264: this->ShowReformatWidgetToolButton->setDefaultAction(this->actionShow_reformat_widget);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:760: this->actionShow_reformat_widget->setChecked(showReformat);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:761: this->actionShow_reformat_widget->setText(showReformat ? tr("Hide reformat widget") : tr("Show reformat widget"));`
- Connected slots/functions: `showReformatWidget`
- API footprints: `GetNextItemAsObject`, `GetPointer`, `GetWidgetVisible`, `InitTraversal`, `SetWidgetVisible`
- Key UI properties: {"checkable": "true"}

## action: actionEnable_slab_reconstruction_widget

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Enable Thick Slab Reconstruction | actionEnable_slab_reconstruction_widget
- Text: Enable Thick Slab Reconstruction
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:193: QObject::connect(this->actionEnable_slab_reconstruction_widget, SIGNAL(toggled(bool)), q, SLOT(showSlabReconstructionWidget(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:764: this->actionEnable_slab_reconstruction_widget->setChecked(sliceNode->GetSlabReconstructionEnabled());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1382: this->SlabReconstructionMenu->addAction(this->actionEnable_slab_reconstruction_widget);`
- Connected slots/functions: `showSlabReconstructionWidget`
- API footprints: `GetMRMLApplicationLogic`, `GetNextItemAsObject`, `GetPointer`, `GetSlabReconstructionEnabled`, `GetSliceDisplayNode`, `GetSliceLogic`, `InitTraversal`, `SetIntersectingThickSlabVisibility`, `SetSlabReconstructionEnabled`, `vtkMRMLSliceViewDisplayableManagerFactory::GetInstance`
- Key UI properties: {"checkable": "true"}

## action: actionSlabReconstructionInteractive

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Interactive | actionSlabReconstructionInteractive
- Text: Interactive
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:194: QObject::connect(this->actionSlabReconstructionInteractive, SIGNAL(toggled(bool)), q, SLOT(toggleSlabReconstructionInteractive(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:766: this->actionSlabReconstructionInteractive->setEnabled(sliceNode->GetSlabReconstructionEnabled());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:769: this->actionSlabReconstructionInteractive->setChecked(slabReconstructionInteractive);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1386: this->SlabReconstructionMenu->addAction(this->actionSlabReconstructionInteractive);`
- Connected slots/functions: `toggleSlabReconstructionInteractive`
- API footprints: `GetIntersectingThickSlabInteractive`, `GetMRMLApplicationLogic`, `GetSlabReconstructionEnabled`, `GetSliceDisplayNode`, `SetIntersectingSlicesEnabled`, `vtkMRMLApplicationLogic::IntersectingSlicesThickSlabInteractive`, `vtkMRMLSliceViewDisplayableManagerFactory::GetInstance`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeCube

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Cube | actionOrientationMarkerTypeCube
- Text: Cube
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1309: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeCube, vtkMRMLAbstractViewNode::OrientationMarkerTypeCube);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1315: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeCube);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeNone`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeHuman

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Human | actionOrientationMarkerTypeHuman
- Text: Human
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1310: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeHuman, vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1316: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeHuman);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeNone`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeAxes

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Axes | actionOrientationMarkerTypeAxes
- Text: Axes
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1311: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeAxes, vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1317: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeAxes);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`
- Key UI properties: {"checkable": "true"}

## action: actionCompositingAlpha_blend

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Alpha blend | actionCompositingAlpha_blend
- Text: Alpha blend
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:179: QObject::connect(this->actionCompositingAlpha_blend, SIGNAL(triggered()), q, SLOT(setCompositingToAlphaBlend()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:431: this->CompositingMenu->addAction(this->actionCompositingAlpha_blend);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:438: compositingGroup->addAction(this->actionCompositingAlpha_blend);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:931: case vtkMRMLSliceCompositeNode::Alpha: this->actionCompositingAlpha_blend->setChecked(true); break;`
- Connected slots/functions: `setCompositingToAlphaBlend`
- API footprints: `GetCompositing`, `vtkMRMLSliceCompositeNode::Add`, `vtkMRMLSliceCompositeNode::Alpha`, `vtkMRMLSliceCompositeNode::ReverseAlpha`
- Key UI properties: {"checkable": "true"}

## action: actionCompositingReverse_alpha_blend

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Reverse alpha blend | actionCompositingReverse_alpha_blend
- Text: Reverse alpha blend
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:180: QObject::connect(this->actionCompositingReverse_alpha_blend, SIGNAL(triggered()), q, SLOT(setCompositingToReverseAlphaBlend()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:432: this->CompositingMenu->addAction(this->actionCompositingReverse_alpha_blend);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:439: compositingGroup->addAction(this->actionCompositingReverse_alpha_blend);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:932: case vtkMRMLSliceCompositeNode::ReverseAlpha: this->actionCompositingReverse_alpha_blend->setChecked(true); break;`
- Connected slots/functions: `setCompositingToReverseAlphaBlend`
- API footprints: `vtkMRMLSliceCompositeNode::Add`, `vtkMRMLSliceCompositeNode::Alpha`, `vtkMRMLSliceCompositeNode::ReverseAlpha`, `vtkMRMLSliceCompositeNode::Subtract`
- Key UI properties: {"checkable": "true"}

## action: actionCompositingAdd

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Add | actionCompositingAdd
- Text: Add
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:181: QObject::connect(this->actionCompositingAdd, SIGNAL(triggered()), q, SLOT(setCompositingToAdd()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:433: this->CompositingMenu->addAction(this->actionCompositingAdd);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:440: compositingGroup->addAction(this->actionCompositingAdd);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:933: case vtkMRMLSliceCompositeNode::Add: this->actionCompositingAdd->setChecked(true); break;`
- Connected slots/functions: `setCompositingToAdd`
- API footprints: `vtkMRMLSliceCompositeNode::Add`, `vtkMRMLSliceCompositeNode::Alpha`, `vtkMRMLSliceCompositeNode::ReverseAlpha`, `vtkMRMLSliceCompositeNode::Subtract`
- Key UI properties: {"checkable": "true"}

## action: actionCompositingSubtract

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Subtract | actionCompositingSubtract
- Text: Subtract
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:182: QObject::connect(this->actionCompositingSubtract, SIGNAL(triggered()), q, SLOT(setCompositingToSubtract()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:434: this->CompositingMenu->addAction(this->actionCompositingSubtract);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:441: compositingGroup->addAction(this->actionCompositingSubtract);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:934: case vtkMRMLSliceCompositeNode::Subtract: this->actionCompositingSubtract->setChecked(true); break;`
- Connected slots/functions: `setCompositingToSubtract`
- API footprints: `vtkMRMLSliceCompositeNode::Add`, `vtkMRMLSliceCompositeNode::ReverseAlpha`, `vtkMRMLSliceCompositeNode::Subtract`
- Key UI properties: {"checkable": "true"}

## action: actionSliceSpacingModeAutomatic

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Automatic | actionSliceSpacingModeAutomatic
- Text: Automatic
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:184: QObject::connect(this->actionSliceSpacingModeAutomatic, SIGNAL(toggled(bool)), q, SLOT(setSliceSpacingMode(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:453: this->SliceSpacingMenu->addAction(this->actionSliceSpacingModeAutomatic);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:780: this->actionSliceSpacingModeAutomatic->setChecked(sliceNode->GetSliceSpacingMode() == vtkMRMLSliceNode::AutomaticSliceSpacingMode);`
- Connected slots/functions: `setSliceSpacingMode`
- API footprints: `EndSliceNodeInteraction`, `GetSliceSpacingMode`, `SetSliceSpacingModeToAutomatic`, `SetSliceSpacingModeToPrescribed`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::AutomaticSliceSpacingMode`, `vtkMRMLSliceNode::SliceSpacingFlag`
- Key UI properties: {"checkable": "true"}

## action: actionSliceModelModeVolumes

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: FOV, Spacing match Volumes | actionSliceModelModeVolumes
- Text: FOV, Spacing match Volumes
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:186: QObject::connect(this->actionSliceModelModeVolumes, SIGNAL(triggered()), q, SLOT(setSliceModelModeVolumes()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:189: QObject::connect(this->actionSliceModelModeVolumes_2D, SIGNAL(triggered()), q, SLOT(setSliceModelModeVolumes_2D()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:494: this->SliceModelMenu->addAction(this->actionSliceModelModeVolumes);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:497: this->SliceModelMenu->addAction(this->actionSliceModelModeVolumes_2D);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:792: this->actionSliceModelModeVolumes->setChecked(sliceNode->GetSliceResolutionMode() == vtkMRMLSliceNode::SliceResolutionMatchVolumes);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:795: this->actionSliceModelModeVolumes_2D->setChecked(sliceNode->GetSliceResolutionMode() == vtkMRMLSliceNode::SliceFOVMatchVolumesSpacingMatch2DView);`
- Connected slots/functions: `setSliceModelModeVolumes`, `setSliceModelModeVolumes_2D`
- API footprints: `GetSliceResolutionMode`, `vtkMRMLSliceNode::SliceFOVMatch2DViewSpacingMatchVolumes`, `vtkMRMLSliceNode::SliceFOVMatchVolumesSpacingMatch2DView`, `vtkMRMLSliceNode::SliceResolutionCustom`, `vtkMRMLSliceNode::SliceResolutionMatch2DView`, `vtkMRMLSliceNode::SliceResolutionMatchVolumes`
- Key UI properties: {"checkable": "true"}

## action: actionSliceModelMode2D

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: FOV, Spacing match 2D | actionSliceModelMode2D
- Text: FOV, Spacing match 2D
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:187: QObject::connect(this->actionSliceModelMode2D, SIGNAL(triggered()), q, SLOT(setSliceModelMode2D()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:188: QObject::connect(this->actionSliceModelMode2D_Volumes, SIGNAL(triggered()), q, SLOT(setSliceModelMode2D_Volumes()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:495: this->SliceModelMenu->addAction(this->actionSliceModelMode2D);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:496: this->SliceModelMenu->addAction(this->actionSliceModelMode2D_Volumes);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:793: this->actionSliceModelMode2D->setChecked(sliceNode->GetSliceResolutionMode() == vtkMRMLSliceNode::SliceResolutionMatch2DView);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:794: this->actionSliceModelMode2D_Volumes->setChecked(sliceNode->GetSliceResolutionMode() == vtkMRMLSliceNode::SliceFOVMatch2DViewSpacingMatchVolumes);`
- Connected slots/functions: `setSliceModelMode2D`, `setSliceModelMode2D_Volumes`
- API footprints: `GetSliceResolutionMode`, `vtkMRMLSliceNode::SliceFOVMatch2DViewSpacingMatchVolumes`, `vtkMRMLSliceNode::SliceFOVMatchVolumesSpacingMatch2DView`, `vtkMRMLSliceNode::SliceResolutionMatch2DView`, `vtkMRMLSliceNode::SliceResolutionMatchVolumes`
- Key UI properties: {"checkable": "true"}

## action: actionSliceModelMode2D_Volumes

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: FOV matches 2D, Spacing matches Volumes | actionSliceModelMode2D_Volumes
- Text: FOV matches 2D, Spacing matches Volumes
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:188: QObject::connect(this->actionSliceModelMode2D_Volumes, SIGNAL(triggered()), q, SLOT(setSliceModelMode2D_Volumes()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:496: this->SliceModelMenu->addAction(this->actionSliceModelMode2D_Volumes);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:794: this->actionSliceModelMode2D_Volumes->setChecked(sliceNode->GetSliceResolutionMode() == vtkMRMLSliceNode::SliceFOVMatch2DViewSpacingMatchVolumes);`
- Connected slots/functions: `setSliceModelMode2D_Volumes`
- API footprints: `GetSliceResolutionMode`, `vtkMRMLSliceNode::SliceFOVMatch2DViewSpacingMatchVolumes`, `vtkMRMLSliceNode::SliceFOVMatchVolumesSpacingMatch2DView`, `vtkMRMLSliceNode::SliceResolutionMatch2DView`, `vtkMRMLSliceNode::SliceResolutionMatchVolumes`
- Key UI properties: {"checkable": "true"}

## action: actionSliceModelModeVolumes_2D

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: FOV matches Volumes, Spacing matches 2D View | actionSliceModelModeVolumes_2D
- Text: FOV matches Volumes, Spacing matches 2D View
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:189: QObject::connect(this->actionSliceModelModeVolumes_2D, SIGNAL(triggered()), q, SLOT(setSliceModelModeVolumes_2D()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:497: this->SliceModelMenu->addAction(this->actionSliceModelModeVolumes_2D);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:795: this->actionSliceModelModeVolumes_2D->setChecked(sliceNode->GetSliceResolutionMode() == vtkMRMLSliceNode::SliceFOVMatchVolumesSpacingMatch2DView);`
- Connected slots/functions: `setSliceModelModeVolumes_2D`
- API footprints: `GetSliceResolutionMode`, `vtkMRMLSliceNode::SliceFOVMatch2DViewSpacingMatchVolumes`, `vtkMRMLSliceNode::SliceFOVMatchVolumesSpacingMatch2DView`, `vtkMRMLSliceNode::SliceResolutionCustom`, `vtkMRMLSliceNode::SliceResolutionMatch2DView`
- Key UI properties: {"checkable": "true"}

## action: actionAdjustDisplayForeground_volume

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Foreground volume | actionAdjustDisplayForeground_volume
- Text: Foreground volume
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Key UI properties: {"checkable": "true"}

## action: actionAdjustDisplayBackground_volume

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Background volume | actionAdjustDisplayBackground_volume
- Text: Background volume
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Key UI properties: {"checkable": "true"}

## action: actionAdjustDisplayLabel_map_volume

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Label map volume | actionAdjustDisplayLabel_map_volume
- Text: Label map volume
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Key UI properties: {"checkable": "true"}

## action: actionForegroundInterpolation

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Interpolate foreground | actionForegroundInterpolation
- Text: Interpolate foreground
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:220: QObject::connect(this->actionForegroundInterpolation, SIGNAL(toggled(bool)), q, SLOT(setForegroundInterpolation(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:246: this->connect(this->ForegroundComboBox, SIGNAL(currentNodeChanged(bool)), this->actionForegroundInterpolation, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:282: this->ForegroundInterpolationButton->setDefaultAction(this->actionForegroundInterpolation);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:671: this->actionForegroundInterpolation->setEnabled(hasForeground);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1170: bool wasBlocked = this->actionForegroundInterpolation->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1171: this->actionForegroundInterpolation->setChecked(displayNode->GetInterpolate());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1172: this->actionForegroundInterpolation->blockSignals(wasBlocked);`
- Connected slots/functions: `setEnabled`, `setForegroundInterpolation`
- API footprints: `GetForegroundLayer`, `GetInterpolate`, `GetVolumeDisplayNode`, `GetVolumeNode`, `Modified`, `SaveStateForUndo`, `SetInterpolate`, `vtkMRMLScalarVolumeDisplayNode::SafeDownCast`
- Key UI properties: {"checkable": "true"}

## action: actionBackgroundInterpolation

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Interpolate background | actionBackgroundInterpolation
- Text: Interpolate background
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:221: QObject::connect(this->actionBackgroundInterpolation, SIGNAL(toggled(bool)), q, SLOT(setBackgroundInterpolation(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:255: this->connect(this->BackgroundComboBox, SIGNAL(currentNodeChanged(bool)), this->actionBackgroundInterpolation, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:283: this->BackgroundInterpolationButton->setDefaultAction(this->actionBackgroundInterpolation);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:670: this->actionBackgroundInterpolation->setEnabled(hasBackground);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1192: bool wasBlocked = this->actionBackgroundInterpolation->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1193: this->actionBackgroundInterpolation->setChecked(displayNode->GetInterpolate());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1194: this->actionBackgroundInterpolation->blockSignals(wasBlocked);`
- Connected slots/functions: `setBackgroundInterpolation`, `setEnabled`
- API footprints: `GetBackgroundLayer`, `GetInterpolate`, `GetVolumeDisplayNode`, `GetVolumeNode`, `Modified`, `SaveStateForUndo`, `SetInterpolate`, `vtkMRMLScalarVolumeDisplayNode::SafeDownCast`
- Key UI properties: {"checkable": "true"}

## action: actionLabelMapVisibility

- Confidence: `linked_to_slot`
- Widget/action class: `action`
- Search text: Show LabelMap | Toggle labelmap visibility | actionLabelMapVisibility
- Text: Show LabelMap
- Tooltip: Toggle labelmap visibility
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:207: this->connect(this->actionLabelMapVisibility, SIGNAL(triggered(bool)), q, SLOT(setLabelMapHidden(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:236: //               this->actionLabelMapVisibility, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:277: this->LabelMapVisibilityButton->setDefaultAction(this->actionLabelMapVisibility);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:665: this->actionLabelMapVisibility->setEnabled(enableVisibility && hasLabelMap);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2052: d->actionLabelMapVisibility->setChecked(opacity == 0.);`
- Connected slots/functions: `setEnabled`, `setLabelMapHidden`
- Key UI properties: {"checkable": "true"}

## action: actionForegroundVisibility

- Confidence: `linked_to_slot`
- Widget/action class: `action`
- Search text: Show Foreground | Toggle foreground visibility | actionForegroundVisibility
- Text: Show Foreground
- Tooltip: Toggle foreground visibility
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:208: this->connect(this->actionForegroundVisibility, SIGNAL(triggered(bool)), q, SLOT(setForegroundHidden(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:245: //               this->actionForegroundVisibility, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:662: this->actionForegroundVisibility->setEnabled(enableVisibility && hasForeground);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2075: d->actionForegroundVisibility->setChecked(opacity == 0.);`
- Connected slots/functions: `setEnabled`, `setForegroundHidden`
- Key UI properties: {"checkable": "true"}

## action: actionBackgroundVisibility

- Confidence: `linked_to_slot`
- Widget/action class: `action`
- Search text: Show Background | Toggle background visibility | actionBackgroundVisibility
- Text: Show Background
- Tooltip: Toggle background visibility
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:209: this->connect(this->actionBackgroundVisibility, SIGNAL(triggered(bool)), q, SLOT(setBackgroundHidden(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:254: //               this->actionBackgroundVisibility, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:659: this->actionBackgroundVisibility->setEnabled(false);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:2083: d->actionBackgroundVisibility->setChecked(opacity == 1.);`
- Connected slots/functions: `setBackgroundHidden`, `setEnabled`
- Key UI properties: {"checkable": "true"}

## action: actionShow_in_3D

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Show in 3D | Toggle slice visibility in 3D view | actionShow_in_3D
- Text: Show in 3D
- Tooltip: Toggle slice visibility in 3D view
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:174: QObject::connect(this->actionShow_in_3D, SIGNAL(toggled(bool)), q, SLOT(setSliceVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:263: this->SliceVisibilityButton->setDefaultAction(this->actionShow_in_3D);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:751: this->actionShow_in_3D->setChecked(sliceNode->GetSliceVisible());`
- Connected slots/functions: `setSliceVisible`
- API footprints: `EndSliceNodeInteraction`, `GetSliceVisible`, `GetWidgetNormalLockedToCamera`, `SetSliceVisible`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::SliceVisibleFlag`
- Key UI properties: {"checkable": "true"}

## action: actionLockNormalToCamera

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Lock Normal To Camera | Lock reformat widget's normal to the camera one.  | actionLockNormalToCamera
- Text: Lock Normal To Camera
- Tooltip: Lock reformat widget's normal to the camera one. 
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:417: reformatMenu->addAction(this->actionLockNormalToCamera);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:419: QObject::connect(this->actionLockNormalToCamera, SIGNAL(triggered(bool)), q, SLOT(lockReformatWidgetToCamera(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:752: this->actionLockNormalToCamera->setChecked(sliceNode->GetWidgetNormalLockedToCamera());`
- Connected slots/functions: `lockReformatWidgetToCamera`
- API footprints: `GetNextItemAsObject`, `GetPointer`, `GetSliceVisible`, `GetWidgetNormalLockedToCamera`, `InitTraversal`, `SetWidgetNormalLockedToCamera`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeNone

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: No orientation marker | Hide orientation marker | actionOrientationMarkerTypeNone
- Text: No orientation marker
- Tooltip: Hide orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1308: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeNone, vtkMRMLAbstractViewNode::OrientationMarkerTypeNone);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1314: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeNone);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeNone`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerSizeSmall

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Small | Set orientation marker size to small | actionOrientationMarkerSizeSmall
- Text: Small
- Tooltip: Set orientation marker size to small
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1322: this->OrientationMarkerSizesMapper->setMapping(this->actionOrientationMarkerSizeSmall, vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1327: orientationMarkerSizesActions->addAction(this->actionOrientationMarkerSizeSmall);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerSizeMedium

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Medium | Set orientation marker size to small to medium | actionOrientationMarkerSizeMedium
- Text: Medium
- Tooltip: Set orientation marker size to small to medium
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1323: this->OrientationMarkerSizesMapper->setMapping(this->actionOrientationMarkerSizeMedium, vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1328: orientationMarkerSizesActions->addAction(this->actionOrientationMarkerSizeMedium);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerSizeLarge

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Large | Set orientation marker size to large | actionOrientationMarkerSizeLarge
- Text: Large
- Tooltip: Set orientation marker size to large
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1324: this->OrientationMarkerSizesMapper->setMapping(this->actionOrientationMarkerSizeLarge, vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1329: orientationMarkerSizesActions->addAction(this->actionOrientationMarkerSizeLarge);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall`
- Key UI properties: {"checkable": "true"}

## action: actionRulerTypeNone

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: No ruler | Hide ruler | actionRulerTypeNone
- Text: No ruler
- Tooltip: Hide ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1348: this->RulerTypesMapper->setMapping(this->actionRulerTypeNone, vtkMRMLAbstractViewNode::RulerTypeNone);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1357: rulerTypesActions->addAction(this->actionRulerTypeNone);`
- API footprints: `vtkMRMLAbstractViewNode::RulerTypeNone`, `vtkMRMLAbstractViewNode::RulerTypeThick`, `vtkMRMLAbstractViewNode::RulerTypeThin`
- Key UI properties: {"checkable": "true"}

## action: actionRulerTypeThin

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Thin | Show thin ruler | actionRulerTypeThin
- Text: Thin
- Tooltip: Show thin ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1349: this->RulerTypesMapper->setMapping(this->actionRulerTypeThin, vtkMRMLAbstractViewNode::RulerTypeThin);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1358: rulerTypesActions->addAction(this->actionRulerTypeThin);`
- API footprints: `vtkMRMLAbstractViewNode::RulerTypeNone`, `vtkMRMLAbstractViewNode::RulerTypeThick`, `vtkMRMLAbstractViewNode::RulerTypeThin`
- Key UI properties: {"checkable": "true"}

## action: actionRulerTypeThick

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Thick | Show thick ruler | actionRulerTypeThick
- Text: Thick
- Tooltip: Show thick ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1350: this->RulerTypesMapper->setMapping(this->actionRulerTypeThick, vtkMRMLAbstractViewNode::RulerTypeThick);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1359: rulerTypesActions->addAction(this->actionRulerTypeThick);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerTypeNone`, `vtkMRMLAbstractViewNode::RulerTypeThick`, `vtkMRMLAbstractViewNode::RulerTypeThin`
- Key UI properties: {"checkable": "true"}

## action: actionRulerColorWhite

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: White ruler | actionRulerColorWhite
- Text: White ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1353: this->RulerColorMapper->setMapping(this->actionRulerColorWhite, vtkMRMLAbstractViewNode::RulerColorWhite);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1363: rulerColorActions->addAction(this->actionRulerColorWhite);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerColorWhite`, `vtkMRMLAbstractViewNode::RulerColorYellow`
- Key UI properties: {"checkable": "true"}

## action: actionRulerColorBlack

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Black ruler | actionRulerColorBlack
- Text: Black ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1352: this->RulerColorMapper->setMapping(this->actionRulerColorBlack, vtkMRMLAbstractViewNode::RulerColorBlack);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1364: rulerColorActions->addAction(this->actionRulerColorBlack);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerColorWhite`, `vtkMRMLAbstractViewNode::RulerColorYellow`, `vtkMRMLAbstractViewNode::RulerTypeThick`
- Key UI properties: {"checkable": "true"}

## action: actionRulerColorYellow

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Yellow ruler | actionRulerColorYellow
- Text: Yellow ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1354: this->RulerColorMapper->setMapping(this->actionRulerColorYellow, vtkMRMLAbstractViewNode::RulerColorYellow);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1365: rulerColorActions->addAction(this->actionRulerColorYellow);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerColorWhite`, `vtkMRMLAbstractViewNode::RulerColorYellow`
- Key UI properties: {"checkable": "true"}

## action: actionSlabReconstructionMax

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Max | Set slab reconstruction type to Max | actionSlabReconstructionMax
- Text: Max
- Tooltip: Set slab reconstruction type to Max
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1407: this->SlabReconstructionTypesMapper->setMapping(this->actionSlabReconstructionMax, VTK_IMAGE_SLAB_MAX);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1413: slabReconstructionTypesActions->addAction(this->actionSlabReconstructionMax);`
- Key UI properties: {"checkable": "true"}

## action: actionSlabReconstructionMin

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Min | Set slab reconstruction type to Min | actionSlabReconstructionMin
- Text: Min
- Tooltip: Set slab reconstruction type to Min
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1408: this->SlabReconstructionTypesMapper->setMapping(this->actionSlabReconstructionMin, VTK_IMAGE_SLAB_MIN);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1414: slabReconstructionTypesActions->addAction(this->actionSlabReconstructionMin);`
- Key UI properties: {"checkable": "true"}

## action: actionSlabReconstructionMean

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Mean | Set slab reconstruction type to Mean | actionSlabReconstructionMean
- Text: Mean
- Tooltip: Set slab reconstruction type to Mean
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1409: this->SlabReconstructionTypesMapper->setMapping(this->actionSlabReconstructionMean, VTK_IMAGE_SLAB_MEAN);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1415: slabReconstructionTypesActions->addAction(this->actionSlabReconstructionMean);`
- Key UI properties: {"checkable": "true"}

## action: actionSlabReconstructionSum

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Sum | Set slab reconstruction type to Sum | actionSlabReconstructionSum
- Text: Sum
- Tooltip: Set slab reconstruction type to Sum
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1410: this->SlabReconstructionTypesMapper->setMapping(this->actionSlabReconstructionSum, VTK_IMAGE_SLAB_SUM);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1416: slabReconstructionTypesActions->addAction(this->actionSlabReconstructionSum);`
- Key UI properties: {"checkable": "true"}

## action: actionSegmentationOutlineFill

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Toggle segmentation outline/fill | Toggle between segmentation outline only, outline and fill, and fill only states | actionSegmentationOutlineFill
- Text: Toggle segmentation outline/fill
- Tooltip: Toggle between segmentation outline only, outline and fill, and fill only states
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:218: QObject::connect(this->actionSegmentationOutlineFill, SIGNAL(triggered()), q, SLOT(toggleSegmentationOutlineFill()));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:227: this->connect(this->SegmentSelectorWidget, SIGNAL(currentNodeChanged(bool)), this->actionSegmentationOutlineFill, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:280: this->SegmentationOutlineButton->setDefaultAction(this->actionSegmentationOutlineFill);`
- Connected slots/functions: `setEnabled`, `toggleSegmentationOutlineFill`
- API footprints: `GetVisibility2DFill`, `GetVisibility2DOutline`, `SetVisibility2DFill`, `SetVisibility2DOutline`

## action: actionSegmentationVisibility

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Show Segmentation | Toggle segmentation visibility | actionSegmentationVisibility
- Text: Show Segmentation
- Tooltip: Toggle segmentation visibility
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:206: this->connect(this->actionSegmentationVisibility, SIGNAL(triggered(bool)), q, SLOT(setSegmentationHidden(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:226: //               this->actionSegmentationVisibility, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:274: this->SegmentationVisibilityButton->setDefaultAction(this->actionSegmentationVisibility);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1006: this->actionSegmentationVisibility->setEnabled(segmentationNode && segmentationNode->GetDisplayNodeID());`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:1035: this->actionSegmentationVisibility->setEnabled(displayNode != nullptr);`
- Connected slots/functions: `setEnabled`, `setSegmentationHidden`
- API footprints: `GetDisplayNodeID`, `SetVisibility`
- Key UI properties: {"checkable": "true"}

## action: actionClipToBackground

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Clip to background | Control if the layers blending would clip the rendering to the background volume | actionClipToBackground
- Text: Clip to background
- Tooltip: Control if the layers blending would clip the rendering to the background volume
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:183: QObject::connect(this->actionClipToBackground, SIGNAL(triggered(bool)), q, SLOT(setClipToBackground(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:436: this->CompositingMenu->addAction(this->actionClipToBackground);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:937: this->actionClipToBackground->setChecked(this->MRMLSliceCompositeNode->GetClipToBackgroundVolume());`
- Connected slots/functions: `setClipToBackground`
- API footprints: `GetClipToBackgroundVolume`, `GetNextItemAsObject`, `GetPointer`, `InitTraversal`, `SetClipToBackgroundVolume`
- Key UI properties: {"checkable": "true"}

## action: actionSliceEdgeVisibility3D

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Show slice edge | Show slice edge in the 3D view | actionSliceEdgeVisibility3D
- Text: Show slice edge
- Tooltip: Show slice edge in the 3D view
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget.h`, `Libs/MRML/Widgets/qMRMLSliceControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:175: QObject::connect(this->actionSliceEdgeVisibility3D, SIGNAL(triggered(bool)), q, SLOT(setSliceEdgeVisibility3D(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:582: this->SliceModelMenu->addAction(this->actionSliceEdgeVisibility3D);`
  - `Libs/MRML/Widgets/qMRMLSliceControllerWidget.cxx:831: this->actionSliceEdgeVisibility3D->setChecked(sliceNode->GetSliceEdgeVisibility3D());`
- Connected slots/functions: `setSliceEdgeVisibility3D`
- API footprints: `EndSliceNodeInteraction`, `GetSliceEdgeVisibility3D`, `SetSliceEdgeVisibility3D`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::SliceEdgeVisibility3DFlag`
- Key UI properties: {"checkable": "true", "checked": "true"}
