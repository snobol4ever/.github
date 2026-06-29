# HANDOFF — 2026-06-29 — Sonnet 4.6 — Icon-only pivot

## SCRIP HEAD: e1ec0679 (pushed to origin/main ✅)

---

## Session summary

Orientation + two concrete steps per Lon's direction.

### Step 1 — emit_drive_node → emit_drive (function rename)

`src/emitter/emit_drive.c` stays `emit_drive.c` (backend-neutral driver name; the x86 lives in
the templates it dispatches to, NOT in the driver). Function renamed from `emit_drive_node` to
`emit_drive` in three places: definition (`emit_drive.c`), declaration (`emit_drive.h`), and both
call sites in `emit_bb.c` (lines 1431 + 1552, sed-anchored). Build + mode-3/4 both green.

### Step 2 — Non-Icon lowerers out of the Makefile build (Icon-only pivot)

Lon's directive: keep `lower_icon.c` in build; slide `lower_snobol4.c`, `lower_raku.c`,
`lower_pascal.c`, `lower_prolog.c` OUT of the Makefile. Files remain intact on disk.

Build surface revealed 7 dangling symbols in surviving code:
- `lower_snobol4` + `lower_sno_stage2` — called from `runtime_eval.c` + `lower_common.c`
- `lower_pascal_stage2`, `lower_pl_stage2`, `lower_raku_stage2` — `lower_common.c` dispatcher
- `pl_dyn_mark`, `pl_dyn_is_marked` — `parser/prolog/prolog_lower.c` + `scrip.c`

Resolved by `src/lower/lower_noicon_stubs.c` (new TU, added to Makefile):
- `lower_sno_stage2` → **faithful no-op `return 0`** — the real one returns 0 for any non-SNO
  program; the polyglot mask sets SNO+ICN even for pure Icon files, so the dispatcher calls it
  unconditionally on the Icon path. Must not abort.
- All other 6 → `abort()` with FATAL message (truly non-Icon paths Icon never reaches).

Build links clean. `lower_icon.c`, `lower_common.c`, `tree_to_sno.c` remain in build.

### Also: GOAL-IR-IMMUTABLE-EMIT.md ENTRY POINT section updated

Now reads `emit_drive` / `emit_drive.c` throughout; notes the function rename; adds the
backend-neutral explanation (driver is language- AND backend-neutral; x86 is in the templates).

---

## Gate

```
A op-writes=6   B field-writes=0   HARD TOTAL=6   (target 0)
C informational: rt_* emit-time queries in emit_bb.c = 16
```

Gate was HARD=38 as of the previous handoff (2026-06-29 D1-CALL-ARGS). The `f8e88daf` commit
("delete old driver wholesale") that landed between that handoff and this session stripped the old
fat driver's mutation sites, bringing it to 6. No new mutations added this session.

---

## What was NOT done (next session)

Lon directed: **delete all IR_e IR_* enum members from IR.h that are not referenced from
`emit_drive`** (keep only the 27 in the current `emit_drive.c` switch). This is the enum
amputation — 185 of 212 members go. The template concern was resolved: templates reference
`IR_*` only inside `x86("comment", "...")` strings (a few in code, e.g. `bb_call.cpp` reads
`IR_VAR_FRAME` — those become the template's own problem when the enum member for IR_VAR_FRAME
is deleted). Cascade: `lower_icon.c` references 33 of the to-delete members — those lower
emissions must be removed (or redirected to JCON-style primitive chains) alongside the enum cut.

Rung order for next session:
1. Delete the 185 IR_e members not in `emit_drive`'s switch from `IR.h`
2. Let the build break; fix each break site in order: `emit_bb.c` → `emit_core.c`/`walk_bb_node`
   → `lower_icon.c` → any template that uses the opcode in real code (not comments)
3. Run the Icon test suite rung ladder from scratch (Icon-from-scratch, Ground Zero)

---

## PUSH STATUS
SCRIP: 584cea96 → e1ec0679 pushed to origin/main ✅
.github: this handoff doc pending push (next step)
