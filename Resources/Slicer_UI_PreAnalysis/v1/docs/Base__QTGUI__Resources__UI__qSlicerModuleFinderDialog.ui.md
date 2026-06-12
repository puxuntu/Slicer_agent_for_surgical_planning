# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerModuleFinderDialog.ui

- Owner class: `qSlicerModuleFinderDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerModuleFinderDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerModuleFinderDialog

- Confidence: `linked_to_code`
- Widget/action class: `QDialog`
- Search text: qSlicerModuleFinderDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:33: #include "qSlicerModuleFinderDialog.h"`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:35: #include "ui_qSlicerModuleFinderDialog.h"`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:38: // qSlicerModuleFinderDialogPrivate`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:41: class qSlicerModuleFinderDialogPrivate : public Ui_qSlicerModuleFinderDialog`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:43: Q_DECLARE_PUBLIC(qSlicerModuleFinderDialog);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:46: qSlicerModuleFinderDialog* const q_ptr;`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:49: qSlicerModuleFinderDialogPrivate(qSlicerModuleFinderDialog& object);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:60: // qSlicerModuleFinderDialogPrivate methods`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:63: qSlicerModuleFinderDialogPrivate::qSlicerModuleFinderDialogPrivate(qSlicerModuleFinderDialog& object)`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:69: void qSlicerModuleFinderDialogPrivate::init()`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:71: Q_Q(qSlicerModuleFinderDialog);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:105: okButton->setText(qSlicerModuleFinderDialog::tr("Switch to module"));`

## widget: ModuleListView

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerModulesListView`
- Search text: ModuleListView | qSlicerModulesListView
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:75: qSlicerModuleFactoryFilterModel* filterModel = this->ModuleListView->filterModel();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:99: QObject::connect(this->ModuleListView->selectionModel(), SIGNAL(selectionChanged(QItemSelection, QItemSelection)), q, SLOT(onSelectionChanged(QItemSelection, QItemSelection)));`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:102: this->ModuleListView->viewport()->installEventFilter(q);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:110: this->ModuleListView->setCurrentIndex(filterModel->index(0, 0));`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:117: qSlicerModuleFactoryFilterModel* filterModel = this->ModuleListView->filterModel();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:120: if (!this->ModuleListView->currentIndex().isValid())`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:125: this->ModuleListView->setCurrentIndex(filterModel->index(0, 0));`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:129: if (this->ModuleListView->currentIndex().isValid())`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:131: this->ModuleListView->scrollTo(this->ModuleListView->currentIndex());`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:153: d->ModuleListView->setFactoryManager(factoryManager);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:167: QModelIndexList selectedIndexes = d->ModuleListView->selectionModel()->selectedIndexes();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:315: qSlicerModuleFactoryFilterModel* filterModel = d->ModuleListView->filterModel();`
- Connected slots/functions: `onSelectionChanged`

## widget: ButtonBox

- Confidence: `linked_to_slot`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:104: QPushButton* okButton = this->ButtonBox->button(QDialogButtonBox::Ok);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:297: QPushButton* okButton = d->ButtonBox->button(QDialogButtonBox::Ok);`
- Connected slots/functions: `accept`, `reject`
- Declared UI connections: `accepted() -> qSlicerModuleFinderDialog.accept()`; `rejected() -> qSlicerModuleFinderDialog.reject()`

## widget: ModuleDescriptionBrowser

- Confidence: `linked_to_code`
- Widget/action class: `QTextBrowser`
- Search text: ModuleDescriptionBrowser | QTextBrowser
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:184: d->ModuleDescriptionBrowser->clear();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:225: d->ModuleDescriptionBrowser->document()->addResource(QTextDocument::ImageResource, QUrl("module://logo.png"), QVariant(guiModule->logo()));`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:281: d->ModuleDescriptionBrowser->setHtml(html);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:285: d->ModuleDescriptionBrowser->clear();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:288: d->ModuleDescriptionBrowser->setText(tr("%1 module is not loaded").arg(moduleName));`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:293: QTextCursor cursor = d->ModuleDescriptionBrowser->textCursor();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:295: d->ModuleDescriptionBrowser->setTextCursor(cursor);`

## widget: FilterTitleSearchBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSearchBox`
- Search text: FilterTitleSearchBox | ctkSearchBox
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:97: QObject::connect(this->FilterTitleSearchBox, SIGNAL(textChanged(QString)), q, SLOT(onModuleTitleFilterTextChanged()));`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:101: this->FilterTitleSearchBox->installEventFilter(q);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:305: if (target == d->FilterTitleSearchBox)`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:369: d->FilterTitleSearchBox->setFocus();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:377: d->FilterTitleSearchBox->setText(text);`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:396: filterModel->setFilterFixedString(d->FilterTitleSearchBox->text());`
- Connected slots/functions: `onModuleTitleFilterTextChanged`

## widget: SearchInAllTextCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: &Full text | Search in full text (module name and description). If unchecked then only module names are searched. | SearchInAllTextCheckBox | QCheckBox
- Text: &Full text
- Tooltip: Search in full text (module name and description). If unchecked then only module names are searched.
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:94: QObject::connect(this->SearchInAllTextCheckBox, SIGNAL(toggled(bool)), q, SLOT(setSearchInAllText(bool)));`
- Connected slots/functions: `setSearchInAllText`

## widget: ShowBuiltInCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: &Built-in | Show built-in modules. Unchecking makes it easier to find modules provided by extensions. | ShowBuiltInCheckBox | QCheckBox
- Text: &Built-in
- Tooltip: Show built-in modules. Unchecking makes it easier to find modules provided by extensions.
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:95: QObject::connect(this->ShowBuiltInCheckBox, SIGNAL(toggled(bool)), q, SLOT(setShowBuiltInModules(bool)));`
- Connected slots/functions: `setShowBuiltInModules`
- Key UI properties: {"checked": "true"}

## widget: ShowTestingCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: &Testing | Show testing modules. Useful for software testing and troubleshooting. | ShowTestingCheckBox | QCheckBox
- Text: &Testing
- Tooltip: Show testing modules. Useful for software testing and troubleshooting.
- Implementation candidates: `Base/QTGUI/qSlicerModuleFinderDialog.cxx`, `Base/QTGUI/qSlicerModuleFinderDialog.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:88: this->ShowTestingCheckBox->hide();`
  - `Base/QTGUI/qSlicerModuleFinderDialog.cxx:96: QObject::connect(this->ShowTestingCheckBox, SIGNAL(toggled(bool)), q, SLOT(setShowTestingModules(bool)));`
- Connected slots/functions: `setShowTestingModules`
