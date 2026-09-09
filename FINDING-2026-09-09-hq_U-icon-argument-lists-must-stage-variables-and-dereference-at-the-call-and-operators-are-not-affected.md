# Icon argument lists must stage VARIABLES and dereference at the CALL — and operators are not affected

**Measured 2026-09-09 by hq_U** · SCRIP `1b9ef783c` · corpus `f7c68a8c5` · `RT_OPT=-O0` · incremental `make` · oracle `icont`/`iconx` v9.5.25a by absolute path.
**Row** CEO-445, the cross-program Icon engine classes: *argument dereference order*. **DIAGNOSIS ONLY — NO CURE ATTEMPTED. Tree clean.**

## The witness (5 lines, both modes)

```icon
procedure main();
    local i;
    i := 1;
    write(i, (i := 2, ""), i);
end
```

`iconx` prints **`22`**. SCRIP prints **`12`**.

Icon evaluates an argument list left to right into **variables**, and dereferences them **when the call is made** — so by the time `write` runs, both `i` arguments read 2. SCRIP dereferences each argument as it is evaluated, so the first `i` is frozen at 1.

## ⭐ THE BOUNDARY, WHICH IS THE EXPENSIVE HALF AND IS NARROWER THAN THE CLASS NAME

The brief reads as *arguments are dereferenced in the wrong order*, which suggests every operand everywhere. **Measured, it is argument LISTS only.** Eight probes across kinds, then five more across contexts:

| construct | oracle | SCRIP | |
|---|---|---|---|
| `write(i, (i:=2,""), i)` local | `22` | `12` | ⛔ |
| same with a **user procedure** | `22` | `12` | ⛔ |
| same with a **global** | `22` | `12` | ⛔ |
| same with a **list element** `L[1]` | `22` | `12` | ⛔ |
| same with a **record field** `r.x` | `22` | `12` | ⛔ |
| `write(i,(i:=2,""),i,(i:=3,""),i)` | `333` | `123` | ⛔ |
| **list literal** `[i, (i:=2,""), i]` | `22` | `12` | ⛔ |
| return value: `h(i,(i:=2,""))` returning `a` | `2` | `1` | ⛔ |
| `write(i + (i:=10, 0))` **binary operator** | `10` | `10` | ✅ |
| `write(i || (i:="b",""))` **concat** | `b` | `b` | ✅ |
| `write(f(i), (i:=2,""), f(i))` **nested call** | `12` | `12` | ✅ |
| `write(L[i], (i:=2,""), L[i])` **subscript** | `12` | `12` | ✅ |
| `write(i, "", i)` **no mutation** | `55` | `55` | ✅ |

⭐ **The four greens are what make the statement precise, and two of them are counter-intuitive:**
- **Operators are NOT affected.** Operand dereference is already correct. So the cure belongs in argument staging, not in a general deref-timing change — a fix aimed at "dereference later" everywhere would move code that is already right.
- **`L[i]` is green while `L[1]` is red, and that is not a contradiction — it is the rule stated exactly.** The *variable identity* is fixed at evaluation time (the subscript expression `i` is read then, giving `L[1]`); only the **dereference** is deferred. In the red case the identity is the same slot and its *value* changed. So the cure must stage the variable **already resolved**, and defer only the read.
- **A nested call is green** because a call yields a value, not a variable — there is nothing to defer.
- `no mutation` is the control proving this is deref *timing* and not argument evaluation order generally.

## Where the cure goes, and why it is not small

`src/lower/lower_icon.c`:
- `case TT_VAR` (line 459) builds **`IR_VAR`**, which reads the variable's *value*. Deferring requires the argument to lower to an l-value — **`IR_VAR_REF`**, which already exists and is already used this way by the `name()` path in `lower_call` (~line 161) — with an **`IR_DEREF`** emitted after the whole argument list rather than inline.
- The argument loop in **`lower_call`** (~line 181) and **`lower_make_list`** are the two sites; the list literal shares the defect, so it shares the cure.

⛔ **NOT ATTEMPTED, AND THE REASON IS THE RISK, NOT THE SIZE.** `IR_VAR_REF` in an argument position must be accepted by every consumer of a staged argument — `IR_CALL`, `IR_PROC_GEN`, `IR_CALL_BUILTIN_GEN`, the `bb_call_*.cpp` family including `bb_call_write_slot.cpp`, and the by-name and generator call paths — and `write`/`writes` take a separate `chains` path in the same function. That is every Icon call in the language, against a master standing at **707/707 FAIL=0 both modes** two days before the announcement. This is a full board cycle's worth of change and it wants a fresh sitting, not the end of a long one. The diagnosis above is the expensive half and it is done.

## Arms owed when it is built

1. Icon master both modes — must hold `707/707`.
2. **Prolog control arm** — `IR_CALL_VALUE` is lowered by icon=2 and prolog=1 (reach, not merely linkage); the ladder's `533/568 FAIL=35` is the standing comparison.
3. A gate over the thirteen probes above, the five greens included — the greens are load-bearing, since the likeliest way to get this wrong is to defer dereference too widely and move the operator cases that are already correct.

## NOT CLAIMED

- No cure, no code touched, tree clean at `1b9ef783c`.
- I have **not** measured how many package programs this flips. It is filed as a cross-program engine class on the ceo's routing (CEO-445), and the probes above are minted witnesses, not graded corpus entries.
- The Icon-vs-SCRIP agreement on operators is measured for `+` and `||` only; it is not proven for every operator.
