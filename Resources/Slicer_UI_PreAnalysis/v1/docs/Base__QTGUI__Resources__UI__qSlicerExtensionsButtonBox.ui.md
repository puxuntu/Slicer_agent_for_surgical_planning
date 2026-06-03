# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerExtensionsButtonBox.ui

- Owner class: `qSlicerExtensionsButtonBox`
- UI file: `Base/QTGUI/Resources/UI/qSlicerExtensionsButtonBox.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerExtensionsButtonBox

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: qSlicerExtensionsButtonBox | QWidget

## widget: InstallProgress

- Confidence: `ui_only`
- Widget/action class: `QProgressBar`
- Search text: InstallProgress | QProgressBar

## widget: InstallButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Install | Install this extension (requires restart). | InstallButton | QPushButton
- Text: Install
- Tooltip: Install this extension (requires restart).

## widget: AddBookmarkButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Click this button to add bookmark this extension. Bookmarked extension will appear in all application versions for easy reinstallation. | AddBookmarkButton | QPushButton
- Tooltip: Click this button to add bookmark this extension. Bookmarked extension will appear in all application versions for easy reinstallation.

## widget: RemoveBookmarkButton

- Confidence: `ui_only`
- Widget/action class: `ctkPushButton`
- Search text: Click to remove the bookmark. | RemoveBookmarkButton | ctkPushButton
- Tooltip: Click to remove the bookmark.

## widget: ScheduleForUninstallButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Uninstall | Tell the application to uninstall this extension when it will restart. | ScheduleForUninstallButton | QPushButton
- Text: Uninstall
- Tooltip: Tell the application to uninstall this extension when it will restart.

## widget: CancelScheduledForUninstallButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Cancel Uninstall | Tell the application to keep this extension installed. | CancelScheduledForUninstallButton | QPushButton
- Text: Cancel Uninstall
- Tooltip: Tell the application to keep this extension installed.

## widget: UpdateOptionsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: UpdateOptionsWidget | QWidget

## widget: UpdateProgress

- Confidence: `ui_only`
- Widget/action class: `QProgressBar`
- Search text: UpdateProgress | QProgressBar

## widget: ScheduleForUpdateButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Update | Tell the application to update this extension on restart. | ScheduleForUpdateButton | QPushButton
- Text: Update
- Tooltip: Tell the application to update this extension on restart.

## widget: CancelScheduledForUpdateButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Cancel Update | Tell the application to keep the currently installed version of this extension. | CancelScheduledForUpdateButton | QPushButton
- Text: Cancel Update
- Tooltip: Tell the application to keep the currently installed version of this extension.

## widget: EnableButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Enable | Tell the application to load this extension by adding all associated module paths to the application settings. | EnableButton | QPushButton
- Text: Enable
- Tooltip: Tell the application to load this extension by adding all associated module paths to the application settings.

## widget: DisableButton

- Confidence: `ui_only`
- Widget/action class: `QPushButton`
- Search text: Disable | Tell the application to skip loading of this extension by removing all associated module paths from the application settings. | DisableButton | QPushButton
- Text: Disable
- Tooltip: Tell the application to skip loading of this extension by removing all associated module paths from the application settings.

## widget: StatusLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: StatusLabel | QLabel
