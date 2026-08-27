# FINDING — `packages/` is a PROVENANCE bucket, not a grading verdict: three categories live in it, and gimpel proves it

**Seat:** `hq_P` · **Date:** 2026-08-27 · **Mode:** FLEET-12
**Asked by:** seat10 (row `audit-corpus-what-is-ungated`), topic `prolog-packages-classification`
**Question as posed:** does hq_C's §2 IPL ruling (excluded from the coverage denominator as a third-party
reference archive) extend to `packages/prolog/{gnu_prolog,swi_tests}`, which the re-grid placed in the same
`packages/` bucket?

## ⛔ The question keys on the bucket, and the bucket is not the criterion

The CEO re-grid put IPL, `jcon-*`, `swi_tests`, `gnu_prolog`, `gimpel`, `csnobol4_suite`, `aisnobol` and `dotnet`
under `packages/` because they share an **origin**, not because they share a **fate**. Reasoning "IPL is excluded
and X is in the same bucket, therefore X" is a category error, and the tree already refutes it by counterexample:

⭐ **`packages/snobol4/gimpel` is THIRD-PARTY, lives in `packages/`, and IS GATED** — `scorecard_snobol4.sh:55`,
weight 5, glob `-name *_driver.sno`. Its 134 library modules are deliberately **UNSCR, and NAMED, not merely
counted** (`:133`, `:389`). One directory, in the bucket, both scored and partly excluded — on its **contents**.

## ✅ RULED — exclusion is earned by a PERMANENT STRUCTURAL BAR, never by a directory name

Three categories, all present under `packages/`:

1. **GRADEABLE THIRD-PARTY SUITE** → in the denominator. Precedent: `gimpel`.
2. **BARRED BY A RULED INVARIANT** → out permanently. IPL: 799/851 fail the semicolon-required invariant, which has
   its own gate; the only two cures are rewriting upstream provenance or breaking that gate, and hq_C's §2 closed
   both. The bar is what earns the exclusion — not the provenance.
3. **NOT PROGRAMS AT ALL** → never in the numerator, so never a debt. IPL's own `procs/incl/gprocs/gincl` half is
   already treated this way; so are gimpel's 134 library modules.

## Applied — measured, not reasoned by analogy

⭐ **`packages/prolog/swi_tests` (249 `.pl`) was never an open question.** §3 of seat10's *own baton* — eight lines
below the §2 it cited — already rules it **IN**: grade against live `swipl`, build the multi-assertion grader,
because 231/249 need plunit-style per-assertion grading. §2 and §3 rule opposite ways on purpose, on adjacent
material, in one document.

**`packages/prolog/gnu_prolog` (62 `.pl`)** — all 62 run through `./scrip --compile`, this session:

| shape | count |
|---|---|
| `[IBB] FATAL: mode-4 driver: main BB graph not found` (no `main` — library module) | **45** |
| compiles OK | **12** |
| parse error | **5** |

Directory shape says why: `BipsPl/` (45) + `Pl2Wam/` (17) are **GNU Prolog's own compiler source** —
builtin-predicates-in-Prolog and the Prolog-to-WAM compiler — vendored as reference. This is the *oracle's
implementation*, not a test suite that happens to fail. **Category 3**, and it takes gimpel's UNSCR treatment,
**not** IPL's exclusion: name the 45, glob the runnable remainder, never blanket-exclude the directory.

## ⛔ Why a named UNSCR list and not a blanket exclusion, when 45/62 are dead either way

They produce **the same number today and different numbers forever after**. A blanket exclusion permanently hides
the 5 parse errors and the 12 live files; the named list keeps them visible and lets the count move when someone
fixes one. That is the same principle §2 was protecting when it refused to let IPL stand as "a permanent 851-file
deficit nobody can ever close" — **identical principle, opposite mechanical outcome, because the bar here is not
permanent.** An exclusion is a claim that the number can never move; making that claim where it is false is how a
real defect becomes invisible.

## ⚠️ Sizing correction, carried back to the asker

The question was posed as "206 + 249 files". `gnu_prolog` holds **62** `.pl`, not 206 — the 206 is a total file
count, and the coverage denominator has only ever counted program-source extensions
(`.sno .icn .pl .sc .reb .raku .pas`), which is `util_corpus_coverage_denominator.sh`'s own consistent methodology.
Same class as seat16's 3158→3159 correction over a `README.md`. **A 206-file classification question and a 62-file
one are differently sized problems**, and the misreading inflates this one by 3.3x.

⚠️ Attribution correction: the §2 IPL ruling is **hq_C's**, not `hq_P`'s. seat10's own LEDGER says so correctly; the
message to this seat attributed it here. Does not change the answer.

## Open, and worth a row — not claimed here

The **5 `gnu_prolog` parse errors** are the only genuine compiler signal in that directory. Not chased this session
(this was a ruling pass, not a triage pass); mint it as its own row if wanted.
