### PelvicFracturePlanning

Generated CLI package status: validated.

Available tool: `PelvicFracturePlanning`.

Execute cookbook workflow steps in order. For automated steps, run the returned code. For interactive or mixed steps, run the pre-code, wait for the user to finish the requested interaction, then run the post-code.

Workflow steps:
- `cb_step_1` [automated]: In the "Input CT Volume" option, choose the Pelvic Volume.
- `cb_step_2` [automated]: Click "Run Step 1: Segment Pelvis" button.
- `cb_step_3` [automated]: Click "Run Step 2: Segment Fractures" button.
- `cb_step_4` [automated]: In the "Untick any fragments to exclude it from planning" section, untick these segments.
- `cb_step_5` [automated]: Click "Run Step 3: Generate Template" button.
- `cb_step_6` [automated]: Click "Run Step 4: Register _Reduce" button.
- `cb_step_7` [automated]: Click "Run Step 4: Register _Reduce" button.
- `cb_step_8` [automated]: If further adjustments are required, tick the "Manually adjust a fragment" checkbox. If not, jump to step 10.
- `cb_step_9` [automated]: Choose which fragment needs adjustment in the "Fragment" selection box.
- `cb_step_10` [automated]: Manually adjust the position and rotation of the selected fragment.
- `cb_step_11` [automated]: Click the "Apply adjustments" button.
- `cb_step_12` [automated]: Click the "Plan Screws" button.
- `cb_step_13` [automated]: If further adjustments are required, tick the "Edit Screw trajectories" checkbox. If not, stop here.
- `cb_step_14` [automated]: Manually adjust the position and rotation of the screw trajectories.
- `cb_step_15` [automated]: Click the "Regenerate screw from edited lines" button.
- `cb_step_16` [automated]: Untick the "Edit Screw trajectories" checkbox.
