# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLThreeDViewControllerWidget.ui

- Owner class: `qMRMLThreeDViewControllerWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLThreeDViewControllerWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLThreeDViewControllerWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qMRMLThreeDViewControllerWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:40: #include "qMRMLThreeDViewControllerWidget_p.h"`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:53: // qMRMLThreeDViewControllerWidgetPrivate methods`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:56: qMRMLThreeDViewControllerWidgetPrivate::qMRMLThreeDViewControllerWidgetPrivate(qMRMLThreeDViewControllerWidget& object)`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:72: qMRMLThreeDViewControllerWidgetPrivate::~qMRMLThreeDViewControllerWidgetPrivate() = default;`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:75: void qMRMLThreeDViewControllerWidgetPrivate::setupPopupUi()`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:77: Q_Q(qMRMLThreeDViewControllerWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:81: this->Ui_qMRMLThreeDViewControllerWidget::setupUi(this->PopupWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:100: QMenu* visibilityMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Visibility"), this->PopupWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:125: QObject::connect(this->OrientationMarkerTypesMapper, &QSignalMapper::mappedInt, q, &qMRMLThreeDViewControllerWidget::setOrientationMarkerType);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:137: QObject::connect(this->OrientationMarkerSizesMapper, &QSignalMapper::mappedInt, q, &qMRMLThreeDViewControllerWidget::setOrientationMarkerSize);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:140: QMenu* orientationMarkerMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Orientation marker"), this->PopupWidget);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:158: QObject::connect(this->RulerTypesMapper, &QSignalMapper::mappedInt, q, &qMRMLThreeDViewControllerWidget::setRulerType);`
- Connected slots/functions: `mappedInt`, `setOrientationMarkerSize`, `setOrientationMarkerType`, `setRulerColor`, `setRulerType`, `setStereoType`
- API footprints: `EndViewNodeInteraction`, `GetMRMLScene`, `GetRenderMode`, `SetOrientationMarkerSize`, `SetOrientationMarkerType`, `SetRenderMode`, `SetRulerColor`, `SetRulerType`, `SetStereoType`, `StartViewNodeInteraction`, `vtkMRMLViewNode::Off`, `vtkMRMLViewNode::OrientationMarkerSizeFlag`, `vtkMRMLViewNode::OrientationMarkerTypeFlag`, `vtkMRMLViewNode::Orthographic`, `vtkMRMLViewNode::RenderModeFlag`, `vtkMRMLViewNode::Rock`, `vtkMRMLViewNode::RulerColorFlag`, `vtkMRMLViewNode::RulerTypeFlag`, `vtkMRMLViewNode::RulerTypeNone`, `vtkMRMLViewNode::SafeDownCast`, `vtkMRMLViewNode::Spin`, `vtkMRMLViewNode::StereoTypeFlag`

## widget: AxesWidget

- Confidence: `linked_to_api`
- Widget/action class: `ctkAxesWidget`
- Search text: AxesWidget | ctkAxesWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:84: QObject::connect(this->AxesWidget, SIGNAL(currentAxisChanged(ctkAxesWidget::Axis)), q, SLOT(lookFromAxis(ctkAxesWidget::Axis)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:519: d->AxesWidget->setAxesLabels(axesLabels);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:666: void qMRMLThreeDViewControllerWidget::lookFromAxis(const ctkAxesWidget::Axis& axis)`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h:25: #include <ctkAxesWidget.h>`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h:82: void lookFromAxis(const ctkAxesWidget::Axis& axis);`
- Connected slots/functions: `lookFromAxis`
- API footprints: `EndCameraNodeInteraction`, `GetAxisLabel`, `StartCameraNodeInteraction`, `vtkMRMLCameraNode::LookFromAxis`

## widget: ZoomOutButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Zoom out of the scene by a small amount. | ZoomOutButton | QToolButton
- Tooltip: Zoom out of the scene by a small amount.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:94: QObject::connect(this->ZoomOutButton, SIGNAL(clicked()), q, SLOT(zoomOut()));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
- Connected slots/functions: `zoomOut`
- API footprints: `EndCameraNodeInteraction`, `StartCameraNodeInteraction`, `vtkMRMLCameraNode::ZoomOutFlag`

## widget: SpinButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Spin the 3D view. | SpinButton | QToolButton
- Tooltip: Spin the 3D view.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:238: this->AnimateViewButtonGroup->addButton(this->SpinButton, vtkMRMLViewNode::Spin);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:240: QObject::connect(this->SpinButton, SIGNAL(toggled(bool)), q, SLOT(spinView(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:570: d->SpinButton->setChecked(viewNode->GetAnimationMode() == vtkMRMLViewNode::Spin);`
- Connected slots/functions: `spinView`
- API footprints: `GetAnimationMode`, `GetRenderMode`, `vtkMRMLViewNode::Off`, `vtkMRMLViewNode::Orthographic`, `vtkMRMLViewNode::Rock`, `vtkMRMLViewNode::Spin`
- Key UI properties: {"checkable": "true"}

## widget: RockButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Rock the 3D view. | RockButton | QToolButton
- Tooltip: Rock the 3D view.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:239: this->AnimateViewButtonGroup->addButton(this->RockButton, vtkMRMLViewNode::Rock);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:241: QObject::connect(this->RockButton, SIGNAL(toggled(bool)), q, SLOT(rockView(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:571: d->RockButton->setChecked(viewNode->GetAnimationMode() == vtkMRMLViewNode::Rock);`
- Connected slots/functions: `rockView`
- API footprints: `GetAnimationMode`, `GetLayoutLabel`, `vtkMRMLViewNode::Off`, `vtkMRMLViewNode::Rock`, `vtkMRMLViewNode::Spin`
- Key UI properties: {"checkable": "true"}

## widget: VisibilityButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Toggle visibility of elements in the 3D view. | VisibilityButton | QToolButton
- Tooltip: Toggle visibility of elements in the 3D view.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:102: this->VisibilityButton->setMenu(visibilityMenu);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## widget: OrientationMarkerButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Orientation marker | OrientationMarkerButton | QToolButton
- Tooltip: Orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:142: this->OrientationMarkerButton->setMenu(orientationMarkerMenu);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:499: << d->MoreToolButton << d->OrientationMarkerButton; // RulerButton enable state is not set here (it depends on render mode)`
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## widget: ZoomInButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Zoom in on the scene by a small amount. | ZoomInButton | QToolButton
- Tooltip: Zoom in on the scene by a small amount.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:93: QObject::connect(this->ZoomInButton, SIGNAL(clicked()), q, SLOT(zoomIn()));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
- Connected slots/functions: `zoomIn`
- API footprints: `EndCameraNodeInteraction`, `StartCameraNodeInteraction`, `vtkMRMLCameraNode::ZoomInFlag`

## widget: MoreToolButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: MoreToolButton | QToolButton
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:186: this->MoreToolButton->setMenu(moreMenu);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:499: << d->MoreToolButton << d->OrientationMarkerButton; // RulerButton enable state is not set here (it depends on render mode)`
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## widget: ShadowsButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Display shadows for improved depth perception | ShadowsButton | QToolButton
- Tooltip: Display shadows for improved depth perception
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:248: this->ShadowsMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Shadows"), this->ShadowsButton);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:256: QMenu* ambientShadowsSizeScaleMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Size scale"), this->ShadowsButton);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:274: QMenu* ambientShadowsVolumeOpacityThresholdMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Volume opacity threshold"), this->ShadowsButton);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:291: QMenu* ambientShadowsIntensityScaleMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Intensity scale"), this->ShadowsButton);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:309: QMenu* ambientShadowsIntensityShiftMenu = new QMenu(qMRMLThreeDViewControllerWidget::tr("Intensity shift"), this->ShadowsButton);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:332: this->ShadowsButton->setMenu(this->ShadowsMenu);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## widget: RulerButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: ... | Show ruler. Only available in orthographic projection mode. | RulerButton | QToolButton
- Text: ...
- Tooltip: Show ruler. Only available in orthographic projection mode.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:176: this->RulerButton->setMenu(rulerMenu);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:499: << d->MoreToolButton << d->OrientationMarkerButton; // RulerButton enable state is not set here (it depends on render mode)`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:568: d->RulerButton->setEnabled(viewNode->GetRenderMode() == vtkMRMLViewNode::Orthographic);`
- API footprints: `GetAnimationMode`, `GetRenderMode`, `vtkMRMLViewNode::Orthographic`, `vtkMRMLViewNode::Spin`
- Key UI properties: {"popupMode": "QToolButton::InstantPopup"}

## widget: OrthoButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Toggle between orthographic and perspective rendering in the 3D view. | OrthoButton | QToolButton
- Tooltip: Toggle between orthographic and perspective rendering in the 3D view.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:90: QObject::connect(this->OrthoButton, SIGNAL(toggled(bool)), q, SLOT(setOrthographicModeEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:546: d->OrthoButton->setChecked(viewNode->GetRenderMode() == vtkMRMLViewNode::Orthographic);`
- Connected slots/functions: `setOrthographicModeEnabled`
- API footprints: `EndViewNodeInteraction`, `GetRenderMode`, `GetStereoType`, `SetRenderMode`, `StartViewNodeInteraction`, `vtkMRMLViewNode::Orthographic`, `vtkMRMLViewNode::Perspective`, `vtkMRMLViewNode::RenderModeFlag`
- Key UI properties: {"checkable": "true"}

## widget: CenterButton

- Confidence: `linked_to_code`
- Widget/action class: `QToolButton`
- Search text: Center view | CenterButton | QToolButton
- Tooltip: Center view
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:97: this->CenterButton->setDefaultAction(this->actionCenter);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:343: this->CenterToolButton->setObjectName("CenterButton_Header");`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:498: widgets << d->AxesWidget << d->CenterButton << d->OrthoButton << d->VisibilityButton << d->ZoomInButton << d->ZoomOutButton << d->ShadowsButton << d->RockButton << d->SpinButton`

## widget: ViewLinkButton

- Confidence: `linked_to_api`
- Widget/action class: `QToolButton`
- Search text: Link 3D views. Synchronizes properties of all 3D views in the same view group. | ViewLinkButton | QToolButton
- Tooltip: Link 3D views. Synchronizes properties of all 3D views in the same view group.
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:87: QObject::connect(this->ViewLinkButton, SIGNAL(toggled(bool)), q, SLOT(setViewLink(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:523: d->ViewLinkButton->setChecked(viewNode->GetLinkedControl());`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:526: d->ViewLinkButton->setIcon(QIcon(":Icons/LinkOn.png"));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:530: d->ViewLinkButton->setIcon(QIcon(":Icons/LinkOff.png"));`
- Connected slots/functions: `setViewLink`
- API footprints: `Delete`, `GetLinkedControl`, `GetNextItemAsObject`, `GetNodesByClass`, `InitTraversal`, `SetLinkedControl`, `vtkMRMLViewNode::SafeDownCast`
- Key UI properties: {"checkable": "true", "checked": "false"}

## action: actionNoStereo

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: No Stereo | actionNoStereo
- Text: No Stereo
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:193: this->StereoTypesMapper->setMapping(this->actionNoStereo, vtkMRMLViewNode::NoStereo);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:203: stereoTypesActions->addAction(this->actionNoStereo);`
- API footprints: `vtkMRMLViewNode::Anaglyph`, `vtkMRMLViewNode::NoStereo`, `vtkMRMLViewNode::QuadBuffer`
- Key UI properties: {"checkable": "true", "checked": "true"}

## action: actionSwitchToRedBlueStereo

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Red/blue | actionSwitchToRedBlueStereo
- Text: Red/blue
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:197: this->StereoTypesMapper->setMapping(this->actionSwitchToRedBlueStereo, vtkMRMLViewNode::RedBlue);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:204: stereoTypesActions->addAction(this->actionSwitchToRedBlueStereo);`
- API footprints: `vtkMRMLViewNode::Interlaced`, `vtkMRMLViewNode::QuadBuffer`, `vtkMRMLViewNode::RedBlue`, `vtkMRMLViewNode::UserDefined_1`, `vtkMRMLViewNode::UserDefined_2`
- Key UI properties: {"checkable": "true"}

## action: actionSwitchToAnaglyphStereo

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Anaglyph | actionSwitchToAnaglyphStereo
- Text: Anaglyph
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:194: this->StereoTypesMapper->setMapping(this->actionSwitchToAnaglyphStereo, vtkMRMLViewNode::Anaglyph);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:205: stereoTypesActions->addAction(this->actionSwitchToAnaglyphStereo);`
- API footprints: `vtkMRMLViewNode::Anaglyph`, `vtkMRMLViewNode::Interlaced`, `vtkMRMLViewNode::NoStereo`, `vtkMRMLViewNode::QuadBuffer`
- Key UI properties: {"checkable": "true"}

## action: actionSwitchToQuadBufferStereo

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: QuadBuffer | actionSwitchToQuadBufferStereo
- Text: QuadBuffer
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:195: this->StereoTypesMapper->setMapping(this->actionSwitchToQuadBufferStereo, vtkMRMLViewNode::QuadBuffer);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:207: stereoTypesActions->addAction(this->actionSwitchToQuadBufferStereo);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:217: this->actionSwitchToQuadBufferStereo->setEnabled(false); // Disabled by default`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:374: d->actionSwitchToQuadBufferStereo->setEnabled(d->ThreeDView->renderWindow()->GetStereoCapableWindow());`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:602: d->actionSwitchToQuadBufferStereo->setEnabled(value);`
- API footprints: `GetStereoCapableWindow`, `vtkMRMLViewNode::Anaglyph`, `vtkMRMLViewNode::Interlaced`, `vtkMRMLViewNode::NoStereo`, `vtkMRMLViewNode::QuadBuffer`, `vtkMRMLViewNode::RedBlue`
- Key UI properties: {"checkable": "true"}

## action: actionSwitchToInterlacedStereo

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Interlaced | Switch to Interlaced stereo mode | actionSwitchToInterlacedStereo
- Text: Interlaced
- Tooltip: Switch to Interlaced stereo mode
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:196: this->StereoTypesMapper->setMapping(this->actionSwitchToInterlacedStereo, vtkMRMLViewNode::Interlaced);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:206: stereoTypesActions->addAction(this->actionSwitchToInterlacedStereo);`
- API footprints: `vtkMRMLViewNode::Anaglyph`, `vtkMRMLViewNode::Interlaced`, `vtkMRMLViewNode::QuadBuffer`, `vtkMRMLViewNode::RedBlue`, `vtkMRMLViewNode::UserDefined_1`
- Key UI properties: {"checkable": "true"}

## action: actionSet3DAxisVisible

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: 3D cube | actionSet3DAxisVisible
- Text: 3D cube
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:105: visibilityMenu->addAction(this->actionSet3DAxisVisible);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:107: QObject::connect(this->actionSet3DAxisVisible, SIGNAL(triggered(bool)), q, SLOT(set3DAxisVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:533: d->actionSet3DAxisVisible->setChecked(viewNode->GetBoxVisible());`
- Connected slots/functions: `set3DAxisVisible`
- API footprints: `EndViewNodeInteraction`, `GetAxisLabelsVisible`, `GetBoxVisible`, `SetBoxVisible`, `StartViewNodeInteraction`, `vtkMRMLViewNode::BoxVisibleFlag`
- Key UI properties: {"checkable": "true", "checked": "true"}

## action: actionSet3DAxisLabelVisible

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: 3D axis label | actionSet3DAxisLabelVisible
- Text: 3D axis label
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:106: visibilityMenu->addAction(this->actionSet3DAxisLabelVisible);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:108: QObject::connect(this->actionSet3DAxisLabelVisible, SIGNAL(triggered(bool)), q, SLOT(set3DAxisLabelVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:534: d->actionSet3DAxisLabelVisible->setChecked(viewNode->GetAxisLabelsVisible());`
- Connected slots/functions: `set3DAxisLabelVisible`
- API footprints: `EndViewNodeInteraction`, `GetAxisLabelsVisible`, `GetBoxVisible`, `GetUseDepthPeeling`, `SetAxisLabelsVisible`, `StartViewNodeInteraction`, `vtkMRMLViewNode::BoxLabelVisibleFlag`
- Key UI properties: {"checkable": "true", "checked": "true"}

## action: actionSetLightBlueBackground

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Light blue background | Set light blue background | actionSetLightBlueBackground
- Text: Light blue background
- Tooltip: Set light blue background
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:226: visibilityMenu->addAction(this->actionSetLightBlueBackground);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:229: backgroundColorActions->addAction(this->actionSetLightBlueBackground);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:232: QObject::connect(this->actionSetLightBlueBackground, SIGNAL(triggered()), q, SLOT(setLightBlueBackground()));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:543: d->actionSetLightBlueBackground->setChecked(!d->actionSetBlackBackground->isChecked() && //`
- Connected slots/functions: `setLightBlueBackground`
- API footprints: `vtkMRMLViewNode::defaultBackgroundColor`, `vtkMRMLViewNode::defaultBackgroundColor2`
- Key UI properties: {"checkable": "true", "checked": "true"}

## action: actionSetBlackBackground

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Black background | Set black background | actionSetBlackBackground
- Text: Black background
- Tooltip: Set black background
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:227: visibilityMenu->addAction(this->actionSetBlackBackground);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:230: backgroundColorActions->addAction(this->actionSetBlackBackground);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:234: QObject::connect(this->actionSetBlackBackground, SIGNAL(triggered()), q, SLOT(setBlackBackground()));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:541: d->actionSetBlackBackground->setChecked(backgroundColor == Qt::black);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:543: d->actionSetLightBlueBackground->setChecked(!d->actionSetBlackBackground->isChecked() && //`
- Connected slots/functions: `setBlackBackground`
- API footprints: `GetBackgroundColor`
- Key UI properties: {"checkable": "true"}

## action: actionSetWhiteBackground

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: White background | Set white background | actionSetWhiteBackground
- Text: White background
- Tooltip: Set white background
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:228: visibilityMenu->addAction(this->actionSetWhiteBackground);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:231: backgroundColorActions->addAction(this->actionSetWhiteBackground);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:233: QObject::connect(this->actionSetWhiteBackground, SIGNAL(triggered()), q, SLOT(setWhiteBackground()));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:542: d->actionSetWhiteBackground->setChecked(backgroundColor == Qt::white);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:544: !d->actionSetWhiteBackground->isChecked());`
- Connected slots/functions: `setWhiteBackground`
- API footprints: `GetRenderMode`, `vtkMRMLViewNode::Orthographic`
- Key UI properties: {"checkable": "true"}

## action: actionCenter

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Center | Center view | actionCenter
- Text: Center
- Tooltip: Center view
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:97: this->CenterButton->setDefaultAction(this->actionCenter);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:98: QObject::connect(this->actionCenter, SIGNAL(triggered()), q, SLOT(resetFocalPoint()));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:342: this->CenterToolButton->setDefaultAction(this->actionCenter);`
- Connected slots/functions: `resetFocalPoint`
- API footprints: `EndCameraNodeInteraction`, `StartCameraNodeInteraction`, `vtkMRMLCameraNode::CenterFlag`

## action: actionUseDepthPeeling

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Use depth peeling | Depth peeling is used to render transparent surface models in order | actionUseDepthPeeling
- Text: Use depth peeling
- Tooltip: Depth peeling is used to render transparent surface models in order
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:183: moreMenu->addAction(this->actionUseDepthPeeling);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:189: QObject::connect(this->actionUseDepthPeeling, SIGNAL(toggled(bool)), q, SLOT(setUseDepthPeeling(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:536: d->actionUseDepthPeeling->setChecked(viewNode->GetUseDepthPeeling());`
- Connected slots/functions: `setUseDepthPeeling`
- API footprints: `EndViewNodeInteraction`, `GetAxisLabelsVisible`, `GetFPSVisible`, `GetUseDepthPeeling`, `SetUseDepthPeeling`, `StartViewNodeInteraction`, `vtkMRMLViewNode::UseDepthPeelingFlag`
- Key UI properties: {"checkable": "true"}

## action: actionSetFPSVisible

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Show/Hide frames per second (FPS) | actionSetFPSVisible
- Text: Show/Hide frames per second (FPS)
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:185: moreMenu->addAction(this->actionSetFPSVisible);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:220: QObject::connect(this->actionSetFPSVisible, SIGNAL(toggled(bool)), q, SLOT(setFPSVisible(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:537: d->actionSetFPSVisible->setChecked(viewNode->GetFPSVisible());`
- Connected slots/functions: `setFPSVisible`
- API footprints: `EndViewNodeInteraction`, `GetBackgroundColor`, `GetFPSVisible`, `GetUseDepthPeeling`, `SetFPSVisible`, `StartViewNodeInteraction`, `vtkMRMLViewNode::FPSVisibleFlag`
- Key UI properties: {"checkable": "true"}

## action: actionSwitchToUserDefinedStereo_1

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: User Defined 1 | Switch to user defined stereo mode 1 | actionSwitchToUserDefinedStereo_1
- Text: User Defined 1
- Tooltip: Switch to user defined stereo mode 1
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:198: this->StereoTypesMapper->setMapping(this->actionSwitchToUserDefinedStereo_1, vtkMRMLViewNode::UserDefined_1);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:208: stereoTypesActions->addAction(this->actionSwitchToUserDefinedStereo_1);`
- API footprints: `vtkMRMLViewNode::Interlaced`, `vtkMRMLViewNode::RedBlue`, `vtkMRMLViewNode::UserDefined_1`, `vtkMRMLViewNode::UserDefined_2`, `vtkMRMLViewNode::UserDefined_3`
- Key UI properties: {"checkable": "true"}

## action: actionSwitchToUserDefinedStereo_2

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: User Defined 2 | Switch to user defined stereo mode 2 | actionSwitchToUserDefinedStereo_2
- Text: User Defined 2
- Tooltip: Switch to user defined stereo mode 2
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:199: this->StereoTypesMapper->setMapping(this->actionSwitchToUserDefinedStereo_2, vtkMRMLViewNode::UserDefined_2);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:209: stereoTypesActions->addAction(this->actionSwitchToUserDefinedStereo_2);`
- API footprints: `vtkMRMLViewNode::RedBlue`, `vtkMRMLViewNode::UserDefined_1`, `vtkMRMLViewNode::UserDefined_2`, `vtkMRMLViewNode::UserDefined_3`
- Key UI properties: {"checkable": "true"}

## action: actionSwitchToUserDefinedStereo_3

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: User Defined 3 | Switch to user defined stereo mode 3 | actionSwitchToUserDefinedStereo_3
- Text: User Defined 3
- Tooltip: Switch to user defined stereo mode 3
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:200: this->StereoTypesMapper->setMapping(this->actionSwitchToUserDefinedStereo_3, vtkMRMLViewNode::UserDefined_3);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:210: stereoTypesActions->addAction(this->actionSwitchToUserDefinedStereo_3);`
- API footprints: `vtkMRMLViewNode::UserDefined_1`, `vtkMRMLViewNode::UserDefined_2`, `vtkMRMLViewNode::UserDefined_3`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeNone

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: No orientation marker | Hide orientation marker | actionOrientationMarkerTypeNone
- Text: No orientation marker
- Tooltip: Hide orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:115: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeNone, vtkMRMLAbstractViewNode::OrientationMarkerTypeNone);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:121: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeNone);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeNone`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeCube

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Cube | Show cube orientation marker | actionOrientationMarkerTypeCube
- Text: Cube
- Tooltip: Show cube orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:116: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeCube, vtkMRMLAbstractViewNode::OrientationMarkerTypeCube);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:122: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeCube);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeNone`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeHuman

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Human | Show human-shaped orientation marker | actionOrientationMarkerTypeHuman
- Text: Human
- Tooltip: Show human-shaped orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:117: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeHuman, vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:123: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeHuman);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeNone`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerTypeAxes

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Axes | Show axes orientation marker | actionOrientationMarkerTypeAxes
- Text: Axes
- Tooltip: Show axes orientation marker
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:118: this->OrientationMarkerTypesMapper->setMapping(this->actionOrientationMarkerTypeAxes, vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:124: orientationMarkerTypesActions->addAction(this->actionOrientationMarkerTypeAxes);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerTypeAxes`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeCube`, `vtkMRMLAbstractViewNode::OrientationMarkerTypeHuman`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerSizeSmall

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Small | Small orientation marker size | actionOrientationMarkerSizeSmall
- Text: Small
- Tooltip: Small orientation marker size
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:129: this->OrientationMarkerSizesMapper->setMapping(this->actionOrientationMarkerSizeSmall, vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:134: orientationMarkerSizesActions->addAction(this->actionOrientationMarkerSizeSmall);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerSizeMedium

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Medium | Medium orientation marker size | actionOrientationMarkerSizeMedium
- Text: Medium
- Tooltip: Medium orientation marker size
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:130: this->OrientationMarkerSizesMapper->setMapping(this->actionOrientationMarkerSizeMedium, vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:135: orientationMarkerSizesActions->addAction(this->actionOrientationMarkerSizeMedium);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall`
- Key UI properties: {"checkable": "true"}

## action: actionOrientationMarkerSizeLarge

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Large | Large orientation marker size | actionOrientationMarkerSizeLarge
- Text: Large
- Tooltip: Large orientation marker size
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:131: this->OrientationMarkerSizesMapper->setMapping(this->actionOrientationMarkerSizeLarge, vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:136: orientationMarkerSizesActions->addAction(this->actionOrientationMarkerSizeLarge);`
- API footprints: `vtkMRMLAbstractViewNode::OrientationMarkerSizeLarge`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeMedium`, `vtkMRMLAbstractViewNode::OrientationMarkerSizeSmall`
- Key UI properties: {"checkable": "true"}

## action: actionRulerTypeNone

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: No ruler | Hide ruler | actionRulerTypeNone
- Text: No ruler
- Tooltip: Hide ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:150: this->RulerTypesMapper->setMapping(this->actionRulerTypeNone, vtkMRMLAbstractViewNode::RulerTypeNone);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:155: rulerTypesActions->addAction(this->actionRulerTypeNone);`
- API footprints: `vtkMRMLAbstractViewNode::RulerTypeNone`, `vtkMRMLAbstractViewNode::RulerTypeThick`, `vtkMRMLAbstractViewNode::RulerTypeThin`
- Key UI properties: {"checkable": "true"}

## action: actionRulerTypeThin

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Thin | Show thin ruler | actionRulerTypeThin
- Text: Thin
- Tooltip: Show thin ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:151: this->RulerTypesMapper->setMapping(this->actionRulerTypeThin, vtkMRMLAbstractViewNode::RulerTypeThin);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:156: rulerTypesActions->addAction(this->actionRulerTypeThin);`
- API footprints: `vtkMRMLAbstractViewNode::RulerTypeNone`, `vtkMRMLAbstractViewNode::RulerTypeThick`, `vtkMRMLAbstractViewNode::RulerTypeThin`
- Key UI properties: {"checkable": "true"}

## action: actionRulerTypeThick

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Thick | Show thick ruler | actionRulerTypeThick
- Text: Thick
- Tooltip: Show thick ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:152: this->RulerTypesMapper->setMapping(this->actionRulerTypeThick, vtkMRMLAbstractViewNode::RulerTypeThick);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:157: rulerTypesActions->addAction(this->actionRulerTypeThick);`
- API footprints: `vtkMRMLAbstractViewNode::RulerTypeNone`, `vtkMRMLAbstractViewNode::RulerTypeThick`, `vtkMRMLAbstractViewNode::RulerTypeThin`
- Key UI properties: {"checkable": "true"}

## action: actionRulerColorWhite

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: White ruler | actionRulerColorWhite
- Text: White ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:162: this->RulerColorMapper->setMapping(this->actionRulerColorWhite, vtkMRMLAbstractViewNode::RulerColorWhite);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:167: rulerColorActions->addAction(this->actionRulerColorWhite);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerColorWhite`, `vtkMRMLAbstractViewNode::RulerColorYellow`
- Key UI properties: {"checkable": "true"}

## action: actionRulerColorBlack

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Black ruler | actionRulerColorBlack
- Text: Black ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:163: this->RulerColorMapper->setMapping(this->actionRulerColorBlack, vtkMRMLAbstractViewNode::RulerColorBlack);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:168: rulerColorActions->addAction(this->actionRulerColorBlack);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerColorWhite`, `vtkMRMLAbstractViewNode::RulerColorYellow`
- Key UI properties: {"checkable": "true"}

## action: actionRulerColorYellow

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Yellow ruler | actionRulerColorYellow
- Text: Yellow ruler
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:164: this->RulerColorMapper->setMapping(this->actionRulerColorYellow, vtkMRMLAbstractViewNode::RulerColorYellow);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:169: rulerColorActions->addAction(this->actionRulerColorYellow);`
- API footprints: `vtkMRMLAbstractViewNode::RulerColorBlack`, `vtkMRMLAbstractViewNode::RulerColorWhite`, `vtkMRMLAbstractViewNode::RulerColorYellow`
- Key UI properties: {"checkable": "true"}

## action: actionStereo

- Confidence: `linked_to_code`
- Widget/action class: `action`
- Search text: Stereo viewing | Select stereo viewing mode | actionStereo
- Text: Stereo viewing
- Tooltip: Select stereo viewing mode
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:184: moreMenu->addAction(this->actionStereo);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:214: this->actionStereo->setMenu(stereoTypesMenu);`

## action: actionShadowsVisibility

- Confidence: `linked_to_api`
- Widget/action class: `action`
- Search text: Shadows visibility | Make objects cast shadows to improve depth perception | actionShadowsVisibility
- Text: Shadows visibility
- Tooltip: Make objects cast shadows to improve depth perception
- Implementation candidates: `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.h`, `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget_p.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:251: this->ShadowsMenu->addAction(this->actionShadowsVisibility);`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:253: QObject::connect(this->actionShadowsVisibility, SIGNAL(toggled(bool)), q, SLOT(setShadowsVisibility(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:267: this->connect(this->actionShadowsVisibility, SIGNAL(toggled(bool)), this->AmbientShadowsSizeScaleSlider, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:284: this->connect(this->actionShadowsVisibility, SIGNAL(toggled(bool)), this->AmbientShadowsVolumeOpacityThresholdPercentSlider, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:302: this->connect(this->actionShadowsVisibility, SIGNAL(toggled(bool)), this->AmbientShadowsIntensityScaleSlider, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:320: this->connect(this->actionShadowsVisibility, SIGNAL(toggled(bool)), this->AmbientShadowsIntensityShiftSlider, SLOT(setEnabled(bool)));`
  - `Libs/MRML/Widgets/qMRMLThreeDViewControllerWidget.cxx:579: d->actionShadowsVisibility->setChecked(viewNode->GetShadowsVisibility());`
- Connected slots/functions: `setEnabled`, `setShadowsVisibility`
- API footprints: `EndViewNodeInteraction`, `GetAmbientShadowsSizeScale`, `GetAmbientShadowsVolumeOpacityThreshold`, `GetShadowsVisibility`, `SetShadowsVisibility`, `StartViewNodeInteraction`, `vtkMRMLViewNode::ShadowsVisibilityFlag`
- Key UI properties: {"checkable": "true"}
