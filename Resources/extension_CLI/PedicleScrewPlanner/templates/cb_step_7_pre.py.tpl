# --- PedicleScrewPlanner: Manually click in the 2D views to add fiducial points. The total number of points added should be three times the value specified in '# to Instrument'. (Setup) ---
import slicer

# In-tool interaction: the active module tool/effect consumes the view
# clicks itself; do NOT create a Markups node or enter placement mode.
print("[PedicleScrewPlanner] Please Place fiducial landmarks by clicking in the 2D views; number of points equals three times the instrument count")
print("When finished, press the 'Done' button in the workflow panel.")
