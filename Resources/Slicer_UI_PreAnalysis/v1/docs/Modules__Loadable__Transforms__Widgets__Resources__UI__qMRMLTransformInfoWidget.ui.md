# Slicer UI Analysis: Modules/Loadable/Transforms/Widgets/Resources/UI/qMRMLTransformInfoWidget.ui

- Owner class: `qMRMLTransformInfoWidget`
- UI file: `Modules/Loadable/Transforms/Widgets/Resources/UI/qMRMLTransformInfoWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLTransformInfoWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLTransformInfoWidget | QWidget
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:24: #include "qMRMLTransformInfoWidget.h"`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:25: #include "ui_qMRMLTransformInfoWidget.h"`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:38: class qMRMLTransformInfoWidgetPrivate : public Ui_qMRMLTransformInfoWidget`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:40: Q_DECLARE_PUBLIC(qMRMLTransformInfoWidget);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:43: qMRMLTransformInfoWidget* const q_ptr;`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:46: qMRMLTransformInfoWidgetPrivate(qMRMLTransformInfoWidget& object);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:57: qMRMLTransformInfoWidgetPrivate::qMRMLTransformInfoWidgetPrivate(qMRMLTransformInfoWidget& object)`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:66: void qMRMLTransformInfoWidgetPrivate::init()`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:68: Q_Q(qMRMLTransformInfoWidget);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:76: void qMRMLTransformInfoWidgetPrivate::setAndObserveCrosshairNode()`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:78: Q_Q(qMRMLTransformInfoWidget);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:92: qMRMLTransformInfoWidget::qMRMLTransformInfoWidget(QWidget* _parent)`
- API footprints: `GetPointer`, `vtkMRMLTransformNode::SafeDownCast`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Transform to parent: | label | QLabel
- Text: Transform to parent:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.h`

## widget: TransformToParentInfoTextBrowser

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: No information available. | TransformToParentInfoTextBrowser | QLabel
- Text: No information available.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:71: this->TransformToParentInfoTextBrowser->setTextInteractionFlags(Qt::TextSelectableByMouse);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:184: d->TransformToParentInfoTextBrowser->setText(d->TransformNode->GetTransformToParentInfo());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:189: d->TransformToParentInfoTextBrowser->clear();`
- API footprints: `GetPointer`, `GetTransformFromParentInfo`, `GetTransformToParentInfo`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Transform from parent: | label_2 | QLabel
- Text: Transform from parent:
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.h`

## widget: TransformFromParentInfoTextBrowser

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: No information available. | TransformFromParentInfoTextBrowser | QLabel
- Text: No information available.
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:72: this->TransformFromParentInfoTextBrowser->setTextInteractionFlags(Qt::TextSelectableByMouse);`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:185: d->TransformFromParentInfoTextBrowser->setText(d->TransformNode->GetTransformFromParentInfo());`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:190: d->TransformFromParentInfoTextBrowser->clear();`
- API footprints: `GetPointer`, `GetTransformFromParentInfo`, `GetTransformToParentInfo`

## widget: ViewerDisplacementVectorRAS

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: ViewerRAS | ViewerDisplacementVectorRAS | QLabel
- Text: ViewerRAS
- Implementation candidates: `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx`, `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:229: d->ViewerDisplacementVectorRAS->setText(QString("Displacement vector  RAS: (%1, %2, %3)%4")`
  - `Modules/Loadable/Transforms/Widgets/qMRMLTransformInfoWidget.cxx:240: d->ViewerDisplacementVectorRAS->clear();`
