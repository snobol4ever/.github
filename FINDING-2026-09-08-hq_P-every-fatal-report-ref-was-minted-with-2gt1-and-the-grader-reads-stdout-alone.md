# FINDING 2026-09-08 hq_P — all 33 SPITBOL-termination-report refs were minted with `2>&1`; the grader compares stdout alone, so NO implementation can match them

## Claim

Every `.ref` in the SNOBOL4 package suites that captures a SPITBOL **termination report** contains
that report **twice**. The grader (`scripts/scorecard_snobol4.sh`) compares the candidate's **stdout
only**. SPITBOL's own stdout contains the report **once**. Therefore **`sbl -bf` cannot reproduce its
own refs**, and neither can SCRIP, nor could a byte-perfect SPITBOL clone.

⛔ These are **not compiler defects and must not be worked as compiler defects.** On the gimpel board
they are 11 of the 26 reds — **42% of that suite's remaining red** — and they are unwinnable as
graded.

## Proof, mechanical and uniform

`sbl -bf SQRT_driver.sno`, three capture disciplines:

| capture | lines | report appears |
|---|---|---|
| stdout alone (`2>/dev/null`) | 18 | once |
| stderr alone | 10 | once (stats only, no leading blanks) |
| `2>&1` | 28 | **twice** |
| the committed `SQRT_driver.ref` | 28 | **twice** — byte-identical to the `2>&1` capture |

SPITBOL writes the termination report to **both** streams. The refs were minted by a script that
merged them; the grader keeps them apart (`> "$W/m3" 2>"$W/m3e"`, `scorecard_snobol4.sh:311`) and
then `cmp`s stdout against the merged pin (`:305`).

Verified against the oracle for ten programs — `stdout == ref` NO in 10/10, `2>&1 == ref` YES in 10/10.

## Census — the whole tree, not a sample

| area | refs with a termination report | report appears once |
|---|---|---|
| `packages/snobol4/csnobol4_suite` | 22 | 0 |
| `packages/snobol4/gimpel` | 11 | 0 |
| `tests/snobol4` | 1 (appears **3x**) | 0 |
| **total** | **34** | **0** |

⭐ **Not one correctly-minted termination-report ref exists in the tree.** That uniformity is the
argument: this is one minting script, not thirty-four separate mistakes.

## The sets are identical — this is the whole class and nothing else

The gimpel board's `pin-only fatal-report` REDs and the doubled-ref programs are the **same 11
programs**, diffed and identical:

`ARC_driver ASM_driver GPM_driver INFINIP_lib_driver INSULATE_driver L_TWO_driver PEEL_driver
SQRT_driver TRIG_driver TUPLE_driver VISIT_driver`

## ⭐ The incoherence that makes this worth a law, not just a fix

`scorecard_snobol4.sh` treats one oracle condition two different ways depending on an accident:

- oracle dies with a fatal report **and no `.ref` exists** → `have_pin=0`, `have_live=0` → **UNSCR**
  (17 gimpel programs, honestly excluded).
- oracle dies with a fatal report **and a `.ref` exists** → graded against that pin → **RED** (11
  gimpel programs, unwinnably).

Same oracle behaviour, opposite verdicts, decided by whether someone once minted a ref. The 17 are
excluded for exactly the reason the 11 should be.

## What SCRIP actually does here — a real defect, separate and smaller than the board suggests

SCRIP prints to **stderr** and nothing to stdout:

```
(0) : ERROR 248 -- attempted redefinition of system function
in statement 0
```

against SPITBOL's stdout:

```
SQRT.sno(8) : ERROR 248 -- attempted redefinition of system function
in file              SQRT.sno
in line              8
in statement         1
stmts executed       1
execution time msec  0
REGENERATIONS        0
memory used (bytes)  12680
memory left (bytes)  1035888
```

Three genuine gaps: (1) the report goes to stderr, not stdout; (2) **the source file and line are
not reported — `(0)` where SPITBOL says `SQRT.sno(8)`**, and statement number is 0 where SPITBOL
says 1; (3) no statistics block. ⭐ Gap (2) is worth curing on its own merits whatever happens to
the refs — an error that cannot name its own line is a bad diagnostic, independent of grading.

## The cure is three parts and only the third is compiler work

1. **Grader** (`hq_T`): normalize the machine-dependent report lines the way `norm=ms` already
   normalizes `iters:`/`ns:`/`ms:` at `scorecard_snobol4.sh:303` — the precedent is in the same
   function. `memory used (bytes)`, `memory left (bytes)`, `execution time msec` and `REGENERATIONS`
   are SPITBOL-internal accounting and **can never be matched by any other implementation**, so no
   correctly-minted ref helps without this step.
2. **Corpus**: re-mint the 34 refs from **stdout alone**, so the oracle reproduces its own ref.
3. **Runtime**: emit the termination report on stdout with the file/line/statement filled in.

⛔ **Steps 1 and 2 flip nothing by themselves** — they only make the target reachable. Anyone
reporting a board gain from them alone has measured something else.

## Recommendation

Until 1–3 land, **the 11 should be reclassified UNSCR alongside the 17 they are indistinguishable
from**, so the gimpel denominator stops charging the compiler for a minting error. That is a
denominator re-cut with its reason recorded inline (`SUITES.tsv:criterion_changed`), exactly the
shape the coo used for snoflake 126→124 tonight — **not** a softening, and it is a `ceo`/`hq_T`
call, not a seat's.

⛔ I have NOT made that change. This FINDING is the diagnosis only.

## Provenance

SCRIP `13c3cf588`, corpus `00eb70759`, `RT_OPT=-O0`, oracle `/home/resources/x64/bin/sbl -bf`.
Surfaced while walking hq_P's NONET Q-Z gimpel slice: SQRT, TRIG, TUPLE and VISIT all die at
`ERROR 248 attempted redefinition of system function`, which looked like one compiler class —
`sn4_sysfn_protected` (`src/runtime/snobol4_system_fns.h:15`) protects all 76 system names. ⭐ **The
oracle raises ERROR 248 on those programs too**, so the shared-name theory was wrong; chasing why
the oracle nevertheless "passed" is what exposed the ref defect.
