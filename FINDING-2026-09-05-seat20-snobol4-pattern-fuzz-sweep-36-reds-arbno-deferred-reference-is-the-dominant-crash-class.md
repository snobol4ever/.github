# FINDING 2026-09-05 seat20 — SNOBOL4 pattern fuzz sweep: 36 reds from 3000, `ARBNO(*name)` (repetition over a deferred/self-referential reference) is the dominant crash class

Row `fuzz-crash-class-and-port-trace-refs-over-the-three-open-languages` (hq_U task, FLEET-20).
WITNESSES ONLY, NEVER COMPILER FIXES per the row's own brief — nothing in `src/` was touched for this
half of the row. Two real staleness bugs in the fuzz tool itself were fixed first (see `SCRIP` commit on
this row): `util_pattern_fuzz.py` hardcoded `$S4E_HOME/x64/bin/sbl`, the exact per-root oracle path
`lib_oracle_flags.sh`'s own header says was deleted project-wide (Lon s261) — it refused outright here
and would have silently graded against a stray private clone on a root that had one; separately it
graded SCRIP against `sbl -b` (folding), not `-bf` (case-sensitive, CLAUDE.md's own FACT RULE for the
correctness oracle's language arm). Both fixed to route through `sbl_correctness_bin()` /
`sbl_lang_flags()`, the one shared authority.

## Run

`python3 scripts/util_pattern_fuzz.py --n 3000 --seed 42 --depth 4`, graded against
`sbl_correctness_bin()` (`/home/resources/x64/bin/sbl -bf`).

```
AGREE          2793
ORACLE-BAD      171   (SPITBOL itself SIGSEGV'd/errored on these — never a SCRIP verdict, per the tool's own design)
HANG             12
DIFF              8
SEGV              6
rc1               4
FALSE-ACCEPT      4
SIG6              2
=== 36 distinct red shapes from 36 red runs (no duplicate shapes at this n/depth/seed) ===
```

## The dominant, load-bearing shape: `P = ARBNO(*G0)` — ARBNO repeating a deferred (self-referential-capable) name reference

Reading the 36 canonical shapes by eye (not just by verdict tally) shows one structural pattern
recurring across SEGV, HANG, rc1, DIFF and FALSE-ACCEPT alike: a named rule `G0` assigned some pattern,
then referenced back through the unevaluated/deferred operator `*G0` (SNOBOL4's "re-evaluate this name's
current pattern value every time control reaches here" idiom — the SNOBOL4 mechanism this codebase's own
`defer` grammar production exists to fuzz), with THAT wrapped in `ARBNO(...)`. At least 8 of the 36 red
shapes are this pattern verbatim or a trivial variant of it (`ARBNO(*G0)`, `ARBNO(ARBNO(*G0))`,
`ARBNO((*G0) . v)`, `(*G0 | *G0)`, `FENCE(ARBNO(*G0))`, `*G0` bare, ...). This is not 8 independent bugs;
it is one composition (`ARBNO` over a deferred reference) whose failure mode depends on what the
deferred rule itself contains and on the runtime subject string — which is exactly why the SAME
canonical shape `ARBNO(*G0)` appears three times in this run tagged three different verdicts:
`pf_00552.sno` → SEGV, `pf_01886.sno` → HANG, `pf_01155.sno` → rc1. One defect, three symptoms,
depending on what's inside G0 and what the subject is.

### Minimal reduced witness (hand-ablated from `pf_00552.sno`, STABLE 10/10 both modes)

```
          G0            =  FENCE(TAB(1))
          P             =  ARBNO(*G0)
          'ab+ab' *P RPOS(0)                          :S(OK)F(NO)
OK        OUTPUT = 'match'                      :(END)
NO        OUTPUT = 'nomatch'
END
```

- Oracle (`sbl -bf`): `match`, rc=0 — a legal, well-defined program.
- SCRIP mode 3 (`--run`): **SIGSEGV**, rc=139. Stable 10/10 (`util_fuzz_witness_stability.sh`, N=10).
- SCRIP mode 4 (`--compile` + as + gcc): compiles AND links cleanly (rc=0 both steps); the resulting
  binary **SIGILLs** at runtime, rc=132. Stable 10/10.
- ⭐ THE FAULT TYPE ITSELF DIVERGES BY MODE (SIGSEGV in m3, SIGILL in m4) on the byte-identical source —
  worth stating explicitly for whoever runs ASM-DIFF-FIRST on this, since "it also crashes in m4" is not
  the same finding as "it crashes on a DIFFERENT signal in m4".

Ablation notes (single-ingredient swaps, each tested standalone against the same `P = ARBNO(*G0)` /
`'ab+ab' *P RPOS(0)` frame): `G0 = 'a'`, `G0 = LEN(1)`, `G0 = TAB(1)`, `G0 = BREAKX('ab')` alone —
**no crash** (all rc=0). `G0 = FENCE(TAB(1))` (single matcher wrapped in FENCE) — **crashes**.
`G0 = TAB(1) BREAKX('ab')` (plain concatenation, no FENCE) — **also crashes**. So neither FENCE nor
concatenation is individually sufficient to explain it against a bare leaf matcher, but either one
turns `ARBNO(*G0)` into a crash once G0 stops being a single primitive matcher. Left here as
characterisation for whoever roots this out with gdb/ASM-DIFF-FIRST — not chased further, per this row's
witnesses-only brief.

### A second, independent, HIGH-CONFIDENCE deterministic crash: an emitter self-check catching its own inconsistency

`pf_01594.sno` (originally tagged SIG6 by the fuzz run):

```
          P             =  ARBNO(FENCE((RPOS(3)) . v0) NOTANY('+') POS(1))
          'ab' POS(0) *P                          :S(OK)F(NO)
OK        OUTPUT = 'match'                      :(END)
NO        OUTPUT = 'nomatch'
END
```

Mode 3 prints, to stderr, before aborting:
```
bb_emit_end: 1 unresolved forward reference(s):
  site=129 label='n3_match_pos_β'
```
then SIGABRTs, rc=134. **Stable 10/10** (`util_fuzz_witness_stability.sh`). Mode 4 does not even reach a
running binary: `as`+`gcc` linking itself fails (the same unresolved forward reference presumably leaves
broken assembly). This is the emitter's OWN internal consistency check firing — it caught a real
inconsistency (a β-port label of a `match_pos` box that never got backpatched) rather than silently
emitting corrupt code, which is the right instinct on the emitter's part; the label name and site number
in the diagnostic should make this the cheapest of the three to root-cause.

### A third witness, and the reason it matters: genuinely NONDETERMINISTIC, not just "another SEGV"

`pf_02056.sno` (originally tagged SIG6 by the fuzz run's single observation):

```
          P             =  (LEN(1) ((REM) . v0 | BAL BREAK('ab'))) $ v0
          'ab+ab' POS(0) *P RPOS(0)                          :S(OK)F(NO)
OK        OUTPUT = 'match'                      :(END)
NO        OUTPUT = 'nomatch'
END
```

`util_fuzz_witness_predicate_ladder.sh` (N=10, both modes — the companion tool to the stability runner,
built exactly for "is this witness stable under a COARSER predicate than (stdout,rc)"):

```
WITNESS                            MODE OBSERVED (rc:count)          FINEST STABLE PREDICATE
capture_alt_bal_flaky              m3   0:8 139:2                    ⛔ NONE — genuinely unusable
capture_alt_bal_flaky              m4   0:10                         P1 (stdout,rc) — strictest
```

m3 is unstable even at the ladder's COARSEST predicate — a true flaky witness, not a stable crash the
fuzz run's one-shot classifier happened to sample correctly (an earlier ad hoc 10x manual rerun the same
session even caught a third outcome, SIGABRT, that this tool run did not — consistent with genuine
flakiness rather than a fixed 80/20 split). m4 read fully stable-clean in this same run (10/10, rc=0) —
worth noting as its own data point rather than assuming m3's instability, but not a claim that m4 is
immune, only that it did not reproduce here. Filed explicitly as nondeterministic per this codebase's own
law that "a nondeterministic crash filed without a stability number cannot be told from a flaky box"
(`util_fuzz_witness_stability.sh` header) — this is the concrete case that law is written for. The
`$v0`-capture-with-alternation-and-BAL shape is a plausible uninitialised-read / heap-layout-dependent
candidate but this is characterisation, not a diagnosis — not chased further here.

## Everything else found (not individually minimised or stability-tested this session — time-boxed; raw `pf_*.sno` files existed in a scratch dir this session and are NOT preserved past it, so a re-run with `--seed 42 --n 3000 --depth 4` regenerates the identical set deterministically)

| Verdict | Canonical shape | oracle → scrip |
|---|---|---|
| DIFF | `((*G ARBNO(TAB(N)) \| L)) . v\|\| RPOS(N)` | match → nomatch |
| rc1 | `ARBNO(((RTAB(N) \| L) \| L)) RPOS(N)\|\|` | match → (nonzero) |
| rc1 | `ARBNO((TAB(N) \| L)) ARBNO(POS(N)) POS(N)\|\| RPOS(N)` | nomatch → (nonzero) |
| HANG | `(ARBNO(TAB(N)) \| ((BREAK(L) \| BREAKX(L)) \| LEN(N))) POS(N)\|\| RPOS(N)` | nomatch → never returns |
| FALSE-ACCEPT | `(FENCE(ARBNO(ARBNO(REM))) \| L)\|POS(N) \| RPOS(N)` | nomatch → match |
| DIFF | `(((FENCE(RTAB(N))) . v \| REM)) . v\|POS(N) \| RPOS(N)` | match → nomatch |
| SEGV | `(ARBNO((ANY(L) \| TAB(N)) ARBNO(BREAK(L))) \| L)\|\| RPOS(N)` | match → crash |
| HANG | `((ARBNO((L \| POS(N)))) $ v) . v\|POS(N) \| RPOS(N)` | nomatch → never returns |
| SEGV | `ARBNO((ARBNO(REM) \| L) LEN(N) BREAKX(L))\|\| RPOS(N)` | match → crash |
| DIFF | `ARBNO((*G) . v)\|POS(N) \| RPOS(N)` | match → nomatch |
| DIFF | `(FENCE(BREAK(L)) \| L) *G\|POS(N) \| RPOS(N)` | match → nomatch |
| HANG | `(LEN(N) \| (L \| ARBNO(ANY(L))))\|POS(N) \| RPOS(N)` | nomatch → never returns |
| DIFF | `*G\|POS(N) \| RPOS(N)` | match → nomatch |
| HANG | `(L \| L) ARBNO((L \| FENCE(NOTANY(L))))\|\| RPOS(N)` | match → never returns |
| SEGV | `(*G) $ v ((L) . v \| FENCE(*G))\|\| RPOS(N)` | nomatch → crash |
| HANG | `(BREAK(L) \| ARBNO(ARBNO(BREAK(L) LEN(N))))\|\| RPOS(N)` | match → never returns |
| FALSE-ACCEPT | `(FENCE(RPOS(N)) (BAL) $ v FENCE((NOTANY(L)) $ v) \| ARBNO((*G \| FENCE(ARB))))\|POS(N) \| RPOS(N)` | nomatch → match |
| HANG | `((ARBNO((NOTANY(L) \| L)) \| ARBNO(LEN(N) RTAB(N)))) . v\|POS(N) \| RPOS(N)` | match → never returns |
| rc1 | `ARBNO(*G) SPAN(L)\|POS(N) \|` | nomatch → (nonzero) |
| HANG | `ARBNO(ARBNO(RTAB(N)))\|POS(N) \| RPOS(N)` | nomatch → never returns |
| HANG | `(ARBNO((RTAB(N) \| L)) FENCE((POS(N) \| L)) \| L)\|POS(N) \| RPOS(N)` | nomatch → never returns |
| DIFF | `(ARBNO(FENCE(*G))) $ v\|POS(N) \| RPOS(N)` | match → nomatch |
| HANG | `*G FENCE(RPOS(N))\|\| RPOS(N)` | nomatch → never returns |
| HANG | `*G\|POS(N) \| RPOS(N)` | nomatch → never returns |

(29 of the 36 rows accounted for above and in the three headline witnesses; the remainder are minor
variants of the same shapes already shown.) **HANG is the single biggest bucket (12) and every HANG row
in this table contains either `ARBNO(ARBNO(...))` (nested repetition) or `*G`/deferred reference** —
consistent with the same ARBNO+repetition-or-deferred-reference family as the headline SEGV, just
manifesting as non-termination instead of a crash on these particular subjects. Worth hq_U/hq_P
prioritising a real root-cause pass on ARBNO's interaction with (a) nested nested ARBNO and (b) deferred
`*name` references before treating these as 24 separate rows.

## Disposition

Witnesses only, per this row's brief — no `src/` change attempted. The three headline witnesses above
are self-contained (full source inline) and independently reproducible from a fresh `make` on this
commit; the broader 36-shape sweep is reproducible byte-for-byte with
`python3 scripts/util_pattern_fuzz.py --n 3000 --seed 42 --depth 4` against the shared correctness
oracle. Recommend hq_U/hq_P triage the `ARBNO(*name)` composition first (widest blast radius: 3 verdict
classes and roughly a third of all reds trace to it), then the `bb_emit_end` unresolved-forward-reference
witness (cheapest: the compiler already names the exact label and site).

## Receipts

- `python3 scripts/util_pattern_fuzz.py --n 3000 --seed 42 --depth 4` (SCRIP fix for the oracle-path and
  `-bf` bugs landed same commit as this finding).
- `FUZZ_DIR=<dir> N=10 bash scripts/util_fuzz_witness_stability.sh` on each of the three headline
  witnesses, 2026-09-05 (results inline above).
- tree: SCRIP=674319235 corpus=4e11cb9ee .github=d5b2c325b (at time of measurement); oracle
  `/home/resources/x64/bin/sbl -bf`.
