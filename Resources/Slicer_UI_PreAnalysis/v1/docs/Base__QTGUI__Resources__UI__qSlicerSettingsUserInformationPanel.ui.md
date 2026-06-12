# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsUserInformationPanel.ui

- Owner class: `qSlicerSettingsUserInformationPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsUserInformationPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsUserInformationPanel

- Confidence: `linked_to_api`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsUserInformationPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:12: #include "qSlicerSettingsUserInformationPanel.h"`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:13: #include "ui_qSlicerSettingsUserInformationPanel.h"`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:23: // qSlicerSettingsUserInformationPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:26: class qSlicerSettingsUserInformationPanelPrivate : public Ui_qSlicerSettingsUserInformationPanel`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:28: Q_DECLARE_PUBLIC(qSlicerSettingsUserInformationPanel);`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:31: qSlicerSettingsUserInformationPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:34: qSlicerSettingsUserInformationPanelPrivate(qSlicerSettingsUserInformationPanel& object);`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:41: // qSlicerSettingsUserInformationPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:44: qSlicerSettingsUserInformationPanelPrivate::qSlicerSettingsUserInformationPanelPrivate(qSlicerSettingsUserInformationPanel& object)`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:51: void qSlicerSettingsUserInformationPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:53: Q_Q(qSlicerSettingsUserInformationPanel);`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:67: // qSlicerSettingsUserInformationPanel methods`
- API footprints: `GetAsString`, `SetEmail`, `SetFromString`, `SetLogin`, `SetName`, `SetOrganization`, `SetOrganizationRole`, `SetProcedureRole`

## widget: ProcedureRoleLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: ProcedureRoleLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:63: QObject::connect(this->ProcedureRoleLineEdit, SIGNAL(editingFinished()), q, SLOT(onProcedureRoleChanged()));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:113: d->ProcedureRoleLineEdit->setText(d->UserInformation->GetProcedureRole().c_str());`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:187: d->UserInformation->SetProcedureRole(d->ProcedureRoleLineEdit->text().toStdString().c_str());`
- Connected slots/functions: `onProcedureRoleChanged`
- API footprints: `GetOrganization`, `GetOrganizationRole`, `GetProcedureRole`, `SetProcedureRole`

## widget: OrganizationRoleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Organization role: | OrganizationRoleLabel | QLabel
- Text: Organization role:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`

## widget: LoginLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: LoginLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:59: QObject::connect(this->LoginLineEdit, SIGNAL(editingFinished()), q, SLOT(onLoginChanged()));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:109: d->LoginLineEdit->setText(d->UserInformation->GetLogin().c_str());`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:152: d->UserInformation->SetLogin(d->LoginLineEdit->text().toStdString().c_str());`
- Connected slots/functions: `onLoginChanged`
- API footprints: `GetEmail`, `GetLogin`, `GetName`, `GetOrganization`, `SetLogin`

## widget: LoginLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Login: | LoginLabel | QLabel
- Text: Login:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`

## widget: OrganizationRoleLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: OrganizationRoleLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:62: QObject::connect(this->OrganizationRoleLineEdit, SIGNAL(editingFinished()), q, SLOT(onOrganizationRoleChanged()));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:112: d->OrganizationRoleLineEdit->setText(d->UserInformation->GetOrganizationRole().c_str());`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:180: d->UserInformation->SetOrganizationRole(d->OrganizationRoleLineEdit->text().toStdString().c_str());`
- Connected slots/functions: `onOrganizationRoleChanged`
- API footprints: `GetEmail`, `GetOrganization`, `GetOrganizationRole`, `GetProcedureRole`, `SetOrganizationRole`

## widget: NameLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Name: | Directory where scenes are saved to by default | NameLabel | QLabel
- Text: Name:
- Tooltip: Directory where scenes are saved to by default
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`

## widget: OrganizationLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: OrganizationLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:61: QObject::connect(this->OrganizationLineEdit, SIGNAL(editingFinished()), q, SLOT(onOrganizationChanged()));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:111: d->OrganizationLineEdit->setText(d->UserInformation->GetOrganization().c_str());`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:173: d->UserInformation->SetOrganization(d->OrganizationLineEdit->text().toStdString().c_str());`
- Connected slots/functions: `onOrganizationChanged`
- API footprints: `GetEmail`, `GetLogin`, `GetOrganization`, `GetOrganizationRole`, `GetProcedureRole`, `SetOrganization`

## widget: ProcedureRoleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Procedure role: | ProcedureRoleLabel | QLabel
- Text: Procedure role:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`

## widget: OrganizationLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Organization: | OrganizationLabel | QLabel
- Text: Organization:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`

## widget: EmailLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: EmailLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:60: QObject::connect(this->EmailLineEdit, SIGNAL(textChanged(QString)), q, SLOT(onEmailChanged(QString)));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:110: d->EmailLineEdit->setText(d->UserInformation->GetEmail().c_str());`
- Connected slots/functions: `onEmailChanged`
- API footprints: `GetEmail`, `GetLogin`, `GetName`, `GetOrganization`, `GetOrganizationRole`, `SetEmail`

## widget: NameLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: NameLineEdit | QLineEdit
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:58: QObject::connect(this->NameLineEdit, SIGNAL(editingFinished()), q, SLOT(onNameChanged()));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:108: d->NameLineEdit->setText(d->UserInformation->GetName().c_str());`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:145: d->UserInformation->SetName(d->NameLineEdit->text().toStdString().c_str());`
- Connected slots/functions: `onNameChanged`
- API footprints: `GetEmail`, `GetLogin`, `GetName`, `SetName`

## widget: EmailLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Email: | Python script that is executed after the application is started | EmailLabel | QLabel
- Text: Email:
- Tooltip: Python script that is executed after the application is started
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`

## widget: EmailValidationLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: EmailValidationLabel | QLabel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx`, `Base/QTGUI/qSlicerSettingsUserInformationPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:138: d->EmailValidationLabel->setText("");`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:161: d->EmailValidationLabel->setText(tr("Invalid format"));`
  - `Base/QTGUI/qSlicerSettingsUserInformationPanel.cxx:165: d->EmailValidationLabel->setText("");`
- API footprints: `SetEmail`
