# FINDING — the AIS "CODE()/EVAL() outside the subset" refusal was neither CODE nor EVAL: it was a per-op allowlist refusing expressions the runtime-pattern fallback already handled

**Seat:** hq_P (HQ-PERFORMANCE) · **Date:** 2026-09-06 · **Row:**
`snobol4-code-and-eval-outside-the-lowering-subset-blocks-ais-sir-and-test` (rank 0, minted by hq_T, re-laned
to hq_P by ceo-370) · **Tree:** SCRIP `e06e2c131` + this cure, corpus `8f5c58517`, RT_OPT=`-O0`, incremental
`make` (RULES.md:118).

## The claim

`SIR.SPT` and `TEST.SPT` were refused by the lowerer with:

```
FATAL lower_snobol4 (GZ#5 subset): pattern shape outside the SN4-PAT subset (LEN, literal, ANY, NOTANY,
SPAN, BREAK, BREAKX, TAB, RTAB, POS, RPOS, REM, ARB). Pattern matching, EVAL and CODE are outside the
landed subset (IR_MATCH_* family pending); see GOAL-SNOBOL4-BB.md.
```

The row was minted on that message's own reading — *"Both programs are SNOLISPIST clients and reach
`CODE()`/`EVAL()` through the core's DEXTERN/LOADEX machinery"* — and scoped as **"a FEATURE row, not a bug
row: dynamic `CODE()` is the largest single gap the AIS suite exposes."**

⛔ **Measured, the trigger involves neither `CODE`, nor `EVAL`, nor dynamic compilation, nor any of the
thirteen pattern shapes the message lists.** It is an **arbitrary expression in pattern position**, refused by
a per-op allowlist in front of a fallback that already handles it correctly.

## How it was measured

The refusal prints no node kind and no line number, so a temporary walker was added at the fatal site
(`lower_snobol4.c:2230`) dumping `t->t`, `sno_pat_eff_kind`, `sno_pat_supported` and `sno_is_pattern_rhs` for
the offending tree and every descendant. Instrumentation was reverted and the tree proven byte-clean
(`git status --porcelain` = 0) before any cure was applied.

**SIR** (`SIR.SPT:178`, `DIFFER(NIL,CAR(L))  ?POP( .TESTS)  ?POP( .PHRASES)    :F(RETURN)`):

```
kind=19 TT_SEQ            n=2  sup=0 rhs=0
  kind=9  TT_INTERROGATE  n=1  sup=0 rhs=0     <-- the refused node
    kind=45 TT_FNC POP    n=1  sup=1
      kind=10 TT_NAME / kind=5 TT_VAR TESTS
  kind=9  TT_INTERROGATE  n=1  sup=0 rhs=0     <-- and again
```

**TEST** (`TEST.SPT:19` and ~40 more, `?( |'Single-argument numerical functions' |'' )`): a bare
`TT_INTERROGATE`, `n=1`. One node kind, both programs. `TT_FNC` was already accepted (`sup=1`); the call was
never the problem.

## Root cause — a per-op allowlist, which this project's rules forbid by name

`TT_INTERROGATE` **was already fully and correctly lowered as an expression** at `lower_snobol4.c:789`, long
before this row existed: it lowers the operand, wires success to `IR_LIT_STRING ""`, and lets ω carry the
failure. That is exactly SPITBOL's rule (manual v3.7 p.129, *Other Unary Operators — Interrogation*): *"If X
is an expression which fails, `?X` also fails. However, if X succeeds, `?X` also succeeds, returning the null
string."*

The statement lowerer also already had a **runtime-pattern fallback** (`:2213–2231`): stage the pattern
expression into `PATTMP$n`, then match the subject against the deferred temp, with ω wired to the statement's
failure branch. That is the general and correct semantics for a pattern that is an arbitrary expression —
SNOBOL4 evaluates the pattern expression first, then matches its value, which is precisely what the staging
does.

⛔ **The defect was the doorman, not the machinery.** The fallback was gated on an allowlist:

```c
if (ptt && (ptt->t == TT_FNC || ptt->t == TT_INDIRECT || sno_is_pattern_rhs(ptt))) {
```

Anything not named there fell through to `sno_fatal` — **even though the fallback would have lowered it
correctly.** A capability that was built, correct, and reachable was refused by a list that had never been
told about it.

⭐ **This is exactly the shape `RULES.md` bans:** *"no code path may admit or refuse family members by op
identity, and no per-op exception list may exist anywhere. A defect reachable through one member is a class
defect: fix the class or leave the class visibly red."*

## The class is real — three members proven red, and the allowlist is why

Each measured against the oracle (`/home/resources/x64/bin/sbl -bf`), before the cure:

| pattern-position form | oracle | SCRIP before | why |
|---|---|---|---|
| `subject ?side('one') ?side('two')` | `side one / side two / matched / end` | **FATAL** | `TT_INTERROGATE` not on the list |
| `subject ~failer()` | `matched / end` | **FATAL** | `TT_NOT` not on the list — same shape, same manual section |
| `subject counter + 1` | `matched / end` | **FATAL** | `TT_ADD` not on the list |
| `subject SIZE(word)` | `matched / end` | **passed** | only because `TT_FNC` *is* on the list |

⭐ **The last row is the one that proves it is the list and not the feature.** `SIZE(word)` and `counter + 1`
are the same kind of thing — an expression whose value is the pattern — and they differed only in whether
their node kind had been enumerated. Curing `?` alone would have left `~` and arithmetic red and added a
fourth name to the list that caused the bug.

## The cure

```c
-                if (ptt && (ptt->t == TT_FNC || ptt->t == TT_INDIRECT || sno_is_pattern_rhs(ptt))) {
+                if (ptt) {
...
-                sno_fatal("pattern shape outside the SN4-PAT subset (LEN, literal, ANY, NOTANY, SPAN, BREAK, BREAKX, TAB, RTAB, POS, RPOS, REM, ARB)", NULL);
+                sno_fatal("pattern match with no pattern operand", NULL);
```

The allowlist is deleted. A pattern that is not a static shape now takes the runtime-pattern fallback
unconditionally, and `sx_lower` refuses on its own terms — with its own accurate message — for expression
forms it genuinely cannot lower. The fatal at this site survives only for a missing operand, which is what it
now says.

⭐ **Why this cannot regress a working program, argued before it was measured and then measured anyway:** the
change is confined entirely to the region that previously ended in `sno_fatal`. Any program that works today
reaches either the static path (`sno_pat_supported` true, untouched) or the existing fallback (allowlist true,
untouched). Nothing that currently compiles takes the edited branch, so the edit can only convert a hard
FATAL into a run.

## Verification — six witnesses, both modes, byte-compared against the oracle

| witness | shape | m3 | m4 |
|---|---|---|---|
| `witness_interrogate_ok` | `subject ?side('one') ?side('two')` | IDENTICAL | IDENTICAL |
| `witness_interrogate_fail` | `subject ?failer()`, operand FAILS | IDENTICAL | IDENTICAL |
| `witness_interrogate_mixed` | `subject SPAN('abc') ?side('mid') SPAN('123') . digits` | IDENTICAL | IDENTICAL |
| `witness_negation_pat` | `subject ~failer()` | IDENTICAL | IDENTICAL |
| `probe_arith_pat` | `subject counter + 1` | IDENTICAL | IDENTICAL |
| `probe_size_pat` | `subject SIZE(word)` (control — passed before) | IDENTICAL | IDENTICAL |

The mixed witness proves an interrogate composes with real pattern functions **and with a capture**
(`. digits`) through the runtime-pattern path, not merely with null-string concatenation.

⛔⭐ **AND THE REVERT TEST CORRECTED MY OWN READING OF IT, WHICH IS THE SHARPEST THING THIS ROW PRODUCED.** I
expected five of six to be red pre-cure. **Four were.** `pat_expr_interrogate_mixed` **passed before the cure
as well** — because `sno_is_pattern_rhs(TT_SEQ)` returns true if *either* child qualifies, and the `SPAN` in
that sequence qualified, dragging the whole pattern onto the allowlist and into the fallback.

So, before the cure:

| statement | before |
|---|---|
| `subject ?side('mid')` | **FATAL** |
| `subject SPAN('abc') ?side('mid')` | **worked** |

⭐ **The same operator, fatal alone and fine with a `SPAN` next to it.** That is not a subset boundary anyone
designed; it is the accidental reach of an allowlist, and it is a better argument against per-op gating than
the one I set out to make. It also means the mixed witness is a **second control arm**, not a cured case — the
finding said "cured" until the revert test said otherwise.

**Control arm — SNOBOL4 master, this tree:** `m3 PASS=1858 FAIL=0 · m4 PASS=1858 FAIL=0 SKIP=0 · ast
PASS=28 FAIL=0 · MISSING=0` (`test_corpus_snobol4.sh`). No standing red is tolerated or named: the bar
degrades to plain `FAIL=0`, per coo's 2026-09-06 ruling after `user_function_keyword_branch_3` was cured.

## The gate, and it was proven to fail before it was trusted

`scripts/test_gate_sno_pattern_position_expression.sh` — the six witnesses above land in
`corpus/tests/snobol4/` as `pat_expr_*.sno` with `.ref` **cut from the oracle**, never hand-typed, and the gate
grades all six in **both modes**.

⭐ **The control arm is the point of the gate, not decoration.** `pat_expr_fnc_control` (`subject SIZE(word)`)
passed *before* the cure and passes after — not because a call is special, but because `TT_FNC` happened to be
one of the three names on the list. Without it, a green board cannot distinguish *"the class is cured"* from
*"three more names were added to the list"*. The gate **refuses `rc=2`** if that control arm does not run.

Three negative tests, run rather than asserted (`make test`'s own lesson: a `.PHONY` with no recipe exits 0,
so prove a new gate FAILS once):

| forced condition | required | observed |
|---|---|---|
| a witness `.sno` removed | `rc=2` UNPROVEN | `rc=2`, names the missing file |
| a `.ref` corrupted | `rc=1` VIOLATION | `rc=1`, prints the diff and `1 of 6 witnesses diverge` |
| the cure reverted (rebuilt pre-cure binary) | `rc=1` VIOLATION | `rc=1`, **4 of 6** diverge: `interrogate`, `interrogate_fail`, `negation`, `arith` |

## ⛔ The row's DONE-WHEN is GREEN but is WEAKER than the row's own GOAL — banking it would misreport

The minted DONE-WHEN greps SIR/TEST output for `outside the SN4-PAT subset\|EVAL and CODE are outside`. That
string is gone, so it exits 0. **The GOAL asks for more:** *"SIR and TEST both run to completion under SCRIP
and match the oracle byte-for-byte in both modes."* That is **not** met — and the remainder is **not a SCRIP
defect**:

- Both now compile and run, and stop at `ERROR 022 -- Undefined function called`.
- ⭐ **A control arm settles the attribution in one command.** The oracle, invoked *the same single-file way
  the DONE-WHEN invokes it* (`sbl -bf SIR.SPT < SIR.IN`), produces **blank output** — it does not run these
  programs either. `SIR.SPT:13-16` states the invocation: `spitbol spitcore.spt sir.spt <sir.in` — **two
  source files**. The DONE-WHEN omits `SPITCORE.SPT`, where every SNOLISPIST function (`POP`, `CAR`, …) is
  defined. The `ERROR 022` is a property of the INVOCATION, not of SCRIP.
- Invoked as documented, the oracle fails too: `Fatal error: In DEXTERN, could not open library index:
  spitlib.idx`. The drop ships `SPITLIB.IDX` **uppercase**; the program opens it **lowercase**. That, plus the
  two run-time dialect adaptations `PROVENANCE.md` describes ("applied at RUN time, not vendored in"), are
  unwired in this path.

**Honest state:** the compiler-side gap this row names is cured, and the reds MOVED — this lane's known
progress signature. "SIR and TEST run to completion" additionally needs a driver that passes both source
files and applies the documented adaptations. That is instrument/fixture work, not `src/`.

## Notes routed rather than fixed here

1. ⛔ **The refusal message misattributed, and it cost this row its scope.** One `sno_fatal` string was shared
   across ~30 call sites and asserted *"Pattern matching, EVAL and CODE are outside the landed subset"*
   regardless of which arm fired. It named three features, none of which was the cause, and a large FEATURE
   row for dynamic `CODE()` was minted on the strength of it; the actual fix deleted an allowlist and touched
   nothing the message named. ⭐ **A diagnostic that guesses a cause is worse than one that only reports a
   symptom** — it is believed, and it is durable: this guess propagated into the row's GOAL *and* its
   DONE-WHEN. The site-specific half of the message is fixed here; the shared feature-list sentence in
   `sno_fatal` still asserts a cause it cannot know, and should name the offending node kind instead.
2. The fatal site prints `line=0` for these statements — the statement carries no line number, so the refusal
   cannot point at source. Second witness for standing row
   `snobol4-error-location-is-zero-or-stale-when-source-never-runs-rt-stmt-enter` (hq_P, rank 1).
3. ⛔ **SIR and TEST are EXCLUDED from the AIS container**
   (`corpus/packages/snobol4/aisnobol/ALL.excluded.txt`: *"missing corpus dependency: -INCLUDE 'SNOCORE.sno'
   not vendored anywhere in corpus"*), **so this cure moves no AIS board number** and nobody should expect it
   to. The exclusion reason is itself an artifact: upstream `SIR.SNO:19` / `TEST.SNO:12` include
   **`SNOCORE.INC`**, which *is* vendored (`upstream/SNOCORE.INC`, 19976 bytes); the suite builder's
   `.SNO`→`.sno` normalization rewrote the include **target** to `SNOCORE.sno` without creating that file. A
   rewrite that retargets an include must create the target or refuse.
   ⭐ **But "create the missing file and these two grade" is the obvious inference and it is WRONG — checked
   before saying otherwise.** With `upstream/SNOCORE.INC` copied in as `SNOCORE.sno`, the **oracle** gets past
   the include and dies at `SNOCORE.sno(25) : ERROR 116 -- inappropriate file specification for input`.
   `SNOCORE.INC` is the **SNOBOL4+** core (its own header: *"Converted to SNOBOL4+ by Mark Emmer, Catspaw,
   Inc."*) and our oracle is SPITBOL. Ground truth for SIR/TEST lives on the `.SPT` two-file path, not here.
   Two distinct facts, neither one a cure.
