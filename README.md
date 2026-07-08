# SlicerAIAgent4SurgicalPlaning

An AI-powered assistant for [3D Slicer](https://www.slicer.org/) that turns natural language into executable scene manipulation. Clinicians state their intent; the agent grounds it against the Slicer knowledge base, plans the steps, generates safe Python code, and runs it directly inside the application.

SlicerAIAgent operates in two complementary modes:

- **Autonomous Mode** — For open-ended requests. The agent interprets the goal, searches documentation and source code on the fly, produces a structured plan, generates executable Python, validates it, and executes it automatically. If something fails, it self-corrects in an isolated loop without polluting the conversation.
- **Guided Workflow Mode** — For complex, multi-step extension-based procedures. The system pre-generates validated operation templates from extension cookbooks and executes them deterministically, mixing automated code steps with interactive 3D operations where the user places curves, planes, or fiducials directly in the Slicer scene.

---

## Demos

### Demo 1 — Pelvic fracture reduction

https://github.com/user-attachments/assets/f3448345-08d9-45c8-9660-9fe4003c8f0b



---

### Demo 2 — Voxtell Segmentation

1. load an example CT chest volume
2. segment the Spine  
3. segment the left lung with the red color
4. segment the right lung with the green color
5. segment the rib with the yellow color

https://github.com/user-attachments/assets/59d5265e-e488-413f-84b5-55eb2f8a2da9

---

### Demo 3 — surgical planning of mandibular reconstruction

1. If the fibula is from the right leg, tick the "Right side leg" checkbox.
2. In the "Select mandibular segmentation" section, choose the mandibular segmentation.
3. In the "Select fibula segmentation" section, choose the fibula segmentation.
4. For the "Current Scalar Volume" option, select the Mandible Volume.
5. Click "Create bone models from segmentations" button.
6. Change the layout to "Conventional".
7. For the R (red) view, toggle on "slice visibility in 3D view".
8. For the R (red) view, toggle on "FOV, Spacing match 2D" (adjusts slice resolution to match the 2D viewport pixel spacing).
9. In the toolbar, turn on "slice intersection visibility". In the slice intersection interaction options, turn on "set interaction", then enable both "Translate" and "Rotate".
10. Manually adjust the slice intersection position by holding Shift and moving the mouse in a view.
11. Click the "Add mandibular curve" button.
12. Configure the display settings of the mandibular curve created by the "Add mandibular curve" button so it is shown in both "View 1" and "Red".
13. Manually click and draw on the "Red" view to create a curve along the mandible.
14. Change the layout to "BoneReconstructionPlanner".
15. For the R (red) view, toggle off "slice visibility in 3D view".
16. Manually set how many cut planes you want.
17. Click "Add cut plane" button.
18. Place one mandibular cut plane using the extension's Add cut plane workflow. If the user requested N cut planes, repeat the Add cut plane + place plane
  interaction N times. Do not store these planes as a rotation plane; they are mandibular cut planes managed by the extension.
19. Click "Add fibula line" button.
20. Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.
21. Click "Center fibula line using fibula model" button to align the line with the anatomical axis of the fibula.
22. Click "Update fibula planes over fibula line; update fibula bone pieces and transform them to mandible" to generate the reconstruction and create the fibula cut planes.

https://github.com/user-attachments/assets/182ba9f6-1c55-4539-ad53-9f9dadfb5388

### Demo 4 — Orbit Surgery Simulation

https://github.com/user-attachments/assets/fdef73cf-6d79-4f96-879f-c250b057894c

---

## Related Projects & Acknowledgments

- **[slicer-skill](https://github.com/pieper/slicer-skill)** — The foundational Claude skill for 3D Slicer that pioneered the MCP integration and local documentation indexing workflow.
- **[SlicerClaw](https://github.com/jumbojing/slicerClaw)** — A lightning-fast AI assistant natively integrated into 3D Slicer.
- **[mcp-slicer](https://github.com/zhaoyouj/mcp-slicer)** — A standalone MCP server for 3D Slicer by @zhaoyouj, installable via `pip` / `uvx`. It uses Slicer's built-in WebServer API as a bridge and can be launched outside of Slicer.
- **[SlicerDeveloperAgent](https://github.com/muratmaga/SlicerDeveloperAgent)** — A Slicer extension by Murat Maga that embeds an AI coding agent directly inside 3D Slicer using Gemini, letting users prompt, run, and iterate on scripts and modules without leaving the application. See the [Discourse discussion](https://discourse.slicer.org/t/developer-agent-for-slicer/44787) for background.
- **[NA-MIC Project Week 44 — Claude Scientific Skill for Imaging Data Commons](https://projectweek.na-mic.org/PW44_2026_GranCanaria/Projects/ClaudeScientificSkillForImagingDataCommons/)** — A project that developed a Claude skill for the [Imaging Data Commons](https://portal.imaging.datacommons.cancer.gov/) (IDC), published at [ImagingDataCommons/idc-claude-skill](https://github.com/ImagingDataCommons/idc-claude-skill).
- **[SlicerChat: Building a Local Chatbot for 3D Slicer](https://arxiv.org/abs/2407.11987)** (Barr, 2024) — Explores integrating a locally-run LLM (Code-Llama Instruct) into 3D Slicer to assist users with the software's steep learning curve, investigating the effects of fine-tuning, model size, and domain knowledge on answer quality.
- **[Talk2View](https://talk2view.com/)** — A platform for conversational interaction with medical imaging data and visualization tools.
- **[VoxTell](https://github.com/MIC-DKFZ/VoxTell)** — A Slicer extension for text-promptable AI segmentation of anatomical structures, enabling natural-language-driven organ and tissue segmentation.
