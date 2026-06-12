# Slicer UI Analysis: Modules/Loadable/Data/Resources/UI/qSlicerDataModuleWidget.ui

- Owner class: `qSlicerDataModuleWidget`
- UI file: `Modules/Loadable/Data/Resources/UI/qSlicerDataModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerDataModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerDataModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:22: #include "qSlicerDataModuleWidget.h"`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:23: #include "ui_qSlicerDataModuleWidget.h"`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:55: class qSlicerDataModuleWidgetPrivate : public Ui_qSlicerDataModuleWidget`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:57: Q_DECLARE_PUBLIC(qSlicerDataModuleWidget);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:60: qSlicerDataModuleWidget* const q_ptr;`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:63: qSlicerDataModuleWidgetPrivate(qSlicerDataModuleWidget& object);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:64: ~qSlicerDataModuleWidgetPrivate();`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:79: // qSlicerDataModuleWidgetPrivate methods`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:82: qSlicerDataModuleWidgetPrivate::qSlicerDataModuleWidgetPrivate(qSlicerDataModuleWidget& object)`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:90: this->CallBack->SetCallback(qSlicerDataModuleWidget::onSubjectHierarchyItemEvent);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:94: qSlicerDataModuleWidgetPrivate::~qSlicerDataModuleWidgetPrivate()`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:104: vtkSlicerDataModuleLogic* qSlicerDataModuleWidgetPrivate::logic() const`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> TransformMRMLTreeView.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> SubjectHierarchyTreeView.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> AllNodesMRMLTreeView.setMRMLScene(vtkMRMLScene*)`
- API footprints: `AddNode`, `GetParentTransformNode`, `GetPointer`, `SetCallback`, `SetClientData`, `vtkMRMLTransformableNode::SafeDownCast`

## widget: FilterLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Filter: | FilterLabel | QLabel
- Text: Filter:
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: FilterLineEdit

- Confidence: `linked_to_slot`
- Widget/action class: `QLineEdit`
- Search text: A case sensitive string to filter nodes, uses all the columns (even if hidden) | FilterLineEdit | QLineEdit
- Tooltip: A case sensitive string to filter nodes, uses all the columns (even if hidden)
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:171: connect(d->FilterLineEdit, SIGNAL(textChanged(QString)), d->SubjectHierarchyTreeView->sortFilterProxyModel(), SLOT(setNameFilter(QString)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:218: connect(d->FilterLineEdit, SIGNAL(textChanged(QString)), d->TransformMRMLTreeView->sortFilterProxyModel(), SLOT(setFilterWildcard(QString)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:239: connect(d->FilterLineEdit, SIGNAL(textChanged(QString)), d->AllNodesMRMLTreeView->sortFilterProxyModel(), SLOT(setFilterWildcard(QString)));`
- Connected slots/functions: `setFilterWildcard`, `setNameFilter`

## widget: DynamicSpacer

- Confidence: `ui_only`
- Widget/action class: `ctkDynamicSpacer`
- Search text: DynamicSpacer | ctkDynamicSpacer
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: ViewTabWidget

- Confidence: `linked_to_slot`
- Widget/action class: `QTabWidget`
- Search text: ViewTabWidget | QTabWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:129: this->onCurrentTabChanged(d->ViewTabWidget->currentIndex());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:143: d->ViewTabWidget->widget(TabIndexSubjectHierarchy)->layout()->setContentsMargins(2, 2, 2, 2);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:144: d->ViewTabWidget->widget(TabIndexSubjectHierarchy)->layout()->setSpacing(4);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:146: d->ViewTabWidget->widget(TabIndexTransformHierarchy)->layout()->setContentsMargins(2, 2, 2, 2);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:147: d->ViewTabWidget->widget(TabIndexTransformHierarchy)->layout()->setSpacing(4);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:149: d->ViewTabWidget->widget(TabIndexAllNodes)->layout()->setContentsMargins(2, 2, 2, 2);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:150: d->ViewTabWidget->widget(TabIndexAllNodes)->layout()->setSpacing(4);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:152: connect(d->ViewTabWidget, SIGNAL(currentChanged(int)), this, SLOT(onCurrentTabChanged(int)));`
- Connected slots/functions: `onCurrentTabChanged`

## widget: tabSubject

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: tabSubject | QWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: SubjectHierarchyDisplayTransformsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show transforms | SubjectHierarchyDisplayTransformsCheckBox | QCheckBox
- Text: Show transforms
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:159: connect(d->SubjectHierarchyDisplayTransformsCheckBox, SIGNAL(toggled(bool)), this, SLOT(setTransformsVisible(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:252: this->setTransformsVisible(d->SubjectHierarchyDisplayTransformsCheckBox->isChecked());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:387: bool wereSignalsBlocked = d->SubjectHierarchyDisplayTransformsCheckBox->blockSignals(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:388: d->SubjectHierarchyDisplayTransformsCheckBox->setChecked(visible);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:389: d->SubjectHierarchyDisplayTransformsCheckBox->blockSignals(wereSignalsBlocked);`
- Connected slots/functions: `setTransformsVisible`
- Key UI properties: {"checked": "true"}

## widget: SubjectHierarchyDisplayDataNodeIDsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show MRML ID's | SubjectHierarchyDisplayDataNodeIDsCheckBox | QCheckBox
- Text: Show MRML ID's
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:158: connect(d->SubjectHierarchyDisplayDataNodeIDsCheckBox, SIGNAL(toggled(bool)), this, SLOT(setMRMLIDsVisible(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:251: this->setMRMLIDsVisible(d->SubjectHierarchyDisplayDataNodeIDsCheckBox->isChecked());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:280: bool wereSignalsBlocked = d->SubjectHierarchyDisplayDataNodeIDsCheckBox->blockSignals(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:281: d->SubjectHierarchyDisplayDataNodeIDsCheckBox->setChecked(visible);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:282: d->SubjectHierarchyDisplayDataNodeIDsCheckBox->blockSignals(wereSignalsBlocked);`
- Connected slots/functions: `setMRMLIDsVisible`

## widget: HelpButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: HelpButton | QToolButton
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:174: connect(d->HelpButton, SIGNAL(clicked()), this, SLOT(onHelpButtonClicked()));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:189: d->HelpButton->setToolTip(aggregatedHelpText);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:508: void qSlicerDataModuleWidget::onHelpButtonClicked()`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.h:81: void onHelpButtonClicked();`
- Connected slots/functions: `onHelpButtonClicked`
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonFollowStyle"}

## widget: SubjectHierarchyTreeView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: SubjectHierarchyTreeView | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:96: vtkMRMLSubjectHierarchyNode* shNode = this->SubjectHierarchyTreeView->subjectHierarchyNode();`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:162: d->SubjectHierarchyTreeView->expandToDepth(4);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:163: d->SubjectHierarchyTreeView->setEditTriggers(QAbstractItemView::DoubleClicked | QAbstractItemView::EditKeyPressed);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:167: connect(d->SubjectHierarchyTreeView, SIGNAL(currentItemChanged(vtkIdType)), this, SLOT(setDataNodeFromSubjectHierarchyItem(vtkIdType)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:168: connect(d->SubjectHierarchyTreeView, SIGNAL(currentItemChanged(vtkIdType)), this, SLOT(setInfoLabelFromSubjectHierarchyItem(vtkIdType)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:171: connect(d->FilterLineEdit, SIGNAL(textChanged(QString)), d->SubjectHierarchyTreeView->sortFilterProxyModel(), SLOT(setNameFilter(QString)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:261: d->SubjectHierarchyTreeView->setColumnHidden(d->SubjectHierarchyTreeView->model()->idColumn(), !visible);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:302: d->SubjectHierarchyTreeView->setVisible(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:306: this->setDataNodeFromSubjectHierarchyItem(d->SubjectHierarchyTreeView->currentItem());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:312: d->SubjectHierarchyTreeView->setVisible(false);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:324: d->SubjectHierarchyTreeView->setVisible(false);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:383: qMRMLSubjectHierarchyModel* model = qobject_cast<qMRMLSubjectHierarchyModel*>(d->SubjectHierarchyTreeView->model());`
- Connected slots/functions: `setDataNodeFromSubjectHierarchyItem`, `setInfoLabelFromSubjectHierarchyItem`, `setNameFilter`
- API footprints: `AddObserver`, `GetItemDataNode`, `HasObserver`, `PrintItem`, `vtkMRMLSubjectHierarchyNode::INVALID_ITEM_ID`, `vtkMRMLSubjectHierarchyNode::SubjectHierarchyItemModifiedEvent`

## widget: SubjectHierarchyItemInfoGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: SubjectHierarchyItemInfoGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: SubjectHierarchyItemInfoLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: No item selected | SubjectHierarchyItemInfoLabel | QLabel
- Text: No item selected
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:165: d->SubjectHierarchyItemInfoLabel->setTextInteractionFlags(Qt::TextSelectableByMouse);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:429: d->SubjectHierarchyItemInfoLabel->setText(infoStream.str().c_str());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:439: d->SubjectHierarchyItemInfoLabel->setText(tr("No item selected"));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:443: d->SubjectHierarchyItemInfoLabel->setProperty("itemID", itemID);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:480: vtkIdType displayedItemID = d->SubjectHierarchyItemInfoLabel->property("itemID").toLongLong();`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:494: d->SubjectHierarchyItemInfoLabel->setText(infoStream.str().c_str());`
- API footprints: `PrintItem`

## widget: tabTransform

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: tabTransform | QWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: TransformDisplayMRMLIDsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show MRML ID's | TransformDisplayMRMLIDsCheckBox | QCheckBox
- Text: Show MRML ID's
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:213: connect(d->TransformDisplayMRMLIDsCheckBox, SIGNAL(toggled(bool)), this, SLOT(setMRMLIDsVisible(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:284: wereSignalsBlocked = d->TransformDisplayMRMLIDsCheckBox->blockSignals(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:285: d->TransformDisplayMRMLIDsCheckBox->setChecked(visible);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:286: d->TransformDisplayMRMLIDsCheckBox->blockSignals(wereSignalsBlocked);`
- Connected slots/functions: `setMRMLIDsVisible`

## widget: TransformShowHiddenCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show hidden nodes | TransformShowHiddenCheckBox | QCheckBox
- Text: Show hidden nodes
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:214: connect(d->TransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->TransformMRMLTreeView->sortFilterProxyModel(), SLOT(setShowHidden(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:215: connect(d->TransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->AllNodesTransformShowHiddenCheckBox, SLOT(setChecked(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:235: connect(d->AllNodesTransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->AllNodesMRMLTreeView->sortFilterProxyModel(), SLOT(setShowHidden(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:236: connect(d->AllNodesTransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->TransformShowHiddenCheckBox, SLOT(setChecked(bool)));`
- Connected slots/functions: `setChecked`, `setShowHidden`

## widget: TransformMRMLTreeView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLTreeView`
- Search text: TransformMRMLTreeView | qMRMLTreeView
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:194: d->TransformMRMLTreeView->sceneModel()->setIDColumn(1);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:195: d->TransformMRMLTreeView->sceneModel()->setHorizontalHeaderLabels(QStringList() << tr("Nodes") << tr("IDs"));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:196: d->TransformMRMLTreeView->header()->setStretchLastSection(false);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:197: d->TransformMRMLTreeView->header()->setSectionResizeMode(0, QHeaderView::Stretch);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:198: d->TransformMRMLTreeView->header()->setSectionResizeMode(1, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:200: connect(d->TransformMRMLTreeView, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onCurrentNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:203: connect(d->TransformMRMLTreeView, SIGNAL(editNodeRequested(vtkMRMLNode*)), qSlicerApplication::application(), SLOT(openNodeModule(vtkMRMLNode*)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:206: d->TransformMRMLTreeView->prependNodeMenuAction(insertTransformAction);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:207: d->TransformMRMLTreeView->prependSceneMenuAction(insertTransformAction);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:214: connect(d->TransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->TransformMRMLTreeView->sortFilterProxyModel(), SLOT(setShowHidden(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:217: d->TransformMRMLTreeView->sortFilterProxyModel()->setFilterKeyColumn(-1);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:218: connect(d->FilterLineEdit, SIGNAL(textChanged(QString)), d->TransformMRMLTreeView->sortFilterProxyModel(), SLOT(setFilterWildcard(QString)));`
- Connected slots/functions: `onCurrentNodeChanged`, `openNodeModule`, `setFilterWildcard`, `setMRMLNode`, `setShowHidden`
- API footprints: `AddNode`, `CanApplyNonLinearTransforms`, `GetParentTransformNode`, `GetPointer`, `IsTransformToWorldLinear`, `vtkMRMLTransformNode::SafeDownCast`, `vtkMRMLTransformableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTransformableNode"]}

## widget: tabAll

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: tabAll | QWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: AllNodesDisplayMRMLIDsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show MRML ID's | AllNodesDisplayMRMLIDsCheckBox | QCheckBox
- Text: Show MRML ID's
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:234: connect(d->AllNodesDisplayMRMLIDsCheckBox, SIGNAL(toggled(bool)), this, SLOT(setMRMLIDsVisible(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:288: wereSignalsBlocked = d->AllNodesDisplayMRMLIDsCheckBox->blockSignals(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:289: d->AllNodesDisplayMRMLIDsCheckBox->setChecked(visible);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:290: d->AllNodesDisplayMRMLIDsCheckBox->blockSignals(wereSignalsBlocked);`
- Connected slots/functions: `setMRMLIDsVisible`

## widget: AllNodesTransformShowHiddenCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show hidden nodes | AllNodesTransformShowHiddenCheckBox | QCheckBox
- Text: Show hidden nodes
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:215: connect(d->TransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->AllNodesTransformShowHiddenCheckBox, SLOT(setChecked(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:235: connect(d->AllNodesTransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->AllNodesMRMLTreeView->sortFilterProxyModel(), SLOT(setShowHidden(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:236: connect(d->AllNodesTransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->TransformShowHiddenCheckBox, SLOT(setChecked(bool)));`
- Connected slots/functions: `setChecked`, `setShowHidden`

## widget: AllNodesMRMLTreeView

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLTreeView`
- Search text: AllNodesMRMLTreeView | qMRMLTreeView
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:225: d->AllNodesMRMLTreeView->sceneModel()->setIDColumn(1);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:226: d->AllNodesMRMLTreeView->sceneModel()->setHorizontalHeaderLabels(QStringList() << tr("Nodes") << tr("IDs"));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:227: d->AllNodesMRMLTreeView->header()->setStretchLastSection(false);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:228: d->AllNodesMRMLTreeView->header()->setSectionResizeMode(0, QHeaderView::Stretch);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:229: d->AllNodesMRMLTreeView->header()->setSectionResizeMode(1, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:232: connect(d->AllNodesMRMLTreeView, SIGNAL(editNodeRequested(vtkMRMLNode*)), qSlicerApplication::application(), SLOT(openNodeModule(vtkMRMLNode*)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:235: connect(d->AllNodesTransformShowHiddenCheckBox, SIGNAL(toggled(bool)), d->AllNodesMRMLTreeView->sortFilterProxyModel(), SLOT(setShowHidden(bool)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:238: d->AllNodesMRMLTreeView->sortFilterProxyModel()->setFilterKeyColumn(-1);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:239: connect(d->FilterLineEdit, SIGNAL(textChanged(QString)), d->AllNodesMRMLTreeView->sortFilterProxyModel(), SLOT(setFilterWildcard(QString)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:241: connect(d->AllNodesMRMLTreeView, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->MRMLNodeAttributeTableWidget, SLOT(setMRMLNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:272: d->AllNodesMRMLTreeView->setColumnHidden(d->AllNodesMRMLTreeView->sceneModel()->idColumn(), !visible);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:273: columnCount = d->AllNodesMRMLTreeView->header()->count();`
- Connected slots/functions: `openNodeModule`, `setFilterWildcard`, `setMRMLNode`, `setShowHidden`

## widget: MRMLNodeInspectorGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: MRMLNodeInspectorGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`

## widget: MRMLNodeAttributeTableWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeAttributeTableWidget`
- Search text: MRMLNodeAttributeTableWidget | qMRMLNodeAttributeTableWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx`, `Modules/Loadable/Data/qSlicerDataModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:220: connect(d->TransformMRMLTreeView, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->MRMLNodeAttributeTableWidget, SLOT(setMRMLNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:241: connect(d->AllNodesMRMLTreeView, SIGNAL(currentNodeChanged(vtkMRMLNode*)), d->MRMLNodeAttributeTableWidget, SLOT(setMRMLNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:316: d->MRMLNodeAttributeTableWidget->setEnabled(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:318: d->MRMLNodeAttributeTableWidget->setMRMLNode(d->TransformMRMLTreeView->currentNode());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:328: d->MRMLNodeAttributeTableWidget->setEnabled(true);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:330: d->MRMLNodeAttributeTableWidget->setMRMLNode(d->AllNodesMRMLTreeView->currentNode());`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:409: d->MRMLNodeAttributeTableWidget->setEnabled(dataNode);`
  - `Modules/Loadable/Data/qSlicerDataModuleWidget.cxx:410: d->MRMLNodeAttributeTableWidget->setMRMLNode(dataNode);`
- Connected slots/functions: `setMRMLNode`
- API footprints: `GetItemDataNode`
