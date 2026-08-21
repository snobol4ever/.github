# FINDING s191 — THE UPPERCASER WAS REWRITING THE PROGRAMS' INPUT DATA, AND THE ACCEPT TEST WAS REVERTING CORRECT WORK OVER 24 BYTES OF MEMORY STATISTICS

**Seat8 `/home/claude8`, Claude Opus 5, 2026-08-20. Queue row `kw-uppercase-dialect` (rank 0, Lon's ruling).**
**corpus `6a795e4c` (3 conversions + 2 data repairs) · SCRIP `d1994fe3` (3 instrument fixes). No compiler file touched.**

---

## ⭐ THE ROW DID NOT GO WHERE THE BRIEF EXPECTED, AND THE INTERESTING PART IS WHY

The brief scoped this to "the csnobol4 lowercase-dialect block — 53 of 77 oracle-flag movers." Running seat1's tool over the residual set converted **zero**. The corpus was not the blocker. **Both instruments were.**

## ⛔⛔ FINDING 1 — THE UPPERCASER HAD NO `END` AWARENESS AND WAS CORRUPTING PROGRAM DATA

In SNOBOL4 everything after the `END` statement is the program's **inline input data**. `util_uppercase_keywords.py`'s `fix_text()` walked every line of the file, so it uppercased English words in that data whenever they collided with a builtin name.

`csnobol4-suite/tab.sno`'s data is the **Gettysburg Address**:

```
- or any nation so conceived and so dedicated     → + or ANY nation so conceived and so dedicated
- portion of that field, as a final resting place → + portion of that FIELD, as a final resting place
```

⛔ **AND IT HAD ALREADY LANDED.** corpus `c8a687ef` (s188) shipped it into `trim0.sno` and `trim1.sno`, whose data *describes itself*:

```
- this line has a leading tab   → + this line has a leading TAB
```

**This is Lon's stated hazard landing on DATA rather than on code** — *"SNOBOL4 RESERVED WORDS THAT ARE NOT REALLY RESERVED VERY WELL."* The brief anticipated it for variables (`OUTPUT`, `SIZE` used as ordinary names); nobody predicted the same collision in the *data section*, where `any`, `field` and `tab` are just English.

**HARM MEASURED, NOT ASSUMED — and it is smaller than it first looks.** SPITBOL never reads post-`END` text, so `-b` output is **byte-identical before and after the corruption on all four affected files** and **no verdict moved**. It is latent, not active. But CSNOBOL4 *does* read post-`END` data, and a re-pin would have baked it in permanently. Both files are repaired here, keeping their code conversions. `fix_text()` now stops at the `END` line — the `END` line itself is still uppercased; only what follows is left alone.

## ⭐⭐ FINDING 2 — THE ACCEPT TEST WAS REVERTING CORRECT CONVERSIONS

`tab.sno` was uppercased **correctly** and reverted anyway. The full diff of its output against the `-b` baseline:

```
memory used (bytes)  15912   vs   15888
memory left (bytes)  1032656 vs   1032680
```

24 bytes — the symbol table holding different identifier strings — inside SPITBOL's **abnormal-termination report**. `execution time msec`, `memory used`, `memory left` are properties of the environment, not of the program. The scorecard already makes exactly this argument for its own `iters:`/`ms:` rule; it simply never reached these three lines.

Widening the normalizer took the pass from **0 FIXED to 3 FIXED**, with nothing else changed.

⛔ **AND THE SAME DEFECT SITS ONE LEVEL UP, IN THE MEASURING INSTRUMENT.** `util_oracle_flag_sweep.sh` shares the narrow normalizer, so **it reports its own noise as flag sensitivity**: 2 of the 42 movers were never flag-sensitive at all, and `tab.sno` would have kept reading as a MOVER *after* being correctly fixed. Both normalizers are widened. `stmts executed` and `REGENERATIONS` are **deliberately kept** — deterministic given the program, so a change in them is real and should still fail.

## ⛔ FINDING 3 — THE DRIVER WAS SEAT-LOCAL, AND IMPORTING IT EDITED THE CORPUS

`util_fix_folding_dialect.py` hardcoded `S4E="/home/claude1"` (unrunnable elsewhere) and called `main()` at **module level**. Importing it to reuse `stdin_for`/`libpath`/`run` therefore **silently executed a full fix pass** over whatever `sys.argv[1]` happened to be. **Measured, because I did it:** it ran over all 42 movers instead of my reviewed 21. **Nothing was damaged** — every file failed the accept test and was reverted, which is the guard working exactly as designed — but a reader must be able to import the module for its helpers without editing the corpus. Root now derives from `$0` per D-17 PORTABLE-HOME; the import is inert.

⛔ **A LOCK THE BRIEF REQUIRED THAT THE TOOL DID NOT HAVE.** `closure()` follows `-INCLUDE` chains and `libspec()` routes gimpel through `programs/include/` — so the walk would have **read and rewritten** files under a directory that inherits the do-not-read half of the `lon` rule. Both `programs/lon/` and `programs/include/` are now excluded **by construction** (in `closure()` so the walk never descends, plus an assert on the write path). These are **read** locks, not write locks: a secret read into a transcript has been copied somewhere new.

## THE CONVERSIONS — PER-FILE LIVE-ORACLE BEFORE/AFTER

Same filename, same cwd, only the content swapped (SPITBOL embeds the filename in error text, so a copy under another name cannot be compared):

| file | `-b` before | `-b` after | normalized `-bf` after vs pre-edit `-b` |
|---|---|---|---|
| `csnobol4-suite/setexit4.sno` | `cbf5681b` | `cbf5681b` **unmoved** | `7e7fd3441f` == `7e7fd3441f` ✓ |
| `csnobol4-suite/tab.sno` | `e17721f8` | `e17721f8` **unmoved** | `4d226db786` == `4d226db786` ✓ |
| `dotnet/1brc.sno` | `402c628a` | `402c628a` **unmoved** | `54f487e116` == `54f487e116` ✓ |

The `-b` answer never moved, and `-bf` now means what `-b` meant. That is the whole content of the ruling.

## THE NEW DISPOSITION OF THE MOVER BLOCK

| sweep | same | MOVER | FLAKY |
|---|---|---|---|
| s191 baseline (post-s188, before this row) | 1750 | **42** | 25 |
| after 3 conversions, old normalizer | 1750 | 41 | 26 |
| after 3 conversions, **fixed** normalizer | 1755 | **37** | 25 |

⛔ **THE RESIDUAL 37 ARE NOT LOWERCASE-DIALECT, AND THE ROW SHOULD NOT BE RE-RUN AGAINST THEM.** Of the 21 csnobol4 movers examined per file: 2 are **case-SENSITIVE dialect** correctly left alone (their pin matches `-bf`); 3 have **nothing to uppercase** (`a.sno` is already uppercase — it is a `&DUMP` test whose output *reports variable names*, so it is a mover *about* case); the rest are **deliberate error tests** (`include2/3/4` reference a missing include on purpose, `diag1`'s own `.ref` expects an ERROR) or fail for reasons uppercasing cannot touch. **18 of 21 already differ from their pinned `.ref` under `-b` as well**, so they are not scoring correctly under either flag for reasons that predate the flag question.

## ⛔ TWO THINGS I DID NOT FIX, NAMED RATHER THAN QUIETLY LEFT

1. **The tool renames LABELS that collide with reserved words.** `tab.sno`'s label `dump` became `DUMP` — a *protected builtin name* — and `rewind1.sno`'s `copy` became `COPY` at s188. It is renamed *consistently* (definition and every `:(…)` reference), so the oracle accept test passes and no program is broken today. But the brief says *"NEVER labels unless the label is itself a reserved word being called,"* and a label named for a protected builtin is a collision waiting to be tripped. Fixing it properly needs label-field and goto-target protection **plus** an exception for `END` itself (which must stay consistent between the terminator and any `:f(END)` that reaches it) — a real design, not a patch. **Own row.**
2. **`csnobol4-suite/tab.sno`'s pin cannot be met.** `tab.ref` records `total words: 271` and a full frequency table, i.e. it was generated with the post-`END` data actually fed as input. Under the harness (`/dev/null` stdin) the program emits `total words: ` and dies `ERROR 256`. **No oracle flag can make this file match its pin** — the harness never feeds it its own data. That is a corpus/harness question, not a dialect one.

## ⛔ A PROBE RETRACTION, KEPT VISIBLE — FOUR THIS SESSION

Four probe constructions produced confident, wrong tables before being caught: `/dev/null` fed to programs that need real stdin (made `json.sno` look like it dissolved, contradicting seat1 — it does not); a before/after table run under *different filenames*, so SPITBOL's filename-bearing error text could never match; a `sed -E` test of an expression the script runs under **BRE**, where `(bytes)` is a group in one and literal in the other; and the module-level `main()` above. Each was caught by re-reading the probe rather than the result. **s188's rule keeps earning its keep: a probe not shown to do the thing it claims to do is not evidence.**

## NEXT

1. **Label/reserved-word collision** — own row (see above).
2. **`tab.ref`'s unmeetable pin** — the harness never feeds post-`END` data; decide whether to re-pin against `/dev/null` or teach the harness the idiom.
3. ⭐ **Re-check any conclusion drawn from a pre-s191 flag sweep.** The mover count was inflated by environment statistics, and `scorecard-oracle-case` (seat2) is sized off exactly that number.
4. **`programs/include/` still blocks the gimpel half** of this ruling — 71 files seat1 flagged, untouchable until Lon rules on that directory.
