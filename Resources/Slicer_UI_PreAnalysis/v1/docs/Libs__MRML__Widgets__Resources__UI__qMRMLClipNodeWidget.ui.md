# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLClipNodeWidget.ui

- Owner class: `qMRMLClipNodeWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLClipNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLClipNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLClipNodeWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:25: #include "qMRMLClipNodeWidget.h"`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:27: #include "ui_qMRMLClipNodeWidget.h"`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:37: class qMRMLClipNodeWidgetPrivate : public Ui_qMRMLClipNodeWidget`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:39: Q_DECLARE_PUBLIC(qMRMLClipNodeWidget);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:42: qMRMLClipNodeWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:45: qMRMLClipNodeWidgetPrivate(qMRMLClipNodeWidget& object);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:53: qMRMLClipNodeWidgetPrivate::qMRMLClipNodeWidgetPrivate(qMRMLClipNodeWidget& object)`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:60: void qMRMLClipNodeWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:62: Q_Q(qMRMLClipNodeWidget);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:76: qMRMLClipNodeWidget::qMRMLClipNodeWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:78: , d_ptr(new qMRMLClipNodeWidgetPrivate(*this))`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:80: Q_D(qMRMLClipNodeWidget);`
- API footprints: `vtkMRMLClipNode::ClipIntersection`, `vtkMRMLClipNode::ClipUnion`, `vtkMRMLClipNode::SafeDownCast`

## widget: IntersectionRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Intersection | Use the intersection of the positive and/or negative spaces defined by the slice planes to clip the model. | IntersectionRadioButton | QRadioButton
- Text: Intersection
- Tooltip: Use the intersection of the positive and/or negative spaces defined by the slice planes to clip the model.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:67: clipTypeGroup->addButton(this->IntersectionRadioButton);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:70: QObject::connect(this->IntersectionRadioButton, SIGNAL(toggled(bool)), q, SLOT(updateNodeClipType()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:149: wasBlocking = d->IntersectionRadioButton->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:150: d->IntersectionRadioButton->setChecked(d->MRMLClipNode->GetClipType() == vtkMRMLClipNode::ClipIntersection);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:151: d->IntersectionRadioButton->blockSignals(wasBlocking);`
- Connected slots/functions: `updateNodeClipType`
- API footprints: `GetClipType`, `vtkMRMLClipNode::ClipIntersection`

## widget: UnionRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Union | Use the union of the positive and/or negative spaces defined by the slice planes to clip the model. | UnionRadioButton | QRadioButton
- Text: Union
- Tooltip: Use the union of the positive and/or negative spaces defined by the slice planes to clip the model.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:66: clipTypeGroup->addButton(this->UnionRadioButton);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:69: QObject::connect(this->UnionRadioButton, SIGNAL(toggled(bool)), q, SLOT(updateNodeClipType()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:124: return d->UnionRadioButton->isChecked() ? vtkMRMLClipNode::ClipUnion : vtkMRMLClipNode::ClipIntersection;`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:145: bool wasBlocking = d->UnionRadioButton->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:146: d->UnionRadioButton->setChecked(d->MRMLClipNode->GetClipType() == vtkMRMLClipNode::ClipUnion);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:147: d->UnionRadioButton->blockSignals(wasBlocking);`
- Connected slots/functions: `updateNodeClipType`
- API footprints: `GetClipType`, `vtkMRMLClipNode::ClipIntersection`, `vtkMRMLClipNode::ClipUnion`
- Key UI properties: {"checked": "true"}

## widget: ClippingTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Clipping Type: | When more than one slice plane is used, this option controls if it's the union or intersection of the positive and/or negative spaces that is used to clip the model. The parts of the model inside the selected space is kept, parts outside of the selection are clipped away. | ClippingTypeLabel | QLabel
- Text: Clipping Type:
- Tooltip: When more than one slice plane is used, this option controls if it's the union or intersection of the positive and/or negative spaces that is used to clip the model. The parts of the model inside the selected space is kept, parts outside of the selection are clipped away.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeWidget.h`

## widget: ClipNodeFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: ClipNodeFrame | QFrame
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:159: QList<QButtonGroup*> clipButtonGroups = d->ClipNodeFrame->findChildren<QButtonGroup*>("ClipButtonGroup");`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:206: while ((item = d->ClipNodeFrame->layout()->takeAt(0)))`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:285: d->ClipNodeFrame->layout()->addWidget(clipNodeFrame);`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:322: QList<qMRMLNodeComboBox*> clipNodeComboBoxes = d->ClipNodeFrame->findChildren<qMRMLNodeComboBox*>();`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:340: QList<QButtonGroup*> clipButtonGroups = d->ClipNodeFrame->findChildren<QButtonGroup*>("ClipButtonGroup");`
  - `Libs/MRML/Widgets/qMRMLClipNodeWidget.cxx:392: QList<qMRMLNodeComboBox*> clipNodeComboBoxes = d->ClipNodeFrame->findChildren<qMRMLNodeComboBox*>();`
