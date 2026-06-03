# Slicer UI Analysis: Modules/Loadable/Colors/Resources/UI/qSlicerColorsModuleWidget.ui

- Owner class: `qSlicerColorsModuleWidget`
- UI file: `Modules/Loadable/Colors/Resources/UI/qSlicerColorsModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerColorsModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerColorsModuleWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:31: #include "qSlicerColorsModuleWidget.h"`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:32: #include "ui_qSlicerColorsModuleWidget.h"`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:74: class qSlicerColorsModuleWidgetPrivate : public Ui_qSlicerColorsModuleWidget`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:76: Q_DECLARE_PUBLIC(qSlicerColorsModuleWidget);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:79: qSlicerColorsModuleWidget* const q_ptr;`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:82: qSlicerColorsModuleWidgetPrivate(qSlicerColorsModuleWidget& obj);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:83: virtual ~qSlicerColorsModuleWidgetPrivate();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:92: qSlicerColorsModuleWidgetPrivate::qSlicerColorsModuleWidgetPrivate(qSlicerColorsModuleWidget& object)`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:98: qSlicerColorsModuleWidgetPrivate::~qSlicerColorsModuleWidgetPrivate() {}`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:101: vtkSlicerColorLogic* qSlicerColorsModuleWidgetPrivate::colorLogic() const`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:103: Q_Q(const qSlicerColorsModuleWidget);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:108: void qSlicerColorsModuleWidgetPrivate::setDefaultColorNode()`
- API footprints: `GetScene`, `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLColorTableNode::SafeDownCast`, `vtkMRMLDisplayableNode::DisplayModifiedEvent`, `vtkMRMLDisplayableNode::SafeDownCast`

## widget: ColorLegendCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Color legend | ColorLegendCollapsibleButton | ctkCollapsibleButton
- Text: Color legend
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: DisplayableNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: DisplayableNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:159: connect(d->DisplayableNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onDisplayableNodeChanged(vtkMRMLNode*)));`
- Connected slots/functions: `onDisplayableNodeChanged`
- API footprints: `vtkMRMLDisplayableNode::DisplayModifiedEvent`, `vtkMRMLDisplayableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLScalarVolumeNode", "vtkMRMLModelNode"]}

## widget: DisplayableNodeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Displayable node: | DisplayableNodeLabel | QLabel
- Text: Displayable node:
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: ColorLegendDisplayNodeWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLColorLegendDisplayNodeWidget`
- Search text: ColorLegendDisplayNodeWidget | qMRMLColorLegendDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:43: #include "qMRMLColorLegendDisplayNodeWidget.h"`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:472: // d->ColorLegendDisplayNodeWidget->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:473: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(d->ColorLegendNode);`

## widget: CreateColorLegendButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Create | Create color legend for the selected displayable node. | CreateColorLegendButton | QPushButton
- Text: Create
- Tooltip: Create color legend for the selected displayable node.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:161: connect(d->CreateColorLegendButton, SIGNAL(clicked()), this, SLOT(createColorLegend()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:469: d->CreateColorLegendButton->setVisible(displayNode && !d->ColorLegendNode);`
- Connected slots/functions: `createColorLegend`
- API footprints: `GetColorNode`, `GetDisplayNode`

## widget: UseCurrentColorsButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Use current colors | Use the currently selected colors for the selected displayable node. | UseCurrentColorsButton | QPushButton
- Text: Use current colors
- Tooltip: Use the currently selected colors for the selected displayable node.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:163: connect(d->UseCurrentColorsButton, SIGNAL(clicked()), this, SLOT(useCurrentColorsForColorLegend()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:470: d->UseCurrentColorsButton->setVisible(displayNode && d->ColorLegendNode);`
- Connected slots/functions: `useCurrentColorsForColorLegend`
- API footprints: `GetDisplayNode`, `GetID`, `SetAndObserveColorNodeID`, `vtkMRMLColorNode::SafeDownCast`

## widget: DeleteColorLegendButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Delete | Delete the color legend for the selected displayable node. | DeleteColorLegendButton | QPushButton
- Text: Delete
- Tooltip: Delete the color legend for the selected displayable node.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:162: connect(d->DeleteColorLegendButton, SIGNAL(clicked()), this, SLOT(deleteColorLegend()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:471: d->DeleteColorLegendButton->setEnabled(d->ColorLegendNode);`
- Connected slots/functions: `deleteColorLegend`
- API footprints: `GetScene`, `RemoveNode`

## widget: DisplayableNodeLabel_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Color legend: | DisplayableNodeLabel_2 | QLabel
- Text: Color legend:
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: frame

- Confidence: `ui_only`
- Widget/action class: `QFrame`
- Search text: frame | QFrame
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: ColorTableLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Colors: | ColorTableLabel | QLabel
- Text: Colors:
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: ColorTableComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLColorTableComboBox`
- Search text: ColorTableComboBox | qMRMLColorTableComboBox
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:112: !this->ColorTableComboBox || //`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:113: this->ColorTableComboBox->currentNode() != nullptr)`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:119: this->ColorTableComboBox->setCurrentNode(defaultNode);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:145: connect(d->ColorTableComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this, SLOT(onMRMLColorNodeChanged(vtkMRMLNode*)));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:181: d->ColorTableComboBox->setCurrentNode(colorNode);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:298: vtkMRMLColorTableNode* colorTableNode = vtkMRMLColorTableNode::SafeDownCast(d->ColorTableComboBox->currentNode());`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:314: vtkMRMLNode* currentNode = d->ColorTableComboBox->currentNode();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:331: vtkMRMLColorNode* currentNode = vtkMRMLColorNode::SafeDownCast(d->ColorTableComboBox->currentNode());`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:363: d->ColorTableComboBox->setCurrentNode(colorNode);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:405: d->ColorTableComboBox->setCurrentNode(newColorTableNode);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:412: vtkMRMLColorTableNode* currentNode = vtkMRMLColorTableNode::SafeDownCast(d->ColorTableComboBox->currentNode());`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:435: vtkMRMLColorTableNode* currentNode = vtkMRMLColorTableNode::SafeDownCast(d->ColorTableComboBox->currentNode());`
- Connected slots/functions: `onMRMLColorNodeChanged`
- API footprints: `GetColorName`, `GetColorTransferFunction`, `GetDefaultLabelMapColorNodeID`, `GetID`, `GetLookupTable`, `GetNodeByID`, `GetNumberOfColors`, `GetRange`, `GetType`, `SetNumberOfValues`, `SetValue`, `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLColorNode::User`, `vtkMRMLColorTableNode::SafeDownCast`, `vtkMRMLColorTableNode::User`, `vtkMRMLProceduralColorNode::SafeDownCast`

## widget: CopyColorNodeButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Duplicate the current color node to allow editing colors, scalar range, size. | CopyColorNodeButton | QToolButton
- Tooltip: Duplicate the current color node to allow editing colors, scalar range, size.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:140: d->CopyColorNodeButton->setIcon(QIcon(":Icons/SlicerCopyColor.png"));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:150: connect(d->CopyColorNodeButton, SIGNAL(clicked()), this, SLOT(copyCurrentColorNode()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:198: d->CopyColorNodeButton->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:203: d->CopyColorNodeButton->setEnabled(true);`
- Connected slots/functions: `copyCurrentColorNode`
- API footprints: `AddNode`, `CopyNode`, `CopyProceduralNode`, `Delete`, `GetClassName`, `GetID`, `GetName`, `IsA`, `vtkMRMLColorNode::SafeDownCast`, `vtkMRMLColorTableNode::SafeDownCast`

## widget: AddColorTableNodeButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Add new empty color table node. | AddColorTableNodeButton | QToolButton
- Tooltip: Add new empty color table node.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:141: d->AddColorTableNodeButton->setIcon(QIcon(":Icons/SlicerNewColor.png"));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:151: connect(d->AddColorTableNodeButton, SIGNAL(clicked()), this, SLOT(addNewColorTableNode()));`
- Connected slots/functions: `addNewColorTableNode`
- API footprints: `AddNode`, `CreateNodeByClass`, `GenerateUniqueName`, `SetHideFromEditors`, `SetName`, `SetTypeToUser`, `vtkMRMLColorTableNode::SafeDownCast`

## widget: EditColorsCollapsibleButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Color table | EditColorsCollapsibleButton | ctkCollapsibleButton
- Text: Color table
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:215: d->EditColorsCollapsibleButton->setText(tr("Discrete table"));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:275: d->EditColorsCollapsibleButton->setText(tr("Continuous scale"));`
- API footprints: `GetType`, `vtkMRMLColorTableNode::User`
- Key UI properties: {"checked": "true"}

## widget: ContinuousScalarsToColorsWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkVTKScalarsToColorsWidget`
- Search text: ContinuousScalarsToColorsWidget | ctkVTKScalarsToColorsWidget
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:156: d->ContinuousScalarsToColorsWidget->view()->setValidBounds(validBounds);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:157: d->ContinuousScalarsToColorsWidget->view()->addColorTransferFunction(nullptr);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:199: d->ContinuousScalarsToColorsWidget->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:213: d->ContinuousScalarsToColorsWidget->hide();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:274: d->ContinuousScalarsToColorsWidget->show();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:279: d->ContinuousScalarsToColorsWidget->view()->setColorTransferFunctionToPlots(procColorNode->GetColorTransferFunction(), editable);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:280: d->ContinuousScalarsToColorsWidget->setEnabled(editable);`
- API footprints: `GetColorTransferFunction`, `GetType`, `vtkMRMLColorNode::User`

## widget: ColorTableFrame

- Confidence: `linked_to_code`
- Widget/action class: `QFrame`
- Search text: ColorTableFrame | QFrame
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:214: d->ColorTableFrame->show();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:273: d->ColorTableFrame->hide();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:438: if (d->ColorTableFrame->isVisible())`

## widget: NumberOfColorsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Number of colors:  | NumberOfColorsLabel | QLabel
- Text: Number of colors: 
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: HideInvalidColorsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Hide empty colors:  | HideInvalidColorsLabel | QLabel
- Text: Hide empty colors: 
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: HideInvalidColorsCheckBox

- Confidence: `ui_only`
- Widget/action class: `QCheckBox`
- Search text: Show/Hide the unnamed color entries in the list below. | HideInvalidColorsCheckBox | QCheckBox
- Tooltip: Show/Hide the unnamed color entries in the list below.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Key UI properties: {"checked": "true"}

## widget: LUTRangeLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scalar Range: | LUTRangeLabel | QLabel
- Text: Scalar Range:
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`

## widget: LUTRangeWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLRangeWidget`
- Search text: The range of scalars that are mapped to the full range of colors. | LUTRangeWidget | qMRMLRangeWidget
- Tooltip: The range of scalars that are mapped to the full range of colors.
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:149: connect(d->LUTRangeWidget, SIGNAL(valuesChanged(double, double)), this, SLOT(setLookupTableRange(double, double)));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:196: d->LUTRangeWidget->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:197: d->LUTRangeWidget->setValues(0., 0.);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:229: d->LUTRangeWidget->setEnabled(editable);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:234: disconnect(d->LUTRangeWidget, SIGNAL(valuesChanged(double, double)), this, SLOT(setLookupTableRange(double, double)));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:244: d->LUTRangeWidget->setRange(range[0] - rangeMargin, range[1] + rangeMargin);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:245: d->LUTRangeWidget->setValues(range[0], range[1]);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:249: d->LUTRangeWidget->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:250: d->LUTRangeWidget->setValues(0., 0.);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:252: connect(d->LUTRangeWidget, SIGNAL(valuesChanged(double, double)), this, SLOT(setLookupTableRange(double, double)));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:271: d->LUTRangeWidget->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:272: d->LUTRangeWidget->setValues(0., 0.);`
- Connected slots/functions: `setLookupTableRange`
- API footprints: `GetLookupTable`, `GetRange`, `SetRange`, `vtkMRMLColorNode::SafeDownCast`

## widget: ColorView

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLColorTableView`
- Search text: ColorView | qMRMLColorTableView
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:440: QModelIndex colorModelIndex = d->ColorView->sortFilterProxyModel()->mapToSource(d->ColorView->currentIndex());`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:441: colorIndex = d->ColorView->colorModel()->colorFromIndex(colorModelIndex);`

## widget: NumberOfColorsSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: NumberOfColorsSpinBox | QSpinBox
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:148: connect(d->NumberOfColorsSpinBox, SIGNAL(editingFinished()), this, SLOT(updateNumberOfColors()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:194: d->NumberOfColorsSpinBox->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:195: d->NumberOfColorsSpinBox->setValue(0);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:220: d->NumberOfColorsSpinBox->setEnabled(editable);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:221: d->NumberOfColorsSpinBox->setValue(colorNode->GetNumberOfColors());`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:222: Q_ASSERT(d->NumberOfColorsSpinBox->value() == colorNode->GetNumberOfColors());`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:269: d->NumberOfColorsSpinBox->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:270: d->NumberOfColorsSpinBox->setValue(0);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:293: if (!d->NumberOfColorsSpinBox->isEnabled())`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:297: int newNumber = d->NumberOfColorsSpinBox->value();`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:427: QSignalBlocker blocker(d->NumberOfColorsSpinBox);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:428: d->NumberOfColorsSpinBox->setValue(newNumber);`
- Connected slots/functions: `updateNumberOfColors`
- API footprints: `GetNumberOfColors`, `SetColor`, `SetNumberOfColors`, `vtkMRMLColorTableNode::SafeDownCast`

## widget: AddNewColorButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Add new color to color table | AddNewColorButton | QToolButton
- Tooltip: Add new color to color table
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:142: d->AddNewColorButton->setIcon(QIcon(":Icons/Add.png"));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:152: connect(d->AddNewColorButton, SIGNAL(clicked()), this, SLOT(addNewColorInCurrentNode()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:192: d->AddNewColorButton->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:224: d->AddNewColorButton->setEnabled(editable);`
- Connected slots/functions: `addNewColorInCurrentNode`
- API footprints: `GetNumberOfColors`, `SetColor`, `SetNumberOfColors`, `vtkMRMLColorTableNode::SafeDownCast`

## widget: RemoveCurrentColorButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Delete currently selected color | RemoveCurrentColorButton | QToolButton
- Tooltip: Delete currently selected color
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:143: d->RemoveCurrentColorButton->setIcon(QIcon(":Icons/Remove.png"));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:153: connect(d->RemoveCurrentColorButton, SIGNAL(clicked()), this, SLOT(removeCurrentColorEntry()));`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:193: d->RemoveCurrentColorButton->setEnabled(false);`
  - `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx:225: d->RemoveCurrentColorButton->setEnabled(editable);`
- Connected slots/functions: `removeCurrentColorEntry`
- API footprints: `RemoveColor`, `vtkMRMLColorTableNode::SafeDownCast`

## widget: DynamicSpacer

- Confidence: `ui_only`
- Widget/action class: `ctkDynamicSpacer`
- Search text: DynamicSpacer | ctkDynamicSpacer
- Implementation candidates: `Modules/Loadable/Colors/qSlicerColorsModuleWidget.cxx`, `Modules/Loadable/Colors/qSlicerColorsModuleWidget.h`
