# Slicer UI Analysis: Modules/Loadable/Plots/Resources/UI/qSlicerPlotsModuleWidget.ui

- Owner class: `qSlicerPlotsModuleWidget`
- UI file: `Modules/Loadable/Plots/Resources/UI/qSlicerPlotsModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerPlotsModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerPlotsModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:33: #include "qSlicerPlotsModuleWidget.h"`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:34: #include "ui_qSlicerPlotsModuleWidget.h"`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:57: class qSlicerPlotsModuleWidgetPrivate : public Ui_qSlicerPlotsModuleWidget`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:59: Q_DECLARE_PUBLIC(qSlicerPlotsModuleWidget);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:62: qSlicerPlotsModuleWidget* const q_ptr;`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:65: qSlicerPlotsModuleWidgetPrivate(qSlicerPlotsModuleWidget& object);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:74: qSlicerPlotsModuleWidgetPrivate::qSlicerPlotsModuleWidgetPrivate(qSlicerPlotsModuleWidget& object)`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:81: vtkSlicerPlotsLogic* qSlicerPlotsModuleWidgetPrivate::logic() const`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:83: Q_Q(const qSlicerPlotsModuleWidget);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:89: vtkPlot* qSlicerPlotsModuleWidgetPrivate::table() const`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:100: qSlicerPlotsModuleWidget::qSlicerPlotsModuleWidget(QWidget* _parentWidget)`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:102: , d_ptr(new qSlicerPlotsModuleWidgetPrivate(*this))`
- API footprints: `GetPointer`, `vtkMRMLPlotChartNode::SafeDownCast`

## widget: PlotsTabWidget

- Confidence: `linked_to_code`
- Widget/action class: `QTabWidget`
- Search text: PlotsTabWidget | QTabWidget
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:211: d->PlotsTabWidget->setCurrentIndex(0);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:224: d->PlotsTabWidget->setCurrentIndex(0);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:230: d->PlotsTabWidget->setCurrentIndex(1);`

## widget: charts

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: charts | QWidget
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`

## widget: PlotChartLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Chart: | PlotChartLabel | QLabel
- Text: Chart:
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`

## widget: PlotChartNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: PlotChartNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:116: this->connect(d->PlotChartNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), SLOT(onNodeSelected(vtkMRMLNode*)));`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:210: d->PlotChartNodeSelector->setCurrentNode(tableNode);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:223: d->PlotChartNodeSelector->setCurrentNode(node);`
- Connected slots/functions: `onNodeSelected`
- API footprints: `vtkMRMLPlotChartNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLPlotChartNode"]}

## widget: ShowChartButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Allow plot editing | ShowChartButton | QPushButton
- Tooltip: Allow plot editing
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:121: this->connect(d->ShowChartButton, SIGNAL(clicked()), SLOT(onShowChartButtonClicked()));`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:264: void qSlicerPlotsModuleWidget::onShowChartButtonClicked()`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h:60: void onShowChartButtonClicked();`
- Connected slots/functions: `onShowChartButtonClicked`
- API footprints: `ShowChartInLayout`

## widget: PlotChartPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLPlotChartPropertiesWidget`
- Search text: PlotChartPropertiesWidget | qMRMLPlotChartPropertiesWidget
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:119: this->connect(d->PlotChartPropertiesWidget, SIGNAL(seriesNodeAddedByUser(vtkMRMLNode*)), SLOT(onSeriesNodeAddedByUser(vtkMRMLNode*)));`
- Connected slots/functions: `onSeriesNodeAddedByUser`
- API footprints: `SetUniqueColor`, `vtkMRMLPlotSeriesNode::SafeDownCast`

## widget: series

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: series | QWidget
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:119: this->connect(d->PlotChartPropertiesWidget, SIGNAL(seriesNodeAddedByUser(vtkMRMLNode*)), SLOT(onSeriesNodeAddedByUser(vtkMRMLNode*)));`
- Connected slots/functions: `onSeriesNodeAddedByUser`
- API footprints: `SetUniqueColor`, `vtkMRMLPlotSeriesNode::SafeDownCast`

## widget: PlotDataSeriesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Data series: | PlotDataSeriesLabel | QLabel
- Text: Data series:
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`

## widget: PlotSeriesNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: PlotSeriesNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:118: this->connect(d->PlotSeriesNodeSelector, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), SLOT(onSeriesNodeAddedByUser(vtkMRMLNode*)));`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:229: d->PlotSeriesNodeSelector->setCurrentNode(node);`
  - `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx:299: d->PlotSeriesNodeSelector->setCurrentNode(addedNode);`
- Connected slots/functions: `onSeriesNodeAddedByUser`
- API footprints: `SetUniqueColor`, `vtkMRMLPlotSeriesNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLPlotSeriesNode"]}

## widget: PlotSeriesPropertiesWidget

- Confidence: `ui_only`
- Widget/action class: `qMRMLPlotSeriesPropertiesWidget`
- Search text: PlotSeriesPropertiesWidget | qMRMLPlotSeriesPropertiesWidget
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`

## widget: copyPlotSeriesNodePushButton

- Confidence: `ui_only`
- Widget/action class: `ctkPushButton`
- Search text: Clone data series | copyPlotSeriesNodePushButton | ctkPushButton
- Text: Clone data series
- Implementation candidates: `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.cxx`, `Modules/Loadable/Plots/qSlicerPlotsModuleWidget.h`
