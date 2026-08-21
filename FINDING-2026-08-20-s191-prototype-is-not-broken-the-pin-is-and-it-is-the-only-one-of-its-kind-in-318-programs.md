# FINDING — s191, seat5, row `prototype-array-dim`: PROTOTYPE IS NOT BROKEN — THE PIN IS, AND IT IS THE ONLY ONE OF ITS KIND IN 318 PROGRAMS

**Session:** 2026-08-20 s191 · seat5 `/home/claude5` · Claude Opus 5 · queue row `prototype-array-dim` (rank 2)
**Landed:** NOTHING IN THE COMPILER. Zero `src/` files touched — the row's premise is falsified and the cure it implies is HQ's precedent call, not mine. Asked as `q-prototype-array-dim`; answer not received at time of writing.
**Watermark:** re-measured on a PRISTINE build at merged SCRIP `bae55c8e` (RT_OPT `-O0`), corpus `c1b653ff`.

---

## 0. THE ROW'S PREMISE IS FALSE, AND THE FALSE HALF IS THE WORD "ORACLE"

The brief says 1110_array_1d *"prints `FAIL 1110/005` where **the oracle and the `.ref`** print `PASS 1110_array_1d (9/9)`."*

**The oracle prints the FAIL too.** Four-way, measured, `< /dev/null`:

| | 1110_array_1d | 1112_array_multi | 1113_table |
|---|---|---|---|
| SCRIP m3 | `FAIL 1110/005` | PASS | PASS |
| SCRIP m4 | `FAIL 1110/005` | PASS | PASS |
| **SPITBOL `sbl -bf`** | **`FAIL 1110/005`** | PASS | PASS |
| CSNOBOL4 `-b` | PASS | PASS | PASS |
| checked-in `.ref` | PASS | PASS | PASS |

SCRIP is **byte-identical to SPITBOL on all three**. The `.ref` for 1110 was pinned from **CSNOBOL4**. There is no SCRIP defect here to fix.

## 1. ROOT CAUSE: PROTOTYPE'S RETURN **DATATYPE**, NOT ITS VALUE — AND THE MANUAL IS ON SCRIP'S SIDE

Both engines return the characters `3`. They disagree on its **datatype**:

```
PROTOTYPE(ARRAY(3))   SPITBOL: dt=INTEGER      CSNOBOL4: dt=STRING      SCRIP: dt=INTEGER
```

The test asserts `DIFFER(PROTOTYPE(a), '3')`, so **the datatype IS the assertion**. `IDENT` is datatype-sensitive
and **all three engines agree it is** — measured, not assumed:

```
IDENT(3,'3') -> DIFFER    IDENT(3,3) -> IDENT    IDENT('3','3') -> IDENT    IDENT(3,3.0) -> DIFFER
```

identical in SPITBOL, CSNOBOL4 and SCRIP. So `DIFFER` is **exonerated**: the return datatype of `PROTOTYPE` is the
only variable in the statement.

**Manual v3.7 p.235 (PROTOTYPE):** *"Returns the prototype string of dimensions used to create the specified array.
**If the array was created by the ARRAY function, then the string returned is identical to the first argument of the
original ARRAY function call.**"* And p.213 (ARRAY) gives two forms — `ARRAY(s,arg)` and **`ARRAY(i,arg)`**, the second
*"used to create one-dimensional arrays (vectors) with i elements"*. `ARRAY(3)`'s first argument **is the integer 3**,
so **INTEGER is the conformant answer** and SPITBOL/SCRIP are right.

**Measured PROTOTYPE surface — SCRIP == SPITBOL 6/6, both modes:**

| created by | PROTOTYPE | dt (SPITBOL == SCRIP) | dt (CSNOBOL4) |
|---|---|---|---|
| `ARRAY(3)` | `3` | **INTEGER** | STRING |
| `ARRAY('3')` | `3` | **INTEGER** | STRING |
| `ARRAY('3,4')` | `3,4` | STRING | STRING |
| `ARRAY('1:10')` | `1:10` | STRING | STRING |
| `ARRAY('0:5,1:3')` | `0:5,1:3` | STRING | STRING |
| `ARRAY('2,3,4')` | `2,3,4` | STRING | STRING |

⭐ **SPITBOL normalises the SINGLE-DIMENSION *string* prototype to an INTEGER too** (`ARRAY('3')` → INTEGER), which is
*not* what "identical to the first argument" says literally, and SCRIP matches that behaviour exactly. **Only the
single-dimension face diverges between the two oracles, in either engine, ever** — which is precisely why 1112 and 1113
are green: they pin `'2,2'`, N-D, and therefore STRING in both.

⛔ **THIS IS WHY THE BRIEF'S "do not fix by special-casing dimension 1" WAS THE RIGHT INSTINCT AIMED AT THE WRONG TARGET.**
Special-casing dimension 1 is *exactly* what it would take to make the current `.ref` pass — it would move SCRIP **off
SPITBOL** to chase a CSNOBOL4 pin, against RULES.md's "SCRIP FOLLOWS SPITBOL SEMANTICS". Not done.

## 2. THE CURE IS TWO CHARACTERS, AND IT MAKES THE TEST STRONGER, NOT WEAKER

```diff
-        DIFFER(PROTOTYPE(a), '3')                   :f(e005)
+        DIFFER(PROTOTYPE(a), 3)                     :f(e005)
-        DIFFER(PROTOTYPE(b), '3')                   :f(e007)
+        DIFFER(PROTOTYPE(b), 3)                     :f(e007)
```

Because `IDENT` is datatype-sensitive (§1, measured), `DIFFER(PROTOTYPE(a), 3)` **failing** pins the value *and* the
INTEGER datatype in one assertion — it is exactly as strong as asserting `DATATYPE(...) = 'INTEGER'` separately, and it
keeps the 9/9 count. The `.ref` then re-pins from `sbl -bf` unchanged (`PASS 1110_array_1d (9/9)`).

⛔ **NOT LANDED, DELIBERATELY.** Re-pinning a `.ref` *away from an oracle* is a precedent about the corpus contract, not
a test edit, and it silently makes 1110 red under CSNOBOL4. Asked HQ; holding.

## 3. THE CENSUS: HOW MANY MORE `.ref` FILES CARRY A CSNOBOL4 PIN? **EXACTLY ONE — THIS ONE.**

Re-pinning one file by hand as a seat trips over it is the wrong shape of cure, so I censused the whole crosscheck
corpus rather than guess at the blast radius. **All 318 `corpus/crosscheck/*.sno`, four ways** — SCRIP m3 vs
SPITBOL `-bf` vs CSNOBOL4 `-b` vs the checked-in `.ref` — run **from the corpus root** (so relative `-include`
resolves) and **fed each program's own `.input`** where one exists (the harness's own convention):

| tag | n | meaning | verdict |
|---|---|---|---|
| `SCR=` | **241** | SCRIP == SPITBOL == CSNOBOL4 == `.ref` | green, fully corroborated |
| `S.Rx` | **66** | SCRIP == SPITBOL == `.ref`; CSNOBOL4 differs | **correct** — SPITBOL is the authority and the pin agrees |
| `.CRx` | **6** | SCRIP == CSNOBOL4 == `.ref`; SPITBOL cannot run it | **oracle gap, pin fine** (§3a) |
| `...=` | **2** | both oracles agree, **SCRIP differs** | **genuine SCRIP defects** (§3b) |
| `...x` | **1** | SCRIP matches neither; oracles disagree | 1 file, named below |
| `..-x` | **1** | **no `.ref` at all** | 1 file, named below |
| `S..x` | 1 | SCRIP == SPITBOL, pin == CSNOBOL4 | ⭐ **`rung11/1110_array_1d.sno` — THIS ROW, AND THE ONLY MEMBER** |

⭐⭐ **THE ROW IS ITS OWN COMPLETE CLASS.** Exactly **one** program in 318 is pinned to CSNOBOL4 against SPITBOL.
Fixing 1110 closes the class outright — there is no second one waiting, and no seat needs to re-run this census.
The 66 `S.Rx` rows are the *reassuring* number: where the oracles disagree, the pin already sides with SPITBOL 66 times
out of 67. 1110 is the single exception, not the tip of anything.

### 3a. The 6 `.CRx` rows are SPITBOL gaps, both DOCUMENTED — not SCRIP defects, and their pins are correct

All six print `ERROR 022 -- undefined function called` under `sbl -bf`, from **two distinct causes**, both confirmed:

- **`rung11/1115_data_basic`, `rung11/1116_data_overlap`** — both call `VALUE('b')`. **Manual v3.7, Appendix
  "Features Not Implemented", item 2: "The VALUE function."** SPITBOL *deliberately* omits it (the SNOBOL4+ table
  lists `VALUE(NAME) value of field or variable, **emulated**` — supplied by `SNOBOL4.inc`, not a builtin).
  ⛔ These are the "PROTOTYPE of a DATA object" files the brief's DONE-WHEN asked about, and the answer is that
  **the DATA prototype face is not what fails in them** — `VALUE` is, two assertions later.
- **`library/test_{case,math,stack,string}`** — all four use lowercase **`-include 'lib/case.sno'`**, which SPITBOL
  **silently ignores**, leaving the library functions undefined. **Proven by cure, not by inspection:** rewriting the
  single directive to uppercase `-INCLUDE` makes `sbl -bf` print the `.ref` output exactly. This independently
  reproduces seat2's s183 include-case class **in a second, unrelated suite** (crosscheck/library, not gimpel).

### 3b. THE DEFECTS THE CENSUS SURFACED — NOT MINE, NAMED SO THEY ARE NOT LOST

- **`patterns/160_pat_alt_inner_gen_resume`** — SPITBOL prints `V=[X]`; **SCRIP DUMPS CORE** (m3). A crash, not a
  wrong answer.
- **`patterns/175_pat_bal_generator_retry`** — SPITBOL prints `A / AB / ABC / done`; SCRIP prints **`A / done`**. The
  generator yields its first result and never retries — a silent wrong answer.
- **`patterns/145_pat_left_assoc_via_arbno_fence`** (`...x`) — matches neither oracle *and* the oracles disagree with
  each other. Named by seat7 at s189 as **not** the alt-seam-tier class (`fb=IR_MATCH_ASSIGN_COND`, `fbtier=2`,
  unmoved); recorded here as still red, not re-diagnosed.
- **`coverage/coverage_sno_nodes`** (`..-x`) — **has no `.ref` at all**, so nothing grades it in either direction. It is
  not passing and not failing; it is unpinned. One file, worth a pin or a deletion decision.

⛔ **I did NOT diagnose 160/175 and do not claim them as new** — both are pattern-engine defects in the
alt-resume / generator-retry neighbourhood that seat6 and seat7 are actively working, and HQ should dedupe them
against those rows rather than mint fresh ones on my say-so. They are reported here because a census that finds them
and stays silent is worse than no census.

⭐ **THE CENSUS ALSO INDEPENDENTLY CORROBORATED seat3's s190 FIX.** Run first on a **stale** binary (my own `efb1cb0b`,
before `git pull`), `rung2/216_indirect_goto_computed` scored `...=` — a genuine defect. Re-run on a **pristine** build
at merged `bae55c8e` it scores `SCR=`, fully green, and **it is the ONLY row in all 318 that changed**. seat3's
`beauty-return-pair-shift` cure is confirmed from outside its own harness, with a clean blast radius of exactly one.
⛔ It is also the reason this census had to be re-run: **a census taken on a stale binary reports other seats' already-
fixed defects as live ones.** Pull and `make pristine` BEFORE the sweep, not after.

## 4. ⭐⭐ THE REAL DEFECT FOUND ON THE WAY: **CONVERT'S ENTIRE STRUCTURAL HALF IS MISSING**, AND IT FAILS SILENTLY

Different mechanism, so **not taken on this row** — proposed as row **`convert-structural`**. Both oracles agree
against SCRIP. m3 and m4 identical.

| call | SPITBOL | CSNOBOL4 | **SCRIP m3 == m4** |
|---|---|---|---|
| `CONVERT(t,'ARRAY')` *(t a TABLE)* | ARRAY | ARRAY | ⛔ **null string** (`dt=STRING`, `SIZE=0`) |
| `CONVERT(a,'ARRAY')` | ARRAY | ARRAY | ⛔ **statement fails** |
| `CONVERT(t,'TABLE')` | TABLE | TABLE | ⛔ **statement fails** |
| `CONVERT(a,'TABLE')` | TABLE | TABLE | ⛔ **statement fails** |
| `CONVERT('ab','PATTERN')` | PATTERN | *(absent)* | ⛔ **statement fails** |
| `CONVERT('ab','EXPRESSION')` | EXPRESSION | EXPRESSION | ⛔ **statement fails** |
| `CONVERT(42,'REAL')` | REAL | REAL | ✅ REAL |
| `CONVERT(1.9,'INTEGER')` | INTEGER | INTEGER | ✅ INTEGER |
| `CONVERT('q','STRING')` | STRING | STRING | ✅ STRING |

**Only the scalar faces work.** Every structural conversion is absent, and — worse than absent — **it does not refuse
loudly**: five of the six make the *statement* fail (control falls through to the next statement, no error, no
diagnostic), and the sixth quietly hands back the null string. A program using CONVERT gets a wrong answer, not a stop.

⭐ **AND IT SHOULD BE CHEAP, BECAUSE THE MACHINERY ALREADY EXISTS:** `SORT(t)` on the same table **correctly** returns
an `ARRAY` whose `PROTOTYPE` is `'2,2'` — exactly the table→array conversion (and exactly the `'N,2'` form the
PROTOTYPE manual entry describes for arrays produced by CONVERT or SORT). The table→array machinery is present and
right; **CONVERT simply is not wired to it.**

⛔ **METHOD TRAP THIS COST ME, WORTH THE NEXT SEAT'S TIME:** my first CONVERT probe concatenated the result into an
`OUTPUT` string. Both oracles died at that line with `ERROR 008 -- concatenation left operand is not a string or
pattern`, while **SCRIP printed a clean empty result and carried on** — which *looks* like SCRIP being tolerant and is
actually SCRIP having returned a string where the oracles returned an array. **The oracle's error was the signal.**
Probe structural results with `DATATYPE()`, never by concatenating them.

## 5. ⛔ TWO INSTRUMENT BUGS OF MY OWN, BOTH CAUGHT BEFORE PUBLICATION, BOTH THE SAME SHAPE

My census was wrong twice before it was right, and both times it **manufactured a defect class that does not exist**.
Recording them because the shape recurs across this fleet's findings:

1. **Ran each program with `cwd` = its own directory.** Relative `-include 'lib/…'` resolves from the **corpus root**,
   so the 4 `library/` tests failed under *both* oracles and were reported `PIN=NEITHER` — a phantom "pins no oracle can
   reproduce" class. Fixed by running from the corpus root; CSNOBOL4 then matches the pin exactly.
2. **Fed `/dev/null` to every program.** Nine programs (`strings/word1-4`, `wordcount`, `cross`, `arith/fileinfo`,
   `arith/triplet`, `control/expr_eval`) have their own `.input` file that the harness feeds as stdin. With empty
   input all three engines agreed on empty-ish output while the `.ref` was pinned *with* input — reported as **9 stale
   `.ref` pins**. Fed correctly, **all nine are `SCR=`, fully green. There are zero stale pins.**

**Both bugs had the same cause: my instrument did not replicate the harness's invocation.** An instrument that
diverges from the harness in `cwd` or stdin does not report *noise* — it reports a **clean, plausible, entirely false
class**, which is the s33 "non-empty is not alive" signature wearing new clothes. ⛔ **A census is a harness; copy
`run_one`'s invocation, do not re-derive it.**

## 6. WHAT IS AND IS NOT CLAIMED

- **NOT CLAIMED: the row's DONE-WHEN.** `1110_array_1d` does **not** pass, and I did not make it pass, because every
  route to that from inside the compiler is a regression away from SPITBOL. The cure is a two-character test edit plus
  a `.ref` re-pin, prepared in §2 and **held for HQ's ruling**.
- **DELIVERED:** root cause with the manual behind it; the N-D and DATA prototype faces verified (§1, §3a); a second
  defect named with a proposed row (§4); the blast radius of the pin question measured to exactly one file (§3).
- **corpus fail-set:** no compiler file touched, so unchanged by construction. RULES step-4 regen **NOT APPLICABLE**.
