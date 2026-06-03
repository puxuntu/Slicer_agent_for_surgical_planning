# Slicer UI Analysis: Modules/Loadable/Markups/Widgets/Resources/UI/qSlicerMarkupsPlaceWidget.ui

- Owner class: `qSlicerMarkupsPlaceWidget`
- UI file: `Modules/Loadable/Markups/Widgets/Resources/UI/qSlicerMarkupsPlaceWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerMarkupsPlaceWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerMarkupsPlaceWidget | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:22: #include "qSlicerMarkupsPlaceWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:23: #include "ui_qSlicerMarkupsPlaceWidget.h"`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:46: class qSlicerMarkupsPlaceWidgetPrivate : public Ui_qSlicerMarkupsPlaceWidget`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:48: Q_DECLARE_PUBLIC(qSlicerMarkupsPlaceWidget);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:51: qSlicerMarkupsPlaceWidget* const q_ptr;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:54: qSlicerMarkupsPlaceWidgetPrivate(qSlicerMarkupsPlaceWidget& object);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:55: ~qSlicerMarkupsPlaceWidgetPrivate();`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:56: virtual void setupUi(qSlicerMarkupsPlaceWidget*);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:65: qSlicerMarkupsPlaceWidget::PlaceMultipleMarkupsType PlaceMultipleMarkups;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:77: qSlicerMarkupsPlaceWidgetPrivate::qSlicerMarkupsPlaceWidgetPrivate(qSlicerMarkupsPlaceWidget& object)`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:84: this->PlaceMultipleMarkups = qSlicerMarkupsPlaceWidget::ShowPlaceMultipleMarkupsOption;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:92: qSlicerMarkupsPlaceWidgetPrivate::~qSlicerMarkupsPlaceWidgetPrivate() = default;`
- API footprints: `vtkMRMLMarkupsFiducialNode::SafeDownCast`, `vtkMRMLMarkupsNode::SafeDownCast`

## widget: ColorButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkColorPickerButton`
- Search text: Select the display color. | ColorButton | ctkColorPickerButton
- Tooltip: Select the display color.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:132: d->OptionsWidgets << d->ColorButton << d->PlaceButton << d->DeleteButton << d->MoreButton;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:136: connect(d->ColorButton, SIGNAL(colorChanged(QColor)), this, SLOT(onColorButtonChanged(QColor)));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:493: d->ColorButton->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:497: bool wasBlockedColorButton = d->ColorButton->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:498: d->ColorButton->setColor(d->DefaultNodeColor);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:499: d->ColorButton->blockSignals(wasBlockedColorButton);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:513: d->ColorButton->setEnabled(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:518: bool wasBlockedColorButton = d->ColorButton->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:527: d->ColorButton->setColor(qColor);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:569: d->ColorButton->blockSignals(wasBlockedColorButton);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:827: void qSlicerMarkupsPlaceWidget::onColorButtonChanged(QColor color)`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h:220: void onColorButtonChanged(QColor);`
- Connected slots/functions: `onColorButtonChanged`
- API footprints: `GetDisplayNode`, `GetNumberOfControlPoints`, `SetSelectedColor`
- Key UI properties: {"checkable": "true"}

## widget: PlaceButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Place a control point | PlaceButton | QToolButton
- Text: ...
- Tooltip: Place a control point
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:132: d->OptionsWidgets << d->ColorButton << d->PlaceButton << d->DeleteButton << d->MoreButton;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:142: QObject::connect(d->PlaceButton, SIGNAL(toggled(bool)), this, SLOT(setPlaceModeEnabled(bool)));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:146: d->PlaceButton->setMenu(d->PlaceMenu);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:494: d->PlaceButton->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:511: d->PlaceButton->setEnabled(activePlaceNodePlacementValid);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:573: bool wasBlockedPlaceButton = d->PlaceButton->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:574: d->PlaceButton->setChecked(placeModeEnabled());`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:575: d->PlaceButton->blockSignals(wasBlockedPlaceButton);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:576: d->PlaceButton->setIcon(QIcon(currentMarkupsNode->GetAddIcon()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:654: if (d->PlaceButton)`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:656: d->PlaceButton->setMenu(d->PlaceMultipleMarkups == ShowPlaceMultipleMarkupsOption ? d->PlaceMenu : nullptr);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:658: d->PlaceButton->setPopupMode(d->PlaceMultipleMarkups == ShowPlaceMultipleMarkupsOption ? QToolButton::MenuButtonPopup : QToolButton::DelayedPopup);`
- Connected slots/functions: `setPlaceModeEnabled`
- API footprints: `GetAddIcon`, `GetControlPointPlacementComplete`, `SetActiveList`, `SetCurrentInteractionMode`, `vtkMRMLInteractionNode::Place`, `vtkMRMLInteractionNode::ViewTransform`
- Key UI properties: {"checkable": "true", "popupMode": "QToolButton::MenuButtonPopup"}

## widget: DeleteButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Delete last added control point | DeleteButton | QToolButton
- Text: ...
- Tooltip: Delete last added control point
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:132: d->OptionsWidgets << d->ColorButton << d->PlaceButton << d->DeleteButton << d->MoreButton;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:149: d->DeleteMenu = new QMenu(tr("Delete options"), d->DeleteButton);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:161: updateDeleteButton();`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:163: d->DeleteButton->setVisible(d->DeleteMarkupsButtonVisible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:164: connect(d->DeleteButton, SIGNAL(clicked()), this, SLOT(modifyLastPoint()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:495: d->DeleteButton->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:514: d->DeleteButton->setEnabled(currentMarkupsNode->GetNumberOfControlPoints() > 0);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:543: d->DeleteButton->setIcon(QIcon(":/Icons/MarkupsUnset.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:544: d->DeleteButton->setToolTip(qSlicerMarkupsPlaceWidget::tr("Unset position of the last control point placed (the control point will not be deleted)."));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:549: d->DeleteButton->setIcon(QIcon(":/Icons/MarkupsDelete.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:550: d->DeleteButton->setToolTip(qSlicerMarkupsPlaceWidget::tr("Delete last added control point"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:554: this->updateDeleteButton();`
- Connected slots/functions: `modifyLastPoint`
- API footprints: `GetDisplayNode`, `GetFixedNumberOfControlPoints`, `GetNumberOfControlPoints`
- Key UI properties: {"popupMode": "QToolButton::MenuButtonPopup"}

## widget: MoreButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Click for more options | MoreButton | QToolButton
- Text: ...
- Tooltip: Click for more options
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:132: d->OptionsWidgets << d->ColorButton << d->PlaceButton << d->DeleteButton << d->MoreButton;`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:166: QMenu* moreMenu = new QMenu(tr("More options"), d->MoreButton);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:174: d->MoreButton->setMenu(moreMenu);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:496: d->MoreButton->setEnabled(false);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:515: d->MoreButton->setEnabled(true);`
- API footprints: `GetNumberOfControlPoints`
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## action: ActionPlacePersistentPoint

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Place multiple control points | Place multiple control points | ActionPlacePersistentPoint
- Text: Place multiple control points
- Tooltip: Place multiple control points
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:140: d->PlaceMenu->addAction(d->ActionPlacePersistentPoint);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:141: QObject::connect(d->ActionPlacePersistentPoint, SIGNAL(toggled(bool)), this, SLOT(onPlacePersistentPoint(bool)));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:578: bool wasBlockedPersistencyAction = d->ActionPlacePersistentPoint->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:579: d->ActionPlacePersistentPoint->setChecked(placeModePersistency());`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:580: d->ActionPlacePersistentPoint->blockSignals(wasBlockedPersistencyAction);`
- Connected slots/functions: `onPlacePersistentPoint`
- API footprints: `GetAddIcon`
- Key UI properties: {"checkable": "true"}

## action: ActionDeleteAll

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Delete all control points | Delete all control points in the list | ActionDeleteAll
- Text: Delete all control points
- Tooltip: Delete all control points in the list
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:155: d->DeleteMenu->addAction(d->ActionDeleteAll);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:156: QObject::connect(d->ActionDeleteAll, SIGNAL(triggered()), this, SLOT(deleteAllPoints()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:158: d->ActionDeleteAll->setVisible(d->DeleteAllControlPointsOptionVisible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:553: d->ActionDeleteAll->setVisible(!fixedNumberControlPoints && d->DeleteAllControlPointsOptionVisible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:599: bool showMenu = (d->ActionDeleteAll->isVisible() || d->ActionUnsetLast->isVisible() || d->ActionUnsetAll->isVisible());`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:687: d->ActionDeleteAll->setVisible(visible);`
- Connected slots/functions: `deleteAllPoints`
- API footprints: `RemoveAllControlPoints`

## action: ActionUnsetLast

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Clear last control point position | Clear the position of the last control point placed (the control point will not be deleted). | ActionUnsetLast
- Text: Clear last control point position
- Tooltip: Clear the position of the last control point placed (the control point will not be deleted).
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:151: d->DeleteMenu->addAction(d->ActionUnsetLast);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:152: QObject::connect(d->ActionUnsetLast, SIGNAL(triggered()), this, SLOT(unsetLastDefinedPoint()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:159: d->ActionUnsetLast->setVisible(d->UnsetLastControlPointOptionVisible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:552: d->ActionUnsetLast->setVisible(!fixedNumberControlPoints && d->UnsetLastControlPointOptionVisible); // QToolButton button action does this so don't also have in menu`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:599: bool showMenu = (d->ActionDeleteAll->isVisible() || d->ActionUnsetLast->isVisible() || d->ActionUnsetAll->isVisible());`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:706: d->ActionUnsetLast->setVisible(visible);`
- Connected slots/functions: `unsetLastDefinedPoint`
- API footprints: `GetNthControlPointPositionStatus`, `GetNumberOfControlPoints`, `UnsetNthControlPointPosition`, `vtkMRMLMarkupsNode::PositionUndefined`

## action: ActionUnsetAll

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Clear all control point positions | Clear the position of all control points in the list (the control points will not be deleted). | ActionUnsetAll
- Text: Clear all control point positions
- Tooltip: Clear the position of all control points in the list (the control points will not be deleted).
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:153: d->DeleteMenu->addAction(d->ActionUnsetAll);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:154: QObject::connect(d->ActionUnsetAll, SIGNAL(triggered()), this, SLOT(unsetAllPoints()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:160: d->ActionUnsetAll->setVisible(d->UnsetAllControlPointsOptionVisible);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:599: bool showMenu = (d->ActionDeleteAll->isVisible() || d->ActionUnsetLast->isVisible() || d->ActionUnsetAll->isVisible());`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:725: d->ActionUnsetAll->setVisible(visible);`
- Connected slots/functions: `unsetAllPoints`
- API footprints: `UnsetAllControlPoints`

## action: ActionVisibility

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Visibility | Toggle markup visibility | ActionVisibility
- Text: Visibility
- Tooltip: Toggle markup visibility
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:168: moreMenu->addAction(d->ActionVisibility);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:171: QObject::connect(d->ActionVisibility, SIGNAL(triggered()), this, SLOT(onVisibilityButtonClicked()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:519: bool wasBlockedVisibilityButton = d->ActionVisibility->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:556: d->ActionVisibility->setEnabled(currentMarkupsNode->GetDisplayNode() != nullptr);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:561: d->ActionVisibility->setIcon(QIcon(":/Icons/Small/SlicerVisible.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:565: d->ActionVisibility->setIcon(QIcon(":/Icons/Small/SlicerInvisible.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:570: d->ActionVisibility->blockSignals(wasBlockedVisibilityButton);`
- Connected slots/functions: `onVisibilityButtonClicked`
- API footprints: `GetDisplayNode`, `GetVisibility`, `SetVisibility`

## action: ActionLocked

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Locked | Toggle control point positions lock | ActionLocked
- Text: Locked
- Tooltip: Toggle control point positions lock
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:169: moreMenu->addAction(d->ActionLocked);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:172: QObject::connect(d->ActionLocked, SIGNAL(triggered()), this, SLOT(onLockedButtonClicked()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:520: bool wasBlockedLockButton = d->ActionLocked->blockSignals(true);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:532: d->ActionLocked->setIcon(QIcon(":/Icons/Small/SlicerLock.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:536: d->ActionLocked->setIcon(QIcon(":/Icons/Small/SlicerUnlock.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:571: d->ActionLocked->blockSignals(wasBlockedLockButton);`
- Connected slots/functions: `onLockedButtonClicked`
- API footprints: `GetDisplayNode`, `GetLocked`, `SetLocked`

## action: ActionFixedNumberOfControlPoints

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Control point number locked | Toggle control point number lock. If locked then it is not possible to add or delete control points. Instead of deleting, position control points can be unset. | ActionFixedNumberOfControlPoints
- Text: Control point number locked
- Tooltip: Toggle control point number lock. If locked then it is not possible to add or delete control points. Instead of deleting, position control points can be unset.
- Implementation candidates: `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx`, `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:170: moreMenu->addAction(d->ActionFixedNumberOfControlPoints);`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:173: QObject::connect(d->ActionFixedNumberOfControlPoints, SIGNAL(triggered()), this, SLOT(onFixedNumberOfControlPointsButtonClicked()));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:542: d->ActionFixedNumberOfControlPoints->setIcon(QIcon(":/Icons/Small/SlicerPointNumberLock.png"));`
  - `Modules/Loadable/Markups/Widgets/qSlicerMarkupsPlaceWidget.cxx:548: d->ActionFixedNumberOfControlPoints->setIcon(QIcon(":/Icons/Small/SlicerPointNumberUnlock.png"));`
- Connected slots/functions: `onFixedNumberOfControlPointsButtonClicked`
- API footprints: `GetFixedNumberOfControlPoints`, `SetCurrentInteractionMode`, `SetFixedNumberOfControlPoints`, `vtkMRMLInteractionNode::ViewTransform`
