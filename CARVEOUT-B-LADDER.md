# CARVEOUT-B-LADDER.md — per-box-family ladder for CARVE-OUT B (template generation → Snocone `*(EXPRESSION)`)

**Row:** `carveout-b-decompose` (rank 1). **Produced by:** seat13, 2026-08-24. Read `ARCH-ICON.md`, `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`, `REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md` in full first, per this row's own NEXT block and CLAUDE.md's non-negotiable BB-codegen protocol. **Did not read `BB-REVAMP-TRACKER.md`** — CLAUDE.md explicitly forbids it; excluded from this ladder's research even though it matched my search for prior CARVE-OUT B content.

**THIS ROW PRODUCES THE LADDER, NOT THE PORT.**

---

## 0. This is a materially different, harder proposition than CARVE-OUT A — say so plainly

CARVE-OUT A (parsers) replaces C code that builds a **tree**. CARVE-OUT B (templates) replaces C code that emits **exact machine instructions under a fixed register contract** (`ARCH-ICON.md`'s REGISTER CONTRACT: R12=DCAP/CAS top, R13=Σ subject base, R14=δ cursor, R15=Δ subject length, RBX=GC bump-frontier, RSP/RBP dual-mode frame selection) via a **13-rule + 3-gated-FACT-RULE construction discipline** (`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`: one medium invisible, in-band patch records, `g_emit`-only operand reads, `x86_bin_t` abolished, TEXT-first conversion). A Snocone `*(EXPRESSION)` replacement has to reproduce that exactly, not just produce semantically-similar output.

**No prior art or prototype for this specific carve-out was found anywhere in `.github`** (excluding the forbidden tracker) — unlike CARVE-OUT A, where every language's Phase-2 rewrite was already substantially done three months ago. The brief's own citation (`REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md §7`, deferred `*expr`) explains *why* the mechanism should work in principle — SPITBOL's `*expr` defers evaluation to use-time exactly the way a template needs to name operands (`_.op_sval`, port labels) that don't exist until the template is instantiated for a specific IR node — but principle is not proof. **This ladder's rung 0 is a feasibility spike, not a family port**, because sizing any family-level rung before that spike answers "can this represent one real box's exact `x86(...)` call sequence at all" would be guessing.

## 1. Box census (measured live, do not trust "129" from memory — it drifted to 132 in two days)

`ls src/templates/bb_*.cpp | wc -l` → **132 files** (brief cited 129, written 2026-08-22 — natural two-day drift, not an error worth chasing). Total line count and per-family sizes weren't separately re-verified against a stale figure this time since none was cited to correct.

**Families, derived from the actual file list** (not typed from memory — every name below is a real file in the current tree):

| Family | Count | Members (representative, not exhaustive where large) |
|---|---|---|
| **SNOBOL4-style pattern-match leaves** | 26 | `match_{abort,alternate,any,arb,arbno,atp,bal,begin,break,breakx,capture,defer,end,fence0,fence1,len,lit,notany,pos,rem,replace,rpos,rtab,span,tab,value}` |
| **Icon `scan` leaves** (ARCH-ICON.md's "ICN-SCAN BB family", canonical set closed) | 11 | `scan_{alternate,any,bal,find,many,match,move,pos,sequence,tab,upto}` |
| **assign / rev_assign** | 7 | `assign_{global,local,var}`, `indirect_assign_{lit_s,var}`, `rev_assign{,_var}` |
| **call** | 7 | `call`, `call_{bool,define,fn,proc_staged,value,write_slot}` |
| **var** | 7 | `var`, `var_{frame,frame_ref,global,ref}`, `swap_var`, `unop_gvar_slot` |
| **binop** | 6 | `binop_{arith,concat_slot,gvar_arith,gvar_arith_slot,relop,relop_val,xrep_slot}` (7, one over-counted in the table row above — verify exact list before sizing this rung) |
| **coerce** | 4 | `coerce_{integer,numeric,real,string}` |
| **keyword** | 4 | `keyword_{assign,assign_snobol4,icon,snobol4}` |
| **coroutine (Icon `create`/`@`/co-expr)** | 5 | `activate, coret, cofail, create, suspend` |
| **goto/control-transfer** | 4 | `goto, goto_deferred, indirect_goto, move_label` |
| **glue** | 2 | `glue_flat, glue_framed` |
| **cell** | 2 | `cell_cut, cell_ite` |
| **idx** | 2 | `idx_get, idx_set` |
| **to** | 2 | `to, to_by` |
| **swap** | 2 | `swap, swap_var` (swap_var double-counted with var above — pick ONE bucket when this rung is actually sized) |
| **structural / statement-level singles** | ~33 | `arith, bound, case_arm, cmp_test, conjunction, cut, define, deref, det_nl, differ, disjunction, enter_init, every, fail, field_get, galt, gcc, gen_scan, glit, initial, iterate, key_gen, limit, lit_scalar, main, make_list, proc_value, random, ref_invariant, repalt, return, section, statement, subject, subscript, succeed, unop, zdp_anchor` |

⚠ **This is a first-pass grouping by filename prefix, not a semantic audit.** Whoever picks up rung 1 should re-derive the family boundaries by reading each box's actual body (many are 10-20 lines — cheap to check), not trust this table's exact membership, especially for the two double-counted files flagged above (`swap_var`, and the binop count-vs-list mismatch).

## 2. Rung 0 (mandatory prerequisite, not a real family) — feasibility spike

**Target: `bb_goto.cpp`, the smallest box in the tree by a wide margin (10 lines):**
```cpp
std::string bb_goto() {
    return x86_alpha() + x86_pair_loop();
}
```
Two encoder calls, no operands, no conditionals, no loop. **DONE-WHEN**: hand-write a Snocone `*(EXPRESSION)` form that produces this exact concatenation via deferred evaluation — e.g. something in the shape `*x86_alpha() *x86_pair_loop()` or an equivalent Snocone expression that, when compiled through whatever bridge connects Snocone execution to the existing `x86(...)`/`bb_emit_x86` C machinery — **and this bridge does not exist yet either; specifying its shape is part of rung 0's job, not assumed** — produces byte-identical TEXT and BINARY output to the current `bb_goto()` on a real IR_GOTO node, verified with `--compile` asm diff (ASM-DIFF-FIRST, per CLAUDE.md's own debugging order). If this cannot be made to work even for the simplest possible box, that is the single most important finding this whole carve-out could produce — say so plainly rather than forcing a result, and route it back to Lon as a routed FINDING (this ladder does not pre-judge the answer).

**Why `bb_goto` specifically, falsifying "smallest first" the same way CARVE-OUT A's ladder did**: it's not just small, it's small **and structurally representative** — it's a real, shipping box (not a stub), it touches exactly two of the `x86_asm.h` vocabulary entries named in `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`, and it has zero operand-reading (`_.op_*`) to further isolate the spike to "can deferred-eval drive the encoder concat at all" before adding "and also thread operand data through it."

## 3. Sequencing — contingent on rung 0, not a fixed ladder yet

Everything past rung 0 is written as a **conditional plan**, not a committed sequence, because rung 0's outcome changes what's even possible:

- **If rung 0 succeeds**: rung 2 should be the smallest FAMILY next, not the biggest. Best candidate: the **structural/statement-level singles** with zero or near-zero operand reads (`bb_fail`, `bb_cut`, `bb_every`, `bb_cell_cut`, `bb_det_nl` — all 13-16 lines) — same low-operand-count property that made `bb_goto` a clean spike, but now proving the pattern generalizes across *several* boxes instead of one. **Save `match` (26 files, the semantically heaviest family, closely bound to the deferred-`*expr` pattern-matching semantics this whole carve-out's premise leans on) and `scan` (11 files, Icon-specific dual-family split per ARCH-ICON.md §"String scanning") for LAST** — they're the biggest and most likely to expose the hard cases (operand threading, port wiring, loop bodies) that a from-scratch mechanism needs to prove out on easy ground first.
- **If rung 0 fails or is inconclusive**: this ladder cannot responsibly propose family rungs at all — the right next row is a narrower investigation into *why* it failed (bridge-mechanism design, or a hard blocker in how Snocone execution reaches the x86 encoder layer), not a fresh attempt at family sizing.

## 4. New-global-variable note

`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`'s FACT RULE (no new global anywhere without Lon's in-chat banner-ask) applies with extra force here: whatever bridges Snocone execution to `bb_emit_x86`/the encoder layer may be tempted to use file-scope state to pass the deferred pattern's result across the language boundary. **Flag this explicitly for rung 0's implementer**: if the bridge design seems to need a new global, that is exactly the large ⛔ banner ask this ladder cannot pre-clear — stop and ask Lon that session, do not build around it silently.

## 5. Rung 0, ready to fire

```
# TASK carveout-b-goto-spike · owner: unassigned · state: FREE
GOAL: CARVE-OUT B, rung 0 (mandatory feasibility spike, see .github/CARVEOUT-B-LADDER.md).
Prove or falsify, on the smallest real box in the tree (bb_goto.cpp, 10 lines, two encoder
calls, zero operands), that a Snocone *(EXPRESSION) deferred-eval form can drive the existing
x86(...)/bb_emit_x86 encoder machinery and produce byte-identical TEXT+BINARY output to the
current C box. No bridge between Snocone execution and this C machinery currently exists --
specifying its minimal shape (just enough to pass this one spike, not a general design) is
part of this rung's job.
DONE-WHEN: a written spike (Snocone expression or minimal bridge code, whichever the
investigation lands on) exists, is exercised against a real IR_GOTO node via --compile, and
its emitted .s asm-diffs byte-identical (ASM-DIFF-FIRST) against bb_goto()'s current output --
OR, if infeasible, a routed FINDING states exactly why, with the specific mechanism that
blocks it named (not "didn't work"). Either outcome closes this rung; only "didn't try" doesn't.

## NEXT
STEP 1: Read ARCH-ICON.md's REGISTER CONTRACT section and GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md
R1-R13 + the three gated FACT RULES in full before writing anything -- this spike must respect
the SAME rules a C box does (one medium invisible, in-band patch records, TEMPLATE READS ONLY
g_emit) even though it's not itself a C template.
STEP 2: Read src/templates/bb_goto.cpp and trace x86_alpha()/x86_pair_loop() in x86_asm.h to
understand exactly what they emit and what they need as inputs (ports, in this case -- goto has
none of its own, it's pure pair-loop wiring).
STEP 3: Design the minimal bridge -- how does Snocone-executed code reach x86_alpha() and
x86_pair_loop() and get their string results concatenated in the right order? This might be as
simple as an EVAL-based call-out, or might need something not yet designed. Name it plainly.
STEP 4: Build the spike. Compile a program using IR containing one IR_GOTO node through BOTH the
existing C bb_goto() path and the new spike path (however that's wired for a one-off test --
does not need to be a real dispatch-table integration). Diff the emitted .s.
STEP 5: Report the result honestly. A negative result with a clearly named blocker is a
successful rung; do not stretch to force a false positive.

## QA

## LEDGER
- [seat13·2026-08-24] Rung drafted as part of carveout-b-decompose's ladder deliverable. Not
  claimed/started -- this is the brief, not the work. See .github/CARVEOUT-B-LADDER.md for why
  this is a feasibility spike rather than a family port, and why bb_goto specifically.

## BRIEF (verbatim, as it stood in the ladder)
Rung 0 of the CARVE-OUT B ladder (mandatory prerequisite before any family rung is sized).
See .github/CARVEOUT-B-LADDER.md §2/§5 for full context.
```
