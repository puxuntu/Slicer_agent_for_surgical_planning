# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerNodeWriterOptionsWidget.ui

- Owner class: `qSlicerNodeWriterOptionsWidget`
- UI file: `Base/QTGUI/Resources/UI/qSlicerNodeWriterOptionsWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerNodeWriterOptionsWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: qSlicerNodeWriterOptionsWidget | QWidget
- Implementation candidates: `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx`, `Base/QTGUI/qSlicerNodeWriterOptionsWidget.h`, `Base/QTGUI/qSlicerNodeWriterOptionsWidget_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:22: #include "qSlicerNodeWriterOptionsWidget.h"`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:23: #include "qSlicerNodeWriterOptionsWidget_p.h"`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:31: qSlicerNodeWriterOptionsWidgetPrivate::~qSlicerNodeWriterOptionsWidgetPrivate() = default;`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:34: void qSlicerNodeWriterOptionsWidgetPrivate::setupUi(QWidget* widget)`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:36: this->Ui_qSlicerNodeWriterOptionsWidget::setupUi(widget);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:42: qSlicerNodeWriterOptionsWidget::qSlicerNodeWriterOptionsWidget(qSlicerNodeWriterOptionsWidgetPrivate* pimpl, QWidget* parentWidget)`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:48: qSlicerNodeWriterOptionsWidget::qSlicerNodeWriterOptionsWidget(QWidget* parentWidget)`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:49: : Superclass(new qSlicerNodeWriterOptionsWidgetPrivate, parentWidget)`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:51: Q_D(qSlicerNodeWriterOptionsWidget);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:56: qSlicerNodeWriterOptionsWidget::~qSlicerNodeWriterOptionsWidget() = default;`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:59: bool qSlicerNodeWriterOptionsWidget::isValid() const`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:61: Q_D(const qSlicerNodeWriterOptionsWidget);`
- API footprints: `vtkMRMLStorableNode::SafeDownCast`

## widget: UseCompressionCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Compress | UseCompressionCheckBox | QCheckBox
- Text: Compress
- Implementation candidates: `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx`, `Base/QTGUI/qSlicerNodeWriterOptionsWidget.h`, `Base/QTGUI/qSlicerNodeWriterOptionsWidget_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:37: QObject::connect(this->UseCompressionCheckBox, SIGNAL(toggled(bool)), widget, SLOT(setUseCompression(bool)));`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:80: d->UseCompressionCheckBox->setEnabled(storageNode != nullptr);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:83: d->UseCompressionCheckBox->setChecked((storageNode->GetUseCompression() == 1));`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:97: d->CompressionParameterSelector->setEnabled(storageNode != nullptr && d->UseCompressionCheckBox->isChecked());`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:107: d->CompressionParameterSelector->setEnabled(d->UseCompressionCheckBox->isChecked());`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:114: return d->UseCompressionCheckBox->isVisibleTo(const_cast<qSlicerNodeWriterOptionsWidget*>(this));`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:121: d->UseCompressionCheckBox->setVisible(show);`
- Connected slots/functions: `setUseCompression`
- API footprints: `GetCompressionPresets`, `GetStorageNode`, `GetUseCompression`, `vtkMRMLStorageNode::CompressionPreset`

## widget: CompressionParameterSelector

- Confidence: `linked_to_api`
- Widget/action class: `QComboBox`
- Search text: CompressionParameterSelector | QComboBox
- Implementation candidates: `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx`, `Base/QTGUI/qSlicerNodeWriterOptionsWidget.h`, `Base/QTGUI/qSlicerNodeWriterOptionsWidget_p.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:38: QObject::connect(this->CompressionParameterSelector, SIGNAL(currentIndexChanged(int)), widget, SLOT(setCompressionParameter(int)));`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:86: d->CompressionParameterSelector->clear();`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:92: d->CompressionParameterSelector->addItem(name, parameter);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:96: d->CompressionParameterSelector->setVisible(d->CompressionParameterSelector->count() > 0);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:97: d->CompressionParameterSelector->setEnabled(storageNode != nullptr && d->UseCompressionCheckBox->isChecked());`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:107: d->CompressionParameterSelector->setEnabled(d->UseCompressionCheckBox->isChecked());`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:122: d->CompressionParameterSelector->setVisible(show && d->CompressionParameterSelector->count() > 0);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:130: QString parameter = d->CompressionParameterSelector->itemData(index).toString();`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:139: int index = d->CompressionParameterSelector->findData(parameter);`
  - `Base/QTGUI/qSlicerNodeWriterOptionsWidget.cxx:140: d->CompressionParameterSelector->setCurrentIndex(index);`
- Connected slots/functions: `setCompressionParameter`
- API footprints: `GetCompressionParameter`, `GetCompressionPresets`, `vtkMRMLStorageNode::CompressionPreset`
