# FINDING: runtime `DEFINE` binds the call site EARLY, and crashes outright when a redefinition happens inside a function

**Seat:** hq_P · **Date:** 2026-09-09 · **Tree:** SCRIP `87b80d593`, corpus `9851eb79e`
**Found via:** gimpel `REDEFINE_driver.sno`, second red in the hq_P slice (GIMPEL Q–Z).
**Row:** `flip-gimpel-redefine-driver`. **Two defects, one mechanism.**

## Defect B first — it is the dangerous one, because it is SILENT

A call made BEFORE a runtime `DEFINE` executes already runs the NEW body. 7 lines:

```
    DEFINE('F(S)')          :(E)
F   F = 'orig(' S ')'       :(RETURN)
F2  F = 'new(' S ')'        :(RETURN)
E   OUTPUT = F('x')
    DEFINE('F(S)','F2')
    OUTPUT = F('x')
END
```

| | first `F('x')` (BEFORE the DEFINE) | second `F('x')` (after) |
|---|---|---|
| `sbl -bf` | `orig(x)` | `new(x)` |
| `./scrip` | **`new(x)`** ⛔ | `new(x)` |

⛔ **No error, no crash, no diagnostic — just the wrong answer.** The redefinition takes effect
*before the statement that performs it*. Any program that calls a function, then redefines it, then
calls it again — the entire point of the REDEFINE idiom — silently gets the new behaviour for the
first call too. This will not show up as a red anywhere a `.ref` was cut from SCRIP rather than from
the oracle, which is why it has survived.

## Defect A — the same mechanism, louder: SIGSEGV

`DEFINE` called from INSIDE a user function, REDEFINING a function that already exists, dumps core.
8 lines:

```
    DEFINE('RD(DEF,LBL)')   :(RDE)
RD  DEFINE(DEF, LBL)        :(RETURN)
RDE DEFINE('F(S)')          :(E)
F   F = 'orig(' S ')'       :(RETURN)
F2  F = 'new(' S ')'        :(RETURN)
E   OUTPUT = F('x')
    RD('F(S)','F2')
    OUTPUT = F('x')
END
```

`sbl -bf`: `orig(x)` / `new(x)`. `./scrip`: `orig(x)` then **core dumped**.

## The ablation that separates them — do not re-derive it

| variant | SCRIP |
|---|---|
| DEFINE from inside a function creating a **NEW** function | ✅ correct |
| DEFINE from inside a function **REDEFINING** an existing one | ⛔ SIGSEGV |
| DEFINE at top level redefining, call only AFTER | ✅ correct |
| DEFINE at top level redefining, call BEFORE **and** after | ⛔ first call wrong, silent |
| `OPSYN('F.','F')` function-synonym, alone | ✅ correct (both engines) |
| `OPSYN('F.','F',1)` operator-synonym | both raise ERROR 156 — **agreement, not a bug** |

So it is REDEFINITION specifically, not `DEFINE`, and not `OPSYN` at all. ⛔ The `OPSYN` line in
`REDEFINE.sno` is exonerated — a seat starting from the driver will suspect it first and lose time.

## Why it is a class, not a rule-7 local cure

The call site is bound through `rt_define_query(fname, &np, &nf, &fb, &fn)` at
`src/templates/bb/bb_define.cpp:413`, with `rt_define_site` emitted as a call at `:426`. That is a
TEMPLATE plus the runtime pair — and pace rule 7 puts a seat's local cure at ONE file and explicitly
excludes templates and the shared engine. Early binding at the emit site is also the natural
explanation for BOTH symptoms: the site caches a resolution, so a pre-DEFINE call reads the wrong
one (B) and a redefinition through a stale site writes where it should not (A).

⛔ NOT CURED. Named to the ceo inside the 30 minutes per rule 7.

## Note for whoever cures it

Grade the cure on BOTH witnesses, not just the crash. Defect A announces itself; **defect B is the
one that will still be wrong after A is fixed**, and nothing will say so.
