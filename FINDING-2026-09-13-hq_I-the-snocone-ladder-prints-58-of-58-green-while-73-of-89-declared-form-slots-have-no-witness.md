# FINDING 2026-09-13 hq_I — the Snocone ladder prints 58/58 green while 73 of 89 declared form-slots have no witness

**Seat:** hq_I (SNOCONE, the per-language ladder seat under MODE NONET line 2 / CEO-670).
**Tree:** SCRIP `202d8bfff` · corpus `7bedb92d0` · .github `1e8df4ccc` · `RT_OPT=-O0` · build: incremental `make`.
**Row:** `snocone-ladder-every-feature-in-isolation-with-variations` (claimed by hq_I this sitting).

## 1. THE MEASUREMENT — a green ladder over a population that excludes the gap

`bash scripts/test_snocone_ladder.sh` reads:

```
LADDER --to max: witnesses=29 modes=2 graded=58 PASS=58 FAIL=0
✅ LADDER OK: rungs 0..16 PASS 58/58        rc=0
```

`python3 scripts/util_ladder_forms_check.py --lang snocone --phase isolation` reads, on the same tree:

```
VERDICT: FAIL -- 73 declared slot(s) have no witness    rc=1
```

**Both are correct, and they answer different questions.** `lib_ladder.sh` enforces the declared census at
**rung** granularity only (its own REFUSE at `lib_ladder.sh:179`: *"a declared rung that is not built is RED,
not absent"*). Every rung 00–16 has *at least one* witness, so that check passes and the runner prints the
success shape. The **FORMS** column — the finer declaration, 89 slots across 17 rungs — is never consulted by
the runner. The forms checker consults it and fails.

⭐ **This is the missing-denominator defect the runner's own comment block at `lib_ladder.sh:160` describes,
cured one level up and still open one level down.** That comment records the identical failure at rung
granularity (*"The DONE-WHEN would have CLOSED THE ROW with six of twelve constructs never implemented"*).
The cure it documents added a rung-level census check. The form-level census was left unchecked, so the same
sentence is true again today with different numbers.

### The gap is not evenly spread — it is concentrated in the pattern engine

Measured by reading every absorbed witness source, not by name-matching:

| rung | construct | declared forms | forms actually exercised | unexercised |
|---|---|---|---|---|
| 00 | program_skeleton | 1 | 1 | 0 |
| 01 | variables_and_assignment | 2 | 1 | 1 |
| 02 | arithmetic_binary_ops | 7 | 4 | 3 |
| 03 | concatenation | 1 | 1 | 0 |
| 04 | builtin_string_functions | 6 | 2 | 4 |
| 05 | predicates_and_comparison | 13 | 2 | 11 |
| 06 | array_aggregate | 6 | 3 | 3 |
| 07 | table_aggregate | 4 | 4 | 0 |
| 08 | struct_declaration | 3 | 3 | 0 |
| 09 | pattern_matching_core | **23** | **4** | **19** |
| 10 | lexical_conventions | 7 | 6 | 1 |
| 11–16 | unary/goto/if/while/dowhile/for | 16 | 16 | 0 |
| | **total** | **89** | **47** | **42** |

⛔ **Rung 09 is the one to look at.** It declares 23 pattern primitives and its single witness is four lines:

```
s = 'key=value';
s ? BREAK('=') . k '=' REM . v;
OUTPUT = k; OUTPUT = v;
```

That exercises the match operator, conditional capture `.`, `BREAK` and `REM`. **SPAN, ANY, NOTANY, LEN, POS,
RPOS, TAB, RTAB, ARB, ARBNO, BAL, FAIL, FENCE, ABORT, alternation `|`, immediate capture `$`, cursor `@`,
`BREAKX` and value-in-expression-position have zero coverage** — nineteen declared primitives of the
language's central construct, under a rung the board reports green.

### Two counts, and why the difference is worth keeping

The checker says **73** unwitnessed of 89; my source read says **42**. The checker is stricter *and it is the
DONE-WHEN authority*, because it asks whether each declared form has an origin named
`ladder__rungNN_<construct>_<form>`. Rungs 00–09 were absorbed one-file-per-rung under the doubled origin
`ladder__rungNN_<slug>__ladder__rungNN_<slug>`, which carries no form suffix, so all 66 of their declared
form-slots read as unwitnessed by name even where the behaviour is exercised. Rung 10's three witnesses are
named for *groupings* (`_literals`, `_comments`, `_case_sensitivity`) rather than for the seven declared forms.
**Neither number should be quoted alone:** 42 is what nobody has tested, 73 is what nobody can grade
individually. The cure for both is the same — per-form witnesses under the declared name.

## 2. THE SANCTIONED ADD-A-WITNESS PATH HAS NO SNOCONE ARM

`scripts/util_add_ladder_witness.py` is *"THE SANCTIONED ADD-A-WITNESS PATH"* and its `ORACLE` table
(`:61-64`) holds exactly two languages — `icon` and `snobol4`. `--lang` is `choices=sorted(ORACLE)`, so
`--lang snocone` is rejected at argument parse. Everything *else* the tool needs for Snocone is already
present and was verified this sitting: `util_build_master_suite.py` has a `snocone` `LANG_TABLES` entry (39
feature columns, matching the master's 39) and `corpus_suite_harness.py` has a `snocone` `LANG_CONFIGS` entry.

⛔ **And the missing piece is not a one-line table addition.** The tool's contract is *the ref is oracle-cut,
never hand-typed*, implemented as "run `ORACLE[lang]` on the witness source". **No such invocation exists for
Snocone**, measured:

```
$ printf "OUTPUT = 'hello world';\n" > t.sno && /home/resources/x64/bin/sbl -bf t.sno
ERROR 221 -- syntax error: missing operand   ...   No END statement found in source file(s).   rc=1
```

SPITBOL cannot parse Snocone — `;` terminators, `//` and `/* */` comments, `struct`, C-style control flow.
So Snocone needs a **twin** input, not a different binary, and that is an interface change to a shared
instrument rather than a table entry. **This is an ASK to the ceo, not a landing by this seat.**

## 3. THE REF-CUTTING METHOD THAT DOES WORK, AND ITS VALIDATION

Snocone's expression semantics **are** SPITBOL's — `config/LADDER.tsv`'s own reference (b) says so, citing
`ARCH-LANGUAGES.md` § SNOCONE. So a witness's ref is cut by writing its **SPITBOL twin**, running
`sbl -bf` on the twin, and taking the twin's stdout. The witness never contributes its own output.

⭐ **Validated before use, against ground that was already green:** the twin method reproduces the stored refs
of `rung00_hello` (`hello world`) and `rung02_arithmetic` (`5 / 6 / 42 / 5`) **byte-for-byte**. A method that
could not reproduce a known-good ref has no business cutting a new one.

## 4. TEN WITNESSES AUTHORED AND FULLY GRADED THIS SITTING — awaiting only the absorption arm

All ten are ≤ 6 lines, one form each, refs oracle-cut via twin (each oracle run performed **twice** and
compared, per the determinism refusal the adder already implements), graded in **both** modes, and each
**proven to fail once** against a corrupted ref. `m3` = `scrip --run`; `m4` = `--compile` + `as --64` +
`gcc -no-pie` + run.

| origin | witness (`.sc`) | SPITBOL twin body | ref | m3 | m4 | fail-once |
|---|---|---|---|---|---|---|
| `ladder__rung00_program_skeleton_string_literal_output` | `OUTPUT = 'hello world';` | `OUTPUT = 'hello world'` | `hello world` | PASS | PASS | ✅ |
| `ladder__rung01_variables_and_assignment_integer_literal_assign` | `x = 42;` `OUTPUT = x;` | `x = 42` / `OUTPUT = x` | `42` | PASS | PASS | ✅ |
| `ladder__rung01_variables_and_assignment_chained_multi_assign` | `a = b = c = 7;` `OUTPUT = a;` `OUTPUT = b;` `OUTPUT = c;` | `a = 7` / `b = 7` / `c = 7` / three `OUTPUT`s | `7` `7` `7` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_add` | `OUTPUT = 2 + 3;` | `OUTPUT = 2 + 3` | `5` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_sub` | `OUTPUT = 10 - 4;` | `OUTPUT = 10 - 4` | `6` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_mul` | `OUTPUT = 6 * 7;` | `OUTPUT = 6 * 7` | `42` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_div` | `OUTPUT = 20 / 4;` | `OUTPUT = 20 / 4` | `5` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_pow` | `OUTPUT = 2 ^ 10;` | `OUTPUT = 2 ^ 10` | `1024` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_precedence_chain` | `OUTPUT = 2 + 3 * 4;` | `OUTPUT = 2 + 3 * 4` | `14` | PASS | PASS | ✅ |
| `ladder__rung02_arithmetic_binary_ops_right_assoc_pow` | `OUTPUT = 2 ^ 3 ^ 2;` | `OUTPUT = 2 ^ 3 ^ 2` | `512` | PASS | PASS | ✅ |

⭐ `right_assoc_pow` is the one worth noting: the **oracle** returns `512`, i.e. `2^(3^2)`, so right
associativity is established by the oracle rather than asserted from the census, and SCRIP agrees in both
modes. `chained_multi_assign` is the one whose twin is an **equivalence rather than a transliteration** —
SPITBOL has no chained assignment, so the twin is three separate assignments with identical output; that is
named here rather than hidden, because it is a weaker link than the other nine.

These ten close rungs 00, 01 and 02 at form granularity (10 of 89 slots). They are recorded in this FINDING
rather than half-absorbed into the master, because the absorption path is the blocked step above.

## 5. THREE SMALLER DEFECTS MEASURED IN PASSING

1. ⛔ **`MODE` line 2 and this row's baton both cite a census path that does not exist.** Both say
   `tests/snocone/ladder/LADDER.tsv`; the live census is **`corpus/tests/snocone/config/LADDER.tsv`**
   (`ls` on the former: *No such file or directory*). A sovereign line naming a nonexistent file sends the
   seat that follows it literally to an empty directory.
2. ⛔ **`corpus/tests/snocone/README.md:27-28` names two patch files that are not on disk** —
   `patches/snocone.sc.diff` and `patches/snocone.sno.diff`. `patches/` holds only `Makefile.budne` and
   `README.budne`, and `README.budne`'s own instructions (`patch < snocone.sno.diff`) therefore cannot be
   followed. The likely reason is the licence note in `README.budne` itself: Mark Emmer's distribution
   **prohibits redistribution of the snocone sources**, which is also why the sources are not vendored.
3. ⭐ **A real Snocone compiler exists off-tree and is *nearly* usable as an oracle — recorded so the next
   seat does not re-derive it, with the four walls that stopped it.** `/home/satirical/SNOCONE/` holds
   Emmer's `snocone.sno` / `snocone.snobol4` (the Snocone compiler written in SNOBOL4).
   (a) The files are **CRLF** — `tr -d '\r'` first, or every line dies `ERROR 230 illegal character`.
   (b) `snocone.sno` is **broken as shipped**: at `:275-285` a continuation line (`BREAK(" '" '"')`) is
   missing its column-1 `+`, so the statement ends early — `ERROR 226 missing right paren`. This is what the
   two missing Budne diffs would have repaired.
   (c) `snocone.snobol4` **does parse cleanly (0 errors)** but is written in lowercase, including its
   `end start` — so it needs **`sbl -b` (folding ON)**, not the `-bf` that is law for cutting *our* refs.
   ⭐ That distinction is worth keeping: `-bf` governs refs graded against case-sensitive SCRIP; it is not a
   blanket rule for invoking a vendor program whose own source requires folding.
   (d) Under `-b` it compiles and runs to statement 380, then dies:
   `exit action not available in this implementation` + SIGSEGV rc=139 — SPITBOL lacks `EXIT()`, and the
   compiler writes its output to a file rather than stdout.
   ⛔ **Even repaired it would not settle SCRIP's refs**, and that is the more important half: it implements
   **Koenig's original dialect**, which `config/LADDER.tsv` already documents as diverging from the derived
   dialect SCRIP implements (`procedure` vs SCRIP's `function`; no `&&`/`||`/`%`). It would be an oracle for
   a neighbouring language. The SPITBOL-twin method in §3 grades the dialect SCRIP actually implements.

## 6. WHAT THIS SEAT IS ASKING FOR

One interface change to `util_add_ladder_witness.py`, owned by the test-standard concern, not by this seat:
a `snocone` arm taking `--source W.sc --oracle-twin W.sno`, cutting the ref by running
`sbl -bf` on the **twin** (twice, refusing on disagreement, exactly as the icon/snobol4 paths already do) and
taking `want_rc` from the twin's observed exit code. Feature columns and entry name come from
`util_build_master_suite.py`'s existing `snocone` table; master shape from `corpus_suite_harness.py`'s
existing `snocone` config. Nothing else is missing.

With that arm landed, the ten witnesses in §4 absorb mechanically, and rungs 00–02 close at form granularity.
