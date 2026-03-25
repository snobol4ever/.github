# GRAND MASTER REORGANIZATION — snobol4ever
*2026-03-25 — authored by Claude Sonnet 4.6 in consultation with the project record*

---

## The Problem

The project has grown organically into a matrix of 5–6 frontends × 3 backends.
Each pipeline was built when it was needed, with naming, folder structure, and IR
conventions that were right-for-the-moment. The result is structural debt:

- **Five separate IRs** (or near-IRs): SNOBOL4's `EXPR_t/EKind`, Icon's `IcnNode`,
  Prolog's `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*`, Snocone's lowered form,
  Rebus's AST. Each frontend invented its own node vocabulary.
- **Emitters are not parallel.** `emit_byrd_asm.c` (6937 lines) is the oracle.
  `emit_byrd_jvm.c` (4479 lines) mirrors it for SNOBOL4 only. `emit_byrd_net.c`
  (2669 lines) mirrors it for SNOBOL4 only. `icon_emit_jvm.c` (3308 lines) is
  Icon-only. `prolog_emit_jvm.c` (2676 lines) is Prolog-only. No frontend other
  than SNOBOL4 has all three backends.
- **Naming is inconsistent.** Greek letters, label prefixes, local variable names,
  and generated-code symbol conventions differ across emitters and frontends.
- **Folder structure reflects history, not architecture.** Prolog and Icon JVM
  emitters live under `src/frontend/`, not `src/backend/`.

The goal of the Grand Master Reorganization is to impose a single clean architecture:

```
5 (or 6) frontends → ONE shared IR → 3 shared backends
```

Every frontend lowers to the same IR. Every backend consumes that same IR.
The 15 (or 18) pipelines become consistent by construction.

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
      scripten/       lex.c  parse.c  lower.c   → IR  [future]
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
    runtime/
      asm/            (unchanged)
      jvm/            (unchanged)
      net/            (unchanged)
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

This convention applies **identically** in all five emitters and all six frontends.
Every generated label, every C variable, every comment uses these names.
No exceptions. No aliases. No abbreviations beyond those listed here.

**Greek ports — source code (C variables and comments):**

| Port | C name | Meaning |
|------|--------|---------|
| α | `lbl_alpha` | Fresh entry |
| β | `lbl_beta` | Resume after downstream failure |
| γ | `lbl_gamma` | Success exit |
| ω | `lbl_omega` | Failure exit |

**Greek ports — generated labels (in .asm / .j / .il output):**

| Backend | Alpha label | Beta label | Notes |
|---------|-------------|------------|-------|
| x64 ASM | `P_<id>_alpha:` | `P_<id>_beta:` | gamma/omega are caller-supplied jumps |
| JVM | `L<id>_alpha` | `L<id>_beta` | id = unique integer per node |
| .NET | `L<id>_alpha` | `L<id>_beta` | same scheme as JVM |

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
| Alpha label string | `lbl_alpha` |
| Beta label string | `lbl_beta` |
| Gamma label string (passed in) | `lbl_gamma` |
| Omega label string (passed in) | `lbl_omega` |
| Emit function signature | `emit_<kind>(EXPR_t *node, const char *lbl_gamma, const char *lbl_omega)` |
| Output file | `out` (all backends) |
| Output macro | `E(fmt, ...)` (x64) · `J(fmt, ...)` (JVM) · `N(fmt, ...)` (.NET) |
| Instruction emit helper | `EI(instr, ops)` · `JI(instr, ops)` · `NI(instr, ops)` |
| Label definition helper | `EL(label, instr, ops)` · `JL(...)` · `NL(...)` |

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
entirely. The test suite (`106/106` ASM corpus + `1903/1903` DOTNET) must be green
at the end of every milestone. Any regression → rollback, diagnose, fix before continuing.

Session prefix for all reorg work: **`G`** (Grand Master). e.g. G-1, G-2, ...

---

## Milestones

### Phase 0 — Freeze and Baseline

| ID | Action | Verify |
|----|--------|--------|
| **M-G0-FREEZE** | Tag current HEAD of snobol4x as `pre-reorg-freeze`. Record 106/106 ASM corpus, DOTNET 1903/1903. | `git tag pre-reorg-freeze && git push --tags` |
| **M-G0-AUDIT** | Audit all five emitters: document every `emit_<thing>` function signature, every local variable name, every generated label pattern. Produce `doc/EMITTER_AUDIT.md`. | File exists, covers all 5 emitters |
| **M-G0-IR-AUDIT** | Audit all five frontend IRs: list every node kind used, cross-reference to the target unified enum above. Produce `doc/IR_AUDIT.md` with a mapping table: `frontend × node_kind → unified_EKind`. | File exists |

---

### Phase 1 — Unified IR Header

| ID | Action | Verify |
|----|--------|--------|
| **M-G1-IR-HEADER** | Create `src/ir/ir.h` with the full unified `EKind` enum (all node kinds from all frontends, listed above). Keep `sno2c.h` intact — add `#include "ir/ir.h"` at top. All existing code still compiles. | `make -j4` clean; 106/106 |
| **M-G1-IR-PRINT** | Create `src/ir/ir_print.c` — a single `ir_print_node(EXPR_t *e, FILE *f)` that prints any node kind. Used for debugging all frontends uniformly. | Unit test: print a known IR, check output |
| **M-G1-IR-VERIFY** | Create `src/ir/ir_verify.c` — structural invariant checker: every node has valid `kind`, `nchildren` matches kind spec, no NULL children where not allowed. Called from driver in debug builds. | `make debug` passes verify on all corpus programs |

---

### Phase 2 — Folder Restructure (mechanical rename only)

| ID | Action | Verify |
|----|--------|--------|
| **M-G2-DIRS** | Create new directory skeleton: `src/backend/x64/`, `src/backend/jvm/`, `src/backend/net/`. (These may already exist — confirm and adjust.) | `ls src/backend/` shows all three |
| **M-G2-MOVE-ASM** | `git mv src/backend/x64/emit_byrd_asm.c src/backend/x64/emit_x64.c`. Update `#include` and `Makefile` references. No content changes. | 106/106 |
| **M-G2-MOVE-JVM** | `git mv src/backend/jvm/emit_byrd_jvm.c src/backend/jvm/emit_jvm.c`. Update references. No content changes. | 106/106 |
| **M-G2-MOVE-NET** | `git mv src/backend/net/emit_byrd_net.c src/backend/net/emit_net.c`. Update references. No content changes. | DOTNET 1903/1903 |
| **M-G2-MOVE-ICON-JVM** | `git mv src/frontend/icon/icon_emit_jvm.c src/backend/jvm/emit_jvm_icon.c`. Update references. No content changes. | Icon JVM corpus 99/99 |
| **M-G2-MOVE-PROLOG-JVM** | `git mv src/frontend/prolog/prolog_emit_jvm.c src/backend/jvm/emit_jvm_prolog.c`. Update references. No content changes. | Prolog JVM 20/20 |
| **M-G2-MOVE-ICON-ASM** | `git mv src/frontend/icon/icon_emit.c src/backend/x64/emit_x64_icon.c`. Update references. No content changes. | Icon ASM rung03 5/5 |
| **M-G2-MOVE-PROLOG-ASM** | ⚠ FILE SPLIT — not a `git mv`. The Prolog ASM emitter is currently embedded in the tail of `emit_x64.c`. Extract it into `src/backend/x64/emit_x64_prolog.c`. Either `#include` it from `emit_x64.c` or add as a separate compilation unit in the Makefile. Do this last within Phase 2 — all clean `git mv` moves above must be verified green first. | Prolog ASM rungs 1–9 PASS |

After M-G2: the file layout matches the target architecture. Every emitter sits
in the backend directory that owns it. **M-G2-MOVE-PROLOG-ASM must be last** —
it is a file split, not a rename, and carries the most risk within this phase.

---

### Phase 3 — Naming Unification (one emitter at a time)

Each sub-milestone touches **one emitter only**. No cross-emitter changes in one commit.
The naming law (see above) is applied mechanically: search-replace C variable names,
rename generated label patterns, update comments. No logic changes.

| ID | File | What changes | Verify |
|----|------|-------------|--------|
| **M-G3-NAME-X64** | `emit_x64.c` | Local variables → `lbl_alpha/beta/gamma/omega`; macros confirmed as `E()`/`EI()`/`EL()`; functions → `emit_x64_<Kind>` | 106/106 |
| **M-G3-NAME-JVM** | `emit_jvm.c` | Same; `J()`/`JI()`/`JL()` confirmed; functions → `emit_jvm_<Kind>` | 106/106 |
| **M-G3-NAME-NET** | `emit_net.c` | Same; `N()`/`NI()`/`NL()` confirmed or renamed; functions → `emit_net_<Kind>` | DOTNET 1903/1903 |
| **M-G3-NAME-JVM-ICON** | `emit_jvm_icon.c` | `ij_emit_*` → `emit_jvm_icon_*` for Icon-specific; shared node handlers → `emit_jvm_<Kind>` | Icon JVM 99/99 |
| **M-G3-NAME-JVM-PROLOG** | `emit_jvm_prolog.c` | `pj_emit_*` → `emit_jvm_prolog_*` for Prolog-specific; shared → `emit_jvm_<Kind>` | Prolog JVM 20/20 |
| **M-G3-NAME-X64-ICON** | `emit_x64_icon.c` | `icon_emit_*` → `emit_x64_icon_*` for Icon-specific; shared → `emit_x64_<Kind>` | Icon ASM rung03 5/5 |

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
| **M-G4-SHARED-ICON** | `E_TO`, `E_TO_BY`, `E_SUSPEND`, `E_ALT_GEN`, `E_BANG`, `E_LIMIT`, `E_SCAN` | Extract Icon wiring shared between `emit_x64_icon.c` and `emit_jvm_icon.c`. | Icon ASM + JVM |
| **M-G4-SHARED-PROLOG** | `E_UNIFY`, `E_CLAUSE`, `E_CHOICE`, `E_CUT`, `E_TRAIL_*` | Extract Prolog wiring shared between ASM and JVM. | Prolog ASM + JVM |

---

### Phase 5 — Frontend Lower-to-IR Unification

Each frontend's `lower.c` must produce only canonical `EXPR_t` nodes from the
unified `ir.h` enum. Any frontend-local node types that duplicate an existing
shared kind are replaced.

| ID | Frontend | Action | Verify |
|----|----------|--------|--------|
| **M-G5-LOWER-SNOBOL4** | snobol4 | Audit `parse.c` / `lower.c` — confirm all output nodes are in unified enum. Document any gaps. | 106/106 |
| **M-G5-LOWER-SNOCONE** | snocone | Same audit. Lower → unified IR. | Snocone corpus PASS |
| **M-G5-LOWER-ICON** | icon | `IcnNode` kinds mapped to unified enum or kept as typed frontend extension with explicit bridge. | Icon ASM rung03 5/5 |
| **M-G5-LOWER-PROLOG** | prolog | `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*` already in unified enum (Phase 1). Confirm. | Prolog JVM 20/20 |
| **M-G5-LOWER-REBUS** | rebus | Audit `rebus_emit.c` — map Rebus AST nodes to unified enum. | Rebus corpus PASS |

---

### Phase 6 — Cross-Matrix Coverage (new pipelines, now cheap)

With unified IR and three shared backends, adding a new frontend×backend pipeline
is: wire the frontend's `lower.c` output into the backend's `emit_*.c`.
No new emitter code for shared node kinds. Priority order:

| ID | Pipeline | Prerequisite | Verify |
|----|----------|-------------|--------|
| **M-G6-ICON-NET** | Icon → .NET | M-G4-SHARED-ICON + M-G5-LOWER-ICON | Icon NET rung01 PASS |
| **M-G6-PROLOG-NET** | Prolog → .NET | M-G4-SHARED-PROLOG + M-G5-LOWER-PROLOG | Prolog NET rung01 PASS |
| **M-G6-SNOCONE-JVM** | Snocone → JVM | M-G5-LOWER-SNOCONE | Snocone JVM corpus PASS |
| **M-G6-SNOCONE-NET** | Snocone → .NET | M-G5-LOWER-SNOCONE | Snocone NET corpus PASS |
| **M-G6-REBUS-JVM** | Rebus → JVM | M-G5-LOWER-REBUS | Rebus JVM PASS |
| **M-G6-REBUS-NET** | Rebus → .NET | M-G5-LOWER-REBUS | Rebus NET PASS |
| **M-G6-SCRIPTEN-ALL** | Scripten → all 3 | M-G5 complete | Scripten rung01 all 3 PASS |

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
| **M-G7-UNFREEZE** | Lift concurrent-development freeze. Update PLAN.md: resume all session rows from their pre-reorg HEADs. Tag `post-reorg-baseline`. | 106/106; 1903/1903; all frontend corpus PASS |

---

## Dependency Graph

```
M-G0-FREEZE
    ├── M-G0-AUDIT
    └── M-G0-IR-AUDIT
            └── M-G1-IR-HEADER
                    ├── M-G1-IR-PRINT
                    └── M-G1-IR-VERIFY
                            └── M-G2-DIRS
                                    └── M-G2-MOVE-* (×7, sequential)
                                            └── M-G3-NAME-* (×6, sequential)
                                                    └── M-G4-SHARED-* (×9, sequential)
                                                            └── M-G5-LOWER-* (×5, sequential)
                                                                    └── M-G6-* (×7, parallel)
                                                                            └── M-G7-STYLE-DOC
                                                                                    └── M-G7-STYLE-*
                                                                                            └── M-G7-UNFREEZE
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
| M-G0-FREEZE       | 0 — Baseline  | ❌ NEXT |
| M-G0-AUDIT        | 0 — Baseline  | ❌ |
| M-G0-IR-AUDIT     | 0 — Baseline  | ❌ |
| M-G1-IR-HEADER    | 1 — IR        | ❌ |
| M-G1-IR-PRINT     | 1 — IR        | ❌ |
| M-G1-IR-VERIFY    | 1 — IR        | ❌ |
| M-G2-DIRS         | 2 — Folders   | ❌ |
| M-G2-MOVE-* (×7)  | 2 — Folders   | ❌ |
| M-G3-NAME-* (×6)  | 3 — Names     | ❌ |
| M-G4-SHARED-* (×9)| 4 — Wiring    | ❌ |
| M-G5-LOWER-* (×5) | 5 — Frontends | ❌ |
| M-G6-* (×7)       | 6 — Matrix    | ❌ |
| M-G7-UNFREEZE     | 7 — Style     | ❌ |
```

---

## What Does NOT Change During Reorg

- No bug fixes. Known bugs (L_io_end, @N, puzzle_03 over-generation) are deferred.
- No new features. M-BEAUTIFY-BOOTSTRAP, M-T2-FULL, M-NET-POLISH all deferred.
- No behavior changes of any kind.
- The runtime libraries (`src/runtime/`) are untouched.
- The test corpus (`test/`) is untouched — it is the ground truth throughout.
- `snobol4dotnet` is a separate repo and is not restructured here. It participates
  only via the 4D matrix documentation update.

---

## Success Criteria

The Grand Master Reorg is complete (M-G7-UNFREEZE fires) when:

1. `src/` has the folder structure shown above, exactly.
2. All emitter files follow the naming law — no deviations.
3. `src/ir/ir.h` contains the unified `EKind` enum covering all frontends.
4. No node kind is defined in more than one header.
5. The Byrd box wiring logic for every shared node kind lives in exactly one place.
6. Every corpus test that passed before the reorg still passes.
7. `doc/STYLE.md` exists and all source files conform to it.
8. The 4D matrix in PLAN.md has at least one ✅ or ⏳ in every cell that was
   previously `—` but is now reachable via shared backend infrastructure.

---

*GRAND_MASTER_REORG.md — living document.*
*Completed G-milestone rows → MILESTONE_ARCHIVE.md per standard protocol.*
*All concurrent development frozen until M-G7-UNFREEZE.*
