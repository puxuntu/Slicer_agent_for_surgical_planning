# Slicer UI Analysis: Modules/Loadable/VolumeRendering/Resources/UI/qMRMLVolumePropertyNodeWidget.ui

- Owner class: `qMRMLVolumePropertyNodeWidget`
- UI file: `Modules/Loadable/VolumeRendering/Resources/UI/qMRMLVolumePropertyNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLVolumePropertyNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLVolumePropertyNodeWidget | QWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:24: #include "qMRMLVolumePropertyNodeWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:25: #include "ui_qMRMLVolumePropertyNodeWidget.h"`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:38: class qMRMLVolumePropertyNodeWidgetPrivate : public Ui_qMRMLVolumePropertyNodeWidget`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:40: Q_DECLARE_PUBLIC(qMRMLVolumePropertyNodeWidget);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:43: qMRMLVolumePropertyNodeWidget* const q_ptr;`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:46: qMRMLVolumePropertyNodeWidgetPrivate(qMRMLVolumePropertyNodeWidget& object);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:47: virtual ~qMRMLVolumePropertyNodeWidgetPrivate();`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:57: qMRMLVolumePropertyNodeWidgetPrivate::qMRMLVolumePropertyNodeWidgetPrivate(qMRMLVolumePropertyNodeWidget& object)`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:64: qMRMLVolumePropertyNodeWidgetPrivate::~qMRMLVolumePropertyNodeWidgetPrivate() = default;`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:67: void qMRMLVolumePropertyNodeWidgetPrivate::setupUi()`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:69: Q_Q(qMRMLVolumePropertyNodeWidget);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:70: this->Ui_qMRMLVolumePropertyNodeWidget::setupUi(q);`
- Connected slots/functions: `buttonToggled`, `updateIndependentComponents`
- API footprints: `GetIndependentComponents`, `GetVolumeProperty`, `SetIndependentComponents`, `vtkMRMLVolumePropertyNode::SafeDownCast`

## widget: IndependentComponentsLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Components: | IndependentComponentsLabel | QLabel
- Text: Components:
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:146: d->IndependentComponentsLabel->setVisible(independentComponentsVisible);`

## widget: RGBColorsRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: RGBA | RGBColorsRadioButton | QRadioButton
- Text: RGBA
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:77: this->ComponentsButtonGroup->addButton(this->RGBColorsRadioButton);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:139: d->RGBColorsRadioButton->setChecked(!independentComponents);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:143: d->RGBColorsRadioButton->setEnabled(d->ComponentCount == 3 || d->ComponentCount == 4);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:147: d->RGBColorsRadioButton->setVisible(independentComponentsVisible);`

## widget: VolumePropertyWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKVolumePropertyWidget`
- Search text: VolumePropertyWidget | ctkVTKVolumePropertyWidget
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:71: QObject::connect(this->VolumePropertyWidget, SIGNAL(chartsExtentChanged()), q, SIGNAL(chartsExtentChanged()));`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:72: QObject::connect(this->VolumePropertyWidget, SIGNAL(thresholdEnabledChanged(bool)), q, SIGNAL(thresholdChanged(bool)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:73: QObject::connect(this->ComponentSpinBox, SIGNAL(valueChanged(int)), this->VolumePropertyWidget, SLOT(setCurrentComponent(int)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:104: return d->VolumePropertyWidget->volumeProperty();`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:127: qvtkReconnect(d->VolumePropertyWidget->volumeProperty(), newVolumeProperty, vtkCommand::ModifiedEvent, this, SIGNAL(volumePropertyChanged()));`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:128: d->VolumePropertyWidget->setVolumeProperty(newVolumeProperty);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:136: d->VolumePropertyWidget->setCurrentComponent(currentComponent);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:160: d->VolumePropertyWidget->chartsBounds(bounds);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:167: d->VolumePropertyWidget->chartsExtent(extent);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:174: d->VolumePropertyWidget->setChartsExtent(min, max);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:181: d->VolumePropertyWidget->chartsExtent(extent);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:188: d->VolumePropertyWidget->setThresholdEnabled(enable);`
- Connected slots/functions: `setCurrentComponent`
- API footprints: `GetIndependentComponents`, `GetVolumeProperty`

## widget: IndependentRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Independent | IndependentRadioButton | QRadioButton
- Text: Independent
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:78: this->ComponentsButtonGroup->addButton(this->IndependentRadioButton);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:140: d->IndependentRadioButton->setChecked(independentComponents);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:148: d->IndependentRadioButton->setVisible(independentComponentsVisible);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:280: bool independentComponents = d->IndependentRadioButton->isChecked();`
- API footprints: `SetIndependentComponents`

## widget: ComponentSpinBox

- Confidence: `linked_to_slot`
- Widget/action class: `QSpinBox`
- Search text: ComponentSpinBox | QSpinBox
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:73: QObject::connect(this->ComponentSpinBox, SIGNAL(valueChanged(int)), this->VolumePropertyWidget, SLOT(setCurrentComponent(int)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:74: QObject::connect(this->ComponentSpinBox, SIGNAL(valueChanged(int)), q, SIGNAL(componentChanged(int)));`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:134: currentComponent = d->ComponentSpinBox->value();`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:151: d->ComponentSpinBox->setVisible(independentComponentsVisible);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:153: d->ComponentSpinBox->setEnabled(independentComponents);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:241: QSignalBlocker blocker(d->ComponentSpinBox);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:242: d->ComponentSpinBox->setValue(component);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:256: d->ComponentSpinBox->setRange(0, d->ComponentCount - 1);`
- Connected slots/functions: `setCurrentComponent`

## widget: ComponentLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Component Index: | ComponentLabel | QLabel
- Text: Component Index:
- Implementation candidates: `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx`, `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:150: d->ComponentLabel->setVisible(independentComponentsVisible);`
  - `Modules/Loadable/VolumeRendering/Widgets/qMRMLVolumePropertyNodeWidget.cxx:152: d->ComponentLabel->setEnabled(independentComponents);`
