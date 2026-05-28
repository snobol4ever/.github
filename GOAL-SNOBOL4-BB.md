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

- **Mode 2 (`--interp`):** `sm_interp_run` + `bb_exec.c` C oracle. Templates not exercised.
- **Mode 3 (`--run`):** End state = `sm_run_native` → SM_templates BINARY arms → sealed RX → jump in. BB call-outs via flat-wired `bb_build_flat`. Currently opt-in via `SCRIP_M3_NATIVE=1`; default path still routes to `sm_interp_run` (interp fallback for unbuilt opcodes/arms). Per ARCH-SCRIP: **no C interp, all langs, no BB graph walking** on this path.
- **Mode 4 (`--compile`):** Emit phase uses TEXT arms → GAS → gcc link. Standalone runtime builds pattern blobs via `bb_build_brokered` → template BINARY arms.

**Absolute rules (RULES.md):**
- No C Byrd boxes. No `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω.
- TEMPLATE-PURITY: every `_str()` body is `state → std::string`, zero `emit_text_n` inside.
- ONE x86 PRODUCER: all emission via `BB_templates/` template functions.
- HQ Invariant 0: returning `std::string()` is a STUB. Stub LOUD — `bomb_bytes()` not silent empty.
- X86 ONLY FOR NOW.
- MODE PURITY: no silent cross-mode fallback; no silent eps substitution on failed build.

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)` which sets `g_emit.lbl_α/β/γ/ω` then calls `walk_bb_node(nd)`. The template emits:

```
<lbl_α>:    α-port code (fresh entry — match, advance Δ, jump γ or ω)
<lbl_β>:    β-port code (retry — undo, advance differently, jump γ or ω)
            (some kinds: β = lbl_ω directly — no retry)
```

**Runtime state in TEXT arm:**
- `[r10]` = Δ (cursor, 32-bit int)
- `[rip + Σ]` = ptr to subject; `[rip + Σlen]` = length
- `nd->sval` = charset string (ANY/SPAN/BREAK/NOTANY) — baked into `.data`
- `nd->counter` (int64) = runtime mutable state for generators

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing the byte offset of each rel32 patch. Use `movabs` for absolute addresses. Reference templates: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104B, sites {17,72,86,90,100}), `bb_pat_notany.cpp`, `bb_pat_break.cpp` (178B), `bb_capture.cpp` (128B; see below).

**Per-node persistent BINARY storage (SHARED PATTERN):** brokered blobs have no ELF `.data`. Two patterns now established:
1. `g_emit.bb_cs_zeta` `rt_cs_t {const char *chars; int delta;}` — `delta @+8` for SPAN/ARBNO loop counters; address baked via `movabs rcx, &zeta`; allocated by emit_bb for charset templates.
2. Process-lifetime `std::deque<int>` allocator (e.g. `cap_alloc_saved_delta_slot()` in bb_capture.cpp) — pointer never invalidates, GC-safe via C++ heap (does not depend on Boehm scanning mmap'd bb_pool). Use this pattern for SPAN-2 / CAP / BREAKX scratch.

DO NOT use `GC_MALLOC` for per-node scratch baked as imm64 — bb_pool is mmap'd, GC can't see the address, scratch may be freed.

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                # GATE-1: 13/13
bash scripts/test_smoke_unified_broker.sh         # GATE-2: ~30-36 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh   # GATE-3: 175/280
bash scripts/test_interp_broad_corpus_and_beauty.sh # GATE-4: 238/280
bash scripts/test_snobol4_pat_rung_suite.sh       # M2=19 M4=15 SKIP=0
bash scripts/audit_m3_native_binary_arms.sh       # GATE OK (no fake-jmp stubs)
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh # 165/280
```

(For full failure list use `INTERP=... bash /tmp/test_all.sh` with `head -300` patched in — the stock script truncates failures at -40.)

---

## Open Rungs (priority order)

### SBL-M3-NATIVE — mode-3 is PURE x86, NO INTERPRETER ⏳ TOP PRIORITY

**End state (ARCH-SCRIP):** mode 3 `--run` = `IR → sm_lower → sm_codegen → sm_jit_run`, native x86 only at runtime. No `sm_interp_run`, no `bb_exec_*`, no PC-dispatch loop, no BB-graph traversal in C.

**Current state:** `scrip.c:449-454` gates native behind `SCRIP_M3_NATIVE=1` (opt-in); default still calls `sm_run_with_recovery(sm, sm_interp_run)`. Native runner exists: `src/processor/sm_native.c` `sm_run_native(SM_sequence_t*)` — drives `codegen_sm_dispatch` over the SM array in BINARY mode through an `open_memstream` sink, copies bytes into a `sm_image` SEG_CODE slab, seals RX, two-pass rel32 patches JUMP/JUMP_S/JUMP_F, enters via 16-aligned trampoline.

**SM-template BINARY coverage (audit GATE OK):** 13/15 REAL: sm_arith, sm_bb_switch, sm_calls, sm_compare, sm_defines, sm_expr_incr, sm_frame_slots, sm_halt, sm_jumps, sm_pat_anchors, sm_pat_combine, sm_pat_nullary, sm_push_pop_lits, sm_returns. sm_label correctly emits zero bytes.

**Recovery resource for unbuilt arms:** the deleted native-SM engine lives in git history (deleted 2026-05-27 JA-D series, principled removal — used forbidden `emit_standard_blob`/`SL_B`/`bake_blob_call`). Recover semantic spec (NOT verbatim bytes) from:
- Engine A (trampoline + h_* handlers): `git show 2073c081~1:src/processor/sm_jit_interp.c`
- Engine B (SB-LINEAR, the ARCH end-state, +799 lines built 916d61a5): `git show 22a17fa3~1:src/processor/sm_jit_interp.c`

Transcription rule: re-express through `SM_templates/*.cpp` MEDIUM_BINARY arms, driven by `codegen_sm_x86` in BINARY medium, sealed via `sm_image`.

**Steps:**

- [x] **M3-NATIVE-0** — BOMB THE STUBS (Opus 4.7, 2026-05-28). `rt_bomb`/`bomb_text`/`bomb_bytes` infrastructure built template-pure (FACT clean). 8 genuine stubs bombed: `bb_pat_span`, `bb_pat_arb`, `bb_arbno`, `bb_capture`, `bb_binop_gen`, `bb_icn_to` dynamic branch, `sm_jump_group`, `sm_return-family`. Audit gate added: `scripts/audit_m3_native_binary_arms.sh` — classifies arms REAL/BOMB/TRIVIAL-JMP/EMPTY, fails on undocumented fake-jmps. Deferred (per-file semantic judgment): `bb_pat_alt`, `bb_pat_cat`, `bb_succeed`, Prolog `bb_pl_alt/_call/_choice/_ite/_seq`.

- [x] **M3-NATIVE-1** — emitter coverage audit (Opus 4.7, partial). Script live: `scripts/audit_m3_native_binary_arms.sh`. SM coverage 13/15 REAL. **TODO:** annotate each arm with deleted `h_*`/`sl_*` semantic-spec reference; classify the 8 deferred EMPTY/COMMENT combinator arms.

- [x] **M3-NATIVE-2 + 2b** — `sm_run_native` runner + JUMP/RETURN BINARY arms (Opus 4.7 + Sonnet 4.6, 2026-05-28). First-ever non-bombing native mode-3 execution. JUMP/JUMP_S/JUMP_F rel32 with two-pass patching; RETURN/FRETURN/NRETURN call rt_do_return; SM_PAT_LIT + SM_CALL_FN rdi-arg fixes. 7+ jumpless programs verified native==interp.

- [x] **M3-NATIVE-3** — BB call-out from native SM (Sonnet 4.6, 2026-05-28, `910d55c3`). ANY pattern fires via flat-wired BINARY arm under `--run` SCRIP_M3_NATIVE=1. Path: `sm_run_native` → `rt_match_variant` → `exec_stmt` (BB_MODE_LIVE) → `bb_build_flat` → BINARY template. 12/13 smokes pass natively.

- [/] **M3-NATIVE-4** — per-language bring-up + corpus parity. SNOBOL4 first.
  - [x] `define` smoke now passes (was blocker per earlier handoff — resolved likely via 08e05f68 LANG-IGNORANT changes). GATE-1 SCRIP_M3_NATIVE=1 = 13/13.
  - [x] **bb_capture BINARY arm FIXED** (Opus 4.7, 2026-05-28, this session): replaced unconditional `bomb_bytes` early-return with proper 128-byte arm. Process-lifetime `std::deque<int>` saved_Δ slot (NOT GC_MALLOC). `push r10`/`pop r10` around child_fn calls. Sites {40, 49(def), 77, 124}; internal jmp rel32 = 32. Validated on 039_pat_any.sno + smoke. Native corpus 156→165/280 (+9): fixed 039_pat_any, 040_pat_notany, 042_pat_break, 043_pat_len, 058_capture_dot_immediate, 059_capture_dollar_deferred, W07_capt_cond/fail/imm. ZERO new regressions. All baseline gates hold.
  - [ ] **Next: knock down the remaining ~73 native-only failures**, in priority cluster order:
    - SPAN (~10 tests, blocked by SBL-SPAN-2 BINARY arm + per-node scratch via deque pattern)
    - ALT (~6 tests, `bb_pat_alt` is EMPTY/COMMENT in audit — combinator deferred from M3-NATIVE-0)
    - ARBNO (~8 tests, `bb_arbno` bombed, blocked by SBL-ARBNO-3 — same scratch facility now available)
    - FENCE (~6 tests, suggest bb_pat_fence native correctness — investigate, may be combinator like ALT)
    - POS/RPOS/TAB/RTAB/REM/ARB/TWO (~10 tests, individual arms)
    - capture-multiple/complex compositions (~10 tests, derive from atomic fixes above)
  - [ ] Flip default to native (remove getenv gate at scrip.c:449), with honest `[NO-SM-BB]` failure for unbuilt arms.

- [ ] **M3-NATIVE-5** — gate sweep + corpus, all langs. Honest failure for unbuilt opcodes.

**Mode-4 sibling (separate goal):** SBL-M4-FLATWIRE — `--compile` standalone brokers at runtime instead of flat-wiring at emit time. Defer until after M3-NATIVE done; shares native-x86 infra.

---

### SBL-CAP-2 — capture template ✅ (this session 2026-05-28)

Closed by M3-NATIVE-4 capture fix above. BINARY arm:
- Sites: `{40 (ω-jmp rel32), 49 (β label-define), 77 (ω-jmp rel32), 124 (γ-jmp rel32)}`
- 128 bytes total
- Internal jmp→assign pre-patch rel32 = 32 (after-addr 49, target 81)
- ABI: r10=&Δ on entry; child preserves via `push r10`/`pop r10`; child_fn(rdi=0, esi=entry); `rt_cap_assign_cursor(rdi=varname, esi=saved_Δ, edx=cur_Δ, ecx=imm)`.
- saved_Δ slot via `cap_alloc_saved_delta_slot()` — process-lifetime `std::deque<int>` (NOT GC_MALLOC).

**KEY PATTERN ESTABLISHED:** the deque-int allocator is the GC-safe replacement for `GC_MALLOC(sizeof(int))` for per-template-call BINARY scratch. SPAN-2, ARBNO-3, BREAKX-2 should all use this same pattern.

---

### SBL-SPAN-2, SBL-ARBNO-3 — BINARY arms ⏳

**SPAN:** generator; β yields successively shorter spans using ABSOLUTE z_orig (NOT `[r10]`-relative — sibling box in concat mutates `[r10]` between α and β re-entry). Needs TWO persistent int slots (z, z_orig). Prior attempt (2026-05-28) widened `rt_cs_t` with `delta2 @+12`; arm disassembled correctly but segfaulted (GC freed `rt_cs_t` baked as imm64). **Reverted; retry now using the `std::deque<int>` slot-pair pattern from bb_capture.cpp** (NOT GC_MALLOC, NOT `rt_cs_t` widening).

**ARBNO:** uses `nd->counter` generator state; TEXT β re-enters child. Closer to capture — use deque pattern + brokered child call (movabs + call). Reference: now-working bb_capture.cpp.

Validate via `--run` (mode 3 WIRED), not `--compile` (which uses TEXT arms only).

---

### SBL-BREAKX-2 — BREAKX BINARY + β rescan ⏳

BREAKX (`pBB->ival==1`) needs own BINARY arm. TEXT β does rescan-to-next using z_orig + z. Two int slots — use deque pattern. Reference deleted `rt_bb_brkx` via `git show 0206b998 -- src/runtime/rt/rt.c`.

---

### SBL-XNME-XLATE ⏳ (paired-prereq DONE in `828f9134`)

Translator XNME/XFNME fallback (`pp->var.s`) and `rt_pat_capture` STRVAL_fn population landed. Gate widening NOT applied — was paired with SBL-CAP-2 which is now closed. Re-evaluate whether the widening is still needed and apply if yes.

Insert in `src/runtime/snobol4/stmt_exec.c` `patnd_needs_xlate` after `patnd_is_simple_atom`:
```c
static int patnd_is_capture_wrapped_safe(const PATND_t *pp) {
    if (!pp) return 0;
    if (pp->kind != XNME && pp->kind != XFNME) return 0;
    if (pp->nchildren < 1 || !pp->children || !pp->children[0]) return 0;
    const PATND_t *inner = pp->children[0];
    return patnd_is_simple_atom(inner) || patnd_contains_arbno(inner);
}
```
Then: `return patnd_contains_arbno(pp) || patnd_is_simple_atom(pp) || patnd_is_capture_wrapped_safe(pp);`

---

### SBL-ATP — `@var` cursor capture ⏳
1. Add `BB_PAT_ATP` to `BB_op_t` in `BB.h`.
2. `lower_pat_dcg.c`: `@var` → `nd->sval=varname; nd->α=nd; nd->β=fp; nd->γ=sp; nd->ω=fp`.
3. `bb_exec.c case BB_PAT_ATP`: α writes Δ as int DESCR via NV_SET; return γ. β: return ω.
4. `bb_pat_atp.cpp` template + emit_core dispatch.

### SBL-G-2 — Re-freeze GATE-PK ⏳
Re-freeze each kind's cell in `test_per_kind_diff.sh`. Baseline references deleted `rt_bb_*` boxes — stale.

### SBL-SM-BINARY (HQ-track) ⏳
`sm_pat_nullary.cpp` BINARY arm embeds emitter-process `rt_pat_*` fn-ptr as imm64 — Invariant-8 violation. Fix: call `rt_pat_*@PLT` directly.

### SBL-LOWER-CLEANUP ⏳
Delete `lower_subj_pat_split` + lower.c:1750 duplicate after Snocone confirmed unused.

### SBL-VERIFY-1/2 — corpus climb ⏳
After all BINARY arms + SBL-ATP + SBL-XNME-XLATE: target ≥260/280 broad corpus.

### Pre-existing m2 oracle gaps (audit-only) ⏳
Rungs 044/045/046/048/052/054/055/056/057 fail m2 too. `bb_exec.c` doesn't implement what rung suite expects for POS/RPOS/TAB/REM/star_deref/fail_builtin. Separate session.

---

## Completed (summary)

**Templates with x86 TEXT arms filled:**
LIT, ARB, LEN, POS/RPOS, TAB/RTAB, REM, ALT, CAT, FENCE, ABORT, EPS, FAIL, ANY, NOTANY, BREAK (plain), SPAN, ARBNO, CAPTURE, DEFER.

**Templates with x86 BINARY arms filled (validated via `--run` mode 3 WIRED):**
LIT, LEN, POS, UPTO (ref). ANY, NOTANY, BREAK (plain), CAPTURE — all VERIFIED-BY-EXECUTION. Others stub/bomb.

**Runtime translators:**
- `patnd_to_bb_graph()` in `lower_pat_dcg.c` — runtime PATND_t→BB_graph_t. Gated by `patnd_needs_xlate`. Covers XARBN-containing trees + simple-atom roots. Does NOT cover XNME/XFNME yet (SBL-XNME-XLATE pending).

**Driver/runtime fixes:**
- BREAK no-terminator failure (oracle + TEXT + BINARY uniformly fixed; previously succeeded incorrectly per SPITBOL)
- FLAT-DRIVER α-LABEL placement; PAT_LIT/REFNAME/USERCALL macro-arg fix; nested-ALT EP_RESET; statement-level `S P` → TT_SCAN
- `rt_cap_assign(varname, base, len)` + `rt_cap_assign_cursor(varname, sΔ, cΔ, imm)` helpers
- SM_PAT_BREAKX opcode separated from SM_PAT_BREAK
- BB_PAT_DEFER opcode + `rt_defer_match` + XDSAR resolve
- Pattern rung suite `test_snobol4_pat_rung_suite.sh` (rungs 038-057)
- `bb_boxes.c` C Byrd boxes + `rt_bb_*` deleted (FACT RULE, JA-D-3)
- bomb infrastructure: `rt_bomb`, `bomb_text`, `bomb_bytes`, audit script
- `cap_alloc_saved_delta_slot()` in bb_capture.cpp — GC-safe deque-int scratch pattern, reusable

**Recovery resource:** original hand-written boxes at `git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`. Native-SM engine at `git show 22a17fa3~1:src/processor/sm_jit_interp.c` (semantic spec only — bytes go through templates).

---

## Session State

```
HEAD one4all       = 08e05f68 (DIRTY: src/emitter/BB_templates/bb_capture.cpp uncommitted)
HEAD .github       = 70f5ce3a (clean)
GATE-1 smoke       = 13/13     (also 13/13 under SCRIP_M3_NATIVE=1)
GATE-2 broker      = 31        (sibling-influenced)
GATE-3 mode-4      = 175/280
GATE-4 mode-2      = 238/280
NATIVE corpus      = 165/280   (was 156 — +9 from bb_capture BINARY arm fix this session)
Rung suite         = M2=19 M4=15 SKIP=0
FACT RULE          = 0
audit_m3_native    = GATE OK
GATE-PK            = stale (re-freeze deferred)
```

---

## Session log (terse, last few only)

- **2026-05-28 Opus 4.7 (this session) — SBL-CAP-2 ✅ + native corpus +9.** Fixed bb_capture.cpp BINARY arm: removed unconditional bomb, added proper gate; replaced GC_MALLOC scratch with process-lifetime `std::deque<int>` allocator (key new pattern, GC-safe); added push r10/pop r10 around child_fn calls; corrected sites to `{40, 49(def), 77, 124}` (off-by-one in old `{35,45,68,116}` — `0F 84` rel32 is at opcode+2, not +1); internal jmp pre-patch 28→32. Validated: 039_pat_any.sno native==oracle ("e"); GATE-1 13/13 (both default and native); broad corpus native 156→165/280; zero baseline regressions; FACT RULE 0; audit GATE OK. Goal file pruned 700+→~290 lines this session.

- **2026-05-28 Opus 4.7 (i) — LANG-IGNORANT SM TEMPLATES (`08e05f68`).** Ripped 9 language-sniffing forks from SM/BB templates. Whacked `SM_BB_PUMP_PROC`. Split `SM_BB_SWITCH` into `SM_BB_INVOKE` + `SM_BB_PL_INVOKE`. Mis-design recorded: PL_INVOKE collapsible after Prolog lower refactor. Gates held except Icon (0/5, expected). Raku frontend relied on deleted user-sub frame-management fast-path. See HANDOFF-2026-05-28-OPUS-LANG-IGNORANT-SM-TEMPLATES.md.

- **2026-05-28 Sonnet 4.6 — M3-NATIVE-3 ✅ (`910d55c3`).** BB call-out confirmed; ANY fires BINARY arm natively. SM_CALL_FN rdi fix. 12/13 native smokes.

- **2026-05-28 Sonnet 4.6 — M3-NATIVE-2b ✅ (`d16c6780`).** JUMP/JUMP_S/JUMP_F + RETURN-family BINARY arms; two-pass rel32 reloc; SM_PAT_LIT rdi fix. Verified native==interp on multiple flow patterns.

- **2026-05-28 Opus 4.7 — M3-NATIVE-2 FIRST SLICE ✅.** Built `sm_run_native(SM_sequence_t*)` template-pure (open_memstream sink, sm_image SEG_CODE, seg_seal RX, 16-aligned trampoline). Verified native==interp on 7 jumpless programs. Wired behind `SCRIP_M3_NATIVE` env (default unchanged).

- **2026-05-28 Opus 4.7 — M3-NATIVE-0 ✅.** Bomb infra: `rt_bomb`/`bomb_text`/`bomb_bytes` template-pure. 8 stubs bombed. Audit script `scripts/audit_m3_native_binary_arms.sh` gates fake-jmps. Thesis confirmed: bombing JUMP+RETURN regressed nothing because mode-3 was still running C interpreter.

- **2026-05-28 Opus 4.7 — discovery + rescope.** ROOT CAUSE: `scrip.c` mode_run was calling `sm_run_with_recovery(sm, sm_interp_run)` — mode-3 RAN MODE-2 INTERPRETER. Native-SM engine had been BUILT (`916d61a5`, +799 SB-LINEAR) then DELETED (JA-D series, FACT RULE — used `SL_B`/`emit_standard_blob`). Rescoped SBL-M3-FLATWIRE → SBL-M3-NATIVE: foundational engine build through templates, NOT a dispatch-arm tweak.

- **2026-05-28 Opus 4.7 — SBL-BREAK-VERIFY ✅.** ANY/NOTANY/LEN/BREAK BINARY arms verified-by-execution via `--run`. BREAK no-terminator FAIL semantics fix (oracle + TEXT + BINARY).

- **2026-05-28 Opus 4.7 — SBL-NOTANY-2 ✅.** BINARY arm (104B, byte-identical to ANY except `jne` vs `je`).

- **2026-05-28 Opus 4.7 — SBL-BREAK-2 ✅.** BINARY arm (178B, sites {150→γ, 154→β-def, 174→ω}). KEY PATTERN: `rt_cs_t.delta @+8` shared scratch via `bb_cs_zeta`.

(Older log entries pruned; check git history of GOAL-SNOBOL4-BB.md for full archive.)

---

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- Mode-3 native runner: `src/processor/sm_native.c sm_run_native`
- PATND legacy: `src/runtime/snobol4/stmt_exec.c exec_stmt` DT_P branch
- Translator gate: `src/runtime/snobol4/stmt_exec.c patnd_needs_xlate`
- Pattern-building runtime helpers: `src/runtime/rt/rt.c rt_pat_*` (called @PLT from templates)
- Bomb infra: `src/emitter/emit_str.{cpp,h}` bomb_text/bomb_bytes; `src/runtime/rt/rt.c rt_bomb`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
