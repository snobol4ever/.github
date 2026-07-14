# FINDING 2026-07-14 s59 — ZS-2 LANDED: jmp-entry DEFER, blob self-allocation on RSP, zls-arena exit

AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
GOAL: GOAL-SNOBOL4-BB.md RUNG ZS-2 (R12-FREE ladder rung 1). Base: SCRIP cb193af5 → this session's commit.

## WHAT LANDED (Lon rulings s58 + s59 in-session: "There is no CALL/RET... It is a JUMP and a JUMP BACK";
## "call a function [to look up], then WIRE the outside γ/ω, and JUMP to the BB"; "BBs do their own [allocation]")
1. **The transfer.** bb_match_defer.cpp blob arm: α resolves fn via rt_defer_get_pat_fn (a LOOKUP — C calls are
   fine for resolution, never for transfer), wires OUTSIDE-γ→rcx and OUTSIDE-ω→rdx (x86_lea_id internal labels),
   `jmp rax`. β is uniformly `jmp qword [rsp+0]`. NO call, NO ret, NO eax code, NO caller-side allocation.
   rt_zls_alloc / rt_fn_frame_bytes / rt_zls_release deleted from the template — grep-clean.
2. **The activation.** New xa_flat jmp-entry regime (g_emit.flat_jmp_entry + flat_frame_bytes, set by the blob
   builders BEFORE emission from zls_g_region): prologue `sub rsp,K_total`; 32B WIRE HEADER at [rsp+0..31]
   ([+0] pad, [+8] γ wire ← rcx, [+16] ω wire ← rdx, [+24] saved frame reg); zr = rsp+32 (region base — every
   FR() offset byte-identical to call-regime); rep-stosb zero; gva reload; anchor. NO esi dispatch.
3. **γ SUSPENDS at the deep frontier.** Epilogue γ-half pushes the 16B RESUME RECORD at the frontier —
   [rsp+0]=β-landing address, [rsp+8]=region base — then jmps the γ wire with the caller's frame reg restored.
   The β landing (`<prefix>_res`, before lbl_β) drops the landing word, pops the frame reg, falls into the
   chain's existing resume dispatch (`jmp [zr+resume_slot]` — NCB-2 machinery untouched).
4. **ω UNWINDS ABSOLUTELY.** `lea rsp,[zr+K_total-32]` (pre-entry rsp reconstructed from the pinned frame reg),
   restore frame reg, jmp the ω wire.
5. **Regime coverage.** rtpat/rtlen/rtbrk (bb_pat_build.cpp) + the lower-synthetic PAT$N pattern procs (all four
   driver proc-emission loops, via emit_jmp_entry_for_patproc — PAT$ names are unreachable by user code and
   consumed ONLY through SNO$MKPAT → DT_P → DEFER). The callout pump (*X / DT_E→any) is unchanged internally
   and suspends a 16B one-shot cell whose [+0] wire lands its own exhaust stub → the shared β needs no guard.
6. **FZ-5b shortcut RETIRED this rung** (its inlined heads are call-regime; the lower-side LIT_STRING mark stays
   in the IR for PROC-CONV to consume). zeta_storage.c:111 → one 16B ZK_RAW pad quad (offset stability).
   x86_rep_stosb encoder added (f3 aa, s58a recipe).

## TWO MEASURED CORRECTIONS — PROC-CONV MUST HONOR BOTH
- **The frontier is the only address β gets.** First cut stored the β wire in the header and had β do
  `jmp [rsp+0]` expecting rsp at the header — WRONG whenever the blob suspended with live INTERIOR cells
  (nested DEFER, ARBNO chains): at β-time the LIFO law hands back the DEEP FRONTIER, not the header
  (measured: rip=0x500000002 — a DESCR executed as code). γ must LEAVE THE RESUME RECORD AT THE FRONTIER.
- **Seal cuts reach ω at any depth.** FENCE/ABORT cut edges jump to lbl_ω WITHOUT the popping cascade
  (lower_snobol4.c:1142 "right of the fence: cut to the SEAL target"), so a relative `add rsp,K` unwind is
  wrong there (measured: 5 fence-class regressions 113/119/129/149/150, both modes). The ω unwind must be
  ABSOLUTE from the pinned frame reg. With that, seal cuts lawfully abandon suspended interior activations —
  the same wholesale-reclaim argument as the statement bracket (S10e).

## GATES (all green, this tree)
- T1 `"(12,(3,45,(6)),78)"` MATCH + T2 `"(12,(34)"` correct-FAIL, BOTH modes — the recursive *LIST class that
  SEGV'd at baseline (rip=rsp=r12). Locked into corpus as crosscheck/patterns/178_pat_recursive_star_list_zs2.
- Crosscheck m3 305/2 (expr_eval, 141) · m4 304/2/1 (expr_eval, 1017) · DIVERGE=1(1017) — fail set IDENTICAL to
  the s58 watermark; the +1 on each PASS count is test 178.
- ZS-0 gate: pattern_bt `result: 500000`, ZLS1 allocs 5,500,011 → **0** (rt_zls_alloc never called — the atexit
  report never even registers). Smoke 7/7×2. Benchmark/feature/demo .s artifacts regenerated ("ZS-2" commits;
  diffs shrink: the jmp-entry protocol is leaner than call+zls round-trips).

## LADDER STATE
ZS-2 DONE → **PROC-CONV is next** (rt.c:549/878/892/980 + :591/:608 family; icon/prolog/raku smokes join the
gate; FZ-5b restoration belongs there). Then SLOT-MIGRATE → FLIP. EVAL/CODE ruling recorded in the goal file:
same shape as DEFER — resolve by function call, wire, jump/jump-back; CODE = deferred execution (NCB-3b's
rt_eval_run shim retirement converts to this exact protocol; ZS-2 is the reference implementation).
