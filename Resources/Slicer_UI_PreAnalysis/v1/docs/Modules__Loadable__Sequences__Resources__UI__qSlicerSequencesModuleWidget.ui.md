# Slicer UI Analysis: Modules/Loadable/Sequences/Resources/UI/qSlicerSequencesModuleWidget.ui

- Owner class: `qSlicerSequencesModuleWidget`
- UI file: `Modules/Loadable/Sequences/Resources/UI/qSlicerSequencesModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSequencesModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSequencesModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:28: #include "qSlicerSequencesModuleWidget.h"`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:30: #include "ui_qSlicerSequencesModuleWidget.h"`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:69: class qSlicerSequencesModuleWidgetPrivate : public Ui_qSlicerSequencesModuleWidget`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:71: Q_DECLARE_PUBLIC(qSlicerSequencesModuleWidget);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:74: qSlicerSequencesModuleWidget* const q_ptr;`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:77: qSlicerSequencesModuleWidgetPrivate(qSlicerSequencesModuleWidget& object);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:78: ~qSlicerSequencesModuleWidgetPrivate();`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:108: // qSlicerSequencesModuleWidgetPrivate methods`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:111: qSlicerSequencesModuleWidgetPrivate::qSlicerSequencesModuleWidgetPrivate(qSlicerSequencesModuleWidget& object)`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:124: qSlicerSequencesModuleWidgetPrivate::~qSlicerSequencesModuleWidgetPrivate()`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:149: void qSlicerSequencesModuleWidgetPrivate::setAndObserveCrosshairNode()`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:151: Q_Q(qSlicerSequencesModuleWidget);`
- Connected slots/functions: `checkStateChanged`, `setMRMLScene`, `synchronizedSequenceNodeOverwriteProxyNameStateChanged`, `synchronizedSequenceNodePlaybackStateChanged`, `synchronizedSequenceNodeRecordingStateChanged`, `synchronizedSequenceNodeSaveChangesStateChanged`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox_ActiveBrowser.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox_SynchronizeSequenceNode.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox_MasterSequence.setMRMLScene(vtkMRMLScene*)`; `mrmlSceneChanged(vtkMRMLScene*) -> MRMLNodeComboBox_Sequence.setMRMLScene(vtkMRMLScene*)`
- API footprints: `AddPlot`, `GetAxis`, `GetClassName`, `GetNodeByID`, `GetNthRegisteredNodeClass`, `GetNumberOfRegisteredNodeClasses`, `GetPointer`, `HasCopyContent`, `IsBatchProcessing`, `RemovePlot`, `SetOverwriteProxyName`, `SetPlayback`, `SetRecording`, `SetSaveChanges`, `SetTitle`, `vtkMRMLSequenceBrowserNode::SafeDownCast`, `vtkMRMLSequenceNode::SafeDownCast`

## widget: mainTabWidget

- Confidence: `linked_to_api`
- Widget/action class: `QTabWidget`
- Search text: mainTabWidget | QTabWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:405: connect(d->mainTabWidget, SIGNAL(currentChanged(int)), this, SLOT(onCurrentTabChanged()));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1171: d->mainTabWidget->setCurrentIndex(0); // browse tab`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1179: d->mainTabWidget->setCurrentIndex(1); // edit tab`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1193: if (d->mainTabWidget->currentWidget() == d->editSequenceTab //`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1206: if (d->mainTabWidget->currentWidget() == d->editSequenceTab)`
- Connected slots/functions: `onCurrentTabChanged`
- API footprints: `GetNumberOfDataNodes`, `vtkMRMLSequenceNode::SafeDownCast`

## widget: browseSequenceTab

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: browseSequenceTab | QWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Sequence browser: | label | QLabel
- Text: Sequence browser:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`, `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py`, `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:72: self.section_SaveVolumeSequence("label")`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:174: # Test saving and loading of sequence with volume type "scalar" or "label"`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:185: elif volumeType == "label":`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:188: volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode", f"labelmap_{i}")`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:192: # Add labelmap to sequence`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:202: elif volumeType == "label":`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:203: slicer.util.setSliceViewerLayers(label=browserNode.GetProxyNode(sequenceNode))`
  - `Modules/Loadable/Sequences/Testing/Python/SequencesSelfTest.py:220: elif volumeType == "label":`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:59: this->label_IndexValue->setFont(QFontDatabase::systemFont(QFontDatabase::FixedFont));`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:126: // Reset the fixed width of the label`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:127: QFontMetrics fontMetrics = QFontMetrics(d->label_IndexValue->font());`
  - `Modules/Loadable/Sequences/Widgets/qMRMLSequenceBrowserSeekWidget.cxx:128: d->label_IndexValue->setFixedWidth(fontMetrics.horizontalAdvance(d->label_IndexValue->text()));`
- API footprints: `AddNewNodeByClass`, `Clear`, `GetClassName`, `GetIndexName`, `GetProxyNode`, `SetDataNodeAtValue`

## widget: MRMLNodeComboBox_ActiveBrowser

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_ActiveBrowser | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:409: connect(d->MRMLNodeComboBox_ActiveBrowser, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(activeBrowserNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:437: this->activeBrowserNodeChanged(d->MRMLNodeComboBox_ActiveBrowser->currentNode());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:660: d->MRMLNodeComboBox_ActiveBrowser->setCurrentNode(browserNode);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:712: vtkMRMLSequenceBrowserNode* browserNode = vtkMRMLSequenceBrowserNode::SafeDownCast(d->MRMLNodeComboBox_ActiveBrowser->currentNode());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1172: d->MRMLNodeComboBox_ActiveBrowser->setCurrentNode(node);`
- Connected slots/functions: `activeBrowserNodeChanged`
- API footprints: `vtkMRMLSequenceBrowserNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSequenceBrowserNode"]}

## widget: InputSection

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Browsing | InputSection | ctkCollapsibleButton
- Text: Browsing
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: sequenceBrowserSeekWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLSequenceBrowserSeekWidget`
- Search text: sequenceBrowserSeekWidget | qMRMLSequenceBrowserSeekWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:662: d->sequenceBrowserSeekWidget->setMRMLSequenceBrowserNode(browserNode);`

## widget: sequenceBrowserPlayWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLSequenceBrowserPlayWidget`
- Search text: sequenceBrowserPlayWidget | qMRMLSequenceBrowserPlayWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:661: d->sequenceBrowserPlayWidget->setMRMLSequenceBrowserNode(browserNode);`

## widget: SynchronizedBrowsingSection

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Synchronized nodes | SynchronizedBrowsingSection | ctkCollapsibleButton
- Text: Synchronized nodes
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:768: d->SynchronizedBrowsingSection->setEnabled(d->ActiveBrowserNode != nullptr);`

## widget: MRMLNodeComboBox_SynchronizeSequenceNode

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_SynchronizeSequenceNode | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:718: vtkMRMLSequenceNode* sequenceNode = vtkMRMLSequenceNode::SafeDownCast(d->MRMLNodeComboBox_SynchronizeSequenceNode->currentNode());`
- API footprints: `AddSynchronizedNode`, `vtkMRMLSequenceNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSequenceNode"]}

## widget: pushButton_AddSequenceNode

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Add the selected sequence to the browser. | pushButton_AddSequenceNode | QPushButton
- Tooltip: Add the selected sequence to the browser.
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:367: d->pushButton_AddSequenceNode->setIcon(QIcon(":/Icons/Add.png"));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:416: connect(d->pushButton_AddSequenceNode, SIGNAL(clicked()), this, SLOT(onAddSequenceNodeButtonClicked()));`
- Connected slots/functions: `onAddSequenceNodeButtonClicked`
- API footprints: `AddSynchronizedNode`, `GetMasterSequenceNode`, `GetNumberOfSynchronizedSequenceNodes`, `GetRecording`, `SetRecording`, `vtkMRMLSequenceBrowserNode::SafeDownCast`, `vtkMRMLSequenceNode::SafeDownCast`

## widget: pushButton_RemoveSequenceNode

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Remove the selected sequence(s) from the browser. | pushButton_RemoveSequenceNode | QPushButton
- Tooltip: Remove the selected sequence(s) from the browser.
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:368: d->pushButton_RemoveSequenceNode->setIcon(QIcon(":/Icons/Remove.png"));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:417: connect(d->pushButton_RemoveSequenceNode, SIGNAL(clicked()), this, SLOT(onRemoveSequenceNodesButtonClicked()));`
- Connected slots/functions: `onRemoveSequenceNodesButtonClicked`
- API footprints: `RemoveSynchronizedSequenceNode`

## widget: tableWidget_SynchronizedSequenceNodes

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: tableWidget_SynchronizedSequenceNodes | QTableWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:370: QHeaderView* tableWidget_SynchronizedSequenceNodes_HeaderView = d->tableWidget_SynchronizedSequenceNodes->horizontalHeader();`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:372: tableWidget_SynchronizedSequenceNodes_HeaderView->setSectionResizeMode(SYNCH_NODES_NAME_COLUMN, QHeaderView::Interactive);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:373: tableWidget_SynchronizedSequenceNodes_HeaderView->setSectionResizeMode(SYNCH_NODES_PROXY_COLUMN, QHeaderView::Interactive);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:374: tableWidget_SynchronizedSequenceNodes_HeaderView->setSectionResizeMode(SYNCH_NODES_PLAYBACK_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:375: tableWidget_SynchronizedSequenceNodes_HeaderView->setSectionResizeMode(SYNCH_NODES_RECORDING_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:376: tableWidget_SynchronizedSequenceNodes_HeaderView->setSectionResizeMode(SYNCH_NODES_OVERWRITE_PROXY_NAME_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:377: tableWidget_SynchronizedSequenceNodes_HeaderView->setSectionResizeMode(SYNCH_NODES_SAVE_CHANGES_COLUMN, QHeaderView::ResizeToContents);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:379: tableWidget_SynchronizedSequenceNodes_HeaderView->setStretchLastSection(false);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:381: d->tableWidget_SynchronizedSequenceNodes->setColumnWidth(SYNCH_NODES_NAME_COLUMN, 200);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:382: d->tableWidget_SynchronizedSequenceNodes->setColumnWidth(SYNCH_NODES_PROXY_COLUMN, 200);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:743: QModelIndexList modelIndexList = d->tableWidget_SynchronizedSequenceNodes->selectionModel()->selectedIndexes();`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:747: QWidget* proxyNodeComboBox = d->tableWidget_SynchronizedSequenceNodes->cellWidget(index->row(), SYNCH_NODES_PROXY_COLUMN);`
- Connected slots/functions: `sequenceNodeNameEdited`
- API footprints: `GetID`, `GetName`, `GetNodeByID`, `GetNumberOfItems`, `GetPointer`, `GetProxyNode`, `GetSynchronizedSequenceNodes`, `SetName`, `vtkMRMLSequenceNode::SafeDownCast`

## widget: PlottingSection

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Plotting | PlottingSection | ctkCollapsibleButton
- Text: Plotting
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:769: d->PlottingSection->setEnabled(d->ActiveBrowserNode != nullptr);`
- Key UI properties: {"checked": "false"}

## widget: pushButton_iCharting

- Confidence: `linked_to_code`
- Widget/action class: `QPushButton`
- Search text: Enable interactive charting | pushButton_iCharting | QPushButton
- Text: Enable interactive charting
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1148: if (d->pushButton_iCharting->isChecked())`
- Key UI properties: {"checkable": "true", "checked": "false"}

## widget: ChartView_iCharting

- Confidence: `linked_to_code`
- Widget/action class: `ctkVTKChartView`
- Search text: ChartView_iCharting | ctkVTKChartView
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:186: this->ChartXY = this->ChartView_iCharting->chart();`

## widget: AdvancedSection

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Advanced | AdvancedSection | ctkCollapsibleButton
- Text: Advanced
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:770: d->AdvancedSection->setEnabled(d->ActiveBrowserNode != nullptr);`
- Key UI properties: {"checked": "false"}

## widget: label_PlaybackItemSkippingEnabled

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable item skip during playback: | label_PlaybackItemSkippingEnabled | QLabel
- Text: Enable item skip during playback:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: checkBox_PlaybackItemSkippingEnabled

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: If checked, items may be skipped during playback to reach the requested frame rate. If not checked then each item is displayed during playback but the playback speed may be lower than requested. | checkBox_PlaybackItemSkippingEnabled | QCheckBox
- Tooltip: If checked, items may be skipped during playback to reach the requested frame rate. If not checked then each item is displayed during playback but the playback speed may be lower than requested.
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:411: connect(d->checkBox_PlaybackItemSkippingEnabled, SIGNAL(toggled(bool)), this, SLOT(playbackItemSkippingEnabledChanged(bool)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:784: wasBlocked = d->checkBox_PlaybackItemSkippingEnabled->blockSignals(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:785: d->checkBox_PlaybackItemSkippingEnabled->setChecked(d->ActiveBrowserNode->GetPlaybackItemSkippingEnabled());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:786: d->checkBox_PlaybackItemSkippingEnabled->blockSignals(wasBlocked);`
- Connected slots/functions: `playbackItemSkippingEnabledChanged`
- API footprints: `GetPlaybackItemSkippingEnabled`, `SetPlaybackItemSkippingEnabled`

## widget: label_RecordMasterOnly

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Record on master node only: | label_RecordMasterOnly | QLabel
- Text: Record on master node only:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: checkBox_RecordMasterOnly

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: checkBox_RecordMasterOnly | QCheckBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:412: connect(d->checkBox_RecordMasterOnly, SIGNAL(toggled(bool)), this, SLOT(recordMasterOnlyChanged(bool)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:788: wasBlocked = d->checkBox_RecordMasterOnly->blockSignals(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:789: d->checkBox_RecordMasterOnly->setChecked(d->ActiveBrowserNode->GetRecordMasterOnly());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:790: d->checkBox_RecordMasterOnly->blockSignals(wasBlocked);`
- Connected slots/functions: `recordMasterOnlyChanged`
- API footprints: `GetRecordMasterOnly`, `SetRecordMasterOnly`

## widget: label_MasterSequence

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Master node: | label_MasterSequence | QLabel
- Text: Master node:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: MRMLNodeComboBox_MasterSequence

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_MasterSequence | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:410: connect(d->MRMLNodeComboBox_MasterSequence, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(sequenceNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:780: bool wasBlocked = d->MRMLNodeComboBox_MasterSequence->blockSignals(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:781: d->MRMLNodeComboBox_MasterSequence->setCurrentNode(sequenceNode);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:782: d->MRMLNodeComboBox_MasterSequence->blockSignals(wasBlocked);`
- Connected slots/functions: `sequenceNodeChanged`
- API footprints: `GetMasterSequenceNode`, `vtkMRMLSequenceNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSequenceNode"]}

## widget: label_RecordingFrameRate

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Recording sampling mode: | label_RecordingFrameRate | QLabel
- Text: Recording sampling mode:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: comboBox_RecordingSamplingMode

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: comboBox_RecordingSamplingMode | QComboBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:413: connect(d->comboBox_RecordingSamplingMode, SIGNAL(currentIndexChanged(int)), this, SLOT(recordingSamplingModeChanged(int)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:792: wasBlocked = d->comboBox_RecordingSamplingMode->blockSignals(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:793: d->comboBox_RecordingSamplingMode->setCurrentIndex(d->ActiveBrowserNode->GetRecordingSamplingMode());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:794: d->comboBox_RecordingSamplingMode->blockSignals(wasBlocked);`
- Connected slots/functions: `recordingSamplingModeChanged`
- API footprints: `GetRecordingSamplingMode`, `SetRecordingSamplingMode`

## widget: label_IndexDisplayMode

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Index display: | label_IndexDisplayMode | QLabel
- Text: Index display:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: comboBox_IndexDisplayMode

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: comboBox_IndexDisplayMode | QComboBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:414: connect(d->comboBox_IndexDisplayMode, SIGNAL(currentIndexChanged(int)), this, SLOT(indexDisplayModeChanged(int)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:796: wasBlocked = d->comboBox_IndexDisplayMode->blockSignals(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:797: d->comboBox_IndexDisplayMode->setCurrentIndex(d->ActiveBrowserNode->GetIndexDisplayMode());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:798: d->comboBox_IndexDisplayMode->blockSignals(wasBlocked);`
- Connected slots/functions: `indexDisplayModeChanged`
- API footprints: `GetIndexDisplayMode`, `SetIndexDisplayMode`

## widget: label_IndexDisplayDecimals

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Index display format: | label_IndexDisplayDecimals | QLabel
- Text: Index display format:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: lineEdit_IndexDisplayFormat

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Display index string in SPRINTF format. Only the first conversion specification is replaced. Available specifiers are: fFgGeEs. | lineEdit_IndexDisplayFormat | QLineEdit
- Tooltip: Display index string in SPRINTF format. Only the first conversion specification is replaced. Available specifiers are: fFgGeEs.
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:415: connect(d->lineEdit_IndexDisplayFormat, SIGNAL(textEdited(const QString)), this, SLOT(indexDisplayFormatChanged(const QString)));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:800: wasBlocked = d->lineEdit_IndexDisplayFormat->blockSignals(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:801: int position = d->lineEdit_IndexDisplayFormat->cursorPosition();`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:802: d->lineEdit_IndexDisplayFormat->setText(QString::fromStdString(d->ActiveBrowserNode->GetIndexDisplayFormat()));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:803: d->lineEdit_IndexDisplayFormat->setCursorPosition(position);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:804: d->lineEdit_IndexDisplayFormat->blockSignals(wasBlocked);`
- Connected slots/functions: `indexDisplayFormatChanged`
- API footprints: `GetIndexDisplayFormat`, `SetIndexDisplayFormat`

## widget: editSequenceTab

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: editSequenceTab | QWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1193: if (d->mainTabWidget->currentWidget() == d->editSequenceTab //`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1206: if (d->mainTabWidget->currentWidget() == d->editSequenceTab)`
- API footprints: `GetNumberOfDataNodes`

## widget: MRMLNodeComboBox_Sequence

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLNodeComboBox_Sequence | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:399: this->setActiveSequenceNode(vtkMRMLSequenceNode::SafeDownCast(d->MRMLNodeComboBox_Sequence->currentNode()));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:407: connect(d->MRMLNodeComboBox_Sequence, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onSequenceNodeSelectionChanged()));`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:553: vtkMRMLSequenceNode* sequenceNode = vtkMRMLSequenceNode::SafeDownCast(d->MRMLNodeComboBox_Sequence->currentNode());`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1180: d->MRMLNodeComboBox_Sequence->setCurrentNode(node);`
- Connected slots/functions: `onSequenceNodeSelectionChanged`
- API footprints: `vtkMRMLScene::EndCloseEvent`, `vtkMRMLScene::EndRestoreEvent`, `vtkMRMLSequenceNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLSequenceNode"]}

## widget: Label_ActiveNode

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Sequence: | Label_ActiveNode | QLabel
- Text: Sequence:
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`

## widget: SequenceEditWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSequenceEditWidget`
- Search text: SequenceEditWidget | qMRMLSequenceEditWidget
- Implementation candidates: `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx`, `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:489: d->SequenceEditWidget->setMRMLScene(scene);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1191: d->SequenceEditWidget->setMRMLSequenceNode(newActiveSequenceNode);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1198: d->SequenceEditWidget->setCandidateNodesSectionVisible(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1208: vtkMRMLSequenceNode* sequenceNode = d->SequenceEditWidget->mrmlSequenceNode();`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1213: d->SequenceEditWidget->setCandidateNodesSectionVisible(true);`
  - `Modules/Loadable/Sequences/qSlicerSequencesModuleWidget.cxx:1219: d->SequenceEditWidget->setCandidateNodesSectionVisible(false);`
- API footprints: `GetNumberOfDataNodes`
