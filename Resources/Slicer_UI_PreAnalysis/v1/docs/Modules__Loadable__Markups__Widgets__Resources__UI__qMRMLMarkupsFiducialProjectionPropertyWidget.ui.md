# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsFiducialProjectionPropertyWidget.ui

- Owner class: `qMRMLMarkupsFiducialProjectionPropertyWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsFiducialProjectionPropertyWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsFiducialProjectionPropertyWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsFiducialProjectionPropertyWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:25: #include "qMRMLMarkupsFiducialProjectionPropertyWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:26: #include "ui_qMRMLMarkupsFiducialProjectionPropertyWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:33: class qMRMLMarkupsFiducialProjectionPropertyWidgetPrivate : public Ui_qMRMLMarkupsFiducialProjectionPropertyWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:35: Q_DECLARE_PUBLIC(qMRMLMarkupsFiducialProjectionPropertyWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:38: qMRMLMarkupsFiducialProjectionPropertyWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:41: qMRMLMarkupsFiducialProjectionPropertyWidgetPrivate(qMRMLMarkupsFiducialProjectionPropertyWidget& object);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:48: // qMRMLMarkupsFiducialProjectionPropertyWidgetPrivate methods`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:51: qMRMLMarkupsFiducialProjectionPropertyWidgetPrivate::qMRMLMarkupsFiducialProjectionPropertyWidgetPrivate(qMRMLMarkupsFiducialProjectionPropertyWidget& object)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:58: void qMRMLMarkupsFiducialProjectionPropertyWidgetPrivate::init()`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:60: Q_Q(qMRMLMarkupsFiducialProjectionPropertyWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:71: // qMRMLMarkupsFiducialProjectionPropertyWidget methods`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:74: qMRMLMarkupsFiducialProjectionPropertyWidget::qMRMLMarkupsFiducialProjectionPropertyWidget(QWidget* newParent)`
- API footprints: `GetMarkupsDisplayNode`

## widget: point2DProjectionLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Projection Visibility: | If enabled then all control points will be displayed in 2D viewers, by projecting them to the slice plane. | point2DProjectionLabel | QLabel
- Text: Projection Visibility:
- Tooltip: If enabled then all control points will be displayed in 2D viewers, by projecting them to the slice plane.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`

## widget: pointProjectionColorLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Projection Color: | Color of the projected control points on 2D viewers | pointProjectionColorLabel | QLabel
- Text: Projection Color:
- Tooltip: Color of the projected control points on 2D viewers
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:149: d->pointProjectionColorLabel->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:155: d->pointProjectionColorLabel->setEnabled(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:214: d->pointProjectionColorLabel->setEnabled(!useFiducialColor);`
- API footprints: `GetSliceProjectionUseFiducialColor`, `SliceProjectionUseFiducialColorOff`, `SliceProjectionUseFiducialColorOn`

## widget: pointProjectionColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: Color of the projected control points on 2D viewers. Only used if "Use Markup Color" is not checked, otherwise the projection uses the selected or unselected markup color. | pointProjectionColorPickerButton | ctkColorPickerButton
- Tooltip: Color of the projected control points on 2D viewers. Only used if "Use Markup Color" is not checked, otherwise the projection uses the selected or unselected markup color.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:63: QObject::connect(this->pointProjectionColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(setProjectionColor(QColor)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:150: d->pointProjectionColorPickerButton->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:156: d->pointProjectionColorPickerButton->setEnabled(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:209: d->pointProjectionColorPickerButton->setColor(displayColor);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:215: d->pointProjectionColorPickerButton->setEnabled(!useFiducialColor);`
- Connected slots/functions: `setProjectionColor`
- API footprints: `GetSliceProjectionColor`, `SetSliceProjectionColor`, `SliceProjectionUseFiducialColorOff`, `SliceProjectionUseFiducialColorOn`

## widget: pointOutlinedBehindSlicePlaneLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Outlined Behind Slice Plane: | Projected control points are displayed filled (opacity = Projection Opacity) when above the slice plane, outlined when behind, and with full opacity when in the plane. Outline isn't used for some glyphs (Dash2D, Cross2D, Starburst). | pointOutlinedBehindSlicePlaneLabel | QLabel
- Text: Outlined Behind Slice Plane:
- Tooltip: Projected control points are displayed filled (opacity = Projection Opacity) when above the slice plane, outlined when behind, and with full opacity when in the plane. Outline isn't used for some glyphs (Dash2D, Cross2D, Starburst).
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`

## widget: pointOutlinedBehindSlicePlaneCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Projected control points are displayed filled (opacity = Projection Opacity) when above the slice plane, outlined when behind, and with full opacity when in the plane. Outline isn't used for some glyphs (Dash2D, Cross2D, Starburst). | pointOutlinedBehindSlicePlaneCheckBox | QCheckBox
- Tooltip: Projected control points are displayed filled (opacity = Projection Opacity) when above the slice plane, outlined when behind, and with full opacity when in the plane. Outline isn't used for some glyphs (Dash2D, Cross2D, Starburst).
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:65: QObject::connect(this->pointOutlinedBehindSlicePlaneCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOutlinedBehindSlicePlane(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:218: d->pointOutlinedBehindSlicePlaneCheckBox->setChecked(d->FiducialDisplayNode->GetSliceProjectionOutlinedBehindSlicePlane());`
- Connected slots/functions: `setOutlinedBehindSlicePlane`
- API footprints: `GetSliceProjectionOutlinedBehindSlicePlane`, `SliceProjectionOutlinedBehindSlicePlaneOff`, `SliceProjectionOutlinedBehindSlicePlaneOn`
- Key UI properties: {"checked": "true"}

## widget: pointUseFiducialColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use Markup Color: | Use the same color as the markup | pointUseFiducialColorLabel | QLabel
- Text: Use Markup Color:
- Tooltip: Use the same color as the markup
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`

## widget: pointUseFiducialColorCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Use the same color as the markup | pointUseFiducialColorCheckBox | QCheckBox
- Tooltip: Use the same color as the markup
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:64: QObject::connect(this->pointUseFiducialColorCheckBox, SIGNAL(toggled(bool)), q, SLOT(setUseFiducialColor(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:213: d->pointUseFiducialColorCheckBox->setChecked(useFiducialColor);`
- Connected slots/functions: `setUseFiducialColor`
- API footprints: `GetSliceProjectionUseFiducialColor`, `SliceProjectionUseFiducialColorOff`, `SliceProjectionUseFiducialColorOn`
- Key UI properties: {"checked": "true"}

## widget: point2DProjectionCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: If enabled then all control points will be displayed in 2D viewers, by projecting them to the slice plane. | point2DProjectionCheckBox | ctkCheckBox
- Tooltip: If enabled then all control points will be displayed in 2D viewers, by projecting them to the slice plane.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:62: QObject::connect(this->point2DProjectionCheckBox, SIGNAL(toggled(bool)), q, SLOT(setProjectionVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:203: d->point2DProjectionCheckBox->setChecked(d->FiducialDisplayNode->GetSliceProjection());`
- Connected slots/functions: `setProjectionVisibility`
- API footprints: `GetSliceProjection`, `SliceProjectionOff`, `SliceProjectionOn`

## widget: projectionOpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | projectionOpacityLabel | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`

## widget: projectionOpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: The opacity of the projection. | projectionOpacitySliderWidget | ctkSliderWidget
- Tooltip: The opacity of the projection.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:66: QObject::connect(this->projectionOpacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setProjectionOpacity(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsFiducialProjectionPropertyWidget.cxx:221: d->projectionOpacitySliderWidget->setValue(d->FiducialDisplayNode->GetSliceProjectionOpacity());`
- Connected slots/functions: `setProjectionOpacity`
- API footprints: `GetSliceProjectionOpacity`, `SetSliceProjectionOpacity`
