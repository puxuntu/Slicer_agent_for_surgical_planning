# [runtime-fixed] Auto-revised by runtime self-correction at 20260802_210701.
# Pre-revision templates backed up under versions/runtime_fix_20260802_210701/.
# Fixed runtime error: Input entry-point fiducial list is invalid
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'ZygomaticImplantPlanner':
    try:
        slicer.util.selectModule('ZygomaticImplantPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'ZygomaticImplantPlanner': {{_module_enter_error}}")
# precondition:end

_widget = None
try:
    _widget = slicer.util.getModuleWidget('ZygomaticImplantPlanner')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.zygomaticimplantplanner.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the ZygomaticImplantPlanner module widget for 'step1Button'.")
if not hasattr(_widget, 'onStep1'):
    raise RuntimeError("ZygomaticImplantPlanner widget has no handler 'onStep1' for 'step1Button'; regenerate the CLI.")

# --- Repair: bind the required inputs before running step 1 ---
# onStep1 -> logic.computeSymmetryPlane(segNode, segId, p.inputFiducials) failed with
# "Input entry-point fiducial list is invalid" because the parameter node's
# inputFiducials (and possibly inputSegmentation) were not bound to scene nodes.
# Bind both explicitly (typed parameterNodeWrapper properties, NOT GetNodeReference/
# SetNodeReferenceID), then re-run the step.
_segNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSegmentationNode1')
if _segNode is None:
    _segNode = slicer.util.getNode('Cranial_Segmentation')
_fidNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode1')
if _fidNode is None:
    _fidNode = slicer.util.getNode('F')
if _segNode is None or _fidNode is None:
    raise RuntimeError("Repair failed: skull segmentation and/or entry-point fiducial node not found in the scene.")

# Ensure the widget's parameter node exists.
if _widget._parameterNode is None:
    _widget.initializeParameterNode()
_p = _widget._parameterNode
if _p is None:
    raise RuntimeError("Repair failed: ZygomaticImplantPlanner parameter node could not be initialized.")

# Drive the input trees so the widget's own selection logic (_selectedSegment /
# _onInputsChanged) is consistent with the bound nodes.
try:
    if _widget.segTree is not None:
        _widget.segTree.setCurrentNode(_segNode)
except Exception as _e:
    print(f"Warning: could not set segmentation tree selection: {{_e}}")
try:
    if _widget.fidTree is not None:
        _widget.fidTree.setCurrentNode(_fidNode)
except Exception as _e:
    print(f"Warning: could not set fiducial tree selection: {{_e}}")

# Belt-and-suspenders: write the node references onto the parameter node wrapper.
_p.inputSegmentation = _segNode
_p.inputFiducials = _fidNode

# Sanity-check the entry-point list actually has control points (module requirement:
# _entryPoints raises if the list is empty).
if _fidNode.GetNumberOfControlPoints() < 1:
    raise RuntimeError("Repair failed: the entry-point fiducial list has no control points.")

# Run the step's full action (computes symmetry plane, creates SkullModel and
# SymmetryPlane nodes, toggles dependent UI).
_widget.onStep1()
print("[ZygomaticImplantPlanner] Step 'cb_step_9': clicked 'step1Button' via onStep1() with inputs bound.")
