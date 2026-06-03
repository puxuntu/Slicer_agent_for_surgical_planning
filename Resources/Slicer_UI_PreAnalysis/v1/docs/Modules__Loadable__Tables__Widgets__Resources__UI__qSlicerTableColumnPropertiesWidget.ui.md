# Slicer UI Analysis: Modules/Loadable/Tables/Widgets/Resources/UI/qSlicerTableColumnPropertiesWidget.ui

- Owner class: `qSlicerTableColumnPropertiesWidget`
- UI file: `Modules/Loadable/Tables/Widgets/Resources/UI/qSlicerTableColumnPropertiesWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTableColumnPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerTableColumnPropertiesWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:22: #include "qSlicerTableColumnPropertiesWidget.h"`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:23: #include "ui_qSlicerTableColumnPropertiesWidget.h"`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:47: class qSlicerTableColumnPropertiesWidgetPrivate : public Ui_qSlicerTableColumnPropertiesWidget`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:49: Q_DECLARE_PUBLIC(qSlicerTableColumnPropertiesWidget);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:52: qSlicerTableColumnPropertiesWidget* const q_ptr;`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:55: qSlicerTableColumnPropertiesWidgetPrivate(qSlicerTableColumnPropertiesWidget& object);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:56: ~qSlicerTableColumnPropertiesWidgetPrivate();`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:57: virtual void setupUi(qSlicerTableColumnPropertiesWidget*);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:71: qSlicerTableColumnPropertiesWidgetPrivate::qSlicerTableColumnPropertiesWidgetPrivate(qSlicerTableColumnPropertiesWidget& object)`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:79: qSlicerTableColumnPropertiesWidgetPrivate::~qSlicerTableColumnPropertiesWidgetPrivate() = default;`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:82: void qSlicerTableColumnPropertiesWidgetPrivate::setupUi(qSlicerTableColumnPropertiesWidget* widget)`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:84: this->Ui_qSlicerTableColumnPropertiesWidget::setupUi(widget);`
- API footprints: `vtkMRMLTableNode::SafeDownCast`

## widget: NameLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Name: | NameLabel | QLabel
- Text: Name:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:218: d->NameLabel->setVisible(d->ColumnNameVisible);`

## widget: NameLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: NameLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:219: d->NameLineEdit->setVisible(d->ColumnNameVisible);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:233: d->NameLineEdit->setText(d->ColumnNames.join(", "));`

## widget: DataTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Data type: | DataTypeLabel | QLabel
- Text: Data type:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## widget: DataTypeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `QComboBox`
- Search text: DataTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:128: connect(d->DataTypeComboBox, SIGNAL(currentIndexChanged(const QString&)), this, SLOT(onDataTypeChanged(const QString&)));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:236: int columnTypeIndex = d->DataTypeComboBox->findText(columnType);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:237: d->DataTypeComboBox->setCurrentIndex(columnTypeIndex);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:353: this->setColumnProperty("type", d->DataTypeComboBox->currentText());`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:372: this->setColumnProperty("type", d->DataTypeComboBox->currentText());`
- Connected slots/functions: `onDataTypeChanged`

## widget: ApplyTypeChangeButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Convert | ApplyTypeChangeButton | QPushButton
- Text: Convert
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:111: d->ApplyTypeChangeButton->setVisible(false);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:133: connect(d->ApplyTypeChangeButton, SIGNAL(clicked()), this, SLOT(onApplyTypeChange()));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:348: d->ApplyTypeChangeButton->setVisible(true);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:373: d->ApplyTypeChangeButton->setVisible(false);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:382: d->ApplyTypeChangeButton->setVisible(false);`
- Connected slots/functions: `onApplyTypeChange`

## widget: CancelTypeChangeButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Cancel | CancelTypeChangeButton | QPushButton
- Text: Cancel
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:112: d->CancelTypeChangeButton->setVisible(false);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:134: connect(d->CancelTypeChangeButton, SIGNAL(clicked()), this, SLOT(onCancelTypeChange()));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:349: d->CancelTypeChangeButton->setVisible(true);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:374: d->CancelTypeChangeButton->setVisible(false);`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:383: d->CancelTypeChangeButton->setVisible(false);`
- Connected slots/functions: `onCancelTypeChange`

## widget: NullValueLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Null value: | NullValueLabel | QLabel
- Text: Null value:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## widget: NullValueLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: NullValueLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:114: d->NullValueLineEdit->setProperty(SCHEMA_PROPERTY_NAME, QString("nullValue"));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:121: d->PropertyEditWidgets << d->NullValueLineEdit;`

## widget: TitleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Title: | TitleLabel | QLabel
- Text: Title:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## widget: TitleLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: TitleLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:115: d->TitleLineEdit->setProperty(SCHEMA_PROPERTY_NAME, QString("title"));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:122: d->PropertyEditWidgets << d->TitleLineEdit;`

## widget: DescriptionLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Description: | DescriptionLabel | QLabel
- Text: Description:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## widget: DescriptionLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: DescriptionLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:116: d->DescriptionLineEdit->setProperty(SCHEMA_PROPERTY_NAME, QString("description"));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:123: d->PropertyEditWidgets << d->DescriptionLineEdit;`

## widget: UnitLabelLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Unit label: | UnitLabelLabel | QLabel
- Text: Unit label:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## widget: UnitLabelLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: UnitLabelLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:117: d->UnitLabelLineEdit->setProperty(SCHEMA_PROPERTY_NAME, QString("unitLabel"));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:124: d->PropertyEditWidgets << d->UnitLabelLineEdit;`

## widget: ComponentCountLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Component count: | ComponentCountLabel | QLabel
- Text: Component count:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:228: d->ComponentCountLabel->setVisible(componentRowsVisible);`

## widget: ComponentCountLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: ComponentCountLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:118: d->ComponentCountLineEdit->setProperty(SCHEMA_PROPERTY_NAME, QString("componentCount"));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:125: d->PropertyEditWidgets << d->ComponentCountLineEdit;`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:229: d->ComponentCountLineEdit->setVisible(componentRowsVisible);`

## widget: ComponentNamesLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: ComponentNamesLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:119: d->ComponentNamesLineEdit->setProperty(SCHEMA_PROPERTY_NAME, QString("componentNames"));`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:126: d->PropertyEditWidgets << d->ComponentNamesLineEdit;`
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:231: d->ComponentNamesLineEdit->setVisible(componentRowsVisible);`

## widget: ComponentNamesLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Component names: | ComponentNamesLabel | QLabel
- Text: Component names:
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx:230: d->ComponentNamesLabel->setVisible(componentRowsVisible);`

## action: ActionPersistent

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Place multiple control points | Place multiple control points | ActionPersistent
- Text: Place multiple control points
- Tooltip: Place multiple control points
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
- Key UI properties: {"checkable": "true"}

## action: ActionDeleteAll

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Delete all control points | Delete all control points in the list | ActionDeleteAll
- Text: Delete all control points
- Tooltip: Delete all control points in the list
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## action: ActionVisibility

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Visibility | Toggle control point visibility | ActionVisibility
- Text: Visibility
- Tooltip: Toggle control point visibility
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`

## action: ActionLocked

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Locked | Toggle control point positions lock | ActionLocked
- Text: Locked
- Tooltip: Toggle control point positions lock
- Implementation candidates: `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.cxx`, `Modules/Loadable/Tables/Widgets/qSlicerTableColumnPropertiesWidget.h`
