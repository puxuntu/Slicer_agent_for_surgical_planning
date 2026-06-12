# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerExtensionsButtonBox.ui

- Owner class: `qSlicerExtensionsButtonBox`
- UI file: `Base/QTGUI/Resources/UI/qSlicerExtensionsButtonBox.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerExtensionsButtonBox

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qSlicerExtensionsButtonBox | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:45: #include "ui_qSlicerExtensionsButtonBox.h"`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:123: class qSlicerExtensionsButtonBox`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:125: , public Ui_qSlicerExtensionsButtonBox`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:129: qSlicerExtensionsButtonBox(QListWidgetItem* widgetItem, QWidget* parent = nullptr)`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:610: this->ButtonBox = new qSlicerExtensionsButtonBox(label->widgetItem());`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:626: qSlicerExtensionsButtonBox* ButtonBox;`

## widget: InstallProgress

- Confidence: `linked_to_code`
- Widget/action class: `QProgressBar`
- Search text: InstallProgress | QProgressBar
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:134: this->InstallProgress->setVisible(false);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1101: widget->ButtonBox->InstallProgress->setRange(0, 0);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1102: widget->ButtonBox->InstallProgress->setValue(0);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1112: widget->ButtonBox->InstallProgress->setRange(0, static_cast<int>(total));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1113: widget->ButtonBox->InstallProgress->setValue(static_cast<int>(received));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1118: widget->ButtonBox->InstallProgress->setVisible(false);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1124: widget->ButtonBox->InstallProgress->setVisible(true);`

## widget: InstallButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Install | Install this extension (requires restart). | InstallButton | QPushButton
- Text: Install
- Tooltip: Install this extension (requires restart).
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:92: QSignalMapper InstallButtonMapper;`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:151: this->InstallButton->setVisible(!installed);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:152: this->InstallButton->setEnabled(compatible && available);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:232: QObject::connect(&this->InstallButtonMapper, &QSignalMapper::mappedString, q, &qSlicerExtensionsLocalWidget::installExtension);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:773: this->InstallButtonMapper.setMapping(widget->ButtonBox->InstallButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:774: QObject::connect(widget->ButtonBox->InstallButton, SIGNAL(clicked()), &this->InstallButtonMapper, SLOT(map()));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1125: widget->ButtonBox->InstallButton->setVisible(false);`
- Connected slots/functions: `installExtension`, `map`, `mappedString`

## widget: AddBookmarkButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Click this button to add bookmark this extension. Bookmarked extension will appear in all application versions for easy reinstallation. | AddBookmarkButton | QPushButton
- Tooltip: Click this button to add bookmark this extension. Bookmarked extension will appear in all application versions for easy reinstallation.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:93: QSignalMapper AddBookmarkButtonMapper;`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:174: this->AddBookmarkButton->setVisible(!bookmarked);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:233: QObject::connect(&this->AddBookmarkButtonMapper, &QSignalMapper::mappedString, q, &qSlicerExtensionsLocalWidget::addBookmark);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:768: this->AddBookmarkButtonMapper.setMapping(widget->ButtonBox->AddBookmarkButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:769: QObject::connect(widget->ButtonBox->AddBookmarkButton, SIGNAL(clicked()), &this->AddBookmarkButtonMapper, SLOT(map()));`
- Connected slots/functions: `addBookmark`, `map`, `mappedString`

## widget: RemoveBookmarkButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkPushButton`
- Search text: Click to remove the bookmark. | RemoveBookmarkButton | ctkPushButton
- Tooltip: Click to remove the bookmark.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:94: QSignalMapper RemoveBookmarkButtonMapper;`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:175: this->RemoveBookmarkButton->setVisible(bookmarked);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:234: QObject::connect(&this->RemoveBookmarkButtonMapper, &QSignalMapper::mappedString, q, &qSlicerExtensionsLocalWidget::removeBookmark);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:770: this->RemoveBookmarkButtonMapper.setMapping(widget->ButtonBox->RemoveBookmarkButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:771: QObject::connect(widget->ButtonBox->RemoveBookmarkButton, SIGNAL(clicked()), &this->RemoveBookmarkButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`, `mappedString`, `removeBookmark`

## widget: ScheduleForUninstallButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Uninstall | Tell the application to uninstall this extension when it will restart. | ScheduleForUninstallButton | QPushButton
- Text: Uninstall
- Tooltip: Tell the application to uninstall this extension when it will restart.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:181: this->ScheduleForUninstallButton->setVisible(!scheduledForUninstall && installed);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:786: this->ScheduleUninstallButtonMapper.setMapping(widget->ButtonBox->ScheduleForUninstallButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:787: QObject::connect(widget->ButtonBox->ScheduleForUninstallButton, SIGNAL(clicked()), &this->ScheduleUninstallButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`

## widget: CancelScheduledForUninstallButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Cancel Uninstall | Tell the application to keep this extension installed. | CancelScheduledForUninstallButton | QPushButton
- Text: Cancel Uninstall
- Tooltip: Tell the application to keep this extension installed.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:182: this->CancelScheduledForUninstallButton->setVisible(scheduledForUninstall);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:788: this->CancelScheduledUninstallButtonMapper.setMapping(widget->ButtonBox->CancelScheduledForUninstallButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:789: QObject::connect(widget->ButtonBox->CancelScheduledForUninstallButton, SIGNAL(clicked()), &this->CancelScheduledUninstallButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`

## widget: UpdateOptionsWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: UpdateOptionsWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:184: this->UpdateOptionsWidget->setVisible(updateAvailable);`

## widget: UpdateProgress

- Confidence: `linked_to_code`
- Widget/action class: `QProgressBar`
- Search text: UpdateProgress | QProgressBar
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:135: this->UpdateProgress->setVisible(false);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1057: widget->ButtonBox->UpdateProgress->setRange(0, 0);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1058: widget->ButtonBox->UpdateProgress->setValue(0);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1068: widget->ButtonBox->UpdateProgress->setRange(0, static_cast<int>(total));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1069: widget->ButtonBox->UpdateProgress->setValue(static_cast<int>(received));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1075: widget->ButtonBox->UpdateProgress->setVisible(false);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:1080: widget->ButtonBox->UpdateProgress->setVisible(true);`

## widget: ScheduleForUpdateButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Update | Tell the application to update this extension on restart. | ScheduleForUpdateButton | QPushButton
- Text: Update
- Tooltip: Tell the application to update this extension on restart.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:186: this->ScheduleForUpdateButton->setVisible(!scheduledForUpdate && !scheduledForUninstall);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:776: this->ScheduleUpdateButtonMapper.setMapping(widget->ButtonBox->ScheduleForUpdateButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:777: QObject::connect(widget->ButtonBox->ScheduleForUpdateButton, SIGNAL(clicked()), &this->ScheduleUpdateButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`

## widget: CancelScheduledForUpdateButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Cancel Update | Tell the application to keep the currently installed version of this extension. | CancelScheduledForUpdateButton | QPushButton
- Text: Cancel Update
- Tooltip: Tell the application to keep the currently installed version of this extension.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:187: this->CancelScheduledForUpdateButton->setVisible(scheduledForUpdate);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:778: this->CancelScheduledUpdateButtonMapper.setMapping(widget->ButtonBox->CancelScheduledForUpdateButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:779: QObject::connect(widget->ButtonBox->CancelScheduledForUpdateButton, SIGNAL(clicked()), &this->CancelScheduledUpdateButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`

## widget: EnableButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Enable | Tell the application to load this extension by adding all associated module paths to the application settings. | EnableButton | QPushButton
- Text: Enable
- Tooltip: Tell the application to load this extension by adding all associated module paths to the application settings.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:95: QSignalMapper EnableButtonMapper;`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:177: this->EnableButton->setVisible(!enabled && installed && !scheduledForUninstall);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:178: this->EnableButton->setEnabled(compatible);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:235: QObject::connect(&this->EnableButtonMapper, &QSignalMapper::mappedString, q, &qSlicerExtensionsLocalWidget::setExtensionEnabled);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:781: this->EnableButtonMapper.setMapping(widget->ButtonBox->EnableButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:782: QObject::connect(widget->ButtonBox->EnableButton, SIGNAL(clicked()), &this->EnableButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`, `mappedString`, `setExtensionEnabled`

## widget: DisableButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Disable | Tell the application to skip loading of this extension by removing all associated module paths from the application settings. | DisableButton | QPushButton
- Text: Disable
- Tooltip: Tell the application to skip loading of this extension by removing all associated module paths from the application settings.
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:96: QSignalMapper DisableButtonMapper;`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:179: this->DisableButton->setVisible(enabled && loaded && installed && !scheduledForUninstall && !scheduledForUpdate);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:236: QObject::connect(&this->DisableButtonMapper, &QSignalMapper::mappedString, q, &qSlicerExtensionsLocalWidget::setExtensionDisabled);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:783: this->DisableButtonMapper.setMapping(widget->ButtonBox->DisableButton, extensionName);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:784: QObject::connect(widget->ButtonBox->DisableButton, SIGNAL(clicked()), &this->DisableButtonMapper, SLOT(map()));`
- Connected slots/functions: `map`, `mappedString`, `setExtensionDisabled`

## widget: StatusLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: StatusLabel | QLabel
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:156: this->StatusLabel->setVisible(true);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:157: this->StatusLabel->setText(qSlicerExtensionsLocalWidget::tr("Install pending restart"));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:161: this->StatusLabel->setVisible(true);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:162: this->StatusLabel->setText(qSlicerExtensionsLocalWidget::tr("Update pending restart"));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:166: this->StatusLabel->setVisible(true);`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:167: this->StatusLabel->setText(qSlicerExtensionsLocalWidget::tr("Uninstall pending restart"));`
  - `Base/QTGUI/qSlicerExtensionsLocalWidget.cxx:171: this->StatusLabel->setVisible(false);`
