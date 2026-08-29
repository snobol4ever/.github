# FINDING 2026-08-29 hq_C — the SNOBOL4 lexer rejected trailing-dot real literals (`414971.`), a parse-time wall in front of 5 gimpel fixtures; and the `.lex.c` regeneration recipe was undocumented but is byte-reproducible

## THE DEFECT AND THE CURE

`src/frontend/snobol4/snobol4.l:220` spelled the real-literal rule as:

```
<BODY>{DIGIT}+"."{DIGIT}+{EXP}? |
```

— **at least one digit required after the point.** SPITBOL accepts a trailing-dot real with no fractional digits. `X = 414971.` was a hard `parse error: syntax error` followed by `missing END statement`; `X = 414971.0` compiled fine. Cure is one character, `+` → `*`:

```
<BODY>{DIGIT}+"."{DIGIT}*{EXP}? |
```

## ⭐ THE EDGE CASES WERE SETTLED AT THE ORACLE FIRST, AND ONE OF THEM RULED OUT THE OBVIOUS GENERALIZATION

A lexer number rule sits next to SNOBOL4's binary `.` (pattern assignment), so "make the dot rule more permissive" is exactly the kind of change that quietly breaks `LEN(1) . C`. Every case was run against `sbl -bf` **before** the edit, and re-run against `scrip` after:

| source | `sbl -bf` | `scrip` after | note |
|---|---|---|---|
| `OUTPUT = 414971.` | `414971.` | `414971.` | the defect |
| `OUTPUT = 1.E3` | `1000.` | `1000.` | trailing dot **plus** exponent is a real |
| `OUTPUT = .5` | **compile error** | refuses | ⛔ a **leading** dot is NOT a real literal |
| `OUTPUT = 5. Y` (Y="yy") | `5.yy` | `5.yy` | real `5.` concatenated — blanks delimit |
| `"AB" LEN(1) . C` | `A` | `A` | binary pattern-assignment intact |

⛔ **`.5` is why the rule is `{DIGIT}+"."{DIGIT}*` and not something symmetric.** The natural instinct — "allow digits to be optional on either side of the point" — is **wrong against the oracle**: SPITBOL rejects `.5`. A cure written from the symmetry of the grammar rather than from the oracle would have added an acceptance SPITBOL does not have, and nothing in the corpus would ever have contradicted it. Longest-match keeps `1.5` matching the full literal rather than stopping at `1.`, so no existing acceptance narrows.

## WHAT IT MOVED — AND IT IS NOT A PASS-COUNT GAIN, WHICH I AM RECORDING PLAINLY

On the snoflake suite (180 fixtures, four-arm): **m3 PASS 76 → 76. m4 PASS 75 → 75.** What moved is **SKIP(cc) 51 → 50 / FAIL-M4 48 → 49** — one fixture went from *would not compile* to *compiles, runs, still wrong*.

⭐ **The real result is layered and only visible per-fixture:** five gimpel fixtures (`gimpel-numeric-random-functions`, `-poker-game`, `-random-string-functions`, `-real-math-functions`, `-stone-game`) each moved **from `parse error: syntax error` to `duplicate label`** — i.e. past this wall and into the *next* one, the missing `-INCLUDE` once-only memo (sibling FINDING, blocked on the no-new-globals ask). Before this cure 13 of the 18 diamond-include fixtures reached the duplicate-label wall; after it, **18 of 18** do. **A board that does not move is not the same as a change that did nothing**, and the per-fixture failure *shape* is the instrument that shows the difference. Reporting only the summary line would have made this cure look inert.

## ⭐⭐ THE REGENERATION RECIPE WAS UNDOCUMENTED AND IS BYTE-REPRODUCIBLE — RECORDED SO NOBODY EDITS THE GENERATED FILE BY HAND

`src/frontend/snobol4/snobol4.lex.c` is **committed** and **no Makefile rule regenerates it** — `grep -n 'lex.c:' Makefile` returns nothing, and the file is listed only as a source to compile. So the `.l` is what humans read while the `.lex.c` is what actually builds: **editing the `.l` alone changes nothing**, and hand-patching the `.lex.c` is unmaintainable because the pattern lives in compiled DFA tables, not in a regex.

Measured, not assumed:

```bash
flex -L -o src/frontend/snobol4/snobol4.lex.c src/frontend/snobol4/snobol4.l   # flex 2.6.4
```

reproduces the committed file **byte-identically** (`diff` = 0 lines) before the edit. ⭐ The `-L` matters and was the whole puzzle: a plain `flex -o` differs from the committed file by **244 lines, every one of them a `#line` directive** — a diff that looks alarming, is entirely inert, and would have pushed a careful person into hand-editing the generated file instead. `--noline` was the missing flag, and the way to find it was to diff the regeneration against the committed artifact rather than to trust either.

⛔ **A generated file that is committed, has no regeneration rule, and whose obvious regeneration command produces a large spurious diff is a trap with three independent layers.** Any of them alone sends the next person to the wrong fix.

## RECEIPTS
- SCRIP: `src/frontend/snobol4/snobol4.l` (1 char) + `snobol4.lex.c` (regenerated, `flex -L`, 2.6.4).
- Oracle arm: `/home/resources/x64/bin/sbl -bf` (§ `-bf ALWAYS`).
- Row: `snoflake-suite-scrip-only-gap` (hq_C, open). Sibling FINDING: `-INCLUDE` has no include-once memo.
