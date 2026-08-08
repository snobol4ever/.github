# FINDING — 2026-08-08 — Claude SN4.6 — RTCC RC-4: Arg Tier Landed

**Session:** s3 of GOAL-RTCC.md (Sonnet 4.6, same day as RC-0/RC-1/RC-2/RC-3)
**SCRIP HEAD:** `f2efb78c`
**Date:** 2026-08-08 UTC

---

## RC-4: FULL 9-GPR WRITEBACK LANDED — DEBUG LADDER II CLEAN

RC-4 claims the ARG TIER {RAX RCX RDX RSI RDI}: writeback now covers all 9 caller-saved GPRs at every generated→C boundary.

---

## Design Decisions Recorded

**RSP-SAFETY in the writeback.** The original RC-2 writeback used `push r11 / pop [r11+64]` to save R11. This moves RSP, corrupting ζ-spine addresses (ZRES/ZTOS) computed by templates that have live cells on the FORTH stack at call sites. Fix: BINARY writeback uses the `48 A3 addr64` moffs encoding (`mov [block+0], rax`) — the one x86-64 MOV encoding that stores RAX to an absolute 64-bit address with no base register and no RSP touch. RAX then becomes the block pointer for the remaining 8 stores. TEXT writeback uses `mov qword ptr [g_rtcc_block + 0], rax` (gas direct symbol reference) then `mov rax, [rip + g_rtcc_block@GOTPCREL]`.

**RC-4 PARTIAL RELOAD (the load-bearing decision).** The ARG TIER {RAX RCX RDX RSI RDI} reload from block slots is **deferred to RC-5** when VM globals are actually assigned to those registers. Until then every block slot is BSS-zero; restoring zero into RAX after a call clobbers the call's return value before templates can read it (`test rax, rax`, `mov r13, rax`, `cmp eax, DT_FAIL` etc.). The RC-4 reload restores only {R8 R9 R10 R11} — identical to the RC-2 scratch-tier reload but with the writeback now covering all 9 GPRs. Semantically correct: no VM global lives in the arg tier yet; block values are meaningless until RC-5.

**Double-writeback prevention.** Any template that emits `x86("rtcc_wb") + x86("call", ...)` would double-writeback because `x86("call", sym, ptr)` goes through `x86_rtcc_call` which also does a writeback. Solution: new `x86("call_bare", sym, ptr)` dispatch arm emits only the call bytes (no veneer) for use inside explicit `rtcc_wb`/`rtcc_rl` brackets.

**`cmp eax, DT_FAIL` inside brackets.** When the bracket is `rtcc_wb + call_bare + cmp + omega + capture + rtcc_rl`, the `cmp eax` and omega jmp must happen INSIDE the bracket (before `rtcc_rl`) so that `eax` is still the live call return code, not the reloaded block value. All converted templates follow this ordering.

---

## New Encoder Infrastructure

| Arm | Purpose |
|---|---|
| `x86("call_rt", sym, slot, ptr)` | DESCR_t-returning call: wb + call + FRQ(slot) capture + rl |
| `x86("rtcc_wb")` | Emit writeback half only; pair with `rtcc_rl` for chained sequences |
| `x86("rtcc_rl")` | Emit reload half only (scratch tier {R8 R9 R10 R11} at RC-4) |
| `x86("call_bare", sym, ptr)` | Raw call, no RTCC veneer; for use inside explicit wb/rl brackets |
| `x86_rtcc_call_descr(sym, ptr, slot)` | RETURN-BEFORE-RELOAD: FRQ capture before rl (defined after FRQ in scope) |

---

## Templates Converted

`bb_binop_arith` (fc_tail + inl_tail + ZD arm), `bb_binop_concat_slot` (FRQ arm via `call_rt`; ZRES arm via `call_bare` bracket), `bb_binop_relop` (`call_rt`), `bb_binop_xrep_slot` (`call_rt`), `bb_binop_gvar_arith_slot` (`call_rt` for NV_GET_fn; `call_bare` bracket for rt_num_arith), `bb_assign_global` (`call_bare` bracket around NV_SET_fn), `bb_call` (NV_GET_fn marshal → `call_rt`; rt_call_arr + rt_call_arr_gen → `call_bare` bracket), `bb_call_fn` (`call_bare` bracket), `bb_call_proc_staged` (`call_bare` bracket for gen_h + resume_frame_h), `bb_match_begin` (`call_bare` bracket for rt_match_enter + r13/r15 capture).

---

## Gate Results

**Smoke (both gates):** OFF 6/7 = baseline; ON 6/7 = MATCHING. One pre-existing failure in both.

**BY-SET board sweep (318 programs):**

| Mode | OFF PASS | OFF DIVERGE | OFF ERROR | ON PASS | ON DIVERGE | ON ERROR | RTCC-FAIL |
|---|---|---|---|---|---|---|---|
| m3 | 240 | 27 | 50 | 240 | 27 | 50 | 0 |
| m4 | 0 | 317 | 1 | 0 | 317 | 1 | 0 |

6 m3 programs swap DIVERGE↔ERROR between gates — confirmed PREEXIST nondeterministic class (same programs were flaky at gate OFF in prior sessions). EMPTY diff on m4.

**Debug Ladder II (12 rungs, RTCC-FAIL by set):**

| Rung | Programs | PASS-OFF | RTCC-FAIL |
|---|---|---|---|
| 1 hello | 4 | 4 | 0 |
| 2 assign | 8 | 8 | 0 |
| 3 concat | 6 | 6 | 0 |
| 4 arith | 2 | 0 | 0 |
| 5 control | 1 | 0 | 0 |
| 6 patterns | 122 | 74 | 0 |
| 7 capture | 9 | 5 | 0 |
| 8 strings | 17 | 11 | 0 |
| 9 keywords | 12 | 12 | 0 |
| 10 functions | 10 | 10 | 0 |
| 11 data | 6 | 6 | 0 |
| 12 beauty | 0 | 0 | 0 |

**RTCC-ATTRIBUTABLE FAILURES ACROSS ALL 12 RUNGS: ZERO.**

**CRATER = ZERO BY SET. ≥ RC-0 floor confirmed.**

---

## regen ×3

benchmark .s: 5 files changed (roman, pattern_bt*, mixed_workload, string_pattern — writeback sequence now uses moffs+movabs instead of push/pop).
feature .s: 40 files changed.
demo .s: 17 files changed (corpus commit `a4c02a64`).

---

## NEXT: RC-5 — GLOBAL ASSIGNMENT (concurrency-safe per assignment)

Assign VM globals into the protected set by MEASURED rank, one at a time on the fixed rail. Candidates (rank by census): NV dict base · GVA base · pat/dcap pool frontiers · keyword cache (&ANCHOR/&FULLSCAN) · subject char cache · statement base. Every assignment: rail A/B on the RC-0(a) instrument, honest ratio, revert if ≤1.00×.

⚠ RC-5 ARG TIER RELOAD NOTE: when the first VM global is assigned to a slot in {RAX RCX RDX RSI RDI}, the `x86_rtcc_rl_bin` and `x86_rtcc_rl_text` helpers must be extended to restore that slot from the block. The deferred-reload design at RC-4 is correct only until assignment begins. Each RC-5 rung that assigns an arg-tier slot must also enable its reload.
