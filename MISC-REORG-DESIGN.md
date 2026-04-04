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
*Extended G-9 s22 to cover full similarity-maximization goal.*

---

#### The Goal: Similarity Maximization

Every variable, function, generated label, local, global, parameter, and
comment that represents **the same concept** must use **the same root name**
across every emitter file and every frontend. The source files should look
almost identical except for the parts that are uniquely specific to a
language's syntax/semantics or a platform's code model.

Differences that are **permitted** (they represent genuinely different things):
- Language-specific semantic distinctions (Icon suspension vs SNOBOL4 cursors)
- Platform code-model distinctions (JVM stack vs x86 registers)
- Backend output-macro letter (`E`/`J`/`N`/`W`) — same concept, different letter because they must be distinct in a multi-backend translation unit

Differences that are **forbidden** (they represent the same concept):
- `jvm_out` vs `net_out` vs `jout` vs `out` — all mean "the output file"
- `jvm_classname` vs `ij_classname` vs `pj_classname` vs `net_classname` — all mean "the output class name"
- `jvm_nvar` vs `net_nvar` vs `nvar` — all mean "number of registered variables"
- `jvm_vars` vs `net_vars` vs `vars` — all mean "the variable registry"
- `uid_ctr`/`next_uid` vs `ij_node_id`/`ij_new_id` vs `pj_label_counter`/`pj_fresh_label` — all mean "the unique-id counter and allocator"
- `jvm_cur_fn` vs `net_cur_fn` vs `cur_fn` — all mean "the current function being emitted"
- `jvm_cur_stmt_fail_label` vs `net_cur_stmt_fail_label` — same concept
- `jvm_classname` init function vs `ij_set_classname` vs `pj_set_classname` vs `net_set_classname` — same concept
- `icn_N_α`/`icn_N_β` (JVM Icon) vs `icon_N_α`/`icon_N_β` (x86 Icon) — same concept, different prefix spelling
- `pj_` prefix inside JVM Prolog vs no prefix in x64 Prolog — same things, different naming regime

**The test:** If you could diff two emitter files and the only differences were
the output macro letter and the platform-specific code sequences, the naming
law is satisfied. Any diff line that differs *only in a name prefix or suffix*
where both sides represent the same concept is a violation.

---

#### Naming partitions — the classes

Variables are partitioned into **root-name equivalence classes** by concept.
Within a single compiland (`emit_<backend>_<frontend>.c`), the root is
morphed with a consistent prefix/suffix for subclassing (e.g. `cur_` for
"currently active", `_count` for a count, `_reset` for a reset function).
The morphing rules are uniform across all files.

**Class 1 — Byrd-box ports (THE key example)**

The four-port Byrd-box model is the central concept. The port names are used
**identically everywhere** — C source, parameters, local variables, generated
labels, and comments. No file-local variation is permitted.

| Port | Root | C param/local | Generated label suffix | Meaning |
|------|------|--------------|------------------------|---------|
| α | `α` | `α` | `_α` | Fresh entry |
| β | `β` | `β` | `_β` | Resume after downstream failure |
| γ | `γ` | `γ` | `_γ` | Success exit (passed in) |
| ω | `ω` | `ω` | `_ω` | Failure exit (passed in) |

Greek letters are used **everywhere**: parameters, locals, struct fields,
label literals, comments. No ASCII spelling-out (`alpha`, `beta`, `gamma`,
`omega`) anywhere. The Greek letter IS the name. The Byrd-box is universal
across all six frontends and all four backends — the name must be too.

**Class 2 — Generated labels for α/β ports**

| Backend | Alpha entry label | Beta resume label | Notes |
|---------|-------------------|-------------------|-------|
| x86 | `P_<id>_α` | `P_<id>_β` | γ/ω are caller-supplied jumps |
| JVM | `L<id>_α` | `L<id>_β` | id = unique integer per node |
| .NET | `L<id>_α` | `L<id>_β` | same scheme as JVM |

Frontend-qualified node labels use the frontend prefix before the id:
`sno_<id>_α`, `icn_<id>_α`, `pl_<id>_α` — prefix identifies the frontend,
`_α`/`_β` suffix identifies the port. **All files use this exact scheme.**
No `icon_` vs `icn_` inconsistency. No `pj_` vs `pl_` inconsistency.

| Frontend | Label prefix | Example α label |
|----------|-------------|-----------------|
| SNOBOL4 | `sno_` | `sno_<id>_α` |
| Icon | `icn_` | `icn_<id>_α` |
| Prolog | `pl_` | `pl_<id>_α` |
| Snocone | `sc_` | `sc_<id>_α` |
| Rebus | `reb_` | `reb_<id>_α` |

**Class 3 — Emitter module globals (same root, backend-letter morphing only)**

Every emitter file has the same set of module-level globals. The root name
is fixed. Within a multi-frontend backend file (not yet the case but future-proof),
a `<frontend>_` prefix is added. Within a single-frontend file the root
stands alone (or with the single backend prefix if two backends are compiled
together).

| Concept | Root | x86/SNOBOL4 | JVM/SNOBOL4 | .NET/SNOBOL4 | JVM/Icon | JVM/Prolog |
|---------|------|-------------|-------------|--------------|----------|------------|
| Output file pointer | `out` | `out` | `out` | `out` | `out` | `out` |
| Class/module name | `classname` | *(n/a — x86 has no classname)* | `classname` | `classname` | `classname` | `classname` |
| Variable registry | `vars` | `vars` | `vars` | `vars` | *(n/a)* | *(n/a)* |
| Variable count | `nvar` | `nvar` | `nvar` | `nvar` | *(n/a)* | *(n/a)* |
| Node UID counter | `uid` | `uid` | `uid` | `uid` | `uid` | `uid` |
| UID allocator | `next_uid()` | `next_uid()` | `next_uid()` | `next_uid()` | `next_uid()` | `next_uid()` |
| Current function def | `cur_fn` | `cur_fn` | `cur_fn` | `cur_fn` | *(n/a)* | *(n/a — prog root used)* |
| Stmt fail label | `cur_stmt_fail` | `cur_stmt_fail` | `cur_stmt_fail` | `cur_stmt_fail` | *(n/a)* | *(n/a)* |
| Fn return label | `fn_return` | `fn_return` | `fn_return` | `fn_return` | *(n/a)* | *(n/a)* |
| Fn fail-return label | `fn_freturn` | `fn_freturn` | `fn_freturn` | `fn_freturn` | *(n/a)* | *(n/a)* |
| Program root | `prog` | `prog` | `prog` | `prog` | `prog` | `prog` |
| Set-classname fn | `set_classname()` | *(n/a)* | `set_classname()` | `set_classname()` | `set_classname()` | `set_classname()` |
| Fn table | `fn_table` | `fn_table` | `fn_table` | `fn_table` | *(n/a)* | *(n/a)* |
| Fn table count | `fn_count` | `fn_count` | `fn_count` | `fn_count` | *(n/a)* | *(n/a)* |

**Morphing rule for file-scoped disambiguation:** When two emitter `.c` files
are compiled into the same translation unit, each global gets the backend prefix
(`jvm_`, `net_`, `x64_`, `wasm_`) to avoid link-time collision. In standalone
files (current architecture — one TU per backend+frontend), no prefix is needed:
`out`, `uid`, `cur_fn`, etc. stand unadorned. **The current architecture is
standalone files; no prefix is needed now.** Remove existing spurious prefixes
(`jvm_out` → `out`, `net_out` → `out`, `jout` → `out`, etc.) as part of the
M-G3-NAME-* passes.

**Class 4 — Emit-function signatures**

All emit functions for IR nodes follow the same signature pattern:

```c
static void emit_<kind>(EXPR_t *node, const char *γ, const char *ω)
```

- `node` — the IR node being emitted (always `node`)
- `γ` — success continuation label (always `γ`)
- `ω` — failure continuation label (always `ω`)
- Return type always `void`
- Local α/β label strings declared as `char α[LBUF]`, `char β[LBUF]`

No `ports` structs, no `IjPorts`, no `IcnPorts` — γ and ω are plain `const char *`
parameters, consistent with `emit_x64.c` (the oracle). Existing `IjPorts` /
`IcnPorts` structs in `emit_jvm_icon.c` / `emit_x64_icon.c` are replaced with
plain `const char *γ, const char *ω` parameters in the M-G3-NAME-JVM-ICON /
M-G3-NAME-X64-ICON passes.

**Class 5 — Output macros (backend-letter subclassing)**

Output macros share identical semantics; the letter is the only difference
(required for multi-backend TU safety):

| Backend file | Raw output | Instruction | Labelled instruction | Comment | Separator |
|---|---|---|---|---|---|
| `emit_x64.c` | `E(fmt,...)` | `EI(op,ops)` | `EL(lbl,op,ops)` | `EC(txt)` | `ESep(tag)` |
| `emit_jvm.c` | `J(fmt,...)` | `JI(op,ops)` | `JL(lbl,op,ops)` | `JC(txt)` | `JSep(tag)` |
| `emit_net.c` | `N(fmt,...)` | `NI(op,ops)` | `NL(lbl,op,ops)` | `NC(txt)` | `NSep(tag)` |
| `emit_wasm.c` | `W(fmt,...)` | `WI(op,ops)` | `WL(lbl,op,ops)` | `WC(txt)` | `WSep(tag)` |
| `emit_jvm_icon.c` | `J(fmt,...)` | `JI(op,ops)` | `JL(lbl)` *(label-only)* | `JC(txt)` | — |
| `emit_jvm_prolog.c` | `J(fmt,...)` | `JI(op,ops)` | `JL(lbl,op,ops)` | `JC(txt)` | `JSep(tag)` |
| `emit_x64_icon.c` | `E(fmt,...)` via `em->out` | `EI`/`Ldef`/`Jmp` | — | — | — |
| `emit_x64_prolog.c` | `A(fmt,...)` | — | — | — | — |

**Law:** All frontend-specific emitters within the same backend family use the
same output macro letter as the SNOBOL4 oracle for that backend. `emit_jvm_icon.c`
uses `J`. `emit_x64_icon.c` uses `E` (or a thin wrapper that calls `fprintf(em->out,…)`
which is equivalent). `emit_x64_prolog.c` uses `A` — this is a legacy name;
the M-G3-NAME-X64-PROLOG pass renames it to `E` (via the `IcnEmitter` struct
approach or direct `out` global, whichever is cleaner).

**Class 6 — IR node locals**

Inside any `emit_<kind>` function:

| Local | Root | Meaning |
|-------|------|---------|
| `node` | `node` | current IR node |
| `left` | `left` | `node->children[0]` |
| `right` | `right` | `node->children[1]` |
| `id` | `id` | unique integer id for this node's labels |
| `α` | `α` | char buf for α label string, `char α[LBUF]` |
| `β` | `β` | char buf for β label string, `char β[LBUF]` |

No `char a[64]`, no `char b[64]`. These are `α` and `β`. No `lα`, `lβ`.

**Class 7 — Generated runtime symbols (same across all backends)**

| Concept | Symbol root | x86 form | JVM/NET form |
|---------|------------|----------|--------------|
| SNOBOL4 variable X | `sno_var_` | `sno_var_X` (bss label) | `sno_var_X` (static field) |
| Subject string | `sno_subject` | `sno_subject` | `sno_subject` |
| Cursor position | `sno_cursor` | `sno_cursor` | `sno_cursor` |
| Subject length | `sno_sublen` | `sno_sublen` | `sno_sublen` |
| Keyword STLIMIT | `sno_kw_STLIMIT` | `sno_kw_STLIMIT` | `sno_kw_STLIMIT` |
| Keyword STCOUNT | `sno_kw_STCOUNT` | `sno_kw_STCOUNT` | `sno_kw_STCOUNT` |
| Icon failed flag | `icn_failed` | `icn_failed` | `icn_failed` |
| Icon suspended flag | `icn_suspended` | `icn_suspended` | `icn_suspended` |
| Icon return value | `icn_retval` | `icn_retval` | `icn_retval` |
| Prolog trail top | `pl_trail_top` | `pl_trail_top` | `pl_trail_top` |

**Class 8 — Function-scope intermediate labels**

Intermediate labels within a single emit function that do not map to α/β ports
follow this pattern: `<frontend>_<id>_<role>` where `<role>` is a short
descriptive word. The frontend prefix must match Class 2 (i.e. `sno_`, `icn_`,
`pl_`). No file-local pseudo-prefixes like `Jfn`, `Nfn`, `jvm_fn`, `pj_` in
the generated output. Generated function-body labels:

| Concept | Pattern | Example |
|---------|---------|---------|
| Fn return label | `<fe>_fn<id>_return` | `sno_fn3_return` |
| Fn fail-return label | `<fe>_fn<id>_freturn` | `sno_fn3_freturn` |
| Stmt-local fail label | `<fe>_<id>_fail` | `sno_42_fail` |
| Loop top | `<fe>_<id>_loop` | `icn_7_loop` |
| Loop done | `<fe>_<id>_done` | `icn_7_done` |
| Conditional mid | `<fe>_<id>_mid` | `sno_12_mid` |

**Class 9 — Function registration tables (same root, no prefix)**

| Concept | Root name |
|---------|-----------|
| Fn definition struct type | `FnDef` |
| Fn table array | `fn_table` |
| Fn table count | `fn_count` |
| Current fn pointer | `cur_fn` |
| Find fn by name | `find_fn()` |

JVM had `JvmFnDef`/`jvm_fn_table`/`jvm_fn_count`/`jvm_cur_fn`/`jvm_find_fn`.
NET had `NetFnDef`/`net_fn_table`/`net_fn_count`/`net_cur_fn`/`net_find_fn`.
Both become `FnDef`/`fn_table`/`fn_count`/`cur_fn`/`find_fn` — same concept,
same name, no spurious prefix (files are standalone TUs; no collision risk).

---

#### Pre-existing law additions (unchanged)

**`ICN_OUT(em, fmt, ...)` — M-G0-SIL-NAMES:**
Write macro for `emit_x64_icon.c`. Distinct from `E(fmt,...)` only where both
files share a TU. In the current standalone architecture this can be unified
to `E` in M-G3-NAME-X64-ICON.

**EKind alias bridges — M-G0-SIL-NAMES:**
`scrip-cc.h` `#define` aliases for old→canonical names. Removed in Phase 5.

**`stmt_` prefix — runtime C shim functions:**
`stmt_init`, `stmt_get`, `stmt_set`, etc. Scopes x86 runtime shim functions.
Not an emitter concept — unchanged.

**`_fn` suffix — engine-level SIL-derived names:**
`VARVAL_fn`, `STRCONCAT_fn`, etc. Unchanged.

---

#### Summary: what changes in M-G3-NAME-* passes

Every M-G3-NAME-* pass is a **full-file similarity pass**, not just function
prefix renames. For each file the pass must:

1. **Globals:** rename to Class 3 roots (strip spurious `jvm_`/`net_`/`ij_`/`pj_` prefixes)
2. **Function names:** rename to `emit_<file-prefix>_<kind>` pattern; helper functions use Class 9 roots
3. **Local variables:** rename `char a[64]`→`char α[LBUF]`, `char b[64]`→`char β[LBUF]`, ports struct fields → plain `γ`/`ω` params
4. **Generated labels:** ensure Class 2 and Class 8 patterns (frontend prefix + `_α`/`_β`)
5. **Comments:** no ASCII port spellings (`alpha`/`beta`/`gamma`/`omega` → `α`/`β`/`γ`/`ω`)

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

