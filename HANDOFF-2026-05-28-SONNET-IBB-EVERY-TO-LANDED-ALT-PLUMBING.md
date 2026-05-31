# HANDOFF-2026-05-28 — Sonnet 4.6 — IBB-4 every_to.icn LANDED + BB_ALT plumbing

**Goal:** ICON-BB (`GOAL-ICON-BB.md`)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
**SCRIP HEAD:** `fac53504`
**.github HEAD:** to be set by handoff push

## Headline

Canonical-5 Icon BB **mode-3 advances 2/5 → 3/5**. `every_to.icn` (`every write(1 to 3)`) now produces `1\n2\n3\n` byte-identical to mode-2. Closure of the one-line blocker named in HANDOFF-2026-05-28-OPUS-IBB-RENAME-AND-FLAT-EVERY-WIP (Opus 4.7's prior session).

## What landed (SCRIP `fac53504`)

### Fix 1: `bb_to.cpp` MEDIUM_BINARY bin-site reorder (the named one-line blocker)

`src/emitter/BB_templates/bb_to.cpp` line ~136. `bin.sites` was `{fail_off+2, succ_off+1, back_off}` = `{64, 84, 19}` — NON-ascending. The patching loop in `bb_emit_asm_result` (`src/emitter/emit_str.cpp:70-77`) assumes ascending site order; it walks `pos < bin.sites[i]` to catch up before each site. With the third entry's site `19` already behind `pos=88` (= end of slab after processing sites 64 and 84), the inner catch-up loop body never ran and `bb_label_define(back_off → arg_β)` fired at `bb_emit_pos=88` instead of slab-offset 19. Hence `arg_β` resolved to the wrong address (= position of `arg_done` immediately after BB_TO), and the trailer's `jmp arg_β` landed on itself — second pop without intervening push → vstack underflow.

```diff
-            bin = { {fail_off+2, succ_off+1, back_off},
-                    {_.lbl_ω_p, _.lbl_γ_p, _.lbl_β_p},
-                    {false, false, true} };
+            bin = { {back_off, fail_off+2, succ_off+1},
+                    {_.lbl_β_p, _.lbl_ω_p, _.lbl_γ_p},
+                    {true, false, false} };
```

### Fix 2: BB_ALT plumbing (clean atomic value, separate from canonical-5)

Five files. `alt.icn` mode-3 still aborts but now at a *named, scoped* site (`flat_drive_alt_icn`) instead of being silently lost in the `bb_limit` fall-through.

- **`Makefile` (2 hunks):**
  - `bb_alt.cpp` added to source list (between `bb_to.cpp` and `bb_every.cpp`, line ~108)
  - `bb_alt.cpp` compile recipe added (between `bb_to.cpp` and `bb_every.cpp` recipes, line ~314)
  - Was a source-tree file with NO build artifact: `bb_alt` symbol was undefined, linker would have failed if anything called it. It didn't fail because:
- **`src/emitter/emit_core.c:563`:** `case BB_ALT:` was sharing the fall-through to `bb_limit(nd)` along with `BB_GOTO`/`BB_RETURN`/`BB_IF`/`BB_WHILE`/`BB_UNTIL`/`BB_REPEAT`/`BB_SIZE`/`BB_CASE`/`BB_LIMIT`. Now splits out: `case BB_ALT: bb_alt(nd); return 0;`. Other cases retain `bb_limit` dispatch.
- **`src/emitter/BB_templates/bb_templates.h`:** `void bb_alt(BB_t *)` declaration added (line ~60).
- **`src/emitter/BB_templates/bb_alt.cpp` MEDIUM_BINARY:** bin extended from 2-site `{{1,6},{γ_p,ω_p},{false,false}}` (no β-define) to 3-site `{{1,5,6},{γ_p,β_p,ω_p},{false,true,false}}`. The β-define entry was missing — would cause unresolved forward reference on any β-fed caller.
- **`src/emitter/emit_bb.c`:** new `flat_drive_alt_icn(pBB, lbl_γ, lbl_ω, lbl_β)` driver added before `walk_bb_flat`. New `case BB_ALT: flat_drive_alt_icn(...)` added to `walk_bb_flat`'s switch (between `BB_TO` and `default:`). The driver currently aborts loudly with a precise next-step doc.

## Empirical validation of the canonical-5 fix

```
$ SCRIP_ICN_BB=1 ./scrip --interp /tmp/every_to.icn
1
2
3
$ SCRIP_ICN_BB=1 ./scrip --run /tmp/every_to.icn
1
2
3
```

Byte-identical mode-2 vs mode-3.

## Empirical scoping of alt.icn architectural gap

Before reverting to ABORT, an experimental SNOBOL4-pattern-style arm-chain driver (no counter, each arm.β-template-internal site jumps to next arm's α) was tested. Result: `alt.icn` printed exactly `1` then exited cleanly. This **confirms** single-arm yield works through chain wiring — the EVERY re-pump entry (`arg_β`) just can't advance through arms without runtime state. SNOBOL4 pattern alt works without explicit state only because pattern matchers carry their own cursor state across re-entry; Icon literal arms have none.

## What is NEEDED for alt.icn mode-3 4/5

A **counter-state dispatch slab** in emitted x86. Mode-2 `bb_exec.c:1720` uses `bb->counter` for the same purpose:

```
α_entry:   movabs rcx,&pBB->counter
           mov qword [rcx],0
           jmp dispatch
β_entry:   movabs rcx,&pBB->counter        ; ← arg_β resolves here
           add qword [rcx],1
dispatch:  movabs rcx,&pBB->counter
           mov rax,[rcx]
           ; for i in 0..n-1:
           ;   movabs rdx,i ; cmp rax,rdx ; je arm[i]_α
           jmp lbl_ω                       ; exhausted
arm[0]_α:  ...BB_LIT_I template bytes (push ival; jmp γ; β: jmp ω where ω = unused/safety)...
arm[1]_α:  ...
arm[n-1]_α: ...
```

Per FACT RULE these dispatch bytes must come from a template. Two options:

**Option A (one template, recommended):** Fold dispatch into `bb_alt.cpp`. The driver mints arm-entry labels, then the template emits init+jmp-dispatch (α-entry), arm-entry collection (via EMIT_PAIR queue carrying arm labels), inc (β-entry), dispatch table. Walk arms via the driver in between α/β/dispatch sections (split-emit pattern). Cleanest.

**Option B (two templates):** New `bb_alt_dispatch.cpp` for the dispatch slab alone; `bb_alt.cpp` becomes the BB_ALT outer-port wrapper. More modular but two coupled templates and more EMIT_PAIR plumbing.

Approximate effort: 100-150 lines of new x86 byte construction in a template. Reference for byte sequences: `bb_to.cpp` (counter init/inc patterns are nearly identical to BB_TO's `cur += 1`), `bb_lit_scalar.cpp` (push convention).

## Gates HOLD

```
smoke_icon              5/5     ✅
smoke_prolog            5/5     ✅
smoke_raku              5/5     ✅
smoke_snobol4          13/13    ✅
smoke_unified_broker   39/14    ✅
icon crosscheck         2/2     ✅  (was 1/3 baseline; every_to flipped FAIL → PASS)
FACT-RULE grep          0       ✅
```

`if_expr --run vs --interp` in crosscheck is FAIL — **pre-existing, NOT a regression**. Verified by `git stash` baseline run: 1/3 PASS, 3 FAIL on `057bc824`. Cause: `flat_drive_binop_tree: missing α or β child` abort. Tracked separately.

## NEXT (in priority order)

1. **`alt.icn` mode-3 → 4/5:** author counter-state dispatch slab in `bb_alt.cpp` (Option A above). One focused session.
2. **`full.icn` mode-3 → 5/5:** BB_BINOP_GEN dispatch in `bb_call` int_expr predicate + new `flat_drive_binop_gen_tree` driver (cross-product walk of two `BB_TO` operand sub-trees applying `*`/`>` via `rt_arith`).
3. After canonical-5 5/5: flip `SCRIP_ICN_BB` default per IBB-7 watermark; run full mode-3 corpus sweep.

## Files touched

```
Makefile                                |  2 ++
src/emitter/BB_templates/bb_alt.cpp     |  7 ++++---
src/emitter/BB_templates/bb_templates.h |  1 +
src/emitter/BB_templates/bb_to.cpp      |  6 +++---
src/emitter/emit_bb.c                   | 28 ++++++++++++++++++++++++++++
src/emitter/emit_core.c                 |  2 +-
6 files changed, 39 insertions(+), 7 deletions(-)
```
