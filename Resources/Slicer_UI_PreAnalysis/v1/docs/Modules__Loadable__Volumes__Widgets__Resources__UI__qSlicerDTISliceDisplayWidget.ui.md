# Slicer UI Analysis: Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerDTISliceDisplayWidget.ui

- Owner class: `qSlicerDTISliceDisplayWidget`
- UI file: `Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerDTISliceDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerDTISliceDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerDTISliceDisplayWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:21: #include "qSlicerDTISliceDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:22: #include "ui_qSlicerDTISliceDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:37: class qSlicerDTISliceDisplayWidgetPrivate : public Ui_qSlicerDTISliceDisplayWidget`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:39: Q_DECLARE_PUBLIC(qSlicerDTISliceDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:42: qSlicerDTISliceDisplayWidget* const q_ptr;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:45: qSlicerDTISliceDisplayWidgetPrivate(qSlicerDTISliceDisplayWidget& object);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:46: ~qSlicerDTISliceDisplayWidgetPrivate();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:53: qSlicerDTISliceDisplayWidgetPrivate::qSlicerDTISliceDisplayWidgetPrivate(qSlicerDTISliceDisplayWidget& object)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:59: qSlicerDTISliceDisplayWidgetPrivate ::~qSlicerDTISliceDisplayWidgetPrivate() = default;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:62: void qSlicerDTISliceDisplayWidgetPrivate::init()`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:64: Q_Q(qSlicerDTISliceDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:86: void qSlicerDTISliceDisplayWidgetPrivate::computeScalarBounds(double scalarBounds[2])`
- API footprints: `GetColorGlyphBy`, `GetDiffusionTensorDisplayPropertiesNode`, `vtkMRMLDiffusionTensorVolumeSliceDisplayNode::SafeDownCast`

## widget: GlyphVisibilityLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Visibility: | GlyphVisibilityLabel | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:353: return d->GlyphVisibilityLabel->isVisibleTo(const_cast<qSlicerDTISliceDisplayWidget*>(this));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:360: d->GlyphVisibilityLabel->setVisible(!hide);`

## widget: GlyphVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: GlyphVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:72: QObject::connect(this->GlyphVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:177: d->GlyphVisibilityCheckBox->setChecked(d->DisplayNode->GetVisibility());`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:361: d->GlyphVisibilityCheckBox->setVisible(!hide);`
- Connected slots/functions: `setVisibility`
- API footprints: `GetColorNode`, `GetOpacity`, `GetVisibility`, `SetVisibility`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::Minor`

## widget: GlypthOpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | GlypthOpacityLabel | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphOpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: GlyphOpacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:73: QObject::connect(this->GlyphOpacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setOpacity(double)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:178: d->GlyphOpacitySliderWidget->setValue(d->DisplayNode->GetOpacity());`
- Connected slots/functions: `setOpacity`
- API footprints: `GetAutoScalarRange`, `GetColorNode`, `GetOpacity`, `GetVisibility`, `SetOpacity`

## widget: GlyphColorTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar ColorMap: | GlyphColorTableLabel | QLabel
- Text: Scalar ColorMap:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphScalarColorTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: GlyphScalarColorTableComboBox | qMRMLColorTableComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:74: QObject::connect(this->GlyphScalarColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setColorMap(vtkMRMLNode*)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:179: d->GlyphScalarColorTableComboBox->setCurrentNode(d->DisplayNode->GetColorNode());`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:231: d->GlyphScalarColorTableComboBox->setEnabled(false);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:236: d->GlyphScalarColorTableComboBox->setEnabled(true);`
- Connected slots/functions: `setColorMap`
- API footprints: `AutoScalarRangeOn`, `GetAutoScalarRange`, `GetColorGlyphBy`, `GetColorNode`, `GetID`, `GetOpacity`, `GetVisibility`, `SetAndObserveColorNodeID`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientationMinEigenvector`

## widget: GlyphColorByScalarLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color by Scalar: | GlyphColorByScalarLabel | QLabel
- Text: Color by Scalar:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphColorByScalarComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLScalarInvariantComboBox`
- Search text: GlyphColorByScalarComboBox | qMRMLScalarInvariantComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:75: QObject::connect(this->GlyphColorByScalarComboBox, SIGNAL(scalarInvariantChanged(int)), q, SLOT(setColorGlyphBy(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:205: d->GlyphColorByScalarComboBox->setScalarInvariant(displayPropertiesNode->GetColorGlyphBy());`
- Connected slots/functions: `setColorGlyphBy`
- API footprints: `AutoScalarRangeOn`, `GetAutoScalarRange`, `GetColorGlyphBy`, `GetGlyphGeometry`, `GetGlyphScaleFactor`, `GetScalarRange`, `SetColorGlyphBy`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientation`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientationMiddleEigenvector`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientationMinEigenvector`

## widget: GlyphScalarRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar Range: | GlyphScalarRangeLabel | QLabel
- Text: Scalar Range:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphGeometryLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Glyph Type: | GlyphGeometryLabel | QLabel
- Text: Glyph Type:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphGeometryComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: GlyphGeometryComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:78: QObject::connect(this->GlyphGeometryComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setGlyphGeometry(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:206: d->GlyphGeometryComboBox->setCurrentIndex(displayPropertiesNode->GetGlyphGeometry());`
- Connected slots/functions: `setGlyphGeometry`
- API footprints: `GetColorGlyphBy`, `GetGlyphGeometry`, `GetGlyphScaleFactor`, `GetLineGlyphResolution`, `SetGlyphGeometry`

## widget: GlyphScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scale Factor: | GlyphScaleLabel | QLabel
- Text: Scale Factor:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: GlyphScaleSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:79: QObject::connect(this->GlyphScaleSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setGlyphScaleFactor(double)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:207: d->GlyphScaleSliderWidget->setValue(displayPropertiesNode->GetGlyphScaleFactor());`
- Connected slots/functions: `setGlyphScaleFactor`
- API footprints: `GetColorGlyphBy`, `GetGlyphEigenvector`, `GetGlyphGeometry`, `GetGlyphScaleFactor`, `GetLineGlyphResolution`, `SetGlyphScaleFactor`

## widget: GlyphSpacingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Spacing: | GlyphSpacingLabel | QLabel
- Text: Spacing:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphSpacingSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: GlyphSpacingSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:80: QObject::connect(this->GlyphSpacingSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setGlyphSpacing(double)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:208: d->GlyphSpacingSliderWidget->setValue(displayPropertiesNode->GetLineGlyphResolution());`
- Connected slots/functions: `setGlyphSpacing`
- API footprints: `GetGlyphEigenvector`, `GetGlyphGeometry`, `GetGlyphScaleFactor`, `GetLineGlyphResolution`, `SetLineGlyphResolution`

## widget: GlyphAdvancedPropertiesWidget

- Confidence: `ui_only`
- Widget/action class: `QStackedWidget`
- Search text: GlyphAdvancedPropertiesWidget | QStackedWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: LinePropertiesPage

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: LinePropertiesPage | QWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: LineEigenVectorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Glyph EigenVector: | LineEigenVectorLabel | QLabel
- Text: Glyph EigenVector:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: LineEigenVectorComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: LineEigenVectorComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:68: this->LineEigenVectorComboBox->setItemData(0, vtkMRMLDiffusionTensorDisplayPropertiesNode::Major);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:69: this->LineEigenVectorComboBox->setItemData(1, vtkMRMLDiffusionTensorDisplayPropertiesNode::Middle);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:70: this->LineEigenVectorComboBox->setItemData(2, vtkMRMLDiffusionTensorDisplayPropertiesNode::Minor);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:81: QObject::connect(this->LineEigenVectorComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setGlyphEigenVector(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:209: int index = d->LineEigenVectorComboBox->findData(QVariant(displayPropertiesNode->GetGlyphEigenvector()));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:210: d->LineEigenVectorComboBox->setCurrentIndex(index);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:345: int eigenVector = d->LineEigenVectorComboBox->itemData(index).toInt();`
- Connected slots/functions: `setGlyphEigenVector`
- API footprints: `GetGlyphEigenvector`, `GetGlyphScaleFactor`, `GetLineGlyphResolution`, `SetGlyphEigenvector`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::Major`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::Middle`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::Minor`

## widget: TubePropertiesPage

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: TubePropertiesPage | QWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: TubeEigenVectorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Glyph EigenVector: | TubeEigenVectorLabel | QLabel
- Text: Glyph EigenVector:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: TubeEigenVectorComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: TubeEigenVectorComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:82: QObject::connect(this->TubeEigenVectorComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setGlyphEigenVector(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:211: d->TubeEigenVectorComboBox->setCurrentIndex(index);`
- Connected slots/functions: `setGlyphEigenVector`
- API footprints: `GetGlyphEigenvector`, `SetGlyphEigenvector`

## widget: EllipsoidPropertiesPage

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: EllipsoidPropertiesPage | QWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`

## widget: GlyphManualScalarRangeCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Manual or Auto scalar range | GlyphManualScalarRangeCheckBox | QCheckBox
- Tooltip: Manual or Auto scalar range
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:76: QObject::connect(this->GlyphManualScalarRangeCheckBox, SIGNAL(toggled(bool)), q, SLOT(setManualScalarRange(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:180: d->GlyphManualScalarRangeCheckBox->setChecked(d->DisplayNode->GetAutoScalarRange() == 0);`
- Connected slots/functions: `setManualScalarRange`
- API footprints: `GetAutoScalarRange`, `GetColorNode`, `GetOpacity`, `SetAutoScalarRange`

## widget: GlyphScalarRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkRangeWidget`
- Search text: GlyphScalarRangeWidget | ctkRangeWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:77: QObject::connect(this->GlyphScalarRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(setScalarRange(double, double)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:193: d->GlyphScalarRangeWidget->blockSignals(true);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:194: d->GlyphScalarRangeWidget->setDecimals(decimals);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:195: d->GlyphScalarRangeWidget->setSingleStep(i);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:196: d->GlyphScalarRangeWidget->setRange(scalarBounds[0], scalarBounds[1]);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:197: d->GlyphScalarRangeWidget->blockSignals(false);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:200: d->GlyphScalarRangeWidget->setValues(scalarRange[0], scalarRange[1]);`
- Connected slots/functions: `setScalarRange`
- API footprints: `GetScalarRange`, `SetScalarRange`
