# GOAL-ICN-ZFRAME-RESTORE.md — Restore Icon to full glory on ZETA FRAMES (STACK); co-expressions stay PTHREAD

**CHARTER (Lon directive, 2026-08-07):** "Write up RUNGS and STEPS to accomplish restoring Icon to its full glory and using ZETA FRAMES on the STACK, and CO-EXPRESSION will remain a PTHREAD." Restore the anchor era's whole-graph ζ-frame regime for Icon graphs as code that fits the FOUR-ZETA-MODE system (GOAL-ZETA-FOUR.md) — a NEW GATED ARM, never a revert. SNOBOL4's per-BB cell regime is untouched and its invariance is a gate on every commit.

## ⛔ CONCURRENT TWIN TRACK (Lon directive, 2026-08-07, added same day as carve)
**`GOAL-ICN-ZETA-CELLS.md` walks the OTHER embodiment SIMULTANEOUSLY: 100% per-BB ζ CELLS on the RSP FORTH spine (the SN4 ZD machinery completed for Icon — LVA locals as cells, GVA globals off-stack, suspension via pthread-stacks-or-pending-cells decided by measurement).** Lon: "We would have FRAMES on STACK and CELLS on STACK being developed simultaneously." BOTH KEPT, switch-selected (the ARCH-ICON two-backends precedent) until Lon picks a default. Rules of engagement, mirrored in both files: one graph is NEVER in both arms — the cells track's `SCRIP_ICN_CELLS=1` opt-IN suppresses `zframe_graph` at the SAME LOWER site R-ICN-A defines (its draft R-ZK-A; either side may renegotiate the selector shape WITH the other's file updated in the same commit); shared choke sites (`zd_*` one-authority lines, BLOB-GRANT block, staging choke) take ADDITIVE arms only; never edit the other track's arm; `=0`/unset identity is a completion criterion on every behavioral edit; SN4 byte-identity every commit (R-ICN-D, both tracks); `git pull --rebase` before every commit — .github now moves under THREE concurrent sessions, so expect this file itself to have changed. FR-1(f)'s bypass enumeration should treat cells-arm machinery (s211 `IR_TO`/LIT admissions, `6967f531`) as LIVE CONCURRENT WORK, not post-anchor rot. FR-7's GOAL-ICON-BB cursor rewrite must preserve that file's cells-track pointers.

## ⛔⭐ LIVE CURSOR — s4 (2026-08-07, Sonnet s4 — orientation + diagnosis; context ~28%)
ICN-FR-3 IN PROGRESS: SCRIP HEAD `eb0b2b87` (working tree clean). f0+f1+fib GREEN (SCRIP_ICN_ZFRAME=1 default). SN4 byte-identical confirmed. Watermark re-derived this session: **PASS≈196 FAIL≈45 XFAIL≈28** (partial — rung36 timed out; TOTAL seen=269 of 293; rung36 generator hangs are known gen/hang class, FR-4 scope).
**VSLOT SIGN BUG FIXED THIS SESSION (committed `eb0b2b87`):**
Prior WIP (`f67d7d47`) had vslot offsets NEGATIVE: `-(i+1)*16`. Corrected to POSITIVE `(i+1)*16` matching `rt_icn_zframe_args_install`. Sentinel guards corrected to `!= -1` (was `>= 0`) in `emit_binop_opnd_slot` and IR_VAR drive in `emit.cpp`. These two changes together make f0/f1/fib all green.
**ROOT CAUSE OF REMAINING ~45 FAILURES — FULLY DIAGNOSED, FIX IS NEXT RUNG:**
`emit_binop_opnd_slot()` for non-IR_VAR operands (e.g. IR_ASSIGN result in `(i := i+1) >= 3`, or any anonymous inter-node wire) falls through to `bb_slot_get(o)` → `nd_slot(o)` → `zls_off(o)`, returning a **FORTH-spine RSP-relative offset** (e.g. 48). In a zframe graph `FRQ(48)` encodes as `[rbp+48]` — wrong base. The ZLS result cell at `[rsp+48]` and `[rbp+48]` are different locations; reading the wrong one gives a raw stack address (e.g. `140722734986264` seen in rung09_loops_repeat_break). Named variables are fixed (vslot table via `bb_varslot_peek`); **anonymous inter-node result cells are not** — they still carry ZLS FORTH-spine offsets while the template uses the rbp-relative FRQ accessor.
**THE FIX (ICN-FR-3 completion, next session’s first task):**
In `ir_drive_slot_assign` for zframe graphs: after the vslot override, extend the flat frame layout to include all anonymous value-producing nodes. Assign each value-producing node (that is not a named var) a frame slot at `[rbp + (np + nl + nimplicit + k + 1)*16]` in graph-walk order, and call `bb_slot_register(node, offset)` so `drive_value_slot` / `bb_slot_get` return an rbp-consistent offset that `FRQ()` addresses correctly. This is one-authority: LOWER grants, emitter consumes; no emit-time allocation (TE-4 law). The `zls_build` result cells remain intact for the cells-arm track; this ladder only overrides what `bb_slot_get` returns for zframe graphs.
**Failure taxonomy at current HEAD (partial suite):**
- Generator/suspension stops early or SEGVs (rung03/07/09-loops/rung11-bang/rung01-to_by/rung35-every_do): **FR-4 scope — do not touch until FR-3 complete.**
- Anonymous result-cell ZLS-vs-rbp mismatch (rung09_repeat_break garbage value, rung18_real_relop SEGV, rung35_block_body wrong count): **FR-3 open item — fix next session.**
- rung36 jcon cluster (args/endetab/fncs1/kwds/mathfunc/mindfa/scan/scan1/scan2): pre-existing jcon defects, anchor die-list, not this ladder’s scope.
**gen SEGV still FR-4 scope, γ-retain. Do not touch until FR-3 complete.**
**NEXT RUNG = ICN-FR-3 COMPLETE** — implement `bb_slot_register` override for anonymous value-producing nodes in zframe graphs inside `ir_drive_slot_assign`; re-run repro quartet + full suite; then ICN-FR-3 declared done and move to ICN-FR-4 (generators on-spine).

## THE ANCHOR — VERIFIED FACTS (measured 2026-08-07; do not re-litigate these; DO re-derive all HEAD numbers)
- **Anchor of record: SCRIP `8d0665c8`** — "FLATDISP-8 (s197): frame base follows the rbp pin — Icon 236→250, SNOBOL4 221/219→295/294" (2026-07-28, ON ORIGIN, message carries its own proof per the COMMIT-SELECTION LAW).
- Builds clean on today's toolchain (`make -j4 scrip`, no libgc needed). Against TODAY's corpus (`22f016d7`): **PASS=252 FAIL=11 XFAIL=30 TOTAL=293** — the best Icon ever measured, better than any surviving recorded baseline.
- Repro trio ALL GREEN at anchor, ALL BROKEN at HEAD `5bd4436b` (f0 SEGV rc=139; f1 Error 18 "Return from level zero"; gen untested at HEAD): see SESSION SETUP for the exact programs.
- **Generators worked WITHOUT pthreads** at the anchor — flat_gen pin + γ-retain (mechanics §5).
- **Anchor die-list (11, the parity target — FR-5 grades against THIS SET, not zero):** `rung36_jcon_args endetab fncs1 kwds mathfunc mindfa scan scan1 scan2 subjpos var`. All are the pre-existing FZ-B/C/E jcon clusters catalogued in GOAL-ICON-BB.md — none are frame defects; they belong to that file's FAIL-ZERO ladder, not this one.
- Anchor rung36 category floor (for FR-4/FR-5): control 4/0/9 · gens 8/1/3 · io 3/0/3 · numbers 3/1/4 · reflection 1/4/4 · scan 3/5/1 · strings 9/0/2 · structures 3/0/4.
- **Death:** CARVE-KILL `ef9a7d2c` (flat prologue emitter deleted outright) + `1ba33ea6` (epilogue), 2026-08-01 — a LON DIRECTIVE for the SNOBOL4 per-BB cell campaign ("a nice broken system to build from"). ⛔ THE RESTORATION IS A NEW ARM BEHIND A GRAPH FLAG, NEVER A REVERT of those commits. Icon fell to 1/293 by s207; `flat_lcl_proc` (s211, `ef4841f1`) rebuilt one narrow slice (procs with locals); HEAD sits at 156.
- **Phantom warning:** GOAL-ICON-BB's recorded best `030d6263` (249/12/32, s162) is ABSENT FROM ORIGIN — a pre-rebase phantom (the documented STALE-ORIENTATION disease). `8d0665c8` supersedes it as the anchor of record. `b404fb95` (R12-island era, 242) exists but is the pre-"true stack" configuration Lon has ruled out.

## ERA MECHANICS (read off the anchor tree 2026-08-07 — FR-1 documents each with an anchor→HEAD pairing)
1. **One ζ FRAME per graph activation.** Layout pass sizes `flat_frame_bytes` (kt); α prologue: `sub rsp,kt`.
2. **WIRE HEADER ABOVE THE FRAME:** outside-γ wire `[rsp+kt-24]`, outside-ω wire `[rsp+kt-16]`, caller rbp `[rsp+kt-8]`; then rbp seeded to this activation's flat base when pinned.
3. **ONE PIN PREDICATE** — `emit_jmp_pin_rbp() = flat_deep_arrival || flat_pat || flat_gen` (anchor emit.h:599, FLATDISP-7) — feeds EVERY save/seed/read/restore site in BOTH media so they cannot drift. FLATDISP-8 = the frame base FOLLOWS the pin: pinned graphs address `[rbp+off]` (depth-immune); depth-static graphs address rsp with `op_flat_disp` compensation. The classifier is language-blind by design (the anchor comment says so verbatim).
4. **SLOT GRANTS ONE-AUTHORITY:** `ir_drive_slot_assign` (scrip_ir.c:246 at anchor) grants every value-producer a ZLS slot at LOWER; the emitter FATALs on any ungranted producer (`drive_value_slot`, "never allocate in the emitter"). Operand access = `FR(off)` against the graph frame — this IS the operand-access answer, proven at 252. Named locals via `ir_varslot_of` (scrip_ir.c:233).
5. **SUSPEND = γ-RETAIN:** a suspending activation's γ retains with rsp at the deep frontier; its resume/exit protocol reads the PINNED rbp header (`[rbp+kt-24/-16/-8]`, the REG-7 U5 record contract). Legal because in-statement resumption is LIFO (s89 ruling of record: gen procs = ordinary BBs on the calling spine; the escapee class is coexpr ONLY).
6. **Co-expressions = pthread+semaphore** (`rt_coexpr.c` + bb_create/activate/coret/cofail, landed 2026-07-01). UNTOUCHED by this ladder (charter).
7. **`zd_wl_kind` DOES NOT EXIST at the anchor** — zero per-BB cells anywhere in any graph; the frame WAS the storage. (ZD-1 `d492b909` and everything FORTH landed after.)
8. ⭐ **THE RESURRECTION SOURCE IS ALREADY TEMPLATE-CLEAN:** anchor `src/templates/xa_flat.cpp:164–170` is the x86()-converted prologue (XA-FLAT-CONVERT slice B) — one `x86(...)` concat, R5-parameterless, pin-gated. ⛔ Its raw-byte legacy twin (~line 209, `bytes(4,"\x48…")+u32le(...)`) is the named FORBIDDEN SHAPE — never copy that one. Re-express under HEAD's current x86_asm.h vocabulary; byte-identity with the anchor is NOT the target (the anchor's own comment: encoder short-forms differ by design, R10; behavioral gates only).

## RULING RECORD (defaults chosen by Sonnet 2026-08-07 per Lon's delegation "I do not know the right answer"; Lon overrides at any session start)
- **R-ICN-F — R12 FREE (Lon ruling 2026-08-07).** R12 is available for whatever use is best in Icon graphs — this track or the CELLS track. The RULES.md `test_gate_icn_no_stack` ban targeted the old value-stack r12-as-TOS regime and is superseded by this ruling for both Icon storage arms. This file does not prescribe a use for R12; GOAL-ICN-ZETA-CELLS.md (the cells track, ZK-6) will assign it first. Record any assignment made by a future rung here.
- **R-ICN-A — ROUTING = LOWER-SET BEHAVIORAL GRAPH FLAG (CHOSEN DEFAULT).** `lower_icon.c` marks every graph it produces via a new `IR_graph_t` field (APPENDED AT STRUCT END per the s141 ABI law), named for WHAT it decides, e.g. `int zframe_graph; /* whole-graph ζ frame + wire header: all constructs depth-static, storage = one frame */`. The emitter routes on the flag. No language name past LOWER (the `flat_lcl_proc` comment's own precedent). SNOBOL4/Prolog/other lowerers never set it → their emitted bytes identical BY CONSTRUCTION, and measured every commit. Polyglot-safe by construction whenever that day comes. RECORDED ALTERNATIVE (not chosen): driver-level storage select on `.icn` extension at first dispatch (legal — the driver is the sanctioned language read) — rejected because it couples this restore to the Z4 selector ladder and flips storage process-globally.
- **R-ICN-B — GENERATORS ON-SPINE** per the anchor + s89: flat_gen pin + γ-retain. NO pthread-per-generator. (Pthreads are for co-expressions only — bounded instances.)
- **R-ICN-C — COEXPR STAYS PTHREAD** (Lon, this charter). Zero coexpr code changes in this ladder.
- **R-ICN-D — SN4 INVARIANCE IS A GATE ON EVERY COMMIT:** SNOBOL4 crosscheck byte-identical (or set-identical where an env flake is already documented, e.g. the 127/152 pad pair). This is the s203/s207/post-s211 drift lesson applied in reverse — the flag-gate is this ladder's armor; use it.
- **R-ICN-E — FOUR-MODE FIT:** this regime is the FRAME_RSP family at per-graph granularity. `8d0665c8` upgrades config 2's Icon-side anchor (GOAL-ZETA-FOUR's own commit-selection note invites a later, better frame-rsp point). No fifth mode; a future heap lift (allocator swap: arena bump for `sub rsp`) is a separate, later ruling.

## CROSS-CUTTING LAWS (the walker cannot miss these)
BOTH-MEDIUM MANDATORY · TEMPLATE-ONLY EMISSION — re-express, never paste (R2/R5/R7/R9/R10; `IF(MEDIUM_TEXT,…)+IF(MEDIUM_BINARY,…)` is the named forbidden shape) · a killswitch on every behavioral arm · MONITOR-FIRST on any divergence (Icon: `CSN_NO_SEGV_HANDLER=1` + gdb spin/ignore counters + `scripts/honest_icon_correctness.sh`; the SN4 IPC monitor is SN4-scoped) · CONSULT CANONICAL SOURCES (`refs/jcon-master/tran/irgen.icn` + `refs/icon-master/src/runtime/*.r` — set up refs/ every session) · O2-DIRECTED-ONLY · `timeout 8s` unit / `30s` corpus · handoff step-4 `.s` regen when codegen touched, incl. `update_icon_bench_asm.sh` (DEMO+BENCHMARK ONLY — the script refuses rung tests) · LIVE CURSOR moves every handoff or the handoff is not done · "HANDOFF COMPLETE" only from `scripts/handoff_status.sh` verbatim stdout · push needs Lon's credential; a local commit is NOT a handoff.

## SESSION SETUP (every session)
```bash
git clone https://github.com/snobol4ever/.github.git /home/claude/.github
git clone https://github.com/snobol4ever/corpus /home/claude/corpus
git clone https://github.com/snobol4ever/SCRIP  /home/claude/SCRIP
cd /home/claude/SCRIP && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
bash scripts/install_system_packages.sh && rm -f scrip && make -j4 scrip   # ~3 min; verify [ -x scrip ]
mkdir -p refs   # then symlink the unzipped icon-master + jcon-master archives Lon supplies; verify ls before trusting
git worktree add /home/claude/wt-icnframe 8d0665c8 && (cd /home/claude/wt-icnframe && make -j4 scrip)   # the LIVING REFERENCE — verify populated before trusting
bash scripts/test_icon_all_rungs.sh 2>/dev/null | tail -1    # re-derive the HEAD watermark FIRST; prose is stale by design
```
**Repro quartet** (write fresh each session; Icon semicolon rule — the front-end does ZERO newline processing):
```
f0.icn:  procedure f(); write("hi"); end
         procedure main(); f(); end
f1.icn:  procedure f(x); write(x); end
         procedure main(); f("hello"); end
gen.icn: procedure g(); suspend 1; suspend 2; end
         procedure main(); every write(g()); end
fib.icn: procedure fib(n); if n < 2 then return n else return fib(n-1) + fib(n-2); end
         procedure main(); write(fib(15)); end        # expect 610; proves per-activation frames under recursion
```

## RUNGS (stop at first `- [ ]`; every rung ends committable + watermark-proven; R-ICN-D SN4 proof on EVERY commit)

- [x] **ICN-FR-0 ANCHOR VERIFIED.** ✅ 2026-08-07 — everything in THE ANCHOR block above; worktree built; suite 252/11/30; repro trio green; mechanics read off the tree.

- [x] **ICN-FR-1 EXTRACT-ICN-FRAME.md (archaeology only).** ✅ s0 2026-08-07 — all 7 rows (a–g) inventoried inline during FR-2 implementation. Key findings: (a) prologue NEW-ARM; (b) emit_jmp_pin_rbp zframe_graph SUBSUMES flat_lcl_proc; (c) CLASS ZF ledgered; (d) param-landing slot-layout mismatch found (deferred FR-3); (e) ir_drive_slot_assign coverage confirmed; (f) ZD bypass via separate flag; (g) CLASS ZF direct wire-read epilogue.

- [x] **ICN-FR-2 THE GRAPH-FRAME REGIME RETURNS (gated, both media).** ✅ COMPLETE s1 `bcf05d33` — f0+f1+fib GREEN m3. Icon 188/75/30 (+23 PASS from 165). SN4 R-ICN-D byte-identical. ZD exclusion for zframe graphs. dc stub: r10 arg-ptr save, [r10+0] load, flat_lbl_α text target. gamma epilogue: mov rdi,rax; mov rsi,rdx. rt_icn_zframe_args_install() new. lbl_α binary-mode define. SCRIP_ICN_ZFRAME=0 reverts.
  (a) xa_flat prologue + epilogue — anchor x86() arm (:164) vs HEAD's deletion; HEAD residue = BLOB-GRANT flat_pat arm + `flat_lcl_proc` arm (emit.cpp ~:2344 at `5bd4436b`; re-grep, lines drift daily).
  (b) `emit_jmp_pin_rbp` — survives at HEAD with a `flat_lcl_proc` disjunct added (emit.h ~:634); decide whether FR-2's general flag SUBSUMES flat_lcl_proc (recommended) or coexists.
  (c) Wire EXIT — anchor reads the frame header directly; HEAD `_wire_stub` (emit.cpp ~:2719 exit-class ledger) routes to `bb_glue_wire_γ/ω` → `rt_flat_ret_snap` → `g_pcall_wires[]`, which is the standing Error-18 on `f("hello")`. FR-3 fixes this; FR-1 documents both shapes and the CLASS ledger fit.
  (d) Param/arg landing AT THE ANCHOR — answer definitively (rt_proc_enter rcx=γ/rdx=ω + `g_call_args[]`? something else?) vs HEAD's `rt_lcl_proc_args_install`; choose the minimal-diff mechanism and say why.
  (e) `ir_drive_slot_assign` grant coverage at HEAD — is every Icon value-producing kind granted? The `drive_value_slot` FATAL is the census instrument; list gaps.
  (f) Post-anchor machinery that could DOUBLE-BILL a flagged graph — ZD/FORTH landed since (zd_wl_kind, op_fc_disp, UCLAIM, ICN-ZD `6967f531` admitting IR_CALL_BUILTIN_ICON, bb_to scaffold at `ef4841f1`): enumerate every emit.cpp site a `zframe_graph=1` graph must bypass, and how `SCRIP_ICN_ZFRAME=0` restores today's exact path.
  (g) Epilogue/whack shape (`1ba33ea6`'s deletion) and where the restored whack sits relative to HEAD's CLASS O/C/P ledger.
  Completion: doc committed to .github; every row decided; zero HEAD edits.

- [ ] **ICN-FR-2 THE GRAPH-FRAME REGIME RETURNS (gated, both media).**
  (2a) `IR_graph_t` += `zframe_graph` at STRUCT END (s141 ABI law), comment names WHAT it decides, never a language.
  (2b) `lower_icon.c` sets it on every graph it produces (main + every proc). No other lowerer touches it.
  (2c) `g_emit` twin populated at the emit_chain choke; `emit_jmp_entry_clear` zeroes it (the s211 pattern verbatim).
  (2d) Prologue arm re-expressed from anchor xa_flat.cpp:164–170 behind the flag: `sub rsp,kt` + wire header kt-24/-16/-8 + pin-gated rbp seed. Killswitch `SCRIP_ICN_ZFRAME` (default ON for flagged graphs; `=0` MUST reproduce pre-rung HEAD byte-exactly — that identity is a completion criterion).
  (2e) Epilogue twin restored under the same gate per FR-1(g).
  (2f) kt from the existing flat layout pass; slots from `ir_drive_slot_assign`; params/locals per FR-1(d); pin rides `emit_jmp_pin_rbp` with the FR-1(b) subsumption decision applied.
  Completion: f0 + f1 green BOTH modes · SN4 crosscheck byte-identical ×3 regen · `SCRIP_ICN_ZFRAME=0` byte-identical to pre-rung HEAD · Icon suite ≥ rung-start (zero regressions) · medium-invisible gate not regressed.

- [ ] **ICN-FR-3 WIRE EXIT VIA THE FRAME HEADER.** For flagged graphs, γ/ω emit: unwind to flat base; load wire from `[fb+kt-24]` (γ) / `[fb+kt-16]` (ω); restore caller rbp from `[fb+kt-8]`; `jmp` the wire — the s211 cursor's own prescription, now in the general arm, replacing the `rt_flat_ret_snap` pcall-array read for this class only (the exit-class ledger gains a named class). Completion: f1 AND fib.icn green both modes (recursion proves per-activation frames) · Error 18 extinct on the quartet · SN4 held.

- [ ] **ICN-FR-4 GENERATORS ON-SPINE.** flat_gen flagged graphs: γ-retain (rsp stays at the deep frontier across suspend) + β-resume against the pinned rbp header per the anchor's REG-7 U5 contract. Audit bb_suspend / bb_every / bb_to at HEAD for post-CARVE-KILL rot (s206 recorded the push=0/whack=2/pop=3 shape on the 7-line suspend repro) and repair in the flagged arm only. Completion: gen.icn green both modes · `rung36_gens` ≥ 8 PASS (anchor floor) · SN4 held.

- [ ] **ICN-FR-5 FULL-SUITE RATCHET TO ANCHOR PARITY.** Run `test_icon_all_rungs.sh`; hunt each residual MONITOR-FIRST (gdb spin-counter; never print-scatter). Target: **PASS ≥ 252 with residual FAIL ⊆ the anchor die-list above** — those 11 are pre-existing jcon defects owned by GOAL-ICON-BB's FAIL-ZERO, out of this ladder's scope. Completion: watermark recorded in the cursor; one-line disposition per residual failure.

- [ ] **ICN-FR-6 GATES + PROCESS.**
  (6a) `scripts/test_gate_icn_zframe.sh`: repro quartet both modes + SN4 byte-identity + suite floor ratchet (a baked count file, DESCENDING-failure ratchet, never a zero-assert) + `SCRIP_ICN_ZFRAME=0` identity. Wire into the pre-commit habit.
  (6b) Existing Icon gates re-proven green: `test_gate_icn_no_stack`, `test_gate_icn_one_reg_frame`, `test_gate_icn_semicolon_required`, ICON SM `count=0`, medium-invisible not regressed vs baseline.
  (6c) Propose the RULES.md FACT RULE: **ICON WATERMARK REQUIRED ON EVERY SHARED-EMITTER/TEMPLATE COMMIT** — third recurrence proven (s203 ZW-1, s207 1/293, post-s211 drift measured 2026-08-07: 29 emitter commits, zero Icon proofs). Lon signs; this ladder only drafts it.
  Completion: gate script committed + green.

- [ ] **ICN-FR-7 CURSOR + DOC SYNC.** Rewrite GOAL-ICON-BB.md's LIVE CURSOR to current reality (its s211 block is stale; point it at this ladder's outcome; retire the phantom `030d6263` baseline in favor of `8d0665c8`). ARCH-ICON.md storage note (whole-graph frames per flagged graph; pin predicate; coexpr = pthread). GOAL-ZETA-FOUR.md one-line cross-ref (`8d0665c8` = the Icon-side frame-rsp anchor upgrade, per its own commit-selection note). Do NOT edit PLAN.md's goals table (RULES). Completion: docs committed; `handoff_status.sh` verbatim.

## SESSION SIZING + CONTEXT BUDGET
3–4 sessions: FR-1 (+start FR-2) · FR-2/FR-3 (the core — budget the whole session) · FR-4/FR-5 · FR-6/FR-7. Every rung boundary is a safe handoff point. Report approximate context percentage at natural checkpoints without being asked; keep anchor-tree reads to `grep -n` + small `sed` windows — the anchor worktree is for building and grepping, never wholesale reading.

## HONEST LIMITS
(a) HEAD moves daily under parallel SN4 sessions — re-derive every number at session start; the flag-gate + SN4 byte-identity is this ladder's armor against the drift that killed Icon twice. (b) The anchor's BYTES are not the target — behavioral gates only (its own comments say the encoder short-forms differ by design). (c) Anchor parity (252, die-list ⊆ the 11) is THIS ladder's finish line; the residual 11 FAILs and 30 XFAILs belong to GOAL-ICON-BB's FAIL-ZERO / XFAIL-ZERO ladders. (d) This file cannot coerce its walker; the LIVE CURSOR, the gates, and Lon's review are the enforcement.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
