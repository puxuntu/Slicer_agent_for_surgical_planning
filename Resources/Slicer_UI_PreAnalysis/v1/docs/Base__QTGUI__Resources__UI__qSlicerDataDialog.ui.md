# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerDataDialog.ui

- Owner class: `qSlicerDataDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerDataDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerDataDialog

- Confidence: `linked_to_slot`
- Widget/action class: `QDialog`
- Search text: qSlicerDataDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerDataDialog.cxx`, `Base/QTGUI/qSlicerDataDialog.h`, `Base/QTGUI/qSlicerDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerDataDialog.cxx:42: #include "qSlicerDataDialog_p.h"`
  - `Base/QTGUI/qSlicerDataDialog.cxx:51: qSlicerDataDialogPrivate::qSlicerDataDialogPrivate(qSlicerDataDialog* object, QWidget* _parent /*=nullptr*/)`
  - `Base/QTGUI/qSlicerDataDialog.cxx:121: qSlicerDataDialogPrivate::~qSlicerDataDialogPrivate() = default;`
  - `Base/QTGUI/qSlicerDataDialog.cxx:124: void qSlicerDataDialogPrivate::addDirectory()`
  - `Base/QTGUI/qSlicerDataDialog.cxx:139: void qSlicerDataDialogPrivate::addFiles()`
  - `Base/QTGUI/qSlicerDataDialog.cxx:152: void qSlicerDataDialogPrivate::addDirectory(const QDir& directory)`
  - `Base/QTGUI/qSlicerDataDialog.cxx:190: void qSlicerDataDialogPrivate::addFile(const QFileInfo& file, const QString& readerDescription, qSlicerIO::IOProperties* ioProperties)`
  - `Base/QTGUI/qSlicerDataDialog.cxx:249: QObject::connect(descriptionComboBox, &QComboBox::currentTextChanged, this, &qSlicerDataDialogPrivate::onFileTypeChanged);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:250: QObject::connect(descriptionComboBox, &QComboBox::textActivated, this, &qSlicerDataDialogPrivate::onFileTypeActivated);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:266: void qSlicerDataDialogPrivate::dragEnterEvent(QDragEnterEvent* event)`
  - `Base/QTGUI/qSlicerDataDialog.cxx:268: Q_Q(qSlicerDataDialog);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:276: void qSlicerDataDialogPrivate::dropEvent(QDropEvent* event)`
- Connected slots/functions: `currentTextChanged`, `onFileTypeActivated`, `onFileTypeChanged`, `textActivated`

## widget: AddDirectoryButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Choose Directory to Add | AddDirectoryButton | QPushButton
- Text: Choose Directory to Add
- Implementation candidates: `Base/QTGUI/qSlicerDataDialog.cxx`, `Base/QTGUI/qSlicerDataDialog.h`, `Base/QTGUI/qSlicerDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerDataDialog.cxx:89: connect(this->AddDirectoryButton, SIGNAL(clicked()), this, SLOT(addDirectory()));`
  - `Base/QTGUI/qSlicerDataDialog.cxx:114: this->AddDirectoryButton->setDefault(false);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:115: this->AddDirectoryButton->setAutoDefault(false);`
- Connected slots/functions: `addDirectory`

## widget: AddFilesButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Choose File(s) to Add | AddFilesButton | QPushButton
- Text: Choose File(s) to Add
- Implementation candidates: `Base/QTGUI/qSlicerDataDialog.cxx`, `Base/QTGUI/qSlicerDataDialog.h`, `Base/QTGUI/qSlicerDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerDataDialog.cxx:90: connect(this->AddFilesButton, SIGNAL(clicked()), this, SLOT(addFiles()));`
  - `Base/QTGUI/qSlicerDataDialog.cxx:116: this->AddFilesButton->setDefault(false);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:117: this->AddFilesButton->setAutoDefault(false);`
- Connected slots/functions: `addFiles`

## widget: FileWidget

- Confidence: `linked_to_code`
- Widget/action class: `QTableWidget`
- Search text: FileWidget | QTableWidget
- Implementation candidates: `Base/QTGUI/qSlicerDataDialog.cxx`, `Base/QTGUI/qSlicerDataDialog.h`, `Base/QTGUI/qSlicerDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerDataDialog.cxx:58: // We replace the current FileWidget header view with a checkable header view.`
  - `Base/QTGUI/qSlicerDataDialog.cxx:63: this->FileWidget->model()->setHeaderData(FileColumn, Qt::Horizontal, Qt::Unchecked, Qt::CheckStateRole);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:64: QHeaderView* previousHeaderView = this->FileWidget->horizontalHeader();`
  - `Base/QTGUI/qSlicerDataDialog.cxx:65: ctkCheckableHeaderView* headerView = new ctkCheckableHeaderView(Qt::Horizontal, this->FileWidget);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:75: this->FileWidget->setHorizontalHeader(headerView);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:82: this->FileWidget->sortItems(-1, Qt::AscendingOrder);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:92: // Reset clears the FileWidget of all previously added files.`
  - `Base/QTGUI/qSlicerDataDialog.cxx:132: bool sortingEnabled = this->FileWidget->isSortingEnabled();`
  - `Base/QTGUI/qSlicerDataDialog.cxx:133: this->FileWidget->setSortingEnabled(false);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:135: this->FileWidget->setSortingEnabled(sortingEnabled);`
  - `Base/QTGUI/qSlicerDataDialog.cxx:196: if (!this->FileWidget->findItems(file.absoluteFilePath(), Qt::MatchExactly).isEmpty())`
  - `Base/QTGUI/qSlicerDataDialog.cxx:230: bool sortingEnabled = this->FileWidget->isSortingEnabled();`

## widget: ButtonBox

- Confidence: `linked_to_code`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTGUI/qSlicerDataDialog.cxx`, `Base/QTGUI/qSlicerDataDialog.h`, `Base/QTGUI/qSlicerDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerDataDialog.cxx:93: QPushButton* resetButton = this->ButtonBox->button(QDialogButtonBox::Reset);`

## widget: ShowOptionsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show Options | ShowOptionsCheckBox | QCheckBox
- Text: Show Options
- Implementation candidates: `Base/QTGUI/qSlicerDataDialog.cxx`, `Base/QTGUI/qSlicerDataDialog.h`, `Base/QTGUI/qSlicerDataDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerDataDialog.cxx:85: connect(this->ShowOptionsCheckBox, SIGNAL(toggled(bool)), this, SLOT(showOptions(bool)));`
  - `Base/QTGUI/qSlicerDataDialog.cxx:324: this->ShowOptionsCheckBox->setChecked(show);`
- Connected slots/functions: `showOptions`
- Key UI properties: {"checked": "true"}
