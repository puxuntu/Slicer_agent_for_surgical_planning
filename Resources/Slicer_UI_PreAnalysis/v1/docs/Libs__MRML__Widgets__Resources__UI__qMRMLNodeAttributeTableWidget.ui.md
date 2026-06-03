# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLNodeAttributeTableWidget.ui

- Owner class: `qMRMLNodeAttributeTableWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLNodeAttributeTableWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLNodeAttributeTableWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLNodeAttributeTableWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:25: #include "qMRMLNodeAttributeTableWidget.h"`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:26: #include "ui_qMRMLNodeAttributeTableWidget.h"`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:35: class qMRMLNodeAttributeTableWidgetPrivate : public Ui_qMRMLNodeAttributeTableWidget`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:37: Q_DECLARE_PUBLIC(qMRMLNodeAttributeTableWidget);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:40: qMRMLNodeAttributeTableWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:43: qMRMLNodeAttributeTableWidgetPrivate(qMRMLNodeAttributeTableWidget& object);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:50: qMRMLNodeAttributeTableWidgetPrivate::qMRMLNodeAttributeTableWidgetPrivate(qMRMLNodeAttributeTableWidget& object)`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:56: void qMRMLNodeAttributeTableWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:58: Q_Q(qMRMLNodeAttributeTableWidget);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:66: // qMRMLNodeAttributeTableWidget methods`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:69: qMRMLNodeAttributeTableWidget::qMRMLNodeAttributeTableWidget(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:71: , d_ptr(new qMRMLNodeAttributeTableWidgetPrivate(*this))`
- API footprints: `GetPointer`

## widget: NodeAttributesGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: NodeAttributesGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`

## widget: MRMLNodeAttributeTableView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeAttributeTableView`
- Search text: MRMLNodeAttributeTableView | qMRMLNodeAttributeTableView
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:61: QObject::connect(this->AddAttributeButton, SIGNAL(clicked()), this->MRMLNodeAttributeTableView, SLOT(addAttribute()));`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:62: QObject::connect(this->RemoveAttributeButton, SIGNAL(clicked()), this->MRMLNodeAttributeTableView, SLOT(removeSelectedAttributes()));`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:91: d->MRMLNodeAttributeTableView->setInspectedNode(node);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:103: qMRMLNodeAttributeTableView* qMRMLNodeAttributeTableWidget::tableView()`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:106: return d->MRMLNodeAttributeTableView;`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h:37: class qMRMLNodeAttributeTableView;`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h:50: qMRMLNodeAttributeTableView* tableView();`
- Connected slots/functions: `addAttribute`, `removeSelectedAttributes`
- API footprints: `GetPointer`

## widget: AddAttributeButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Add | Add blank row to the table. The attribute is added to the MRML node when the name and value is set | AddAttributeButton | QPushButton
- Text: Add
- Tooltip: Add blank row to the table. The attribute is added to the MRML node when the name and value is set
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:61: QObject::connect(this->AddAttributeButton, SIGNAL(clicked()), this->MRMLNodeAttributeTableView, SLOT(addAttribute()));`
- Connected slots/functions: `addAttribute`

## widget: RemoveAttributeButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Remove | Remove selected attribute(s) | RemoveAttributeButton | QPushButton
- Text: Remove
- Tooltip: Remove selected attribute(s)
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:62: QObject::connect(this->RemoveAttributeButton, SIGNAL(clicked()), this->MRMLNodeAttributeTableView, SLOT(removeSelectedAttributes()));`
- Connected slots/functions: `removeSelectedAttributes`

## widget: NodePropertiesGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: NodePropertiesGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:131: d->NodePropertiesGroupBox->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:138: d->NodePropertiesGroupBox->setVisible(false);`
- API footprints: `GetPointer`, `PrintSelf`

## widget: MRMLNodeInfoLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: MRMLNodeInfoLabel | QLabel
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:134: d->MRMLNodeInfoLabel->setText(infoStream.str().c_str());`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableWidget.cxx:139: d->MRMLNodeInfoLabel->clear();`
- API footprints: `PrintSelf`
