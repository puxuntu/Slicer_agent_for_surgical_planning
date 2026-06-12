# Slicer UI Analysis: Utilities/Templates/Modules/Scripted/Resources/UI/TemplateKey.ui

- Owner class: `TemplateKey`
- UI file: `Utilities/Templates/Modules/Scripted/Resources/UI/TemplateKey.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: TemplateKey

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLWidget`
- Search text: TemplateKey | qMRMLWidget
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:21: # TemplateKey`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:25: class TemplateKey(ScriptedLoadableModule):`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:32: self.parent.title = _("TemplateKey")  # TODO: make this more human readable by adding spaces`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:41: See more information in <a href="https://github.com/organization/projectname#TemplateKey">module documentation</a>.`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:70: # TemplateKey1`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:73: category="TemplateKey",`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:74: sampleName="TemplateKey1",`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:77: thumbnailFileName=os.path.join(iconsPath, "TemplateKey1.png"),`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:80: fileNames="TemplateKey1.nrrd",`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:85: nodeNames="TemplateKey1",`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:88: # TemplateKey2`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:91: category="TemplateKey",`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> inputSelector.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> outputSelector.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> invertedOutputSelector.setMRMLScene(vtkMRMLScene*)`

## widget: inputsCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Inputs | inputsCollapsibleButton | ctkCollapsibleButton
- Text: Inputs
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input volume: | label | QLabel
- Text: Input volume:
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: inputSelector

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the input to the algorithm. | inputSelector | qMRMLNodeComboBox
- Tooltip: Pick the input to the algorithm.
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:246: self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:252: self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Image threshold: | label_3 | QLabel
- Text: Image threshold:
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: imageThresholdSliderWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkSliderWidget`
- Search text: Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero. | imageThresholdSliderWidget | ctkSliderWidget
- Tooltip: Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:247: self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:253: self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)`

## widget: outputsCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Outputs | outputsCollapsibleButton | ctkCollapsibleButton
- Text: Outputs
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Thresholded volume: | label_2 | QLabel
- Text: Thresholded volume:
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: outputSelector

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the output to the algorithm. | outputSelector | qMRMLNodeComboBox
- Tooltip: Pick the output to the algorithm.
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:246: self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Inverted volume: | label_5 | QLabel
- Text: Inverted volume:
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: invertedOutputSelector

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Result with inverted threshold will be written into this volume | invertedOutputSelector | qMRMLNodeComboBox
- Tooltip: Result with inverted threshold will be written into this volume
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:250: if self.ui.invertedOutputSelector.currentNode():`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:252: self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: advancedCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced | advancedCollapsibleButton | ctkCollapsibleButton
- Text: Advanced
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Invert threshold:  | label_4 | QLabel
- Text: Invert threshold: 
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`

## widget: invertOutputCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: If checked, values above threshold are set to 0. If unchecked, values below are set to 0. | invertOutputCheckBox | QCheckBox
- Tooltip: If checked, values above threshold are set to 0. If unchecked, values below are set to 0.
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:247: self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:253: self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)`

## widget: applyButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Apply | Run the algorithm. | applyButton | QPushButton
- Text: Apply
- Tooltip: Run the algorithm.
- Implementation candidates: `Utilities/Templates/Modules/Scripted/TemplateKey.py`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:171: self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:236: self.ui.applyButton.toolTip = _("Compute output volume")`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:237: self.ui.applyButton.enabled = True`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:239: self.ui.applyButton.toolTip = _("Select input and output volume nodes")`
  - `Utilities/Templates/Modules/Scripted/TemplateKey.py:240: self.ui.applyButton.enabled = False`
