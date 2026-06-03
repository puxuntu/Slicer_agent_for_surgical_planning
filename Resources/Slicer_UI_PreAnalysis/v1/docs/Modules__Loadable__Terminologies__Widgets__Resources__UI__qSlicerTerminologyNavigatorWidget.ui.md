# Slicer UI Analysis: Modules/Loadable/Terminologies/Widgets/Resources/UI/qSlicerTerminologyNavigatorWidget.ui

- Owner class: `qSlicerTerminologyNavigatorWidget`
- UI file: `Modules/Loadable/Terminologies/Widgets/Resources/UI/qSlicerTerminologyNavigatorWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTerminologyNavigatorWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qSlicerTerminologyNavigatorWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:24: #include "qSlicerTerminologyNavigatorWidget.h"`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:28: #include "ui_qSlicerTerminologyNavigatorWidget.h"`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:64: qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle::TerminologyInfoBundle()`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:70: qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle::TerminologyInfoBundle(vtkSlicerTerminologyEntry* entry,`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:90: qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle::~TerminologyInfoBundle()`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:100: const qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle& qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle::operator=(`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:101: const qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle& other)`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:113: vtkSlicerTerminologyEntry* qSlicerTerminologyNavigatorWidget::TerminologyInfoBundle::GetTerminologyEntry()`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:119: // qSlicerTerminologyNavigatorWidgetPrivate methods`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:122: class qSlicerTerminologyNavigatorWidgetPrivate : public Ui_qSlicerTerminologyNavigatorWidget`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:124: Q_DECLARE_PUBLIC(qSlicerTerminologyNavigatorWidget);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:127: qSlicerTerminologyNavigatorWidget* const q_ptr;`
- API footprints: `Copy`, `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetHasModifiers`, `GetShowAnatomy`, `GetTerminologyEntry`

## widget: frame_TerminologyEntry

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: frame_TerminologyEntry | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1001: this->frame_TerminologyEntry->setVisible(!terminologyIsColorTable);`

## widget: frame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: frame | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:281: this->frame_ColorTableView->setLayout(colorTableLayout);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1001: this->frame_TerminologyEntry->setVisible(!terminologyIsColorTable);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1002: this->frame_ColorTable->setVisible(terminologyIsColorTable);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1991: return d->frame_TerminologyOverride->isVisible();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1998: d->frame_TerminologyOverride->setVisible(visible);`

## widget: ComboBox_Terminology

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_Terminology | ctkComboBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:284: QObject::connect(this->ComboBox_Terminology, SIGNAL(currentIndexChanged(int)), q, SLOT(onTerminologySelectionChanged(int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:285: QObject::connect(this->ComboBox_Terminology_2, SIGNAL(currentIndexChanged(int)), q, SLOT(onTerminologySelectionChanged(int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:580: QSignalBlocker blocker(this->ComboBox_Terminology);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:581: QSignalBlocker blocker2(this->ComboBox_Terminology_2);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:582: this->ComboBox_Terminology->clear();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:583: this->ComboBox_Terminology_2->clear();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:600: this->ComboBox_Terminology->addItem(termIt->c_str());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:601: this->ComboBox_Terminology_2->addItem(termIt->c_str());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:614: this->ComboBox_Terminology->addItem(QString::fromUtf8(colorNode->GetName()), QString::fromStdString(colorNodeId));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:615: this->ComboBox_Terminology_2->addItem(QString::fromUtf8(colorNode->GetName()), QString::fromStdString(colorNodeId));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:914: terminologyIndex = this->ComboBox_Terminology->findText(terminologyName);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:918: terminologyIndex = this->ComboBox_Terminology->findData(colorNodeID);`
- Connected slots/functions: `onTerminologySelectionChanged`
- API footprints: `GetMRMLScene`, `GetName`

## widget: pushButton_LoadTerminology

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: pushButton_LoadTerminology | QPushButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:337: QObject::connect(this->pushButton_LoadTerminology, SIGNAL(clicked()), q, SLOT(onLoadTerminologyClicked()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:338: QObject::connect(this->pushButton_LoadTerminology_2, SIGNAL(clicked()), q, SLOT(onLoadTerminologyClicked()));`
- Connected slots/functions: `onLoadTerminologyClicked`
- API footprints: `LoadTerminologyFromFile`

## widget: frame_TerminologyOverride

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: frame_TerminologyOverride | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1991: return d->frame_TerminologyOverride->isVisible();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1998: d->frame_TerminologyOverride->setVisible(visible);`

## widget: label_Name

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Name: | label_Name | QLabel
- Text: Name:
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`

## widget: lineEdit_Name

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: lineEdit_Name | QLineEdit
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:299: QObject::connect(this->lineEdit_Name, SIGNAL(textChanged(QString)), q, SLOT(onNameChanged(QString)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:327: this->pushButton_ResetName->setMaximumHeight(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:328: this->pushButton_ResetName->setMaximumWidth(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:329: this->pushButton_ResetColor->setMaximumHeight(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:330: this->pushButton_ResetColor->setMaximumWidth(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:381: this->lineEdit_Name->blockSignals(true); // The callback function is to save the user's manual name entry`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:382: this->lineEdit_Name->setText(name);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:383: this->lineEdit_Name->blockSignals(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1517: terminologyInfo.Name = d->lineEdit_Name->text();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1544: d->lineEdit_Name->blockSignals(true); // Only call callback function if user changes from UI`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1545: d->lineEdit_Name->setText(terminologyInfo.Name);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1546: d->lineEdit_Name->blockSignals(false);`
- Connected slots/functions: `onNameChanged`
- API footprints: `GetColorName`, `GetTerminologyEntry`

## widget: pushButton_ResetName

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: pushButton_ResetName | QPushButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:300: QObject::connect(this->pushButton_ResetName, SIGNAL(clicked()), q, SLOT(onResetNameClicked()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:327: this->pushButton_ResetName->setMaximumHeight(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:328: this->pushButton_ResetName->setMaximumWidth(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:379: this->pushButton_ResetName->setEnabled(!this->NameAutoGenerated);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1549: d->pushButton_ResetName->setEnabled(!d->NameAutoGenerated && !noneType);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2178: d->pushButton_ResetName->setEnabled(!d->NameAutoGenerated);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2274: d->pushButton_ResetName->setEnabled(!d->NameAutoGenerated);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2375: d->pushButton_ResetName->setEnabled(true);`
- Connected slots/functions: `onResetNameClicked`
- API footprints: `GetColor`, `GetColorName`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Color: | label | QLabel
- Text: Color:
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:276: // sortFilterModel->setFilterKeyColumn(colorModel->labelColumn());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1866: // Assemble from selection if there is no label`
- API footprints: `GetSlicerLabel`, `GetTypeModifierObject`

## widget: ColorPickerButton_RecommendedRGB

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: ColorPickerButton_RecommendedRGB | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:301: QObject::connect(this->ColorPickerButton_RecommendedRGB, SIGNAL(colorChanged(QColor)), q, SLOT(onColorChanged(QColor)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:334: this->ColorPickerButton_RecommendedRGB->setDialogOptions(options);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:435: this->ColorPickerButton_RecommendedRGB->blockSignals(true); // The callback function is to save the user's custom color selection`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:436: this->ColorPickerButton_RecommendedRGB->setColor(`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:438: this->ColorPickerButton_RecommendedRGB->blockSignals(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:448: this->ColorPickerButton_RecommendedRGB->blockSignals(true); // The callback function is to save the user's custom color selection`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:449: this->ColorPickerButton_RecommendedRGB->setColor(color);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:450: this->ColorPickerButton_RecommendedRGB->blockSignals(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1519: terminologyInfo.Color = d->ColorPickerButton_RecommendedRGB->color();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1566: d->ColorPickerButton_RecommendedRGB->blockSignals(true); // Only call callback function if user changes from UI`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1567: d->ColorPickerButton_RecommendedRGB->setColor(terminologyInfo.Color);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1568: d->ColorPickerButton_RecommendedRGB->blockSignals(false);`
- Connected slots/functions: `onColorChanged`
- API footprints: `GetColor`

## widget: pushButton_ResetColor

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: pushButton_ResetColor | QPushButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:302: QObject::connect(this->pushButton_ResetColor, SIGNAL(clicked()), q, SLOT(onResetColorClicked()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:329: this->pushButton_ResetColor->setMaximumHeight(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:330: this->pushButton_ResetColor->setMaximumWidth(this->lineEdit_Name->sizeHint().height());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:446: this->pushButton_ResetColor->setEnabled(!this->ColorAutoGenerated);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1574: d->pushButton_ResetColor->setEnabled(enableResetColor && !noneType);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2185: d->pushButton_ResetColor->setEnabled(!d->ColorAutoGenerated);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2279: d->pushButton_ResetColor->setEnabled(!d->ColorAutoGenerated);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2395: d->pushButton_ResetColor->setEnabled(true);`
- Connected slots/functions: `onResetColorClicked`

## widget: frame_Category

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame_Category | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`

## widget: SearchBox_Category

- Confidence: `linked_to_api`
- Widget/action class: `ctkSearchBox`
- Search text: SearchBox_Category | ctkSearchBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:291: QObject::connect(this->SearchBox_Category, SIGNAL(textChanged(QString)), q, SLOT(onCategorySearchTextChanged(QString)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:309: this->SearchBox_Category->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:643: logic->FindCategoriesInTerminology(this->CurrentTerminologyName.toUtf8().constData(), categories, this->SearchBox_Category->text().toUtf8().constData());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:996: this->SearchBox_Category->setEnabled(true);`
- Connected slots/functions: `onCategorySearchTextChanged`
- API footprints: `FindCategoriesInTerminology`

## widget: tableWidget_Category

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: tableWidget_Category | QTableWidget
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:286: QObject::connect(this->tableWidget_Category, SIGNAL(itemSelectionChanged()), q, SLOT(onCategorySelectionChanged()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:308: this->tableWidget_Category->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:513: QList<QTableWidgetItem*> items = this->tableWidget_Category->findItems(categoryName, flags);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:626: this->tableWidget_Category->clearContents();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:630: this->tableWidget_Category->setRowCount(0);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:646: this->tableWidget_Category->setRowCount(categories.size());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:656: this->tableWidget_Category->setItem(index, 0, addedCategoryItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:670: this->tableWidget_Category->setCurrentItem(selectedItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:675: this->tableWidget_Category->selectAll();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:986: if (this->tableWidget_Category->rowCount() == 0)`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:988: this->tableWidget_Category->setEnabled(!this->SearchBox_Type->text().isEmpty()); // Might be empty because of a search`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:995: this->tableWidget_Category->setEnabled(true);`
- Connected slots/functions: `onCategorySelectionChanged`
- API footprints: `GetCategoryInTerminology`, `GetCodeMeaning`, `GetCodingSchemeDesignator`, `GetShowAnatomy`, `Initialize`

## widget: pushButton_SelectAllCategories

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Select all | pushButton_SelectAllCategories | QPushButton
- Text: Select all
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:287: QObject::connect(this->pushButton_SelectAllCategories, SIGNAL(clicked()), q, SLOT(onSelectAllCategoriesButtonClicked()));`
- Connected slots/functions: `onSelectAllCategoriesButtonClicked`

## widget: ComboBox_TypeModifier

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_TypeModifier | ctkComboBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:290: QObject::connect(this->ComboBox_TypeModifier, SIGNAL(currentIndexChanged(int)), q, SLOT(onTypeModifierSelectionChanged(int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:312: this->ComboBox_TypeModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:836: this->ComboBox_TypeModifier->clear();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:840: this->ComboBox_TypeModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:846: this->ComboBox_TypeModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:860: this->ComboBox_TypeModifier->addItem(qSlicerTerminologyNavigatorWidget::tr("No type modifier"));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:879: this->ComboBox_TypeModifier->addItem(addedTypeModifierName, QVariant(userData));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:890: this->ComboBox_TypeModifier->setCurrentIndex(selectedIndex);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:991: this->ComboBox_TypeModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1054: this->ComboBox_TypeModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1115: this->ComboBox_TypeModifier->setEnabled(this->ComboBox_TypeModifier->count());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1147: int modifierIndex = this->findComboBoxIndexForModifier(this->ComboBox_TypeModifier, modifier);`
- Connected slots/functions: `onTypeModifierSelectionChanged`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetHasModifiers`, `GetTypeModifierInTerminologyType`, `Initialize`

## widget: tableWidget_Type

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: tableWidget_Type | QTableWidget
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:288: QObject::connect(this->tableWidget_Type, SIGNAL(currentItemChanged(QTableWidgetItem*, QTableWidgetItem*)), q, SLOT(onTypeSelected(QTableWidgetItem*, QTableWidgetItem*)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:289: QObject::connect(this->tableWidget_Type, SIGNAL(cellDoubleClicked(int, int)), q, SLOT(onTypeCellDoubleClicked(int, int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:310: this->tableWidget_Type->setEnabled(true); // None item always present`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:684: this->tableWidget_Type->clearContents();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:701: this->tableWidget_Type->setRowCount(1);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:703: this->tableWidget_Type->setItem(0, 0, noneItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:704: this->tableWidget_Type->setCurrentItem(noneItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:770: this->tableWidget_Type->setRowCount(types.size() + noneTypeExists);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:771: this->tableWidget_Type->setItem(0, 0, noneItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:775: this->tableWidget_Type->setRowCount(types.size());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:803: this->tableWidget_Type->setItem(typeIndex + noneTypeExists, 0, addedTypeItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:817: this->tableWidget_Type->setCurrentItem(selectedItem);`
- Connected slots/functions: `onTypeCellDoubleClicked`, `onTypeSelected`
- API footprints: `Copy`, `GetCategoryInTerminology`, `GetCodingSchemeDesignator`, `GetShowAnatomy`, `GetTypeInTerminologyCategory`, `Initialize`

## widget: frame_Region

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame_Region | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`

## widget: ComboBox_RegionContext

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_RegionContext | ctkComboBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:294: QObject::connect(this->ComboBox_RegionContext, SIGNAL(currentIndexChanged(int)), q, SLOT(onRegionContextSelectionChanged(int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1063: this->ComboBox_RegionContext->setEnabled(this->CurrentCategoryObject->GetShowAnatomy());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1211: this->ComboBox_RegionContext->clear();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1224: this->ComboBox_RegionContext->addItem(anIt->c_str());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1413: this->ComboBox_RegionContext->setEnabled(this->CurrentCategoryObject->GetShowAnatomy());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1791: int regionContextIndex = d->ComboBox_RegionContext->findText(regionContextName);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1797: if (regionContextIndex != d->ComboBox_RegionContext->currentIndex())`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1799: d->setCurrentRegionContext(d->ComboBox_RegionContext->itemText(regionContextIndex));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1801: d->ComboBox_RegionContext->blockSignals(true);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1802: d->ComboBox_RegionContext->setCurrentIndex(regionContextIndex);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1803: d->ComboBox_RegionContext->blockSignals(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1828: int lastRegionContextIndex = d->ComboBox_RegionContext->findText(lastRegionContextName);`
- Connected slots/functions: `onRegionContextSelectionChanged`
- API footprints: `GetShowAnatomy`

## widget: pushButton_LoadRegionContext

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: pushButton_LoadRegionContext | QPushButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:339: QObject::connect(this->pushButton_LoadRegionContext, SIGNAL(clicked()), q, SLOT(onLoadRegionContextClicked()));`
- Connected slots/functions: `onLoadRegionContextClicked`
- API footprints: `LoadRegionContextFromFile`

## widget: SearchBox_Region

- Confidence: `linked_to_api`
- Widget/action class: `ctkSearchBox`
- Search text: SearchBox_Region | ctkSearchBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:297: QObject::connect(this->SearchBox_Region, SIGNAL(textChanged(QString)), q, SLOT(onRegionSearchTextChanged(QString)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:314: this->SearchBox_Region->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1065: this->SearchBox_Region->setEnabled(this->CurrentCategoryObject->GetShowAnatomy());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1251: logic->FindRegionsInRegionContext(this->CurrentRegionContextName.toUtf8().constData(), regions, this->SearchBox_Region->text().toUtf8().constData());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1372: if (this->SearchBox_Region->text().isEmpty())`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1375: this->SearchBox_Region->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1382: this->SearchBox_Region->setEnabled(true);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1415: this->SearchBox_Region->setEnabled(this->CurrentCategoryObject->GetShowAnatomy());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2086: d->SearchBox_Region->setEnabled(showAnatomyOnInAnyCategories);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2170: d->SearchBox_Region->setEnabled(d->CurrentCategoryObject->GetShowAnatomy());`
- Connected slots/functions: `onRegionSearchTextChanged`
- API footprints: `FindRegionsInRegionContext`, `GetShowAnatomy`

## widget: tableWidget_Region

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: tableWidget_Region | QTableWidget
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:295: QObject::connect(this->tableWidget_Region, SIGNAL(currentItemChanged(QTableWidgetItem*, QTableWidgetItem*)), q, SLOT(onRegionSelected(QTableWidgetItem*, QTableWidgetItem*)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:315: this->tableWidget_Region->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1032: this->tableWidget_Region->setCurrentItem(nullptr);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1064: this->tableWidget_Region->setEnabled(this->CurrentCategoryObject->GetShowAnatomy());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1234: this->tableWidget_Region->clearContents();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1238: this->tableWidget_Region->setRowCount(0);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1253: this->tableWidget_Region->setRowCount(regions.size() + 1); // +1 for the "None" item`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1259: this->tableWidget_Region->setItem(index++, 0, noneRegionItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1270: this->tableWidget_Region->setItem(index, 0, addedRegionItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1284: this->tableWidget_Region->setCurrentItem(selectedItem);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1369: if (this->tableWidget_Region->rowCount() == 0)`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1371: this->tableWidget_Region->setEnabled(false);`
- Connected slots/functions: `onRegionSelected`
- API footprints: `FindRegionsInRegionContext`, `GetCodingSchemeDesignator`, `GetRegionInRegionContext`, `GetShowAnatomy`, `Initialize`

## widget: ComboBox_RegionModifier

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_RegionModifier | ctkComboBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:296: QObject::connect(this->ComboBox_RegionModifier, SIGNAL(currentIndexChanged(int)), q, SLOT(onRegionModifierSelectionChanged(int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:316: this->ComboBox_RegionModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1066: this->ComboBox_RegionModifier->setEnabled(false); // Disabled until valid region selection`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1293: this->ComboBox_RegionModifier->clear();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1297: this->ComboBox_RegionModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1303: this->ComboBox_RegionModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1320: this->ComboBox_RegionModifier->addItem(qSlicerTerminologyNavigatorWidget::tr("No region modifier"));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1333: this->ComboBox_RegionModifier->addItem(addedRegionModifierName, QVariant(userData));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1344: this->ComboBox_RegionModifier->setCurrentIndex(selectedIndex);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1377: this->ComboBox_RegionModifier->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1416: this->ComboBox_RegionModifier->setEnabled(false); // Disabled until valid region selection`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1432: this->ComboBox_RegionModifier->setEnabled(this->ComboBox_RegionModifier->count());`
- Connected slots/functions: `onRegionModifierSelectionChanged`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetHasModifiers`, `GetRegionModifierInRegion`, `GetShowAnatomy`

## widget: SearchBox_Type

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSearchBox`
- Search text: SearchBox_Type | ctkSearchBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:292: QObject::connect(this->SearchBox_Type, SIGNAL(textChanged(QString)), q, SLOT(onTypeSearchTextChanged(QString)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:311: this->SearchBox_Type->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:723: std::string searchTerm(this->SearchBox_Type->text().toUtf8().constData());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:988: this->tableWidget_Category->setEnabled(!this->SearchBox_Type->text().isEmpty()); // Might be empty because of a search`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:990: this->SearchBox_Type->setEnabled(false);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1059: this->SearchBox_Type->setEnabled(true);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2080: d->SearchBox_Type->setEnabled(true);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2620: d->SearchBox_Type->setFocus();`
- Connected slots/functions: `onTypeSearchTextChanged`

## widget: RegionExpandButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkExpandButton`
- Search text: RegionExpandButton | ctkExpandButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:323: this->RegionExpandButton->setChecked(settings->value("Terminology/ShowRegionSelector", false).toBool());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1070: this->RegionExpandButton->setEnabled(true);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1075: this->RegionExpandButton->setEnabled(this->CurrentCategoryObject->GetShowAnatomy());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1079: this->RegionExpandButton->setDown(true);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1080: QTimer::singleShot(50, q, SLOT(onRegionExpandButtonUp()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1081: QTimer::singleShot(100, q, SLOT(onRegionExpandButtonDown()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1082: QTimer::singleShot(150, q, SLOT(onRegionExpandButtonUp()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1083: QTimer::singleShot(200, q, SLOT(onRegionExpandButtonDown()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1084: QTimer::singleShot(250, q, SLOT(onRegionExpandButtonUp()));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1508: settings->setValue("Terminology/ShowRegionSelector", d->RegionExpandButton->isChecked());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1976: return d->RegionExpandButton->isChecked();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1984: d->RegionExpandButton->setChecked(visible);`
- Connected slots/functions: `onRegionExpandButtonDown`, `onRegionExpandButtonUp`
- API footprints: `GetShowAnatomy`
- Key UI properties: {"checked": "true"}

## widget: CategoryExpandButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkExpandButton`
- Search text: CategoryExpandButton | ctkExpandButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:322: this->CategoryExpandButton->setChecked(settings->value("Terminology/ShowCategorySelector", false).toBool());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1507: settings->setValue("Terminology/ShowCategorySelector", d->CategoryExpandButton->isChecked());`
- Key UI properties: {"checked": "true"}

## widget: frame_ColorTable

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: frame_ColorTable | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:281: this->frame_ColorTableView->setLayout(colorTableLayout);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:1002: this->frame_ColorTable->setVisible(terminologyIsColorTable);`

## widget: pushButton_LoadTerminology_2

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: pushButton_LoadTerminology_2 | QPushButton
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:338: QObject::connect(this->pushButton_LoadTerminology_2, SIGNAL(clicked()), q, SLOT(onLoadTerminologyClicked()));`
- Connected slots/functions: `onLoadTerminologyClicked`
- API footprints: `LoadTerminologyFromFile`

## widget: ComboBox_Terminology_2

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: ComboBox_Terminology_2 | ctkComboBox
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:285: QObject::connect(this->ComboBox_Terminology_2, SIGNAL(currentIndexChanged(int)), q, SLOT(onTerminologySelectionChanged(int)));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:581: QSignalBlocker blocker2(this->ComboBox_Terminology_2);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:583: this->ComboBox_Terminology_2->clear();`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:601: this->ComboBox_Terminology_2->addItem(termIt->c_str());`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:615: this->ComboBox_Terminology_2->addItem(QString::fromUtf8(colorNode->GetName()), QString::fromStdString(colorNodeId));`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:922: QSignalBlocker blocker2(this->ComboBox_Terminology_2);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:924: this->ComboBox_Terminology_2->setCurrentIndex(terminologyIndex);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2007: ctkComboBox* visibleComboBox = (d->ComboBox_Terminology->isVisible() ? d->ComboBox_Terminology : d->ComboBox_Terminology_2);`
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:2008: ctkComboBox* invisibleComboBox = (!d->ComboBox_Terminology->isVisible() ? d->ComboBox_Terminology : d->ComboBox_Terminology_2);`
- Connected slots/functions: `onTerminologySelectionChanged`
- API footprints: `GetMRMLScene`, `GetName`

## widget: frame_ColorTableView

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: frame_ColorTableView | QFrame
- Implementation candidates: `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx`, `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/Widgets/qSlicerTerminologyNavigatorWidget.cxx:281: this->frame_ColorTableView->setLayout(colorTableLayout);`
