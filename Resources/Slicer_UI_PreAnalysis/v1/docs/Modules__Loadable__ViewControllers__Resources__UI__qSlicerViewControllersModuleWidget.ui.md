# Slicer UI Analysis: Modules/Loadable/ViewControllers/Resources/UI/qSlicerViewControllersModuleWidget.ui

- Owner class: `qSlicerViewControllersModuleWidget`
- UI file: `Modules/Loadable/ViewControllers/Resources/UI/qSlicerViewControllersModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerViewControllersModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerViewControllersModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:33: #include "qSlicerViewControllersModuleWidget.h"`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:34: #include "ui_qSlicerViewControllersModuleWidget.h"`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:52: class qSlicerViewControllersModuleWidgetPrivate : public Ui_qSlicerViewControllersModuleWidget`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:54: Q_DECLARE_PUBLIC(qSlicerViewControllersModuleWidget);`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:57: qSlicerViewControllersModuleWidget* const q_ptr;`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:60: qSlicerViewControllersModuleWidgetPrivate(qSlicerViewControllersModuleWidget& obj);`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:61: virtual ~qSlicerViewControllersModuleWidgetPrivate();`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:76: qSlicerViewControllersModuleWidgetPrivate::qSlicerViewControllersModuleWidgetPrivate(qSlicerViewControllersModuleWidget& object)`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:82: qSlicerViewControllersModuleWidgetPrivate::~qSlicerViewControllersModuleWidgetPrivate() = default;`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:85: void qSlicerViewControllersModuleWidgetPrivate::createController(vtkMRMLNode* n, qSlicerLayoutManager* layoutManager)`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:87: Q_Q(qSlicerViewControllersModuleWidget);`
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:91: qDebug() << "qSlicerViewControllersModuleWidgetPrivate::createController - Node already added to module";`
- API footprints: `GetLayoutName`, `GetName`, `IsBatchProcessing`, `vtkMRMLSliceNode::SafeDownCast`

## widget: SliceControllersCollapsibleButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Slice Controllers | SliceControllersCollapsibleButton | ctkCollapsibleButton
- Text: Slice Controllers
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:100: qMRMLSliceControllerWidget* widget = new qMRMLSliceControllerWidget(this->SliceControllersCollapsibleButton);`
- API footprints: `GetLayoutLabel`, `GetName`

## widget: ThreeDViewControllersCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: 3D View Controllers | ThreeDViewControllersCollapsibleButton | ctkCollapsibleButton
- Text: 3D View Controllers
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:126: qMRMLThreeDViewControllerWidget* widget = new qMRMLThreeDViewControllerWidget(this->ThreeDViewControllersCollapsibleButton);`

## widget: PlotViewControllersCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Plot View Controllers | PlotViewControllersCollapsibleButton | ctkCollapsibleButton
- Text: Plot View Controllers
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:141: qMRMLPlotViewControllerWidget* widget = new qMRMLPlotViewControllerWidget(this->PlotViewControllersCollapsibleButton);`

## widget: AdvancedCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced | AdvancedCollapsibleButton | ctkCollapsibleButton
- Text: Advanced
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:220: d->AdvancedCollapsibleButton->setCollapsed(true);`

## widget: MRMLViewNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select a view from the current scene. Each element corresponds to a specific widget. View nodes are connected with 3D rendering widgets. PlotView with Plotting widgets. Slices (Red, Green, Yellow) with 2D rendering widgets. | MRMLViewNodeComboBox | qMRMLNodeComboBox
- Tooltip: Select a view from the current scene. Each element corresponds to a specific widget. View nodes are connected with 3D rendering widgets. PlotView with Plotting widgets. Slices (Red, Green, Yellow) with 2D rendering widgets.
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:218: connect(d->MRMLViewNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onAdvancedViewNodeChanged(vtkMRMLNode*)));`
- Connected slots/functions: `onAdvancedViewNodeChanged`
- API footprints: `vtkMRMLSliceNode::SafeDownCast`, `vtkMRMLViewNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSliceNode", "vtkMRMLViewNode", "vtkMRMLPlotViewNode"]}

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View Node: | label | QLabel
- Text: View Node:
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`

## widget: MRMLSliceInformationWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliceInformationWidget`
- Search text: MRMLSliceInformationWidget | qMRMLSliceInformationWidget
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:449: d->MRMLSliceInformationWidget->setVisible(vtkMRMLSliceNode::SafeDownCast(viewNode) != nullptr);`
- API footprints: `vtkMRMLSliceNode::SafeDownCast`, `vtkMRMLViewNode::SafeDownCast`

## widget: MRMLThreeDViewInformationWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLThreeDViewInformationWidget`
- Search text: MRMLThreeDViewInformationWidget | qMRMLThreeDViewInformationWidget
- Implementation candidates: `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx`, `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/ViewControllers/qSlicerViewControllersModuleWidget.cxx:450: d->MRMLThreeDViewInformationWidget->setVisible(vtkMRMLViewNode::SafeDownCast(viewNode) != nullptr);`
- API footprints: `vtkMRMLSliceNode::SafeDownCast`, `vtkMRMLViewNode::SafeDownCast`
