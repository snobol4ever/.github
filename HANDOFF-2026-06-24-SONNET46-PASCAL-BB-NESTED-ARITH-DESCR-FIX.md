# HANDOFF 2026-06-24 (Claude Sonnet 4.6) — PASCAL-BB: nested descriptor-arith read-offset fix (recparam3)

## TL;DR
- **`recparam3` CLOSED** (`dot := a.x*b.x + a.y*b.y` → 11, was 12). Pascal M3/M4 123/4 → **124/3**.
- Fix is in `emit_bb.c` only (SCRIP `cd4672a`). Validated zero regression across SNOBOL/Prolog/Icon.
- **Remaining 3** (`arr2dtype`, `arr2dtype2`, `arrparam`) fully diagnosed but deferred — different bug, higher cross-language risk.

## What was wrong (recparam3)

`dot := a.x*b.x + a.y*b.y` computes two field-read products then sums them.

- Each product (`a.x*b.x`) has two call-kind operands (`arr_get` acting as field accessor) → `bb_arith_is_dynamic` true + both operand slots ≥0 → routes to **Arm 1** (`IR_BINOP_GVAR_ARITH_SLOT` with `op_arith_descr=1`) → `rt_num_arith` → emits a full **tagged descriptor** at its output slot: `[slot+0]=tag (DT_I=6), [slot+8]=value`.

- The outer sum (`product1 + product2`) sees two `IR_BINOP` operands. In the dispatch arm (emit_bb.c ~3212), `bb_lk = ir_norm_call_kind(IR_BINOP) = IR_BINOP`. The template Arm-2 (bare-int inline path) reads its left operand at `FRQ(op_sa + 0)` for any operand kind that isn't `IR_CALL`/`IR_VAR_FRAME`/`IR_VAR_FRAME_REF`. Since `IR_BINOP` is not in that list, it reads `[slot+0]` — **the tag field** (= 6 = DT_I). Both operands: `6 + 6 = 12`. Expected `3 + 8 = 11`.

## Fix (emit_bb.c `cd4672a`)

Two-part change:

1. **`arith_emits_descr(IR_t *o)`** — new static helper (added between `bb_arith_is_dynamic` and `binop_slot_kind`, with proper separator). Returns true iff the BINOP `o` will emit a 16-byte tagged descriptor to its output slot (i.e., it took Arm 1). Predicate: `bb_arith_is_dynamic(o) && both operands are call/idx-kind or themselves arith_emits_descr`. This mirrors exactly the dispatcher's Arm-1-vs-Arm-2 choice. Key distinction:
   - `a.x * b.x`: both operands call-kind → `arith_emits_descr` true → Arm 1 → descriptor ✓
   - `t + f`: gvar + call → gvar is NOT call/idx → `arith_emits_descr` false → Arm 2 → bare int ✓

2. **Dispatch arm (emit_bb.c ~3219)**: when computing `bb_lk`/`bb_rk`, if the child is `arith_emits_descr` (and has a slot), normalize its kind to `IR_CALL` so the `+8` value-read in Arm 2's operand fetch fires. All other fields (`op_sa`, `op_sb`, `op_arith_descr`, `op_off`) unchanged.

This leaves:
- The bare-int chain (gvar/literal operands → Arm 2 → next Arm 2 reads +0) untouched → `t := t+f+2` still correct.
- The IDX-arm (emit_bb.c 3193, the existing two-call/two-idx Arm-1 path) untouched.
- All routing decisions unchanged.

## Why arith_emits_descr is needed (not bb_arith_is_dynamic)

`bb_arith_is_dynamic` is true for BOTH `a.x*b.x` (→ Arm 1, descriptor) AND `t+f` (→ Arm 2, bare int). Using it as the predicate for the read-offset fix caused `enum2`, `alphacmp`, `pb33/34/35` to regress (those use Arm-2 chains containing gvar operands). `arith_emits_descr` adds the second condition: *both* of the inner node's own operands are slot-bearing (call/idx), which selects exactly the Arm-1 (descriptor) case.

## Cross-language validation

- **SNOBOL feature `.s`**: 0/153 changed (md5 compare baseline vs fixed).
- **SNOBOL bench M4**: OK=15 FAIL=0 CRASH=1 — identical baseline and fixed.
- **Prolog parity gate** (`test_gate_pl_m34_parity.sh`): PASS=115 FAIL=0 — identical.
- **Template byte-identity gate**: PASS=0 FAIL=4 — identical (the 4 pre-existing SM-path failures, rc=1/sm gone since DE-INTERP).
- **Icon**: 3 of 1320 files appeared different; proven nondeterministic on baseline itself (two baseline runs give different md5s) and all 3 use 0 `IR_BINOP_GVAR_ARITH_SLOT` blocks — provably unrelated.

## Remaining 3 fails (arr2dtype, arr2dtype2, arrparam) — diagnosed, NOT fixed

Shape: `s := s + a[j]` (gvar + call-kind operand, flat non-nested).

Root cause: `IR_BINOP_GVAR_ARITH_SLOT` **Arm 2** writes its result as a **bare int** to `slot+0` only. The consuming `IR_ASSIGN` (via `flat_drive_gvar_assign_binop`, emit_bb.c:3327) reads that slot as a full descriptor (`[+0]=tag→rbx+0`, `[+8]=value→rbx+8`). So `rbx+0` (the gvar's tag field) gets the numeric result (e.g. 15) instead of DT_I, and `rbx+8` (the value field) gets stale garbage.

This is distinct from the `recparam3` bug: that was a *read* offset error on the consuming arith; this is a *write* representation mismatch between Arm-2 output and the assign consumer. The `t := t+f+2` case avoids this because its terminal assign does `mov [rbx+0], 6` (hardcodes DT_I) rather than copying from the slot as a descriptor — but gvar-assign-binop (the path for `s := s+a[j]`) does not.

Fix options (both risky, deferred):
- A. Make `flat_drive_gvar_assign_binop` apply DT_I tag when RHS is an Arm-2 BINOP (slot-based bare int).
- B. Make Arm-2 always write a full descriptor (`[slot+0]=DT_I, [slot+8]=value`) — principled but changes the shared representation relied on by chained Arm-2 arith in SNOBOL/Icon/Prolog.

Early-session attempts at A/B regressed 5 tests before the correct `arith_emits_descr` predicate was found for the recparam3 fix. The flat case is a separate, scoped piece that needs its own session with the full four-language gate budget.

## Gate scripts (recreate if lost)

```bash
# M3
for pas in /home/claude/corpus/programs/pascal/*.pas; do
  b=$(basename "$pas" .pas)
  case "$b" in pcom*|pint*|ppp*) continue;; esac
  [ -f "${pas%.pas}.ref" ] || continue
  [ "$b" = "recursion" ] && continue
  inp="${pas%.pas}.in"; [ -f "$inp" ] || inp=/dev/null
  got=$(timeout 30s scrip --run "$pas" < "$inp" 2>/dev/null)
  exp=$(cat "${pas%.pas}.ref")
  [ "$got" = "$exp" ] && echo "PASS $b" || echo "FAIL $b"
done | grep -c PASS

# M4 (compile+link+run)
# see /tmp/run_gate_m4.sh pattern from session
```

## Watermark
Session 66 (2026-06-24, Sonnet 4.6). M3/M4: 123/4 → 124/3. recparam3 CLOSED. 3 remaining (arr2dtype, arr2dtype2, arrparam).
