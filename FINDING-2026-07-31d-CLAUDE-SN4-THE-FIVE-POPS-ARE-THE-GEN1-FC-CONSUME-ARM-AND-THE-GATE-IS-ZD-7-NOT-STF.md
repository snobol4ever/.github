# FINDING 2026-07-31d — THE FIVE CONSUMER POPS ARE THE GEN-1 FC ARM'S CONSUME DISCIPLINE; THE GATE IS ZD-7 (IR_CALL), **NOT** THE STF ARMING WIDEN

Session s22f. Goal: `GOAL-SNOBOL4-BB.md`, head rung "NON-POPPING FORTH-style RSP ζ stack with a C-style RBP used occasionally only when absolutely necessary" (Lon, this session).

Baseline re-proven at session start, EXACT vs the s22e cursor: crosscheck **m3 232/85 · m4 229/86/2 · DIV=1 {W04_arbno_basic}**. Re-proven again at close, unchanged.

---

## ⭐⭐ THE HEADLINE — THE INHERITED GATE IS THE WRONG GATE, AND IT IS WRONG BY MEASUREMENT, NOT BY OPINION

`s22a NEXT(1)` (carried verbatim into the s22e cursor) says the five `IF(!stf())` consumer pops are gated on the **STF ARMING WIDEN** — widen the per-statement rbp bracket from 31/318 graphs to "higher", then the pops become deletable because there is finally "a bracket to cut back to."

**THAT IS FALSE, IN TWO INDEPENDENT WAYS, BOTH MEASURED AT HEAD.**

1. **THREE OF THE FIVE POPS HAVE NO `stf()` TERM AT ALL.** Read live this session: only `bb_assign_global.cpp:48` and `:60` are `IF(!stf(), x86_zrelease(16))`. `bb_binop_arith.cpp:66` (inside `fc_tail()`) / `:107` and `bb_binop_concat_slot.cpp:40` are **unconditional** `x86_zrelease(16)` inside their FC arms. No amount of STF widening can reach them. The cursor's "five `IF(!stf())` pops" is a mis-description of three of its own five sites.
2. **ALL 119 ASSIGN FC FIRINGS CARRY `stf=0`.** So for the two sites STF *can* reach, suppressing the pop means arming the rbp bracket on every one of them — **universal rbp**, which is the exact opposite of the directive "a C-style RBP used occasionally only when absolutely necessary."

---

## ⭐⭐ WHAT THE POPS ACTUALLY ARE — GEN-1 FC, A SECOND CORPSE BESIDE THE CARVE

All three templates have the **same three-arm shape**, and the arms are three generations of value-spine machinery stacked in one file:

| arm | predicate | operand addressing | release | verdict |
|---|---|---|---|---|
| **ZD (Gen-2)** | `_.op_zres` | `ZOPQ(k,·)` — **staged differences** `op_zread[k]` | **NONE** — cells persist to statement boundary, `op_zgpop`/`op_wpop` restore rsp wholesale | ✅ the ratified model |
| **FC (Gen-1)** | `vfc()`/`vfcb()`/`vfcc()` = `port==FORTH && op_fc_disp>=0` | `ZTOS(16)/ZTOS(24)` + `ZTOS(0)/ZTOS(8)` — **TOP TWO ADJACENT CELLS** | `x86_zrelease(16)`, result overwrites the surviving cell | ❌ **"2 in, 1 out" consumption** |
| **FLAT (legacy)** | `op_off>=0` | `FR`/`FRQ` — the whole-graph carve | none | ❌ the carve corpse |

The ZD arm returns FIRST in all three templates (`if (_.op_zres) return …`), so **the FC arm only ever runs on a node ZD declined.**

⭐ **THE POPS ARE THEREFORE NOT A FALLBACK FOR A MISSING BRACKET. THEY ARE THE Gen-1 FORTH-MACHINE CONSUME DISCIPLINE** — precisely the "2 in 1 out" reading that s22b recorded Lon forbidding (*"NO BB EVER CONSUMES ANYTHING, EVER … Nothing consumes. Scope frees."*). The ZB-VAL-1/5/6a comments say so in their own words: *"operands are the TOP TWO cells (a=[rsp+16..31], b=[rsp+0..15]) … result replaces both via one net add rsp,16."* **`GOAL-SNOBOL4-BB.md` names ONE corpse (the carve). There are TWO. Gen-1 FC is the second, and it is the one that pops.**

---

## ⭐ THE CENSUS (new instrument `SCRIP_FC_DIAG=1`, env-gated, verified byte-identical inert when off)

Full crosscheck corpus, 318 programs, live `--compile` sweep (**the compiler, never the artifacts**):

- **163 FC-arm firings total**, in **29 programs**.
- By kind: **ASSIGN 119** · **BINOP_CAT_CONCAT 25** · **BINOP_CAT_ARITH 19**.
- **`fallback=FLAT-OK` on 163 of 163** — every FC node has `op_sa`/`op_sb`/`op_off` (resp. `op_a_slot`/`op_off`) ≥ 0, i.e. the legacy flat arm is *syntactically* able to carry all of them. ⛔ **THIS IS A TRAP AND IT IS WHY THE DELETION EXPERIMENT BELOW WAS RUN:** slot-validity says nothing about whether the *producer* ever WROTE that slot.

## ⭐⭐ THE PERFECT CORRELATION — FC IS 100% COLLATERAL OF ZD STATEMENT DECLINES

Per-program, FC firings vs `SCRIP_ZD_DIAG=1` declines across all 318:

- programs with **FC>0 and declines==0: ZERO**.
- programs with **FC>0 and declines>0: 29 of 29**.

Decline first-blocker census (789 declined runs, four kinds only, re-derived live): **`IR_CALL` 519 · `IR_MATCH_HEAD` 247 · `IR_SAVE_RESTORE` 17 · `IR_GOTO_DEFERRED` 6.**

`zd_plan` is **all-or-nothing per STATEMENT** (the reader-frontier law). So an arith/concat/assign node that would arm perfectly well is dragged off the ZD plan because *some other node in its statement* is a CALL or a MATCH_HEAD — and it then lands on Gen-1 FC, which pops. **The pops are a shadow cast by the IR_CALL frontier.**

## ⛔⭐⭐ THE DISCRIMINATING EXPERIMENT — FC CANNOT BE DELETED DIRECTLY, RE-MEASURED AT HEAD *AFTER* WPOP-1

s21x-z's FINDING 3 deletion test (m4 222/93/2, DIV=7) was run BEFORE s22b's WPOP-1 fixed a 32-byte fail-edge over-free at two of these exact sites, so it was worth re-running rather than inheriting. New killswitch `SCRIP_NOFC=1` (env-gated, **byte-identical inert when off, verified 318/318**) forces all three FC predicates to 0, routing every FC node to the flat arm.

**RESULT — STILL RED, WPOP-1 DID NOT CHANGE IT:** m3 232→**211** (−21) · m4 229→**209** (−20) · DIV=1.

**NEWLY BROKEN (m4), set-diffed, 20 programs, ZERO fixed:**
`082_keyword_stcount 083_define_simple_return 084_define_loop_call 085_define_two_args 086_define_locals 088_define_recursive_fib 090_define_entry_label 097_define_capture_return_d2probe 100_roman_numeral 1012_func_locals 1019_eval_string 1020_code_label_transfer 1021_code_direct_goto 204_gc_recursive_frames 212_gc_args_in_flight 214_indirect_goto 215_indirect_goto_cond 216_indirect_goto_computed test_math test_stack`

⭐ **EVERY ONE IS A DEFINE / CALL / EVAL / CODE / INDIRECT-GOTO PROGRAM.** The break set and the ZD blocker set are the SAME FAMILY. Gen-1 FC is currently the **only** value-spine mechanism serving call-bearing statements; the flat arm cannot carry them because their producers wrote ζ cells, not carve slots. This is also a live re-confirmation of the SPITBOL semantics the family encodes: a DEFINE prototype's locals and formals are ordinary globals saved on a **pushdown stack** at call and restored at return (manual Ch.4, *"any existing values … will be saved on a pushdown stack … restored to their previous values"*) — that push/restore is `IR_SAVE_RESTORE` + `IR_CALL`, i.e. law 7, and it is exactly the frontier that blocks ZD.

---

## ✅ THE CORRECTED GATE

**THE FIVE POPS DIE WHEN ZD ARMS `IR_CALL` (ZD-7) — AND NOT BEFORE.** Order:

1. **ZD-7 / `IR_CALL` (519 declines)** — the protocol rung the s21x-y cursor already names as *"law 4's other genuine RBP citizen, the frame dance."* ⛔ Cross-goal substrate: read `DESIGN-SN4-CELL-MACHINE.md § DL` first (the cursor says so; this finding independently confirms the CALL family is the blocker).
2. **ZD-5 / `IR_MATCH_HEAD` (247 declines)** — the other half; also the 85/86-red mass (the fail sets are almost entirely `pat_*`).
3. **THEN** flip `SCRIP_NOFC=1` to the default and delete the FC arm + all five pops. The killswitch is already in the tree for exactly this A/B, and its success metric is now defined: **`SCRIP_NOFC=1` must reach the watermark**, at which point the arm is provably dead and deletion is mechanical.

⚠ **DO NOT** spend a rung on the STF ARMING WIDEN in order to reach the pops. It cannot reach 44 of the 163 firings at all, and it buys the other 119 only at the price of universal rbp. **The STF/rbp question is orthogonal to the popping question and s22b already resolved it correctly by defaulting the bracket OFF.**

⚠ **`fallback=FLAT-OK` IS NOT A DELETION LICENSE** — 163/163 reported it and deletion still cost 20 programs. Slot validity ≠ slot written. Record it as an instrument law: *a fallback-viability census over the CONSUMER cannot license removing an arm whose PRODUCERS write elsewhere.*

---

## INSTRUMENTS LANDED (both env-gated, both proven inert when off)

- **`SCRIP_FC_DIAG=1`** (`emit.cpp`, IR_BINOP + IR_ASSIGN dispatch) — prints `[FC-ARM] kind=… zres=… fc_disp=… sa/sb/off … fallback=…` for every node taking the Gen-1 FC arm. Inertness verified byte-identical over 40 programs.
- **`SCRIP_NOFC=1`** (`bb_assign_global.cpp` / `bb_binop_arith.cpp` / `bb_binop_concat_slot.cpp`) — forces `vfc`/`vfcb`/`vfcc` to 0, killing the FC arm corpus-wide. Inertness verified byte-identical over **318/318** programs. This is the A/B that gates step 3 above.

Watermark at close, default path: **m3 232/85 · m4 229/86/2 · DIV=1 {W04_arbno_basic}** — EXACT, fail sets identical by SET both modes.
