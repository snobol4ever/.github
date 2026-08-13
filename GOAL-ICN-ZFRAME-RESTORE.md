# GOAL-ICN-ZFRAME-RESTORE.md — Restore Icon to full glory on ZETA FRAMES (STACK); co-expressions stay PTHREAD

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


## ⚙️ CONCURRENT BY DEFAULT — AND THE REPOS MOVE UNDER YOU

**Many seats run this file's siblings at the same time. Edit any file, commit and push whenever a rung is buildable and green — mid-session, per rung. Never park work or decline an edit on concurrency grounds; stranding has cost this project far more than merging ever has.** Git merges; `git pull --rebase` and resolve normally.

**⛔ ASSUME ORIGIN MOVED SINCE YOU LAST LOOKED.** Another seat may have landed in your exact files while you were reading them.
- `git pull --rebase` before every push; **re-prove THIS file's gate/watermark after any rebase** — shared state moves under you and a watermark measured pre-rebase is void.
- `git log origin/main..HEAD` at orientation AND before handoff. **A clean `git status` is NOT a clean tree** — it hides local commits a peer seat left in a shared working copy.
- Place trees at canonical absolute paths (`/home/claude/{SCRIP,corpus,.github,x64}`) BEFORE running any gate: **many scripts grade a tree by absolute path.**
- Prefer **one clone per seat**; two seats in one working copy silently overwrite each other's uncommitted edits, and a global gitconfig scrambles attribution.
- Push **code repos before `.github`**, so no FINDING ever describes an unpushed tree.
- Push needs a credential — **ask Lon in chat and wait.** Never write push status into a doc.
- `bash scripts/handoff_status.sh` verbatim is the ONLY push truth. Not this file, not a commit message.

**Semantic collisions (two seats claiming one register) are caught MECHANICALLY by the claim gates, not by scheduling.** That is why no window is needed.

## ⛔ CONCURRENT TWIN TRACK (Lon directive, 2026-08-07, added same day as carve)
**`GOAL-ICN-ZETA-CELLS.md` walks the OTHER embodiment SIMULTANEOUSLY: 100% per-BB ζ CELLS on the RSP FORTH spine (the SN4 ZD machinery completed for Icon — LVA locals as cells, GVA globals off-stack, suspension via pthread-stacks-or-pending-cells decided by measurement).** Lon: "We would have FRAMES on STACK and CELLS on STACK being developed simultaneously." BOTH KEPT, switch-selected (the ARCH-ICON two-backends precedent) until Lon picks a default. Rules of engagement, mirrored in both files: one graph is NEVER in both arms — the cells track's `SCRIP_ICN_CELLS=1` opt-IN suppresses `zframe_graph` at the SAME LOWER site R-ICN-A defines (its draft R-ZK-A; either side may renegotiate the selector shape WITH the other's file updated in the same commit); shared choke sites (`zd_*` one-authority lines, BLOB-GRANT block, staging choke) take ADDITIVE arms only; never edit the other track's arm; `=0`/unset identity is a completion criterion on every behavioral edit; SN4 byte-identity every commit (R-ICN-D, both tracks); `git pull --rebase` before every commit — .github now moves under THREE concurrent sessions, so expect this file itself to have changed. FR-1(f)'s bypass enumeration should treat cells-arm machinery (s211 `IR_TO`/LIT admissions, `6967f531`) as LIVE CONCURRENT WORK, not post-anchor rot. FR-7's GOAL-ICON-BB cursor rewrite must preserve that file's cells-track pointers.

## ⛔⭐ LIVE CURSOR — s18 (2026-08-09, Sonnet s18 — FR-5 ONE-SLOT FIX LANDED; watermark 247→248; SCRIP `8487d499`)
**NEXT RUNG = ICN-FR-5 (continuing — 5 in-scope fails remain).** Watermark at HEAD `8487d499`: **m3 PASS=248 FAIL=15 XFAIL=30 TOTAL=293**. R-ICN-D: roman.sno md5 `77fc5a38d566fe87392b6e1a6331ac8f` BYTE-IDENTICAL with/without SCRIP_ICN_ZFRAME. Canary `rung17_real_arith_real_add` → `4.0`.

**ONE-SLOT FIX LANDED (SCRIP `8487d499`):** FR-4's four process globals were correct for one pending generator; two simultaneously pending (nested or sibling) caused the second to clobber the first. Fix: persistent `icn_gen_state_t` stack (g_icn_gen_stk, initial cap 64, grows by doubling) keyed by `generator_rbp`. PUSH at `save_wires` (prologue, after `lexprep2` populates `pcall.fb`). UPDATE cont at `save_cont` (each suspend α). POP via `save_wires(gen_rbp, NULL, NULL)` sentinel at ω exit. READ by LIFO scan at γ/ω epilogues and β-resume. Global cache maintained as fast path. KEY ORDERING: `save_wires`/`save_caller_rbp` moved after `lexprep2` in prologue. ω epilogue reads `caller_rbp` BEFORE the pop (saves in `rbx`). Template ABI changes: all save/get functions take `gen_rbp` as first arg; `bb_suspend.cpp`, `xa_flat.cpp` (prologue + both epilogues), `bb_call_proc_staged.cpp` (β arm pre-loads FRQ(act+8) into rdi).

**MEASURED (all probe table GREEN):** pd `1 2 10 20 done`; pb3 `10 20 10 20 done`; pb4 `10 20 done`; pb1 `10 done`; pa `no 1 done`.

**NEWLY PASSING:** `genqueen` rc=1 PASS 56/56 lines (was rc=124 HANG pb4-shape). `cxprimes` rc=1 PASS 25/25 lines (was rc=134 SIGABRT; in XFAIL set — counts as zero in FAIL but shows correctness).

**5 IN-SCOPE FAILS REMAINING:**
- `rung36_jcon_recogn` — rc=124 HANG. Recursive suspend: `s()` suspends the result of calling itself. Nested depth unbounded → state stack stores each activation correctly but β-resume path through multiple nested levels may have a wiring issue. MONITOR-FIRST gdb spin on `proc_s_α`.
- `rung36_jcon_level` — RUNAWAY (rsp-drift-per-β, distinct mechanism, s11). NOT billable to the one-slot fix.
- `rung36_jcon_prepro` — &features interaction. MONITOR-FIRST.
- `rung37_proc_lookup` — DC-stub double-execute, pre-existing. MONITOR-FIRST gdb on `proc_p_dcα`.
- `rung03_suspend_return` — pre-existing suspend/return interaction in rung03 cluster. MONITOR-FIRST.

**⛔ STALE-ASM-TAG THIRD INSTANCE STILL LIVE:** `rtx_icnagg.S` and `rtx_icnsub.S` carry `DT_DATA=100` (live `0x70`). Elevated to RULES.md FACT RULE candidate in s17 cursor. Still unfixed at this session's close.

## ⛔⭐ LIVE CURSOR — s17 (2026-08-09, Opus s17 — CUSTODIAL: re-derived watermark 247, published s16's stranded work; NO new rung)
**NEXT RUNG = ICN-FR-5 (continuing — 6 in-scope fails; the FIX DIRECTION is written, see FINDING-2026-08-09-…-ONE-SLOT).** Watermark **MEASURED THIS SESSION, TWICE — before and after a mid-handoff rebase that pulled 4 parallel commits (AB-2/AB-3, PL-FR-4 N0-SUPPRESS + W1 m4 twins, .s regen; then ZK-2 IR_BINOP_TEST, OS-2 SLICE-1, OPS-1 driver)** — at HEAD `4a5f8731`: **m3 PASS=247 FAIL=16 XFAIL=30 TOTAL=293**. R-ICN-D re-proven by direct run: roman.sno output md5 `e02da06b49f64c44168830cff34bba94` identical with `SCRIP_ICN_ZFRAME` on and `=0`. Canary `rung17_real_arith_real_add` → `4.0` (no stale-.so).

**⚠ WHAT THIS SESSION DID AND DID NOT DO — READ BEFORE TRUSTING THE ABOVE.** s17 wrote NO code and moved NO rung. It found the working tree holding **concurrent session s16's stranded work**: SCRIP `64fe9c18`→rebased `4a5f8731` (lexcmp fix) committed but UNPUSHED, and s16's FINDING sitting UNTRACKED in `.github`. s17 built, re-derived the watermark independently (247/16/30 — confirms s16's claim to the digit), re-proved R-ICN-D, and PUBLISHED both. The +1 over s15's 246 is **s16's fix, not s17's**. Attribution matters here because the next session inherits a queue whose most valuable item is s16's diagnosis, not its patch.

**THREE CORRECTIONS TO THE s15 CURSOR BELOW (do not re-litigate from it):**
1. **`lexcmp` was NOT "pre-existing image() quoting, not a frame defect."** s15 dismissed it; s16 falsified that. It was `rtx_icnrel.S` carrying pre-s229 tags DT_S=1/DT_I=6 (live 0x02/0x03), so `rt_str_coerce`'s asm identity arm swallowed csets unconverted. FIXED in `4a5f8731` (+1). **A cursor's "not a frame defect" disposition is a hypothesis, not a finding — s15 recorded six more of them below and at least one was wrong.**
2. **`genqueen` is NOT "0L: produces nothing."** It is `rc=124` **zero-output HANG**, and it is not alone: it shares a mechanism with `recogn` and probably `cxprimes`.
3. **The root cause of that mechanism is FOUND (s16), not open.** The FR-4 (s8) fix parked all cross-yield generator state in **four one-slot process globals** (`rt.c:1408-1411`). One slot serves exactly ONE pending generator. Two pending simultaneously — nested (`suspend h()` inside a generator) or sibling (`g() & h()`) — and the second clobbers the first. Silent hang, never a crash. s16's probe table (pd GREEN / pb3, pb4 HANG) is the reproduction; `pa` acquits `<-`. **`rt.c:1412` already dual-writes caller_rbp per-activation into `g_pcall[].rname` exactly as s8's own "option B" specified — and `rt.c:1413` returns the global anyway. The per-activation half was built and never read.**

**NEXT SESSION STARTS HERE:** implement s16's FIX DIRECTION (key pending state by the generator's own activation; getter finds the record by `.fb == arg`). It is a **template-ABI rung, not a runtime patch** — call-site arity changes ripple through `bb_suspend.cpp` / `bcps_spine_gen_arm` / `xa_flat` epilogues + `rtx_icngen.S` veneers + `.s` regen; s141 append-only law applies to the pcall record. **Budget the whole session.** Test each of `recogn`/`cxprimes` against the pd/pb probes BEFORE billing it to this defect — `level` (s11: distinct rsp-drift-per-β), `prepro`, and `proc_lookup` (DC-stub double-execute) are explicitly NOT claimed.

**⛔ ELEVATED — THE STALE-ASM-TAG CLASS IS NOW THREE-FOR-THREE, AND ONE IS STILL LIVE.** s15 fixed `DT_E` in `rtx_icncall.S`; s16 fixed `DT_S`/`DT_I` in `rtx_icnrel.S`; **`rtx_icnagg.S` and `rtx_icnsub.S` still carry `DT_DATA=100` (live `0x70`) — UNFIXED, shipping, and silently wrong by construction.** Every instance had the same shape: the RTX gate is ON by default, the asm arm mints or tests a descriptor with a pre-renumber tag, the C fallback is correct, and the optimisation silently corrupts. **The structural gap: `_Static_assert` in `rtx_init.c` cannot reach asm `#define`s, so nothing links the two spellings.** A generated single-source header (`descr.h` → `.inc`) or a build-time grep gate would have caught all three. Recommend this be raised to a RULES.md FACT RULE candidate alongside FR-6(c); s17 does not have Lon's signature to write one.

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

- [x] DONE — ICN-FR-0 ANCHOR VERIFIED
- [x] DONE — ICN-FR-1 EXTRACT-ICN-FRAME
- [x] DONE — ICN-FR-2 THE GRAPH-FRAME REGIME RETURNS (gated, both media) (bcf05d33)
- [x] DONE — ICN-FR-3 WIRE EXIT VIA THE FRAME HEADER (76287768)
- [x] DONE — ICN-FR-4 GENERATORS ON-SPINE
- [ ] **ICN-FR-5 FULL-SUITE RATCHET TO ANCHOR PARITY.** ⬅ NEXT. Run `test_icon_all_rungs.sh`; hunt each residual MONITOR-FIRST (gdb spin-counter; never print-scatter). Target: **PASS ≥ 252 with residual FAIL ⊆ the anchor die-list above** — those 11 are pre-existing jcon defects owned by GOAL-ICON-BB's FAIL-ZERO, out of this ladder's scope. **The s9 cursor carries the classified 34-program in-scope queue (218+34=252 exact); start at rung01_paper_to_by (NEW at s8), then the SUSPEND/GEN 8.** Completion: watermark recorded in the cursor; one-line disposition per residual failure.

- [ ] **ICN-FR-6 GATES + PROCESS.**
  (6a) `scripts/test_gate_icn_zframe.sh`: repro quartet both modes + SN4 byte-identity + suite floor ratchet (a baked count file, DESCENDING-failure ratchet, never a zero-assert) + `SCRIP_ICN_ZFRAME=0` identity. Wire into the pre-commit habit.
  (6b) Existing Icon gates re-proven green: `test_gate_icn_no_stack`, `test_gate_icn_one_reg_frame`, `test_gate_icn_semicolon_required`, ICON SM `count=0`, medium-invisible not regressed vs baseline.
  (6c) Propose the RULES.md FACT RULE: **ICON WATERMARK REQUIRED ON EVERY SHARED-EMITTER/TEMPLATE COMMIT** — third recurrence proven (s203 ZW-1, s207 1/293, post-s211 drift measured 2026-08-07: 29 emitter commits, zero Icon proofs). Lon signs; this ladder only drafts it.
  (6d) Land `scripts/test_icon_m4_all_rungs.sh` — the canonical mode-4 full-suite runner (recipe in the s9 cursor; copy `test_icon_all_rungs.sh` per CORPUS-LOCATIONS' sibling-script rule so the DENOMINATOR MATCHES the m3 runner's 293, not the s9 sweep's 300). Until it lands, every m4 suite number is a sweep-instrument reading and must say so.
  Completion: gate script committed + green.

- [ ] **ICN-FR-7 CURSOR + DOC SYNC.** Rewrite GOAL-ICON-BB.md's LIVE CURSOR to current reality (its s211 block is stale; point it at this ladder's outcome; retire the phantom `030d6263` baseline in favor of `8d0665c8`). ARCH-ICON.md storage note (whole-graph frames per flagged graph; pin predicate; coexpr = pthread). GOAL-ZETA-FOUR.md one-line cross-ref (`8d0665c8` = the Icon-side frame-rsp anchor upgrade, per its own commit-selection note). Do NOT edit PLAN.md's goals table (RULES). Completion: docs committed; `handoff_status.sh` verbatim.

## SESSION SIZING + CONTEXT BUDGET
3–4 sessions: FR-1 (+start FR-2) · FR-2/FR-3 (the core — budget the whole session) · FR-4/FR-5 · FR-6/FR-7. Every rung boundary is a safe handoff point. Report approximate context percentage at natural checkpoints without being asked; keep anchor-tree reads to `grep -n` + small `sed` windows — the anchor worktree is for building and grepping, never wholesale reading.

## HONEST LIMITS
(a) HEAD moves daily under parallel SN4 sessions — re-derive every number at session start; the flag-gate + SN4 byte-identity is this ladder's armor against the drift that killed Icon twice. (b) The anchor's BYTES are not the target — behavioral gates only (its own comments say the encoder short-forms differ by design). (c) Anchor parity (252, die-list ⊆ the 11) is THIS ladder's finish line; the residual 11 FAILs and 30 XFAILs belong to GOAL-ICON-BB's FAIL-ZERO / XFAIL-ZERO ladders. (d) This file cannot coerce its walker; the LIVE CURSOR, the gates, and Lon's review are the enforcement.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
