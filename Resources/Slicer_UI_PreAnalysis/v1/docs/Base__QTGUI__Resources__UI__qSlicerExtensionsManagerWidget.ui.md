# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerExtensionsManagerWidget.ui

- Owner class: `qSlicerExtensionsManagerWidget`
- UI file: `Base/QTGUI/Resources/UI/qSlicerExtensionsManagerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerExtensionsManagerWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qSlicerExtensionsManagerWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx`, `Base/QTGUI/qSlicerExtensionsManagerWidget.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:46: #include "qSlicerExtensionsManagerWidget.h"`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:52: #include "ui_qSlicerExtensionsManagerWidget.h"`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:159: class qSlicerExtensionsManagerWidgetPrivate : public Ui_qSlicerExtensionsManagerWidget`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:161: Q_DECLARE_PUBLIC(qSlicerExtensionsManagerWidget);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:164: qSlicerExtensionsManagerWidget* const q_ptr;`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:167: qSlicerExtensionsManagerWidgetPrivate(qSlicerExtensionsManagerWidget& object);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:188: qSlicerExtensionsManagerWidgetPrivate::qSlicerExtensionsManagerWidgetPrivate(qSlicerExtensionsManagerWidget& object)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:200: void qSlicerExtensionsManagerWidgetPrivate::init()`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:202: Q_Q(qSlicerExtensionsManagerWidget);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:261: this->MessageWidget->setWindowTitle(qSlicerExtensionsManagerWidget::tr("Extensions Manager"));`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:270: bool qSlicerExtensionsManagerWidgetPrivate::setBatchProcessing(bool newMode)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:272: Q_Q(qSlicerExtensionsManagerWidget);`

## widget: tabWidget

- Confidence: `linked_to_slot`
- Widget/action class: `QTabWidget`
- Search text: tabWidget | QTabWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx`, `Base/QTGUI/qSlicerExtensionsManagerWidget.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:230: this->tabWidget->setCornerWidget(actionsWidget, Qt::TopLeftCorner);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:239: this->tabWidget->setCornerWidget(this->ToolsWidget, Qt::TopRightCorner);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:241: QObject::connect(this->tabWidget, SIGNAL(currentChanged(int)), actionsWidget, SLOT(setCurrentIndex(int)));`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:250: QObject::connect(this->tabWidget, SIGNAL(currentChanged(int)), q, SLOT(onCurrentTabChanged(int)));`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:389: int manageExtensionsTabIndex = d->tabWidget->indexOf(d->ManageExtensionsTab);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:442: d->tabWidget->setTabText(manageExtensionsTabIndex,`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:448: d->tabWidget->setTabEnabled(manageExtensionsTabIndex, false);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:449: d->tabWidget->setCurrentWidget(d->InstallExtensionsTab);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:453: d->tabWidget->setTabEnabled(manageExtensionsTabIndex, true);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:494: if (d->tabWidget->currentWidget() == d->ManageExtensionsTab)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:499: else if (d->tabWidget->currentWidget() == d->InstallExtensionsTab)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:609: if (d->tabWidget->currentWidget() == d->ManageExtensionsTab)`
- Connected slots/functions: `onCurrentTabChanged`, `setCurrentIndex`

## widget: ManageExtensionsTab

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: ManageExtensionsTab | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx`, `Base/QTGUI/qSlicerExtensionsManagerWidget.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:389: int manageExtensionsTabIndex = d->tabWidget->indexOf(d->ManageExtensionsTab);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:494: if (d->tabWidget->currentWidget() == d->ManageExtensionsTab)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:609: if (d->tabWidget->currentWidget() == d->ManageExtensionsTab)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:777: if (d->tabWidget->currentWidget() != d->ManageExtensionsTab)`

## widget: ManageExtensionsPager

- Confidence: `linked_to_code`
- Widget/action class: `QStackedWidget`
- Search text: ManageExtensionsPager | QStackedWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx`, `Base/QTGUI/qSlicerExtensionsManagerWidget.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:215: this->ManageExtensionsPager->addWidget(this->ExtensionsManageBrowser);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:546: d->ManageExtensionsPager->setCurrentIndex(1);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:557: d->ManageExtensionsPager->setCurrentIndex(newUrl.scheme() == /*no tr*/ "about" ? 0 : 1);`

## widget: ExtensionsLocalWidget

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerExtensionsLocalWidget`
- Search text: ExtensionsLocalWidget | qSlicerExtensionsLocalWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx`, `Base/QTGUI/qSlicerExtensionsManagerWidget.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:242: QObject::connect(this->ExtensionsLocalWidget, SIGNAL(linkActivated(QUrl)), q, SLOT(onManageLinkActivated(QUrl)));`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:309: return d->ExtensionsLocalWidget->extensionsManagerModel();`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:325: d->ExtensionsLocalWidget->setExtensionsManagerModel(model);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:611: d->ExtensionsLocalWidget->setSearchText(searchText);`
- Connected slots/functions: `onManageLinkActivated`

## widget: InstallExtensionsTab

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: InstallExtensionsTab | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx`, `Base/QTGUI/qSlicerExtensionsManagerWidget.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:208: this->ExtensionsServerWidget = new qSlicerExtensionsServerWidget(this->InstallExtensionsTab);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:210: this->InstallExtensionsTabLayout->addWidget(this->ExtensionsServerWidget);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:449: d->tabWidget->setCurrentWidget(d->InstallExtensionsTab);`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:499: else if (d->tabWidget->currentWidget() == d->InstallExtensionsTab)`
  - `Base/QTGUI/qSlicerExtensionsManagerWidget.cxx:614: else if (d->tabWidget->currentWidget() == d->InstallExtensionsTab)`
