# Icon range strictness is an IR OPERAND CONTRACT — and the checked helper's own number grammar was the second bug

**Measured 2026-09-09 by hq_U** · SCRIP `2197495bc` · corpus `669be1d7c` · `RT_OPT=-O0` · incremental `make` · oracles `icont`/`iconx` v9.5.25a (absolute path) and `raku` (rakudo).
**Row** CEO-454, the integer-coercion class. Cure landed.

## What was wrong

Icon's `to` requires integer operands and refuses a non-integer with error **101**. SCRIP coerced silently through raw `to_int`:

| | `iconx` | SCRIP before |
|---|---|---|
| `every write("a" to 5)` | error 101 | **`0 1 2 3 4 5`** |
| `every write(seq("a") \ 3)` | error 101 | **`0 1 2`** |
| `every write(5 to "a")` | error 101 | **nothing — no output, no error** |
| `write(repl("x","a"))` | error 101 | **empty string** |
| `write(repl("x",-1))` | error **205** | empty string (silent clamp to 0) |
| `every write(1 to 5 by "a")` | error 101 | error 211 (coerced to 0, then hit by-zero) |

⭐ `5 to "a"` is the worst shape of the six: it generates nothing and exits 0, so a program using it produces a short answer with no diagnostic anywhere.

## ⛔ THE SHARED-NODE PROBLEM, AND WHY THE OBVIOUS FIX IS WRONG

`core_icn_to_int_check` — validate, then coerce, raising 101 — **already existed**, and was called from exactly **two** places: `bb_scan_tab.cpp` and `bb_scan_move.cpp`. That single fact is the whole explanation of the table: `tab` and `move` were the only builtins already correct.

Swapping `bb_to.cpp`'s four raw `to_int` calls for it looks like the cure. It is not:

```
IR_TO      icon=2  prolog=5  raku=3
IR_TO_BY   icon=2
```

**Measured, not reasoned:** SCRIP's Raku `my @a = "a" .. "e"` prints `0` (rakudo gives `a,b,c,d,e` — a separate, pre-existing Raku defect) and reaches that `0` through **the same lenient `to_int`**. A strict box would make a **Raku** program raise **Icon error 101**.

**The cure is an IR-level OPERAND CONTRACT** (CEO-454): `ir_range_operands_must_be_integers()` in `IR.h`, named for *what differs*, carried on the existing `IR_TO` tag (no new `IR_t` or `BB_t` field — PEERS RULE), **set by `lower_icon.c`** because Icon's `to` requires it and **left unset by prolog and raku**, surfaced to the box as `op_range_int_operands` like every other emit property. `test_gate_emit_no_lang` passes: no language identifier enters the emitter or templates.

⭐ **`seq` needed no site of its own** — `lower_seq` builds `IR_TO`/`IR_TO_BY` directly, so it is cured by them. Locating it before cutting (CEO-454's precondition) is what showed that; it would otherwise have been "fixed" a second time somewhere it does not live.

## ⛔ THE SECOND BUG, WHICH ONLY THE CONTROL ARMS FOUND

Routing the range boxes onto the checked helper immediately **regressed** `"2.7" to 4` from `2 3 4` to error 101. **`core_icn_int_ok`'s number grammar was too STRICT**: its string branch accepted digits only, while Icon accepts real-looking and exponent strings and truncates. Pinned from the oracle:

`"2.7" to 4` → `2 3 4` · `"-2.7" to 0` → `-2 -1 0` · `"1e2" to 101` → `100 101` · `"+3" to 4` → `3 4` · `"  3  " to 5` → `3 4 5` · `"2.7.3" to 4` → **101** · `"" to 2` → **101**

⭐ **So the helper that looked like the fix was itself carrying a bug, and it had been carrying it in production the whole time** — because only `tab`/`move` reached it and nobody had probed `tab("2.7")`. Widening the grammar (fraction and exponent accepted; empty and blank still refused) **flips a pre-existing red that predates this row**: `tab("2.7")` and `move("2.7")` were wrong before I touched anything, verified on a stashed pre-change build.

⭐ **And `to_int` cannot convert an exponent string at all** — `to_int("1e2")` is 1, so accepting `"1e2"` in the validator would have promised a conversion the converter could not deliver, turning a refusal into a silently wrong sequence. The exponent conversion is done **inside the checked helper**, which only Icon reaches, leaving shared `to_int` untouched.

## Consistency kept on purpose

The two string-invoked `"..."` arms **move with native in the same commit** (CEO-454), so string invocation never diverges from the operator it names. The `"[:]"` arm is deliberately **left lenient**, because native section is not part of this row and the two must stay consistent — the same reasoning, applied in the other direction.

## Arms

- **Icon master `714/728` both modes** (`board_icon_master.sh`, row written by the runner).
- ⭐ **Name-level A/B against a build with only this change reverted: IDENTICAL in both directions.** The board's CRASH count moving 2→3 across the sitting was the **two corpus entries that arrived in the pull**, not this cure — a total-only comparison would have read it as a regression.
- **Prolog ladder `533/568 FAIL=35`** — identical, a fourth time.
- **Raku control arm**: numeric range `1,2,3,4,5` unchanged; string range still prints its own wrong `0` and **raises no Icon error** — the proof the contract does not leak.
- **Gate** `test_gate_icn_range_operands_must_be_integers.sh`: **GREEN 30/30**, then **RED 18/30** on a control build, in that order before wiring (CEO-381); wired at `Makefile` with its measured ~4s and adopted. Twelve arms stay green on **both** sides, so it is not red-by-default.

⛔ **The gate's two Raku arms assert the ABSENCE of an Icon error, never a pinned value.** Raku's `0` is wrong; pinning it would freeze a defect into a gate and make the eventual Raku cure look like a regression. Guard the leak; do not bless the bug.

## NOT CLAIMED

- The **traceback format** still differs from `iconx` on every refusal (it prints `File …; Line N` and a Traceback; SCRIP prints code and message). Codes and values match. This is the non-defect class recorded under CEO-454 — three probes that look like DIFFs and are not.
- Raku's `"a" .. "e"` remains **wrong and untouched**; it is a separate row in a parked language.
- `core_icn_int_ok` reads `d.s` as NUL-terminated, unchanged from before. That is the same length-carrying-descriptor class filed on 2026-09-09; whether a slice can reach it here is **not** measured.
- Whether Prolog's `IR_TO` uses can receive a non-integer is still **not** measured — only Raku's was, and only the leak direction matters for this landing.
