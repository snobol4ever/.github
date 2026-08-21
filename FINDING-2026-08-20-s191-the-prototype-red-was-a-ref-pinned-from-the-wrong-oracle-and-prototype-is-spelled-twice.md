# FINDING — s191 seat5 (`/home/claude5`, Claude Opus 5) — queue row `prototype-array-dim`, rank 2

## ⭐⭐⭐ THE RED WAS NOT A COMPILER DEFECT. THE `.ref` WAS PINNED FROM THE WRONG ORACLE, AND THE REAL DEFECT IS THAT `PROTOTYPE` IS SPELLED TWICE.

**WATERMARK (pristine at SCRIP `21819132`, RT_OPT `-O0`, corpus `6913c6e8`, tree clean):** broad corpus board
**m3 334/3 · m4 327/9 · SKIP 1 (337)**, up from the standing **m3 332/5 · m4 325/11 · SKIP 1**.
⛔ **THE +2/+2 IS NOT ALL MINE AND SAYING SO IS THE POINT:** my row cures `1110_array_1d` (+1/+1); the other
+1/+1 arrived with the rebase, seat7's `21819132` ALT-TAIL-RESUME. A board run after a rebase measures the
*merged* tree, and attributing its whole delta to your own rung is how a watermark becomes a lie.
**⛔ `.s` REGEN NOT APPLICABLE — ZERO COMPILER FILES TOUCHED** (`git diff --name-only` over `src/`, `emit*`,
`x86_asm*`, `lower_*` = **0**). The rung is two corpus files and two new probes.

## ⭐⭐ THE MEASUREMENT THAT DISSOLVED THE ROW — THREE ENGINES, ONE PROGRAM

The brief stated *"the oracle and the `.ref` print `PASS 1110_array_1d (9/9)`"*. **The oracle does not.**

| engine | `crosscheck/rung11/1110_array_1d.sno` |
|---|---|
| SCRIP m3 **and** m4 | `FAIL 1110/005: PROTOTYPE(ARRAY(3))=3` |
| SPITBOL `sbl -bf` | `FAIL 1110/005: PROTOTYPE(ARRAY(3))=3` |
| CSNOBOL4 `snobol4 -b` | `PASS 1110_array_1d (9/9)` |
| the checked-in `.ref` | `PASS 1110_array_1d (9/9)` |

**SCRIP already agreed with SPITBOL byte for byte. The pin agreed with CSNOBOL4** — the engine RULES.md does
**not** name as the authority for SNOBOL4. This is exactly the class my own s191 census commit (`6e112617`)
counted as *"1 `S..x` — the pin is from the WRONG oracle"*; the row is that census row's single instance.

**The two oracles genuinely disagree, and the disagreement is a DATATYPE, not a value.** For a **1-based 1-D**
array SPITBOL normalises the prototype to the **INTEGER** upper bound; CSNOBOL4 returns the **STRING** `'3'`:

```
DATATYPE(PROTOTYPE(ARRAY(3)))      SPITBOL INTEGER   SCRIP INTEGER   CSNOBOL4 STRING
DATATYPE(PROTOTYPE(ARRAY('3')))    SPITBOL INTEGER   SCRIP INTEGER   CSNOBOL4 STRING
DATATYPE(PROTOTYPE(ARRAY('1:3')))  SPITBOL STRING    SCRIP STRING    CSNOBOL4 STRING
IDENT(PROTOTYPE(ARRAY(3)), '3')    SPITBOL FAILS     SCRIP FAILS     CSNOBOL4 SUCCEEDS
IDENT(PROTOTYPE(ARRAY(3)),  3 )    SPITBOL SUCCEEDS  SCRIP SUCCEEDS  CSNOBOL4 FAILS
```

`DIFFER`/`IDENT` compare **datatype AND value**, so the old assertion `DIFFER(PROTOTYPE(a), '3')` was not
testing the prototype at all — **it was asserting CSNOBOL4's datatype**, and every engine that gets SPITBOL
right must fail it.

**THE CURE IS ONE TOKEN PER ASSERTION AND IT IS STRICTLY STRONGER THAN WHAT IT REPLACES.** Assertions 005 and
007 now compare against the bare numeral `3`. Because `IDENT` does not coerce in either engine, the bare
numeral asserts the SPITBOL **value and datatype together** — a regression to `STRING '3'` now fails a test
that the string form would have passed. 9/9 preserved, `.ref` untouched, m3 ≡ m4. CSNOBOL4 now fails the
program, which is correct: it encodes the declared authority's semantics.

## ⛔⭐ THE BRIEF'S OWN PROHIBITION WAS RIGHT, AND THE SWEEP IS WHY

The brief said **⛔ *do not fix by special-casing dimension 1***. Following it was load-bearing: a dim-1 special
case would have made SCRIP return `STRING '3'` and **broken** an agreement it already had. The whole prototype
surface was swept rather than the one face the row was named for, and **every other face was already exact**:

```
ARRAY(3) ARRAY('3') => INTEGER 3     ARRAY('1:3') => '1:3'      ARRAY('2,3')     => '2,3'
ARRAY('1:2,1:3') => '1:2,1:3'        ARRAY('0:5') => '0:5'      ARRAY('-2:2')    => '-2:2'
ARRAY(' 3 ')     => ' 3 '            ARRAY('2,3,4') => '2,3,4'  ARRAY(3,'x')     => 3
```

`1112_array_multi` (N-D string form) and `1113_table` (the CONVERT/SORT `N,2` form the manual documents at
p.235) already **PASS in all three engines**. The divergence was the 1-based 1-D face alone, and SCRIP had it
right. ⭐ **A row that names one face is not a licence to look at one face** — the sweep is what turned
"fix the builtin" into "the builtin is correct and the test is wrong."

## ⛔⭐⭐⭐ THE REAL DEFECT, FOUND ONLY BECAUSE THE FIRST ONE EVAPORATED — `PROTOTYPE` HAS TWO IMPLEMENTATIONS AND BOTH ARE LIVE

| | site | 1-based 1-D array | TABLE | non-object |
|---|---|---|---|---|
| **live at `nargs==1`** | `src/runtime/by_name_dispatch.c:6827` `BID_PROTOTYPE` | **INTEGER 3** ✅ | FAIL ❌ | FAIL ❌ |
| **live at `nargs!=1`** | `src/runtime/core/core.c:1596` `_PROTOTYPE_` (registered `:1752`) | **STRING `"1:3"`** ❌ | `""` ❌ | FAIL ❌ |
| **SPITBOL** | — | INTEGER 3 | INTEGER 11 / 5 / 5 | **ERROR 164** |

**The second spelling is not dead code — one extra argument reaches it:**

```
PROTOTYPE(a,1)   SPITBOL: INTEGER 3        SCRIP: STRING 1:3
PROTOTYPE(TABLE(),1)  SPITBOL: 11          SCRIP: (empty)
```

Manual Ch.8 (the same passage `src/contracts/stage2.h` already cites for `nformals`) says **excess arguments
are evaluated then IGNORED** — so `PROTOTYPE(a,1)` *must* answer exactly `PROTOTYPE(a)`. SPITBOL obeys;
**SCRIP changes implementation.** This is the `spelled-twice disease` RULES.md names, with the two spellings
disagreeing on both the value and the datatype.

**Three divergences filed, two probed and one deliberately not:**

1. **`probe/proto/proto_excess_arg`** — checked in RED, ref from the live oracle. Ships its **green 1-argument
   controls in the same file**, so the refused ingredient is isolated to the excess argument: not `PROTOTYPE`,
   not the array, not the datatype.
2. **`probe/proto/proto_table`** — checked in RED, ref from the live oracle. `TABLE()` ⇒ **11**, `TABLE(5)` ⇒ 5,
   `TABLE(5,7)` ⇒ 5 (the second argument is the value-block size, **not** the header count). Green ARRAY control.
3. **`PROTOTYPE` of a STRING / INTEGER / DATA object is `ERROR 164 -- prototype argument is not valid object`**
   in SPITBOL and a **silent statement FAILURE** in SCRIP. ⛔ **Named but NOT probed, on purpose:** its oracle
   arm is a fatal report, and no `.ref` may pin a SPITBOL error dump — the trap s190 filed and s191's
   `gimpel-suite-harness` filed again (`sbl` exits **0** after a fatal error). A probe I cannot pin honestly
   is a FINDING row, not a corpus file.

Both probes verified **m3 ≡ m4** before checking in. Queue row **`prototype-spelled-twice`** (rank 2) carries
the fix with its own DONE-WHEN; it is a different mechanism from this row (dispatch, not arithmetic), which is
why it is a row and not a silent extension of this one.

## ⭐ THE GENERALISABLE MOVE — **A RED IS A DISAGREEMENT BETWEEN TWO THINGS, AND THE `.ref` IS ONE OF THEM**

Every harness that grades against a single pinned file quietly asserts that the pin is right. `test_corpus_snobol4.sh`
compares **against `.ref` only** — which is why 1110 read as a builtin bug for as long as it did — while
`scorecard_snobol4.sh` passes a row that matches **the pin OR the live oracle**, and would already have scored
this program green. ⭐ **Two harnesses over one program disagreed, and the disagreement was the evidence.**
When a program is red on one board and green on another, **diff the boards' grading rules before debugging the
compiler.** Same family as s191's *"a lookup that prints is not a lookup that checks"* and s189's
`default: return 0` — a default that nobody chose, wearing the face of a measurement.

⛔ **AND THE CHEAPEST CHECK CAME FIRST AND SHOULD HAVE ALL ALONG:** the row was dissolved by running the witness
under `sbl -bf` — **one command, two minutes, before reading a line of runtime source**, exactly as the brief's
FIRST STEP instructed. The brief was wrong about what that command would print, and running it anyway is what
found that out.

## NEXT
1. **`prototype-spelled-twice`** (queue, rank 2) — make the two spellings ONE authority; cures the TABLE face and
   the excess-argument face together. Do **not** patch `_PROTOTYPE_` to imitate the other, and do **not**
   special-case an argument count.
2. **The `.ref` provenance question is bigger than this row.** My census (`6e112617`,
   `scripts/util_crosscheck_two_oracle_census.sh`) found **66 rows whose pin sides with SPITBOL** (correct),
   **6 SPITBOL cannot run**, **1 no `.ref` at all**, and this **1 wrong-oracle pin**. The 1 is now 0. The 6 and
   the 1-with-no-pin are unexamined and each is a program nobody can currently grade.
