# Slicer UI Analysis: Modules/Loadable/Colors/Widgets/Resources/UI/qSlicerTerminologyEditorWidget.ui

- Owner class: `qSlicerTerminologyEditorWidget`
- UI file: `Modules/Loadable/Colors/Widgets/Resources/UI/qSlicerTerminologyEditorWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTerminologyEditorWidget

- Confidence: `linked_to_code`
- Widget/action class: `QWidget`
- Search text: qSlicerTerminologyEditorWidget | QWidget
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:22: #include "qSlicerTerminologyEditorWidget.h"`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:23: #include "ui_qSlicerTerminologyEditorWidget.h"`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:29: class qSlicerTerminologyEditorWidgetPrivate : public Ui_qSlicerTerminologyEditorWidget`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:31: Q_DECLARE_PUBLIC(qSlicerTerminologyEditorWidget);`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:34: qSlicerTerminologyEditorWidget* const q_ptr;`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:37: qSlicerTerminologyEditorWidgetPrivate(qSlicerTerminologyEditorWidget& object);`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:52: qSlicerTerminologyEditorWidgetPrivate::qSlicerTerminologyEditorWidgetPrivate(qSlicerTerminologyEditorWidget& object)`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:58: void qSlicerTerminologyEditorWidgetPrivate::init()`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:60: Q_Q(qSlicerTerminologyEditorWidget);`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:71: void qSlicerTerminologyEditorWidgetPrivate::updateGUIFromTerminologyInfo()`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:73: Q_Q(qSlicerTerminologyEditorWidget);`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:106: void qSlicerTerminologyEditorWidgetPrivate::updateTerminologyFromGUI()`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Value | label_3 | QLabel
- Text: Value
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Scheme | label_2 | QLabel
- Text: Scheme
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: label_7

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Region: | label_7 | QLabel
- Text: Region:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: typeModifierCodeMeaningLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: typeModifierCodeMeaningLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:84: this->typeModifierCodeMeaningLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetTypeModifierObject()->GetCodeMeaning());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:119: TerminologyInfo.GetTerminologyEntry()->GetTypeModifierObject()->SetCodeMeaning(this->typeModifierCodeMeaningLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `GetTypeModifierObject`, `GetTypeObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: typeModifierCSDLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: typeModifierCSDLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:86: this->typeModifierCSDLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetTypeModifierObject()->GetCodingSchemeDesignator());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:121: TerminologyInfo.GetTerminologyEntry()->GetTypeModifierObject()->SetCodingSchemeDesignator(this->typeModifierCSDLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionObject`, `GetTerminologyEntry`, `GetTypeModifierObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: categoryCodeMeaningLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: categoryCodeMeaningLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:76: this->categoryCodeMeaningLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetCategoryObject()->GetCodeMeaning());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:111: TerminologyInfo.GetTerminologyEntry()->GetCategoryObject()->SetCodeMeaning(this->categoryCodeMeaningLineEdit->text().toStdString().c_str());`
- API footprints: `GetCategoryObject`, `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: label_6

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text:     Modifier: | label_6 | QLabel
- Text:     Modifier:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: label_4

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Category: | label_4 | QLabel
- Text: Category:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: categoryCSDLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: categoryCSDLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:78: this->categoryCSDLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetCategoryObject()->GetCodingSchemeDesignator());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:113: TerminologyInfo.GetTerminologyEntry()->GetCategoryObject()->SetCodingSchemeDesignator(this->categoryCSDLineEdit->text().toStdString().c_str());`
- API footprints: `GetCategoryObject`, `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `GetTypeObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: label_5

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Type: | label_5 | QLabel
- Text: Type:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: typeCSDLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: typeCSDLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:82: this->typeCSDLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetTypeObject()->GetCodingSchemeDesignator());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:117: TerminologyInfo.GetTerminologyEntry()->GetTypeObject()->SetCodingSchemeDesignator(this->typeCSDLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `GetTypeModifierObject`, `GetTypeObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: categoryCodeValueLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: categoryCodeValueLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:77: this->categoryCodeValueLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetCategoryObject()->GetCodeValue());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:112: TerminologyInfo.GetTerminologyEntry()->GetCategoryObject()->SetCodeValue(this->categoryCodeValueLineEdit->text().toStdString().c_str());`
- API footprints: `GetCategoryObject`, `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: typeCodeMeaningLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: typeCodeMeaningLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:80: this->typeCodeMeaningLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetTypeObject()->GetCodeMeaning());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:115: TerminologyInfo.GetTerminologyEntry()->GetTypeObject()->SetCodeMeaning(this->typeCodeMeaningLineEdit->text().toStdString().c_str());`
- API footprints: `GetCategoryObject`, `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `GetTypeObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: typeCodeValueLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: typeCodeValueLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:81: this->typeCodeValueLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetTypeObject()->GetCodeValue());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:116: TerminologyInfo.GetTerminologyEntry()->GetTypeObject()->SetCodeValue(this->typeCodeValueLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `GetTypeObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: typeModifierCodeValueLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: typeModifierCodeValueLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:85: this->typeModifierCodeValueLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetTypeModifierObject()->GetCodeValue());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:120: TerminologyInfo.GetTerminologyEntry()->GetTypeModifierObject()->SetCodeValue(this->typeModifierCodeValueLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetTerminologyEntry`, `GetTypeModifierObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: label

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Meaning | label | QLabel
- Text: Meaning
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:63: // Make sure color label width is correct (size hint is not computed before widget is shown)`

## widget: label_8

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text:     Modifier: | label_8 | QLabel
- Text:     Modifier:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`

## widget: regionModifierCodeMeaningLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: regionModifierCodeMeaningLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:92: this->regionModifierCodeMeaningLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetRegionModifierObject()->GetCodeMeaning());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:127: TerminologyInfo.GetTerminologyEntry()->GetRegionModifierObject()->SetCodeMeaning(this->regionModifierCodeMeaningLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionModifierObject`, `GetRegionObject`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: regionModifierCodeValueLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: regionModifierCodeValueLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:93: this->regionModifierCodeValueLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetRegionModifierObject()->GetCodeValue());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:128: TerminologyInfo.GetTerminologyEntry()->GetRegionModifierObject()->SetCodeValue(this->regionModifierCodeValueLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionModifierObject`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: regionModifierCSDLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: regionModifierCSDLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:94: this->regionModifierCSDLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetRegionModifierObject()->GetCodingSchemeDesignator());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:129: TerminologyInfo.GetTerminologyEntry()->GetRegionModifierObject()->SetCodingSchemeDesignator(this->regionModifierCSDLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionModifierObject`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: regionCodeValueLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: regionCodeValueLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:89: this->regionCodeValueLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetRegionObject()->GetCodeValue());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:124: TerminologyInfo.GetTerminologyEntry()->GetRegionObject()->SetCodeValue(this->regionCodeValueLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionObject`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: regionCSDLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: regionCSDLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:90: this->regionCSDLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetRegionObject()->GetCodingSchemeDesignator());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:125: TerminologyInfo.GetTerminologyEntry()->GetRegionObject()->SetCodingSchemeDesignator(this->regionCSDLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionModifierObject`, `GetRegionObject`, `GetTerminologyEntry`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: regionCodeMeaningLineEdit

- Confidence: `linked_to_api`
- Widget/action class: `QLineEdit`
- Search text: regionCodeMeaningLineEdit | QLineEdit
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:88: this->regionCodeMeaningLineEdit->setText(TerminologyInfo.GetTerminologyEntry()->GetRegionObject()->GetCodeMeaning());`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:123: TerminologyInfo.GetTerminologyEntry()->GetRegionObject()->SetCodeMeaning(this->regionCodeMeaningLineEdit->text().toStdString().c_str());`
- API footprints: `GetCodeMeaning`, `GetCodeValue`, `GetCodingSchemeDesignator`, `GetRegionObject`, `GetTerminologyEntry`, `GetTypeModifierObject`, `SetCodeMeaning`, `SetCodeValue`, `SetCodingSchemeDesignator`

## widget: autoGeneratedInfoFrame

- Confidence: `linked_to_api`
- Widget/action class: `QFrame`
- Search text: autoGeneratedInfoFrame | QFrame
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:97: this->autoGeneratedInfoFrame->setVisible(TerminologyInfo.GetTerminologyEntry()->IsValid());`
- API footprints: `GetTerminologyEntry`, `IsValid`

## widget: useAutoGeneratedCheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: Use automatically generated label and color from selected terminology: | useAutoGeneratedCheckBox | QCheckBox
- Text: Use automatically generated label and color from selected terminology:
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:132: if (this->useAutoGeneratedCheckBox->isChecked())`
- Key UI properties: {"checked": "true"}

## widget: autoGeneratedColorLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: autoGeneratedColorLabel | QLabel
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:64: this->autoGeneratedColorLabel->setMinimumWidth(this->autoGeneratedColorLabel->sizeHint().height() * 2);`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:65: this->autoGeneratedColorLabel->setMaximumWidth(this->autoGeneratedColorLabel->sizeHint().height() * 2);`
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:102: this->autoGeneratedColorLabel->setStyleSheet(colorStyleSheet);`

## widget: autoGeneratedNameLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: autoGeneratedNameLabel | QLabel
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:100: this->autoGeneratedNameLabel->setText(TerminologyInfo.Name);`

## widget: selectFromTerminologyButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Select from terminology... | selectFromTerminologyButton | QPushButton
- Text: Select from terminology...
- Implementation candidates: `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx`, `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Colors/Widgets/qSlicerTerminologyEditorWidget.cxx:67: QObject::connect(this->selectFromTerminologyButton, SIGNAL(clicked()), q, SLOT(onSelectFromTerminology()));`
- Connected slots/functions: `onSelectFromTerminology`
