### Interactive Workflow: OrbitalFractureReconstruction

**Tool name:** `OrbitalFractureReconstruction`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what OrbitalFractureReconstruction does (any task the steps below accomplish), call `OrbitalFractureReconstruction` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "Input CT volume" section, select the CT volume for processing.
   - Ask user: Select the CT volume for processing
2. `cb_step_2` [slicer_op] — In the "Markups" module, click "ROI" to create an empty MarkupsROI node named "Orbital_Region".
3. `cb_step_3` [user_interaction] — Manually click and adjust on the Slice views to create the ROI for the "Orbital_Region".
   - Interaction: roi
   - Tell user: Click and adjust on the slice views to create the ROI for Orbital_Region
4. `cb_step_4` [user_choice] — In the "Bounding box (ROI)" section, select the MarkupsROI node.
   - Ask user: Select the MarkupsROI node for the bounding box
5. `cb_step_5` [extension_op] — Click the "Cut the volume with ROI" button.
6. `cb_step_6` [slicer_op] — In the "Segment Editor" module, create a new segmentation named "Bone_Segmentation" for the "OFR_CutVolume" volume node.
7. `cb_step_7` [slicer_op] — In the "Segment Editor" module, click the "Add" button and rename the segment to "Bone_Segment".
8. `cb_step_8` [slicer_op] — In the "Segment Editor" module, click the "Threshold" button.
9. `cb_step_9` [user_choice] — In the "Segment Editor" module, adjust the threshold slider to set the segmentation range.
   - Ask user: Adjust the threshold range for bone segmentation
10. `cb_step_10` [slicer_op] — In the "Segment Editor" module, click the "Apply" button.
11. `cb_step_11` [user_choice] — In the "Bone segmentation" section, select the segment node.
   - Ask user: Select the bone segmentation node for full bone reconstruction
12. `cb_step_12` [extension_op] — Click the "Reconstruct full bone" button.
13. `cb_step_13` [user_choice] — In the "Fractured side (pick the colored box over the fractured orbit)" section, select the segment node.
   - Ask user: Select the fractured side (left/right)
14. `cb_step_14` [extension_op] — Click the "Segment orbit" button.
15. `cb_step_15` [extension_op] — Click the "Reconstruct fractured" button.

**Protocol:**
1. Call `OrbitalFractureReconstruction` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
2. For **extension_op** and **slicer_op** steps: output the returned `code` verbatim in a ```python block. Then call the next step.
3. For **user_interaction** steps: output the returned `pre_code` verbatim in a ```python block. Relay instructions to the user. Wait for them to click 'Done'.
4. For **user_choice** steps: ask the returned question. After the user answers, call the same step with `user_action='choice_made'` and `choice_value`.
5. For **branch_op** steps: a yes/no decision that also acts and branches. Ask the returned question, then call the same step with `user_action='choice_made'` and `choice_value` ('Yes'/'No'). 'Yes' performs the step's action (e.g. ticks a checkbox) and runs the optional body once; 'No' jumps to the indicated step or stops.
6. After each step completes, call the tool with the NEXT step's `step_id` and `user_action='start'`.
7. Continue until all steps are done.

**CRITICAL RULES:**
- Execute ONE step per turn. Do NOT call multiple steps in a single turn.
- Do NOT skip extension_op or slicer_op steps. Their code MUST be output and executed.
- Always start from step 1 (`cb_step_1`) and proceed in order.