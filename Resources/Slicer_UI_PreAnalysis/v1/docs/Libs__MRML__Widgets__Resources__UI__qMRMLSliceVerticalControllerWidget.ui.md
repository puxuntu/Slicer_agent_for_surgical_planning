# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLSliceVerticalControllerWidget.ui

- Owner class: `qMRMLSliceVerticalControllerWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLSliceVerticalControllerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSliceVerticalControllerWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSliceVerticalControllerWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:22: #include "qMRMLSliceVerticalControllerWidget.h"`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:23: #include "ui_qMRMLSliceVerticalControllerWidget.h"`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:42: class qMRMLSliceVerticalControllerWidgetPrivate : public Ui_qMRMLSliceVerticalControllerWidget`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:44: Q_DECLARE_PUBLIC(qMRMLSliceVerticalControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:47: qMRMLSliceVerticalControllerWidgetPrivate(qMRMLSliceVerticalControllerWidget& object);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:48: ~qMRMLSliceVerticalControllerWidgetPrivate();`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:56: qMRMLSliceVerticalControllerWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:65: qMRMLSliceVerticalControllerWidgetPrivate::qMRMLSliceVerticalControllerWidgetPrivate(qMRMLSliceVerticalControllerWidget& object)`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:71: qMRMLSliceVerticalControllerWidgetPrivate::~qMRMLSliceVerticalControllerWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:74: void qMRMLSliceVerticalControllerWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:76: Q_Q(qMRMLSliceVerticalControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:80: this->SliceVerticalOffsetSlider->setToolTip(qMRMLSliceVerticalControllerWidget::tr("Slice distance from RAS origin"));`
- API footprints: `GetSliceNode`, `vtkMRMLSliceLogic::ModifiedEvent`

## widget: SliceVerticalOffsetSlider

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliderWidget`
- Search text: SliceVerticalOffsetSlider | qMRMLSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:79: this->SliceVerticalOffsetSlider->setTracking(false);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:80: this->SliceVerticalOffsetSlider->setToolTip(qMRMLSliceVerticalControllerWidget::tr("Slice distance from RAS origin"));`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:84: QObject::connect(this->SliceVerticalOffsetSlider, SIGNAL(valueChanged(double)), q, SLOT(setSliceOffsetValue(double)), Qt::QueuedConnection);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:85: QObject::connect(this->SliceVerticalOffsetSlider, SIGNAL(valueIsChanging(double)), q, SLOT(trackSliceOffsetValue(double)), Qt::QueuedConnection);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:123: bool wasBlocking = this->SliceVerticalOffsetSlider->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:126: this->SliceVerticalOffsetSlider->setValue(this->SliceLogic->GetSliceOffset());`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:127: this->SliceVerticalOffsetSlider->blockSignals(wasBlocking);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:137: this->SliceVerticalOffsetSlider->setVisible(this->ShowSliceOffsetSlider);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:224: d->SliceVerticalOffsetSlider->setRange(min, max);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:242: d->SliceVerticalOffsetSlider->setSingleStep(resolution * displayCoeffiecient);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:243: d->SliceVerticalOffsetSlider->setPageStep(resolution * displayCoeffiecient);`
  - `Libs/MRML/Widgets/qMRMLSliceVerticalControllerWidget.cxx:319: return d->SliceVerticalOffsetSlider;`
- Connected slots/functions: `setSliceOffsetValue`, `trackSliceOffsetValue`
- API footprints: `EndSliceOffsetInteraction`, `GetMRMLApplicationLogic`, `GetSliceOffset`, `PauseRender`, `ResumeRender`, `SetSliceOffset`, `StartSliceOffsetInteraction`, `vtkMRMLSliceViewDisplayableManagerFactory::GetInstance`
