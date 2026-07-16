### Interactive Workflow: LongBoneFractureReduction

**Tool name:** `LongBoneFractureReduction`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what LongBoneFractureReduction does (any task the steps below accomplish), call `LongBoneFractureReduction` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "Input volume" section, select the CT volume for processing.
   - Ask user: Select the CT volume for processing.
2. `cb_step_2` [slicer_op] — In the "Segment Editor" module, create a new segmentation named "Reference_Segmentation".
3. `cb_step_3` [slicer_op] — In the "Segment Editor" module, click the "Add" button and rename the segment to "Reference_Segment" under "Reference_Segmentation".
4. `cb_step_4` [slicer_op] — In the "Segment Editor" module, click the "Threshold" button.
5. `cb_step_5` [user_choice] — In the "Segment Editor" module, adjust the threshold slider to set the segmentation range.
   - Ask user: Adjust the threshold slider to set the segmentation range.
6. `cb_step_6` [slicer_op] — In the "Segment Editor" module, click the "Apply" button.
7. `cb_step_7` [slicer_op] — In the "Segment Editor" module, click the "Islands" button.
8. `cb_step_8` [slicer_op] — In the "Segment Editor" module, select the "Keep selected island" option.
9. `cb_step_9` [user_interaction] — In the 2D view, click to select the reference part.
   - Interaction: generic
   - Tell user: Click in the 2D view to select the reference part island.
10. `cb_step_10` [slicer_op] — Set the segment "Reference_Segment" invisible.
11. `cb_step_11` [slicer_op] — In the "Segment Editor" module, create a new segmentation named "Moving_Segmentation".
12. `cb_step_12` [slicer_op] — In the "Segment Editor" module, click the "Add" button and rename the segment to "Moving_Segment" under "Moving_Segmentation".
13. `cb_step_13` [slicer_op] — In the "Segment Editor" module, click the "Threshold" button.
14. `cb_step_14` [user_choice] — In the "Segment Editor" module, adjust the threshold slider to set the segmentation range.
   - Ask user: Adjust the threshold slider to set the segmentation range.
15. `cb_step_15` [slicer_op] — In the "Segment Editor" module, click the "Apply" button.
16. `cb_step_16` [slicer_op] — In the "Segment Editor" module, click the "Islands" button.
17. `cb_step_17` [slicer_op] — In the "Segment Editor" module, select the "Keep selected island" option.
18. `cb_step_18` [user_interaction] — In the 2D view, click to select the moving part.
   - Interaction: generic
   - Tell user: Click in the 2D view to select the moving part island.
19. `cb_step_19` [slicer_op] — Set the segment "Moving_Segment" invisible.
20. `cb_step_20` [user_choice] — In the "Reference segmentation (blue)" section, select the reference segmentation node.
   - Ask user: Select the reference segmentation node.
21. `cb_step_21` [extension_op] — Click the "3D Reconstruction (reference)" button.
22. `cb_step_22` [user_choice] — In the "Moving segmentation (blue)" section, select the moving segmentation node.
   - Ask user: Select the moving segmentation node.
23. `cb_step_23` [extension_op] — Click the "3D Reconstruction (moving)" button.
24. `cb_step_24` [extension_op] — Click the "Add / reset reference ROI" button.
25. `cb_step_25` [user_interaction] — Manually adjust the boundaries of the ROI to retain the fractured part of the reference model.
   - Interaction: roi
   - Tell user: Manually adjust the ROI boundaries for the reference model.
26. `cb_step_26` [extension_op] — Click the "Add / reset moving ROI" button.
27. `cb_step_27` [user_interaction] — Manually adjust the boundaries of the ROI to retain the fractured part of the moving model.
   - Interaction: roi
   - Tell user: Manually adjust the ROI boundaries for the moving model.
28. `cb_step_28` [extension_op] — Click the "Detect fracture surfaces" button.
29. `cb_step_29` [extension_op] — Click the "Reduce fracture" button.
30. `cb_step_30` [branch_op] — If further adjustments are required, check the "Manually adjust the moving fragment" box. If not, stop here.
   - Ask user: Further adjustments required?
31. `cb_step_31` [user_interaction] — Manually adjust the moving fragment.
   - Interaction: generic
32. `cb_step_32` [extension_op] — Click the "Harden transform into moving fragment" button.

**Protocol:**
1. Call `LongBoneFractureReduction` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
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