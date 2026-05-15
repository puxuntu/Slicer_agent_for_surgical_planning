"""
PelvicFractureTools - Tool for integrating PelvicFracturePlanner pipeline into SlicerAIAgent.

Generates Python code that calls the PelvicFracturePlanner deep learning pipeline
for pelvic fracture segmentation, reduction, and screw planning.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def get_pelvic_fracture_tools() -> List[Dict]:
    """Return tool schemas for pelvic fracture planning."""
    return [
        {
            "type": "function",
            "function": {
                "name": "PelvicFracturePlanning",
                "description": (
                    "Generate Python code for pelvic fracture surgical planning using deep learning. "
                    "Supports three stages: "
                    "'segmentation' - segments pelvis anatomy (sacrum, left/right hip) and fracture fragments from CT; "
                    "'planning' - performs virtual fracture reduction and automatic screw placement planning; "
                    "'full' - runs the complete pipeline (segmentation + planning) in one step. "
                    "Use this tool when the user asks about pelvic fracture segmentation, "
                    "fracture reduction, screw placement, or any pelvic fracture surgical workflow. "
                    "The returned 'code' string should be inserted directly into the final executable script."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stage": {
                            "type": "string",
                            "enum": ["segmentation", "planning", "full"],
                            "description": (
                                "Pipeline stage to run: "
                                "'segmentation' for pelvis and fracture fragment segmentation only, "
                                "'planning' for fracture reduction and screw planning (requires prior segmentation), "
                                "'full' for the complete end-to-end pipeline."
                            ),
                        },
                        "volume_node_name": {
                            "type": "string",
                            "description": "Name of the input CT volume node. If omitted, auto-detects the first scalar volume in the scene.",
                        },
                        "screw_radius": {
                            "type": "number",
                            "description": "Screw radius in mm (default: 1.5). Only applies to 'planning' or 'full' stages.",
                        },
                    },
                    "required": ["stage"],
                },
            },
        },
    ]


def generate_pelvic_fracture_code(
    stage: str,
    volume_node_name: Optional[str] = None,
    screw_radius: Optional[float] = None,
) -> Dict:
    """
    Generate Python code for the pelvic fracture planning pipeline.

    Args:
        stage: One of 'segmentation', 'planning', or 'full'.
        volume_node_name: Optional name of the CT volume node.
        screw_radius: Optional screw radius in mm (default 1.5).

    Returns:
        Dict with 'tool', 'stage', 'code', 'instruction', 'explanation' keys.
    """
    if stage not in ("segmentation", "planning", "full"):
        return {
            "error": f"Invalid stage '{stage}'. Must be 'segmentation', 'planning', or 'full'."
        }

    screw_radius_str = str(screw_radius) if screw_radius else "1.5"

    if stage == "segmentation":
        code = _generate_segmentation_template(volume_node_name)
        explanation = (
            "Pelvis anatomy segmentation (sacrum, left/right hip bones) and "
            "fracture fragment identification from CT using U-Net + AMFNet deep learning models."
        )
    elif stage == "planning":
        code = _generate_planning_template(volume_node_name, screw_radius_str)
        explanation = (
            "Virtual fracture reduction via deformation network + RANSAC/ICP registration, "
            "followed by automatic screw placement planning using SVM direction estimation, "
            "Chebyshev center positioning, and cone-search optimization."
        )
    else:  # full
        code = _generate_full_template(volume_node_name, screw_radius_str)
        explanation = (
            "Complete pelvic fracture planning pipeline: pelvis and fracture segmentation, "
            "virtual fracture reduction, and automatic screw placement planning."
        )

    return {
        "tool": "PelvicFracturePlanning",
        "stage": stage,
        "code": code,
        "instruction": (
            "OUTPUT THE 'code' FIELD ABOVE VERBATIM INSIDE A ```python BLOCK "
            "AS YOUR NEXT RESPONSE. Do not modify the code. "
            "Do not write analysis or explanation before the code block."
        ),
        "explanation": explanation,
        "requirements": [
            "PelvicFracturePlanner Slicer extension must be installed",
            "Pre-trained neural network models (~763 MB) must be present in the extension's Resources directory",
            "CUDA GPU recommended (falls back to CPU but significantly slower)",
        ],
    }


def _volume_lookup_code(volume_node_name: Optional[str]) -> str:
    """Generate volume node resolution code."""
    if volume_node_name:
        return f'inputVolume = slicer.util.getNode("{volume_node_name}")'
    return "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"


_SEGMENTATION_TEMPLATE = r'''# --- Pelvic Fracture Segmentation ---
# PelvicFracturePlanner: Deep learning pipeline for pelvis anatomy and fracture segmentation.

{vol_lookup}
if inputVolume is None:
    raise RuntimeError("No CT volume found in the scene. Load a pelvic CT scan first.")
print(f"[PelvicFracture] Using volume: {{inputVolume.GetName()}}")

# Import the PelvicFracturePlanner logic class
try:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
except ImportError:
    raise RuntimeError(
        "PelvicFracturePlanner extension is not installed. "
        "Please install it via Slicer's Extension Manager first."
    )

# Progress stub (non-GUI execution)
class _ProgressStub:
    def setMaximum(self, v): pass
    def setValue(self, v): pass

# Create output segmentation nodes WITHOUT adding to scene.
# process_seg() internally calls slicer.mrmlScene.AddNode() on these nodes,
# so pre-adding them would cause "Node already added" VTK errors.
pelvisSegNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
fracSegNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")

# Run segmentation
print("[PelvicFracture] Starting pelvis and fracture segmentation...")
print("[PelvicFracture] Stage 1/2: Pelvis anatomy segmentation (U-Net, 2D slice-by-slice)...")
logic = PelvicFracturePlanningLogic()
logic.process_seg(inputVolume, pelvisSegNode, fracSegNode, _ProgressStub())

# Cache logic instance and node references for later planning stage
_pelvicFractureLogic = logic
_pelvicFracturePelvisNode = pelvisSegNode
_pelvicFractureFracNode = fracSegNode

# Create closed surface representation for 3D visualization
pelvisSegNode.CreateClosedSurfaceRepresentation()
fracSegNode.CreateClosedSurfaceRepresentation()

# Set segment display properties
for seg_node in [pelvisSegNode, fracSegNode]:
    seg_id_list = vtk.vtkStringArray()
    seg_node.GetSegmentation().GetSegmentIDs(seg_id_list)
    for i in range(seg_id_list.GetNumberOfValues()):
        seg_id = seg_node.GetSegmentation().GetNthSegmentID(i)
        display_node = seg_node.GetDisplayNode()
        if display_node:
            display_node.SetSegmentVisibility(seg_id, True)

print("[PelvicFracture] Segmentation complete.")
print(f"  Pelvis segments: {{pelvisSegNode.GetSegmentation().GetNumberOfSegments()}}")
print(f"  Fracture segments: {{fracSegNode.GetSegmentation().GetNumberOfSegments()}}")
'''

_PLANNING_TEMPLATE = r'''# --- Pelvic Fracture Planning (Reduction + Screw Placement) ---
# PelvicFracturePlanner: Virtual fracture reduction and automatic screw planning.

{vol_lookup}
if inputVolume is None:
    raise RuntimeError("No CT volume found in the scene. Load a pelvic CT scan first.")
print(f"[PelvicFracture] Using volume: {{inputVolume.GetName()}}")

# Retrieve cached logic instance and node references from prior segmentation run
try:
    logic = _pelvicFractureLogic
    pelvisSegNode = _pelvicFracturePelvisNode
    fracSegNode = _pelvicFractureFracNode
    print("[PelvicFracture] Reusing cached logic instance and segmentation nodes from prior segmentation.")
except NameError:
    raise RuntimeError(
        "No cached segmentation results found. Please run segmentation first "
        "(use stage='segmentation' or stage='full')."
    )

# Import the PelvicFracturePlanner logic class (needed if running standalone)
try:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
except ImportError:
    raise RuntimeError(
        "PelvicFracturePlanner extension is not installed. "
        "Please install it via Slicer's Extension Manager first."
    )

# Create output nodes WITHOUT adding to scene.
# process_plan() internally calls slicer.mrmlScene.AddNode() on OutputReduction,
# and conditionally adds OutputScrew if not already in the scene.
reductionNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
screwNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")

# Progress stub
class _ProgressStub:
    def setMaximum(self, v): pass
    def setValue(self, v): pass

# Run planning pipeline
print("[PelvicFracture] Starting surgical planning...")
print("[PelvicFracture] Stage 1/3: Template model generation (Deformation Network)...")
print("[PelvicFracture] Stage 2/3: Fracture reduction (RANSAC + ICP)...")
print("[PelvicFracture] Stage 3/3: Screw placement planning (SVM + Chebyshev + Cone search)...")
logic.process_plan(
    inputVolume, pelvisSegNode, fracSegNode,
    reductionNode, screwNode, _ProgressStub()
)

# Show reduction results
reductionNode.CreateClosedSurfaceRepresentation()
reduction_display = reductionNode.GetDisplayNode()
if reduction_display:
    reduction_display.SetVisibility(True)

# Show screws (process_plan creates child screw models under screwNode)
screw_display = screwNode.GetDisplayNode()
if screw_display:
    screw_display.SetVisibility(0)  # Parent node hidden; individual screws are visible

# Count child screw models
sh_node = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
screw_parent_id = sh_node.GetItemByDataNode(screwNode)
screw_count = 0
if screw_parent_id:
    screw_count = sh_node.GetNumberOfItemChildren(screw_parent_id)

print("[PelvicFracture] Planning complete.")
print(f"  Reduction segments: {{reductionNode.GetSegmentation().GetNumberOfSegments()}}")
print(f"  Screws planned: {{screw_count}}")
'''

_FULL_TEMPLATE = r'''# --- Full Pelvic Fracture Planning Pipeline ---
# PelvicFracturePlanner: End-to-end pipeline (Segmentation + Reduction + Screw Planning).

{vol_lookup}
if inputVolume is None:
    raise RuntimeError("No CT volume found in the scene. Load a pelvic CT scan first.")
print(f"[PelvicFracture] Using volume: {{inputVolume.GetName()}}")

# Import the PelvicFracturePlanner logic class
try:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
except ImportError:
    raise RuntimeError(
        "PelvicFracturePlanner extension is not installed. "
        "Please install it via Slicer's Extension Manager first."
    )

# Progress stub (non-GUI execution)
class _ProgressStub:
    def setMaximum(self, v): pass
    def setValue(self, v): pass

# ============================================================
# STAGE 1: Segmentation (Pelvis Anatomy + Fracture Fragments)
# ============================================================
# Create nodes WITHOUT adding to scene — process_seg() calls AddNode() internally.
pelvisSegNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
fracSegNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")

print("[PelvicFracture] === STAGE 1: Segmentation ===")
print("[PelvicFracture] Pelvis anatomy segmentation (U-Net, 2D slice-by-slice)...")
logic = PelvicFracturePlanningLogic()
logic.process_seg(inputVolume, pelvisSegNode, fracSegNode, _ProgressStub())

pelvisSegNode.CreateClosedSurfaceRepresentation()
fracSegNode.CreateClosedSurfaceRepresentation()
print(f"  Pelvis segments: {{pelvisSegNode.GetSegmentation().GetNumberOfSegments()}}")
print(f"  Fracture segments: {{fracSegNode.GetSegmentation().GetNumberOfSegments()}}")

# ============================================================
# STAGE 2: Surgical Planning (Reduction + Screws)
# ============================================================
# Create nodes WITHOUT adding to scene — process_plan() calls AddNode() internally.
reductionNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
screwNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")

print("[PelvicFracture] === STAGE 2: Surgical Planning ===")
print("[PelvicFracture] Template generation (Deformation Network)...")
print("[PelvicFracture] Fracture reduction (RANSAC + ICP)...")
print("[PelvicFracture] Screw placement (SVM + Chebyshev + Cone search)...")
logic.process_plan(
    inputVolume, pelvisSegNode, fracSegNode,
    reductionNode, screwNode, _ProgressStub()
)

# Display results
reductionNode.CreateClosedSurfaceRepresentation()
reduction_display = reductionNode.GetDisplayNode()
if reduction_display:
    reduction_display.SetVisibility(True)

screw_display = screwNode.GetDisplayNode()
if screw_display:
    screw_display.SetVisibility(0)  # Parent node hidden; individual screws are visible

# Count child screw models
sh_node = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
screw_parent_id = sh_node.GetItemByDataNode(screwNode)
screw_count = 0
if screw_parent_id:
    screw_count = sh_node.GetNumberOfItemChildren(screw_parent_id)

# Cache for potential re-use
_pelvicFractureLogic = logic
_pelvicFracturePelvisNode = pelvisSegNode
_pelvicFractureFracNode = fracSegNode

print("[PelvicFracture] === Pipeline Complete ===")
print(f"  Pelvis segments: {{pelvisSegNode.GetSegmentation().GetNumberOfSegments()}}")
print(f"  Fracture segments: {{fracSegNode.GetSegmentation().GetNumberOfSegments()}}")
print(f"  Reduction segments: {{reductionNode.GetSegmentation().GetNumberOfSegments()}}")
print(f"  Screws planned: {{screw_count}}")
'''


def _generate_segmentation_template(volume_node_name: Optional[str]) -> str:
    return _SEGMENTATION_TEMPLATE.format(vol_lookup=_volume_lookup_code(volume_node_name))


def _generate_planning_template(volume_node_name: Optional[str], screw_radius: str) -> str:
    # screw_radius is reserved for future use; currently the PelvicFracturePlanner
    # uses a hard-coded 1.5mm radius. The parameter is accepted here so the tool
    # schema can expose it without breaking when the planner adds support.
    return _PLANNING_TEMPLATE.format(vol_lookup=_volume_lookup_code(volume_node_name))


def _generate_full_template(volume_node_name: Optional[str], screw_radius: str) -> str:
    return _FULL_TEMPLATE.format(vol_lookup=_volume_lookup_code(volume_node_name))
