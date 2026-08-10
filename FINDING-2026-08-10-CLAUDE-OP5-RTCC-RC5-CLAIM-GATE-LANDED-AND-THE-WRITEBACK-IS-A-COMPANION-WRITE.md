# FINDING — 2026-08-10 — Claude Opus 5 — RTCC s8: the claim-gate lands, and the veneer's own writeback is a companion write

**Session:** s8 of GOAL-RTCC.md (Opus 5)
**SCRIP HEAD at open:** `930539c0` · **at close:** `a42f4b2a`
**Deliverable:** `scripts/test_gate_rtcc_claimed_regs.sh` + `scripts/rtcc_claimed_reg_whitelist.txt`. Scripts only; ZERO emitter bytes; no regen owed (RULES.md §4).
**Concurrency:** CONCURRENCY-SAFE (RC-0 class — scripts/docs only). Ran alongside live seats; touched no `x86_asm.h`, no template, no `.s`.

---

## 0. Why this rung, out of order

Lon's question opened the session: *"Is this not just a one pass, done and done, process? Why not just identify every C call and slap save/restore code around each?"*

The audit answer is that the one-pass part **is** done and the framing exposes where the time actually goes:

- The veneer is not per-call-site work. It is ONE encoder choke (`x86_asm.h:1606`), and all **332** template call sites route through it because TEMPLATE-ONLY EMISSION already funnels every emitted instruction there. RC-1..RC-4 are closed; the registers are freed.
- The tiering was forced, not ceremonial: `{R10,R11,R8,R9}` can be bracketed, but `{RAX,RCX,RDX,RSI,RDI}` *are* the SysV arg/return registers, so claiming them required moving arg staging and `DESCR_t` RAX:RDX capture into the encoder (RC-4).
- **Freeing registers buys nothing by itself; it only costs** (9 stores + 9 loads per crossing, on a boundary seeing ~10M rt calls/run). The payoff is RC-5, which is inherently one-global-at-a-time-and-measured.

But the dominant cost was none of the above. **Two of the last three sessions (s6, s7) went entirely to a cross-seat register collision** — AB-2 grabbing r9 after RC-5-GVA claimed it. That is a process defect, not a design defect, and it is cheap to close. Hence this rung ahead of more RC-5 mining.

---

## 1. The gate

`test_gate_rtcc_claimed_regs.sh`. Registry `LIVE_CLAIMS` currently `r9:RT_GVA_VA:RC-5-GVA` — one line to extend per future RC-5 assignment, which is the point: each new assignment buys itself this protection for the cost of one edit.

Reports the HAZARD SURFACE (all writes/base-uses of a live-claimed register in templates) and hard-fails under `--strict` only the **COLLISION CLASS**: files that BOTH write a live-claimed register AND read through `GVARQ`. Comments stripped, so a comment naming a register is not a live use.

Ships **INFORMATIONAL by default** so it blocks no concurrent seat; `--strict` exists for the RC-7 fold. This mirrors the VSX-1..8 idiom.

## 2. FALSIFICATION PASSED — the gate has teeth

Per this file's own law (*"BY CONSTRUCTION IS A HYPOTHESIS UNTIL A PROBE KILLS THE ARM"*), a gate never shown to fire is worthless. Tested against real history, not a synthetic shape:

| tree | collision class | `--strict` exit |
|------|-----------------|-----------------|
| `2af35d7d^` (pre-fix, AB-2 r9 defect live) | `bb_func_activate.cpp` **`bb_save_restore.cpp`** | **1 (FAIL)** |
| HEAD (post-fix) | `bb_func_activate.cpp` | 1 (see §3) |

`bb_save_restore.cpp` enters the collision class exactly when the defect is present and drops out exactly when it is fixed. **The gate would have caught the s6/s7 bug at commit time.** Working tree restored clean (0 diffs) after the test.

## 3. AT HEAD the class is not empty — `bb_func_activate.cpp` is UNCLEARED

`bb_func_activate.cpp` writes r9 (`movzx r9, cl`, line 205 — the RETURN/NRETURN/FRETURN type code) and reads `GVARQ` (lines 147/149/166/167 — save-set formal save/restore).

This is **the same collision the RTX-FUNC-0 commit message already flagged in passing** (`22a61ccf`: *"beta movzx r9,cl vs RTCC_GLOBAL_R9_GVA r9=GVA-base claim (beta restore is ABSQ-only; new result read kept ABSQ deliberately)"*) — a human noticed it, wrote it in a commit message, and left it ungated. The gate rediscovers it mechanically. That is the case for the gate in one line.

**NOT convicted and NOT acquitted here.** File order is not execution order, and RULES.md forbids conviction by code-reading — it equally forbids acquittal by code-reading. Deliberately left off the whitelist for the owning seat (RTX-FUNC / AB) to clear by probe or fix.

## 4. SECOND-ORDER FINDING — the "no companion writes" exception is not true as written

`rtcc_init.c` seeds the R9 slot once and comments: *"no companion writes needed anywhere in the runtime (BLOCK-CANONICAL EXCEPTION for constant globals)."*

But `x86_rtcc_wb_bin` emits, unconditionally, at **every** crossing:

```
mov [rax+48], r9        /* R9 slot 6 */
```

**The veneer's own writeback IS a companion write.** The exception holds only under the stronger unstated premise that r9 *always* equals RT_GVA_VA at every veneered call. Consequence, if that premise is ever violated: a template clobber of r9 that reaches a veneered call does not merely misread locally (H1) — the writeback stores the clobbered value into the canonical slot and the reload propagates it, **destroying RT_GVA_VA for the remainder of the process** (H2). H2 is strictly worse than the AB-2 bug, which was local.

Why the board is green anyway: `var_access.sno` uses `LT(...)` and passes RTCC=1 with the correct result, because the int-int relop **fast** arm never stages r9 — the `lea r9, FRQ(...)` sites in `bb_binop_relop.cpp` are the slow/6-arg arms. That is the same invisibility pattern that hid AB-2 from every flat benchmark and required doubly-recursive fibonacci to expose.

**Status: RECORDED, NOT PROBED.** No claim of a live defect is made. The honest next step is the probe, below.

## 5. Candidate fix (for whoever takes the probe) — do not land unprobed

Make the stated exception true in code: **skip slot 6 in the writeback when `RTCC_GLOBAL_R9_GVA` is on.** One line each in `x86_rtcc_wb_bin` and `x86_rtcc_wb_text`. Then a template clobber of r9 becomes *self-healing* — the next reload restores RT_GVA_VA from the pristine seed — which converts all 20 surface sites from live hazards into harmless transients and removes H2 entirely.

⛔ Touches `x86_asm.h` ⇒ NOT-CONCURRENCY-SAFE by this file's protocol; Lon routes the window. Mitigating fact: killswitch OFF short-circuits before the writeback (`x86_rtcc_call` returns `x86_call_ro`), so the change is invisible at default and `.s` artifacts — generated at default — do not move, meaning **no regen ×3 is owed**. That is an argument, not a measurement; verify the md5 before believing it.

## 6. Strategy note for the board (Lon's question, answered)

RC-5's well is thin and the cursor already concedes it: remaining candidates are `g_call_args` (13 sites), `g_scan_hit_start` (8), `g_cap_gen` (8) against GVA's 1038. Each further assignment must clear a real per-crossing toll, and each one also widens the collision surface this gate now watches. **RC-6 (veneer bypass lanes) is the more probable payoff**, and the emitted-hotness ranking for it is already recorded in the s6 cursor (`rt_call_arr` 99 · `rt_coerce_num2_d` 62 · `rt_add` 50).

## 7. Open items

- `bb_func_activate.cpp` collision: probe or fix (owning seat).
- §4 writeback/companion-write: probe, then the §5 one-liner in Lon's routed window.
- RC-5-GVA rail still not re-proved on current HEAD with the min-of-N instrument (inherited from s7).
- Gate is INFORMATIONAL; promote to `--strict` in CI at RC-7.
