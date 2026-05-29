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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-8a DT_R SEGV CLOSED — canonical-5 mode-3 5/5, corpus 17→32 (+15), SEGV 2→0** (Opus 4.8, 2026-05-29, one4all `e9f09fdc`). Root cause (gdb-verified): flat BINARY slab entered via driver `call fn(NULL,0)` at rsp%16==8, `xa_flat_prologue` pushed nothing, so every internal `call *rax` to a runtime helper landed at rsp%16==8 → callee entry rsp%16==0, one slot off SysV ABI. Int helpers tolerated it; `fprintf("%g")` faulted on aligned `movaps %xmm0,-0x80(%rbp)`. Fix: `sub rsp,8` in `xa_flat.cpp` BINARY prologue before esi-dispatch (jne-β bin-site +4) + paired `add rsp,8` before each `ret` in BINARY epilogue. Plus `rt_pop_write_any_nl` DT_R → canonical `real_str` (not `%g`), and `bb_call.cpp` `arg_is_any` extended to BB_BINOP/BB_BINOP_GEN so DT_R-producing arith routes through type-aware any-write trailer. PASS: rung26_pow_pow_expr/assoc, rung37_augop_pow byte-identical. Gates: canonical-5 5/5 byte-identical + zero-SM, smoke_icon 5/5, smoke_prolog 5/5, broker 39/14, FACT 0. Zero regressions. Handoff `HANDOFF-2026-05-29-OPUS48-ICON-BB-IBB8A-DTR-SEGV.md`. **NEXT (IBB-8b):** relop in if-condition (~13) — FULLY DIAGNOSED. Cond relop arrives AG-pure (α=β=NULL, operands chain via γ to vstack, γ=ω→BB_IF router). Need (1) `flat_drive_if` + `case BB_IF` in walk_bb_flat; (2) AG-pure relop apply arm in `bb_binop.cpp` MEDIUM_BINARY mirroring `bb_binop_gen.cpp` lines 137-198 (`rt_acomp`/`rt_lcomp` + `rt_last_ok` + `test eax,eax; jz ω`); (3) string relops SLT..SNE → rt_lcomp. All runtime primitives exist. Then every-E-do-body (~4), write(BB_CALL), user-proc dispatch. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **WAM-CP-8 FIRST-ARG INDEXING ✅** (Opus 4.8, 2026-05-29, one4all `d9062238`). First-arg clause indexing — 137 lines, additive, three files (`src/lower/bb_exec.c`, `src/lower/lower_pl.c`, `src/include/BB.h`), zero deletions, NO emitter/template/FACT change (pure mode-2 interpreter logic; both FACT grep arms byte-identical 0/12). Each multi-clause `bb_pl_choice_state_t` carries `idx_key[]` (class-tagged `long` per clause, computed at lower time from clause head `c[0]`) + `idx_ok`. On BB_CHOICE fresh entry, a bound first arg (`g_pl_env[0]` deref) filters the clause set via exact key compare; EXACTLY-ONE matching clause whose body is `bb_body_single_solution` → dispatch with NO `pl_cp_push` (`g_pl_bfr` unchanged = the gate). Zero matches → fast-fail; >1 or non-single-solution candidate → unchanged CP-pushing scan. **Encoding (`BB.h`):** 3-bit class tag (bits 60-62) ATOM/INT/FLT/CMP so atom_id/int/float/packed-functor key spaces never collide; `PL_IDX_VAR`=0 (var-headed wildcard), `PL_IDX_NOKEY`=-1 (caller unbound). **Safety lesson (mirrors B1 gate 4):** first cut without the `bb_body_single_solution` gate regressed GATE-SWI 57→56 — `memberchk` committed deterministically to `member/2` clause 2 and stranded the recursive tail-call's backtrack; gating restored 57/57. A clause-selection commit ≠ body determinacy. **Proof** `SCRIP_IDX_TRACE=1` (default OFF): `[IDX] CP-ELIDED` fires for unique-key lookups (`color(grape,X)`→clause 2), NOT for multi-clause keys (`p(a,_)` enumerates 1/2/4 via normal scan), zero-candidate keys fast-fail. **Gates byte-identical:** GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-SWI 57/57, FACT 0/12, sibling smokes icon/raku 5/5/5, snobol4 13/13. Handoff `HANDOFF-2026-05-29-OPUS-PROLOG-BB-WAM-CP-8-FIRST-ARG-INDEXING.md`. **NEXT: Phase B2** — combine this CP-elision with the WAM-CP-6 B1 redirect sentinel (frame-reuse) instead of deterministic-commit-and-return, so a uniquely-indexed tail-position call (e.g. `count/1` once base/recursive clauses are first-arg distinguishable) flattens `count(1e6)` to O(1) C stack. Extend the gate (currently `bb_body_single_solution` excludes ALL BB_PL_CALL incl. the tail recursion B2 wants), reuse the B1 mechanism. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SPAN-VERIFIED / DEFER-NESTED-XDSAR ISOLATED** (Opus 4.8, 2026-05-29, analysis only — no commit, baseline `ce99d578` restored bit-for-bit, zero regression). Two findings: **(1)** the prior watermark NEXT "SBL-SPAN-2 BINARY arm (~10 tests)" is a **phantom** — `bb_pat_span.cpp` MEDIUM_BINARY already has full deque z/z_orig slots + working β backtracking (committed `4ce8c385`/`44766d91`). Verified native PASS: deep backtrack, two SPAN boxes, SPAN-in-ARBNO re-entrant, SPAN capture, and "071-minus-deref" (inline SPAN+POS+CAT+capture). SPAN is innocent; do not spend a session on it. **(2) Real blocker isolated: nested XDSAR (`*var`) child of XCAT fails only under `sm_run_native`.** `*WORD` → SM_PAT_REFNAME → XDSAR PATND. Top-level deref resolves early (`stmt_exec.c:335`) and works native; nested `POS(0) *WORD` → NOMATCH native / MATCH m2 with the SAME g_bb_mode=BROKERED builder + same rt_*/exec_stmt C — only sm_run_native vs sm_interp_run differs. A MODE3-DISPATCH-GAP instance narrowed to the smallest SNOBOL4 repro (one XDSAR child of XCAT). Unblocks the largest native-only cluster: 056/070-074(star_var)/108-115(fence-via-var)/140-141(eval-fn)/147. Gates held at baseline: G1 13/13, native 13/13, rung M2=19/M4=17, G3 184/280, native 223/280. Handoff `HANDOFF-2026-05-29-OPUS48-SBL-SPAN-VERIFIED-DEFER-NESTED-XDSAR.md`. **NEXT:** instrument `sm_run_native` over the 071 stream (instrs 5-11); dig order (1) SM_PAT_CAT arm (`sm_pat_combine.cpp`) vstack with XDSAR child, (2) SM_EXEC_STMT BINARY arm — confirm Σ/Σlen/Δ/Ω globals match the C-loop setup at entry, (3) `patnd_to_bb_graph` of XCAT-over-XDSAR. Ruled out / reverted: bb_pat_defer flat BINARY arm + lower_flat_invariant gate (both off this dynamic-build path). [Prior: **SBL-TAB-RTAB-FIX ✅** (`0ae0e7c2`) native +3; **SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`) native +25; plus SBL-BOMB/SPAN-ARB-ESCAPE, POS-PATCH-OFFSET, ARBNO child-gate, M3-NATIVE-4 flat-wire, EP-BINARY, bb_capture.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-1c LANDED ✅** (Opus 4.7, 2026-05-29, one4all `8d3a8cdf`). **Mode-3 native 19→25 PASS / 13→7 CRASH** (+6: rk_fileio38, rk_for_array{,_simple,_underscore}, rk_given18, rk_map_grep_sort24 all CRASH→PASS). `bb_iterate.cpp` Raku MEDIUM_BINARY arm was a 1-line stub returning a comment; now a full ~110-line raw-x86 mirror of the existing MEDIUM_TEXT arm. α zeroes `&pBB->counter` → fall into β-define which is also load-block entry; load calls `NV_GET_fn(pBB->sval)` via absolute `movabs+call` (no PLT in mode-3), unpacks `rax:rdx` (low32=v, hi32=slen; rdx=base ptr), strlen-fallback when slen=0 with stack-aligned push/sub/call/add/pop, bounds-check vs slen → `jge lω` (bin.sites rel32); scan advances rcx through `r10[rcx]` looking for SOH separator with self-patched rel32 forward jumps; send computes seg_len, `GC_malloc(seg_len+1)` + `rep movsb` copy + NUL-term, advances counter past separator, `rt_push_str(ptr,len)` + `jmp lγ` (bin.sites). bin.sites ascending per the 1b invariant: `{beta_off, fail_off+2, succ_off+1}` paired with `{lβ_p define, lω_p, lγ_p}`. Headers: `#include "descr.h"` + extern decls for `NV_GET_fn`/`rt_push_str`/`GC_malloc`/`strlen`. GOAL-RAKU-BB.md pruned — verbose completed-rung prose collapsed to one-liners. All gates HOLD: GATE-RK 23/33, GATE-RK4 26/33, smoke raku/prolog/icon 5/5/5, snobol4 13/13, FACT 0, build clean. Handoff `HANDOFF-2026-05-29-OPUS-RAKU-BB-M3-NOINTERP-1c-LANDED.md`. **NEXT:** **M3-RK-NOINTERP-1d** (`bb_upto.cpp` / `bb_suspend.cpp` / `bb_seq.cpp` for `rk_gather` — last Cluster-1 native test). NOT a mechanical mirror like 1c: the SEQ+SUSPEND+TAKE pipeline relies on `flat_drive_seq` populating `g_emit.xa_bb_emit_pair_*[]` before walking, but SM_BB_INVOKE's scratch flush in sm_bb_switch.cpp calls `walk_bb_node(gen, NULL)` not `walk_bb_flat` — so the pair arrays may be unpopulated when bb_seq's BINARY arm fires. Investigate either (a) initialize pair arrays from the wrapper before walk_bb_node, or (b) author a self-contained gather-driver shape in bb_seq BINARY that doesn't depend on pre-populated pairs. Current failure: `bb_emit_end: 1 unresolved forward reference(s): site=20 label='.Lbbinv0_β'` (same shape as the 1c starting failure). [Prior: **M3-RK-NOINTERP-1b ✅** (Opus 4.7, `48ca4e21`) SM_BB_INVOKE MEDIUM_BINARY scratch-buffer-flush w/ sink save/restore; **1a ✅** (Sonnet 4.6, `55d03444`) bb_to_by.cpp r12→rt_push_int; **3 ✅** (Sonnet, `c3476078`) SM_NAMED_CALL absolute-target patching closed Cluster 2.] |
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
