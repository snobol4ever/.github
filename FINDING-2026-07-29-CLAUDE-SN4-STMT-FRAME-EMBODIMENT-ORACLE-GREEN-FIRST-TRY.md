# FINDING 2026-07-29 (s21x-c) — SN4 STATEMENT-FRAME HAND EMBODIMENT: ORACLE-GREEN FIRST TRY, AND THE VALUE SPINE ALREADY SELF-CARVES AT HEAD

**Design of record:** RBP/RSP FRAMES + FORTH-STYLE VARIABLE-LENGTH ζ CELLS, statement scope law — the s21x-c LON DIRECTIVE block atop `GOAL-SNOBOL4-BB.md` (per-BB one-instruction carves; sliding RSP offsets; RBP only at STATEMENT/FUNCTION/ARBNO/FENCE1; NO function-level processing; call = IR_SAVE_RESTORE + IR_CALL, the save slots being the ONLY ζ in the call).

## BASELINE RE-MEASURED AT HEAD (the s21x-b 311 counts are STALE — corpus grew to 334)
`test_broad_corpus_snobol4.sh`, RT_OPT=-O0: **m3 PASS=329 FAIL=5 · m4 PASS=324 FAIL=2 SKIP=8 (334 total; M3=18s M4=22s).**
FAIL membership (record, for the post-diff discipline): m3 = {test_case, 140_pat_eval_double_fn_trick, 141_pat_eval_double_fn_arbno, 160_pat_alt_inner_gen_resume, omega_driver} · m4 = {test_case, 160_pat_alt_inner_gen_resume}. No compiler source was touched this session; this baseline carries.

## THE EMBODIMENT (per the embodiment-first precedent: seeds before encoders)
Witness `SCRIP/seed/test_sno_stmt_frame_1.sno`: `DEFINE('ADD3(N)')` · body `ADD3 = N + 3 :(RETURN)` · `MAIN OUTPUT = ADD3(4 * 2) + 1`. SPITBOL oracle (`sbl -b`): `12`.
Hand-written `SCRIP/seed/test_sno_stmt_frame_1.s` in the target shape assembled, linked against `libscrip_rt.so`, and printed `12` — **oracle-exact on the first assembly**. Shape proven live:
- **STATEMENT bracket** = `push rbp; mov rbp,rsp; sub rsp,8` forward / `mov rsp,rbp; pop rbp` backward (16B, C-call parity preserved by construction). Fail edges jump the bracket cut — zero hand-counted pops anywhere.
- **Per-BB carves**: 5 × `sub rsp,16` (var/lit RESULT cells) + FORTH-net binops reading TOS-relative sliding offsets; assign consumes TOS.
- **IR_SAVE_RESTORE (role 0), inlined**: ONE `sub rsp,32` = the save slots (save N + fname, bind N←arg cell, fname←null per manual Ch.8) — **the only ζ in the entire call process**.
- **IR_CALL**: header {pad, caller rbp, γ wire, ω wire}, `mov rbp,rsp`, then a DIRECT `jmp` into the body — constant-folded DEFINE emits NOTHING else at runtime: no stub proc, no `rt_proc_register/set_fn/set_nparams/set_frame_bytes/set_jmpentry`, no `rt_flat_wire_adopt`, no `rt_goto_transfer`, no `rt_flat_ret_snap`, no `rt_proc_call_open*/epilogue*`.
- **RETURN floater** = `mov rsp,rbp` (reclaims every statement/BB carve from ANY depth), restore caller rbp, `jmp` γ wire. **Return value = the fname global at RETURN** — confirmed both in the legacy emission (its γ wire reads the fname GVA cell before restoring it) and in the embodiment.

## LEGACY vs TARGET, same program (regenerate legacy: `SCRIP_ASM_SEP=0 scrip --compile seed/test_sno_stmt_frame_1.sno`)
LEGACY: 3 graph carves (`sub rsp,240/240/216` = 696B standing frames) + 2 `rep stosb` zero-fill runs + slot0 zeroing + 21 proc-linkage runtime call sites + a whole stub proc + frame_bytes registration. TARGET: **0 graph carves, 0 zero-fills, 0 proc-linkage calls**; peak live ζ ≈ 176B, all of it named by the BB that carved it.

## ⭐ DISCOVERY — THE DIRECTIVE IS HALF-LANDED AT HEAD
The legacy body statement (`ADD3 = N + 3`) ALREADY emits per-BB self-carves with sliding TOS offsets (`sub rsp,16` at var/lit α, binop net −16, assign net −16) — the s191 "99.999% inside the BB's" machinery (zeta_storage.c:269) live in production. What remains legacy is exactly the other half: the graph carves + fills, granted flat slots for call-bearing trees (the FORTH registration DECLINES any tree containing a call — main's statement fell back to flat slots wholesale), wires-in-frame, and the function-level linkage family.

## UNPROVEN (named, not skipped)
(a) **ω/FRETURN path emitted but UNEXERCISED** (witness only takes γ). (b) **Recursion unproven** — the shape is re-entrant by construction (fresh header + fresh save slots per call, no static frame anywhere) but no witness has run it. (c) Multi-statement bodies, ARBNO/FENCE1 brackets, pattern statements: untouched. (d) Alignment law (bracket 16B / header 32B / cells 16B ⇒ every C call ≡0 mod 16) held empirically (no movaps fault through core_lib_init/NV_SET/rt_add/rt_mul); not formally audited.

## NEXT EXECUTABLE, IN ORDER
1. **Witness 2 = recursion + FRETURN** (factorial-shaped: `F(N) = LT(N,1) 1 :S(RETURN)` else `F = N * F(N - 1)`), same hand method — proves re-entrancy and the ω wire before any encoder learns the shape.
2. **Additive encoders** in `x86_asm.h` (BB-CODEGEN DESIGN SET binds: R2/R7/R9/R10, one medium invisible): statement bracket pair, IR_CALL header, RETURN/FRETURN floaters, save-slot carve.
3. **Per-graph all-or-nothing regime** (classifier + env switch) — mixed regimes inside one graph are the s188 disease; the watermark may only add passes; fail-set membership diffed programmatically against the baseline above.

## WITNESS 2 (same session) — RECURSION + FRETURN: ORACLE-GREEN FIRST TRY
`SCRIP/seed/test_sno_stmt_frame_2.{sno,s}` — factorial(5) + a zero-param always-FRETURN function; oracle `120` then `7`, matched exactly (legacy emission also verified oracle-exact first: 1056 lines, in-subset). Proven live, first assembly:
- **RECURSION**: five nested activations = fresh 32B save slots + fresh 32B IR_CALL header per call, pure machine-stack LIFO. No .bss depth arenas, no counters, no frame_bytes. **Dynamic scoping correct by construction**: per-BB operand cells snapshot the globals BEFORE the inner call rebinds them — the left `N` cell survives the recursive rebind untouched.
- **FRETURN / ω wire**: NOPE() FRETURNs; ω wire restores the fname save slot; the failing call fails its statement; the STATEMENT bracket cut reclaims every live cell (zero hand-counted pops); the next statement runs.
- **Per-call return wires**: each call site owns its γ/ω labels; wires ride the frame header, so recursion needs nothing further.
- **nparams=0 IR_SAVE_RESTORE variant**: one 16B slot (fname only); on γ the slot is REUSED as the call's RESULT cell — net +16 for a zero-arg call.
- **Two constant-folded DEFINEs** emit nothing at runtime. **Both floaters** (RETURN + FRETURN) now exercised.
- New runtime shapes taken verbatim from the legacy emission: `rt_cmp_d(&a,&b)→sign` (LE fails on `jg`), `rt_sub` (rt_add mirror). SCOPE NOTE recorded in the seed: LE emitted as the int/real fast shape only — the op75 coercion tower is emitter work, out of embodiment scope.
STILL UNPROVEN: multi-arg (>1) and prototype-locals save sets (mechanical extensions of the slot block); pattern statements; ARBNO/FENCE1 brackets; string-descr literals.
