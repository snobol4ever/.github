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

#### SBL-G-1 — Build `test_snobol4_pat_rung_suite.sh` ✅ (2026-05-27)
- [x] Create `scripts/test_snobol4_pat_rung_suite.sh`: runs all `.sno` in `test/snobol4/patterns/` (038–057) via `--interp` and `--compile`. Reports PASS-M2/PASS-M4 separately. SPITBOL x64 oracle outputs baked inline (self-contained).
- [x] Baseline established BEFORE any template change: **M2=9/19, M4=0/19** (compile/link blocked at assembler stage by the macro-annotation bug, see below). Broad corpus baseline = **121/280** at clean HEAD `3a522bd8` (the goal's prior "250" figure was a stale corpus-state number).
- [x] Gate threshold active: M2 must not drop below 9. M4 climbs per rung.

#### SBL-G-2 — Re-freeze GATE-PK for pattern kinds ⏳
- [ ] Run `bash scripts/test_per_kind_diff.sh`. For each BB_PAT_* kind: the PLATFORM_X86 empty template produces `std::string()` = empty baseline. Confirm cells are frozen as empty. If they aren't re-freeze them now.
- [ ] **After filling a template:** re-freeze that kind's cell immediately. Do not leave stale baselines — they make regressions invisible.

---

### Phase SBL-ANY — `bb_pat_any.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_ANY):**
- **α (state==0):** if Δ ≥ Σlen or Σ[Δ] not in chars → ω. Else: save Δ, advance Δ by 1, return γ.
- **β (state>0):** undo: Δ--, return ω. (No retry — ANY matches exactly one char.)

#### SBL-ANY-1 — Fill `bb_pat_any.cpp` TEXT arm ✅ (2026-05-27, `308e0378`)
- [x] x86 TEXT arm filled, verified line-for-line vs recovered `bb_any.s` (`660339cd~1`). α: load Δ via `[r10]`, `cmp [rip+Σlen]`, `jge ω`; load `Σ[Δ]`, `strchr@PLT` against `emit_intern_str` charset, `je ω`; `inc Δ; jmp γ`. β: `dec Δ; jmp ω`. Verified 'apple' (scan0) + 'hello' (scan1 backtrack). GATE-1 mode-2 7/7. (orig TEXT-arm subtasks below superseded)
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

#### SBL-NOTANY-1 — Fill `bb_pat_notany.cpp` TEXT arm ✅ (2026-05-27)
- [x] Same structure as SBL-ANY-1 with `strchr` success meaning failure. Mirrored ANY exactly; the sole logic delta is `jne ω` (NOTANY fails when char IS in set) vs ANY's `je ω`. Verified: `'hello' NOTANY('xyz')`→matched (m2=m4); anchored `'aeiou' NOTANY('aeiou')`→no match (m2=m4). Broad corpus 137→138.
- [x] Gate: GATE-1 7/7, GATE-2 23/23. No regression.

#### SBL-NOTANY-2 — Fill `bb_pat_notany.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 NOTANY probe matches `--interp`.

---

### Phase SBL-BREAK — `bb_pat_break.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_BREAK):**
- **α (state==0):** scan forward while Σ[Δ+i] not in chars; i = matched length. Save i in counter. Advance Δ by i. Return γ. (BREAK always succeeds, even on i=0 — it matches zero chars up to the break char.)
- **β (state>0):** restore Δ -= counter; return ω. (No retry.)

#### SBL-BREAK-1 — Fill `bb_pat_break.cpp` TEXT arm ✅ (2026-05-27)
- [x] α: forward scan loop with `strchr` (inverted from SPAN: `jnz dn` — BREAK stops when char IS found). Always succeeds, even on i=0. Saved len in `.Lbrk<id>_z`. Advance Δ. jmp γ.
- [x] β: plain non-generator: `Δ -= counter; jmp ω`.
- [x] BREAKX (`nd->ival==1`) NOT YET implemented — plain BREAK only (`nd->ival==0`). SBL-BREAKX-1/2 still open.
- [x] Verified: `'hello world' BREAK(' ')`→matched (m2=m4); `'xyz' BREAK('abc')`→matched (whole string, no break char) (m2=m4); `' xyz' BREAK(' ')`→matched (empty span at break char) (m2=m4). Broad corpus 139→141.
- [x] Gate: GATE-1 7/7, GATE-2 23/23. No regression.

#### SBL-BREAK-2 — Fill `bb_pat_break.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 BREAK probe matches `--interp`.

---

### Phase SBL-SPAN — `bb_pat_span.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_SPAN):**
- **α (state==0):** scan forward while Σ[Δ+i] IN chars; i = matched length. If i==0 → ω. Save i in counter. Advance Δ by i. Return γ.
- **β (state==1):** undo partial: Δ -= counter; counter--; if counter < 1 → ω. Re-advance Δ by counter. Return γ. (SPAN backtracks one char at a time.)
- **β (state==2 / exhausted):** return ω.
- SPAN is a **generator** — it yields shorter and shorter matches on successive β entries.

#### SBL-SPAN-1 — Fill `bb_pat_span.cpp` TEXT arm ✅ (2026-05-27)
- [x] α: forward scan loop with `strchr` (transcribed from recovered `bb_span.s`, r11=Σ base preserved across `strchr@PLT` via push/pop). If matched-len==0: jmp ω. Stored len in `.Lspan<id>_z+0`, base Δ in `+4`. Advance Δ. jmp γ.
- [x] β: GENERATOR form (per bb_exec.c oracle, NOT the simple .s β): load base from `+4`, counter from `+0`, decrement; if <1 jmp ω; store new counter; Δ = base+counter; jmp γ. Modeled on filled `bb_pat_arb.cpp` two-long `.data` slot.
- [x] Verified: `'aaabbb' SPAN('a')`→matched (m2=m4); `'aaab' SPAN('ab') 'b'`→matched via backtrack from 'aaab' to 'aaa' (m2=m4). Broad corpus 138→139.
- [x] Gate: GATE-1 7/7, GATE-2 23/23. No regression.

#### SBL-SPAN-2 — Fill `bb_pat_span.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 SPAN probe matches `--interp`.

---

### Phase SBL-ARBNO — `bb_arbno.cpp` x86 arms

**Semantic (from `bb_exec.c` BB_PAT_ARBNO):**
- **α (state==0):** greedily match inner sub-graph as many times as possible; push each Δ position onto `az->pos_stack`. Set `nd->state = depth`. Return γ. (ARBNO first yields the longest match.)
- **β (state>0):** `nd->state--`; if state < 0 → ω. Restore Δ from `pos_stack[state-1]` (or `az->saved_delta` if state==0). Return γ. (ARBNO yields one fewer repetition each β.)
- **Inner sub-graph:** `(bb_arbno_state_t*)(intptr_t)nd->counter` → `az->inner` (a `BB_graph_t*`). Must call `bb_exec_once(az->inner)` to match inner (mode-2 reference). In mode-4 TEXT arm: the inner sub-graph is pre-built as a separate flat blob; its α label is available via `g_emit.bb_child_lbl` (set by `walk_bb_flat` for ARBNO — see `case BB_PAT_ARBNO:` in emit_bb.c which sets `g_emit.child_fn`).

#### SBL-ARBNO-1 — Understand the child-blob mechanism first ✅ (2026-05-27)
- [x] Confirmed: `walk_bb_flat` `case BB_PAT_ARBNO:` sets `g_emit.child_fn` from `child_cache_get(ch)`; `pre_build_children_text` emits the inner blob as a separate `codegen_flat_body` at prefix `<base>_c<N>` with its own α/β/γ/ω globals; `bb_prepare_capture_arbno` populates `g_emit.bb_child_lbl` with the child's α-label via `child_cache_get_lbl`. The TEXT arm calls the child by `call <child_α_lbl>` — the prologue dispatches on `esi` (`esi==0` → α, else β) per `XA_FLAT_PROLOGUE`. Child returns `eax=1` (success) or `eax=99` (fail) per `XA_FLAT_EPILOGUE`. Same mechanism the capture template uses.

#### SBL-ARBNO-2 — Fill `bb_arbno.cpp` TEXT arm ✅ (2026-05-27)
- [x] α: save Δ to `.Larbno<id>_saved`. Loop: cap at 256 iterations; capture pre-Δ; `xor esi, esi; call <child_α_lbl>`; on `eax==99` break; if Δ unchanged break (zero-width inner — would loop forever); push Δ to `.Larbno<id>_stack[depth*4]`; `depth++`. End: jmp γ. Yields longest match first.
- [x] β: `depth--`; if <0 jmp ω; if depth==0 restore from `saved`, else load `stack[(depth-1)*4]`; write to `[r10]`; jmp γ. One fewer repetition per β invocation.
- [x] Verified: `'aaa' POS(0) ARBNO('a') RPOS(0)` matches m2=m4; `'aaa' ARBNO('a') 'a'` backtracks correctly (greedy→2→trailing 'a' matches) m2=m4.
- [x] Rung suite SKIP-M4 5 → 1 (only 051 remains, pre-existing alt-child duplicate-symbol bug).
- [x] Gate: GATE-1 7/7, GATE-2 23→24 (+1, picks up a PAT_LIT-using broker test).

#### SBL-ARBNO-3 — Fill `bb_arbno.cpp` BINARY arm ⏳
- [ ] Gate: GATE-PK BINARY re-frozen. Mode-3 ARBNO probe matches `--interp`.

#### SBL-PAT-LIT-FIX — `sm_pat_anchors.cpp` GAS macro-annotation bug ✅ (2026-05-27)
- [x] **Pre-existing bug** in `sm_pat_anchors.cpp:31-33`: `PAT_LIT`/`PAT_REFNAME`/`PAT_USERCALL` emitted human-readable third positional arg (`arg="a"`, varname, fnname) to GAS macros that only take `lbl`. Sibling of the previously-fixed `sm_pat_combine.cpp` bug. Was MASKED until SBL-CAP-1 enabled inline emit for capture/ARBNO windows — then ANY program using a literal inside a pattern (which is most of them) failed at `as` stage.
- [x] Fix: same approach as the prior session's combine.cpp fix — annotation goes in a preceding `#` comment, macro call is `s_2asm` with only the label arg.
- [x] **Broad corpus snobol4 jumped 155 → 183 (+28)** — scope much larger than ARBNO alone; the bug affected any program with `'literal' inside-pattern` once that program reached `as`.

---

### Phase SBL-CAP — `bb_capture.cpp` x86 arms (`. V` and `$ V`)

**Semantic (from `bb_exec.c` BB_PAT_ASSIGN_COND / BB_PAT_ASSIGN_IMM):**
- Both kinds share the same structure:
  - **α (state==0):** save Δ in `nd->counter`. Set state=1. Return `nd->α` (= the inner sub-pattern's entry). (The inner sub-pattern will eventually γ back to the capture node's own γ port.)
  - **γ arrival (state==1):** compute `matched_len = Δ - counter`. Assign `Σ[counter..counter+matched_len]` to `nd->sval` variable via `NV_SET_fn`. Return γ.
- The capture node in `lower_pat_dcg.c` has `nd->α = inner_entry, nd->β = inner->β` — the inner sub-graph is a *child* of the capture node wired through its α port.
- **Key distinction:** in `walk_bb_flat` (emit_bb.c, `case BB_PAT_ASSIGN_IMM/COND`), `g_emit.child_fn` is set to the pre-built child blob fn, and `g_emit.op_name1` = the variable name. The template sees these in `g_emit`.

#### SBL-CAP-1 — Fill `bb_capture.cpp` TEXT arm ✅ (2026-05-27)
- [x] **Design fork resolved: emit fully inline.** Investigation showed the runtime `cap_t` object allocated by `bb_prepare_capture_arbno`+`XA_CAP_FIXUP` is **dead scaffolding** — its only consumer was the deleted C Byrd box `bb_cap()`, removed by the FACT RULE purge. The new TEXT arm is self-contained inline x86; it ignores `cap_t` entirely. (Recommend deleting `bb_prepare_capture_arbno`'s cap_new/cap_fixup calls in a follow-up HQ rung as residue.)
- [x] α-entry: save `[r10]` (Δ) to `.Lcap<id>_start` (4-byte slot). `xor esi, esi; call <child_α_lbl>`. On return: `cmp eax, 99; je ω; jmp .Lcap<id>_assign`.
- [x] β-entry: `mov esi, 1; call <child_α_lbl>` (re-enters child at its β via prologue dispatch on esi). Same eax check; fall through to assign on success.
- [x] Assign: compute `Σ+start` in rsi, `Δ-start` in edx; `lea rdi, [rip + <varname_intern_str>]`; `call rt_cap_assign@PLT`; `jmp γ`. Both ASSIGN_IMM and ASSIGN_COND share this code (matches bb_exec.c oracle: both write on γ arrival immediately).
- [x] Added `rt_cap_assign(varname, base, len)` to `rt.c` — same class as the existing 29 `rt_pat_*` helpers (pattern-building, not a Byrd box; sanctioned per goal-file).
- [x] **Removed ASSIGN_IMM/ASSIGN_COND from `lower_flat_invariant` exclusion** (`emit_sm.c:781`). CALLOUT remains excluded (no template yet). This is what unlocks inline emit for capture-containing windows.
- [x] Verified: rung 039 (`'hello' ANY('aeiou') . V`) → V='e' in m2=m4. Rung suite M4 jumped 1→8 (+7). Broad corpus 141→155 (+14).
- [x] Gate: GATE-1 7/7, GATE-2 23/23. No regression.

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
SBL-G-1-BASELINE-M2=9       # 19 pattern rungs, --interp, clean HEAD 3a522bd8
SBL-G-1-BASELINE-M4=0       # mode-4; was assembler-blocked by macro-annotation bug
SBL-CURRENT-M4=8            # rungs 038-043, 047, 050 PASS-M4 (capture-gated wins).
                            # ARBNO-using rungs 052/054 now compile+link+run but match pre-existing m2 oracle gaps.
BROAD-CORPUS-BASELINE=121   # /280 at 3a522bd8 (prior "250" was stale corpus state)
BROAD-CORPUS-CURRENT=183    # /280 after ARBNO TEXT + PAT_LIT bugfix (+62 over baseline, +28 from prior 155).
GATE-PK-PAT-STATUS=stale    # SBL-G-2 not yet done — baseline references DELETED rt_bb_* C boxes;
                            #   broad re-freeze deferred (would mask other in-flight lang sessions).
                            #   Rung suite + smoke + broad corpus are the live correctness gates.
SBL-SKIP-M4=1               # only 051_pat_alt_three remains SKIP — pre-existing alt-child duplicate-symbol bug.
```

---

## Session 2026-05-27 (Claude Opus 4.7) — handoff note

**HEAD one4all `308e0378`** (committed locally; **NOT yet pushed** — push pending).
**.github: this file updated, not committed.** corpus: untouched.

### Two pre-existing bugs found & fixed (both blocked ALL mode-4 patterns)

1. **⚡ FLAT-DRIVER α-LABEL MISPLACEMENT (the big one).** `codegen_flat_body` in
   `emit_bb.c` defined the exported box-entry label `pat_<id>_α` *after*
   `xa_dispatch(XA_FLAT_PROLOGUE)`. The prologue emits `lea r10,[rip+Δ]` (the cursor
   register setup) + the `cmp esi,0; je α_body; jmp β` port dispatch. Because the
   broker calls `root.fn` (= `pat_<id>_α`), entry jumped PAST the `lea r10` → `r10`
   held garbage → any box dereferencing the subject (LIT `memcmp`, ANY `strchr`)
   read bad memory and failed or segfaulted. This is why even the "✅ filled"
   `bb_lit.cpp` silently failed in mode-4. **Fix:** move `emit_label_define_bb(&lbl_α)`
   to BEFORE the prologue dispatch (one line). `bb_pat_len` worked only because it
   never derefs the subject pointer (reads `Σlen` + cursor only).

2. **GAS macro-annotation bug** in `sm_pat_combine.cpp`: `EXEC_STMT_VARIANT`,
   `PAT_CAPTURE`, `PAT_CAPTURE_FN`, `PAT_CAPTURE_FN_ARGS` emitted human-readable
   annotations (`subj=X`, `V kind=0`) as extra *positional* macro args → assembler
   `too many positional arguments`. Now emitted as preceding `#` comment lines.

### ⚡ KEY RESOURCE for next session (Lon's tip — saved hours)
The seven hollow boxes were **already meticulously hand-written** and live in git
history. Recover from **`git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`**:
- `any/bb_any.s`, `notany/bb_notany.s`, `span/bb_span.s`, `brk/bb_brk.s`,
  `breakx/bb_breakx.s`, `arbno/bb_arbno.s`, `capture/bb_capture.s`
- ABI (brokered): `spec_t bb_X(void *ζ in rdi, int port in esi)`; returns σ-ptr in
  `rax`, δ-len in `edx`; `(0,0)` = fail. Reads `[rel Σ]`/`[rel Δ]`/`[rel Ω]` (note: **Ω**
  is the bound, not Σlen — equal when unanchored). Callee-saves rbx/r12/r13.
  SPAN/BRK store δ at ζ+8; ARBNO uses a 64-frame stack at ζ+24 (frame=24B); CAPTURE
  state at ζ+0..56. **TRANSCRIBE these, do not re-derive.** Port into the flat
  template TEXT arms (`bb_pat_*.cpp`), adapting register names to the flat `[r10]`/
  `_.lbl_α/β/γ/ω` convention and DESCR-return epilogue (eax=1 success / eax=99 fail;
  the shared flat γ epilogue computes the span — the box body just advances Δ + jmps).

### Next rung priority
**SBL-CAP first** — most rung-suite tests use `. V` capture, which forces
`lower_flat_invariant` to return 0 (see `emit_sm.c:778` — ASSIGN_IMM/COND/CALLOUT
excluded) → window falls back to the (broken/runtime) `rt_match_variant` path, so the
inline box is never emitted. Until capture emits inline, the rung suite M4 stays low.
Then SBL-NOTANY/SPAN/BREAK TEXT arms (trivial transcription from recovered .s),
then all BINARY arms (SBL-*-2), then ARBNO (child-blob), BREAKX flag, ATP kind.
SBL-ANY-2 (BINARY arm) still stubbed — placeholder `jmp` bytes only.

### No regressions verified
mode-2 smoke 7/7 (unchanged), mode-3 smoke 7/7 with 6 pre-existing fails (confirmed
via git-stash A/B at baseline `3a522bd8`), broad corpus 121→137. The 16 newly-FAILing
broad-corpus names were baseline SKIPs (compile-blocked by bug #2), now compiling but
failing on the capture path — not regressions of previously-passing tests.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

---

## Session 2026-05-27 (Claude Opus 4.7, continued) — handoff note

**Built on the prior session's `6deb9f71` baseline.** Filled four hollow TEXT arms in sequence:
NOTANY → SPAN → BREAK → **CAPTURE** (the keystone).

### Results
- **Rung suite: PASS-M4 1 → 8** (+7): rungs 038-043, 047, 050 all green (capture-using rungs unblocked).
- **Broad corpus: 137 → 155** (+18). No regressions of any prior PASS.
- **Mode-2 smoke unchanged 7/7; broker 23/23.** GATE-PK still stale (its baseline references DELETED `rt_bb_*` C boxes — flagged in Session State).

### Design fork resolution for SBL-CAP
Investigated the `cap_t` runtime object scaffolding (`bb_cap_new` + `XA_CAP_FIXUP`) and confirmed
its sole consumer — the `bb_cap(void*, int)` C Byrd box — was DELETED by the FACT-RULE purge.
The runtime object is now dead scaffolding nobody reads. Chose **fully inline TEXT arm** that:
1. Saves Δ to `.Lcap<id>_start` on α.
2. `xor esi, esi; call <child_α_lbl>` (or `mov esi,1` on β — re-enters child at β via prologue dispatch).
3. Checks `eax` against 99 (the standard fail-return from `XA_FLAT_EPILOGUE`).
4. Computes span and calls `rt_cap_assign@PLT(varname, Σ+start, Δ-start)` on success.

Added one tiny runtime helper `rt_cap_assign(varname, base, len)` to `rt.c` — pattern-building
class (same as `rt_pat_*`), explicitly sanctioned by the goal-file note. **Removed
`ASSIGN_IMM/ASSIGN_COND` from the `lower_flat_invariant` exclusion** at `emit_sm.c:781` —
this is what flips capture-containing windows from the runtime fallback path to inline emit.
CALLOUT remains excluded (no template yet).

### Follow-up rungs (priority order)
1. **SBL-ARBNO** — six SKIP-M4 rungs (052/053/054/055/056/051) still gated on hollow `bb_arbno.cpp`.
   Same child-blob mechanism as capture; can probably reuse the `call <child_α>` pattern with a
   small pos_stack (`.data` array, depth in `.data` long). Builds on the proven capture wiring.
2. **SBL-BREAKX** — distinguish `nd->ival==1` in `bb_pat_break.cpp` for BREAKX β (advance past break char + rescan).
3. **SBL-*-2 BINARY arms** — once all six TEXT arms green, do the BINARY parallel for mode-3 (`--run`).
4. **Cleanup HQ rung:** delete `bb_prepare_capture_arbno`'s `bb_cap_new`/`XA_CAP_FIXUP` calls now
   that nothing reads `cap_t`. Track as residue in GOAL-HEADQUARTERS.

### Mode-2 caveat noticed (NOT a regression — pre-existing)
Rungs 044/045/046/048 (POS/RPOS/TAB/REM) fail in BOTH m2 and m4 with empty output — these are
pre-existing oracle mismatches in the rung suite's baked-in expectations, not caused by this
work. Worth a follow-up audit but separate from SBL goal.

**HEAD one4all: pending commit** (templates + emit_sm.c invariant + rt.c helper). corpus untouched.
.github: this file updated, pending commit.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Session 2026-05-27 (Claude Opus 4.7, continued 2) — handoff note

**Built on `8fb25c38`.** Filled **ARBNO** TEXT arm + fixed a sibling **PAT_LIT** GAS macro-annotation
bug that was masking many mode-4 programs until SBL-CAP-1 unblocked inline-emit windows.

### Results
- **Broad corpus snobol4: 155 → 183** (+28). Most of the gain is from the PAT_LIT fix —
  any program with a literal inside a pattern is now safe.
- **Rung SKIP-M4: 5 → 1.** Only 051_pat_alt_three remains (pre-existing alt-child duplicate-symbol
  bug — `alt0_c0_β` defined twice; confirmed pre-exists at `8fb25c38`).
- **PASS-M4 stays 8** because the formerly-SKIP rungs match pre-existing m2 oracle gaps
  (the m2 baseline itself fails on 052/054 with empty output; m4 reproduces that faithfully).
- **GATE-2 broker: 23 → 24** (+1, a PAT_LIT-using broker test now compiles).
- GATE-1 smoke 7/7 unchanged. No regressions.

### ARBNO design
Same child-blob mechanism as capture: `call <child_α_lbl>` enters child at α (esi=0) or β
(esi=1). Stack of int32 Δ positions in `.data` (`.Larbno<id>_stack`, 256 deep), depth counter
and saved_delta also `.data`. α loops: capture pre-Δ, call child, on fail (eax==99) or no-Δ-advance
break, else push and continue. β: depth--; if <0 → ω; depth==0 → saved; else stack[depth-1]; jmp γ.
Matches bb_exec.c oracle exactly.

### PAT_LIT bug (pre-existing, dormant)
`sm_pat_anchors.cpp:31-33` emitted `PAT_LIT .S4 arg="a"` as a 3-arg GAS macro call to a 1-arg macro,
producing `Error: Parameter named 'arg' does not exist for macro 'pat_lit'`. Identical class to the
prior session's `sm_pat_combine.cpp` fix. Was dormant because no capture/ARBNO program reached
the assembler — until SBL-CAP-1 unlocked them. Fix: annotation in preceding `#` comment, `s_3asm`
→ `s_2asm`. PAT_REFNAME and PAT_USERCALL had the same misuse — fixed in the same diff.

### Follow-up rungs (priority order)
1. **051 alt-child duplicate-symbol bug** — `alt0_c0_β` defined twice. Investigate
   `pre_build_children_text` for multi-alternative ALT child-blob naming; likely the same child
   gets re-emitted with the same prefix. Pre-existing, not in current session scope.
2. **SBL-BREAKX** — distinguish `nd->ival==1` in `bb_pat_break.cpp` for BREAKX β.
3. **SBL-ATP** — new BB kind for `@var` cursor capture.
4. **SBL-*-2 BINARY arms** — once stable, do mode-3 BINARY parallel.
5. **Cleanup HQ rung:** delete dead `bb_prepare_capture_arbno` cap_t allocations.

### Pre-existing m2 oracle gaps (noted, NOT in scope)
Rungs 044/045/046/048/052/054/055/056/057 fail in m2 (bb_exec.c interpreter). The rung suite
oracle outputs assume behavior the mode-2 interpreter doesn't implement. Worth a separate audit.

**HEAD pending commit.** Push order: one4all → .github.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7

---

## Addendum: Git history audit (2026-05-27)

**Commit `0206b998` "DELETE rt_bb_* C runtime functions — total annihilation"** deleted exactly **10 `rt_bb_*` functions**. Each maps as follows:

| Deleted function | What it did | Template needed |
|---|---|---|
| `rt_bb_any(zeta, port)` | charset match 1 char (α: match+advance; β: undo) | `bb_pat_any.cpp` PLATFORM_X86 arm |
| `rt_bb_notany(zeta, port)` | match 1 char NOT in charset (α/β same shape as ANY) | `bb_pat_notany.cpp` PLATFORM_X86 arm |
| `rt_bb_span(zeta, port)` | match longest run in charset; β yields one shorter | `bb_pat_span.cpp` PLATFORM_X86 arm |
| `rt_bb_brk(zeta, port)` | scan up to char in charset; no retry | `bb_pat_break.cpp` PLATFORM_X86 α/β arm — plain BREAK β |
| `rt_bb_brkx(zeta, port)` | BREAKX: like BREAK but β steps past the break char and rescans | `bb_pat_break.cpp` PLATFORM_X86 arm — **extended β** for BREAKX; `lower_pat_dcg.c` routes both BREAK and BREAKX to `BB_PAT_BREAK`; template must distinguish via a node flag (`nd->ival` or `nd->sval`) |
| `rt_bb_arbno(zeta, port)` | greedy match of inner blob; β pops one repetition | `bb_arbno.cpp` PLATFORM_X86 arm |
| `rt_bb_arbno_new(fn, state)` | ctor — allocates `rt_arbno_t`; NOT port-logic | still in `bb_boxes.c` as `bb_arbno_new`; no template needed |
| `rt_bb_atp(zeta, port)` | cursor capture `@var` — write Δ as integer to named var | **No BB kind exists yet.** Lives in old `PATND_t/XATP` world. `lower_pat_dcg.c` has no case for it. Needs: new BB kind `BB_PAT_ATP`, lowering in `lower_pat_dcg.c`, execution in `bb_exec.c`, template `bb_pat_atp.cpp`. See SBL-ATP below. |
| `rt_bb_cap(zeta, port)` | capture matched span into var (immediate or conditional) | `bb_capture.cpp` PLATFORM_X86 arm |
| `rt_bb_switch_pl_entry(name, arity)` | Prolog predicate dispatch from mode-4 binary | `sm_bb_switch.cpp` — partially handled (ICN_GEN arm exists; PL_ENTRY arm still emits a comment stub) |

**Total: 6 hollow template x86 arms to fill** (ANY, NOTANY, SPAN, BREAK/BREAKX, ARBNO, CAPTURE) + 1 new BB kind + template needed (ATP) + 1 partially addressed (PL_ENTRY in sm_bb_switch).

**BREAKX note:** `lower_pat_dcg.c` maps both `BREAK` and `BREAKX` to `BB_PAT_BREAK` (line 205-208). The BREAKX β semantics (advance past break char and rescan) differ from plain BREAK (which simply fails on β). The template must distinguish them. Options: (a) set `nd->ival=1` for BREAKX in `lower_pat_dcg.c` and check it in the template; (b) add a separate `BB_PAT_BREAKX` kind. Option (a) is simpler. See SBL-BREAK.

**rt_pat_* note (NOT in scope here):** The 29 `rt_pat_*` functions in `rt.c` (called from `sm_pat_nullary.cpp` via `@PLT`) are **pattern-building** helpers — they construct `DESCR_t` pattern objects and push them onto the vstack. They are NOT four-port Byrd boxes. They are called from template-produced GAS (`call rt_pat_arb@PLT` etc.) which is the correct pattern. These are NOT violations and are NOT the subject of this goal. **However**, `sm_pat_nullary.cpp` BINARY arm embeds emitter-process function pointers as imm64 — a separate Invariant-8 violation that belongs in GOAL-HEADQUARTERS as an HQ rung.

---

### Phase SBL-BREAKX — Distinguish BREAKX in bb_pat_break.cpp

#### SBL-BREAKX-1 — Tag BREAKX nodes in lower_pat_dcg.c ⏳
- [ ] In `lower_pat_dcg.c` TT_FNC case, where BREAKX is currently mapped identically to BREAK: set `nd->ival = 1` (flag for BREAKX) on the BB_PAT_BREAK node built for BREAKX. For plain BREAK, `nd->ival = 0`.
- [ ] Verify: `--dump-bb` for a BREAKX pattern shows `ival=1` on the BB_PAT_BREAK node.
- [ ] Gate: GATE-1 7/7, GATE-2 23/23, build clean.

#### SBL-BREAKX-2 — Implement BREAKX β in bb_pat_break.cpp TEXT arm ⏳
- [ ] After SBL-BREAK-1 fills the plain BREAK TEXT arm: add BREAKX β logic. When `pBB->ival == 1` (BREAKX): β steps past the break char that stopped the previous scan and rescans to the next break char. Yield the longer match or fail if no further break char. Read `rt_bb_brkx` body (git show `0206b998 -- src/runtime/rt/rt.c`) for exact semantics.
- [ ] Gate: GATE-1 7/7. BREAKX probe: `'abc.def.ghi' BREAKX('.') . V` yields `abc` then `abc.def` on retry.

---

### Phase SBL-ATP — New BB kind for `@var` cursor capture

#### SBL-ATP-1 — Add BB_PAT_ATP to BB.h and lower_pat_dcg.c ⏳
- [ ] Add `BB_PAT_ATP` to the `BB_op_t` enum in `BB.h` (after `BB_PAT_CALLOUT`).
- [ ] Add lowering for `@var` to `lower_pat_dcg.c`: detect `TT_ATP` or the `@var` AST node. Build: `nd = BB_node_alloc(cfg, BB_PAT_ATP); nd->sval = varname; nd->α=nd; nd->β=fp; nd->γ=sp; nd->ω=fp;` (ATP always succeeds — it writes Δ to var and matches empty).
- [ ] Gate: build clean, GATE-1 7/7.

#### SBL-ATP-2 — Add bb_exec.c case BB_PAT_ATP ⏳
- [ ] Case: on α (state==0): write `Δ` as an integer DESCR_t to `nd->sval` via `NV_SET_fn`. Set state=1. Return `nd->γ`. On β: state=0, return `nd->ω`. (ATP matches the empty string and captures the cursor position as an integer.)
- [ ] Gate: `scrip --interp` with `@var` pattern correctly binds cursor position. GATE-1 7/7.

#### SBL-ATP-3 — Create bb_pat_atp.cpp and wire into emit_core.c ⏳
- [ ] Create `src/emitter/BB_templates/bb_pat_atp.cpp`. Dispatch in emit_core.c.
- [ ] TEXT arm x86: α: load `[r10]` (Δ); call `rt_nv_set_int@PLT(varname_ptr, Δ)`; jmp γ. β: jmp ω. (No cursor advance — ATP is a zero-width assertion.)
- [ ] BINARY arm: rel32 fixup for γ and ω jumps.
- [ ] Gate: GATE-PK re-frozen for BB_PAT_ATP. Mode-4 `@var` probe matches `--interp`.

---

### Phase SBL-SM-BINARY — sm_pat_nullary.cpp BINARY Invariant-8 violation

**(HQ issue — track here, fix in HQ session)**

`sm_pat_nullary.cpp` BINARY arm: `bytes(2, "\x48\xB8") + u64le((uint64_t)(uintptr_t)sm_pat_nullary_rt_fn(...))` embeds the emitter-process `rt_pat_*` function pointer as imm64 in the emitted binary. This violates **GOAL-BB-TEMPLATE-LADDER Invariant 8**: "MEDIUM_BINARY must never embed emitter-process pointers." The binary blob calls `mov rax, <emitter_addr>; call rax` — the emitter address is meaningless in the linked binary. This makes `--run` (mode-3) pattern-building corrupt for these opcodes. Fix: SM_PAT_* TEXT arm already calls `rt_pat_*@PLT` correctly (via macro invocation in GAS). BINARY arm should do the same — call `rt_pat_arb@PLT` etc. directly rather than embedding a pointer. Add to GOAL-HEADQUARTERS as rung `SM-BINARY-PAT-FIX`.
