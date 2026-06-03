# Slicer UI Analysis: Modules/Scripted/DICOM/Resources/UI/DICOM.ui

- Owner class: `UtilTest`
- UI file: `Modules/Scripted/DICOM/Resources/UI/DICOM.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: UtilTest

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: UtilTest | QWidget

## widget: importButton

- Confidence: `ui_only`
- Widget/action class: `ctkMenuButton`
- Search text:  Import DICOM files | Import files into DICOM database | importButton | ctkMenuButton
- Text:  Import DICOM files
- Tooltip: Import files into DICOM database

## widget: showBrowserButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Show DICOM database | Show DICOM database | showBrowserButton | QPushButton
- Text: Show DICOM database
- Tooltip: Show DICOM database
- Key UI properties: {"checkable": "true"}

## widget: showVisualBrowserButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Visual browser | If enabled, the DICOM browser widget will be substituted with the visual browser. | showVisualBrowserButton | QPushButton
- Text: Visual browser
- Tooltip: If enabled, the DICOM browser widget will be substituted with the visual browser.
- Key UI properties: {"checkable": "true"}

## widget: dockToRightPushButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Side panel | Show the dicom database in vertical mode allowing to use the Slicer views. | dockToRightPushButton | QPushButton
- Text: Side panel
- Tooltip: Show the dicom database in vertical mode allowing to use the Slicer views.
- Key UI properties: {"checkable": "true"}

## widget: loadedDataLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Loaded data | loadedDataLabel | QLabel
- Text: Loaded data

## widget: subjectHierarchyTree

- Confidence: `ui_only`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: subjectHierarchyTree | qMRMLSubjectHierarchyTreeView

## widget: networkingFrame

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: DICOM networking | networkingFrame | ctkCollapsibleButton
- Text: DICOM networking

## widget: queryServerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Pull data from remote server: | queryServerLabel | QLabel
- Text: Pull data from remote server:

## widget: queryServerButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Query and retrieve | Query and retrieve DICOM data sets from remote server | queryServerButton | QPushButton
- Text: Query and retrieve
- Tooltip: Query and retrieve DICOM data sets from remote server

## widget: storageListenerLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Storage listener: | storageListenerLabel | QLabel
- Text: Storage listener:

## widget: toggleListener

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: Enable DICOM listening server to receive images (C-Store SCP) | toggleListener | QCheckBox
- Tooltip: Enable DICOM listening server to receive images (C-Store SCP)

## widget: listenerStateLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: listenerStateLabel | QLabel

## widget: runListenerAtStartLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Start storage listener on startup: | runListenerAtStartLabel | QLabel
- Text: Start storage listener on startup:

## widget: runListenerAtStart

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: Automatically start listener on application startup | runListenerAtStart | QCheckBox
- Tooltip: Automatically start listener on application startup

## widget: browserSettingsFrame

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: DICOM database settings | browserSettingsFrame | ctkCollapsibleButton
- Text: DICOM database settings

## widget: databaseDirectoryLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Database location: | databaseDirectoryLabel | QLabel
- Text: Database location:

## widget: directoryButton

- Confidence: `ui_only`
- Widget/action class: `ctkDirectoryButton`
- Search text: directoryButton | ctkDirectoryButton

## widget: browserAutoHideLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Auto-hide browser window: | browserAutoHideLabel | QLabel
- Text: Auto-hide browser window:

## widget: databaseMaintenanceLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Maintenance: | databaseMaintenanceLabel | QLabel
- Text: Maintenance:

## widget: browserAutoHideCheckBox

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: Hide DICOM database browser after data loaded | browserAutoHideCheckBox | QCheckBox
- Tooltip: Hide DICOM database browser after data loaded

## widget: repairDatabaseButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Remove unavailable data sets | Remove all items from the DICOM database if referenced DICOM file is not found on disk. | repairDatabaseButton | QPushButton
- Text: Remove unavailable data sets
- Tooltip: Remove all items from the DICOM database if referenced DICOM file is not found on disk.

## widget: clearDatabaseButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Remove all data sets | Removes all data from the database and all files that were copied into the database during import. | clearDatabaseButton | QPushButton
- Text: Remove all data sets
- Tooltip: Removes all data from the database and all files that were copied into the database during import.

## widget: refreshBrowserButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Refresh browser | Refresh the visual DICOM browser to show the current state of the database. | refreshBrowserButton | QPushButton
- Text: Refresh browser
- Tooltip: Refresh the visual DICOM browser to show the current state of the database.

## widget: dicomPluginsFrame

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: DICOM plugins | dicomPluginsFrame | ctkCollapsibleButton
- Text: DICOM plugins
