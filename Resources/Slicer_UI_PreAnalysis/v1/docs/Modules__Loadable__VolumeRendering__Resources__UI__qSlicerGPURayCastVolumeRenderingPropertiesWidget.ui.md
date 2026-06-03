# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qSlicerGPURayCastVolumeRenderingPropertiesWidget.ui

- Owner class: `qSlicerGPURayCastVolumeRenderingPropertiesWidget`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qSlicerGPURayCastVolumeRenderingPropertiesWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerGPURayCastVolumeRenderingPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qSlicerGPURayCastVolumeRenderingPropertiesWidget | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:22: #include "qSlicerGPURayCastVolumeRenderingPropertiesWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:24: #include "ui_qSlicerGPURayCastVolumeRenderingPropertiesWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:31: class qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate : public Ui_qSlicerGPURayCastVolumeRenderingPropertiesWidget`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:33: Q_DECLARE_PUBLIC(qSlicerGPURayCastVolumeRenderingPropertiesWidget);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:36: qSlicerGPURayCastVolumeRenderingPropertiesWidget* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:39: qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate(qSlicerGPURayCastVolumeRenderingPropertiesWidget& object);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:40: virtual ~qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:42: virtual void setupUi(qSlicerGPURayCastVolumeRenderingPropertiesWidget*);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:47: qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate::qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate(qSlicerGPURayCastVolumeRenderingPropertiesWidget& object)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:53: qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate::~qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:56: void qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate::setupUi(qSlicerGPURayCastVolumeRenderingPropertiesWidget* widget)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:58: this->Ui_qSlicerGPURayCastVolumeRenderingPropertiesWidget::setupUi(widget);`
- API footprints: `vtkMRMLGPURayCastVolumeRenderingDisplayNode::SafeDownCast`, `vtkMRMLViewNode::Composite`, `vtkMRMLViewNode::MaximumIntensityProjection`, `vtkMRMLViewNode::MinimumIntensityProjection`

## widget: RenderingTechniqueLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Technique: | RenderingTechniqueLabel | QLabel
- Text: Technique:
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.h`

## widget: RenderingTechniqueComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Select ray casting technique for the views where the current volume is visible | RenderingTechniqueComboBox | QComboBox
- Tooltip: Select ray casting technique for the views where the current volume is visible
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:43: void populateRenderingTechniqueComboBox();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:59: this->populateRenderingTechniqueComboBox();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:60: QObject::connect(this->RenderingTechniqueComboBox, SIGNAL(currentIndexChanged(int)), widget, SLOT(setRenderingTechnique(int)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:65: void qSlicerGPURayCastVolumeRenderingPropertiesWidgetPrivate::populateRenderingTechniqueComboBox()`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:67: this->RenderingTechniqueComboBox->clear();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:68: this->RenderingTechniqueComboBox->addItem(qSlicerGPURayCastVolumeRenderingPropertiesWidget::tr("Composite With Shading"), vtkMRMLViewNode::Composite);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:69: this->RenderingTechniqueComboBox->addItem(qSlicerGPURayCastVolumeRenderingPropertiesWidget::tr("Maximum Intensity Projection"), vtkMRMLViewNode::MaximumIntensityProjection);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:70: this->RenderingTechniqueComboBox->addItem(qSlicerGPURayCastVolumeRenderingPropertiesWidget::tr("Minimum Intensity Projection"), vtkMRMLViewNode::MinimumIntensityProjection);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:111: int index = d->RenderingTechniqueComboBox->findData(QVariant(technique));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:116: bool wasBlocked = d->RenderingTechniqueComboBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:117: d->RenderingTechniqueComboBox->setCurrentIndex(index);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:118: d->RenderingTechniqueComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setRenderingTechnique`
- API footprints: `GetID`, `GetNodesByClass`, `GetRaycastTechnique`, `GetScene`, `IsDisplayableInView`, `SetRaycastTechnique`, `vtkMRMLViewNode::Composite`, `vtkMRMLViewNode::MaximumIntensityProjection`, `vtkMRMLViewNode::MinimumIntensityProjection`, `vtkMRMLViewNode::SafeDownCast`

## widget: SurfaceSmoothingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Surface smoothing: | Option for removing wood-grain artifacts by applying random noise to raycasting | SurfaceSmoothingLabel | QLabel
- Text: Surface smoothing:
- Tooltip: Option for removing wood-grain artifacts by applying random noise to raycasting
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.h`

## widget: SurfaceSmoothingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Option for removing wood-grain artifacts by applying random noise to raycasting | SurfaceSmoothingCheckBox | QCheckBox
- Tooltip: Option for removing wood-grain artifacts by applying random noise to raycasting
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:61: QObject::connect(this->SurfaceSmoothingCheckBox, SIGNAL(toggled(bool)), widget, SLOT(setSurfaceSmoothing(bool)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:120: wasBlocked = d->SurfaceSmoothingCheckBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:121: d->SurfaceSmoothingCheckBox->setChecked(firstViewNode->GetVolumeRenderingSurfaceSmoothing());`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerGPURayCastVolumeRenderingPropertiesWidget.cxx:122: d->SurfaceSmoothingCheckBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setSurfaceSmoothing`
- API footprints: `GetID`, `GetNodesByClass`, `GetScene`, `GetVolumeRenderingSurfaceSmoothing`, `IsDisplayableInView`, `SetVolumeRenderingSurfaceSmoothing`, `vtkMRMLViewNode::SafeDownCast`
