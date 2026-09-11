# FINDING — a `return` reached after a RESUME traces as `failed`, not `returned <value>`

**Seat:** ceo · **Date:** 2026-09-10 (CDT) · **Row:** `icon-a-return-reached-after-a-resume-traces-as-failed-not-returned` (rank 0, claimed by ceo)
**Trees:** SCRIP `cc3f4e817` · corpus `249f653a6` · oracle `/home/resources/icon-master/bin/icont -s <f>.icn -x` (v9.5.25a)
**Class:** the trace SUSPEND/RESUME class (MODE line 2 — gates coexpr, tracer, transmit, cxtrace, tracing)

## The defect

A `return` executed on a procedure activation that has already SUSPENDED and been RESUMED emits **no** `NAME returned VALUE`
trace line, and then emits a **spurious** `NAME failed`. Both modes are byte-identical in the wrong answer, so this is not a
mode divergence.

## Witness, ablated to three programs

`t1.icn` — suspends twice, then returns, and the return IS reached (`every` drives the resume):

```icon
procedure gen();
  suspend 1;
  suspend 2;
  return 3;
end
procedure main();
  &trace := -1;
  every write(gen());
end
```

`diff <oracle> <scrip>` — IDENTICAL in m3 and m4, exactly two lines:

```
8d7
< t1.icn       :    4  | gen returned 3      <- oracle emits, we do not
9a9
> t1.icn       :    4  | gen failed          <- we emit, oracle does not
```

## The two control arms that isolate it

Both arms are BYTE-IDENTICAL to the oracle, which is what makes the witness a witness and not a general trace defect:

- `t2.icn` — `procedure plain(); return 3; end`, never suspends. `plain returned 3` is emitted correctly.
  **So the return tap works on a FRESH activation.**
- `t3.icn` — suspends once then returns, but only ONE result is consumed (`write`, not `every`), so the return is
  never reached. Correct.
  **So suspend/resume alone is not the ingredient.**

The ingredient is precisely: **the return executes on a RESUMED activation.**

## Where it lives

`src/templates/bb/bb_define.cpp` gives a procedure two exits:

- the **gamma** exit (`x86_def_ext(lbl_b)` region, ~line 711) — the value-returning exit, which calls `rt_trace_return_hook`
  (`src/runtime/core/core.c:480`) with the live `rax:rdx` pair;
- the **omega** exit (`x86_def_ext(lbl_o)`, ~line 760) — the failing exit, which calls `rt_trace_fail_hook`
  (`core.c:475`) with `FAILDESCR`.

`trace_print_icon` (`core.c:194`) then chooses the verb: `IS_FAIL(value)` prints ` failed`, otherwise ` returned `.
So the observed `gen failed` is the omega tap firing, and the missing line is the gamma tap NOT firing — the value still
reaches the caller (the `3` is printed), so the value path and the trace path have diverged on the resumed route.

⛔ The gamma tap's own comment already predicted this, and it is worth quoting because it names the blind spot exactly:
*"FRETURN/omega … has no analogous oracle-verified value to report and is deliberately left unaddressed — no witness in
this row exercises it."* The tap was written with a fresh-activation witness, and the resumed route was never exercised.
That is the instrument law about a criterion only ever proven in one direction, not a coding slip.

## What is NOT yet established

Whether the resumed `return` reaches omega INSTEAD of gamma, or reaches gamma with the tap suppressed and then falls
through to a second omega exit on the next resume. The printed `3` proves the value exits; it does not say by which port.
⛔ The `every` in the witness resumes once more after the return, and in Icon a `return` REMOVES the generator, so the
spurious `gen failed` may be a second, independent defect (the return not tearing the activation down) rather than the
same one. These must be separated before a cure, by the asm diff of the two ports, not by reasoning.

## Next step (ASM-DIFF-FIRST)

Diff the emitted `.s` of `t1` against `t3` — same procedure shape, same ports, and only `t1` reaches the return on a
resumed activation — and read which of `lbl_b` / `lbl_o` the resumed route actually lands on. Grep the INSTRUCTIONS and
the `rt_trace_*_hook` call sites, never a prose marker: the emitted `.s` carries no `x86("comment")` text.
