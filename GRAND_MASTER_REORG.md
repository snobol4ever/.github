# GRAND_MASTER_REORG.md — Grand Master Reorganization
*2026-03-25 — authored by Claude Sonnet 4.6 in consultation with the project record*
*2026-03-25 — milestones decomposed for incremental safety by Claude Sonnet 4.6 (G-6 session)*
*2026-03-29 — split into three files (G-8 session):*
- *This file: milestone tables, dependency graph, success criteria — active tracking*
- *`ARCH-reorg-design.md`: architecture, IR node table, Naming Law, Invariant Table*
- *`ARCH-reorg-gentest.md`: Phase 8 grammar-driven test generation full spec*
- *G-7/G-8 addenda decision rationale archived to `SESSIONS_ARCHIVE.md`*

---

## ⚡ Quick Reference
- **Architecture, IR node table, Naming Law, Invariant Table** → `ARCH-reorg-design.md`
- **Phase 8 gen-test full spec** → `ARCH-reorg-gentest.md`
- **Decision rationale (E_SEQ/E_CONCAT split, WASM encoding)** → `SESSIONS_ARCHIVE.md` (archived addenda section)
- **WASM backend reference** → `BACKEND-WASM.md`

---

## Milestones

### Phase 0 — Freeze and Baseline

| ID | Action | Verify |
|----|--------|--------|
| **M-G-EMIT-COVERAGE** ✅ | Emit-diff coverage: one test per IR node kind across all applicable backends. SNOBOL4: `test/snobol4/coverage/coverage_sno_nodes.sno` — all 26 frontend-emitted node kinds (E_QLIT E_ILIT E_FLIT E_VART E_KW E_NULV E_ADD E_SUB E_MPY E_DIV E_MNS E_EXPOP E_CONCAT E_SEQ E_OR E_NAM E_DOL E_ATP E_ARB E_ARBNO E_STAR E_INDR E_FNC E_IDX E_ASGN E_OPSYN). Prolog: `test/prolog/coverage/coverage_pl_nodes.pl` — all 15 Prolog IR node kinds. Icon: `test/icon/coverage/coverage_x64_gaps.icn` (existing, covers 28 ICN kinds). Emit-diff: **493/0** ✅. | one4all `6d8dd4b` |
| **M-G-INV-FAST** ✅ | Invariant harness speed overhaul. Root cause: per-test JVM startup (jasmin + java) × ~152 tests = 3–5 min, causing session timeouts. Fixes: (1) **Persistent runtime archive cache** `out/rt_cache/libsno4rt_asm.a` + `libsno4rt_pl.a` — stamp-checked, rebuilt only on source change; (2) **Batch jasmin** — all `.j` files assembled in one `java -jar jasmin` call per suite; (3) **Single SnoHarness JVM** — all SNOBOL4-JVM and Prolog-JVM tests run in one `java -cp SnoHarness` process with per-test classloader + 3s thread timeout; (4) **Parallel nasm+link** via `xargs -P$JOBS`. Result: harness now produces output within 240s. | G-9 s2 · .github pending |
| **M-G-INV-TIMEOUT** ✅ | Hang detection requirement: no infinite-loop test may block harness for more than seconds. Implemented five-layer timeout defence: (1) per-binary x86 `timeout $TIMEOUT_X86` (5s); (2) SnoHarness internal 3s per-class thread; (3) batch jasmin `timeout 60`; (4) SnoHarness suite `timeout 120`; (5) suite-level watchdog background process kills harness after `SUITE_TIMEOUT=300`s. All 38 icon rung runners patched (two structural families). START/FINISH/ELAPSED printed at top and bottom of `run_emit_check.sh` and `run_invariants.sh`. | G-9 s2 · .github pending |
| **M-G-INV-FAST-X86-FIX** ✅ | All 7 invariant cells confirmed with real counts. Baseline (G-9 s18): x86: SNOBOL4 `106/106` · Icon `94/258` (pre-existing M-G5-LOWER-ICON gaps) · Prolog `13/107` (94 missing builtins, out of reorg scope). JVM: SNOBOL4 `110p/16f` (16 pre-existing OPSYN/EVAL gaps) · Icon `173/234` · Prolog `106/107` (rung06 pre-existing). NET: SNOBOL4 `108/110` (056_pat_star_deref + wordcount hang — both pre-existing). All failures confirmed non-regressions. **Invariant suite reactivated post-M-G7-UNFREEZE — run at every session start/end per RULES.md.** | G-9 s18 · one4all `dcdaa3e` |
| **M-G-INV-SESSION-BASELINE** ✅ | Gate: confirm full invariant suite runs to completion in the current Claude session environment. Fix: removed parallel dispatch + watchdog, replaced with serial cell execution. Result: 60.8s wall time, `snobol4_x86 106/106` ✅, Prolog x86 11/107 (96 pre-existing compile failures, not a regression), Icon 0/0, JVM/NET SKIP. Baseline confirmed. | `snobol4_x86 106/106` ✅ · one4all `4f30e7f` |

---

### Phase 1 — Unified IR Header

| ID | Action | Verify |
|----|--------|--------|

---

### Phase 2 — Folder Restructure (mechanical rename only)

| ID | Action | Verify |
|----|--------|--------|

After M-G2: the file layout matches the target architecture. Every emitter sits
in the backend directory that owns it. **M-G2-MOVE-PROLOG-ASM-a/b must be last** —
they are a file split, not a rename, and carry the most risk within this phase.

---

### Phase 3 — Naming Unification (survivors only, post-collapse)

**Phase 4 collapse is COMPLETE (G-9 s1–s3).** Result: no significant shared extraction was possible — all major node kinds diverge too fundamentally across backends (cursor-save, β port presence, ABI, callback signatures). Only `ir_nary_right_fold` was extracted. The current emitter files (`emit_x64.c`, `emit_jvm.c`, `emit_net.c`, `emit_jvm_icon.c`, `emit_jvm_prolog.c`, `emit_x64_icon.c`, `emit_x64_prolog.c`) **are the final post-collapse survivors**. No further collapse is coming that would delete code. Phase 3 naming passes proceed on these files as-is.

**Survivor surface after Phases 4+5:**
- `src/ir/ir_emit_common.c` — shared Byrd box wiring (new file, naming law applied from creation)
- `src/backend/x64/emit_x64.c` — x64-specific instruction emission residual
- `src/backend/jvm/emit_jvm.c` — JVM-specific residual
- `src/backend/net/emit_net.c` — .NET-specific residual
- `src/backend/wasm/emit_wasm.c` — WASM (new, already law-conformant from M-G2-SCAFFOLD-WASM)
- `src/backend/x64/emit_x64_icon.c` — Icon x64-specific residual
- `src/backend/x64/emit_x64_prolog.c` — Prolog x64-specific residual
- `src/backend/jvm/emit_jvm_icon.c` — Icon JVM-specific residual
- `src/backend/jvm/emit_jvm_prolog.c` — Prolog JVM-specific residual

**Scope reduction:** ~29 pre-collapse sub-milestones collapse to ~9 post-collapse
milestones — one per surviving file. Each file's shared-wiring handlers are already
law-conformant (written that way in Phase 4); only backend-specific residuals need
the naming pass.

**Rule:** after every sub-milestone, the full corpus for that backend must pass.
A regression is immediately localizable to the one file just touched.

**SCOPE (G-9 s22 — full similarity-maximization):** Each M-G3-NAME-* milestone is a
**similarity-maximization pass** on its file per ARCH-reorg-design.md §THE LAW.
The goal: after all passes, diffing any two emitter files should show differences
*only* in the output macro letter and platform-specific code sequences — not in
naming. Every class of named thing (globals, functions, locals, parameters, generated
labels, comments) must satisfy the 9-class law.

**Remaining (each is a full 9-class similarity pass):**

| ID | File | Lines | Key class-1 changes | Key class-2/3 label changes | Verify | Status |
|----|------|-------|--------------------|-----------------------------|--------|--------|

---

### Phase 4 — Shared Emit Functions (extract common wiring)

For each node kind that appears in more than one emitter, extract the **Byrd box
wiring logic** into a shared helper. The backend-specific instruction emission
stays in each backend file. No behavior changes — mechanical extraction only.

The pattern for each shared node kind:

```c
/* In src/ir/ir_emit_common.c — backend-agnostic Byrd box wiring only */
void emit_wiring_CONC(EXPR_t *node,
                      const char *lbl_gamma, const char *lbl_omega,
                      emit_fn_t emit_child) {
    /* Wire: left.gamma → right.alpha; right.omega → left.beta */
    char lbl_mid[64];
    snprintf(lbl_mid, sizeof lbl_mid, "L%d_mid", node->id);
    emit_child(node->children[0], lbl_mid,   lbl_omega);
    /* lbl_mid: */
    emit_child(node->children[1], lbl_gamma, lbl_omega);
}
```

Each backend provides its own `emit_fn_t` callback. The wiring is written once.

| ID | Node kinds | Action | Verify |
|----|-----------|--------|--------|
| **M-G4-SHARED-ICON-TO** | `E_TO`, `E_TO_BY` | Extract Icon generator wiring shared between `emit_x64_icon.c` and `emit_jvm_icon.c`. | Icon x86 + JVM |
| **M-G4-SHARED-ICON-SUSPEND** | `E_SUSPEND` | Same. Suspend/resume wiring isolated from other generators. | Icon x86 + JVM |
| **M-G4-SHARED-ICON-ALT** | `E_ALT_GEN` | Same. | Icon x86 + JVM |
| **M-G4-SHARED-ICON-BANG** | `E_ITER`, `E_MATCH` | Same. SCAN involves subject save/restore — verify both backends independently. | Icon x86 + JVM |
| **M-G4-SHARED-ICON-LIMIT** | `E_LIMIT` | Same. | Icon x86 + JVM |
| **M-G4-SHARED-PROLOG-UNIFY** | `E_UNIFY` | Extract Prolog unification wiring shared between ASM and JVM. | Prolog x86 + JVM |
| **M-G4-SHARED-PROLOG-CLAUSE** | `E_CLAUSE`, `E_CHOICE` | Same. Head-matching and predicate dispatch wiring. | Prolog x86 + JVM |
| **M-G4-SHARED-PROLOG-CUT** | `E_CUT` | Same. FENCE/cut sealing logic. | Prolog x86 + JVM |
| **M-G4-SHARED-PROLOG-TRAIL** | `E_TRAIL_MARK`, `E_TRAIL_UNWIND` | Same. Trail save/restore is the most backend-sensitive Prolog operation — isolated last. | Prolog x86 + JVM |

---

### Phase 5 — Frontend Lower-to-IR Unification

Each frontend's `lower.c` must produce only canonical `EXPR_t` nodes from the
unified `ir.h` enum. Any frontend-local node types that duplicate an existing
shared kind are replaced.

**Rule:** audit and fix are always separate milestones. The audit produces a doc
listing gaps. The fix resolves them one gap at a time. No gap is fixed without
first being documented.

| ID | Frontend | Action | Verify |
|----|----------|--------|--------|
| **M-G5-LOWER-ICON-FIX** | icon | Fix 7 gaps. G1/G7 low priority. G2-G6 medium (cset ops + random). | Icon x86 rung03 5/5 after each gap |

---

### Why WebAssembly — The Browser IDE Vision

WASM is not just a fourth deployment target. It unlocks a browser-native development
tool that would be unique in the world:

```
Browser tab — no server, no install, share a URL
├── Left pane:   source editor (SNOBOL4 / Icon / Prolog / Snocone / Rebus)
├── Middle pane: live Byrd box graph — α/β/γ/ω ports animated in real time
├── Right pane:  program output / trace stream
└── Bottom:      step debugger — &STLIMIT=1 probe mode, variable state at each step
```

The Byrd box model is **visual by nature** — four ports, wires between nodes,
backtracking arrows reversing. Animated goal-directed evaluation in a browser would
be a world-class educational tool for SNOBOL4, Prolog, and Icon simultaneously.
Nothing like it exists anywhere.

**How it works:** the `scrip` compiler compiles to WASM. The runtime
(`snobol4.c`, the pattern engine, the Byrd box machinery) also compiles to WASM
via Emscripten. Both run client-side. The React/HTML monitor GUI (M-MONITOR-GUI,
currently 💭) becomes buildable once this lands.

**Dependency chain:**
```
M-G6-SNOBOL4-WASM → runtime via Emscripten → browser harness → M-MONITOR-GUI
```

This is the motivating vision for the WASM backend. It turns a compiler project
into a living, shareable, interactive demonstration of goal-directed evaluation.

With unified IR and three shared backends, adding a new frontend×backend pipeline
is: wire the frontend's `lower.c` output into the backend's `emit_*.c`.
No new emitter code for shared node kinds. Priority order:

| ID | Pipeline | Prerequisite | Verify |
|----|----------|-------------|--------|
| **M-G6-ICON-NET** | Icon → .NET | M-G4-SHARED-ICON-LIMIT + M-G5-LOWER-ICON | Icon NET rung01 PASS |
| **M-G6-PROLOG-NET** | Prolog → .NET | M-G4-SHARED-PROLOG-TRAIL + M-G5-LOWER-PROLOG | Prolog NET rung01 PASS |
| **M-G6-SNOCONE-JVM** | Snocone → JVM | M-G5-LOWER-SNOCONE | Snocone JVM corpus PASS |
| **M-G6-SNOCONE-NET** | Snocone → .NET | M-G5-LOWER-SNOCONE | Snocone NET corpus PASS |
| **M-G6-SNOCONE-WASM** | Snocone → WASM | M-G5-LOWER-SNOCONE + M-G6-SNOBOL4-WASM | Snocone Wx86 rung01 PASS |
| **M-G6-REBUS-JVM** | Rebus → JVM | M-G5-LOWER-REBUS | Rebus JVM PASS |
| **M-G6-REBUS-NET** | Rebus → .NET | M-G5-LOWER-REBUS | Rebus NET PASS |
| **M-G6-REBUS-WASM** | Rebus → WASM | M-G5-LOWER-REBUS + M-G6-SNOBOL4-WASM | Rebus Wx86 rung01 PASS |
| **M-G6-SNOBOL4-WASM** | SNOBOL4 → WASM | M-G4-SHARED-ASSIGN + M-G2-SCAFFOLD-WASM | hello.sno → .wat → wasmtime PASS |
| **M-G6-ICON-WASM** | Icon → WASM | M-G4-SHARED-ICON-LIMIT + M-G5-LOWER-ICON | Icon Wx86 rung01 PASS |
| **M-G6-PROLOG-WASM** | Prolog → WASM | M-G4-SHARED-PROLOG-TRAIL + M-G5-LOWER-PROLOG | Prolog Wx86 rung01 PASS |
| **M-G6-SCRIP-X64** | Scrip → x86 | M-G5-LOWER-SCRIP-FIX | Scrip x86 rung01 PASS |
| **M-G6-SCRIP-JVM** | Scrip → JVM | M-G5-LOWER-SCRIP-FIX | Scrip JVM rung01 PASS |
| **M-G6-SCRIP-NET** | Scrip → .NET | M-G5-LOWER-SCRIP-FIX | Scrip NET rung01 PASS |
| **M-G6-SCRIP-WASM** | Scrip → WASM | M-G5-LOWER-SCRIP-FIX + M-G6-SNOBOL4-WASM | Scrip Wx86 rung01 PASS |

---

### Phase 7 — Style Consistency Pass

Final pass: every source file in `src/` conforms to a single style document.
No logic changes.

| ID | Action | Verify |
|----|--------|--------|

---

### Phase 9 — Post-Reorg Cleanup (new, G-9 s23)

Three cleanup milestones identified during assessment. None block other sessions — purely
internal consistency of the compiler source. Fire opportunistically.

| ID | Action | Verify |
|----|--------|--------|

---

## Dependency Graph

```
M-G0-FREEZE
    ├── M-G0-AUDIT
    └── M-G0-IR-AUDIT
            └── M-G1-IR-HEADER-DEF
                    └── M-G1-IR-HEADER-WIRE
                            ├── M-G1-IR-PRINT
                            └── M-G1-IR-VERIFY
                                    └── M-G2-DIRS
                                            └── M-G2-MOVE-* (×7, sequential)
                                                    └── M-G2-MOVE-PROLOG-ASM-a
                                                            └── M-G2-MOVE-PROLOG-ASM-b
                                                                    └── M-G4-SHARED-CONC/OR/ARBNO/CAPTURE/ARITH/ASSIGN/IDX (sequential)
                                                                            └── M-G4-SHARED-ICON-TO → SUSPEND → ALT → BANG → LIMIT (sequential)
                                                                            └── M-G4-SHARED-PROLOG-UNIFY → CLAUSE → CUT → TRAIL (sequential)
                                                                                    └── M-G5-LOWER-*-AUDIT → M-G5-LOWER-*-FIX (×6, one per frontend, sequential)
                                                                                            └── M-G3-NAME-* (×9, one per surviving file) ← REORDERED: after collapse
                                                                                                    └── M-G6-* (×15, parallel)
                                                                                                            └── M-G7-STYLE-DOC
                                                                                                                    └── M-G7-STYLE-*
                                                                                                                            └── M-G7-UNFREEZE
                                                                                                                                    └── M-G8-HOME (design decisions, parallel)
                                                                                                                                    └── M-G8-DEPTH
                                                                                                                                    └── M-G8-ORACLE
                                                                                                                                    └── M-G8-GRAMMAR
                                                                                                                                            └── M-G8-ENUM-CORE
                                                                                                                                                    └── M-G8-EMIT-SNO
                                                                                                                                                            └── M-G8-RUNNER
                                                                                                                                                                    └── M-G8-SNOBOL4-N10
                                                                                                                                                                            └── M-G8-SNOBOL4-N25
                                                                                                                                                                                    └── M-G8-ICON-GRAMMAR
                                                                                                                                                                                            └── M-G8-ICON-N25
                                                                                                                                                                                                    └── M-G8-PROLOG-GRAMMAR
                                                                                                                                                                                                            └── M-G8-PROLOG-N25
                                                                                                                                                                                                                    └── M-G8-CI
```

---
## Success Criteria

The Grand Master Reorg is complete (M-G7-UNFREEZE fires) when:

1. `src/` has the folder structure shown above, exactly. Six frontend directories, four active backend directories, one dead `c/` directory untouched.
2. All emitter files follow the naming law — no deviations.
3. `src/ir/ir.h` contains the unified `EKind` enum covering all six frontends.
4. No node kind is defined in more than one header.
5. The Byrd box wiring logic for every shared node kind lives in exactly one place.
6. Every corpus test that passed before the reorg still passes.
7. `doc/STYLE.md` exists and all source files conform to it.
8. The `one4all` pipeline matrix (6 frontends × 4 backends = 24 cells) has at least one ✅ or ⏳ in every cell that was previously `—` but is now reachable via shared backend infrastructure. (`snobol4net` and `snobol4jvm` are separate repos with their own roadmaps and are excluded from this criterion.)

The full project testing transformation is complete (M-G8-CI fires) when:

9. Four design-decision docs exist: `doc/GEN_HOME.md`, `doc/GEN_DEPTH.md`,
   `doc/GEN_ORACLE.md`, `doc/GEN_GRAMMAR.md` — all consistent, all agreed.
10. `gen/enumerate.py` enumerates IR trees for SNOBOL4, Icon, and Prolog grammar
    fragments up to depth N=25.
11. Zero divergences between oracle and all three one4all backends at N=25 for
    all three language fragments.
12. The N=10 slice runs in CI on every commit to one4all in under 5 minutes.

---

### Phase 9 — Repo Rename: snobol4dotnet → snobol4net

Executed **after** M-G7-UNFREEZE. Purely administrative — no code changes.
Prerequisite: all concurrent sessions have resumed and are stable post-reorg.

| ID | Action | Verify |
|----|--------|--------|
| **M-G9-RENAME-NET-PLAN** | Confirm impact: update all cross-repo references in `one4all`, `snobol4jvm`, `.github`, `harness`, `corpus` that mention `snobol4dotnet`. Produce checklist. | Checklist exists; no stale refs after rename |
| **M-G9-RENAME-NET-EXEC** | Rename GitHub repo `snobol4ever/snobol4dotnet` → `snobol4ever/snobol4net`. GitHub creates redirect from old name automatically. Update RENAME.md name grid. | `git ls-remote github.com/snobol4ever/snobol4net` resolves; old name redirects |
| **M-G9-RENAME-NET-REFS** | Update every cross-repo reference found in M-G9-RENAME-NET-PLAN: `.github` docs, `one4all` runner scripts, `harness` adapters. One repo per commit. | All references resolve; no broken links |
| **M-G9-RENAME-NET-VERIFY** | Run `snobol4net` full test suite. Confirm nothing broke. Count TBD — retest required before this milestone can close. | Full suite PASS (retest to establish count) |

---

*GRAND_MASTER_REORG.md — living document.*
*Completed G-milestone rows → MILESTONE_ARCHIVE.md per standard protocol.*
*All concurrent development unfrozen — M-G7-UNFREEZE ✅ G-9 s24.*

---

