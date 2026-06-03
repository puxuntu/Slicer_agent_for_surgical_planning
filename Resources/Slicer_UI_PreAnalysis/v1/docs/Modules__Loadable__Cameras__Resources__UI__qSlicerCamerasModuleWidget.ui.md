# Slicer UI Analysis: Modules/Loadable/Cameras/Resources/UI/qSlicerCamerasModuleWidget.ui

- Owner class: `qSlicerCamerasModuleWidget`
- UI file: `Modules/Loadable/Cameras/Resources/UI/qSlicerCamerasModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerCamerasModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerCamerasModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx`, `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:22: #include "qSlicerCamerasModuleWidget.h"`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:23: #include "ui_qSlicerCamerasModuleWidget.h"`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:34: class qSlicerCamerasModuleWidgetPrivate : public Ui_qSlicerCamerasModuleWidget`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:40: qSlicerCamerasModuleWidget::qSlicerCamerasModuleWidget(QWidget* _parent)`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:42: , d_ptr(new qSlicerCamerasModuleWidgetPrivate)`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:47: qSlicerCamerasModuleWidget::~qSlicerCamerasModuleWidget() = default;`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:50: void qSlicerCamerasModuleWidget::setup()`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:52: Q_D(qSlicerCamerasModuleWidget);`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:63: void qSlicerCamerasModuleWidget::onCurrentViewNodeChanged(vtkMRMLNode* mrmlNode)`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:70: void qSlicerCamerasModuleWidget::synchronizeCameraWithView()`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:72: Q_D(qSlicerCamerasModuleWidget);`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:78: void qSlicerCamerasModuleWidget::synchronizeCameraWithView(vtkMRMLViewNode* currentViewNode)`
- API footprints: `vtkMRMLCameraNode::SafeDownCast`, `vtkMRMLViewNode::SafeDownCast`

## widget: CameraCollapsibleWidget

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Camera | CameraCollapsibleWidget | ctkCollapsibleButton
- Text: Camera
- Implementation candidates: `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx`, `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.h`

## widget: ViewNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View: | ViewNodeLabel | QLabel
- Text: View:
- Implementation candidates: `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx`, `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.h`

## widget: ViewNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ViewNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx`, `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:56: connect(d->ViewNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onCurrentViewNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:73: vtkMRMLViewNode* currentViewNode = vtkMRMLViewNode::SafeDownCast(d->ViewNodeSelector->currentNode());`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:99: vtkMRMLViewNode* currentViewNode = vtkMRMLViewNode::SafeDownCast(d->ViewNodeSelector->currentNode());`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:151: d->ViewNodeSelector->setCurrentNode(node);`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:163: d->ViewNodeSelector->setCurrentNode(viewNode);`
- Connected slots/functions: `onCurrentViewNodeChanged`
- API footprints: `vtkMRMLViewNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLViewNode"]}

## widget: CameraNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Camera: | CameraNodeLabel | QLabel
- Text: Camera:
- Implementation candidates: `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx`, `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.h`

## widget: CameraNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: CameraNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx`, `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:57: connect(d->CameraNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(setCameraToCurrentView(vtkMRMLNode*)));`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:58: connect(d->CameraNodeSelector, SIGNAL(nodeAdded(vtkMRMLNode*)), this, SLOT(onCameraNodeAdded(vtkMRMLNode*)));`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:59: connect(d->CameraNodeSelector, SIGNAL(nodeAboutToBeRemoved(vtkMRMLNode*)), this, SLOT(onCameraNodeRemoved(vtkMRMLNode*)));`
  - `Modules/Loadable/Cameras/qSlicerCamerasModuleWidget.cxx:87: d->CameraNodeSelector->setCurrentNode(found_camera_node);`
- Connected slots/functions: `onCameraNodeAdded`, `onCameraNodeRemoved`, `setCameraToCurrentView`
- API footprints: `GetLayoutName`, `GetViewActiveCameraNode`, `SetLayoutName`, `vtkMRMLCameraNode::LayoutNameModifiedEvent`, `vtkMRMLCameraNode::SafeDownCast`, `vtkMRMLViewNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLCameraNode"]}
