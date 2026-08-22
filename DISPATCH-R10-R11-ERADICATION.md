# DISPATCH — r10/r11 ERADICATION LADDER (HQ s256, 2026-08-22)

## THE PLAN, IN LON'S WORDS — READ THIS BEFORE ANY ROW

*"R10 and R11 usage was to be totally eradicated first. Then used for two new things. That was the plan."*

Three sequential states. **They are never true at the same time:**

1. **Now** — r10/r11 scattered as ad-hoc scratch across templates, emitter and the RTX hand-asm.
2. **After this ladder** — **ZERO uses.** *Free* means **EMPTY**. Nobody touching them.
3. **`diag-regs-stmt-and-bb`** — **r10 = SNOBOL4 statement number** at every `IR_STATEMENT_BEGIN`; **r11 = BB node id** at every α and every β of every box. Now they are **ASSIGNED**, and no longer free.

⛔ **"Free" is the PRECONDITION for the claim, not a policy.** A single surviving scratch write clobbers the telemetry at the one moment it is wanted — a crash. That is why the DONE-WHEN is literally zero and is not negotiable.

⛔⛔ **HQ GOT THIS WRONG AT s256 AND RULED THE OPPOSITE** — that ruling is DELETED (`b2a72602`). If you have a clone carrying `FINDING-…-inverted-done-when-…`, discard it. seat3, seat6 and seat8 were each right; HQ was the broken component.

## ⛔ THE SHAPE CHANGED: DISPATCH IS BY **FILE**, NOT BY REGISTER

The original `free-r10` / `free-r11` split is **retired as a work split** (the rows stay as the tracking pair). Reason, measured: chasing r10 alone, seat3 moved 71 scratch sites off r10 **onto r11** — `0ff71be8` r10=136/r11=91 → `ef553d3a` r10=65/r11=152. Both registers are claimed, so the sibling is never a destination. **Every rung below takes ONE FILE (or one idiom family) and drives BOTH registers to zero in it.** That makes the r10→r11 mistake impossible by construction rather than by warning.

## ⛔ DESTINATION RULE — BINDING ON EVERY RUNG

Available: **rax · rcx · rdx · rsi · rdi**, per-site liveness reviewed.
⛔ **NOT r8** — live ANCHOR. ⛔ **NOT r9** — live GVA (`RTCC_GLOBAL_R9_GVA` is a hardcoded `1`, `g_rtcc_on` defaults `1`; this is not a killswitch). ⛔ **NOT r10/r11** — being claimed.
⭐ The bench is narrow on purpose. **Where no caller-saved register is free at a site, SPILL TO THE STACK — do not force a rename.** A forced rename onto an occupied register is the s194 collision class, which cost Milestone 1 once already. seat3 has already landed `rcx` and `rax` at real sites, so both the approach and the liveness-review method are proven.

## RUNG SET — TEMPLATES + EMITTER (217 sites)

| rung | files | sites | notes |
|---|---|---|---|
| **E-1** | `bb_call_fn.cpp` | **86** (r10=52 r11=34) | Prolog trail/unify/carve fast path. `lea r10,[rip+g_pl_trail]` + loads off `[r10+0/24/32]`; r11 a load target. Largest single file, one mechanism. Some sites have r8/r9 occupied by sibling Prolog values — liveness review, expect spills. |
| **E-2** | `bb_scan_{any,alternate,bal,find,many,move,sequence,tab,upto}.cpp`, `bb_idx_{get,set}.cpp`, `bb_initial.cpp`, `bb_subject.cpp`, + tail `bb_glit.cpp` `bb_gcc.cpp` `xa_bb_macro_library.cpp` `bb_lit_scalar.cpp` | **58** (all r11) | ONE uniform idiom: `push r11` … `pop r11` save/restore. Most mechanical rung on the board. |
| **E-3** | `xa_flat.cpp` | **20** (all r11) | Icon's OWN generator-suspend continuation (`rt_gen_save_wires` / `rt_gen_get_{gamma,omega}_wire`), the `ARCH-ICON.md` BB_PUMP model — a separate live mechanism, not γ/ω debris. Re-state it in the contract; do not delete it. |
| **E-4** | `bb_define.cpp` | **15** (r10=2 r11=13) | ⛔ HIGH BLAST RADIUS — every user-written SNOBOL4 procedure activates through this. (a) role-4 shim ω half at `:471`/`:525`: `lea rcx,[γ]; lea r11,[ω]; push r11; push rcx` — r10's half already moved to `rcx`, r11 still carries ω. (b) `:138-145` monitor push-all-8-GPRs: ⭐ under a DEDICATED claim a save/restore **preserves** the value rather than clobbering it, so this site may KEEP naming r10/r11 — but it must be re-stated in `ARCH-SNOBOL4-RTX.md` §2 as *preserving the diagnostic registers* and licensed explicitly in the gate registry. That is the answer to seat3's `q-free-r10-zero-scope`. |
| **E-5** | `emit.cpp`, `bb_call_proc_staged.cpp`, `bb_scan_match.cpp` | **18** | ⛔ HIGH BLAST RADIUS — `emit.cpp:2744` (frameless entry) reads the caller-pushed {γ,ω} pair from `[rsp]` into r10/r11 so `:3052` can build a resume record and `jmp r10`. Nothing enforces that box code between entry and suspend leaves them alone — the shape `FINDING-2026-08-20-s194b/c` convicted. |
| **E-6** | `x86_asm.h` | **20** (r10=9 r11=11) | Encoder internals + the RTCC binary call stub `movabs r10,ptr; call r10` (`0x49 0xBA … 0x41 0xFF 0xD2`), so in BINARY the call mechanism itself clobbers r10. Retargeting it is real work, both media, and it touches every emission — take it alone. |

## RUNG SET — RTX HAND-ASM (228 sites)

The claim is **product-wide**, so hand-asm clobbers the telemetry exactly as a template does. seat6 was right to flag these as never having been in scope.

| rung | files | sites |
|---|---|---|
| **A-1** | `rtx_match.S` | **79** (r10=51 r11=28) |
| **A-2** | `rtx_icn{sub,rel,agg,var,num}.S` | **68** |
| **A-3** | `rtx_alloc.S` `rtx_str.S` | **44** |
| **A-4** | `rtx_zdp.S` `rtx_arith.S` | **33** |

## PER-RUNG DONE-WHEN (identical for all)

1. `grep -rEc "\br1[01][dwb]?\b"` over the rung's files == **0** — except E-4's licensed monitor-save pair, which is named in the contract and the gate registry.
2. Every relocation liveness-reviewed; every spill justified in one line in the FINDING.
3. `ARCH-SNOBOL4-RTX.md` §2 amended in the SAME commit (RULES.md: register-contract rungs amend the contract with the code).
4. Corpus unchanged vs the rung's own measured pre-baseline. ⛔ **Measure your own baseline first and cite it** — the "m3 339/341 m4 338/341+1SKIP" in the old briefs is stale; seat3 measured 320/321 and 319/321+1skip on the crosscheck. HQ's numbers are hypotheses you may falsify (HQ LAW 17), and the corrected number IS a deliverable.
5. Two live gates green (`test_gate_emit_no_lang.sh`, `test_gate_template_medium_invisible.sh`) + `make pristine` EXIT=0.
6. FINDING with the by-file before/after count.

## THE INSTRUMENT

`scripts/test_gate_wreg_claim.sh --strict` / `_binary.sh` is the right gate and HQ's earlier "retire it" call is **withdrawn**. It is a SCOPE gate — *who mentions r10/r11 outside the licensed sites* — and that question is identical whether the claim is γ/ω or statement/BB-id. **Re-point its registry at the new claim; flip `WREG_CLAIM_LIVE=1` at `diag-regs-stmt-and-bb`, not before.** Its currently-pinned counts are in drift (`emit.cpp` pinned occ=6, now 16) — re-pin as each rung lands, so the burn-down is computed and never typed.

## AFTER THE LADDER

`diag-regs-stmt-and-bb` unblocks and is unchanged: r10 ← statement number at `IR_STATEMENT_BEGIN`, r11 ← BB node id at every α and β, BOTH MEDIA through `x86(...)` only, NO-PER-OP-FILTER (every family member or none), no new globals, killswitch `SCRIP_DIAG_REGS=0` proven byte-identical, and a core-dump witness reading both registers. ⭐ Honesty clause from its brief, which every consumer must repeat: **r10 holds the last statement ENTERED, not the faulting statement.**
