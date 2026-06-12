# Slicer UI Analysis: Modules/Scripted/LineProfile/Resources/UI/LineProfile.ui

- Owner class: `LineProfile`
- UI file: `Modules/Scripted/LineProfile/Resources/UI/LineProfile.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: LineProfile

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: LineProfile | qMRMLWidget
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Matched implementation lines:
  - `Modules/Scripted/LineProfile/LineProfile.py:19: # LineProfile`
  - `Modules/Scripted/LineProfile/LineProfile.py:23: class LineProfile(ScriptedLoadableModule):`
  - `Modules/Scripted/LineProfile/LineProfile.py:48: class LineProfileParameterNode:`
  - `Modules/Scripted/LineProfile/LineProfile.py:80: # LineProfileWidget`
  - `Modules/Scripted/LineProfile/LineProfile.py:84: class LineProfileWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):`
  - `Modules/Scripted/LineProfile/LineProfile.py:102: uiWidget = slicer.util.loadUI(self.resourcePath("UI/LineProfile.ui"))`
  - `Modules/Scripted/LineProfile/LineProfile.py:113: self.logic = LineProfileLogic()`
  - `Modules/Scripted/LineProfile/LineProfile.py:175: def setParameterNode(self, inputParameterNode: LineProfileParameterNode | None) -> None:`
  - `Modules/Scripted/LineProfile/LineProfile.py:226: # LineProfileLogic`
  - `Modules/Scripted/LineProfile/LineProfile.py:238: class LineProfileLogic(ScriptedLoadableModuleLogic):`
  - `Modules/Scripted/LineProfile/LineProfile.py:258: self._parameterNode = LineProfileParameterNode(parameterNode)`
  - `Modules/Scripted/LineProfile/LineProfile.py:417: distanceArray = LineProfileLogic.getArrayFromTable(outputTable, DISTANCE_ARRAY_NAME)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> inputVolumeSelector.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> inputLineWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> outputTableSelector.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> outputPlotSeriesSelector.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> outputPeaksTableSelector.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetNumberOfPoints`, `GetTable`, `SetNumberOfRows`

## widget: parametersCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Parameters | parametersCollapsibleButton | ctkCollapsibleButton
- Text: Parameters
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: inputVolumeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input Volume: | inputVolumeLabel | QLabel
- Text: Input Volume:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: inputVolumeSelector

- Confidence: `ui_only`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the input to the algorithm which will be sampled along the line. | inputVolumeSelector | qMRMLNodeComboBox
- Tooltip: Pick the input to the algorithm which will be sampled along the line.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode"]}

## widget: inputLineLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input Line: | inputLineLabel | QLabel
- Text: Input Line:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: lineResolutionLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Line Resolution: | lineResolutionLabel | QLabel
- Text: Line Resolution:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: lineResolutionSliderWidget

- Confidence: `ui_only`
- Widget/action class: `ctkSliderWidget`
- Search text: Number of points to sample along the line. | lineResolutionSliderWidget | ctkSliderWidget
- Tooltip: Number of points to sample along the line.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: inputLineWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerSimpleMarkupsWidget`
- Search text: Pick line or curve to take image samples along. | inputLineWidget | qSlicerSimpleMarkupsWidget
- Tooltip: Pick line or curve to take image samples along.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Matched implementation lines:
  - `Modules/Scripted/LineProfile/LineProfile.py:116: self.inputLineSelector = self.ui.inputLineWidget.markupsSelectorComboBox()`
  - `Modules/Scripted/LineProfile/LineProfile.py:122: self.ui.inputLineWidget.tableWidget().setVisible(False)`

## widget: plottingCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced | plottingCollapsibleButton | ctkCollapsibleButton
- Text: Advanced
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: outputTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Output Intensities Table: | outputTableLabel | QLabel
- Text: Output Intensities Table:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: outputTableSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the table that will store the intensity and distance values. | outputTableSelector | qMRMLNodeComboBox
- Tooltip: Pick the table that will store the intensity and distance values.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Matched implementation lines:
  - `Modules/Scripted/LineProfile/LineProfile.py:209: if not self.ui.outputTableSelector.currentNode():`
  - `Modules/Scripted/LineProfile/LineProfile.py:211: self.ui.outputTableSelector.setCurrentNode(outputTableNode)`
- API footprints: `AddNewNodeByClass`
- Key UI properties: {"nodeTypes": ["vtkMRMLTableNode"]}

## widget: outputPlotSeriesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Output Intensities Plot Series: | outputPlotSeriesLabel | QLabel
- Text: Output Intensities Plot Series:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: outputPlotSeriesSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the output plot series to the algorithm. | outputPlotSeriesSelector | qMRMLNodeComboBox
- Tooltip: Pick the output plot series to the algorithm.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Matched implementation lines:
  - `Modules/Scripted/LineProfile/LineProfile.py:212: if self.ui.plotShowCheckBox.checked and not self.ui.outputPlotSeriesSelector.currentNode():`
  - `Modules/Scripted/LineProfile/LineProfile.py:216: self.ui.outputPlotSeriesSelector.setCurrentNode(outputPlotSeriesNode)`
- API footprints: `AddNewNodeByClass`, `SetColor`, `SetMarkerStyle`
- Key UI properties: {"nodeTypes": ["vtkMRMLPlotSeriesNode"]}

## widget: plotProportionalDistanceLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Plot Proportional Distance (%): | plotProportionalDistanceLabel | QLabel
- Text: Plot Proportional Distance (%):
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: plotProportionalDistanceCheckBox

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: If checked, then distance along the line in plot is not absolute, but the percent distance from the start of the line. | plotProportionalDistanceCheckBox | QCheckBox
- Tooltip: If checked, then distance along the line in plot is not absolute, but the percent distance from the start of the line.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Key UI properties: {"checked": "false"}

## widget: plotProportionalDistanceLabel_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show plot: | plotProportionalDistanceLabel_3 | QLabel
- Text: Show plot:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: plotShowCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: If checked, then the intensity profile plot is automatically shown when the intensity profile is updated. | plotShowCheckBox | QCheckBox
- Tooltip: If checked, then the intensity profile plot is automatically shown when the intensity profile is updated.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Matched implementation lines:
  - `Modules/Scripted/LineProfile/LineProfile.py:212: if self.ui.plotShowCheckBox.checked and not self.ui.outputPlotSeriesSelector.currentNode():`
- API footprints: `AddNewNodeByClass`, `SetMarkerStyle`
- Key UI properties: {"checked": "true"}

## widget: peaksCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Peak Detection | peaksCollapsibleButton | ctkCollapsibleButton
- Text: Peak Detection
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: outputPeaksTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Peaks Output Table: | outputPeaksTableLabel | QLabel
- Text: Peaks Output Table:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: outputPeaksTableSelector

- Confidence: `ui_only`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Pick the output table that will store information about each detected peak. | outputPeaksTableSelector | qMRMLNodeComboBox
- Tooltip: Pick the output table that will store information about each detected peak.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Key UI properties: {"nodeTypes": ["vtkMRMLTableNode"]}

## widget: peakMinimumWidthLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Minimum Peak Width: | peakMinimumWidthLabel | QLabel
- Text: Minimum Peak Width:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: peakMinimumWidthSpinBox

- Confidence: `ui_only`
- Widget/action class: `qMRMLSpinBox`
- Search text: Minimum width of the peak. Use higher values to reject small peaks detected due to image noise. | peakMinimumWidthSpinBox | qMRMLSpinBox
- Tooltip: Minimum width of the peak. Use higher values to reject small peaks detected due to image noise.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: heightPercentageForWidthMeasurementLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Height for Width Measurement: | heightPercentageForWidthMeasurementLabel | QLabel
- Text: Height for Width Measurement:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: heightPercentageForWidthMeasurementSpinBox

- Confidence: `ui_only`
- Widget/action class: `qMRMLSpinBox`
- Search text: Height at which the peak width is measured. 50% computes full width at half maximum. Larger value means that the height is measured near the top of the peak. | heightPercentageForWidthMeasurementSpinBox | qMRMLSpinBox
- Tooltip: Height at which the peak width is measured. 50% computes full width at half maximum. Larger value means that the height is measured near the top of the peak.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: peakIsMaximumLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Peak is Maximum: | peakIsMaximumLabel | QLabel
- Text: Peak is Maximum:
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`

## widget: peakIsMaximumCheckBox

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: If checked then peaks are local maximum values. If unchecked then peaks are local minimum values. | peakIsMaximumCheckBox | QCheckBox
- Tooltip: If checked then peaks are local maximum values. If unchecked then peaks are local minimum values.
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Key UI properties: {"checked": "true"}

## widget: applyButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCheckablePushButton`
- Search text: Compute intensity profile | applyButton | ctkCheckablePushButton
- Text: Compute intensity profile
- Implementation candidates: `Modules/Scripted/LineProfile/LineProfile.py`
- Matched implementation lines:
  - `Modules/Scripted/LineProfile/LineProfile.py:130: self.ui.applyButton.clicked.connect(self.onApplyButton)`
  - `Modules/Scripted/LineProfile/LineProfile.py:197: self.ui.applyButton.enabled = True`
  - `Modules/Scripted/LineProfile/LineProfile.py:199: self.ui.applyButton.enabled = False`
- Connected slots/functions: `onApplyButton`
- Key UI properties: {"checkable": "false"}
