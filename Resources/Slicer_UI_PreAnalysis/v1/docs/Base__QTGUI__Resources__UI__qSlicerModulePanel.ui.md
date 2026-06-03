# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerModulePanel.ui

- Owner class: `qSlicerModulePanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerModulePanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerModulePanel

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerModulePanel | qSlicerWidget
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModulePanel.cxx:30: #include "qSlicerModulePanel.h"`
  - `Base/QTGUI/qSlicerModulePanel.cxx:31: #include "ui_qSlicerModulePanel.h"`
  - `Base/QTGUI/qSlicerModulePanel.cxx:38: class qSlicerModulePanelPrivate : public Ui_qSlicerModulePanel`
  - `Base/QTGUI/qSlicerModulePanel.cxx:47: qSlicerModulePanel::qSlicerModulePanel(QWidget* _parent, Qt::WindowFlags f)`
  - `Base/QTGUI/qSlicerModulePanel.cxx:49: , d_ptr(new qSlicerModulePanelPrivate)`
  - `Base/QTGUI/qSlicerModulePanel.cxx:51: Q_D(qSlicerModulePanel);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:57: qSlicerModulePanel::~qSlicerModulePanel()`
  - `Base/QTGUI/qSlicerModulePanel.cxx:63: qSlicerAbstractCoreModule* qSlicerModulePanel::currentModule() const`
  - `Base/QTGUI/qSlicerModulePanel.cxx:65: Q_D(const qSlicerModulePanel);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:76: QString qSlicerModulePanel::currentModuleName() const`
  - `Base/QTGUI/qSlicerModulePanel.cxx:83: void qSlicerModulePanel::setModule(const QString& moduleName)`
  - `Base/QTGUI/qSlicerModulePanel.cxx:104: void qSlicerModulePanel::setModule(qSlicerAbstractCoreModule* module)`

## widget: ScrollArea

- Confidence: `linked_to_code`
- Widget/action class: `QScrollArea`
- Search text: ScrollArea | QScrollArea
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModulePanel.cxx:66: QBoxLayout* scrollAreaLayout = qobject_cast<QBoxLayout*>(d->ScrollArea->widget()->layout());`
  - `Base/QTGUI/qSlicerModulePanel.cxx:157: QWidget* scrollAreaContents = d->ScrollArea->widget();`
  - `Base/QTGUI/qSlicerModulePanel.cxx:212: QBoxLayout* scrollAreaLayout = qobject_cast<QBoxLayout*>(d->ScrollArea->widget()->layout());`
  - `Base/QTGUI/qSlicerModulePanel.cxx:290: // QScrollArea::minumumSizeHint is wrong. QScrollArea are not meant to`
  - `Base/QTGUI/qSlicerModulePanel.cxx:293: QSize size = QSize(d->ScrollArea->widget()->minimumSizeHint().width() + d->ScrollArea->horizontalScrollBar()->sizeHint().width(), this->Superclass::minimumSizeHint().height());`
  - `Base/QTGUI/qSlicerModulePanel.cxx:336: this->ScrollArea = new QScrollArea;`
  - `Base/QTGUI/qSlicerModulePanel.cxx:337: this->ScrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:338: this->ScrollArea->setWidget(panel);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:339: this->ScrollArea->setWidgetResizable(true);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:342: gridLayout->addWidget(this->ScrollArea);`

## widget: scrollAreaWidgetContents

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: scrollAreaWidgetContents | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`

## widget: HelpCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Help && Acknowledgement | HelpCollapsibleButton | ctkCollapsibleButton
- Text: Help && Acknowledgement
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModulePanel.cxx:175: d->HelpCollapsibleButton->setVisible(this->isHelpAndAcknowledgmentVisible() && !help.isEmpty());`
  - `Base/QTGUI/qSlicerModulePanel.cxx:257: d->HelpCollapsibleButton->setVisible(true);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:262: d->HelpCollapsibleButton->setVisible(false);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:310: this->HelpCollapsibleButton = new ctkCollapsibleButton("Help");`
  - `Base/QTGUI/qSlicerModulePanel.cxx:311: this->HelpCollapsibleButton->setCollapsed(true);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:312: this->HelpCollapsibleButton->setSizePolicy(`
  - `Base/QTGUI/qSlicerModulePanel.cxx:327: QGridLayout* helpLayout = new QGridLayout(this->HelpCollapsibleButton);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:331: this->Layout->addWidget(this->HelpCollapsibleButton);`

## widget: HelpAcknowledgementTabWidget

- Confidence: `ui_only`
- Widget/action class: `QTabWidget`
- Search text: HelpAcknowledgementTabWidget | QTabWidget
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`

## widget: HelpTab

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: HelpTab | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`

## widget: HelpLabel

- Confidence: `linked_to_code`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: HelpLabel | ctkFittedTextBrowser
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModulePanel.cxx:126: // d->HelpLabel->setHtml("");`
  - `Base/QTGUI/qSlicerModulePanel.cxx:176: d->HelpLabel->setHtml(help);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:255: if (!d->HelpLabel->toHtml().isEmpty())`
  - `Base/QTGUI/qSlicerModulePanel.cxx:304: this->HelpLabel->setOpenExternalLinks(true);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:316: //this->HelpLabel = new QWebView;`
  - `Base/QTGUI/qSlicerModulePanel.cxx:317: this->HelpLabel = static_cast<QTextBrowser*>(new ctkFittedTextBrowser);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:318: this->HelpLabel->setOpenExternalLinks(true);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:319: this->HelpLabel->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:320: this->HelpLabel->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:321: this->HelpLabel->setFrameShape(QFrame::NoFrame);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:323: QPalette p = this->HelpLabel->palette();`
  - `Base/QTGUI/qSlicerModulePanel.cxx:325: this->HelpLabel->setPalette(p);`

## widget: AcknowledgementTab

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: AcknowledgementTab | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`

## widget: AcknowledgementLabel

- Confidence: `linked_to_code`
- Widget/action class: `ctkFittedTextBrowser`
- Search text: AcknowledgementLabel | ctkFittedTextBrowser
- Implementation candidates: `Base/QTGUI/qSlicerModulePanel.cxx`, `Base/QTGUI/qSlicerModulePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerModulePanel.cxx:177: d->AcknowledgementLabel->clear();`
  - `Base/QTGUI/qSlicerModulePanel.cxx:181: d->AcknowledgementLabel->document()->addResource(QTextDocument::ImageResource, QUrl("module://logo.png"), QVariant(guiModule->logo()));`
  - `Base/QTGUI/qSlicerModulePanel.cxx:182: d->AcknowledgementLabel->append(QString("<center><img src=\"module://logo.png\"/></center><br>"));`
  - `Base/QTGUI/qSlicerModulePanel.cxx:185: d->AcknowledgementLabel->insertHtml(acknowledgement);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:191: d->AcknowledgementLabel->append(contributorsText);`
  - `Base/QTGUI/qSlicerModulePanel.cxx:305: this->AcknowledgementLabel->setOpenExternalLinks(true);`
