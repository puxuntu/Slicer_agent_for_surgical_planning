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
    clear_workflow_step_completions,
    dispatch_extension_cli_tool,
    find_next_workflow_step,
    get_validated_extensions,
    get_workflow_graph,
    mark_workflow_step_completed,
    reset_workflow_session,
    set_workflow_repeat_state,
)


WAIT_TYPES = {"interactive", "user_interaction", "user_choice"}
COMPLETE_TYPES = {
    "automated",
    "extension_op",
    "slicer_op",
    "interactive_done",
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
    repeat_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    completed_instances: List[Dict[str, Any]] = field(default_factory=list)
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
            "repeat_states": copy.deepcopy(self.session.repeat_states),
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
        ui_guidance = self._ui_guidance_from_result(source, current_meta)
        guidance_title = str(ui_guidance.get("title", "") or "").strip()
        guidance_instruction = str(ui_guidance.get("instruction", "") or "").strip()
        is_repeat_decision = result_type == "user_choice" and bool(source.get("repeat_decision"))
        if is_repeat_decision:
            # A loop continue/exit decision: surface the decision's own question
            # and instruction, NOT the underlying step's guidance. Otherwise the
            # panel shows e.g. "Regenerate reconstruction / Repeat steps 27-30 if
            # needed" — making the Yes/No buttons read as "Yes = repeat" when Yes
            # actually accepts and exits the loop.
            description = (
                source.get("question")
                or guidance_title
                or current_meta.get("description")
                or ""
            )
            instructions = source.get("instruction") or guidance_instruction
        elif result_type == "user_choice":
            description = (
                guidance_title
                or source.get("question")
                or source.get("explanation")
                or current_meta.get("description")
                or ""
            )
            instructions = guidance_instruction or self._instructions_from_result(source)
        else:
            description = (
                guidance_title
                or source.get("explanation")
                or source.get("instruction")
                or current_meta.get("description")
                or ""
            )
            instructions = guidance_instruction or self._instructions_from_result(source)
        choices = self._choices_from_result(source, current_meta)
        is_optional = bool(source.get("is_optional") or current_meta.get("is_optional"))
        choice_info = current_meta.get("choice_info", {}) if isinstance(current_meta, dict) else {}
        default_value = source.get("default_value")
        if default_value is None:
            default_value = choice_info.get("default_value")
        parameter_name = source.get("parameter_name") or choice_info.get("parameter_name") or ""
        repeat_progress = source.get("repeat_progress") or {}
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
            "choice_label": ui_guidance.get("choice_label", ""),
            "input_label": ui_guidance.get("input_label", ""),
            "done_label": ui_guidance.get("done_label", "Done") or "Done",
            "object_label": ui_guidance.get("object_label", ""),
            "repeat_progress": repeat_progress,
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
        call_args.setdefault("_workflow_id", self.session.workflow_id)

        self.session.current_step = target_step
        self.session.status = "running"
        repeat_decision = self._handle_pending_repeat_decision(
            target_step, action, call_args
        )
        if repeat_decision is not None:
            self.session.last_result = repeat_decision
            self._apply_pre_execution_state(repeat_decision)
            next_step = repeat_decision.get("next_step")
            if next_step:
                self.session.current_step = next_step.get("step_id")
                self.session.status = "running"
            else:
                self.session.current_step = None
                self.session.status = "completed"
                repeat_decision["workflow_completed"] = True
            self._write_event(
                "repeat_decision",
                {"args": call_args, "result": self._compact_result(repeat_decision)},
            )
            return repeat_decision

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

        if result_type in {"interactive", "user_interaction"}:
            self.session.status = "waiting_for_user"
            self.session.current_step = step_id
            self._write_event("step_waiting_for_user", {"step_id": step_id})
            return result

        if result_type == "user_choice":
            self.session.status = "waiting_for_choice"
            self.session.current_step = step_id
            self._write_event("step_waiting_for_choice", {"step_id": step_id})
            return result

        if result.get("repeat_decision"):
            # A loop continue/exit decision result is already fully transitioned
            # by _handle_pending_repeat_decision in run_step (body cleared +
            # iteration advanced for "repeat", or exit target chosen). Re-marking
            # its terminal step complete here would undo _clear_repeat_body and
            # make the loop skip its own body on the next pass. Just advance to
            # the already-computed next_step.
            next_step = result.get("next_step")
            if next_step:
                self.session.current_step = next_step.get("step_id")
                self.session.status = "running"
            else:
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

        if result_type in COMPLETE_TYPES and step_id:
            self._mark_completed(step_id)
            repeat_transition = self._repeat_transition_after_completion(
                step_id, result
            )
            if repeat_transition:
                result.update(repeat_transition)
                result_type = result.get("type")
                if result_type == "user_choice":
                    self.session.last_result = result
                    self.session.status = "waiting_for_choice"
                    self.session.current_step = step_id
                    return result
            elif not result.get("next_step"):
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
        elif result_type in {"interactive", "user_interaction"}:
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
            self.session.completed_instances.append({
                "step_id": step_id,
                "repeat": self._repeat_instance_for_step(step_id),
            })
        mark_workflow_step_completed(self.session.extension_name, step_id)

    def _next_step(self) -> Optional[Dict[str, Any]]:
        if not self.session:
            return None
        return find_next_workflow_step(
            self.session.extension_name,
            set(self.session.completed_steps),
        )

    def _repeat_blocks(self) -> List[Dict[str, Any]]:
        if not self.session:
            return []
        graph = get_workflow_graph(self.session.extension_name) or {}
        return [
            block for block in graph.get("repeat_blocks", []) or []
            if isinstance(block, dict) and block.get("repeat_id")
        ]

    def _repeat_instance_for_step(self, step_id: str) -> Dict[str, Any]:
        if not self.session:
            return {}
        for block in self._repeat_blocks():
            if step_id in (block.get("body_steps") or []):
                state = self.session.repeat_states.get(block["repeat_id"], {})
                return {
                    "repeat_id": block["repeat_id"],
                    "iteration": int(state.get("iteration", 1) or 1),
                }
        return {}

    def _sync_repeat_state(self, repeat_id: str) -> None:
        if not self.session:
            return
        state = self.session.repeat_states.get(repeat_id, {})
        set_workflow_repeat_state(
            self.session.extension_name,
            repeat_id,
            state,
        )

    def _clear_repeat_body(self, block: Dict[str, Any]) -> None:
        if not self.session:
            return
        body_steps = list(block.get("body_steps") or [])
        body_set = set(body_steps)
        self.session.completed_steps = [
            step_id for step_id in self.session.completed_steps
            if step_id not in body_set
        ]
        clear_workflow_step_completions(self.session.extension_name, body_steps)

    @staticmethod
    def _normalize_control_value(value: Any) -> Any:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "y", "1"}:
                return True
            if lowered in {"false", "no", "n", "0"}:
                return False
            try:
                return int(lowered)
            except ValueError:
                return value.strip()
        return value

    def _repeat_transition_after_completion(
        self,
        step_id: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return a control-flow transition after one atomic step succeeds."""
        if not self.session:
            return {}
        if result.get("repeat_decision"):
            return {}
        for block in self._repeat_blocks():
            repeat_id = block["repeat_id"]
            controller = block.get("controller", {}) or {}
            kind = controller.get("kind", "")
            state = self.session.repeat_states.setdefault(
                repeat_id, {"iteration": 1}
            )

            if kind == "count" and step_id == controller.get("source_step"):
                raw_target = self._normalize_control_value(result.get("choice_value"))
                try:
                    target = int(raw_target)
                except (TypeError, ValueError):
                    target = 0
                state.update({"iteration": 1, "target": max(0, target)})
                self._sync_repeat_state(repeat_id)
                if target <= 0:
                    for body_step in block.get("body_steps", []) or []:
                        self._mark_completed(body_step)
                    next_step = self._step_summary(block.get("exit_step"))
                    return {
                        "next_step": next_step,
                        "repeat_progress": {
                            "repeat_id": repeat_id,
                            "current": 0,
                            "completed": 0,
                            "total": 0,
                        },
                    }

            if step_id != block.get("terminal_step"):
                continue

            iteration = int(state.get("iteration", 1) or 1)
            max_iterations = int(block.get("max_iterations", 20) or 20)
            if kind == "count":
                target = int(state.get("target", 1) or 1)
                if iteration < min(target, max_iterations):
                    self._clear_repeat_body(block)
                    state["iteration"] = iteration + 1
                    self._sync_repeat_state(repeat_id)
                    return {
                        "next_step": self._step_summary(block.get("entry_step")),
                        "repeat_progress": {
                            "repeat_id": repeat_id,
                            "current": iteration + 1,
                            "completed": iteration,
                            "total": target,
                        },
                    }
                return {
                    "next_step": self._step_summary(block.get("exit_step")),
                    "repeat_limit_reached": target > max_iterations,
                    "repeat_progress": {
                        "repeat_id": repeat_id,
                        "current": iteration,
                        "completed": iteration,
                        "total": target,
                    },
                }

            if kind in {"until_choice", "while_choice"}:
                state["waiting_for_decision"] = True
                self._sync_repeat_state(repeat_id)
                prompt = controller.get("prompt") or "Continue the repeated workflow?"
                choices = [
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ]
                # Derive which answer exits vs repeats from the controller, so the
                # instruction is correct for both until_choice (exit on the exit
                # value) and while_choice. This makes the Yes/No meaning explicit
                # instead of leaving the user to guess.
                exit_value = self._normalize_control_value(controller.get("exit_value"))
                exit_label = next(
                    (c["label"] for c in choices
                     if self._normalize_control_value(c["value"]) == exit_value),
                    "Yes",
                )
                loop_label = next(
                    (c["label"] for c in choices
                     if self._normalize_control_value(c["value"]) != exit_value),
                    "No",
                )
                decision_instruction = (
                    f'Choose "{loop_label}" to repeat this section and refine the '
                    f'result; choose "{exit_label}" to accept it and continue.'
                )
                return {
                    "type": "user_choice",
                    "question": prompt,
                    "instruction": decision_instruction,
                    "choices": choices,
                    "parameter_name": f"repeat_decision:{repeat_id}",
                    "repeat_decision": repeat_id,
                    "repeat_progress": {
                        "repeat_id": repeat_id,
                        "current": iteration,
                        "completed": iteration,
                        "total": 0,
                    },
                    "next_step": None,
                }
        return {}

    def _handle_pending_repeat_decision(
        self,
        step_id: str,
        action: str,
        args: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if not self.session or action != "choice_made":
            return None
        for block in self._repeat_blocks():
            repeat_id = block["repeat_id"]
            state = self.session.repeat_states.get(repeat_id, {})
            if not state.get("waiting_for_decision"):
                continue
            if step_id != block.get("terminal_step"):
                continue
            controller = block.get("controller", {}) or {}
            choice = self._normalize_control_value(args.get("choice_value"))
            exit_value = self._normalize_control_value(controller.get("exit_value"))
            should_exit = choice == exit_value
            iteration = int(state.get("iteration", 1) or 1)
            max_iterations = int(block.get("max_iterations", 20) or 20)
            state["waiting_for_decision"] = False
            limit_reached = not should_exit and iteration >= max_iterations
            if should_exit or limit_reached:
                next_step = self._step_summary(block.get("exit_step"))
            else:
                self._clear_repeat_body(block)
                state["iteration"] = iteration + 1
                next_step = self._step_summary(block.get("entry_step"))
            self._sync_repeat_state(repeat_id)
            return {
                "tool": self.session.tool_name,
                "type": "choice_made",
                "step_id": step_id,
                "choice_value": choice,
                "repeat_decision": repeat_id,
                "repeat_limit_reached": limit_reached,
                "next_step": next_step,
                "repeat_progress": {
                    "repeat_id": repeat_id,
                    "current": int(state.get("iteration", iteration) or iteration),
                    "completed": iteration,
                    "total": 0,
                },
            }
        return None

    def _step_summary(self, step_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if not self.session or not step_id:
            return None
        graph = get_workflow_graph(self.session.extension_name) or {}
        for step in graph.get("steps", []) or []:
            if step.get("step_id") == step_id:
                return {
                    "step_id": step_id,
                    "operation_type": (
                        step.get("operation_type")
                        or step.get("op_type")
                        or step.get("step_type", "extension_op")
                    ),
                    "step_type": step.get("step_type", "extension_op"),
                    "description": step.get("description", ""),
                    "is_optional": bool(step.get("is_optional", False)),
                    "ui_guidance": step.get("ui_guidance", {}),
                }
        return None

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
    def _ui_guidance_from_result(result: Dict[str, Any], step_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Return generated UI guidance from result or workflow metadata."""
        guidance = {}
        if isinstance(step_meta, dict) and isinstance(step_meta.get("ui_guidance"), dict):
            guidance.update(step_meta["ui_guidance"])
        if isinstance(result, dict) and isinstance(result.get("ui_guidance"), dict):
            guidance.update(result["ui_guidance"])
        if isinstance(result, dict):
            interaction = result.get("interaction") or {}
            if isinstance(interaction, dict) and isinstance(interaction.get("ui_guidance"), dict):
                guidance.update(interaction["ui_guidance"])
        return guidance

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
            "ui_guidance",
            "repeat_progress",
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
