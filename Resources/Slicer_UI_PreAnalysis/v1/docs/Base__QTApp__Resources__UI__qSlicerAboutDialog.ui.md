# Slicer UI Analysis: Base/QTApp/Resources/UI/qSlicerAboutDialog.ui

- Owner class: `qSlicerAboutDialog`
- UI file: `Base/QTApp/Resources/UI/qSlicerAboutDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerAboutDialog

- Confidence: `linked_to_code`
- Widget/action class: `QDialog`
- Search text: qSlicerAboutDialog | QDialog
- Implementation candidates: `Base/QTApp/qSlicerAboutDialog.cxx`, `Base/QTApp/qSlicerAboutDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerAboutDialog.cxx:24: #include "qSlicerAboutDialog.h"`
  - `Base/QTApp/qSlicerAboutDialog.cxx:26: #include "ui_qSlicerAboutDialog.h"`
  - `Base/QTApp/qSlicerAboutDialog.cxx:33: class qSlicerAboutDialogPrivate : public Ui_qSlicerAboutDialog`
  - `Base/QTApp/qSlicerAboutDialog.cxx:39: // qSlicerAboutDialogPrivate methods`
  - `Base/QTApp/qSlicerAboutDialog.cxx:42: // qSlicerAboutDialog methods`
  - `Base/QTApp/qSlicerAboutDialog.cxx:43: qSlicerAboutDialog::qSlicerAboutDialog(QWidget* parentWidget)`
  - `Base/QTApp/qSlicerAboutDialog.cxx:45: , d_ptr(new qSlicerAboutDialogPrivate)`
  - `Base/QTApp/qSlicerAboutDialog.cxx:47: Q_D(qSlicerAboutDialog);`
  - `Base/QTApp/qSlicerAboutDialog.cxx:93: void qSlicerAboutDialog::setLogo(const QPixmap& newLogo)`
  - `Base/QTApp/qSlicerAboutDialog.cxx:95: Q_D(qSlicerAboutDialog);`
  - `Base/QTApp/qSlicerAboutDialog.cxx:100: qSlicerAboutDialog::~qSlicerAboutDialog() = default;`
  - `Base/QTApp/qSlicerAboutDialog.h:21: #ifndef __qSlicerAboutDialog_h`

## widget: SlicerLinksTextBrowser

- Confidence: `linked_to_code`
- Widget/action class: `QTextBrowser`
- Search text: SlicerLinksTextBrowser | QTextBrowser
- Implementation candidates: `Base/QTApp/qSlicerAboutDialog.cxx`, `Base/QTApp/qSlicerAboutDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerAboutDialog.cxx:86: d->SlicerLinksTextBrowser->insertHtml(slicer->copyrights());`

## widget: CreditsTextBrowser

- Confidence: `linked_to_code`
- Widget/action class: `QTextBrowser`
- Search text: CreditsTextBrowser | QTextBrowser
- Implementation candidates: `Base/QTApp/qSlicerAboutDialog.cxx`, `Base/QTApp/qSlicerAboutDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerAboutDialog.cxx:52: d->CreditsTextBrowser->setFontPointSize(25);`
  - `Base/QTApp/qSlicerAboutDialog.cxx:53: d->CreditsTextBrowser->append(slicer->mainApplicationDisplayName());`
  - `Base/QTApp/qSlicerAboutDialog.cxx:54: d->CreditsTextBrowser->setFontPointSize(11);`
  - `Base/QTApp/qSlicerAboutDialog.cxx:55: d->CreditsTextBrowser->append("");`
  - `Base/QTApp/qSlicerAboutDialog.cxx:58: d->CreditsTextBrowser->append(slicer->applicationVersion() + " " + "r" + slicer->revision() + " / " + slicer->repositoryRevision());`
  - `Base/QTApp/qSlicerAboutDialog.cxx:59: d->CreditsTextBrowser->append("");`
  - `Base/QTApp/qSlicerAboutDialog.cxx:67: d->CreditsTextBrowser->insertHtml(`
  - `Base/QTApp/qSlicerAboutDialog.cxx:69: d->CreditsTextBrowser->append("");`
  - `Base/QTApp/qSlicerAboutDialog.cxx:74: d->CreditsTextBrowser->insertHtml(tr("Visit the %1 to check if a new version is available.").arg(downloadSiteLink));`
  - `Base/QTApp/qSlicerAboutDialog.cxx:75: d->CreditsTextBrowser->append("");`
  - `Base/QTApp/qSlicerAboutDialog.cxx:77: d->CreditsTextBrowser->append("");`
  - `Base/QTApp/qSlicerAboutDialog.cxx:81: d->CreditsTextBrowser->append(slicer->applicationVersion() + " (" + slicer->mainApplicationRepositoryRevision() + ")");`

## widget: SlicerLabel

- Confidence: `linked_to_code`
- Widget/action class: `ctkThumbnailLabel`
- Search text: SlicerLabel | ctkThumbnailLabel
- Implementation candidates: `Base/QTApp/qSlicerAboutDialog.cxx`, `Base/QTApp/qSlicerAboutDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerAboutDialog.cxx:96: d->SlicerLabel->setPixmap(newLogo);`

## widget: ButtonBoxWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: ButtonBoxWidget | QWidget
- Implementation candidates: `Base/QTApp/qSlicerAboutDialog.cxx`, `Base/QTApp/qSlicerAboutDialog.h`

## widget: ButtonBox

- Confidence: `linked_to_slot`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTApp/qSlicerAboutDialog.cxx`, `Base/QTApp/qSlicerAboutDialog.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerAboutDialog.cxx:89: connect(d->ButtonBox, SIGNAL(rejected()), this, SLOT(close()));`
- Connected slots/functions: `close`
