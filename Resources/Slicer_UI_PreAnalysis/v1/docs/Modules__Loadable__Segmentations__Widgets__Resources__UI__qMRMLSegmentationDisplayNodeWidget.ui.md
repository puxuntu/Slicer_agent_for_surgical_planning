# Slicer UI Analysis: Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationDisplayNodeWidget.ui

- Owner class: `qMRMLSegmentationDisplayNodeWidget`
- UI file: `Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationDisplayNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentationDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSegmentationDisplayNodeWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:24: #include "qMRMLSegmentationDisplayNodeWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:26: #include "ui_qMRMLSegmentationDisplayNodeWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:47: class qMRMLSegmentationDisplayNodeWidgetPrivate : public Ui_qMRMLSegmentationDisplayNodeWidget`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:49: Q_DECLARE_PUBLIC(qMRMLSegmentationDisplayNodeWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:52: qMRMLSegmentationDisplayNodeWidget* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:55: qMRMLSegmentationDisplayNodeWidgetPrivate(qMRMLSegmentationDisplayNodeWidget& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:73: qMRMLSegmentationDisplayNodeWidgetPrivate::qMRMLSegmentationDisplayNodeWidgetPrivate(qMRMLSegmentationDisplayNodeWidget& object)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:82: void qMRMLSegmentationDisplayNodeWidgetPrivate::init()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:84: Q_Q(qMRMLSegmentationDisplayNodeWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:96: &qMRMLSegmentationDisplayNodeWidget::onVisibilityChanged);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:107: &qMRMLSegmentationDisplayNodeWidget::onVisibilitySliceFillChanged);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:111: &qMRMLSegmentationDisplayNodeWidget::onVisibilitySliceOutlineChanged);`
- Connected slots/functions: `onSegmentVisibility3DChanged`, `onSegmentVisibilitySliceFillChanged`, `onSegmentVisibilitySliceOutlineChanged`, `onVisibility3DChanged`, `onVisibilityChanged`, `onVisibilitySliceFillChanged`, `onVisibilitySliceOutlineChanged`, `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox_Clip.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> SlicerWidget_ClipNodeDisplayProperties.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> SlicerWidget_ClipNodeProperties.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetDisplayNode`, `GetID`, `GetPointer`, `SetSegmentVisibility2DFill`, `SetSegmentVisibility2DOutline`, `SetSegmentVisibility3D`, `SetVisibility`, `SetVisibility2DFill`, `SetVisibility2DOutline`, `SetVisibility3D`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`

## widget: SliderWidget_Opacity

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SliderWidget_Opacity | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:100: QObject::connect(this->SliderWidget_Opacity, SIGNAL(valueChanged(double)), q, SLOT(onOpacityChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:122: QObject::connect(this->SliderWidget_OpacitySliceFill, SIGNAL(valueChanged(double)), q, SLOT(onOpacitySliceFillChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:123: QObject::connect(this->SliderWidget_OpacitySliceOutline, SIGNAL(valueChanged(double)), q, SLOT(onOpacitySliceOutlineChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:124: QObject::connect(this->SliderWidget_Opacity3D, SIGNAL(valueChanged(double)), q, SLOT(onOpacity3DChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:151: QObject::connect(this->SliderWidget_OpacitySliceFill_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacitySliceFillChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:152: QObject::connect(this->SliderWidget_OpacitySliceOutline_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacitySliceOutlineChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:153: QObject::connect(this->SliderWidget_Opacity3D_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacity3DChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:272: d->SliderWidget_OpacitySliceFill_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:273: d->SliderWidget_OpacitySliceFill_SelectedSegment->setValue(properties.Opacity2DFill);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:274: d->SliderWidget_OpacitySliceFill_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:276: d->SliderWidget_OpacitySliceOutline_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:277: d->SliderWidget_OpacitySliceOutline_SelectedSegment->setValue(properties.Opacity2DOutline);`
- Connected slots/functions: `onOpacity3DChanged`, `onOpacityChanged`, `onOpacitySliceFillChanged`, `onOpacitySliceOutlineChanged`, `onSegmentOpacity3DChanged`, `onSegmentOpacitySliceFillChanged`, `onSegmentOpacitySliceOutlineChanged`
- API footprints: `GetOpacity`, `GetOpacity2DFill`, `GetOpacity2DOutline`, `GetOpacity3D`, `GetPointer`, `GetVisibility`, `SetOpacity`, `SetOpacity2DFill`, `SetOpacity2DOutline`, `SetOpacity3D`, `SetSegmentOpacity2DFill`, `SetSegmentOpacity2DOutline`, `SetSegmentOpacity3D`

## widget: label_OverallOpacity

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Overall opacity: | label_OverallOpacity | QLabel
- Text: Overall opacity:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: CollapsibleGroupBox_Advanced

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_Advanced | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Key UI properties: {"checked": "false"}

## widget: label_Views

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Views: | label_Views | QLabel
- Text: Views:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: comboBox_DisplayedRepresentation3D

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Representation that is shown in 3D (models only) | comboBox_DisplayedRepresentation3D | QComboBox
- Tooltip: Representation that is shown in 3D (models only)
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:128: QObject::connect(this->comboBox_DisplayedRepresentation3D, SIGNAL(currentIndexChanged(int)), q, SLOT(onRepresentation3DChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:370: d->comboBox_DisplayedRepresentation3D->setCurrentIndex(d->comboBox_DisplayedRepresentation3D->findText(displayRepresentation3D.c_str()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:418: d->comboBox_DisplayedRepresentation3D->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:419: d->comboBox_DisplayedRepresentation3D->clear();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:426: d->comboBox_DisplayedRepresentation3D->addItem(reprIt->c_str());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:430: d->comboBox_DisplayedRepresentation3D->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:436: d->comboBox_DisplayedRepresentation3D->setCurrentIndex(d->comboBox_DisplayedRepresentation3D->findText(displayRepresentation3D.c_str()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:607: QString representationName = d->comboBox_DisplayedRepresentation3D->itemText(index);`
- Connected slots/functions: `onRepresentation3DChanged`
- API footprints: `GetDisplayRepresentationName2D`, `GetPointer`, `SetPreferredDisplayRepresentationName3D`

## widget: label_Representation2D

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Representation in 2D views: | label_Representation2D | QLabel
- Text: Representation in 2D views:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: label_SliceIntersectionThickness

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice intersection thickness: | label_SliceIntersectionThickness | QLabel
- Text: Slice intersection thickness:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: groupBox_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `QGroupBox`
- Search text: groupBox_SelectedSegment | QGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:253: d->groupBox_SelectedSegment->setEnabled(segmentSelected);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:256: d->groupBox_SelectedSegment->setTitle(tr("Selected segment: none"));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:298: d->groupBox_SelectedSegment->setTitle(newTitle);`
- API footprints: `GetName`

## widget: label_SliceOutline_SelectedSegment

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice outline: | label_SliceOutline_SelectedSegment | QLabel
- Text: Slice outline:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: checkBox_VisibilitySliceFill_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_VisibilitySliceFill_SelectedSegment | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:133: QObject::connect(this->checkBox_VisibilitySliceFill_SelectedSegment, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:146: QObject::connect(this->checkBox_VisibilitySliceFill_SelectedSegment, SIGNAL(stateChanged(int)), q, SLOT(onSegmentVisibilitySliceFillChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:260: d->checkBox_VisibilitySliceFill_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:261: d->checkBox_VisibilitySliceFill_SelectedSegment->setChecked(properties.Visible2DFill);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:262: d->checkBox_VisibilitySliceFill_SelectedSegment->blockSignals(false);`
- Connected slots/functions: `onSegmentVisibilitySliceFillChanged`
- API footprints: `GetPointer`, `SetSegmentVisibility2DFill`

## widget: label_SliceFill_SelectedSegment

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice fill: | label_SliceFill_SelectedSegment | QLabel
- Text: Slice fill:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: checkBox_VisibilitySliceOutline_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_VisibilitySliceOutline_SelectedSegment | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:137: QObject::connect(this->checkBox_VisibilitySliceOutline_SelectedSegment, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:147: QObject::connect(this->checkBox_VisibilitySliceOutline_SelectedSegment, SIGNAL(stateChanged(int)), q, SLOT(onSegmentVisibilitySliceOutlineChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:264: d->checkBox_VisibilitySliceOutline_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:265: d->checkBox_VisibilitySliceOutline_SelectedSegment->setChecked(properties.Visible2DOutline);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:266: d->checkBox_VisibilitySliceOutline_SelectedSegment->blockSignals(false);`
- Connected slots/functions: `onSegmentVisibilitySliceOutlineChanged`
- API footprints: `GetPointer`, `SetSegmentVisibility2DOutline`

## widget: label_Visibility_SelectedSegment

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility | label_Visibility_SelectedSegment | QLabel
- Text: Visibility
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: checkBox_Visibility3D_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_Visibility3D_SelectedSegment | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:141: QObject::connect(this->checkBox_Visibility3D_SelectedSegment, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:148: QObject::connect(this->checkBox_Visibility3D_SelectedSegment, SIGNAL(stateChanged(int)), q, SLOT(onSegmentVisibility3DChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:268: d->checkBox_Visibility3D_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:269: d->checkBox_Visibility3D_SelectedSegment->setChecked(properties.Visible3D);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:270: d->checkBox_Visibility3D_SelectedSegment->blockSignals(false);`
- Connected slots/functions: `onSegmentVisibility3DChanged`
- API footprints: `GetPointer`, `SetSegmentVisibility3D`

## widget: label_3D_SelectedSegment

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: 3D: | label_3D_SelectedSegment | QLabel
- Text: 3D:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: SliderWidget_OpacitySliceFill_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Value relative to other segments. The final opacity depends both on the per-segment opacity and the overall opacity (above) | SliderWidget_OpacitySliceFill_SelectedSegment | ctkSliderWidget
- Tooltip: Value relative to other segments. The final opacity depends both on the per-segment opacity and the overall opacity (above)
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:151: QObject::connect(this->SliderWidget_OpacitySliceFill_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacitySliceFillChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:272: d->SliderWidget_OpacitySliceFill_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:273: d->SliderWidget_OpacitySliceFill_SelectedSegment->setValue(properties.Opacity2DFill);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:274: d->SliderWidget_OpacitySliceFill_SelectedSegment->blockSignals(false);`
- Connected slots/functions: `onSegmentOpacitySliceFillChanged`
- API footprints: `GetPointer`, `SetSegmentOpacity2DFill`

## widget: SliderWidget_OpacitySliceOutline_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Value relative to other segments. The final opacity depends both on the per-segment opacity and the overall opacity (above) | SliderWidget_OpacitySliceOutline_SelectedSegment | ctkSliderWidget
- Tooltip: Value relative to other segments. The final opacity depends both on the per-segment opacity and the overall opacity (above)
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:152: QObject::connect(this->SliderWidget_OpacitySliceOutline_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacitySliceOutlineChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:276: d->SliderWidget_OpacitySliceOutline_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:277: d->SliderWidget_OpacitySliceOutline_SelectedSegment->setValue(properties.Opacity2DOutline);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:278: d->SliderWidget_OpacitySliceOutline_SelectedSegment->blockSignals(false);`
- Connected slots/functions: `onSegmentOpacitySliceOutlineChanged`
- API footprints: `GetPointer`, `SetSegmentOpacity2DOutline`

## widget: SliderWidget_Opacity3D_SelectedSegment

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Value relative to other segments. The final opacity depends both on the per-segment opacity and the overall opacity (above) | SliderWidget_Opacity3D_SelectedSegment | ctkSliderWidget
- Tooltip: Value relative to other segments. The final opacity depends both on the per-segment opacity and the overall opacity (above)
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:153: QObject::connect(this->SliderWidget_Opacity3D_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacity3DChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:280: d->SliderWidget_Opacity3D_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:281: d->SliderWidget_Opacity3D_SelectedSegment->setValue(properties.Opacity3D);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:282: d->SliderWidget_Opacity3D_SelectedSegment->blockSignals(false);`
- Connected slots/functions: `onSegmentOpacity3DChanged`
- API footprints: `GetPointer`, `SetSegmentOpacity3D`

## widget: label_Opacity_SelectedSegment

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity | label_Opacity_SelectedSegment | QLabel
- Text: Opacity
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: label_Representation3D

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Representation in 3D views: | Representation that is shown as a model in 3D and as slice intersections in 2D if exists | label_Representation3D | QLabel
- Text: Representation in 3D views:
- Tooltip: Representation that is shown as a model in 3D and as slice intersections in 2D if exists
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: comboBox_DisplayedRepresentation2D

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Representation that is shown in the 2D slice views | comboBox_DisplayedRepresentation2D | QComboBox
- Tooltip: Representation that is shown in the 2D slice views
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:129: QObject::connect(this->comboBox_DisplayedRepresentation2D, SIGNAL(currentIndexChanged(int)), q, SLOT(onRepresentation2DChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:375: d->comboBox_DisplayedRepresentation2D->setCurrentIndex(d->comboBox_DisplayedRepresentation2D->findText(displayRepresentation2D.c_str()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:450: d->comboBox_DisplayedRepresentation2D->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:451: d->comboBox_DisplayedRepresentation2D->clear();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:456: d->comboBox_DisplayedRepresentation2D->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:465: d->comboBox_DisplayedRepresentation2D->addItem(reprIt->c_str());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:469: d->comboBox_DisplayedRepresentation2D->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:475: d->comboBox_DisplayedRepresentation2D->setCurrentIndex(d->comboBox_DisplayedRepresentation2D->findText(displayRepresentation2D.c_str()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:623: QString representationName = d->comboBox_DisplayedRepresentation2D->itemText(index);`
- Connected slots/functions: `onRepresentation2DChanged`
- API footprints: `GetDisplayableNode`, `GetPointer`, `SetPreferredDisplayRepresentationName2D`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: DisplayNodeViewComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLDisplayNodeViewComboBox`
- Search text: DisplayNodeViewComboBox | qMRMLDisplayNodeViewComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:379: d->DisplayNodeViewComboBox->setMRMLDisplayNode(d->SegmentationDisplayNode);`
- API footprints: `GetClipNode`

## widget: spinBox_SliceIntersectionThickness

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: spinBox_SliceIntersectionThickness | QSpinBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:127: QObject::connect(this->spinBox_SliceIntersectionThickness, SIGNAL(valueChanged(int)), q, SLOT(onSliceIntersectionThicknessChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:360: d->spinBox_SliceIntersectionThickness->setValue(d->SegmentationDisplayNode->GetSliceIntersectionThickness());`
- Connected slots/functions: `onSliceIntersectionThicknessChanged`
- API footprints: `GetPointer`, `GetSliceIntersectionThickness`, `SetSliceIntersectionThickness`

## widget: CollapsibleGroupBox_Advanced3D

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_Advanced3D | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: MaterialPropertyWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkVTKSurfaceMaterialPropertyWidget`
- Search text: MaterialPropertyWidget | ctkVTKSurfaceMaterialPropertyWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:88: this->MaterialPropertyWidget->setProperty(this->Property);`

## widget: checkBox_Visible

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_Visible | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:93: QObject::connect(this->checkBox_Visible, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:98: QObject::connect(this->checkBox_Visible, SIGNAL(stateChanged(int)), q, SLOT(onVisibilityChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:326: d->checkBox_Visible->setChecked(d->SegmentationDisplayNode->GetVisibility());`
- Connected slots/functions: `onVisibilityChanged`
- API footprints: `GetPointer`, `GetVisibility`, `SetVisibility`

## widget: frame_VisibilityOpacity

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame_VisibilityOpacity | QFrame
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: label_SliceFill

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice fill: | label_SliceFill | QLabel
- Text: Slice fill:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: label_SliceOutline

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice outline: | label_SliceOutline | QLabel
- Text: Slice outline:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: label_3D

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: 3D: | label_3D | QLabel
- Text: 3D:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: label_Opacity

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity | label_Opacity | QLabel
- Text: Opacity
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: SliderWidget_OpacitySliceOutline

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SliderWidget_OpacitySliceOutline | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:123: QObject::connect(this->SliderWidget_OpacitySliceOutline, SIGNAL(valueChanged(double)), q, SLOT(onOpacitySliceOutlineChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:152: QObject::connect(this->SliderWidget_OpacitySliceOutline_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacitySliceOutlineChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:276: d->SliderWidget_OpacitySliceOutline_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:277: d->SliderWidget_OpacitySliceOutline_SelectedSegment->setValue(properties.Opacity2DOutline);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:278: d->SliderWidget_OpacitySliceOutline_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:349: wasBlocked = d->SliderWidget_OpacitySliceOutline->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:350: d->SliderWidget_OpacitySliceOutline->setValue(d->SegmentationDisplayNode->GetOpacity2DOutline());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:351: d->SliderWidget_OpacitySliceOutline->blockSignals(wasBlocked);`
- Connected slots/functions: `onOpacitySliceOutlineChanged`, `onSegmentOpacitySliceOutlineChanged`
- API footprints: `GetOpacity2DOutline`, `GetPointer`, `SetOpacity2DOutline`, `SetSegmentOpacity2DOutline`

## widget: SliderWidget_OpacitySliceFill

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SliderWidget_OpacitySliceFill | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:122: QObject::connect(this->SliderWidget_OpacitySliceFill, SIGNAL(valueChanged(double)), q, SLOT(onOpacitySliceFillChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:151: QObject::connect(this->SliderWidget_OpacitySliceFill_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacitySliceFillChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:272: d->SliderWidget_OpacitySliceFill_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:273: d->SliderWidget_OpacitySliceFill_SelectedSegment->setValue(properties.Opacity2DFill);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:274: d->SliderWidget_OpacitySliceFill_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:345: wasBlocked = d->SliderWidget_OpacitySliceFill->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:346: d->SliderWidget_OpacitySliceFill->setValue(d->SegmentationDisplayNode->GetOpacity2DFill());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:347: d->SliderWidget_OpacitySliceFill->blockSignals(wasBlocked);`
- Connected slots/functions: `onOpacitySliceFillChanged`, `onSegmentOpacitySliceFillChanged`
- API footprints: `GetOpacity2DFill`, `GetPointer`, `SetOpacity2DFill`, `SetSegmentOpacity2DFill`

## widget: SliderWidget_Opacity3D

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SliderWidget_Opacity3D | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:124: QObject::connect(this->SliderWidget_Opacity3D, SIGNAL(valueChanged(double)), q, SLOT(onOpacity3DChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:153: QObject::connect(this->SliderWidget_Opacity3D_SelectedSegment, SIGNAL(valueChanged(double)), q, SLOT(onSegmentOpacity3DChanged(double)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:280: d->SliderWidget_Opacity3D_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:281: d->SliderWidget_Opacity3D_SelectedSegment->setValue(properties.Opacity3D);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:282: d->SliderWidget_Opacity3D_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:353: wasBlocked = d->SliderWidget_Opacity3D->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:354: d->SliderWidget_Opacity3D->setValue(d->SegmentationDisplayNode->GetOpacity3D());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:355: d->SliderWidget_Opacity3D->blockSignals(wasBlocked);`
- Connected slots/functions: `onOpacity3DChanged`, `onSegmentOpacity3DChanged`
- API footprints: `GetOpacity3D`, `GetPointer`, `SetOpacity3D`, `SetSegmentOpacity3D`

## widget: checkBox_VisibilitySliceFill

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_VisibilitySliceFill | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:104: QObject::connect(this->checkBox_VisibilitySliceFill, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:117: QObject::connect(this->checkBox_VisibilitySliceFill, SIGNAL(stateChanged(int)), q, SLOT(onVisibilitySliceFillChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:133: QObject::connect(this->checkBox_VisibilitySliceFill_SelectedSegment, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:146: QObject::connect(this->checkBox_VisibilitySliceFill_SelectedSegment, SIGNAL(stateChanged(int)), q, SLOT(onSegmentVisibilitySliceFillChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:260: d->checkBox_VisibilitySliceFill_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:261: d->checkBox_VisibilitySliceFill_SelectedSegment->setChecked(properties.Visible2DFill);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:262: d->checkBox_VisibilitySliceFill_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:333: wasBlocked = d->checkBox_VisibilitySliceFill->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:334: d->checkBox_VisibilitySliceFill->setChecked(d->SegmentationDisplayNode->GetVisibility2DFill());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:335: d->checkBox_VisibilitySliceFill->blockSignals(wasBlocked);`
- Connected slots/functions: `onSegmentVisibilitySliceFillChanged`, `onVisibilitySliceFillChanged`
- API footprints: `GetPointer`, `GetVisibility2DFill`, `SetSegmentVisibility2DFill`, `SetVisibility2DFill`

## widget: label_Visibility

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility | label_Visibility | QLabel
- Text: Visibility
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: checkBox_VisibilitySliceOutline

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_VisibilitySliceOutline | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:108: QObject::connect(this->checkBox_VisibilitySliceOutline, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:118: QObject::connect(this->checkBox_VisibilitySliceOutline, SIGNAL(stateChanged(int)), q, SLOT(onVisibilitySliceOutlineChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:137: QObject::connect(this->checkBox_VisibilitySliceOutline_SelectedSegment, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:147: QObject::connect(this->checkBox_VisibilitySliceOutline_SelectedSegment, SIGNAL(stateChanged(int)), q, SLOT(onSegmentVisibilitySliceOutlineChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:264: d->checkBox_VisibilitySliceOutline_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:265: d->checkBox_VisibilitySliceOutline_SelectedSegment->setChecked(properties.Visible2DOutline);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:266: d->checkBox_VisibilitySliceOutline_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:337: wasBlocked = d->checkBox_VisibilitySliceOutline->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:338: d->checkBox_VisibilitySliceOutline->setChecked(d->SegmentationDisplayNode->GetVisibility2DOutline());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:339: d->checkBox_VisibilitySliceOutline->blockSignals(wasBlocked);`
- Connected slots/functions: `onSegmentVisibilitySliceOutlineChanged`, `onVisibilitySliceOutlineChanged`
- API footprints: `GetPointer`, `GetVisibility2DOutline`, `SetSegmentVisibility2DOutline`, `SetVisibility2DOutline`

## widget: checkBox_Visibility3D

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_Visibility3D | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:112: QObject::connect(this->checkBox_Visibility3D, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:119: QObject::connect(this->checkBox_Visibility3D, SIGNAL(stateChanged(int)), q, SLOT(onVisibility3DChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:141: QObject::connect(this->checkBox_Visibility3D_SelectedSegment, //`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:148: QObject::connect(this->checkBox_Visibility3D_SelectedSegment, SIGNAL(stateChanged(int)), q, SLOT(onSegmentVisibility3DChanged(int)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:268: d->checkBox_Visibility3D_SelectedSegment->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:269: d->checkBox_Visibility3D_SelectedSegment->setChecked(properties.Visible3D);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:270: d->checkBox_Visibility3D_SelectedSegment->blockSignals(false);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:341: wasBlocked = d->checkBox_Visibility3D->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:342: d->checkBox_Visibility3D->setChecked(d->SegmentationDisplayNode->GetVisibility3D());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:343: d->checkBox_Visibility3D->blockSignals(wasBlocked);`
- Connected slots/functions: `onSegmentVisibility3DChanged`, `onVisibility3DChanged`
- API footprints: `GetPointer`, `GetVisibility3D`, `SetSegmentVisibility3D`, `SetVisibility3D`

## widget: label_Visible

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Overall visibility: | label_Visible | QLabel
- Text: Overall visibility:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: CollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: SlicerWidget_ClipNodeProperties

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLClipNodeWidget`
- Search text: SlicerWidget_ClipNodeProperties | qMRMLClipNodeWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:385: d->SlicerWidget_ClipNodeProperties->setMRMLClipNode(d->SegmentationDisplayNode->GetClipNode());`
- API footprints: `GetClipNode`

## widget: label_ClipNode

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Clip node: | label_ClipNode | QLabel
- Text: Clip node:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`

## widget: MRMLNodeComboBox_Clip

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_Clip | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:155: QObject::connect(this->MRMLNodeComboBox_Clip, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onClipNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:380: wasBlocked = d->MRMLNodeComboBox_Clip->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:381: d->MRMLNodeComboBox_Clip->setCurrentNode(d->SegmentationDisplayNode->GetClipNode());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:382: d->MRMLNodeComboBox_Clip->blockSignals(wasBlocked);`
- Connected slots/functions: `onClipNodeChanged`
- API footprints: `GetClipNode`, `GetID`, `SetAndObserveClipNodeID`, `vtkMRMLClipNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLClipNode"]}

## widget: SlicerWidget_ClipNodeDisplayProperties

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLClipNodeDisplayWidget`
- Search text: SlicerWidget_ClipNodeDisplayProperties | qMRMLClipNodeDisplayWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationDisplayNodeWidget.cxx:384: d->SlicerWidget_ClipNodeDisplayProperties->setMRMLDisplayNode(d->SegmentationDisplayNode);`
- API footprints: `GetClipNode`
