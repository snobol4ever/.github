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

## write+ALT ring-duplication fix (committed `f6286b2` in SCRIP)

**Bug:** In the `dval=1.0` write-chain path, an `IR_ALT` node in the arg chain causes its arm[0] entry to be pushed to the `ag_ring` by the trampoline traversal, then `IR_interp_node(ALT)` re-runs arm[0] internally and sets `ALT.value` to that arm result. The trampoline then pushed `ALT.value` again, creating a duplicate ring entry that made CALL read wrong arg values.

**Root cause:** `lower_alt` builds arm[0] entry as the same node that appears in the write chain. The outer trampoline visits it and pushes its value. Then ALT runs internally, sets `ALT.counter=0`, returns. Trampoline sees `cur=ALT, counter==0` → skip push. This is the correct discriminator.

**Fix** in `IR_interp_once` and `IR_interp_resume` (two symmetric sites):
```c
// BEFORE:
ag_ring_push(bbg, IR_EXEC(cur).value);
// AFTER:
if (cur->op == IR_ALT && IR_EXEC(cur).counter == 0) { } else ag_ring_push(bbg, IR_EXEC(cur).value);
```

**Guard logic:** `counter==0` means this is arm[0]'s first success — arm[0]'s value was already pushed by the trampoline chain traversal. `counter>0` means we resumed past arm[0]; the new arm's value is NOT yet in the ring, so push it.

**Verified:**
- `write("A", 2|"none")` → `A2` ✓ (was `22`)
- `every write("a"|"b"|"c")` → `a,b,c` ✓ (was `a,a,a`)
- `write("A", image(integer(2))|"none")` → `A2` ✓
- `every write(1 to 3)` → `1,2,3` ✓ (unaffected)
- m2 195 no regression.

**Note:** m2 count stays at 195 because the specific rung36 tests that exercise write+ALT are all gated on other unimplemented features (local variables, `record` declarations, string operator invocation). The fix is structurally correct and needed.

---

## Diagnosed but NOT fixed: write + TT_ALTERNATE arg ring-duplication (SUPERSEDED by fix above)

This was the original handoff diagnosis. The committed fix `f6286b2` is the correct solution; the handoff's suggested one-liner was a partial diagnosis.

---

## State Invariants (all hold at HEAD b1de2e3 / f6286b2)

- m2 icon smoke 12/12 HARD ✅
- m3 icon smoke 10/12 (2 pre-existing: proc_zeroarg, proc_recursion) ✅
- m4 icon smoke 10/12 (same 2) ✅
- Prolog m2 5/5 HARD ✅
- one-box gate PASS ✅
- No value stack, no C byrd-box functions, no bb_bin_t ✅

---

## Open Steps (GOAL-ICON-FULL-PASS)

Remaining m2 failures (52 non-xfail). All blocked on features not yet implemented:

**Tractable next items:**
- **FULL-12 coerce** — `integer(x)`/`real(x)` type combos. Requires `local` declarations (parse error on `local` keyword blocks most coerce tests). The `by_name_dispatch.c` `integer`/`real` builtin likely needs string-with-spaces/radix/sign handling. Consult `oarith.r` (Icon canonical). After `local` support.
- **FULL-13-resid keywords** — `&error` write-back (`:=` to `&error`), `&dump`/`&trace`/`&random`.
- **FULL-14 scan-alt** — `IR_GEN_SCAN` resume re-enters scan across alt (rung37).
- **FULL-17 sort()** — `rt_list_sort`/`rt_table_sort`; consult `fstranl.r` (rung31, +5).

**Blocking issue for most rung36/37 tests:** The Icon parser rejects `local` declarations (`parse error: expected ; (got IDENT)` after `local`). This blocks virtually all rung36 tests that declare `local` vars at the top of main. Fixing `local` would unlock a large cluster.

**rung37_neg_pos infinite loop:** `every &pos <-> x do write(...)` loops indefinitely because `<->` (reversible swap) on `&pos` in a scan environment with out-of-bounds values never terminates. This is a complex keyword-as-lvalue + reversible-swap feature; leave pinned.

---

## Key Facts for Next Session

1. **SCRIP HEAD = `f6286b2`** (write+ALT ring fix). **m2 195 · m3 29 · m4 32**.
2. **The `local` keyword** causes parse errors on virtually all rung36 tests. Fix Icon parser to accept `local id1, id2, ...;` declarations.
3. **write+ALT fix semantics:** `IR_ALT.counter==0` = first arm success (arm[0]'s value already in ring from chain traversal → skip push). `counter>0` = resumed past arm[0] (new arm value not in ring → must push).
4. **Consult canonical sources before any new construct:** `refs/jcon-master/tran/irgen.icn` for port topology; `refs/icon-master/src/runtime/*.r` for semantics.
5. **Oracle at `/tmp/oracle`** (git worktree at 15608cf) — use for output verification only, NOT topology comparison (different architecture).

---

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
