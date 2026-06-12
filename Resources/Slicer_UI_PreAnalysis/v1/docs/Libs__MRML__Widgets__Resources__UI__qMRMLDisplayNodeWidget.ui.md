# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLDisplayNodeWidget.ui

- Owner class: `qMRMLDisplayNodeWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLDisplayNodeWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLDisplayNodeWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLDisplayNodeWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:24: #include "qMRMLDisplayNodeWidget.h"`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:25: #include "ui_qMRMLDisplayNodeWidget.h"`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:36: class qMRMLDisplayNodeWidgetPrivate : public Ui_qMRMLDisplayNodeWidget`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:38: Q_DECLARE_PUBLIC(qMRMLDisplayNodeWidget);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:41: qMRMLDisplayNodeWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:44: qMRMLDisplayNodeWidgetPrivate(qMRMLDisplayNodeWidget& object);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:52: qMRMLDisplayNodeWidgetPrivate::qMRMLDisplayNodeWidgetPrivate(qMRMLDisplayNodeWidget& object)`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:59: void qMRMLDisplayNodeWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:61: Q_Q(qMRMLDisplayNodeWidget);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:78: qMRMLDisplayNodeWidget::qMRMLDisplayNodeWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:80: , d_ptr(new qMRMLDisplayNodeWidgetPrivate(*this))`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:82: Q_D(qMRMLDisplayNodeWidget);`
- API footprints: `GetPointer`, `vtkMRMLDisplayNode::SafeDownCast`, `vtkMRMLDisplayableNode::SafeDownCast`

## widget: CollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: VisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: &Visibility: | VisibilityLabel | QLabel
- Text: &Visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: VisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: VisibilityCheckBox | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:64: QObject::connect(this->VisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setVisibility(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:67: QObject::connect(this->ThreeDVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(set3DVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:68: QObject::connect(this->SliceIntersectionVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setSliceIntersectionVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:133: return d->VisibilityCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:140: d->VisibilityCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:220: return d->ThreeDVisibilityCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:227: return d->SliceIntersectionVisibilityCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:234: d->ThreeDVisibilityCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:241: d->SliceIntersectionVisibilityCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:303: d->VisibilityCheckBox->setChecked(d->MRMLDisplayNode->GetVisibility());`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:308: d->ThreeDVisibilityCheckBox->setChecked(d->MRMLDisplayNode->GetVisibility3D());`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:309: d->SliceIntersectionVisibilityCheckBox->setChecked(d->MRMLDisplayNode->GetVisibility2D());`
- Connected slots/functions: `set3DVisible`, `setSliceIntersectionVisible`, `setVisibility`
- API footprints: `GetClipping`, `GetPointer`, `GetSelectable`, `GetSelected`, `GetSliceIntersectionOpacity`, `GetSliceIntersectionThickness`, `GetVisibility`, `GetVisibility2D`, `GetVisibility3D`, `SetVisibility`, `SetVisibility2D`

## widget: SelectedLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: &Selected: | SelectedLabel | QLabel
- Text: &Selected:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:165: d->SelectedLabel->setVisible(visible);`

## widget: SelectedCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: SelectedCheckBox | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:65: QObject::connect(this->SelectedCheckBox, SIGNAL(toggled(bool)), q, SLOT(setSelected(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:158: return d->SelectedCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:166: d->SelectedCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:305: d->SelectedCheckBox->setEnabled(d->MRMLDisplayNode->GetSelectable());`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:306: d->SelectedCheckBox->setChecked(d->MRMLDisplayNode->GetSelected());`
- Connected slots/functions: `setSelected`
- API footprints: `GetClipping`, `GetPointer`, `GetSelectable`, `GetSelected`, `GetVisibility`, `GetVisibility3D`, `SetSelected`

## widget: ClippingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: &Clip: | ClippingLabel | QLabel
- Text: &Clip:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: ClippingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: ClippingCheckBox | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:66: QObject::connect(this->ClippingCheckBox, SIGNAL(toggled(bool)), q, SLOT(setClipping(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:184: return d->ClippingCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:191: d->ClippingCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:307: d->ClippingCheckBox->setChecked(d->MRMLDisplayNode->GetClipping());`
- Connected slots/functions: `setClipping`
- API footprints: `GetClipping`, `GetPointer`, `GetSelectable`, `GetSelected`, `GetVisibility2D`, `GetVisibility3D`, `SetClipping`

## widget: SliceIntersectionVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice &Intersections Visibility: | SliceIntersectionVisibilityLabel | QLabel
- Text: Slice &Intersections Visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: SliceIntersectionVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: SliceIntersectionVisibilityCheckBox | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:68: QObject::connect(this->SliceIntersectionVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(setSliceIntersectionVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:227: return d->SliceIntersectionVisibilityCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:241: d->SliceIntersectionVisibilityCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:309: d->SliceIntersectionVisibilityCheckBox->setChecked(d->MRMLDisplayNode->GetVisibility2D());`
- Connected slots/functions: `setSliceIntersectionVisible`
- API footprints: `GetClipping`, `GetPointer`, `GetSliceIntersectionOpacity`, `GetSliceIntersectionThickness`, `GetVisibility2D`, `GetVisibility3D`, `SetVisibility2D`

## widget: SliceIntersectionThicknessLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice Intersections &Thickness: | SliceIntersectionThicknessLabel | QLabel
- Text: Slice Intersections &Thickness:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: SliceIntersectionThicknessSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: SliceIntersectionThicknessSpinBox | QSpinBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:69: QObject::connect(this->SliceIntersectionThicknessSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setSliceIntersectionThickness(int)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:259: return d->SliceIntersectionThicknessSpinBox->value();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:266: d->SliceIntersectionThicknessSpinBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:310: d->SliceIntersectionThicknessSpinBox->setValue(d->MRMLDisplayNode->GetSliceIntersectionThickness());`
- Connected slots/functions: `setSliceIntersectionThickness`
- API footprints: `GetPointer`, `GetSliceIntersectionOpacity`, `GetSliceIntersectionThickness`, `GetVisibility2D`, `GetVisibility3D`, `SetSliceIntersectionThickness`

## widget: SliceIntersectionOpacityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Slice Intersections Opacity: | SliceIntersectionOpacityLabel | QLabel
- Text: Slice Intersections Opacity:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: SliceIntersectionOpacitySlider

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: SliceIntersectionOpacitySlider | ctkSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:70: QObject::connect(this->SliceIntersectionOpacitySlider, SIGNAL(valueChanged(double)), q, SLOT(setSliceIntersectionOpacity(double)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:284: return d->SliceIntersectionOpacitySlider->value();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:291: d->SliceIntersectionOpacitySlider->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:311: d->SliceIntersectionOpacitySlider->setValue(d->MRMLDisplayNode->GetSliceIntersectionOpacity());`
- Connected slots/functions: `setSliceIntersectionOpacity`
- API footprints: `GetPointer`, `GetSliceIntersectionOpacity`, `GetSliceIntersectionThickness`, `GetVisibility2D`, `SetSliceIntersectionOpacity`

## widget: DisplayNodeViewComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLDisplayNodeViewComboBox`
- Search text: Select views in which to show this node. All unchecked shows in all 3D and 2D views. | DisplayNodeViewComboBox | qMRMLDisplayNodeViewComboBox
- Tooltip: Select views in which to show this node. All unchecked shows in all 3D and 2D views.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:304: d->DisplayNodeViewComboBox->setMRMLDisplayNode(d->MRMLDisplayNode);`
- API footprints: `GetSelectable`, `GetSelected`, `GetVisibility`

## widget: DisplayNodeViewLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: View: | DisplayNodeViewLabel | QLabel
- Text: View:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: ThreeDVisibilityLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: 3D Visibility: | ThreeDVisibilityLabel | QLabel
- Text: 3D Visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`

## widget: ThreeDVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: ThreeDVisibilityCheckBox | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:67: QObject::connect(this->ThreeDVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(set3DVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:220: return d->ThreeDVisibilityCheckBox->isChecked();`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:234: d->ThreeDVisibilityCheckBox->setVisible(visible);`
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:308: d->ThreeDVisibilityCheckBox->setChecked(d->MRMLDisplayNode->GetVisibility3D());`
- Connected slots/functions: `set3DVisible`
- API footprints: `GetClipping`, `GetSelected`, `GetSliceIntersectionThickness`, `GetVisibility2D`, `GetVisibility3D`

## widget: PropertyWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKPropertyWidget`
- Search text: PropertyWidget | ctkVTKPropertyWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx`, `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLDisplayNodeWidget.cxx:72: this->PropertyWidget->setProperty(this->Property);`
- API footprints: `GetPointer`
