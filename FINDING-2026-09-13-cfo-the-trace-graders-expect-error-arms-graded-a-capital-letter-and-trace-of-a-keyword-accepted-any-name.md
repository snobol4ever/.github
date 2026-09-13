# FINDING 2026-09-13 cfo — THE TRACE GRADER'S `--expect-error` ARMS GRADED A CAPITAL LETTER, AND `TRACE`/`STOPTR` OF A KEYWORD ACCEPTED ANY NAME

**Row** `snobol4-ladder-every-feature-in-isolation-with-variations` (rungs 19, 20, 21 walked). **Tree** SCRIP `71b32337f`, corpus `bdbb7cfb9`. **Oracle** `/home/resources/x64/bin/sbl -bf`.

## 1. THE INSTRUMENT DEFECT — EVERY `--expect-error` ARM IN THE FLEET WAS RED ON CASING

`scripts/util_sno_trace_witness.sh` grades a trace witness that must raise an error by asserting that the oracle and both SCRIP modes each print `ERROR NNN` — deliberately, because a fatal SPITBOL listing carries a pathname and a banner **date**, so an error witness can never be byte-compared. The assertion was `grep -q "ERROR $errno"`, **case-sensitive**.

SPITBOL says `file(2) : ERROR 198 -- trace first argument is not appropriate name`.
SCRIP has said `scrip: error 198: trace first argument is not appropriate name` since the ONE ERROR VOICE landing (`146d027e7`, CEO-624).

So the two implementations agreed on the number and the arm reported FAIL on the capital letters. Measured on this tree before the fix:

```
trace_bogus_type.sno        --expect-error 199   FAIL m3, FAIL m4   (got: scrip: error 199: trace second argument is not trace type)
trace_undefined_function.sno --expect-error 198  FAIL m3, FAIL m4   (got: scrip: error 198: trace first argument is not appropriate name)
```

Both are arms of the trunk row `snobol4-trace-types-v-l-c-r-k-a-print-spitbols-banner-in-both-modes`, which is CLOSED. **A closed row's DONE-WHEN has been unrunnable-green since the error-voice landing, and nothing said so**: the arm prints `FAIL`, which reads as a compiler defect, so the honest reading of that row's criterion has been a false red for days.

**CURE:** the three greps match the NUMBER and not the casing (`grep -qiE "error 0*$errno([^0-9]|$)"`). The oracle guard keeps its force — an arm still REFUSES rc=2 when the ORACLE does not raise the error, so it can never pass by both sides being silent. After the fix both witnesses PASS m3 and m4.

**THE SHAPE WORTH KEEPING:** a landing that unifies an *output voice* silently re-grades every instrument that greps that voice. The error-voice commit was correct and its blast radius was never censused. **CENSUSED NOW:** seven `scripts/*.sh` grep a capital `ERROR ` followed by a number, and six of them grep the ORACLE's output, where the capital is right (`test_gate_kw_integer_hex_refused.sh`, `test_gate_outside_baseline_rows_name_a_live_measurement.sh`, `test_gate_icn_loadfunc_returns_a_callable.sh` and the three package runners). `util_sno_trace_witness.sh` was the ONLY one asserting that spelling against **SCRIP's own** output, and so the only victim — which is why this stayed invisible: the same literal is correct in six places and wrong in one.

## 2. THE COMPILER DEFECT — A KEYWORD TRACE ACCEPTED A NAME THAT IS NOT TRACEABLE

SPITBOL manual Ch10 p.148, on type `'K'` / `'KEYWORD'`: *"Produce a trace when keyword name's value is changed by the system. The name is specified without an ampersand. Only keywords &ERRTYPE, &FNCLEVEL, and &STCOUNT may be traced."*

Measured on `71b32337f`, **both modes**, against the live oracle:

| witness | oracle | SCRIP before |
|---|---|---|
| `TRACE('ALPHABET', 'KEYWORD')` | `ERROR 198` | accepted, program ran on, printed `done 100` |
| `TRACE('&FNCLEVEL', 'KEYWORD')` | `ERROR 198` | accepted, traced nothing, printed `done 100` |
| `STOPTR('ALPHABET', 'KEYWORD')` | `ERROR 190` | accepted, printed `done 100` |
| `TRACE('errtype', 'KEYWORD')` | `ERROR 198` | (same class — the names are case-sensitive) |
| `TRACE('ERRTYPE'/'FNCLEVEL'/'STCOUNT', 'KEYWORD')` | accepted | accepted |

`_TRACE_` validated its first argument only for `CALL`/`RETURN`/`FUNCTION` (the function must already be DEFINEd — that arm was right and is untouched); the `KEYWORD` kind fell straight through to `trace_register`, which happily registered a watch on a name the system never writes. The failure mode is the bad one: **not a wrong answer, a missing refusal** — the program prints the success shape and the trace it asked for never comes.

**CURE** (`src/runtime/core/core.c`, 3 lines): one predicate `sno_kw_is_traceable()` beside `trace_type_parse()`, consulted by `_TRACE_` (raising 198) and by `_STOPTR_` (raising SPITBOL's own different number for the same shape, **190**, `stoptr first argument is not appropriate name` — SCRIP had no 190 anywhere before this). Blast radius is exactly `TRACE`/`STOPTR` with type `K`/`KEYWORD`, a SNOBOL4-only builtin pair.

**GATE** `scripts/test_gate_sno_trace_keyword_name_is_validated.sh`, ~2 s, 3 witnesses x 2 modes, wired into `make test` in the same commit. Proven **fail-once** (6 of 6 arms RED on the pre-cure binary, by reverting the 3 lines and rebuilding — 1.4 s) and **pass-once** after. It grades by error NUMBER through the repaired grader, because these three forms can never be master witnesses: the oracle answers each with a dated listing (RULING R5).

## 3. WHY A CENSUS FOUND WHAT TWO CLOSED ROWS DID NOT

The `KEYWORD` row (`snobol4-trace-keyword-fnclevel-stcount-errtype-on-every-system-write`) states the rule in its own GOAL — *"only those three are traceable"* — and closed on a DONE-WHEN that greps one banner line out of `trace_keyword.sno`, a witness that traces only legal names. **The clause was in the brief, never in the criterion.** The defect surfaced only when the ladder made the census enumerate the reference page by page and mint one witness per claim, which is what the ladder row is for: a DONE-WHEN grades the shape its author thought of, and an enumerated census grades the page.

## 4. WHAT THE WALK ALSO MEASURED (no cure owed here)

Re-measured on this tree, both modes, against the live oracle — the 2026-09-05 "all nine trace arms RED" reading is **eight days stale**: `trace_trunk`, `trace_function`, `trace_ftrace`, `trace_label`, `trace_keyword` are all **0 diff lines in both modes**. `trace_value_sinks` is 12 diff lines, `trace_access` 4, `trace_element` 5 in m3 and **does not build in m4** — three FREE rows, each already minted, none this row's.

`snobol4-trace-label-fires-on-every-goto-transfer-and-never-on-fall-through` (rank 1, FREE since 09-07) was **closed on measurement with no cure written**: its DONE-WHEN runs rc=0, PASS both modes. It had been carried green by the trunk landing and never re-read.
