# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLNodeAttributeTableView.ui

- Owner class: `qMRMLNodeAttributeTableView`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLNodeAttributeTableView.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLNodeAttributeTableView

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qMRMLNodeAttributeTableView | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:29: #include "qMRMLNodeAttributeTableView.h"`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:30: #include "ui_qMRMLNodeAttributeTableView.h"`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:39: class qMRMLNodeAttributeTableViewPrivate : public Ui_qMRMLNodeAttributeTableView`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:41: Q_DECLARE_PUBLIC(qMRMLNodeAttributeTableView);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:44: qMRMLNodeAttributeTableView* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:47: qMRMLNodeAttributeTableViewPrivate(qMRMLNodeAttributeTableView& object);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:59: qMRMLNodeAttributeTableViewPrivate::qMRMLNodeAttributeTableViewPrivate(qMRMLNodeAttributeTableView& object)`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:66: void qMRMLNodeAttributeTableViewPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:68: Q_Q(qMRMLNodeAttributeTableView);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:79: // qMRMLNodeAttributeTableView methods`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:82: qMRMLNodeAttributeTableView::qMRMLNodeAttributeTableView(QWidget* _parent)`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:84: , d_ptr(new qMRMLNodeAttributeTableViewPrivate(*this))`

## widget: NodeAttributesTable

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: NodeAttributesTable | QTableWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx`, `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:73: QObject::connect(this->NodeAttributesTable, SIGNAL(itemChanged(QTableWidgetItem*)), q, SLOT(onAttributeChanged(QTableWidgetItem*)));`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:119: bool wasBlocked = d->NodeAttributesTable->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:121: d->NodeAttributesTable->clearContents();`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:125: d->NodeAttributesTable->setHorizontalHeaderLabels(headerLabels);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:126: d->NodeAttributesTable->setColumnWidth(0, d->NodeAttributesTable->width() / 2 - 10);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:127: d->NodeAttributesTable->setColumnWidth(1, d->NodeAttributesTable->width() / 2 - 10);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:131: d->NodeAttributesTable->setRowCount(0);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:132: d->NodeAttributesTable->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:139: d->NodeAttributesTable->setRowCount(0);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:143: d->NodeAttributesTable->setRowCount(attributeNames.size());`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:154: d->NodeAttributesTable->setItem(row, 0, attributeNameItem);`
  - `Libs/MRML/Widgets/qMRMLNodeAttributeTableView.cxx:157: d->NodeAttributesTable->setItem(row, 1, new QTableWidgetItem(QString(d->InspectedNode->GetAttribute(iter->c_str()))));`
- Connected slots/functions: `onAttributeChanged`
- API footprints: `EndModify`, `GetAttribute`, `RemoveAttribute`, `SetAttribute`, `StartModify`
