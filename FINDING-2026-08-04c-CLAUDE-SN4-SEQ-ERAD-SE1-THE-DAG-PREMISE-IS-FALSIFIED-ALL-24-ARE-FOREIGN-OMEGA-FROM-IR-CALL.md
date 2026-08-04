# FINDING-2026-08-04c (s5) — SEQ-ERAD SE-1: the DAG premise is falsified; all 24 are foreign-ω from IR_CALL

**Session:** 2026-08-04 session 5, Opus. Goal: `GOAL-SNOBOL4-BB` (HQ seat), LADDER SEQ-ERAD opened this session.
**SCRIP HEAD:** `f5389c0c`. **Zero lower/template changes.** Emitter change is three env-gated `fprintf`s
(`SCRIP_SEQDAG=1`, default off) plus the deletion of a tracked `.bak`.

---

## Result 1 — three paths dirty a sequence, and we only knew about one

`seqclean[k] = 0` has **three** independent sites in `emit.cpp`. The inherited narrative — and the ladder's own
first draft — knew only the second:

| path | site | what it means |
|---|---|---|
| **CHAIN** | `:2422` | an element's entry or resume root is not present in this emission chain |
| **DAG** | `:2433` | one operand node is claimed by two different sequences (the shared-subtree fence) |
| **FOREIGN** | `:2443` | a σ/φ-marked edge enters the sequence from a node that is not one of its element roots |

The corpus figure everyone was citing ("26 need the counter") is the count of `clean=0`, which **sums all
three**. Nobody had ever split it.

## Result 2 — ⛔ THE SPLIT: 32 events, 24 nodes, **100% FOREIGN**

Instrumented all three paths and swept **all 211 SNOBOL4 corpus + benchmark programs**:

| path | events | files |
|---|---|---|
| CHAIN | **0** | 0 |
| DAG | **0** | 0 |
| **FOREIGN** | **32** | **8** |

- **24 distinct dirty nodes** (32 events; a node can be dirtied by more than one incoming edge).
- The inherited **26 was never re-derived**; HEAD-stamped it is **24**. CENSUS SHELF LIFE, again.
- **Origins: 26 `IR_CALL` + 6 `IR_LIT_INTEGER`.**
- **Side: 32 of 32 ω.** Every single one is a FAIL edge. Not one γ.
- Files: `beauty.sno` 14 · `omega_driver` 4 · `treebank-list` 4 · `Gen` · `Gen_driver` · `TDump_driver` ·
  `omega` · `treebank-array` 2 each.

## Result 3 — what this falsifies, precisely

**FINDING-2026-08-04b's DAG counterexample is CORRECT AS A PROPERTY and WRONG AS A CAUSE.** SNOBOL4 patterns
*are* values; a reused pattern variable *can* lower as a shared subtree; the claim algorithm at `emit.cpp:2430`
implements that fence correctly. **But it fires zero times on the entire corpus.** No sequence anywhere needs
the counter because of shared-subtree ambiguity.

Lon's stage-2 BUILD argument (a statement builds its pattern; a build yields a fresh object; two use sites are
two builds, so the DAG is manufactured by LOWER rather than present in the semantics) **stands as semantics and
is untested as a defect**, because the defect it predicted does not occur.

The fence's own comment had named the real class all along, and three sessions read past it:
*"GOTO-chased marks from foreign protocol glue — DEFER return, ARBNO seal — must keep the counter."*

## Result 4 — the real class, and why it is a better target

**A σ/φ-marked ω edge enters the sequence from outside its 2N element-root list**, so the static φ re-point has
no legal target and the counter survives as the runtime disambiguator. With 26 of 32 origins `IR_CALL` on the ω
side, this is the **`:F()` fail protocol re-entering the pattern spine**.

It is a better target than the DAG on three counts:

1. **It is reachable.** The DAG fix would have been a no-op; this one has 32 live customers.
2. **It may be a LOWER registration bug, not a protocol problem.** A call inside a pattern element is still
   that element. If LOWER simply fails to push it to the 2N operand list, registering it flips `seqclean` to 1
   with no protocol change at all — the cheapest possible outcome.
3. **If genuinely external**, the counter is holding a *return point for a foreign re-entry* — which is the call
   unit's job (`corpus/probe/bb/test_sno_cell_5.s`, `resume = MY continuation`, carved per entry), not the
   sequence's. Same conclusion the DAG story reached, by a route that actually fires.

⚠ **Open sub-class:** the 6 `IR_LIT_INTEGER` origins. A literal with an ω edge is a *deferred* integer — check
against the open D07/D08 defect (`LEN(*N)` deferred integer fails to evaluate) before fixing twice.

## Result 5 — `beauty.sno` is not an instrument, and does not currently compile

Ruled by Lon this session: **`beauty.sno` is the FINAL FINAL DESTINATION** — it becomes SCRIP's SNOBOL4 parser
`parser_snobol4.sc` in Snocone source. It is what the compiler is built *to run*, never a gate to measure the
compiler *with*. The ladder's first draft had `beauty.sno md5 EXACT` in five acceptance criteria; all five are
rewritten to `beauty_suite/` driver goldens (verified reproducing byte-exact under `sbl -b` at SE-0).

Measured incidentally and logged for its own sake: **`beauty.sno` does not compile under the SPITBOL oracle in
a fresh checkout** — `semantic.inc(16) : ERROR 217 -- syntax error: duplicate label`, with the listing printing
source line 588 **twice** while the sources contain exactly one `shift` label and exactly one
`-INCLUDE 'semantic.inc'`. SCRIP m3 additionally SIGSEGVs on it with empty output. **Not diagnosed here; not
SEQ-ERAD's problem.** Same family as FINDING-2026-08-01c (two demo artifacts frozen on a duplicate label).
It also holds **14 of the 32** foreign-ω events — nearly half the class lives in the destination program.

## Result 6 — process note: the instrument was already written and throwing its answer away

The fence at `emit.cpp:2432` **computes the collision pair and discards it.** SE-1 cost one `fprintf` in a
branch that already had every value in scope. Three sessions reasoned about which of two hypotheses explained
the 26 while the compiler was in a position to answer it directly, for free, at any point.

**Deleted this session:** `corpus/probe/bb/test_sno_5.c` + `test_sno_6.c` (the DDS-1 R12 frame-pointer goldens
— 5's thesis retired by 6 on 2026-06-23; both superseded by `test_sno_cell_5.s`, a month newer, oracle-verified,
carrying the surviving idea as a call unit rather than a frame pointer) and the tracked
`SCRIP/src/templates/bb_match_sequence.cpp.bak`.

⚠ **Dangling reference repointed:** the LIVE CURSOR's ruling-#2 text named *"the `test_sno_5/6.c` model"*.
Ruling #2 is now **dissolved rather than answered** — both its options assumed the DAG is real.
