# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qSlicerMultiVolumeRenderingPropertiesWidget.ui

- Owner class: `qSlicerMultiVolumeRenderingPropertiesWidget`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qSlicerMultiVolumeRenderingPropertiesWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerMultiVolumeRenderingPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qSlicerMultiVolumeRenderingPropertiesWidget | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:23: #include "qSlicerMultiVolumeRenderingPropertiesWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:25: #include "ui_qSlicerMultiVolumeRenderingPropertiesWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:32: class qSlicerMultiVolumeRenderingPropertiesWidgetPrivate : public Ui_qSlicerMultiVolumeRenderingPropertiesWidget`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:34: Q_DECLARE_PUBLIC(qSlicerMultiVolumeRenderingPropertiesWidget);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:37: qSlicerMultiVolumeRenderingPropertiesWidget* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:40: qSlicerMultiVolumeRenderingPropertiesWidgetPrivate(qSlicerMultiVolumeRenderingPropertiesWidget& object);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:41: virtual ~qSlicerMultiVolumeRenderingPropertiesWidgetPrivate();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:43: virtual void setupUi(qSlicerMultiVolumeRenderingPropertiesWidget*);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:48: qSlicerMultiVolumeRenderingPropertiesWidgetPrivate::qSlicerMultiVolumeRenderingPropertiesWidgetPrivate(qSlicerMultiVolumeRenderingPropertiesWidget& object)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:54: qSlicerMultiVolumeRenderingPropertiesWidgetPrivate::~qSlicerMultiVolumeRenderingPropertiesWidgetPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:57: void qSlicerMultiVolumeRenderingPropertiesWidgetPrivate::setupUi(qSlicerMultiVolumeRenderingPropertiesWidget* widget)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:59: this->Ui_qSlicerMultiVolumeRenderingPropertiesWidget::setupUi(widget);`
- API footprints: `vtkMRMLMultiVolumeRenderingDisplayNode::SafeDownCast`, `vtkMRMLViewNode::Composite`, `vtkMRMLViewNode::MaximumIntensityProjection`, `vtkMRMLViewNode::MinimumIntensityProjection`

## widget: RenderingTechniqueLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Technique: | RenderingTechniqueLabel | QLabel
- Text: Technique:
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.h`

## widget: RenderingTechniqueComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Select ray casting technique for the views where the current volume is visible | RenderingTechniqueComboBox | QComboBox
- Tooltip: Select ray casting technique for the views where the current volume is visible
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:44: void populateRenderingTechniqueComboBox();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:60: this->populateRenderingTechniqueComboBox();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:61: QObject::connect(this->RenderingTechniqueComboBox, SIGNAL(currentIndexChanged(int)), widget, SLOT(setRenderingTechnique(int)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:66: void qSlicerMultiVolumeRenderingPropertiesWidgetPrivate::populateRenderingTechniqueComboBox()`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:68: this->RenderingTechniqueComboBox->clear();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:69: this->RenderingTechniqueComboBox->addItem(qSlicerMultiVolumeRenderingPropertiesWidget::tr("Composite With Shading"), vtkMRMLViewNode::Composite);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:70: this->RenderingTechniqueComboBox->addItem(qSlicerMultiVolumeRenderingPropertiesWidget::tr("Maximum Intensity Projection"), vtkMRMLViewNode::MaximumIntensityProjection);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:71: this->RenderingTechniqueComboBox->addItem(qSlicerMultiVolumeRenderingPropertiesWidget::tr("Minimum Intensity Projection"), vtkMRMLViewNode::MinimumIntensityProjection);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:112: int index = d->RenderingTechniqueComboBox->findData(QVariant(technique));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:117: bool wasBlocked = d->RenderingTechniqueComboBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:118: d->RenderingTechniqueComboBox->setCurrentIndex(index);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:119: d->RenderingTechniqueComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setRenderingTechnique`
- API footprints: `GetID`, `GetNodesByClass`, `GetRaycastTechnique`, `GetScene`, `IsDisplayableInView`, `SetRaycastTechnique`, `vtkMRMLViewNode::Composite`, `vtkMRMLViewNode::MaximumIntensityProjection`, `vtkMRMLViewNode::MinimumIntensityProjection`, `vtkMRMLViewNode::SafeDownCast`

## widget: SurfaceSmoothingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Surface smoothing: | Option for removing wood-grain artifacts by applying random noise to raycasting | SurfaceSmoothingLabel | QLabel
- Text: Surface smoothing:
- Tooltip: Option for removing wood-grain artifacts by applying random noise to raycasting
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.h`

## widget: SurfaceSmoothingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Option for removing wood-grain artifacts by applying random noise to raycasting | SurfaceSmoothingCheckBox | QCheckBox
- Tooltip: Option for removing wood-grain artifacts by applying random noise to raycasting
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:62: QObject::connect(this->SurfaceSmoothingCheckBox, SIGNAL(toggled(bool)), widget, SLOT(setSurfaceSmoothing(bool)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:121: wasBlocked = d->SurfaceSmoothingCheckBox->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:122: d->SurfaceSmoothingCheckBox->setChecked(firstViewNode->GetVolumeRenderingSurfaceSmoothing());`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerMultiVolumeRenderingPropertiesWidget.cxx:123: d->SurfaceSmoothingCheckBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setSurfaceSmoothing`
- API footprints: `GetID`, `GetNodesByClass`, `GetScene`, `GetVolumeRenderingSurfaceSmoothing`, `IsDisplayableInView`, `SetVolumeRenderingSurfaceSmoothing`, `vtkMRMLViewNode::SafeDownCast`
