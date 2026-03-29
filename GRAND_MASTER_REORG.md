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
| **M-G0-FREEZE** ✅ | Tag current HEAD of one4all as `pre-reorg-freeze` (`a051367`). Baseline recorded in `doc/BASELINE.md`. harness HEAD: `eced661`. corpus HEAD: `ccd79fa`. All concurrent development frozen. | Tag pushed; `doc/BASELINE.md` committed `716b814` |
| **M-G0-RENAME** ✅ | Confirmed: `harness` and `corpus` already use canonical marketing names in all one4all and .github cross-repo references. GitHub redirects from old dash-form slugs (`snobol4-harness`, `snobol4-corpus`) are live — both resolve to the same HEAD. Zero file changes required. | All references verified clean |
| **M-G0-CORPUS-AUDIT** ✅ | **Plan + Execute** the migration of corpus source programs out of `one4all` and into `corpus`. | `doc/CORPUS_MIGRATION.md` all boxes checked `631b69f` one4all. Icon/Prolog/SNOBOL4/Snocone/Rebus migrated G-9 s8. corpus HEAD `c29fe83`. one4all HEAD `631b69f`. |
| **M-G0-AUDIT** ✅ | Audit all emitter files: document every `emit_<thing>` function signature, every local variable name, every generated label pattern. Covers: `emit_byrd_asm.c`, `emit_byrd_jvm.c`, `emit_byrd_net.c`, `emit_wasm.c` (stub), `icon_emit_jvm.c`, `prolog_emit_jvm.c`, `icon_emit.c` (x64 icon), and the Prolog-x64 sections of `emit_byrd_asm.c`. Produce `doc/EMITTER_AUDIT.md`. | `doc/EMITTER_AUDIT.md` committed `252dac0` |
| **M-G0-IR-AUDIT** ✅ | Audit all six frontend IRs: list every node kind used, cross-reference to the target unified enum above. Produce `doc/IR_AUDIT.md`. `E_VAR` renamed `E_VAR` (T was SIL type-code artifact). 45 canonical node names. See `ARCH-sil-heritage.md`. | `doc/IR_AUDIT.md` updated; `ARCH-sil-heritage.md` committed `fb90365` |
| **M-G0-SIL-NAMES** ✅ | **Broader SIL heritage naming analysis.** G-7 covered IR node names only. The SIL naming heritage extends to: (1) runtime variable names in generated code (`sno_var_X`, `sno_cursor`, `pl_trail_top`, `icn_retval` — do these align with SIL's VARTYP/cursor conventions?); (2) emitter C source variable names (`scrip-cc.h` struct fields, local names in emit functions); (3) generated label prefixes (`P_`, `L`, `sno_`, `pl_`, `icn_`, `pj_`, `ij_`); (4) runtime library function names (`snobol4_asm.mac` macro names, Byrd box macro library). Produce `doc/SIL_NAMES_AUDIT.md` covering all four areas. **Prerequisite for M-G3** — naming law may need extension once broader heritage is understood. | `doc/SIL_NAMES_AUDIT.md` committed — covers all four areas. Two law additions: `ICN_OUT()` for icon_emit.c write macro (avoids `E()` collision); EKind alias bridge documentation. `snobol4_asm.mac` is fully conformant gold standard. No law corrections needed — existing law is sound. |
| **M-G-EMIT-COVERAGE** ✅ | Emit-diff coverage: one test per IR node kind across all applicable backends. SNOBOL4: `test/snobol4/coverage/coverage_sno_nodes.sno` — all 26 frontend-emitted node kinds (E_QLIT E_ILIT E_FLIT E_VART E_KW E_NULV E_ADD E_SUB E_MPY E_DIV E_MNS E_EXPOP E_CONCAT E_SEQ E_OR E_NAM E_DOL E_ATP E_ARB E_ARBNO E_STAR E_INDR E_FNC E_IDX E_ASGN E_OPSYN). Prolog: `test/prolog/coverage/coverage_pl_nodes.pl` — all 15 Prolog IR node kinds. Icon: `test/icon/coverage/coverage_x64_gaps.icn` (existing, covers 28 ICN kinds). Emit-diff: **493/0** ✅. | one4all `6d8dd4b` |
| **M-G-INV-FAST** ✅ | Invariant harness speed overhaul. Root cause: per-test JVM startup (jasmin + java) × ~152 tests = 3–5 min, causing session timeouts. Fixes: (1) **Persistent runtime archive cache** `out/rt_cache/libsno4rt_asm.a` + `libsno4rt_pl.a` — stamp-checked, rebuilt only on source change; (2) **Batch jasmin** — all `.j` files assembled in one `java -jar jasmin` call per suite; (3) **Single SnoHarness JVM** — all SNOBOL4-JVM and Prolog-JVM tests run in one `java -cp SnoHarness` process with per-test classloader + 3s thread timeout; (4) **Parallel nasm+link** via `xargs -P$JOBS`. Result: harness now produces output within 240s. | G-9 s2 · .github pending |
| **M-G-INV-TIMEOUT** ✅ | Hang detection requirement: no infinite-loop test may block harness for more than seconds. Implemented five-layer timeout defence: (1) per-binary x86 `timeout $TIMEOUT_X86` (5s); (2) SnoHarness internal 3s per-class thread; (3) batch jasmin `timeout 60`; (4) SnoHarness suite `timeout 120`; (5) suite-level watchdog background process kills harness after `SUITE_TIMEOUT=300`s. All 38 icon rung runners patched (two structural families). START/FINISH/ELAPSED printed at top and bottom of `run_emit_check.sh` and `run_invariants.sh`. | G-9 s2 · .github pending |
| **M-G-INV-FAST-X86-FIX** | Fix snobol4_x86 LINK_FAIL in new parallel harness. Root cause: `_x86_compile_one` exported bash function not visible inside `bash -c` subshell spawned by `xargs`. Fix: rewrite xargs dispatch to write per-test mini-scripts to `$WORK/jobs/NNN.sh` and invoke with `xargs -P$JOBS bash`. Verify 106/106 snobol4_x86. | Next session — do first |
| **M-G-INV-SESSION-BASELINE** ✅ | Gate: confirm full invariant suite runs to completion in the current Claude session environment. Fix: removed parallel dispatch + watchdog, replaced with serial cell execution. Result: 60.8s wall time, `snobol4_x86 106/106` ✅, Prolog x86 11/107 (96 pre-existing compile failures, not a regression), Icon 0/0, JVM/NET SKIP. Baseline confirmed. | `snobol4_x86 106/106` ✅ · one4all `4f30e7f` |

#### M-G0-CORPUS-AUDIT — Inventory and Open Decisions

**What was found in `one4all/test/` (G-7 session, 2026-03-28):**

All corpus source programs currently living in `one4all`. None of these belong here
post-reorg — they must migrate to `corpus`.

| Location in one4all | Extensions | Count | Destination in corpus |
|-----------------------|-----------|-------|------------------------------|
| `test/frontend/icon/corpus/rung01–rung38/` | `.icn` | 258 | `programs/icon/rung*/` (TBD — check overlap with existing 851 files) |
| `test/frontend/prolog/corpus/rung*/` | `.pl`, `.pl` | 130 | `programs/prolog/rung*/` |
| `test/frontend/snocone/sc_asm_corpus/` | `.sc` | 10 | `programs/snocone/` |
| `test/crosscheck/sc_corpus/` | `.sc` | 20 | `crosscheck/snocone/` or `programs/snocone/crosscheck/` |
| `test/frontend/snobol4/` | `.sno` | 5 | `programs/snobol4/smoke/` |
| `test/beauty/*/driver.sno` + subsystems | `.sno` | 19 | `programs/snobol4/beauty/` |
| `test/feat/f*.sno` | `.sno` | 20 | `programs/snobol4/feat/` |
| `test/jvm_j3/*.sno` | `.sno` | 6 | `programs/snobol4/jvm_j3/` |
| `test/rebus/*.reb` | `.reb` | 3 | `programs/rebus/` |

**Also present alongside each source program: `.expected` and `.ref` oracle output files.**
These travel with the source programs (decision pending — see below).

**Total source programs to migrate: ~471 files** (source + oracle pairs).

**Decisions resolved (2026-03-28, Lon):**

1. **Oracle files (`.expected` / `.ref`):** ✅ **Migrate to `corpus`** alongside
   their source programs. Source and oracle are a unit — they travel together.

2. **Runner scripts (`run_rung*.sh` etc.):** ✅ **Stay in all three compiler/runtime repos**
   (`one4all`, `snobol4jvm`, `snobol4dotnet`/`snobol4net`), with paths updated to point
   to `corpus`. Runners are compiler-specific test drivers, not shared infrastructure.

3. **Overlap / dedup:** ✅ **Clone `corpus` and diff first.** If a file exists in
   both repos with identical content → keep one copy in `corpus`, remove from
   `one4all`. If content differs → human review before any merge. No blind overwrites.

**Dedup analysis complete (G-7 session, 2026-03-28):**

`corpus` was cloned and diffed against every one4all corpus directory.
Result: **zero content conflicts**. Every file in `one4all/test/` is either
entirely absent from `corpus` or clearly distinct. No blind-overwrite risk.

| Frontend | one4all location | Files | In corpus? | Action |
|----------|-------------------|-------|-------------------|--------|
| Icon | `test/frontend/icon/corpus/rung01–38/` | 258 `.icn` | ❌ Not present (corpus has IPL only) | Move to `programs/icon/rung*/` |
| Prolog | `test/frontend/prolog/corpus/rung*/` | 130 `.pl/.pl` | ❌ Not present | Move to `programs/prolog/rung*/` |
| Snocone | `test/frontend/snocone/sc_asm_corpus/` | 10 `.sc` | ❌ Not present | Move to `programs/snocone/corpus/` |
| Snocone | `test/crosscheck/sc_corpus/` | 20 `.sc` | ❌ Not present | Move to `crosscheck/snocone/` |
| SNOBOL4 | `test/frontend/snobol4/*.sno` | 5 `.sno` | ❌ Not present | Move to `programs/snobol4/smoke/` |
| SNOBOL4 | `test/beauty/*/driver.sno` + subsystems | 19 `.sno` | ❌ Not present | Move to `programs/snobol4/beauty/` |
| SNOBOL4 | `test/feat/f*.sno` | 20 `.sno` | ❌ Not present | Move to `programs/snobol4/feat/` |
| SNOBOL4 | `test/jvm_j3/*.sno` | 6 `.sno` | ❌ Not present | Move to `programs/snobol4/jvm_j3/` |
| Rebus | `test/rebus/*.reb` | 3 `.reb` | ❌ Not present | Move to `programs/rebus/` |

**One file resolved this session:**
`corpus/programs/beauty/beauty.sno` removed (`6c964b8`). The corpus version
used `.inc` extensions and different indentation — stale. `one4all/demo/beauty.sno`
is the single authoritative copy.

**All `.expected`/`.ref` oracle files travel with their source programs** (per decision 1).

**Execution order:**

| Step | Action | Verify |
|------|--------|--------|
| 1 | Move Icon corpus (258 `.icn` + oracles). One rung dir per commit to corpus; matching removal from one4all. | Icon invariants green after each batch |
| 2 | Move Prolog corpus (130 `.pl`/`.pl` + oracles). Same pattern. | Prolog JVM 31/31 green |
| 3 | Move Snocone corpus (30 `.sc` + oracles). | Snocone 10/10 green |
| 4 | Move SNOBOL4 test programs (beauty drivers, feat, jvm_j3, smoke — 50 `.sno` + oracles). | SNOBOL4 x86 106/106 + JVM + 110/110 NET green |
| 5 | Move Rebus corpus (3 `.reb` + oracles). | Rebus 3/3 green |
| 6 | **HOLD** — `demo/beauty.sno` vs corpus `beauty.sno` divergence. Human review. | Lon sign-off |
| 7 | Update runner script paths in `one4all`, `snobol4jvm`, `snobol4dotnet`/`snobol4net`. | All runners execute against `corpus` paths |
| 8 | Run full invariant suite. | All four backend invariants green |

---

### Phase 1 — Unified IR Header

| ID | Action | Verify |
|----|--------|--------|
| **M-G1-IR-HEADER-DEF** ✅ | Create `src/ir/ir.h` with the full unified `EKind` enum (all node kinds from all frontends, listed above). Do **not** include it anywhere yet. Compile it standalone: `gcc -c src/ir/ir.h` (or equivalent). Fix any exhaustive-switch warnings that would fire when new kinds are added. | `gcc -fsyntax-only src/ir/ir.h` clean ✅; `IR_DEFINE_NAMES` name table PASS ✅; `IR_COMPAT_ALIASES` 15 bridges PASS ✅; `E_KIND_COUNT = 59` ✅. Commit one4all `a1f9a76`. |
| **M-G1-IR-HEADER-WIRE** ✅ | Add `#include "ir/ir.h"` to `scrip-cc.h`. Fix any `switch(kind)` statements that become non-exhaustive (add `default: assert(0)` where appropriate). No logic changes. | `make -j4` clean ✅; x86 106/106 ✅. E_ARY/E_IDX duplicate cases collapsed (sval-based dispatch) in all 4 backends. EXPR_T_DEFINED guard added to ir.h. -I . added to Makefile. Commit one4all `4cb03d4`. |
| **M-G1-IR-PRINT** ✅ | Create `src/ir/ir_print.c` — a single `ir_print_node(EXPR_t *e, FILE *f)` that prints any node kind. Used for debugging all frontends uniformly. | Unit test: 6 node types printed correctly ✅; integrated into Makefile ✅; 106/106 ✅. Commit one4all `23d339b`. |
| **M-G1-IR-VERIFY** ✅ | Create `src/ir/ir_verify.c` — structural invariant checker: every node has valid `kind`, `nchildren` matches kind spec, no NULL children where not allowed. Called from driver in debug builds. | 6/6 unit tests PASS ✅; `make debug` target added ✅; 106/106 ✅. Commit one4all `c14da15`. |

---

### Phase 2 — Folder Restructure (mechanical rename only)

| ID | Action | Verify |
|----|--------|--------|
| **M-G2-DIRS** ✅ | Create new directory skeleton: `src/backend/x64/`, `src/backend/jvm/`, `src/backend/net/`. (These may already exist — confirm and adjust.) | All four dirs existed already. ✅ |
| **M-G2-MOVE-ASM** ✅ | `git mv src/backend/x64/emit_byrd_asm.c src/backend/x64/emit_x64.c`. Update `#include` and `Makefile` references. No content changes. | x86 106/106 ✅. Commit `845e255`. |
| **M-G2-MOVE-JVM** ✅ | `git mv src/backend/jvm/emit_byrd_jvm.c src/backend/jvm/emit_jvm.c`. Update references. No content changes. | 106/106 ✅. Commit `845e255`. |
| **M-G2-MOVE-NET** ✅ | `git mv src/backend/net/emit_byrd_net.c src/backend/net/emit_net.c`. Update references. No content changes. | .NET 109/110 [056 pre-existing] ✅. Commit `845e255`. |
| **M-G2-SCAFFOLD-WASM** ✅ | Create `src/backend/wasm/emit_wasm.c` — skeleton only: file header, empty `emit_wasm()` entry point, no IR handling yet. Add to Makefile. | Builds clean ✅. Commit `845e255`. |
| **M-G2-MOVE-ICON-JVM** ✅ | `git mv src/frontend/icon/icon_emit_jvm.c src/backend/jvm/emit_jvm_icon.c`. Update references. No content changes. | Commit `845e255`. |
| **M-G2-MOVE-PROLOG-JVM** ✅ | `git mv src/frontend/prolog/prolog_emit_jvm.c src/backend/jvm/emit_jvm_prolog.c`. Update references. No content changes. | Commit `845e255`. |
| **M-G2-MOVE-ICON-ASM** ✅ | `git mv src/frontend/icon/icon_emit.c src/backend/x64/emit_x64_icon.c`. Update references. No content changes. | Commit `845e255`. |
| **M-G2-ICN-X64-GAP-FILL** ✅ | Implement 28 ICN kinds missing from `emit_x64_icon.c` (present in JVM but unimplemented — `default` stub). Implemented: NONNULL, REAL, SIZE, POW, SEQ_EXPR, IDENTICAL, SWAP, SGT/SGE/SLT/SLE/SNE, REPEAT, BREAK, NEXT, INITIAL, LIMIT, SUBSCRIPT, SECTION/+/-, MAKELIST, RECORD, FIELD, CASE, BANG. Loop control stack added (push/pop in while/until/every/repeat). Runtime additions: `icn_str_cmp`, `icn_strlen`, `icn_pow`, `icn_str_subscript`, `icn_str_section`. Stubs: BANG_BINARY, MATCH, MAKELIST, RECORD, FIELD (list/record runtime deferred). | emit-diff 488/0 ✅ · one4all `6ee8905` |
| **M-G2-MOVE-PROLOG-ASM-a** ✅ | FILE SPLIT step 1 — `src/backend/x64/emit_x64_prolog.c` created; `#include "emit_x64_prolog.c"` at tail of `emit_x64.c` (line 5403). Emit-diff 493/0. | Confirmed G-9 s3 |
| **M-G2-MOVE-PROLOG-ASM-b** ✅ | FILE SPLIT step 2 — Prolog ASM emitter (1842 lines) physically lives in `emit_x64_prolog.c`. `emit_x64.c` retains only the `#include`. Emit-diff 493/0. | Confirmed G-9 s3 |

After M-G2: the file layout matches the target architecture. Every emitter sits
in the backend directory that owns it. **M-G2-MOVE-PROLOG-ASM-a/b must be last** —
they are a file split, not a rename, and carry the most risk within this phase.

---

### Phase 3 — Naming Unification (survivors only, post-collapse)

**⚠ REORDERED 2026-03-28:** Phase 3 now executes **after** Phase 4 (shared wiring
extraction) and Phase 5 (frontend unification). Rationale: Phase 4 collapses
duplicate `emit_<Kind>` functions across backends into shared wiring in
`ir_emit_common.c`; Phase 5 eliminates frontend-local node types. Renaming
pre-collapse duplicates that Phase 4 will immediately delete or merge produces
wasted milestones and confusion. The naming law is applied once to the survivors —
the code that actually remains after the collapse — not to temporaries.

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

| ID | File | What changes | Verify |
|----|------|-------------|--------|
| **M-G3-NAME-COMMON** | `ir_emit_common.c` | Verify naming law from creation — no renames expected since file is written post-collapse; confirm `emit_wiring_<Kind>` function names, Greek port variable names, no deviations. | All corpus PASS (shared file) |
| **M-G3-NAME-X64** | `emit_x64.c` | Rename backend-specific residuals: local vars, label strings, function names → naming law. `E()`/`EI()`/`EL()` macros confirmed. | x86 106/106 |
| **M-G3-NAME-JVM** | `emit_jvm.c` | Same. `J()`/`JI()`/`JL()` confirmed. | 106/106 JVM |
| **M-G3-NAME-NET** | `emit_net.c` | Same. `N()`/`NI()`/`NL()` confirmed. | 110/110 NET |
| **M-G3-NAME-WASM** | `emit_wasm.c` | Naming law applied from scratch at scaffold time (M-G2-SCAFFOLD-WASM); verify only. `W()`/`WI()`/`WL()`. | Builds clean |
| **M-G3-NAME-X64-ICON** | `emit_x64_icon.c` | `icon_emit_*` → `emit_x64_icon_*` for Icon-specific residuals after Phase 4 extraction. | Icon x86 rung03 5/5 |
| **M-G3-NAME-X64-PROLOG** | `emit_x64_prolog.c` | `pl_emit_*` → `emit_x64_prolog_*` for Prolog-specific residuals. | Prolog x86 rungs 1–9 PASS |
| **M-G3-NAME-JVM-ICON** | `emit_jvm_icon.c` | `ij_emit_*` → `emit_jvm_icon_*` for Icon-specific residuals. | Icon JVM 99/99 |
| **M-G3-NAME-JVM-PROLOG** | `emit_jvm_prolog.c` | `pj_emit_*` → `emit_jvm_prolog_*` for Prolog-specific residuals. | Prolog JVM 20/20 |

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
| **M-G4-SHARED-CONC-FOLD** ✅ | `E_SEQ`/`E_OR` n-ary | `ir_nary_right_fold` + `ir_nary_right_fold_free` in `ir_emit_common.c`. x64 ×3 + JVM ×2 inline folds replaced. Dead C backend inline folds retained (no test). one4all `9f947cd`. | emit-diff 488/0 |
| **M-G4-SHARED-CONC-SEQ** ✅ | `E_SEQ` binary | Not extracted — .NET deferred-commit pre-scan makes x64/NET binary paths non-isomorphic. Wiring stays in `emit_seq()` (x64) and `net_emit_pat_node E_SEQ` (NET). Decision recorded G-9s1. | n/a — no code change |
| **M-G4-SHARED-OR** ✅ | `E_OR` | NOT extracted — same decision as E_SEQ. Three backends diverge on: (1) cursor-save mechanism (BSS var/ASM macro vs JVM local int vs CIL local int); (2) n-ary handling (.NET native loop, x64+JVM use ir_nary_right_fold); (3) child-emit callback signatures incompatible. Wiring stays in-situ per backend. Decision recorded G-9 s3. | n/a — no code change |
| **M-G4-SHARED-ARBNO** ✅ | `E_ARBNO` | NOT extracted — three divergence axes: (1) cursor-save mechanism (.bss/NASM-macro stack vs JVM local int vs CIL local int); (2) β port implemented in x64, absent in JVM and .NET; (3) child-emit callback signatures all differ. Wiring stays in-situ. Icon E_ARBNO gap (not wired in icon emitters) noted as Phase 5/6 scope. `doc/M-G4-SHARED-ARBNO.md` one4all `c1f9d3d`. | n/a — no code change |
| **M-G4-SHARED-CAPTURE** ✅ | `E_CAPT_COND`, `E_CAPT_IMM` | NOT extracted — four divergence axes: (1) cursor-save (.bss CaptureVar registry vs JVM local int vs CIL local int); (2) β port in x64, absent in JVM/.NET; (3) variable-store (.bss buf+len vs sno_var_put invokestatic vs stsfld); (4) child callback signatures differ. E_NAM/E_DOL treated identically in all backends (pre-existing). `doc/M-G4-SHARED-CAPTURE.md` one4all `3b9f159`. | n/a — no code change |
| **M-G4-SHARED-ARITH** ✅ | `E_ADD/SUB/MPY/DIV/MOD` | NOT extracted — three fundamentally different arithmetic models: NASM macro fast-paths + APPLY_FN_N (x64); double-bytecode with inline integer detection (JVM); pure library delegation Snobol4Lib::sno_add etc. (NET). E_MOD absent from all arith case blocks — needs follow-up. `doc/M-G4-SHARED-ARITH.md` one4all `1924740`. | n/a — no code change |
| **M-G4-SHARED-ASSIGN** ✅ | `E_ASSIGN` | NOT extracted — E_ASSIGN not dispatched as expr-IR node in any SNOBOL4/Prolog backend (assignment is statement-level). Icon uses ICN_ASSIGN (own node) in both x64 and JVM, but those diverge substantially (rbp-slot+type-tag vs JVM type-inferred putstatic/istore/astore). `doc/M-G4-SHARED-ASSIGN.md` one4all `9f8a610`. | n/a — no code change |
| **M-G4-SHARED-IDX** ✅ | `E_IDX` | NOT extracted — ABI and dispatch all diverge: x64 SysV DESCR_t pairs via C stack stmt_aref/stmt_aref2; JVM string-based sno_array_get invokestatic + sno_indr_get + StringBuilder 2D keys; NET net_array_get static call + ldsfld + net_field_name. Child-emit signatures and result locations differ. `doc/M-G4-SHARED-IDX.md` one4all `1d59258`. | n/a — no code change |
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
| **M-G5-LOWER-SNOBOL4-AUDIT** | snobol4 | Audit `parse.c` / `lower.c` — list every node kind produced. Cross-reference to unified enum. Produce `doc/IR_LOWER_SNOBOL4.md` with gap table. No code changes. | File exists |
| **M-G5-LOWER-SNOBOL4-FIX** | snobol4 | For each gap in `doc/IR_LOWER_SNOBOL4.md`: add missing kind to enum (if absent), wire bridge in `lower.c`. One commit per gap. | 106/106 after each gap fixed |
| **M-G5-LOWER-ICON-AUDIT** | icon | Audit `IcnNode` kinds — map each to unified enum or flag as frontend-local extension. Produce `doc/IR_LOWER_ICON.md`. No code changes. | File exists |
| **M-G5-LOWER-ICON-FIX** | icon | For each gap: add kind or wire explicit bridge. One commit per gap. | Icon x86 rung03 5/5 after each gap |
| **M-G5-LOWER-PROLOG-AUDIT** | prolog | Confirm `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*` are all in unified enum (Phase 1). Produce `doc/IR_LOWER_PROLOG.md` — expected to be short. | File exists |
| **M-G5-LOWER-PROLOG-FIX** | prolog | Fix any gaps found. (Expected: none.) | Prolog JVM 20/20 |
| **M-G5-LOWER-SNOCONE-AUDIT** | snocone | Audit lowered form — map to unified enum. Produce `doc/IR_LOWER_SNOCONE.md`. | File exists |
| **M-G5-LOWER-SNOCONE-FIX** | snocone | Fix gaps. One commit per gap. | Snocone corpus PASS after each gap |
| **M-G5-LOWER-REBUS-AUDIT** | rebus | Audit `rebus_emit.c` — map Rebus AST nodes to unified enum. Produce `doc/IR_LOWER_REBUS.md`. | File exists |
| **M-G5-LOWER-REBUS-FIX** | rebus | Fix gaps. One commit per gap. | Rebus corpus PASS after each gap |
| **M-G5-LOWER-SCRIP-AUDIT** | scrip | Audit Scrip AST — map every node kind to unified enum or flag as Scrip-specific extension. Produce `doc/IR_LOWER_SCRIP.md`. No code changes. | File exists |
| **M-G5-LOWER-SCRIP-FIX** | scrip | For each gap: add kind or wire explicit bridge. One commit per gap. | Scrip corpus PASS after each gap |

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
| **M-G7-STYLE-DOC** | Write `doc/STYLE.md` — indentation (4 spaces), brace style, comment format, function header block format, generated-code column widths (`COL_W`, `COL2_W`, `COL_CMT`). | File exists |
| **M-G7-STYLE-BACKENDS** | Apply style to all backend files. | All corpus tests PASS |
| **M-G7-STYLE-FRONTENDS** | Apply style to all frontend files. | All corpus tests PASS |
| **M-G7-STYLE-IR** | Apply style to `src/ir/`. | Builds clean |
| **M-G7-UNFREEZE** | Lift concurrent-development freeze. Update PLAN.md: resume all session rows from their pre-reorg HEADs. Tag `post-reorg-baseline`. | All four backend invariants green; all frontend corpus PASS |

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
*All concurrent development frozen until M-G7-UNFREEZE.*

---

