# FINDING — s188 (seat1, Opus 5; queue lane: successor to `lon-include-root`, the `-b`/`-bf` row)

## THE ORACLE FLAG IS A LANGUAGE-SEMANTICS SWITCH, `-b` MANUFACTURES THE CRASHES IT IS BLAMED FOR, AND THE M1 PROGRAM'S ORACLE IS NONDETERMINISTIC UNDER THE FLAG 13 OF 14 SUITES USE

**Watermark:** SCRIP `213771e2`, corpus `66259281`, both trees clean, RT_OPT `-O0`. **No compiler source touched, no corpus program touched.** One new script (`scripts/util_oracle_flag_sweep.sh`) and this FINDING. RULES step-4 `.s` regen NOT APPLICABLE.
**⛔ `corpus/programs/lon/` was never enumerated, run, or compiled.** The sweep tool carries two independent locks (suite not listed + per-path guard). This is why the row was measurable at all: `scorecard_snobol4.sh` runs the `lon` suite and is therefore currently unrunnable, so the whole measurement was rebuilt on a lon-safe harness.

## 1. WHAT THE FLAG ACTUALLY IS — FROM THE MANUAL, NOT FROM TASTE

`scorecard_snobol4.sh:80` runs the live oracle as `sbl -b` for **13 of 14 suites** and `sbl -bf` for `beauty_self` alone. CLAUDE.md documents `-bf` purely as a SIGSEGV workaround. That is wrong, and the manual is unambiguous (line numbers are `pdftotext -layout` of `1-spitbol-manual-v3.7.pdf`):

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

**The Milestone-1 program has no stable oracle at all under the flag 13/14 suites use.** beauty came back `FLAKY` in the sweep, and the FLAKY tag *was* the finding.

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

## 10. REPRODUCTION
```bash
bash scripts/util_oracle_flag_sweep.sh sweep      /tmp/ofs 12   # 3-arm sweep -> arms.tsv
bash scripts/util_oracle_flag_sweep.sh transition /tmp/ofs      # movers -> scorecard verdict delta
```
