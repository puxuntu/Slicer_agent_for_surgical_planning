# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLThreeDViewInformationWidget.ui

- Owner class: `qMRMLThreeDViewInformationWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLThreeDViewInformationWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLThreeDViewInformationWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLThreeDViewInformationWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:25: #include "qMRMLThreeDViewInformationWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:34: qMRMLThreeDViewInformationWidgetPrivate::qMRMLThreeDViewInformationWidgetPrivate(qMRMLThreeDViewInformationWidget& object)`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:41: qMRMLThreeDViewInformationWidgetPrivate::~qMRMLThreeDViewInformationWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:44: void qMRMLThreeDViewInformationWidgetPrivate::setupUi(qMRMLWidget* widget)`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:46: Q_Q(qMRMLThreeDViewInformationWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:48: this->Ui_qMRMLThreeDViewInformationWidget::setupUi(widget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:54: void qMRMLThreeDViewInformationWidgetPrivate::updateWidgetFromMRMLViewNode()`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:56: Q_Q(qMRMLThreeDViewInformationWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:72: qMRMLThreeDViewInformationWidget::qMRMLThreeDViewInformationWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:74: , d_ptr(new qMRMLThreeDViewInformationWidgetPrivate(*this))`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:76: Q_D(qMRMLThreeDViewInformationWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:82: qMRMLThreeDViewInformationWidget::~qMRMLThreeDViewInformationWidget() = default;`
- API footprints: `vtkMRMLViewNode::SafeDownCast`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Layout Name: | label_2 | QLabel
- Text: Layout Name:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget_p.h`

## widget: LayoutNameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Name of the slice | LayoutNameLineEdit | QLineEdit
- Tooltip: Name of the slice
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:64: this->LayoutNameLineEdit->setText(this->MRMLViewNode->GetLayoutName());`
- API footprints: `GetLayoutName`, `GetViewGroup`

## widget: label_11

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View group: | label_11 | QLabel
- Text: View group:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget_p.h`

## widget: ViewGroupSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: Navigation and linked properties are synchronized in views that has the same group index. | ViewGroupSpinBox | QSpinBox
- Tooltip: Navigation and linked properties are synchronized in views that has the same group index.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:50: this->connect(this->ViewGroupSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setViewGroup(int)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewInformationWidget.cxx:65: this->ViewGroupSpinBox->setValue(this->MRMLViewNode->GetViewGroup());`
- Connected slots/functions: `setViewGroup`
- API footprints: `GetLayoutName`, `GetViewGroup`, `SetViewGroup`
