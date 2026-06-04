# HANDOFF 2026-06-04 (Opus 4.8) — PROLOG-BB: LOWER SPLIT · PL-GZ-1 · PL-GZ-1b MODE-3 TRUTH · CORPUS-S-HYGIENE · PL-GZ-2 DESIGN

**HEADS:** SCRIP `b6913ec` (was `14ec99a` at session start) · .github this commit · corpus UNTOUCHED (clean).
**Gates at HEAD:** GATE-1 `5/5 HARD · 2/0/3-EXCISED · 5/5` · GATE-3 `115/115 HARD · 12/0/103-EXCISED · 105/0/10`
· coupling PASS (choice 19 · goal 10 · others 0 · rung05 .s 39) · one-box PASS · pl-no-value-stack PASS
· no_bb_bin_t OK · FACT greps 0/0 · prove_lower2 PASS · siblings Icon m2 12/12 · SNOBOL4 m2 7/7.

## Directives received (Lon, this session)
1. **Per-language LOWER split** — "a unified AST/LOWER stage does not buy much; it is truly the shared IR
   graph which is LANGUAGE INDEPENDENT." Prolog → `lower_prolog.c` now; the rest split from `lower.c` later.
2. **Mode definitions are NORMATIVE** — m2 = the ONLY interpreter mode; m3 = EMIT and RUN in-memory in the
   CURRENT process; m4 = EMIT, assemble, link, EXECUTE as a system process. If the implementation has m3
   interpreting → rung + steps + big banner. (It did. See PL-GZ-1b.)
3. **CORPUS-S-HYGIENE** — gates STOP updating corpus `*.s`; tracked `.s` are frozen DEMO artifacts only
   (roman, wordcount, claws5, treebank, …). Keep-list still needs Lon's confirmation (step b).

## Landed (SCRIP, in order)
- **`d6d93c6` — LOWER SPLIT.** `src/lower/lower_prolog.c` (535 ln): g_unify/g_arith_expr/g_compare/
  g_term_compare/g_is/g_term/g_builtin/g_goal/g_ite/g_neg_goal/g_not_unify/g_catch/g_findall/g_phrase/
  lower_goal + lower2_goal_entry + g_head_unify + lower2_clause_body_entry. `lower.c` 1914→1373 ln. NEW
  `lower_internal.h` (30 ln): lcx_t/role/pl_vars_t typedefs + de-static'd shared spine (lower2, lower_goal,
  lower_unhandled, nalloc, set_succ_fail, ret, emit_leaf, wire_seq, wire_alt, tm, tm_g) — collision-checked.
  `wire_det_builtin1` stayed (Icon value-role). Makefile: scrip rule + RT_PIC_SRCS. Entry points were
  already extern'd at call sites (lower_program.c:335, prove_lower2.c:17). All gates byte-identical.
- **`04804fb` — PL-GZ-1 coupling gate** `scripts/test_gate_pl_coupling.sh`. Normative seven symbols;
  call site == comment-stripped `SYM@PLT` emission. Measured ceilings: bb_choice 19 · bb_goal 10 · all
  other templates 0 · rung05 emitted .s 39 (the reset handoff's 24/14/4 counted CP-push/trail/unify sites
  outside the normative set; bb_unify's 4 were sanctioned rt_unify_* VALUE calls = 0 here). Ratchet down
  never up; new files default ceiling 0. Negative proven (injected call → exit 1). Emits into mktemp.
- **`5a7bb41` — PL-GZ-1b(a,c) MODE-3 TRUTH.** scrip.c mode_run/Prolog had a SILENT
  `(void)IR_interp_once(pl_main)` fallback counted as m3 PASS. (a) LOUD stderr marker
  `[PBB] MODE-3 INTERP-FALLBACK` before it. (c) the native flat-walk MISCOMPILED var↔ATOM unify — printed
  the rodata LABEL (`.S0`) instead of the atom, BOTH orders; THIS was the old "GATE-1 m3 4/5 known harness
  artifact". IR_ATOM evicted from `pl_flat_goal_is_simple`'s const set (var↔LIT_I probe-proven, stays).
  GATE-1 harness m3 capture `2>&1`→`2>/dev/null` aligning with m2/m4. GATE-1 m3 → 5/5 honestly.
- **`15642ab` — CORPUS-S-HYGIENE(a).** `run_prolog_via_x86_backend.sh` emits `.s` + `bb_macros.s` into
  its mktemp WORK dir, never next to the source. Full GATE-3 compile leg proven corpus-clean (0 dirty).
  The old "corpus .s label-churn discard" toil is GONE — do not expect or re-create it.
- **`25549a5` — PL-GZ-1b(d).** GATE-3 + GATE-1 detect the marker (suite: stderr→ERRTMP; smoke: per-run
  tmp) and count those programs EXCISED while STILL verifying output (mismatch = FAIL, never hidden).
  Re-baseline: GATE-3 m3 **12/0/103-EXCISED** (12 native: rung01 hello · rung22 write_canonical ·
  rung23 arith_ext ×5 · rung29 number_ops ×5) · GATE-1 m3 **2/0/3-EXCISED**. Zero FAILs.
- **`b6913ec` — prove_lower2.sh carries the split** (compile+link lower_prolog.c); RED→GREEN. Caught by
  the SHARED-LOWERER FACT RULE completion test during this handoff.

## .github landed
`3b3bc01f` (Three-modes block rewritten to the normative definitions; PL-GZ-1b rung inserted; watermark
annotated; PL-GZ-1 marked LANDED; CORPUS-S-HYGIENE step) · `88121e64` (1b(d) marked; gate table
re-baselined) · `c7ddbf25` (PL-GZ-2 DESIGN) · `97cbb750` (SHARED-LOWERER FACT RULE lockstep-amended in
all three GOAL files for the per-language split, md5-verified identical; KEEP-list wording; gate-table
header; this handoff).

## PL-GZ-2 — next, DESIGN IS IN THE GOAL (recon at `25549a5`)
Three load-bearing recon facts: (1) the seed collapses four ports to (entry∈{α,β}, verdict-in-rax);
choice = clause cursor + trail-mark in the predicate's OWN ζ row; conj = λ-checked wiring with
β-resumption; cut = β→ω wiring. (2) the x86()-self-encoding ONE-body template idiom already serves both
mediums (bb_pat_pos.cpp style; PORT_GAMMA/OMEGA/BETA; IF(MEDIUM_TEXT,…) decoration only) — m3 consumer
`bb_build_flat` (emit_bb.c:2495, EMIT_BINARY_WIRED → RX slab), m4 consumer = codegen text walk. (3) BOTH
Prolog driver branches already front-tier on `pl_flat_body_root` — the ONE shared gate (`pl_gz_admit`)
slots symmetrically in FRONT of both; non-admitted falls THROUGH to today's tiers, so GATE-3 legacy
counts stay frozen by construction. Build sub-steps (a)–(f) in the GOAL under PL-GZ-2. Box names
(`bb_query_frame`/`bb_det_write`/`bb_det_nl`) are Lon-adjustable.

## Next (in order)
1. **PL-GZ-2 build** per sub-steps (a)–(f) — fresh session, design sealed.
2. **CORPUS-S-HYGIENE (b)** — prune tracked corpus `.s` to the DEMO keep-list; NEEDS Lon's confirmed list.
3. **PL-GZ-1b(e)** — executes at the PL-GZ FENCE only (delete the fallback; uncovered `--run` prints
   EXCISED and exits like m4).

## Cautions
- Do NOT open PT-4b or WAM-CP (legacy, closed). The m2 ITE-commit oracle bug stands until PL-GZ-7.
- m3's GATE-3 number is now 12/0/103-EXCISED BY DESIGN — it is the truth, not a regression; m2 HARD and
  m4 numbers are the unchanged legacy watermark. "Legacy counts must not regress" applies to m2/m4 and to
  m3's PASS floor (≥12, growing only via PL-GZ).
- `lower_internal.h` is now lockstep scaffolding (FACT RULE rule 5): signature changes to the shared spine
  update all three GOAL files in the SAME commit.
- The coupling gate's `.s` leg compiles rung05 fresh into mktemp; corpus `.s` are never regenerated by any
  gate now. Session setup unchanged: install_system_packages.sh · make -j4 scrip · make libscrip_rt.
