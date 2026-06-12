# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerWebWidget.ui

- Owner class: `qSlicerWebWidget`
- UI file: `Base/QTGUI/Resources/UI/qSlicerWebWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerWebWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qSlicerWebWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerWebWidget.cxx`, `Base/QTGUI/qSlicerWebWidget.h`, `Base/QTGUI/qSlicerWebWidget_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerWebWidget.cxx:49: #include "qSlicerWebWidget.h"`
  - `Base/QTGUI/qSlicerWebWidget.cxx:50: #include "qSlicerWebWidget_p.h"`
  - `Base/QTGUI/qSlicerWebWidget.cxx:90: qSlicerWebWidgetPrivate::qSlicerWebWidgetPrivate(qSlicerWebWidget& object)`
  - `Base/QTGUI/qSlicerWebWidget.cxx:98: qSlicerWebWidgetPrivate::~qSlicerWebWidgetPrivate() = default;`
  - `Base/QTGUI/qSlicerWebWidget.cxx:101: void qSlicerWebWidgetPrivate::initializeWebChannel(QWebChannel* webChannel)`
  - `Base/QTGUI/qSlicerWebWidget.cxx:107: void qSlicerWebWidgetPrivate::init()`
  - `Base/QTGUI/qSlicerWebWidget.cxx:109: Q_Q(qSlicerWebWidget);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:163: void qSlicerWebWidgetPrivate::onAppAboutToQuit()`
  - `Base/QTGUI/qSlicerWebWidget.cxx:174: void qSlicerWebWidgetPrivate::updateWebChannelScript(QByteArray& webChannelScript)`
  - `Base/QTGUI/qSlicerWebWidget.cxx:183: void qSlicerWebWidgetPrivate::initializeWebChannelTransport(QByteArray& webChannelScript)`
  - `Base/QTGUI/qSlicerWebWidget.cxx:189: void qSlicerWebWidgetPrivate::initializeWebEngineProfile(QWebEngineProfile* profile)`
  - `Base/QTGUI/qSlicerWebWidget.cxx:235: void qSlicerWebWidgetPrivate::setDocumentWebkitHidden(bool value)`

## widget: ProgressBar

- Confidence: `linked_to_slot`
- Widget/action class: `QProgressBar`
- Search text: ProgressBar | QProgressBar
- Implementation candidates: `Base/QTGUI/qSlicerWebWidget.cxx`, `Base/QTGUI/qSlicerWebWidget.h`, `Base/QTGUI/qSlicerWebWidget_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerWebWidget.cxx:152: QObject::connect(this->WebView, SIGNAL(loadProgress(int)), this->ProgressBar, SLOT(setValue(int)));`
  - `Base/QTGUI/qSlicerWebWidget.cxx:156: this->ProgressBar->setVisible(false);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:382: d->ProgressBar->setVisible(true);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:408: d->ProgressBar->setFormat(QString("%p% (%1 %2)").arg(speed, 3, 'f', 1).arg(unit));`
  - `Base/QTGUI/qSlicerWebWidget.cxx:409: d->ProgressBar->setMaximum(bytesTotal);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:410: d->ProgressBar->setValue(bytesReceived);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:418: d->ProgressBar->reset();`
  - `Base/QTGUI/qSlicerWebWidget.cxx:419: d->ProgressBar->setVisible(false);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:443: d->ProgressBar->setFormat("%p%");`
  - `Base/QTGUI/qSlicerWebWidget.cxx:444: d->ProgressBar->setVisible(true);`
  - `Base/QTGUI/qSlicerWebWidget.cxx:459: d->ProgressBar->reset();`
  - `Base/QTGUI/qSlicerWebWidget.cxx:460: d->ProgressBar->setVisible(false);`
- Connected slots/functions: `setValue`
