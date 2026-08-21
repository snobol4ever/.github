# FINDING s189 (HQ) — FISHING THE UNGRADED SUITE: **AN ENTIRE BUILTIN FAMILY IS MISSING**, A SPITBOL GOTO FORM WON'T PARSE, AND `OPSYN` ACCEPTS WHAT THE ORACLE REJECTS

**Date:** 2026-08-20 · **SCRIP:** `28e2122a` (pristine, RT_OPT `-O0`) · oracle live `sbl` · manual `spitbol-docs-master/v37.min`.
**Provenance (Lon, in-chat: *"I want to see some more 2-way IPC/ZSM findings. I love seeing those get caught. Just like fishing."*):** cast the automatic bug finder at `corpus/programs/snobol4/feat/` — 21 self-checking feature programs, **19 of which have no `.ref` and have therefore never been graded by any board**. The finder bit on 10 of 14 run; three survived grading against the live oracle as real defects. **A suite that is never graded is not a passing suite, it is an unopened one.**

## 1 · ⭐⭐⭐ EIGHT SPITBOL REAL-NUMBER BUILTINS DO NOT EXIST IN SCRIP

`f19_real_numbers` — oracle `PASS`, SCRIP `** Error 5 in statement 0 / Undefined function or operation`. One probe per function, `OUTPUT = F(1.0)`:

| function | oracle | SCRIP |
|---|---|---|
| `ATAN` | `0.785398163397448` | Error 5 — undefined |
| `CHOP` | `1.` | Error 5 — undefined |
| `COS` | `0.54030230586814` | Error 5 — undefined |
| `EXP` | `2.71828182845905` | Error 5 — undefined |
| `LN` | `0.` | Error 5 — undefined |
| `SIN` | `0.841470984807897` | Error 5 — undefined |
| `SQRT` | `1.` | Error 5 — undefined |
| `TAN` | `1.5574077246549` | Error 5 — undefined |

**They are a documented family, not eight coincidences** — manual `v37.min:258` lists them together: *"functions- atan, chop, cos, exp, ln, sin, sqrt"*, and `:11547` gives `chp — chop to integral value`. `CHOP` is the truncate-toward-integral function, not a string operation.

⭐ **The REAL type itself is fine** — `3.9 + 1.1` → `5.` and `DATATYPE(3.9)` → `REAL` in both engines. So this is not a numeric-tower gap; it is **eight unregistered functions over a working type**, which is why it is a clean, bounded, high-yield rung rather than an architecture problem. Registration site: the `register_fn("NAME", fn, min, max)` block in `src/runtime/core/core.c` (~line 1780–1832). No codegen, no templates, no pattern machinery.

⛔ **Do not take the probe table as the specification.** SPITBOL's real formatting is its own contract (`LN(1.0)` prints `0.` and `SQRT(1.0)` prints `1.` — note the trailing point, and `&FULLSCAN`-era digit counts); the oracle is the reference for **format** as well as value, and `f19`'s own assertions (`INTEGER(R)` fails on a real, `DATATYPE(R)` is `'REAL'`, `EQ(CHOP(3.9), 3.0)`) are the acceptance test.

⛔ **One probe was too weak to convict and is excluded honestly:** `REMDR(1.0)` errors in the oracle and returns empty in SCRIP, but `REMDR` takes integers — the probe was wrong, not necessarily the engine. Re-probe `REMDR(7,3)` before claiming anything.

## 2 · A SPITBOL GOTO FORM SCRIP CANNOT PARSE — `:<expr>`

`f13_eval_code` — oracle `PASS`, SCRIP fails **at parse time**:
```
snobol4:4: error: parse error: syntax error
scrip: 1 parse error(s) in 'f13_eval_code.sno' — no code generated
```
Line 4 is `:< C >`, transferring into the object built by `C = CODE("CPASS OUTPUT = 'PASS' :(END)")` on line 3. The oracle parses and executes it. SCRIP's SNOBOL4 parser has no angle-bracket goto form at all (grep of `src/parser/snobol4/` finds none).

This is a **front-end gap, not a runtime defect** — the program never reaches code generation, so no amount of pattern/codegen work can reach it. It is also the reason `f13` never appeared on any board: an unparseable program in an ungraded directory is invisible twice over.

## 3 · `OPSYN` IS MORE PERMISSIVE THAN THE ORACLE (SCRIP says PASS where SPITBOL raises ERROR 156)

`f14_opsyn` line 2: `OPSYN('STRLEN', 'SIZE', 1)`.
- **Oracle:** `f14_opsyn.sno(2) : ERROR 156 -- opsyn first arg is not correct operator name` (twice), then continues.
- **SCRIP:** accepts it, `STRLEN('hello')` works, prints `PASS`.

Manual: the three-argument `OPSYN` is the **operator** form (`v37.min:16801–16805` carries its error family, e.g. `err 152, opsyn third argument is not integer`), and `'STRLEN'` is not an operator name — so **ERROR 156 is correct SPITBOL behaviour and SCRIP's acceptance is the divergence**. RULES.md: *SCRIP FOLLOWS SPITBOL SEMANTICS.*

⛔ **This one is a RULING QUESTION, not a bug to fix on sight, and the row says so.** The three-argument function form (`OPSYN(new, old, arity)`) is legal in **CSNOBOL4**, so `f14_opsyn` may simply be a corpus program written in the wrong dialect — in which case the fix is the *program*, not the engine. Two candidate dispositions, and the seat must decide with the manual and a live-oracle probe rather than by taste: (a) SCRIP rejects the 3-arg form when arg 1 is not an operator (matching SPITBOL), and `f14_opsyn` is rewritten to `OPSYN('STRLEN','SIZE')`; or (b) SCRIP keeps the permissive form as a documented, tested extension. **Being stricter can break passing programs — measure the corpus before choosing (a).**

## 4 · METHOD NOTE — TWO INSTRUMENT FAULTS CAUGHT IN THIS SESSION'S OWN HARNESS

1. **An unquoted shell variable manufactured a fake bug.** A comparison loop used `echo $s`, and SCRIP's output contained a `*`, which bash expanded into a directory listing — reported as SCRIP printing `/bin /boot /dev`. Quoting fixed it; the real output was `Error 5`. **A sweep harness is an instrument and gets the same scrutiny as the thing it measures.**
2. **10 of 14 programs "bit" on the finder, and only 3 were real.** A monitor divergence is a *pointer*, never a verdict — most of the ten were trace-level path differences with identical final output, and one (`f18_error_handling`) had a **crashing oracle** (rc=139), where no verdict is possible in either direction. Every claim above is graded by live-oracle output diff, per RULES ASM-DIFF-FIRST: *the tool LOCATES, it never GRADES.*

## 5 · ROWS MINTED

`real-fn-family` (rank 1, the eight builtins) · `goto-code-object-parse` (rank 1, the `:<expr>` form) · `opsyn-3arg-ruling` (rank 2, the permissiveness question). **And a standing one worth more than all three: `feat/` and `parser/` hold 107 programs with no `.ref` — an entire ungraded pond.** Row `ref-the-ungraded-suites` mints refs from the live oracle so these programs can never again fail invisibly.
