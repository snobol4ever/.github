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
| **ICON-BB** | `GOAL-ICON-BB.md` | **GEN-BUILTIN ✅** (Opus 4.7, 2026-05-28, one4all `8cc487e9`): Icon `find()`/`key()` were lowered via flat `SM_CALL_FN`, so they returned only first value when used as generators. Routed shape-2 TT_FNC dispatch through `lower_icn_expr_top` for fn∈{find,key} → SM_BB_INVOKE. Recovered `rung08_strbuiltins_find_gen`. `key(t)` standalone generates 3 keys; `rung23_table_table_key` still FAILs because `t[key(t)]` triggers a separate stack-underflow (generator-in-subscript family). **Earlier this session: BANG-EXPR** (`381df169`) — `lower_iterate` for LANG_ICN was the same anti-pattern: build bbg, BB_free, lower_unhandled. Recovered 10 rungs (rung22 bang_list/put_bang, rung31 sort/sortf, rung11/13/15 each one). **LIMIT-EXPR** (`471ac1c9`) — `lower_limit` was lower_unhandled stub; mirrored `lower_to`. Recovered all 5 rung14 + rung30_misc_seq. Also added rung37 to runner glob (was silently skipped, 14 tests). **PARAM-SHADOW** (`4d5fe69e`) — applied last session's diagnosis: `emit_var_load` was checking LANG_ICN proc-as-value before `scope_get`, so parameters didn't shadow proc names. Reordered (matches `emit_var_store`). Recovered rung32_basic_strret. **rung36 split** (corpus `e89681b` + one4all `64c7530c`): 75-test JCON pool split into 8 intent categories via runner-side sidecar. No file renames. Per-category subtotals emitted by `test_icon_all_rungs.sh`. Gates: smoke_icon 5/5 · smoke_prolog 5/5 · broker 36 (+1) · rungs 170 → **194** / FAIL 53 / XFAIL 36 / TOTAL 269 → **283** (+14 from rung37 glob) · FACT 0. **rung36 by category snapshot:** control 0/4/9, gens 0/6/6, io 0/3/3, numbers 0/3/5, reflection 1/4/4, scan 0/6/3 (best signal/noise), strings 5/4/2 (moving), structures 0/3/4. **NEXT options:** rung36_scan cluster · every-augop-gen stack underflow · generator-in-subscript stack underflow · block-body BREAK/NEXT on new BANG path · rung37 newly-visible tactical fails (8). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-PLUNIT track opened** (Sonnet 4.6, 2026-05-28, one4all `8c556f29`). Gates: G1=5/5, G2=132/0, G3=**104/107 mode-2=mode-3; mode-4=54/107**, G4=4/4, FACT=0. GATE-SWI=**0/57 (0%)** — root causes diagnosed: (A) `begin_tests`/`end_tests` directives silently dropped by `lower.c`; (B) `test/2` clauses never enter `pj_test/4` (no term_expansion); (C) `:- if/else/endif` not implemented; (D) bare `Var==Val` option form not normalised. Plan: SWI-1 (directive calling) → SWI-2 (clause/2 + test registration) → SWI-3 (option normalisation) → SWI-4 (if/else/endif) → SWI-5 (false-positive fix) → SWI-6 (per-suite rung scripts, 3 modes each) → SWI-7 (gap-fill builtins) → SWI-8 (3-mode suite script). **NEXT: SWI-1a** — add `begin_tests`/`end_tests`/`dynamic` to directive-call whitelist in `lower.c`. |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-IO ✅** (Claude Sonnet 4.6, 2026-05-28, one4all `753d85e2`): `rk_fileio38`+`rk_stdio39` mode-4. fileio38: `for lines($path) -> $line` was calling `lines` on every iteration; added `TT_ITERATE(TT_FNC)` arm in `lower_every` — materialise call once into `__arr_N` temp, iterate via `lower_raku_iterate_arr` BB path. stdio39: `raku_capture` returned `INTVAL` not `FHVAL`; fixed. `fflush(stdout)` before non-stdout fh writes; `setvbuf` in `rt_init`; runner `2>&1`. GATE-RK4 23→25. GATE-RK 21→22. 8 FAILs remain: REGEX/NFA (6, deferred), JUNCTIONS (1, blocked Q9-Q12), CLASS (1). NEXT: CLASS or Q9-Q12 junctions. |
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
