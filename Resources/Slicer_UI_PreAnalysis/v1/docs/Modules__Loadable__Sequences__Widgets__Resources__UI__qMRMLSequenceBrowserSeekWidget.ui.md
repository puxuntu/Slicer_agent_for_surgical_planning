# Slicer UI Analysis: Modules/Loadable/Sequences/Widgets/Resources/UI/qMRMLSequenceBrowserSeekWidget.ui

- Owner class: `qMRMLSequenceBrowserSeekWidget`
- UI file: `Modules/Loadable/Sequences/Widgets/Resources/UI/qMRMLSequenceBrowserSeekWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSequenceBrowserSeekWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLSequenceBrowserSeekWidget | QWidget
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:19: #include "qMRMLSequenceBrowserSeekWidget.h"`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:20: #include "ui_qMRMLSequenceBrowserSeekWidget.h"`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:31: class qMRMLSequenceBrowserSeekWidgetPrivate : public Ui_qMRMLSequenceBrowserSeekWidget`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:33: Q_DECLARE_PUBLIC(qMRMLSequenceBrowserSeekWidget);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:36: qMRMLSequenceBrowserSeekWidget* const q_ptr;`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:39: qMRMLSequenceBrowserSeekWidgetPrivate(qMRMLSequenceBrowserSeekWidget& object);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:46: // qMRMLSequenceBrowserSeekWidgetPrivate methods`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:49: qMRMLSequenceBrowserSeekWidgetPrivate::qMRMLSequenceBrowserSeekWidgetPrivate(qMRMLSequenceBrowserSeekWidget& object)`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:55: void qMRMLSequenceBrowserSeekWidgetPrivate::init()`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:57: Q_Q(qMRMLSequenceBrowserSeekWidget);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:65: // qMRMLSequenceBrowserSeekWidget methods`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:68: qMRMLSequenceBrowserSeekWidget::qMRMLSequenceBrowserSeekWidget(QWidget* newParent)`
- API footprints: `GetMasterSequenceNode`, `GetPointer`, `vtkMRMLSequenceBrowserNode::IndexDisplayFormatModifiedEvent`, `vtkMRMLSequenceBrowserNode::SafeDownCast`

## widget: label_IndexName

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Index name | label_IndexName | QLabel
- Text: Index name
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:139: d->label_IndexName->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:145: d->label_IndexName->setText(sequenceNode->GetIndexName().c_str());`
- API footprints: `GetIndexName`

## widget: slider_IndexValue

- Confidence: `linked_to_api`
- Widget/action class: `QSlider`
- Search text: slider_IndexValue | QSlider
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:60: QObject::connect(this->slider_IndexValue, SIGNAL(valueChanged(int)), q, SLOT(setSelectedItemNumber(int)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:149: bool sliderBlockSignals = d->slider_IndexValue->blockSignals(true);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:153: d->slider_IndexValue->setEnabled(true);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:154: d->slider_IndexValue->setMinimum(0);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:155: d->slider_IndexValue->setMaximum(numberOfDataNodes - 1);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:159: d->slider_IndexValue->setEnabled(false);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:161: d->slider_IndexValue->blockSignals(sliderBlockSignals);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:192: d->slider_IndexValue->setValue(selectedItemNumber);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:199: d->slider_IndexValue->setValue(0);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:207: return d->slider_IndexValue;`
- Connected slots/functions: `setSelectedItemNumber`
- API footprints: `GetMasterSequenceNode`, `GetNumberOfDataNodes`, `GetRecordingActive`, `GetSelectedItemNumber`, `SetSelectedItemNumber`

## widget: label_IndexValue

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: - | label_IndexValue | QLabel
- Text: -
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:59: this->label_IndexValue->setFont(QFontDatabase::systemFont(QFontDatabase::FixedFont));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:127: QFontMetrics fontMetrics = QFontMetrics(d->label_IndexValue->font());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:128: d->label_IndexValue->setFixedWidth(fontMetrics.horizontalAdvance(d->label_IndexValue->text()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:141: d->label_IndexValue->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:186: QFontMetrics fontMetrics = QFontMetrics(d->label_IndexValue->font());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:188: d->label_IndexValue->setText(indexValue);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:191: d->label_IndexValue->setFixedWidth(std::max(fontMetrics.horizontalAdvance(indexValue), d->label_IndexValue->width()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:196: d->label_IndexValue->setFixedWidth(0);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:197: d->label_IndexValue->setText("");`

## widget: label_IndexUnit

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: - | label_IndexUnit | QLabel
- Text: -
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:140: d->label_IndexUnit->setText("");`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:189: d->label_IndexUnit->setText(indexUnit);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:198: d->label_IndexUnit->setText("");`
