### Interactive Workflow: CranialImplantPlanning

**Tool name:** `CranialImplantPlanning`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what CranialImplantPlanning does (any task the steps below accomplish), call `CranialImplantPlanning` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [slicer_op] — In the "Segmentation Editor" module, create new segmentation as "Cranial_Segmentation".
2. `cb_step_2` [user_choice] — In the "Sourve Volume" selection section of "Segmentation Editor" module, choose the volume for segmentation.
   - Ask user: Choose the volume for segmentation.
3. `cb_step_3` [slicer_op] — In the "Segmentation Editor" module, Click the "Add" botton to add a new segment as "Cranial_Segment".
4. `cb_step_4` [slicer_op] — In the "Segmentation Editor" module, Click the "Threshold" botton.
5. `cb_step_5` [user_choice] — In the "Segmentation Editor" module, set the Threshold Range including the lowest value and the largest value.
   - Ask user: Set the threshold range (lowest and largest value).
6. `cb_step_6` [slicer_op] — In the "Segmentation Editor" module, Click the "Apply" botton.
7. `cb_step_7` [user_choice] — In the "Skull Mask" section, choose the segment node.
   - Ask user: Choose the skull mask segment node.
8. `cb_step_8` [extension_op] — Click "Load Skull Mask" button.
9. `cb_step_9` [extension_op] — Click "Add ROI" button.
10. `cb_step_10` [user_interaction] — Manually adjust the boundary of the ROI to keep the skull part.
   - Interaction: generic
11. `cb_step_11` [extension_op] — Click "Crop to ROI" button.
12. `cb_step_12` [slicer_op] — In the "Markups" module, click the "Closed Curve" to create a closed curve node.
13. `cb_step_13` [user_interaction] — Manually draw the curve on the skull model to include the fractured skull part.
   - Interaction: generic
14. `cb_step_14` [user_choice] — In the "Curve selection" section, choose the Curve node.
   - Ask user: Choose the curve node.
15. `cb_step_15` [extension_op] — Click "Cut Defect" button.
16. `cb_step_16` [extension_op] — Click "Generate Implant" button.

**Protocol:**
1. Call `CranialImplantPlanning` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
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