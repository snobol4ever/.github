# FINDING — a captured number was not a number, because two coercions disagreed about what the value was

**ceo, 2026-09-14. Cure + gate at SCRIP `f36c022c4`. Gimpel 126/132 → 127/132 (`ASM_driver`).**

## The symptom, sixty lines from the cause

`ASM_driver` assembles a small program and prints a listing. Every instruction came out with a **wrong register column** (`0` where the oracle prints `1`) and **two spurious error causes** (`UR`). Nothing in the listing mentions numbers.

## What it actually was

**A pattern capture is a VIEW.** Its descriptor's `.s` points *into* the subject and the length is **carried** in `.slen`, so the captured bytes do not end at a NUL. Three numeric paths read `.s` raw and demanded the number end at `'\0'`:

- `bn_integer` — the dispatcher's `INTEGER`
- `_OPCOERCE` and `_SNOCOERCE` — the macros **every numeric builtin in the dispatcher** goes through

On `AC` captured as `"1"` out of `"START LOAD 1,ONE "`, all three walked past the capture into `",ONE "`, saw a comma where they wanted a terminator, and concluded it was not a number. `ASM.sno`'s `CVTSYM` then took its table path, found no symbol `1` in `SYMS`, and flagged the `U` cause — which is the listing column that was wrong.

This is the project's own law broken in one layer: **a descriptor's length is carried, never measured.** `rt_cstr_d` honours it — `.s` untouched when the byte at `slen` is already NUL, a materialised copy only when it is not — so the common path stays a pointer compare.

## Why it survived, and why the gate holds four paths

**The template arithmetic path already honoured the length.** On the very same value:

| expression | ours (before) | oracle |
|---|---|---|
| `SIZE(AC)` | 1 | 1 |
| `AC + 1` | 2 | 2 |
| `INTEGER(AC)` | **FAIL** | succeeds |
| `REMDR(AC,16)` | **FAIL** | 1 |

Two coercions for one language, **disagreeing about what the value is**, each of them right on its own witness. That is why the gate asserts `INTEGER`, `REMDR`, the numeric relations *and* arithmetic rather than the one builtin that reported the problem: a gate holding only `INTEGER` would let the next builtin re-acquire this in silence. Expectations are cut from `sbl -bf`; fail-once proven by removing the cure — **2 of 2 modes red**.

`_INTEGER_` and `_REAL_` in `core.c` carried the same latent defect on the slow path and were cured with it. No per-op filter.

⭐ This is the **sibling** of `test_gate_sno_cset_from_a_string_view_uses_its_length` — same view, same flattening, different consumer. That one's note already recorded that two Gimpel programs had been **misattributed to a stack-overflow class** by this shape. A third consumer existed and nothing was looking for it.

## Control arms (shared dispatcher)

Icon master **826/826** both modes · SNOBOL4 master **1968/1980** unchanged, crash=0 · Prolog master **542/563** unchanged · `make preflight` 49 arms, 0 red.

## One process note

The explanation above was first written as two comments **in the C**. `strip_comments.py` reddened preflight and I removed them. The law is zero comments; the reasoning belongs in the gate header, the commit and this file — and the instrument caught it rather than a reader noticing later.
