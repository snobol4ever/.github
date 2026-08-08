# FINDING-2026-08-08-CLAUDE-SN4-RTX-EVAL-RETURN-TYPE-WAS-ALWAYS-STRING-AND-DEFER-LATCH-WAS-ONE-SLOT.md

## Session s_this (2026-08-08, Claude Sonnet 4.6) — SCRIP commit c2e78f6d

### EVAL-RETURN-FIX

**Symptom:** EVAL('LEN(1)') returns STRING, not PATTERN. EVAL('3 + 4') returns
STRING, not INTEGER. All EVAL string expressions return wrong type.

**Root cause (CLASS C chain exit bypasses NV_GET_fn):**
CLASS C chains (EVAL/CODE JIT fragments) exit via bb_glue_outer_γ:
  mov rsp, rbp   ; restore to eval_chain_run_capture frame base
  pop rbp         ; restore caller rbp
  mov eax, DT_S  ; chain "return value"
  ret             ; lands in eval_string_transient PAST call eval_chain_run_capture

The ret skips eval_chain_run_capture's NV_GET_fn(EVAL_TMP) read entirely.
The chain CORRECTLY assigns ZZEVALZZ the right type (PATTERN, INTEGER, etc.)
but eval_string_transient never reads it because the call's "return" is the
chain's ret, landing past the call instruction.
eax=DT_S=2 became result.v — always STRING.

**Discovery:** Added fprintf before/after rt_chain_enter in eval_chain_run_capture.
[CAP-PRE] printed, [CAP-POST] never printed. Hex dump of chain entry showed
sub rsp,16 (per-BB ZD carve) not sub rsp,48 (flat_frame_bytes). Traced through
objdump to confirm ret at chain exit lands at cf0 in eval_string_transient,
not inside eval_chain_run_capture.

**Fix:** Renamed eval_chain_run_capture → eval_chain_enter_only (void return).
Moved NV_GET_fn/NV_SET_fn save-read-restore into eval_string_transient directly
after the call, which the chain's ret correctly returns to.

**Scope note:** rt_chain_enter calls at runtime_eval.c:303/308/312/379/412
(EXPVAL_fn, code()) use the same CLASS C mechanism — auditing them is a next rung.

### DEFER-LATCH-FIX

**Symptom:** Deferred function calls in patterns built in sequence clobbered each other.

**Root cause:** g_star_peek was a single {nm, val, valid} slot. Pattern
"outer('c1') outer('c2')" pushed two entries; second overwrote first. At match time
c_rt_defer_open("*inner(c1)") found no match, fell through to
rt_proc_call_open("inner(c1)",0) — a proc named literally "inner(c1)" — crash.

**Fix:** Replaced g_star_peek with g_spk[] 256-entry FIFO stack using rt_cas_carve
(same pattern as g_dfx). FIFO-pop by name restores left-to-right ordering.

**Gate programs 140/141 remain red:** Separate pre-existing defect —
*func_call() in pattern context passes "inner(c1)" as proc name, not "inner" with
arg "c1". Confirmed crashes at HEAD before this commit. Own rung, Lon routing.

### WATERMARK
HEAD c2e78f6d, N=1, setarch -R:
m3 291/26/0 · m4 274/42/1 SKIP · DIVERGE 18
vs s241 baseline 289/28/0 · 272/44/1 · DIVERGE 18.
Net +2 m3, +2 m4. Zero regression.
