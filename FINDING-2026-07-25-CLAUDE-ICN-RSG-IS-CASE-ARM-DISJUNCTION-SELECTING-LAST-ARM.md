# FINDING (2026-07-25, s166) — `rsg` ROOT CAUSE: A DISJUNCTION LEADING A MULTI-STATEMENT `case` ARM SELECTS ITS **LAST** ARM

**SCRIP `6c740055` (no code changed this session) · RT_OPT=-O0 · oracle iconx 9.5.25a**

## ⛔ THREE PRIOR DIAGNOSES ARE STALE — DO NOT CHASE THEM

s164/s165 left `GOAL-ICON-BB.md` pointing at `defnon`, at `syms` returning `nsym=0`, and at "the grammar
table never populates". **All three are now FALSE.** s165b's `lower_not` fail-conduit fix cascaded further
than it was credited for. Verified this session against the oracle, both in isolation AND inside the running
program:

| Re-tested | Verdict |
|---|---|
| `defnon` (scan-as-`if`-condition with `else`) | ✅ identical |
| `syms` (`nsym`) | ✅ identical — `nalts=1 nsym=2`, records and all |
| `alts` / `define` (scan with computed subscript key+value) | ✅ identical |
| grammar table inside REAL `rsg` (instrumented `generate`) | ✅ identical — `nalts=1 nsym_alt1=2` on BOTH engines |
| multi-name `global a,b,c` declaration + cross-proc visibility | ✅ identical |
| `type()` on record instances (`gener`'s case selector) | ✅ identical |
| `?list`, `\x`, `list ||| list`, and the whole `?\defs[k] ||| pending` expression | ✅ identical |
| `while x := get(L)` where the body REBINDS `L` to a new list | ✅ identical |

The grammar table is **correct**. The defect is entirely in `gener`.

## THE MINIMAL REPRO (12 lines, no records / tables / globals / `?` / `|||` / `break`)

```icon
procedure main();
   local pending, symbol, n;
   pending := ["A"];
   n := 0;
   while symbol := get(pending) do {
      n +:= 1;
      case type(symbol) of {
         "integer": write("int=", symbol);
         "string": {
            pending := [1,2] | [9];
            n +:= 0
            }
         }
      }
   write("iters=", n, " (expect 3)");
end
```

| | output |
|---|---|
| iconx 9.5.25a | `int=1` `int=2` `iters=3` |
| SCRIP m3 | `int=9` `iters=2` |
| SCRIP m4 | `int=9` `iters=2` (mode-identical) |

**SCRIP EVALUATES THE LAST ARM OF THE DISJUNCTION INSTEAD OF THE FIRST.** Arm 2 genuinely executes —
slot 40's `MAKE_LIST [9]` produced the value that reached `pending` — so this is arm *selection*, not a
value-slot delivery miss. (That distinguishes it from the s164 "empty value slot" framing.)

## THE THREE NECESSARY INGREDIENTS (each measured by removal)

1. **`case`** — the identical body under `if ... then {...}` is CORRECT (`m1_if` ✅). `case`-specific.
2. **The arm's FIRST expression is an assignment whose RHS is a disjunction** — a plain
   `pending := [1,2]` with the same trailing statement is CORRECT (`c2_plain_assign` ✅).
3. **At least one MORE expression follows it in the same arm** — the disjunction-assignment ALONE in the
   arm is CORRECT (`c3_disj_only` ✅).

`break` is NOT an ingredient (`c4` has none). Removing the `break`s from the real `gener` does not help
(`e_lim_nobreak`, `f_disj_nobreak`, `g_both_nobreak` all still diverge); removing the whole trailing
`if *pending > \limit then {...}` block DOES fix it (`c_no_limit_chk` ✅). Symmetrically, in full `rsg`
inserting **any** statement — even a bare `1;` — BEFORE the assignment fixes it, while the same statement
inserted at the top of the `while` body or AFTER the assignment does not. All consistent with one rule:
**broken iff the disjunction-assignment is the first of ≥2 expressions in a `case` arm.**

## IR EVIDENCE — THE ONE WIRING BIT THAT DIFFERS

`--dump-ir-verbose`, broken (`c4`) vs working (`c3`, trailing statement removed):

```
c4 BROKEN : 27  γ=28  ω=29    DISJUNCTION [36,27,39,27,38,40]
            28  γ=29  ω=29    ASSIGN [27] var="pending"
c3 WORKING : 27  γ=28  ω=24@  DISJUNCTION [30,27,33,27,32,36]
            28  γ=29  ω=24@  ASSIGN [27] var="pending"
```

The ONLY change is the disjunction's (and its ASSIGN's) **ω edge**: the case glue `24@` when the arm ends
there, versus **slot 29 — the trailing statement itself** when one follows. Operand layout is correct in
both (`(entry,resume)×N` then `result×N`, `N=ival=2`): entries 36/39, resumes 27/27 (the self marker =
"advance to next alternative"), results 38/40. Arms:

```
36 γ=37 ω=27 LIT_INTEGER 1 · 37 γ=38 ω=27 LIT_INTEGER 2 · 38 γ=27 ω=27 MAKE_LIST[36,37]   <- arm 1
39 γ=40 ω=27 LIT_INTEGER 9 ·                              40 γ=27 ω=27 MAKE_LIST[39]      <- arm 2
```

So the IR shape is sound and the arm order is right; what changes with the trailing statement is only where
the dj's ω lands, and that is enough to flip which arm runs. **START IN THE EMITTER, not `lower_icon.c`.**

## WHERE TO LOOK

`src/emitter/emit.cpp`, the nary-DISJUNCTION drive:
- **L1100** — entry-dispatch pair array: `t = node_ω` default, overridden to `lbls[k]` when the arm head is
  found. `node_ω` is exactly the edge that differs between c3 and c4.
- **L1101** — resume targets; `r == nd` (self marker) → `na_f[i]` = advance-to-next-alternative.
- **L1112** — per-arm result slots into `g_emit.op_parts_ival[j]`, consumed by the σ-glue.
- **L950 / `bb_disjunction()`** — the α/alt_i self-state dispatch template.

Hypothesis to test FIRST (not yet confirmed — do not build on it): the arm-selection state (`alt_i`) or the
entry dispatch is keyed off a comparison involving `node_ω`, so when `node_ω` is a real statement slot
rather than the arm-glue label the α entry resolves to the last arm instead of the first.

## WHY THIS IS `rsg`

`gener`'s nonterm arm is exactly ingredient 1+2+3:

```icon
"nonterm":  {
   pending := ?\defs[symbol.name] ||| pending | {      <- disjunction, FIRST in arm
      write(&errout,"*** undefined nonterminal:  <",symbol.name,">");
      break
      };
   if *pending > \limit then { ... }                   <- the trailing expression
   }
```

SCRIP takes the LAST arm → prints `*** undefined nonterminal: <s>` and `break`s out of the `while` →
`gener` falls through to its trailing `write()` → **one blank line per call**. With `limit := 1000` that is
`rsg`'s exact signature: **1000 blank lines, 1 distinct value**, vs the oracle's 5000 lines / 1604 distinct
sentences. Reproduced in a standalone harness carrying `gener` verbatim (`/tmp/p/g1x.icn`), which prints the
`undefined nonterminal` message the full program swallows.

## FIX / RE-TEST GATE

After the emitter fix, re-test in this order — each is a one-command check:
1. `c4` minimal repro → `int=1 int=2 iters=3`
2. verbatim-`gener` harness → `he runs.`
3. `rsg` on the 3-line `mini.dat` → `he runs.`
4. `bash scripts/honest_icon_correctness.sh` → **8/8 IDENTICAL** (this closes the LAST bench defect)
5. `bash scripts/test_icon_all_rungs.sh` → must not regress 249/12/32
6. Re-check the FZ-E cluster (`scan1`/`scan2`/`recogn`/`rung36_jcon_*`) — several are plausibly the same
   shape, so the FAIL count may drop by more than one.

⚠ `rsg`'s currently-reported m4 speedup remains **VOID** until it is byte-identical; it short-circuits.
