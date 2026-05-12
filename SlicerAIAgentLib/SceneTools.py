"""
SceneTools - Structured scene introspection for the Slicer AI Agent.

Provides:
- buildSceneSummary(): A compact JSON summary of all MRML nodes.
- getNodeProperties(node_id): Detailed, type-aware structured properties for a specific node.
- get_scene_tools(): Tool definitions for the LLM tool-calling loop.
"""

import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def buildSceneSummary(max_nodes: int = 50) -> Dict[str, Any]:
    """
    Build a structured JSON summary of the current Slicer MRML scene.

    Args:
        max_nodes: Maximum number of nodes to include in the summary.
                   If the scene exceeds this, a note is appended.

    Returns:
        Dictionary with keys:
        - scene_summary: List of node dicts (id, name, class, visible, brief, etc.)
        - total_nodes: Total number of nodes in the scene
        - shown_nodes: Number of nodes included in the summary
        - note: Optional truncation warning
    """
    try:
        import slicer
        import vtk
    except ImportError:
        return {"scene_summary": [], "total_nodes": 0, "shown_nodes": 0, "note": "Slicer not available"}

    scene = slicer.mrmlScene
    total = scene.GetNumberOfNodes()

    # Collect all nodes first so we can prioritize data nodes over default UI nodes
    all_nodes = []
    for i in range(total):
        node = scene.GetNthNode(i)
        if not node:
            continue
        all_nodes.append(node)

    # Priority classes that contain user data (volumes, segmentations, models, etc.)
    priority_prefixes = (
        "vtkMRMLScalarVolumeNode",
        "vtkMRMLVectorVolumeNode",
        "vtkMRMLLabelMapVolumeNode",
        "vtkMRMLSegmentationNode",
        "vtkMRMLModelNode",
        "vtkMRMLMarkups",
        "vtkMRMLTransformNode",
        "vtkMRMLLinearTransformNode",
        "vtkMRMLBSplineTransformNode",
        "vtkMRMLGridTransformNode",
        "vtkMRMLTableNode",
        "vtkMRMLTextNode",
        "vtkMRMLFolderDisplayNode",
    )

    # Sort: data nodes first, then everything else
    def _node_priority(node):
        cls = node.GetClassName()
        if cls.startswith(priority_prefixes):
            return 0
        return 1

    all_nodes.sort(key=_node_priority)

    summary = []
    for node in all_nodes:
        if len(summary) >= max_nodes:
            break

        item = {
            "id": node.GetID(),
            "name": node.GetName(),
            "class": node.GetClassName(),
        }

        # Visibility via display node (not all MRML nodes have a display node)
        if hasattr(node, "GetDisplayNode"):
            displayNode = node.GetDisplayNode()
            if displayNode:
                item["visible"] = bool(displayNode.GetVisibility())
                item["displayNodeID"] = displayNode.GetID()
            else:
                item["visible"] = None

        # Transform node reference (only transformable nodes)
        if hasattr(node, "GetTransformNode"):
            transformNode = node.GetTransformNode()
            if transformNode:
                item["transformNodeID"] = transformNode.GetID()

        # Storage node reference (only storable nodes)
        if hasattr(node, "GetStorageNode"):
            storageNode = node.GetStorageNode()
            if storageNode:
                item["storageNodeID"] = storageNode.GetID()

        # Type-specific brief
        brief = ""
        try:
            if node.IsA("vtkMRMLScalarVolumeNode"):
                imageData = node.GetImageData()
                if imageData:
                    dims = imageData.GetDimensions()
                    spacing = node.GetSpacing()
                    brief = (
                        f"Dimensions: {dims[0]}\u00d7{dims[1]}\u00d7{dims[2]}, "
                        f"Spacing: {spacing[0]:.3f}\u00d7{spacing[1]:.3f}\u00d7{spacing[2]:.3f}"
                    )
                else:
                    brief = "No image data"

            elif node.IsA("vtkMRMLSegmentationNode"):
                segmentation = node.GetSegmentation()
                if segmentation:
                    count = segmentation.GetNumberOfSegments()
                    brief = f"Segments: {count}"
                else:
                    brief = "Empty segmentation"

            elif node.IsA("vtkMRMLMarkupsNode"):
                count = node.GetNumberOfControlPoints()
                brief = f"Control points: {count}"

            elif node.IsA("vtkMRMLModelNode"):
                polyData = node.GetPolyData()
                if polyData:
                    brief = f"PolyData: {polyData.GetNumberOfPoints()} points, {polyData.GetNumberOfPolys()} cells"
                else:
                    brief = "No polydata"

            elif node.IsA("vtkMRMLTransformNode"):
                brief = "Transform node"

            elif node.IsA("vtkMRMLFolderDisplayNode"):
                brief = "Subject hierarchy folder"

        except Exception as e:
            brief = f"Brief generation error: {e}"

        if brief:
            item["brief"] = brief

        summary.append(item)

    result = {
        "scene_summary": summary,
        "total_nodes": total,
        "shown_nodes": len(summary),
    }

    if total > max_nodes:
        result["note"] = (
            f"Scene contains {total} nodes. Showing first {max_nodes}. "
            f"Use GetNodeProperties with a specific node ID to inspect nodes not shown."
        )

    return result


def getNodeProperties(node_id: str) -> Dict[str, Any]:
    """
    Get detailed structured properties of a single MRML node.

    Args:
        node_id: The MRML node ID (e.g., 'vtkMRMLScalarVolumeNode1').

    Returns:
        Dictionary with common fields (id, name, class) and type-specific details.
        Returns {"error": "..."} if the node is not found.
    """
    try:
        import slicer
        import vtk
    except ImportError:
        return {"error": "Slicer not available"}

    node = slicer.mrmlScene.GetNodeByID(node_id)
    if not node:
        return {"error": f"Node '{node_id}' not found"}

    result = {
        "id": node.GetID(),
        "name": node.GetName(),
        "class": node.GetClassName(),
    }

    # --- Common properties ---
    if hasattr(node, "GetDisplayNode"):
        displayNode = node.GetDisplayNode()
        if displayNode:
            d = {"id": displayNode.GetID(), "visible": bool(displayNode.GetVisibility())}
            if hasattr(displayNode, "GetColor"):
                d["color"] = list(displayNode.GetColor())
            if hasattr(displayNode, "GetOpacity"):
                d["opacity"] = displayNode.GetOpacity()
            if hasattr(displayNode, "GetSliceIntersectionVisibility"):
                d["sliceIntersectionVisible"] = bool(displayNode.GetSliceIntersectionVisibility())
            result["display"] = d

    if hasattr(node, "GetTransformNode"):
        transformNode = node.GetTransformNode()
        if transformNode:
            result["transformNodeID"] = transformNode.GetID()

    if hasattr(node, "GetStorageNode"):
        storageNode = node.GetStorageNode()
        if storageNode:
            s = {"id": storageNode.GetID()}
            if hasattr(storageNode, "GetFileName"):
                s["fileName"] = storageNode.GetFileName()
            result["storage"] = s

    # --- Type-specific properties ---
    try:
        if node.IsA("vtkMRMLScalarVolumeNode"):
            imageData = node.GetImageData()
            if imageData:
                dims = imageData.GetDimensions()
                spacing = node.GetSpacing()
                origin = node.GetOrigin()
                directionMatrix = vtk.vtkMatrix4x4()
                node.GetIJKToRASDirectionMatrix(directionMatrix)
                result["volume"] = {
                    "dimensions": dims,
                    "spacing": spacing,
                    "origin": origin,
                    "scalarType": imageData.GetScalarTypeAsString(),
                    "ijkToRasMatrix": [
                        [directionMatrix.GetElement(r, c) for c in range(4)] for r in range(4)
                    ],
                }
            else:
                result["volume"] = {"error": "No image data"}

        elif node.IsA("vtkMRMLSegmentationNode"):
            segmentation = node.GetSegmentation()
            segments = []
            if segmentation:
                for i in range(segmentation.GetNumberOfSegments()):
                    segID = segmentation.GetNthSegmentID(i)
                    segment = segmentation.GetSegment(segID)
                    if segment:
                        tag_value = ""
                        try:
                            tag_value = segment.GetTag("RepresentationType") or ""
                        except Exception:
                            try:
                                tag_value = segment.GetTag("RepresentationType", "") or ""
                            except Exception:
                                tag_value = ""
                        segments.append({
                            "id": segID,
                            "name": segment.GetName(),
                            "color": list(segment.GetColor()),
                            "tag": tag_value,
                        })
                result["segmentation"] = {
                    "segmentCount": len(segments),
                    "segments": segments,
                    "masterRepresentation": segmentation.GetMasterRepresentationName(),
                    "containedRepresentations": list(segmentation.GetContainedRepresentationNames()) if hasattr(segmentation, "GetContainedRepresentationNames") else [],
                }
            else:
                result["segmentation"] = {"error": "No segmentation object"}

        elif node.IsA("vtkMRMLMarkupsNode"):
            points = []
            for i in range(node.GetNumberOfControlPoints()):
                pos = [0.0, 0.0, 0.0]
                node.GetNthControlPointPositionWorld(i, pos)
                points.append({
                    "index": i,
                    "label": node.GetNthControlPointLabel(i),
                    "position": pos,
                })
            result["markups"] = {
                "pointCount": len(points),
                "points": points,
            }

        elif node.IsA("vtkMRMLModelNode"):
            polyData = node.GetPolyData()
            if polyData:
                result["model"] = {
                    "points": polyData.GetNumberOfPoints(),
                    "polys": polyData.GetNumberOfPolys(),
                    "lines": polyData.GetNumberOfLines(),
                    "strips": polyData.GetNumberOfStrips(),
                }
            else:
                result["model"] = {"error": "No polydata"}

        elif node.IsA("vtkMRMLTransformNode"):
            matrix = vtk.vtkMatrix4x4()
            if hasattr(node, "GetMatrixTransformToParent") and node.GetMatrixTransformToParent(matrix):
                result["transform"] = {
                    "type": "linear",
                    "matrix": [
                        [matrix.GetElement(r, c) for c in range(4)] for r in range(4)
                    ],
                }
            else:
                result["transform"] = {"type": "non-linear or empty"}

        elif node.IsA("vtkMRMLFolderDisplayNode"):
            result["folder"] = {"expanded": bool(node.GetExpanded()) if hasattr(node, "GetExpanded") else None}

    except Exception as e:
        result["propertyError"] = str(e)

    return result


def get_scene_tools() -> List[Dict[str, Any]]:
    """
    Return tool definitions for the LLM tool-calling loop.
    These are merged with skill tools in SlicerAIAgentLogic.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "GetNodeProperties",
                "description": (
                    "Get detailed structured properties of one or more MRML nodes by their IDs. "
                    "Use this BEFORE operating on an existing node when you need specific details "
                    "(volume dimensions/spacing/origin, segment names/colors, markup control point positions, "
                    "transform matrices, display color/opacity, storage filenames) that are NOT in the scene summary. "
                    "Do NOT call this tool with an empty ids list. "
                    "Only call this when you have specific node IDs from the scene summary and need deeper inspection."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of MRML node IDs to inspect "
                                "(e.g., ['vtkMRMLScalarVolumeNode1', 'vtkMRMLSegmentationNode1']). "
                                "You may pass multiple IDs in one call."
                            ),
                        }
                    },
                    "required": ["ids"],
                },
            },
        }
    ]
