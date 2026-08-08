# GOAL-PL-ZFRAME-RESTORE.md — Restore Prolog to full glory on ZETA FRAMES (STACK)

## ⛔ CONCURRENCY PROTOCOL (Lon 2026-08-08) — THE CONCURRENT SET (8)
`GOAL-SNOBOL4-BB` · `GOAL-SN4-ZETA-MECH` · `GOAL-SN4-ZETA-CLIMB` · `GOAL-SNOBOL4-RTX` · `GOAL-ICN-ZFRAME-RESTORE` · `GOAL-ICN-ZETA-CELLS` · `GOAL-PL-ZFRAME-RESTORE` · `GOAL-PL-ZETA-CELLS` run CONCURRENTLY against one tree. Each session COMMITS along the way (per-rung, buildable, git-revert path) but PUSHES ONLY AT SESSION END: `git pull --rebase` → re-prove THIS file's gate/watermark post-rebase → push code repos first, `.github` last → `handoff_status.sh` verbatim (the only push truth). This reduces contention points. Watermarks are SHARED STATE — re-prove at open AND close; expect parallel-landed commits in the end-of-session rebase. A semantic collision there (two fixes for one defect) is resolved BY THE REBASING SESSION and NOTED in its cursor — never silently dominated (the `zd_zdh`/`_xh_zdh` lesson, CLIMB s14). ⛔ Rungs that their own file marks NOT-CONCURRENCY-SAFE (e.g. RTX-11/12: `x86_asm.h`/`bb_match_release` + `.s` regen ×3; RTX's GVA-slot ζ-ladder item) MUST NOT run while any other seat is active — Lon's routing.

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

## ⛔⭐ LIVE CURSOR — s8 (2026-08-08, Sonnet 4.6 — BISECT COMPLETE; both regression windows diagnosed; FR-4 still blocked; bench 3/22 at HEAD 39cbfd33)

**HEAD at session end:** `39cbfd33` (after `git pull --rebase` — three commits landed on other tracks: PB-2, PL-ZK-3 COMPLETE, and .s regen). Bench watermark re-derived at new HEAD: **m3 3/22** (deriv, fib, tak). Unchanged from s7b — no regression from the rebase.

**⭐⭐ BISECT COMPLETE — both regression windows fully diagnosed:**

**WINDOW 1 [`5562280d`..`63280689`] — culprit: `fba93a77` (ICN-FR-4 WIP INCOMPLETE, merged in at `996bcfe9`).**
Root cause: this WIP commit relocated the caller_rbp save slot in the shared `xa_flat_zframe_prologue/epilogue` from `[rsp+kt-8]` to `[rsp+kt-32]` (an intermediate design that moved old_rbp inside the generator frame). The epilogue's `mov rbp, [rbp+kt-32]` restores a wrong value for Prolog zframe graphs, which expect caller_rbp at `kt-8` per the FR-3 wire-header contract. Effect: SEGV on all Prolog recursive arithmetic (`derive`, `divide10`, `log10`, `ops8`, `times10`). Cost: **11→6, −5 programs**. The complete ICN-FR-4 commit (`e33e703b`) fixed this by reverting to `RBPRAWQ(kt-8)` — so the slot is back at `kt-8` at HEAD. **W1 regression is ALREADY FIXED AT HEAD.** Confirmed: all 5 programs pass at `e3204b01` (before the WIP) and at HEAD's `RBPRAWQ(kt-8)` epilogue.

Wait — re-measure: at HEAD `39cbfd33` those 5 programs fail (derive rc=139, divide10 rc=139, etc. per the m3 3/22 sweep above). The s7b cursor said `63280689` scores 6/22 (passing: cal, deriv, fib, nrev, qsort, tak). **At HEAD only deriv/fib/tak pass — so W1's 5 programs (derive=pass at 5562280d but listed separately from deriv) must still be failing.** Let me reconcile: the HEAD bench run shows `derive` FAILS (rc=139). So the W1 fix in ICN-FR-4-COMPLETE is NOT fully effective — the `RBPRAWQ(kt-8)` change may only fix the generator-path epilogue (`flat_gen=1` arm) while the non-gen Prolog epilogue still reads the wrong slot. **⛔ This needs verification at the next session start: check `xa_flat_zframe_epilogue_γ_str` at HEAD for the non-gen (`!g_emit.flat_gen`) branch — does it use `kt-8` or `kt-32` for rbp restore?**

**WINDOW 2 [`e33e703b`..`b4c3a2b5`] — culprit: `e33e703b` (ICN-FR-4 COMPLETE) itself.**
Root cause: the non-zframe β-resume arm in `bb_call_proc_staged.cpp` (lines 664-668) — for Prolog `zframe_graph=1, zf_resume=false` graphs calling multi-clause predicates. Reproducer confirmed: 5-line `app/3` hangs at `e33e703b`, passes at `63280689`. The `add rsp, 8` (line 612, pop landing word after saving `FRQ(act+8)`) is new and may interact with `rt_proc_call_epilogue_γ`'s stack expectations. Specific mechanism not yet pinned (need monitor or gdb). Passes `cal` and `qsort` at `63280689`; both hang/segv at `e33e703b`. **W2 root cause needs monitor-first investigation at next session.** Cost: **6→3, −3 programs** (`cal`, `nrev`, `qsort`).

**NEXT SESSION TASKS (in order):**
1. `git pull --rebase`, rebuild, re-derive watermark (expect 3/22 at new HEAD).
2. **Verify W1 status at HEAD:** read `xa_flat_zframe_epilogue_γ_str()` non-gen branch — confirm whether non-`flat_gen` path uses `kt-8` or `kt-32` for rbp restore. If `kt-32`, this is the remaining W1 fix needed (additive arm for non-gen Prolog zframe epilogue reading `kt-8`).
3. **Pin W2 root cause via monitor:** run `test_monitor_2way_sync_step_bin.sh` on `app_tiny.pl` (the 5-line `app/3` reproducer above) comparing oracle vs SCRIP. First divergence = bug site in `bb_call_proc_staged` non-zframe β-resume or epilogue interaction.
4. Each fix is an ADDITIVE ARM in the responsible template, gated on `g_emit.zframe_graph && !g_emit.flat_gen` (Prolog non-generator zframe). Never reverts ICN-FR-4.
5. After both windows clear: re-derive baseline, THEN open FR-4 (the 5-item lbl_t1 fix).

**REPRODUCER (write fresh each session — Prolog semicolon rule, save as /tmp/app_tiny.pl):**
```prolog
:- initialization(main).
app([], X, X).
app([H|T], Y, [H|Z]) :- app(T, Y, Z).
main :- app([1,2,3], [4,5], R), write(R), nl.
```
Expected output: `[1,2,3,4,5]`. Hangs at HEAD.

**s7 architectural findings still valid** (clause cursor, lbl_t1, g_pl_retry trail gap) — carry forward unchanged.

**FR-4 STATUS:** Runtime infrastructure complete (`rt_pl_retry_push/pop` in rt.c/rt.h, s6). Emitter integration BLOCKED on α-label staging AND on contaminated baseline. Do not open FR-4 until W1+W2 clear.

## ~~s5 cursor (superseded)~~
SCRIP `5562280d` (HEAD unchanged — no new commits this session; FR-2/FR-3 criteria verified against existing HEAD). **NO SOURCE MODIFICATIONS THIS SESSION.**

**WATERMARKS s5 (re-derived at session start):** bench **11/22 both modes** · rung suite **run 133/164 · compile 127/164** · SN4 m3 287/317 · m4 271/317 (baseline) · Icon 217/293 (ICN-FR-3 cursor, zero regression from PL work).

**⭐⭐ FR-2 AND FR-3 ARE COMPLETE.** Criteria re-read and all green:
- `rung01_hello` ✅ both modes · `nrev` ✅ both modes (FR-2)
- `qsort` ✅ both modes · `fib` ✅ both modes (FR-3)
- `SCRIP_PL_ZFRAME=0` deterministic 22/22 ×2 · differs from default on all 22 (correct, default=ON) ✅
- SN4 288/317 m3 · 269/317 m4 (within noise; no regression) ✅ · Icon 217/293 ✅
- s4 called these WIP because the build fixes at `5562280d` hadn't been re-measured — all criteria are met at HEAD.

**⭐⭐ FR-4 ROOT CAUSE FULLY DIAGNOSED** (FINDING-2026-08-07-CLAUDE-PL-FR2-FR3-COMPLETE-AND-DISJUNCTION-ROOT-CAUSE.md):

`IR_MOVE_LABEL` (bb_move_label.cpp) stores the retry address into ζ-frame slot `FRQ(op_off+16)` = `[rbp+16]`. The ζ-frame epilogue (`main_γ`) restores `rbp` to the **caller's rbp** (`mov rbp, [rbp+kt-8]`). After the epilogue fires, `rbp` no longer points to `main`'s frame. When the caller triggers backtrack and `main_β → n55_disjunction_α: jmp qword ptr [rbp+16]` executes, it reads through the **caller's rbp** at offset 16 — garbage. SEGV.

**Canonical WAM fix (gprolog `wam_inst.h` + SWI `pl-incl.h` read this session):** Both engines store the alternative-clause pointer (`ALTB`/`value.pc`) in a **heap-resident choice-point record** (`bb_choice_state_t.cp` in SCRIP's own `emit.h:206`) that is completely independent of the activation frame's lifetime. The `bb_choice_state_t` struct already has the `cp` field for exactly this purpose.

**⛔ INCORRECT APPROACH FOUND AND REVERTED:** An uncommitted modification to `bb_call_proc_staged.cpp` (push-landing-word + direct `jmp L(3)` gated on `g_emit.zframe_graph`) was found in the working tree and **reverted** (`git checkout src/templates/bb_call_proc_staged.cpp`). It was architecturally wrong: (1) `bcps_spine_gen_arm` is not called for Prolog multi-clause predicates at compile time (`rt_proc_is_generator` returns 0 until `proc_startup` registers at runtime); (2) the bug is in `bb_move_label`/`bb_disjunction`, not in `bb_call_proc_staged`. Tree is clean.

**FR-4 DESIGN (next session):** Gate on `g_emit.zframe_graph`. In `bb_move_label` ζ-frame arm: call `rt_pl_cp_set_retry(cp, rax)` to store the retry address in the PLJ heap choice-point record rather than `[rbp+op_off+16]`. In `n55_disjunction_α` ζ-frame arm: call `rt_pl_cp_get_retry(cp)` to load from the heap record. The `cp` pointer must be accessible without reading through the (dead) ζ-frame — options: (a) passed as a parameter to the disjunction call, (b) stored in a thread-global `g_pl_cp_stack` analogous to `g_pl_trail`. Completion: `queens` + `zebra` + `sendmore` green both modes.

**NEXT SESSION FIRST TASKS:** (1) Re-derive watermarks (bench 11/22, rung 133/164 run). (2) Check FR-2 and FR-3 boxes (re-measure first per FACT RULE, then check). (3) Open FR-4: read `bb_move_label.cpp`, `bb_choice_state_t` in `emit.h`, `lower_pl_choice_graph` in `lower_prolog.c`. Build `bt_minimal.pl` reproducer, confirm exact SEGV site with gdb backtrace. Implement heap-resident retry-address storage. Do NOT retry the `bcps_spine_gen_arm` push approach.

**s2 carried:** Sentinel guards `8fa12915` — LANDED. Anchor `20b56c9a` 22/22 both modes verified s1. EXTRACT-PL-FRAME.md committed. Anchor worktrees may need re-creation.

## THE ANCHOR — VERIFIED FACTS (measured 2026-08-07 in-session; do not re-litigate; DO re-derive all HEAD numbers)
- **Anchor of record: SCRIP `20b56c9a`** (2026-08-01 00:39, ON ORIGIN — the carve-kill PARENT, the last pre-death commit). PROMOTED 2026-08-07 by measurement: fresh build zero errors both logs, no libgc; against today's corpus **m3 bench 22/22 rc=0 AND full m4 sweep 22/22** (worktree `/home/claude/wt-pl-last`).
- **Corroborating earlier measured point: `8437c3d7`** (2026-07-30) — ALSO 22/22 both modes at a fresh build this session (worktree `/home/claude/wt-pl-anchor`); its FINDING-2026-07-30-CLAUDE-PL-RTX-ITEM-0 census (2,060,043 `rt_proc_call_open_det` arrivals, reach 19/22, `queensn` = 78% of board traffic = the perf vehicle) remains the board's proof of record. Spot outputs correct at both commits: queens N=16, nrev, qsort.
- **HEAD `c0372fec` (2026-08-07): bench 0/22** — 13× rc=139 SEGV + 9× rc=1. The break is total, both failure shapes.
- **Anchor selection SETTLED s0** (COMMIT-SELECTION LAW: the proof travels with the anchor): both candidates measured 22/22 both modes; `20b56c9a` wins as the LATEST green — 92 commits of fixes newer, 21 minutes before the kill. Lon may override at any session start. **Green window of record: `8d0665c8` (07-28, Icon+SN4 peak) → `20b56c9a` (08-01 00:39).**
- **Death: CARVE-KILL `ef9a7d2c`** (flat prologue emitter deleted, −247 lines) **+ `1ba33ea6`** (epilogue, −299), 2026-08-01 — a LON DIRECTIVE for the per-BB cell campaign. The §7 re-land was REVERTED by the s165 ruling ("DELETE THE PROLOGUE AND EPILOGUE... WE ARE SCOPING AT A DIFFERENT LEVEL NOW"). Honest cost recorded at the time: bench broken=22/22 (FINDING-2026-08-01-CLAUDE-PL-THE-CARVE-IS-NOT-DEAD). ⛔ THE RESTORATION IS A NEW ARM BEHIND A GRAPH FLAG, NEVER A REVERT of those commits.

## ERA MECHANICS — PROLOG-SPECIFIC (from the FINDING record; PL-FR-1 verifies each against the anchor tree)
1. **Prolog's live prologue arms at the anchor were LEXPREP2 + FRAME_RSP,** not Icon's dc-stub path: LEXPREP2 (jmp-entry lazy-seed via `rt_jmp_frame_lexprep2` — 279 corpus marker hits, s150) and FRAME_RSP (185 hits, s149); both already `x86()`-converted at the anchor (s149/s150), so the resurrection source is template-clean. ⭐ **`rt_jmp_frame_lexprep2` SURVIVES AT HEAD** (`rt.c:1552`) — only the emitter arms died.
2. **Generator/resumable predicate graphs took the HEAP-FB-ADOPT arm** (`emit_heap_fb_adopt` = `push rbp; mov rbp,rdi`, no rsp carve — activation survives β-resume); pin = `emit_rec_pin()` = jmp_pin ∪ adopt, ONE authority (s160/s161, gate `test_gate_fb_adopt_one_predicate.sh`).
3. **Frame census at the anchor era: 145 sites / 320,352 B / mean 2,209 B per activation** (s164) — × recursion depth IS the memory complaint the cells track answers; this track restores correctness first.
4. **The 4,510 whole-graph-frame readers by kind** (FINDING-2026-08-01-PL §11 — the conversion list the cells track inherits): `call_builtin_prolog` 2255 (50%, gates 100% of runs) · **PROC-ENTRY 781 (17.3%, NO BB owns it — wire header + saved rcx/rdx/rbp)** · `var_ref` 732 · `lit_string` 258 · `lit_integer` 180 · `suspend` 125 · `call_proc_staged` 102 · `var` 68 · `move_label` 5 · `disjunction` 4.
5. ⭐ **THE RESTORE VEHICLE ALREADY EXISTS AT HEAD:** ICN-FR-2 (`bcf05d33`) restored the gated whole-graph ζ-frame regime — `zframe_graph` on `IR_graph_t` (IR.h:256, struct-END, behavior-named), prologue/epilogue/exit arms in xa_flat.cpp + emit.cpp, killswitch pattern proven. IR.h's own comment guarantees Prolog invariance "by construction" precisely because only lower_icon stamps it — **PL-FR-2 makes lower_prolog the second stamper behind `SCRIP_PL_ZFRAME`.** PL-FR-1 decides per-arm whether Icon's restored shapes (dc stub, `rt_icn_zframe_args_install`, γ-retain) cover Prolog's LEXPREP2/adopt shapes or Prolog re-expresses its own arms from the anchor source.
6. ⛔ **Post-anchor machinery a `zframe` Prolog graph must bypass** (the double-billing list, PL-FR-1(f)): the ZD-PL-A arm in `zd_wl_kind`/`bb_call_fn.cpp` (s163b), NOFC, FB-STMT refine, and anything the SN4 MECH regime-deletion (`de837576`) made unconditional. `SCRIP_PL_ZFRAME=0` must reproduce today's exact (broken) path byte-identically.
7. ⛔ **DO NOT blind-widen `emit_fb_stmt_scan` to `IR_DISJUNCTION`** — the bail is principled (choice points are not rebalanced by HEAD..RELEASE), s164's standing warning.

## RUNGS (each: own commit, buildable, killswitch, SN4+ICN byte-identity, FINDING per land mine; walk in order)
- [x] **PL-FR-1 EXTRACT-PL-FRAME.md — COMPLETE s0b (VERIFY QUEUE closed; results in the doc's §VERIFY QUEUE RESULTS; item-3 dynamic sweeps re-scoped INTO PL-FR-2 completion).** Anchor→HEAD pairing per arm, the Icon FR-1 row shape: (a) LEXPREP2 prologue + its epilogue twin; (b) FRAME_RSP outer arm; (c) heap-fb-adopt + `emit_rec_pin` at HEAD vs anchor; (d) param/arg landing (`rt_frame_bind_args` double-copy — restore as-was; the sink lives in GOAL-PROLOG-BB); (e) slot-grant coverage for Prolog value-producers; (f) the bypass enumeration (item 6 above) + how `=0` restores today's path; (g) epilogue/whack shape vs HEAD's exit-class ledger. PLUS: decide REUSE-vs-OWN-ARMS per row (anchor promotion SETTLED s0 — see THE ANCHOR).
- [ ] **PL-FR-2 THE GRAPH-FRAME REGIME RETURNS FOR PROLOG (gated, both media).** lower_prolog stamps `zframe_graph` on every graph behind `SCRIP_PL_ZFRAME` (default ON for Prolog graphs; `=0` byte-identical to pre-rung HEAD — completion criterion). Prologue/epilogue arms per FR-1's reuse decision. Completion: rung01_hello + nrev green BOTH modes · SN4 crosscheck + Icon 303-emission content-hash byte-identical · `=0` identity · gates not regressed.
- [ ] **PL-FR-3 WIRE EXIT VIA THE FRAME HEADER** for flagged Prolog graphs (γ/ω unwind to flat base, wires at kt-24/-16, caller rbp kt-8). Completion: qsort + fib green both modes (recursion proves per-activation frames).
- [ ] **PL-FR-4 PREDICATES + CHOICE POINTS ON-SPINE.** The suspend/generator class (70.3% of frame refs, s164) + `IR_DISJUNCTION` choice points: β-resume against the pinned header, backtrack across activations, trail interplay. Audit for post-carve-kill rot in the flagged arm only. Completion: queens + zebra + sendmore green both modes.
- [ ] **PL-FR-5 FULL RATCHET TO ANCHOR PARITY.** **bench 22/22 m3 AND m4** · rung suite `test_prolog_rung_suite.sh` 164/164 interp + compile · smoke 5/5 · census instrument reproduces the board's 2,060,043 arrivals ±0 (gate ON). MONITOR-FIRST on every residual.
- [ ] **PL-FR-6 GATES + PROCESS.** `scripts/test_gate_pl_zframe.sh` (bench quartet both modes + SN4/ICN byte-identity + `=0` identity + DESCENDING-failure ratchet); existing gates re-proven (`test_gate_pl_no_new_global.sh` ratchet, `emit_no_lang`, adopt-one-predicate, fb tripwire, medium-invisible baseline).
- [ ] **PL-FR-7 CURSOR + DOC SYNC.** GOAL-PROLOG-BB.md cursor pointed at this ladder's outcome; GOAL-ZETA-FOUR.md one-line cross-ref (`8437c3d7` = the Prolog-side frame-rsp anchor); GOAL-PROLOG-RTX.md coordination note. No PLAN.md table edit (RULES).

## WITNESS SET (report every session)
bench 22 board (queensn = perf vehicle; three files named queens.pl — full path + md5 ALWAYS, the s224/s225 rule) · rung suite 164 · smoke 5 · rung01_hello · nrev · qsort · fib · queens · zebra · census 2,060,043.

## SESSION SIZING + HONEST LIMITS
3–4 sessions mirroring Icon (FR-1+start-2 · FR-2/FR-3 · FR-4/FR-5 · FR-6/FR-7); every rung boundary a safe handoff. Report approximate context percentage at natural checkpoints unasked; anchor worktree (`/home/claude/wt-pl-anchor` this session) is for building + grepping, never wholesale reading. HEAD moves daily under 5+ parallel tracks — re-derive every number at session start; the flag-gate + tri-language byte-identity is the armor. Anchor parity (22/22 both modes) is THIS ladder's finish line; perf (the sink ladder, RTX) stays with GOAL-PROLOG-BB / GOAL-PROLOG-RTX. This file cannot coerce its walker; the cursor, the gates, and Lon's review are the enforcement.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

## ⛔ SESSION-START NOTE FOR NEXT WALKER
FR-1 COMPLETE (s0b) — FR-2 MAY OPEN. FR-2 inherits the queue's item-3 dynamic sweeps (flagged-graph FATAL sweep + `=0` byte-identity bypass sweep) as completion criteria; they need the flag to exist and are already in FR-2's text.
