# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qSlicerCPURayCastVolumeRenderingPropertiesWidget.ui

- Owner class: `qSlicerCPURayCastVolumeRenderingPropertiesWidget`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qSlicerCPURayCastVolumeRenderingPropertiesWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerCPURayCastVolumeRenderingPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qSlicerCPURayCastVolumeRenderingPropertiesWidget | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:22: #include "qSlicerCPURayCastVolumeRenderingPropertiesWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:24: #include "ui_qSlicerCPURayCastVolumeRenderingPropertiesWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:31: class qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate : public Ui_qSlicerCPURayCastVolumeRenderingPropertiesWidget`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:33: Q_DECLARE_PUBLIC(qSlicerCPURayCastVolumeRenderingPropertiesWidget);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:36: qSlicerCPURayCastVolumeRenderingPropertiesWidget* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:39: qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate(qSlicerCPURayCastVolumeRenderingPropertiesWidget& object);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:40: virtual ~qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:42: virtual void setupUi(qSlicerCPURayCastVolumeRenderingPropertiesWidget*);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:47: qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate::qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate(qSlicerCPURayCastVolumeRenderingPropertiesWidget& object)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:53: qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate::~qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:56: void qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate::setupUi(qSlicerCPURayCastVolumeRenderingPropertiesWidget* widget)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:58: this->Ui_qSlicerCPURayCastVolumeRenderingPropertiesWidget::setupUi(widget);`
- API footprints: `vtkMRMLCPURayCastVolumeRenderingDisplayNode::SafeDownCast`, `vtkMRMLViewNode::Composite`, `vtkMRMLViewNode::MaximumIntensityProjection`, `vtkMRMLViewNode::MinimumIntensityProjection`

## widget: RenderingTechniqueLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Technique: | RenderingTechniqueLabel | QLabel
- Text: Technique:
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.h`

## widget: RenderingTechniqueComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Select ray casting technique for the views where the current volume is visible | RenderingTechniqueComboBox | QComboBox
- Tooltip: Select ray casting technique for the views where the current volume is visible
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:43: void populateRenderingTechniqueComboBox();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:59: this->populateRenderingTechniqueComboBox();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:60: QObject::connect(this->RenderingTechniqueComboBox, SIGNAL(currentIndexChanged(int)), widget, SLOT(setRenderingTechnique(int)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:64: void qSlicerCPURayCastVolumeRenderingPropertiesWidgetPrivate::populateRenderingTechniqueComboBox()`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:66: this->RenderingTechniqueComboBox->clear();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:67: this->RenderingTechniqueComboBox->addItem(qSlicerCPURayCastVolumeRenderingPropertiesWidget::tr("Composite With Shading"), vtkMRMLViewNode::Composite);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:68: this->RenderingTechniqueComboBox->addItem(qSlicerCPURayCastVolumeRenderingPropertiesWidget::tr("Maximum Intensity Projection"), vtkMRMLViewNode::MaximumIntensityProjection);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:69: this->RenderingTechniqueComboBox->addItem(qSlicerCPURayCastVolumeRenderingPropertiesWidget::tr("Minimum Intensity Projection"), vtkMRMLViewNode::MinimumIntensityProjection);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:108: int index = d->RenderingTechniqueComboBox->findData(QVariant(technique));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:113: d->RenderingTechniqueComboBox->setCurrentIndex(index);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerCPURayCastVolumeRenderingPropertiesWidget.cxx:125: int technique = d->RenderingTechniqueComboBox->itemData(index).toInt();`
- Connected slots/functions: `setRenderingTechnique`
- API footprints: `GetID`, `GetNodesByClass`, `GetRaycastTechnique`, `GetScene`, `IsDisplayableInView`, `SetRaycastTechnique`, `vtkMRMLViewNode::Composite`, `vtkMRMLViewNode::MaximumIntensityProjection`, `vtkMRMLViewNode::MinimumIntensityProjection`, `vtkMRMLViewNode::SafeDownCast`
