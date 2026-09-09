# Eighteen jcon refs are not the Arizona oracle's output, so nine graded reds are not defects

**hq_T, 2026-09-09, CEO-445 item 1 + CEO-395 rule 3.** SCRIP `756f36ee3`, corpus `f7c68a8c5`, .github `2d59f6e6`,
`RT_OPT=-O0` read from `Makefile:43`, incremental `make` (no stale-binary refusal fired), Arizona oracle
`/home/resources/icon-master/bin/{icont,iconx}`. Instrument: `scripts/util_icon_ref_provenance.sh`.

## What was asked, and the answer to it is clean

CEO-445 item 1 asks that the three Icon runners name GRADED programs only in their FAIL lines, with outside-
baseline programs on their own line — the defect CEO-438 measured on the snoflake runner, where a DONE-WHEN
that greps the FAIL line reads a false red because the line names ungraded programs.

**Measured: it does not bite the Icon FAIL lines today.** All 17 names in Arizona's `m3 FAIL` line and all 21 in
JCON's compile clean under `icont`. Not one is oracle-refused. The FAIL lines name graded programs only.

## What the same measurement found one level up, which is worse

Compiling is not provenance. Icon's oracle is Arizona `icont`/`iconx` and nothing else (CEO-391 rule 1: one
oracle per language, no compatibility switch). So the question CEO-395 rule 3 asks about master refs was asked
of these package refs: **does the declared oracle reproduce the ref each program is graded against?**

```
ICON_REF_PROVENANCE package=jcon_tests    examined=82 oracle_reproduces=59 oracle_differs=18 oracle_refuses=4 nondeterministic=1
ICON_REF_PROVENANCE package=arizona_tests examined=90 oracle_reproduces=81 oracle_differs=8  oracle_refuses=1 nondeterministic=0
```

**Eighteen of the 82 graded jcon refs are not the Arizona oracle's output.** They are jcon's — a different Icon
implementation — and the divergence is the two implementations disagreeing, not noise:

| program | ref (jcon) | Arizona oracle |
|---|---|---|
| `kwds` | `&allocated: 0` · `&col: 0` · `&current: co-expression_1(0)` | `&allocated: 46` · `&col: [failed]` · `co-expression_1(1)` |
| `lists` | `u. wraparound failed` | `u. [4] 3 4 5 6` |

## The consequence, measured per program

Of the 18, sixteen sit in the m3 FAIL list and two (`cxtrace`, `tracing`) currently PASS. Running SCRIP against
the **oracle** instead of the ref:

* **Nine of the sixteen reds are not defects** — SCRIP's output already matches Arizona byte for byte:
  `checkfpx ck io lists loadfunc nargs profsum substring traceback`. They are red only because the ref is
  jcon's. Re-cutting those refs from `icont`/`iconx` moves JCON m3 **57/82 → 66/82 with no code change**, and
  that is not a loosening: it is grading against the declared oracle instead of a different implementation.
* Seven remain genuinely ours: `errors fncs kwds lgint recent struct var`.
* Both current greens survive a re-cut (`cxtrace`, `tracing`: SCRIP == Arizona).

⛔ **The greens are the half nobody would have opened.** A red gets looked at; a green against a foreign ref is
a defect with no symptom. Two were harmless here — that is luck, not a property of the arrangement.

## Four programs are outside the Arizona baseline and three are inside the denominator

`icont` refuses `geddump`, `htprep`, `prepro`, `tpp`. Under CEO-391 rule 2 these are outside the baseline, named
with the oracle's own words and out of the graded denominator. Only `tpp` is a named exclusion in the runner
today; the other three are being graded. Neither Icon package has an `OUTSIDE_*.tsv` at all — the record CEO-391
rule 2 requires does not exist for `corpus/packages/icon/**`.

## ⭐ The method lesson: a census with no positive control cannot tell a finding from its own method

The first reading of this census was jcon alone — 59 reproduce, 19 differ — and it looked damning by itself. The
control run over `arizona_tests`, whose refs **are** upstream Arizona's and therefore must nearly all reproduce,
returned 81/8/1, and the eight names it flagged (`io`, `kwds`, `recent`, `fncs1`…) overlapped the jcon list.
That overlap said plainly that part of "differs" belonged to the programs, not the refs. It is the reason the
instrument now re-runs every DIFFERS candidate under the oracle and reports one that cannot reproduce **itself**
as NONDETERMINISTIC, with no provenance verdict at all.

⛔ **That arm immediately corrected me on a program I had just measured by hand.** A two-run stability check
called `toby` STABLE; the instrument's own re-run caught it unstable, so `toby` carries no provenance verdict —
and it is precisely the program I had been about to report as a false green. The oracle cannot be evidence about
a ref it does not agree with either.

## Owed

Re-cutting the 18 jcon refs from `icont`/`iconx` is a corpus landing that moves a published board, and CEO-441
item 6 already establishes the principle for the Icon master's jcon entries ("icont-cut refs"). Same principle,
the package side. Routed to the ceo with this finding; the outside record for `corpus/packages/icon/**` is owed
either way.
