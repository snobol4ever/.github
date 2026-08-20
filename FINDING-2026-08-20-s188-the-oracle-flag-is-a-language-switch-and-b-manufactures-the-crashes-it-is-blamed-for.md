# FINDING — s188 (seat1, Opus 5; queue lane: successor to `lon-include-root`, the `-b`/`-bf` row)

## THE ORACLE FLAG IS A LANGUAGE-SEMANTICS SWITCH, `-b` MANUFACTURES THE CRASHES IT IS BLAMED FOR, AND THE M1 PROGRAM'S ORACLE IS NONDETERMINISTIC UNDER THE FLAG 13 OF 14 SUITES USE

**Watermark:** SCRIP `213771e2`, corpus `66259281`, both trees clean, RT_OPT `-O0`. **No compiler source touched, no corpus program touched.** One new script (`scripts/util_oracle_flag_sweep.sh`) and this FINDING. RULES step-4 `.s` regen NOT APPLICABLE.
**⛔ `corpus/programs/lon/` was never enumerated, run, or compiled.** The sweep tool carries two independent locks (suite not listed + per-path guard). This is why the row was measurable at all: `scorecard_snobol4.sh` runs the `lon` suite and is therefore currently unrunnable, so the whole measurement was rebuilt on a lon-safe harness.

## 1. WHAT THE FLAG ACTUALLY IS — FROM THE MANUAL, NOT FROM TASTE

`scorecard_snobol4.sh:80` runs the live oracle as `sbl -b` for **12 of its 13 suites — 11 once the off-limits `lon` suite is set aside** and `sbl -bf` for `beauty_self` alone. CLAUDE.md documents `-bf` purely as a SIGSEGV workaround. That is wrong, and the manual is unambiguous (line numbers are `pdftotext -layout` of `1-spitbol-manual-v3.7.pdf`):

- **l.6943** `-b` = "suppress SPITBOL's two-line screen sign-on message". Cosmetic. That is its *whole* job.
- **l.6945** `-f` = "don't fold lower-case names to upper case".
- **l.1205** "Normally, SPITBOL performs case-folding on names … so that `Buffer`, `buFFer`, and `BUFFER` are all equivalent."
- **l.7049** (Defaults) "All variable names are folded to upper-case during compilation and execution."
- **l.7531** labels fold too; **l.7743-7747** the indirect-reference operator `$` folds the string it converts; **l.7891** `&CASE` reports the state.
- **l.11074-11077** — decisive: "All lower-case letters appearing in a name are by default folded to upper case … **If compatibility with standard SNOBOL4 is desired, disable case-folding via the –f command line option or the –CASE control statement.**"

So folding is SPITBOL's **deviation** from standard SNOBOL4, `-f` is the conformance switch, and `RULES.md` declares **SCRIP IS CASE-SENSITIVE**. ⭐ **The tree already knew this and never propagated it:** `util_run_beauty_oracle.sh:61` says *"-bf: -b suppress banner, -f case-sensitive"* and `test_monitor_3way_sync_step_auto.sh:205` says *"Run with -bf for case-sensitive identifiers"*. The `-bf` half of the tree documents the correct reason; the **scoring** half runs `-b`.

## 2. THE MEASUREMENT — THREE ARMS, BECAUSE TWO ARMS LIE

`scripts/util_oracle_flag_sweep.sh sweep` runs **three** arms per program: `-b`, `-b` **again (control)**, `-bf`; `^iters:`/`^ms:` deleted from all three (the scorecard's own `norm=ms` rule) before hashing.
**1786 programs, 12 suites: `same` 1683 · `MOVER` 77 · `FLAKY` 26.**
⛔ **The control arm is not ceremony.** The naive two-arm form reported **103** movers; three arms report **77 + 26 flaky**. ~26 of the "movers" were timing-bearing or runaway programs disagreeing with *themselves*. A flag sweep without a same-flag control arm reports its own noise as signal.

**The oracle's own health, per arm, same 1786 programs:**

| oracle exit | `-b` (folding) | `-bf` |
|---|---|---|
| rc=0 clean | 1590 | 1556 |
| rc=1 refused | 168 | 216 |
| rc=231 ERROR exit | 7 | 2 |
| **rc=139 SIGSEGV** | **19** | **12** |

## 3. ⭐⭐⭐ THE HEADLINE — beauty's ORACLE IS NONDETERMINISTIC UNDER `-b` AND BYTE-STABLE UNDER `-bf`

Three runs each, `beauty.sno < beauty.sno`, SETL4PATH=.:

| arm | run 1 | run 2 | run 3 | bytes |
|---|---|---|---|---|
| `sbl -b` | rc=**139** | rc=**139** | rc=**231** | 1081 (error listing) |
| `sbl -bf` | rc=0 `6f1671c07577` | rc=0 `6f1671c07577` | rc=0 `6f1671c07577` | **40971** |

**The Milestone-1 program has no stable oracle at all under the flag 12 of the 13 suites use.** beauty came back `FLAKY` in the sweep, and the FLAKY tag *was* the finding.

⛔ **AND THE SIGSEGV IS AN EFFECT OF FOLDING, NOT AN INDEPENDENT ORACLE BUG.** Under `-b` beauty dies in a storm of `ERROR 217 -- syntax error: duplicate label` at lines 559/561/563… on `visit_1`, `visitEnd` — camelCase labels that only collide **when folded** — and *then* cores. SPITBOL cores during **error recovery**, and folding is what manufactures the errors. Independent 2-line witness (`endlbl.sno`): a stray label produces `ERROR 215` + **rc=139** under `-b`, and a clean `rc=1` under `-bf`. **Three separate documents in this tree blame the environment for this:** CLAUDE.md/RULES.md ("plain `-b` SIGSEGVs after 34 lines"), `board_beauty_m1.sh:18`, and `cmp3_snobol4.sh:31` ("benign sandbox segfault-on-exit"). It is neither the sandbox nor a beauty bug — it is the flag.

## 4. THE 4-LINE WITNESS, AND TWO CHECKED-IN TESTS THE LIVE `-b` ORACLE GRADES WRONG

`Shift`/`shift` as two labels: `sbl -b` → `ERROR 217 duplicate label`; `sbl -bf` → clean; **SCRIP m3 and m4 → clean.** SCRIP agrees with `-bf` in both modes.

Two crosscheck tests where **both** arms answer and the answers differ — the pinned `.ref` agrees with `-bf` and SCRIP, and the live `-b` oracle contradicts both:
- `crosscheck/rung2/210_indirect_ref.sno` — `bal = 'the real bal'`; folded, `bal` becomes `BAL`, SPITBOL's **protected built-in BAL pattern**, so `-b` yields `ERROR 042 attempt to change value of protected variable`. `-bf` → `PASS 210_indirect_ref (2/2)`. SCRIP → `PASS`. Pin → `PASS`.
- `crosscheck/patterns/127_pat_json_keyvalue.sno` — lowercase `s` (subject) and uppercase `S` (a `.` target) are the SAME variable when folded, so the subject leaks: `-b` prints `s="age":42`, `-bf` prints `s=`. SCRIP prints `s=`. Pin says `s=`.
⭐ These pass today only because `grade()` accepts **either** pin or live. The pin is rescuing them from the oracle.

⭐ **CROSS-CHECK OF ANOTHER SEAT, CONFIRMED NOT CONTRADICTED:** seat5's s186 "BAL is ORACLE-INCOMPATIBLE (`ERROR 042`)" is the same protected-name mechanism, but `programs/gimpel/BAL.sno` names its function in **UPPERCASE** (`DEFINE('BAL(PARENS,QTS)…')`), so its clash is real under both arms. **Their call survives the flip.**

## 5. ⛔ THE HONEST COST — AND MOST OF IT IS A SCORING DEFECT, NOT A REGRESSION

`util_oracle_flag_sweep.sh transition` replays `grade()` over all 77 movers. Flipping the live arm `-b` → `-bf`:
**m3: 49 FAIL→FAIL · 15 PASS→PASS · 13 PASS→FAIL · ZERO FAIL→PASS.  m4: 31/20 NOBUILD/15/11 · ZERO FAIL→PASS.**
At face value the flip is a pure loss of 13 passes. It is not, and the 13 split cleanly:

- **8 are VACUOUS passes** (`preload1..4`, `longrec`, `setexit2`, `trim0`, `trim1`): SCRIP emits **0 bytes**, `-b` emits **0 bytes** with rc=0, so `grade()` calls it PASS — **while every one of them has a pinned `.ref` with real content** (3, 6, 6, 6, 2049, 29, 355, 101 bytes) that SCRIP does not produce. `preload1.sno`'s entire source is the single line `end`; its pin says `aa`. ⭐ **The scorecard is awarding PASS for MUTUAL SILENCE against a pin that says otherwise.** That is a grading defect independent of the flag, and the flip converts 8 false passes into honest fails.
- **5 are REAL passes** (`test_{stack,case,math,string}.sno` under `SCRIP/test/snobol4/library/`, `1113_table.sno`) — and their cause is §6, a curable SPITBOL bug, not a case collision.

## 6. ⭐⭐ A REAL SPITBOL BUG, THREE LINES TO REPRODUCE — `-f` SILENTLY DISABLES LOWERCASE `-include`

| control spelling | `sbl -b` | `sbl -bf` |
|---|---|---|
| `-include 'mylib.sno'` | from-library | **ERROR 022 undefined function called** |
| `-INCLUDE 'mylib.sno'` | from-library | from-library |
| `-Include 'mylib.sno'` | from-library | **ERROR 022** |

Under `-f`, **only the all-uppercase spelling is honored.** This contradicts the manual at **l.7311**: *"Controls may be specified in upper- or lower-case, **regardless of the current state of case-folding**."* And it fails **SILENTLY** — Catspaw SPITBOL "ignores unrecognized control statements" (same paragraph), so the include is dropped without a word and only surfaces later as a missing function. This is the entire cause of all 5 real regressions in §5.
**Census (lon excluded): 973 `-INCLUDE` vs 35 `-include`; exactly 18 files use ONLY the lowercase spelling** — 4 in `crosscheck/library/`, 4 in `SCRIP/test/snobol4/library/`, 9 in `programs/csnobol4-suite/`, 1 in `programs/gimpel/` (`INFINIP.sno`). ⭐ **Independently confirms seat5's s186 note that exactly one gimpel module uses that spelling.** Uppercasing the control word costs nothing under `-b` (973 files already do it) and is required for `-bf`; the four `csnobol4-suite/include*.sno` are tests *of the include mechanism* and may be deliberate — those want a ruling, not a sed.

## 7. TWO SCRIP DEFECTS FOUND ON THE WAY (both independent of the flag ruling)

- ⛔ **SCRIP DOES NOT REQUIRE AN END STATEMENT — A FALSE ACCEPT BOTH ARMS REJECT.** `noend.sno` = one line `OUTPUT = "no-end-at-all"` with no `END`: SCRIP m3 prints it and exits **0**; `sbl -b` **and** `sbl -bf` both give `rc=1 "No END statement found in source file(s)."` The two oracle arms **agree**, so this needs no flag ruling. The lexer is `strcmp(strbuf,"END")` (`snobol4.lex.c:1466`) — correctly case-sensitive — so SCRIP never mistakes lowercase `end` for END; it simply runs off the end of the program. Deserves its own queue row.
- ⛔ **`&CASE` REPORTS 1 WHILE SCRIP BEHAVES AS 0.** `probe/kw/kw_defaults.sno`: `-b` → `CASE=1`, `-bf` → `CASE=0`, **SCRIP → `CASE=1`** — while SCRIP demonstrably does *not* fold (`Shift`≠`shift`, `size`≠`SIZE`). Manual l.7891: `&CASE` "Initially 1, causing case-folding to occur." SCRIP declares a folding engine and implements a case-sensitive one. This is the **only** genuine head-to-head evidence for `-b` in the whole sweep (2 of 2 such rows are these `kw` probes), and it dissolves into a SCRIP bug rather than support for folding.

## 8. ⭐ THE THING THAT MUST BE RULED — THE LOWERCASE DIALECT (LON'S KNOB)

**53 of the 77 movers are `csnobol4_suite`.** These are not case collisions; they are a **wholesale lowercase dialect** — `output`, `size`, `&alphabet`, and the terminator spelled `end`. Under `-bf` the oracle refuses them outright ("No END statement found", rc=1, zero bytes: that is the +48 in the rc=1 row of §2). **SCRIP cannot pass them under either arm** — `alph.sno` gives `** Error 5 Undefined function or operation` because lowercase `size` is not `SIZE`, which is exactly what RULES.md requires of a case-sensitive engine. Under `-b` they are graded against an answer SCRIP is **structurally forbidden to produce**; under `-bf` they have no oracle. Either way they are unwinnable; the flag only changes the LABEL (FAIL/DIFF vs ORACLE_FAIL/UNSCR) — **and UNSCR moves META, which is Lon's knob (HQ-73).** The principled disposition is the one seat5 used for the 3 oracle-incompatible gimpel modules: mark them out-of-dialect and stop scoring them. **Not attempted; escalated.**

## 9. RECOMMENDATION

1. **Flip the live-oracle arm to `-bf`** and delete the `beauty_self` special case at `scorecard_snobol4.sh:80` — it is not a special case, it is the only suite currently graded correctly. Same flip for the `-b` scoring sites: `board_sno15_{perf,perf2,ident}.sh`, `board_sno_apps.sh`, `test_bench_snobol4_timed.sh`, `cmp3_snobol4.sh`, `test_demo_descent_sweep.sh`.
2. **Uppercase the 16 lowercase `-include` control words** in the 14 non-`include*.sno` files of §6 (24 such lines exist across all 18) — this cures all 5 real regressions and is a no-op under `-b`.
3. **Fix the vacuous-PASS rule**: mutual empty output must not be a PASS when a non-empty pin exists.
4. **Rule the csnobol4 lowercase dialect** (§8) — Lon's call, it moves META.
5. Correct CLAUDE.md/RULES.md/`board_beauty_m1.sh:18`/`cmp3_snobol4.sh:31`: `-bf` is not a SIGSEGV workaround; `-f` is the case-sensitivity switch and the SIGSEGVs are downstream of folding-induced errors.
6. `datatype-case` (queue rank 34) **cannot be adjudicated before this ruling**: 4-line witness `DATA('jobj(a,b)')` → `DATATYPE` answers `JOBJ` under `-b`, `jobj` under `-bf`, and SCRIP answers `JOBJ`. SCRIP's uppercase answer is a bug **iff** the reference is `-bf`. This row is that row's prerequisite. (Same mechanism produces the one `demos` mover, `json.sno`'s `root=JOBJ` vs `root=jobj`.)

## 11. ⭐⭐⭐ LON'S RULING, EXECUTED — "WE FIX ALL THE PROGRAMS BY UPPERCASING THE KEYWORDS"

**Ruling (Lon, in-chat, s188):** *"We fix all the programs by uppercasing the keywords."* — i.e. §8's lowercase dialect is NOT to be marked out-of-dialect and dropped; the programs are to be REPAIRED so they mean under `-bf` what they meant under `-b`. Executed this session.

**⛔ THE TRAP THAT BLANKET UPPERCASING WALKS INTO, AND IT IS NOT HYPOTHETICAL — THE CORPUS HOLDS BOTH DIALECTS.** A naive pass over all 2088 lon-excluded `.sno`/`.inc` files changes **197** of them, and among them it corrupts the very programs that already work: **`beauty.sno` uses `Integer` and `tab` as USER GRAMMAR NONTERMINALS**, and uppercasing them collides them with the built-in `INTEGER()` predicate and `TAB()` pattern — beauty runs clean under `-bf` (§3) *precisely because* `Integer` != `INTEGER`. Likewise `crosscheck/rung2/210_indirect_ref.sno` deliberately names a variable `bal`, which must NOT become the protected built-in `BAL`. **A corpus-wide sed would have broken the Milestone-1 program itself.**

**THE DIALECT GUARD — the pinned `.ref` is the arbiter of which dialect a program is written in**, because it records the intended answer:
- pin exists and `-bf` output == pin ⇒ **CASE-SENSITIVE dialect, never touched.**
- program runs clean under `-bf` ⇒ not broken, not touched.
- otherwise ⇒ folding dialect: uppercase keywords in the program **and its transitive `-INCLUDE` closure**, then ACCEPT only if `-bf` afterwards reproduces the pin (or, where the pin is independently broken, the pre-edit `-b` output). Anything else is **reverted automatically.**

**WHAT THE UPPERCASER TOUCHES:** built-in function names (ch.19 summary ∪ Function-Descriptions headwords), the special system names (l.8027: `ABORT CONTINUE END FRETURN INPUT NRETURN OUTPUT RETURN SCONTINUE TERMINAL`) and primitive pattern variables (`ARB BAL FAIL REM SUCCEED`), every `&keyword`, and the control word of a control statement. **NEVER touched:** string-literal contents, `*`-comment lines, `;*` comment tails, and every user-defined name.

**RESULT — 34 programs repaired across 35 files, each individually verified:**
- **15** verified byte-identical to their pinned `.ref`.
- **18** verified byte-identical to their pre-edit `-b` output, with a pin that **matches neither arm** — pre-existing pin breakage, left untouched and reported rather than papered over.
- **1** (`programs/gimpel/INFINIP.sno`, unpinned) verified against its `-b` baseline.
- **4 LEFT ALONE by the dialect guard** — `127_pat_json_keyvalue`, `210_indirect_ref`, `space2`, `noexec` — exactly the case-sensitive-dialect programs §4 identified by hand. The guard reproduced a human judgement mechanically.
- **39 NOT FIXED, named with reasons:** 13 still differ after uppercasing, 11 still `rc!=0`, 8 are already all-caps so the uppercaser changes nothing (their difference is `&CASE`, or a name minted from a STRING LITERAL by `DATA`/`DEFINE`, which folding uppercases and `-f` does not — the §9.6 `datatype-case` mechanism), 7 are ambiguous (no pin, both arms clean and disagreeing). **All reverted; none left half-edited.**

**⭐⭐ THE PAYOFF, MEASURED BY STASH A/B ON THE 33 PINNED EDITED PROGRAMS — SCRIP GOES 0/33 → 12/33, IN BOTH MODES.** Before the edit every one of them failed (`alph.sno`: `** Error 5 Undefined function or operation`, because lowercase `size` is not `SIZE`); after it, 12 match their pins exactly. **m3 and m4 agree to the program — 12/12 both — so the 1:1 law is preserved.** These were the rows §8 called unwinnable-by-construction; they are now ordinary passes, and the remaining 21 are honest reds against real references rather than rows SCRIP was forbidden to win.

**⛔ TWO METHOD NOTES, RECORDED BECAUSE BOTH COST ME A MEASUREMENT.** (1) An earlier acceptance gate targeted the pinned `.ref` unconditionally; it refused 52 of 77 because so many csnobol4 pins match neither arm, and a later one targeted the `-b` output unconditionally and **wrongly "fixed" `210_indirect_ref` — reproducing the `ERROR 042` its pin says is wrong.** Only the two-part guard above is correct: *which arm the pin agrees with* is the question, not *what the pin says*. (2) A `git stash` run to measure the "before" arm **while a sweep was still in flight** silently contaminated that sweep (1848 rows against an 1786-program tree). A tree must be frozen for the whole of a measurement, not merely at its start.

**⭐ THE SWEEP DELTA, RE-MEASURED ON THE REPAIRED TREE — MOVERS 77 → 42 OVER THE INTERSECTION, 36 CURED, AND ZERO GENUINE NEW ONES.** Compared BY NAME over the 1786 programs present in both sweeps (the tree moved under me mid-session — corpus `66259281` → `42530cb0` via another seat's push — so counts alone are not comparable and the set comparison is what carries the claim). ⛔ **The raw diff shows ONE apparent new mover, `programs/snobol4/smoke/empty_string.sno`, and it is a FALSE ALARM I chased down rather than shipped:** git shows the file untouched by this session, and four runs per arm give four different md5s under `-b` and three under `-bf` — it is nondeterministic under BOTH arms (the §3 error-recovery-core class). It read FLAKY before and MOVER after purely because the two same-flag control runs happened to agree that time. `programs/snobol4/smoke/multi.sno` appears as "cured" for the same reason and was likewise never edited. ⭐ **THE LIMITATION THAT MATTERS FOR ANY SEAT REUSING THIS TOOL: the control arm is a PROBABILISTIC filter, not a proof.** A nondeterministic program can still slip through as a MOVER when its two control runs coincide, so a mover set is an UPPER bound on real flag-dependence, exactly as seat7's s184 board note says a single-run two-arm sweep is a LOWER bound on a nondeterministic defect. Neither direction is safe without re-running the individual witness.

**GATE RECEIPT (corpus board, after the edits):** **m3 332/5 · m4 325/11 · SKIP 1 (337)** — the standing watermark to the digit, fail-set unchanged. A no-op by construction (the board enumerates `crosscheck` + `beauty_suite` + 4 demos and never reaches `programs/csnobol4-suite` or `programs/gimpel`), which is exactly what makes it the right proof that 35 corpus edits regressed nothing. SCRIP tree untouched: `git status` clean, so no `.s` regen debt.

**HYGIENE, NOTED NOT FIXED:** `programs/csnobol4-suite/popen.sno` / `popen2.sno` associate a file with a shell pipe (`OUTPUT(.o, 99,, "|cat >popen2.dat")`) and leave stray artifacts (`test.bin`, a file literally named `|cat >popen2.dat`) in the corpus when run. Removed by hand this session; the suite wants a scratch-dir convention.

## 12. REPRODUCTION
```bash
bash scripts/util_oracle_flag_sweep.sh sweep      /tmp/ofs 12   # 3-arm sweep -> arms.tsv
bash scripts/util_oracle_flag_sweep.sh transition /tmp/ofs      # movers -> scorecard verdict delta
```

## 13. ⛔ CORRECTIONS TO THIS FINDING (kept visible, not silently edited)

- **"13 of 14 suites" WAS WRONG — caught by seat2 at s189, and it originated in my own s186 note and was copied into the rank-0 queue brief from there.** At SCRIP `213771e2` the `SUITES` table has **13 rows**, not 14, and `beauty_self` alone ran `-bf`, so **12 suites ran `-b`** — of which one is the off-limits `lon` suite, leaving **11 non-lon suites that actually flip**. Corrected throughout this file, in the cursor, and in `util_oracle_flag_sweep.sh`'s header. The queue brief still carries the wrong figure and wants the same fix. **A number invented once and quoted onward is indistinguishable from a measured one** — this is the same class as the stale-build lesson seat5 recorded at s186.
- **THE SIGSEGV CLAIM IS SHARPENED BY seat2'S INDEPENDENT MEASUREMENT, NOT WEAKENED.** They showed a *genuine* duplicate label (`shift`/`shift`, both lower-case) **SIGSEGVs under `-bf` too**. So the crash lives in SPITBOL's **ERROR-217 REPORT path**, and folding's role is precisely to *manufacture the phantom errors that walk into it* — which is what §3's "cores in error recovery" says, now with the cleaner separation: the flag is not the crash, it is the supply of crashes. `CLAUDE.md`'s oracle line is a **fourth** document needing the correction listed in §9.5.
- **MY TRANSITION REPLAY IS A FLOOR, NOT THE BOARD.** `verdict()` compares outputs only; it does not reproduce `grade()`'s `TIMEOUT`/`SIG<n>`/`RC<n>` labels, so the §5 transition counts bound the real per-suite movement from below. seat2 is running the full board on both arms for the true META delta — that number, not mine, is the one to quote.
- **seat2 ADDS THREE CONSTRUCTS I DID NOT MEASURE**, so the case for `-bf` does not rest on labels: lower-case `output` (`-b` prints both lines; `-bf` and SCRIP print one); and indirect reference in **both** directions — with only lower-case `abc` assigned, `$('ABC')` resolves under `-b` and is null under `-bf` **and under SCRIP**, and symmetrically with only `ABC` assigned. Manual p.192: special names take any case ONLY under folding; p.182: folding treats the `$` string as upper-case when making the name.
