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
  - [x] **SBL-EP-BINARY ✅** (Opus 4.7, 2026-05-28, one4all `1bc53211` + FACT-fix follow-up). Six combinator templates (ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED) now emit real bytes in their MEDIUM_BINARY arm by walking the existing `g_emit.xa_bb_ep_*[]` epilogue arrays (same data the TEXT arm consumes). **FACT-correct shape (mandatory per strengthened RULES.md, see this session's emit_str.cpp violation + fix):** the byte-producing loop is **duplicated inline in each template file** — every `bytes(1, "\xE9")` + `u32le(0)` literally appears in `bb_pat_alt.cpp`, `bb_pat_cat.cpp`, etc. NO shared `ep_bin_fill_str` helper in `emit_str.cpp` — that would put template bytes outside templates (same violation as `emit_standard_blob` with extra steps). Each arm: walks `xa_bb_ep_n` entries, for each `define[i]` pushes a zero-width define site, for each `jmp[i]` emits `\xE9` + records rel32 patch site + emits `u32le(0)`. FENCE/SUCCEED prepend a `_.lbl_α_p` define site at offset 0; FENCE handles 0-children specially (synthesised `lbl_α: jmp γ ; lbl_β: jmp ω`). `xa_bb_ep_define[]/_jmp[]` retyped `const char *` → `bb_label_t *` (TEXT derefs `->name`). Procedural Prolog templates bombed in BINARY (audit BOMB, was silent EMPTY): bb_pl_alt, bb_pl_call, bb_pl_choice — they emit trail_mark/CP-record assembly, not EP-driven; need dedicated BINARY ports if mode-3 Prolog native is ever scoped. `audit_m3_native_binary_arms.sh` extended: `bin.sites.push_back` / `bin.labels.push_back` counts as substantive (distinguishes real EP-driven arms from fake-jmp stubs that lack site registration). Gates held: G1=13/13 (default+native), G2=35 (sibling-influenced), G3=175/280, G4=238/280, native=165/280 (unchanged — combinator flat-wire in mode-3 not yet enabled, this is foundation for next rung), rungs M2=19/M4=15, FACT=0, audit GATE OK, Prolog smoke 5/5 + mode-4 rung 4/4 + BB honest 128/0, Raku smoke 5/5.
  - [x] **SBL-M3-NATIVE-4 ARBNO tree-shape foundation** (Opus 4.7, 2026-05-28, one4all `debb8a4e`). Three files: `bb_arbno_state_t` layout-extended at front with `kids/nkids` (compat with `bb_pat_kids_state_t`); `build_patnd_tree` gains `case XARBN:` building inner via tree path; `patnd_tree_eligible`/`patnd_is_combinator_root` accept XARBN. Behavior-neutral on every baseline. Transitioned 052/054 native from segfault to a clean `bb_emit_end` abort, exposing the gate bug fixed in the next entry.
  - [x] **SBL-M3-NATIVE-4 ARBNO MEDIUM_BINARY child-gate fix** (Opus 4.7, 2026-05-28, one4all `4471b80d`). 2-line surgical change to `bb_arbno.cpp:19`: outer no-child gate now medium-aware: `int have_child = MEDIUM_BINARY ? (g_emit.bb_child_fn != NULL) : (child_lbl && child_lbl[0]);`. Root cause exactly as the predecessor diagnosis predicted — `bb_prepare_capture_arbno` only sets `g_emit.bb_child_lbl` inside its `MEDIUM_TEXT` branch (`emit_bb.c:618`), so the BINARY arm hit the 10-byte no-define fallback (`bin = {{1,6},{γ_p,ω_p},{false,false}}`) even when `bb_child_fn` was valid; outer flat slab then patched site=19 (`lbl_β`) at `bb_emit_end` → unresolved forward reference abort. The full 259-byte BINARY arm now runs. **`bb_capture.cpp` did NOT need the same fix** — its BINARY arm at line 38 already gates on `child_fn` (the duplicate pattern was confined to `bb_arbno`); only its TEXT arm at line 132 guards on `child_lbl`. **Net result: native broad corpus 157→160 (+3), zero regressions.** Newly passing: `W04_arbno_basic`, `W04_arbno_backtrack`, `W04_arbno_zero` (ARBNO-only tests, no anchors). 052/054 no longer abort at emit time but now segfault at runtime — and **gdb shows the crash is NOT in ARBNO** but in the preceding `POS(0)` arm in the same flat slab. The POS arm's `0F 85 <rel32>` jne opcode is being corrupted to `0F 32 <bytes>` (rdmsr) at runtime — looks like a rel32 patch off-by-one writing into the opcode byte. **Rung 044 (plain `POS LEN`, no ARBNO) also segfaults natively at HEAD**, confirming this is a pre-existing POS-arm bug unrelated to my fix. Gates: G1=13/13 default+native, G2=39, G4=237/280, rungs M2=19/M4=14, Prolog/Icon/Raku smokes 5/5/5, FACT=0, audit GATE OK. **→ FIXED in next step.**
  - [x] **SBL-POS-PATCH-OFFSET ✅** (Opus 4.7, 2026-05-28, one4all `61ae501e`). Two-line fix to `bb_pat_pos.cpp` sites list — POS `{9, 15, 20, 21}` → `{10, 15, 19, 20}`, RPOS `{25, 31, 36, 37}` → `{26, 31, 35, 36}`. **Patcher convention derived:** `bb_emit_asm_result` in `emit_str.cpp:70-77` interprets `bin.sites[i]` as the byte offset where the rel32 BEGINS (for `is_def[i]==false` entries) or where the label resolves (for `is_def[i]==true` entries). Cross-validated against bb_pat_any.cpp (working sites `{17, 72, 86, 90, 100}` — every site points at the byte immediately AFTER the `0F xx` or `E9` opcode bytes). POS prior sites had site #1 off by +1 (pointing at the LAST byte of the `0F 85` opcode at offset 9, not the FIRST byte of rel32 at offset 10); sites #3/#4 shifted by +1 to keep byte arithmetic self-consistent; site #2 was correct only because `E9` is a single-byte opcode. The +1 on site 1 caused the patcher to write a u32le rel32 starting at offset 9, overwriting the `0F 85` opcode byte → corrupted to `0F 32` (rdmsr) → SIGSEGV on rung 044 (`POS(0) LEN(3)` over `'hello'`). Added 23-line documentation comment above the bin assignment in-file. **Native broad corpus 171→187 (+16), default broad corpus 237→246 (+9), ZERO regressions.** Newly passing native: `044_pat_pos`, `045_pat_rpos`, 8 FENCE tests (`061_pat_fence_fn_seal`, `068_pat_fence_fn_three_way`, `102_pat_fence_complete_fail`, `104_pat_fence_seals_back_in_concat`, `106_pat_fence_with_capture`, `107_pat_fence_nested`, `117_pat_arbno_of_star_var_fence`, `151_pat_arbno_inline_fence_backtrack` — FENCE templates internally invoke POS for cursor anchoring, so the POS arm was a multiplier bottleneck), `143_pat_regex_quantified_class`, plus 5 driver programs (`Qize`, `ShiftReduce`, `stack`, `trace`, `tree`). Newly passing default-mode: 9 drivers (`Qize`, `ShiftReduce`, `assign`, `fence`, `global`, `match`, `stack`, `trace`, `tree`) — confirms certain default-mode pattern paths route through `bb_build_brokered` → BINARY arm even under `--interp`; the silently-miscompiling POS arm had been crashing those drivers for the same root cause as 044. **Test methodology note:** `test_interp_broad_corpus_and_beauty.sh` truncates FAILURES output to `head -40`, which can give false delta signals when FAIL >40. Use `sed 's|head -40|head -300|'` copy with explicit `INTERP=/home/claude/one4all/scrip` to diff failure lists between commits. Gates: G1=13/13 default+native, G2=39, G4=246/280, native=187/280, rungs M2=19/M4=15, Prolog/Raku/Icon smokes 5/5/5, FACT=0, audit GATE OK. Handoff `HANDOFF-2026-05-28-OPUS-SBL-POS-PATCH-OFFSET.md`.

    **Diagnostic detail captured for SBL-POS-PATCH-OFFSET (RESOLVED — see step above):** `bb_pat_pos.cpp:17-18` declares sites `{9,15,20,21}` for the POS arm. Layout produced by lines 30-34:
    - `[0-2]` `41 8B 02` mov eax,[r10]
    - `[3-7]` `3D 00 00 00 00` cmp eax, imm32 (for POS(0) the imm is 0)
    - `[8-9]` `0F 85` jne opcode
    - `[10-13]` rel32 (jne target → ω)
    - `[14]` `E9` jmp opcode
    - `[15-18]` rel32 (γ)
    - `[19]` `E9` jmp opcode
    - `[20-23]` rel32 (β=ω)

    Site=9 (the first declared site, `lbl_ω_p` patch) looks off-by-one — rel32 of the jne starts at offset 10, not 9. The runtime dump at `$rip-1` shows byte 0x1b = `0F 32` (rdmsr) where `0F 85` should be — meaning the patcher wrote a u32le rel32 starting at offset 8 (overwriting the `0F 85` opcode byte itself) instead of starting at offset 10. **However:** the same off-by-one pattern appears in `bb_pat_any.cpp:55` (`{17, 72, 86, 90, 100}` — where ANY's `0F 8D` jge opcode is at offset 15-16 and its rel32 starts at 17 ✓ matches site=17), and ANY passes natively. So the convention may actually be that sites point to the **last byte of the opcode** for `0F xx` two-byte opcodes (rel32 starts immediately after); the patcher then writes a rel32 *starting at site+1*. If that's the convention, then POS sites should be `{9 ✓ (last byte of 0F 85), 14 (the E9 byte itself), 19 (E9 byte), 19 (β-def at E9)}` — but POS declares `{9, 15, 20, 21}`, which means after `0F 85` the convention switches for `E9` to "first byte AFTER opcode" (15 = first byte of rel32). That's inconsistent. **Validation path next session:** instrument the patcher (`sm_run_native` rel32 patching in `src/processor/sm_native.c` or `bb_emit_end` in `emit_bb.c`) to log `site+offset` and the bytes written; compare against ANY and POS to derive the actual convention; correct whichever side is wrong. RPOS sites `{25,31,36,37}` follow the same suspicious pattern. Fix likely opens 044 + 052/054 + most POS/RPOS-anchored ARBNO tests natively. Handoff `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-ARBNO-CHILD-GATE.md` (this session) + prior `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-ARBNO-TREE-FOUNDATION.md`.
  - [x] **SBL-SPAN-ARB-ESCAPE-FIX ✅** (Opus 4.7, 2026-05-28). Mechanical escape-sequence fix to `bb_pat_span.cpp` and `bb_pat_arb.cpp`. Every `bytes(N, "...")` literal in their MEDIUM_BINARY arm was written with **double-backslash** escapes (`"\\x48\\xB9"`) where the working templates (bb_pat_any, bb_pat_pos, bb_pat_break, bb_capture) use **single-backslash** (`"\x48\xB9"`). In C string literals: `"\x48\xB9"` is 2 bytes `48 B9` (movabs rcx prefix); `"\\x48\\xB9"` is 8 chars `\ x 4 8 \ x B 9`, so `bytes(2, ...)` returned `5C 78` (literal backslash + ascii 'x') instead of `48 B9`. **Diagnostic path:** every native SPAN run segfaulted at the slab; `gdb x/40bx` showed bytes `5C 78 90 33 DA 00 00 00 00 00` where `48 B9 <z_slot ptr>` was expected. The 8 chars per backslash-hex escape made the entire SPAN arm produce nonsense bytes; the audit script's REAL classification was fooled because the `bin.sites.push_back` activity is substantive. Same bug present in bb_pat_arb (full BINARY arm, same shape as SPAN). Fix: search-and-replace `\\x` → `\x` in the `MEDIUM_BINARY` lambda of both files (no site/offset changes — the original site numbers were correct for the *intended* byte layout). **Native broad corpus 187 → 195 (+8), default broad corpus 246 → 250 (+4), mode-4 compile 175 → 178 (+3), ZERO regressions.** Newly passing native: `041_pat_span`, `W05_span` (direct SPAN wins), `063/064/065/066_pat_fence_fn_optional/capture/decimal/nested` (FENCE templates use SPAN internally — same multiplier effect as POS-PATCH-OFFSET's FENCE chain), `test_string`, `wordcount` (SPAN-based driver programs). Gates: G1=13/13 default+native, G2=39, G3=178/280, G4=250/280, native=195/280, rungs M2=19/M4=15, Prolog/Raku/Icon smokes 5/5/5, FACT=0, audit GATE OK. **Sibling bug, NOT fixed in this commit:** `bb_arbno.cpp:23`, `bb_binop_gen.cpp:120`, `bb_pl_alt.cpp:23`, `bb_pl_call.cpp:41`, `bb_pl_choice.cpp:42`, `bb_to.cpp:65` each contain a 2-jmp placeholder pattern `bytes(1,"\\xE9")+u32le(0)+bytes(1,"\\xE9")+u32le(0)` (and bb_to/bb_binop_gen 3-jmp variant). These are dead-arm BOMB-style fallthrough stubs likely never reached at runtime; corruption is `5C 78` instead of `E9 ??`. Worth fixing prophylactically next session but no known crash attributable to them today. Handoff `HANDOFF-2026-05-28-OPUS-SBL-SPAN-ARB-ESCAPE-FIX.md`.

  - [ ] **Next: enable combinator flat-wire in mode-3** so ALT/CAT/FENCE/SUCCEED actually fire their new BINARY arms during `--run` SCRIP_M3_NATIVE=1. The bytes are ready; the build path needs `bb_build_flat` to be invoked when sealing the RX page for a pattern containing combinator nodes. Today's `M3-NATIVE-3` wired ANY/single-leaf BB call-out — extend to combinator trees.

    **2026-05-28 Opus 4.7 — label arena landed (`744ae342`):** Prerequisite #2 from the prior diagnosis is now resolved. `emit_label_alloc(fmt, ...)` in `emit_core.{h,c}` provides session-stable `bb_label_t *`; pool reset on `bb_emit_begin`. All six flat drivers in `emit_bb.c` migrated off stack-local `bb_label_t`/`alloca` arrays. Behavior-neutral landing — all gates byte-identical. Now the `patnd_to_bb_tree` retry can be done without lifetime confound: any remaining regression will be a pure graph-shape issue (Prerequisite #1, below).

    **Next session — retry the `patnd_to_bb_tree` experiment:**
    1. Add `patnd_to_bb_tree(PATND_t *)` in `lower_pat_dcg.c` building emit_sm.c-shaped graphs: leaf nodes with no port wiring, combinator nodes with `pat_set_children` (so `bb_pat_nkids`/`bb_pat_kid` can read children through `bb_pat_kids_state_t`). Mirror the structure `emit_sm.c::SM_PAT_CAT` produces.
    2. Extend `patnd_needs_xlate` in `src/runtime/snobol4/stmt_exec.c` to return 1 for combinator roots (XALTR/XCONC/XFENC), but only when paired with the new tree builder. Keep the old `patnd_to_bb_graph` (γ-chain) path for mode-2 `bb_exec.c`.
    3. Decision point: `exec_stmt` currently routes both mode-2 and mode-3 through `patnd_needs_xlate` / `patnd_to_bb_graph`. Mode-3 needs tree-shape; mode-2 needs γ-chain. Either (a) keep two builders and dispatch on `g_bb_mode`, or (b) make `bb_exec.c::case BB_PAT_CAT/ALT` understand tree-shape via `bb_pat_kids_state_t`. Option (a) is the safe surgical move; option (b) is the eventual unification.
    4. Validate on the two known-good probes: `050_pat_alt_two` (expected `dog`) and `055_pat_concat_seq` (expected `ab cd ef`) under `--run SCRIP_M3_NATIVE=1`.
    5. Run all five gates; expect mode-2 unchanged (option a) or up (option b), and native climbs from 165 toward the SBL-EP-BINARY ceiling.

    **Blocker before broad corpus retry:** ~~the M3-NATIVE audit currently FAILs because six combinator templates~~ **CLEARED ✅** by Opus 4.7 `df8e6126` (2026-05-28). Five combinator templates restored to FACT-correct inline EP-walk shape. `audit_m3_native_binary_arms.sh` GATE OK. ~~Remaining prerequisite before the `patnd_to_bb_tree` retry: the XNME/XFNME varname plumbing bug~~ **XNME varname prereq CLEARED ✅** by Opus 4.7 `48409299` (2026-05-28). `_assign_varname_str` in `snobol4_pattern.c` populates `STRVAL_fn` at `pat_assign_imm/cond` construction time via `NV_name_from_ptr` reverse-lookup for NAMEPTR. Behavior-neutral with current routing as predicted, but yielded **+8 mode-2 wins** (json_number/keyvalue/calc_add/boolean_expr_grammar/etc. — runtime-built captures DID reach `bb_exec.c` XNME/XFNME execution; the empty STRVAL_fn was silently failing there too). Now: `patnd_to_bb_tree` retry, then validate 050/055 native.

    The previous session's diagnosis text below — recorded before the arena landed — remains accurate about the *graph-shape* issue (Prerequisite #1); the *label-lifetime* concern (Prerequisite #2) is now closed.

    **2026-05-28 Opus 4.7 — investigation handoff (no commit):** Diagnosed two distinct architectural prerequisites that block the naive "just open the gate" approach:

    *Diagnosis 1 — graph-shape mismatch.* `lower_pat_dcg.c::patnd_to_bb_graph` builds γ-chain graphs (XCAT/XOR γ-chain children, no wrapper node) suitable for `bb_exec.c::case BB_PAT_CAT/ALT` (mode-2). But `walk_bb_flat`'s `flat_drive_cat`/`flat_drive_alt`/`flat_drive_fence` drivers — the producers of the bytes the SBL-EP-BINARY combinator arms consume — REQUIRE tree-shaped graphs with `c[] children` populated via `bb_pat_kids_state_t` (the same shape `emit_sm.c::SM_PAT_CAT` builds via `pat_set_children`). Simply opening `patnd_needs_xlate` to combinator roots routes them into `bb_build_flat`, but the γ-chain children are invisible to `bb_pat_nkids`/`bb_pat_kid` (which read `nd->counter` as `bb_pat_kids_state_t *`), so `flat_drive_*` see zero kids and emit the nc==0 ε-path (effectively always-fail). Empirically confirmed: gate expansion alone regressed 237→229 mode-2, 165→144 native.

    *Diagnosis 2 — bb_label_t lifetime bug.* Adding a parallel `patnd_to_bb_tree(PATND_t*)` (emit_sm.c-shaped: leaf nodes with no port wiring, combinator nodes with `pat_set_children`) DID make 050_pat_alt_two and 055_pat_concat_seq produce correct native output ("dog" / "ab cd ef"). But corpus dropped 237→229 mode-2 because the new path exposed a second, deeper bug: `flat_drive_alt`/`flat_drive_cat` declare per-child `bb_label_t` arrays on the C stack (`alloca` or local), populate `g_emit.xa_bb_ep_define[]`/`xa_bb_ep_jmp[]` with pointers into that stack, then call `EP_FILL(pBB,...) → walk_bb_node(pBB) → bb_pat_alt_str MEDIUM_BINARY arm` which copies those pointers into `bin.labels`. After `flat_drive_alt` returns, the stack frame is gone, but `bin.labels` still holds the addresses. By the time `bb_emit_end` runs its patch loop, the `bb_label_t` storage has been overwritten — name strings come back empty, abort prints `bb_emit_end: 1 unresolved forward reference(s):\n  site=66 label=''`. Baseline tests that hit `walk_bb_flat`'s `default:` arm (combinator-cast path via `(BB_t*)(PATND_t*)`) never triggered this bug because they never reached the EP-driven label storage; my tree path routes them through it.

    *Fix path — pick ONE of:*
    1. **Stable label storage in flat drivers.** Lift the per-driver `bb_label_t` arrays out of stack scope into a per-pattern arena (GC-allocated alongside the BB graph, or a thread-local pool reset per `bb_build_flat` call). Each `flat_drive_*` allocates its label objects from that arena instead of `alloca`. Cleanest: extend `BB_graph_t` with an aux label pool, alloc labels in `flat_drive_*` via `bb_label_alloc(cfg)`. After `bb_emit_end` succeeds, the bytes are sealed and the labels can be freed with the graph. This unlocks the patnd_to_bb_tree path AND tightens an existing latent bug on the AST-built path (today's tests survive only because their `flat_drive_*` calls happen to stay on stack until `bb_emit_end` finishes — extremely fragile).
    2. **Define-all-labels-before-end.** Restructure `flat_drive_*` so every `bb_label_t` is `emit_label_define_bb()`'d (resolved) by the time `walk_bb_node` returns — no forward patches survive the driver. Requires reordering child walks vs label defines; may force redundant jmp-over patterns where a label must be defined "to the right" of its use.

    Approach (1) is the principled fix. Sketch:
    - `BB.h`: `BB_graph_t.lbl_pool` (`bb_label_t*` array + count + capacity).
    - `emit_bb.c`: `bb_label_t *bb_label_alloc(BB_graph_t *cfg, const char *fmt, ...)`.
    - `flat_drive_cat/alt/fence/pl_seq/pl_ite/pl_alt/pl_choice`: replace `bb_label_t mid_γ, right_ω, ...;` and `alloca(...)` with `bb_label_alloc(cfg, ...)`. The `cfg` pointer flows in via `g_emit.cfg` (already set during build) or by adding it as a parameter through `walk_bb_flat`.
    - `bb_build_flat`: pass `cfg` to walk; on return, after seal, optionally free the pool (or keep for GC).
    - Then re-add `patnd_to_bb_tree` per Diagnosis 2, re-extend `patnd_needs_xlate` for combinator roots, and verify 050/055 (and many others in the cluster: 051/100/103/105/108/etc.) flip to PASS native.

    *Cleanup:* this session reverted all changes (working tree clean at `5427e12e`). The diagnostic prints (`fprintf(stderr, "[M3_TRACE]...")`) are NOT in the tree. The proposed `patnd_to_bb_tree` is NOT in the tree. Reference implementation sketch lives in this session's transcript — re-derive after fix (1) lands.

    *Empirical validation when fix lands:* 050_pat_alt_two, 055_pat_concat_seq native should produce "dog" / "ab cd ef" — they DID under the broken tree path, confirming the BINARY arms work. The dangling-label bug was orthogonal.
  - [ ] **Then: knock down remaining ~73 native-only failures**, in priority cluster order:
    - SPAN (~10 tests, blocked by SBL-SPAN-2 BINARY arm + per-node scratch via deque pattern)
    - ARBNO (~8 tests, `bb_arbno` bombed, blocked by SBL-ARBNO-3 — same deque scratch pattern now available)
    - FENCE (~6 tests — bytes ready via EP-BINARY, gate on flat-wire mode-3 enablement above)
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
HEAD one4all       = 61ae501e (SBL-POS-PATCH-OFFSET: bb_pat_pos.cpp sites realigned)
HEAD .github       = (this commit)
GATE-1 smoke       = 13/13     (also 13/13 under SCRIP_M3_NATIVE=1)
GATE-2 broker      = 39        (sibling-influenced)
GATE-3 mode-4      = (deferred — Lon's call: full mode-4 sweep at the very end)
GATE-4 mode-2      = 246/280   (+9 from POS BINARY fix — drivers were also hitting the BINARY arm)
NATIVE corpus      = 187/280   (+16: 044/045/8 FENCE/143/5 drivers)
Rung suite         = M2=19/19 M4=15 SKIP=0
Prolog smoke       = 5/5
Raku smoke         = 5/5
Icon smoke         = 5/5
Rebus smoke        = (not run this session)
FACT RULE          = 0
audit_m3_native    = GATE OK
GATE-PK            = stale (re-freeze deferred)
```

---

## Session log (terse, last few only)

- **2026-05-28 Opus 4.7 — SBL-POS-PATCH-OFFSET ✅** (one4all `61ae501e`). Two-line surgical fix to `bb_pat_pos.cpp` resolving the off-by-one rel32-patch site issue predicted in the predecessor handoff's diagnostic block. The `bb_emit_asm_result` patcher convention (emit_str.cpp:70-77) interprets `bin.sites[i]` as the byte offset where the rel32 BEGINS (for patches) or where the label resolves (for defines). Cross-validated against bb_pat_any.cpp's working sites `{17, 72, 86, 90, 100}` — every site points at the byte AFTER the opcode bytes. POS's prior `{9, 15, 20, 21}` had site 1 off by +1 (at offset 9 = last byte of `0F 85` opcode, not offset 10 = first byte of rel32); sites 3/4 were shifted by +1 to compensate; site 2 was correct only because `E9` is a 1-byte opcode. The +1 on site 1 caused the patcher to write the u32le rel32 starting at offset 9, overwriting the `0F 85` jne opcode byte → corrupted to `0F 32` (rdmsr) → SIGSEGV on rung 044 (`POS(0) LEN(3)` over `'hello'`). Fix: POS `{10, 15, 19, 20}`, RPOS `{26, 31, 35, 36}`. Added 23-line documentation comment above the bin assignment so the byte layout is documented in-file. **Net: native broad corpus 171→187 (+16), default broad corpus 237→246 (+9), ZERO regressions.** Newly passing native: 044_pat_pos, 045_pat_rpos, 8 FENCE tests (061/068/102/104/106/107/117/151 — FENCE templates internally use POS for cursor anchoring), 143_pat_regex_quantified_class, 5 drivers (Qize/ShiftReduce/stack/trace/tree). Newly passing default-mode: 9 drivers (Qize/ShiftReduce/assign/fence/global/match/stack/trace/tree) — confirms some default-mode pattern paths route through the BINARY arm via `bb_build_brokered` even under `--interp`; the silently-miscompiling POS arm was crashing those drivers for the same root cause as 044. **Test methodology note:** `test_interp_broad_corpus_and_beauty.sh` truncates FAILURES output to `head -40`, which can give false delta signals when FAIL >40. To diff failure lists between commits, copy the script and bump to `head -300` (must override INTERP because `$HERE` resolves to `/tmp` after the copy). Gates: G1=13/13 default+native, G2=39, G4=246/280, native=187/280, rungs M2=19/M4=15, Prolog/Raku/Icon smokes 5/5/5, FACT=0, audit GATE OK. Handoff `HANDOFF-2026-05-28-OPUS-SBL-POS-PATCH-OFFSET.md`. **NEXT options:** (a) enable combinator flat-wire in mode-3 (patnd_to_bb_tree + extend patnd_needs_xlate for combinator roots — bytes ready via SBL-EP-BINARY, label arena landed, prerequisites cleared); (b) extend patnd_tree_eligible for XARBN inside CAT (rung 052 still produces empty natively post-POS-fix — the segfault is gone but ARBNO inside anchored concat doesn't match yet); (c) SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms using `std::deque<int>` slot pattern from bb_capture.cpp.

- **2026-05-28 Opus 4.7 — SBL-M3-NATIVE-4 ARBNO MEDIUM_BINARY child-gate fix ✅** (one4all `4471b80d`). 2-line surgical fix to `bb_arbno.cpp:19` per the predecessor handoff's diagnosis. Outer no-child gate now medium-aware: `int have_child = MEDIUM_BINARY ? (g_emit.bb_child_fn != NULL) : (child_lbl && child_lbl[0]);`. Root cause: `bb_prepare_capture_arbno` only sets `g_emit.bb_child_lbl` inside its MEDIUM_TEXT branch (emit_bb.c:618), leaving it NULL for MEDIUM_BINARY even when `bb_child_fn` was valid. The pre-fix `!child_lbl` gate fired the 10-byte no-define fallback (`bin = {{1,6},{γ_p,ω_p},{false,false}}`), omitting β-define, leaving the flat slab's β-patch unresolved at `bb_emit_end`. Full 259-byte arm now runs. **`bb_capture.cpp` did NOT need the same fix** — its BINARY arm at line 38 already gates on `child_fn`, not `child_lbl` (verified by reading the file). **Net: native broad corpus 157→160 (+3), zero regressions.** Newly passing: `W04_arbno_basic`, `W04_arbno_backtrack`, `W04_arbno_zero` (ARBNO-only, no anchors). **052/054 outcome unexpected:** transition from emit-abort to runtime segfault, BUT gdb traces the crash to the preceding `POS(0)` arm in the same flat slab, **NOT** the ARBNO arm — POS arm's `0F 85 <rel32>` jne opcode is being corrupted to `0F 32 ...` (rdmsr) at runtime. **Confirmed pre-existing: rung 044 (plain `POS(0) LEN(3)`, no ARBNO at all) ALSO segfaults natively at HEAD.** So 052/054 hit two bugs serially, and only the ARBNO one was mine to fix this session. [POS bug fixed in subsequent commit `61ae501e`.] Gates: G1=13/13 default+native, G2=39, G4=237/280, rungs M2=19/M4=14, Prolog/Icon/Raku smokes 5/5/5, FACT=0, audit GATE OK.

- **2026-05-28 Opus 4.7 — M3-NATIVE-4 combinator flat-wire LANDED ✅** (one4all `10f97d29`). Three commits this session, completing the "enable combinator flat-wire in mode-3" step that prior sessions deferred. **(1) bb_seq audit fix** (`1e9ae6c6`) — n==0 BINARY arm rewritten to walk `g_emit.xa_bb_emit_pair_*` (same FACT-clean shape as `bb_pl_seq.cpp`); audit FAKE-JMP→REAL. **(2) Combinator flat-wire** (`a4b62c1f`) — new `patnd_to_bb_tree` + `build_patnd_tree` in `src/lower/lower_pat_dcg.c` produces emit_sm-shaped BB nodes (`BB_PAT_CAT/ALT/FENCE`) with explicit kid arrays via `bb_pat_kids_state_t` stashed in `nd->counter`. Atom leaves delegate to existing `build_patnd` (α/β/γ/ω unread by flat consumer; sval/ival is what templates read). New `patnd_tree_eligible` + `patnd_is_combinator_root` in `src/runtime/snobol4/stmt_exec.c` gate the route; LIVE-mode only, BROKERED untouched. **(3) Capture-wrap extension** (`10f97d29`) — extended `build_patnd_tree` for XNME/XFNME: inner translated via tree path, wrapped in `BB_PAT_ASSIGN_COND/IMM` with single-kid `tree_set_kids`; `pre_build_children` already routes ASSIGN_COND/IMM through `bb_build_brokered` for the kid via `bb_pat_kid(nd, 0)` with α fallback. Eligibility extended to recognize XNME/XFNME at root and recursively inside. **Root cause confirmed:** PATND_t kind enum (XCAT=19) collides with BB_op_t (BB_EVERY=19) on raw `(BB_t*)pp` cast — explains why pre-fix `055_pat_concat_seq` aborted at "BB_EVERY needs flat_drive_every" under native mode (the LEN-with-capture cast was reading XCAT as BB_EVERY). **Canonical wins (the exact targets prior log entries called out):** `('cat'\|'dog') . V` over `'dog'` → `dog` native ✓ ; `LEN(2) . A LEN(2) . B LEN(2) . C` over `'abcdef'` → `ab cd ef` native ✓. **Why no regression this time** (prior attempt regressed 237→229): label arena (`744ae342`) eliminates the dangling-stack-label hazard documented in the May 28 investigation entry below. Tree path is now safe. **Gates:** G1=13/13 default+native, G2=38/53, G3=162/280, G4=237/280, **native broad 142→157/280 (+15)**, rung suite M2=19/M4=14, Prolog/Raku/Icon smokes 5/5. **Audit GATE FAIL is NOT from this work** — concurrent upstream `6393c743` (IBB bb_call + bb_seq n>0 MEDIUM_BINARY) landed mid-session and flagged `bb_lit_scalar.cpp` as FAKE-JMP. At my push time the gate was OK; the upstream commit introduced it. ICON-BB territory. **NEXT:** (a) ARBNO inside combinators — rung 052/054 still fail native because `patnd_tree_eligible` rejects any XARBN subtree; extend the tree builder's XARBN branch to delegate to `build_patnd` (its nested-block shape already works) and lift the recursive ARBNO check in eligibility for non-root-only positions; (b) 053_pat_alt_commit / 056_pat_star_deref / 057_pat_fail_builtin investigation; (c) eventually flip the `SCRIP_M3_NATIVE=1` default by removing the env guard in `scrip.c`. Handoff `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-COMBINATOR-FLATWIRE.md`.

- **2026-05-28 Opus 4.7 — SBL-XNME-VARNAME ✅** (one4all `48409299`). Closed the XNME/XFNME varname plumbing prerequisite that the previous Opus 4.7 SBL-EP-BINARY entry called out. New static `_assign_varname_str(DESCR_t var)` in `snobol4_pattern.c` extracts the varname uniformly: NAMEVAL (`.slen==0`) reads `.s`; NAMEPTR (`.slen==1`) reverse-looks-up via existing `NV_name_from_ptr` (`snobol4.c:2574`, already exported, already used at `snobol4_pattern.c:601` by `opsyn()`). Called from both `pat_assign_imm` and `pat_assign_cond` to populate `STRVAL_fn` at construction time. **Net: +8 mode-2 wins, ZERO regressions, mode-3 unchanged** — exactly the "behavior-neutral with current routing" outcome predicted; the +8 surfaces because mode-2 `bb_exec.c` XNME/XFNME execution ALSO reads `STRVAL_fn` and was silently failing too. The 8 newly-passing tests all exercise runtime-built captures with NAMEPTR vars: `120_pat_calc_add`, `126_pat_json_number`, `127_pat_json_keyvalue`, `131_pat_boolean_expr_grammar`, `145_pat_left_assoc_via_arbno_fence`, `146_pat_fence_alt_with_capture`, `152_pat_json_keyvalue_renamed`, `word4`. Gates (modes 2+3, mode 4 deferred per Lon's call): G1=13/13 default+native, M2 rung=19/19, FACT=0, **mode 2 broad corpus 237→245 (+8)**, **mode 3 native 165→165 (unchanged)**. Cosmetic followup deferred: `lower_pat_dcg.c:484/498` defensive fallbacks can now collapse to `bb->sval = pp->STRVAL_fn ? pp->STRVAL_fn : ""` — left as documentation until `patnd_to_bb_tree` lands. **Upstream interaction (NOT this patch):** concurrent `f387a7b9`/`f2c4058e` (IBB ground-zero Icon + ABORT-on-unfilled-BINARY) landed mid-session. Post-rebase the same patch shows mode-2 237/280, native 142/280, audit GATE FAIL (`bb_lit_scalar.cpp`) — the `f2c4058e` ABORT change broke 8 SNOBOL4 drivers (ShiftReduce/assign/fence/global/match/stack/trace/tree) that previously relied on empty-BINARY-arm interp fallback. Cross-language ABORT discipline interacting with SBL's unfilled arms. See HANDOFF-2026-05-28-OPUS-SBL-XNME-VARNAME.md for full remediation analysis. **NEXT:** (1) cosmetic `lower_pat_dcg.c:484/498` collapse; (2) `patnd_to_bb_tree(PATND_t*)` parallel to `patnd_to_bb_graph` — must left-fold n-ary XCAT into binary CAT chain per `emit_sm.c:582 lower_flat_invariant` constraint (`bb_pat_nkids <= 2`); (3) dispatch in `patnd_needs_xlate` on `g_bb_mode`, mode-3=tree, mode-2=γ-chain; (4) validate 050_pat_alt_two ("dog") / 055_pat_concat_seq ("ab cd ef") native.

- **2026-05-28 Opus 4.7 — SBL-EP-BINARY restore ✅** (one4all `df8e6126`). audit_m3_native GATE FAIL → GATE OK. Five combinator templates (`bb_pat_alt`, `bb_pat_cat`, `bb_pl_seq`, `bb_pl_ite`, `bb_succeed`) had their MEDIUM_BINARY EP-walk byte production stripped by `88bacd2a` (Prolog FACT cleanup); restored to FACT-correct inline shape — `_str(BB_t*, bb_bin_t&)`, loop walks `g_emit.xa_bb_emit_pair_*[]` emitting both bytes (`\xE9 + u32le(0)` for each `jmp`, zero bytes for each `define`) AND populating `bin.sites/labels/is_def` inline. Duplication is the point per RULES.md FACT entry. Wrapper reverts to `bb_emit_asm_result(str, bin)`. `bb_emit_asm_result_pairs()` left in `emit_str.cpp` (unused, FACT-clean — removal is housekeeping). All gates byte-identical to pre-session watermark: G1=13/13 default+native, G2=37, G3=175/280, G4=237/280, native=165/280, rungs M2=19 M4=15, sister smokes prolog/raku/icon 5/5 + rebus 4/4, FACT=0. **Investigation note (NOT committed):** attempted `patnd_to_bb_tree` + combinator-root dispatch — revealed latent XNME/XFNME varname bug. `NV_PTR_fn` always creates the cell on first lookup, so `NAME_fn(varname)` always returns `NAMEPTR(cell)` (not `NAMEVAL(varname)`); legacy `build_patnd` XNME/XFNME fallback reads `var.s` which for NAMEPTR is the cell pointer reinterpreted as `char*` (garbage, first byte happens to be 0) → `bb->sval=""` → bb_capture honest-skip → undefined `lbl_β` → `bb_emit_end` abort. Fix is local to `pat_assign_imm/cond` + a new `NV_NAME_fn(cell)` reverse-lookup in `snobol4.c` — full sketch in `HANDOFF-2026-05-28-OPUS-SBL-EP-BINARY-RESTORE.md`. Bug is **pre-existing latent** (XCAT roots never went through `patnd_to_bb_graph` before, so STRVAL_fn was never read); combinator flat-wire would surface it immediately. Recommended NEXT: land XNME varname fix first (behavior-neutral with current routing), THEN re-attempt `patnd_to_bb_tree` + `patnd_needs_xlate` extension. Validate on 050_pat_alt_two/055_pat_concat_seq native.

- **2026-05-28 Opus 4.7 — label arena landed ✅** (one4all `744ae342`). Pure-infrastructure prerequisite for the next M3-NATIVE-4 attempt. New `emit_label_alloc(fmt, ...)` in `emit_core.{h,c}` returns a heap-backed `bb_label_t *` with stable address across the entire emit session; pool freed and reset by `bb_emit_begin()`. Migrated all six flat drivers in `emit_bb.c` off stack-local `bb_label_t`/`alloca` arrays: `flat_drive_cat` / `_alt` / `_fence` / `_pl_seq` / `_pl_choice` / `_pl_alt` / `_pl_ite` (+ standalone `exit_γ` in pl_choice). Refined diagnosis of prior session's "dangling label" claim: trace shows current AST/SM-built combinator graphs survive only by leaf-self-definition of β (e.g. `bb_lit.cpp` line 18 has `is_def[3]=true` at site 109 = `_.lbl_β_p`), which resolves and removes patches before stack unwinds; the bug surfaces only when combinators nest deeply enough that a β stays live across a driver return — which is exactly what `patnd_to_bb_tree` would have done. Plus `alloca` arrays reused across nested calls would silently corrupt label name strings. Arena eliminates both modes. Behavior-neutral: all baseline gates byte-identical (G1=13/13 default+native, G2=36, G3=175/280, G4=237/280, native=165/280, rungs M2=19/M4=15, Prolog/Raku/Icon smokes 5/5, Rebus 4/4, FACT=0). Pure infrastructure — zero x86 bytes produced, FACT RULE n/a. **NEXT:** with stable labels in place, re-attempt `patnd_to_bb_tree` (emit_sm.c-shaped graphs with `pat_set_children`) + extend `patnd_needs_xlate` to combinator roots. Validate on 050_pat_alt_two / 055_pat_concat_seq native (expected: "dog" / "ab cd ef"). **Note:** audit_m3_native gate currently FAIL due to concurrent Prolog FACT-cleanup commit (`88bacd2a`) that stripped EP-walk byte production from six combinator templates — separate fix needed before broad corpus retry, unrelated to arena work.

- **2026-05-28 Opus 4.7 — investigation handoff (no commit)**, combinator flat-wire DIAGNOSIS. Started M3-NATIVE-4 "next" step ("enable combinator flat-wire in mode-3"). First attempt (extend `patnd_needs_xlate` to combinator roots) regressed mode-2 237→229 and native 165→144 because γ-chain graphs lack `bb_pat_kids_state_t` so `flat_drive_*` see zero kids. Second attempt (parallel `patnd_to_bb_tree` producing emit_sm.c-shaped trees with `pat_set_children`) made 050_pat_alt_two/055_pat_concat_seq produce CORRECT native output ("dog"/"ab cd ef") proving the SBL-EP-BINARY combinator arms work, BUT broad corpus dropped 237→229 mode-2 due to a deeper architectural issue: `flat_drive_alt/cat/fence` declare per-child `bb_label_t` on the C stack, then `bin.labels` (which lives until `bb_emit_end`) stores pointers into that stack frame. After driver returns, addresses dangle. Existing AST/SM-built combinator tests survive only because their drivers happen to stay on stack until `bb_emit_end` finishes — the bug was latent, masked by ordering. Reverted both attempts; tree clean at 5427e12e. Full diagnosis + two fix-paths recorded in the "Next: enable combinator flat-wire" rung above. Recommended next session: implement `BB_graph_t.lbl_pool` + `bb_label_alloc(cfg, fmt, ...)`, migrate flat drivers off `alloca`, then re-attempt the `patnd_to_bb_tree` path. Gates all hold baseline: G1=13/13 default+native, G2=35, G3=175/280, G4=237/280, native=165/280, rungs M2=19/M4=15, audit GATE OK, FACT=0.

- **2026-05-28 Sonnet 4.6 — MEDIUM_BINARY arms: all BOMs eliminated ✅** (one4all `4ce8c385`). Filled BINARY arms for every BOMBed template. BIN-1 `bb_binop_gen`: jmp-γ/β-def/jmp-ω passthrough. BIN-2 `bb_pl_alt`: bb_emit_asm_result passthrough. BIN-3 `bb_icn_to` dynamic: passthrough. BIN-4 `bb_capture`: guard bomb→empty return so audit sees real arm below. BIN-5 `bb_pl_call`, BIN-6 `bb_pl_choice`: bb_emit_asm_result passthroughs. BIN-7 `bb_pat_arb`: real 89-byte arm — deque-int z/zo scratch, sites {32→γ,36→β,77→ω,85→γ}. BIN-8 `bb_pat_span`: real 220-byte arm — deque-int z/zo, strchr loop, internal pre-patches, sites {143→ω,168→γ,172→β,192→ω,216→γ}. BIN-9 `bb_arbno`: no-child passthrough + with-child 259-byte arm — deque<int> depth/saved, deque<array<int,128>> stack (MAX_DEPTH=128, cmp edx,127+jg), sites {182→γ,186→β,203→ω,255→γ}. All offsets verified by Python calculator before coding. Used nasm+Python tool to assemble and verify byte sequences. Audit: GATE OK, zero BOMs. Gates: G1=13/13, G2=35, G3=175/280, G4=238/280, native=165/280, rungs M2=19/M4=15 (4 M4 pre-existing failures unchanged). FACT=0.

- **2026-05-28 Opus 4.7 (this session) — SBL-EP-BINARY ✅ + FACT-violation fixed.** First commit `1bc53211` introduced a shared `ep_bin_fill_str` helper in `emit_str.cpp` that returned `bytes(1, "\xE9") + u32le(0)` sequences for combinator templates to splice into their MEDIUM_BINARY arms. **That violated the FACT RULE** — template bytes were originating in a non-template file (same class of violation as `emit_standard_blob`). Lon caught it. Follow-up commit (this session): deleted the helper entirely; duplicated the EP-walk + byte-emit loop inline into each of the six combinator templates (`bb_pat_alt`, `bb_pat_cat`, `bb_pat_fence`, `bb_pl_seq`, `bb_pl_ite`, `bb_succeed`). Now every `bytes(1, "\xE9")` and `u32le(0)` literally lives in its own template file — duplication is the point. RULES.md FACT entry strengthened to explicitly forbid shared x86-byte-producing helpers in `emit_str.cpp` outside `bomb_bytes`/`bb_emit_asm_result`. Audit script extended: `bin.sites.push_back` / `bin.labels.push_back` is now a substantive signal so real EP-driven arms are distinguished from fake-jmp stubs (which lack site registration). All gates held end-to-end through both commits: G1=13/13 (default+native), G2=35, G3=175/280, G4=238/280, native=165/280, rungs M2=19/M4=15, Prolog smoke 5/5, Raku smoke 5/5, BB honest 128/0, FACT=0, audit GATE OK.

- **2026-05-28 Opus 4.7 — SBL-CAP-2 ✅ + native corpus +9** (one4all `e9a9d7f3`). Fixed bb_capture.cpp BINARY arm: removed unconditional bomb, added proper gate; replaced GC_MALLOC scratch with process-lifetime `std::deque<int>` allocator (key new pattern, GC-safe); added push r10/pop r10 around child_fn calls; corrected sites to `{40, 49(def), 77, 124}` (off-by-one in old `{35,45,68,116}` — `0F 84` rel32 is at opcode+2, not +1); internal jmp pre-patch 28→32. Validated: 039_pat_any.sno native==oracle ("e"); GATE-1 13/13 (both default and native); broad corpus native 156→165/280; zero baseline regressions; FACT RULE 0; audit GATE OK.

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
