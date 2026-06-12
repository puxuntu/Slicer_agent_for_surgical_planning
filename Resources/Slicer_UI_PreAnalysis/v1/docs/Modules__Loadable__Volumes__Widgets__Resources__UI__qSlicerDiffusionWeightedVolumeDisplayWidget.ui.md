# Slicer UI Analysis: Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerDiffusionWeightedVolumeDisplayWidget.ui

- Owner class: `qSlicerDiffusionWeightedVolumeDisplayWidget`
- UI file: `Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerDiffusionWeightedVolumeDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerDiffusionWeightedVolumeDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerDiffusionWeightedVolumeDisplayWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:21: #include "qSlicerDiffusionWeightedVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:22: #include "ui_qSlicerDiffusionWeightedVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:36: class qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate : public Ui_qSlicerDiffusionWeightedVolumeDisplayWidget`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:38: Q_DECLARE_PUBLIC(qSlicerDiffusionWeightedVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:41: qSlicerDiffusionWeightedVolumeDisplayWidget* const q_ptr;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:44: qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate(qSlicerDiffusionWeightedVolumeDisplayWidget& object);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:45: ~qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:51: qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate::qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate(qSlicerDiffusionWeightedVolumeDisplayWidget& object)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:57: qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate ::~qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate() = default;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:60: void qSlicerDiffusionWeightedVolumeDisplayWidgetPrivate::init()`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:62: Q_Q(qSlicerDiffusionWeightedVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:70: qSlicerDiffusionWeightedVolumeDisplayWidget::qSlicerDiffusionWeightedVolumeDisplayWidget(QWidget* parentWidget)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ScalarVolumeDisplayWidget.setMRMLScene(vtkMRMLScene*)`
- API footprints: `vtkMRMLDiffusionWeightedVolumeNode::SafeDownCast`

## widget: ScalarDisplayGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: ScalarDisplayGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.h`

## widget: DWIComponentLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: DWI Component: | DWIComponentLabel | QLabel
- Text: DWI Component:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.h`

## widget: ScalarVolumeDisplayWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerScalarVolumeDisplayWidget`
- Search text: ScalarVolumeDisplayWidget | qSlicerScalarVolumeDisplayWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:115: d->ScalarVolumeDisplayWidget->setMRMLVolumeNode(volumeNode);`

## widget: DWIComponentSlider

- Confidence: `linked_to_api`
- Widget/action class: `QSlider`
- Search text: DWIComponentSlider | QSlider
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:66: QObject::connect(this->DWIComponentSlider, SIGNAL(valueChanged(int)), q, SLOT(setDWIComponent(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:135: int component = displayNode ? displayNode->GetDiffusionComponent() : d->DWIComponentSlider->value();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:136: bool sliderWasBlocking = d->DWIComponentSlider->blockSignals(true);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:138: d->DWIComponentSlider->setRange(0, maxRange);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:140: d->DWIComponentSlider->blockSignals(sliderWasBlocking);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:142: d->DWIComponentSlider->setValue(component);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:154: d->DWIComponentSlider->setValue(displayNode->GetDiffusionComponent());`
- Connected slots/functions: `setDWIComponent`, `setValue`
- Declared UI connections: `valueChanged(int) -> DWIComponentSpinBox.setValue(int)`
- API footprints: `GetDiffusionComponent`, `SetDiffusionComponent`

## widget: DWIComponentSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: DWIComponentSpinBox | QSpinBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:137: bool spinBoxWasBlocking = d->DWIComponentSpinBox->blockSignals(true);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:139: d->DWIComponentSpinBox->setRange(0, maxRange);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionWeightedVolumeDisplayWidget.cxx:141: d->DWIComponentSpinBox->blockSignals(spinBoxWasBlocking);`
- Connected slots/functions: `setValue`
- Declared UI connections: `valueChanged(int) -> DWIComponentSlider.setValue(int)`
- API footprints: `GetDiffusionComponent`
