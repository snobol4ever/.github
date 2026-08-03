# FINDING 2026-08-03e-3 — SN4 HQ DIRECTIVE AUDIT: six NOT-TRUEs, roman prints VI, and the -O0 perf baseline

**Seat:** Lon-directed advisory/HQ. **Method:** Lon supplied his standing directives verbatim; every claim measured against origin HEAD (SCRIP `c9d84615`, corpus `c092374e`) — source + committed `.s` artifacts + a live bench run. Perf labeled **RT_OPT=-O0** per O2-DIRECTED-ONLY (no `-O2` directed this session).

## 1 · SCOREBOARD

**TRUE at HEAD:** one-instruction carve via `x86_alpha_carve` (admitted set) · ELIDE switchable (`SCRIP_SLOT_ELIDE=0`, live) · `zls_build` exists as the offset traversal · FOUR-mode parameterized operand spellings (`ZRES/ZOPQ/FRQ/HKQ`) · IF-logic-in-templates for zeta modes · FLAT glue proven (`bb_glue_pass_wires`).
**PLANNED and routed:** per-BB-only allocation + UCLAIM death (Steps 1–4, DoD-4) · fail-side rollback as default (U-1b, gate OFF today) · RBP at STATEMENT/FUNCTION/ARBNO/FENCE1 (U-2; match frame live on 49) · FRAMED glue #2 ("needs building", s39) · frameless folded-pattern calls (pat_static FLAT arm live; slow arm C-frames).
**NOT TRUE:** #1 roman `proc_LBL` · #2 no-frame-relative-operands · #3 ONE offset authority · #4 statement-only scoping · #5 every-BB switchable · #6 CALL "just sets up the frame."

## 2 · NOT-TRUE #1 — "get rid of proc_LBL__ROMAN_α already"

Measured in the committed artifact: line 4 `proc_LBL__ROMAN_α:` · line 5 `proc_LBL__ROMAN_α_body:` · **lines 5–900 ≈ 897 lines of main's statement boxes DUPLICATED** (33% of 2713; why roman carries 2× `sub rsp,240` and every roman number double-counts) · real `proc_ROMAN_α` at 901 (~42 lines) · main chain from 943. OMEGA s39 told Lon *"proc_LBL__ROMAN_α is ALREADY EMPTY (two labels, zero instructions)"* — true of the **label**, false of the 897-line body it fronts, i.e. the thing the directive named. Third conviction of answering-the-letter. **FIX exists verbatim = finishing-plan Step 5** (`scrip.c` ~:887/~:1348, emit main first, every `proc_LBL__*` a 2-line trampoline; acceptance roman 2713→~1818, 318 BY SET identical, every LBL section ≤5 lines). **ASSIGNED: its own session, HQ/OMEGA seat (per ALPHA s38 "wants a fresh session"). The ≤5-line grep joins U-GATE.**

## 3 · NOT-TRUE #2 — "There is NO FRAME RELATIVE addressing anymore for operands. Not. None."

roman.s: **96 `[rbp` refs** vs 434 `[rsp`. Tree-wide: **9,842 rbp data refs** (s33b watermark). The sanctioned slice is HKQ housekeeping (48B match frame); the rest is FRQ-on-pinned-graph operand traffic (blob members, UCLAIM slots — the O-PB-1 crash was literally a cset read from stale `[rbp+152]`). Routed via the U ladder, but "Not. None." is currently unmeasurable — **U-GATE gains an `rbp-op-refs` column** so the number is watched, not vibed.

## 4 · NOT-TRUE #3 — "ONE main function that does graph traversal and calculates the zeta offsets"

`zls_build` is the ONE — and it has company. Measured carve authorities outside it: the UCLAIM owner-table arm (`zvo_resolve`) · `bb_match_begin.cpp:57/:175/:194` in-template `x86_zclaim` (48B stfh + 32B hfc ×2) · `bb_save_restore.cpp:83` `x86_zclaim(sb)` (dynamic size). Line :175's comment **quotes the directive verbatim** ("each BB allocates its LOCAL STORAGE... by one instruction, decrement RSP") while constituting the extra authority — the directive reached the code piecemeal, each landing locally right and globally a fork. Routing: the UCLAIM arm dies at Steps 1–4; the match zclaims fold into planner K at U-2; save_restore's at the ZD-7 protocol work. Consolidation is a DoD-adjacent audit, not a new mechanism.

## 5 · NOT-TRUE #4 — "NO FUNCTION-level processing whatsoever. ONLY statement level scoping."

Live violation at HEAD: **owner-table cross-statement closure contamination** (s40 O-PB-2a measurement — stmt1's ASSIGN_SAVE/LIT_STRING/ASSIGN_IMM inflate stmt2's claim via the `cm[]` walk; +224B on any.sno stmt2). The s21x-w law's remaining breach lives in the owner table's base scoping. Routed: ALPHA owner-table fix, queued after U-GATE (already in ALPHA's advisory queue).

## 6 · NOT-TRUE #5 — "You should be able to turn on allocation dynamically FOR EVERY single BB. No need to be shy."

The shyness is institutionalized: `zd_wl_kind` absences, `zdyn` vetoes, `SCRIP_ZD_PATREF` default OFF, pat_static declines. All individually justified, collectively the opposite of the directive. The DoD's coverage conditions are the end state; **U-GATE's ω-coverage census is the shyness meter** — the number replaces the argument.

## 7 · NOT-TRUE #6 — CALL "just sets up the stack frame with RBP/RSP, and that is all it does"

`bb_call_proc_staged.cpp` does staging, GVA installs, SCC paths — far beyond frame setup. And the flagship proves the family broken end-to-end: see §8. D9's two-box minimal call (SAVE_RESTORE + frame-only CALL) is the target shape, not current truth.

## 8 · BENCH TRUTH — the 18/21 board is honest, and its red set is load-bearing

Live run at HEAD reproduced **18/21 m3 EXACTLY** (timing-insensitive diff vs `.ref`). The three reds: **`roman` — silent WRONG OUTPUT `result: VI` vs `MDCCLXXVI`** (the s23q "last recursion level only" signature, predicted to clear at A-2, DID NOT — accumulated conversion lost across the call chain, exactly the state-release-on-the-wrong-side class the UNWIND addresses) · **`eval_fixed` — segv rc=139** (the U-1 tail class) · `eval_dynamic` — timeout. **`roman` + `eval_fixed` JOIN THE U-2 WITNESS SET: if the unwind model is right, both flip.** Also: `indirect_dispatch` emits no `ms:` line — a benchmark that cannot time itself cannot regress visibly; fix program or `.ref`.

## 9 · PERF BASELINE vs SPITBOL — RT_OPT=-O0, best-of-3, self-timed ms

| program | SPITBOL | SCRIP -O0 | ratio | | program | SPITBOL | SCRIP -O0 | ratio |
|---|---:|---:|---:|---|---|---:|---:|---:|
| string_concat | 147 | 9 | 16.33× | | arith_str | 354 | 461 | 0.77× |
| pattern_bt | 508 | 93 | 5.46× | | func_call | 1009 | 1894 | 0.53× |
| var_access | 1599 | 382 | 4.19× | | func_call_ovh | 995 | 1921 | 0.52× |
| op_dispatch | 127 | 33 | 3.85× | | string_pattern | 709 | 1508 | 0.47× |
| arith_int | 4948 | 1327 | 3.73× | | string_manip | 667 | 1483 | 0.45× |
| arith_mixed | 2367 | 651 | 3.64× | | mixed_workload | 183 | 418 | 0.44× |
| arith_loop | 49 | 14 | 3.50× | | fibonacci | 196 | 495 | 0.40× |
| pattern_bt_deep | 8355 | 2878 | 2.90× | | table_access | 365 | 1188 | 0.31× |
| | | | | | table_churn | 342 | 1132 | 0.30× |

**geomean 1.34× · median 0.77× · 8/17 faster.** The shape is bimodal and architectural: wins = the compiled spine (concat/patterns/arith/var); losses cluster in exactly two families — **CALL (0.40–0.53×)** and **TABLE (0.30–0.31×)** — the un-migrated C-sink surface. A directed `-O2` runtime build would move the losing set most (needs Lon's explicit directive; run detached with the s126 before/after artifact checks). "Ten times faster": achieved n=1 (string_concat), geomean 1.34× at -O0.

## 10 · POSITIVE-CONTROL LAW (add to every new instrument, U-GATE first)

This session's first bench harness scored **1/21** by strict-diffing the `ms:` timing line against fixed `.ref`s — a confident number measuring the wrong thing, caught only because the output was absurd. Second conviction of the class (ZD-DEPTH's first census was wrong 3×). **LAW: before an instrument's number is ever quoted, hand-verify one known-good and one known-bad case through it.**
