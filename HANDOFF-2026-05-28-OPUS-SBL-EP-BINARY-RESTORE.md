# HANDOFF-2026-05-28-OPUS-SBL-EP-BINARY-RESTORE

**Author:** Claude Opus 4.7
**Date:** 2026-05-28
**Goal:** GOAL-SNOBOL4-BB · M3-NATIVE-4 prerequisite
**Repos:** one4all `df8e6126` · .github (this commit)

---

## Summary

Restored MEDIUM_BINARY byte production in five combinator templates that were stripped to FAKE-JMP stubs by `88bacd2a` (Prolog FACT cleanup, prior session). `audit_m3_native_binary_arms.sh` GATE FAIL → GATE OK. No byte-level change to any other gate.

This unblocks the M3-NATIVE-4 combinator-flat-wire retry described in `GOAL-SNOBOL4-BB.md`. With these arms producing real bytes again, a future session can route XCAT/XOR/XFNCE roots through `patnd_to_bb_tree` + `bb_pat_kid` and expect the combinator BINARY arms to actually fire.

## Five templates touched

`bb_pat_alt.cpp`, `bb_pat_cat.cpp`, `bb_pl_seq.cpp`, `bb_pl_ite.cpp`, `bb_succeed.cpp` — each restored to the FACT-correct inline EP-walk shape (the shape `0e077eb5` originally landed):

- `_str` signature reverts from `(BB_t*)` to `(BB_t*, bb_bin_t & bin)`.
- Inside `IF(MEDIUM_BINARY, ...)`, the loop over `g_emit.xa_bb_emit_pair_*[]` now emits both the byte (`\xE9 + u32le(0)`) AND populates `bin.sites.push_back / bin.labels.push_back / bin.is_def.push_back` inline for every `define[i]` and `jmp[i]` entry. **Duplication is the point** — every byte-and-metadata pair lives in its own template file; no shared helper.
- `extern "C"` wrapper reverts from `bb_emit_asm_result_pairs(s)` to `bb_emit_asm_result(bb_pat_xxx_str(pBB, bin), bin)`.

`bb_emit_asm_result_pairs()` in `emit_str.cpp` is now unused but left in place — it doesn't violate the FACT RULE (no byte production, only metadata reconstruction), and removal can be a separate housekeeping commit.

## Gates (all byte-identical to PLAN watermark except the audit)

| Gate | Before | After |
|------|--------|-------|
| audit_m3_native | **GATE FAIL** | **GATE OK** |
| G1 smoke default | 13/13 | 13/13 |
| G1 smoke `SCRIP_M3_NATIVE=1` | 13/13 | 13/13 |
| G2 broker | 37 | 37 |
| G3 mode-4 corpus | 175/280 | 175/280 |
| G4 mode-2 corpus | 237/280 | 237/280 |
| native corpus | 165/280 | 165/280 |
| Rung suite | M2=19 M4=15 | M2=19 M4=15 |
| Prolog smoke | 5/5 | 5/5 |
| Raku smoke | 5/5 | 5/5 |
| Icon smoke | 5/5 | 5/5 |
| Rebus smoke | 4/4 | 4/4 |
| FACT RULE grep | 0 | 0 |

## WIP investigated this session but NOT committed

Attempted `patnd_to_bb_tree` + combinator-root dispatch in `patnd_needs_xlate`. Built; G1 smokes green default+native; rung suite M2=19/M4=15 held. But broad corpus mode-2 regressed 237→229.

**Root cause discovered (the genuinely new finding):** `patnd_to_bb_tree` exposes a latent bug in runtime XNME/XFNME varname plumbing. `pat_assign_cond/imm` (in `src/runtime/snobol4/snobol4_pattern.c`) sets `p->var = var` where `var` is the result of `NAME_fn(varname_str)`. `NAME_fn` calls `NV_PTR_fn` which **always creates the variable cell on first lookup**, so it always returns `NAMEPTR(cell)` (DT_N, slen=1, .ptr=cell) — never `NAMEVAL(varname)` (DT_N, slen=0, .s=varname). The legacy `build_patnd` XNME/XFNME fallback at `src/lower/lower_pat_dcg.c`:

```c
bb->sval = (pp->STRVAL_fn && pp->STRVAL_fn[0]) ? pp->STRVAL_fn :
           ((pp->var.v == DT_N && pp->var.s) ? pp->var.s : NULL);
```

For NAMEPTR, `var.s` is the cell pointer reinterpreted as `char*` — garbage. Empirically the first byte happens to be 0, so `bb->sval = ""` (empty string), and the bb_capture template's MEDIUM_BINARY arm hits its `!varname[0]` honest-skip branch — emitting nothing and never defining `lbl_β`. Outer `flat_drive_cat` references `xcat0_right_β` → `bb_emit_end` aborts with "unresolved forward reference".

This bug **has always been present** but was masked because XCAT roots were never routed through `patnd_to_bb_graph` (they were rejected by `patnd_needs_xlate`) — the cast-as-BB path was used instead, which never reads `STRVAL_fn`. Combinator flat-wire surfaces it immediately.

### Fix sketch (verified locally, reverted before commit per safe-handoff policy)

In `pat_assign_imm`/`pat_assign_cond` populate `p->STRVAL_fn` from the var DESCR:

```c
if (var.v == DT_N) {
    if (var.slen == 0 && var.s && var.s[0]) {
        p->STRVAL_fn = GC_strdup(var.s);                       /* NAMEVAL */
    } else if (var.slen == 1 && var.ptr) {
        const char *nm = NV_NAME_fn((const DESCR_t *)var.ptr); /* NAMEPTR */
        if (nm && nm[0]) p->STRVAL_fn = GC_strdup(nm);
    }
}
```

with new helper `NV_NAME_fn(const DESCR_t *cell)` in `snobol4.c` that scans `_var_buckets` for `&e->val == cell` and returns `e->name`. (NAME_fn creates entries via `e = GC_malloc(sizeof(NV_t)); e->name = GC_strdup(name); ...` — the `name` field IS already populated; we just need the reverse-lookup.)

With this fix in place + `patnd_to_bb_tree` + extending `patnd_needs_xlate` to combinator roots, mode-2 should hold at 237/280 or climb; native should climb above 165 as combinator BB blobs start firing correctly. Two probes from the prior session log are expected to flip to PASS native: `050_pat_alt_two` (expect `dog`) and `055_pat_concat_seq` (expect `ab cd ef`).

## NEXT (in order)

1. **Land the XNME varname fix** described above. Pure runtime change in `snobol4_pattern.c` + new helper in `snobol4.c`. Should be behavior-neutral with current routing (XNME roots still go through the cast path), but will be the foundation for step 2.
2. **Land `patnd_to_bb_tree`** in `lower_pat_dcg.c` + extend `patnd_needs_xlate` in `stmt_exec.c` to recognize combinator roots. Dispatch on `patnd_is_combinator_root(pp)` for the builder choice. The graph-shape diagnosis (Prerequisite #1) and label-arena (Prerequisite #2 — `744ae342`) are both addressed; with the varname fix the empty-emission hole closes too.
3. **Validate 050/055 native**; expect PASS.
4. **Run all gates** — expect mode-2 ≥ 237/280, native ≥ 165/280 with a meaningful cluster of capture-in-XCAT patterns now passing.
5. **Then** SBL-SPAN-2 / SBL-ARBNO-3 / SBL-BREAKX-2 BINARY arms per the per-cluster knockdown plan in GOAL-SNOBOL4-BB.md.

## Files touched this commit

- `src/emitter/BB_templates/bb_pat_alt.cpp`
- `src/emitter/BB_templates/bb_pat_cat.cpp`
- `src/emitter/BB_templates/bb_pl_seq.cpp`
- `src/emitter/BB_templates/bb_pl_ite.cpp`
- `src/emitter/BB_templates/bb_succeed.cpp`

## Session state

```
HEAD one4all       = df8e6126
HEAD .github       = (this commit)
GATE-1 smoke       = 13/13     (also 13/13 under SCRIP_M3_NATIVE=1)
GATE-2 broker      = 37        (sibling-influenced)
GATE-3 mode-4      = 175/280
GATE-4 mode-2      = 237/280
NATIVE corpus      = 165/280
Rung suite         = M2=19 M4=15 SKIP=0
Prolog smoke       = 5/5
Raku smoke         = 5/5
Icon smoke         = 5/5
Rebus smoke        = 4/4
FACT RULE          = 0
audit_m3_native    = GATE OK   (was FAIL at session start)
GATE-PK            = stale (re-freeze deferred)
```
