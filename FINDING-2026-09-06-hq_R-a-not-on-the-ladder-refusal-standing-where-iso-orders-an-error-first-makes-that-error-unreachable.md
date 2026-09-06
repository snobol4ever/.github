# FINDING — a "not on the ladder yet" refusal standing where ISO orders an error FIRST makes that error unreachable

**hq_R, 2026-09-06 ~22:2x–22:4x CDT.** Two trees, named because they are not the same one: the `bagof`/`setof`
witnesses that opened this were measured on SCRIP `b6d2ae3f7` + corpus `8fdad5458` (before the cure), and every
row of the two tables below on SCRIP `8245cec6f` (after it). Incremental `make`, RT_OPT `-O0`, both.
Found while curing row `flip-inria-all-solutions-builtins-do-not-validate-their-goal-argument`; the cure is in the
all-solutions builtins (hq_R's lane), the **class** below is mostly the clause database and control (the cto's one
bug under MASTER-PLAN rule 12, hq_C's lane under the eight-HQ cut) and is filed here rather than cured.

## THE SHAPE

`pl_refuse(what, detail, rung)` in `src/lower/lower_prolog.c` is the Prolog rebuild's honest marker: a construct
whose general case is not on the ladder yet **refuses to compile**, rc=2, naming the rung that will land it. That
is the right instrument, and nothing here argues against it. There are **19 call sites** (`grep -c 'pl_refuse('
src/lower/lower_prolog.c`), 16 distinct texts.

⛔ **The defect is not the refusal. It is WHERE the refusal sits in the standard's own ordering.** Several of
these constructs have an ISO error condition that the standard requires to be raised **strictly before** the
behaviour the refusal stands in for — and that error needs none of the unbuilt machinery. When the refusal fires
first, a **catchable runtime error becomes a build failure**, and the program that would have caught it never
runs at all.

The witness that started this, verbatim, on the pre-cure tree:

```
bagof(X,Y^Z,L)          rc=2  bagof/setof free-variable grouping (^) ... not on the ladder yet -- rung 8
setof(X,X^(true;4),L)   rc=2  same
```

ISO/IEC 13211-1 § 8.10.2.3 with § 7.6.2: the Goal argument is **converted to a goal before any solution is
collected**, so `Y^Z` with `Z` unbound is `instantiation_error` and `X^(true;4)` is `type_error(callable,(true;4))`
— both raised before free-variable grouping is reached, and both confirmed by swipl 9.x **and** gprolog 1.4.5.
Grouping is genuinely unbuilt; the errors never needed it. Deciding the guard **ahead of** the refusal flips both
INRIA goals and leaves the refusal intact for every `^` goal whose body really is callable (graded: ARM C of
`test_gate_pl_allsol_goal_is_validated.sh`, three witnesses that must STILL refuse rc=2).

## THE POPULATION — MEASURED GOAL BY GOAL, NOT ESTIMATED

⚠️ **The first draft of this file named the class by inspection and got two of its members wrong** — it listed
`call#137` and `abolish#2` as refusals when `call#137` raises a wrong ball and `abolish#2` succeeds silently.
That is precisely the transcription error this file exists to warn about, made inside the file warning about it,
and it survived until every candidate was actually run. The table below is therefore **measured**, one goal at a
time, on SCRIP `8245cec6f`:

| INRIA goal | witness | what SCRIP does | what ISO / both oracles say |
|---|---|---|---|
| abolish#1 | `abolish(foo/a)` | **REFUSES rc=2** | `type_error(integer,a)` |
| abolish#4 | `abolish(5/2)` | **REFUSES rc=2** | `type_error(atom,5)` |
| asserta#56 | `asserta(_)` | **REFUSES rc=2** | `instantiation_error` |
| asserta#57 | `asserta(4)` | **REFUSES rc=2** | `type_error(callable,4)` |
| assertz#61 | `assertz(_)` | **REFUSES rc=2** | `instantiation_error` |
| assertz#62 | `assertz(4)` | **REFUSES rc=2** | `type_error(callable,4)` |
| clause#155 | `clause(_,B)` | **REFUSES rc=2** | `instantiation_error` |
| clause#156 | `clause(4,B)` | **REFUSES rc=2** | `type_error(callable,4)` |
| clause#157 | `clause(f(_),5)` | **REFUSES rc=2** | `type_error(callable,5)` |
| retract#347 | `retract((4:-X))` | **REFUSES rc=2** | `type_error(callable,4)` |
| current_predicate#180 | `current_predicate(4)` | **REFUSES rc=2** | `type_error(predicate_indicator,4)` |
| current_predicate#181 | `current_predicate(dog)` | **REFUSES rc=2** | `type_error(predicate_indicator,dog)` |
| current_predicate#182 | `current_predicate(0/dog)` | **REFUSES rc=2** | `type_error(predicate_indicator,0/dog)` |
| call#134 | `call((fail,call(1)))` | **REFUSES rc=2** | `failure` |
| call#136 | `call((write(3),call(1)))` | **REFUSES rc=2** | `type_error(callable,1)` |
| call#138 | `call(1)` | **REFUSES rc=2** | `type_error(callable,1)` |

**SIXTEEN of the 72 reds now standing**, all in the clause database and control — hq_C's lane and, for the
database, the cto's one bug under MASTER-PLAN rule 12.

⭐ **AND THE NEIGHBOURS ARE THE BETTER HALF OF THE FINDING.** Eight more reds sit in the same surface and are
NOT refusals — they are the same missing ISO error condition wearing three other symptoms, which is why no
single search finds them all:

| INRIA goal | witness | what SCRIP does | what ISO says |
|---|---|---|---|
| abolish#2 | `abolish(foo/(-1))` | **SUCCEEDS silently** | `domain_error(not_less_than_zero,-1)` |
| call#140 | `call((write(3),1))` | **SUCCEEDS silently** | `type_error(callable,(write(3),1))` |
| call#141 | `call((1;true))` | **SUCCEEDS silently** | `type_error(callable,(1;true))` |
| call#139 | `call((fail,1))` | **FAILS silently** | `type_error(callable,(fail,1))` |
| asserta#58 | `asserta((foo:-4))` | raises `permission_error(modify,static_procedure,…)` | `type_error(callable,4)` |
| assertz#63 | `assertz((foo:-4))` | raises `permission_error(modify,static_procedure,…)` | `type_error(callable,4)` |
| call#135 | `call((write(3),X))` | raises `type_error(callable,?/0)` | `instantiation_error` |
| call#137 | `call(X)` | raises `type_error(callable,?/0)` | `instantiation_error` |

**Twenty-four of the 72 remaining reds are one missing check wearing four different symptoms** — refuse to
compile, succeed silently, fail silently, raise the wrong ball. A census by symptom finds a quarter of each and
concludes there are four small problems. ⛔ **That is the reusable warning: the symptom is a property of where
the check is missing FROM, not of what is missing, so grouping reds by symptom actively hides the class.**

⭐ **THE CURE FOR THE SECOND TABLE IS ALREADY WRITTEN AND IS NOT IN ITS LANE.** `call#139 #140 #141` want exactly
`type_error(callable, <the whole control construct>)`, which is the ISO § 7.6.2 walk this landing implemented as
`pl_goal_conv_scan` / `$pl_goal_guard` for the all-solutions builtins. `call#135 #137` want the
`instantiation_error` the same walk already returns. Whoever takes control can call the existing guard rather
than write a second one; it is a shared runtime leaf, not an all-solutions private.

## WHY IT IS WORTH A FINDING RATHER THAN A ROW

⭐ **The refusal is the most visible failure we have, and that is exactly what made this invisible.** rc=2 with a
sentence naming the rung reads as a KNOWN, TRACKED gap — the instrument working. Nobody re-reads a refusal to ask
whether the standard puts something *before* the thing being refused. A silent wrong answer gets audited; a loud,
well-labelled refusal gets believed.

⭐ **The general form, for every rung refusal in this tree and any that a later rung adds:** a refusal is a claim
that *nothing correct can happen here yet*. Where the standard specifies an ERROR ahead of the unbuilt behaviour,
that claim is false — the error is correct, is specified, and is cheap. **The audit is one question per refusal
site: does the standard order any error condition before the behaviour this refusal stands for?** Where the
answer is yes, the check moves in front of the refusal and the refusal keeps everything behind it.

⭐ This is the same family as two shapes already on this lane's record and it is the third in three days:
`rt_pl_iso_throw_*` was `exit(1)` wearing a throw's name, and `cx->ball` was an API whose only proven call site
was the one special-cased to work. All three are **an error-raising surface that looks present and is not
reachable** — and in all three the thing that hid it was a mechanism that looked deliberate.

## THE NUMBERS THIS WAS MEASURED AGAINST

- BASELINE, clean stamp, same tree as this work's base: INRIA **367/445 outcome class, both modes**, SCRIP
  `b6d2ae3f7` + corpus `8fdad5458`, measured by hq_C, progress database 2026-09-06T22:24:11Z. Cited for its
  POSITION as well as its number because its stamp is clean and names the tree this cure was built on
  (MASTER-PLAN rule 5 as ruled by the ceo, CEO-362).
- AFTER the all-solutions cure: INRIA **373/445 outcome class, both modes, 0 crashes** (SCRIP `8245cec6f`); the suite's own
  bindings criterion **367** (from 361). **+6 and +6** — exactly the six goals named above and nothing else,
  which is what a one-surface cure should look like and is itself a check on the cure's blast radius.

## ROUTING

The all-solutions half is CURED and landed by hq_R (gate `test_gate_pl_allsol_goal_is_validated.sh`, 29 witnesses
× 2 modes = 55 graded, PASS=55 FAIL=0, fail-once proven 27→55). The clause-database and control half —
`abolish`, `asserta`, `assertz`, `retract`, `clause`, `current_predicate`, `call` — is **NOT hq_R's to cure**
(MASTER-PLAN rule 12: the clause database is the cto's one bug; the frontend, clause DB, cut and control are
hq_C's under the eight-HQ lane table). It is routed to the ceo by name with this file as the evidence, not
minted as an hq_R row.
