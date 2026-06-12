# Slicer UI Analysis: Modules/Loadable/Plots/Widgets/Resources/UI/qMRMLPlotChartPropertiesWidget.ui

- Owner class: `qMRMLPlotChartPropertiesWidget`
- UI file: `Modules/Loadable/Plots/Widgets/Resources/UI/qMRMLPlotChartPropertiesWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLPlotChartPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLPlotChartPropertiesWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:27: #include "qMRMLPlotChartPropertiesWidget.h"`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:28: #include "qMRMLPlotChartPropertiesWidget_p.h"`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:29: #include "ui_qMRMLPlotChartPropertiesWidget.h"`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:51: qMRMLPlotChartPropertiesWidgetPrivate::qMRMLPlotChartPropertiesWidgetPrivate(qMRMLPlotChartPropertiesWidget& object)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:58: qMRMLPlotChartPropertiesWidgetPrivate::~qMRMLPlotChartPropertiesWidgetPrivate() = default;`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:61: void qMRMLPlotChartPropertiesWidgetPrivate::setupUi(qMRMLWidget* widget)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:63: Q_Q(qMRMLPlotChartPropertiesWidget);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:65: this->Ui_qMRMLPlotChartPropertiesWidget::setupUi(widget);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:98: void qMRMLPlotChartPropertiesWidgetPrivate::updateWidgetFromMRML()`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:100: Q_Q(qMRMLPlotChartPropertiesWidget);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:215: void qMRMLPlotChartPropertiesWidget::setFontType(const QString& type)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:217: Q_D(qMRMLPlotChartPropertiesWidget);`
- API footprints: `vtkMRMLPlotChartNode::SafeDownCast`

## widget: plotDataSeriesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Plot data series: | plotDataSeriesLabel | QLabel
- Text: Plot data series:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: plotSeriesComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLCheckableNodeComboBox`
- Search text: Add/Remove plots data series to/from the current chart. | plotSeriesComboBox | qMRMLCheckableNodeComboBox
- Tooltip: Add/Remove plots data series to/from the current chart.
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:91: this->connect(this->plotSeriesComboBox, SIGNAL(checkedNodesChanged()), this, SLOT(onPlotSeriesNodesSelected()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:92: this->connect(this->plotSeriesComboBox, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), this, SLOT(onPlotSeriesNodeAdded(vtkMRMLNode*)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:94: QObject::connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->plotSeriesComboBox, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:127: bool plotBlockSignals = this->plotSeriesComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:128: for (int idx = 0; idx < this->plotSeriesComboBox->nodeCount(); idx++)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:130: this->plotSeriesComboBox->setCheckState(this->plotSeriesComboBox->nodeFromIndex(idx), Qt::Unchecked);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:132: this->plotSeriesComboBox->blockSignals(plotBlockSignals);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:194: bool plotBlockSignals = this->plotSeriesComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:195: for (int idx = 0; idx < this->plotSeriesComboBox->nodeCount(); idx++)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:197: vtkMRMLNode* node = this->plotSeriesComboBox->nodeFromIndex(idx);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:198: this->plotSeriesComboBox->setCheckState(node, Qt::Unchecked);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:209: this->plotSeriesComboBox->setCheckState(plotSeriesNode, Qt::Checked);`
- Connected slots/functions: `onPlotSeriesNodeAdded`, `onPlotSeriesNodesSelected`, `setMRMLScene`
- API footprints: `AddAndObservePlotSeriesNodeID`, `GetID`, `GetPlotSeriesNodeIDs`, `RemovePlotSeriesNodeID`, `vtkMRMLPlotSeriesNode::SafeDownCast`, `vtkMRMLScene::EndBatchProcessEvent`
- Key UI properties: {"nodeTypes": ["vtkMRMLPlotSeriesNode"]}

## widget: chartTitleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Chart title: | chartTitleLabel | QLabel
- Text: Chart title:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: titleLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Enter a title for the chart. | titleLineEdit | QLineEdit
- Tooltip: Enter a title for the chart.
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:74: QObject::connect(this->titleLineEdit, SIGNAL(textEdited(const QString&)), q, SLOT(setTitle(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:106: this->titleLineEdit->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:186: this->titleLineEdit->setText(this->PlotChartNode->GetTitle() ? this->PlotChartNode->GetTitle() : "");`
- Connected slots/functions: `setTitle`
- API footprints: `GetTitle`, `GetXAxisTitle`, `GetYAxisTitle`, `SetTitle`

## widget: xAxisTitleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X axis title: | xAxisTitleLabel | QLabel
- Text: X axis title:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: xAxisLabelLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Enter a label for the X-axis. | xAxisLabelLineEdit | QLineEdit
- Tooltip: Enter a label for the X-axis.
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:75: QObject::connect(this->xAxisLabelLineEdit, SIGNAL(textEdited(const QString&)), q, SLOT(setXAxisLabel(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:107: this->xAxisLabelLineEdit->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:187: this->xAxisLabelLineEdit->setText(this->PlotChartNode->GetXAxisTitle() ? this->PlotChartNode->GetXAxisTitle() : "");`
- Connected slots/functions: `setXAxisLabel`
- API footprints: `GetTitle`, `GetXAxisTitle`, `GetYAxisTitle`, `SetXAxisTitle`

## widget: xAxisRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: X axis range: | xAxisRangeLabel | QLabel
- Text: X axis range:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: xAxisManualRangeCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable manual setting of X axis range for all views of this chart | xAxisManualRangeCheckBox | QCheckBox
- Tooltip: Enable manual setting of X axis range for all views of this chart
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:80: this->connect(this->xAxisManualRangeCheckBox, SIGNAL(toggled(bool)), q, SLOT(setXAxisManualRangeEnabled(bool)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:110: this->xAxisManualRangeCheckBox->setChecked(false);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:137: this->xAxisManualRangeCheckBox->setChecked(!this->PlotChartNode->GetXAxisRangeAuto());`
- Connected slots/functions: `setEnabled`, `setXAxisManualRangeEnabled`
- Declared UI connections: `toggled(bool) -> xAxisRangeMinDoubleSpinBox.setEnabled(bool)`; `toggled(bool) -> xAxisRangeMaxDoubleSpinBox.setEnabled(bool)`
- API footprints: `GetXAxisRangeAuto`, `SetXAxisRangeAuto`

## widget: xAxisRangeMinDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: xAxisRangeMinDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:81: this->connect(this->xAxisRangeMinDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setXAxisRangeMin(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:113: this->xAxisRangeMinDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:141: this->xAxisRangeMinDoubleSpinBox->setValue(range[0]);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:146: bool wasBlocked = this->xAxisRangeMinDoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:147: this->xAxisRangeMinDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:148: this->xAxisRangeMinDoubleSpinBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setXAxisRangeMin`
- API footprints: `GetXAxisRange`, `SetXAxisRange`

## widget: xAxisRangeMaxDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: xAxisRangeMaxDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:82: this->connect(this->xAxisRangeMaxDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setXAxisRangeMax(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:114: this->xAxisRangeMaxDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:142: this->xAxisRangeMaxDoubleSpinBox->setValue(range[1]);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:149: wasBlocked = this->xAxisRangeMaxDoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:150: this->xAxisRangeMaxDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:151: this->xAxisRangeMaxDoubleSpinBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setXAxisRangeMax`
- API footprints: `GetXAxisRange`, `SetXAxisRange`

## widget: yAxisRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y axis range: | yAxisRangeLabel | QLabel
- Text: Y axis range:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: yAxisManualRangeCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable manual setting of Y axis range for all views of this chart | yAxisManualRangeCheckBox | QCheckBox
- Tooltip: Enable manual setting of Y axis range for all views of this chart
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:84: this->connect(this->yAxisManualRangeCheckBox, SIGNAL(toggled(bool)), q, SLOT(setYAxisManualRangeEnabled(bool)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:111: this->yAxisManualRangeCheckBox->setChecked(false);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:154: this->yAxisManualRangeCheckBox->setChecked(!this->PlotChartNode->GetYAxisRangeAuto());`
- Connected slots/functions: `setEnabled`, `setYAxisManualRangeEnabled`
- Declared UI connections: `toggled(bool) -> yAxisRangeMinDoubleSpinBox.setEnabled(bool)`; `toggled(bool) -> yAxisRangeMaxDoubleSpinBox.setEnabled(bool)`
- API footprints: `GetYAxisRangeAuto`, `SetYAxisRangeAuto`

## widget: yAxisRangeMinDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: yAxisRangeMinDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:85: this->connect(this->yAxisRangeMinDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setYAxisRangeMin(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:115: this->yAxisRangeMinDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:158: this->yAxisRangeMinDoubleSpinBox->setValue(range[0]);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:163: bool wasBlocked = this->yAxisRangeMinDoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:164: this->yAxisRangeMinDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:165: this->yAxisRangeMinDoubleSpinBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setYAxisRangeMin`
- API footprints: `GetYAxisRange`, `SetYAxisRange`

## widget: yAxisRangeMaxDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: yAxisRangeMaxDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:86: this->connect(this->yAxisRangeMaxDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setYAxisRangeMax(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:116: this->yAxisRangeMaxDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:159: this->yAxisRangeMaxDoubleSpinBox->setValue(range[1]);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:166: wasBlocked = this->yAxisRangeMaxDoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:167: this->yAxisRangeMaxDoubleSpinBox->setValue(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:168: this->yAxisRangeMaxDoubleSpinBox->blockSignals(wasBlocked);`
- Connected slots/functions: `setYAxisRangeMax`
- API footprints: `GetYAxisRange`, `SetYAxisRange`

## widget: yAxisTitleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Y axis title: | yAxisTitleLabel | QLabel
- Text: Y axis title:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: yAxisLabelLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Enter a label for the Y-axis. | yAxisLabelLineEdit | QLineEdit
- Tooltip: Enter a label for the Y-axis.
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:76: QObject::connect(this->yAxisLabelLineEdit, SIGNAL(textEdited(const QString&)), q, SLOT(setYAxisLabel(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:108: this->yAxisLabelLineEdit->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:188: this->yAxisLabelLineEdit->setText(this->PlotChartNode->GetYAxisTitle() ? this->PlotChartNode->GetYAxisTitle() : "");`
- Connected slots/functions: `setYAxisLabel`
- API footprints: `GetLegendVisibility`, `GetTitle`, `GetXAxisTitle`, `GetYAxisTitle`, `SetYAxisTitle`

## widget: fontTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: fontTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:68: this->connect(this->fontTypeComboBox, SIGNAL(currentIndexChanged(const QString&)), q, SLOT(setFontType(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:118: this->fontTypeComboBox->setCurrentIndex(-1);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:178: this->fontTypeComboBox->setCurrentIndex(this->fontTypeComboBox->findText(this->PlotChartNode->GetFontType() ? this->PlotChartNode->GetFontType() : ""));`
- Connected slots/functions: `setFontType`
- API footprints: `GetFontType`, `GetTitleFontSize`, `SetFontType`

## widget: fontTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Font Type: | fontTypeLabel | QLabel
- Text: Font Type:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: titleFontSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Chart title font size: | titleFontSizeLabel | QLabel
- Text: Chart title font size:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: titleFontSizeDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: titleFontSizeDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:69: this->connect(this->titleFontSizeDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setTitleFontSize(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:119: this->titleFontSizeDoubleSpinBox->setValue(20);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:180: this->titleFontSizeDoubleSpinBox->setValue(this->PlotChartNode->GetTitleFontSize());`
- Connected slots/functions: `setTitleFontSize`
- API footprints: `GetAxisTitleFontSize`, `GetFontType`, `GetLegendFontSize`, `GetTitleFontSize`, `SetTitleFontSize`

## widget: axisTitleFontSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Axis title font size: | axisTitleFontSizeLabel | QLabel
- Text: Axis title font size:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: axisTitleFontSizeDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: axisTitleFontSizeDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:71: this->connect(this->axisTitleFontSizeDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setAxisTitleFontSize(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:121: this->axisTitleFontSizeDoubleSpinBox->setValue(16);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:182: this->axisTitleFontSizeDoubleSpinBox->setValue(this->PlotChartNode->GetAxisTitleFontSize());`
- Connected slots/functions: `setAxisTitleFontSize`
- API footprints: `GetAxisLabelFontSize`, `GetAxisTitleFontSize`, `GetLegendFontSize`, `GetTitleFontSize`, `SetAxisTitleFontSize`

## widget: axisLabelFontSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Axis label font size: | axisLabelFontSizeLabel | QLabel
- Text: Axis label font size:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: axisLabelFontSizeDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: axisLabelFontSizeDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:72: this->connect(this->axisLabelFontSizeDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setAxisLabelFontSize(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:122: this->axisLabelFontSizeDoubleSpinBox->setValue(12);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:183: this->axisLabelFontSizeDoubleSpinBox->setValue(this->PlotChartNode->GetAxisLabelFontSize());`
- Connected slots/functions: `setAxisLabelFontSize`
- API footprints: `GetAxisLabelFontSize`, `GetAxisTitleFontSize`, `GetLegendFontSize`, `SetAxisLabelFontSize`

## widget: legendVisibleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Legend visibility: | legendVisibleLabel | QLabel
- Text: Legend visibility:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: legendVisibleCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: legendVisibleCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:77: this->connect(this->legendVisibleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setLegendVisibility(bool)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:124: this->legendVisibleCheckBox->setChecked(false);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:190: this->legendVisibleCheckBox->setChecked(this->PlotChartNode->GetLegendVisibility());`
- Connected slots/functions: `setLegendVisibility`
- API footprints: `GetGridVisibility`, `GetLegendVisibility`, `GetYAxisTitle`, `SetLegendVisibility`

## widget: gridVisibleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Grid visibility: | gridVisibleLabel | QLabel
- Text: Grid visibility:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: legendFontSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Legend font size: | legendFontSizeLabel | QLabel
- Text: Legend font size:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: legendFontSizeDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: legendFontSizeDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:70: this->connect(this->legendFontSizeDoubleSpinBox, SIGNAL(valueChanged(double)), q, SLOT(setLegendFontSize(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:120: this->legendFontSizeDoubleSpinBox->setValue(16);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:181: this->legendFontSizeDoubleSpinBox->setValue(this->PlotChartNode->GetLegendFontSize());`
- Connected slots/functions: `setLegendFontSize`
- API footprints: `GetAxisLabelFontSize`, `GetAxisTitleFontSize`, `GetLegendFontSize`, `GetTitleFontSize`, `SetLegendFontSize`

## widget: logScaleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Logarithmic scale: | logScaleLabel | QLabel
- Text: Logarithmic scale:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`

## widget: xAxisLogScaleCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: X axis | xAxisLogScaleCheckBox | QCheckBox
- Text: X axis
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:88: this->connect(this->xAxisLogScaleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setXAxisLogScale(bool)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:171: bool blockedLogScale = this->xAxisLogScaleCheckBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:172: this->xAxisLogScaleCheckBox->setChecked(this->PlotChartNode->GetXAxisLogScale());`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:173: this->xAxisLogScaleCheckBox->blockSignals(blockedLogScale);`
- Connected slots/functions: `setXAxisLogScale`
- API footprints: `GetXAxisLogScale`, `GetYAxisLogScale`, `SetXAxisLogScale`

## widget: yAxisLogScaleCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Y axis | yAxisLogScaleCheckBox | QCheckBox
- Text: Y axis
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:89: this->connect(this->yAxisLogScaleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setYAxisLogScale(bool)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:174: blockedLogScale = this->yAxisLogScaleCheckBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:175: this->yAxisLogScaleCheckBox->setChecked(this->PlotChartNode->GetYAxisLogScale());`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:176: this->yAxisLogScaleCheckBox->blockSignals(blockedLogScale);`
- Connected slots/functions: `setYAxisLogScale`
- API footprints: `GetFontType`, `GetXAxisLogScale`, `GetYAxisLogScale`, `SetYAxisLogScale`

## widget: gridVisibleCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: gridVisibleCheckBox | QCheckBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:78: this->connect(this->gridVisibleCheckBox, SIGNAL(toggled(bool)), q, SLOT(setGridVisibility(bool)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:125: this->gridVisibleCheckBox->setChecked(false);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:191: this->gridVisibleCheckBox->setChecked(this->PlotChartNode->GetGridVisibility());`
- Connected slots/functions: `setGridVisibility`
- API footprints: `GetGridVisibility`, `GetLegendVisibility`, `SetGridVisibility`
