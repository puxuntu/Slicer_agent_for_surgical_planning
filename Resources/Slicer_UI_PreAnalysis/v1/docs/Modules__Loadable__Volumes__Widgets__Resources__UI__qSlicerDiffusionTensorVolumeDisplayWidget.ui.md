# Slicer UI Analysis: Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerDiffusionTensorVolumeDisplayWidget.ui

- Owner class: `qSlicerDiffusionTensorVolumeDisplayWidget`
- UI file: `Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerDiffusionTensorVolumeDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerDiffusionTensorVolumeDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerDiffusionTensorVolumeDisplayWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:21: #include "qSlicerDiffusionTensorVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:22: #include "ui_qSlicerDiffusionTensorVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:37: class qSlicerDiffusionTensorVolumeDisplayWidgetPrivate : public Ui_qSlicerDiffusionTensorVolumeDisplayWidget`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:39: Q_DECLARE_PUBLIC(qSlicerDiffusionTensorVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:42: qSlicerDiffusionTensorVolumeDisplayWidget* const q_ptr;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:45: qSlicerDiffusionTensorVolumeDisplayWidgetPrivate(qSlicerDiffusionTensorVolumeDisplayWidget& object);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:46: ~qSlicerDiffusionTensorVolumeDisplayWidgetPrivate();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:53: qSlicerDiffusionTensorVolumeDisplayWidgetPrivate::qSlicerDiffusionTensorVolumeDisplayWidgetPrivate(qSlicerDiffusionTensorVolumeDisplayWidget& object)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:59: qSlicerDiffusionTensorVolumeDisplayWidgetPrivate ::~qSlicerDiffusionTensorVolumeDisplayWidgetPrivate() = default;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:62: void qSlicerDiffusionTensorVolumeDisplayWidgetPrivate::init()`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:64: Q_Q(qSlicerDiffusionTensorVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:76: void qSlicerDiffusionTensorVolumeDisplayWidgetPrivate::glyphsOnSlicesDisplaySetEnabled(bool enabled)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ScalarVolumeDisplayWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> DTISliceDisplayWidget.setMRMLScene(vtkMRMLScene*)`
- API footprints: `vtkMRMLDiffusionTensorVolumeNode::SafeDownCast`

## widget: CollapsibleGroupBox_2

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_2 | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`

## widget: ScalarInvariantLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar Mode: | ScalarInvariantLabel | QLabel
- Text: Scalar Mode:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`

## widget: ScalarInvariantComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLScalarInvariantComboBox`
- Search text: ScalarInvariantComboBox | qMRMLScalarInvariantComboBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:69: QObject::connect(this->ScalarInvariantComboBox, SIGNAL(scalarInvariantChanged(int)), q, SLOT(setVolumeScalarInvariant(int)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:189: d->ScalarInvariantComboBox->setScalarInvariant(displayNode->GetScalarInvariant());`
- Connected slots/functions: `setVolumeScalarInvariant`
- API footprints: `GetScalarInvariant`, `SetScalarInvariant`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientation`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientationMiddleEigenvector`

## widget: ScalarVolumeDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerScalarVolumeDisplayWidget`
- Search text: ScalarVolumeDisplayWidget | qSlicerScalarVolumeDisplayWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:147: d->ScalarVolumeDisplayWidget->setMRMLVolumeNode(volumeNode);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:194: d->ScalarVolumeDisplayWidget->setColorTableComboBoxEnabled(false);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:195: d->ScalarVolumeDisplayWidget->setMRMLWindowLevelWidgetEnabled(false);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:201: d->ScalarVolumeDisplayWidget->setColorTableComboBoxEnabled(true);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:202: d->ScalarVolumeDisplayWidget->setMRMLWindowLevelWidgetEnabled(true);`
- API footprints: `AutoScalarRangeOn`, `AutoWindowLevelOn`, `GetScalarInvariant`, `GetVolumeDisplayNode`, `vtkMRMLDiffusionTensorDisplayPropertiesNode::ColorOrientationMinEigenvector`

## widget: GlyphsOnSlicesDisplayCollapsibleGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: GlyphsOnSlicesDisplayCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:78: this->GlyphsOnSlicesDisplayCollapsibleGroupBox->setEnabled(enabled);`

## widget: GlyphVisibilityLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Slice Visibility: | GlyphVisibilityLabel | QLabel
- Text: Slice Visibility:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`, `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:353: return d->GlyphVisibilityLabel->isVisibleTo(const_cast<qSlicerDTISliceDisplayWidget*>(this));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDTISliceDisplayWidget.cxx:360: d->GlyphVisibilityLabel->setVisible(!hide);`

## widget: RedSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Red | RedSliceCheckBox | QCheckBox
- Text: Red
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:70: QObject::connect(this->RedSliceCheckBox, SIGNAL(toggled(bool)), q, SLOT(setRedSliceVisible(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:81: this->RedSliceCheckBox->setCheckState(Qt::Unchecked);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:159: d->RedSliceCheckBox->setChecked(dtiSliceDisplayNodes[0]->GetVisibility());`
- Connected slots/functions: `setRedSliceVisible`
- API footprints: `GetVisibility`, `SetVisibility`

## widget: YellowSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Yellow | YellowSliceCheckBox | QCheckBox
- Text: Yellow
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:71: QObject::connect(this->YellowSliceCheckBox, SIGNAL(toggled(bool)), q, SLOT(setYellowSliceVisible(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:82: this->YellowSliceCheckBox->setCheckState(Qt::Unchecked);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:162: d->YellowSliceCheckBox->setChecked(dtiSliceDisplayNodes[1]->GetVisibility());`
- Connected slots/functions: `setYellowSliceVisible`
- API footprints: `GetVisibility`, `SetVisibility`

## widget: GreenSliceCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Green | GreenSliceCheckBox | QCheckBox
- Text: Green
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:72: QObject::connect(this->GreenSliceCheckBox, SIGNAL(toggled(bool)), q, SLOT(setGreenSliceVisible(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:83: this->GreenSliceCheckBox->setCheckState(Qt::Unchecked);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:166: d->GreenSliceCheckBox->setChecked(dtiSliceDisplayNodes[1]->GetVisibility());`
- Connected slots/functions: `setGreenSliceVisible`
- API footprints: `GetVisibility`, `SetVisibility`

## widget: DTISliceDisplayWidget

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerDTISliceDisplayWidget`
- Search text: DTISliceDisplayWidget | qSlicerDTISliceDisplayWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:67: this->DTISliceDisplayWidget->setVisibilityHidden(true);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerDiffusionTensorVolumeDisplayWidget.cxx:172: d->DTISliceDisplayWidget->setMRMLDTISliceDisplayNode(glyphableVolumeSliceNode);`
