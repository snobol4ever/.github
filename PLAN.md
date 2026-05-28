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
| **ICON-BB** | `GOAL-ICON-BB.md` | **RESET 2026-05-28** (Opus 4.7, one4all `89777f09`). Two and a half months of mode-2 `SM_BB_INVOKE`-per-statement watermark hunting wiped. New shape per ARCH-ICON.md *"Icon IS a Byrd Box graph"* and GOAL-ICON-BB-NATIVE.md *"ZERO C BYRD BOX FUNCTIONS"*: two-SM-op boot (`SM_BB_RUN_THE_DAMN_ICON` + `SM_HALT`), the whole program is one connected port-graph, modes 2+4 byte-identical from each rung onward. **IBB-0 ✅ reset.** **IBB-1 steps 1-5 ✅** (one4all `89777f09`): SM enum + opname + mode-2 handler + emit stubs. Build green; legacy smokes 5/5+5/5+36 hold; FACT 0. **NEXT: IBB-1 steps 6-11** — write `src/lower/lower_icn_bb.c` with `lower_icn_bb(CODE_t*) → BB_graph_t*`, hook in `lower.c` gated by `SCRIP_ICN_BB=1`, run `procedure main() write("hello") end` mode 2 with exactly two SM ops. Watermark: 0 programs (dual-mode byte-identical, not rungs PASS). See HANDOFF-2026-05-28-OPUS-ICON-BB-RESET.md. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **EP→emit_pair rename ✅ (Step 1 of FACT cleanup)** (Opus 4.7, 2026-05-28, one4all `68c2c5bc`): pure mechanical rename pass — `xa_bb_ep_define/jmp/n` → `xa_bb_emit_pair_define/jmp/n`, `EP_RESET/DEF/JMP/DEF_JMP/FILL` → `EMIT_PAIR_*`, `XA_BB_EP_MAX` → `XA_BB_EMIT_PAIR_MAX`, IFT-7 block comment rewritten without "epilogue" framing. 115 references across 8 files. Behavior-neutral; all gates byte-identical (build / G1 5/5 / G4 4/4 / sister smokes icn 5/5, raku 5/5, sno 13/13, sc 5/5, rb 4/4). Step 1 of 3-step plan to remove FACT-violating `push_back` / `bin.sites/labels/is_def` from six combinator templates (bb_pat_fence/alt/cat, bb_pl_seq/ite, bb_succeed) introduced by `0e077eb5`. **Steps 2 + 3 NOT done — fully scoped in HANDOFF-2026-05-28-OPUS-PROLOG-BB-EMIT-PAIR-RENAME.md**: Step 2 adds `bb_emit_asm_result_pairs()` driver-side helper that reconstructs (site, label, is_def) metadata from the same `xa_bb_emit_pair_*` arrays the templates consult; Step 3 strips the six template files to pure byte production (no `bin.*` access). FACT grep currently still shows the 6 violation files; Step 3 closes that. **Pre-existing: WAM-CP-1/2/3/4/5 ✅. WAM-CP-9 partial 🟡. WAM-CP-10 partial 🟡** (Opus 4.7, 2026-05-28, one4all `5427e12e`): catch/throw mode-2 via new `BB_PL_CATCH` BB node + `bb_pl_catch_state_t {goal_g, catcher, rec_g}` — Goal and Recovery each lower into their own self-contained `BB_graph_t`; Catcher is a term-tree BB node in the OUTER graph so its vars share the surrounding clause's env. `lower_pl.c` recognises `catch/3` and `throw/1` before the generic call fall-through. `pl_runtime.c` exposes the previously-static `Pl_CatchFrame` stack via public wrappers (`pl_catch_push/_pop_top/_top_trail_mark/_top_env`, `pl_throw_term`, `pl_catch_take_exception`). Mode-2 `bb_exec.c BB_PL_CATCH` setjmps the frame, runs goal_g; on longjmp(1) re-entry **restores `g_pl_env`** from the saved frame (CRITICAL — a throw originating in a sub-call leaves `g_pl_env` pointing at the inner callee env at longjmp time, so any `BB_PL_VAR` read in Recovery would otherwise index the wrong slot table), unwinds trail to the frame's mark, unifies Catcher with the exception, runs rec_g; rethrows if catcher doesn't match. Mode-4: minimal FACT-clean stub template (`bb_pl_catch.cpp`) — α/β both `jmp ω` (mode-4 catch always fails until WAM-CP-13). **Gates: G1=5/5, G2=132/0, G3 mode-2 91→96/107 (+5 rung28), G4=4/4, mode-4 corpus=54/107 (unchanged), FACT=0, sister smokes icn/raku/sno/sc/rb all unchanged.** Earlier this session: **WAM-CP-9 partial ✅** (`549c7fca`) mode-4 cut-scope nested in pl_choice (saved_cut_flag +56, saved_cut_barrier +64); 4 rt helpers; rung07_cut_cut fixed. **NEXT:** complete Steps 2+3 of FACT cleanup, then WAM-CP-13 (longjmp-free CP-barrier unwind + mode-4 catch emit, reusing the WAM-CP-9 r12 + saved-state-slot pattern), or **WAM-CP-6 (LCO)** (principled SEGFAULT-CLUSTER fix; gate: `count(N)` to 1e6 stays O(1) stack), or **WAM-CP-9 Steps B–D** (committed-ITE node + `!` in `(A;B)` truncate). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. RK-GIVEN-MODE4 ✅. RK-HASH ✅. **RK-NAMED-CALL ✅** (Opus 4.7, 2026-05-28, one4all `c944db09`): template-pure restoration of Raku user-sub dispatch after LANG-IGNORANT-SM-TEMPLATES (`08e05f68`) ripped `rk_sub_lookup` from sm_calls.cpp/sm_jumps.cpp. New language-ignorant `SM_NAMED_CALL` opcode (a[0].s=name, a[1].i=nparams) emits `mov edi,nparams; call rt_frame_enter@PLT; call .Lsub_<name>; call rt_frame_leave@PLT`. `sm_label_str` MEDIUM_TEXT emits `.Lsub_<name>:` symbol when `a[0].s` non-empty (named labels emit symbols — opcode semantics, not language sniffing). `lower_fnc` for LANG_RAKU emits SM_NAMED_CALL when callee matches TT_SUB_DECL in proc_table. Templates contain ZERO `g_lang` refs. **GATE-RK4 17→22** (+rk_subs, +rk_combinator, +rk_interp, +rk_given, +rk_given18). GATE-RK 20 HOLD. Smokes raku/prolog/snobol4 HOLD. Icon (restored by MAIN-BOOT `80d0d5ee` in same session): smoke 5/5, broker 35, rungs 161 (rebased from `c944db09` — see ICON row). FACT RULE 0. GOAL file pruned 356→146 lines. Remaining 11 FAILs: regex/NFA (6, deferred), I/O (2), exceptions (1), junctions (1, blocked Q9-Q12), class (1). NEXT: I/O or exceptions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **M3-NATIVE-4 combinator flat-wire DIAGNOSIS** (Opus 4.7, 2026-05-28, no commit): two compounding architectural blockers identified, full fix-path recorded in GOAL file. **(1) Graph-shape mismatch:** `patnd_to_bb_graph` produces γ-chain graphs (for `bb_exec.c` mode-2), but `walk_bb_flat`'s `flat_drive_cat/alt/fence` need tree-shaped graphs with `bb_pat_kids_state_t` children (as `emit_sm.c::SM_PAT_CAT` produces via `pat_set_children`). Simply opening `patnd_needs_xlate` to combinator roots regressed corpus 237→229 because γ-chain children are invisible to `bb_pat_nkids`. **(2) Dangling bb_label_t pointers:** Adding parallel `patnd_to_bb_tree` (emit_sm.c-shaped) made 050_pat_alt_two/055_pat_concat_seq produce CORRECT native output ("dog"/"ab cd ef") — proving SBL-EP-BINARY combinator arms work — but corpus still regressed because `flat_drive_alt/cat/fence` declare `bb_label_t` on the C stack via `alloca`/locals; `bin.labels` stores pointers there; by `bb_emit_end` the frame is gone, name=""→`abort()`. This is a latent bug exposed by routing more patterns through EP-driven storage. **Recommended next session:** add `BB_graph_t.lbl_pool` + `bb_label_alloc(cfg, fmt, ...)`, migrate flat drivers off stack-local labels to graph-owned arena, THEN re-implement `patnd_to_bb_tree` + extend `patnd_needs_xlate` gate. All work reverted; tree clean at `5427e12e`. **Gates HOLD baseline:** G1=13/13 default+native, G2=35, G3=175/280, G4=237/280 (−1 drift from 238 watermark, recorded), native=165/280, rungs M2=19/M4=15, audit GATE OK, FACT=0. Earlier on `5427e12e` (Sonnet/Opus prior sessions): **M3-NATIVE-4 EP-BINARY ✅** (`0e077eb5`) combinator templates emit real bytes via inline EP-walk in each template (no shared helper, per strengthened FACT RULE). **MEDIUM_BINARY arms: all BOMs eliminated ✅** (`4ce8c385`) — bb_arbno/arb/span/binop_gen/pl_alt/pl_call/pl_choice/icn_to/capture all real bytes via deque-int scratch pattern. **NEXT:** stable label storage (above), then combinator flat-wire native landing; then knock down SPAN/ARBNO/BREAKX/FENCE/POS/RPOS/TAB/RTAB clusters via existing per-template BINARY ports. |
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
