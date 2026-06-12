# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qSlicerVolumeRenderingPresetComboBox.ui

- Owner class: `qSlicerVolumeRenderingPresetComboBox`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qSlicerVolumeRenderingPresetComboBox.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerVolumeRenderingPresetComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerVolumeRenderingPresetComboBox | qSlicerWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:22: #include "qSlicerVolumeRenderingPresetComboBox.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:23: #include "ui_qSlicerVolumeRenderingPresetComboBox.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:46: class qSlicerVolumeRenderingPresetComboBoxPrivate : public Ui_qSlicerVolumeRenderingPresetComboBox`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:48: Q_DECLARE_PUBLIC(qSlicerVolumeRenderingPresetComboBox);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:51: qSlicerVolumeRenderingPresetComboBox* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:54: qSlicerVolumeRenderingPresetComboBoxPrivate(qSlicerVolumeRenderingPresetComboBox& object);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:55: virtual ~qSlicerVolumeRenderingPresetComboBoxPrivate();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:68: // qSlicerVolumeRenderingPresetComboBoxPrivate methods`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:71: qSlicerVolumeRenderingPresetComboBoxPrivate::qSlicerVolumeRenderingPresetComboBoxPrivate(qSlicerVolumeRenderingPresetComboBox& object)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:79: qSlicerVolumeRenderingPresetComboBoxPrivate::~qSlicerVolumeRenderingPresetComboBoxPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:82: void qSlicerVolumeRenderingPresetComboBoxPrivate::init()`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:84: Q_Q(qSlicerVolumeRenderingPresetComboBox);`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> PresetComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `vtkMRMLVolumePropertyNode::SafeDownCast`

## widget: PresetsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Preset: | PresetsLabel | QLabel
- Text: Preset:
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.h`

## widget: PresetComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerPresetComboBox`
- Search text: PresetComboBox | qSlicerPresetComboBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:22: #include "qSlicerVolumeRenderingPresetComboBox.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:23: #include "ui_qSlicerVolumeRenderingPresetComboBox.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:24: #include "qSlicerPresetComboBox.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:46: class qSlicerVolumeRenderingPresetComboBoxPrivate : public Ui_qSlicerVolumeRenderingPresetComboBox`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:48: Q_DECLARE_PUBLIC(qSlicerVolumeRenderingPresetComboBox);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:51: qSlicerVolumeRenderingPresetComboBox* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:54: qSlicerVolumeRenderingPresetComboBoxPrivate(qSlicerVolumeRenderingPresetComboBox& object);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:55: virtual ~qSlicerVolumeRenderingPresetComboBoxPrivate();`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:68: // qSlicerVolumeRenderingPresetComboBoxPrivate methods`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:71: qSlicerVolumeRenderingPresetComboBoxPrivate::qSlicerVolumeRenderingPresetComboBoxPrivate(qSlicerVolumeRenderingPresetComboBox& object)`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:79: qSlicerVolumeRenderingPresetComboBoxPrivate::~qSlicerVolumeRenderingPresetComboBoxPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:82: void qSlicerVolumeRenderingPresetComboBoxPrivate::init()`
- Connected slots/functions: `applyPreset`
- API footprints: `CopyContent`, `GetName`, `GetRGBTransferFunction`, `GetRange`, `GetVolumeProperty`, `SetName`, `vtkMRMLVolumePropertyNode::SafeDownCast`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Shift: | Shift transfer functions | label | QLabel
- Text: Shift:
- Tooltip: Shift transfer functions
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.h`, `Modules/Loadable/VolumeRendering/Logic/vtkSlicerVolumeRenderingLogic.h`, `Modules/Loadable/VolumeRendering/Testing/Cxx/qSlicerPresetComboBoxTest.cxx`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Logic/vtkSlicerVolumeRenderingLogic.h:159: /// the labelmap display node to the volume rendering displaynode.`
  - `Modules/Loadable/VolumeRendering/Logic/vtkSlicerVolumeRenderingLogic.h:160: /// If labelMapDisplayNode is 0, it uses the first displaynode.`
  - `Modules/Loadable/VolumeRendering/Logic/vtkSlicerVolumeRenderingLogic.h:164: vtkMRMLLabelMapVolumeDisplayNode* labelMapDisplayNode = nullptr);`
  - `Modules/Loadable/VolumeRendering/Logic/vtkSlicerVolumeRenderingLogic.h:213: /// transfer function from the labelmap LUT \a colors.`
  - `Modules/Loadable/VolumeRendering/Testing/Cxx/qSlicerPresetComboBoxTest.cxx:115: QLabel label;`
  - `Modules/Loadable/VolumeRendering/Testing/Cxx/qSlicerPresetComboBoxTest.cxx:119: label.setText(QString("<img src=\"%1\"/>").arg(ctk::base64HTMLImageTagSrc(image)));`
  - `Modules/Loadable/VolumeRendering/Testing/Cxx/qSlicerPresetComboBoxTest.cxx:120: // label.setPixmap(pixmap); ok !`
  - `Modules/Loadable/VolumeRendering/Testing/Cxx/qSlicerPresetComboBoxTest.cxx:121: label.show();`
- API footprints: `GetPointer`

## widget: PresetOffsetSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSlider`
- Search text: Shift transfer functions | PresetOffsetSlider | ctkDoubleSlider
- Tooltip: Shift transfer functions
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:92: QObject::connect(this->PresetOffsetSlider, SIGNAL(valueChanged(double)), q, SLOT(offsetPreset(double)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:93: QObject::connect(this->PresetOffsetSlider, SIGNAL(sliderPressed()), q, SLOT(startInteraction()));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:94: QObject::connect(this->PresetOffsetSlider, SIGNAL(valueChanged(double)), q, SLOT(interaction()));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:95: QObject::connect(this->PresetOffsetSlider, SIGNAL(sliderReleased()), q, SLOT(endInteraction()));`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:246: d->PresetOffsetSlider->setValue(0.0);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:264: if (d->PresetOffsetSlider->slider()->isSliderDown())`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:282: bool wasBlocking = d->PresetOffsetSlider->blockSignals(true);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:283: d->PresetOffsetSlider->setRange(-transferFunctionWidth, transferFunctionWidth);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:284: d->PresetOffsetSlider->setSingleStep(ctk::closestPowerOfTen(transferFunctionWidth) / 500.0);`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:285: d->PresetOffsetSlider->setPageStep(d->PresetOffsetSlider->singleStep());`
  - `Modules/Loadable/VolumeRendering/Widgets/qSlicerVolumeRenderingPresetComboBox.cxx:286: d->PresetOffsetSlider->blockSignals(wasBlocking);`
- Connected slots/functions: `endInteraction`, `interaction`, `offsetPreset`, `startInteraction`
- API footprints: `GetVolumeProperty`, `InvokeEvent`
