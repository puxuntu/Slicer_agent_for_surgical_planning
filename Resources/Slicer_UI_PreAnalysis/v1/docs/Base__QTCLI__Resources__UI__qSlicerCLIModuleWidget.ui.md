# Slicer UI Analysis: Base/QTCLI/Resources/UI/qSlicerCLIModuleWidget.ui

- Owner class: `qSlicerCLIModuleWidget`
- UI file: `Base/QTCLI/Resources/UI/qSlicerCLIModuleWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerCLIModuleWidget

- Confidence: `linked_to_api`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerCLIModuleWidget | qSlicerWidget
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:30: #include "qSlicerCLIModuleWidget_p.h"`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:38: // qSlicerCLIModuleWidgetPrivate methods`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:41: qSlicerCLIModuleWidgetPrivate::qSlicerCLIModuleWidgetPrivate(qSlicerCLIModuleWidget& object)`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:53: vtkSlicerCLIModuleLogic* qSlicerCLIModuleWidgetPrivate::logic() const`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:55: Q_Q(const qSlicerCLIModuleWidget);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:60: vtkMRMLCommandLineModuleNode* qSlicerCLIModuleWidgetPrivate::commandLineModuleNode() const`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:66: qSlicerCLIModule* qSlicerCLIModuleWidgetPrivate::module() const`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:68: Q_Q(const qSlicerCLIModuleWidget);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:74: void qSlicerCLIModuleWidgetPrivate::setupUi(qSlicerWidget* widget)`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:76: Q_Q(qSlicerCLIModuleWidget);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:78: this->Ui_qSlicerCLIModuleWidget::setupUi(widget);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:94: QMenu* autoRunMenu = new QMenu(qSlicerCLIModuleWidget::tr("AutoRun"), this->AutoRunPushButton);`
- API footprints: `GetAutoRunMode`, `GetDefaultModuleDescription`, `GetTitle`, `SetAutoRun`, `vtkMRMLCommandLineModuleNode::SafeDownCast`

## widget: scrollArea

- Confidence: `ui_only`
- Widget/action class: `QScrollArea`
- Search text: scrollArea | QScrollArea
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`

## widget: scrollAreaWidgetContents

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: scrollAreaWidgetContents | QWidget
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`

## widget: ModuleCollapsibleButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkCollapsibleButton`
- Search text: Module Title | ModuleCollapsibleButton | ctkCollapsibleButton
- Text: Module Title
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:81: this->ModuleCollapsibleButton->setText(title);`
- API footprints: `GetDefaultModuleDescription`, `GetTitle`

## widget: MRMLCommandLineModuleNodeSelector

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: MRMLCommandLineModuleNodeSelector | qMRMLNodeComboBox
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:62: return vtkMRMLCommandLineModuleNode::SafeDownCast(this->MRMLCommandLineModuleNodeSelector->currentNode());`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:83: this->MRMLCommandLineModuleNodeSelector->setBaseName(title);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:87: this->MRMLCommandLineModuleNodeSelector->addAttribute("vtkMRMLCommandLineModuleNode", "CommandLineModule", sourceLanguageTitle);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:89: this->MRMLCommandLineModuleNodeSelector->setNodeTypeLabel(tr("Parameter set"), "vtkMRMLCommandLineModuleNode");`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:136: this->connect(this->MRMLCommandLineModuleNodeSelector, SIGNAL(currentNodeChanged(vtkMRMLNode*)), q, SLOT(setCurrentCommandLineModuleNode(vtkMRMLNode*)));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:138: this->connect(this->MRMLCommandLineModuleNodeSelector, SIGNAL(nodeAddedByUser(vtkMRMLNode*)), SLOT(setDefaultNodeValue(vtkMRMLNode*)));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:140: // Scene must be set in node selector widgets before the MRMLCommandLineModuleNodeSelector widget`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:141: // because when the scene is set in MRMLCommandLineModuleNodeSelector the first available module node`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:144: // we set the scene here for all widgets, before MRMLCommandLineModuleNodeSelector has a chance to trigger`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:145: // an update. Scene in MRMLCommandLineModuleNodeSelector will be set later by qSlicerAbstractCoreModule.`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:147: this->connect(q, SIGNAL(mrmlSceneChanged(vtkMRMLScene*)), this->MRMLCommandLineModuleNodeSelector, SLOT(setMRMLScene(vtkMRMLScene*)));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:299: this->MRMLCommandLineModuleNodeSelector->addNode();`
- Connected slots/functions: `setCurrentCommandLineModuleNode`, `setDefaultNodeValue`, `setMRMLScene`
- API footprints: `GetDefaultModuleDescription`, `GetTitle`, `SetModuleDescription`, `vtkMRMLCommandLineModuleNode::SafeDownCast`
- Key UI properties: {"nodeTypes": ["vtkMRMLCommandLineModuleNode"]}

## widget: ParameterSetLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Parameter set: | ParameterSetLabel | QLabel
- Text: Parameter set:
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`

## widget: widget_2

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: widget_2 | QWidget
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`

## widget: CLIProgressBar

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerCLIProgressBar`
- Search text: CLIProgressBar | qSlicerCLIProgressBar
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:389: d->CLIProgressBar->setCommandLineModuleNode(d->CommandLineModuleNode);`

## widget: DefaultPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Restore Defaults | Reset parameters to default. | DefaultPushButton | QPushButton
- Text: Restore Defaults
- Tooltip: Reset parameters to default.
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:132: this->connect(this->DefaultPushButton, SIGNAL(clicked()), q, SLOT(reset()));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:158: this->DefaultPushButton->setEnabled(false);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:176: this->DefaultPushButton->setEnabled(!node->IsBusy());`
- Connected slots/functions: `reset`
- API footprints: `IsBusy`

## widget: AutoRunPushButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkMenuButton`
- Search text: AutoRun | AutoRunPushButton | ctkMenuButton
- Text: AutoRun
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:94: QMenu* autoRunMenu = new QMenu(qSlicerCLIModuleWidget::tr("AutoRun"), this->AutoRunPushButton);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:125: this->AutoRunPushButton->setMenu(autoRunMenu);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:134: this->connect(this->AutoRunPushButton, SIGNAL(toggled(bool)), q, SLOT(setAutoRun(bool)));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:153: this->AutoRunPushButton->setEnabled(commandLineModuleNode != nullptr);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:183: if (this->AutoRunPushButton->isChecked() != node->GetAutoRun())`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:185: this->AutoRunPushButton->setChecked(node->GetAutoRun());`
- Connected slots/functions: `setAutoRun`
- API footprints: `GetAutoRun`, `GetAutoRunMode`, `SetAutoRun`, `vtkMRMLCommandLineModuleNode::AutoRunCancelsRunningProcess`, `vtkMRMLCommandLineModuleNode::AutoRunOnOtherInputEvents`
- Key UI properties: {"checkable": "true"}

## widget: CancelPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Cancel | Cancel the execution of the module | CancelPushButton | QPushButton
- Text: Cancel
- Tooltip: Cancel the execution of the module
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:130: this->connect(this->CancelPushButton, SIGNAL(clicked()), q, SLOT(cancel()));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:157: this->CancelPushButton->setEnabled(false);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:177: this->CancelPushButton->setEnabled(node->IsBusy());`
- Connected slots/functions: `cancel`
- API footprints: `GetAutoRunMode`, `IsBusy`, `vtkMRMLCommandLineModuleNode::AutoRunOnChangedParameter`

## widget: ApplyPushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Apply | Execute the module | ApplyPushButton | QPushButton
- Text: Apply
- Tooltip: Execute the module
- Implementation candidates: `Base/QTCLI/qSlicerCLIModuleWidget.cxx`, `Base/QTCLI/qSlicerCLIModuleWidget.h`, `Base/QTCLI/qSlicerCLIModuleWidget_p.h`
- Matched implementation lines:
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:128: this->connect(this->ApplyPushButton, SIGNAL(clicked()), q, SLOT(apply()));`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:156: this->ApplyPushButton->setEnabled(false);`
  - `Base/QTCLI/qSlicerCLIModuleWidget.cxx:175: this->ApplyPushButton->setEnabled(!node->IsBusy());`
- Connected slots/functions: `apply`
- API footprints: `IsBusy`
