### Interactive Workflow: PelvicFracturePlanning

**Tool name:** `PelvicFracturePlanning`
**Type:** Guided interactive workflow

**When to use:** when the user asks to run, plan, or perform what PelvicFracturePlanning does (any task the steps below accomplish), call `PelvicFracturePlanning` and drive this workflow -- do NOT write custom code or fall back to codebase search/generation.

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "Input CT Volume" option, choose the Pelvic Volume.
   - Ask user: Choose the Pelvic Volume in the Input CT Volume option.
2. `cb_step_2` [extension_op] — Click "Run Step 1: Segment Pelvis" button.
3. `cb_step_3` [slicer_op] — For the 3D view, click the "Center view" botton.
4. `cb_step_4` [extension_op] — Click "Run Step 2: Segment Fractures" button.
5. `cb_step_5` [user_choice] — In the "Untick a piece to stop treating it as separate" section, untick these segments.
   - Ask user: Untick the segments that should stop being treated as separate.
6. `cb_step_6` [branch_op] — If a piece should have been split but was and and require cut it manually, jump to step 7. If not, jump to step 10.
   - Ask user: Does a piece require manual cutting because it should have been split but was not?
7. `cb_step_7` [extension_op] — Click "Manually seperate" button.
8. `cb_step_8` [user_interaction] — Manually click to add a cut point and adjust the position and rotation of the cutting plane.
   - Interaction: plane
   - Tell user: Click in the view to add a cut point, then adjust the cutting plane's position and rotation.
9. `cb_step_9` [extension_op] — Click "Confirm seperation" button.
10. `cb_step_10` [extension_op] — Click "Run Step 3: Generate template" button.
11. `cb_step_11` [branch_op] — If further adjustments of the template are required, tick the "Manually adjust a template" checkbox. If not, jump to step 13.
   - Ask user: Are further adjustments of the template required?
12. `cb_step_12` [user_choice] — In the "Template" option, Choose which template needs adjustment in the "Template" selection box.
   - Ask user: Choose which template needs adjustment.
13. `cb_step_13` [extension_op] — Click the "Apply template adjustment" button.
14. `cb_step_14` [extension_op] — Click "Run Step 4: Register _Reduce" button.
15. `cb_step_15` [branch_op] — If further adjustments are required, tick the "Manually adjust a fragment" checkbox. If not, jump to step 17.
   - Ask user: Are further adjustments of a fragment required?
16. `cb_step_16` [user_choice] — In the "Fragment" option, Choose which fragment needs adjustment in the "Fragment" selection box.
   - Ask user: Choose which fragment needs adjustment.
17. `cb_step_17` [extension_op] — Click the "Apply adjustments" button.
18. `cb_step_18` [extension_op] — Click the "Run Step 5: Plan Screws" button.
19. `cb_step_19` [branch_op] — If further adjustments are required, tick the "Edit Screw trajectories" checkbox. If not, stop here.
   - Ask user: Are further screw trajectory adjustments required?
20. `cb_step_20` [user_choice] — In the "Trajectory" option, Choose which trajectory needs adjustment in the "Trajectory" selection box.
   - Ask user: Choose which trajectory needs adjustment.
21. `cb_step_21` [extension_op] — Click the "Regenerate screws from edited lines" button.

**Protocol:**
1. Call `PelvicFracturePlanning` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
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