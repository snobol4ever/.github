# HANDOFF 2026-06-06 (Opus 4.8) — SNOBOL4 MODE-4 PIVOT + OWNED-BUILD MANDATE

**Repos:** SCRIP + .github. **Identity:** LCherryholmes <lcherryh@yahoo.com>. **Type:** directive/pivot + inventory + design-ownership + S0 rung.

## Lon directives this session (all inscribed)
1. **MODE 4 ONLY** until 100% PASS all SNOBOL4 m4 suites; m2/m3 dead to this goal; never run them. Hygiene/revamp → GOAL-BB-FIXUP exclusively.
2. **OWNED-BUILD MANDATE:** Lon sets boundaries; Claude owns design+build, no design questions back. 5 stages via BBs, new BB per piece, LOWER wiring per existing convention, manual = authority.
3. **RULES OF ENGAGEMENT:** (1) BBs/XAs only through templates; (2) one template may serve multiple IRs but usually not; (3) NO runtime calls from emitted code without express permission (ledger); (4) BB DUMP visible every session; GUI deferred (force-directed when built).

## Landed (SCRIP)
- `083401d` m4-only corpus runner `scripts/test_mode4_only_corpus_snobol4.sh` (all-modes runners now forbidden by goal).
- `7bf0b61`+`b27e06e`+`68747a0` `SNOBOL4-5STAGE-OWNED-BUILD.md`: decisions D1 (jmp-threaded instances, π reg, replaces dead broker clause in ARCH-SNOBOL4), D2 (STITCH_SEQ/ALT = runtime wire_seq/wire_alt), D3 (capture pending-ring + COMMIT at match-γ), D4 (shims fallback till S6, corpus non-decreasing HARD), D5 (ζ-arena instance alloc, no malloc); ladder S0-S7; RoE; permission ledger.
- `d312290` **S0-DUMP ✅**: `--dump-bb` recurses IR_SCAN pat/subj/repl subgraphs (indented four-port) + generic sval/ival fallback; pattern BBs no longer hidden; smoke m4 7/7 held. Residue: ARBNO-inner + S3 instance graphs dump at S3.

## Inventory of record (post-b42ef1c build, this container)
smoke m4 **7/7** · pat-rung **18 PASS / 1 SKIP** (053 FATAL `flat_drive_assign` kind=22, pattern-valued var) · m4 corpus **148/103 FAIL/29 SKIP** of 280 · beauty subsystems **1/17** (emit=4 link=5 diff=7). Clusters + specimen probes in GOAL-SNOBOL4-BB.md.

## Probe artifacts (m4, this session)
- capA: `S='ab'; S 'a' . V 'x' :F(NO)` → `nomatch a` — **M4-CAPTURE-COND proven** (rt_cap_assign_cursor discards is_imm, pattern_match.c:1089).
- capB: literal-subject + non-lit pattern → runtime **BOMB** `bb_scan: TEXT(mode-4) non-literal pattern needs native PB-RB graph`.
- Dynamic-pattern map: IR_PAT_DEFER → rt_defer_match; DT_P arm = Σ-rebase + recursive exec_stmt (no β re-entry — ch.18 violation). All in goal file M4-STARVAR/M4-CRASH notes.

## ⛔ BLOCKED ON LON — permission ledger stamps (RoE rule 3)
(a) **nv get/set** from emitted code (S2/S3/S5); (b) **raw allocator** (S5 splice only). Strike either and Claude engineers around it.

## NEXT SESSION
"here we go" → GOAL-SNOBOL4-BB.md → **S1 SUBJECT-EVERYWHERE** (drop named-var-only guard in flat_drive_scan_native; subject value-chain → ζ → Σ/δ/Δ all routes; probe-first vs sbl; m4 gates; corpus non-decreasing).
