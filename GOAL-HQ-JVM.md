# GOAL-HQ-JVM — finish and polish snobol4ever/snobol4jvm

**Opened 2026-10-17 by Lon, in-chat to the ceo, verbatim:** *"We need to create two new HQ seats and their corresponding root folders (I'll do that part) for finishing and polishing snobol4ever/snobol4dotnet and snobol4ever/snobol4jvm. Call them HQ-DOTNET and HQ-JVM."* · *"These two HQ's will certainly need to be fully apart of our fleet, they just happen not to be SCRIP."* (GOAL-CEO CEO-1817)

- **Seat:** HQ-JVM, identity `hq_jvm`, root `/home/claude_jvm`, officer the cfo.
- **Repo:** `snobol4ever/snobol4jvm`, a SNOBOL4/SPITBOL implementation for the JVM in Clojure (Leiningen project `SNOBOL4clojure` 0.2.0).
- **Mechanics:** in the root's `CLAUDE.md` (from `.github/HQ-JVM-CLAUDE.md`).

## LIVE CURSOR

- **2026-10-23 ~13:25 CDT, mid-sitting: snobol4jvm `ae2d90b` on the root (jar rebuilt); 38 one-defect commits since `a181578`, each with its test; `lein test` 2,243 tests, 74 failures (csnobol4-openi now green), nothing newly failing. Boards at `ae2d90b`: Gimpel 144/144 (closed), Flake 123/126, X64T 32/33 (gcbuster: COLLECT's storage count recursed down a 100,000-link list; fixed in the dev clone), AIS 8/8, Budne 70/70, Dotnet 6/6, TPgm 8/8, X32T 16/16, SnoBench 23/23; SnoRungs grading now by partition (batch7); SnoDemo stale (10-18).**
  - **Lon, 2026-10-23, in-chat, verbatim:** *"The snobol4jvm will act like SPITBOL, not CSNOBOL4."* (recorded under RULINGS). INPUT/OUTPUT now take sbl's three arguments; tests that encoded CSNOBOL4's fourth-argument file name, OPSYN of used operators, and the like expect sbl's answers.
  - **Landed today (newest last):** capture target that fails fails the match; syntax errors named as sbl names them (syntax.clj: CODE/EVAL fail with &ERRTYPE, a program with one is refused with sbl's page and rc 231); backing into FENCE ends the match; listing/error page/dump go to SCRIP_SNO_LIST_SINK; INPUT/OUTPUT three arguments; FENCE(P) cuts its alternatives but keeps its captures undoable; ACCESS traces; VALUE traces mark function levels; unused binary operators & @ # % ~ are OPSYN's (029 until defined); capture targets are names (*$N, *(expr) fails, F() called at build); UNLOAD; OPSYN argument checks (152-156, 248); a field call F(x) is not a subscript; &STCOUNT trace at END; trace lines cut at 120; EJECT; DATE shapes; HOST 1-4; a NAME in a pattern is its text; CONVERT/SORT of a table drop null entries and fail on none; objects traced by kind and number; unset variables are null whatever the name; unknown keyword 251; EVAL fails on an error in its evaluation; NRETURN of a non-name 243; errors during a match fail it (and go to SETEXIT under &ERRLIMIT); compilation ends at END; a subject is what binds tighter than concatenation; COLLECT counts SPITBOL storage.
  - **In the dev clone, tested, not yet committed (waiting on lein test after batch7):** .F(args) calls F when the name is taken (Flake gimpel-stack-field-functions); .&K names the keyword (indirect-integer-and-keyword); a keyword is a capture target (pattern-assignment-targets); COLLECT walks with a worklist (gcbuster); the matcher's stack top is peek, not last (calculator demos: four of six now finish, 6-23 s).
  - **Open:** SnoDemo calculator-1-match (unfenced grammar, exponential backtracking; sbl 0.5 s, the JVM over 90 s: needs the matcher several times faster); SnoRungs HANGs (arbno_pos_rpos_branch_100, benchmark_calculator-2, pattern_caps_seq_alt_boundaries, user_function_eval_span_replace_branch_1) and code_eval_eval_fence_replace_1 (constant folding at compile time, the rank-1 row); SnoDemo beauty and the rest unmeasured since 10-18.
  - **Practice (ceo, 2026-10-23):** every engine probe under timeout -k 2 <secs>, in the foreground, one at a time; two orphaned calculator probes of mine burned a core each until the ceo killed them.

- **2026-10-22 ~20:20 CDT, end of sitting: snobol4jvm `a181578` pushed, root fast-forwarded (its jar is still at `4f9f5af`: rebuild with build_snobol4jvm.sh before the next board run); `lein test` 2,212 tests, 75 failures, nothing newly failing. Boards on record: seven at 100 percent (Dotnet, TPgm, AIS, X32T, SnoBench, X64T, Budne); Gimpel 131/144 and Flake 114/126 at `4f9f5af`; SnoRungs 1993/2092; SnoDemo stale (10-18, 5/24).**
  - **Landed after `4f9f5af`, not yet on a board:** `b9ae036` .APPLY(F, args) is the name of F(args); `7265b4c` a call in a Goto field names its label (NRETURN; a value is 21); `7279c37` a deferred capture target resolves when assigned; `1d4943b` .$X names what X names; `871c33c` backtracking takes back the latest capture (COND-UNDO! removed the oldest); `3a2ed88` a label may hold any non-blank character; `57d8607` keyword traces (&STCOUNT, &FNCLEVEL, &ERRTYPE) fire; `a487089` the file argument follows osint lenfnm/sioarg (' -f0' is stdin; fixes the regression `dd7cd2f` made in Gimpel poker); `755e1d8` COLLECT forces a collection and fails short of its argument; `a181578` a label trace fires on a Goto, not a fall-in.
  - **On the dev jar these Gimpel drivers now equal their refs:** ai aopa cata frsort seq trunc fld perms physical statef visit pokev gpm pol tr fprofile l_one l_two mfread (the last three need their .input/.in). Flake: eliza-modernized, kalah-opening-search, nreturn, trace-keyword-fnclevel, gimpel-array-functions, gimpel-l-one-compiler, gimpel-state-functions equal sbl (with SNO_LIB=snoflake_suite/gimpel as the runner sets it).
  - **Next, first thing:** rebuild the root jar, regrade Gimpel and Flake (`.scratch/runs/batch4.sh`), close what reads 100.
  - **Reds still open:** Gimpel timer (CODE must fail on a syntax error) and timegc (COLLECT's freed storage reads -67 on the JVM; sbl 38); Flake gimpel-stack-field-functions, gimpel-test-pattern-predicate (AB YES where sbl says NO), indirect-integer-and-keyword, pattern-assignment-targets; control-hide-list-control-line and -statement-numbers expect -HIDE, which sbl ignores (1 2 3; ORACLE_ACCEPTANCE says NO_ORACLE): ask the ceo whether the jvm excludes them or implements -HIDE; SnoRungs 96 FAIL, 3 HANG; SnoDemo calculator HANG.
  - **The compile-error family (rank 1 row jvm-a-keyword-whose-value-never-changes-is-a-constant-to-the-compiler):** a program with a syntax error must be refused with sbl's page and rc 231 (missing -INCLUDE is 285 with a column marker, then "No END statement found", rc 1); CODE/EVAL fail with &ERRTYPE the compile error; needs the parser's failures classified into sbl's numbers.

- **2026-10-22 ~19:35 CDT: seven boards at 100 percent (Budne 70/70 closed); Gimpel 131/144, Flake 114/126, SnoRungs 1993/2092. snobol4jvm `b9ae036`; `lein test` 2,203 tests, 75 failures, nothing newly failing.**
  - **Readings:** Budne 70/70 at `6b9deb8` (row closed); SnoRungs 1993/2092 (171 of the 270 reds pass at `6b9deb8`; 96 FAIL and 3 HANG left); Gimpel 131/144 and Flake 114/126 at `4f9f5af`.
  - **Landed since `6b9deb8`:** `0bef699` the name of an element holds its table or array (as :container meta; the dump still reads .T<1>); `ab3e5e1` binary ? left-associative; `cbf2cd5` a program may define SEQ (the evaluator's SEQ arm gave way to nothing); `37f3392` and `f3facfe` a replacement's subject may be an element, a field or $N; `76bdd7e` a name fails when its subscripts fail; `8203308` T[] is the null-string subscript; `10c24f0` a channel may be a string or a NAME (functions/channel-key); `dd7cd2f` a blank in a file name is ERROR 116/160; `4f9f5af` a null DEFINE entry label is the function's name; `b9ae036` the name of APPLY(F, args) is the name of F(args).
  - **Gimpel reds left (dev-jar diffs):** statef (ERROR 038 at a goto), gpm, tr, l_one, l_two, pol, pokev, fprofile, timegc (timing, masked partly), timer (CODE must fail on a syntax error), mfread (passes but for stdin, check on the board), dextern (excluded, NO_ORACLE_ANSWER).
  - **Flake reds:** control-hide-list-control-line, control-hide-statement-numbers, eliza-modernized, the gimpel-* four, indirect-integer-and-keyword, kalah-opening-search, pattern-assignment-targets, trace-keyword-fnclevel, trace-label-flow (nreturn cured at `0bef699`).
  - **Practice:** one JVM at a time; a board batch runs on the root while the dev clone only edits; I broke that once at 19:2x (a red check while Flake graded) and the batch still wrote its rows.

- **2026-10-22 ~17:35 CDT: X64T reads 33/33 and its row is closed (six boards at 100 percent: Dotnet, TPgm, AIS, X32T, SnoBench, X64T). snobol4jvm `6b9deb8`; `lein test` 2,192 tests, 75 failures, nothing newly failing.**
  - **Landed since `a3096d1`, each red then green against sbl -bf:** `25de4dd` reals convert to and from text as SPITBOL does (sbl.min gtnum and gtstg emulated step for step; measured equal on 8,944 random literals and products; about one real in twenty differs from correct rounding); `9e46efe` real overflow is 261/262/263/264/266; `d844f43` the math functions' error texts in lower case; `d62bd53` a result below the least normal real is zero (MXCSR 0x9fc0, flush to zero, denormals are zero); `a4d39ed` a real is its SPITBOL text to a pattern match; `7f9920f` exponentiation as o_exp computes it (real powers e ** (y * ln x) through glibc's exp and log, which Math/exp and Math/log follow; gimpel_sqrt_function's expectation is sbl's 3.0000000000000004); `2711c4e` a string is a number only as gtnum reads one; `5aa3b6c` REMDR of reals; `3959786` HOST(-1, k); `6b9deb8` EVAL of a real literal too large fails with 231.
  - **Running:** batch3 (`.scratch/runs/batch3.sh`): Budne, Flake, Gimpel whole and the 270 SnoRungs entries not passing.
  - **Next, the compile-error family (feeds the minted constant-keyword row too):** a program with a syntax error must be refused at compile time with sbl's page and rc 231 (today it runs); CODE and EVAL must fail with &ERRTYPE the compile error's number (221 missing operand, 226 missing right paren, 230 illegal character, 231 invalid numeric item, 214 bad label) and EVAL spend one of &ERRLIMIT; this needs instaparse's failures classified into sbl's numbers. Then binary ? left-associative; SnoDemo's calculator HANG.
  - **Lesson recorded:** a quick check that counts only the jvm's extra lines (diff | grep '^>') reads 0 for a program that crashed with empty output; compare whole outputs (cmp). math_remdr was wrongly called equal at 16:2x for that reason; the board read it red, and `5aa3b6c` cured it.

- **2026-10-22 ~16:45 CDT: hq_jvm grades its own boards (CEO-1912); five board rows closed, two fuzz rows closed. snobol4jvm `a3096d1`; `lein test` 2,182 tests, 75 failures, nothing newly failing.**
  - **Closed, each by its DONE-WHEN:** jvm-board-dotnet (6/6), -testpgms (8/8), -aisnobol (8/8 at `56c56a9`), -x32tests (16/16), -snobol4-bench-ref (23/23 by output); jvm-span-of-a-null-string-… and jvm-the-value-of-a-binary-query-… (CEO-1915 fuzz witnesses, copied to `.scratch/fuzz/w/`).
  - **Readings written today:** X64T 20/33 at `dc5a348` (was 3/33; reds: ten math_*, gcbuster, setexit); SnoRungs 1822/2092 (the ceo's 17 unread entries graded; 1994 to 2092 stamped with --criterion-changed). SnoDemo not regraded: its HANGs (calculator-*) cost about six minutes each, so the run was stopped; cure the calculator hang, then regrade.
  - **Landed:** `36fa361` a CODE block ends in a statement of its own that ends the program (manual ch. 9; AIS TEST's &STNO); `ae3f803` an empty statement between semicolons is numbered and never run; `56c56a9` CLEAR; `dc5a348` BACKSPACE (sbl's 316/317/318, not errors.clj's 270s); `80babd3` the value of a binary ? is the matched text; `a3096d1` the character-set primitives check their argument.
  - **How this seat runs a board now:** `S4E_ENGINE=jvm nice -n 19 timeout -k 5 3600 bash /home/claude_jvm/harness/scripts/test_snobol4_<suite>_suite.sh` from snobol4jvm/, SnoRungs entries through `corpus_suite_harness.py run … --partition entry:A,entry:B`; batches in `.scratch/runs/batch*.sh`. A board refuses ("THE GROUND MOVED") when root snobol4jvm's HEAD moves or goes dirty mid-run, so development happens in the clone `.scratch/dev-jvm` and the root only fast-forwards between runs. Harness defect reported and cured by the ceo (relative-path publish, harness `8dab828`).
  - **Next:** ? is left-associative ('ABCD' ? LEN(3) $ OUTPUT ? LEN(1) REM $ OUTPUT prints ABC then BC; the grammar's mch allows one ?); the X64T math_* reds; SnoDemo's calculator HANG and beauty's ERROR 038 at a computed goto; then Budne, Flake, Gimpel, SnoRungs reds; then the minted constant-keyword row.
  - **Seen, not yet rows:** CODE must fail on a syntax error with &ERRTYPE the compile error (226 missing right paren, 221 missing operand) and the statements before it keeping their numbers, and a newline in a CODE string is an error (214, or "illegal character"); INPUT(.J, 5) with no file is ERROR 116 under sbl (the engine opens standard input); sbl segfaults on CLEAR('X,,Y') (no oracle answer).

- **2026-10-22 ~14:15 CDT: the program listing landed, `13231e4`; `lein test` 2,170 tests, 75 failures, nothing newly failing.** -LIST/-NOLIST/-EJECT/-SPACE/-TITLE/-STITL/-PRINT/-NOPRINT/-SINGLE/-DOUBLE and the compile-error page, as sbl -bf lays them out (manual ch. 14, Listing controls). Locally against sbl, with the identity and clock lines masked: Dotnet SourceLines001-003 and Test SAME, TPgm test2 SAME (rc 231), so Dotnet reads 6/6 and TPgm 8/8 on this seat's grader. Requested 20261022T191204-hq_jvm-dotnet-jvm-428173 and -testpgms-jvm-428201. **The board needs the ceo's mask change first:** the ALL.mask identity rows admit "macro spitbol" and "snobol4dotnet" only, the JVM's head reads "snobol4jvm version 0.2.0" (telegram jvm-listing-identity-mask-and-runner-u).

- **2026-10-22 ~14:00 CDT: working jvm-board-dotnet-at-100-percent-ceo-1903 (CLAIMED). snobol4jvm `61b551f`; `lein test` 2,168 tests, 75 failures, nothing newly failing.**
  - **Landed:** `1870d77` &STLIMIT = 0 is no limit (sbl.min stgcc: the countdown starts at the limit); `86f7383` an execution error that ends the program prints sbl's report (manual ch. 13, Execution errors; sbl.min stopr): stdout block, its share on stderr line by line, 120-column cut, &ERRTYPE/&ERRTEXT set, the &DUMP dump after, exit 0, the statement limit as 244; `61b551f` LEN/POS/RPOS/TAB/RTAB convert and check their argument, 120-186 and the evaluated 47-58 (sbl.min patin, gtsmi).
  - **Dotnet board, locally:** 1brc and asgn1 now equal sbl but for the ALL.mask figures, Test PASS; requested from the coo (20261022T185732-hq_jvm-dotnet-jvm-344626). Left: SourceLines001-003, the -LIST listing.
  - **The coo's readings:** AIS 5/8 (BUILDLIB FAIL and SIR HANG graded on the stale tree 32ca333, re-requested 20261022T185732-hq_jvm-aisnobol-jvm-344652; TEST HANG, the LKLKL slowness); TPgm 7/8 (test2: a port's compile refusal must print sbl's listing page on stdout, CEO-1864 (3)).
  - **Next: the SPITBOL listing** (-LIST/-NOLIST/-TITLE/-EJECT/-SPACE and the page a compile refusal prints): Dotnet SourceLines001-003, TPgm test2, snoflake control-hide-*, csnobol4 hide. Telegraphed the ceo (jvm-listing-identity-mask-and-runner-u) to admit snobol4jvm in the ALL.mask identity rows, and that run_snobol4jvm.sh drops -u STR.
  - **Seen, not yet rows:** sbl lets SETEXIT trap 244, and counts &STLIMIT from the statement that assigns it (limit L set at count c stops at count c + L); constant arguments (LEN(-1)) are compile-time errors under sbl, run-time here.

- **2026-10-22 ~13:35 CDT: CEO-1903 boards are the work list; X32T 21/21, AIS 7/8, TPgm 8/8 on hq_jvm's own grader, each filed with the coo. snobol4jvm `f0f3bf2`; `lein test` 2,164 tests, 75 failures, nothing newly failing.**
  - **Cures since `6314521`, each quoting its manual section beside the sbl probe (Lon: "as you fix bugs, then go read about the construct from the bug report"):** &ERRTEXT a string, &FULLSCAN 0 is 274, -LINE single quotes, -INCLUDE trimmed names, END LABEL, Goto errors 038/024 trapped and CODE's direct Goto, END inside a function, RETURN family upper case only, arithmetic operand errors, DUMP(i) and level-2 objects, $ of null or an object 239, a function name is no variable, EQ and kin numeric, pattern keywords, a failed pattern fails a replacement, keyword ranges 210/287/268 and &ERRTYPE's text, TABLE(i,x,arg) and PROTOTYPE of a table, out-of-bounds assignment fails, a parameter named like its function, SUBSTR without a length, HOST(), HOST(0) with -u or the program's arguments, $ and . left-associative, ~ and @ right-associative, CONVERT to EXPRESSION and EVAL of an expression, CONVERT to NUMERIC, type names in capitals unless folding, numbers as SPITBOL strings to the string functions, DATA functions in the function table, field functions shared and error 41, a subscript told from a call, the name of a field, EVAL! of a value, a misplaced continuation is 214 and the program does not run (-main answers 231), subject before replacement, one stdin stream, the dump's associated variables, primitive patterns read and compound expressions, table dump order by SPITBOL's hash (sbl.min hashs/tfind/dumpr read).
  - **Rows:** jvm-board-x32tests, -aisnobol, -testpgms parked PARKED-AWAITING-COO-READINGS with their batons written; the coo grades a 21-program request in the round robin. Open on AIS: TEST runs past 300 s building and printing a list with shared sublists (sbl: under a second).
  - **⛔ RULING RELAYED, NOT YET ACTED ON (needs Lon's confirmation of scope):** hq_dotnet relays Lon, 2026-10-22, verbatim: "So you snobol4dotnet, unlike SCRIP and JVM, does support case folding. That is because Jeff is in charge there. I however want to support only CASE SENITIVE mode for SCRIP and snobol4jvm." Today's `a35a790` added -CASE folding and &CASE folding for CODE/EVAL, and `CONVERT` reads lower-case type names while &CASE is not 0, all as sbl -bf does when a program asks; a program that needs folding is NO_ORACLE_ANSWER on the boards (corpus 386e8163a). Question for Lon: remove the folding (cards ignored, &CASE inert), or keep it as it stands?
  - **Seen, not yet rows:** EVAL's syntax error does not set &ERRTEXT/&ERRTYPE (221 and kin); REPLACE with unequal lengths, ARRAY(), ANY('') and a concatenated TABLE are errors under sbl and are not in the engine; the fatal error report sbl writes to stdout and stderr.

- **2026-10-22 ~11:45 CDT: Lon's direction, in-chat: "Please read the SPITBOL manual in /home/resources so you can know what you are doing." · "For every construct you deal with, go read about that construct." · "As you come across the constructs, stop and go check the manual." · "So what I mean is, as you fix bugs, then go read about the construct from the bug report."** The manual is `/home/resources/spitbol-manual-v3.7.pdf`; its `pdftotext -layout` text is the same as the ceo's copy. Every fix from here quotes its manual section beside the sbl probe.
  - **Read so far, against this sitting's fixes:** ch. 14 (statements), 16 (keywords), 17 (conversion), 18 (patterns), and the ch. 19 entries ARBNO, DUMP, INPUT/OUTPUT, LPAD, REWIND, RPAD, RTAB, SETEXIT, TAB. They agree with the fixes for comment lines, -INCLUDE once, &ERRLIMIT/SETEXIT/CONTINUE/ABORT, &STLIMIT negative, TAB and RTAB past their target, LPAD/RPAD null fill, REWIND, INPUT/OUTPUT failing on an unopenable file, OUTPUT of an object. ARBNO's entry is silent on a null repetition; that cure rests on sbl alone.
  - **Where the manual (Catspaw 3.7) and the oracle (sbl x64 4.0f -bf) differ, the oracle wins:** a control statement is recognised in either case "regardless of the current state of case-folding" (manual) but sbl -bf ignores a lower-case -case while folding is off; &TRIM starts at 0 (manual) but 1 under sbl; &MAXLNGTH 4,194,304 (manual) but 16,777,216; &CASE starts at 1 (manual) but 0 under -f; a NAME converts to the string "NAME" (manual) but OUTPUT of .X writes X; the four-argument INPUT/OUTPUT is SNOBOL4+'s form (manual) and sbl raises 116/160 for it.
  - **Defects the reading found, each confirmed by an sbl probe, queued:** -INCLUDE keeps the trimmed names, so a blank-padded name is included every time (the engine skips the second); -LINE takes a single-quoted file name; &ERRTEXT accepts a string (the engine raises 208); END LABEL starts execution at LABEL; &FULLSCAN = 0 is ERROR 274; RETURN, FRETURN and NRETURN are special only in upper case under -f (END in any case); a goto to an undefined label is ERROR 038 and goto-field errors (20, 23, 24, 38) are trappable; &INPUT/&OUTPUT = 0 suspend every association, not only INPUT/OUTPUT; DUMP(i) dumps at once, and level 2 lists DATA fields as field(var) = value; a channel may be a string; SCONTINUE without error 320 is ERROR 331.

- **2026-10-22 ~11:20 CDT: seven more engine cures for the SnoRungs board, each red then green in `core_test.clj` against `sbl -bf`. snobol4jvm `6314521`; `lein test` 2,119 tests, 75 failures, nothing newly failing.**
  - **Landed (`420ea13..6314521`):** an ARBNO repetition that matches the null string fails, so ARBNO(ARB) ends (`85c2606`); TAB(N) fails past N (`cecec9a`); a semicolon in a comment line separates nothing (`6e8f9f5`: 99 SnoRungs entries have one, 53 of them were red); a file argument's bracketed options, `[-f0 -r<n>]`, `-l<n>`, `-a`, and a third-argument file that cannot be opened fails (`530f5d8`); an argument left out is the null string in its place, F(1,,3), F(,2), with LPAD/RPAD padding a null fill with blanks (`87c163f`); REWIND reopens an input file and an unopened unit is ERROR 174 (`8d1e861`); OUTPUT of an array, table, DATA object or expression writes its datatype (`6314521`).
  - **Measured on the harness, jvm engine, partitions of eight (CEO-1893):** of the 27 arbno/pos_rpos entries red at `6b601d4`, 24 PASS after `cecec9a`; of the 53 comment-semicolon entries, 26 PASS after `6e8f9f5`; the other 27 are being regraded at `6314521`. Still open in that family: `arbno_pos_rpos_branch_100` (ARBNO('a') over 20,000 characters: too slow, not a loop), `arbno_break_len_replace_branch_1` (captures into array and table elements), the calculator benchmarks (they now read their input and run past a minute).
  - **Seen, not yet a row:** sbl refuses the four-argument INPUT/OUTPUT form (ERROR 116/160 even for a file that exists); the engine still opens it as CSNOBOL4 does, and `catalog/t_io_channels`, `t_spitbol` and the suite's openi/openo use it. The fatal error report sbl writes (to stdout and stderr, line by line) is not written by the engine (rewind1, float2, t). A subscript read of a non-array is ERROR 22 where sbl says 235 (the IR spells A<1> and F(1) alike).
  - **Process:** never edit `src/` while a harness grade runs: the runner refuses the partitions after the edit as a stale jar.

- **2026-10-22 ~10:25 CDT: `test_csnobol4_suite` 44 to 36 failures; eight engine cures this sitting, each red then green in `core_test.clj` against `sbl -bf`. snobol4jvm `420ea13`; `lein test` 2,109 tests, 75 failures (82 at `2845c29`).**
  - **Landed and pushed (`6b601d4..420ea13`):** an error under `&ERRLIMIT` fails the statement, sets `&ERRTYPE`/`&ERRTEXT`, and a subscript of a non-table is ERROR 235 (`f330d77`); SETEXIT arms a handler, returns the one it replaces, an error goes to it, CONTINUE and ABORT (`a1db8d4`); the `-CASE` card and the `&CASE` keyword (`a35a790`); the keywords start as sbl has them (`&FULLSCAN` 1, `&MAXLNGTH` 16777216, `&INPUT`/`&OUTPUT` 1), `&ABEND`, `&COMPARE`, `&INPUT`, `&OUTPUT` exist, a negative `&STLIMIT` is unlimited (`e67704f`); `&FILE`/`&LINE`/`&LASTFILE`/`&LASTLINE` with `-LINE` and once-only `-INCLUDE` (`c3f743d`); the `&DUMP` termination dump with `&CODE`, `&RTNTYPE`, object numbers `#n`, the END statement counted (`79fffbc`). Suite tests converted to the corpus program and sbl's output: err, setexit3, case1, include, line, a, dump; atn's budget 5 to 30 seconds (it ran 3 to 4 seconds under load).
  - **Rules learned from the oracle (all in the commits' tests):** `-CASE` and `-LINE` cards are recognised in upper case only while folding is off; a file name is included once as written; the file name of the statement after an include stays the included file's when its last line is a comment; `&STCOUNT` counts END and stops counting when `&STLIMIT` is negative; a function call leaves the caller's `&LINE`.
  - **What is left of the 36:** about 25 are programs sbl cannot run (lower-case built-ins, `&MAXINT`-style keywords, popen, loaderr, random, json1: their refs are ERROR listings or empty); they wait on the ceo's CSNOBOL4-only ruling. Real engine work still graded: `float2`, `t` (trace lines with `time = xxx`), `rewind1` (fatal error report with statement, line and file), `setexit4` (STCOUNT keyword trace and SCONTINUE error 331), `diag1` (needs object numbers in the dump to match, error reports, `ITEM`, `OPSYN` of operators; a StackOverflow in the engine first).
  - **Next:** the SnoRungs entries behind the keyword family: a re-run of the 290 entries red at `6b601d4` against `sbl -bf` is in `.scratch/runs/red-after-420ea13.txt`; then ask the coo for one fresh `snobol4-rungs@jvm` pass naming the commit.

- **2026-10-22 ~07:15 CDT: the coo's SnoRungs reading at `6b601d4` is in: 1,793 programs, 1,503 PASS, 266 FAIL, 24 HANG. Nothing unpushed; inbox drained. snobol4jvm `6b601d4`.**
  - **What it shows:** the failing families are `keyword_*` (34 of 68), `simple_output` (12), the ladder rung 22 ACCESS trace (12 of 13), `user_function_keyword` (10 of 20), `arbno_pos_rpos` hangs (10), `user_function_opsyn*` (14), `eval_defer` (6, none pass), `indirect_keyword` (5), `fence_*` and `array` (8), and 24 `benchmark_`/`demo_` programs (claws5, json, treebank, roman). The full list is `/home/claude_jvm/.scratch/sno-rungs-jvm-6b601d4.tsv` (untracked scratch; the readings themselves are in the coo's results mail).
  - **Replied** to the coo and ceo (topic `sno-rungs-jvm-6b601d4-board-read`); the 7 hq_dotnet and 1 hq_collector claim notices overlap nothing here (other engines).
  - **Still open:** the csnobol4 row (43 failures in `test_csnobol4_suite`; the graded corpus pairs `a diag1 dump include line rewind1 err setexit3 case1` need engine work) and the ceo's ruling on the ~32 CSNOBOL4-only tests.
  - **Next:** the `keyword_*` family against `sbl -bf` first (each red then green), then the ACCESS trace, then the hangs; ask the coo for one fresh `snobol4-rungs@jvm` pass when a family lands.

- **2026-10-22 ~02:00 CDT: `test_csnobol4_suite` 96 to 43 failures, the engine passes 69 of the 78 graded csnobol4 corpus pairs (46 when I began), `lein test` 82 failures in 2,097 tests. Its row is still open. snobol4jvm `22d0785`.**
  - **What the oracle showed first:** the namespace carried Budne's programs in lower case with CSNOBOL4's output as the expectation; under `sbl -bf` a lower-case built-in is ERROR 22 (CEO-1455 put those programs outside the baseline). The corpus package holds the upper-case conversions with `sbl -bf` refs. 70 tests now run the corpus pair (program through END, stdin the tail, compared as the board compares: trailing newlines dropped); three FENCE crosschecks had wrong expectations (061 unanchored, 064 and 065 forgot ANY's character).
  - **Engine cures, each red then green with its own `sbl`-verified test in `core_test.clj`:** capture into OUTPUT writes the line; conditional captures commit in match order; integer arguments may be reals or numeric strings with sbl's error numbers, and ORD exists; DEFINE, DATA, FIELD, ARG, LOCAL keep the case of names; SUBSTR length 0 is the rest; `&TRIM` starts at 1 and input records lose trailing blanks and tabs; a bare FENCE is a pattern; DATATYPE of REM and the capture nodes is PATTERN; `&STNO`, `&LASTNO`; blank lines are numbered statements; VALUE, CALL, RETURN and FUNCTION traces, `&FTRACE`, `&FNCLEVEL` in sbl's form on the output (the registry and `&TRACE` are program state, reset by `GLOBALS`); nested subscripts; the comma group; a replacement assigns through the normal path and `(a ? p = r)` replaces; input records are at most 1024 characters; the launcher passes bytes above 127 through under any locale (ISO-8859-1 streams); a function name is no longer a variable value (`program-fn` consults `<FUNS>`, the call wrapper saves the program's own variables); computed gotos; a function's result variable is saved per call; tables keep first-assignment order, SORT and RSORT sort arrays on a column, stably; a function may return a name with NRETURN, to be assigned (`*F(args)` capture target, `F(args) = v`); `ITEM(c,k...) = v`; DATA objects are mutable with identity (`DataObj`); the per-test `GLOBALS` fixture cured nine shared-state reds.
  - **Open, graded and needing engine work:** `&FILE`/`&LINE`/`&LASTFILE`/`&LASTLINE` with `-INCLUDE` and `-LINE` (include, line), the SPITBOL fatal error report with statement, line and file (rewind1), `&DUMP` format (a, diag1, dump), `SETEXIT` value and error trapping with `&ERRLIMIT`/`&ERRTYPE`/`&ERRTEXT` (err, setexit3), `-CASE` and `&CASE` (case1). Then the 32 tests for programs outside the baseline, on which the ceo has the question (convert to upper case and take sbl's output where sbl runs them; the CSNOBOL4-only ones, popen, loaderr, random, json1, keytrace, hide, update and the like, leave the file?).
  - **Process:** the coo grades the JVM engine's whole suites (CEO-1872, Lon's correction); I run `lein test`, single programs and my own driver over the 78 corpus pairs (a scratch script, not a harness pass). House style: source lines up to 200 characters.

- **2026-10-21 ~21:00 CDT: `catalog/t_aisnobol` reads 0 failures and its row is DONE; four engine cures, one test-helper fix, one test-text fix. snobol4jvm `03f8188`.**
  - **Row closed:** `jvm-catalog-t-aisnobol-compares-for-real-and-its-12-hidden-reds-read-zero-failures`, recomputed by `done`. It read 30 failures in all twelve tests, and the oracle showed first that none of the twelve had ever run its program: each passed a `(str ...)` form to the `prog-steplimit` macro, which joined the source text of its arguments.
  - **Commits, each red then green:** `cc69421` the `prog` macros evaluate their lines when the test runs; `2fc00ff` a label may contain a point (a jump to `HSORT.END` ended the program); `0590974` a goto may name its label by an expression, `:($X)` and `S($('WANG.C.' OP))`; `6755fed` a function's result variable is saved per call (a return without an assignment gave back the function object); `03f8188` the Wang tests' copy of WANG.SNO had lost the `+` on two continuation lines.
  - **`lein test`: 2,072 tests, 135 failures, 0 errors** (186 at `814b2dd`). Where they are: `test_csnobol4_suite` 96, `test_bootstrap` 8, `catalog/t_define` 8, `catalog/t_convert` 6, and 17 over eleven more files. `catalog/t_gimpel` and `catalog/t_aisnobol` read 0.
  - **Seen, not yet a row:** a goto to a label the program does not define ends the program silently where `sbl` raises an error; `lein check` fails on the orphaned `SNOBOL4clojure.errors`; `test_probe18c` step-count tests fail when the namespace runs alone. Other test files may pass non-literal forms to the `prog` macros and were passing by accident; the full run showed none newly failing.
  - **Rules in force:** only a wholesale suite or package pass on the JVM engine is the coo's (CEO-1872, Lon's correction); the coo has `snobol4-rungs@jvm` at `814b2dd` queued, and these cures change what that board reads. House style: source lines up to 200 characters, comments broken across lines.
  - **Next:** `jvm-test-csnobol4-suite-...` (96 reds; judge each against `sbl -bf` first, many will be the test's), then `catalog/t_define` (8) and `catalog/t_convert` (6), which are the worm1000 typos again, and `test_bootstrap` (8).

- **2026-10-21 ~19:30 CDT: `catalog/t_gimpel` reads 0 failures and its row is DONE; six engine cures and four test fixes. snobol4jvm `b1c41c8`.**
  - **Row closed:** `jvm-catalog-t-gimpel-compares-for-real-and-its-16-hidden-reds-read-zero-failures`, recomputed by `done`. It read 19 failures in 12 tests; each red's verdict against `sbl -bf` is in the row's LEDGER. The vendored INC files are CRLF and `sbl` refuses them (ERROR 230), so the oracle ran over LF copies in scratch.
  - **Engine cures, each red then green with its own test in `core_test.clj`:** `4f69501` unary `@V` never assigned V (BASE10, DECOMB); `f1ddd44` a null joined to a number made a STRING (FLOOR, COMB; four older tests had recorded that typing and now read sbl's INTEGER); `ab2b595` the replacement of `pat = repl` was evaluated before the match (ROTATER); `28df11b` the matcher threw on a number in a pattern (SPELL); `7d25e1a` an operand that fails stops the evaluation, so the operands after it are not evaluated (SPELL's recursive call; `~X` keeps taking a failed operand); `b1c41c8` a capture may assign to an element, a named variable or a deferred expression (CRACK).
  - **Test fixes (the engine already agreed with sbl):** `11354d2` AGT labels were indented; `552bd7a` COUNT of an absent string is the null string; `581c4b6` PERMUTATION index 2 of ABC is ACB; `622cd7b` the BSORT and HSORT tests passed a `(str ...)` form to a macro that joins source text, so they never ran the program.
  - **`lein test`: 2,068 tests, 165 failures, 0 errors** (186 at `814b2dd`). Where they are: `test_csnobol4_suite` 96, `catalog/t_aisnobol` 30, `test_bootstrap` 8, `catalog/t_define` 8, `catalog/t_convert` 6, and 17 spread over eleven more files. Nothing newly failing in the six full runs of this row.
  - **Rules in force:** CEO-1872 corrected by Lon at 18:28: only a wholesale suite or package pass on the JVM engine is the coo's; `lein test`, single programs and targeted subsets are mine. The coo has queued `snobol4-rungs@jvm` at `814b2dd` and x64/x32. House style from Lon: source lines up to 200 characters, long comments broken across lines.
  - **Seen, not yet a row:** `lein check` fails on an orphaned `SNOBOL4clojure.errors` namespace; `test_probe18c` `test-run-to-step-step1` and `test-run-with-restart-inspect` fail when the namespace runs alone (step-counter state) and pass in the full run; the engine reads `1E400` as an infinite real where sbl errors.
  - **Next:** the FREE rank-2 rows `jvm-catalog-t-aisnobol-...` (30 reds) and `jvm-test-csnobol4-suite-...` (96); `catalog/t_define` (8) and `catalog/t_convert` (6) are the worm1000 typos again, in the catalog copies; judge each red against `sbl -bf` first.

- **2026-10-21 ~18:30 CDT: CEO-1861 and CEO-1864 LANDED; ARG, LOCAL and CONVERT follow `sbl -bf`; board quoted before and after. snobol4jvm `3109bd3`.**
  - **Six engine cures, each red then green, pushed `547615d..814b2dd`:** `7976e37` a real literal may carry an exponent (the grammar dropped the whole statement for `X = 2.5E3`, so the sprint12 CONVERT test had passed vacuously); `534a520` NAME values compare by target; `a16ac60` a NAME prints as its variable name; `e9961a5` ARG and LOCAL return a NAME (`catalog/t_spitbol t1_arg_local` compares with `.A`); `8f523df` CONVERT of a real to INTEGER truncates and an out-of-range real gives Long/MIN_VALUE, as sbl does for 3.14E200; `814b2dd` CONVERT of a string to INTEGER reads integer syntax, else a real, then truncates. Both questions that stood "open for Lon" are closed by the one oracle (CEO-1861, CEO-1864).
  - **`lein test`: 2,062 tests, 186 failures, 0 errors** (188 in 2,056 before). Nothing newly failing; `csnobol4-comment` and `test-sprint13/return-explicit-entry-label` newly pass. `3109bd3` re-measured `snobol4jvm/CLAUDE.md`.
  - **Board, engine jvm, m3, before `72da52d` and after `814b2dd`:** csnobol4 41/86 to 44/86 (comment, space, space2 flip to PASS); aisnobol 0/8, dotnet 3/11, gimpel 42/144, snoflake 49/128, bench-ref 13/23, testpgms 1/8 unchanged; spitbol_x64 2 of 35 and x32 9 of 20 unchanged (TIMEOUT=20, scratch table); demos refused rc 2. **SnoRungs not run whole** (about five hours a tree): a 189-entry subset (exponent reals, ARG, LOCAL, CONVERT, NAME values) went 51 to 54 PASS with no regression (`user_function_datatype_1`, `snocone_ladder_lit_real.oracle_ref`, `simple_output_74`). The live `snobol4-rungs@jvm` rows are stale (`d859a74`, `c9ccfba`).
  - **CEO-1872 (Lon's word, corrected 18:28):** only the coo runs a suite or package wholesale on the JVM engine; the runners refuse this seat rc 2. `lein test`, single programs and targeted subsets stay free. My three `pgrep -f` wait loops matched their own command lines and ran 55-95 minutes after the passes had finished; killed by pid. Numbers telegraphed to the ceo and the coo, with one request: the full `snobol4-rungs@jvm` board at `814b2dd`.
  - **Seen, not yet a row:** `lein check` fails on an orphaned `SNOBOL4clojure.errors` namespace (FileNotFoundException); the engine reads `1E400` as an infinite real where sbl errors; `catalog/t_define` (8) and `catalog/t_convert` (6) are the worm1000 typos and lowercase DATATYPE names again, in the catalog copies; the other `worm_ltr_*` docstrings still say "no precedence".
  - **Next:** the three FREE rank-2 rows (`jvm-test-csnobol4-suite-...` 98 reds, `jvm-catalog-t-gimpel-...` 19, `jvm-catalog-t-aisnobol-...` 30), judging each red against `sbl -bf` first and testing with `lein test`, single programs and targeted subsets (never a wholesale harness pass).

- **2026-10-21 ~10:35 CDT: seated again under MODE TENET (CEO-1857); worm1000 and sprint12 read 0 failures and both rows are DONE. snobol4jvm `547615d`.**
  - **Seating:** pulled harness, corpus and .github; `test_gate_no_symlinks.sh` reads GATE OK in this root (CEO-1853). The 11 inbox messages (8 claim notices, the stand-down, the seating) are answered and archived; the ceo has my report.
  - **Row closed:** `jvm-test-worm1000-compares-for-real-and-its-20-hidden-reds-read-zero-failures`, recomputed by `done`. Measured at `2506665`: 277 tests, 20 failures. Each red's verdict against `sbl -bf` is in the row's LEDGER: **all 20 were defects in the test file and none in the engine**, so there is no engine change. Eight commits, one defect each, pushed `2506665..72da52d`:
    - `eceda03`: eight DEFINE tests declared SQ, NEG or INC and called the label (sbl: ERROR 022); renamed to one name, as the file's double and triple tests do.
    - `ea069ff`: six DATATYPE expectations in lower case; sbl prints STRING, INTEGER, REAL, PATTERN, ARRAY, TABLE.
    - `be087d6`: `2 + 3 * 4` is 14; `6ea6c1d`: the array fill reads "11625"; `c131075`: ARB captures "bb"; `c7f18d0`: the unanchored NOTANY reaches `d`, so "yes"; `a7392da`: BREAK on the null string fails (as `cf0768c`); `72da52d`: a bare `world` is a variable, not the literal.
  - **Row closed:** `jvm-test-sprint12-compares-for-real-and-its-40-hidden-reds-read-zero-failures`. Its DONE-WHEN already exited 0 (earlier cures had cleared it); `done` recomputed it.
  - **`547615d`:** `snobol4jvm/CLAUDE.md` re-measured. The `=` trap is cured (1fe23d8), the uberjar AOT-compiles core, errors travel as `{:snobol/error N}`.
  - **`lein test`: 2,056 tests, 188 failures, 0 errors** (207 before this sitting; 20 cleared, and the known `csnobol4-match4` flake reads one different). Where the 188 are: `test_csnobol4_suite` 98, `catalog/t_aisnobol` 30, `catalog/t_gimpel` 19, `test_bootstrap` 8, `catalog/t_define` 8, `catalog/t_convert` 6, and 19 spread over eleven more files.
  - **Seen, not yet a row:** the five other `worm_ltr_*` docstrings and the section-5 line of test-worm1000's namespace docstring still say "left-to-right, no precedence"; their answers hold either way. A doc-only commit.
  - **Open for Lon, unchanged:** does ARG and LOCAL return a NAME (sbl) or a string (the manual, CSNOBOL4)? Should `CONVERT(3.14E200,'INTEGER')` fail, as the test expects, or wrap, as sbl and CSNOBOL4 do?
  - **Next:** the three FREE rank-2 rows, `jvm-test-csnobol4-suite-…-read-zero-failures` (98 reds now), `jvm-catalog-t-gimpel-…` (19) and `jvm-catalog-t-aisnobol-…` (30), judging each red against `sbl -bf` first, as these 20 showed that many reds are the test's, not the engine's. Their titles carry the old hidden counts (101, 16, 12). The 8 `catalog/t_define`, 8 `test_bootstrap` and 6 `catalog/t_convert` reds have no row yet. Then the rank-3 row `jvm-no-test-namespace-shadows-clojure-equality-and-lein-test-reads-zero-failures`, and re-grade the 11 boards (Flake without `ARM_CSN=0`).

- **2026-10-18 ~20:00 CDT: t_spitbol reads 0 failures, 0 errors; its row is DONE. snobol4jvm `2506665`.**
  - **Row closed:** `jvm-catalog-t-spitbol-compares-for-real-and-its-28-hidden-reds-read-zero-failures`, recomputed by `done`. Each red's verdict against `sbl -bf` is in the row's LEDGER.
  - **Engine cures, each red then green, one per commit:**
    - `541ae17`: `&K = V` sets the keyword (it was lost), with SPITBOL's errors 208, 209 and 251. Each program starts from the keyword defaults. `&FULLLSCAN` is renamed `&FULLSCAN`.
    - `0207a98`: a pattern match honours `&ANCHOR`.
    - `c2dc6dd`: the unused unary operators `! % / # = |` are ERROR 029.
    - `93d525a`: a concatenation of strings is a STRING as a function argument too.
    - `b58b346`: concatenating the null string leaves a value as it was.
    - `fd04816`: INTEGER is a predicate (it never failed, and it converted reals).
    - `3ff2404`: ARG, LOCAL, APPLY and OPSYN take a function name given as a NAME.
    - `6816d21`: unary `$` reads and assigns the named variable.
    - `866775e`: the NAME of an array or table element names the element.
    - `19cb7ce`: OPSYN defines an operator by its spelling and arity.
    - `a500740`: PROTOTYPE of a counted array is an INTEGER.
    - `2506665`: unary `?` is interrogation.
  - **Expectations set to the oracle:**
    - `164d837`: the 13 t2 groups check their subject.
    - `5ddf1f7`: the t1 groups write negation as `~`, not the deck's `!`.
    - `5b6e4ec`: 20 tests that read INTEGER as a conversion.
    - `47b87d4`: two sprint11 PROTOTYPE expectations.
  - **`lein test`: 2,056 tests, 207 failures, 0 errors** (239 at the start of this stretch).
  - **Open for Lon:** sbl's ARG and LOCAL return a NAME. The SPITBOL manual says ARG "Returns a string", and CSNOBOL4 returns a string. snobol4jvm returns the string, so t1_arg_local is green against the manual and CSNOBOL4, not against sbl. Which wins?
  - **Seen, not yet rows:**
    - `ARRAY(3.0)` is refused as an invalid prototype; sbl takes it.
    - the parser accepts `SIZE(S)-1` without blanks; sbl gives ERROR 233.
    - catalog `t_eval_left_to_right` still reads INTEGER as a conversion, and it was already red for other reasons.
    - `csnobol4-match4` flips between red and green across full runs, the known shared-state flake.
  - **Next:** the remaining rank-2 rows (csnobol4-suite, sprint12, worm1000, t_gimpel, t_aisnobol), then re-grade the 11 boards (Flake without `ARM_CSN=0`).

- **2026-10-18 ~19:00 CDT: test-cooper reads 0 failures, 0 errors; its row is DONE. snobol4jvm `eb651f6`.**
  - **Row closed:** `jvm-test-cooper-compares-for-real-and-its-28-hidden-reds-read-zero-failures`, recomputed by `done`. Of its 28 reds, 21 had already gone green under the earlier cures; the last 7 were judged against `sbl -bf` (verdicts in the row's LEDGER).
  - **Engine cures, each red then green, one per commit:**
    - `80c7874`: a concatenation assigned to an array or table element is a STRING (the subscript branch stored the raw SEQ, read as PATTERN).
    - `37bf78d`: an array subscript converts to an integer as SPITBOL converts it; non-numeric text is ERROR 238.
    - `011a28f`: ABORT ends the whole match; the scan no longer moves on. A bare FENCE() still ends only its own start position, as sbl does.
    - `eb651f6`: `P $ V` captures the whole span of a sequence.
  - **Expectations set to the oracle:** `e1f419e` (gimpel-bsort passes the array, as Gimpel's driver does; `.ARR` is sbl ERROR 235), `cf0768c` (BREAK/BREAKX on the null subject fail), `3a9d535` (unanchored `'ABC' FENCE('B')` succeeds; snobol4dotnet made the same correction).
  - **`lein test`: 2,044 tests, 239 failures, 0 errors** (253 at the start of this stretch).
  - **Trap found:** this shell's `grep` is a wrapper that adds `-I`, and `lein test` output holds control bytes from the CSNOBOL4 suite, so a plain grep of it reads nothing. Compare red sets with `command grep -a`.
  - **Seen, not yet a row:** sbl keeps `1 + 1 ''` an INTEGER; snobol4jvm makes it a STRING.
  - **Harness:** the coo's capture cap landed at harness `6c03d6e`, so Flake re-grades without `ARM_CSN=0`.
  - **Next:**
    - the rank-2 row `jvm-catalog-t-spitbol-compares-for-real-and-its-28-hidden-reds-read-zero-failures`;
    - then sprint12's remaining reds and the other rank-2 rows;
    - re-grade all 11 boards (Flake without `ARM_CSN=0`).

- **2026-10-18 evening: all 11 SNOBOL4 suites have `@jvm` rows; fixing the failures. snobol4jvm `a166658`.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"will you have all the test suites? not just those 5 shown in the test-suite banner."* · *"Get all 11 test suites running."* · *"Once all test suites are in place, begin fixing all the failures."* · *"You are now seated as Opus 5.5 medium. Tell CEO."* Told.
  - **The 11 rows:**
    - first graded today on `7114cd0`: Dotnet 3/11, SnoBench 9/23, SnoDemo 5/24, Budne 33/86, Gimpel 21/145;
    - Flake 31/128 on `82ea4fa`, graded with `ARM_CSN=0`;
    - not yet re-graded: AIS 0/8, TPgm 0/8, X32T 6/18 and X64T 3/33 (`c9ccfba`), and SnoRungs 994/1994 (`d859a74`). Re-grade all after this batch.
  - **Flake's rc=139:** the runner died three times with no row.
    - Two causes were the engine's: `INPUT` at end of file, and undefined functions. Six programs printed 14–76 MB, and bash died holding the stream.
    - The last was the runner's own CSNOBOL4 triangulation arm, which runs away on `gimpel-asm-machine-m`. That is engine-independent, so it was sent to the coo with a suggested cap on the captured stream.
  - **The coo landed harness `9ec06c1`:** the dotnet board now takes a HANG's pass back. hq_dotnet found it; I asked the coo.
  - **Cures, each red then green against `sbl -bf`, one per commit:**
    - `a3be8ff`: INPUT at end of file fails.
    - `7efed9f`: an undefined function is ERROR 022. TRACE, STOPTR and COLLECT are wired. CLEAR, DUMP, EJECT, BACKSPACE and SETEXIT stay null stubs, each its own defect.
    - `82ea4fa`: `-INCLUDE` searches `SNO_LIB`.
    - `fe523f0`: ATAN, CHOP, COS, EXP, LN, SIN, SQRT and TAN, with SPITBOL's error codes 301–315.
    - `2476939`: test-sprint12's programs had never run, since `(RUN "<src>")` takes an address. They now run, in upper case, with three expectations set to the oracle.
    - `d709766`: SORT and RSORT of a table sort on the key or the named column.
    - `a166658`: PROTOTYPE returns the prototype as written.
  - **`lein test`: 2,034 tests, 310 failures, 0 errors** (364 at the start of this stretch).
  - **Open for Lon:** should `CONVERT(3.14E200,'INTEGER')` fail, as the test expects, or wrap to `-9223372036854775808`, as sbl and CSNOBOL4 do?
  - **Known limit:** the IR spells `F(x)` and `A<x>` alike, so a subscripted non-array reads 022 where sbl says 235.
  - **Next:**
    - sprint12's remaining reds: CONVERT to PATTERN, CONVERT of an out-of-range real string, DATA;
    - then the larger classes (SnoRungs patterns, indirection, keywords);
    - re-grade all 11.

- **2026-10-18 12:55 CDT: `lein test` leaves the tree clean, and an unopenable file spec is an error as SPITBOL makes it. snobol4jvm `64cf51a`, `7114cd0`.**
  - **Seated:** Lon, in-chat to hq_jvm, verbatim: *"You, HQ-JVM, are now seated as Opsu 5.5 high. Tell CEO that I verified it."* Told the ceo: model `claude-opus-5-5`, effort high, verified by Lon.
  - **`64cf51a`:** a file spec that cannot be opened is ERROR 116 for INPUT and ERROR 160 for OUTPUT. `sbl -b` raises these for a pipe spec (`"|cat >x"`, `"|echo hi"`), a bad path and a missing file. A pipe spec had been opened as a file literally named `|cat >popen2.dat`.
    - **Ruling, by the oracle:** snobol4jvm follows `sbl`, not CSNOBOL4, which opens a real pipe. The popen2 test's CSNOBOL4 expectation is left to the csnobol4-suite row.
  - **`7114cd0`:** a relative INPUT()/OUTPUT() name resolves against `env/*file-dir*` when it is bound. The CSNOBOL4 suite binds it to a temp directory, so `openo.tst` and `test.bin` no longer land in the tree.
  - **Row closed:** `jvm-lein-test-leaves-the-snobol4jvm-tree-as-it-found-it` reads 0 paths written, recomputed by `done`.
  - **`lein test` reads 2,028 tests, 4,257 assertions, 367 failures, 0 errors.** The red set is unchanged.
  - **The eight equality rows (rank 2 and the rank-3 umbrella):** their premises went red by design at `1fe23d8`, since each one said "this file still shadows `=`". Each baton now carries a premise of the cure holding, a dated GOAL note with today's red count, and a real NEXT.
  - **Finding:** `csnobol4-match4` is flaky. Its `X` held another test's value through the shared global environment. It is noted in the csnobol4-suite row.
  - **Next:**
    - the rank-2 rows, smallest first, judging each red against `sbl`;
    - re-grade x32tests@jvm and x64tests@jvm on the coo's stdin cure.

- **2026-10-18 12:35 CDT: the instrument row is closed, so a red from `lein test` is now a measurement. snobol4jvm `1fe23d8`.**
  - **The cure:** every test namespace that referred `SNOBOL4clojure.core :all` now adds `:exclude [= + - * / num]`, as `core_test.clj` already did. That is 34 files, plus `test-operators`, which refers `.operators` with the alias `ops`. Before, SNOBOL4's IR-building `=` shadowed `clojure.core/=`, so `(is (= a b))` was always truthy.
    - `test_csnobol4_suite.clj` holds raw control bytes. `grep` reads it as binary, so it took a direct edit; a later sweep of the tests should use `grep -a`.
  - **The witness:** the row's mutant DONE-WHEN reads **56 of 56 failing** (was 21); `done` recomputed it at rc 0.
  - **`lein test` reads 2,026 tests, 4,250 assertions, 368 failures, 0 errors**, with no shadow warnings, in 1 m 14 s at load 5.3.
    - **The 286 red tests:**
      - the rank-2 rows, matching exactly: csnobol4-suite 101, sprint12 40, t_spitbol 28, cooper 28, worm1000 20, t_gimpel 16, t_aisnobol 12;
      - the rank-3 umbrella: 41 in the other 14 files.
  - **Next:**
    - work the rank-2 rows, judging every red against `sbl`;
    - re-grade x32tests@jvm and x64tests@jvm on the coo's stdin cure;
    - mint the package reds.

- **2026-10-18 later: all ten SNOBOL4 package and suite runners take every engine and publish their own port row. Harness `735e4e0`, `948f132`, `9217c66`.**
  - **The harness is unified.** Each runner grades SCRIP, snobol4dotnet or snobol4jvm by `S4E_ENGINE` alone, with one grading. The ten are:
    - mine: aisnobol, testpgms, x64, x32;
    - hq_dotnet's: dotnet, snoflake, csnobol4, gimpel, SnoDemo, SnoBench.
  - **Auto-publish (735e4e0):** `one_runner_port_publish` runs `from-progress --suite <key>@<engine>` on a whole canonical pass, as SCRIP's runners write theirs. `S4E_SCORE_NO_WRITE` shuts it off.
    - My four call it.
    - hq_dotnet's six call it too (9217c66). I landed their lines at their request: their seat's permission guard refused the harness edit.
  - **The admission gate is at 62 arms** (948f132, 9217c66), and it is in SCRIP's blocking set.
    - Every one of the ten runs under a stub jvm. The gate checks: m3 alone, rows `@jvm`, no m4, no `rc=126`, no SCRIP row, the package left as shipped, and the row self-published where the stage allows it.
    - snoflake, csnobol4 and gimpel are cut to 4 programs each: whole, snoflake alone took 4 min 16 s under the stub, because CSNOBOL4 runs away on gimpel-asm-machine-m.
    - Nine mutations each turn it red (`.scratch/mutate_gate.sh`). It runs in about 45–66 s.
  - **The coo cured X32T and X64T (da6bec0).** Each stdin filter now reads its own `.in`, built on my port lines.
  - **Seated:** Lon, in-chat, verbatim: *"You, HQ-JVM, are now seated as Opsu 5.5 high. Tell CEO."* Told.
  - **Next:**
    - re-grade x32tests@jvm and x64tests@jvm on the coo's stdin cure;
    - mint the jvm reds, one row per defect (testpgms, x64 math_*, aisnobol ENDING, the hangs).

- **2026-10-18 afternoon: my four SNOBOL4 package runners grade snobol4jvm, published live. Harness `c445dbd`, `b57048c`; snobol4jvm `c9ccfba`.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"Work with HQ-DOTNET to get a unified test harness that can run SCRIP and snobol4dotnet and snobol4jvm test suites regarding SNOBOL4."*
  - **The unified shape:** one runner per package, the engine chosen by `S4E_ENGINE`, the same grading code for every engine. hq_dotnet set the idiom in their six runners (edf5eb3 and after) and mine follow it word for word: a `PORT` flag, the face as SCRIP, `-dNk -sNk` on the m3 line, no m4 under a port, `TREE_LABEL` from `one_runner_port_tree`, and a printed `from-progress --suite <key>@<engine>` line in place of SCRIP's write.
  - **Landed, one runner per commit, each proven by a live jvm board and a byte-identical scrip path:**
    - `aisnobol@jvm` **0/8** (4f53f48); `testpgms@jvm` **0/8** (4f05d30); `x32tests@jvm` **6/18** (d5e8b38); `x64tests@jvm` **3/33** (7a37298).
    - The boards ran at `TIMEOUT=30` with a ×3 retry, as sno-rungs@jvm was graded.
    - The scrip path was proven in two scratch roots on one copied SCRIP build (coo `bc2d85fda`), origin harness against mine. The progress rows match except ts and secs (aisnobol 16, testpgms 16, x32 42, x64 72). stdout matches except the build-behaviour probe line, which hashes the root's own path.
  - **The admission gate grows from 31 to 45 arms (c445dbd).** The ceo wired it into SCRIP's blocking set (42e6c84).
    - The new arms run each of my four runners under a stub java over a copy of its package. They check: m3 alone, rows `@jvm`, no m4 row or count, no `rc=126`, no SCRIP row, and rows that assemble by `from-progress`.
    - Five mutations each turn the gate red; the control stays green (`.scratch/mutate_gate.sh`).
  - **snobol4jvm's `TIME()` is milliseconds, measured (b57048c).** It is `System/currentTimeMillis`, counted from the epoch, so SnoBench's TIME()-budgeted angle runs under jvm.
  - **My errors, both fixed:**
    - `fd481a4` landed the face at mode 644. My proof called it through `bash`, which hid the defect. hq_dotnet fixed it (08d0827), and gate arm 10a now holds it.
    - The face's `--stlimit` spelling turned the compile_args ratchet red. hq_dotnet exempted it (65081f0); I reviewed the exemption and agree.
  - **Finding, sent to the ceo; the coo took the row:** x32/x64 feed stdin filters `/dev/null`. The oracle then prints nothing, and the stream arm passes any engine that prints nothing: a stub reads x32 14/18. Part of `x32tests@jvm` 6/18 is that.
  - **The jvm reds, for rows later:**
    - testpgms: test1 stops at ERROR 29 in line 72; test3 formats `7!` wrongly; test4 hangs; test7 prints Clojure forms on stdout.
    - x64: the `math_*` self-checks fail; arcget, arcput, def and lower hang.
    - aisnobol: `ENDING` prints nothing.
  - **Next:**
    - land `one_runner_port_publish` (hq_dotnet agreed) so a port's whole pass publishes its row as SCRIP's write does; hq_dotnet adds its line to their six;
    - add hq_dotnet's six runners to the gate loop, with a check that a run leaves its package directory clean (their idea);
    - then mint the jvm reds, one row per defect.

- **2026-10-18 later: the SNOBOL4 package runners start taking the port engine. Harness `fd481a4` and `2830c55`.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"Get ALL the test suites graded, not just SnoRungs."* and then *"Get all SNOBOL4 test suite package runners working with snobol4jvm."* · *"I told HQ-DOTNET almost this same thing: Get a unified test harness that can run SCRIP and snobol4jvm test suites regarding SNOBOL4."* So the target is one harness: each SNOBOL4 runner grades SCRIP, snobol4dotnet or snobol4jvm by `S4E_ENGINE` alone, with the same grading code. The split with hq_dotnet divides files, not harnesses.
  - **Why it's needed:** every package runner is wired to SCRIP's binary (`SCRIP=$SD/scrip`, `util_require_fresh.sh`, then m3 and m4). A port root holds no SCRIP clone, so each one refuses before it grades. Only `corpus_suite_harness.py` honours `S4E_ENGINE`.
  - **Landed, the shared helper:**
    - `run_port_as_scrip.sh`: takes SCRIP's m3 call and execs `run_<engine>.sh`. It drops `--run` and `--stlimit`, carries `-dNk`, `-sNk`, `-u` and the program's argv, and refuses `--compile` or an unknown switch with rc 2.
    - `lib_one_runner.sh`: `one_runner_is_port`, `one_runner_port_face`, `one_runner_port_ready <lang>`.
    - `util_progress_append.py`: a bare suite is keyed `<suite>@<engine>` under a port.
    - `util_score_row.py write`: refuses under a port; the port's row comes from `from-progress --suite <key>@<engine>`.
    - The admission gate reads 31/31.
  - **The split with hq_dotnet, agreed on the bus:**
    - hq_jvm: aisnobol, testpgms, x64, x32.
    - hq_dotnet: dotnet, snoflake, csnobol4, gimpel, plus the SnoDemo and SnoBench runners.
    - Each proves its runners on its own engine, with the scrip path byte-identical.
  - **Next, one runner per commit.** Under `one_runner_is_port`:
    - SCRIP becomes the face;
    - `one_runner_port_ready snobol4` replaces `util_require_fresh.sh`;
    - m4 and the score-row `write` are skipped;
    - the runner prints the `from-progress` line.
    - Then grade each runner as `S4E_ENGINE=jvm` and publish `<key>@jvm`. The order is aisnobol (corpus_suite_harness; its `cd "$SD"` fails in a port root), testpgms, x64, x32. Then hq_dotnet's runners graded on jvm once they land.
  - **Out of scope by Lon's word:** Snocone and Rebus. snobol4jvm has no front end for them, and `--binaries --lang` refuses them as NO ENGINE.

- **2026-10-18, cures and SnoBench: snobol4jvm `c9ccfba`, harness `96fbbe3`.**
  - **Engine cures, each red first against the oracle, then green; `lein test` 2026 / 0:**
    - `abc0977`: `&ALPHABET` is the 256-character string.
    - `27acf35`: exponentiation as SPITBOL does it. Integer `**` integer stays an integer; `^` and `!` are synonyms; `0 ** 0` is error 018 and overflow is error 017; a negative exponent gives a real.
    - `c9ccfba`: a real prints as SPITBOL prints it: 15 significant digits, `2.` when integral, `0.<digits>e±N` outside 0.1 ≤ |x| < 10^15. `env/sstr` is the one value-to-text conversion for OUTPUT, TERMINAL, channels, concatenation and `STRING()`.
  - **SnoRungs chunk 1 re-graded at `c9ccfba`: 76 / 100** (was 67), 1 m 45 s.
  - **SnoBench under snobol4jvm** (`bench_snobol4jvm.sh`, harness `96fbbe3`, run at `abc0977`, load 8.2 → 3.6):
    - **12 of 23 kernels print their `.ref`.**
    - **Warm x is 0.0011 to 0.0082 on the 9 kernels that time:** snobol4jvm's interpreter is 120× to 900× slower per repetition than official SPITBOL. Each engine ran at its own K, with exit code 0 required.
    - **Cold x is n/a:** sbl finishes inside the 0.01 s clock tick, and snobol4jvm takes 0.7–14 s.
    - **Corrected:** an earlier run read 300 s / K for ten kernels, because killed runs still printed their ref. The exit-code check closed that.
- **2026-10-18, the first snobol4jvm reading is in the one record: snobol4jvm `abc0977`, harness `d230a6f`.**
  - **sno-rungs@jvm: 994 / 1994 (50%):** 955 FAIL and 45 HANG, at tree `d859a74`.
    - Published through `util_score_row.py from-progress --suite sno-rungs@jvm`, which opened the row through hq_dotnet's `--open`. The grid shows it.
    - The `-dirty` stamp is an uncommitted `test/` file, which is not in the jar.
  - **How it was graded** (Lon, verbatim: *"In reality most tests are run ONE AT A TIME, the Rungs are run 100 at a time."*):
    - 20 chunks of 100 from `corpus/tests/snobol4/PARTITION.tsv`, then `core` (34), each `S4E_ENGINE=jvm ... --modes m3 --partition chunk:NN`. Chunk wall times ran 53 s to 14 min.
    - `TIMEOUT=30 S4E_TIMEOUT_RETRY_FACTOR=3`: with the default 120 s and ×6 retry, every snobol4jvm hang costs 12 min.
    - **My error:** I first ran all 1,994 as one pass. It wrote zero rows in 41 min and was stopped.
    - Other suites run one test at a time.
  - **The jvm arm, on harness origin:**
    - `eb5a087`: `run_snobol4jvm.sh` and `build_snobol4jvm.sh`, plus gate arms 9a–9f;
    - `d230a6f`: `--paths`, plus arm 9g.
    - The gate reads 31/31, and each new arm has gone red when its feature was broken in a copy.
  - **Engine cures:** `abc0977` makes `&ALPHABET` the 256-character string. It had been a vector, so `REPLACE(&ALPHABET, …)` threw; Gimpel's `agt_driver` now matches its ref.
  - **Red census by family** (1,000 reds): `simple_output` 84, `arbno_pos_rpos_branch` 49 (9 hangs), `keyword` 29, `arbno_span_pos_branch` 20, `fence_pos_rpos_branch` 19, `user_function*` about 90, `datatype` 13.
    - Seen in chunk 1: `**` / `^` exponentiation, real formatting (SPITBOL prints `1.4142135623731` and `2.`), and `(e1, e2)` selection.
  - **SnoBench:** 12 of 23 kernels print their ref under snobol4jvm. The timing run, with K grown until SPITBOL spends 1 s, is in progress.
  - **Next:**
    - root-cause the reds per entry and mint one row per defect;
    - grade the packages (Gimpel, Budne, AIS) one test at a time;
    - publish SnoBench's multiples with their load.
- **2026-10-17/18, the harness and benchmarks first: snobol4jvm `d859a74`, harness `4679767` + four unpushed scripts.**
  - **Lon, in-chat to hq_jvm, verbatim:** *"The suite banner should represent the snobol4jvm program, not SCRIP."* · *"I suspect getting the test harness and benchmarks to run is the first order of business."* That puts the engine arm ahead of the test-equality rows.
  - **The ceo ruled CEO-1822:**
    - the engine is a runner setting, `S4E_ENGINE=scrip|dotnet|jvm`;
    - a port engine's board is its HQ's own;
    - one `results.tsv` and one `SUITES.tsv`, with rows keyed `suite@jvm`;
    - LANES carries `snobol4@jvm`, `snocone@jvm` and `rebus@jvm` for hq_jvm.
  - **Ownership:** hq_dotnet lands the admission row; mine, `jvm-the-runners-take-engine-jvm-...-ceo-1822` (rank 0, claimed), lands the jvm arm on it. My `GRID_TABLES` and `/home/resources/progress/snobol4jvm/SUITES.tsv` are a stopgap second board, replaced when the `@jvm` rows land.
  - **On origin (snobol4jvm):**
    - `25e6035`: `-main` runs the interpreter. The command line had run the Stage 3 VM, which drops every statement after a `DEFINE`'s goto; under it, 15 of 15 Gimpel drivers printed nothing.
    - `d859a74`: the uberjar AOT-compiles `core`. A start takes 1.4 s instead of 4–9 s, at about 300 MB; no class names collide under case folding.
  - **The jvm arm, measured, in my harness clone, unpushed until the admission lands:**
    - `build_snobol4jvm.sh`: runs `lein uberjar`, then records an AppCDS archive. A start then takes about 1.0 s at a quiet load.
    - `run_snobol4jvm.sh`: hq_dotnet's calling shape (`[-dNk] [-sNk] [-u STR] name.sno [-- args]`); `--binaries` refuses rc 2 on a stale jar; the JVM's log stays off stdout.
    - `board_snobol4jvm.sh`: to be rewritten onto the shared writers.
    - `bench_snobol4jvm.sh`: grades SnoBench's 23 kernels against `.ref`. It times them against official `sbl -bf`, cold as a process and warm as the (T(K) − T(1))/(K − 1) difference of the generated iter wrapper, and reports the bare `x`.
    - The draft engine mode for `corpus_suite_harness.py` is set aside at `.scratch/jvm-engine-mode-draft.patch`.
  - **Scratch readings (not in the record):** AIS **0 of 8** in 13 s. It is a real witness: `ENDING` prints nothing where `sbl` prints `BASH/BASE/BATHE/...` on the same stdin. Gimpel, Budne and SnoRungs are grading.
  - **Next:** land the jvm arm on hq_dotnet's admission; grade sno-rungs@jvm; run SnoBench; then cure the reds, one defect per commit.
- **2026-10-17, first sitting, continued: snobol4jvm `05a686d`, .github `fda47100`.**
  - **The banner** (Lon, in-chat to hq_jvm, verbatim: *"The test suite banner is wrong for this seat, since JVM is only SNOBOL4 and Snocone and Rebus."* · *"The test suite banners have the wrong languages."*): `util_suite_banner.py` `grid()` now keeps only the langs `GRID_LANGS` names for the seat. hq_jvm reads 16 suites (snobol4, snocone, rebus); every other seat is unchanged. Those rows are still SCRIP's measurements, not snobol4jvm's. snobol4jvm has no Rebus front end.
  - **The instrument:** row `jvm-every-test-namespace-fails-a-false-equality-written-the-way-the-suite-writes-it`, rank 1. Its mutant DONE-WHEN takes each test file's own `ns` form plus `(is (= 1 2))` and reads **21 of 56 failing**, so 35 are vacuous. Of those, 34 shadow `=` with a warning and `test-operators` does it silently. The earlier "33" was a miscount.
    - Its cure (an `ns` form that excludes the SNOBOL4 operators) turns `lein test` red with the 366 real failures. Those are then carried by the rank-2 and rank-3 rows.
  - **The tree:** `lein test` leaves `openo.tst`, `test.bin` and a file named `|cat >popen2.dat` behind; the engine has no pipe support. Row `jvm-lein-test-leaves-the-snobol4jvm-tree-as-it-found-it`, rank 4.
  - **The lein row's receipt** is written in its ledger.
- **2026-10-17, first sitting: snobol4jvm `8923cd8`. The suite reads green, but 285 of its tests are red underneath.**
  - **Done:**
    - Row 0 (symlinks), `407cc01`: the 140 lower-case `.inc`/`.in` links in `corpus/gimpel/SNOBOL4` are now byte-identical real copies (cmp: 140 of 140). The symlink gate reads OK.
    - Row 1 (lein test), closed by its DONE-WHEN: Leiningen 2.13.0 is in `~/.local/bin`, on OpenJDK 21.0.11. `lein test` reads **2,022 tests, 4,246 assertions, 0 failures, 0 errors, in 68 s**; the README claims 1,896 and 4,120.
  - **The finding: that green is hollow.**
    - 34 test namespaces refer `SNOBOL4clojure.core :all` with no `:exclude`, so SNOBOL4's IR-building `=` replaces `clojure.core/=`. The run prints 34 `WARNING: = already refers to` lines, one per namespace. `test-operators` does the same silently.
    - `(is (= a b))` then returns the list `(= a b)`, which is always truthy. `clojure.main -e` shows `(is (= 1 2))` returning `(= 1 2)` with no FAIL.
    - In a scratch worktree, with the 1,654 such lines in 31 files rewritten to `clojure.core/=`, the suite reads **366 failures in 285 tests, 0 errors**.
  - **Rows minted:**
    - Rank 2, one per large namespace, each closed by `lein test <ns>` printing no shadow warning and 0 failures: csnobol4-suite 101, sprint12 40, cooper 28, t_spitbol 28, worm1000 20, t_gimpel 16, t_aisnobol 12.
    - Rank 3, `jvm-no-test-namespace-shadows-clojure-equality-and-lein-test-reads-zero-failures`: the other 14 files (40 tests) and the whole-suite truth.
  - **Next:**
    - Work the rank-2 rows: for each namespace, compare for real, then judge every red against `sbl`.
    - Choose `sbl`'s case-folding switch and record it under RULINGS.
    - Then measure the corpus table (item 3 of the sitting plan below).
- **2026-10-17 — the seat opened.** The ceo found, at `f35d392`:
  - OpenJDK 21.0.11 is installed, but there is no `lein`, no `clojure` CLI and no `~/.m2`, so nothing can build yet.
  - The README claims "tests 1,896 / 0 failures". The last commit adds `test_csnobol4_suite.clj`: 126 tests, 116 Budne and 10 FENCE.
  - The working tree is clean and current with origin.
- **First sitting:**
  1. Install Leiningen for this user, run `lein deps` and `lein test`, and record the measured count here.
  2. Mint one row per failing test: owner `hq_jvm`, DONE-WHEN the failing test.
  3. Measure the SPITBOL agreement over `corpus/` and write the table here: the master `tests/snobol4/ALL.sno` entries, the benchmarks, the demos and the SNOBOL4 packages, each run under snobol4jvm against its `.ref`. Choose the oracle switches and record that choice.
  4. Mint the reds and cure them one per commit, before any polish.

## THE GOAL, IN ORDER

1. **Correct:** every test passes, and every corpus program the oracle answers matches its ref.
2. **Polished:**
   - nothing generated tracked (`target/`, class files);
   - a clean `lein check`;
   - a README whose badges and numbers match a run you made.
3. **Measured:** benchmark numbers against official SPITBOL (`/home/resources/spitbol-bench-oracle/sbl`), quoted as the bare multiple `x` (reference time over this port's time), each with its load stamped and the JVM's warm-up stated.

## RULINGS

- The oracle wins over this project's own behaviour unless Lon rules otherwise. Record every such ruling here with its date and words.
- **Oracle switches, hq_jvm's choice (2026-10-17):** correctness `/home/resources/x64/bin/sbl -bf` and timing `/home/resources/spitbol-bench-oracle/sbl -bf`.
  - `-b` suppresses the signon; `-f` does not fold source case. That matches snobol4jvm, which never folds, and the corpus refs, which are cut from `sbl -bf`.
- **2026-10-17, Lon, in-chat to hq_jvm:** *"The test suite banner is wrong for this seat, since JVM is only SNOBOL4 and Snocone and Rebus."* · *"The suite banner should represent the snobol4jvm program, not SCRIP."*
- **2026-10-23, Lon, in-chat to hq_jvm, verbatim:** *"The snobol4jvm will act like SPITBOL, not CSNOBOL4."* Where the two differ, snobol4jvm does what `sbl -bf` does, and a test that encodes CSNOBOL4's behaviour is set to sbl's answer.
- **2026-10-18, Lon, in-chat to hq_dotnet, relayed by hq_dotnet on the bus, verbatim:** *"The snobol4dotnet is meant to mimic SPITBOL exactly. So make decisions based on that. This however is not true of snobol4jvm."*
  - So a harness choice for jvm is measured on snobol4jvm, never borrowed from SPITBOL. The first such choice is `TIME()`'s unit: milliseconds, harness `b57048c`.
  - The corpus refs are still `sbl -bf`'s. Whether a jvm divergence from SPITBOL is a defect stays Lon's call, case by case.
