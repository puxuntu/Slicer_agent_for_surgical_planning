# Slicer UI Analysis: Applications/SlicerApp/Testing/Python/Resources/UI/ScenePerformance.ui

- Owner class: `ScenePerformance`
- UI file: `Applications/SlicerApp/Testing/Python/Resources/UI/ScenePerformance.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: ScenePerformance

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLWidget`
- Search text: ScenePerformance | qMRMLWidget
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:11: # ScenePerformance`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:15: class ScenePerformance(ScriptedLoadableModule):`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:31: # ScenePerformanceWidget`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:33: class ScenePerformanceWidget(ScriptedLoadableModuleWidget):`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:37: moduleName = "ScenePerformance"`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:39: path = os.path.join(scriptedModulesPath, "Resources", "UI", "ScenePerformance.ui")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:69: tester = ScenePerformanceTest()`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:73: tester = ScenePerformanceTest()`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:80: logic = ScenePerformanceLogic()`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:116: # ScenePerformanceLogic`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:118: class ScenePerformanceLogic(ScriptedLoadableModuleLogic):`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:135: class ScenePerformanceTest(ScriptedLoadableModuleTest):`

## widget: groupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox | QGroupBox
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: FileLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: File | FileLabel | QLabel
- Text: File
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: ActionPathLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `ctkPathLineEdit`
- Search text: ActionPathLineEdit | ctkPathLineEdit
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:52: self.ActionPathLineEdit = self.findWidget(self.parent, "ActionPathLineEdit")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:78: file = self.ActionPathLineEdit.currentPath`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:104: self.ActionPathLineEdit.setEnabled(enableAddData)`

## widget: ActionComboBox

- Confidence: `linked_to_code`
- Widget/action class: `QComboBox`
- Search text: ActionComboBox | QComboBox
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:51: self.ActionComboBox = self.findWidget(self.parent, "ActionComboBox")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:65: self.ActionComboBox.connect("currentIndexChanged(int)", self.updateActionProperties)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:76: if self.ActionComboBox.currentIndex == 0:  # Add Data`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:84: elif self.ActionComboBox.currentIndex == 1:  # Restore`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:87: elif self.ActionComboBox.currentIndex == 3:  # Layout`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:90: elif self.ActionComboBox.currentIndex == 2:  # Close`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:93: elif self.ActionComboBox.currentIndex == 4:  # Add Node`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:97: elif self.ActionComboBox.currentIndex == 5:  # Modify Node`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:103: enableAddData = True if self.ActionComboBox.currentIndex == 0 else False`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:107: self.SceneViewSpinBox.setEnabled(True if self.ActionComboBox.currentIndex == 1 else False)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:108: self.LayoutSpinBox.setEnabled(True if self.ActionComboBox.currentIndex == 3 else False)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:109: self.MRMLNodeComboBox.setEnabled(True if self.ActionComboBox.currentIndex == 4 or self.ActionComboBox.currentIndex == 5 else False)`

## widget: URLLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: URL | URLLabel | QLabel
- Text: URL
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: ResultsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Results | ResultsLabel | QLabel
- Text: Results
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: ResultsTextEdit

- Confidence: `linked_to_code`
- Widget/action class: `QTextEdit`
- Search text: ResultsTextEdit | QTextEdit
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:53: self.ResultsTextEdit = self.findWidget(self.parent, "ResultsTextEdit")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:83: self.ResultsTextEdit.append(results)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:86: self.ResultsTextEdit.append(results)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:89: self.ResultsTextEdit.append(results)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:92: self.ResultsTextEdit.append(results)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:96: self.ResultsTextEdit.append(results)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:100: self.ResultsTextEdit.append(results)`

## widget: LayoutLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Layout | LayoutLabel | QLabel
- Text: Layout
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: LayoutSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `QSpinBox`
- Search text: LayoutSpinBox | QSpinBox
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:57: self.LayoutSpinBox = self.findWidget(self.parent, "LayoutSpinBox")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:88: results = tester.setLayout(self.LayoutSpinBox.value)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:108: self.LayoutSpinBox.setEnabled(True if self.ActionComboBox.currentIndex == 3 else False)`

## widget: URLLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: URLLineEdit | QLineEdit
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:54: self.URLLineEdit = self.findWidget(self.parent, "URLLineEdit")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:77: if self.URLLineEdit.text == "":`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:81: file = logic.downloadFile(self.URLLineEdit.text, self.URLFileNameLineEdit.text)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:105: self.URLLineEdit.setEnabled(enableAddData)`

## widget: URLFileNameLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: file name: | URLFileNameLabel | QLabel
- Text: file name:
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: URLFileNameLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: URLFileNameLineEdit | QLineEdit
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:55: self.URLFileNameLineEdit = self.findWidget(self.parent, "URLFileNameLineEdit")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:81: file = logic.downloadFile(self.URLLineEdit.text, self.URLFileNameLineEdit.text)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:106: self.URLFileNameLineEdit.setEnabled(enableAddData)`

## widget: MRMLNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Node | MRMLNodeLabel | QLabel
- Text: Node
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: MRMLNodeComboBox

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:58: self.MRMLNodeComboBox = self.findWidget(self.parent, "MRMLNodeComboBox")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:62: # self.MRMLNodeComboBox.setMRMLScene(slicer.mrmlScene)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:94: node = self.MRMLNodeComboBox.currentNode()`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:98: node = self.MRMLNodeComboBox.currentNode()`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:109: self.MRMLNodeComboBox.setEnabled(True if self.ActionComboBox.currentIndex == 4 or self.ActionComboBox.currentIndex == 5 else False)`

## widget: TimePushButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Run and time | TimePushButton | QPushButton
- Text: Run and time
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:50: self.TimePushButton = self.findWidget(self.parent, "TimePushButton")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:64: self.TimePushButton.connect("clicked()", self.timeAction)`

## widget: RepeatSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `QSpinBox`
- Search text: RepeatSpinBox | QSpinBox
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:59: self.RepeatSpinBox = self.findWidget(self.parent, "RepeatSpinBox")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:75: tester.setRepeat(self.RepeatSpinBox.value)`

## widget: SceneViewLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: SceneView | SceneViewLabel | QLabel
- Text: SceneView
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`

## widget: SceneViewSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `QSpinBox`
- Search text: SceneViewSpinBox | QSpinBox
- Implementation candidates: `Applications/SlicerApp/Testing/Python/ScenePerformance.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:56: self.SceneViewSpinBox = self.findWidget(self.parent, "SceneViewSpinBox")`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:85: results = tester.restoreSceneView(self.SceneViewSpinBox.value)`
  - `Applications/SlicerApp/Testing/Python/ScenePerformance.py:107: self.SceneViewSpinBox.setEnabled(True if self.ActionComboBox.currentIndex == 1 else False)`
