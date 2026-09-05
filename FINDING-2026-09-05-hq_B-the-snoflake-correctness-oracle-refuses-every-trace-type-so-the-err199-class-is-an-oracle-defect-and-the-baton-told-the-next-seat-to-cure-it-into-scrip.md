# FINDING (hq_B, 2026-09-05): the snoflake correctness oracle refuses EVERY trace type, so the ERR199 class is an ORACLE defect — and the baton told the next seat to cure it INTO SCRIP

**Seat:** hq_B · **Mode at measurement:** FLEET-8 · **Tree:** SCRIP `df9fe6af0`, corpus `d58a796fa`, RT_OPT=`-O0`, incremental `make`
**Row:** `snobol4-snoflake-suite-180-to-100-percent-by-class`

## THE CLAIM

`/home/resources/x64/bin/sbl` — THE CORRECTNESS ORACLE, the binary that under CEO-251 *is* the verdict for
every SNOBOL4 suite — rejects **every documented TRACE second argument** with `ERROR 199 -- trace second
argument is not trace type`. Stock upstream SPITBOL accepts them and traces correctly. The manual documents
the full table. **8 snoflake fixtures fail against a broken instrument, and 3 of them are programs SCRIP
already gets exactly right.**

## MEASURED, ACROSS FOUR BUILDS

Program: `X = 1 ; TRACE('X', '<type>') ; OUTPUT = 'OK'`, staged as `f.sno` through the runner's own
`sbl_listing_sink_flag` staging (short name — the 119-column trap this baton already documented).

| second arg | `x64/bin/sbl` (oracle) | `x64` backup (Aug 22) | `spitbol-bench-oracle/sbl` (stock) |
|---|---|---|---|
| `V` / `VALUE`   | ERROR 199 | ERROR 199 | **runs + traces** |
| `A` / `ACCESS`  | ERROR 199 | ERROR 199 | **runs + traces** |
| `K` / `KEYWORD` | ERROR 199 | ERROR 199 | ERROR 198 (correct: `X` is not a keyword) |
| `L` / `LABEL`   | ERROR 199 | ERROR 199 | ERROR 198 (correct: `X` is not a label) |
| `F` / `C` / `R` | ERROR 199 | ERROR 199 | ERROR 198 (correct: `X` is not a defined function) |

Manual v3.7 p.244 (`TRACE(name1, s1, s2, name2)`) documents exactly: `'A'/'ACCESS'`, `'V'/'VALUE'/null`,
`'K'/'KEYWORD'`, `'L'/'LABEL'`, `'F'/'FUNCTION'`, `'C'/'CALL'`, `'R'/'RETURN'`. Error 198 is *"TRACE first
argument is not appropriate name"* and 199 is *"TRACE second argument is not trace type"*. **The stock
build's 198s are the CORRECT diagnostic** — the type parsed fine and the plain variable `X` was the wrong
kind of name for it. The oracle never gets that far.

## ⛔ THE CLINCHER — IT IS INCOHERENT, NOT A DIALECT CHOICE

The oracle **traces correctly with a null second argument**, byte-identical to stock:

```
$ sbl -bf f.sno     # &TRACE = 100 ; TRACE('X') ; X = 2 ; X = 3
****4*******  X = 2
****5*******  X = 3
DONE                # ← IDENTICAL from x64/bin/sbl AND from stock
```

The manual defines `'V'` and null as **the same trace type**. A build that accepts null-Value and refuses
`'V'`-Value is not expressing a semantic preference; its type-name dispatch is broken while the tracing
engine underneath it works. That is the difference between "this fork chose differently" and "this fork
has a defect", and it is decidable from the binary's own behaviour without reading its source.

## BLAST RADIUS — MEASURED OVER ALL 180, NOT ESTIMATED

Every fixture run through **both** builds with the runner's staging and `@input` extraction
(`scratchpad/oracle_pair.sh`): **180 fixtures, 10 raw disagreements, of which 8 are real.** The other two
(`recursive-expression-recognizer`, `recursive-yz-pattern`) differ only in `execution time msec` inside
SPITBOL's own statistics block — nondeterministic furniture, not semantics.

**So the oracle is independently validated on 172 of 180 snoflake fixtures.** That is the reusable half of
this finding: the other ~49 board reds are NOT oracle-build artifacts, and nobody needs to re-litigate them.

The 8: `trace-procedure`, `trace-function-calls`, `trace-keyword-fnclevel`, `trace-label-flow`,
`trace-value-watch`, `value-trace-during-match`, `stop-tracing`, `twelve-days`.

## ⛔ WHAT THIS COSTS THE BATON, AND IT IS MY OWN NEXT BLOCK

The live `## NEXT` on this row says, in bold: *"START WITH THE ERR199/ERR248 CLASSES, NOT THE 24 OUT->OUT …
they are argument/redefinition VALIDATION we do not implement — a refusal SCRIP never raises — so each is a
small, well-bounded cure with an oracle-exact acceptance test."* Walked as written, that instructs the next
seat to **implement `ERROR 199` refusal of every trace type into SCRIP**. That cure would have:

1. made SCRIP contradict the SPITBOL manual and stock SPITBOL simultaneously;
2. **broken three fixtures SCRIP already passes** — `trace-procedure`, `value-trace-during-match` and
   `stop-tracing` are **byte-identical to stock SPITBOL today**, verified per-fixture;
3. destroyed working `TRACE()` support to make a board go green.

Checked against both engines: `ERR248` is **NOT** affected — both builds agree (`ERROR 285`) across the
whole gimpel set. The pairing of 199 with 248 as one tractable class was the broken oracle's doing.

## WHAT REAL WORK ACTUALLY REMAINS HERE (hq_B's lane, per the 09:4x LANE REVIEW)

Against **stock**, 3 of 7 already pass. The remaining 4 are genuine and are output-format/feature work,
never a refusal:

- **Trace output FORMAT.** SPITBOL prints `****<stmtno>*******  NAME = VALUE`. SCRIP prints
  `<abs-path>:14 stmt 3: TOTAL = 0, time = 0.00195401`. ⛔ Note SCRIP's line carries a **wall-clock time**,
  so that format can never match any pinned ref or oracle stream on any run — it is nondeterministic output
  in a graded stream, which is a defect independent of this whole class.
- **FUNCTION/CALL/RETURN tracing is absent.** On `trace-function-calls` stock emits six call/return lines
  with depth indentation (`****3******* ii FACT(1)`, `RETURN FACT = 1`); SCRIP emits nothing at all.
- `twelve-days` is a genuine `ERROR 160` under stock — a different class, misfiled into 199 by the oracle.

## THE LESSON THIS ROW KEEPS RE-LEARNING FROM A NEW DIRECTION

This is the **third** time this baton's classification has been invalidated by its own instrument: first
CEO-251 changed the question from `@expect` to the oracle; then the 119-column listing-sink truncation
graded error numbers on pathname length; now the oracle binary itself. Each time the *classification* was
re-cut and the *instrument* was assumed.

⭐ **The generalisation worth keeping: "grade against the oracle" silently assumes the oracle is one thing.
There are five `sbl` binaries on this box and they are not interchangeable — two agree with the manual, two
share a fork defect, and one cannot parse `END`.** A verdict that names its tree and its `RT_OPT` and not
its *oracle build* is under-specified. The standing PAIR rule in this baton's ledger (run every suite
against the pre-swap backup and the new binary, report the pair) exists for exactly this and would not have
caught it — **both x64 builds share the defect; the disagreeing arm is a binary the rule never names.**

## ROUTING — NOT FIXED BY ME, AND DELIBERATELY SO

The oracle lives at `/home/resources/x64/`, outside every seat root, and is **hq_P's lane** under THE
SNOBOL4 CUT (*"hq_P csnobol4 + oracle + B"*). Swapping or rebuilding it changes the grading baseline for
**every** SNOBOL4 suite on the board, which is a ruling, not a cure. Reported to the ceo and hq_P with this
witness; non-blocking per THE LOOP, and I am carrying on with the untriaged classes that this census has
just proved are *not* oracle artifacts.

⛔ **Until it is ruled on, no seat should "cure" the ERR199 class.** The `## NEXT` block on the row has been
rewritten and the old one demoted to `## SUPERSEDED-NEXT`.

---

# ⛔⭐⭐ ROOT CAUSE (same seat, ~1h later, on Lon's order "when the oracle is broken, we always stop and fix it") — AND A CORRECTION TO THE SECTIONS ABOVE

**Everything above about the SYMPTOM stands and is re-verified. The ATTRIBUTION above is WRONG and is
corrected here: it says the x64 oracle is broken and stock is correct. The truth is BOTH BUILDS ARE
BROKEN, in opposite places, and I would have "fixed" the oracle by installing a build with a different
defect.**

## THE MECHANISM, LOCATED EXACTLY

MINIMAL has a single opcode `flc` ("fold character"). It is emitted by the translator `asm.sbl`, procedure
`g_flc`. **The complete diff between stock's translator and the fork's is three lines — and it is this:**

```
             stock (bench)                    fork (x64)
  genop('cmp',t1,"'A'")            vs    genop('cmp',t1,"'a'")
  genop('cmp',t1,"'Z'")            vs    genop('cmp',t1,"'z'")
  genop('add',t1,'32')             vs    genop('sub',t1,'32')
        upper -> lower                        lower -> UPPER
```

Introduced by fork commit `e68dfeb` *"SN-30g: rebuilt bin/sbl + resync bootstrap/ from SN-30 sources …
(cc68516 SN-30 — **UPPERCASE canonical case**)"*, which reversed it from `39c9dc9` *"Enable support for the
&case keyword"*. It is baked into the tracked `bootstrap/sbl.asm` at all four `flc` sites.

## ⛔ THE PART THAT INVERTS MY EARLIER ATTRIBUTION: `flc` HAS FOUR CALL SITES AND THEY WANT OPPOSITE THINGS

- **`flstg`** (`sbl.min:21643`, the &CASE name folder) guards `blt wa,=ch_la` / `bgt wa,=ch_l_` — i.e. it
  admits only **a–z** and then calls `flc`. It therefore requires **lower→UPPER**.
- **`trace`** (`sbl.min:28661`) and the **`cnc` control-card scanner** (`19574`, `19681`) fold the first
  character and then compare it against **lowercase** constants (`ch_la equ 97`, `ch_lv`, `ch_li`, `ch_ln`
  …). They therefore require **upper→lower**.

One opcode cannot satisfy both, so **each build is correct in one place and broken in the other**, and I
verified this rather than deducing it:

| | identifier folding (`abc` ≡ `ABC`) | TRACE / control-card dispatch |
|---|---|---|
| `x64/bin/sbl` (correctness oracle) | ✅ prints `5` | ❌ ERROR 199 on every type |
| `spitbol-bench-oracle/sbl` (benchmarks) | ❌ prints null — folding is a silent NO-OP | ✅ works |

⭐ **Both sbl.min files carry the SAME lowercase dispatch constants and the SAME `a–z` guard in `flstg`.**
So the trace dispatch is a defect *in the MINIMAL source itself*, present in both trees, which stock merely
**masks** with a translator that folds the wrong way. Two bugs that cancel in one build and don't in the
other. The manual requires BOTH behaviours, so **neither shipped binary is a correct SPITBOL.**

## ⛔⛔ THE CONSEQUENCE NOBODY HAS PRICED, AND IT IS NOT IN MY LANE

**The BENCHMARK oracle cannot case-fold names.** That is hq_P's timing arm. It is dormant only because
`lib_oracle_flags.sh` mandates `-bf` and `-f` turns folding off, so `flstg` returns at `bze kvcas,fst99`
before reaching the broken fold. ⭐ **The s189 finding that established `-bf` — "SPITBOL case-folds names by
default, `-f` turns it off" — is measured behaviour of the x64 build and is NOT true of the bench build**,
where folding is off no matter what you pass. Any measurement that assumed the two binaries differ only in
LOAD support is under-specified. Told hq_P.

## THE FIX, DESIGNED AND NOT YET BUILT

⛔ **NOT** the three-line translator revert. That trades the trace defect for the folding defect — it would
have made the oracle *look* fixed on my witness while silently disabling `&CASE`, which is the same
"symptom leaves the board, bug stays in the tree" shape this row keeps hitting.

✅ **Keep the fork's `flc` (lower→UPPER — it matches the MINIMAL contract: the comment says "fold to upper
case" and `flstg`'s guard admits only a–z), and repair the THREE dispatch sites to compare against the
UPPERCASE constants**, which already exist with correct values (`ch_ua equ 65`, `ch_ui equ 73`,
`ch_un equ 78`, `ch_uv equ 86`, …). Eleven constants in `sbl.min`:

- `trace`: `ch_la→ch_ua`, `ch_lv→ch_uv`, `ch_lf→ch_uf`, `ch_lr→ch_ur` (×2), `ch_ll→ch_ul`,
  `ch_lk→ch_uk`, `ch_lc→ch_uc` (×2) — `ch_bl` (blank) unchanged
- `cnc01`: `ch_li→ch_ui` · `cnc07`: `ch_ln→ch_un`

That yields a build that is correct on **both** axes — strictly better than either binary on this box, and
self-consistent with its own source rather than depending on two defects cancelling.

## ✅ BUILT AND VERIFIED (CEO-280 ruled hq_B fixes it as the finder; hq_P stands by as owner)

The rebuild went through on a second attempt and the fix is **built and proven in a private `cp -a` copy**
(`scratchpad/x64work`). Eleven constants changed in `sbl.min`, same-width substitutions so MINIMAL's fixed
columns do not shift, and `flstg`'s `a–z` guard deliberately untouched.

**All four acceptance tests pass in ONE binary — which no build on this box achieved before:**

| test | old x64 | stock bench | **fixed** |
|---|---|---|---|
| `TRACE('X','VALUE')` traces | ❌ ERROR 199 | ✅ | ✅ |
| `TRACE('X','value')` traces (folded) | ❌ ERROR 199 | ✅ | ✅ |
| `abc` ≡ `ABC` under `-b` prints `5` | ✅ | ❌ null | ✅ |
| `-bf` correctly case-SENSITIVE (null) | ✅ | ✅ | ✅ |

**Cross-lineage census, all 180 fixtures, fixed vs stock: disagreements 10 → 2**, and both survivors are
only `execution time msec` inside SPITBOL's statistics block — nondeterministic furniture, not semantics.

**Regression check, all 180, old-x64 vs fixed: differs on EXACTLY the 8 trace fixtures** (plus that one
timing entry). Zero collateral. The `cnc` control-card path I also touched was tested directly — `-IN72`
and `-in72` behave identically across old, fixed and stock.

## ⛔ NOT INSTALLED — BLOCKED, AND NOTHING SHARED WAS TOUCHED

`/home/resources/x64` is **byte-identical to how I found it**: `bin/sbl` still `d15160bb…`, no dated backup
created, `sbl.min` unmodified. (The pre-existing `M bin/sbl` and the `sbl.bak-20260904T231932Z` in that
tree predate this session — they are yesterday's swap, not mine.)

The install step — `cp` into `/home/resources/x64`, commit, push the fork, broadcast the swap minute,
re-baseline snoflake, name the commit in `ORACLES.md` — is refused by the harness permission classifier.
That is a correct thing to gate: it re-baselines every SNOBOL4 suite for eight working seats. **Surfaced to
Lon for the decision rather than worked around.** Artifacts are ready and the remaining sequence is
mechanical.
