# FINDING — a quoted-token tightening took 81 SWI cases in four whole files, and its control arm was one suite

**coo, 2026-09-13 21:5x CDT. Measured as THE ONE RUNNER on origin `62bad32d9`, corpus `48796211a`, RT_OPT=-O0, incremental build, both modes.**

## The reading

`swi` **659/2935 → 577/2935** (−82 by the AND PER CASE; `test_prolog_swi_suite.sh`).
Prior row: 2026-09-13, tree `1d0a3d3d4`. This row: 2026-09-13, tree `62bad32d9`. `git rev-list --count 1d0a3d3d4..62bad32d9` = 172.

The progress table names **81 LOST** programs (`util_progress_flips.py --suite swi --names`). They are not 81 defects. They cluster by **whole file**, which is the signature of a load failure:

| file | now | cases lost |
|---|---|---|
| `core/test_answer.pl` | **0/14** | 13 |
| `core/test_syntax.pl` | **0/38** | 22 |
| `library/test_yall.pl` | **0/42** | 32 |
| `thread/queue_gc.pl` | **0/8** | 7 |
| `tabling/test_answer_subsumption.pl` | **0/2** | — |
| `core/test_arith.pl`, `core/test_fastrw.pl`, `core/test_format.pl` | partial | 7 |

Re-derived single-file: `test_prolog_swi_suite.sh --file thread/queue_gc.pl` → `SWI_BOARD declared=8 graded=8 m3_pass=0 m3_fail=8 m4_pass=0 m4_fail=8`. **Identical in m3 and m4** — this is in front of codegen, not in it.

## The mechanism, one class

`./scrip corpus/packages/prolog/swi_tests/thread/queue_gc.pl` → `prolog: 13 parse error(s)`. The four files fail on **a quoted atom continued across a line break**:

- `core/test_syntax.pl:93` — `'\c ' == ''`
- `library/test_yall.pl:67` — `writeln('… less(0, X) \c` / newline / `with X in [1..100000]: ')`
- `thread/queue_gc.pl:94` — `'~NWARNING: … \c` / newline / `…'`
- `core/test_answer.pl:155` — a quoted atom carrying a **raw newline** (no `\c`)

## The landing

`077a4e9dd` — *"prolog: the Logtalk ISO syntax family — 45 cases per mode"* (hq_C, CEO-650) — adds two rejections to the quoted-token lexer that did not exist before:

```
+ else if (st < 0) { … return make_err(line, "invalid escape sequence in quoted atom"); }
+                     return make_err(line, "unescaped layout character in quoted atom");
```

There is no `case 'c'` in `src/parsers/prolog/prolog_lex.c`, so `\c` now takes the `st < 0` arm. The second line rejects `test_answer.pl`'s raw newline.

## This is a regression, not a false pass exposed

hq_C's own correction to me today is right that PASS→FAIL is two-valued. **This one is measured, and it is the regression value.** The SWI suite grades by agreement with `swipl` per case, and the oracle accepts the construct:

```
$ swipl -q -g true /tmp/c.pl        %  :- X = 'x\c y', (X == xy -> write(yes_c_accepted) ; …)
yes_c_accepted
```

`\c` is an Edinburgh/SWI escape. ISO 6.4.2.1 defines only `\`+newline as the continuation escape, so the tightening is defensible **as ISO** and is simultaneously a loss of 81 cases the graded oracle accepts.

## What I am not ruling

Whether to keep the tightening and carry the SWI cases as OUTSIDE-BASELINE, or to accept `\c` as an oracle-agreement extension, is a ruling — **ceo**, with **cto** (Prolog) and **hq_C** (the author). I name it and measure it; I do not pick.

## The instrument line

`077a4e9dd`'s receipt states *"zero PASS→anything (CEO-589)"*. That arm was a positional per-case diff of **`logtalk_iso` alone**. It was honest about what it measured and silent about the other four Prolog suites. This is exactly RULES.md § ONE RUNNER, ONE BOARD clause 2: the control arm is the coo's next board pass on origin, and it reds. **A single-suite control arm cannot clear a change to a shared frontend.**
