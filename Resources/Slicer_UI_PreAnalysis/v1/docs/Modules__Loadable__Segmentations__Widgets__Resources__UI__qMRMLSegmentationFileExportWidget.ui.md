# Slicer UI Analysis: Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationFileExportWidget.ui

- Owner class: `qMRMLSegmentationFileExportWidget`
- UI file: `Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationFileExportWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentationFileExportWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSegmentationFileExportWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:24: #include "qMRMLSegmentationFileExportWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:26: #include "ui_qMRMLSegmentationFileExportWidget.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:55: class qMRMLSegmentationFileExportWidgetPrivate : public Ui_qMRMLSegmentationFileExportWidget`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:57: Q_DECLARE_PUBLIC(qMRMLSegmentationFileExportWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:60: qMRMLSegmentationFileExportWidget* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:63: qMRMLSegmentationFileExportWidgetPrivate(qMRMLSegmentationFileExportWidget& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:72: qMRMLSegmentationFileExportWidgetPrivate::qMRMLSegmentationFileExportWidgetPrivate(qMRMLSegmentationFileExportWidget& object)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:79: void qMRMLSegmentationFileExportWidgetPrivate::init()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:81: Q_Q(qMRMLSegmentationFileExportWidget);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:92: // qMRMLSegmentationFileExportWidget methods`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:95: qMRMLSegmentationFileExportWidget::qMRMLSegmentationFileExportWidget(QWidget* _parent)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:97: , d_ptr(new qMRMLSegmentationFileExportWidgetPrivate(*this))`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ColorTableNodeSelector.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> ReferenceVolumeComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetID`, `GetPointer`, `vtkMRMLSegmentationNode::SafeDownCast`

## widget: VisibleSegmentsOnlyLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visible segments only:  | VisibleSegmentsOnlyLabel | QLabel
- Text: Visible segments only: 
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: SizeScaleSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Adjust the exported model size. Point coordinates in the exported model will be multiplied by this number. By default Slicer uses millimeter unit for coordinates. | SizeScaleSpinBox | ctkDoubleSpinBox
- Tooltip: Adjust the exported model size. Point coordinates in the exported model will be multiplied by this number. By default Slicer uses millimeter unit for coordinates.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:190: d->SizeScaleSpinBox->setValue(settings.value(d->SettingsKey + "/SizeScale", 1.0).toDouble());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:214: settings.setValue(d->SettingsKey + "/SizeScale", d->SizeScaleSpinBox->value());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:261: d->SizeScaleSpinBox->value(),`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:360: d->SizeScaleSpinBox->setEnabled(formatIsModel);`

## widget: UseColorTableValuesCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: UseColorTableValuesCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:88: QObject::connect(this->UseColorTableValuesCheckBox, SIGNAL(toggled(bool)), q, SLOT(setUseLabelsFromColorNode(bool)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:277: if (d->UseColorTableValuesCheckBox->isChecked())`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:362: d->UseColorTableValuesCheckBox->setEnabled(!formatIsModel);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:363: d->ColorTableNodeSelector->setEnabled(!formatIsModel && d->UseColorTableValuesCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:371: d->ColorTableNodeSelector->setEnabled(d->UseColorTableValuesCheckBox->isEnabled() && d->UseColorTableValuesCheckBox->isChecked());`
- Connected slots/functions: `setUseLabelsFromColorNode`
- API footprints: `vtkMRMLColorTableNode::SafeDownCast`

## widget: ColorTableNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ColorTableNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:87: QObject::connect(this->ColorTableNodeSelector, SIGNAL(currentNodeIDChanged(const QString&)), q, SLOT(setColorNodeID(const QString&)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:164: d->ColorTableNodeSelector->setCurrentNode(exportColorTableNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:279: labelmapConversionColorTableNode = vtkMRMLColorTableNode::SafeDownCast(d->ColorTableNodeSelector->currentNode());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:363: d->ColorTableNodeSelector->setEnabled(!formatIsModel && d->UseColorTableValuesCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:371: d->ColorTableNodeSelector->setEnabled(d->UseColorTableValuesCheckBox->isEnabled() && d->UseColorTableValuesCheckBox->isChecked());`
- Connected slots/functions: `setColorNodeID`
- API footprints: `GetLabelmapConversionColorTableNode`, `GetLabelmapConversionColorTableNodeID`, `SetLabelmapConversionColorTableNodeID`, `vtkMRMLColorTableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLColorTableNode"]}

## widget: DestinationFoldeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Destination folder:  | DestinationFoldeLabel | QLabel
- Text: Destination folder: 
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: CoordinateSystemComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Output model XYZ axes are mapped to LPS (left-posterior-superior) or RAS (right-anterior-superior) patient axis directions. LPS is used more commonly. | CoordinateSystemComboBox | QComboBox
- Tooltip: Output model XYZ axes are mapped to LPS (left-posterior-superior) or RAS (right-anterior-superior) patient axis directions. LPS is used more commonly.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:194: d->CoordinateSystemComboBox->setCurrentIndex(d->CoordinateSystemComboBox->findText(coordinateSystem));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:216: settings.setValue(d->SettingsKey + "/CoordinateSystem", d->CoordinateSystemComboBox->currentText());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:260: d->CoordinateSystemComboBox->currentText() == "LPS",`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:358: d->CoordinateSystemComboBox->setEnabled(formatIsModel);`
- API footprints: `GetPointer`

## widget: UseColorTableValuesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use color table values: | UseColorTableValuesLabel | QLabel
- Text: Use color table values:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: FileFormatLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: File format: | FileFormatLabel | QLabel
- Text: File format:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: CoordinateSystemLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Coordinate system:  | CoordinateSystemLabel | QLabel
- Text: Coordinate system: 
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: VisibleSegmentsOnlyCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Only export those segments that are currently visible. | VisibleSegmentsOnlyCheckBox | QCheckBox
- Tooltip: Only export those segments that are currently visible.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:185: d->VisibleSegmentsOnlyCheckBox->setChecked(settings.value(d->SettingsKey + "/VisibleSegmentsOnly", false).toBool());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:212: settings.setValue(d->SettingsKey + "/VisibleSegmentsOnly", d->VisibleSegmentsOnlyCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:242: if (d->VisibleSegmentsOnlyCheckBox->isChecked() //`
- API footprints: `GetDisplayNode`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`

## widget: MergeIntoSingleFileLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Merge into single file: | MergeIntoSingleFileLabel | QLabel
- Text: Merge into single file:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: ExportToFilesButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Export | ExportToFilesButton | QPushButton
- Text: Export
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:84: QObject::connect(this->ExportToFilesButton, SIGNAL(clicked()), q, SLOT(exportToFiles()));`
- Connected slots/functions: `exportToFiles`
- API footprints: `GetDisplayNode`, `GetPointer`, `GetVisibleSegmentIDs`, `vtkMRMLColorTableNode::SafeDownCast`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`, `vtkMRMLVolumeNode::SafeDownCast`

## widget: ShowDestinationFolderOnExportCompleteCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Open destination folder when export is completed. | ShowDestinationFolderOnExportCompleteCheckBox | QCheckBox
- Tooltip: Open destination folder when export is completed.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:191: d->ShowDestinationFolderOnExportCompleteCheckBox->setChecked(settings.value(d->SettingsKey + "/ShowDestinationFolderOnExportComplete", true).toBool());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:215: settings.setValue(d->SettingsKey + "/ShowDestinationFolderOnExportComplete", d->ShowDestinationFolderOnExportCompleteCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:314: if (d->ShowDestinationFolderOnExportCompleteCheckBox->isChecked())`
- Key UI properties: {"checked": "true"}

## widget: DestinationFolderButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkDirectoryButton`
- Search text: DestinationFolderButton | ctkDirectoryButton
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:85: QObject::connect(this->ShowDestinationFolderButton, SIGNAL(clicked()), q, SLOT(showDestinationFolder()));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:184: d->DestinationFolderButton->setDirectory(path);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:210: QString path = qSlicerCoreApplication::application()->toSlicerHomeRelativePath(d->DestinationFolderButton->directory());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:256: vtkSlicerSegmentationsModuleLogic::ExportSegmentsClosedSurfaceRepresentationToFiles(d->DestinationFolderButton->directory().toUtf8().constData(),`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:302: vtkSlicerSegmentationsModuleLogic::ExportSegmentsBinaryLabelmapRepresentationToFiles(d->DestinationFolderButton->directory().toUtf8().constData(),`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:326: QDesktopServices::openUrl(QUrl("file:///" + d->DestinationFolderButton->directory(), QUrl::TolerantMode));`
- Connected slots/functions: `showDestinationFolder`
- API footprints: `GetPointer`

## widget: ShowDestinationFolderButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Browse to destination folder | ShowDestinationFolderButton | QToolButton
- Tooltip: Browse to destination folder
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:85: QObject::connect(this->ShowDestinationFolderButton, SIGNAL(clicked()), q, SLOT(showDestinationFolder()));`
- Connected slots/functions: `showDestinationFolder`

## widget: SizeScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Size scale: | SizeScaleLabel | QLabel
- Text: Size scale:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: MergeIntoSingleOBJFileCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Export all segments to a single OBJ file. It is always enabled for OBJ files, as segments can be distinguished based on their material. | MergeIntoSingleOBJFileCheckBox | QCheckBox
- Tooltip: Export all segments to a single OBJ file. It is always enabled for OBJ files, as segments can be distinguished based on their material.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:188: d->MergeIntoSingleOBJFileCheckBox->setChecked(settings.value(d->SettingsKey + "/MergeIntoSingleFile", false).toBool());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:355: d->MergeIntoSingleOBJFileCheckBox->setVisible(!formatIsSTL);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:356: d->MergeIntoSingleOBJFileCheckBox->setEnabled(formatIsModel);`
- Key UI properties: {"checked": "true"}

## widget: MergeIntoSingleSTLFileCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Export all segments to a single output STL file. | MergeIntoSingleSTLFileCheckBox | QCheckBox
- Tooltip: Export all segments to a single output STL file.
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:187: d->MergeIntoSingleSTLFileCheckBox->setChecked(settings.value(d->SettingsKey + "/MergeIntoSingleFile", false).toBool());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:213: settings.setValue(d->SettingsKey + "/MergeIntoSingleFile", d->MergeIntoSingleSTLFileCheckBox->isChecked());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:251: bool merge = d->MergeIntoSingleSTLFileCheckBox->isChecked(); // merge is only used for STL format`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:352: d->MergeIntoSingleSTLFileCheckBox->setVisible(formatIsSTL);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:353: d->MergeIntoSingleSTLFileCheckBox->setEnabled(formatIsModel);`

## widget: UseCompressionCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: UseCompressionCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:270: if (d->UseCompressionCheckBox->isChecked())`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:306: d->UseCompressionCheckBox->isChecked(),`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:361: d->UseCompressionCheckBox->setEnabled(!formatIsModel);`
- API footprints: `GetPointer`

## widget: FileFormatComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: FileFormatComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:86: QObject::connect(this->FileFormatComboBox, SIGNAL(currentIndexChanged(const QString&)), q, SLOT(setFileFormat(const QString&)));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:180: d->FileFormatComboBox->setCurrentIndex(d->FileFormatComboBox->findText(fileFormat));`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:209: settings.setValue(d->SettingsKey + "/FileFormat", d->FileFormatComboBox->currentText());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:253: QString fileFormat = d->FileFormatComboBox->currentText();`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:259: d->FileFormatComboBox->currentText().toUtf8().constData(),`
- Connected slots/functions: `setFileFormat`
- API footprints: `GetPointer`

## widget: UseCompressionLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use compression: | UseCompressionLabel | QLabel
- Text: Use compression:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: ShowDestinationFolderOnExportCompleteLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show destination folder: | ShowDestinationFolderOnExportCompleteLabel | QLabel
- Text: Show destination folder:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: ReferenceVolumeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Reference volume: | ReferenceVolumeLabel | QLabel
- Text: Reference volume:
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`

## widget: ReferenceVolumeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: ReferenceVolumeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:229: d->ReferenceVolumeComboBox->setCurrentNode(referenceVolumeNode);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:282: vtkMRMLVolumeNode* referenceVolumeNode = vtkMRMLVolumeNode::SafeDownCast(d->ReferenceVolumeComboBox->currentNode());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationFileExportWidget.cxx:359: d->ReferenceVolumeComboBox->setEnabled(!formatIsModel);`
- API footprints: `GetNodeReference`, `vtkMRMLSegmentationNode::GetReferenceImageGeometryReferenceRole`, `vtkMRMLVolumeNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLVolumeNode"]}
