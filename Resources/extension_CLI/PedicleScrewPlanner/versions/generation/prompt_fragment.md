### Interactive Workflow: PedicleScrewPlanner

**Tool name:** `PedicleScrewPlanner`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what PedicleScrewPlanner does (any task the steps below accomplish), call `PedicleScrewPlanner` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "Spine CT" section, select the CT volume for processing.
   - Ask user: Select the CT volume for processing.
2. `cb_step_2` [extension_op] — Click the "Next" button in the "1. Load Image Volume" page.
3. `cb_step_3` [user_interaction] — Manually adjust the boundaries of the ROI.
   - Interaction: generic
   - Tell user: Manually adjust the boundaries of the ROI.
4. `cb_step_4` [user_choice] — Choose the "Instrumented Levels:". Choose the "# Sides:". Choose the "Approach Direction:".
   - Ask user: Instrumented Levels
5. `cb_step_5` [extension_op] — Click the "Next" button in the "2. Define Surgical Region of Interest (ROI)" page.
6. `cb_step_6` [slicer_op] — In the toolbar, turn on "slice intersection visibility". In the slice intersection interaction options, turn on "set interaction", then enable both "T
7. `cb_step_7` [user_interaction] — Manually adjust the rotation angle of the red slice.
   - Interaction: generic
   - Tell user: Manually adjust the rotation angle of the red slice.
8. `cb_step_8` [extension_op] — Click the "Place a control point" button to activate the point placement.
9. `cb_step_9` [user_interaction] — Manually click in the 2D views to add fiducial points for one part of the spine.
   - Interaction: fiducial
   - Tell user: Manually click in the 2D views to add fiducial points for one part of the spine.
10. `cb_step_10` [extension_op] — Click the "Place a control point" button to inactivate the point placement.
11. `cb_step_11` [branch_op] — If all points are configured for all parts, jump to step 12. If not, jump to step 7.
   - Ask user: Are all points configured for all parts?
12. `cb_step_12` [slicer_op] — In the slice intersection interaction options of the toolbar, turn off "set interaction".
13. `cb_step_13` [user_choice] — Set the Level/Side/Landmarks following the original selection widget.
   - Ask user: Set the Level/Side/Landmarks following the original selection widget.
14. `cb_step_14` [extension_op] — Click the "Next" button in the "3. Place the Landmarks" page.
15. `cb_step_15` [user_choice] — Choose the "Choose the puncture site". Choose the "Select screw diametermm".
   - Ask user: Choose the puncture site
16. `cb_step_16` [user_interaction] — Manually adjust the start and end position of puncture site in 2D views.
   - Interaction: generic
   - Tell user: Manually adjust the start and end position of the puncture site in the 2D views.
17. `cb_step_17` [extension_op] — Click the "Update" button.
18. `cb_step_18` [extension_op] — Click the "OK" button.
19. `cb_step_19` [branch_op] — If every puncture site is configured, jump to step 20. If not, jump to step 15.
   - Ask user: Is every puncture site configured?
20. `cb_step_20` [extension_op] — Click the "Next" button in the "4. Adjust Screws" page.
21. `cb_step_21` [extension_op] — Click the "Grade Screws" button.
22. `cb_step_22` [review_op] — Review the generated Grade Screws output Table following the original results table.
23. `cb_step_23` [extension_op] — Click the "Next" button in the "Grading Step" page.

**Protocol:**
1. Call `PedicleScrewPlanner` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
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