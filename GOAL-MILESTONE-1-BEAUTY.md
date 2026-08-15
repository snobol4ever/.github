# ⛔⭐⭐⭐ GOAL-MILESTONE-1-BEAUTY — RE-EARN MILESTONE 1 ON THE NATIVE ENGINE: beauty.sno SELF-HOST, BOTH MODES, BYTE-IDENTICAL TO sbl

**Opened 2026-08-15 s91 by Lon in-chat (PIVOT, Fable seat): "today is the day ... surpassing Sonnet and reaching MILESTONE 1, the BEAUTY self host demo test. Take a full accounting of the status of EVERY SINGLE test suite ... We'll want a scorecard moving forward, and we need a META SCORE."**

## THE INSTRUMENT (landed this session): `SCRIP/scripts/scorecard_snobol4.sh`
```
bash scripts/scorecard_snobol4.sh run  [--suites a,b] [--jobs N] [--out DIR]   # ~1 h on 1 core for all 13 suites; run detached
bash scripts/scorecard_snobol4.sh report [DIR]                                 # any time, works on a partial results.tsv
```
Every SNOBOL4 `.sno` in corpus/ (1229) + SCRIP/test (167) is a member of exactly ONE of 13 suites. Every program runs in BOTH modes
(m3 `--run`, m4 `--compile`→`gcc -no-pie`→run) and is PASS iff its stdout equals the pinned sibling `.ref` OR the live x64 sbl output
(same stdin, same cwd; `.input`/`.in` siblings + the demo family map claws5/treebank/json/calculator/porter). Failure classes per mode:
DIFF · TIMEOUT · SIG<n> · RC<n> · COMPILE_FAIL · ASM_FAIL(=link) · ORACLE_FAIL(unscoreable, excluded from denominator).
SUITE SCORE = mean(m3 pass %, m4 pass %). **META SCORE = weight-averaged suite score.** Weights (COMPLEXITY, Lon's tuning knob — one table
in the script): beauty_self 20 · beauty_suite 15 · demos 15 · benchmarks 10 · bb_probes 10 · patterns 10 · crosscheck 10 ·
feature_test 5 · probes_misc 5 · csnobol4_suite 5 · gimpel 5 · lon 5 · misc 3 (=118). Results dirs: `SCRIP/test-results/scorecard-*/results.tsv`.
⛔ CONTAINER LAW (re-confirmed s91): the container restarted mid-sweep (uptime reset, /tmp partly kept, all processes killed) — a
detached sweep must write incrementally (it does) and be resumed with `--suites` into a `-part2` dir; report on the concatenation.

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-15 s91 (Claude Fable 5) — **BASELINE SCORECARD TAKEN AT SCRIP `ffb8fe57`; MILESTONE 1 IS 0/2 MODES; ONE CROSS-MODE ROOT CAUSE NAMED FOR THE WHOLE BEAUTY FAMILY; THE s62-OWED m3 UNIFICATION IS BUILT ON A BRANCH AND STOPS ONE CROSSING SHORT.**

⭐⭐⭐ (1) **BASELINE (see SCORECARD table in the handoff message / `test-results/scorecard-20260815-115505{,-part2}`):** beauty_self 0/1 both modes ·
beauty_suite 0/17 both · demos 5/23 both · benchmarks m3 12 / m4 15 of 23 · bb_probes 156/163 of 188 · patterns 55/55 of 122 (partial when read) ·
crosscheck 159 PASS/PASS of 196 (m3 COMPILE_FAIL 23, m4 SIG11 10) · META ≈ 30 (partial, all heavy suites in). The m3 COMPILE_FAIL class across
beauty_suite (16/17), demos, feature_test IS s90's "RETURN/FRETURN/NRETURN gap" — `bb_emit_end: N unresolved forward reference(s)` — i.e. the
s62-owed **m3 unification** rung. It is THE m3 blocker of Milestone 1, not an RBP-EARN side issue.

⭐⭐⭐ (2) **MILESTONE 1 MEASURED (oracle: `cd demo/beauty; sbl -bf beauty.sno < beauty.sno` → 622 lines, rc 0):** m3 aborts at emission —
`FLAT_BUF_MAX exceeded` (main chain > 1MB; m3 additionally re-emitted a suffix slice of the whole program per LBL__ pseudo-proc) + unresolved refs;
m4 emits 168k asm lines (`.text` 935KB) and FAILS TO LINK: `undefined reference n7498_match_assign_cond_α` (and siblings) referenced from a
`match_alternate` — a walker/lowering reachability gap: the assign_cond node is REFERENCED (3 sites each) but its α is NEVER EMITTED.
⭐ **THE SAME LABEL CLASS SURFACES IN m3 ONCE THE RETURN CLASS IS REMOVED** (Gen_driver on the unify branch: `n2190_match_assign_cond_α`,
`n2222_...` unresolved) ⇒ **ONE cross-mode root cause for the beauty family: capture (`.`/`$` conditional assignment) reached only through an
alternation arm inside a stored/named pattern is never walked into the emitted chain.** Repro candidates: any beauty_suite driver; minimal witness
NOT yet minted (next seat: bisect Gen.inc's patterns; the referencing box is `nNNNN_match_alternate_s5`).

⭐⭐ (3) **m3 UNIFICATION — BUILT, VERIFIED HALF-WAY, NOT MERGED. Branch `s91-m3-unify` (worktree `/home/claude/SCRIP-wip`, commit below):**
(a) `FLAT_BUF_MAX` 1MB→4MB, `BB_POOL_SIZE` 16→64MB (reserve only); (b) floater singletons `g_flt_lbl[]` now reset with the label pool (they DANGLED
across chains: `emit_label_pool_reset` frees the pool at every `bb_emit_begin`); (c) `emit_label_lookup_offset(name)` accessor (first DEFINED
label of that name); (d) the `g_is_text &&` gate on `_stmt_seed` LIFTED — m3 mains are now STATEMENT-ORDER chains exactly like m4;
(e) driver m3 proc loop no longer emits LBL__ pseudo-procs standalone; the m4 BODY-ALIAS build is twinned before main's emission and every
LBL__ row is registered from main's live label pool (`<name>_body` → `rt_proc_set_fn`, frame_bytes = main's). NO NEW GLOBALS.
GATES: 60 non-DEFINE crosscheck programs m3 old-vs-new **60 same / 0 broke**; the six-line RETURN repro no longer aborts (RETURN class gone).
⛔ **STOPS ONE CROSSING SHORT:** DEFINE programs now SEGV in m3 (`jmp` to garbage) because the TINY call-site arm is TEXT-only
(`bb_call_proc_staged.cpp:280/549` `MEDIUM_TEXT &&` — itself a standing BOTH-MEDIUM violation): the site's `x86("lea","rax","[rip + __]",0,"<FN>_alpha")`
becomes `movabs rax,0` in binary because the sealed form needs the ABSOLUTE address and the shim lives in the DEFINE stub chain = a DIFFERENT
sealed buffer whose label pool is already freed. So m3 sites fall to the SLIM (C-runtime, by-name) arm, which enters the inline body with a
protocol the RETURN floater's `pop rcx; jmp rcx` does not match. **THE FIX = a cross-chain sealed-symbol table** (name → absolute address,
recorded at each binary `emit_chain` seal for `<FN>_alpha` [and gamma/omega], consulted by the site so binary emits `movabs rax,<abs>; jmp rax`)
+ lifting the two `MEDIUM_TEXT` conjuncts. That table is NEW STATE ⇒ needs Lon's banner-ask, OR ride the existing runtime proc registry
(`rt_proc_set_fn("<FN>_alpha", addr)` — no new global, slightly abusive of the name space). Also `.quad <label>` data under SIG mode must
be binary-capable. Ordering is fine: all stub chains (shims) emit before main; every site is in main (bodies inline).

⛔ OWED / NEXT, IN ORDER: (1) finish part-2 of the baseline sweep and paste the full 13-suite table + META here; (2) mint the minimal witness for the
`match_assign_cond_α` never-emitted class (both media) — this is the Milestone-1 root cause; (3) the tiny-site binary crossing above, then merge
`s91-m3-unify`, then re-run the scorecard (expect beauty_suite m3 to move from COMPILE_FAIL into whatever m4 shows, and the m3 COMPILE_FAIL
column across demos/feature_test to collapse); (4) demos SIG6/SIG6 ×10 (both modes abort at runtime — heap? bomb?) uncharacterized;
(5) push credential — asked in chat.
