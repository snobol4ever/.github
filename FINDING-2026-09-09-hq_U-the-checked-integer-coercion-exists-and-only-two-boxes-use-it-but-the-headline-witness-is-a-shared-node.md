# The checked integer coercion already exists and only TWO boxes use it — but the headline witness sits on a SHARED node

**Measured 2026-09-09 by hq_U** · SCRIP `f046ef00b` · corpus `b191d461f` · oracle `icont`/`iconx` v9.5.25a, `raku` (rakudo) by PATH.
**Row** CEO-452(b), the integer-coercion class. **DIAGNOSIS ONLY — NO CURE. Tree clean.**

## ⛔ A CORRECTION TO THE ROUTING PREMISE, WHICH IS WHY THIS IS FILED BEFORE ANY CODE

CEO-452 routes this as *"one coercion site."* **The checked helper is one; the call sites that bypass it are several, and one of them is a shared node that cannot take the fix.** That changes who can land it and how, so it is said first.

## What exists, and why two builtins are already right

`core_icn_to_int_check(lo, hi)` (`src/runtime/core/core.c`) is exactly the wanted helper: it validates with `core_icn_int_ok` and raises **Icon error 101** on a non-integer, otherwise returns `to_int`. It is called from exactly **two** places in the whole tree — `bb_scan_tab.cpp` and `bb_scan_move.cpp`.

⭐ **That single fact explains the entire probe table.** `tab("a")` and `move("a")` raise 101 correctly; everything else coerces `"a"` to 0 and carries on, because everything else calls raw `to_int`.

## The probes, with the non-defects separated out

| probe | `iconx` | SCRIP | |
|---|---|---|---|
| `every write("a" to 5)` | error **101** | **`0 1 2 3 4 5`** | ⛔ generates where Icon refuses |
| `every write(seq("a") \ 3)` | error **101** | **`0 1 2`** | ⛔ |
| `every write(5 to "a")` | error **101** | **silently generates nothing** | ⛔ worst shape — no output, no error |
| `write(repl("x","a"))` | error **101** | **empty string** | ⛔ |
| `every write(1 to 5 by "a")` | error **101** | error **211** | ⚠ coerced to 0, then hit by-zero — right refusal, wrong code |
| `every write("2" to "4")` | `2 3 4` | `2 3 4` | ✅ control — numeric strings must still coerce |
| `every write("2.7" to 4)` | `2 3 4` | `2 3 4` | ✅ control |
| `write("a" + 1)` | error 102 | error 102 | ✅ **not a defect** |
| `write("hello" ? tab("a"))` | error 101 | error 101 | ✅ **not a defect** |
| `write("hello" ? move("a"))` | error 101 | error 101 | ✅ **not a defect** |

⭐ **The last three matter as much as the reds.** They differ from the oracle only in *traceback formatting* (`iconx` prints `File c.icn; Line N` and a Traceback; SCRIP prints the code and message). A seat diffing raw output sees ten DIFFs and would "fix" three things that are already correct — and `tab`/`move` are the two that show the cure working.

## ⛔ THE HEADLINE WITNESS IS ON A SHARED NODE, AND THE OBVIOUS FIX IS WRONG

`"a" to 5` lowers to **`IR_TO`**, whose box `bb_to.cpp` makes four raw `to_int` calls. Swapping them for `core_icn_to_int_check` looks like the one-line cure. **It is not, because `IR_TO` is not Icon's:**

```
IR_TO      icon=2  prolog=5  raku=3
IR_TO_BY   icon=2
```

Measured, not assumed: SCRIP's Raku `my @a = "a" .. "e"` currently prints **`0`** (rakudo gives `a,b,c,d,e` — a separate, pre-existing Raku defect, and Raku is `PARKED-LON-HOLD`). It reaches that `0` through **the same lenient `to_int`**. A strict check in `bb_to.cpp` would make a **Raku** program raise **Icon error 101** — trading a wrong answer for a wrong-language error, and violating *language identity stops at lower*.

⭐ **So `bb_to.cpp` needs a BEHAVIORAL discriminator, and there is not one today.** All three lowerers tag `IR_TO` with the identical `IR_LIT(nd).sval = "ag"`, so the tag carries no information to branch on, and `bb_to.cpp` does not read it. The legal shape is an IR-level property meaning *this range requires integer operands* — set by `lower_icon.c` because Icon's `to` does, not set by Prolog/Raku — with the box branching on that property and never on a language name.

**`IR_TO_BY` is Icon-only and takes the fix directly** — that is the `1 to 5 by "a"` row, worth landing on its own.

## What a cure has to cover

1. `bb_to_by.cpp` — Icon-only, safe today.
2. `bb_to.cpp` — needs the discriminator above **first**.
3. `seq` (`lower_seq` in `lower_icon.c`) and `repl` — sites not yet traced to their coercion call; **not** measured for reach.
4. ⭐ **My own two string-invocation arms** (`"..."` and `"[:]"` in `by_name_dispatch.c`) use raw `to_int` **deliberately**, so the string form matches the native operator. When native gets the checked helper, those must move with it — that consistency was promised in the string-invocation FINDING and is the whole reason they were not "fixed" separately.

## Arms owed

Icon master (currently **712/726** both modes), plus a **Prolog control arm** and — because `IR_TO` reaches it — a **Raku** arm, even though Raku is parked: the point of the arm is to show the parked language did not move.

## NOT CLAIMED

- No code touched; tree clean.
- `seq` and `repl` coercion sites are **named, not located** — I did not trace them to a specific call.
- Whether Prolog's `IR_TO` uses can even receive a non-integer is **not** measured; only Raku's was.
- The Raku `"a" .. "e"` defect is reported as observed, not diagnosed, and is not in this lane.
