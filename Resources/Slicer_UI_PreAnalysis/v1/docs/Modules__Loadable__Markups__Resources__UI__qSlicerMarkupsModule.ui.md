# Slicer UI Analysis: Modules/Loadable/Markups/Resources/UI/qSlicerMarkupsModule.ui

- Owner class: `qSlicerMarkupsModule`
- UI file: `Modules/Loadable/Markups/Resources/UI/qSlicerMarkupsModule.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerMarkupsModule

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerMarkupsModule | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:46: #include "qSlicerMarkupsModule.h"`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:47: #include "qSlicerMarkupsModuleWidget.h"`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:81: class qSlicerMarkupsModulePrivate`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:84: Q_DECLARE_PUBLIC(qSlicerMarkupsModule);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:87: qSlicerMarkupsModule* const q_ptr;`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:90: qSlicerMarkupsModulePrivate(qSlicerMarkupsModule& object);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:95: virtual ~qSlicerMarkupsModulePrivate();`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:103: // qSlicerMarkupsModulePrivate methods`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:106: qSlicerMarkupsModulePrivate::qSlicerMarkupsModulePrivate(qSlicerMarkupsModule& object)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:116: qSlicerMarkupsModulePrivate::~qSlicerMarkupsModulePrivate()`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:135: void qSlicerMarkupsModulePrivate::addToolBar()`
  - `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx:137: Q_Q(qSlicerMarkupsModule);`
- Connected slots/functions: `mappedString`, `onCreateMarkupByClass`
- API footprints: `AddNewMarkupsNode`, `GetClassName`, `GetDefaultMarkupsDisplayNode`, `GetHideFromEditors`, `GetMarkupType`, `GetNthControlPointPosition`, `GetNthControlPointPositionStatus`, `GetPlaceAddIcon`, `GetTypeDisplayName`, `IsBatchProcessing`, `SetNthControlPointDescription`, `SetNthControlPointLabel`, `SetNthControlPointLocked`, `SetNthControlPointSelected`, `SetNthControlPointVisibility`, `vtkMRMLMarkupsNode::PositionDefined`, `vtkMRMLMarkupsNode::SafeDownCast`

## widget: createMarkupsGroupBox

- Confidence: `linked_to_code`
- Widget/action class: `QGroupBox`
- Search text: createMarkupsGroupBox | QGroupBox
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:773: if (createMarkupsGroupBox->layout())`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:776: tempWidget.setLayout(createMarkupsGroupBox->layout());`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:779: this->createMarkupsGroupBox->setLayout(layout);`

## widget: ResizableFrame

- Confidence: `ui_only`
- Widget/action class: `ctkExpandableWidget`
- Search text: ResizableFrame | ctkExpandableWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: activeMarkupTreeView

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLSubjectHierarchyTreeView`
- Search text: activeMarkupTreeView | qMRMLSubjectHierarchyTreeView
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:254: this->activeMarkupTreeView->setNodeTypes(registeredMarkups);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:255: this->activeMarkupTreeView->setColumnHidden(this->activeMarkupTreeView->model()->idColumn(), true);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:256: this->activeMarkupTreeView->setColumnHidden(this->activeMarkupTreeView->model()->transformColumn(), true);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:257: this->activeMarkupTreeView->setColumnHidden(this->activeMarkupTreeView->model()->descriptionColumn(), false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:376: QObject::connect(this->activeMarkupTreeView, SIGNAL(currentItemChanged(vtkIdType)), q, SLOT(onActiveMarkupItemChanged(vtkIdType)));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:599: vtkMRMLSubjectHierarchyNode* shNode = this->activeMarkupTreeView->subjectHierarchyNode();`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:616: QModelIndex itemIndex = this->activeMarkupTreeView->sortFilterProxyModel()->indexFromSubjectHierarchyItem(itemID);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:838: vtkMRMLSubjectHierarchyNode* shNode = d->activeMarkupTreeView->subjectHierarchyNode();`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:845: QModelIndex itemIndex = d->activeMarkupTreeView->sortFilterProxyModel()->indexFromSubjectHierarchyItem(itemID);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:848: d->activeMarkupTreeView->scrollTo(itemIndex);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:849: d->activeMarkupTreeView->setCurrentNode(markupsNode);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:898: bool wasBlocked = d->activeMarkupTreeView->blockSignals(true);`
- Connected slots/functions: `onActiveMarkupItemChanged`
- API footprints: `GetItemByDataNode`, `vtkMRMLMarkupsNode::SafeDownCast`

## widget: displayCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLCollapsibleButton`
- Search text: Display | displayCollapsibleButton | qMRMLCollapsibleButton
- Text: Display
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1858: d->displayCollapsibleButton->setEnabled(enable);`

## widget: markupsDisplayWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLMarkupsDisplayNodeWidget`
- Search text: markupsDisplayWidget | qMRMLMarkupsDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:912: d->markupsDisplayWidget->setMRMLMarkupsNode(d->MarkupsNode);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:916: vtkMRMLDisplayNode* displayNode = d->markupsDisplayWidget->mrmlMarkupsDisplayNode();`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1022: d->markupsDisplayWidget->setMaximumMarkupsScale(maxScale);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1831: vtkMRMLDisplayNode* displayNode = d->markupsDisplayWidget->mrmlMarkupsDisplayNode();`

## widget: ColorLegendCollapsibleGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: Color legend for the Color Table selected in Scalars section. | ColorLegendCollapsibleGroupBox | ctkCollapsibleGroupBox
- Tooltip: Color legend for the Color Table selected in Scalars section.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:509: QObject::connect(this->ColorLegendCollapsibleGroupBox, SIGNAL(toggled(bool)), q, SLOT(onColorLegendCollapsibleGroupBoxToggled(bool)));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:920: d->ColorLegendCollapsibleGroupBox->setCollapsed(!colorLegendNode);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:921: d->ColorLegendCollapsibleGroupBox->setEnabled(displayNode && displayNode->GetColorNode());`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1821: void qSlicerMarkupsModuleWidget::onColorLegendCollapsibleGroupBoxToggled(bool toggled)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h:262: void onColorLegendCollapsibleGroupBoxToggled(bool);`
- Connected slots/functions: `onColorLegendCollapsibleGroupBoxToggled`
- API footprints: `GetColorNode`, `GetMRMLApplicationLogic`, `PauseRender`, `ResumeRender`, `SetVisibility`

## widget: ColorLegendDisplayNodeWidget

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLColorLegendDisplayNodeWidget`
- Search text: ColorLegendDisplayNodeWidget | qMRMLColorLegendDisplayNodeWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:918: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(colorLegendNode);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1850: d->ColorLegendDisplayNodeWidget->setMRMLColorLegendDisplayNode(colorLegendNode);`

## widget: saveToDefaultDisplayPropertiesPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Save to Defaults | Save current display properties to defaults. These properties will be used even after application restart. | saveToDefaultDisplayPropertiesPushButton | QPushButton
- Text: Save to Defaults
- Tooltip: Save current display properties to defaults. These properties will be used even after application restart.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:479: QObject::connect(this->saveToDefaultDisplayPropertiesPushButton, SIGNAL(clicked()), q, SLOT(onSaveToDefaultDisplayPropertiesPushButtonClicked()));`
- Connected slots/functions: `onSaveToDefaultDisplayPropertiesPushButtonClicked`
- API footprints: `GetDefaultMarkupsDisplayNode`, `SetDisplayDefaultsFromNode`

## widget: resetToDefaultDisplayPropertiesPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Reset to Defaults | Use default display properties. | resetToDefaultDisplayPropertiesPushButton | QPushButton
- Text: Reset to Defaults
- Tooltip: Use default display properties.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:478: QObject::connect(this->resetToDefaultDisplayPropertiesPushButton, SIGNAL(clicked()), q, SLOT(onResetToDefaultDisplayPropertiesPushButtonClicked()));`
- Connected slots/functions: `onResetToDefaultDisplayPropertiesPushButtonClicked`
- API footprints: `SetDisplayNodeToDefaults`

## widget: controlPointsCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Control Points | controlPointsCollapsibleButton | ctkCollapsibleButton
- Text: Control Points
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:259: // We need to disable the controlPointsCollapsibleButton here because doing so in the .ui file would lead to`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:261: this->controlPointsCollapsibleButton->setEnabled(false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1859: d->controlPointsCollapsibleButton->setEnabled(enable);`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Interaction:  | label_3 | QLabel
- Text: Interaction: 
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: listLockedUnlockedPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Enable/disable all interactions in slice and 3D views. | listLockedUnlockedPushButton | QPushButton
- Tooltip: Enable/disable all interactions in slice and 3D views.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:390: QObject::connect(this->listLockedUnlockedPushButton, SIGNAL(clicked()), q, SLOT(onListLockedUnlockedPushButtonClicked()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:932: d->listLockedUnlockedPushButton->setIcon(QIcon(":Icons/Medium/SlicerLock.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:933: d->listLockedUnlockedPushButton->setToolTip(tr("Click to unlock this control point list so points can be moved by the mouse"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:937: d->listLockedUnlockedPushButton->setIcon(QIcon(":Icons/Medium/SlicerUnlock.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:938: d->listLockedUnlockedPushButton->setToolTip(tr("Click to lock this control point list so points cannot be moved by the mouse"));`
- Connected slots/functions: `onListLockedUnlockedPushButtonClicked`
- API footprints: `GetLocked`, `SetLocked`

## widget: fixedNumberOfControlPointsPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Lock the number of points allowed in the active markup. | fixedNumberOfControlPointsPushButton | QPushButton
- Tooltip: Lock the number of points allowed in the active markup.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:395: QObject::connect(this->fixedNumberOfControlPointsPushButton, SIGNAL(clicked()), q, SLOT(onFixedNumberOfControlPointsPushButtonClicked()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:943: d->fixedNumberOfControlPointsPushButton->setIcon(QIcon(":Icons/Medium/SlicerPointNumberLock.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:944: d->fixedNumberOfControlPointsPushButton->setToolTip(tr("Click to unlock the number of control points so points can be added or deleted"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:950: d->fixedNumberOfControlPointsPushButton->setIcon(QIcon(":Icons/Medium/SlicerPointNumberUnlock.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:951: d->fixedNumberOfControlPointsPushButton->setToolTip(tr("Click to lock the number of control points so no points can be added or deleted"));`
- Connected slots/functions: `onFixedNumberOfControlPointsPushButtonClicked`
- API footprints: `GetFixedNumberOfControlPoints`, `SetFixedNumberOfControlPoints`

## widget: label

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Jump Slices: | label | QLabel
- Text: Jump Slices:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:115: /// the number of columns matches the column labels by using the size of the QStringList`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1146: QString label = QString::fromStdString(markupsNode->GetNthControlPointLabel(controlPointIndex));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1147: if (isNewItem || item->text() != label)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1149: item->setText(label);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1545: QString labelText = QString(tr("Delete %1 control points from this list?").arg(rows.size()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1548: deleteAllMsgBox.setText(labelText);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1752: QString labelText = QString(tr("Delete all %1 control points from this list?").arg(d->MarkupsNode->GetNumberOfControlPoints()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1756: deleteAllMsgBox.setText(labelText);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2307: // label this selected markup if more than one`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2311: // if there's a label use it`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2765: // update the transform check box label`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3023: // Update measurements description label`
- API footprints: `GetNthControlPointLabel`, `GetNumberOfControlPoints`

## widget: jumpModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Offset: set slice plane position. Centered: set slice plane position and center the slice view on the control point. | jumpModeComboBox | QComboBox
- Tooltip: Offset: set slice plane position. Centered: set slice plane position and center the slice view on the control point.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2193: if ((d->jumpModeComboBox->currentIndex() == JUMP_MODE_COMBOBOX_INDEX_IGNORE))`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2199: bool jumpCentered = (d->jumpModeComboBox->currentIndex() == JUMP_MODE_COMBOBOX_INDEX_CENTERED);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2388: if (d->jumpModeComboBox->currentIndex() == JUMP_MODE_COMBOBOX_INDEX_CENTERED)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2678: if (d->jumpModeComboBox->currentIndex() != JUMP_MODE_COMBOBOX_INDEX_IGNORE)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2719: if (d->jumpModeComboBox->currentIndex() == JUMP_MODE_COMBOBOX_INDEX_IGNORE)`
- API footprints: `GetID`, `JumpSlicesToNthPointInMarkup`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show Slice Intersections: | label_2 | QLabel
- Text: Show Slice Intersections:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: sliceIntersectionsVisibilityCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCheckBox`
- Search text: Show how the other slice planes intersect each slice plane. | sliceIntersectionsVisibilityCheckBox | ctkCheckBox
- Tooltip: Show how the other slice planes intersect each slice plane.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:384: this->sliceIntersectionsVisibilityCheckBox->setChecked(false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:385: QObject::connect(this->sliceIntersectionsVisibilityCheckBox, SIGNAL(toggled(bool)), q, SLOT(onSliceIntersectionsVisibilityToggled(bool)));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:956: d->sliceIntersectionsVisibilityCheckBox->setChecked(this->sliceIntersectionsVisible());`
- Connected slots/functions: `onSliceIntersectionsVisibilityToggled`
- API footprints: `SetIntersectingSlicesEnabled`, `vtkMRMLApplicationLogic::GetIntersectingSlicesEnabled`, `vtkMRMLApplicationLogic::IntersectingSlicesVisibility`

## widget: visibilityAllControlPointsInListMenuButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkMenuButton`
- Search text: Toggle visibility flag on all control points in the list. Use the drop down menu to set all to visible or invisible. | visibilityAllControlPointsInListMenuButton | ctkMenuButton
- Tooltip: Toggle visibility flag on all control points in the list. Use the drop down menu to set all to visible or invisible.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:266: visibilityMenu = new QMenu(qSlicerMarkupsModuleWidget::tr("Visibility"), this->visibilityAllControlPointsInListMenuButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:281: this->visibilityAllControlPointsInListMenuButton->setMenu(this->visibilityMenu);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:282: this->visibilityAllControlPointsInListMenuButton->setIcon(QIcon(":/Icons/VisibleOrInvisible.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:285: QObject::connect(this->visibilityAllControlPointsInListMenuButton, SIGNAL(clicked()), q, SLOT(onVisibilityAllControlPointsInListToggled()));`
- Connected slots/functions: `onVisibilityAllControlPointsInListToggled`
- API footprints: `ToggleAllControlPointsVisibility`

## widget: selectedAllControlPointsInListMenuButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkMenuButton`
- Search text: Toggle selected flag on all control points in the list. Use the drop down menu to set all to selected or deselected. | selectedAllControlPointsInListMenuButton | ctkMenuButton
- Tooltip: Toggle selected flag on all control points in the list. Use the drop down menu to set all to selected or deselected.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:312: selectedMenu = new QMenu(qSlicerMarkupsModuleWidget::tr("Selected"), this->selectedAllControlPointsInListMenuButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:327: this->selectedAllControlPointsInListMenuButton->setMenu(this->selectedMenu);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:328: this->selectedAllControlPointsInListMenuButton->setIcon(QIcon(":/Icons/MarkupsSelectedOrUnselected.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:331: QObject::connect(this->selectedAllControlPointsInListMenuButton, SIGNAL(clicked()), q, SLOT(onSelectedAllControlPointsInListToggled()));`
- Connected slots/functions: `onSelectedAllControlPointsInListToggled`
- API footprints: `ToggleAllControlPointsSelected`

## widget: lockAllControlPointsInListMenuButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkMenuButton`
- Search text: Toggle lock flag on all control points in the list. Use the drop down menu to set all to locked or unlocked. | lockAllControlPointsInListMenuButton | ctkMenuButton
- Tooltip: Toggle lock flag on all control points in the list. Use the drop down menu to set all to locked or unlocked.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:289: lockMenu = new QMenu(qSlicerMarkupsModuleWidget::tr("Lock"), this->lockAllControlPointsInListMenuButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:304: this->lockAllControlPointsInListMenuButton->setMenu(this->lockMenu);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:305: this->lockAllControlPointsInListMenuButton->setIcon(QIcon(":/Icons/Small/SlicerLockUnlock.png"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:308: QObject::connect(this->lockAllControlPointsInListMenuButton, SIGNAL(clicked()), q, SLOT(onLockAllControlPointsInListToggled()));`
- Connected slots/functions: `onLockAllControlPointsInListToggled`
- API footprints: `ToggleAllControlPointsLocked`

## widget: missingControlPointPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Skip placement of highlighted control point(s) from the active list (will clear current position). | missingControlPointPushButton | QPushButton
- Tooltip: Skip placement of highlighted control point(s) from the active list (will clear current position).
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:339: QObject::connect(this->missingControlPointPushButton, SIGNAL(clicked()), q, SLOT(onMissingControlPointPushButtonClicked()));`
- Connected slots/functions: `onMissingControlPointPushButtonClicked`
- API footprints: `GetNthControlPointPositionStatus`, `SetNthControlPointPositionMissing`, `UnsetNthControlPointPosition`, `vtkMRMLMarkupsNode::PositionMissing`

## widget: unsetControlPointPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Clear the position of highlighted control point(s) from the active list (the control points will not be deleted). | unsetControlPointPushButton | QPushButton
- Tooltip: Clear the position of highlighted control point(s) from the active list (the control points will not be deleted).
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:340: QObject::connect(this->unsetControlPointPushButton, SIGNAL(clicked()), q, SLOT(onUnsetControlPointPushButtonClicked()));`
- Connected slots/functions: `onUnsetControlPointPushButtonClicked`
- API footprints: `UnsetNthControlPointPosition`

## widget: deleteControlPointPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Delete the highlighted control point(s) from the active list | deleteControlPointPushButton | QPushButton
- Tooltip: Delete the highlighted control point(s) from the active list
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:342: QObject::connect(this->deleteControlPointPushButton, SIGNAL(clicked()), q, SLOT(onDeleteControlPointPushButtonClicked()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:945: d->deleteControlPointPushButton->setEnabled(false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:952: d->deleteControlPointPushButton->setEnabled(true);`
- Connected slots/functions: `onDeleteControlPointPushButtonClicked`
- API footprints: `RemoveNthControlPoint`

## widget: deleteAllControlPointsInListPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Remove all control points from the active list | deleteAllControlPointsInListPushButton | QPushButton
- Tooltip: Remove all control points from the active list
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:343: QObject::connect(this->deleteAllControlPointsInListPushButton, SIGNAL(clicked()), q, SLOT(onDeleteAllControlPointsInListPushButtonClicked()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:946: d->deleteAllControlPointsInListPushButton->setEnabled(false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:953: d->deleteAllControlPointsInListPushButton->setEnabled(true);`
- Connected slots/functions: `onDeleteAllControlPointsInListPushButtonClicked`
- API footprints: `GetNumberOfControlPoints`, `RemoveAllControlPoints`

## widget: CutControlPointsToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Cut | CutControlPointsToolButton | QToolButton
- Text: Cut
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:352: this->CutControlPointsToolButton->setDefaultAction(this->cutAction);`

## widget: CopyControlPointsToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Copy | CopyControlPointsToolButton | QToolButton
- Text: Copy
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:362: this->CopyControlPointsToolButton->setDefaultAction(this->copyAction);`

## widget: PasteControlPointsToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Paste | PasteControlPointsToolButton | QToolButton
- Text: Paste
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:372: this->PasteControlPointsToolButton->setDefaultAction(this->pasteAction);`

## widget: label_coords

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Coordinates:   | label_coords | QLabel
- Text: Coordinates:  
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: coordinatesComboBox

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: Set visibility and coordinate system of control point positions. | coordinatesComboBox | QComboBox
- Tooltip: Set visibility and coordinate system of control point positions.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:434: QObject::connect(this->coordinatesComboBox, SIGNAL(currentIndexChanged(int)), q, SLOT(onHideCoordinateColumnsToggled(int)));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1177: if (d->coordinatesComboBox->currentIndex() == COORDINATE_COMBOBOX_INDEX_WORLD)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2060: if (d->coordinatesComboBox->currentIndex() == COORDINATE_COMBOBOX_INDEX_WORLD)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2080: if (d->coordinatesComboBox->currentIndex() == COORDINATE_COMBOBOX_INDEX_WORLD)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:2325: if (d->coordinatesComboBox->currentIndex() == COORDINATE_COMBOBOX_INDEX_WORLD)`
- Connected slots/functions: `onHideCoordinateColumnsToggled`
- API footprints: `SetNthControlPointPositionWorld`

## widget: activeMarkupTableWidget

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: The control points in the currently active markups node. Right click in a row for delete, jump, copy, move. | activeMarkupTableWidget | QTableWidget
- Tooltip: The control points in the currently active markups node. Right click in a row for delete, jump, copy, move.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:415: this->activeMarkupTableWidget->setSelectionBehavior(QAbstractItemView::SelectRows);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:417: this->activeMarkupTableWidget->setSelectionMode(QAbstractItemView::ExtendedSelection);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:420: this->activeMarkupTableWidget->setColumnCount(this->numberOfColumns());`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:421: this->activeMarkupTableWidget->setHorizontalHeaderLabels(this->columnLabels);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:423: this->activeMarkupTableWidget->horizontalHeader()->setSectionResizeMode(qSlicerMarkupsModuleWidgetPrivate::NameColumn, QHeaderView::Stretch);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:424: this->activeMarkupTableWidget->horizontalHeader()->setStretchLastSection(false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:427: this->activeMarkupTableWidget->setColumnWidth(qSlicerMarkupsModuleWidgetPrivate::NameColumn, 60);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:428: this->activeMarkupTableWidget->setColumnWidth(qSlicerMarkupsModuleWidgetPrivate::DescriptionColumn, 120);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:429: this->activeMarkupTableWidget->setColumnWidth(qSlicerMarkupsModuleWidgetPrivate::RColumn, 65);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:430: this->activeMarkupTableWidget->setColumnWidth(qSlicerMarkupsModuleWidgetPrivate::AColumn, 65);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:431: this->activeMarkupTableWidget->setColumnWidth(qSlicerMarkupsModuleWidgetPrivate::SColumn, 65);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:438: QTableWidgetItem* selectedHeader = this->activeMarkupTableWidget->horizontalHeaderItem(qSlicerMarkupsModuleWidgetPrivate::SelectedColumn);`
- Connected slots/functions: `onActiveMarkupTableCellChanged`, `onActiveMarkupTableCellClicked`, `onActiveMarkupTableCurrentCellChanged`, `onRightClickActiveMarkupTableWidget`
- API footprints: `GetID`, `GetNthControlPointPosition`, `GetNthControlPointPositionStatus`, `GetNthControlPointPositionWorld`, `GetNumberOfControlPoints`, `JumpSlicesToNthPointInMarkup`, `ResetNthControlPointPosition`, `SetControlPointPlacementStartIndex`, `SetNthControlPointDescription`, `SetNthControlPointLabel`, `SetNthControlPointLocked`, `SetNthControlPointPosition`, `SetNthControlPointPositionMissing`, `SetNthControlPointPositionWorld`, `SetNthControlPointSelected`, `SetNthControlPointVisibility`, `SwapControlPoints`, `UnsetNthControlPointPosition`, `vtkMRMLMarkupsNode::PositionDefined`, `vtkMRMLMarkupsNode::PositionMissing`, `vtkMRMLMarkupsNode::PositionPreview`, `vtkMRMLMarkupsNode::PositionUndefined`

## widget: advancedCollapsibleButton

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: Display, naming, volume interactions, moving up/down, adding | advancedCollapsibleButton | ctkCollapsibleGroupBox
- Tooltip: Display, naming, volume interactions, moving up/down, adding
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: moveControlPointUpPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Move a highlighted control point up one spot in the list | moveControlPointUpPushButton | QPushButton
- Tooltip: Move a highlighted control point up one spot in the list
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:336: QObject::connect(this->moveControlPointUpPushButton, SIGNAL(clicked()), q, SLOT(onMoveControlPointUpPushButtonClicked()));`
- Connected slots/functions: `onMoveControlPointUpPushButtonClicked`
- API footprints: `SwapControlPoints`

## widget: moveControlPointDownPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Move a highlighted control point down one spot in the list | moveControlPointDownPushButton | QPushButton
- Tooltip: Move a highlighted control point down one spot in the list
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:337: QObject::connect(this->moveControlPointDownPushButton, SIGNAL(clicked()), q, SLOT(onMoveControlPointDownPushButtonClicked()));`
- Connected slots/functions: `onMoveControlPointDownPushButtonClicked`
- API footprints: `SwapControlPoints`

## widget: addControlPointPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Add a new control point to the active list, at origin | addControlPointPushButton | QPushButton
- Tooltip: Add a new control point to the active list, at origin
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:334: QObject::connect(this->addControlPointPushButton, SIGNAL(clicked()), q, SLOT(onAddControlPointPushButtonClicked()));`
- Connected slots/functions: `onAddControlPointPushButtonClicked`
- API footprints: `AddControlPoint`, `GetFixedNumberOfControlPoints`, `GetMaximumNumberOfControlPoints`, `GetNumberOfControlPoints`, `UnsetNthControlPointPosition`

## widget: namingCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: namingCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: nameFormatLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Name Format | Include %N for list name, %d for number. | nameFormatLabel | QLabel
- Text: Name Format
- Tooltip: Include %N for list name, %d for number.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: nameFormatLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: Format for creating names of new control points, using sprintf format style. %N is replaced by the list name, %S is replaced by the markup's short name and %d by an integer. | nameFormatLineEdit | QLineEdit
- Tooltip: Format for creating names of new control points, using sprintf format style. %N is replaced by the list name, %S is replaced by the markup's short name and %d by an integer.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:400: QObject::connect(this->nameFormatLineEdit, SIGNAL(textEdited(const QString&)), q, SLOT(onNameFormatLineEditTextEdited(const QString&)));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:960: d->nameFormatLineEdit->setText(nameFormat);`
- Connected slots/functions: `onNameFormatLineEditTextEdited`
- API footprints: `GetControlPointLabelFormat`, `SetControlPointLabelFormat`

## widget: resetNameFormatToDefaultPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Reset | Reset the name format field to the default value. | resetNameFormatToDefaultPushButton | QPushButton
- Text: Reset
- Tooltip: Reset the name format field to the default value.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:404: QObject::connect(this->resetNameFormatToDefaultPushButton, SIGNAL(clicked()), q, SLOT(onResetNameFormatToDefaultPushButtonClicked()));`
- Connected slots/functions: `onResetNameFormatToDefaultPushButtonClicked`
- API footprints: `CreateNodeByClass`, `GetClassName`, `GetControlPointLabelFormat`, `GetDefaultNodeByClass`, `SetControlPointLabelFormat`, `vtkMRMLMarkupsNode::SafeDownCast`

## widget: renameAllWithCurrentNameFormatPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Apply | Rename all control points in this list according to the current name format, trying to preserve numbers. | renameAllWithCurrentNameFormatPushButton | QPushButton
- Text: Apply
- Tooltip: Rename all control points in this list according to the current name format, trying to preserve numbers.
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:408: QObject::connect(this->renameAllWithCurrentNameFormatPushButton, SIGNAL(clicked()), q, SLOT(onRenameAllWithCurrentNameFormatPushButtonClicked()));`
- Connected slots/functions: `onRenameAllWithCurrentNameFormatPushButtonClicked`
- API footprints: `RenameAllControlPointsFromCurrentFormat`

## widget: measurementsCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Measurements | measurementsCollapsibleButton | ctkCollapsibleButton
- Text: Measurements
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1860: d->measurementsCollapsibleButton->setEnabled(enable);`

## widget: measurementsLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: No measurement | measurementsLabel | QLabel
- Text: No measurement
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3054: d->measurementsLabel->setText(tr("No measurement"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3081: d->measurementsLabel->setText(measurementsString.isEmpty() ? tr("No measurement") : measurementsString);`

## widget: MeasurementSettingsCollapsibleGroupBox

- Confidence: `ui_only`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: MeasurementSettingsCollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: measurementSettingsTableWidget

- Confidence: `linked_to_api`
- Widget/action class: `QTableWidget`
- Search text: measurementSettingsTableWidget | QTableWidget
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:487: this->measurementSettingsTableWidget->setVisible(false);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3037: QList<QTableWidgetItem*> nameItemsFound = d->measurementSettingsTableWidget->findItems(measurementName, Qt::MatchExactly);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3040: QCheckBox* checkbox = qobject_cast<QCheckBox*>(d->measurementSettingsTableWidget->cellWidget(nameItem->row(), 1));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3089: d->measurementSettingsTableWidget->clear();`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3090: d->measurementSettingsTableWidget->setVisible(d->MarkupsNode != nullptr && d->MarkupsNode->Measurements->GetNumberOfItems() > 0);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3097: d->measurementSettingsTableWidget->setHorizontalHeaderLabels(QStringList() << tr("Name") << tr("Enabled"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3098: d->measurementSettingsTableWidget->setRowCount(d->MarkupsNode->Measurements->GetNumberOfItems());`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3108: d->measurementSettingsTableWidget->setItem(i, 0, nameItem);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3114: d->measurementSettingsTableWidget->setCellWidget(i, 1, enabledCheckbox);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3115: d->measurementSettingsTableWidget->setRowHeight(i, enabledCheckbox->sizeHint().height());`
- API footprints: `GetEnabled`, `GetName`, `GetNumberOfItems`

## widget: exportImportCollapsibleButton

- Confidence: `linked_to_code`
- Widget/action class: `qMRMLCollapsibleButton`
- Search text: Export/import Table | exportImportCollapsibleButton | qMRMLCollapsibleButton
- Text: Export/import Table
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:490: this->ImportExportOperationButtonGroup = new QButtonGroup(this->exportImportCollapsibleButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:494: this->ImportExportCoordinateSystemButtonGroup = new QButtonGroup(this->exportImportCollapsibleButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1861: d->exportImportCollapsibleButton->setEnabled(enable);`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Operation: | label_4 | QLabel
- Text: Operation:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: tableExportRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Export | tableExportRadioButton | QRadioButton
- Text: Export
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:491: this->ImportExportOperationButtonGroup->addButton(this->tableExportRadioButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:498: this->tableExportRadioButton->setChecked(true);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3159: bool isExport = d->tableExportRadioButton->isChecked();`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3189: if (d->tableExportRadioButton->isChecked())`

## widget: tableImportRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: Import | tableImportRadioButton | QRadioButton
- Text: Import
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:492: this->ImportExportOperationButtonGroup->addButton(this->tableImportRadioButton);`

## widget: exportImportTableLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Table: | exportImportTableLabel | QLabel
- Text: Table:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3163: d->exportImportTableLabel->setText(tr("Output table:"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3170: d->exportImportTableLabel->setText(tr("Input table:"));`

## widget: exportedImportedNodeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: exportedImportedNodeComboBox | qMRMLNodeComboBox
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:501: QObject::connect(this->exportedImportedNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(updateImportExportWidgets()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3177: d->exportImportPushButton->setEnabled(d->exportedImportedNodeComboBox->currentNode() != nullptr);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3193: this->markupsLogic()->ExportControlPointsToTable(d->MarkupsNode, vtkMRMLTableNode::SafeDownCast(d->exportedImportedNodeComboBox->currentNode()), coordinateSystem);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3197: this->markupsLogic()->ImportControlPointsFromTable(d->MarkupsNode, vtkMRMLTableNode::SafeDownCast(d->exportedImportedNodeComboBox->currentNode()));`
- Connected slots/functions: `updateImportExportWidgets`
- API footprints: `ExportControlPointsToTable`, `ImportControlPointsFromTable`, `vtkMRMLStorageNode::CoordinateSystemLPS`, `vtkMRMLStorageNode::CoordinateSystemRAS`, `vtkMRMLTableNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLTableNode"]}

## widget: exportImportPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Apply | exportImportPushButton | QPushButton
- Text: Apply
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:505: QObject::connect(this->exportImportPushButton, SIGNAL(clicked()), q, SLOT(onImportExportApply()));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3164: d->exportImportPushButton->setText(tr("Export"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3165: d->exportImportPushButton->setToolTip(tr("Export control points coordinates and properties to table."));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3171: d->exportImportPushButton->setText(tr("Import"));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3172: d->exportImportPushButton->setToolTip(tr("Import control points coordinates and properties from table node.\n"`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3177: d->exportImportPushButton->setEnabled(d->exportedImportedNodeComboBox->currentNode() != nullptr);`
- Connected slots/functions: `onImportExportApply`
- API footprints: `ExportControlPointsToTable`, `ImportControlPointsFromTable`, `vtkMRMLStorageNode::CoordinateSystemLPS`, `vtkMRMLStorageNode::CoordinateSystemRAS`, `vtkMRMLTableNode::SafeDownCast`

## widget: CollapsibleGroupBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleGroupBox`
- Search text: CollapsibleGroupBox | ctkCollapsibleGroupBox
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:509: QObject::connect(this->ColorLegendCollapsibleGroupBox, SIGNAL(toggled(bool)), q, SLOT(onColorLegendCollapsibleGroupBoxToggled(bool)));`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:920: d->ColorLegendCollapsibleGroupBox->setCollapsed(!colorLegendNode);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:921: d->ColorLegendCollapsibleGroupBox->setEnabled(displayNode && displayNode->GetColorNode());`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:1821: void qSlicerMarkupsModuleWidget::onColorLegendCollapsibleGroupBoxToggled(bool toggled)`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h:262: void onColorLegendCollapsibleGroupBoxToggled(bool);`
- Connected slots/functions: `onColorLegendCollapsibleGroupBoxToggled`
- API footprints: `GetColorNode`, `GetMRMLApplicationLogic`, `PauseRender`, `ResumeRender`, `SetVisibility`

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Export coordinate system: | label_5 | QLabel
- Text: Export coordinate system:
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`

## widget: rasExportRadioButton

- Confidence: `linked_to_api`
- Widget/action class: `QRadioButton`
- Search text: RAS | rasExportRadioButton | QRadioButton
- Text: RAS
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:496: this->ImportExportCoordinateSystemButtonGroup->addButton(this->rasExportRadioButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:499: this->rasExportRadioButton->setChecked(true);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3176: d->rasExportRadioButton->setEnabled(isExport);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3192: int coordinateSystem = d->rasExportRadioButton->isChecked() ? vtkMRMLStorageNode::CoordinateSystemRAS : vtkMRMLStorageNode::CoordinateSystemLPS;`
- API footprints: `ExportControlPointsToTable`, `vtkMRMLStorageNode::CoordinateSystemLPS`, `vtkMRMLStorageNode::CoordinateSystemRAS`, `vtkMRMLTableNode::SafeDownCast`

## widget: lpsExportRadioButton

- Confidence: `linked_to_code`
- Widget/action class: `QRadioButton`
- Search text: LPS | lpsExportRadioButton | QRadioButton
- Text: LPS
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:495: this->ImportExportCoordinateSystemButtonGroup->addButton(this->lpsExportRadioButton);`
  - `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx:3175: d->lpsExportRadioButton->setEnabled(isExport);`

## widget: DynamicSpacer

- Confidence: `ui_only`
- Widget/action class: `ctkDynamicSpacer`
- Search text: DynamicSpacer | ctkDynamicSpacer
- Implementation candidates: `Modules/Loadable/Markups/qSlicerMarkupsModule.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModule.h`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.cxx`, `Modules/Loadable/Markups/qSlicerMarkupsModuleWidget.h`
