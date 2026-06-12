# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsModulesPanel.ui

- Owner class: `qSlicerSettingsModulesPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsModulesPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsModulesPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsModulesPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:34: #include "qSlicerSettingsModulesPanel.h"`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:35: #include "ui_qSlicerSettingsModulesPanel.h"`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:38: // qSlicerSettingsModulesPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:41: class qSlicerSettingsModulesPanelPrivate : public Ui_qSlicerSettingsModulesPanel`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:43: Q_DECLARE_PUBLIC(qSlicerSettingsModulesPanel);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:46: qSlicerSettingsModulesPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:49: qSlicerSettingsModulesPanelPrivate(qSlicerSettingsModulesPanel& object);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:57: // qSlicerSettingsModulesPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:60: qSlicerSettingsModulesPanelPrivate::qSlicerSettingsModulesPanelPrivate(qSlicerSettingsModulesPanel& object)`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:67: void qSlicerSettingsModulesPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:69: Q_Q(qSlicerSettingsModulesPanel);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:174: qSlicerSettingsModulesPanel::tr("Additional module paths"),`

## widget: LoadModulesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Skip loading of any: | LoadModulesLabel | QLabel
- Text: Skip loading of any:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: SkipLoadingContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: SkipLoadingContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: LoadLoadableModulesCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: loadable modules | To temporarily disable, pass --disable-loadable-modules on the command line | LoadLoadableModulesCheckBox | QCheckBox
- Text: loadable modules
- Tooltip: To temporarily disable, pass --disable-loadable-modules on the command line
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:132: this->LoadLoadableModulesCheckBox,`

## widget: LoadCommandLineModulesCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: command-line plugins | To temporarily disable, pass --disable-cli-modules on the command line | LoadCommandLineModulesCheckBox | QCheckBox
- Text: command-line plugins
- Tooltip: To temporarily disable, pass --disable-cli-modules on the command line
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:140: this->LoadCommandLineModulesCheckBox,`

## widget: LoadScriptedLoadableModulesCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: scripted loadable modules | To temporarily disable, pass  --disable-scripted-loadable-modules on the command line | LoadScriptedLoadableModulesCheckBox | QCheckBox
- Text: scripted loadable modules
- Tooltip: To temporarily disable, pass  --disable-scripted-loadable-modules on the command line
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:136: this->LoadScriptedLoadableModulesCheckBox,`

## widget: LoadBuildInModulesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Skip loading of builtin: | LoadBuildInModulesLabel | QLabel
- Text: Skip loading of builtin:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: SkipLoadingBuiltinContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: SkipLoadingBuiltinContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: LoadBuiltInLoadableModulesCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: loadable modules | To temporarily disable, pass --disable-builtin-loadable-modules on the command line | LoadBuiltInLoadableModulesCheckBox | QCheckBox
- Text: loadable modules
- Tooltip: To temporarily disable, pass --disable-builtin-loadable-modules on the command line
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:145: this->LoadBuiltInLoadableModulesCheckBox,`

## widget: LoadBuiltInCommandLineModulesCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: command-line plugins | To temporarily disable, pass --disable-builtin-cli-modules on the command line | LoadBuiltInCommandLineModulesCheckBox | QCheckBox
- Text: command-line plugins
- Tooltip: To temporarily disable, pass --disable-builtin-cli-modules on the command line
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:153: this->LoadBuiltInCommandLineModulesCheckBox,`

## widget: LoadBuiltInScriptedLoadableModulesCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: scripted loadable modules | To temporarily disable, pass  --disable-builtin-scripted-loadable-modules on the command line | LoadBuiltInScriptedLoadableModulesCheckBox | QCheckBox
- Text: scripted loadable modules
- Tooltip: To temporarily disable, pass  --disable-builtin-scripted-loadable-modules on the command line
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:149: this->LoadBuiltInScriptedLoadableModulesCheckBox,`

## widget: ShowHiddenModulesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show hidden modules: | ShowHiddenModulesLabel | QLabel
- Text: Show hidden modules:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: ShowHiddenContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: ShowHiddenContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: ShowHiddenModulesCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: ShowHiddenModulesCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:77: QObject::connect(this->ShowHiddenModulesCheckBox, SIGNAL(toggled(bool)), q, SLOT(onShowHiddenModulesChanged(bool)));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:166: this->ShowHiddenModulesCheckBox,`
- Connected slots/functions: `onShowHiddenModulesChanged`

## widget: TemporaryDirectoryLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Temporary directory: | TemporaryDirectoryLabel | QLabel
- Text: Temporary directory:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: TempDirContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: TempDirContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: TemporaryDirectoryButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkDirectoryButton`
- Search text: TemporaryDirectoryButton | ctkDirectoryButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:111: this->TemporaryDirectoryButton->setDirectory(coreApp->defaultTemporaryPath());`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:163: qSlicerRelativePathMapper* relativePathMapper = new qSlicerRelativePathMapper(this->TemporaryDirectoryButton, /*no tr*/ "directory", SIGNAL(directoryChanged(QString)));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:191: QObject::connect(this->TemporaryDirectoryButton, SIGNAL(directoryChanged(QString)), q, SLOT(onTemporaryPathChanged(QString)));`
- Connected slots/functions: `onTemporaryPathChanged`

## widget: AdditionalModulePathsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: <html><head/><body>
<p>Additional module paths:</p>
<p style="margin-left: 10px;"><span style=" font-size:small; font-style:italic;">Drag &amp; drop files or folders<br/>from File Explorer</span></p>
</body></html>
 | AdditionalModulePathsLabel | QLabel
- Text: <html><head/><body>
<p>Additional module paths:</p>
<p style="margin-left: 10px;"><span style=" font-size:small; font-style:italic;">Drag &amp; drop files or folders<br/>from File Explorer</span></p>
</body></html>

- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: AdditionalModulePathsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: AdditionalModulePathsWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: AdditionalModulePathsView

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerDirectoryListView`
- Search text: AdditionalModulePathsView | qSlicerDirectoryListView
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:169: qSlicerRelativePathMapper* relativePathMapper2 = new qSlicerRelativePathMapper(this->AdditionalModulePathsView, "directoryList", SIGNAL(directoryListChanged()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:192: QObject::connect(this->AdditionalModulePathsView, SIGNAL(directoryListChanged()), q, SLOT(onAdditionalModulePathsChanged()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:301: d->RemoveAdditionalModulePathButton->setEnabled(d->AdditionalModulePathsView->directoryList().count() > 0);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:316: d->AdditionalModulePathsView->addDirectory(path);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:325: d->AdditionalModulePathsView->removeSelectedDirectories();`
- Connected slots/functions: `onAdditionalModulePathsChanged`

## widget: groupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox | QGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: AddAdditionalModulePathButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Add | AddAdditionalModulePathButton | QPushButton
- Text: Add
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:195: QObject::connect(this->AddAdditionalModulePathButton, SIGNAL(clicked()), q, SLOT(onAddModulesAdditionalPathClicked()));`
- Connected slots/functions: `onAddModulesAdditionalPathClicked`

## widget: RemoveAdditionalModulePathButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Remove | RemoveAdditionalModulePathButton | QPushButton
- Text: Remove
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:196: QObject::connect(this->RemoveAdditionalModulePathButton, SIGNAL(clicked()), q, SLOT(onRemoveModulesAdditionalPathClicked()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:301: d->RemoveAdditionalModulePathButton->setEnabled(d->AdditionalModulePathsView->directoryList().count() > 0);`
- Connected slots/functions: `onRemoveModulesAdditionalPathClicked`

## widget: AdditionalModulePathMoreButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkExpandButton`
- Search text: AdditionalModulePathMoreButton | ctkExpandButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:80: this->AdditionalModulePathMoreButton->setChecked(false);`
- Connected slots/functions: `setVisible`
- Declared UI connections: `toggled(bool) -> groupBox.setVisible(bool)`
- Key UI properties: {"checked": "true"}

## widget: DisableModulesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Modules: | when checking/unchecking a module, its dependencies are checked/unchecked accordingly | DisableModulesLabel | QLabel
- Text: Modules:
- Tooltip: when checking/unchecking a module, its dependencies are checked/unchecked accordingly
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: ModuleListContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: ModuleListContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: DisableModulesListView

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerModulesListView`
- Search text: DisableModulesListView | qSlicerModulesListView
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:83: qSlicerModuleFactoryFilterModel* filterModel = this->DisableModulesListView->filterModel();`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:112: this->DisableModulesListView->setFactoryManager(factoryManager);`

## widget: FilterGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: FilterGroupBox | QGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: FilterToLoadPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCheckablePushButton`
- Search text: To load | Hide modules to load at startup | FilterToLoadPushButton | ctkCheckablePushButton
- Text: To load
- Tooltip: Hide modules to load at startup
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:84: QObject::connect(this->FilterToLoadPushButton, SIGNAL(toggled(bool)), filterModel, SLOT(setShowToLoad(bool)));`
- Connected slots/functions: `setShowToLoad`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: FilterToIgnorePushButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkCheckablePushButton`
- Search text: To ignore | Hide modules to ignore at startup | FilterToIgnorePushButton | ctkCheckablePushButton
- Text: To ignore
- Tooltip: Hide modules to ignore at startup
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:85: QObject::connect(this->FilterToIgnorePushButton, SIGNAL(toggled(bool)), filterModel, SLOT(setShowToIgnore(bool)));`
- Connected slots/functions: `setShowToIgnore`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: FilterLoadedPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Loaded | Hide loaded modules | FilterLoadedPushButton | QPushButton
- Text: Loaded
- Tooltip: Hide loaded modules
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:86: QObject::connect(this->FilterLoadedPushButton, SIGNAL(toggled(bool)), filterModel, SLOT(setShowLoaded(bool)));`
- Connected slots/functions: `setShowLoaded`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: FilterIgnoredPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Ignored | Hide ignored modules | FilterIgnoredPushButton | QPushButton
- Text: Ignored
- Tooltip: Hide ignored modules
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:87: QObject::connect(this->FilterIgnoredPushButton, SIGNAL(toggled(bool)), filterModel, SLOT(setShowIgnored(bool)));`
- Connected slots/functions: `setShowIgnored`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: FilterFailedPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Failed | Hide Failed to load modules | FilterFailedPushButton | QPushButton
- Text: Failed
- Tooltip: Hide Failed to load modules
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:88: QObject::connect(this->FilterFailedPushButton, SIGNAL(toggled(bool)), filterModel, SLOT(setShowFailed(bool)));`
- Connected slots/functions: `setShowFailed`
- Key UI properties: {"checkable": "true", "checked": "true"}

## widget: FilterTitleSearchBox

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSearchBox`
- Search text: FilterTitleSearchBox | ctkSearchBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:89: QObject::connect(this->FilterTitleSearchBox, SIGNAL(textChanged(QString)), filterModel, SLOT(setFilterFixedString(QString)));`
- Connected slots/functions: `setFilterFixedString`

## widget: FilterMoreButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkExpandButton`
- Search text: FilterMoreButton | ctkExpandButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:91: this->FilterMoreButton->setChecked(false); // hide filters by default`
- Connected slots/functions: `setVisible`
- Declared UI connections: `toggled(bool) -> FilterGroupBox.setVisible(bool)`
- Key UI properties: {"checked": "true"}

## widget: HomeModuleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default startup module: | HomeModuleLabel | QLabel
- Text: Default startup module:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: DefaultStartupContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: DefaultStartupContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: HomeModuleButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: HomeModuleButton | QPushButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:96: this->HomeModuleButton->setMenu(this->ModulesMenu);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:275: d->HomeModuleButton->setText(moduleAction->text());`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:276: d->HomeModuleButton->setIcon(moduleAction->icon());`

## widget: FavoritesModulesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: <html><head/><body><p>Favorite Modules:</p><p style="margin-left: 10px;"><span style=" font-size:small; font-style:italic;">Drag &amp; drop modules<br/>from </span><span style=" font-size:small;">Modules</span><span style=" font-size:small; font-style:italic;"> list</span></p></body></html> | Add to the list by dragging modules from the above "Modules" list. Note: modules with no icons will not appear in the toolbar. | FavoritesModulesLabel | QLabel
- Text: <html><head/><body><p>Favorite Modules:</p><p style="margin-left: 10px;"><span style=" font-size:small; font-style:italic;">Drag &amp; drop modules<br/>from </span><span style=" font-size:small;">Modules</span><span style=" font-size:small; font-style:italic;"> list</span></p></body></html>
- Tooltip: Add to the list by dragging modules from the above "Modules" list. Note: modules with no icons will not appear in the toolbar.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: FavoriteModulesContainerWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: FavoriteModulesContainerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: FavoritesModulesListView

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerModulesListView`
- Search text: FavoritesModulesListView | qSlicerModulesListView
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:101: this->FavoritesModulesListView->filterModel()->setHideAllWhenShowModulesIsEmpty(true);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:104: QObject::connect(this->FavoritesRemoveButton, SIGNAL(clicked()), this->FavoritesModulesListView, SLOT(hideSelectedModules()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:105: QObject::connect(this->FavoritesMoveLeftButton, SIGNAL(clicked()), this->FavoritesModulesListView, SLOT(moveLeftSelectedModules()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:106: QObject::connect(this->FavoritesMoveRightButton, SIGNAL(clicked()), this->FavoritesModulesListView, SLOT(moveRightSelectedModules()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:107: QObject::connect(this->FavoritesMoreButton, SIGNAL(toggled(bool)), this->FavoritesModulesListView, SLOT(scrollToSelectedModules()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:113: this->FavoritesModulesListView->setFactoryManager(factoryManager);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:118: this->FavoritesModulesListView->filterModel()->setDynamicSortFilter(false);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:128: this->FavoritesModulesListView->filterModel()->setShowModules(favorites);`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:158: q->registerProperty("Modules/FavoriteModules", this->FavoritesModulesListView->filterModel(), "showModules", SIGNAL(showModulesChanged(QStringList)));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:161: QObject::connect(this->FavoritesModulesListView->filterModel(), SIGNAL(showModulesChanged(QStringList)), q, SIGNAL(favoriteModulesChanged()));`
- Connected slots/functions: `hideSelectedModules`, `moveLeftSelectedModules`, `moveRightSelectedModules`, `scrollToSelectedModules`

## widget: FavoritesMoreGroupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: Add to the list by dragging modules from the above "Modules" list | FavoritesMoreGroupBox | QGroupBox
- Tooltip: Add to the list by dragging modules from the above "Modules" list
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`

## widget: FavoritesRemoveButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Remove | Remove selected module from favorites | FavoritesRemoveButton | QPushButton
- Text: Remove
- Tooltip: Remove selected module from favorites
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:104: QObject::connect(this->FavoritesRemoveButton, SIGNAL(clicked()), this->FavoritesModulesListView, SLOT(hideSelectedModules()));`
- Connected slots/functions: `hideSelectedModules`

## widget: FavoritesMoveLeftButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Move Left | Move to the left | FavoritesMoveLeftButton | QToolButton
- Text: Move Left
- Tooltip: Move to the left
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:102: this->FavoritesMoveLeftButton->setIcon(q->style()->standardIcon(QStyle::SP_ArrowLeft));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:105: QObject::connect(this->FavoritesMoveLeftButton, SIGNAL(clicked()), this->FavoritesModulesListView, SLOT(moveLeftSelectedModules()));`
- Connected slots/functions: `moveLeftSelectedModules`

## widget: FavoritesMoveRightButton

- Confidence: `linked_to_slot`
- Widget/action class: `QToolButton`
- Search text: Move Right | Move to the right | FavoritesMoveRightButton | QToolButton
- Text: Move Right
- Tooltip: Move to the right
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:103: this->FavoritesMoveRightButton->setIcon(q->style()->standardIcon(QStyle::SP_ArrowRight));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:106: QObject::connect(this->FavoritesMoveRightButton, SIGNAL(clicked()), this->FavoritesModulesListView, SLOT(moveRightSelectedModules()));`
- Connected slots/functions: `moveRightSelectedModules`

## widget: FavoritesMoreButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkExpandButton`
- Search text: FavoritesMoreButton | ctkExpandButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsModulesPanel.cxx`, `Base/QTGUI/qSlicerSettingsModulesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:107: QObject::connect(this->FavoritesMoreButton, SIGNAL(toggled(bool)), this->FavoritesModulesListView, SLOT(scrollToSelectedModules()));`
  - `Base/QTGUI/qSlicerSettingsModulesPanel.cxx:108: this->FavoritesMoreButton->setChecked(false);`
- Connected slots/functions: `scrollToSelectedModules`, `setVisible`
- Declared UI connections: `toggled(bool) -> FavoritesMoreGroupBox.setVisible(bool)`
- Key UI properties: {"checked": "true"}
