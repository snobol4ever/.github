# ARCH-PASCAL-PROLOG-PROGRAM-SOURCES — the Pascal and Prolog programs downloaded for demos and suites: what they are, what the oracles say, what SCRIP lacks

**Opened 2026-10-09 18:1x CDT by the coo on Lon's word, in-chat to the coo, verbatim:** *"Let's look at the new Pascal and Prolog code recently downloaded to make demos and test suite drivers."* · *"Let's do get rosetta, tex, and standardpascaline."* · *"Oh also tangle too"* · *"Let's get rosseta for both Pascal and Prolog on the official test suite banner. Graded against the oracle."* · *"Put into some ARCH\*.md document the information gathered from your search of Pascal and Prolog programs."*

Every number on this page was measured on 2026-10-09 by the coo on this box. Oracles: `/usr/bin/fpc -Miso` (through `SCRIP/scripts/fpc_oracle_run.sh`) and `/usr/bin/swipl -q`. SCRIP: `48d8bd2ee`–`2e2067ff4`, `-O0`. The survey tables are diagnostics: no rows, no progress appends.

## 1. Where the downloads live

`/home/resources/pascal-demos/` (9 sets) and `/home/resources/prolog-demos/` (11 sets), shared, read-only for every seat. Nothing there is graded until it is vendored into `corpus/` with oracle-cut refs.

### Pascal — `fpc -Miso` compile of every file, as shipped

| set | what it is | license | files | compiles under `fpc -Miso` | note |
|---|---|---|---|---|---|
| `standardpascaline` | Scott Franco's ISO 7185 source page (standardpascaline.org/source.html): Basic-S, Pascal-S (+ `pascals.ins`, Wirth's paper), the PL/0 compiler, a prettyprinter, Star Trek, Chess05 | per the site's rights page | 6 programs | **5 of 6** | Chess05 is CDC 6000 Pascal: see § 3 |
| `rosetta` | RosettaCodeData (acmeism), commit `1d475861d`, every Pascal solution | GFDL 1.2 | 664 | 297 (256 tasks) | 209 files carry a `{$mode}` directive: see § 4.2 |
| `wirth1976` | bonthron/wirth1976: four sorts from *Algorithms + Data Structures = Programs* | none | 5 | 5 | ⚠ all five carry `{$mode objfpc}`, so the compile proves nothing about ISO; hq_pascal's row transcribes the book to ISO 7185 |
| `tex` | Knuth's `tex.web` and `tangle.web` | Knuth's terms | 2 WEB | — | tangled 2026-10-09 by `/usr/bin/tangle`: `tex.p` (6122 lines) + `tex.pool` (1045 strings), `tangle.p` (801 lines), no errors. `fpc -Miso` refuses both (`tex.p`: "readln/writeln on typed file"; `tangle.p`: string constant to char) — a WEB program needs a change file for its system-dependent parts |
| `advpas350` | Barry Breen's *Adventures in Pascal* (Colossal Cave, 350 points), ports for FPC, TP3, TP5.5, PASTA/80 and the OMSI original | none | 216 | 2 | multi-file, `{$MODE TP}`; ships `tests/walkthrough.txt` + `expected.txt`, a ready whole-program test once a port is ISO |
| `tply` | TP Lex and Yacc | COPYING | 21 (18 units) | 1 | Turbo/Object Pascal |
| `cocor_pascal` | Pat Terry's Coco/R Pascal kits | none | 19 (16 units) | 0 | Turbo units |
| `pascal-lisp` | a small Scheme-like Lisp in Delphi Pascal | COPYING | 8 (2 units) | 0 | Delphi |
| `DSA` | data-structures exercises | none | 1 + 10 `.lpr` | 0 | Lazarus projects |

### Prolog — `swipl` load of every file, as shipped (`--on-error=status`, stdin `/dev/null`, 15 s)

| set | files | load clean | with warnings | errors | timeouts | note |
|---|---|---|---|---|---|---|
| `rosetta` (Prolog half of the Rosetta clone) | 786 | 557 | 22 | 205 | 2 | 442 tasks load; 38 use `clpfd`; `Chat-server` starts a server and ignores TERM |
| `hakank/swi_prolog` | 260 | 256 | 4 | 0 | 0 | 257 define `go/0` — but **251 load `library(clpfd)`** |
| `hakank/sicstus` | 199 | 21 | 2 | 176 | 0 | SICStus syntax |
| `bratko_4th_edition` | 103 | 40 | 46 | 17 | 0 | Bratko's book programs; no entry points |
| `PRESS` | 120 | 47 | 9 | 64 | 0 | the equation solver |
| `PrologPuzzles` | 28 | 15 | 11 | 2 | 0 | |
| `chat80` | 24 | 10 | 14 | 0 | 0 | the CHAT-80 NL system |
| `provers` | 19 | 8 | 6 | 5 | 0 | leanCoP, nanoCoP, leanTAP (CEO-1583's demo row) |
| `pl2wam` | 17 | 10 | 1 | 6 | 0 | GNU Prolog's compiler (hq_prolog landed it as a ProDemo entry, corpus `e0e6512d0`) |
| `99-prolog-problems` | 7 | 7 | 0 | 0 | 0 | no entry points |
| `advent-of-code-prolog` | 8 | 8 | 0 | 0 | 0 | no entry points |
| `clpfd` | 8 | 8 | 0 | 0 | 0 | |
| `eliza` | 1 | 1 | 0 | 0 | 0 | |

**CLP(FD)** is Constraint Logic Programming over Finite Domains (`library(clpfd)` in SWI, the built-in FD solver in GNU Prolog): variables range over finite integer sets, constraints (`#=`, `all_different/1`) prune them, `label/1` searches. SCRIP's Prolog has no FD solver; Lon deferred the class (*"Do not count the FD as failures for us."*, CEO-579). hakank's SWI set is therefore blocked on the solver, not on drivers.

## 2. The three sets fetched on 2026-10-09 (Lon: *"Let's do get rosetta, tex, and standardpascaline."*)

- **rosetta** was a blobless (`--filter=blob:none`) sparse clone holding only `Lang/Pascal`, `Lang/Free-Pascal`, `Lang/Prolog` — and in RosettaCodeData every `Lang/<L>/<task>` entry is a **symlink into `Task/<task>/<L>/`**, which was not checked out, so every link dangled and the set held zero sources. Cure: `git sparse-checkout set --no-cone '/Lang/{Pascal,Free-Pascal,Prolog}/' '/Task/*/{Pascal,Free-Pascal,Prolog}/'` → Pascal 523 tasks / 664 files, Prolog 511 tasks / 786 files (Free Pascal is `Lang/Free-Pascal-Lazarus` in that repo, not taken).
- **tex**: both WEB files tangled in place (above); the tangle logs sit beside them.
- **standardpascaline**: the first download saved a 406 page — the site's mod_security refuses a bare `curl`/`wget`; with a browser user agent `source.html` and every program it links came down. `links.txt` records each URL; `chess05ISO.pas` (the site's ISO version of Chess05) answers 404, a dead link; `pascals.exe` (a DOS binary) and the external USUS archive were not taken.

## 3. Chess05 is not a one-character fix

It is CDC 6000 Pascal: every string and character literal uses `"` (393 sites) where ISO uses `'`, and its character set is CDC display code — `AC = "A"; ZC = ","` and `SC = SET OF AC..ZC` span the whole printable set in CDC order and are an empty range in ASCII. Swapping the quotes (escaping the 9 apostrophes inside strings) and remapping the range to `' '..'Z'` makes it compile under `fpc -Miso`, but it prints its greeting and dies at the first `GO` with runtime error 207 (invalid floating-point operation): its comments say parts of it need CDC's `EXPO` and `CARD` on 60-bit words, and some character comparisons assume CDC order (`ORD(c) >= ORD('+')` meant "punctuation" in CDC and is true for letters in ASCII). A porting job; or recover the site's own `chess05ISO.pas` from an archive.

## 4. The Rosetta suites — PasRosetta and ProRosetta (Lon: *"... on the official test suite banner. Graded against the oracle."*)

**Packages** (corpus `df56f1058` and after): `packages/pascal/rosetta-pascal` (664 `.pas`) and `packages/prolog/rosetta-prolog` (786 `.pl`, renamed from `.pro`), one file per Rosetta solution, names sanitized to `[A-Za-z0-9._-]`; `TASKS.tsv` maps each to its task, `README.md` names source and license. **Runners**: `test_pascal_rosetta_suite.sh`, `test_prolog_rosetta_suite.sh`, both thin over `lib_container_package_runner.sh` (grade the container through `corpus_suite_harness.py run`, print the board and the inventory, write the row through `util_score_row.py`, the AND per program). Rows `rosetta-pascal` (PasRosetta) and `rosetta-prolog` (ProRosetta) in the suite table.

**Building the containers** (`util_build_package_suite.py --twice`, every ref cut from the oracle). Three builder rules came out of this package, each measured on it:
1. `--twice` — the oracle runs twice in fresh directories; a program whose two answers differ is excluded (Rosetta prints times, random draws, addresses: 42 Pascal, 3 Prolog).
2. a program whose oracle output carries a carriage return is excluded (`gapful-numbers-1`, `ludic-numbers-2`, `two-sum` redraw a progress line with `#13`: the ref broke OUR FILES ARE LF — `test_gate_our_files_are_lf.sh` read origin red at corpus `df56f1058` for about fifteen minutes — and the harness reader splits a line on CR, so the container fell out of step).
3. ~~a Pascal source whose own `{$mode …}` overrides `-Miso` is excluded~~ — **REVERSED the same evening on Lon's word** (*"I suspect you should ignore the compiler directives suggesting and hinting at the dialect. Let's get all those rosetta programs working if they run and give reasonable results, REF file, from the oracle."*): the builder rule is withdrawn (it lived only in SCRIP `2e2067ff4`) and the package declares `CONTRACT.tsv dialect=any-fpc-mode` — fpc compiles each program under `-Miso`, then its default mode (which honours the source's own `{$mode}`), then `objfpc`, `delphi` and `tp`; the first mode that compiles cuts the ref and `ALL.dialect` names it per entry. A program no mode compiles is `ORACLE_REFUSES`.

**Prolog drivers** (CEO-700: a library is graded through a driver written for it): a Rosetta Prolog solution usually defines its predicates and never calls them, so under `swipl -q` it prints nothing (742 of 786 on the first build). The 120 that define a zero-arity entry (`main` 71, `test` 25, `go` 12, `run` 4, `task` 3, `example` 3, `start` 2) and no `initialization` directive carry one appended line, `:- initialization(<entry>).`, named in `DRIVERS.tsv`; the build went from 40 graded to 118. The other 458 printing nothing need a driver written for them (`NEEDS_DRIVER`).

### 4.1 Readings (the coo seat, both modes, the AND per program; the denominator is shipped by CEO-1286)

| row | reading | tree | shipped | graded | pass both modes | owed (`UNGRADED.tsv`) | no one ground truth (`UNGRADABLE.tsv`) |
|---|---|---|---|---|---|---|---|
| PasRosetta | **30/664** | SCRIP `d4fa381f8` / corpus `bd7d3aea8` | 664 | 319 (fpc modes: iso 203, default 92, objfpc 23, delphi 1 — `ALL.dialect`) | 30 | NEEDS_DRIVER 42, TIMEOUT 34, NEEDS_RUNNER_WIRING 10 | ORACLE_REFUSES 205 (no fpc mode compiles them), NONDETERMINISTIC 54 |
| ProRosetta | **36/786** | SCRIP `d4fa381f8` / corpus `bd7d3aea8` | 786 | 118 | 36 | NEEDS_DRIVER 458, TIMEOUT 7 | ORACLE_REFUSES 200 (swipl load error), NONDETERMINISTIC 3 |

Earlier readings the same evening, superseded: PasRosetta 29/664 (203 graded, `-Miso` only) and 28/664 (101 graded, the withdrawn `$mode` exclusion). `test_gate_score_row_denominator_includes_xfails.sh` reads AGREE on both rows since the runner appends one UNGRADED progress row per mode for every shipped program the container does not grade (SCRIP `df8e75e8f`).

### 4.2 `fpc -Miso` is not an ISO 7185 checker (the measurement behind rule 3, kept as history; Lon ruled the directives ignored)

- **A `{$mode}` directive in the source wins over the command line.** 102 of the first build's 203 graded Rosetta programs carried `{$mode delphi}` (58) or `{$mode objfpc}` (44), so fpc cut their refs as Delphi or Object Pascal; they left the container (rule 3). **The same is true of `corpus/packages/pascal/fpc_tests`: 59 of its files carry a non-ISO `{$mode}`** (and 2 benchmark sources) — the FPC suite's refs for those were not cut in ISO mode. Reported to hq_pascal and the ceo; not changed here (the shared `fpc_oracle_run.sh` and the FPC suite are hq_pascal's lane).
- **Even without a directive, `-Miso` accepts what ISO 7185 does not.** Of the 101 programs graded after rule 3, SCRIP's ISO front end refuses 53 at parse, on `//` comments (13), open `array of T` parameters and types, `LongInt`, and constant expressions in subrange bounds (`0 .. max_points - 1`) — none of them ISO 7185, all accepted by fpc in ISO mode. Correction: the corpus commit `7a865a2fe` says the 102 accounted for "118 of SCRIP's 154 parse refusals"; that figure was the sum of three categories, not a measurement — the measured split is the paragraph above.
- **A strict checker exists in corpus**: Pascal-P5 (`packages/pascal/p5`, Scott Franco's ISO 7185 compiler) accepts only ISO 7185. Running each candidate through P5 before cutting its ref would make "graded against the oracle" mean ISO for every Pascal package. ⛔ OPEN FOR LON (§ 6 b).

### 4.3 What SCRIP's Prolog lacks, measured on ProRosetta's 82 failures (first `stderr` line under `./scrip`)

`writef/2` missing (23 programs), `swritef/3` (2), `library(assoc)`'s `empty_assoc/1` (2); type errors on lists and strings (`type_error(list, …)` 6, `type_error(atom|atomic|integer|character|evaluable, …)` 9) — the SWI-7 double-quoted-string shape, where swipl reads `"abc"` as a string object and SCRIP as a code list; a parse error after a directive (2). These are hq_prolog's rows to mint from this table.

## 5. Candidates for demos and drivers

- **Ready**: the five standardpascaline programs (Basic-S, Pascal-S, PL/0, the prettyprinter, Star Trek) compile under `fpc -Miso` as shipped and carry no `{$mode}`; Pascal-S and Star Trek are named in hq_pascal's PasDemo row (CEO-1579).
- **With a port**: Adventure (`advpas350`, its walkthrough is the test), Chess05 (§ 3), TeX and TANGLE (a change file for fpc's ISO mode).
- **With drivers**: ProRosetta's 458 `NEEDS_DRIVER` solutions, PasRosetta's 27; Bratko, 99 problems, Advent of Code, PRESS and the provers define predicates with no entry point.
- **Blocked on a solver**: hakank's 251 CLP(FD) models (CEO-579 defers the class).

## 6. Open for Lon

- **(a)** Should a Rosetta program the oracle cannot grade leave the denominator as a ruled EXCLUDED class (the rows would read 28/101 Excl 563 and 36/118 Excl 668), or stay in as debt (28/664, 36/786 — published today, by CEO-1286)?
- **(b)** Should ISO-ness be checked by Pascal-P5 (strict) before a Pascal ref is cut, for Rosetta and for FPC's 59 `$mode` files — and what is a program that fpc's ISO mode runs but P5 refuses: an expected refusal (the FPC suite's CEO-1228 shape), an exclusion, or debt?

## 7. Reproduce

Survey scripts and tables: the coo's session scratchpad `survey/` (`pas1.sh`, `pl1.sh`, `*.tsv`) — the measurement method is the table headers above. Containers: `python3 SCRIP/scripts/util_build_package_suite.py corpus/packages/<lang>/rosetta-<lang> --lang <lang> --twice` (TIMEOUT=20). Readings: `bash SCRIP/scripts/test_<lang>_rosetta_suite.sh` from the coo seat.

## 8. The dialects in Rosetta Pascal, itemized, and what a mechanical conversion could do (Lon: *"Can we itemize the differences in the dialects so we might consider some mechanical conversion techniques?"*)

**Counted over all 664 `rosetta-pascal` sources** (a program counts once per construct; comments and string literals stripped before matching except for the comment and directive rows; regular expressions, so a count is approximate to a few programs). **Probed** with one tiny program per construct through `./scrip` (mode 3, SCRIP `7e3bcdb63`) and `fpc -Miso`. Only **42 of the 664** use none of the constructs below.

| construct | programs | SCRIP today | `fpc -Miso` | mechanical conversion |
|---|---|---|---|---|
| `uses` clause | 292 | ✗ parse error | ✗ (✓ under a `{$mode}`) | drop the clause and link a **prelude** that defines what the units supplied (rows below) — mechanical once the prelude exists |
| `{$…}` compiler directives | 266 | ✓ ignored | ✓ (a `{$mode}` switches dialect) | none needed |
| `//` line comments | 262 | ✗ parse error | ✓ | **trivial**: `// x` → `{ x }` (lexical) |
| integer types `longint int64 qword cardinal word byte …` | 243 | ✓ | ✓ | none needed |
| `inc` / `dec` | 245 | ✓ | ✓ | none needed |
| `string` / `AnsiString` type | 241 | ✓ | ✗ | none needed — but **SCRIP's `copy(s, 2, 3)` returns the whole string** (`'hello'`, not `'ell'`): a defect, hq_pascal's |
| string intrinsics `length copy pos delete insert concat val str` | 178 | ✓ (copy wrong, above) | ✗ | none needed once `copy` is right |
| dynamic arrays `array of T` / `SetLength` | 165 | ✗ parse error | ✓ | **hard**: a fixed array at a guessed bound plus a length variable — semi-mechanical, needs a bound per program; better a SCRIP feature |
| `Result :=` | 161 | ✓ | ✗ | none needed |
| typed constants / initialised variables `x: T = v` | 144 | ✗ parse error | ✓ | **mechanical for scalars**: a `var` plus an assignment at block entry; typed array constants need an initialiser block |
| `Low` / `High` | 143 | ✓ | ✓ | none needed |
| `exit` / `exit(v)` | 126 | ✓ | ✓ | none needed |
| no `program` header (starts `uses`/`var`/`begin`) | 125 | ✗ parse error | ✓ | **trivial**: prepend `program p(input, output);` |
| `break` / `continue` | 107 | ✗ (`error 22: undefined function called`) | ✓ | **mechanical**: a label after (break) or at the end of (continue) the innermost loop body and a `goto` — or a small SCRIP feature |
| SysUtils helpers `IntToStr StrToInt Format UpperCase Trim …` | 103 | ✗ (no unit) | ✗ (✓ under `{$mode}`) | prelude: `IntToStr`/`StrToInt`/`UpperCase`/`Trim` are short ISO functions; `Format` is not mechanical |
| `@` address-of | 98 | ✗ parse error | ✓ | **hard**: ISO has no pointer to a variable; rewrite per program |
| `#13`-style character literals, hex `$FF` | 79, 22 | ✓ | ✓ | none needed |
| `shl` / `shr` / `xor` | 54 | ✗ parse error | ✗ (✓ under `{$mode}`) | `shl n` → `* 2^n`, `shr n` → `div 2^n` for non-negative operands; `xor` → a prelude function — mechanical with care for signs, or a SCRIP feature |
| Math unit `Power Floor Ceil Log10 Max Min …` | 52 | ✗ (no unit) | ✗ | prelude |
| C-style `+= -= *= /=` | 48 | ✗ parse error | ✓ | **trivial**: `x += e` → `x := x + (e)` |
| form feed (`^L`, a page break) between declarations | (in Basic-S; old sources) | ✗ lexer: "invalid character" | ✓ | **trivial**: a form feed is a separator — or a one-line SCRIP lexer change |
| open array parameters `array of T` | 35 | ✗ parse error | ✓ | to an ISO conformant array `array[lo..hi: integer] of T` with `high(a)` → `hi` — **but SCRIP has no conformant arrays either** (probed: parse error): a SCRIP feature first |
| empty-parenthesis call `f()` | 35 | ✗ parse error | ✓ | **trivial**: drop the `()` |
| `halt` | 35 | ✓ | ✓ | none needed |
| `for … in … do` | 33 | ✗ parse error | ✓ | mechanical over a string or array: an index loop |
| exceptions `try except finally raise` | 28 | ✗ | ✓ under `{$mode}` | not mechanical |
| classes / objects | 25 | ✗ | ✓ under `{$mode}` | not mechanical |
| `case … else` (and `otherwise`) | 15 | ✗ parse error (both) | ✓ | mechanical: `if sel in [labels] then case … else …` — or a SCRIP feature |
| Crt terminal `ClrScr GotoXY ReadKey …` | 17 | ✗ | — | none: a graded run has no terminal (`NEEDS_INTERACTIVE_TTY`) |
| generics | 11 | ✗ | ✓ under `{$mode}` | not mechanical |
| `Random` / `Randomize` | 60 | ✓ | ✓ | none: the output differs run to run (`NONDETERMINISTIC` under `--twice`) |

**Reading.** Two kinds of work, and the counts say which first:
1. **Trivial textual rewrites, one pass each, no semantics**: `//` comments (262), a missing program header (125), `+=` (48), `f()` (35). A normalizer that does only these four is a few dozen lines and loses nothing.
2. **A prelude unit for what `uses` supplied** (292 programs name a unit): SysUtils' `IntToStr`/`StrToInt`/`UpperCase`/`Trim`, Math's `Power`/`Floor`/`Ceil`/`Max`/`Min`/`Log10` — short ISO functions, prepended to the program the way a driver is.
3. **Small SCRIP front-end features rather than rewrites**: `break`/`continue` (107), typed constants (144), `case … else` (15), `shl`/`shr`/`xor` (54), conformant and open arrays (35) — each is a parser and lowering change the conversion would otherwise have to fake with `goto`s and copies.
4. **Out of reach mechanically**: dynamic arrays (165), `@` (98), classes, exceptions, generics, `Format` — a program using them stays debt until SCRIP has the feature or someone ports it by hand.

**Where a converted program is graded**: the ref stays cut from the oracle on the ORIGINAL source (fpc in the program's own dialect, § 4 rule 3 as reversed); the conversion runs on SCRIP's side only, so a conversion that changes behaviour shows up as a FAIL instead of hiding in the ref.

## 9. Rosetta Code's own outputs are not refs (Lon: *"Does the rosetta web-site offer results which we can use as REF files?"*)

- **RosettaCodeData carries no outputs**: per task only `00-TASK.txt`, `00-META.yaml` and the code files.
- **The website shows an output block for about a quarter of solutions**: sampled 2026-10-09 through `index.php?title=<task>&action=raw` (a browser user agent), eight tasks (Ackermann, Towers of Hanoi, Hailstone, Sieve, Fibonacci, GCD, Anagrams, 0-1 Knapsack): Pascal sections 16 code blocks with 4 `{{out}}` blocks, Prolog 39 code blocks with 10. None for 100 doors' two Pascal solutions.
- **Not usable as refs**: produced by an unnamed compiler and version, often abbreviated or trimmed by hand, sometimes a top-level transcript (`?- knapsack` and its answer) rather than the program's stdout; a ref is cut from the ONE oracle (RULES: correctness is an oracle diff).
- **Usable two ways**: (a) a **sanity check** on our oracle-cut ref where the site shows output (Lon's "give reasonable results"); (b) for Prolog, the **query the output block shows is the driver goal** a `NEEDS_DRIVER` solution lacks (`?- knapsack.`, `?- hanoi(3).`) — a mechanical source of drivers for part of ProRosetta's 458.

## 10. The standardpascaline programs under SCRIP (PasDemo, CEO-1579), first look

All five compile under `fpc -Miso` with no `{$mode}`. **Basic-S** (stdin: a BASIC program, `list`, `run`, `bye`) runs a primes demo under fpc; under SCRIP it stops at a form feed in its source (lexer: "invalid character", line 125), and with the form feeds turned into newlines SCRIP's code generator aborts: `FATAL emit_drive: IR op=4 HAS a template and its own case REFUSED AT A GUARD -- emit.cpp:2016` (rc 134). **Star Trek** seeds its own generator (`rndseq := 1`), so it is deterministic, but the generator divides by `maxint`, which is implementation-defined — fpc and SCRIP may legitimately differ there. **Pascal-S** (`program Pascals(input, output, srcfil)`) and the **prettyprinter** (`PROGRAM PRETTYPRINT(INPUTFILE, OUTPUTFILE)`) read named files bound as program parameters — the binding convention has to be the same under fpc and SCRIP before a ref means anything. **PL/0** reads its source from stdin.
