# Slicer UI Analysis: Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/Resources/UI/qMRMLMarkupsTestLineWidget.ui

- Owner class: `qMRMLMarkupsTestLineWidget`
- UI file: `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/Resources/UI/qMRMLMarkupsTestLineWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsTestLineWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsTestLineWidget | QWidget
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

## widget: lineTestCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Test Line Settings | lineTestCollapsibleButton | ctkCollapsibleButton
- Text: Test Line Settings
- Implementation candidates: `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx`, `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.h`
- Matched implementation lines:
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:57: this->lineTestCollapsibleButton->setVisible(false);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:84: d->lineTestCollapsibleButton->setVisible(false);`
  - `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx:88: d->lineTestCollapsibleButton->setVisible(true);`
- Key UI properties: {"checked": "false"}

## widget: qMRMLMarkupsTestLineWidgetLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: This is a test label in a test widget! | qMRMLMarkupsTestLineWidgetLabel | QLabel
- Text: This is a test label in a test widget!
- Implementation candidates: `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.cxx`, `Utilities/Templates/Modules/LoadableCustomMarkups/Widgets/qMRMLMarkupsTestLineWidget.h`
