# FINDING — W-0 CENSUS: THE CURSOR'S 93/25 WERE RIGHT AND MY OWN GREP WAS WRONG; bb_call_fn.cpp + bb_var.cpp ARE 100% GENUINE SCRATCH, xa_flat.cpp SPLITS INTO TWO UNRELATED CLUSTERS

**Seat:** WIRES (`GOAL-SN4-HOME-WIRES.md`) — W-0 finish, first item of "NEXT SEAT, IN ORDER" from the s33 cursor.
**Session:** 2026-08-12, Sonnet 5. **Trees:** SCRIP `51934a9f` · corpus `14dc06bd` · `.github` `4a292e25`. **ZERO compiler bytes.**

---

## 1. SELF-CORRECTION FIRST — MY OWN CENSUS WAS THE BROKEN INSTRUMENT, NOT THE CURSOR

Before trusting the s33 cursor's "`bb_call_fn.cpp` (93 occ) + `xa_flat.cpp` (25) + `bb_var.cpp:19`" tally, I ran my own `grep -c`/`grep -o` pass and got 81 lines/101 occ and 39 lines/50 occ respectively — neither matching. I did **not** overwrite the cursor's numbers with mine. Running the actual instrument (`scripts/test_gate_wreg_claim.sh`, informational mode) reproduced the cursor's figures exactly: `bb_call_fn.cpp` = 78 lines/**93 occ**, `xa_flat.cpp` = 23 lines/**25 occ**, `bb_var.cpp` = 1 line/**4 occ** (so "`bb_var.cpp:19`" is a *line number*, not a count — the notation is inconsistent with the other two entries in the same cursor sentence and is worth fixing next edit).

Root cause of my own miscount, both documented in the gate script's own header as prior lessons (WREG-0 finding, s13/s14 corrections) that I re-derived independently before finding they were already on record:
- I didn't strip comments; the gate does. `xa_flat.cpp` carries a long historical-bug-narrative comment (lines 217–236, the ICN-FR-3 postmortem) that mentions "r10"/"r11" in prose repeatedly — inflates a naive grep by ~24 occurrences on that file alone.
- I restricted to quoted `"r10"`/`"r11"` tokens; the majority of real occurrences are register names used as the base of a bracketed memory operand — `"[r10 + 32]"`, `"dword ptr [r10 + 32]"` — which don't match a bare `"r10"` quote pattern at all. `bb_call_fn.cpp` alone has 75 such lines invisible to a quote-restricted search.

**Lesson for whoever reads this next:** don't grep by hand when `test_gate_wreg_claim.sh` exists — it already strips comments, matches every sub-register spelling (`r10d`/`r11b`/etc., per the `AB_TC_REG` blind-spot it documents), and reports both LINE and OCCURRENCE counts. I found this out the hard way after re-deriving a problem the codebase had already solved.

## 2. bb_var.cpp — CONFIRMED, 1 SITE, GENUINE SCRATCH

Line 19, one conditional, four tokens (`mov r10,ZRES(0)` / `mov FRQ(op_off),r10` / `mov r11,ZRES(8)` / `mov FRQ(op_off+8),r11`), gated on `_.op_off >= 0 && g_emit_cfg && g_emit_cfg->pl_cells_graph`. Comment names it "PL-ZK-5B DUAL-WRITE (Bug 4 Option C)": copies a match result from `ZRES` into an rbp-relative frame slot so a β-continuation node not on the gamma-chain can still read it. r10/r11 hold nothing before this snippet and nothing after — pure scratch, zero relationship to wire duty.

## 3. bb_call_fn.cpp — 93/93 OCCURRENCES READ BY HAND, 100% GENUINE SCRATCH, ZERO PRESERVERS

Every occurrence (quoted + bracketed-operand forms, all 93, all cross-checked against real source line numbers — not the comment-stripped stream, which shifts line numbers when a multi-line `/* */` block is deleted and should never be used with `grep -n`) falls into exactly two buckets:

- **Prolog global-pointer scratch** (the majority): `lea r10,[rip+__]` off one of `g_pl_trail`, `g_hp_fr`, `g_plw_dot_sl`, `g_plw_cellws_on`, `g_zeta_mode`, `g_pl_zf_pending_cursor`, then load/store/test/add through r10 and r11 entirely within one helper function. Trail-stack push tests, heap-frontier bump-checks, and small flag reads. Never crosses a call boundary; nothing here is preserved for later.
- **The same PL-ZK-5B dual-write idiom as `bb_var.cpp`**, duplicated verbatim (modulo comment wording) at lines 509 and 549.

No push/pop-around-a-call pattern anywhere in this file for either register — this distinguishes it cleanly from the `bb_scan_*` preservers (§5).

**Two live confirmations of the cursor's predicted "Encoder landmine"** (`[r10]` parses as `XK_R10MIR` → `x86_store_cursor_mirror()`, a store-only mirror with no load arm): line 90's comment notes the trail-check "*Requires r10 = &g_pl_trail*" as a precondition rather than an inline read, and line 372 spells the reasoning out directly — *"r11 parses XK_MEMIND (x86_load_mem64 dispatch); r10 would parse XK_R10MIR (store-cursor-only, no load arm)"* — i.e. the author already hit this landmine once and chose r11 over r10 specifically to route around it. Anyone touching `[r10]`-shaped operands in W-3/W-5 should grep for `XK_R10MIR` before assuming a clean slate; this file already has two hand-verified workarounds baked in.

## 4. xa_flat.cpp — NOT UNIFORM. TWO UNRELATED CLUSTERS UNDER THE SAME OCCURRENCE COUNT

- **Lines 474–479** (small): identical Prolog-scratch pattern to §3 — `g_pl_zf_pending_cursor`, lea+load+test+store, self-contained. Consistent with the rest of the genuine-scratch classification.
- **Lines 238–307** (the bulk): the "ICN-FR-3 zframe dc stub" and "PL-DC direct-call entry" — a return-address/argument-marshaling shim wrapping calls into `rt_arg_stage`. r10 holds a transient cell-pointer reloaded from `[rsp+i*8]` each loop iteration (specifically *not* held across the call in a register, because the very comment block explains an earlier version tried that and SIGSEGV'd when `rt_arg_stage`'s SysV clobber set ate it — this is a **third**, file-level confirmation that carelessness with these two registers across a call is a proven, not theoretical, crash class here). r11 holds the real return address, doubled onto the stack for 16-byte alignment, later popped twice and jumped through. **This is shape-similar to a preserver (push, later pop-and-use) but is not one** — it protects a plain C-ABI return address, not pattern-match continuation state, and it is the pre-existing PROC-shim mechanism itself (the exact thing the seat's charter quotes Lon asking to delete: *"remove the stupid PROC shim... use proper PASS-THRU glue using R10 and R11"*), not stray misuse of the wire registers.

**I am not touching this cluster.** It carries two already-fixed, hand-documented production SIGSEGVs in its own comments (the iteration-1-reads-garbage-rdx bug, and the rsp≡8-at-proc-entry alignment bug), which is exactly the kind of code the RULES.md MONITOR-FIRST discipline exists to protect from confident-looking guesses. Reassigning its registers is real work with a design question attached (what carries the retaddr instead, and does this stub ever run while a wire is live) — that's W-5 territory (blocked: `frame_need_of` predicate still empty) or a question for Lon, not a mechanical sweep.

## 5. bb_scan_match.cpp — SPOT-CHECKED, PRESERVER CLAIM HOLDS

Read in full (75 lines, 8 occurrences, all r10, zero r11). Every occurrence is `push r10` immediately before a `call` to `rt_scan_needle`/`memcmp`, `pop r10` immediately after — the doubled push/pop around the `rt_scan_needle` call is 16-byte stack-alignment padding, not double protection. This is exactly what "the cure, not the disease" means: it protects whatever value r10 already holds across an external call that would otherwise clobber it. I did not exhaustively re-verify the other nine `bb_scan_*` files or `bb_idx_get/set`/`bb_initial`/`bb_rk_*`/`bb_glue_flat`/`bb_call_proc_staged`/`xa_bb_macro_library`/`bb_lit_scalar.cpp` (31 remaining occurrences across those); this is one confirmed member of the class per the seat's own INSTRUMENT RULE, not a completed sweep of it.

## 6. SCOPE THE CURSOR'S SUMMARY DIDN'T SURFACE

- `x86_asm.h` sits at 25 occurrences in the unwhitelisted sweep surface. Expected — the gate's own comment says the whitelist stays empty until W-3 creates the glue emitters — but worth naming since the seat charter lists "x86_asm.h encoder internals" as one of the four site classes meant to own the wires eventually.
- **RTX hand-written asm is tracked separately by the same gate and is large: 223 occurrences across 10 `.S` files, `rtx_match.S` alone at 89.** The gate's own comment: *"rtx_match.S is the sharpest edge: it executes DURING a match, i.e. while the wires are live."* This is outside the original 178-site design census (added per a cross-goal bulletin) and I have not looked at any of it yet — it's real remaining scope for W-0, arguably the highest-risk part of it, and I'd flag it as the next thing to open rather than the remaining `bb_scan_*` files, which are now fairly well-trusted as a class.

## NEXT

1. Fix the `bb_var.cpp:19` notation in the WIRES cursor (line number, not a count of 19 — as written it misreads next to the other two entries).
2. Open `rtx_match.S` — highest-risk unreviewed surface, live during a match.
3. If a register-reassignment plan is wanted for the confirmed genuine-scratch sites (bb_call_fn.cpp's Prolog bookkeeping, bb_var.cpp), that's a design question (which register replaces r10/r11 for Prolog-internal scratch — r8/rcx/rdx look free at those specific sites on a quick read, not verified) worth a design note or a direct call from Lon before editing, given RTCC already claims r9 and RULES.md's O2-DIRECTED-ONLY-style caution about not touching shared surfaces without a plan.
4. `xa_flat.cpp`'s dc-stub cluster (238–307) stays untouched pending W-5 (blocked on `frame_need_of`) or explicit direction — it is the shim W-5 exists to delete, not a scratch bug.
