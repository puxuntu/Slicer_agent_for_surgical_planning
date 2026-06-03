# Slicer UI Analysis: Modules/Core/Resources/UI/qSlicerEventBrokerModuleWidget.ui

- Owner class: `qSlicerEventBrokerModuleWidget`
- UI file: `Modules/Core/Resources/UI/qSlicerEventBrokerModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerEventBrokerModuleWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerEventBrokerModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx`, `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.h`
- Matched implementation lines:
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:24: #include "qSlicerEventBrokerModuleWidget.h"`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:25: #include "ui_qSlicerEventBrokerModuleWidget.h"`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:31: class qSlicerEventBrokerModuleWidgetPrivate : public Ui_qSlicerEventBrokerModuleWidget`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:38: void qSlicerEventBrokerModuleWidgetPrivate::setupUi(qSlicerWidget* widget)`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:40: this->Ui_qSlicerEventBrokerModuleWidget::setupUi(widget);`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:45: qSlicerEventBrokerModuleWidget::qSlicerEventBrokerModuleWidget(QWidget* _parent)`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:47: , d_ptr(new qSlicerEventBrokerModuleWidgetPrivate)`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:52: qSlicerEventBrokerModuleWidget::~qSlicerEventBrokerModuleWidget() = default;`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:55: void qSlicerEventBrokerModuleWidget::setup()`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:57: Q_D(qSlicerEventBrokerModuleWidget);`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:63: void qSlicerEventBrokerModuleWidget::onCurrentObjectChanged(vtkObject* object)`
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:65: Q_D(qSlicerEventBrokerModuleWidget);`

## widget: RefreshPushButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Refresh | RefreshPushButton | QPushButton
- Text: Refresh
- Implementation candidates: `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx`, `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.h`

## widget: EventBrokerWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLEventBrokerWidget`
- Search text: EventBrokerWidget | qMRMLEventBrokerWidget
- Implementation candidates: `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx`, `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.h`
- Matched implementation lines:
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:41: QObject::connect(this->EventBrokerWidget, SIGNAL(currentObjectChanged(vtkObject*)), widget, SLOT(onCurrentObjectChanged(vtkObject*)));`
- Connected slots/functions: `onCurrentObjectChanged`
- API footprints: `Print`

## widget: ResetElapsedTimesPushButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Reset Times | ResetElapsedTimesPushButton | QPushButton
- Text: Reset Times
- Implementation candidates: `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx`, `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.h`

## widget: ShowElapsedTimesPushButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Show observations with Elapsed Times > 0 | ShowElapsedTimesPushButton | QPushButton
- Text: Show observations with Elapsed Times > 0
- Implementation candidates: `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx`, `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.h`

## widget: TextEdit

- Confidence: `linked_to_api`
- Widget/action class: `QTextEdit`
- Search text: TextEdit | QTextEdit
- Implementation candidates: `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx`, `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.h`
- Matched implementation lines:
  - `Modules/Core/EventBroker/qSlicerEventBrokerModuleWidget.cxx:72: d->TextEdit->setText(QString::fromStdString(dumpStream.str()));`
- API footprints: `Print`
