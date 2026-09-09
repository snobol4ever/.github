# A generator in a non-first operand was entered at its resume port, so its first run was lost

**Measured 2026-09-09 by hq_C** · oracle `icont`/`iconx` v9.5.25a · CEO-457 (question), CEO-461 (ruling: cut it).
The symptom hq_V reduced was `1 to (3|7)` generating seven values where iconx generates ten.

## One cause, three constructs

`lower_icon.c` wires an operand's entry with a **generator-aware** helper that routes to the target's **β (resume)** port whenever the target is a generator. An alternation *is* a generator, so it was entered at its resume port and its first run never ran.

This is the cfo's `TT_REVASSIGN` defect verbatim (SCRIP `20a3c797c`, where `x <- 2 | 3` gave `3`), and the cure is the same single edge: **α on entry**. The consistency argument, not a guess: the owning node's own ω is *already* wired to the operand's β for resumption, so α-on-entry / β-on-resume is what the rest of the wiring already assumes.

**Three sites, all measured:**

| construct | before | after |
|---|---|---|
| `1 to (2\|4\|6)` | `1..4`, `1..6` | `1,2` · `1..4` · `1..6` |
| `1 to 6 by (1\|2\|3)` | first run lost | matches |
| `"abcdef"[1:(2\|4\|6)]` | `abc`, `abcde` | `a` · `abc` · `abcde` |
| `"abcdef"[(1\|3\|5):6]` | first run lost | matches |
| `"abcdef"[(1\|2):(4\|5)]` | 1 of 4 results | all 4 |

## ⭐ A two-alternative witness cannot state this bug

On `1 to (3|7)` — two alternatives — "the **first** run is lost" and "only the **last** survives" produce **identical output** and are different bugs. Reading the two-alternative witness, I concluded the latter and told the ceo so; a three-alternative witness settles it immediately (`1 to (2|4|6)` yields `1..4` then `1..6`, so exactly the first is lost and the rest are intact). hq_V's original framing was right and my intermediate reading was wrong.

⛔ **The correction matters beyond the etiquette: the two readings imply different cures.** "Only the last survives" says the alternation is being driven to exhaustion before use; "the first is lost" says it is entered one port too far along. A witness that cannot separate them is not a smaller version of the right witness — it is a witness that licenses the wrong fix. hq_V has been asked to pin rungs on three alternatives.

## ⭐ The green rows are the finding's other half

Five constructs were measured **green** and they are what bound the class:

`1 + (2|4|6)` · `"x" || ("a"|"b"|"c")` · `1 < (2|4|6)` · `[1,(2|4|6)][2]` · `"abcdef"[(2|4|6)]` · `(1|3|5) to 6`

Without them the obvious generalisation is "binops with generator operands", which is **wrong** — a plain binop is not itself a generator and was always correct, and so is a plain subscript. The real class is narrower and stateable: **a node that is itself a generator, taking another generator in a non-first operand.** `(1|3|5) to 6` is the sharpest of the five: a generator in the *first* operand is green because that operand never goes through the helper at all.

⭐ An ablation set's yield is as much in the rows that stay green as in the rows that flip; the green rows are what turn a symptom into a class with edges.

## NOT CLAIMED

- No board row is claimed to move here. Control arm: `test_gate_icon_master_per_entry_identity`, per-entry, at identity.
- Whether other generator-valued nodes take a generator in a non-first operand anywhere else in `lower_icon.c` is **not** exhaustively swept — 29 sites use the generator-aware helper and three are cured. The remaining ones are not known to be wrong; they are simply not measured.
- The witness is handed to hq_V for absorption rather than landed loose (CEO-452; CEO-462's exception was one-time and is spent).
