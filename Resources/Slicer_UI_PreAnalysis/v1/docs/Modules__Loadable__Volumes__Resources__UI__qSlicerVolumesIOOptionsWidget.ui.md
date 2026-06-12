# Slicer UI Analysis: Modules/Loadable/Volumes/Resources/UI/qSlicerVolumesIOOptionsWidget.ui

- Owner class: `qSlicerVolumesIOOptionsWidget`
- UI file: `Modules/Loadable/Volumes/Resources/UI/qSlicerVolumesIOOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerVolumesIOOptionsWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerVolumesIOOptionsWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:34: #include "qSlicerVolumesIOOptionsWidget.h"`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:35: #include "ui_qSlicerVolumesIOOptionsWidget.h"`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:45: class qSlicerVolumesIOOptionsWidgetPrivate`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:47: , public Ui_qSlicerVolumesIOOptionsWidget`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:53: qSlicerVolumesIOOptionsWidget::qSlicerVolumesIOOptionsWidget(QWidget* parentWidget)`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:54: : qSlicerIOOptionsWidget(new qSlicerVolumesIOOptionsWidgetPrivate, parentWidget)`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:56: Q_D(qSlicerVolumesIOOptionsWidget);`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:77: qSlicerVolumesIOOptionsWidget::~qSlicerVolumesIOOptionsWidget() = default;`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:80: void qSlicerVolumesIOOptionsWidget::updateProperties()`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:82: Q_D(qSlicerVolumesIOOptionsWidget);`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:105: void qSlicerVolumesIOOptionsWidget::setFileName(const QString& fileName)`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:111: void qSlicerVolumesIOOptionsWidget::setFileNames(const QStringList& fileNames)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ColorTableComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetPointer`

## widget: NameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: NameLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:61: connect(d->NameLineEdit, SIGNAL(textChanged(QString)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:83: if (!d->NameLineEdit->text().isEmpty())`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:85: QStringList names = d->NameLineEdit->text().split(';');`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:162: d->NameLineEdit->setText(names.join("; "));`
- Connected slots/functions: `updateProperties`
- API footprints: `GetScene`, `RemoveNode`

## widget: LabelMapCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: LabelMap | Load the volume as a labelmap (each voxel value representing a segmented structure). | LabelMapCheckBox | QCheckBox
- Text: LabelMap
- Tooltip: Load the volume as a labelmap (each voxel value representing a segmented structure).
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:62: connect(d->LabelMapCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:70: connect(d->LabelMapCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateColorSelector()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:96: d->Properties["labelmap"] = d->LabelMapCheckBox->isChecked();`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:164: d->LabelMapCheckBox->setChecked(hasLabelMapName);`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:183: if (d->LabelMapCheckBox->isChecked())`
- Connected slots/functions: `updateColorSelector`, `updateProperties`
- API footprints: `GetColorLogic`, `GetDefaultLabelMapColorNodeID`, `GetDefaultVolumeColorNodeID`

## widget: SingleFileCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Single File | Only load the selected file. The application will not attempt to look for similar files that can make up the complete volume. | SingleFileCheckBox | QCheckBox
- Text: Single File
- Tooltip: Only load the selected file. The application will not attempt to look for similar files that can make up the complete volume.
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:64: connect(d->SingleFileCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:73: d->SingleFileCheckBox->setChecked(true);`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:98: d->Properties["singleFile"] = d->SingleFileCheckBox->isChecked();`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:163: d->SingleFileCheckBox->setChecked(!onlyNumberInName && !onlyNumberInExtension);`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:202: d->SingleFileCheckBox->setChecked(ioProperties["singleFile"].toBool());`
- Connected slots/functions: `updateProperties`

## widget: CenteredCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Centered | Ignore image position information that is specified in the image header. | CenteredCheckBox | QCheckBox
- Text: Centered
- Tooltip: Ignore image position information that is specified in the image header.
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:63: connect(d->CenteredCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:97: d->Properties["center"] = d->CenteredCheckBox->isChecked();`
- Connected slots/functions: `updateProperties`

## widget: OrientationCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Ignore Orientation | Ignore axis orientation information that is specified in the image header. | OrientationCheckBox | QCheckBox
- Text: Ignore Orientation
- Tooltip: Ignore axis orientation information that is specified in the image header.
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:65: connect(d->OrientationCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:99: d->Properties["discardOrientation"] = d->OrientationCheckBox->isChecked();`
- Connected slots/functions: `updateProperties`

## widget: ShowCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show | Show volume in slice viewers after loading is completed. | ShowCheckBox | QCheckBox
- Text: Show
- Tooltip: Show volume in slice viewers after loading is completed.
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:66: connect(d->ShowCheckBox, SIGNAL(toggled(bool)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:100: d->Properties["show"] = d->ShowCheckBox->isChecked();`
- Connected slots/functions: `updateProperties`
- Key UI properties: {"checked": "true"}

## widget: ColorTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: Color table node used to display this volume. | ColorTableComboBox | qMRMLColorTableComboBox
- Tooltip: Color table node used to display this volume.
- Implementation candidates: `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx`, `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:67: connect(d->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(updateProperties()));`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:101: d->Properties["colorNodeID"] = d->ColorTableComboBox->currentNodeID();`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:185: d->ColorTableComboBox->setCurrentNodeID(appLogic->GetColorLogic()->GetDefaultLabelMapColorNodeID());`
  - `Modules/Loadable/Volumes/qSlicerVolumesIOOptionsWidget.cxx:189: d->ColorTableComboBox->setCurrentNodeID(appLogic->GetColorLogic()->GetDefaultVolumeColorNodeID());`
- Connected slots/functions: `updateProperties`
- API footprints: `GetColorLogic`, `GetDefaultLabelMapColorNodeID`, `GetDefaultVolumeColorNodeID`
