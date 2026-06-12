# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsStylesPanel.ui

- Owner class: `qSlicerSettingsStylesPanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsStylesPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsStylesPanel

- Confidence: `linked_to_slot`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsStylesPanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:31: #include "qSlicerSettingsStylesPanel.h"`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:32: #include "ui_qSlicerSettingsStylesPanel.h"`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:35: // qSlicerSettingsStylesPanelPrivate`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:38: class qSlicerSettingsStylesPanelPrivate : public Ui_qSlicerSettingsStylesPanel`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:40: Q_DECLARE_PUBLIC(qSlicerSettingsStylesPanel);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:41: typedef qSlicerSettingsStylesPanelPrivate Self;`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:44: qSlicerSettingsStylesPanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:47: qSlicerSettingsStylesPanelPrivate(qSlicerSettingsStylesPanel& object);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:59: // qSlicerSettingsStylesPanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:62: qSlicerSettingsStylesPanelPrivate::qSlicerSettingsStylesPanelPrivate(qSlicerSettingsStylesPanel& object)`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:68: void qSlicerSettingsStylesPanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:70: Q_Q(qSlicerSettingsStylesPanel);`
- Connected slots/functions: `currentTextChanged`, `onStyleChanged`

## widget: AdditionalModulePathsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Additional style paths: | AdditionalModulePathsLabel | QLabel
- Text: Additional style paths:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: AdditionalStylePathsWidget

- Confidence: `ui_only`
- Widget/action class: `QWidget`
- Search text: AdditionalStylePathsWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: AdditionalStylePathsView

- Confidence: `linked_to_slot`
- Widget/action class: `qSlicerDirectoryListView`
- Search text: AdditionalStylePathsView | qSlicerDirectoryListView
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:91: QObject::connect(this->AdditionalStylePathsView, SIGNAL(directoryListChanged()), q, SLOT(onAdditionalStylePathsChanged()));`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:92: qSlicerRelativePathMapper* relativePathMapper = new qSlicerRelativePathMapper(this->AdditionalStylePathsView, "directoryList", SIGNAL(directoryListChanged()));`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:223: d->AdditionalPaths = d->AdditionalStylePathsView->directoryList(true);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:244: d->AdditionalStylePathsView->addDirectory(path);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:252: d->AdditionalStylePathsView->removeSelectedDirectories();`
- Connected slots/functions: `onAdditionalStylePathsChanged`

## widget: groupBox

- Confidence: `ui_only`
- Widget/action class: `QGroupBox`
- Search text: groupBox | QGroupBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: AddAdditionalStylePathButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Add | <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Add a style plugin path.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Adding a style plugin path will make accessible this style plugin (and thus all the its styles) to the application. This action </span><span style=" font-size:8pt; font-weight:600;">requires</span><span style=" font-size:8pt;"> to restart the application.</span></p></body></html> | AddAdditionalStylePathButton | QPushButton
- Text: Add
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Add a style plugin path.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Adding a style plugin path will make accessible this style plugin (and thus all the its styles) to the application. This action </span><span style=" font-size:8pt; font-weight:600;">requires</span><span style=" font-size:8pt;"> to restart the application.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:107: QObject::connect(this->AddAdditionalStylePathButton, SIGNAL(clicked()), q, SLOT(onAddStyleAdditionalPathClicked()));`
- Connected slots/functions: `onAddStyleAdditionalPathClicked`

## widget: RemoveAdditionalStylePathButton

- Confidence: `linked_to_slot`
- Widget/action class: `QPushButton`
- Search text: Remove | <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Remove the currently selected style plugin path.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Removing a style plugin path will make inaccessible this style plugin (and thus all the its styles) the next time the application is opened. This action </span><span style=" font-size:8pt; font-weight:600;">requires</span><span style=" font-size:8pt;"> to restart the application.</span></p></body></html> | RemoveAdditionalStylePathButton | QPushButton
- Text: Remove
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Remove the currently selected style plugin path.</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Removing a style plugin path will make inaccessible this style plugin (and thus all the its styles) the next time the application is opened. This action </span><span style=" font-size:8pt; font-weight:600;">requires</span><span style=" font-size:8pt;"> to restart the application.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:108: QObject::connect(this->RemoveAdditionalStylePathButton, SIGNAL(clicked()), q, SLOT(onRemoveStyleAdditionalPathClicked()));`
- Connected slots/functions: `onRemoveStyleAdditionalPathClicked`

## widget: AdditionalStylePathMoreButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkExpandButton`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Show the interface to add/remove additional style paths.</span></p></body></html> | AdditionalStylePathMoreButton | ctkExpandButton
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Show the interface to add/remove additional style paths.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:88: this->AdditionalStylePathMoreButton->setChecked(false);`
- Connected slots/functions: `setVisible`
- Declared UI connections: `toggled(bool) -> groupBox.setVisible(bool)`
- Key UI properties: {"checked": "true"}

## widget: StyleLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Style | StyleLabel | QLabel
- Text: Style
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: StyleComboBox

- Confidence: `linked_to_slot`
- Widget/action class: `QComboBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Select the application current style.</span></p></body></html> | StyleComboBox | QComboBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Select the application current style.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:103: QObject::connect(this->StyleComboBox, &QComboBox::currentTextChanged, q, &qSlicerSettingsStylesPanel::onStyleChanged);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:114: int styleIndex = this->StyleComboBox->findText(styleName, Qt::MatchFixedString);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:119: styleIndex = this->StyleComboBox->findText("Slicer", Qt::MatchFixedString);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:154: QString currentStyle = this->StyleComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:156: bool wasBlocking = this->StyleComboBox->blockSignals(true);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:158: this->StyleComboBox->clear();`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:161: this->StyleComboBox->addItem(toCamelCase(style));`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:166: this->StyleComboBox->blockSignals(wasBlocking);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:168: this->StyleComboBox->setCurrentIndex(currentStyleIndex);`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:274: return d->StyleComboBox->currentText();`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:281: d->StyleComboBox->setCurrentIndex(d->styleIndex(newStyleName));`
- Connected slots/functions: `currentTextChanged`, `onStyleChanged`

## widget: ShowToolTipsLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Disable tooltips: | ShowToolTipsLabel | QLabel
- Text: Disable tooltips:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: ShowToolTipsCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set if tooltips (just like this) appear or not when the mouse hovers above widgets.</span></p></body></html> | ShowToolTipsCheckBox | QCheckBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Set if tooltips (just like this) appear or not when the mouse hovers above widgets.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:76: QObject::connect(this->ShowToolTipsCheckBox, SIGNAL(toggled(bool)), q, SLOT(onShowToolTipsToggled(bool)));`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:79: q->registerProperty("no-tooltip", this->ShowToolTipsCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
- Connected slots/functions: `onShowToolTipsToggled`

## widget: FontLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Font and size: | FontLabel | QLabel
- Text: Font and size:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: FontButton

- Confidence: `linked_to_slot`
- Widget/action class: `ctkFontButton`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Customize the application's font and size to your preference.</span></p></body></html> | FontButton | ctkFontButton
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Customize the application's font and size to your preference.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:75: QObject::connect(this->FontButton, SIGNAL(currentFontChanged(QFont)), q, SLOT(onFontChanged(QFont)));`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:80: q->registerProperty("font", this->FontButton, "currentFont", SIGNAL(currentFontChanged(QFont)));`
- Connected slots/functions: `onFontChanged`

## widget: ShowToolButtonTextLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Show text under icons in toolbar buttons: | ShowToolButtonTextLabel | QLabel
- Text: Show text under icons in toolbar buttons:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: ShowToolButtonTextCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">When disabled, only icons are seen in the main window toolbar. Otherwise the action's corresponding text is shown underneath.</span></p></body></html> | ShowToolButtonTextCheckBox | QCheckBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">When disabled, only icons are seen in the main window toolbar. Otherwise the action's corresponding text is shown underneath.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:77: QObject::connect(this->ShowToolButtonTextCheckBox, SIGNAL(toggled(bool)), q, SLOT(onShowToolButtonTextToggled(bool)));`
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:82: this->ShowToolButtonTextCheckBox,`
- Connected slots/functions: `onShowToolButtonTextToggled`

## widget: RestoreUILabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Save user interface size and position on exit: | RestoreUILabel | QLabel
- Text: Save user interface size and position on exit:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`

## widget: RestoreUICheckBox

- Confidence: `linked_to_code`
- Widget/action class: `QCheckBox`
- Search text: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">When enabled, the application size and position will be remembered for the next time the application is started.</span></p></body></html> | RestoreUICheckBox | QCheckBox
- Tooltip: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">When enabled, the application size and position will be remembered for the next time the application is started.</span></p></body></html>
- Implementation candidates: `Base/QTGUI/qSlicerSettingsStylesPanel.cxx`, `Base/QTGUI/qSlicerSettingsStylesPanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsStylesPanel.cxx:85: q->registerProperty("MainWindow/RestoreGeometry", this->RestoreUICheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
- Key UI properties: {"checked": "true"}
