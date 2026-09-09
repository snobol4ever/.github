# FINDING 2026-09-08 (cto, MODE EXECUTIVE) — keyword tracing fires on the system's own writes; and SPITBOL fails its own manual on `&STCOUNT`

Row `snobol4-trace-keyword-fnclevel-stcount-errtype-on-every-system-write` (hq_P's), the second type of the trace class whose FUNCTION half landed the same sitting (SCRIP `a2f772d49`). This landing is SCRIP `586722457`.

## The cure, and why it is two lines of plumbing rather than a new mechanism

`TRACE(name,'KEYWORD')` was accepted and then silent: `_TRACE_` registered the entry and nothing ever consulted it, because a keyword write has no single chokepoint in compiled code. Both traceable keywords already have exactly one writer each, so the tap goes there and nowhere else.

- **`&FNCLEVEL`.** Its writers are `bb_fnclevel_enter`/`bb_fnclevel_leave`, emitted as inline assembly, and the CALL and RETURN taps of the same box already fire at those two instants. So `rt_trace_event_args` consults the KEYWORD registry when it fires: on CALL the level is already incremented and is the value SPITBOL prints; on RETURN the decrement is still pending, so the reported value is `level - 1`. The depth column shows that same value, not the caller's level — SPITBOL prints one `i` at level 1 and no mark at level 0.
- **`&STCOUNT`.** Its writer is `rt_stmt_enter`, which is reached from the per-statement `SNO$STMT` hook the lowerer mints whenever a program names a statement keyword — and since the function-trace landing, whenever it names `&TRACE`/`&FTRACE` or calls `TRACE(`. The tap sits immediately after the increment, which is the manual's own wording.

A trace **function** (the fourth argument) reaches the same path as any other traced item, so `TRACE(.STCOUNT,'KEYWORD',,'FPROFILE')` now calls the program's own function before each statement.

## Measured against `sbl -bf`

- snoflake `trace-keyword-fnclevel`: byte-exact, and it flips — Snoflake both-modes stream **101 → 102**.
- `trace_keyword.sno`: all four `&FNCLEVEL` lines byte-exact, including statement numbers and depth marks.
- A trace function on `&STCOUNT`: identical to SPITBOL (`fired 3 lastno 8` from both).
- Budne holds **64/93** both modes, Gimpel holds **100/127**, SNOBOL4 master **1858/1858**, seven language smokes green, style gate 0, every blocking `make test` arm green.

## ⛔ SPITBOL fails its own manual on `&STCOUNT`, and this landing does not imitate it

**`TRACE('STCOUNT','KEYWORD')` resets SPITBOL's statement counter.** Measured identically on **both** SPITBOL builds — the x64 fork and `spitbol-bench-oracle` — so it is SPITBOL's behaviour and not our fork's:

```
       X = 1 ... four statements ...
5      OUTPUT = "before " &STCOUNT      ->  before 5
6      &TRACE = 100
7      TRACE("STCOUNT","K")
8      OUTPUT = "after " &STCOUNT       ->  ****8*******  &STCOUNT = 3
                                            after 2
```

The counter falls from 5 to 2, and within one statement the traced value (3) and the readable value (2) disagree. The manual is unambiguous — v3.7, Tutorial p150 and ch16 Keywords: *"&STCOUNT — The total number of statements executed. This keyword is incremented by one as each statement begins execution"*, and *"tracing keyword &STCOUNT produces a trace after every SPITBOL statement"*. SCRIP reads 5, 8, 10 on that witness and prints its traces with the same value the program reads.

**Consequence, stated plainly:** `trace_keyword.sno`'s `&STCOUNT` banner lines cannot match the oracle without reproducing the defect, and its ref is cut live from `sbl`, so the row's DONE-WHEN cannot pass honestly. Lon 2026-09-08: *"Also fix SPITBOL when it obviously fails to implement its documented features. CHeck the SPITBOL manual for the definitive answer to many questions."* Fixing the fork's counter invalidates every ref cut from `sbl` fleet-wide, so it is the ceo's ruling and not the cto's to make; asked, with three options named (fix the fork, re-cut the criterion to the `&FNCLEVEL` half plus the trace-function arm and record an ORACLE QUIRK, or imitate the defect — recommended against).

## The next bug in the same file, measured while here

Gimpel's `FPROFILE_driver` is still red, and no longer for a trace reason: its profiler sizes its array with `LPROG()`, which is `:<CODE(' LPROG = &STNO :(RETURN)')>`. **A statement compiled at run time is numbered from the current statement, not from the program's length.** Witness: a five-statement program whose last statement compiles a fragment reads `frag stno 7` under SPITBOL and `frag stno 6` under SCRIP; inside Gimpel's included module the gap is far wider (23 vs 3). The base comes from `runtime_eval.c`'s `stno_base = g_stno`. Naming it here as the next bug rather than fixing it inside a trace landing.
