# Slicer UI Analysis: Utilities/Templates/Modules/Loadable/Resources/UI/qSlicerTemplateKeyModuleWidget.ui

- Owner class: `qSlicerTemplateKeyModuleWidget`
- UI file: `Utilities/Templates/Modules/Loadable/Resources/UI/qSlicerTemplateKeyModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTemplateKeyModuleWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerTemplateKeyModuleWidget | qSlicerWidget
- Implementation candidates: `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx`, `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.h`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:22: #include "qSlicerTemplateKeyModuleWidget.h"`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:23: #include "ui_qSlicerTemplateKeyModuleWidget.h"`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:26: class qSlicerTemplateKeyModuleWidgetPrivate : public Ui_qSlicerTemplateKeyModuleWidget`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:29: qSlicerTemplateKeyModuleWidgetPrivate();`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:33: // qSlicerTemplateKeyModuleWidgetPrivate methods`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:36: qSlicerTemplateKeyModuleWidgetPrivate::qSlicerTemplateKeyModuleWidgetPrivate() {}`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:39: // qSlicerTemplateKeyModuleWidget methods`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:42: qSlicerTemplateKeyModuleWidget::qSlicerTemplateKeyModuleWidget(QWidget* _parent)`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:44: , d_ptr(new qSlicerTemplateKeyModuleWidgetPrivate)`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:49: qSlicerTemplateKeyModuleWidget::~qSlicerTemplateKeyModuleWidget() {}`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:52: void qSlicerTemplateKeyModuleWidget::setup()`
  - `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx:54: Q_D(qSlicerTemplateKeyModuleWidget);`

## widget: CTKCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Display | CTKCollapsibleButton | ctkCollapsibleButton
- Text: Display
- Implementation candidates: `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx`, `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.h`

## widget: FooBar

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerTemplateKeyFooBarWidget`
- Search text: FooBar | qSlicerTemplateKeyFooBarWidget
- Implementation candidates: `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.cxx`, `Utilities/Templates/Modules/Loadable/qSlicerTemplateKeyModuleWidget.h`, `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx`, `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.h`
- Matched implementation lines:
  - `Utilities/Templates/Modules/Loadable/Widgets/qSlicerTemplateKeyFooBarWidget.cxx:21: // FooBar Widgets includes`
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
