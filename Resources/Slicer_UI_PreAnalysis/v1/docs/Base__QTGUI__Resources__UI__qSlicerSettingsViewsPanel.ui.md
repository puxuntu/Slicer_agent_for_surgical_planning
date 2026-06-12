# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsViewsPanel.ui

- Owner class: `qSlicerSettingsViewsPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsViewsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsViewsPanel

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsViewsPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:25: #include "qSlicerSettingsViewsPanel.h"`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:26: #include "ui_qSlicerSettingsViewsPanel.h"`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:33: // qSlicerSettingsViewsPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:36: class qSlicerSettingsViewsPanelPrivate : public Ui_qSlicerSettingsViewsPanel`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:38: Q_DECLARE_PUBLIC(qSlicerSettingsViewsPanel);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:41: qSlicerSettingsViewsPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:44: qSlicerSettingsViewsPanelPrivate(qSlicerSettingsViewsPanel& object);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:49: // qSlicerSettingsViewsPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:52: qSlicerSettingsViewsPanelPrivate::qSlicerSettingsViewsPanelPrivate(qSlicerSettingsViewsPanel& object)`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:58: void qSlicerSettingsViewsPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:60: Q_Q(qSlicerSettingsViewsPanel);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:77: QObject::connect(this->MSAAComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::onMSAAChanged);`
- Connected slots/functions: `currentMSAAChanged`, `currentSliceOrientationMarkerSizeChanged`, `currentSliceOrientationMarkerTypeChanged`, `currentSliceRulerTypeChanged`, `currentTextChanged`, `currentThreeDOrientationMarkerSizeChanged`, `currentThreeDOrientationMarkerTypeChanged`, `currentThreeDRulerTypeChanged`, `onMSAAChanged`

## widget: scrollArea

- Confidence: `ui_only`
- Widget/action class: `QScrollArea`
- Search text: scrollArea | QScrollArea
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: scrollAreaWidgetContents

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: scrollAreaWidgetContents | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: CollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: SliceOrientationMarkerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Orientation marker: | SliceOrientationMarkerLabel | QLabel
- Text: Orientation marker:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: SliceOrientationMarkerTypeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: SliceOrientationMarkerTypeComboBox | ctkComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:82: this->SliceOrientationMarkerTypeComboBox->addItem(qSlicerSettingsViewsPanel::tr("none"), QString(/*no tr*/ "none"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:83: this->SliceOrientationMarkerTypeComboBox->addItem(qSlicerSettingsViewsPanel::tr("cube"), QString(/*no tr*/ "cube"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:84: this->SliceOrientationMarkerTypeComboBox->addItem(qSlicerSettingsViewsPanel::tr("human"), QString(/*no tr*/ "human"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:85: this->SliceOrientationMarkerTypeComboBox->addItem(qSlicerSettingsViewsPanel::tr("axes"), QString(/*no tr*/ "axes"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:87: QObject::connect(this->SliceOrientationMarkerTypeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentSliceOrientationMarkerTypeChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:249: return d->SliceOrientationMarkerTypeComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:257: d->SliceOrientationMarkerTypeComboBox->setCurrentIndex(qMax(d->SliceOrientationMarkerTypeComboBox->findText(text), 0));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:341: if (d->SliceOrientationMarkerTypeComboBox->currentData() == /*no tr*/ "none")`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:345: int index = d->SliceOrientationMarkerTypeComboBox->findData(/*no tr*/ "axes");`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:346: d->SliceOrientationMarkerTypeComboBox->setCurrentIndex(index);`
- Connected slots/functions: `currentSliceOrientationMarkerTypeChanged`, `currentTextChanged`

## widget: SliceOrientationMarkerSizeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: SliceOrientationMarkerSizeComboBox | ctkComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:94: QObject::connect(this->SliceOrientationMarkerSizeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentSliceOrientationMarkerSizeChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:264: return d->SliceOrientationMarkerSizeComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:272: d->SliceOrientationMarkerSizeComboBox->setCurrentIndex(qMax(d->SliceOrientationMarkerSizeComboBox->findText(text), 0));`
- Connected slots/functions: `currentSliceOrientationMarkerSizeChanged`, `currentTextChanged`

## widget: SliceRulerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Ruler: | SliceRulerLabel | QLabel
- Text: Ruler:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: SliceRulerTypeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: SliceRulerTypeComboBox | ctkComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:101: QObject::connect(this->SliceRulerTypeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentSliceRulerTypeChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:279: return d->SliceRulerTypeComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:287: d->SliceRulerTypeComboBox->setCurrentIndex(qMax(d->SliceRulerTypeComboBox->findText(text), 0));`
- Connected slots/functions: `currentSliceRulerTypeChanged`, `currentTextChanged`

## widget: SliceViewOrientationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View orientation: | SliceViewOrientationLabel | QLabel
- Text: View orientation:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: SliceViewOrientationComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: SliceViewOrientationComboBox | ctkComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:109: this->SliceViewOrientationComboBox->addItem(qSlicerSettingsViewsPanel::tr("patient right is screen left (default)"), QString("PatientRightIsScreenLeft"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:110: this->SliceViewOrientationComboBox->addItem(qSlicerSettingsViewsPanel::tr("patient right is screen right"), QString("PatientRightIsScreenRight"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:112: this->SliceViewOrientationComboBox,`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:117: QObject::connect(this->SliceViewOrientationComboBox, SIGNAL(activated(int)), q, SLOT(sliceViewOrientationChangedByUser()));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:339: if (d->SliceViewOrientationComboBox->currentUserDataAsString() == "PatientRightIsScreenRight")`
- Connected slots/functions: `sliceViewOrientationChangedByUser`

## widget: SliceViewOrientationLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show slice edge in 3D: | SliceViewOrientationLabel_2 | QLabel
- Text: Show slice edge in 3D:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: SliceEdgeVisibility3DCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCheckBox`
- Search text: Show colored frame around the slice when displayed in 3D views. | SliceEdgeVisibility3DCheckBox | ctkCheckBox
- Tooltip: Show colored frame around the slice when displayed in 3D views.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:120: this->SliceEdgeVisibility3DCheckBox,`
- Key UI properties: {"checked": "true"}

## widget: CollapsibleGroupBox_2

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_2 | ctkCollapsibleGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDBoxVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show 3D cube: | ThreeDBoxVisibilityLabel | QLabel
- Text: Show 3D cube:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDBoxVisibilityCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCheckBox`
- Search text: ThreeDBoxVisibilityCheckBox | ctkCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:127: this->ThreeDBoxVisibilityCheckBox,`
- Key UI properties: {"checked": "true"}

## widget: ThreeDAxisLabelsVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show 3D axis label: | ThreeDAxisLabelsVisibilityLabel | QLabel
- Text: Show 3D axis label:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDAxisLabelsVisibilityCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCheckBox`
- Search text: ThreeDAxisLabelsVisibilityCheckBox | ctkCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:132: this->ThreeDAxisLabelsVisibilityCheckBox,`
- Key UI properties: {"checked": "true"}

## widget: ThreeDOrientationMarkerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Orientation marker: | ThreeDOrientationMarkerLabel | QLabel
- Text: Orientation marker:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDOrientationMarkerTypeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: ThreeDOrientationMarkerTypeComboBox | ctkComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:136: QObject::connect(this->ThreeDOrientationMarkerTypeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentThreeDOrientationMarkerTypeChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:294: return d->ThreeDOrientationMarkerTypeComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:302: d->ThreeDOrientationMarkerTypeComboBox->setCurrentIndex(qMax(d->ThreeDOrientationMarkerTypeComboBox->findText(text), 0));`
- Connected slots/functions: `currentTextChanged`, `currentThreeDOrientationMarkerTypeChanged`

## widget: ThreeDOrientationMarkerSizeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: ThreeDOrientationMarkerSizeComboBox | ctkComboBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:143: QObject::connect(this->ThreeDOrientationMarkerSizeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentThreeDOrientationMarkerSizeChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:309: return d->ThreeDOrientationMarkerSizeComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:317: d->ThreeDOrientationMarkerSizeComboBox->setCurrentIndex(qMax(d->ThreeDOrientationMarkerSizeComboBox->findText(text), 0));`
- Connected slots/functions: `currentTextChanged`, `currentThreeDOrientationMarkerSizeChanged`

## widget: label

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Use orthographic projection: | label | QLabel
- Text: Use orthographic projection:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:135: qSlicerSettingsViewsPanel::tr("3D view axis label visibility"));`

## widget: ThreeDUseOrthographicProjectionCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCheckBox`
- Search text: ThreeDUseOrthographicProjectionCheckBox | ctkCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:163: this->ThreeDUseOrthographicProjectionCheckBox,`
- Connected slots/functions: `setEnabled`
- Declared UI connections: `toggled(bool) -> ThreeDRulerTypeComboBox.setEnabled(bool)`

## widget: ThreeDRulerTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Ruler: | ThreeDRulerTypeLabel | QLabel
- Text: Ruler:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDRulerTypeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkComboBox`
- Search text: Ruler is only displayed if orthographic projection mode is used. | ThreeDRulerTypeComboBox | ctkComboBox
- Tooltip: Ruler is only displayed if orthographic projection mode is used.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:150: QObject::connect(this->ThreeDRulerTypeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentThreeDRulerTypeChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:324: return d->ThreeDRulerTypeComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:332: d->ThreeDRulerTypeComboBox->setCurrentIndex(qMax(d->ThreeDRulerTypeComboBox->findText(text), 0));`
- Connected slots/functions: `currentTextChanged`, `currentThreeDRulerTypeChanged`

## widget: ThreeDUseDepthPeelingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use depth peeling: | ThreeDUseDepthPeelingLabel | QLabel
- Text: Use depth peeling:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDUseDepthPeelingCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCheckBox`
- Search text: Enabling depth peeling improves rendering of transparent models at the cost of higher computational cost. | ThreeDUseDepthPeelingCheckBox | ctkCheckBox
- Tooltip: Enabling depth peeling improves rendering of transparent models at the cost of higher computational cost.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:158: this->ThreeDUseDepthPeelingCheckBox,`
- Key UI properties: {"checked": "true"}

## widget: ThreeDShadowsVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Shadows visibility: | ThreeDShadowsVisibilityLabel | QLabel
- Text: Shadows visibility:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDShadowsVisibilityCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCheckBox`
- Search text: Show shadows by default to improve depth perception | ThreeDShadowsVisibilityCheckBox | ctkCheckBox
- Tooltip: Show shadows by default to improve depth perception
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:168: this->ThreeDShadowsVisibilityCheckBox,`
- Connected slots/functions: `setEnabled`
- Declared UI connections: `toggled(bool) -> ThreeDAmbientShadowsSizeScaleSlider.setEnabled(bool)`; `toggled(bool) -> ThreeDAmbientShadowsVolumeOpacityThresholdSlider.setEnabled(bool)`; `toggled(bool) -> ThreeDAmbientShadowsIntensityScaleSlider.setEnabled(bool)`; `toggled(bool) -> ThreeDAmbientShadowsIntensityShiftSlider.setEnabled(bool)`
- Key UI properties: {"checked": "false"}

## widget: ThreeDAmbientShadowsSizeScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Size scale: | ThreeDAmbientShadowsSizeScaleLabel | QLabel
- Text: Size scale:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDAmbientShadowsSizeScaleSlider

- Confidence: `linked_to_code`
- Widget/action class: `ctkSliderWidget`
- Search text: ThreeDAmbientShadowsSizeScaleSlider | ctkSliderWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:173: this->ThreeDAmbientShadowsSizeScaleSlider,`

## widget: ThreeDAmbientShadowsVolumeOpacityThresholdLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Volume opacity threshold: | ThreeDAmbientShadowsVolumeOpacityThresholdLabel | QLabel
- Text: Volume opacity threshold:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDAmbientShadowsVolumeOpacityThresholdSlider

- Confidence: `linked_to_code`
- Widget/action class: `ctkSliderWidget`
- Search text: ThreeDAmbientShadowsVolumeOpacityThresholdSlider | ctkSliderWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:178: this->ThreeDAmbientShadowsVolumeOpacityThresholdSlider,`

## widget: ThreeDAmbientShadowsIntensityScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Intensity scale: | ThreeDAmbientShadowsIntensityScaleLabel | QLabel
- Text: Intensity scale:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDAmbientShadowsIntensityScaleSlider

- Confidence: `linked_to_code`
- Widget/action class: `ctkSliderWidget`
- Search text: ThreeDAmbientShadowsIntensityScaleSlider | ctkSliderWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:183: this->ThreeDAmbientShadowsIntensityScaleSlider,`

## widget: ThreeDAmbientShadowsIntensityShiftLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Intensity offset: | ThreeDAmbientShadowsIntensityShiftLabel | QLabel
- Text: Intensity offset:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: ThreeDAmbientShadowsIntensityShiftSlider

- Confidence: `linked_to_code`
- Widget/action class: `ctkSliderWidget`
- Search text: ThreeDAmbientShadowsIntensityShiftSlider | ctkSliderWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:188: this->ThreeDAmbientShadowsIntensityShiftSlider,`

## widget: MSAALabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Multi-sampling (MSAA): | MSAALabel | QLabel
- Text: Multi-sampling (MSAA):
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`

## widget: MSAAComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `QComboBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Use multisampling for full-screen anti-aliasing.</span></p></body></html> | MSAAComboBox | QComboBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Use multisampling for full-screen anti-aliasing.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsViewsPanel.cxx`, `Base/QTGUI/qSlicerSettingsViewsPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:68: this->MSAAComboBox->addItem("Off", 0);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:69: this->MSAAComboBox->addItem("Auto", -1);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:70: this->MSAAComboBox->addItem("2x", 2);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:71: this->MSAAComboBox->addItem("4x", 4);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:72: this->MSAAComboBox->addItem("8x", 8);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:73: this->MSAAComboBox->addItem("16x", 16);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:74: this->MSAAComboBox->setCurrentIndex(this->MSAAComboBox->findText("Off"));`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:77: QObject::connect(this->MSAAComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::onMSAAChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:78: QObject::connect(this->MSAAComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsViewsPanel::currentMSAAChanged);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:225: const int index = d->MSAAComboBox->findText(text);`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:226: const int nSamples = d->MSAAComboBox->itemData(index).toInt();`
  - `Base/QTGUI/qSlicerSettingsViewsPanel.cxx:234: return d->MSAAComboBox->currentText();`
- Connected slots/functions: `currentMSAAChanged`, `currentTextChanged`, `onMSAAChanged`
