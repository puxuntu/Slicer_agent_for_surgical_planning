# Slicer UI Analysis: Modules/Loadable/Transforms/Resources/UI/qSlicerTransformsModuleWidget.ui

- Owner class: `qSlicerTransformsModuleWidget`
- UI file: `Modules/Loadable/Transforms/Resources/UI/qSlicerTransformsModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTransformsModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerTransformsModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:34: #include "qSlicerTransformsModuleWidget.h"`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:35: #include "ui_qSlicerTransformsModuleWidget.h"`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:62: class qSlicerTransformsModuleWidgetPrivate : public Ui_qSlicerTransformsModuleWidget`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:64: Q_DECLARE_PUBLIC(qSlicerTransformsModuleWidget);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:67: qSlicerTransformsModuleWidget* const q_ptr;`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:70: qSlicerTransformsModuleWidgetPrivate(qSlicerTransformsModuleWidget& object);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:79: qSlicerTransformsModuleWidgetPrivate::qSlicerTransformsModuleWidgetPrivate(qSlicerTransformsModuleWidget& object)`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:87: vtkSlicerTransformLogic* qSlicerTransformsModuleWidgetPrivate::logic() const`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:89: Q_Q(const qSlicerTransformsModuleWidget);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:94: QList<vtkSmartPointer<vtkMRMLTransformableNode>> qSlicerTransformsModuleWidgetPrivate::getSelectedNodes(qMRMLTreeView* tree)`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:111: qSlicerTransformsModuleWidget::qSlicerTransformsModuleWidget(QWidget* _parentWidget)`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:113: , d_ptr(new qSlicerTransformsModuleWidgetPrivate(*this))`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> TransformableTreeView.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> TransformedTreeView.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> TransformDisplayNodeWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> TranslationSliders.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> TransformInfoWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> ConvertOutputDisplacementFieldNodeComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetTransformToParent`, `IsLinear`, `vtkMRMLTransformNode::SafeDownCast`

## widget: ResizableFrame

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: TransformNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: TransformNodeSelector | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:163: this->connect(d->TransformNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onNodeSelected(vtkMRMLNode*)));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:228: vtkMRMLSubjectHierarchyNode* shNode = d->TransformNodeSelector->subjectHierarchyNode();`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:239: if (!d->TransformNodeSelector->currentNode())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:241: vtkMRMLNode* node = d->TransformNodeSelector->findFirstNodeByClass("vtkMRMLTransformNode");`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:244: d->TransformNodeSelector->setCurrentNode(node);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:257: vtkMRMLSubjectHierarchyNode* shNode = d->TransformNodeSelector->subjectHierarchyNode();`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:759: d->TransformNodeSelector->setCurrentNode(node);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:771: d->TransformNodeSelector->setCurrentNode(displayableNode);`
- Connected slots/functions: `onNodeSelected`
- API footprints: `GetDisplayNode`, `GetID`, `IsComposite`, `IsLinear`, `vtkMRMLTransformDisplayNode::SafeDownCast`, `vtkMRMLTransformNode::SafeDownCast`, `vtkMRMLTransformableNode::TransformModifiedEvent`
- Key UI properties: {"nodeTypes": ["vtkMRMLTransformNode"]}

## widget: InfoCollapsibleWidget

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Information | InfoCollapsibleWidget | ctkCollapsibleButton
- Text: Information
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Key UI properties: {"checked": "false"}

## widget: TransformInfoWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLTransformInfoWidget`
- Search text: TransformInfoWidget | qMRMLTransformInfoWidget
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:342: d->TransformInfoWidget->setMRMLTransformNode(transformNode);`

## widget: DisplayEditCollapsibleWidget

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Edit | DisplayEditCollapsibleWidget | ctkCollapsibleButton
- Text: Edit
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: MatrixViewGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: MatrixViewGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:309: // Enable/Disable CoordinateReference, identity, split buttons, MatrixViewGroupBox, and`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:322: d->MatrixViewGroupBox->setEnabled(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:328: d->MatrixViewGroupBox->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:397: d->MatrixViewGroupBox->setEnabled(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:407: if (isLinearTransform != d->MatrixViewGroupBox->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:409: d->MatrixViewGroupBox->setVisible(isLinearTransform);`
- API footprints: `IsComposite`

## widget: MatrixWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLMatrixWidget`
- Search text: MatrixWidget | qMRMLMatrixWidget
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:166: d->MatrixWidget->setRange(-1e10, 1e10);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:172: QTableWidgetItem* item = d->MatrixWidget->widgetItem(3, col);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:340: d->MatrixWidget->setMRMLTransformNode(transformNode);`

## widget: TranslationSliders

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLTransformSliders`
- Search text: TranslationSliders | qMRMLTransformSliders
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:285: d->TranslationSliders->setCoordinateReference(ref);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:329: d->TranslationSliders->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:338: d->TranslationSliders->setMRMLTransformNode(transformNode);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:411: if (isLinearTransform != d->TranslationSliders->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:413: d->TranslationSliders->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:475: d->TranslationSliders->resetUnactiveSliders();`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:492: d->TranslationSliders->resetUnactiveSliders();`
- Connected slots/functions: `resetUnactiveSliders`
- Declared UI connections: `valuesChanged() -> RotationSliders.resetUnactiveSliders()`

## widget: RotationSliders

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLTransformSliders`
- Search text: RotationSliders | qMRMLTransformSliders
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:180: d->RotationSliders->setSingleStep(0.1);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:181: d->RotationSliders->setDecimals(1);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:286: d->RotationSliders->setCoordinateReference(ref);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:330: d->RotationSliders->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:339: d->RotationSliders->setMRMLTransformNode(transformNode);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:415: if (isLinearTransform != d->RotationSliders->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:417: d->RotationSliders->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:476: d->RotationSliders->resetUnactiveSliders();`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:493: d->RotationSliders->resetUnactiveSliders();`

## widget: IdentityPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Identity | IdentityPushButton | QPushButton
- Text: Identity
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:145: this->connect(d->IdentityPushButton, SIGNAL(clicked()), SLOT(identity()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:321: d->IdentityPushButton->setEnabled(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:396: d->IdentityPushButton->setEnabled(isLinearTransform);`
- Connected slots/functions: `identity`
- API footprints: `GetPointer`, `IsLinear`, `SetMatrixTransformToParent`

## widget: InvertPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Invert | InvertPushButton | QPushButton
- Text: Invert
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:148: this->connect(d->InvertPushButton, SIGNAL(clicked()), SLOT(invert()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:312: d->InvertPushButton->setEnabled(isTransform);`
- Connected slots/functions: `invert`
- API footprints: `Inverse`, `InverseName`

## widget: SplitPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Split | Split a composite transform to its components | SplitPushButton | QPushButton
- Text: Split
- Tooltip: Split a composite transform to its components
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:151: this->connect(d->SplitPushButton, SIGNAL(clicked()), SLOT(split()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:336: d->SplitPushButton->setVisible(isCompositeTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:427: if (isCompositeTransform != d->SplitPushButton->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:429: d->SplitPushButton->setVisible(isCompositeTransform);`
- Connected slots/functions: `split`
- API footprints: `Split`

## widget: TranslateFirstToolButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Translation in global or local (rotated) reference frame | TranslateFirstToolButton | QToolButton
- Text: ...
- Tooltip: Translation in global or local (rotated) reference frame
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:142: this->connect(d->TranslateFirstToolButton, SIGNAL(toggled(bool)), SLOT(onTranslateFirstButtonPressed(bool)));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:320: d->TranslateFirstToolButton->setEnabled(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:331: d->TranslateFirstToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:395: d->TranslateFirstToolButton->setEnabled(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:403: if (isLinearTransform != d->TranslateFirstToolButton->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:405: d->TranslateFirstToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:605: return (d->TranslateFirstToolButton->isChecked() ? qMRMLTransformSliders::LOCAL : qMRMLTransformSliders::GLOBAL);`
- Connected slots/functions: `onTranslateFirstButtonPressed`
- API footprints: `IsComposite`
- Key UI properties: {"checkable": "true"}

## widget: CopyTransformToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Copy transform | CopyTransformToolButton | QToolButton
- Text: Copy transform
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:196: d->CopyTransformToolButton->setDefaultAction(d->CopyAction);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:332: d->CopyTransformToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:419: if (isLinearTransform != d->CopyTransformToolButton->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:421: d->CopyTransformToolButton->setVisible(isLinearTransform);`

## widget: PasteTransformToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Paste transform | PasteTransformToolButton | QToolButton
- Text: Paste transform
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:199: d->PasteTransformToolButton->setDefaultAction(d->PasteAction);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:333: d->PasteTransformToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:423: if (isLinearTransform != d->PasteTransformToolButton->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:425: d->PasteTransformToolButton->setVisible(isLinearTransform);`

## widget: CenterOfTransformationGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CenterOfTransformationGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:441: d->CenterOfTransformationGroupBox->setEnabled(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:442: if (isLinearTransform != d->CenterOfTransformationGroupBox->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:444: d->CenterOfTransformationGroupBox->setVisible(isLinearTransform);`
- API footprints: `IsLinear`

## widget: CenterOfTransformationCoordinatesComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: CenterOfTransformationCoordinatesComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:154: this->connect(d->CenterOfTransformationCoordinatesComboBox, SIGNAL(currentIndexChanged(int)), SLOT(updateCenterOfTransformationWidgets()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:453: if (d->CenterOfTransformationCoordinatesComboBox->currentIndex() == COORDINATE_COMBOBOX_INDEX_WORLD)`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:573: if (d->CenterOfTransformationCoordinatesComboBox->currentIndex() == COORDINATE_COMBOBOX_INDEX_LOCAL)`
- Connected slots/functions: `updateCenterOfTransformationWidgets`
- API footprints: `GetCenterOfTransformation`, `GetTransformToWorld`, `IsLinear`, `SetCenterOfTransformation`, `TransformPoint`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Coordinates: | label | QLabel
- Text: Coordinates:
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: ResetCenterOfTransformationButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Reset | ResetCenterOfTransformationButton | QPushButton
- Text: Reset
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:160: this->connect(d->ResetCenterOfTransformationButton, SIGNAL(clicked()), SLOT(resetCenterOfTransformation()));`
- Connected slots/functions: `resetCenterOfTransformation`
- API footprints: `SetCenterOfTransformation`

## widget: CenterOfTransformationCoordinatesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: CenterOfTransformationCoordinatesWidget | qMRMLCoordinatesWidget
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:157: this->connect(d->CenterOfTransformationCoordinatesWidget, SIGNAL(coordinatesChanged(double*)), SLOT(onCenterOfTransformationChanged()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:460: bool wasBlocked = d->CenterOfTransformationCoordinatesWidget->blockSignals(true);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:461: d->CenterOfTransformationCoordinatesWidget->setCoordinates(centerOfTransformation);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:462: d->CenterOfTransformationCoordinatesWidget->blockSignals(wasBlocked);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:572: const double* coordinates = d->CenterOfTransformationCoordinatesWidget->coordinates();`
- Connected slots/functions: `onCenterOfTransformationChanged`
- API footprints: `GetTransformFromWorld`, `IsLinear`, `SetCenterOfTransformation`, `TransformPoint`

## widget: DisplayCollapsibleButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display | DisplayCollapsibleButton | ctkCollapsibleButton
- Text: Display
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:189: this->connect(d->DisplayCollapsibleButton, SIGNAL(clicked(bool)), SLOT(onDisplaySectionClicked(bool)));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:374: d->DisplayCollapsibleButton->setCollapsed(true);`
- Connected slots/functions: `onDisplaySectionClicked`
- API footprints: `CreateDefaultDisplayNodes`, `GetDisplayNode`, `vtkMRMLTransformDisplayNode::SafeDownCast`
- Key UI properties: {"checked": "true"}

## widget: TransformDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLTransformDisplayNodeWidget`
- Search text: TransformDisplayNodeWidget | qMRMLTransformDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:275: // when the TransformDisplayNodeWidget was set in the widget.`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:276: d->TransformDisplayNodeWidget->setMRMLTransformNode(d->MRMLTransformNode);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:341: d->TransformDisplayNodeWidget->setMRMLTransformNode(transformNode);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:671: d->TransformDisplayNodeWidget->setMRMLTransformNode(d->MRMLTransformNode);`
- API footprints: `CreateDefaultDisplayNodes`

## widget: TransformedCollapsibleButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Apply transform | TransformedCollapsibleButton | ctkCollapsibleButton
- Text: Apply transform
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:193: this->connect(d->TransformedCollapsibleButton, SIGNAL(clicked(bool)), SLOT(onTransformableSectionClicked(bool)));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:216: this->onTransformableSectionClicked(d->TransformedCollapsibleButton->isChecked());`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:300: d->TransformedCollapsibleButton->setCollapsed(false);`
- Connected slots/functions: `onTransformableSectionClicked`
- Key UI properties: {"checked": "false"}

## widget: TransformableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Transformable: | TransformableLabel | QLabel
- Text: Transformable:
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: TransformableTreeView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLTreeView`
- Search text: TransformableTreeView | qMRMLTreeView
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:316: d->TransformableTreeView->setEnabled(isTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:362: d->TransformableTreeView->sortFilterProxyModel()->setHiddenNodeIDs(hiddenNodeIDs);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:616: d->TransformableTreeView->setRootIndex(d->TransformableTreeView->sortFilterProxyModel()->mrmlSceneIndex());`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:623: QList<vtkSmartPointer<vtkMRMLTransformableNode>> nodesToTransform = qSlicerTransformsModuleWidgetPrivate::getSelectedNodes(d->TransformableTreeView);`
- API footprints: `GetID`
- Key UI properties: {"nodeTypes": ["vtkMRMLTransformableNode"]}

## widget: TransformToolButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: > | Apply the selected transform to the selected transformable nodes | TransformToolButton | QToolButton
- Text: >
- Tooltip: Apply the selected transform to the selected transformable nodes
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:184: this->connect(d->TransformToolButton, SIGNAL(clicked()), SLOT(transformSelectedNodes()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:196: d->CopyTransformToolButton->setDefaultAction(d->CopyAction);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:199: d->PasteTransformToolButton->setDefaultAction(d->PasteAction);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:204: d->TransformToolButton->setIcon(rightIcon);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:313: d->TransformToolButton->setEnabled(isTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:332: d->CopyTransformToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:333: d->PasteTransformToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:419: if (isLinearTransform != d->CopyTransformToolButton->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:421: d->CopyTransformToolButton->setVisible(isLinearTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:423: if (isLinearTransform != d->PasteTransformToolButton->isVisible())`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:425: d->PasteTransformToolButton->setVisible(isLinearTransform);`
- Connected slots/functions: `transformSelectedNodes`
- API footprints: `GetID`, `SetAndObserveTransformNodeID`

## widget: UntransformToolButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: < | Remove the selected transform from the selected transformed nodes | UntransformToolButton | QToolButton
- Text: <
- Tooltip: Remove the selected transform from the selected transformed nodes
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:185: this->connect(d->UntransformToolButton, SIGNAL(clicked()), SLOT(untransformSelectedNodes()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:207: d->UntransformToolButton->setIcon(leftIcon);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:314: d->UntransformToolButton->setEnabled(isTransform);`
- Connected slots/functions: `untransformSelectedNodes`
- API footprints: `SetAndObserveTransformNodeID`

## widget: HardenToolButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Harden transform | HardenToolButton | QToolButton
- Tooltip: Harden transform
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:186: this->connect(d->HardenToolButton, SIGNAL(clicked()), SLOT(hardenSelectedNodes()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:315: d->HardenToolButton->setEnabled(isTransform);`
- Connected slots/functions: `hardenSelectedNodes`
- API footprints: `vtkMRMLTransformableNode::SafeDownCast`

## widget: TransformedLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Transformed: | TransformedLabel | QLabel
- Text: Transformed:
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: TransformedTreeView

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLTreeView`
- Search text: TransformedTreeView | qMRMLTreeView
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:317: d->TransformedTreeView->setEnabled(isTransform);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:351: d->TransformedTreeView->setNodeTypes(nodeTypes);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:354: d->TransformedTreeView->setRootNode(transformNode);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:634: QList<vtkSmartPointer<vtkMRMLTransformableNode>> nodesToTransform = qSlicerTransformsModuleWidgetPrivate::getSelectedNodes(d->TransformedTreeView);`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:645: QList<vtkSmartPointer<vtkMRMLTransformableNode>> nodesToTransform = qSlicerTransformsModuleWidgetPrivate::getSelectedNodes(d->TransformedTreeView);`

## widget: ConvertCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Convert | ConvertCollapsibleButton | ctkCollapsibleButton
- Text: Convert
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:318: d->ConvertCollapsibleButton->setEnabled(isTransform);`
- Key UI properties: {"checked": "false"}

## widget: ConvertReferenceVolumeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Reference volume: | ConvertReferenceVolumeLabel | QLabel
- Text: Reference volume:
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: ConvertReferenceVolumeNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Volume that defines origin, spacing, and axis directions of the exported displacement field. If the reference volume is under a non-linear transform then the non-transformed geometry is used as reference. | ConvertReferenceVolumeNodeComboBox | qMRMLNodeComboBox
- Tooltip: Volume that defines origin, spacing, and axis directions of the exported displacement field. If the reference volume is under a non-linear transform then the non-transformed geometry is used as reference.
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:213: this->connect(d->ConvertReferenceVolumeNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(updateConvertButtonState()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:701: if (d->ConvertReferenceVolumeNodeComboBox->currentNode() == nullptr)`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:714: vtkMRMLVolumeNode* referenceVolumeNode = vtkMRMLVolumeNode::SafeDownCast(d->ConvertReferenceVolumeNodeComboBox->currentNode());`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:746: && d->ConvertReferenceVolumeNodeComboBox->currentNode() != nullptr //`
- Connected slots/functions: `updateConvertButtonState`
- API footprints: `vtkMRMLTransformNode::SafeDownCast`, `vtkMRMLVectorVolumeNode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}

## widget: ConvertOutputDisplacementFieldLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Output displacement field: | ConvertOutputDisplacementFieldLabel | QLabel
- Text: Output displacement field:
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`

## widget: ConvertOutputDisplacementFieldNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Volume or transform node that will store the displacement field. If scalar volume node is chosen then only displacement magnitude is saved. In vector volume or transform node 3D displacement vector is saved. | ConvertOutputDisplacementFieldNodeComboBox | qMRMLNodeComboBox
- Tooltip: Volume or transform node that will store the displacement field. If scalar volume node is chosen then only displacement magnitude is saved. In vector volume or transform node 3D displacement vector is saved.
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:214: this->connect(d->ConvertOutputDisplacementFieldNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(updateConvertButtonState()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:706: if (d->ConvertOutputDisplacementFieldNodeComboBox->currentNode() == nullptr)`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:711: vtkMRMLScalarVolumeNode* scalarOutputVolumeNode = vtkMRMLScalarVolumeNode::SafeDownCast(d->ConvertOutputDisplacementFieldNodeComboBox->currentNode());`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:712: vtkMRMLVectorVolumeNode* vectorOutputVolumeNode = vtkMRMLVectorVolumeNode::SafeDownCast(d->ConvertOutputDisplacementFieldNodeComboBox->currentNode());`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:713: vtkMRMLTransformNode* outputTransformNode = vtkMRMLTransformNode::SafeDownCast(d->ConvertOutputDisplacementFieldNodeComboBox->currentNode());`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:747: && d->ConvertOutputDisplacementFieldNodeComboBox->currentNode() != nullptr);`
- Connected slots/functions: `updateConvertButtonState`
- API footprints: `vtkMRMLScalarVolumeNode::SafeDownCast`, `vtkMRMLTransformNode::SafeDownCast`, `vtkMRMLVectorVolumeNode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTransformNode", "vtkMRMLScalarVolumeNode", "vtkMRMLVectorVolumeNode"]}

## widget: ConvertPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Apply | ConvertPushButton | QPushButton
- Text: Apply
- Implementation candidates: `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx`, `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:210: this->connect(d->ConvertPushButton, SIGNAL(clicked()), SLOT(convert()));`
  - `Modules/Loadable/Transforms/qSlicerTransformsModuleWidget.cxx:748: d->ConvertPushButton->setEnabled(enableConvert);`
- Connected slots/functions: `convert`
- API footprints: `ConvertToGridTransform`, `CreateDisplacementVolumeFromTransform`, `vtkMRMLScalarVolumeNode::SafeDownCast`, `vtkMRMLTransformNode::SafeDownCast`, `vtkMRMLVectorVolumeNode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`
