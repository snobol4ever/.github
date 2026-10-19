# GOAL-HQ-DOTNET — finish and polish snobol4ever/snobol4dotnet

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-DOTNET, identity `hq_dotnet`, root `/home/claude_dotnet`, officer the cfo.
- **Repo:** `snobol4ever/snobol4dotnet`, a SNOBOL4 + SPITBOL-extensions compiler in C#/.NET.
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-DOTNET-CLAUDE.md`).

## LIVE CURSOR

- **2026-10-19 night — snobol4dotnet `9c77d9d`. Board at `d31a322`: aisnobol 8/8, Gimpel 132/145, Budne 70/86, snoflake 126/128, X64T 25/33, dotnet 6/11, testpgms 5/8, no regressions.** Batched TestSnobol4: 2,648 / 2,586 / 60 failed / 2 skipped (the same 60). Since `8da7544`, each a defect with a test red before and green after, checked against sbl; tests that asserted non-SPITBOL answers were corrected only after sbl answered their exact programs (TEST_Corpus_1116, 1017, Arg_001, Local_001, four Ident/Differ pattern tests, Detach_001/002, three SaveDll scripts with an indented END):
  - traces and values: `f79ed5e` trace lines print through prtvl (CONS #1, TABLE(11) #3, *X) and under an OPSYN'd function's own name (SIR's &FTRACE byte-identical); `630dd16` a pattern keeps its identity through copies; `d7c35aa` ARG/LOCAL return NAMEs; `b012d98` a variable holding an expression is itself the target; `3a870f1` a line read becomes the input variable's value;
  - DATA: `c47a991` OPSYN'd constructors and fields; `8d0aead` wrong-type field argument is error 41;
  - compilation: `3c41c07` compile errors suppress execution (-NOERRORS default; -k and -ERRORS run), every error reported, reaching one is error 7; `d31a322` misplaced continuation is 214; `f7647dc` D exponents; `85547b4` listing controls silent; `9c77d9d` :(END) runs the END statement.
  - testpgms: test6 now differs only in &TRIM; test1 only by VALUE and &TRIM; test2 only by SPITBOL's error report on stdout. All three wait on Lon.
  - **For Lon:** (1) VALUE and CONCAT are not SPITBOL functions (sbl: error 22) -- remove them, as mimic-SPITBOL-exactly implies, or keep them as extensions? (2) &TRIM's initial value (sbl x64 reports 1, the manual 0); (3) SPITBOL's error report and compile errors on stdout; (4) HOST() identification string; (5) 8-bit OUTPUT; (6) class B tests.
- **2026-10-19 early — snobol4dotnet `8da7544`. Board at `2bca72e`: aisnobol 8/8 (was 3/8 at `0907656`), testpgms 5/8 (was 2), Gimpel 131/145 (was 128), snoflake 126/128, X64T 25/33, dotnet 6/11, Budne 69/86; its one regression (spit) fixed in `8da7544`, so Budne should read 70 again.** Batched TestSnobol4: 2,634 / 2,572 / 60 failed / 2 skipped (the same 60). Since `fdf3c64`, each a defect with a test red before and green after, checked against sbl:
  - input and calls: `6a0bffe` ? and ~ read an input-associated operand (?INPUT counts lines; HSORT); `63280e2` parameters, locals and the function variable keep their I/O associations, ENDFILE/reopen drop stale readers, REWIND reaches an unread channel; `4389f91` unary operators OPSYN'd to DEFINEd functions (program, CODE, EVAL); `a12bca6` no operator runs once an operand failed (FRETURN's null is still marked succeeded);
  - values: `7fefeb1` IDENT/DIFFER compare names by what they name (IDENT(.X) fails; each .&KEYWORD new); `8d5b465` CONVERT NUMERIC; `8da7544` type names fold only while &CASE folds; `01362b4` STOPTR returns null;
  - compilation: `5a8aace` CODE and CONVERT to CODE/EXPRESSION fail quietly with &ERRTYPE/&ERRTEXT, a failed block numbers only statements before the error; `2bca72e` blank statements between semicolons take numbers (CODE keeps trailing blanks, a source line trims them, nothing after a final semicolon).
  - **Seen, not fixed:** traces print `<CONS:CONS>` where sbl prints prtvl's `CONS #n` (also ARRAY(3) #n, TABLE(11) #n, *X); an OPSYN'd function traces under the called name where sbl uses the original. Next: those two, then testpgms' 3, dotnet's 5, X64T.
  - **For Lon (unchanged):** HOST() identification string; error report on stdout; &TRIM's initial value; 8-bit OUTPUT; class B tests.
- **2026-10-18 night (later) — snobol4dotnet `c9a6d20`. At `598d467`: snoflake 126/128, Gimpel 128/145 (was 96 at `ad23567`), X64T 16/33, Budne 69/86, dotnet 4/11, testpgms 2/8; sno-rungs 1,923/2,035 at `4ef8daf` (none newly failing). Regrade at `c9a6d20` running.** Batched TestSnobol4: 2,619 / 2,557 / 60 failed / 2 skipped. Since `4ef8daf`, each a defect with a red-then-green test checked against sbl -b:
  - patterns and control: `0c62a52` left recursion is fatal 246; `775f513` ~ negates only its operand's failure (FailureOrigin); `598d467` :(END) inside a function ends the program; `aac05ec` SETEXIT :(CONTINUE) resumes at the failure exit;
  - numbers: `3c62699` SSE flush-to-zero/denormals-are-zero on real arithmetic and math functions; `61a1f14` ** per o_exp (exp(y ln x), integer overflow 17); `4354a4e` integer-vs-real comparisons used the wrong operand; `c9a6d20` PROTOTYPE of a vector is an integer;
  - I/O and run: `5577dd7` -f1/-f2 and raw mode in file specs (code.sno regression from `873c0be` fixed); `469fe22` words after the END file are program arguments, HOST(0..4) per sbl (argv row closed); `12e11fb` the &DUMP end-of-run dump goes to the -o listing; `dd1a9b9` EVAL compile errors fail quietly with &ERRTYPE; `19da5ce` replacements fire VALUE traces.
  - **For Lon:** HOST()'s identification string — copy SPITBOL's ("x86-64:unix :Macro SPITBOL 15.01 #") or keep snobol4dotnet's own? Plus the earlier three (error report on stdout, &TRIM initial value, 8-bit OUTPUT).
  - **Seen, not fixed:** sbl folds constant expressions at compile time (0 ** 0, 10 ** 30 as constants are compile errors); *S in DUMP prints EXPRESSION; include-file error locations show negative counts; concatenating a NAME makes a pattern here (error 8/9 in sbl); X64T gcbuster (memory statistics).
- **2026-10-18 late night — snobol4dotnet `4ef8daf`. snoflake@dotnet 125 / 128 (was 107 at `c59036f`); sno-rungs@dotnet 1,912 / 2,035 at `018904e` (was 1,883), its one regression fixed in `a643cf2`.** Batched TestSnobol4: 2,606 / 2,544 / 60 failed / 2 skipped (TEST_Csnobol4_ord fixed on the way). Each a defect, a test red before and green after, checked against sbl -b:
  - output and I/O: `8e8fdd8` OUTPUT = INPUT at end of input writes nothing; `2c7d1d9` -o=file takes the listing (harness `0a75286` now passes the sink; control-hide pair PASS); `060f049` &OUTPUT integer; `fbb0f04` &MAXLNGTH 16m; `6104a33` .INPUT reads no line;
  - names and calls: `9f0a165` element NAMEs through their collection; `c8514f4` an element read names the element; `018904e` + `a643cf2` NRETURN gives the named value, RETURN keeps a NAME; `1cb211f` + `4ef8daf` a function's own variable is saved/restored (protected stays protected); `bec87d9` a skipped call pops its arguments; `228c11e` values copied from FAIL/&TRIM are not protected;
  - functions: `5a8b2db` OPSYN per s_ops (16 old expectations corrected against sbl); `ba1dc16` ORD; `7c81e8d` COPY one level deep; `6e1b386` UNLOAD of a name; `cea02c8` @C fires VALUE traces; `2ccb0fb` empty-name access check;
  - CODE: `c5cf173` :<CODE(...)> transfers; `503a180` CODE statements numbered on from the program, each block +1 for its implicit end, EVAL none;
  - DUMP: `8b58070` SPITBOL's dump exactly (lexical order, keywords, blocks by idval, names by hashs order, table buckets).
  - **Snoflake left:** dump-ordered, dump-variables (&TRIM initial value, Lon's question); kalah-opening-search (search differs, not yet traced); recursive-expression-recognizer and recursive-yz-pattern (sbl stack overflow 246); 44 match only up to sbl's error report on stdout (Lon's question).
  - **Seen, not fixed:** *S prints EXPRESSION in DUMP; dotnet's include-file error location shows negative code/list counts; concatenating a NAME is error 8/9 in sbl but makes a pattern here; ACCESS traces fire for assignment targets.
- **2026-10-18 night — reseated as Opus 5.5 medium (Lon, in-chat; ceo told). Fixing the 11 dotnet suites' failures at snobol4dotnet `c59036f`.** Gimpel@dotnet graded for the first time: 96 / 145 at `ad23567`. Batched TestSnobol4: 2,583 / 2,520 / 61 failed / 2 skipped, the same 61 throughout. One defect per commit, each with a test that failed before and passes after, checked against sbl -b:
  - reals: `07e3bc1` SPITBOL's gtstg digits; `22e4fa8` gtnum reading (3,006 literals byte-identical; x64 math_sqrt now SAME);
  - `90cf8a5` SETEXIT traps an error inside EVAL (row closed); `ad23567` a ( after [ < , groups (hoare-quicksort, leadering-replacement SAME);
  - `c4f1fc1` TRACE's fourth argument calls a trace function (trxeq), &FNCLEVEL before RETURN; `881d7a3` unary + keeps a real's sign; `b246851` CLEAR keeps I/O associations; `dd24863` $ through a keyword's NAME; `c766364` @ to deferred and element targets;
  - `873c0be` INPUT/OUTPUT file specs per osint lenfnm/sioarg (options, append, replace, errors 116/160); `b3b618d` DATA refuses only system functions (CONCAT, VALUE are not SPITBOL's, now unprotected); `3bea733` DEFINE defers its entry label (286 at the call); `c59036f` runtime errors name their own line.
  - **Snoflake left after these:** output-format-ignored and twelve-days stop at sbl's error 160 but sbl also writes its error report to stdout (Lon's question); recursive-yz-pattern (stack overflow 246); the rest of the 45 unmeasured since.
  - **Seen, not yet fixed:** ACCESS trace fires for an assignment's target and prints NAME, not NAME = value (only ALL.sno uses it); the lexer refuses a D exponent in a real literal (error 231); concatenating a keyword's NAME is error 9 in sbl; a field function falls back to the builtin for a non-DATA argument (class B).
  - **Lapse:** one Gimpel run refused as stale because I edited Lexer.cs while it ran; the rerun at `ad23567` graded.
- **2026-10-18 late evening — `sno-rungs@dotnet` 1,863 / 2,035 (92%) at snobol4dotnet `85dd4c4`, up from 1,734 / 1,996 (87%) at `9548cd9`.** 22 partition parts, 0 hangs; published by from-progress with the denominator stamped (the corpus grew to 2,035, chunk:21 new). TRACE now prints SPITBOL's lines on stdout (`94af378`, `85dd4c4`; four trace rows closed). Batched TestSnobol4: 2,559 / 2,496 / 61 failed.
  - **Measured and ready to land next** (all checked against sbl, nothing edited yet): one real formatter (15 digits, fixed for 0.1 <= x < 1e15, else 0.ddde+-N; the model matches sbl on 19 edge values; draft in the scratchpad), closing both real-format rows; integer ^ negative integer is a real and a zero base gives 0.; &ERRTEXT is the message only (keep the full diagnostic in its own field); -INCLUDE trims a trailing (not a leading) blank; -LINE n ["file"] renumbers the following lines.
  - **For Lon (row QAs):** class B CSNOBOL4-only expectations (26 tests); SPITBOL's error report on stdout; &TRIM's initial value; 8-bit OUTPUT versus the README's Unicode support.
- **2026-10-18 evening — NINE MORE CURES, batched 66 → 61 failed (2,549 tests, 2,486 passed).** Each red then green against `sbl -b`, each row closed by its computed DONE-WHEN.
  - `25466ee`: `-n` and `-NOEXECUTE` compile without running (nothing read `SuppressExecution` before); noexec.
  - `86ed09f`: type names are SPITBOL's, upper case; a DATA type keeps its name as DATA folded it (NODE under `-b`, node/Pair under `-bf`). 63 tests asserting lower case corrected, each checked to differ only in case; fun1, lexcmp. `8356448` removed three BOMs this sitting's edits had added.
  - `0dec9f7`: `&STNO`, `&LINE`, `&LASTNO`, `&LASTLINE`, `&FILE`, `&LASTFILE` read SPITBOL's numbers (blank lines are null statements; `&LASTNO` is taken at statement start and the caller's statement comes back after a call); contin.
  - `c23d5de`: `-r` gives INPUT the lines after END, then fails.
  - atn, three defects behind one row: `432d192` (a DATA object kept no identity through copies; IDENT now follows its shared field store), `b7cffc6` (a parameter first named in CODE text got a second variable slot and read null), `3f71d9d` (X = V wrote into the element X had once been read from; an element is the target only when indexed in the same statement). atn's 664 lines now equal sbl's.
  - **Seen, not yet rowed:** `OUTPUT = TABLE()` raises error 42 (sbl prints TABLE); `&TRIM = -1.5` should be error 210; `DUPL('x', -1.5)` should fail; a `?` match expression's value is the matched substring under sbl; `-HIDE` and other unknown controls print "invalid control statement" where SPITBOL ignores them silently.
  - **Next:** the probe rows (8-bit OUTPUT, TRACE to stdout, &ERRTEXT, real formats, compile-time refusals, include name blanks, -LINE, -CASE scope), then a fresh `sno-rungs@dotnet` board, since alternation, assignment and DATA identity changed underneath it.
- **2026-10-18 late afternoon — SEVEN CURES ON THE BUDNE REDS, batched 71 → 66 failed (2,538 tests, 2,470 passed).** Each red then green against `sbl -b`, one per commit, each row closed by its computed DONE-WHEN. Lon re-seated this seat as Opus 5.5 high mid-sitting; the ceo was told.
  - `0200e0d`: an alternative restarts where its alternation began. Every later node of a left arm re-saved the arm's alternative at its own cursor (SPAN, LEN, ARBNO arms; nqueens). Numbers001 had asserted the defect.
  - `d31f3f0`: `&TRIM` trims INPUT (blanks and tabs only); trim1.
  - `671ef04`: a return restores the caller's variables under their own names, even with an array passed on; sudoku.
  - `305d487`: a real or numeric string converts to an integer where one is needed (keywords, CHAR, CONVERT, subscripts, ARRAY); intval. TEST_Abend corrected to a value sbl rejects.
  - `957e934`: CONVERT takes a NAME type, a string of blanks reads 0; space. space2 went red: its `-PLUSOPS 0` expectation is CSNOBOL4-only, added to the class B question.
  - `2231417`: `*X . V` defers X to match time, as `$` did; uneval2.
  - `3b79d58`: a function called mid-match keeps the caller's pending `.` assignments.
  - **Asked of Lon (triage baton QA):** class B (now 26 tests); SPITBOL's error report on stdout; `&TRIM`'s initial value (manual 0, x64 source 1).
  - **Harness:** my six runners now self-publish their `@dotnet` rows (hq_jvm landed the lines, harness `9217c66`, after this seat's edit was refused by its permission guard).
  - **Next:** noexec, then DATATYPE (fun1, lexcmp; also fixes several CorpusRef expectations in lower case), `&STNO`, dash-r, atn, then the probe rows.
- **2026-10-18 afternoon — THE 71 BUDNE UNIT-TEST REDS, TRIAGED AGAINST SPITBOL** (row `dotnet-testsnobol4-reads-every-unit-test-passed-twelve-fail-at-80c828a-ceo-1817`). At snobol4dotnet `9548cd9`, `scripts/test_in_batches.sh` reads `TOTAL tests=2518 passed=2445 failed=71 skipped=2 not_run=0`. Every red is in `CorpusRef_Csnobol4Suite`.
  - **The oracle switch is `sbl -b` (SPITBOL's default `-F`, folding).** The inline programs are Budne's lower-case originals. SNOBOL4.NET folds by default as SPITBOL does. The corpus copies were upper-cased for the fleet's `-bf`, so they no longer equal the inline programs.
  - **The fork is a faithful oracle here.** Upstream x64 (`spitbol-bench-oracle/sbl`) folds nothing even under its own `-F`, against the manual (*"lower-case letters are converted to upper-case before defining the label"*). It also refuses a lower-case `end`, and the fork follows the manual on both. On the upper-cased corpus copies, upstream and the fork agree on 66 of the 71. The five that differ are `&CASE`'s reported value (a, dump, diag1), `-CASE` (case1) and ORD (ord): ORD is a fleet addition, and upstream answers it with error 22, as dotnet does.
  - **How the corpus refs were cut:** `sbl -bf prog 2>&1`. SPITBOL writes an error report and its statistics block to both stdout and stderr, so a ref of an erring program holds them twice, with time and memory figures. That is why label, words and digits matched neither engine. The triage compares the output before the error report, plus the error number.
  - **Triage (inline program; dn = `dotnet Snobol4.dll -b`; want = the test's inline expectation):**

    | class | tests | what |
    |---|---|---|
    | A. dotnet ≠ SPITBOL, want = SPITBOL | atn, contin, fun1, intval, lexcmp, noexec, nqueens, space, sudoku, trim1, uneval2 | engine defects; each test is its own DONE-WHEN |
    | A'. dotnet ≠ SPITBOL, want = CSNOBOL4 | 8bit, alph, a, dump, diag1, diag2, case1, err, float, float2, ftrace, trace1, trace2, trfunc, spit, hide, include, line, keytrace, setexit, setexit4, setexit5, setexit6, scanerr, loaderr, update, t, random, pow | engine defects; DONE-WHEN a probe against `sbl -b` |
    | B. dotnet = SPITBOL, want = CSNOBOL4 only | 8bit2, alis, digits, file, function, json1, label, labelcode, maxint, openi, openo2, popen, popen2, rewind1, setexit2, setexit7, tab, vdiffer, ord, preload1-4 | the expectation is not SPITBOL's answer; question for Lon in the row's QA |
    | B'. data after END | len, repl, words, words1 | want = `sbl -b -r`; CSNOBOL4 reads after END by default, SPITBOL needs `-r`, and dotnet's `-r` feeds nothing (row `dotnet-dash-r-...`) |
    | C. in-process only | base, include2, include3, include4 | CLI dotnet = sbl = want from the suite folder; in-process, `-INCLUDE` resolves against `TestSnobol4/bin/...` and finds no file |

  - **Defect causes (A and A'), each its own row:**
    - an ARBNO in one alternative continues into a later alternative's successor: `'aab' (ARBNO('a') 'c' | ARBNO('x') 'b')` matches (nqueens). It predates `c91c416`, measured on its parent;
    - `&TRIM` is not applied to INPUT (trim1; sudoku's blank-line test);
    - a name keeps its source case: `OUTPUT = .one` prints `one` where SPITBOL prints `ONE`, and `TRACE('foo')` traces nothing (case1, trace1);
    - DATATYPE in lower case (fun1, lexcmp; existing row);
    - `&STNO` one low (contin, hide; existing row);
    - a real where an integer is required raises error 208 (intval: `&TRIM = 1.0`, `CHAR(65.0)`, `DUPL('*', 5.9999)`);
    - `CONVERT(' ', .INTEGER)` throws an InvalidCastException (space);
    - `*BREAK(QUOTE)`, with QUOTE set by `$` earlier in the same match, raises error 69 (uneval2);
    - `-NOEXECUTE`, `-CASE` and `-LINE` are not recognised (noexec, case1, line);
    - `&ERRTEXT` holds the whole diagnostic, with file, line and source, instead of the message (err);
    - integer `^` a negative integer answers 1 instead of a real (pow);
    - reals: `0.001` where SPITBOL prints `0.1e-2` (float); `0.30000000000000004` (float2; existing 17-digit row);
    - OUTPUT writes characters 128 to 255 as two UTF-8 bytes where SPITBOL writes one byte (8bit, alph). The inline expectations also lost those bytes to U+FFFD in the C# file;
    - TRACE output goes to stderr with other statement numbers (ftrace, trfunc, spit, trace2);
    - `&DUMP = 1` omits SPITBOL's keyword dump (a, dump, diag1);
    - SPITBOL refuses at compile time what dotnet runs: a constant `1 / 0` is error 14 (keytrace, setexit, setexit5, setexit6), `"FOO" @1` is error 212 (scanerr), diag2 line 242 is error 214;
    - a missing `-INCLUDE` file is reported and the program still runs (random). SPITBOL stops with error 285;
    - `-INCLUDE "line2.sno "`: SPITBOL drops the trailing blank in the name (include, line);
    - error numbers: LOAD 142 vs 22 (loaderr), TRACE of a function not yet defined 198 vs none (t), TRACE's fourth argument given as a name 197 (setexit4), `"B,U"` I/O options 289 vs 160 (update), `HOST(HOST_REAL_BITS)` 254 vs none (float2);
    - atn loops (existing row).
  - **Not counted as a mismatch:** SPITBOL also writes its error report and statistics to stdout, and dotnet writes them only to stderr. That is a policy question, held for later.
- **2026-10-18 — LON'S RULING: snobol4dotnet mimics SPITBOL exactly.** Lon, in-chat to hq_dotnet, verbatim: *"The snobol4dotnet is meant to mimic SPITBOL exactly. So make decisions based on that. This however is not true of snobol4jvm."* Every semantic choice for this engine is SPITBOL's: the manual, and Dewar and Emmer's own source where the manual is silent. The fleet's oracle builds carry fleet patches, and where a patch departs from SPITBOL, SPITBOL wins. snobol4jvm is no SPITBOL mimic, so a shared-harness rule for "a port" never assumes SPITBOL for it.
  - **TIME() stays milliseconds**, as SPITBOL answers it. The manual says *"Returns the execution time in milliseconds"*, and upstream's `zystm` (x64 `9e3f042`) says *"in milliseonds"*. The fleet's `sbl` answers nanoseconds only by NS-TIME (x64 `ec80390`, Lon s249). The instrument learns the unit instead (harness `4043267`):
    - `bench_wrap_snobol4.py --time-unit-ns`;
    - `one_runner_port_time_unit_ns` answers 1000000 for dotnet, and nothing for jvm.
    - SnoBench's time angle runs again: `snobol4-bench-ref@dotnet` 23 / 23 on all three angles, re-published.
  - **csnobol4's preload pair runs as the oracle ran it**, without CSNOBOL4's `-L`: SPITBOL has no such switch, and the refs are `sbl`'s answer to the bare program (harness `e29b7ef`). `csnobol4@dotnet` 44 → 46 / 86, re-published.
  - **Audited, already SPITBOL-faithful:**
    - csnobol4's EXTENSIONS.tsv lists no entries;
    - gimpel's eight drivers headed "this .ref comes from CSNOBOL4": `sbl` prints six of those refs exactly and answers the other two, and the scorecard passes a match to live `sbl`;
    - snoflake and dotnet grade against live `sbl`;
    - the rungs, AIS, demos and bench refs are cut from `sbl -bf`.
- **2026-10-18 midday — ONE HARNESS GRADES SCRIP AND snobol4dotnet: all six of hq_dotnet's SNOBOL4 runners take `S4E_ENGINE=dotnet`.** Lon: *"Get a unified test harness that can run SCRIP and snobol4dotnet test suites regarding SNOBOL4."*
  - **The shape (the split with hq_jvm, on hq_jvm's helper `fd481a4`):** under a port engine, a runner uses the port's face as its SCRIP and `one_runner_port_ready` as its one check. It passes each program's declared heap and stack as `-dNk -sNk` and grades m3 alone, with no m4 row. Its rows are keyed `SUITE@dotnet`, and it writes no SCRIP score row: the row is `from-progress --suite SUITE@dotnet`. Under scrip, every command line reads as before.
  - **Runners on origin (harness):** dotnet `edf5eb3`, snoflake `21ef10a`, csnobol4 `e678f95`, gimpel `457adb3` (through `scorecard_snobol4.sh` `55ec60f`), demos `60b6796`, SnoBench `a423bab` (with `/usr/bin/time` as the process angle's stopwatch).
  - **Published `@dotnet` rows, all at snobol4dotnet `9548cd9`:** `dotnet@dotnet` 5 / 11 · `snoflake@dotnet` 82 / 128 · `csnobol4@dotnet` 44 / 86 · `gimpel@dotnet` 77 / 145 · `snobol4-demos@dotnet` 6 / 24 · `snobol4-bench-ref@dotnet` 23 / 23 (process and iteration angles), beside yesterday's `sno-rungs@dotnet` 1,734 / 1,996 and `aisnobol@dotnet` 2 / 8. Every row was graded by a live board and set by `from-progress`; none was typed.
  - **Shared harness defects found on the way, each cured and proven:**
    - `08d0827`: the face was tracked 100644, so every runner call read rc 126.
    - `3ca8e7b`: a bash runner's rows pinned SCRIP as their tree ("unknown" in a port root); they now pin the port's checkout.
    - `bc2d810`: a timed-out face run was stamped m4.
    - `65081f0`: the compile_args ratchet went red on the face's `--stlimit` case arm (exempted: the face only drops it).
    - `a881390`: `gate_tree_watch` read SCRIP's HEAD; under a port it watches the port's checkout.
    - `395f4cc`: `from-progress` assembles a port's bench and demo rows from their runners' census; those trees carry no ALL.csv.
  - **Root resolution:** every runner computed ROOT as SCRIP/.., which is empty in a port root, and then recorded no row, silently. ROOT is now the root beside harness.
  - **SnoBench under a port grades the process and fixed-iteration angles; the time angle is skipped.** The wrapper's budget reads TIME() as nanoseconds. Both SPITBOLs on this box are patched to answer nanoseconds (fork: 90,812,757 for 0.09 s), while snobol4dotnet answers milliseconds, as the SPITBOL manual has it (1,879 for 1.9 s). **Ruled by Lon the same day:** milliseconds, as SPITBOL answers it (the entry above).
  - **Rows minted:**
    - INPUT of a missing file succeeds and creates it;
    - a relative file name resolves against the program's folder, not the cwd. This defect wrote words.txt and a file named `[-f2 -r1]` into the corpus checkout during the boards; both were removed;
    - an options-only OUTPUT file argument creates a file named by the brackets, and later output is lost.
    - Each DONE-WHEN reads red on dotnet and green with sbl in its place.
  - **Biggest lever on the demos:** 16 of SnoDemo's 18 reds are the open row `dotnet-the-name-of-input-is-rejected-and-a-bracketed-input-with-no-file-reads-nothing` (`INPUT(.INPUT, 9, '[-f0 -r1000000]')` reads error 212).
  - **Next:** cure the reds in rank order, red-then-green on sbl; each cure is re-graded by its runner and re-published by from-progress.
- **2026-10-18 — WHERE THIS SITTING STOPPED (for the next one).** Lon: *"Get ALL the test suites graded, not just SnoRungs."* · *"Get all SNOBOL4 package runners working with snobol4dotnet."*
  - **Published `@dotnet` rows:** `sno-rungs@dotnet` 1,734 / 1,996 (87%) and `aisnobol@dotnet` 2 / 8, both at snobol4dotnet `9548cd9`. AIS was graded from its container, which is canonical because its own runner calls the harness on it.
  - **Budne and Gimpel cannot go through their containers.** The harness refuses both on corpus drift: `csnobol4_suite`'s ALL.mask names `diag1`, which ALL.sno no longer holds, and `gimpel`'s PARTITION.tsv is stale (`dextern_driver`). Reported to the ceo; this seat edits no corpus. Their boards are their bespoke runners.
  - **The package runners: hq_jvm and this seat split them, on the same word from Lon to both.** Topic `jvm-package-runners-take-the-port-engine`; my proposal is sent, and hq_jvm's answer is still pending.
    - hq_jvm lands the one shared helper (`lib_one_runner.sh` one_runner_port_scrip and one_runner_port_check, with `run_port_as_scrip.sh`) and the aisnobol, testpgms, x64 and x32 runners.
    - hq_dotnet takes dotnet, snoflake, csnobol4 and gimpel, plus `test_demos_suite.sh snobol4` (SnoDemo) and `test_snobol4_bench_suite.sh` (SnoBench), **only after the helper is on origin**.
    - Each runner under a port engine grades m3 alone, keys its rows `SUITE@ENGINE`, writes no SCRIP score row, and publishes with `from-progress --suite SUITE@ENGINE`. The scrip path stays byte-identical.
  - **Claimed, not started:** `dotnet-arguments-after-the-source-file-are-compiled-as-source-and-host-2-n-reads-nothing`. SPITBOL's measured rule and the cure are in its baton's `## NEXT`.
  - **Asked of the ceo:** wire `test_gate_one_runner_admits_a_port_engine_by_lang_at_engine_and_keys_its_rows.sh` (30 arms) into SCRIP's `make test`. The cfo found it unwired, and `util_gate_wiring.py` cannot run in a port root.
  - **Board discipline:** while a board runs, snobol4dotnet stays untouched (no edit, build or commit). SnoRungs runs one partition part per harness run; each package program runs as its own process; TestSnobol4 runs in batches of 100 (`scripts/test_in_batches.sh`).
- **2026-10-18 — THE FIRST PORT ROW: `sno-rungs@dotnet` 1,734 / 1,996 (87%) at snobol4dotnet `9548cd9`, Wall 392 s, in SUITES.tsv.** This seat's banner shows it. The board ran on Lon's batch rule: 21 partition parts, all recorded, 0 hangs. It was published by `from-progress`, which opened and set the row.
  - **Cured to reach it:**
    - `c91c416`: ARBNO repetitions are grafted into the outer match.
    - `936401a`: `-INCLUDE` searches `SNOLIB`.
    - `9548cd9`: `NULL` is no longer predefined as a pattern. That fixed `IDENT(S,NULL)`; FORTPUT's loop had flooded the board.
    - harness `e37e30c`: `-d` becomes .NET's GC hard cap. porter's runaway had hit the board's 8 GB cgroup kill.
    - harness `8d0d801`: `SNO_LIB` reaches the engine as `SNOLIB`.
  - **Rowed, open, for the 262 failing:**
    - `$` in a later alternative is lost (porter);
    - `.INPUT`, and bracketed INPUT with no file;
    - TRACE VALUE;
    - reals print 15 vs 17 digits;
    - SETEXIT;
    - `&STNO`/`&LINE`;
    - DEFINE error 86;
    - DATATYPE in lower case;
    - atn loops after line 438;
    - `-r`;
    - program argv;
    - a `../` path;
    - allocation speed;
    - the intermittent test host.
  - **Reported to the ceo:** the harness captures a program's stdout without a bound, so a runaway printer takes the board's scope into its cgroup kill.
  - **Next:** the rows in rank order (`$` and `.INPUT` first), each red-then-green on sbl and re-graded by its chunk; then the package suites as `@dotnet` boards.
- **2026-10-18 night — the first live board (`sno-rungs@dotnet`) is running, one 100-entry chunk per run, on snobol4dotnet `936401a`.**
  - **Scratch diagnostic of all 1,996 rungs** (10 s bound, no retry, scratch table): 1,613 of 1,896 graded passed. Chunk 10 was refused by a build I ran mid-pass.
  - **Cured since, each red-then-green against sbl, the batched suite unchanged at 71:**
    - `c91c416`: ARBNO's repetitions are grafted into the outer match, so backtracking reaches the argument's alternatives. Chunk 03 went from 47 to 34 failing.
    - `936401a`: `-INCLUDE` searches `SNOLIB`, as the SPITBOL manual documents.
    - harness `8d0d801`: the runner maps the harness's `SNO_LIB` onto `SNOLIB`.
  - **Harness, for the board itself:**
    - `69466b8`: fingerprints read the runner's `--paths`, so a source edited mid-board is not a moved binary.
    - `711c0f8` with `.github` `70b71b92`: the first publish opens the port's `SUITES.tsv` row through the table's writer.
  - **Board discipline, measured three times tonight:** while a board runs, snobol4dotnet stays untouched. An edit makes the tree `-dirty`, a commit moves its HEAD, and a build moves its DLLs; each refuses the append, correctly. The harness lists only 40 failures per run unless `SUITE_LIST_ALL=1`.
  - **Classes named by the diagnostic, rowed:**
    - TRACE VALUE prints twice and unquoted;
    - allocation-heavy loops run about 73x slower than SPITBOL;
    - program argv after the source is compiled as source.
  - **Seen, not yet rowed:**
    - reals print 17 significant digits where SPITBOL prints 15;
    - SETEXIT keeps its handler after firing;
    - `&STNO`, `&LINE`, `&LASTNO` and `&LASTLINE` read wrong;
    - TRACE of a conditional assignment prints nothing.
- **2026-10-18 early — the harness runs snobol4dotnet (CEO-1822).** Lon's lane ruling: hq_dotnet runs the SNOBOL4 suites and benchmarks on the dotnet engine. The ceo's: the engine is a runner setting.
  - **Landed in harness:**
    - `707e10f`: `S4E_ENGINE`, the `lang@engine` lane, the dotnet arm, the DLL fingerprints, rows keyed `@dotnet`.
    - `25ac84e`: `run_m3` dispatches a port to its own runner script (`run_snobol4dotnet.sh`), in the calling shape agreed with hq_jvm. hq_jvm's `eb5a087` landed the jvm arm on it.
    - `71db7a8`: `from-progress` and the audit carry the `@engine` key, and grade a port in m3 alone.
    - The admission gate is 24 of 24; the admission row is DONE.
  - **Landed in `.github` `815f661f`:** this seat's grid reads only `@dotnet` rows (today "no row yet (engine dotnet)"), and SCRIP's views stay byte-identical.
  - **Engine defects the board found, each red-then-green with sbl as the oracle:**
    - `166fada`: OUTPUT was on stderr. That alone moved 60 rungs from 5 to 51 passing.
    - `4add3d8`: ARBNO of a null-matching argument repeated forever. SPITBOL requires each repetition to advance.
  - **Rows minted:** a `../` source path is resolved to a doubled path; the test host intermittently hangs or crashes.
  - **Noted, not yet minted:** a label after `;` (`...;EN;END`) raises error 23; program argv after the source is compiled as more source files.
  - **Next:** a scratch diagnostic pass of all 1,996 rungs (10 s bound, no retry) is finding the remaining hang classes. Then the live `sno-rungs@dotnet` board writes the first `@dotnet` row, then the package suites, then benchmarks against official SPITBOL.
- **2026-10-17 night — Lon: *"I suspect getting the test harness and benchmarks to run is the first order of business."***
  - **Benchmarks (this repo's runner) run.** `dotnet run --project benchmarks/Benchmarks.csproj -c Release` did not compile (`CS8803`; cured in `0ff85f8`). After that it found no programs: every entry SKIPped, since it looked in `corpus/benchmarks/` and ignored `CORPUS` (cured in `1972f32`). Now 13 of 15 entries measure, all in-process: Roman_1776 33.6 ms, Fibonacci_18 48.0 ms, PatternBacktrack_500 44.8 ms. The other two programs are not in the corpus. Still owed:
    - the Result column reads `?` for 12 of 13, so its correctness check is vacuous;
    - in-process times are not comparable with `sbl` process times; the `x` multiple of THE GOAL item 3 needs a whole-process timing beside the official SPITBOL.
  - **The fleet harness can grade snobol4dotnet with no harness edit.** `.scratch/dn/bin/scrip_as_dotnet.sh` takes the m3 call (`scrip --run [switches] prog.sno`) and runs `dotnet Snobol4.dll -b -f [-dNk -sNk -u] prog.sno`. Its output on a rungs program is byte-identical to the ref. But `corpus_suite_harness.py` refuses this seat rc 2, ONE SEAT, ONE LANGUAGE, because `LANES: snobol4=coo`. It refuses even over a plain-copy scratch population with a scratch progress table. **Blocked on a lane ruling**: the snobol4 suites on the dotnet engine as hq_dotnet's own board, with rows tagged by engine. Asked of the ceo (topic `banner-scoped-to-snobol4-landed`) and of Lon.
  - **Banner:** the ceo landed `.github` `5ed9a61d`: this seat's grid is the 11 snobol4 rows, footnoted as SCRIP's readings until a runner grades dotnet.
  - **Found on the way:** snobol4dotnet treats every argument after the first source file as another file to compile, so a program's own argv (HOST(2,n)) never reaches it. To be minted.
- **2026-10-17 evening — the first row, `dotnet-testsnobol4-reads-every-unit-test-passed-twelve-fail-at-80c828a-ceo-1817`, CLAIMED and still open.**
  - **The "12 FAILED" was an aborted run.** At `80c828a` the test host crashes with a stack overflow 3 s in, during `TEST_Csnobol4_file` (named by `--blame`). The summary line still printed counts ("Failed: 14, Total: 2087" here), so the number was never a measurement.
  - **Cured in `12201c0`.** `ExecuteLoop` caught the fatal `CompilerException` at every level, and it also runs function bodies, so an error inside a function resumed the caller: it looped one call deep and overflowed two deep. SPITBOL and CSNOBOL4 both stop at the first error. Only the outermost `ExecuteLoop` catches now. `TEST_Define_007/008` were red and are green.
  - **The suite now completes: 2,505 tests, 2,429 passed, 74 FAILED, 2 skipped.** Every failure is in `CorpusRef_Csnobol4Suite` (Budne's CSNOBOL4 suite, expectations inline). The 2 skips are `[Ignore]`d "fix pending" tests.
  - **Next:** triage the 74 against `sbl`. A failure where SNOBOL4.NET differs from SPITBOL is a defect, minted one row each. An expectation that is CSNOBOL4-only behaviour (`file.sno`'s FILE functions, which `sbl` answers with error 22) is a question for Lon. The baton's `## NEXT` has the steps.
  - **Watch:** one full run hung once (testhost idle 10 min) and four others finished in 8–12 s. Re-run under `--blame-hang` until it recurs, then mint it.
  - **Landed:** `snobol4dotnet/CLAUDE.md` (`b69c86a`), the repo's own guidance for Claude Code.
- **2026-10-17 — the seat opened.** The ceo measured, at `80c828a`, .NET SDK 10.0.110, in a scratch clone:
  - `dotnet build Snobol4.sln -m:4` succeeds in 11 s with 0 warnings and 0 errors.
  - `dotnet test TestSnobol4/TestSnobol4.csproj -m:4` takes 17 s: **2,084 tests, 2,072 passed, 12 FAILED.**
  - Six build outputs are tracked in git (`*.dll`, `*.pdb`, `*.cache`).
  - The working tree is clean and current with origin.
- **First sitting:**
  1. Re-measure the build and the tests in this root. Name the 12 failing tests here, and mint one row per defect: owner `hq_dotnet`, DONE-WHEN the failing test.
  2. Measure the SPITBOL agreement over `corpus/` and write the table here: the master `tests/snobol4/ALL.sno` entries, the benchmarks, the demos and the SNOBOL4 packages, each run under Snobol4.NET against its `.ref`. Choose the oracle switches and record that choice.
  3. Mint the reds. Cure them one per commit, before any polish.

## THE GOAL, IN ORDER

1. **Correct:** every unit test passes, and every corpus program the oracle answers matches its ref.
2. **Polished:**
   - no build output tracked;
   - a clean build, no warnings;
   - a README that matches what the code does today;
   - the bridge smokes (`scripts/test_smoke_dot_bridge*.sh`) green.
3. **Measured:** benchmark numbers against official SPITBOL (`/home/resources/spitbol-bench-oracle/sbl`), quoted as the bare multiple `x` (reference time over this port's time), each with its load stamped.

## RULINGS

- **Batches, Lon 2026-10-18, in this seat's chat, verbatim:** *"You better be running tests in batches of 100."* The unit suite runs through `snobol4dotnet/scripts/test_in_batches.sh`: 26 batches, each in its own bounded test host, and a batch that hangs or crashes is named NOT RUN. A board runs one partition part at a time (`--partition core` and `chunk:01`..`chunk:20`, 100 entries each, the suite's own `PARTITION.tsv`). Never one whole-population process. This seat's DONE-WHENs measure the same way. Refined the same night, verbatim: *"You run each test seperately except the Rungs are run in batches of 100."* Asked which tests run one per process, Lon chose the corpus programs: each package, demo and benchmark program runs as its own process; SnoRungs runs in 100-entry chunks; TestSnobol4 keeps its batches of 100.
- **Lane, Lon 2026-10-17 night, in this seat's chat, answering "Who should run the SNOBOL4 suites and benchmarks on the snobol4dotnet engine?":** *"hq_dotnet runs them."* The snobol4 suites and benchmarks on the dotnet engine are this seat's own board. LANES gets an engine-qualified entry, and the rows carry engine=dotnet so they never mix with SCRIP's. This seat gets the adapter or a proper engine option into the harness with the ceo.
- The oracle wins over this project's own behaviour unless Lon rules otherwise. Record every such ruling here with its date and words.
- **Scope, Lon 2026-10-17, in this seat's chat, verbatim:** *"The test suite banner is wrong since .NET supports only SNOBOL4, actually SPITBOL."* · *"The test suite banner has the wrong list of languages."* · *"The suite banner should represent the snobol4dotnet executable program, not SCRIP."* SNOBOL4.NET's language is SNOBOL4 in the SPITBOL dialect and nothing else, and this seat's banner grades the snobol4dotnet executable, not SCRIP. Both points went to the ceo by telegram (topic `banner-languages-wrong-for-hq-dotnet`). Landing it needs an engine setting in the harness's SNOBOL4 runners, engine-tagged rows in SUITES.tsv, and a banner that renders its own seat's engine. The ceo decides whether the ceo lands it or assigns the dotnet arm to this seat.
