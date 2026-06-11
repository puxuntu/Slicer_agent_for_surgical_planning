from .common import *


PIPELINE_VERSION = "agentic-cli-v2"
MANIFEST_VERSION = 3


PHASES = {
    "discover": "Discover Source And Cookbook",
    "analyze": "Analyze Extension Logic",
    "contract": "Build Workflow Contract",
    "audit_contract": "Audit Workflow Contract",
    "ground": "Ground Slicer APIs",
    "generate": "Generate Schemas And Templates",
    "verify_repair": "Verify And Repair Templates",
    "package": "Package Validated CLI",
}


LEGACY_STAGE_TO_PHASE = {
    "1": "discover",
    "2": "discover",
    "3": "analyze",
    "3.5": "analyze",
    "4": "contract",
    "4.5": "contract",
    "5C": "contract",
    "5T": "ground",
    "6": "generate",
    "7": "generate",
    "7.5": "verify_repair",
    "8": "package",
    "9": "verify_repair",
    1: "discover",
    2: "discover",
    3: "analyze",
    4: "contract",
    6: "generate",
    7: "generate",
    8: "package",
    9: "verify_repair",
}


def canonical_phase_id(stage_or_phase: Any) -> str:
    value = str(stage_or_phase)
    return LEGACY_STAGE_TO_PHASE.get(stage_or_phase) or LEGACY_STAGE_TO_PHASE.get(value) or value


def phase_label(phase_id: str) -> str:
    return PHASES.get(phase_id, str(phase_id).replace("_", " ").title())


class AnalyzerPhaseMixin:
    def _set_phase(self, phase_id: str) -> None:
        self._current_stage_label = canonical_phase_id(phase_id)

    def _record_phase(self, result: Dict, phase_id: str) -> None:
        phase_id = canonical_phase_id(phase_id)
        phases = result.setdefault("phases_completed", [])
        if phase_id not in phases:
            phases.append(phase_id)
        stages = result.setdefault("stages_completed", [])
        if phase_id not in stages:
            stages.append(phase_id)

    def _phase_progress(self, phase_id: str, detail: str, label: Optional[str] = None) -> None:
        phase_id = canonical_phase_id(phase_id)
        self.on_progress(phase_id, label or phase_label(phase_id), detail)
