# FINDING 2026-09-06 hq_C — all 240 swi_tests exclusions name OUR OWN COMPILER as the reason, so failing a program is what removes it from the denominator

**Rows:** THE PACKAGE LOCKDOWN (Lon 2026-09-06: *"Fix the never graded business"*) ·
`prolog-swi-class-ref-coverage-9-of-249-swi-tests-files` · `prolog-swi-tests-refs-were-cut-through-a-shim-...`
**Tree:** corpus `b06b6ecd6`, oracle `/usr/bin/swipl` 9.0.4, measured by
`test_prolog_swi_suite.sh --census-packages`.

## The claim

`corpus/packages/prolog/swi_tests/EXCLUDED.md` names **240** programs as not graded. **Every single one gives a
SCRIP-side reason. Not one gives an oracle-side reason.**

```
$ grep -c '^- ' EXCLUDED.md                          -> 240
$ grep '^- ' EXCLUDED.md | grep -ci 'scrip'          -> 240
$ grep '^- ' EXCLUDED.md | grep -ci 'swipl'          ->   0
```

Typical entries — the reason is always what *we* cannot do:

```
- GC/test_agc_copyterm.pl: scrip produces zero PASS/FAIL/EMPTY lines for this file today (rung 10 incomplete)
- GC/test_ch_shift.pl: ... -- GC/test_ch_shift.pl:48: parse error: expected . at end of fact
```

⛔ **A program excluded because SCRIP fails it is a RED that has been moved out of the denominator.** The score
cannot fall when we fail, because failing is the thing that removes the entry from the population being scored.
That is *the never-graded business* in its exact form.

## What the ORACLE actually says

Of **170** shipped files declaring a `begin_tests/1` unit, the oracle can grade **165**. **Five** are genuinely
ungradable, and every one of the five is ungradable *for an oracle-side reason*:

| file | oracle |
|---|---|
| `test_string.pl` | rc=134 — swipl aborts in `./src/os/pl-ctype.c:606` |
| `core/test_string.pl` | rc=134 — same abort |
| `tabling/test_tabled_shortest_path.pl` | rc=139 SIGSEGV |
| `tabling/test_trie.pl` | rc=139 SIGSEGV |
| `thread/test_rwlocks.pl` | rc=124 timeout, after an ERROR at `:39` |

**So the legitimate ungradable set is 5, and the recorded excluded set is 240.**

## Population census (the denominator this suite should have)

```
CENSUS inventory: shipped=170 loadable=165 ungradable=5 units-declared=429
157 of the loadable files ship with NO .ref at all
```

Against what the suite grades today: **9 files**. And the runner never notices the other 161 —
`test_prolog_swi_suite.sh` builds `ref="$SWIT/${base}.ref"` and does a bare `[ -f "$ref" ] || continue`, so
**a shipped program with no ref is not red, not skipped, and not counted: it never existed.** (hq_T reached
this same runner line independently this sitting, from the denominator side.)

## ⭐ The shape

**An exclusion list is a denominator edit, and it must therefore be justified from the ORACLE's side only.**
"Our compiler cannot do this yet" is a statement about the *subject under test*; admitting it as grounds for
exclusion lets the subject choose its own population. The invariant worth stating: **a program leaves the
denominator only when the ORACLE cannot produce an answer for it — never when we cannot match the answer.**

⛔ And the failure is self-concealing in the direction that matters: each entry is individually *honest and
well-documented* — it names the file, the rung, and the exact error. Two hundred and forty carefully written,
individually true notes compose into a denominator that cannot fall. **Diligence at the entry level is what
makes the aggregate invisible**, which is the same mechanism as a message that rules out one confound reading
as a message that ruled out the confounds.

## Reconciliation note (two censuses, one subject)

hq_T reported `shipped=76` this sitting; this census reports `shipped=170`. Both are correct for their own
definition and neither is wrong — the populations differ (`170` = every `.pl` under `swi_tests` declaring
`begin_tests(`; the smaller counts are residues of `test_*.pl` naming and of the exclusion list itself). ⚠ This
is the same class hq_T raised one level up the same day — *two runners writing one cell over two populations* —
and it is recorded here rather than resolved by picking, because **which population is THE denominator is a
lockdown ruling, not a measurement.** The census prints its definition beside its number for exactly this
reason.

## Cure direction (not landed here)

1. **Re-derive `EXCLUDED.md` from the oracle.** On this measurement it should hold 5 entries, not 240.
2. Everything else that ships becomes part of the denominator, graded by `util_swi_cut_refs.sh` (the one
   cutter), and reads RED until SCRIP can match it. **The board goes down. That is the correct direction** —
   the same direction the swi cell moved when its refs were fixed.
3. The runner's `[ -f "$ref" ] || continue` must count a missing ref as ungraded, never as absent.
