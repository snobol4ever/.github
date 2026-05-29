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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-6 full.icn LANDED — canonical-5 mode-3 5/5** (Sonnet 4.6, 2026-05-28, one4all `3aa200cd`). `BB_BINOP_GEN` flat-wired cross-product odometer in `bb_binop_gen.cpp` MEDIUM_BINARY + `flat_drive_binop_gen_tree` driver in `emit_bb.c`. Vstack-transience problem solved via per-node cache slots (`pBB->counter` = lhs cached int, `pBB->value.i` = rhs cached int) using new `rt_pop_store_i64`/`rt_push_stored_i64` helpers. Template emits store→restore→apply slab keyed off five EMIT_PAIR entries. `every write((1 to 2)*(3 to 4))` = `3\n4\n6\n8\n` byte-identical m2 vs m3. `every write(5>((1 to 2)*(3 to 4)))` = `3\n4\n` byte-identical. FACT=0. Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 39/14. **Mode-3 corpus sweep result (249 testable programs): 20 PASS / 23 FAIL / 206 ABORT. Dominant blocker: bb_call unsupported shape (181 cases).** Handoff `HANDOFF-2026-05-28-SONNET-ICON-BB-IBB6-FULL-ICN.md`. **NEXT:** Add `rt_pop_write_any_nl` + `write(BB_VAR)` support (~30 cases): (1) `rt_pop_write_any_nl` in rt.c/rt.h; (2) add `BB_VAR` to `is_write_intexpr` in bb_call.cpp; (3) flat-wire `BB_VAR` arg0 via `rt_nv_get` call + any-write trailer; (4) case BB_VAR in walk_bb_flat. After that: relop in if-condition context (16 cases), every-with-do-body (4 cases). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **WAM-CP-6 Step B Phase B1 FRAME-REUSE ✅** (Opus 4.8, 2026-05-29, one4all this commit). Actual LCO frame-reuse for tail-position deterministic singleton-callee `BB_PL_CALL` — 94 lines, `src/lower/bb_exec.c` ONLY, no enum/emitter/lowering/FACT change. Driver-recognized redirect sentinel (two file-scope globals `g_pl_tail_redirect_cfg`/`_entry`), NOT a new op. Fresh path binds args into fresh callee env (unify records on trail BEFORE redirect), sets `g_pl_env`, `bb_reset`, trips sentinel, `return NULL` (no PlCallSt, no resume). Both driver loops (`bb_exec_once`+`bb_exec_resume`) check sentinel after `bb_exec_node` and reuse their own C frame → flat stack across deep singleton tail recursion. **Phase-B1 gate (all 4 static at fresh-call entry):** (1) `γ==NULL` tail-pos; (2) `g_pl_bfr==NULL` no live CP; (3) `entry->t!=BB_CHOICE` singleton callee; (4) `bb_body_cp_free_except_tail` (new helper). **Two regressions found+fixed:** gates (2) and (4) were each required — first cut (only 1+3) broke rung11 findall_filter (`[2,4]`→`[2]`, body-CP stranded findall backtrack → fixed by gate 4) and SWI memberchk (`f(X,a),[f(x,b),f(y,a)]` lost backtrack with member's multi-clause CP live → fixed by gate 2). **Proof:** `SCRIP_LCO_TRACE=2` logs `[LCO] ACTED` per redirect; `greet:-hello. hello:-world. world:-write(ok),nl.` shows hello+world both redirect, one C frame, prints `ok`. **All gates BYTE-IDENTICAL** to `860d1163`: GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57, FACT 0, smokes icon/raku 5/5/5, snobol4 13/13. Handoff `HANDOFF-2026-05-29-OPUS-PROLOG-BB-WAM-CP-6-STEP-B-FRAME-REUSE.md`. **NEXT: Phase B2 pairs with WAM-CP-8 first-arg indexing** — `count(N)` benchmark still fails gates (2)+(3) (multi-clause + live clause-selection CP); WAM-CP-8 must elide that CP and dispatch to one clause before B2 flattens `count(1e6)` to O(1) C stack. The B1 mechanism is what B2 reuses — extend the gate, not the mechanism. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-TAB-RTAB-FIX ✅** (Opus 4.7, 2026-05-29, one4all this commit). Three-bug fix in `bb_pat_tab.cpp` BINARY arm. (1) TAB sites `{9, 23, 28, 29}` had the same off-by-one as bb_pat_pos pre-`61ae501e` — the `0F 8F jg` opcode byte was being overwritten by rel32 → SIGSEGV on any TAB(N). (2) RTAB sites `{25, 32, 37, 38}` same off-by-one. (3) RTAB BINARY arm had a SEMANTIC bug at offset 30: success-path writeback was `89 C1` (mov ecx, eax) — a no-op that overwrote ecx (Σlen-N) with eax (Δ), never writing the new Δ. Correct instruction: `41 89 0A` (mov [r10], ecx) per TEXT arm. Fix: TAB sites `{10, 23, 27, 28}`; RTAB writeback corrected (+1 byte); RTAB sites `{26, 34, 38, 39}` accounting for the shift. 36-line documentation comment recording the layout in-file. **Gates: G1=13/13 default+native, G2=39, G3=184/280, G4=252/280, native=223/280 (+3), rungs M2=19/M4=17, Prolog/Raku/Icon smokes 5/5/5, FACT=0, audit GATE OK. Zero regressions.** Newly-passing native: 046_pat_tab, 047_pat_rtab, W06_tab. Modest +3 because TAB/RTAB used in few corpus tests (compared to RPOS-FLAG-FIX's +25 same-day). GATE-3/4 unchanged because TEXT arm was already correct. Handoff `HANDOFF-2026-05-29-OPUS-SBL-TAB-RTAB-FIX.md`. **NEXT:** (a) SBL-SPAN-2 BINARY arm — largest remaining cluster (~10 tests), use `std::deque<int>` slot pattern from `bb_capture.cpp`; TWO persistent int slots (z, z_orig); β yields successively shorter spans using ABSOLUTE z_orig (not [r10]-relative — sibling concat boxes mutate [r10] between α and β re-entry). (b) SBL-ARBNO-3 BINARY arm (~8 tests). (c) Audit remaining bb_pat_* sites against the now-thrice-confirmed convention (rel32 starts at byte AFTER opcode bytes). [Prior: **SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`) rpos = sval==\"r\" not ival != 0 in BOTH BINARY and TEXT arms — affected mode-3 AND mode-4, native +25, mode-4 +6, mode-2 +1, rung M4 +2; **SBL-BOMB-STUB-ESCAPE-FIX ✅** (`c6abd06c`) prophylactic `\\\\x`→`\\x` cleanup; **SBL-SPAN-ARB-ESCAPE-FIX ✅** (`44766d91`) bb_pat_span/arb double-backslash bug; **SBL-POS-PATCH-OFFSET ✅** (`61ae501e`) bb_pat_pos sites realigned; **ARBNO MEDIUM_BINARY child-gate fix ✅** (`4471b80d`); **M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED ✅** (`e9a9d7f3`).] |
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
