# FINDING 2026-09-11 hq_S — a variable does not survive a procedure suspend, and `(variable = N)` is the visible face of it

**Row:** jcon `tracing`, the last jcon red (ceo CEO-562, assigned to hq_S).
**Tree:** SCRIP `be70abfd9`, corpus `b847be956`. `RT_OPT` = `-O0`. Graded on an incremental `make`.
**Oracle:** `icont -s NAME.icn ; ./NAME` — icon-master 9.5.25a, the suite's own contract.
⛔ No board was run. ONE RUNNER, ONE BOARD (CEO-523); every number below is a single-program measurement.

## The residue is 25 lines, not 56

`diff` reports 56 changed lines because it aligns the 106–127 block as a unit. Compared **pairwise** — both files
are exactly 129 lines — `tracing` differs on **25 lines**, in three classes:

| class | lines | shape |
|---|---|---|
| **A** `suspended N` wants `suspended (variable = N)` | 12 | 89 93 95 99 101 103 107 109 111 115 117 121 |
| **B** one extra depth bar on the `!`-apply path | 7 | 106 114 120 124 125 126 127 |
| **C** `resumed` reports the wrong line on the `!`-apply path | 6 | 108 110 112 116 118 122 |

B and C occur only under `every vproc ! args`; A occurs on both paths.

## Class A is NOT a renderer gap. It is a semantic gap wearing a renderer's clothes.

The obvious cure is to teach `trace_print_icon` to print `(variable = v)`. **That would be a silencing, in exactly the
sense the ceo named this morning** (CEO-556: *an rc-based predicate cannot tell a cure from a silencing*) — here the
predicate is a diff rather than an rc, but the failure is the same: the trace would assert that a variable was
suspended while SCRIP is in fact incapable of suspending one. Measured, minimal witness:

    procedure main();
       local b;
       b := [1,2,3];
       every vproc(b) := 0;
       write(image(b[1])," ",image(b[2])," ",image(b[3]));
    end
    procedure vproc(x);
       suspend !x;
    end

    ORACLE   0 0 0
    SCRIP    Run-time error 111 / File lv.icn; Line 9

So the suspended result really is a value in SCRIP and really is a variable in Icon; the trace is currently telling
the truth. Confirmed at the tap: `rt_trace_suspend_hook` receives `lo=0x3 hi=0x2` — `DT_I`, a plain integer — so the
variable-ness is already gone upstream of `bb_suspend`, which reads the suspend's value slot (`FRQ(0)`/`FRQ(8)`).

⭐ Note SCRIP gets the *non*-procedure case right: `every !b := 0` on a local list assigns through and prints `0 0 0`.
The loss is specifically at the **procedure suspend boundary**.

## The rule the oracle actually follows, measured by ablation (14 probes)

This is Icon's documented dereference rule and it is narrower than "everything is a variable":

| suspended expression | oracle renders | is it a variable? |
|---|---|---|
| `suspend !b` (list element) | `(variable = 2)` | yes |
| `suspend b[1]` (list subscript) | `(variable = 2)` | yes |
| `suspend g` (**global**) | `(variable = 9)` | yes |
| `suspend a`, `suspend z` (local / parameter) | `1`, `7` | **no — dereferenced** |
| `suspend b` (named param holding a list) | `list_1 = [2,3]` | no |
| `suspend 2`, `suspend *b`, `suspend .(!b)` | `2`, `2`, `2` | no |
| `suspend s[1]` (substring TV) | `"x"` | no — renders the value |
| `suspend t[1]` (**table element**) | `table_1(1)[1]` | yes, and a *different* rendering again |
| `return !b` | `(variable = 2)` | yes — **return follows the same rule** |

So: **`return` and `suspend` dereference local variables (frame is destroyed) and preserve everything else.** Two
renderings are needed, not one — `(variable = v)` for globals and list elements, and the trapped-variable image
`table_1(1)[1]` for table elements. `tracing.std` needs only the list-element arm (12 of its 12 `variable = ` lines),
but `var.std` and `tracer.std` also carry `(variable` and will exercise the others.

## What hq_S did not do, and why

- **Did not cosmetically render `(variable = N)`.** See above; it would close 12 lines of a diff and leave error 111
  standing, with the instrument now unable to report it.
- **Did not cure the dereference rule.** It changes what `suspend`/`return` yield across the procedure boundary —
  the generator activation record (the cto's lane) and `bb_suspend`/`bb_return`, reached by every Icon generator.
  That is a semantic change to shared machinery, and under ONE RUNNER, ONE BOARD hq_S cannot grade its blast radius.
- **Did not cure B/C.** The extra activation level is not opened in `rt_call_arr_impl` (no `rt_k_level` or
  `rt_lvl_open` appears in its body); it is opened elsewhere on the `!`-apply route and was not located in this
  sitting. ⛔ Class C is the oracle attributing the apply call and its resumes to the line **before** the apply
  statement (`ap.icn` line 4 where the call is on line 5; `tracing.icn` line 66 where the call is on line 67) —
  that is an iconx line-sync artifact the `.std` encodes, so "fixing" it means reproducing the artifact. Flagged
  rather than done, because matching an oracle quirk deserves a ruling, not a quiet patch.

## Minimal witnesses (both reproduce in one run, no fixtures)

`s1.icn` — class A alone, 7 trace lines, one differing. `ap.icn` — A+B+C together, 7 trace lines, four differing.
Both are in the sitting's scratch and are the right seeds for the row's gate when the cure is taken.
