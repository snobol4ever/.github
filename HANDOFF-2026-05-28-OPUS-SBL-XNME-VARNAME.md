# HANDOFF 2026-05-28 — Opus 4.7 — SBL-XNME-VARNAME prerequisite + upstream interaction

**Goal:** GOAL-SNOBOL4-BB.md — M3-NATIVE-4 prerequisite landed; `patnd_to_bb_tree` retry now unblocked from the varname side.

## State at handoff

- one4all HEAD `48409299`, pushed.
- .github HEAD `(this commit)`, pushed.
- Modes 2+3 only (mode 4 deferred per Lon's call — full mode-4 sweep at the very end).

## What landed this session

### `48409299` — SBL-XNME-VARNAME: populate STRVAL_fn at pat_assign_imm/cond construction time

The M3-NATIVE-4 prerequisite the prior GOAL-SNOBOL4-BB.md session log called out
("XNME/XFNME varname plumbing bug … fix is local to `pat_assign_imm/cond` …
behavior-neutral with current routing"). Landed exactly as scoped.

**Bug:** Runtime-built XNME/XFNME captures (`pat_assign_cond/imm` in `snobol4_pattern.c`)
stored the varname only in `pp->var` (DESCR_t, kind DT_N — NAMEVAL or NAMEPTR) —
NOT in `pp->STRVAL_fn`. Downstream readers in mode 2 (`bb_exec.c` XNME/XFNME
execution) and the lowering (`lower_pat_dcg.c:484/498`) read `STRVAL_fn` first,
then fell through to `pp->var.s`. For NAMEPTR (`.slen==1`), `.s` is the cell
pointer reinterpreted as `char*` → garbage. Latent because XCAT roots didn't
flow through `patnd_to_bb_graph` previously (`patnd_needs_xlate` doesn't route
combinator roots); surfaces immediately when combinator flat-wire is enabled.

**Fix:** new static `_assign_varname_str(DESCR_t var)` in `snobol4_pattern.c`:
```c
if (var.v != DT_N) return "";
if (var.slen == 0 && var.s && *var.s) return GC_strdup(var.s);
if (var.slen == 1 && var.ptr) {
    const char *nm = NV_name_from_ptr((const DESCR_t *)var.ptr);
    if (nm && *nm) return GC_strdup(nm);
}
return "";
```
Called from both `pat_assign_imm` and `pat_assign_cond` to populate
`p->STRVAL_fn`. `NV_name_from_ptr` is already exported and already in use at
`snobol4_pattern.c:601` by `opsyn()` — no new public API.

**Cosmetic followup (deferred, intentional):** `lower_pat_dcg.c:484` and `:498`
still carry the prior session's defensive `(pp->STRVAL_fn && pp->STRVAL_fn[0])
? pp->STRVAL_fn : ((pp->var.v == DT_N && pp->var.s) ? pp->var.s : NULL)`
fallback. Now that `STRVAL_fn` is always populated at construction, this
collapses to `bb->sval = pp->STRVAL_fn ? pp->STRVAL_fn : ""`. Left in place
deliberately so the next session's `patnd_to_bb_tree` work can validate the
collapse against the combinator-tree path with a clean baseline.

## Gates (modes 2+3 only — mode 4 deferred per Lon's call)

| Gate | Pristine | Post-patch (pre-rebase) | Post-rebase | Δ from pristine |
|---|---|---|---|---|
| GATE-1 default smoke | 13/13 | 13/13 ✅ | 13/13 ✅ | 0 |
| GATE-1 SCRIP_M3_NATIVE=1 smoke | 13/13 | 13/13 ✅ | 13/13 ✅ | 0 |
| Pattern rung suite M2 | 19/19 | 19/19 ✅ | 19/19 ✅ | 0 |
| Mode 2 broad corpus | 237/280 | **245/280** ✅ | 237/280 | **0 (see "Upstream interaction" below)** |
| Mode 3 native broad corpus | 165/280 | 165/280 ✅ | 142/280 | **−23 (upstream, NOT my patch)** |
| audit_m3_native_binary_arms | GATE OK | GATE OK ✅ | GATE FAIL | **upstream regression** |
| FACT RULE | 0 | 0 ✅ | 0 ✅ | 0 |

**Verified via full failure-set diff** (after temporarily defeating the test
script's `head -40` truncation): my pre-rebase patch produced exactly **+8 mode-2
wins, ZERO regressions, ZERO mode-3 change** — exactly the "behavior-neutral with
current routing" outcome the GOAL doc predicted. The 8 newly-passing tests are
the ones that exercise runtime-built XNME/XFNME with NAMEPTR vars:
`120_pat_calc_add`, `126_pat_json_number`, `127_pat_json_keyvalue`,
`131_pat_boolean_expr_grammar`, `145_pat_left_assoc_via_arbno_fence`,
`146_pat_fence_alt_with_capture`, `152_pat_json_keyvalue_renamed`, `word4`.

## ⚠ Upstream interaction (NOT my patch) — needs attention next session

While this session was running, three concurrent upstream commits landed:

- `f387a7b9` IBB ground-zero: hello.icn passes mode 4 (first ever) — introduced
  `bb_lit_scalar.cpp` with a **fake-jmp placeholder BINARY arm**, breaking
  `audit_m3_native_binary_arms.sh` (GATE OK → GATE FAIL). Pre-existing on the
  rebased tree at rebase point, not caused by my patch.
- `9b0e9fd3` IBB mode-3 native for Icon.
- `f2c4058e` IBB mode-3 ground zero: ABORT every unfilled MEDIUM_BINARY arm.
  **This change masks my +8 with 8 different SNOBOL4 driver regressions** (see
  below). Per-language ground-zero is reasonable strategy, but it's
  language-mixing: an Icon ground-zero discipline now ABORTs SNOBOL4 patterns
  that were previously silent EMPTY-arm passthrough (i.e. the binary arm was
  empty bytes, the TEXT arm ran fine, mode 3 native fell back to interp).

**The 8 SNOBOL4 driver programs broken by `f2c4058e`** (all were PASSing both
pristine pre-rebase AND after my +8 patch):
- `ShiftReduce_driver`
- `assign_driver`
- `fence_driver`
- `global_driver`
- `match_driver`
- `stack_driver`
- `trace_driver`
- `tree_driver`

Mode 3 native dropped 165 → 142 (−23) on the same rebase — the ABORT now fires
on the unfilled BINARY arms that the SBL track was scheduled to fill one-at-a-
time (SBL-SPAN-2 / SBL-ARBNO-3 / SBL-BREAKX-2). Net: pre-existing-known-empty
arms now ABORT instead of fall-through to interp.

**Recommended remediation (next session, NOT urgent):**
1. Either teach `f2c4058e`'s ABORT to be SNOBOL4-aware — only ABORT on Icon
   templates while SBL track finishes filling its remaining BINARY arms — or
2. Accelerate the SBL BINARY-arm-fill rungs (SPAN-2 / ARBNO-3 / BREAKX-2) so
   mode-3 native climbs above the new ABORT floor.

Option (1) is the surgical short-term move; option (2) is the eventual
end-state. The GOAL doc's existing rung ordering (SPAN-2 → ARBNO-3 → BREAKX-2
via the `std::deque<int>` slot-pair pattern) already covers this — `f2c4058e`
just makes the priority more visible.

**Audit GATE FAIL is `bb_lit_scalar.cpp` only** (Icon, NOT SNOBOL4). Quick fix:
`bomb_bytes("bb_lit_scalar: not yet implemented in mode-3 BINARY")` in the
MEDIUM_BINARY arm to make it honest. Out of scope for an SBL-track session
since the file is Icon's.

## Next session — recommended priority order

1. **Land the cosmetic `lower_pat_dcg.c:484/498` simplification** (`bb->sval =
   pp->STRVAL_fn ? pp->STRVAL_fn : ""`). Behavior-identical with current
   routing; lays clean baseline for the next item.

2. **Write `patnd_to_bb_tree(PATND_t *)` in `lower_pat_dcg.c`** — parallel to
   `patnd_to_bb_graph`, builds emit_sm.c-shaped trees. Key constraints learned
   while preparing this work:
   - `pat_set_children` is `static` in `emit_sm.c:545`. Lift it to a shared
     header (or duplicate; same `bb_pat_kids_state_t` struct definition).
   - `lower_flat_invariant` at `emit_sm.c:582` **requires `bb_pat_nkids(nd) <=
     2` for `BB_PAT_CAT` nodes**. The tree builder MUST left-fold n-ary XCAT
     into a binary CAT chain: `CAT(CAT(CAT(a,b),c),d)`. Same constraint should
     be applied to ALT for safety. The existing γ-chain `build_patnd::XCAT`
     at `lower_pat_dcg.c:420` handles n-ary via chain entries and CANNOT just
     be copied — needs the explicit binary fold.
   - The label arena `744ae342` is in tree; `flat_drive_*` already migrated
     off `alloca` to `emit_label_alloc`. Prerequisite #2 (dangling label
     storage) from the prior session is fully closed.

3. **Dispatch decision in `patnd_needs_xlate`** — option (a) safe-surgical:
   keep two builders, dispatch on `g_bb_mode` (mode-3 uses tree, mode-2 keeps
   γ-chain). Option (b) eventual unification: teach `bb_exec.c::case
   BB_PAT_CAT/ALT` to read tree-shape via `bb_pat_kids_state_t`. Start with
   (a) — last attempt under (a) only had the dangling-label bug, which is
   now closed.

4. **Validate on the two known-good probes:**
   - `050_pat_alt_two` (expected `dog`) under `--run SCRIP_M3_NATIVE=1`
   - `055_pat_concat_seq` (expected `ab cd ef`) under `--run SCRIP_M3_NATIVE=1`
   Both produced correct output under the failed prior attempt (proving
   SBL-EP-BINARY combinator arms work) — re-confirm.

5. **Address the upstream ABORT interaction.** Once `patnd_to_bb_tree` lands,
   re-measure native corpus — many of the 23-dropped mode-3 programs may
   recover once combinator flat-wire routes through filled BINARY arms.

## Architecture notes that emerged this session

- `NV_PTR_fn` (`snobol4.c:2546`) ALWAYS creates a cell on first lookup
  (line 2566-2571). So `NAME_fn(varname)` at line 2634 ALWAYS returns a
  NAMEPTR (cell-ptr in `.ptr`, `.slen=1`), never a NAMEVAL — except for the
  keyword bypass list (STLIMIT, ANCHOR, INPUT, OUTPUT, etc) that returns
  `NAMEVAL(GC_strdup(varname))` directly. This is why the bug was specifically
  about NAMEPTR — virtually every user variable goes through that path.

- `NV_name_from_ptr` (`snobol4.c:2574`) is O(VAR_BUCKETS × chain_len). Cheap
  in practice; called once per `pat_assign_imm/cond` at pattern construction,
  not on each match attempt.

- The cosmetic `lower_pat_dcg.c` cleanup is deferred deliberately — it would
  remove the visible reminder of the bug being closed at construction. Next
  session can decide whether to keep the defensive read as documentation or
  collapse it.

## Verify-before-handoff checklist (all confirmed at HEAD `48409299`)

```bash
bash scripts/build_scrip.sh                            # OK
make libscrip_rt                                       # Built
bash scripts/test_smoke_snobol4.sh                     # 13/13 ✅
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh   # 13/13 ✅
bash scripts/test_snobol4_pat_rung_suite.sh            # M2=19/19 ✅ (M4=14/19, see upstream note)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" \
  | grep -v "_templates/" | grep -v emit_core.c | wc -l   # FACT 0 ✅
# audit_m3_native_binary_arms.sh GATE FAIL (bb_lit_scalar.cpp, upstream f387a7b9)
```

## Session totals (this session only — SNOBOL4 patch in isolation)

| Metric | Pristine | After SBL-XNME-VARNAME (pre-rebase) | Δ attributable to my patch |
|---|---|---|---|
| Mode 2 broad corpus | 237/280 | 245/280 | **+8 ZERO regressions** |
| Mode 3 native broad corpus | 165/280 | 165/280 | 0 (behavior-neutral, as predicted) |
| Pattern rung suite M2 | 19/19 | 19/19 | 0 |
| GATE-1 default + native | 13/13 + 13/13 | 13/13 + 13/13 | 0 |
| audit_m3_native_binary_arms | GATE OK | GATE OK | 0 |
| FACT RULE compliance | 0 | 0 | 0 |
| Commits to one4all | — | 1 (`48409299`) | — |
| Commits to .github | — | 1 (this handoff) | — |

## Files touched

- `src/runtime/snobol4/snobol4_pattern.c` (+14 lines, 1 helper + 2 callers)
- `.github/HANDOFF-2026-05-28-OPUS-SBL-XNME-VARNAME.md` (this file)

No other files modified.
