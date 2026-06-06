from .common import *


class SlicerOpGeneratorRunMixin:
    def generate(self, sub_ops: List[tuple]) -> Dict[str, str]:
        """Generate code templates for all slicer_op sub-operations.

        Args:
            sub_ops: List of (step_number, SubOperation) tuples.

        Returns:
            Dict mapping "cb_step_{num}_{idx}" -> template code string.
        """
        import time as _time
        import threading as _threading
        import json as _json

        self._ensure_executor()

        results: Dict[str, str] = {}
        total = len(sub_ops)
        started = [0]
        finished = [0]
        lock = _threading.Lock()
        errors: list = []
        debug_log: list = []
        timed_out_keys = set()

        def _write_debug():
            if not self._debug_path:
                return
            try:
                with open(self._debug_path, "w", encoding="utf-8") as f:
                    _json.dump({
                        "stage": "5T",
                        "debug_schema_version": 2,
                        "debug_features": [
                            "slicer_op_classification",
                            "slicer_ui_analysis_evidence_audit",
                            "source_verification_summary",
                            "generated_code_preview",
                            "final_state_intent",
                        ],
                        "total_operations": total,
                        "started": started[0],
                        "finished": finished[0],
                        "errors_count": len(errors),
                        "operations": debug_log,
                    }, f, indent=2)
            except Exception:
                pass

        if not sub_ops:
            return results

        def _emit_progress(finished_count: int, total_count: int, detail: str):
            if not self._on_progress:
                return
            try:
                self._on_progress(finished_count, total_count, detail)
            except Exception:
                logger.debug("[5T] progress callback failed", exc_info=True)

        def _gen_one(item: tuple, idx: int) -> Tuple[str, str]:
            step_num, sub_op = item
            key = f"cb_step_{step_num}_{idx}"
            desc_short = sub_op.description.split("\n")[0][:60]
            category = self._infer_category(sub_op)
            t0 = _time.monotonic()

            op_record = {
                "step": step_num,
                "key": key,
                "description": sub_op.description[:200],
                "keywords": sub_op.slicer_api_keywords[:10],
                "category": category,
                "final_state_intent": infer_final_state_intent(
                    " ".join([
                        getattr(sub_op, "description", "") or "",
                        " ".join(getattr(sub_op, "slicer_api_keywords", []) or []),
                    ])
                ),
                "classification": {
                    "op_type": getattr(sub_op, "op_type", "slicer_op"),
                    "evidence_type": getattr(sub_op, "evidence_type", None),
                    "evidence_id": getattr(sub_op, "evidence_id", None),
                    "confidence": getattr(sub_op, "confidence", None),
                    "interaction_kind": getattr(sub_op, "interaction_kind", None),
                    "node_class": getattr(sub_op, "node_class", None),
                    "slicer_op_category": getattr(sub_op, "slicer_op_category", None),
                },
                "search_policy": {
                    "preferred_root": "slicer-ui-analysis",
                    "requires_ui_first_when_ui_labeled": True,
                    "category_hints": _CATEGORY_SEARCH_HINTS.get(category, [])[:10],
                },
                "status": "started",
                "total_time_s": None,
                "code_chars": 0,
                "tool_rounds": None,
                "api_calls": None,
                "error": None,
                "progress_events": [],
            }

            with lock:
                started[0] += 1
                started_idx = started[0]
                debug_log.append(op_record)
            logger.info(
                "[5T] step %d STARTED [%d/%d]: %s",
                step_num, started_idx, total, desc_short,
            )
            _write_debug()
            _emit_progress(finished[0], total, f"started {desc_short}")

            def _emit_op_progress(detail: str):
                with lock:
                    if key in timed_out_keys:
                        return
                _emit_progress(finished[0], total, f"{desc_short}: {detail}")

            try:
                code, status = self._generate_one(
                    sub_op, category, op_record, lock, _write_debug,
                    emit_progress=_emit_op_progress,
                )
                t1 = _time.monotonic()

                with lock:
                    timed_out = key in timed_out_keys
                if timed_out:
                    return key, code

                op_record["status"] = status
                op_record["total_time_s"] = round(t1 - t0, 2)
                op_record["code_chars"] = len(code)

                logger.info(
                    "[5T] step %d done: %.1fs, code=%d chars, status=%s  %s",
                    step_num, t1 - t0, len(code), status, desc_short,
                )

                if status == "fallback":
                    with lock:
                        errors.append(
                            f"Step {step_num} ({desc_short}): used fallback template"
                        )

                return key, code
            except Exception as exc:
                err_msg = f"Step {step_num} FAILED: {type(exc).__name__}: {exc}"
                with lock:
                    timed_out = key in timed_out_keys
                if timed_out:
                    return key, (
                        f"# Timed out or failed after timeout: {sub_op.description}\n"
                        f"# Error: {exc}\npass"
                    )
                op_record["status"] = "failed"
                op_record["error"] = err_msg
                logger.exception("[5T] %s", err_msg)
                with lock:
                    errors.append(err_msg)
                return key, f"# Failed to generate slicer_op: {sub_op.description}\n# Error: {exc}\npass"
            finally:
                with lock:
                    timed_out = key in timed_out_keys
                    if timed_out:
                        fin = finished[0]
                    else:
                        finished[0] += 1
                        fin = finished[0]
                _write_debug()
                if not timed_out:
                    _emit_progress(fin, total, f"done {desc_short}")

        logger.info("[5T] Starting generation of %d slicer_op templates (sequential)", total)
        _write_debug()
        _emit_progress(0, total, f"starting {total} slicer_op templates")

        for idx, item in enumerate(sub_ops):
            step_num, sub_op = item
            desc = sub_op.description[:60]
            key = f"cb_step_{step_num}_{idx}"
            pool = ThreadPoolExecutor(max_workers=1)
            future = pool.submit(_gen_one, item, idx)
            try:
                result_key, code = future.result(timeout=_PER_OP_TIMEOUT_S)
                results[result_key] = code
            except FuturesTimeoutError:
                err_msg = (
                    f"Step {step_num} ({desc}): timed out after "
                    f"{_PER_OP_TIMEOUT_S}s"
                )
                logger.warning("[5T] %s", err_msg)
                future.cancel()
                with lock:
                    timed_out_keys.add(key)
                    errors.append(err_msg)
                    for rec in debug_log:
                        if rec.get("key") == key:
                            rec["status"] = "timeout"
                            rec["error"] = err_msg
                            break
                results[key] = f"# Timed out: {desc}\npass"
                _write_debug()
                _emit_progress(finished[0], total, err_msg)
            except Exception as exc:
                err_type = type(exc).__name__
                err_msg = f"Step {step_num} ({desc}): {err_type}: {exc}"
                logger.warning("[5T] %s", err_msg)
                with lock:
                    errors.append(err_msg)
                    for rec in debug_log:
                        if rec.get("key") == key:
                            rec["status"] = "failed"
                            rec["error"] = err_msg
                            break
                results[key] = f"# Timed out or failed: {desc}\n# {err_type}: {exc}\npass"
                _write_debug()
                _emit_progress(finished[0], total, err_msg)
            finally:
                pool.shutdown(wait=False, cancel_futures=True)

        logger.info(
            "[5T] Generation complete: %d/%d succeeded, %d errors",
            len(results) - len(errors), total, len(errors),
        )
        if errors:
            logger.warning("[5T] Errors:\n  %s", "\n  ".join(errors))

        _write_debug()
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generation_failed_template(sub_op, reason: str) -> str:
        desc = getattr(sub_op, "description", "")
        safe_reason = reason.replace('"', "'")
        return (
            f"# [{_GENERATION_FAILED_SENTINEL}] {safe_reason}\n"
            f"# Operation: {desc}\n"
            "raise RuntimeError("
            f"\"Slicer-op template generation failed: {safe_reason}\""
            ")\n"
        )

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Remove surrounding ```python ... ``` fences."""
        text = text.strip()
        if text.startswith("```"):
            nl = text.find("\n")
            if nl >= 0:
                text = text[nl + 1:]
            if text.rstrip().endswith("```"):
                text = text.rstrip()[:-3].rstrip()
        return text
