from .common import *


class LogicSceneMixin:
    def _buildSceneContext(self):
        """
        Build structured context about the current Slicer MRML scene.

        Returns:
            Dictionary with a structured scene summary, or None.
        """
        try:
            from SlicerAIAgentLib import SceneTools
            summary = SceneTools.buildSceneSummary(max_nodes=50)
            if summary.get("scene_summary") is not None:
                return summary
        except Exception as e:
            logger.warning(f"Failed to build scene context: {e}")

        return None

    def executeCode(self, code):
        validation = self.codeValidator.validate(code)
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"Code validation failed: {validation['reason']}"
            }
        return self.executor.execute(code)

    def executeCodeAsync(self, code, callback=None):
        """
        Execute code asynchronously without blocking the UI.

        Note: Due to Qt thread constraints, execution happens in the main thread
        but is scheduled via QTimer to allow the current event loop to process.

        Args:
            code: Python code to execute
            callback: Function to call with result dict when complete
        """
        validation = self.codeValidator.validate(code)
        if not validation["valid"]:
            if callback:
                callback({
                    "success": False,
                    "error": f"Code validation failed: {validation['reason']}"
                })
            return

        self.executor.executeAsync(code, callback)

    def buildSceneSnapshot(self):
        """Capture lightweight scene state for semantic verification."""
        snapshot = {
            "counts": {},
            "nodes": [],
            "segmentations": [],
            "models": [],
            "transforms": [],
            "volumes": [],
            "visible_nodes": 0,
            "layout": None,
            "active_module": None,
            "active_volume_id": None,
            "active_label_volume_id": None,
            "active_place_node_id": None,
        }
        try:
            scene = slicer.mrmlScene
            try:
                layout_node = slicer.app.layoutManager().layoutLogic().GetLayoutNode()
                if layout_node:
                    snapshot["layout"] = layout_node.GetViewArrangement()
            except Exception:
                pass
            try:
                module_manager = slicer.app.moduleManager()
                active_module = module_manager.activeModule() if module_manager else None
                snapshot["active_module"] = active_module.name if active_module else None
            except Exception:
                pass
            try:
                selection_node = slicer.app.applicationLogic().GetSelectionNode()
                if selection_node:
                    snapshot["active_volume_id"] = selection_node.GetActiveVolumeID()
                    snapshot["active_label_volume_id"] = selection_node.GetActiveLabelVolumeID()
                    snapshot["active_place_node_id"] = selection_node.GetActivePlaceNodeID()
            except Exception:
                pass
            for i in range(scene.GetNumberOfNodes()):
                node = scene.GetNthNode(i)
                if not node:
                    continue
                class_name = node.GetClassName()
                snapshot["counts"][class_name] = snapshot["counts"].get(class_name, 0) + 1

                display_node = node.GetDisplayNode() if hasattr(node, "GetDisplayNode") else None
                node_info = {
                    "id": node.GetID(),
                    "name": node.GetName(),
                    "class": class_name,
                    "mtime": node.GetMTime() if hasattr(node, "GetMTime") else None,
                    "has_display": bool(display_node),
                    "visible": bool(display_node and display_node.GetVisibility()),
                }
                snapshot["nodes"].append(node_info)
                if display_node and display_node.GetVisibility():
                    snapshot["visible_nodes"] += 1

                if class_name == "vtkMRMLSegmentationNode":
                    segmentation_info = {
                        "id": node.GetID(),
                        "name": node.GetName(),
                        "segments": 0,
                        "has_closed_surface": False,
                        "total_voxels": 0,
                    }
                    try:
                        segmentation = node.GetSegmentation()
                        segmentation_info["segments"] = segmentation.GetNumberOfSegments()
                        if hasattr(segmentation, "ContainsRepresentation"):
                            segmentation_info["has_closed_surface"] = bool(segmentation.ContainsRepresentation("Closed surface"))
                        # Count total voxels across all segments
                        import vtkSegmentationCorePython as vtkSegmentationCore
                        for seg_idx in range(segmentation.GetNumberOfSegments()):
                            segment = segmentation.GetNthSegment(seg_idx)
                            if segment:
                                labelmap = segment.GetRepresentation("Binary labelmap")
                                if labelmap:
                                    segmentation_info["total_voxels"] += labelmap.GetNumberOfPoints()
                    except Exception:
                        pass
                    snapshot["segmentations"].append(segmentation_info)

                if class_name == "vtkMRMLModelNode":
                    model_info = {
                        "id": node.GetID(),
                        "name": node.GetName(),
                        "points": 0,
                        "cells": 0,
                        "has_polydata": False,
                    }
                    try:
                        polydata = node.GetPolyData()
                        if polydata:
                            model_info["points"] = polydata.GetNumberOfPoints()
                            model_info["cells"] = polydata.GetNumberOfCells()
                            model_info["has_polydata"] = True
                    except Exception:
                        pass
                    snapshot["models"].append(model_info)

                if class_name == "vtkMRMLLinearTransformNode":
                    transform_info = {
                        "id": node.GetID(),
                        "name": node.GetName(),
                        "is_identity": True,
                    }
                    try:
                        matrix = vtk.vtkMatrix4x4()
                        node.GetMatrixTransformToParent(matrix)
                        transform_info["is_identity"] = matrix.IsIdentity()
                    except Exception:
                        pass
                    snapshot["transforms"].append(transform_info)

                if class_name == "vtkMRMLScalarVolumeNode":
                    volume_info = {
                        "id": node.GetID(),
                        "name": node.GetName(),
                        "dimensions": [0, 0, 0],
                        "voxel_count": 0,
                    }
                    try:
                        image_data = node.GetImageData()
                        if image_data:
                            dims = image_data.GetDimensions()
                            volume_info["dimensions"] = list(dims)
                            volume_info["voxel_count"] = dims[0] * dims[1] * dims[2]
                    except Exception:
                        pass
                    snapshot["volumes"].append(volume_info)
        except Exception as e:
            logger.warning(f"Failed to build scene snapshot: {e}")
        return snapshot

    def getSceneCheckRegistry(self):
        """Return supported deterministic checks for optional plan verification."""
        return {
            "node_count_delta": self._checkNodeCountDelta,
            "node_exists": self._checkNodeExists,
            "node_modified": self._checkNodeModified,
            "node_has_display": self._checkNodeHasDisplay,
            "node_name_matches": self._checkNodeNameMatches,
            "node_has_content": self._checkNodeHasContent,
            "layout_changed": self._checkLayoutChanged,
            "selection_changed": self._checkSelectionChanged,
            "module_entered": self._checkModuleEntered,
            "property_true": self._checkPropertyTrue,
            "not_checked": self._checkNotChecked,
        }

    def verifySceneAgainstPlan(self, before, after, plan):
        """Compare optional machine-checkable expectations against scene snapshots."""
        result = {"valid": True, "errors": [], "warnings": [], "diagnostics": []}
        if not isinstance(plan, dict):
            return result

        steps = plan.get("steps", [])
        if not isinstance(steps, list):
            return result

        registry = self.getSceneCheckRegistry()

        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            expected = step.get("expected_scene_change")
            if not isinstance(expected, dict):
                continue

            change_type = str(expected.get("type", "")).lower()
            if not change_type:
                change_type = self._inferLegacySceneCheckType(expected)
            check = registry.get(change_type)
            if not check:
                result["warnings"].append(
                    f"Step {idx} has unsupported expected_scene_change type '{change_type}' and was not checked"
                )
                continue
            check_result = check(before, after, expected)
            for warning in check_result.get("warnings", []):
                result["warnings"].append(f"Step {idx} {warning}")
            for error in check_result.get("errors", []):
                result["errors"].append(f"Step {idx} {error}")
            diag = check_result.get("_diagnostic")
            if diag:
                result["diagnostics"].append({"step": idx, **diag})

        if result["errors"]:
            result["valid"] = False
        return result

    def _inferLegacySceneCheckType(self, expected):
        if expected.get("node_class") or expected.get("class"):
            return "node_count_delta"
        if expected.get("property"):
            return "property_true"
        return ""

    def _matchSnapshotNodes(self, snapshot, node_class=None, name_contains=None):
        nodes = snapshot.get("nodes", []) if isinstance(snapshot, dict) else []
        name_filter = str(name_contains or "").lower()
        matches = []
        for node in nodes:
            if node_class and node.get("class") != node_class:
                continue
            if name_filter and name_filter not in str(node.get("name") or "").lower():
                continue
            matches.append(node)
        return matches

    def _collectSnapshotCandidates(self, snapshot, node_class=None, name_contains=None):
        """Collect near-miss node candidates when an exact match fails.

        Returns up to 5 candidate dicts with keys: id, name, class, score, match_notes.
        """
        nodes = snapshot.get("nodes", []) if isinstance(snapshot, dict) else []
        name_filter = str(name_contains or "").lower()
        class_filter = str(node_class or "").lower()
        candidates = []
        seen_ids = set()
        for node in nodes:
            nid = node.get("id")
            if nid in seen_ids:
                continue
            seen_ids.add(nid)
            actual_class = str(node.get("class") or "").lower()
            actual_name = str(node.get("name") or "").lower()
            score = 0
            notes = []
            if class_filter:
                if actual_class == class_filter:
                    score += 3
                    notes.append("class_exact")
                elif class_filter in actual_class or actual_class in class_filter:
                    score += 1
                    notes.append("class_partial")
            if name_filter:
                if actual_name == name_filter:
                    score += 3
                    notes.append("name_exact")
                elif name_filter in actual_name or actual_name in name_filter:
                    score += 1
                    notes.append("name_partial")
            if score > 0:
                candidates.append({
                    "id": nid,
                    "name": node.get("name"),
                    "class": node.get("class"),
                    "score": score,
                    "match_notes": notes,
                })
        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates[:5]

    def _checkNotChecked(self, before, after, expected):
        return {"errors": [], "warnings": []}

    def _checkNodeCountDelta(self, before, after, expected):
        before_counts = before.get("counts", {}) if isinstance(before, dict) else {}
        after_counts = after.get("counts", {}) if isinstance(after, dict) else {}
        node_class = expected.get("node_class") or expected.get("class")
        count_delta = expected.get("min_delta", expected.get("count_delta"))
        if not node_class or not isinstance(count_delta, int) or count_delta <= 0:
            return {"errors": [], "warnings": ["node_count_delta is missing node_class or positive min_delta"]}
        observed_delta = after_counts.get(node_class, 0) - before_counts.get(node_class, 0)
        if observed_delta < count_delta:
            return {"errors": [f"expected {node_class} count_delta >= {count_delta}, observed {observed_delta}"], "warnings": []}
        # If content assertions are specified, also verify the new nodes have actual data
        content_errors = self._checkContentAssertions(after, node_class, expected)
        if content_errors:
            return {"errors": content_errors, "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkNodeExists(self, before, after, expected):
        node_class = expected.get("node_class") or expected.get("class")
        matches = self._matchSnapshotNodes(after, node_class, expected.get("name_contains"))
        if not matches:
            label = node_class or "node"
            name = expected.get("name_contains")
            suffix = f" with name containing '{name}'" if name else ""
            error_msg = f"expected {label}{suffix} to exist"
            candidates = self._collectSnapshotCandidates(after, node_class, expected.get("name_contains"))
            return {
                "errors": [error_msg],
                "warnings": [],
                "_diagnostic": {
                    "check_type": "node_exists",
                    "expected": {"node_class": node_class, "name_contains": name},
                    "actual_candidates": candidates,
                }
            }
        # If content assertions are specified, also verify matching nodes have actual data
        content_errors = self._checkContentAssertions(after, node_class, expected)
        if content_errors:
            return {"errors": content_errors, "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkNodeModified(self, before, after, expected):
        node_class = expected.get("node_class") or expected.get("class")
        before_nodes = {
            node.get("id"): node
            for node in self._matchSnapshotNodes(before, node_class, expected.get("name_contains"))
            if node.get("id")
        }
        after_nodes = [
            node for node in self._matchSnapshotNodes(after, node_class, expected.get("name_contains"))
            if node.get("id")
        ]
        for node in after_nodes:
            before_node = before_nodes.get(node.get("id"))
            if before_node and node.get("mtime") and before_node.get("mtime") and node.get("mtime") > before_node.get("mtime"):
                return {"errors": [], "warnings": []}
        return {"errors": [f"expected an existing {node_class or 'node'} to be modified"], "warnings": []}

    def _checkNodeHasDisplay(self, before, after, expected):
        node_class = expected.get("node_class") or expected.get("class")
        matches = self._matchSnapshotNodes(after, node_class, expected.get("name_contains"))
        if not any(node.get("has_display") for node in matches):
            return {"errors": [f"expected {node_class or 'node'} to have a display node"], "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkContentAssertions(self, snapshot, node_class, expected):
        """Verify that matching nodes in the snapshot have actual content (points, voxels, etc.).

        Supported assertions:
        - min_points (for vtkMRMLModelNode)
        - min_cells (for vtkMRMLModelNode)
        - min_voxels (for vtkMRMLSegmentationNode)
        - min_segments (for vtkMRMLSegmentationNode)
        - min_voxel_count (for vtkMRMLScalarVolumeNode)
        - is_non_identity (for vtkMRMLLinearTransformNode)

        Returns a list of error strings (empty if all pass).
        """
        errors = []
        assertions = expected.get("content_assertions", {})
        if not assertions:
            # Also check legacy top-level keys for backward compat
            if expected.get("min_points") is not None:
                assertions["min_points"] = expected["min_points"]
            if expected.get("min_cells") is not None:
                assertions["min_cells"] = expected["min_cells"]
            if expected.get("min_voxels") is not None:
                assertions["min_voxels"] = expected["min_voxels"]
            if expected.get("min_segments") is not None:
                assertions["min_segments"] = expected["min_segments"]
            if expected.get("is_non_identity") is not None:
                assertions["is_non_identity"] = expected["is_non_identity"]
            if not assertions:
                return errors

        # Match nodes by class and optional name filter
        name_filter = expected.get("name_contains")
        if node_class == "vtkMRMLModelNode":
            models = snapshot.get("models", [])
            if name_filter:
                models = [m for m in models if name_filter.lower() in m.get("name", "").lower()]
            if assertions.get("min_points") is not None:
                min_p = assertions["min_points"]
                if not any(m.get("points", 0) >= min_p for m in models):
                    actual = ", ".join(f"{m.get('name', '?')}:{m.get('points', 0)}pts" for m in models) if models else "none"
                    errors.append(f"expected model with >= {min_p} points, found: {actual}")
            if assertions.get("min_cells") is not None:
                min_c = assertions["min_cells"]
                if not any(m.get("cells", 0) >= min_c for m in models):
                    actual = ", ".join(f"{m.get('name', '?')}:{m.get('cells', 0)}cells" for m in models) if models else "none"
                    errors.append(f"expected model with >= {min_c} cells, found: {actual}")

        elif node_class == "vtkMRMLSegmentationNode":
            segmentations = snapshot.get("segmentations", [])
            if name_filter:
                segmentations = [s for s in segmentations if name_filter.lower() in s.get("name", "").lower()]
            if assertions.get("min_voxels") is not None:
                min_v = assertions["min_voxels"]
                if not any(s.get("total_voxels", 0) >= min_v for s in segmentations):
                    actual = ", ".join(f"{s.get('name', '?')}:{s.get('total_voxels', 0)}voxels" for s in segmentations) if segmentations else "none"
                    errors.append(f"expected segmentation with >= {min_v} voxels, found: {actual}")
            if assertions.get("min_segments") is not None:
                min_s = assertions["min_segments"]
                if not any(s.get("segments", 0) >= min_s for s in segmentations):
                    actual = ", ".join(f"{s.get('name', '?')}:{s.get('segments', 0)}segs" for s in segmentations) if segmentations else "none"
                    errors.append(f"expected segmentation with >= {min_s} segments, found: {actual}")

        elif node_class == "vtkMRMLScalarVolumeNode":
            volumes = snapshot.get("volumes", [])
            if name_filter:
                volumes = [v for v in volumes if name_filter.lower() in v.get("name", "").lower()]
            if assertions.get("min_voxel_count") is not None:
                min_vc = assertions["min_voxel_count"]
                if not any(v.get("voxel_count", 0) >= min_vc for v in volumes):
                    actual = ", ".join(f"{v.get('name', '?')}:{v.get('voxel_count', 0)}voxels" for v in volumes) if volumes else "none"
                    errors.append(f"expected volume with >= {min_vc} voxels, found: {actual}")

        elif node_class == "vtkMRMLLinearTransformNode":
            transforms = snapshot.get("transforms", [])
            if name_filter:
                transforms = [t for t in transforms if name_filter.lower() in t.get("name", "").lower()]
            if assertions.get("is_non_identity"):
                if not any(not t.get("is_identity", True) for t in transforms):
                    actual = ", ".join(f"{t.get('name', '?')}:identity={t.get('is_identity', True)}" for t in transforms) if transforms else "none"
                    errors.append(f"expected non-identity transform, found: {actual}")

        return errors

    def _checkNodeHasContent(self, before, after, expected):
        """Verify that matching nodes have actual content (points, voxels, etc.)."""
        node_class = expected.get("node_class") or expected.get("class")
        if not node_class:
            return {"errors": [], "warnings": ["node_has_content is missing node_class"]}
        content_errors = self._checkContentAssertions(after, node_class, expected)
        if content_errors:
            return {"errors": content_errors, "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkNodeNameMatches(self, before, after, expected):
        name_contains = expected.get("name_contains")
        if not name_contains:
            return {"errors": [], "warnings": ["node_name_matches is missing name_contains"]}
        return self._checkNodeExists(before, after, expected)

    def _checkLayoutChanged(self, before, after, expected):
        if before.get("layout") == after.get("layout"):
            return {"errors": [f"expected layout to change from {before.get('layout')}"], "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkSelectionChanged(self, before, after, expected):
        before_selection = (
            before.get("active_volume_id"),
            before.get("active_label_volume_id"),
            before.get("active_place_node_id"),
        )
        after_selection = (
            after.get("active_volume_id"),
            after.get("active_label_volume_id"),
            after.get("active_place_node_id"),
        )
        if before_selection == after_selection:
            return {"errors": [f"expected active selection to change from {before_selection}"], "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkModuleEntered(self, before, after, expected):
        module_name = expected.get("module") or expected.get("module_name")
        active_module = after.get("active_module")
        if module_name and str(module_name).lower() != str(active_module).lower():
            return {"errors": [f"expected active module '{module_name}', observed '{active_module}'"], "warnings": []}
        if not module_name and before.get("active_module") == active_module:
            return {"errors": [f"expected active module to change from '{active_module}'"], "warnings": []}
        return {"errors": [], "warnings": []}

    def _checkPropertyTrue(self, before, after, expected):
        prop = str(expected.get("property", "")).lower()
        expected_value = expected.get("expected", True)
        if expected_value is not True:
            return {"errors": [], "warnings": ["property_true only checks expected=true properties"]}
        if prop in ("segmentation_has_segments", "segmentation_contains_segment"):
            if not any(s.get("segments", 0) > 0 for s in after.get("segmentations", [])):
                return {"errors": ["expected a segmentation with at least one segment"], "warnings": []}
        elif prop in ("segmentation_has_closed_surface", "closed_surface"):
            if not any(s.get("has_closed_surface") for s in after.get("segmentations", [])):
                return {"errors": ["expected a closed surface segmentation representation"], "warnings": []}
        elif prop in ("segmentation_has_voxels", "segmentation_voxels"):
            if not any(s.get("total_voxels", 0) > 0 for s in after.get("segmentations", [])):
                return {"errors": ["expected a segmentation with at least one voxel"], "warnings": []}
        elif prop in ("model_has_polydata", "model_polydata"):
            if not any(m.get("points", 0) > 0 and m.get("cells", 0) > 0 for m in after.get("models", [])):
                return {"errors": ["expected a model node with valid polydata"], "warnings": []}
        elif prop in ("model_has_points", "model_points"):
            if not any(m.get("points", 0) > 0 for m in after.get("models", [])):
                return {"errors": ["expected a model node with at least one point"], "warnings": []}
        elif prop in ("transform_is_non_identity", "non_identity_transform"):
            if not any(not t.get("is_identity", True) for t in after.get("transforms", [])):
                return {"errors": ["expected a non-identity transform"], "warnings": []}
        elif prop in ("display_visibility", "visible"):
            if after.get("visible_nodes", 0) <= 0:
                return {"errors": [], "warnings": ["expected at least one visible display node"]}
        else:
            return {"errors": [], "warnings": [f"unsupported property_true property '{prop}' was not checked"]}
        return {"errors": [], "warnings": []}
