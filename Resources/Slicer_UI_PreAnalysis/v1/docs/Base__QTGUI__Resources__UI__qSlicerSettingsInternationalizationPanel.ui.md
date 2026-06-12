# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsInternationalizationPanel.ui

- Owner class: `qSlicerSettingsInternationalizationPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsInternationalizationPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsInternationalizationPanel

- Confidence: `linked_to_code`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsInternationalizationPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx`, `Base/QTGUI/qSlicerSettingsInternationalizationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:26: #include "qSlicerSettingsInternationalizationPanel.h"`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:27: #include "ui_qSlicerSettingsInternationalizationPanel.h"`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:30: // qSlicerSettingsInternationalizationPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:33: class qSlicerSettingsInternationalizationPanelPrivate : public Ui_qSlicerSettingsInternationalizationPanel`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:35: Q_DECLARE_PUBLIC(qSlicerSettingsInternationalizationPanel);`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:38: qSlicerSettingsInternationalizationPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:41: qSlicerSettingsInternationalizationPanelPrivate(qSlicerSettingsInternationalizationPanel& object);`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:46: // qSlicerSettingsInternationalizationPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:49: qSlicerSettingsInternationalizationPanelPrivate::qSlicerSettingsInternationalizationPanelPrivate(qSlicerSettingsInternationalizationPanel& object)`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:55: void qSlicerSettingsInternationalizationPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:57: Q_Q(qSlicerSettingsInternationalizationPanel);`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:69: qSlicerSettingsInternationalizationPanel::tr("Enable/Disable Internationalization"),`

## widget: InternationalizationEnabledLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable Internationalization: | InternationalizationEnabledLabel | QLabel
- Text: Enable Internationalization:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx`, `Base/QTGUI/qSlicerSettingsInternationalizationPanel.h`

## widget: InternationalizationEnabledCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: InternationalizationEnabledCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx`, `Base/QTGUI/qSlicerSettingsInternationalizationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:62: this->InternationalizationEnabledCheckBox->setChecked(false);`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:66: this->InternationalizationEnabledCheckBox,`
  - `Base/QTGUI/qSlicerSettingsInternationalizationPanel.cxx:73: QObject::connect(this->InternationalizationEnabledCheckBox, SIGNAL(toggled(bool)), q, SLOT(enableInternationalization(bool)));`
- Connected slots/functions: `enableInternationalization`
