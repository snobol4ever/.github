# GOAL-PL-ZFRAME-RESTORE.md — Restore Prolog to full glory on ZETA FRAMES (STACK)

## ✅ CONCURRENT WORK — COMMIT AND PUSH FREELY (Lon 2026-08-10 — SUPERSEDES the 2026-08-08 CONCURRENCY PROTOCOL, which is DELETED)
**Any session may edit ANY file at ANY time, and push whenever it has something worth saving.** There is no routed window, no reserved file, no "not-concurrency-safe" rung, no concurrent set, and no waiting on another seat. Git merges; `git pull --rebase` before pushing and resolve conflicts normally. ⛔ **NEVER hold back a commit or a push on concurrency grounds, and never park work waiting for a window** — stranding has cost this project vastly more than merging ever has (s9/s10 lost two sessions of RTCC work; s19–s26 stranded eight sessions of MECH work and BUG-7 was re-derived from scratch). **Push early and often — mid-session, per rung — not only at session end.**
Three things survive because they are about CORRECTNESS, not scheduling: (1) after a `git pull --rebase`, re-prove THIS file's gate/watermark — shared state can move under you; (2) push code repos before `.github`, so a FINDING never describes a tree that was not pushed; (3) `handoff_status.sh` verbatim is the only push truth. **Semantic collisions — two seats claiming one register, the r9/GVA class — are caught MECHANICALLY by `scripts/test_gate_rtcc_claimed_regs.sh`, not by scheduling. That gate is the replacement for the window, and it is why the window is no longer needed.**

**CHARTER (Lon directive, 2026-08-07):** Restore Prolog to where it was — `benchmarks/prolog/bench/` 22/22 both modes — using ZETA FRAMES on the STACK, as code that fits the FOUR-ZETA-MODE system (GOAL-ZETA-FOUR.md): **a NEW GATED ARM, never a revert** of the carve-kill commits. Mirror of `GOAL-ICN-ZFRAME-RESTORE.md` (read it first every session — its rungs, armor, and rulings are the template; only Prolog-specific facts live here). SNOBOL4 AND Icon byte-identity is a gate on every commit.

## ⛔ CONCURRENT TWIN TRACK (Lon directive, 2026-08-07, same day)
**`GOAL-PL-ZETA-CELLS.md` walks the OTHER embodiment SIMULTANEOUSLY: 100% per-BB ζ CELLS on the RSP FORTH spine.** Lon: same two-track shape as Icon — FRAMES on STACK and CELLS on STACK developed simultaneously, BOTH KEPT, switch-selected until Lon picks a default. Rules of engagement mirrored from the Icon pair: one graph NEVER in both arms (the cells track's opt-IN suppresses the zframe stamp at the SAME LOWER site this file's R-PL-A defines); shared choke sites (`zd_*` one-authority lines, staging choke, xa_flat arms) take ADDITIVE arms only; `=0`/unset identity is a completion criterion on every behavioral edit; `git pull --rebase` before every commit — FIVE-plus concurrent tracks now share this emitter (SN4 MECH/CLIMB, ICN ZFRAME/CELLS, PL ZFRAME/CELLS).

## ⛔ CROSS-TRACK NOTICE (ICN s5, 2026-08-07) — the zframe vslot override is DELETED; PL gained +85/+79
`ir_drive_slot_assign`'s `zframe_graph` param/local vslot override is a **SHARED choke site**: PL-FR-2 stamps `zframe_graph` at `lower_prolog.c:1385`, so that block was live for Prolog too. It has been **DELETED** at SCRIP `1567f28a` by the ICN-ZFRAME session. Prolog was **measured before the cut, not after**, per the rules of engagement:
- **Prolog rung suite: interp 47/117 -> 132/32 · compile 47/117 -> 126/38.** Strict gain, no renegotiation needed.
- Icon 206/57/30 -> 217/46/30 (11 fixed, 0 broken). SN4 byte-identical 318/318.
**WHY it was wrong:** ZLS vslot offsets are FLAT-FRAME offsets in the graph root scope, correct under a pinned rbp by construction — the "FORTH-spine offsets" premise was false. The override re-granted locals at `(np+j+1)*16` = `base+j*16`, which IS node result cell k=j, aliasing every local onto a result cell. ZLS already grants params, named locals, AND implicit locals (its own IR_ASSIGN/IR_VAR/IR_VAR_REF scan, `zeta_storage.c` ~:536, with a dedup guard).
**If PL needs zframe-specific vslot behaviour later, add it as PL's OWN arm keyed behaviourally — do not restore this one.** Full rationale is the separator comment at the deletion site and the `1567f28a` commit message.

⛔ **s3 NOTE:** This session's `lnames` registration (commit `6a87662b`) adds body vars to `lnames` so ZLS grants them slots at its own flat-frame offsets (without the now-deleted override). The deletion is compatible with the lnames approach; verify Prolog body-var vslot correctness at next session start.

## ⛔⭐ LIVE CURSOR — s13 (2026-08-09, Sonnet — FR-4: N0-SUPPRESS `a92d269d` + W1 m4 twins `4c94eaad`; bench 11/22 BOTH MODES (+5); nested 2-gen backtrack proven; NEXT = disjunction `;` path)

**s13 HEAD at session end: `4c94eaad`** (two commits: `a92d269d` N0-SUPPRESS + `4c94eaad` W1 m4 twins). Bench watermark: **m3 11/22 · m4 11/22 · combined 11/22** (up from 6/22). SN4 roman.sno + Icon generators.icn byte-identical; zero new symbols in their .s.

**W1 m4 twins (`4c94eaad`):** The compiled -no-pie binary never got m3's two pre-entry fixes. (1) W1-Bug1: core bt confirmed `rt_plj_alloc → rt_gcheap_init → gc_static_segs_init → dl_iterate_phdr` with rsp≡8 — the lazy gc init firing from a misaligned JIT frame, NOT plc_dead_cstack as s9's Bug-2 framing suggested for m4. Fix: emitted `call rt_gcheap_warmup@PLT` in the m4 zframe main wrapper. (2) W1-Bug2: `g_plw_floor_bypass` must be set by PLT call INTO the .so — new `rt_plw_floor_bypass_on()` in by_name_dispatch.c; a direct `[rip+sym]` store from the exe copy-relocates a dead duplicate into the exe's .bss while dop_call (same TU as the definition) binds locally to the .so's still-zero copy. **RULE: the emitted binary controls .so-resident runtime state only through PLT calls, never direct data stores.** Both calls gated `is_prolog && zframe_graph && !icn_cells_graph`, placed before `xor esi` (rsi caller-saved), after the r12 seed (callee-saved); no clears (emitted main exits via zf wires).

**⭐ NESTED BACKTRACK PROVEN:** `color(red). color(green). color(blue). main :- color(X), color(Y), write(X-Y), nl, fail.` prints all NINE pairs red-red…blue-blue in correct order, rc=0 (m3). Two concurrent activations of the same zframe generator interleave correctly on the LIFO triple stack — N0-SUPPRESS + push3/pop3 generalize past the single-clause-chain case. The queens-class blocker is therefore NOT the generator resume protocol.

**N0-SUPPRESS fix:** `sink_trail_mark_str` in `bb_call_fn.cpp` gained a `resoff` parameter and a zframe-only guard block: read `g_pl_zf_pending_cursor`; if set (β-resume re-entry), load `rax:rdx` from `FRQ(resoff)` (lexprep2's already-correct trail mark) and jmp to label-101, skipping `pl_trail_mark()`. Byte-identical for SN4/Icon (`zframe_graph=0` → guard absent). Two call sites updated: legacy arm (line 593, passes `resoff`) and ZD arm (line 488, passes `_.op_off`). Root cause confirmed from gprolog `CREATE_CHOICE_COMMON_PART` / `UPDATE_DELETE_COMMON_PART` (`wam_inst.c:1407–1436`): canonical WAM writes `TRB(cur_B)=TR` once at choice-point creation; retry never re-samples it.

**WITNESS:** `bt_debug.pl` (`p(1). p(2). p(3). main :- p(X),write(X),nl,fail.`) — BEFORE: prints `1` only (clause-2 unification failed, X stayed bound). AFTER: prints `1`, `2`, `3`, rc=1 ✓.

**m3 recovery detail:** The 5 W1 programs (`derive`, `divide10`, `log10`, `ops8`, `times10`) now pass m3 — all arithmetic-recursive, fail mode-4 due to W1-Bug2 (`plc_dead_cstack → sscanf` rsp-misalignment in JIT, pre-existing since s9). `g_plw_floor_bypass` mechanism is in place (by_name_dispatch.c:1463); the mode-4 fix needs that bypass to be wired at the correct scrip.c call site for zframe Prolog graphs.

**⛔ REMAINING OPEN — the disjunction path:** `queens`, `ham`, `mu`, `zebra`, `sendmore`, `crypt`, etc. (11 programs) still fail both modes. Nested generator backtracking is proven green (above), so the frontier is the s12-diagnosed "separate (outer) issue": `; ` disjunction via `bb_move_label`/`bb_indirect_goto` (retry address in `g_pl_retry` per FINDING-PL-FR4-RETRY-STACK.md — emitter integration never landed), plus whatever cut/arith-guard classes the failures decompose into.

**NEXT SESSION TASKS (in order):**
1. `git pull --rebase`; rebuild; re-derive watermark (expect 11/22 both modes; HEAD `4c94eaad`).
2. Decompose the 11 failures by feature: run each, bucket by first divergence (disjunction / cut / assert / arity). `bt_minimal.pl` (`main :- color(X), write(X), nl, fail ; true.`) is the disjunction reproducer from FINDING-PL-FR4-RETRY-STACK.md.
3. Land the FINDING's one-line change set (α-label retry via `lbl_t1`, `rt_pl_retry_push/pop` emitter arms in `bb_move_label`/`bb_indirect_goto`) — re-read its "Correct fix" section first; the runtime half already exists in rt.c.
4. SN4+ICN byte-identity before every behavioral commit. Target 15+/22 both modes.



## ⛔⭐ LIVE CURSOR — s14 (2026-08-09, Sonnet 4.6 — ROOT CAUSE FOUND; FIX COMMITTED; NEXT = RE-DERIVE WATERMARK)

**s14 HEAD at session end: `2f620d2d`** (SCRIP). Two files changed: `src/runtime/rt/rt.c` + `src/templates/bb_suspend.cpp`.

**ROOT CAUSE OF ALL 11 REMAINING FAILURES FOUND AND FIXED:**

The 11 bench failures (nreverse, queens, sendmore, crypt, zebra, ham, mu, meta_qsort, query, queens_8, queensn) were NOT a disjunction problem. They were caused by **pending-cursor contamination** in the β-resume re-entry path — a bug in the triple-stack mechanism introduced in s13.

**The bug:** When predicate P β-resumes, `rt_pl_zf_resume_set` sets `g_pl_zf_pending_cursor`. This global stayed set through the entire re-entry α execution. When P's clause-1 body called an **inner predicate Q** (e.g. nreverse calls concatenate), Q's own `bb_suspend` node fired. Q's clause-cursor gate (`op_sb == g_emit_cfg->resume_slot`) passed — every predicate's gate passes for its own suspend node — and Q **wrongly intercepted the pending resume for P**. This created a triple-stack imbalance growing O(recursion depth), tripping glibc's stack canary at depths ≥ 15 in a **non-monotone pattern** (n=15 crashes, n=20 passes, n=25 passes, n=28 crashes) depending on the specific call count at each depth.

**The fix (per-frame sentinel at `[fb+0]`):** `rt_jmp_frame_lexprep2` now writes sentinel `1` to `[fb+0]` (the yield-value lo word, normally 0 until suspend fires). α_body NEVER writes `[rbp+0]` — only the yield path does. `bb_suspend` checks `[rbp+0] == 1` (β-resume re-entry) vs 0 (fresh call or INNER predicate), instead of the global `g_pl_zf_pending_cursor`. Per-frame: correct for any recursion depth. No global contamination of inner predicates.

**CONFIRMED BEFORE FIX:** Canary crash at n=15, n=18, n=28, n=30; pass at n=20, n=25 (non-monotone = hallmark of stack-imbalance, not depth overflow).
**SN4/Icon byte-identity:** `zframe_graph=0` for their graphs → bb_suspend intercept block absent → byte-identical by construction (structural argument, not measured this session — R-ICN-D re-proof deferred to next session).

**STALE FINDING:** `FINDING-PL-FR4-RETRY-STACK.md` is a historical artifact. Do NOT follow its "one-line change set." The disjunction (`;`) case was already fixed by s13's N0-SUPPRESS work. The 11 failures were the triple-stack contamination bug, now fixed.

**NEXT SESSION TASKS (in order):**
1. `git pull --rebase`; rebuild (`make -j$(nproc)`); re-derive watermark BOTH modes (expect substantial improvement: 16–22/22 range, pending arithmetic/cut failures).
2. Re-prove R-ICN-D: `roman.sno` byte-identity with/without `SCRIP_ICN_ZFRAME=1` and `generators.icn` — zero new `.s` symbols for SN4/Icon.
3. Run `bt_debug.pl` (1,2,3/rc=1) and `bt_minimal.pl` (red/green/blue/rc=0) as witnesses.
4. If arithmetic programs (derive, divide10, log10, ops8, times10) still fail m4 after fix — that is the pre-existing W1-Bug2 (`g_plw_floor_bypass` not wired for m4 zframe); separate from this fix.
5. Update this cursor with measured watermark. Push `.github` last.

**ALSO NOTE:** `g_pl_zf_target_pcall_top` global is defined and set in this commit but not yet read in `bb_suspend` (it was a parallel approach explored and superseded by the sentinel). Safe to leave; dead code until a future session uses it or removes it.
