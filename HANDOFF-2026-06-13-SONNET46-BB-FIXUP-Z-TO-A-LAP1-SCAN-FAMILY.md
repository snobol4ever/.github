# HANDOFF 2026-06-13 — Sonnet 4.6 — BB-FIXUP Z→A Lap 1 (scan family)

## Session identity
Model: Claude Sonnet 4.6 · Goal: GOAL-BB-FIXUP-Z-to-A.md · Attended by Lon (context checks each turn, "Continue" ×3)

## Repos at handoff
SCRIP @ b063b07 (local==origin)
.github @ 256cd7df + this commit (local==origin)

## Cursor at handoff
`bb_scan_bal.cpp` — Z→A ring, lap 1

## Work completed this session — 7 cursor stops

| File | Violations before → after | Key conversions | Commit |
|---|---|---|---|
| `bb_scan_tab.cpp` | 2→1* | CV6 substr_fp local→inline cast, over_col→tab_admit() R2-KEEP static | b61d7a8 |
| `bb_scan_stmt.cpp` | 17→9 **[S]** | CV6 5 locals→inline + scan_lbl→static helper; medium_any=4 + rp=5 BLOCKED | 47b1f90 |
| `bb_scan_pos.cpp` | 0 already CLEAN | — | — |
| `bb_scan_move.cpp` | 1→0 CLEAN | CV6 substr_fp local→inline cast | 9756566 |
| `bb_scan_many.cpp` | 3→0 CLEAN | CV6 strchr_fp→inline; CV2 ro_load_q→ROQ + ro_seal_str→def/.quad/label/.string | 0883967 |
| `bb_scan_match.cpp` | 3→0 CLEAN | CV6 memcmp_fp→inline; CV2 same bypass decomposition | 4fb0076 |
| `bb_scan_find.cpp` | 2→2* | over_col→find_admit() static; rp 1→2 composition change, all sanctioned | b063b07 |

*residuals = counter-scope-trio sanctioned (R2-KEEP static/FOR-lambda returns per 38th/40th-run standing verdict)

## [S] flags raised this session

**bb_scan_stmt.cpp — ONE-IR-ONE-LOGIC violator.** Two emission strategies crammed in one
template, MEDIUM-selected: TEXT arm → rt_scan_lit (rip-relative literal fast path, valid
both media); BINARY arm → rt_scan (graph-pointer x86_load_ro with "??" TEXT label = TEXT-broken
by construction). The medium split extends INTO the driver: emit_bb.c flat_drive_scan_stmt
line 2068 has its own MEDIUM_TEXT branch routing to flat_drive_scan_native. The split is
IR_SCAN → IR_SCAN_LIT + IR_SCAN_GRAPH at LOWER/driver, NOT template-local. medium_any=4 and
rp=5 cannot clear until this pins. Design NOT pinned — needs Lon/coordinated session.

## Proof standard maintained
- C2 asm-identity: bbN/RESOLVE/.LcallN-normalized A/B diff EMPTY for every code-touching stop
  (tab/stmt/move/many/match/find — each with its box LIVE in the probe .s)
- Probes used: tab(6), SNOBOL `S "X" = "Y"` scan, move(5), many('a'), match("hello"), find("XYZ")
- C3 floors held every commit: smoke all-modes 2/2 · icon m2 12/12 HARD · prolog m2 5/5 HARD
  m3=m4 5/5 · bin_t 0 · sno_pat_reg HARD (TIER 1+2) · handencoded 0 · vstack 3
- icn_scan gate: 8 pre-existing FAILs (tab_upto/upto_oneshot/find_oneshot/eq_match_*/augop_*) —
  verified identical on stashed baseline, NOT introduced by this session, untouched per law 5

## Recurring patterns confirmed this lap (for the next session)
1. **fp-cast inline:** `uint64_t X_fp; { T (*fp)(...) = F; X_fp = ... }` two-liner →
   `(uint64_t)(uintptr_t)(void*)F` (or with explicit fn-ptr cast for overloaded names like
   strchr/memcmp) directly in the x86("call",...) operand. Clears lv=1 every time.
2. **bypass pair decomposition:** `x86_ro_load_q(reg, n)` → `x86("mov", reg, ROQ(n))`;
   `x86_ro_seal_str(n, lit)` → `x86("def", L(n)) + x86(".quad", LS(n), lit) +
   x86("label", LS(n)) + x86(".string", lit)`. Byte-identical by construction (the .quad
   (sym,str) arm bakes the lit pointer in BINARY; .string is BINARY-empty). Verified
   asm-diff EMPTY on scan_many + scan_match.
3. **over-col admission guard:** → `static int X_admit() { return <guard>; }` R2-KEEP
   value computer. Adds one sanctioned rp residual; clears over_col.

## Next stop: bb_scan_bal.cpp
Pre-audited: 4 violations = lv=1 + bypass=2 + over_col=1. Exactly the union of the
session's three recurring patterns — apply fp-cast inline + ROQ/seal decomposition +
bal_admit() static. Expected 4→0 CLEAN. Probe shape: `s ? write(bal(...))` per
icn_scan_tab_arg_ok's sibling list (bal needs nonempty literal cset without parens
per scrip.c admission).

## Outstanding verdicts (unchanged from prior sessions)
1. rp/hc counter-scope scope-widening (exclude lambda/helper returns from count?)
2. bb_arith dead-dispatch retirement (lower-unreachable finding, 37th run)
3. nw subscript-regex widen (audit misses param-alias form)
4. NEW: bb_scan_stmt IR_SCAN_LIT/IR_SCAN_GRAPH split (this session's [S], see above)

## Environment notes
- install_system_packages.sh required before first build (gc/gc.h)
- .github remote needs token re-set on clone (`git remote set-url origin https://TOKEN@...`)
