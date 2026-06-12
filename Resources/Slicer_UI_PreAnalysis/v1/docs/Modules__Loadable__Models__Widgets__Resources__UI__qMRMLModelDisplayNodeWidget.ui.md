# Slicer UI Analysis: Modules/Loadable/Models/Widgets/Resources/UI/qMRMLModelDisplayNodeWidget.ui

- Owner class: `qMRMLModelDisplayNodeWidget`
- UI file: `Modules/Loadable/Models/Widgets/Resources/UI/qMRMLModelDisplayNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLModelDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLModelDisplayNodeWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:28: #include "qMRMLModelDisplayNodeWidget.h"`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:29: #include "ui_qMRMLModelDisplayNodeWidget.h"`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:54: class qMRMLModelDisplayNodeWidgetPrivate`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:56: , public Ui_qMRMLModelDisplayNodeWidget`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:58: Q_DECLARE_PUBLIC(qMRMLModelDisplayNodeWidget);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:61: qMRMLModelDisplayNodeWidget* const q_ptr;`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:65: qMRMLModelDisplayNodeWidgetPrivate(qMRMLModelDisplayNodeWidget& object);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:87: qMRMLModelDisplayNodeWidgetPrivate::qMRMLModelDisplayNodeWidgetPrivate(qMRMLModelDisplayNodeWidget& object)`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:94: void qMRMLModelDisplayNodeWidgetPrivate::init()`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:96: Q_Q(qMRMLModelDisplayNodeWidget);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:142: QList<vtkMRMLModelDisplayNode*> qMRMLModelDisplayNodeWidgetPrivate::modelDisplayNodesFromSelection() const`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:144: Q_Q(const qMRMLModelDisplayNodeWidget);`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ScalarsDisplayWidget.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetPointer`, `vtkMRMLModelDisplayNode::SafeDownCast`, `vtkMRMLScene::EndBatchProcessEvent`

## widget: RepresentationCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: RepresentationCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: RepresentationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Representation: | RepresentationLabel | QLabel
- Text: Representation:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: RepresentationComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: RepresentationComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:113: q->connect(this->RepresentationComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setRepresentation(int)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:418: case REPRESENTATION_POINTS: d->RepresentationComboBox->setCurrentIndex(0); break;`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:419: case REPRESENTATION_WIREFRAME: d->RepresentationComboBox->setCurrentIndex(1); break;`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:423: d->RepresentationComboBox->setCurrentIndex(3);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:427: d->RepresentationComboBox->setCurrentIndex(2);`
- Connected slots/functions: `setRepresentation`
- API footprints: `EndModify`, `GetEdgeVisibility`, `GetRepresentation`, `SetEdgeVisibility`, `SetRepresentation`, `StartModify`

## widget: CullingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visible Sides: | CullingLabel | QLabel
- Text: Visible Sides:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: ShowFacesComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: All: recommended for open surface. Front: recommended for faster rendering of closed opaque surfaces. Back: Useful for rendering backface of open surfaces with different color. | ShowFacesComboBox | QComboBox
- Tooltip: All: recommended for open surface. Front: recommended for faster rendering of closed opaque surfaces. Back: Useful for rendering backface of open surfaces with different color.
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:116: q->connect(this->ShowFacesComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setShowFaces(int)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:447: d->ShowFacesComboBox->setCurrentIndex(1);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:452: d->ShowFacesComboBox->setCurrentIndex(2);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:457: d->ShowFacesComboBox->setCurrentIndex(0);`
- Connected slots/functions: `setShowFaces`
- API footprints: `EndModify`, `GetBackfaceCulling`, `GetFrontfaceCulling`, `SetBackfaceCulling`, `SetFrontfaceCulling`, `StartModify`

## widget: ClippingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Clipping: | ClippingLabel | QLabel
- Text: Clipping:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: ClippingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Hide part of the model according to Clipping Planes settings. | ClippingCheckBox | QCheckBox
- Tooltip: Hide part of the model according to Clipping Planes settings.
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:103: q->connect(this->ClippingCheckBox, SIGNAL(toggled(bool)), q, SLOT(setClipping(bool)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:387: d->ClippingCheckBox->setChecked(d->CurrentDisplayNode->GetClipping());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:541: return d->ClippingCheckBox->isChecked();`
- Connected slots/functions: `setClipping`
- API footprints: `GetClipping`, `GetSliceIntersectionThickness`, `GetVisibility`, `GetVisibility2D`, `SetClipping`

## widget: ConfigureClippingPushButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Configure... | Configure clipping planes | ConfigureClippingPushButton | QPushButton
- Text: Configure...
- Tooltip: Configure clipping planes
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:104: q->connect(this->ConfigureClippingPushButton, SIGNAL(clicked()), q, SIGNAL(clippingConfigurationButtonClicked()));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:105: this->ConfigureClippingPushButton->setVisible(false);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:885: return d->ConfigureClippingPushButton->isVisible();`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:892: d->ConfigureClippingPushButton->setVisible(show);`

## widget: Advanced3dCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: Advanced3dCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: PointSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Point Size: | PointSizeLabel | QLabel
- Text: Point Size:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: PointSizeSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: PointSizeSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:114: q->connect(this->PointSizeSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setPointSize(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:432: d->PointSizeSliderWidget->setValue(d->CurrentDisplayNode->GetPointSize());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:434: d->PointSizeSliderWidget->setEnabled(showPointSize);`
- Connected slots/functions: `setPointSize`
- API footprints: `GetLineWidth`, `GetPointSize`, `GetRepresentation`, `SetPointSize`

## widget: LineWidthLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Line Width: | LineWidthLabel | QLabel
- Text: Line Width:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: LineWidthSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: LineWidthSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:115: q->connect(this->LineWidthSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setLineWidth(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:436: d->LineWidthSliderWidget->setValue(d->CurrentDisplayNode->GetLineWidth());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:442: d->LineWidthSliderWidget->setEnabled(showLineWidth);`
- Connected slots/functions: `setLineWidth`
- API footprints: `GetBackfaceCulling`, `GetFrontfaceCulling`, `GetLineWidth`, `GetRepresentation`, `SetLineWidth`

## widget: EdgeColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Edge Color: | EdgeColorLabel | QLabel
- Text: Edge Color:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: EdgeColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: EdgeColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:119: q->connect(this->EdgeColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(setEdgeColor(QColor)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:467: d->EdgeColorPickerButton->setColor(QColor::fromRgbF(qMin(ec[0], 1.), qMin(ec[1], 1.), qMin(ec[2], 1.)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:469: d->EdgeColorPickerButton->setEnabled(showEdgeColor);`
- Connected slots/functions: `setEdgeColor`
- API footprints: `GetEdgeColor`, `GetEdgeVisibility`, `GetOpacity`, `GetRepresentation`, `SetEdgeColor`

## widget: LightingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Lighting: | LightingLabel | QLabel
- Text: Lighting:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: LightingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: LightingCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:125: q->connect(this->LightingCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLighting(bool)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:486: d->LightingCheckBox->setChecked(d->CurrentDisplayNode->GetLighting());`
- Connected slots/functions: `setLighting`
- API footprints: `GetInterpolation`, `GetLighting`, `GetPointer`, `SetLighting`

## widget: InterpolationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Interpolation: | InterpolationLabel | QLabel
- Text: Interpolation:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: InterpolationComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: InterpolationComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:126: q->connect(this->InterpolationComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setInterpolation(int)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:487: d->InterpolationComboBox->setCurrentIndex(d->CurrentDisplayNode->GetInterpolation());`
- Connected slots/functions: `setInterpolation`
- API footprints: `GetInterpolation`, `GetLighting`, `GetPointer`, `SetInterpolationToFlat`, `SetInterpolationToGouraud`, `SetInterpolationToPBR`, `SetInterpolationToPhong`, `vtkMRMLDisplayNode::FlatInterpolation`, `vtkMRMLDisplayNode::GouraudInterpolation`, `vtkMRMLDisplayNode::PBRInterpolation`, `vtkMRMLDisplayNode::PhongInterpolation`

## widget: MaterialPropertyWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkVTKSurfaceMaterialPropertyWidget`
- Search text: MaterialPropertyWidget | ctkVTKSurfaceMaterialPropertyWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:99: this->MaterialPropertyWidget->setProperty(this->Property);`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Backface Color Offset: | Backface color hue, saturation, and brightess offset to frontface color | label_2 | QLabel
- Text: Backface Color Offset:
- Tooltip: Backface color hue, saturation, and brightess offset to frontface color
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: BackfaceHueOffsetSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Color hue offset | BackfaceHueOffsetSpinBox | ctkDoubleSpinBox
- Tooltip: Color hue offset
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:121: q->connect(this->BackfaceHueOffsetSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setBackfaceHueOffset(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:475: QSignalBlocker blocker1(d->BackfaceHueOffsetSpinBox);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:478: d->BackfaceHueOffsetSpinBox->setValue(hsvOffset[0]);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:482: d->BackfaceHueOffsetSpinBox->setEnabled(d->CurrentModelDisplayNode != nullptr);`
- Connected slots/functions: `setBackfaceHueOffset`
- API footprints: `GetBackfaceColorHSVOffset`, `SetBackfaceColorHSVOffset`, `vtkMRMLModelDisplayNode::SafeDownCast`

## widget: BackfaceSaturationOffsetSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Color saturation offset | BackfaceSaturationOffsetSpinBox | ctkDoubleSpinBox
- Tooltip: Color saturation offset
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:122: q->connect(this->BackfaceSaturationOffsetSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setBackfaceSaturationOffset(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:476: QSignalBlocker blocker2(d->BackfaceSaturationOffsetSpinBox);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:477: QSignalBlocker blocker3(d->BackfaceSaturationOffsetSpinBox);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:479: d->BackfaceSaturationOffsetSpinBox->setValue(hsvOffset[1]);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:483: d->BackfaceSaturationOffsetSpinBox->setEnabled(d->CurrentModelDisplayNode != nullptr);`
- Connected slots/functions: `setBackfaceSaturationOffset`
- API footprints: `GetBackfaceColorHSVOffset`, `SetBackfaceColorHSVOffset`, `vtkMRMLModelDisplayNode::SafeDownCast`

## widget: BackfaceBrightnessOffsetSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Color saturation offset | BackfaceBrightnessOffsetSpinBox | ctkDoubleSpinBox
- Tooltip: Color saturation offset
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:123: q->connect(this->BackfaceBrightnessOffsetSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setBackfaceBrightnessOffset(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:480: d->BackfaceBrightnessOffsetSpinBox->setValue(hsvOffset[2]);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:484: d->BackfaceBrightnessOffsetSpinBox->setEnabled(d->CurrentModelDisplayNode != nullptr);`
- Connected slots/functions: `setBackfaceBrightnessOffset`
- API footprints: `GetBackfaceColorHSVOffset`, `GetLighting`, `SetBackfaceColorHSVOffset`, `vtkMRMLModelDisplayNode::SafeDownCast`

## widget: SliceDisplayCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: SliceDisplayCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: SliceIntersectionVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | SliceIntersectionVisibilityLabel | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: SliceIntersectionVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: SliceIntersectionVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:107: q->connect(this->SliceIntersectionVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setSliceIntersectionVisible(bool)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:388: d->SliceIntersectionVisibilityCheckBox->setChecked(d->CurrentDisplayNode->GetVisibility2D());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:560: return d->SliceIntersectionVisibilityCheckBox->isChecked();`
- Connected slots/functions: `setSliceIntersectionVisible`
- API footprints: `GetClipping`, `GetSliceIntersectionThickness`, `GetVisibility2D`, `SetVisibility2D`

## widget: SliceIntersectionOpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | SliceIntersectionOpacityLabel | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: SliceIntersectionOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SliceIntersectionOpacitySlider | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:110: q->connect(this->SliceIntersectionOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(setSliceIntersectionOpacity(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:393: d->SliceIntersectionOpacitySlider->setValue(d->CurrentDisplayNode->GetSliceIntersectionOpacity());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:598: return d->SliceIntersectionOpacitySlider->value();`
- Connected slots/functions: `setSliceIntersectionOpacity`
- API footprints: `GetSliceDisplayMode`, `GetSliceIntersectionOpacity`, `SetSliceIntersectionOpacity`, `vtkMRMLModelDisplayNode::SliceDisplayIntersection`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Mode: | label | QLabel
- Text: Mode:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: SliceDisplayModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Intersection: shows intersection of the model with the slice. Projection: shows the full model projected on the slice plane with solid color. Colored projection: shows the full model projected on the slice plane, colored by distance from the slice plane (overrides Active scalar selection). | SliceDisplayModeComboBox | QComboBox
- Tooltip: Intersection: shows intersection of the model with the slice. Projection: shows the full model projected on the slice plane with solid color. Colored projection: shows the full model projected on the slice plane, colored by distance from the slice plane (overrides Active scalar selection).
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:108: q->connect(this->SliceDisplayModeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setSliceDisplayMode(int)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:395: d->SliceDisplayModeComboBox->setEnabled(d->CurrentModelDisplayNode);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:398: d->SliceDisplayModeComboBox->setCurrentIndex(d->CurrentModelDisplayNode->GetSliceDisplayMode());`
- Connected slots/functions: `setSliceDisplayMode`
- API footprints: `EndModify`, `GetDistanceEncodedProjectionColorNodeID`, `GetSliceDisplayMode`, `GetSliceIntersectionOpacity`, `SetAndObserveDistanceEncodedProjectionColorNodeID`, `SetSliceDisplayMode`, `StartModify`, `vtkMRMLModelDisplayNode::SliceDisplayDistanceEncodedProjection`

## widget: SliceIntersectionThicknessLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Line Width: | SliceIntersectionThicknessLabel | QLabel
- Text: Line Width:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: SliceIntersectionThicknessSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: SliceIntersectionThicknessSpinBox | QSpinBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:109: q->connect(this->SliceIntersectionThicknessSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setSliceIntersectionThickness(int)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:389: d->SliceIntersectionThicknessSpinBox->setValue(d->CurrentDisplayNode->GetSliceIntersectionThickness());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:392: d->SliceIntersectionThicknessSpinBox->setEnabled(showSliceIntersectionThickness);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:579: return d->SliceIntersectionThicknessSpinBox->value();`
- Connected slots/functions: `setSliceIntersectionThickness`
- API footprints: `GetClipping`, `GetSliceDisplayMode`, `GetSliceIntersectionOpacity`, `GetSliceIntersectionThickness`, `GetVisibility2D`, `SetSliceIntersectionThickness`, `vtkMRMLModelDisplayNode::SliceDisplayIntersection`

## widget: DistanceToColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color Table: | DistanceToColorLabel | QLabel
- Text: Color Table:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: DistanceToColorNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: Color table that maps distance from slice plane to colors. Used when 'Distance encoded projection' mode is chosen. | DistanceToColorNodeComboBox | qMRMLColorTableComboBox
- Tooltip: Color table that maps distance from slice plane to colors. Used when 'Distance encoded projection' mode is chosen.
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:111: q->connect(this->DistanceToColorNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setDistanceToColorNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:401: bool wasBlocking = d->DistanceToColorNodeComboBox->blockSignals(true);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:402: if (d->DistanceToColorNodeComboBox->mrmlScene() != this->mrmlScene())`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:404: d->DistanceToColorNodeComboBox->setMRMLScene(this->mrmlScene());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:407: && d->DistanceToColorNodeComboBox->currentNodeID() != d->CurrentModelDisplayNode->GetDistanceEncodedProjectionColorNodeID())`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:409: d->DistanceToColorNodeComboBox->setCurrentNodeID(d->CurrentModelDisplayNode->GetDistanceEncodedProjectionColorNodeID());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:411: d->DistanceToColorNodeComboBox->setEnabled(d->CurrentModelDisplayNode && //`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:413: d->DistanceToColorNodeComboBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setDistanceToColorNode`
- API footprints: `GetDistanceEncodedProjectionColorNodeID`, `GetID`, `GetPointer`, `GetSliceDisplayMode`, `SetAndObserveDistanceEncodedProjectionColorNodeID`, `vtkMRMLModelDisplayNode::SliceDisplayDistanceEncodedProjection`

## widget: ScalarsGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: ScalarsGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Key UI properties: {"checked": "false"}

## widget: ScalarsDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLScalarsDisplayWidget`
- Search text: ScalarsDisplayWidget | qMRMLScalarsDisplayWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:128: q->connect(this->ScalarsDisplayWidget,`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:132: q->connect(this->ScalarsDisplayWidget, SIGNAL(displayNodeChanged()), q, SIGNAL(displayNodeChanged()));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:334: d->ScalarsDisplayWidget->setMRMLDisplayNodes(d->displayNodesFromSelection());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:363: d->ScalarsDisplayWidget->setMRMLDisplayNode(displayNode);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:498: d->ScalarsDisplayWidget->updateWidgetFromMRML();`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h:26: #include "qMRMLScalarsDisplayWidget.h"`
- API footprints: `GetPointer`, `vtkMRMLDisplayNode::ScalarRangeFlagType`

## widget: CollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: DisplayNodeViewComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLDisplayNodeViewComboBox`
- Search text: Select views in which to show this node. All unchecked shows in all 3D and 2D views. | DisplayNodeViewComboBox | qMRMLDisplayNodeViewComboBox
- Tooltip: Select views in which to show this node. All unchecked shows in all 3D and 2D views.
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:386: d->DisplayNodeViewComboBox->setMRMLDisplayNode(d->CurrentDisplayNode);`
- API footprints: `GetClipping`, `GetVisibility`, `GetVisibility2D`

## widget: DisplayNodeViewLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View: | DisplayNodeViewLabel | QLabel
- Text: View:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: ColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: ColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:117: q->connect(this->ColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(setColor(QColor)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:119: q->connect(this->EdgeColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(setEdgeColor(QColor)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:461: bool wasBlocked = d->ColorPickerButton->blockSignals(true);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:462: d->ColorPickerButton->setColor(QColor::fromRgbF(qMin(c[0], 1.), qMin(c[1], 1.), qMin(c[2], 1.)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:463: d->ColorPickerButton->blockSignals(wasBlocked);`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:467: d->EdgeColorPickerButton->setColor(QColor::fromRgbF(qMin(ec[0], 1.), qMin(ec[1], 1.), qMin(ec[2], 1.)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:469: d->EdgeColorPickerButton->setEnabled(showEdgeColor);`
- Connected slots/functions: `setColor`, `setEdgeColor`
- API footprints: `GetColor`, `GetEdgeColor`, `GetEdgeVisibility`, `GetOpacity`, `GetRepresentation`, `SetColor`, `SetEdgeColor`, `SetScalarVisibility`

## widget: ColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color: | ColorLabel | QLabel
- Text: Color:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: VisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: VisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:102: q->connect(this->VisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility(bool)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:107: q->connect(this->SliceIntersectionVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setSliceIntersectionVisible(bool)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:385: d->VisibilityCheckBox->setChecked(d->CurrentDisplayNode->GetVisibility());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:388: d->SliceIntersectionVisibilityCheckBox->setChecked(d->CurrentDisplayNode->GetVisibility2D());`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:521: return d->VisibilityCheckBox->isChecked();`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:560: return d->SliceIntersectionVisibilityCheckBox->isChecked();`
- Connected slots/functions: `setSliceIntersectionVisible`, `setVisibility`
- API footprints: `GetClipping`, `GetSliceIntersectionThickness`, `GetVisibility`, `GetVisibility2D`, `SetVisibility`, `SetVisibility2D`

## widget: OpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | OpacityLabel | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`

## widget: OpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: OpacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:118: q->connect(this->OpacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setOpacity(double)));`
  - `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx:465: d->OpacitySliderWidget->setValue(d->CurrentDisplayNode->GetOpacity());`
- Connected slots/functions: `setOpacity`
- API footprints: `GetEdgeColor`, `GetOpacity`, `SetOpacity`

## widget: VisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | VisibilityLabel | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.cxx`, `Modules/Loadable/Models/Widgets/qMRMLModelDisplayNodeWidget.h`
