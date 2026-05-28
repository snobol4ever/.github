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
| **ICON-BB** | `GOAL-ICON-BB.md` | **ALT-EXPR ✅** (Opus 4.7, 2026-05-28, `8b0ad2ba`): TT_ALTERNATE in `lower_expr` (call-arg, `:=` RHS, bare stmt) was emitting `SM_PUSH_NULL` because `lower.c` case TT_ALTERNATE built a CFG via `lower_icn_expr_top` and immediately discarded it before calling `lower_unhandled`. Replaced with `lower_to`-shaped body: build CFG, `SM_seq_bb_add`, emit `SM_BB_INVOKE`. `BB_ALT` mode-2 exec and `SM_BB_INVOKE` interp dispatch were both already in place — pure lowering hookup. Gates: smoke_icon 5/5 · smoke_prolog 5/5 · broker 35 · rungs **161 → 165** (+4: `rung08_strbuiltins_match`, `rung13_alt_alt_int`, `rung13_alt_alt_every_write`, `rung32_strretval_strret_every`) · FACT 0. Zero regressions. **Earlier this session: MAIN-BOOT** (Opus 4.7, 2026-05-28, `80d0d5ee`) recovered Icon from 0/5 smoke after `08e05f68` whacked SM_BB_PUMP_PROC (four coordinated fixes: SM_CALL_FN main bootstrap, every-loop exit_pc onto a[2] off α/β collision slot a[0], lower_return alignment, one-shot path for non-generator `every E` with no body). **NOT-DONE for future sessions:** rung13 cartesian-product cases (`alt_alt_nested`, `alt_alt_cross_arg*`) need ICN-Z zipper / BB-port-graph mode-4 path; pre-existing stack underflow in `every <var> ||:= <gen>` (reproducible with `1 to 3` — independent of alternation); 68 remaining rung FAILs still dominated by generator-proc semantics on SM_CALL_FN path (rung03 suspend_gen family — needs GeneratorState wiring on the SM call side). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **WAM-CP-1/2/3/4 ✅** (Opus 4.7, 2026-05-28). **WAM-CP-5 ✅ COMPLETE** (Sonnet 4.6, 2026-05-28, `414d5da3`/`60dea34f`/`b1e27f56`): BB_CHOICE+BB_PL_CALL migrate rsp-frame cursor to heap `pl_choice` via `pl_cp_push/pop`; compound args via `emit_build_compound_term`; `rt_pl_arith` extended with bitwise/shift/max/min/mod/power. full mode-4 (with .expected) 40/107 (+7). GATE-1 5/5, GATE-2 132/0, GATE-3 91/107, GATE-4 4/4, FACT 0. **NEXT: WAM-CP-6 (LCO)** or fix open bugs: `**` power prefix clash with `*` in `rt_pl_arith`; unary sign/truncate/integer (different BB path). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. RK-GIVEN-MODE4 ✅. RK-HASH ✅. **RK-NAMED-CALL ✅** (Opus 4.7, 2026-05-28, one4all `c944db09`): template-pure restoration of Raku user-sub dispatch after LANG-IGNORANT-SM-TEMPLATES (`08e05f68`) ripped `rk_sub_lookup` from sm_calls.cpp/sm_jumps.cpp. New language-ignorant `SM_NAMED_CALL` opcode (a[0].s=name, a[1].i=nparams) emits `mov edi,nparams; call rt_frame_enter@PLT; call .Lsub_<name>; call rt_frame_leave@PLT`. `sm_label_str` MEDIUM_TEXT emits `.Lsub_<name>:` symbol when `a[0].s` non-empty (named labels emit symbols — opcode semantics, not language sniffing). `lower_fnc` for LANG_RAKU emits SM_NAMED_CALL when callee matches TT_SUB_DECL in proc_table. Templates contain ZERO `g_lang` refs. **GATE-RK4 17→22** (+rk_subs, +rk_combinator, +rk_interp, +rk_given, +rk_given18). GATE-RK 20 HOLD. Smokes raku/prolog/snobol4 HOLD. Icon (restored by MAIN-BOOT `80d0d5ee` in same session): smoke 5/5, broker 35, rungs 161 (rebased from `c944db09` — see ICON row). FACT RULE 0. GOAL file pruned 356→146 lines. Remaining 11 FAILs: regex/NFA (6, deferred), I/O (2), exceptions (1), junctions (1, blocked Q9-Q12), class (1). NEXT: I/O or exceptions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **M3-NATIVE-4 EP-BINARY ✅** (Opus 4.7, 2026-05-28, one4all `1bc53211`): universal `ep_bin_fill_str(bin, prelude_lbl)` helper in emit_str.{cpp,h} translates the existing `g_emit.xa_bb_ep_*[]` epilogue arrays into bytes + patch sites — same data structure the TEXT arms walk. Combinator BB templates ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED previously returned `std::string()` in MEDIUM_BINARY (mode-3 flat-wire would emit no glue between children); now all 6 emit real bytes via the helper, classified REAL by audit. `xa_bb_ep_define/jmp` arrays changed from `const char *` → `bb_label_t *` so BINARY can patch rel32 directly (TEXT derefs `->name`). bb_pl_alt/bb_pl_call/bb_pl_choice are procedural (trail_mark/CP records), not EP-driven; they now `bomb_bytes()` in BINARY (loud, was silent). audit_m3_native_binary_arms.sh updated to detect `ep_bin_fill_str` as real-arm signal. Earlier this day: **SBL-CAP-2 ✅** (`e9a9d7f3`) bb_capture BINARY arm — proper gate, deque-int scratch (GC-safe), push/pop r10 around child_fn, sites {40,49(def),77,124}, native corpus **156→165/280** (+9: 039/040/042/043 + 058/059 + W07_capt_×3); LANG-IGNORANT SM TEMPLATES (`08e05f68`); M3-NATIVE-2/2b/3. Gates: G1=13/13 (default+native), G2=31, G3=175/280, G4=238/280, native=165/280 (unchanged — EP-BINARY plumbed but combinator flat-wire in mode-3 not yet enabled), rungs M2=19/M4=15, FACT=0, audit GATE OK, Prolog smoke 5/5 + mode-4 rung 4/4 + BB honest 128/0, Raku smoke 5/5. **NEXT:** enable combinator flat-wire in mode-3 (wire ALT/CAT/FENCE through `bb_build_flat` for `--run` SCRIP_M3_NATIVE=1) to actually exercise the new BINARY arms, then knock down remaining native-only failures by cluster — SPAN, ARBNO, BREAKX. Procedural Prolog templates (PL_ALT/CALL/CHOICE) need dedicated BINARY ports if mode-3 Prolog native is ever scoped — currently bombed. |
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
