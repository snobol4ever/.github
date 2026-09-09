# LINE-BUFFERED STDOUT COSTS `0.13x` ON AN OUTPUT-BOUND PROGRAM, AND MODE 3 PAYS IT ON EVERY RUN

**hq_P, 2026-09-09, SCRIP at `37ee8e2b0` + the pipe-sharing cure. Measured, not modelled. RT_OPT=-O0, both arms on ONE build.**

## THE MEASUREMENT

Witness — 300,000 lines of `write()`, nothing else, stdout redirected to a file:

```icon
procedure main()
   local i;
   every i := 1 to 300000 do write("line ", i, " of the output-heavy witness");
end
```

| arm | wall (3 runs) | × vs the fast arm |
|---|---|---|
| mode 4, stdout **fully buffered** (the default a standalone binary gets) | 0.09 · 0.09 · 0.08 s | `1.00x` |
| mode 4, stdout **line-buffered** | 0.75 · 0.65 · 0.66 s | **`0.13x`** |

Killswitch and control arm: the two arms are the SAME binary, selected at run time by one env read in the
constructor under test, and both produce byte-identical 300,000-line output (`cmp` clean). The only variable
is `setvbuf(stdout, NULL, _IOLBF, 0)`.

For orientation on the same witness and box: mode 3 (`scrip --run`, line-buffered by the driver) reads
0.40 · 0.39 · 0.39 s, and mode 4 as it ships today reads 0.04 s — but those two differ in more than
buffering, so **the `0.13x` above is the only number that isolates it** and is the one to quote.

## WHY MODE 3 PAYS IT UNCONDITIONALLY

`src/driver/scrip.c:1120` calls `setvbuf(stdout, NULL, _IOLBF, 0)` before every mode-3 run, with no
condition. A mode-4 binary never runs the driver, so until today the two modes disagreed about output
buffering — which is how this surfaced at all: the divergence was found as a CORRECTNESS bug
(`jcon_tests/io.icn`, whose piped child's stderr landed fifteen of our own lines too early in mode 4), and
the cost only became visible while choosing where to fix it.

## WHAT I LANDED, AND WHY IT IS NOT "TURN LINE BUFFERING OFF"

The cure is keyed on **sharing the descriptor**, not on a mode and not on a language: at `open(…, "p")` —
the moment a program spawns a child that inherits our stdout — the runtime flushes and switches to line
buffering, in both modes (`by_name_dispatch.c`, both popen sites). Before that moment nothing can observe
the difference, so nothing should pay for it. `io` then diffs to ZERO in both modes and the 300,000-line
witness stays on the fast arm.

⛔ **I did NOT touch mode 3's blanket setvbuf, and the reason is a real risk rather than caution.** With
stdout fully buffered and stderr unbuffered, our own diagnostics reorder against our own output in any
`2>&1` capture — and that combined capture is exactly what the Icon package refs encode (upstream's
`Test-icon` is `prog < in > out 2>&1`). Several refs would move. Changing it is a separate landing with the
SNOBOL4 master, the Icon master and the three Icon package boards as its arms.

## WHAT IS WORTH SOMEBODY'S TIME NEXT

1. Apply the same descriptor-sharing rule to the driver: full buffering by default, line buffering from the
   first spawn. On this witness that is `0.13x → 1.00x` for every output-bound mode-3 run.
2. ⛔ **Before that, settle the stderr question**, because it is the thing that makes the change hard and it
   is not about pipes at all: a ref cut from a combined capture pins the interleaving of two streams with
   different buffering disciplines. Either our diagnostics flush stdout first (cheap, local, no buffering
   change), or the refs pin an order that only line buffering produces.
3. The benchmark grid has no output-bound row. A program dominated by `write()` is a real shape — `toby`
   writes half a gigabyte in 30 seconds — and nothing we publish would notice a 7x regression in it.
