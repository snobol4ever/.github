# HANDOFF 2026-06-03 (Opus 4.8) — SNOBOL4-BB SR-1a: de-fuse `rt_call_named_proc` into thin save/restore helpers

## Summary

Landed **SR-1a**, the first clause of the SR-1 de-fuse ladder: `rt_call_named_proc` no longer inlines its
save/install/restore loops. They are now two thin extern runtime helpers. Pure, byte-faithful refactor — the loop
bodies are verbatim and the NV operations happen in the same order, so program output is unchanged. All HARD gates
hold. SR-1b (the box-bracketing remainder) is now fully de-risked and mechanically specified in the goal file but
NOT started — it needs a fresh budget to implement + gate green in one go (see "Why SR-1b was not started").

## What changed (diff = `src/runtime/rt/rt.c` only, +23/-15)

Two new extern helpers, defined immediately above `rt_call_named_proc`:

```c
int  rt_name_save_push(const char **names, DESCR_t *args, int nargs, int n);
     /* save old DESCRs of names[0..n), install args[k] for k<nargs else NUL; returns the LIFO base */
void rt_name_restore(int base);
     /* restore LIFO from g_name_save_top-1 down to base; set g_name_save_top = base */
```

`rt_call_named_proc` now:
- `save_base = rt_name_save_push(pn, args, nargs, np)` — params (was the inlined param loop, lines 492-499).
- `rt_name_save_push(&name, (DESCR_t*)0, 0, 1)` — fn-name save + null (was lines 500-503; n=1/nargs=0 ⇒ installs NUL).
- frame-nest setup, `p->fn(fb,0)`, `result = IS_FAIL(fret) ? FAIL : NV_GET(name)` — unchanged.
- `rt_name_restore(save_base)` — restore (was the inlined restore loop, lines 509-511).

Equivalence is exact: same names pushed in the same order, same actuals/NUL installed, same capture-before-restore,
same restore span down to the pre-param base.

## Gate state (clean rebuild of `scrip` + `libscrip_rt`)

- SNOBOL4 m2 **7/7 HARD** · m3 **6/6** (`DOUBLE(21)`→`42`) · m4 0/6
- Icon m2 **12/12 HARD** · m3 4/12 · m4 4/12 (NOT regressed)
- `prove_lower2` PASS · `no_bb_bin_t` 0 · LI-FENCE OK · concurrency invariants OK
- ENV: `apt-get install -y libgc-dev`

## Mechanism notes gathered this session (carry-forward for SR-1b)

- The mode-3 SNOBOL userproc path is **rt.c's `rt_call_named_proc`** (confirmed by the prior session's probe trace).
  `src/runtime/core/name_save.c` is a SEPARATE mechanism — do not confuse them.
- Proc body build: `scrip.c` SNOBOL `--run` block registers each non-main proc (`rt_proc_register` +
  `gvar_flat_chain_build` + `rt_proc_set_fn`); `rt_call_named_proc` wraps `p->fn(fb,0)`.
- Inside the body **`r12 = fb`** — `XA_FLAT_PROLOGUE` (`xa_flat.cpp`, `g_frame_active`) is `push r12; mov r12, rdi`.
- Body exits: RETURN → `lbl_γ` → success epilogue returns `eax=1, edx=0`; FRETURN → `lbl_ω` → fail epilogue
  returns `eax=99` AND writes `[r12+0]=99`. **The function result is NOT in the return regs** — `rt_call_named_proc`
  reads it from the NV store via `NV_GET(name)` after the body returns, before restoring.
- Frame allocator is a trivial bump: `g_flat_slot_count` (`emit_bb.c:61`), `bb_slot_alloc16` += 16. The gvar body
  path (`emit_bb.c:2096`) starts it at 0; offset 0 already doubles as the result slot.

## SR-1b — ready to execute (epilogue-neutral; full spec in GOAL-SNOBOL4-BB.md)

Make `SAVE → body → RESTORE` explicit WITHOUT touching the shared `XA_FLAT_EPILOGUE` (Icon shares it). Key
constraint: result is read via `NV_GET(name)` and must be captured BEFORE restore; restore must run on BOTH
`lbl_γ` (RETURN) and `lbl_ω` (FRETURN). Design: `bb_proc_save` at body head (reads actuals `[r12+16*(k+1)]` +
baked RO param names, calls `rt_name_save_push`, stores base in a reserved frame slot); RESTORE-success box at
`lbl_γ` before the epilogue (`g_proc_result = NV_GET(name); rt_name_restore(base)`); RESTORE-fail box at `lbl_ω`
(`rt_name_restore(base)`). `rt_call_named_proc` stages actuals into `fb+16*(k+1)` (np-normalized, NUL-fill, like
the `g_call_args` path at `rt.c:466`), invokes the body, reads result from the new `g_proc_result` global.
SR-1b does NOT need body bytes byte-identical (boxes are ADDED) — gate is m3 6/6 OUTPUT + Icon bytes unchanged.
Layout: result `[0]`, actuals `[16..16+16*np)`, base `[16+16*np]`, body temps from `16+16*np+8`. Remaining work
is purely mechanical: 2-3 box templates (TEXT+BINARY arms), `emit_core.c` dispatch, the `codegen_gvar_flat_chain_body`
insertion, the `rt_call_named_proc` rewrite, then gating.

## Why SR-1b was not started

SR-1b is all-or-nothing for a green commit (new BINARY box-template encodings rarely land first-try; expect
2-3 build+gate+debug iterations, each consuming meaningful budget). Session context was ~65% when the decision
point arrived; starting then risked ending mid-debug in a half-applied or broken state, which the "no broken
commits" rule forbids. Stopped at a clean green boundary instead. SR-2 (save-area = ζ-frame) is unchanged, after SR-1b.

## Still open (does NOT block anything above)

**String-arg `slen`.** `marshal_call_arg` IR_LIT_S arms (`bb_call.cpp`) leave `slen`=0; a string param reads
zero-length (`G('AB')` → empty). Fix both arms: pack `tag | ((uint64_t)strlen(sval) << 32)`. Shared with the Raku
`rt_call_arr` path — keep byte-neutral to Raku.

## Build / verify recipe

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh && make libscrip_rt          # emit path lives in BOTH
bash scripts/test_smoke_snobol4.sh                        # m2 7/7 HARD; m3 6/6
bash scripts/test_smoke_icon.sh                           # m2 12/12 HARD (regression check)
bash scripts/prove_lower2.sh ; bash scripts/test_gate_no_bb_bin_t.sh
bash scripts/test_gate_no_lang_names.sh ; bash scripts/audit_concurrency_invariants.sh
```

## Watermark

SCRIP tip = `b05170c` (SR-1a helper de-fuse; SNOBOL4 m3 6/6). .github tip = this commit. Goal single-source-of-truth
updated in `GOAL-SNOBOL4-BB.md` (SR-1a `[x]`, SR-1b spec + allocator/layout, watermark). Detail: this file.
