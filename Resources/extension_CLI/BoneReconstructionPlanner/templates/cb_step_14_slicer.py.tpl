# Switch to the BoneReconstructionPlanner custom layout
# The layout ID is defined by the extension as 101
slicer.BRPLayoutId = 101

# Register the layout description if not already registered
layoutManager = slicer.app.layoutManager()
layoutNode = layoutManager.layoutLogic().GetLayoutNode()
if not layoutNode.IsLayoutDescription(slicer.BRPLayoutId):
    # Layout definition: vertical split with mandible 3D view + Red slice on top,
    # and fibula 3D view on bottom
    BRPLayout = """\
    <layout type="vertical">
    <item>
      <layout type="horizontal">
      <item>
        <view class="vtkMRMLViewNode" singletontag="1">
        <property name="viewlabel" action="default">1</property>
        </view>
      </item>
      <item>
        <view class="vtkMRMLSliceNode" singletontag="Red">
        <property name="orientation" action="default">Axial</property>
        <property name="viewlabel" action="default">R</property>
        <property name="viewcolor" action="default">#F34A33</property>
        </view>
      </item>
      </layout>
    </item>
    <item>
      <view class="vtkMRMLViewNode" singletontag="2">
      <property name="viewlabel" action="default">2</property>
      </view>
    </item>
    </layout>
    """
    layoutNode.AddLayoutDescription(slicer.BRPLayoutId, BRPLayout)

# Activate the BoneReconstructionPlanner layout
layoutManager.setLayout(slicer.BRPLayoutId)