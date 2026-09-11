# [runtime-fixed] Auto-revised by runtime self-correction at 20260909_224041.
# Pre-revision templates backed up under versions/runtime_fix_20260909_224041/.
# Fixed runtime error: Blocked function call: dir (line 80)
import slicer

# --- Resolve the mandible curve -------------------------------------------------
# Resolution order (robust, no hard-coded literal placeholders):
#   0) optional injected helper resolve_interaction_node("mandible_curve")
#   1) BoneReconstructionPlanner parameter node reference "mandibleCurve"
#   2) fuzzy name match ("mandibul" covers both "mandible" and "mandibular")
#   3) first markups curve node in the scene
def _findMandibleCurve():
    node = None

    # 0) Optional injected helper -- probed WITHOUT using the forbidden dir()
    if resolve_interaction_node is not None:
        try:
            node = resolve_interaction_node("mandible_curve")
        except Exception:
            node = None
        if node is not None and node.GetClassName() == "vtkMRMLMarkupsCurveNode":
            return node
        node = None

    # 1) Parameter node reference set by the extension
    try:
        _logic = _bonereconstructionplanner_logic
    except NameError:
        _logic = None
    if _logic is not None:
        try:
            _paramNode = _logic.getParameterNode()
        except Exception:
            _paramNode = None
        if _paramNode is not None:
            try:
                node = _paramNode.GetNodeReference("mandibleCurve")
            except Exception:
                node = None
            if node is None:
                # parameterNodeWrapper style: typed property access
                try:
                    node = _paramNode.mandibleCurve
                except Exception:
                    node = None
    if node is not None:
        return node

    # 2) and 3) Scene-wide search for markups curve nodes
    curveNodes = []
    try:
        collection = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
        for i in range(collection.GetNumberOfItems()):
            n = collection.GetItemAsObject(i)
            if n is not None:
                curveNodes.append(n)
    except Exception:
        curveNodes = []
    if not curveNodes:
        try:
            curveNodes = list(slicer.util.getNodesByClass("vtkMRMLMarkupsCurveNode").values())
        except Exception:
            curveNodes = []

    keywords = ("mandibul", "mandible")
    for n in curveNodes:
        if any(k in n.GetName().lower() for k in keywords):
            return n
    if curveNodes:
        return curveNodes[0]
    return None

mandibleNode = _findMandibleCurve()
if mandibleNode is None:
    raise RuntimeError("MISSING_NODE: mandible curve not found in scene")

if remember_interaction_node is not None:
    try:
        remember_interaction_node("mandible_curve", mandibleNode)
    except Exception:
        pass

displayNode = mandibleNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("MISSING_NODE: display node for mandible curve not found")

# --- Resolve target views by identity, not by layout position -------------------
# 3D View 1      -> vtkMRMLViewNode singleton tag "1"
# Red slice view -> vtkMRMLSliceNode singleton tag "Red"
threeDViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
if threeDViewNode is None:
    viewNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLViewNode")
    if viewNodes.GetNumberOfItems() > 0:
        threeDViewNode = viewNodes.GetItemAsObject(0)

redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
if redSliceNode is None:
    sliceNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSliceNode")
    for i in range(sliceNodes.GetNumberOfItems()):
        n = sliceNodes.GetItemAsObject(i)
        if n is not None and n.GetName().lower().startswith("red"):
            redSliceNode = n
            break

if threeDViewNode is None or redSliceNode is None:
    raise RuntimeError("MISSING_NODE: target view node (3D View 1 / Red) not found")

viewNodeIDs = [threeDViewNode.GetID(), redSliceNode.GetID()]

# Restrict the curve's display to exactly these views (view filter).
displayNode.SetViewNodeIDs(viewNodeIDs)

# A slice view is included in the target, so make sure the markups display
# is enabled for 2D (slice) views as well as 3D.
displayNode.SetVisibility2D(True)

# --- Verify the state actually took effect --------------------------------------
applied = list(displayNode.GetViewNodeIDs())
if set(applied) != set(viewNodeIDs):
    raise RuntimeError("STATE_NOT_APPLIED: ViewNodeIDs = %s" % applied)
if not displayNode.GetVisibility2D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility2D")
