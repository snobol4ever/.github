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
bash scripts/test_smoke_snobol4.sh                # GATE-1: 7/7
bash scripts/test_smoke_unified_broker.sh         # GATE-2: 24
bash scripts/test_mode4_broad_corpus_snobol4.sh   # GATE-3: ≥174/280
bash scripts/test_snobol4_pat_rung_suite.sh       # Rungs: M2=15, M4=15, SKIP=0
```

---

## Open Rungs (priority order)

### NEXT: SBL-DCG-DEFER-M4 stmt_exec.c wiring ✅ (narrowed) + SBL-ARBNO-COUNTER-RESET ✅

**Status:** Both landed (this session).

**SBL-ARBNO-COUNTER-RESET ✅:** `scrip_ir.c bb_reset()` — one-line guard `if (nd->t != BB_PAT_ARBNO) nd->counter = 0;` Preserves the `bb_arbno_state_t*` aux pointer across `bb_exec_once` calls. Rung suite M2 16 → 18 (rungs 052, 054 newly pass).

**SBL-DCG-DEFER-M4 stmt_exec.c wiring ✅ (narrowed):** Added `lower_pat_dcg.h` include + `patnd_contains_arbno()` static helper + gated translator path in both `BB_MODE_LIVE` and `BB_MODE_BROKERED/DRIVER` branches. When the PATND root tree contains XARBN anywhere, `patnd_to_bb_graph(pp)` builds a proper BB graph and `bb_build_brokered/flat` walks its `entry` (a real `BB_t*`). Else falls back to legacy cast. Mode-2 broad corpus 210 → 218 (+8: 052/054/070/075/116/142/W04_arbno_basic/backtrack/zero).

**Why narrowed:** The unconditional translator path traded 6 ARBNO wins for 6 fence/capture/func regressions (146/147/152/1011/1013/1017). Non-ARBNO PATND trees rely on the legacy cast's accidentally-benign garbage-opcode behaviour and break under the translator. XARBN-gating isolates the wins cleanly.

**Known follow-up — SBL-ARBNO-NOTANY-CORRECTNESS (NEW):** `ARBNO(NOTANY(...))` against any string yields empty match (`m=""`) where SPITBOL yields full greedy match. Probe: `pat = ARBNO(NOTANY("'")); s = 'abc'; s pat . m` → m="" (should be "abc"). Affects Qize_driver in GATE-3 mode-4 (newly segfaults; legacy path also produces wrong output, just doesn't crash). Likely in `bb_exec.c case BB_PAT_ARBNO` loop or how `lower_pat_dcg.c::build_patnd(inner_blk, ..., NULL, NULL)` wires the inner sub-graph's success-port behaviour vs `bb_exec_once` termination semantics. Out of scope for SBL-DCG-DEFER-M4; carve as its own rung.

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
GATE-1 mode-2 smoke         = 7/7
GATE-2 unified broker       = 24
GATE-3 broad corpus mode-4  = 173/280 (-1 vs prior baseline: Qize_driver newly segfaults — see SBL-ARBNO-NOTANY-CORRECTNESS below)
GATE-4 broad corpus mode-2  = 218/280 (was 210, +8 net: 052/054/070/075/116/142/W04_arbno_*)
Rung suite                  = M2=18, M4=15, SKIP=0
HEAD one4all                = (this commit)
GATE-PK status              = stale (re-freeze deferred)
```

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
