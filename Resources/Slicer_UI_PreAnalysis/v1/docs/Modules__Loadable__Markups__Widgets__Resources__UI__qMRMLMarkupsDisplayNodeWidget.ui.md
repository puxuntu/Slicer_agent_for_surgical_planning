# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsDisplayNodeWidget.ui

- Owner class: `qMRMLMarkupsDisplayNodeWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsDisplayNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLMarkupsDisplayNodeWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:25: #include "qMRMLMarkupsDisplayNodeWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:26: #include "ui_qMRMLMarkupsDisplayNodeWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:47: class qMRMLMarkupsDisplayNodeWidgetPrivate`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:49: , public Ui_qMRMLMarkupsDisplayNodeWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:51: Q_DECLARE_PUBLIC(qMRMLMarkupsDisplayNodeWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:54: qMRMLMarkupsDisplayNodeWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:58: qMRMLMarkupsDisplayNodeWidgetPrivate(qMRMLMarkupsDisplayNodeWidget& object);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:65: qMRMLMarkupsDisplayNodeWidgetPrivate::qMRMLMarkupsDisplayNodeWidgetPrivate(qMRMLMarkupsDisplayNodeWidget& object)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:71: void qMRMLMarkupsDisplayNodeWidgetPrivate::init()`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:73: Q_Q(qMRMLMarkupsDisplayNodeWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:86: QObject::connect(this->glyphTypeComboBox, &QComboBox::currentTextChanged, q, &qMRMLMarkupsDisplayNodeWidget::onGlyphTypeComboBoxChanged);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:104: this->SnapModeComboBox->addItem(qMRMLMarkupsDisplayNodeWidget::tr("unconstrained"), vtkMRMLMarkupsDisplayNode::SnapModeUnconstrained);`
- Connected slots/functions: `currentTextChanged`, `onGlyphTypeComboBoxChanged`, `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ScalarsDisplayWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> InteractionHandleWidget.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetDisplayNode`, `GetPointer`, `SetGlyphTypeFromString`, `vtkMRMLMarkupsDisplayNode::SafeDownCast`, `vtkMRMLMarkupsDisplayNode::SnapModeToVisibleSurface`, `vtkMRMLMarkupsDisplayNode::SnapModeUnconstrained`, `vtkMRMLMarkupsNode::SafeDownCast`

## widget: VisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Overall visibility of the selected node in all views | VisibilityCheckBox | QCheckBox
- Tooltip: Overall visibility of the selected node in all views
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:82: QObject::connect(this->VisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:93: QObject::connect(this->PropertiesLabelVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setPropertiesLabelVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:94: QObject::connect(this->PointLabelsVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setPointLabelsVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:99: QObject::connect(this->FillVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setFillVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:100: QObject::connect(this->OutlineVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOutlineVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:108: QObject::connect(this->OccludedVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOccludedVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:111: QObject::connect(this->OccludedVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOccludedVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:113: QObject::connect(this->LineDirectionVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineDirectionVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:119: QObject::connect(this->LineSliceIntersectionPointVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineSliceIntersectionPointVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:253: d->VisibilityCheckBox->setChecked(d->MarkupsDisplayNode ? d->MarkupsDisplayNode->GetVisibility() : false);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:329: d->PropertiesLabelVisibilityCheckBox->setChecked(markupsDisplayNode->GetPropertiesLabelVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:331: d->PointLabelsVisibilityCheckBox->setChecked(markupsDisplayNode->GetPointLabelsVisibility());`
- Connected slots/functions: `setFillVisibility`, `setLineDirectionVisibility`, `setLineSliceIntersectionPointVisibility`, `setOccludedVisibility`, `setOutlineVisibility`, `setPointLabelsVisibility`, `setPropertiesLabelVisibility`, `setVisibility`
- API footprints: `GetFillVisibility`, `GetLineDirectionVisibility`, `GetLineSliceIntersectionPointVisibility`, `GetOccludedVisibility`, `GetOutlineVisibility`, `GetPointLabelsVisibility`, `GetPointer`, `GetPropertiesLabelVisibility`, `GetScene`, `GetVisibility`, `SetFillVisibility`, `SetLineDirectionVisibility`, `SetLineSliceIntersectionPointVisibility`, `SetOccludedVisibility`, `SetOutlineVisibility`, `SetPointLabelsVisibility`, `SetPropertiesLabelVisibility`, `SetVisibility`

## widget: opacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | opacityLabel | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: opacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: opacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:97: QObject::connect(this->opacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onOpacitySliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:271: d->opacitySliderWidget->setValue(markupsDisplayNode->GetOpacity());`
- Connected slots/functions: `onOpacitySliderWidgetChanged`
- API footprints: `GetActiveColor`, `GetOpacity`, `SetOpacity`

## widget: VisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | VisibilityLabel | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: glyphSizeIsAbsoluteButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: absolute | If button is pressed then control point glyph size is specified in physical length unit, otherwise as percentage of window size | glyphSizeIsAbsoluteButton | QPushButton
- Text: absolute
- Tooltip: If button is pressed then control point glyph size is specified in physical length unit, otherwise as percentage of window size
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:87: QObject::connect(this->glyphSizeIsAbsoluteButton, SIGNAL(toggled(bool)), q, SLOT(setGlyphSizeIsAbsolute(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:170: this->glyphSizeSliderWidget->setVisible(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:171: this->glyphScaleSliderWidget->setHidden(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:173: this->curveLineDiameterSliderWidget->setVisible(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:174: this->curveLineThicknessSliderWidget->setHidden(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:281: d->glyphSizeIsAbsoluteButton->setChecked(!markupsDisplayNode->GetUseGlyphScale());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:520: return d->glyphSizeIsAbsoluteButton->isChecked();`
- Connected slots/functions: `setGlyphSizeIsAbsolute`, `setHidden`, `setVisible`
- Declared UI connections: `toggled(bool) -> glyphScaleSliderWidget.setHidden(bool)`; `toggled(bool) -> glyphSizeSliderWidget.setVisible(bool)`
- API footprints: `GetPointer`, `GetUseGlyphScale`, `SetUseGlyphScale`
- Key UI properties: {"checkable": "true"}

## widget: glyphScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: glyphScaleSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:88: QObject::connect(this->glyphScaleSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onGlyphScaleSliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:171: this->glyphScaleSliderWidget->setHidden(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:286: if (glyphScale > d->glyphScaleSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:288: d->glyphScaleSliderWidget->setMaximum(glyphScale);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:290: d->glyphScaleSliderWidget->setValue(glyphScale);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:660: if (maxScale > d->glyphScaleSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:662: d->glyphScaleSliderWidget->setMaximum(maxScale);`
- Connected slots/functions: `onGlyphScaleSliderWidgetChanged`
- API footprints: `GetGlyphScale`, `SetGlyphScale`

## widget: glyphSizeSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: glyphSizeSliderWidget | qMRMLSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:89: QObject::connect(this->glyphSizeSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onGlyphSizeSliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:170: this->glyphSizeSliderWidget->setVisible(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:295: if (glyphSize > d->glyphSizeSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:297: d->glyphSizeSliderWidget->setMaximum(glyphSize);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:299: d->glyphSizeSliderWidget->setValue(glyphSize);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:300: d->glyphSizeSliderWidget->setMRMLScene(markupsDisplayNode->GetScene());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:675: if (maxSize > d->glyphSizeSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:677: d->glyphSizeSliderWidget->setMaximum(maxSize);`
- Connected slots/functions: `onGlyphSizeSliderWidgetChanged`
- API footprints: `GetCurveLineSizeMode`, `GetGlyphSize`, `GetScene`, `SetGlyphSize`, `vtkMRMLMarkupsDisplayNode::UseLineDiameter`

## widget: SliceDisplayCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: SliceDisplayCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Key UI properties: {"checked": "false"}

## widget: TextDisplayGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: TextDisplayGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: TextFontFamilyComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: TextFontFamilyComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:121: this->TextFontFamilyComboBox->addItem(vtkTextProperty::GetFontFamilyAsString(VTK_ARIAL), VTK_ARIAL);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:122: this->TextFontFamilyComboBox->addItem(vtkTextProperty::GetFontFamilyAsString(VTK_COURIER), VTK_COURIER);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:123: this->TextFontFamilyComboBox->addItem(vtkTextProperty::GetFontFamilyAsString(VTK_TIMES), VTK_TIMES);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:125: QObject::connect(this->TextFontFamilyComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onTextPropertyWidgetsChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:374: wasBlocking = d->TextFontFamilyComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:375: int fontFamilyIndex = d->TextFontFamilyComboBox->findData(property->GetFontFamily());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:376: d->TextFontFamilyComboBox->setCurrentIndex(fontFamilyIndex);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:377: d->TextFontFamilyComboBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:767: int fontFamily = d->TextFontFamilyComboBox->currentData().toInt();`
- Connected slots/functions: `onTextPropertyWidgetsChanged`
- API footprints: `GetFontFamily`, `GetTextProperty`, `SetBackgroundColor`, `SetBackgroundOpacity`, `SetBold`, `SetFontFamily`, `SetItalic`, `SetShadow`

## widget: TextBoldCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Bold | TextBoldCheckBox | QCheckBox
- Text: Bold
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:126: QObject::connect(this->TextBoldCheckBox, SIGNAL(toggled(bool)), q, SLOT(onTextPropertyWidgetsChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:379: wasBlocking = d->TextBoldCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:380: d->TextBoldCheckBox->setChecked(property->GetBold());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:381: d->TextBoldCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:768: bool textBold = d->TextBoldCheckBox->isChecked();`
- Connected slots/functions: `onTextPropertyWidgetsChanged`
- API footprints: `GetBold`, `GetTextProperty`, `SetBackgroundColor`, `SetBackgroundOpacity`, `SetBold`, `SetFontFamily`, `SetItalic`, `SetShadow`

## widget: TextItalicCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Italic | TextItalicCheckBox | QCheckBox
- Text: Italic
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:127: QObject::connect(this->TextItalicCheckBox, SIGNAL(toggled(bool)), q, SLOT(onTextPropertyWidgetsChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:383: wasBlocking = d->TextItalicCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:384: d->TextItalicCheckBox->setChecked(property->GetItalic());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:385: d->TextItalicCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:769: bool textItalic = d->TextItalicCheckBox->isChecked();`
- Connected slots/functions: `onTextPropertyWidgetsChanged`
- API footprints: `GetItalic`, `GetTextProperty`, `SetBackgroundColor`, `SetBackgroundOpacity`, `SetBold`, `SetFontFamily`, `SetItalic`, `SetShadow`

## widget: TextShadowCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Shadow | TextShadowCheckBox | QCheckBox
- Text: Shadow
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:128: QObject::connect(this->TextShadowCheckBox, SIGNAL(toggled(bool)), q, SLOT(onTextPropertyWidgetsChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:387: wasBlocking = d->TextShadowCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:388: d->TextShadowCheckBox->setChecked(property->GetShadow());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:389: d->TextShadowCheckBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:770: bool textShadow = d->TextShadowCheckBox->isChecked();`
- Connected slots/functions: `onTextPropertyWidgetsChanged`
- API footprints: `GetShadow`, `GetTextProperty`, `SetBackgroundColor`, `SetBackgroundOpacity`, `SetBold`, `SetFontFamily`, `SetItalic`, `SetShadow`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Font: | label_3 | QLabel
- Text: Font:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: TextBackgroundColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: TextBackgroundColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:129: QObject::connect(this->TextBackgroundColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(onTextPropertyWidgetsChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:395: wasBlocking = d->TextBackgroundColorPickerButton->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:398: d->TextBackgroundColorPickerButton->setColor(QColor::fromRgbF(textBackgroundColorF[0], textBackgroundColorF[1], textBackgroundColorF[2]));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:399: d->TextBackgroundColorPickerButton->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:772: QColor backgroundColor = d->TextBackgroundColorPickerButton->color();`
- Connected slots/functions: `onTextPropertyWidgetsChanged`
- API footprints: `GetBackgroundColor`, `GetTextProperty`, `SetBackgroundColor`, `SetBackgroundOpacity`, `SetBold`, `SetFontFamily`, `SetItalic`, `SetShadow`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity | label_2 | QLabel
- Text: Opacity
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: TextBackgroundOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: TextBackgroundOpacitySlider | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:130: QObject::connect(this->TextBackgroundOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(onTextPropertyWidgetsChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:391: wasBlocking = d->TextBackgroundOpacitySlider->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:392: d->TextBackgroundOpacitySlider->setValue(property->GetBackgroundOpacity());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:393: d->TextBackgroundOpacitySlider->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:771: double backgroundOpacity = d->TextBackgroundOpacitySlider->value();`
- Connected slots/functions: `onTextPropertyWidgetsChanged`
- API footprints: `GetBackgroundOpacity`, `GetTextProperty`, `SetBackgroundColor`, `SetBackgroundOpacity`, `SetBold`, `SetFontFamily`, `SetItalic`, `SetShadow`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Background: | label | QLabel
- Text: Background:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`, `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:740: QTableWidgetItem* labelItem = new QTableWidgetItem(QString::fromStdString(controlPointLabel));`
  - `Modules/Loadable/Markups/Widgets/qSlicerSimpleMarkupsWidget.cxx:763: d->MarkupsControlPointsTableWidget->setItem(i, CONTROL_POINT_LABEL_COLUMN, labelItem);`
- API footprints: `GetNthControlPointPosition`

## widget: glyphTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: glyphTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:86: QObject::connect(this->glyphTypeComboBox, &QComboBox::currentTextChanged, q, &qMRMLMarkupsDisplayNodeWidget::onGlyphTypeComboBoxChanged);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:133: if (this->glyphTypeComboBox->count() == 0)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:138: this->glyphTypeComboBox->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:141: this->glyphTypeComboBox->addItem(displayNode->GetGlyphTypeAsString(i), displayNode->GetGlyphTypeAsString(i));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:143: this->glyphTypeComboBox->setEnabled(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:146: if (this->glyphTypeComboBox->currentIndex() == 0)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:150: this->glyphTypeComboBox->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:151: int index = this->glyphTypeComboBox->findData(glyphType);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:154: this->glyphTypeComboBox->setCurrentIndex(index);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:159: this->glyphTypeComboBox->setCurrentIndex(displayNode->GetGlyphType() - 1);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:161: this->glyphTypeComboBox->setEnabled(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:275: int glyphTypeIndex = d->glyphTypeComboBox->findData(glyphTypeStr);`
- Connected slots/functions: `currentTextChanged`, `onGlyphTypeComboBoxChanged`
- API footprints: `GetGlyphType`, `GetGlyphTypeAsString`, `GetMaximumGlyphType`, `GetMinimumGlyphType`, `SetGlyphTypeFromString`

## widget: DisplayNodeViewComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLDisplayNodeViewComboBox`
- Search text: Select views in which to show this node. All unchecked shows in all 3D and 2D views. | DisplayNodeViewComboBox | qMRMLDisplayNodeViewComboBox
- Tooltip: Select views in which to show this node. All unchecked shows in all 3D and 2D views.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:251: d->DisplayNodeViewComboBox->setMRMLDisplayNode(d->MarkupsDisplayNode);`
- API footprints: `GetVisibility`

## widget: activeColorPickerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Active Color: | activeColorPickerLabel | QLabel
- Text: Active Color:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: TwoDDisplayGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: TwoDDisplayGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: pointFiducialProjectionWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLMarkupsFiducialProjectionPropertyWidget`
- Search text: pointFiducialProjectionWidget | qMRMLMarkupsFiducialProjectionPropertyWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:252: d->pointFiducialProjectionWidget->setMRMLMarkupsDisplayNode(d->MarkupsDisplayNode);`
- API footprints: `GetVisibility`

## widget: FillLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Fill: | FillLabel | QLabel
- Text: Fill:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: glyphTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Glyph Type: | glyphTypeLabel | QLabel
- Text: Glyph Type:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: OutlineVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: OutlineVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:100: QObject::connect(this->OutlineVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOutlineVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:347: wasBlocking = d->OutlineVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:348: d->OutlineVisibilityCheckBox->setChecked(markupsDisplayNode->GetOutlineVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:349: d->OutlineVisibilityCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setOutlineVisibility`
- API footprints: `GetOutlineVisibility`, `SetOutlineVisibility`

## widget: OpacityLabel2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | OpacityLabel2 | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: OutlineOpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: OutlineOpacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:102: QObject::connect(this->OutlineOpacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onOutlineOpacitySliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:355: wasBlocking = d->OutlineOpacitySliderWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:356: d->OutlineOpacitySliderWidget->setValue(markupsDisplayNode->GetOutlineOpacity());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:357: d->OutlineOpacitySliderWidget->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:726: void qMRMLMarkupsDisplayNodeWidget::onOutlineOpacitySliderWidgetChanged(double opacity)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h:90: void onOutlineOpacitySliderWidgetChanged(double opacity);`
- Connected slots/functions: `onOutlineOpacitySliderWidgetChanged`
- API footprints: `GetOutlineOpacity`, `SetOutlineOpacity`, `vtkMRMLMarkupsDisplayNode::SnapModeUnconstrained`

## widget: DisplayNodeViewLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View: | DisplayNodeViewLabel | QLabel
- Text: View:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: unselectedColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Unselected Color: | unselectedColorLabel | QLabel
- Text: Unselected Color:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: OutlineLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Outline: | OutlineLabel | QLabel
- Text: Outline:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: PointLabelsVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show control point labels | PointLabelsVisibilityCheckBox | QCheckBox
- Tooltip: Show control point labels
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:94: QObject::connect(this->PointLabelsVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setPointLabelsVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:331: d->PointLabelsVisibilityCheckBox->setChecked(markupsDisplayNode->GetPointLabelsVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:502: return d->PointLabelsVisibilityCheckBox->isChecked();`
- Connected slots/functions: `setPointLabelsVisibility`
- API footprints: `GetPointLabelsVisibility`, `GetPointer`, `GetPropertiesLabelVisibility`, `SetPointLabelsVisibility`

## widget: selectedColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: selectedColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:77: this->selectedColorPickerButton->setDialogOptions(ctkColorPickerButton::UseCTKColorDialog);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:78: this->unselectedColorPickerButton->setDialogOptions(ctkColorPickerButton::UseCTKColorDialog);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:83: QObject::connect(this->selectedColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(onSelectedColorPickerButtonChanged(QColor)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:84: QObject::connect(this->unselectedColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(onUnselectedColorPickerButtonChanged(QColor)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:266: d->selectedColorPickerButton->setColor(QColor::fromRgbF(color[0], color[1], color[2]));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:268: d->unselectedColorPickerButton->setColor(QColor::fromRgbF(color[0], color[1], color[2]));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:553: void qMRMLMarkupsDisplayNodeWidget::onUnselectedColorPickerButtonChanged(QColor color)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h:107: void onUnselectedColorPickerButtonChanged(QColor qcolor);`
- Connected slots/functions: `onSelectedColorPickerButtonChanged`, `onUnselectedColorPickerButtonChanged`
- API footprints: `GetActiveColor`, `GetColor`, `GetSelectedColor`, `SetColor`, `SetSelectedColor`

## widget: curveLineSizeIsAbsoluteButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: absolute | If button is pressed then line thickness is specified in physical length unit, otherwise as percentage of glyph size | curveLineSizeIsAbsoluteButton | QPushButton
- Text: absolute
- Tooltip: If button is pressed then line thickness is specified in physical length unit, otherwise as percentage of glyph size
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:90: QObject::connect(this->curveLineSizeIsAbsoluteButton, SIGNAL(toggled(bool)), q, SLOT(setCurveLineSizeIsAbsolute(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:302: d->curveLineSizeIsAbsoluteButton->setChecked(markupsDisplayNode->GetCurveLineSizeMode() == vtkMRMLMarkupsDisplayNode::UseLineDiameter);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:324: d->curveLineSizeIsAbsoluteButton->setEnabled(lineSizeEnabled);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:538: return d->curveLineSizeIsAbsoluteButton->isChecked();`
- Connected slots/functions: `setCurveLineSizeIsAbsolute`, `setHidden`, `setVisible`
- Declared UI connections: `toggled(bool) -> curveLineThicknessSliderWidget.setHidden(bool)`; `toggled(bool) -> curveLineDiameterSliderWidget.setVisible(bool)`
- API footprints: `GetCurveLineSizeMode`, `GetDisplayableNode`, `GetPointer`, `GetScene`, `SetCurveLineSizeMode`, `vtkMRMLMarkupsDisplayNode::UseLineDiameter`, `vtkMRMLMarkupsDisplayNode::UseLineThickness`, `vtkMRMLMarkupsFiducialNode::SafeDownCast`
- Key UI properties: {"checkable": "true"}

## widget: curveLineThicknessSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: curveLineThicknessSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:91: QObject::connect(this->curveLineThicknessSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onCurveLineThicknessSliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:174: this->curveLineThicknessSliderWidget->setHidden(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:307: if (lineThicknessPercentage > d->curveLineThicknessSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:309: d->curveLineThicknessSliderWidget->setMaximum(lineThicknessPercentage);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:311: d->curveLineThicknessSliderWidget->setValue(lineThicknessPercentage);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:326: d->curveLineThicknessSliderWidget->setEnabled(lineSizeEnabled);`
- Connected slots/functions: `onCurveLineThicknessSliderWidgetChanged`
- API footprints: `GetLineThickness`, `GetScene`, `SetLineThickness`

## widget: curveLineDiameterSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: curveLineDiameterSliderWidget | qMRMLSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:92: QObject::connect(this->curveLineDiameterSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onCurveLineDiameterSliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:173: this->curveLineDiameterSliderWidget->setVisible(this->glyphSizeIsAbsoluteButton->isChecked());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:316: if (lineDiameter > d->curveLineDiameterSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:318: d->curveLineDiameterSliderWidget->setMaximum(lineDiameter);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:320: d->curveLineDiameterSliderWidget->setValue(lineDiameter);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:325: d->curveLineDiameterSliderWidget->setEnabled(lineSizeEnabled);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:327: d->curveLineDiameterSliderWidget->setMRMLScene(markupsDisplayNode->GetScene());`
- Connected slots/functions: `onCurveLineDiameterSliderWidgetChanged`
- API footprints: `GetDisplayableNode`, `GetLineDiameter`, `GetPropertiesLabelVisibility`, `GetScene`, `SetLineDiameter`, `vtkMRMLMarkupsFiducialNode::SafeDownCast`

## widget: lineThicknessLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Line Thickness: | lineThicknessLabel | QLabel
- Text: Line Thickness:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: selectedColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Selected Color: | selectedColorLabel | QLabel
- Text: Selected Color:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: FillVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: FillVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:99: QObject::connect(this->FillVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setFillVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:343: wasBlocking = d->FillVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:344: d->FillVisibilityCheckBox->setChecked(markupsDisplayNode->GetFillVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:345: d->FillVisibilityCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setFillVisibility`
- API footprints: `GetFillVisibility`, `SetFillVisibility`

## widget: OpacityLabel3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | OpacityLabel3 | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: FillOpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: FillOpacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:101: QObject::connect(this->FillOpacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onFillOpacitySliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:351: wasBlocking = d->FillOpacitySliderWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:352: d->FillOpacitySliderWidget->setValue(markupsDisplayNode->GetFillOpacity());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:353: d->FillOpacitySliderWidget->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:715: void qMRMLMarkupsDisplayNodeWidget::onFillOpacitySliderWidgetChanged(double opacity)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h:89: void onFillOpacitySliderWidgetChanged(double opacity);`
- Connected slots/functions: `onFillOpacitySliderWidgetChanged`
- API footprints: `GetFillOpacity`, `SetFillOpacity`

## widget: PointLabelsVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Control Point Labels: | PointLabelsVisibilityLabel | QLabel
- Text: Control Point Labels:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: unselectedColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: unselectedColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:78: this->unselectedColorPickerButton->setDialogOptions(ctkColorPickerButton::UseCTKColorDialog);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:84: QObject::connect(this->unselectedColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(onUnselectedColorPickerButtonChanged(QColor)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:268: d->unselectedColorPickerButton->setColor(QColor::fromRgbF(color[0], color[1], color[2]));`
- Connected slots/functions: `onUnselectedColorPickerButtonChanged`
- API footprints: `GetActiveColor`, `GetColor`, `SetColor`

## widget: ThreeDDisplayGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: ThreeDDisplayGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: OccludedVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Occluded Visibility: | OccludedVisibilityLabel | QLabel
- Text: Occluded Visibility:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: OccludedVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: OccludedVisibilityCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:108: QObject::connect(this->OccludedVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOccludedVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:111: QObject::connect(this->OccludedVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setOccludedVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:359: wasBlocking = d->OccludedVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:360: d->OccludedVisibilityCheckBox->setChecked(markupsDisplayNode->GetOccludedVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:361: d->OccludedVisibilityCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setOccludedVisibility`
- API footprints: `GetOccludedVisibility`, `SetOccludedVisibility`

## widget: OpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | OpacityLabel | QLabel
- Text: Opacity:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: OccludedOpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: OccludedOpacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:109: QObject::connect(this->OccludedOpacitySliderWidget, SIGNAL(valueChanged(double)), q, SLOT(setOccludedOpacity(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:368: wasBlocking = d->OccludedOpacitySliderWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:369: d->OccludedOpacitySliderWidget->setValue(markupsDisplayNode->GetOccludedOpacity());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:370: d->OccludedOpacitySliderWidget->blockSignals(wasBlocking);`
- Connected slots/functions: `setOccludedOpacity`
- API footprints: `GetOccludedOpacity`, `GetTextProperty`, `SetOccludedOpacity`

## widget: PointLabelsVisibilityLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Placement mode: | PointLabelsVisibilityLabel_2 | QLabel
- Text: Placement mode:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: SnapModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: SnapModeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:104: this->SnapModeComboBox->addItem(qMRMLMarkupsDisplayNodeWidget::tr("unconstrained"), vtkMRMLMarkupsDisplayNode::SnapModeUnconstrained);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:105: this->SnapModeComboBox->addItem(qMRMLMarkupsDisplayNodeWidget::tr("snap to visible surface"), vtkMRMLMarkupsDisplayNode::SnapModeToVisibleSurface);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:106: QObject::connect(this->SnapModeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onSnapModeWidgetChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:363: wasBlocking = d->SnapModeComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:364: int snapModeIndex = d->SnapModeComboBox->findData(markupsDisplayNode->GetSnapMode());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:365: d->SnapModeComboBox->setCurrentIndex(snapModeIndex);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:366: d->SnapModeComboBox->blockSignals(wasBlocking);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:870: int snapMode = d->SnapModeComboBox->currentData().toInt();`
- Connected slots/functions: `onSnapModeWidgetChanged`
- API footprints: `GetSnapMode`, `SetSnapMode`, `vtkMRMLMarkupsDisplayNode::SnapModeToVisibleSurface`, `vtkMRMLMarkupsDisplayNode::SnapModeUnconstrained`

## widget: PropertiesLabelVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Properties Label: | PropertiesLabelVisibilityLabel | QLabel
- Text: Properties Label:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: activeColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: activeColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:79: this->activeColorPickerButton->setDialogOptions(ctkColorPickerButton::UseCTKColorDialog);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:85: QObject::connect(this->activeColorPickerButton, SIGNAL(colorChanged(QColor)), q, SLOT(onActiveColorPickerButtonChanged(QColor)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:270: d->activeColorPickerButton->setColor(QColor::fromRgbF(color[0], color[1], color[2]));`
- Connected slots/functions: `onActiveColorPickerButtonChanged`
- API footprints: `GetActiveColor`, `GetOpacity`, `SetActiveColor`

## widget: PropertiesLabelVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show node name and measurements | PropertiesLabelVisibilityCheckBox | QCheckBox
- Tooltip: Show node name and measurements
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:93: QObject::connect(this->PropertiesLabelVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setPropertiesLabelVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:329: d->PropertiesLabelVisibilityCheckBox->setChecked(markupsDisplayNode->GetPropertiesLabelVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:495: return d->PropertiesLabelVisibilityCheckBox->isChecked();`
- Connected slots/functions: `setPropertiesLabelVisibility`
- API footprints: `GetPointLabelsVisibility`, `GetPointer`, `GetPropertiesLabelVisibility`, `GetScene`, `SetPropertiesLabelVisibility`

## widget: LineDirectionMarkersCollapsibleGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: LineDirectionMarkersCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:404: d->LineDirectionMarkersCollapsibleGroupBox->setVisible(isLineOrCurve);`
- API footprints: `GetDisplayableNode`, `vtkMRMLMarkupsCurveNode::SafeDownCast`, `vtkMRMLMarkupsLineNode::SafeDownCast`

## widget: LineDirectionVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show Direction Markers: | Show or hide directional arrow markers along curve and line markups. | LineDirectionVisibilityLabel | QLabel
- Text: Show Direction Markers:
- Tooltip: Show or hide directional arrow markers along curve and line markups.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineDirectionVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show or hide directional arrow markers along curve and line markups. | LineDirectionVisibilityCheckBox | QCheckBox
- Tooltip: Show or hide directional arrow markers along curve and line markups.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:113: QObject::connect(this->LineDirectionVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineDirectionVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:406: wasBlocking = d->LineDirectionVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:407: d->LineDirectionVisibilityCheckBox->setChecked(markupsDisplayNode->GetLineDirectionVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:408: d->LineDirectionVisibilityCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setLineDirectionVisibility`
- API footprints: `GetLineDirectionVisibility`, `SetLineDirectionVisibility`

## widget: LineDirectionVisibility3DLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: 3D Visibility: | Show direction markers in 3D views. Requires "Show Direction Markers" to be enabled. | LineDirectionVisibility3DLabel | QLabel
- Text: 3D Visibility:
- Tooltip: Show direction markers in 3D views. Requires "Show Direction Markers" to be enabled.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineDirectionVisibility3DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show direction markers in 3D views. Requires "Show Direction Markers" to be enabled. | LineDirectionVisibility3DCheckBox | QCheckBox
- Tooltip: Show direction markers in 3D views. Requires "Show Direction Markers" to be enabled.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:114: QObject::connect(this->LineDirectionVisibility3DCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineDirectionVisibility3D(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:410: wasBlocking = d->LineDirectionVisibility3DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:411: d->LineDirectionVisibility3DCheckBox->setChecked(markupsDisplayNode->GetLineDirectionVisibility3D());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:412: d->LineDirectionVisibility3DCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setLineDirectionVisibility3D`
- API footprints: `GetLineDirectionVisibility3D`, `SetLineDirectionVisibility3D`

## widget: LineDirectionVisibility2DLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: 2D Visibility: | Show direction markers in 2D slice views. Requires "Show Direction Markers" to be enabled. | LineDirectionVisibility2DLabel | QLabel
- Text: 2D Visibility:
- Tooltip: Show direction markers in 2D slice views. Requires "Show Direction Markers" to be enabled.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineDirectionVisibility2DCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show direction markers in 2D slice views. Requires "Show Direction Markers" to be enabled. | LineDirectionVisibility2DCheckBox | QCheckBox
- Tooltip: Show direction markers in 2D slice views. Requires "Show Direction Markers" to be enabled.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:115: QObject::connect(this->LineDirectionVisibility2DCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineDirectionVisibility2D(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:414: wasBlocking = d->LineDirectionVisibility2DCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:415: d->LineDirectionVisibility2DCheckBox->setChecked(markupsDisplayNode->GetLineDirectionVisibility2D());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:416: d->LineDirectionVisibility2DCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setLineDirectionVisibility2D`
- API footprints: `GetLineDirectionVisibility2D`, `SetLineDirectionVisibility2D`

## widget: LineSliceIntersectionPointVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice Intersection Points: | Show markers at positions where the curve/line crosses the current slice plane. | LineSliceIntersectionPointVisibilityLabel | QLabel
- Text: Slice Intersection Points:
- Tooltip: Show markers at positions where the curve/line crosses the current slice plane.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineSliceIntersectionPointVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Show markers at positions where the curve/line crosses the current slice plane. | LineSliceIntersectionPointVisibilityCheckBox | QCheckBox
- Tooltip: Show markers at positions where the curve/line crosses the current slice plane.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:119: QObject::connect(this->LineSliceIntersectionPointVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineSliceIntersectionPointVisibility(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:430: wasBlocking = d->LineSliceIntersectionPointVisibilityCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:431: d->LineSliceIntersectionPointVisibilityCheckBox->setChecked(markupsDisplayNode->GetLineSliceIntersectionPointVisibility());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:432: d->LineSliceIntersectionPointVisibilityCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setLineSliceIntersectionPointVisibility`
- API footprints: `GetLineSliceIntersectionPointVisibility`, `SetLineSliceIntersectionPointVisibility`

## widget: LineDirectionMarkerReversedLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Reverse Direction: | Reverse the direction of the arrow markers so they point in the opposite direction along the curve or line. | LineDirectionMarkerReversedLabel | QLabel
- Text: Reverse Direction:
- Tooltip: Reverse the direction of the arrow markers so they point in the opposite direction along the curve or line.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineDirectionMarkerReversedCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Reverse the direction of the arrow markers so they point in the opposite direction along the curve or line. | LineDirectionMarkerReversedCheckBox | QCheckBox
- Tooltip: Reverse the direction of the arrow markers so they point in the opposite direction along the curve or line.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:118: QObject::connect(this->LineDirectionMarkerReversedCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLineDirectionMarkerReversed(bool)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:426: wasBlocking = d->LineDirectionMarkerReversedCheckBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:427: d->LineDirectionMarkerReversedCheckBox->setChecked(!markupsDisplayNode->GetLineDirectionFirstToLastControlPoint());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:428: d->LineDirectionMarkerReversedCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setLineDirectionMarkerReversed`
- API footprints: `GetLineDirectionFirstToLastControlPoint`, `SetLineDirectionFirstToLastControlPoint`

## widget: LineDirectionMarkerSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Marker Size: | Size of each direction marker relative to the physical line thickness. | LineDirectionMarkerSizeLabel | QLabel
- Text: Marker Size:
- Tooltip: Size of each direction marker relative to the physical line thickness.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineDirectionMarkerScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Size of each direction marker relative to the physical line thickness. | LineDirectionMarkerScaleSliderWidget | ctkSliderWidget
- Tooltip: Size of each direction marker relative to the physical line thickness.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:116: QObject::connect(this->LineDirectionMarkerScaleSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onLineDirectionMarkerScaleChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:418: wasBlocking = d->LineDirectionMarkerScaleSliderWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:419: d->LineDirectionMarkerScaleSliderWidget->setValue(markupsDisplayNode->GetLineDirectionMarkerScale() * 100.0);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:420: d->LineDirectionMarkerScaleSliderWidget->blockSignals(wasBlocking);`
- Connected slots/functions: `onLineDirectionMarkerScaleChanged`
- API footprints: `GetLineDirectionMarkerScale`, `SetLineDirectionMarkerScale`

## widget: LineDirectionMarkerSpacingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Marker Spacing: | Distance between direction markers relative to the marker height. | LineDirectionMarkerSpacingLabel | QLabel
- Text: Marker Spacing:
- Tooltip: Distance between direction markers relative to the marker height.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: LineDirectionMarkerSpacingScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Distance between consecutive direction markers relative to the marker height. 100% = markers touch, 200% = one gap, 300% = two gaps. | LineDirectionMarkerSpacingScaleSliderWidget | ctkSliderWidget
- Tooltip: Distance between consecutive direction markers relative to the marker height. 100% = markers touch, 200% = one gap, 300% = two gaps.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:117: QObject::connect(this->LineDirectionMarkerSpacingScaleSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onLineDirectionMarkerSpacingScaleChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:422: wasBlocking = d->LineDirectionMarkerSpacingScaleSliderWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:423: d->LineDirectionMarkerSpacingScaleSliderWidget->setValue(markupsDisplayNode->GetLineDirectionMarkerSpacingScale() * 100.0);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:424: d->LineDirectionMarkerSpacingScaleSliderWidget->blockSignals(wasBlocking);`
- Connected slots/functions: `onLineDirectionMarkerSpacingScaleChanged`
- API footprints: `GetLineDirectionMarkerSpacingScale`, `SetLineDirectionMarkerSpacingScale`

## widget: glyphScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Glyph Size: | glyphScaleLabel | QLabel
- Text: Glyph Size:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: textScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: textScaleSliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:95: QObject::connect(this->textScaleSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onTextScaleSliderWidgetChanged(double)));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:336: if (textScale > d->textScaleSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:338: d->textScaleSliderWidget->setMaximum(textScale);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:340: d->textScaleSliderWidget->setValue(textScale);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:664: if (maxScale > d->textScaleSliderWidget->maximum())`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:666: d->textScaleSliderWidget->setMaximum(maxScale);`
- Connected slots/functions: `onTextScaleSliderWidgetChanged`
- API footprints: `GetTextScale`, `SetTextScale`

## widget: textScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Text Size: | textScaleLabel | QLabel
- Text: Text Size:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: ScalarsCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: ScalarsCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`

## widget: ScalarsDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLScalarsDisplayWidget`
- Search text: ScalarsDisplayWidget | qMRMLScalarsDisplayWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:176: q->connect(this->ScalarsDisplayWidget,`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:180: q->connect(this->ScalarsDisplayWidget, SIGNAL(displayNodeChanged()), q, SIGNAL(displayNodeChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:239: d->ScalarsDisplayWidget->setMRMLDisplayNode(markupsDisplayNode);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:435: d->ScalarsDisplayWidget->updateWidgetFromMRML();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h:23: #include "qMRMLScalarsDisplayWidget.h"`
- API footprints: `vtkMRMLDisplayNode::ScalarRangeFlagType`

## widget: CollapsibleGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:404: d->LineDirectionMarkersCollapsibleGroupBox->setVisible(isLineOrCurve);`
- API footprints: `GetDisplayableNode`, `vtkMRMLMarkupsCurveNode::SafeDownCast`, `vtkMRMLMarkupsLineNode::SafeDownCast`

## widget: InteractionHandleWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLMarkupsInteractionHandleWidget`
- Search text: InteractionHandleWidget | qMRMLMarkupsInteractionHandleWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsDisplayNodeWidget.cxx:241: d->InteractionHandleWidget->setMRMLDisplayNode(markupsDisplayNode);`
