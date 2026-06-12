# Slicer UI Analysis: Modules/Loadable/SubjectHierarchy/Resources/UI/qSlicerSubjectHierarchyModule.ui

- Owner class: `qSlicerSubjectHierarchyModule`
- UI file: `Modules/Loadable/SubjectHierarchy/Resources/UI/qSlicerSubjectHierarchyModule.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSubjectHierarchyModule

- Confidence: `linked_to_code`
- Widget/action class: `qSlicerWidget`
- Search text: qSlicerSubjectHierarchyModule | qSlicerWidget
- Implementation candidates: `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.h`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModuleWidget.cxx`, `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModuleWidget.h`
- Matched implementation lines:
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:32: #include "qSlicerSubjectHierarchyModule.h"`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:33: #include "qSlicerSubjectHierarchyModuleWidget.h"`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:45: class qSlicerSubjectHierarchyModulePrivate`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:48: qSlicerSubjectHierarchyModulePrivate();`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:49: ~qSlicerSubjectHierarchyModulePrivate();`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:55: // qSlicerSubjectHierarchyModulePrivate methods`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:58: qSlicerSubjectHierarchyModulePrivate::qSlicerSubjectHierarchyModulePrivate() = default;`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:61: qSlicerSubjectHierarchyModulePrivate::~qSlicerSubjectHierarchyModulePrivate()`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:71: // qSlicerSubjectHierarchyModule methods`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:74: qSlicerSubjectHierarchyModule::qSlicerSubjectHierarchyModule(QObject* _parent)`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:76: , d_ptr(new qSlicerSubjectHierarchyModulePrivate)`
  - `Modules/Loadable/SubjectHierarchy/qSlicerSubjectHierarchyModule.cxx:81: qSlicerSubjectHierarchyModule::~qSlicerSubjectHierarchyModule() = default;`
