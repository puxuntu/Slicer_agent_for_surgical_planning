## Surgical Planning for Cranial Implant Planning

1. [op=user_choice] In the "Segment Editor" module, under the "Source Volume" selection section, choose the volume for segmentation.
2. [op=slicer_op] In the "Segment Editor" module, create a new segmentation named "Cranial_Segmentation".
3. [op=slicer_op] In the "Segment Editor" module, click the "Add" button and rename the segment to "Cranial_Segment".
4. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
5. [op=user_choice] In the "Segment Editor" module, adjust the threshold range bar to set the range value for segmentation.
6. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
7. [op=slicer_op] In the "Segment Editor" module, click the "Islands" button.
8. [op=slicer_op] In the "Segment Editor" module, select the "Keep largest island" option.
9. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
10. [op=user_choice] In the "1. Pick the skull segmentation, then Load Skull Mask" section, choose the segment node.
11. [op=extension_op] Click the "Load Skull Mask" button.
12. [op=extension_op] Click the "Add ROI" button.
13. [op=user_interaction] Manually adjust the boundaries of the ROI to retain the skull portion.
14. [op=extension_op] Click the "Crop to ROI" button.
15. [op=user_interaction] Manually adjust the 3D view to get the best angle for placing the cutting curve.
16. [op=slicer_op] In the "Markups" module, click "Closed Curve" to create a closed curve node.
17. [op=user_interaction] Manually draw the curve on the skull model to enclose the fractured skull portion.
18. [op=user_choice] In the "Curve selection" section, choose the curve node.
19. [op=extension_op] Click the "Cut Defect" button.
20. [op=extension_op] Click the "Generate Implant" button.