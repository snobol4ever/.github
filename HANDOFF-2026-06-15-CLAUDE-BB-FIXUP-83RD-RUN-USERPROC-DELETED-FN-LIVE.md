# HANDOFF — 83rd run (Claude) — IR_CALL split: USERPROC dead-code DELETED; FN-is-LIVE correction; BYNAME 2-path characterized

**Goal:** GOAL-BB-FIXUP-A-to-Z.md (FIX-3-iii, the IR_CALL ONE-IR-ONE-LOGIC split). Full detail in that goal's 83rd-run watermark; this is the pointer.

**Cursor:** `bb_call.cpp` (stays — FIX-3 not closed; no LADDER rung closed this run).

**Heads:** SCRIP @ `9250b37` · .github @ this commit. Both clean, local==origin, merged trees rebuilt+regated GREEN.

## The disposition Lon asked for — resolved by MEASUREMENT, not by trusting the 82nd handoff
The 82nd run left a BLOCK: "USERPROC/FN no-chain routes unexercised — dead-delete vs synth-probe, Lon disposition." Lon said "delete dead code" (option A). Before deleting, I instrumented the routes and swept — and the handoff's central claim was **wrong**.

### Landed (SCRIP `9250b37`, rebased clean over doc-only `e91abc0`)
- **`CALL_ROUTE_USERPROC` (route 2611) DELETED** — proven dead: 0 hits across 162 `test/` (m3+m4) + 1488 corpus snobol4/icon (m4) + **9 hand-built firing-probe shapes** (SNOBOL predicate `myp('abc'):f()s()` / RHS `OUTPUT=myp(5)` / binop-operand `Z=myp(7)+1` / concat / SIZE-arg; Icon procedure predicate / operand / write-arg / every-generator) in BOTH modes — the exact shapes that fire FN for builtins. Structural cause: registered user-proc calls are ALWAYS flat-staged (descr→PROC_STAGED / gvar→GVAR_USERPROC); only builtins reach the non-flat `walk_bb_node` operand fallthrough.
- Deletion set: emit_bb.c classifier USERPROC return; bb_call.cpp dispatch case + extern decl; emit_globals.h enum value (FN renumbered 12→11, contiguous, end-of-enum so no other renumber); `bb_call_userproc.cpp` (no other callers, git-grep verified); Makefile ×2; `test_gate_bb_one_box.sh` ICN_HELPER_FILES manifest + comment.
- **Behavior-neutral:** A/B m4 `.s` **RAW byte-identical 6/6** (no normalization needed) on FN probes (913/094/1113/test_math) + user-proc staged+gvar (p1) + 083. Gates at floors pre+post.

## ⛔ CORRECTION to the 82nd handoff (do NOT repeat)
The 82nd handoff lumped USERPROC+FN as the "no-chain family" and guessed `CALL_ROUTE_FN` was "almost certainly the same" (dead), with a "BUILTIN producer gated on the USERPROC/FN disposition." **FALSE.** `CALL_ROUTE_FN` is **LIVE** — fires 20× in `test/` alone (`integer`/`min`/`max`/`table`/`real`/`abs`, dv=2, m3 AND m4: 913_integer_pred, 094_data_define_access, 1113_table, test_math). FN is load-bearing for builtin calls on the non-flat path. Deleting it would have been the documented confident-wrongness-on-unexercised-paths anti-pattern.

## ⛔ BYNAME characterized (2nd half of run) — handoff was wrong on 3 counts
The handoff called BYNAME "route 2655, gvar !registered dv3, lowest-risk clean mechanical rung." Measured reality (probe per BYNAME-returning line, swept all langs): BYNAME is returned from **three** conditions across **two** emission paths → it is a **2-PATH rung**:
- **cond-2608** `g_gvar_flat_chain && dv==2 && !registered && !builtin` = **588 LIVE** (SNOBOL by-name: differ/ne/GT/SIZE/REPLACE/define — not in `rt_builtin_is_known`).
- **cond-2602** `g_descr_flat_chain && dv==2 && builtin` = **39 LIVE** (test/prolog or test/raku descr-chain builtins).
- **cond-2607** `g_gvar_flat_chain && dv==3 && !registered` = **0** across 1650 SNOBOL/Icon + 1020 prolog/raku/pascal = **candidate-dead** (the handoff called THIS the live primary BYNAME — the exact inversion). Resolve with USERPROC-grade rigor (targeted probe + structural argument) before producing OR deleting.

## ⛔ NEW design insight / proof obligation (applies to all producer rungs)
An **inert** producer's byte-identity does **NOT** verify the stamp is correct: emission still route-classifies and IGNORES the stamp, so gates stay green even if the stamp set is wrong; the stamp is load-bearing only at cleanup. A producer rung MUST additionally prove **stamp-set == classify-route-set** (e.g. a temporary assert: every stamped node classifies to that route and vice-versa), not merely byte-identity + green gates. Retroactively applicable to PROC_STAGED / GVAR_USERPROC — verify their stamp completeness at cleanup.

## Inherited red carried (NOT mine, NOT a fixup target)
mode-2 `--run` is **globally red** (prolog smoke m2 0/5 labeled HARD GATE; pat M2 0/19) while every mode-3/mode-4 gate is GREEN. Lineage: `b7a2717` (AST-walk evaluators → loud bombs, "Lon: nothing interprets tree_t at runtime") + `476af37` (kill AST-walk exec_code). Intentional, Lon-directed demolition landed by the concurrent EVAL DT_E / SNOBOL4-BB DT_C goals; consistent with prove_lower already DEAD/VACUOUS. mode-3/mode-4 (the media this goal's emission changes touch) fully green.

## Next session (de-risked, in the watermark)
1. **BYNAME producer** — 2-path inert rung (82nd-run model): extend `resolve_call_kinds_descr` to stamp IR_CALL_BYNAME on (op==IR_CALL && dv==2 && builtin) [2602]; extend `resolve_call_kinds_gvar` on (!registered && (dv==3 || (dv==2 && !builtin))) [2607+2608, disjoint from the registered-only GVAR_USERPROC stamp]. Land in halves if needed (gvar-half 588 probes first). Apply the stamp-set==classify-set proof.
2. **2607 disposition** — dead-vs-live with USERPROC-grade rigor.
3. **BUILTIN producer** (FN, route 11, PROVEN LIVE, abundant probes) — non-flat-path analog.
4. **Cleanup rung** — dispatch + consumer dval-reads → kind-reads; DELETE `bb_call_route_classify` + the `bb_call.cpp:556` switch; verify every producer's stamp completeness here.

## Gates at floors (pre+post the deletion)
sno m3/m4 7/7 HARD · pat M4 19/0 · icon m3/m4 12/12 HARD · prolog m3/m4 5/5 (m2 0/5 inherited, unchanged) · purity 1 · bin_t 0 · medium_inv 0 · handenc 0 · vstack 3 · sno_pat_reg HARD · prove VACUOUS rc=0 · emit_blind 0. Rank 780→779 (−1 = bb_call.cpp losing one counted line; the deleted file was CLEAN so its removal is GRAND-neutral); FILES 126→125; no file grew. `bb_one_box` FAILs PRE-EXISTING (stash-confirmed at baseline — stale post-STRIP-WRAPPER; not in floor battery).

## Env / process
Corpus at /home/claude/corpus (clone snobol4ever/corpus). `make clean` after enum/IR.h edits. add/commit → `pull --rebase` → push; rebuild+regate every merged tree. SCRIP `9250b37` is a usable byte-identical baseline for the next producer rung.
