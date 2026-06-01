import slicer
import BoneReconstructionPlanner

# Reuse existing logic instance if available
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlanner.BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure parameter node exists
parameterNode = logic.getParameterNode()

# Ensure required node references are set
# Mandible model
mandibleNode = parameterNode.GetNodeReference("mandibleModelNode")
if mandibleNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if n and "mandible" in n.GetName().lower():
            mandibleNode = n
            break
    if mandibleNode:
        parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleNode.GetID())

# Fibula model
fibulaNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if n and "fibula" in n.GetName().lower():
            fibulaNode = n
            break
    if fibulaNode:
        parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaNode.GetID())

# Decimated versions (optional, but needed if checked)
decMandible = parameterNode.GetNodeReference("decimatedMandibleModelNode")
if decMandible is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if n and "decimated" in n.GetName().lower() and "mandible" in n.GetName().lower():
            decMandible = n
            break
    if decMandible:
        parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decMandible.GetID())

decFibula = parameterNode.GetNodeReference("decimatedFibulaModelNode")
if decFibula is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if n and "decimated" in n.GetName().lower() and "fibula" in n.GetName().lower():
            decFibula = n
            break
    if decFibula:
        parameterNode.SetNodeReferenceID("decimatedFibulaModelNode", decFibula.GetID())

# Set parameter for kindOfMandibleResection if not set
if not parameterNode.GetParameter("kindOfMandibleResection"):
    parameterNode.SetParameter("kindOfMandibleResection", "Hemimandibulectomy")  # default

# Call the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("[BoneReconstructionPlanner] Step 22 completed: fibula planes, bone pieces, and transforms generated.")