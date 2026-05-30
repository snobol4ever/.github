# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md · GOAL-TEMPLATES-X86.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
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

### ⭐ MILESTONE (2026-05-29 Opus 4.8): NATIVE-ONLY GAP CLOSED

After SBL-1010 + SBL-1016, the broad-corpus partition has **ZERO native-only failures**:
every one of the 28 remaining native FAILs **also fails in `--interp` (mode-2)**. Native ==
mode-2 oracle == **252/280**. The "knock down remaining native-only failures" objective of this
rung is therefore effectively DONE — there are no more native-dispatch bugs in the broad corpus.
All further corpus climb now requires fixing the **mode-2 ORACLE** (which lifts BOTH modes
simultaneously, exactly as SBL-1016 demonstrated: fix once, both modes gain). Verified via
`comm -23 native_fails m2_fails` = empty. To re-confirm: run the broad corpus under
`SCRIP_M3_NATIVE=1` and under plain `--interp`, sort the two FAIL lists, diff them.

### Next phase: ORACLE-PARITY (lifts both modes)

- [x] **VARIABLE-ARGUMENT PATTERN FAMILY (mode-2 oracle) ✅** (2026-05-29 Opus 4.8, commits
  `acc9ae77`/`3278f60f`/`36fe8ab9`/`0c7f9cfb`). A whole class of mode-2-only failures shared ONE
  root cause: `lower_pat_dcg.c` accepted ONLY literal arguments to pattern primitives (`TT_QLIT`
  charset / `TT_ILIT` integer). A `TT_VAR` argument → `build_node` returns NULL → `BB_lower_pat`
  fails for the whole pattern → mode-2 falls to a legacy path that mismatches (matched nothing,
  or wrong fall-through). Native was always correct (it resolves args at runtime via `rt_pat_*`).
  Fix pattern (uniform): accept `TT_VAR`, store the **varname** in `sval`, set a flag, and resolve
  at exec time in `bb_exec.c` via `VARVAL_fn(NV_GET_fn(sval))` (charset) or `to_int(NV_GET_fn(sval))`
  (integer) — the arg variable is assigned by an earlier statement, AFTER pattern lowering, so
  resolution MUST be late. Flag convention: SPAN uses `ival=1` (ival otherwise unused); BREAK/BREAKX
  reserve `ival` for the BREAKX distinction so the family standardized on `dval` (1.0 = "sval is a
  varname"; for POS/RPOS/TAB/RTAB, `dval` also carries from-end: 2.0=POS/TAB-var, 1.0=RPOS/RTAB-var).
  Covered: **SPAN, ANY, NOTANY, BREAK, BREAKX, LEN, POS, RPOS, TAB, RTAB**. Also folded in here:
  **SBL-SIZE-SHADOW** (`acc9ae77`) — mode-2 `SIZE(12)` returned 0 (Icon `*E`) instead of 2 because
  the `sm_interp.c` `SM_CALL_FN` ladder ran `icn_try_call_builtin_by_name` BEFORE `INVOKE_fn`; added
  the `!sno_fn_registered(name)` guard mirroring the native `rt.c` SBL-DATA-FN-SHADOW fix (`SIZE` is
  in the SNOBOL4 func table). **mode-2 248→253 (+5: 811_size, 063_pat_fence_fn_optional,
  065_pat_fence_fn_decimal, 061_capture_in_arbno, test_string); native 255→256 (+1: XDump_driver,
  via the shared bb_exec SPAN-VAR arm). Zero regressions** across all four commits (FAIL-list diffs
  empty on the RED side each time). Gates each commit: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053
  pre-existing), broker 57/5, cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0. Pure C — no byte
  code. NOTE the audit GATE FAIL is **pre-existing** (Raku NFA `xa_wasm_main.cpp` NO-ARM, confirmed
  identical on clean `2b5a2e77` via `git stash`), NOT from this work.

- [~] **FENCE-commit / ALT-fall-through (124 + 114, SHARED class) — INLINE CLASS FIXED; DEFER-resume blocker remains.**
  `124_pat_regex_keyword_seal` (mode-2-only gap; native already green) and `114_pat_fence_via_var_in_paren_alt`
  (both modes). **Root cause found + INLINE class fixed (SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL, this
  session):** the mode-2 oracle's ALT fall-through did NOT restore the cursor Δ to the alternation's entry
  position. A Δ-advancing single-shot leaf (LIT/REM/ANY/BREAK/LEN/NOTANY/TAB/RTAB) was lowered with `β = fp`,
  so the CAT retry-chain (`successor.ω = preceding.β`) jumped straight past it WITHOUT re-entering it to undo
  its Δ advance — invisible without an ALT (whole match just fails + Δ resets in `bb_exec_pat`'s start-loop),
  but an ALT fallthrough leaks the cursor into the next alternative (`('ab' 'X' | 'abc')` on 'abc' → mode-2
  matched 'abc' from Δ=2 → fail). Fix: those leaves now set `β = bb` (self) in BOTH `build_node` (AST) and
  `build_patnd` (PATND) — matching the generator convention. FENCE additionally needed seal semantics: set
  `β = self` at both oracle lowering sites (native XFNCE tree-builder already self) and rewrote `bb_exec.c
  case BB_PAT_FENCE` to save Δ on α (`counter`) and RESTORE it on β (restore cursor, fail to ω WITHOUT
  retrying inner alternatives = the commit). **Verified:** inline probes now correct in mode-2 — `('ab'
  'X'|'abc')`, `(FENCE('if') 'X'|SPAN.I)`, `(FENCE('if'|'else') 'X'|SPAN.I)`, and the full
  `(FENCE('if'|'else'|'while'|'for').K | SPAN(lc).I)` keyword-seal pattern (= 124 INLINED) all pass mode-2.
  Gates: smoke 13/13 ×2, mode-2 broad 253 (ZERO regression, FAIL-list diff empty both sides), native broad
  256 (ZERO regression), pat rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang 5/5/5/5, FACT 0, audit
  pre-existing Raku NO-ARM only. **REMAINING blocker for the exact corpus tests 124/114:** they reach the
  alternation THROUGH a pattern VARIABLE (`token`, `*cmd` → `BB_PAT_DEFER`), whose sub-graph is run via a
  nested `bb_exec_once` then resumed via `bb_exec_resume`. `bb_exec_resume` re-runs from `bbg->entry`; for an
  alternation the entry is alt1's **capture node** (`BB_PAT_ASSIGN_COND`), and re-entering it takes the COMMIT
  path (re-commits the same match) instead of backtracking to alt2. Diagnosed precisely: the capture cannot
  distinguish "arrived from inner.γ (commit/regrow)" vs "arrived from successor.ω (backtrack)" — both have
  inner.state>0 — which is the same ambiguity the SBL-CAP-REGROW comment (`bb_exec.c` ~2916) documents.
  Attempted a `BB_graph_t.resume_at` (re-enter last-success node, SNO-gated) — works for self-backtracking
  leaves but NOT for commit-nodes; REVERTED (didn't fix target, adds risk to the Prolog/Icon-shared
  `bb_exec_resume`). **NEXT-SESSION FIX:** make the capture node backtrack-transparent — distinguish the
  backtrack edge from the commit/regrow edge (e.g. a per-graph `resume_at` last-success node PLUS a one-shot
  "backtrack" signal whose lifetime ends at the first forward γ step, so a committed capture re-entered on
  backtrack delegates to `inner.β` while inner.γ regrow still re-commits). This pairs with the already-present
  DEFER-grow (`bb_exec.c case BB_PAT_DEFER` state==1 → `bb_exec_resume`). p8 (`token=('if'.K|SPAN.I)`,
  no FENCE) is the minimal repro of JUST the DEFER-capture-resume gap (FENCE-independent).
  **2026-05-29 follow-up — capture-transparency PROTOTYPED then REVERTED (+1/−3, not pushable).** Implemented
  the planned fix: `BB_graph_t.resume_at` (last-success node, set in bb_exec_once/resume), a `g_resume_backtrack`
  one-shot (SET only when `bb_exec_resume` re-enters a SNO graph's resume_at, CLEARED on the first forward γ
  step in the resume driver loop), and made `BB_PAT_ASSIGN_COND`/`_IMM` delegate to `bb->α` (re-enter inner to
  backtrack) instead of committing when `g_resume_backtrack` is set. **Result: 124 went GREEN both modes, p8
  green, cross-lang 5/5/5/5 (Prolog safe — SNO-gating works), smoke 13/13 ×2, native unchanged 256 — BUT it
  REGRESSED 3 mode-2 tests: `068_pat_fence_fn_via_var`, `109_pat_fence_via_var_seal_blocks_retry`,
  `113_pat_fence_via_var_two_with_seal_retry` (mode-2 253→251).** The delegation over-reaches: for a FENCE-via-var
  whose seal must BLOCK retry, re-entering the capture's inner on backtrack lets the sealed FENCE be retried /
  produces the wrong extent. **NEXT FIX:** gate the capture's backtrack-delegation so it does NOT re-enter an
  inner that is (or wraps) a sealed FENCE — i.e. when the inner sub-pattern committed via a FENCE, the capture
  must fail upstream (current commit-then-fail behavior) rather than delegate. Distinguish "inner holds a live
  backtrackable generator" (delegate) from "inner is sealed/exhausted" (fail upstream). The +1/−3 patch is
  reproducible from this watermark; the leaf+FENCE base (committed `77a39e82`) is the clean floor.

- [x] **ANY/SPAN/etc. with a CONSTANT charset EXPRESSION argument (064_pat_fence_fn_capture) ✅** (SBL-CSET-FOLD,
  2026-05-29 Opus 4.8, commit `216d95dc`). `ANY(&UCASE &LCASE)`: arg is `TT_SEQ(TT_KEYWORD UCASE, TT_KEYWORD LCASE)`
  — a CONSTANT concat of immutable charset keywords. FIX: `build_node` (lower_pat_dcg.c) now constant-folds a charset
  arg that is a single immutable charset keyword (&UCASE/&LCASE/&DIGITS) or a TT_SEQ/TT_CAT of literals + those
  keywords into one literal charset string in `sval` (identical to literal `ANY('...')`), so `BB_lower_pat` succeeds
  and mode-2 uses the bb_exec oracle instead of the brokered PATND fallback. &ALPHABET excluded (runtime-filled).
  Non-constant pieces (TT_VAR / other keywords) still return NULL → PATND fallback preserved. Folded sval is a plain
  charset string → modes 2/3/4 read it correctly (no mode-4 byte hazard). **mode-2 253→254 (+1: 064); native 259
  unchanged; zero regression both modes.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053), cross-lang 5/5/5/5,
  broker 57/5, FACT 0, audit pre-existing Raku NO-ARM. **Qize_driver/XDump_driver NOT covered** — their charsets mix
  a literal/keyword with a VARIABLE (`BREAK('"' "'" QizeWierd)`) so not constant-foldable, plus ARBNO+capture (the
  brokered-wiring bug below). **case_driver/test_case = DIFFERENT root cause** (SBL-ALTCAT-XLATE, session log): the
  fold made their `icase` BUILD correctly, exposing the inline-function-returned-alternation bug.

- [ ] **TRIAGED — charset-EXPRESSION arg is ONE root cause covering `XDump_driver` + `Qize_driver` + `064`**
  (2026-05-29 Opus 4.8, full bisection + wired-graph dump; repro `/tmp/min4.sno` case P). Both drivers
  fail on the IDENTICAL diff: `Qize('hello')` renders `'' '' '' '' '' '' '' '' '' '' '' '' 'hello'`
  (12 spurious empty captures) vs ref `'hello'` — XDump test 2 "string dump" and Qize_driver test 2
  "Qize simple" are the same call. Source: `corpus/.../beauty_suite/Qize.sno`, the two quote-branch
  patterns `(BREAK('"' "'" QizeWierd) '"' ARBNO(NOTANY("'" QizeWierd))) . part RTAB(0) . str`.
  **Trigger (bisected, all three required):** (1) a pattern primitive `BREAK/ANY/NOTANY/SPAN` whose
  charset arg is a **concatenation expression** (`'"' "'"`, or literal+var `'"' "'" QizeWierd`) — NOT a
  single literal (correct) and NOT a single `TT_VAR` (correct, SBL-BREAK-VAR handles it); (2) an `ARBNO`
  in the surrounding group; (3) the full anchored capture shape. Minimal failing repro: case P =
  `str POS(0) (BREAK('"' "'") '"' ARBNO(NOTANY("'"))) . p RTAB(0) . r` on `str='cat'` → mode-2 MATCHES
  empty (WRONG); native + single-literal (case G) + var-arg (case Q) all correctly NO-MATCH.
  **Routing (why native/single-lit/var are fine, concat is not):** `lower.c:752-757` emits BOTH a runtime
  PATND (`lower_pat_expr`, native consumes — concat handled correctly) AND the mode-2 oracle BB graph
  (`BB_lower_pat`). `build_node` (`lower_pat_dcg.c:91-101` BREAK, and ANY/NOTANY/SPAN siblings) accepts
  ONLY `TT_QLIT`|`TT_VAR`; a `TT_SEQ` concat → returns NULL → `BB_lower_pat` fails → `bb_idx=-1`. For
  single-lit/var, `BB_lower_pat` SUCCEEDS so mode-2 uses the correct `build_node` oracle directly (verified:
  cases G/Q emit NO translator traces). For concat, `bb_idx=-1` → mode-2 falls to `stmt_exec.c exec_stmt`;
  the PATND contains `XARBN` so `patnd_needs_xlate` (`stmt_exec.c:237-311`) routes it through
  `patnd_to_bb_graph`→`build_patnd` (`lower_pat_dcg.c:368`), and `exec_stmt` then runs that graph via
  **`bb_build_brokered`→`bb_broker`** (`stmt_exec.c:382`), NOT `bb_exec_once`.
  **Charset is correctly resolved (RULED OUT):** `build_patnd` XBRKC (`lower_pat_dcg.c:384`) sets
  `bb->sval = pp->STRVAL_fn`; the wired-graph dump shows the BREAK node (`BB_PAT_BREAK`=kind 35) with
  `sval=["']` — the correct 2-char set. So the empty match is a **four-port WIRING / brokered-walk bug**
  for capture+ARBNO trees, corroborated by the `stmt_exec.c:237` gate comment ("legacy cast has been
  compensating for latent issues in fence-heavy and capture-heavy PATND trees"; routing more through the
  translator regressed 146/147/152/1011/1013/1017). Wired graph for case P (entry #6):
  `#6 POS γ→#2; #2 cap[part] α→#5 γ→#0 ω=NULL; #5 BREAK["'] γ→#4 ω=NULL; #4 lit["] γ→#3 ω→#5;
  #3 ARBNO γ→#2 ω→#4; #0 cap[rest] γ=NULL(accept) ω→#5; #1 RTAB γ→#0`. A static-trace under `bb_exec_once`
  *should* fail (BREAK→ω=NULL→FAIL), so the empty success arises in the **brokered box driver
  (`bb_broker`/`bb_build_brokered`)** walk of this capture+ARBNO+failing-leaf graph — that is the residual
  fix locus (mode-2-only; native uses templates, mode-4 emit unaffected since these nodes are not built
  for it today).
  **Fix routes (none implemented — fragile, needs full mode-2 corpus gate):**
  (A) GOAL-preferred/larger: make charset-expression args lower correctly — emit SM ops to compute the
  concatenated charset and feed the pattern node (like native). Touches `build_node` + **mode-4 emit**
  (`emit_bb.c:1482-1485` reads `nd->sval` for BB_PAT_SPAN/ANY/BREAK/NOTANY → must teach mode-4 the
  dynamic case, or only constant-fold the all-literal sub-case which lifts ~0 corpus tests since nearly
  all concats are literal+var: `SPAN(' ' tab)`×7, `SPAN(' ' nl)`×4, `SPAN('.' digits &UCASE '_' &LCASE)`×8,
  `BREAK(nl ';')`, the Qize family). (B) contained/mode-2-only: fix the brokered-driver / `build_patnd`
  four-port wiring for capture+ARBNO trees — charset already correct, bug is structural. **Do NOT overload
  `bb->sval` with a binary recipe** — `emit_bb.c:1482` consumes it as a plain C charset string and would
  emit corrupt mode-4 x86. **Lifts a sizable latent cluster + 2 driver tests** when fixed.
  **REFINEMENT (verified, same session): mode-2 `--interp` → `bb_driver=1` (`scrip.c:157`) →
  `g_bb_mode=BB_MODE_BROKERED` (`scrip.c:161`), so `exec_stmt` takes the BROKERED branch: an ARBNO pattern
  (`needs_xlate`, no defer) → `patnd_to_bb_graph` (γ-CHAIN builder) → `bb_build_brokered`. build_patnd's
  γ-chain + `bb_build_brokered` is the INTENDED pairing (`bb_broker` mode `bb_scan`, `bb_broker.c:14`),
  so this is a genuine brokered-box-WALK wiring bug for capture+ARBNO — NOT the flat-driver-drops-γ-nodes
  mismatch the `SBL-DEFER-NESTED` comment (`stmt_exec.c:396`) describes (that is a separate mode-3/flat
  case where `patnd_to_bb_tree` kid-arrays are the fix). Do NOT chase "switch to `patnd_to_bb_tree`" here:
  under BROKERED mode the γ-chain is correct by construction; the defect is downstream in the box-template
  brokered arms (`BB_templates/bb_capture.cpp`, `bb_assign.cpp`, `bb_arbno.cpp`, `bb_pat_break.cpp`) walking
  this specific capture+ARBNO+failing-leaf γ-graph. Box-template-level instrumentation is the next concrete step.**
  To regenerate the live mode-2-only list: broad corpus under `--interp` and `SCRIP_M3_NATIVE=1`, sort
  both FAIL lists, `comm -13 native m2` (stock harness runs bare `$INTERP` = mode-3 native per
  `scrip.c:135`; inject `--interp`). **Current mode-2-only gaps (4):** `064_pat_fence_fn_capture`,
  `124_pat_regex_keyword_seal` (the `[~]` DEFER-resume item), `Qize_driver`, `XDump_driver` — the latter
  three (064/Qize/XDump) all = this charset-expr root cause. **NEW native-only gap (1): `fence_driver`
  RESOLVED ✅ (SBL-POOL-TRIM, 2026-05-29 Opus 4.8)** — NOT a FENCE-SEAL regression; it was `bb_pool`
  exhaustion (fixed 256KB/blob × 16 = 4MB pool full → 17th pattern fails to build). The "ZERO native-only"
  milestone held; fence_driver just allocated >15 blobs via global.sno's preamble. See the SBL-POOL-TRIM
  handoff + session log entry below.


- [x] **SBL-ARB-CAT-BACKTRACK (mode-3 native + mode-4 flat) ✅** (2026-05-29 Opus 4.8). The prior
  session's "capture-registry / deferred-commit" hypothesis was **WRONG** — disproved by the no-capture
  repro `U='xxNAMExx'; U ? 'xx' ARB 'xx'` which ALSO fails (oracle: MATCH). The real defect is **ARB
  failing to backtrack/grow when it is a NON-LAST element of a 3+ element CAT**, and it lived in
  `flat_drive_cat` (`emit_bb.c`): the multi-kid loop wired **every** kid's ω-port to the shared
  `right_ω → left_β` (= kid[0].β), so when the trailing `'xx'` failed it jumped back to the FIRST
  element and SKIPPED the middle generator's β (its grow-retry). Correct four-port wiring: a CAT
  element that fails must retry the *immediately preceding* element (`kid[i].ω → kid[i-1].β`), so a
  middle generator (ARB/SPAN/ARBNO) gets to grow. Fix (2 lines): in the loop, `kid_ω = (i==1) ? left_β
  : betas[i-2]` and pass it as kid[i]'s ω instead of `right_ω`. 2-kid path already correct (its single
  fail path is kid[0].β); only 3+ was broken — which is why most corpus passed but the
  word/calc/eval cluster failed. **Native broad 252→255 (+3: 124_pat_regex_keyword_seal, word2, word3),
  zero regressions** (FAIL-list diff: exactly those 3 newly green, none dropped). word2 (`POS(0) LEN(4)
  . WHEN TAB(6) ARB . WHO " :" TAB(24) REM . WHAT`) now byte-identical to `.ref` AND SPITBOL oracle.
  Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-4 194 unchanged, broker 51/11,
  audit GATE OK, FACT seg_byte=0, cross-lang icon/prolog/raku/snocone 5/5/5/5. Pure C control-flow
  (label pointers) — zero byte-producing code added. Capture works through the fix for free (mode-3
  `W=[NAME]`), confirming this was never a capture bug.

- [ ] **ARB-as-pattern-VARIABLE backtracking in mode-2 oracle (`bb_exec_pat` / `BB_PAT_DEFER`)**
  — DIAGNOSED 2026-05-29 Opus 4.8, mode-2 FIX NOT YET DONE (mode-3/4 already fixed above). True
  `--interp` does NOT use `flat_drive_cat` — it runs a **pre-lowered `BB_graph_t`** (built by
  `BB_lower_pat` in `lower_pat_dcg.c`, sp=NULL/fp=NULL) through the `bb_exec.c` oracle
  (`bb_exec_pat → bb_exec_once → bb_exec_node`, following γ/ω/β pointers). Root cause of the mode-2
  failure: the bare keyword `ARB` lowers to a **`BB_PAT_DEFER`** node (sval="ARB", a *variable*
  reference — confirmed via pointer trace: enum offset +13, t=50=DEFER, t=36=the real embedded
  BB_PAT_ARB built at runtime). `BB_PAT_DEFER` in `bb_exec.c` (case at line ~2893) is **single-shot**:
  α runs the embedded sub-pattern once via `bb_exec_once(sub_bb)` (finds ARB's shortest = empty),
  β just `return bb->ω` (comment: "no retry — treated as a single-attempt sub-match like LIT"). So
  the embedded generator can never grow across the DEFER boundary. Compounding: the DEFER node's
  `β=NULL` in the lowering (the TT_VAR/TT_DEFER `build_node` case), so the TT_CAT fixup
  `b->ω = a->β ? a->β : fp` sets the successor's ω to NULL and the walk halts. **TWO-part fix needed:**
  (1) lowering: give the DEFER node `β = bb` (self) so the CAT fixup wires successor.ω → DEFER;
  (2) `bb_exec.c BB_PAT_DEFER`: on β (state>0), persist the embedded `sub_bb` graph pointer + the
  outer-Δ origin across α→β (e.g. via `bb->counter`/a side slot), restore the sub-Σ context, and call
  `bb_exec_resume(sub_bb)` (NOT `bb_exec_once`, which `bb_reset`s) to obtain the generator's NEXT
  (longer) match; on success update outer Δ and `return bb->γ`, else `return bb->ω`. This is the
  general, principled fix (any pattern-valued variable holding a backtracking generator), matching
  mode-3 where the PATND path resolves ARB to a real XARB/BB_PAT_ARB. Risk: oracle DEFER semantics +
  embedded-graph state — test against all gates. Expected to lift word1/139/140/141/expr_eval cluster
  in mode-2 to match mode-3. (Note: the corpus harness `test_interp_broad_corpus_and_beauty.sh` runs
  mode-3 NATIVE by default — `bare scrip` = mode_run=1; true mode-2 needs explicit `--interp`.)

### Open work

- [ ] **DEFERRED capture-commit (word1 + any OUTPUT/side-effecting/mid-pattern-ref capture)** —
  pre-existing, SHARED (mode-2 oracle AND native template), NOT yet fixed. SNOBOL4 `.`/`$` is
  DEFERRED: the assignment commits ONCE, on FULL-pattern-match success, with the final matched
  substring. Both engines commit IMMEDIATELY at each capture-node execution: mode-2 `bb_exec.c`
  `BB_PAT_ASSIGN_COND` (line ~2840) calls `NV_SET_fn` inline; native `rt_cap_assign_cursor`
  (`rt.c`) calls `NV_SET_fn` inline. For a backtracking child (ARB grows on each β), the capture
  re-fires at every step → OUTPUT prints `''`,`c`,`ca`,`cat` (word1 expects just `cat`). Invisible
  for ordinary vars (last write wins) but wrong for OUTPUT / any associated or mid-pattern-referenced
  var. FIX: route capture through the existing capture-registry (`rt_cap_*` rt.c:1842,
  `reset_capture_registry` stmt_exec.c) — RECORD `(varname, start, extent)` on capture-node success,
  and COMMIT all recorded captures only when the whole pattern matches (commit hook in `bb_exec_pat`
  / the native match epilogue), rewinding/overwriting the record on backtrack so the final
  (successful) extent wins. Touches both engines; verify against word1 + all gates. Prereq
  SBL-CAP-OUTPUT-R10 ✅ (the native commit no longer SEGVs).

- [x] **POS/RPOS-NON-FIRST-IN-CAT ✅** (2026-05-29 Opus 4.7). Bisection led to a *different*
  bug: `bb_pat_pos.cpp:14` (and `bb_pat_tab.cpp:14`) used `int rpos = (pBB->ival != 0)`
  to distinguish RPOS from POS. Wrong — POS/RPOS (and TAB/RTAB) are distinguished by
  `pBB->sval == "r"` per lowering (`lower_pat_dcg.c` TT_RPOS/TT_RTAB/XRPSI/XRTB branches).
  The `ival != 0` heuristic misclassified RPOS(0) as POS(0) and POS(N>0) as RPOS(N>0).
  Fix: one-line each, `int rpos = (pBB->sval && pBB->sval[0] == 'r')`. Bug present in
  BOTH binary AND TEXT arms (same `rpos` variable), so both mode-3 native AND mode-4
  compile failed identically. **Native +25, mode-4 +6, mode-2 +1, rung M4 +2 (052, 054),
  zero regressions.** Handoff `HANDOFF-2026-05-29-OPUS-SBL-POS-RPOS-FLAG-FIX.md`.

- [x] **1010 SEGV (OPSYN-alias recursion + alternate entry point) ✅** (2026-05-29 Opus 4.8).
  Both bisected sub-bugs share ONE root cause and ONE fix — `interp_hooks.c::_usercall_hook`
  early `FNCEX_fn` guard. It bounced to `APPLY_fn` whenever `sm_label_pc_lookup(&sm, name) < 0`,
  testing only the DIRECT name. An OPSYN alias (`facto`, SM body under entry `fact`) and an
  alt-entry fn (`fact2`, SM body under `fact2_entry`) have no SM label under their own name, so
  both bounced to `APPLY_fn`; `fn==NULL` (interpreted, not a C builtin) → `g_user_call_hook` →
  `_usercall_hook` → infinite recursion → stack-overflow SIGSEGV. Block-1 below ALREADY resolves
  both correctly via `FUNC_ENTRY_fn`, but the early guard never let execution reach it. Fix:
  before bouncing, also try uppercase-name and `FUNC_ENTRY_fn(name)` PCs (mirrors block-1); only
  bounce to `APPLY_fn` when no SM PC resolves by ANY means (genuine C builtins). +13 lines, one
  file. **Native 250→251 (+1: 1010_func_recursion 4/4, byte-exact vs oracle); zero regression**
  (FAIL-list diff: exactly 1010 newly green, nothing dropped). Gates: smoke 13/13 ×2, rung
  M2=19/0 M4=18/1 (053 pre-existing), mode-2 oracle 251 unchanged, broker 49/11 (identical
  before/after — sibling-influenced, not from this change), cross-lang icon/prolog/raku/snocone
  5/5/5/5, FACT 0, audit GATE OK. Not template work, as predicted.

- [x] **1016 EVAL SEGV (deferred-expression dispatch) ✅** (2026-05-29 Opus 4.8). `*expr`
  (unevaluated expression) lowers to `SM_PUSH_EXPRESSION entry_pc`, which builds a `DT_E`
  descriptor. Mode-2 (`sm_interp.c`) builds `{slen=1, i=entry_pc}` → `EXPVAL_fn` slen==1 path →
  `sm_eval_subexpr(entry_pc)` (runs the subexpr via the interpreter on the SM program). The
  mode-3 native MEDIUM_BINARY arm of `sm_push_expression_str` (`sm_expr_incr.cpp`) passed
  `mov esi, 2` (slen=2 = THUNK) with `movabs rdi, <entry_pc>` — but entry_pc (e.g. 5) is an SM PC,
  NOT a code address, so `EXPVAL_fn` slen==2 did `call *5` → SIGSEGV at PC 0x5. The MACRO/TEXT arms
  legitimately use slen=2 because mode-4 emits the subexpr as a real callable address
  (`lea rdi,[rip+.L<entry>]`); only the BINARY (mode-3-native, raw-SM-PC) arm was wrong. Fix:
  `u32le(2u)`→`u32le(1u)` in the BINARY arm only — descriptor now `{slen=1, i=entry_pc}` identical
  to mode-2 → `sm_eval_subexpr`. **Native 251→252 (+1: 1016_eval 3/3 byte-exact, all three EVAL
  forms — concat / var-ref / failing-expr); zero regression** (FAIL-diff = exactly 1016 newly
  green; mode-2 oracle 252 unchanged; smoke 13/13 ×2; rung M2=19/0 M4=18/1; cross-lang
  icon/prolog/raku/snocone 5/5/5/5; FACT 0; audit GATE OK). Not template-byte work beyond the
  one immediate-operand correction.

- [ ] **NOTE — 1011/1013/1017 are m2 oracle gaps, NOT native-only** (triaged 2026-05-29 Opus 4.8).
  All three FAIL in `--interp` (mode-2) too, so they are NOT native-dispatch bugs and do not
  belong to this M3-NATIVE cluster: **1011_func_redefine** (`FAIL 1011/003: redefined myfunc(4)=24`
  both modes — DEFINE-redefinition semantics), **1013_func_nreturn** (mode-2 even raises Error 5
  "Undefined function or operation" then `FAIL 1013/002` — NRETURN-as-lvalue assignment),
  **1017_arg_local** (`FAIL 1017/001: ARG(.jlab,1) = A` both modes — ARG/local introspection).
  Move to the "Pre-existing m2 oracle gaps (audit-only)" bucket below; fix the oracle first, then
  native parity follows for free as with 1016.

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
- **SBL-BREAKX-2 ✅ DONE** (2026-05-29 Opus 4.8). Own BINARY arm. TEXT β rescans-to-next using z_orig + z. z lives in [zeta+8]; z_orig recovered arithmetically (Δ - z) so no second slot needed. 302-byte α-scan + β-rescan, assembled+verified via `as`. Native +2 (W05_breakx, word4); zero regression.
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
HEAD one4all       = 5e1bad51  SBL-CSET-FOLD (constant-fold charset-expr args; mode-2 +1: 064)
HEAD corpus        = SBL-911-PORTABLE (staged, NOT pushed pending `perform hand off`)
GATE-1 smoke       = 13/13    (also 13/13 under SCRIP_M3_NATIVE=1)
GATE-2 broker      = 57/5     (sibling-influenced; engine untouched this session → unchanged by construction)
GATE-3 mode-4      = (not gated this session; rung M4=18/19, 053_pat_alt_commit pre-existing)
DEFAULT/NATIVE     = 260/280  (+1 this session: 911_datatype — corpus test fix, no engine change)
true --interp      = 255/280  (+1 this session: 911_datatype — corpus test fix, no engine change)
Rung suite         = M2=19/19 SKIP=0  (M4=18/19, 053 pre-existing)
Prolog/Raku/Icon/Snocone smokes = 5/5/5/5
FACT RULE          = 0
audit_m3_native    = GATE FAIL (PRE-EXISTING — Raku NFA xa_wasm_main.cpp NO-ARM; present on clean baseline via git stash)
GATE-PK            = stale
```

**Live mode-2-only gaps (5, after 064 closed):** `124_pat_regex_keyword_seal` (DEFER-resume `[~]`), `Qize_driver`,
`XDump_driver` (both charset-expr WITH a variable piece + ARBNO — NOT constant-foldable), `case_driver`,
`test_case`. The latter two now share ONE precisely-diagnosed root cause — see SBL-ALTCAT-XLATE in the
session log below: an inline FUNCTION-RETURNED ALTERNATION pattern (`'Hello' icase('hello')`) routes through
`exec_stmt`'s legacy `(BB_t*)pp` cast (BROKERED mode), which mis-executes a concatenation-of-alternations.

**WATERMARK CORRECTION (2026-05-29 Opus 4.8 audit, bisection-verified).** The prior claim that Raku commit `30e7c0a1` regressed SNOBOL4 m2 252→223 via shared bb_exec.c/coerce is **FALSE** — that commit's bb_exec.c change is `BB_LANG_RKU`-gated and its parent already scored 223. The real story: the default corpus harness (`bare scrip f.sno`) is **mode-3 native by default** (`scrip.c:135` mode_run=1), NOT mode-2; commit `0f4fcfde` ("Remove all mode fallback paths", Lon no-fallback directive) removed the mode_run→sm_interp_run fallback, **honestly exposing native-arm gaps** previously masked. There is no Raku-induced shared-path regression to chase. Full evidence: `HANDOFF-2026-05-29-OPUS48-SBL-NATIVE-GAP-AUDIT-AND-WATERMARK-CORRECTION.md`. Remaining native gaps (oracle-pass / native-fail): Cluster A native user-functions (**1010 recursion SEGV — BISECTED (Opus 4.8, 2026-05-29): plain recursion is FINE native (`fact(5)`→120, `fact(1)`→1 both pass); the SEGV is TWO distinct native-dispatch sub-bugs, each reproduced in isolation: (a) OPSYN-alias recursion — `OPSYN(.facto,'fact'); facto(4)` SIGSEGVs (register_fn_alias path under recursive native call); (b) alternate entry point — `DEFINE('fact2(n)', .fact2_entry)` + recursive call SIGSEGVs (DEFINE_fn_entry / entry-label≠name native dispatch). Next session: gdb each in isolation; likely the native call/return frame setup for aliased/alt-entry fns. Not template work.**), 1016 eval SEGV, 1013 NRETURN-lvalue, 1011 redefine, 1017 arg_local), Cluster B BREAKX (**CLOSED ✅ SBL-BREAKX-2**), Cluster C drivers (fence_driver; **match_driver CLOSED ✅ by SBL-DATA-FN-SHADOW**).**094 DATA accessor — FIXED ✅ (SBL-DATA-FN-SHADOW, Opus 4.8, 2026-05-29)**: root cause was NOT case-folding — the native `rt_call` (rt.c) consults the cross-language `icn_try_call_builtin_by_name` table (ungated, serving Raku/Icon `write`) BEFORE the SNOBOL4 `INVOKE_fn`. Icon has a `real()` builtin → a SNOBOL4 `real(X)` on a `DATA('complex(real,imag)')` object was intercepted by Icon's `real` (fails on DT_DATA) instead of reaching the DATA accessor; `imag` worked only because Icon has no `imag`. Fix: exported `sno_fn_registered(name)` (case-sensitive func-table presence check) and gated the icn fallback behind `if(!sno_fn_registered(name))` — a user-DEFINE'd or DATA-registered SNOBOL4 fn now shadows any cross-lang builtin and reaches its home dispatcher; unregistered names (Icon/Raku `write`, Icon `real` w/o a DATA def) unaffected. Native +3: 094 + 811_size (SIZE/`size` shadow, same class) + match_driver. Cross-lang smokes icon/prolog/raku/snocone/snobol4 5/5/5/5/13 unchanged.)

---

## Session log (last few, terse)

- **2026-05-30 Opus 4.8 — SBL-911-PORTABLE ✅ (corpus) + counter/semantic-driver triage** (corpus staged,
  NOT pushed pending `perform hand off`; one4all UNTOUCHED at `5e1bad51` — binary byte-identical to baseline,
  so all engine-side gates unchanged by construction). **(1) SBL-911-PORTABLE ✅:** `911_datatype` was the lone
  shared FAIL (both native AND mode-2) that turned out to be a **buggy corpus test, not an engine bug**. It
  wrapped DATATYPE results in `lcase(...)` to case-normalize, but (a) it's the ONLY test in the entire corpus
  using LCASE/UCASE as a *function*, (b) it used lowercase `lcase` which SCRIP correctly rejects (Error 5 /
  SPITBOL ERROR 022 — case-sensitive, RULES), and (c) even uppercase `LCASE(...)` fails the SPITBOL oracle
  because in standard SPITBOL `LCASE` is a predefined *variable* (the lc alphabet), there is no LCASE *function*.
  The `.ref` (PASS 4/4) was generated against scrip's extended builtins, NOT the oracle. Fix: rewrote the four
  assertions to the SPITBOL-portable idiom `REPLACE(DATATYPE(x), &UCASE, &LCASE)` — exactly what the sibling
  `semantic_driver.sno:9` already uses. Verified PASS 4/4 under **all three**: SPITBOL oracle, scrip native,
  scrip mode-2 (`.ref` unchanged). **Native 259→260 (+1), mode-2 254→255 (+1); FAIL-diff = exactly 911 newly
  green both modes, zero regression.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang
  icon/prolog/raku/snocone 5/5/5/5. (broker/FACT/audit unchanged — no engine code touched.) **(2) counter_driver
  + semantic_driver triage (NOT fixed — documented frontier):** both depend on the classic SNOBOL4 side-effect-
  during-match idiom in `semantic.sno`: `nPush = epsilon . *PushCounter()` (a CONDITIONAL ASSIGNMENT `.` whose
  value-TARGET is a DEFERRED EXPRESSION `*PushCounter()`; on match-commit the target expr is evaluated, firing
  the counter side effect and returning `.dummy` via NRETURN). Tests 1-3 only check the returned pattern's
  DATATYPE (PASS); tests 4-8 actually MATCH the pattern (`'' nPush()`) to trigger the side effect, then read
  `nTop()` — which comes back EMPTY (assertion 8: got `DATATYPE=STRING` on `""` vs expected `INTEGER`), i.e. the
  counter never updates because the deferred-expression assignment target is not evaluated at commit. This is
  the intersection of the documented **DEFERRED capture-commit** (Open work) and **deferred-expression eval**
  (`*expr` / SBL-1016 family) frontiers — the same entangled residue behind word1/139/140/141/expr_eval. Left
  for a dedicated engine session; flagged here so the cluster's shared root cause (`. *Func()` target-eval at
  capture-commit) is on record. **(3) Also confirmed:** the watermark's "5 mode-2-only gaps, 0 native-only" holds
  exactly on a clean clone+build (`comm -23 native m2` empty; the 5 mode-2-only = 124/Qize/XDump/case/test_case).

- **2026-05-29 Opus 4.8 — SBL-CSET-FOLD ✅ + SBL-ALTCAT-XLATE diagnosis** (one4all `216d95dc` committed locally,
  NOT pushed pending `perform hand off`; base `2d73a667`). Two findings closing/diagnosing the live mode-2-only
  gaps. **(1) SBL-CSET-FOLD ✅ (committed):** a constant charset-expression arg (single immutable keyword
  &UCASE/&LCASE/&DIGITS, or a TT_SEQ/TT_CAT of literals + those keywords) to ANY/SPAN/NOTANY/BREAK/BREAKX now
  constant-folds to one literal charset string in `build_node` (lower_pat_dcg.c), so `BB_lower_pat` succeeds and
  mode-2 uses the bb_exec oracle rather than the brokered PATND fallback (which mis-wires a charset-expr leaf inside
  a multi-element CAT → NO-MATCH). Bisected via an isolation matrix: bare `ANY(&UCASE &LCASE)` ALREADY worked in
  mode-2, but `POS(0) ANY(&UCASE &LCASE)` (and any CAT context, incl. a single `&UCASE`) failed — so the trigger is
  a non-QLIT/non-VAR charset arg making build_node return NULL, NOT charset resolution. Fold helpers (`cset_kw_value`
  /`cset_fold_len`/`cset_fold_fill`/`cset_try_fold`) are pure C, &ALPHABET excluded (runtime-filled), non-constant
  pieces still NULL → fallback preserved, folded sval is a plain charset string (no mode-4 hazard). **mode-2 253→254
  (+1: 064); native 259 unchanged; zero regression both modes** (FAIL-diffs empty RED side). Gates: smoke 13/13 ×2,
  rung M2=19/0 M4=18/1 (053 pre-existing), cross-lang icon/prolog/raku/snocone 5/5/5/5, broker 57/5, FACT 0, audit
  pre-existing Raku NO-ARM. **(2) SBL-ALTCAT-XLATE — DIAGNOSED, prototype REVERTED (NOT safe):** with the fold in
  place, `case_driver`/`test_case` exposed a DISTINCT root cause. Their `icase('s')` builds
  `('H'|'h')('E'|'e')...` correctly now, but using the function result INLINE as a match pattern (`'Hello'
  icase('hello')`) fails in mode-2 while storing-then-matching (`p=icase('hello'); 'Hello' p`) works. Bisected
  (isolation matrix + env-gated `exec_stmt` PATND-dump): ONLY an ALTERNATION (XOR / XCAT-of-XOR) returned from a
  function and used inline fails — lit/concat/span/len all fine. The dumped PATND is a PERFECT `XCAT(XOR,XOR)` yet
  NO-MATCHes. Cause: a bare `TT_FNC` pattern operand can't be lowered by `build_node` → `BB_lower_pat` fails →
  `bb_idx=-1` → `exec_stmt`; in BROKERED mode (mode-2) a non-defer combinator root is NOT `needs_xlate` and NOT
  `defer_combinator`, so it falls to the legacy `(BB_t*)pp` cast → `bb_build_brokered`, which mis-executes a
  concatenation-of-alternations. (The stored case works because a bare `TT_VAR` pattern lowers to a `BB_PAT_DEFER`
  node → `BB_lower_pat` succeeds → `bb_exec_pat` oracle resolves the var at runtime, never reaching `exec_stmt`;
  the static inline `'Hi' ('H'|'h')` works for the same `bb_exec_pat`/build_node reason.) Prototype tried: a
  `patnd_pure_altcat` predicate (XOR/XCAT over leaf atoms only — excludes XFNCE/XNME/XFNME/XARBN/XDSAR/capture, so
  the legacy-cast-compensated fence/capture trees that regressed 146/147/152/1011/1013/1017 stay untouched) routing
  those roots through `patnd_to_bb_graph` in the BROKERED branch. **Result: POSITIVE matches went green (test_case
  6/7, inline alt-concat ok) BUT the γ-chain translation OVER-MATCHES the NEGATIVE case** — `'world' icase('hello')`
  matched when it must not (test_case line 7 `FAIL: icase matched wrong string`). The isolated 2-element negative
  (`'xyz' ('H'|'h')('I'|'i')`) was correct, so the over-match needs the full 5-element + leading-empty (`icase`
  starts NULL) shape — suspect the leading eps/empty concat element in the γ-chain anchoring. REVERTED (stmt_exec.c
  restored to HEAD): shipping a fix that turns NO-MATCH into false MATCH would regress the broad corpus. **NEXT
  SESSION:** fix `patnd_to_bb_graph` (γ-chain) over-match for XCAT-of-XOR with a leading empty element (or strip the
  leading eps in the fold/translation), re-confirm `'world' icase('hello')` NO-MATCH, then re-apply the
  `patnd_pure_altcat` route and FULL-gate (must keep 146/147/152/1011/1013/1017 green). Closes case_driver +
  test_case (case_driver ALSO emits `sm_lower: undefined label 'error' → Error 24` — a separate lowering issue to
  check). `case_driver`/`test_case` minimal repro: `DEFINE('mp()'); mp mp = ('H'|'h')('I'|'i') :(RETURN)` then
  `'xyz' mp()` must NO-MATCH and `'Hi' mp()` must MATCH, both modes.

- **2026-05-29 Opus 4.8 — SBL-POOL-TRIM ✅** (staged, NOT pushed pending `perform hand off`; base `5cc1224e`).
  `fence_driver` native FAIL was misattributed to FENCE-SEAL — actual cause is **`bb_pool` exhaustion**.
  `bb_build_flat`/`bb_build_brokered` reserve a fixed `FLAT_BUF_MAX` (256 KB) per blob, seal only ~200 B used,
  never reclaim the slack; native caches+persists blobs (no per-stmt pool reset, only mode-4 resets), so 4 MB
  ÷ 256 KB = exactly **16 blobs** then `bb_alloc`→NULL → the 17th pattern (FENCE, after global.sno's >15-blob
  preamble) silently fails to build. Bisected: capture stmts fail at N=8, plain at N=20; `bb_alloc` probe
  showed size=262144 each, exhausting at used=4194304. Fix (3 files, +25/−7): new `bb_pool_trim_last(buf,
  reserved, used)` rewinds `pool_top` to `page_ceil(buf+used)` when `buf` is topmost (LIFO-guarded, no-op
  otherwise); reordered both builders so `pre_build_children` runs BEFORE `bb_alloc` (parent buf topmost at
  trim time) + `bb_pool_trim_last` after `bb_seal`; emission stays in-place (no memcpy → no rel32/movabs
  hazard). Corrected stale `bb_pool.h` comment (claimed 64 MB, defined 4 MB). **Native 256→259 (+3:
  case_driver, fence_driver, test_case — all pool-exhaustion victims); ZERO regression** (stash/rebuild
  baseline diff: exactly those 3 newly green, none dropped). Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1
  (053 pre-existing), broker 57/5, cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0, audit pre-existing
  NO-ARM only (no `xa_*` arm touched). Language-agnostic pool mechanics — likely lifts latent pool-exhaustion
  victims in Prolog/Icon/Raku BB too (their parsers build many sub-pattern blobs). Handoff:
  `HANDOFF-2026-05-29-OPUS48-SBL-POOL-TRIM-FENCE-DRIVER.md`.

- **2026-05-29 Opus 4.8 — SBL-CHARSET-EXPR TRIAGE (no code; consolidation)** (one4all UNCHANGED `77a39e82`;
  .github `195066df`+`84daf610`). Proved `XDump_driver` + `Qize_driver` + `064` share ONE root cause: a
  charset-EXPRESSION (concatenation) arg to `BREAK/ANY/NOTANY/SPAN`. `build_node` rejects `TT_SEQ` charset →
  `BB_lower_pat` fails → `bb_idx=-1` → mode-2 (`--interp` = `BB_MODE_BROKERED`, scrip.c:157/161) routes
  ARBNO patterns via `patnd_to_bb_graph` (γ-chain) → `bb_build_brokered`, whose box-template walk mis-wires
  capture+ARBNO into an empty match. Charset itself correctly resolved (`BB_PAT_BREAK sval=["']`) → structural
  bug. Minimal repro = case P. Ruled out: sval-recipe shortcut (emit_bb.c:1482 mode-4 hazard) and the
  `patnd_to_bb_tree` red herring (that is the separate mode-3 SBL-DEFER-NESTED case; under BROKERED the
  γ-chain is the intended pairing). Fix routes documented (A larger / B fragile mode-2). Also flagged NEW
  native-only gap `fence_driver` (post-FENCE-SEAL). Handoff:
  `HANDOFF-2026-05-29-OPUS48-SBL-CHARSET-EXPR-TRIAGE-CONSOLIDATION.md`.

- **2026-05-29 Opus 4.8 — VARIABLE-ARGUMENT PATTERN FAMILY + SIZE-SHADOW ✅** (one4all `0c7f9cfb`,
  chain `acc9ae77`→`3278f60f`→`36fe8ab9`→`0c7f9cfb`). Four commits closing one root-cause class of
  mode-2-only oracle gaps: DCG lowering (`lower_pat_dcg.c`) accepted ONLY literal args to pattern
  primitives, so a `TT_VAR` arg made `BB_lower_pat` fail → mode-2 fell to a mismatching legacy path
  (native always correct via runtime `rt_pat_*`). Uniform fix: accept `TT_VAR`, varname→`sval`,
  flag (`ival=1` for SPAN; `dval` for the rest since BREAK/BREAKX need `ival` for the BREAKX bit and
  POS/RPOS/TAB/RTAB need from-end), resolve late in `bb_exec.c` via `VARVAL_fn(NV_GET_fn)` /
  `to_int(NV_GET_fn)`. Covered SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB. Plus SBL-SIZE-SHADOW:
  mode-2 `SIZE(12)`→0 (Icon `*E`) fixed by the `!sno_fn_registered` guard on the `sm_interp.c` icn
  fallback (mirror of native `rt.c` SBL-DATA-FN-SHADOW; `SIZE` is in the SNOBOL4 func table).
  **mode-2 248→253 (+5: 811_size, 063, 065, 061, test_string); native 255→256 (+1: XDump_driver via
  shared SPAN-VAR arm). Zero regressions each commit** (empty RED FAIL-diffs). Gates per commit:
  smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), broker 57/5, cross-lang 5/5/5/5, FACT 0.
  Pure C, no byte code. Method: diff mode-2 vs native FAIL lists → isolate oracle gaps → bisect to the
  literal-only lowering. Audit GATE FAIL pre-existing (Raku NFA `xa_wasm_main.cpp`, verified on clean
  `2b5a2e77` via stash). Next: FENCE×ALT fall-through (124+114, shared), then charset-expr args (064).

- **2026-05-29 Opus 4.8 — SBL-M2-CAT-FLATTEN+DEFER-GROW+CAP-REGROW ✅** (one4all `2b5a2e77`). Mode-2 (`--interp`) oracle parity for ARB-in-CAT + capture. Prior DEFER hypothesis was WRONG (bare ARB compiles to SM_PAT_ARB/XFARB, and the failing path is the bb_exec.c ORACLE via SM_EXEC_STMT bb_table — BB_lower_pat succeeds — NOT the broker). Three real fixes: (1) lower_pat_dcg.c CAT-FLATTEN — parser emits left-nested binary CAT(CAT(a,b),c); the TT_CAT retry fixup wired successor.ω→a->β where a is the inner CAT entry (FIRST element β), never the buried middle generator, so 'xx' ARB 'xx' could not grow ARB. Flatten nested TT_SEQ/TT_CAT into one flat leaf chain (concat associative) → flat fixup wires kid[i+1].ω→kid[i].β. (2) bb_exec.c BB_PAT_DEFER growable — persist sub-graph ptr (dval) + outer-Δ origin (counter) in α, bb_exec_resume on β; β=self in the two DEFER lowering sites. (3) bb_exec.c ASSIGN_COND/IMM capture-regrow — node reset state=0 after commit so a regrown inner re-recorded a fresh start (captured var empty/wrong); discriminate fresh vs inner-return on inner state (bb->α->state), preserve start. **mode-2 246→248 (+2: word2, word3 byte-correct; FAIL-diff = exactly those two, zero regression).** native 255 unchanged; smoke 13/13 ×2; rung M2=19/0 M4=18/1 (053 pre-existing); cross-lang 5/5/5/5; FACT=0. Pure C control-flow/state, no byte code. NOTE: real mode-2 baseline is 246 (re-measured clean 28a720f2), the prior "252" was stale. audit GATE FAIL is pre-existing bb_nfa.cpp (Raku NFA sibling), present on clean baseline — not this change.

- **2026-05-29 Opus 4.8 — SBL-CAP-OUTPUT-R10 ✅** (one4all `28a720f2`). `bb_capture.cpp` BINARY arm
  called `rt_cap_assign_cursor` WITHOUT preserving `r10`. The brokered blob holds `&Δ` in `r10`
  (caller-saved, SysV); `NV_SET_fn` on the **OUTPUT** (or any associated) variable enters the print
  path (printf/fwrite) which clobbers `r10`; the post-assign consumer of `[r10]` (broker final-cursor
  read / following CAT element) then SIGSEGVs — the print itself succeeds (`cat` emitted) then the blob
  crashes. Minimal repro: `S='cat'; S ? 'cat' . OUTPUT` → prints `cat` then SEGV (native only; `--interp`
  fine). Fix: `push r10` TWICE around the call (preserve r10 AND keep rsp 16-aligned so the print's
  aligned SSE does not fault) + `pop r10` twice; γ site 124→132, blob 128→136 B; matches the child-fn
  calls' own r10 convention. **Native broad 255 unchanged** (word1's SEGV → clean fail), zero
  regressions: word2/word3 capture PASS, smoke 13/13 native, rung M2=19/0 M4=18/1 (053 pre-existing),
  broker 57/5, cross-lang 5/5/5/5, audit GATE OK, FACT 0. **word1's REMAINING failure is a separate
  pre-existing bug — DEFERRED-vs-immediate capture commit** (see Open work): native commits the `.`
  assignment at EVERY ARB backtracking step (`''`,`c`,`ca`,`cat`) instead of ONCE on full-match success,
  so capturing to OUTPUT prints every intermediate. Invisible for regular vars (last write wins) but
  observable for OUTPUT / any side-effecting or mid-pattern-referenced var.

- **2026-05-29 Opus 4.8 — SBL-ARB-CAT-BACKTRACK ✅** (one4all, flat driver). Corrected the prior
  session's WRONG "capture-registry" hypothesis: `'xx' ARB 'xx'` fails to match even with NO capture
  (oracle: MATCH), so it's an ARB-backtracking bug, not a capture bug. Root cause in
  `flat_drive_cat` (`emit_bb.c`) multi-kid loop: every kid's ω wired to the shared `right_ω → left_β`
  (= kid[0].β), so a failing trailing element jumped to the FIRST element and skipped a *middle*
  generator's β (grow-retry). Fix (2 lines): `kid_ω = (i==1) ? left_β : betas[i-2]`, so
  `kid[i].ω → kid[i-1].β` (retry the immediately-preceding element). 2-kid was already correct; only
  3+ element CATs with a non-last generator (ARB/SPAN/ARBNO) were broken — hence most corpus passed.
  **Mode-3 native broad 252→255 (+3: 124_pat_regex_keyword_seal, word2, word3); mode-4 194 unchanged;
  zero regressions** (FAIL-diff = exactly those 3, none dropped). word2 byte-identical to `.ref` +
  SPITBOL oracle. Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), broker 51/11, audit
  GATE OK, FACT 0, cross-lang 5/5/5/5. Pure C label-pointer control flow — no byte-producing code.
  Mode-2 (`--interp`) NOT fixed by this — it uses `bb_exec_pat` (lowered-graph oracle), where the bare
  `ARB` keyword lowers to a single-shot `BB_PAT_DEFER` that can't grow the embedded generator; the
  two-part mode-2 follow-up is documented in Open work above (DEFER β=self + `bb_exec_resume` on β).

- **2026-05-29 Opus 4.8 — SBL-1016-EVAL-SLEN ✅.** `*expr` (unevaluated/deferred expression, EVAL target) lowers to `SM_PUSH_EXPRESSION entry_pc` → builds a `DT_E` descriptor consumed by `EXPVAL_fn` (eval_code.c). slen==1 → `sm_eval_subexpr(entry_pc)` (SM-PC path); slen==2 → treat `i` as a callable code pointer and `call *i` (thunk path, used by mode-4 where the subexpr is emitted as a real `lea rdi,[rip+.L<entry>]` address). The mode-3 native MEDIUM_BINARY arm of `sm_push_expression_str` (`SM_templates/sm_expr_incr.cpp`) wrongly emitted `mov esi, 2` (slen=2) while `rdi`=`movabs <entry_pc>` (a raw SM PC, e.g. 5) → `EXPVAL_fn` did `call *5` → SIGSEGV at PC 0x5 (gdb: `EXPVAL_fn:431` → 0x5). Mode-2 `sm_interp.c` builds the descriptor with `slen=1`. Fix: BINARY arm `u32le(2u)`→`u32le(1u)` (one immediate operand) so the native descriptor is `{slen=1, i=entry_pc}` identical to mode-2 → routes to `sm_eval_subexpr` (strong def in sm_interp.c; EVAL is a runtime builtin, mode-agnostic). MACRO/TEXT arms untouched (mode-4 thunk path stays correct). **Native 251→252 (+1: 1016_eval 3/3 byte-exact — concat `*('abc' 'def')`, var-ref `*q`, failing `*IDENT(1,2)`); FAIL-diff = exactly 1016 newly green, zero regression.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-2 oracle 252 unchanged, broker 51/11 (sibling-up, not this change), cross-lang 5/5/5/5, FACT 0, audit GATE OK. Also triaged 1011/1013/1017 as m2 oracle gaps (fail both modes) — reclassified out of this native cluster.

- **2026-05-29 Opus 4.8 — SBL-1010-ALIAS-ALTENTRY-FIX ✅.** The two bisected 1010 sub-bugs (OPSYN-alias recursion `OPSYN(.facto,'fact');facto(4)` and alternate entry point `DEFINE('fact2(n)',.fact2_entry)`+recursion) turned out NOT to be call/return frame setup — they were a single name-resolution infinite loop in `src/driver/interp_hooks.c::_usercall_hook`. The early `if(!_body && FNCEX_fn(name))` guard bounced to `APPLY_fn` whenever `sm_label_pc_lookup(&g_stage2.sm, name) < 0` — i.e. whenever there was no SM label under the function's OWN name. An alias (`facto`: SM body lives under entry label `fact`) and an alt-entry fn (`fact2`: body under `fact2_entry`) both lack a direct same-name SM label, so both bounced; `APPLY_fn` found the FNCBLK but `fn==NULL` (interpreted, not a C builtin) → `g_user_call_hook` → `_usercall_hook` → ∞ → stack-overflow SIGSEGV (gdb showed pure `_usercall_hook`↔`APPLY_fn` alternation on `name="facto"`). Block-1 (the `if(1)` SM-PC resolver lower down) ALREADY handles both via `FUNC_ENTRY_fn` (`facto`→`fact`, `fact2`→`fact2_entry`), but the early guard never let control reach it. Fix: before bouncing, try uppercase-name then `FUNC_ENTRY_fn(name)` SM PCs (mirrors block-1's own ladder); only bounce to `APPLY_fn` when NO SM PC resolves by any means — i.e. genuine C builtins, the only case `APPLY_fn` can service without bouncing. +13 lines, one file, no template/byte work. **Native 250→251 (+1: 1010_func_recursion, 4/4 byte-exact); FAIL-list diff = exactly 1010 newly green, zero drops.** Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-2 251 unchanged, broker 49/11 (identical before/after — proved by stash/remeasure), cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0, audit GATE OK.

- **2026-05-29 Opus 4.8 — SBL-DATA-FN-SHADOW ✅** (uncommitted, same session as BREAKX-2). Native `rt_call` (rt.c) consulted the ungated cross-language `icn_try_call_builtin_by_name` table (which serves Raku/Icon `write` etc.) BEFORE SNOBOL4 `INVOKE_fn`. Icon has a `real()` builtin, so a SNOBOL4 `real(X)` on a `DATA('complex(real,imag)')` object was intercepted by Icon's `real` (fails on DT_DATA) instead of the DATA accessor; `imag` worked only because Icon lacks an `imag` builtin (proved by renaming fields `real,imag`→`rrr,iii` → native passes; `foo,bar` DATA passes; `imag(3.5)` no-DATA → Error 5 undefined; `real(3.5)` no-DATA → 3.5 via Icon). Fix: exported `sno_fn_registered(name)` (case-sensitive `_func_buckets` presence check, mirrors `fn_has_builtin` w/o the `fn!=NULL` filter so user-DEFINE bodies count too) and wrapped the icn fallback in `if(!sno_fn_registered(name))` — a registered SNOBOL4 fn (user DEFINE or DATA accessor) now shadows any cross-lang builtin and reaches `INVOKE_fn`; unregistered names unaffected. **Native 247→250 (+3: 094_data_define_access, 811_size [SIZE/`size`, same class], match_driver), all byte-exact; zero regression** (smoke 13/13 native, rung M2=19/0 M4=18/1, broker 44, cross-lang smokes icon/prolog/raku/snocone/snobol4 5/5/5/5/13, FACT 0, audit GATE OK). Mode-2 oracle already correct (it prefers the registered fn); this aligns native with the oracle.

- **2026-05-29 Opus 4.8 — SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL ✅** (uncommitted at writing; base
  `55a92d39`). Mode-2 oracle ALT fall-through did not restore Δ to the alternation entry: Δ-advancing
  single-shot leaves (LIT/REM/ANY/BREAK/LEN/NOTANY/TAB/RTAB) had `β = fp`, so the CAT retry-chain skipped
  re-entering them to undo their Δ advance. Fixed to `β = bb` (self) in BOTH `build_node` (13 sites) and
  `build_patnd` (8 sites). FENCE: `β = self` at both oracle lowering sites + `bb_exec.c case BB_PAT_FENCE`
  now saves Δ on α and restores on β (seal: restore cursor, fail without retrying inner). **Inline FENCE/ALT/
  capture class fully fixed** (verified via inlined-124 + 4 other probes, all green mode-2). **mode-2 253,
  native 256 — ZERO regression both modes (FAIL-list diffs empty), zero net corpus change** (the corpus
  FENCE/ALT tests 124/114 reach the alternation through DEFER vars, blocked on the separately-diagnosed
  DEFER-capture-resume gap — see the `[~]` item above). Gates: smoke 13/13 ×2, pat rung M2=19/0 M4=18/1
  (053 pre-existing), cross-lang icon/prolog/raku/snocone 5/5/5/5, FACT 0, audit pre-existing Raku
  `xa_wasm_main.cpp` NO-ARM only. Pure C control-flow + a 2-line Δ save/restore — no byte-producing code.
  A `resume_at` experiment (re-enter last-success node on resume, SNO-gated) was tried for the DEFER gap and
  REVERTED (handles self-backtrack leaves, not capture commit-nodes; risk to shared `bb_exec_resume`).

 (uncommitted, base 5d5cede1). `bb_pat_break.cpp` BREAKX (is_breakx, ival==1) MEDIUM_BINARY arm was a 2-jump stub with malformed sites `{1,2}` (the second `E9` opcode got eaten by the patcher → a rel32 landed at output offset 19 against a garbage/empty-named label → `bb_emit_end` "unresolved forward reference site=19 label=''" → SIGABRT on every native BREAKX). Replaced with a real 302-byte α-scan + β-rescan blob: α scans to the first cset char (Δ += z, jmp γ; end → ω); β recovers z_orig = Δ − z arithmetically (no second persistent slot), steps past (z++), rescans to the NEXT cset char (jmp γ on found, jmp ω on exhausted). z persists in `[zeta+8]`. Assembled+verified via `as`/objdump, transcribed mechanically to `bytes()`/`u64le()`/`u32le()` (FACT-pure). Sites γ(139)/ω(144)/β-DEF(148)/γ(293)/ω(298). **Native 245→247 (+2: W05_breakx, word4); zero regression** (smoke 13/13 ×2, rung M2=19/0 M4=18/1 [053 pre-existing], cross-lang 5/5/5/5, GATE-2 broker 44, FACT 0, audit GATE OK). word4 (BREAKX mid-pattern w/ REM+SPAN backtracking into β) byte-exact vs ref. Oracle + mode-4 TEXT arm untouched.

- **2026-05-29 Opus 4.8 — SBL-NATIVE-FN-1 NRETURN read-deref ✅ + watermark correction** (one4all 5d5cede1). `rt_call` (rt.c:1339, the native SM_CALL_FN runtime helper) deref'd NRETURN results ONLY in the `if(cfn)` chunk branch; the bottom `INVOKE_fn` fallthrough — which native user-function dispatch actually takes — pushed the returned NAME with no deref, so `OUTPUT = ref_b()` (ref_b returns `.A` via :(NRETURN)) printed the name `A` instead of the value `77`. The mode-2 sm_interp consumer derefs correctly; native didn't. Fix: 4 lines mirroring the `cfn` branch, guarded by `kw_rtntype=="NRETURN"` + `IS_NAMEPTR/IS_NAMEVAL` (no-op for every non-NRETURN call → zero risk to other paths). **Native 243→245 (+2: 213_indirect_name, assign_driver); true --interp 246 unchanged (native-only fix); smoke 13/13 ×2; FACT 0; audit GATE OK; rung M2=19/0.** 1013_func_nreturn now reaches assertion 2 (NRETURN-as-lvalue, a separate sub-feature — next). **Also corrected a false watermark** (see Session State + HANDOFF-...-NATIVE-GAP-AUDIT): the "Raku 30e7c0a1 regressed m2 252→223" claim is wrong; the 252→243 drop is `0f4fcfde`'s deliberate no-fallback exposure of native gaps. Handoffs: `HANDOFF-2026-05-29-OPUS48-SBL-NATIVE-GAP-AUDIT-AND-WATERMARK-CORRECTION.md`.

- **2026-05-29 Opus 4.8 — SBL-DEFER-NESTED ✅** (prior commit). Nested `*var` (XDSAR→BB_PAT_DEFER) under a combinator failed under `sm_run_native`. Root cause was three gaps: missing `case BB_PAT_DEFER` in `walk_bb_flat` (→ no-op zero-width false matches); BROKERED branch used the γ-chain builder `patnd_to_bb_graph` where the flat driver needs the kid-tree `patnd_to_bb_tree`; empty + then mis-aligned BINARY arm in `bb_pat_defer.cpp` (single `push r10` → SIGSEGV when the deref ran a sub-pattern). Fixes: `walk_bb_flat` DEFER→FILL; XDSAR added to `patnd_is_simple_atom`; surgical `defer_combinator` gate routes only defer-bearing combinator roots through the tree builder (legacy-cast trees untouched); BINARY arm rewritten with `and rsp,-16` 16-byte alignment around `rt_defer_match`. Native 223→243 (+20) and m2 also 223→243 (+20) measured against the live sibling base one4all 30e7c0a1 (which a Raku commit had regressed from the 252 baseline); zero mode-2/3 regression introduced by THIS commit (empty FAIL-line regression diff). smoke 13/13 ×2, rung M2=19, FACT=0, audit GATE OK. Mode-4 deferred per Lon (not gated); `bb_pat_defer.cpp` TEXT arm still needs the same alignment fix for the mode-4 session. Handoff `HANDOFF-2026-05-29-OPUS48-SBL-DEFER-NESTED-LANDED.md`.

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
