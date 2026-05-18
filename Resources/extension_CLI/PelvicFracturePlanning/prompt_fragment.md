### PelvicFracturePlanning Extension

- **PelvicFracturePlanning**: If the user asks to segment pelvic fractures and plan surgical screw placement, call `PelvicFracturePlanning` with the appropriate `stage` parameter rather than writing custom code.
  - `stage="segmentation"` — Performs pelvis and fracture segmentation on input volume, producing two segmentation nodes.
  - `stage="planning"` — Performs fracture reduction planning and screw planning using pelvis/fracture segmentations.
  - `stage="full"` — Run the complete pipeline: segmentation + planning
  - Prerequisites: PelvicFracturePlanning Slicer extension must be installed; Required data (e.g., CT volume) must be loaded in the scene; CUDA GPU recommended (CPU fallback may be very slow); Pre-trained model files must be present in the extension's Resources directory
  **CRITICAL**: After receiving the `PelvicFracturePlanning` result, your very next response must be exactly one ```agent_plan JSON block followed by one ```python code block containing the tool's `code` string verbatim. Do NOT modify the generated code. Do NOT write analysis or planning text before the code blocks.