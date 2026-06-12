# Slicer UI Analysis: Modules/Scripted/DataProbe/DataProbeLib/Resources/UI/settings.ui

- Owner class: `Settings`
- UI file: `Modules/Scripted/DataProbe/DataProbeLib/Resources/UI/settings.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: Settings

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: Settings | QWidget
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbe.py:555: settingsCollapsibleButton.text = _("Slice View Annotations Settings")`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:198: settings = qt.QSettings()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:212: settings = qt.QSettings()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:220: settings = qt.QSettings()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:232: settings = qt.QSettings()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:246: settings = qt.QSettings()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:253: settings = qt.QSettings()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:286: settings = qt.QSettings()`
- API footprints: `QSettings`, `QVBoxLayout`

## widget: sliceViewAnnotationsCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable Slice View Annotations | sliceViewAnnotationsCheckBox | QCheckBox
- Text: Enable Slice View Annotations
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:134: self.sliceViewAnnotationsCheckBox = find(window, "sliceViewAnnotationsCheckBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:135: self.sliceViewAnnotationsCheckBox.checked = self.sliceViewAnnotationsEnabled`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:173: self.sliceViewAnnotationsCheckBox.connect("clicked()", self.onSliceViewAnnotationsCheckBox)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:196: self.sliceViewAnnotationsEnabled = int(self.sliceViewAnnotationsCheckBox.checked)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:262: self.sliceViewAnnotationsCheckBox.checked = _defaultValue("enabled")`
- API footprints: `QSettings`

## widget: cornerTextParametersCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Corner Text Annotation | cornerTextParametersCollapsibleButton | ctkCollapsibleButton
- Text: Corner Text Annotation
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:133: self.cornerTextParametersCollapsibleButton = find(window, "cornerTextParametersCollapsibleButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:308: self.cornerTextParametersCollapsibleButton.enabled = enabled`

## widget: activateCornersGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `QGroupBox`
- Search text: activateCornersGroupBox | QGroupBox
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:137: self.activateCornersGroupBox = find(window, "activateCornersGroupBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:309: self.activateCornersGroupBox.enabled = enabled`

## widget: topLeftCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Top Left | topLeftCheckBox | QCheckBox
- Text: Top Left
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:138: self.topLeftCheckBox = find(window, "topLeftCheckBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:139: self.topLeftCheckBox.checked = self.topLeft`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:175: self.topLeftCheckBox.connect("clicked()", self.onCornerTextsActivationCheckBox)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:226: self.topLeft = int(self.topLeftCheckBox.checked)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:270: self.topLeftCheckBox.checked = _defaultValue("topLeft")`
- Key UI properties: {"checked": "true"}

## widget: topRightCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Top Right | topRightCheckBox | QCheckBox
- Text: Top Right
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:140: self.topRightCheckBox = find(window, "topRightCheckBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:141: self.topRightCheckBox.checked = self.topRight`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:176: self.topRightCheckBox.connect("clicked()", self.onCornerTextsActivationCheckBox)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:227: self.topRight = int(self.topRightCheckBox.checked)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:273: self.topRightCheckBox.checked = _defaultValue("topRight")`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:491: self.topRightCheckBox.checked = True`
- API footprints: `GetSlabReconstructionEnabled`
- Key UI properties: {"checked": "true"}

## widget: bottomLeftCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Bottom Left | bottomLeftCheckBox | QCheckBox
- Text: Bottom Left
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:143: self.bottomLeftCheckBox = find(window, "bottomLeftCheckBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:144: self.bottomLeftCheckBox.checked = self.bottomLeft`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:177: self.bottomLeftCheckBox.connect("clicked()", self.onCornerTextsActivationCheckBox)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:228: self.bottomLeft = int(self.bottomLeftCheckBox.checked)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:276: self.bottomLeftCheckBox.checked = _defaultValue("bottomLeft")`
- Key UI properties: {"checked": "true"}

## widget: annotationsAmountGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: annotationsAmountGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:166: self.annotationsAmountGroupBox = find(window, "annotationsAmountGroupBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:311: self.annotationsAmountGroupBox.enabled = enabled`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Annotation Display Level: | label | QLabel
- Text: Annotation Display Level:
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbe.py:143: labelIndex = int(imageData.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], 0))`
  - `Modules/Scripted/DataProbe/DataProbe.py:144: labelValue = _("Unknown")`
  - `Modules/Scripted/DataProbe/DataProbe.py:149: labelValue = colorNode.GetColorName(labelIndex)`
  - `Modules/Scripted/DataProbe/DataProbe.py:150: return "%s (%d)" % (labelValue, labelIndex)`
  - `Modules/Scripted/DataProbe/DataProbe.py:179: # default - non label scalar volume`
  - `Modules/Scripted/DataProbe/DataProbe.py:477: # this method makes labels`
  - `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py:44: # node.SetParameter( "label", "1" )`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:415: labelLayer = sliceLogic.GetLabelLayer()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:420: labelVolume = labelLayer.GetVolumeNode()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:510: if (labelVolume is not None) and self.bottomLeft:`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:511: labelOpacity = sliceCompositeNode.GetLabelOpacity()`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:512: labelVolumeName = labelVolume.GetName()`
- API footprints: `AddNode`, `GetBackgroundLayer`, `GetColorName`, `GetColorNode`, `GetDisplayNode`, `GetForegroundLayer`, `GetLabelLayer`, `GetLabelOpacity`, `GetName`, `GetNumberOfScalarComponents`, `GetScalarComponentAsDouble`, `GetScalarInvariantAsString`, `GetVolumeNode`, `IsA`, `QFrame`, `QGridLayout`, `SetModuleName`, `SetParameter`, `SetSingletonTag`

## widget: level1RadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: 1 | level1RadioButton | QRadioButton
- Text: 1
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:146: self.level1RadioButton = find(window, "level1RadioButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:149: radioButtons = [self.level1RadioButton, self.level2RadioButton, self.level3RadioButton]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:182: self.level1RadioButton.connect("clicked()", self.onDisplayDisplayLevelRadioButton)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:205: if self.level1RadioButton.checked:`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:266: radioButtons = [self.level1RadioButton, self.level2RadioButton, self.level3RadioButton]`
- Key UI properties: {"checked": "true"}

## widget: level2RadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: 2 | level2RadioButton | QRadioButton
- Text: 2
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:147: self.level2RadioButton = find(window, "level2RadioButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:149: radioButtons = [self.level1RadioButton, self.level2RadioButton, self.level3RadioButton]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:183: self.level2RadioButton.connect("clicked()", self.onDisplayDisplayLevelRadioButton)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:207: elif self.level2RadioButton.checked:`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:266: radioButtons = [self.level1RadioButton, self.level2RadioButton, self.level3RadioButton]`

## widget: level3RadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: 3 | level3RadioButton | QRadioButton
- Text: 3
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:148: self.level3RadioButton = find(window, "level3RadioButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:149: radioButtons = [self.level1RadioButton, self.level2RadioButton, self.level3RadioButton]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:184: self.level3RadioButton.connect("clicked()", self.onDisplayDisplayLevelRadioButton)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:209: elif self.level3RadioButton.checked:`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:266: radioButtons = [self.level1RadioButton, self.level2RadioButton, self.level3RadioButton]`

## widget: fontPropertiesGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: fontPropertiesGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:152: self.fontPropertiesGroupBox = find(window, "fontPropertiesGroupBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:310: self.fontPropertiesGroupBox.enabled = enabled`

## widget: fontFamilyLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Font Family:  | fontFamilyLabel | QLabel
- Text: Font Family: 
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`

## widget: timesFontRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Times | timesFontRadioButton | QRadioButton
- Text: Times
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:153: self.timesFontRadioButton = find(window, "timesFontRadioButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:156: self.timesFontRadioButton.checked = True`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:178: self.timesFontRadioButton.connect("clicked()", self.onFontFamilyRadioButton)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:242: if self.timesFontRadioButton.checked:`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:280: self.timesFontRadioButton.checked = _defaultValue("fontFamily") == "Times"`
- Key UI properties: {"checked": "true"}

## widget: arialFontRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Arial | arialFontRadioButton | QRadioButton
- Text: Arial
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:154: self.arialFontRadioButton = find(window, "arialFontRadioButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:158: self.arialFontRadioButton.checked = True`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:179: self.arialFontRadioButton.connect("clicked()", self.onFontFamilyRadioButton)`

## widget: fontSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Font Size:  | fontSizeLabel | QLabel
- Text: Font Size: 
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`

## widget: fontSizeSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: fontSizeSpinBox | QSpinBox
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:160: self.fontSizeSpinBox = find(window, "fontSizeSpinBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:161: self.fontSizeSpinBox.value = self.fontSize`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:180: self.fontSizeSpinBox.connect("valueChanged(int)", self.onFontSizeSpinBox)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:252: self.fontSize = self.fontSizeSpinBox.value`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:279: self.fontSizeSpinBox.value = _defaultValue("fontSize")`
- API footprints: `QSettings`

## widget: dicomAnnotationsCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: dicomAnnotationsCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`

## widget: backgroundPersistenceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Background DICOM annotations persistence | Show background volume DICOM annotations if foreground volume is non-DICOM. | backgroundPersistenceCheckBox | QCheckBox
- Text: Background DICOM annotations persistence
- Tooltip: Show background volume DICOM annotations if foreground volume is non-DICOM.
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:163: self.backgroundPersistenceCheckBox = find(window, "backgroundPersistenceCheckBox")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:164: self.backgroundPersistenceCheckBox.checked = self.backgroundDICOMAnnotationsPersistence`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:186: self.backgroundPersistenceCheckBox.connect("clicked()", self.onBackgroundLayerPersistenceCheckBox)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:219: self.backgroundDICOMAnnotationsPersistence = int(self.backgroundPersistenceCheckBox.checked)`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:284: self.backgroundPersistenceCheckBox.checked = _defaultValue("bgDICOMAnnotationsPersistence")`
- API footprints: `QSettings`

## widget: restoreDefaultsButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Restore Defaults | restoreDefaultsButton | QPushButton
- Text: Restore Defaults
- Implementation candidates: `Modules/Scripted/DataProbe/DataProbe.py`, `Modules/Scripted/DataProbe/DataProbeLib/__init__.py`, `Modules/Scripted/DataProbe/DataProbeLib/DataProbeUtil.py`, `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py`
- Matched implementation lines:
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:168: self.restoreDefaultsButton = find(window, "restoreDefaultsButton")[0]`
  - `Modules/Scripted/DataProbe/DataProbeLib/SliceViewAnnotations.py:188: self.restoreDefaultsButton.connect("clicked()", self.restoreDefaultValues)`
