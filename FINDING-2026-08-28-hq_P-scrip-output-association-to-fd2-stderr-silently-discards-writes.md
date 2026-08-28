# `OUTPUT(.V, ch, '[-f2]')` silently discards every write in SCRIP — no output, no error, rc=0

**Seat:** hq_P (found while building the aspect-2 bracket for the rep-loop demo harness) · **Date:** 2026-08-28
**Lane:** ⛔ **hq_C** — this is a wrong ANSWER (a missing one), routed under the two-HQ interlock, not cured here.

## Minimal witness

```
        OUTPUT(.E1, 3, '[-f2]')
        E1 = 'WITNESS-fd2'
        OUTPUT = 'done'
END
```

| engine | rc | stdout | stderr |
|---|---|---|---|
| scrip `--run` (m3) | 0 | `done` | *(empty)* |
| scrip `--compile` (m4) | 0 | `done` | *(empty)* |
| clean oracle `sbl -bf` | 0 | `done` | `WITNESS-fd2` |

Both modes, identically. The association is accepted, the assignment executes, and the bytes go nowhere.

## Why this one matters more than its size

⛔ **It fails silently and it fails green.** There is no diagnostic, no non-zero exit, and no missing-file
error — the program looks like it ran correctly. A SNOBOL4 program that reports progress or diagnostics on
standard error produces **nothing at all** under SCRIP and **no way to notice**, which is the same
false-signal class as the three defects found tonight (a cure compiled out by a flag, a regen that
regenerated nothing, a Pascal grid agreeing at `reps=0`).

⭐ **Association is not broken in general — only the file-descriptor form.** Verified in the same session:
`OUTPUT(.F1, 4, 'PROBEOUT.txt')` writes correctly in **both** engines. So the defect is specific to the
`-fn` file-descriptor spec, not to `OUTPUT()` association as a mechanism. The manual
(`spitbol-manual-v3.7.txt`, the `–fn` switch) defines fd 0 = standard input, 1 = standard output,
**2 = standard error**.

⚠️ Not investigated here (hq_C's call): whether `-f1` and `-f0` behave, and whether the spec is parsed and
dropped or never parsed at all. The witness above is deliberately the smallest one that shows the divergence.

## Impact on my lane, and how I worked around it rather than waiting

Lon's two-aspect presentation law requires **aspect 2: an in-program bracket** (`elapsed+cpu` read by the
program itself at fixture begin/end). The obvious channel for a bracket is standard error, because it keeps
the measurement off stdout and therefore leaves every committed `.ref` and the whole cross-engine
output-agreement gate byte-identical.

⛔ That channel does not exist in SCRIP today, so the rep-loop harness writes its bracket to a **temp file**
instead — which works in both engines *now*, keeps stdout equally clean, and needs no compiler change.
**The harness is not blocked on this.** Recording it because the next person to reach for stderr from a
SNOBOL4 program will lose an hour to a program that cheerfully prints nothing.

## Bonus, verified while probing — `TIME()` IS NANOSECONDS IN BOTH ENGINES

Calibrated against an external clock rather than assumed from the manual's usual millisecond convention:

| engine | `TIME()` delta | external wall |
|---|---|---|
| scrip m3 | 18,377,668 | 0.02 s |
| clean oracle | 60,197,413 | 0.06 s |

⭐ Both engines agree on the **unit**, which is what makes a cross-engine in-program bracket legitimate at
all. ⚠️ Whether `TIME()` is wall or CPU is **not** settled by this test — both runs are compute-bound, so
the two clocks coincide. The harness therefore reports the bracket **alongside** external rusage rather
than in place of it, and labels it as `TIME()` rather than as "cpu" or "elapsed".
