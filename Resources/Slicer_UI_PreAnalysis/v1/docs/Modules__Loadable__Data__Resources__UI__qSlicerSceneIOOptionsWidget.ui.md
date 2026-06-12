# Slicer UI Analysis: Modules/Loadable/Data/Resources/UI/qSlicerSceneIOOptionsWidget.ui

- Owner class: `qSlicerSceneIOOptionsWidget`
- UI file: `Modules/Loadable/Data/Resources/UI/qSlicerSceneIOOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSceneIOOptionsWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSceneIOOptionsWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx`, `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:30: #include "qSlicerSceneIOOptionsWidget.h"`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:31: #include "ui_qSlicerSceneIOOptionsWidget.h"`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:34: class qSlicerSceneIOOptionsWidgetPrivate`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:36: , public Ui_qSlicerSceneIOOptionsWidget`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:42: qSlicerSceneIOOptionsWidget::qSlicerSceneIOOptionsWidget(QWidget* parentWidget)`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:43: : qSlicerIOOptionsWidget(new qSlicerSceneIOOptionsWidgetPrivate, parentWidget)`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:45: Q_D(qSlicerSceneIOOptionsWidget);`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:56: qSlicerSceneIOOptionsWidget::~qSlicerSceneIOOptionsWidget() = default;`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:59: void qSlicerSceneIOOptionsWidget::updateProperties()`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:61: Q_D(qSlicerSceneIOOptionsWidget);`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:67: void qSlicerSceneIOOptionsWidget::updateGUI(const qSlicerIO::IOProperties& ioProperties)`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:69: Q_D(qSlicerSceneIOOptionsWidget);`

## widget: ClearSceneCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Clear existing scene | ClearSceneCheckBox | QCheckBox
- Text: Clear existing scene
- Implementation candidates: `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx`, `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:50: connect(d->ClearSceneCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:63: d->Properties["clear"] = d->ClearSceneCheckBox->isChecked();`
  - `Modules/Loadable/Data/qSlicerSceneIOOptionsWidget.cxx:73: d->ClearSceneCheckBox->setChecked(ioProperties["clear"].toBool());`
- Connected slots/functions: `updateProperties`
- Key UI properties: {"checked": "false"}
