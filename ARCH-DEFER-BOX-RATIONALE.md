# ARCH-DEFER-BOX-RATIONALE.md — the design rationale that used to sit in `bb_match_defer.cpp`'s comment calls

⭐ **WHY THIS FILE EXISTS.** `src/templates/bb/bb_match_defer.cpp` carried **10,056 characters of prose**
inside its 15 `x86("comment", ...)` calls. CONVERSION CV1/R1 (GOAL-BB-FIXUP.md) requires each such call to
carry only the bare `IR_<KIND>` the box dispatches from, so the prose had to go.

⛔ **AND IT WAS DEAD DATA — WHICH IS NOT WHAT THE FILE LOOKS LIKE.** The natural reading is that this prose
was being emitted into every `.s`. It was not. `src/templates/x86/x86_asm.h:1613` reads
`if (!strcmp(mnem, "comment")) return std::string();` — **the `comment` mnemonic emits nothing, in either
medium.** Measured on the pre-edit binary: `beauty.sno` fires `IR_MATCH_DEFER` 75 times and `porter.sno` 124
times, and the emitted `.s` of each contains **zero** occurrences of any of this text. All 10,056 characters
lived in `libscrip_rt.so`'s rodata and were discarded at emission; the `.so` is 8,256 bytes smaller without
them. ⭐ Recorded because the mistake is easy and was made once already while doing this very edit: a
`"comment"` string in a template reads like output and is not.

⛔ **IT IS RECORDED HERE RATHER THAN DELETED because none of it existed anywhere else.** Checked before the
edit: `SECOND and LAST operator-BB` and `WHOLE FRAME is the watermark` returned ZERO hits across all 964
files of `.github`. This is the only copy. It is design rationale for the DEFER box — the ζ-FRAME
push-rbp immunity argument, the Defect C analysis, the killswitch-polarity lesson, the inline-cache and
merged-probe derivations — and it is exactly the class of knowledge RULES.md's own corollary says must live
in ONE versioned file rather than in an unversioned one.

⚠️ **This is a VERBATIM transcript, not a rewrite.** Text extracted programmatically from the pre-edit
source; the arm tags below are the terse comments that replaced each block, so a reader can go from an
emitted `.s` comment straight to the paragraph that used to be there.

| emitted tag | pre-edit line | prose chars |
|---|---|---|
| `IR_MATCH_DEFER (ZS-2 jmp-entry)` | 73 | 31 |
| `IR_MATCH_DEFER ζ-frame` | 76 | 1229 |
| `IR_MATCH_DEFER sealed` | 80 | 69 |
| `IR_MATCH_DEFER cell` | 83 | 223 |
| `IR_MATCH_DEFER patv-fast` | 92 | 967 |
| `IR_MATCH_DEFER $V-slot` | 112 | 269 |
| `IR_MATCH_DEFER probe-head` | 163 | 1628 |
| `IR_MATCH_DEFER inline-read` | 206 | 1248 |
| `IR_MATCH_DEFER ic` | 237 | 1832 |
| `IR_MATCH_DEFER resolve` | 257 | 940 |
| `IR_MATCH_DEFER ic-hit` | 266 | 91 |
| `IR_MATCH_DEFER probe-str` | 294 | 157 |
| `IR_MATCH_DEFER $V-scalar` | 316 | 177 |
| `IR_MATCH_DEFER pseudo-record` | 367 | 1122 |
| `IR_MATCH_DEFER β unsealed-carve` | 396 | 73 |

## `IR_MATCH_DEFER (ZS-2 jmp-entry)` — was line 73

IR_MATCH_DEFER (ZS-2 jmp-entry)


## `IR_MATCH_DEFER ζ-frame` — was line 76

THREE ZETAS ζ-FRAME (s85): *P DEFER establishes its own RBP activation frame at alpha -- the SECOND and LAST operator-BB (with MATCH_BEGIN/ζ-STANDING) permitted to push rbp.  Replaces the s137 rsp-watermark save (FRQ(op_off)=rsp, restored rsp-relatively at every exit): that save/restore pair is Defect C -- both ends compute [rsp#+op_off] against WHATEVER rsp happens to be AT THAT POINT, sound only if the deferred target's own body never carves stack without self-releasing before jumping back through the wire, which the non-popping ζ-SPINE law (committed growth released only by bracket whacks) guarantees it does NOT.  rbp does not move across the jmp-entry wire transfer (the callee's own carves are rsp-relative, never touch our rbp), so a push here is immune by construction -- the exact argument bb_match_capture.cpp's s81/s83 activation-frame arm already uses for the SAVE/IMM-or-COND capture-family crossing.  No slot registration for spine-only BBs is added here: the frame exists so THEY can register into it (ARBNO's chained-K0/K16-defer bodies, per bb_match_arbno.cpp's own op_frame_need consultation), not so this box owns extra state of its own -- op_off is unused on this arm; the WHOLE FRAME is the watermark.


## `IR_MATCH_DEFER sealed` — was line 80

s137 SEALED defer: fence-demarked sync point (watermark in defer.pad)


## `IR_MATCH_DEFER cell` — was line 83

s142 cell reworked s108: the cell holds the DTP (write-once => the DTP is as fixed as the fn once armed), fn loaded at [dtp+0] (the pinned offset-0 assert), so the cached fast path still carries the DTP into the blob in rdx


## `IR_MATCH_DEFER patv-fast` — was line 92

⭐ PT-3 ROUND-TRIP COLLAPSE (SCRIP_PATV_FAST): the 3-call C round trip rt_patv_defer_get_pat_dtp -> patv_slot -> dtp_fn_of, measured at 59.4% of ALL treebank-match cycles (FINDING s168 PT-0/1/2), is spent ONLY on the arms that need it.  WHAT MAKES THE SKIP PROVABLE, not merely plausible: dtp_fn_of is `if (!h->fn && h->rcp) { lazy-compile }; return h->fn;` -- so once fn is MATERIALIZED it is a PURE function returning [dtp+0], which is the very word the cold arm below re-loads by hand two lines later.  Reproduce patv_slot's snap arm inline (h=[rbp-24], snap=[h+32], nsnap=[h+40] -- the offsets DTP_t's own definition publishes for asm consumers), take the DT_P/payload test in the GVA arm's already-verified spelling, and if fn is non-null we are DONE with zero calls.  EVERY other case -- no DTP, no snap, index past nsnap, not DT_P, null payload, fn not yet compiled -- falls through to the UNCHANGED cold path, so the arm cannot answer differently, only sooner.


## `IR_MATCH_DEFER $V-slot` — was line 112

PB-1s (s108) $V PER-CONSTRUCTION SLOT: value = snap[i] of the DTP this activation runs under ([rbp-24], preamble-stored from entry rdx); the PAT$n$V global is stage-2 marshalling whose lifetime ends at MKPAT -- per-site cell reads were the case_driver cycle/stale class


## `IR_MATCH_DEFER probe-head` — was line 163

⭐⭐ FUSED PROBE HEAD (ceo s283, row perf-pattern-defer-capture-layer-cure): the one-char-string arm (defer_inline, s261) and the resolved-fn inline cache (defer_ic, slice a) each loaded the SAME (key,cell) pair and compared the SAME baked varname back to back -- and the one-char arm's DT_S/len==1 preconditions ran FIRST on every position even when the deferred value is a PATTERN (this kernel: tag DT_P=8, so the one-char probe was a structurally-guaranteed miss costing ~9 insns per anchor position, the ARM-A class of a probe that cannot fire).  MEASURED before this cure (pattern_bt m4, 2M iter, perf annotate): n58_match_defer_bx 28.9%% of the kernel with the duplicated head executed per position.  THIS ARM: ONE pair load, ONE key compare, ONE cell load + null test (⛔ the standalone one-char arm dereferenced cell WITHOUT a null test -- latent, inherited from s261, fixed here for free), ONE tag read, then a TAG BRANCH routes to the one-char tail (DT_S) or the fn-cache tail (DT_P); every miss lands on the UNCHANGED cold call at L22.  ⛔ IT CANNOT ANSWER DIFFERENTLY, ONLY SOONER -- both tails are byte-for-byte the originals' tails, every fall-through reaches the same cold path, and a multi-char DT_S goes cold exactly as before (old route: one-char len-miss -> fn-cache tag-miss -> cold; new route: len-miss -> cold, same destination two compares earlier).  ⭐ KILLSWITCH MATRIX PRESERVED: this fused arm emits only when BOTH SCRIP_DEFER_INLINE and SCRIP_DEFER_IC are on (the default); either switch off restores that arm's ORIGINAL standalone emission verbatim below, so the A/B story of each original cure survives.


## `IR_MATCH_DEFER inline-read` — was line 206

⭐⭐⭐ THE DEFERRED READ, INLINE, WITH NO CALL AT ALL (hq_P s261).  After the cell cache the remaining cost was not the lookup -- it was the CEREMONY of reaching it: an xfer_enter/leave push-pop of r13/r14/r15, an rtccb save/restore of r8/r9, a PLT call, and a branch chain, ~120 Ir per execution for what is finally 'read a cell, compare one byte'.  This arm does the whole common case in ~18 instructions: confirm the site's cached (key,cell) pair still names THIS baked literal, confirm the value is a one-character string, and compare that character against the subject at the cursor.  ⛔ WHY IT CANNOT ANSWER DIFFERENTLY, ONLY SOONER -- the same argument the PT-3 arm above already relies on: EVERY other case falls through to L30 and the UNCHANGED call.  A cold slot, a different name at a shared slot, a non-string value, a multi-character string, a pattern, an unevaluated expression -- all take the old path untouched.  ⭐ THE REGISTER MAP IS NOT ASSUMED, IT IS VERIFIED: bb_match_break's emitted scan reads 'movzx esi, byte ptr [r13+rcx]' after 'movsxd rcx, r14d' and 'cmp ecx, r15d', so r13 is the subject base, r14d the cursor and r15d the length.  This arm reuses that exact idiom rather than a second guess about which register holds what.


## `IR_MATCH_DEFER ic` — was line 237

⭐⭐ THE RESOLVED-fn INLINE CACHE (hq_P, slice (a) of perf-pattern-defer-capture-layer-cure).  The merged arm below already resolves ONCE instead of twice, and the runtime already remembers the site's NV cell in the g_sno_defer_cells pair -- but EVERY iteration still paid a full C call to be told a thing the pair could answer here: xfer_enter's three wire pushes, the argument marshalling, call/ret, rt_defer_probe_run's own prologue, the (now always_inline) slot compare, and the load of [dtp+0].  MEASURED at fixed work on pattern_bt, m4 -O0: rt_defer_probe_run 15.1% + rt_defer_cell_read 10.5% + dtp_fn_of 5.1% of the whole program, with the call ceremony itself inside n58_match_defer_a's 25.7%.  This arm answers the DT_P-with-materialised-fn case with ZERO calls and zero stack traffic, in the same register contract the call publishes: rax=fn, rdx=dtp.  ⛔ IT CANNOT ANSWER DIFFERENTLY, ONLY SOONER -- exactly the PT-3 argument the $V arm above already relies on.  Six conditions must ALL hold or we fall through to the unmodified call: the pair's key still equals THIS site's baked varname (pointer identity, so a collision or a re-resolution MISSES rather than lying), a non-null cell, cell->v == DT_P, a non-null payload, and a non-null [dtp+0].  fn is read out of the LIVE DTP every iteration and is never memoised beside the pair, so reassigning the deferred variable is seen immediately -- a new DTP has a different pointer and a different fn, and a non-pattern value fails the DT_P test.  ⭐ NO NEW GLOBAL: the pair is the EXISTING slot the runtime already writes; this arm only READS it, and it is the runtime's own write that arms it on the first iteration.  ⛔ The killswitch SCRIP_DEFER_MERGE=0 also disarms this for free -- with merging off the runtime never writes the pair, the key stays 0, and every probe misses.


## `IR_MATCH_DEFER resolve` — was line 257

⭐ ONE RESOLUTION, NOT TWO (hq_P s260): this site used to call rt_defer_get_pat_dtp and then, on the not-a-pattern fall-through, rt_defer_run_all -- and BOTH opened by resolving the SAME baked literal through the global name table, back to back, with only a test and a jz between them.  Measured on roman.sno: rt_defer_nv_read'rt_defer_get_pat_dtp and rt_defer_nv_read'rt_defer_run_all at 594,060 Ir EACH -- identical counts -- pushing NV_GET_fn to 19.35% of the whole program with another 5.91% of __strcmp_avx2 under it.  rt_defer_probe_run resolves once and answers both questions in registers: rax=fn (0 => not a pattern, take L0), rdx=dtp when it IS a pattern and the new cursor when it is not.  The string half therefore needs no call at all -- L0 just moves edx into eax.  esi now carries cur_delta where it used to carry a constant-zero ival_flag, which is sound because this is the only arm that reaches here and it always passed 0.


## `IR_MATCH_DEFER ic-hit` — was line 266

the inline cache's fast exit lands here: rax=fn, rdx=dtp, identical to what the call leaves


## `IR_MATCH_DEFER probe-str` — was line 294

⭐ the string half of the merged probe: rt_defer_probe_run already ran it and left the new cursor in rdx, so there is no second call and no second name lookup


## `IR_MATCH_DEFER $V-scalar` — was line 316

PB-1s (s108): scalar half of the $V slot read -- open with the FROZEN value (dtp->snap[i]), not the per-site global; this is the pb_stale_snapshot_value silent-wrong-answer half


## `IR_MATCH_DEFER pseudo-record` — was line 367

s127 R-4(a) CURSOR-BEARING PSEUDO-RECORD: the C-path 16B record's pad now carries the instance's ENTRY cursor and the exhaust stub RESTORES it before af.  The old stub (add rsp,16 only) was built for a world where the af retry edge was suppressed for defer bodies -- it was only ever consumed by the as null-progress je, where r14d's value no longer mattered at the pop.  With the sn4_alt_carrier af->PAIR(1) edge admitted, af cascades `jne -> jmp [rsp]` per placed instance and each pop MUST rewind r14d to that instance's entry, or the Δ0 compare never terminates and the walk descends past every record into the statement spine -- measured 165_pat_arbno_defer_var_body stmt 2 (Q='aa' on 'aaa'): rip=0 on a zeroed pad with r14d stuck at 2.  Spelled push/pop-only (mov ecx,r14d zero-extends; rcx is dead post-call) so no [rsp+N] text spelling can pick up FR64 depth compensation (the s97 x86_rsp_load64 lesson).  The blob path needs nothing: a target blob's interior (ALT af) restores r14d from ITS OWN record by construction, and the record layout/size here is unchanged -- {stub@0, cursor-pad@8}, same 16B, same parity.


## `IR_MATCH_DEFER β unsealed-carve` — was line 396

s139 UNSEALED CARVE-DEFER beta: RESTORE THE FRAME, THEN RESUME THE RECORD

---

Extracted 2026-09-01 by seat04 (row `bb-fixup-az-cleanup`) at the R1 conversion of `bb_match_defer.cpp`.
Source of truth for the box's CURRENT behaviour is always the file itself; this is provenance, not spec.
