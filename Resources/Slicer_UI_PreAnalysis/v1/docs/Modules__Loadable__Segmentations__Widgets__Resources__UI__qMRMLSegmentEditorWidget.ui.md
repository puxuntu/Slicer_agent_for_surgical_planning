# Slicer UI Analysis: Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentEditorWidget.ui

- Owner class: `qMRMLSegmentEditorWidget`
- UI file: `Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentEditorWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentEditorWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSegmentEditorWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:24: #include "qMRMLSegmentEditorWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:26: #include "ui_qMRMLSegmentEditorWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:117: QPointer<qMRMLSegmentEditorWidget> EditorWidget;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:131: // qMRMLSegmentEditorWidgetPrivate methods`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:134: class qMRMLSegmentEditorWidgetPrivate : public Ui_qMRMLSegmentEditorWidget`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:136: Q_DECLARE_PUBLIC(qMRMLSegmentEditorWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:139: qMRMLSegmentEditorWidget* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:142: explicit qMRMLSegmentEditorWidgetPrivate(qMRMLSegmentEditorWidget& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:143: ~qMRMLSegmentEditorWidgetPrivate();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:240: CTK_GET_CPP(qMRMLSegmentEditorWidget, bool, maskingSectionVisible, MaskingSectionVisible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:241: CTK_GET_CPP(qMRMLSegmentEditorWidget, bool, specifyGeometryButtonVisible, SpecifyGeometryButtonVisible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:244: qMRMLSegmentEditorWidgetPrivate::qMRMLSegmentEditorWidgetPrivate(qMRMLSegmentEditorWidget& object)`
- API footprints: `CanRedo`, `CanTriviallyConvertSourceRepresentationToBinaryLabelMap`, `CanUndo`, `ExportSegmentationToColorTableNode`, `GetCurrentSegmentID`, `GetMaximumNumberOfUndoStates`, `GetPointer`, `GetSegmentIDs`, `GetSegmentationIJKToRAS`, `GetSegmentationNode`, `GetSourceVolumeNode`, `IsBatchProcessing`, `IsClosing`, `IsSegmentationDisplayableInView`, `Redo`, `RemoveSelectedSegment`, `SaveStateForUndo`, `SetCallback`, `SetClientData`, `SetDefaultTerminologyEntry`, `SetMaximumNumberOfUndoStates`, `SetSourceVolumeNode`, `ToggleSegmentationSurfaceRepresentation`, `ToggleSourceVolumeIntensityMask`, `Undo`, `UpdateVolume`, `vtkMRMLSegmentEditorNode::OverwriteAllSegments`, `vtkMRMLSegmentEditorNode::OverwriteNone`, `vtkMRMLSegmentEditorNode::OverwriteVisibleSegments`, `vtkMRMLSegmentationNode::EditAllowedEverywhere`

## widget: SourceVolumeNodeLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Source volume: | SourceVolumeNodeLabel | QLabel
- Text: Source volume:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2203: d->SourceVolumeNodeLabel->setVisible(visible);`

## widget: SourceVolumeNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: SourceVolumeNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:301: this->SourceVolumeNodeComboBox->setSizeAdjustPolicy(QComboBox::AdjustToMinimumContentsLengthWithIcon);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:305: this->SpecifyGeometryButton->setMaximumHeight(this->SourceVolumeNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:306: this->SpecifyGeometryButton->setMaximumWidth(this->SourceVolumeNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:339: QObject::connect(this->SourceVolumeNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onSourceVolumeNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:649: d->SourceVolumeNodeComboBox->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:664: d->SourceVolumeNodeComboBox->setEnabled(d->SegmentationNode != nullptr);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:885: d->SourceVolumeNodeComboBox->setCurrentNode(referenceVolumeNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:954: bool wasBlocked = d->SourceVolumeNodeComboBox->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:955: d->SourceVolumeNodeComboBox->setCurrentNode(d->SourceVolumeNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:956: d->SourceVolumeNodeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1156: const QSignalBlocker blocker2(d->SourceVolumeNodeComboBox);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1211: if (d->ParameterSetNode->GetSourceVolumeNode() != d->SourceVolumeNodeComboBox->currentNode())`
- Connected slots/functions: `onSourceVolumeNodeChanged`
- API footprints: `GetNodeReference`, `GetSourceVolumeNode`, `IsBatchProcessing`, `vtkMRMLSegmentationNode::EditAllowedEverywhere`, `vtkMRMLSegmentationNode::GetReferenceImageGeometryReferenceRole`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: SegmentationNodeLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Segmentation: | SegmentationNodeLabel | QLabel
- Text: Segmentation:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2174: d->SegmentationNodeLabel->setVisible(visible);`

## widget: SpecifyGeometryButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Specify geometry of the edited labelmap representation | Specify geometry (grid origin, spacing, axis directions, and default extent) of the edited labelmap representation | SpecifyGeometryButton | QToolButton
- Text: Specify geometry of the edited labelmap representation
- Tooltip: Specify geometry (grid origin, spacing, axis directions, and default extent) of the edited labelmap representation
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:182: bool SpecifyGeometryButtonVisible{ true };`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:241: CTK_GET_CPP(qMRMLSegmentEditorWidget, bool, specifyGeometryButtonVisible, SpecifyGeometryButtonVisible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:305: this->SpecifyGeometryButton->setMaximumHeight(this->SourceVolumeNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:306: this->SpecifyGeometryButton->setMaximumWidth(this->SourceVolumeNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:340: QObject::connect(this->SpecifyGeometryButton, SIGNAL(clicked()), q, SLOT(showSegmentationGeometryDialog()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2204: d->SpecifyGeometryButton->setVisible(visible && d->SpecifyGeometryButtonVisible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2943: void qMRMLSegmentEditorWidget::setSpecifyGeometryButtonVisible(bool visible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2946: d->SpecifyGeometryButtonVisible = visible;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2947: d->SpecifyGeometryButton->setVisible(d->SourceVolumeNodeComboBox->isVisible() && d->SpecifyGeometryButtonVisible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:72: Q_PROPERTY(bool specifyGeometryButtonVisible READ specifyGeometryButtonVisible WRITE setSpecifyGeometryButtonVisible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:343: void setSpecifyGeometryButtonVisible(bool);`
- Connected slots/functions: `showSegmentationGeometryDialog`
- API footprints: `CreateAndSetBlankSourceVolumeIfNeeded`, `vtkMRMLSegmentationNode::EditAllowedEverywhere`

## widget: SegmentationNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: SegmentationNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:300: this->SegmentationNodeComboBox->setSizeAdjustPolicy(QComboBox::AdjustToMinimumContentsLengthWithIcon);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:303: this->SliceRotateWarningButton->setMaximumHeight(this->SegmentationNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:304: this->SliceRotateWarningButton->setMaximumWidth(this->SegmentationNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:337: QObject::connect(this->SegmentationNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onSegmentationNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:645: d->SegmentationNodeComboBox->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:653: d->SegmentationNodeComboBox->setEnabled(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:854: // d->SegmentationNodeComboBox->currentNode() may initially differ from d->SegmentationNode.`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:855: if (segmentationNode != d->SegmentationNodeComboBox->currentNode())`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:857: bool wasBlocked = d->SegmentationNodeComboBox->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:858: d->SegmentationNodeComboBox->setCurrentNode(segmentationNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:859: d->SegmentationNodeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1155: const QSignalBlocker blocker1(d->SegmentationNodeComboBox);`
- Connected slots/functions: `onSegmentationNodeChanged`
- API footprints: `GetSegmentationNode`, `GetSourceVolumeNode`, `IsBatchProcessing`
- Key UI properties: {"nodeTypes": ["vtkMRMLSegmentationNode"]}

## widget: SliceRotateWarningButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Slice rotated | Slice views orientation are not aligned with segmentation. Striping artifacts may appear. Click to align slice views to segmentation. | SliceRotateWarningButton | QToolButton
- Text: Slice rotated
- Tooltip: Slice views orientation are not aligned with segmentation. Striping artifacts may appear. Click to align slice views to segmentation.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:303: this->SliceRotateWarningButton->setMaximumHeight(this->SegmentationNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:304: this->SliceRotateWarningButton->setMaximumWidth(this->SegmentationNodeComboBox->sizeHint().height());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:338: QObject::connect(this->SliceRotateWarningButton, SIGNAL(clicked()), q, SLOT(rotateSliceViewsToSegmentation()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:392: q->updateSliceRotateWarningButtonVisibility();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:659: this->updateSliceRotateWarningButtonVisibility();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:834: this->updateSliceRotateWarningButtonVisibility();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:871: qvtkReconnect(d->SegmentationNode, segmentationNode, vtkSegmentation::SourceRepresentationModified, this, SLOT(updateSliceRotateWarningButtonVisibility()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1956: this->updateSliceRotateWarningButtonVisibility();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2026: self->updateSliceRotateWarningButtonVisibility();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2180: d->SegmentActionsLayout->removeWidget(d->SliceRotateWarningButton);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2181: d->SegmentationNodeSelectorLayout->addWidget(d->SliceRotateWarningButton);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2185: d->SegmentationNodeSelectorLayout->removeWidget(d->SliceRotateWarningButton);`
- Connected slots/functions: `rotateSliceViewsToSegmentation`, `updateSliceRotateWarningButtonVisibility`
- API footprints: `GetPointer`, `GetSegmentation`, `GetSegmentationIJKToRAS`, `GetSegmentationNode`, `GetSliceToRAS`, `RotateToAxes`, `vtkMRMLDisplayableNode::DisplayModifiedEvent`

## widget: AddSegmentButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Add | Add new empty segment | AddSegmentButton | QPushButton
- Text: Add
- Tooltip: Add new empty segment
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:343: QObject::connect(this->AddSegmentButton, SIGNAL(clicked()), q, SLOT(onAddSegment()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:365: this->AddSegmentButton->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:682: d->AddSegmentButton->setEnabled(d->Logic->CanAddSegments());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2968: d->AddSegmentButton->setVisible(visible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2976: return d->AddSegmentButton->isVisible() && d->RemoveSegmentButton->isVisible();`
- Connected slots/functions: `onAddSegment`
- API footprints: `AddEmptySegment`, `CanAddSegments`

## widget: RemoveSegmentButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Remove | Remove selected segment(s) | RemoveSegmentButton | QPushButton
- Text: Remove
- Tooltip: Remove selected segment(s)
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:344: QObject::connect(this->RemoveSegmentButton, SIGNAL(clicked()), q, SLOT(onRemoveSegment()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:366: this->RemoveSegmentButton->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:685: d->RemoveSegmentButton->setEnabled(!selectedSegmentID.isEmpty() && (!d->Locked));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2965: void qMRMLSegmentEditorWidget::setAddRemoveSegmentButtonsVisible(bool visible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2969: d->RemoveSegmentButton->setVisible(visible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2973: bool qMRMLSegmentEditorWidget::addRemoveSegmentButtonsVisible() const`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2976: return d->AddSegmentButton->isVisible() && d->RemoveSegmentButton->isVisible();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:74: Q_PROPERTY(bool addRemoveSegmentButtonsVisible READ addRemoveSegmentButtonsVisible WRITE setAddRemoveSegmentButtonsVisible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:206: bool addRemoveSegmentButtonsVisible() const;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:349: void setAddRemoveSegmentButtonsVisible(bool);`
- Connected slots/functions: `onRemoveSegment`
- API footprints: `RemoveSelectedSegment`

## widget: Show3DButton

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLSegmentationShow3DButton`
- Search text: Show3DButton | qMRMLSegmentationShow3DButton
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:650: d->Show3DButton->setLocked(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:687: d->Show3DButton->setLocked(d->Locked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:878: d->Show3DButton->setSegmentationNode(segmentationNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2951: void qMRMLSegmentEditorWidget::setShow3DButtonVisible(bool visible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2954: d->Show3DButton->setVisible(visible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2961: return d->Show3DButton->isVisible();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:73: Q_PROPERTY(bool show3DButtonVisible READ show3DButtonVisible WRITE setShow3DButtonVisible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:346: void setShow3DButtonVisible(bool);`

## widget: SwitchToSegmentationsButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Segmentations | Go to Segmentations module | SwitchToSegmentationsButton | QToolButton
- Text: Segmentations
- Tooltip: Go to Segmentations module
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:320: this->SwitchToSegmentationsButton->setIcon(q->style()->standardIcon(QStyle::SP_ArrowRight));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:322: QMenu* segmentationsButtonMenu = new QMenu(qMRMLSegmentEditorWidget::tr("Segmentations"), this->SwitchToSegmentationsButton);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:334: this->SwitchToSegmentationsButton->setMenu(segmentationsButtonMenu);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:345: QObject::connect(this->SwitchToSegmentationsButton, SIGNAL(clicked()), q, SLOT(onSwitchToSegmentations()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:367: this->SwitchToSegmentationsButton->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:688: d->SwitchToSegmentationsButton->setEnabled(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1581: d->SwitchToSegmentationsButton->setEnabled(segmentationNode != nullptr);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2211: return d->SwitchToSegmentationsButton->isVisible();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2215: void qMRMLSegmentEditorWidget::setSwitchToSegmentationsButtonVisible(bool visible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2218: d->SwitchToSegmentationsButton->setVisible(visible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:78: Q_PROPERTY(bool switchToSegmentationsButtonVisible READ switchToSegmentationsButtonVisible WRITE setSwitchToSegmentationsButtonVisible)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h:351: void setSwitchToSegmentationsButtonVisible(bool);`
- Connected slots/functions: `onSwitchToSegmentations`
- API footprints: `GetSegmentationNode`, `vtkMRMLSegmentEditorNode::OverwriteNone`
- Key UI properties: {"popupMode": "QToolButton::MenuButtonPopup"}

## widget: EffectsGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `QFrame`
- Search text: EffectsGroupBox | QFrame
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:368: this->EffectsGroupBox->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:371: this->EffectsGroupBox->setLayout(new QGridLayout(this->EffectsGroupBox));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:487: QToolButton* effectButton = new QToolButton(d->EffectsGroupBox);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:529: QToolButton* effectButton = new QToolButton(d->EffectsGroupBox);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:557: while ((child = d->EffectsGroupBox->layout()->takeAt(0)) != 0)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:595: auto gridLayout = dynamic_cast<QGridLayout*>(d->EffectsGroupBox->layout());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:608: // Set UndoRedoGroupBox buttons with same column count as EffectsGroupBox`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:646: d->EffectsGroupBox->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:661: d->EffectsGroupBox->setEnabled(d->SegmentationNode != nullptr);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1034: d->EffectsGroupBox->setEnabled(effectsOverallEnabled);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1798: return d->EffectsGroupBox->layout()->count();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1805: if (index < 0 || index >= d->EffectsGroupBox->layout()->count())`
- API footprints: `GetReferenceGeometryImage`, `GetSourceVolumeNode`

## widget: UndoRedoGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `QFrame`
- Search text: UndoRedoGroupBox | QFrame
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:212: /// Button group for the UndoRedoGroupBox`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:608: // Set UndoRedoGroupBox buttons with same column count as EffectsGroupBox`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:614: auto undoRedoGridLayout = dynamic_cast<QGridLayout*>(d->UndoRedoGroupBox->layout());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2225: return d->UndoRedoGroupBox->isVisible();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2236: d->UndoRedoGroupBox->setVisible(enabled);`
- API footprints: `ClearUndoState`

## widget: UndoButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Undo | Undo last editing operation | UndoButton | QToolButton
- Text: Undo
- Tooltip: Undo last editing operation
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:352: QObject::connect(this->UndoButton, SIGNAL(clicked()), q, SLOT(undo()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:376: this->UndoRedoButtonGroup.addButton(this->UndoButton);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2297: d->UndoButton->setEnabled(!d->Locked && d->Logic->CanUndo());`
- Connected slots/functions: `undo`
- API footprints: `CanRedo`, `CanUndo`, `Undo`

## widget: RedoButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Redo | Redo last editing operation | RedoButton | QToolButton
- Text: Redo
- Tooltip: Redo last editing operation
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:213: QButtonGroup UndoRedoButtonGroup;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:353: QObject::connect(this->RedoButton, SIGNAL(clicked()), q, SLOT(redo()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:376: this->UndoRedoButtonGroup.addButton(this->UndoButton);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:377: this->UndoRedoButtonGroup.addButton(this->RedoButton);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:611: QList<QAbstractButton*> undoRedoButtons = d->UndoRedoButtonGroup.buttons();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:612: for (QAbstractButton* const button : undoRedoButtons)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:710: this->updateUndoRedoButtonsState();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2294: void qMRMLSegmentEditorWidget::updateUndoRedoButtonsState()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2298: d->RedoButton->setEnabled(!d->Locked && d->Logic->CanRedo());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2304: this->updateUndoRedoButtonsState();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2503: QList<QAbstractButton*> undoRedoButtons = d->UndoRedoButtonGroup.buttons();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2504: for (QAbstractButton* const button : undoRedoButtons)`
- Connected slots/functions: `redo`
- API footprints: `CanRedo`, `CanUndo`, `Redo`

## widget: SegmentsTableResizableFrame

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: SegmentsTableResizableFrame | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`

## widget: SegmentsTableView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSegmentsTableView`
- Search text: SegmentsTableView | qMRMLSegmentsTableView
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:341: QObject::connect(this->SegmentsTableView, SIGNAL(selectionChanged(QItemSelection, QItemSelection)), q, SLOT(onSegmentSelectionChanged(QItemSelection, QItemSelection)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:342: QObject::connect(this->SegmentsTableView, SIGNAL(segmentAboutToBeModified(QString)), q, SLOT(saveStateForUndo()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:360: this->SegmentsTableView->setSelectionMode(QAbstractItemView::SingleSelection);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:361: this->SegmentsTableView->setHeaderVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:362: this->SegmentsTableView->setVisibilityColumnVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:363: this->SegmentsTableView->setColorColumnVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:364: this->SegmentsTableView->setOpacityColumnVisible(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:454: this->SegmentsTableView->setSelectedSegmentIDs(firstSegmentID);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:697: d->SegmentsTableView->setSelectedSegmentIDs(segmentID);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:702: d->SegmentsTableView->clearSelection();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:704: d->SegmentsTableView->setReadOnly(d->Locked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:874: bool wasBlocked = d->SegmentsTableView->blockSignals(true);`
- Connected slots/functions: `onSegmentSelectionChanged`, `saveStateForUndo`
- API footprints: `AddEmptySegment`, `GetSelectedSegmentID`, `SaveStateForUndo`, `SetSelectedSegmentID`

## widget: OptionsGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `QGroupBox`
- Search text: OptionsGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:369: this->OptionsGroupBox->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:387: this->OptionsGroupBox->hide();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:388: this->OptionsGroupBox->setTitle("");`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1035: d->OptionsGroupBox->setEnabled(effectsOverallEnabled);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1092: d->OptionsGroupBox->show();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1093: d->OptionsGroupBox->setTitle(activeEffect->title());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1099: d->OptionsGroupBox->hide();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1100: d->OptionsGroupBox->setTitle("");`
- API footprints: `GetSourceVolumeNode`

## widget: EffectHelpBrowser

- Confidence: `linked_to_code`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: EffectHelpBrowser | ctkFittedTextBrowser
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:389: this->EffectHelpBrowser->setText("");`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1094: d->EffectHelpBrowser->setCollapsibleText(activeEffect->helpText());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1101: d->EffectHelpBrowser->setText("");`

## widget: EffectsOptionsFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: EffectsOptionsFrame | QFrame
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:380: QVBoxLayout* layout = new QVBoxLayout(this->EffectsOptionsFrame);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:546: d->EffectsOptionsFrame->layout()->addWidget(effectOptionsFrame);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:648: d->EffectsOptionsFrame->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:663: d->EffectsOptionsFrame->setEnabled(d->SegmentationNode != nullptr);`

## widget: MaskingGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: MaskingGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:390: this->MaskingGroupBox->hide();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:647: d->MaskingGroupBox->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:662: d->MaskingGroupBox->setEnabled(d->SegmentationNode != nullptr);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1095: d->MaskingGroupBox->setVisible(d->MaskingSectionVisible);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:1102: d->MaskingGroupBox->hide();`

## widget: MaskModeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Editable area: | MaskModeLabel | QLabel
- Text: Editable area:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`

## widget: MaskModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: MaskModeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:215: int MaskModeComboBoxFixedItemsCount;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:251: , MaskModeComboBoxFixedItemsCount(0)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:308: this->MaskModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Everywhere"), vtkMRMLSegmentationNode::EditAllowedEverywhere);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:309: this->MaskModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Inside all segments"), vtkMRMLSegmentationNode::EditAllowedInsideAllSegments);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:310: this->MaskModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Inside all visible segments"), vtkMRMLSegmentationNode::EditAllowedInsideVisibleSegments);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:311: this->MaskModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Outside all segments"), vtkMRMLSegmentationNode::EditAllowedOutsideAllSegments);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:312: this->MaskModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Outside all visible segments"), vtkMRMLSegmentationNode::EditAllowedOutsideVisibleSegments);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:313: this->MaskModeComboBox->insertSeparator(this->MaskModeComboBox->count());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:314: this->MaskModeComboBoxFixedItemsCount = this->MaskModeComboBox->count();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:347: QObject::connect(this->MaskModeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onMaskModeChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:734: bool wasBlocked = d->MaskModeComboBox->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:739: maskModeIndex = d->MaskModeComboBox->findData(qSlicerUtils::safeQStringFromUtf8Ptr(d->ParameterSetNode->GetMaskSegmentID()));`
- Connected slots/functions: `onMaskModeChanged`
- API footprints: `GetMaskMode`, `GetMaskSegmentID`, `GetName`, `GetSegment`, `SetMaskMode`, `SetMaskSegmentID`, `vtkMRMLSegmentEditorNode::OverwriteAllSegments`, `vtkMRMLSegmentationNode::EditAllowedEverywhere`, `vtkMRMLSegmentationNode::EditAllowedInsideAllSegments`, `vtkMRMLSegmentationNode::EditAllowedInsideSingleSegment`, `vtkMRMLSegmentationNode::EditAllowedInsideVisibleSegments`, `vtkMRMLSegmentationNode::EditAllowedOutsideAllSegments`, `vtkMRMLSegmentationNode::EditAllowedOutsideVisibleSegments`

## widget: SourceVolumeIntensityMaskRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Editable intensity range: | SourceVolumeIntensityMaskRangeLabel | QLabel
- Text: Editable intensity range:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`

## widget: SourceVolumeIntensityMaskCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: Only those regions are allowed to be changed where the source volume intensity is in the specified range | SourceVolumeIntensityMaskCheckBox | ctkCheckBox
- Tooltip: Only those regions are allowed to be changed where the source volume intensity is in the specified range
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:348: QObject::connect(this->SourceVolumeIntensityMaskCheckBox, SIGNAL(toggled(bool)), q, SLOT(onSourceVolumeIntensityMaskChecked(bool)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:749: wasBlocked = d->SourceVolumeIntensityMaskCheckBox->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:750: d->SourceVolumeIntensityMaskCheckBox->setChecked(d->ParameterSetNode->GetSourceVolumeIntensityMask());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:751: d->SourceVolumeIntensityMaskCheckBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onSourceVolumeIntensityMaskChecked`
- API footprints: `GetSourceVolumeIntensityMask`, `SetSourceVolumeIntensityMask`

## widget: SourceVolumeIntensityMaskRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkRangeWidget`
- Search text: SourceVolumeIntensityMaskRangeWidget | ctkRangeWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:349: QObject::connect(this->SourceVolumeIntensityMaskRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(onSourceVolumeIntensityMaskRangeChanged(double, double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:784: wasBlocked = d->SourceVolumeIntensityMaskRangeWidget->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:785: d->SourceVolumeIntensityMaskRangeWidget->setVisible(d->ParameterSetNode->GetSourceVolumeIntensityMask());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:786: d->SourceVolumeIntensityMaskRangeWidget->setMinimumValue(d->ParameterSetNode->GetSourceVolumeIntensityMaskRange()[0]);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:787: d->SourceVolumeIntensityMaskRangeWidget->setMaximumValue(d->ParameterSetNode->GetSourceVolumeIntensityMaskRange()[1]);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:788: d->SourceVolumeIntensityMaskRangeWidget->blockSignals(wasBlocked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:983: d->SourceVolumeIntensityMaskRangeWidget->setRange(range[0], range[1]);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:984: d->SourceVolumeIntensityMaskRangeWidget->setEnabled(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:988: d->SourceVolumeIntensityMaskRangeWidget->setEnabled(false);`
- Connected slots/functions: `onSourceVolumeIntensityMaskRangeChanged`
- API footprints: `GetImageData`, `GetScalarRange`, `GetSourceVolumeIntensityMask`, `GetSourceVolumeIntensityMaskRange`, `SetSourceVolumeIntensityMaskRange`

## widget: OverwriteModeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Modify other segments: | OverwriteModeLabel | QLabel
- Text: Modify other segments:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`

## widget: OverwriteModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Controls which segments the current segment will overwrite. Segments that are not overwritten may overlap with the selected segment. | OverwriteModeComboBox | QComboBox
- Tooltip: Controls which segments the current segment will overwrite. Segments that are not overwritten may overlap with the selected segment.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:316: this->OverwriteModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Overwrite all"), vtkMRMLSegmentEditorNode::OverwriteAllSegments);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:317: this->OverwriteModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Overwrite visible"), vtkMRMLSegmentEditorNode::OverwriteVisibleSegments);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:318: this->OverwriteModeComboBox->addItem(qMRMLSegmentEditorWidget::tr("Allow overlap"), vtkMRMLSegmentEditorNode::OverwriteNone);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:350: QObject::connect(this->OverwriteModeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onOverwriteModeChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:790: wasBlocked = d->OverwriteModeComboBox->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:791: int overwriteModeIndex = d->OverwriteModeComboBox->findData(d->ParameterSetNode->GetOverwriteMode());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:792: d->OverwriteModeComboBox->setCurrentIndex(overwriteModeIndex);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:793: d->OverwriteModeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentEditorWidget.cxx:2159: d->ParameterSetNode->SetOverwriteMode(d->OverwriteModeComboBox->itemData(index).toInt());`
- Connected slots/functions: `onOverwriteModeChanged`
- API footprints: `GetOverwriteMode`, `SetOverwriteMode`, `vtkMRMLSegmentEditorNode::OverwriteAllSegments`, `vtkMRMLSegmentEditorNode::OverwriteNone`, `vtkMRMLSegmentEditorNode::OverwriteVisibleSegments`
