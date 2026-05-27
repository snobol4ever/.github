# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates: fill hollow x86 arms

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md · GOAL-MODE4-SN4-SNOCONE.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle — read this first)
    → [mode 4] walk_bb_flat → FILL macro → walk_bb_node → emit_core dispatch
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 bytes via bb_bin_t)
```

**Mode 2 (`--interp`):** `sm_interp.c SM_EXEC_STMT` → `exec_stmt_blob` → `bb_build_brokered` → `bb_broker` → dispatched x86 blob from template BINARY arm. ALSO: `bb_exec.c case BB_PAT_*` is the pure-C correctness reference for mode-2 direct execution.

**Mode 3 (`--run`):** `sm_interp.c SM_EXEC_STMT` → `rt_match_blob` → `exec_stmt_blob` → `bb_build_flat` → inline x86 blob from template TEXT arm.

**Mode 4 (`--compile`):** `codegen_sm_x86` → `walk_bb_pattern_blobs` → `codegen_flat_build` → `walk_bb_flat` → FILL macro → `walk_bb_node` → template TEXT arm → emits GAS.

**Absolute rules (RULES.md):**
- No C Byrd boxes. No `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω.
- TEMPLATE-PURITY: every `_str()` body is `state → std::string`, zero `emit_text_n` inside.
- ONE x86 PRODUCER: all emission via template functions in `BB_templates/`.
- HQ Invariant 0: returning `std::string()` is a STUB, not an implementation.
- X86 ONLY FOR NOW — do not write JVM/JS/NET/WASM arms until directed.

---

## ⚡ THE ACTUAL PROBLEM (read before touching any source)

Six `BB_PAT_*` templates have **`if (PLATFORM_X86) { return std::string(); }`** — they emit **zero bytes** in x86 mode:

| Template | BB kind | What's missing |
|---|---|---|
| `bb_pat_any.cpp` | BB_PAT_ANY | complete x86 TEXT + BINARY arms |
| `bb_pat_span.cpp` | BB_PAT_SPAN | complete x86 TEXT + BINARY arms |
| `bb_pat_break.cpp` | BB_PAT_BREAK | complete x86 TEXT + BINARY arms |
| `bb_pat_notany.cpp` | BB_PAT_NOTANY | complete x86 TEXT + BINARY arms |
| `bb_arbno.cpp` | BB_PAT_ARBNO | complete x86 TEXT + BINARY arms |
| `bb_capture.cpp` | BB_PAT_ASSIGN_IMM / BB_PAT_ASSIGN_COND | complete x86 TEXT + BINARY arms |

**Why they're empty:** These were previously backed by C Byrd-box functions in `bb_boxes.c` (the dispatched `bb_build_brokered` path — `DESCR_t bb_any_fn(void *ζ, int entry)` etc.). Those C functions are now deleted per the FACT RULE (zero C Byrd boxes). The templates were created as placeholders — JVM/JS/NET/WASM arms exist — but the x86 arms were never written. **This is the work.**

The following are correctly filled and not the subject of this goal:
- BB_PAT_LIT (`bb_lit.cpp`) ✅, BB_PAT_ARB (`bb_pat_arb.cpp`) ✅, BB_PAT_LEN ✅, BB_PAT_POS/RPOS ✅, BB_PAT_TAB/RTAB ✅, BB_PAT_REM ✅, BB_PAT_ALT ✅, BB_PAT_CAT ✅, BB_PAT_FENCE ✅, BB_PAT_ABORT ✅, BB_EPS ✅, BB_FAIL ✅

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)` which sets `g_emit.lbl_α/β/γ/ω` then calls `walk_bb_node(nd)` which dispatches to the template. The template must emit:

```
<lbl_α>:    α-port code (fresh entry — attempt match, advance Δ, jump lbl_γ or lbl_ω)
<lbl_β>:    β-port code (retry entry — undo, advance differently, jump lbl_γ or lbl_ω)
            (some kinds: β = lbl_ω directly — no retry)
```

**Runtime state available in TEXT arm:**
- `[r10]` = Δ (cursor, 32-bit int, `[r10]` in GAS intel syntax) — the scan position
- `[rip + Σ]` = pointer to subject string (extern symbol `Σ` in `emit_bb.c`)
- `[rip + Σlen]` = subject length (extern `Σlen`)
- Per-node static data: `.data` section label, referenced via `[rip + .Lfoo<id>]`
- `nd->sval` = charset string (for ANY/SPAN/BREAK/NOTANY) — baked into `.data` at emit time
- `nd->counter` (int64) = runtime mutable state for generators (SPAN β uses it)

**Runtime state available in BINARY arm:**
- `g_emit.bb_cs_zeta` = `rt_cs_new(nd->sval)` — pre-allocated charset object (already set in the `bb_pat_any` wrapper before `_str()` is called)
- The BINARY arm emits raw x86 bytes; `bb_bin_t` carries the rel32 fixup site list

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — each case shows exactly what α (state==0) and β (state>0) must do. Read this before writing each template. The x86 must implement the same logic.

**Reference for charset operations:** `rt_cs_*` functions exist in `rt.c` for BINARY; for TEXT the charset string is baked inline as a `.rodata` byte array or via `emit_intern_str`.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
```

Gates (run before and after every change):
```bash
bash scripts/test_smoke_snobol4.sh                # GATE-1: 7/7 (--interp + --run)
bash scripts/test_smoke_unified_broker.sh         # GATE-2: 23/23
bash scripts/test_mode4_broad_corpus_snobol4.sh   # GATE-3: ≥250/280
bash scripts/test_per_kind_diff.sh                # GATE-PK: FAIL=0 for pattern kinds
```

---

## Open Rungs (priority order)

### Phase SBL-G — Gate infrastructure (do first)

#### SBL-G-1 — Build `test_snobol4_pat_rung_suite.sh` ⏳
- [ ] Create `scripts/test_snobol4_pat_rung_suite.sh`: run all `.sno` files in `test/snobol4/patterns/` (038–057) via `--interp` and `--compile`. Report PASS-M2 and PASS-M4 separately.
- [ ] Establish baseline BEFORE touching any template. Record as `SBL-G-1-BASELINE-M2=N SBL-G-1-BASELINE-M4=M` in Session State below.
- [ ] Gate threshold: M2 must not drop below baseline. M4 starts at current level and must climb with each rung.

#### SBL-G-2 — Re-freeze GATE-PK for pattern kinds ⏳
- [ ] Run `bash scripts/test_per_kind_diff.sh`. For each BB_PAT_* kind: the PLATFORM_X86 empty template produces `std::string()` = empty baseline. Confirm cells are frozen as empty. If they aren't re-freeze them now.
- [ ] **After filling a template:** re-freeze that kind's cell immediately. Do not leave stale baselines — they make regressions invisible.

---

### Phase SBL-ANY — `bb_pat_any.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_ANY):**
- **α (state==0):** if Δ ≥ Σlen or Σ[Δ] not in chars → ω. Else: save Δ, advance Δ by 1, return γ.
- **β (state>0):** undo: Δ--, return ω. (No retry — ANY matches exactly one char.)

#### SBL-ANY-1 — Fill `bb_pat_any.cpp` TEXT arm ⏳
- [ ] Replace `if (PLATFORM_X86) { return std::string(); }` with a real x86 TEXT arm.
- [ ] α: load `[r10]` (Δ); compare against `[rip+Σlen]`; jge ω. Load `Σ[Δ]`; call `strchr` with charset (inlined or via `.rodata`); test result; je ω. Increment `[r10]`; jmp γ.
- [ ] β: decrement `[r10]`; jmp ω.
- [ ] Charset: bake `nd->sval` into `.section .data` as `.Lany<id>_cs: .asciz "..."`, reference via `[rip + .Lany<id>_cs]` in the `strchr` call.
- [ ] Label convention: `.Lany<id>_α:` / `.Lany<id>_β:` where `id = bb_node_id(pBB)`.
- [ ] Gate: GATE-PK re-frozen for BB_PAT_ANY. GATE-1 7/7, GATE-2 23/23.

#### SBL-ANY-2 — Fill `bb_pat_any.cpp` BINARY arm ⏳
- [ ] `g_emit.bb_cs_zeta = rt_cs_new(nd->sval)` is already called in the wrapper before `_str()`. Use `g_emit.bb_cs_zeta` pointer (embedded as imm64 in the binary blob) as the charset lookup object.
- [ ] Emit raw x86 bytes mirroring the TEXT arm logic. `bb_bin_t` sites: list every rel32 fixup (jge ω, je ω, jmp γ, jmp ω for β).
- [ ] Reference: `bb_pat_len.cpp` BINARY arm for the `bb_bin_t` site-list pattern. Reference: `bb_pat_break.cpp` BINARY arm (if it has one) or compare to the known-good `bb_pat_pos.cpp`.
- [ ] Gate: GATE-PK BINARY cell re-frozen. Mode-3 ANY probe matches `--interp`.

---

### Phase SBL-NOTANY — `bb_pat_notany.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_NOTANY):**
- **α:** if Δ ≥ Σlen or Σ[Δ] IN chars → ω. Else: advance Δ by 1, return γ.
- **β:** undo Δ--, return ω.
- Identical shape to ANY but with the `strchr` sense inverted.

#### SBL-NOTANY-1 — Fill `bb_pat_notany.cpp` TEXT arm ⏳
- [ ] Same structure as SBL-ANY-1 with `strchr` success meaning failure (jne ω becomes je ω and vice versa).
- [ ] Gate: GATE-PK re-frozen. GATE-1 7/7.

#### SBL-NOTANY-2 — Fill `bb_pat_notany.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 NOTANY probe matches `--interp`.

---

### Phase SBL-BREAK — `bb_pat_break.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_BREAK):**
- **α (state==0):** scan forward while Σ[Δ+i] not in chars; i = matched length. Save i in counter. Advance Δ by i. Return γ. (BREAK always succeeds, even on i=0 — it matches zero chars up to the break char.)
- **β (state>0):** restore Δ -= counter; return ω. (No retry.)

#### SBL-BREAK-1 — Fill `bb_pat_break.cpp` TEXT arm ⏳
- [ ] α: loop with `strchr` until char IN chars or end of string. Store loop count in `.data` slot (or `[r10+N]`). Advance Δ. jmp γ.
- [ ] β: load saved count, subtract from Δ, jmp ω.
- [ ] Gate: GATE-PK re-frozen. GATE-1 7/7.

#### SBL-BREAK-2 — Fill `bb_pat_break.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 BREAK probe matches `--interp`.

---

### Phase SBL-SPAN — `bb_pat_span.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_SPAN):**
- **α (state==0):** scan forward while Σ[Δ+i] IN chars; i = matched length. If i==0 → ω. Save i in counter. Advance Δ by i. Return γ.
- **β (state==1):** undo partial: Δ -= counter; counter--; if counter < 1 → ω. Re-advance Δ by counter. Return γ. (SPAN backtracks one char at a time.)
- **β (state==2 / exhausted):** return ω.
- SPAN is a **generator** — it yields shorter and shorter matches on successive β entries.

#### SBL-SPAN-1 — Fill `bb_pat_span.cpp` TEXT arm ⏳
- [ ] α: forward scan loop with `strchr`. If i==0: jmp ω. Store i in `.data` slot. Advance Δ. jmp γ.
- [ ] β: load counter from `.data`. Subtract from Δ. Decrement counter. If counter < 1: jmp ω. Add counter to Δ. jmp γ.
- [ ] Two `.data` slots needed: `counter` (int64) and a state flag (or reuse counter sign). See `bb_pat_arb.cpp` PLATFORM_X86 arm as reference for a generator with counter.
- [ ] Gate: GATE-PK re-frozen. GATE-1 7/7. Verify SPAN backtracking: `'aaa' SPAN('a') . V` → `V='aaa'` then backtracks to `V='aa'` etc.

#### SBL-SPAN-2 — Fill `bb_pat_span.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 SPAN probe matches `--interp`.

---

### Phase SBL-ARBNO — `bb_arbno.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_ARBNO):**
- **α (state==0):** greedily match inner sub-graph as many times as possible; push each Δ position onto `az->pos_stack`. Set `nd->state = depth`. Return γ. (ARBNO first yields the longest match.)
- **β (state>0):** `nd->state--`; if state < 0 → ω. Restore Δ from `pos_stack[state-1]` (or `az->saved_delta` if state==0). Return γ. (ARBNO yields one fewer repetition each β.)
- **Inner sub-graph:** `(bb_arbno_state_t*)(intptr_t)nd->counter` → `az->inner` (a `BB_graph_t*`). Must call `bb_exec_once(az->inner)` to match inner (mode-2 reference). In mode-4 TEXT arm: the inner sub-graph is pre-built as a separate flat blob; its α label is available via `g_emit.bb_child_lbl` (set by `walk_bb_flat` for ARBNO — see `case BB_PAT_ARBNO:` in emit_bb.c which sets `g_emit.child_fn`).

#### SBL-ARBNO-1 — Understand the child-blob mechanism first ⏳
- [ ] Read `emit_bb.c` `case BB_PAT_ARBNO:` in `walk_bb_flat` (line ~493): it calls `child_cache_get(ch)` and stores the child `bb_box_fn` in `g_emit.child_fn`. In TEXT mode, `pre_build_children_text` pre-emits the inner blob under a `<prefix>_c0` label; `g_emit.bb_child_lbl` is set to the child's α-entry label. **The template calls the child by `call [rip + <child_α_label>]` — not via a C function pointer.**
- [ ] Read `bb_arbno.cpp` current JVM/JS arms to understand the structure the template is expected to have.
- [ ] Read `bb_pat_arb.cpp` PLATFORM_X86 arm — it is a generator and uses a counter in `.data`. ARBNO is similar but uses a stack.
- [ ] Gate: read-only; no code change.

#### SBL-ARBNO-2 — Fill `bb_arbno.cpp` TEXT arm ⏳
- [ ] α: loop calling inner blob via `call <child_α_lbl>@PLT` (TEXT mode) or `call [rip + .Larbno<id>_child]`; check result (last_ok or return val); push Δ to stack; break when inner fails or Δ doesn't advance. Then return γ.
- [ ] β: pop one entry from stack. If stack empty: restore `saved_delta`, return ω. Else: set Δ from top of stack, return γ.
- [ ] Stack: the `az->pos_stack` is a runtime GC-allocated array; access via the `bb_arbno_state_t*` pointer baked into the blob (as imm64 in BINARY, or via a `.data` pointer slot in TEXT).
- [ ] Gate: GATE-PK re-frozen. GATE-1 7/7. GATE-2 23/23. `'aaa' ARBNO('a')` succeeds.

#### SBL-ARBNO-3 — Fill `bb_arbno.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 ARBNO probe matches `--interp`.

---

### Phase SBL-CAP — `bb_capture.cpp` x86 arms (`. V` and `$ V`)

**Semantic (from `bb_exec.c` BB_PAT_ASSIGN_COND / BB_PAT_ASSIGN_IMM):**
- Both kinds share the same structure:
  - **α (state==0):** save Δ in `nd->counter`. Set state=1. Return `nd->α` (= the inner sub-pattern's entry). (The inner sub-pattern will eventually γ back to the capture node's own γ port.)
  - **γ arrival (state==1):** compute `matched_len = Δ - counter`. Assign `Σ[counter..counter+matched_len]` to `nd->sval` variable via `NV_SET_fn`. Return γ.
- The capture node in `lower_pat_dcg.c` has `nd->α = inner_entry, nd->β = inner->β` — the inner sub-graph is a *child* of the capture node wired through its α port.
- **Key distinction:** in `walk_bb_flat` (emit_bb.c, `case BB_PAT_ASSIGN_IMM/COND`), `g_emit.child_fn` is set to the pre-built child blob fn, and `g_emit.op_name1` = the variable name. The template sees these in `g_emit`.

#### SBL-CAP-1 — Fill `bb_capture.cpp` TEXT arm ⏳
- [ ] α-entry: save `[r10]` (Δ) to a `.data` slot (`.Lcap<id>_start`). Then jump to the child blob's α entry (`call <child_α_lbl>` — child pre-built as a flat blob).
- [ ] γ-arrival (the child succeeded): compute `matched_len = [r10] - [rip + .Lcap<id>_start]`. Call `rt_nv_set_str@PLT(varname_ptr, subj+start, matched_len)` (or equivalent runtime helper). Jump lbl_γ.
- [ ] ω-arrival (child failed): jump lbl_ω.
- [ ] The child's own β is `g_emit.bb_child_lbl`'s β — the template does not own that; the child blob handles retry internally.
- [ ] Read existing JVM/NET arms in `bb_capture.cpp` for structural reference.
- [ ] Gate: GATE-PK re-frozen. GATE-1 7/7. `S 'abc' . V` succeeds with V=matched span.

#### SBL-CAP-2 — Fill `bb_capture.cpp` BINARY arm ⏳
- [ ] Fix `bb_bin_t` site list to cover all rel32 fixups.
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 capture probe matches `--interp`. GATE-1 7/7.

---

### Phase SBL-VERIFY — Rung sweep after all six are filled

#### SBL-VERIFY-1 — Run full pattern rung suite, climb M4=M2 ⏳
- [ ] After SBL-ANY, SBL-NOTANY, SBL-BREAK, SBL-SPAN, SBL-ARBNO, SBL-CAP all filled: run `test_snobol4_pat_rung_suite.sh`. Target: PASS-M4 = PASS-M2 for rungs 038–057.
- [ ] Gate: record new PASS-M4 count in Session State. GATE-3 ≥250/280.

#### SBL-VERIFY-2 — Broad corpus mode-4 climb ⏳
- [ ] Run `test_mode4_broad_corpus_snobol4.sh`. Filled templates should unblock corpus programs that use ANY/SPAN/BREAK/NOTANY/ARBNO/capture in mode-4. Record new PASS count.
- [ ] Target: ≥260/280 (further gains may require DATA-type accessors — see GOAL-MODE4-SN4-SNOCONE).

---

## Completed Steps

**Templates with x86 arms already filled (not the subject of this goal):**
- BB_PAT_LIT (`bb_lit.cpp`) ✅ — literal string match, full TEXT+BINARY
- BB_PAT_ARB (`bb_pat_arb.cpp`) ✅ — zero-or-more cursor advance generator
- BB_PAT_LEN (`bb_pat_len.cpp`) ✅ — match exactly N chars
- BB_PAT_POS / BB_PAT_RPOS (`bb_pat_pos.cpp`) ✅ — cursor position anchor
- BB_PAT_TAB / BB_PAT_RTAB (`bb_pat_tab.cpp`) ✅ — advance cursor to column
- BB_PAT_REM (`bb_pat_rem.cpp`) ✅ — match rest of string
- BB_PAT_ALT (`bb_pat_alt.cpp`) ✅ — pattern alternation (flat_drive_alt)
- BB_PAT_CAT (`bb_pat_cat.cpp`) ✅ — pattern concatenation (flat_drive_cat)
- BB_PAT_FENCE (`bb_pat_fence.cpp`) ✅ — commit barrier (flat_drive_fence)
- BB_PAT_ABORT (`bb_pat_abort.cpp`) ✅ — unconditional abort
- BB_EPS (`bb_eps.cpp`) ✅ — empty pattern
- BB_FAIL (`bb_fail.cpp`) ✅ — always fail

**Infrastructure completed:**
- TEMPLATE-PURITY / LOCAL-PURGE: every `_str()` body pure `state → std::string` ✅
- CAPS-CONCAT: all filled pattern X86 arms collapsed to single-return IF()/FOR() form ✅
- SBL-M4-ASM: mode-4 broad corpus 0→250/280 ✅
- bb_boxes.c C Byrd-box functions deleted (FACT RULE) ✅
- rt_bb_pump_proc and other rt_bb_* deleted (Engine A deletion, JA-D-3) ✅

---

## Session State

```
SBL-G-1-BASELINE-M2=?       # set when gate script first run — before any template change
SBL-G-1-BASELINE-M4=?       # set when gate script first run — before any template change
GATE-PK-PAT-STATUS=stale    # set GREEN after SBL-G-2 complete
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
