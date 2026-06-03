# Slicer UI Analysis: Modules/Loadable/Terminologies/Resources/UI/qSlicerTerminologiesModule.ui

- Owner class: `qSlicerTerminologiesModule`
- UI file: `Modules/Loadable/Terminologies/Resources/UI/qSlicerTerminologiesModule.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerTerminologiesModule

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerTerminologiesModule | qSlicerWidget
- Implementation candidates: `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx`, `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.h`, `Modules/Loadable/Terminologies/qSlicerTerminologiesModuleWidget.cxx`, `Modules/Loadable/Terminologies/qSlicerTerminologiesModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:24: #include "qSlicerTerminologiesModule.h"`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:25: #include "qSlicerTerminologiesModuleWidget.h"`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:39: class qSlicerTerminologiesModulePrivate`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:42: qSlicerTerminologiesModulePrivate();`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:46: // qSlicerTerminologiesModulePrivate methods`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:49: qSlicerTerminologiesModulePrivate::qSlicerTerminologiesModulePrivate() = default;`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:52: // qSlicerTerminologiesModule methods`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:55: qSlicerTerminologiesModule::qSlicerTerminologiesModule(QObject* _parent)`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:57: , d_ptr(new qSlicerTerminologiesModulePrivate)`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:62: qSlicerTerminologiesModule::~qSlicerTerminologiesModule() = default;`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:65: QString qSlicerTerminologiesModule::helpText() const`
  - `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx:73: QString qSlicerTerminologiesModule::acknowledgementText() const`

## widget: TerminologyNavigatorWidget

- Confidence: `ui_only`
- Widget/action class: `qSlicerTerminologyNavigatorWidget`
- Search text: TerminologyNavigatorWidget | qSlicerTerminologyNavigatorWidget
- Implementation candidates: `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.cxx`, `Modules/Loadable/Terminologies/qSlicerTerminologiesModule.h`, `Modules/Loadable/Terminologies/qSlicerTerminologiesModuleWidget.cxx`, `Modules/Loadable/Terminologies/qSlicerTerminologiesModuleWidget.h`
