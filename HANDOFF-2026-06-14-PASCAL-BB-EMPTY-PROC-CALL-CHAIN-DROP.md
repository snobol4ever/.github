# HANDOFF-2026-06-14-PASCAL-BB-EMPTY-PROC-CALL-CHAIN-DROP.md

## Session summary
Goal: GOAL-PASCAL-BB.md. Lon's directive: "your choice — continue." Closed the
Session-58 live pcom blocker (open item #1): the **empty-procedure-call chain-drop
bug** in Pascal M3/M4. SCRIP `emit_bb.c` ONE-line change; zero
template/lower/interp/machine/contracts files touched. Then re-drove pcom and
characterized the next frontier.

## Gate state
- Entering: M2 121/0 · M3 121/0 · M4 121/0  XFAIL=1
- Leaving:  M2 122/0 · M3 122/0 · M4 122/0  XFAIL=1  (+1 probe `emptyproc.pas`)
- Cross-language smoke after the shared `emit_bb.c` change: SNOBOL4 7/0 ×3
  (incl. empty-DEFINE canary, same driver), Icon 12/0 ×3, Prolog 5/0 ×3,
  Raku 37/0 m2 (EXCISED=2 pre-existing). All clean.
- Survived an upstream rebase (SCRIP 4486f88..1ec4b09): rebuilt + re-gated 122/0 ×3.

## Commits (all on origin/main)
- SCRIP   `3039f79` — the fix
- corpus  `8d19b3de` — regression probe `emptyproc.pas` (+ `.ref`)
- .github `e5433a68` — GOAL-PASCAL-BB Session 59 watermark

## What landed (the bug, root cause, fix)
**Symptom:** a `procedure p; begin end;` call in M3/M4 silently dropped every
statement after the call. Repro: `program t(output); var x:integer;
procedure noop; begin end; begin x:=1; noop; x:=x+1; writeln(x) end.` printed `2`
in M2 but NOTHING in M3.

**Root cause:** `codegen_gvar_flat_chain_body` (emit_bb.c ~3630, the gvar flat-chain
proc-body driver that Pascal AND SNOBOL4 run on) defines `<proc>_α_body:` then emits
the statement chain. For an EMPTY body all nodes are `IR_SUCCEED`/`IR_FAIL` →
`gvar_chain_is_real` rejects them → `n==0` → NOTHING is emitted between `α_body:`
and `β:`. So `α_body` FELL THROUGH into `β: jmp ω` — the GZ-10 PROC FAIL EXIT, which
writes FAILDESCR (eax=99) to frame[0] and returns. `rt_call_named_proc` (rt.c ~547)
then saw `IS_FAIL_fn(fret)` true → returned FAILDESCR → the CALLER's
`cmp eax,99; je ω` took ω → the caller's WHOLE statement sequence FAILED → drop.

**Fix (one line, emit_bb.c ~3688):**
```c
    }                                            // end of node-emission loop
    if (n == 0) emit_jmp_label(&lbl_γ, JMP_JMP); // NEW: empty body -> success
    emit_label_define_bb(&lbl_β);
```
An empty body now jumps to SUCCESS (γ) instead of falling into FAIL (β/ω). No-op for
any non-empty body (`n>0`). Semantically a `begin end` block always succeeds, so a
Pascal/SNOBOL4 empty proc must return success. The emitted `empty_α_body:` now reads
`jmp empty_γ` (→ eax=1, success) instead of falling into `empty_β: jmp empty_ω`.

**Discipline:** the change is in the chain-WIRING driver (`codegen_gvar_flat_chain_body`),
NOT a `bb_*.cpp` template. `emit_jmp_label` is the sanctioned medium-complete jump
emitter used throughout that same function (it already emits `jmp ω` two lines down).
Zero raw bytes, zero `MEDIUM_*`, zero language names. Per RULES, TEMPLATE-ONLY
EMISSION governs `bb_*.cpp`; emit_bb.c is the dispatch/driver layer.

## CRITICAL nuance — do NOT apply this fix to the sibling descr driver
`codegen_flat_chain_body` (emit_bb.c ~3164, the DESCR-chain driver used by
Icon/Prolog/Raku/pattern bodies + `proc_flat`) has the IDENTICAL `n==0`
fall-through-into-β structure. **It must NOT get the same fix.** Reason: a Pascal
procedure *completes/succeeds*, but an Icon procedure that falls off the end *fails*
(`&fail`). Empirically, an empty Icon proc emits the same `proc_noop_α_body:` →
`proc_noop_β: jmp proc_noop_ω` (FAILDESCR), and that is CORRECT Icon semantics —
in statement context the caller tolerates the failure and continues (`before`/`after`
both print in M2 AND M3). Changing the descr driver to jump-to-γ would make empty
Icon procs wrongly succeed. The two drivers look identical but require OPPOSITE
empty-body behavior.

## Findings handed to Lon (NOT acted on — out of scope / different goal)
1. **pcom's deeper M3 listing-output divergence — the NEW live pcom frontier.**
   With empty-proc fixed, M2 now emits pcom's full source listing on a tiny program
   (`program t(output); begin end.` → 3-line listing), but M3 emits NOTHING (rc=0,
   no abort; M4 compiles 234K-line asm clean). pcom's first output is the
   source-listing `write` (in `endofline`/main read loop); that `write` isn't reaching
   stdout in M3. All 122 gated probes pass M3, so it's a pcom-SCALE construct, not a
   primitive. pcom is NOT gated; needs a fresh context budget. Repro:
   `scrip --run pcom.pas < tiny.pas` vs `--interp`.
2. **Pre-existing latent Icon empty-proc bug (a GOAL-ICON-BB matter).** In a
   CONDITIONAL context `if noop() then write("succeeded") else write("failed")`:
   M2 prints "succeeded", M3 prints NOTHING (drops the whole conditional), and per
   strict Icon semantics BOTH are arguably wrong (fall-off-end = `&fail` → should be
   "failed"). This is on the descr driver and is independent of this session's
   gvar-driver change (Icon smoke stayed 12/0). Belongs to the Icon goal, gated
   separately.

## Landmines reconfirmed
- After ANY runtime (`by_name_dispatch.c`/`rt/`) edit, `make libscrip_rt` — M4 links
  the external `.so`. (This session touched no runtime, but rebuilt the `.so` anyway.)
- `.ref` files follow SCRIP width-10 integer convention; `emptyproc.ref` was generated
  from M2 (value-cross-checked = 3), not fpc.
- Every `git pull --rebase` → `rm -f scrip && make` → full gate re-run (did this; 122/0).

## What to read next session
- GOAL-PASCAL-BB.md (live state). Frontier #1 above (pcom M3 listing output) is the
  next Pascal step; deserves a fresh context budget.
- For the Icon finding, GOAL-ICON-BB.md owns it.

## Watermark
Session 59 (2026-06-14). Pascal gates 121→122 (+1 probe). Empty-procedure-call
chain-drop closed in M3/M4 (one-line gvar-driver fix). Sibling descr driver
deliberately left unchanged (Icon needs opposite empty-body semantics).
