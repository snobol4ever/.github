# FINDING — an unsupplied Icon argument is null by every predicate except the one `case` uses

**hq_I, 2026-09-06.** Measured on SCRIP `028fcd764`+ / corpus `cc5f53a29`, RT_OPT=-O0, incremental `make`.
Cure landed in `src/runtime/by_name_dispatch.c` (`BID_IDENTICAL`). Flips `corpus/packages/icon/ipl/progs/toktab.icn`
from FAIL to PASS in **both** modes.

## The claim

`case x of { &null : ... }` did not match when `x` was a parameter the caller **did not supply**, although the
same value matched when `&null` was passed explicitly, and although every other null predicate in the language
agreed the value was null.

## The witness

```icon
procedure first(x)
   return case x of { &null : "MATCH"; "AA" : "AA"; default : "DEFAULT" };
end
procedure unsup(a, b)
   return first(b);
end
procedure main()
   write("literal &null    : ", first(&null));   # SCRIP MATCH    icont MATCH
   write("explicit &null   : ", unsup("x", &null));  # SCRIP MATCH    icont MATCH
   write("unsupplied param : ", unsup("x"));     # SCRIP DEFAULT  icont MATCH   <-- the defect
end
```

Clause **position is irrelevant** — a `&null` clause written first, third, or inside an alternation
(`"incr" | &null`) all behaved identically. The only variable that moved the answer was whether the
argument was supplied.

## Why it survived

Every instrument a program can reach said the value was null:

| probe | unsupplied param | verdict |
|---|---|---|
| `image(b)` | `&null` | agrees |
| `type(b)` | `null` | agrees |
| `/b` | succeeds | agrees |
| `\b` | fails | agrees |
| `b === &null` | **TRUE** | agrees |
| `case b of { &null : … }` | **DEFAULT** | **disagrees** |

⭐ **The reusable half: source-level `===` and `case` are not the same comparison.** `===` lowers to
`IR_BINOP_TEST` (binop 22) and never reaches the builtin at all; `case` lowers to
`IR_CALL_BUILTIN "IDENTICAL"` (`src/lower/lower_icon.c:668`, the **only** producer of that builtin in the
tree). So a value could be null by the operator a programmer would naturally use to check it, and not null
by the one the language uses internally — and no amount of probing with `===` would ever show it. Confirmed
by reading `--dump-ir` on a program containing both, not by inference.

## Root cause

`BID_IDENTICAL` gates on `a.v == b.v`, then dispatches on type. Null is `DT_SNUL`, which is `0x00` — chosen so
that "bulk memset init mints null strings for free" (`src/ir/descr.h`, and its own static assert says so). So a
null arrives by two different routes carrying two different `s` pointers:

- a null minted by **memset** (an unsupplied argument) has `s == NULL`;
- a null from the **`&null` keyword** carries `s == ""`.

Both are `DT_SNUL`, so both fell into the shared `DT_S || DT_SNUL` string arm, which compares
`(a.s == b.s || (a.s && b.s && strcmp(a.s,b.s)==0))`. The pointers differ, and the `strcmp` never ran because
the `(a.s && b.s)` guard short-circuits on the `NULL` half. Two nulls, split into two classes by a pointer that
carries no meaning for a null.

**The cure is one line**: `if (a.v == DT_SNUL) same = 1;` ahead of the string arm. `&null` has no identity in
Icon — every null is `===` every other null — so the pointer must never be consulted.

## The program it was found on

`ipl/progs/toktab.icn` calls `showtbl(names[i], tables[i], k, limit)` — four arguments to an eleven-parameter
procedure. `procs/showtbl.icn` then defaults the rest through
`sort_order := case sort_order of { "incr" | &null: "incr"; "decr": "decr"; default: stop(...) }`.
The `&null` clause did not match its own null, the default arm ran, and the program died on the first line of
its output with `*** invalid sort order in showtbl()` — an IPL library diagnostic that reads like a bad
argument and was in fact the engine failing to recognise its own null.

⭐ This shape — a library procedure defaulting unsupplied parameters through a `case` — is idiomatic
throughout IPL, so the class is expected to be wider than the one program that exposed it. It is named here
by mechanism rather than by program count so the next reader can recognise it without re-deriving it.

## Still open, and NOT cured by this change (separate defect, named so it is not lost)

`&null === ""` reads **TRUE** in SCRIP and **FALSE** in icont. This is the opposite error — the `===`
path (`IR_BINOP_TEST`) conflates null with the empty string, where the builtin correctly separates them
(`case &null of { "" : … }` already reads FALSE, matching icont). The two comparison paths are wrong in
opposite directions, which is itself the argument for them not being two paths. Not folded into this cure
because it is a different site with a different blast radius, and this one is proven by a flipped program.

## Verdict

`make test` (incremental `make`, RT_OPT=-O0) — the build this was graded on, per the loosened pristine rule.
Receipts in the baton ledger.
