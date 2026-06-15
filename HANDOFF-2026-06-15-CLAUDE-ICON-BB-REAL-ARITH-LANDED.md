# HANDOFF 2026-06-15 — Icon native real-arithmetic path (✅ LANDED)

**Author:** Claude Sonnet · **Trigger:** GOAL-ICON-FULL-PASS "real-arithmetic runtime path".
**Status: GREEN — landed `c26f89f` on origin/main.** Supersedes the RED WIP handoff
`HANDOFF-2026-06-15-CLAUDE-ICON-BB-REAL-ARITH-WIP.md` (that session got the path ~90% done
but left two regressions; this session applied that WIP patch + the two documented fixes and
landed clean).

## Result
Icon **m3 127→132**, **m4 127→132** (+5 each). FAIL 25→23, EXCISED 95→92 (both modes).

FAIL→PASS (both modes): `rung18_real_relop_mixed_relop`, `rung18_real_relop_real_gt`.
EXCISED→PASS (both modes): `rung17_real_arith_real_add`, `rung18_real_relop_real_eq`,
`rung18_real_relop_real_lt`.
baseline→EXCISED (Fix 1, NOT a regression): `rung19_pow_toby_pow_var`.

Verified by explicit FAIL-name AND EXCISED-name diffs in BOTH modes = zero new FAIL, zero
EXCISE→FAIL. (A net +PASS can hide an EXCISE→FAIL — the diff is the source of truth.)

## What landed (7 files)
1. **`src/runtime/arithmetic.c`** — `DESCR_t rt_num_arith(DESCR_t a, DESCR_t b, int op)`:
   Icon int/real/mixed coercion (`anyf = lf||rf`; ADD/SUB/MUL/DIV/MOD/POW), div-by-zero →
   `FAILDESCR`. Pure value, NO α/β/γ/ω ports (RT=value, BOX=ports — the no-duplicated-logic
   law). `#include "builtins/gen.h"` for `BINOP_*`.
2. **`src/runtime/by_name_dispatch.c`** — `rt_jct_relop` additive real/mixed branch BEFORE the
   int-int fast path (also improves SNOBOL4/Prolog real relops; int-int + string paths
   untouched).
3. **`src/emitter/emit_globals.h`** — new representation flag `int op_num_real;`.
4. **`src/emitter/emit_bb.c`** — static helpers `var_assigned_real_static`,
   `binop_operand_real_static` (LIT_F→1; VAR→scan graph for `IR_ASSIGN(name,LIT_F-rhs)`;
   BINOP/ALT→recurse; depth≤8), `binop_is_num_real`, `descr_binop_set_slots(nd)` (sets
   `op_num_real`, resolves `op_sa/op_sb` LIT_F-inclusive + `bb_slot_alloc16`, else falls back to
   `descr_binop_opnd_slot`). Wired into both `flat_drive_binop_tree` and
   `flat_drive_binop_gen_tree` tails and the non-walk descr branch. **Fix 2 also here.**
5. **`bb_binop_arith.cpp`** — real arm gated on `op_num_real`: marshal both DESCRs
   (rdi:rsi / rdx:rcx, op→r8d) → `call rt_num_arith` → `cmp eax,DT_FAIL; je ω` → store rax:rdx →
   γ. Int arm got `&& !_.op_num_real`. Pure `x86()`, medium-invisible, 0 byte-producers.
6. **`bb_binop_relop.cpp`** — int payload-compare arm gated `!op_num_real && LT..NE`; the
   `rt_jct_relop` call arm fires on `(op_num_real && LT..NE) || (SLT..SNE)` — one call body,
   real-numeric + string merged, no duplication.
7. **`src/driver/scrip.c`** — **Fix 1.**

## The two fixes (the WIP's open regressions)

### Fix 1 — `graph_has_pow` (`scrip.c`)
The WIP relaxed `local_assign_rhs_ok_g`'s LIT_F guard to `return 1`, which ADMITTED
POW-bearing graphs (`x:=3.0;write(x^2)`). But `x^2` is `BINOP_POW`, which is (a) not in
`binop_is_num_real` and (b) routed by `binop_slot_kind` to generic `IR_BINOP`, not the real
arm → `[walk_bb_node: kind=7 unhandled]` garbage instead of the clean baseline EXCISE.
**Fix:** added `static int graph_has_pow(const IR_graph_t *g)` (scan for `IR_BINOP &&
IR_LIT(nd).ival==BINOP_POW`) and changed the guard to `if (rhs && rhs->op == IR_LIT_F) return
!graph_has_pow(g);`. POW-bearing LIT_F-assign graphs stay cleanly EXCISED;
real_add/gt/eq/lt/mixed carry no POW → still admitted.

### Fix 2 — skip already-slotted child in `flat_drive_binop_tree` (`emit_bb.c`)
The root_node tree path re-walked LIT_F operands ALREADY emitted as chain nodes → the same
`bb<id>_α` label twice. m3 (binary emitter) silently tolerates duplicate labels (last-wins);
m4 (`as` on the text) errors → rc=1. **Fix:** before walking each child, if
`bb_slot_get(child) >= 0` skip the walk and `emit_jmp_label(<child>_done, JMP_JMP)` — the value
is already in its slot (the chain produced it earlier in execution order).
`descr_binop_set_slots` resolves via `bb_slot_get` so it reuses the original chain slot.
**Verified:** the `real_gt` `.s` now has ZERO duplicate labels, assembles clean with `as`,
links, and outputs correctly. (Always assemble the m4 `.s` standalone when a kind passes m3 but
not m4 — m3 last-wins masks dup-label bugs that `as` rejects.)

## Gates (pre-push, and re-verified identical after EACH of two rebases)
icon m3 132 / m4 132 (FAIL 23, EXCISED 92, FAIL+EXCISED name-sets stable) · icon smoke 12/12
m3+m4 · prolog smoke 5/5 m3+m4 · no-stack 0 · one-reg-frame 0 · FACT 0 · bb_bin_t 0 · g_vstack
0 · no added line >200 chars · the two binop template files have 0 raw-byte producers /
`IF(MEDIUM_BINARY)`. Rebased clean twice over concurrent Raku-OO / Prolog-retract / SNOBOL4
const-fold / BB-FIXUP-ZtoA / `bb_call` IR_CALL_BUILTIN-producer landings; zero interaction with
the Icon real-arith path each time.

## NEXT (real-arith remainder, scoped)
- **native real-POW**: route `BINOP_POW` → `bb_binop_arith`, add `BINOP_POW` to
  `binop_is_num_real`; `rt_num_arith` already does `REALVAL(pow(ld,rd))`. Unblocks
  `rung19_pow_toby_pow_var` (today EXCISED) and the real-VAR pow cases.
- **real TO/BY**: `rung19_pow_toby_real_toby_neg`/`_pos` (rc=124 m3 / rc=1 m4) — real-step
  generator (`bb_to` real arm), the generator-retry track.
- `real_relop_goal` (`every write(3.0<(2.5|3.5|4.5))`) stays EXCISED — gen-alt resume
  (`cross_arg` track), separate item.

## Note
The GitHub token used this session is in the conversation and was embedded in the SCRIP remote
URL to push; rotate it after the session.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
