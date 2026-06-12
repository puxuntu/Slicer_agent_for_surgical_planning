# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLVolumeInfoWidget.ui

- Owner class: `qMRMLVolumeInfoWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLVolumeInfoWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLVolumeInfoWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLVolumeInfoWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:28: #include "qMRMLVolumeInfoWidget.h"`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:29: #include "ui_qMRMLVolumeInfoWidget.h"`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:48: class qMRMLVolumeInfoWidgetPrivate : public Ui_qMRMLVolumeInfoWidget`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:50: Q_DECLARE_PUBLIC(qMRMLVolumeInfoWidget);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:53: qMRMLVolumeInfoWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:56: qMRMLVolumeInfoWidgetPrivate(qMRMLVolumeInfoWidget& object);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:63: qMRMLVolumeInfoWidgetPrivate::qMRMLVolumeInfoWidgetPrivate(qMRMLVolumeInfoWidget& object)`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:69: void qMRMLVolumeInfoWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:71: Q_Q(qMRMLVolumeInfoWidget);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:110: qMRMLVolumeInfoWidget::qMRMLVolumeInfoWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:112: , d_ptr(new qMRMLVolumeInfoWidgetPrivate(*this))`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:114: Q_D(qMRMLVolumeInfoWidget);`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ImageOriginWidget.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> ImageSpacingWidget.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetImageData`, `GetScalarVolumeDisplayNode`, `vtkMRMLScalarVolumeNode::SafeDownCast`, `vtkMRMLVolumeNode::ImageDataModifiedEvent`, `vtkMRMLVolumeNode::SafeDownCast`

## widget: ImageDimensionsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Image Dimensions: | ImageDimensionsLabel | QLabel
- Text: Image Dimensions:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: ImageDimensionsWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkCoordinatesWidget`
- Search text: ImageDimensionsWidget | ctkCoordinatesWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:173: d->ImageDimensionsWidget->setCoordinates(dimensions);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:215: d->ImageDimensionsWidget->setCoordinates(dimensions);`
- API footprints: `GetSpacing`

## widget: ImageSpacingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Image Spacing: | ImageSpacingLabel | QLabel
- Text: Image Spacing:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: ImageSpacingWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: ImageSpacingWidget | qMRMLCoordinatesWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:88: QObject::connect(this->ImageSpacingWidget, SIGNAL(coordinatesChanged(double*)), q, SLOT(setImageSpacing(double*)));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:176: d->ImageSpacingWidget->setCoordinates(spacing);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:218: d->ImageSpacingWidget->setCoordinates(spacing);`
- Connected slots/functions: `setImageSpacing`
- API footprints: `GetOrigin`, `GetSpacing`, `SetSpacing`

## widget: ImageOriginLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Image Origin: | ImageOriginLabel | QLabel
- Text: Image Origin:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: ImageOriginWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCoordinatesWidget`
- Search text: ImageOriginWidget | qMRMLCoordinatesWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:89: QObject::connect(this->ImageOriginWidget, SIGNAL(coordinatesChanged(double*)), q, SLOT(setImageOrigin(double*)));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:179: d->ImageOriginWidget->setCoordinates(origin);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:221: d->ImageOriginWidget->setCoordinates(origin);`
- Connected slots/functions: `setImageOrigin`
- API footprints: `GetOrigin`, `SetOrigin`

## widget: IJKToRASDirectionLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: IJK to RAS Direction Matrix: | IJKToRASDirectionLabel | QLabel
- Text: IJK to RAS Direction Matrix:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: IJKToRASDirectionMatrixWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkMatrixWidget`
- Search text: IJKToRASDirectionMatrixWidget | ctkMatrixWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:186: d->IJKToRASDirectionMatrixWidget->setValue(i, j, i == j ? 1. : 0.);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:229: d->IJKToRASDirectionMatrixWidget->setValue(i, j, IJKToRASDirections[i][j]);`

## widget: CenterVolumePushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Center Volume | Set a parent transform to the volume that center it on the origin. Harden the transform to permanently change the volume position. | CenterVolumePushButton | QPushButton
- Text: Center Volume
- Tooltip: Set a parent transform to the volume that center it on the origin. Harden the transform to permanently change the volume position.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:90: QObject::connect(this->CenterVolumePushButton, SIGNAL(clicked()), q, SLOT(center()));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:233: d->CenterVolumePushButton->setEnabled(!this->isCentered());`
- Connected slots/functions: `center`
- API footprints: `AddCenteringTransform`

## widget: ScanOrderLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scan Order: | ScanOrderLabel | QLabel
- Text: Scan Order:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: ScanOrderValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: ScanOrderValueLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:151: d->ScanOrderValueLabel->setVisible(!enable);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:193: d->ScanOrderValueLabel->setText("");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:238: d->ScanOrderValueLabel->setText(d->ScanOrderComboBox->currentText());`
- API footprints: `GetIJKToRASMatrix`, `GetPointer`, `vtkMRMLVolumeNode::ComputeScanOrderFromIJKToRAS`

## widget: ScanOrderComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: ScanOrderComboBox | QComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:80: this->ScanOrderComboBox->addItem("Sagittal LR", "LR");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:81: this->ScanOrderComboBox->addItem("Sagittal RL", "RL");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:82: this->ScanOrderComboBox->addItem("Coronal PA", "PA");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:83: this->ScanOrderComboBox->addItem("Coronal AP", "AP");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:84: this->ScanOrderComboBox->addItem("Axial IS", "IS");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:85: this->ScanOrderComboBox->addItem("Axial SI", "SI");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:99: QObject::connect(this->ScanOrderComboBox, SIGNAL(activated(int)), q, SLOT(setScanOrder(int)));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:150: d->ScanOrderComboBox->setVisible(enable);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:162: return d->ScanOrderComboBox->isVisible();`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:192: d->ScanOrderComboBox->setCurrentIndex(-1);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:237: d->ScanOrderComboBox->setCurrentIndex(d->ScanOrderComboBox->findData(vtkMRMLVolumeNode::ComputeScanOrderFromIJKToRAS(mat.GetPointer())));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:238: d->ScanOrderValueLabel->setText(d->ScanOrderComboBox->currentText());`
- Connected slots/functions: `setScanOrder`
- API footprints: `GetDimensions`, `GetIJKToRASMatrix`, `GetImageData`, `GetOrigin`, `GetPointer`, `GetSpacing`, `SetElement`, `SetIJKToRASMatrix`, `vtkMRMLVolumeNode::ComputeIJKToRASFromScanOrder`, `vtkMRMLVolumeNode::ComputeScanOrderFromIJKToRAS`

## widget: NumberOfScalarsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of Scalars: | NumberOfScalarsLabel | QLabel
- Text: Number of Scalars:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: NumberOfScalarsValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: NumberOfScalarsValueLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:153: d->NumberOfScalarsValueLabel->setVisible(!enable);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:196: d->NumberOfScalarsValueLabel->setText("");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:243: d->NumberOfScalarsValueLabel->setText(QString::number(image->GetNumberOfScalarComponents()));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:253: d->NumberOfScalarsValueLabel->setText("");`
- API footprints: `GetNumberOfScalarComponents`, `GetScalarType`

## widget: NumberOfScalarsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: NumberOfScalarsSpinBox | QSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:100: QObject::connect(this->NumberOfScalarsSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setNumberOfScalars(int)));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:152: d->NumberOfScalarsSpinBox->setVisible(enable);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:195: d->NumberOfScalarsSpinBox->setValue(1);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:242: d->NumberOfScalarsSpinBox->setValue(image->GetNumberOfScalarComponents());`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:252: d->NumberOfScalarsSpinBox->setValue(1);`
- Connected slots/functions: `setNumberOfScalars`
- API footprints: `GetImageData`, `GetNumberOfScalarComponents`, `GetOutputInformation`, `GetScalarType`, `SetOutput`

## widget: ScalarTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar Type: | ScalarTypeLabel | QLabel
- Text: Scalar Type:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: ScalarTypeValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: ScalarTypeValueLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:155: d->ScalarTypeValueLabel->setVisible(!enable);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:199: d->ScalarTypeValueLabel->setText("");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:245: d->ScalarTypeValueLabel->setText(d->ScalarTypeComboBox->currentText());`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:255: d->ScalarTypeValueLabel->setText("");`
- API footprints: `GetNumberOfScalarComponents`, `GetScalarRange`, `GetScalarType`

## widget: ScalarTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: ScalarTypeComboBox | QComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:77: this->ScalarTypeComboBox->addItem(vtkImageScalarTypeNameMacro(i), i);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:101: QObject::connect(this->ScalarTypeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(setScalarType(int)));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:154: d->ScalarTypeComboBox->setVisible(enable);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:198: d->ScalarTypeComboBox->setCurrentIndex(-1);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:244: d->ScalarTypeComboBox->setCurrentIndex(d->ScalarTypeComboBox->findData(image->GetScalarType()));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:245: d->ScalarTypeValueLabel->setText(d->ScalarTypeComboBox->currentText());`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:254: d->ScalarTypeComboBox->setCurrentIndex(-1);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:393: int type = d->ScalarTypeComboBox->itemData(index).toInt();`
- Connected slots/functions: `setScalarType`
- API footprints: `GetImageData`, `GetNumberOfScalarComponents`, `GetOutputInformation`, `GetScalarRange`, `GetScalarType`, `SetOutput`

## widget: ScalarRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar Range: | ScalarRangeLabel | QLabel
- Text: Scalar Range:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: ScalarRangeValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: ScalarRangeValueLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:190: d->ScalarRangeValueLabel->setText("");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:248: d->ScalarRangeValueLabel->setText(QString("%1 to %2").arg(scalarRange[0]).arg(scalarRange[1]));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:256: d->ScalarRangeValueLabel->setText("");`
- API footprints: `GetScalarRange`

## widget: VolumeTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Volume type: | VolumeTypeLabel | QLabel
- Text: Volume type:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: VolumeTagLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: VolumeTag | VolumeTagLabel | QLabel
- Text: VolumeTag
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:203: d->VolumeTagLabel->setText("");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:277: d->VolumeTagLabel->setText(volumeType);`

## widget: FileNameLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: File Name: | FileNameLabel | QLabel
- Text: File Name:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: FileNameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: FileNameLineEdit | QLineEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:201: d->FileNameLineEdit->setText("");`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:260: d->FileNameLineEdit->setText(storageNode ? storageNode->GetFileName() : "");`
- API footprints: `GetFileName`, `GetStorageNode`

## widget: WindowLevelPresetsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Window/Level Presets: | WindowLevelPresetsLabel | QLabel
- Text: Window/Level Presets:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`

## widget: WindowLevelPresetsListWidget

- Confidence: `linked_to_api`
- Widget/action class: `QListWidget`
- Search text: WindowLevelPresetsListWidget | QListWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:102: QObject::connect(this->WindowLevelPresetsListWidget, SIGNAL(itemDoubleClicked(QListWidgetItem*)), q, SLOT(setWindowLevelFromPreset(QListWidgetItem*)));`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:284: d->WindowLevelPresetsListWidget->clear();`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:299: d->WindowLevelPresetsListWidget->addItem(windowLevelPreset);`
  - `Libs/MRML/Widgets/qMRMLVolumeInfoWidget.cxx:410: displayNode->SetWindowLevelFromPreset(d->WindowLevelPresetsListWidget->row(presetItem));`
- Connected slots/functions: `setWindowLevelFromPreset`
- API footprints: `GetLevelPreset`, `GetScalarVolumeDisplayNode`, `GetWindowPreset`, `SetWindowLevelFromPreset`, `vtkMRMLScalarVolumeNode::SafeDownCast`
