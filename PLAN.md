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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **UNCOLLECTABLE prophylactic SWEEP COMPLETE ✅** (Opus 4.7, 2026-05-29, one4all `5bf88205`). 7 more `GC_MALLOC → GC_MALLOC_UNCOLLECTABLE` swaps in `src/lower/lower_pl.c` at the four state-struct sites flagged in the predecessor handoff: line 77 `bb_pl_ite_state_t`, line 148+150 `bb_pl_seq_state_t`+`zs->goals` (`lower_pl_new_Conj`), line 527 `bb_pl_catch_state_t`, line 553 `bb_pl_findall_state_t`, line 648+650 `bb_pl_seq_state_t`+`zs->goals` (`lower_pl_clause_body`). Same hazard pattern as `98c2f974`: sidecar reachable only through `bb->ival` (int64_t in libc-calloc'd `BB_t`), libgc cannot trace through libc memory, sweeps under deep GC → recycles pages → SIGSEGV on read-back. Latent today because pj_rev path didn't enter ite/catch/findall/seq sites, but any recursive predicate using if-then-else, catch/3, findall/3, or a multi-goal body at depth would have triggered identical `bb=0xN`/`bbg=0xN` corruption. The hazard class in `lower_pl.c` is now closed. Working arrays at lines 126-128 (`gα`/`gβ`/`gnodes`) intentionally not swapped — stack-scoped, copied into UNCOLLECTABLE `zs->goals[]`, then unreachable. **All gates BYTE-IDENTICAL to `98c2f974` baseline:** GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI m2 57/57 (100%), GATE-SWI m3 57/57 (100%), FACT 0, smokes icon/raku 5/5/5, snobol4 13/13. ZERO regressions. Handoff `HANDOFF-2026-05-29-OPUS-PROLOG-BB-UNCOLLECTABLE-PROPHYLACTIC.md`. **NEXT (3 long-arc options):** (a) **WAM-CP-6 LCO proper** — refactor `bb_exec_once` from recursive C-tail-calls to explicit trampoline; UNCOLLECTABLE now protects sidecars but stack still grows; unlocks `count/1` 1e6 benchmark. SWIPL study `doc/SWIPL-STUDY-2026-05-28-OPUS.md` CP-stack idea #4 is the compass. Multi-session. (b) **WAM-CP-13 mode-4 corpus** — push from 4/4 minimal to ~50-60/107 by emitting per-builtin mode-4 arms (mechanical, broad). (c) **PL-RT-ASSERTZ** — `assertz/asserta/retract` in `pl_runtime.c` clause-table; independent of CP. Recommend (a). [Prior: **bb=0x3 corruption FIXED** (`98c2f974`) — 8 swaps at call/choice sites unblocked `test_string.pl` from SIGSEGV (8 lines lost) to `13/8/0` completion; GATE-SWI 55/57 (96%) → 57/57 (100%) after honest `test_string.ref` re-baseline `EMPTY/EMPTY → FAIL/PASS`. **SWI-NEXT step 2 + WAM-CP-6 prelude** (`52f80293`) once/1 intercept + 80 KB stack-redux in bb_exec_node surfaced this bug class.] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-BOMB-STUB-ESCAPE-FIX ✅** (Opus 4.7, 2026-05-28, one4all this commit `c6abd06c`). Prophylactic cleanup of the 5 remaining `\\x` BOMB-stub sites flagged in the predecessor SBL-SPAN-ARB-ESCAPE-FIX (`44766d91`). Each placeholder fallthrough (`bytes(1,"\\xE9")+u32le(0)+…` 2-jmp or 3-jmp pattern) was emitting `5C 78 ?? ?? ?? ?? 5C 78 …` instead of `E9 ?? ?? ?? ?? E9 …`. Sites: bb_arbno.cpp:23 (no-child fallthrough), bb_pl_alt.cpp:23 (n<=0), bb_pl_call.cpp:41 (degenerate-call), bb_pl_choice.cpp:42 (n<=0), bb_to.cpp:65 (dynamic-operand passthrough TODO). One-line str_replace each. bb_binop_gen.cpp:120 sibling was already cleaned by IBB-6 (Sonnet 4.6, `3aa200cd`) — that commit replaced the placeholder with a full odometer slab. **Gates: G1=13/13 default+native, G2=39, G3=178/280, G4=251/280 (+1 marginal — likely the bb_to dynamic-passthrough corrupt stub now emits clean fallthrough for some default-mode pattern), native=195/280, rungs M2=19/M4=15, all five language smokes green, FACT=0, audit GATE OK. ZERO regressions.** `grep -rE 'bytes\([0-9]+, ?"\\\\x' src/emitter/` now returns empty across all template directories — the double-backslash bug class is closed. Latent landmine eliminated: if any of these paths ever became reachable, they would have SIGSEGV the same way SPAN/ARB did. **NEXT:** (a) enable combinator flat-wire in mode-3 (patnd_to_bb_tree path live in stmt_exec.c, rungs 050/055 verified passing — broader corpus probably needs `patnd_tree_eligible` extension for nested combinators); (b) extend `patnd_tree_eligible` for XARBN inside CAT (rungs 052/054 still empty native — POS+SPAN+ARB segfaults gone, but anchored ARBNO-in-CAT still doesn't match). [Prior: **SBL-SPAN-ARB-ESCAPE-FIX ✅** (`44766d91`) bb_pat_span/arb `\\x`→`\x` (native +8, default +4, mode-4 +3); **SBL-POS-PATCH-OFFSET ✅** (`61ae501e`) bb_pat_pos sites realigned to rel32-start convention; **ARBNO MEDIUM_BINARY child-gate fix ✅** (`4471b80d`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED**.] |
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
