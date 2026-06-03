# Slicer UI Analysis: Libs/MRML/Widgets/Resources/UI/qMRMLSceneFactoryWidget.ui

- Owner class: `qMRMLSceneFactoryWidget`
- UI file: `Libs/MRML/Widgets/Resources/UI/qMRMLSceneFactoryWidget.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: SceneFactoryWidget

- Confidence: `linked_to_api`
- Widget/action class: `QWidget`
- Search text: SceneFactoryWidget | QWidget
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:26: #include "qMRMLSceneFactoryWidget.h"`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:28: #include "ui_qMRMLSceneFactoryWidget.h"`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:34: class qMRMLSceneFactoryWidgetPrivate : public Ui_qMRMLSceneFactoryWidget`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:36: Q_DECLARE_PUBLIC(qMRMLSceneFactoryWidget);`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:39: qMRMLSceneFactoryWidget* const q_ptr;`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:42: qMRMLSceneFactoryWidgetPrivate(qMRMLSceneFactoryWidget& object);`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:51: qMRMLSceneFactoryWidgetPrivate::qMRMLSceneFactoryWidgetPrivate(qMRMLSceneFactoryWidget& object)`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:59: void qMRMLSceneFactoryWidgetPrivate::init()`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:61: Q_Q(qMRMLSceneFactoryWidget);`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:70: void qMRMLSceneFactoryWidgetPrivate::setNodeActionsEnabled(bool enable)`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:79: // qMRMLSceneFactoryWidget methods`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:82: qMRMLSceneFactoryWidget::qMRMLSceneFactoryWidget(QWidget* _parent)`
- API footprints: `GetClassName`, `GetNthNodeByClass`, `RemoveNode`

## widget: NewSceneButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: New Scene | NewSceneButton | QPushButton
- Text: New Scene
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:63: QObject::connect(this->NewSceneButton, SIGNAL(clicked()), q, SLOT(generateScene()));`
- Connected slots/functions: `generateScene`
- API footprints: `Delete`, `vtkMRMLScene::New`

## widget: DeleteSceneButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Delete Scene | DeleteSceneButton | QPushButton
- Text: Delete Scene
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:64: QObject::connect(this->DeleteSceneButton, SIGNAL(clicked()), q, SLOT(deleteScene()));`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:107: d->DeleteSceneButton->setEnabled(true);`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:120: d->DeleteSceneButton->setEnabled(false);`
- Connected slots/functions: `deleteScene`
- API footprints: `Delete`, `vtkMRMLScene::New`

## widget: NewNodeLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: NewNodeLineEdit | QLineEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:73: this->NewNodeLineEdit->setEnabled(enable);`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:138: QString nodeClassName = d->NewNodeLineEdit->text();`

## widget: NewNodeButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: New Node | NewNodeButton | QPushButton
- Text: New Node
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:65: QObject::connect(this->NewNodeButton, SIGNAL(clicked()), q, SLOT(generateNode()));`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:72: this->NewNodeButton->setEnabled(enable);`
- Connected slots/functions: `generateNode`
- API footprints: `GetClassName`, `GetNthRegisteredNodeClass`, `GetNumberOfRegisteredNodeClasses`, `GetSingletonTag`, `IsA`

## widget: DeleteNodeLineEdit

- Confidence: `linked_to_code`
- Widget/action class: `QLineEdit`
- Search text: DeleteNodeLineEdit | QLineEdit
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:75: this->DeleteNodeLineEdit->setEnabled(enable);`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:179: QString nodeClassName = d->DeleteNodeLineEdit->text();`

## widget: DeleteNodeButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Delete Node | DeleteNodeButton | QPushButton
- Text: Delete Node
- Implementation candidates: `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx`, `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.h`
- Matched implementation lines:
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:66: QObject::connect(this->DeleteNodeButton, SIGNAL(clicked()), q, SLOT(deleteNode()));`
  - `Libs/MRML/Widgets/qMRMLSceneFactoryWidget.cxx:74: this->DeleteNodeButton->setEnabled(enable);`
- Connected slots/functions: `deleteNode`
- API footprints: `GetNthNode`, `GetNumberOfNodes`, `RemoveNode`
