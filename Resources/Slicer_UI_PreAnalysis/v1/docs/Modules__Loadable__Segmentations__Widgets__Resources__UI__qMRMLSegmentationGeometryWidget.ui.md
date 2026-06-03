# Slicer UI Analysis: Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationGeometryWidget.ui

- Owner class: `qMRMLSegmentationGeometryWidget`
- UI file: `Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationGeometryWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentationGeometryWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSegmentationGeometryWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:23: #include "qMRMLSegmentationGeometryWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:25: #include "ui_qMRMLSegmentationGeometryWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:55: class qMRMLSegmentationGeometryWidgetPrivate : public Ui_qMRMLSegmentationGeometryWidget`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:57: Q_DECLARE_PUBLIC(qMRMLSegmentationGeometryWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:60: qMRMLSegmentationGeometryWidget* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:63: qMRMLSegmentationGeometryWidgetPrivate(qMRMLSegmentationGeometryWidget& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:64: virtual ~qMRMLSegmentationGeometryWidgetPrivate();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:82: qMRMLSegmentationGeometryWidgetPrivate::qMRMLSegmentationGeometryWidgetPrivate(qMRMLSegmentationGeometryWidget& object)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:91: qMRMLSegmentationGeometryWidgetPrivate::~qMRMLSegmentationGeometryWidgetPrivate()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:101: void qMRMLSegmentationGeometryWidgetPrivate::init()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:103: Q_Q(qMRMLSegmentationGeometryWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:117: void qMRMLSegmentationGeometryWidgetPrivate::updateGeometryWidgets()`
- API footprints: `GetID`, `GetOutputGeometryImageData`, `GetPointer`, `GetScene`, `ResampleLabelmapsInSegmentationNode`, `SetIsotropicSpacing`, `SetOversamplingFactor`, `SetPadOutputGeometry`, `SetSourceGeometryNode`, `SetUserSpacing`, `vtkMRMLDisplayableNode::SafeDownCast`

## widget: frame_SourceGeometry

- Confidence: `linked_to_api`
- Widget/action class: `QFrame`
- Search text: frame_SourceGeometry | QFrame
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:396: d->frame_SourceGeometry->setVisible(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:414: d->frame_SourceGeometry->setVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:418: d->frame_SourceGeometry->setVisible(false);`
- API footprints: `GetPointer`

## widget: label_SourceGeometryNode

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Source geometry: | label_SourceGeometryNode | QLabel
- Text: Source geometry:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: MRMLNodeComboBox_SourceGeometryNode

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_SourceGeometryNode | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:107: QObject::connect(this->MRMLNodeComboBox_SourceGeometryNode, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onSourceNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:248: return d->MRMLNodeComboBox_SourceGeometryNode->currentNode();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:263: d->MRMLNodeComboBox_SourceGeometryNode->setCurrentNode(sourceNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:406: vtkMRMLTransformableNode* sourceNode = vtkMRMLTransformableNode::SafeDownCast(d->MRMLNodeComboBox_SourceGeometryNode->currentNode());`
- Connected slots/functions: `onSourceNodeChanged`
- API footprints: `GetSourceAxisIndexForInputAxis`, `GetUserSpacing`, `SetSourceGeometryNode`, `vtkMRMLDisplayableNode::SafeDownCast`, `vtkMRMLScalarVolumeNode::SafeDownCast`, `vtkMRMLTransformableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode", "vtkMRMLSegmentationNode", "vtkMRMLModelNode", "vtkMRMLMarkupsROINode"]}

## widget: groupBox_VolumeSpacingOptions

- Confidence: `linked_to_api`
- Widget/action class: `QGroupBox`
- Search text: groupBox_VolumeSpacingOptions | QGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:397: d->groupBox_VolumeSpacingOptions->setVisible(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:423: d->groupBox_VolumeSpacingOptions->setVisible(sourceNode != nullptr && sourceIsVolume);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:430: d->groupBox_VolumeSpacingOptions->setVisible(false);`
- API footprints: `GetConversionParameter`, `GetSegmentation`

## widget: label_OversamplingFactor

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Oversampling factor: | Split each voxel of the volume to this many voxels along each direction. Useful when increasing the resolution is needed | label_OversamplingFactor | QLabel
- Text: Oversampling factor:
- Tooltip: Split each voxel of the volume to this many voxels along each direction. Useful when increasing the resolution is needed
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: DoubleSpinBox_OversamplingFactor

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Split each voxel of the volume to this many voxels along each direction. Useful when increasing the resolution is needed | DoubleSpinBox_OversamplingFactor | ctkDoubleSpinBox
- Tooltip: Split each voxel of the volume to this many voxels along each direction. Useful when increasing the resolution is needed
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:108: QObject::connect(this->DoubleSpinBox_OversamplingFactor, SIGNAL(valueChanged(double)), q, SLOT(onOversamplingFactorChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:329: return d->DoubleSpinBox_OversamplingFactor->value();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:336: d->DoubleSpinBox_OversamplingFactor->setValue(aOversamplingFactor);`
- Connected slots/functions: `onOversamplingFactorChanged`
- API footprints: `SetOversamplingFactor`

## widget: label_IsotropicSpacing

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Isotropic spacing: | Resample the volume to have isotropic spacing, which means the voxels will be cubes. Use smallest spacing. Useful if the volume has elongated voxels. | label_IsotropicSpacing | QLabel
- Text: Isotropic spacing:
- Tooltip: Resample the volume to have isotropic spacing, which means the voxels will be cubes. Use smallest spacing. Useful if the volume has elongated voxels.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: checkBox_IsotropicSpacing

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Resample the volume to have isotropic spacing, which means the voxels will be cubes. Use smallest spacing. Useful if the volume has elongated voxels. | checkBox_IsotropicSpacing | QCheckBox
- Tooltip: Resample the volume to have isotropic spacing, which means the voxels will be cubes. Use smallest spacing. Useful if the volume has elongated voxels.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:109: QObject::connect(this->checkBox_IsotropicSpacing, SIGNAL(toggled(bool)), q, SLOT(onIsotropicSpacingChanged(bool)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:343: return d->checkBox_IsotropicSpacing->isChecked();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:350: d->checkBox_IsotropicSpacing->setChecked(aIsotropicSpacing);`
- Connected slots/functions: `onIsotropicSpacingChanged`
- API footprints: `SetIsotropicSpacing`

## widget: groupBox_SegmentationLabelmapGeometry

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_SegmentationLabelmapGeometry | QGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: label_Origin

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Origin: | label_Origin | QLabel
- Text: Origin:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: MRMLCoordinatesWidget_Spacing

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: MRMLCoordinatesWidget_Spacing | qMRMLCoordinatesWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:110: QObject::connect(this->MRMLCoordinatesWidget_Spacing, SIGNAL(coordinatesChanged(double*)), q, SLOT(onUserSpacingChanged(double*)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:140: bool blocked = this->MRMLCoordinatesWidget_Spacing->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:141: this->MRMLCoordinatesWidget_Spacing->setCoordinates(outputSpacing);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:142: this->MRMLCoordinatesWidget_Spacing->blockSignals(blocked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:284: bool wasBlocked = d->MRMLCoordinatesWidget_Spacing->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:285: d->MRMLCoordinatesWidget_Spacing->setCoordinates(outputSpacing);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:286: d->MRMLCoordinatesWidget_Spacing->blockSignals(wasBlocked);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:357: d->MRMLCoordinatesWidget_Spacing->setCoordinates(aSpacing);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:398: d->MRMLCoordinatesWidget_Spacing->setEnabled(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:425: d->MRMLCoordinatesWidget_Spacing->setEnabled(sourceNode != nullptr && !sourceIsVolume && d->EditEnabled);`
- Connected slots/functions: `onUserSpacingChanged`
- API footprints: `GetUserSpacing`, `SetUserSpacing`

## widget: MatrixWidget_Directions

- Confidence: `linked_to_api`
- Widget/action class: `ctkMatrixWidget`
- Search text: MatrixWidget_Directions | ctkMatrixWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:154: this->MatrixWidget_Directions->setValue(i, j, directions->GetElement(i, j));`
- API footprints: `GetElement`

## widget: label_Directions

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Directions: | label_Directions | QLabel
- Text: Directions:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: label_Error

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Error message | label_Error | QLabel
- Text: Error message
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:392: d->label_Error->setVisible(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:399: d->label_Error->setText(tr("No segmentation node specified!"));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:400: d->label_Error->setVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:445: d->label_Error->setText(errorMessage.c_str());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:446: d->label_Error->setVisible(true);`
- API footprints: `GetPointer`

## widget: label_Spacing

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Spacing: | label_Spacing | QLabel
- Text: Spacing:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: label_Dimensions

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Dimensions: | label_Dimensions | QLabel
- Text: Dimensions:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: MRMLCoordinatesWidget_Origin

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: MRMLCoordinatesWidget_Origin | qMRMLCoordinatesWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:146: this->MRMLCoordinatesWidget_Origin->setCoordinates(origin);`
- API footprints: `GetOrigin`

## widget: MRMLCoordinatesWidget_Dimensions

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: MRMLCoordinatesWidget_Dimensions | qMRMLCoordinatesWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:131: this->MRMLCoordinatesWidget_Dimensions->setCoordinates(dimsDouble);`
- API footprints: `GetDimensions`

## widget: groupBox_AdditionalOptions

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_AdditionalOptions | QGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Pad output: | label | QLabel
- Text: Pad output:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:392: d->label_Error->setVisible(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:399: d->label_Error->setText(tr("No segmentation node specified!"));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:400: d->label_Error->setVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:427: // If no source node is selected, then show the current labelmap geometry`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:445: d->label_Error->setText(errorMessage.c_str());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:446: d->label_Error->setVisible(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h:85: /// Resample existing labelmaps in segmentation node with specified geometry`
- API footprints: `GetPointer`

## widget: CheckBox_PadSegmentation

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: CheckBox_PadSegmentation | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:111: QObject::connect(this->CheckBox_PadSegmentation, SIGNAL(toggled(bool)), q, SLOT(onPadSegmentationChanged(bool)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:158: this->CheckBox_PadSegmentation->setIcon(QIcon());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:159: this->CheckBox_PadSegmentation->setText("");`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:168: this->CheckBox_PadSegmentation->setIcon(warningIcon);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:169: this->CheckBox_PadSegmentation->setText(qMRMLSegmentationGeometryWidget::tr("The current segmentation may not fit into the new geometry."));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:364: return d->CheckBox_PadSegmentation->isChecked();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationGeometryWidget.cxx:371: d->CheckBox_PadSegmentation->setChecked(aPadSegmentation);`
- Connected slots/functions: `onPadSegmentationChanged`
- API footprints: `GetPadOutputGeometry`, `GetPointer`, `GetSegmentation`, `SetPadOutputGeometry`
- Key UI properties: {"checked": "false"}
