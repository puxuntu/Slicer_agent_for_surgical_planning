# Slicer UI Analysis: Modules/Loadable/Models/Resources/UI/qSlicerModelsModuleWidget.ui

- Owner class: `qSlicerModelsModuleWidget`
- UI file: `Modules/Loadable/Models/Resources/UI/qSlicerModelsModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerModelsModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerModelsModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:36: #include "qSlicerModelsModuleWidget.h"`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:37: #include "ui_qSlicerModelsModuleWidget.h"`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:60: class qSlicerModelsModuleWidgetPrivate : public Ui_qSlicerModelsModuleWidget`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:63: qSlicerModelsModuleWidgetPrivate();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:71: // qSlicerModelsModuleWidgetPrivate methods`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:74: qSlicerModelsModuleWidgetPrivate::qSlicerModelsModuleWidgetPrivate()`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:82: // qSlicerModelsModuleWidget methods`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:85: qSlicerModelsModuleWidget::qSlicerModelsModuleWidget(QWidget* _parent)`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:87: , d_ptr(new qSlicerModelsModuleWidgetPrivate)`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:92: qSlicerModelsModuleWidget::~qSlicerModelsModuleWidget()`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:94: Q_D(qSlicerModelsModuleWidget);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:106: void qSlicerModelsModuleWidget::setup()`
- API footprints: `AddObserver`, `GetClipNode`, `SetCallback`, `SetClientData`, `vtkMRMLClipNode::SafeDownCast`, `vtkMRMLScene::EndImportEvent`

## widget: ResizableFrame

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`

## widget: FilterModelSearchBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSearchBox`
- Search text: FilterModelSearchBox | ctkSearchBox
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:126: connect(d->FilterModelSearchBox, SIGNAL(textChanged(QString)), sortFilterProxyModel, SLOT(setNameFilter(QString)));`
- Connected slots/functions: `setNameFilter`

## widget: hideAllModelsButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Turn the visibility off on all models (does not include hierarchies) | hideAllModelsButton | QPushButton
- Tooltip: Turn the visibility off on all models (does not include hierarchies)
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`

## widget: showAllModelsButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Turns visibility on for all models (does not include hierarchies) | showAllModelsButton | QPushButton
- Tooltip: Turns visibility on for all models (does not include hierarchies)
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`

## widget: SubjectHierarchyTreeView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: SubjectHierarchyTreeView | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:31: #include "qMRMLSubjectHierarchyTreeView.h"`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:115: qMRMLSortFilterSubjectHierarchyProxyModel* sortFilterProxyModel = d->SubjectHierarchyTreeView->sortFilterProxyModel();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:117: d->SubjectHierarchyTreeView->setColumnHidden(d->SubjectHierarchyTreeView->model()->idColumn(), true);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:118: d->SubjectHierarchyTreeView->setColumnHidden(d->SubjectHierarchyTreeView->model()->transformColumn(), true);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:119: d->SubjectHierarchyTreeView->setPluginAllowlist(QStringList() << "Models" << "Folder" << "Opacity" << "Visibility");`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:120: d->SubjectHierarchyTreeView->setSelectRoleSubMenuVisible(false);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:121: d->SubjectHierarchyTreeView->expandToDepth(4);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:122: d->SubjectHierarchyTreeView->setEditTriggers(QAbstractItemView::DoubleClicked | QAbstractItemView::EditKeyPressed);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:124: connect(d->SubjectHierarchyTreeView, SIGNAL(currentItemsChanged(QList<vtkIdType>)), this, SLOT(setDisplaySelectionFromSubjectHierarchyItems(QList<vtkIdType>)));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:150: int displayedItemCount = d->SubjectHierarchyTreeView->displayedItemCount();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:151: int headerHeight = d->SubjectHierarchyTreeView->header()->sizeHint().height();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:156: treeViewHeight = headerHeight + displayedItemCount * d->SubjectHierarchyTreeView->sizeHintForRow(0) + 2;`
- Connected slots/functions: `setDisplaySelectionFromSubjectHierarchyItems`
- API footprints: `GetItemDataNode`, `GetSceneItemID`, `vtkMRMLFolderDisplayNode::SafeDownCast`, `vtkMRMLModelNode::SafeDownCast`

## widget: InformationButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Information | InformationButton | ctkCollapsibleButton
- Text: Information
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:128: connect(d->InformationButton, SIGNAL(contentsCollapsed(bool)), this, SLOT(onInformationSectionCollapsed(bool)));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:443: d->MRMLModelInfoWidget->setMRMLModelNode(d->InformationButton->collapsed() ? nullptr : firstDataNode);`
- Connected slots/functions: `onInformationSectionCollapsed`

## widget: MRMLModelInfoWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLModelInfoWidget`
- Search text: MRMLModelInfoWidget | qMRMLModelInfoWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:443: d->MRMLModelInfoWidget->setMRMLModelNode(d->InformationButton->collapsed() ? nullptr : firstDataNode);`

## widget: DisplayButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display | DisplayButton | ctkCollapsibleButton
- Text: Display
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`

## widget: ModelDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLModelDisplayNodeWidget`
- Search text: ModelDisplayWidget | qMRMLModelDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:112: d->ModelDisplayWidget->setEnabled(false);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:132: connect(d->ModelDisplayWidget, SIGNAL(clippingToggled(bool)), this, SLOT(onClipSelectedModelToggled(bool)));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:134: connect(d->ModelDisplayWidget, SIGNAL(clippingConfigurationButtonClicked()), this, SLOT(onClippingConfigurationButtonClicked()));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:137: connect(d->ModelDisplayWidget, SIGNAL(displayNodeChanged()), this, SLOT(onDisplayNodeChanged()));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:328: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:367: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:379: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:391: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:403: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:415: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:445: d->ModelDisplayWidget->setCurrentSubjectHierarchyItemIDs(itemIDs);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:480: vtkMRMLModelDisplayNode* displayNode = d->ModelDisplayWidget->mrmlModelDisplayNode();`
- Connected slots/functions: `onClipSelectedModelToggled`, `onClippingConfigurationButtonClicked`, `onDisplayNodeChanged`
- API footprints: `GetClipNode`, `GetColorNode`, `SetClipping`, `vtkMRMLClipNode::SafeDownCast`

## widget: ColorLegendCollapsibleGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: Color legend for the Color Table selected in Scalars section. | ColorLegendCollapsibleGroupBox | ctkCollapsibleGroupBox
- Tooltip: Color legend for the Color Table selected in Scalars section.
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:139: connect(d->ColorLegendCollapsibleGroupBox, SIGNAL(toggled(bool)), this, SLOT(onColorLegendCollapsibleGroupBoxToggled(bool)));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:356: d->ColorLegendCollapsibleGroupBox->setCollapsed(true);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:358: d->ColorLegendCollapsibleGroupBox->setEnabled(displayNode && displayNode->GetColorNode());`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:470: void qSlicerModelsModuleWidget::onColorLegendCollapsibleGroupBoxToggled(bool toggled)`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.h:68: void onColorLegendCollapsibleGroupBoxToggled(bool);`
- Connected slots/functions: `onColorLegendCollapsibleGroupBoxToggled`
- API footprints: `GetColorNode`, `GetMRMLApplicationLogic`, `PauseRender`, `ResumeRender`, `SetVisibility`

## widget: ColorLegendDisplayNodeWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLColorLegendDisplayNodeWidget`
- Search text: ColorLegendDisplayNodeWidget | qMRMLColorLegendDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:352: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(colorLegendNode);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:499: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(colorLegendNode);`

## widget: ClippingButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Clipping | ClippingButton | ctkCollapsibleButton
- Text: Clipping
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:312: d->ClippingButton->setCollapsed(false);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:319: scrollArea->ensureWidgetVisible(d->ClippingButton);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:331: d->ClippingButton->setEnabled(displayNode != nullptr);`
- API footprints: `GetClipNode`
- Key UI properties: {"checked": "true"}

## widget: ClipModelsNodeComboBoxLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Clip node: | ClipModelsNodeComboBoxLabel | QLabel
- Text: Clip node:
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`

## widget: MRMLClipNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLClipNodeWidget`
- Search text: MRMLClipNodeWidget | qMRMLClipNodeWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:344: wasBlocked = d->MRMLClipNodeWidget->blockSignals(true);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:345: d->MRMLClipNodeWidget->setEnabled(clipNode != nullptr);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:346: d->MRMLClipNodeWidget->setMRMLClipNode(clipNode);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:347: d->MRMLClipNodeWidget->blockSignals(wasBlocked);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:372: d->MRMLClipNodeWidget->setMRMLClipNode(clipNode);`
- API footprints: `GetID`, `SetAndObserveClipNodeID`

## widget: ClipModelsNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ClipModelsNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:130: connect(d->ClipModelsNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onClipModelsNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:339: wasBlocked = d->ClipModelsNodeComboBox->blockSignals(true);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:340: d->ClipModelsNodeComboBox->setEnabled(displayNode != nullptr);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:341: d->ClipModelsNodeComboBox->setCurrentNode(clipNode);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:342: d->ClipModelsNodeComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onClipModelsNodeChanged`
- API footprints: `GetID`, `SetAndObserveClipNodeID`, `vtkMRMLClipNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLClipNode"]}

## widget: MRMLClipNodeDisplayWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLClipNodeDisplayWidget`
- Search text: MRMLClipNodeDisplayWidget | qMRMLClipNodeDisplayWidget
- Implementation candidates: `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx`, `Modules/Loadable/Models/qSlicerModelsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:335: wasBlocked = d->MRMLClipNodeDisplayWidget->blockSignals(true);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:336: d->MRMLClipNodeDisplayWidget->setMRMLDisplayNode(displayNode);`
  - `Modules/Loadable/Models/qSlicerModelsModuleWidget.cxx:337: d->MRMLClipNodeDisplayWidget->blockSignals(wasBlocked);`
