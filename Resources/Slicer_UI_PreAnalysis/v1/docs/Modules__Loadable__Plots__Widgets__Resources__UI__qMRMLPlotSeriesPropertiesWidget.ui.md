# Slicer UI Analysis: Modules/Loadable/Plots/Widgets/Resources/UI/qMRMLPlotSeriesPropertiesWidget.ui

- Owner class: `qMRMLPlotSeriesPropertiesWidget`
- UI file: `Modules/Loadable/Plots/Widgets/Resources/UI/qMRMLPlotSeriesPropertiesWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLPlotSeriesPropertiesWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLWidget`
- Search text: qMRMLPlotSeriesPropertiesWidget | qMRMLWidget
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:27: #include "qMRMLPlotSeriesPropertiesWidget_p.h"`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:28: #include "ui_qMRMLPlotSeriesPropertiesWidget.h"`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:46: // qMRMLPlotSeriesPropertiesWidgetPrivate methods`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:49: qMRMLPlotSeriesPropertiesWidgetPrivate::qMRMLPlotSeriesPropertiesWidgetPrivate(qMRMLPlotSeriesPropertiesWidget& object)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:56: qMRMLPlotSeriesPropertiesWidgetPrivate::~qMRMLPlotSeriesPropertiesWidgetPrivate() = default;`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:59: void qMRMLPlotSeriesPropertiesWidgetPrivate::setupUi(qMRMLWidget* widget)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:61: Q_Q(qMRMLPlotSeriesPropertiesWidget);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:63: this->Ui_qMRMLPlotSeriesPropertiesWidget::setupUi(widget);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:78: void qMRMLPlotSeriesPropertiesWidgetPrivate::updateWidgetFromMRML()`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:80: Q_Q(qMRMLPlotSeriesPropertiesWidget);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:238: void qMRMLPlotSeriesPropertiesWidgetPrivate::onPlotSeriesNodeChanged(vtkMRMLNode* node)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:255: void qMRMLPlotSeriesPropertiesWidgetPrivate::onInputTableNodeChanged(vtkMRMLNode* node)`
- Connected slots/functions: `setMRMLScene`
- Declared UI connections: `mrmlSceneChanged(vtkMRMLScene*) -> inputTableComboBox.setMRMLScene(vtkMRMLScene*)`
- API footprints: `vtkMRMLPlotSeriesNode::SafeDownCast`, `vtkMRMLTableNode::SafeDownCast`

## widget: InputTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Input Table: | InputTableLabel | QLabel
- Text: Input Table:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: inputTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: inputTableComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:65: this->connect(this->inputTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onInputTableNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:86: this->inputTableComboBox->setCurrentNode(nullptr);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:98: this->inputTableComboBox->setCurrentNode(mrmlTableNode);`
- Connected slots/functions: `onInputTableNodeChanged`
- API footprints: `GetID`, `GetTableNode`, `SetAndObserveTableNodeID`, `vtkMRMLTableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTableNode"]}

## widget: plotTypeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Plot Type: | plotTypeLabel | QLabel
- Text: Plot Type:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: plotTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: plotTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:69: this->connect(this->plotTypeComboBox, SIGNAL(currentIndexChanged(int)), this, SLOT(onPlotTypeChanged(int)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:90: this->plotTypeComboBox->setCurrentIndex(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:187: bool wasBlocked = this->plotTypeComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:188: this->plotTypeComboBox->setCurrentIndex(this->PlotSeriesNode->GetPlotType());`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:189: this->plotTypeComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onPlotTypeChanged`
- API footprints: `GetPlotType`, `SetPlotType`

## widget: xAxisLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: X Axis Column: | xAxisLabel | QLabel
- Text: X Axis Column:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:75: QObject::connect(this->xAxisLabelLineEdit, SIGNAL(textEdited(const QString&)), q, SLOT(setXAxisLabel(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:107: this->xAxisLabelLineEdit->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:187: this->xAxisLabelLineEdit->setText(this->PlotChartNode->GetXAxisTitle() ? this->PlotChartNode->GetXAxisTitle() : "");`
- Connected slots/functions: `setXAxisLabel`
- API footprints: `GetTitle`, `GetXAxisTitle`, `GetYAxisTitle`, `SetXAxisTitle`

## widget: xAxisComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: xAxisComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:66: this->connect(this->xAxisComboBox, SIGNAL(currentIndexChanged(int)), this, SLOT(onXAxisChanged(int)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:87: this->xAxisComboBox->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:101: bool xAxisBlockSignals = this->xAxisComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:107: this->xAxisComboBox->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:129: if (xColumnRequired && this->xAxisComboBox->findData(QString(columnName.c_str())) == -1)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:131: this->xAxisComboBox->addItem(columnName.c_str(), QString(columnName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:144: int xAxisIndex = this->xAxisComboBox->findData(QString(xAxisName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:147: this->xAxisComboBox->addItem(xAxisName.c_str(), QString(xAxisName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:148: xAxisIndex = this->xAxisComboBox->findData(QString(xAxisName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:150: this->xAxisComboBox->setCurrentIndex(xAxisIndex);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:151: this->xAxisComboBox->setToolTip("");`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:155: this->xAxisComboBox->addItem("(Indexes)", QString());`
- Connected slots/functions: `onXAxisChanged`
- API footprints: `GetXColumnName`, `IsXColumnRequired`, `SetXColumnName`

## widget: yAxisLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Y Axis Column: | yAxisLabel | QLabel
- Text: Y Axis Column:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:76: QObject::connect(this->yAxisLabelLineEdit, SIGNAL(textEdited(const QString&)), q, SLOT(setYAxisLabel(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:108: this->yAxisLabelLineEdit->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotChartPropertiesWidget.cxx:188: this->yAxisLabelLineEdit->setText(this->PlotChartNode->GetYAxisTitle() ? this->PlotChartNode->GetYAxisTitle() : "");`
- Connected slots/functions: `setYAxisLabel`
- API footprints: `GetLegendVisibility`, `GetTitle`, `GetXAxisTitle`, `GetYAxisTitle`, `SetYAxisTitle`

## widget: yAxisComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: yAxisComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:68: this->connect(this->yAxisComboBox, SIGNAL(currentIndexChanged(int)), this, SLOT(onYAxisChanged(int)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:89: this->yAxisComboBox->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:103: bool yAxisBlockSignals = this->yAxisComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:109: this->yAxisComboBox->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:133: if (this->yAxisComboBox->findData(QString(columnName.c_str())) == -1)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:135: this->yAxisComboBox->addItem(columnName.c_str(), QString(columnName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:171: int yAxisIndex = this->yAxisComboBox->findData(QString(yAxisName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:174: this->yAxisComboBox->addItem(yAxisName.c_str(), QString(yAxisName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:175: yAxisIndex = this->yAxisComboBox->findData(QString(yAxisName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:177: this->yAxisComboBox->setCurrentIndex(yAxisIndex);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:181: this->yAxisComboBox->blockSignals(yAxisBlockSignals);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:184: this->yAxisComboBox->setEnabled(mrmlTableNode != nullptr);`
- Connected slots/functions: `onYAxisChanged`
- API footprints: `GetYColumnName`, `IsXColumnRequired`, `SetYColumnName`

## widget: labelsComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: This column contains a label for each data point. Label is displayed in the tooltip when the mouse hovers over a data point in the plot view. | labelsComboBox | QComboBox
- Tooltip: This column contains a label for each data point. Label is displayed in the tooltip when the mouse hovers over a data point in the plot view.
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:67: this->connect(this->labelsComboBox, SIGNAL(currentIndexChanged(int)), this, SLOT(onLabelsChanged(int)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:88: this->labelsComboBox->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:102: bool labelsBlockSignals = this->labelsComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:108: this->labelsComboBox->clear();`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:112: if (this->labelsComboBox->findData(QString()) == -1)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:114: this->labelsComboBox->addItem("(none)", QString());`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:122: if (this->labelsComboBox->findData(QString(columnName.c_str())) == -1)`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:124: this->labelsComboBox->addItem(columnName.c_str(), QString(columnName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:161: int labelsIndex = this->labelsComboBox->findData(QString(labelsName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:164: this->labelsComboBox->addItem(labelsName.c_str(), QString(labelsName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:165: labelsIndex = this->labelsComboBox->findData(QString(labelsName.c_str()));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:167: this->labelsComboBox->setCurrentIndex(labelsIndex);`
- Connected slots/functions: `onLabelsChanged`
- API footprints: `GetLabelColumnName`, `GetNumberOfColumns`, `GetYColumnName`, `IsXColumnRequired`, `SetLabelColumnName`

## widget: markersStyleComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: markersStyleComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:70: this->connect(this->markersStyleComboBox, SIGNAL(currentIndexChanged(const QString&)), this, SLOT(onMarkersStyleChanged(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:91: this->markersStyleComboBox->setCurrentIndex(0);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:192: wasBlocked = this->markersStyleComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:195: // this->markersStyleComboBox->setCurrentText(plotMarkersStyle);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:196: this->markersStyleComboBox->setCurrentIndex(this->markersStyleComboBox->findText(plotMarkersStyle));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:197: this->markersStyleComboBox->setEnabled(this->PlotSeriesNode->GetPlotType() == vtkMRMLPlotSeriesNode::PlotTypeScatter //`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:199: this->markersStyleComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:212: // this->markersStyleComboBox->setCurrentText(plotMarkersStyle);`
- Connected slots/functions: `onMarkersStyleChanged`
- API footprints: `GetLineStyle`, `GetLineStyleAsString`, `GetMarkerStyle`, `GetMarkerStyleAsString`, `GetMarkerStyleFromString`, `GetPlotType`, `SetMarkerStyle`, `vtkMRMLPlotSeriesNode::PlotTypeLine`, `vtkMRMLPlotSeriesNode::PlotTypeScatter`

## widget: markersSizeDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: markersSizeDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:71: this->connect(this->markersSizeDoubleSpinBox, SIGNAL(valueChanged(double)), this, SLOT(onMarkersSizeChanged(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:202: wasBlocked = this->markersSizeDoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:203: this->markersSizeDoubleSpinBox->setValue(this->PlotSeriesNode->GetMarkerSize());`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:204: this->markersSizeDoubleSpinBox->setEnabled(this->PlotSeriesNode->GetPlotType() == vtkMRMLPlotSeriesNode::PlotTypeScatter //`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:206: this->markersSizeDoubleSpinBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onMarkersSizeChanged`
- API footprints: `GetMarkerSize`, `GetPlotType`, `SetMarkerSize`, `vtkMRMLPlotSeriesNode::PlotTypeLine`, `vtkMRMLPlotSeriesNode::PlotTypeScatter`

## widget: lineStyleComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: lineStyleComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:72: this->connect(this->lineStyleComboBox, SIGNAL(currentIndexChanged(const QString&)), this, SLOT(onLineStyleChanged(const QString&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:209: wasBlocked = this->lineStyleComboBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:213: this->lineStyleComboBox->setCurrentIndex(this->lineStyleComboBox->findText(plotLineStyle));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:214: this->lineStyleComboBox->setEnabled(this->PlotSeriesNode->GetPlotType() == vtkMRMLPlotSeriesNode::PlotTypeScatter //`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:216: this->lineStyleComboBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onLineStyleChanged`
- API footprints: `GetLineStyle`, `GetLineStyleAsString`, `GetLineStyleFromString`, `GetPlotType`, `SetLineStyle`, `vtkMRMLPlotSeriesNode::PlotTypeLine`, `vtkMRMLPlotSeriesNode::PlotTypeScatter`

## widget: lineWidthDoubleSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: lineWidthDoubleSpinBox | ctkDoubleSpinBox
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:73: this->connect(this->lineWidthDoubleSpinBox, SIGNAL(valueChanged(double)), this, SLOT(onLineWidthChanged(double)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:219: wasBlocked = this->lineWidthDoubleSpinBox->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:220: this->lineWidthDoubleSpinBox->setValue(this->PlotSeriesNode->GetLineWidth());`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:221: this->lineWidthDoubleSpinBox->setEnabled(this->PlotSeriesNode->GetPlotType() == vtkMRMLPlotSeriesNode::PlotTypeScatter //`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:223: this->lineWidthDoubleSpinBox->blockSignals(wasBlocked);`
- Connected slots/functions: `onLineWidthChanged`
- API footprints: `GetLineWidth`, `GetPlotType`, `SetLineWidth`, `vtkMRMLPlotSeriesNode::PlotTypeLine`, `vtkMRMLPlotSeriesNode::PlotTypeScatter`

## widget: plotSeriesColorPickerButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: plotSeriesColorPickerButton | ctkColorPickerButton
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
- Matched implementation lines:
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:74: this->connect(this->plotSeriesColorPickerButton, SIGNAL(colorChanged(const QColor&)), this, SLOT(onPlotSeriesColorChanged(const QColor&)));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:92: this->plotSeriesColorPickerButton->setColor(QColor(127, 127, 127));`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:226: wasBlocked = this->plotSeriesColorPickerButton->blockSignals(true);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:233: this->plotSeriesColorPickerButton->setColor(color);`
  - `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx:234: this->plotSeriesColorPickerButton->blockSignals(wasBlocked);`
- Connected slots/functions: `onPlotSeriesColorChanged`
- API footprints: `GetColor`, `GetOpacity`, `SetColor`, `SetOpacity`

## widget: labelsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Labels Column: | labelsLabel | QLabel
- Text: Labels Column:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: markerStyleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Markers Style: | markerStyleLabel | QLabel
- Text: Markers Style:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: markersSizeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Markers Size: | markersSizeLabel | QLabel
- Text: Markers Size:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: lineStyleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Line Style: | lineStyleLabel | QLabel
- Text: Line Style:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: lineWidthLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Line Width: | lineWidthLabel | QLabel
- Text: Line Width:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`

## widget: plotSeriesColorLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color: | plotSeriesColorLabel | QLabel
- Text: Color:
- Implementation candidates: `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.cxx`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget.h`, `Modules/Loadable/Plots/Widgets/qMRMLPlotSeriesPropertiesWidget_p.h`
