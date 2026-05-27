# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates: all primitives, modes 2/3/4

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md · GOAL-MODE4-SN4-SNOCONE.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired) → bb_exec.c (Mode 2 reference)
    → BB_templates/bb_pat_*.cpp → x86 (Modes 3/4)
```

**Three modes:**
- **Mode 2 (`--interp`):** `sm_interp.c SM_EXEC_STMT` → `bb_build_brokered` → `bb_exec_once/resume`. Correctness oracle.
- **Mode 3 (`--run`):** routes through sm_interp for SNOBOL4 pattern matching (same as Prolog AGW-1c) until `bb_pat_*.cpp` templates are complete. Do not touch.
- **Mode 4 (`--compile --target=x86`):** emitter DFS walks BB graph, emits via `bb_pat_*.cpp`. Freed by `stage2_free_bb_after_emit` after emit.

**Absolute rules (RULES.md):**
- No C Byrd boxes. No `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω.
- No AST walking in modes 2/3/4. No SM/BB walking at runtime in modes 3/4.
- Four ports = Greek letters α/β/γ/ω only. No English synonyms.
- X86 ONLY FOR NOW — IS_JVM/JS/NET/WASM arms are stubs.
- TEMPLATE-PURITY: every `_str()` body is `state → std::string`, zero `emit_text_n` inside.
- ONE x86 PRODUCER: all emission goes through template functions in `BB_templates/`.
- HQ Invariant 0: a template returning `std::string()` or stub jumps only is NOT done. Real GAS + real bytes, or it is a stub.

**Port semantics for SNOBOL4 pattern matching:**
| Port | Direction | Pattern meaning |
|---|---|---|
| α | synthesized UP | fresh-entry: reset state, attempt match from current cursor Δ |
| β | synthesized UP | retry-entry: advance or backtrack, try next match position |
| γ | inherited DOWN | success continuation: match succeeded, Δ advanced |
| ω | inherited DOWN | failure continuation: match failed, restore Δ |

**Key distinction from Icon/Prolog:** SNOBOL4 patterns are cursor-scanning machines. State is the cursor position Δ (`bb_exec.c` calls it `delta`). α sets the initial match position; β advances it. γ is the success exit (cursor has moved to end of match); ω is the failure exit (cursor unchanged).

---

## ⚡ CURRENT WATERMARK

**one4all HEAD: see PLAN.md — check `git log --oneline -1`.**
**GATE-SBL-PAT (mode-2 pattern rung suite):** script TBD — build in SBL-G-1.
**GATE-PK (per-kind):** status per GOAL-HEADQUARTERS.md — PASS=504 FAIL=0 STUB=625 is the HQ target; pattern kinds contribute to STUB until templates are filled.
**Broad corpus mode-4:** 250/280 at last watermark (GOAL-MODE4-SN4-SNOCONE.md).

**Template fill status (2026-05-27):**

| BB kind | Template file | x86 TEXT | x86 BINARY | Status |
|---|---|---|---|---|
| BB_PAT_LIT | bb_lit.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_ANY | bb_pat_any.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_NOTANY | bb_pat_notany.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_SPAN | bb_pat_span.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_BREAK | bb_pat_break.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_ARB | bb_pat_arb.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_LEN | bb_pat_len.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_POS / RPOS | bb_pat_pos.cpp | ✅ | ✅ | **FILLED** (grouped — same shape) |
| BB_PAT_TAB / RTAB | bb_pat_tab.cpp | ✅ | ✅ | **FILLED** (grouped — same shape) |
| BB_PAT_REM | bb_pat_rem.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_ALT | bb_pat_alt.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_CAT | bb_pat_cat.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_FENCE | bb_pat_fence.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_ABORT | bb_pat_abort.cpp | ✅ | ✅ | **FILLED** |
| BB_EPS | bb_eps.cpp | ✅ | ✅ | **FILLED** |
| BB_FAIL | bb_fail.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_ARBNO | bb_arbno.cpp | ✅ | ✅ | **FILLED** |
| BB_PAT_ASSIGN_IMM | bb_capture.cpp | ✅ | ✅ | **FILLED** (`. V` immediate) |
| BB_PAT_ASSIGN_COND | bb_capture.cpp | ✅ | ✅ | **FILLED** (`$ V` conditional) |
| BB_PAT_CALLOUT | — | ⏳ | ⏳ | **STUB** (`*Fn()` deferred call) |

**Summary:** All structural pattern primitives have filled TEXT and BINARY arms. The known open issues are verification gaps and specific bugs, not missing templates. See Open Rungs below.

---

## ⚠ Known open bugs / gaps (from GOAL-MODE4-SN4-SNOCONE and GOAL-PROLOG-BB watermarks)

1. **SBL-TAB-RELOC** — `bb_pat_tab.cpp` BINARY arm `bb_bin_t` relocation is incomplete or missing for the TAB/RTAB cursor-set case (from SBL-PAT-PRIM watermark: ANY/NOTANY/SPAN/BREAK fixed, TAB still open). Symptom: TAB/RTAB incorrect in `--run` (mode 3) binary path.
2. **SBL-CAP-SEGFAULT** — `. V` conditional capture (BB_PAT_ASSIGN_COND) segfaults in mode 3 SNOBOL4. Root cause: `bb_capture.cpp` BINARY arm. (SBL-PAT-PRIM watermark).
3. **SBL-CALLCAP** — `*Fn()` deferred-call captures (`BB_PAT_CALLOUT`) have no template body; `emit_core.c` case 538 stubs it. Three corpus programs fail (expr_eval, 140_pat_eval_double_fn_trick, 141_pat_eval_double_fn_arbno). Both also fail in `--interp` — deeper issue.
4. **SBL-CURSOR-CAP** — `@var` cursor capture (XATP node, likely `emit_bb_xatp` in legacy emitter) is empty in `--interp`. Two programs: 074_pat_star_var_cursor, W07_capt_cur.
5. **SBL-BENCH-ALL** — 16 SNOBOL4 bench programs: m2=m3=m4 parity not yet achieved for all 16.
6. **GATE-PK stale** — per-kind baselines for pattern kinds not re-frozen since last round of template changes. See SBL-G-2.

---

## Architecture

```
lower_pat_dcg.c  — BB_lower_pat(tree_t *pat) → BB_graph_t*
    build_node(cfg, t, sp, fp):
        sp = success continuation (the γ pointer)
        fp = failure continuation (the ω pointer)
        Leaf nodes:  nd->α=nd, nd->β=fp, nd->γ=sp, nd->ω=fp   (most)
        Generator nodes (ARB, SPAN): nd->α=nd, nd->β=nd (self-loop on β)
        CAT (sequence): right-to-left chain, each left feeds into right's α
        ALT (alternation): right-to-left chain, each left's ω → next alt's α
        ARBNO:   nd->α=nd, nd->β=nd, γ=sp, ω=fp; inner sub-graph in aux state
        CAPTURE: nd->α=inner_entry, nd->β=inner->β; nd's own γ/ω = sp/fp

SM bridge:   SM_EXEC_STMT (snobol4) or SM_BB_SWITCH (Snocone/Icon patterns)
             → bb_build_brokered or bb_build_flat → BB_graph_t
             → walk_bb_node → emit_core dispatch → bb_pat_*.cpp
```

**Reference oracle for each BB kind:** `bb_exec.c` `case BB_PAT_*:` — read it before writing or modifying any template. The template must produce x86 that implements exactly what bb_exec does in C.

**Lower_pat_dcg port contract** (verified from source, 2026-05-27):
- **Leaves** (LIT, ANY, NOTANY, BREAK, LEN, POS/RPOS, TAB/RTAB, REM, ABORT): `α=self, β=fp, γ=sp, ω=fp`. On α: attempt match, jump γ on success or ω on failure. No retry (β=fp fails immediately).
- **Generators** (ARB, SPAN): `α=self, β=self, γ=sp, ω=fp`. On α: try empty/shortest; on β: advance by one and retry. Self-loop on β drives backtracking from the continuation.
- **ARBNO**: `α=self, β=self, γ=sp, ω=fp`. Inner sub-graph in `az->inner`. On α: try matching inner once more and recurse; on β: pop one level from pos_stack and retry inner.
- **CAT** (TT_CAT/TT_SEQ): right-to-left chain. The leftmost node's α is the entry; its γ→next_node's α; last node's γ=sp. Any node's ω = its left neighbor's β (backtrack to re-drive the predecessor).
- **ALT** (TT_ALT): right-to-left chain. Each alt's ω→next_alt's α. Last alt's ω=fp. α = leftmost alt's α.
- **CAPTURE** (ASSIGN_IMM / ASSIGN_COND): `α=inner_entry, β=inner->β`. On success (γ=sp): record matched span in named variable. On failure (ω=fp): no binding.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                # GATE-1: 7/7 (--interp + --run)
bash scripts/test_smoke_unified_broker.sh         # GATE-2: 23/23
bash scripts/test_mode4_broad_corpus_snobol4.sh   # GATE-3: ≥250/280
bash scripts/test_snobol4_pat_rung_suite.sh       # GATE-4: ≥N/M (once SBL-G-1 exists)
bash scripts/test_per_kind_diff.sh                # GATE-PK: FAIL=0 (once SBL-G-2 done)
```

---

## Open Rungs (priority order)

### Phase SBL-G — Gate infrastructure

#### SBL-G-1 — Build `test_snobol4_pat_rung_suite.sh` ⏳
- [ ] Create `scripts/test_snobol4_pat_rung_suite.sh`: run all `.sno` files in `test/snobol4/patterns/` (038..057 + any future rungs) via both `--interp` and `--compile`. For each program: `scrip --interp file.sno` → compare against `.s` (expected) file; `scrip --compile file.sno` → assemble → link → run → compare. Report PASS-M2=N PASS-M4=M FAIL-M2=X FAIL-M4=Y.
- [ ] Wire into Session Setup above.
- [ ] Establish baseline: run once, record counts as `SBL-G-1-BASELINE-M2=N SBL-G-1-BASELINE-M4=M` in this file.
- [ ] Gate threshold: M2 must not drop below baseline. M4 must climb rung-by-rung.

#### SBL-G-2 — Re-freeze GATE-PK for pattern kinds ⏳
- [ ] Run `bash scripts/test_per_kind_diff.sh`. For each BB_PAT_* kind: if the template body has honest x86 content, verify the baseline matches. If the baseline is stale (template changed since freeze), re-freeze that cell.
- [ ] For BB_PAT_CALLOUT and any pure-stub kinds: confirm baseline is empty `std::string()`.
- [ ] Target: GATE-PK FAIL=0 for all pattern kinds. NEW=0 GONE=0.
- [ ] **Do not proceed to SBL-TAB, SBL-CAP, or SBL-CALLOUT until GATE-PK is GREEN for the kinds being fixed** — a stale baseline makes regressions invisible.

---

### Phase SBL-TAB — TAB/RTAB BINARY relocation fix

#### SBL-TAB-1 — Diagnose `bb_pat_tab.cpp` BINARY arm `bb_bin_t` ⏳
- [ ] Read `bb_pat_tab.cpp` BINARY arm. Check if it fills `bin.sites`, `bin.labels`, `bin.is_def` correctly for every rel32 fixup site (every `jmp`, `je`, `jg`, etc. targeting a port label outside the blob).
- [ ] Compare against `bb_pat_span.cpp` or `bb_pat_any.cpp` BINARY arm as a known-good reference — those were fixed in SBL-PAT-PRIM.
- [ ] Write a minimal mode-3 probe: `X = 'abcde'; X TAB(3); OUTPUT = X` — run `scrip --run` and compare to `scrip --interp`. If they differ, BINARY arm is the bug.
- [ ] Gate: diagnose only; gate is `test_smoke_snobol4.sh` 7/7 unchanged.

#### SBL-TAB-2 — Fix `bb_pat_tab.cpp` BINARY arm ⏳
- [ ] Fix the `bb_bin_t` site list to match the TEXT arm's jump structure. TAB's TEXT arm: `α: load Δ; compare against N; jl ω; set Δ=N; jmp γ`. BINARY must have rel32 fixup entries for every `jl ω`, `jmp γ`, `jmp β` in the same positions.
- [ ] RTAB variant: same structure but `compare against (Σlen - N)`.
- [ ] Gate: GATE-PK FAIL=0 for BB_PAT_TAB. `scrip --run` TAB/RTAB probe matches `--interp`.

---

### Phase SBL-CAP — Capture BINARY arm segfault (`. V` in mode 3)

#### SBL-CAP-1 — Diagnose `bb_capture.cpp` BINARY arm ⏳
- [ ] Minimal probe: `S = 'hello'; S 'hel' . V; OUTPUT = V` — run `scrip --run`. If segfault or wrong output, BINARY arm is the bug.
- [ ] Read `bb_capture.cpp` BINARY arm. Check: (a) `bb_bin_t` sites cover all jumps; (b) the `XA_BB_PTR_SLOT` mechanism (`bb_prepare_capture_arbno`) correctly sets up the rt object pointer in binary mode; (c) `g_cap_fixup_cb` is registered.
- [ ] Cross-reference `bb_arbno.cpp` BINARY arm — both go through `bb_prepare_capture_arbno`. If arbno works but capture doesn't, the divergence is in bb_capture's own BINARY body.
- [ ] Gate: diagnose only; gate is `test_smoke_snobol4.sh` 7/7 unchanged.

#### SBL-CAP-2 — Fix `bb_capture.cpp` BINARY arm ⏳
- [ ] Fix the `bb_bin_t` site list and/or the rt-object pointer setup for the BINARY/brokered path.
- [ ] Test both `BB_PAT_ASSIGN_COND` (`. V`) and `BB_PAT_ASSIGN_IMM` (`$ V`) — they share the template; verify both.
- [ ] Gate: GATE-PK FAIL=0 for BB_PAT_ASSIGN_COND/IMM. `scrip --run` capture probe matches `--interp`. GATE-1 7/7.

---

### Phase SBL-CALLOUT — BB_PAT_CALLOUT (`*Fn()` deferred call)

#### SBL-CALLOUT-1 — Diagnose `*Fn()` in mode 2 first ⏳
- [ ] Confirm: `expr_eval.sno`, `140_pat_eval_double_fn_trick.sno`, `141_pat_eval_double_fn_arbno.sno` fail in `--interp`. If so, this is a mode-2 lowering problem, not a template problem. Do NOT write a template until mode-2 is correct.
- [ ] Read `emit_core.c` case 538 (BB_PAT_CALLOUT stub). Read `lower_pat_dcg.c` TT_FNC default handler — does it build a BB_PAT_CALLOUT node?
- [ ] Trace the `*Fn(args)` path from parser → lower_pat_dcg → bb_exec.c. If bb_exec.c has no `case BB_PAT_CALLOUT:` arm or it's incomplete, that is the mode-2 bug.
- [ ] Gate: diagnose only.

#### SBL-CALLOUT-2 — Wire BB_PAT_CALLOUT in mode 2 (lower + exec) ⏳
- [ ] If `lower_pat_dcg.c` does not build a BB_PAT_CALLOUT node for `*Fn(arg)`, add that case. Node fields: `sval=fn_name`, `α=nd, β=fp, γ=sp, ω=fp`.
- [ ] Add `case BB_PAT_CALLOUT:` to `bb_exec.c`: evaluate the function call (via `icn_try_call_builtin_by_name` or equivalent), use result as a pattern, attempt the sub-match at current Δ. On success: advance Δ, return `nd->γ`. On failure: return `nd->ω`.
- [ ] Gate: `scrip --interp expr_eval.sno` passes. GATE-1 7/7. GATE-2 23/23.

#### SBL-CALLOUT-3 — Fill `bb_pat_callout.cpp` (mode 4) ⏳
- [ ] Create `src/emitter/BB_templates/bb_pat_callout.cpp` (new file — does not exist yet).
- [ ] Wire into `emit_core.c` dispatch (replace the case-538 stub with `bb_pat_callout(nd); return 0;`).
- [ ] Add to Makefile.
- [ ] TEXT arm: emit `call <fn_name>@PLT` using `nd->sval`; test return value; `jne ω; jmp γ`. BINARY arm: rel32 fixup for the γ/ω jumps.
- [ ] Gate: GATE-PK FAIL=0 for BB_PAT_CALLOUT. Mode-4 probe with `*Fn()` pattern matches `--interp`. GATE-1 7/7.

---

### Phase SBL-CURSOR — `@var` cursor capture

#### SBL-CURSOR-1 — Diagnose and fix XATP / `@var` in mode 2 ⏳
- [ ] `074_pat_star_var_cursor.sno` and `W07_capt_cur.sno` produce empty output in `--interp`. Trace `@var` AST node through `lower_pat_dcg.c` — is there a `TT_CURSOR_ASSIGN` or `TT_XATP` case? If not, the node falls through to the `default: return NULL` and the pattern silently fails.
- [ ] Add lowering for cursor-capture: `@var` should bind the current cursor integer to `var` at match time. Build a BB node (new kind or reuse BB_PAT_ASSIGN_IMM with a cursor flag).
- [ ] Gate: `scrip --interp 074_pat_star_var_cursor.sno` matches oracle. GATE-1 7/7.

#### SBL-CURSOR-2 — Emit cursor capture in mode 4 ⏳
- [ ] Add template or extend `bb_capture.cpp` for the cursor-capture variant.
- [ ] Gate: mode-4 cursor capture probe matches `--interp`.

---

### Phase SBL-BENCH — SNOBOL4 bench parity m2=m3=m4

#### SBL-BENCH-1 — Triage 16 bench programs ⏳
- [ ] Run `bash scripts/test_snobol4_bench.sh` (or equivalent) under `--interp`, `--run`, `--compile`. Record which benches differ across modes.
- [ ] Categorize failures: (a) correctness difference — a pattern or statement produces wrong output; (b) crash/segfault; (c) timeout.
- [ ] Produce a table: bench name | m2 | m3 | m4 | status. Record as `SBL-BENCH-1-TABLE` in session state below.
- [ ] Gate: triage only. GATE-1 7/7, GATE-3 ≥250 unchanged.

#### SBL-BENCH-2..N — Fix each bench divergence (one rung per bench) ⏳
- [ ] For each bench with m2≠m3 or m2≠m4: trace the divergence to the specific BB kind or SM opcode. Fix the template or lowering. Gate: that bench passes m2=m3=m4. Non-regression: all other benches unchanged.

---

### Phase SBL-VERIFY — Full mode-2/4 parity sweep

#### SBL-VERIFY-1 — Run full pattern rung suite in mode-4, climb to M4=M2 ⏳
- [ ] After SBL-TAB-2 + SBL-CAP-2 + SBL-CALLOUT-3 land: run `test_snobol4_pat_rung_suite.sh`. M4 should now equal M2 for 038..057. If any rung still differs, diagnose and fix.
- [ ] Target: PASS-M4 = PASS-M2 for all pattern rungs 038–057. Record as verified watermark.

#### SBL-VERIFY-2 — Broad corpus mode-4: climb from 250 toward 280 ⏳
- [ ] After all pattern fixes land: run `test_mode4_broad_corpus_snobol4.sh`. Each fixed pattern kind should unblock additional corpus programs. Record new PASS count.
- [ ] Target: ≥260/280. (Further gains may require DATA-type accessor and `*Fn()` callout fixes — see GOAL-MODE4-SN4-SNOCONE for detail on the remaining 30 failures.)

---

## Completed Steps

**All structural BB_PAT_* templates filled (TEXT + BINARY x86 arms):**
- BB_PAT_LIT, BB_PAT_ANY, BB_PAT_NOTANY, BB_PAT_SPAN, BB_PAT_BREAK ✅
- BB_PAT_ARB, BB_PAT_ARBNO ✅
- BB_PAT_LEN, BB_PAT_POS/RPOS (grouped), BB_PAT_TAB/RTAB (grouped) ✅ (BINARY reloc open — SBL-TAB)
- BB_PAT_REM, BB_PAT_ALT, BB_PAT_CAT, BB_PAT_FENCE, BB_PAT_ABORT ✅
- BB_EPS, BB_FAIL ✅
- BB_PAT_ASSIGN_IMM / BB_PAT_ASSIGN_COND (bb_capture.cpp) ✅ (BINARY segfault open — SBL-CAP)
- TEMPLATE-PURITY: LOCAL-PURGE LP-7-NONX86 completed bb_capture JVM+JS arms ✅
- CAPS-CONCAT: all pattern template X86 arms collapsed to single return per IF()/FOR() ✅
- SBL-PAT-PRIM: ANY/NOTANY/SPAN/BREAK bb_bin_t reloc fixed ✅
- SBL-M4-ASM: mode-4 broad corpus 0→250/280 ✅

---

## Session State

```
SBL-G-1-BASELINE-M2=?       # set when gate script is first run
SBL-G-1-BASELINE-M4=?       # set when gate script is first run
SBL-BENCH-1-TABLE=pending   # set in SBL-BENCH-1 triage
GATE-PK-PAT-STATUS=stale    # set GREEN when SBL-G-2 complete
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
