### Interactive Workflow: ZygomaticImplantPlanner

**Tool name:** `ZygomaticImplantPlanner`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what ZygomaticImplantPlanner does (any task the steps below accomplish), call `ZygomaticImplantPlanner` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "Segment Editor" module, under the "Source Volume" selection section, choose the volume for segmentation.
   - Ask user: Select the source volume for segmentation.
2. `cb_step_2` [slicer_op] — In the "Segment Editor" module, create a new segmentation named "Cranial_Segmentation".
3. `cb_step_3` [slicer_op] — In the "Segment Editor" module, click the "Add" button and rename the segment to "Cranial_Segment".
4. `cb_step_4` [slicer_op] — In the "Segment Editor" module, click the "Threshold" button.
5. `cb_step_5` [user_choice] — In the "Segment Editor" module, adjust the threshold range bar to set the range value for segmentation.
   - Ask user: Set the threshold range for segmentation.
6. `cb_step_6` [slicer_op] — In the "Segment Editor" module, click the "Apply" button.
7. `cb_step_7` [user_choice] — In the "Skull segmentation" section, choose the segment node.
   - Ask user: Choose the skull segmentation node.
8. `cb_step_8` [user_choice] — In the "Entry points" section, choose the Point List node.
   - Ask user: Choose the point list (fiducial) node for entry points.
9. `cb_step_9` [extension_op] — Click the "1. Compute symmetry plane" button.
10. `cb_step_10` [user_choice] — In the "Crop radius (mm)" section, adjust the range bar to set the range value for crop.
   - Ask user: Set the crop radius (mm).
11. `cb_step_11` [extension_op] — Click the "2. Cut skull (cylinder)" button.
12. `cb_step_12` [extension_op] — Click the "3. Seperate maxilla / mandible" button.
13. `cb_step_13` [branch_op] — If further adjustments are required, tick the "Manually adjust the segmentation plane" checkbox. If not, jump to step 16.
   - Ask user: Manually adjust the segmentation plane?
14. `cb_step_14` [user_interaction] — Manually adjust the separation plane.
   - Interaction: plane
15. `cb_step_15` [extension_op] — Click the "Apply separation" button.
16. `cb_step_16` [extension_op] — Click the "4. Identify zygomatic bones" button.
17. `cb_step_17` [branch_op] — If further adjustments are required, tick the "Manually adjust the boundary planes" checkbox. If not, jump to step 20.
   - Ask user: Manually adjust the boundary planes?
18. `cb_step_18` [user_interaction] — Manually adjust the boundary planes.
   - Interaction: plane
19. `cb_step_19` [extension_op] — Click the "Apply boundaries" button.
20. `cb_step_20` [extension_op] — Click the "5. Generate Implant paths" button.
21. `cb_step_21` [branch_op] — If further adjustments are required, tick the "Manually adjust the paths" checkbox. If not, stop here.
   - Ask user: Manually adjust the paths?
22. `cb_step_22` [user_interaction] — Manually adjust the paths.
   - Interaction: line
23. `cb_step_23` [extension_op] — Click the "Apply paths" button.

**Protocol:**
1. Call `ZygomaticImplantPlanner` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
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