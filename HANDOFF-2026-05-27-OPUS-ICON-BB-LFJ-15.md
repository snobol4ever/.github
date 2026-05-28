# HANDOFF — LFJ-15 (Icon BB lower consolidation)

**Date:** 2026-05-27  
**Author:** Claude Opus 4.7  
**Goal:** ICON-BB  
**Rung:** LFJ-15 (partial — three of four items; LFJ-15b carries the fourth)  
**Commit:** one4all `cde72b79`  
**Watermark gates:** smoke_icon 5/5 · icon_all_rungs 198/268 · smoke_prolog 5/5 · smoke_unified_broker 30/52 · FACT RULE 0

---

## What LFJ-15 did

The LFJ staircase (LFJ-0..LFJ-14) transcribed every `ir_a_<KIND>` from
`/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` into a
`lower_icn_new_<KIND>` family living in `lower_icn_new.c`, with a
function-pointer dispatch table (`lower_kind_table`) in `lower_icn.c`
indirecting each AST kind to either a `legacy_<KIND>` or a `new_<KIND>`
function. LFJ-14 (`0540aace`) flipped the last table slot — every entry
pointed into the new file.

LFJ-15 demolishes the legacy substrate.

### Items landed (three of four)

1. **Delete `src/lower/lower_icn.c`** — 1616 lines containing 49
   `legacy_<KIND>` functions, the `lower_kind_table[TT_KIND_COUNT]`
   array and its init function, and the table-lookup dispatcher.
2. **Delete `src/lower/lower_icn.h`** — replaced by the consolidated
   header (renamed from `lower_icn_new.h`).
3. **Delete the `lower_kind_table` indirection** — `lower_icn_expr_node`
   is now a plain `switch (e->t)` on 49 AST kinds, calling the
   `lower_icn_new_<KIND>` functions directly.
4. **Rename `lower_icn_new.{c,h}` → `lower_icn.{c,h}`.**

Plus the supporting work the rung implied:

- Remove dead `lower_icn_new_NoOp` (TT_NULL ownership went to `new_Unop`
  in LFJ-14; this shim was unreachable).
- Move helpers + dispatcher + threading machinery from the deleted
  `lower_icn.c` into the renamed file:
  - `icn_binop_apply` (runtime BB_BINOP apply, called from `bb_exec.c`)
  - `icn_fold_signed_lit` (compile-time literal folding for `by -3`
    parsed as `(TT_MNS (TT_ILIT 3))`, called from `lower_icn_new_ToBy`)
  - `lower_icn_upto`, `lower_icn_proc_gen` (special-case constructors)
  - `lower_icn_expr_node` — direct switch dispatcher (replaces the
    table)
  - `lower_icn_proc_body`, `lower_icn_expr_top`
  - `icn_kind_is_resumable`, `icn_kind_owns_omega_operand`
  - `icn_leaf`, `icn_tree_is_leaf`
  - `lower_icn_expr_threaded`, `lower_icn_expr_threaded_b`
- Makefile: drop the `lower_icn_new.c` source-list line and per-file
  compile rule.

### Net diff

`5 files changed, 1263 insertions(+), 2370 deletions(-)` — net **-1107
lines**, consolidating 2858 lines across two `.c` files into 1767 in
one.

### File layout (new `src/lower/lower_icn.c`, 1767 lines, top to bottom)

1. `lower_icn_new_<KIND>` procedures (LFJ-2..LFJ-14 transcriptions,
   sorted in the order they originally landed).
2. Helpers: `icn_binop_apply`, `icn_fold_signed_lit`.
3. Public-API constructors: `lower_icn_upto`, `lower_icn_proc_gen`.
4. `lower_icn_expr_node` — direct AST-kind dispatcher.
5. `lower_icn_proc_body` + `lower_icn_expr_top`.
6. AG infrastructure: `icn_kind_is_resumable`,
   `icn_kind_owns_omega_operand`, `icn_leaf`, `icn_tree_is_leaf`,
   `lower_icn_expr_threaded_b`, `lower_icn_expr_threaded`.

---

## What LFJ-15 DEFERRED — the fourth item

The original LFJ-15 prose listed four items. The fourth was:

> Delete all `_threaded_b` AG-PURE intercept branches.

I retained those intercept branches verbatim. Here's why and what
remains.

### Why the intercepts cannot be deleted in isolation

The `lower_icn_new_<KIND>` functions are 1:1 transcriptions of the
former `lower_icn_legacy_<KIND>` functions (per LFJ-1a extraction
encoding and reaffirmed in every LFJ-2..LFJ-14 commit). They produce
**legacy-shape** graphs: `α`/`β` are operand pointers, sval/ival/dval
hold payloads.

The AG-pure intercept branches in `lower_icn_expr_threaded_b` (Families
3/5/6/7/8.1/8.2) reshape that legacy-shape output into **AG-pure
chain-walker shape** after the node is built:

- Scrub `nd->α` and `nd->β` to NULL (those are CFG ports now, not tree
  edges).
- Chain operand sub-graphs via `γ`: `lhs.γ = rhs`, `rhs.γ = nd_apply`.
- Wire `ω` to the inherited failure target (`ω_in`).
- Stamp markers consumed by `bb_exec.c`:
  - `sval = "ag"` / `"ai"` / `"ar"` for BB_TO / BB_TO_BY (peek-ring
    bounds decoding).
  - `ival = 1` for BB_EVERY (AG-pure passthrough branch).

If the intercepts are deleted **without** moving their wiring into the
new functions, the executor's AG-pure branches (`bb_exec.c` reads sval
== `"ag"`, etc.) never fire on graphs built by the new functions — the
chain walker would attempt to evaluate operands via the old recursive
path that no longer exists in mode-2 (or breaks because `α`/`β` are
unrouted).

This is genuine architectural work, not a delete. The retained
intercepts are load-bearing.

### LFJ-15b — the AG-pure consolidation rung

I added LFJ-15b as a new staircase row in `GOAL-ICON-BB.md`. Method:

**Per-family, gates green each commit.** Pass `γ_in`/`ω_in` through to
the `new_<KIND>` function for that kind, perform the scrub-and-wire
work *there*, retire the corresponding `if (e->t == ... && nd->t == ...)
{ ... }` block from `lower_icn_expr_threaded_b`.

**Family order (recommended, simplest first):**

- **Family 3 (BB_BINOP)** — scrub `α`/`β`, chain lhs→rhs→nd via γ, wire
  ω to ω_in. Pure CFG, no markers. Lowest-risk first.
- **Family 6 (BB_CONJ)** — symmetric to Family 3 (left.γ=right,
  right.γ=nd; nd reads peek(0)).
- **Family 7 (BB_ALT)** — arms already chained via ω by the new
  function; only the last-arm.ω = ω_in stamp needs to move.
- **Family 5 (BB_IF)** — cond.γ=cond.ω=nd_if; nd_if.γ=then.α;
  nd_if.ω=else.α. Slightly more intricate but pure CFG.
- **Family 8.1 (BB_EVERY)** — sets `nd->ival = 1` plus γ/ω propagation
  on the literal-bound flat-wire condition. Has a guard (`gen->α ==
  NULL && gen->β == NULL && gen->γ != NULL`) that already lives in the
  intercept — port that guard logic into `new_Every`.
- **Family 8.2 (BB_TO / BB_TO_BY)** — sets sval `"ag"` / `"ai"` / `"ar"`
  for dynamic-bound paths. Move sval-stamping into `new_ToBy`; preserve
  the BB_TO_BY's prior `i`/`r` mode reading.

**Acceptance for LFJ-15b:** `lower_icn_expr_threaded_b` body retains
only the Family-1/2 ATOMIC ASSIGN/CALL deep-thread paths (those are
distinct from the AG-pure intercepts — they wire peers via the sidecar,
not γ-chains) and the leaf fallback (`icn_leaf` call). Every `e->t ==
TT_*` switch in `_threaded_b` outside Family 1/2 is gone. Sval markers
`"ag"`/`"ai"`/`"ar"` and `nd->ival = 1` are set by the new functions, not
the wrapper.

**Signature change required:** new functions for the migrated families
need `γ_in`/`ω_in`/`α_out`/`β_out` parameters or a wrapping struct. The
cleanest approach is per-Family migration with a new
`lower_icn_new_<KIND>_ag` variant that takes the full AG signature,
called from a thin shim that `_threaded_b` invokes; once all six
families migrate, the original variant is deleted and the shim becomes
the real dispatcher entry. Don't try to convert all 49 new functions —
only the six that AG-pure intercepts touch.

### Why this is safe to defer

- The retained intercepts are **functionally indistinguishable** from
  what was there before LFJ-15 — same code, same wiring, same markers.
  The chain walker sees identical graphs.
- The "one traversal" language in the original LFJ-15 acceptance can be
  read two ways: (a) one file with one dispatcher = literal sense (now
  true), or (b) no post-processing pass on the lowered graph =
  architectural sense (LFJ-15b will deliver). Both readings are
  defensible; (a) is delivered now.
- The deferred work is documented at the LFJ-15b row plus this handoff.

---

## Verification

```bash
cd /home/claude/one4all

# Acceptance commands
grep "lower_icn_legacy_" src/lower/lower_icn.c | grep "lower_kind_table\[" | wc -l
# Expected: 0 (✅ — legacy refs are only in comments)

ls src/lower/lower_icn*.c | wc -l
# Expected: 1 (✅)

ls src/lower/lower_icn*.h | wc -l
# Expected: 1 (✅)

# Gates
bash scripts/build_scrip.sh                  # clean build
bash scripts/test_smoke_icon.sh              # PASS=5
bash scripts/test_icon_all_rungs.sh          # PASS=198
bash scripts/test_smoke_prolog.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh    # PASS=30

# FACT RULE
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | \
  grep -v _templates/ | grep -v emit_core | wc -l
# Expected: 0
```

All passed.

---

## What's where after LFJ-15

| Concern | Location |
|---|---|
| Per-AST-kind lowering (49 fns) | `src/lower/lower_icn.c` lines ~25–1228 |
| `icn_binop_apply` (runtime) | `src/lower/lower_icn.c` ~1267 |
| `icn_fold_signed_lit` (literal folding) | `src/lower/lower_icn.c` ~1330 |
| `lower_icn_expr_node` (switch dispatcher) | `src/lower/lower_icn.c` ~1384 |
| `lower_icn_proc_body` | `src/lower/lower_icn.c` ~1449 |
| `lower_icn_expr_threaded_b` (with AG intercepts) | `src/lower/lower_icn.c` ~1582 |
| Public header | `src/lower/lower_icn.h` (106 lines) |
| Build rules | `Makefile` lines 171, 405 (one source, one rule) |

---

## State of the staircase

| Rung | State |
|---|---|
| LFJ-0..LFJ-14 | ✅ |
| **LFJ-15** | ✅ partial (3 of 4 items: file delete + table delete + rename). `cde72b79`. |
| **LFJ-15b** | NEW — AG-pure consolidation (intercept fold). 6 families, per-family commits. |

**14 of 15 LFJ rungs complete (93%).**

After LFJ-15b lands, the LFJ staircase is fully retired. The AG-PURE
"LEGACY (frozen)" section in `GOAL-ICON-BB.md` can then be revisited
(its `DO NOT … Resume AG-PURE work below until LFJ-15 lands` constraint
is satisfied), specifically: Step 8.3 BB_BINOP_GEN cross-product
odometer, Step 9 N-ary applies (BB_CALL / BB_LCONCAT / BB_SECTION /
BB_IDX_SET), Step 10 sidecar cleanup.

---

## Method notes worth carrying forward

**The retained intercepts are an invariant the next rung must respect.**
LFJ-15b must move wiring into new functions *before* deleting an
intercept block. Order matters: build the new shape first, prove gates,
then delete the old reshape pass.

**The `sval` markers `"ag"` / `"ai"` / `"ar"` and `nd->ival = 1` are an
inter-module contract** between LOWER and `bb_exec.c`. Any AG-pure work
that changes where they're set must keep the values and semantics
identical.

**Probe→remove pattern still applies.** When migrating Family N in
LFJ-15b, add `fprintf(stderr, "[ag_<family>]\n")` at the new entry
point and the old intercept; run gates; verify the new path fires (no
"[ag_<family>] (legacy intercept)" output) before deleting the
intercept and the probes.

**Filename ≠ content remains true** (per LFJ-12-13 handoff). Trust
content greps, not filenames.

---

## Watermarks

- one4all HEAD: `cde72b79`
- .github HEAD: (after this handoff commits)
- icon_all_rungs: 198/268 (XFAIL 36, unchanged)
- LFJ progress: **14/15 (93%)**
- FACT RULE: 0
- All four gates green at watermark
