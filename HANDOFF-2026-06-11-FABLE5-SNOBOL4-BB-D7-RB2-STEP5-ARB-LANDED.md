# HANDOFF — 2026-06-11 · Fable 5 · SNOBOL4-BB · D7-RB-2 step-5/5 ARB LANDED → D7-RB-2 COMPLETE

**SCRIP commit: `fb0b825` (pushed). Pattern-builder `ins*` = 0 — the D7-RB-2 completion criterion.**

## What landed (6 files, +61/−45)

1. **`src/runtime/pattern_match.c` + `src/include/dtp.h`** — `bb_arb_proto[104]` + `bb_arb_proto_desc {81,32,16,24,-1,-1,-1}` (entry@81, β@32, γ-slot@16, ω-slot@24, no build-time operand fills; +8 dword = saved-δ scratch, +12 dword = extension counter). Bytes derived by ASSEMBLING a .s source with `as` and extracting via objcopy — never hand-encoded. SEMANTIC FIX vs the old inline proto: β increments the counter BEFORE computing the extension, so the first retry extends by 1 (the old proto re-matched null once redundantly). SPITBOL Ch.6 (ARB = shortest first, expand per retry) + Ch.18 p.203 manual-verified.
2. **`src/emitter/BB_templates/bb_pattern_arb.cpp`** — regenerated whole: 24 `ins*` → 0; pure `x86()` marshal (rdi=FRQ frag slot, rsi=RIPSEAL proto, edx=104, rcx=RIPSEAL desc, r8d/r9d=0) → stack-align → `call rt_pattern_build` → `jmp γ`; proto+desc inline as TEXT `raw .byte`/`.long`; `def β; jmp ω`. Byte-identical structure to the proven `bb_pattern_nullary.cpp`.
3. **`src/interp/IR_interp.c`** — `case IR_PATTERN_ARB` m2 build arm (mirrors REM: GC_MALLOC frag, `rt_pattern_build(frag, bb_arb_proto, 104, &bb_arb_proto_desc, 0, NULL)`, frag→`IR_EXEC(bb).counter`, state=1).
4. **`src/lower/nl/lower_snobol4.c`** — TT_VAR `"ARB"`/`"arb"` → `IR_PATTERN_ARB` in the predefined-pattern name block (joins REM/FAIL/SUCCEED/FENCE/ABORT). REBASE NOTE: landed as `fb0b825` after two peer rebases (d07afad bb_disj fixup — disjoint; 662f249 LOWER PROMOTION nl/ fold-up — rename-detection carried the edit into `src/lower/lower_snobol4.c`, clean-rebuilt + full fast-gate re-run green post-rebase).
5. **`src/emitter/emit_bb.c`** — (a) ARB FILL slot `bb_slot_alloc32` → `bb_slot_alloc24` (frag held at 3-field/24B per ladder); (b) `descr_chain_arity`: ARB + FENCE + ABORT added to the IR_PATTERN_* 0-arity leaf list. FENCE/ABORT were a LATENT step-3 omission — probed INERT today (`P=FENCE` m4 worked because lower-time `ir_operand_push` operands survive the `default:-1` stack-reset for these shapes) but the reset was a hazard for future mixed chains.

## Verification (all green before commit)

- **rt-level unit harness 6/6** (gcc against libscrip_rt; source preserved at the bottom of this doc): ARB`'C'`/ABC→3 (β-extend ×2) · ARB`'C'`/ABD→−1 (exhaust) · ARB`'B'`/ABAB→2 (shortest-first) · ARB`'A'`/ABC→1 (null match) · ARB`'C'`/""→−1 (no hang) · `'A'`(ARB`'X'`)/ABC→−1 (δ-restore in nested CAT). Harness builds frags via `rt_pattern_build`, stitches via `rt_pattern_stitch_cat`, hand-builds the 36-byte head, drives `rt_dtp_run`. **This is currently the ONLY exercise of the CAT stitch — see FINDING.**
- **Family probes 10/10** m2==m3==m4==sbl: ARB/REM/FAIL/SPAN(+nomatch)/ANY/LEN(+nomatch)/ALT/FENCE, named-var subject, `:S/F` branch shape.
- **smoke** 7/7/7 HARD · **pat-rung** M2 19/19 · M3 19/19 · M4 16/19 (050/051/054 = pre-existing b11a963, untouched, FIX-FORWARD ONLY) · **fence** `test_gate_sno_pat_reg.sh` HARD · **beauty** 3/17 (≥ documented 1/17 floor).
- **Corpus stash-baseline BYTE-IDENTICAL all three modes**: with-change AND `git stash` baseline both 172(m2)/156(m3)/144(m4 PASS, 115 FAIL, 21 SKIP of 280); FAIL/SKIP name-set diff EMPTY. The 144-vs-148 "floor" delta is CONTAINER DRIFT exactly per this goal's learned-fact ("always stash-baseline before treating a count as a regression") — non-decreasing HELD by the strongest possible standard.

## ⚠️ FINDING → next rung D7-RB-2b (recorded in the goal-file ladder)

**No NL lowering produces `IR_PATTERN_CAT`.** `bb_pattern_cat` (step-1/5) and its m2 arm are converted but UNREACHED: buildable TT_SEQ falls to the legacy orphan `sno_has_pat` arm (`lower_snobol4.c:582`). Live consequence: `P = 'A' ARB 'C'` / `'XABYC'` → m2/m3/sbl `matched`, m4 `nomatch` (the legacy-SEQ m4 divergence class — NOT a builder gap). FIX (D7-RB-2b): in `lower_assign`, BEFORE the orphan arm, admit buildable TT_SEQ (flatten; every leaf admissible by the existing TT_VAR-name/primitive-arg rules or QLIT) → recurse per kid → pairwise left-assoc `IR_PATTERN_CAT` mirroring the TT_ALT all-QLIT arm (:511) → DTP_ASSIGN consumer. That transplants the B6 TT_SEQ recipe to NL and lets ARB's β-regen fire through real programs and the pat-rung ARB cases.

## Facts that cost time (do not re-derive)

- `pgrep -f <script-name>` from a polling loop matches the POLLING COMMAND's own string — backgrounded-runner liveness must be checked by PID (`kill -0 $pid`), not pattern.
- `test_mode4_only_corpus_snobol4.sh` runs ALL THREE modes (m2/m3 informational) and takes ~306s; background with `setsid ... &` and poll the pid.
- Fresh container: mode-4 anything requires `make libscrip_rt` (smoke reads `<mode4-build-failed>` without it); SPITBOL needs the `x64` clone BEFORE `build_spitbol_oracle.sh`.
- `rt_dtp_run` ABI: rdi=head (slot+0 entry; it WRITES success/fail label addrs to +8/+16), rsi→r13=Σ, rdx→r14=δ, rcx→r15=Δ; returns final r14 or −1. Head = the 36-byte blob in `rt_dtp_head_build`; a harness can hand-build it (copy bytes, fill +0, patch `*frag->γ_site = blob+24`, `*frag->ω_site = blob+30`) to avoid the NV/gvar machinery.
- Proto byte derivation pipeline: `.intel_syntax noprefix` .s with the 32-byte `.quad 0` header + labeled code → `as` → `objcopy -O binary --only-section=.text` → python hex-dump twice (C array for pattern_match.c, `.byte` lines for the template's TEXT inline). `nm` on `.set` symbols gives entry_off/total_len. One binary, two renderings, zero divergence.

## Unit harness (reproduce: gcc -I src/include -L out -lscrip_rt -Wl,-rpath,$PWD/out)

Six cases as described above; structure: `pat_pool_init()` → `rt_pattern_build` per element → `rt_pattern_stitch_cat` → hand-built 36-byte head → `rt_dtp_run(head, subj, 0, len)`. LIT frags built with `rt_pattern_build(&lit, bb_lit_proto, 125, &bb_lit_proto_desc, <len>, "<str>")` (desc op1@0=string ptr, op2@8=len).
