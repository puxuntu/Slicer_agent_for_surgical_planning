### BoneReconstructionPlanner

Generated CLI package status: validated.

Available tool: `BoneReconstructionPlanner`.

Execute cookbook workflow steps in order. For automated steps, run the returned code. For interactive or mixed steps, run the pre-code, wait for the user to finish the requested interaction, then run the post-code.

Workflow steps:
- `cb_step_1` [user_choice]: 1. If the fibula is from the right leg, tick the "Right side leg" checkbox.
- `cb_step_2` [user_choice]: 2. In the "Select mandibular segmentation" section, choose the mandibular segmentation.
- `cb_step_3` [user_choice]: 3. In the "Select fibula segmentation" section, choose the fibula segmentation.
- `cb_step_4` [user_choice]: 4. For the "Current Scalar Volume" option, select the Mandible Volume.
- `cb_step_5` [automated]: 5. Click "Create bone models from segmentations" button.
- `cb_step_6` [automated]: 6. Change the layout to "Conventional".
- `cb_step_7` [automated]: 7. For the R (red) view, toggle on "slice visibility in 3D view".
- `cb_step_8` [automated]: 8. For the R (red) view, select "FOV, Spacing match 2D" (adjusts slice resolution to match the 2D viewport pixel spacing).
- `cb_step_9` [automated]: 9. In the "Crosshair selection" toolbar, toggle on "slice intersection visibility" (shows crosshair lines at slice intersections in 2D views).
- `cb_step_10` [automated]: 10. In the "Crosshair selection" toolbar, toggle on "enable interaction" (allows dragging the crosshair to navigate slices by clicking in 2D views).
- `cb_step_11` [interactive]: 11. Manually adjust the slice intersection position.
- `cb_step_12` [automated]: 12. Click the "Add mandibular curve" button.
- `cb_step_13` [automated]: 13. In the Markups module's "Display" > "Advanced" panel, configure "View" to show in both "View 1" and "Red".
- `cb_step_14` [interactive]: 14. Manually click and draw on the "Red" view to create a curve along the mandible.
- `cb_step_15` [automated]: 15. Change the layout from "Conventional" back to the custom layout "BoneReconstructionPlanner" (restore the extension's dedicated layout).
- `cb_step_16` [automated]: 16. For the R (red) view, toggle off "slice visibility in 3D view".
- `cb_step_17` [user_choice]: 17. Manually set how many cut planes you want.
- `cb_step_18` [automated]: 18. Click "Add cut plane" button.
- `cb_step_19` [interactive]: 19. Click where you want the plane in "3D View 1" to create the first plane. Repeat this process to add as many planes as needed.
- `cb_step_20` [automated]: 20. Click "Add fibula line" button.
- `cb_step_21` [interactive]: 21. Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
- `cb_step_22` [automated]: 22. Click "Center fibula line using fibula model" button to align the line with the anatomical axis of the fibula.
- `cb_step_23` [automated]: 23. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the fibula cut planes.
