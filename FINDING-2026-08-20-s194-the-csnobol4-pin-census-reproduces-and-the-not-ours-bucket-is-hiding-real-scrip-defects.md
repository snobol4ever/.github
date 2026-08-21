# FINDING s194 (seat2) — THE csnobol4-suite PIN CENSUS REPRODUCES, AND THE "NOT OURS" BUCKET IS HIDING REAL SCRIP DEFECTS

**Row:** `csnobol4-pin-provenance` (rank 0). **Measured at SCRIP `c43d8f51` · corpus `fea93a27` · .github `e1881104`, all three trees CLEAN, RT_OPT `-O0`.**
**ZERO FILES CHANGED IN SCRIP OR corpus.** The suite was copied to a scratchpad before any engine ran, because several programs do file I/O (`popen2.dat`, `openo.tst`, `test.bin`, `B,U`) and an in-place census would have written into the corpus tree. `git status --porcelain` is empty in all three repos; this FINDING is the only file added.

---

## 0. THE ANSWER TO THE ROW'S QUESTION — THE STRUCTURAL FACT IS REAL AND IT REPRODUCES

**HQ was right that the suite's score is not a statement about SCRIP.** The census reproduces the shape of HQ's s191 result independently, twice, from a clean room. But three of the brief's supporting claims are wrong on the facts, and **the correction runs in the direction nobody audits: the "not ours" bucket is too big, and it has real SCRIP defects inside it.**

| | HQ s191 | seat2 s194 (SCRIP `c43d8f51`) |
|---|---|---|
| dialect programs excluded by construction | 21 | **21** (reproduced exactly, independently — see §2) |
| non-dialect board reds | 62 | **56** |
| pin reproducible by live SPITBOL | 10 | **9** |
| pin NOT reproducible by live SPITBOL | 52 | **47** |

The counts moved because **cures landed between s191 and `c43d8f51`** — `collect2`, HQ's own residue-six item (a), is now `PASS/PASS`. The *structure* is identical. **The structural fact stands: most of this suite's reds are not gradeable against SPITBOL.**

---

## 1. THE INSTRUMENT — AND WHY IT IS NOT THE SHIPPED ONE

The brief says to reuse `scripts/util_crosscheck_two_oracle_census.sh`. **That script is hardwired to `corpus/crosscheck` (`CC="$S4E/corpus/crosscheck"`, `find ./crosscheck`) and cannot see `programs/csnobol4-suite` at all.** Editing it was not an option (ZERO FILES CHANGED), so what was reused is the thing that actually matters — **its law, stated in its own header: *"A census is a harness: copy run_one's invocation, never re-derive it."*** The census copies `scorecard_snobol4.sh` verbatim for this suite's row (`csnobol4_suite 5 programs/csnobol4-suite -maxdepth 1 -name *.sno SELFDIR 20 -`): oracle cwd = the program's dir, `SETL4PATH=".:SELFDIR"`, `sbl -bf -d512m -i64m`, `stdin_for` for `.in`/`.input`, `timeout 60` oracle / `20` run, and `grade()` copied line-for-line.

⛔ **THE BRIEF SAYS `sbl -b`. RULES.md SAYS `-bf` ALWAYS, AND RULES.md WINS.** `-f` is the oracle's language switch (s189): SCRIP is CASE-SENSITIVE, `-b` grades it against a case-folding language it is required not to speak. **Both arms were measured anyway**, because that is exactly what separates a *case-dialect* split from a *provenance* split — and it earned its keep: 3 programs (`conv2`, `func2`, `space`) have pins that **only** the folding arm reproduces. Those are dialect, not provenance, and a `-bf`-only census would have mislabelled them.

---

## 2. THE 21 DIALECT PROGRAMS — REPRODUCED FROM THE SOURCE, NOT TAKEN ON TRUST

The brief says the 21 lowercase-keyword programs "were EXCLUDED from this census by construction" but does not name them. Detecting the s189 signature directly — a lowercase special name used as an assignment target, `grep -lE "(^|[^A-Za-z._&])(output|input|terminal)[ \t]*="` — returns **exactly 21 programs**, an independent arrival at HQ's own number:

> `base bench breakline case1 conv2 crlf diag1 diag2 hide json1 k noexec random setexit setexit5 setexit6 setexit7 sleep space space2 tab`

**2 of the 21 are already GREEN** (`noexec`, `space2`), so 19 are red and excluded below.

---

## 3. THE 52/10 SPLIT, PUBLISHED BY NAME — AND THEN SPLIT AGAIN ON THE QUESTION THAT DECIDES DISPOSITION

All 124 programs, classified. Sums to 124. Both runs agree (§6).

**(0) GREEN — 49**
> `100func 8bit alph alt1 alt2 any bal case2 cat char collect collect2 contin digits fact factor float fun1 fun2 hello ind len lgt local longline longrec loop match match2 match3 match4 matchloop noexec openo ops pad punch repl reverse roman setexit2 space2 str sudoku uneval unsc vdiffer words words1`

**(1) DIALECT-21, red — 19** (excluded by construction; row `kw-uppercase-dialect` owns these)
> `base bench breakline case1 conv2 crlf diag1 diag2 hide json1 k random setexit setexit5 setexit6 setexit7 sleep space tab`

**(2) THE 9 — pin IS reproducible by live SPITBOL, SCRIP red ⇒ genuinely ours**
> `breakx comment convert end intval lexcmp nqueens setexit3 substr`

These map exactly onto HQ's existing rows: `substr`→`substr-zero-length`; `breakx`→`breakx-no-extend-runaway`; `comment`+`end`→`lower-fatal-bombs-two`; `convert intval lexcmp nqueens setexit3`→5 of `csnobol4-residue-six`. **The 6th, `collect2`, is now `PASS/PASS` — see §5.**

**(3) PLACEHOLDER PIN — 9 non-dialect (11 in total)** ⭐ **A CLASS NO ROW NAMES YET**
> `a dump ftrace keytrace spit t trace1 trace2 trfunc` (+ dialect `diag1 diag2`)

**(4) NO LIVE SPITBOL DOOR — 26** (oracle dead or rc≠0; the pin is the only grader and it is unreachable)
> `8bit2 alis file float2 func2 function genc include2 include3 include4 label labelcode line2 loaderr maxint ndbm openi openo2 ord popen popen2 rewind1 scanerr setexit4 time update`

**(5) LIVE DOOR EXISTS AND SCRIP DISAGREES WITH LIVE TOO — 12**
> `atn err include line pow preload1 preload2 preload3 preload4 trim0 trim1 uneval2`

### ⛔⭐⭐⭐ THE SPLIT THAT ACTUALLY DECIDES THE QUESTION

"Whose .ref is it" is the wrong first cut, because **a program that never produced output cannot have been failed by its .ref.** Cutting the 56 non-dialect reds on *did SCRIP produce comparable output* × *does live SPITBOL run the program*:

| | SPITBOL RUNS IT | SPITBOL CANNOT RUN IT |
|---|---|---|
| **SCRIP fails structurally** (parse/compile/crash/timeout) | **(A) 17 — ⛔ SCRIP DEFECTS** | (B) 22 — SCRIP may be *agreeing*; red is a grading artifact |
| **SCRIP runs, output differs** | (C) 9 — provenance *can* explain these | (D) 8 — pin unreachable, ungradeable |

**(A) = `atn breakx comment end include intval lexcmp line nqueens pow preload1 preload2 preload3 preload4 trim0 trim1 uneval2`**

Tightened to the airtight core — live SPITBOL emits **real, non-empty output** and SCRIP still cannot compile or run the program:

> **A1 (8, airtight): `breakx comment include intval lexcmp line nqueens pow`**
> A2 (9, weaker — `sbl` exits 0 but prints *nothing*, so the oracle may be silently failing): `atn end preload1 preload2 preload3 preload4 trim0 trim1 uneval2`

⛔ **THREE OF THE AIRTIGHT EIGHT — `include`, `line`, `pow` — ARE INSIDE HQ's "52 NOT OURS".** HQ's framing would have written them off as CSNOBOL4 provenance. They are SCRIP defects, and two of them share one root cause found this session (§4).

---

## 4. ⭐⭐⭐ THE ROW PAID FOR ITSELF: A NAMED, ROOT-CAUSED SCRIP BUG THAT WAS FILED UNDER "NOT OURS"

`include.sno` and `line.sno` both fail with:

```
snobol4:8: error: cannot open include 'line2.sno '
```

**Note the trailing space inside the quotes.** The source is deliberate — `include.sno:4` and `line.sno:8` read:

```
-INCLUDE "line2.sno "
```

while lines 2 and 6 read `-INCLUDE "line2.sno"`. **The program is a test that the `-INCLUDE` filename is right-trimmed**, `line2.sno` exists in the suite, live SPITBOL trims it and runs the program, and **SCRIP does not trim and refuses to parse the file.** One missing trim; two programs; sitting in the bucket labelled *"SCRIP could not pass them without abandoning SPITBOL semantics."*

⛔ **NOT the same defect: `include2/3/4` reference `aa.sno`/`bb.sno`, which do not exist in the suite at all — SPITBOL fails them too (rc=1). Those are missing fixtures (class B) and SCRIP is right to refuse them.** Naming them together would have manufactured a four-program class out of a two-program one.

---

## 5. THE FOUR BUILTINS — NAMED, AND THE BRIEF IS WRONG ON TWO OF THEM

The brief: *"probing each against the LIVE ORACLE shows SPITBOL ITSELF RAISES 'undefined function' for all four (controls CHAR and SUBSTR return correct values, so the probe is sound)"*. Probed with one minimal witness per function through `sbl -bf`; **ERROR 022 = "Undefined function called" (v3.7 p.271)**:

| function | live `sbl -bf` verdict | manual v3.7 |
|---|---|---|
| `ORD("A")` | **`ERROR 022 -- undefined function called`** | **0 hits.** Not a SPITBOL function. |
| `BREAKPOINT(15,1)` | **`ERROR 022`** | **0 hits** as a function (only Ch.10 prose about planting a *machine* breakpoint) |
| `SET(5,0,1)` | **`ERROR 022`** | ⛔ **DOCUMENTED** — `SET(channel,i1,i2)`, "Position file", in the manual's own **Built-in functions** table (p.237) |
| `REWIND(5)` | ⛔ **`ERROR 174 -- rewind file does not exist`** | ⛔ **DOCUMENTED** — `REWIND(channel)`, p.127/137/237, with its own error family 172–176 |
| `CHAR(65)` (control) | `A` | ✅ probe sound |
| `SUBSTR("hello",1,3)` (control) | `hel` | ✅ probe sound |

**Two corrections, and each matters in a different way:**

1. ⛔ **`REWIND` IS IMPLEMENTED IN SPITBOL AND THE ORACLE PROVES IT.** It raised an *argument* error from its own documented 172–176 family, not ERROR 022. It is **not** a CSNOBOL4-only builtin. Every `REWIND` call in the suite passes an **integer channel** (`rewind1.sno:2 REWIND(5)`, `update.sno:11 REWIND(10)`) — precisely SPITBOL's documented signature.
2. ⭐ **`SET` IS DOCUMENTED BUT NOT IMPLEMENTED** in this oracle binary (`spitbol v4.0f`). The manual lists it; the binary refuses it. **The oracle grades, not the manual** — but a seat reading only the manual would have concluded SCRIP must implement `SET`, and a seat reading only the brief would have concluded SPITBOL has no `SET` at all. Both are wrong.

⛔ **AND THE CALL CENSUS IS 5 PROGRAMS OF 124, NOT A STRUCTURAL CAUSE.** True (non-comment) call sites: `ORD` → `ord.sno` only; `REWIND` → `rewind1 update bench`; `SET` → `update`; `BREAKPOINT` → `keytrace`. **`collect2.sno:5` and `genc.sno:1322` are COMMENT lines (`*` in column 1) and call nothing.** The function-level probe is therefore **corroboration on 5 programs, not an independent confirmation of the 52-program class** — and HQ's residue-six item (a) rests on it: *"collect2 — it calls ORD, which the LIVE ORACLE ALSO REFUSES"*. **`collect2` does not call `ORD`, and it is now `PASS/PASS` in both modes with a pin live SPITBOL reproduces.**

---

## 6. REPRODUCIBILITY — RUN TWICE, AND THE ONLY MOVER IS THE ONE seat5 WARNED ABOUT

Two full independent runs of the identical script, sequential (never concurrent — seat5's s189 `scorecard-provenance` row is exactly this suite being corrupted by a co-tenant):

| column | programs differing / 124 |
|---|---|
| **provenance VERDICT** | **0** ✅ |
| **board m3** | **0** ✅ |
| board m4 | **1** — `nqueens` only (`TIMEOUT` vs `SIG11`) |
| SCRIP m3 / pin md5 / CSNOBOL4 status | **0** ✅ |
| `sbl -bf` status | 1 — `keytrace` (`RC231` vs `RC139`; **both non-live, so no class moves**) |
| `md5_live` | 12 — ⛔ **every one of them on a DEAD or rc≠0 arm.** No LIVE arm's output changed. Only crash-dump *text* varies, which is the s189 fact restated. |

**`nqueens` is exactly the program seat5's row says to distrust on a single draw**, and it flapped here on an idle box — recorded, not smoothed.

⭐ **CSNOBOL4 ITSELF IS NONDETERMINISTIC ON 4 PROGRAMS** (`keytrace spit t trace1`), all LIVE: its `&TRACE` output embeds wall-clock timings (`time = 0.022` / `time = 0.0129999999999999`). A future seat re-pinning from CSNOBOL4 on those four would pin a flapping value.

---

## 7. ⭐⭐ A CLASS NO ROW NAMES: 11 PINS ARE NOT ENGINE OUTPUT AT ALL

`trace1.ref` reads:

```
trace1.sno:3 stmt 3: FOO = 1, time = xxx
```

**`xxx` is a literal placeholder.** These pins are CSNOBOL4's own test-harness output **after normalization** — Budne's suite sed-replaces the volatile timing field before comparing. Today's CSNOBOL4 2.3.3 prints `time = 0.` and **cannot reproduce its own pin either**; live SPITBOL prints a completely different trace format (`****3*******  foo = 1`).

**11 pins carry `xxx`, and all 11 are board-red:** `a diag1 diag2 dump ftrace keytrace spit t trace1 trace2 trfunc` (9 non-dialect).

⛔ **This is a strictly worse case than "the wrong oracle."** Reproducing these needs the right engine *and* the right post-processor. **No engine — SPITBOL, CSNOBOL4, or SCRIP — can ever match them byte-for-byte.** They are unpassable by construction and will sit red forever under any disposition that does not touch them.

---

## 8. ⛔⭐⭐ THE FACT THAT CHANGES WHAT DISPOSITION (a) IS WORTH

**`run_one`'s `grade()` already falls back to the live oracle:**

```
{ [ $have_pin  = 1 ] && cmp -s "$o" "$W/pin";  } && { echo PASS; return; }
{ [ $have_live = 1 ] && cmp -s "$o" "$W/live"; } && { echo PASS; return; }
```

A program passes if SCRIP matches **the pin OR live SPITBOL**. Therefore:

- **A CSNOBOL4-provenance pin cannot, by itself, make a program red.** If SCRIP matched live SPITBOL, the board would already have passed it through the second door. Every one of the 47 is red because SCRIP *also* fails to match live SPITBOL — or because there is no live SPITBOL at all.
- ⛔ **DISPOSITION (a) — "re-pin the 52 from live SPITBOL where SPITBOL runs them" — IS VERY NEARLY A NO-OP FOR THE SCORE.** Where SPITBOL is live and SCRIP already agrees with it, the board is *already* green. Re-pinning changes the stored bytes, not the verdict.
- The programs that genuinely cannot be rescued are **(B) 22 + (D) 8 = 30 with no live SPITBOL door**, plus the **9 non-dialect placeholder pins**, which no re-pin from any engine can fix without also fixing the normalizer.

**`scorecard_snobol4.sh` already emits a `pin!=live` note per program — the harness has been computing this fact all along and nothing was reading it.**

---

## 9. AN INVENTORY DEFECT FOUND IN PASSING

The README says "124 `.sno`, 125 `.ref`", which reads as one-to-one plus a spare. It is not:

- **3 ORPHAN `.ref` with no program:** `callgraph.ref`, `proc.h.ref`, `static.h.ref`
- **2 programs with NO pin:** `bench.sno`, `line2.sno` — graded live-only, and **both have a dead/rc≠0 oracle, so neither can ever pass** (seat1's `ref-the-ungraded-suites` class)

122 paired + 3 orphans = 125 refs; 122 paired + 2 unpinned = 124 programs.

---

## 10. ⛔ THE QUESTION, ASKED — NOT DECIDED. NO FILE WAS CHANGED.

Asked via `s4e_msg.sh ask csnobol4-pin-provenance`. Evidence: this FINDING; census TSVs (both runs) in the seat's scratchpad.

The disposition is **Lon's**, and the measurement says the brief's three-way choice is **under-specified — the suite is at least five populations, not one**, and they do not take the same disposition:

1. **The 8 airtight SCRIP defects** (`breakx comment include intval lexcmp line nqueens pow`) — **not a disposition question at all.** They are ours; 3 of them (`include`, `line`, `pow`) are currently mis-filed as "not ours" and `include`/`line` already have a root cause. **Recommend: a row.**
2. **The 9 placeholder pins** — unpassable by every engine. Disposition (a) cannot reach them and (b) is the only honest option unless someone ports the normalizer.
3. **The 30 with no live SPITBOL door** — the real "cannot be graded against SPITBOL" class. seat5's gimpel precedent (mark out-of-dialect, stop scoring) fits these.
4. **The 9 where both engines run and outputs differ** — the only population where re-pinning changes a verdict, and each needs looking at individually.
5. **The 19 red dialect programs** — already owned by `kw-uppercase-dialect`; untouched here.

⛔ **AND THE SCORE QUESTION UNDERNEATH IT:** `csnobol4_suite` carries **5 META weight**. Whatever is decided, **9 pins in it are unmatchable by any engine and 2 programs have no pin at all** — so the suite's ceiling is below 124/124 no matter how good SCRIP gets, and that ceiling has never been stated. **A weighted suite with an unreachable maximum reports a permanent deficit as a SCRIP shortfall.**

---

## 11. GENERALISABLE

⭐ **"Whose oracle produced the pin" is the second question. The first is "did the engine under test produce output at all."** 39 of these 56 reds never reached the comparison — SCRIP parse-errored, refused to compile, crashed or hung. **A provenance census that skips that cut will file every compile bomb under "wrong oracle", and it fails in the flattering direction**: the bucket labelled *not our fault* is the one nobody re-audits. Cut on *did we produce output* first, *does the oracle run it* second, and only then ask whose pin it is.

⭐ **A pin containing a literal placeholder is not a pin.** Grep every `.ref` for normalization artefacts (`xxx`, `time = `, `0x…`) before trusting a suite's score; a suite can carry an unreachable ceiling for years without one red line ever saying so.

⭐ **When a brief hands you a list of "functions the oracle does not have", call them.** Two of these four were in the manual's own Built-in Functions table and one of those two answered from its own documented error family. **The oracle is the authority over the manual, and both are authorities over the brief.**
