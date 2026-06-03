# Slicer UI Analysis: Modules/Loadable/Units/Widgets/Resources/UI/qMRMLUnitWidget.ui

- Owner class: `qMRMLUnitWidget`
- UI file: `Modules/Loadable/Units/Widgets/Resources/UI/qMRMLUnitWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLUnitWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLUnitWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:25: #include "qMRMLUnitWidget.h"`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:26: #include "ui_qMRMLUnitWidget.h"`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:32: class qMRMLUnitWidgetPrivate : public Ui_qMRMLUnitWidget`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:34: Q_DECLARE_PUBLIC(qMRMLUnitWidget);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:37: qMRMLUnitWidget* const q_ptr;`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:40: qMRMLUnitWidgetPrivate(qMRMLUnitWidget& obj);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:42: void setupUi(qMRMLUnitWidget*);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:47: qMRMLUnitWidget::UnitProperties DisplayFlags;`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:48: qMRMLUnitWidget::UnitProperties EditableProperties;`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:52: // qMRMLUnitWidgetPrivate methods`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:55: qMRMLUnitWidgetPrivate::qMRMLUnitWidgetPrivate(qMRMLUnitWidget& object)`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:59: this->DisplayFlags = qMRMLUnitWidget::All;`
- API footprints: `vtkMRMLUnitNode::SafeDownCast`

## widget: PresetLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Preset | PresetLabel | QLabel
- Text: Preset
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:115: this->PresetLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Preset));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:116: this->PresetLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Preset));`

## widget: PresetNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: PresetNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:92: QObject::connect(this->PresetNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setUnitFromPreset(vtkMRMLNode*)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:113: this->PresetNodeComboBox->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Preset));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:114: this->PresetNodeComboBox->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Preset));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:226: d->PresetNodeComboBox->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:243: bool modifying = d->PresetNodeComboBox->blockSignals(true);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:244: d->PresetNodeComboBox->addAttribute("vtkMRMLUnitNode", "Quantity", d->CurrentUnitNode->GetQuantity());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:245: d->PresetNodeComboBox->setMRMLScene(this->mrmlScene());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:246: d->PresetNodeComboBox->setCurrentNode(nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:247: d->PresetNodeComboBox->blockSignals(modifying);`
- Connected slots/functions: `setUnitFromPreset`
- API footprints: `EndModify`, `GetDisplayCoefficient`, `GetDisplayOffset`, `GetMaximumValue`, `GetMinimumValue`, `GetName`, `GetPrecision`, `GetPrefix`, `GetQuantity`, `GetSuffix`, `SetDisplayCoefficient`, `SetDisplayOffset`, `SetMaximumValue`, `SetMinimumValue`, `SetPrecision`, `SetPrefix`, `SetQuantity`, `SetSuffix`, `StartModify`, `vtkMRMLUnitNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLUnitNode"]}

## widget: PrefixLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Prefix | PrefixLabel | QLabel
- Text: Prefix
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:133: this->PrefixLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Prefix));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:134: this->PrefixLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Prefix));`

## widget: PrefixLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the prefix of the unit.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">The unit prefix will be displayed in the application before the unit's value. For example, the prefix &quot;</span><span style=" font-size:8pt; font-weight:600;">$</span><span style=" font-size:8pt;">&quot; could be used before an unit.</span></p></body></html> | PrefixLineEdit | QLineEdit
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the prefix of the unit.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">The unit prefix will be displayed in the application before the unit's value. For example, the prefix &quot;</span><span style=" font-size:8pt; font-weight:600;">$</span><span style=" font-size:8pt;">&quot; could be used before an unit.</span></p></body></html>
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:74: QObject::connect(this->PrefixLineEdit, SIGNAL(textChanged(QString)), q, SLOT(setPrefix(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:75: QObject::connect(this->PrefixLineEdit, SIGNAL(textChanged(QString)), q, SIGNAL(prefixChanged(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:101: this->PrefixLineEdit->clear();`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:131: this->PrefixLineEdit->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Prefix));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:132: this->PrefixLineEdit->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Prefix));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:228: d->PrefixLineEdit->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:252: d->PrefixLineEdit->setText(QString(d->CurrentUnitNode->GetPrefix()));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:300: return d->PrefixLineEdit->text();`
- Connected slots/functions: `setPrefix`
- API footprints: `GetMinimumValue`, `GetPrecision`, `GetPrefix`, `GetQuantity`, `GetSuffix`, `SetPrefix`

## widget: SuffixLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Suffix | SuffixLabel | QLabel
- Text: Suffix
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:138: this->SuffixLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Suffix));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:139: this->SuffixLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Suffix));`

## widget: SuffixLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the suffix of the unit. For example, the suffix for the unit </span><span style=" font-size:8pt; font-weight:600;">Meter</span><span style=" font-size:8pt;"> should probably be </span><span style=" font-size:8pt; font-weight:600;">m</span><span style=" font-size:8pt;">.</span></p></body></html> | SuffixLineEdit | QLineEdit
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the suffix of the unit. For example, the suffix for the unit </span><span style=" font-size:8pt; font-weight:600;">Meter</span><span style=" font-size:8pt;"> should probably be </span><span style=" font-size:8pt; font-weight:600;">m</span><span style=" font-size:8pt;">.</span></p></body></html>
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:76: QObject::connect(this->SuffixLineEdit, SIGNAL(textChanged(QString)), q, SLOT(setSuffix(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:77: QObject::connect(this->SuffixLineEdit, SIGNAL(textChanged(QString)), q, SIGNAL(suffixChanged(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:102: this->SuffixLineEdit->clear();`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:136: this->SuffixLineEdit->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Suffix));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:137: this->SuffixLineEdit->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Suffix));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:229: d->SuffixLineEdit->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:251: d->SuffixLineEdit->setText(d->CurrentUnitNode->GetSuffix());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:320: return d->SuffixLineEdit->text();`
- Connected slots/functions: `setSuffix`
- API footprints: `GetName`, `GetPrecision`, `GetPrefix`, `GetQuantity`, `GetSuffix`, `SetSuffix`

## widget: MaximumValueLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Maximum | MaximumValueLabel | QLabel
- Text: Maximum
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:153: this->MaximumValueLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Maximum));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:154: this->MaximumValueLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Maximum));`

## widget: MaximumSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the maximum value possible for the unit.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">For example, a speed unit (in </span><span style=" font-size:8pt; font-weight:600;">m.s</span><span style=" font-size:8pt; font-weight:600; vertical-align:super;">-1</span><span style=" font-size:8pt;">) should probably have a maximum of 3e6. </span></p></body></html> | MaximumSpinBox | ctkDoubleSpinBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the maximum value possible for the unit.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">For example, a speed unit (in </span><span style=" font-size:8pt; font-weight:600;">m.s</span><span style=" font-size:8pt; font-weight:600; vertical-align:super;">-1</span><span style=" font-size:8pt;">) should probably have a maximum of 3e6. </span></p></body></html>
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:84: QObject::connect(this->MaximumSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setMaximum(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:85: QObject::connect(this->MaximumSpinBox, SIGNAL(valueChanged(double)), q, SIGNAL(maximumChanged(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:105: this->MaximumSpinBox->setValue(1000);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:151: this->MaximumSpinBox->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Maximum));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:152: this->MaximumSpinBox->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Maximum));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:232: d->MaximumSpinBox->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:255: d->MaximumSpinBox->setValue(d->CurrentUnitNode->GetMaximumValue());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:312: d->MaximumSpinBox->setPrefix(newPrefix);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:332: d->MaximumSpinBox->setSuffix(newSuffix);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:352: d->MaximumSpinBox->setDecimals(newPrecision);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:383: return d->MaximumSpinBox->value();`
- Connected slots/functions: `setMaximum`
- API footprints: `GetDisplayCoefficient`, `GetDisplayOffset`, `GetMaximumValue`, `GetMinimumValue`, `GetPrecision`, `SetMaximumValue`, `SetPrecision`, `SetPrefix`, `SetSuffix`

## widget: PrecisionLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Precision | PrecisionLabel | QLabel
- Text: Precision
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:143: this->PrecisionLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Precision));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:144: this->PrecisionLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Precision));`

## widget: PrecisionSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the precision (i.e. number of significant digits) of the unit.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">This is used by the GUI to determine how many digits one can input for the current unit. For example, with a </span><span style=" font-size:8pt; font-weight:600;">Precision</span><span style=" font-size:8pt;"> of 3 the 1.0123 will be rounded to 1.112.</span></p></body></html> | PrecisionSpinBox | QSpinBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set the precision (i.e. number of significant digits) of the unit.</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">This is used by the GUI to determine how many digits one can input for the current unit. For example, with a </span><span style=" font-size:8pt; font-weight:600;">Precision</span><span style=" font-size:8pt;"> of 3 the 1.0123 will be rounded to 1.112.</span></p></body></html>
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:79: QObject::connect(this->PrecisionSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setPrecision(int)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:80: QObject::connect(this->PrecisionSpinBox, SIGNAL(valueChanged(int)), q, SIGNAL(precisionChanged(int)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:103: this->PrecisionSpinBox->setValue(3);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:141: this->PrecisionSpinBox->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Precision));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:142: this->PrecisionSpinBox->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Precision));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:230: d->PrecisionSpinBox->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:253: d->PrecisionSpinBox->setValue(d->CurrentUnitNode->GetPrecision());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:340: return d->PrecisionSpinBox->value();`
- Connected slots/functions: `setPrecision`
- API footprints: `GetMaximumValue`, `GetMinimumValue`, `GetPrecision`, `GetPrefix`, `GetSuffix`, `SetPrecision`

## widget: MinimumValueLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Minimum | MinimumValueLabel | QLabel
- Text: Minimum
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:148: this->MinimumValueLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Minimum));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:149: this->MinimumValueLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Minimum));`

## widget: MinimumSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Set the minimum value possible for the unit.</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">For example, a temperature unit (in <span style=" font-weight:600;">Kelvin</span>) should probably have a minimum of 0. </p></body></html> | MinimumSpinBox | ctkDoubleSpinBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Set the minimum value possible for the unit.</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">For example, a temperature unit (in <span style=" font-weight:600;">Kelvin</span>) should probably have a minimum of 0. </p></body></html>
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:82: QObject::connect(this->MinimumSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setMinimum(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:83: QObject::connect(this->MinimumSpinBox, SIGNAL(valueChanged(double)), q, SIGNAL(minimumChanged(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:104: this->MinimumSpinBox->setValue(-1000);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:146: this->MinimumSpinBox->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Minimum));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:147: this->MinimumSpinBox->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Minimum));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:231: d->MinimumSpinBox->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:254: d->MinimumSpinBox->setValue(d->CurrentUnitNode->GetMinimumValue());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:313: d->MinimumSpinBox->setPrefix(newPrefix);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:333: d->MinimumSpinBox->setSuffix(newSuffix);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:353: d->MinimumSpinBox->setDecimals(newPrecision);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:363: return d->MinimumSpinBox->value();`
- Connected slots/functions: `setMinimum`
- API footprints: `GetDisplayCoefficient`, `GetMaximumValue`, `GetMinimumValue`, `GetPrecision`, `GetPrefix`, `SetMinimumValue`

## widget: NameLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Name | NameLabel | QLabel
- Text: Name
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:123: this->NameLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Name));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:124: this->NameLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Name));`

## widget: NameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: NameLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:69: QObject::connect(this->NameLineEdit, SIGNAL(textChanged(QString)), q, SLOT(setName(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:70: QObject::connect(this->NameLineEdit, SIGNAL(textChanged(QString)), q, SIGNAL(nameChanged(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:99: this->NameLineEdit->clear();`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:121: this->NameLineEdit->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Name));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:122: this->NameLineEdit->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Name));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:227: d->NameLineEdit->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:249: d->NameLineEdit->setText(d->CurrentUnitNode->GetName());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:264: return d->NameLineEdit->text();`
- Connected slots/functions: `setName`
- API footprints: `GetName`, `GetQuantity`, `GetSuffix`, `SetName`

## widget: SeparationLine

- Confidence: `linked_to_code`
- Widget/action class: `Line`
- Search text: SeparationLine | Line
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:118: this->SeparationLine->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Preset) //`

## widget: QuantityLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Quantity | QuantityLabel | QLabel
- Text: Quantity
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:128: this->QuantityLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Quantity));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:129: this->QuantityLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Quantity));`

## widget: QuantityLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: QuantityLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:71: QObject::connect(this->QuantityLineEdit, SIGNAL(textChanged(QString)), q, SLOT(setQuantity(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:72: QObject::connect(this->QuantityLineEdit, SIGNAL(textChanged(QString)), q, SIGNAL(quantityChanged(QString)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:100: this->QuantityLineEdit->clear();`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:126: this->QuantityLineEdit->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Quantity));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:127: this->QuantityLineEdit->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Quantity));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:250: d->QuantityLineEdit->setText(d->CurrentUnitNode->GetQuantity());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:282: return d->QuantityLineEdit->text();`
- Connected slots/functions: `setQuantity`
- API footprints: `GetName`, `GetPrefix`, `GetQuantity`, `GetSuffix`, `SetQuantity`

## widget: CoefficientLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Coefficient | CoefficientLabel | QLabel
- Text: Coefficient
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:158: this->CoefficientLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Coefficient));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:159: this->CoefficientLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Coefficient));`

## widget: CoefficientSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: CoefficientSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:87: QObject::connect(this->CoefficientSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setCoefficient(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:88: QObject::connect(this->CoefficientSpinBox, SIGNAL(valueChanged(double)), q, SIGNAL(coefficientChanged(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:106: this->CoefficientSpinBox->setValue(1.0);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:156: this->CoefficientSpinBox->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Coefficient));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:157: this->CoefficientSpinBox->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Coefficient));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:233: d->CoefficientSpinBox->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:256: d->CoefficientSpinBox->setValue(d->CurrentUnitNode->GetDisplayCoefficient());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:355: d->CoefficientSpinBox->setDecimals(newPrecision);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:403: return d->CoefficientSpinBox->value();`
- Connected slots/functions: `setCoefficient`
- API footprints: `GetDisplayCoefficient`, `GetDisplayOffset`, `GetMaximumValue`, `GetMinimumValue`, `SetDisplayCoefficient`

## widget: OffsetLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Offset | OffsetLabel | QLabel
- Text: Offset
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:163: this->OffsetLabel->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Offset));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:164: this->OffsetLabel->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Offset));`

## widget: OffsetSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: OffsetSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:89: QObject::connect(this->OffsetSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setOffset(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:90: QObject::connect(this->OffsetSpinBox, SIGNAL(valueChanged(double)), q, SIGNAL(offsetChanged(double)));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:107: this->OffsetSpinBox->setValue(0.0);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:161: this->OffsetSpinBox->setVisible(this->DisplayFlags.testFlag(qMRMLUnitWidget::Offset));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:162: this->OffsetSpinBox->setEnabled(this->EditableProperties.testFlag(qMRMLUnitWidget::Offset));`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:234: d->OffsetSpinBox->setEnabled(d->CurrentUnitNode != nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:257: d->OffsetSpinBox->setValue(d->CurrentUnitNode->GetDisplayOffset());`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:356: d->OffsetSpinBox->setDecimals(newPrecision);`
  - `Modules/Loadable/Units/Widgets/qMRMLUnitWidget.cxx:423: return d->OffsetSpinBox->value();`
- Connected slots/functions: `setOffset`
- API footprints: `GetDisplayCoefficient`, `GetDisplayOffset`, `GetMaximumValue`, `SetDisplayOffset`
