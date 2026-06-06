## Virtual Surgical Planning

1. If the fibula is from the right leg, tick the "Right side leg" checkbox.
2. In the "Select mandibular segmentation" section, choose the mandibular segmentation.
3. In the "Select fibula segmentation" section, choose the fibula segmentation.
4. For the "Current Scalar Volume" option, select the Mandible Volume.
5. Click "Create bone models from segmentations" button.
6. Change the layout to "Conventional".
7. For the R (red) view, toggle on "slice visibility in 3D view".
8. For the R (red) view, toggle on "FOV, Spacing match 2D" (adjusts slice resolution to match the 2D viewport pixel spacing).
9. In the toolbar, turn on "slice intersection visibility". In the slice intersection interaction options, turn on "set interaction", then enable both "Translate" and "Rotate".
10. Manually adjust the slice intersection position by translate and rotate of the cross lines in each view.
11. Click the "Add mandibular curve" button.
12. Configure the display settings of the mandibular curve created by the "Add mandibular curve" button so it is shown in both "View 1" and "Red".
13. Manually click and draw on the "Red" view to create a curve along the mandible.
14. Change the layout to "BoneReconstructionPlanner".
15. For the R (red) view, toggle off "slice visibility in 3D view".
16. Manually set how many cut planes you want.
17. Click "Add cut plane" button.
18. Place one mandibular cut plane using the extension's Add cut plane workflow. If the user requested N cut planes, repeat the Add cut plane + place plane
  interaction N times. Do not store these planes as a rotation plane; they are mandibular cut planes managed by the extension.
19. Click "Add fibula line" button.
20. Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
21. Click "Center fibula line using fibula model" button to align the line with the anatomical axis of the fibula.
22. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the fibula cut planes.
