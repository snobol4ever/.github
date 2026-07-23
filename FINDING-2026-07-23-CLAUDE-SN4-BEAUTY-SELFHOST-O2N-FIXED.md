# FINDING: SN4 Beauty Self-Host O(n²) Lowering Blowup — ROOT-CAUSED AND FIXED

**Date**: 2026-07-23  
**Session**: s134  
**Status**: RESOLVED — source committed, artifacts regen'd; two remaining blockers characterized  
**Supersedes**: FINDING-2026-07-23-CLAUDE-SN4-BEAUTY-SELFHOST-SHARE-GRAPH-BLOCKED-ON-REEMISSION.md

---

## Problem

`scrip --compile beauty.sno < beauty.sno` hung indefinitely — both modes rc=124 at 90s, no output.

## Root Cause — Three Sites

**Site 1 — DEFINE entry-in-main O(n²) (lower_snobol4.c ~line 2159 pre-fix)**  
The entry-in-main DEFINE branch called `sno_build_graph(st, nst, eidx, is_def, rn)` —
re-lowering the FULL main array (nst ≈ 208) once per DEFINE. beauty has 78 DEFINEs → O(n²).

**Site 2 — LBL__ emission explosion (lower_snobol4.c ~lines 2122-2140 pre-fix)**  
The LBL__ loop shared main's graph (reusing `proc_table[pi].bb_idx` / same entry node).
This avoided re-lowering but caused `emit_chain` to re-emit main's suffix from each entry.
beauty has 8478 LBL__ entries → 15M-line `.s` explosion.

**Site 3 — asm_sym_name mangling bug (scrip.c:58, pre-existing latent)**  
Mangler only did `/`→`$`. beauty has SNOBOL labels with punctuation that are
computed-goto targets: `pp_:()`, `pp_:<>`, `pp_:S()`, `ss_:()` etc. (line 259:
`$('pp_' t)`, line 475: `$('ss_' t)`). These produced illegal gas symbols
(`proc_LBL__pp_:()_α`). beauty never reached emission before — this was dormant.

## The Fix — SCRIP commit 82c9f67a (src/lower/lower_snobol4.c + src/driver/scrip.c)

**Helpers added before `lower_sno_stage2` (lower_snobol4.c):**
- `sno_lbl_index(st,nst,nm)` — statement index for a label, -1 for terminals/not-found
- `sno_reach_body(st,nst,eidx,is_def,inbody)` — BFS reachable-statement set from entry
  following fall-through + local S/F/U label gotos; RETURN/FRETURN/END/NRETURN/computed
  `$`-gotos are terminals; fills `char* inbody[nst]`, returns reachable count

**DEFINE entry-in-main branch:** replaced `sno_build_graph(st, nst, eidx, ...)` with
reachable-body extraction → build `bst`/`bis` subset arrays from `inbody[]`, then
`sno_build_graph(bst, bk, bentry, bis, rn)`. O(body) not O(main). Out-of-body gotos
reach main labels via `rt_goto_transfer` automatically (sno_goto_target line 673-678).

**LBL__ loop:** replaced shared-graph with per-LBL__ small reachable-body graph →
`sno_build_graph(bst, bk, bentry, bis, NULL)`, `proc_entry_node = NULL` (small graph's
own entry), `bb_idx = bb_program_add(gl)`. Eliminates per-label suffix re-emission.

**asm_sym_name (scrip.c:58):** preserve `[A-Za-z0-9_$.]`, mangle every other byte to
`$%02X` hex. `$` preserved → existing `EXPR$0` symbols untouched. Runtime lookups use
the original key string — consistent since `asm_sym_name` is the single mangling point
(used at symbol definition AND `lea` address-taking; greek suffix appended after).

## Results

| Metric | Before | After |
|---|---|---|
| beauty compile time | >180s (abort/timeout) | **24s rc=0** |
| beauty .s size | 15M lines | **1.41M lines** |
| beauty link | gas errors (illegal symbols) | **clean** |
| beauty run | no output | **runs rc=0** |
| SN4 crosscheck m3 | 302 PASS / 8 FAIL | **307 PASS / 3 FAIL** |
| SN4 crosscheck m4 | 302 PASS / 6 FAIL | **307 PASS / 3 FAIL** |
| DIVERGE | 0 | **0** |
| Icon crosscheck | 4/0 | **4/0** |
| Prolog crosscheck | 188/0 | **188/0** |
| eim.sno guard (m3+m4) | green | **green** |

**5 tests fixed** (restores FINDING's stated 307 watermark; HEAD s133 had regressed to 302):
`1020_code_label_transfer`, `1021_code_direct_goto`, `214_indirect_goto`,
`215_indirect_goto_cond`, `216_indirect_goto_computed`

**3 remaining failures** (identical in pristine, pre-existing baseline):
`test_case`, `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`

**Artifacts regen'd:** feature `.s` (SCRIP commit 6bd64d00, 11 files),
demo `.s` (corpus commit afa1400f), benchmark `.s` (corpus, same session).

## Remaining Blockers (byte-identical beauty self-host — separate from this fix)

### Blocker 1 — LBL__ scale: entry table overflow
Per-LBL__ small-body graphs: reachable bodies from early main labels span most of main
(main flows to END not RETURN) → Σ entries > 65536 cap → abort in 5s.

A temporary probe (ZLS_MAX_ENTRIES 1<<19) confirmed correctness end-to-end:
beauty compiled (24s, 1.41M lines), linked cleanly, ran rc=0.
Reverted before commit — growing tables is not the solution (Lon: "losing game").

**Clean fix: emitter label-registration.** During main's `emit_chain`, register each
emitted label address via `rt_label_register_fn(name, addr)`. Add an `rt_goto_transfer`
arm for registered main labels. This eliminates separate LBL__ emissions entirely —
zero extra emission, zero entry pressure. Requires BB-CODEGEN/TEMPLATE-REVAMP.

### Blocker 2 — Pattern engine: *Parse recursive-grammar match
beauty's main match (line 616: `Src POS(0) *Parse *Space RPOS(0)`) fails under SCRIP
but succeeds under oracle → only 10 lines output ("Parse Error") vs oracle 622 lines.

This match is in **MAIN** (lowered identically to before this fix, line 2073) —
independent of the DEFINE/LBL__ work. Basic deferred `*VAR` patterns work in SCRIP;
the gap is with beauty's complex recursive grammar pattern specifically.

**Next:** MONITOR-FIRST investigation — 2-way sync-step monitor to bracket first
divergence between `Parse` pattern construction (in the DEFINE bodies) and the
`Src POS(0) *Parse *Space RPOS(0)` match execution in main.

## Acceptance Gate Status

| Gate | Status |
|---|---|
| `scrip --run beauty.sno < beauty.sno` = 622 lines md5 `9cddff25...` | NOT MET (blocker 2) |
| eim.sno m3 AND m4 = `fact(5)=120 / fact(8)=40320` | **MET** |
| crosscheck m3/m4 ≥ 307 DIVERGE=0 | **MET (307/0)** |
| .s artifact regen committed | **MET** |
