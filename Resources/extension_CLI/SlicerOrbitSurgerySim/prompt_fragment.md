### Interactive Workflow: SlicerOrbitSurgerySim

**Tool name:** `SlicerOrbitSurgerySim`
**Type:** Guided interactive workflow

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [user_choice] — In the "Orbit Model" section, choose Orbit Model node.
   - Ask user: In the "Orbit Model" section, choose Orbit Model node.
2. `cb_step_2` [user_choice] — In the "Plate model" section, choose the plate model node.
   - Ask user: In the "Plate model" section, choose the plate model node.
3. `cb_step_3` [user_choice] — In the "Orbit landmarks" section, choose the orbit landmarks node.
   - Ask user: In the "Orbit landmarks" section, choose the orbit landmarks node.
4. `cb_step_4` [user_choice] — In the "Plate landmarks" section, choose the plate landmarks node.
   - Ask user: In the "Plate landmarks" section, choose the plate landmarks node.
5. `cb_step_5` [extension_op] — Click "Initial registration" button.
6. `cb_step_6` [extension_op] — Click "Posterior stop and antero-posterior stops alignment" button.
7. `cb_step_7` [extension_op] — Tick the "Enable 3D interaction transform handle" checkbox.
8. `cb_step_8` [user_interaction] — Manually adjust the position and rotation of the plate.
   - Interaction: generic
9. `cb_step_9` [extension_op] — Click "Mark intersection" button.
10. `cb_step_10` [extension_op] — Click "Create Distance Heatmap" button.

**Protocol:**
1. Call `SlicerOrbitSurgerySim` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
2. For **extension_op** and **slicer_op** steps: output the returned `code` verbatim in a ```python block. Then call the next step.
3. For **user_interaction** steps: output the returned `pre_code` verbatim in a ```python block. Relay instructions to the user. Wait for them to click 'Done'.
4. For **user_choice** steps: ask the returned question. After the user answers, call the same step with `user_action='choice_made'` and `choice_value`.
5. After each step completes, call the tool with the NEXT step's `step_id` and `user_action='start'`.
6. Continue until all steps are done.

**CRITICAL RULES:**
- Execute ONE step per turn. Do NOT call multiple steps in a single turn.
- Do NOT skip extension_op or slicer_op steps. Their code MUST be output and executed.
- Always start from step 1 (`cb_step_1`) and proceed in order.