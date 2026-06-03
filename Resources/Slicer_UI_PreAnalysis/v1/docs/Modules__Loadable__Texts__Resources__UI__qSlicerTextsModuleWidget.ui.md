# Slicer UI Analysis: Modules/Loadable/Texts/Resources/UI/qSlicerTextsModuleWidget.ui

- Owner class: `qSlicerTextsModuleWidget`
- UI file: `Modules/Loadable/Texts/Resources/UI/qSlicerTextsModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTextsModuleWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerTextsModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:22: #include "qSlicerTextsModuleWidget.h"`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:23: #include "ui_qSlicerTextsModuleWidget.h"`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:32: class qSlicerTextsModuleWidgetPrivate : public Ui_qSlicerTextsModuleWidget`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:34: Q_DECLARE_PUBLIC(qSlicerTextsModuleWidget);`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:37: qSlicerTextsModuleWidget* const q_ptr;`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:40: qSlicerTextsModuleWidgetPrivate(qSlicerTextsModuleWidget& object);`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:45: qSlicerTextsModuleWidgetPrivate::qSlicerTextsModuleWidgetPrivate(qSlicerTextsModuleWidget& object)`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:51: vtkSlicerTextsLogic* qSlicerTextsModuleWidgetPrivate::logic() const`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:53: Q_Q(const qSlicerTextsModuleWidget);`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:58: qSlicerTextsModuleWidget::qSlicerTextsModuleWidget(QWidget* _parentWidget)`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:60: , d_ptr(new qSlicerTextsModuleWidgetPrivate(*this))`
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:65: qSlicerTextsModuleWidget::~qSlicerTextsModuleWidget() = default;`

## widget: TextNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Text node: | TextNodeLabel | QLabel
- Text: Text node:
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`

## widget: TextNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: TextNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx:83: d->TextNodeSelector->setCurrentNode(node);`
- API footprints: `vtkMRMLTextNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTextNode"]}

## widget: ContentsCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `qMRMLCollapsibleButton`
- Search text: Contents | ContentsCollapsibleButton | qMRMLCollapsibleButton
- Text: Contents
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`

## widget: TextWidget

- Confidence: `ui_only`
- Widget/action class: `qMRMLTextWidget`
- Search text: TextWidget | qMRMLTextWidget
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`

## widget: CollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced | CollapsibleButton | ctkCollapsibleButton
- Text: Advanced
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`

## widget: AutoSaveCheckBox

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: Auto-save edits to the text node | <html><head/><body><p>If checked, the text node is immediately updated as the contents are edited. If unchecked, text node is updated only when &quot;Save&quot; is clicked.</p></body></html> | AutoSaveCheckBox | QCheckBox
- Text: Auto-save edits to the text node
- Tooltip: <html><head/><body><p>If checked, the text node is immediately updated as the contents are edited. If unchecked, text node is updated only when &quot;Save&quot; is clicked.</p></body></html>
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`

## widget: WordWrapCheckBox

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: Enable word wrapping | WordWrapCheckBox | QCheckBox
- Text: Enable word wrapping
- Implementation candidates: `Modules/Loadable/Texts/qSlicerTextsModuleWidget.cxx`, `Modules/Loadable/Texts/qSlicerTextsModuleWidget.h`
- Key UI properties: {"checked": "true"}
