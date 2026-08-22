# FINDING — seat15: `box-fusion` FIRST STEP done — target shape confirmed on real demo code; implementation still BLOCKED on the design call two prior sessions already flagged

**Date:** 2026-08-22 · **Seat:** seat15 (`/home/claude15`, Claude Sonnet 5) · **Row:** `box-fusion` (rank 6) · **Status:** investigation complete, NOTHING LANDED (by design — see §4). Tree: SCRIP `77300c397` (HEAD, untouched), clean.

## 1. What the brief asked

FIRST STEP: re-confirm `FINDING-2026-08-21-s250`'s counts still hold on the live tree, then "identify the fusible adjacency classes from a real demo's box stream (not a synthetic) and pick the single most frequent one for rung 1."

## 2. Live-tree re-confirmation of s250

`bb_binop_gvar_arith.cpp` and `bb_binop_gvar_arith_slot.cpp` both still exist, both still declared in `bb_templates.h`, both still **zero call sites** (`grep -rn 'bb_binop_gvar_arith' src/` returns only the two declarations and the two definitions). `IR_BINOP_GVAR_ARITH` still appears **nowhere** in `src/contracts/` — no enum member exists under that name anywhere in the tree; the string only occurs as a comment/label inside the two dead `.cpp` files themselves. s250 §4/§7's factual claims stand, unchanged, on today's HEAD.

## 3. Real-demo census (not synthetic) — the target shape IS the most frequent non-trivial chain

`--dump-bb` on the six real BM-4 demo grammars (`calculator-1`, `calculator-2`, `claws5`, `json`, `porter`, `treebank-match` — actual mini-applications, not the purpose-built microbenchmarks like `arith_loop`), split into per-statement box-kind chunks on `STATEMENT_END` boundaries, 765 chunks total:

| rank | shape (sorted kinds) | count | % | note |
|---|---|---|---|---|
| 1 | `(ASSIGN, LIT_INTEGER)` | 82 | 10.7% | 2-box, e.g. `ZCHK = 1` — nothing to fuse, one producer already |
| 2 | `(DEFINE,)` | 70 | 9.2% | 1-box, not a runtime hot path |
| 3 | `(ASSIGN, CALL, LIT_STRING)` | 57 | 7.5% | once-per-DEFINE glue |
| 4 | `(ASSIGN, LIT_STRING)` | 53 | 6.9% | 2-box, nothing to fuse |
| **5** | **`(ASSIGN, BINOP, LIT_INTEGER, VAR)`** | **45** | **5.9%** | **s250's rung-1 target — the top-ranked shape with ≥3 boxes / genuine multi-producer chain** |
| 6 | `(ASSIGN, VAR)` | 43 | 5.6% | plain copy, different mechanism |
| 7 | `(CALL, VAR)` | 39 | 5.1% | |
| 8 | `(ASSIGN, BINOP, VAR, VAR)` | 30 | 3.9% | two DIFFERENT var operands — harder case, two GVA reads |
| 9 | `(ASSIGN, BINOP, LIT_STRING, VAR)` | 26 | 3.4% | string concat self-update — different type family, out of scope for the arithmetic condition |

**All 45 of the rank-5 hits are genuine same-name self-updates** (`ASSIGN` label == `VAR` label — verified per-instance, not assumed), i.e. exactly the `V = V <op> <int-literal>` shape s250 §4.1 scoped, satisfying condition 2 universally in this sample. Two instances are `harness.inc`'s own `ZFLR = ZFLR * 1000000` / `ZBUD = ZBUD * 1000000` (present in all six files via `-INCLUDE`), which is an independent sanity check that the census is finding real, semantically-meaningful hits, not an artifact. **This closes the FIRST STEP: on real demo code, not just the synthetic `arith_loop` ladder, s250's chosen shape is empirically the single most frequent fusible multi-box chain — the brief's own selection criterion is satisfied.**

## 4. A scoping detail NEITHER prior session flagged: the dead code only computes the value — neither template writes it back

Read both dead templates in full. `bb_binop_gvar_arith_slot()`'s live arm (`_.op_arith_descr` false path, lines 45-79) and `bb_binop_gvar_arith()`'s two-named-operand arm (lines 48-73) both **compute `op(a,b)` into an operand slot (`FRQ(_.op_off)`)** — a spine cell — and stop there. **Neither one stores the result back into the GVA-resident variable's own memory.** That write-back is the `ASSIGN` box's job today, and nothing dead in the tree does it as part of the same emission. s250 §4's asm prototype (`mov rax,[r9+40]; add rax,1; mov [r9+40],rax` — one load, one add, one store, done) folds the write-back into the SAME three instructions; wiring the existing dead arms as-is would still leave a separate `ASSIGN` box reading the slot and storing to the GVA cell — a partial win (3 boxes → 2), not s250's measured −19 instr / −7 stores (4 boxes → 1). **Completing the actual measured win requires extending the emission (or adding a sibling arm) to fold the GVA store into the same box — new logic, even though it needs no new `IR_*` enum tag.** This is worth flagging precisely because it reconciles two pieces of history that read as contradictory: s250 §7 says "fusion needs no new IR kind" (true — confirmed, the shape-dispatch predicate runs entirely on existing per-BB operand-aux fields already used by ordinary `IR_BINOP` emission) while seat06's second-session cursor says the target "needs new machinery (new optimizer elision pass + one new IR opcode)" (also plausibly true, if seat06 was scoping the *general* box-fusion mechanism rather than this one narrow rung). Neither claim was wrong; they were scoping different things, and this session's read of the actual dead code shows the narrow rung-1 case sits in between: no new enum value, but real new emission logic (the write-back fold) plus a new dispatch-selection rule (an optimizer or lowering-time recognizer that decides an `IR_BINOP` qualifies under §4.1 and routes it to the completed template instead of the default one).

## 5. Why this stops here — CHAT-ESCALATION, properly routed this time

RULES.md's CHAT-ESCALATION law: "any blocker only Lon can clear goes into chat as one question at the TOP of the reply; ≥2 zero-rung sessions ⇒ ask before code." This row already has two: s250 itself ("NOTHING LANDED. This row is BLOCKED on a design call... Filed as `ask chain-slot-coalescing`") and seat06's second session ("CHAT-ESCALATED per this file's own law rather than freelance a third zero-rung build... that escalation was typed in-chat only and never routed via `s4e_msg.sh ask`, so it likely never reached anyone"). Writing code now — on what would be the third zero-rung session's watch, this time as an actual implementation rather than more measurement — without the design call landing would repeat exactly the failure mode the row's own history twice tried and failed to avoid. **Routed this time through both channels that exist:** `s4e_msg.sh ask box-fusion` (fixing the prior routing gap) and directly to the operator in this session's own chat (since CHAT-ESCALATION's whole point — asking where only Lon can clear it — is satisfied most directly by a live session, which this one is).

**Not done, and deliberately not attempted:** any lowering/optimizer/emitter code. **Done:** the FIRST STEP measurement in full, on real (not synthetic) demo code, plus the write-back scoping detail in §4 that sharpens exactly what "rung 1" would need to build.

**Watermark:** SCRIP `77300c397` (untouched) · corpus (untouched) · `.github` this commit. Scratch (not committed, reproducible from §3's recipe): `--dump-bb` census script, six real demo programs, no corpus/SCRIP files touched.
