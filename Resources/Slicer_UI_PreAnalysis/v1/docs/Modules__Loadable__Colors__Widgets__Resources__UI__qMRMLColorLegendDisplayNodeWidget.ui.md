# Slicer UI Analysis: Modules/Loadable/Colors/Widgets/Resources/UI/qMRMLColorLegendDisplayNodeWidget.ui

- Owner class: `qMRMLColorLegendDisplayNodeWidget`
- UI file: `Modules/Loadable/Colors/Widgets/Resources/UI/qMRMLColorLegendDisplayNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLColorLegendDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLColorLegendDisplayNodeWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:41: #include "qMRMLColorLegendDisplayNodeWidget.h"`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:42: #include "ui_qMRMLColorLegendDisplayNodeWidget.h"`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:45: class qMRMLColorLegendDisplayNodeWidgetPrivate`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:47: , public Ui_qMRMLColorLegendDisplayNodeWidget`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:49: Q_DECLARE_PUBLIC(qMRMLColorLegendDisplayNodeWidget);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:52: qMRMLColorLegendDisplayNodeWidget* const q_ptr;`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:56: qMRMLColorLegendDisplayNodeWidgetPrivate(qMRMLColorLegendDisplayNodeWidget& object);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:57: virtual void setupUi(qMRMLColorLegendDisplayNodeWidget*);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:65: qMRMLColorLegendDisplayNodeWidgetPrivate::qMRMLColorLegendDisplayNodeWidgetPrivate(qMRMLColorLegendDisplayNodeWidget& object)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:71: void qMRMLColorLegendDisplayNodeWidgetPrivate::setupUi(qMRMLColorLegendDisplayNodeWidget* widget)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:73: this->Ui_qMRMLColorLegendDisplayNodeWidget::setupUi(widget);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:77: void qMRMLColorLegendDisplayNodeWidgetPrivate::init()`
- API footprints: `vtkMRMLColorLegendDisplayNode::SafeDownCast`

## widget: VisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Visibility: | VisibilityLabel | QLabel
- Text: Visibility:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: ColorLegendVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: ColorLegendVisibilityCheckBox | ctkCheckBox
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:110: QObject::connect(this->ColorLegendVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(onColorLegendVisibilityToggled(bool)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:179: QSignalBlocker blocker1(d->ColorLegendVisibilityCheckBox);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:180: d->ColorLegendVisibilityCheckBox->setChecked(d->ColorLegendDisplayNode->GetVisibility());`
- Connected slots/functions: `onColorLegendVisibilityToggled`
- API footprints: `GetVisibility`, `SetVisibility`

## widget: DisplayedOnViewLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View: | DisplayedOnViewLabel | QLabel
- Text: View:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: DisplayNodeViewComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLDisplayNodeViewComboBox`
- Search text: DisplayNodeViewComboBox | qMRMLDisplayNodeViewComboBox
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:145: d->DisplayNodeViewComboBox->setMRMLDisplayNode(d->ColorLegendDisplayNode);`
- API footprints: `GetTitleTextProperty`

## widget: TitleTextLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Title: | TitleTextLabel | QLabel
- Text: Title:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: TitleTextLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: TitleTextLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:100: QObject::connect(this->TitleTextLineEdit, SIGNAL(textChanged(QString)), q, SLOT(onTitleTextChanged(QString)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:224: QString currentTitle = d->TitleTextLineEdit->text();`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:227: QSignalBlocker blocker10(d->TitleTextLineEdit);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:228: d->TitleTextLineEdit->setText(newTitle.c_str());`
- Connected slots/functions: `onTitleTextChanged`
- API footprints: `GetTitleText`, `SetTitleText`

## widget: LabelTextLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Label text: | LabelTextLabel | QLabel
- Text: Label text:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: UseScalarValueAsLabelTextRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Value | Show numeric value as label text | UseScalarValueAsLabelTextRadioButton | QRadioButton
- Text: Value
- Tooltip: Show numeric value as label text
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:195: QSignalBlocker blocker5(d->UseScalarValueAsLabelTextRadioButton);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:203: d->UseScalarValueAsLabelTextRadioButton->setChecked(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:248: QSignalBlocker blocker15(d->UseScalarValueAsLabelTextRadioButton);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:255: d->UseScalarValueAsLabelTextRadioButton->setChecked(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:309: else if (button == d->UseScalarValueAsLabelTextRadioButton)`
- API footprints: `GetDefaultTextLabelFormat`, `GetUseColorNamesForLabels`, `SetLabelFormat`, `SetUseColorNamesForLabels`
- Key UI properties: {"checked": "true"}

## widget: UseColorNameAsLabelTextRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Color name | Show color name as label text | UseColorNameAsLabelTextRadioButton | QRadioButton
- Text: Color name
- Tooltip: Show color name as label text
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:194: QSignalBlocker blocker4(d->UseColorNameAsLabelTextRadioButton);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:199: d->UseColorNameAsLabelTextRadioButton->setChecked(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:247: QSignalBlocker blocker14(d->UseColorNameAsLabelTextRadioButton);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:251: d->UseColorNameAsLabelTextRadioButton->setChecked(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:304: if (button == d->UseColorNameAsLabelTextRadioButton)`
- API footprints: `GetUseColorNamesForLabels`, `SetUseColorNamesForLabels`

## widget: NumberOfLabelsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of labels: | NumberOfLabelsLabel | QLabel
- Text: Number of labels:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: NumberOfLabelsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: Number of labels to display. Only applicable if values are used as label text (not color name). | NumberOfLabelsSpinBox | QSpinBox
- Tooltip: Number of labels to display. Only applicable if values are used as label text (not color name).
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:107: QObject::connect(this->NumberOfLabelsSpinBox, SIGNAL(valueChanged(int)), q, SLOT(onNumberOfLabelsChanged(int)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:210: d->NumberOfLabelsSpinBox->setEnabled(!useColorNamesForLabels);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:242: QSignalBlocker blocker13(d->NumberOfLabelsSpinBox);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:244: d->NumberOfLabelsSpinBox->setValue(d->ColorLegendDisplayNode->GetNumberOfLabels());`
- Connected slots/functions: `onNumberOfLabelsChanged`
- API footprints: `GetMaxNumberOfColors`, `GetNumberOfLabels`, `SetNumberOfLabels`

## widget: MaxNumberOfColorsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of colors: | MaxNumberOfColorsLabel | QLabel
- Text: Number of colors:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: MaxNumberOfColorsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: Maximum number of colors displayed. Reduce the number to see discrete colors instead of a continuous color gradient. Only applicable if values are used as label text (not color name). | MaxNumberOfColorsSpinBox | QSpinBox
- Tooltip: Maximum number of colors displayed. Reduce the number to see discrete colors instead of a continuous color gradient. Only applicable if values are used as label text (not color name).
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:106: QObject::connect(this->MaxNumberOfColorsSpinBox, SIGNAL(valueChanged(int)), q, SLOT(onMaximumNumberOfColorsChanged(int)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:209: d->MaxNumberOfColorsSpinBox->setEnabled(!useColorNamesForLabels);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:241: QSignalBlocker blocker12(d->MaxNumberOfColorsSpinBox);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:243: d->MaxNumberOfColorsSpinBox->setValue(d->ColorLegendDisplayNode->GetMaxNumberOfColors());`
- Connected slots/functions: `onMaximumNumberOfColorsChanged`
- API footprints: `GetMaxNumberOfColors`, `GetNumberOfLabels`, `SetMaxNumberOfColors`

## widget: ColorLegendOrientationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Orientation: | ColorLegendOrientationLabel | QLabel
- Text: Orientation:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: VerticalOrientationRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Vertical | VerticalOrientationRadioButton | QRadioButton
- Text: Vertical
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:183: QSignalBlocker blocker2(d->VerticalOrientationRadioButton);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:187: d->VerticalOrientationRadioButton->setChecked(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:287: else if (button == d->VerticalOrientationRadioButton)`
- API footprints: `GetOrientation`, `SetOrientation`, `vtkMRMLColorLegendDisplayNode::Horizontal`, `vtkMRMLColorLegendDisplayNode::Vertical`
- Key UI properties: {"checked": "true"}

## widget: HorizontalOrientationRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: Horizontal | HorizontalOrientationRadioButton | QRadioButton
- Text: Horizontal
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:184: QSignalBlocker blocker3(d->HorizontalOrientationRadioButton);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:191: d->HorizontalOrientationRadioButton->setChecked(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:283: if (button == d->HorizontalOrientationRadioButton)`
- API footprints: `GetOrientation`, `SetOrientation`, `vtkMRMLColorLegendDisplayNode::Horizontal`, `vtkMRMLColorLegendDisplayNode::Vertical`

## widget: PositionWithinViewLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Position: | PositionWithinViewLabel | QLabel
- Text: Position:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: H: | Horizontal position of the color legend | label | QLabel
- Text: H:
- Tooltip: Horizontal position of the color legend
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:81: // Set tooltip in label format widget`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:87: - string label annotation: <b>%s</b></body></html>"));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:205: // When using color names for labels then that determines`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:206: // the number of colors and labels (each label is displayed)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:240: // Number of colors and labels`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:353: void qMRMLColorLegendDisplayNodeWidget::onLabelFormatChanged(const QString& labelFormat)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:361: d->ColorLegendDisplayNode->SetLabelFormat(labelFormat.toStdString());`
- API footprints: `SetLabelFormat`

## widget: PositionXSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSlider`
- Search text: Horizontal position of the color legend | PositionXSlider | ctkDoubleSlider
- Tooltip: Horizontal position of the color legend
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:94: QObject::connect(this->PositionXSlider, SIGNAL(valueChanged(double)), q, SLOT(onPositionChanged()));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:217: QSignalBlocker blocker8(d->PositionXSlider);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:219: d->PositionXSlider->setValue(d->ColorLegendDisplayNode->GetPosition()[0]);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:325: d->ColorLegendDisplayNode->SetPosition(d->PositionXSlider->value(), d->PositionYSlider->value());`
- Connected slots/functions: `onPositionChanged`
- API footprints: `GetPosition`, `GetSize`, `SetPosition`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: V: | Vertical position of the color legend | label_2 | QLabel
- Text: V:
- Tooltip: Vertical position of the color legend
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: PositionYSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSlider`
- Search text: Vertical position of the color legend | PositionYSlider | ctkDoubleSlider
- Tooltip: Vertical position of the color legend
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:95: QObject::connect(this->PositionYSlider, SIGNAL(valueChanged(double)), q, SLOT(onPositionChanged()));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:218: QSignalBlocker blocker9(d->PositionYSlider);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:220: d->PositionYSlider->setValue(d->ColorLegendDisplayNode->GetPosition()[1]);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:325: d->ColorLegendDisplayNode->SetPosition(d->PositionXSlider->value(), d->PositionYSlider->value());`
- Connected slots/functions: `onPositionChanged`
- API footprints: `GetPosition`, `SetPosition`

## widget: DimensionsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Size: | DimensionsLabel | QLabel
- Text: Size:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: S: | Short side length of the color legend, relative to view size | label_4 | QLabel
- Text: S:
- Tooltip: Short side length of the color legend, relative to view size
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: ShortSideSizeSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSlider`
- Search text: Short side length of the color legend, relative to view size | ShortSideSizeSlider | ctkDoubleSlider
- Tooltip: Short side length of the color legend, relative to view size
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:96: QObject::connect(this->ShortSideSizeSlider, SIGNAL(valueChanged(double)), q, SLOT(onSizeChanged()));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:212: QSignalBlocker blocker6(d->ShortSideSizeSlider);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:214: d->ShortSideSizeSlider->setValue(d->ColorLegendDisplayNode->GetSize()[0]);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:337: d->ColorLegendDisplayNode->SetSize(d->ShortSideSizeSlider->value(), d->LongSideSizeSlider->value());`
- Connected slots/functions: `onSizeChanged`
- API footprints: `GetSize`, `SetSize`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: L: | Long side length of the color legend, relative to view size | label_3 | QLabel
- Text: L:
- Tooltip: Long side length of the color legend, relative to view size
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: LongSideSizeSlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSlider`
- Search text: Long side length of the color legend, relative to view size | LongSideSizeSlider | ctkDoubleSlider
- Tooltip: Long side length of the color legend, relative to view size
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:97: QObject::connect(this->LongSideSizeSlider, SIGNAL(valueChanged(double)), q, SLOT(onSizeChanged()));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:213: QSignalBlocker blocker7(d->LongSideSizeSlider);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:215: d->LongSideSizeSlider->setValue(d->ColorLegendDisplayNode->GetSize()[1]);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:337: d->ColorLegendDisplayNode->SetSize(d->ShortSideSizeSlider->value(), d->LongSideSizeSlider->value());`
- Connected slots/functions: `onSizeChanged`
- API footprints: `GetSize`, `SetSize`

## widget: TitlePropertiesGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: TitlePropertiesGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: TitleTextPropertyWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKTextPropertyWidget`
- Search text: TitleTextPropertyWidget | ctkVTKTextPropertyWidget
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:147: d->TitleTextPropertyWidget->setTextProperty(d->ColorLegendDisplayNode ? d->ColorLegendDisplayNode->GetTitleTextProperty() : nullptr);`
- API footprints: `GetLabelTextProperty`, `GetTitleTextProperty`

## widget: LabelPropertiesGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: LabelPropertiesGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`

## widget: LabelTextPropertyWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKTextPropertyWidget`
- Search text: LabelTextPropertyWidget | ctkVTKTextPropertyWidget
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:82: this->LabelTextPropertyWidget->textEditWidget()->setToolTip(`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:103: QObject::connect(this->LabelTextPropertyWidget, SIGNAL(textChanged(QString)), q, SLOT(onLabelFormatChanged(QString)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:148: d->LabelTextPropertyWidget->setTextProperty(d->ColorLegendDisplayNode ? d->ColorLegendDisplayNode->GetLabelTextProperty() : nullptr);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:233: QString currentFormat = d->LabelTextPropertyWidget->text();`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:236: QSignalBlocker blocker11(d->LabelTextPropertyWidget);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx:237: d->LabelTextPropertyWidget->setText(newFormat.c_str());`
- Connected slots/functions: `onLabelFormatChanged`
- API footprints: `GetLabelFormat`, `GetLabelTextProperty`, `GetTitleTextProperty`, `SetLabelFormat`

## widget: DynamicSpacer

- Confidence: `ui_only`
- Widget/action class: `ctkDynamicSpacer`
- Search text: DynamicSpacer | ctkDynamicSpacer
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorLegendDisplayNodeWidget.h`
