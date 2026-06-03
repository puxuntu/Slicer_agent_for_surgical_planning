# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerExportNodeDialog.ui

- Owner class: `qSlicerExportNodeDialog`
- UI file: `Base/QTGUI/Resources/UI/qSlicerExportNodeDialog.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerExportNodeDialog

- Confidence: `linked_to_api`
- Widget/action class: `QDialog`
- Search text: qSlicerExportNodeDialog | QDialog
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:34: #include "qSlicerExportNodeDialog_p.h"`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:131: this->exportFormatComboBox->setEditText(qSlicerExportNodeDialog::tr("Select a format"));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:165: this->label->setText(qSlicerExportNodeDialog::tr("Export format:"));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:335: QString qSlicerExportNodeDialogPrivate::forceFileNameExtension(const QString& fileName, const QString& extension, vtkMRMLNode* node)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:344: QString qSlicerExportNodeDialogPrivate::defaultFilename(vtkMRMLNode* node, QString extension)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:356: return qSlicerExportNodeDialogPrivate::forceFileNameExtension(safeNodeName, extension, node);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:361: bool qSlicerExportNodeDialogPrivate::setDifferenceIsNonempty(const QList<T>& a, const QList<T>& b)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:374: bool qSlicerExportNodeDialogPrivate::layoutWidgetsAllInvisible(const QLayout* layout, const QWidget* relativeTo)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:388: qSlicerExportNodeDialogPrivate::qSlicerExportNodeDialogPrivate(QWidget* parentWidget)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:400: connect(this->RecursiveChildrenCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerExportNodeDialogPrivate::onNodeInclusionCheckboxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:401: connect(this->IncludeChildrenCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerExportNodeDialogPrivate::onNodeInclusionCheckboxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:402: connect(this->IncludeChildrenCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerExportNodeDialogPrivate::onIncludeChildrenCheckBoxStateChanged);`
- Connected slots/functions: `checkStateChanged`, `currentTextChanged`, `formatChangedSlot`, `onIncludeChildrenCheckBoxStateChanged`, `onNodeInclusionCheckboxStateChanged`, `stateChanged`
- API footprints: `AddMessage`, `GetID`, `GetName`, `GetNumberOfMessages`

## widget: FilenameLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Filename: | FilenameLabel | QLabel
- Text: Filename:
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`

## widget: FilenameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: FilenameLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:394: , ProtectFilenameLineEdit{ false }`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:398: connect(this->FilenameLineEdit, SIGNAL(editingFinished()), this, SLOT(onFilenameEditingFinished()));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:737: this->FilenameLineEdit->setEnabled(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:738: this->FilenameLineEdit->setToolTip(qSlicerExportNodeDialog::tr("When exporting multiple nodes, filenames are automatically set"));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:740: this->FilenameLineEdit->setText(qSlicerExportNodeDialog::tr("<automatic>"));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:746: this->FilenameLineEdit->setEnabled(true);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:747: this->FilenameLineEdit->setToolTip("");`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:749: this->FilenameLineEdit->setText(defaultFilename(this->theOnlyNode(), this->theOnlyNodeTypeWidgetSet()->extension()));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:751: this->FilenameLineEdit->setFocus(Qt::ActiveWindowFocusReason);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:792: setTabOrder(this->FilenameLineEdit, this->DirectoryPathLineEdit);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:865: if (this->nodeList().size() == 1 && this->FilenameLineEdit->isEnabled())`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:872: if (this->FilenameLineEdit->text() != betterFilename)`
- Connected slots/functions: `onFilenameEditingFinished`
- API footprints: `GetName`

## widget: DirectoryLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Directory: | DirectoryLabel | QLabel
- Text: Directory:
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`

## widget: DirectoryPathLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `ctkPathLineEdit`
- Search text: Destination directory | DirectoryPathLineEdit | ctkPathLineEdit
- Tooltip: Destination directory
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:409: // Set up DirectoryPathLineEdit widget to be a directory selector`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:410: this->DirectoryPathLineEdit->setLabel(qSlicerExportNodeDialog::tr("Output folder:"));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:411: this->DirectoryPathLineEdit->setFilters(ctkPathLineEdit::Dirs);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:412: this->DirectoryPathLineEdit->setMinimumSize(this->DirectoryPathLineEdit->sizeHint());`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:413: this->DirectoryPathLineEdit->setFocusPolicy(Qt::StrongFocus); // (ctkPathLineEdit has a default focus policy of NoFocus)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:512: this->DirectoryPathLineEdit->setCurrentPath(this->LastUsedDirectory.isEmpty() ? this->MRMLScene->GetRootDirectory() : this->LastUsedDirectory);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:790: // properly set up for DirectoryPathLineEdit and for each optionsStackedWidget`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:792: setTabOrder(this->FilenameLineEdit, this->DirectoryPathLineEdit);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:804: setTabOrder(this->DirectoryPathLineEdit, nodeTypeWidgetSet->exportFormatComboBox);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:838: this->LastUsedDirectory = this->DirectoryPathLineEdit->currentPath();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:916: QDir directory = this->PreserveHierarchyCheckBox->isChecked() ? this->getSubjectHierarchyBasedDirectory(node) : this->DirectoryPathLineEdit->currentPath();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:1116: return this->DirectoryPathLineEdit->currentPath();`
- API footprints: `GetName`, `GetRootDirectory`

## widget: ExportFormatsLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Export formats: | ExportFormatsLabel | QLabel
- Text: Export formats:
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:417: this->formLayout->getWidgetPosition(this->ExportFormatsLabel, &exportFormatsLabelRow, nullptr); // (returns to second parameter)`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:765: this->ExportFormatsLabel->show();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:770: this->ExportFormatsLabel->hide();`

## widget: GeneralOptionsLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Options: | GeneralOptionsLabel | QLabel
- Text: Options:
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:779: this->GeneralOptionsLabel->setVisible(!layoutWidgetsAllInvisible(this->GeneralOptionsLayout, this));`

## widget: GeneralOptionsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: GeneralOptionsWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`

## widget: IncludeChildrenCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Include children | Include nodes directly under the selected item in the hierarchy. | IncludeChildrenCheckBox | QCheckBox
- Text: Include children
- Tooltip: Include nodes directly under the selected item in the hierarchy.
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:401: connect(this->IncludeChildrenCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerExportNodeDialogPrivate::onNodeInclusionCheckboxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:402: connect(this->IncludeChildrenCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerExportNodeDialogPrivate::onIncludeChildrenCheckBoxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:405: connect(this->IncludeChildrenCheckBox, &QCheckBox::stateChanged, this, &qSlicerExportNodeDialogPrivate::onNodeInclusionCheckboxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:406: connect(this->IncludeChildrenCheckBox, &QCheckBox::stateChanged, this, &qSlicerExportNodeDialogPrivate::onIncludeChildrenCheckBoxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:436: if (!this->IncludeChildrenCheckBox->isChecked())`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:464: this->IncludeChildrenCheckBox->blockSignals(true); // don't trigger onNodeInclusionCheckboxStateChanged`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:468: this->IncludeChildrenCheckBox->setChecked(true);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:469: this->IncludeChildrenCheckBox->hide();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:474: this->IncludeChildrenCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:475: this->IncludeChildrenCheckBox->hide();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:480: this->IncludeChildrenCheckBox->setChecked(this->LastUsedIncludeChildren);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:481: this->IncludeChildrenCheckBox->show();`
- Connected slots/functions: `checkStateChanged`, `onIncludeChildrenCheckBoxStateChanged`, `onNodeInclusionCheckboxStateChanged`, `stateChanged`

## widget: RecursiveChildrenCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Recursively include children | Include all nodes in the selected item in the hierarchy, including in subfolders. | RecursiveChildrenCheckBox | QCheckBox
- Text: Recursively include children
- Tooltip: Include all nodes in the selected item in the hierarchy, including in subfolders.
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:400: connect(this->RecursiveChildrenCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerExportNodeDialogPrivate::onNodeInclusionCheckboxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:404: connect(this->RecursiveChildrenCheckBox, &QCheckBox::stateChanged, this, &qSlicerExportNodeDialogPrivate::onNodeInclusionCheckboxStateChanged);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:442: return this->RecursiveChildrenCheckBox->isChecked() ? this->NodesRecursive : this->NodesNonrecursive;`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:486: this->RecursiveChildrenCheckBox->blockSignals(true); // don't trigger onNodeInclusionCheckboxStateChanged`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:489: this->RecursiveChildrenCheckBox->setChecked(this->LastUsedRecursiveChildren);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:490: this->RecursiveChildrenCheckBox->setEnabled(true);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:494: this->RecursiveChildrenCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:495: this->RecursiveChildrenCheckBox->setEnabled(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:498: this->RecursiveChildrenCheckBox->setVisible(setDifferenceIsNonempty(nodesRecursive, nodesNonrecursive));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:502: this->RecursiveChildrenCheckBox->setChecked(true);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:503: this->RecursiveChildrenCheckBox->hide();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:505: this->RecursiveChildrenCheckBox->blockSignals(false);`
- Connected slots/functions: `checkStateChanged`, `onNodeInclusionCheckboxStateChanged`, `stateChanged`

## widget: PreserveHierarchyCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Export folder structure | Create subdirectory structure based on node hierarchy. Uncheck this to export all nodes directly into the target directory. | PreserveHierarchyCheckBox | QCheckBox
- Text: Export folder structure
- Tooltip: Create subdirectory structure based on node hierarchy. Uncheck this to export all nodes directly into the target directory.
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:509: this->updatePreserveHierarchyCheckBox();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:558: this->updatePreserveHierarchyCheckBox();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:587: void qSlicerExportNodeDialogPrivate::updatePreserveHierarchyCheckBox()`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:590: this->PreserveHierarchyCheckBox->setVisible(this->NodesSelectedOnly.empty() || this->NodesRecursive.size() > 1);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:595: this->PreserveHierarchyCheckBox->setEnabled(true);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:596: this->PreserveHierarchyCheckBox->setChecked(this->LastUsedPreserveHierarchy);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:600: this->PreserveHierarchyCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:601: this->PreserveHierarchyCheckBox->setEnabled(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:818: setTabOrder(this->RecursiveChildrenCheckBox, this->PreserveHierarchyCheckBox);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:819: setTabOrder(this->PreserveHierarchyCheckBox, this->HardenTransformCheckBox);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:845: if (this->PreserveHierarchyCheckBox->isVisible())`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:847: this->LastUsedPreserveHierarchy = this->PreserveHierarchyCheckBox->isChecked();`

## widget: HardenTransformCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Apply transforms | Temporarily harden any transforms for export | HardenTransformCheckBox | QCheckBox
- Text: Apply transforms
- Tooltip: Temporarily harden any transforms for export
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:508: this->updateHardenTransformCheckBox();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:548: this->updateHardenTransformCheckBox();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:562: void qSlicerExportNodeDialogPrivate::updateHardenTransformCheckBox()`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:576: this->HardenTransformCheckBox->show();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:577: this->HardenTransformCheckBox->setChecked(this->LastUsedHardenTransform);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:581: this->HardenTransformCheckBox->hide();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:582: this->HardenTransformCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:819: setTabOrder(this->PreserveHierarchyCheckBox, this->HardenTransformCheckBox);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:820: setTabOrder(this->HardenTransformCheckBox, this->ButtonBox);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:840: if (this->HardenTransformCheckBox->isVisible())`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:842: this->LastUsedHardenTransform = this->HardenTransformCheckBox->isChecked();`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:1026: bool success = coreIOManager->exportNodes(savingParameterMaps, this->HardenTransformCheckBox->isChecked(), userMessages);`

## widget: ButtonBox

- Confidence: `linked_to_code`
- Widget/action class: `QDialogButtonBox`
- Search text: ButtonBox | QDialogButtonBox
- Implementation candidates: `Base/QTGUI/qSlicerExportNodeDialog.cxx`, `Base/QTGUI/qSlicerExportNodeDialog.h`, `Base/QTGUI/qSlicerExportNodeDialog_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:427: this->ButtonBox->button(QDialogButtonBox::Save)->setText(qSlicerExportNodeDialog::tr("&Export"));`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:742: this->ButtonBox->setFocus(Qt::ActiveWindowFocusReason);`
  - `Base/QTGUI/qSlicerExportNodeDialog.cxx:820: setTabOrder(this->HardenTransformCheckBox, this->ButtonBox);`
