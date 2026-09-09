# FINDING 2026-09-09 hq_R — `expr \ N` re-entered after its generator exhausted early keeps a stale counter for exactly one evaluation

**Status:** OPEN, NAMED, NOT CURED. Residual of the cure landed this sitting for the IPL `words()` class
(`flip-ipl-datmerge-tab-move-do-not-restore-pos-when-backtracked-across-a-suspend`). Filed so the remaining
hole is a known quantity rather than a surprise; it is strictly smaller than the defect it is left over from.

## What was cured

`bb_limit`'s counter lived at `drive_value_slot(limit)+16` and was zeroed by `bb_limit_init()` emitted ONCE
per activation, in the procedure prologue (`emit.cpp`, the `for (_li...) if (nodes[_li]->op == IR_LIMIT)`
loop). So a limit expression evaluated a second time inside the same activation resumed with the counter its
previous evaluation left behind. `suspend expr \ 1` inside a `while` — the exact shape of IPL `procs/strings.icn
words()` — therefore yielded on its first evaluation and nothing ever after.

The cure gives the box a fresh-entry reset using the already-granted, previously-unused slot at `+24`
(`limit.pad (unused)` in `zeta_storage.c`, now relabelled `limit.resumed flag`): β sets the flag immediately
before it resumes the generator; α consumes and clears it, and zeroes the counter when it was NOT set.
α cannot zero unconditionally because α is the arrival point for BOTH a fresh evaluation and every re-yield
of the inner generator — the generator's γ targets that same label.

## What is left, measured

The LIMIT box cannot observe its generator conceding. Lowering (`lower_icon.c` `case TT_LIMIT`) builds the
limit with the enclosing ω and lowers the generator against that SAME ω, and `x86_omega()` is a jump to an
external target rather than a box-owned block — so when the generator exhausts BEFORE the limit cuts, control
leaves through the shared ω and the box's β never runs. The resumed flag is then left set, and the next fresh
evaluation consumes it and skips its reset once.

Witness (`wR.icn`), graded against `/home/resources/icon-master/bin/icont`:

```icon
procedure main();
   local i;
   every i := 1 to 4 do { writes("  eval", i, ":"); every writes(" ", (1 | 2) \ 5); write() };
end
```

| eval | oracle | SCRIP before the cure | SCRIP after the cure |
|------|--------|-----------------------|----------------------|
| 1    | `1 2`  | `1 2`                 | `1 2`                |
| 2    | `1 2`  | `1 2`                 | `1 2`                |
| 3    | `1 2`  | `1`                   | `1` ⛔ still wrong    |
| 4    | `1 2`  | (nothing)             | `1 2`                |

The control arm in the same program — a limit that actually CUTS each time, `(1 | 2 | 3) \ 2` — is correct
for all four evaluations after the cure and was wrong from evaluation 2 onward before it.

## Why it was landed anyway

Strict improvement, no regression: every case where the limit itself terminates the evaluation is now right,
and the surviving case was already wrong (worse) before. It is the difference between "wrong from the second
evaluation onward, always" and "wrong on one evaluation after the generator under-delivers".

## The cure, when someone takes it

Give the LIMIT a box-owned ω trampoline that zeroes the counter and clears the flag before jumping to the
shared ω, and route the generator's concede through it — the extra-label-plane mechanism `flat_drive_repalt`
already uses for REPALT (`ra_y`/`ra_t`) is the working precedent in this emitter. That closes the hole
without a flag at all. NOT attempted here: it changes the ω wiring of a node every frontend lowers through,
so it wants its own row, its own control arms and hq_U's co-sign.
