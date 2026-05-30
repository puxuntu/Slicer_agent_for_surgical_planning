## Virtual Surgical Planning

1. If the fibula is from the right leg, tick the "Right side leg" checkbox.
2. In the "Select mandibular segmentation" section, choose the mandibular segmentation, and in the "Select fibula segmentation" section, choose the fibula segmentation.
3. For the "Current Scalar Volume" option, select the Mandible Volume.
4. Click "Create bone models from segmentations" botton. 
5. Change the layout to "Conventional". For the R (red) view, toggle on slice visibility in the 3D view. You should also toggle on slice intersection visibility and enable interaction. Then, you manually adjust the slice intersection position.
6. Click the "Add mandibular curve" button and open the "Markups" module. Expand the "Display" panel, then the "Advanced" panel, and set "View" to "View 1" with "Red" selected.
7. Manually click and draw on the "Red" view to create a curve along the mandible.
8. Change the layout from "Conventional" back to the custom layout "BoneReconstructionPlanner". For the R (red) view, toggle off the slice visibility in the 3D view.
9. Click "Add cut plane" botton and click where you want the plane in "3D View 1" to create the first plane. Repeat this process by clicking "Add cut plane" again to add as many planes as needed.
10. Click "Add fibula line." Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally. 
11. Click "Center fibula line using fibula model" botton to align the line with the anatomical axis of the fibula.
12. Tick the following options: "Automatic mandibular planes positioning for maximum bones contact area" and "Make all mandible planes rotate together."
13. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the fibula cut planes.
14. Move the mandible planes manually to change the position and orientation of the cuts.
