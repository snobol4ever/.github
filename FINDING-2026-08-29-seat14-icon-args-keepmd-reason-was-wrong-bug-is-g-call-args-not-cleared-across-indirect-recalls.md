# FINDING — `rung36_jcon_args`'s KEEP.md reason is wrong; the real defect is a stale shared arg-staging buffer on indirect recall

Row `tests-consolidate-icon` · seat14 · 2026-08-29

⛔ **`tests/icon/KEEP.md`'s `rung36_jcon_args` entry says: "reads command-line arguments the harness has
no mechanism to supply... a harness capability gap, not a SCRIP bug." This is wrong on its own terms —
the file never reads command-line arguments.** `main()` in `rung36_jcon_args.icn` is declared
`procedure main();` — zero parameters. Its own header comment is "test various numbers of args," and the
body only ever calls its own local procedures `p0`..`p12` (via a list, `(!plist)(...)`) with 0–12
*literal* arguments — it has no dependency on argv, `.stdin`, or any external input at all.

## Measured: it runs to completion, no crash, no missing input

`./scrip rung36_jcon_args.icn < /dev/null` → **rc=0**, produces all 447 lines the `.expected` file has —
but ~140 of those lines are wrong. Every wrong line is a call where a formal parameter was **omitted**
(fewer actual args than the procedure declares); `.expected` shows the missing tail as `~` (Icon's
null-marker in this witness's own `note` helper: `writes(\e | "~", " ")`), SCRIP instead prints a stale
leftover value in that slot (e.g. `p2 1 1` where `.expected` has `p2 1 ~`; the very first block, called
with zero args each, prints `p1 list`, `p2 list list`, ... instead of `p1 ~`, `p2 ~ ~`, ...). This is a
real correctness bug, not a harness gap — the file needs no new harness capability to test at all.

## Root-caused, not guessed at: three minimal repros isolate the exact trigger

1. **Direct, named, repeated calls with a shrinking arg count are CORRECT:**
   ```
   procedure p2(a,b); write(image(a), " ", image(b)); end
   procedure main(); p2(1); p2(); end
   ```
   → `1 &null` then `&null &null`. Correct both times.

2. **Indirect call through a list element (`(!plist)(...)`), called ONCE, is also CORRECT:**
   `plist := [p2]; every write((!plist)());` → `&null &null`. Correct.

3. **Indirect call through a list element, called TWICE with a SHRINKING arg count, is WRONG:**
   ```
   plist := [p2];
   every write((!plist)(1));   # -> 1 &null (correct)
   every write((!plist)());    # -> 1 &null (WRONG -- expected &null &null)
   ```
   The second call's omitted parameter `b` silently keeps the first call's value instead of reading as
   unbound. Reproduces deterministically, confirmed twice.

**Conclusion: indirection is required to trigger it, and the trigger is specifically "a later call
supplies fewer arguments than an earlier call did."** Direct calls are unaffected regardless of
call-count or arg-count changes.

## Located: `src/runtime/by_name_dispatch.c`, three call sites, same pattern

`rt_call_arr`'s registered-name branch (`:905`), `rt_call_value_gen_h`'s registered-name branch (`:919`),
and `rt_call_value_spine_prep` (`:945`) each stage the current call's arguments into the SAME shared
global buffer the same way:
```c
for (int k = 0; k < n && k < 64; k++) g_call_args[k] = argv[k];
```
This writes only indices `[0, n)` — the number of arguments the *current* call actually supplies — and
never clears anything at or past index `n`. If an earlier call into this same shared buffer (to this
procedure or, plausibly, any other routed through the same three sites — not tested beyond the
single-procedure case above) left values in indices the current call doesn't overwrite, whatever binds
the callee's formal parameters downstream reads those leftover descriptors instead of treating the
unsupplied tail as unbound. `g_call_args[]` is an existing global (`extern DESCR_t g_call_args[];`);
this finding does not touch it or propose a fix — flagging the fan-in for whoever owns the cure, since
the array is shared across all three of these dispatch paths, not scoped per-call.

**Why direct calls are unaffected — confirmed empirically, not traced further:** `bb_call.cpp` /
`bb_call_fn.cpp` (the by-name-at-compile-time paths) don't reproduce this under repro #1 above, so they
evidently wire arguments some other way consistent with this project's Byrd-box compile-time-wiring
design, rather than funneling through `g_call_args[]`. Which exact mechanism, not read.

**Not attempted here** — out of `tests-consolidate-icon`'s lane (suite conversion, not runtime
bug-fixing), same discipline this row has applied to every other bug it has found (`proto`, `scan1`,
`level`, `kwds`/`subjpos`, `scan`/`upto`). `rung36_jcon_args.icn` stays loose, **not** KEEP.md'd as a
permanent exclusion (it is a bug that could still convert once cured, not a design choice) — `tests/icon/
KEEP.md`'s entry corrected to this characterization in the same push as this FINDING. Mailed `hq_C`
(`icon-args-stale-g-call-args-on-indirect-recall`).
