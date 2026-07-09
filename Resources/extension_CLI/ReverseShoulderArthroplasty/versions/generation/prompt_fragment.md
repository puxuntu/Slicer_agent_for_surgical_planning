### Interactive Workflow: ReverseShoulderArthroplasty

**Tool name:** `ReverseShoulderArthroplasty`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what ReverseShoulderArthroplasty does (any task the steps below accomplish), call `ReverseShoulderArthroplasty` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "1. CT volume - bone density for optimization" section, select the CT volume for processing.
   - Ask user: Select the CT volume for processing
2. `cb_step_2` [slicer_op] — In the "Segment Editor" module, create a new segmentation named "Bone_Segmentation".
3. `cb_step_3` [slicer_op] — In the "Segment Editor" module, click the "Add" button and rename the segment to "Bone_Segment".
4. `cb_step_4` [slicer_op] — In the "Segment Editor" module, click the "Threshold" button.
5. `cb_step_5` [user_choice] — In the "Segment Editor" module, adjust the threshold slider to set the segmentation range.
   - Ask user: Adjust the threshold range
6. `cb_step_6` [slicer_op] — In the "Segment Editor" module, click the "Apply" button.
7. `cb_step_7` [slicer_op] — In the "Segment Editor" module, click the "Islands" button.
8. `cb_step_8` [slicer_op] — In the "Segment Editor" module, select the "Keep largest island" option.
9. `cb_step_9` [slicer_op] — In the "Segment Editor" module, click the "Apply" button.
10. `cb_step_10` [user_choice] — In the "Bone segmentation" section, select the segment node.
   - Ask user: Select the bone segmentation node
11. `cb_step_11` [extension_op] — Click the "3D Reconstruction" button.
12. `cb_step_12` [slicer_op] — In the "Markups" module, click "Point List" to create an empty MarkupsFiducial node named "Prosthesis_center_point".
13. `cb_step_13` [user_interaction] — Manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point".
   - Interaction: fiducial
   - Tell user: Click on the glenoid cavity surface to place the point
14. `cb_step_14` [user_choice] — In the "Planning point" section, select the MarkupsFiducial node.
   - Ask user: Select the prosthesis center point fiducial node
15. `cb_step_15` [extension_op] — Click the "Prosthesis implantation" button.
16. `cb_step_16` [branch_op] — If further adjustments are required, check the "Adjust Prosthesis (3D transform handles)" box. If not, proceed to Step 19.
   - Ask user: Are further adjustments required for the prosthesis?
17. `cb_step_17` [user_interaction] — Manually adjust the 3D transform handles.
   - Interaction: generic
   - Tell user: Adjust the 3D transform handles of the implanted prosthesis
18. `cb_step_18` [extension_op] — Click the "Update Prosthesis" button.
19. `cb_step_19` [extension_op] — Click the "Plan" button.
20. `cb_step_20` [branch_op] — If further adjustments are required, check the "Adjust screw" box. If not, stop here.
   - Ask user: Are further adjustments required for the screw?
21. `cb_step_21` [user_interaction] — Manually adjust the endpoints of the planning paths.
   - Interaction: generic
   - Tell user: Adjust the endpoints of the planning paths for the screw
22. `cb_step_22` [extension_op] — Click the "Update screw" button.

**Protocol:**
1. Call `ReverseShoulderArthroplasty` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
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