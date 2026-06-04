"""Deterministic runtime for validated generated extension CLI workflows."""

from __future__ import annotations

import copy
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .ExtensionCLILoader import (
    dispatch_extension_cli_tool,
    find_next_workflow_step,
    get_validated_extensions,
    get_workflow_graph,
    mark_workflow_step_completed,
    reset_workflow_session,
)


WAIT_TYPES = {"interactive", "mixed", "user_choice", "branch"}
COMPLETE_TYPES = {
    "automated",
    "interactive_done",
    "mixed_done",
    "choice_made",
    "skipped",
}


@dataclass
class WorkflowSession:
    """State for one generated CLI workflow run."""

    extension_name: str
    tool_name: str
    workflow_id: str
    current_step: Optional[str] = None
    status: str = "running"
    completed_steps: List[str] = field(default_factory=list)
    queued_prompts: List[str] = field(default_factory=list)
    last_result: Optional[Dict[str, Any]] = None
    started_at: float = field(default_factory=time.time)

    @property
    def active(self) -> bool:
        return self.status in {"running", "waiting_for_user", "waiting_for_choice"}


class WorkflowRuntime:
    """Run generated CLI workflow steps without re-entering the LLM loop."""

    def __init__(self, log_dir: Optional[str] = None):
        self.session: Optional[WorkflowSession] = None
        self.log_dir = log_dir

    def has_active_workflow(self) -> bool:
        return bool(self.session and self.session.active)

    def state_for_router(self) -> Dict[str, Any]:
        if not self.session:
            return {"active": False}
        return {
            "active": self.session.active,
            "extension_name": self.session.extension_name,
            "tool_name": self.session.tool_name,
            "workflow_id": self.session.workflow_id,
            "current_step": self.session.current_step,
            "status": self.session.status,
            "completed_steps": list(self.session.completed_steps),
        }

    def state_for_ui(self, result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return a compact, user-facing state for workflow progress UI."""
        if not self.session:
            return {"active": False}

        graph = get_workflow_graph(self.session.extension_name) or {}
        steps = graph.get("steps", []) if isinstance(graph, dict) else []
        step_ids = [step.get("step_id") for step in steps if step.get("step_id")]
        step_map = {step.get("step_id"): step for step in steps if step.get("step_id")}
        total_steps = graph.get("step_count") or len(steps)

        source = result if isinstance(result, dict) else self.session.last_result or {}
        next_step = source.get("next_step") or {}
        current_step = (
            source.get("step_id")
            or self.session.current_step
            or next_step.get("step_id")
        )
        current_meta = step_map.get(current_step, {})
        current_index = 0
        if current_step in step_ids:
            current_index = step_ids.index(current_step) + 1
        elif self.session.status == "completed" and total_steps:
            current_index = int(total_steps)

        completed_count = len(set(self.session.completed_steps))
        if self.session.status == "completed" and total_steps:
            completed_count = int(total_steps)

        result_type = source.get("type", "")
        status = self._ui_status_label(self.session.status, result_type)
        if result_type == "user_choice":
            description = (
                source.get("question")
                or source.get("explanation")
                or current_meta.get("description")
                or ""
            )
        else:
            description = (
                source.get("explanation")
                or source.get("instruction")
                or current_meta.get("description")
                or ""
            )
        instructions = self._instructions_from_result(source)
        choices = self._choices_from_result(source, current_meta)
        is_optional = bool(source.get("is_optional") or current_meta.get("is_optional"))
        choice_info = current_meta.get("choice_info", {}) if isinstance(current_meta, dict) else {}
        default_value = source.get("default_value")
        if default_value is None:
            default_value = choice_info.get("default_value")
        parameter_name = source.get("parameter_name") or choice_info.get("parameter_name") or ""
        active = self.session.active or self.session.status in {"completed", "cancelled"}

        return {
            "active": active,
            "extension_name": self.session.extension_name,
            "workflow_title": self._display_name(self.session.extension_name),
            "tool_name": self.session.tool_name,
            "workflow_id": self.session.workflow_id,
            "current_step": current_step,
            "current_index": current_index,
            "completed_steps": completed_count,
            "total_steps": int(total_steps or 0),
            "status": status,
            "raw_status": self.session.status,
            "result_type": result_type,
            "description": description,
            "instructions": instructions,
            "choices": choices,
            "default_value": default_value,
            "parameter_name": parameter_name,
            "needs_choice_input": result_type == "user_choice" and not choices,
            "can_done": self.session.status == "waiting_for_user",
            "can_skip": self.session.active and is_optional,
            "can_cancel": self.session.active,
        }

    def start_from_result(self, result: Dict[str, Any]) -> Optional[WorkflowSession]:
        """Create a session from a generated CLI tool result if needed."""
        if not isinstance(result, dict) or not result.get("tool"):
            return self.session
        tool_name = result.get("tool")
        ext_name = self._extension_name_for_tool(tool_name) or tool_name
        if not ext_name:
            return self.session
        if self.session and self.session.extension_name == ext_name and self.session.active:
            if result.get("step_id"):
                self.session.current_step = result.get("step_id")
            self._apply_pre_execution_state(result)
            return self.session
        workflow_id = f"{ext_name}_{int(time.time() * 1000)}"
        reset_workflow_session(ext_name)
        self.session = WorkflowSession(
            extension_name=ext_name,
            tool_name=tool_name,
            workflow_id=workflow_id,
            current_step=result.get("step_id"),
        )
        self._apply_pre_execution_state(result)
        self._write_event("workflow_started", {"initial_result": self._compact_result(result)})
        return self.session

    def start_for_extension(self, extension_name: str, tool_name: Optional[str] = None) -> WorkflowSession:
        """Start a session explicitly for a validated generated extension."""
        ext_data = get_validated_extensions().get(extension_name)
        if not ext_data:
            raise ValueError(f"Validated extension CLI not found: {extension_name}")
        resolved_tool = tool_name or self._tool_name_for_extension(ext_data) or extension_name
        workflow_id = f"{extension_name}_{int(time.time() * 1000)}"
        reset_workflow_session(extension_name)
        graph = get_workflow_graph(extension_name)
        first_step = find_next_workflow_step(extension_name, set())
        self.session = WorkflowSession(
            extension_name=extension_name,
            tool_name=resolved_tool,
            workflow_id=workflow_id,
            current_step=(first_step or {}).get("step_id"),
        )
        self._write_event("workflow_started", {"workflow": graph.get("name", extension_name)})
        return self.session

    def run_step(
        self,
        step_id: Optional[str] = None,
        action: str = "start",
        args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Dispatch one generated CLI step and return the generated result."""
        if not self.session:
            return {"type": "error", "error": "No active generated CLI workflow"}

        target_step = step_id or self.session.current_step
        if not target_step and action != "cancel":
            return {"type": "error", "error": "No current workflow step"}

        call_args = dict(args or {})
        call_args.setdefault("workflow_step", target_step)
        call_args.setdefault("user_action", action)

        self.session.current_step = target_step
        self.session.status = "running"
        result = dispatch_extension_cli_tool(self.session.tool_name, call_args)
        if result is None:
            result = {"type": "error", "error": f"Unknown workflow tool: {self.session.tool_name}"}
        elif isinstance(result, dict):
            result = copy.deepcopy(result)
            result.setdefault("tool", self.session.extension_name)
            result.setdefault("step_id", target_step)

        self.session.last_result = result
        self._apply_pre_execution_state(result)
        self._write_event("step_dispatched", {"args": call_args, "result": self._compact_result(result)})
        return result

    def handle_execution_result(
        self,
        step_result: Dict[str, Any],
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update workflow state after generated code execution completes."""
        if not self.session:
            return step_result
        result = dict(step_result or {})
        result_type = result.get("type")
        step_id = result.get("step_id") or self.session.current_step
        success = bool(execution_result.get("success")) and not execution_result.get("timed_out", False)

        if not success:
            self.session.status = "running"
            self._write_event("step_execution_failed", {
                "step_id": step_id,
                "error": execution_result.get("error"),
            })
            return result

        if result_type in {"interactive", "mixed"}:
            self.session.status = "waiting_for_user"
            self.session.current_step = step_id
            self._write_event("step_waiting_for_user", {"step_id": step_id})
            return result

        if result_type == "user_choice":
            self.session.status = "waiting_for_choice"
            self.session.current_step = step_id
            self._write_event("step_waiting_for_choice", {"step_id": step_id})
            return result

        if result_type in COMPLETE_TYPES and step_id:
            self._mark_completed(step_id)
            if not result.get("next_step"):
                result["next_step"] = self._next_step()

        next_step = result.get("next_step")
        if next_step:
            self.session.current_step = next_step.get("step_id")
            self.session.status = "running"
        elif result_type in COMPLETE_TYPES:
            self.session.current_step = None
            self.session.status = "completed"
            result["workflow_completed"] = True

        self._write_event("step_execution_completed", {
            "step_id": step_id,
            "result_type": result_type,
            "next_step": next_step,
            "workflow_completed": result.get("workflow_completed", False),
        })
        return result

    def queue_traditional_prompt(self, prompt: str) -> int:
        if not self.session:
            return 0
        self.session.queued_prompts.append(prompt)
        self._write_event("traditional_prompt_queued", {"prompt": prompt})
        return len(self.session.queued_prompts)

    def pop_queued_prompts(self) -> List[str]:
        if not self.session:
            return []
        queued = list(self.session.queued_prompts)
        self.session.queued_prompts.clear()
        return queued

    def get_prompt_fragment(self) -> str:
        if not self.session or not self.session.active:
            return ""
        completed = ", ".join(self.session.completed_steps) or "none"
        return (
            f"### Active Generated CLI Workflow: {self.session.extension_name}\n"
            f"- Workflow ID: {self.session.workflow_id}\n"
            f"- Status: {self.session.status}\n"
            f"- Current step: {self.session.current_step}\n"
            f"- Completed steps: {completed}\n"
        )

    def _apply_pre_execution_state(self, result: Dict[str, Any]) -> None:
        if not self.session or not isinstance(result, dict):
            return
        result_type = result.get("type")
        if result_type == "cancelled":
            self.session.status = "cancelled"
            self.session.current_step = None
        elif result_type == "user_choice":
            self.session.status = "waiting_for_choice"
            self.session.current_step = result.get("step_id")
        elif result_type in {"interactive", "mixed"}:
            self.session.status = "running"
            self.session.current_step = result.get("step_id")
        elif result_type == "skipped" and result.get("step_id"):
            self._mark_completed(result["step_id"])
            next_step = result.get("next_step") or self._next_step()
            if next_step:
                result["next_step"] = next_step
                self.session.current_step = next_step.get("step_id")
                self.session.status = "running"
            else:
                self.session.current_step = None
                self.session.status = "completed"

    def _mark_completed(self, step_id: str) -> None:
        if not self.session or not step_id:
            return
        if step_id not in self.session.completed_steps:
            self.session.completed_steps.append(step_id)
        mark_workflow_step_completed(self.session.extension_name, step_id)

    def _next_step(self) -> Optional[Dict[str, Any]]:
        if not self.session:
            return None
        return find_next_workflow_step(
            self.session.extension_name,
            set(self.session.completed_steps),
        )

    @staticmethod
    def _instructions_from_result(result: Dict[str, Any]) -> str:
        if not isinstance(result, dict):
            return ""
        if result.get("type") == "user_choice":
            return ""
        interaction = result.get("interaction") or {}
        return (
            interaction.get("placement_instructions")
            or result.get("interaction_instructions")
            or ""
        )

    @staticmethod
    def _choices_from_result(result: Dict[str, Any], step_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        source_choices = []
        if isinstance(result, dict):
            source_choices = result.get("choices") or []
        if not source_choices and isinstance(step_meta, dict):
            source_choices = (step_meta.get("choice_info") or {}).get("choices") or []
        if not source_choices and isinstance(result, dict):
            source_choices = WorkflowRuntime._choices_from_instruction(result.get("instruction", ""))
        choices = []
        for choice in source_choices:
            if not isinstance(choice, dict):
                continue
            label = str(choice.get("label", choice.get("value", ""))).strip()
            value = str(choice.get("value", label)).strip()
            if label or value:
                choices.append({"label": label or value, "value": value or label})
        return choices

    @staticmethod
    def _choices_from_instruction(instruction: str) -> List[Dict[str, Any]]:
        """Best-effort fallback for compact user_choice results."""
        choices = []
        for line in str(instruction or "").splitlines():
            match = re.match(r"\s*\d+[.)]\s+(.+?)\s*$", line)
            if not match:
                continue
            label = match.group(1).strip()
            if label:
                lowered = label.lower()
                if lowered == "yes":
                    value = "true"
                elif lowered == "no":
                    value = "false"
                else:
                    value = label
                choices.append({"label": label, "value": value})
        return choices

    @staticmethod
    def _ui_status_label(status: str, result_type: str = "") -> str:
        if status == "waiting_for_user":
            return "Waiting for your interaction"
        if status == "waiting_for_choice":
            return "Waiting for your choice"
        if status == "completed":
            return "Completed"
        if status == "cancelled":
            return "Cancelled"
        if result_type == "user_choice":
            return "Waiting for your choice"
        return "Running"

    @staticmethod
    def _display_name(name: str) -> str:
        text = str(name or "").replace("_", " ").replace("-", " ").strip()
        if not text:
            return "Workflow"
        return re.sub(r"(?<!^)(?=[A-Z])", " ", text).strip()

    @staticmethod
    def _tool_name_for_extension(ext_data: Dict[str, Any]) -> Optional[str]:
        for schema in ext_data.get("schemas", []):
            func = schema.get("function", {})
            if func.get("name"):
                return func["name"]
        return None

    @classmethod
    def _extension_name_for_tool(cls, tool_name: str) -> Optional[str]:
        for ext_name, ext_data in get_validated_extensions().items():
            if cls._tool_name_for_extension(ext_data) == tool_name:
                return ext_name
        return None

    @staticmethod
    def _compact_result(result: Dict[str, Any]) -> Dict[str, Any]:
        compact = {}
        for key in (
            "tool",
            "type",
            "step_id",
            "instruction",
            "explanation",
            "interaction_instructions",
            "question",
            "choices",
            "default_value",
            "next_step",
            "workflow_completed",
            "error",
        ):
            if key in result:
                compact[key] = result[key]
        if result.get("code"):
            compact["code_chars"] = len(result.get("code") or "")
        return compact

    def _write_event(self, event: str, payload: Dict[str, Any]) -> None:
        if not self.log_dir or not self.session:
            return
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            path = os.path.join(self.log_dir, "workflow_runtime.jsonl")
            entry = {
                "time": round(time.time(), 3),
                "event": event,
                "workflow_id": self.session.workflow_id,
                "extension_name": self.session.extension_name,
                "current_step": self.session.current_step,
                "status": self.session.status,
                "payload": payload,
            }
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        except Exception:
            pass
