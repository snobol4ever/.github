# FINDING — a call-value resume site reads a handle cell its own alpha never wrote, and segfaults on the garbage

**cfo · 2026-09-08 · row `icon-arizona-jcon-class-conversions-builtins-and-io-fidelity`**
**Trees:** SCRIP `196d19e79` (the crash reproduces on `df7ba0a2b`, the tree BEFORE the `seq` cure landed beside it — it is not caused by that cure) · corpus `af7d27aca` · .github `23812ac1c` · `RT_OPT=-O0`, incremental `make`.

## The one-sentence claim

`rt_call_value_resume_h()` (`src/runtime/by_name_dispatch.c:1069`) dereferences `*hslot` as an
`ICN_OPGEN_t *` and reads `g->magic` after testing only that the pointer is **non-NULL**; when the
beta port of an `IR_CALL_VALUE` box is entered in an activation whose **alpha never ran**, that cell
holds a stale value from an earlier activation rather than the `0` alpha would have written, the
`cmp rax,1` spine discriminator in `bb_call_value.cpp` reads it as a C-window handle, and the load
of `g->magic` takes SIGSEGV.

## The witness — 8 lines, no suite, oracle-clean

`d1.icn`, run with `IPATH=corpus/packages/icon/ipl/procs`:

```icon
link datetime
procedure main()
   write("A"); gen(DateLineToSec, "Friday, September 7, 1984  1:07 pm"); write("B");
end
procedure gen(p, a[]);
   every writes(" ", ((p ! a) \ 25) | "\n");
   return;
end
```

- Arizona `icont`/`iconx`: prints `A`, ` 463410420 `, `B`, rc=0.
- SCRIP mode 3: prints `A`, then **SIGSEGV (rc=139)**.

Backtrace (gdb, `-O0 -g`):

```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff2e9b153 in rt_call_value_resume_h (hslot=0x7fffffbeee40)
    at src/runtime/by_name_dispatch.c:1069
1069  if (g->magic == ICN_OPGEN_MAGIC) { DESCR_t v = icn_opgen_pump(g); ... }
```

## What is and is not required to reproduce

Each of these ALONE does **not** crash — the crash needs the combination:

- `DateLineToSec` called directly, or applied from a list built in `main` with the same
  `((...) \ 25) | "\n"` limitation and alternation: **runs, rc=0** (it returns a wrong value, see below,
  but it does not crash).
- The same `gen(p, a[])` wrapper applied to plain local procedures (`return x+1`, `suspend x | x+1`):
  **runs, rc=0**, output identical to Arizona.

So the trigger is **apply (`p ! a`) of a procedure VALUE, held in a procedure parameter, whose callee
leaves live choice points, resumed through a limitation** — the path where `bb_call_value`'s beta is
reached without its alpha having established `FRQ(H)`.

## Why the cell is stale rather than uninitialised

`bb_call_value.cpp` alpha does write it — `x86("mov", FRQ(H), 0L)` — and the PL arm additionally zeroes
`FRQ(H+8)` with a comment saying that fact "must be established at alpha, not inferred at beta". That
is exactly the invariant this shape breaks: the beta is entered on a re-drive whose alpha did not run in
this activation, so the zero was never (re-)established and the cell still holds the previous
activation's handle. The runtime then trusts it. Two independent halves:

1. **The wiring** lets a beta run without its alpha for an applied call-value with live choice points.
2. **The runtime guard is not a guard.** `if (!hslot || !*hslot) return FAILDESCR;` rejects only NULL.
   A stale non-NULL word passes straight into `g->magic`. Whatever is decided about (1), a resume
   entry point that can be handed a word it did not write needs a validity check it can actually fail.

## How it was found, and the state it explains

Working `ilib` (the last unblocked red in this row). `ilib` links five IPL modules and was recorded on
2026-09-07 as "SEGFAULTS ... the crash is the finding"; measured today it **hangs** (rc=124) at 125
lines on `df7ba0a2b`. The verdict is unstable because it depends on what earlier activations left in
the handle cell: with the `seq` cure in the same sitting (a strictly separate, oracle-checked lowering
fix) the same binary **crashes at line 9** instead. Same defect, different garbage. That instability is
itself the signature — and it means `ilib`'s CRASH/HANG verdict is not a stable measurement of anything
until this is cured.

## Two smaller defects found beside it, recorded so they are not re-derived

- **`DateLineToSec` ignores the parsed date.** `DateLineToSec("Friday, September 7, 1984  1:07 pm", 0)`
  returns `1788825600` (≈ the wall clock at the time of the run) where Arizona returns `463385220`.
  Reproduces standalone with no crash, so it is independent of the above.
- **`bal()` generates one result where Arizona generates two.** `every bal('+',,,"a+b+c")` gives
  SCRIP `2`, Arizona `2 4`. `bal` is one of Icon's five function generators and is **deliberately left
  out** of `icn_call_allow_gen()` in the `seq` cure landed this sitting: marking it resumable while its
  own generation is short turns a wrong-but-finite answer into an **infinite resumption loop**
  (`bal('+',,,"a+b+c") & 7` then yields `7` forever against Arizona's two). Cure `bal`'s generation
  first, add it to the list second, in that order.

## What this blocks

`ilib` cannot be graded honestly until the crash is cured; the row's other reds
(`recogn`/`gener`/`recent`/`sorting` behind row 676, `fncs` behind the record-serial row) are already
blocked elsewhere. This finding is the reason `ilib` is not "one more easy builtin gap": the crash is in
the shared call-value spine, not in the Icon library.
