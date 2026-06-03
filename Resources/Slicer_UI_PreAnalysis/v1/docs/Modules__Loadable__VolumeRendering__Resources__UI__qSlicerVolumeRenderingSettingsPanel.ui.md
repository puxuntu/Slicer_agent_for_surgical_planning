# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qSlicerVolumeRenderingSettingsPanel.ui

- Owner class: `qSlicerVolumeRenderingSettingsPanel`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qSlicerVolumeRenderingSettingsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerVolumeRenderingSettingsPanel

- Confidence: `linked_to_api`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerVolumeRenderingSettingsPanel | ctkSettingsPanel
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:27: #include "qSlicerVolumeRenderingSettingsPanel.h"`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:28: #include "ui_qSlicerVolumeRenderingSettingsPanel.h"`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:45: // qSlicerVolumeRenderingSettingsPanelPrivate`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:48: class qSlicerVolumeRenderingSettingsPanelPrivate : public Ui_qSlicerVolumeRenderingSettingsPanel`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:50: Q_DECLARE_PUBLIC(qSlicerVolumeRenderingSettingsPanel);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:53: qSlicerVolumeRenderingSettingsPanel* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:56: qSlicerVolumeRenderingSettingsPanelPrivate(qSlicerVolumeRenderingSettingsPanel& object);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:68: // qSlicerVolumeRenderingSettingsPanelPrivate methods`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:71: qSlicerVolumeRenderingSettingsPanelPrivate::qSlicerVolumeRenderingSettingsPanelPrivate(qSlicerVolumeRenderingSettingsPanel& object)`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:77: void qSlicerVolumeRenderingSettingsPanelPrivate::init()`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:79: Q_Q(qSlicerVolumeRenderingSettingsPanel);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:132: void qSlicerVolumeRenderingSettingsPanelPrivate::addRenderingMethod(const QString& methodName, const QString& methodClassName)`
- API footprints: `vtkMRMLViewNode::GetVolumeRenderingQualityAsString`

## widget: RenderingMethodLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default rendering method: | RenderingMethodLabel | QLabel
- Text: Default rendering method:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`

## widget: RenderingMethodComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Default rendering method | RenderingMethodComboBox | QComboBox
- Tooltip: Default rendering method
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:134: this->RenderingMethodComboBox->addItem(methodName, methodClassName);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:212: if (static_cast<int>(renderingMethods.size()) != d->RenderingMethodComboBox->count())`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:220: QObject::connect(d->RenderingMethodComboBox, SIGNAL(currentIndexChanged(int)), this, SLOT(onDefaultRenderingMethodChanged(int)), Qt::UniqueConnection);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:227: int defaultRenderingMethodIndex = d->RenderingMethodComboBox->findData(QString(defaultRenderingMethod));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:228: d->RenderingMethodComboBox->setCurrentIndex(defaultRenderingMethodIndex);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:280: QString renderingClassName = d->RenderingMethodComboBox->itemData(d->RenderingMethodComboBox->currentIndex()).toString();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:288: int methodIndex = d->RenderingMethodComboBox->findData(method);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:289: d->RenderingMethodComboBox->setCurrentIndex(methodIndex);`
- Connected slots/functions: `onDefaultRenderingMethodChanged`
- API footprints: `GetDefaultRenderingMethod`, `GetRenderingMethods`

## widget: QualityControlLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default quality: | QualityControlLabel | QLabel
- Text: Default quality:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`

## widget: GPUMemoryLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: GPU memory size: | GPUMemoryLabel | QLabel
- Text: GPU memory size:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:117: this->GPUMemoryLabel->hide();`

## widget: GPUMemoryComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerGPUMemoryComboBox`
- Search text: Amount of memory allocated for volume rendering on the graphic card | GPUMemoryComboBox | qSlicerGPUMemoryComboBox
- Tooltip: Amount of memory allocated for volume rendering on the graphic card
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:118: this->GPUMemoryComboBox->hide();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:120: QObject::connect(this->GPUMemoryComboBox, SIGNAL(editTextChanged(QString)), q, SLOT(onGPUMemoryChanged()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:121: QObject::connect(this->GPUMemoryComboBox, SIGNAL(currentTextChanged(QString)), q, SLOT(onGPUMemoryChanged()));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:235: return d->GPUMemoryComboBox->currentGPUMemoryAsString();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:242: d->GPUMemoryComboBox->setCurrentGPUMemoryFromString(gpuMemoryString);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:255: int memory = d->GPUMemoryComboBox->currentGPUMemoryInMB();`
- Connected slots/functions: `onGPUMemoryChanged`
- API footprints: `GetNodesByClass`, `SetGPUMemorySize`, `vtkMRMLViewNode::SafeDownCast`

## widget: QualityControlComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Quality control method to def | QualityControlComboBox | QComboBox
- Tooltip: Quality control method to def
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:88: this->QualityControlComboBox->addItem(vtkMRMLViewNode::GetVolumeRenderingQualityAsString(qualityIndex));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:90: this->QualityControlComboBox->setCurrentText(vtkMRMLViewNode::GetVolumeRenderingQualityAsString(vtkMRMLViewNode::Normal));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:91: QObject::connect(this->QualityControlComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onDefaultQualityChanged(int)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:315: int qualityIndex = d->QualityControlComboBox->currentIndex();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:324: int qualityIndex = d->QualityControlComboBox->findText(quality);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:325: d->QualityControlComboBox->setCurrentIndex(qualityIndex);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:491: this->onDefaultQualityChanged(d->QualityControlComboBox->currentIndex());`
- Connected slots/functions: `onDefaultQualityChanged`
- API footprints: `GetNodesByClass`, `SetVolumeRenderingQuality`, `vtkMRMLViewNode::GetVolumeRenderingQualityAsString`, `vtkMRMLViewNode::Normal`, `vtkMRMLViewNode::SafeDownCast`, `vtkMRMLViewNode::VolumeRenderingQuality_Last`

## widget: InteractiveSpeedLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default interactive speed: | InteractiveSpeedLabel | QLabel
- Text: Default interactive speed:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`

## widget: InteractiveSpeedSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: InteractiveSpeedSlider | ctkSliderWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:97: QObject::connect(this->InteractiveSpeedSlider, SIGNAL(valueChanged(double)), q, SLOT(onDefaultInteractiveSpeedChanged(double)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:361: int interactiveSpeed = d->InteractiveSpeedSlider->value();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:369: d->InteractiveSpeedSlider->setValue(interactiveSpeed);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:492: this->onDefaultInteractiveSpeedChanged(d->InteractiveSpeedSlider->value());`
- Connected slots/functions: `onDefaultInteractiveSpeedChanged`
- API footprints: `GetNodesByClass`, `SetExpectedFPS`, `vtkMRMLViewNode::SafeDownCast`

## widget: SurfaceSmoothingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default surface smoothing: | SurfaceSmoothingLabel | QLabel
- Text: Default surface smoothing:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`

## widget: SurfaceSmoothingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Reduce wood grain artifact to make surfaces appear smoother. | SurfaceSmoothingCheckBox | QCheckBox
- Tooltip: Reduce wood grain artifact to make surfaces appear smoother.
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:103: QObject::connect(this->SurfaceSmoothingCheckBox, SIGNAL(toggled(bool)), q, SLOT(onDefaultSurfaceSmoothingChanged(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:404: bool smoothing = d->SurfaceSmoothingCheckBox->isChecked();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:412: d->SurfaceSmoothingCheckBox->setChecked(surfaceSmoothing);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:493: this->onDefaultSurfaceSmoothingChanged(d->SurfaceSmoothingCheckBox->isChecked());`
- Connected slots/functions: `onDefaultSurfaceSmoothingChanged`
- API footprints: `GetNodesByClass`, `SetVolumeRenderingSurfaceSmoothing`, `vtkMRMLViewNode::SafeDownCast`

## widget: FramerateLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Auto-release resources: | FramerateLabel_2 | QLabel
- Text: Auto-release resources:
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`

## widget: AutoReleaseGraphicsResourcesCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Immediately unload volumes from graphics memory when not visible. Reduces memory usage but makes toggling volume visibility slower. | AutoReleaseGraphicsResourcesCheckBox | QCheckBox
- Tooltip: Immediately unload volumes from graphics memory when not visible. Reduces memory usage but makes toggling volume visibility slower.
- Implementation candidates: `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx`, `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:109: QObject::connect(this->AutoReleaseGraphicsResourcesCheckBox, SIGNAL(toggled(bool)), q, SLOT(onDefaultAutoReleaseGraphicsResourcesChanged(bool)));`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:447: bool autoRelease = d->AutoReleaseGraphicsResourcesCheckBox->isChecked();`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:455: d->AutoReleaseGraphicsResourcesCheckBox->setChecked(autoRelease);`
  - `Modules/Loadable/VolumeRendering/qSlicerVolumeRenderingSettingsPanel.cxx:494: this->onDefaultAutoReleaseGraphicsResourcesChanged(d->AutoReleaseGraphicsResourcesCheckBox->isChecked());`
- Connected slots/functions: `onDefaultAutoReleaseGraphicsResourcesChanged`
- API footprints: `GetNodesByClass`, `SetAutoReleaseGraphicsResources`, `vtkMRMLViewNode::SafeDownCast`
