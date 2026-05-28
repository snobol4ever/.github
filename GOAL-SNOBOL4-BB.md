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
- [x] **SBL-MODE-PURITY-2**: Mode-gate L309/L311/L367/L377 literal-coercion paths. Under LIVE call `bb_build_flat`; under BROKERED call `bb_build_brokered`. The literal-coercion EPS rescues (L311 / `!bin_done` paths) also become mode-gated. **DONE 2026-05-27 (Opus 4.7, continued 13):** new helper `bb_build_pure_mode(BB_t *nd)` in `src/emitter/emit_bb.c` dispatches on g_bb_mode without fallback. All four coercion sites in stmt_exec.c (DVAR_α DT_P/DT_S, exec_stmt XDSAR-coerce, exec_stmt DT_S literal) now call through it.
- [x] **SBL-MODE-PURITY-3**: Mode-gate L354 / L361 / L384 catch-alls. **DONE 2026-05-27 (Opus 4.7, continued 13):** every eps rescue removed. On builder NULL, `root.fn = NULL`; `bb_broker` (line 11) returns 0 cleanly on NULL fn; `exec_stmt` returns 0 cleanly. Honest failure path. Silent eps substitution was the same class of signal corruption as cross-mode fallback — a failed build reported zero-width "match" success.
- [x] **SBL-MODE-PURITY-4**: Fix emit_bb.c:846-847. Per-node-kind builder split is arguably correct (some kinds genuinely need the brokered ABI for child recursion) but the L847 fallback is unconditional and must go. Investigate whether the per-kind split is intentional architecture or another latent leak. **DONE 2026-05-27 (Opus 4.7, continued 13):** L847 `if (!fn) fn = bb_build_brokered(ch);` removed. Per-kind split retained (ARBNO/ASSIGN_* → brokered, CALLOUT → flat) because it reflects ABI requirements at the child consumer (ARBNO calls into child via broker; CALLOUT splices child slab into flat-driver). On failure, NULL is cached → caller surfaces honestly.
- [x] **SBL-MODE-PURITY-5**: Audit any cache_insert path (L334) that may cache a brokered blob under LIVE mode. The cache must be mode-tagged or cleared on mode transitions, or the cache itself becomes a fallback vector. **DONE 2026-05-27 (Opus 4.7, continued 13):** verified by construction. With PURITY-1 landed, the LIVE branch only writes flat-built blobs to `root` before `cache_insert(pp, root)` at L327. `g_bb_mode` is fixed once by the driver at startup; no mid-process mode transitions; `cache_reset` is only called from `exec_stmt_pool_reset` between sessions. Cache cannot accumulate cross-mode blobs in one execution.

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

### SBL-ANY-2 — Fill `bb_pat_any.cpp` BINARY arm ✅ (Opus 4.7, continued 15, 2026-05-27)
- [x] 104-byte BINARY arm landed, mirrors TEXT arm byte-for-byte. Pattern after `bb_lit.cpp` (TEMPLATE_ADDR_SIGMA/SIGLEN, `bytes()+u32le()+u64le()`, `bb_bin_t` site list). 5 sites: jge ω@17, je ω@72, jmp γ@86, β label-define@90, jmp ω@100. See SBL-ANY-2-DISPATCH-TRACE section for the dispatch picture.
- [x] **SBL-ANY-2-DISPATCH-TRACE ✅** (see below). Investigation found the BINARY arm is exercised ONLY by the mode-4 *runtime* path (compiled binary executing pattern stmt → rt_match_variant → exec_stmt → bb_build_brokered → walk_bb_flat → bb_pat_any). Mode-2/-3 `--interp`/`--run` and mode-4 emit phase do NOT exercise it.

### SBL-NOTANY-2, SBL-BREAK-2, SBL-SPAN-2, SBL-ARBNO-3, SBL-CAP-2 — BINARY arms ⏳
- [ ] Mode-3 BINARY parallel for the six TEXT arms. Once all green, mode-3 `--run` smoke should climb.
- **Scope clarified (continued-15, SBL-ANY-2-DISPATCH-TRACE):** these BINARY arms are exercised ONLY by the runtime-PATND mode-4 path (compiled binary → `rt_match_variant` → `exec_stmt` → `bb_build_brokered/flat` → templates). Mode-2/-3 `--interp`/`--run` use the C oracle (`bb_exec.c`); mode-4 emit phase uses TEXT arms. Verify each fill with a runtime-PATND probe (template in continued-15 session notes — probe7.sno shape).

### SBL-XNME-XLATE — translator coverage for capture wrappers ⏳ (carved by continued-15)
- [ ] Extend `patnd_needs_xlate` (`stmt_exec.c:255`) and/or `patnd_to_bb_graph` (`lower_pat_dcg.c`) to cover XNME and XFNME (the conditional and immediate capture wrappers — `PAT . VAR` and `PAT $ VAR`). Currently XNME falls through to the legacy `(BB_t *)pp` cast; XNME=23 in XKIND_t collides with BB_ALT=23 in BB_op_t (NOT BB_PAT_ALT), `walk_bb_flat` hits `default:`, emits a 2-jump fail stub. Match always fails under mode-4 runtime-PATND.
- [ ] Wedge probe: `PAT = ANY('cab'); S = 'xyzabcdef'; S PAT . M; OUTPUT = "M=" M`. Pre-fix mode-4 prints `M=` empty; oracle and mode-2/-3 print `M=a`. Carve as rung 058.
- [ ] **High risk:** continued-9/10/11 documented that translator-gate widening breaks fence/capture/func tests because legacy-cast garbage opcodes accidentally satisfy unrelated semantics. XNME has `nchildren≥1` and `var` field; `lower_pat_dcg.c:490 case XNME` already exists and produces `BB_PAT_ASSIGN_COND` with proper four-port wiring. The gate widening should be staged: first run the full broad-corpus FAIL list pre-widening, then widen, then diff. Accept only widenings that net positive without losing previously-green tests.

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
GATE-2 unified broker       = 28
GATE-3 broad corpus mode-4  = 175/280
GATE-4 broad corpus mode-2  = 238/280
Rung suite                  = M2=19, M4=15, SKIP=0
HEAD one4all                = 3b78f297 (SBL-ANY-2 BINARY arm)
GATE-PK status              = stale (re-freeze deferred)
```

---

## Session 2026-05-27 (Claude Opus 4.7, continued 15) — SBL-ANY-2 BINARY arm ✅ + SBL-ANY-2-DISPATCH-TRACE ✅

### What landed
`src/emitter/BB_templates/bb_pat_any.cpp`: replaced the 2-jump stub BINARY arm (`bin = { {1, 2}, {ω, γ}, {false, false} }` emitting only `jmp ω`) with a 104-byte fill mirroring the TEXT arm byte-for-byte. Pattern follows `bb_lit.cpp` exactly: `TEMPLATE_ADDR_SIGMA/SIGLEN` macros for runtime globals, `(uint64_t)(uintptr_t)cs` for cset string address, `const char *(*fp)(const char *, int) = strchr` trick for strchr address (C++ overload resolution), `bytes() + u32le() + u64le()` concat, `bb_bin_t` site list. Five sites: `{17, 72, 86, 90, 100}` with labels `{ω, ω, γ, β, ω}` and is_def `{false, false, false, true, false}`. Added `<cstring>` + `<cstdint>` includes.

### Dispatch trace — the answer to SBL-ANY-2-DISPATCH-TRACE

| Mode | Pattern path | BINARY arm? | TEXT arm? |
|------|-------------|-------------|-----------|
| `--interp` / `--run` (any pattern, AST or runtime) | `SM_EXEC_STMT` → `bb_exec_pat` → `bb_exec_once` → C oracle in `bb_exec.c case BB_PAT_*` | No | No |
| `--compile` emit phase | `codegen_sm_x86` → `walk_bb_pattern_blobs` → `codegen_flat_build` → `walk_bb_flat` → FILL → `walk_bb_node` → `bb_pat_any` template (TEXT_MODE set at `emit_sm.c:936`) | No | **Yes** |
| `--compile` *runtime* (compiled binary executing) | compiled binary calls `rt_match_variant` (in libscrip_rt.so) → `exec_stmt` → for DT_P runtime PATND, `patnd_needs_xlate` gate → `patnd_to_bb_graph` translator → `bb_build_brokered` (g_bb_mode=BB_MODE_BROKERED via rt_init at `rt.c:335`) → `walk_bb_flat` → `bb_pat_any` template | **Yes** | No |

This resolves continued-14's open puzzle ("investigate why 042-048 mode-4 rungs pass despite stub BINARY arms"): the TEXT arms carry mode-4 emit-time output; the BINARY arms only matter for the narrow runtime-PATND-under-compiled-mode-4 path, which current corpus rungs don't exercise.

`sm_interp.c:582 SM_EXEC_STMT`: when `pat_bb` (from `bb_table[ins->a[2].i]`, set by `SM_seq_bb_add` during AST→BB lowering at `lower.c:692`) is non-NULL, dispatch is `bb_exec_pat` (C oracle). When NULL (rare — `BB_lower_pat` failed at compile time), falls through to `exec_stmt`. For runtime-constructed patterns (`PAT = ANY('cab'); S PAT . M`), `pat_bb` is non-NULL (lowering compiled the outer wrapper) but the inner runtime PATND_t resolves at runtime via `BB_PAT_DEFER` C-oracle path, never reaching templates.

`rt_match_variant → exec_stmt` is invoked from compiled x86 (via the `EXEC_STMT_VARIANT` GAS macro emitted by `xa_exec_stmt_blob.cpp`). That's how mode-4 binaries get into `exec_stmt` and from there into `bb_build_brokered/flat → templates`.

### Verification — probe7.sno (runtime-PATND mode-4 path, byte-identical to SPITBOL oracle)

```snobol
	PAT = ANY('cab')
	S = 'xyzabcdef'
	S PAT					:F(NOMATCH)
	OUTPUT = "matched"			:(THEEND)
NOMATCH OUTPUT = "no match"
THEEND
END
```

| Path | Pre-fill | Post-fill | Oracle |
|------|----------|-----------|--------|
| `sbl -b probe7.sno` (SPITBOL) | — | — | `matched` |
| `scrip --interp probe7.sno` | `matched` | `matched` (C oracle, unchanged) | match |
| `scrip --compile probe7.sno` + gcc link + run | `no match` (stub jmp ω) | **`matched`** | match |

The corresponding inline-AST control (`S ANY('cab')`) continues to print `matched` under mode-4 via the TEXT-arm path (unchanged). Literal-pattern control (`PAT = 'ab'; S PAT`) confirms `bb_lit` BINARY arm + the runtime-PATND→brokered-blob path is end-to-end functional.

### Investigation methodology

Per Lon's continued-13C directive (do not commit code we cannot prove ran), the BINARY-arm fill was bracketed by transient stderr probes in the `bb_pat_any` C wrapper: (a) entry-trace to confirm the template is invoked at runtime, and (b) hexdump of the 104 emitted bytes + sites to confirm `bb_emit_asm_result` interprets the `bb_bin_t` correctly. Both probes fired with the expected output (medium=BINARY, sval='cab', bytes-and-sites byte-identical to the hand-computed layout). Probes reverted before commit; only the fill itself ships.

Initial test (`probe1.sno` with capture `S PAT . M`) gave `M=` empty post-fill — the stderr probe revealed `bb_pat_any` was NOT invoked for that case. Root cause: the capture wrapper `M . S` builds an XNME PATND at root. `patnd_needs_xlate` (`stmt_exec.c:255`) does not include XNME → falls through to the legacy `(BB_t *)pp` cast. XNME=23 in PATND enum collides with BB_ALT=23 in BB_op_t (NOT BB_PAT_ALT). `walk_bb_flat` has no `case BB_ALT:` → hits `default:` arm emitting a 2-jump fail stub. Match always fails. This is a SEPARATE bug (see SBL-XNME-XLATE below), unrelated to `bb_pat_any` BINARY arm correctness.

### Gates — all hold at watermark

| Gate | Before | After |
|------|--------|-------|
| GATE-1 SNOBOL4 smoke   | 13/13 | 13/13 ✓ |
| GATE-2 unified broker  | 28    | 28 ✓ |
| GATE-3 mode-4 broad    | 175   | 175 ✓ |
| GATE-4 mode-2 broad    | 238   | 238 ✓ |
| Rung suite M2          | 19    | 19 ✓ |
| Rung suite M4          | 15    | 15 ✓ |

No regressions. No gate movement either — expected, because the rung suite and broad corpus exercise patterns whose `BB_lower_pat` succeeds at compile time (TEXT-arm path) rather than runtime-constructed PATND patterns. probe7.sno would be a candidate new rung to capture the runtime-PATND mode-4 lift formally.

### Next-session priorities

1. **SBL-XNME-XLATE** (newly carved): extend `patnd_needs_xlate` to include XNME/XFNME (the capture wrappers `PAT . M` and `PAT $ M`) and/or extend the translator to cover them at the runtime-PATND level. Continued-9/10/11 documented that gate-widening is high-risk because legacy-cast accidents compensate for unrelated bugs — must be staged with rung-level proofs. Wedge: probe1.sno (`PAT = ANY('cab'); S PAT . M; OUTPUT = "M=" M`) currently prints `M=` under mode-4 (vs oracle `M=a`); the same probe under `--interp`/`--run` is correct via the C-oracle path. Carve as rung 058 (or appropriate next slot).

2. **SBL-NOTANY-2 / SBL-SPAN-2 / SBL-BREAK-2 / SBL-ARBNO-3 / SBL-CAP-2** — fill remaining BINARY arms. Same template as SBL-ANY-2: mirror TEXT arm byte-for-byte, use `TEMPLATE_ADDR_*` macros, follow `bb_lit.cpp` pattern. Each fill should be verified with a runtime-PATND probe (analogous to probe7) before commit.

3. **SBL-G-2** (re-freeze GATE-PK) — stale bookkeeping; low-leverage but unblocks per-kind regression detection going forward.

4. **probe7.sno → rung 058**: formalize the runtime-PATND-under-mode-4 test pattern as a rung. Without a rung exercising this path, future regressions to BINARY-arm correctness will be invisible to the gate signal.

### Reusable probe template (probe7.sno) for verifying other BINARY-arm fills

```snobol
	PAT = ANY('cab')          ; ← change to NOTANY / SPAN / BREAK / etc.
	S = 'xyzabcdef'           ; ← change subject to match the predicate
	S PAT					:F(NOMATCH)
	OUTPUT = "matched"			:(THEEND)
NOMATCH OUTPUT = "no match"
THEEND
END
```

Test cycle:
```bash
./scrip --compile probe7.sno > /tmp/p.s
gcc -c /tmp/p.s -o /tmp/p.o
gcc /tmp/p.o -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$(pwd)/out -o /tmp/p.bin
/tmp/p.bin               # should print "matched"
```

Pre-fill: prints `no match` (or empty). Post-fill: prints `matched`. Cross-check against `/home/claude/x64/bin/sbl -b probe7.sno`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 14) — SBL-ANY-2-CORRECTNESS ✅ (one4all `3eb09ba0`)

### The dispatch trace landed the bug, not the BINARY arm

Continued-13C left the next-session task as **SBL-ANY-2-DISPATCH-TRACE**: map the actual dispatch path before filling any BINARY arm, because probes had shown `bb_pat_any` and `exec_stmt` were never called for `S PAT . M` under `--interp`. Tracing this session revealed the dispatch path AND a pair of latent bugs that, fixed, climbed mode-2 broad corpus by **+20** without touching any BINARY arm.

### Dispatch path (the answer to SBL-ANY-2-DISPATCH-TRACE)

For `S PAT . M` under `--interp`:

```
sm_interp.c:582 SM_EXEC_STMT
  → pat_bb = g_stage2.sm.bb_table[ins->a[2].i]   (precompiled BB_graph_t*)
  → bb_exec_pat(pat_bb, "S", &subj_d, NULL, 0)
      → outer position-scan loop (start = 0..Ω if !kw_anchor)
      → bb_reset(cfg); bb_exec_once(cfg)
        → bb_exec_node walking by ports
        → case BB_PAT_ASSIGN_COND   (the '. M' capture, entry node, t=42)
          → α-port
          → case BB_PAT_DEFER       (the 'PAT' var-ref)
            → NV_GET("PAT") → val.v == DT_P → patnd_to_bb_graph(val.p)
            → bb_exec_once(sub_bb)   [post-fix; was bb_exec_pat(...) pre-fix]
              → case BB_PAT_ANY in bb_exec.c   (the C oracle)
```

The template file `bb_pat_any.cpp` is **NOT exercised** under `--interp` for var-deref patterns. The C oracle in `bb_exec.c case BB_PAT_ANY` is the executor. This explains why continued-13C's BINARY-arm probes saw zero hits on `bb_pat_any`.

### Bug #1 — DESCR_t union clobber (bb_exec.c:2378, rt.c:560)

```c
DESCR_t sub_d; sub_d.v = DT_S; sub_d.s = (char *)sub; sub_d.slen = ...; sub_d.i = 0;
```

`.s` and `.i` share a union in `DESCR_t` (descr.h). The trailing `sub_d.i = 0` clobbered `sub_d.s` to NULL. The recursive `bb_exec_pat` then saw `Σ=NULL Σlen=9`. BB_PAT_ANY read past NULL and ran on **stale** Σ from the OUTER scope — returning the first character of `'xyzabcdef'` ('x') instead of failing or matching 'a'.

This bug was the root of `match=x`. The handoff's prior framing "pre-existing mode-independent bug in ANY" was wrong-tree — ANY's code was correct, the substrate handed it garbage.

**Fix:** designated initializer:
```c
DESCR_t sub_d = { .v = DT_S, .slen = (uint32_t)sublen, .s = (char *)sub };
```

After fix #1, `match=xyza`. Closer but still wrong.

### Bug #2 — Architectural double-scan (bb_exec.c:2382)

`BB_PAT_DEFER` was calling `bb_exec_pat(sub_bb, NULL, &sub_d, NULL, 0)` recursively for the inner sub-pattern. But `bb_exec_pat` has its OWN position-scan loop (`for start = 0..Ω`). So the inner pattern was scanning the entire sub-subject independently of the outer's position scan. With outer start=0, the inner ANY scanned 'xyzabcdef' from position 0, found 'a' at position 3, returned matched=4. M was bound to "xyza" (positions 0..4 of outer Σ).

**Fix:** replace inner call with anchored single-shot match:
```c
DESCR_t result = bb_exec_once(sub_bb);
int ok = !IS_FAIL_fn(result);
```

`bb_exec_once` walks the cfg ONCE at the current Δ=0 of the sub-Σ; no anchor scan. The OUTER `bb_exec_pat` keeps the position-scan responsibility.

After fix #2: `match=a` byte-identical to SPITBOL across all three modes.

### Validation across pattern kinds (all SPITBOL-oracle byte-identical, all three modes)

```snobol
S = 'xyzabcdef'
PAT_ANY    = ANY('cab')     ;  S PAT_ANY . MA       →  MA=a
PAT_NOTANY = NOTANY('xyz')  ;  S PAT_NOTANY . MN    →  MN=a
PAT_SPAN   = SPAN('cab')    ;  S PAT_SPAN . MS      →  MS=abc
PAT_BREAK  = BREAK('c')     ;  S PAT_BREAK . MB     →  MB=xyzab
```

### Gates

| Gate | Before | After | Δ |
|------|--------|-------|---|
| GATE-1 SNOBOL4 smoke   | 13/13  | 13/13  | hold |
| GATE-2 unified broker  | 28     | 28     | hold |
| GATE-3 mode-4 broad    | 175    | 175    | hold |
| GATE-4 mode-2 broad    | 218    | **238**| **+20** |
| Rung suite M2          | 18     | **19** | **+1** (053) |
| Rung suite M4          | 15     | 15     | hold |

### Two locations patched (mechanically identical bug)

- `src/lower/bb_exec.c:2378` (translator path) — fixes #1 + #2
- `src/runtime/rt/rt.c:560` (legacy `rt_pat_*` runtime helper called from emitted x86) — fixes #1 only (this site already called `exec_stmt` not `bb_exec_pat`, so no double-scan to undo)

### Architectural takeaway

The pre-existing union-clobber pattern in `DESCR_t` literal-init was a latent landmine. The designated-initializer form is structurally immune. Any future site doing similar inline DESCR_t construction should use designated init. There is no remaining occurrence of the `sub_d; sub_d.x = ...` pattern with `.i = 0` after `.s = ...` in the SNOBOL4 dispatch surface (grep clean post-fix).

### Next-session priority

- **SBL-ANY-2 BINARY arm** (continued-13C reusable artifact still valid for mode-3 `--run` flat path): the BINARY arm of `bb_pat_any.cpp` is still a stub. But now we know it's exercised only via the template path under `--run` (mode-3) or `--compile` (mode-4), NOT under `--interp`. Mode-2 var-deref patterns are now correct via the C oracle. Filling the BINARY arm is still work, but its scope is narrower than continued-13C assumed: it doesn't unblock `--interp` (already green); it unblocks `--run` of compiled patterns.
- **SBL-NOTANY-2, SBL-BREAK-2, SBL-SPAN-2, SBL-ARBNO-3, SBL-CAP-2** BINARY arms — same scope clarification: mode-3/mode-4 only.
- **Investigate why 042/044/045/046/047/048 mode-4 rungs pass** despite stub BINARY arms in their templates — there is some other path producing correct mode-4 output for these (inline-pattern lowering? AST-driven BB_lower_pat?). Mapping that path is the prereq for confidently filling the BINARY arms knowing what they replace.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 13C) — SBL-ANY-2 attempted, NOT COMMITTED ⛔ (investigation findings)

**HEAD one4all** unchanged at `e7e7bd63` (PURITY-2/3/4). No commit landed this segment.

### Goal
Fill `bb_pat_any.cpp` BINARY arm. With PURITY-1..5 landed, the hold on BINARY-arm work is lifted — the signal is clean enough that a real BINARY-arm failure would surface honestly.

### What was attempted
Wrote a 104-byte BINARY arm in `bb_pat_any_str` that mirrors the TEXT arm byte-for-byte. Encoding verified against GAS disassembly of an equivalent `.s` file. `bb_bin_t.sites` = `{17, 72, 86, 90, 100}` with labels `{ω, ω, γ, β, ω}` and is_def `{false, false, false, true, false}`. Uses `movabs` for in-process absolute addresses of Σ/Σlen/cset_chars/strchr (per `bb_upto.cpp` precedent — all valid because mode-2/mode-3 brokered blobs run in the emitter process).

### Why NOT committed
**Probe instrumentation proved `bb_pat_any` is never called for `S PAT . M` patterns under `--interp --bb=brokered`.** Worse, `exec_stmt` itself is never entered for these patterns — the entry-point fprintf (above all branches in stmt_exec.c::exec_stmt) emitted zero output across multiple runs.

Per the architectural rule Lon established this session: *do not commit code we cannot prove ran*. Same epistemic hazard as cross-mode fallback — a green test that runs different code than we think corrupts the signal. So the BINARY arm fill is reverted along with all probes.

### Diagnostic test case
```snobol
        S = 'xyzabcdef'
        PAT = ANY('cab')
        S PAT . M
        OUTPUT = "match=" M
END
```
SPITBOL oracle: `match=a` (first char in 'cab' found in S, at position 3).
Current scrip: `match=x` under `--interp`, `--interp --bb=brokered`, `--interp --bb=wired`, AND `--run`. ALL modes wrong.

This is a **pre-existing, mode-independent bug** — not introduced by PURITY work; PURITY runs (this session pre-attempt) had identical FAIL list to baseline.

### Where the actual dispatch lives
`grep SM_EXEC_STMT src/processor/sm_interp.c` → hit at line 582. This is the SM-level pattern-statement handler that processes `S PAT . M`. It bypasses `exec_stmt` entirely under `--interp`. The dispatch chain to investigate next session is approximately:
- `sm_interp_run` walks SM instructions
- `case SM_EXEC_STMT` at sm_interp.c:582 — figure out what it does for DT_P pat operand
- Likely path: builds a brokered blob via `bb_build_brokered` and invokes `bb_broker` directly, NOT via `exec_stmt`
- Find which BB template ends up being walked; it may be a different code path through `walk_bb_node` that wraps BB_PAT_ANY differently, OR may be hitting a stub elsewhere

### What was NOT learned
- Whether the OLD ANY BINARY-arm stub (`E9 0 E9 0`) was reaching the JIT'd blob path at all, or whether the `match=x` was coming from somewhere else entirely (e.g., a separate inline-pattern lowering that uses TEXT-arm-derived bytes via `codegen_flat_build` → ldscript → some other broker entry).
- Whether the `xa_flat_epilogue` success-half (which emits the spec-build code) is what was producing `match=x` for the old stub fall-through case.

### Next-session strategy
1. **Trace `SM_EXEC_STMT` in sm_interp.c:582** first. Place a printf there. Confirm which path the test case takes.
2. **THEN** instrument `bb_build_brokered` to see what BB_PAT_* kinds get JIT'd.
3. **THEN** instrument `bb_pat_any` (the wrapper, not the body) to confirm whether MY new BINARY arm bytes would even be reached.
4. Only after that triangle is mapped: re-apply the SBL-ANY-2 BINARY arm fill and re-test.

If `bb_pat_any` is truly never called under `--interp`, then **SBL-ANY-2 is misnamed** — there's some OTHER ANY implementation that handles the live brokered blob path. Find it first.

### Working set of intel from this segment
- `bb_pat_any.cpp` TEXT arm IS correct (mirrors hand-written `bb_any.s` from git `660339cd~1`).
- BINARY-arm encoding I designed is correct (GAS-disassembly-verified against the TEXT arm).
- `bb_upto.cpp` BINARY arm is the working reference for movabs+call-indirect patterns.
- `bb_pat_len.cpp` / `bb_pat_pos.cpp` BINARY arms are working references for the rel32-fixup `bb_bin_t` pattern.
- `xa_flat.cpp` FLAT_PROLOGUE sets `r10 = &Δ`; templates read/write Δ via `[r10]`.

### Reusable artifact — bb_pat_any.cpp BINARY arm source (GAS-verified, ready to drop in after SBL-ANY-2-DISPATCH-TRACE maps the path)

Add to top of file (under existing `#include <string>`):
```cpp
#include <cstring>
#include <cstdint>
```

Inside `bb_pat_any_str` PLATFORM_X86 block, replace the stub `bin = { {1, 2}, ... }` + stub BINARY fragment with:

```cpp
        const char *cs = pBB->sval ? pBB->sval : "";
        const char *cs_label = emit_intern_str(cs);
        /* SBL-ANY-2: BINARY arm filled. Mirrors TEXT arm byte-for-byte.
         * MEDIUM_BINARY runs in-process so emitter addresses for &Σ, &Σlen, pBB->sval, strchr are valid imm64 loads.
         * Layout (104 bytes total):
         *   off  bytes                  asm
         *    0   41 8B 02               mov eax, [r10]                ; eax = Δ
         *    3   48 B9 [&Σlen u64]      movabs rcx, &Σlen
         *   13   3B 01                  cmp eax, [rcx]                ; cmp Δ, Σlen
         *   15   0F 8D [rel32]          jge lbl_ω                     ; site 17 → ω
         *   21   48 B9 [&Σ u64]         movabs rcx, &Σ
         *   31   48 8B 01               mov rax, [rcx]                ; rax = subject ptr
         *   34   49 63 0A               movsxd rcx, dword [r10]       ; rcx = Δ sign-extended
         *   37   0F B6 34 08            movzx esi, byte [rax+rcx]     ; esi = subject[Δ]
         *   41   48 BF [cs_ptr u64]     movabs rdi, &cset_chars       ; rdi = cset (1st strchr arg)
         *   51   41 52                  push r10                      ; preserve r10 across call
         *   53   48 B8 [strchr u64]     movabs rax, &strchr
         *   63   FF D0                  call rax
         *   65   41 5A                  pop r10
         *   67   48 85 C0               test rax, rax
         *   70   0F 84 [rel32]          je lbl_ω                      ; site 72 → ω (strchr NULL)
         *   76   41 8B 02               mov eax, [r10]
         *   79   83 C0 01               add eax, 1
         *   82   41 89 02               mov [r10], eax                ; Δ++
         *   85   E9 [rel32]             jmp lbl_γ                     ; site 86 → γ
         *   90   (lbl_β definition)                                   ; site 90, is_def=true
         *   90   41 8B 02               mov eax, [r10]
         *   93   83 E8 01               sub eax, 1
         *   96   41 89 02               mov [r10], eax                ; Δ--
         *   99   E9 [rel32]             jmp lbl_ω                     ; site 100 → ω
         *  104   (end)
         */
        bin = { {17, 72, 86, 90, 100},
                {_.lbl_ω_p, _.lbl_ω_p, _.lbl_γ_p, _.lbl_β_p, _.lbl_ω_p},
                {false, false, false, true, false} };
        uint64_t strchr_addr;
        { const char *(*fp)(const char *, int) = strchr; strchr_addr = (uint64_t)(uintptr_t)(void *)fp; }
        uint64_t cs_addr = (uint64_t)(uintptr_t)(const void *)cs;
        return IF(MEDIUM_MACRO_DEF, s_comment("# no macro form — ANY"))
             + IF(MEDIUM_BINARY,
                   bytes(3, "\x41\x8B\x02")                                       /*  0: mov eax,[r10]                */
                 + bytes(2, "\x48\xB9") + u64le(TEMPLATE_ADDR_SIGLEN)             /*  3: movabs rcx,&Σlen             */
                 + bytes(2, "\x3B\x01")                                           /* 13: cmp eax,[rcx]                */
                 + bytes(2, "\x0F\x8D") + u32le(0)                                /* 15: jge ω (rel32 @17)            */
                 + bytes(2, "\x48\xB9") + u64le(TEMPLATE_ADDR_SIGMA)              /* 21: movabs rcx,&Σ                */
                 + bytes(3, "\x48\x8B\x01")                                       /* 31: mov rax,[rcx]                */
                 + bytes(3, "\x49\x63\x0A")                                       /* 34: movsxd rcx,dword[r10]        */
                 + bytes(4, "\x0F\xB6\x34\x08")                                   /* 37: movzx esi,byte[rax+rcx]      */
                 + bytes(2, "\x48\xBF") + u64le(cs_addr)                          /* 41: movabs rdi,&cs               */
                 + bytes(2, "\x41\x52")                                           /* 51: push r10                     */
                 + bytes(2, "\x48\xB8") + u64le(strchr_addr)                      /* 53: movabs rax,&strchr           */
                 + bytes(2, "\xFF\xD0")                                           /* 63: call rax                     */
                 + bytes(2, "\x41\x5A")                                           /* 65: pop r10                      */
                 + bytes(3, "\x48\x85\xC0")                                       /* 67: test rax,rax                 */
                 + bytes(2, "\x0F\x84") + u32le(0)                                /* 70: je ω  (rel32 @72)            */
                 + bytes(3, "\x41\x8B\x02")                                       /* 76: mov eax,[r10]                */
                 + bytes(3, "\x83\xC0\x01")                                       /* 79: add eax,1                    */
                 + bytes(3, "\x41\x89\x02")                                       /* 82: mov [r10],eax                */
                 + bytes(1, "\xE9") + u32le(0)                                    /* 85: jmp γ (rel32 @86)            */
                                                                                  /* 90: lbl_β: (label_define)        */
                 + bytes(3, "\x41\x8B\x02")                                       /* 90: mov eax,[r10]                */
                 + bytes(3, "\x83\xE8\x01")                                       /* 93: sub eax,1                    */
                 + bytes(3, "\x41\x89\x02")                                       /* 96: mov [r10],eax                */
                 + bytes(1, "\xE9") + u32le(0))                                   /* 99: jmp ω (rel32 @100)           */
             + IF(MEDIUM_TEXT, /* … existing TEXT arm unchanged … */ std::string());
```

**Caveats for the next session:**
- The TEXT arm shown ends with `std::string()` — use the existing TEXT arm from the file verbatim (omitted here to avoid bloat).
- The C++ overload resolution for `strchr` needs the `const char *(*fp)(const char *, int) = strchr;` trick — taking the address of `strchr` directly fails with "overloaded function with no contextual type information".
- After dropping in, run `bash scripts/build_scrip.sh` then `bash scripts/test_smoke_snobol4.sh` (GATE-1 should hold at 13/13).
- ONLY AFTER SBL-ANY-2-DISPATCH-TRACE confirms `bb_pat_any` is actually being invoked, exercise with the ANY-specific probe (`PAT = ANY('cab'); 'xyzabcdef' PAT . M` should give `match=a` per SPITBOL oracle).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 13B) — SBL-MODE-PURITY-2/3/4/5 ✅

### Architectural rule (Lon directive, restated stronger)
**Modes do NOT silently fall back between themselves, AND failed builds do NOT silently substitute eps.** Both are signal corruption. A passing test must be passing through the mode it claims AND through the pattern it claims to compile.

### What landed
1. **New helper** `bb_box_fn bb_build_pure_mode(BB_t *nd)` in `src/emitter/emit_bb.c` (declared in `emit_bb.h`). Dispatches on `g_bb_mode`:
   - `BB_MODE_LIVE` → `bb_build_flat`
   - `BB_MODE_BROKERED` / `BB_MODE_DRIVER` → `bb_build_brokered`
   - Never falls back across modes. Returns NULL on failure.

2. **stmt_exec.c — all literal-coercion paths route through pure helper:**
   - `bb_deferred_var DVAR_α` DT_P coercion (was L167) → `bb_build_pure_mode`
   - `bb_deferred_var DVAR_α` DT_S coercion (was L183) → `bb_build_pure_mode`
   - `exec_stmt` XDSAR-resolved DT_S/DT_SNUL coercion (was L301) → `bb_build_pure_mode`
   - `exec_stmt` top-level DT_S literal (was L367) → `bb_build_pure_mode`

3. **stmt_exec.c — all eps rescues removed:**
   - `bb_deferred_var` DT_P build-failure rescue (was L173) → `ζ->child_fn = NULL`
   - `bb_deferred_var` else-clause empty-child rescue (was L191) → `ζ->child_fn = NULL`
   - `exec_stmt` XDSAR-coerce build-failure (was L303) → `root.fn = NULL`
   - `exec_stmt` `!bin_done` DT_P rescue (was L352) → `root.fn = NULL`
   - `exec_stmt` DT_P-with-NULL-p catch-all (was L361) → `root.fn = NULL`
   - `exec_stmt` DT_S literal build-failure (was L375) → `root.fn = NULL`
   - `exec_stmt` final catch-all (was L383) → `root.fn = NULL`

4. **emit_bb.c:847** unconditional `if (!fn) fn = bb_build_brokered(ch);` removed. Per-kind builder split retained (ARBNO/ASSIGN_* → brokered; CALLOUT → flat) because it reflects child-consumer ABI requirements, not mode dispatch.

### Safety net on the honest-failure path
When `root.fn = NULL`, `bb_broker` (line 10-11 of bb_broker.c) does `if (!root.fn) return 0;` cleanly. `exec_stmt` then sees `ticks <= 0` and falls through to `return 0` — pattern failed honestly. No segfault, no eps masquerade.

### Results — every gate held or improved at watermark
- GATE-1 SNOBOL4 smoke: **13/13** ✓
- GATE-2 unified broker: **28** (was 26 at watermark; +2 due to sibling Raku BB work — not from this change)
- GATE-3 mode-4 broad: **175/280** ✓ (FAIL list byte-identical to baseline)
- GATE-4 mode-2 broad: **218/280** ✓
- Rung suite: **M2=18, M4=15, SKIP=0** ✓

### The "expect breakage" prediction did not materialize
Per Lon's directive: "We want this change to break everything so we can see it." The breakage did not materialize. Every formerly-fallback-protected code path is genuinely unreachable under the current 280-test corpus and rung suite. The fallbacks were dead leaks — removing them exposes nothing new because nothing was hitting them.

**This is actually the desired epistemic state:** from this point on, every passing test is genuinely passing through the mode it claims, every failing test is failing for a real reason, and the corpus is the only thing that can tell us if new work introduces regressions vs. surfacing previously-hidden bugs. The signal is now clean.

### Status of SBL-ANY-2 and BINARY arm fills
The hold is lifted. SBL-ANY-2 / SBL-NOTANY-2 / SBL-BREAK-2 / SBL-SPAN-2 / SBL-ARBNO-3 / SBL-CAP-2 can now proceed safely: a failed flat-build in any of these templates will surface as honest mode-3 / mode-2 broker no-match (`root.fn = NULL` → `bb_broker` returns 0), not as a silent brokered substitute or eps zero-width success. The signal is reliable.

### Next session priority
- **SBL-ANY-2**: fill `bb_pat_any.cpp` BINARY arm. Reference `bb_upto.cpp` BINARY (which uses `movabs` for emitter-process absolute addresses + `call rax` indirect for strchr), plus `bb_pat_pos.cpp` / `bb_pat_len.cpp` for the rel32-fixup pattern via `bb_bin_t.sites`. The TEXT arm in `bb_pat_any.cpp` (already correct) is the spec; transcribe to raw bytes with `bytes()` + `u32le(0)` placeholders and a `bb_bin_t` listing the offset of every rel32 site (lbl_ω jges, lbl_ω jes, lbl_γ jmps, lbl_β define, lbl_ω final jmp).
- Then SBL-NOTANY-2 / SBL-BREAK-2 / SBL-SPAN-2 / SBL-ARBNO-3 / SBL-CAP-2 (same pattern).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

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
