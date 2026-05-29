# GOAL-RAKU-BB.md — Raku: goal-directed ~20% onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**. `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_INVOKE` (language-ignorant BB jump-in/jump-out; split out of the old SM_BB_SWITCH per LANG-IGNORANT-SM-TEMPLATES, 2026-05-28). Raku reuses the ICN_GEN emit-time contract verbatim. Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed. Raku today is ~100% eager SM in practice; the goal-directed ~20% is what this ladder moves onto shared BB kinds.

## The insight

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP) suffices; every generative construct is a PRODUCER or CONSUMER of it. A 10-kind ladder collapses to ~3 rungs on shared kinds.

## Port semantics (identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | `take` yield / next Seq element |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`**. NOT Prolog's `BB_ONCE`.

## Moves to BB vs stays SM

**MOVES (goal-directed, REUSE shared kinds):**

| Raku construct | shared BB kind | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | `BB_TO_BY` | RK-BB-1 ✅ |
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 ✅ |
| lazy `map` / `grep` | `BB_ITERATE` consumer | RK-BB-3 ✅ |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse | RK-BB-4 (blocked) |

**STAYS eager SM:** scalar builtins (`uc`/`lc`/`substr`/`trim`/`index`/`rindex`), `say`/`print`, arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. Defer until SNOBOL4-BB and PROLOG-BB land more rungs.

## ⛔ Rules

- No C Byrd boxes; no SM/BB walking at runtime in modes 3/4; ports are α/β/γ/ω; X86 arms only.
- No `rt_*`/`raku_*` port-logic helpers. Conversion/effect helpers via `@PLT` are fine.
- **No language sniffing in SM/BB/XA templates.** No `g_lang`/`LANG_*`/`rk_sub_*` branches inside template bodies. Per-language behavior lives in the lowering (choose which SM opcode to emit). Templates emit one fixed sequence per opcode.

## Completed rungs (terse)

- **RK-BB-1** ✅ — `for $a..$b -> $i` → `BB_TO_BY`.
- **RK-BB-2** ✅ — KEYSTONE lazy `Seq`. `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`.
- **RK-BB-3** ✅ — lazy `map`/`grep` as Seq CONSUMERS (eager-drain materialization). 3.0+3a/3b/3c/3d sub-steps all green.
- **RK-BB-SEGFAULT-CLUSTER** ✅ — 4 bugs: polyglot union-clobber, multi-sub structure (lower_stmt/lower_proc_skeletons/build_proc_scope for TT_SUB_DECL), and Raku `lower_return` value preservation.
- **RK-BB-SM-FRAME-MODE4** ✅ — Mode-4 named-sub frame slots: `rt_frame_enter/leave/load/store` in libscrip_rt; SM_LOAD/STORE_FRAME x86 templates.
- **RK-GIVEN-MODE4** ✅ — `given`/`when` rewritten as if-chain over already-templated opcodes (no SM_PUMP_CASE, no thunks).
- **RK-HASH** ✅ — hash builtins (set/get/exists/keys/values/pairs/delete), SOH/STX encoding; polyglot TT_FNC skip fix; SSE alignment fix; stale-frame writeback; rt_acomp string coercion.
- **RK-IO** ✅ (Claude Sonnet 4.6, 2026-05-28, one4all `753d85e2`) — `rk_fileio38` + `rk_stdio39` mode-4. **fileio38:** `for lines($path) -> $line` was lowering as a call-per-iteration loop; added `TT_ITERATE(TT_FNC)` arm in `lower_every` that materialises the array-returning call once into a fresh `__arr_N` temp then routes through `lower_raku_iterate_arr` BB path. **stdio39:** `raku_capture` returned `INTVAL` not `FHVAL` so `$*STDOUT`/`$*STDERR` failed `IS_FH_fn` check in `write`; fixed to return `FHVAL(n)`. Added `fflush(stdout)` before non-stdout handle writes + `setvbuf(stdout,NULL,_IOLBF,0)` in `rt_init` for ordering. Runner `2>&1` to capture stderr in diff. GATE-RK4 23→25, GATE-RK 21→22.
- **RK-EXCEPTIONS** ✅ (Claude Sonnet 4.6, 2026-05-28, one4all `ed6fec27`) — try/CATCH/die mode-4. Added `raku_exc_clear`, `raku_exc_check`, `raku_exc_get` to `raku_try_call_builtin_by_name` (were referenced by lower.c but never implemented in the rt path). Fixed `raku_die` to use SSE-safe `memcpy` instead of `snprintf` (Q13a). Fixed `raku_try_hash_builtin` to guard `args[0].v == DT_S` before `VARVAL_fn` — was segfaulting when `say(integer)` called inside any sub that had a `my`-decl (hash builtin check was passing integers to `VARVAL_fn` → `snprintf` on garbage pointer). GATE-RK4 22→23, GATE-RK 20→21.
- **RK-CLASS** ✅ (Claude Sonnet, 2026-05-28) — `rk_class26` PASS in modes 2 and 4. Root cause: Raku `TT_CLASS_DECL` lowered to a runtime `RECORD_MAKE` call but the type was never registered. Polyglot's `TT_RECORD` path registers via `icn_record_register` at lower time for Icon records; that path doesn't fire for `TT_CLASS_DECL`, leaving `sc_dat_find_type("Point")` returning NULL → `RECORD_MAKE` silently returns FAILDESCR. Fix lives at SM-emission level so it works in all modes uniformly: `lower_class_decl` now emits `PUSH_STR "Point(x,y)"; CALL_FN "RECORD_REGISTER" 1; VOID_POP` before `RECORD_MAKE`, and `icn_try_call_builtin_by_name` has a new `RECORD_REGISTER` handler that delegates to the idempotent `icn_record_register`. Reachable from `sm_interp` (mode-2) and `rt_call` (mode-4) via the same dispatch chain. **GATE-RK 22→23, GATE-RK4 25→26.** Mode-3 (SCRIP_M3_NATIVE=1) still segfaults at the first `$p.sum()` — separate engine bug in `sm_run_native`'s method dispatch, NOT the registration fix; tracked under MODE3-DISPATCH-GAP.
- **Mode-3 honest baseline** 📋 (Claude Sonnet, 2026-05-28) — empirical trace at `scrip.c:518` confirmed plain `--run` for Raku invokes `sm_interp_run` (C interpreter), violating Lon's stated mode-3 invariant. Per Lon's 2026-05-28 directive (3× this session): mode-3 = flat-wired x86 SM AND BB, interpreters reserved for mode-2. Honest mode-3 = `SCRIP_M3_NATIVE=1 ./scrip --run` (engine: `sm_run_native`). Baseline on test/raku corpus: **PASS=11 FAIL=2 CRASH=20 TOTAL=33**. Crashes cluster around method dispatch, gather/take, frame slots — overlapping with open Raku-BB work. Tracked separately in `.github/MODE3-DISPATCH-GAP.md`; needs its own goal ladder mirroring IBB ground-zero. Old "Crosscheck 37/37" line in this watermark was comparing `sm_interp_run` to `sm_interp_run` (same engine, both flags) and reporting agreement — meaningless; replaced.

## Open rungs

- [~] **RK-BB-4 substrate audit** — Probe-based audit found goal text's "REUSE bb_gen_alt.cpp/bb_alt.cpp" is unfounded. Seven gaps: lex (no KW_ANY/ALL/ONE/NONE, no single `|`/`&`); TT_ALT overloaded with SNOBOL4 pat-alt; bb_exec.c BB_ALTERNATE mode-2 is no-op; bb_alternate.cpp mode-4 missing; bb_alt.cpp mode-4 stub; bb_gen_alt.cpp stub; Icon TT_ALTERNATE lowers to BB_ALT not BB_ALTERNATE → **BB_ALTERNATE is orphan; reusable substrate is BB_ALT (mode-4 stub)**. `test/raku/rk_junctions.{raku,expected}` committed as probe (`4ee45eb7`); fails at lex.

  **Open Qs for Lon (Q9-Q12, gating any work):**
  - Q9: New TT_LOR/TT_LAND for Raku `||`/`&&` to disentangle from SNOBOL4 patterns?
  - Q10: BB_ALT (n-ary, mode-4 stub) or finish orphan BB_ALTERNATE? Recommend BB_ALT.
  - Q11: Substrate-first or frontend-first? Recommend frontend-first (path b).
  - Q12: Junction value rep: (i) tagged string mirroring `\x01`-arrays, (ii) DT_JUNCT, (iii) DT_DATA. Recommend (i).

- [ ] **RK-BB-4-frontend** — pending Q9-Q12.
- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers; `zip`/`cross` = multi-Seq drivers (later).
- [~] **MODE3-NO-INTERP** — see `MODE3-DISPATCH-GAP.md` (2026-05-28 addendum, updated). Per-language ladder to remove `sm_interp_run` from `--run` path. Suggested order: Raku (this goal's responsibility), then Prolog, Snocone, Rebus. SNOBOL4 already has `SCRIP_M3_NATIVE`; flip the default. **Progress 2026-05-28:** **M3-RK-NOINTERP-3 ✅** (SM_NAMED_CALL absolute-target patching in `sm_run_native` Pass 3) closed Cluster 2 — 11/33 → 17/33 native. **2026-05-28 follow-up-3 (Sonnet) deep-dive:** M3-RK-NOINTERP-1 is *architectural*, not a one-symbol fix. The MEDIUM_BINARY arms of bb_to_by/bb_upto/bb_suspend/bb_iterate/bb_icn_to all write yielded values to **r12 as a brokered-slab vstack pointer**, but `sm_run_native` does not initialise r12 (nor does XA_FLAT_PROLOGUE or bb_broker). Splicing those BINARY arms into the SM byte stream of mode-3 yields segfault-or-corruption + the SM vstack underflow that prints "libscrip_rt: SM value stack underflow." Required path: **(a) new mode-3-ABI branch in each generator BB template using `rt_push_int@PLT`** (matches the existing MEDIUM_TEXT arm at bb_to_by.cpp:89-90 line); template-per-step. Split as 1a (bb_to_by), 1b (bb_upto), 1c (bb_iterate), 1d (bb_suspend / bb_seq) — each closes a slice of Cluster 1. **Remaining:** Cluster 1 (8 tests, includes rk_given18 revealed behind Cluster 2); Cluster 3 (6 regex, DEFERRED to GOAL-RAKU-PAT-BB).

## Rung methodology

Per rung: (1) lower the Raku construct to the shared BB kind via `lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp` covers it; (3) only if semantics differ, **extend the lowering** — never the template — to match; (4) run GATE-RK4 + GATE-RK (mode-2) + smoke. Commit when goldens match and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (33 cases). Job is mode-4 conformance (Prolog GATE-4 pattern). Add NEW flat files only for laziness probes the eager suite can't express.

## Mode-3 (`--run`)

**2026-05-28 Lon directive (3× this session, BINDING):** mode-3 = flat-wired x86 SM AND BB. Interpreters reserved for mode-2. `--run` MUST NOT invoke `sm_interp_run`. Honest mode-3 measurement = `SCRIP_M3_NATIVE=1 ./scrip --run`. Today's default `--run` for Raku silently falls through to `sm_interp_run` (empirically traced); that is a violation pending ladder work — see `MODE3-DISPATCH-GAP.md`.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt > /tmp/build.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash scripts/test_raku_ir_rungs.sh    # GATE-RK mode-2 baseline
bash scripts/test_raku_mode4_rung.sh  # GATE-RK4 mode-4 baseline
bash scripts/test_smoke_raku.sh       # smoke baseline
```

## Gates

```
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: M3-RK-NOINTERP-1a — bb_to_by.cpp MEDIUM_BINARY arm rt_push_int conversion (Sonnet 4.6, 2026-05-28 follow-up-4). Surgical edit in `src/emitter/BB_templates/bb_to_by.cpp`: the four `r12`-relative yield writes (mov dword[r12],DT_I / mov dword[r12+4],0 / mov [r12+8],rcx / add r12,16 — 18 bytes) replaced with the rt_push_int call convention from bb_to.cpp (IBB-3): `mov rdi,rcx ; movabs rax,&rt_push_int ; call rax` (15 bytes). Added `void rt_push_int(int64_t v);` forward-decl + `<stdint.h>` include at file top. **Mode-4 brokered path UNAFFECTED:** verified that `BB_TO_BY` MEDIUM_BINARY is reached only via `sm_run_native` (mode-3 native) — the SNOBOL4 pattern brokered builder `bb_build_brokered` is exclusively for BB_PAT_* kinds; mode-4 Raku `--compile` uses MEDIUM_TEXT (verified by emitting `lea rax,[rip+.Ltoby*_cur]` style asm). All three offsets in `bin = {fail_off+2, succ_off+1, back_off}` recomputed correctly across the byte-length change; the jcc rel32 patch site moves but the bin descriptor uses `(int)b.size()` snapshots so it tracks automatically. **DISCOVERED ARCHITECTURAL BLOCKER for closing rk_range_for / Cluster 1:** `sm_bb_invoke` MEDIUM_BINARY arm at `src/emitter/SM_templates/sm_bb_switch.cpp:35-36` is a 5-byte no-op stub (`E8 00 00 00 00` — `call rel32=0`). The MEDIUM_TEXT arm inlines the BB graph (calls `walk_bb_node_str_c(gen)` + emits γ/ω epilogue with rt_set_last_ok); the MEDIUM_BINARY arm does not. Therefore even with bb_to_by.cpp emitting correct yield bytes, the generator never runs under mode-3 native — SM_BB_INVOKE executes the no-op call, the next SM op (`SM_JUMP_F → exit`) finds the vstack empty → underflow. **rk_range_for still CRASH** until SM_BB_INVOKE MEDIUM_BINARY is wired up. The prior-author watermark recommended path (a) — template-per-step — assumed sm_bb_invoke would route through inline templates; that assumption was wrong. Path (a) AND a sibling sm_bb_invoke MEDIUM_BINARY fix are both required; they compose cleanly (bb_to_by is now ready for that wiring). Also note: `walk_bb_flat` (the MEDIUM_TEXT inline driver in `emit_bb.c:981`) has `case BB_TO:` but no `case BB_TO_BY:` — BB_TO_BY currently falls into `default:` (define β + jmp ω twice). This needs adding alongside the SM_BB_INVOKE MEDIUM_BINARY change. **Mode-3 measurement re-baselined:** 17→18 PASS (rk_stdio39 PASS this session — same flip the prior watermark noted, in the other direction; stderr-ordering is order-of-rt_init contingent and not actually about Cluster 1). All other gates HOLD byte-for-byte.
.github: GOAL-RAKU-BB.md watermark update for M3-RK-NOINTERP-1a + discovered SM_BB_INVOKE BINARY stub blocker
corpus:  unchanged

GATE-RK   mode-2:                23/33  HOLD
GATE-RK3  --run SCRIP_M3_NATIVE: 18/33 + 1 FAIL + 14 CRASH (rk_stdio39 PASS this session; all 14 CRASHes unchanged)
GATE-RK4  mode-4:                26/33  HOLD
Smoke raku:       5/5    HOLD
Smoke prolog:     5/5    HOLD
Smoke snobol4:    13/13  HOLD
Smoke icon:       5/5    HOLD
FACT RULE grep:   0
Build:            clean
```

## Remaining 7 mode-4 FAILs

- REGEX/NFA (6): rk_re32/33/34/35/37, rk_regex23 — DEFERRED to GOAL-RAKU-PAT-BB.
- JUNCTIONS (1): rk_junctions — BLOCKED on Lon Q9-Q12.

## Mode-3 (SCRIP_M3_NATIVE=1) status — 18 PASS, 1 FAIL, 14 CRASH

PASS (18): rk_arith rk_arrays rk_class26 rk_combinator rk_control rk_forloop rk_given rk_hash17 rk_hashes rk_interp rk_stdio39 rk_str22 rk_strings rk_subs rk_try_catch25 rk_typed_vars rk_unless_until rk_vars
FAIL  (1): rk_junctions
CRASH (14): rk_fileio38 rk_for_array rk_for_array_simple rk_for_array_underscore rk_gather rk_given18 rk_map_grep_sort24 rk_range_for rk_re32 rk_re33 rk_re34 rk_re35 rk_re37 rk_regex23

Remaining crash structure: 8 in Cluster 1 (SM_BB_INVOKE MEDIUM_BINARY no-op stub — the architectural blocker described in this watermark; bb_to_by template-level fix is in place but unreachable until SM_BB_INVOKE wires up; rk_given18 belongs here behind its prior Cluster 2 SEGV), 6 in Cluster 3 (regex, deferred to GOAL-RAKU-PAT-BB).

## NEXT STEP RECOMMENDATION — M3-RK-NOINTERP-1b (sm_bb_invoke wiring)

Before further BB-template mode-3-ABI conversions (bb_iterate / bb_upto / bb_suspend / bb_seq), the SM_BB_INVOKE MEDIUM_BINARY arm in `src/emitter/SM_templates/sm_bb_switch.cpp` must be wired to inline the BB graph like its MEDIUM_TEXT sibling. Concretely:
  1. Add `case BB_TO_BY:` to `walk_bb_flat` in `emit_bb.c:981` area (alongside the existing `case BB_TO:`).
  2. Make SM_BB_INVOKE MEDIUM_BINARY emit: an entry-flag byte (or use a global allocated at sm_image_init), a load+compare+jcc to dispatch fresh-α vs resume-β, a call to walk_bb_flat (which now emits BINARY bytes via FILL→template dispatch), and a γ/ω epilogue with `mov rdi,1/0 ; call rt_set_last_ok@PLT` then jmp to exit_pc. The MEDIUM_TEXT arm at `sm_bb_switch.cpp:38-87` is the exact reference shape — translate each `s_directive`/`s_2asm` into the equivalent raw-byte sequence.
  3. Verify on rk_range_for first (the simplest BB_TO_BY case); expect 18→19 PASS, 14→13 CRASH. Then re-attempt bb_iterate / bb_upto / bb_suspend / bb_seq mode-3-ABI edits.

Alternative path (option b in prior watermark): allocate r12 as a per-invoke malloc'd region in sm_bb_invoke MEDIUM_BINARY, set r12, run inlined BB, then drain r12 → rt_push_int. Less invariant-preserving (introduces a second vstack convention into mode-3) but localised to one site; useful if (1) is gated.

## Open questions for Lon

Resolved (2026-05-27): 100% template emission via BB/SM/XA only.

Pending:
- **Q5.** Union-clobber proper fix. TT_SUB_DECL uses `v.ival` for nparams AND wants `v.sval` for name. Move nparams to a side-channel so `v.sval = name` semantics is restored.
- **Q9-Q12.** RK-BB-4 directives — see substrate audit above.
- **Q13.** `rk_try_catch25` — for try/CATCH/die mode-4. Per Lon: no language gates in SM/BB/XA templates. Correct path: (a) SSE-safe `raku_die` byname (replace snprintf with manual byte-copy); (b) per-stmt `raku_exc_check` catches at try-body level; (c) `lower_stmt` for TT_DIE emits SM_RETURN after die-payload when `g_in_proc_body` (pure lowering, no template change).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
