# ARCH-reorg-design.md — Grand Master Reorg: Architecture & Design Reference
*Split from GRAND_MASTER_REORG.md (G-8 session, 2026-03-29) — stable reference, rarely changes.*
*See GRAND_MASTER_REORG.md for milestone tables and active tracking.*

---
## The Problem

The project is a matrix of **6 frontends × 4 active backends**, housed across three
compiler/runtime product repos:

| Repo | Role | Language | Notes |
|------|------|----------|-------|
| `one4all` | Compiler/runtime — 2D matrix | C | 6 frontends × 4 active backends |
| `snobol4jvm` | Compiler/runtime | Clojure | SNOBOL4/SPITBOL → JVM only |
| `snobol4dotnet` → `snobol4net` | Compiler/runtime | C# | SNOBOL4/SPITBOL → .NET only; rename pending (M-G9) |
| `harness` | Test infrastructure | Shell/Python | Corpus runner, adapter scripts, probe/monitor |
| `corpus` | Test data | SNOBOL4/Icon/Prolog | Canonical crosscheck corpus used by all backends |
| `snobol4python` | Pattern library | Python | Out of scope for this reorg |
| `snobol4csharp` | Pattern library | C# | Out of scope for this reorg |

`snobol4jvm` and `snobol4dotnet` are single-frontend/single-backend repos in different
host languages; they are **not restructured here**.

`harness` and `corpus` are infrastructure repos. They are **not
structurally reorganized** but their rename (to the canonical `harness` /
`corpus` marketing names, per RENAME.md) is part of the reorg scope and
is executed in **M-G0-RENAME** below.

`one4all` is the 2D matrix repo — the only one that is, or will be, multi-frontend
and multi-backend. `snobol4jvm` and `snobol4dotnet` are single-frontend/single-backend
repos written in different host languages; they are **not restructured here**.

A fifth backend, **C** (`scrip-cc`), exists in `one4all` but is effectively dead — it
produces C output that is not actively maintained or tested. It is **excluded from
the reorg** (not moved, not renamed, not wired to shared IR). Its presence is noted
here only to prevent confusion with the active backends.

Each pipeline in `one4all` was built when it was needed, with naming, folder
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
across `one4all`:

```
6 frontends → ONE shared IR → 4 active backends (x86, JVM, .NET, WASM)
```

Every frontend lowers to the same IR. Every backend consumes that same IR.
The 24 pipelines (6 × 4) become consistent by construction.

---

## Target Architecture

### Folder Structure (post-reorg)

```
one4all/
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
      c/              ← DEAD — scrip-cc C backend, not maintained, excluded from reorg
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

**Byrd box node kinds — canonical names (all backends must handle all of these):**

*`E_` prefix = Expression node. Names derived from SIL `xxxTYP` token type codes
(CSNOBOL4 v311.sil) where applicable. See `ARCH-sil-heritage.md` for full lineage.*

| Kind | Meaning | α | β |
|------|---------|---|---|
| **Literals** | | | |
| `E_QLIT` | String / pattern literal (`QLITYP` in SIL) | load/match value | — |
| `E_ILIT` | Integer literal (`ILITYP` in SIL) | load value | — |
| `E_FLIT` | Float/real literal (`FLITYP` in SIL) | load value | — |
| `E_CSET` | Cset literal (Icon/Rebus) | load cset value | — |
| `E_NUL` | Null / empty value | load null | — |
| **References** | | | |
| `E_VAR` | Variable reference (`VARTYP=3` in SIL; T = Type code discriminant) | load binding | — |
| `E_KW` | `&IDENT` keyword reference (`K=10` data type in SIL) | load keyword value | — |
| `E_INDR` | `$expr` indirect / immediate-assign target | resolve indirection | — |
| `E_DEFER` | `*expr` deferred / indirect pattern reference (`XSTAR=32` in SIL) | load deferred pattern | — |
| **Arithmetic** | | | |
| `E_NEG` | Unary minus (`MNSM/MNSR` procs in SIL) | negate | — |
| `E_PLS` | Unary plus — coerces `''` to 0 (`PLS` proc in SIL; distinct op, not identity) | coerce to numeric | — |
| `E_ADD` | Addition | evaluate | — |
| `E_SUB` | Subtraction | evaluate | — |
| `E_MPY` | Multiplication | evaluate | — |
| `E_DIV` | Division | evaluate | — |
| `E_MOD` | Modulo / remainder | evaluate | — |
| `E_POW` | Exponentiation (`EXR` in SIL; `E_EXPOP` in scrip-cc.h) | evaluate | — |
| **Sequence and Alternation** | | | |
| `E_SEQ` | Sequence / concatenation, n-ary (`CONCAT`/`CONCL` in SIL; was `E_CONC`) | left then right | right-ω → left-β |
| `E_ALT` | SNOBOL4 pattern alternation, n-ary (`ORPP` in SIL; was `E_OR`) | try left | left-ω → try right |
| `E_OPSYN` | `&` operator: reduce(left, right) | evaluate | — |
| **Pattern Primitives** | | | |
| `E_ARB` | Arbitrary match (`XFARB=17`/`XEARBNO` in SIL; `p$arb`) | try 0 chars | advance one, retry |
| `E_ARBNO` | Zero-or-more (`XARBN=3`/`p$arb`; also: every/while/repeat via lowering) | try zero | undo last match |
| `E_POS` | Cursor position assert `POS(n)` (`XPOSI=24` in SIL) | check cursor == n | fail |
| `E_RPOS` | Right cursor assert `RPOS(n)` (`XRPSI=25` in SIL) | check cursor == len-n | fail |
| `E_ANY` | `ANY(S)` — match one char from cset S (`p$any`) | match one | fail |
| `E_NOTANY` | `NOTANY(S)` — match one char not in S | match one | fail |
| `E_SPAN` | `SPAN(S)` — match longest run of chars from S (`p$spn`) | match run | fail |
| `E_BREAK` | `BREAK(S)` — match up to char in S (`p$brk`) | match up-to | fail |
| `E_BREAKX` | `BREAKX(S)` — BREAK with backtrack past delimiter (`p$bkx`) | match up-to | advance past, retry |
| `E_LEN` | `LEN(N)` — match exactly N chars (`p$len`) | match N | fail |
| `E_TAB` | `TAB(N)` — match to cursor pos N (`p$tab`) | advance to N | fail |
| `E_RTAB` | `RTAB(N)` — match to N from right (`p$rtb`) | advance to len-N | fail |
| `E_REM` | `REM` — match remainder of subject (`p$rem`) | match rest | fail |
| `E_FAIL` | `FAIL` — always fail (`p$fal`; α and β both → ω) | fail | fail |
| `E_SUCCEED` | `SUCCEED` — always succeed (`p$suc`) | succeed | succeed |
| `E_FENCE` | `FENCE` — succeed then seal β (`XFNCE=35`; no backtrack past) | succeed | abort |
| `E_ABORT` | `ABORT` — abort entire match immediately | abort | — |
| `E_BAL` | `BAL` — match balanced parentheses (`p$bal`) | match balanced | fail |
| **Captures** | | | |
| `E_CAPT_COND` | `.` conditional capture (`E_NAM` in scrip-cc.h) | match, save on success | pass β to child |
| `E_CAPT_IMM` | `$` immediate capture (`E_DOL` in scrip-cc.h) | match, save immediately | pass β to child |
| `E_CAPT_CUR` | `@var` cursor position capture (`XATP=4` in SIL; `E_ATP` in scrip-cc.h) | capture cursor | — |
| **Call, Access, Assignment** | | | |
| `E_FNC` | Function call / goal / builtin, n-ary (`FNCTYP=5` in SIL) | call | — |
| `E_IDX` | Array / table / record subscript (`ARYTYP=7` in SIL; absorbs `E_ARY`) | aref | — |
| `E_ASSIGN` | Assignment (`ASGN` proc in SIL; `E_ASGN` in scrip-cc.h) | evaluate RHS, assign | — |
| **Scan and Swap** | | | |
| `E_MATCH` | `E ? E` scanning (`XSCON=30`/`SCONCL` in SIL) | set subject | restore subject |
| `E_SWAP` | `:=:` swap bindings (`SWAP` proc in SIL) | swap | — |
| **Icon Generators** | | | |
| `E_SUSPEND` | Generator suspend / yield | yield value | resume |
| `E_TO` | `i to j` generator | emit i | increment, retry |
| `E_TO_BY` | `i to j by k` generator | emit i | step by k, retry |
| `E_LIMIT` | `E \ N` limitation | count down | fail at 0 |
| `E_GENALT` | Icon / Rebus alt generator — emit left exhausted then right (was `E_ALT_GEN`) | emit left | left-done → emit right |
| `E_ITER` | `!E` iterate list or string elements | emit first | next element |
| **Icon / Rebus Constructors** | | | |
| `E_MAKELIST` | `[e1,e2,...]` list constructor | evaluate all, build list | — |
| **Prolog** | | | |
| `E_UNIFY` | Prolog unification `=/2` | bind with trail | unwind trail, fail |
| `E_CLAUSE` | Prolog Horn clause | try head | retry next |
| `E_CHOICE` | Prolog predicate choice point | α of first clause | β chain |
| `E_CUT` | Prolog `!` cut / FENCE (`XFNCE=35` in SIL) | seal β | unreachable |
| `E_TRAIL_MARK` | Save trail top into env slot | mark | — |
| `E_TRAIL_UNWIND` | Restore trail to saved mark | unwind | — |

**59 node kinds total** (45 + 14 pattern primitives that each have distinct Byrd box wiring in `emit_byrd_asm.c`).

**Rename bridge — old scrip-cc.h names → canonical ir.h names:**

| Old name | Canonical name | Note |
|----------|---------------|------|
| `E_VART` | `E_VAR` | T was SIL type-code artifact |
| `E_NULV` | `E_NUL` | Null value |
| `E_STAR` | `E_DEFER` | `*X` deferred pattern — names the operation |
| `E_MNS` | `E_NEG` | Unary minus |
| *(new)* | `E_PLS` | Unary plus — affirmation, coerces `''→0` |
| `E_EXPOP` | `E_POW` | Exponentiation |
| `E_CONC` | `E_SEQ` | Sequence |
| `E_OR` | `E_ALT` | Alternation |
| `E_NAM` | `E_CAPT_COND` | `.` conditional capture |
| `E_DOL` | `E_CAPT_IMM` | `$` immediate capture |
| `E_ATP` | `E_CAPT_CUR` | `@` cursor capture |
| `E_ARY` | `E_IDX` | Merged — same node |
| `E_ASGN` | `E_ASSIGN` | Assignment |
| `E_ALT_GEN` | `E_GENALT` | Generator alternation |
| `E_SCAN` | `E_MATCH` | Pattern match / scanning |
| `E_BANG` | `E_ITER` | Iterate elements |

During Phase 1 (M-G1-IR-HEADER-WIRE), `scrip-cc.h` gets `#define` aliases so
existing code compiles without change. The aliases are removed in Phase 3.

| Source construct | Lowers to | Rationale |
|-----------------|-----------|-----------|
| `every E do body` | `E_ARBNO(E_SEQ(E, body))` | ARBNO wiring covers it |
| `while E do body` | `E_ARBNO(E_SEQ(E, body))` | Same |
| `until E do body` | `E_ARBNO(E_SEQ(E_ALT(fail,E), body))` | Composable |
| `repeat body` | `E_ARBNO(body)` | Same |
| `if E then A else B` | `E_ALT(E_SEQ(E,A), B)` | ALT wiring |
| `unless E then body` | `E_ALT(E_SEQ(E_CUT,fail), body)` | FENCE pattern |
| `E1 ; E2` (seq expr) | `E_SEQ(E1, E2)` | Sequencing IS SEQ |
| `E1 & E2` (conjunction) | `E_SEQ(E1, E2)` | Conjunction IS sequencing |
| `{ s1; s2; ... }` (compound) | `E_SEQ(s1, E_SEQ(s2, ...))` | Same |
| `x op:= e` (augmented assign) | `E_ASSIGN(x, E_op(x, e))` | Composable |
| `for i from a to b` | `E_SEQ(E_ASSIGN(i,a), E_ARBNO(...))` | Composable |
| `E.field` (field access) | `E_IDX(E, E_QLIT("field"))` | Named subscript |
| `E[i:j]` (substring) | `E_FNC("sub", E, i, j)` | Builtin call |
| `E \|\|\| F` (list concat) | `E_FNC("lconcat", E, F)` | Builtin call |
| All comparisons (LT,GE,SEQ...) | `E_FNC("LT",2)` etc. | Builtin calls |
| `*E` (size), `?E` (random), `===` | `E_FNC(...)` | Builtin calls |
| `not E`, `\E`, `/E` | `E_FNC(...)` | Builtin calls |
| Cset ops (`++`,`--`,`**`,`~`) | `E_FNC(...)` | Builtin calls |
| `return/fail/break/next` | γ/ω routing at stmt level | Not IR nodes |
| `proc/record/global/initial` | Program/STMT_t level | Not EKind |

### IR Node Set — Living Target

**The 44-node set above is the best current analysis, not a frozen contract.**

The unification work itself — Phases 3 through 5 — is the real test. When the
emitters are actually being merged and the backends are consuming the same IR,
the code will tell us things the analysis cannot. Expect the set to change:

**Nodes may be added** when a lowering that looked clean on paper fights back
in code. If `E_ARBNO(E_SEQ(E, body))` for `every` turns out to require
β-wiring that differs subtly from plain ARBNO (e.g. because the body's ω
behavior is different than a pattern's ω), that warrants a new node. The
emitter will make this obvious.

**Nodes may be removed** when two nodes that looked distinct turn out to share
identical emitter code across all four backends. If the generated output for
node A and node B is always the same modulo a constant, they should merge.

**Some lowering combinations may prove wrong.** The `if/else → E_ALT(E_SEQ)`
lowering, the `unless → E_CUT FENCE` lowering, and the goal-directed comparison
`→ E_FNC` decisions are analysis-time best guesses. The CISC/RISC tension is
real: a CISC approach would give each construct its own node (clean frontend
lowering, complex backend); a RISC approach pushes complexity into the lowering
layer (complex frontend, clean backend). The right balance is found empirically
during Phases 3–5, not theoretically in advance.

**Protocol for IR changes during the reorg:**

| Change type | Who decides | How |
|-------------|-------------|-----|
| Add a node | Lon — after emitter evidence shows lowering fails | Add to `ir.h`, update all four backends, re-run invariants |
| Remove a node | Lon — after evidence shows two nodes always emit identically | Merge in `ir.h`, update frontends that used removed node |
| Rename a node | Lon — for clarity | Phase 3 naming pass; alias bridging in `scrip-cc.h` |
| Split a node | Lon — if β behavior diverges by context | Same as add |

**The 45 nodes are the starting point. The reorg execution produces the final answer.**

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
| x86 | `P_<id>_α:` | `P_<id>_β:` | γ/ω are caller-supplied jumps |
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

**Output macro — law addition (M-G0-SIL-NAMES):**

`ICN_OUT(em, fmt, ...)` — write macro for `icon_emit.c` (Icon x64 backend).
Distinct from `E(fmt, ...)` (SNOBOL4/x64 instruction output). The distinction
is necessary because both files may be compiled together after Phase 2
restructuring. `ICN_OUT` is the law; do not use bare `E()` in `icon_emit.c`.

**EKind alias bridges — law addition (M-G0-SIL-NAMES):**

During Phase 1 (M-G1-IR-HEADER-WIRE), `scrip-cc.h` receives `#define` aliases
mapping old names to canonical `ir.h` names (e.g. `#define E_VART E_VAR`).
These aliases exist only for compilation compatibility. They are removed
in Phase 5 when all frontends are updated to use canonical names.

**`stmt_` prefix — runtime C shim functions (confirmed law):**

`stmt_init`, `stmt_get`, `stmt_set`, `stmt_concat`, `stmt_any_ptr`, etc.
The `stmt_` prefix scopes all C runtime shim functions called from x86
macros. Not to be confused with SIL's `STMT` (statement number field). Do
not use `stmt_` for any non-shim function.

**`_fn` suffix — engine-level SIL-derived function names (confirmed law):**

`VARVAL_fn`, `STRCONCAT_fn`, `NV_GET_fn`, etc. The `_fn` suffix appended to
SIL procedure names avoids clashes with SNOBOL4 source-language identifiers.
All engine-level functions derived from SIL proc names use this suffix.

---

**Concurrent development continues normally until Lon gives the word to begin execution.**
When execution is scheduled, all sessions will be paused for the duration of the reorg.
Until then, every session row in PLAN.md remains active and unblocked.

When execution begins: the reorg is **purely mechanical** at each step — no new features,
no bug fixes, no behavior changes. If a step introduces a regression, it is reverted
entirely. The test suite must be green at the end of every milestone. Any regression → rollback, diagnose, fix before continuing.

### Invariant Table

Each milestone's Verify column references the **minimum set of backend invariants
its change can affect**. A change to a shared file (e.g. `ir.h`, `scrip-cc.h`,
`emit_x64.c`) triggers all four backends. A change scoped to one backend's emitter
triggers only that backend. A change to one frontend's `lower.c` triggers only the
backends that frontend is wired to.

**Rule:** never declare a milestone done until every backend invariant it touches
is green. If a backend has no runner yet (WASM), "builds clean" is the gate.

**⚠ NAMING NOTE (2026-03-28):** The native backend was originally called "ASM" or
"x64 ASM" — imprecise. Canonical name is now **x86** everywhere. The emitter file
will be `emit_x64.c` (folder name stays `backend/x64/`) but the backend is referred
to as "x86" in all docs, PLAN.md, session summaries, and invariant reports.
Physical file renames happen in Phase 2 (M-G2-MOVE-ASM).

**Invariant format — always report all three active backends:**
`x86 106/106 · JVM 106/106 · .NET 110/110`
Never report only one backend. If a backend cannot be run in the current
environment, mark it with its last known good count and note why.

#### x86 backend — trigger when: any change to `emit_x64.c`, `emit_x64_*.c`, `ir.h`, `scrip-cc.h`, or any frontend lower.c wired to x64

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| SNOBOL4 | crosscheck corpus | `106/106` | `test/crosscheck/run_crosscheck_asm_corpus.sh` |
| Icon | rung ladder (rungs 01–35+) | `38 rungs` | `test/frontend/icon/run_icon_x64_rung.sh` |
| Prolog | rung ladder (rungs 1–9, expanding) | per-rung PASS | `test/frontend/prolog/` (per-rung scripts) |
| Snocone | x86 corpus | `10/10` | `test/frontend/snocone/sc_asm_corpus/run_sc_asm_corpus.sh` |
| Rebus | round-trip | `3/3` | `test/rebus/run_roundtrip.sh` |

#### JVM backend — trigger when: any change to `emit_jvm.c`, `emit_jvm_*.c`, `ir.h`, `scrip-cc.h`, or any frontend lower.c wired to JVM

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| SNOBOL4 | crosscheck corpus | `106/106` | `test/crosscheck/run_crosscheck_jvm_rung.sh` |
| Icon | rung corpus (rungs 01–38) | `38 rung folders` | `test/frontend/icon/corpus/` (per-rung) |
| Prolog | SWI bench ladder | `31/31` | `test/frontend/prolog/run_prolog_jvm_rung.sh` |

#### .NET backend — trigger when: any change to `emit_net.c`, `ir.h`, `scrip-cc.h`, or any frontend lower.c wired to .NET

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| SNOBOL4 | crosscheck corpus | `110/110` | `test/crosscheck/run_crosscheck_net.sh` |

*(Icon .NET, Prolog .NET, Snocone .NET, Rebus .NET added here as M-G6 milestones deliver them)*

#### WASM backend — trigger when: any change to `emit_wasm.c`, `ir.h`, or any frontend lower.c wired to WASM

| Frontend | Suite | Count | Runner |
|----------|-------|-------|--------|
| *(none yet — WASM scaffolded in M-G2-SCAFFOLD-Wx86; suites added as M-G6 milestones deliver them)* | — | — | `builds clean` |

`snobol4dotnet` and `snobol4jvm` are separate repos with different host languages
and are not part of these invariants.

Session prefix for all reorg work: **`G`** (Grand Master). e.g. G-1, G-2, ...

---

