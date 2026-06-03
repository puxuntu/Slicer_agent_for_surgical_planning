# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLClipNodeDisplayWidget.ui

- Owner class: `qMRMLClipNodeDisplayWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLClipNodeDisplayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLClipNodeDisplayWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLClipNodeDisplayWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:24: #include "qMRMLClipNodeDisplayWidget.h"`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:25: #include "ui_qMRMLClipNodeDisplayWidget.h"`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:38: class qMRMLClipNodeDisplayWidgetPrivate : public Ui_qMRMLClipNodeDisplayWidget`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:40: Q_DECLARE_PUBLIC(qMRMLClipNodeDisplayWidget);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:43: qMRMLClipNodeDisplayWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:46: qMRMLClipNodeDisplayWidgetPrivate(qMRMLClipNodeDisplayWidget& object);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:54: qMRMLClipNodeDisplayWidgetPrivate::qMRMLClipNodeDisplayWidgetPrivate(qMRMLClipNodeDisplayWidget& object)`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:60: void qMRMLClipNodeDisplayWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:62: Q_Q(qMRMLClipNodeDisplayWidget);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:74: qMRMLClipNodeDisplayWidget::qMRMLClipNodeDisplayWidget(QWidget* _parent /*=nullptr*/)`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:76: , d_ptr(new qMRMLClipNodeDisplayWidgetPrivate(*this))`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:78: Q_D(qMRMLClipNodeDisplayWidget);`
- API footprints: `vtkMRMLDisplayNode::SafeDownCast`

## widget: checkBox_ClippingKeepWholeCells

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_ClippingKeepWholeCells | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:70: QObject::connect(this->checkBox_ClippingKeepWholeCells, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:171: wasBlocking = d->checkBox_ClippingKeepWholeCells->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:172: d->checkBox_ClippingKeepWholeCells->setEnabled(clipNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:173: d->checkBox_ClippingKeepWholeCells->setChecked(clipNode ? clipNode->GetClippingMethod() == vtkMRMLClipNode::WholeCells : false);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:174: d->checkBox_ClippingKeepWholeCells->setVisible(surfaceWidgetsVisible);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:175: d->checkBox_ClippingKeepWholeCells->blockSignals(wasBlocking);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:217: clipNode->SetClippingMethod(d->checkBox_ClippingKeepWholeCells->isChecked() ? vtkMRMLClipNode::WholeCells : vtkMRMLClipNode::Straight);`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetClipNode`, `GetClippingMethod`, `SetClipping`, `SetClippingCapOpacity`, `SetClippingCapSurface`, `SetClippingMethod`, `SetClippingOutline`, `vtkMRMLClipNode::Straight`, `vtkMRMLClipNode::WholeCells`, `vtkMRMLModelDisplayNode::SafeDownCast`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`

## widget: label_Clipping

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Clipping: | label_Clipping | QLabel
- Text: Clipping:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`

## widget: label_ClippingCapping

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Cap visibility: | label_ClippingCapping | QLabel
- Text: Cap visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`

## widget: label_ClippingCapOpacity

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Opacity: | label_ClippingCapOpacity | QLabel
- Text: Opacity:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`

## widget: label_ClippingOutline

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Outline visibility: | label_ClippingOutline | QLabel
- Text: Outline visibility:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`

## widget: checkBox_ClippingCapping

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_ClippingCapping | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:67: QObject::connect(this->checkBox_ClippingCapping, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:153: wasBlocking = d->checkBox_ClippingCapping->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:154: d->checkBox_ClippingCapping->setEnabled(clipNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:155: d->checkBox_ClippingCapping->setChecked(capping);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:156: d->checkBox_ClippingCapping->setVisible(surfaceWidgetsVisible);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:157: d->checkBox_ClippingCapping->blockSignals(wasBlocking);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:200: modelDisplayNode->SetClippingCapSurface(d->checkBox_ClippingCapping->isChecked());`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:208: segmentationDisplayNode->SetClippingCapSurface(d->checkBox_ClippingCapping->isChecked());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetClipNode`, `SetClipping`, `SetClippingCapOpacity`, `SetClippingCapSurface`, `SetClippingMethod`, `SetClippingOutline`, `vtkMRMLClipNode::Straight`, `vtkMRMLClipNode::WholeCells`, `vtkMRMLModelDisplayNode::SafeDownCast`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Keep only whole cells: | label | QLabel
- Text: Keep only whole cells:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`

## widget: checkBox_ClippingOutline

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_ClippingOutline | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:69: QObject::connect(this->checkBox_ClippingOutline, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:165: wasBlocking = d->checkBox_ClippingOutline->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:166: d->checkBox_ClippingOutline->setEnabled(clipNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:167: d->checkBox_ClippingOutline->setChecked(outline);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:168: d->checkBox_ClippingOutline->setVisible(surfaceWidgetsVisible);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:169: d->checkBox_ClippingOutline->blockSignals(wasBlocking);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:202: modelDisplayNode->SetClippingOutline(d->checkBox_ClippingOutline->isChecked());`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:210: segmentationDisplayNode->SetClippingOutline(d->checkBox_ClippingOutline->isChecked());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetClipNode`, `SetClipping`, `SetClippingCapOpacity`, `SetClippingCapSurface`, `SetClippingMethod`, `SetClippingOutline`, `vtkMRMLClipNode::Straight`, `vtkMRMLClipNode::WholeCells`, `vtkMRMLModelDisplayNode::SafeDownCast`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`

## widget: checkBox_Clipping

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_Clipping | QCheckBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:66: QObject::connect(this->checkBox_Clipping, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:67: QObject::connect(this->checkBox_ClippingCapping, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:69: QObject::connect(this->checkBox_ClippingOutline, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:70: QObject::connect(this->checkBox_ClippingKeepWholeCells, SIGNAL(toggled(bool)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:148: wasBlocking = d->checkBox_Clipping->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:149: d->checkBox_Clipping->setEnabled(clipNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:150: d->checkBox_Clipping->setChecked(d->MRMLDisplayNode ? d->MRMLDisplayNode->GetClipping() : false);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:151: d->checkBox_Clipping->blockSignals(wasBlocking);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:153: wasBlocking = d->checkBox_ClippingCapping->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:154: d->checkBox_ClippingCapping->setEnabled(clipNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:155: d->checkBox_ClippingCapping->setChecked(capping);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:156: d->checkBox_ClippingCapping->setVisible(surfaceWidgetsVisible);`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetClipNode`, `GetClipping`, `GetClippingMethod`, `SetClipping`, `SetClippingCapOpacity`, `SetClippingCapSurface`, `SetClippingMethod`, `SetClippingOutline`, `vtkMRMLClipNode::Straight`, `vtkMRMLClipNode::WholeCells`, `vtkMRMLModelDisplayNode::SafeDownCast`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`

## widget: sliderWidget_ClippingCapOpacity

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: sliderWidget_ClippingCapOpacity | ctkSliderWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx`, `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:68: QObject::connect(this->sliderWidget_ClippingCapOpacity, SIGNAL(valueChanged(double)), q, SLOT(updateMRMLFromWidget()));`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:159: wasBlocking = d->sliderWidget_ClippingCapOpacity->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:160: d->sliderWidget_ClippingCapOpacity->setEnabled(capping);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:161: d->sliderWidget_ClippingCapOpacity->setValue(capOpacity);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:162: d->sliderWidget_ClippingCapOpacity->setVisible(surfaceWidgetsVisible);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:163: d->sliderWidget_ClippingCapOpacity->blockSignals(wasBlocking);`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:201: modelDisplayNode->SetClippingCapOpacity(d->sliderWidget_ClippingCapOpacity->value());`
  - `Libs/MRML/Widgets/qMRMLClipNodeDisplayWidget.cxx:209: segmentationDisplayNode->SetClippingCapOpacity(d->sliderWidget_ClippingCapOpacity->value());`
- Connected slots/functions: `updateMRMLFromWidget`
- API footprints: `GetClipNode`, `SetClipping`, `SetClippingCapOpacity`, `SetClippingCapSurface`, `SetClippingMethod`, `SetClippingOutline`, `vtkMRMLClipNode::Straight`, `vtkMRMLClipNode::WholeCells`, `vtkMRMLModelDisplayNode::SafeDownCast`, `vtkMRMLSegmentationDisplayNode::SafeDownCast`
