import slicer

# Create an empty MarkupsFiducial node with the specified name
prosthesis_point_node = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode", "Prosthesis_center_point"
)

# Create default display nodes so the node is visible in views
prosthesis_point_node.CreateDefaultDisplayNodes()

# Verify that the node was created and named correctly
if prosthesis_point_node.GetName() != "Prosthesis_center_point":
    raise RuntimeError(
        "STATE_NOT_APPLIED: node name - expected 'Prosthesis_center_point', got '{}'".format(
            prosthesis_point_node.GetName()
        )
    )