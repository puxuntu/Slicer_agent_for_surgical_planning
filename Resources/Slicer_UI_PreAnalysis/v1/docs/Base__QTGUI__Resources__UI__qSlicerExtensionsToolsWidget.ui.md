# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerExtensionsToolsWidget.ui

- Owner class: `qSlicerExtensionsToolsWidget`
- UI file: `Base/QTGUI/Resources/UI/qSlicerExtensionsToolsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerExtensionsToolsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: qSlicerExtensionsToolsWidget | QWidget

## widget: CheckForUpdatesButton

- Confidence: `ui_only`
- Widget/action class: `QToolButton`
- Search text: Check for updates | Query the Extensions Server if there are updates for any of the installed extensions | CheckForUpdatesButton | QToolButton
- Text: Check for updates
- Tooltip: Query the Extensions Server if there are updates for any of the installed extensions
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonTextBesideIcon"}

## widget: InstallUpdatesButton

- Confidence: `ui_only`
- Widget/action class: `QToolButton`
- Search text: Update all | Updates all extensions with the latest version available on the Extensions Server | InstallUpdatesButton | QToolButton
- Text: Update all
- Tooltip: Updates all extensions with the latest version available on the Extensions Server
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonTextBesideIcon"}

## widget: InstallBookmarkedButton

- Confidence: `ui_only`
- Widget/action class: `QToolButton`
- Search text: Install bookmarked | Install all the bookmarked extensions | InstallBookmarkedButton | QToolButton
- Text: Install bookmarked
- Tooltip: Install all the bookmarked extensions
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonTextBesideIcon"}

## widget: InstallFromFileButton

- Confidence: `ui_only`
- Widget/action class: `QToolButton`
- Search text: Install from file... | Install extensions from one or more extension package files | InstallFromFileButton | QToolButton
- Text: Install from file...
- Tooltip: Install extensions from one or more extension package files
- Key UI properties: {"toolButtonStyle": "Qt::ToolButtonTextBesideIcon"}

## widget: ConfigureButton

- Confidence: `ui_only`
- Widget/action class: `QToolButton`
- Search text: ConfigureButton | QToolButton
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## widget: SearchBox

- Confidence: `ui_only`
- Widget/action class: `ctkSearchBox`
- Search text: SearchBox | ctkSearchBox

## action: AutoUpdateCheckAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Automatically check for updates | Periodically check for updated extensions. | AutoUpdateCheckAction
- Text: Automatically check for updates
- Tooltip: Periodically check for updated extensions.
- Key UI properties: {"checkable": "true"}

## action: AutoUpdateInstallAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Automatically install updates | Automatically install updated extensions | AutoUpdateInstallAction
- Text: Automatically install updates
- Tooltip: Automatically install updated extensions
- Key UI properties: {"checkable": "true"}

## action: CheckForUpdatesAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Check for updates | Query the Extensions Server if there are updates for any of the installed extensions | CheckForUpdatesAction
- Text: Check for updates
- Tooltip: Query the Extensions Server if there are updates for any of the installed extensions

## action: EditBookmarksAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Edit bookmarks... | Edit list of bookmarks in a text field | EditBookmarksAction
- Text: Edit bookmarks...
- Tooltip: Edit list of bookmarks in a text field

## action: OpenExtensionsCatalogWebsiteAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Open Extensions Catalog website... | Open Extensions Catalog website in the default web browser. Useful for downloading extension packages for offline use. | OpenExtensionsCatalogWebsiteAction
- Text: Open Extensions Catalog website...
- Tooltip: Open Extensions Catalog website in the default web browser. Useful for downloading extension packages for offline use.

## action: AutoInstallDependenciesAction

- Confidence: `ui_only`
- Widget/action class: `action`
- Search text: Automatically install dependencies | Automatically install required additional extensions when installing an extension | AutoInstallDependenciesAction
- Text: Automatically install dependencies
- Tooltip: Automatically install required additional extensions when installing an extension
- Key UI properties: {"checkable": "true"}
