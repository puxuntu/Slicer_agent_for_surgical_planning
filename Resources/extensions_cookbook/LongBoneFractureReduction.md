## Surgical Planning for Reverse Shoulder Arthroplasty

1. [op=user_choice] In the "Input volume" section, select the CT volume for processing.
2. [op=slicer_op] In the "Segment Editor" module, create a new segmentation as "bone_segmentation".
3. [op=slicer_op] In the "Segment Editor" module, click the "Add" button to add a new segment as "bone_segment".
4. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
5. [op=user_choice] In the "Segment Editor" module, adjust the threshold slider to set the segmentation range. 
6. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
7. [op=slicer_op] In the "Segment Editor" module, click the "Islands" button.
8. [op=slicer_op] In the "Segment Editor" module, select the "Split islands to segments" option.
9. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
10. [op=user_choice] In the "Reference segment (fixed)" section, select the reference segment node.
11. [op=extension_op] Click the "3D Reconstruction (reference)" button.
12. [op=user_choice] In the "Moving segment (repositioned)" section, select the moving segmentation node.
13. [op=extension_op] Click the "3D Reconstruction (moving)" button.
14. [op=extension_op] Click the "Detect fracture surfaces" button.
15. [op=extension_op] Click the "Reduction planning" button.
16. [op=branch_op] If further adjustments are required, check the "Manually adjust the moving fragment" box. If not, stop here.
17. [op=user_interaction] Manually adjust the moving fragment.
18. [op=extension_op] Click the "Harden transform into moving fragment" button.