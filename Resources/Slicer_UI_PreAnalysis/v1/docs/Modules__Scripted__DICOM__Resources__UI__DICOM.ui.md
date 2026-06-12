# Slicer UI Analysis: Modules/Scripted/DICOM/Resources/UI/DICOM.ui

- Owner class: `UtilTest`
- UI file: `Modules/Scripted/DICOM/Resources/UI/DICOM.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: UtilTest

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: UtilTest | QWidget
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: importButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkMenuButton`
- Search text:  Import DICOM files | Import files into DICOM database | importButton | ctkMenuButton
- Text:  Import DICOM files
- Tooltip: Import files into DICOM database
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:877: self.ui.importButton.connect("clicked()", self.importFolder)`
  - `Modules/Scripted/DICOM/DICOM.py:884: importButtonMenu = qt.QMenu(_("Import options"), self.ui.importButton)`
  - `Modules/Scripted/DICOM/DICOM.py:885: importButtonMenu.toolTipsVisible = True`
  - `Modules/Scripted/DICOM/DICOM.py:886: self.ui.importButton.setMenu(importButtonMenu)`
  - `Modules/Scripted/DICOM/DICOM.py:887: importButtonMenu.connect("aboutToShow()", self.aboutToShowImportOptionsMenu)`
  - `Modules/Scripted/DICOM/DICOM.py:889: self.copyOnImportAction = qt.QAction(_("Copy imported files to DICOM database"), importButtonMenu)`
  - `Modules/Scripted/DICOM/DICOM.py:893: importButtonMenu.addAction(self.copyOnImportAction)`

## widget: showBrowserButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Show DICOM database | Show DICOM database | showBrowserButton | QPushButton
- Text: Show DICOM database
- Tooltip: Show DICOM database
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:133: # Update the showBrowserButton state and button visibility if DICOMWidget exists`
  - `Modules/Scripted/DICOM/DICOM.py:136: ui.showBrowserButton.checked = False`
  - `Modules/Scripted/DICOM/DICOM.py:137: ui.showBrowserButton.text = _("Show DICOM Database")`
  - `Modules/Scripted/DICOM/DICOM.py:873: self.ui.showBrowserButton.checked = viewArrangement == slicer.vtkMRMLLayoutNode.SlicerLayoutDicomBrowserView`
  - `Modules/Scripted/DICOM/DICOM.py:876: self.ui.showBrowserButton.connect("clicked()", self.toggleBrowserWidget)`
  - `Modules/Scripted/DICOM/DICOM.py:897: self.ui.showVisualBrowserButton.visible = self.ui.showBrowserButton.checked`
  - `Modules/Scripted/DICOM/DICOM.py:902: if self.ui.showBrowserButton.checked:`
  - `Modules/Scripted/DICOM/DICOM.py:903: self.ui.showBrowserButton.text = _("Hide DICOM database")`
  - `Modules/Scripted/DICOM/DICOM.py:905: self.ui.showBrowserButton.text = _("Show DICOM database")`
  - `Modules/Scripted/DICOM/DICOM.py:909: self.ui.dockToRightPushButton.visible = self.ui.showBrowserButton.checked`
  - `Modules/Scripted/DICOM/DICOM.py:1047: self.ui.showBrowserButton.checked = viewArrangement == slicer.vtkMRMLLayoutNode.SlicerLayoutDicomBrowserView`
  - `Modules/Scripted/DICOM/DICOM.py:1048: self.ui.showBrowserButton.text = (_("Hide DICOM database") if self.ui.showBrowserButton.checked`
- API footprints: `GetLayoutNode`, `GetViewArrangement`
- Key UI properties: {"checkable": "true"}

## widget: showVisualBrowserButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Visual browser | If enabled, the DICOM browser widget will be substituted with the visual browser. | showVisualBrowserButton | QPushButton
- Text: Visual browser
- Tooltip: If enabled, the DICOM browser widget will be substituted with the visual browser.
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:138: ui.showVisualBrowserButton.visible = False`
  - `Modules/Scripted/DICOM/DICOM.py:897: self.ui.showVisualBrowserButton.visible = self.ui.showBrowserButton.checked`
  - `Modules/Scripted/DICOM/DICOM.py:898: self.ui.showVisualBrowserButton.checked = settingsValue("DICOM/UseVisualDICOMBrowser", False, converter=toBool)`
  - `Modules/Scripted/DICOM/DICOM.py:899: self.ui.showVisualBrowserButton.connect("toggled(bool)", self.onShowVisualDICOMBrowser)`
  - `Modules/Scripted/DICOM/DICOM.py:1053: self.ui.showVisualBrowserButton.visible = browserIsShown`
  - `Modules/Scripted/DICOM/DICOM.py:1054: self.ui.showVisualBrowserButton.checked = settingsValue("DICOM/UseVisualDICOMBrowser", False, converter=toBool)`
  - `Modules/Scripted/DICOM/DICOM.py:1085: self.ui.showVisualBrowserButton.visible = browserIsShown`
  - `Modules/Scripted/DICOM/DICOM.py:1086: self.ui.showVisualBrowserButton.checked = settingsValue("DICOM/UseVisualDICOMBrowser", False, converter=toBool)`
  - `Modules/Scripted/DICOM/DICOM.py:1114: self.ui.showVisualBrowserButton.visible = False`
- Key UI properties: {"checkable": "true"}

## widget: dockToRightPushButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Side panel | Show the dicom database in vertical mode allowing to use the Slicer views. | dockToRightPushButton | QPushButton
- Text: Side panel
- Tooltip: Show the dicom database in vertical mode allowing to use the Slicer views.
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:139: ui.dockToRightPushButton.visible = False`
  - `Modules/Scripted/DICOM/DICOM.py:140: ui.dockToRightPushButton.checked = False`
  - `Modules/Scripted/DICOM/DICOM.py:880: self.ui.dockToRightPushButton.connect("clicked()", self.onDockToRight)`
  - `Modules/Scripted/DICOM/DICOM.py:909: self.ui.dockToRightPushButton.visible = self.ui.showBrowserButton.checked`
  - `Modules/Scripted/DICOM/DICOM.py:910: self.ui.dockToRightPushButton.text = _("Side panel")`
  - `Modules/Scripted/DICOM/DICOM.py:1055: self.ui.dockToRightPushButton.visible = browserIsShown`
  - `Modules/Scripted/DICOM/DICOM.py:1087: self.ui.dockToRightPushButton.visible = browserIsShown`
  - `Modules/Scripted/DICOM/DICOM.py:1115: self.ui.dockToRightPushButton.visible = False`
  - `Modules/Scripted/DICOM/DICOM.py:1209: self.ui.dockToRightPushButton.checked = True`
  - `Modules/Scripted/DICOM/DICOM.py:1248: self.ui.dockToRightPushButton.checked = False`
- Key UI properties: {"checkable": "true"}

## widget: loadedDataLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Loaded data | loadedDataLabel | QLabel
- Text: Loaded data
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: subjectHierarchyTree

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: subjectHierarchyTree | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:912: # Connect subjectHierarchyTree`
  - `Modules/Scripted/DICOM/DICOM.py:914: self.ui.subjectHierarchyTree.setMRMLScene(slicer.mrmlScene)`
  - `Modules/Scripted/DICOM/DICOM.py:915: self.ui.subjectHierarchyTree.currentItemChanged.connect(self.onCurrentItemChanged)`
  - `Modules/Scripted/DICOM/DICOM.py:916: self.ui.subjectHierarchyTree.currentItemModified.connect(self.onCurrentItemModified)`
  - `Modules/Scripted/DICOM/DICOM.py:918: self.ui.subjectHierarchyTree.setColumnHidden(self.ui.subjectHierarchyTree.model().idColumn, True)`
- Connected slots/functions: `onCurrentItemChanged`, `onCurrentItemModified`

## widget: networkingFrame

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: DICOM networking | networkingFrame | ctkCollapsibleButton
- Text: DICOM networking
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:924: self.ui.networkingFrame.collapsed = True`
  - `Modules/Scripted/DICOM/DICOM.py:935: self.ui.networkingFrame.layout().addWidget(self.toggleServer)`
  - `Modules/Scripted/DICOM/DICOM.py:939: self.ui.networkingFrame.layout().addWidget(self.verboseServer)`
- API footprints: `QCheckBox`, `QPushButton`

## widget: queryServerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Pull data from remote server: | queryServerLabel | QLabel
- Text: Pull data from remote server:
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: queryServerButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Query and retrieve | Query and retrieve DICOM data sets from remote server | queryServerButton | QPushButton
- Text: Query and retrieve
- Tooltip: Query and retrieve DICOM data sets from remote server
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:925: self.ui.queryServerButton.connect("clicked()", self.browserWidget.dicomBrowser, "openQueryDialog()")`

## widget: storageListenerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Storage listener: | storageListenerLabel | QLabel
- Text: Storage listener:
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: toggleListener

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Enable DICOM listening server to receive images (C-Store SCP) | toggleListener | QCheckBox
- Tooltip: Enable DICOM listening server to receive images (C-Store SCP)
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:927: self.ui.toggleListener.connect("toggled(bool)", self.onToggleListener)`
  - `Modules/Scripted/DICOM/DICOM.py:1280: wasBlocked = self.ui.toggleListener.blockSignals(True)`
  - `Modules/Scripted/DICOM/DICOM.py:1281: self.ui.toggleListener.checked = False`
  - `Modules/Scripted/DICOM/DICOM.py:1282: self.ui.toggleListener.blockSignals(wasBlocked)`
  - `Modules/Scripted/DICOM/DICOM.py:1296: self.ui.toggleListener.checked = True`

## widget: listenerStateLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: listenerStateLabel | QLabel
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:1279: self.ui.listenerStateLabel.text = _("not started")`
  - `Modules/Scripted/DICOM/DICOM.py:1286: self.ui.listenerStateLabel.text = _("starting")`
  - `Modules/Scripted/DICOM/DICOM.py:1293: self.ui.listenerStateLabel.text = _("running at port %s") % port`
  - `Modules/Scripted/DICOM/DICOM.py:1295: self.ui.listenerStateLabel.text = _("running at port %s with TLS") % port`

## widget: runListenerAtStartLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Start storage listener on startup: | runListenerAtStartLabel | QLabel
- Text: Start storage listener on startup:
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: runListenerAtStart

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Automatically start listener on application startup | runListenerAtStart | QCheckBox
- Tooltip: Automatically start listener on application startup
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:929: self.ui.runListenerAtStart.checked = settingsValue("DICOM/RunListenerAtStart", False, converter=toBool)`
  - `Modules/Scripted/DICOM/DICOM.py:930: self.ui.runListenerAtStart.connect("toggled(bool)", self.onRunListenerAtStart)`

## widget: browserSettingsFrame

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: DICOM database settings | browserSettingsFrame | ctkCollapsibleButton
- Text: DICOM database settings
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:950: self.ui.browserSettingsFrame.collapsed = True`

## widget: databaseDirectoryLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Database location: | databaseDirectoryLabel | QLabel
- Text: Database location:
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: directoryButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkDirectoryButton`
- Search text: directoryButton | ctkDirectoryButton
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:567: directoryButton = ctk.ctkDirectoryButton()`
  - `Modules/Scripted/DICOM/DICOM.py:568: genericGroupBoxFormLayout.addRow(_("Database location:"), directoryButton)`
  - `Modules/Scripted/DICOM/DICOM.py:569: parent.registerProperty(slicer.dicomDatabaseDirectorySettingsKey, directoryButton,`
  - `Modules/Scripted/DICOM/DICOM.py:954: self.ui.directoryButton.directoryChanged.connect(self.updateDatabaseDirectoryFromWidget)`
  - `Modules/Scripted/DICOM/DICOM.py:955: self.ui.directoryButton.sizePolicy = qt.QSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Fixed)`
  - `Modules/Scripted/DICOM/DICOM.py:1363: wasBlocked = self.ui.directoryButton.blockSignals(True)`
  - `Modules/Scripted/DICOM/DICOM.py:1364: self.ui.directoryButton.directory = databaseDirectory`
  - `Modules/Scripted/DICOM/DICOM.py:1365: self.ui.directoryButton.blockSignals(wasBlocked)`
  - `Modules/Scripted/DICOM/DICOM.py:1373: wasBlocked = self.ui.directoryButton.blockSignals(True)`
  - `Modules/Scripted/DICOM/DICOM.py:1374: self.ui.directoryButton.directory = databaseDirectory`
  - `Modules/Scripted/DICOM/DICOM.py:1375: self.ui.directoryButton.blockSignals(wasBlocked)`
- Connected slots/functions: `updateDatabaseDirectoryFromWidget`
- API footprints: `QFormLayout`, `QSizePolicy`, `SIGNAL`

## widget: browserAutoHideLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Auto-hide browser window: | browserAutoHideLabel | QLabel
- Text: Auto-hide browser window:
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: databaseMaintenanceLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Maintenance: | databaseMaintenanceLabel | QLabel
- Text: Maintenance:
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`

## widget: browserAutoHideCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Hide DICOM database browser after data loaded | browserAutoHideCheckBox | QCheckBox
- Tooltip: Hide DICOM database browser after data loaded
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:959: self.ui.browserAutoHideCheckBox.checked = not settingsValue("DICOM/BrowserPersistent", False, converter=toBool)`
  - `Modules/Scripted/DICOM/DICOM.py:960: self.ui.browserAutoHideCheckBox.stateChanged.connect(self.onBrowserAutoHideStateChanged)`
  - `Modules/Scripted/DICOM/DICOM.py:961: self.browserWidget.setBrowserPersistence(not self.ui.browserAutoHideCheckBox.checked)`
- Connected slots/functions: `onBrowserAutoHideStateChanged`

## widget: repairDatabaseButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Remove unavailable data sets | Remove all items from the DICOM database if referenced DICOM file is not found on disk. | repairDatabaseButton | QPushButton
- Text: Remove unavailable data sets
- Tooltip: Remove all items from the DICOM database if referenced DICOM file is not found on disk.
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:963: self.ui.repairDatabaseButton.connect("clicked()", self.onRepairDatabase)`

## widget: clearDatabaseButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Remove all data sets | Removes all data from the database and all files that were copied into the database during import. | clearDatabaseButton | QPushButton
- Text: Remove all data sets
- Tooltip: Removes all data from the database and all files that were copied into the database during import.
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:964: self.ui.clearDatabaseButton.connect("clicked()", self.onClearDatabase)`

## widget: refreshBrowserButton

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Refresh browser | Refresh the visual DICOM browser to show the current state of the database. | refreshBrowserButton | QPushButton
- Text: Refresh browser
- Tooltip: Refresh the visual DICOM browser to show the current state of the database.
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:965: self.ui.refreshBrowserButton.connect("clicked()", self.onRefreshBrowserButton)`

## widget: dicomPluginsFrame

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: DICOM plugins | dicomPluginsFrame | ctkCollapsibleButton
- Text: DICOM plugins
- Implementation candidates: `Modules/Scripted/DICOM/DICOM.py`
- Matched implementation lines:
  - `Modules/Scripted/DICOM/DICOM.py:987: self.ui.dicomPluginsFrame.collapsed = True`
  - `Modules/Scripted/DICOM/DICOM.py:988: self.pluginSelector = DICOMLib.DICOMPluginSelector(self.ui.dicomPluginsFrame)`
  - `Modules/Scripted/DICOM/DICOM.py:989: self.ui.dicomPluginsFrame.layout().addWidget(self.pluginSelector)`
- API footprints: `DICOMPluginSelector`
