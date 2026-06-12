# Slicer UI Analysis: Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationRepresentationsListView.ui

- Owner class: `qMRMLSegmentationRepresentationsListView`
- UI file: `Modules/Loadable/Segmentations/Widgets/Resources/UI/qMRMLSegmentationRepresentationsListView.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSegmentationRepresentationsListView

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLSegmentationRepresentationsListView | QWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:24: #include "qMRMLSegmentationRepresentationsListView.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:25: #include "ui_qMRMLSegmentationRepresentationsListView.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:50: class qMRMLSegmentationRepresentationsListViewPrivate : public Ui_qMRMLSegmentationRepresentationsListView`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:52: Q_DECLARE_PUBLIC(qMRMLSegmentationRepresentationsListView);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:55: qMRMLSegmentationRepresentationsListView* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:58: qMRMLSegmentationRepresentationsListViewPrivate(qMRMLSegmentationRepresentationsListView& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:76: qMRMLSegmentationRepresentationsListViewPrivate::qMRMLSegmentationRepresentationsListViewPrivate(qMRMLSegmentationRepresentationsListView& object)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:83: void qMRMLSegmentationRepresentationsListViewPrivate::init()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:85: Q_Q(qMRMLSegmentationRepresentationsListView);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:96: int qMRMLSegmentationRepresentationsListViewPrivate::columnIndex(QString label)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:102: void qMRMLSegmentationRepresentationsListViewPrivate::setMessage(const QString& message)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:109: // qMRMLSegmentationRepresentationsListView methods`
- API footprints: `vtkMRMLSegmentationNode::SafeDownCast`

## widget: RepresentationsListMessageLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: No node selected | RepresentationsListMessageLabel | QLabel
- Text: No node selected
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:104: this->RepresentationsListMessageLabel->setVisible(!message.isEmpty());`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:105: this->RepresentationsListMessageLabel->setText(message);`

## widget: RepresentationsList

- Confidence: `linked_to_api`
- Widget/action class: `QListWidget`
- Search text: RepresentationsList | QListWidget
- Implementation candidates: `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx`, `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:24: #include "qMRMLSegmentationRepresentationsListView.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:25: #include "ui_qMRMLSegmentationRepresentationsListView.h"`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:50: class qMRMLSegmentationRepresentationsListViewPrivate : public Ui_qMRMLSegmentationRepresentationsListView`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:52: Q_DECLARE_PUBLIC(qMRMLSegmentationRepresentationsListView);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:55: qMRMLSegmentationRepresentationsListView* const q_ptr;`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:58: qMRMLSegmentationRepresentationsListViewPrivate(qMRMLSegmentationRepresentationsListView& object);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:76: qMRMLSegmentationRepresentationsListViewPrivate::qMRMLSegmentationRepresentationsListViewPrivate(qMRMLSegmentationRepresentationsListView& object)`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:83: void qMRMLSegmentationRepresentationsListViewPrivate::init()`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:85: Q_Q(qMRMLSegmentationRepresentationsListView);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:91: this->RepresentationsList->setSelectionMode(QAbstractItemView::NoSelection);`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:92: this->RepresentationsList->setStyleSheet("QListWidget::item { border-bottom: 1px solid lightGray; }");`
  - `Modules/Loadable/Segmentations/Widgets/qMRMLSegmentationRepresentationsListView.cxx:96: int qMRMLSegmentationRepresentationsListViewPrivate::columnIndex(QString label)`
- Connected slots/functions: `populateRepresentationsList`
- API footprints: `ContainsRepresentation`, `GetAvailableRepresentationNames`, `GetNumberOfSegments`, `GetSegmentation`, `GetSourceRepresentationName`, `RemoveRepresentation`, `SetSourceRepresentationName`, `vtkMRMLSegmentationNode::SafeDownCast`
