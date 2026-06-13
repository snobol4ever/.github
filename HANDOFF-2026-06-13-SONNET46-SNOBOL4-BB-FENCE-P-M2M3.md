# HANDOFF 2026-06-13 · Sonnet 4.6 · SNOBOL4-BB (full session)

**SCRIP HEAD:** 900fee0
**.github HEAD:** 84ab58a3 (updated by this commit)

---

## What this session did (3 code commits)

### 1. M3-CONCAT-MULTIPART — eb98b8e (pat-rung 055, 18/19 → 19/19)

`bb_gvar_assign_concat.cpp`: the `lea rdi` BINARY arm baked the wrong ptr as
the destination variable name in both arms.

- `lit_s` arm used `_.op_sval` — **NULL** for `IR_ASSIGN_CONCAT` (never set by
  `flat_drive_gvar_assign`). BINARY baked `movabs rdi, 0`.
- multi-part arm used `_.bb_ls` — the scratch label-name buffer, not the var
  name. BINARY baked the address of the scratch char array.

Fix: both → `IR_LIT(_.node).sval` (permanent IR destination-variable-name ptr).
TEXT arm byte-identical (reads `_.bb_ls` as an assembler label). Pat-rung went
M3 18/19 → 19/19; full m2/m3/m4 19/19/19 no-SKIP parity achieved.

### 2. M4-SMOKE-REGRESS — verified stale, closed (no code change)

Both halves resolved by this and the prior session. `bb_unify.cpp` dup label
`.Lx2_0` is gone (grep 0). `DEFINE('DOUBLE(N)') … OUTPUT=DOUBLE(21)` with
`< /dev/null` returns `42` in M3, M4, and sbl. Smoke 7/7/7 confirmed.

### 3. FENCE(P) function form — 900fee0 (M2/M3 +9 in fence family)

**Root cause:** `lower_snobol4.c` `case TT_FENCE` (the pattern-subgraph
builder, ~line 379) ignored `t->c[0]` (the sub-pattern P) and aliased `FENCE(P)`
to the nullary keyword `IR_PAT_FENCE`, discarding P entirely. So
`FENCE(LEN(1)|LEN(2))` produced a bare fence (matches null, P never matched).
All-mode bug — M2 oracle also wrong. Decisive proof:
`X='AB'; X POS(0) FENCE(LEN(2)) RPOS(0)` → SCRIP M2 "cursor at 0" / sbl
"cursor advanced 2".

**Fix (3 lines, pure-lowering, no matcher/template changes):**

SPITBOL identity (Ch.19 p.207): `FENCE(P)` = P, except P's alternatives are
visible only moving forward; backtracking *into* P seals them. That is exactly
**P concatenated with the keyword FENCE** (Ch.18 p.204: null match, fail on
retreat). The keyword `IR_PAT_FENCE` node already seals correctly in all three
modes — 058 proves it.

```c
    case TT_FENCE: {
        if (t->n > 0 && t->c[0]) {
            IR_t * seal = IR_node_alloc(pg, IR_PAT_FENCE); γ_to(seal, succ); ω_to(seal, fail);
            return lower_pat_node(pg, t->c[0], seal, fail); }
        IR_t * nd = IR_node_alloc(pg, IR_PAT_FENCE); γ_to(nd, succ); ω_to(nd, fail); return nd; }
```

**Verified (probe-first vs sbl throughout):**
- 100/101/103: 0/3 modes → correct in M2 and M3.
- Fence family 46 tests: M2 20→29, M3 21→30, **zero regressions** (stash-baseline
  sweep).
- Broad corpus: M2 172→181, M3 152→155.
- M4 emission **byte-identical** for non-FENCE(P) and keyword-fence programs
  (diff-proven via stash). M4 count delta in broad corpus = container/SKIP noise.
- Gates at 900fee0: smoke 7/7/7 HARD · pat-rung m2/m3/m4 19/19/19 no-SKIP ·
  fence HARD.

---

## What remains: M4-FENCE-P case B

The M4 (TEXT/assembly) path has a **separate, pre-existing** bug in how it
emits fence-in-concatenation backtracking. M2/M3/sbl are all correct; M4 is
wrong. This is NOT the new lowering (emission byte-identical pre/post for
non-FENCE(P) programs).

**Still failing M4-only after this session:**

| test | ref | M2 | M3 | M4 |
|------|-----|----|----|-----|
| 062 `('a'\|'b') FENCE('x')` | outer alt worked | ✅ | ✅ | ❌ failed |
| 100 `POS(0) FENCE(LEN(1)\|LEN(2)) LEN(1) RPOS(0)` | matched first alt then continued | ✅ | ✅ | ❌ unexpected fail |
| 101 `POS(0) FENCE('X'\|LEN(2)) RPOS(0)` | second alt taken | ✅ | ✅ | ❌ unexpected fail |
| 103 `POS(0) 'a' FENCE('X'\|'XY') 'b' RPOS(0)` | a-X-b matched | ✅ | ✅ | ❌ unexpected fail |

**Key diagnostic fact:** 058 (`LEN(1) FENCE LEN(2)` — keyword alone) passes M4.
So the bug is specifically the fence seal node **with live alternatives or
continuation** around it on the TEXT arm, not the seal node in isolation.

**Where to look:** `emit_bb.c:366` `flat_drive_fence` and `emit_bb.c:279`
`flat_drive_cat_arms` — the TEXT-arm β back-wiring. The M3 BINARY path for
these tests is correct; compare `--compile` (TEXT) asm output of test 100 vs the
correct BINARY execution to find where the TEXT β-wire diverges. The relevant
BB template is `bb_match_fence.cpp` (correct; does not need changes) — the fault
is in the *driver* that wraps it inside a concatenation or alternation context.

**Suggested first probe for next session:**

```bash
cd SCRIP
# Dump TEXT asm for test 100 (fence with two alts + continuation)
./scrip --compile corpus/crosscheck/patterns/100_pat_fence_two_alts_first.sno > /tmp/100.s
# Run under M3 with tracing if available to see which branch fires
./scrip --run corpus/crosscheck/patterns/100_pat_fence_two_alts_first.sno < /dev/null
# Look at flat_drive_fence in emit_bb.c — how does it emit the ω/β arms on TEXT path
# vs the BINARY (runtime) arm? The TEXT path must emit the seal's ω as an asm label
# that the outer cat-arm β target also reaches correctly.
sed -n '366,430p' src/emitter/emit_bb.c
```

---

## Gates at session end (900fee0)

- smoke: **7/7/7 HARD** ✓
- pat-rung: **m2 19/19 · m3 19/19 · m4 19/19 no-SKIP** ✓
- fence (test_gate_sno_pat_reg): **HARD** ✓ (TIER 1 + TIER 2 both 0)
- no_bb_bin_t: **0** ✓
- Broad corpus THIS CONTAINER: M2=181 · M3=155 · M4=145 SKIP=27
  (container-sensitive — stash-baseline before treating as regression)

---

## Session corpus net (this container, from session start)

| mode | start | end | Δ |
|------|-------|-----|---|
| M2   | 172   | 181 | +9 |
| M3   | 144   | 155 | +11 |
| M4   | 148   | 145\* | ±0\* |

\*M4 byte-identical for unchanged constructs; Δ is SKIP-count noise (10→27).
