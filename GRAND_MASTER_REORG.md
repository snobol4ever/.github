# GRAND_MASTER_REORG.md — Grand Master Reorganization
*2026-03-25 — authored by Claude Sonnet 4.6 in consultation with the project record*
*2026-03-25 — milestones decomposed for incremental safety by Claude Sonnet 4.6 (G-6 session)*

---

## The Problem

The project is a matrix of **6 frontends × 4 active backends**, housed across three
compiler/runtime product repos:

| Repo | Role | Language | Notes |
|------|------|----------|-------|
| `snobol4x` | Compiler/runtime — 2D matrix | C | 6 frontends × 4 active backends |
| `snobol4jvm` | Compiler/runtime | Clojure | SNOBOL4/SPITBOL → JVM only |
| `snobol4dotnet` → `snobol4net` | Compiler/runtime | C# | SNOBOL4/SPITBOL → .NET only; rename pending (M-G9) |
| `snobol4harness` | Test infrastructure | Shell/Python | Corpus runner, adapter scripts, probe/monitor |
| `snobol4corpus` | Test data | SNOBOL4/Icon/Prolog | Canonical crosscheck corpus used by all backends |
| `snobol4python` | Pattern library | Python | Out of scope for this reorg |
| `snobol4csharp` | Pattern library | C# | Out of scope for this reorg |

`snobol4jvm` and `snobol4dotnet` are single-frontend/single-backend repos in different
host languages; they are **not restructured here**.

`snobol4harness` and `snobol4corpus` are infrastructure repos. They are **not
structurally reorganized** but their rename (to the canonical `snobol4harness` /
`snobol4corpus` marketing names, per RENAME.md) is part of the reorg scope and
is executed in **M-G0-RENAME** below.

`snobol4x` is the 2D matrix repo — the only one that is, or will be, multi-frontend
and multi-backend. `snobol4jvm` and `snobol4dotnet` are single-frontend/single-backend
repos written in different host languages; they are **not restructured here**.

A fifth backend, **C** (`sno2c`), exists in `snobol4x` but is effectively dead — it
produces C output that is not actively maintained or tested. It is **excluded from
the reorg** (not moved, not renamed, not wired to shared IR). Its presence is noted
here only to prevent confusion with the active backends.

Each pipeline in `snobol4x` was built when it was needed, with naming, folder
structure, and IR conventions that were right-for-the-moment. The result is structural debt:

- **Six separate IRs** (or near-IRs): SNOBOL4's `EXPR_t/EKind`, Icon's `IcnNode`,
  Prolog's `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*`, Snocone's lowered form,
  Rebus's AST, Scrip's AST. Each frontend invented its own node vocabulary.
- **Emitters are not parallel.** `emit_byrd_asm.c` (6937 lines) is the oracle.
  `emit_byrd_jvm.c` (4479 lines) mirrors it for SNOBOL4 only. `emit_byrd_net.c`
  (2669 lines) mirrors it for SNOBOL4 only. `icon_emit_jvm.c` (3308 lines) is
  Icon-only. `prolog_emit_jvm.c` (2676 lines) is Prolog-only. No frontend other
  than SNOBOL4 has all four active backends.
- **Naming is inconsistent.** Greek letters, label prefixes, local variable names,
  and generated-code symbol conventions differ across emitters and frontends.
- **Folder structure reflects history, not architecture.** Prolog and Icon JVM
  emitters live under `src/frontend/`, not `src/backend/`.

The goal of the Grand Master Reorganization is to impose a single clean architecture
across `snobol4x`:

```
6 frontends → ONE shared IR → 4 active backends (x64 ASM, JVM, .NET, WASM)
```

Every frontend lowers to the same IR. Every backend consumes that same IR.
The 24 pipelines (6 × 4) become consistent by construction.

---

## Target Architecture

### Folder Structure (post-reorg)

```
snobol4x/
  src/
    frontend/
      snobol4/        lex.c  parse.c  lower.c   → IR
      snocone/        lex.c  parse.c  lower.c   → IR
      rebus/          lex.c  parse.c  lower.c   → IR
      icon/           lex.c  parse.c  lower.c   → IR
      prolog/         lex.c  parse.c  lower.c   → IR
      scrip/          lex.c  parse.c  lower.c   → IR
    ir/
      ir.h            ← THE shared IR: unified EKind enum + EXPR_t
      ir_print.c      ← IR pretty-printer (debugging)
      ir_verify.c     ← IR structural invariant checker
    backend/
      x64/
        emit_x64.c    ← THE x64 emitter (consumes IR)
        emit_x64.h
      jvm/
        emit_jvm.c    ← THE JVM emitter (consumes IR)
        emit_jvm.h
      net/
        emit_net.c    ← THE .NET emitter (consumes IR)
        emit_net.h
      wasm/
        emit_wasm.c   ← THE WebAssembly emitter (consumes IR)
        emit_wasm.h
      c/              ← DEAD — sno2c C backend, not maintained, excluded from reorg
    runtime/
      asm/            (unchanged)
      jvm/            (unchanged)
      net/            (unchanged)
      wasm/           (Emscripten-compiled runtime for browser IDE)
    driver/
      main.c          (updated: route any frontend → any backend)
```

### The Shared IR

All frontends lower to `EXPR_t` nodes using a **unified `EKind` enum**.
New node kinds are added to the shared enum only — never in a frontend header.

**Byrd box node kinds (all backends must handle all of these):**

| Kind | Meaning | α | β |
|------|---------|---|---|
| `E_QLIT` | String literal match | match at cursor | restore, fail |
| `E_ILIT` | Integer literal | load value | — |
| `E_FLIT` | Float literal | load value | — |
| `E_VART` | Variable reference | load binding | — |
| `E_CONC` | Concatenation / sequence | left then right | right-ω → left-β |
| `E_OR` | Alternation | try left | left-ω → try right |
| `E_ARBNO` | Zero-or-more | try zero | undo last match |
| `E_POS` | Cursor position assert | check cursor == n | fail |
| `E_RPOS` | Right cursor assert | check cursor == len-n | fail |
| `E_ARB` | Arbitrary match | try 0 chars | advance one, retry |
| `E_DOT` | Cursor capture (`.`) | match, capture cursor | pass β to child |
| `E_DOLLAR` | Value capture (`$`) | match, capture value | pass β to child |
| `E_FNC` | Function call / goal | call | — |
| `E_ASSIGN` | Assignment | evaluate RHS, assign | — |
| `E_ADD/SUB/MPY/DIV/MOD` | Arithmetic | evaluate | — |
| `E_IDX` | Array/table subscript | aref | — |
| `E_UNIFY` | Prolog unification | bind with trail | unwind trail, fail |
| `E_CLAUSE` | Prolog Horn clause | try head | retry next |
| `E_CHOICE` | Prolog predicate | α of first clause | β chain |
| `E_CUT` | Prolog cut / FENCE | seal β | unreachable |
| `E_TRAIL_MARK` | Save trail top | mark | — |
| `E_TRAIL_UNWIND` | Restore trail | unwind | — |
| `E_SUSPEND` | Icon suspend / generator | yield value | resume |
| `E_TO` | Icon `i to j` generator | emit i | increment, retry |
| `E_TO_BY` | Icon `i to j by k` | emit i | step by k, retry |
| `E_LIMIT` | Icon `E \ N` limitation | count down | fail at 0 |
| `E_ALT_GEN` | Icon alt generator | emit left | left-done → emit right |
| `E_BANG` | Icon `!E` (iterate string) | emit first char | next char |
| `E_SCAN` | Icon `E ? E` scanning | set subject | restore subject |
| `E_SWAP` | Icon `:=:` swap | swap bindings | — |
| `E_POW` | Icon `^` power | compute | — |

### Naming Convention — THE LAW

This convention applies **identically** in all emitter files and all six frontends.
Every generated label, every C variable, every comment uses these names.
No exceptions. No aliases. No abbreviations beyond those listed here.

**Greek ports — used everywhere without exception (C source, comments, generated output):**

| Port | C name | Generated label fragment | Meaning |
|------|--------|--------------------------|---------|
| α | `α` | `_α` | Fresh entry |
| β | `β` | `_β` | Resume after downstream failure |
| γ | `γ` | `_γ` | Success exit |
| ω | `ω` | `_ω` | Failure exit |

Greek letters are used **everywhere**: C variable names, C parameter names, struct
field names, label string literals, comments. No ASCII spelling-out (`alpha`,
`beta`, `gamma`, `omega`) anywhere. No `lbl_alpha`, no `lbl_gamma`. The Greek
letter is the name.

**Greek ports — generated labels (in .asm / .j / .il output):**

| Backend | Alpha label | Beta label | Notes |
|---------|-------------|------------|-------|
| x64 ASM | `P_<id>_α:` | `P_<id>_β:` | γ/ω are caller-supplied jumps |
| JVM | `L<id>_α` | `L<id>_β` | id = unique integer per node |
| .NET | `L<id>_α` | `L<id>_β` | same scheme as JVM |

**Node ID convention:** Every IR node gets a unique integer `id` assigned during
the emit pass. Generated labels are always `L<id>_<port>` (JVM/.NET) or
`P_<id>_<port>` (x64).

**C-side naming (emitter source code):**

| Purpose | Name |
|---------|------|
| Current node being emitted | `node` |
| Left child | `left` / `node->children[0]` |
| Right child | `right` / `node->children[1]` |
| Node unique id | `node->id` |
| Alpha label string | `α` |
| Beta label string | `β` |
| Gamma label string (passed in) | `γ` |
| Omega label string (passed in) | `ω` |
| Emit function signature | `emit_<kind>(EXPR_t *node, const char *γ, const char *ω)` |
| Output file | `out` (all backends) |
| Output macro | `E(fmt, ...)` (x64) · `J(fmt, ...)` (JVM) · `N(fmt, ...)` (.NET) · `W(fmt, ...)` (WASM) |
| Instruction emit helper | `EI(instr, ops)` · `JI(instr, ops)` · `NI(instr, ops)` · `WI(instr, ops)` |
| Label definition helper | `EL(label, instr, ops)` · `JL(...)` · `NL(...)` · `WL(...)` |

**Runtime variable naming in generated code:**

| What | x64 symbol | JVM field | .NET field |
|------|-----------|-----------|-----------|
| SNOBOL4 variable `X` | `sno_var_X` (bss) | `sno_var_X` (static String) | `sno_var_X` (static string) |
| Subject string | `sno_subject` | `sno_subject` | `sno_subject` |
| Cursor position | `sno_cursor` | `sno_cursor` (static long) | `sno_cursor` (static int32) |
| Subject length | `sno_sublen` | `sno_sublen` | `sno_sublen` |
| Keyword `&STLIMIT` | `sno_kw_STLIMIT` | `sno_kw_STLIMIT` | `sno_kw_STLIMIT` |
| Keyword `&STCOUNT` | `sno_kw_STCOUNT` | `sno_kw_STCOUNT` | `sno_kw_STCOUNT` |
| Icon failed flag | `icn_failed` | `icn_failed` | `icn_failed` |
| Icon suspended flag | `icn_suspended` | `icn_suspended` | `icn_suspended` |
| Icon return value | `icn_retval` | `icn_retval` | `icn_retval` |
| Prolog trail top | `pl_trail_top` | `pl_trail_top` | `pl_trail_top` |

---

## Migration Strategy

**Concurrent development continues normally until Lon gives the word to begin execution.**
When execution is scheduled, all sessions will be paused for the duration of the reorg.
Until then, every session row in PLAN.md remains active and unblocked.

When execution begins: the reorg is **purely mechanical** at each step — no new features,
no bug fixes, no behavior changes. If a step introduces a regression, it is reverted
entirely. The test suite must be green at the end of every milestone. Any regression → rollback, diagnose, fix before continuing.

### Invariant Table

Each milestone's Verify column references the **minimum set of backend invariants
its change can affect**. A change to a shared file (e.g. `ir.h`, `sno2c.h`,
`emit_x64.c`) triggers all four backends. A change scoped to one backend's emitter
triggers only that backend. A change to one frontend's `lower.c` triggers only the
backends that frontend is wired to.

**Rule:** never declare a milestone done until every backend invariant it touches
is green. If a backend has no runner yet (WASM), "builds clean" is the gate.

#### x64 ASM backend — trigger when: any change to `emit_x64.c`, `emit_x64_*.c`, `ir.h`, `sno2c.h`, or any frontend lower.c wired to x64

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| SNOBOL4 | crosscheck corpus | `106/106` | `test/crosscheck/run_crosscheck_asm_corpus.sh` |
| Icon | rung ladder (rungs 01–35+) | `38 rungs` | `test/frontend/icon/run_icon_x64_rung.sh` |
| Prolog | rung ladder (rungs 1–9, expanding) | per-rung PASS | `test/frontend/prolog/` (per-rung scripts) |
| Snocone | ASM corpus | `10/10` | `test/frontend/snocone/sc_asm_corpus/run_sc_asm_corpus.sh` |
| Rebus | round-trip | `3/3` | `test/rebus/run_roundtrip.sh` |

#### JVM backend — trigger when: any change to `emit_jvm.c`, `emit_jvm_*.c`, `ir.h`, `sno2c.h`, or any frontend lower.c wired to JVM

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| SNOBOL4 | crosscheck corpus | `106/106` | `test/crosscheck/run_crosscheck_jvm_rung.sh` |
| Icon | rung corpus (rungs 01–38) | `38 rung folders` | `test/frontend/icon/corpus/` (per-rung) |
| Prolog | SWI bench ladder | `31/31` | `test/frontend/prolog/run_prolog_jvm_rung.sh` |

#### .NET backend — trigger when: any change to `emit_net.c`, `ir.h`, `sno2c.h`, or any frontend lower.c wired to .NET

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| SNOBOL4 | crosscheck corpus | `110/110` | `test/crosscheck/run_crosscheck_net.sh` |

*(Icon .NET, Prolog .NET, Snocone .NET, Rebus .NET added here as M-G6 milestones deliver them)*

#### WASM backend — trigger when: any change to `emit_wasm.c`, `ir.h`, or any frontend lower.c wired to WASM

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| *(none yet — WASM scaffolded in M-G2-SCAFFOLD-WASM; suites added as M-G6 milestones deliver them)* | — | — | `builds clean` |

`snobol4dotnet` and `snobol4jvm` are separate repos with different host languages
and are not part of these invariants.

Session prefix for all reorg work: **`G`** (Grand Master). e.g. G-1, G-2, ...

---

## Milestones

### Phase 0 — Freeze and Baseline

| ID | Action | Verify |
|----|--------|--------|
| **M-G0-FREEZE** ✅ | Tag current HEAD of snobol4x as `pre-reorg-freeze` (`a051367`). Baseline recorded in `doc/BASELINE.md`. snobol4harness HEAD: `eced661`. snobol4corpus HEAD: `ccd79fa`. All concurrent development frozen. | Tag pushed; `doc/BASELINE.md` committed `716b814` |
| **M-G0-RENAME** ✅ | Confirmed: `snobol4harness` and `snobol4corpus` already use canonical marketing names in all snobol4x and .github cross-repo references. GitHub redirects from old dash-form slugs (`snobol4-harness`, `snobol4-corpus`) are live — both resolve to the same HEAD. Zero file changes required. | All references verified clean |
| **M-G0-CORPUS-AUDIT** | **Plan** the migration of corpus source programs out of `snobol4x` and into `snobol4corpus`. No files move yet — this milestone produces the migration map only. See full inventory and open decisions below. | `doc/CORPUS_MIGRATION.md` exists and all three open decisions are resolved |
| **M-G0-AUDIT** ✅ | Audit all emitter files: document every `emit_<thing>` function signature, every local variable name, every generated label pattern. Covers: `emit_byrd_asm.c`, `emit_byrd_jvm.c`, `emit_byrd_net.c`, `emit_wasm.c` (stub), `icon_emit_jvm.c`, `prolog_emit_jvm.c`, `icon_emit.c` (x64 icon), and the Prolog-x64 sections of `emit_byrd_asm.c`. Produce `doc/EMITTER_AUDIT.md`. | `doc/EMITTER_AUDIT.md` committed `252dac0` |
| **M-G0-IR-AUDIT** | Audit all six frontend IRs: list every node kind used, cross-reference to the target unified enum above. Produce `doc/IR_AUDIT.md` with a mapping table: `frontend × node_kind → unified_EKind`. | File exists |

#### M-G0-CORPUS-AUDIT — Inventory and Open Decisions

**What was found in `snobol4x/test/` (G-7 session, 2026-03-28):**

All corpus source programs currently living in `snobol4x`. None of these belong here
post-reorg — they must migrate to `snobol4corpus`.

| Location in snobol4x | Extensions | Count | Destination in snobol4corpus |
|-----------------------|-----------|-------|------------------------------|
| `test/frontend/icon/corpus/rung01–rung38/` | `.icn` | 258 | `programs/icon/rung*/` (TBD — check overlap with existing 851 files) |
| `test/frontend/prolog/corpus/rung*/` | `.pro`, `.pl` | 130 | `programs/prolog/rung*/` |
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

1. **Oracle files (`.expected` / `.ref`):** ✅ **Migrate to `snobol4corpus`** alongside
   their source programs. Source and oracle are a unit — they travel together.

2. **Runner scripts (`run_rung*.sh` etc.):** ✅ **Stay in all three compiler/runtime repos**
   (`snobol4x`, `snobol4jvm`, `snobol4dotnet`/`snobol4net`), with paths updated to point
   to `snobol4corpus`. Runners are compiler-specific test drivers, not shared infrastructure.

3. **Overlap / dedup:** ✅ **Clone `snobol4corpus` and diff first.** If a file exists in
   both repos with identical content → keep one copy in `snobol4corpus`, remove from
   `snobol4x`. If content differs → human review before any merge. No blind overwrites.

**Dedup analysis complete (G-7 session, 2026-03-28):**

`snobol4corpus` was cloned and diffed against every snobol4x corpus directory.
Result: **zero content conflicts**. Every file in `snobol4x/test/` is either
entirely absent from `snobol4corpus` or clearly distinct. No blind-overwrite risk.

| Frontend | snobol4x location | Files | In snobol4corpus? | Action |
|----------|-------------------|-------|-------------------|--------|
| Icon | `test/frontend/icon/corpus/rung01–38/` | 258 `.icn` | ❌ Not present (corpus has IPL only) | Move to `programs/icon/rung*/` |
| Prolog | `test/frontend/prolog/corpus/rung*/` | 130 `.pro/.pl` | ❌ Not present | Move to `programs/prolog/rung*/` |
| Snocone | `test/frontend/snocone/sc_asm_corpus/` | 10 `.sc` | ❌ Not present | Move to `programs/snocone/corpus/` |
| Snocone | `test/crosscheck/sc_corpus/` | 20 `.sc` | ❌ Not present | Move to `crosscheck/snocone/` |
| SNOBOL4 | `test/frontend/snobol4/*.sno` | 5 `.sno` | ❌ Not present | Move to `programs/snobol4/smoke/` |
| SNOBOL4 | `test/beauty/*/driver.sno` + subsystems | 19 `.sno` | ❌ Not present | Move to `programs/snobol4/beauty/` |
| SNOBOL4 | `test/feat/f*.sno` | 20 `.sno` | ❌ Not present | Move to `programs/snobol4/feat/` |
| SNOBOL4 | `test/jvm_j3/*.sno` | 6 `.sno` | ❌ Not present | Move to `programs/snobol4/jvm_j3/` |
| Rebus | `test/rebus/*.reb` | 3 `.reb` | ❌ Not present | Move to `programs/rebus/` |

**One file requiring human review before move:**
`snobol4corpus/programs/beauty/beauty.sno` and `snobol4x/demo/beauty.sno` have
**different MD5s** — they are divergent versions of the beauty program. Similarly
`expression.sno` differs. These are in `demo/` not `test/`, and the corpus versions
may be older. Lon must decide which is authoritative before either moves.

**All `.expected`/`.ref` oracle files travel with their source programs** (per decision 1).

**Execution order:**

| Step | Action | Verify |
|------|--------|--------|
| 1 | Move Icon corpus (258 `.icn` + oracles). One rung dir per commit to snobol4corpus; matching removal from snobol4x. | Icon invariants green after each batch |
| 2 | Move Prolog corpus (130 `.pro`/`.pl` + oracles). Same pattern. | Prolog JVM 31/31 green |
| 3 | Move Snocone corpus (30 `.sc` + oracles). | Snocone 10/10 green |
| 4 | Move SNOBOL4 test programs (beauty drivers, feat, jvm_j3, smoke — 50 `.sno` + oracles). | SNOBOL4 106/106 ASM + JVM + 110/110 NET green |
| 5 | Move Rebus corpus (3 `.reb` + oracles). | Rebus 3/3 green |
| 6 | **HOLD** — `demo/beauty.sno` vs corpus `beauty.sno` divergence. Human review. | Lon sign-off |
| 7 | Update runner script paths in `snobol4x`, `snobol4jvm`, `snobol4dotnet`/`snobol4net`. | All runners execute against `snobol4corpus` paths |
| 8 | Run full invariant suite. | All four backend invariants green |

---

### Phase 1 — Unified IR Header

| ID | Action | Verify |
|----|--------|--------|
| **M-G1-IR-HEADER-DEF** | Create `src/ir/ir.h` with the full unified `EKind` enum (all node kinds from all frontends, listed above). Do **not** include it anywhere yet. Compile it standalone: `gcc -c src/ir/ir.h` (or equivalent). Fix any exhaustive-switch warnings that would fire when new kinds are added. | `gcc -fsyntax-only src/ir/ir.h` clean; no `-Werror` violations |
| **M-G1-IR-HEADER-WIRE** | Add `#include "ir/ir.h"` to `sno2c.h`. Fix any `switch(kind)` statements that become non-exhaustive (add `default: assert(0)` where appropriate). No logic changes. | `make -j4` clean; all four backend invariants green (shared header change triggers all backends) |
| **M-G1-IR-PRINT** | Create `src/ir/ir_print.c` — a single `ir_print_node(EXPR_t *e, FILE *f)` that prints any node kind. Used for debugging all frontends uniformly. | Unit test: print a known IR, check output |
| **M-G1-IR-VERIFY** | Create `src/ir/ir_verify.c` — structural invariant checker: every node has valid `kind`, `nchildren` matches kind spec, no NULL children where not allowed. Called from driver in debug builds. | `make debug` passes verify on all corpus programs |

---

### Phase 2 — Folder Restructure (mechanical rename only)

| ID | Action | Verify |
|----|--------|--------|
| **M-G2-DIRS** | Create new directory skeleton: `src/backend/x64/`, `src/backend/jvm/`, `src/backend/net/`. (These may already exist — confirm and adjust.) | `ls src/backend/` shows all three |
| **M-G2-MOVE-ASM** | `git mv src/backend/x64/emit_byrd_asm.c src/backend/x64/emit_x64.c`. Update `#include` and `Makefile` references. No content changes. | 106/106 |
| **M-G2-MOVE-JVM** | `git mv src/backend/jvm/emit_byrd_jvm.c src/backend/jvm/emit_jvm.c`. Update references. No content changes. | 106/106 |
| **M-G2-MOVE-NET** | `git mv src/backend/net/emit_byrd_net.c src/backend/net/emit_net.c`. Update references. No content changes. | 110/110 NET |
| **M-G2-SCAFFOLD-WASM** | Create `src/backend/wasm/emit_wasm.c` — skeleton only: file header, empty `emit_wasm()` entry point, no IR handling yet. Add to Makefile. | Builds clean |
| **M-G2-MOVE-ICON-JVM** | `git mv src/frontend/icon/icon_emit_jvm.c src/backend/jvm/emit_jvm_icon.c`. Update references. No content changes. | Icon JVM corpus 99/99 |
| **M-G2-MOVE-PROLOG-JVM** | `git mv src/frontend/prolog/prolog_emit_jvm.c src/backend/jvm/emit_jvm_prolog.c`. Update references. No content changes. | Prolog JVM 20/20 |
| **M-G2-MOVE-ICON-ASM** | `git mv src/frontend/icon/icon_emit.c src/backend/x64/emit_x64_icon.c`. Update references. No content changes. | Icon ASM rung03 5/5 |
| **M-G2-MOVE-PROLOG-ASM-a** | ⚠ FILE SPLIT step 1 — create `src/backend/x64/emit_x64_prolog.c` as an empty stub and `#include` it from the **tail** of `emit_x64.c`. Prolog code still physically lives in `emit_x64.c` at this step. Add stub to Makefile if needed. | 106/106 ASM; Prolog ASM rungs 1–9 PASS; `emit_x64.c` still passes 106/106 |
| **M-G2-MOVE-PROLOG-ASM-b** | ⚠ FILE SPLIT step 2 — physically move Prolog ASM emitter code from `emit_x64.c` into `emit_x64_prolog.c`. Remove from `emit_x64.c`. The `#include` from step (a) stays. | 106/106 ASM; Prolog ASM rungs 1–9 PASS; `emit_x64.c` still passes 106/106 |

After M-G2: the file layout matches the target architecture. Every emitter sits
in the backend directory that owns it. **M-G2-MOVE-PROLOG-ASM-a/b must be last** —
they are a file split, not a rename, and carry the most risk within this phase.

---

### Phase 3 — Naming Unification (one opcode group at a time)

Each sub-milestone touches **one emitter, one opcode group only**. No cross-emitter
changes in one commit. The naming law (see above) is applied mechanically:
search-replace C variable names, rename generated label patterns, update comments.
No logic changes. Old-style names may coexist with new-style names across groups
within the same file — the file is fully conformant only after all sub-milestones
for that emitter are done.

**Rule:** after every sub-milestone, the full corpus for that backend must pass.
A regression is immediately localizable to the one opcode group just touched.

#### emit_x64.c

| ID | Opcode group | What changes | Verify |
|----|-------------|-------------|--------|
| **M-G3-NAME-X64-CORE** | `E_QLIT`, `E_CONC`, `E_OR` | Local vars → `lbl_alpha/beta/gamma/omega`; functions → `emit_x64_<Kind>` | 106/106 |
| **M-G3-NAME-X64-ITERATE** | `E_ARB`, `E_ARBNO` | Same | 106/106 |
| **M-G3-NAME-X64-CAPTURE** | `E_DOT`, `E_DOLLAR` | Same | 106/106 |
| **M-G3-NAME-X64-CURSOR** | `E_POS`, `E_RPOS` | Same | 106/106 |
| **M-G3-NAME-X64-LOAD** | `E_VART`, `E_ILIT`, `E_FLIT` | Same | 106/106 |
| **M-G3-NAME-X64-ARITH** | `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD` | Same; macros confirmed as `E()`/`EI()`/`EL()` | 106/106 |
| **M-G3-NAME-X64-ASSIGN** | `E_ASSIGN`, `E_IDX`, `E_FNC` | Same | 106/106 |
| **M-G3-NAME-X64-REMAINING** | All remaining kinds in `emit_x64.c` | Same; confirm no non-conforming names remain | 106/106 |

#### emit_jvm.c

| ID | Opcode group | What changes | Verify |
|----|-------------|-------------|--------|
| **M-G3-NAME-JVM-CORE** | `E_QLIT`, `E_CONC`, `E_OR` | `J()`/`JI()`/`JL()` confirmed; functions → `emit_jvm_<Kind>` | 106/106 |
| **M-G3-NAME-JVM-ITERATE** | `E_ARB`, `E_ARBNO` | Same | 106/106 |
| **M-G3-NAME-JVM-CAPTURE** | `E_DOT`, `E_DOLLAR` | Same | 106/106 |
| **M-G3-NAME-JVM-CURSOR** | `E_POS`, `E_RPOS` | Same | 106/106 |
| **M-G3-NAME-JVM-LOAD** | `E_VART`, `E_ILIT`, `E_FLIT` | Same | 106/106 |
| **M-G3-NAME-JVM-ARITH** | `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD` | Same | 106/106 |
| **M-G3-NAME-JVM-ASSIGN** | `E_ASSIGN`, `E_IDX`, `E_FNC` | Same | 106/106 |
| **M-G3-NAME-JVM-REMAINING** | All remaining kinds in `emit_jvm.c` | Same; confirm no non-conforming names remain | 106/106 |

#### emit_net.c

| ID | Opcode group | What changes | Verify |
|----|-------------|-------------|--------|
| **M-G3-NAME-NET-CORE** | `E_QLIT`, `E_CONC`, `E_OR` | `N()`/`NI()`/`NL()` confirmed or renamed; functions → `emit_net_<Kind>` | 110/110 NET |
| **M-G3-NAME-NET-ITERATE** | `E_ARB`, `E_ARBNO` | Same | 110/110 NET |
| **M-G3-NAME-NET-CAPTURE** | `E_DOT`, `E_DOLLAR` | Same | 110/110 NET |
| **M-G3-NAME-NET-CURSOR** | `E_POS`, `E_RPOS` | Same | 110/110 NET |
| **M-G3-NAME-NET-LOAD** | `E_VART`, `E_ILIT`, `E_FLIT` | Same | 110/110 NET |
| **M-G3-NAME-NET-ARITH** | `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD` | Same | 110/110 NET |
| **M-G3-NAME-NET-ASSIGN** | `E_ASSIGN`, `E_IDX`, `E_FNC` | Same | 110/110 NET |
| **M-G3-NAME-NET-REMAINING** | All remaining kinds in `emit_net.c` | Same; confirm no non-conforming names remain | 110/110 NET |

#### emit_wasm.c, emit_jvm_icon.c, emit_jvm_prolog.c, emit_x64_icon.c, emit_x64_prolog.c

These files are either new (WASM) or smaller/split files. A single milestone per file is
acceptable here since diffs are bounded and reviewable.

| ID | File | What changes | Verify |
|----|------|-------------|--------|
| **M-G3-NAME-WASM** | `emit_wasm.c` | Establish naming law from scratch: `W()`/`WI()`/`WL()`, `lbl_alpha/beta/gamma/omega`, `emit_wasm_<Kind>`. WASM uses `br_table` for tableswitch (maps to JVM pattern). | Builds clean |
| **M-G3-NAME-JVM-ICON** | `emit_jvm_icon.c` | `ij_emit_*` → `emit_jvm_icon_*` for Icon-specific; shared node handlers → `emit_jvm_<Kind>` | Icon JVM 99/99 |
| **M-G3-NAME-JVM-PROLOG** | `emit_jvm_prolog.c` | `pj_emit_*` → `emit_jvm_prolog_*` for Prolog-specific; shared → `emit_jvm_<Kind>` | Prolog JVM 20/20 |
| **M-G3-NAME-X64-ICON** | `emit_x64_icon.c` | `icon_emit_*` → `emit_x64_icon_*` for Icon-specific; shared → `emit_x64_<Kind>` | Icon ASM rung03 5/5 |
| **M-G3-NAME-X64-PROLOG** | `emit_x64_prolog.c` | Apply naming law to Prolog x64 emitter split out in M-G2-MOVE-PROLOG-ASM-b: `pl_emit_*` → `emit_x64_prolog_*` for Prolog-specific; shared → `emit_x64_<Kind>` | Prolog ASM rungs 1–9 PASS |

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
| **M-G4-SHARED-CONC** | `E_CONC` | Extract wiring to `ir_emit_common.c`. All three SNOBOL4 backends use it. | 106/106 ASM + JVM + NET |
| **M-G4-SHARED-OR** | `E_OR` | Same. | All |
| **M-G4-SHARED-ARBNO** | `E_ARBNO` | Same. | All |
| **M-G4-SHARED-CAPTURE** | `E_DOT`, `E_DOLLAR` | Same. | All |
| **M-G4-SHARED-ARITH** | `E_ADD/SUB/MPY/DIV/MOD` | Same. | All |
| **M-G4-SHARED-ASSIGN** | `E_ASSIGN` | Same. | All |
| **M-G4-SHARED-IDX** | `E_IDX` | Same. | All |
| **M-G4-SHARED-ICON-TO** | `E_TO`, `E_TO_BY` | Extract Icon generator wiring shared between `emit_x64_icon.c` and `emit_jvm_icon.c`. | Icon ASM + JVM |
| **M-G4-SHARED-ICON-SUSPEND** | `E_SUSPEND` | Same. Suspend/resume wiring isolated from other generators. | Icon ASM + JVM |
| **M-G4-SHARED-ICON-ALT** | `E_ALT_GEN` | Same. | Icon ASM + JVM |
| **M-G4-SHARED-ICON-BANG** | `E_BANG`, `E_SCAN` | Same. SCAN involves subject save/restore — verify both backends independently. | Icon ASM + JVM |
| **M-G4-SHARED-ICON-LIMIT** | `E_LIMIT` | Same. | Icon ASM + JVM |
| **M-G4-SHARED-PROLOG-UNIFY** | `E_UNIFY` | Extract Prolog unification wiring shared between ASM and JVM. | Prolog ASM + JVM |
| **M-G4-SHARED-PROLOG-CLAUSE** | `E_CLAUSE`, `E_CHOICE` | Same. Head-matching and predicate dispatch wiring. | Prolog ASM + JVM |
| **M-G4-SHARED-PROLOG-CUT** | `E_CUT` | Same. FENCE/cut sealing logic. | Prolog ASM + JVM |
| **M-G4-SHARED-PROLOG-TRAIL** | `E_TRAIL_MARK`, `E_TRAIL_UNWIND` | Same. Trail save/restore is the most backend-sensitive Prolog operation — isolated last. | Prolog ASM + JVM |

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
| **M-G5-LOWER-ICON-FIX** | icon | For each gap: add kind or wire explicit bridge. One commit per gap. | Icon ASM rung03 5/5 after each gap |
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
| **M-G6-SNOCONE-WASM** | Snocone → WASM | M-G5-LOWER-SNOCONE + M-G6-SNOBOL4-WASM | Snocone WASM rung01 PASS |
| **M-G6-REBUS-JVM** | Rebus → JVM | M-G5-LOWER-REBUS | Rebus JVM PASS |
| **M-G6-REBUS-NET** | Rebus → .NET | M-G5-LOWER-REBUS | Rebus NET PASS |
| **M-G6-REBUS-WASM** | Rebus → WASM | M-G5-LOWER-REBUS + M-G6-SNOBOL4-WASM | Rebus WASM rung01 PASS |
| **M-G6-SNOBOL4-WASM** | SNOBOL4 → WASM | M-G4-SHARED-ASSIGN + M-G2-SCAFFOLD-WASM | hello.sno → .wat → wasmtime PASS |
| **M-G6-ICON-WASM** | Icon → WASM | M-G4-SHARED-ICON-LIMIT + M-G5-LOWER-ICON | Icon WASM rung01 PASS |
| **M-G6-PROLOG-WASM** | Prolog → WASM | M-G4-SHARED-PROLOG-TRAIL + M-G5-LOWER-PROLOG | Prolog WASM rung01 PASS |
| **M-G6-SCRIP-X64** | Scrip → x64 ASM | M-G5-LOWER-SCRIP-FIX | Scrip ASM rung01 PASS |
| **M-G6-SCRIP-JVM** | Scrip → JVM | M-G5-LOWER-SCRIP-FIX | Scrip JVM rung01 PASS |
| **M-G6-SCRIP-NET** | Scrip → .NET | M-G5-LOWER-SCRIP-FIX | Scrip NET rung01 PASS |
| **M-G6-SCRIP-WASM** | Scrip → WASM | M-G5-LOWER-SCRIP-FIX + M-G6-SNOBOL4-WASM | Scrip WASM rung01 PASS |

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
                                                                    └── M-G3-NAME-X64-* (×8, sequential)
                                                                    └── M-G3-NAME-JVM-* (×8, sequential)
                                                                    └── M-G3-NAME-NET-* (×8, sequential)
                                                                    └── M-G3-NAME-WASM / JVM-ICON / JVM-PROLOG / X64-ICON / X64-PROLOG
                                                                            └── M-G4-SHARED-CONC/OR/ARBNO/CAPTURE/ARITH/ASSIGN/IDX (sequential)
                                                                                    └── M-G4-SHARED-ICON-TO → SUSPEND → ALT → BANG → LIMIT (sequential)
                                                                                    └── M-G4-SHARED-PROLOG-UNIFY → CLAUSE → CUT → TRAIL (sequential)
                                                                                            └── M-G5-LOWER-*-AUDIT → M-G5-LOWER-*-FIX (×6, one per frontend, sequential)
                                                                                                    └── M-G6-* (×10, parallel)
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

## PLAN.md Changes Required

### NOW Table — add at top, above all frozen rows

```
| **GRAND MASTER REORG** | G-0 — M-G0-FREEZE ❌ NEXT | pre-reorg-freeze | M-G0-AUDIT |
```

### Freeze annotation — add `[FROZEN]` suffix to every other NOW row

```
| **TINY backend** | [FROZEN B-292 `acbc71e`] | — | resume post-reorg |
| **TINY NET**     | [FROZEN N-248 `425921a`] | — | resume post-reorg |
| **TINY JVM**     | [FROZEN J-216 `a74ccd8`] | — | resume post-reorg |
...etc
```

### Milestone Dashboard — add new section

```markdown
### Grand Master Reorganization — Active

| ID | Phase | Status |
|----|-------|--------|
| M-G0-FREEZE             | 0 — Baseline  | ❌ NEXT |
| M-G0-AUDIT              | 0 — Baseline  | ❌ |
| M-G0-IR-AUDIT           | 0 — Baseline  | ❌ |
| M-G1-IR-HEADER-DEF      | 1 — IR        | ❌ |
| M-G1-IR-HEADER-WIRE     | 1 — IR        | ❌ |
| M-G1-IR-PRINT           | 1 — IR        | ❌ |
| M-G1-IR-VERIFY          | 1 — IR        | ❌ |
| M-G2-DIRS               | 2 — Folders   | ❌ |
| M-G2-MOVE-* (×7)        | 2 — Folders   | ❌ |
| M-G2-MOVE-PROLOG-ASM-a  | 2 — Folders   | ❌ |
| M-G2-MOVE-PROLOG-ASM-b  | 2 — Folders   | ❌ |
| M-G3-NAME-X64-* (×8)    | 3 — Names     | ❌ |
| M-G3-NAME-JVM-* (×8)    | 3 — Names     | ❌ |
| M-G3-NAME-NET-* (×8)    | 3 — Names     | ❌ |
| M-G3-NAME-WASM/ICON/PRO/X64-PRO (×5) | 3 — Names | ❌ |
| M-G4-SHARED-CONC/OR/ARBNO/CAPTURE/ARITH/ASSIGN/IDX (×7) | 4 — Wiring | ❌ |
| M-G4-SHARED-ICON-* (×5) | 4 — Wiring    | ❌ |
| M-G4-SHARED-PROLOG-* (×4) | 4 — Wiring  | ❌ |
| M-G5-LOWER-*-AUDIT (×6) | 5 — Frontends (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) | ❌ |
| M-G5-LOWER-*-FIX (×6)   | 5 — Frontends | ❌ |
| M-G6-* (×15)            | 6 — Matrix (6 frontends × 4 backends, minus already-done SNOBOL4 x64/JVM/NET) | ❌ |
| M-G7-UNFREEZE           | 7 — Style     | ❌ |
| M-G8-HOME               | 8 — GenTest: where does enumerator live? | ❌ |
| M-G8-DEPTH              | 8 — GenTest: token-count vs IR-node depth bound? | ❌ |
| M-G8-ORACLE             | 8 — GenTest: differential vs reference-cache oracle? | ❌ |
| M-G8-GRAMMAR            | 8 — GenTest: first language + fragment + BNF | ❌ |
| M-G8-ENUM-CORE          | 8 — GenTest: enumerate.py core | ❌ |
| M-G8-EMIT-SNO           | 8 — GenTest: IR tree → .sno serializer | ❌ |
| M-G8-RUNNER             | 8 — GenTest: full pipeline + Monitor hook | ❌ |
| M-G8-SNOBOL4-N10        | 8 — GenTest: SNOBOL4 pattern N=10 clean | ❌ |
| M-G8-SNOBOL4-N25        | 8 — GenTest: SNOBOL4 pattern N=25 clean | ❌ |
| M-G8-ICON-N25           | 8 — GenTest: Icon generators N=25 clean | ❌ |
| M-G8-PROLOG-N25         | 8 — GenTest: Prolog clause bodies N=25 clean | ❌ |
| M-G8-CI                 | 8 — GenTest: N=10 slice wired into CI | ❌ |
| M-G9-RENAME-NET-PLAN    | 9 — snobol4dotnet→snobol4net: impact checklist | ❌ |
| M-G9-RENAME-NET-EXEC    | 9 — snobol4dotnet→snobol4net: GitHub repo rename | ❌ |
| M-G9-RENAME-NET-REFS    | 9 — snobol4dotnet→snobol4net: update all cross-repo refs | ❌ |
| M-G9-RENAME-NET-VERIFY  | 9 — snobol4dotnet→snobol4net: 1903/1903 PASS | ❌ |
```

---

### Phase 8 — Grammar-Driven Exhaustive Test Generation

The reorg creates a unified IR whose node kinds are exactly the productions of a
formal grammar over each frontend language. Phase 8 exploits that structure to build
a depth-bounded exhaustive enumerator: every syntactically valid program from 0 to
N tokens (target: N = 25) is compiled through all backends, run against the oracle,
and on any divergence the Monitor drills to the exact first diverging trace event.

This replaces the current ad-hoc approach (hand-written corpus + `Expressions.py`
random arithmetic fuzzing) with a **structural** approach: bugs in cases nobody
thought to write a test for are found automatically by exhausting the grammar.

The unified IR from Phase 1 is the enabling prerequisite: the enumerator walks
IR-node trees directly — no source parsing needed — which makes it frontend-language-
independent. A new grammar spec per frontend maps grammar productions to IR node
kinds. The enumerator is shared across all languages.

---

#### Design Decisions — Four Milestones Before Any Code

| ID | Decision | Action | Deliverable |
|----|----------|--------|-------------|
| **M-G8-HOME** | Where does the enumerator live? | Evaluate `snobol4harness` (cross-repo test infra, already hosts probe/monitor) vs new `snobol4gen` repo (cleaner separation). Decide and document. | `doc/GEN_HOME.md` — one-page decision record: chosen location, rationale, how other repos reference it |
| **M-G8-DEPTH** | Token-count or IR-node depth as the bound? | Token-count is user-intuitive ("programs up to 20 tokens"). IR-node depth is uniform across languages (depth-5 tree has the same combinatorial budget in every grammar). Evaluate both for SNOBOL4 pattern fragment: how many programs does each generate at N=10, N=20, N=25? Is the count tractable? | `doc/GEN_DEPTH.md` — table: language × bound-type × N → program count. Chosen primary bound documented. |
| **M-G8-ORACLE** | How is expected output determined for generated programs? | Option A: differential (CSNOBOL4 + SPITBOL agree → that is correct; any snobol4x backend that disagrees → bug). Option B: reference cache (run CSNOBOL4 once per generated program, store `.ref`). Evaluate: is differential sufficient, or do we need cached refs for regression detection after a fix? | `doc/GEN_ORACLE.md` — decision record: chosen strategy, how divergences are reported, what "PASS" means for a generated test |
| **M-G8-GRAMMAR** | What is the Phase-1 grammar scope? | Which language first and what fragment? Candidates: (a) SNOBOL4 pattern expressions — richest, most bug-prone, maps directly to E_QLIT/E_CONC/E_OR/E_ARBNO/E_DOT/E_DOLLAR/E_VART (7 node kinds); (b) Icon generator expressions — E_TO/E_TO_BY/E_SUSPEND/E_ALT_GEN/E_BANG/E_LIMIT (6 kinds, `Expressions.py` already seeds this); (c) Prolog clause bodies — E_UNIFY/E_CLAUSE/E_CHOICE/E_CUT (4 kinds, simpler). Evaluate coverage ROI vs implementation effort. | `doc/GEN_GRAMMAR.md` — chosen first language and fragment, BNF of the fragment, mapping from each production to its IR node kind(s), estimated program count at N=25 |

All four `doc/GEN_*.md` files must exist and be consistent before any enumerator
code is written. They are the spec. Disagreement between team members → resolve in
the doc, not in code.

---

#### Implementation Milestones

| ID | Action | Prerequisite | Verify |
|----|--------|-------------|--------|
| **M-G8-ENUM-CORE** | Implement `gen/enumerate.py` — depth-bounded IR-tree enumerator. Takes a grammar spec (dict of node-kind → children rules) and a depth bound. Yields `EXPR_t`-compatible tree objects. No serialization yet. | M-G8-GRAMMAR | Unit test: SNOBOL4 pattern fragment, depth=3 → exact expected count matches `doc/GEN_DEPTH.md` table |
| **M-G8-EMIT-SNO** | Implement `gen/emit_sno.py` — serializes an IR tree to a one-statement `.sno` file: fixed subject string, pattern match, OUTPUT of captures. | M-G8-ENUM-CORE | 10 hand-verified generated `.sno` files compile and run correctly under CSNOBOL4 |
| **M-G8-RUNNER** | Implement `gen/run_gen.py` — pipeline: enumerate → emit `.sno` → compile all backends → differential check (CSNOBOL4 vs each snobol4x backend) → on divergence: invoke Monitor → report first diverging event. | M-G8-EMIT-SNO + M-G8-ORACLE | 100 generated SNOBOL4 pattern programs, depth ≤ 4, all PASS or divergences reported with Monitor drill-down |
| **M-G8-SNOBOL4-N10** | Run SNOBOL4 pattern fragment, depth bound N=10. All divergences found → Monitor drill-down → fix emitter → re-run → clean. | M-G8-RUNNER | Zero divergences at N=10 across all three snobol4x backends |
| **M-G8-SNOBOL4-N25** | Extend to N=25. | M-G8-SNOBOL4-N10 | Zero divergences at N=25 |
| **M-G8-ICON-GRAMMAR** | Write grammar spec for Icon generator expressions (BNF + IR node mapping). Extend `gen/emit_sno.py` for `.icn` serialization. | M-G8-SNOBOL4-N25 | `doc/GEN_GRAMMAR.md` updated; 10 hand-verified `.icn` files correct |
| **M-G8-ICON-N25** | Run Icon generator fragment, N=25, all three backends. | M-G8-ICON-GRAMMAR | Zero divergences at N=25 |
| **M-G8-PROLOG-GRAMMAR** | Write grammar spec for Prolog clause bodies (BNF + IR node mapping). Extend for `.pro` serialization. | M-G8-ICON-N25 | `doc/GEN_GRAMMAR.md` updated; 10 hand-verified `.pro` files correct |
| **M-G8-PROLOG-N25** | Run Prolog clause body fragment, N=25, all three backends. | M-G8-PROLOG-GRAMMAR | Zero divergences at N=25 |
| **M-G8-CI** | Wire the enumerator into CI: on every commit to `snobol4x`, run the N=10 slice for all three languages. N=25 run on demand (too slow for every commit). | M-G8-PROLOG-N25 | CI green; N=10 run completes in < 5 minutes |

---

#### How Monitor Integration Works

For any generated program where a backend diverges, the existing 5-way sync-step
Monitor is invoked directly. No new Monitor infrastructure is needed — the enumerator
simply calls `run_monitor.sh` on the diverging `.sno` file:

```
enumerate_programs(language='snobol4', max_depth=25)
  for each program:
    compile: asm, jvm, net
    run csnobol4 → oracle output
    for each backend:
      if backend output != oracle output:
        run_monitor.sh(program)   ← existing tool, no changes needed
        report: first diverging TRACE event
        stop this program
```

The enumerator is a **test discovery engine**. The Monitor is the **drill-down engine**.
They compose without modification.

---

#### Why IR-Tree Enumeration Is Better Than Source Fuzzing

The existing `test/backend/c/Expressions.py` generates random arithmetic expressions
as *source text*, which then gets parsed. This has two weaknesses:

1. The parser is in the loop — parser bugs mask emitter bugs and vice versa.
2. Random sampling misses systematic gaps: if alternation-of-concatenations is never
   randomly generated, that class of bug is never found.

IR-tree enumeration bypasses the parser entirely — trees are emitted directly into
the backend's emit functions. Parser and emitter bugs are tested independently.
Exhaustive enumeration guarantees coverage of every tree shape up to the depth bound.

After Phase 1 (unified `ir.h`), all six frontends lower to the same `EXPR_t` tree.
The enumerator works on that tree type — it tests all backends for all languages
with one shared tool.

---

- No bug fixes. Known bugs (L_io_end, @N, puzzle_03 over-generation) are deferred.
- No new features. M-BEAUTIFY-BOOTSTRAP, M-T2-FULL, M-NET-POLISH all deferred.
- No behavior changes of any kind.
- The runtime libraries (`src/runtime/`) are untouched.
- The test corpus (`test/`) is untouched — it is the ground truth throughout.
- `snobol4dotnet` (pending rename to `snobol4net`) and `snobol4jvm` are separate repos
  written in different host languages (C# and Clojure respectively). They are not
  restructured here. They participate only via the pipeline matrix documentation update
  in PLAN.md and the corpus migration (M-G0-CORPUS-AUDIT).

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
8. The `snobol4x` pipeline matrix (6 frontends × 4 backends = 24 cells) has at least one ✅ or ⏳ in every cell that was previously `—` but is now reachable via shared backend infrastructure. (`snobol4net` and `snobol4jvm` are separate repos with their own roadmaps and are excluded from this criterion.)

The full project testing transformation is complete (M-G8-CI fires) when:

9. Four design-decision docs exist: `doc/GEN_HOME.md`, `doc/GEN_DEPTH.md`,
   `doc/GEN_ORACLE.md`, `doc/GEN_GRAMMAR.md` — all consistent, all agreed.
10. `gen/enumerate.py` enumerates IR trees for SNOBOL4, Icon, and Prolog grammar
    fragments up to depth N=25.
11. Zero divergences between oracle and all three snobol4x backends at N=25 for
    all three language fragments.
12. The N=10 slice runs in CI on every commit to snobol4x in under 5 minutes.

---

### Phase 9 — Repo Rename: snobol4dotnet → snobol4net

Executed **after** M-G7-UNFREEZE. Purely administrative — no code changes.
Prerequisite: all concurrent sessions have resumed and are stable post-reorg.

| ID | Action | Verify |
|----|--------|--------|
| **M-G9-RENAME-NET-PLAN** | Confirm impact: update all cross-repo references in `snobol4x`, `snobol4jvm`, `.github`, `snobol4harness`, `snobol4corpus` that mention `snobol4dotnet`. Produce checklist. | Checklist exists; no stale refs after rename |
| **M-G9-RENAME-NET-EXEC** | Rename GitHub repo `snobol4ever/snobol4dotnet` → `snobol4ever/snobol4net`. GitHub creates redirect from old name automatically. Update RENAME.md name grid. | `git ls-remote github.com/snobol4ever/snobol4net` resolves; old name redirects |
| **M-G9-RENAME-NET-REFS** | Update every cross-repo reference found in M-G9-RENAME-NET-PLAN: `.github` docs, `snobol4x` runner scripts, `snobol4harness` adapters. One repo per commit. | All references resolve; no broken links |
| **M-G9-RENAME-NET-VERIFY** | Run `snobol4net` full test suite (`1903/1903` DOTNET invariant). Confirm nothing broke. | 1903/1903 PASS |

---

*GRAND_MASTER_REORG.md — living document.*
*Completed G-milestone rows → MILESTONE_ARCHIVE.md per standard protocol.*
*All concurrent development frozen until M-G7-UNFREEZE.*
