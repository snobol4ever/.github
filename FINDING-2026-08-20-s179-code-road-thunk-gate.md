# FINDING s179 (HQ, Fable 5, 2026-08-20) — THE CODE ROAD'S FRAGMENT-THUNK GATE TESTED THE WRONG COUNTER

**One sentence:** a `*F()` (function-road) defer inside a `CODE()`-compiled statement mints an `EXPR$N` proc but no new `PAT$` pattern, and `code()`'s thunk-emission guard (`runtime_eval.c:507`) gated **both** `sno_pat_thunks_build` **and** `eval_thunks_emit_from` on `sno_pat_count() > pat0` — so the fragment proc was never emitted/registered, `rt_call_proc_descr` answered `[GZ-10] 'EXPR$N' has no stackless slab`, and the in-code match silently reported nomatch (oracle: match).

## How it was found
PT-COMBO grid extension (this session): classes 6/7/8 filled to full `ptc<class><f|b>_<var|fn><2|3>` parity + new class 9 (beauty-conjunction tier), 26 new oracle-refed witnesses (corpus push `PT-COMBO class 6-9 fills`), run by the new `SCRIP/scripts/board_passthru_combo.sh`. Board at SCRIP `e66dff18` (pristine -O2): m3 100/104, m4 97/104. THREE fresh reds, one shape, both modes: `ptc7b_fn2` · `ptc7b_fn3` · `ptc7f_fn3` — all have `*F()`/`*F2()` inside the CODE text. The controls that pass isolate the ingredient: `ptc7*_var*` (var road `*P` in-code) PASS; `ptc7f_fn2` (fn builds the code STRING at build time, no in-code defer) PASSES.

## Minimal witness + the seeded twin (corpus `probe/passthru/`)
- `ptw_min_code_fn.sno` — DEFINE F; `CODE(" 'abcdef' POS(0) *F() 'ef' RPOS(0) ...")`; oracle `before|match|back`; scrip m3 `before|[GZ-10] EXPR$0 has no stackless slab|nomatch|back`.
- `ptw_min_code_fn_seeded.sno` — same, but main program ALSO runs `*F()` before the CODE: the failure moves to `EXPR$1` — proof the runtime compile CONTINUES the fragment counter (shared in-process lowerer state) yet skips the emit+register walk for the proc it minted.

## The mechanism (one asymmetry between two roads in one file)
- EVAL road (`runtime_eval.c:306,317`): `if (sno_pat_count() > pat0) sno_pat_thunks_build(pat0);` then `eval_thunks_emit_from(pc0)` **UNCONDITIONALLY** — correct: the walk is index-driven over `[pc0, g_stage2.proc_count)`, zero-iteration when nothing was minted.
- CODE road (`runtime_eval.c:507`, the s144 BLOCKER-C patch): both calls inside `if (sno_pat_count() > pat0)` — the guard encodes "new PATTERNS were minted", but the s144 defect it patched was pattern-shaped, so the EXPR$-only case (fn-road defer, no stored pattern) was invisible to it. A gate assembled from the defect already seen is one shape behind the code — the s170 medium-ratchet lesson, in the runtime.

## The cure (landed this session, `runtime_eval.c`)
Mirror the EVAL road: `thunks_build` stays conditional; `eval_thunks_emit_from(proc0)` unconditional. `SCRIP_CODE_THUNKS=0` restores the old gate exactly (killswitch-inversion). Runtime-`.so`-only: ZERO mode-4 `.s` movers by construction (the CODE road runs at runtime in both modes; nothing in `--compile` output changes).

## Receipts (post-rebuild — appended after the s179 scorecard run releases the tree)
- ptw_min_code_fn + seeded + ptc7{f,b}_fn* → expected green BOTH modes; board_passthru_combo m3 target 104/104 mod the standing `pt1_retreat_3layer_bare` (DT_P class, named in the s178-f cursor).
- Corpus fail-set A/B (killswitch two arms) + zero-mover check.

## Not this class (named, parked)
m4-only reds `ptx_shift_alt_arms{,_2layer}` + `ptx_shift_chain_3layer` (FAIL-diff rc=0, m3 green) — first seen at the new -O2 default watermark; suspected sibling of the `161_pat_defer_fn_nested_match` -O2-exposed class (s178-e named red). Owed its own witness minimization; not touched by this cure.
