# FINDING — CURED (dispatch route) + CLASS MEASURED (scan-node route): SCRIP's Icon builtins accepted
# argument types their own oracle rejects, silently continuing where icont/iconx raises and aborts. The
# two filed witnesses (`insert()`, `bal()`) were the visible tip of a 22-wide class over TWO INDEPENDENT
# ROUTES. The dispatch route (9 builtins) is cured; the scan-node route (8 builtins) is measured, named,
# and still red. Also cured here: the rung19 real `to`/`by` generator, and a `by 0` INFINITE LOOP that
# curing rung19 would otherwise have widened.

**hq_B · 2026-09-04 · row `icon-ladder-top-rung-census-from-the-icon-book`** (QUARTET inherit from seat01;
path (a) of that row's `## NEXT` — cure the three filed defects in `src/`).

## The three filed defects, all cured

| FINDING | witness | before | after |
|---|---|---|---|
| `FINDING-2026-09-03-seat01-icon-real-toby-generator-prints-trailing-decimal-...` | `every write(3.0 to 1.0 by -1.0)` | `3.0/2.0/1.0` | `3/2/1` = oracle |
| `FINDING-2026-09-03-seat01-icon-insert-missing-set-table-type-check.md` | `insert(3, 1)` | rc=0, silent | Run-time error 122, rc=1 = oracle |
| `FINDING-2026-09-04-seat01-icon-bal-missing-cset-type-check.md` | `bal([1,2,3])` | rc=0, silent | Run-time error 104, rc=1 = oracle |

Row DONE-WHEN re-run for real: `test_icon_ladder.sh --to 37` → `graded=394 PASS=394 FAIL=0` (was
`PASS=386 FAIL=8`). rc=0.

## seat01's shared-root-cause question: answered — one IDIOM, two ROUTES, not one call site

seat01 raised (explicitly not confirmed) that `insert()` and `bal()` might share a root cause. They share
an **idiom**, not a helper: every site spelled a wrong-type argument as `*out = FAILDESCR; return 1;` —
Icon *failure* — where the oracle raises a *runtime error*. That conflates "right type, no match" (fail,
ordinary control flow) with "wrong type" (error, aborts). There is no single shared coercion helper to
repair; the fix is to make each expected-type family raise its own code.

Sizing it against the oracle rather than guessing (14 probes, `icont -s f.icn -x` v9.5.25a) found the gap
is **not two builtins but the whole family**, and that it is reachable by two independent routes:

**Route A — the builtin dispatcher** (`by_name_dispatch.c`), non-scanning call forms. All 9 diverged:
`insert` `delete` `member` (122) · `key` (124) · `any` `many` `upto` `bal` (104) · `find` `match` (103).

**Route B — the scan-node templates.** Inside a scanning expression (`s ? any(x)`), `lower_icon.c` lowers
these to dedicated `IR_SCAN_*` nodes (`bb_scan_any.cpp` etc.), which **never reach the dispatcher at all**.
All 8 still diverge: `any` `many` `upto` `bal` (104) · `find` `match` (103) · `tab` `move` (101).

⭐ This is why a per-handler edit would have produced a false cure. `bal`'s own handler is guarded
`(_bid == BID_bal) && (scan_pos > 0 || nargs >= 4)` — the filed rung37 witness `bal([1,2,3])` has
`nargs == 1` and no scanning context, so it **never enters the handler**. A type check written inside
`if (_bid == BID_bal)` would have compiled, read correctly, passed review, and left the witness red.

## What was cured (Route A)

One table-driven gate, `icn_argtype_gate()`, placed after `_bid` is computed and before the handler chain
(and before the `g_bidjmp_on` jump table, which otherwise branches straight past any per-handler check) —
so it is immune to each handler's own guard. It reuses the idiom already established in this file by
`detab`/`entab`: type-check → `core_icn_error(code, val)` → `FAILDESCR`. `core_icn_error` already honours
`&error`, so error-to-failure conversion keeps working.

⭐ Routing through `core_icn_error` rather than a fresh abort path is what earns Icon's **error trapping**
for free, and that was verified rather than assumed: with `&error := 1`, both
`insert(3,1)` and `bal([1,2,3])` convert to ordinary failure, execution continues, and `&errornumber`
reads `122` / `104` — byte-identical to icont/iconx on the same programs. A hand-rolled
`fprintf`+`exit(1)` would have passed every board here and broken every error-trapping program.

Acceptance sets were measured, not assumed, so the gate does not over-refuse: integer/real/string/cset are
all cset- and string-convertible (`any(1,"1bc")` and `find(1,"a1c")` are legal and stay legal), `tab("2")`
/`tab(2.0)` convert, and `bal`'s c1/c2/c3 legitimately default when `&null` — while `any(&null,...)` is an
error, because `any` has no default. `key` is table-only: `key(set())` is error 124, not a fail.

## Also cured, and why it was mandatory rather than scope creep

Icon's `to`/`by` is integer-valued: the oracle truncates (`3.5 to 1.0 by -1.0` → `3,2,1`). `lower_icon.c`
was tagging the node `"ar"` when any operand was a real literal, selecting `bb_to_by`'s real arm; deleting
that tag routes Icon through the integer arm, which already calls `to_int` on all three operands.

That cure alone would have made things **worse** for one input. `1.0 to 3.0 by 0.5` previously generated
`1.0/1.5/…/3.0` — wrong, but terminating. Truncating `by` to integer makes it `by 0`, and SCRIP had **no
by-zero check at all**: it printed `1` forever. (Pre-existing: plain `1 to 3 by 0` already hung; the oracle
raises 211 "by value equal to zero".) So `core_icn_by_zero_check()` was added and is emitted by
`bb_to_by` right after the `by` operand is converted. Trading a wrong answer for a hang is not a cure.

## Two pre-existing message bugs, fixed in passing

`icn_errmsg()` carried a hand-written 10-entry subset with two wrong mappings: **110** returned
`"file expected"` (Icon: 110 is `"string or list expected"`; 105 is `"file expected"`) and **210** returned
`"invalid tab stop"` (Icon: `"non-ascending arguments to detab/entab"`). It is now generated from Icon's
own `src/runtime/data.r` errtab (58 entries, Graphics/FAttrib blocks excluded) rather than transcribed —
`RULES.md` § TRANSCRIPTION IS WHERE PROVENANCE DIES. Three vendored `.std` references
(`packages/icon/{arizona,jcon}_tests/…`, `tests/icon/rung36_jcon_errors.expected`) expect **both** texts,
so the old table could never have satisfied them.

## Shared-node scope

`by_name_dispatch.c` and `core.c` are reached by every frontend, so per `RULES.md` § SHARED-NODE VERDICT
SCOPE the control arms were graded, not assumed. SNOBOL4's `ANY`/`TAB`/`BAL` are **parser tokens**
(`TT_ANY`/`TT_TAB`/`TT_BAL`, `snobol4.tab.c`), not `BID_*` dispatches, so they do not reach the gate — a
prediction, then confirmed by the board: SNOBOL4 master `m3 PASS=1696 FAIL=0 · m4 PASS=1696 FAIL=0`.
`IR_TO_BY` is produced only by `lower_icon.c`; `IR_TO` is shared with Prolog/Raku but never carried the
`"ar"` tag, so the `to`/`by` cure cannot reach them.

## What is still red — named, not hidden

Route B's 8 builtins. Reproducers (each prints `before`/`after` rc=0; oracle raises and aborts):
`"abc" ? any([1,2])` · `many` · `upto` (104) · `find` · `match` (103) · `"a(b)" ? bal([1,2])` (104) ·
`"abc" ? tab([1,2])` · `move` (101). Separately measured and also still red: `tab("2")`, `tab(2.0)`,
`move("1")` **fail** in a scanning context where the oracle converts and succeeds — a conversion gap in
`bb_scan_tab`/`bb_scan_move`, the mirror image of the missing refusal.

Not attempted here: these live in the scan templates, would need a shared choke point
(`rt_scan_needle` is common to any/many/upto/find/match/bal but does not know the expected type, so it
cannot pick 104 vs 103 unaided) plus per-template work for `tab`/`move`, and a fresh Icon+SNOBOL4 grading
pass. Left visibly red with named witnesses rather than half-cured behind an op-name filter
(`CLAUDE.md` § no per-op filter within a BB family).
