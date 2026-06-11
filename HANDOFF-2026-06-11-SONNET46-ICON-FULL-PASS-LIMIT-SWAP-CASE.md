# HANDOFF-2026-06-11-SONNET46-ICON-FULL-PASS-LIMIT-SWAP-CASE.md

**Session:** 2026-06-11 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — TT_LIMIT / TT_SWAP / TT_LCONCAT / TT_NULL(unary) / TT_CASE arm-entry fix
**HEAD (SCRIP):** `2eaf3bf`
**m2:** 194/247 (was 184 at session start)

---

## Work Done (+10 m2 tests)

### TT_LIMIT (`e \ n`) — 5 tests gained (rung14 all 5)

`lower_icon_nl.c`: new `case TT_LIMIT` — builds `IR_LIMIT` node, lowers expr subgraph
with `γ=nd, ω=ω`, lowers limit subgraph separately. **Key insight:** `cx->beta` is set to
`inner_beta` (the generator's own β, e.g. TO node), NOT to the LIMIT node. This makes
`lower_every`'s `gen_node = cx->beta = TO`, so `loop_back = TO`. The body's γ/ω both wire
back to TO (the generator), not to LIMIT. LIMIT is only reached once per generator success
(via TO.γ=LIMIT), counts arrivals, and uses `IR_EXEC(operands[0]).value` (the cached value
in the generator result node) to read the yielded value — never ag_ring, which is stale on
loop-back.

`IR_interp.c` — `IR_LIMIT` rewritten:
- `operands[0]` = generator result node (TO), `operands[1]` = limit node, `operands[2]` = entry
- `IR_LIT(bb).ival = 1` = persistent exhausted flag (not cleared by `bb_reset` since only
  `IR_EXEC` fields are reset, not `IR_LIT`)
- state=0: eval limit, init counter=max, state=1, return γ.node
- state=1: read `IR_EXEC(operands[0]).value`, counter--, if <=0 set ival=1 (exhausted), return γ
- ival=1: return ω immediately (exhausted guard — fires when EVERY re-drives generator)

**Tracing (confirmed):** `every write((1 to 10) \ 3)`:
Entry LIT_I(1)→LIT_I(10)→TO(val=1)→LIMIT(state=0: mx=3, counter=3→2, val=TO.val=1, return γ=CALL)→CALL(write 1, γ=TO)→TO(counter++=2,val=2)→LIMIT(state=1: counter=2→1, val=2, return γ=CALL)→CALL(write 2, γ=TO)→TO(counter++=3,val=3)→LIMIT(state=1: counter=1→0, ival=1, return γ=CALL)→CALL(write 3, γ=TO)→TO(counter++=4,val=4)→LIMIT(ival=1: return ω). Done. ✓

### TT_SWAP (`:=:`) — 2 tests gained (rung15_swap_basic, rung15_swap_str)

`lower_icon_nl.c`: `case TT_SWAP` — builds `IR_SWAP` node, lowers both children with
`γ=nd, ω=ω`, pushes result nodes as `operands[0]`/`[1]`. IR_SWAP interpreter already correct
(reads `IR_LIT(operands[*]).sval` for variable names, does NV_SET swap).

### TT_LCONCAT (`|||`) — 1 test gained (rung15_lconcat)

`lower_icon_nl.c`: `case TT_LCONCAT` — builds `IR_LCONCAT`, wires two operands via
`bb_operand_aux_set(cx->g, nd, ax, 2)` exactly like IR_BINOP.

`IR_interp.c` — `IR_LCONCAT` rewritten: operand_aux-first (call `IR_interp_node` on each,
read their values), ag_ring fallback for the SNOBOL4 path (the old always-ag_ring path was
a stub — `!((IR_t*)0)` is always true because NULL != NULL in C boolean context).

### TT_NULL (unary `/`) — 1 test gained (rung34_null_test_null_fails)

**Bug:** `TT_NULL` in `lower_icon_nl.c` switch (line ~140) was always producing `IR_LIT_NUL`
regardless of whether the node had a child. Unary `/x` parses as `e_unary(TT_NULL, x)` with
n=1, but the handler ignored the child and emitted literal null.

**Fix:** `case TT_NULL`: if `t->n > 0 && t->c[0]` → emit `IR_UNOP` with `ival=TT_NULL`;
otherwise emit `IR_LIT_NUL`.

`IR_interp.c` — added `case TT_NULL` to `IR_UNOP` switch: fail if non-null (`v.v != DT_SNUL`),
succeed if null. (Inverted from `TT_NONNULL`.)

### TT_CASE (arm-entry fix) — 2 tests gained (rung33_case_case_arith x3 cases)

**Bug:** `lower_icon_nl.c TT_CASE` was calling `lower(cx, t->c[i], NULL, NULL, &kn)` and
`lower(cx, t->c[i+1], γ, ω, &vn)` then pushing `kn`/`vn` (result nodes) as arm operands.
For `1: 1*10`, the value subgraph entry is LIT_I(1), result is BINOP(1*10). CASE interpreter
started walking from BINOP directly, missing the LIT_I chain — so BINOP's operand_aux
LIT_I nodes had FAILDESCR values, causing BINOP to fail → fell through to default arm (700).

**Fix:** capture entry nodes: `IR_t * ke = lower(..., &kn); IR_t * ve = lower(..., &vn);`
and push `ke`/`ve` (entries) instead of `kn`/`vn` (results).

---

## State Invariants (all hold)

- m2 icon smoke 12/12 HARD ✅
- m3 icon smoke 10/12 (2 pre-existing: proc_zeroarg, proc_recursion) ✅
- m4 icon smoke 10/12 (same 2) ✅
- Prolog m2 5/5 HARD ✅
- No value stack, no C byrd-box functions, no bb_bin_t
- one-box gate PASS ✅

---

## Open Steps (GOAL-ICON-FULL-PASS)

Remaining m2 failures (53 non-xfail):

**Tractable cluster (14 tests):**

- **rung13_alt_filter, rung13_alt_cross_arg/sideeffect** — FULL-18-resid: assign-generator
  β not propagating through chaining call into enclosing every. `every (x := (1|2|3|4)) > 2 & write(x)` gives empty. The `c9ec94c` gate guards write-chaining; do NOT loosen blindly.
- **rung16_subscript_sub_every** — `every write(s[1 to 3])` only yields first char. Same β-chain issue in subscript generator context.
- **rung19_pow_toby_real_toby_neg/pos** — `every write(3.0 to 1.0 by -1.0)` gives `0`. Real-valued `to-by`; check `IR_TO_BY` real path in interpreter.
- **rung23_table_table_key** — `key(t)` returns only first key (10 instead of 60=10+20+30). `key()` not generative; needs suspension/resume in `by_name_dispatch.c`.
- **rung24_records_field_assign, record_loop** — `b.w := 99` hits `[NO-AST] interp_eval stub`. IDX_SET for record field lvalue. Check `TT_ASSIGN` with `TT_FIELD` lhs.
- **rung30_builtins_misc_seq** — `seq(1) \ 3` gives empty. `seq()` builtin not generative.
- **rung32_strretval_strret_every** — `every write(tag("a"|"b"|"c"))` only yields first. Call doesn't propagate β back to alt generator.
- **rung35_block_body_every_gen_block** — `if v=20 then break` inside `every...do` goes to wrong target (20 printed instead of stopping at 10). break/next target wiring in every-do block.

**rung36/37 cluster (39 remaining failures):** Larger programs, various issues. Do FULL-12..17 first.

**Standing open intel (carried from prior sessions):**
1. `--dump-bb` does NOT show `operand_aux` — verify by output, not dump alone
2. HEAD interp reads `bb->operands[0]` for NOT/SECTION/BANG; push via `ir_operand_push`, not `bb_operand_aux_set`
3. 15608cf baseline scored 193; HEAD is 194 — the 43-test gap from BB-FIXUP/Pascal shared-lowerer changes may be closing; `git bisect` if needed
4. `IR_LIT(bb).ival` is persistent across `bb_reset` — safe to use as exhausted/state flags

---

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
