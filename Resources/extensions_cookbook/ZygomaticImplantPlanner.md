## Surgical Planning for Cranial Implant Planning

1. [op=user_choice] In the "Segment Editor" module, under the "Source Volume" selection section, choose the volume for segmentation.
2. [op=slicer_op] In the "Segment Editor" module, create a new segmentation named "Cranial_Segmentation".
3. [op=slicer_op] In the "Segment Editor" module, click the "Add" button and rename the segment to "Cranial_Segment".
4. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
5. [op=user_choice] In the "Segment Editor" module, adjust the threshold range bar to set the range value for segmentation.
6. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
7. [op=user_choice] In the "Skull segmentation" section, choose the segment node.
8. [op=user_choice] In the "Entry points" section, choose the Point List node.
9. [op=extension_op] Click the "1. Compute symmetry plane" button.
10. [op=user_choice] In the "Crop radius (mm)" section, adjust the range bar to set the range value for crop.
11. [op=extension_op] Click the "2. Cut skull (cylinder)" button.
12. [op=extension_op] Click the "3. Seperate maxilla / mandible" button.
13. [op=branch_op] If further adjustments are required, tick the "Manually adjust the segmentation plane" checkbox. If not, jump to step 16.
14. [op=user_interaction] Manually adjust the separation plane.
15. [op=extension_op] Click the "Apply separation" button.
16. [op=extension_op] Click the "4. Identify zygomatic bones" button.
17. [op=branch_op] If further adjustments are required, tick the "Manually adjust the boundary planes" checkbox. If not, jump to step 20.
18. [op=user_interaction] Manually adjust the boundary planes.
19. [op=extension_op] Click the "Apply boundaries" button.
20. [op=extension_op] Click the "5. Generate Implant paths" button.
21. [op=branch_op] If further adjustments are required, tick the "Manually adjust the paths" checkbox. If not, stop here.
22. [op=user_interaction] Manually adjust the paths.
23. [op=extension_op] Click the "Apply paths" button.