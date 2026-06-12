# Slicer UI Analysis: Modules/Loadable/Transforms/Widgets/Resources/UI/qMRMLTransformDisplayNodeWidget.ui

- Owner class: `qMRMLTransformDisplayNodeWidget`
- UI file: `Modules/Loadable/Transforms/Widgets/Resources/UI/qMRMLTransformDisplayNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLTransformDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: Whether the transform widget can be translated. | qMRMLTransformDisplayNodeWidget | qMRMLWidget
- Tooltip: Whether the transform widget can be translated.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:24: #include "qMRMLTransformDisplayNodeWidget.h"`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:25: #include "ui_qMRMLTransformDisplayNodeWidget.h"`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:47: class qMRMLTransformDisplayNodeWidgetPrivate : public Ui_qMRMLTransformDisplayNodeWidget`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:49: Q_DECLARE_PUBLIC(qMRMLTransformDisplayNodeWidget);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:52: qMRMLTransformDisplayNodeWidget* const q_ptr;`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:55: qMRMLTransformDisplayNodeWidgetPrivate(qMRMLTransformDisplayNodeWidget& object);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:56: ~qMRMLTransformDisplayNodeWidgetPrivate();`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:64: // qMRMLTransformDisplayNodeWidgetPrivate methods`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:67: qMRMLTransformDisplayNodeWidgetPrivate::qMRMLTransformDisplayNodeWidgetPrivate(qMRMLTransformDisplayNodeWidget& object)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:75: qMRMLTransformDisplayNodeWidgetPrivate ::~qMRMLTransformDisplayNodeWidgetPrivate()`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:82: void qMRMLTransformDisplayNodeWidgetPrivate::init()`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:84: Q_Q(qMRMLTransformDisplayNodeWidget);`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> RegionNodeComboBox.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> GlyphSpacingMm.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> GridSpacingMm.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> GridLineDiameterMm.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> GridResolutionMm.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> ContourResolutionMm.setMRMLScene(vtkMRMLScene*)`
- API footprints: `Delete`, `vtkMRMLTransformNode::SafeDownCast`

## widget: VisualizationCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: VisualizationCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: ColorsSection

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: ColorsSection | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Key UI properties: {"checked": "false"}

## widget: ColorMapWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKScalarsToColorsWidget`
- Search text: ColorMapWidget | ctkVTKScalarsToColorsWidget
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:89: this->ColorMapWidget->view()->setValidBounds(validBounds);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:90: this->ColorMapWidget->view()->addColorTransferFunction(nullptr);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:91: this->ColorMapWidget->view()->setColorTransferFunctionToPlots(this->ColorTransferFunction);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:94: this->ColorMapWidget->view()->chartBounds(chartBounds);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:97: this->ColorMapWidget->view()->setChartUserBounds(chartBounds);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:100: this->ColorMapWidget->view()->setPlotsUserBounds(chartBounds);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:101: this->ColorMapWidget->view()->update();`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1045: d->ColorMapWidget->view()->chartBounds(chartBounds);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1048: d->ColorMapWidget->view()->setChartUserBounds(chartBounds);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1049: d->ColorMapWidget->view()->update();`
- API footprints: `GetRange`

## widget: GlyphToggle

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Glyph | Visualize transform using glyphs | GlyphToggle | QPushButton
- Text: Glyph
- Tooltip: Visualize transform using glyphs
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:165: QObject::connect(this->GlyphToggle, SIGNAL(toggled(bool)), q, SLOT(setGlyphVisualizationMode(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:267: d->GlyphToggle->setChecked(glyphMode);`
- Connected slots/functions: `setGlyphVisualizationMode`
- API footprints: `GetVisualizationMode`, `SetVisualizationMode`, `vtkMRMLTransformDisplayNode::VIS_MODE_CONTOUR`, `vtkMRMLTransformDisplayNode::VIS_MODE_GLYPH`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: GridToggle

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Grid | Visualize transform using a warped grid | GridToggle | QPushButton
- Text: Grid
- Tooltip: Visualize transform using a warped grid
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:166: QObject::connect(this->GridToggle, SIGNAL(toggled(bool)), q, SLOT(setGridVisualizationMode(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:268: d->GridToggle->setChecked(gridMode);`
- Connected slots/functions: `setGridVisualizationMode`
- API footprints: `SetVisualizationMode`, `vtkMRMLTransformDisplayNode::VIS_MODE_GRID`
- Key UI properties: {"checkable": "true"}

## widget: ContourToggle

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Contour | Visualize transform by isoline/isosurface contours of the displacement magnitude | ContourToggle | QPushButton
- Text: Contour
- Tooltip: Visualize transform by isoline/isosurface contours of the displacement magnitude
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:167: QObject::connect(this->ContourToggle, SIGNAL(toggled(bool)), q, SLOT(setContourVisualizationMode(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:269: d->ContourToggle->setChecked(contourMode);`
- Connected slots/functions: `setContourVisualizationMode`
- API footprints: `GetRegionNode`, `SetVisualizationMode`, `vtkMRMLTransformDisplayNode::VIS_MODE_CONTOUR`
- Key UI properties: {"checkable": "true"}

## widget: Visible3dCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show transform in the 3D views | Visible3dCheckBox | QCheckBox
- Tooltip: Show transform in the 3D views
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:111: QObject::connect(this->InteractionVisible3dCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorVisibility3d(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:161: QObject::connect(this->Visible3dCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility3d(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:261: d->Visible3dCheckBox->setChecked(d->TransformDisplayNode->GetVisibility3D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:379: wasBlocking = d->InteractionVisible3dCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:380: d->InteractionVisible3dCheckBox->setChecked(d->TransformDisplayNode->GetEditorVisibility3D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:381: d->InteractionVisible3dCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setEditorVisibility3d`, `setVisibility3d`
- API footprints: `GetEditorVisibility3D`, `GetVisibility`, `GetVisibility2D`, `GetVisibility3D`, `GetVisualizationMode`, `SetEditorVisibility3D`, `SetVisibility3D`, `vtkMRMLTransformDisplayNode::VIS_MODE_GLYPH`
- Key UI properties: {"checked": "true"}

## widget: RegionLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Region: | Reference image for visualizing transform nodes (will only use size, orientation and position) | RegionLabel | QLabel
- Text: Region:
- Tooltip: Reference image for visualizing transform nodes (will only use size, orientation and position)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: RegionNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Region for visualizing transform nodes (will only use size, orientation and position) | RegionNodeComboBox | qMRMLNodeComboBox
- Tooltip: Region for visualizing transform nodes (will only use size, orientation and position)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:163: QObject::connect(this->RegionNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(regionNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:271: d->RegionNodeComboBox->setCurrentNode(d->TransformDisplayNode->GetRegionNode());`
- Connected slots/functions: `regionNodeChanged`
- API footprints: `GetRegionNode`, `SetAndObserveRegionNode`
- Key UI properties: {"nodeTypes": ["vtkMRMLSliceNode", "vtkMRMLModelNode", "vtkMRMLVolumeNode", "vtkMRMLMarkupsROINode", "vtkMRMLMarkupsPlaneNode"]}

## widget: VisibleCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: VisibleCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:110: QObject::connect(this->InteractionVisibleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorVisibility(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:159: QObject::connect(this->VisibleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:259: d->VisibleCheckBox->setChecked(d->TransformDisplayNode->GetVisibility());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:375: wasBlocking = d->InteractionVisibleCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:376: d->InteractionVisibleCheckBox->setChecked(d->TransformDisplayNode->GetEditorVisibility());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:377: d->InteractionVisibleCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setEditorVisibility`, `setVisibility`
- API footprints: `GetEditorVisibility`, `GetVisibility`, `GetVisibility2D`, `GetVisibility3D`, `SetEditorVisibility`, `SetVisibility`

## widget: AdvancedParameters

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: AdvancedParameters | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:107: this->AdvancedParameters->setCollapsed(true);`

## widget: SliceIntersectionThicknessLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: 2D line width: | Adjust radius of base of arrow tip | SliceIntersectionThicknessLabel | QLabel
- Text: 2D line width:
- Tooltip: Adjust radius of base of arrow tip
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: SliceIntersectionThicknessSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: SliceIntersectionThicknessSpinBox | QSpinBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:170: QObject::connect(this->SliceIntersectionThicknessSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setSliceIntersectionThickness(int)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:276: d->SliceIntersectionThicknessSpinBox->setValue(d->TransformDisplayNode->GetSliceIntersectionThickness());`
- Connected slots/functions: `setSliceIntersectionThickness`
- API footprints: `GetSliceIntersectionThickness`, `SetSliceIntersectionThickness`

## widget: GlyphPointsLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Source points: | GlyphPointsLabel | QLabel
- Text: Source points:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:286: d->GlyphPointsLabel->setVisible(glyphMode);`
- API footprints: `GetGlyphPointsNode`, `GetGlyphSpacingMm`

## widget: GlyphPointsNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Markups node that defines glyph starting positions. If specified then 3D view 'Region' is ignored. | GlyphPointsNodeComboBox | qMRMLNodeComboBox
- Tooltip: Markups node that defines glyph starting positions. If specified then 3D view 'Region' is ignored.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:173: QObject::connect(this->GlyphPointsNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(glyphPointsNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:284: d->GlyphPointsNodeComboBox->setCurrentNode(d->TransformDisplayNode->GetGlyphPointsNode());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:285: d->GlyphPointsNodeComboBox->setVisible(glyphMode);`
- Connected slots/functions: `glyphPointsNodeChanged`
- API footprints: `GetGlyphPointsNode`, `GetGlyphSpacingMm`, `GetGlyphType`, `SetAndObserveGlyphPointsNode`, `vtkMRMLTransformDisplayNode::GLYPH_TYPE_SPHERE`
- Key UI properties: {"nodeTypes": ["vtkMRMLMarkupsNode"]}

## widget: GlyphSpacingLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Spacing: | Distance between the glyph points | GlyphSpacingLabel | QLabel
- Text: Spacing:
- Tooltip: Distance between the glyph points
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:290: d->GlyphSpacingLabel->setVisible(glyphMode);`
- API footprints: `GetGlyphPointsNode`, `GetGlyphScalePercent`

## widget: GlyphSpacingMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Distance between the glyph points | GlyphSpacingMm | qMRMLSliderWidget
- Tooltip: Distance between the glyph points
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:174: QObject::connect(this->GlyphSpacingMm, SIGNAL(valueChanged(double)), q, SLOT(setGlyphSpacingMm(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:287: d->GlyphSpacingMm->setValue(d->TransformDisplayNode->GetGlyphSpacingMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:288: d->GlyphSpacingMm->setEnabled(d->TransformDisplayNode->GetGlyphPointsNode() == nullptr);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:289: d->GlyphSpacingMm->setVisible(glyphMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:661: void qMRMLTransformDisplayNodeWidget::setGlyphSpacingMm(double spacing)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:668: d->TransformDisplayNode->SetGlyphSpacingMm(spacing);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:69: void setGlyphSpacingMm(double spacing);`
- Connected slots/functions: `setGlyphSpacingMm`
- API footprints: `GetGlyphPointsNode`, `GetGlyphScalePercent`, `GetGlyphSpacingMm`, `SetGlyphSpacingMm`

## widget: GlyphScaleLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Scale factor: | Percentage of displacement used for setting the glyph size. 100% means the glyph size equals the actual displacement. | GlyphScaleLabel | QLabel
- Text: Scale factor:
- Tooltip: Percentage of displacement used for setting the glyph size. 100% means the glyph size equals the actual displacement.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:293: d->GlyphScaleLabel->setVisible(glyphMode);`
- API footprints: `GetGlyphDisplayRangeMaxMm`, `GetGlyphDisplayRangeMinMm`, `GetGlyphScalePercent`

## widget: GlyphScalePercent

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Percentage of displacement used for setting the glyph size. 100% means the glyph size equals the actual displacement. Does not affect coloring and visible range. | GlyphScalePercent | qMRMLSliderWidget
- Tooltip: Percentage of displacement used for setting the glyph size. 100% means the glyph size equals the actual displacement. Does not affect coloring and visible range.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:175: QObject::connect(this->GlyphScalePercent, SIGNAL(valueChanged(double)), q, SLOT(setGlyphScalePercent(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:291: d->GlyphScalePercent->setValue(d->TransformDisplayNode->GetGlyphScalePercent());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:292: d->GlyphScalePercent->setVisible(glyphMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:672: void qMRMLTransformDisplayNodeWidget::setGlyphScalePercent(double scale)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:679: d->TransformDisplayNode->SetGlyphScalePercent(scale);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:70: void setGlyphScalePercent(double scale);`
- Connected slots/functions: `setGlyphScalePercent`
- API footprints: `GetGlyphDisplayRangeMaxMm`, `GetGlyphScalePercent`, `SetGlyphScalePercent`

## widget: GlyphDisplayRangeLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Visible range: | Glyphs are shown if the displacement magnitude is within this range | GlyphDisplayRangeLabel | QLabel
- Text: Visible range:
- Tooltip: Glyphs are shown if the displacement magnitude is within this range
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:297: d->GlyphDisplayRangeLabel->setVisible(glyphMode);`
- API footprints: `GetGlyphDisplayRangeMinMm`, `GetGlyphType`

## widget: GlyphDisplayRangeMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: Only those glyphs are shown that have displacement magnitude within this range | GlyphDisplayRangeMm | qMRMLRangeWidget
- Tooltip: Only those glyphs are shown that have displacement magnitude within this range
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:176: QObject::connect(this->GlyphDisplayRangeMm, SIGNAL(valuesChanged(double, double)), q, SLOT(setGlyphDisplayRangeMm(double, double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:294: d->GlyphDisplayRangeMm->setMaximumValue(d->TransformDisplayNode->GetGlyphDisplayRangeMaxMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:295: d->GlyphDisplayRangeMm->setMinimumValue(d->TransformDisplayNode->GetGlyphDisplayRangeMinMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:296: d->GlyphDisplayRangeMm->setVisible(glyphMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:683: void qMRMLTransformDisplayNodeWidget::setGlyphDisplayRangeMm(double min, double max)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:71: void setGlyphDisplayRangeMm(double min, double max);`
- Connected slots/functions: `setGlyphDisplayRangeMm`
- API footprints: `EndModify`, `GetGlyphDisplayRangeMaxMm`, `GetGlyphDisplayRangeMinMm`, `GetGlyphType`, `SetGlyphDisplayRangeMaxMm`, `SetGlyphDisplayRangeMinMm`, `StartModify`

## widget: GlyphTypeLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Glyph type: | Choose a glyph type to use | GlyphTypeLabel | QLabel
- Text: Glyph type:
- Tooltip: Choose a glyph type to use
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:300: d->GlyphTypeLabel->setVisible(glyphMode);`
- API footprints: `GetGlyphType`

## widget: GlyphTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: Choose a glyph type to use | GlyphTypeComboBox | ctkComboBox
- Tooltip: Choose a glyph type to use
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:177: QObject::connect(this->GlyphTypeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setGlyphType(int)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:298: d->GlyphTypeComboBox->setCurrentIndex(d->TransformDisplayNode->GetGlyphType());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:299: d->GlyphTypeComboBox->setVisible(glyphMode);`
- Connected slots/functions: `setGlyphType`
- API footprints: `GetGlyphType`, `SetGlyphType`

## widget: GlyphSourceOptions2D

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: GlyphSourceOptions2D | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:303: d->GlyphSourceOptions2D->setVisible(glyphMode);`
- API footprints: `GetGlyphTipLengthPercent2D`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: GlyphTipLengthLabel2D

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Tip length: | Adjust how much of the tip the arrow will consist of as a decimal percentage | GlyphTipLengthLabel2D | QLabel
- Text: Tip length:
- Tooltip: Adjust how much of the tip the arrow will consist of as a decimal percentage
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:306: d->GlyphTipLengthLabel2D->setVisible(arrowGlyph);`
- API footprints: `GetGlyphResolution2D`, `GetGlyphTipLengthPercent2D`

## widget: GlyphTipLengthPercent2D

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Length of the arrow tip  as percentage of displacement | GlyphTipLengthPercent2D | ctkSliderWidget
- Tooltip: Length of the arrow tip  as percentage of displacement
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:185: QObject::connect(this->GlyphTipLengthPercent2D, SIGNAL(valueChanged(double)), q, SLOT(setGlyphTipLengthPercent2D(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:304: d->GlyphTipLengthPercent2D->setValue(d->TransformDisplayNode->GetGlyphTipLengthPercent2D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:305: d->GlyphTipLengthPercent2D->setVisible(arrowGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:639: void qMRMLTransformDisplayNodeWidget::setGlyphTipLengthPercent2D(double lengthPercent)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:646: d->TransformDisplayNode->SetGlyphTipLengthPercent2D(lengthPercent);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:79: void setGlyphTipLengthPercent2D(double lengthPercent);`
- Connected slots/functions: `setGlyphTipLengthPercent2D`
- API footprints: `GetGlyphResolution2D`, `GetGlyphTipLengthPercent2D`, `SetGlyphTipLengthPercent2D`

## widget: GlyphResolutionLabel2D

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Resolution: | Adjust resolution of the glyph (higher value generates smoother curved lines but visualization may be slower) | GlyphResolutionLabel2D | QLabel
- Text: Resolution:
- Tooltip: Adjust resolution of the glyph (higher value generates smoother curved lines but visualization may be slower)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:309: d->GlyphResolutionLabel2D->setVisible(sphereGlyph);`
- API footprints: `GetGlyphResolution2D`

## widget: GlyphResolution2D

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Adjust resolution of arrow (lower is less detailed but rendered faster) | GlyphResolution2D | ctkSliderWidget
- Tooltip: Adjust resolution of arrow (lower is less detailed but rendered faster)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:186: QObject::connect(this->GlyphResolution2D, SIGNAL(valueChanged(double)), q, SLOT(setGlyphResolution2D(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:307: d->GlyphResolution2D->setValue(d->TransformDisplayNode->GetGlyphResolution2D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:308: d->GlyphResolution2D->setVisible(sphereGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:628: void qMRMLTransformDisplayNodeWidget::setGlyphResolution2D(double resolution)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:635: d->TransformDisplayNode->SetGlyphResolution2D(static_cast<int>(resolution));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:78: void setGlyphResolution2D(double resolution);`
- Connected slots/functions: `setGlyphResolution2D`
- API footprints: `GetGlyphResolution2D`, `SetGlyphResolution2D`

## widget: GlyphSourceOptions3D

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: GlyphSourceOptions3D | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:312: d->GlyphSourceOptions3D->setVisible(glyphMode);`
- API footprints: `GetGlyphDiameterMm`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: GlyphShaftDiameterPercent

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Diameter of the arrow shaft relative to the base diameter | GlyphShaftDiameterPercent | ctkSliderWidget
- Tooltip: Diameter of the arrow shaft relative to the base diameter
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:181: QObject::connect(this->GlyphShaftDiameterPercent, SIGNAL(valueChanged(double)), q, SLOT(setGlyphShaftDiameterPercent(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:319: d->GlyphShaftDiameterPercent->setValue(d->TransformDisplayNode->GetGlyphShaftDiameterPercent());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:321: d->GlyphShaftDiameterPercent->setVisible(arrowGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:730: void qMRMLTransformDisplayNodeWidget::setGlyphShaftDiameterPercent(double diameterPercent)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:737: d->TransformDisplayNode->SetGlyphShaftDiameterPercent(diameterPercent);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:75: void setGlyphShaftDiameterPercent(double diameterPercent);`
- Connected slots/functions: `setGlyphShaftDiameterPercent`
- API footprints: `GetGlyphResolution`, `GetGlyphShaftDiameterPercent`, `SetGlyphShaftDiameterPercent`

## widget: GlyphTipLengthPercent

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Length of the arrow tip  as percentage of displacement | GlyphTipLengthPercent | ctkSliderWidget
- Tooltip: Length of the arrow tip  as percentage of displacement
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:180: QObject::connect(this->GlyphTipLengthPercent, SIGNAL(valueChanged(double)), q, SLOT(setGlyphTipLengthPercent(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:185: QObject::connect(this->GlyphTipLengthPercent2D, SIGNAL(valueChanged(double)), q, SLOT(setGlyphTipLengthPercent2D(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:304: d->GlyphTipLengthPercent2D->setValue(d->TransformDisplayNode->GetGlyphTipLengthPercent2D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:305: d->GlyphTipLengthPercent2D->setVisible(arrowGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:316: d->GlyphTipLengthPercent->setValue(d->TransformDisplayNode->GetGlyphTipLengthPercent());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:318: d->GlyphTipLengthPercent->setVisible(arrowGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:639: void qMRMLTransformDisplayNodeWidget::setGlyphTipLengthPercent2D(double lengthPercent)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:646: d->TransformDisplayNode->SetGlyphTipLengthPercent2D(lengthPercent);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:708: void qMRMLTransformDisplayNodeWidget::setGlyphTipLengthPercent(double length)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:715: d->TransformDisplayNode->SetGlyphTipLengthPercent(length);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:73: void setGlyphTipLengthPercent(double length);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:79: void setGlyphTipLengthPercent2D(double lengthPercent);`
- Connected slots/functions: `setGlyphTipLengthPercent`, `setGlyphTipLengthPercent2D`
- API footprints: `GetGlyphResolution2D`, `GetGlyphShaftDiameterPercent`, `GetGlyphTipLengthPercent`, `GetGlyphTipLengthPercent2D`, `SetGlyphTipLengthPercent`, `SetGlyphTipLengthPercent2D`

## widget: GlyphDiameterMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Base diameter of the widget | GlyphDiameterMm | qMRMLSliderWidget
- Tooltip: Base diameter of the widget
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:179: QObject::connect(this->GlyphDiameterMm, SIGNAL(valueChanged(double)), q, SLOT(setGlyphDiameterMm(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:313: d->GlyphDiameterMm->setValue(d->TransformDisplayNode->GetGlyphDiameterMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:314: d->GlyphDiameterMmLabel->setVisible(arrowGlyph || coneGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:315: d->GlyphDiameterMm->setVisible(arrowGlyph || coneGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:719: void qMRMLTransformDisplayNodeWidget::setGlyphDiameterMm(double diameterMm)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:726: d->TransformDisplayNode->SetGlyphDiameterMm(diameterMm);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:74: void setGlyphDiameterMm(double diameterMm);`
- Connected slots/functions: `setGlyphDiameterMm`
- API footprints: `GetGlyphDiameterMm`, `GetGlyphTipLengthPercent`, `SetGlyphDiameterMm`

## widget: GlyphResolution

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Adjust resolution of arrow (lower is less detailed but rendered faster) | GlyphResolution | ctkSliderWidget
- Tooltip: Adjust resolution of arrow (lower is less detailed but rendered faster)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:182: QObject::connect(this->GlyphResolution, SIGNAL(valueChanged(double)), q, SLOT(setGlyphResolution(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:186: QObject::connect(this->GlyphResolution2D, SIGNAL(valueChanged(double)), q, SLOT(setGlyphResolution2D(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:307: d->GlyphResolution2D->setValue(d->TransformDisplayNode->GetGlyphResolution2D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:308: d->GlyphResolution2D->setVisible(sphereGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:309: d->GlyphResolutionLabel2D->setVisible(sphereGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:322: d->GlyphResolution->setValue(d->TransformDisplayNode->GetGlyphResolution());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:628: void qMRMLTransformDisplayNodeWidget::setGlyphResolution2D(double resolution)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:635: d->TransformDisplayNode->SetGlyphResolution2D(static_cast<int>(resolution));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:741: void qMRMLTransformDisplayNodeWidget::setGlyphResolution(double resolution)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:748: d->TransformDisplayNode->SetGlyphResolution(static_cast<int>(resolution));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:76: void setGlyphResolution(double resolution);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:78: void setGlyphResolution2D(double resolution);`
- Connected slots/functions: `setGlyphResolution`, `setGlyphResolution2D`
- API footprints: `GetGlyphResolution`, `GetGlyphResolution2D`, `SetGlyphResolution`, `SetGlyphResolution2D`

## widget: GlyphShaftDiameterLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Shaft diameter: | Adjust radius of arrow shaft | GlyphShaftDiameterLabel | QLabel
- Text: Shaft diameter:
- Tooltip: Adjust radius of arrow shaft
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:320: d->GlyphShaftDiameterLabel->setVisible(arrowGlyph);`
- API footprints: `GetGlyphResolution`, `GetGlyphShaftDiameterPercent`

## widget: GlyphResolutionLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Resolution: | Adjust resolution of the glyph (higher value generates smoother curved lines but visualization may be slower) | GlyphResolutionLabel | QLabel
- Text: Resolution:
- Tooltip: Adjust resolution of the glyph (higher value generates smoother curved lines but visualization may be slower)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:309: d->GlyphResolutionLabel2D->setVisible(sphereGlyph);`
- API footprints: `GetGlyphResolution2D`

## widget: GlyphTipLengthLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Tip length: | Adjust how much of the tip the arrow will consist of as a decimal percentage | GlyphTipLengthLabel | QLabel
- Text: Tip length:
- Tooltip: Adjust how much of the tip the arrow will consist of as a decimal percentage
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:306: d->GlyphTipLengthLabel2D->setVisible(arrowGlyph);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:317: d->GlyphTipLengthLabel->setVisible(arrowGlyph);`
- API footprints: `GetGlyphResolution2D`, `GetGlyphShaftDiameterPercent`, `GetGlyphTipLengthPercent`, `GetGlyphTipLengthPercent2D`

## widget: GlyphDiameterMmLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Diameter: | Adjust radius of base of arrow tip | GlyphDiameterMmLabel | QLabel
- Text: Diameter:
- Tooltip: Adjust radius of base of arrow tip
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:314: d->GlyphDiameterMmLabel->setVisible(arrowGlyph || coneGlyph);`
- API footprints: `GetGlyphDiameterMm`, `GetGlyphTipLengthPercent`

## widget: GlyphOptions_2

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: GlyphOptions_2 | QFrame
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: GridSpacingLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Spacing: | Distance between the gridlines | GridSpacingLabel | QLabel
- Text: Spacing:
- Tooltip: Distance between the gridlines
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:330: d->GridSpacingLabel->setVisible(gridMode);`
- API footprints: `GetGridLineDiameterMm`, `GetGridSpacingMm`

## widget: GridSpacingMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Distance between the gridlines | GridSpacingMm | qMRMLSliderWidget
- Tooltip: Distance between the gridlines
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:190: QObject::connect(this->GridSpacingMm, SIGNAL(valueChanged(double)), q, SLOT(setGridSpacingMm(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:328: d->GridSpacingMm->setValue(d->TransformDisplayNode->GetGridSpacingMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:329: d->GridSpacingMm->setVisible(gridMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:763: void qMRMLTransformDisplayNodeWidget::setGridSpacingMm(double spacing)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:770: d->TransformDisplayNode->SetGridSpacingMm(spacing);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:81: void setGridSpacingMm(double spacing);`
- Connected slots/functions: `setGridSpacingMm`
- API footprints: `GetGridLineDiameterMm`, `GetGridSpacingMm`, `SetGridSpacingMm`

## widget: GridScaleLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Scale factor: | Percentage of displacement applied to the gridpoints. 100% means that the grid is deformed with the actual displacement. | GridScaleLabel | QLabel
- Text: Scale factor:
- Tooltip: Percentage of displacement applied to the gridpoints. 100% means that the grid is deformed with the actual displacement.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:327: d->GridScaleLabel->setVisible(gridMode);`
- API footprints: `GetGridScalePercent`, `GetGridSpacingMm`

## widget: GridScalePercent

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Percentage of displacement applied to the gridpoints. 100% means that the grid is deformed with the actual displacement. | GridScalePercent | ctkSliderWidget
- Tooltip: Percentage of displacement applied to the gridpoints. 100% means that the grid is deformed with the actual displacement.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:189: QObject::connect(this->GridScalePercent, SIGNAL(valueChanged(double)), q, SLOT(setGridScalePercent(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:325: d->GridScalePercent->setValue(d->TransformDisplayNode->GetGridScalePercent());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:326: d->GridScalePercent->setVisible(gridMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:752: void qMRMLTransformDisplayNodeWidget::setGridScalePercent(double scale)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:759: d->TransformDisplayNode->SetGridScalePercent(scale);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:80: void setGridScalePercent(double scale);`
- Connected slots/functions: `setGridScalePercent`
- API footprints: `GetGridScalePercent`, `GetGridSpacingMm`, `SetGridScalePercent`

## widget: GridShowNonWarpedLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Show original grid: | Show non-warped grid in the slice view | GridShowNonWarpedLabel | QLabel
- Text: Show original grid:
- Tooltip: Show non-warped grid in the slice view
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:339: d->GridShowNonWarpedLabel->setVisible(gridMode);`
- API footprints: `GetGridShowNonWarped`

## widget: GridShowNonWarped

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: Show non-warped grid in the slice view | GridShowNonWarped | ctkCheckBox
- Tooltip: Show non-warped grid in the slice view
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:193: QObject::connect(this->GridShowNonWarped, SIGNAL(toggled(bool)), q, SLOT(setGridShowNonWarped(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:337: d->GridShowNonWarped->setChecked(d->TransformDisplayNode->GetGridShowNonWarped());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:338: d->GridShowNonWarped->setVisible(gridMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:339: d->GridShowNonWarpedLabel->setVisible(gridMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:796: void qMRMLTransformDisplayNodeWidget::setGridShowNonWarped(bool show)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:803: d->TransformDisplayNode->SetGridShowNonWarped(show);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:84: void setGridShowNonWarped(bool show);`
- Connected slots/functions: `setGridShowNonWarped`
- API footprints: `GetGridShowNonWarped`, `SetGridShowNonWarped`

## widget: GridLineDiameterLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 3D gridline diameter: | Thickness of the gridlines in the 3D view | GridLineDiameterLabel | QLabel
- Text: 3D gridline diameter:
- Tooltip: Thickness of the gridlines in the 3D view
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:333: d->GridLineDiameterLabel->setVisible(gridMode);`
- API footprints: `GetGridLineDiameterMm`, `GetGridResolutionMm`

## widget: GridLineDiameterMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Thickness of the gridlines in the 3D view | GridLineDiameterMm | qMRMLSliderWidget
- Tooltip: Thickness of the gridlines in the 3D view
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:191: QObject::connect(this->GridLineDiameterMm, SIGNAL(valueChanged(double)), q, SLOT(setGridLineDiameterMm(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:331: d->GridLineDiameterMm->setValue(d->TransformDisplayNode->GetGridLineDiameterMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:332: d->GridLineDiameterMm->setVisible(gridMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:774: void qMRMLTransformDisplayNodeWidget::setGridLineDiameterMm(double diameterMm)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:781: d->TransformDisplayNode->SetGridLineDiameterMm(diameterMm);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:82: void setGridLineDiameterMm(double diameterMm);`
- Connected slots/functions: `setGridLineDiameterMm`
- API footprints: `GetGridLineDiameterMm`, `GetGridResolutionMm`, `SetGridLineDiameterMm`

## widget: GridResolutionLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Resolution: | Distance between sample points along the gridlines. Lower values result in gridlines that follow more closely the actual displacement vectors, but require more computation time. | GridResolutionLabel | QLabel
- Text: Resolution:
- Tooltip: Distance between sample points along the gridlines. Lower values result in gridlines that follow more closely the actual displacement vectors, but require more computation time.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:336: d->GridResolutionLabel->setVisible(gridMode);`
- API footprints: `GetGridResolutionMm`, `GetGridShowNonWarped`

## widget: GridResolutionMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Distance between sample points along the gridlines. Lower values result in gridlines that follow more closely the actual displacement vectors, but require more computation time. | GridResolutionMm | qMRMLSliderWidget
- Tooltip: Distance between sample points along the gridlines. Lower values result in gridlines that follow more closely the actual displacement vectors, but require more computation time.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:192: QObject::connect(this->GridResolutionMm, SIGNAL(valueChanged(double)), q, SLOT(setGridResolutionMm(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:334: d->GridResolutionMm->setValue(d->TransformDisplayNode->GetGridResolutionMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:335: d->GridResolutionMm->setVisible(gridMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:785: void qMRMLTransformDisplayNodeWidget::setGridResolutionMm(double resolutionMm)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:792: d->TransformDisplayNode->SetGridResolutionMm(resolutionMm);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:83: void setGridResolutionMm(double resolutionMm);`
- Connected slots/functions: `setGridResolutionMm`
- API footprints: `GetGridResolutionMm`, `GetGridShowNonWarped`, `SetGridResolutionMm`

## widget: ContourLevelsLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Levels (mm): | Values defining the isolines and isosurfaces to contour. Values are separated by spaces. | ContourLevelsLabel | QLabel
- Text: Levels (mm):
- Tooltip: Values defining the isolines and isosurfaces to contour. Values are separated by spaces.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:357: d->ContourLevelsLabel->setVisible(contourMode);`

## widget: ContourLevelsMm

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: 1 2 3 4 | Values defining the isolines and isosurfaces to contour. Values are separated by spaces. | ContourLevelsMm | QLineEdit
- Text: 1 2 3 4
- Tooltip: Values defining the isolines and isosurfaces to contour. Values are separated by spaces.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:197: this->ContourLevelsMm->setValidator(new QRegularExpressionValidator(rx, q));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:199: QObject::connect(this->ContourLevelsMm, SIGNAL(textChanged(QString)), q, SLOT(setContourLevelsMm(QString)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:349: std::vector<double> levelsInWidget = vtkMRMLTransformDisplayNode::ConvertContourLevelsFromString(d->ContourLevelsMm->text().toUtf8());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:351: d->TransformDisplayNode->GetContourLevelsMm(levelsInMRML);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:354: d->ContourLevelsMm->setText(QLatin1String(d->TransformDisplayNode->GetContourLevelsMmAsString().c_str()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:356: d->ContourLevelsMm->setVisible(contourMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:807: void qMRMLTransformDisplayNodeWidget::setContourLevelsMm(QString values_str)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:814: d->TransformDisplayNode->SetContourLevelsMmFromString(values_str.toUtf8());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:85: void setContourLevelsMm(QString values_str);`
- Connected slots/functions: `setContourLevelsMm`
- API footprints: `GetContourLevelsMm`, `GetContourLevelsMmAsString`, `SetContourLevelsMmFromString`, `vtkMRMLTransformDisplayNode::ConvertContourLevelsFromString`, `vtkMRMLTransformDisplayNode::IsContourLevelEqual`

## widget: ContourResolutionLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Resolution: | Sampling distance for discretizing the displacement field. Lower values result in more accurate contours, but require more computation time. | ContourResolutionLabel | QLabel
- Text: Resolution:
- Tooltip: Sampling distance for discretizing the displacement field. Lower values result in more accurate contours, but require more computation time.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:344: d->ContourResolutionLabel->setVisible(contourMode);`
- API footprints: `GetContourOpacity`, `GetContourResolutionMm`

## widget: ContourResolutionMm

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: Sampling distance for discretizing the displacement field. Lower values result in more accurate contours, but require more computation time. | ContourResolutionMm | qMRMLSliderWidget
- Tooltip: Sampling distance for discretizing the displacement field. Lower values result in more accurate contours, but require more computation time.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:200: QObject::connect(this->ContourResolutionMm, SIGNAL(valueChanged(double)), q, SLOT(setContourResolutionMm(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:342: d->ContourResolutionMm->setValue(d->TransformDisplayNode->GetContourResolutionMm());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:343: d->ContourResolutionMm->setVisible(contourMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:818: void qMRMLTransformDisplayNodeWidget::setContourResolutionMm(double resolutionMm)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:825: d->TransformDisplayNode->SetContourResolutionMm(resolutionMm);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:86: void setContourResolutionMm(double resolutionMm);`
- Connected slots/functions: `setContourResolutionMm`
- API footprints: `GetContourOpacity`, `GetContourResolutionMm`, `SetContourResolutionMm`

## widget: ContourOpacityLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 3D opacity: | Opacity of the contour isosurfaces in the 3D view | ContourOpacityLabel | QLabel
- Text: 3D opacity:
- Tooltip: Opacity of the contour isosurfaces in the 3D view
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:347: d->ContourOpacityLabel->setVisible(contourMode);`
- API footprints: `GetContourOpacity`, `vtkMRMLTransformDisplayNode::ConvertContourLevelsFromString`

## widget: ContourOpacityPercent

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Opacity of the contour isosurfaces in the 3D view | ContourOpacityPercent | ctkSliderWidget
- Tooltip: Opacity of the contour isosurfaces in the 3D view
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:201: QObject::connect(this->ContourOpacityPercent, SIGNAL(valueChanged(double)), q, SLOT(setContourOpacityPercent(double)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:345: d->ContourOpacityPercent->setValue(d->TransformDisplayNode->GetContourOpacity() * 100.0);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:346: d->ContourOpacityPercent->setVisible(contourMode);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:829: void qMRMLTransformDisplayNodeWidget::setContourOpacityPercent(double opacityPercent)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h:87: void setContourOpacityPercent(double opacity);`
- Connected slots/functions: `setContourOpacityPercent`
- API footprints: `GetContourOpacity`, `SetContourOpacity`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility in 3D view: | label_4 | QLabel
- Text: Visibility in 3D view:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: Visible2dCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show transform in the slice views | Visible2dCheckBox | QCheckBox
- Tooltip: Show transform in the slice views
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:112: QObject::connect(this->InteractionVisible2dCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorVisibility2d(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:160: QObject::connect(this->Visible2dCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility2d(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:260: d->Visible2dCheckBox->setChecked(d->TransformDisplayNode->GetVisibility2D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:383: wasBlocking = d->InteractionVisible2dCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:384: d->InteractionVisible2dCheckBox->setChecked(d->TransformDisplayNode->GetEditorSliceIntersectionVisibility());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:385: d->InteractionVisible2dCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setEditorVisibility2d`, `setVisibility2d`
- API footprints: `GetEditorSliceIntersectionVisibility`, `GetVisibility`, `GetVisibility2D`, `GetVisibility3D`, `SetEditorSliceIntersectionVisibility`, `SetVisibility2D`
- Key UI properties: {"checked": "true"}

## widget: label_6

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | label_6 | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility in slice view: | label_3 | QLabel
- Text: Visibility in slice view:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: InteractionCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: InteractionCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Key UI properties: {"checked": "true"}

## widget: InteractionVisible2dCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: InteractionVisible2dCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:112: QObject::connect(this->InteractionVisible2dCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorVisibility2d(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:383: wasBlocking = d->InteractionVisible2dCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:384: d->InteractionVisible2dCheckBox->setChecked(d->TransformDisplayNode->GetEditorSliceIntersectionVisibility());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:385: d->InteractionVisible2dCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setEditorVisibility2d`
- API footprints: `GetEditorSliceIntersectionVisibility`, `SetEditorSliceIntersectionVisibility`

## widget: InteractiveAdvancedOptions3DFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: InteractiveAdvancedOptions3DFrame | QFrame
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:154: this->InteractiveAdvancedOptions3DFrame->hide();`

## widget: InteractiveScaling3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable scaling by manipulating 3D widget (left click and drag the handle at the center of widget face) | InteractiveScaling3DCheckBox | QCheckBox
- Tooltip: Enable scaling by manipulating 3D widget (left click and drag the handle at the center of widget face)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:116: QObject::connect(this->InteractiveScaling3DCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorScalingEnabled(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:471: wasBlocking = d->InteractiveScaling3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:473: d->InteractiveScaling3DCheckBox->setChecked(scalingEnabled);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:474: d->InteractiveScaling3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:475: d->InteractiveScaling3DCheckBox->setEnabled(enabled3D);`
- Connected slots/functions: `setEditorScalingEnabled`
- API footprints: `GetEditorScalingEnabled`, `SetEditorScalingEnabled`
- Key UI properties: {"checked": "true"}

## widget: translateX3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateX3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:122: QObject::connect(this->translateX3DCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:419: wasBlocking = d->translateX3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:420: d->translateX3DCheckBox->setChecked(translationComponentVisibility[0]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:421: d->translateX3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:422: d->translateX3DCheckBox->setEnabled(translationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1096: d->translateX3DCheckBox->isChecked(), d->translateY3DCheckBox->isChecked(), d->translateZ3DCheckBox->isChecked(), d->translateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `GetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: label_13

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y | label_13 | QLabel
- Text: Y
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: rotateX3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateX3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:127: QObject::connect(this->rotateX3DCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:449: wasBlocking = d->rotateX3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:450: d->rotateX3DCheckBox->setChecked(rotationComponentVisibility[0]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:451: d->rotateX3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:452: d->rotateX3DCheckBox->setEnabled(rotationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1117: d->rotateX3DCheckBox->isChecked(), d->rotateY3DCheckBox->isChecked(), d->rotateZ3DCheckBox->isChecked(), d->rotateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `GetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: scaleViewPlane3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleViewPlane3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:135: QObject::connect(this->scaleViewPlane3DCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:494: wasBlocking = d->scaleViewPlane3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:495: d->scaleViewPlane3DCheckBox->setChecked(scalingComponentVisibility[3]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:496: d->scaleViewPlane3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:497: d->scaleViewPlane3DCheckBox->setEnabled(scalingEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1137: bool componentVisibility[4] = { d->scaleX3DCheckBox->isChecked(), d->scaleY3DCheckBox->isChecked(), d->scaleZ3DCheckBox->isChecked(), d->scaleViewPlane3DCheckBox->isChecked() };`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: translateViewPlane3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateViewPlane3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:125: QObject::connect(this->translateViewPlane3DCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:434: wasBlocking = d->translateViewPlane3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:435: d->translateViewPlane3DCheckBox->setChecked(translationComponentVisibility[3]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:436: d->translateViewPlane3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:437: d->translateViewPlane3DCheckBox->setEnabled(translationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1096: d->translateX3DCheckBox->isChecked(), d->translateY3DCheckBox->isChecked(), d->translateZ3DCheckBox->isChecked(), d->translateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: label_15

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View plane | label_15 | QLabel
- Text: View plane
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: scaleX3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleX3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:132: QObject::connect(this->scaleX3DCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:479: wasBlocking = d->scaleX3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:480: d->scaleX3DCheckBox->setChecked(scalingComponentVisibility[0]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:481: d->scaleX3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:482: d->scaleX3DCheckBox->setEnabled(scalingEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1137: bool componentVisibility[4] = { d->scaleX3DCheckBox->isChecked(), d->scaleY3DCheckBox->isChecked(), d->scaleZ3DCheckBox->isChecked(), d->scaleViewPlane3DCheckBox->isChecked() };`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `GetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: InteractiveRotationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable rotation:  | InteractiveRotationLabel | QLabel
- Text: Enable rotation: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: translateZ3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateZ3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:124: QObject::connect(this->translateZ3DCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:429: wasBlocking = d->translateZ3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:430: d->translateZ3DCheckBox->setChecked(translationComponentVisibility[2]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:431: d->translateZ3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:432: d->translateZ3DCheckBox->setEnabled(translationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1096: d->translateX3DCheckBox->isChecked(), d->translateY3DCheckBox->isChecked(), d->translateZ3DCheckBox->isChecked(), d->translateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: rotateY3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateY3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:128: QObject::connect(this->rotateY3DCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:454: wasBlocking = d->rotateY3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:455: d->rotateY3DCheckBox->setChecked(rotationComponentVisibility[1]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:456: d->rotateY3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:457: d->rotateY3DCheckBox->setEnabled(rotationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1117: d->rotateX3DCheckBox->isChecked(), d->rotateY3DCheckBox->isChecked(), d->rotateZ3DCheckBox->isChecked(), d->rotateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: label_14

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Z | label_14 | QLabel
- Text: Z
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: translateY3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateY3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:123: QObject::connect(this->translateY3DCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:424: wasBlocking = d->translateY3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:425: d->translateY3DCheckBox->setChecked(translationComponentVisibility[1]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:426: d->translateY3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:427: d->translateY3DCheckBox->setEnabled(translationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1096: d->translateX3DCheckBox->isChecked(), d->translateY3DCheckBox->isChecked(), d->translateZ3DCheckBox->isChecked(), d->translateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: InteractiveRotation3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable translating by manipulating 3D widget (left click and drag anywhere on the widget face) | InteractiveRotation3DCheckBox | QCheckBox
- Tooltip: Enable translating by manipulating 3D widget (left click and drag anywhere on the widget face)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:115: QObject::connect(this->InteractiveRotation3DCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorRotationEnabled(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:441: wasBlocking = d->InteractiveRotation3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:443: d->InteractiveRotation3DCheckBox->setChecked(rotationEnabled);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:444: d->InteractiveRotation3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:445: d->InteractiveRotation3DCheckBox->setEnabled(enabled3D);`
- Connected slots/functions: `setEditorRotationEnabled`
- API footprints: `GetEditorRotationEnabled`, `SetEditorRotationEnabled`
- Key UI properties: {"checked": "true"}

## widget: rotateZ3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateZ3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:129: QObject::connect(this->rotateZ3DCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:459: wasBlocking = d->rotateZ3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:460: d->rotateZ3DCheckBox->setChecked(rotationComponentVisibility[2]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:461: d->rotateZ3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:462: d->rotateZ3DCheckBox->setEnabled(rotationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1117: d->rotateX3DCheckBox->isChecked(), d->rotateY3DCheckBox->isChecked(), d->rotateZ3DCheckBox->isChecked(), d->rotateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: label_12

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X | label_12 | QLabel
- Text: X
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: InteractiveScalingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable scaling:  | InteractiveScalingLabel | QLabel
- Text: Enable scaling: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: rotateViewPlane3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateViewPlane3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:130: QObject::connect(this->rotateViewPlane3DCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:464: wasBlocking = d->rotateViewPlane3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:465: d->rotateViewPlane3DCheckBox->setChecked(rotationComponentVisibility[3]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:466: d->rotateViewPlane3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:467: d->rotateViewPlane3DCheckBox->setEnabled(rotationEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1117: d->rotateX3DCheckBox->isChecked(), d->rotateY3DCheckBox->isChecked(), d->rotateZ3DCheckBox->isChecked(), d->rotateViewPlane3DCheckBox->isChecked()`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: scaleZ3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleZ3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:134: QObject::connect(this->scaleZ3DCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:489: wasBlocking = d->scaleZ3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:490: d->scaleZ3DCheckBox->setChecked(scalingComponentVisibility[2]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:491: d->scaleZ3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:492: d->scaleZ3DCheckBox->setEnabled(scalingEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1137: bool componentVisibility[4] = { d->scaleX3DCheckBox->isChecked(), d->scaleY3DCheckBox->isChecked(), d->scaleZ3DCheckBox->isChecked(), d->scaleViewPlane3DCheckBox->isChecked() };`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: InteractiveTranslation3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable scaling by manipulating 3D widget (shift +left click and drag the handle at the center of widget face, or left click and drag the center handle) | InteractiveTranslation3DCheckBox | QCheckBox
- Tooltip: Enable scaling by manipulating 3D widget (shift +left click and drag the handle at the center of widget face, or left click and drag the center handle)
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:114: QObject::connect(this->InteractiveTranslation3DCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorTranslationEnabled(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:411: wasBlocking = d->InteractiveTranslation3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:413: d->InteractiveTranslation3DCheckBox->setChecked(translationEnabled);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:414: d->InteractiveTranslation3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:415: d->InteractiveTranslation3DCheckBox->setEnabled(enabled3D);`
- Connected slots/functions: `setEditorTranslationEnabled`
- API footprints: `GetEditorTranslationEnabled`, `SetEditorTranslationEnabled`
- Key UI properties: {"checked": "true"}

## widget: InteractiveTranslationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable translation:  | InteractiveTranslationLabel | QLabel
- Text: Enable translation: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: scaleY3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleY3DCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:133: QObject::connect(this->scaleY3DCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:484: wasBlocking = d->scaleY3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:485: d->scaleY3DCheckBox->setChecked(scalingComponentVisibility[1]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:486: d->scaleY3DCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:487: d->scaleY3DCheckBox->setEnabled(scalingEnabled && enabled3D);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1137: bool componentVisibility[4] = { d->scaleX3DCheckBox->isChecked(), d->scaleY3DCheckBox->isChecked(), d->scaleZ3DCheckBox->isChecked(), d->scaleViewPlane3DCheckBox->isChecked() };`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: label_17

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility in 3D view: | label_17 | QLabel
- Text: Visibility in 3D view:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: InteractionVisibleCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show/Hide the transform widget in the 3D view. | InteractionVisibleCheckBox | QCheckBox
- Tooltip: Show/Hide the transform widget in the 3D view.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:110: QObject::connect(this->InteractionVisibleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorVisibility(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:375: wasBlocking = d->InteractionVisibleCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:376: d->InteractionVisibleCheckBox->setChecked(d->TransformDisplayNode->GetEditorVisibility());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:377: d->InteractionVisibleCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setEditorVisibility`
- API footprints: `GetEditorVisibility`, `SetEditorVisibility`
- Key UI properties: {"checked": "false"}

## widget: InteractionVisibleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility:  | InteractionVisibleLabel | QLabel
- Text: Visibility: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: label_9

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility in slice view: | label_9 | QLabel
- Text: Visibility in slice view:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: InteractionVisible3dCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: InteractionVisible3dCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:111: QObject::connect(this->InteractionVisible3dCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorVisibility3d(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:379: wasBlocking = d->InteractionVisible3dCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:380: d->InteractionVisible3dCheckBox->setChecked(d->TransformDisplayNode->GetEditorVisibility3D());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:381: d->InteractionVisible3dCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setEditorVisibility3d`
- API footprints: `GetEditorVisibility3D`, `SetEditorVisibility3D`

## widget: ShowInteractionAdvancedOptionsButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: More options... | ShowInteractionAdvancedOptionsButton | QPushButton
- Text: More options...
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Connected slots/functions: `setVisible`
- Declared UI connections: `toggled(bool) -> InteractiveAdvancedOptions3DFrame.setVisible(bool)`; `toggled(bool) -> InteractiveAdvancedOptionsSliceFrame.setVisible(bool)`
- Key UI properties: {"checkable": "true"}

## widget: InteractiveAdvancedOptionsSliceFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: InteractiveAdvancedOptionsSliceFrame | QFrame
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:155: this->InteractiveAdvancedOptionsSliceFrame->hide();`

## widget: label_22

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable rotation:  | label_22 | QLabel
- Text: Enable rotation: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: InteractiveTranslationSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: InteractiveTranslationSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:118: QObject::connect(this->InteractiveTranslationSliceCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorTranslationSliceEnabled(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:516: wasBlocking = d->InteractiveTranslationSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:518: d->InteractiveTranslationSliceCheckBox->setChecked(translationEnabled);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:519: d->InteractiveTranslationSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:520: d->InteractiveTranslationSliceCheckBox->setEnabled(enabledSlice);`
- Connected slots/functions: `setEditorTranslationSliceEnabled`
- API footprints: `GetEditorTranslationSliceEnabled`, `SetEditorTranslationSliceEnabled`

## widget: label_21

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable translation:  | label_21 | QLabel
- Text: Enable translation: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: translateZSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateZSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:139: QObject::connect(this->translateZSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:534: wasBlocking = d->translateZSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:535: d->translateZSliceCheckBox->setChecked(translationComponentVisibility[2]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:536: d->translateZSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:537: d->translateZSliceCheckBox->setEnabled(translationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1102: componentVisibility[2] = d->translateZSliceCheckBox->isChecked();`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: rotateYSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateYSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:143: QObject::connect(this->rotateYSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:559: wasBlocking = d->rotateYSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:560: d->rotateYSliceCheckBox->setChecked(rotationComponentVisibility[1]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:561: d->rotateYSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:562: d->rotateYSliceCheckBox->setEnabled(rotationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1122: componentVisibility[1] = d->rotateYSliceCheckBox->isChecked();`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: InteractiveScalingSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: InteractiveScalingSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:120: QObject::connect(this->InteractiveScalingSliceCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorScalingSliceEnabled(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:576: wasBlocking = d->InteractiveScalingSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:578: d->InteractiveScalingSliceCheckBox->setChecked(scalingEnabled);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:579: d->InteractiveScalingSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:580: d->InteractiveScalingSliceCheckBox->setEnabled(enabledSlice);`
- Connected slots/functions: `setEditorScalingSliceEnabled`
- API footprints: `GetEditorScalingSliceEnabled`, `SetEditorScalingSliceEnabled`

## widget: rotateViewPlaneSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateViewPlaneSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:145: QObject::connect(this->rotateViewPlaneSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:569: wasBlocking = d->rotateViewPlaneSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:570: d->rotateViewPlaneSliceCheckBox->setChecked(rotationComponentVisibility[3]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:571: d->rotateViewPlaneSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:572: d->rotateViewPlaneSliceCheckBox->setEnabled(rotationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1124: componentVisibility[3] = d->rotateViewPlaneSliceCheckBox->isChecked();`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: scaleYSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleYSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:148: QObject::connect(this->scaleYSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:589: wasBlocking = d->scaleYSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:590: d->scaleYSliceCheckBox->setChecked(scalingComponentVisibility[1]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:591: d->scaleYSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:592: d->scaleYSliceCheckBox->setEnabled(scalingEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1141: componentVisibility[1] = d->scaleYSliceCheckBox->isChecked();`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: translateXSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateXSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:137: QObject::connect(this->translateXSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:524: wasBlocking = d->translateXSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:525: d->translateXSliceCheckBox->setChecked(translationComponentVisibility[0]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:526: d->translateXSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:527: d->translateXSliceCheckBox->setEnabled(translationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1100: componentVisibility[0] = d->translateXSliceCheckBox->isChecked();`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `GetTranslationHandleComponentVisibilitySlice`, `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: InteractiveRotationSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: InteractiveRotationSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:119: QObject::connect(this->InteractiveRotationSliceCheckBox, SIGNAL(toggled(bool)), q, SLOT(setEditorRotationSliceEnabled(bool)));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:546: wasBlocking = d->InteractiveRotationSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:548: d->InteractiveRotationSliceCheckBox->setChecked(rotationEnabled);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:549: d->InteractiveRotationSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:550: d->InteractiveRotationSliceCheckBox->setEnabled(enabledSlice);`
- Connected slots/functions: `setEditorRotationSliceEnabled`
- API footprints: `GetEditorRotationSliceEnabled`, `SetEditorRotationSliceEnabled`

## widget: scaleZSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleZSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:149: QObject::connect(this->scaleZSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:594: wasBlocking = d->scaleZSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:595: d->scaleZSliceCheckBox->setChecked(scalingComponentVisibility[2]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:596: d->scaleZSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:597: d->scaleZSliceCheckBox->setEnabled(scalingEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1142: componentVisibility[2] = d->scaleZSliceCheckBox->isChecked();`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: scaleXSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleXSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:147: QObject::connect(this->scaleXSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:584: wasBlocking = d->scaleXSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:585: d->scaleXSliceCheckBox->setChecked(scalingComponentVisibility[0]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:586: d->scaleXSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:587: d->scaleXSliceCheckBox->setEnabled(scalingEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1140: componentVisibility[0] = d->scaleXSliceCheckBox->isChecked();`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `GetScaleHandleComponentVisibilitySlice`, `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: translateViewPlaneSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateViewPlaneSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:140: QObject::connect(this->translateViewPlaneSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:539: wasBlocking = d->translateViewPlaneSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:540: d->translateViewPlaneSliceCheckBox->setChecked(translationComponentVisibility[3]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:541: d->translateViewPlaneSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:542: d->translateViewPlaneSliceCheckBox->setEnabled(translationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1103: componentVisibility[3] = d->translateViewPlaneSliceCheckBox->isChecked();`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: label_23

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable scaling:  | label_23 | QLabel
- Text: Enable scaling: 
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: rotateZSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateZSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:144: QObject::connect(this->rotateZSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:564: wasBlocking = d->rotateZSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:565: d->rotateZSliceCheckBox->setChecked(rotationComponentVisibility[2]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:566: d->rotateZSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:567: d->rotateZSliceCheckBox->setEnabled(rotationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1123: componentVisibility[2] = d->rotateZSliceCheckBox->isChecked();`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: scaleViewPlaneSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: scaleViewPlaneSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:150: QObject::connect(this->scaleViewPlaneSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateScalingComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:599: wasBlocking = d->scaleViewPlaneSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:600: d->scaleViewPlaneSliceCheckBox->setChecked(scalingComponentVisibility[3]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:601: d->scaleViewPlaneSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:602: d->scaleViewPlaneSliceCheckBox->setEnabled(scalingEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1143: componentVisibility[3] = d->scaleViewPlaneSliceCheckBox->isChecked();`
- Connected slots/functions: `updateScalingComponentVisibility`
- API footprints: `SetScaleHandleComponentVisibility3D`, `SetScaleHandleComponentVisibilitySlice`

## widget: rotateXSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: rotateXSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:142: QObject::connect(this->rotateXSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateRotationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:554: wasBlocking = d->rotateXSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:555: d->rotateXSliceCheckBox->setChecked(rotationComponentVisibility[0]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:556: d->rotateXSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:557: d->rotateXSliceCheckBox->setEnabled(rotationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1121: componentVisibility[0] = d->rotateXSliceCheckBox->isChecked();`
- Connected slots/functions: `updateRotationComponentVisibility`
- API footprints: `GetRotationHandleComponentVisibilitySlice`, `SetRotationHandleComponentVisibility3D`, `SetRotationHandleComponentVisibilitySlice`

## widget: translateYSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: translateYSliceCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:138: QObject::connect(this->translateYSliceCheckBox, SIGNAL(clicked()), q, SLOT(updateTranslationComponentVisibility()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:529: wasBlocking = d->translateYSliceCheckBox->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:530: d->translateYSliceCheckBox->setChecked(translationComponentVisibility[1]);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:531: d->translateYSliceCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:532: d->translateYSliceCheckBox->setEnabled(translationEnabled && enabledSlice);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1101: componentVisibility[1] = d->translateYSliceCheckBox->isChecked();`
- Connected slots/functions: `updateTranslationComponentVisibility`
- API footprints: `SetTranslationHandleComponentVisibility3D`, `SetTranslationHandleComponentVisibilitySlice`

## widget: label_11

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X | label_11 | QLabel
- Text: X
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: label_16

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y | label_16 | QLabel
- Text: Y
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: label_18

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Z | label_18 | QLabel
- Text: Z
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: label_19

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View plane | label_19 | QLabel
- Text: View plane
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: label_20

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Size: | label_20 | QLabel
- Text: Size:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`

## widget: interactionHandleScaleSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: interactionHandleScaleSlider | qMRMLSliderWidget
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:152: QObject::connect(this->interactionHandleScaleSlider, SIGNAL(valueChanged(double)), q, SLOT(updateInteractionHandleScale()));`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:387: wasBlocking = d->interactionHandleScaleSlider->blockSignals(true);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:388: d->interactionHandleScaleSlider->setValue(d->TransformDisplayNode->GetInteractionScalePercent());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:389: d->interactionHandleScaleSlider->blockSignals(wasBlocking);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformDisplayNodeWidget.cxx:1156: double scale = d->interactionHandleScaleSlider->value();`
- Connected slots/functions: `updateInteractionHandleScale`
- API footprints: `GetInteractionScalePercent`, `SetInteractionScalePercent`
