# SESSION CLOSE: Icon BB — Records + bb_scan_any cset-var + bb_unop real-neg

**Date:** 2026-06-25
**Model:** Claude Sonnet 4.6
**SCRIP commit:** fa95344 (main)
**Corpus commit:** 51df0fc2 (main)
**Status:** COMPLETE — m3+m4 PASS=190 (was 186 apples-to-apples), zero regression
**Baseline:** m3/m4 PASS=186 (61bcc17, same counting method)

---

## Three permanent BB-march fixes

### Fix 1 — Records (rung24 ×5)

All five `rung24_records_*` programs now pass in m3 and m4.

**Root cause A — lowering bug** (`src/lower/lower_icon.c`):
`IR_FIELD_SET` was lowering its RHS *after* the object, so a generator RHS
(`IR_TO`) ended up downstream in the γ-chain — its slot was never filled when
the field-set emitted. Fixed: lower RHS first (entry=RHS head → object →
set), exactly mirroring the working `IR_ASSIGN` value-flow. This made
`every c.n := 1 to 3` work. The slot-strand was a genuine lowering bug
independent of the gate.

**Root cause B — gate gap** (`src/driver/scrip.c`):
`IR_TO`/`IR_TO_BY` not in `rhs_kind_ok`. Added. Verified codegen already
handles it (gated `every v := a to b` programs now also run).

**Diagnostic infrastructure**: `SCRIP_ICN_NOGATE=1` env flag added to
`graph_native_emittable_mode` — bypasses the gate for a full-corpus bomb map.
Inert unless set. Used to produce the real map of what's broken vs. hidden.

### Fix 2 — `bb_scan_any` cset-from-variable (rung06_cset_cset_var)

**Shape:** `vowels := 'aeiou'; "icon" ? write(any(vowels))` → `2`

**Root cause:** `bb_scan_any` only handled literal/keyword cset args. A cset
variable was `NULL` for `op_name1` → bomb. Wrong first attempt used
`rt_nv_cstr` (NV hash) — locals live in **frame slots**, not the NV hash.

**Fix:**
- `emit_bb.c`: `scan_cset_var_arg()` extracts the variable name from the arg
  subgraph; `bb_varslot_peek(name)` captures the slot offset into `op_sa`.
- `bb_scan_any.cpp`: new arm when `op_name1=NULL` and `op_sa>=0`: load the
  cset's `.s` pointer from `[r12+op_sa+8]` (the `.s` union member of `DESCR_t`
  at offset +8) and `strchr`-test membership. Same logic as the literal arm,
  just with a frame-slot load instead of a sealed `ROQ(0)` literal.
- `scrip.c`: `scan_any_cset_var_ok()` helper admits the var-cset case at the
  gate, scoped to `any()` only (not `many`/`upto` which don't have this arm).

### Fix 3 — `bb_unop` real-aware NEG/POS

**Shape:** `x := 3.5; write(-x)` was producing `-4615063718147915776` (raw
IEEE-754 bit pattern negated as integer) instead of `-3.5`.

**Root cause:** the NEG/POS fallthrough arm in `bb_unop` always loaded the
raw 8 bytes of the value half, integer-negated, and tagged `DT_I`. For
`DT_R` (real), this negated the bit pattern and mislabeled it as integer.

**Fix:**
- `arithmetic.c`: `rt_num_neg(DESCR_t a)` / `rt_num_pos(DESCR_t a)` —
  identical pattern to `rt_num_arith`: `IS_REAL_fn(a)` → negate/identity as
  double and return `REALVAL`; else integer path returns `INTVAL`. 10 lines.
- `bb_unop.cpp`: NEG/POS arm now passes the full DESCR (`rdi:rsi` = `op_sa` /
  `op_sa+8`) to `rt_num_neg`/`rt_num_pos`, stores `rax:rdx` to `op_off`.
  The old inline `neg rax` / `DT_I` tag is gone.

The `rung36_jcon_random` benchmark still bombs `bb_unop` with a *different*
sub-issue (`op_sa < 0` — a non-slot producer, related to `&random`
keyword-lvalue and record-arg tangling). That is a separate, unrelated gap.

---

## The gate-bypass workflow — why it matters

The session opened with a diagnosis of the gate (`graph_native_emittable_mode`).
Key findings:
- Running `SCRIP_ICN_NOGATE=1` against all 289 corpus programs gives the
  **real failure map**: PASS=193, WRONG=50, BOMB=12, CRASH=32, HANG=2 (vs.
  the gate's "EXCISE" which hides everything in a generic message).
- The 12 BOMs cluster into 5 box kinds: `bb_var` ×4 (function-as-value),
  `bb_alt` ×4 (non-literal arms), `bb_assign_local` ×2, `bb_unop` ×1,
  `bb_scan_any` ×1.
- The gate produced false negatives: `every v := 1 to 3` (purely a missing
  whitelist entry — one line fixed it) was rejected while the codegen was
  already correct.
- The gate also hid real bugs: the `IR_FIELD_SET` lowering strand was only
  exposed when the gate was bypassed.

The `SCRIP_ICN_NOGATE` flag is the right tool for the next session to continue
the BB march: bypass, get the bomb list, fix each box arm, verify m3==m4,
verify discipline gates, commit. Repeat.

---

## Remaining bomb map (post-this-session, gate bypassed)

| box | count | shape | notes |
|-----|------:|-------|-------|
| `bb_var` | 4 | builtin-as-first-class-value | `nargs(abs,...)` — `args()` introspection |
| `bb_alt` | 4 | non-literal alt arms | needs value-flow facility; deliberately deferred |
| `bb_assign_local` | 2 | descr flat-chain + rhs-slot | rung36_jcon_collate/concord |
| `bb_unop` | 1 | `op_sa<0` non-slot producer | rung36_jcon_random, &random lvalue tangle |

Feature ladder (rung01–35) not-passing (20 programs):
`rung06_cset_upto_basic`, `rung08_find_gen`, `rung08_strbuiltins_match`,
`rung13_alt_*` ×5, `rung15_real_swap_lconcat`, `rung16_seqexpr_gen_basic`,
`rung18_real_relop_real_relop_goal`, `rung23_table_table_key`,
`rung27_read_*` ×4, `rung30_builtins_misc_seq`, `rung35_block_body_*` ×2.

---

## Verification

| Metric | Result |
|--------|--------|
| m3 PASS (real gate) | **190** (was 186, +4) |
| m3 FAIL (real gate) | 99 (was 103) |
| m3==m4 on new features | ✅ records / cset-var / real-neg all verified |
| Icon smoke | ✅ 12/12 m3+m4 |
| no-stack gate | ✅ 0 |
| one-reg gate | ✅ 0 |
| semicolon prison | ✅ PASS |
| regression | ✅ zero |

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
