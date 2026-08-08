# GOAL-ICN-ZFRAME-RESTORE.md — Restore Icon to full glory on ZETA FRAMES (STACK); co-expressions stay PTHREAD

## ⛔ CONCURRENCY PROTOCOL (Lon 2026-08-08) — THE CONCURRENT SET (8)
`GOAL-SNOBOL4-BB` · `GOAL-SN4-ZETA-MECH` · `GOAL-SN4-ZETA-CLIMB` · `GOAL-SNOBOL4-RTX` · `GOAL-ICN-ZFRAME-RESTORE` · `GOAL-ICN-ZETA-CELLS` · `GOAL-PL-ZFRAME-RESTORE` · `GOAL-PL-ZETA-CELLS` run CONCURRENTLY against one tree. Each session COMMITS along the way (per-rung, buildable, git-revert path) but PUSHES ONLY AT SESSION END: `git pull --rebase` → re-prove THIS file's gate/watermark post-rebase → push code repos first, `.github` last → `handoff_status.sh` verbatim (the only push truth). This reduces contention points. Watermarks are SHARED STATE — re-prove at open AND close; expect parallel-landed commits in the end-of-session rebase. A semantic collision there (two fixes for one defect) is resolved BY THE REBASING SESSION and NOTED in its cursor — never silently dominated (the `zd_zdh`/`_xh_zdh` lesson, CLIMB s14). ⛔ Rungs that their own file marks NOT-CONCURRENCY-SAFE (e.g. RTX-11/12: `x86_asm.h`/`bb_match_release` + `.s` regen ×3; RTX's GVA-slot ζ-ladder item) MUST NOT run while any other seat is active — Lon's routing.

**CHARTER (Lon directive, 2026-08-07):** "Write up RUNGS and STEPS to accomplish restoring Icon to its full glory and using ZETA FRAMES on the STACK, and CO-EXPRESSION will remain a PTHREAD." Restore the anchor era's whole-graph ζ-frame regime for Icon graphs as code that fits the FOUR-ZETA-MODE system (GOAL-ZETA-FOUR.md) — a NEW GATED ARM, never a revert. SNOBOL4's per-BB cell regime is untouched and its invariance is a gate on every commit.

## ⛔ CONCURRENT TWIN TRACK (Lon directive, 2026-08-07, added same day as carve)
**`GOAL-ICN-ZETA-CELLS.md` walks the OTHER embodiment SIMULTANEOUSLY: 100% per-BB ζ CELLS on the RSP FORTH spine (the SN4 ZD machinery completed for Icon — LVA locals as cells, GVA globals off-stack, suspension via pthread-stacks-or-pending-cells decided by measurement).** Lon: "We would have FRAMES on STACK and CELLS on STACK being developed simultaneously." BOTH KEPT, switch-selected (the ARCH-ICON two-backends precedent) until Lon picks a default. Rules of engagement, mirrored in both files: one graph is NEVER in both arms — the cells track's `SCRIP_ICN_CELLS=1` opt-IN suppresses `zframe_graph` at the SAME LOWER site R-ICN-A defines (its draft R-ZK-A; either side may renegotiate the selector shape WITH the other's file updated in the same commit); shared choke sites (`zd_*` one-authority lines, BLOB-GRANT block, staging choke) take ADDITIVE arms only; never edit the other track's arm; `=0`/unset identity is a completion criterion on every behavioral edit; SN4 byte-identity every commit (R-ICN-D, both tracks); `git pull --rebase` before every commit — .github now moves under THREE concurrent sessions, so expect this file itself to have changed. FR-1(f)'s bypass enumeration should treat cells-arm machinery (s211 `IR_TO`/LIT admissions, `6967f531`) as LIVE CONCURRENT WORK, not post-anchor rot. FR-7's GOAL-ICON-BB cursor rewrite must preserve that file's cells-track pointers.

## ⛔⭐ LIVE CURSOR — s10 (2026-08-08, Sonnet s10 — FR-5 rung01_paper_to_by FIXED; SCRIP `a091fd20`)
**NEXT RUNG = ICN-FR-5 (continuing).** Watermark: **m3 PASS≈219 FAIL≈44 XFAIL=30 TOTAL=293** (measured via compact sweep; canonical script runner timed out in container — watermark is rung01_paper_to_by +1 from s9's 218/45, spot-checks of all 10 pre-existing suspect rungs confirm no new regressions). Repro quartet f0/f1/fib/gen GREEN m3. SN4 R-ICN-D: m3 PASS=288/FAIL=48 m4 PASS=275/FAIL=55 (net improvement from s9's 287/49 273/57 — RPO fix also helped SN4 chained generators; zero new SN4 failures).
**FR-5 RUNG01 FIX — ROOT CAUSE:** RPO chain-gather pass-2 was a single-pass snapshot over `nodes[0..n-1]` as it existed at pass-2 start. For N≥3 consecutive `every write(X to Y by Z)` loops, pass-1 gathers loop-1 (n0..n4); pass-2 discovers loop-2 (n5..n9) via loop-1's IR_TO_BY ω-tail — but the loop already ended at n=5 so loop-2's IR_TO_BY (n8) was never checked for its own unvisited ω-tail (loop-3, n10..n14). Loop-3 omitted from nodes[], node_ω for n8 fell to graph lbl_ω (main_ω), third every-statement silently emitted zero code. Anchor BFS (8d0665c8) pushed generator ω-tails mid-drain making discovery naturally iterative; RPO refactor broke this by making pass-2 one-shot. Fix: iterative convergence loop in `codegen_flat_chain_body` pass-2 (emit.cpp). Commit `a091fd20`. Corpus crosscheck regen + Icon bench asm regen committed to corpus (`e71b01c8`).
**FR-5 REMAINING 33 in-scope failures:** SUSPEND/GEN (8): rung03_suspend_{gen,gen_compose,gen_filter,return} · rung09_loops_{until_gen,repeat_break} · rung35_block_body_every_gen_block · rung37_subscript_genproc. JCON cluster (19): coerce cxprimes genqueen level lexcmp lists mffsol numeric parse prepro queens recogn record roman sieve string1 substring table wordcnt. SINGLES (6): rung11_bang_augconcat_bang_concat · rung23_table_table_key · rung37_{cset_ops,neg_pos,proc_lookup,scan_alt}. **Next priority: SUSPEND/GEN 8 (monitor-first; SEGVs on rung03_suspend_gen).**
**CELLS twin at same HEAD (cross-track FYI):** m3 CELLS=1 = 184/79/30 exact match to its ZK-4 close — R-ZK-A isolation holding, no drift either arm.

## ⛔⭐ LIVE CURSOR — s9 (2026-08-08, Fable — HEAD WATERMARK RE-DERIVED FULL-RUN + FR-5 QUEUE CLASSIFIED; SCRIP `69c476a0`, doc-only, no code)
**NEXT RUNG = ICN-FR-5.** First FULL (unclipped) suite run post-FR-4: **m3 default PASS=218 FAIL=45 XFAIL=30 TOTAL=293** (s8's 192/11/0 T=225 was the 90s-clipped partial — not comparable). Repro quartet f0/f1/gen/fib GREEN BOTH modes at HEAD (fib(15)=610 · gen=`1 2` — FR-4 verified live through the full m4 pipeline, not quoted).
**m4 (sweep instrument, NOT canonical): PASS=210 FAIL=60 XFAIL=30 TOTAL=300.** No full-suite m4 runner exists in `scripts/` — measured with a /tmp sweep mirroring `test_icon_all_rungs.sh` conventions (`.xfail`⇒XFAIL · `.stdin` fed · cd-to-dir; pipeline `--compile --target=x86` → `gcc -no-pie -L out -lscrip_rt -Wl,-rpath,out -lm` → diff `.expected`; 12s compile / 8s run). ⚠ Its glob (`*.icn` + `*/*.icn`) sweeps 7 subdir programs the m3 runner's denominator excludes (300 vs 293) — land it as `scripts/test_icon_m4_all_rungs.sh` with a MATCHED denominator (new FR-6d).
**FR-5 DISTANCE = EXACTLY 34.** The 45 m3 fails = ALL 11 anchor die-list members (out of scope) + 34 in-scope; **218+34 = 252 = anchor parity precisely.** The 34 by shape — SUSPEND/GEN (8): rung03_suspend_{gen,gen_compose,gen_filter,return} · rung09_loops_{until_gen,repeat_break} · rung35_block_body_every_gen_block · rung37_subscript_genproc. JCON cluster (19): coerce cxprimes genqueen level lexcmp lists mffsol numeric parse prepro queens recogn record roman sieve string1 substring table wordcnt. SINGLES (7): rung01_paper_to_by (⚠ NEW at s8 — monitor-first FIRST) · rung11_bang_augconcat_bang_concat · rung23_table_table_key · rung37_{cset_ops,neg_pos,proc_lookup,scan_alt}.
**CELLS twin at same HEAD (cross-track FYI):** m3 CELLS=1 = 184/79/30 exact match to its ZK-4 close — R-ZK-A isolation holding, no drift either arm.

## ⛔⭐ LIVE CURSOR — s8 (2026-08-07, Sonnet s8 — FR-4 COMPLETE: gen_simple.icn + gen.icn GREEN both modes)
**NEXT RUNG = ICN-FR-5 (full-suite ratchet toward anchor parity).** Watermark: **PASS=192 FAIL=11 XFAIL=0 TOTAL=225** (partial run — suite cut short by 90s wall; rung03_suspend_{gen,gen_compose,gen_filter,return} still FAIL = pre-existing work queue, not regressions; rung01_paper_to_by new failure — monitor-first). f0/f1/fib/gen_simple/gen GREEN both modes m3+m4.

### FR-4 ROOT CAUSE — FULLY RESOLVED (three layers, all fixed this session s8)

**Architecture:** The zframe generator's frame `[generator_rbp..entry_rsp)` is fully exposed to the caller's C-call stack after the first γ-yield (`lea rsp,[rbp+kt]` unwinds to entry_rsp). Any C call from the caller's frame can clobber generator frame slots. This rules out ALL in-frame slot storage for data that must survive across yields.

**Layer 1 — missing `generator_rbp` in rax at L(3):** The γ epilogue must pass `generator_rbp` in rax to the L(3) landing (which saves it to `FRQ(act+8)` for β-resume). Without `mov r14,rbp` before rbp-restore, rax held the yield value at L(3) → garbage saved as generator_rbp → β-resume jumped through address 1 → SEGV.

**Layer 2 — continuation pointer `[generator_rbp+cont_off]` clobbered:** The caller's C-calls (write() → rt_call_arr → its callees) push stack frames into `[generator_rbp..entry_rsp)`, overwriting `[generator_rbp+32]` (the continuation slot). β-resume `jmp [rax+32]` → jumped to 0 → SEGV.

**Layer 3 — caller_rbp `[generator_rbp+kt-8]` and γ/ω wires clobbered:** Same mechanism clobbers the wire header slots.

**Fix:** Save all generator state that must survive yields in the heap-allocated pcall record (`g_pcall[]` array) and dedicated globals — both immune to caller stack expansion:
- `rt_gen_save_caller_rbp` / `rt_gen_get_caller_rbp` — `g_gen_pending_caller_rbp` global (set in prologue, read by γ/ω epilogues)
- `rt_gen_save_wires` / `rt_gen_get_{gamma,omega}_wire` — wire globals (set in prologue before any yield, read by epilogues using callee-saved r15 to survive the `rt_gen_get_caller_rbp` call)
- `rt_gen_save_cont` / `rt_gen_get_cont` — `g_gen_pending_cont` global (set by bb_suspend before each yield, read by β-resume via `rt_gen_get_cont`)
- yield value read from `FRQ(0/8)=[generator_rbp+0/8]` (written by bb_suspend before γ, not clobbered before epilogue reads it)
- generator_rbp saved in callee-saved `r14` to survive C calls in epilogue

### FR-4 THREE-LAYER ROOT CAUSE — layers 1+2 fixed, layer 3 active

**Layer 1 FIXED — Wrong β trigger**: The β arm now does `rt_gen_get_fb → generator_rbp; mov rbp,rax; mov rsp,rax; jmp [rax+cont_off]` where cont_off = zls_g_resume_by_name(callee) at emit time. The generator_rbp is saved to FRQ(act+8) at L(3) from the epilogue's rax (no stack-based call needed).

**Layer 2 FIXED — Wrong rdi:rsi in γ epilogue**: xa_flat_zframe_epilogue_γ now loads `rdi=[rbp+0]; rsi=[rbp+8]` (FRQ(0/8) = yield value stored by bb_suspend) instead of stale rax:rdx. Also adds `mov rax,rbp` before rbp-restore to pass generator_rbp to L(3) in rax. L(3) stores it to FRQ(act+8) call-free.

**Layer 3 ACTIVE — old_rbp header clobber**:
Generator's prologue stores caller_rbp at `[entry_rsp - 8]` = `[rbp + kt - 8]` (the stack header). Between the first yield and the β-resume, the caller executes write() → rt_call_arr. The `call rt_call_arr` pushes its return address to `[stmt_claim_rsp - 8]` = `[entry_rsp - 8]` = **the old_rbp slot**, permanently corrupting it. When β-resume fires proc_g_ω → `mov rbp, [rbp+kt-8]` reads garbage → SEGV.

**Evidence**: gen_simple.icn (single suspend) prints "1" then SEGVs. Root cause confirmed by tracing: write(1) call at stmt_claim_rsp pushes return addr to [entry_rsp-8] = old_rbp slot.

**Attempts and why they failed**:
- `sub rsp, 8` guard: rt_call_arr's return address still hits old_rbp at [entry_rsp-16]
- `sub rsp, 16` guard: same problem, just one level deeper
- Relocate old_rbp to [rbp+kt-32]: still only 32 bytes from entry_rsp; rt_call_arr frame (≥32 bytes on -O0) reaches it. Also broke fib (layout change propagated to non-generator γ epilogue).

**CORRECT FIX (not yet implemented)**:
Save caller_rbp while rsp is still in the FORTH stack zone (deep below entry_rsp), where C calls can't reach the header. Two-step in xa_flat_zframe_epilogue_γ:
1. BEFORE `lea rsp,[rbp+kt]` (while rsp is safely deep in FORTH stack): call `rt_gen_get_caller_rbp()` → rax; `mov r8, rax`
2. AFTER: `lea rsp,[rbp+kt]; mov rcx,[rbp+kt-24]; mov rbp,r8; jmp rcx`

Requires storing caller_rbp somewhere safe. Options:
- A) In the generator's prologue, call `rt_gen_save_caller_rbp(old_rbp)` which stores in a parallel array (like g_pcall_wires). The prologue runs at a safe rsp depth.
- B) Repurpose pcall.rname (pointer field, offset 8) — currently holds proc name, but could hold caller_rbp during the generator's active span. `rt_gen_save_caller_rbp(rbp)` at prologue, `rt_gen_get_caller_rbp()` in epilogue.
- C) Callee-saved register r15 (check if GVA uses it — see g_gva_active in emit.h). Prologue saves caller_rbp to r15; epilogue reads r15.

**Recommended option B** (pcall.rname repurpose): minimal change, no struct size change, the rname field isn't needed after proc registration.

### Implementation Plan for Layer 3

1. In `rt.c`: add `void rt_gen_save_caller_rbp(void *rbp)` → `g_pcall[top-1].rname = (const char *)rbp`
2. In `rt.c`: add `void *rt_gen_get_caller_rbp(void)` → `return (g_pcall_top > 0) ? (void *)g_pcall[g_pcall_top-1].rname : NULL`
3. In `rtx_icngen.S`: add RTX wrappers (delegate to C twins)
4. In `xa_flat.cpp`: revert old_rbp back to `[rbp+kt-8]` (restore pre-session layout for fib fix). Change epilogue γ/ω to call `rt_gen_get_caller_rbp` before `lea rsp,[rbp+kt]`. Use r8 as temporary.
5. In `xa_flat.cpp`: in generator prologue, after `mov rbp, rsp`, call `rt_gen_save_caller_rbp([rbp+kt-8])`.
6. Test: gen_simple.icn green, gen.icn green, fib green, full suite ≥ FR-3 watermark.

### Key WIP Commits
- `fba93a77` — FR-4 WIP (Layers 1+2 fixed, Layer 3 broken)
- `996bcfe9` — Merge of remote ZK-4/ZD-5b work with WIP

### FR-3 COMPLETE — criteria re-read and met
ICN-FR-3 criteria: f1 AND fib green both modes (recursion proves per-activation frames) · Error 18 extinct · SN4 held.
- **mode-3:** f0 ✅ f1 ✅ fib ✅. **mode-4 (--compile + as + gcc):** f0 ✅ f1 ✅ fib ✅. Error 18 gone from all three.
- SN4 proven by direct byte comparison at two bases, 318/318, md5 `47ef94a6a76f53503e0c9f49bb41b26c`.
- ICN-FR-3 rung box may be checked.

### FR-4 ROOT CAUSE — FULLY DIAGNOSED (do the fix next session)
**The `bcps_spine_gen_arm` template (`bb_call_proc_staged.cpp:534`) places NO resume landing word on the spine.**

The GENP-SPINE protocol comment says `"jmp qword [rsp] (the record's landing word sits AT the frontier by LIFO balance"`. That law was derived for the per-BB FORTH-spine model where each activation allocates 16B and `[entry_rsp]` holds a placed landing word. **The zframe prologue does `sub rsp,kt` (a whole-frame allocation), not per-BB cells.** After γ-retain (the generator's `xa_flat_zframe_epilogue_γ` runs `lea rsp,[rbp+kt]`), the restored rsp equals the generator's entry rsp. `[rsp]` at that point is whatever data was at the TOP of the CALLER's spine — NOT a code pointer. So `jmp [rsp]` at the β resume site jumps to a data word → SEGV.

**The fix (FR-4 work):** At the generator call site (β re-entry arm in `bcps_spine_gen_arm`), push an explicit resume landing word onto the caller's spine **before** the first call into the generator. The landing is a pointer to `L(3)_resume_entry` (the β path's actual re-entry point after `rt_gen_spine_resume_enter`). Shape:
```
; α call path — before rt_proc_call_open_det:
lea  rax, L(3_landing)      ; address of the resume entry
push rax                    ; push landing word AT [rsp] where γ-retain will leave it
; ... rt_proc_call_open_det ...
; γ-retain unwinds to entry_rsp, finds [rsp] = landing address; β restore: mov rsp,FRQ(act+8)+add 8 (pop the landing); jmp L(3_landing)
```
Alternatively — and cleaner for the zframe model — **skip `jmp [rsp]` entirely** and jump directly to L(3_landing) from the β arm, using `FRQ(act+8)` only to verify the saved-rsp invariant. The resume protocol for zframe does not need an RSP-based dispatch because rbp is pinned and depth-immune; the β re-entry can be a direct `jmp L(3)` with `mov rsp,FRQ(act+8)` still restoring the FORTH frontier before the re-entry.

**Gate: zframe graphs only.** `g_emit.zframe_graph` gates every change; the cells arm and SNOBOL4/Prolog paths are byte-identical.

### CROSS-TRACK: vslot override DELETED (from s5 notes)
The param/local vslot override in `ir_drive_slot_assign` is DELETED at `fcbb75b7`. Two prior cursor claims are FALSIFIED — do not re-implement them:
1. "ZLS vslots are FORTH-spine offsets" — FALSE. ZLS grants flat-frame offsets, correct under the pin.
2. "anonymous producers need rbp-relative `bb_slot_register` calls" — wrong premise, and the until2/rung09 garbage is a β re-entry defect (FR-4), not a base mismatch.

### HARNESS FACT
Feed `.stdin` files + `cd` to program dir (mirrors `test_icon_all_rungs.sh:89-97`). Never run two suites concurrently.

### 43 PROGRAMS TO ANCHOR PARITY (217 + 43 = 252)
In-scope residue by failure mode: SEGV(10) HANG(13) WRONG(10) EMPTY(10) — classified in s5 cursor, all generator/resume-shaped. FR-4's work queue is the SEGV list: rung03_suspend_{gen,gen_compose,gen_filter,return} rung09_loops_{repeat_counter,until_gen} rung36_jcon_{cxprimes,genqueen,level} rung37_subscript_genproc.

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
  (Duplicate FR-1/FR-2 spec bodies pruned s9 — merge debris from parallel doc edits; the [x] one-liners above are the record, full text in git ≤ `912a0644`.)

- [x] **ICN-FR-3 WIRE EXIT VIA THE FRAME HEADER.** ✅ COMPLETE s2+s5 — `76287768` (dc-stub caller-save + alignment, 188→195) + `fcbb75b7` (vslot-override DELETE, 206→217; the two falsified claims recorded in CROSS-TRACK note). Criteria met per s8 cursor: f1 AND fib green both modes (recursion proves per-activation frames) · Error 18 extinct on the quartet · SN4 318/318 byte-identical md5 `47ef94a6`.

- [x] **ICN-FR-4 GENERATORS ON-SPINE.** ✅ COMPLETE s8 — gen_simple.icn + gen.icn GREEN both modes m3+m4. Root cause: three-layer clobber bug (see LIVE CURSOR above). Fix: heap-allocated pcall globals for all generator-suspended state. rung03_suspend_gen* still FAIL (pre-existing: suspend-with-body `lbl_t0` re-loop path, not touched by this rung). rung36_gens floor not yet re-proven (FR-5 scope). SN4 held: corpus m3 PASS=287/FAIL=49, m4 PASS=273/FAIL=57 (pre-existing failures only).

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
