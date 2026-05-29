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

- **Mode 2 (`--interp`):** `sm_interp_run` + `bb_exec.c` C oracle.
- **Mode 3 (`--run`):** `sm_run_native` → SM_templates BINARY arms → sealed RX → jump in. BB call-outs via flat-wired `bb_build_flat`. Opt-in via `SCRIP_M3_NATIVE=1`; default still `sm_interp_run`.
- **Mode 4 (`--compile`):** Emit phase uses TEXT arms → GAS → gcc link. Standalone runtime builds pattern blobs via `bb_build_brokered` → template BINARY arms.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY (no silent cross-mode fallback / no silent eps substitution).

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)`. Template emits α-port code (fresh: match, advance Δ, jump γ or ω) followed by β-port code (retry: undo, advance differently, jump γ or ω; some kinds β = lbl_ω directly).

**Runtime state in TEXT arm:** `[r10]` = Δ (cursor, 32-bit int). `[rip + Σ]` = subject ptr. `[rip + Σlen]` = length. `nd->sval` = charset string baked into `.data`. `nd->counter` (int64) = runtime mutable state for generators.

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing rel32 patch offsets. `movabs` for absolute addresses. Refs: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104B, sites {17,72,86,90,100}), `bb_pat_notany.cpp`, `bb_pat_break.cpp` (178B), `bb_capture.cpp` (128B).

**Per-node persistent BINARY storage (SHARED PATTERN):** brokered blobs have no ELF `.data`. Two patterns:
1. `g_emit.bb_cs_zeta` `rt_cs_t {const char *chars; int delta;}` — `delta @+8` for SPAN/ARBNO counters; baked via `movabs rcx, &zeta`.
2. Process-lifetime `std::deque<int>` allocator (e.g. `cap_alloc_saved_delta_slot()`) — pointer never invalidates, GC-safe via C++ heap. Use for SPAN-2 / CAP / BREAKX scratch.

**DO NOT** use `GC_MALLOC` for per-node scratch baked as imm64 — bb_pool is mmap'd, GC can't see the address.

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
bash scripts/test_smoke_snobol4.sh                   # GATE-1: 13/13
bash scripts/test_smoke_unified_broker.sh            # GATE-2: ~30-36 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh      # GATE-3: 178/280
bash scripts/test_interp_broad_corpus_and_beauty.sh  # GATE-4: 251/280
bash scripts/test_snobol4_pat_rung_suite.sh          # M2=19 M4=15 SKIP=0
bash scripts/audit_m3_native_binary_arms.sh          # GATE OK
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh  # 195/280
```

For full failure list patch `head -40` to `head -300` in test_interp_broad_corpus_and_beauty.sh copy.

---

## Active rung: M3-NATIVE-4 — per-language bring-up + corpus parity (SNOBOL4)

### Open work

- [x] **POS/RPOS-NON-FIRST-IN-CAT ✅** (2026-05-29 Opus 4.7). Bisection led to a *different*
  bug: `bb_pat_pos.cpp:14` (and `bb_pat_tab.cpp:14`) used `int rpos = (pBB->ival != 0)`
  to distinguish RPOS from POS. Wrong — POS/RPOS (and TAB/RTAB) are distinguished by
  `pBB->sval == "r"` per lowering (`lower_pat_dcg.c` TT_RPOS/TT_RTAB/XRPSI/XRTB branches).
  The `ival != 0` heuristic misclassified RPOS(0) as POS(0) and POS(N>0) as RPOS(N>0).
  Fix: one-line each, `int rpos = (pBB->sval && pBB->sval[0] == 'r')`. Bug present in
  BOTH binary AND TEXT arms (same `rpos` variable), so both mode-3 native AND mode-4
  compile failed identically. **Native +25, mode-4 +6, mode-2 +1, rung M4 +2 (052, 054),
  zero regressions.** Handoff `HANDOFF-2026-05-29-OPUS-SBL-POS-RPOS-FLAG-FIX.md`.

- [ ] **Then knock down remaining ~57 native-only failures**, by cluster:
  - [x] **046/047 TAB/RTAB SIGSEGV native ✅** (2026-05-29 Opus 4.7). `bb_pat_tab.cpp` BINARY arm
    had two bug classes carried in from `c01959f4` (the bb_bin_t conversion). (1) Same off-by-one
    site convention as bb_pat_pos pre-`61ae501e`: TAB sites `{9, 23, 28, 29}` (last-byte-of-opcode
    convention) — patcher wrote rel32 starting at offset 9, overwriting the `0F 8F` jg opcode byte
    → SIGSEGV. Same off-by-one on RTAB. (2) RTAB BINARY arm had a SEMANTIC bug: the success-path
    "writeback" at offset 30 was `89 C1` (mov ecx, eax) — a no-op that overwrote ecx (which held
    Σlen-N) with eax (Δ), never writing the new Δ. TEXT arm shows the intent: `mov [r10], ecx`
    (3 bytes: `41 89 0A`). Three-bug fix: TAB sites `{10, 23, 27, 28}`; RTAB writeback corrected
    (+1 byte); RTAB sites `{26, 34, 38, 39}` accounting for the shift. **Native +3
    (046_pat_tab, 047_pat_rtab, W06_tab), zero regressions, all other gates unchanged.**
  - [x] **SPAN — ALREADY COMPLETE, "SBL-SPAN-2" was a phantom ✅** (2026-05-29 Opus 4.8, analysis).
    `bb_pat_span.cpp` MEDIUM_BINARY arm (committed `4ce8c385`, escape `44766d91`) already has the full
    deque z/z_orig slots + working β backtracking. Verified native: deep backtrack, two SPAN boxes,
    SPAN-in-ARBNO (re-entrant), SPAN capture, and "071 minus deref" (inline SPAN+POS+CAT+capture) — all
    PASS m2==m3. The "SPAN cluster" native fails (071/124/138/139/expr_eval) fail on a DIFFERENT feature
    (nested `*var` deref — see below), NOT on SPAN. Do not spend a session on SBL-SPAN-2.
  - [x] **REAL BLOCKER — nested XDSAR (`*var`) inside a combinator under sm_run_native — RESOLVED ✅** (2026-05-29 Opus 4.8).
    Three-part root cause: (1) `walk_bb_flat` (src/emitter/emit_bb.c) had **no `case BB_PAT_DEFER`** → fell to `default` (define β; jmp ω; jmp ω), never FILLing the template → DEFER degenerated to a zero-width no-op (false matches, e.g. `POS(0) *WORD RPOS(0)` on a non-matching subject said MATCH). (2) The BROKERED branch of `exec_stmt` routed defer trees through `patnd_to_bb_graph` (γ-pointer chain) but the flat driver traverses **kids**, not γ — so POS→DEFER collapsed to bare POS. (3) The `bb_pat_defer.cpp` MEDIUM_BINARY arm was empty, and once filled, a single `push r10` before `call rt_defer_match` left rsp mis-aligned → SIGSEGV when the deref resolved to a *pattern* (run via exec_stmt→bb_broker→SSE). Fix: add the `walk_bb_flat` DEFER→FILL case; make XDSAR a `patnd_is_simple_atom` (tree-eligible); route **defer-bearing combinator roots** through `patnd_to_bb_tree` (kid-tree) surgically (non-defer trees keep the legacy-cast path, so fence/capture trees are undisturbed); implement the BINARY arm with bulletproof 16-byte alignment (`push r10; push rbx; mov rbx,rsp; and rsp,-16; call; mov rsp,rbx; pop rbx; pop r10`). **Native 223→243 (+20), zero mode-2/3 regression** (m2 flat 252, smoke 13/13 ×2, rung M2=19, FACT=0, audit OK). Newly native: 056/070-073/108/110-112/115/128/132-138/144/147 + fence/arbno-over-defer (068/117/143/150 no longer SIGSEGV). NOTE: mode-4 not gated this session (deferred per Lon); the TEXT arm still uses the old `push r10; call; pop r10` and needs the same alignment fix when mode-4 work resumes.
    Ruled out (reverted): bb_pat_defer flat BINARY arm + lower_flat_invariant gate — both off this path.
  - SPAN ~10 tests (SBL-SPAN-2 BINARY arm + deque pattern)
  - ARBNO ~8 tests (SBL-ARBNO-3 — deque pattern available)
  - FENCE ~6 tests (bytes ready via EP-BINARY)
  - POS/RPOS/REM/ARB/TWO ~10 tests (individual arms)
  - capture-multiple/complex ~10 tests (derives from atomic fixes)

- [ ] **Flip default to native** (remove getenv gate at `scrip.c:449`), honest `[NO-SM-BB]` failure for unbuilt arms.

### Pending rungs (priority)

- **SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms.** Use `std::deque<int>` slot pattern from bb_capture.cpp (NOT GC_MALLOC). SPAN: TWO persistent int slots (z, z_orig); β yields successively shorter spans using ABSOLUTE z_orig. ARBNO: uses `nd->counter`, deque pattern + brokered child call. Validate via `--run`.
- **SBL-BREAKX-2.** Own BINARY arm. TEXT β rescans-to-next using z_orig + z. Two int slots via deque.
- **SBL-ATP** (`@var` cursor capture). (1) Add `BB_PAT_ATP` to `BB_op_t`. (2) `lower_pat_dcg.c`: `@var` → `nd->sval=varname; nd->α=nd; nd->β=fp; nd->γ=sp; nd->ω=fp`. (3) `bb_exec.c case BB_PAT_ATP` α writes Δ as int DESCR via NV_SET. (4) `bb_pat_atp.cpp` + emit_core dispatch.
- **SBL-SM-BINARY (HQ-track).** `sm_pat_nullary.cpp` BINARY arm embeds emitter-process `rt_pat_*` fn-ptr as imm64 — Invariant-8 violation. Fix: call `rt_pat_*@PLT` directly.
- **SBL-G-2.** Re-freeze GATE-PK in `test_per_kind_diff.sh`. Baseline references deleted `rt_bb_*` boxes — stale.
- **SBL-LOWER-CLEANUP.** Delete `lower_subj_pat_split` + `lower.c:1750` duplicate after Snocone confirmed unused.
- **SBL-VERIFY-1/2.** Corpus climb after all BINARY arms + SBL-ATP: target ≥260/280 broad corpus.
- **Pre-existing m2 oracle gaps** (audit-only). Rungs 044/045/046/048/052/054/055/056/057 fail m2 too: `bb_exec.c` doesn't implement what rung suite expects for POS/RPOS/TAB/REM/star_deref/fail_builtin. Separate session.

### M3-NATIVE-5 (final)

Gate sweep + corpus, all langs. Honest failure for unbuilt opcodes.

**Mode-4 sibling (separate goal):** SBL-M4-FLATWIRE — `--compile` standalone brokers at runtime instead of flat-wiring at emit time. Defer until after M3-NATIVE done.

---

## Completed (summary)

**Templates with x86 TEXT arms filled:** LIT, ARB, LEN, POS/RPOS, TAB/RTAB, REM, ALT, CAT, FENCE, ABORT, EPS, FAIL, ANY, NOTANY, BREAK (plain), SPAN, ARBNO, CAPTURE, DEFER.

**Templates with x86 BINARY arms filled and validated by `--run`:** LIT, LEN, POS, UPTO, ANY, NOTANY, BREAK (plain), CAPTURE. Combinator arms (ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED) emit real bytes via inline EP-walk (per-template, FACT-clean).

**Runtime translators:** `patnd_to_bb_graph()` (γ-chain, mode-2) + `patnd_to_bb_tree()` (tree-shape, mode-3 flat-wire). `patnd_needs_xlate` covers XARBN trees + simple-atom roots + capture-wrapped. `patnd_is_combinator_root` + `patnd_tree_eligible` route XCAT/XOR/XFNCE/XNME/XFNME/XARBN through tree builder.

**Infra:** `cap_alloc_saved_delta_slot()` deque-int pattern. `bomb_text`/`bomb_bytes`/`rt_bomb`. `audit_m3_native_binary_arms.sh`. `emit_label_alloc()` session-stable label arena. `_assign_varname_str` populates STRVAL_fn at construction time (NAMEPTR reverse-lookup via `NV_name_from_ptr`).

**Recovery resource:** original hand-written boxes at `git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`. Native-SM engine semantic spec at `git show 22a17fa3~1:src/processor/sm_jit_interp.c` (bytes through templates only).

---

## Session State

```
HEAD one4all       = (this commit)  SBL-TAB-RTAB-FIX
GATE-1 smoke       = 13/13    (also 13/13 under SCRIP_M3_NATIVE=1)
GATE-2 broker      = 39
GATE-3 mode-4      = (not gated this session — deferred per Lon; was 184/280)
GATE-4 mode-2      = 243/280  ⚠ down from 252 at baf8397d — a SIBLING Raku commit (one4all 30e7c0a1 "mode-2 gather + ACOMP coercion + junctions") regressed SNOBOL4 m2 252→223 via shared bb_exec.c/coerce; THIS goal's defer fix then recovered 223→243. The residual 243<252 gap is the sibling's, NOT this commit's — flag for cross-goal investigation.
NATIVE corpus      = 243/280  (+20 from nested-XDSAR/DEFER fix: walk_bb_flat dispatch + aligned BINARY arm + tree-route gate; measured against sibling base 30e7c0a1 which was 223 native)
Rung suite         = M2=19/19 SKIP=0
Prolog/Raku/Icon smokes = 5/5/5
FACT RULE          = 0
audit_m3_native    = GATE OK
GATE-PK            = stale
```

---

## Session log (last few, terse)

- **2026-05-29 Opus 4.8 — SBL-DEFER-NESTED ✅** (this commit). Nested `*var` (XDSAR→BB_PAT_DEFER) under a combinator failed under `sm_run_native`. Root cause was three gaps: missing `case BB_PAT_DEFER` in `walk_bb_flat` (→ no-op zero-width false matches); BROKERED branch used the γ-chain builder `patnd_to_bb_graph` where the flat driver needs the kid-tree `patnd_to_bb_tree`; empty + then mis-aligned BINARY arm in `bb_pat_defer.cpp` (single `push r10` → SIGSEGV when the deref ran a sub-pattern). Fixes: `walk_bb_flat` DEFER→FILL; XDSAR added to `patnd_is_simple_atom`; surgical `defer_combinator` gate routes only defer-bearing combinator roots through the tree builder (legacy-cast trees untouched); BINARY arm rewritten with `and rsp,-16` 16-byte alignment around `rt_defer_match`. Native 223→243 (+20) and m2 also 223→243 (+20) measured against the live sibling base one4all 30e7c0a1 (which a Raku commit had regressed from the 252 baseline); zero mode-2/3 regression introduced by THIS commit (empty FAIL-line regression diff). smoke 13/13 ×2, rung M2=19, FACT=0, audit GATE OK. Mode-4 deferred per Lon (not gated); `bb_pat_defer.cpp` TEXT arm still needs the same alignment fix for the mode-4 session.

- **2026-05-29 Opus 4.7 — SBL-TAB-RTAB-FIX ✅** (this commit). Three-bug fix in
  `bb_pat_tab.cpp` BINARY arm: (1) TAB sites `{9, 23, 28, 29}` → `{10, 23, 27, 28}` —
  same off-by-one as the POS-PATCH-OFFSET fix last session, `0F 8F` opcode byte was
  being overwritten by rel32 → SIGSEGV on TAB(N). (2) RTAB sites `{25, 32, 37, 38}` →
  `{26, 34, 38, 39}` same off-by-one + extra +1 shift on tail sites from fix (3).
  (3) RTAB SEMANTIC bug: success-path writeback at offset 30 was `89 C1` (mov ecx, eax)
  — a no-op clobbering ecx with eax. Should be `41 89 0A` (mov [r10], ecx) per TEXT arm.
  **Native +3 (046_pat_tab, 047_pat_rtab, W06_tab), zero regressions, all other gates
  unchanged.** Handoff `HANDOFF-2026-05-29-OPUS-SBL-TAB-RTAB-FIX.md`.

- **2026-05-29 Opus 4.7 — SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`). `bb_pat_pos.cpp:14`
  and `bb_pat_tab.cpp:14` used `int rpos = (pBB->ival != 0)` to distinguish RPOS/RTAB
  from POS/TAB. Wrong — distinguished by `pBB->sval == "r"` per lowering. Heuristic
  misclassified RPOS(0) as POS(0) (and POS(N>0) as RPOS(N>0)). One-line fix each:
  `int rpos = (pBB->sval && pBB->sval[0] == 'r')`. Bug in BOTH BINARY and TEXT arms —
  affected mode-3 native AND mode-4. **Native broad 195→220 (+25), GATE-3 mode-4 178→184
  (+6), GATE-4 mode-2 251→252 (+1), rung M4 15→17 (+2: 052, 054), zero regressions.**
  Newly-passing clusters: anchored captures with RPOS(0) terminator (052, 054, 061, 069,
  075, 100/101/103/105 FENCE, 116, 120-127 calc+JSON, 131, 142, 145/146, 152, W06_pos,
  W06_rpos, global_driver). Pruned GOAL file 363→204 lines this session. Handoff
  `HANDOFF-2026-05-29-OPUS-SBL-POS-RPOS-FLAG-FIX.md`.

- **2026-05-28 Opus 4.7 — SBL-BOMB-STUB-ESCAPE-FIX ✅** (`c6abd06c`). Cleaned 5 remaining `\\x` BOMB-stub sites (bb_arbno:23, bb_pl_alt:23, bb_pl_call:41, bb_pl_choice:42, bb_to:65). Latent landmine class closed: `grep -rE 'bytes\([0-9]+, ?"\\\\\\\\x' src/emitter/` now empty. Gates: G1=13/13, G2=39, G3=178/280, G4=251/280, native=195/280, M2=19/M4=15, FACT=0, audit GATE OK. Zero regressions.

- **2026-05-28 Opus 4.7 — SBL-SPAN-ARB-ESCAPE-FIX ✅** (`44766d91`). Mechanical `\\x`→`\x` in `bb_pat_span.cpp` and `bb_pat_arb.cpp` MEDIUM_BINARY (double-backslash bug). Native +8, default +4, mode-4 +3. Newly passing native: 041_pat_span, W05_span, 4 FENCE tests (SPAN inside), test_string, wordcount.

- **2026-05-28 Opus 4.7 — SBL-POS-PATCH-OFFSET ✅** (`61ae501e`). Two-line fix to `bb_pat_pos.cpp` sites: POS `{9,15,20,21}` → `{10,15,19,20}`, RPOS `{25,31,36,37}` → `{26,31,35,36}`. Patcher convention: `bin.sites[i]` is byte offset where rel32 BEGINS. Native +16, default +9. Newly passing: 044_pat_pos, 045_pat_rpos, 8 FENCE tests (POS inside), 143, 5 drivers.

- **2026-05-28 Opus 4.7 — SBL-M3-NATIVE-4 ARBNO MEDIUM_BINARY child-gate fix ✅** (`4471b80d`). 2-line surgical fix to `bb_arbno.cpp:19`: outer no-child gate medium-aware: `int have_child = MEDIUM_BINARY ? (g_emit.bb_child_fn != NULL) : (child_lbl && child_lbl[0]);`. Newly passing: W04_arbno_basic/backtrack/zero.

- **2026-05-28 Opus 4.7 — SBL-M3-NATIVE-4 ARBNO tree-shape foundation ✅** (`debb8a4e`). `bb_arbno_state_t` layout-extended at front with `kids/nkids`; `build_patnd_tree` gains `case XARBN:`; `patnd_tree_eligible`/`patnd_is_combinator_root` accept XARBN. Behavior-neutral baseline.

- **2026-05-28 Opus 4.7 — M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`). Three commits: (1) bb_seq audit fix → REAL (`1e9ae6c6`); (2) Combinator flat-wire (`a4b62c1f`) — new `patnd_to_bb_tree`+`build_patnd_tree`, `patnd_tree_eligible`+`patnd_is_combinator_root`; (3) Capture-wrap (`10f97d29`) — XNME/XFNME inner via tree path. Canonical wins: 050 ("dog"), 055 ("ab cd ef"). Native broad 142→157/280 (+15). No regression (label arena had cleared the dangling-stack-label hazard).

- **2026-05-28 Opus 4.7 — SBL-XNME-VARNAME ✅** (`48409299`). `_assign_varname_str(DESCR_t var)` extracts varname uniformly: NAMEVAL reads `.s`; NAMEPTR reverse-looks-up via `NV_name_from_ptr`. Called from `pat_assign_imm/cond` to populate STRVAL_fn at construction time. +8 mode-2 wins, zero regressions, mode-3 unchanged.

- **2026-05-28 Opus 4.7 — SBL-EP-BINARY restore ✅** (`df8e6126`). Five combinator templates (`bb_pat_alt`, `bb_pat_cat`, `bb_pl_seq`, `bb_pl_ite`, `bb_succeed`) had EP-walk byte production stripped by `88bacd2a`; restored to FACT-correct inline shape per template. Audit GATE OK.

- **2026-05-28 Opus 4.7 — label arena landed ✅** (`744ae342`). New `emit_label_alloc(fmt, ...)` in `emit_core.{h,c}` returns heap-backed `bb_label_t *` with stable address across emit session; pool reset by `bb_emit_begin()`. Migrated all six flat drivers in `emit_bb.c` off stack-local arrays. Behavior-neutral; prereq for combinator flat-wire retry.

- **2026-05-28 Sonnet 4.6 — MEDIUM_BINARY arms: all BOMs eliminated ✅** (`4ce8c385`). Filled BINARY arms for every BOMBed template: bb_binop_gen, bb_pl_alt/call/choice, bb_capture, bb_pat_arb (89B), bb_pat_span (220B), bb_arbno (259B with-child). Audit: GATE OK, zero BOMs.

- **2026-05-28 Opus 4.7 — SBL-EP-BINARY ✅** (`1bc53211` + FACT fix). Six combinator templates emit real bytes by walking `g_emit.xa_bb_ep_*[]` arrays. FACT-correct: byte-producing loop duplicated inline per template file (NO shared helper).

- **2026-05-28 Opus 4.7 — SBL-CAP-2 ✅** (`e9a9d7f3`). bb_capture.cpp BINARY arm: removed unconditional bomb; process-lifetime `std::deque<int>` allocator (NOT GC_MALLOC); push/pop r10 around child_fn; sites `{40, 49(def), 77, 124}`. Native +9 (039_pat_any, 040, 042, 043, 058, 059, W07_capt_*).

- **2026-05-28 Opus 4.7 — LANG-IGNORANT SM TEMPLATES** (`08e05f68`). Ripped 9 language-sniffing forks. Split `SM_BB_SWITCH` into `SM_BB_INVOKE` + `SM_BB_PL_INVOKE`.

- **2026-05-28 Sonnet 4.6 — M3-NATIVE-3 ✅** (`910d55c3`). BB call-out confirmed; ANY fires BINARY arm natively. SM_CALL_FN rdi fix. 12/13 native smokes.

- **2026-05-28 Sonnet 4.6 — M3-NATIVE-2b ✅** (`d16c6780`). JUMP/JUMP_S/JUMP_F + RETURN-family BINARY arms; two-pass rel32 reloc.

- **2026-05-28 Opus 4.7 — M3-NATIVE-2 first slice ✅.** Built `sm_run_native(SM_sequence_t*)` template-pure. Wired behind `SCRIP_M3_NATIVE` env.

- **2026-05-28 Opus 4.7 — M3-NATIVE-0 ✅.** Bomb infra template-pure. 8 stubs bombed. `audit_m3_native_binary_arms.sh` gates fake-jmps.

- **2026-05-28 Opus 4.7 — discovery + rescope.** Found `scrip.c` mode_run was calling `sm_run_with_recovery(sm, sm_interp_run)` — mode-3 was running mode-2 interpreter. Rescoped SBL-M3-FLATWIRE → SBL-M3-NATIVE.

(Older entries pruned; see git history of GOAL-SNOBOL4-BB.md.)

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
