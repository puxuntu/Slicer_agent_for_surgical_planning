"""
Change the view layout to Conventional (3 slice views + 1 3D view).
"""
import slicer

# Access the layout manager
layoutManager = slicer.app.layoutManager()

# Set layout to Conventional (Axial, Sagittal, Coronal slices + 3D view)
layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)