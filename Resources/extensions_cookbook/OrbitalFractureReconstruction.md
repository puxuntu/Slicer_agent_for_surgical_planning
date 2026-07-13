## Surgical Planning for Orbital Fracture Reconstruction

1. [op=user_choice] In the "Input CT volume" section, select the CT volume for processing.
2. [op=slicer_op] In the "Markups" module, click "ROI" to create an empty MarkupsROI node named "Orbital_Region".
3. [op=user_interaction] Manually click and adjust on the Slice views to create the ROI for the "Orbital_Region".
4. [op=user_choice] In the "Bounding box (ROI)" section, select the MarkupsROI node.
5. [op=extension_op] Click the "Cut the volume with ROI" button.
6. [op=slicer_op] In the "Segment Editor" module, create a new segmentation named "Bone_Segmentation" for the "OFR_CutVolume" volume node.
7. [op=slicer_op] In the "Segment Editor" module, click the "Add" button and rename the segment to "Bone_Segment".
8. [op=slicer_op] In the "Segment Editor" module, click the "Threshold" button.
9. [op=user_choice] In the "Segment Editor" module, adjust the threshold slider to set the segmentation range. 
10. [op=slicer_op] In the "Segment Editor" module, click the "Apply" button.
11. [op=user_choice] In the "Bone segmentation" section, select the segment node.
12. [op=extension_op] Click the "Reconstruct full bone" button.
13. [op=user_choice] In the "Fractured side (pick the colored box over the fractured orbit)" section, select the segment node.
14. [op=extension_op] Click the "Segment orbit" button.
15. [op=extension_op] Click the "Reconstruct fractured" button.