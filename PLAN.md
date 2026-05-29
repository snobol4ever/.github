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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-2e call/N mode-2 fallback ✅** (Opus 4.7, 2026-05-28, one4all `3de01576`): extended SWI-2d to N>1 (partial application with appended args). BB_PL_CALL call-meta intercept widened from `carity == 1` to `carity >= 1`; new public `pl_call_term_n(Term *gt, int n_extra, Term **extras)` in `pl_runtime.c` reconstructs the goal compound (atom → `G(extras…)`, compound `G(a1..ak)` → `G(a1..ak, extras…)`) and dispatches via `pl_invoke_var_goal`. Mirrors the call/N arm at `interp_exec_pl_builtin:1050` which only fires when call/N arrives as a synthesized FNC tree-node — the BB_PL_CALL path bypassed it. Three files, +61 lines. **rung33_bridge_callN: 1/5 → 2/5** (01 atom + 03 call/2 builtin+arg — the canonical SWI-2e case). The hoped-for 5/5 didn't materialize: tests 02/04/05 hit a **separate pre-existing bug** confirmed at `d805b0fe` baseline (re-tested) — `call(G)` where G is bound to a *user-defined* compound dispatches through `interp_exec_pl_builtin`'s user-call branch at `pl_runtime.c:894-900`, which is **stubbed** at line 895 with `[NO-AST] interp_eval stub` returning FAILDESCR, then segfaults downstream. SWI-2e works cleanly for its target case (builtin reconstruction). Lowering unchanged → mode-3/4 byte output untouched (FACT-safe, grep clean). Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-2E-CALLN.md`. Gates unchanged: smoke 5/5, G2=132/0 (5 ORACLE_MISS), G3=104/107, GATE-SWI=53/57 (92%), BB-honest=128/0, FACT=0, Icon 5/5, Raku 16/1. **NEXT options:** (a) **PL-RT-USER-FROM-SYNTH** (RECOMMENDED — closes rung33 02/04/05 by making `interp_exec_pl_builtin:895` user-call stub actually execute the user predicate, probably via `pl_bb_lookup`+`bb_exec_once` mirroring BB_PL_CALL's own post-intercept path); (b) SWI-5 EMPTY verdict; (c) PL-RT-ASSERTZ; (d) WAM-CP-13; (e) WAM-CP-6 LCO. [Prior: **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **SWI-2-fold ✅** (`43933846`) 0/57 → 53/57; **SWI-2-pre ✅** (`cda40a70`) findall determinism guard; **SWI-1a ✅** (`86abe166`) directive whitelist; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-CLASS ✅** (Sonnet, 2026-05-28, one4all `baf73030`): rk_class26 PASS in modes 2+4. Root: `lower_class_decl` emitted `RECORD_MAKE` but type was never registered (polyglot's `TT_RECORD` registration doesn't fire for Raku `TT_CLASS_DECL`). Fix at SM-emission level: `lower_class_decl` now emits `PUSH_STR "Point(x,y)"; CALL_FN "RECORD_REGISTER" 1; VOID_POP` before `RECORD_MAKE`; new `RECORD_REGISTER` handler in `icn_try_call_builtin_by_name` delegates to idempotent `icn_record_register`. Reachable from `sm_interp` (mode-2) and `rt_call` (mode-4) via the same dispatch chain — one source of truth, all modes. **GATE-RK 22→23, GATE-RK4 25→26.** **Mode-3 honest baseline established (per Lon 3× directive "mode 3 = flat-wired x86 SM AND BB"):** `SCRIP_M3_NATIVE=1 --run` over test/raku = PASS=11 FAIL=2 CRASH=20 TOTAL=33. Plain `--run` empirically traced to `sm_interp_run` — same engine as `--interp`, prior "Crosscheck 37/37" was meaningless. `bb_seq.cpp` n==0 empty-passthrough allowlisted (same shape as bb_fail.cpp); M3-NATIVE audit truthfully GATE OK. Tracked in `.github/MODE3-DISPATCH-GAP.md`. **NEXT:** triage mode-3 native crashes (20 tests, likely method dispatch + gather + frames), OR fold MODE3-NO-INTERP ladder into this goal, OR resolve Lon Q9-Q12 for RK-BB-4 junctions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **M3-NATIVE-4 combinator flat-wire LANDED ✅** (Opus 4.7, 2026-05-28, one4all `10f97d29`). Three commits this session: `1e9ae6c6` (bb_seq n==0 BINARY arm walks EP-pair — audit FAKE-JMP→REAL); `a4b62c1f` (combinator flat-wire — new `patnd_to_bb_tree` in lower_pat_dcg.c translates XCAT/XOR/XFNCE roots over atoms into emit_sm-shaped trees with `bb_pat_kids_state_t` kid arrays via `nd->counter`, so `flat_drive_alt/cat/fence` finds populated kids via `bb_pat_nkids/bb_pat_kid`. New `patnd_tree_eligible` + `patnd_is_combinator_root` in stmt_exec.c gate the route; LIVE-mode only, BROKERED untouched); `10f97d29` (capture-wrap extension — XNME/XFNME wrapping eligible subtrees translate to `BB_PAT_ASSIGN_COND/IMM` with inner as single kid, routes through existing `bb_build_brokered` child-build via `pre_build_children`). Root cause confirmed: PATND_t kind enum (XCAT=19) collides with BB_op_t (BB_EVERY=19) on raw cast — explains 055_pat_concat_seq's "BB_EVERY needs flat_drive_every" abort. With label arena (`744ae342`) in place, no dangling-stack-label regression from prior attempts. **Canonical wins:** `('cat'\|'dog') . V` over `'dog'` → `dog` native ✓ ; `LEN(2) . A LEN(2) . B LEN(2) . C` over `'abcdef'` → `ab cd ef` native ✓. **Gates:** G1=13/13 default+native, G2=38/53, G3=162/280, G4=237/280, **native broad 142→157/280 (+15)**, rung suite M2=19/M4=14, Prolog/Raku/Icon smokes 5/5. Audit was OK at my push time; concurrent upstream commit `6393c743` (IBB bb_call/bb_seq n>0) introduced a new FAKE-JMP in `bb_lit_scalar.cpp` — separate from this work, owned by ICON-BB. Handoff `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-COMBINATOR-FLATWIRE.md`. **NEXT:** ARBNO inside combinators (rung 052/054 still fail native — extend XARBN handling in `build_patnd_tree`, likely delegate to `build_patnd` since its inner-block shape already works); then 053_pat_alt_commit / 056_pat_star_deref / 057_pat_fail_builtin investigation; eventually flip the `SCRIP_M3_NATIVE=1` default. |
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
