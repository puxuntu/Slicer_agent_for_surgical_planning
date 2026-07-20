# SlicerAIAgent4SurgicalPlaning

An AI-powered assistant for [3D Slicer](https://www.slicer.org/) that turns natural language into executable scene manipulation. Clinicians state their intent; the agent grounds it against the Slicer knowledge base, plans the steps, generates safe Python code, and runs it directly inside the application.

SlicerAIAgent operates in two complementary modes:

- **Autonomous Mode** — For open-ended requests. The agent interprets the goal, searches documentation and source code on the fly, produces a structured plan, generates executable Python, validates it, and executes it automatically. If something fails, it self-corrects in an isolated loop without polluting the conversation.
- **Guided Workflow Mode** — For complex, multi-step extension-based procedures. The system pre-generates validated operation templates from extension cookbooks and executes them deterministically, mixing automated code steps with interactive 3D operations where the user places curves, planes, or fiducials directly in the Slicer scene.

---

## Demos

### Demo 1 — Mandible Reconstruction
https://github.com/user-attachments/assets/95f02328-f035-43c1-b8fe-8ea94b12766b

---
### Demo 2 — Skull Repairing
https://github.com/user-attachments/assets/729b5133-a568-48b4-8b04-894068f7a398

---
### Demo 3 — Pelvic fracture reduction 
https://github.com/user-attachments/assets/915ed031-f1cd-4312-bf5a-e4c51d0dbd18

---
### Demo 4 — Zygomatic Implantation 
https://github.com/user-attachments/assets/5321032a-aeb0-42cd-9f45-7929ed3d4e27

---
### Demo 5 — Orbit implant simulation 
https://github.com/user-attachments/assets/903a5fad-552c-4565-8048-8f9f961893f0

---
### Demo 6 — Reverse Shoulder Arthroplasty
https://github.com/user-attachments/assets/3d923801-38f4-498f-b452-7e306014c5c2

---
### Demo 7 — Pedicle Screw Placement Planning
https://github.com/user-attachments/assets/2622e5d5-1e8f-4915-b531-4ee800566df1

---
### Demo 8 — Long bone fracture reduction
https://github.com/user-attachments/assets/ee69d64e-7a5e-4c00-a3f1-43c1520e5199

---
### Demo 9 — Orbit Fracture Reconstruction
https://github.com/user-attachments/assets/3ab12682-b8d2-4355-8c33-5301fef68e4f

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
