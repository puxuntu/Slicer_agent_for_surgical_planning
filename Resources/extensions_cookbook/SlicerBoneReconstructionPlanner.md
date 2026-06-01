## Virtual Surgical Planning

1. If the fibula is from the right leg, tick the "Right side leg" checkbox.
2. In the "Select mandibular segmentation" section, choose the mandibular segmentation.
3. In the "Select fibula segmentation" section, choose the fibula segmentation.
4. For the "Current Scalar Volume" option, select the Mandible Volume.
5. Click "Create bone models from segmentations" button.
6. Change the layout to "Conventional".
7. For the R (red) view, toggle on "slice visibility in 3D view".
8. For the R (red) view, select "FOV, Spacing match 2D" (adjusts slice resolution to match the 2D viewport pixel spacing).
9. In the toolbar, toggle on "slice intersection visibility" (Note it's not "crosshair visibility").
10. In the toolbar, toggle on "enable interaction" for "slice intersection visibility" (allows dragging the crosshair to navigate slices by clicking in 2D views).
11. Manually adjust the slice intersection position.
12. Click the "Add mandibular curve" button.
13. In the Markups module's "Display" > "Advanced" panel, configure "View" to show in both "View 1" and "Red".
14. Manually click and draw on the "Red" view to create a curve along the mandible.
15. Change the layout from "Conventional" back to the custom layout "BoneReconstructionPlanner" (restore the extension's dedicated layout).
16. For the R (red) view, toggle off "slice visibility in 3D view".
17. Manually set how many cut planes you want.
18. Click "Add cut plane" button.
19. Click where you want the plane in "3D View 1" to create the first plane. Repeat this process to add as many planes as needed.
20. Click "Add fibula line" button.
21. Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
22. Click "Center fibula line using fibula model" button to align the line with the anatomical axis of the fibula.
23. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the fibula cut planes.
