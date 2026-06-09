# HANDOFF — PLG-9j: mode-4 native `numbervars/3` + write/1 list-rendering fix

**Date:** 2026-06-01 · **Model:** Opus 4.8 · **Track:** GOAL-PROLOG-BB, mode-4 ladder
**Status:** COMPLETE, all gates green, landed. (Third rung this session, after PLG-9h + PLG-9i.)

## What shipped

`numbervars/3` now emits natively in mode-4, and the mode-4 write/1 list-rendering gap is closed.

**GATE-3 rung suite m4: 81 → 86 PASS** (0 FAIL, 30 → 25 EXCISED). Closed **all 5 rung20** numbervars
rungs: basic `f(A,B,A)/2`, list `[A,B,C]/3`, rollover `f(Z,A1)/27`, start_offset `f(D,E)/5`,
atom_unchanged `foo/0`. Byte-exact in all three modes.

## Two coupled pieces

### 1. numbervars/3 — another missed closure (same shape as PLG-9i)

mode-3 numbervars worked via the PLR-K-3 MEDIUM_BINARY arm + the helper `rt_pl_numbervars_term`
(bb_exec.c:886 — walks the term binding each `TERM_VAR` to `'$VAR'(N)` via unify, then unifies End=N),
but there was **no `@PLT` TEXT twin**, so the rich gate EXCISED it. The handoff's "term-mutation: mode-4
leaves vars unbound" was a stale observation; it was a missing twin, like copy_term/writeq.

Fix = a MEDIUM_TEXT twin of PLR-K-3 in `bb_builtin.cpp`: build a0 (the term) via
`emit_build_compound_term`, then `rt_pl_numbervars_term(t0=rdi, start=rsi, k2=edx, i2=rcx, s2=r8)`@PLT.
The var-cell aliasing works for free: the TEXT builder's `IR_LOGICVAR` path calls `rt_pl_node_to_term`,
which writes the fresh var back to `g_resolve_env[slot]`, so the helper binding those cells to `'$VAR'(N)`
mutates the very cells the later `write` rereads. Gate: `pl_rich_node_emittable` admits numbervars/3
(`α→γ→γ`).

### 2. write/1 list-rendering — a latent mode-4 gap (was blocking the 5th rung)

`rung20_numbervars_list` writes the list `[A,B,C]`. The mode-4 write/1 TEXT arm used the `emit_write_term`
inline walker, which renders an `IR_STRUCT '.'/2` generically as functor notation → `.(A,.(B,.(C,[])))`,
whereas the mode-2/3 oracle routes `TERM_COMPOUND` to `pl_write` (sugars cons-cells → `[A,B,C]`). This was
**latent**: write/1 admitted any arg and rendered lists wrong, but no passing rung hit it. Admitting
numbervars/3 would have turned the list rung into a FAIL.

Fix = route write/1's **compound** arg (`IR_STRUCT`/`IR_ARITH`) through `emit_build_compound_term` +
`rt_pl_write_term_ptr`@PLT (→ `pl_write`, the oracle's writer), mirroring the writeq TEXT twin and the
BINARY write arm. Since `pl_write` *is* the m2 oracle, m4 now matches m2 for all compounds:
`write([a,b,c])`→`[a,b,c]`, `write(1+2)`→`1+2` (operator form), `write(foo(a,b))`→`foo(a,b)`. The now-dead
`emit_write_term` (its only external caller removed) was deleted.

## Tier-dependent alignment — the one subtlety (cost a debug cycle)

Bare leaves and compounds enter the box at **different rsp alignments**:
- **flat tier** (bare int/float/atom/var args — admitted by the PLG-9b flat gate): **16-aligned** entry. A
  direct `@PLT` call is correct; a `sub rsp,8` *mis*-aligns it → fault.
- **rich tier** (compound args — flat gate rejects them): **8-misaligned** entry, so the compound path's
  `sub rsp,8` (which realigns to 16 across the build's + writer's calls) is correct.

So the leaves get **direct** writers with no rsp adjust: `IR_LIT_I` → `rt_pl_write_int`; `IR_LIT_F` →
`mov rax,<bits>; movq xmm0,rax; rt_pl_write_float` (also fixes bare-float write, previously a no-op —
`emit_build_compound_term` hard-codes xmm0=0 for leaves, so routing a float leaf through it would render
0.0). Only `IR_STRUCT`/`IR_ARITH` take the `sub rsp,8` + build + `pl_write` path. A first cut routed *all*
non-atom/var args through the compound path and segfaulted on `print(42)` (rung22) — the alignment split
is the fix.

## The two changed files (Prolog-arm-only, FACT-clean)

- **`src/emitter/BB_templates/bb_builtin.cpp`**: numbervars/3 MEDIUM_TEXT twin; write/1 arm split
  (IR_LIT_I/IR_LIT_F direct leaves + IR_STRUCT/IR_ARITH via `rt_pl_write_term_ptr`); removed dead
  `emit_write_term`; reworded the `emit_build_compound_term` comment that referenced it.
- **`src/driver/scrip.c`**: `pl_rich_node_emittable` admits numbervars/3; updated the EXCISED-list and
  flat-tier write-gate comments (the latter no longer names `emit_write_term`).

## Verification (all green)

- GATE-1 **5/5/5**; GATE-3 m2 **111/111**, m3 **111/111**, m4 **86 PASS / 0 FAIL / 25 EXCISED**.
- FACT grep 0; `g_vstack` 0; no-value-stack PASS; template-purity 7 baseline (`bb_builtin.cpp` unflagged).
- Siblings: Icon 12/12/12; SNOBOL4 12 PASS / 7 FAIL.
- Edge cases m2==m4: `write(3.14)`/`print(2.5)`/`write(0.7)` (float leaves), `write(1+2)` (operator term),
  `write(foo(a,b))` (non-list compound), `write([a,b,c])` (list), `print(42)`/rung22 (the regression case).

## Remaining 25 EXCISED — genuinely all substrate

findall ×5, retract/retractall ×5, abolish ×5, aggregate ×4, catch/throw ×5, dcg_generate ×1. With float
`is/2` (PLG-9h), copy_term (PLG-9i), and numbervars + write-list (PLG-9j) closed, **every remaining EXCISED
family needs a real runtime substrate** — there is no missing-TEXT-twin closure left anywhere. The two
buckets are **WAM-CP-13** (dynamic-DB: the rung14/15 tests call+enumerate dynamically-asserted predicates,
so this needs dynamic-predicate call + backtracking/CP in the standalone `.s`, not a deterministic helper)
and **PLG-10** (findall/aggregate goal-subgraph + the catch/throw exception barrier). Both are multi-session
substrates warranting a fresh design pass against the gprolog/swipl sources before any emit code.
