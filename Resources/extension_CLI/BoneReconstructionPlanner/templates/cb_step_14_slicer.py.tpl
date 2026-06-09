# Switch to BoneReconstructionPlanner custom layout
# This custom layout shows: 3D Mandible View (top-left), Red Slice / Axial (top-right), and 3D Fibula View (bottom)

# Define the custom layout ID (must match the extension's convention)
slicer.BRPLayoutId = 101
slicer.MANDIBLE_VIEW_SINGLETON_TAG = "1"
slicer.FIBULA_VIEW_SINGLETON_TAG = "2"

# Register the custom layout description if not already registered
layoutManager = slicer.app.layoutManager()
layoutNode = layoutManager.layoutLogic().GetLayoutNode()

# Check if layout 101 is already described
existingLayout = layoutNode.GetLayoutDescription(slicer.BRPLayoutId)
if existingLayout == "":
    BRPLayout = (
        '<layout type="vertical">'
        '<item>'
        '<layout type="horizontal">'
        '<item>'
        '<view class="vtkMRMLViewNode" singletontag="' + slicer.MANDIBLE_VIEW_SINGLETON_TAG + '">'
        '<property name="viewlabel" action="default">1</property>'
        '</view>'
        '</item>'
        '<item>'
        '<view class="vtkMRMLSliceNode" singletontag="Red">'
        '<property name="orientation" action="default">Axial</property>'
        '<property name="viewlabel" action="default">R</property>'
        '<property name="viewcolor" action="default">#F34A33</property>'
        '</view>'
        '</item>'
        '</layout>'
        '</item>'
        '<item>'
        '<view class="vtkMRMLViewNode" singletontag="' + slicer.FIBULA_VIEW_SINGLETON_TAG + '">'
        '<property name="viewlabel" action="default">2</property>'
        '</view>'
        '</item>'
        '</layout>'
    )
    layoutNode.AddLayoutDescription(slicer.BRPLayoutId, BRPLayout)

# Switch to the BoneReconstructionPlanner layout
layoutManager.setLayout(slicer.BRPLayoutId)