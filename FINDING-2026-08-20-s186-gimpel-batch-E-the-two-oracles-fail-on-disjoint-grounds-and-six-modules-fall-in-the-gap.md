# FINDING s186 — gimpel batch E: the two oracles fail on DISJOINT grounds, six modules fall in the gap, and the OR family is nondeterministic

**Session:** 2026-08-20 s186 · seat6 · queue row `gimpel-drivers-E` · corpus `5d72325f`, SCRIP `cecb7d11` (pristine, RT_OPT `-O0`)
**Brief:** Lon s183 ruling — *"make tests out of each Gimpel function, an entire test suite around it."* Batch E = 25 modules, **all include-bearing**.
**Delivered:** 25 `<NAME>_driver.sno`, 19 oracle `.ref`, 3 `.input` fixtures, 1 probe (+ its 2 module copies).
**Corpus fail-set for the existing suites: UNCHANGED — m3 332/5, m4 325/11** (§6).
**RE-PROVEN ON TWO TREES**, each its own `make pristine`: `cecb7d11` → **`d3251f23` (seat7's s188 SPAN-FRAME FLIP, `SCRIP_SPAN_FRAME` default ON)**. Corpus identical on both; the batch-E table identical on both **except the three rows §3 measures as nondeterministic**. The flip moves nothing here.

---

## 1. THE BOARD

| module | m3 | m4 | module | m3 | m4 |
|---|---|---|---|---|---|
| NOT | PASS | PASS | MSORT | **SIG6** | **COMPILE_FAIL** |
| PAD | PASS | PASS | ONEWAY | **COMPILE_FAIL** | **COMPILE_FAIL** |
| PARAGRAP | PASS | PASS | OR | **crash, signal varies** | **crash, signal varies** |
| PUT | PASS | PASS | ORSORT | **crash, signal varies** | **crash, signal varies** |
| QUOTE | PASS | PASS | ORVISUAL | **crash or DIFF** | **crash or DIFF** |
| RAISE | PASS | PASS | PEEL | **RC1** | **COMPILE_FAIL** |
| REPL | PASS | PASS | PERM | **SIG6** | **SIG6** |
| | | | POKEV | **COMPILE_FAIL** | **COMPILE_FAIL** |
| PHRASE | *unscoreable* | | POL | **RC1** | **COMPILE_FAIL** |
| PHYSICAL | *unscoreable* | | RAMM | **COMPILE_FAIL** | **COMPILE_FAIL** |
| POKER | *unscoreable* | | RCHAR | **COMPILE_FAIL** | **COMPILE_FAIL** |
| QUEST | *unscoreable* | | RPERMUTE | **COMPILE_FAIL** | **COMPILE_FAIL** |
| RPOEM | *unscoreable* | | RSEASON | *unscoreable* | |

**7 GREEN both modes · 12 RED (checked in red, law 0d) · 6 UNSCOREABLE by construction** (§2 — no `.ref` exists for those six, and none can be honestly made).
Three fixed m3 ≢ m4 divergences on top of the OR family's flapping: `MSORT` SIG6 vs COMPILE_FAIL, `PEEL` RC1 vs COMPILE_FAIL, `POL` RC1 vs COMPILE_FAIL.

## 2. ⭐⭐ THE HEADLINE — THE TWO SANCTIONED ORACLES FAIL ON DISJOINT GROUNDS

Batch C found three modules Spitbol refuses and routed them to CSNOBOL4. Batch E shows that was not a workaround with unlimited range: **there are things only Spitbol can run and things only CSNOBOL4 can run, and the sets do not cover each other.** Three walls, each measured with a one-line control:

| wall | who refuses | what it is | evidence |
|---|---|---|---|
| **W1 — redefining a built-in** | **sbl only** | `BAL.sno` assigns to `BAL`, a protected Spitbol built-in | `BAL.sno(11) : ERROR 042 — attempt to change value of protected variable`. (Batch C's `SQRT`/`LOAD` ERROR 248 is the same wall, different message.) CSNOBOL4 runs it. |
| **W2 — four-argument file association** | **sbl only** | `INPUT(.INPUT,5,,'rpoem.in')` / `OUTPUT(.DISK,10,,'ASMTEMP')` | `ERROR 116 — inappropriate file specification for input` (`ERROR 160` for output, batch C's ASM). CSNOBOL4 accepts the form. |
| **W3 — real-argument `REMDR`** | **CSNOBOL4 only** | `RANDOM.sno:5` — `REMDR(RAN_VAR * 4676., 414971.)` | `Error 1 — Illegal data type`. Isolated with a two-line control: sbl prints `0.112682572999077e-1` and `5`; CSNOBOL4 dies. sbl runs it fine. |

**A module needing (W1 or W2) AND W3 has no oracle at all.** That is exactly the six: `PHRASE` (BAL via RSENTENCE + RANDOM), `QUEST` (same), `POKER` (W2 + W1 via SQRT + RANDOM via CARDPAK), `RPOEM` (W2 + RANDOM), `RSEASON` (W2 + RANDOM). `PHYSICAL` falls out separately and worse: sbl refuses `REDEFINE( , 'EQ(X,Y)')` with `ERROR 156 — opsyn first arg is not correct operator name` (you cannot OPSYN the blank/concatenation operator), and **CSNOBOL4 dumps core on it**.

⛔ **THE OBVIOUS CURE WAS TRIED AND DOES NOT WORK — DO NOT SPEND A RUNG ON IT.** Four data files are referenced in lowercase by the code (`phrases.in`, `poker.in`, `rpoem.in`, `rstory.in`, plus `rseason.in`) and exist on disk only in DOS uppercase (`PHRASES.IN`, …) — the same case-mismatch class seat1 normalized for includes, one level down. Supplying the lowercase names **was measured** and changes nothing: with `rpoem.in` present, sbl still stops at ERROR 116 and CSNOBOL4 walks straight into the RANDOM wall. The rename is therefore **not** what unblocks these modules, and this row deliberately did not do it.

## 3. ⭐⭐ THE OR FAMILY IS NONDETERMINISTIC — AND A ONE-RUN BOARD ROW ON IT IS AN ARBITRARY DRAW

`OR`, `ORSORT` and `ORVISUAL` always fail, but **which** failure varies run to run. Measured n=12 per module per mode on a pristine build:

| module | m3 | m4 |
|---|---|---|
| `OR` | SIGSEGV 7 · SIGABRT 5 | SIGSEGV 8 · SIGABRT 4 |
| `ORSORT` | SIGSEGV 9 · SIGABRT 3 | SIGSEGV 6 · SIGABRT 6 |
| `ORVISUAL` | SIGSEGV 2 · SIGABRT 5 · **completed 5** | SIGABRT 9 · **completed 3** |

Three consecutive whole-batch sweeps disagreed on these three rows and on nothing else — that is how it was caught, and it is why the table in §1 reports them as a distribution rather than a status.

⭐ **THE m4 BINARY FLAPS TOO.** The same emitted, linked binary run twice gives different signals, so the nondeterminism lives in the **runtime** (`out/libscrip_rt.so`), not in compilation. This is the class seat7 and seat1 warned about (`cf_goto_computed`, row-14): a two-arm A/B sweep taken once is a **lower bound** on a nondeterministic defect, never a verdict.

⭐ **AND WHEN IT DOES COMPLETE, IT IS NOT A WRONG STRING — `OR()` FAILS.** On the ORVISUAL runs that finish, the three `OUTPUT = OR(...)` statements produce **no lines at all** (a failed statement assigns nothing), and the documented EVAL round trip then fails too. Oracle: three pattern strings plus `round trip ANCHOR: matched`. SCRIP: two lines, both "no match".

⛔ **AND ONE NEAR-MISS THAT IS *NOT* IN THIS CLASS, CHECKED BEFORE IT WAS REPORTED AS ONE.** `PERM` showed `TIMEOUT` in one sweep and `SIG6` in the others, which looks identical to the OR family from the outside. It is not: measured n=12 it is **SIG6 12/12, deterministic**, at a steady **~9.7–13.1 s** per run. The single TIMEOUT was the harness's **20 s** gimpel budget losing to a ~10 s runtime while the box carried a load average of 5.9 from other seats' builds. ⭐ **That budget is only 2× PERM's real runtime, so PERM's board row is load-sensitive and will flap on a busy machine** — a distinct hazard from a nondeterministic defect, and one a board run cannot tell apart without timing it.

**Probe: `corpus/probe/gimpel/gim_or_single_alternative_crash.sno`** (with `OR.sno` + `BALREV.sno` copied in beside it, the `BLANKS.sno`+`DIFF.sno` precedent). ⛔ **Shrinking proves it is NOT the alternation:** `OR(',A')` — a single one-character alternative — crashes **6/6**, alternating 139 and 134, exactly as `',A,B'`, `',AB,AC'` and `',ABLE,ACTOR'` do. The defect is reached by OR's machinery on one alternative and needs no alternation at all.

## 4. THE PARSE GAP IS THE HIGHEST-YIELD DEFECT IN THIS CORPUS

Five of batch E's twelve reds are the **same** trailing-dot real-literal parse failure batch C hit and batch B already witnessed as `gim_real_literal_parse`: `ONEWAY`, `POKEV`, `RAMM`, `RCHAR`, `RPERMUTE` are all `COMPILE_FAIL` in both modes, and all five reach it through `RANDOM.sno:5`'s `4676.` / `414971.`. No probe is committed for it here — **batch B's witness stands and is not duplicated**. But the arithmetic is worth stating: one parse rule, five batch-E modules plus batch C's `SQRT` and `ARC`, and every module downstream of `RANDOM.sno` in the batches still to come.

## 5. FIVE THINGS ABOUT THE CORPUS ITSELF

- ⛔ **`RAISE.sno` IS BROKEN AS SHIPPED, IN BOTH DIALECTS.** Its one live statement is `DEXP('RAISE(X,Y) = X ** Y')  :(EXP_END)` and `EXP_END` is commented out along with the series expansion above it. sbl: `ERROR 038 — goto undefined label`. CSNOBOL4: `Error 24 — undefined or erroneous goto`. No oracle can run the included form, so `RAISE_driver` drives what the module's own header says it now is (`X ** Y`) and says why — the batch-C `SQRT_driver` arrangement. **It passes**, which is worth noting: real exponentiation and exact-value real printing agree with the oracle.
- ⛔ **`PEEL` DOES NOT FAIL ON AN EXHAUSTED VARIABLE** — it returns the null string and SUCCEEDS, forever. A driver written the obvious way (`:F()` on the loop) does not terminate under either oracle. Recorded because the next batch will meet the shape.
- **Four modules ship with NO header comment**, so they have no contract to write cases from: `PEEL`, `RAMM`, `ONEWAY`, `PHYSICAL`. The manifest's empty `contract_line` is the reliable tell. Each driver says so in its header and drives only what the published *interface* fixes.
- **`POL.sno` has the strongest contract in the batch** — its header carries a worked example, and case 1 of `POL_driver` is that example verbatim: `"IF A(I) > 6 THEN I = 2"` must give `IFTHEN:2,>:2,REF:2,A,I,6,=:2,I,2`. The oracle reproduces it exactly. SCRIP: RC1 / COMPILE_FAIL.
- **`RANDOM.sno` is a seeded LCG with no `DATE()`/`TIME()`**, so every "random" module in this batch is fully deterministic and legal under the brief's determinism rule. That is worth carrying forward: `RPERMUTE`, `RCHAR`, `RAMM`, `ONEWAY`, `PHRASE`, `POKER` and `CARDPAK` are all testable, and their `.ref`s are stable.

## 6. GATE

`make pristine` first (HQ-27), then `bash scripts/test_corpus_snobol4.sh`:

```
mode-3 (--run):     PASS=332 FAIL=5
mode-4 (--compile): PASS=325 FAIL=11 SKIP=1  (337 total)
```

Identical to the brief's baseline on **both** measured trees (`cecb7d11` and `d3251f23`), fail-sets matching by name. This batch touched **no SCRIP code** — corpus files only — so the invariance is confirmation, not a claim of work.

## 7. WHAT BATCH E ADDS TO THE PICTURE

Batch C's closing line was that a third of gimpel's reds are nowhere near the M1 pattern wall. Batch E sharpens it in a direction worth naming: **the largest single obstacle in this corpus is not a SCRIP defect at all — it is that the two sanctioned oracles do not agree on what SNOBOL4 is.** Six of twenty-five modules are unscoreable not because SCRIP is behind but because no ground truth exists for them on this machine, and the reason splits cleanly three ways with a one-line control for each. That number will only grow in the batches still to come, because W2 (four-argument file association) and W3 (`RANDOM.sno`) are both *common* idioms in this library, not exotic ones.

⭐ The other addition is methodological and cost nothing but three sweeps instead of one: **the OR family would have been reported as `SIG6`, or `SIG11`, or `DIFF` — three different verdicts, all defensible, all wrong** — by a board that ran once. Any gimpel batch that reports a crash status from a single run is reporting a draw, not a measurement.
