# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLSliceWidget.ui

- Owner class: `qMRMLSliceWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLSliceWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSliceWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSliceWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceWidget.h`, `Libs/MRML/Widgets/qMRMLSliceWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:28: #include "qMRMLSliceWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:48: // qMRMLSliceWidgetPrivate methods`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:51: qMRMLSliceWidgetPrivate::qMRMLSliceWidgetPrivate(qMRMLSliceWidget& object)`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:57: qMRMLSliceWidgetPrivate::~qMRMLSliceWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:60: void qMRMLSliceWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:62: Q_Q(qMRMLSliceWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:80: void qMRMLSliceWidgetPrivate::updateSliceOffsetSliderOrientation()`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:88: void qMRMLSliceWidgetPrivate::setSliceViewSize(const QSize& size)`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:95: void qMRMLSliceWidgetPrivate::resetSliceViewSize()`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:101: void qMRMLSliceWidgetPrivate::endProcessing()`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:109: void qMRMLSliceWidgetPrivate::setImageDataConnection(vtkAlgorithmOutput* imageDataConnection)`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:111: // qDebug() << "qMRMLSliceWidgetPrivate::setImageDataConnection";`
- API footprints: `vtkMRMLSliceNode::SafeDownCast`

## widget: SliceController

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSliceControllerWidget`
- Search text: SliceController | qMRMLSliceControllerWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceWidget.h`, `Libs/MRML/Widgets/qMRMLSliceWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:65: vtkMRMLSliceLogic* sliceLogic = this->SliceController->sliceLogic();`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:72: connect(this->SliceController, SIGNAL(imageDataConnectionChanged(vtkAlgorithmOutput*)), this, SLOT(setImageDataConnection(vtkAlgorithmOutput*)));`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:73: connect(this->SliceController, SIGNAL(renderRequested()), this->SliceView, SLOT(scheduleRender()), Qt::QueuedConnection);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:83: this->SliceController->setShowSliceOffsetSlider(horizontal);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:91: this->SliceController->setSliceViewSize(scaledSizeF.toSize());`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:145: // In SliceController and  SliceVerticalController widgets`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:155: d->SliceController->setMRMLSliceNode(newSliceNode);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:176: return d->SliceController->mrmlSliceCompositeNode();`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:183: d->SliceController->setSliceViewName(newSliceViewName);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:190: return d->SliceController->sliceViewName();`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:225: d->SliceController->setSliceOrientation(orientation);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:232: return d->SliceController->sliceOrientation();`
- Connected slots/functions: `scheduleRender`, `setImageDataConnection`

## widget: frame

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame | QFrame
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceWidget.h`, `Libs/MRML/Widgets/qMRMLSliceWidget_p.h`

## widget: SliceView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliceView`
- Search text: SliceView | qMRMLSliceView
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceWidget.h`, `Libs/MRML/Widgets/qMRMLSliceWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:29: #include "qMRMLSliceView.h"`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:32: #include <vtkMRMLSliceViewInteractorStyle.h>`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:68: this->SliceView->interactorObserver()->SetSliceLogic(sliceLogic);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:70: connect(this->SliceView, SIGNAL(resized(QSize)), this, SLOT(setSliceViewSize(QSize)));`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:73: connect(this->SliceController, SIGNAL(renderRequested()), this->SliceView, SLOT(scheduleRender()), Qt::QueuedConnection);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:74: connect(this->SliceVerticalController, SIGNAL(renderRequested()), this->SliceView, SLOT(scheduleRender()), Qt::QueuedConnection);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:88: void qMRMLSliceWidgetPrivate::setSliceViewSize(const QSize& size)`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:90: QSizeF scaledSizeF = QSizeF(size) * this->SliceView->devicePixelRatioF();`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:91: this->SliceController->setSliceViewSize(scaledSizeF.toSize());`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:95: void qMRMLSliceWidgetPrivate::resetSliceViewSize()`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:97: this->setSliceViewSize(this->SliceView->size());`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:105: this->setSliceViewSize(this->SliceView->size());`
- Connected slots/functions: `resetSliceViewSize`, `scheduleRender`, `setSliceViewSize`
- API footprints: `SetSliceLogic`

## widget: SliceVerticalController

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSliceVerticalControllerWidget`
- Search text: SliceVerticalController | qMRMLSliceVerticalControllerWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceWidget.h`, `Libs/MRML/Widgets/qMRMLSliceWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:67: this->SliceVerticalController->setSliceLogic(sliceLogic);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:74: connect(this->SliceVerticalController, SIGNAL(renderRequested()), this->SliceView, SLOT(scheduleRender()), Qt::QueuedConnection);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:84: this->SliceVerticalController->setShowSliceOffsetSlider(!horizontal);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:145: // In SliceController and  SliceVerticalController widgets`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:156: d->SliceVerticalController->setMRMLSliceNode(newSliceNode);`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:340: qMRMLSliceVerticalControllerWidget* qMRMLSliceWidget::sliceVerticalController() const`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.cxx:343: return d->SliceVerticalController;`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.h:38: class qMRMLSliceVerticalControllerWidget;`
  - `Libs/MRML/Widgets/qMRMLSliceWidget.h:71: Q_INVOKABLE qMRMLSliceVerticalControllerWidget* sliceVerticalController() const;`
- Connected slots/functions: `scheduleRender`
- API footprints: `SetSliceLogic`
