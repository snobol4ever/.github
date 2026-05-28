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
| **ICON-BB** | `GOAL-ICON-BB.md` | **CASE-EXPR ✅** (Opus 4.7, 2026-05-28, `d1031b0c`): Icon `TT_CASE` was misrouted through Snocone-shaped branches in `lower_case` — legacy branch interpreted trailing TT_QLIT default body as an end-label name (silently dropped); modern-Snocone branch did `lower_expr(body); SM_VOID_POP` per arm then final `SM_PUSH_NULL` (destroyed case-as-expression value). Fix: gate both branches on `g_lang == LANG_SNO`. Icon now falls through to the `!is_raku` branch (line ~1419) which already correctly handles `has_def = (t->n - 1) % 2` and preserves arm values. Recovered all 5 rung33 cases (`case_int`, `case_str`, `case_arith`, `case_no_default`, `case_in_proc`). **Earlier this session: RENAME** (`b84153c3`) — pure rename in `src/lower/`: `BB_graph_t *cfg` → `*bbg`, `BB_t *nd` → `*bb`. **ALT-EXPR** (`8b0ad2ba`) — TT_ALTERNATE in `lower_expr` builds CFG and emits SM_BB_INVOKE (was emitting SM_PUSH_NULL); recovered 4 rungs. **MAIN-BOOT** (`80d0d5ee`) — recovered Icon from 0/5 smoke after `08e05f68` whacked SM_BB_PUMP_PROC. Gates: smoke_icon 5/5 · smoke_prolog 5/5 · broker 35 · rungs 161 → 165 → **170** · FACT 0. Zero regressions. **DIAGNOSIS-only (Opus 4.7, 2026-05-28, no commit):** `rung32_basic_strret` repro — `procedure greet(name); return name; end` prints `name`, expected `world`. SM dump shows `SM_PUSH_VAR "name"` inside `greet` (should be `SM_LOAD_FRAME 0`). Root cause in `src/lower/lower.c::emit_var_load` line 128: LANG_ICN proc-as-value fallback (lines 138-143) fires *before* `scope_get(g_proc_scope, vn)` at line 145. Parameters must shadow proc names — reorder scope-check above proc-as-value check. Pure SM-lowering reorder, FACT-clean. See GOAL-ICON-BB.md "Next options" for full sketch. Expected to recover rung36_jcon_* family + rung32/08/16/22 param-shadowing failures. **NOT-DONE for future sessions:** apply the diagnosed reorder; rung13 cartesian-product cases (`alt_alt_nested`, `alt_alt_cross_arg*`) need ICN-Z zipper / BB-port-graph mode-4 path; pre-existing stack underflow in `every <var> ||:= <gen>` (reproducible with `1 to 3` — independent of alternation); 63 remaining rung FAILs still dominated by param-shadowing + generator-proc semantics on SM_CALL_FN path (rung03 suspend_gen family — needs GeneratorState wiring on the SM call side). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9 partial 🟡. WAM-CP-10 partial 🟡** (Opus 4.7, 2026-05-28, one4all `5427e12e`): catch/throw mode-2 via new `BB_PL_CATCH` BB node + `bb_pl_catch_state_t {goal_g, catcher, rec_g}` — Goal and Recovery each lower into their own self-contained `BB_graph_t`; Catcher is a term-tree BB node in the OUTER graph so its vars share the surrounding clause's env. `lower_pl.c` recognises `catch/3` and `throw/1` before the generic call fall-through. `pl_runtime.c` exposes the previously-static `Pl_CatchFrame` stack via public wrappers (`pl_catch_push/_pop_top/_top_trail_mark/_top_env`, `pl_throw_term`, `pl_catch_take_exception`). Mode-2 `bb_exec.c BB_PL_CATCH` setjmps the frame, runs goal_g; on longjmp(1) re-entry **restores `g_pl_env`** from the saved frame (CRITICAL — a throw originating in a sub-call leaves `g_pl_env` pointing at the inner callee env at longjmp time, so any `BB_PL_VAR` read in Recovery would otherwise index the wrong slot table), unwinds trail to the frame's mark, unifies Catcher with the exception, runs rec_g; rethrows if catcher doesn't match. Mode-4: minimal FACT-clean stub template (`bb_pl_catch.cpp`) — α/β both `jmp ω` (mode-4 catch always fails until WAM-CP-13). **Gates: G1=5/5, G2=132/0, G3 mode-2 91→96/107 (+5 rung28), G4=4/4, mode-4 corpus=54/107 (unchanged), FACT=0, sister smokes icn/raku/sno/sc/rb all unchanged.** Earlier this session: **WAM-CP-9 partial ✅** (`549c7fca`) mode-4 cut-scope nested in pl_choice (saved_cut_flag +56, saved_cut_barrier +64); 4 rt helpers; rung07_cut_cut fixed. **NEXT:** WAM-CP-13 (longjmp-free CP-barrier unwind + mode-4 catch emit, reusing the WAM-CP-9 r12 + saved-state-slot pattern), or **WAM-CP-6 (LCO)** (principled SEGFAULT-CLUSTER fix; gate: `count(N)` to 1e6 stays O(1) stack), or **WAM-CP-9 Steps B–D** (committed-ITE node + `!` in `(A;B)` truncate). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. RK-GIVEN-MODE4 ✅. RK-HASH ✅. **RK-NAMED-CALL ✅** (Opus 4.7, 2026-05-28, one4all `c944db09`): template-pure restoration of Raku user-sub dispatch after LANG-IGNORANT-SM-TEMPLATES (`08e05f68`) ripped `rk_sub_lookup` from sm_calls.cpp/sm_jumps.cpp. New language-ignorant `SM_NAMED_CALL` opcode (a[0].s=name, a[1].i=nparams) emits `mov edi,nparams; call rt_frame_enter@PLT; call .Lsub_<name>; call rt_frame_leave@PLT`. `sm_label_str` MEDIUM_TEXT emits `.Lsub_<name>:` symbol when `a[0].s` non-empty (named labels emit symbols — opcode semantics, not language sniffing). `lower_fnc` for LANG_RAKU emits SM_NAMED_CALL when callee matches TT_SUB_DECL in proc_table. Templates contain ZERO `g_lang` refs. **GATE-RK4 17→22** (+rk_subs, +rk_combinator, +rk_interp, +rk_given, +rk_given18). GATE-RK 20 HOLD. Smokes raku/prolog/snobol4 HOLD. Icon (restored by MAIN-BOOT `80d0d5ee` in same session): smoke 5/5, broker 35, rungs 161 (rebased from `c944db09` — see ICON row). FACT RULE 0. GOAL file pruned 356→146 lines. Remaining 11 FAILs: regex/NFA (6, deferred), I/O (2), exceptions (1), junctions (1, blocked Q9-Q12), class (1). NEXT: I/O or exceptions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **M3-NATIVE-4 EP-BINARY ✅ (FACT-correct)** (Opus 4.7, 2026-05-28, one4all `0e077eb5`): combinator BB templates ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED now emit real bytes in MEDIUM_BINARY by walking `g_emit.xa_bb_ep_*[]` (the same epilogue arrays the TEXT arm consumes). **Byte production lives in each template's own file — duplicated by design per strengthened FACT RULE.** First attempt `1bc53211` violated FACT by putting `bytes(1,"\xE9") + u32le(0)` in a shared `emit_str.cpp` helper; fixed in `0e077eb5` by deleting the helper and inlining the EP-walk loop into all six combinator templates. RULES.md FACT entry strengthened to explicitly forbid shared x86-byte-producing helpers outside `*_templates/`. `xa_bb_ep_define/jmp` retyped `const char *` → `bb_label_t *` (TEXT derefs `->name`). Procedural Prolog templates bombed in BINARY (audit BOMB): bb_pl_alt, bb_pl_call, bb_pl_choice — need dedicated BINARY ports if mode-3 Prolog native scoped. Audit extended: `bin.sites.push_back` is substantive. Earlier this day: **SBL-CAP-2 ✅** (`e9a9d7f3`) native corpus 156→165/280 + LANG-IGNORANT (`08e05f68`) + M3-NATIVE-2/2b/3. Gates: G1=13/13 (default+native), G2=35, G3=175/280, G4=238/280, native=165/280 (unchanged — combinator flat-wire in mode-3 not yet enabled), rungs M2=19/M4=15, FACT=0 (restored), audit GATE OK, Prolog smoke 5/5 + mode-4 rung 4/4 + BB honest 128/0, Raku smoke 5/5. **NEXT:** wire `bb_build_flat` for combinator nodes through mode-3 sealed-RX so ALT/CAT/FENCE actually fire their new arms under `--run SCRIP_M3_NATIVE=1`; bytes are ready, build path needs the extension. Then knock SPAN/ARBNO/BREAKX leaves (each is its own per-template BINARY port using the deque-int scratch pattern from SBL-CAP-2). |
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
