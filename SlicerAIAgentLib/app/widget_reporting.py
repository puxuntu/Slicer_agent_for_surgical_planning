from .common import *


class WidgetReportingMixin:
    def _updateTokenLabel(self):
        """Update the token/cost label with per-turn cumulative usage."""
        turn = getattr(self, '_currentTurn', 1)
        tokens = getattr(self, '_currentTurnTokens', 0)
        cost = getattr(self, '_currentTurnCost', 0.0)
        self.tokenLabel.text = f"Turn {turn} | Cumulative: {tokens} tokens | ${cost:.4f}"

    def _writeTimingReport(self):
        """Write detailed performance timing to a text file."""
        import time
        if not self._timing:
            return
        try:
            turn_number = 1
            if self.logic and hasattr(self.logic, 'llmClient') and self.logic.llmClient:
                turn_number = getattr(self.logic.llmClient, 'turn_number', 1)
                suffix = getattr(self.logic.llmClient, 'debug_suffix', "")
            else:
                suffix = ""
            # turn_number is already incremented after response, so current turn is turn_number-1
            turn_number = max(1, turn_number - 1)
            logPath = os.path.join(self._getCurrentLogDir(), f'{turn_number}_performance_log{suffix}.txt')

            t = self._timing
            lines = ["="*50, "Performance Timing Report", "="*50, ""]

            # ---- Compute phase times so the overview adds up ----
            phase1_scene = t.get('context_build_time', 0.0)

            phase2_decompose = 0.0
            phase2_faiss = 0.0
            phase2_retrieval = 0.0
            rt = t.get('retrieval_timing', {})
            if rt:
                phase2_decompose = rt.get('decompose_time', 0.0)
                phase2_faiss = sum(pq.get('time', 0.0) for pq in rt.get('retrieval_per_query', []))
                phase2_retrieval = phase2_decompose + phase2_faiss

            phase3_api = 0.0
            phase3_tool = 0.0
            phase3_other = 0.0
            phase3_tools = 0.0
            lt = t.get('llm_timing', {})
            if lt:
                phase3_api = lt.get('total_api_time', 0.0)
                phase3_tool = lt.get('total_tool_time', 0.0)
                phase3_other = lt.get('total_other_time', 0.0)
                phase3_tools = phase3_api + phase3_tool + phase3_other

            phase4_validation = 0.0
            if 'validation_start' in t and 'validation_end' in t:
                phase4_validation = t['validation_end'] - t['validation_start']
            phase4_exec = 0.0
            if 'execution_start' in t and 'execution_end' in t:
                phase4_exec = t['execution_end'] - t['execution_start']
            phase4_total = phase4_validation + phase4_exec

            # Totals
            total_to_generation = 0.0
            total_with_execution = 0.0
            if 'turn_start' in t:
                if 'generation_complete' in t:
                    total_to_generation = t['generation_complete'] - t['turn_start']
                if 'execution_end' in t:
                    total_with_execution = t['execution_end'] - t['turn_start']

            # Unmeasured overhead = remainder not captured by the explicit phases above
            measured_sum = phase1_scene + phase2_retrieval + phase3_tools + phase4_total
            unmeasured = max(0.0, total_with_execution - measured_sum)

            # ---- Timeline Overview (numbers must add up) ----
            lines.append("=== Timeline Overview ===")
            lines.append(f"Total turn wall-clock (including execution): {total_with_execution:.3f}s")
            if total_to_generation > 0:
                lines.append(f"Total up to code generation: {total_to_generation:.3f}s")
            lines.append("")
            lines.append("Phase breakdown:")
            lines.append(f"  1. Scene context build: {phase1_scene:.3f}s")
            lines.append(f"  2. Pre-retrieval (query decomposition + vector search): {phase2_retrieval:.3f}s")
            lines.append(f"  3. Autonomous tool-calling & code generation: {phase3_tools:.3f}s")
            lines.append(f"  4. Code validation & execution: {phase4_total:.3f}s")
            if unmeasured > 0.001:
                lines.append(f"  5. Unmeasured overhead (prompt formatting, UI handoff, etc.): {unmeasured:.3f}s")
            lines.append("")
            lines.append("Verification: " + " + ".join([
                f"{phase1_scene:.3f}", f"{phase2_retrieval:.3f}", f"{phase3_tools:.3f}",
                f"{phase4_total:.3f}", f"{unmeasured:.3f}"
            ]) + f" = {measured_sum + unmeasured:.3f}s")
            lines.append("")

            if 'tokens' in t:
                lines.append(f"Main generation tokens: {t['tokens']}")
            if 'cost' in t:
                lines.append(f"Main generation cost: ${t['cost']:.4f}")
            lines.append("")

            # ---- Role Trace ----
            if t.get('role_trace'):
                lines.append("-" * 40)
                lines.append("Role-Composed Agent Trace")
                lines.append("-" * 40)
                for event in t.get('role_trace', []):
                    role = event.get('role', 'Unknown')
                    name = event.get('event', 'event')
                    details = event.get('details', {})
                    detail_text = json.dumps(details, ensure_ascii=False, default=str)
                    if len(detail_text) > 240:
                        detail_text = detail_text[:240] + "... "
                    lines.append(f"{role}: {name} | {detail_text}")
                lines.append("")

            # ---- Phase 1: Scene Context (detail) ----
            if 'context_build_time' in t:
                lines.append("-" * 40)
                lines.append("Phase 1 — Scene Context Build")
                lines.append("-" * 40)
                lines.append(f"Scene context build: {t['context_build_time']:.3f}s")
                lines.append("")

            # ---- Phase 2: Pre-Retrieval (detail) ----
            if rt:
                lines.append("-" * 40)
                lines.append("Phase 2 — Dense Pre-Retrieval (Decompose + Vector Search)")
                lines.append("-" * 40)
                if 'decompose_time' in rt:
                    thinking_flag = "ON" if rt.get('decompose_thinking') else "OFF"
                    lines.append(f"Query decomposition: {rt['decompose_time']:.3f}s (thinking={thinking_flag})")
                if 'sub_queries' in rt:
                    for i, sq in enumerate(rt['sub_queries'], 1):
                        lines.append(f"  Sub-query {i}: {sq}")
                if 'retrieval_count' in rt:
                    lines.append(f"Retrieval calls: {rt['retrieval_count']}")
                if 'concatenated_count' in rt:
                    lines.append(f"Total chunks in context: {rt['concatenated_count']}")
                if 'retrieval_per_query' in rt:
                    lines.append(f"Vector search total: {phase2_faiss:.3f}s")
                    for pq in rt['retrieval_per_query']:
                        lines.append(f"  - {pq.get('query', '')}: {pq.get('count', 0)} chunks in {pq.get('time', 0):.3f}s")
                lines.append("")

            # ---- Phase 3: Tool-Calling Loop (detail) ----
            if lt:
                lines.append("-" * 40)
                lines.append("Phase 3 — Autonomous Tool-Calling Loop")
                lines.append("-" * 40)
                rounds = lt.get('rounds', [])
                grep_count = sum(1 for r in rounds if 'Grep' in r.get('tools', []))
                readfile_count = sum(1 for r in rounds if 'ReadFile' in r.get('tools', []))
                vectorsearch_count = sum(1 for r in rounds if 'VectorSearch' in r.get('tools', []))
                lines.append(f"API calls: {lt.get('api_calls', 0)}")
                lines.append(f"Tool rounds: {lt.get('tool_rounds', 0)}")
                lines.append(f"Grep calls: {grep_count}")
                lines.append(f"ReadFile calls: {readfile_count}")
                lines.append(f"VectorSearch calls: {vectorsearch_count}")
                lines.append("")
                lines.append(f"Time inside this phase:")
                lines.append(f"  LLM API wait time: {phase3_api:.3f}s")
                lines.append(f"  Tool execution time: {phase3_tool:.3f}s")
                lines.append(f"  Overhead (JSON parse, prompt rebuild, etc.): {phase3_other:.3f}s")
                lines.append("")
                if rounds:
                    lines.append("Per-round breakdown:")
                    for r in rounds:
                        tools = ', '.join(r.get('tools', [])) or 'done'
                        tok = r.get('tokens', 0)
                        tok_str = f" tokens={tok}" if tok else ""
                        thinking_flag = "ON" if r.get('thinking') else "OFF"
                        lines.append(
                            f"  Round {r['round']} | "
                            f"api={r['api_time']:.3f}s tool={r.get('tool_time', 0):.3f}s "
                            f"other={r.get('other_time', 0):.3f}s total={r['round_time']:.3f}s | "
                            f"thinking={thinking_flag} | tools=[{tools}]{tok_str}"
                        )
                    lines.append("")

            # ---- Phase 4: Execution (detail) ----
            has_exec = 'execution_start' in t or 'autoexecute_start' in t
            if has_exec:
                lines.append("-" * 40)
                lines.append("Phase 4 — Code Validation & Execution")
                lines.append("-" * 40)
                if 'validation_start' in t and 'validation_end' in t:
                    v_t = t['validation_end'] - t['validation_start']
                    lines.append(f"Syntax validation: {v_t:.3f}s")
                if 'execution_async_call' in t and 'autoexecute_start' in t:
                    async_t = t['execution_async_call'] - t['autoexecute_start']
                    lines.append(f"Pre-execution overhead: {async_t:.3f}s")
                if 'executor_scheduled' in t and 'execution_async_call' in t:
                    sched_t = t['executor_scheduled'] - t['execution_async_call']
                    lines.append(f"Executor scheduling delay: {sched_t:.3f}s")
                if 'executor_actual_start' in t and 'executor_scheduled' in t:
                    actual_delay = t['executor_actual_start'] - t['executor_scheduled']
                    lines.append(f"Qt event-loop delay (singleShot→run): {actual_delay:.3f}s")
                if 'execution_start' in t and 'executor_actual_start' in t:
                    exec_startup = t['execution_start'] - t['executor_actual_start']
                    lines.append(f"Executor startup overhead: {exec_startup:.3f}s")
                if 'execution_callback_start' in t and 'execution_end' in t:
                    cb_t = t['execution_callback_start'] - t['execution_end']
                    lines.append(f"Callback dispatch delay: {cb_t:.3f}s")
                if 'execution_start' in t:
                    if 'execution_end' in t:
                        exec_t = t['execution_end'] - t['execution_start']
                        lines.append(f"Code execution (exec() only): {exec_t:.3f}s (result: {t.get('execution_result', 'unknown')})")
                    else:
                        lines.append("Code execution: started but not finished yet")
                lines.append("")

            # ---- Self-corrections ----
            lines.append("-" * 40)
            lines.append("Self-Correction")
            lines.append("-" * 40)
            if 'corrections' in t:
                lines.append(f"Attempts: {len(t['corrections'])}")
                for corr in t['corrections']:
                    lines.append(f"  Attempt {corr['attempt']}: start={corr['start']:.3f}s")
                    if 'tokens' in corr:
                        lines.append(f"    Tokens: {corr['tokens']}")
                    if 'cost' in corr:
                        lines.append(f"    Cost: ${corr['cost']:.4f}")
                    if 'timing_report' in corr:
                        ct = corr['timing_report']
                        lines.append(f"    API calls: {ct.get('api_calls', 0)}")
                        lines.append(f"    Total API time: {ct.get('total_api_time', 0):.3f}s")
                        lines.append(f"    Total tool time: {ct.get('total_tool_time', 0):.3f}s")
                        lines.append(f"    Tool rounds: {ct.get('tool_rounds', 0)}")
                        rounds = ct.get('rounds', [])
                        if rounds:
                            lines.append(f"    Rounds: {len(rounds)}")
            else:
                lines.append("Attempts: 0")
            lines.append("")

            # ---- Token & Cost summary ----
            lines.append("-" * 40)
            lines.append("Token & Cost Summary")
            lines.append("-" * 40)
            total_tokens = t.get('tokens', 0)
            total_cost = t.get('cost', 0.0)
            if 'corrections' in t:
                for corr in t['corrections']:
                    total_tokens += corr.get('tokens', 0)
                    total_cost += corr.get('cost', 0.0)
            lines.append(f"TOTAL TOKENS (main + corrections): {total_tokens}")
            lines.append(f"TOTAL COST (main + corrections): ${total_cost:.4f}")
            lines.append("")
            lines.append("="*50)

            with open(logPath, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
        except Exception as e:
            logger.warning(f"Failed to write timing report: {e}")

    # Note: onCopyButtonClicked removed - copy functionality not needed with auto-execution
