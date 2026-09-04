# FINDING 2026-09-03 seat05: Icon IPL runner landed (851 files, zero runner before this row); compile_pass=437, linkgap=354 is a known architectural gap not cured here, parseerr=57 collapses 40:1 onto one already-documented parser limitation; one console-display bug found and fixed in util_score_row.py

**Task:** `icon-ipl-runner-and-denominator` (hq_T mint, 2026-09-03T23:29:06Z). **GOAL:** grade all 851 vendored Icon Program Library `.icn` files (compile-graded at least, run-graded where a `.std` exists), print the denominator, rewrite SCORE.md, classify the reds.

## The runner
`SCRIP/scripts/test_icon_ipl_suite.sh` (new). Every file gets `./scrip --compile FILE -o out.s` under an 8s timeout; classified by directly-observed signal, same discipline as `FINDING-2026-09-03-seat01-icon-arizona-suite-...`: group by shared signature, never force a bucket, a genuinely new shape reported by name.

```
IPL_SUITE_BOARD total=851 compile_graded=851 compile_pass=437 compile_fail=414 run_graded=0 nomain_total=391 hasmain_total=460 nomain_ok=296 linkgap=354 parseerr=57 timeout=0 other=3
```
Verified: `git status --short` clean, SCRIP `e8a7263d5` · corpus `ad523f7a4` · .github `06cdb113` · 2026-09-03 23:07 CDT. The task's literal DONE-WHEN command run end-to-end: exit 0.

**run_graded=0 is honest, not a bug**: `find $PKG -iname '*.std'` → 0 files. Unlike Arizona's `general/` (upstream-shipped `.std` per entry), IPL is upstream's *code library*, not a regression suite — it ships no reference outputs. The population is computed structurally each run, so this self-corrects the day anyone vendors references.

**Compile-graded numbers are written as bare `key=value`, never `N/851`**, in both the standardized-display cell (`util_score_row.py write --suite IPL`) and the September-10 grid (hand-edited, since `write` does not touch that table — see below). The task's own words: "Compile-graded-only entries must be COUNTED AS SUCH and never folded into a run-graded pass rate." `util_score_row.py`'s `cell_fractions()` sweeps every bare `\d+/\d+` in a cell into the ONE LEADERBOARD's automatic per-language pass-rate sum — a fraction here would silently misrepresent "compiles" as "verified correct." Same convention `test_prolog_gnu_suite.sh` already set (`lib=56`, never `56/62`).

## Classes

### `nomain_ok` — 296 of 391 no-`procedure main` files — NOT a defect, compile-graded PASS
No `procedure main`; sole failure is `[IBB] FATAL: mode-4 driver: main BB graph not found` — the expected terminal state for a library module (`procs`/`gprocs`/`incl`/`gincl` are IPL's library tree by convention: 251/140/3/5 files respectively, only 9/0/0/0 of which define `main`). ⚠️ **Self-correction kept in the open**: my first probe of this signal reused a stale `/tmp/w.s` left by an unrelated process on this shared box and concluded (wrongly) that `--compile` writes a non-trivial `.s` before this FATAL fires; a fresh output path shows it writes **nothing**. The classifier's `nomain_ok` check does not require `-s "$out"` for exactly this reason — matches `test_prolog_gnu_suite.sh`'s sibling LIB check, which also keys on the string alone.

The other 95 no-main files fail for a *different*, earlier reason (linkgap/parseerr) before ever reaching this check — by the compiler's own control flow (each failure class is a distinct hard `exit()`), a file cannot hit two classes in one run.

### `linkgap` — 354 — KNOWN, NAMED, NOT cured this row
`icon: link: cannot open X (linked from Y)`. Root cause read directly: `icon_driver.c:26-45`'s `icn_resolve_links` resolves every `link NAME` as exactly `"<dirname of the linking file>/NAME.icn"` — one directory, no search path, no `ICONPATH`/`LPATH` support anywhere in the tree (checked, zero hits, no CLI flag either — `./scrip` with no args prints the full flag list and there is none). IPL's own `progs`/`procs`/`gprocs`/`incl`/`gincl` split is upstream's **normal organization** — a `progs/format.icn` linking `procs/options.icn` is the library working as designed, not a corpus defect (confirmed: `options.icn` exists exactly where expected, in `procs/`, and `format.icn` fails on that link alone).

**Deliberately not cured**: this task is a runner+census row ("print the denominator ... classify the reds"), same scope line `test_prolog_gnu_suite.sh` (row `gnu-prolog-suite-runner-and-score`) and the Arizona vendor-suite rows already drew before landing their own runners without curing what they found. A real fix means either (a) a genuine link search-path feature in SCRIP's Icon frontend — shared-node, cross-language-adjacent, its own unit of work — or (b) vendoring/renaming cross-linked files at IPL's actual scale. The Arizona finding did (b) **by hand, for 5 colliding names**, in one file; 354 witnesses across a 6-way directory split is not a same-sitting pattern-match of that fix. Left named for whoever scopes it next.

### `parseerr` — 57 — **40 of 57 collapse onto ONE already-documented cause**
Re-swept with normalized signatures (all 57, not a sample):

| Signature | Count |
|---|---|
| `return statement: expected ; (got \|\|\|)` in `procs/io.icn`, direct or via `link` | **40** |
| `expected ..., or ... (got :)` in `procs/regexp.icn`, direct or via `link` | 2 |
| 15 further named singletons (`xtable`, `shar`, `roffcmds`, `proto`, `midisig`, `igrep`, `html`, `hetero`, `lshade`, `penelope`, `img`, `dlgvu`, `breakout`, `maccolor`, +1) | 15 |

The **40-witness cluster is not 40 independent defects** — it is every file that `link`s `procs/io.icn` (directly, or transitively through another linked file) inheriting `io.icn`'s own single parse failure: `return EXPR ||| EXPR2` — a trailing binary operator (`|||`, Icon's alternation) after a `return`-led statement, unparenthesized. **This is the identical architecture already named in `FINDING-2026-09-03-seat01-icon-arizona-suite-...`'s Session-2 addendum**: `icon_parse.c`'s `parse_expr` (~572-676) dispatches `case`/`if`/`every`/`while`/`until`/`repeat`/`create`/`suspend` as early-return branches directly in the outermost expression grammar, so none of them can feed a trailing binary operator unless parenthesized — that finding hit it via `case...of{}|||expr` in `io_lib.icn`; this row hits the same shape via `return X ||| Y` in the *original* `ipl/procs/io.icn`, meaning `return` belongs on the same affected-keyword list. Not re-minted as a new class — cross-referenced. A parser-side fix here (adding `return` to whatever the eventual cure list is) would very likely resolve most of this row's own 40-witness cluster in one motion, which is exactly why it is named precisely rather than left folded into a generic "parseerr" count.

### `other` — 3, all individually diagnosed (none left unexplained)
- **`procs/dijkstra.icn`** (rc=1, `main BB graph not found`) — **not a compiler bug**: my `has_main` detector is a plain `grep -E '^procedure main'` and does not understand Icon's `$ifdef`/`$endif` preprocessor. `dijkstra.icn`'s `procedure main(arg)` (line 190) sits inside `$ifdef TEST ... $endif` (lines 163-201, confirmed by reading the file); `TEST` is not defined by `--compile`, so upstream Icon itself would also treat this file as having no active `main` under default conditions. A false positive in the classifier's *population split* (should count toward `nomain_total`, not `hasmain_total`), not a defect in SCRIP. Not worth encoding `$ifdef`-awareness into the classifier for one witness — documented here instead.
- **`procs/iftrace.icn`** (rc=2) — genuine, already self-diagnosed SCRIP gap: `variable(vp) :=: variable(vf)` (line 66) — SCRIP's own message names it exactly: `"variable(expr) with a computed name is not an assignable variable in SCRIP yet (a literal name is)"`. A real, narrow, precisely-scoped language-feature gap (computed-name dynamic variable access under the reversible swap operator).
- **`progs/fset.icn`** (rc=134, SIGABRT / core dump) — a **genuine internal compiler crash**, distinct from every other class in this suite: `FATAL emit_drive: IR op=3 has no template in the universal driver`. Real, minted for whoever picks up codegen work next; not root-caused further this sitting (would need reading what IR op #3 is and what `fset.icn` construct reaches it — compiler-internals work, out of scope for a runner+census row).

## Side finding, cured inline: `util_score_row.py`'s `write` console output misreports a `--suite` merge
While landing the SCORE.md row, the console printed (dry-run and real-write paths both): `now: IPL runner landed: ...` — i.e. **only my new clause**, looking exactly like the Arizona/JCON clauses already in that cell had been clobbered. Verified directly against the real file before reacting: they had **not** — `merge_clause` had correctly appended the new `IPL:` clause alongside the existing ones, `cells[idx]` was correct, only the two `print("  now: %s" % text)` lines (using the raw `--text` argument instead of the merged `cells[idx]`) were wrong. This is exactly the "instrument lies about its own result" shape this project's culture treats as a first-class defect, and a one-line×2, zero-logic-risk fix, so cured inline rather than filed: `scripts/util_score_row.py` now prints `cells[idx]` in both places. Verified via `util_score_row.py selftest` (PASS, all six assertions) before and after landing.

## SCORE.md
Both tables updated: standardized display via `write --suite IPL` (Arizona/JCON clauses confirmed intact); September-10 grid's icon/V cell hand-edited (`write` does not touch that table — the known dual-write gap `test_gate_score_tables_agree.sh` exists to report). Hit a real rebase conflict landing this (a concurrent session's newer `bench_triangulate_snobol4.sh`/`bench_two_number_ir.sh snocone` citations on the adjacent rows in the same table); resolved by keeping origin's newer snobol4/snocone rows (each explicitly cites and supersedes the numbers my stale pre-rebase copies carried) and my icon row (identical to origin's except the IPL clause). Both `util_score_row.py columns` (blocking in `make test`) and `agree` (reported) verified GREEN after, 0 same-denominator conflicts, no new icon-specific staleness.

## NOT cured this sitting (named for whoever scopes next)
- `linkgap` (354): needs either a real link search-path feature (cross-language blast radius, its own ARCH-level unit) or large-scale corpus vendoring/renaming across IPL's 6-directory split.
- The `return`-before-`|||` (and sibling keyword-led-statement-before-binary-operator) parser limitation: would likely clear most of the 40-witness `io.icn` cluster in one motion. Owner: whoever holds `icon_parse.c` grammar work; cross-reference the Arizona finding's Session-2 addendum for the `case` sibling.
- 15 named `parseerr` singletons + `fset.icn`'s IR-op-3 crash: not individually root-caused, each needs its own single-file read.
- `iftrace.icn`'s `variable(expr)` computed-name gap: narrow, precisely scoped, not attempted.
