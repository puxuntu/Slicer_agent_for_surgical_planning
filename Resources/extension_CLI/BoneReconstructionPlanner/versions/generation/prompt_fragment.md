### Interactive Workflow: BoneReconstructionPlanner

**Tool name:** `BoneReconstructionPlanner`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what BoneReconstructionPlanner does (any task the steps below accomplish), call `BoneReconstructionPlanner` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — If the fibula is from the right leg, tick the "Right side leg" checkbox.
   - Ask user: Is the fibula graft taken from the right leg?
2. `cb_step_2` [user_choice] — In the "Select mandibular segmentation" section, choose the mandibular segmentation.
   - Ask user: Which segmentation contains the mandible?
3. `cb_step_3` [user_choice] — In the "Select fibula segmentation" section, choose the fibula segmentation.
   - Ask user: Which segmentation contains the fibula?
4. `cb_step_4` [user_choice] — In the "Current Scalar Volume" option, choose the Mandible Volume.
   - Ask user: Which scalar volume should be used as the current volume (e.g. the Mandible Volume)?
5. `cb_step_5` [extension_op] — Click "Create bone models from segmentations" button.
6. `cb_step_6` [slicer_op] — Change the layout to "Conventional".
7. `cb_step_7` [slicer_op] — For the R (red) slice view, toggle ON "slice visibility in 3D view": render the red 2D slice plane inside the 3D view (the slice controller's eye/visi
8. `cb_step_8` [slicer_op] — For the R (red) view, toggle on "FOV, Spacing match 2D" (adjusts slice resolution to match the 2D viewport pixel spacing).
9. `cb_step_9` [slicer_op] — In the toolbar, turn on "slice intersection visibility". In the slice intersection interaction options, turn on "set interaction", then enable both "T
10. `cb_step_10` [user_interaction] — Manually adjust the slice intersection position by translate and rotate of the cross lines in each view.
   - Interaction: generic
11. `cb_step_11` [extension_op] — Click the "Add mandibular curve" button.
12. `cb_step_12` [slicer_op] — Configure the display settings of the mandibular curve created by the "Add Mandibular Curve" button. Specifically, in the "Markups" module, under the 
13. `cb_step_13` [user_interaction] — Manually click and draw on the "Red" view to create a curve along the mandible.
   - Interaction: curve
   - Tell user: In the Red slice view, click along the mandibular bone to place control points of the mandible curve, following the mandible from one end to the other.
14. `cb_step_14` [slicer_op] — Change the layout to "BoneReconstructionPlanner".
15. `cb_step_15` [slicer_op] — For the R (red) slice view, toggle OFF "slice visibility in 3D view": stop rendering the red 2D slice plane inside the 3D view (the same per-slice 3D-
16. `cb_step_16` [user_choice] — Manually set how many cut planes you want.
   - Ask user: How many mandibular cut planes do you want?
17. `cb_step_17` [extension_op] — Click "Add cut plane" button.
18. `cb_step_18` [user_interaction] — Place one mandibular cut plane using the extension's Add cut plane workflow. If the user requested N cut planes, repeat the Add cut plane + place plan
   - Interaction: plane
   - Tell user: Place this plane, then click Done.
19. `cb_step_19` [extension_op] — Click "Add fibula line" button.
20. `cb_step_20` [user_interaction] — Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
   - Interaction: line
   - Tell user: In 3D View 2, click the first control point of the fibula line at the distal end of the fibula and the second control point at the proximal end.
21. `cb_step_21` [slicer_op] — Click "Reset field of view" button in the R (red) slice view.
22. `cb_step_22` [extension_op] — Click "Center fibula line using fibula model" button to align the line with the anatomical axis of the fibula.
23. `cb_step_23` [extension_op] — Tick the "Automatic mandibular planes positioning for maximum bones contact area" checkbox.
24. `cb_step_24` [extension_op] — Tick the "Make all mandible planes rotate together" checkbox.
25. `cb_step_25` [user_choice] — Enter the desired value in "Initial space (mm)".
   - Ask user: Enter the desired initial space (mm):
26. `cb_step_26` [user_choice] — Enter the desired value in "Between space (mm)".
   - Ask user: Enter the desired between space (mm):
27. `cb_step_27` [extension_op] — Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the 
28. `cb_step_28` [extension_op] — Tick the "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" checkbox.
29. `cb_step_29` [extension_op] — In the BoneReconstructionPlanner module, in the "Mandible planes" row, toggle on the eye-icon tool button to show the mandibular cut planes.
30. `cb_step_30` [extension_op] — In the same "Mandible planes" row, toggle on the axes-icon tool button to show the plane interaction handles.
31. `cb_step_31` [user_interaction] — Manually adjust the mandibular cut planes in the mandible 3D view by dragging the visible plane interaction handles.
   - Interaction: plane
   - Tell user: Manually adjust the mandibular cut planes in the 3D view by dragging their visible interaction handles.
32. `cb_step_32` [extension_op] — In the "Mandible planes" row, toggle off the eye-icon tool button to hide the mandibular cut planes.
33. `cb_step_33` [extension_op] — Clear the "Show original mandible model" checkbox.

**Protocol:**
1. Call `BoneReconstructionPlanner` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
2. For **extension_op** and **slicer_op** steps: output the returned `code` verbatim in a ```python block. Then call the next step.
3. For **user_interaction** steps: output the returned `pre_code` verbatim in a ```python block. Relay instructions to the user. Wait for them to click 'Done'.
4. For **user_choice** steps: ask the returned question. After the user answers, call the same step with `user_action='choice_made'` and `choice_value`.
5. For **branch_op** steps: a yes/no decision that also acts and branches. Ask the returned question, then call the same step with `user_action='choice_made'` and `choice_value` ('Yes'/'No'). 'Yes' performs the step's action (e.g. ticks a checkbox) and runs the optional body once; 'No' jumps to the indicated step or stops.
6. For **review_op** steps: the panel shows the generated results for the user to review. Relay the instructions and wait for them to click Confirm — no code, no question.
7. After each step completes, call the tool with the NEXT step's `step_id` and `user_action='start'`.
8. Continue until all steps are done.

**CRITICAL RULES:**
- Execute ONE step per turn. Do NOT call multiple steps in a single turn.
- Do NOT skip extension_op or slicer_op steps. Their code MUST be output and executed.
- Always start from step 1 (`cb_step_1`) and proceed in order.