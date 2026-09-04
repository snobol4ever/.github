# FINDING: Pascal master's "ELEVEN reds" was a harness bug (5) + one real class (6, hq_P cured 5/6 concurrently) — true remaining count is ONE, precisely isolated

**Who/when:** seat11, 2026-09-04 (box clock; FLEET-16), row `pascal-master-eleven-reds-cured` (PAS2), re-laned to seat11 from seat13 by ceo 2026-09-04T00:22:51Z per Lon's seat-range correction.

## The eleven was never eleven

`pascal-master-eleven-reds-cured`'s own GOAL (hq_P, measured 2026-09-03 ~21:00) and SCORE.md (both the summary row and the detail row) all report **m3 153/164 · m4 153/164, ELEVEN reds**: seat09's five (`program_array_packed_5`, `program_array_packed_replace_1/2/3`, `program_procedure_array_3`), `ladder__rung09_strings`, and five `parser__*` entries "in nobody's ledger" (`parser__assign_simple`, `parser__if_then_else`, `parser__for_loop`, `parser__procedure_call_args`, `parser__array_index`).

**Five of the eleven were never defects.** `corpus/tests/pascal/ALL.csv` declares `modes=ast` for exactly those 5 `parser__*` entries — `corpus_suite_harness.py` grades `modes=ast` entries by `scrip --dump-ast` diff (never executes them), *if and only if* invoked with `--by-modes-column`. `test_gate_pascal_m3.sh`/`m4.sh` (and this row's own DONE-WHEN) invoked the harness with a bare `--modes m3`/`--modes m4,m3` instead, which silently ignores the CSV's per-entry column and grades every entry by execution — so 5 programs that print nothing by design (no `write`/`writeln` anywhere in source; confirmed by reading all 5) got compared against their `ALL.ref` AST-dump text as if it were expected stdout, and "output mismatch" was reported for all 5, every time, forever. Re-running with `--by-modes-column`: `SUITE_BOARD_AST total=5 ast_pass=5 ast_fail=0`. **This exact bug class already hit Raku once** (SCORE.md's raku row: "the ceo's earlier 42-ast_fail reading was a FALSE BOARD: the same command WITHOUT `--modes` collapsed the 42 run-graded entries into the ast bucket — harness now refuses rc=3" — the mirror-image failure mode of the same root cause, a harness invocation not agreeing with the CSV's declared per-entry grading mode).

I did NOT touch `ALL.ref`/`ALL.pas`/`ALL.csv` — an earlier attempt to "fix" the 5 witnesses by rewriting their `.ref` to empty (matching plain-execution grading) was **reverted** before commit once the CSV's `modes=ast` column was found; the AST-dump reference content was correct all along for its intended grading path, the invocation was wrong.

**Fixed instead:** `scripts/test_gate_pascal_m3.sh` and `scripts/test_gate_pascal_m4.sh` (SCRIP `c967cc91`) — added `--by-modes-column`, and extended each gate's board-parsing to fold the harness's separate `SUITE_BOARD_AST` line into PASS/FAIL/MASTER_EXAMINED instead of dropping it (a naive `--by-modes-column` add alone would have silently stopped counting the 5 ast entries at all, rather than crediting them as the passes they are). `pascal-master-eleven-reds-cured`'s own DONE-WHEN corrected the same way (see task LEDGER).

## The real six (now one)

The other six were real: `program_array_packed_replace_1/2/3`, `program_array_packed_5`, `program_procedure_array_3`, `ladder__rung09_strings` all raised `Run-time error 102 / numeric expected` on `packed array[..] of char` compared via `=`/`<>`/`<`/`<=`/`>`/`>=` (against another packed-array-of-char, a string literal, or both) — ISO 7185 defines these as valid structural/lexicographic comparisons; SCRIP's relop implementation didn't recognize the composite type and fell through to a numeric-only check. Confirmed directly against `fpc -Miso` (FPC 3.2.2) for two witnesses before this was even filed.

**hq_P cured 5 of these 6 while this census was in progress** (SCRIP `ccd45a59`, "packed array of char compared NUMERICALLY, so every string relation died at error 102", pulled in via rebase). Re-measuring after: `SUITE_BOARD total=159 m3_pass=158 m3_fail=1 m4_pass=158 m4_fail=1` — only `program_array_packed_5` still red.

**The one residual, precisely isolated:** hq_P's fix covers a bare packed-array-of-char **variable** compared directly (`a < b`, confirmed passing now). It does not cover a packed-array-of-char value reached through **array indexing** — `rw[i] < rw[j]` where `rw: array[1..3] of packed array[1..4] of char`. Minimal 7-line witness (constant indices, no variables needed to trigger it):

```pascal
program m1;
type alfa = packed array[1..4] of char;
var rw: array[1..3] of alfa;
begin
  rw[1] := 'aaaa';
  rw[2] := 'bbbb';
  if rw[1] < rw[2] then writeln('lt') else writeln('nolt')
end.
```

`Run-time error 102 / numeric expected`, both `<` and `=`, both m3 and m4 (confirmed by hand-assembling and running the m4 binary directly, not inferred from m3). `program_array_packed_5` is the only master-suite witness whose packed-array-of-char operand is an indexed array element rather than a plain variable, which is exactly why it's the only one of the six hq_P's fix didn't already reach.

## Cross-suite link (fpc_tests, not this row)

`pascal-fpc-class-runtime-102-numeric-expected` (fpc_tests suite, currently unassigned — released by seat15 2026-09-03T21:29Z, not worked) bundles 3 witnesses under the same error message: `test_tparray10`, `webtbs_tw3572`, `webtbs_tw37393`. Checked all three source files directly:
- `test_tparray10.pas` line 29 (`if pacy <> 'ABCD' then halt(1)`) — genuinely the same packed-array-of-char-vs-literal mechanism. **But this witness cannot currently reach that line either way**: it fails earlier with 5 lex "invalid character" errors (lines 33-41, `#0` char-literal syntax) and an "Error 5 Undefined function" (`pack`/`unpack` not implemented) — confirmed by running it directly. Answers that row's own open question ("check whether the lex issue is upstream... or a red herring"): **it is upstream and blocking**, independent of the relop mechanism.
- `webtbs_tw3572.pas` — Delphi-mode `string` type (`{$MODE DELPHI}`, `function x(value: string): string`), not `packed array of char` at all. Different type, almost certainly a different mechanism sharing only the generic error message.
- `webtbs_tw37393.pas` — 12 `single`-typed (float) parameters compared as integers (`i<>9` where `i: single`), no string/array construct anywhere. Also almost certainly unrelated.

Recommend hq_P/whoever picks up that row split it: `test_tparray10`'s packed-array mechanism folds into this finding (blocked on the lex+builtin defects, not on relop); `webtbs_tw3572` and `webtbs_tw37393` are likely two more distinct classes still needing their own isolation. Not split by me — that row is fpc_tests/PAS1 territory, not touched this session, flagging only.

## Bonus defect found, not part of this suite's graded population

Manually testing `parser__if_then_else`'s source directly (it's ast-graded, so its runtime behavior is invisible to this suite either way) surfaced a second, unrelated real defect: comparing an **uninitialized `integer`** via a relop (`if x > 0 then` with `x` never assigned) raises the same `Run-time error 102 / numeric expected`, where `fpc -Miso` only warns at compile time ("Variable x does not seem to be initialized") and runs to completion normally (rc=0). Minted separately: `pascal-uninitialized-scalar-relop-numeric-expected` (does not block this row; filed because it's a genuine, previously-unknown defect this investigation happened to surface).

## Row disposition

`pascal-master-eleven-reds-cured` DONE-WHEN corrected to `--by-modes-column` and to check both the `SUITE_BOARD` and `SUITE_BOARD_AST` fail/crash fields (see task LEDGER for the exact command). Current state: **164 total, 158 pass, 1 fail (both m3 and m4)** — one minimal witness above, `ask`ed to hq_P with the exact repro. Row stays OPEN for hq_P's cure; not cured by me (construct-level relop/IR fix, outside "fixture, xfail, or instrument" scope). Per the row's own ordering rule ("DO NOT START PAS1 UNTIL PAS2's CENSUS IS FILED"), census is now filed — proceeding to `pascal-fpc-suite-62-reds-censused-by-class-and-cured` (PAS1) next.
