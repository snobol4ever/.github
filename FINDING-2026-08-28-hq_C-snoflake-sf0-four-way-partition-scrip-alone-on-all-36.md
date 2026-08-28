# FINDING — snoflake SF-0: the four-way partition, and SCRIP is ALONE on every one of the 36

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `snoflake-suite-scrip-only-gap` (RUNG SF-0, ceo-assigned)
**Measured at** SCRIP `8d944ead` · corpus `57cd91a8b` · pristine `-O0` · timeout 8s · graded vs EMBEDDED `@expect`

## THE FOUR ARMS

| arm | PASS | FAIL |
|---|---|---|
| SCRIP m3 (`--run`) | **73** | 100 |
| SCRIP m4 (`--compile`) | 72 | 48 + SKIP(cc) 54 |
| `sbl -bf` (SPITBOL) | 107 | 66 |
| `csnobol4` (home dialect) | **168** | 5 |

## THE PARTITION — denominator authority for SF-1..SF-7

| set | definition | count |
|---|---|---|
| **(a)** | csnobol4-FAIL — suite/environment defects | **5** |
| **(b)** | sbl-fail ∩ csnobol4-pass — DIALECT DISTANCE | **62** |
| **(c)** | SCRIP-fail ∩ sbl-pass — **THE DEFECT SURFACE** | **36** |
| **(d)** | SCRIP-pass | **73** |

Reconciles: m3 fails 100 = (c) 36 + 64 shared with sbl · 180 = 73 + 100 + 7 NSTD.

**(a), named as SF-0 requires:** `case-fold-disabled eliza-duquet-original endfile-rewind-write-read gimpel-asm-machine-m math-functions `

## ⭐⭐ SCRIP IS ALONE ON ALL 36

Every fixture in set (c) is passed by **both** oracles — `sbl` *and* `csnobol4`. So set (c) is not
dialect distance, not suite rot, and not an artefact of grading against the CSNOBOL4-flavoured
`@expect`: **36 of 36 are SCRIP alone producing the wrong answer.** That is the strongest form the
defect surface can take, and it means SF-2..SF-6 need no further disposition argument — every one of
these is in scope by construction.

**(c), the working list for SF-2..SF-6:**

```
control-hide-list-control-line cursor-position-underline dump-ordered dump-variables 
eliza-modernized fullscan-overlap fullscan-palindrome gimpel-array-functions gimpel-asm360-pli-once 
gimpel-binary-tree-linearize gimpel-code-function gimpel-combinatorics gimpel-conversions 
gimpel-linked-list-functions gimpel-l-one-compiler gimpel-read-list-functions 
gimpel-rseason-baseball gimpel-snobol-statement-reader gimpel-sorting-functions 
gimpel-stack-field-functions gimpel-state-functions gimpel-test-pattern-predicate 
gimpel-tictactoe-functions gimpel-tree-pattern indirect-integer-and-keyword infix-to-polish 
kalah-opening-search letter-count letter-counter n-queens pattern-assignment-targets 
real-to-integer-coercion stlimit-negative-stcount wang-theorem-prover word-count-table-convert 
word-ending-analysis 
```

## MOVEMENT SINCE THE MINT, ATTRIBUTED

ceo measured (a)=4 · (b)=63 · (c)=46 at SCRIP `7a63ff8a`. At `8d944ead`:
- **(c) 46 → 36** — SF-1 (SCRIP `89e8fb4e`, the missing `<<EOF>>` lexer arms) cured 10 of them.
- **(a) 4 → 5 / (b) 63 → 62** — `math-functions` moved from (b) into (a): it FAILS csnobol4 in this
  build. ⚠️ That is a one-fixture disagreement with ceo's 169/4 and it is an ORACLE-BUILD difference,
  not a SCRIP change — this root built csnobol4 2.3.3 from `/home/resources/snobol4-2_3_3_tar`, and
  ceo's arm resolved some other tree. **Do not treat 168/5-vs-169/4 as movement**; settle which
  csnobol4 build is canonical before either number is quoted as a baseline.

## ⛔ THE ARM COULD NOT RUN HERE AT ALL, AND THE REASON GENERALIZES

`ARM_CSN` resolved csnobol4 only at `$SD/../csnobol4/snobol4` — **inside the workspace root**. Two
standing rules forbid that: CLAUDE.md '*the oracles are NOT siblings here, they live outside every
root*' (sbl, icont/iconx, swipl are all asset-path), and the handoff law, since `handoff_status.sh`
auto-discovers every top-level git repo with an origin remote — so a csnobol4 clone placed there
becomes a **permanent handoff blocker** once it has a local commit. Its own sibling script
`build_csnobol4_archive.sh` already used the asset root. ⭐ **The disagreement was invisible because
whoever wrote the line had the tree in the one place that worked for them** — the same shape as this
root's `command -v icont` lesson: an instrument that answers *for my machine* read as *in general*.
Fixed in SCRIP `1503a1ce` (asset root first, workspace root as fallback so existing setups keep working).
