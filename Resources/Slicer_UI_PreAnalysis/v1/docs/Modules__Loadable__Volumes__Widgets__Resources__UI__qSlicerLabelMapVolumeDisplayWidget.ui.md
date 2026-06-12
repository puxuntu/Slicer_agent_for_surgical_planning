# Slicer UI Analysis: Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerLabelMapVolumeDisplayWidget.ui

- Owner class: `qSlicerLabelMapVolumeDisplayWidget`
- UI file: `Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerLabelMapVolumeDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerLabelMapVolumeDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerLabelMapVolumeDisplayWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:21: #include "qSlicerLabelMapVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:22: #include "ui_qSlicerLabelMapVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:34: class qSlicerLabelMapVolumeDisplayWidgetPrivate : public Ui_qSlicerLabelMapVolumeDisplayWidget`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:36: Q_DECLARE_PUBLIC(qSlicerLabelMapVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:39: qSlicerLabelMapVolumeDisplayWidget* const q_ptr;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:42: qSlicerLabelMapVolumeDisplayWidgetPrivate(qSlicerLabelMapVolumeDisplayWidget& object);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:43: ~qSlicerLabelMapVolumeDisplayWidgetPrivate();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:50: qSlicerLabelMapVolumeDisplayWidgetPrivate::qSlicerLabelMapVolumeDisplayWidgetPrivate(qSlicerLabelMapVolumeDisplayWidget& object)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:57: qSlicerLabelMapVolumeDisplayWidgetPrivate::~qSlicerLabelMapVolumeDisplayWidgetPrivate() = default;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:60: void qSlicerLabelMapVolumeDisplayWidgetPrivate::init()`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:62: Q_Q(qSlicerLabelMapVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:73: qSlicerLabelMapVolumeDisplayWidget::qSlicerLabelMapVolumeDisplayWidget(QWidget* _parent)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ColorTableComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetVolumeDisplayNode`, `vtkMRMLLabelMapVolumeDisplayNode::SafeDownCast`, `vtkMRMLScalarVolumeNode::SafeDownCast`

## widget: SliceIntersectionThicknessSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: When displaying the label map with the outline/not filled option, this controls the width of the outline. | SliceIntersectionThicknessSpinBox | QSpinBox
- Tooltip: When displaying the label map with the outline/not filled option, this controls the width of the outline.
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:66: QObject::connect(this->SliceIntersectionThicknessSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setSliceIntersectionThickness(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:124: d->SliceIntersectionThicknessSpinBox->setValue(displayNode->GetSliceIntersectionThickness());`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:155: return d->SliceIntersectionThicknessSpinBox->value();`
- Connected slots/functions: `setSliceIntersectionThickness`
- API footprints: `GetColorNode`, `GetSliceIntersectionThickness`, `SetSliceIntersectionThickness`

## widget: ColorTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: ColorTableComboBox | qMRMLColorTableComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:65: QObject::connect(this->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setColorNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx:123: d->ColorTableComboBox->setCurrentNode(displayNode->GetColorNode());`
- Connected slots/functions: `setColorNode`
- API footprints: `GetColorNode`, `GetID`, `GetSliceIntersectionThickness`, `SetAndObserveColorNodeID`, `vtkMRMLColorNode::SafeDownCast`

## widget: LookupTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Lookup Table: | LookupTableLabel | QLabel
- Text: Lookup Table:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.h`

## widget: SliceIntersectionThicknessLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Label Outline &Thickness: | SliceIntersectionThicknessLabel | QLabel
- Text: Label Outline &Thickness:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerLabelMapVolumeDisplayWidget.h`
