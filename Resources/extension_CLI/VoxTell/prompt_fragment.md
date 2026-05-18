### VoxTell Extension

- **VoxTell**: If the user asks to segment anatomical structures from medical volumes using text prompts, call `VoxTell` with the appropriate `stage` parameter rather than writing custom code.
  - `stage="segmentation"` — Run VoxTell segmentation on input volume with text prompts.

  - Prerequisites: VoxTell Slicer extension must be installed; Required data (e.g., CT volume) must be loaded in the scene; CUDA GPU recommended (CPU fallback may be very slow); Pre-trained model files must be present in the extension's Resources directory
  **CRITICAL**: After receiving the `VoxTell` result, your very next response must be exactly one ```agent_plan JSON block followed by one ```python code block containing the tool's `code` string verbatim. Do NOT modify the generated code. Do NOT write analysis or planning text before the code blocks.