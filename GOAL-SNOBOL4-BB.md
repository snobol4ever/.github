# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md · GOAL-MODE4-SN4-SNOCONE.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle)
    → [mode 4] walk_bb_flat → FILL → walk_bb_node → emit_core
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 via bb_bin_t)
```

- **Mode 2 (`--interp`):** `SM_EXEC_STMT` → `exec_stmt_blob` → `bb_build_brokered` → `bb_broker` → dispatched x86 blob from template BINARY arm. ALSO: `bb_exec.c case BB_PAT_*` is the pure-C correctness reference.
- **Mode 3 (`--run`):** `SM_EXEC_STMT` → `rt_match_blob` → `exec_stmt_blob` → `bb_build_flat` → inline x86 from template TEXT arm.
- **Mode 4 (`--compile`):** `codegen_sm_x86` → `walk_bb_pattern_blobs` → `codegen_flat_build` → `walk_bb_flat` → FILL → `walk_bb_node` → template TEXT arm → GAS.

**Absolute rules (RULES.md):**
- No C Byrd boxes. No `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω.
- TEMPLATE-PURITY: every `_str()` body is `state → std::string`, zero `emit_text_n` inside.
- ONE x86 PRODUCER: all emission via `BB_templates/` template functions.
- HQ Invariant 0: returning `std::string()` is a STUB.
- X86 ONLY FOR NOW — no JVM/JS/NET/WASM arms until directed.

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)` which sets `g_emit.lbl_α/β/γ/ω` then calls `walk_bb_node(nd)`. The template emits:

```
<lbl_α>:    α-port code (fresh entry — match, advance Δ, jump γ or ω)
<lbl_β>:    β-port code (retry — undo, advance differently, jump γ or ω)
            (some kinds: β = lbl_ω directly — no retry)
```

**Runtime state in TEXT arm:**
- `[r10]` = Δ (cursor, 32-bit int) — scan position
- `[rip + Σ]` = pointer to subject string; `[rip + Σlen]` = length
- Per-node static data: `.data` label `[rip + .Lfoo<id>]`
- `nd->sval` = charset string (ANY/SPAN/BREAK/NOTANY) — baked into `.data`
- `nd->counter` (int64) = runtime mutable state for generators (SPAN β)

**BINARY arm:** `g_emit.bb_cs_zeta = rt_cs_new(nd->sval)` pre-allocated; emits raw bytes; `bb_bin_t` carries rel32 fixup site list.

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                # GATE-1: 13/13 (mode-2 7/7 + mode-3 6/6)
bash scripts/test_smoke_unified_broker.sh         # GATE-2: 25
bash scripts/test_mode4_broad_corpus_snobol4.sh   # GATE-3: ≥175/280
bash scripts/test_snobol4_pat_rung_suite.sh       # Rungs: M2=18, M4=15, SKIP=0
```

---

## Open Rungs (priority order)

### SBL-MODE-PURITY — eliminate inter-mode brokered/flat fallbacks ⏳

**Architectural rule (Lon, 2026-05-27):** Modes do NOT silently fall back between themselves. If the user runs `--run` (mode-3, BB_MODE_LIVE), patterns must be built via `bb_build_flat`. If the user runs `--interp` (mode-2, BB_MODE_BROKERED), patterns must be built via `bb_build_brokered`. Inter-mode fallback corrupts the test signal: a green test cannot be trusted to have actually run in the mode it claims, because a hidden fallback may have substituted a different builder behind the back of the measurement.

**Known leak sites:**

`src/runtime/snobol4/stmt_exec.c`:
- L309: DT_S/DT_SNUL post-XDSAR coercion → `bb_build_brokered` unconditionally (mode-blind)
- L311: EPS rescue when L309 fails → `bb_build_brokered` (mode-blind)
- L327: **BB_MODE_LIVE branch fallback** — `if (!bb_build_flat) bb_build_brokered` (the flagship leak)
- L354: post-dispatch `!bin_done` rescue → `bb_build_brokered` (mode-blind)
- L361: DT_P but `pat.p` NULL → `bb_build_brokered` (mode-blind)
- L367: DT_S literal coercion → `bb_build_brokered` (mode-blind)
- L377: `!bin_done` rescue in DT_S branch → `bb_build_brokered` (mode-blind)
- L384: catch-all → `bb_build_brokered` (mode-blind)

`src/emitter/emit_bb.c`:
- L846: `pre_build_children` mixes brokered/flat per node-kind (ARBNO/ASSIGN_*/CALLOUT split)
- L847: `if (!fn) fn = bb_build_brokered(ch)` — silent fallback in pre-build path

**Probe results (this session):**
- GATE-1 smoke under `--run`: zero fallback hits at L327. The LIVE flat path is actually carrying these tests.
- Rung suite: zero L327 hits. The rungs that fail M4 are failing in `bb_build_flat` itself, not the dispatcher.
- DT_S coercion probe (L367): zero hits under `--run` smoke. Literal patterns reach stmt_exec.c as DT_P (already lowered to PATND).
- L309/L311/L354/L361/L377/L384 leaks unmeasured — likely zero hits in current corpus but cannot be assumed.

**Strategy:** carve sub-steps, fix one site at a time, re-gate after each.

- [x] **SBL-MODE-PURITY-1**: Remove L327 LIVE→brokered fallback. Replace with honest NULL propagation; assert `bin_done==0` keeps `!bin_done` path; `g_bin_misses++` already increments. Expectation: GATE-1 holds (probe showed no hits); GATE-3 unchanged (mode-4 binary doesn't traverse this branch in scrip's process). Rung M4 unchanged. If anything regresses, the regression is REAL — it surfaces a previously-masked flat builder failure. **DONE 2026-05-27 (Opus 4.7, continued 13):** removed `if (!bfn) bfn = bb_build_brokered(pp_bb);` at stmt_exec.c:327. All five gates hold at watermark (13/13, 26, 175/280, 218/280, M2=18 M4=15). Probe instrumentation confirmed zero fallback hits in GATE-1 smoke and rung suite — the fallback was unreachable under current corpus.
- [ ] **SBL-MODE-PURITY-2**: Mode-gate L309/L311/L367/L377 literal-coercion paths. Under LIVE call `bb_build_flat`; under BROKERED call `bb_build_brokered`. The literal-coercion EPS rescues (L311 / `!bin_done` paths) also become mode-gated.
- [ ] **SBL-MODE-PURITY-3**: Mode-gate L354 / L361 / L384 catch-alls.
- [ ] **SBL-MODE-PURITY-4**: Fix emit_bb.c:846-847. Per-node-kind builder split is arguably correct (some kinds genuinely need the brokered ABI for child recursion) but the L847 fallback is unconditional and must go. Investigate whether the per-kind split is intentional architecture or another latent leak.
- [ ] **SBL-MODE-PURITY-5**: Audit any cache_insert path (L334) that may cache a brokered blob under LIVE mode. The cache must be mode-tagged or cleared on mode transitions, or the cache itself becomes a fallback vector.

**Do NOT proceed to SBL-ANY-2 (BINARY arm filling) until SBL-MODE-PURITY-1 lands** — filling BINARY arms while a brokered-fallback exists in the LIVE path means the new bytes will also be silently substituted by brokered behavior if any flat-build fails, defeating the purpose of the fill.

---

### NEXT: SBL-DCG-DEFER-M4 stmt_exec.c wiring ✅ (narrowed) + SBL-ARBNO-COUNTER-RESET ✅

**Status:** Both landed (this session).

**SBL-ARBNO-COUNTER-RESET ✅:** `scrip_ir.c bb_reset()` — one-line guard `if (nd->t != BB_PAT_ARBNO) nd->counter = 0;` Preserves the `bb_arbno_state_t*` aux pointer across `bb_exec_once` calls. Rung suite M2 16 → 18 (rungs 052, 054 newly pass).

**SBL-DCG-DEFER-M4 stmt_exec.c wiring ✅ (narrowed):** Added `lower_pat_dcg.h` include + `patnd_contains_arbno()` static helper + gated translator path in both `BB_MODE_LIVE` and `BB_MODE_BROKERED/DRIVER` branches. When the PATND root tree contains XARBN anywhere, `patnd_to_bb_graph(pp)` builds a proper BB graph and `bb_build_brokered/flat` walks its `entry` (a real `BB_t*`). Else falls back to legacy cast. Mode-2 broad corpus 210 → 218 (+8: 052/054/070/075/116/142/W04_arbno_basic/backtrack/zero).

**Why narrowed:** The unconditional translator path traded 6 ARBNO wins for 6 fence/capture/func regressions (146/147/152/1011/1013/1017). Non-ARBNO PATND trees rely on the legacy cast's accidentally-benign garbage-opcode behaviour and break under the translator. XARBN-gating isolates the wins cleanly.

**Widened (this session, follow-up commit `26913b08`):** Extended the translator gate from XARBN-only to also accept single-atom PATND roots (XCHR/XSPNC/XBRKC/XBRKX/XANYC/XNNYC/XLNTH/XPOSI/XRPSI/XTB/XRTB/XFARB/XSTAR) via new `patnd_is_simple_atom` + `patnd_needs_xlate` helpers. These atoms were broken on the legacy cast (opcode misread → broker fails fast) but the translator produces correct BB_PAT_<KIND> nodes that the broker handles. Mode-4 broad 173 → 175 (+2): Qize_driver restored + W02_seq_basic + W02_seq_nested. Mode-2 broad unchanged at 218. Rung suite unchanged.

**Known follow-up — SBL-ARBNO-NOTANY-CORRECTNESS:** Still open as a separate concern but the mode-4 Qize_driver regression is GONE. Probe `pat = ARBNO(NOTANY("'")); s = 'abc'; s pat . m` → m="" matches the SPITBOL oracle (m="" is correct under unanchored leftmost-shortest semantics). The bug is actually that **inline** `ARBNO(NOTANY)` returns m="abc" — opposite of var-stored. Trace cause: inline pattern flat-driver uses different code path. Carve as fresh rung if it affects corpus tests.

---

### SBL-G-2 — Re-freeze GATE-PK for pattern kinds ⏳
- [ ] After filling each template, re-freeze its kind's cell in `test_per_kind_diff.sh`. Current baseline references DELETED `rt_bb_*` C boxes — stale.

### SBL-ANY-2 — Fill `bb_pat_any.cpp` BINARY arm ⏳
- [ ] Use `g_emit.bb_cs_zeta` (pre-allocated by wrapper). Mirror TEXT arm logic in raw bytes. `bb_bin_t` rel32 fixups: jge ω, je ω, jmp γ, jmp ω. Reference: `bb_pat_len.cpp` BINARY arm.

### SBL-NOTANY-2, SBL-BREAK-2, SBL-SPAN-2, SBL-ARBNO-3, SBL-CAP-2 — BINARY arms ⏳
- [ ] Mode-3 BINARY parallel for the six TEXT arms. Once all green, mode-3 `--run` smoke should climb.

### SBL-BREAKX-2 — BREAKX β in TEXT arm ⏳
- [x] SBL-BREAKX-1 (SM_PAT_BREAKX opcode wiring) ✅ `7c834dea`
- [x] SBL-BREAKX-3 (TT_BREAKX case in lower_pat_dcg.c::build_node) ✅ `da2bc106`
- [ ] BREAKX β rescan in `bb_pat_break.cpp` TEXT arm when `pBB->ival==1`. Reference deleted `rt_bb_brkx` body (git show `0206b998 -- src/runtime/rt/rt.c`). Add rung 058 to exercise it.

### SBL-ATP — `@var` cursor capture ⏳
- [ ] Add `BB_PAT_ATP` to `BB_op_t` enum in `BB.h`.
- [ ] Lowering in `lower_pat_dcg.c` for `@var`: `nd->sval=varname; nd->α=nd; nd->β=fp; nd->γ=sp; nd->ω=fp`.
- [ ] `bb_exec.c case BB_PAT_ATP`: α writes Δ as int DESCR to varname via NV_SET; return γ. β: return ω.
- [ ] Create `bb_pat_atp.cpp` template + emit_core dispatch. α: `call rt_nv_set_int@PLT(varname, Δ); jmp γ`. β: `jmp ω`.

### SBL-LOWER-CLEANUP ⏳
- [ ] Delete `lower_subj_pat_split` and inline duplicate at lower.c:1750 once Snocone confirmed not using them (check `lower.c:1655`).

### SBL-VERIFY-1, SBL-VERIFY-2 — corpus climb ⏳
- [ ] After all BINARY arms + SBL-ATP + SBL-DCG-DEFER-M4: target ≥260/280 broad corpus.

### SBL-SM-BINARY (HQ-track) ⏳
`sm_pat_nullary.cpp` BINARY arm embeds emitter-process `rt_pat_*` function pointer as imm64 → violates Invariant-8 (MEDIUM_BINARY must not embed emitter-process pointers). Fix: call `rt_pat_*@PLT` directly. Track as `SM-BINARY-PAT-FIX` in GOAL-HEADQUARTERS.

### Pre-existing m2 oracle gaps (audit-only) ⏳
Rungs 044/045/046/048/052/054/055/056/057 fail in m2 too. `bb_exec.c` doesn't implement what the rung suite oracle expects for POS/RPOS/TAB/REM/star_deref/fail_builtin. Separate session.

---

## Completed (summary)

**Templates with x86 TEXT arms filled:**
LIT, ARB, LEN, POS/RPOS, TAB/RTAB, REM, ALT, CAT, FENCE, ABORT, EPS, FAIL — pre-existing
ANY, NOTANY, BREAK (plain), SPAN, ARBNO, CAPTURE — this work
DEFER — SBL-DCG-DEFER `2b68dc44`

**Runtime translators:**
- `patnd_to_bb_graph()` in `lower_pat_dcg.c` — runtime PATND_t→BB_graph_t parallel to `BB_lower_pat` (AST→BB). SBL-DCG-DEFER-M4 partial `954236f5`. Wired into `bb_exec.c case BB_PAT_DEFER` DT_P branch; `stmt_exec.c` wiring still pending.

**Driver-level fixes (this work):**
- FLAT-DRIVER α-LABEL placement: `emit_label_define_bb(&lbl_α)` moved before XA_FLAT_PROLOGUE in `codegen_flat_body` (was emitting `lea r10,[rip+Δ]` past the entry label → r10 held garbage).
- PAT_LIT/REFNAME/USERCALL GAS macro-arg bug in `sm_pat_anchors.cpp` (annotation must be `#` comment, not positional arg).
- Nested-ALT EP_RESET bug in `flat_drive_alt` (+ defensive same in `flat_drive_cat`).
- Grammar fix in `opt_subject`: statement-level `S P` produces TT_SCAN at parse time (was bleeding into generic TT_SEQ, forcing splitter heuristic).
- Removed ASSIGN_IMM/COND from `lower_flat_invariant` exclusion at `emit_sm.c:781` (unlocks inline capture emit).

**Infrastructure:**
- `rt_cap_assign(varname, base, len)` helper added to `rt.c` (pattern-building class).
- SM_PAT_BREAKX opcode (separate from SM_PAT_BREAK) wired through 12 layers.
- BB_PAT_DEFER opcode + `rt_defer_match` + XDSAR resolve.
- Pattern rung suite `test_snobol4_pat_rung_suite.sh` (rungs 038-057, M2 + M4 columns).
- bb_boxes.c C Byrd boxes deleted; rt_bb_* deleted (FACT RULE, JA-D-3).

**Recovery resource:** Hand-written original boxes live in git at `660339cd~1:src/runtime/boxes/<box>/<file>.s` (any/notany/span/brk/breakx/arbno/capture). Transcribe ABI register names to flat `[r10]`/`lbl_α/β/γ/ω` convention.

---

## Session State

```
GATE-1 SNOBOL4 smoke        = 13/13 (mode-2 7/7 + mode-3 6/6)
GATE-2 unified broker       = 26
GATE-3 broad corpus mode-4  = 175/280
GATE-4 broad corpus mode-2  = 218/280
Rung suite                  = M2=18, M4=15, SKIP=0
HEAD one4all                = 24df0702 (SBL-MODE-PURITY-1)
GATE-PK status              = stale (re-freeze deferred)
```

---

## Session 2026-05-27 (Claude Opus 4.7, continued 13) — SBL-MODE-PURITY-1 ✅

### Architectural rule (Lon directive)
**Modes do NOT silently fall back between themselves.** If the user runs `--run` (mode-3, BB_MODE_LIVE), patterns are built via `bb_build_flat`. If the user runs `--interp` (mode-2, BB_MODE_BROKERED), patterns are built via `bb_build_brokered`. A cross-mode fallback corrupts the test signal: a green test cannot be trusted to have run in the mode it claims, because a hidden fallback may have substituted a different builder behind the back of the measurement. This bit us once already with the XCAT/XOR widening attempt (continued-11) where the legacy garbage-opcode cast was accidentally compensating for unrelated bugs. The principle: **the mode the user asked for is the mode the user gets, or the run fails honestly.**

### What landed
`src/runtime/snobol4/stmt_exec.c:327`: removed the line `if (!bfn) bfn = bb_build_brokered(pp_bb);` from the `BB_MODE_LIVE` branch of the DT_P pattern dispatch in `exec_stmt`. Under LIVE, if `bb_build_flat(pp_bb)` returns NULL, `bin_done` stays 0 and the existing `!bin_done` rescue at L352 takes over (constructs an EPS — already in place). The leak: under `--run` (mode-3 / LIVE) the code was secretly building a brokered pattern whenever `bb_build_flat` failed, making `--run` a mixed-mode runner with no way for the test signal to tell which mode actually executed.

Probe instrumentation (transient, reverted before commit) confirmed: GATE-1 smoke under `--run` triggers zero fallback hits at L327; rung suite triggers zero hits. The flat path is genuinely carrying the current corpus.

### Results — all gates hold at watermark
- GATE-1 SNOBOL4 smoke: **13/13** ✓
- GATE-2 unified broker: **26** ✓
- GATE-3 broad corpus mode-4: **175/280** ✓
- GATE-4 broad corpus mode-2: **218/280** ✓
- Rung suite: **M2=18, M4=15, SKIP=0** ✓

The fix is mechanically safe because the fallback was unreachable under current corpus. The gain is structural: from now on, any `--run` test that exercises a pattern kind `bb_build_flat` can't handle will surface as a real failure rather than masking under brokered substitution.

### Remaining SBL-MODE-PURITY sub-steps
- **SBL-MODE-PURITY-2** (next): mode-gate L309/L311/L367/L377 literal-coercion paths. Currently all four sites call `bb_build_brokered` unconditionally regardless of `g_bb_mode`.
- **SBL-MODE-PURITY-3**: mode-gate L354/L361/L384 catch-alls.
- **SBL-MODE-PURITY-4**: audit `src/emitter/emit_bb.c:846-847` `pre_build_children` — per-kind brokered/flat split plus an unconditional brokered fallback.
- **SBL-MODE-PURITY-5**: audit `cache_insert(pp, root)` at L334; a brokered blob cached under LIVE mode would permanently mask subsequent flat misses for the same PATND.

**Hold SBL-ANY-2 (BINARY arm fill) and other BINARY-arm work until SBL-MODE-PURITY-2 through 5 land.** Otherwise newly-filled BINARY arms can be silently substituted by brokered behavior if any flat-build fails, defeating the purpose of the fill.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 12) — SBL-MODE3-REACTIVATE ✅

**HEAD one4all `380b4683`** (pushed).

### What landed
`src/driver/scrip.c`: removed the `[NO-SM-BB] --run: linear emitter deleted` gate. Routed `--run` through `sm_preamble` + `sm_run_with_recovery(&s2->sm, sm_interp_run)` — identical to the `--interp` branch. The gate was a stale leftover from the SB-LINEAR removal era. BB/SM/XA templates now produce MEDIUM_BINARY output via `bb_build_brokered`, so the substrate mode-3 needs is already in place (BB_MODE_BROKERED default exercises template BINARY arms during pattern matching).

### Results
- GATE-1: **7/7 → 13/13** (+6: output, concat, arith, pattern, goto_s, define all PASS under `--run`)
- GATE-2 unified broker: 25 (held)
- GATE-3 mode-4 broad: 175/280 (held)
- GATE-4 mode-2 broad: 218/280 (held)
- Rung suite: M2=18, M4=15, SKIP=0 (held)

### Note
Per Lon's session directive: "We have emitters that generate binary for templates, so not sure what's up with that." The gate was failing closed on capability that already existed.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 11) — XCAT/XOR widening attempted, REVERTED ⛔

**HEAD one4all `26913b08`** (unchanged — change was reverted before commit).

### Goal
Execute the explicit handoff item from continued-10: widen translator gate to XCAT/XOR composites. Previous session predicted this would lift 070-074 (XCAT(ARBNO, ...) family) without re-triggering the 146/147/152 fence regressions, by gating on "root is XCAT/XOR AND all kids are atoms-or-XARBN".

### What was attempted
`stmt_exec.c`: new `patnd_is_xlate_safe(pp)` recursive predicate. Safe set: simple atoms ∪ {XARBN, XCAT, XOR, XDSAR, XEPS, XFAIL, XABRT}. Explicitly excludes XFNCE/XNME/XFNME/XCALLCAP/XVAR/XATP/XBAL/XSUCF. `patnd_needs_xlate` extended with `(pp->kind == XCAT || pp->kind == XOR) && patnd_is_xlate_safe(pp)`.

### Results: pure regression
- GATE-3 mode-4: **175 → 164 (-11)**.
- 11 newly failed: 057_pat_fail_builtin, 068_pat_fence_fn_via_var, 109_pat_fence_via_var_seal_blocks_retry, 113_pat_fence_via_var_two_with_seal_retry, 118_pat_arbno_of_star_var_fence_seal_blocks, 119_pat_arbno_of_fence_via_var_via_outer, 129_pat_arbno_star_var_fence_with_alts, 130_pat_two_star_fence_concat_outer, 148_pat_arbno_star_var_fence_short, 149_pat_arbno_star_var_fence_outer_pre_match, 150_pat_star_var_fence_alts_no_arbno.
- 0 newly passed. The predicted wins (070-074) did NOT materialise — those tests still fail.

### Why the previous handoff's prediction was wrong
The handoff theory: XFNCE is the only regression vector, exclude it from the safe set and wins follow. Reality: even XCAT(XCHR, XFAIL) (test 057, no fence anywhere) regresses. The legacy `(BB_t*)(PATND_t*)` cast doesn't merely "misread opcodes when fence is present" — for XCAT/XOR composites it produces a garbage opcode value (XCAT=19 → BB_WHILE; XOR=20 → BB_UNTIL when cast to BB_op_t) that the broker treats as a no-op (returning success or fail-through) which **accidentally satisfies many pattern semantics that the semantically-correct translator path does not**. The translator emits proper four-port-wired BB_PAT_CAT/BB_PAT_ALT chains, but the brokered-blob execution of those chains diverges from what the legacy cast accidentally did. The wins in 070-074 require a different mechanism — likely XDSAR runtime deref handling in the brokered path, not gate widening.

### Action taken
`git checkout src/runtime/snobol4/stmt_exec.c` to revert. All four gates re-verified against watermark post-revert: GATE-1 7/7, GATE-2 25, GATE-3 175/280, GATE-4 218/280, M2=18 M4=15.

### Forward guidance for next session
1. **Do NOT retry naive XCAT/XOR gate widening.** The "exclude XFNCE" heuristic is insufficient; non-fence composites also regress because of the garbage-opcode compensation effect. Any XCAT/XOR widening must come WITH a corresponding fix to the brokered-blob execution of XCAT/XOR chains, not as a gate-only change.
2. **Higher-confidence next steps:**
   - **SBL-ANY-2** (and SBL-NOTANY-2 / SBL-BREAK-2 / SBL-SPAN-2 / SBL-ARBNO-3 / SBL-CAP-2) — fill the BINARY arms. Currently each is `bytes(1, "\xE9") + u32le(0) + bytes(1, "\xE9") + u32le(0)` (2 stub jumps). The TEXT arms are correct and serve as the spec. Reference templates with filled BINARY arms: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp` (all use `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing the offset of each rel32). Caveat: mode-3 `--run` currently returns `[NO-SM-BB] --run: linear emitter deleted (FACT RULE); use --interp until templates land`, so BINARY arms are dormant from the user-facing side. They will not move GATE numbers in this state — pure infrastructure prep for mode-3 reactivation. The mode-2 brokered path also exercises them via `bb_build_brokered → EMIT_BINARY_BROKERED`, but the C oracle in `bb_exec.c case BB_PAT_*` may be the path actually consulted (var-stored ANY probe returned correct `"a"` despite the stub BINARY arm — confirms the brokered blob is either not taken on this path or its failure is masked).
   - **Inline-path ARBNO(NOTANY) divergence** (still open from continued-10): `s ARBNO(NOTANY("'")) . m` returns m=`"abc"` inline but m=`""` via var. SPITBOL says m=`""` for both. Audit inline lowering's anchoring semantics — different code path than var-stored.
3. **SBL-G-2** (re-freeze GATE-PK) remains stale bookkeeping; low-leverage but unblocks per-kind regression detection going forward.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7



**HEAD one4all `26913b08`** (pushed).

### What landed
- `stmt_exec.c`: new static `patnd_is_simple_atom()` and `patnd_needs_xlate()` helpers (union of `patnd_contains_arbno || patnd_is_simple_atom`). Single-atom PATND root kinds — XCHR, XSPNC, XBRKC, XBRKX, XANYC, XNNYC, XLNTH, XPOSI, XRPSI, XTB, XRTB, XFARB, XSTAR — now route through `patnd_to_bb_graph` instead of the broken legacy cast. Both call-sites (`BB_MODE_LIVE`, `BB_MODE_BROKERED/DRIVER`) updated.

### Results
- GATE-3 mode-4: 173 → **175** (+2). Restored Qize_driver. Added W02_seq_basic, W02_seq_nested.
- GATE-4 mode-2: 218 (unchanged).
- Rung suite: M2=18, M4=15 (unchanged).
- GATE-1: 7/7. GATE-2: 24. All clean.

### Investigation findings
- Probe `pat = NOTANY("'"); s = 'abc'; s pat . m` → "no match" in both baseline and post-fix. SPITBOL gives `match:[a]`. **Pre-existing bug** in scrip's brokered-blob path for single-atom var patterns — bug survives both the legacy cast (opcode misread → fail) and the translator (correct codegen, but broker still reports `ticks=0`). Root cause is deeper in the broker/blob-wiring, not the cast or translator. Out of scope.
- Probe `pat = ARBNO(NOTANY("'")); s = 'abc'; s pat . m` → m="" both in scrip and SPITBOL — **the post-fix output now matches the oracle**. The original "SBL-ARBNO-NOTANY-CORRECTNESS" framing was based on a wrong mental oracle; what is actually anomalous is that **inline** `s ARBNO(NOTANY("'")) . m` returns m="abc" in scrip — diverging from SPITBOL. That's a separate inline-path bug.

### Not done — handoff
1. **Investigate inline-path divergence:** `s ARBNO(NOTANY("'")) . m` returns m="abc" inline but m="" via var. SPITBOL says m="" for both. The inline path uses a different lowering (probably the AST-driven `BB_lower_pat`); audit its anchoring semantics.
2. **Widen translator gate to XCAT/XOR composites:** This would likely lift more broad-corpus tests (the 070-074 family includes XCAT(ARBNO, ...)). Carefully — the 6 fence/capture regressions originally came from XFNCE/XFNME composites. The right wedge may be: `patnd_contains_arbno(any subtree) || (root is XCAT/XOR AND all kids are atoms-or-XARBN)`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 9) — SBL-DCG-DEFER-M4 stmt_exec wiring + SBL-ARBNO-COUNTER-RESET ✅

**HEAD one4all** = this commit. Rebased onto LFJ-1b (`e5eb34b0`) cleanly.

### What landed
- `scrip_ir.c bb_reset()`: one-line guard — `if (nd->t != BB_PAT_ARBNO) nd->counter = 0;`. Preserves the `bb_arbno_state_t*` aux pointer that ARBNO stashes in counter. NOT touching BB_PROC_GEN/BB_PL_SEQ/BB_CHOICE here (Prolog kinds; out of scope for SNOBOL4 goal).
- `stmt_exec.c`: `#include "lower_pat_dcg.h"`; new static helper `patnd_contains_arbno(const PATND_t *)`; both `BB_MODE_LIVE` (line ~292) and `BB_MODE_BROKERED/DRIVER` (line ~316) DT_P branches now do `int needs_xlate = patnd_contains_arbno(pp); BB_graph_t *pp_cfg = needs_xlate ? patnd_to_bb_graph(pp) : NULL; BB_t *pp_bb = (pp_cfg && pp_cfg->entry) ? pp_cfg->entry : (BB_t *)pp;` then pass `pp_bb` to `bb_build_flat/brokered` instead of the raw `(BB_t*)PATND_t*` cast.

### Results
- Rung suite M2: 16 → 18 (rungs 052_pat_arbno, 054_pat_arbno_alt newly pass)
- Mode-2 broad corpus: 210 → 218 (+8: 052, 054, 070, 075, 116, 142, W04_arbno_basic, W04_arbno_backtrack, W04_arbno_zero — minus the single mode-2 carryover)
- Mode-4 broad corpus: 174 → 173 (-1 Qize_driver — see follow-up below)
- GATE-1 7/7, GATE-2 24, rungs M4=15 — all unchanged

### Why the translator path is narrowed
First attempt: unconditionally route every DT_P PATND through `patnd_to_bb_graph`. Mode-2 broad corpus 210 → 211 (+1 net) but composition was +6 ARBNO / -6 fence/capture/func (146/147/152/1011/1013/1017). Conclusion: the legacy `(BB_t*)(PATND_t*)` cast misreads opcodes but happened to compensate for unrelated bugs in non-ARBNO paths. Narrowing to `patnd_contains_arbno(pp)` keeps the 8 ARBNO wins clean.

### Known follow-up — SBL-ARBNO-NOTANY-CORRECTNESS
`ARBNO(NOTANY(...))` against a fully-non-matching subject yields empty match (`m=""`) instead of greedy full consumption. Probe `pat = ARBNO(NOTANY("'")); s = 'abc'; s pat . m` → m="" (oracle says "abc"). Affects Qize_driver in GATE-3 mode-4. Likely cause: `bb_exec.c case BB_PAT_ARBNO` loop semantics or `build_patnd(inner_blk, ..., NULL, NULL)` inner sub-graph success-port wiring. Carve as new rung; not in scope for SBL-DCG-DEFER-M4.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 8) — SBL-DCG-DEFER-M4 partial ✅

**HEAD one4all `954236f5`** (pushed). .github pruned 949→223 lines this session.

### What landed
- `patnd_to_bb_graph()` translator in `lower_pat_dcg.c` (~170 LOC). Parallel to `BB_lower_pat` (AST→BB) but consumes PATND_t. Handles 22 PATND kinds; returns NULL on XVAR/XBAL/XATP/XCALLCAP/XSUCF for legacy fallback. Forward decl in `lower_pat_dcg.h`.
- `bb_exec.c case BB_PAT_DEFER` DT_P branch: tries translator+`bb_exec_pat` first, falls back to legacy `exec_stmt` on NULL.
- XEPS mapped to `BB_PAT_LIT("")` since `BB_EPS` enumerator doesn't exist in `BB.h`.

### Results
- Rung suite M2: 15 → 16 (+1, rung 048 REM newly passing)
- M4 unchanged (mode-4 emits compiled x86; this fix is mode-2 only)
- GATE-1/2/3 all unchanged. Zero regressions.

### Not done — handoff for next session
1. **stmt_exec.c DT_P branch wiring.** More invasive: `root.fn` is fed to `bb_broker(root, bb_scan, scan_body_fn_u9, &scan_res)` at `stmt_exec.c:367`, which orchestrates the scan loop and capture-recording callback. Intercepting cleanly requires either (a) a parallel scan loop built on `bb_exec_pat`, or (b) a thin `bb_box_fn` wrapper that hides a translated graph behind the existing broker API. Either way, must reproduce the `match_start`/`match_end` semantics that `scan_body_fn_u9` records. This is where the goal-file's "+15 broad-corpus" tests live (070-074, 105-117).

2. **Pre-existing bug: `SBL-ARBNO-COUNTER-RESET`.** `scrip_ir.c:114` `bb_reset()` blindly zeros `nd->counter` for every node. BB_PAT_ARBNO stores its `bb_arbno_state_t*` aux pointer in `nd->counter` — wiped on every `bb_exec_once`. This is why rungs 052/054 fail M2 with empty ARBNO output (the inner sub-graph pointer becomes NULL after the first reset). Same affects BB_PROC_GEN, BB_PL_SEQ, BB_CHOICE which also use counter as aux ptr. Fix: kind-aware reset (skip counter clear for kinds with aux-ptr semantics). Out of scope this session — unblocks the ARBNO(*var) corpus family (070-074) once combined with stmt_exec.c wiring.

3. **One4all rebased onto `0ed7ace3`** (mid-session ICON LFJ-1a-vi push) cleanly; build green; gates unchanged. No conflict in pattern subsystem.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- PATND legacy: `src/runtime/stmt_exec.c exec_stmt` DT_P branch
- Pattern-building runtime helpers: `src/runtime/rt.c rt_pat_*` (29 fns; called @PLT from templates)

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
