# FINDING — `rt_g_want_name` is a global left LIVE across the callee's whole body, so an NRETURN result is not dereferenced inside a deferred assignment target

**Seat:** hq_V · **Date:** 2026-09-08 22:1x–22:3x CDT · **Tree:** SCRIP `60d58c05b` (measured), tree returned **CLEAN** — nothing landed
**Row:** `snobol4-nreturn-result-is-stringified-to-its-name-inside-a-deferred-star-expression-evaluated-during-a-match` (rank 2, hq_V)
**Red it explains:** `gimpel-l-one-compiler` (snoflake, graded) — whole diff is three lines

## The symptom, and the whole of the fixture's diff

`gimpel-l-one-compiler` differs from `sbl -bf` in exactly three lines: ` STORE ` with an **empty operand** where the oracle reads ` STORE TEMP1`, ` STORE TEMP2`, ` STORE TEMP3`. Everything else — ` LOAD C`, ` MUL D`, ` SUB TEMP1`, ` LOAD TEMP2` — matches, so `TEMP()` and the stack are correct. Only the **return value** of `PUSH(...)` is lost, and `PUSH.INC` returns **by name**: `PUSH = .VALUE(PUSH_POP) :(NRETURN)`.

## The minimal repro — same function, two contexts, one wrong

```
        DEFINE('NV()')
        DEFINE('DEF()')                 :(D_END)
NV      V = 'BYNAME'
        NV = .V                         :(NRETURN)
DEF     OUTPUT = 'in-def[' NV() ']'
        DEF = 'X'                       :(RETURN)
D_END
        PAT1 = NULL . *DEF()
        'X' PAT1
        PAT2 = *DEF()
        'X' PAT2
END
```

| | oracle `sbl -bf` | SCRIP m3 |
|---|---|---|
| `NULL . *DEF()` — deferred call **as an assignment target** | `in-def[BYNAME]` | **`in-def[V]`** ⛔ |
| `*DEF()` — deferred call as a plain pattern element | `in-def[BYNAME]` | `in-def[BYNAME]` ✅ |

The **same** `DEF`, calling the **same** `NV`, one statement apart. Where the named cell is a **data-field** reference (`.VALUE(PUSH_POP)`, as in `PUSH.INC`) the stringification comes out **empty**, which is exactly the ` STORE ` lines.

**Four intermediate repros are GREEN** and are recorded so nobody re-walks them: the same NRETURN function called at top level; called with a nested user-function argument; called from inside an ordinary function body; and the whole `PUSH`/`POP`/`TEMP` trio driven directly. The defect is **the deferred-evaluation-during-match context and nothing simpler.**

## ⭐ The mechanism, measured at the seam

`rt_g_want_name` (`src/runtime/rt/rt.c:804`) is a **global** meaning "the caller wants a NAME, not a value". `src/runtime/pattern_match.c:736` sets it to 1 around the deferred *assignment target* call and restores it after — correctly, because that call really must yield a name. Instrumented run of the repro above (probes reverted):

```
[WN] call_proc_descr name=DEF glob=1        <- DEF's body is entered with the flag still 1
[WN] nret_fix_TINY entered glob=1           <- NV() returns via the staged/tiny epilogue
[WN] nret_fix wn=1 ret_by_name=1 rv=40      <- rv=40 is DT_N; wn=1 so the name is KEPT
in-def[V]
[WN] call_proc_descr name=EXPR$0 glob=0     <- the plain deferred element: flag is 0
[WN] nret_fix wn=0 ret_by_name=1 rv=40      <- wn=0 so it dereferences
in-def[BYNAME]
```

`rt_nret_fix(r, wn)` dereferences a `DT_N` result **only when `!wn`**. The flag is 1 for the whole of `DEF`'s body, so every nested call inside inherits the outer caller's "I want a name" intent. `rt_nret_fix_tiny` makes it worse by reading the global at **return** time (`int wn = rt_g_want_name;`) rather than at call time — note its second parameter is literally named `unused_edx`, where the intent to pass `wn` was evidently never wired.

## ⛔ THIS IS BY DESIGN, WHICH IS WHY THE OBVIOUS FIXES DO NOT WORK

The global is the **channel** that carries the caller's intent into the callee, and it is deliberately left live:

- `rt_proc_call_prologue` (`rt.c:1320`) **ends with** `rt_g_want_name = wn;`
- `rt_call_proc_descr` (`rt.c:942-952`) saves `_wn_gen` and **restores it at :952, immediately before `rt_proc_enter_named`** — i.e. re-arms it for the body
- `rt_call_named_proc` (`rt.c:1758-1764`) clears it, then **restores it right before `rt_tiny_record_enter`**

So merely clearing the flag for the body breaks the by-name return it exists to deliver. **Measured and reverted:** guarding both tiny-shim seams with `!_wn` so a want-name call takes the full prologue did **not** cure the repro (the prologue re-arms the flag anyway) and **introduced a SIGSEGV** in a fourth repro. Tree was returned clean; the baseline SIGSEGV is gone.

## What the real cure is, and why it is not a one-bug flip

`wn` must live in the **activation**, consumed by that activation's own return-fix — not in a global that is live for everything the callee does. **The machinery already exists and is simply not on this path**: `rt_ab_enter_env` (`rt.c:519`) stashes it as `*(fb + AB_OFF_WN)` and clears the global, and `rt_ab_leave_env` reads it back for `rt_nret_fix`. In the instrumented run above **`rt_ab_enter_env` never fired once** — mode 3's dyn-scope calls reach `rt_proc_enter_named` without it.

That makes the landing a **shared-node change in `src/runtime/rt/`**: it needs hq_U's co-sign and THE CONTROL-ARM BAR (ceo-359) on every other frontend, because `rt_g_want_name`, `rt_nret_fix` and the staged-call epilogue are reached by more than SNOBOL4. It is not the "one package program, cure it, flip it" shape OCTET/NONET is run on, and it should not be attempted as one.

**Row PARKED, not done, with this recorded.** `gimpel-l-one-compiler` stays red and stays counted. hq_B was told the fixture is claimed here so its Gimpel class does not double-count it, and told the cause, because any driver built on the by-name-returning includes (`PUSH.INC` and anything ending `:(NRETURN)`) will show the same wrong-or-empty **operand** shape the moment it is driven through a deferred star-expression.
