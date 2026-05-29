### Interactive Workflow: BoneReconstructionPlanner

**Tool name:** `BoneReconstructionPlanner`
**Type:** Guided interactive workflow

This tool orchestrates a multi-step workflow where some steps require the user to
perform 3D interactions (drawing curves, positioning planes, placing fiducials).
Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user
and wait for them to complete the interaction before proceeding.

**Workflow Steps:**
1. `cb_step_1` [optional] — 1. If the fibula is from the right leg, tick the "Right side leg" checkbox.
2. `cb_step_2` [optional] — 2. In the "Select mandibular segmentation" section, choose the mandibular segmentation, and in the "Select fibula segmentation" section, choose the fi
3. `cb_step_3` [optional] — 3. For the "Current Scalar Volume" option, select the Mandible Volume.
4. `cb_step_4` [automated: extension_op] — 4. Click "Create bone models from segmentations" botton.
5. `cb_step_5` [mixed: automated + interaction] — 5. Change the layout to "Conventional". For the R (red) view, toggle on slice visibility in the 3D view. You should also toggle on slice intersection 
   - User interaction: fiducial
   - Tell user: Drag the slice intersection point in the 3D view to adjust its position.
6. `cb_step_6` [mixed: automated + interaction] — 6. Click the "Add mandibular curve" button and open the "Markups" module. Expand the "Display" panel, then the "Advanced" panel, and set "View" to "Vi
7. `cb_step_7` [interactive] — 7. Manually click and draw on the "Red" view to create a curve along the mandible.
   - Interaction: curve
   - Tell user: Click and draw on the Red slice view to create a curve along the mandible.
8. `cb_step_8` [mixed: automated + interaction] — 8. Change the layout from "Conventional" back to the custom layout "BoneReconstructionPlanner". For the R (red) view, toggle off the slice visibility 
9. `cb_step_9` [mixed: automated + interaction] — 9. Click "Add cut plane" botton and click where you want the plane in "3D View 1" to create the first plane. Repeat this process by clicking "Add cut 
   - User interaction: plane
   - Tell user: Click in 3D View 1 where you want the cut plane to be placed. Each click creates a new plane after clicking 'Add cut plane'.
10. `cb_step_10` [mixed: automated + interaction] — 10. Click "Add fibula line." Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
   - User interaction: line
   - Tell user: In 3D View 2, click the first point at the distal end of the fibula, then click the last point at the proximal end to create the line.
11. `cb_step_11` [automated: extension_op] — 11. Click "Center fibula line using fibula model" botton to align the line with the anatomical axis of the fibula.
12. `cb_step_12` [automated: extension_op] — 12. Tick the following options: "Automatic mandibular planes positioning for maximum bones contact area" and "Make all mandible planes rotate together
13. `cb_step_13` [automated: extension_op] — 13. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create 
14. `cb_step_14` [interactive] — 14. Move the mandible planes manually to change the position and orientation of the cuts.
   - Interaction: plane
   - Tell user: Drag and rotate the mandible planes in the 3D view to change their position and orientation for optimal cuts.

**Protocol:**
1. Call `BoneReconstructionPlanner` with `workflow_step='cb_step_1'` and `user_action='start'` to begin
2. For **automated** steps (extension_op and slicer_op): output the returned `code` verbatim in a ```python block. Then call the next step.
3. For **interactive** steps: output the returned `pre_code` verbatim in a ```python block. Relay instructions to the user. Wait for them to click 'Done'.
4. For **mixed** steps: output the returned `pre_code` verbatim. Then relay interaction instructions. Wait for 'Done'. Then output post_code.
5. For **optional** steps: ask user if they want to proceed. If yes, call with `user_action='start'`. If no, call with `user_action='skip'`.
6. After each step completes, call the tool with the NEXT step's `step_id` and `user_action='start'`.
7. Continue until all steps are done.

**CRITICAL RULES:**
- Execute ONE step per turn. Do NOT call multiple steps in a single turn.
- Do NOT skip automated steps. Their code MUST be output and executed.
- Always start from step 1 (`cb_step_1`) and proceed in order.