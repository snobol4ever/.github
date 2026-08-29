# FINDING — the by-name generator resume-cell defect (`rt_call_arr_gen` inside `rt_jmp_frame_lexprep2`'s
# wiped region) is not limited to `between/3`-style generators or `$dyn_iter`. 5 more independent witnesses,
# all ASM-confirmed to route through the same two functions, show the identical first-solution-only
# signature through `bagof/3`, `findall/3`, `clause/2` reflection, and PLAIN multi-clause dynamic-predicate
# backtracking with no generator/aggregation builtin at all.

**seat03 · 2026-08-29 · row `tests-consolidate-prolog`** (widens the blast radius hq_P's
`FINDING-2026-08-29-hq_P-prolog-generator-resume-cell-lives-inside-lexprep2-cleared-frame-region.md`
already root-caused; extends the chain-of-custody entry in `prolog-backtracking-yields-first-solution-only`'s
own ledger, which asked *"is the blast radius bigger than three builtins?"* and had so far answered yes for
one additional witness, `$dyn_iter`/`abolish_then_reassert`.)

**Not fixed — diagnosis only, corroborating an already-owned defect. Nothing committed to SCRIP or corpus.**
The cure belongs to `prolog-pz4-gamma-retain-activation-frames` (owner `hq_C`,
`PARKED-AWAITING:icon-n2-generator-activation-frames`). This row's own current `## NEXT` (item 5) named
these 5 files as "the ~6-7 remaining SCRIP-DIFF files... still need individual ASM-diffs, don't guess from
text" — this FINDING is that ASM-diff, and the answer is they are not independent SCRIP-DIFF bugs.

## 0. Answer

**All 5 of this row's remaining "SCRIP-DIFF" candidates are more witnesses of the one defect, not five new
bugs.** Method: for each of the 5 loose files whose `scrip --run` output disagrees with its own pre-existing
`.expected` pin, (a) compared actual vs. expected content, (b) compiled with `--compile` and grepped the
emitted `.s` for calls to `rt_call_arr_gen` and `rt_jmp_frame_lexprep2`, (c) spot-checked m4 (compile+link)
actual output against m3 for 3 of the 5.

| file | construct | expected | scrip actual (m3 == m4 where checked) | `rt_call_arr_gen` calls | `rt_jmp_frame_lexprep2` calls |
|---|---|---|---|---|---|
| `rung14_retract_retract_basic.pl` | plain dynamic-predicate backtrack (`color(X)`, no builtin) | `red\nblue` | `red` | 1 | 1 |
| `rung14_retract_retract_mixed.pl` | plain dynamic-predicate backtrack (`fact(X)`) | `1\n3` | `1` | 1 | 1 |
| `rung44_setof_group.pl` | `bagof/3` + fail-loop | `5-[tom]\n7-[peter]\n8-[pat]\n11-[ann,sue]\ndone` | `5-[tom]` (rc=1, second `main/0` clause never tried) | 1 | 2 |
| `rung45_reflect_clause_facts.pl` | `clause/2` reflection + fail-loop | `red true\ngreen true\nblue true` | `red true` | 2 | 3 |
| `rung45_reflect_clause_findall.pl` | `findall/3` over `clause/2` | `[a,b,c]` | `[a]` | 2 | 3 |

Every one truncates after exactly the first solution — the identical signature hq_P's FINDING already named
("first solution survives, every later one is gone") — and every one's own emitted assembly calls both
functions the root-cause FINDING identifies. This is not a coincidence of similar symptoms; it is the same
mechanism, measured, not pattern-matched (the discipline this row's own §4 correction insists on: overlap,
not occurrence — here confirmed by presence of the actual calls in each file's own codegen, not by symptom
resemblance alone).

## 1. Why this widens the known blast radius specifically

The chain so far (per `prolog-backtracking-yields-first-solution-only`'s ledger) confirmed: `between/3`,
GNU Prolog's `for/3`, `current_stream/1`'s enumeration form, and `$dyn_iter` (one plain `assertz`'d predicate,
`abolish_then_reassert`, mid-clause `assertz` immediately before a same-clause backtrack). All four are named
generator-style dispatch through `rt_call_arr_gen`.

**`rung14_retract_retract_basic`/`_mixed` are a materially different shape from any prior witness**: no
`abolish`, no in-body `assertz` timing trick, no aggregation builtin — just `retract/1` followed by an
ordinary `Name(X), write(X), nl, fail` loop over what is left of a 2-or-3-fact dynamic predicate. If this
still routes through `rt_call_arr_gen`, then **any** call to a dynamic (`assertz`'d) predicate that yields
more than one solution under backtracking is affected, not merely predicates touched by `assertz`/`abolish`
in the same clause. That is confirmed here: both do.

**`rung44_setof_group` (`bagof/3`) and `rung45_reflect_clause_*` (`clause/2`, `findall/3`) are the first
confirmed instances of aggregation/reflection builtins sharing the mechanism** — previously only
enumeration-style generators (`between`, `for`, `current_stream`) and `$dyn_iter` were confirmed. `bagof`'s
own internal grouping-and-backtrack presumably lowers through the same by-name dispatch path as the simpler
generators; `clause/2` used as a `fail`-loop generator (both directly and via `findall/3`) does too.

## 2. `rung44_setof_group`'s own shape is worth flagging separately

Unlike the other 4 (which have a single `main/0` clause and just print fewer lines than expected), this
file's `main/0` has **two clauses** — the `bagof`+fail loop, and a fallback `main :- write(done), nl.` that
should run once the loop is exhausted. Actual output is `5-[tom]` and **nothing else** (rc=1) — the fallback
clause is never reached. This is consistent with the generator defect making the `bagof` call appear to fail
*permanently* (rather than backtracking for the next group) the moment the first group's cell is clobbered,
which then fails the first `main/0` clause as a whole and *should* fall through to the second clause under
ordinary Prolog clause resolution — but does not. Not investigated further here (would need its own ASM/gdb
session and is still downstream of the same un-cured defect either way); flagging so whoever eventually cures
`prolog-pz4-gamma-retain-activation-frames` has this as an extra corpus witness with a slightly different
failure shape (silent non-fallback, not just silent truncation).

## 3. m3/m4 agreement, where checked

Spot-checked 3 of the 5 (`retract_retract_basic`, `reflect_clause_findall`, `setof_group`) under m4
(`--compile` + link against `libscrip_rt.so`): identical truncated output and identical rc to m3 in all 3.
No m3/m4 divergence observed for this specific witness set (unlike the row's separately-flagged concern
about `sm_interp_run` silently dropping conjunction goals — not reproduced here; these 3 all reproduce
consistently in both modes, consistent with the defect living in shared runtime, `rt.c`/`by_name_dispatch.c`,
not in the m3-only interpreter).

## 4. Reproduce

```
cd corpus/tests/prolog
/home/claude03/SCRIP/scrip --run rung14_retract_retract_basic.pl < /dev/null   # prints "red", rc=1
/home/claude03/SCRIP/scrip --compile rung14_retract_retract_basic.pl < /dev/null | grep -c rt_call_arr_gen   # 1
```

## 5. State

- Trees measured: SCRIP `358a88d6`, corpus `a37491bd`, `.github` `a63c19d9`; built via `make -j4 scrip &&
  make libscrip_rt` (not `make pristine` — investigative, no gate verdict claimed), `RT_OPT=-O0` (default).
- Row gate **unchanged** (no conversions possible for these 5 — they are not this row's to fix, matching
  every prior session's precedent for PZ-4/generator-family files):
  `total: 156  converted: 100  loose: 56`, `loose-but-undeclared: 49`, rc=1.
- Both external blockers re-checked fresh via `QUEUE.tsv` (not assumed) and **still unmoved**:
  `icon-n2-generator-activation-frames` `ASSIGNED:ceo` (not DONE), `prolog-pz4-gamma-retain-activation-frames`
  `PARKED-AWAITING` it.
- Mailed to `hq_C` (this row's standing convention for runtime-bug findings) and the 5 file names + this
  finding added to `prolog-backtracking-yields-first-solution-only`'s own ledger context (that row's DONE-WHEN
  already asks whether the blast radius exceeds "three builtins" — it does, and now includes aggregation,
  reflection, and plain dynamic-predicate backtracking with no special builtin at all).
