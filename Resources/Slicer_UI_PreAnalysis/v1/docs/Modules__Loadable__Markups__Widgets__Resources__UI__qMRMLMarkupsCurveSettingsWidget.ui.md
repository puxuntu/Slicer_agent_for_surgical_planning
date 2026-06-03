# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsCurveSettingsWidget.ui

- Owner class: `qMRMLMarkupsCurveSettingsWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qMRMLMarkupsCurveSettingsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLMarkupsCurveSettingsWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLMarkupsCurveSettingsWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:21: #include "qMRMLMarkupsCurveSettingsWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:22: #include "ui_qMRMLMarkupsCurveSettingsWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:39: class qMRMLMarkupsCurveSettingsWidget;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:42: class qMRMLMarkupsCurveSettingsWidgetPrivate : public Ui_qMRMLMarkupsCurveSettingsWidget`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:45: qMRMLMarkupsCurveSettingsWidgetPrivate(qMRMLMarkupsCurveSettingsWidget& widget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:52: virtual void setupUi(qMRMLMarkupsCurveSettingsWidget*);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:57: qMRMLMarkupsCurveSettingsWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:60: Q_DECLARE_PUBLIC(qMRMLMarkupsCurveSettingsWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:64: qMRMLMarkupsCurveSettingsWidgetPrivate::qMRMLMarkupsCurveSettingsWidgetPrivate(qMRMLMarkupsCurveSettingsWidget& widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:71: void qMRMLMarkupsCurveSettingsWidgetPrivate::setupUi(qMRMLMarkupsCurveSettingsWidget* widget)`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:73: Q_Q(qMRMLMarkupsCurveSettingsWidget);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:75: this->Ui_qMRMLMarkupsCurveSettingsWidget::setupUi(widget);`
- API footprints: `vtkMRMLMarkupsCurveNode::SafeDownCast`

## widget: curveSettingsCollapseButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Curve Settings | curveSettingsCollapseButton | ctkCollapsibleButton
- Text: Curve Settings
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: curveSettingsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: curveSettingsWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: label_7

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Curve Type: | label_7 | QLabel
- Text: Curve Type:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: curveTypeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: curveTypeComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:77: this->curveTypeComboBox->clear();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:80: this->curveTypeComboBox->addItem(qMRMLMarkupsCurveSettingsWidgetPrivate::curveTypeAsDisplayableString(curveType), curveType);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:94: QObject::connect(this->curveTypeComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onCurveTypeParameterChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:211: bool wasBlocked = d->curveTypeComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:212: d->curveTypeComboBox->setCurrentIndex(d->curveTypeComboBox->findData(curveNode->GetCurveType()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:213: d->curveTypeComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:284: curveNode->SetCurveType(d->curveTypeComboBox->currentData().toInt());`
- Connected slots/functions: `onCurveTypeParameterChanged`
- API footprints: `GetCurveType`, `GetSurfaceConstraintNode`, `SetAndObserveSurfaceConstraintNode`, `SetCurveType`, `SetSurfaceCostFunctionType`, `SetSurfaceDistanceWeightingFunction`, `vtkMRMLMarkupsCurveNode::SafeDownCast`, `vtkMRMLModelNode::SafeDownCast`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Constrain to Model: | label_4 | QLabel
- Text: Constrain to Model:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: modelNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: modelNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:95: QObject::connect(this->modelNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(onCurveTypeParameterChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:216: wasBlocked = d->modelNodeSelector->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:217: d->modelNodeSelector->setCurrentNode(modelNode);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:218: d->modelNodeSelector->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:285: curveNode->SetAndObserveSurfaceConstraintNode(vtkMRMLModelNode::SafeDownCast(d->modelNodeSelector->currentNode()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:376: d->modelNodeSelector->setMRMLScene(mrmlScene);`
- Connected slots/functions: `onCurveTypeParameterChanged`
- API footprints: `GetSurfaceConstraintNode`, `SetAndObserveSurfaceConstraintNode`, `SetCurveType`, `SetSurfaceCostFunctionType`, `SetSurfaceDistanceWeightingFunction`, `vtkMRMLMarkupsCurveNode::SafeDownCast`, `vtkMRMLModelNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLModelNode"]}

## widget: surfaceCurveCollapsibleButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: surfaceCurveCollapsibleButton | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:264: d->surfaceCurveCollapsibleButton->setEnabled(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:268: d->surfaceCurveCollapsibleButton->setEnabled(false);`
- API footprints: `GetCurveType`

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Cost function: | label_5 | QLabel
- Text: Cost function:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: label_6

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Distance weighting function: | label_6 | QLabel
- Text: Distance weighting function:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: scalarFunctionWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: scalarFunctionWidget | QWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: scalarFunctionPrefixLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: distance / ( | scalarFunctionPrefixLabel | QLabel
- Text: distance / (
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:259: d->scalarFunctionPrefixLabel->setText(prefixString);`

## widget: scalarFunctionLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: activeScalar | <html><head/><body><p align="justify">Function used to calculate scalar weights for pathfinding. The currently active point scalar can be accessed using the &quot;activeScalar&quot; variable name. All other scalars can be accessed as variables provided that they don't contain any illegal characters (&quot;./* etc.).</p><p>Example functions: &quot;activeScalar*activeScalar&quot;, &quot;exp(activeScalar)&quot;, &quot;1.0-activeScalar&quot;, &quot;scalarA*scalarB&quot;</p></body></html> | scalarFunctionLineEdit | QLineEdit
- Text: activeScalar
- Tooltip: <html><head/><body><p align="justify">Function used to calculate scalar weights for pathfinding. The currently active point scalar can be accessed using the &quot;activeScalar&quot; variable name. All other scalars can be accessed as variables provided that they don't contain any illegal characters (&quot;./* etc.).</p><p>Example functions: &quot;activeScalar*activeScalar&quot;, &quot;exp(activeScalar)&quot;, &quot;1.0-activeScalar&quot;, &quot;scalarA*scalarB&quot;</p></body></html>
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:97: QObject::connect(this->scalarFunctionLineEdit, SIGNAL(textChanged(QString)), this->editScalarFunctionDelay, SLOT(start()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:225: wasBlocked = d->scalarFunctionLineEdit->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:226: int currentCursorPosition = d->scalarFunctionLineEdit->cursorPosition();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:227: d->scalarFunctionLineEdit->setText(curveNode->GetSurfaceDistanceWeightingFunction());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:228: d->scalarFunctionLineEdit->setCursorPosition(currentCursorPosition);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:229: d->scalarFunctionLineEdit->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:237: d->scalarFunctionLineEdit->setVisible(false);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:241: d->scalarFunctionLineEdit->setVisible(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:286: std::string functionString = d->scalarFunctionLineEdit->text().toStdString();`
- Connected slots/functions: `start`
- API footprints: `GetSurfaceDistanceWeightingFunction`, `SetAndObserveSurfaceConstraintNode`, `SetCurveType`, `SetSurfaceCostFunctionType`, `SetSurfaceDistanceWeightingFunction`, `vtkMRMLModelNode::SafeDownCast`

## widget: scalarFunctionSuffixLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: )^2 | scalarFunctionSuffixLabel | QLabel
- Text: )^2
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:260: d->scalarFunctionSuffixLabel->setText(suffixString);`
- API footprints: `GetCurveType`

## widget: costFunctionComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: costFunctionComboBox | QComboBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:83: this->costFunctionComboBox->clear();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:86: this->costFunctionComboBox->addItem(qMRMLMarkupsCurveSettingsWidgetPrivate::costFunctionAsDisplayableString(costFunction), costFunction);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:96: QObject::connect(this->costFunctionComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onCurveTypeParameterChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:220: wasBlocked = d->costFunctionComboBox->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:222: d->costFunctionComboBox->setCurrentIndex(d->costFunctionComboBox->findData(costFunction));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:223: d->costFunctionComboBox->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:287: curveNode->SetSurfaceCostFunctionType(d->costFunctionComboBox->currentData().toInt());`
- Connected slots/functions: `onCurveTypeParameterChanged`
- API footprints: `GetSurfaceCostFunctionType`, `SetAndObserveSurfaceConstraintNode`, `SetCurveType`, `SetSurfaceCostFunctionType`, `SetSurfaceDistanceWeightingFunction`, `vtkMRMLMarkupsCurveNode::SafeDownCast`, `vtkMRMLModelNode::SafeDownCast`

## widget: CurveSettingsAdvancedOptionCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CurveSettingsAdvancedOptionCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Key UI properties: {"checked": "false"}

## widget: projectCurveMaxSearchRadiusLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Maximum projection distance: | projectCurveMaxSearchRadiusLabel | QLabel
- Text: Maximum projection distance:
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: projectCurveMaxSearchRadiusSliderWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkSliderWidget`
- Search text: Select the maximum projection distance as percentage of bounding box size. | projectCurveMaxSearchRadiusSliderWidget | ctkSliderWidget
- Tooltip: Select the maximum projection distance as percentage of bounding box size.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:98: QObject::connect(this->projectCurveMaxSearchRadiusSliderWidget, SIGNAL(valueChanged(double)), q, SLOT(onProjectCurveMaximumSearchRadiusChanged()));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:231: wasBlocked = d->projectCurveMaxSearchRadiusSliderWidget->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:232: d->projectCurveMaxSearchRadiusSliderWidget->setValue(curveNode->GetSurfaceConstraintMaximumSearchRadiusTolerance() * 100.);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:233: d->projectCurveMaxSearchRadiusSliderWidget->blockSignals(wasBlocked);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:342: const double maximumSearchRadius = 0.01 * d->projectCurveMaxSearchRadiusSliderWidget->value();`
- Connected slots/functions: `onProjectCurveMaximumSearchRadiusChanged`
- API footprints: `GetSurfaceConstraintMaximumSearchRadiusTolerance`, `SetSurfaceConstraintMaximumSearchRadiusTolerance`, `vtkMRMLMarkupsCurveNode::SafeDownCast`

## widget: resampleCurveCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Resample | Resample a curve with the number of points specified. | resampleCurveCollapsibleButton | ctkCollapsibleButton
- Text: Resample
- Tooltip: Resample a curve with the number of points specified.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: resampleCurveOutputNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Output node:  | resampleCurveOutputNodeLabel | QLabel
- Text: Output node: 
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: resampleCurveNumerOfOutputPointsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of resampled points:  | Select the number of points on the resampled curve.  | resampleCurveNumerOfOutputPointsLabel | QLabel
- Text: Number of resampled points: 
- Tooltip: Select the number of points on the resampled curve. 
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`

## widget: resampleCurveNumerOfOutputPointsSpinBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkDoubleSpinBox`
- Search text: The active curve will be resamples with the number of points specified. | resampleCurveNumerOfOutputPointsSpinBox | ctkDoubleSpinBox
- Tooltip: The active curve will be resamples with the number of points specified.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:296: double resampleNumberOfPoints = d->resampleCurveNumerOfOutputPointsSpinBox->value();`

## widget: resampleCurveOutputNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select a node to store the resampled curve  | resampleCurveOutputNodeSelector | qMRMLNodeComboBox
- Tooltip: Select a node to store the resampled curve 
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:200: vtkMRMLNode* previousOutputNode = d->resampleCurveOutputNodeSelector->currentNode();`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:201: d->resampleCurveOutputNodeSelector->setNodeTypes(QStringList(QString(curveNode->GetClassName())));`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:204: d->resampleCurveOutputNodeSelector->setCurrentNode(previousOutputNode);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:208: d->resampleCurveOutputNodeSelector->setCurrentNode(nullptr);`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:308: vtkMRMLMarkupsCurveNode* outputNode = vtkMRMLMarkupsCurveNode::SafeDownCast(d->resampleCurveOutputNodeSelector->currentNode());`
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:377: d->resampleCurveOutputNodeSelector->setMRMLScene(mrmlScene);`
- API footprints: `GetClassName`, `GetCurveClosed`, `IsA`, `vtkMRMLMarkupsCurveNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLMarkupsCurveNode"]}

## widget: resampleCurveButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Resample curve | Resamples the active curve with the number of points specified. | resampleCurveButton | QPushButton
- Text: Resample curve
- Tooltip: Resamples the active curve with the number of points specified.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx`, `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qMRMLMarkupsCurveSettingsWidget.cxx:99: QObject::connect(this->resampleCurveButton, SIGNAL(clicked()), q, SLOT(onApplyCurveResamplingPushButtonClicked()));`
- Connected slots/functions: `onApplyCurveResamplingPushButtonClicked`
- API footprints: `GetControlPointLabels`, `GetControlPointPositionsWorld`, `GetCurveClosed`, `GetCurveLengthWorld`, `GetCurveType`, `GetNumberOfPointsPerInterpolatingSegment`, `GetSurfaceConstraintNode`, `GetSurfaceCostFunctionType`, `GetSurfaceDistanceWeightingFunction`, `ResampleCurveWorld`, `SetAndObserveSurfaceConstraintNode`, `SetControlPointLabels`, `SetControlPointPositionsWorld`, `SetCurveType`, `SetNumberOfPointsPerInterpolatingSegment`, `SetSurfaceCostFunctionType`, `SetSurfaceDistanceWeightingFunction`, `vtkMRMLMarkupsCurveNode::SafeDownCast`
