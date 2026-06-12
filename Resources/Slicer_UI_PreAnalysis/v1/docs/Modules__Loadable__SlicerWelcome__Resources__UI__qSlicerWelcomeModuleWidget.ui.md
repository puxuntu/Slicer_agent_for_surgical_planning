# Slicer UI Analysis: Modules/Loadable/SlicerWelcome/Resources/UI/qSlicerWelcomeModuleWidget.ui

- Owner class: `qSlicerWelcomeModuleWidget`
- UI file: `Modules/Loadable/SlicerWelcome/Resources/UI/qSlicerWelcomeModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerWelcomeModuleWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerWelcomeModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:34: #include "qSlicerWelcomeModuleWidget.h"`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:35: #include "ui_qSlicerWelcomeModuleWidget.h"`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:60: class qSlicerWelcomeModuleWidgetPrivate : public Ui_qSlicerWelcomeModuleWidget`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:62: Q_DECLARE_PUBLIC(qSlicerWelcomeModuleWidget);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:65: qSlicerWelcomeModuleWidget* const q_ptr;`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:68: qSlicerWelcomeModuleWidgetPrivate(qSlicerWelcomeModuleWidget& object);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:87: // qSlicerWelcomeModuleWidgetPrivate methods`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:90: qSlicerWelcomeModuleWidgetPrivate::qSlicerWelcomeModuleWidgetPrivate(qSlicerWelcomeModuleWidget& object)`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:96: void qSlicerWelcomeModuleWidgetPrivate::setupUi(qSlicerWidget* widget)`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:98: Q_Q(qSlicerWelcomeModuleWidget);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:100: this->Ui_qSlicerWelcomeModuleWidget::setupUi(widget);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:108: this->CheckingForUpdatesText = qSlicerWelcomeModuleWidget::tr("Checking for updates...");`
- Connected slots/functions: `checkStateChanged`, `onAutoUpdateCheckStateChanged`

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: <html><head/><body><p align="center"><span style=" font-size:22pt; color:#afb7d5;">Welcome</span></p></body></html> | label | QLabel
- Text: <html><head/><body><p align="center"><span style=" font-size:22pt; color:#afb7d5;">Welcome</span></p></body></html>
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: ButtonsFrame

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: ButtonsFrame | QFrame
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: OpenExtensionsManagerButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text:  Install Extensions | Raise the "Extensions Manager" wizard that allows to find, download and install Slicer extensions.<br><br>An extension is a delivery package bundling together one or more Slicer modules.<br><br>After installing an extension, the associated modules will be available in the module selector. | OpenExtensionsManagerButton | QPushButton
- Text:  Install Extensions
- Tooltip: Raise the "Extensions Manager" wizard that allows to find, download and install Slicer extensions.<br><br>An extension is a delivery package bundling together one or more Slicer modules.<br><br>After installing an extension, the associated modules will be available in the module selector.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:232: QObject::connect(d->OpenExtensionsManagerButton, SIGNAL(clicked()), qSlicerApplication::application(), SLOT(openExtensionsManagerDialog()));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:249: d->OpenExtensionsManagerButton->hide();`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:252: d->OpenExtensionsManagerButton->hide();`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:347: if (d->OpenExtensionsManagerButton->property(extensionUpdateAvailablePropertyName).toBool() != isAvailable)`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:350: d->OpenExtensionsManagerButton->setProperty(extensionUpdateAvailablePropertyName, isAvailable);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:353: d->OpenExtensionsManagerButton->setIcon(QIcon(":/Icons/ExtensionNotificationIcon.png"));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:357: d->OpenExtensionsManagerButton->setIcon(QIcon(":/Icons/ExtensionDefaultIcon.png"));`
- Connected slots/functions: `openExtensionsManagerDialog`

## widget: LoadSampleDataButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Download Sample Data | LoadSampleDataButton | QPushButton
- Text: Download Sample Data
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:216: connect(d->LoadSampleDataButton, SIGNAL(clicked()), this, SLOT(loadRemoteSampleData()));`
- Connected slots/functions: `loadRemoteSampleData`

## widget: LoadNonDicomDataButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Add Data | LoadNonDicomDataButton | QPushButton
- Text: Add Data
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:215: connect(d->LoadNonDicomDataButton, SIGNAL(clicked()), this, SLOT(loadNonDicomData()));`
- Connected slots/functions: `loadNonDicomData`

## widget: LoadDicomDataButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Add DICOM Data | LoadDicomDataButton | QPushButton
- Text: Add DICOM Data
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:214: connect(d->LoadDicomDataButton, SIGNAL(clicked()), this, SLOT(loadDicomData()));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:221: d->LoadDicomDataButton->hide();`
- Connected slots/functions: `loadDicomData`

## widget: EditApplicationSettingsButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Customize Slicer | EditApplicationSettingsButton | QPushButton
- Text: Customize Slicer
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:217: connect(d->EditApplicationSettingsButton, SIGNAL(clicked()), this, SLOT(editApplicationSettings()));`
- Connected slots/functions: `editApplicationSettings`

## widget: ExploreLoadedDataPushButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Explore Added Data | ExploreLoadedDataPushButton | QPushButton
- Text: Explore Added Data
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:218: connect(d->ExploreLoadedDataPushButton, SIGNAL(clicked()), this, SLOT(exploreLoadedData()));`
- Connected slots/functions: `exploreLoadedData`

## widget: ApplicationUpdateAvailableButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: A new version of the application is available. Click the button to go to the download page. | ApplicationUpdateAvailableButton | QPushButton
- Tooltip: A new version of the application is available. Click the button to go to the download page.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:104: palette.setColor(this->ApplicationUpdateAvailableButton->foregroundRole(), QColor("orange"));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:105: this->ApplicationUpdateAvailableButton->setPalette(palette);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:106: this->ApplicationUpdateAvailableButton->hide();`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:258: QObject::connect(d->ApplicationUpdateAvailableButton, SIGNAL(clicked()), qSlicerApplication::application(), SLOT(openApplicationDownloadWebsite()));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:403: d->ApplicationUpdateAvailableButton->hide();`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:411: d->ApplicationUpdateAvailableButton->setText(buttonText);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:412: d->ApplicationUpdateAvailableButton->show();`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:415: d->ApplicationUpdateStatusButton->setToolTip(d->ApplicationUpdateAvailableButton->toolTip());`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:444: d->ApplicationUpdateAvailableButton->hide();`
- Connected slots/functions: `openApplicationDownloadWebsite`

## widget: FeedbackCollapsibleWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Feedback | FeedbackCollapsibleWidget | ctkCollapsibleButton
- Text: Feedback
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:125: widgetList << this->FeedbackCollapsibleWidget         //`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:298: d->FeedbackCollapsibleWidget->setCollapsed(false);`

## widget: feedbackTextBrowser

- Confidence: `ui_only`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: feedbackTextBrowser | ctkFittedTextBrowser
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: WelcomeAndAboutCollapsibleWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: About | WelcomeAndAboutCollapsibleWidget | ctkCollapsibleButton
- Text: About
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:126: << this->WelcomeAndAboutCollapsibleWidget  //`

## widget: aboutTextBrowser

- Confidence: `ui_only`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: aboutTextBrowser | ctkFittedTextBrowser
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: OtherUsefulHintsCollapsibleWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Documentation && Tutorials | OtherUsefulHintsCollapsibleWidget | ctkCollapsibleButton
- Text: Documentation && Tutorials
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:127: << this->OtherUsefulHintsCollapsibleWidget //`

## widget: documentationTextBrowser

- Confidence: `ui_only`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: documentationTextBrowser | ctkFittedTextBrowser
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: AutomaticUpdatesCollapsibleWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Updates | Click the button to check for updates now. Note that anonymized usage statistics will be recorded. | AutomaticUpdatesCollapsibleWidget | ctkCollapsibleButton
- Text: Updates
- Tooltip: Click the button to check for updates now. Note that anonymized usage statistics will be recorded.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:277: d->AutomaticUpdatesCollapsibleWidget->hide();`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Check for updates:  | label_3 | QLabel
- Text: Check for updates: 
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: CheckForUpdatesAutomaticallyCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Automatically | Periodically check for updates. Note that anonymized usage statistics will be recorded. If the box appears as partially checked it means that automatic updates are only checked for the application or for extensions, but not both - click the checkbox to enable/disable all automatic update checks. | CheckForUpdatesAutomaticallyCheckBox | QCheckBox
- Text: Automatically
- Tooltip: Periodically check for updates. Note that anonymized usage statistics will be recorded. If the box appears as partially checked it means that automatic updates are only checked for the application or for extensions, but not both - click the checkbox to enable/disable all automatic update checks.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:286: QObject::connect(d->CheckForUpdatesAutomaticallyCheckBox, &QCheckBox::checkStateChanged, this, &qSlicerWelcomeModuleWidget::onAutoUpdateCheckStateChanged);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:288: QObject::connect(d->CheckForUpdatesAutomaticallyCheckBox, SIGNAL(stateChanged(int)), this, SLOT(onAutoUpdateCheckStateChanged(int)));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:510: QSignalBlocker blocker(d->CheckForUpdatesAutomaticallyCheckBox);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:513: d->CheckForUpdatesAutomaticallyCheckBox->setCheckState(Qt::Checked);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:514: d->CheckForUpdatesAutomaticallyCheckBox->setTristate(false);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:518: d->CheckForUpdatesAutomaticallyCheckBox->setTristate(false);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:519: d->CheckForUpdatesAutomaticallyCheckBox->setCheckState(Qt::Unchecked);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:523: d->CheckForUpdatesAutomaticallyCheckBox->setCheckState(Qt::PartiallyChecked);`
- Connected slots/functions: `checkStateChanged`, `onAutoUpdateCheckStateChanged`

## widget: CheckForUpdatesNowButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Check now | Click the button to check for updates now. Note that anonymized usage statistics will be recorded. | CheckForUpdatesNowButton | QPushButton
- Text: Check now
- Tooltip: Click the button to check for updates now. Note that anonymized usage statistics will be recorded.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:291: QObject::connect(d->CheckForUpdatesNowButton, SIGNAL(clicked()), this, SLOT(checkForUpdates()));`
- Connected slots/functions: `checkForUpdates`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Application update:  | label_4 | QLabel
- Text: Application update: 
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: ApplicationUpdateStatusButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: No information is available. | ApplicationUpdateStatusButton | QPushButton
- Text: No information is available.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:259: QObject::connect(d->ApplicationUpdateStatusButton, SIGNAL(clicked()), qSlicerApplication::application(), SLOT(openApplicationDownloadWebsite()));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:404: d->ApplicationUpdateStatusButton->setEnabled(false);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:405: d->ApplicationUpdateStatusButton->setText(d->NoUpdatesWereFoundText);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:406: d->ApplicationUpdateStatusButton->setToolTip("");`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:413: d->ApplicationUpdateStatusButton->setText(buttonText);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:414: d->ApplicationUpdateStatusButton->setEnabled(true);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:415: d->ApplicationUpdateStatusButton->setToolTip(d->ApplicationUpdateAvailableButton->toolTip());`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:441: d->ApplicationUpdateStatusButton->setEnabled(false);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:442: d->ApplicationUpdateStatusButton->setText(d->CheckingForUpdatesText);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:443: d->ApplicationUpdateStatusButton->setToolTip("");`
- Connected slots/functions: `openApplicationDownloadWebsite`

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Extension updates:  | label_5 | QLabel
- Text: Extension updates: 
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`

## widget: ExtensionUpdatesStatusButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: No information is available. | Raise the "Extensions Manager" wizard that allows to find, download and install Slicer extensions.<br><br>An extension is a delivery package bundling together one or more Slicer modules.<br><br>After installing an extension, the associated modules will be available in the module selector. | ExtensionUpdatesStatusButton | QPushButton
- Text: No information is available.
- Tooltip: Raise the "Extensions Manager" wizard that allows to find, download and install Slicer extensions.<br><br>An extension is a delivery package bundling together one or more Slicer modules.<br><br>After installing an extension, the associated modules will be available in the module selector.
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:293: QObject::connect(d->ExtensionUpdatesStatusButton, SIGNAL(clicked()), qSlicerApplication::application(), SLOT(openExtensionsManagerDialog()));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:370: d->ExtensionUpdatesStatusButton->setEnabled(false);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:371: d->ExtensionUpdatesStatusButton->setText(d->NoUpdatesWereFoundText);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:375: d->ExtensionUpdatesStatusButton->setEnabled(true);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:376: d->ExtensionUpdatesStatusButton->setText(tr("%1 extension update is available", "%1 extension updates are available", availableUpdates.size()).arg(availableUpdates.size()));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:377: d->ExtensionUpdatesStatusButton->setToolTip(tr("Use Extensions Manager to update these extensions:") + QString("\n- ") + availableUpdates.join("\n- "));`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:429: d->ExtensionUpdatesStatusButton->setText(d->CheckingForUpdatesText);`
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:430: d->ExtensionUpdatesStatusButton->setEnabled(false);`
- Connected slots/functions: `openExtensionsManagerDialog`

## widget: AcknowledgmentCollapsibleWidget

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Acknowledgment | AcknowledgmentCollapsibleWidget | ctkCollapsibleButton
- Text: Acknowledgment
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx:128: << this->AcknowledgmentCollapsibleWidget;`

## widget: acknowledgmentTextBrowser

- Confidence: `ui_only`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: acknowledgmentTextBrowser | ctkFittedTextBrowser
- Implementation candidates: `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.cxx`, `Modules/Loadable/SlicerWelcome/qSlicerWelcomeModuleWidget.h`
