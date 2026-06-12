# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLPlotViewControllerWidget.ui

- Owner class: `qMRMLPlotViewControllerWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLPlotViewControllerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLPlotViewControllerWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkPopupWidget`
- Search text: qMRMLPlotViewControllerWidget | ctkPopupWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:46: #include "qMRMLPlotViewControllerWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:60: // qMRMLPlotViewControllerWidgetPrivate methods`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:63: qMRMLPlotViewControllerWidgetPrivate::qMRMLPlotViewControllerWidgetPrivate(qMRMLPlotViewControllerWidget& object)`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:73: qMRMLPlotViewControllerWidgetPrivate::~qMRMLPlotViewControllerWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:76: void qMRMLPlotViewControllerWidgetPrivate::setupPopupUi()`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:78: Q_Q(qMRMLPlotViewControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:82: this->Ui_qMRMLPlotViewControllerWidget::setupUi(this->PopupWidget);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:101: void qMRMLPlotViewControllerWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:103: Q_Q(qMRMLPlotViewControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:107: this->ViewLabel->setText(qMRMLPlotViewControllerWidget::tr("P"));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:118: vtkMRMLPlotChartNode* qMRMLPlotViewControllerWidgetPrivate::GetPlotChartNodeFromView()`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:120: Q_Q(qMRMLPlotViewControllerWidget);`
- API footprints: `vtkMRMLPlotChartNode::SafeDownCast`, `vtkMRMLPlotViewNode::SafeDownCast`

## widget: plotChartComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select the PlotChartNode which handles the general Properties of the Plot and allow to select multiple PlotSeriesNodes. | plotChartComboBox | qMRMLNodeComboBox
- Tooltip: Select the PlotChartNode which handles the general Properties of the Plot and allow to select multiple PlotSeriesNodes.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:84: this->connect(this->plotChartComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onPlotChartNodeSelected(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:96: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->plotChartComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:358: bool wasBlocked = d->plotChartComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:359: d->plotChartComboBox->setCurrentNode(mrmlPlotChartNode);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:360: d->plotChartComboBox->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:431: bool plotChartBlockSignals = d->plotChartComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:436: d->plotChartComboBox->blockSignals(plotChartBlockSignals);`
- Connected slots/functions: `onPlotChartNodeSelected`, `setMRMLScene`
- API footprints: `GetID`, `GetNodeByID`, `SetActivePlotChartID`, `SetPlotChartNodeID`, `vtkMRMLPlotChartNode::SafeDownCast`, `vtkMRMLScene::EndBatchProcessEvent`, `vtkMRMLSelectionNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLPlotChartNode"]}

## widget: exportPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Export... | Export plot to SVG file | exportPushButton | QPushButton
- Text: Export...
- Tooltip: Export plot to SVG file
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:93: QObject::connect(this->exportPushButton, SIGNAL(clicked()), q, SLOT(onExportButton()));`
- Connected slots/functions: `onExportButton`
- API footprints: `GetName`, `GetPlotChartNodeFromView`

## widget: plotSeriesComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCheckableNodeComboBox`
- Search text: Add/Remove plots data series to/from the current chart. | plotSeriesComboBox | qMRMLCheckableNodeComboBox
- Tooltip: Add/Remove plots data series to/from the current chart.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:86: this->connect(this->plotSeriesComboBox, SIGNAL(checkedNodesChanged()), SLOT(onPlotSeriesNodesSelected()));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:87: this->connect(this->plotSeriesComboBox, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), SLOT(onPlotSeriesNodeAdded(vtkMRMLNode*)));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:97: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->plotSeriesComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:170: for (int idx = 0; idx < this->plotSeriesComboBox->nodeCount(); idx++)`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:172: vtkMRMLPlotSeriesNode* dn = vtkMRMLPlotSeriesNode::SafeDownCast(this->plotSeriesComboBox->nodeFromIndex(idx));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:174: bool checked = (this->plotSeriesComboBox->checkState(dn) == Qt::Checked);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:363: d->plotSeriesComboBox->setEnabled(mrmlPlotChartNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:372: bool plotBlockSignals = d->plotSeriesComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:373: for (int idx = 0; idx < d->plotSeriesComboBox->nodeCount(); idx++)`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:375: d->plotSeriesComboBox->setCheckState(d->plotSeriesComboBox->nodeFromIndex(idx), Qt::Unchecked);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:377: d->plotSeriesComboBox->blockSignals(plotBlockSignals);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:382: bool plotBlockSignals = d->plotSeriesComboBox->blockSignals(true);`
- Connected slots/functions: `onPlotSeriesNodeAdded`, `onPlotSeriesNodesSelected`, `setMRMLScene`
- API footprints: `AddAndObservePlotSeriesNodeID`, `GetGridVisibility`, `GetID`, `GetPlotSeriesNodeIDs`, `HasPlotSeriesNodeID`, `RemovePlotSeriesNodeID`, `vtkMRMLPlotSeriesNode::SafeDownCast`, `vtkMRMLScene::EndBatchProcessEvent`
- Key UI properties: {"nodeTypes": ["vtkMRMLPlotSeriesNode"]}

## widget: label

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Plot chart: | label | QLabel
- Text: Plot chart:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h:52: /// Set the label for the Plot view (abbreviation for the view name).`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h:55: /// Get the label for the view (abbreviation for the view name).`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Plot data series: | label_2 | QLabel
- Text: Plot data series:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Plot type: | label_3 | QLabel
- Text: Plot type:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`

## widget: plotTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: This combobox allows to change the Type for all the active PlotSeriesNodes. If a value is chosen, all the PlotSeriesNodes referenced by the PlotChartNode will be updated with the new value.  | plotTypeComboBox | QComboBox
- Tooltip: This combobox allows to change the Type for all the active PlotSeriesNodes. If a value is chosen, all the PlotSeriesNodes referenced by the PlotChartNode will be updated with the new value. 
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:89: this->connect(this->plotTypeComboBox, SIGNAL(currentIndexChanged(int)), SLOT(onPlotTypeChanged(int)));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:362: d->plotTypeComboBox->setEnabled(mrmlPlotChartNode != nullptr);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:368: bool wasBlocked = d->plotTypeComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:369: d->plotTypeComboBox->setCurrentIndex(-1);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:370: d->plotTypeComboBox->blockSignals(wasBlocked);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:403: wasBlocked = d->plotTypeComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:407: d->plotTypeComboBox->setCurrentIndex(vtkMRMLPlotSeriesNode::GetPlotTypeFromString(plotType.c_str()));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:411: d->plotTypeComboBox->setCurrentIndex(-1);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:413: d->plotTypeComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onPlotTypeChanged`
- API footprints: `GetPropertyFromAllPlotSeriesNodes`, `SetPropertyToAllPlotSeriesNodes`, `vtkMRMLPlotChartNode::PlotType`, `vtkMRMLPlotSeriesNode::GetPlotTypeAsString`, `vtkMRMLPlotSeriesNode::GetPlotTypeFromString`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Interaction mode: | label_4 | QLabel
- Text: Interaction mode:
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`

## widget: interactionModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Action performed on mouse left-click and drag. | interactionModeComboBox | QComboBox
- Tooltip: Action performed on mouse left-click and drag.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:90: this->connect(this->interactionModeComboBox, SIGNAL(currentIndexChanged(int)), SLOT(onInteractionModeChanged(int)));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:398: wasBlocked = d->interactionModeComboBox->blockSignals(true);`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:399: d->interactionModeComboBox->setCurrentIndex(this->mrmlPlotViewNode()->GetInteractionMode());`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:400: d->interactionModeComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onInteractionModeChanged`
- API footprints: `GetInteractionMode`, `GetLegendVisibility`, `SetInteractionMode`

## action: actionShow_Grid

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Grid | Show grid | actionShow_Grid
- Text: Grid
- Tooltip: Show grid
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:395: d->actionShow_Grid->setChecked(mrmlPlotChartNode->GetGridVisibility());`
- API footprints: `GetGridVisibility`, `GetLegendVisibility`
- Key UI properties: {"checkable": "true"}

## action: actionShow_Legend

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Legend | Show legend | actionShow_Legend
- Text: Legend
- Tooltip: Show legend
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:396: d->actionShow_Legend->setChecked(mrmlPlotChartNode->GetLegendVisibility());`
- API footprints: `GetGridVisibility`, `GetLegendVisibility`
- Key UI properties: {"checkable": "true"}

## action: actionFit_to_window

- Confidence: `linked_to_slot`
- Widget/action class: `action`
- Search text: Fit_to_window | Adjust the Plot Viewer's field of view to match the extent of the Plot axes | actionFit_to_window
- Text: Fit_to_window
- Tooltip: Adjust the Plot Viewer's field of view to match the extent of the Plot axes
- Implementation candidates: `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:91: QObject::connect(this->actionFit_to_window, SIGNAL(triggered()), q, SLOT(fitPlotToAxes()));`
  - `Libs/MRML/Widgets/qMRMLPlotViewControllerWidget.cxx:113: this->FitToWindowToolButton->setDefaultAction(this->actionFit_to_window);`
- Connected slots/functions: `fitPlotToAxes`
