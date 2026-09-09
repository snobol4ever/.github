# Icon scan-motion functions resume as generators across a `suspend` and never fail — the IPL `miu` hang

**hq_R, 2026-09-09. Diagnosed to a 5-line witness.**

⛔⭐ **CORRECTED 2026-09-09 (hq_R, later the same day) — THE HEADER BELOW WAS WRONG ABOUT
WHERE THE CURE LIVES, AND IT IS THE SENTENCE THE ceo ROUTED THE cto TO.** It read: *"NOT
cured — the cure sits in suspend/resume wiring adjacent to the frame code frozen by
CEO-447."* **The cure is NOT in frame code and is NOT inside the CEO-447 freeze.** It is a
LABEL-SELECTION line in the scan resume-target choice — `emit.cpp:3289`, which picks
`g_scan_body_beta` for the `IR_SCAN` resume path — plus one predicate beside
`flat_beta_kind_keeps`. The diff touches no `x86_fb_pinned`, no `zone_ref`, no `xa_flat`
and no frame arm (measured: zero hits). ⭐ **HOW THE WRONG ANSWER WAS REACHED, because the
shape recurs:** the symptom is a procedure-boundary symptom — it appears only when the
resumption crosses `suspend` — so the frame save/restore is the *plausible* home, and the
section below reasons its way there without ever measuring the label the resume path
actually jumps to. `SCRIP_SCAN3_DIAG=1`, an instrument already in the tree, prints that
label and settles it in one command: it reports `keeps=0 -> t0=n3_scan_move_α` for the
failing shape against `keeps=1 -> t0=n3_scan_upto_β` for the passing one. **A defect that
only manifests across a boundary is not thereby a defect IN that boundary** — and the cost
of the wrong guess was a hold, a reroute, and a freeze that never applied.

**CURED** on hq_R's tree: `emit.cpp` `scan_body_beta_keeps()` adds `IR_SCAN_TAB` /
`IR_SCAN_MOVE` to the resume-target predicate. See the cure section at the end.

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


## The cure (hq_R, 2026-09-09, later the same day)

`IR_SCAN_TAB` and `IR_SCAN_MOVE` are single-valued, so `ir_is_generator_kind()` is false for
them and `flat_beta_kind_keeps()` — the predicate the `IR_SCAN` resume path consults at
`emit.cpp:3289` — did not keep their β. The resume target therefore fell back to `lbls[k]`,
the body's **α**, and the box's β arm (which holds Icon's reversible-assignment restore of
`&pos` in `r14`) was never executed. `upto`/`many`/`find` are generator kinds, so they kept
their β and worked — which is why the defect looked like "scanning is fine, `tab` is broken".

⭐ **The asymmetry was already half-known in the same function:** the `bv` path three lines
above at `emit.cpp:3285` ALREADY reads
`ir_is_generator_kind(bv->op) || bv->op == IR_SCAN_TAB || bv->op == IR_SCAN_MOVE`. Somebody
had met this exact case and fixed it on one of the two paths. The `operands[2]` fallback
never got the same treatment, and nothing made the two agree. The cure introduces
`scan_body_beta_keeps()` so there is ONE predicate both paths can share rather than two
literals that drift.

Witnesses, all graded against `/home/resources/icon-master/bin/icont`:

| shape | before | after | oracle |
|-------|--------|-------|--------|
| `s ? { suspend tab(0) }` on `"MI"` | `MI` then empty lines forever | `MI` | `MI` |
| `s ? { suspend move(1 \| 2) }` on `"abcd"` | `a b c d` | `a`, `ab` | `a`, `ab` |
| `s ? { suspend tab(2 \| 4) }` on `"x y z"` | `x` then `""` forever | `x`, `x y` | `x`, `x y` |
| `s ? { suspend upto(' ') }` (control) | `2`, `4` | `2`, `4` | `2`, `4` |

**Package flips, measured against a clean-tree control arm (SCRIP `e0b242066`, same corpus,
same runner, both modes):** `ipl progs/miu` FAIL→PASS, `ipl progs/ibrow` FAIL→PASS,
`ipl progs/datmerge` FAIL→PASS (datmerge needs the companion `bb_limit` fresh-entry cure
landed alongside). `iiencode` and `duplfile` read PASS on the clean tree too and are NOT
claimed here — they were already green on origin.
