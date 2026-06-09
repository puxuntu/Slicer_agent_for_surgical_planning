### BoneReconstructionPlanner

Generated CLI package status: validated.

Available tool: `BoneReconstructionPlanner`.

Execute cookbook workflow steps in order. For automated steps, run the returned code. For interactive or mixed steps, run the pre-code, wait for the user to finish the requested interaction, then run the post-code.

Workflow steps:
- `cb_step_1` [user_choice]: If the fibula is from the right leg, tick the "Right side leg" checkbox.
- `cb_step_2` [user_choice]: In the "Select mandibular segmentation" section, choose the mandibular segmentation.
- `cb_step_3` [user_choice]: In the "Select fibula segmentation" section, choose the fibula segmentation.
- `cb_step_4` [user_choice]: For the "Current Scalar Volume" option, select the Mandible Volume.
- `cb_step_5` [extension_op]: Click "Create bone models from segmentations" button.
- `cb_step_6` [slicer_op]: Change the layout to "Conventional".
- `cb_step_7` [slicer_op]: For the R (red) view, toggle on "slice visibility in 3D view".
- `cb_step_8` [slicer_op]: For the R (red) view, toggle on "FOV, Spacing match 2D" (adjusts slice resolution to match the 2D viewport pixel spacing).
- `cb_step_9` [slicer_op]: In the toolbar, turn on "slice intersection visibility". In the slice intersection interaction options, turn on "set interaction", then enable both "Translate" and "Rotate".
- `cb_step_10` [user_interaction]: Manually adjust the slice intersection position by translate and rotate of the cross lines in each view.
- `cb_step_11` [extension_op]: Click the "Add mandibular curve" button.
- `cb_step_12` [slicer_op]: Configure the display settings of the mandibular curve created by the "Add mandibular curve" button so it is shown in both "View 1" and "Red".
- `cb_step_13` [user_interaction]: Manually click and draw on the "Red" view to create a curve along the mandible.
- `cb_step_14` [slicer_op]: Change the layout to "BoneReconstructionPlanner".
- `cb_step_15` [slicer_op]: For the R (red) view, toggle off "slice visibility in 3D view".
- `cb_step_16` [user_choice]: Manually set how many cut planes you want.
- `cb_step_17` [extension_op]: Click "Add cut plane" button.
- `cb_step_18` [user_interaction]: Place one mandibular cut plane using the extension's Add cut plane workflow. If the user requested N cut planes, repeat the Add cut plane + place plane interaction N times. Do not store these planes as a rotation plane; they are mandibular cut planes managed by the extension.
- `cb_step_19` [extension_op]: Click "Add fibula line" button.
- `cb_step_20` [user_interaction]: Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
- `cb_step_21` [extension_op]: Click "Center fibula line using fibula model" button to align the line with the anatomical axis of the fibula.
- `cb_step_22` [extension_op]: Tick the "Automatic mandibular planes positioning for maximum bones contact area" checkbox.
- `cb_step_23` [extension_op]: Tick the "Make all mandible planes rotate together" checkbox.
- `cb_step_24` [extension_op]: Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the fibula cut planes.
- `cb_step_25` [extension_op]: In the BoneReconstructionPlanner module, in the "Mandible planes" row, toggle on the eye-icon tool button to show the mandibular cut planes.
- `cb_step_26` [extension_op]: In the same "Mandible planes" row, toggle on the axes-icon tool button to show the plane interaction handles.
- `cb_step_27` [user_choice]: Enter the desired value in "Initial space (mm)".
- `cb_step_28` [user_choice]: Enter the desired value in "Between space (mm)".
- `cb_step_29` [user_interaction]: Manually adjust the mandibular cut planes in the mandible 3D view by dragging the visible plane interaction handles until the positions and rotations look correct.
- `cb_step_30` [extension_op]: Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to regenerate the reconstruction. Review the result; if it is not satisfactory, repeat steps 27-30 until the reconstruction is satisfactory.
- `cb_step_31` [extension_op]: When the reconstruction is satisfactory, in the BoneReconstructionPlanner module's "Mandible planes" row, toggle off the eye-icon tool button to hide the mandibular cut planes.
- `cb_step_32` [extension_op]: Clear the "Show original mandible model" checkbox.
