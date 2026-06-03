# Slicer UI Analysis: Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationConversionParametersWidget.ui

- Owner class: `qMRMLSegmentationConversionParametersWidget`
- UI file: `Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationConversionParametersWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentationConversionParametersWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLSegmentationConversionParametersWidget | QWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:24: #include "qMRMLSegmentationConversionParametersWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:25: #include "ui_qMRMLSegmentationConversionParametersWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:49: class qMRMLSegmentationConversionParametersWidgetPrivate : public Ui_qMRMLSegmentationConversionParametersWidget`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:51: Q_DECLARE_PUBLIC(qMRMLSegmentationConversionParametersWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:54: qMRMLSegmentationConversionParametersWidget* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:57: qMRMLSegmentationConversionParametersWidgetPrivate(qMRMLSegmentationConversionParametersWidget& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:84: qMRMLSegmentationConversionParametersWidgetPrivate::qMRMLSegmentationConversionParametersWidgetPrivate(qMRMLSegmentationConversionParametersWidget& object)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:91: void qMRMLSegmentationConversionParametersWidgetPrivate::init()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:93: Q_Q(qMRMLSegmentationConversionParametersWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:106: this->PathsColumnLabels << qMRMLSegmentationConversionParametersWidget::tr("Cost") << qMRMLSegmentationConversionParametersWidget::tr("Path");`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:111: this->ParametersColumnLabels << qMRMLSegmentationConversionParametersWidget::tr("Name") << qMRMLSegmentationConversionParametersWidget::tr("Value");`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:117: int qMRMLSegmentationConversionParametersWidgetPrivate::pathsColumnIndex(QString label)`
- API footprints: `GetNumberOfPaths`, `RemoveAllParameters`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: label_Converting

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Converting | label_Converting | QLabel
- Text: Converting
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`

## widget: label_RepresentationName

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Closed surface model | label_RepresentationName | QLabel
- Text: Closed surface model
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:182: d->label_RepresentationName->setText(representationName);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:186: d->label_RepresentationName->setText(tr("Invalid representation"));`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: in | label | QLabel
- Text: in
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:61: int pathsColumnIndex(QString label);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:64: int parametersColumnIndex(QString label);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:117: int qMRMLSegmentationConversionParametersWidgetPrivate::pathsColumnIndex(QString label)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:119: return this->PathsColumnLabels.indexOf(label);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:123: int qMRMLSegmentationConversionParametersWidgetPrivate::parametersColumnIndex(QString label)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:125: return this->ParametersColumnLabels.indexOf(label);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:154: d->label_SegmentationName->setText(QString(segmentationNode->GetName()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:158: d->label_SegmentationName->setText(tr("Invalid segmentation"));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:182: d->label_RepresentationName->setText(representationName);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:186: d->label_RepresentationName->setText(tr("Invalid representation"));`
- API footprints: `GetName`

## widget: label_SegmentationName

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Segmentation | label_SegmentationName | QLabel
- Text: Segmentation
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:154: d->label_SegmentationName->setText(QString(segmentationNode->GetName()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:158: d->label_SegmentationName->setText(tr("Invalid segmentation"));`
- API footprints: `GetName`

## widget: CollapsibleGroupBox_Paths

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_Paths | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`

## widget: PathsTable

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: PathsTable | QTableWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:97: QObject::connect(this->PathsTable, SIGNAL(itemSelectionChanged()), q, SLOT(populateParametersTable()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:102: this->PathsTable->horizontalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:103: this->PathsTable->horizontalHeader()->setStretchLastSection(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:104: this->PathsTable->setSelectionMode(QAbstractItemView::SingleSelection);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:105: this->PathsTable->setSelectionBehavior(QAbstractItemView::SelectRows);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:107: this->PathsTable->setColumnCount(this->PathsColumnLabels.size());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:138: this->populatePathsTable();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:161: this->populatePathsTable();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:189: this->populatePathsTable();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:202: void qMRMLSegmentationConversionParametersWidget::populatePathsTable()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:207: d->PathsTable->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:209: d->PathsTable->clearContents();`
- Connected slots/functions: `populateParametersTable`
- API footprints: `GetConversionParametersForPath`, `GetDescription`, `GetName`, `GetNumberOfParameters`, `GetNumberOfPaths`, `GetSegmentation`, `GetValue`, `RemoveAllItems`

## widget: CollapsibleGroupBox_Parameters

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox_Parameters | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`

## widget: ParametersTable

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: ParametersTable | QTableWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:97: QObject::connect(this->PathsTable, SIGNAL(itemSelectionChanged()), q, SLOT(populateParametersTable()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:98: QObject::connect(this->ParametersTable, SIGNAL(itemChanged(QTableWidgetItem*)), q, SLOT(onParameterChanged(QTableWidgetItem*)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:109: this->ParametersTable->horizontalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:110: this->ParametersTable->horizontalHeader()->setStretchLastSection(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:112: this->ParametersTable->setColumnCount(this->ParametersColumnLabels.size());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:113: this->ParametersTable->setSelectionMode(QAbstractItemView::NoSelection);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:139: this->populateParametersTable();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:162: this->populateParametersTable();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:190: this->populateParametersTable();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:279: void qMRMLSegmentationConversionParametersWidget::populateParametersTable()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:284: d->ParametersTable->blockSignals(true);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:286: d->ParametersTable->clearContents();`
- Connected slots/functions: `onParameterChanged`, `populateParametersTable`
- API footprints: `GetConversionParametersForPath`, `GetDescription`, `GetName`, `GetNumberOfParameters`, `GetSegmentation`, `GetValue`, `SetConversionParameter`

## widget: pushButton_Convert

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Convert | pushButton_Convert | QPushButton
- Text: Convert
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationConversionParametersWidget.cxx:99: QObject::connect(this->pushButton_Convert, SIGNAL(clicked()), q, SLOT(applyConversion()));`
- Connected slots/functions: `applyConversion`
- API footprints: `CreateRepresentation`, `GetName`, `GetSegmentation`
