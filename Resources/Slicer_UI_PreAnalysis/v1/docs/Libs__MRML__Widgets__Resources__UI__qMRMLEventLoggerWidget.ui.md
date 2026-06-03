# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLEventLoggerWidget.ui

- Owner class: `qMRMLEventLoggerWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLEventLoggerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLEventLoggerWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLEventLoggerWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx`, `Libs/MRML/Widgets/qMRMLEventLoggerWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:24: #include "qMRMLEventLoggerWidget.h"`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:25: #include "ui_qMRMLEventLoggerWidget.h"`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:34: class qMRMLEventLoggerWidgetPrivate : public Ui_qMRMLEventLoggerWidget`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:50: qMRMLEventLoggerWidget::qMRMLEventLoggerWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:52: , d_ptr(new qMRMLEventLoggerWidgetPrivate)`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:54: Q_D(qMRMLEventLoggerWidget);`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:78: qMRMLEventLoggerWidget::~qMRMLEventLoggerWidget() = default;`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:81: void qMRMLEventLoggerWidget::setMRMLScene(vtkMRMLScene* scene)`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:83: Q_D(qMRMLEventLoggerWidget);`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:88: void qMRMLEventLoggerWidget::setConsoleOutputEnabled(bool enabled)`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:90: Q_D(qMRMLEventLoggerWidget);`
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:95: void qMRMLEventLoggerWidget::onNodeAddedEvent(vtkObject* caller, vtkObject* call_data)`
- API footprints: `vtkMRMLNode::SafeDownCast`

## widget: TextEdit

- Confidence: `linked_to_code`
- Widget/action class: `QTextEdit`
- Search text: TextEdit | QTextEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx`, `Libs/MRML/Widgets/qMRMLEventLoggerWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLEventLoggerWidget.cxx:152: this->TextEdit->append(text);`
