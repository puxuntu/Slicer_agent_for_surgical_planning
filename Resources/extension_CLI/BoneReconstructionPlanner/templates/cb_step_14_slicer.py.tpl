# Switch to BoneReconstructionPlanner (BRP) custom layout
# The BRP layout ID is defined by the extension
if not hasattr(slicer, 'BRPLayoutId'):
    # If the extension has not set up the layout ID yet, define it here
    slicer.BRPLayoutId = 101

# Ensure the BRP layout description is registered (safe to call even if already registered)
layoutManager = slicer.app.layoutManager()
layoutNode = layoutManager.layoutLogic().GetLayoutNode()
if not layoutNode.IsLayoutDescription(slicer.BRPLayoutId):
    # Register the BRP layout: top row has mandible 3D view (left) + Red slice (right),
    # bottom row has fibula 3D view
    brpLayout = (
        '<layout type="vertical">'
        '<item>'
        '<layout type="horizontal">'
        '<item>'
        '<view class="vtkMRMLViewNode" singletontag="1">'
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
        '<view class="vtkMRMLViewNode" singletontag="2">'
        '<property name="viewlabel" action="default">2</property>'
        '</view>'
        '</item>'
        '</layout>'
    )
    layoutNode.AddLayoutDescription(slicer.BRPLayoutId, brpLayout)

# Switch to the BRP layout
layoutManager.setLayout(slicer.BRPLayoutId)