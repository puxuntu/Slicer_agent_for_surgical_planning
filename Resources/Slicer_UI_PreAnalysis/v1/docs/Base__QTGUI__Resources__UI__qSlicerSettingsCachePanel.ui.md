# Slicer UI Analysis: Base/QTGUI/Resources/UI/qSlicerSettingsCachePanel.ui

- Owner class: `qSlicerSettingsCachePanel`
- UI file: `Base/QTGUI/Resources/UI/qSlicerSettingsCachePanel.ui`

This document maps user-facing Slicer UI controls to nearby implementation evidence. Use UI evidence to identify intent, then verify executable code against implementation/API evidence.

## widget: qSlicerSettingsCachePanel

- Confidence: `linked_to_api`
- Widget/action class: `ctkSettingsPanel`
- Search text: qSlicerSettingsCachePanel | ctkSettingsPanel
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:29: #include "qSlicerSettingsCachePanel.h"`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:30: #include "ui_qSlicerSettingsCachePanel.h"`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:39: // qSlicerSettingsCachePanelPrivate`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:42: class qSlicerSettingsCachePanelPrivate : public Ui_qSlicerSettingsCachePanel`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:44: Q_DECLARE_PUBLIC(qSlicerSettingsCachePanel);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:47: qSlicerSettingsCachePanel* const q_ptr;`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:50: qSlicerSettingsCachePanelPrivate(qSlicerSettingsCachePanel& object);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:57: // qSlicerSettingsCachePanelPrivate methods`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:60: qSlicerSettingsCachePanelPrivate::qSlicerSettingsCachePanelPrivate(qSlicerSettingsCachePanel& object)`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:67: void qSlicerSettingsCachePanelPrivate::init()`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:69: Q_Q(qSlicerSettingsCachePanel);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:84: // qSlicerSettingsCachePanel methods`
- API footprints: `ClearCache`, `SetEnableForceRedownload`, `SetRemoteCacheDirectory`, `SetRemoteCacheFreeBufferSize`, `SetRemoteCacheLimit`

## widget: CachePathLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Cache location: | Cache directory for downloaded files | CachePathLabel | QLabel
- Text: Cache location:
- Tooltip: Cache directory for downloaded files
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`

## widget: UsedCacheSizeLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: ~0MB used | UsedCacheSizeLabel | QLabel
- Text: ~0MB used
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:132: d->UsedCacheSizeLabel->setText(tr("%1MB used").arg(QString::number(qMax(d->CacheManager->GetCurrentCacheSize(), 0.f), 'f', 2)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:138: palette.setColor(d->UsedCacheSizeLabel->foregroundRole(), Qt::red);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:142: palette.setColor(d->UsedCacheSizeLabel->foregroundRole(), QColor("orange"));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:144: d->UsedCacheSizeLabel->setPalette(palette);`
- API footprints: `CacheSizeCheck`, `FreeCacheBufferCheck`, `GetCurrentCacheSize`, `GetFreeCacheSpaceRemaining`, `GetRemoteCacheFreeBufferSize`, `GetRemoteCacheLimit`

## widget: FreeCacheSizeLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: ~200MB free | FreeCacheSizeLabel | QLabel
- Text: ~200MB free
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:134: d->FreeCacheSizeLabel->setText(tr("%1MB free").arg(QString::number(d->CacheManager->GetFreeCacheSpaceRemaining(), 'f', 2)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:145: d->FreeCacheSizeLabel->setPalette(palette);`
- API footprints: `FreeCacheBufferCheck`, `GetCurrentCacheSize`, `GetFreeCacheSpaceRemaining`, `GetRemoteCacheLimit`

## widget: UsageLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Cache usage: | Current usage of the cache | UsageLabel | QLabel
- Text: Cache usage:
- Tooltip: Current usage of the cache
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`

## widget: CacheSizeSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: CacheSizeSpinBox | QSpinBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:73: QObject::connect(this->CacheSizeSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setCacheSize(int)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:114: this->registerProperty("Cache/Size", d->CacheSizeSpinBox, /*no tr*/ "value", SIGNAL(valueChanged(int)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:129: d->CacheSizeSpinBox->setValue(d->CacheManager->GetRemoteCacheLimit());`
- Connected slots/functions: `setCacheSize`
- API footprints: `CacheSizeCheck`, `GetRemoteCacheDirectory`, `GetRemoteCacheLimit`, `SetRemoteCacheLimit`

## widget: CacheSizeLabel

- Confidence: `linked_to_api`
- Widget/action class: `QLabel`
- Search text: Cache size: | Upper limit of the dedicated cache for downloaded files | CacheSizeLabel | QLabel
- Text: Cache size:
- Tooltip: Upper limit of the dedicated cache for downloaded files
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:132: d->UsedCacheSizeLabel->setText(tr("%1MB used").arg(QString::number(qMax(d->CacheManager->GetCurrentCacheSize(), 0.f), 'f', 2)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:134: d->FreeCacheSizeLabel->setText(tr("%1MB free").arg(QString::number(d->CacheManager->GetFreeCacheSpaceRemaining(), 'f', 2)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:138: palette.setColor(d->UsedCacheSizeLabel->foregroundRole(), Qt::red);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:142: palette.setColor(d->UsedCacheSizeLabel->foregroundRole(), QColor("orange"));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:144: d->UsedCacheSizeLabel->setPalette(palette);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:145: d->FreeCacheSizeLabel->setPalette(palette);`
- API footprints: `CacheSizeCheck`, `FreeCacheBufferCheck`, `GetCurrentCacheSize`, `GetFreeCacheSpaceRemaining`, `GetRemoteCacheFreeBufferSize`, `GetRemoteCacheLimit`

## widget: CacheFreeBufferSpinBox

- Confidence: `linked_to_api`
- Widget/action class: `QSpinBox`
- Search text: CacheFreeBufferSpinBox | QSpinBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:74: QObject::connect(this->CacheFreeBufferSpinBox, SIGNAL(valueChanged(int)), q, SLOT(setCacheFreeBufferSize(int)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:115: this->registerProperty("Cache/FreeBufferSize", d->CacheFreeBufferSpinBox, /*no tr*/ "value", SIGNAL(valueChanged(int)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:147: d->CacheFreeBufferSpinBox->setRange(0, d->CacheManager->GetRemoteCacheLimit());`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:148: d->CacheFreeBufferSpinBox->setValue(d->CacheManager->GetRemoteCacheFreeBufferSize());`
- Connected slots/functions: `setCacheFreeBufferSize`
- API footprints: `GetEnableForceRedownload`, `GetRemoteCacheFreeBufferSize`, `GetRemoteCacheLimit`, `SetRemoteCacheFreeBufferSize`

## widget: CacheFreeBufferLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Cache free buffer: | Amount of space that should remain free. It should be the typical size of a file to download. | CacheFreeBufferLabel | QLabel
- Text: Cache free buffer:
- Tooltip: Amount of space that should remain free. It should be the typical size of a file to download.
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`

## widget: ForceRedownloadLabel

- Confidence: `ui_only`
- Widget/action class: `QLabel`
- Search text: Force redownload: | Control whether a file must be downloaded even if it is already in the cache | ForceRedownloadLabel | QLabel
- Text: Force redownload:
- Tooltip: Control whether a file must be downloaded even if it is already in the cache
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`

## widget: ForceRedownloadCheckBox

- Confidence: `linked_to_api`
- Widget/action class: `QCheckBox`
- Search text: ForceRedownloadCheckBox | QCheckBox
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:75: QObject::connect(this->ForceRedownloadCheckBox, SIGNAL(toggled(bool)), q, SLOT(setForceRedownload(bool)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:116: this->registerProperty("Cache/ForceRedownload", d->ForceRedownloadCheckBox, /*no tr*/ "checked", SIGNAL(toggled(bool)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:149: d->ForceRedownloadCheckBox->setChecked(d->CacheManager->GetEnableForceRedownload() == 1);`
- Connected slots/functions: `setForceRedownload`
- API footprints: `GetEnableForceRedownload`, `GetRemoteCacheFreeBufferSize`, `GetRemoteCacheLimit`, `SetEnableForceRedownload`

## widget: FilesListWidget

- Confidence: `linked_to_api`
- Widget/action class: `QListWidget`
- Search text: FilesListWidget | QListWidget
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:80: // this->FilesListWidget->setVisible(false);`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:151: d->FilesListWidget->clear();`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:159: d->FilesListWidget->addItem(fileItem);`
- API footprints: `GetCachedFiles`, `GetEnableForceRedownload`

## widget: FilesListLabel

- Confidence: `linked_to_code`
- Widget/action class: `QLabel`
- Search text: Files in cache: | FilesListLabel | QLabel
- Text: Files in cache:
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:79: // this->FilesListLabel->setVisible(false);`

## widget: ClearCachePushButton

- Confidence: `linked_to_api`
- Widget/action class: `QPushButton`
- Search text: Clear cache | Delete all files in cache directory | ClearCachePushButton | QPushButton
- Text: Clear cache
- Tooltip: Delete all files in cache directory
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:76: QObject::connect(this->ClearCachePushButton, SIGNAL(clicked()), q, SLOT(clearCache()));`
- Connected slots/functions: `clearCache`
- API footprints: `ClearCache`

## widget: CachePathButton

- Confidence: `linked_to_api`
- Widget/action class: `ctkDirectoryButton`
- Search text: CachePathButton | ctkDirectoryButton
- Implementation candidates: `Base/QTGUI/qSlicerSettingsCachePanel.cxx`, `Base/QTGUI/qSlicerSettingsCachePanel.h`
- Matched implementation lines:
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:72: QObject::connect(this->CachePathButton, SIGNAL(directoryChanged(QString)), q, SLOT(setCachePath(QString)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:112: qSlicerRelativePathMapper* relativePathMapper = new qSlicerRelativePathMapper(d->CachePathButton, "directory", SIGNAL(directoryChanged(QString)));`
  - `Base/QTGUI/qSlicerSettingsCachePanel.cxx:128: d->CachePathButton->setDirectory(QString(d->CacheManager->GetRemoteCacheDirectory()));`
- Connected slots/functions: `setCachePath`
- API footprints: `GetRemoteCacheDirectory`, `GetRemoteCacheLimit`, `SetRemoteCacheDirectory`
