# Slicer UI Analysis: Modules/Loadable/Sequences/Widgets/Resources/UI/qMRMLSequenceBrowserPlayWidget.ui

- Owner class: `qMRMLSequenceBrowserPlayWidget`
- UI file: `Modules/Loadable/Sequences/Widgets/Resources/UI/qMRMLSequenceBrowserPlayWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSequenceBrowserPlayWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLSequenceBrowserPlayWidget | QWidget
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:19: #include "qMRMLSequenceBrowserPlayWidget.h"`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:20: #include "ui_qMRMLSequenceBrowserPlayWidget.h"`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:31: class qMRMLSequenceBrowserPlayWidgetPrivate : public Ui_qMRMLSequenceBrowserPlayWidget`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:33: Q_DECLARE_PUBLIC(qMRMLSequenceBrowserPlayWidget);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:36: qMRMLSequenceBrowserPlayWidget* const q_ptr;`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:39: qMRMLSequenceBrowserPlayWidgetPrivate(qMRMLSequenceBrowserPlayWidget& object);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:50: // qMRMLSequenceBrowserPlayWidgetPrivate methods`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:53: qMRMLSequenceBrowserPlayWidgetPrivate::qMRMLSequenceBrowserPlayWidgetPrivate(qMRMLSequenceBrowserPlayWidget& object)`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:60: void qMRMLSequenceBrowserPlayWidgetPrivate::init()`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:62: Q_Q(qMRMLSequenceBrowserPlayWidget);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:83: // qMRMLSequenceBrowserPlayWidget methods`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:86: qMRMLSequenceBrowserPlayWidget::qMRMLSequenceBrowserPlayWidget(QWidget* newParent)`
- API footprints: `GetMasterSequenceNode`, `GetPointer`, `vtkMRMLSequenceBrowserNode::SafeDownCast`

## widget: pushButton_VcrFirst

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: First frame | pushButton_VcrFirst | QPushButton
- Tooltip: First frame
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:65: QObject::connect(this->pushButton_VcrFirst, SIGNAL(clicked()), q, SLOT(onVcrFirst()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:127: vcrPlaybackControls << d->pushButton_VcrFirst << d->pushButton_VcrLast << d->pushButton_VcrLoop << d->pushButton_VcrNext << d->pushButton_VcrPlayPause`
- Connected slots/functions: `onVcrFirst`
- API footprints: `SelectFirstItem`

## widget: pushButton_VcrPrevious

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Previous frame | pushButton_VcrPrevious | QPushButton
- Tooltip: Previous frame
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:66: QObject::connect(this->pushButton_VcrPrevious, SIGNAL(clicked()), q, SLOT(onVcrPrevious()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:128: << d->pushButton_VcrPrevious;`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:334: d->pushButton_VcrPrevious->setToolTip(tr("Previous frame (%1)").arg(keySequence));`
- Connected slots/functions: `onVcrPrevious`
- API footprints: `SelectNextItem`

## widget: pushButton_VcrPlayPause

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Play/Pause | pushButton_VcrPlayPause | QPushButton
- Tooltip: Play/Pause
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:69: QObject::connect(this->pushButton_VcrPlayPause, SIGNAL(toggled(bool)), q, SLOT(setPlaybackEnabled(bool)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:127: vcrPlaybackControls << d->pushButton_VcrFirst << d->pushButton_VcrLast << d->pushButton_VcrLoop << d->pushButton_VcrNext << d->pushButton_VcrPlayPause`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:136: bool pushButton_VcrPlayPauseBlockSignals = d->pushButton_VcrPlayPause->blockSignals(true);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:137: d->pushButton_VcrPlayPause->setChecked(d->SequenceBrowserNode->GetPlaybackActive());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:138: d->pushButton_VcrPlayPause->blockSignals(pushButton_VcrPlayPauseBlockSignals);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:318: d->pushButton_VcrPlayPause->setToolTip(tr("Play/Pause (%1)").arg(keySequence));`
- Connected slots/functions: `setPlaybackEnabled`
- API footprints: `GetPlaybackActive`, `SetPlaybackActive`, `SetRecordingActive`
- Key UI properties: {"checkable": "true"}

## widget: pushButton_VcrNext

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Next frame | pushButton_VcrNext | QPushButton
- Tooltip: Next frame
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:67: QObject::connect(this->pushButton_VcrNext, SIGNAL(clicked()), q, SLOT(onVcrNext()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:127: vcrPlaybackControls << d->pushButton_VcrFirst << d->pushButton_VcrLast << d->pushButton_VcrLoop << d->pushButton_VcrNext << d->pushButton_VcrPlayPause`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:350: d->pushButton_VcrNext->setToolTip(tr("Next frame (%1)").arg(keySequence));`
- Connected slots/functions: `onVcrNext`
- API footprints: `SelectNextItem`

## widget: pushButton_VcrLast

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Last frame | pushButton_VcrLast | QPushButton
- Tooltip: Last frame
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:68: QObject::connect(this->pushButton_VcrLast, SIGNAL(clicked()), q, SLOT(onVcrLast()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:127: vcrPlaybackControls << d->pushButton_VcrFirst << d->pushButton_VcrLast << d->pushButton_VcrLoop << d->pushButton_VcrNext << d->pushButton_VcrPlayPause`
- Connected slots/functions: `onVcrLast`
- API footprints: `SelectLastItem`

## widget: doubleSpinBox_VcrPlaybackRate

- Confidence: `linked_to_api`
- Widget/action class: `QDoubleSpinBox`
- Search text: doubleSpinBox_VcrPlaybackRate | QDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:71: QObject::connect(this->doubleSpinBox_VcrPlaybackRate, SIGNAL(valueChanged(double)), q, SLOT(setPlaybackRateFps(double)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:145: bool signalsBlocked = d->doubleSpinBox_VcrPlaybackRate->blockSignals(true);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:146: d->doubleSpinBox_VcrPlaybackRate->setValue(d->SequenceBrowserNode->GetPlaybackRateFps());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:147: d->doubleSpinBox_VcrPlaybackRate->blockSignals(signalsBlocked);`
- Connected slots/functions: `setPlaybackRateFps`
- API footprints: `GetPlaybackRateFps`, `SetPlaybackRateFps`

## widget: pushButton_VcrLoop

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Loop playback | pushButton_VcrLoop | QPushButton
- Tooltip: Loop playback
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:70: QObject::connect(this->pushButton_VcrLoop, SIGNAL(toggled(bool)), q, SLOT(setPlaybackLoopEnabled(bool)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:127: vcrPlaybackControls << d->pushButton_VcrFirst << d->pushButton_VcrLast << d->pushButton_VcrLoop << d->pushButton_VcrNext << d->pushButton_VcrPlayPause`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:140: bool pushButton_VcrLoopBlockSignals = d->pushButton_VcrLoop->blockSignals(true);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:141: d->pushButton_VcrLoop->setChecked(d->SequenceBrowserNode->GetPlaybackLooped());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:142: d->pushButton_VcrLoop->blockSignals(pushButton_VcrLoopBlockSignals);`
- Connected slots/functions: `setPlaybackLoopEnabled`
- API footprints: `GetPlaybackLooped`, `SetPlaybackLooped`
- Key UI properties: {"checkable": "true"}

## widget: pushButton_VcrRecord

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Record proxy nodes modifications continuously | pushButton_VcrRecord | QPushButton
- Tooltip: Record proxy nodes modifications continuously
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:72: QObject::connect(this->pushButton_VcrRecord, SIGNAL(toggled(bool)), q, SLOT(setRecordingEnabled(bool)));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:149: bool pushButton_VcrRecordingBlockSignals = d->pushButton_VcrRecord->blockSignals(true);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:150: d->pushButton_VcrRecord->setChecked(d->SequenceBrowserNode->GetRecordingActive());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:151: d->pushButton_VcrRecord->blockSignals(pushButton_VcrRecordingBlockSignals);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:157: d->pushButton_VcrRecord->setVisible(recordingAllowed && d->RecordingControlsVisible);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:158: d->pushButton_VcrRecord->setEnabled(!playbackActive);`
- Connected slots/functions: `setRecordingEnabled`
- API footprints: `GetRecordingActive`, `IsAnySequenceNodeRecording`, `SetPlaybackActive`, `SetRecordingActive`
- Key UI properties: {"checkable": "true"}

## widget: pushButton_Snapshot

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Record snapshot of current state of all proxy nodes | pushButton_Snapshot | QPushButton
- Tooltip: Record snapshot of current state of all proxy nodes
- Implementation candidates: `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:73: QObject::connect(this->pushButton_Snapshot, SIGNAL(clicked()), q, SLOT(onRecordSnapshot()));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:159: d->pushButton_Snapshot->setVisible(recordingAllowed && d->RecordingControlsVisible);`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserPlayWidget.cxx:160: d->pushButton_Snapshot->setEnabled(!playbackActive && !recordingActive);`
- Connected slots/functions: `onRecordSnapshot`
- API footprints: `SaveProxyNodesState`
