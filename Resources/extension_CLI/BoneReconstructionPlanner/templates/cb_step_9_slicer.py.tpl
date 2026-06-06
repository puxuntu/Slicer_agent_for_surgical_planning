# Turn on slice intersection visibility and enable Translate + Rotate interaction
appLogic = slicer.app.applicationLogic()
if appLogic:
    appLogic.SetIntersectingSlicesEnabled(appLogic.IntersectingSlicesVisibility, True)
    appLogic.SetIntersectingSlicesEnabled(appLogic.IntersectingSlicesInteractive, True)
    appLogic.SetIntersectingSlicesEnabled(appLogic.IntersectingSlicesTranslation, True)
    appLogic.SetIntersectingSlicesEnabled(appLogic.IntersectingSlicesRotation, True)