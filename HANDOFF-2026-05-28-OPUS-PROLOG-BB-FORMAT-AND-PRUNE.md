# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: arith + succ/plus + format + GOAL prune

**Goal:** GOAL-PROLOG-BB.md — CAT-D mode-4 emit gaps + housekeeping.

## State at handoff

- SCRIP HEAD `3c384e25`, pushed.
- .github HEAD `34ab63b9`, pushed.
- GATE-1 5/5 · GATE-2 132/0 (5 ORACLE_MISS) · GATE-3 mode-2 91/107 · GATE-4 4/4 · FACT 0
- Sibling smokes: raku 5/5, prolog/snocone/snobol4 hello-all baseline.
- Full mode-4 corpus (with .expected): **53/107** (+13 vs session-start baseline 40).

## What landed this session

### `6cf5a429` — arith `**` prefix fix, unary arith mode-4, succ/2 + plus/3

Mode-4 corpus 40→48 (+8). Fixes:

1. `rt_pl_arith` op-prefix clash: `op[0]=='*'` was firing on `"**"`. Reordered all checks
   so multi-char `strcmp` precedes single-char tests; added `op[1]=='\0'` guards. Added
   missing `//` (integer division).

2. Unary arith mode-4: new `bb_builtin.cpp` is/2 arm for unary BB_ARITH (`!pBB->β->β`)
   calling `rt_pl_is@PLT` with sentinel `r8d=-1, r9=0`. `rt_pl_arith` dispatches integer-
   result unary ops (sign/abs/truncate/integer/round/ceiling/floor/`\\`/msb) by op-name.

3. `succ/2` and `plus/3` mode-4: new arms + `rt_pl_succ`/`rt_pl_plus` effect helpers.
   succ was already PL_BI_AB; plus added to PL_BI_CHAIN. 6-scalar (succ) and 9-scalar
   (plus, 6 regs + 3 stack) SysV AMD64 ABI packing.

**Wins:** rung18 succ_plus 0/5→5/5; rung23 ext 3/5→5/5.

### `3c384e25` — CAT-D-format: format/1 + format/2 mode-4 emit

Mode-4 corpus 48→53 (+5). rung19 0/5→5/5.

- `bb_exec.c`: `rt_pl_format(arity, k0,i0,s0, k1,i1,s1)` + `rt_pl_format_term(arity,
  k0,i0,s0, args_term_ptr)`. Shared `rt_pl_format_walk` extracts the printf loop from
  mode-2 BB_BUILTIN format arm at bb_exec.c:3772. Handles ~n/~N, ~i, ~a/~w/~d/~p, ~~, ~t.
  `rt_pl_format_resolve` handles atom OR char-code-list format strings.
- `bb_builtin.cpp`: two-path emit arm (after plus/3). Path A scalar args1 (7-scalar call,
  6 regs + 1 stack at `[rsp+0]`, 16B alignment). Path B BB_PL_STRUCT args1 like `[world]`
  built via `emit_build_compound_term` → r8; calls `rt_pl_format_term@PLT`.

## GOAL file prune — `34ab63b9` (.github)

GOAL-PROLOG-BB.md: 802 lines → 328 lines (-59%). Preserves all 14 WAM-CP rungs, design
principle, port semantics, gate table, all OPEN rungs + CAT-D + Other open. Multi-paragraph
WAM-CP-1..5 completion narratives pruned to one-line each; LOWER-PIVOT / rung25-TERM-STRING
/ CAT-RUNG07-1 / CAT-D-11 success blocks rolled into terse roll-up at bottom.

## Verify-before-commit checklist (all confirmed)

```bash
make -j4 scrip                                  # clean
make libscrip_rt                                # clean
bash scripts/test_smoke_prolog.sh               # GATE-1 5/5 ✅
bash scripts/test_crosscheck_prolog.sh          # GATE-2 132/0 ✅
bash scripts/test_prolog_rung_suite.sh          # GATE-3 91/107 ✅
bash scripts/test_prolog_mode4_rung.sh          # GATE-4 4/4 ✅
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" \
  | grep -v "_templates/" | grep -v emit_core.c | wc -l   # FACT 0 ✅
```

Sibling smokes: raku 5/5 ✅, prolog/snocone/snobol4 hello-all matches baseline. Icon smoke
0/5 — pre-existing at `08e05f68` predating this session, not touched. Self-host needs
`corpus/SCRIP/lower.sc` absent from clone — environment, not code.

## Established mode-4 builtin emit pattern (for next session)

Each new BB_BUILTIN family (~4-5 corpus tests, mode-2 oracle in place) follows:

1. **Effect helper** in `bb_exec.c`: serializable scalars, calls `rt_pl_node_to_term` to
   materialize args, returns 1/0. NO port logic. RULES.md permitted (conversion + unify).
2. **Two-path template** in `bb_builtin.cpp`:
   - Path A (scalar args): N-scalar SysV call (rdi/rsi/rdx/rcx/r8/r9, stack `[rsp+0..]` if >6).
   - Path B (compound-literal args, BB_PL_STRUCT): `emit_build_compound_term` post-order
     walker builds Term* in rax → moved to reg; call `*_term` variant.
3. Trail mark on entry, unwind on fail (for fallible builtins).
4. Template owns `test eax,eax / je ω / jmp γ / β: jmp ω`.
5. 16B rsp alignment at every `call` — `sub rsp, 8` is wrong; use `sub rsp, 16` for one
   stack slot, `sub rsp, 32` for up to 3 stack slots. (Discovered during format work.)

## Open work — next priority order

1. **CAT-D mode-4 emit gaps** (each ~4-5 rungs, mode-2 oracle exists). Order by ease:
   - **`numbervars/3`** (rung20, 5 tests) — mode-2 model `pl_runtime.c:1258`. Stack-walk
     binds all vars in term to `$VAR(N)`. Straightforward.
   - **`char_type/2`** (rung21, 4 tests) — character predicates (alpha, digit, upper/lower).
   - **`writeq/1` `write_canonical/1` `print/1`** (rung22, 4 tests) — variants of `write`.
     `pl_writeq` / `pl_write_canonical` already in pl_runtime.c.
   - **`retract/1` `retractall/1`** (rung14, 5 tests) — mutates predicate's clause set.
   - **`abolish/1`** (rung15, 4 tests) — PL_BI_CHAIN_ABOLISH special wiring already in lower.
   - **`number_string/2`** + string ops (rung24-26).
   - **`term_to_atom/2` `term_string/2`** mode-4 emit (mode-2 ✅).

2. **`findall/3`** (rung11, 5 tests) — distinct because `nd->ival` holds
   `bb_pl_findall_state_t*` not arity int. Needs dedicated template path (emit goal
   sub-graph inline or route through `sm_interp_run`).

3. **WAM-CP-6 (Last-Call Optimization)** — principled SEGFAULT fix for deep recursion.
   Foundation work, larger scope than a single CAT-D arm.

4. **WAM-CP-9** — committed-ITE node + cut-truncate via CP-stack barrier (fixes rung07
   cut_cut, rung15 one_of_two). Subsumes PJ-AGW-5.

5. **Float-result unary arith** — `rt_pl_arith_d` returning double + parallel
   `rt_pl_is_d` constructing TERM_FLOAT. No corpus tests cover yet; defer.

## Session totals

| Metric | Start | End | Δ |
|---|---|---|---|
| Full mode-4 corpus | 40/107 | 53/107 | **+13** |
| rung families closed | — | rung18, rung19, rung23-ext | 3 families |
| Lines pruned from GOAL file | — | -474 (-59%) | |
| FACT RULE compliance | 0 | 0 | preserved |
| Commits to SCRIP | — | 2 | `6cf5a429`, `3c384e25` |
| Commits to .github | — | 3 | handoffs + GOAL prune |
