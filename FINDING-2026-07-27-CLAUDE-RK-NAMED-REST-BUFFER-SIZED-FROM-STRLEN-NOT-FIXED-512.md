# FINDING-2026-07-27-CLAUDE-RK-NAMED-REST-BUFFER-SIZED-FROM-STRLEN-NOT-FIXED-512.md

## Session: s2026-07-27 · Claude Sonnet 4.6 · GOAL-RAKU-BB · RAKU-100 `*%h` SLURPY_NAMED rung

## Summary

`by_name_dispatch.c`'s named-rest collector buffer was sized at a fixed **512 bytes per named pair**.
`to_cstring` returns the descriptor's own pointer for STRING (its `VARVAL_fn` tail), so the
`kb[128]`/`vb2[256]` scratch buffers do NOT bound `strlen(k)`/`strlen(v)`. A named value longer
than ~510 bytes overwrites past the allocated workspace block — silent corruption via the
bump-allocator's mapped free space, no crash.

## A/B proof (same program, same input — 20,000-char named value)

| build | `%h{'k'}.chars` |
|---|---|
| unfixed (512/pair) | **526** — truncated at the allocation boundary |
| fixed (measured) | **20000** — correct |

No fault, no stderr. The next `rt_ws_alloc` call `memset`s the overwritten region to zero,
erasing hash content silently.

## Root cause

```c
/* BEFORE (defective) */
size_t hcap = 1; for (int i = 2 + npos; i + 1 < nargs; i += 2) hcap += 512;
```

`to_cstring` definition (`by_name_dispatch.c:338-342`):
```c
static const char *to_cstring(DESCR_t v, char *scratch, size_t scap) {
    if (IS_INT_fn(v))  { return itos((long long)v.i, scratch, scap); }
    if (IS_REAL_fn(v)) { return rtos(v.r, scratch, scap); }
    const char *s = VARVAL_fn(v); return s ? s : "";   /* <-- STRING: returns own pointer, never truncates */
}
```

Only INT and REAL use the scratch buffer. A STRING descriptor bypasses it entirely.

## Fix

```c
/* AFTER (correct) */
size_t hcap = 1;
for (int i = 2 + npos; i + 1 < nargs; i += 2) {
    char kb0[128], vb0[256];
    const char *k0 = to_cstring(args[i],     kb0, sizeof kb0);
    const char *v0 = to_cstring(args[i + 1], vb0, sizeof vb0);
    hcap += (k0 ? strlen(k0) : 0) + (v0 ? strlen(v0) : 0) + 2;
}
```

Buffer is now measured from the real strings before the copy loop.
Over-estimates by params that later bind to a declared name — safe.

## Misattribution caught and corrected

First hypothesis: a 2MB named value segfaulted therefore the overflow faults.
Negative control: a 2MB string literal (no slurpy, no hbuf) segfaulted identically.
Conclusion: that fault is a **pre-existing string-size limit** unrelated to this bug.
The correct proof is the readback A/B above; the segfault was confounding.

## Generalizable lesson

Any allocation sized with a fixed per-item budget that later calls `to_cstring` and
`memcpy(strlen(...))` is defective if STRING descriptors are possible inputs.
The fix pattern: **measure before allocating**; one pre-pass computing actual lengths,
then allocate, then copy.

## Rung context

This finding is part of the `*%h` SLURPY_NAMED rung (`RAKU-100`).
SCRIP commit: `6defd71a` (post-rebase hash on origin).
Watermark after: m3 719/0, m4 719/0.
