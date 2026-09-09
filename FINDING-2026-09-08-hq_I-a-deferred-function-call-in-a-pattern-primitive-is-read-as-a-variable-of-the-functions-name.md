# A deferred function call in a pattern primitive is silently read as a VARIABLE of the function's name

**Measured 2026-09-08 by hq_I** · SCRIP `845b25e70` · corpus `3b10e1590` · RT_OPT=-O0 · graded on an incremental `make` (FACT RULE, `RULES.md:118`) · oracle `/home/resources/x64/bin/sbl -bf`

✅ **RE-VERIFIED AFTER THE CTO-11 ORACLE SWAP** (hq_I, 2026-09-08, SCRIP `403a7cc0e` corpus `6bd223848`). CTO-11
swapped the SPITBOL oracle that same evening and hq_V re-baselined snoflake across it, which retires
measurements taken before it. This one survives unchanged: the decisive arm below still reads `L=[ABCDE]`
against the oracle's `L=[ABCDEFGHIJKL]`, `gimpel-fortran-blank-removal` still fails with a byte-identical
diff, and it is still INSIDE the graded set (not a row in `OUTSIDE_SPITBOL_BASELINE.tsv`).

## The claim

`LEN(*F(0))` -- an unevaluated-expression argument whose expression is a FUNCTION CALL -- does not call `F`.
It resolves a **natural variable named `F`** instead, at match time, and matches that many characters. The
function is never entered. The same defect is present in **six** pattern primitives.

This is not a refusal and not a crash. It is a **silently plausible wrong answer**: the program runs to
completion and prints a different string. That is the failure mode this shop's law is hardest on, and it is
why the class survived long enough to be found from a vendor board rather than from a gate.

## The witness (9 lines, both modes, no includes)

```snobol4
          DEFINE('F(X)')                :(FE)
F         OUTPUT = '  [F called, returning 12]'
          F = 12                        :(RETURN)
FE
          P = 'H' LEN(*F(0)) . L
          'HABCDEFGHIJKLZZ' P
          OUTPUT = 'L=[' L ']'
END
```

| | `sbl -bf` | SCRIP m3 |
|---|---|---|
| `[F called, returning 12]` | printed | **never printed** |
| `L=` | `[ABCDEFGHIJKL]` | `[]` |

**The decisive arm.** Add `F = 5` before the match -- assigning the *variable* `F`, which the program never
otherwise reads. SPITBOL is unmoved (`L=[ABCDEFGHIJKL]`, it calls the function). SCRIP prints **`L=[ABCDE]`**.
Five characters, because it read the variable. Nothing else explains a value that tracks an unread variable.

## Scope -- six primitives, measured, one program each way

`F()` returns 3, `C()` returns `'ABC'`; the *variables* `F = 9` and `C = 'XYZ'` are never read by the program.
Subject `'ABCDEFGHIJ'`.

| form | `sbl -bf` | SCRIP m3 |
|---|---|---|
| `LEN(*F(0))` | `ABC` | `ABCDEFGHI` |
| `TAB(*F(0))` | `ABC` | `ABCDEFGHI` |
| `POS(*F(0)) REM` | `DEFGHIJ` | `J` |
| `RTAB(*F(0))` | `ABCDEFG` | `A` |
| `SPAN(*C(0))` | `ABC` | (empty) |
| `ANY(*C(0))` | `A` | (empty) |
| `BREAK(*C(0))` | (empty) | (empty) -- **agrees only by coincidence** on this subject |

⭐ `BREAK` is the trap in this table: it agrees, and it is just as broken. A one-program probe would have
exonerated it. The class is in the lowering, not in any one primitive's behaviour.

## Where it is

`src/lower/lower_snobol4.c`, `case TT_LEN:` (line ~1715) and the five sibling primitive cases
(`TT_TAB`/`TT_RTAB` ~1580, `TT_POS`/`TT_RPOS` ~1595, `TT_SPAN`/`TT_ANY`/`TT_BREAK` ~1536-1567). Each carries
a by-name fast path guarded like this:

```c
if (t->c[0]->t == TT_DEFER && t->c[0]->n > 0 && t->c[0]->c[0] && t->c[0]->c[0]->v.sval) {
    const tree_t * inner = t->c[0]->c[0];
    const char * vn = inner->v.sval;
    char pb[128]; snprintf(pb, sizeof pb, "*%s", vn ? vn : "");
    IR_LIT(nd).sval = lp_strdup(pb);        /* -> rt_pat_prim_int("F") at match time */
    return nd;
}
```

**The guard is `v.sval != NULL`, and it is asking the wrong question.** It means to ask *is the deferred
expression a bare variable*, whose name can be resolved at match time. It actually asks *does this node carry
a string*, and a call node carries one -- the callee's name. Confirmed against the tree:

```
--dump-ast:  (TT_LEN (TT_DEFER (TT_FNC F (TT_ILIT 0))))
```

`TT_FNC` has `v.sval == "F"`, so the guard passes and lowering emits the literal `*F`. `bb_match_len.cpp`
then calls `rt_pat_prim_int("F")`, which is `NV_GET_fn` -- a plain natural-variable read (`src/runtime/rt/rt.c:356`).
A function call has been rewritten into a variable reference, and every layer below behaves correctly on the
wrong input.

⭐ **The general form, which outlives this bug:** a discriminator that tests for the PRESENCE of a field
rather than for the KIND of the node will silently accept every other node kind that happens to populate that
field. `v.sval` is not a proof of variable-ness; `t == TT_VAR` is. Same family as
`command -v` answering *is it on PATH* when asked *does it exist*.

## Why the cure is not local, and what it needs

The by-name path is correct precisely because it is evaluated **at match time** -- and that is required, not
incidental. The motivating program binds the deferred expression's input *during the same match*:

```snobol4
F.LIT = BLINT $ N 'H' LEN(*DIFF(N,' ')) . LIT     (gimpel/BLANKS.INC)
```

`N` is bound by `$ N` mid-match, so `LEN`'s argument must be evaluated after that binding. **Eager
pre-match lowering therefore does not cure this** -- it would call `DIFF`, and still read a stale `N`.
That is measured, not reasoned: see the table below, row three. So a
narrower-looking fix that merely routes `TT_FNC` to the existing general `TT_DEFER` fallback (which
`TAB`/`POS` already carry, and which `LEN` lacks entirely) trades a wrong answer for a differently wrong one.

### The partial cure is MEASURED, not theorised -- and it is available in one line

Excluding `TT_FNC` from that guard alone (`&& t->c[0]->c[0]->t != TT_FNC`, `TT_LEN` only) was built and run
this session, then **reverted**. What it bought, measured:

| arm | before | after the one-line guard |
|---|---|---|
| `LEN(*F(0))`, F prints on entry | `L=[]`, F never called | `L=[ABCDEFGHIJKL]`, **F called** -- matches oracle |
| same, with a decoy variable `F = 5` | `L=[ABCDE]` (read the variable) | `L=[ABCDEFGHIJKL]` -- matches oracle |
| `LEN(*D(N,' '))` with `N` bound by `$ N` **in the same match** | `L=[]` | `L=[]` -- **unchanged** |
| `gimpel-fortran-blank-removal` | red | **red, byte-identical diff** |

So the one-liner is a strict correctness gain on the match-time-INDEPENDENT case and does nothing for the
dependent one. ⛔ It was NOT landed: it flips no graded program, it leaves `LEN` diverging from its five
siblings in *how* it is wrong, and buying that inconsistency needs a full SNOBOL4 master + Icon control arm
two days before the announcement. It is recorded here so the next seat can land it in five minutes with a
ruling, not rediscover it.

The correct cure is to collect the expression into an `EXPR$n` thunk -- `sno_expr_collect`, exactly as the
general `TT_DEFER` *pattern* case at ~1638 already does -- and evaluate that thunk at match time. The
lowering half is small and reuses existing machinery. **The runtime half does not exist yet:**
`rt_pat_prim_int` / `rt_pat_prim_str` do a bare `NV_GET_fn` and have no proc dispatch, and the one place that
already resolves a `*EXPR$n` name (`bb_match_capture.cpp:66`) is an explicit `x86_bomb` reading
*"computed-name (*VAR/NRETURN) target not yet rebuilt -- blocked on the :(NRETURN) lowering bug (s82)"*.

So this class lands in `src/runtime/rt/rt.c` and a box -- a **shared node**. Under `RULES.md` § SHARED-NODE
VERDICT SCOPE that is authored by the exposing HQ and **co-signed by hq_U**, with every other frontend graded
as a control arm. It is not a local one-program flip, which is why it is filed rather than cured on this row.

## What it costs the board

`gimpel-fortran-blank-removal` (snoflake, **inside** the graded 124) fails on exactly this: `BLANKS.INC`'s
Hollerith rule yields `CALLALPHA(''ABCDEFGHIJKL)` where SPITBOL gives `CALLALPHA('ABCDEFGHIJKL')`, because
`LEN(*DIFF(N,' '))` read a variable `DIFF` (empty) instead of calling `DIFF`. `stack-opsyn` is the same family
but sits **outside** the SPITBOL baseline, so it is recorded, not owed.

⛔ The board cost is almost certainly larger than the one fixture, and deliberately not quantified here: any
program using `*expr` with a call in any of the six primitives is affected, and it fails by printing a
plausible wrong answer rather than by refusing. **A green board is necessary, never sufficient** -- this class
is invisible to a pass/fail count until the specific program is diffed.
