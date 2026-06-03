# Slicer UI Analysis: Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerScalarVolumeDisplayWidget.ui

- Owner class: `qSlicerScalarVolumeDisplayWidget`
- UI file: `Modules/Loadable/Volumes/Widgets/Resources/UI/qSlicerScalarVolumeDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerScalarVolumeDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerScalarVolumeDisplayWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:1: #include "qSlicerScalarVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:2: #include "ui_qSlicerScalarVolumeDisplayWidget.h"`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:41: class qSlicerScalarVolumeDisplayWidgetPrivate : public Ui_qSlicerScalarVolumeDisplayWidget`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:43: Q_DECLARE_PUBLIC(qSlicerScalarVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:46: qSlicerScalarVolumeDisplayWidget* const q_ptr;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:49: qSlicerScalarVolumeDisplayWidgetPrivate(qSlicerScalarVolumeDisplayWidget& object);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:50: ~qSlicerScalarVolumeDisplayWidgetPrivate();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:60: qSlicerScalarVolumeDisplayWidgetPrivate::qSlicerScalarVolumeDisplayWidgetPrivate(qSlicerScalarVolumeDisplayWidget& object)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:68: qSlicerScalarVolumeDisplayWidgetPrivate::~qSlicerScalarVolumeDisplayWidgetPrivate()`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:74: void qSlicerScalarVolumeDisplayWidgetPrivate::init()`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:76: Q_Q(qSlicerScalarVolumeDisplayWidget);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:110: QString presetName = qSlicerScalarVolumeDisplayWidget::tr(preset.name.c_str());`
- API footprints: `GetVolumeDisplayPreset`, `vtkMRMLScalarVolumeNode::SafeDownCast`

## widget: PresetsGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `QGroupBox`
- Search text: PresetsGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:99: QLayout* volumeDisplayPresetsLayout = this->PresetsGroupBox->layout();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:103: this->PresetsGroupBox->setLayout(volumeDisplayPresetsLayout);`
- API footprints: `GetVolumeDisplayPresetIDs`

## widget: LookupTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Lookup Table: | LookupTableLabel | QLabel
- Text: Lookup Table:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`

## widget: ColorTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: Select the color mapping for scalar volumes to colors. | ColorTableComboBox | qMRMLColorTableComboBox
- Tooltip: Select the color mapping for scalar volumes to colors.
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:131: QObject::connect(this->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setColorNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:158: bool qSlicerScalarVolumeDisplayWidget::isColorTableComboBoxEnabled() const`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:161: return d->ColorTableComboBox->isEnabled();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:165: void qSlicerScalarVolumeDisplayWidget::setColorTableComboBoxEnabled(bool enable)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:168: d->ColorTableComboBox->setEnabled(enable);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:222: QSignalBlocker blocker1(d->ColorTableComboBox);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:225: d->ColorTableComboBox->setCurrentNode(displayNode->GetColorNode());`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h:24: Q_PROPERTY(bool enableColorTableComboBox READ isColorTableComboBoxEnabled WRITE setColorTableComboBoxEnabled)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h:35: bool isColorTableComboBoxEnabled() const;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h:36: void setColorTableComboBoxEnabled(bool);`
- Connected slots/functions: `setColorNode`
- API footprints: `GetColorNode`, `GetID`, `GetInterpolate`, `GetInvertDisplayScalarRange`, `SetAndObserveColorNodeID`, `vtkMRMLColorNode::SafeDownCast`

## widget: InterpolateLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Interpolate: | InterpolateLabel | QLabel
- Text: Interpolate:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`

## widget: InterpolateCheckbox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: When checked, slice views will display linearly interpolated slices through input volumes. Unchecked indicates nearest neighbor resampling. | InterpolateCheckbox | QCheckBox
- Tooltip: When checked, slice views will display linearly interpolated slices through input volumes. Unchecked indicates nearest neighbor resampling.
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:129: QObject::connect(this->InterpolateCheckbox, SIGNAL(toggled(bool)), q, SLOT(setInterpolate(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:223: QSignalBlocker blocker2(d->InterpolateCheckbox);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:226: d->InterpolateCheckbox->setChecked(displayNode->GetInterpolate());`
- Connected slots/functions: `setInterpolate`
- API footprints: `GetColorNode`, `GetInterpolate`, `GetInvertDisplayScalarRange`, `SetInterpolate`

## widget: InvertDisplayScalarRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Invert: | InvertDisplayScalarRangeLabel | QLabel
- Text: Invert:
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`

## widget: InvertDisplayScalarRangeCheckbox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Reverse the order of colors in the lookup table to display this volume. | InvertDisplayScalarRangeCheckbox | QCheckBox
- Tooltip: Reverse the order of colors in the lookup table to display this volume.
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:130: QObject::connect(this->InvertDisplayScalarRangeCheckbox, SIGNAL(toggled(bool)), q, SLOT(setInvert(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:224: QSignalBlocker blocker3(d->InvertDisplayScalarRangeCheckbox);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:227: d->InvertDisplayScalarRangeCheckbox->setChecked(displayNode->GetInvertDisplayScalarRange());`
- Connected slots/functions: `setInvert`
- API footprints: `GetColorNode`, `GetInterpolate`, `GetInvertDisplayScalarRange`, `SetInvertDisplayScalarRange`

## widget: groupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`

## widget: MRMLWindowLevelWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWindowLevelWidget`
- Search text: MRMLWindowLevelWidget | qMRMLWindowLevelWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:154: return vtkMRMLScalarVolumeNode::SafeDownCast(d->MRMLWindowLevelWidget->mrmlVolumeNode());`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:172: bool qSlicerScalarVolumeDisplayWidget::isMRMLWindowLevelWidgetEnabled() const`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:175: return d->MRMLWindowLevelWidget->isEnabled();`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:179: void qSlicerScalarVolumeDisplayWidget::setMRMLWindowLevelWidgetEnabled(bool enable)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:182: d->MRMLWindowLevelWidget->setEnabled(enable);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:207: d->MRMLWindowLevelWidget->setMRMLVolumeNode(volumeNode);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h:25: Q_PROPERTY(bool enableMRMLWindowLevelWidget READ isMRMLWindowLevelWidgetEnabled WRITE setMRMLWindowLevelWidgetEnabled)`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h:38: bool isMRMLWindowLevelWidgetEnabled() const;`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h:39: void setMRMLWindowLevelWidgetEnabled(bool);`
- API footprints: `GetVolumeDisplayNode`, `vtkMRMLScalarVolumeNode::SafeDownCast`

## widget: groupBox_2

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_2 | QGroupBox
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`

## widget: MRMLVolumeThresholdWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLVolumeThresholdWidget`
- Search text: MRMLVolumeThresholdWidget | qMRMLVolumeThresholdWidget
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:208: d->MRMLVolumeThresholdWidget->setMRMLVolumeNode(volumeNode);`

## widget: HistogramGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: Shows the number of pixels (y axis) vs the image intensity (x axis) over a background of the current window/level and threshold mapping. | HistogramGroupBox | ctkCollapsibleGroupBox
- Tooltip: Shows the number of pixels (y axis) vs the image intensity (x axis) over a background of the current window/level and threshold mapping.
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:132: QObject::connect(this->HistogramGroupBox, SIGNAL(toggled(bool)), q, SLOT(onHistogramSectionExpanded(bool)));`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:251: if (d->HistogramGroupBox->testAttribute(Qt::WA_WState_Created))`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:253: d->HistogramGroupBox->setVisible(voxelValues != nullptr);`
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:261: if (!voxelValues || !this->isVisible() || d->HistogramGroupBox->collapsed())`
- Connected slots/functions: `onHistogramSectionExpanded`
- API footprints: `RemoveAllPoints`
- Key UI properties: {"checked": "false"}

## widget: TransferFunctionView

- Confidence: `linked_to_code`
- Widget/action class: `ctkTransferFunctionView`
- Search text: TransferFunctionView | ctkTransferFunctionView
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:80: ctkTransferFunctionScene* scene = qobject_cast<ctkTransferFunctionScene*>(this->TransferFunctionView->scene());`

## widget: MinValueLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: 0 | MinValueLabel | QLabel
- Text: 0
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:299: d->MinValueLabel->setText(QString::number(range[0], 'g', 5));`

## widget: CenterValueLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: 0 | CenterValueLabel | QLabel
- Text: 0
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:300: d->CenterValueLabel->setText(QString::number(center, 'g', 5));`

## widget: MaxValueLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: 0 | MaxValueLabel | QLabel
- Text: 0
- Implementation candidates: `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx`, `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/Widgets/qSlicerScalarVolumeDisplayWidget.cxx:301: d->MaxValueLabel->setText(QString::number(range[1], 'g', 5));`
