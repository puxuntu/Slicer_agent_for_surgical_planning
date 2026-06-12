# Slicer UI Analysis: Modules/Scripted/DICOMLib/Widgets/Resources/UI/qSlicerDICOMExportDialog.ui

- Owner class: `qSlicerDICOMExportDialog`
- UI file: `Modules/Scripted/DICOMLib/Widgets/Resources/UI/qSlicerDICOMExportDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerDICOMExportDialog

- Confidence: `linked_to_api`
- Widget/action class: `QDialog`
- Search text: qSlicerDICOMExportDialog | QDialog
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:24: #include "qSlicerDICOMExportDialog.h"`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:25: #include "ui_qSlicerDICOMExportDialog.h"`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:74: class qSlicerDICOMExportDialogPrivate`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:76: , public Ui_qSlicerDICOMExportDialog`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:78: Q_DECLARE_PUBLIC(qSlicerDICOMExportDialog);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:81: qSlicerDICOMExportDialog* const q_ptr;`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:84: qSlicerDICOMExportDialogPrivate(qSlicerDICOMExportDialog& object);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:85: ~qSlicerDICOMExportDialogPrivate() override;`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:97: qSlicerDICOMExportDialogPrivate::qSlicerDICOMExportDialogPrivate(qSlicerDICOMExportDialog& object)`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:106: qSlicerDICOMExportDialogPrivate::~qSlicerDICOMExportDialogPrivate() = default;`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:109: void qSlicerDICOMExportDialogPrivate::init()`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:111: Q_Q(qSlicerDICOMExportDialog);`
- API footprints: `vtkMRMLSubjectHierarchyNode::INVALID_ITEM_ID`

## widget: frame

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame | QFrame
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`

## widget: groupBox_1SelectNode

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_1SelectNode | QGroupBox
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`

## widget: SubjectHierarchyTreeView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: SubjectHierarchyTreeView | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:30: #include "qMRMLSubjectHierarchyTreeView.h"`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:114: qMRMLSubjectHierarchyModel* sceneModel = (qMRMLSubjectHierarchyModel*)this->SubjectHierarchyTreeView->model();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:115: this->SubjectHierarchyTreeView->setMRMLScene(this->Scene);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:116: this->SubjectHierarchyTreeView->expandToDepth(4);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:117: this->SubjectHierarchyTreeView->setEditTriggers(QAbstractItemView::DoubleClicked | QAbstractItemView::EditKeyPressed);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:118: this->SubjectHierarchyTreeView->hideColumn(sceneModel->idColumn());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:119: this->SubjectHierarchyTreeView->hideColumn(sceneModel->visibilityColumn());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:120: this->SubjectHierarchyTreeView->hideColumn(sceneModel->transformColumn());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:126: connect(this->SubjectHierarchyTreeView, SIGNAL(currentItemChanged(vtkIdType)), q, SLOT(onCurrentItemChanged(vtkIdType)));`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:186: d->SubjectHierarchyTreeView->setCurrentItem(d->ItemToSelect);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:217: vtkIdType currentItemID = d->SubjectHierarchyTreeView->currentItem();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:223: vtkMRMLSubjectHierarchyNode* shNode = d->SubjectHierarchyTreeView->subjectHierarchyNode();`
- Connected slots/functions: `onCurrentItemChanged`
- API footprints: `vtkMRMLSubjectHierarchyNode::INVALID_ITEM_ID`

## widget: groupBox_2SelectExportType

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_2SelectExportType | QGroupBox
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`

## widget: ExportablesListWidget

- Confidence: `linked_to_slot`
- Widget/action class: `QListWidget`
- Search text: ExportablesListWidget | QListWidget
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:127: connect(this->ExportablesListWidget, SIGNAL(currentRowChanged(int)), q, SLOT(onExportableSelectedAtRow(int)));`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:231: d->ExportablesListWidget->clear();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:324: QListWidgetItem* exportableItem = new QListWidgetItem(itemText, d->ExportablesListWidget);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:337: d->ExportablesListWidget->setCurrentRow(0);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:349: QListWidgetItem* exportableItem = d->ExportablesListWidget->item(row);`
- Connected slots/functions: `onExportableSelectedAtRow`

## widget: groupBox_3EditDICOMTags

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox_3EditDICOMTags | QGroupBox
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`

## widget: DICOMTagEditorWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerDICOMTagEditorWidget`
- Search text: DICOMTagEditorWidget | qSlicerDICOMTagEditorWidget
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:128: connect(this->DICOMTagEditorWidget, SIGNAL(tagEdited()), q, SLOT(onTagEdited()));`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:232: d->DICOMTagEditorWidget->clear();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:372: d->DICOMTagEditorWidget->setMRMLScene(d->Scene);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:373: QString error = d->DICOMTagEditorWidget->setExportables(exportableList);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:388: d->DICOMTagEditorWidget->commitChangesToItems();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:491: d->DICOMTagEditorWidget->commitChangesToItems();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:529: d->DICOMTagEditorWidget->commitChangesToItems();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:532: if (d->DICOMTagEditorWidget->exportables().isEmpty())`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:542: for (qSlicerDICOMExportable* const exportable : d->DICOMTagEditorWidget->exportables())`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:563: .arg(qSlicerCorePythonManager::toPythonStringLiteral(d->DICOMTagEditorWidget->exportables()[0]->pluginClass())));`
- Connected slots/functions: `onTagEdited`

## widget: SaveTagsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Save modified tags | If checked, the manually edited tags will be saved into the scene, preserved for the next export. If unchecked, temporary changes can be made, only for this export operation. | SaveTagsCheckBox | QCheckBox
- Text: Save modified tags
- Tooltip: If checked, the manually edited tags will be saved into the scene, preserved for the next export. If unchecked, temporary changes can be made, only for this export operation.
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:130: connect(this->SaveTagsCheckBox, SIGNAL(toggled(bool)), q, SLOT(onSaveTagsCheckBoxToggled(bool)));`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:386: if (d->SaveTagsCheckBox->isChecked())`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:484: void qSlicerDICOMExportDialog::onSaveTagsCheckBoxToggled(bool on)`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:527: if (d->SaveTagsCheckBox->isChecked())`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h:85: void onSaveTagsCheckBoxToggled(bool);`
- Connected slots/functions: `onSaveTagsCheckBoxToggled`
- Key UI properties: {"checked": "true"}

## widget: ExportFrame

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: ExportFrame | QFrame
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`

## widget: ExportToFolderCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Export to folder: | If checked, the exported DICOM files will be written into the specified folder.
If unchecked, the exported dataset will be added to the DICOM database. | ExportToFolderCheckBox | QCheckBox
- Text: Export to folder:
- Tooltip: If checked, the exported DICOM files will be written into the specified folder.
If unchecked, the exported dataset will be added to the DICOM database.
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:131: connect(this->ExportToFolderCheckBox, SIGNAL(toggled(bool)), q, SLOT(onExportToFolderCheckBoxToggled(bool)));`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:194: d->ExportToFolderCheckBox->setChecked(exportToFolder);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:399: if (d->ExportToFolderCheckBox->isChecked())`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:411: bool exportToDatabase = !d->ExportToFolderCheckBox->isChecked();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:496: void qSlicerDICOMExportDialog::onExportToFolderCheckBoxToggled(bool on)`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h:88: void onExportToFolderCheckBoxToggled(bool);`
- Connected slots/functions: `onExportToFolderCheckBoxToggled`, `setEnabled`
- Declared UI connections: `toggled(bool) -> PathLineEdit_OutputFolder.setEnabled(bool)`

## widget: PathLineEdit_OutputFolder

- Confidence: `linked_to_code`
- Widget/action class: `ctkPathLineEdit`
- Search text: Exported DICOM files into this folder instead of the application's DICOM database. | PathLineEdit_OutputFolder | ctkPathLineEdit
- Tooltip: Exported DICOM files into this folder instead of the application's DICOM database.
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:401: d->PathLineEdit_OutputFolder->addCurrentPathToHistory();`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:408: QDir outputFolder(d->PathLineEdit_OutputFolder->currentPath());`

## widget: ErrorLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Error messages | ErrorLabel | QLabel
- Text: Error messages
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:123: this->ErrorLabel->setText(QString());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:205: d->ErrorLabel->setText(QString());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:346: d->ErrorLabel->setText(QString());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:365: d->ErrorLabel->setText(errorMessage);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:376: d->ErrorLabel->setText(error);`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:405: d->ErrorLabel->setText(QString());`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:439: d->ErrorLabel->setText("No DICOM database is set, so the data (that was successfully exported) cannot be imported back");`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:571: d->ErrorLabel->setText("Error occurred in exporter");`
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:577: d->ErrorLabel->setText(errorMessage);`

## widget: ExportButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Export | ExportButton | QPushButton
- Text: Export
- Implementation candidates: `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx`, `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.h`
- Matched implementation lines:
  - `Modules/Scripted/DICOMLib/Widgets/qSlicerDICOMExportDialog.cxx:129: connect(this->ExportButton, SIGNAL(clicked()), q, SLOT(onExport()));`
- Connected slots/functions: `onExport`
