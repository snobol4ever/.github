# FINDING 2026-08-19 s154 — BM-4: THE WORKLOAD FAMILY LANDED, AND ITS FIRST BOARD SAYS **FENCE IS INERT ON SCRIP** WHILE IT MOVES THE ORACLE BY UP TO 2.3×

**Seat:** local `/home/claude3` (Claude Opus 5). **Goal:** `GOAL-SNOBOL4-100.md` (benchmarks, weight 10).
**Baseline:** SCRIP `e26dbad41`+ · corpus `6ec20be6c`+. No codegen touched — corpus + instrument only.
**Companion:** `FINDING-2026-08-19-s154-gc-stall-is-the-benchmark-and-collect-cannot-fix-it.md` (BM-3).

---

## 1. WHAT LANDED — `corpus/benchmarks/snobol4/demo/`, 15 PROGRAMS

The microbenchmark family isolates one operation per row. This family **deserializes structured
text into live memory** — pattern matching with sprinkled loads, the thing SNOBOL4 is for. Same
`harness.inc` (shared via `-INCLUDE '../harness.inc'`, not copied), same `check:`/`iters:`/`ms:`
contract, same runner via `BENCH_DIR`.

Five grammars × three variants, and **the three-variant shape is the instrument**:

| variant | what it runs | what the delta prices |
|---|---|---|
| `<name>` | parse **and build** — captures + `*function()` | the real workload |
| `<name>-match` | same grammar, **no captures, no side effects** | pure pattern throughput |
| `<name>-match-fence` | as `-match` + `FENCE` | what backtracking costs |

`plain − match` is the price of the loads; `match − match-fence` is the price of the backtracking
FENCE removes. Neither is visible from a single number — which is the whole point, see §3.

`check:` is the **deserialization census, not a byte count**: `claws5` returns tokens built, `json`
returns `objects/arrays/strings/ints/reals/bools/nulls/maxdepth`, the calculators the sum of every
expression evaluated, `porter` total stem length. Every value the original driver would have
PRINTED is accumulated into the check instead — stdout stays clean for the harness, and the check
witnesses the whole computation rather than merely "the match succeeded". Each iteration resets its
structures, so a batch is steady-state and re-deserializes from scratch.

Input is a sibling `<family>.dat` on stdin (family = program name minus any `-match`/`-match-fence`
suffix), so a grammar's three variants provably read the same bytes. **The originals in
`programs/snobol4/demo/` are untouched** — the scorecard's `demos` suite (weight 15) globs that
directory and diffs `.ref`s holding real output, so converting in place would have destroyed it.

## 2. THE BOARD (ZBUD=1000 ms, best-of-2, `SCRIP_HEAP_MB=1024`, gc 0 on every row)

| benchmark | sbl/s | m3/s | m4/s | m3:sbl | status |
|---|---:|---:|---:|---:|---|
| calculator-1-match | 33 | **50** | 49 | **1.52×** | ok |
| treebank-match-fence | 2.2K | 2.3K | 2.2K | **1.04×** | ok |
| treebank-match | 2.5K | 2.3K | 2.2K | 0.89× | ok |
| calculator-1-match-fence | 77 | 50 | 48 | 0.65× | ok |
| calculator-2-match-fence | 2.0K | 1.0K | 1.0K | 0.50× | ok |
| calculator-2-match | 2.9K | 1.0K | 1.0K | 0.35× | ok |
| calculator-1 | 165 | 75 | **NA** | 0.45× | ⛔ m4 Error 22 |
| calculator-2 | 143 | 66 | **NA** | 0.46× | ⛔ m4 Error 22 |
| claws5 · claws5-match · claws5-match-fence | 207 · 10.3K · 9.1K | NA | NA | — | ⛔ m3 SIGSEGV |
| json · json-match · json-match-fence | 71 · 1.0K · 901 | NA | NA | — | ⛔ m3 >60 s |
| porter | 16 | NA | NA | — | ⛔ Error 22 both modes |

**6 of 15 rows measure on all three engines. 9 fail on SCRIP; the oracle runs all 15.**

## 3. ⛔⭐ THE HEADLINE — FENCE IS INERT ON SCRIP

Read the fenced/unfenced pairs down the m3 column and then down the sbl column:

| grammar | sbl unfenced | sbl fenced | **oracle effect** | m3 unfenced | m3 fenced | **SCRIP effect** |
|---|---:|---:|---|---:|---:|---|
| calculator-1 | 33 | 77 | **2.3× FASTER fenced** | 50 | 50 | **none** |
| calculator-2 | 2.9K | 2.0K | 1.45× slower fenced | 1.0K | 1.0K | **none** |
| treebank | 2.5K | 2.2K | 1.14× slower fenced | 2.3K | 2.3K | **none** |

**On all three grammars SCRIP's fenced and unfenced throughput are identical**, while the oracle
moves by 1.14×–2.3× and in BOTH directions. FENCE is a backtracking-pruning construct; identical
throughput across it means SCRIP's emitted code is not changing the backtracking it does.

This also explains the one row where SCRIP wins outright and the one where it loses worst — they
are the SAME grammar: `calculator-1-match` **1.52×** (SCRIP faster) and `calculator-1-match-fence`
**0.65×**. SCRIP's number never moved; the oracle's more than doubled. Any claim of a win or loss on
that grammar is really a statement about FENCE.

### ⭐ ASM-DIFF-FIRST RUN, AND IT HALVES THE QUESTION

The opening move was made rather than left for the next seat. `--compile` on both variants:

| variant | `.s` bytes | md5 |
|---|---:|---|
| `calculator-1-match` | 314,998 | `9c79bd7033da` |
| `calculator-1-match-fence` | 309,819 | `befb525f1965` |

**NOT byte-identical — they differ by 210 lines, and the fenced form is 5,179 bytes SMALLER**, with
4 fence sites named in the emitted asm. **So the "FENCE emits a no-op wiring" hypothesis is
REFUTED: FENCE is lowered and it does change the emitted code.** Both variants also compute the
correct answer (check 32512, matching the oracle ref), so this is not a correctness bug.

⛔ **What remains, NOT root-caused here** (END-OF-CONTEXT LAW — minted and routed): SCRIP emits
different, smaller code for FENCE and gets *exactly the same throughput* from it, while the oracle
gets 2.3×. So either the emitted pruning is semantically inert at run time, or SCRIP's execution of
the unfenced form was never doing the backtracking FENCE exists to remove — in which case the
oracle's 33/s unfenced figure, not SCRIP's, is the anomaly. Next instrument is a backtrack counter
(or a `gdb` hit-count on the choice-point site) across the pair, NOT another `.s` read.

## 4. ⛔ ERROR 22 — "UNDEFINED FUNCTION CALLED" WHEN A SNOBOL FUNCTION IS CALLED FROM INSIDE ONE

Four rows die this way: `porter` in **both** modes, `calculator-1`/`calculator-2` in **m4 only**
(m3 runs them fine — a MODE34-IDENTICAL violation, `GOAL-MODE34-IDENTICAL.md`).

**This is the s156 B1 class** (`FINDING-…-s156-B1-root-cause-byname-dispatch-cannot-reach-snobol-defined-targets-in-m4`),
reproduced independently on real programs — and **extended: porter shows it in m3 as well**, which
the B1 write-up scopes to m4. Isolation done, so the next seat does not repeat it:

- The converted `porter` **runs correctly on the oracle** (check 139812), so the program is valid.
- Replacing `stemmer(ZWORDS[ZJ])` with `SIZE(ZWORDS[ZJ])` — same loop, same array — **passes**
  (check 166607, 224 iters). The ARRAY access is not implicated.
- Replacing it with `stemmer('running')` — a literal argument — **still fails**. The argument is
  not implicated either. It is the CALL.
- A hand-built 3-deep nest (`h`→`g`→`f`) **works in m3**, so plain nesting is not sufficient to
  trigger it. Something about these specific callees is.

## 5. TWO CORPUS FACTS WORTH RECORDING

- ⛔ **`treebank.sno` (plain) does not compile on the ORACLE** — `ERROR 217 duplicate label` ×5 then
  SIGSEGV (rc=139). No `.ref` can be baked and no engine can be scored on it, so it is excluded from
  the family and the exclusion is documented in the README. **A corpus defect in the original**, not
  a SCRIP one. Its two `-match` variants are fine.
- ⛔ **`claws5` all three variants SIGSEGV in m3, and the ORIGINAL programs do too** (verified against
  `programs/snobol4/demo/claws5-match.sno` on both the 66 KB workload and the 1 KB smoke input) — so
  this is pre-existing, not a conversion artifact. **Consequence: `SCRIP/README.md`'s benchmark
  section quotes claws5-match figures (0.195 ms/match, "SCRIP beats SPITBOL per-match") that cannot
  be reproduced at this HEAD.** Either the row regressed or those numbers predate the regression;
  either way the README is quoting an unrunnable program and should be marked.

## 6. INSTRUMENT REPAIRS MADE WHILE BUILDING THIS

- A **CRASHed row reported `-` for its gc field**, which went straight into `$(( ))` and killed the
  whole board mid-table. One dead row could abort the run. Coerced to 0.
- The harness guard grepped for a literal `INCLUDE 'harness.inc'`; the demo family uses
  `'../harness.inc'` to share ONE driver. Widened. (It failed loudly — an empty board — rather than
  silently mis-measuring, which is the behaviour we want.)
- `SBLFLAGS` (default `-s16m`): `json`'s recursive descent overflows the oracle's default stack
  (`ERROR 246`) once its match runs inside the harness function's frame. A stack size is not a
  throughput knob; larger values are refused by this container.

## 7. ⛔ NEXT SEAT — PICK UP EXACTLY HERE

1. **FENCE inertness (§3) is the highest-value open item on this board.** The `.s` diff is DONE and
   refutes the no-op hypothesis (210 lines differ, fenced form 5,179 bytes smaller, 4 fence sites
   emitted). Next instrument is a backtrack/choice-point COUNT across the pair, not another `.s`
   read — and consider that the oracle's 2.3× unfenced penalty, not SCRIP's flatness, may be the
   anomaly worth explaining.
2. **Error 22 (§4)** — take the s156 B1 hunt and add porter's m3 case to it; the isolation above
   narrows it to the call itself, with argument and array ruled out.
3. **json on SCRIP exceeds 60 s** where the oracle does 1.0K iters/s. Not characterised — could be a
   hang or a >1000× slowdown, and those want different hunts. The plain `json` printing
   `input bytes=631514` and then never finishing is why a census that reads only the FIRST line of
   output is not a census; it was recorded as passing before this rung.
4. **The demo family's `NOISE-FLOOR.tsv` is not baked** — the runner prints `-` for min-det on every
   row, which is honest but means no delta on this board is yet gate-able.
