# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLSliceInformationWidget.ui

- Owner class: `qMRMLSliceInformationWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLSliceInformationWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSliceInformationWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSliceInformationWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:27: #include "qMRMLSliceInformationWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:36: qMRMLSliceInformationWidgetPrivate::qMRMLSliceInformationWidgetPrivate(qMRMLSliceInformationWidget& object)`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:43: qMRMLSliceInformationWidgetPrivate::~qMRMLSliceInformationWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:46: void qMRMLSliceInformationWidgetPrivate::setupUi(qMRMLWidget* widget)`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:48: Q_Q(qMRMLSliceInformationWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:50: this->Ui_qMRMLSliceInformationWidget::setupUi(widget);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:55: this->connect(this->SliceOrientationSelector, &QComboBox::currentTextChanged, q, &qMRMLSliceInformationWidget::setSliceOrientation);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:78: void qMRMLSliceInformationWidgetPrivate::updateWidgetFromMRMLSliceNode()`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:80: Q_Q(qMRMLSliceInformationWidget);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:88: // qDebug() << "qMRMLSliceInformationWidgetPrivate::updateWidgetFromMRMLSliceNode";`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:138: qMRMLSliceInformationWidget::qMRMLSliceInformationWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:140: , d_ptr(new qMRMLSliceInformationWidgetPrivate(*this))`
- Connected slots/functions: `currentTextChanged`, `setSliceOrientation`
- API footprints: `SetOrientation`, `vtkMRMLSliceNode::AutomaticSliceSpacingMode`, `vtkMRMLSliceNode::SafeDownCast`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Layout Name: | label_2 | QLabel
- Text: Layout Name:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: LayoutNameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Name of the slice | LayoutNameLineEdit | QLineEdit
- Tooltip: Name of the slice
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:91: this->LayoutNameLineEdit->setText(QString::fromUtf8(this->MRMLSliceNode->GetLayoutName()));`
- API footprints: `GetLayoutName`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Orientation: | label_3 | QLabel
- Text: Orientation:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: SliceOrientationSelector

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Slice orientation (Axial, Sagittal, Coronal, Reformat) | SliceOrientationSelector | QComboBox
- Tooltip: Slice orientation (Axial, Sagittal, Coronal, Reformat)
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:26: #include "qMRMLSliceControllerWidget_p.h" // For updateSliceOrientationSelector`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:55: this->connect(this->SliceOrientationSelector, &QComboBox::currentTextChanged, q, &qMRMLSliceInformationWidget::setSliceOrientation);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:93: qMRMLSliceControllerWidgetPrivate::updateSliceOrientationSelector(this->MRMLSliceNode, this->SliceOrientationSelector);`
- Connected slots/functions: `currentTextChanged`, `setSliceOrientation`
- API footprints: `GetLayoutName`, `SetOrientation`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice visibility: | label_4 | QLabel
- Text: Slice visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: SliceVisibilityToggle

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Toggle the visibility of the slice in the 3D scene | SliceVisibilityToggle | QToolButton
- Text: ...
- Tooltip: Toggle the visibility of the slice in the 3D scene
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:58: this->connect(this->SliceVisibilityToggle, SIGNAL(clicked(bool)), q, SLOT(setSliceVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:96: this->SliceVisibilityToggle->setChecked(this->MRMLSliceNode->GetSliceVisible());`
- Connected slots/functions: `setSliceVisible`
- API footprints: `GetSliceVisible`, `SetSliceVisible`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Widget visibility: | label_5 | QLabel
- Text: Widget visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: WidgetVisibilityToggle

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Toggle the visibility of the reformat widget in the 3D scene | WidgetVisibilityToggle | QToolButton
- Text: ...
- Tooltip: Toggle the visibility of the reformat widget in the 3D scene
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:61: this->connect(this->WidgetVisibilityToggle, SIGNAL(clicked(bool)), q, SLOT(setWidgetVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:99: this->WidgetVisibilityToggle->setChecked(this->MRMLSliceNode->GetWidgetVisible());`
- Connected slots/functions: `setWidgetVisible`
- API footprints: `GetWidgetVisible`, `SetWidgetVisible`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: label_6

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Dimension: | Dimension of the slice. | label_6 | QLabel
- Text: Dimension:
- Tooltip: Dimension of the slice.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: DimensionWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkCoordinatesWidget`
- Search text: DimensionWidget | ctkCoordinatesWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:108: this->DimensionWidget->setCoordinates(coordinatesInDouble);`

## widget: label_7

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Field of view: | Field of view of slice | label_7 | QLabel
- Text: Field of view:
- Tooltip: Field of view of slice
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: FieldOfViewWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkCoordinatesWidget`
- Search text: FieldOfViewWidget | ctkCoordinatesWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:116: this->FieldOfViewWidget->setCoordinates(coordinatesInDouble);`
- API footprints: `GetViewGroup`

## widget: label_9

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice spacing mode: | Slice spacing may be set automatically or manually by the user or context | label_9 | QLabel
- Text: Slice spacing mode:
- Tooltip: Slice spacing may be set automatically or manually by the user or context
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: AutomaticSliceSpacingRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Automatic | AutomaticSliceSpacingRadioButton | QRadioButton
- Text: Automatic
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:69: this->SliceSpacingModeGroup->addButton(this->AutomaticSliceSpacingRadioButton, vtkMRMLSliceNode::AutomaticSliceSpacingMode);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:123: this->AutomaticSliceSpacingRadioButton->setChecked(true);`
- API footprints: `GetSliceSpacingMode`, `vtkMRMLSliceNode::AutomaticSliceSpacingMode`, `vtkMRMLSliceNode::PrescribedSliceSpacingMode`
- Key UI properties: {"checked": "true"}

## widget: PrescribedSliceSpacingRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Manual | PrescribedSliceSpacingRadioButton | QRadioButton
- Text: Manual
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:70: this->SliceSpacingModeGroup->addButton(this->PrescribedSliceSpacingRadioButton, vtkMRMLSliceNode::PrescribedSliceSpacingMode);`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:127: this->PrescribedSliceSpacingRadioButton->setChecked(true);`
- Connected slots/functions: `setEnabled`
- Declared UI connections: `toggled(bool) -> label_10.setEnabled(bool)`; `toggled(bool) -> PrescribedSpacingSpinBox.setEnabled(bool)`
- API footprints: `GetPrescribedSliceSpacing`, `GetSliceSpacingMode`, `vtkMRMLSliceNode::AutomaticSliceSpacingMode`, `vtkMRMLSliceNode::PrescribedSliceSpacingMode`

## widget: label_10

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Manual spacing: | label_10 | QLabel
- Text: Manual spacing:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: PrescribedSpacingSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: Manual spacing is used when slice spacing is set manually by the user or context | PrescribedSpacingSpinBox | ctkDoubleSpinBox
- Tooltip: Manual spacing is used when slice spacing is set manually by the user or context
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:74: this->connect(this->PrescribedSpacingSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setPrescribedSliceSpacing(double)));`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:130: this->PrescribedSpacingSpinBox->setValue(prescribedSpacing[2]);`
- Connected slots/functions: `setPrescribedSliceSpacing`
- API footprints: `GetPrescribedSliceSpacing`, `SetPrescribedSliceSpacing`

## widget: label_11

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View group: | label_11 | QLabel
- Text: View group:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`

## widget: ViewGroupSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: Navigation and linked properties are synchronized in views that has the same group index. | ViewGroupSpinBox | QSpinBox
- Tooltip: Navigation and linked properties are synchronized in views that has the same group index.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget.h`, `Libs/MRML/Widgets/qMRMLSliceInformationWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:65: this->connect(this->ViewGroupSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setViewGroup(int)));`
  - `Libs/MRML/Widgets/qMRMLSliceInformationWidget.cxx:118: this->ViewGroupSpinBox->setValue(this->MRMLSliceNode->GetViewGroup());`
- Connected slots/functions: `setViewGroup`
- API footprints: `GetViewGroup`, `SetViewGroup`
