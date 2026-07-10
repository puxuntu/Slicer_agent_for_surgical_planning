## Surgical Planning for Reverse Shoulder Arthroplasty

1. [op=user_choice] In the "1. CT volume - bone density for optimization" section, select the CT volume for processing.
2. [op=slicer_op] In the "Segment Editor" module, create a new segmentation named "Bone_Segmentation".
3. [op=slicer_op] In the "Segment Editor" module, click the "Add" button and rename the segment to "Bone_Segment".
4. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
5. [op=user_choice] In the "Segment Editor" module, adjust the threshold slider to set the segmentation range. 
6. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
7. [op=slicer_op] In the "Segment Editor" module, click the "Islands" button.
8. [op=slicer_op] In the "Segment Editor" module, select the "Keep largest island" option.
9. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
10. [op=user_choice] In the "Bone segmentation" section, select the segment node.
11. [op=extension_op] Click the "3D Reconstruction" button.
12. [op=user_interaction] Manually adjust the 3D view to get the best angle for placing the fiducial point on the glenoid cavity surface.
13. [op=slicer_op] In the "Markups" module, click "Point List" to create an empty MarkupsFiducial node named "Prosthesis_center_point".
14. [op=user_interaction] Manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point".
15. [op=user_choice] In the "Planning point" section, select the MarkupsFiducial node.
16. [op=extension_op] Click the "Prosthesis implantation" button.
17. [op=branch_op] If further adjustments are required, check the "Adjust Prosthesis (3D transform handles)" box. If not, proceed to Step 20.
18. [op=user_interaction] Manually adjust the 3D transform handles.
19. [op=extension_op] Click the "Update Prosthesis" button.
20. [op=extension_op] Click the "Plan" button.
21. [op=branch_op] If further adjustments are required, check the "Adjust screw" box. If not, stop here.
22. [op=user_interaction] Manually adjust the endpoints of the planning paths.
23. [op=extension_op] Click the "Update screw" button.