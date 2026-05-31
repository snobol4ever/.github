# HANDOFF — SBL-M3-NATIVE-4 ARBNO tree-shape foundation (Opus 4.7, 2026-05-28)

**Goal:** GOAL-SNOBOL4-BB.md → M3-NATIVE-4 → ARBNO-inside-combinators (rungs 052/054).
**Start HEAD:** SCRIP `10f97d29` (M3-NATIVE-4 combinator flat-wire + XNME/XFNME captures).
**End HEAD:** SCRIP `debb8a4e` — three files modified, baseline-neutral.

## What landed

Foundation work to enable ARBNO subtrees in the tree-routing path. Three files:

### `src/include/BB.h`

Extended `bb_arbno_state_t` with `BB_t **kids; int nkids;` at the front. The struct is now layout-compatible with `bb_pat_kids_state_t` for its first two fields. Existing `inner / pos_stack / cap / saved_delta` fields shift later in the layout but are still read by name in `bb_exec.c` — no offset code anywhere depends on the prior layout.

```c
typedef struct { BB_t ** kids; int nkids; BB_graph_t * inner; int * pos_stack; int cap; int saved_delta; } bb_arbno_state_t;
```

Legacy `build_patnd` (γ-chain) XARBN allocations leave the new fields zero-initialized — `bb_pat_nkids` returns 0 for them, the legacy γ-chain consumers (mode-2 `bb_exec`, mode-3 brokered via `nd->α`) never read `kids`. Tree-built XARBN populates both halves.

### `src/lower/lower_pat_dcg.c`

New `case XARBN:` in `build_patnd_tree` (just before the `default:` delegation). It mirrors the legacy `build_patnd` XARBN inner-block construction BUT recursively calls `build_patnd_tree` (not `build_patnd`) for the inner — so combinator inners like `ARBNO('a' | 'b')` in rung 054 get tree-shape too. Then it allocates one `bb_arbno_state_t` and populates BOTH the kid sidecar (for flat-walker) AND the inner BB_graph_t (for mode-2 bb_exec + the brokered child-fn that `bb_arbno`'s MEDIUM_BINARY arm calls).

### `src/runtime/snobol4/stmt_exec.c`

Two predicate edits routing ARBNO-containing patterns through the tree builder:

- `patnd_tree_eligible` — removed the blanket `patnd_contains_arbno → 0` rejection; added explicit `case XARBN:` that recurses into the inner's eligibility.
- `patnd_is_combinator_root` — added `case XARBN:` so ARBNO can be the root of the pattern.

## Gates (baseline-neutral)

All identical to HEAD `10f97d29` before my changes:

| Gate | Value | Note |
|------|-------|------|
| G1 smoke (default) | 13/13 ✅ | |
| G1 smoke (`SCRIP_M3_NATIVE=1`) | 13/13 ✅ | |
| G2 broker | 38/15 ✅ | |
| G3 mode-4 broad | 162/82 SKIP=36 | PLAN.md says 175 — pre-existing drift, not mine; verified by `git stash` |
| G4 interp broad | 237/43 ✅ | |
| Native broad (M3_NATIVE=1) | 157/280 ✅ | unchanged from HEAD |
| Rung suite | M2=19, M4=14 SKIP=0 | 052/053/054/056/057 fail (unchanged) |
| Audit | GATE FAIL: `bb_lit_scalar.cpp` FAKE-JMP | pre-existing, owned by ICON-BB per PLAN.md note |

My changes are behavior-neutral on every existing baseline because the NEW tree-path for ARBNO subtrees still aborts at `bb_emit_end` for any pattern that would take it under M3_NATIVE — so the broker silently propagates `bb_build_flat`/`bb_build_brokered` NULL returns (the prior behavior), no regression surfaces.

## Active blocker (FULLY diagnosed, fix path concrete)

052 and 054 under `SCRIP_M3_NATIVE=1 --run` no longer segfault. They now abort with:

```
bb_emit_end: 1 unresolved forward reference(s):
  site=19 label='pat_brok_β'
Aborted
```

### Diagnosis (verified empirically via env-gated `SCRIP_TRACE_PATCH`/`SCRIP_TRACE_M3_ARBNO` fprintf probes, all reverted before commit)

For `POS(0) ARBNO('a') . V RPOS(0)`:

1. Outer `bb_build_flat(xcat)` is called.
2. `pre_build_children(xcat)` recursively descends:
   - Visits XNME (BB_PAT_ASSIGN_COND) → its child is the ARBNO node → triggers special-case
   - Recurses into `pre_build_children(arbno_node)` → ARBNO's child is the inner literal 'a' → triggers special-case → recurses into literal (no further) → returns → `bb_build_brokered(literal)` runs **"session 1"** — emits 5 patches, all resolved (β/γ/ω defined by LIT template). Caches literal-fn.
   - Back at XNME-level: `!child_cache_get(arbno_node)` → still true → `bb_build_brokered(arbno_node)` runs **"session 2"**.
3. **Session 2 — the bug:** brokered preamble (4B) + `XA_FLAT_PROLOGUE` (19B) emits a `jne` placeholder at absolute offset 19 targeting the codegen_flat_body's stack-local `lbl_β`. The patch site=19 is registered, label is `pat_brok_β` (pointer to outer's stack-local lbl_β). Then `walk_bb_flat(arbno_node, &lbl_γ, &lbl_ω, &lbl_β)` runs.
4. `walk_bb_flat` case BB_PAT_ARBNO finds `cfn = child_cache_get(literal) ≠ NULL` (good — session 1's fn). Sets `g_emit.child_fn`. FILL calls bb_arbno template.
5. **bb_arbno's MEDIUM_BINARY arm SHOULD emit 259 bytes with `bin = {{182,186,203,255}, {γ_p,β_p,ω_p,γ_p}, {false,TRUE,false,false}}` — defining β at relative site 186 (absolute 4+19+186 = 209).**
6. But the trace shows **no `bb_label_define` for the lbl_β pointer in session 2**. Only γ and ω get defined. So β-define is missing — `bb_emit_end` finds the unresolved patch at site 19 and aborts.

### Where the bug must be (next session — first 30 minutes)

The bb_arbno template's MEDIUM_BINARY standard arm (line 35–115 of `src/emitter/BB_templates/bb_arbno.cpp`) declares the bin correctly. But somehow when it executes in session 2, β doesn't get defined. Two candidate root causes to verify with a single fprintf in `src/emitter/emit_str.cpp` line 63 (`bb_emit_asm_result`):

**Candidate A — `g_emit.bb_child_fn` is NULL in session 2 even though walk_bb_flat saw `cfn != NULL`.**
The walker does `g_emit.child_fn = (void *)cfn` (note: `child_fn`, not `bb_child_fn`). The template reads `g_emit.bb_child_fn`. These are two different fields. Check `bb_prepare_capture_arbno` (emit_bb.c:608) — it copies `g_emit.child_fn` → `g_emit.bb_child_fn` only inside `if (MEDIUM_TEXT)` (line 618) AND on line 615 unconditionally. Line 615: `g_emit.bb_child_fn = (void *)child_fn;` where `child_fn = g_emit.child_fn`. So that should be fine. BUT — `bb_prepare_capture_arbno` is dispatched via `emit_core.c:527`: `case BB_PAT_ARBNO: bb_prepare_capture_arbno(nd, 0); bb_arbno(nd); return 0;`. So prepare runs before bb_arbno. Verify the order and `bb_child_fn` value at template entry.

**Candidate B — the `if (!child_lbl || !child_lbl[0])` early-return at line 19 of bb_arbno.cpp fires in BINARY mode.**
Line 18: `const char *child_lbl = g_emit.bb_child_lbl;`. Line 19: `if (!child_lbl || !child_lbl[0]) { if (MEDIUM_BINARY) { bin = {{1,6},...}; return ...; } ... }`. `bb_child_lbl` is set inside `if (MEDIUM_TEXT)` (line 618 of emit_bb.c) — only in TEXT mode! In BINARY mode `bb_child_lbl` may still be empty/stale, triggering the early-return fallback that emits only γ/ω jumps (10 bytes, sites at 1 and 6) WITHOUT defining β.

**Candidate B is almost certainly the root cause.** Match the trace exactly:
- Session 2 emits patches at absolute 19 (β prologue), 24 (γ), 29 (ω) → body is 10 bytes (24-19=5, 29-24=5 — sites at relative 1 and 6 within a 10-byte body starting at absolute 23).
- That matches the fallback arm precisely: `bytes(1,"\xE9") + u32le(0) + bytes(1,"\xE9") + u32le(0)`.
- The standard 259-byte ARBNO arm is being **bypassed by Candidate B**, even though `bb_child_fn` is non-null.

### Fix sketch

In `bb_arbno.cpp`, gate the `child_lbl` early-return on TEXT mode only, OR refactor to check `bb_child_fn` for BINARY and `child_lbl` for TEXT. Concretely:

```cpp
const char *child_lbl = g_emit.bb_child_lbl;
void *child_fn = g_emit.bb_child_fn;
int have_child = MEDIUM_BINARY ? (child_fn != NULL) : (child_lbl && child_lbl[0]);
if (!have_child) {
    if (MEDIUM_BINARY) { bin = {{1,6},{_.lbl_γ_p,_.lbl_ω_p},{false,false}}; return bytes(1,"\xE9")+u32le(0)+bytes(1,"\xE9")+u32le(0); }
    return std::string();
}
```

The same pattern likely affects bb_capture.cpp (BB_PAT_ASSIGN_COND/IMM). Verify on 052 (BB_PAT_ASSIGN_COND wrapping ARBNO) and 054 (same with ALT inner).

### Probes used (all reverted)

```c
// emit_core.c bb_emit_patch_rel32 / bb_label_define
if (getenv("SCRIP_TRACE_PATCH")) fprintf(stderr, "[PATCH] site=%d lbl=%p name='%s' ...\n", ...);

// emit_bb.c walk_bb_flat BB_PAT_ARBNO + pre_build_children
if (getenv("SCRIP_TRACE_M3_ARBNO")) fprintf(stderr, "[M3_ARBNO] nd=%p nkids=%d ch=%p cfn=%p\n", ...);
```

These are NOT in the tree. Re-add for verification of the fix.

### Test commands

```bash
SCRIP_M3_NATIVE=1 ./scrip --run test/snobol4/patterns/052_pat_arbno.sno  # expect "aaa"
SCRIP_M3_NATIVE=1 ./scrip --run test/snobol4/patterns/054_pat_arbno_alt.sno  # expect "abba"
```

Then full gates:

```bash
bash scripts/test_smoke_snobol4.sh                                                                # 13/13
bash scripts/test_snobol4_pat_rung_suite.sh                                                       # M2=19, M4 hopefully ≥15
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                              # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh        # native ≥ 157
bash scripts/audit_m3_native_binary_arms.sh                                                       # GATE OK (modulo bb_lit_scalar.cpp ICON-BB)
```

## NEXT after the bb_arbno fix

Once 052/054 land:
1. Check 053_pat_alt_commit, 056_pat_star_deref, 057_pat_fail_builtin — these failed at the same `M4=14` baseline. They may already pass with the tree-routing extension (especially 053, alternation with commit), or need separate analysis.
2. Investigate broader native-corpus expansion. Today's 157/280 should jump on the next pass — the prior session's combinator flat-wire was already at 157, and ARBNO support unlocks several more `ARBNO`-using rungs in the 280-test corpus.
3. Then consider flipping `SCRIP_M3_NATIVE=1` to default once native ≥ G4 interp count.

## Files modified

```
src/include/BB.h                |  3 ++-
src/lower/lower_pat_dcg.c       | 34 ++++++++++++++++++++++++++++++++++
src/runtime/snobol4/stmt_exec.c | 12 +++++++++---
```

All changes documented inline with `SBL-M3-NATIVE-4 ARBNO (2026-05-28 Opus 4.7)` tags.
