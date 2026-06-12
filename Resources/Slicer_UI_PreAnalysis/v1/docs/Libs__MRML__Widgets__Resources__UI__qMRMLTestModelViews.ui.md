# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLTestModelViews.ui

- Owner class: `Form`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLTestModelViews.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: Form

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: Form | QWidget

## widget: MRMLSceneFactoryWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSceneFactoryWidget`
- Search text: MRMLSceneFactoryWidget | qMRMLSceneFactoryWidget
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> MRMLListWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> MRMLTreeView.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox.setMRMLScene(vtkMRMLScene*)`

## widget: MRMLNodeComboBox

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx`, `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:21: #include "qMRMLNodeComboBoxPlugin.h"`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:22: #include "qMRMLNodeComboBox.h"`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:24: qMRMLNodeComboBoxPlugin::qMRMLNodeComboBoxPlugin(QObject* _parent)`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:29: QWidget* qMRMLNodeComboBoxPlugin::createWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:31: qMRMLNodeComboBox* _widget = new qMRMLNodeComboBox(_parent);`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:35: QString qMRMLNodeComboBoxPlugin::domXml() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:38: "<widget class=\"qMRMLNodeComboBox\" name=\"MRMLNodeComboBox\">\n"`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:46: QIcon qMRMLNodeComboBoxPlugin::icon() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:51: QString qMRMLNodeComboBoxPlugin::includeFile() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:53: return "qMRMLNodeComboBox.h";`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:56: bool qMRMLNodeComboBoxPlugin::isContainer() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLNodeComboBoxPlugin.cxx:61: QString qMRMLNodeComboBoxPlugin::name() const`
- Key UI properties: {"nodeTypes": ["vtkMRMLCameraNode"]}

## widget: MRMLListWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLListWidget`
- Search text: MRMLListWidget | qMRMLListWidget
- Implementation candidates: `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx`, `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:21: #include "qMRMLListWidgetPlugin.h"`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:22: #include "qMRMLListWidget.h"`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:24: qMRMLListWidgetPlugin::qMRMLListWidgetPlugin(QObject* _parent)`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:29: QWidget* qMRMLListWidgetPlugin::createWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:31: qMRMLListWidget* _widget = new qMRMLListWidget(_parent);`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:35: QString qMRMLListWidgetPlugin::domXml() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:37: return "<widget class=\"qMRMLListWidget\" \`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:38: name=\"MRMLListWidget\">\n"`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:42: QIcon qMRMLListWidgetPlugin::icon() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:47: QString qMRMLListWidgetPlugin::includeFile() const`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:49: return "qMRMLListWidget.h";`
  - `Libs/MRML/Widgets/DesignerPlugins/qMRMLListWidgetPlugin.cxx:52: bool qMRMLListWidgetPlugin::isContainer() const`

## widget: MRMLTreeView

- Confidence: `ui_only`
- Widget/action class: `qMRMLTreeView`
- Search text: MRMLTreeView | qMRMLTreeView
