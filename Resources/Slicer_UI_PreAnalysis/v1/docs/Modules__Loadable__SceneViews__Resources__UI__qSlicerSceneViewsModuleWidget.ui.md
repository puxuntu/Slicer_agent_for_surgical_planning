# Slicer UI Analysis: Modules/Loadable/SceneViews/Resources/UI/qSlicerSceneViewsModuleWidget.ui

- Owner class: `qSlicerSceneViewsModuleWidget`
- UI file: `Modules/Loadable/SceneViews/Resources/UI/qSlicerSceneViewsModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSceneViewsModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSceneViewsModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx`, `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:1: #include "GUI/qSlicerSceneViewsModuleWidget.h"`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:2: #include "ui_qSlicerSceneViewsModuleWidget.h"`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:47: class qSlicerSceneViewsModuleWidgetPrivate : public Ui_qSlicerSceneViewsModuleWidget`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:49: Q_DECLARE_PUBLIC(qSlicerSceneViewsModuleWidget);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:52: qSlicerSceneViewsModuleWidget* const q_ptr;`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:55: qSlicerSceneViewsModuleWidgetPrivate(qSlicerSceneViewsModuleWidget& object);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:56: ~qSlicerSceneViewsModuleWidgetPrivate();`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:67: // qSlicerSceneViewsModuleWidgetPrivate methods`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:70: vtkSlicerSceneViewsModuleLogic* qSlicerSceneViewsModuleWidgetPrivate::logic() const`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:72: Q_Q(const qSlicerSceneViewsModuleWidget);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:77: qSlicerSceneViewsModuleDialog* qSlicerSceneViewsModuleWidgetPrivate::sceneViewDialog()`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:92: qSlicerSceneViewsModuleWidgetPrivate::qSlicerSceneViewsModuleWidgetPrivate(qSlicerSceneViewsModuleWidget& object)`
- API footprints: `GetID`, `GetNthNodeByClass`, `IsBatchProcessing`, `MoveSceneViewDown`, `MoveSceneViewUp`, `RestoreSceneView`

## widget: CTKSpacer

- Confidence: `ui_only`
- Widget/action class: `ctkDynamicSpacer`
- Search text: CTKSpacer | ctkDynamicSpacer
- Implementation candidates: `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx`, `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.h`

## widget: CTKCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: SceneViews | CTKCollapsibleButton | ctkCollapsibleButton
- Text: SceneViews
- Implementation candidates: `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx`, `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.h`

## widget: SceneViewTableWidget

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: SceneViewTableWidget | QTableWidget
- Implementation candidates: `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx`, `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:114: this->SceneViewTableWidget->setColumnCount(SCENE_VIEW_NUMBER_OF_COLUMNS);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:115: this->SceneViewTableWidget->setHorizontalHeaderLabels(QStringList() //`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:118: this->SceneViewTableWidget->horizontalHeader()->hide();`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:120: this->SceneViewTableWidget->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:121: this->SceneViewTableWidget->horizontalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:122: this->SceneViewTableWidget->horizontalHeader()->setSectionResizeMode(SCENE_VIEW_DESCRIPTION_COLUMN, QHeaderView::Stretch);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:126: this->SceneViewTableWidget->setSelectionMode(QAbstractItemView::NoSelection);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:129: QObject::connect(this->SceneViewTableWidget, SIGNAL(cellDoubleClicked(int, int)), q, SLOT(onSceneViewDoubleClicked(int, int)));`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:136: if (row >= this->SceneViewTableWidget->rowCount())`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:143: QLabel* thumbnailWidget = dynamic_cast<QLabel*>(this->SceneViewTableWidget->cellWidget(row, SCENE_VIEW_THUMBNAIL_COLUMN));`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:147: this->SceneViewTableWidget->setCellWidget(row, SCENE_VIEW_THUMBNAIL_COLUMN, thumbnailWidget);`
  - `Modules/Loadable/SceneViews/GUI/qSlicerSceneViewsModuleWidget.cxx:165: ctkFittedTextBrowser* descriptionWidget = dynamic_cast<ctkFittedTextBrowser*>(this->SceneViewTableWidget->cellWidget(row, SCENE_VIEW_DESCRIPTION_COLUMN));`
- Connected slots/functions: `onSceneViewDoubleClicked`
- API footprints: `GetID`, `GetNthNodeByClass`, `GetNthSceneViewScreenshot`
