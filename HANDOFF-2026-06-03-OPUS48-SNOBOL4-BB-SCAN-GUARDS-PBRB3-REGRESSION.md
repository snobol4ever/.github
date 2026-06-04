# HANDOFF 2026-06-03 (Opus 4.8, session 3) — m4 scan subject/replacement SILENT-WRONG → LOUD; pat-bb probe suite un-darkened; PB-RB-3 found STRUCTURALLY REGRESSED; restore designed (= REG-0)

## Leg 1 — five m4 scan SILENT-WRONGs → LOUD (SCRIP `f406239`)

Closed the prior handoff's flagged-UNVERIFIED hole: subject/replacement classification in `flat_drive_scan_stmt`
was entry-only. Oracle-probed matrix (A–G): const-concat repl OK (lowerer fold); var repl / var-concat repl /
lit-leading-concat repl SILENTLY DELETED (repl=NULL ≡ deletion); compound subject ×2 SILENTLY FAILED the match.
Ground truth: value graphs put the combinator (IR_SEQ=10) at entry; **legit deletion lowers as `IR_LIT_S ""`** —
the NULL-repl path is NEVER legitimate, so the guard has zero deletion ambiguity. FIX mirrors `9e8e4b8`:
`scan_val_is_single_lit()` (sentinels + exactly one IR_LIT_S) replaces both entry-only checks; TEXT arm bombs on
no-name-no-lit subject and on `is_repl && !replace_lit`. m2/m3 byte-paths untouched (BINARY drives full graphs
via rt_scan). Manual grounding ch.14: replacement evaluated only after match success; absent field = null string;
literal subject valid only without replacement. 2 files, +16/−2.

## Leg 2 — probe suite dark since LI-2; PB-RB-3 regression surfaced (SCRIP `c4da0b1` + goal-file `[~]`)

All 3 `test/snobol4/pat_bb/` probes failed to LINK since LI-2 renamed `sno_flat_chain_build`→
`gvar_flat_chain_build` (suite wired into no gate → invisible). Sweep landed; honest state **1/3**: both
`_3_match` probes abort at `bb_emit_end: unresolved smatch%d_adv`. Root cause: **`bb_match.cpp` no longer
exists** — stubbed in TEMPLATE-REVAMP ("was offset-table"), stub deleted by STUB CLEANUP `cd10224`; emit_core has
no IR_PAT_MATCH/IR_SUBJECT arms; `g_subject_slot` orphaned. Goal checkbox flipped `[x]`→`[~]` with the finding.

## Leg 3 — PB-RB-3-RESTORE designed to the keystroke (= REG-0; design-only, tree green)

Original recovered: `git show 706d665:src/emitter/BB_templates/bb_match.cpp` (byte-level doc intact; LEGACY
storage — copy the ALGORITHM not the cells). New design: ONE bb_match template, THREE emissions from the one
node (`op_ival` sub-kind {head,retry,advance}); ports REMAPPED per FILL (advance's γ→match_retry — verified
trick, flat_drive_cat does it); retry FALLS THROUGH into the inline element (no elem_entry label at all);
start slot driver-claimed once, shared via `op_off`; bb_subject writes Σ→`[r12+sa]`/Δ→`[r12+sa+8]`. Full
drafted bodies + 6-step integration checklist + **2 VERIFY-FIRST items (FRQ qword constructor — the REX.B bug
class; EMIT_PAIR_FILL multi-emission semantics)** in
`HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORE-DESIGN.md`. On green: probes 3/3, flip PB-RB-3 + REG-0,
then PB-RB-4 ALT/CAT probes (flat_drive_alt/cat verified present + port-correct — invariant PB-RB-4 likely
needs NO new STITCH machinery).

## Gate state (final pushed tree `c4da0b1`, rebased over `f13838f` ICN-SCAN-0 + `0604ae5`, rebuilt + re-gated)

SNOBOL m2 **7/7 HARD** · m3 **6/6** · m4 **6/6** · Icon m2 **12/12 HARD** · prove_lower2 **67** ·
no_bb_bin_t 0 · LANG-NAMES 17 stash-compared Δ0 · concurrency OK · REG-FENCE TIER1=0 · no-handencoded
`--strict` 0 · unified-broker 32 · pat-bb probes 1/3 (honest; RESTORE rung owns the 2).

## Build / verify recipe

```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_snobol4.sh ; bash scripts/test_smoke_icon.sh
bash scripts/prove_lower2.sh ; bash scripts/test_gate_no_bb_bin_t.sh
bash scripts/test_sno_pat_bb_probe.sh        # 1/3 until RESTORE lands
```

## Watermark

SCRIP tip **`c4da0b1`** (pushed). .github tip = this commit. Detail: this file +
`HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORE-DESIGN.md`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
