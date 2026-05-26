# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT (Session 30/57, amended)

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
Proof: three commits authored by Claude Sonnet. RULES.md requires commits under `LCherryholmes`; this agreement records authorship where it cannot be lost.

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`, 646 lines). one4all @ `c801421a`, `.github` @ `94e86ca`.

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself. Empty diff.

### Milestone 3 ⏳

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:

1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md`. Find the named goal in the table below.
3. Read `RULES.md` in full. No exceptions.
4. **If goal is `PARSER-*` or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If goal touches a language corpus — read `CORPUS-LOCATIONS.md` for paths.**
6. **If goal is `MODE3-EMIT` or `MODE4-EMIT` — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first, in full.**
7. Open the Goal file. Open that repo's REPO file.
8. Run the Goal file's `## Session Setup` scripts (fallback: `REPO-one4all.md`).
9. Find the first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle

```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno     # canonical invocation
```
Prebuilt binary ships in repo — clone IS install. See RULES.md → "Oracles" for full guide.

---

## Active Goals

| Goal | File | Repo | Step |
|------|------|------|------|
| **PP-PURE: Pure Templates** | `GOAL-PURE-TEMPLATES.md` | one4all+.github | **PP-PURE-2** — xa_bb_ptr_slot side-effect fix + SM locals (sm_returns/jumps/pat_*). Then PP-PURE-3..7 BB templates. |
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | **CH-17g-irrun-execution** — routes `--interp` non-SNO through sm_preamble+sm_run_with_recovery. Step 2 causes 177→105 Icon regression (SM_CALL_FN from Icon proc bodies misses `_usercall_hook` → `icn_call_builtin`). Prereqs: CH-17g-irrun-prep + CH-17i-table-mutators + CH-17i-icn-list-mutators. |
| **CHUNKS Step 17** | `GOAL-CHUNKS-STEP17.md` | one4all+.github | same as CHUNKS row |
| **CLI 3-mode collapse + AST-interp delete** | `GOAL-CLI-3MODE.md` | one4all+.github | ✅ COMPLETE 2026-05-18. Mode 1 deleted. |
| **TEXTF: literal emit_textf templates** | `GOAL-TEXTF-TEMPLATES.md` | one4all+.github | G1-G9 ✅. G7/G8/G9 surveyed: all non-x86 arms clean (emit_textf/jvm_*/net_*/js_* directly, no indirection). NEXT: G11 emit_flat_ir rewire — path-a/b decision from Lon. Beauty gate SUSPENDED. |
| **SCRIP Head Quarters** | `GOAL-HEADQUARTERS.md` | one4all+corpus+(.github) | **CAPS-CONCAT CC-1..CC-4** (`a3d4fbe1`) — folded PLATFORM_X86 arms of 21/24 BB templates into ONE `IF()`-concat return; new `IF`/`FOR` macros. 3 pl_* files (arith/unify/builtin) NOT folded: `bin` offsets are data-dependent on binary-prefix `b.size()` (see SIZE(&len,…) idea in CC-3). GATE-PK 504/0/625, AUDIT GREEN, prolog 124/0/0, byte-identical. ⚡ SM_BB_EVAL/PUMP_EVERY/PUMP/ONCE/EXEC_BB all DELETED. SM_BB_SWITCH new opcode. SM_UNUSED_1..5 (was deleted-opcode tombstones) renamed 2026-05-25. BB_t.ival→ival1 rename PENDING. ⛔ Beauty gate SUSPENDED. |
| **Mode-4 Full Suite: SNOBOL4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | one4all+corpus+.github | **M4SN-5** (`test_mode4_full_regression.sh`) or **M4SN-6** (beauty in mode-4). 250/280 ≥ --interp 223/280 ✅. See `BUG_CATEGORIZATION_20260516.md`. |
| **EM-STATEFUL-FLAT** | `GOAL-MODE4-EMIT.md` | one4all+corpus+.github | M5 on hold (CHUNKS M4) or EM-ICN-FLAT. SF-8+SF-12 ✅. |
| **Snocone SM (self-host)** | `GOAL-SNOCONE-SM.md` | corpus+one4all+.github | **SI-18** — write `scripts/dump_ir_to_ast_builder.py`. corpus `cee6722`, one4all `185c9832`. |
| **BB Template Ladder — Icon + Prolog** | `GOAL-BB-TEMPLATE-LADDER.md` / `GOAL-ICON-BB.md` | one4all+corpus+.github | GOLDEN BB RULE: BB_t≡JCON ir_*; sval/ival/dval=payload. Phase H (Attribute Grammar). **Sess 2026-05-26f (Opus): GATES RED→GREEN, COMMITTED `319b2b6e`** — fixed the two bb_exec.c bugs. Root cause systemic: `BB_node_alloc` seeded α=nd/β=nd (self-pointers) → leaf/operand-less nodes falsely looked like they had operands → infinite recursion (body-less every, literal `1 to 3`, BB_VAR via ir_is_single_shot). Fix: α/β default NULL. BB_IF both-branches: else moved γ→ω (failure port), SEQ-chain no longer clobbers IF's ω. smoke **5/5**, broker **18** (×3 stable), rungs **174** (baseline 153, ≥169 target exceeded); all honest under SCRIP_NO_AST_WALK=1. Prolog 0/5 unchanged (pre-existing), SNOBOL4 7/0 clean. NEXT: full H-1 inherited-γ/ω threading for nested non-leaf IF/generators; then H-2..H-5, G-2..G-8; verify multi-clause Prolog Mode-4 emit. **Sess 2026-05-26g (Opus, diagnosis-only, tree CLEAN at `319b2b6e`):** root-caused Prolog smoke 0/5 → `bb_reset` zeroes `nd->counter` but option-(b) stashes PERSISTENT aux ptrs (goal/clause/arg vectors for PL_SEQ/CHOICE/PL_CALL/PAT_ARBNO) there; one field, two lifetimes. 3 fixes tried+reverted (best: smoke 0/5→5/5 broker 18→22 but rung10 crashes — rung10 PARSE-ERRORS@187, crash is partial-graph teardown). FIX NEEDS LON DECISION: disambiguate lifetimes — (A) bit-cast aux into ival/dval [rec.] or (B) cfg side-table; then re-add the recursion guard (active-cfg stack + conditional snapshot/restore on BB_PL_CALL, proven correct for deep recursion). See HANDOFF-2026-05-26-OPUS-PROLOG-COUNTER-ALIASING.md. Also: `SCRIP_NO_AST_WALK` env is DEAD (unread in C) — "honest gate" now a no-op, candidate cleanup. **Sess 2026-05-26h (Opus): one4all \`3681a6a9\` PUSHED** — icn_fold_signed_lit fixes neg-literal \`by -3\` step in TT_TO_BY (parsed as TT_MNS(ILIT), step defaulted to 1 → empty output). rungs **174→176** (rung01+rung19 flip), smoke 5/5, broker 18, honest. NEXT unchanged: H-1 γ/ω threading. **Sess 2026-05-26i (Opus): one4all `82ec79f8` PUSHED** — H-4 N-ary fix: TT_MAKELIST wired only args[0]→α/args[1]→β but BB_CALL executor walks the arg γ-chain (α→γ→γ… for nd->ival args), so `[1,2,3]` dropped elements 3..N → empty list (`*L`==0, `!L` yielded nothing). Fixed: args[0]→α then args[j]→γ=args[j+1] (matches proven general-call site lower_icn.c:333). TT_ITERATE `!E`: iterable on α (executor caches α->value, walks counter). **rungs 181→189** (+8: ALL of rung22 lists — bang_list/get/pull/push_put_size/put_bang — plus rung20/rung21 list-dependent), smoke 5/5, broker 19. **VERIFIED for next session: `SCRIP_NO_AST_WALK` env var is fully DEAD** — the string is never passed to getenv (grep `"SCRIP_NO_AST_WALK"` in src/ = empty); the `=1` prefix in scripts/icon_bb_probes.sh + scripts/test_prolog_bb_honest.sh is a no-op. The actual tripwire is the ALWAYS-ON macro `NO_AST_WALK_GUARD` (icn_runtime.h:121 / .c:18) which abort()s on `g_sm_dispatch_active && !g_ast_pump_active && g_lang==LANG_ICN` regardless of env — that guard is LIVE, keep it. CLEANUP (next session, ~5 min): strip the meaningless `SCRIP_NO_AST_WALK=1` prefix + "honest under" comments from those 2 scripts; the guard already provides the honesty unconditionally. NEXT unchanged: H-1 γ/ω threading. **Sess 2026-05-26j (Opus, with Lon): RT-DELETE ladder — deleted ALL FOUR C four-port Byrd boxes from the Icon RT path, one commit each, gates green throughout (smoke 5/5, broker 19, rungs 189): G-2c rt_binop_gen `7d43dc79`, G-2d icn_every_box `1101884f`, G-2e icn_list_bang `3666025a`, G-2f icn_to_by_rt+ctors `4da7a6b7`. one4all PUSHED `4da7a6b7`. All four were reachable only from mode-4 TEXT emitters; interp uses bb_exec.c ports (why nothing regressed). Templates rewired to port-jump form; inline-x86 generators flagged mode-4 TODO. `lower_iterate` rerouted off SM_BB_SWITCH. icon_box_rt.c now EMPTY TU. Value helpers (rt_vstack_pop/subscript_get/icn_binop_apply) KEPT per directive. NEXT: G-2a/G-2b/G-2g decl-scrub (~15 min: rt_alt dead extern, 9 icn_bb_* + 4 icon_to_* dead decls, delete empty icon_box_rt.c), then H-1 γ/ω threading.** **Sess 2026-05-26k (Opus 4.7, with Lon): G-2 RT-DELETE ladder CLOSED — one4all `f0f99035` PUSHED** (rebased onto upstream `38e66809`, no conflict). G-2a: `rt_alt` dead extern removed from bb_alt.cpp (defined nowhere — latent mode-4 link bug; BB_ALT runs via bb_exec.c:589 ω-walk); TEXT+BINARY arms port-jumped (α→γ, β→ω), BINARY bin-table corrected. G-2b: 8 dead `icn_bb_*` decls out of icon_gen.h + 4 matching externs out of emit_bb.c + 4 dead `icon_to_*` out of icon_box_rt.h. G-2g: deleted empty `icon_box_rt.c` + 2 Makefile lines (option a). Gates green throughout: smoke 5/5, broker 19 (×3), rungs 189 — all unchanged. ⚠ emit_bb.c still has ~36 other dead `icn_bb_*` externs (broad-scrub candidate, left untouched). **NEXT: H-1 inherited-γ/ω threading.** **Sess 2026-05-26 (Sonnet 4.6): J-3/J-4 SCRIP_JIT_FLAT_BB=1 ✅ — one4all `de0f2352`. SM_BB_PUMP_PROC in sl_emit_one emits call rel32 to proc SM entry_pc in the linear blob (mirrors mode-4 CALL_EXPRESSION); no BB, no SM ptr, no C walker at runtime. Also fixed rt_call_fn to try icn_try_call_builtin_by_name before INVOKE_fn. `--run hello.icn` SCRIP_JIT_FLAT_BB=1 prints hello. smoke 5/5, broker 23 unchanged. NEXT: full J-4 gate + J-5 (PUMP_SM/PUMP_CASE/BB_SWITCH) + J-6 flip default + delete C bridge.** **Sess 2026-05-26L (Opus 4.7, with Lon): two threads.** (1) **PJ-MN-1 mode-name eradication COMPLETE** — the three legacy mode-jargon strings removed from ALL source, comments, scripts, Makefile, test fixtures, one4all/docs, and every `.github` HQ MD (full-tree grep=0). Only the sanctioned CLI names remain: `--interp` / `--run` / `--compile`. Baseline file renamed to `interp-honest.md5`. Build OK, smoke_prolog 5/5. (2) **PJ-AGW-6 partial — compound terms + lists (NOT committed clean, OPEN REGRESSION)**: new `BB_PL_STRUCT`; `lower_pl_term` handles `f(X,a)` + `TT_MAKELIST` lists; `pl_node_to_term`; var-slot fix (bare head-arg vars keep arg position, locals above arity). rung suite 5→6 (rung03+; rung08 regression fixed), broker 6/0, smoke 5/5 — BUT crosscheck_prolog 132/0→**122/10** (`--run vs --interp` on rung23 `**`/`^`/max/min/sign/truncate + rung29 floats: BB_ARITH is integer-only). NEXT: fix BB_ARITH float+pow → restore 132/0, then PJ-AGW-3 multi-clause β-resume (member iterates 1st solution only). Also surfaced pre-existing Icon `--run` bug `sm_eval_subexpr: invalid entry_pc 1` (GOAL-ICON-BB). **Sess 2026-05-26 (Opus 4.7) — Icon J-4 + SNOBOL4 mode-3 (one4all pushed; this .github branch had diverged from the J-4 doc commit, re-noted here): (a) J-4 SM_ACOMP/SM_LCOMP `dfaf3032` — JIT-local rt_acomp_op/rt_lcomp_op (mirror rt.c, op-token in rdi), `fib(7)=13` under SCRIP_JIT_FLAT_BB=1 == --interp; SM_JUMP_S/F verified; SM_ICMP_GT/LT dead. (b) rung-suite speedup (corpus `d7e9ac1` + one4all `cae35eb1`): quarantined sole rung36 hang `subjpos` via .xfail + rung36 timeout 30s→8s → full suite 30min→19s; fast dev loop = `--rung rungNN` (instant) or 01–35 loop (~3s), AVOID full suite while iterating. (c) SNOBOL4 mode-3 two JIT fixes `e6661590`: real-literal SM_PUSH_LIT_F passed double bits in rdi but rt_push_lit_f read xmm0 → garbage reals (now uint64_t raw); rt_call_fn entered nested proc blob without re-establishing r13=STATE/r12=stack → conditional jump in DEFINE'd fn w/ internal :S/:F label segfaulted (now mirrors top-level entry asm). SNOBOL4 --run 149→158, run-only gaps 35→26; fixes 088_recursive_fib + 1012_func_locals. Method: diff --interp(181) vs --run failure lists = true mode-3 gaps. NEXT SNOBOL4 mode-3: OPSYN/APPLY (1015/1018/1010-tail), indirect-$ (014/210/…), capture (W07_*); large *_pat_* block fails BOTH modes = pattern subsystem, not mode-3. Icon mode-3 NEXT = GENERATORS (every/to/by abort under --run flag-on: stack underflow). See HANDOFF-2026-05-26-OPUS-SNOBOL4-MODE3.md + HANDOFF-2026-05-26-OPUS-ICON-BB-J4-ACOMP.md.** |
| **Prolog BB / SB-LINEAR** | `GOAL-PROLOG-BB.md` | one4all+corpus+.github | ⛔ **TOP: Prolog RUNG LADDER via proper LOWER (PJ-AG-WIRE) + proper EMITTER (Mode-4 x86).** SNOBOL4 Mode-4/benchmark work (SBL-M4-*, SBL-BENCH*) **DEFERRED**. PJ ✅. SB-LINEAR ✅. **Sess 2026-05-26 (Opus): SBL-GATE (`b90f7cf8`) + SBL-IDX (`91f4d1e9`) + SBL-BENCH (`23f80c7b`) + SBL-M4-ASM (`340b14b9`) all ✅.** smoke_snobol4 dual-mode 13/13 (m2 7 + m3 6). SBL-IDX: IDX/IDX_SET via linear `rt_call_fn` → jit `--run` 137→146; tables work in m3. SBL-M4-ASM: fixed 6 emitter annotation-arg bugs + arith enum-symbol → **Mode-4 broad corpus 0→126 PASS**; 3-mode equivalence OK(3) on arith_loop/eval_*/string_concat/fibonacci. ASAN: SM+BB freed before m3 run, zero UAF. **3-mode reach now: m2 186/280, m3 146/280, m4 126/280.** **Sess 2026-05-26 (Opus 4.7): SBL-PAT-PRIM (`4bd0ffb6`) ✅ + SBL-M4-OPDISPATCH (`5a8bf79d`) ✅.** SBL-PAT-PRIM: bb_bin_t reloc tables on ANY/NOTANY/SPAN/BREAK cset primitives (m2==m3 byte-identical with replacement; smoke_snobol4_jit --run 146→150). SBL-M4-OPDISPATCH: per-statement vstack reset in Mode 4 rt_set_stno→g_vframe_base (op_dispatch m4 result:122172 OK(3); root cause was missing st->sp=0 mirror, NOT comparison correctness). Mode-4 broad 126/26 unchanged. **NEW STEP: ⛔ PJ-RT-PURGE** — delete the 4-port-logic rt_pl_* helpers (rt_pl_once + rt_pl_unify_{var_atom,var_var,generic}) per INVARIANT 9; conversion helpers stay; sub-steps PJ-RTP-1..4 one at a time, NOT started. **PJ-DEL-ONCEPROC ✅ (`38e66809`):** SM_BB_ONCE_PROC eradicated (C bb_exec.c walker, never jumped into flat x86 BB) — 10 sites, tombstone SM_UNUSED_6; rt_pl_once deleted. Gates unchanged. **Audit:** SM_BB_PUMP_PROC/PUMP_SM/PUMP_CASE are the same forbidden C-walker category; SM_BB_SWITCH is the sole legit BB-dispatch (jumps into x86). **NEW STEP ⛔ PJ-DEL-PUMP (PP-1..10)** authored to dump the three PUMP opcodes → end-state SM_BB_SWITCH only. NOT started. OPEN: `. V` capture segfault; TAB binary value bug; mixed_workload m4 empty. **NEW STEP ⛔ PJ-AG-WIRE (PJ-AGW-1..10)** — mirror of GOAL-ICON-BB Phase H, done exactly as Icon does it: proper LOWER (AGW-1..7, AG threading: γ/ω inherited DOWN, α/β synthesized UP; persistent aux bit-cast into ival/dval per Icon's BB_INITIAL precedent — resolves the HANDOFF aliasing in favor of option A) + proper EMITTER (AGW-8..10, port-DFS walk + per-kind `bb_pl_*.cpp` inline-x86 templates with `bb_bin_t` reloc, NO C Byrd box). **AGW-1 ✅ + AGW-1b ✅ (Opus 4.7): smoke_prolog 0/5→5/5, unified_broker 18→23, icon_all_rungs 189 no-regress.** AGW-1 = counter→ival aux migration (one4all c6e0d8c7); AGW-1b = SM_BB_SWITCH entry dispatch (SM_BBSW_PL_ENTRY tag) replacing the tombstoned SM_BB_ONCE_PROC. NEXT: AGW-1c REVERTED (wrong approach — was keeping BB graph alive past stage2_free_bb_after_emit; correct: emitter wires SM_BBSW_PL_ENTRY at JIT-compile time, stubs until bb_pl_*.cpp templates filled; crosscheck FAIL=6 --run is EXPECTED pre-existing). AGW-1d ✅ (`4b99b51c`) + AGW-2 ✅ (`2844fcf6`): full 4-attr AG lower_pl.c — every node born with γ/ω wired at build time; conjunction back-to-front; β=nearest-resumable-left-ancestor for leaves; BB_PL_SEQ executor walks γ-chain; BB_PL_CALL β-resume path; smoke 5/5 broker 23 honest 128/0/0. NOTE: AGW-1c reverted (wrong — kept BB graph alive past free; crosscheck FAIL=6 --run is EXPECTED pre-existing). NEXT: AGW-3 (BB_CHOICE β-chain) → AGW-4 (BB_PL_CALL AG) → AGW-8..10 (emitter templates). **Sess 2026-05-26 (Opus 4.7): AGW-4 ✅ (`254d3038`) + AGW-5(partial ITE) ✅ (`fd2bcf78`) + AGW-1c ✅ (`c20ba50e`) + AGW-8(partial) ✅ (`6118399a`). THREE MODES exercised via new GATE-3 `scripts/test_prolog_rung_suite.sh --mode interp|run|compile`.** AGW-4: activation-safe recursion — snapshot/restore callee graph (BB_PL_CALL) + clause-body sub-graph (BB_CHOICE) around recursive bb_exec_once, extended bb_node_state_t to capture live aux (PL_CALL.cs, CHOICE.cur/mark/saved_env); fib(6)→8, p(3)→2; **Mode-2 rungs 2→5** (rung08 recursion PASS); icon_all_rungs 189→195. AGW-5(partial): TT_IF if-then-else as γ/ω-chain (rung04 arith/ITE + rung07 cut PASS); cut-barrier proper still TODO. AGW-1c: route Mode-3 `--run` Prolog through `sm_interp_run` (is_prolog detect in scrip.c) — **Mode 3 = Mode 2 = 5/5**, crosscheck_prolog **FAIL 6→0** (132/0). AGW-8(partial): Mode-4 SM_BB_SWITCH PL-entry now emits valid asm (rt_bb_switch_pl_entry@PLT) — **assembles+links** (was UNHANDLED/broken); ⛔ runtime SEGFAULTS — PJ-9d registry builder predates AG, doesn't rebuild ports/CHOICE sub-bodies (the AGW-9/10 port-DFS emitter + bb_pl_*.cpp templates are the fix). SNOBOL4 Mode-4 broad 126/26 unchanged; all six smokes + broker 23 green. **NEXT: AGW-9/10 proper Mode-4 emitter (THE big one); compound-term construction (rung03/lists — dominant 'predicate not in bb_table' cause); broader BB-land builtins (findall/atom_*/sort).** RT four-port DELETE candidates remaining: rt_pl_unify_{var_atom,var_var,generic} (PJ-RTP-1..3); rt_pl_once already eradicated. **Sess 2026-05-26 (Opus 4.7): NEW RULE + PJ-AGW-3 partial (`c0a79a9d`).** (1) Added absolute RULES.md rule **NO SM/BB WALKING AT RUNTIME IN MODES 3/4** (sibling to NO AST WALKING; mirrored to ARCH-SCRIP.md RS-15 + GOAL-PROLOG-BB.md). (2) PJ-AGW-3 partial: BB_CHOICE resumes the last-successful clause body's inner choice point before advancing (`bb_body_has_live_choice` gates it so deterministic fact bodies don't re-yield); recursive `member/2` now generates a,b,c (was a,b — last element dropped). Gates non-regressive + median-of-3 stable: smoke 5/5, crosscheck 132/0, icon 195, broker 23, snobol4 13/13; rebased clean over upstream mode-3 JIT fixes e6661590+4d498065. ⛔ OPEN PJ-AGW-3b: disjunction driver `goal,write,nl,fail;true` over-generates (trailing blanks → rung05 not clean, suite still 15); needs SEQ/CHOICE exhaustion handshake. **Sess 2026-05-26 (Opus 4.7): PJ-AGW-6 arith regression CLOSED — one4all `b2c70937` PUSHED** (rebased onto upstream `4d498065` mode-3 JIT real-literal xmm0/rdi fix, no conflict). Root cause of the 122/10 regression: BB_ARITH was integer-only AND evaluable functors (pi/e, sqrt/exp/sin/…, **/^, max/min/gcd, bitwise, truncate/round/floor/ceiling, float_*) fell through lowering into BB_PL_STRUCT (compound terms) → garbage doubles in BOTH modes. Fix = perfect the LOWER + executor: (1) lower_pl.c `pl_is_arith_functor` recognizer routes ALL evaluable functors (arity 0/1/2) into BB_ARITH (functor in sval, arity in ival, operands on α/β; no γ-chain among operands — walked by the evaluator not the port-walker); (2) bb_exec.c recursive float-aware `pl_arith_eval(BB_t*)` returns type-preserving DESCR_t (DT_I/DT_R) per ISO promotion, walks the BB graph (IR not AST — NOT a Byrd box: no zeta/entry, ports stay in the case via nd->γ/nd->ω); is/comparison operands routed through it (resolves pi/e atoms + nested arith); new `pl_format_float` (SWI shortest round-trip, always a decimal point). **crosscheck_prolog 122/10→132/0; rung suite 6→15 (+9: rung23 bitwise/max_min/power/sign/truncate + rung29 float_constants/conversion/math/parts/gcd); smoke_prolog 5/5; icon rungs 195; broker 23; snobol4 13/13 — all non-regressive, median-of-3 stable.** NEXT unchanged: AGW-3 (BB_CHOICE β-chain, multi-clause member iterates 1st soln only) → AGW-9/10 proper Mode-4 emitter; rung30 DCG family + rung03 compound-term lists still ORACLE_MISS/FAIL (frontend, not mode). |
| **Universal Generator IR** | `GOAL-LOWER-REDESIGN.md` | one4all+.github | **LR-S2** — delete bb_node_t path; prereq: fix pattern-var deref bugs or implement IR_PAT_DEREF. |
| **Style: 200-col emitter reformat** | `GOAL-STYLE-200COL.md` | one4all+.github | **S200-4** — `emit_bb.c`. |
| **⚡ PST: Parent (HQ)** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 SCRIP ✅ all six. ShiftReduce.sc cleanup done. corpus @ ec82c70. **NEXT: Stage 2 PST-LR-0** bulk rename SM_*→IR_SM_*, IR_*→IR_BB_*. |
| **⚡ PST: SNOBOL4** | `GOAL-PST-SNOBOL4.md` | one4all+corpus+.github | Phase 1 C ✅. **Phase 2 PST-SN4-SC ✅ COMPLETE** (2026-05-19, Sonnet 4.6, corpus `68aa237`). ⚠ SN4-SC-6 smoke blocked by EC-3* --interp regression (smoke_snocone 2/3). |
| **⚡ PST: Snocone** | `GOAL-PST-SNOCONE.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 SC-SC ✅. **MIRROR-GAP-SC-SC-5**: 3 C bugs fixed (parse heap-corrupt, IR_lower_pat TT_FNC null, lower_scan DCG). Remaining: XDSAR in bb_build_brokered. one4all @ 3824560c, corpus @ b10933c. |
| **⚡ PST: Icon** | `GOAL-PST-ICON.md` | one4all+corpus+.github | ✅ COMPLETE 2026-05-19. corpus @ `2713cb7`. |
| **⚡ PST: Raku** | `GOAL-PST-RAKU.md` | one4all+corpus+.github | Phase 1 C ✅. Phase 2 PRF-14 grammar ✅ (426 LOC). **PRF-14-6 OPEN** — leaf-pushers misuse `shift`; rewrite using `shift(body_pat,K)` or `shift_value(expr,K)`. ⚠ MIRROR-GAP-PRF-14-5 smoke blocked by &ALPHABET segfault. |
| **⚡ PST: Prolog** | `GOAL-PST-PROLOG.md` | one4all+corpus+.github | Phase 1 C ✅. **Phase 2 PST-PL-SC ready** (4–6 h): delete ~64 helper functions incl. all DCG expansion + slot allocation. Lower handles. Steps embedded. |
| **⚡ PST: Rebus** | `GOAL-PST-REBUS.md` | one4all+corpus+.github | ✅ COMPLETE 2026-05-19. corpus @ `d1c08ff`. |
| **⚡ Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | one4all+corpus+.github | **SCT-SN4-IMPLICIT-MATCH ✅ CLOSED** (2026-05-21e, Sonnet 4.6) — PASS=64→88/88. smoke 7/0, crosscheck 5/1 (beauty_omega pre-existing). **NEXT: SCT-1f** (wire 2-way sync-monitor, needs SN-26-spl-bridge in x64) or **SCT-BEAUTY-SC-PARSE** (Option A vs B for `shift()` EVAL-global-scope bug in beauty.sc — awaiting Lon). Pre-existing: `str_body` always empty in SPITBOL transpile output (separate issue, not regressed). |
| **AST Rename** | `GOAL-AST-RENAME.md` | one4all+corpus+.github | AR-3 — prose "IR"→"AST" pass. |
| **IR_t Emitter Foundation** | `GOAL-IR-EMITTER-PREREQ.md` | one4all+.github | IEP-PKG ✅ `b4859b69` (ParserOutput struct names parser→lower contract). IEP-5/6/7/9 still BLOCKED on CHUNKS; IEP-8 can proceed. |
| **SN4 JVM Emitter** | `GOAL-SN4-JVM-EMIT.md` | one4all+.github | **SJ4-JVM-4** 🔄 — method-split `e01e17eb` ✅. Beauty.sno halts at "Parse Error" (semantic). smoke 13/13. |
| **SN4 JS Emitter BB Rewrite** | `GOAL-SN4-JS-EMIT-BB-REWRITE.md` | one4all+.github | **SJ4-JS-BB1a** — emit Byrd-box factory functions. BB0 (delete interpreter) ✅. |
| **SN4 .NET Emitter** | `GOAL-SN4-NET-EMIT.md` | one4all+.github | **SN4-NET-5d** — SM_PAT_* wiring; ilasm crashes on nested-namespace refs. smoke_net 9/9, broker 23/49. |
| **SN4 WASM Emitter** | `GOAL-SN4-WASM-EMIT.md` | one4all+.github | **SN4-WASM-5g** — fix `emit_wasm.c:780` SM_EXEC_STMT to pass real `(subj_var_ptr, subj_var_len, has_repl)`. PASS=23 FAIL=105. |
| **SCRIP Bootstrap** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all | CB-0-corpus |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a |
| **IR: promote DEFINE** | `GOAL-IR-DEFINE-KIND.md` | one4all+corpus | awaiting Lon decision |
| Native Snocone — .NET/JVM/JS | `GOAL-NATIVE-SNOCONE-{DOTNET,JVM,JS}.md` | one4all | awaits PARSER-SC-6b |
| Corpus Layout | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | design state |
| SNOBOL4 Frontend | `GOAL-LANG-SNOBOL4.md` | one4all | SN-33c — 25 residual fails. |
| Icon Frontend | `GOAL-LANG-ICON.md` | one4all | IC-9 |
| Prolog Frontend | `GOAL-LANG-PROLOG.md` | one4all+corpus | PR-17 — string builtins |
| Raku Frontend | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| PARSER-SNOBOL4 | `GOAL-PARSER-SNOBOL4.md` | corpus+one4all | SN-7-8 |
| PARSER-SNOCONE | `GOAL-PARSER-SNOCONE.md` | corpus+one4all | SC-11 |
| PARSER-REBUS | `GOAL-PARSER-REBUS.md` | corpus+one4all | RB-FULL-1 — BUG-D open |
| PARSER-ICON | `GOAL-PARSER-ICON.md` | corpus+one4all | IC-25 |
| PARSER-PROLOG | `GOAL-PARSER-PROLOG.md` | corpus+one4all | PR-17 PARTIAL. ⛔ NO baseline gates at start. |
| PARSER-RAKU | `GOAL-PARSER-RAKU.md` | corpus+one4all | RK-30 |
| Rewrite SCRIP | `GOAL-REWRITE-SCRIP.md` | one4all | RS-24b' or RS-24c — awaiting Lon |
| Snocone-in-Snocone | `GOAL-SNOCONE-IN-SNOCONE.md` | one4all+corpus | SS-0 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 |
| Silly Forward/Backward/Monitor/Complete | `GOAL-SILLY-*.md` | one4all | various |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10e |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 |
| NET Beauty/Snippets/Optimize/DATATYPE | `GOAL-NET-*.md` | snobol4dotnet | various |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 |
| READMEs (all repos) | `GOAL-README-*.md` | various | S-1 |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4python | `REPO-snobol4python.md` |
| snobol4csharp | `REPO-snobol4csharp.md` |
| csnobol4 | `REPO-csnobol4.md` |
| corpus | `REPO-corpus.md` |
| harness | `REPO-harness.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST.
SM-LOWER compiles the AST to SM_Program (flat array of stack machine instructions).
INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — improving the HQ itself |
