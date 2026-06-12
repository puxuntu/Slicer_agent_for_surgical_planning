# Slicer UI Analysis: Base/QTApp/Resources/UI/qSlicerErrorReportDialog.ui

- Owner class: `qSlicerErrorReportDialog`
- UI file: `Base/QTApp/Resources/UI/qSlicerErrorReportDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerErrorReportDialog

- Confidence: `linked_to_code`
- Widget/action class: `QDialog`
- Search text: qSlicerErrorReportDialog | QDialog
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:31: #include "qSlicerErrorReportDialog.h"`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:34: #include "ui_qSlicerErrorReportDialog.h"`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:37: class qSlicerErrorReportDialogPrivate : public Ui_qSlicerErrorReportDialog`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:43: // qSlicerErrorReportDialogPrivate methods`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:46: // qSlicerErrorReportDialog methods`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:47: qSlicerErrorReportDialog::qSlicerErrorReportDialog(QWidget* parentWidget)`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:49: , d_ptr(new qSlicerErrorReportDialogPrivate)`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:51: Q_D(qSlicerErrorReportDialog);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:141: qSlicerErrorReportDialog::~qSlicerErrorReportDialog() = default;`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:144: void qSlicerErrorReportDialog::onLogCopy()`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:146: Q_D(qSlicerErrorReportDialog);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:151: void qSlicerErrorReportDialog::onLogFileSelectionChanged()`

## widget: InstructionsLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: <html><head/><body><p><span style=" font-weight:600;">Questions and feature requests:</span> visit the <a href="https://discourse.slicer.org"><span style=" text-decoration: underline;">Slicer forum</span></a>.</p><p><span style=" font-weight:600;">Bug reports: </span><a href="https://discourse.slicer.org/new-topic?body=Problem%20report%20for%20[appname-version-platform]:%20[please%20describe%20expected%20and%20actual%20behavior]&amp;category=support"><span style=" text-decoration: underline;">post a new topic to the Slicer forum</span></a> to tell us about your problem or submit a bug report to the <a href="https://issues.slicer.org"><span style=" text-decoration: underline;">3D Slicer bugtracker</span></a>. Describe the steps that lead to the error and also attach log messages.</p><p><span style=" font-weight:600;">Warning - if you work with patient data:</span> Check that the log messages do not contain any information that may identify a patient. Send the log messages to specific people instead of sharing them publicly on a mailing list or website.</p></body></html> | InstructionsLabel | QLabel
- Text: <html><head/><body><p><span style=" font-weight:600;">Questions and feature requests:</span> visit the <a href="https://discourse.slicer.org"><span style=" text-decoration: underline;">Slicer forum</span></a>.</p><p><span style=" font-weight:600;">Bug reports: </span><a href="https://discourse.slicer.org/new-topic?body=Problem%20report%20for%20[appname-version-platform]:%20[please%20describe%20expected%20and%20actual%20behavior]&amp;category=support"><span style=" text-decoration: underline;">post a new topic to the Slicer forum</span></a> to tell us about your problem or submit a bug report to the <a href="https://issues.slicer.org"><span style=" text-decoration: underline;">3D Slicer bugtracker</span></a>. Describe the steps that lead to the error and also attach log messages.</p><p><span style=" font-weight:600;">Warning - if you work with patient data:</span> Check that the log messages do not contain any information that may identify a patient. Send the log messages to specific people instead of sharing them publicly on a mailing list or website.</p></body></html>
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:54: QString instructionsText = d->InstructionsLabel->text();`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:60: d->InstructionsLabel->setText(instructionsText);`

## widget: RecentLogFilesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Recent log files: | RecentLogFilesLabel | QLabel
- Text: Recent log files:
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`

## widget: LogText

- Confidence: `linked_to_code`
- Widget/action class: `QPlainTextEdit`
- Search text: LogText | QPlainTextEdit
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:147: QApplication::clipboard()->setText(d->LogText->toPlainText());`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:161: d->LogText->setPlainText(logText);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:165: d->LogText->clear();`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:193: d->LogText->setReadOnly(!editable);`

## widget: LogCopyToClipboardPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkPushButton`
- Search text: Copy log to clipboard | LogCopyToClipboardPushButton | ctkPushButton
- Text: Copy log to clipboard
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:130: QObject::connect(d->LogCopyToClipboardPushButton, SIGNAL(clicked()), this, SLOT(onLogCopy()));`
- Connected slots/functions: `onLogCopy`

## widget: LogFileOpenPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkPushButton`
- Search text: Open log in editor | LogFileOpenPushButton | ctkPushButton
- Text: Open log in editor
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:132: QObject::connect(d->LogFileOpenPushButton, SIGNAL(clicked()), this, SLOT(onLogFileOpen()));`
- Connected slots/functions: `onLogFileOpen`

## widget: LogOpenFileLocationPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkPushButton`
- Search text: Open log location | LogOpenFileLocationPushButton | ctkPushButton
- Text: Open log location
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:131: QObject::connect(d->LogOpenFileLocationPushButton, SIGNAL(clicked()), this, SLOT(onLogFileLocationOpen()));`
- Connected slots/functions: `onLogFileLocationOpen`

## widget: LogFileEditCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Edit Log | LogFileEditCheckBox | QCheckBox
- Text: Edit Log
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:133: QObject::connect(d->LogFileEditCheckBox, SIGNAL(clicked(bool)), this, SLOT(onLogFileEditClicked(bool)));`
- Connected slots/functions: `onLogFileEditClicked`

## widget: ButtonBox

- Confidence: `linked_to_slot`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:135: connect(d->ButtonBox, SIGNAL(rejected()), this, SLOT(close()));`
- Connected slots/functions: `close`

## widget: RecentLogFilesComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `QTableWidget`
- Search text: RecentLogFilesComboBox | QTableWidget
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:64: d->RecentLogFilesComboBox->setSelectionMode(QAbstractItemView::ExtendedSelection);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:65: d->RecentLogFilesComboBox->setColumnCount(6);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:66: d->RecentLogFilesComboBox->setHorizontalHeaderLabels(headers);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:67: for (int i = 0; i < d->RecentLogFilesComboBox->columnCount(); i++)`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:69: d->RecentLogFilesComboBox->horizontalHeader()->setSectionResizeMode(i, QHeaderView::ResizeToContents);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:114: int row = d->RecentLogFilesComboBox->rowCount();`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:115: d->RecentLogFilesComboBox->insertRow(row);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:116: d->RecentLogFilesComboBox->setItem(row, 0, itemApp);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:117: d->RecentLogFilesComboBox->setItem(row, 1, itemVersion);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:118: d->RecentLogFilesComboBox->setItem(row, 2, itemRevision);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:119: d->RecentLogFilesComboBox->setItem(row, 3, itemDate);`
  - `Base/QTApp/qSlicerErrorReportDialog.cxx:120: d->RecentLogFilesComboBox->setItem(row, 4, itemTime);`
- Connected slots/functions: `onLogFileSelectionChanged`

## widget: RecentLogFilesLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Log file content: | RecentLogFilesLabel_2 | QLabel
- Text: Log file content:
- Implementation candidates: `Base/QTApp/qSlicerErrorReportDialog.cxx`, `Base/QTApp/qSlicerErrorReportDialog.h`
