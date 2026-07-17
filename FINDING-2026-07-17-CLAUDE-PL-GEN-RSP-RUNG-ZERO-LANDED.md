# FINDING 2026-07-17 (s60, Claude Sonnet 4.6) — PL-GEN-RSP RUNG-ZERO: generator proc boxes adopt heap fb as rbp frame base; 88→138/138 ×3

SCRIP HEAD at landing: `0a45bb6f` (pushed). Baseline before: 88/138 ×3.

## One-line

The s65 RSP conversion applied the outer-graph self-allocating prologue to generator proc boxes, discarding the heap fb that rt_proc_call_gen_h binds args into. Generator boxes must now adopt the passed fb as their rbp frame base instead.

## Root cause (mechanism, not symptom)

rt_proc_call_gen_h (rt/rt.c ~616) allocates `base = rt_zls_alloc(total)`, sets `fb = base+16`, pre-zeroes the frame, binds args at `[fb+16*i]`, then calls `p->fn((void*)fb, 0)` — passing fb in rdi. Both α (entry=0) and β-resume (entry=1, via rt_proc_resume_frame → fn(fb,1)) pass the same heap fb in rdi.

The s65 RSP conversion (xa_flat.cpp g_frame_active arm) emits:
```
  sub rsp, 65544        ; self-allocates a THROWAWAY rsp frame
  mov rdi, rsp          ; overwrites the passed fb
  ...rep stosb...       ; zeroes the throwaway frame
```
Box locals address `[rbp+off]` (FR/FRQ under RSP, REG-7 U3 — already landed), where rbp was seeded to rsp. So all box locals live in the throwaway rsp frame; the heap fb with the bound args is abandoned. q(hello) → q(X), write(X) → empty (X stays unbound in caller's cell; under backtrack the stale stack region → jump-to-0 segfault).

The pre-s65 non-RSP arm did it correctly: `mov zr, rdi` (adopt the passed frame register). s65 applied the outer-graph regime to gen procs when it should not have.

## Fix (xa_flat.cpp, 4 edits, +27 lines, one file)

In both BINARY and TEXT RSP g_frame_active arms, guard on `g_gen_proc_active || g_resumable_callable_active`:

**Prologue (both media):** instead of sub rsp + rep stosb, emit:
```
  push rbp              ; save caller rbp (SysV callee-saved)
  mov rbp, rdi          ; adopt the heap fb as the frame base
  cmp esi, 0            ; α vs β dispatch
  jne <β>
```
The heap fb is already pre-zeroed and args are already bound at [rbp+16]+. rsp stays free; both α and β re-enter through this prefix and both see the same persistent frame.

**Epilogue (both media):** instead of anchor-leave + add rsp + ret, emit:
- Success: `pop rbp; ret` (IR_RETURN already wrote the result DESCR to [rbp+0])
- Fail: write FAILDESCR to [rbp+0]+[rbp+4]+[rbp+8], then `pop rbp; ret`

rt_proc_call_gen_h reads the result from `*(DESCR_t*)(fb+0)` after the call returns — which is now [rbp+0] = correct. rt_proc_resume_frame does the same. The heap fb outlives the C call frame (rt_zls_alloc; freed only on final failure), so β-resume is safe.

Outer-graph path (main graph, non-gen case): **byte-identical, untouched**.

## Stale-doc corrections found during investigation

Two GOAL-file claims were false at landing time:
1. **REG-7 U3 was already landed** — the GOAL file described it as "unchecked". In the actual code, `x86_fr32_prefix()`/`x86_fr64_prefix()` already return `"[rbp + "` under RSP (op_flat_disp compensation deleted). The fix works because U3 had landed.
2. **The s58d cursor's "138/138 ×3" was stale prose** — measured fresh baseline was 88/138 ×3. STALE-ORIENTATION rule applies.

## Gates at landing

- Prolog rung suite: **138/138 ×3** (interp/run/compile) — was 88
- Prolog crosscheck: PASS=150 FAIL=0 SKIP=13 ORACLE_MISS=0
- no-new-global gate: PASS, floor 14
- SNOBOL4 smoke: 7/7
- Icon smoke: 14/14 ×2
- Raku smoke: 283/283 ×2
- SCRIP build: clean (one file, +27 insertions)

## Next rung

PL-ISO-11: `term_variables/2` + `subsumes_term/2`. Both ISO core, both MISSING. Semantics read from gprolog refs/gprolog-master/src/BipsPl/term_inl_c.c (Pl_Term_Variables_3, Pl_Subsumes_Term_2). Det builtins → rt_pl_det_builtin_target tab. Completion: rung51_terminspect ×5 ×3 == gprolog.
