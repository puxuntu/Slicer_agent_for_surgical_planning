# Slicer UI Analysis: Modules/Loadable/Segmentations/Resources/UI/qSlicerSegmentationsSettingsPanel.ui

- Owner class: `qSlicerSegmentationsSettingsPanel`
- UI file: `Modules/Loadable/Segmentations/Resources/UI/qSlicerSegmentationsSettingsPanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSegmentationsSettingsPanel

- Confidence: `linked_to_api`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSegmentationsSettingsPanel | ctkSettingsPanel
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:32: #include "qSlicerSegmentationsSettingsPanel.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:34: #include "ui_qSlicerSegmentationsSettingsPanel.h"`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:43: // qSlicerSegmentationsSettingsPanelPrivate`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:46: class qSlicerSegmentationsSettingsPanelPrivate : public Ui_qSlicerSegmentationsSettingsPanel`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:48: Q_DECLARE_PUBLIC(qSlicerSegmentationsSettingsPanel);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:51: qSlicerSegmentationsSettingsPanel* const q_ptr;`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:54: qSlicerSegmentationsSettingsPanelPrivate(qSlicerSegmentationsSettingsPanel& object);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:64: // qSlicerSegmentationsSettingsPanelPrivate methods`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:67: qSlicerSegmentationsSettingsPanelPrivate::qSlicerSegmentationsSettingsPanelPrivate(qSlicerSegmentationsSettingsPanel& object)`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:73: void qSlicerSegmentationsSettingsPanelPrivate::init()`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:75: Q_Q(qSlicerSegmentationsSettingsPanel);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:95: qSlicerSegmentationsSettingsPanel::tr("Automatically set opacities of the segments based on which contains which, "`
- Connected slots/functions: `currentTextChanged`, `setDefaultOverwriteMode`
- API footprints: `SetDefaultOverwriteMode`, `vtkMRMLSegmentEditorNode::ConvertOverwriteModeFromString`

## widget: AutoOpacitiesLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Automatic segment opacities: | Automatically set opacities of the segments when loading from file based on which contains which, so that no segment obscures another | AutoOpacitiesLabel | QLabel
- Text: Automatic segment opacities:
- Tooltip: Automatically set opacities of the segments when loading from file based on which contains which, so that no segment obscures another
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`

## widget: AutoOpacitiesCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: Automatically set opacities of the segments when loading from file based on which contains which, so that no segment obscures another | AutoOpacitiesCheckBox | QCheckBox
- Tooltip: Automatically set opacities of the segments when loading from file based on which contains which, so that no segment obscures another
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:86: this->AutoOpacitiesCheckBox->setChecked(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:92: this->AutoOpacitiesCheckBox,`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:128: QObject::connect(this->AutoOpacitiesCheckBox, SIGNAL(toggled(bool)), q, SLOT(setAutoOpacities(bool)));`
- Connected slots/functions: `setAutoOpacities`
- Key UI properties: {"checked": "true"}

## widget: SurfaceSmoothingLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Enable surface smoothing by default: | Enable surface smoothing during binary labelmap to closed surface conversion in new segmentations. Smoothing improves appearance in 3D views and exported models but makes segment editing considerably slower. | SurfaceSmoothingLabel | QLabel
- Text: Enable surface smoothing by default:
- Tooltip: Enable surface smoothing during binary labelmap to closed surface conversion in new segmentations. Smoothing improves appearance in 3D views and exported models but makes segment editing considerably slower.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`

## widget: SurfaceSmoothingCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: Enable surface smoothing during binary labelmap to closed surface conversion in new segmentations. Smoothing improves appearance in 3D views and exported models but makes segment editing considerably slower. | SurfaceSmoothingCheckBox | QCheckBox
- Tooltip: Enable surface smoothing during binary labelmap to closed surface conversion in new segmentations. Smoothing improves appearance in 3D views and exported models but makes segment editing considerably slower.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:87: this->SurfaceSmoothingCheckBox->setChecked(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:99: this->SurfaceSmoothingCheckBox,`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:129: QObject::connect(this->SurfaceSmoothingCheckBox, SIGNAL(toggled(bool)), q, SLOT(setDefaultSurfaceSmoothing(bool)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:254: this->setDefaultSurfaceSmoothing(d->SurfaceSmoothingCheckBox->isChecked());`
- Connected slots/functions: `setDefaultSurfaceSmoothing`
- API footprints: `SetDefaultSurfaceSmoothingEnabled`
- Key UI properties: {"checked": "true"}

## widget: UseTerminologyLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Use standard terminology for segments: | If enabled, double-clicking the segment name or color in the segment tables opens the terminology selector. Otherwise the name and color can be simply edited. True by default.

Note: This applies to segment tables in Segment Editor and Segmentations modules, but other modules may choose to use custom setting that is not controlled by this checkbox. | UseTerminologyLabel | QLabel
- Text: Use standard terminology for segments:
- Tooltip: If enabled, double-clicking the segment name or color in the segment tables opens the terminology selector. Otherwise the name and color can be simply edited. True by default.

Note: This applies to segment tables in Segment Editor and Segmentations modules, but other modules may choose to use custom setting that is not controlled by this checkbox.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`

## widget: UseTerminologyCheckBox

- Confidence: `linked_to_slot`
- Widget/action class: `QCheckBox`
- Search text: If enabled, double-clicking the segment name or color in the segment tables opens the terminology selector. Otherwise the name and color can be simply edited. True by default.

Note: This applies to segment tables in Segment Editor and Segmentations modules, but other modules may choose to use custom setting that is not controlled by this checkbox. | UseTerminologyCheckBox | QCheckBox
- Tooltip: If enabled, double-clicking the segment name or color in the segment tables opens the terminology selector. Otherwise the name and color can be simply edited. True by default.

Note: This applies to segment tables in Segment Editor and Segmentations modules, but other modules may choose to use custom setting that is not controlled by this checkbox.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:88: this->UseTerminologyCheckBox->setChecked(true);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:105: this->UseTerminologyCheckBox,`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:130: QObject::connect(this->UseTerminologyCheckBox, SIGNAL(toggled(bool)), q, SLOT(setUseTerminology(bool)));`
- Connected slots/functions: `setUseTerminology`
- Key UI properties: {"checked": "true"}

## widget: label

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default terminology entry: | This terminology will be used by default for new segments in an empty segmentation. | label | QLabel
- Text: Default terminology entry:
- Tooltip: This terminology will be used by default for new segments in an empty segmentation.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`

## widget: EditDefaultTerminologyEntryPushButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkPushButton`
- Search text: (set) | This terminology will be used by default for new segments in an empty segmentation. | EditDefaultTerminologyEntryPushButton | ctkPushButton
- Text: (set)
- Tooltip: This terminology will be used by default for new segments in an empty segmentation.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:131: QObject::connect(this->EditDefaultTerminologyEntryPushButton, SIGNAL(clicked()), q, SLOT(onEditDefaultTerminologyEntry()));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:226: d->EditDefaultTerminologyEntryPushButton->setText(buttonText);`
- Connected slots/functions: `onEditDefaultTerminologyEntry`
- API footprints: `DeserializeTerminologyEntry`

## widget: label_3

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Default overwrite mode: | Default mode of editing in areas of other segments. | label_3 | QLabel
- Text: Default overwrite mode:
- Tooltip: Default mode of editing in areas of other segments.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`

## widget: DefaultOverwriteModeComboBox

- Confidence: `linked_to_api`
- Widget/action class: `ctkComboBox`
- Search text: Default mode of editing in areas of other segments. | DefaultOverwriteModeComboBox | ctkComboBox
- Tooltip: Default mode of editing in areas of other segments.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:122: this->DefaultOverwriteModeComboBox->addItem(qSlicerSegmentationsSettingsPanel::tr("Overwrite all"), QString(/*no tr*/ "OverwriteAllSegments"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:123: this->DefaultOverwriteModeComboBox->addItem(qSlicerSegmentationsSettingsPanel::tr("Overwrite visible"), QString(/*no tr*/ "OverwriteVisibleSegments"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:124: this->DefaultOverwriteModeComboBox->addItem(qSlicerSegmentationsSettingsPanel::tr("Allow overlap"), QString(/*no tr*/ "OverwriteNone"));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:125: q->registerProperty("Segmentations/DefaultOverwriteMode", this->DefaultOverwriteModeComboBox, "currentUserDataAsString", SIGNAL(currentIndexChanged(int)));`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:132: QObject::connect(this->DefaultOverwriteModeComboBox, &QComboBox::currentTextChanged, q, &qSlicerSegmentationsSettingsPanel::setDefaultOverwriteMode);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:261: this->setDefaultOverwriteMode(d->DefaultOverwriteModeComboBox->currentData().toString());`
- Connected slots/functions: `currentTextChanged`, `setDefaultOverwriteMode`
- API footprints: `SetDefaultOverwriteMode`, `vtkMRMLSegmentEditorNode::ConvertOverwriteModeFromString`

## widget: label_2

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Edit hidden segments:  | This option controls what the application should do if the user edits a segment that is currently not visible. It is meant to prevent unintentional changes to hidden segments. | label_2 | QLabel
- Text: Edit hidden segments: 
- Tooltip: This option controls what the application should do if the user edits a segment that is currently not visible. It is meant to prevent unintentional changes to hidden segments.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`

## widget: AllowEditingHiddenSegmentComboBox

- Confidence: `linked_to_code`
- Widget/action class: `ctkComboBox`
- Search text: This option controls what the application should do if the user edits a segment that is currently not visible. It is meant to prevent unintentional changes to hidden segments. | AllowEditingHiddenSegmentComboBox | ctkComboBox
- Tooltip: This option controls what the application should do if the user edits a segment that is currently not visible. It is meant to prevent unintentional changes to hidden segments.
- Implementation candidates: `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx`, `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.h`
- Matched implementation lines:
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:117: this->AllowEditingHiddenSegmentComboBox->addItem(qSlicerSegmentationsSettingsPanel::tr("Ask user"), QMessageBox::InvalidRole);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:118: this->AllowEditingHiddenSegmentComboBox->addItem(qSlicerSegmentationsSettingsPanel::tr("Always make visible"), QMessageBox::Yes);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:119: this->AllowEditingHiddenSegmentComboBox->addItem(qSlicerSegmentationsSettingsPanel::tr("Always allow"), QMessageBox::No);`
  - `Modules/Loadable/Segmentations/qSlicerSegmentationsSettingsPanel.cxx:120: q->registerProperty("Segmentations/ConfirmEditHiddenSegment", this->AllowEditingHiddenSegmentComboBox, "currentUserDataAsString", SIGNAL(currentIndexChanged(int)));`
