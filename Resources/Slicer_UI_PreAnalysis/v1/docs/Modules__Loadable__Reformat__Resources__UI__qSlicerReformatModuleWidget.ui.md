# Slicer UI Analysis: Modules/Loadable/Reformat/Resources/UI/qSlicerReformatModuleWidget.ui

- Owner class: `qSlicerReformatModuleWidget`
- UI file: `Modules/Loadable/Reformat/Resources/UI/qSlicerReformatModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerReformatModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerReformatModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:31: #include "qSlicerReformatModuleWidget.h"`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:32: #include "ui_qSlicerReformatModuleWidget.h"`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:52: class qSlicerReformatModuleWidgetPrivate : public Ui_qSlicerReformatModuleWidget`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:54: Q_DECLARE_PUBLIC(qSlicerReformatModuleWidget);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:57: qSlicerReformatModuleWidget* const q_ptr;`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:60: qSlicerReformatModuleWidgetPrivate(qSlicerReformatModuleWidget& object);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:90: // qSlicerReformatModuleWidgetPrivate methods`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:93: qSlicerReformatModuleWidgetPrivate::qSlicerReformatModuleWidgetPrivate(qSlicerReformatModuleWidget& object)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:99: this->LastRotationValues[qSlicerReformatModuleWidget::axisX] = 0;`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:100: this->LastRotationValues[qSlicerReformatModuleWidget::axisY] = 0;`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:101: this->LastRotationValues[qSlicerReformatModuleWidget::axisZ] = 0;`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:105: void qSlicerReformatModuleWidgetPrivate::setupReformatOptionsMenu()`
- Connected slots/functions: `currentTextChanged`, `onSliceOrientationChanged`
- API footprints: `SetOrientation`, `vtkMRMLSliceNode::SafeDownCast`

## widget: VisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: Slice: | VisibilityCheckBox | ctkCheckBox
- Text: Slice:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:131: bool wasVisibilityCheckBoxBlocking = this->VisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:133: this->VisibilityCheckBox->setEnabled(this->MRMLSliceNode != nullptr);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:136: this->VisibilityCheckBox->setChecked(visibility);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:138: this->VisibilityCheckBox->blockSignals(wasVisibilityCheckBoxBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:309: this->connect(d->VisibilityCheckBox, SIGNAL(toggled(bool)), this, SLOT(onSliceVisibilityChanged(bool)));`
- Connected slots/functions: `onSliceVisibilityChanged`
- API footprints: `GetSliceVisible`, `SetSliceVisible`

## widget: SliceNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: SliceNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:312: this->connect(d->SliceNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onNodeSelected(vtkMRMLNode*)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:682: d->SliceNodeSelector->setCurrentNode(node);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:694: d->SliceNodeSelector->setCurrentNode(sliceNode);`
- Connected slots/functions: `onNodeSelected`
- API footprints: `GetMRMLApplicationLogic`, `GetSliceLogic`, `vtkMRMLSliceNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSliceNode"]}

## widget: ShowReformatWidgetToolButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Show reformat widget in 3D view | ShowReformatWidgetToolButton | QToolButton
- Tooltip: Show reformat widget in 3D view
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:109: QMenu* reformatMenu = new QMenu(qSlicerReformatModuleWidget::tr("Reformat"), this->ShowReformatWidgetToolButton);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:115: this->ShowReformatWidgetToolButton->setMenu(reformatMenu);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:141: bool wasVisibilityReformatWidgetCheckBoxBlocking = this->ShowReformatWidgetToolButton->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:145: this->ShowReformatWidgetToolButton->setEnabled(this->MRMLSliceNode != nullptr);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:150: this->ShowReformatWidgetToolButton->setChecked(widgetVisibility);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:155: this->ShowReformatWidgetToolButton->blockSignals(wasVisibilityReformatWidgetCheckBoxBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:310: this->connect(d->ShowReformatWidgetToolButton, SIGNAL(toggled(bool)), this, SLOT(onReformatWidgetVisibilityChanged(bool)));`
- Connected slots/functions: `onReformatWidgetVisibilityChanged`
- API footprints: `GetWidgetNormalLockedToCamera`, `GetWidgetVisible`, `SetSliceVisible`, `SetWidgetVisible`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: DisplayEditCollapsibleWidget

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display && Edit | DisplayEditCollapsibleWidget | ctkCollapsibleButton
- Text: Display && Edit
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: OffsetSlidersGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: OffsetSlidersGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:69: void updateOffsetSlidersGroupBox();`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:122: this->updateOffsetSlidersGroupBox();`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:161: void qSlicerReformatModuleWidgetPrivate::updateOffsetSlidersGroupBox()`

## widget: OffsetSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: OffsetSlider | qMRMLLinearTransformSlider
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:69: void updateOffsetSlidersGroupBox();`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:122: this->updateOffsetSlidersGroupBox();`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:161: void qSlicerReformatModuleWidgetPrivate::updateOffsetSlidersGroupBox()`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:168: bool wasBlocking = this->OffsetSlider->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:174: this->OffsetSlider->setSingleStep(offsetResolution);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:175: this->OffsetSlider->setPageStep(offsetResolution);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:182: this->OffsetSlider->setRange(sliceBounds[4], sliceBounds[5]);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:185: this->OffsetSlider->setValue(this->MRMLSliceLogic->GetSliceOffset());`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:186: this->OffsetSlider->blockSignals(wasBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:315: this->connect(d->OffsetSlider, SIGNAL(valueChanged(double)), this, SLOT(setSliceOffsetValue(double)), Qt::QueuedConnection);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:316: this->connect(d->OffsetSlider, SIGNAL(valueIsChanging(double)), this, SLOT(onTrackSliceOffsetValueChanged(double)), Qt::QueuedConnection);`
- Connected slots/functions: `onTrackSliceOffsetValueChanged`, `setSliceOffsetValue`
- API footprints: `EndSliceOffsetInteraction`, `GetLowestVolumeSliceBounds`, `GetSliceOffset`, `SetSliceOffset`, `StartSliceOffsetInteraction`

## widget: MinMaxWidget_2

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: MinMaxWidget_2 | QWidget
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: OriginCoordinatesGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: OriginCoordinatesGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: CoordinateReferenceGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `QGroupBox`
- Search text: CoordinateReferenceGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:324: d->CoordinateReferenceGroupBox->setHidden(true);`

## widget: OnPlaneRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: On Plane | OnPlaneRadioButton | QRadioButton
- Text: On Plane
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:320: d->OriginCoordinateReferenceButtonGroup->addButton(d->OnPlaneRadioButton, qSlicerReformatModuleWidget::ONPLANE);`
- Key UI properties: {"checked": "true"}

## widget: InVolumeRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: In Volume | InVolumeRadioButton | QRadioButton
- Text: In Volume
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:321: d->OriginCoordinateReferenceButtonGroup->addButton(d->InVolumeRadioButton, qSlicerReformatModuleWidget::INVOLUME);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:325: d->InVolumeRadioButton->setChecked(true);`

## widget: OnPlaneGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `QGroupBox`
- Search text: OnPlaneGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:326: d->OnPlaneGroupBox->setHidden(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:447: d->OnPlaneGroupBox->setHidden(ref == qSlicerReformatModuleWidget::INVOLUME);`

## widget: OnPlaneXdoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: OnPlaneXdoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:201: // bool wasOnPlaneXBlocking = this->OnPlaneXdoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:220: this->OnPlaneXdoubleSpinBox->setMinimum(sliceBounds[0]);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:221: this->OnPlaneXdoubleSpinBox->setMaximum(sliceBounds[1]);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:233: // this->OnPlaneXdoubleSpinBox->blockSignals(wasOnPlaneXBlocking);`
- API footprints: `GetLowestVolumeSliceBounds`

## widget: OnPlaneYdoubleSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: OnPlaneYdoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:202: // bool wasOnPlaneYBlocking = this->OnPlaneYdoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:222: this->OnPlaneYdoubleSpinBox->setMinimum(sliceBounds[2]);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:223: this->OnPlaneYdoubleSpinBox->setMaximum(sliceBounds[3]);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:234: // this->OnPlaneYdoubleSpinBox->blockSignals(wasOnPlaneYBlocking);`

## widget: CenterPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Center | CenterPushButton | QPushButton
- Text: Center
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:338: this->connect(d->CenterPushButton, SIGNAL(pressed()), this, SLOT(centerSliceNode()));`
- Connected slots/functions: `centerSliceNode`

## widget: InVolumeCoordinatesWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkCoordinatesWidget`
- Search text: InVolumeCoordinatesWidget | ctkCoordinatesWidget
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:203: bool wasInVolumeBlocking = this->InVolumeCoordinatesWidget->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:212: this->InVolumeCoordinatesWidget->setMinimum(minimum);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:213: this->InVolumeCoordinatesWidget->setMaximum(maximum);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:228: this->InVolumeCoordinatesWidget->setCoordinates(sliceToRAS->GetElement(0, 3), sliceToRAS->GetElement(1, 3), sliceToRAS->GetElement(2, 3));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:235: this->InVolumeCoordinatesWidget->blockSignals(wasInVolumeBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:332: this->connect(d->InVolumeCoordinatesWidget, SIGNAL(coordinatesChanged(double*)), this, SLOT(setWorldPosition(double*)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:448: d->InVolumeCoordinatesWidget->setHidden(ref != qSlicerReformatModuleWidget::INVOLUME);`
- Connected slots/functions: `setWorldPosition`
- API footprints: `GetElement`, `GetSliceToRAS`

## widget: RotationSlidersGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: RotationSlidersGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: RotateZSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: Rotate the slice in the current slice plane, around the slice normal | RotateZSlider | qMRMLLinearTransformSlider
- Tooltip: Rotate the slice in the current slice plane, around the slice normal
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:277: else if (slider == this->RotateZSlider)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:362: this->connect(d->RotateZSlider, SIGNAL(valueChanged(double)), this, SLOT(onSliderRotationChanged(double)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:580: d->resetSlider(d->RotateZSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:602: d->resetSlider(d->RotateZSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:616: d->resetSlider(d->RotateZSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:628: d->resetSlider(d->RotateZSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:636: else if (this->sender() == d->RotateZSlider)`
- Connected slots/functions: `onSliderRotationChanged`
- API footprints: `SetOrientation`

## widget: PALabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Vertical: | PALabel | QLabel
- Text: Vertical:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: ISLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: In-Plane: | ISLabel | QLabel
- Text: In-Plane:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: NormalToLRPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Normal to LR | NormalToLRPushButton | QPushButton
- Text: Normal to LR
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:352: this->connect(d->NormalToLRPushButton, SIGNAL(pressed()), this, SLOT(setNormalToAxisLR()));`
- Connected slots/functions: `setNormalToAxisLR`

## widget: NormalToPAPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Normal to PA | NormalToPAPushButton | QPushButton
- Text: Normal to PA
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:353: this->connect(d->NormalToPAPushButton, SIGNAL(pressed()), this, SLOT(setNormalToAxisPA()));`
- Connected slots/functions: `setNormalToAxisPA`

## widget: NormalToISPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Normal to IS | NormalToISPushButton | QPushButton
- Text: Normal to IS
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:354: this->connect(d->NormalToISPushButton, SIGNAL(pressed()), this, SLOT(setNormalToAxisIS()));`
- Connected slots/functions: `setNormalToAxisIS`

## widget: RotateToVolumePlanePushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Rotate to volume plane | Rotate the slice view to be aligned with the axes of the displayed volume | RotateToVolumePlanePushButton | QPushButton
- Text: Rotate to volume plane
- Tooltip: Rotate the slice view to be aligned with the axes of the displayed volume
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:343: this->connect(d->RotateToVolumePlanePushButton, SIGNAL(pressed()), this, SLOT(rotateToVolumePlane()));`
- Connected slots/functions: `rotateToVolumePlane`
- API footprints: `EndSliceNodeInteraction`, `RotateSliceToLowestVolumeAxes`, `StartSliceNodeInteraction`, `vtkMRMLSliceNode::RotateToBackgroundVolumePlaneFlag`

## widget: Normal_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Rotation: | Normal_2 | QLabel
- Text: Rotation:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: RotateYSlider

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: Rotate around the slice vertical axis | RotateYSlider | qMRMLLinearTransformSlider
- Tooltip: Rotate around the slice vertical axis
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:273: else if (slider == this->RotateYSlider)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:361: this->connect(d->RotateYSlider, SIGNAL(valueChanged(double)), this, SLOT(onSliderRotationChanged(double)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:579: d->resetSlider(d->RotateYSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:601: d->resetSlider(d->RotateYSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:615: d->resetSlider(d->RotateYSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:624: else if (this->sender() == d->RotateYSlider)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:640: d->resetSlider(d->RotateYSlider);`
- Connected slots/functions: `onSliderRotationChanged`

## widget: RotateXSlider

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLLinearTransformSlider`
- Search text: Rotate around the slice horizontal axis | RotateXSlider | qMRMLLinearTransformSlider
- Tooltip: Rotate around the slice horizontal axis
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:269: if (slider == this->RotateXSlider)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:360: this->connect(d->RotateXSlider, SIGNAL(valueChanged(double)), this, SLOT(onSliderRotationChanged(double)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:578: d->resetSlider(d->RotateXSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:600: d->resetSlider(d->RotateXSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:612: if (this->sender() == d->RotateXSlider)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:627: d->resetSlider(d->RotateXSlider);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:639: d->resetSlider(d->RotateXSlider);`
- Connected slots/functions: `onSliderRotationChanged`

## widget: Resetlabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Reset to: | Resetlabel | QLabel
- Text: Reset to:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: Normal

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Normal: | Normal | QLabel
- Text: Normal:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:111: reformatMenu->addAction(this->actionLockNormalToCamera);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:113: QObject::connect(this->actionLockNormalToCamera, SIGNAL(triggered(bool)), q, SLOT(onLockReformatWidgetToCamera(bool)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:142: bool wasLockReformatWidgetCheckBoxBlocking = this->actionLockNormalToCamera->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:143: bool wasLockReformatWidgetCheckBoxButtonBlocking = this->NormalToCameraCheckablePushButton->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:148: int lockWidgetNormal = (this->MRMLSliceNode) ? this->MRMLSliceNode->GetWidgetNormalLockedToCamera() : 0;`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:151: this->actionLockNormalToCamera->setChecked(lockWidgetNormal);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:152: this->NormalToCameraCheckablePushButton->setChecked(lockWidgetNormal);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:153: this->NormalToCameraCheckablePushButton->setCheckState((lockWidgetNormal) ? Qt::Checked : Qt::Unchecked);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:156: this->actionLockNormalToCamera->blockSignals(wasLockReformatWidgetCheckBoxBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:157: this->NormalToCameraCheckablePushButton->blockSignals(wasLockReformatWidgetCheckBoxButtonBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:250: bool wasNormalBlocking = this->NormalCoordinatesWidget->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:259: this->NormalCoordinatesWidget->setCoordinates(normal);`
- Connected slots/functions: `onLockReformatWidgetToCamera`, `setNormalToAxisIS`, `setNormalToAxisLR`, `setNormalToAxisPA`, `setNormalToCamera`, `setSliceNormal`
- API footprints: `GetCamera`, `GetElement`, `GetFirstNodeByClass`, `GetMRMLScene`, `GetViewPlaneNormal`, `GetWidgetNormalLockedToCamera`, `GetWidgetVisible`, `SetWidgetNormalLockedToCamera`, `SetWidgetVisible`, `vtkMRMLCameraNode::SafeDownCast`

## widget: LRLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Horizontal: | LRLabel | QLabel
- Text: Horizontal:
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: MinMaxWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: MinMaxWidget | QWidget
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`

## widget: SliceOrientationSelector

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: Slice orientation (Axial, Sagittal, Coronal, Reformat). | SliceOrientationSelector | ctkComboBox
- Tooltip: Slice orientation (Axial, Sagittal, Coronal, Reformat).
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:27: #include "qMRMLSliceControllerWidget_p.h" // For updateSliceOrientationSelector`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:243: this->SliceOrientationSelector->setCurrentIndex(-1);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:247: qMRMLSliceControllerWidgetPrivate::updateSliceOrientationSelector(this->MRMLSliceNode, this->SliceOrientationSelector);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:335: this->connect(d->SliceOrientationSelector, &QComboBox::currentTextChanged, this, &qSlicerReformatModuleWidget::onSliceOrientationChanged);`
- Connected slots/functions: `currentTextChanged`, `onSliceOrientationChanged`
- API footprints: `SetOrientation`

## widget: NormalToCameraCheckablePushButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckablePushButton`
- Search text: Normal to Camera | NormalToCameraCheckablePushButton | ctkCheckablePushButton
- Text: Normal to Camera
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:143: bool wasLockReformatWidgetCheckBoxButtonBlocking = this->NormalToCameraCheckablePushButton->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:152: this->NormalToCameraCheckablePushButton->setChecked(lockWidgetNormal);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:153: this->NormalToCameraCheckablePushButton->setCheckState((lockWidgetNormal) ? Qt::Checked : Qt::Unchecked);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:157: this->NormalToCameraCheckablePushButton->blockSignals(wasLockReformatWidgetCheckBoxButtonBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:356: QObject::connect(d->NormalToCameraCheckablePushButton, SIGNAL(clicked()), this, SLOT(setNormalToCamera()));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:357: QObject::connect(d->NormalToCameraCheckablePushButton, SIGNAL(checkBoxToggled(bool)), this, SLOT(onLockReformatWidgetToCamera(bool)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:525: if (d->NormalToCameraCheckablePushButton->checkState() == Qt::Checked)`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:527: d->NormalToCameraCheckablePushButton->setCheckState(Qt::Unchecked);`
- Connected slots/functions: `onLockReformatWidgetToCamera`, `setNormalToCamera`
- API footprints: `GetCamera`, `GetFirstNodeByClass`, `GetMRMLScene`, `GetViewPlaneNormal`, `SetWidgetNormalLockedToCamera`, `SetWidgetVisible`, `vtkMRMLCameraNode::SafeDownCast`
- Key UI properties: {"checkable": "false", "checked": "false"}

## widget: NormalCoordinatesWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkCoordinatesWidget`
- Search text: NormalCoordinatesWidget | ctkCoordinatesWidget
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:250: bool wasNormalBlocking = this->NormalCoordinatesWidget->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:259: this->NormalCoordinatesWidget->setCoordinates(normal);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:260: this->NormalCoordinatesWidget->blockSignals(wasNormalBlocking);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:341: this->connect(d->NormalCoordinatesWidget, SIGNAL(coordinatesChanged(double*)), this, SLOT(setSliceNormal(double*)));`
- Connected slots/functions: `setSliceNormal`
- API footprints: `GetElement`

## widget: FlipHorizontalPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Flip H | Flip slice view horizontally (left-right) | FlipHorizontalPushButton | QPushButton
- Text: Flip H
- Tooltip: Flip slice view horizontally (left-right)
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:346: this->connect(d->FlipHorizontalPushButton, SIGNAL(pressed()), this, SLOT(flipHorizontal()));`
- Connected slots/functions: `flipHorizontal`

## widget: FlipVerticalPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Flip V | Flip slice view vertically (upside-down) | FlipVerticalPushButton | QPushButton
- Text: Flip V
- Tooltip: Flip slice view vertically (upside-down)
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:347: this->connect(d->FlipVerticalPushButton, SIGNAL(pressed()), this, SLOT(flipVertical()));`
- Connected slots/functions: `flipVertical`

## widget: RotateClockwisePushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Rotate CW | Rotate slice view clockwise by 90 degrees | RotateClockwisePushButton | QPushButton
- Text: Rotate CW
- Tooltip: Rotate slice view clockwise by 90 degrees
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:348: this->connect(d->RotateClockwisePushButton, SIGNAL(pressed()), this, SLOT(rotateClockwise()));`
- Connected slots/functions: `rotateClockwise`

## widget: RotateCounterClockwisePushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Rotate CCW | Rotate slice view counterclockwise by 90 degrees | RotateCounterClockwisePushButton | QPushButton
- Text: Rotate CCW
- Tooltip: Rotate slice view counterclockwise by 90 degrees
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:349: this->connect(d->RotateCounterClockwisePushButton, SIGNAL(pressed()), this, SLOT(rotateCounterClockwise()));`
- Connected slots/functions: `rotateCounterClockwise`

## action: actionLockNormalToCamera

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Lock Normal To Camera | Lock reformat widget's normal to the camera one.  | actionLockNormalToCamera
- Text: Lock Normal To Camera
- Tooltip: Lock reformat widget's normal to the camera one. 
- Implementation candidates: `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx`, `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:111: reformatMenu->addAction(this->actionLockNormalToCamera);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:113: QObject::connect(this->actionLockNormalToCamera, SIGNAL(triggered(bool)), q, SLOT(onLockReformatWidgetToCamera(bool)));`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:142: bool wasLockReformatWidgetCheckBoxBlocking = this->actionLockNormalToCamera->blockSignals(true);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:151: this->actionLockNormalToCamera->setChecked(lockWidgetNormal);`
  - `Modules/Loadable/Reformat/qSlicerReformatModuleWidget.cxx:156: this->actionLockNormalToCamera->blockSignals(wasLockReformatWidgetCheckBoxBlocking);`
- Connected slots/functions: `onLockReformatWidgetToCamera`
- API footprints: `SetWidgetNormalLockedToCamera`, `SetWidgetVisible`
- Key UI properties: {"checkable": "true"}
