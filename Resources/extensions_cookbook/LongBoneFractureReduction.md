## Surgical Planning for Reverse Shoulder Arthroplasty

1. [op=user_choice] In the "Input volume" section, select the CT volume for processing.
2. [op=slicer_op] In the "Segment Editor" module, create a new segmentation named "Reference_Segmentation".
3. [op=slicer_op] In the "Segment Editor" module, click the "Add" button and rename the segment to "Reference_Segment" under "Reference_Segmentation".
4. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
5. [op=user_choice] In the "Segment Editor" module, adjust the threshold slider to set the segmentation range. 
6. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
7. [op=slicer_op] In the "Segment Editor" module, click the "Islands" button.
8. [op=slicer_op] In the "Segment Editor" module, select the "Keep selected island" option.
9. [op=user_interaction] In the 2D view, click to select the reference part.
10. [op=slicer_op] Set the segment "Reference_Segment" invisible.
11. [op=slicer_op] In the "Segment Editor" module, create a new segmentation named "Moving_Segmentation".
12. [op=slicer_op] In the "Segment Editor" module, click the "Add" button and rename the segment to "Moving_Segment" under "Moving_Segmentation".
13. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
14. [op=user_choice] In the "Segment Editor" module, adjust the threshold slider to set the segmentation range. 
15. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
16. [op=slicer_op] In the "Segment Editor" module, click the "Islands" button.
17. [op=slicer_op] In the "Segment Editor" module, select the "Keep selected island" option.
18. [op=user_interaction] In the 2D view, click to select the moving part.
19. [op=slicer_op] Set the segment "Moving_Segment" invisible.
20. [op=user_choice] In the "Reference segmentation (blue)" section, select the reference segmentation node.
21. [op=extension_op] Click the "3D Reconstruction (reference)" button.
22. [op=user_choice] In the "Moving segmentation (blue)" section, select the moving segmentation node.
23. [op=extension_op] Click the "3D Reconstruction (moving)" button.
24. [op=extension_op] Click the "Add / reset reference ROI" button.
25. [op=user_interaction] Manually adjust the boundaries of the ROI to retain the fractured part of the reference model.
26. [op=extension_op] Click the "Add / reset moving ROI" button.
27. [op=user_interaction] Manually adjust the boundaries of the ROI to retain the fractured part of the moving model.
28. [op=extension_op] Click the "Detect fracture surfaces" button.
29. [op=extension_op] Click the "Reduce fracture" button.
30. [op=branch_op] If further adjustments are required, check the "Manually adjust the moving fragment" box. If not, stop here.
31. [op=user_interaction] Manually adjust the moving fragment.
32. [op=extension_op] Click the "Harden transform into moving fragment" button.

