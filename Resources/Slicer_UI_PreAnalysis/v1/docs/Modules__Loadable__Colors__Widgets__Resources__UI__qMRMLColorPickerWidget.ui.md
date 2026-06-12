# Slicer UI Analysis: Modules/Loadable/Colors/Widgets/Resources/UI/qMRMLColorPickerWidget.ui

- Owner class: `qMRMLColorPickerWidget`
- UI file: `Modules/Loadable/Colors/Widgets/Resources/UI/qMRMLColorPickerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLColorPickerWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLColorPickerWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:29: #include "qMRMLColorPickerWidget.h"`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:31: #include "ui_qMRMLColorPickerWidget.h"`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:44: class qMRMLColorPickerWidgetPrivate : public Ui_qMRMLColorPickerWidget`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:46: Q_DECLARE_PUBLIC(qMRMLColorPickerWidget);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:49: qMRMLColorPickerWidget* const q_ptr;`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:52: qMRMLColorPickerWidgetPrivate(qMRMLColorPickerWidget& object);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:59: qMRMLColorPickerWidgetPrivate::qMRMLColorPickerWidgetPrivate(qMRMLColorPickerWidget& object)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:67: void qMRMLColorPickerWidgetPrivate::init()`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:69: Q_Q(qMRMLColorPickerWidget);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:86: qMRMLColorPickerWidget::qMRMLColorPickerWidget(QWidget* _parent)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:88: , d_ptr(new qMRMLColorPickerWidgetPrivate(*this))`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:90: Q_D(qMRMLColorPickerWidget);`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> ColorTableComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `GetPointer`, `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLNode::SafeDownCast`, `vtkMRMLScene::NodeAddedEvent`

## widget: ColorTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color node: | ColorTableLabel | QLabel
- Text: Color node:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.h`

## widget: ColorTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: ColorTableComboBox | qMRMLColorTableComboBox
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:71: QObject::connect(this->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onCurrentColorNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:72: QObject::connect(this->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this->SearchBox, SLOT(clear()));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:115: return vtkMRMLColorNode::SafeDownCast(d->ColorTableComboBox->currentNode());`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:122: d->ColorTableComboBox->setCurrentNode(node);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:160: if (scene && !d->ColorTableComboBox->currentNode())`
- Connected slots/functions: `clear`, `onCurrentColorNodeChanged`, `setMRMLColorNode`
- Declared UI connections: `currentNodeChanged(vtkMRMLNode*) -> MRMLColorListView.setMRMLColorNode(vtkMRMLNode*)`
- API footprints: `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLScene::NodeAddedEvent`

## widget: MRMLColorListView

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLColorListView`
- Search text: MRMLColorListView | qMRMLColorListView
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:73: QObject::connect(this->MRMLColorListView, SIGNAL(colorSelected(int)), q, SIGNAL(colorEntrySelected(int)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:74: QObject::connect(this->MRMLColorListView, SIGNAL(colorSelected(QColor)), q, SIGNAL(colorSelected(QColor)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:75: QObject::connect(this->MRMLColorListView, SIGNAL(colorSelected(QString)), q, SIGNAL(colorNameSelected(QString)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:76: this->MRMLColorListView->setDragDropMode(QAbstractItemView::NoDragDrop);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:173: QModelIndex rootIndex = d->MRMLColorListView->rootIndex();`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:174: const int count = d->MRMLColorListView->model()->rowCount(rootIndex);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:177: QSize sizeHint = d->MRMLColorListView->sizeHintForIndex(d->MRMLColorListView->model()->index(i, 0, rootIndex));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:183: d->MRMLColorListView->setGridSize(maxSizeHint);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:194: d->MRMLColorListView->sortFilterProxyModel()->setFilterRegularExpression(regExp);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:200: QModelIndex start = d->MRMLColorListView->sortFilterProxyModel()->index(0, 0);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:201: QModelIndexList indexList = d->MRMLColorListView->sortFilterProxyModel()->match(start, 0, d->SearchBox->text(), 1, Qt::MatchStartsWith);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:205: indexList = d->MRMLColorListView->sortFilterProxyModel()->match(start, 0, d->SearchBox->text(), 1, Qt::MatchContains);`

## widget: SearchBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSearchBox`
- Search text: SearchBox | ctkSearchBox
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx`, `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:72: QObject::connect(this->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this->SearchBox, SLOT(clear()));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:78: // SearchBox`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:79: this->SearchBox->setPlaceholderText("Search color...");`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:80: this->SearchBox->setShowSearchIcon(true);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:81: this->SearchBox->installEventFilter(q);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:82: QObject::connect(this->SearchBox, SIGNAL(textChanged(QString)), q, SLOT(onTextChanged(QString)));`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:198: if (!d->SearchBox->text().isEmpty())`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:201: QModelIndexList indexList = d->MRMLColorListView->sortFilterProxyModel()->match(start, 0, d->SearchBox->text(), 1, Qt::MatchStartsWith);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:205: indexList = d->MRMLColorListView->sortFilterProxyModel()->match(start, 0, d->SearchBox->text(), 1, Qt::MatchContains);`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:214: d->SearchBox->setFocus();`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:221: if (target == d->SearchBox)`
  - `Modules/Loadable/Colors/Widgets/qMRMLColorPickerWidget.cxx:225: d->SearchBox->clear();`
- Connected slots/functions: `clear`, `onTextChanged`
