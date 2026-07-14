# FINDING 2026-07-14 s60 — EVAL/CODE onto RSP (ζ-on-rsp's last work) + CAS-1 (the GC's first root island)

AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
GOAL: GOAL-SNOBOL4-BB.md — RUNG ZS (ZS-3b) and RUNG GC-U (CAS-1). Base: SCRIP `cb193af5`+s59 → `9e714ed7` → `a15b82ad`.
LON DIRECTIVES THIS SESSION: "EVAL and CODE are already working, just switch them over to RSP" · "implement a
unified GC which handles MARK/ADJUST/SLIDE … the GVA will be its own mmap section … SNOBOL4 will have a
CONDITIONAL ASSIGN stack in separate mmap … scan the live ZETA blocks, the GVA, and all other SPECIAL mmap
structs, for references and do the MARK."

## 1. ZS-3b — EVAL/CODE-RSP (`9e714ed7`). The s59 ruling ("EVAL/CODE = the DEFER shape") executed.
`rt_eval_run` — the 64KB-donation call shim — is **DELETED, grep = 0 tree-wide**. Replaced by `rt_chain_enter`:
RESOLVE (cache / compile / label-registry lookup — a C call is fine, it is not the transfer) → WIRE outside-γ→rcx
and outside-ω→rdx to ONE shared landing → `jmp rax`. The chain is a NEW ACTIVATION that self-allocates on rsp
(`emit_jmp_entry_for_chain` brackets the emission; same K_total = `(32 + region + 15) & ~15` as the PAT$ gate).
No call, no ret, no donated frame.

**The landing reclaims WHOLESALE: `mov rsp, r12`.** r12 is not an arbitrary choice — it is the ONLY register that
can carry the anchor. An xa_flat callee preserves *only its frame register*; r13/r14/r15/rbx/rbp may be clobbered
by the chain. r12 IS the frame register, saved by the jmp-entry prologue at [+24] and restored on BOTH exits ⇒
the anchor survives precisely because the protocol already saves it. This also makes the γ path correct: EVAL/CODE
chains are ONE-SHOT (never β-resumed), so γ leaving rsp at the deep frontier is fine — the landing abandons the
frontier and everything under it in one instruction, the same wholesale-reclaim argument as the seal cut (s59) and
the statement bracket (S10e).

`rt_callregime_run` retains the OLD shim **verbatim** for the single citizen this rung does not own: `LBL__<name>`
main-program pseudo-procs (`rt_goto_transfer` arm 4). Those are procs. Procs convert at PROC-CONV.

### ⚠ MEASURED CORRECTION — THE SHIM MUST HAVE EXACTLY FIVE PUSHES (do not re-derive; it cost one debug cycle)
rsp is 8 mod 16 at C entry (the call pushed the return address). Five pushes = +40B ⇒ rsp ≡ 0 mod 16 at the `jmp`,
and the blob's 16-aligned `sub rsp, K_total` carries that alignment INTO the activation. The first cut pushed a
SIXTH register (rbp) ⇒ rsp ≡ 8 mod 16 through the jmp ⇒ **every C callee reached FROM the chain ran on a misaligned
stack and SEGV'd inside libc's SSE `printf` path** (gdb: `__printf_buffer_init` under `snprintf`, `$rsp` = …`be8`).
rbp must NOT be saved here: it is the align-save register the chains manage themselves (`x86_align_enter/leave`),
and the old shim didn't save it either.
**THE TELL, worth keeping:** simple `EVAL('3 * N + 2')` SURVIVED the defect and printed correctly. Only NESTED EVAL
(`EVAL('EVAL("1 + 2") * 10')`) and CODE crashed — i.e. chain→C→chain re-entrancy, where the misaligned frame reaches
a C callee that actually uses SSE. **A green simple-EVAL proves nothing about alignment.** Probe both shapes.

### Gates
Watermark **IDENTICAL** to s59: m3 305/2 (expr_eval, 141) · m4 304/2/1 (expr_eval, 1017) · DIVERGE=1(1017), same
fail set. Manual-Ch.9 probe vs `/home/claude/x64/bin/sbl` byte-identical for: unevaluated-expression EVAL, string
EVAL, NESTED EVAL, CODE + `:<C>` direct goto + fragment-to-main `F(DONE)` crossing. Smokes sno 7/7×2, icon 14/0,
prolog 5/0, raku 234/20 (documented pre-existing). **C→BB ledger V6 (the EVAL/CODE transfer group) → 0.**
⚠ Pre-existing and NOT mine (verified by stashing to the s59 baseline and re-running): `EVAL("SPAN('012345')")` used
as a pattern → `SNO$MKPAT: compiled pattern blob 'PAT$0' not registered`. That is the SZ-5 `[B-RE]` opaque-DT_P class.

## 2. CAS-1 (`a15b82ad`) — and the finding that HALVES the rung
⭐ **`g_dcap` — THE conditional-assign stack — IS ALREADY ITS OWN BASE-PINNED ISLAND** (`RT_DCAP_ISLAND_BYTES` 4MB via
`rt_slab_region`, live cursor = register rbp in emitted code, built on the `rt_gva_island` precedent, ARCH-ZETA §12).
AND its 24B entry is **deliberately POINTER-FREE** — varname is sealed RO strtab, saved_delta is resolved against the
subject at flush, never stored as a pointer ⇒ **no GC root, no ADJUST entry, nothing to move.** The **GVA** has been an
island since s39. So Lon's "GVA and CAS in their own mmap sections" was already TRUE for the stacks themselves.

What was NOT done — and is the actual GC exposure — is the **DESCR-bearing residue**: `g_capx` (the *FN() commit-value
stack), `g_dfx` (deferred-function frames) and `g_dcf` (the pump's re-entrant cursor stack) were plain **libc realloc**
arrays holding live `DESCR_t`. **libgc does not scan malloc'd memory** (the TR-2 lesson, which cost a `GC_add_roots`
compensation there) ⇒ live workspace pointers were sitting where no collector could see them. CAS-1 moves all three
onto ONE base-pinned island (`rt_cas_carve`, 8MB `rt_slab_region`), fixed caps + a loud bomb instead of doubling —
**an island cannot realloc-move under a collector that has recorded its base** — and exports `rt_cas_roots(&base,&used)`
as the named root area for GC-W-1's MARK and GC-W-2's ADJUST (the scan walks the USED cursor, not the reserve).
NOT touched, named so it is not re-derived: `rt_zcol_push`'s per-iteration COLLECTIONS ride the `ZC_COLLECTION` flavor
switch and belong to ZB-ITER, not here.

### Gates
Watermark IDENTICAL (m3 305/2 · m4 304/2/1 · DIVERGE=1). **GC STRESS SUITE = the same 8 bisect-proven pre-existing
cells** (204_gc_recursive_frames at every level; 212_gc_args_in_flight at STRESS=1) — this, NOT the crosscheck, is the
load-bearing gate for a pointer-bearing family move (TR-3(c)'s lesson: a broken root compensation is a stress-only
corruption the watermark cannot see). Smokes green.

## 3. LADDER STATE
ζ-on-rsp: EVAL/CODE done ⇒ **PROC-CONV is the last transfer** (ordinary procs + LBL__ pseudo-procs are the only
call-regime citizens left), then SLOT-MIGRATE → FLIP. GC: the root islands are now GVA (s39) + dcap (pointer-free) +
CAS (s60) ⇒ next is **GC-U-2 ZA-FLIP → GC-U-4 TR-4 (delete libgc) → GC-W-0/1/2** (the MARK→ADJUST→SLIDE collector,
ARCH-ZETA §6 is the design + manual pins; roots = live ζ (rsp traversal once FLIP lands, arena chain before that) +
GVA + CAS + dictionary buckets).
