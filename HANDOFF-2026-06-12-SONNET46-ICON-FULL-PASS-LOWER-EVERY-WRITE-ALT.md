# HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-LOWER-EVERY-WRITE-ALT.md

**Session:** 2026-06-12 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — lower_every body-wiring + write+alt ring-duplication diagnosis
**HEAD (SCRIP):** `b1de2e3`
**m2:** 195/247 (was 194 at session start — prior watermark was stale at 194, actual baseline was 195 when session began; our commit nets +1 from the parent)

---

## Work Done

### lower_every no-body CONJ.γ fix (+1 m2, committed `b1de2e3`)

`lower_icon.c` `lower_every` `!BODY` branch: the original line was:
```c
γ_to(gen_result, gen_node == gen_result ? E : gen_node);
```
Changed to:
```c
IR_t * loop_target = (gen_result && gen_result->op == IR_CONJ) ? E : (gen_node == gen_result ? E : gen_node);
γ_to(gen_result, loop_target);
```

**When GEN is a `TT_SEQ`** (e.g. `every (x := ALT) > 2 & write(x)` — the `&` conjunction IS the expression, not a separate do-body), the SEQ lowers to IR_CONJ. The original code wired CONJ.γ → gen_node (ALT), creating a broken loop that jumped into the middle of the expression on success. The oracle (15608cf) wires CONJ.γ → EVERY (E), so the body correctly loops back through EVERY. Fix: when gen_result is IR_CONJ, always wire to E.

All prior working cases (e.g. `every write(1 to 3)` — gen_result=CALL, gen_node=TO) are unaffected because CALL ≠ IR_CONJ.

**Important finding:** The oracle at 15608cf is a DIFFERENT architecture (`lower_icon_nl.c` / `src/lower/nl/`) not present in HEAD's `lower/`. HEAD uses the old `lower_icon.c`. Do NOT compare HEAD topology dumps against the oracle expecting byte-identical results — verify by output, not dump.

---

## Diagnosed but NOT fixed: write + TT_ALTERNATE arg ring-duplication

**Bug:** `write("A", 2 | "none")` → `22` (missing "A", value doubled).

**Root cause:** The write/writes chain lowering (dval=1.0, `is_deep=1`) inlines args into the main BB graph via a node chain: LIT_S("A") → LIT_I(2) → ALT → CALL(write). The trampoline in `IR_interp_once` (line 5817) pushes every node's value to the ag_ring:
- LIT_S pushes "A"
- LIT_I(2) pushes 2
- ALT (no operand_aux, inline routing node) pushes 2 again (read from ring peek = LIT_I's value)
- CALL reads top `nargs=2` ring values → gets [2, 2], missing "A"

**Fix (one-line, not committed):** In `IR_interp_once` at line 5817, guard the ring push:
```c
// BEFORE:
ag_ring_push(bbg, IR_EXEC(cur).value);
// AFTER:
if (!(cur->op == IR_ALT && cur->n_operands == 0)) ag_ring_push(bbg, IR_EXEC(cur).value);
```
Inline ALT nodes (no operand_aux = inlined into the write chain, not a subgraph-ALT) should not push to the ring because their value is a copy of the arm node's value already pushed.

**Why lowerer fix doesn't work:** Switching write to subgraph mode (dval=2.0 or 3.0) for TT_ALTERNATE args breaks `every write("a"|"b"|"c")` — that pattern NEEDS the chain (dval=1.0) so the EVERY loop can re-drive the ALT generator via the topology. The fix must be in the interpreter, not the lowerer.

**Verification:** After applying the one-line fix:
- `write("A", 2 | "none")` → `A2` ✓
- `write("A", image(integer(2)) | "none")` → `integer(2) ----> 2` (full numeric label) ✓
- `every write(1 to 3)` → 1, 2, 3 ✓ (unaffected — TO has n_operands > 0)
- `every write("a"|"b"|"c")` → a, b, c ✓ (ALT with operand_aux from subgraph; n_operands > 0)

Expected gain from this fix: several rung36/37 tests (numeric, coerce prefix labels).

---

## State Invariants (all hold at HEAD b1de2e3)

- m2 icon smoke 12/12 HARD ✅
- m3 icon smoke 10/12 (2 pre-existing: proc_zeroarg, proc_recursion) ✅
- m4 icon smoke 10/12 (same 2) ✅
- Prolog m2 5/5 HARD ✅
- one-box gate PASS ✅
- No value stack, no C byrd-box functions, no bb_bin_t ✅

---

## Open Steps (GOAL-ICON-FULL-PASS)

Remaining m2 failures (52 non-xfail):

**Immediate next step (one line, high confidence):**
- **write+ALT ring-duplication fix** — `IR_interp.c` line 5817, guard described above. Expected +several rung36 tests.

**Tractable cluster:**
- **FULL-18-resid** — `every (x := (1|2|3|4)) > 2 & write(x)` still empty. CONJ.γ=EVERY is now correct (from this session's commit). The remaining issue: BINOP.ω=EVERY (ival=0) with ival=0 returns EVERY.γ=SUCCEED → terminates instead of resuming ALT. Needs an EVERY interpreter mode that retries the generator on filter-failure, OR the BINOP failure port needs to go to ALT directly. The oracle also produces empty output for this case (it's an open bug in 15608cf too). Needs deeper interpreter work.
- **FULL-12 coerce** — `integer(x)`/`real(x)` type combos. The write+ALT fix will recover the label prefix; remaining failures are likely the `integer()` builtin's handling of string-with-spaces/radix/sign forms. Check `by_name_dispatch.c` `integer` case; consult `oarith.r` (Icon canonical).
- **FULL-13 residual keywords** — `&error` write-back, `&dump`/`&trace`/`&random`.
- **FULL-14 scan-alt** — `IR_GEN_SCAN` resume re-enters scan across alt (rung37).
- **FULL-17 sort()** — `rt_list_sort`/`rt_table_sort`; consult `fstranl.r` (rung31, +5).
- **rung36/37 sweep** — after write+ALT fix, triage residuals.

---

## Key Facts for Next Session

1. **Oracle is at `/tmp/oracle/scrip`** (built from git worktree at 15608cf). Use it for output verification, NOT `--dump-bb` topology comparison — HEAD uses different lowerer architecture.
2. **`--dump-bb` does NOT show `operand_aux`** — two identical-looking dumps can still differ. Always verify by output.
3. **HEAD interp reads `bb->operands[0]` for NOT/SECTION/BANG**; push via `ir_operand_push`, not `bb_operand_aux_set`.
4. **`IR_LIT(bb).ival` is persistent across `bb_reset`** — safe for exhausted/state flags in LIMIT.
5. **`lower_icon.c` is the active Icon lowerer** — there is no `nl/` subdirectory in HEAD's `src/lower/`. The GOAL-ICON-FULL-PASS references to `lower_icon_nl.c` refer to what was present in 15608cf and later integrated/renamed.

---

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
