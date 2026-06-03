# Slicer UI Analysis: Modules/Loadable/Units/Widgets/Resources/UI/qMRMLSettingsUnitWidget.ui

- Owner class: `qMRMLSettingsUnitWidget`
- UI file: `Modules/Loadable/Units/Widgets/Resources/UI/qMRMLSettingsUnitWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qMRMLSettingsUnitWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qMRMLSettingsUnitWidget | QWidget
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:32: #include "qMRMLSettingsUnitWidget.h"`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:34: #include "ui_qMRMLSettingsUnitWidget.h"`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:46: class qMRMLSettingsUnitWidgetPrivate : public Ui_qMRMLSettingsUnitWidget`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:48: Q_DECLARE_PUBLIC(qMRMLSettingsUnitWidget);`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:51: qMRMLSettingsUnitWidget* const q_ptr;`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:54: qMRMLSettingsUnitWidgetPrivate(qMRMLSettingsUnitWidget& obj);`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:55: void setupUi(qMRMLSettingsUnitWidget*);`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:61: // qMRMLSettingsUnitWidgetPrivate methods`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:64: qMRMLSettingsUnitWidgetPrivate::qMRMLSettingsUnitWidgetPrivate(qMRMLSettingsUnitWidget& object)`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:71: void qMRMLSettingsUnitWidgetPrivate::setupUi(qMRMLSettingsUnitWidget* q)`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:73: this->Ui_qMRMLSettingsUnitWidget::setupUi(q);`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:83: // qMRMLSettingsUnitWidget methods`

## widget: UnitLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Unit: | UnitLabel | QLabel
- Text: Unit:
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:78: this->UnitLabel->setVisible(false);`

## widget: UnitNodeComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `qMRMLNodeComboBox`
- Search text: Select the current unit node to modify. | UnitNodeComboBox | qMRMLNodeComboBox
- Tooltip: Select the current unit node to modify.
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:75: QObject::connect(this->UnitNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this->UnitInfoWidget, SLOT(setCurrentNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:79: this->UnitNodeComboBox->setVisible(false);`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:114: return d->UnitNodeComboBox;`
- Connected slots/functions: `setCurrentNode`
- Key UI properties: {"nodeTypes": ["vtkMRMLUnitNode"]}

## widget: UnitInfoWidget

- Confidence: `linked_to_api`
- Widget/action class: `qMRMLUnitWidget`
- Search text: UnitInfoWidget | qMRMLUnitWidget
- Implementation candidates: `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx`, `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:75: QObject::connect(this->UnitNodeComboBox, SIGNAL(currentNodeChanged(vtkMRMLNode*)), this->UnitInfoWidget, SLOT(setCurrentNode(vtkMRMLNode*)));`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:107: d->UnitInfoWidget->setMRMLScene(d->Logic ? d->Logic->GetUnitsScene() : nullptr);`
  - `Modules/Loadable/Units/Widgets/qMRMLSettingsUnitWidget.cxx:121: return d->UnitInfoWidget;`
- Connected slots/functions: `setCurrentNode`
- API footprints: `GetUnitsScene`
