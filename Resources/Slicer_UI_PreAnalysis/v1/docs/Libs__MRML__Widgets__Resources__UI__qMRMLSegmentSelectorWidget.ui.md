# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLSegmentSelectorWidget.ui

- Owner class: `qMRMLSegmentSelectorWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLSegmentSelectorWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentSelectorWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLSegmentSelectorWidget | qMRMLWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:24: #include "qMRMLSegmentSelectorWidget.h"`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:26: #include "ui_qMRMLSegmentSelectorWidget.h"`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:43: class qMRMLSegmentSelectorWidgetPrivate : public Ui_qMRMLSegmentSelectorWidget`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:45: Q_DECLARE_PUBLIC(qMRMLSegmentSelectorWidget);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:48: qMRMLSegmentSelectorWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:51: qMRMLSegmentSelectorWidgetPrivate(qMRMLSegmentSelectorWidget& object);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:73: qMRMLSegmentSelectorWidgetPrivate::qMRMLSegmentSelectorWidgetPrivate(qMRMLSegmentSelectorWidget& object)`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:81: void qMRMLSegmentSelectorWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:83: Q_Q(qMRMLSegmentSelectorWidget);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:100: void qMRMLSegmentSelectorWidgetPrivate::setMessage(QString message)`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:109: // qMRMLSegmentSelectorWidget methods`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:112: qMRMLSegmentSelectorWidget::qMRMLSegmentSelectorWidget(QWidget* _parent)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox_Segmentation.setMRMLScene(vtkMRMLScene*)`
- API footprints: `vtkMRMLSegmentationNode::SafeDownCast`

## widget: frame_Segment

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: frame_Segment | QFrame
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:531: d->gridLayout->takeAt(d->gridLayout->indexOf(d->frame_Segment));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:534: d->gridLayout->addWidget(d->frame_Segment, 0, 1);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:542: d->gridLayout->addWidget(d->frame_Segment, 1, 0);`

## widget: frame_SegmentIndented

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame_SegmentIndented | QFrame
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`

## widget: CheckableComboBox_Segment

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckableComboBox`
- Search text: CheckableComboBox_Segment | ctkCheckableComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:93: QObject::connect(this->CheckableComboBox_Segment, SIGNAL(checkedIndexesChanged()), q, SLOT(onSegmentMultiSelectionChanged()));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:96: this->CheckableComboBox_Segment->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:179: wasBlocked = d->CheckableComboBox_Segment->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:180: d->CheckableComboBox_Segment->clear();`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:181: d->CheckableComboBox_Segment->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:190: d->CheckableComboBox_Segment->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:200: d->CheckableComboBox_Segment->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:203: wasBlocked = d->CheckableComboBox_Segment->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:216: d->CheckableComboBox_Segment->addItem(name, QVariant(segmentId));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:220: d->CheckableComboBox_Segment->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:313: for (const QModelIndex& index : d->CheckableComboBox_Segment->checkedIndexes())`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:315: d->SelectedSegmentIDs << d->CheckableComboBox_Segment->itemData(index.row()).toString();`
- Connected slots/functions: `onSegmentMultiSelectionChanged`
- API footprints: `GetName`

## widget: comboBox_Segment

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: comboBox_Segment | QComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:92: QObject::connect(this->comboBox_Segment, SIGNAL(currentIndexChanged(int)), q, SLOT(onCurrentSegmentChanged(int)));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:175: bool wasBlocked = d->comboBox_Segment->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:176: d->comboBox_Segment->clear();`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:177: d->comboBox_Segment->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:189: d->comboBox_Segment->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:227: d->comboBox_Segment->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:230: wasBlocked = d->comboBox_Segment->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:235: d->comboBox_Segment->addItem(NONE_DISPLAY, QVariant(NONE_DISPLAY));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:247: d->comboBox_Segment->addItem(name, QVariant(segmentId));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:251: d->comboBox_Segment->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:258: wasBlocked = d->comboBox_Segment->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:260: d->comboBox_Segment->blockSignals(wasBlocked);`
- Connected slots/functions: `onCurrentSegmentChanged`
- API footprints: `GetName`, `GetSegment`

## widget: label_Segment

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Segment:  | label_Segment | QLabel
- Text: Segment: 
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:188: d->label_Segment->setVisible(false);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:194: d->label_Segment->setVisible(true);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:535: d->label_Segment->setText("");`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:543: d->label_Segment->setText("Segment: ");`

## widget: label_Message

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Messages label | label_Message | QLabel
- Text: Messages label
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:102: this->label_Message->setVisible(!message.isEmpty());`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:103: this->label_Message->setText(message);`

## widget: MRMLNodeComboBox_Segmentation

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_Segmentation | qMRMLNodeComboBox
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx`, `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:87: QObject::connect(this->MRMLNodeComboBox_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onCurrentNodeChanged(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:88: QObject::connect(this->MRMLNodeComboBox_Segmentation, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SIGNAL(currentNodeChanged(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:89: QObject::connect(this->MRMLNodeComboBox_Segmentation, SIGNAL(currentNodeChanged(bool)), q, SIGNAL(currentNodeChanged(bool)));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:90: QObject::connect(this->MRMLNodeComboBox_Segmentation, SIGNAL(nodeAboutToBeEdited(vtkMRMLNode*)), q, SIGNAL(nodeAboutToBeEdited(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:146: d->MRMLNodeComboBox_Segmentation->setCurrentNode(node);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:153: return d->MRMLNodeComboBox_Segmentation->currentNode();`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:160: d->MRMLNodeComboBox_Segmentation->setCurrentNodeID(nodeID);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:167: return d->MRMLNodeComboBox_Segmentation->currentNodeID();`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:448: d->MRMLNodeComboBox_Segmentation->setNoneEnabled(enable);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:458: return d->MRMLNodeComboBox_Segmentation->noneEnabled();`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:465: d->MRMLNodeComboBox_Segmentation->setEditEnabled(enable);`
  - `Libs/MRML/Widgets/qMRMLSegmentSelectorWidget.cxx:472: return d->MRMLNodeComboBox_Segmentation->editEnabled();`
- Connected slots/functions: `onCurrentNodeChanged`
- API footprints: `vtkMRMLSegmentationNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSegmentationNode"]}
