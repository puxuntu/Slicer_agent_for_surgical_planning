## Surgical Planning for Cranial Implant Planning

1. [op=slicer_op] In the "Segmentation Editor" module, create new segmentation as "Cranial_Segmentation".
2. [op=user_choice] In the "Sourve Volume" selection section of "Segmentation Editor" module, choose the volume for segmentation.
3. [op=slicer_op] In the "Segmentation Editor" module, Click the "Add" botton to add a new segment as "Cranial_Segment".
4. [op=slicer_op] In the "Segmentation Editor" module, Click the "Threshold" botton.
5. [op=user_choice] In the "Segmentation Editor" module, set the Threshold Range including the lowest value and the largest value.
6. [op=slicer_op] In the "Segmentation Editor" module, Click the "Apply" botton.
7. [op=user_choice] In the "Skull Mask" section, choose the segment node.
8. [op=extension_op] Click "Load Skull Mask" button.
9. [op=extension_op] Click "Add ROI" button.
10. [op=user_interaction] Manually adjust the boundary of the ROI to keep the skull part.
11. [op=extension_op] Click "Crop to ROI" button.
12. [op=slicer_op]  In the "Markups" module, click the "Closed Curve" to create a closed curve node.
13. [op=user_interaction] Manually draw the curve on the skull model to include the fractured skull part.
14. [op=user_choice] In the "Curve selection" section, choose the Curve node.
15. [op=extension_op] Click "Cut Defect" button.
16. [op=extension_op] Click "Generate Implant" button.