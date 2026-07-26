# FINDING (2026-07-26) — THE `=s` β SEGV IS AN **EDGE** DEFECT, NOT A PORT DEFECT. BOTH FACES CLOSED.

**SCRIP `43c5837b` (face 1) + `9027445c` (face 2) · pushed · RT_OPT=-O0 · oracle iconx 9.5.25a**

## ⛔ CORRECTION TO THE PRIOR FINDING

`FINDING-2026-07-26-...-SCAN-MATCH-BETA-RESUCCEEDS-...` states:

> SCRIP's β does **not** restore-δ-and-fail. It re-enters as though from α …

**The first sentence is FALSE and cost the fix its first attempt.** Both templates are CORRECT and were
never the bug — verified by reading them:

| template | β body | verdict |
|---|---|---|
| `bb_scan_tab.cpp` L45-47 | `def β; mov r14,[op_off+16]; jmp ω` | ✅ restores δ, fails — exactly ARCH-ICON.md |
| `bb_scan_match.cpp` L47 | `x86_beta_trampoline()` = `def β; jmp ω` | ✅ correct det-leaf |

The defect is the **EDGE THAT NEVER ARRIVES AT β.** The second sentence ("re-enters as though from α") was
right, and is the whole bug.

## THE MEASURED WIRING

`--dump-ir-verbose` on the 6-line repro:

```
13   γ=14  ω=5     LIT_STRING "."
14   γ=15  ω=5     SCAN_MATCH  [13]     <- first conjunct  ="."
15   γ=16  ω=5     SCAN_TAB    [14]
16   γ=17  ω=22@   LIT_STRING "9"
17   γ=18  ω=22@   SCAN_MATCH  [16]     <- second conjunct ="9"
18   γ=19  ω=22@   SCAN_TAB    [17]
22@  γ=15  ω=15    GOTO                 <- THE BACKTRACK EDGE
```

Slot `22@` is the backtrack GOTO from the failing second conjunct. **Both its ports point at node 15 — the
first conjunct's `SCAN_TAB` — as a plain successor reference, i.e. at its α.** Per the FROZEN label model
(`GOAL-JCON-IN-SCRIP.md`), γ/ω are `IR_ref_t` successor pointers to the target's **α**. Re-entering α re-runs
`tab` at the SAME δ, it succeeds again, the second conjunct fails again → unbounded spin. Under
`ZC_FRAME_RSP` each spin pushes ζ cells, so the stack dies: the SEGV. This is exactly consistent with gdb's
repeating `rt_substr(".abc", 1, 1)` (a=1,b=1 — old δ = new δ = 1, the post-dot position, every time).

## ROOT CAUSE — `lower_icon.c` TT_CONJ, the helper defeats the predicate

```c
IR_t * tgt = ω; if (lr >= 0) tgt = (bet[lr] && bet[lr] != ω) ? bet[lr] : val[lr];
γ_to(jn[i], tgt); ω_to(jn[i], tgt);          /* <- downgrades to α */
...
if (is_resumable(S[i]) || icn_tree_is_cursor_mover(S[i])) lr = i;
```

`lr` is selected CORRECTLY — `icn_tree_is_cursor_mover` already covers `=s`/tab/move, and the ICN-CURSOR-BACKTRACK
comment above it states the exact intent ("routes a later operand's failure back through their β"). But
`γ_to`/`ω_to` (L24) retarget to β **only** when `ir_is_generator_kind(tgt)`, and `IR_SCAN_TAB`/`IR_SCAN_MOVE`
are DELIBERATELY excluded from that predicate — correctly, per ARCH-ICON.md's two-family split
(`upto/find/many/bal` are `{*}` generators; `tab/move` are `{0,1+}` cursor-movers). So the edge silently
fell back to `lc_ω_to` = α. **The predicate was right; the writer threw the answer away.**

⚠ **DO NOT "FIX" THIS BY ADDING IR_SCAN_TAB TO `ir_is_generator_kind`.** tab is not a generator; that would
change its semantics everywhere.

⚠ **AND DO NOT GUARD ON `tgt->op`** — my first attempt did, and it silently never fired. **MEASURED:** at
conjunction-wiring time `tgt->op == IR_CALL (6)`, not `IR_SCAN_TAB (57)`; the node is only specialized to
`IR_SCAN_TAB` by a LATER pass, so the dump (post-specialization) shows a tab where lower still sees a call.
Guard on the SOURCE TREE.

## THE FIX (landed, 4 lines)

Track *why* `lr` was chosen; when it was chosen solely as a cursor-mover, force β:

```c
int lr = -1; int lr_cm = 0;
...
if (lr >= 0 && lr_cm && tgt && tgt != ω) { lc_γ_to_β(jn[i], tgt); lc_ω_to_β(jn[i], tgt); }
else { γ_to(jn[i], tgt); ω_to(jn[i], tgt); }
...
if (is_resumable(S[i]) || icn_tree_is_cursor_mover(S[i])) { lr = i; lr_cm = (!is_resumable(S[i]) && icn_tree_is_cursor_mover(S[i])); }
```

## MEASURED RESULT

| gate | oracle | SCRIP before | SCRIP after |
|---|---|---|---|
| 6-line repro, m3 | `N` `done` | **SEGV rc=139** | ✅ `N` `done` |
| 6-line repro, m4 | `N` `done` | **SEGV rc=139** | ✅ `N` `done` (mode-identical) |
| `<-` variant (face 2) | `pos=1` | `pos=2` | ✅ `pos=1` — closed in `9027445c` |
| `test_icon_all_rungs.sh` | — | 249/12/32 | ✅ **249/12/32 — zero regression** |

## FACE 2 — CLOSED (`9027445c`) — WAS THE ONE BLOCKING jtran

The prior finding said "one family, two faces; fix must close both." **This fix closes face 1 only**, and
face 2 is the shape that actually kills the self-host at `lexer.icn:135`:

```icon
if str <- ="." & str ||:= tab(many(&digits)) then ...
```

**MECHANISM (read off the code, not yet gdb-confirmed):** `str <- ="."` is `TT_REVASSIGN`, which IS in
`is_resumable` (L88). So `lr_cm` is 0 by construction and the new arm deliberately does not fire; the edge
goes through `ω_to` → `IR_REV_ASSIGN` IS a generator kind → routes to the **rev-assign's** β. That β restores
the VARIABLE and then exits; it never chains onward into the inner cursor-mover's β, so δ is never restored.
Canonical Icon unwinds BOTH on backtrack.

**NEXT RUNG:** make `IR_REV_ASSIGN`'s β, after restoring the variable, continue into its operand's β when that
operand is a cursor-mover, instead of going straight to ω. Start at the `TT_REVASSIGN` lower arm and
`bb_rev_assign*` — NOT at the conjunction, which is now correct.

## RE-TEST GATE FOR FACE 2
1. `<-` variant → `pos=1`.
2. 6-line repro must STAY `N`/`done` (both modes).
3. `test_icon_all_rungs.sh` must stay 249/12/32.
4. Then re-attempt `SCRIP-jtran ... irgen.icn` → 114 class files.

## SESSION STATE
`icont`/`iconx` 9.5.25a built · oracle `jtran` (17 modules) built · `scrip`+`libscrip_rt.so` -O0 built ·
SCRIP `43c5837b`+`9027445c` **pushed to origin/main**. Java never installed, JVM never run (s121).
Sibling gap noted but NOT fixed: TT_IDX/TT_SECTION rev-assign branch (line ~831, `b5` path) has identical
`if (rbeta)` shape — `t[i] <- ="."` still loses δ restore. Fix = same `icn_tree_is_cursor_mover` guard
or (principled) publish `cx->beta` at cursor-mover construction to close all three sites.
