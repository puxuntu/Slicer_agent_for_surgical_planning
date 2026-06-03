# Slicer UI Analysis: Base/QTApp/Resources/UI/qSlicerMainWindow.ui

- Owner class: `qSlicerMainWindow`
- UI file: `Base/QTApp/Resources/UI/qSlicerMainWindow.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerMainWindow

- Confidence: `linked_to_api`
- Widget/action class: `QMainWindow`
- Search text: qSlicerMainWindow | QMainWindow
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:21: #include "qSlicerMainWindow_p.h"`
  - `Base/QTApp/qSlicerMainWindow.cxx:108: // qSlicerMainWindowPrivate methods`
  - `Base/QTApp/qSlicerMainWindow.cxx:110: qSlicerMainWindowPrivate::qSlicerMainWindowPrivate(qSlicerMainWindow& object)`
  - `Base/QTApp/qSlicerMainWindow.cxx:116: qSlicerMainWindowPrivate::~qSlicerMainWindowPrivate() {}`
  - `Base/QTApp/qSlicerMainWindow.cxx:119: void qSlicerMainWindowPrivate::init()`
  - `Base/QTApp/qSlicerMainWindow.cxx:121: Q_Q(qSlicerMainWindow);`
  - `Base/QTApp/qSlicerMainWindow.cxx:131: void qSlicerMainWindowPrivate::setupUi(QMainWindow* mainWindow)`
  - `Base/QTApp/qSlicerMainWindow.cxx:133: Q_Q(qSlicerMainWindow);`
  - `Base/QTApp/qSlicerMainWindow.cxx:135: this->Ui_qSlicerMainWindow::setupUi(mainWindow);`
  - `Base/QTApp/qSlicerMainWindow.cxx:155: this->PanelDockWidget->toggleViewAction()->setText(qSlicerMainWindow::tr("Show &Module Panel"));`
  - `Base/QTApp/qSlicerMainWindow.cxx:156: this->PanelDockWidget->toggleViewAction()->setToolTip(qSlicerMainWindow::tr("Collapse/Expand the GUI panel and allows Slicer's viewers to occupy "`
  - `Base/QTApp/qSlicerMainWindow.cxx:179: this->ModuleSelectorToolBar = new qSlicerModuleSelectorToolBar(qSlicerMainWindow::tr("Module Selection"), q);`
- Connected slots/functions: `onFileRecentLoadedActionTriggered`
- API footprints: `Redo`, `Undo`, `vtkMRMLLayoutNode::SlicerLayoutConventionalView`, `vtkMRMLScene::SafeDownCast`

## widget: CentralWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: CentralWidget | QWidget
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:233: QFrame* layoutFrame = new QFrame(this->CentralWidget);`
  - `Base/QTApp/qSlicerMainWindow.cxx:234: layoutFrame->setObjectName("CentralWidgetLayoutFrame");`
  - `Base/QTApp/qSlicerMainWindow.cxx:235: QHBoxLayout* centralLayout = new QHBoxLayout(this->CentralWidget);`
  - `Base/QTApp/qSlicerMainWindow_p.h:89: // In case of a custom CentralWidget is used, the layout manager may get deleted.`

## widget: StatusBar

- Confidence: `linked_to_code`
- Widget/action class: `QStatusBar`
- Search text: StatusBar | QStatusBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:124: this->setupStatusBar();`
  - `Base/QTApp/qSlicerMainWindow.cxx:159: this->AppearanceMenu->insertAction(this->ShowStatusBarAction, this->PanelDockWidget->toggleViewAction());`
  - `Base/QTApp/qSlicerMainWindow.cxx:697: void qSlicerMainWindowPrivate::setupStatusBar()`
  - `Base/QTApp/qSlicerMainWindow.cxx:873: void qSlicerMainWindow::on_ShowStatusBarAction_triggered(bool toggled)`
  - `Base/QTApp/qSlicerMainWindow.h:118: virtual void on_ShowStatusBarAction_triggered(bool);`
  - `Base/QTApp/qSlicerMainWindow_p.h:54: virtual void setupStatusBar();`

## widget: PanelDockWidget

- Confidence: `linked_to_slot`
- Widget/action class: `QDockWidget`
- Search text: PanelDockWidget | QDockWidget
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:155: this->PanelDockWidget->toggleViewAction()->setText(qSlicerMainWindow::tr("Show &Module Panel"));`
  - `Base/QTApp/qSlicerMainWindow.cxx:156: this->PanelDockWidget->toggleViewAction()->setToolTip(qSlicerMainWindow::tr("Collapse/Expand the GUI panel and allows Slicer's viewers to occupy "`
  - `Base/QTApp/qSlicerMainWindow.cxx:158: this->PanelDockWidget->toggleViewAction()->setShortcut(QKeySequence("Ctrl+5"));`
  - `Base/QTApp/qSlicerMainWindow.cxx:159: this->AppearanceMenu->insertAction(this->ShowStatusBarAction, this->PanelDockWidget->toggleViewAction());`
  - `Base/QTApp/qSlicerMainWindow.cxx:191: QObject::connect(this->ModuleSelectorToolBar, SIGNAL(moduleSelected(QString)), this->PanelDockWidget, SLOT(show()));`
- Connected slots/functions: `show`

## widget: dockWidgetContents

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: dockWidgetContents | QWidget
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## widget: ModulePanel

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerModulePanel`
- Search text: ModulePanel | qSlicerModulePanel
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:153: // ModulePanel`
  - `Base/QTApp/qSlicerMainWindow.cxx:187: this->ModulePanel->setModuleManager(moduleManager);`
  - `Base/QTApp/qSlicerMainWindow.cxx:188: QObject::connect(this->ModuleSelectorToolBar, SIGNAL(moduleSelected(QString)), this->ModulePanel, SLOT(setModule(QString)));`
- Connected slots/functions: `setModule`

## widget: DataProbeCollapsibleWidget

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Data Probe | DataProbeCollapsibleWidget | ctkCollapsibleButton
- Text: Data Probe
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## widget: MainToolBar

- Confidence: `linked_to_code`
- Widget/action class: `QToolBar`
- Search text: MainToolBar | QToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:202: toolBarActions << this->MainToolBar->toggleViewAction();`

## widget: ModuleToolBar

- Confidence: `linked_to_code`
- Widget/action class: `QToolBar`
- Search text: ModuleToolBar | QToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:183: q->insertToolBar(this->ModuleToolBar, this->ModuleSelectorToolBar);`
  - `Base/QTApp/qSlicerMainWindow.cxx:184: this->ModuleSelectorToolBar->stackUnder(this->ModuleToolBar);`
  - `Base/QTApp/qSlicerMainWindow.cxx:205: toolBarActions << this->ModuleToolBar->toggleViewAction();`
  - `Base/QTApp/qSlicerMainWindow.cxx:749: for (QAction* const toolBarAction : this->ModuleToolBar->actions())`
  - `Base/QTApp/qSlicerMainWindow.cxx:759: this->ModuleToolBar->insertAction(beforeAction, action);`
  - `Base/QTApp/qSlicerMainWindow.cxx:760: action->setParent(this->ModuleToolBar);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1530: for (QAction* const action : d->ModuleToolBar->actions())`
  - `Base/QTApp/qSlicerMainWindow.cxx:1534: d->ModuleToolBar->removeAction(action);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1775: d->ModuleToolBar->clear();`

## widget: UndoRedoToolBar

- Confidence: `linked_to_code`
- Widget/action class: `QToolBar`
- Search text: UndoRedoToolBar | QToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:203: // toolBarActions << this->UndoRedoToolBar->toggleViewAction();`
  - `Base/QTApp/qSlicerMainWindow.cxx:223: this->UndoRedoToolBar->toggleViewAction()->trigger();`
  - `Base/QTApp/qSlicerMainWindow.cxx:225: // q->removeToolBar(this->UndoRedoToolBar);`
  - `Base/QTApp/qSlicerMainWindow.cxx:227: delete this->UndoRedoToolBar;`
  - `Base/QTApp/qSlicerMainWindow.cxx:228: this->UndoRedoToolBar = nullptr;`

## widget: ViewToolBar

- Confidence: `linked_to_slot`
- Widget/action class: `QToolBar`
- Search text: ViewToolBar | QToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:206: toolBarActions << this->ViewToolBar->toggleViewAction();`
  - `Base/QTApp/qSlicerMainWindow.cxx:302: this->ViewToolBar->addWidget(this->LayoutButton);`
  - `Base/QTApp/qSlicerMainWindow.cxx:303: QObject::connect(this->ViewToolBar, SIGNAL(toolButtonStyleChanged(Qt::ToolButtonStyle)), this->LayoutButton, SLOT(setToolButtonStyle(Qt::ToolButtonStyle)));`
- Connected slots/functions: `setToolButtonStyle`

## widget: MouseModeToolBar

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerMouseModeToolBar`
- Search text: MouseModeToolBar | qSlicerMouseModeToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:197: this->MouseModeToolBar->setApplicationLogic(qSlicerApplication::application()->applicationLogic());`
  - `Base/QTApp/qSlicerMainWindow.cxx:198: this->MouseModeToolBar->setMRMLScene(qSlicerApplication::application()->mrmlScene());`
  - `Base/QTApp/qSlicerMainWindow.cxx:199: QObject::connect(qSlicerApplication::application(), SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->MouseModeToolBar, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Base/QTApp/qSlicerMainWindow.cxx:208: toolBarActions << this->MouseModeToolBar->toggleViewAction();`
- Connected slots/functions: `setMRMLScene`

## widget: ViewersToolBar

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerViewersToolBar`
- Search text: ViewersToolBar | qSlicerViewersToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:209: toolBarActions << this->ViewersToolBar->toggleViewAction();`
  - `Base/QTApp/qSlicerMainWindow.cxx:309: this->ViewersToolBar->setApplicationLogic(qSlicerApplication::application()->applicationLogic());`
  - `Base/QTApp/qSlicerMainWindow.cxx:310: this->ViewersToolBar->setMRMLScene(qSlicerApplication::application()->mrmlScene());`
  - `Base/QTApp/qSlicerMainWindow.cxx:311: QObject::connect(qSlicerApplication::application(), SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->ViewersToolBar, SLOT(setMRMLScene(vtkMRMLScene*)));`
- Connected slots/functions: `setMRMLScene`

## widget: DialogToolBar

- Confidence: `linked_to_code`
- Widget/action class: `QToolBar`
- Search text: DialogToolBar | QToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:210: toolBarActions << this->DialogToolBar->toggleViewAction();`
  - `Base/QTApp/qSlicerMainWindow.cxx:414: this->DialogToolBar->addAction(this->PythonConsoleToggleViewAction);`

## widget: LayoutToolBar

- Confidence: `linked_to_code`
- Widget/action class: `QToolBar`
- Search text: LayoutToolBar | QToolBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:207: // toolBarActions << this->LayoutToolBar->toggleViewAction();`
  - `Base/QTApp/qSlicerMainWindow.cxx:224: this->LayoutToolBar->toggleViewAction()->trigger();`
  - `Base/QTApp/qSlicerMainWindow.cxx:226: // q->removeToolBar(this->LayoutToolBar);`
  - `Base/QTApp/qSlicerMainWindow.cxx:229: delete this->LayoutToolBar;`
  - `Base/QTApp/qSlicerMainWindow.cxx:230: this->LayoutToolBar = nullptr;`

## widget: menubar

- Confidence: `ui_only`
- Widget/action class: `QMenuBar`
- Search text: menubar | QMenuBar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## widget: FileMenu

- Confidence: `ui_only`
- Widget/action class: `QMenu`
- Search text: FileMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## widget: RecentlyLoadedMenu

- Confidence: `linked_to_slot`
- Widget/action class: `QMenu`
- Search text: RecentlyLoadedMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:482: void qSlicerMainWindowPrivate::setupRecentlyLoadedMenu(const QList<qSlicerIO::IOProperties>& fileProperties)`
  - `Base/QTApp/qSlicerMainWindow.cxx:486: this->RecentlyLoadedMenu->setEnabled(fileProperties.size() > 0);`
  - `Base/QTApp/qSlicerMainWindow.cxx:487: this->RecentlyLoadedMenu->clear();`
  - `Base/QTApp/qSlicerMainWindow.cxx:499: QAction* action = this->RecentlyLoadedMenu->addAction(fileName, q, SLOT(onFileRecentLoadedActionTriggered()));`
  - `Base/QTApp/qSlicerMainWindow.cxx:505: this->RecentlyLoadedMenu->addSeparator();`
  - `Base/QTApp/qSlicerMainWindow.cxx:506: QAction* clearAction = this->RecentlyLoadedMenu->addAction(qSlicerMainWindow::tr("Clear History"), q, SLOT(onFileRecentLoadedActionTriggered()));`
  - `Base/QTApp/qSlicerMainWindow.cxx:1167: d->setupRecentlyLoadedMenu(d->RecentlyLoadedFileProperties);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1432: d->setupRecentlyLoadedMenu(d->RecentlyLoadedFileProperties);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1662: d->setupRecentlyLoadedMenu(d->RecentlyLoadedFileProperties);`
  - `Base/QTApp/qSlicerMainWindow_p.h:56: virtual void setupRecentlyLoadedMenu(const QList<qSlicerIO::IOProperties>& fileProperties);`
- Connected slots/functions: `onFileRecentLoadedActionTriggered`

## widget: EditMenu

- Confidence: `ui_only`
- Widget/action class: `QMenu`
- Search text: EditMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## widget: ViewMenu

- Confidence: `linked_to_code`
- Widget/action class: `QMenu`
- Search text: ViewMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:370: this->ViewMenu->insertAction(this->ModuleHomeAction, this->ErrorLogToggleViewAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:401: this->PythonConsoleToggleViewAction = new QAction("", this->ViewMenu);`
  - `Base/QTApp/qSlicerMainWindow.cxx:412: this->ViewMenu->insertAction(this->ModuleHomeAction, this->PythonConsoleToggleViewAction);`

## widget: LayoutMenu

- Confidence: `linked_to_slot`
- Widget/action class: `QMenu`
- Search text: LayoutMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:295: this->LayoutButton->setMenu(this->LayoutMenu);`
  - `Base/QTApp/qSlicerMainWindow.cxx:300: QObject::connect(this->LayoutMenu, SIGNAL(triggered(QAction*)), q, SLOT(onLayoutActionTriggered(QAction*)));`
  - `Base/QTApp/qSlicerMainWindow.cxx:1561: for (QAction* const maction : d->LayoutMenu->actions())`
  - `Base/QTApp/qSlicerMainWindow.cxx:1615: for (QAction* const action : d->LayoutMenu->actions())`
- Connected slots/functions: `onLayoutActionTriggered`

## widget: WindowToolBarsMenu

- Confidence: `linked_to_code`
- Widget/action class: `QMenu`
- Search text: WindowToolBarsMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:211: this->WindowToolBarsMenu->addActions(toolBarActions);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1361: d->WindowToolBarsMenu->removeAction(d->ViewExtensionsManagerAction);`

## widget: AppearanceMenu

- Confidence: `linked_to_code`
- Widget/action class: `QMenu`
- Search text: AppearanceMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:159: this->AppearanceMenu->insertAction(this->ShowStatusBarAction, this->PanelDockWidget->toggleViewAction());`

## widget: HelpMenu

- Confidence: `ui_only`
- Widget/action class: `QMenu`
- Search text: HelpMenu | QMenu
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## action: FileLoadSceneAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Load Scene | Raise a file browser to select a scene (mrml, xcat or xml) to load. It first clears any existing scene in Slicer and resets the application state. | FileLoadSceneAction
- Text: Load Scene
- Tooltip: Raise a file browser to select a scene (mrml, xcat or xml) to load. It first clears any existing scene in Slicer and resets the application state.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:903: void qSlicerMainWindow::on_FileLoadSceneAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:76: virtual void on_FileLoadSceneAction_triggered();`

## action: FileLoadDataAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Load Data | Raise an "Add Data" widget that allows you to select individual datasets to add to the existing scene. This load option is most useful when you want to load many different data types at once (volumes, models, etc.) which may not yet be described by a scene file. | FileLoadDataAction
- Text: Load Data
- Tooltip: Raise an "Add Data" widget that allows you to select individual datasets to add to the existing scene. This load option is most useful when you want to load many different data types at once (volumes, models, etc.) which may not yet be described by a scene file.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:891: void qSlicerMainWindow::on_FileLoadDataAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:74: virtual void on_FileLoadDataAction_triggered();`

## action: LoadDICOMAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Load DICOM | Raise the DICOM module for loading DICOM datasets. | LoadDICOMAction
- Text: Load DICOM
- Tooltip: Raise the DICOM module for loading DICOM datasets.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:149: this->LoadDICOMAction->setVisible(false);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1377: void qSlicerMainWindow::on_LoadDICOMAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:85: virtual void on_LoadDICOMAction_triggered();`

## action: FileImportSceneAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Import Scene | Raise a file browser to navigate and select a scene file to be added to the existing scene. The scene is not cleared. | FileImportSceneAction
- Text: Import Scene
- Tooltip: Raise a file browser to navigate and select a scene file to be added to the existing scene. The scene is not cleared.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:897: void qSlicerMainWindow::on_FileImportSceneAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:75: virtual void on_FileImportSceneAction_triggered();`

## action: FileAddDataAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: &Add Data | Raise an "Add Data" widget that allows you to select individual datasets to add to the existing scene. This load option is most useful when you want to load many different data types at once (volumes, models, etc.) which may not yet be described by a scene file. | FileAddDataAction
- Text: &Add Data
- Tooltip: Raise an "Add Data" widget that allows you to select individual datasets to add to the existing scene. This load option is most useful when you want to load many different data types at once (volumes, models, etc.) which may not yet be described by a scene file.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:885: void qSlicerMainWindow::on_FileAddDataAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:73: virtual void on_FileAddDataAction_triggered();`

## action: FileAddVolumeAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Add Volume | Raise an "Add Volume" widget that allows you to select a volumetric dataset to add to the existing scene. The "Volume Options" panel can be used to clarify how a selected dataset should be loaded and displayed. | FileAddVolumeAction
- Text: Add Volume
- Tooltip: Raise an "Add Volume" widget that allows you to select a volumetric dataset to add to the existing scene. The "Volume Options" panel can be used to clarify how a selected dataset should be loaded and displayed.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:909: void qSlicerMainWindow::on_FileAddVolumeAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:77: virtual void on_FileAddVolumeAction_triggered();`

## action: FileAddTransformAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Add Transform | Raise a standard file browser that allows you to select a transform to the existing scene. | FileAddTransformAction
- Text: Add Transform
- Tooltip: Raise a standard file browser that allows you to select a transform to the existing scene.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:915: void qSlicerMainWindow::on_FileAddTransformAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:78: virtual void on_FileAddTransformAction_triggered();`

## action: FileSaveSceneAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Save Data | Display the "Save Data" widget, which offers many options for saving a scene and/or individual datasets. | FileSaveSceneAction
- Text: Save Data
- Tooltip: Display the "Save Data" widget, which offers many options for saving a scene and/or individual datasets.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:586: this->FileSaveSceneAction->trigger();`
  - `Base/QTApp/qSlicerMainWindow.cxx:921: void qSlicerMainWindow::on_FileSaveSceneAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:79: virtual void on_FileSaveSceneAction_triggered();`

## action: SDBSaveToDirectoryAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Save Scene To Directory | UNDER CONSTRUCTION: Save the current scene to a stand alone directory. | SDBSaveToDirectoryAction
- Text: Save Scene To Directory
- Tooltip: UNDER CONSTRUCTION: Save the current scene to a stand alone directory.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:933: void qSlicerMainWindow::on_SDBSaveToDirectoryAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:82: virtual void on_SDBSaveToDirectoryAction_triggered();`

## action: SDBSaveToMRBAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Save Scene to MRB File | Create a Medical Reality Bundle containing the scene. | SDBSaveToMRBAction
- Text: Save Scene to MRB File
- Tooltip: Create a Medical Reality Bundle containing the scene.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:961: void qSlicerMainWindow::on_SDBSaveToMRBAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:83: virtual void on_SDBSaveToMRBAction_triggered();`

## action: FileCloseSceneAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Close Scene | Close the current scene and reset the application state.  | FileCloseSceneAction
- Text: Close Scene
- Tooltip: Close the current scene and reset the application state. 
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:985: void qSlicerMainWindow::on_FileCloseSceneAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:84: virtual void on_FileCloseSceneAction_triggered();`

## action: FileExitAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: E&xit | Quit the application | FileExitAction
- Text: E&xit
- Tooltip: Quit the application
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:330: setThemeIcon(this->FileExitAction, "application-exit");`
  - `Base/QTApp/qSlicerMainWindow.cxx:927: void qSlicerMainWindow::on_FileExitAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:80: virtual void on_FileExitAction_triggered();`

## action: EditUndoAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Undo | Undo the history of undoable commands, from last to first. | EditUndoAction
- Text: Undo
- Tooltip: Undo the history of undoable commands, from last to first.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:331: setThemeIcon(this->EditUndoAction, "edit-undo");`
  - `Base/QTApp/qSlicerMainWindow.cxx:1018: void qSlicerMainWindow::on_EditUndoAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.cxx:1551: // d->EditUndoAction->setEnabled(scene && scene->GetNumberOfUndoLevels());`
  - `Base/QTApp/qSlicerMainWindow.h:89: virtual void on_EditUndoAction_triggered();`
- API footprints: `GetNumberOfRedoLevels`, `GetNumberOfUndoLevels`, `Undo`

## action: EditRedoAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Redo | Redo the history of commands most recently undone, from last to first. | EditRedoAction
- Text: Redo
- Tooltip: Redo the history of commands most recently undone, from last to first.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:332: setThemeIcon(this->EditRedoAction, "edit-redo");`
  - `Base/QTApp/qSlicerMainWindow.cxx:1024: void qSlicerMainWindow::on_EditRedoAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.cxx:1552: // d->EditRedoAction->setEnabled(scene && scene->GetNumberOfRedoLevels());`
  - `Base/QTApp/qSlicerMainWindow.h:90: virtual void on_EditRedoAction_triggered();`
- API footprints: `GetNumberOfRedoLevels`, `GetNumberOfUndoLevels`, `Redo`

## action: ViewExtensionsManagerAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Extensions Manager | Raise the "Extensions Manager" wizard that provides status and information about available extensions | ViewExtensionsManagerAction
- Text: Extensions Manager
- Tooltip: Raise the "Extensions Manager" wizard that provides status and information about available extensions
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1358: d->ViewExtensionsManagerAction->setVisible(app->revisionUserSettings()->value("Extensions/ManagerEnabled").toBool());`
  - `Base/QTApp/qSlicerMainWindow.cxx:1360: d->ViewExtensionsManagerAction->setVisible(false);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1361: d->WindowToolBarsMenu->removeAction(d->ViewExtensionsManagerAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1501: void qSlicerMainWindow::on_ViewExtensionsManagerAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.cxx:1748: if (d->ViewExtensionsManagerAction->property(extensionUpdateAvailablePropertyName).toBool() == updateAvailable)`
  - `Base/QTApp/qSlicerMainWindow.cxx:1753: d->ViewExtensionsManagerAction->setProperty(extensionUpdateAvailablePropertyName, updateAvailable);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1757: d->ViewExtensionsManagerAction->setIcon(QIcon(":/Icons/ExtensionNotificationIcon.png"));`
  - `Base/QTApp/qSlicerMainWindow.cxx:1761: d->ViewExtensionsManagerAction->setIcon(QIcon(":/Icons/ExtensionDefaultIcon.png"));`
  - `Base/QTApp/qSlicerMainWindow.h:116: virtual void on_ViewExtensionsManagerAction_triggered();`

## action: ViewCacheRemoteIOManagerAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Cache & Remote I/O Manager | The Cache and Remote Data Handling interface provides status and information about all remote data transfers, and allows some control over the local cache. | ViewCacheRemoteIOManagerAction
- Text: Cache & Remote I/O Manager
- Tooltip: The Cache and Remote Data Handling interface provides status and information about all remote data transfers, and allows some control over the local cache.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## action: FileFavoriteModulesAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Favorite Modules | Open settings to the Modules panel where Favorite Modules can be defined. | FileFavoriteModulesAction
- Text: Favorite Modules
- Tooltip: Open settings to the Modules panel where Favorite Modules can be defined.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:879: void qSlicerMainWindow::on_FileFavoriteModulesAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:72: virtual void on_FileFavoriteModulesAction_triggered();`

## action: EditApplicationSettingsAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Application Settings | The Application Settings provides options for controlling the application's user interface preferences into the application registry, so they are preserved across sessions. | EditApplicationSettingsAction
- Text: Application Settings
- Tooltip: The Application Settings provides options for controlling the application's user interface preferences into the application registry, so they are preserved across sessions.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:336: setThemeIcon(this->EditApplicationSettingsAction, "preferences-system");`
  - `Base/QTApp/qSlicerMainWindow.cxx:1398: void qSlicerMainWindow::on_EditApplicationSettingsAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:112: virtual void on_EditApplicationSettingsAction_triggered();`

## action: CutAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Cut | Cut currently selected item and place in clipboard | CutAction
- Text: Cut
- Tooltip: Cut currently selected item and place in clipboard
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:326: this->CutAction->setShortcutContext(Qt::WidgetWithChildrenShortcut);`
  - `Base/QTApp/qSlicerMainWindow.cxx:333: setThemeIcon(this->CutAction, "edit-cut");`
  - `Base/QTApp/qSlicerMainWindow.cxx:1490: void qSlicerMainWindow::on_CutAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:113: virtual void on_CutAction_triggered();`

## action: CopyAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Copy | Copy currently selected item to clipboard | CopyAction
- Text: Copy
- Tooltip: Copy currently selected item to clipboard
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:327: this->CopyAction->setShortcutContext(Qt::WidgetWithChildrenShortcut);`
  - `Base/QTApp/qSlicerMainWindow.cxx:334: setThemeIcon(this->CopyAction, "edit-copy");`
  - `Base/QTApp/qSlicerMainWindow.cxx:1468: void qSlicerMainWindow::on_CopyAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:114: virtual void on_CopyAction_triggered();`

## action: PasteAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Paste | Paste the current contents of the clipboard | PasteAction
- Text: Paste
- Tooltip: Paste the current contents of the clipboard
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:328: this->PasteAction->setShortcutContext(Qt::WidgetWithChildrenShortcut);`
  - `Base/QTApp/qSlicerMainWindow.cxx:335: setThemeIcon(this->PasteAction, "edit-paste");`
  - `Base/QTApp/qSlicerMainWindow.cxx:1479: void qSlicerMainWindow::on_PasteAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:115: virtual void on_PasteAction_triggered();`

## action: WindowMaximizeViewAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: &Maximize view | Maximize/Minimize the current view. | WindowMaximizeViewAction
- Text: &Maximize view
- Tooltip: Maximize/Minimize the current view.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Key UI properties: {"checkable": "true", "checked": "true"}

## action: FeedbackReportUsabilityIssueAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Feedback: report usability issue (www) | Create a topic at the Slicer forum (https://discourse.slicer.org) to report any usability issues and make suggestions how to address them. | FeedbackReportUsabilityIssueAction
- Text: Feedback: report usability issue (www)
- Tooltip: Create a topic at the Slicer forum (https://discourse.slicer.org) to report any usability issues and make suggestions how to address them.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## action: FeedbackMakeFeatureRequestAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Feedback: make a feature request (www) | Create a topic at the Slicer forum (https://discourse.slicer.org) to request a new feature. | FeedbackMakeFeatureRequestAction
- Text: Feedback: make a feature request (www)
- Tooltip: Create a topic at the Slicer forum (https://discourse.slicer.org) to request a new feature.
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## action: DebugLoadModuleAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Load Module | DebugLoadModuleAction
- Text: Load Module
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`

## action: ViewLayoutConventionalAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Conventional | ViewLayoutConventionalAction
- Text: Conventional
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:298: this->LayoutButton->setDefaultAction(this->ViewLayoutConventionalAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1304: d->ViewLayoutConventionalAction->setData(vtkMRMLLayoutNode::SlicerLayoutConventionalView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutConventionalPlotView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalWidescreenView`

## action: ViewLayoutFourUpAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four-Up | ViewLayoutFourUpAction
- Text: Four-Up
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1307: d->ViewLayoutFourUpAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourUpView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutConventionalPlotView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalWidescreenView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpView`

## action: ViewLayoutDual3DAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Dual 3D | ViewLayoutDual3DAction
- Text: Dual 3D
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1311: d->ViewLayoutDual3DAction->setData(vtkMRMLLayoutNode::SlicerLayoutDual3DView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDual3DView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpTableView`, `vtkMRMLLayoutNode::SlicerLayoutOneUp3DView`, `vtkMRMLLayoutNode::SlicerLayoutTriple3DEndoscopyView`

## action: ViewLayoutOneUp3DAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: 3D only | ViewLayoutOneUp3DAction
- Text: 3D only
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1313: d->ViewLayoutOneUp3DAction->setData(vtkMRMLLayoutNode::SlicerLayoutOneUp3DView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayout3DTableView`, `vtkMRMLLayoutNode::SlicerLayoutDual3DView`, `vtkMRMLLayoutNode::SlicerLayoutOneUp3DView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutTriple3DEndoscopyView`

## action: ViewLayout3DTableAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: 3D Table | ViewLayout3DTableAction
- Text: 3D Table
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1314: d->ViewLayout3DTableAction->setData(vtkMRMLLayoutNode::SlicerLayout3DTableView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayout3DTableView`, `vtkMRMLLayoutNode::SlicerLayoutOneUp3DView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpRedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutTriple3DEndoscopyView`

## action: ViewLayoutOneUpRedSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Red slice only | ViewLayoutOneUpRedSliceAction
- Text: Red slice only
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1316: d->ViewLayoutOneUpRedSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutOneUpRedSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayout3DTableView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpGreenSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpRedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpYellowSliceView`

## action: ViewLayoutOneUpYellowSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Yellow slice only | ViewLayoutOneUpYellowSliceAction
- Text: Yellow slice only
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1317: d->ViewLayoutOneUpYellowSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutOneUpYellowSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutOneUpGreenSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpRedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpYellowSliceView`, `vtkMRMLLayoutNode::SlicerLayoutTabbed3DView`

## action: ViewLayoutOneUpGreenSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Green slice only | ViewLayoutOneUpGreenSliceAction
- Text: Green slice only
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1318: d->ViewLayoutOneUpGreenSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutOneUpGreenSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutOneUpGreenSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpRedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpYellowSliceView`, `vtkMRMLLayoutNode::SlicerLayoutTabbed3DView`, `vtkMRMLLayoutNode::SlicerLayoutTabbedSliceView`

## action: ViewLayoutTabbed3DAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Tabbed 3D | ViewLayoutTabbed3DAction
- Text: Tabbed 3D
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1319: d->ViewLayoutTabbed3DAction->setData(vtkMRMLLayoutNode::SlicerLayoutTabbed3DView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutCompareView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpGreenSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpYellowSliceView`, `vtkMRMLLayoutNode::SlicerLayoutTabbed3DView`, `vtkMRMLLayoutNode::SlicerLayoutTabbedSliceView`

## action: ViewLayoutTabbedSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Tabbed slice | ViewLayoutTabbedSliceAction
- Text: Tabbed slice
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1320: d->ViewLayoutTabbedSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutTabbedSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutCompareGridView`, `vtkMRMLLayoutNode::SlicerLayoutCompareView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpGreenSliceView`, `vtkMRMLLayoutNode::SlicerLayoutTabbed3DView`, `vtkMRMLLayoutNode::SlicerLayoutTabbedSliceView`

## action: ViewLayoutCompareAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Compare | ViewLayoutCompareAction
- Text: Compare
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:274: this->ViewLayoutCompareAction->setMenu(compareMenu);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1321: d->ViewLayoutCompareAction->setData(vtkMRMLLayoutNode::SlicerLayoutCompareView);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1585: this->setLayout(d->ViewLayoutCompareAction->data().toInt());`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutCompareGridView`, `vtkMRMLLayoutNode::SlicerLayoutCompareView`, `vtkMRMLLayoutNode::SlicerLayoutTabbed3DView`, `vtkMRMLLayoutNode::SlicerLayoutTabbedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreeView`

## action: ViewLayoutTwoOverTwoAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Two over two | Two over Two Layout | ViewLayoutTwoOverTwoAction
- Text: Two over two
- Tooltip: Two over Two Layout
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1326: d->ViewLayoutTwoOverTwoAction->setData(vtkMRMLLayoutNode::SlicerLayoutTwoOverTwoView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutFourByThreeSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourOverFourView`, `vtkMRMLLayoutNode::SlicerLayoutSideBySideView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreePlotView`, `vtkMRMLLayoutNode::SlicerLayoutTwoOverTwoView`

## action: ModuleHomeAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Home | Favorite module for easy access | ModuleHomeAction
- Text: Home
- Tooltip: Favorite module for easy access
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:337: setThemeIcon(this->ModuleHomeAction, "go-home");`
  - `Base/QTApp/qSlicerMainWindow.cxx:370: this->ViewMenu->insertAction(this->ModuleHomeAction, this->ErrorLogToggleViewAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:412: this->ViewMenu->insertAction(this->ModuleHomeAction, this->PythonConsoleToggleViewAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1030: void qSlicerMainWindow::on_ModuleHomeAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:92: virtual void on_ModuleHomeAction_triggered();`

## action: ViewLayoutConventionalWidescreenAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Conventional Widescreen | ViewLayoutConventionalWidescreenAction
- Text: Conventional Widescreen
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1305: d->ViewLayoutConventionalWidescreenAction->setData(vtkMRMLLayoutNode::SlicerLayoutConventionalWidescreenView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutConventionalPlotView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalWidescreenView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpView`

## action: ViewLayoutTriple3DAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Triple 3D | ViewLayoutTriple3DAction
- Text: Triple 3D
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1312: d->ViewLayoutTriple3DAction->setData(vtkMRMLLayoutNode::SlicerLayoutTriple3DEndoscopyView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayout3DTableView`, `vtkMRMLLayoutNode::SlicerLayoutDual3DView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpTableView`, `vtkMRMLLayoutNode::SlicerLayoutOneUp3DView`, `vtkMRMLLayoutNode::SlicerLayoutTriple3DEndoscopyView`

## action: ViewLayoutThreeOverThreeAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Three over three | ViewLayoutThreeOverThreeAction
- Text: Three over three
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1323: d->ViewLayoutThreeOverThreeAction->setData(vtkMRMLLayoutNode::SlicerLayoutThreeOverThreeView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutCompareGridView`, `vtkMRMLLayoutNode::SlicerLayoutCompareView`, `vtkMRMLLayoutNode::SlicerLayoutFourOverFourView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreePlotView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreeView`

## action: ViewLayoutFourOverFourAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four over four | ViewLayoutFourOverFourAction
- Text: Four over four
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1325: d->ViewLayoutFourOverFourAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourOverFourView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutFourOverFourView`, `vtkMRMLLayoutNode::SlicerLayoutSideBySideView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreePlotView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreeView`, `vtkMRMLLayoutNode::SlicerLayoutTwoOverTwoView`

## action: ViewLayoutCompare_2_viewersAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: 2 viewers | ViewLayoutCompare_2_viewersAction
- Text: 2 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:267: compareMenu->addAction(this->ViewLayoutCompare_2_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1334: d->ViewLayoutCompare_2_viewersAction->setData(2);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDualMonitorFourUpView`

## action: ViewLayoutCompare_3_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 3 viewers | ViewLayoutCompare_3_viewersAction
- Text: 3 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:268: compareMenu->addAction(this->ViewLayoutCompare_3_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1335: d->ViewLayoutCompare_3_viewersAction->setData(3);`

## action: ViewLayoutCompare_4_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 4 viewers | ViewLayoutCompare_4_viewersAction
- Text: 4 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:269: compareMenu->addAction(this->ViewLayoutCompare_4_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1336: d->ViewLayoutCompare_4_viewersAction->setData(4);`

## action: ViewLayoutCompare_5_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 5 viewers | ViewLayoutCompare_5_viewersAction
- Text: 5 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:270: compareMenu->addAction(this->ViewLayoutCompare_5_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1337: d->ViewLayoutCompare_5_viewersAction->setData(5);`

## action: ViewLayoutCompare_6_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 6 viewers | ViewLayoutCompare_6_viewersAction
- Text: 6 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:271: compareMenu->addAction(this->ViewLayoutCompare_6_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1338: d->ViewLayoutCompare_6_viewersAction->setData(6);`

## action: ViewLayoutCompare_7_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 7 viewers | ViewLayoutCompare_7_viewersAction
- Text: 7 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:272: compareMenu->addAction(this->ViewLayoutCompare_7_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1339: d->ViewLayoutCompare_7_viewersAction->setData(7);`

## action: ViewLayoutCompare_8_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 8 viewers | ViewLayoutCompare_8_viewersAction
- Text: 8 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:273: compareMenu->addAction(this->ViewLayoutCompare_8_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1340: d->ViewLayoutCompare_8_viewersAction->setData(8);`

## action: ViewLayoutCompareGridAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Compare Grid | ViewLayoutCompareGridAction
- Text: Compare Grid
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:283: this->ViewLayoutCompareGridAction->setMenu(compareMenu);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1322: d->ViewLayoutCompareGridAction->setData(vtkMRMLLayoutNode::SlicerLayoutCompareGridView);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1598: this->setLayout(d->ViewLayoutCompareGridAction->data().toInt());`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutCompareGridView`, `vtkMRMLLayoutNode::SlicerLayoutCompareView`, `vtkMRMLLayoutNode::SlicerLayoutTabbedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreePlotView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreeView`

## action: ViewLayoutCompareGrid_2x2_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 2x2 viewers | ViewLayoutCompareGrid_2x2_viewersAction
- Text: 2x2 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:280: compareMenu->addAction(this->ViewLayoutCompareGrid_2x2_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1342: d->ViewLayoutCompareGrid_2x2_viewersAction->setData(2);`

## action: ViewLayoutCompareGrid_3x3_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 3x3 viewers | ViewLayoutCompareGrid_3x3_viewersAction
- Text: 3x3 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:281: compareMenu->addAction(this->ViewLayoutCompareGrid_3x3_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1343: d->ViewLayoutCompareGrid_3x3_viewersAction->setData(3);`

## action: ViewLayoutCompareGrid_4x4_viewersAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: 4x4 viewers | ViewLayoutCompareGrid_4x4_viewersAction
- Text: 4x4 viewers
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:282: compareMenu->addAction(this->ViewLayoutCompareGrid_4x4_viewersAction);`
  - `Base/QTApp/qSlicerMainWindow.cxx:1344: d->ViewLayoutCompareGrid_4x4_viewersAction->setData(4);`

## action: EditRecordMacroAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Record Macro | EditRecordMacroAction
- Text: Record Macro
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1002: void qSlicerMainWindow::on_EditRecordMacroAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.cxx:1369: d->EditRecordMacroAction->setVisible(true);`
  - `Base/QTApp/qSlicerMainWindow.h:87: virtual void on_EditRecordMacroAction_triggered();`

## action: EditPlayMacroAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Play Macro | EditPlayMacroAction
- Text: Play Macro
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1010: void qSlicerMainWindow::on_EditPlayMacroAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.cxx:1368: d->EditPlayMacroAction->setVisible(true);`
  - `Base/QTApp/qSlicerMainWindow.h:88: virtual void on_EditPlayMacroAction_triggered();`

## action: ViewLayoutSideBySideAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Side by side | ViewLayoutSideBySideAction
- Text: Side by side
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1327: d->ViewLayoutSideBySideAction->setData(vtkMRMLLayoutNode::SlicerLayoutSideBySideView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutFourByThreeSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourOverFourView`, `vtkMRMLLayoutNode::SlicerLayoutSideBySideView`, `vtkMRMLLayoutNode::SlicerLayoutTwoOverTwoView`

## action: ViewLayoutFourByThreeSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four by three slice | Four by three slice | ViewLayoutFourByThreeSliceAction
- Text: Four by three slice
- Tooltip: Four by three slice
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1328: d->ViewLayoutFourByThreeSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourByThreeSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutFiveByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByThreeSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutSideBySideView`, `vtkMRMLLayoutNode::SlicerLayoutTwoOverTwoView`

## action: ViewLayoutFourByTwoSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four by two slice | Four by two slice | ViewLayoutFourByTwoSliceAction
- Text: Four by two slice
- Tooltip: Four by two slice
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1329: d->ViewLayoutFourByTwoSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourByTwoSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutFiveByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByThreeSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutSideBySideView`, `vtkMRMLLayoutNode::SlicerLayoutThreeByThreeSliceView`

## action: ViewLayoutFiveByTwoSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Five by two slice | Five by two slice | ViewLayoutFiveByTwoSliceAction
- Text: Five by two slice
- Tooltip: Five by two slice
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1330: d->ViewLayoutFiveByTwoSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutFiveByTwoSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDualMonitorFourUpView`, `vtkMRMLLayoutNode::SlicerLayoutFiveByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByThreeSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutThreeByThreeSliceView`

## action: ViewLayoutThreeByThreeSliceAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Three by three slice | Three by three slice | ViewLayoutThreeByThreeSliceAction
- Text: Three by three slice
- Tooltip: Three by three slice
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1331: d->ViewLayoutThreeByThreeSliceAction->setData(vtkMRMLLayoutNode::SlicerLayoutThreeByThreeSliceView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDualMonitorFourUpView`, `vtkMRMLLayoutNode::SlicerLayoutFiveByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutFourByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutThreeByThreeSliceView`

## action: ViewLayoutDualMonitorFourUpViewAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Dual-monitor Four-Up | Dual-monitor Four-Up | ViewLayoutDualMonitorFourUpViewAction
- Text: Dual-monitor Four-Up
- Tooltip: Dual-monitor Four-Up
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1332: d->ViewLayoutDualMonitorFourUpViewAction->setData(vtkMRMLLayoutNode::SlicerLayoutDualMonitorFourUpView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDualMonitorFourUpView`, `vtkMRMLLayoutNode::SlicerLayoutFiveByTwoSliceView`, `vtkMRMLLayoutNode::SlicerLayoutThreeByThreeSliceView`

## action: ViewLayoutOneUpPlotAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Plot only | Plot view | ViewLayoutOneUpPlotAction
- Text: Plot only
- Tooltip: Plot view
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1315: d->ViewLayoutOneUpPlotAction->setData(vtkMRMLLayoutNode::SlicerLayoutOneUpPlotView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayout3DTableView`, `vtkMRMLLayoutNode::SlicerLayoutOneUp3DView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpRedSliceView`, `vtkMRMLLayoutNode::SlicerLayoutOneUpYellowSliceView`

## action: ViewLayoutFourUpPlotAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four-Up Plot | Three slices and a plot in four-Up layout | ViewLayoutFourUpPlotAction
- Text: Four-Up Plot
- Tooltip: Three slices and a plot in four-Up layout
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1308: d->ViewLayoutFourUpPlotAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourUpPlotView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutConventionalPlotView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpView`

## action: ViewLayoutConventionalPlotAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Conventional Plot | Conventional three slices and 3D view with an additional plot | ViewLayoutConventionalPlotAction
- Text: Conventional Plot
- Tooltip: Conventional three slices and 3D view with an additional plot
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1306: d->ViewLayoutConventionalPlotAction->setData(vtkMRMLLayoutNode::SlicerLayoutConventionalPlotView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutConventionalPlotView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalView`, `vtkMRMLLayoutNode::SlicerLayoutConventionalWidescreenView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpView`

## action: ViewLayoutThreeOverThreePlotAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Three over three Plot | Three plots over three slices | ViewLayoutThreeOverThreePlotAction
- Text: Three over three Plot
- Tooltip: Three plots over three slices
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1324: d->ViewLayoutThreeOverThreePlotAction->setData(vtkMRMLLayoutNode::SlicerLayoutThreeOverThreePlotView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutCompareGridView`, `vtkMRMLLayoutNode::SlicerLayoutFourOverFourView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreePlotView`, `vtkMRMLLayoutNode::SlicerLayoutThreeOverThreeView`, `vtkMRMLLayoutNode::SlicerLayoutTwoOverTwoView`

## action: ViewLayoutFourUpTableAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four-Up Table | ViewLayoutFourUpTableAction
- Text: Four-Up Table
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1310: d->ViewLayoutFourUpTableAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourUpTableView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDual3DView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpTableView`, `vtkMRMLLayoutNode::SlicerLayoutTriple3DEndoscopyView`

## action: ViewLayoutFourUpPlotTableAction

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Four-Up Quantitative | Four-up slice and 3D view with an additional table and plot | ViewLayoutFourUpPlotTableAction
- Text: Four-Up Quantitative
- Tooltip: Four-up slice and 3D view with an additional table and plot
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1309: d->ViewLayoutFourUpPlotTableAction->setData(vtkMRMLLayoutNode::SlicerLayoutFourUpPlotTableView);`
- API footprints: `vtkMRMLLayoutNode::SlicerLayoutDual3DView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpPlotView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpTableView`, `vtkMRMLLayoutNode::SlicerLayoutFourUpView`

## action: WindowToolbarsResetToDefaultAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Reset to default | WindowToolbarsResetToDefaultAction
- Text: Reset to default
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:1149: void qSlicerMainWindow::on_WindowToolbarsResetToDefaultAction_triggered()`
  - `Base/QTApp/qSlicerMainWindow.h:110: virtual void on_WindowToolbarsResetToDefaultAction_triggered();`

## action: ShowStatusBarAction

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Show Status Bar | ShowStatusBarAction
- Text: Show Status Bar
- Implementation candidates: `Base/QTApp/qSlicerMainWindow.cxx`, `Base/QTApp/qSlicerMainWindow.h`, `Base/QTApp/qSlicerMainWindow_p.h`
- Matched implementation lines:
  - `Base/QTApp/qSlicerMainWindow.cxx:159: this->AppearanceMenu->insertAction(this->ShowStatusBarAction, this->PanelDockWidget->toggleViewAction());`
  - `Base/QTApp/qSlicerMainWindow.cxx:873: void qSlicerMainWindow::on_ShowStatusBarAction_triggered(bool toggled)`
  - `Base/QTApp/qSlicerMainWindow.h:118: virtual void on_ShowStatusBarAction_triggered(bool);`
- Key UI properties: {"checkable": "true", "checked": "true"}
