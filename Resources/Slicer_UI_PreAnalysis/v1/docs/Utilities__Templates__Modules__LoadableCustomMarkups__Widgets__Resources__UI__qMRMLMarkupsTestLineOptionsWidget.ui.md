# Slicer UI Analysis: Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/Resources/UI/qMRMLMarkupsTestLineOptionsWidget.ui

- Owner class: `qMRMLMarkupsTestLineOptionsWidget`
- UI file: `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/Resources/UI/qMRMLMarkupsTestLineOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsTestLineOptionsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsTestLineOptionsWidget | QWidget

## widget: MarkupsTestLineWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLMarkupsTestLineWidget`
- Search text: MarkupsTestLineWidget | qMRMLMarkupsTestLineWidget
- Implementation candidates: `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx`, `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.h`
- Matched implementation lines:
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:21: #include "qMRMLMarkupsTestLineWidget.h"`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:22: #include "ui_qMRMLMarkupsTestLineWidget.h"`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:31: class qMRMLMarkupsTestLineWidgetPrivate : public Ui_qMRMLMarkupsTestLineWidget`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:33: Q_DECLARE_PUBLIC(qMRMLMarkupsTestLineWidget);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:36: qMRMLMarkupsTestLineWidget* const q_ptr;`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:39: qMRMLMarkupsTestLineWidgetPrivate(qMRMLMarkupsTestLineWidget* object);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:40: void setupUi(qMRMLMarkupsTestLineWidget*);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:46: qMRMLMarkupsTestLineWidgetPrivate::qMRMLMarkupsTestLineWidgetPrivate(qMRMLMarkupsTestLineWidget* object)`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:52: void qMRMLMarkupsTestLineWidgetPrivate::setupUi(qMRMLMarkupsTestLineWidget* widget)`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:54: Q_Q(qMRMLMarkupsTestLineWidget);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:56: this->Ui_qMRMLMarkupsTestLineWidget::setupUi(widget);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:61: qMRMLMarkupsTestLineWidget::qMRMLMarkupsTestLineWidget(QWidget* parent)`
- API footprints: `vtkMRMLMarkupsTestLineNode::SafeDownCast`
