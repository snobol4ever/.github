# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`).

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself.

### Milestone 3 ⏳
All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md`. Find goal in table below.
3. Read `RULES.md` in full.
4. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
6. **If MODE3-EMIT or MODE4-EMIT — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.**
7. Open Goal file. Open that repo's REPO file.
8. Run Goal file's `## Session Setup` scripts.
9. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-8b STRING RELOPS IN IF-COND ✅ (partial) — corpus same-sweep 22→28 (+6), SEGV 0** (Opus 4.8, 2026-05-29, one4all `0e926c16`). Three pieces: (1) `bb_binop.cpp` AG-pure relop/strrel apply arm — `rt_acomp`(numeric)/`rt_lcomp`(string) + unconditional `jmp γ`; both ports of an AG-pure relop reach the BB_IF router, per the mode-2 oracle. (2) NEW `bb_if.cpp` router — `rt_pop_void; rt_last_ok; test eax,eax; jz ω(else); jmp γ(then)`; registered in emit_core dispatch + bb_templates.h + Makefile. (3) `flat_drive_seq` rewritten from γ-only linear walker into a **node-keyed CFG emitter** (BFS follows γ always, ω ONLY for BB_IF so operand children aren't double-emitted; non-IF nodes keep outer lbl_ω as baseline — resolving ω generally SEGV'd by mis-wiring operands that tree-shape drivers walk inline; one stable arena label per node, emitted once). AG-pure BB_BINOP routes to FILL; added `case BB_IF`. BB_SEQ is Icon-exclusive (only lower_icn.c builds it) → zero cross-family impact. **The original IBB-8 `flat_drive_if`/`pBB->cond` plan was unworkable (BB_IF has no back-pointer to the cond chain; PEERS RULE forbids adding one) and was superseded by the CFG-seq approach.** Newly passing: rung12_strrelop_size_{slt,sge,sne}, rung37_strrelop_hello, rung07_control_seq, canonical if_expr crosscheck. Gates: FACT 0, smoke icon 5/5, prolog 5/5, broker 39/14, zero-SM holds, no regressions. Handoff `HANDOFF-2026-05-29-OPUS48-ICON-BB-IBB8B-STRING-RELOPS.md`. **NEXT (IBB-8c):** numeric/real relops blocked on **BB_LIT_F vstack-push** — `bb_lit_scalar.cpp` BB_LIT_F path is a pass-through stub that never pushes the real (mirror the BB_LIT_I arm with a DT_R DESCR_t push); unblocks rung18_real_relop_*. Then block-body if (rung35_block_body_if_*) nested-block flattening, every-E-do-body (~4), write(BB_CALL), user-proc dispatch. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **NO-MODE-FALLBACK — a mode runs FULLY or ABORTS** (Opus 4.8, 2026-05-29, one4all `94bbd9eb`). Per Lon directive, removed ALL cross-mode fallback paths. `scrip.c` mode_run: dropped the `SCRIP_M3_NATIVE` env-gate AND the native→`sm_interp_run` fallback — `--run` (mode-3, non-Icon) now calls `sm_run_native` unconditionally and ABORTS on failure (no interpreter masquerade). `sm_run_native` gains `g_sm_native_unsupported` flag (emit_core.h/.c): an unimplemented MEDIUM_BINARY template arm → return -1 → abort (no bogus success). `SM_BB_PL_INVOKE` MEDIUM_BINARY stub sets the flag (FACT unchanged — a C set, not emitted bytes). Dead `has_non_sno`+default `else` branches (unreachable; mode_run is default) had stray `sm_interp_run` calls → replaced with LOUD `abort()` (`94bbd9eb`): abort, never fail-normally, since a clean rc1 is ambiguous with a legit error. Gate scripts: mode-3 = plain `--run` (now always native); crosscheck counts abort (rc≥128) as NATIVE-ABORT, never a pass. **Honest mode-3: 0/132 native (all NATIVE-ABORT)** — Prolog native program entry unimplemented (`SM_BB_PL_INVOKE` MEDIUM_BINARY stub; real entry only in MEDIUM_TEXT). SNOBOL4/Icon `--run` still pass (genuinely native). **Mode-2 authoritative + unchanged:** GATE-1 5/5, GATE-3 m2 104/107, GATE-SWI 57/57; siblings 5/5/5/13. FACT 0/12. **NEXT (headline, multi-session): M3-PL-NOINTERP** — implement native MEDIUM_BINARY Prolog entry (port MEDIUM_TEXT env-push+walk_bb_flat to raw bytes + populate BB_PL_* MEDIUM_BINARY arms; mirrors Raku M3-RK-NOINTERP-1a..1d) so `--run` runs instead of aborts. Prior stands: B3 sumto(1e7) O(1) heap (`0019cc7b`), print/1 mode-4 corpus 55/107 (`2fae45ec`). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SPAN-VERIFIED / DEFER-NESTED-XDSAR ISOLATED** (Opus 4.8, 2026-05-29, analysis only — no commit, baseline `ce99d578` restored bit-for-bit, zero regression). Two findings: **(1)** the prior watermark NEXT "SBL-SPAN-2 BINARY arm (~10 tests)" is a **phantom** — `bb_pat_span.cpp` MEDIUM_BINARY already has full deque z/z_orig slots + working β backtracking (committed `4ce8c385`/`44766d91`). Verified native PASS: deep backtrack, two SPAN boxes, SPAN-in-ARBNO re-entrant, SPAN capture, and "071-minus-deref" (inline SPAN+POS+CAT+capture). SPAN is innocent; do not spend a session on it. **(2) Real blocker isolated: nested XDSAR (`*var`) child of XCAT fails only under `sm_run_native`.** `*WORD` → SM_PAT_REFNAME → XDSAR PATND. Top-level deref resolves early (`stmt_exec.c:335`) and works native; nested `POS(0) *WORD` → NOMATCH native / MATCH m2 with the SAME g_bb_mode=BROKERED builder + same rt_*/exec_stmt C — only sm_run_native vs sm_interp_run differs. A MODE3-DISPATCH-GAP instance narrowed to the smallest SNOBOL4 repro (one XDSAR child of XCAT). Unblocks the largest native-only cluster: 056/070-074(star_var)/108-115(fence-via-var)/140-141(eval-fn)/147. Gates held at baseline: G1 13/13, native 13/13, rung M2=19/M4=17, G3 184/280, native 223/280. Handoff `HANDOFF-2026-05-29-OPUS48-SBL-SPAN-VERIFIED-DEFER-NESTED-XDSAR.md`. **ROOT CAUSE FOUND (probe-confirmed):** m2 matches via pre-lowered BB graph (`sm_interp.c:582` bb_exec_pat, mode-2-only walker); m3 native must build the dynamic PATND and calls `exec_stmt`→ok=0. The translator-eligibility gate (`stmt_exec.c:301 patnd_needs_xlate` BROKERED / `:271 patnd_tree_eligible` LIVE) refuses XDSAR-bearing trees → falls to the legacy `(BB_t*)pp` cast that misreads opcodes (`:237`). `build_patnd:468` translates XDSAR→BB_PAT_DEFER correctly; the gate just won't invoke it. **TWO-PART FIX (both required):** (1) add `patnd_contains_defer` into `patnd_needs_xlate` + make XDSAR tree-eligible (`patnd_tree_eligible`/`patnd_is_simple_atom`); (2) implement the EMPTY `bb_pat_defer.cpp` MEDIUM_BINARY arm — brokered ABI (rdi=ζ,esi=port,ret) for bb_build_brokered, flat ABI (r10,jmp) for bb_build_flat; logic = call rt_defer_match(varname,ival,Δ);test;js ω;writeback;γ (mirror TEXT arm). MUST NOT regress 146/147/152/1011/1013/1017 (legacy-cast-compensated). Target native 223→~235+. [Prior: **SBL-TAB-RTAB-FIX ✅** (`0ae0e7c2`) native +3; **SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`) native +25; plus SBL-BOMB/SPAN-ARB-ESCAPE, POS-PATCH-OFFSET, ARBNO child-gate, M3-NATIVE-4 flat-wire, EP-BINARY, bb_capture.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-1d LANDED ✅** (Opus 4.8, 2026-05-29, one4all `a894af4a`). **Mode-3 native 25→26 PASS / 7→6 CRASH** — `rk_gather` CRASH→PASS, closing the last Cluster-1 native test. The gather body BB graph is `BB_SEQ(n=4) → SUSPEND·SUSPEND·SUSPEND·FAIL` (NOT the bb_upto path the prior handoff guessed). THREE coordinated fixes. **(1) `bb_seq.cpp`** new raw-x86 gather-driver `bb_seq_gather_binary`: the MEDIUM_BINARY arm only walked the `xa_bb_emit_pair_*[]` passthrough, UNPOPULATED on the SM_BB_INVOKE → `walk_bb_node` path (no `flat_drive_seq` ran), leaving outer β (`.Lbbinv%d_β`) undefined → `bb_emit_end` abort. New driver mirrors the MEDIUM_TEXT gather-driver in raw bytes: α `jmp s0_α`; define outer β = `movabs rax,&resume_slot; mov rax,[rax]; jmp rax`; per child define Lα[k], `walk_bb_node(child,NULL)`, define Lγ[k] fixup (`movabs rax,&resume_slot; lea rcx,[rip+nxt]; mov [rax],rcx; jmp outer_γ`); done → outer_ω. resume_slot = malloc'd quad (scratch page has no `.data`); intermediate labels malloc'd so pointers survive into the wrapper's `bb_emit_end` (runs after bb_seq returns); rip-relative `lea` via standard `bb_emit_patch_rel32` (site+4=rip). **(2) `bb_suspend.cpp`** MEDIUM_BINARY now pushes via `rt_push_int` (movabs+call) not raw `mov [r12]` — `sm_run_native` doesn't init r12 as a value-stack pointer (the SM value stack is the `g_vstack` C global), so the old r12 stores segfaulted; same fix bb_to_by took in 1a; bin sites reordered ascending per 1b. **(3) `lower.c` `lower_every`** new branch for `for gather{} -> $v` (`TT_EVERY(TT_ITERATE(v, TT_FNC(__gather_N)))`): the generic scaffold routed through `lower_iterate` which emitted `SM_BB_INVOKE; STORE_VAR v` BEFORE the scaffold's `JUMP_F` → loop var stored from an empty value-stack on the exhaustion pull → underflow; new branch mirrors the iterate-array branches (JUMP_F gates the store). Mode-4 rk_gather also PASSes (already in the 26). Mode-2 rk_gather still FAILs (pre-existing, verified by stash — `bb_exec.c` BB_SEQ doesn't drive the multi-yield loop; separate path). Gates: GATE-RK 23/33 HOLD, GATE-RK4 26/33 HOLD, GATE-RK3 26/1/6, smoke raku/prolog/icon 5/5/5, snobol4 13/13, FACT 0, build clean. FACT/PEERS clean; ports α/β/γ/ω; no BB_t fields added. Handoff `HANDOFF-2026-05-29-OPUS-RAKU-BB-M3-NOINTERP-1d-LANDED.md`. **NEXT:** Cluster-1 native COMPLETE (26/33). Remaining 7 = regex cluster (6: rk_re32/33/34/35/37, rk_regex23 — DEFERRED to GOAL-RAKU-PAT-BB) + rk_junctions (1 — BLOCKED on Lon Q9-Q12). Substantive next: RK-BB-4 junctions (after Q9-Q12), or the mode-2 gather gap in bb_exec.c. [Prior: **1c ✅** (`8d3a8cdf`) bb_iterate.cpp Raku MEDIUM_BINARY arm, mode-3 19→25; **1b ✅** (`48ca4e21`) SM_BB_INVOKE MEDIUM_BINARY scratch-buffer-flush; **1a ✅** (`55d03444`) bb_to_by.cpp r12→rt_push_int; **3 ✅** (`c3476078`) SM_NAMED_CALL absolute-target patching closed Cluster 2.] |
| **PP-PURE** | `GOAL-PURE-TEMPLATES.md` | PP-PURE-2 — xa_bb_ptr_slot side-effect fix + SM locals. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **Mode-4 SN4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | M4SN-5 or M4SN-6. 250/280 ✅. |
| **PST Parent** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | Stage 2 PST-LR-0 bulk rename. |
| **PST SNOBOL4** | `GOAL-PST-SNOBOL4.md` | SN4-SC-6 smoke blocked by EC-3* regression. |
| **PST Snocone** | `GOAL-PST-SNOCONE.md` | MIRROR-GAP-SC-SC-5: XDSAR in bb_build_brokered. |
| **PST Raku** | `GOAL-PST-RAKU.md` | PRF-14-6 OPEN — leaf-pushers misuse shift. |
| **SN4 JVM** | `GOAL-SN4-JVM-EMIT.md` | SJ4-JVM-4 done. Beauty.sno halts at Parse Error. smoke 13/13. |
| **SN4 .NET** | `GOAL-SN4-NET-EMIT.md` | SN4-NET-5d — SM_PAT_* wiring. smoke_net 9/9, broker 23/49. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed; IEP-5/6/7/9 blocked on CHUNKS. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2 — delete bb_node_t path. |
| **Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | SCT-1f or SCT-BEAUTY-SC-PARSE. |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| corpus | `REPO-corpus.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles AST to SM_Program. INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
