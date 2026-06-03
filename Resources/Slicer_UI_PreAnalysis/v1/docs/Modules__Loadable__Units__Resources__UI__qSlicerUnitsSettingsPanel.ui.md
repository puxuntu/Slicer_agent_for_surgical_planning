# Slicer UI Analysis: Modules/Loadable/Units/Resources/UI/qSlicerUnitsSettingsPanel.ui

- Owner class: `qSlicerUnitsSettingsPanel`
- UI file: `Modules/Loadable/Units/Resources/UI/qSlicerUnitsSettingsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerUnitsSettingsPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerUnitsSettingsPanel | ctkSettingsPanel
- Implementation candidates: `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx`, `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:37: #include "qSlicerUnitsSettingsPanel.h"`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:38: #include "ui_qSlicerUnitsSettingsPanel.h"`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:51: // qSlicerUnitsSettingsPanelPrivate`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:54: class qSlicerUnitsSettingsPanelPrivate : public Ui_qSlicerUnitsSettingsPanel`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:56: Q_DECLARE_PUBLIC(qSlicerUnitsSettingsPanel);`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:59: qSlicerUnitsSettingsPanel* const q_ptr;`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:62: qSlicerUnitsSettingsPanelPrivate(qSlicerUnitsSettingsPanel& object);`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:78: // qSlicerUnitsSettingsPanelPrivate methods`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:81: qSlicerUnitsSettingsPanelPrivate::qSlicerUnitsSettingsPanelPrivate(qSlicerUnitsSettingsPanel& object)`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:90: void qSlicerUnitsSettingsPanelPrivate::init()`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:92: Q_Q(qSlicerUnitsSettingsPanel);`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:101: void qSlicerUnitsSettingsPanelPrivate::registerProperties(QString quantity, qMRMLSettingsUnitWidget* unitWidget)`

## widget: WarningLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#ff0000;">Warning:</span> Changing the properties of the unit only change the display, not the value !</p></body></html> | WarningLabel | QLabel
- Text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#ff0000;">Warning:</span> Changing the properties of the unit only change the display, not the value !</p></body></html>
- Implementation candidates: `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx`, `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.h`

## widget: ShowAllCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Show advanced options | Show all the units' properties.
This should only used by advanced users who understand the consequences of changing a unit's property. | ShowAllCheckBox | QCheckBox
- Text: Show advanced options
- Tooltip: Show all the units' properties.
This should only used by advanced users who understand the consequences of changing a unit's property.
- Implementation candidates: `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx`, `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:96: q->connect(this->ShowAllCheckBox, SIGNAL(toggled(bool)), q, SLOT(showAll(bool)));`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:97: this->ShowAllCheckBox->setChecked(false);`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:158: unitWidget->unitWidget()->setDisplayedProperties(this->ShowAllCheckBox->isChecked() ? qMRMLUnitWidget::All : qMRMLUnitWidget::Precision);`
- Connected slots/functions: `showAll`
- Key UI properties: {"checked": "true"}

## widget: scrollArea

- Confidence: `linked_to_code`
- Widget/action class: `QScrollArea`
- Search text: scrollArea | QScrollArea
- Implementation candidates: `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx`, `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:228: this->scrollArea->setMinimumSize(QSize(0, 700));`
  - `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx:232: this->scrollArea->setMinimumSize(QSize(0, 350));`

## widget: scrollAreaWidgetContents

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: scrollAreaWidgetContents | QWidget
- Implementation candidates: `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.cxx`, `Modules/Loadable/Units/qSlicerUnitsSettingsPanel.h`
