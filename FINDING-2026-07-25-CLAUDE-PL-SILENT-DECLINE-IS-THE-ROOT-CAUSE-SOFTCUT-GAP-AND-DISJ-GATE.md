# FINDING 2026-07-25 — PL: SILENT LOWER-TIME DECLINE IS THE ROOT CAUSE; `*->` GAP; `$disj` GATE CLOSED

Session: GOAL-PROLOG-BB orientation + gate repair. Pristine HEAD at session start: `04eeaa8f`.
Landed: `6ba5eaec` (gate allowlist, one file). Oracles consulted: `refs/gprolog-master`,
`refs/swipl-devel-master` (uploaded archives, per RULES.md CONSULT CANONICAL SOURCES).

---

## 1. ⛔ ROOT CAUSE — AN UNRECOGNIZED BODY GOAL FAILS SILENTLY ON EVERY CHANNEL

This is the headline. A clause whose body contains a goal the lowerer does not recognize is
**declined at lower time**; the predicate is then effectively clause-less and simply FAILS at
runtime — with **no diagnostic on stdout, stderr, or the exit code**.

Repro (`/tmp/declined.pl`):
```prolog
:- initialization(main, main).
p :- totally_unknown_thing(1).
main :- ( p -> write(yes) ; write(no) ), nl.
```
`--run` → `rc=0`, stdout `no`, **stderr EMPTY**.

Why this is a defect and not a policy choice — three facts that contradict each other in-tree:
1. `src/runtime/unification.c:1425` declares the ISO default: `{ "unknown", 1, "error", 0, 0 }`.
2. The ISO throw machinery EXISTS and is wired: `rt_call_proc_descr` (`src/runtime/rt/rt.c:608`)
   does `rt_pl_iso_throw_existence_key(name)` and prints `[GZ-10] ... has no stackless slab`.
3. Neither fires, because the failure happens **before emission** — the call never reaches
   `rt_call_proc_descr`. The lower-time whitelist (`pl_gz_rule_body_goal_ok` /
   `pl_gz_rule_clause` in `scrip.c`) declines the clause first, and the decline is mute.

`resolve_throw_existence_error_procedure` (`src/parser/prolog/pl_resolve.h:12`) is **declared and
never called anywhere in `src/`** — dead.

**Consequence.** Every unimplemented construct degrades to a WRONG ANSWER instead of a loud error.
This is the unifying explanation for the "silent no-output, rc=0" symptom class (see §3). It also
means the corpus pass-rate is a weaker signal than it looks: a construct can be entirely missing
and the only evidence is a diff mismatch, with nothing naming the cause.

**Proposed rung PL-DECLINE-LOUD:** make the lower-time decline emit a diagnostic naming the
offending goal + clause (env-gated at minimum, e.g. `SCRIP_PL_DECLINE_WARN=1`), and/or lower an
unrecognized goal to an `existence_error` throw leaf so `unknown=error` is honoured as declared.
Cheap, and it converts a whole class of silent wrongness into mechanical bug reports.

---

## 2. `*->` (SOFT CUT) — PARSED, NEVER LOWERED, AND MIS-CLASSIFIED BY `dj_is_plain`

**Parser is correct.** `src/parser/prolog/prolog_parse.c:70` has `{ "*->", 1050, ASSOC_RIGHT }`.
Confirmed against SWI: `src/pl-op.c:676` → `OP(ATOM_softcut, OP_XFY, 1050)`. Exact match.

**Lowerer has ZERO handling.** `grep '\*->' src/lower/lower_prolog.c` → 0 hits.

**SWI compiles it as a DISTINCT construct**, not as a disjunction and not as hard if-then-else
(`src/pl-comp.c:2312`):
```c
if ( (hard=hasFunctor(*a0, FUNCTOR_ifthen2)) ||  /* A  -> B ; C */
     hasFunctor(*a0, FUNCTOR_softcut2) )         /* A *-> B ; C */
  ...
  Output_2(ci, hard ? C_IFTHENELSE : C_SOFTIF, var, (code)0);
  ci->cut.instruction = hard ? C_LCUT : C_LSCUT;
```
i.e. `C_SOFTIF` + `C_LSCUT` vs `C_IFTHENELSE` + `C_LCUT`.

**SCRIP's guard only excludes the hard arrow.** `dj_is_plain` (`lower_prolog.c`) rejects a `;`
whose left child is `->`, but NOT one whose left child is `*->`. So a soft-cut if-then-else is
classified as a PLAIN disjunction and lifted into a 2-clause aux predicate — which is wrong
independently of §1, because soft-cut must suppress the else branch once the condition has
succeeded at least once, and separate clauses cannot express that.

Observed (`/tmp/softcut.pl`):
```prolog
t1 :- ( member(X,[1,2]) *-> write(X) ; write(none) ), nl, fail.
```
SCRIP prints `none`. ISO/SWI require `1` then `2`. Mechanism = §1 + this: the disjunction is
lifted, clause 1 calls undefined `*->`/2 which silently fails, clause 2 writes `none`.

**Two defects, fix both:** (a) add `*->` to `dj_is_plain`'s exclusion so it is never lifted;
(b) lower it as its own construct. (a) alone converts a silent wrong answer into a clean decline —
worth landing first as it is a one-line guard.

---

## 3. PL-BENCH BENCH-6 IS MIS-ATTRIBUTED — "arity>8" IS NOT THE BLOCKER

GOAL-PROLOG-BB.md attributes bench-6 to `arity>8 (unify-9, reducer-11, simple_analyzer-12,
fast_mu-11/13, nand-13, chat_parser-14)`. Measured, that label is wrong on both halves.

**Arity>8 works.** Direct probe, arity-9 predicate, `--run` → prints `123456789` correctly.

**The four programs fail FIRST on a missing entry point.** reducer / simple_analyzer /
chat_parser / nand all define `top`, none defines `main/0`, none has an `initialization`
directive → `[IBB] FATAL: mode-4 driver: main BB graph not found`. That is a harness convention
gap, not a language gap.

**With an entry shim (`main :- top.`) they split into THREE distinct real blockers:**

| Program | Result with shim |
|---|---|
| reducer | **segfault** (rc=139) |
| nand | **segfault** (rc=139) |
| simple_analyzer | rc=0, **no output** (silent — §1) |
| chat_parser | rc=0, **no output** (silent — §1) |

Recommend re-splitting bench-6 into: BENCH-6a entry-point convention, BENCH-6b segfault
(reducer, nand — monitor-first per RULES.md), BENCH-6c silent decline (= §1).

---

## 4. DISPROVEN SUSPECT — DISJUNCTION LIFTING PASSES A WIDER VAR SET THAN gprolog

Real difference, but NOT the bench-6 arity cause.

- **gprolog** (`src/Pl2Wam/syn_sugar.pl`, `normalize_alts1`) passes only
  `set_inter(VarAlt, VarRestC, V)` — vars shared between the disjunction and the rest of clause.
- **SCRIP** (`dj_collect_vars` in `lower_prolog.c`) passes **every** var in the disjunction
  subtree. Correct but wider.

Measured (temporary instrumentation at the `$disj` mint site, since reverted):
- van Roy benchmarks: 15 mints, **max arity 5** → cannot be bench-6's arity story.
- Prolog corpus (400 programs): 128 mints, **max arity 19**
  (`corpus/programs/prolog/gnu_prolog/Pl2Wam/code_gen.pl`), plus one 9 and three 8s.

So the wider var set DOES reach arity>8 in the corpus, just not on van Roy. Worth fixing on
tidiness grounds; the enclosing clause IS available at the `pl_expand_disjunctions` call site
(it iterates `cl`), it is simply not threaded into `dj_expand_node`, which is why the
intersection cannot currently be computed.

Aside: gprolog uses its own global aux-name counter (`g_read(aux,...)`/`g_assign(aux,...)` with
`(Aux+1) /\ (1<<26 - 1)` wraparound), so a monotonic name counter is structurally ordinary —
supporting §5. (Cited as observable precedent only; PROEBSTING REMAINS THE CANON.)

---

## 5. LANDED — `g_pl_disj_ctr` SANCTIONED, 229-COMMIT SILENT RED CLOSED (`6ba5eaec`)

`scripts/test_gate_pl_no_new_global.sh` FAILed (RC=1) at pristine `04eeaa8f` on `g_pl_disj_ctr`.
Introduced by `762aafc5` (2026-07-19, the cut-free `(A;B;C)` → aux-predicate transform) and never
allowlisted — the same un-listed pre-existing red class as `g_pl_functor_slot_ctr`.

It is a `static int` in `lower_prolog.c` minting `$disj%d` names; the name lands in
`g_stage2.resolve_pred_table` (itself SANCTIONED, compile/emit-time, freed before run). Never read
at runtime, holds no control or value state — not a DESIGN §10 spine. Exact sibling of the
already-SANCTIONED `g_pb_fresh_ctr`. Gate now RC=0; doomed-ratchet unchanged at **14 / floor 14**.

---

## 6. ⚠ ENVIRONMENT ANOMALY — UNOWNED UNCOMMITTED WORK IN THE SANDBOX (NOT MINE, NOT TOUCHED)

Recorded because it affects trust in this session's measurements.

After a clean `git clone` at 15:54:31 (reflog shows exactly one entry, the clone), two artifacts
appeared in the SCRIP working tree that this session did not create:

| Artifact | Content | Created |
|---|---|---|
| `src/templates/bb_call_proc_staged.cpp` (modified, +26/−4) | A complete **PL-GENIDX-1** optimization — emit-time-resolved callee index for the *generator* arm, authored rationale comment dated 2026-07-25, `SCRIP_NO_GENIDX=1` A/B hatch, one-pop-law equivalence argument | mtime **16:05:03** |
| `stash@{0}` "WIP on main: 04eeaa8f" | A different change: `src/parser/prolog/pl_cell.h`, +17/−6 | ref **16:15:27** |

`git log origin/main -S "PL-GENIDX-1"` → no hits, so it is not upstream. No script under
`scripts/` invokes `git stash`. Meanwhile `origin/main` advanced during the session
(`04eeaa8f` → `2de78b10`, ICON PERF BID-2 s160), so a concurrent session appears to be live.

**Actions taken: NONE on either artifact.** The session commit used an explicit pathspec
(`git commit -- scripts/test_gate_pl_no_new_global.sh`) so neither was swept in. Both remain
uncommitted in the working tree. A `git pull --rebase` will be needed before any push, and should
be done by whoever owns that WIP.

**Measurement caveat:** GATE-3 measured **164/164/164** (interp/run/compile) this session, but the
run straddles the 16:05 mtime, so it cannot be cleanly attributed to a pristine tree. Treat 164 as
PROVISIONAL and re-measure on a known-clean checkout before moving the PL-GZ-9 ratchet floor.
GATE-1 ran before 16:05 and is clean: **5/5/5**.

Note the goal file's PL-GZ-9 floor still reads **115** while the suite now runs **164** programs —
stale by 49 regardless of the attribution question.

---

## 7. OTHER GATE STATE (unmodified, reported only)

`scripts/test_gate_bb_one_box.sh` → **RC=1, 35 FAILs**, all Icon `bb_binop_*` boxes
(`bb_binop_arith`, `bb_binop_relop`, `bb_binop_gvar_arith`, missing `bb_binop_gvar_relop`, …).
Pre-existing at pristine HEAD before any edit in this session. Out of Prolog scope — flagged only.

---

## 8. DOC DRIFT SPOTTED

`GOAL-PROLOG-BB.md`'s per-construct port-wiring table names `IR_GCONJ`, `IR_CHOICE`, `IR_GOAL`,
`IR_UNIFY` etc.; of these only `IR_CUT` (and `IR_ITERATE`) appear in `src/contracts/IR.h`. Either
the table is aspirational or the opcodes were renamed — it should not be trusted as a map of the
current tree until reconciled.
