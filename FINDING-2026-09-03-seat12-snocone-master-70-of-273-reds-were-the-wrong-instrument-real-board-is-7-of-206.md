# FINDING — Snocone master: 70 of 273 "reds" were graded by the WRONG INSTRUMENT (67 AST fixtures forced through m3/m4); the real board is 206 entries, 7 reds, cleanly classified into two causes

**Seat:** seat12 · **Date:** 2026-09-03 · **Row:** `snocone-master-remeasured-on-origin-and-reds-classified` (SC1, hq_P lane, MASTER-PLAN ladder)
**Tree:** SCRIP `b625b9c1` (incremental `make`, RT_OPT=-O0 — pristine loosened per `RULES.md:118`) · corpus `f4f1146e` · .github `190130fd` · clean working trees, freshly `pull --rebase`d.
**Control arm:** SNOBOL4 `make test` FAIL=0 both modes (m3 PASS=1689 FAIL=0 · m4 PASS=1689 FAIL=0 SKIP=0).

## THE BOARD, AS LITERALLY COMMANDED BY THIS ROW'S OWN DONE-WHEN

```
python3 scripts/corpus_suite_harness.py run --lang snocone --modes m3,m4 ../corpus/tests/snocone/ALL.sc ../corpus/tests/snocone/ALL.ref
SUITE_BOARD family=ALL total=273 m3_pass=176 m3_fail=70 m3_crash=0 m3_hang=4 ... m4_pass=176 m4_fail=64 ... m4_skip=6 ...
```

Every single one of the ~20 sampled fail lines printed to console was named `simple_assign_N`. That shape — one family, wall-to-wall red, on a compiler whose SNOBOL4 corpus (which shares Snocone's lowering) is 1689/1689 — is the exact "plausible, entirely false all-FAIL table" class root `CLAUDE.md` warns about.

## ⛔⛔ THE CORRECTION — SAME BUG hq_T FOUND ON THE RAKU MASTER TODAY, NOT YET PORTED TO THIS ROW'S DONE-WHEN

`corpus_suite_harness.py`'s own `LANG_CONFIGS` (line 111) declares Snocone's default grading mode as `"ast"` — same as Raku, Rebus and Prolog. Passing `--modes m3,m4` **without** `--by-modes-column` overrides that default and forces **every** entry, including pure parser/AST fixtures, through execution grading. `simple_assign_1`'s own `ALL.csv` row says `modes=ast`, `origin=parser__arith_add`; its `.ref` is `(STMT :subj (TT_ASSIGN (TT_VAR x) (TT_ADD (TT_ILIT 1) (TT_ILIT 2))))` — an AST dump, not program output. Running `x = 1 + 2;` prints nothing, so it "fails" against an AST s-expression every time, regardless of compiler correctness. **67 of the 273 entries carry `modes=ast`; 206 carry `modes=m3,m4`.**

The harness source (`scripts/corpus_suite_harness.py:1691-1707`) documents this precise trap, dated to **hours before this measurement**: *"MEASURED, NOT REASONED (hq_T 2026-09-03, on the Raku master): `run --lang raku --by-modes-column` ... All 42 'failures' were the wrong instrument, not a wrong answer."* Snocone's task-file DONE-WHEN (`snocone-master-remeasured-on-origin-and-reds-classified.task.md`) was minted with the same `--modes m3,m4`-without-`--by-modes-column` shape and was not updated when the Raku fix landed. **This is the Prolog-C2 false-board class (`FINDING-2026-09-01-hq_C-...`) recurring for the third language.**

**Correct instrument and result:**

```
python3 scripts/corpus_suite_harness.py run --lang snocone --by-modes-column --modes m3,m4 ../corpus/tests/snocone/ALL.sc ../corpus/tests/snocone/ALL.ref
SUITE_BOARD_AST family=ALL total=67 ast_pass=67 ast_fail=0 ast_crash=0 ast_hang=0 ast_unproven=0 ast_skip=0
MODES_COLUMN ast_graded=67/273 run_graded=206/273 unknown_defaulted_to_run=0
SUITE_BOARD family=ALL total=206 m3_pass=176 m3_fail=7 m3_crash=0 m3_hang=0 ... m4_pass=176 m4_fail=1 m4_crash=0 m4_hang=0 ... m4_skip=6 ...
```

The 67 AST fixtures are **67/67 clean**. The genuine runtime board is **206 entries, m3 7 fail, m4 1 fail + 6 skip** — not 273/70/64/4-hang. **DISPATCH CONSEQUENCE:** this row's own DONE-WHEN command needs `--by-modes-column` added (mirroring the Raku fix) before it can ever legitimately read `m3_fail=0`; as literally written it grades 67 entries by the wrong question forever, no matter how many real bugs get cured. Sent to hq_P as `ask` rather than blocking on it (see task LEDGER).

## THE 7 REAL REDS — TWO CLASSES

| class | n | entries | signature |
|---|---|---|---|
| **A · `procedure` keyword not implemented** | **5** | `simple_output_145` (Fib), `simple_output_151` (Double/MayFail/NullFn), `size_replace_2` (Reverse/IsPalindrome), `array_replace_3` (QSort), `table_size_replace_1` (SplitWords) | parses fail in BOTH m3 and m4, same line, `snocone parse error: syntax error` |
| **B · pattern CAPTURE (`.`) not wired for Snocone's `subject ? pattern` conditional form** | **2** | `arb_span_break_replace_2`, `arb_span_break_replace_1` | m3: runs correctly through every non-capture test, `** Error 5 ... Undefined function or operation` on the first captured pattern; m4: `FATAL lower_snobol4 (GZ#5 subset): pattern element not in the SN4-PAT subset` |

### Class A — root cause confirmed, minimal witness proven

`grep -rn procedure src/parsers/snocone/` → **zero matches, anywhere, ever.** The lexer's keyword table (`snocone_lex.c:68`) maps only `{"function", T_DEFINE}`. All 8 real (non-comment) uses of the `procedure` keyword in the entire 273-entry master are inside these 5 failing entries — **there is no passing comparison example anywhere in-corpus.**

Minimal ablation (byte-identical bodies, only the keyword changed):
```
procedure Fib(n) { if (LE(n,1)) { Fib=n; return; } Fib = Fib(n-1)+Fib(n-2); }   → parse error, both modes
function  Fib(n) { if (LE(n,1)) { Fib=n; return; } Fib = Fib(n-1)+Fib(n-2); }   → m3 prints "0 1 1 5 55" (byte-exact ref match); m4 compiles clean
```
Confirmed NOT position-dependent (fails first-in-file and mid-file alike), NOT about the recursion or the one-line brace body (a trivial non-recursive one-liner fails identically). **Not a shared-SNOBOL4 defect** — SNOBOL4 has no `procedure` surface form to share the bug with; this is Snocone-frontend-only. **Not a regression** — grep shows it was never implemented. `GOAL-SNOCONE-100.md`'s own translation table documents `procedure F(a,b) { ... }` as canonical Snocone syntax (Lon's stated design), which argues for teaching the lexer `procedure` as an alias for `function` over rewriting the 5 corpus entries — but that call belongs to whoever cures it.

### Class B — root cause NOT fully isolated; shared-node ambiguity flagged for routing

`arb_span_break_replace_2` prints `PASS: 1` through `PASS: 8 alternation` correctly (literal match, ANY, LEN, SPAN, BREAK, ARB, alternation all work), then hits `Error 5` exactly on test 9, the **only** test using `.` capture (`SPAN(...) . word`). `arb_span_break_replace_1` fails on its very first test — **every** test in that file captures (`ARB . cap`, `SPAN('a') . run`, etc.), so it fails immediately rather than 8-deep.

The m4 FATAL names `lower_snobol4` — the **shared** lowering function SNOBOL4 also uses — which raises the shared-node question hq_P flagged in the dispatch mail. But SNOBOL4's own master suite has **100 entries tagged `capture_plus_defer`, all passing** (1689/1689 FAIL=0), so pattern capture is not universally broken in the shared lowering; it is more likely specific to how Snocone's `if (subject ? pattern)` **conditional-expression** form lowers a captured pattern, versus SNOBOL4's native statement-level match. I did not read `lower_snobol4.c` far enough to confirm the exact code-path split — that is a cure-level dig, not a census one. **Recommend hq_P run the shared-node check from the dispatch mail** (`grep -c` the IR node Snocone's `?`-conditional-capture lowers to, against what SNOBOL4's capturing statements lower to) before assuming this is purely a Snocone row.

## 6 STALE XFAIL MARKERS — XPASS, PROMOTE

`simple_output_146/147/148/149/150`, `indirect_replace_1` all now pass cleanly in both modes under the corrected instrument (`XPASS(marker stale, promote it)`). Not touched this session — flagged for whoever next edits `ALL.xfail`/`ALL.csv`, per the INTERIM PROMOTION PROTOCOL precedent in the Prolog C2 finding above.

## REPRODUCE

```bash
cd SCRIP
python3 scripts/corpus_suite_harness.py run --lang snocone --by-modes-column --modes m3,m4 \
  ../corpus/tests/snocone/ALL.sc ../corpus/tests/snocone/ALL.ref
# per red:
python3 scripts/corpus_suite_harness.py extract ../corpus/tests/snocone/ALL.sc ../corpus/tests/snocone/ALL.ref <name> /tmp/e.sc --out-ref /tmp/e.ref
./scrip /tmp/e.sc </dev/null                 # m3
./scrip --compile /tmp/e.sc </dev/null       # m4
```
