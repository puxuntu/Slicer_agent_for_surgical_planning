## Pelvic Fracture Surgical Planning

1. Select the input CT volume. The extension expects a pelvic CT scan as input.
2. Click "Start Segmentation" to run pelvis and fracture segmentation. This uses a deep learning model to segment the pelvis and identify fracture fragments. The results are stored as segmentation nodes (pelvis segmentation and fracture segmentation).
3. Click "Start Planning" to generate the surgical plan. This performs fracture reduction (realigning fragments), generates 3D models, and computes screw placement trajectories. The results include a reduction segmentation node and a screw model node.
