# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSaveDataDialog.ui

- Owner class: `qSlicerSaveDataDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSaveDataDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSaveDataDialog

- Confidence: `linked_to_api`
- Widget/action class: `QDialog`
- Search text: qSlicerSaveDataDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:41: #include "qSlicerSaveDataDialog_p.h"`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:97: object = qSlicerSaveDataDialogPrivate::getNodeByID(nodeID.toUtf8().data(), mrmlScene);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:109: qSlicerSaveDataDialogPrivate::qSlicerSaveDataDialogPrivate(QWidget* parentWidget)`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:171: qSlicerSaveDataDialogPrivate::~qSlicerSaveDataDialogPrivate() = default;`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:174: void qSlicerSaveDataDialogPrivate::setMRMLScene(vtkMRMLScene* scene)`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:186: vtkMRMLScene* qSlicerSaveDataDialogPrivate::mrmlScene() const`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:192: void qSlicerSaveDataDialogPrivate::setDirectory(const QString& newDirectory)`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:213: void qSlicerSaveDataDialogPrivate::populateItems()`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:269: void qSlicerSaveDataDialogPrivate::populateScene()`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:350: void qSlicerSaveDataDialogPrivate::populateNode(vtkMRMLNode* node)`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:421: QFileInfo qSlicerSaveDataDialogPrivate::nodeFileInfo(vtkMRMLStorableNode* node)`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:491: QTableWidgetItem* qSlicerSaveDataDialogPrivate::createNodeNameItem(vtkMRMLStorableNode* node)`
- API footprints: `AddMessage`, `GetModifiedSinceRead`, `GetName`, `GetNodeByID`, `GetNodeTagName`, `GetStorageNode`, `GetUserMessages`, `SetRootDirectory`, `vtkMRMLStorableNode::SafeDownCast`

## widget: SelectDataButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: select modified data only | SelectDataButton | QToolButton
- Tooltip: select modified data only
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:154: connect(this->SelectDataButton, SIGNAL(clicked()), this, SLOT(selectModifiedData()));`
- Connected slots/functions: `selectModifiedData`

## widget: ButtonBox

- Confidence: `linked_to_slot`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Connected slots/functions: `accept`, `reject`
- Declared UI connections: `accepted() -> qSlicerSaveDataDialog.accept()`; `rejected() -> qSlicerSaveDataDialog.reject()`

## widget: DirectoryButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkDirectoryButton`
- Search text: Change directory for selected files | DirectoryButton | ctkDirectoryButton
- Text: Change directory for selected files
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:152: connect(this->DirectoryButton, SIGNAL(directorySelected(QString)), this, SLOT(setDirectory(QString)));`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:235: this->DirectoryButton->setDirectory(this->MRMLScene->GetRootDirectory());`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:466: if (snode->GetFileName() == nullptr && !this->DirectoryButton->directory().isEmpty())`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:474: QFileInfo fileName(QDir(this->DirectoryButton->directory()), safeNodeName + fileExtension);`
- Connected slots/functions: `setDirectory`
- API footprints: `GetDefaultWriteFileExtension`, `GetFileName`, `GetRootDirectory`, `SetFileName`

## widget: ShowMoreCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show options | ShowMoreCheckBox | QCheckBox
- Text: Show options
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:156: connect(this->ShowMoreCheckBox, SIGNAL(toggled(bool)), this, SLOT(showMoreColumns(bool)));`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:164: this->ShowMoreCheckBox->setChecked(qSlicerApplication::application()->userSettings()->value(SHOW_OPTIONS_SETTINGS_KEY).toBool());`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:165: this->showMoreColumns(this->ShowMoreCheckBox->isChecked());`
- Connected slots/functions: `showMoreColumns`

## widget: SelectSceneDataButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Select scene & modified data only | SelectSceneDataButton | QToolButton
- Tooltip: Select scene & modified data only
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:153: connect(this->SelectSceneDataButton, SIGNAL(clicked()), this, SLOT(selectModifiedSceneData()));`
- Connected slots/functions: `selectModifiedSceneData`

## widget: FileWidget

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: FileWidget | QTableWidget
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:123: this->FileWidget->setItemDelegateForColumn(FileNameColumn, new qSlicerFileNameItemDelegate(this));`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:124: this->FileWidget->setStyleSheet(QStringLiteral("QAbstractItemView::indicator:unchecked {\n"`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:130: this->FileWidget->verticalHeader()->setVisible(false);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:133: // We replace the current FileWidget header view with a checkable header view.`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:137: this->FileWidget->model()->setHeaderData(SelectColumn, Qt::Horizontal, Qt::Unchecked, Qt::CheckStateRole);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:138: QHeaderView* previousHeaderView = this->FileWidget->horizontalHeader();`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:139: ctkCheckableHeaderView* headerView = new ctkCheckableHeaderView(Qt::Horizontal, this->FileWidget);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:149: this->FileWidget->setHorizontalHeader(headerView);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:158: connect(this->FileWidget, SIGNAL(itemChanged(QTableWidgetItem*)), this, SLOT(onItemChanged(QTableWidgetItem*)));`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:178: qSlicerFileNameItemDelegate* fileNameItemDelegate = dynamic_cast<qSlicerFileNameItemDelegate*>(this->FileWidget->itemDelegateForColumn(Self::FileNameColumn));`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:197: const int rowCount = this->FileWidget->rowCount();`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:200: QTableWidgetItem* selectItem = this->FileWidget->item(row, SelectColumn);`
- Connected slots/functions: `onItemChanged`
- API footprints: `GetID`, `GetModifiedSinceRead`, `GetRootDirectory`, `GetStorageNode`

## widget: DataBundleButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Create a Medical Record Bundle containing the scene | DataBundleButton | QToolButton
- Tooltip: Create a Medical Record Bundle containing the scene
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:155: connect(this->DataBundleButton, SIGNAL(clicked()), this, SLOT(saveSceneAsDataBundle()));`
- Connected slots/functions: `saveSceneAsDataBundle`

## widget: ErrorLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: <html><head/><body><p><span style=" font-weight:600; color:#ff0000;">Errors or warnings occurred while saving. See status icons for details.</span></p></body></html> | ErrorLabel | QLabel
- Text: <html><head/><body><p><span style=" font-weight:600; color:#ff0000;">Errors or warnings occurred while saving. See status icons for details.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSaveDataDialog.cxx`, `Base/QTGUI/qSlicerSaveDataDialog.h`, `Base/QTGUI/qSlicerSaveDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:116: this->ErrorLabel->setVisible(false);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:217: this->ErrorLabel->setVisible(false);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:654: this->ErrorLabel->setVisible(false);`
  - `Base/QTGUI/qSlicerSaveDataDialog.cxx:713: this->ErrorLabel->setVisible(!success);`
