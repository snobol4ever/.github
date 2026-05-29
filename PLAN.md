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
| **ICON-BB** | `GOAL-ICON-BB.md` | **HELLO MODE-3 PASS** (Opus 4.7, 2026-05-28 follow-up, one4all `6393c743`). Three template MEDIUM_BINARY arms landed: `bb_lit_scalar` (10-byte pass-through, exact `bb_fail` shape), `bb_call` for `write(string_literal)` only (37 bytes: movabs rdi,sptr; mov esi,slen; movabs rax,fnptr; call rax; jmp γ; β: jmp ω — runtime-fn and string-literal addrs embedded as movabs immediates per `bb_upto.cpp` precedent), `bb_seq(n>0)` (EP-pair iteration mirroring `bb_pl_seq.cpp`). **Mode-3 canonical-5: 0/5 → 1/5 (hello.icn).** Mode 2 + mode 3 byte-identical on hello.icn (`hello\n`). Mode 2 corpus unchanged at PASS=200 FAIL=47 XFAIL=36 TOTAL=283. Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 38/15, FACT=0, SM count=0 for hello.icn. **Remaining canonical-5 abort sites (verified by running):** `add.icn` → `bb_call: write(BB_BINOP)` shape unsupported; `every_to/alt/full` → `walk_bb_flat: BB_EVERY needs flat_drive_every`. **NEXT (architectural decision needed):** value-passing convention for mode-3 slabs — `r12`-anchored ring (precedent: `bb_upto.cpp`), `vstack` via runtime helpers, or in-slab per-node u64 slots. All four remaining canonical-5 share this dependency. Handoff `HANDOFF-2026-05-28-OPUS-IBB-HELLO-MODE3.md`. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-2d call/1 mode-2 fallback ✅** (Opus 4.7, 2026-05-28, one4all `d805b0fe`): closed the `call(true)` blocker named by SWI-2c. **Diagnosis correction:** the prior handoff's three hooks in `pl_runtime.c` (`pl_invoke_var_goal:845`, `pl_term_to_synth_expr` TERM_ATOM at 805, `interp_exec_pl_builtin` `true` arm at 894) are **all dead code in mode-2 `--interp`** — verified by env-gated `SCRIP_TRACE_CALL1` fprintf in each: none fired. Real path: `--interp` → `SM_BB_PL_INVOKE("main/0", 0)` → `bb_broker` → `BB_PL_CALL` in `bb_exec.c:3259`. Lowerer falls `call/N` through to `lower_pl_new_Call` (no entry in `pl_builtin_style`), producing a `BB_PL_CALL "call/1"` node whose `pl_bb_lookup` misses. **Fix:** `bb_exec.c` BB_PL_CALL handler intercepts `callee=="call" && carity==1` before lookup, converts `zc->args[0]` via existing `pl_node_to_term`, derefs through `g_pl_env`, dispatches via new public `pl_call_term` wrapper (formerly-static `pl_invoke_var_goal`). Three files, +28 lines. Empirically verified: `call(true)` `call(fail)` `call(G)` with G bound to atom or compound all work correctly. Lowering unchanged so mode-3/4 byte output untouched (FACT-safe). Does NOT handle call/N for N>1 — natural next step. Gates unchanged from `a88f1e68`: smoke 5/5, G2=132/0, G3=104/107, GATE-SWI=53/57 (92%, 4 MISS: catch/variant/float_compare/max_integer_size), BB-honest=128/0, FACT=0. Gate number static because the 53 PASSes were already PASS-by-accident via `SF=:=0` and most test bodies use `call/N` for N≥2 (still unsupported) or other unimplemented features. Critical path is unblocked nonetheless. **NEXT options:** (a) **call/N for N>1** (RECOMMENDED — mechanical extension of SWI-2d, likely closes `rung33_bridge_callN` 1/5→5/5); (b) SWI-5 EMPTY verdict; (c) PL-RT-ASSERTZ; (d) WAM-CP-13; (e) WAM-CP-6 LCO. [Prior: **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **SWI-2-fold ✅** (`43933846`) 0/57 → 53/57; **SWI-2-pre ✅** (`cda40a70`) findall determinism guard; **SWI-1a ✅** (`86abe166`) directive whitelist; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-CLASS partial-2 🟡** (Claude Sonnet 4.6, 2026-05-28, one4all `456cc7d0`): `lower_class_prescan` registers method subs in proc_table before `lower_proc_skeletons`; method bodies now emit correctly (nparams offset fix: parser sets `v.ival = explicit+1` for implicit self); `TT_TWIGIL_FIELD` uses `emit_var_load("self")` → `SM_LOAD_FRAME slot 0`; `TT_METHCALL` static-resolves via `g_raku_meth_table` → `SM_NAMED_CALL`; `raku_new`/`raku_mcall` added to `raku_builtins_byname.c`. SM structure verified correct. **Open blocker:** `raku_new` byname returns FAILDESCR — `sc_dat_find_type("Point")` likely returns NULL because `RECORD_MAKE` registers via a different path than `sc_dat_find_type` expects (spec key vs bare name). See `HANDOFF-2026-05-28-SONNET-RAKU-BB-CLASS-2.md`. GATE-RK4 25/33 HOLD. Mode 4 deferred per Lon directive. |
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
