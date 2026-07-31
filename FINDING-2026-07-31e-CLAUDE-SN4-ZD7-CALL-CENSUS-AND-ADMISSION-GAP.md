# FINDING-2026-07-31e — ZD-7 TAG-SAFE CALLEE CENSUS AND THE CALL ADMISSION GAP

**Session:** s22g · **Watermark throughout:** m3 232/85 · m4 229/86/2 · DIV=1 {W04_arbno_basic} — EXACT both ends.

---

## ⭐⭐ WHAT WAS PROVEN

### 1. TAG-SAFE CALLEE ACCESSOR — VERIFIED SAFE

`IR_LIT(nd).sval` is safe for bare `IR_CALL` nodes built by `lower_snobol4.c` — every IR_CALL node in that lowerer unconditionally writes `.sval`. The prior 18-program crash from attempting an instrument was caused by accidentally reading `.sval` on **`IR_CALL_VALUE`** nodes, which `lower_icon.c:399` builds WITHOUT writing sval (the union is uninitialized). The tag-safe predicate: `op == IR_CALL || (op != IR_CALL_VALUE && ir_is_call_kind(op))`. Landed as `SCRIP_CALL_DIAG=1` instrument in `emit.cpp`'s zd_plan decline path (SCRIP `cebcb320`).

### 2. FULL CALLEE PARTITION — 318-PROGRAM CENSUS

Run across all crosscheck programs. Decline-blocker breakdown:

| Kind | Count | Rung |
|---|---|---|
| `IR_MATCH_HEAD` | 247 | ZD-5 |
| `IR_CALL` (all callees) | ~519 total | ZD-7 |
| `IR_SAVE_RESTORE` | 17 | protocol |
| `IR_GOTO_DEFERRED` | 6 | jmp-entry excluded |

**IR_CALL callee partition (top):** SNO$MKPAT 145 · DIFFER 57 · DUPL 41 · SNO$NAME 38 · SNO$KWSET 22 · ARRAY 16 · SIZE 15 · EVAL/CODE 12 (jmp-entry excluded) · TABLE/REPLACE/DATATYPE/CONVERT/TRIM/RPAD/LPAD/REVERSE/REMDR/INTEGER 5–6 each · user-defined procs (roman, fib, build, node, val, dispatch, etc.).

Most of the 519 are **builtins** (DIFFER, DUPL, IDENT, SNO$*, SIZE, ARRAY, TABLE, etc.) routed through `bb_call_fn_str` or `bb_call_byname_str`. EVAL/CODE (12 total) are already excluded by `flat_jmp_entry` at graph level.

### 3. THE ADMISSION GAP — MARSHAL_CALL_ARG READS FLAT SLOTS

**Attempted ZD arm for IR_CALL was reverted.** The approach of adding `if (_.op_zres) { store ZRES(0)/ZRES(8); }` to `bb_call_fn_str` / `bb_call_byname_str` regressed by −63 (m3 232→169). Root cause measured:

`marshal_call_arg` reads producer results from flat slots (`FRQ(bb_slot_get(lf))` or `FRQ(zls_off(lf))`). Under ZD, **the producer's result was written to its own ζ cell (ZRES = [rsp+0..7])**, NOT to its flat slot. The flat slot still exists (LOWER granted it) but was never written. The call template reads garbage.

The ZD arm is also NOT just a result-store change — `argbase = resoff + 16` under ZD with `op_zdepth=16` places `FRQ(argbase)` at `[rsp + argbase + 16]`, which is wrong relative to the ζ cell layout.

**THEREFORE: IR_CALL admission requires a protocol change in how call arguments are sourced.** Two options:

**(A) ZD-aware marshal**: when `op_zres` and a producer has `zon[i]=1` (is ZD-armed), read its value from `[rsp + op_zread[k]]` (the staged delta) rather than from `FRQ(flat_slot)`. Requires threading the `zon[]` / `zout[]` arrays into `marshal_call_arg`, or staging an `op_arg_slot[]` array with the ZD-corrected offsets at plan time.

**(B) CALL stays FLAT, producers stay ZD**: IR_CALL is NOT admitted to ZD. Instead, ZD-armed producers (LIT/VAR/BINOP/COERCE) in a statement that contains a CALL write their results to BOTH the ζ cell AND the flat slot (a dual-write arm). The call reads the flat slot as before; ZD consumers of the same producer read the ζ cell. This is the **"flat slot as a write-through cache"** model — more copies, but zero marshal_call_arg changes.

**(C) ALL-OR-NOTHING PER STATEMENT** (current law): a statement containing IR_CALL declines ZD wholesale. This is the status quo and is already correct — the census confirms IR_CALL is the dominant decliner (519 of 789 decline firings). The ZD-7 rung converts call statements to ZD by implementing option A or B.

---

## ⛔ THE NEXT DISCRIMINATING EXPERIMENT

Before choosing A or B, verify whether any IR_CALL in a declining run ever has a ZD-armed predecessor in the SAME run. Prediction: NO — IR_CALL runs are always single-node (the call is the head and sole member). If confirmed:

- The `op_zread[]` operand-predecessor problem is VACUOUS for calls (no predecessors to read)
- The `argbase` problem remains: args are sub-graphs, not run-members, so they're always in flat slots
- Option B (dual-write) is unnecessary — flat marshalling already works because producers in a call statement are themselves NOT ZD-armed (they decline with the call)

The remaining issue is ONLY: **the result store**. `FRQ(resoff)` under ZD adds `op_zdepth=16` compensation, placing the result at `[rsp + resoff + 16]` instead of `[rsp + resoff]`. The correct fix: use `FRQ(resoff - (int)_.op_zdepth)` = `FRQ(resoff - 16)` when op_zres, OR use `ZRES(0)/ZRES(8)` and fix `argbase` accordingly.

Actually simpler: **just confirm run-length = 1 for IR_CALL runs**. If true, ZD-7 arm = single-node statement, no producer cells to read, and the argbase/result store issue reduces to: result goes to ZRES(0)/ZRES(8), argbase stays `resoff + 16` (flat frame, no ZD compensation needed for the marshal target), just need to carve the ζ cell AND preserve the flat frame intact under it. The alpha carve adds 16B below; FRQ refs compensate via op_zdepth; the result is deposited at ZRES(0)/ZRES(8) which is `[rsp+0]` — that's 16B BELOW the original flat frame, in the carved space. This should work IF the flat arg slots are at `resoff+16` in the uncompensated flat frame (which they are, per the ZD=0 disassembly: args at rsp+32, result at rsp+16 with resoff=16, argbase=32). Under ZD with zdepth=16: `FRQ(32)` = `[rsp+48]` — but the original flat args were at `[rsp+32]`. STILL WRONG by 16.

**THE FIX IS CLEAR NOW**: the op_zdepth compensation shifts every FRQ reference up by K=16. This is intentional for nodes that are consumed BY OTHER ZD nodes (their cells stack). But a call's arg slots are in the STATIC flat frame — they should NOT be shifted. The call arm under ZD must use `FRQ(argbase - (int)_.op_zdepth)` for its arg addresses (so the net = no shift), OR carve the args into its OWN ζ cell region (making argbase = 0, below the result at zres+16). Option: **argbase = 0** under ZD (result at ZRES(0)/ZRES(8), args at ZRES(16)/ZRES(32)/...), and use the ζ carve K = 16 + narg*16. Then the ZLS grant bytes and the ζ carve must agree. This requires `zw_node_k` to return 16 + narg*16 for IR_CALL — currently it returns 16 (standard leaf).

---

## ⛔⭐ NEXT — ORDERED (Supersedes s22f NEXT)

**(1) CONFIRM IR_CALL RUN LENGTH = 1 via SCRIP_CALL_DIAG** — instrument already live; add run-length logging alongside the blocker. If always 1: the predecessor-read problem is vacuous, admission reduces to a ζ-cell-size and argbase fix.

**(2) WIDEN ζ CELL FOR IR_CALL**: set `zw_node_k(IR_CALL) = 16 + narg*16` — result at `[rsp+0]`, args at `[rsp+16..]`. Zero changes to `marshal_call_arg` (it writes `FRQ(argbase + i*16)` with `argbase=0+16=16`; under ZD `FRQ(16) = [rsp+16+16]`... still off by 16 because of zdepth). Alternatively: **under ZD, use raw ZTOSD/ZTOS addressing for args** instead of FRQ. `ZTOS(16*i)` = `[rsp + 16*i + op_zdepth]` = `[rsp + 16*i + K]` — where K is the total carve. If `argbase_base = 0` and args start at ζ+16 (first arg), then `ZTOS(16)` = result+16 = first arg. This is self-consistent once K = result + narg*16.

**(3) ZD-5 / `IR_MATCH_HEAD` (247 declines)** — parallel ladder, the larger mass of the pat_* failure set.
