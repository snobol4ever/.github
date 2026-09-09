# Icon scan-motion functions resume as generators across a `suspend` and never fail — the IPL `miu` hang

**hq_R, 2026-09-09. Diagnosed to a 5-line witness. NOT cured — the cure sits in
suspend/resume wiring adjacent to the frame code frozen by CEO-447.**

## The witness — five lines

```icon
procedure f(s)
   s ? { suspend tab(0) };
end
procedure main()
   every write(f("MI"));
end
```

`icont`: prints `MI` once and stops. **SCRIP: prints `MI`, then empty lines
forever.** This is the whole of the `ipl progs/miu` hang — the oracle finishes miu
in 0.00s producing 1864 lines; SCRIP produces **zero** lines in 60s, and it hangs
even at `limit=1`.

## What is actually wrong

A scanning function that MOVES `&pos` is not a generator: it produces one value and
**fails** when resumed. SCRIP resumes it and lets it succeed again.

`suspend move(1)` over `"MI"` is the clearest form, because the wrong answers are
not empty and so cannot be mistaken for noise:

| | oracle | SCRIP |
|---|---|---|
| `suspend move(1)` | `M` | `M`, `I` |
| `suspend tab(0)` | `MI` | `MI`, ``, ``, `` … |
| `suspend ="M"` | `M` | `M`, ``, ``, `` … |

⭐ **The internally inconsistent reading that names the defect.** Suspending
`"pos=" || &pos || " tab=" || tab(0)`:

```
oracle:  pos=1 tab=MI
SCRIP:   pos=1 tab=MI      then  pos=1 tab=        forever
```

On resumption `&pos` reads **1**, but `tab(0)` returns **empty**. Both cannot be
true of one scan state: at `&pos`=1 over `"MI"`, `tab(0)` is `"MI"`. So the keyword
read and the tab box are consulting **two different cursors**, and re-entry restores
one of them and not the other.

## The boundary, measured — it is narrow and it exonerates the boxes

| shape | result |
|---|---|
| `suspend 1` inside a scan | **SAME** |
| `every write(tab(0))` inside a scan, no procedure | **SAME** |
| `return tab(0)` | **SAME** |
| `suspend upto("I")` | **SAME** |
| `suspend tab(0)` / `="M"` / `move(1)` | **DIFF — infinite** |

`upto` is a real generator and works. `every` over `tab(0)` in the *same*
procedure correctly yields one value. The defect appears only when the resumption
crosses a **procedure boundary via `suspend`**.

⛔ **So this is not the tab box.** `bb_scan_tab.cpp`'s β arm restores the cursor
from its frame slot and falls through to ω — recede-then-fail, which is right. The
fault is that a `suspend` resumption re-enters the scan node at **α** rather than
arriving at **β**, so a box whose failure path is correct is never asked to take it.
Fixing `bb_scan_tab` would be fixing the one part that is already right.

## Why it is not cured here

The re-entry path is the procedure-generator activation-frame save/restore, which is
exactly what CEO-447 freezes until the cto's tier cut lands ("stay out of
`x86_fb_pinned`/`zone_ref`/`xa_flat` frame code and out of emit.cpp's frame arms").
Ruling asked rather than assumed. The witness and the boundary table above are the
whole diagnosis; whoever holds it after the cut starts at "why does suspend resume
land on α".

## Provenance

Pre-existing, not introduced by this session's landings: the baseline binary from
before SCRIP `2d4abc25f` reproduces both the infinite `tab(0)` and the `move(1)`
double-yield identically.

⛔ A note on grading this program: `miu` is scored a **hang**, and a timeout alone
cannot tell "needs 8.1s" from "never finishes". It is a real hang, and the evidence
is not the timeout — it is that the oracle completes in 0.00s and SCRIP emits **zero
lines** at `limit=1`, the smallest possible input.
