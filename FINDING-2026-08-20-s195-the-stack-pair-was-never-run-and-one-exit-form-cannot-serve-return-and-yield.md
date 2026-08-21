# FINDING s195 — THE STACK PAIR HAS NEVER WORKED, AND THE REASON IS THAT ONE EXIT FORM CANNOT SERVE BOTH RETURN AND YIELD
**HQ (Opus 5, 1M), 2026-08-20 s195. Pristine at SCRIP `c8b2c738` (HQ-27 satisfied, `make pristine` rc=0, RT_OPT `-O0`). Oracle-baked refs beside every witness.**
## ⭐⭐⭐ THE HEADLINE — THREE NUMBERS, ONE DIAGNOSIS
| arm | m3 | m4 |
|---|---|---|
| **A — default (r10/r11 wires)** | **82/82** | **82/82** |
| **C — default + ZSM-ALL RBP invariant armed** | **79/82** | **80/82** |
| **D — `SCRIP_WIRE_STACK=1` (stack pair)** | **1/82** | **1/82** |
**(1) THE PASS-THRU GRID IS TOTAL AND GREEN ON THE DEFAULT ARM.** All 80 cells of the ARCH-PASSTHRU combinatorial plan exist and pass: classes 0–9 × {γ-forward, β-retreat} × {`*PAT_var`, `PAT_func()`} × {2, 3 levels}, plus 2 class-7 extras — 82 rows, both modes, oracle-diffed. The witness plan Lon specified at s179 is COMPLETE; nothing needed writing.
**(2) ⛔ BUT THREE OF THOSE GREENS ARE GREEN BY LUCK — LAW 0b IS VIOLATED AND THE PROGRAMS STILL PRINT THE RIGHT ANSWER.** Arming the ZSM RBP invariant (`SCRIP_ZSM=1 SCRIP_ZSM_ALL=1`) turns three passing rows into fatal `β FRAME LOST` bombs. **Every one is a backtrack (`b`) row** — the β direction, exactly where Lon predicted the defect would live:
| witness | class | skew | modes |
|---|---|---|---|
| `ptc8b_fn2` | 8 (MEGA) | **80** | m3 **and** m4 |
| `ptc8b_var2` | 8 (MEGA) | **80** | m3 **and** m4 |
| `ptc6b_var3` | 6 (EVAL) | **10184** | m3 only |
Bomb text (`ptc8b_var2`): `ZSM β node=736 FRAME LOST: α established F=0x7ffcea90c918 (E=0x7ffcea90c918); at β rbp=0x7ffcea90c968 skew=80`. In each case the immediately preceding event is an `ω·` — a box conceded and released frame, and then β arrived at the enclosing box with rbp **above** what that box established at α. That is "the coming out part" (`bb_glue_flat.cpp`, named in-source since s55) reproduced on a checked-in witness rather than on beauty.
⛔ **INSTRUMENT CAVEAT, STATED BEFORE THE CLAIM IS USED.** 79 of 82 rows pass *under* the instrument, so it does not convict wholesale — but two facts are not yet ruled out and must be before these three are treated as compiler defects: (a) **skew=80 is exactly the ZSM event shim's own 10-push depth** (`x86_zsm_ev` pushes rax,rax,rdi,rsi,rdx,rcx,r8,r9,r10,r11); (b) the **γ arm carries a documented whack-owner exemption that the β arm does not**, and `ptc6b_var3`'s 10184 skew appears at a `γ·` line the instrument itself calls legal. The m3≡m4 agreement on both class-8 rows is evidence *for* a real defect; the two caveats above are the falsification work owed. **Do not quote these three as bugs until (a) and (b) are closed.**
**(3) ⛔⛔⛔ THE STACK PAIR HAS NEVER BEEN RUN, AND IT DOES NOT WORK: 1/82, BOTH MODES.** `SCRIP_WIRE_STACK=1` collapses the grid from 82/82 to **1/82** — 81 SEGVs. The lone survivor is `ptc7f_code`, both modes. **Isolated to the EMITTER half:** the collapse is identical (1/82) with the baseline runtime *and* with a runtime built `-DSCRIP_WIRE_STACK_RT`, so the runtime define is not implicated.
⛔ **WHAT s194 ACTUALLY PROVED, AND WHAT IT DID NOT.** Rung 1 (`985dac3b`) is recorded as *"DEFAULT OFF, off-arm byte-identical over 80 programs"* and rung 2 (`42206dd8`) as *"default build byte-identical BY CONSTRUCTION."* Both statements are TRUE and both are about the **off** arm only. **No one ever ran the on arm against the grid.** A killswitch proven inert proves the killswitch, never the feature. The s194 cursor's claim that the directive is *"half-landed"* and that the crash *"MOVES from rip=rtccb to rip=0"* is consistent with this: `rip=0` is not progress toward a cure, it is the stack pair being read out of a frame that no longer holds it.
## ⭐ THE DIAGNOSIS (Lon, in-chat s195, and it is the load-bearing half)
Lon specified the caller protocol — *"the CALLER will do PUSH F; PUSH S, and the CALLEE will do the same as RETURN and FRETURN labels in the emitted code"* — and then corrected himself within the slice, and **the correction is the finding**: *"that is only if returning. If you are yielding, i.e. suspending, it is different. Then you just load the address and JUMP."*
**One exit form cannot serve both, because the two have OPPOSITE FRAME LIFETIMES:**
| exit | activation fate | correct form |
|---|---|---|
| RETURN (γ, done) | frame **retires** | restore depth from the frame → `ret` (pops S); the landing owns `add rsp,8` |
| FRETURN (ω, done) | frame **retires** | restore depth → `add rsp,8` → `ret` (pops F) |
| **γ-SUSPEND (yield)** | frame **stays alive** | **load the address and `jmp`** — the pair and the frame both stay put, because β must still find them |
| β re-entry | resumes | `mov rbp,[rsp]; jmp [rbp−16]` (the frame's own resume slot) |
**The tree today emits ONE form for both** — `bb_glue_wire_exit()` is `jmp [rsp+0]` / `jmp [rsp+8]` with the landing owning `add rsp,16`, and it carries **no depth restoration at all**. Every callee that carves locals leaves rsp below the pair and reads its own locals as a continuation address. **That is the whole 1/82.** ⭐ This is not a new law: ARCH-PASSTHRU law 0a already records Lon's s194 ruling in the same two halves (γ-suspend *"keeps the frame and pushes the retained rbp as the ONE-SLOT β-handle"*), so the design was right in the file and the implementation collapsed it to one form.
⭐ **AND THE RETURN/FRETURN DISCRIMINATION ALREADY EXISTS IN ONE BOX.** `bb_define.cpp:250-255` restores rsp from a saved entry-rsp slot (`mov rsp,[rsi+AB_OFF_ERSP]`, stored at `:76`) and then selects the port by `cmp AB_TC_REG_D, AB_TC_FRETURN ; je L6`. The shape Lon is asking for is already emitted by the DEFINE box; what is missing is that it is not the ONE authority and the suspend road does not share it.
## THE r10/r11 CENSUS (Lon: *"Free up R10 and R11 completely"*)
**232 sites tree-wide**, by role: **79 `push r10`/`pop r10` save-restore sites** · 30 wire-carry (`jmp r10`, `lea_id r10/r11`) · 70 runtime asm (`%r10`/`%r11` in `.c` inline strings + `rtx_*.S`) · ~53 RTCC-bank references, declarations and comments.
⭐ **79 of 232 exist ONLY to save and restore the wires** — Lon's argument (*"they are needing to be saved/restored at every transition anyway"*) measured. The whole `bb_scan_*` family is the shape: `push r10` … `pop r10` bracketing every transition. Those 79 sites are pure tax that the stack pair deletes.
⛔ **SCOPE CORRECTION, OWED TO THE DIRECTIVE.** *"Ensure no code uses R10 or R11 ANYWHERE"* is strictly stronger than freeing the wires. r10/r11 are SysV caller-saved scratch and the RTCC bank claims them by name (`x86_asm.h:12`, *"R10=7, R11=8"*) — the same collision the s194 cursor convicted for the M1 SIGSEGV. Freeing them from the **γ/ω contract** makes them ordinary scratch and is the achievable, ruled goal (law 0a). Forbidding them outright is a separate decision about two general-purpose registers and is **Lon's to make**; it is not implied by the wire migration and is not assumed here.
## WHAT THIS CHANGES ABOUT THE PLAN
The directive *"guarantee EVERYWHERE that all transitions are PUSH F; PUSH S"* is **a campaign, not a flip.** The measured distance is 82/82 → 1/82. The ordered work:
1. **Split the exit into two forms** (retire vs suspend) behind the existing `SCRIP_WIRE_STACK` killswitch — `bb_glue_wire_exit()` becomes two functions, and the retire form gets the depth restoration it has never had.
2. **Make the depth restoration the ONE authority** — `bb_define`'s ERSP restore is the working precedent; the blob/DTP/TINY crossings must share it, not re-spell it (ARCH-PASSTHRU's four protocols are the disease).
3. **Re-measure the grid per class** — the ladder is the gate: a class is not open until its whole witness family is oracle-identical in BOTH modes.
4. **Then** delete the 79 push/pop sites and mint the gate that proves no γ/ω contract rides r10/r11.
5. Close instrument caveats (a) and (b) above before the three β FRAME LOST rows are quoted as defects.
## RECEIPTS
Pristine `make pristine` rc=0 before every arm (HQ-27). Runner `SCRIP/scripts/board_passthru_combo.sh both ptc` (82 rows × 2 modes, oracle-diffed, per-class rollup). Arms A/C/D logs in the session scratchpad. Baseline binaries saved and restored between arms so the A/D comparison is the same tree. Bomb text captured per witness with `tail`, not inferred from exit codes.
