# Slicer UI Analysis: Modules/Loadable/Markups/Resources/UI/qSlicerMarkupsSettingsPanel.ui

- Owner class: `qSlicerMarkupsSettingsPanel`
- UI file: `Modules/Loadable/Markups/Resources/UI/qSlicerMarkupsSettingsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerMarkupsSettingsPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerMarkupsSettingsPanel | ctkSettingsPanel
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:23: #include "qSlicerMarkupsSettingsPanel.h"`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:24: #include "ui_qSlicerMarkupsSettingsPanel.h"`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:36: // qSlicerMarkupsSettingsPanelPrivate`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:39: class qSlicerMarkupsSettingsPanelPrivate : public Ui_qSlicerMarkupsSettingsPanel`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:41: Q_DECLARE_PUBLIC(qSlicerMarkupsSettingsPanel);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:44: qSlicerMarkupsSettingsPanel* const q_ptr;`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:47: qSlicerMarkupsSettingsPanelPrivate(qSlicerMarkupsSettingsPanel& object);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:54: // qSlicerMarkupsSettingsPanelPrivate methods`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:57: qSlicerMarkupsSettingsPanelPrivate::qSlicerMarkupsSettingsPanelPrivate(qSlicerMarkupsSettingsPanel& object)`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:63: void qSlicerMarkupsSettingsPanelPrivate::init()`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:65: Q_Q(qSlicerMarkupsSettingsPanel);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:71: // qSlicerMarkupsSettingsPanel methods`

## widget: defaultGlyphTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default glyph type: | defaultGlyphTypeLabel | QLabel
- Text: Default glyph type:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultGlyphTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: The symbol used for the markup | defaultGlyphTypeComboBox | QComboBox
- Tooltip: The symbol used for the markup
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:120: QObject::connect(d->defaultGlyphTypeComboBox, SIGNAL(currentIndexChanged(int)),`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:124: //  d->defaultGlyphTypeComboBox->setCurrentIndex(glyphType - 1);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:125: int glyphTypeIndex = d->defaultGlyphTypeComboBox->findData(glyphType);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:128: d->defaultGlyphTypeComboBox->setCurrentIndex(glyphTypeIndex);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:166: int currentIndex = d->defaultGlyphTypeComboBox->currentIndex();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:170: glyphType = d->defaultGlyphTypeComboBox->itemText(currentIndex);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:240: int glyphTypeIndex = d->defaultGlyphTypeComboBox->findData(glyphType);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:244: d->defaultGlyphTypeComboBox->setCurrentIndex(glyphTypeIndex);`
- API footprints: `GetDefaultMarkupsDisplayNodeGlyphTypeAsString`

## widget: defaultSelectedColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default selected color: | defaultSelectedColorLabel | QLabel
- Text: Default selected color:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultSelectedColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: defaultSelectedColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:139: QObject::connect(d->defaultSelectedColorPickerButton, SIGNAL(colorChanged(QColor)),`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:142: d->defaultSelectedColorPickerButton->setColor(qcolor);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:190: QColor color = d->defaultSelectedColorPickerButton->color();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:261: d->defaultSelectedColorPickerButton->setColor(color);`
- API footprints: `GetDefaultMarkupsDisplayNodeGlyphScale`, `GetDefaultMarkupsDisplayNodeSelectedColor`

## widget: defaultUnselectedColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default unselected color: | defaultUnselectedColorLabel | QLabel
- Text: Default unselected color:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultUnselectedColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: defaultUnselectedColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:133: QObject::connect(d->defaultUnselectedColorPickerButton, SIGNAL(colorChanged(QColor)),`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:136: d->defaultUnselectedColorPickerButton->setColor(qcolor);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:180: QColor color = d->defaultUnselectedColorPickerButton->color();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:253: d->defaultUnselectedColorPickerButton->setColor(color);`
- API footprints: `GetDefaultMarkupsDisplayNodeColor`, `GetDefaultMarkupsDisplayNodeSelectedColor`

## widget: defaultGlyphScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default glyph scale: | defaultGlyphScaleLabel | QLabel
- Text: Default glyph scale:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultGlyphScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Default glyph scale | defaultGlyphScaleSliderWidget | ctkSliderWidget
- Tooltip: Default glyph scale
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:145: QObject::connect(d->defaultGlyphScaleSliderWidget, SIGNAL(valueChanged(double)),`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:147: d->defaultGlyphScaleSliderWidget->setValue(glyphScale);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:210: double glyphScale = d->defaultGlyphScaleSliderWidget->value();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:277: d->defaultGlyphScaleSliderWidget->setValue(glyphScale);`
- API footprints: `GetDefaultMarkupsDisplayNodeGlyphScale`, `GetDefaultMarkupsDisplayNodeTextScale`

## widget: defaultTextScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default text scale: | defaultTextScaleLabel | QLabel
- Text: Default text scale:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultTextScaleSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Default text scale | defaultTextScaleSliderWidget | ctkSliderWidget
- Tooltip: Default text scale
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:150: QObject::connect(d->defaultTextScaleSliderWidget, SIGNAL(valueChanged(double)),`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:152: d->defaultTextScaleSliderWidget->setValue(textScale);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:220: double textScale = d->defaultTextScaleSliderWidget->value();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:285: d->defaultTextScaleSliderWidget->setValue(glyphScale);`
- API footprints: `GetDefaultMarkupsDisplayNodeOpacity`, `GetDefaultMarkupsDisplayNodeTextScale`

## widget: defaultOpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default opacity: | defaultOpacityLabel | QLabel
- Text: Default opacity:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultOpacitySliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: defaultOpacitySliderWidget | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:155: QObject::connect(d->defaultOpacitySliderWidget, SIGNAL(valueChanged(double)),`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:157: d->defaultOpacitySliderWidget->setValue(opacity);`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:230: double opacity = d->defaultOpacitySliderWidget->value();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:293: d->defaultOpacitySliderWidget->setValue(opacity);`
- API footprints: `GetDefaultMarkupsDisplayNodeOpacity`

## widget: defaultActiveColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default active color: | defaultActiveColorLabel | QLabel
- Text: Default active color:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`

## widget: defaultActiveColorPickerButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkColorPickerButton`
- Search text: defaultActiveColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:200: QColor color = d->defaultActiveColorPickerButton->color();`
  - `Modules/Loadable/Markups/qSlicerMarkupsSettingsPanel.cxx:269: d->defaultActiveColorPickerButton->setColor(color);`
