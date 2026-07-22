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
   - Ask user: In the "Spine CT" section, select the CT volume for processing.
2. `cb_step_2` [extension_op] — Click the "Next" button in the "1. Load Image Volume" page.
3. `cb_step_3` [user_interaction] — Manually adjust the boundaries of the ROI.
   - Interaction: roi
4. `cb_step_4` [user_choice] — Choose the "1st Instrumented Level:". Choose the "# Sides:". Choose the "# to Instrument:". Choose the "Approach Direction:".
   - Ask user: 1st Instrumented Level
5. `cb_step_5` [extension_op] — Click the "Next" button in the "2. Define Surgical Region of Interest (ROI)" page.
6. `cb_step_6` [extension_op] — Click the "Place a control point" button.
7. `cb_step_7` [user_interaction] — Manually click in the 2D views to add fiducial points. The total number of points added should be three times the value specified in '# to Instrument'
   - Interaction: fiducial
   - Tell user: Place fiducial landmarks by clicking in the 2D views; number of points equals three times the instrument count
8. `cb_step_8` [user_choice] — Set the Level/Side/Landmarks following the original selection widget.
   - Ask user: Set the Level/Side/Landmarks following the original selection widget.
9. `cb_step_9` [extension_op] — Click the "Next" button in the "3. Place the Landmarks" page.
10. `cb_step_10` [user_choice] — Choose the "Choose the puncture site". Choose the "Select screw diametermm".
   - Ask user: Choose the puncture site
11. `cb_step_11` [user_interaction] — Manually adjust the start and end position of puncture site in 2D views.
   - Interaction: line
12. `cb_step_12` [extension_op] — Click the "Update" button.
13. `cb_step_13` [extension_op] — Click the "OK" button.
14. `cb_step_14` [branch_op] — If every puncture site is configured, jump to step 15. If not, jump to step 10.
   - Ask user: Is every puncture site configured?
15. `cb_step_15` [extension_op] — Click the "Next" button in the "4. Adjust Screws" page.
16. `cb_step_16` [extension_op] — Click the "Grade Screws" button.
17. `cb_step_17` [review_op] — Review the generated Grade Screws output Table following the original results table.
18. `cb_step_18` [extension_op] — Click the "Next" button in the "Grading Step" page.

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