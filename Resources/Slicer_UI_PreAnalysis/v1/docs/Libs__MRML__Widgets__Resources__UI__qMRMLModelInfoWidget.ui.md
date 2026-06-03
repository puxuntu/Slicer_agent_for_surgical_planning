# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLModelInfoWidget.ui

- Owner class: `qMRMLModelInfoWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLModelInfoWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLModelInfoWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLModelInfoWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:24: #include "qMRMLModelInfoWidget.h"`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:25: #include "ui_qMRMLModelInfoWidget.h"`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:42: class qMRMLModelInfoWidgetPrivate : public Ui_qMRMLModelInfoWidget`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:44: Q_DECLARE_PUBLIC(qMRMLModelInfoWidget);`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:47: qMRMLModelInfoWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:50: qMRMLModelInfoWidgetPrivate(qMRMLModelInfoWidget& object);`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:60: qMRMLModelInfoWidgetPrivate::qMRMLModelInfoWidgetPrivate(qMRMLModelInfoWidget& object)`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:71: void qMRMLModelInfoWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:73: Q_Q(qMRMLModelInfoWidget);`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:81: qMRMLModelInfoWidget::qMRMLModelInfoWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:83: , d_ptr(new qMRMLModelInfoWidgetPrivate(*this))`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:85: Q_D(qMRMLModelInfoWidget);`
- API footprints: `vtkMRMLModelNode::DisplayModifiedEvent`, `vtkMRMLModelNode::SafeDownCast`

## widget: MeshTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Mesh Type: | MeshTypeLabel | QLabel
- Text: Mesh Type:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: MeshTypeLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: MeshTypeLineEdit | QLineEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:166: d->MeshTypeLineEdit->setText("Surface Mesh (vtkPolyData)");`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:174: d->MeshTypeLineEdit->setText("Volumetric Mesh (vtkUnstructuredGrid)");`
- API footprints: `GetNumberOfLines`, `GetNumberOfVerts`

## widget: SurfaceAreaLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Surface Area: | SurfaceAreaLabel | QLabel
- Text: Surface Area:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: SurfaceAreaDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: SurfaceAreaDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:153: d->SurfaceAreaDoubleSpinBox->setValue(d->MassProperties->GetSurfaceArea());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:158: d->SurfaceAreaDoubleSpinBox->setValue(0);`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:186: d->SurfaceAreaDoubleSpinBox->setValue(0.);`
- API footprints: `GetNumberOfCells`, `GetOutput`, `GetSurfaceArea`, `GetVolume`

## widget: VolumeAreaLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Volume: | VolumeAreaLabel | QLabel
- Text: Volume:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: VolumeAreaDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: VolumeAreaDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:154: d->VolumeAreaDoubleSpinBox->setValue(d->MassProperties->GetVolume());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:159: d->VolumeAreaDoubleSpinBox->setValue(0);`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:187: d->VolumeAreaDoubleSpinBox->setValue(0.);`
- API footprints: `GetSurfaceArea`, `GetVolume`

## widget: NumberOfPointsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of Points: | NumberOfPointsLabel | QLabel
- Text: Number of Points:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: NumberOfPointsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: NumberOfPointsSpinBox | QSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:162: d->NumberOfPointsSpinBox->setValue(mesh->GetNumberOfPoints());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:189: d->NumberOfPointsSpinBox->setValue(0);`
- API footprints: `GetNumberOfCells`, `GetNumberOfPoints`

## widget: NumberOfPointsScalarsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of Points Scalars: | NumberOfPointsScalarsLabel | QLabel
- Text: Number of Points Scalars:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: NumberOfPointsScalarsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: NumberOfPointsScalarsSpinBox | QSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:181: d->NumberOfPointsScalarsSpinBox->setValue(mesh->GetPointData()->GetNumberOfComponents());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:196: d->NumberOfPointsScalarsSpinBox->setValue(0);`
- API footprints: `GetCellData`, `GetMaxCellSize`, `GetNumberOfComponents`, `GetPointData`

## widget: NumberOfCellsScalarsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of Cells Scalars: | NumberOfCellsScalarsLabel | QLabel
- Text: Number of Cells Scalars:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: NumberOfCellsScalarsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: NumberOfCellsScalarsSpinBox | QSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:182: d->NumberOfCellsScalarsSpinBox->setValue(mesh->GetCellData()->GetNumberOfComponents());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:197: d->NumberOfCellsScalarsSpinBox->setValue(0);`
- API footprints: `GetCellData`, `GetMaxCellSize`, `GetNumberOfComponents`, `GetPointData`

## widget: FileNameLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Filename: | FileNameLabel | QLabel
- Text: Filename:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: FileNameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: FileNameLineEdit | QLineEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:203: d->FileNameLineEdit->setText(storageNode->GetFileName());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:207: d->FileNameLineEdit->setText("");`
- API footprints: `GetFileName`

## widget: NumberOfCellsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: NumberOfCellsSpinBox | QSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:163: d->NumberOfCellsSpinBox->setValue(mesh->GetNumberOfCells());`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:190: d->NumberOfCellsSpinBox->setValue(0);`
- API footprints: `GetNumberOfCells`, `GetNumberOfPoints`

## widget: ExpandButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkExpandButton`
- Search text: ExpandButton | ctkExpandButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:75: this->ExpandButton->setOrientation(Qt::Vertical);`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:76: this->ExpandButton->setChecked(false);`
- Key UI properties: {"checked": "true"}

## widget: widget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: widget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:119: // Update the widget, now that it becomes becomes visible`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:120: // (we might have missed some updates, because widget contents is not updated`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:121: // if the widget is not visible).`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:132: // so if the widget is not visible then do not update`

## widget: NumberOfVertsValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | NumberOfVertsValueLabel | QLabel
- Text: 0
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:167: d->NumberOfVertsValueLabel->setText(QString::number(poly->GetNumberOfVerts()));`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:175: d->NumberOfVertsValueLabel->setText("0");`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:191: d->NumberOfVertsValueLabel->setText("0");`
- API footprints: `GetNumberOfLines`, `GetNumberOfPolys`, `GetNumberOfVerts`

## widget: NumberOfVertsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Verts | NumberOfVertsLabel | QLabel
- Text: Verts
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: NumberOfLinesValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | NumberOfLinesValueLabel | QLabel
- Text: 0
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:168: d->NumberOfLinesValueLabel->setText(QString::number(poly->GetNumberOfLines()));`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:176: d->NumberOfLinesValueLabel->setText("0");`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:192: d->NumberOfLinesValueLabel->setText("0");`
- API footprints: `GetNumberOfLines`, `GetNumberOfPolys`, `GetNumberOfStrips`, `GetNumberOfVerts`

## widget: NumberOfLinesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Lines | NumberOfLinesLabel | QLabel
- Text: Lines
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: NumberOfPolysValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | NumberOfPolysValueLabel | QLabel
- Text: 0
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:169: d->NumberOfPolysValueLabel->setText(QString::number(poly->GetNumberOfPolys()));`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:177: d->NumberOfPolysValueLabel->setText("0");`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:193: d->NumberOfPolysValueLabel->setText("0");`
- API footprints: `GetNumberOfLines`, `GetNumberOfPolys`, `GetNumberOfStrips`, `GetNumberOfVerts`

## widget: NumberOfStripsValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | NumberOfStripsValueLabel | QLabel
- Text: 0
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:170: d->NumberOfStripsValueLabel->setText(QString::number(poly->GetNumberOfStrips()));`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:178: d->NumberOfStripsValueLabel->setText("0");`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:194: d->NumberOfStripsValueLabel->setText("0");`
- API footprints: `GetMaxCellSize`, `GetNumberOfLines`, `GetNumberOfPolys`, `GetNumberOfStrips`

## widget: NumberOfPolysLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Polys | NumberOfPolysLabel | QLabel
- Text: Polys
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: NumberOfStripsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Strips | NumberOfStripsLabel | QLabel
- Text: Strips
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: MaxCellSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Max cell size | MaxCellSizeLabel | QLabel
- Text: Max cell size
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`

## widget: MaxCellSizeValueLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: 0 | MaxCellSizeValueLabel | QLabel
- Text: 0
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:180: d->MaxCellSizeValueLabel->setText(QString::number(mesh->GetMaxCellSize()));`
  - `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx:195: d->MaxCellSizeValueLabel->setText("0");`
- API footprints: `GetCellData`, `GetMaxCellSize`, `GetNumberOfComponents`, `GetPointData`

## widget: NumberOfCellsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of Cells: | NumberOfCellsLabel | QLabel
- Text: Number of Cells:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLModelInfoWidget.cxx`, `Libs/MRML/Widgets/qMRMLModelInfoWidget.h`
