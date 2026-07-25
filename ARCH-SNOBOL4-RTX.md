# ARCH-SNOBOL4-RTX.md — The SNOBOL4 Runtime in Optimized x86-64 Assembly

**Minted s162 (2026-07-25, Claude + Lon). READ THIS BEFORE ANY RTX RUNG. It is the register/ABI/build contract; the ladder lives in `GOAL-SNOBOL4-BB.md` §SN4-RTX.**

## 1. RULINGS OF RECORD (Lon, s162 — all four forks resolved)
1. **SYNTAX: Intel, one project-wide.** GNU `as` with `.intel_syntax noprefix` — registers on the left, exactly what `scrip --compile` already emits (verified: `claws5.s` line 1). ONE assembler (as, via `gcc -c`), ONE syntax, everywhere. nasm remains oracle-tooling only (`build_spitbol_archive.sh`).
2. **C BOUNDARY: libc only.** No direct `syscall`. Revisit only if a measured rung nominates an I/O edge.
3. **MIGRATION: dual-build with per-family kill-switch, then eradicate.** C bodies stay as the fallback + bisection oracle until a family is watermark-proven, then that family's C is deleted.
4. **REGISTERS: phase-1 blob pins UNCHANGED; RTX owns the volatile nine internally.** Cross-boundary pin promotion and registerized signatures are phase-2 (RTX-CC), measured, per-family.

## 2. REGISTER CONTRACT
**Blob pins (UNCHANGED in phase 1 — RTX must preserve all of these across every entry/exit):**
| reg | role |
|---|---|
| rbx | arena heap top — DESCR mint pointer (16-byte DESCR in 64-bit) |
| r12 | conditional-assignment stack pointer — its own mmap area (Lon s162; REGISTER-LAYOUT.md's "ζ frame base" entry is an era behind) |
| r13 | Σ subject base ptr |
| r14 | δ subject cursor |
| r15 | Δ subject length/end |
| rsp | ζ + C stack (ONE stack — we do NOT adopt SPITBOL's compsp/osisp two-stack switch; our ζ frames already live on rsp, s157) |
| rbp | ζ frame base |
**These six GP pins are exactly the SysV callee-saved set — the historical reason C runtime interop was free. RTX routines called via C signatures inherit that safety automatically; hand-written entries that clobber any pin must save/restore it explicitly.**

**RTX working set (free at every blob→runtime entry, zero boundary cost):** rax rcx rdx rsi rdi r8 r9 r10 r11 + xmm0-15. Internal role conventions (SPITBOL lessons, adopted):
| reg | RTX internal role |
|---|---|
| rax | value word of the descriptor pair; result; W0 |
| rdx | tag:slen word of the descriptor pair; mul/div companion |
| rsi / rdi | string source / dest — movs/lods/stos/scas/cmps native (SPITBOL xl/xr) |
| rcx | length/count — rep and shift-count native; `cl` for char work (SPITBOL wa) |
| r10 | idiv divisor scratch — keeps rdx clear of the div blast zone (SPITBOL's exact trick) |
| r8 r9 r11 | scratch / secondary args |
| xmm0 | REAL scratch (mxcsr note: set once at init; save/restore around libc math calls — int.asm precedent) |
**Condition results use EFLAGS + setcc/jcc, never SPITBOL's memory `fl` byte. `cld` is a global invariant: set at init; any `std` user restores before return.**

**THE DESCRIPTOR-PAIR CONVENTION (the ABI cornerstone, verified from `src/contracts/descr.h:28`):** `DESCR_t` = 16 bytes = word0 `{DTYPE_t v; uint32_t slen}` + word1 `union{char*s; int64_t i; double r; void*p; ARBLK_t*arr; …}`. Two INTEGER-class eightbytes ⇒ **SysV already passes a by-value DESCR_t in a register pair and returns it in rdx:rax.** Consequence: phase-1 ports that keep the C signatures get descriptor-in-registers in/out FOR FREE — no template churn, no convention invention. Phase-2 (RTX-CC) adds what SysV cannot: S/F signaled in EFLAGS instead of a DT_FAIL compare, >2-arg register staging, multi-value returns.

## 3. BOUNDARY PROTOCOLS
**blob→RTX (phase 1):** every exported symbol keeps its EXACT current C signature. Speed comes from the bodies (no -O0 C, fused fast paths, register discipline, rep-string idioms), not the call convention. Templates untouched ⇒ no `.s` regen, no both-medium work, in this phase.
**blob→RTX (phase 2, RTX-CC):** per-family registerized signatures; every template call-sequence change goes through `x86(...)` encoders in `x86_asm.h` per RULES (TEMPLATE-ONLY EMISSION, BOTH-MEDIUM); `.s` regen ×3 fires.
**RTX→libc:** `and rsp,-16`-equivalent alignment guarantee (track parity; the entry from blob is a `call`, so rsp≡8 mod 16 at entry — one push realigns), save live volatiles on the stack, `call foo@PLT` (m4) / `call foo` (m3 — same source, PLT relaxes), restore. **No SPITBOL-style global reg_block:** libc never inspects SCRIP state (unlike SPITBOL's osint functions, which read compiler registers from globals — int.asm:127-137). The pins are callee-saved, so libc preserves them for free.

## 4. FILE LAYOUT · BUILD · KILL-SWITCH
- **Source:** `src/runtime/rtx/rtx_abi.inc` (this contract as asm macros: pin names, save/restore macros, gate macro) + `src/runtime/rtx/rtx_<family>.s` (alloc, str, call, agg, arith, nv, match, pat, misc). `.intel_syntax noprefix` at top of every file. C code style rules do not apply to `.s`; comment generously — asm needs it (SPITBOL sbl.asm precedent).
- **Build:** each `.s` → `gcc -c` → linked into BOTH `scrip` (mode 3) and `libscrip_rt.so` (mode 4). ONE source, both modes identical by construction. Makefile: add `RTX_OBJS` to both link lines.
- **Kill-switch (per family):** C body renamed `c_<name>` (mechanical, one commit per family). asm exports `<name>`: `cmp byte ptr [rip+rtx_gate_<fam>], 0 ; je c_<name> ; <asm body>`. `runtime_init` reads `SCRIP_RTX_<FAM>` (default ON after the family's gates are green) into the gate bytes. Eradication rung deletes gate + `c_` body. Byte-identity proof at every landing: `SCRIP_RTX_<FAM>=0` run is md5-identical to pristine-C build output on the full crosscheck.

## 5. THE REPLACEMENT INVENTORY (measured s162 across all committed SNOBOL4 `.s` artifacts; ~110 runtime symbols; regenerate mechanically at RTX-1 — do not trust this list blindly)
| family | symbols (principal) | C source |
|---|---|---|
| ALLOC | blk_alloc blk_free (+ descr mint idioms; zls/ζ mark-release stay template-side) | rt/rt_arena.c gc_heap.c zeta_*.c |
| STR | str_concat_d rt_concat rt_lcomp rt_acomp rt_coerce_str_d rt_substr (+SIZE/TRIM/DUPL/REPLACE builtins) | string_ops.c string_builtins.c |
| CALL | rt_proc_call_open(_slim) rt_proc_call_epilogue_(slim_) rt_proc_open_fn rt_call_arr rt_call_named_proc rt_call rt_arg_stage rt_do_return rt_define(_entry) rt_proc_register/set_* rt_proc_reset rt_frame | invocation.c core/name_save.c core/argval.c |
| AGG | rt_subscript_var rt_deref rt_field_var record_register (+TABLE hash/lookup/insert internals) | aggregates.c values.c |
| ARITH | rt_num_arith rt_arith rt_binop_overload rt_coerce_num2_d rt_coerce_num rt_num_pos rt_neg rt_incr rt_decr rt_exp rt_cmp_d | arithmetic.c core/coerce.c |
| NV | NV_GET_fn NV_SET_fn rt_nv_get rt_nv_set rt_gvar_get_int rt_gvar_assign_{str,var,int,descr,pat,concat_parts} rt_gva_island gva_register rt_subject_load_nv | name_binding.c |
| MATCH | rt_match_enter rt_match_variant rt_match_value_* rt_match_replace rt_cap_{push,pop,top} rt_cap_assign_cursor rt_dcap_* rt_defer_{open,step,close,match,get_pat_fn} rt_scan_splice_empty | pattern_match.c |
| PAT | rt_pat_* (lit any notany span break len pos rpos rem tab rtab arb arbno bal alt cat eps fail succeed abort fence fence1 deref refname capture* usercall*) | rt/bb_pat_build.cpp pattern_match.c |
| MISC | rt_faildescr rt_is_truthy rt_last_ok rt_assign_var rt_goto_transfer rt_keyword_read(_snobol4) rt_bomb rt_unhandled_* execute_code_dyn comm_stno core_lib_init dtp_fn_of rt_push_*/rt_pop_void/rt_halt_tos (value-stack residue — AUDIT: may be dead per NO-VSTACK rules) rt_write_any_nl + io | runtime_eval.c keywords.c io_format.c runtime_init.c |
| libc (stays) | memcmp memcpy strchr malloc-family read write | — |

## 6. PORT ORDER AND WHY (heat: s147/s148/s161 — claws5/json are runtime-bound; treebank/calc are emitter-ceremony-bound and keep their own ladder)
ALLOC → STR → CALL → AGG → ARITH → NV → MATCH → PAT → MISC/IO. Alloc first (everything mints); STR next (concat ×38 static in claws5, allocates); CALL is claws5's measured NRETURN lever (93% of time is semantic actions on BOTH engines, uniform 4–5× gap); AGG is claws5 layer C (~11 subscripts/token); PAT is construction-path (size-not-time, s160a) and ports LAST.

## 7. EVERY-RUNG PROTOCOL (the walking session's checklist)
1. **READ FIRST:** this file → the family's C source in full → its `sbl.asm` counterpart for shapes (grep the section; SPITBOL block layouts are NOT ours — steal idioms, never structures) → the SPITBOL manual chapter for every construct the family implements (Lon standing directive; e.g. CALL rung = Ch.13 DEFINE/RETURN/NRETURN/FRETURN incl. by-name args; ARITH = mixed-mode coercion chapter; MATCH = Ch.9 deferred evaluation + p.122 well-foundedness + p.125 FENCE).
2. **PORT** behind the family gate; C renamed `c_*` same commit.
3. **GATES:** smokes 7/7×2 · full crosscheck BOTH modes at current watermark (s159–s161 constant: m3 314/1 · m4 309/4 · DIVERGE=3 — re-prove at session start before touching anything) · beauty · 15-demo board identity · kill-switch md5 byte-identity vs pristine.
4. **RAIL** same-moment A/B (`bench_sno_rail.sh`), label every number `RTX_<FAM>=on/off, RT_OPT=-O0` (RT_OPT now describes only the residual C).
5. **FINDING** doc + **LIVE CURSOR** move + handoff per RULES. `.s` regen ONLY if templates changed (phase 1: never).

## 8. SPITBOL LESSONS — ADOPTED vs REJECTED
**Adopted:** register-pinned runtime discipline; xl/xr/wa physical mapping (rsi/rdi/rcx) for the string engine; rdx/r10 div discipline; low-byte aliases (cl/dl) for char work; hardware stack as THE stack; cld invariant; mxcsr management; boundary save protocol (simplified — no global block).
**Rejected:** Minimal's 9-register ceiling (r8 r9 r11 r14 r15 rbp are UNUSED in all 19,064 lines of sbl.asm — we design for 15); the cp interpreter code-pointer (we are compiled, no interpreter loop); memory `fl` condition byte (EFLAGS); the N-exit-points-after-call convention (our α/β/γ/ω port model already covers multi-exit); two-stack compsp/osisp switching (our ζ is already on rsp); SPITBOL's block/descriptor formats (ours are `src/contracts/descr.h`, full stop).
