# Slicer UI Analysis: Applications/SlicerApp/Testing/Python/Resources/UI/UtilTest.ui

- Owner class: `UtilTest`
- UI file: `Applications/SlicerApp/Testing/Python/Resources/UI/UtilTest.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: UtilTest

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: UtilTest | QWidget
- Implementation candidates: `Applications/SlicerApp/Testing/Python/UtilTest.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:11: # UtilTest`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:15: class UtilTest(ScriptedLoadableModule):`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:18: parent.title = "UtilTest"  # TODO make this more human readable by adding spaces`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:29: # UtilTestWidget`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:33: class UtilTestWidget(ScriptedLoadableModuleWidget):`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:41: moduleName = "UtilTest"`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:50: # UtilTestLogic`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:54: class UtilTestLogic(ScriptedLoadableModuleLogic):`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:60: # UtilTestLogic`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:64: class UtilTestTest(ScriptedLoadableModuleTest):`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:165: utilWidget = UtilTestWidget()`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:168: label = slicer.util.findChild(utilWidget.parent, "UtilTest_Label")`

## widget: UtilTest_Label

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: My custom UI | UtilTest_Label | QLabel
- Text: My custom UI
- Implementation candidates: `Applications/SlicerApp/Testing/Python/UtilTest.py`
- Matched implementation lines:
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:168: label = slicer.util.findChild(utilWidget.parent, "UtilTest_Label")`
  - `Applications/SlicerApp/Testing/Python/UtilTest.py:180: label = slicer.util.findChild(utilWidget.Widget, "UtilTest_Label")`
