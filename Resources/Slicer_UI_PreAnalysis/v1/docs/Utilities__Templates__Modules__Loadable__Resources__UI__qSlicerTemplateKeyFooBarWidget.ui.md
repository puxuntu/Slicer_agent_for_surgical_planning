# Slicer UI Analysis: Utilities/Templates/Modules/Loadable/Resources/UI/qSlicerTemplateKeyFooBarWidget.ui

- Owner class: `qSlicerTemplateKeyFooBarWidget`
- UI file: `Utilities/Templates/Modules/Loadable/Resources/UI/qSlicerTemplateKeyFooBarWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTemplateKeyFooBarWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qSlicerTemplateKeyFooBarWidget | QWidget
- Implementation candidates: `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx`, `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.h`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:22: #include "qSlicerTemplateKeyFooBarWidget.h"`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:23: #include "ui_qSlicerTemplateKeyFooBarWidget.h"`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:26: class qSlicerTemplateKeyFooBarWidgetPrivate : public Ui_qSlicerTemplateKeyFooBarWidget`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:28: Q_DECLARE_PUBLIC(qSlicerTemplateKeyFooBarWidget);`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:31: qSlicerTemplateKeyFooBarWidget* const q_ptr;`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:34: qSlicerTemplateKeyFooBarWidgetPrivate(qSlicerTemplateKeyFooBarWidget& object);`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:35: virtual void setupUi(qSlicerTemplateKeyFooBarWidget*);`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:39: qSlicerTemplateKeyFooBarWidgetPrivate::qSlicerTemplateKeyFooBarWidgetPrivate(qSlicerTemplateKeyFooBarWidget& object)`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:45: void qSlicerTemplateKeyFooBarWidgetPrivate::setupUi(qSlicerTemplateKeyFooBarWidget* widget)`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:47: this->Ui_qSlicerTemplateKeyFooBarWidget::setupUi(widget);`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:51: // qSlicerTemplateKeyFooBarWidget methods`
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:54: qSlicerTemplateKeyFooBarWidget::qSlicerTemplateKeyFooBarWidget(QWidget* parentWidget)`

## widget: FooBarButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Foo Bar | FooBarButton | QPushButton
- Text: Foo Bar
- Implementation candidates: `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx`, `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.h`
