# Slicer UI Analysis: Modules/Loadable/CropVolume/Resources/UI/qSlicerCropVolumeModuleWidget.ui

- Owner class: `qSlicerCropVolumeModuleWidget`
- UI file: `Modules/Loadable/CropVolume/Resources/UI/qSlicerCropVolumeModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerCropVolumeModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerCropVolumeModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:21: #include "qSlicerCropVolumeModuleWidget.h"`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:22: #include "ui_qSlicerCropVolumeModuleWidget.h"`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:42: class qSlicerCropVolumeModuleWidgetPrivate : public Ui_qSlicerCropVolumeModuleWidget`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:44: Q_DECLARE_PUBLIC(qSlicerCropVolumeModuleWidget);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:47: qSlicerCropVolumeModuleWidget* const q_ptr;`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:50: qSlicerCropVolumeModuleWidgetPrivate(qSlicerCropVolumeModuleWidget& object);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:51: ~qSlicerCropVolumeModuleWidgetPrivate();`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:68: // qSlicerCropVolumeModuleWidgetPrivate methods`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:71: qSlicerCropVolumeModuleWidgetPrivate::qSlicerCropVolumeModuleWidgetPrivate(qSlicerCropVolumeModuleWidget& object)`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:77: qSlicerCropVolumeModuleWidgetPrivate::~qSlicerCropVolumeModuleWidgetPrivate() = default;`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:80: vtkSlicerCropVolumeLogic* qSlicerCropVolumeModuleWidgetPrivate::logic() const`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:82: Q_Q(const qSlicerCropVolumeModuleWidget);`
- Connected slots/functions: `mappedInt`, `setFitROIMode`
- API footprints: `FitROI`, `GetClassName`, `GetInputVolumeNode`, `GetOutputVolumeNode`, `GetPointer`, `GetROINode`, `IsBatchProcessing`, `ReorientVolumeEnd`, `ReorientVolumeStart`, `SetFitROIMode`, `vtkMRMLCropVolumeParametersNode::FitROIKeepOrientation`, `vtkMRMLCropVolumeParametersNode::SafeDownCast`

## widget: ParameterSetCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Crop Volume | ParameterSetCollapsibleButton | ctkCollapsibleButton
- Text: Crop Volume
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: ParameterNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Parameter set: | ParameterNodeLabel | QLabel
- Text: Parameter set:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: ParametersNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ParametersNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:98: this->ParametersNodeComboBox->addNode();`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:253: connect(d->ParametersNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(setParametersNode(vtkMRMLNode*)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:349: d->ParametersNodeComboBox->setCurrentNode(parametersNode.GetPointer());`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:355: if (d->ParametersNodeComboBox->currentNode() == nullptr)`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:357: d->ParametersNodeComboBox->setCurrentNode(scene->GetFirstNodeByClass("vtkMRMLCropVolumeParametersNode"));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:440: // before ParametersNodeComboBox is initialized, so don't log a warning here`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:454: vtkMRMLCropVolumeParametersNode* parametersNode = vtkMRMLCropVolumeParametersNode::SafeDownCast(d->ParametersNodeComboBox->currentNode());`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:716: d->ParametersNodeComboBox->setCurrentNode(node);`
- Connected slots/functions: `setParametersNode`
- API footprints: `GetFirstNodeByClass`, `GetPointer`, `vtkMRMLCropVolumeParametersNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLCropVolumeParametersNode"]}

## widget: InputOutputCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: IO | InputOutputCollapsibleButton | ctkCollapsibleButton
- Text: IO
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InputVolumeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input volume: | InputVolumeLabel | QLabel
- Text: Input volume:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InputVolumeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: InputVolumeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:255: connect(d->InputVolumeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(setInputVolume(vtkMRMLNode*)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:439: // setInputVolume may be triggered by calling setScene on InputVolumeComboBox`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:648: d->InputVolumeComboBox->setCurrentNode(nullptr);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:685: d->InputVolumeComboBox->setCurrentNode(d->ParametersNode->GetInputVolumeNode());`
- Connected slots/functions: `setInputVolume`
- API footprints: `GetID`, `GetInputVolumeNode`, `GetOutputVolumeNode`, `GetPointer`, `GetROINode`, `SetInputVolumeNodeID`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: InputROILabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input ROI: | InputROILabel | QLabel
- Text: Input ROI:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InputROIComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: InputROIComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:179: this->InputROIComboBox->addNode();`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:261: connect(d->InputROIComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(setInputROI(vtkMRMLNode*)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:262: connect(d->InputROIComboBox, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), this, SLOT(initializeInputROI(vtkMRMLNode*)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:263: connect(d->InputROIComboBox, SIGNAL(nodeAdded(vtkMRMLNode*)), this, SLOT(onInputROIAdded(vtkMRMLNode*)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:649: d->InputROIComboBox->setCurrentNode(nullptr);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:686: d->InputROIComboBox->setCurrentNode(d->ParametersNode->GetROINode());`
- Connected slots/functions: `initializeInputROI`, `onInputROIAdded`, `setInputROI`
- API footprints: `CreateDefaultDisplayNodes`, `GetDisplayNode`, `GetID`, `GetInputVolumeNode`, `GetOutputVolumeNode`, `GetPointer`, `GetROINode`, `GetVoxelBased`, `SetFillVisibility`, `SetHandlesInteractive`, `SetROINodeID`, `vtkMRMLMarkupsDisplayNode::SafeDownCast`, `vtkMRMLMarkupsROINode::SafeDownCast`, `vtkMRMLTransformableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLMarkupsROINode"]}

## widget: VisibilityButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: Display ROI | VisibilityButton | ctkCheckBox
- Text: Display ROI
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:267: connect(d->VisibilityButton, SIGNAL(toggled(bool)), this, SLOT(onROIVisibilityChanged(bool)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:655: d->VisibilityButton->setChecked(true);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:698: d->VisibilityButton->setChecked(d->ParametersNode->GetROINode() && (d->ParametersNode->GetROINode()->GetDisplayVisibility() != 0));`
- Connected slots/functions: `onROIVisibilityChanged`
- API footprints: `GetDisplayVisibility`, `GetIsotropicResampling`, `GetROINode`, `GetSpacingScalingConst`, `SetDisplayVisibility`

## widget: ROIFitPushButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkMenuButton`
- Search text: Fit to Volume | ROIFitPushButton | ctkMenuButton
- Text: Fit to Volume
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:246: d->FitROIModeMenu = new QMenu(tr("ROI fit mode"), d->ROIFitPushButton);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:248: d->ROIFitPushButton->setMenu(d->FitROIModeMenu);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:268: connect(d->ROIFitPushButton, SIGNAL(clicked()), this, SLOT(onROIFit()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:665: d->ROIFitPushButton->setEnabled(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:670: d->ROIFitPushButton->setEnabled(d->ParametersNode->GetInputVolumeNode() != nullptr);`
- Connected slots/functions: `onROIFit`
- API footprints: `FitROI`, `GetInputVolumeNode`

## widget: OutputVolumeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Output volume: | OutputVolumeLabel | QLabel
- Text: Output volume:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: OutputVolumeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: OutputVolumeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:265: connect(d->OutputVolumeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(setOutputVolume(vtkMRMLNode*)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:650: d->OutputVolumeComboBox->setCurrentNode(nullptr);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:687: d->OutputVolumeComboBox->setCurrentNode(d->ParametersNode->GetOutputVolumeNode());`
- Connected slots/functions: `setOutputVolume`
- API footprints: `GetID`, `GetInputVolumeNode`, `GetOutputVolumeNode`, `GetROINode`, `GetVoxelBased`, `SetOutputVolumeNodeID`, `vtkMRMLCropVolumeParametersNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode", "vtkMRMLVectorVolumeNode"]}

## widget: ReorientInputVolumeGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: ReorientInputVolumeGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:652: d->ReorientInputVolumeGroupBox->setEnabled(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:672: d->ReorientInputVolumeGroupBox->setEnabled(d->ParametersNode->GetInputVolumeNode() != nullptr);`
- API footprints: `GetInputVolumeNode`, `GetReorientTransformNode`

## widget: ReorientInputVolumeCancelButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Cancel | ReorientInputVolumeCancelButton | QPushButton
- Text: Cancel
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:259: connect(d->ReorientInputVolumeCancelButton, SIGNAL(clicked()), this, SLOT(onReorientInputVolumeCancel()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:676: d->ReorientInputVolumeCancelButton->setEnabled(reorientInProgress);`
- Connected slots/functions: `onReorientInputVolumeCancel`
- API footprints: `GetFitROIMode`, `ReorientVolumeEnd`

## widget: ReorientInputVolumeApplyButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Apply | ReorientInputVolumeApplyButton | QPushButton
- Text: Apply
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:258: connect(d->ReorientInputVolumeApplyButton, SIGNAL(clicked()), this, SLOT(onReorientInputVolumeApply()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:675: d->ReorientInputVolumeApplyButton->setEnabled(reorientInProgress);`
- Connected slots/functions: `onReorientInputVolumeApply`
- API footprints: `GetReorientTransformNode`, `ReorientVolumeEnd`

## widget: ReorientInputVolumeInitializeButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Initialize | ReorientInputVolumeInitializeButton | QPushButton
- Text: Initialize
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:257: connect(d->ReorientInputVolumeInitializeButton, SIGNAL(clicked()), this, SLOT(onReorientInputVolumeInitialize()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:674: d->ReorientInputVolumeInitializeButton->setEnabled(!reorientInProgress);`
- Connected slots/functions: `onReorientInputVolumeInitialize`
- API footprints: `GetInputVolumeNode`, `GetReorientTransformNode`, `ReorientVolumeStart`

## widget: InterpolationOptionsCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced | InterpolationOptionsCollapsibleButton | ctkCollapsibleButton
- Text: Advanced
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: FillValueLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Fill value: | FillValueLabel | QLabel
- Text: Fill value:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: FillValueSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Voxel values outside the input volume will be filled with this value | FillValueSpinBox | ctkDoubleSpinBox
- Tooltip: Voxel values outside the input volume will be filled with this value
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:279: connect(d->FillValueSpinBox, SIGNAL(valueChanged(double)), this, SLOT(onFillValueChanged(double)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:660: d->FillValueSpinBox->setValue(0.0);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:702: d->FillValueSpinBox->setValue(d->ParametersNode->GetFillValue());`
- Connected slots/functions: `onFillValueChanged`
- API footprints: `GetFillValue`, `GetSpacingScalingConst`, `SetFillValue`

## widget: IsotropicOutputVoxelLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Interpolated cropping: | IsotropicOutputVoxelLabel_2 | QLabel
- Text: Interpolated cropping:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InterpolationEnabledCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Interpolate and pad the input volume to make the output image exactly the size of the ROI, with the requested spacing. | InterpolationEnabledCheckBox | QCheckBox
- Tooltip: Interpolate and pad the input volume to make the output image exactly the size of the ROI, with the requested spacing.
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:270: connect(d->InterpolationEnabledCheckBox, SIGNAL(toggled(bool)), this, SLOT(onInterpolationEnabled(bool)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:654: d->InterpolationEnabledCheckBox->setChecked(true);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:688: d->InterpolationEnabledCheckBox->setChecked(!d->ParametersNode->GetVoxelBased());`
- Connected slots/functions: `onInterpolationEnabled`
- API footprints: `GetInterpolationMode`, `GetOutputVolumeNode`, `GetROINode`, `GetVoxelBased`, `SetVoxelBased`
- Key UI properties: {"checked": "true"}

## widget: InputSpacingScalingConstantLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Spacing scale: | The voxel spacing in the output volume will be scaled by this value. Values larger than 1.0 will make the cropped volume lower resolution than the input volume. Values smaller than 1.0 will make the cropped volume higher resolution than the input volume. | InputSpacingScalingConstantLabel | QLabel
- Text: Spacing scale:
- Tooltip: The voxel spacing in the output volume will be scaled by this value. Values larger than 1.0 will make the cropped volume lower resolution than the input volume. Values smaller than 1.0 will make the cropped volume higher resolution than the input volume.
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: SpacingScalingSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: The voxel spacing in the output volume will be scaled by this value. Values larger than 1.0 will make the cropped volume lower resolution than the input volume. Values smaller than 1.0 will make the cropped volume higher resolution than the input volume. | SpacingScalingSpinBox | ctkDoubleSpinBox
- Tooltip: The voxel spacing in the output volume will be scaled by this value. Values larger than 1.0 will make the cropped volume lower resolution than the input volume. Values smaller than 1.0 will make the cropped volume higher resolution than the input volume.
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:271: connect(d->SpacingScalingSpinBox, SIGNAL(valueChanged(double)), this, SLOT(onSpacingScalingValueChanged(double)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:658: d->SpacingScalingSpinBox->setValue(1.0);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:700: d->SpacingScalingSpinBox->setValue(d->ParametersNode->GetSpacingScalingConst());`
- Connected slots/functions: `onSpacingScalingValueChanged`
- API footprints: `GetDisplayVisibility`, `GetFillValue`, `GetROINode`, `GetSpacingScalingConst`, `SetSpacingScalingConst`

## widget: IsotropicOutputVoxelLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Isotropic spacing: | IsotropicOutputVoxelLabel | QLabel
- Text: Isotropic spacing:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: IsotropicCheckbox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: IsotropicCheckbox | QCheckBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:272: connect(d->IsotropicCheckbox, SIGNAL(toggled(bool)), this, SLOT(onIsotropicModeChanged(bool)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:657: d->IsotropicCheckbox->setChecked(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:697: d->IsotropicCheckbox->setChecked(d->ParametersNode->GetIsotropicResampling());`
- Connected slots/functions: `onIsotropicModeChanged`
- API footprints: `GetDisplayVisibility`, `GetIsotropicResampling`, `GetROINode`, `SetIsotropicResampling`, `vtkMRMLCropVolumeParametersNode::InterpolationBSpline`
- Key UI properties: {"checked": "false"}

## widget: BSRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: B-spline | High quality, slow | BSRadioButton | QRadioButton
- Text: B-spline
- Tooltip: High quality, slow
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:277: connect(d->BSRadioButton, SIGNAL(toggled(bool)), this, SLOT(onInterpolationModeChanged()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:559: if (d->BSRadioButton->isChecked())`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:695: case vtkMRMLCropVolumeParametersNode::InterpolationBSpline: d->BSRadioButton->setChecked(true); break;`
- Connected slots/functions: `onInterpolationModeChanged`
- API footprints: `GetIsotropicResampling`, `SetInterpolationMode`, `vtkMRMLCropVolumeParametersNode::InterpolationBSpline`, `vtkMRMLCropVolumeParametersNode::InterpolationLinear`, `vtkMRMLCropVolumeParametersNode::InterpolationNearestNeighbor`, `vtkMRMLCropVolumeParametersNode::InterpolationWindowedSinc`

## widget: NNRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Nearest Neighbor | Low quality, fastest | NNRadioButton | QRadioButton
- Text: Nearest Neighbor
- Tooltip: Low quality, fastest
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:275: connect(d->NNRadioButton, SIGNAL(toggled(bool)), this, SLOT(onInterpolationModeChanged()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:547: if (d->NNRadioButton->isChecked())`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:692: case vtkMRMLCropVolumeParametersNode::InterpolationNearestNeighbor: d->NNRadioButton->setChecked(true); break;`
- Connected slots/functions: `onInterpolationModeChanged`
- API footprints: `GetInterpolationMode`, `SetInterpolationMode`, `vtkMRMLCropVolumeParametersNode::InterpolationBSpline`, `vtkMRMLCropVolumeParametersNode::InterpolationLinear`, `vtkMRMLCropVolumeParametersNode::InterpolationNearestNeighbor`, `vtkMRMLCropVolumeParametersNode::InterpolationWindowedSinc`

## widget: LinearRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Linear | Medium quality, medium speed | LinearRadioButton | QRadioButton
- Text: Linear
- Tooltip: Medium quality, medium speed
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:274: connect(d->LinearRadioButton, SIGNAL(toggled(bool)), this, SLOT(onInterpolationModeChanged()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:551: if (d->LinearRadioButton->isChecked())`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:659: d->LinearRadioButton->setChecked(true);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:693: case vtkMRMLCropVolumeParametersNode::InterpolationLinear: d->LinearRadioButton->setChecked(true); break;`
- Connected slots/functions: `onInterpolationModeChanged`
- API footprints: `SetInterpolationMode`, `vtkMRMLCropVolumeParametersNode::InterpolationBSpline`, `vtkMRMLCropVolumeParametersNode::InterpolationLinear`, `vtkMRMLCropVolumeParametersNode::InterpolationNearestNeighbor`, `vtkMRMLCropVolumeParametersNode::InterpolationWindowedSinc`

## widget: WSRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Windowed Sinc | High quality, slow | WSRadioButton | QRadioButton
- Text: Windowed Sinc
- Tooltip: High quality, slow
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:276: connect(d->WSRadioButton, SIGNAL(toggled(bool)), this, SLOT(onInterpolationModeChanged()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:555: if (d->WSRadioButton->isChecked())`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:694: case vtkMRMLCropVolumeParametersNode::InterpolationWindowedSinc: d->WSRadioButton->setChecked(true); break;`
- Connected slots/functions: `onInterpolationModeChanged`
- API footprints: `SetInterpolationMode`, `vtkMRMLCropVolumeParametersNode::InterpolationBSpline`, `vtkMRMLCropVolumeParametersNode::InterpolationLinear`, `vtkMRMLCropVolumeParametersNode::InterpolationNearestNeighbor`, `vtkMRMLCropVolumeParametersNode::InterpolationWindowedSinc`

## widget: VolumeInformationCollapsibleButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Volume information | VolumeInformationCollapsibleButton | ctkCollapsibleButton
- Text: Volume information
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:282: this->connect(d->VolumeInformationCollapsibleButton, SIGNAL(clicked(bool)), SLOT(onVolumeInformationSectionClicked(bool)));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:736: if (d->VolumeInformationCollapsibleButton->collapsed())`
- Connected slots/functions: `onVolumeInformationSectionClicked`

## widget: InputVolumeInfoGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: InputVolumeInfoGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InputDimensionsWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: Output volume dimension after cropping | InputDimensionsWidget | qMRMLCoordinatesWidget
- Tooltip: Output volume dimension after cropping
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:749: d->InputDimensionsWidget->setCoordinates(dimensions[0], dimensions[1], dimensions[2]);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:754: d->InputDimensionsWidget->setCoordinates(0, 0, 0);`
- API footprints: `GetDimensions`, `GetImageData`, `GetSpacing`

## widget: InputSpacingWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: Output volume spacing after cropping | InputSpacingWidget | qMRMLCoordinatesWidget
- Tooltip: Output volume spacing after cropping
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:750: d->InputSpacingWidget->setCoordinates(inputVolumeNode->GetSpacing());`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:755: d->InputSpacingWidget->setCoordinates(0, 0, 0);`
- API footprints: `GetDimensions`, `GetImageData`, `GetSpacing`

## widget: InputDimensionsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Dimensions: | InputDimensionsLabel | QLabel
- Text: Dimensions:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InputSpacingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Spacing: | InputSpacingLabel | QLabel
- Text: Spacing:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: OutputVolumeInfoGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: OutputVolumeInfoGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: CroppedDimensionsWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: Output volume dimension after cropping | CroppedDimensionsWidget | qMRMLCoordinatesWidget
- Tooltip: Output volume dimension after cropping
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:778: d->CroppedDimensionsWidget->setCoordinates(outputExtent[1] - outputExtent[0] + 1, outputExtent[3] - outputExtent[2] + 1, outputExtent[5] - outputExtent[4] + 1);`

## widget: CroppedSpacingWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: Output volume spacing after cropping | CroppedSpacingWidget | qMRMLCoordinatesWidget
- Tooltip: Output volume spacing after cropping
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:779: d->CroppedSpacingWidget->setCoordinates(outputSpacing);`

## widget: CroppedSpacingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Spacing: | CroppedSpacingLabel | QLabel
- Text: Spacing:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: CroppedDimensionsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Dimensions: | CroppedDimensionsLabel | QLabel
- Text: Dimensions:
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`

## widget: InputErrorLabel

- Confidence: `linked_to_code`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: InputErrorLabel | ctkFittedTextBrowser
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:284: d->InputErrorLabel->setVisible(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:633: d->InputErrorLabel->setVisible(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:640: d->InputErrorLabel->setText(inputCheckErrorMessage);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:641: d->InputErrorLabel->setVisible(true);`

## widget: InputErrorFixButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Fix | InputErrorFixButton | QPushButton
- Text: Fix
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:285: d->InputErrorFixButton->setVisible(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:286: connect(d->InputErrorFixButton, SIGNAL(clicked()), this, SLOT(onFixAlignment()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:634: d->InputErrorFixButton->setVisible(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:642: d->InputErrorFixButton->setVisible(autoFixAvailable);`
- Connected slots/functions: `onFixAlignment`

## widget: CropButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Apply | CropButton | QPushButton
- Text: Apply
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:288: connect(d->CropButton, SIGNAL(clicked()), this, SLOT(onApply()));`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:664: d->CropButton->setEnabled(false);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:669: d->CropButton->setEnabled(inputCheckErrorMessage.isEmpty());`
- Connected slots/functions: `onApply`
- API footprints: `Apply`, `GetInputVolumeNode`, `GetOutputVolumeNode`, `GetOutputVolumeNodeID`, `GetPointer`, `GetROINode`, `GetSelectionNode`, `PropagateVolumeSelection`, `SetActiveVolumeID`

## action: ROIFitAlignToVolumeAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Align to volume axes + Resize | Set axes of the ROI box to match the volume axes | ROIFitAlignToVolumeAction
- Text: Align to volume axes + Resize
- Tooltip: Set axes of the ROI box to match the volume axes
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:235: fitROIModeActions->addAction(d->ROIFitAlignToVolumeAction);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:240: d->FitROIModeMapper->setMapping(d->ROIFitAlignToVolumeAction, vtkMRMLCropVolumeParametersNode::FitROIAlignToVolume);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:680: case vtkMRMLCropVolumeParametersNode::FitROIAlignToVolume: d->ROIFitAlignToVolumeAction->setChecked(true); break;`
- API footprints: `GetFitROIMode`, `vtkMRMLCropVolumeParametersNode::FitROIAlignToVolume`, `vtkMRMLCropVolumeParametersNode::FitROIAlignToWorld`, `vtkMRMLCropVolumeParametersNode::FitROIKeepOrientation`
- Key UI properties: {"checkable": "true"}

## action: ROIFitAlignToWorldAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Align to world axes + Resize | Set axes of the ROI box to match the world coordinate system axes | ROIFitAlignToWorldAction
- Text: Align to world axes + Resize
- Tooltip: Set axes of the ROI box to match the world coordinate system axes
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:236: fitROIModeActions->addAction(d->ROIFitAlignToWorldAction);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:241: d->FitROIModeMapper->setMapping(d->ROIFitAlignToWorldAction, vtkMRMLCropVolumeParametersNode::FitROIAlignToWorld);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:681: case vtkMRMLCropVolumeParametersNode::FitROIAlignToWorld: d->ROIFitAlignToWorldAction->setChecked(true); break;`
- API footprints: `vtkMRMLCropVolumeParametersNode::FitROIAlignToVolume`, `vtkMRMLCropVolumeParametersNode::FitROIAlignToWorld`, `vtkMRMLCropVolumeParametersNode::FitROIKeepOrientation`
- Key UI properties: {"checkable": "true"}

## action: ROIFitKeepOrientationAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Resize only | Do not change ROI box orientation | ROIFitKeepOrientationAction
- Text: Resize only
- Tooltip: Do not change ROI box orientation
- Implementation candidates: `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx`, `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:237: fitROIModeActions->addAction(d->ROIFitKeepOrientationAction);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:242: d->FitROIModeMapper->setMapping(d->ROIFitKeepOrientationAction, vtkMRMLCropVolumeParametersNode::FitROIKeepOrientation);`
  - `Modules/Loadable/CropVolume/qSlicerCropVolumeModuleWidget.cxx:682: case vtkMRMLCropVolumeParametersNode::FitROIKeepOrientation: d->ROIFitKeepOrientationAction->setChecked(true); break;`
- API footprints: `vtkMRMLCropVolumeParametersNode::FitROIAlignToVolume`, `vtkMRMLCropVolumeParametersNode::FitROIAlignToWorld`, `vtkMRMLCropVolumeParametersNode::FitROIKeepOrientation`
- Key UI properties: {"checkable": "true"}
