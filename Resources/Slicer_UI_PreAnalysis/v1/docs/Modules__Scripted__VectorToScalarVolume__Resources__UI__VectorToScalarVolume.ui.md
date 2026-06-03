# Slicer UI Analysis: Modules/Scripted/VectorToScalarVolume/Resources/UI/VectorToScalarVolume.ui

- Owner class: `VectorToScalarVolume`
- UI file: `Modules/Scripted/VectorToScalarVolume/Resources/UI/VectorToScalarVolume.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: VectorToScalarVolume

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLWidget`
- Search text: VectorToScalarVolume | qMRMLWidget
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`
- Matched implementation lines:
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:46: # VectorToScalarVolume`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:50: class VectorToScalarVolume(ScriptedLoadableModule):`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:82: # VectorToScalarVolumeParameterNode`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:102: class VectorToScalarVolumeParameterNode:`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:110: # VectorToScalarVolumeWidget`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:112: class VectorToScalarVolumeWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:117: _parameterNode: VectorToScalarVolumeParameterNode | None`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:133: uiWidget = slicer.util.loadUI(self.resourcePath("UI/VectorToScalarVolume.ui"))`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:150: self.logic = VectorToScalarVolumeLogic()`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:216: inputParameterNode = VectorToScalarVolumeParameterNode(inputParameterNode)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:295: # VectorToScalarVolumeLogic`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:299: class VectorToScalarVolumeLogic(ScriptedLoadableModuleLogic):`

## widget: selectionCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Parameters | selectionCollapsibleButton | ctkCollapsibleButton
- Text: Parameters
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input vector volume: | label | QLabel
- Text: Input vector volume:
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`

## widget: inputSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the input to the algorithm. | inputSelector | qMRMLNodeComboBox
- Tooltip: Pick the input to the algorithm.
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`
- Matched implementation lines:
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:160: self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:243: self.ui.inputSelector.setCurrentNode(self._parameterNode.InputVolume)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:277: self._parameterNode.InputVolume = self.ui.inputSelector.currentNode()`
- API footprints: `NodeModify`
- Key UI properties: {"nodeTypes": ["vtkMRMLVectorVolumeNode"]}

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Conversion Method:  | label_3 | QLabel
- Text: Conversion Method: 
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Output scalar Volume: | label_2 | QLabel
- Text: Output scalar Volume:
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`

## widget: outputSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the output to the algorithm. | outputSelector | qMRMLNodeComboBox
- Tooltip: Pick the output to the algorithm.
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`
- Matched implementation lines:
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:161: self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:244: self.ui.outputSelector.setCurrentNode(self._parameterNode.OutputVolume)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:278: self._parameterNode.OutputVolume = self.ui.outputSelector.currentNode()`
- API footprints: `NodeModify`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: methodSelectorComboBox

- Confidence: `linked_to_code`
- Widget/action class: `QComboBox`
- Search text: methodSelectorComboBox | QComboBox
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`
- Matched implementation lines:
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:140: self.ui.methodSelectorComboBox.addItem(title, method)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:141: self.ui.methodSelectorComboBox.setItemData(i, tooltip, qt.Qt.ToolTipRole)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:162: self.ui.methodSelectorComboBox.connect("currentIndexChanged(int)", self.updateParameterNodeFromGUI)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:245: self.ui.methodSelectorComboBox.setCurrentIndex(`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:246: self.ui.methodSelectorComboBox.findData(self._parameterNode.ConversionMethod))`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:279: self._parameterNode.ConversionMethod = self.ui.methodSelectorComboBox.currentData`

## widget: componentsSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `QSpinBox`
- Search text: componentsSpinBox | QSpinBox
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`
- Matched implementation lines:
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:163: self.ui.componentsSpinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:247: self.ui.componentsSpinBox.value = self._parameterNode.ComponentToExtract`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:250: self.ui.componentsSpinBox.visible = isMethodSingleComponent`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:280: self._parameterNode.ComponentToExtract = self.ui.componentsSpinBox.value`

## widget: applyButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Apply | applyButton | QPushButton
- Text: Apply
- Implementation candidates: `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py`
- Matched implementation lines:
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:166: self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:260: self.ui.applyButton.enabled = not applyErrorMessage`
  - `Modules/Scripted/VectorToScalarVolume/VectorToScalarVolume.py:261: self.ui.applyButton.toolTip = applyErrorMessage`
