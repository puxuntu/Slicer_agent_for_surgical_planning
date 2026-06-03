# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLScalarsDisplayWidget.ui

- Owner class: `qMRMLScalarsDisplayWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLScalarsDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLScalarsDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLScalarsDisplayWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:25: #include "qMRMLScalarsDisplayWidget.h"`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:26: #include "ui_qMRMLScalarsDisplayWidget.h"`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:39: class qMRMLScalarsDisplayWidgetPrivate : public Ui_qMRMLScalarsDisplayWidget`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:41: Q_DECLARE_PUBLIC(qMRMLScalarsDisplayWidget);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:44: qMRMLScalarsDisplayWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:47: qMRMLScalarsDisplayWidgetPrivate(qMRMLScalarsDisplayWidget& object);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:61: qMRMLScalarsDisplayWidgetPrivate::qMRMLScalarsDisplayWidgetPrivate(qMRMLScalarsDisplayWidget& object)`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:69: void qMRMLScalarsDisplayWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:71: Q_Q(qMRMLScalarsDisplayWidget);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:94: QList<vtkMRMLModelDisplayNode*> qMRMLScalarsDisplayWidgetPrivate::currentModelDisplayNodes() const`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:111: qMRMLScalarsDisplayWidget::qMRMLScalarsDisplayWidget(QWidget* parentWidget)`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:113: , d_ptr(new qMRMLScalarsDisplayWidgetPrivate(*this))`
- API footprints: `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLDisplayNode::SafeDownCast`, `vtkMRMLDisplayNode::ScalarRangeFlagType`

## widget: ScalarsVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | ScalarsVisibilityLabel | QLabel
- Text: Visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`

## widget: ScalarsVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: ScalarsVisibilityCheckBox | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:76: QObject::connect(this->ScalarsVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setScalarsVisibility(bool)));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:208: return d->ScalarsVisibilityCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:419: if (d->ScalarsVisibilityCheckBox->isChecked() != (bool)firstDisplayNode->GetScalarVisibility())`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:421: wasBlocking = d->ScalarsVisibilityCheckBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:422: d->ScalarsVisibilityCheckBox->setChecked(firstDisplayNode->GetScalarVisibility());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:423: d->ScalarsVisibilityCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setScalarsVisibility`
- API footprints: `GetScalarVisibility`, `SetScalarVisibility`, `UpdateAssignedAttribute`

## widget: ActiveScalarLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Active Scalar: | ActiveScalarLabel | QLabel
- Text: Active Scalar:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`

## widget: ActiveScalarComboBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKDataSetArrayComboBox`
- Search text: ActiveScalarComboBox | ctkVTKDataSetArrayComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:77: QObject::connect(this->ActiveScalarComboBox, SIGNAL(activated(int)), q, SLOT(onCurrentArrayActivated()));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:215: this->setActiveScalarName(d->ActiveScalarComboBox->currentArrayName());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:227: displayNode->SetActiveScalar(arrayName.toUtf8(), d->ActiveScalarComboBox->currentArrayLocation());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:244: vtkAbstractArray* array = d->ActiveScalarComboBox->currentArray();`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:516: wasBlocking = d->ActiveScalarComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:517: d->ActiveScalarComboBox->setEnabled(firstDisplayNode);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:520: if (d->ActiveScalarComboBox->dataSet() != firstDisplayNode->GetScalarDataSet())`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:522: d->ActiveScalarComboBox->setDataSet(firstDisplayNode->GetScalarDataSet());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:524: if (d->ActiveScalarComboBox->currentArrayName() != firstDisplayNode->GetActiveScalarName())`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:526: d->ActiveScalarComboBox->setCurrentArray(firstDisplayNode->GetActiveScalarName());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:527: // Array location would need to be set in d->ActiveScalarComboBox if`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:531: d->ActiveScalarComboBox->blockSignals(wasBlocking);`
- Connected slots/functions: `onCurrentArrayActivated`
- API footprints: `GetActiveScalarName`, `GetName`, `GetScalarDataSet`, `SetActiveScalar`, `StartModify`

## widget: ScalarsColorTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color Table: | ScalarsColorTableLabel | QLabel
- Text: Color Table:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`

## widget: ScalarsColorNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: ScalarsColorNodeComboBox | qMRMLColorTableComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:78: QObject::connect(this->ScalarsColorNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setScalarsColorNode(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:272: return vtkMRMLColorNode::SafeDownCast(d->ScalarsColorNodeComboBox->currentNode());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:533: wasBlocking = d->ScalarsColorNodeComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:534: if (d->ScalarsColorNodeComboBox->mrmlScene() != this->mrmlScene())`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:536: d->ScalarsColorNodeComboBox->setMRMLScene(this->mrmlScene());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:538: if (d->ScalarsColorNodeComboBox->currentNodeID() != firstDisplayNode->GetColorNodeID())`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:540: d->ScalarsColorNodeComboBox->setCurrentNodeID(firstDisplayNode->GetColorNodeID());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:542: d->ScalarsColorNodeComboBox->setEnabled(firstDisplayNode->GetScalarRangeFlag() != vtkMRMLDisplayNode::UseDirectMapping);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:543: d->ScalarsColorNodeComboBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setScalarsColorNode`
- API footprints: `GetColorNodeID`, `GetScalarRangeFlag`, `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLDisplayNode::UseDirectMapping`

## widget: ScalarRangeModeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar Range Mode: | ScalarRangeModeLabel | QLabel
- Text: Scalar Range Mode:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`

## widget: DisplayedScalarRangeModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Set the scalar range mode flag. Data (auto) updates the Display Scalar Range from the scalar range of the data. Direct color mapping option bypasses lookup table and uses scalar values as RGB color. | DisplayedScalarRangeModeComboBox | QComboBox
- Tooltip: Set the scalar range mode flag. Data (auto) updates the Display Scalar Range from the scalar range of the data. Direct color mapping option bypasses lookup table and uses scalar values as RGB color.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:80: QObject::connect(this->DisplayedScalarRangeModeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setScalarRangeMode(int)));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:306: return (vtkMRMLDisplayNode::ScalarRangeFlagType)d->DisplayedScalarRangeModeComboBox->currentIndex();`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:512: wasBlocking = d->DisplayedScalarRangeModeComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:513: d->DisplayedScalarRangeModeComboBox->setCurrentIndex(firstDisplayNode->GetScalarRangeFlag());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:514: d->DisplayedScalarRangeModeComboBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setScalarRangeMode`
- API footprints: `GetScalarRangeFlag`, `SetScalarRangeFlag`, `vtkMRMLDisplayNode::ScalarRangeFlagType`

## widget: DisplayedScalarRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Displayed Range: | DisplayedScalarRangeLabel | QLabel
- Text: Displayed Range:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`

## widget: DisplayedScalarRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: Set the display scalar range, used when the Display option is selected. | DisplayedScalarRangeWidget | qMRMLRangeWidget
- Tooltip: Set the display scalar range, used when the Display option is selected.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:81: QObject::connect(this->DisplayedScalarRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(setScalarsDisplayRange(double, double)));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:360: return d->DisplayedScalarRangeWidget->minimumValue();`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:368: return d->DisplayedScalarRangeWidget->maximumValue();`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:381: d->DisplayedScalarRangeWidget->setMinimumValue(min);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:394: d->DisplayedScalarRangeWidget->setMaximumValue(max);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:464: wasBlocking = d->DisplayedScalarRangeWidget->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:467: d->DisplayedScalarRangeWidget->setRange(std::min(dataMin, displayRange[0]), std::max(dataMax, displayRange[1]));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:472: d->DisplayedScalarRangeWidget->range(currentRange);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:473: d->DisplayedScalarRangeWidget->setRange(std::min(currentRange[0], displayRange[0]), std::max(currentRange[1], displayRange[1]));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:475: d->DisplayedScalarRangeWidget->setValues(displayRange[0], displayRange[1]);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:476: d->DisplayedScalarRangeWidget->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:477: d->DisplayedScalarRangeWidget->setSingleStep(precision);`
- Connected slots/functions: `setScalarsDisplayRange`
- API footprints: `GetScalarRange`, `GetScalarRangeFlag`, `SetScalarRange`, `vtkMRMLDisplayNode::UseManualScalarRange`

## widget: ThresholdLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Threshold: | ThresholdLabel | QLabel
- Text: Threshold:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:406: d->ThresholdLabel->setVisible(firstModelDisplayNode != nullptr);`

## widget: ThresholdCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Apply thresholding to your displayed model based on its scalar values. Some cells normals might be flipped, in which case you
should set "backface" and "frontface" to OFF in the Representation options to visualize all cells. | ThresholdCheckBox | QCheckBox
- Tooltip: Apply thresholding to your displayed model based on its scalar values. Some cells normals might be flipped, in which case you
should set "backface" and "frontface" to OFF in the Representation options to visualize all cells.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:84: this->ThresholdCheckBox->setChecked(false);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:86: QObject::connect(this->ThresholdCheckBox, SIGNAL(toggled(bool)), q, SLOT(setTresholdEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:407: d->ThresholdCheckBox->setVisible(firstModelDisplayNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:507: wasBlocking = d->ThresholdCheckBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:508: d->ThresholdCheckBox->setEnabled(firstModelDisplayNode);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:509: d->ThresholdCheckBox->setChecked(firstModelDisplayNode && firstModelDisplayNode->GetThresholdEnabled());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:510: d->ThresholdCheckBox->blockSignals(wasBlocking);`
- Connected slots/functions: `setTresholdEnabled`
- API footprints: `GetThresholdEnabled`, `SetThresholdEnabled`

## widget: ThresholdRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkRangeWidget`
- Search text: Range used to threshold scalar values. | ThresholdRangeWidget | ctkRangeWidget
- Tooltip: Range used to threshold scalar values.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:85: this->ThresholdRangeWidget->setEnabled(false);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:87: QObject::connect(this->ThresholdRangeWidget, SIGNAL(valuesChanged(double, double)), q, SLOT(setThresholdRange(double, double)));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:408: d->ThresholdRangeWidget->setVisible(firstModelDisplayNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:487: wasBlocking = d->ThresholdRangeWidget->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:488: d->ThresholdRangeWidget->setEnabled(firstModelDisplayNode && firstModelDisplayNode->GetThresholdEnabled());`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:489: d->ThresholdRangeWidget->setRange(dataRange[0] - precision, dataRange[1] + precision);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:496: d->ThresholdRangeWidget->setValues(std::max(dataRange[0] - precision, thresholdRange[0]), std::min(dataRange[1] + precision, thresholdRange[1]));`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:501: d->ThresholdRangeWidget->setValues(dataRange[0], dataRange[1]);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:503: d->ThresholdRangeWidget->setDecimals(decimals);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:504: d->ThresholdRangeWidget->setSingleStep(precision);`
  - `Libs/MRML/Widgets/qMRMLScalarsDisplayWidget.cxx:505: d->ThresholdRangeWidget->blockSignals(wasBlocking);`
- Connected slots/functions: `setThresholdRange`
- API footprints: `GetThresholdEnabled`, `GetThresholdMax`, `GetThresholdMin`, `SetThresholdRange`
