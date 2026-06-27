# HANDOFF — 2026-06-27 — Claude Sonnet 4.6 — ICON-BB: every (A & B) conjunction-filter generators

**SCRIP HEAD:** `654f720`
**Suite:** PASS=209 FAIL=43 EXCISED=1 (289 total) — both m3 and m4, FAIL sets byte-identical.
**Delta vs baseline (`cbbf24d`):** +1/−1 (rung13_alt_alt_filter GAINED, zero regressions, no swaps).

---

## What was fixed

`every (A & B)` conjunction-filter generators now enumerate all results.

**Repro:** `every (x := (1|2|3|4|5)) > 2 & write(x)` → was `3`, now `3 4 5`.
**Also fixed:** 3+-element conjunctions `every A & B & C` (was m3/m4 asymmetric, m4 looped; now both modes correct).

---

## Root cause

`every A & B` parses as `every (A & B)` — an `IR_EVERY` driving a monolithic `IR_CONJ`.
In `lower_every` (lower_icon.c), the no-BODY path does:

```c
IR_t * loop_target = (gen_node && gen_node != gen_result && gen_node != ω && gen_node != E) ? gen_node : E;
```

The conjunction reported `cx->beta == E` (its rightmost element `write` is non-resumable), so `gen_node` collapsed to `gen_result` (CONJ), and `loop_target` collapsed to `E`. The buried generator (ALT, reachable via the relop's `ω`) was never re-driven. EVERY looped back to itself (E) on each completion of `write`, getting the same first-passing value forever.

The `do` form (`every (x:=(ALT))>2 do write(x)`) already worked because the BODY path uses `gen_node = loop_back` set by the separate BODY lower call; it was only the no-BODY (bare conjunction) path that collapsed.

---

## The fix — two surgical changes, +11/−9 total

### Fix 1 — `src/lower/lower_icon.c` (+10/−9)

Added field `IR_t * conj_resumable;` to `icx_t` struct.

In both conjunction-lowering branches (`TT_SEQ_EXPR` and the default `TT_SEQ`):
```c
// Track rightmost resumable element's β (additive — never touches cx->beta)
IR_t * rb = NULL;
for (int i = k-1; i >= 0; i--) {
    ...lower S[i]...
    if (!rb && is_resumable(S[i])) rb = cx->beta;
    ...
}
cx->conj_resumable = rb;
```

In `lower_every`, reset `cx->conj_resumable = NULL` before lowering GEN, capture `conj_rb` after, and use it as fallback:
```c
IR_t * conj_rb = cx->conj_resumable;
if (!BODY) {
    IR_t * loop_target = (gen_node && gen_node != gen_result && gen_node != ω && gen_node != E)
        ? gen_node
        : ((conj_rb && conj_rb != gen_result && conj_rb != ω && conj_rb != E) ? conj_rb : E);
    ...
}
```

**Why not touching `cx->beta`:** morning dead-end-2 tried changing `cx->beta` in the conjunction and passed the repro but regressed ~10 canary programs. `cx->beta` is read by many callers; `conj_resumable` is a new, scoped field read only by `lower_every`.

### Fix 2 — `src/emitter/emit_bb.c` (+1)

In `codegen_flat_chain_body`, ω-routing loop — after the `omega_resolved` lookup:
```c
// Binop-over-generator followthrough: consumer→IR_BINOP(non-gen)→generator → route to generator's β
if (omega_resolved && omega_k >= 0 && i > omega_k
    && !ir_is_generator_kind(nodes[omega_k]->op) && nodes[omega_k]->op == IR_BINOP) {
    IR_t *bw = nodes[omega_k]->ω.node;
    if (bw) for (int g = 0; g < n; g++)
        if (nodes[g] == bw && ir_is_generator_kind(nodes[g]->op) && i > g)
            { node_ω = betas[g]; break; }
}
```

For 3+-element conjunctions (`A & B & C`), the middle relop `B` has `ω→A` (also a binop, non-gen). Without this, the chain walker routed `C`'s loopback to `A`'s α, recomputing `A` fresh with the same value — infinite loop in m4. This routes through to the ALT's β instead.

---

## Validation

- **Rigorous baseline FAIL-set diff:** stash → rebuild baseline → capture FAIL list → restore → diff.
  Result: exactly **one gain** (`rung13_alt_alt_filter`), **zero regressions**, **no swaps**.
- Full suite 209/43/1 **both m3 and m4**, FAIL sets byte-identical (perfect m3/m4 symmetry).
- 15-program canary set (rung02_arith_gen_*, rung01_paper_*, rung36_jcon_primes, rung10_augop_break_repeat, rung02_proc_locals) green both modes.
- Robustness sweep: 2-element, 3-element, larger ranges, `to`-generators, alt-generators, post-filter arithmetic — all correct both modes.
- Icon smoke 12/12 both modes · Prolog 5/5 · SNOBOL4 7/7 · all 4 icn discipline gates green.
- Bench-asm: `updated=0` — fix alters no compiling bench program's assembly.
- Rebased cleanly on Jeffrey's concurrent SNOBOL4 push (`795eaef`).

---

## IR shape reference (for next session)

**Passing case (relfilter, `every write((1 to 6) > 3)`):**
- write.ω → EVERY (not back into relop) — `every` resumption works via E's own loop
- No conjunction involved; this shape was always correct

**Fixed case (alt_alt_filter, `every (x:=(1|2|3|4|5)) > 2 & write(x)`):**
```
IR_CONJ [write]
  ← relop (BINOP) .ω → ALT   ← this is conj_resumable
    ← ALT [lit1 lit2 lit3 lit4 lit5]
  ← write (CALL)
IR_EVERY [gen_entry]
```

---

## What did NOT flip and why

**`rung13_alt_alt_cross_arg_sideeffect`** (`every write(1|2, noisy(), 3|4)`) — a different, harder subsystem. IR:
```
IR_EVERY → write (CALL) with 3 args:
  arg0: IR_ALT [1, 2]           ← generator
  arg1: IR_CALL noisy()         ← once-only, single-shot
  arg2: IR_ALT [3, 4]           ← generator
```
Failure is two-fold:
1. The single-shot middle arg's value is dropped — shows `13` not `1X3`
2. `noisy()` is re-evaluated each resume (shows `[eval]` once per digit pair, should be once total)

This is call-argument-evaluation machinery. The fix lives in how `bb_call.cpp` handles mixed generator/non-generator args — it needs to memoize once-only args across the cartesian product resumption. Not a conjunction problem.

**Suggested entry for next session:** trace `bb_call.cpp` to find where generator-kind args trigger resumption vs once-only args, and how the arg-evaluation slot map is populated for calls where some args are `IR_ALT`-shaped and others are plain.

---

## Files touched

```
src/lower/lower_icon.c   +10/-9  (icx_t.conj_resumable field + conjunction tracking + lower_every fallback)
src/emitter/emit_bb.c    +1/+0   (chain-walker binop-over-generator ω-followthrough)
```

SCRIP commit `654f720`. `.github` watermark updated. Bench `.s` unchanged.
