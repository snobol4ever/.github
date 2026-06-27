# GOAL-SCRIP-BOOTSTRAP.md — SCRIP self-hosts everywhere

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP (primary), snobol4dotnet, snobol4jvm, snobol4js (new),
snobol4wasm (new)

**Done when:** SCRIP — the compiler / interpreter / runtime currently
written as **~50,400 lines of hand-written C and headers** plus
~18,900 lines of Bison/Flex generated code (which vanishes on port)
in `SCRIP/src/` — re-emits itself in the SCRIP language family
(SNOBOL4, Snocone, Icon, Prolog, Raku, Rebus) such that:

1. **Stage-1:** the existing C-based `scrip` binary compiles the
   SCRIP-language sources and runs them. Output of those rewritten
   sources, when fed `beauty.sno < beauty.sno`, is byte-identical
   to today's md5 `abfd19a7a834484a96e824851caee159` (646 lines).
2. **Stage-2:** the SCRIP-language sources, run by Stage-1, compile
   themselves end-to-end. Stage-2 output equals Stage-1 output —
   empty diff, the bootstrap fixed point.
3. **Backend grid closed:** the SCRIP-language sources run on every
   backend in PLAN.md's milestone-3 grid (C/x86-64, JVM, .NET, WASM,
   JS) with byte-identical beauty self-host output on each.

This is **PLAN.md Milestone 2** (compiler / interpreter / runtime
self-hosting on x86-64) and **PLAN.md Milestone 3** (everywhere) — the
two remaining authorship-agreement milestones, expressed as one
ladder.

**Cross-pollination:** every fix to a SCRIP-language source benefits
all six frontends and all five backends downstream. The existing
GOAL-LANG-* ladders feed parts; this Goal integrates them.

---

## Why this Goal exists

The session-#61 win — `--run`, `--run`, `--run` all
byte-identical to SPITBOL on `beauty.sno < beauty.sno` — closed
**Milestone 1**. SCRIP's SNOBOL4 frontend self-hosts a SNOBOL4
program. But SCRIP itself is still C; the meta-circular loop is
not yet closed.

Two paths forward exist after Milestone 1:

- **Path A** — extend the SNOBOL4 work language-by-language on the
  existing x86-64 backend (close GOAL-LANG-ICON, GOAL-LANG-PROLOG,
  GOAL-LANG-RAKU, GOAL-LANG-SNOCONE, GOAL-LANG-REBUS one at a time
  on the C runtime).
- **Path B** — write SCRIP **in** the languages it implements, so
  the compiler/interpreter/runtime stops being C and starts being
  SCRIP. Once that is true on x86-64, porting to JVM / .NET / JS /
  WASM is a backend exercise, not a re-implementation.

**This Goal is Path B.** It does not block Path A — Path A's
deliverables (rung ladders for each frontend) feed into this Goal
as runtime-completeness gates. Path B turns SCRIP from "a C
program that hosts six languages" into "six languages, one of
which happens to be SCRIP".

A third realization emerged session #62 while sizing the port
surface: the Byrd-box runtime (`bb_*.c`, ~4,200 LoC) and the SM
opcode handlers are **doubly duplicated** today — once across
execution modes (IR-interp, SM-interp, JIT, and AOT text-gen),
once across host platforms (x86 asm, JS, MSIL, JVM bytecode,
WASM).  Hand-maintaining both axes is what made SN-32c possible:
session #60's fix to `sm_interp.c` SM_STORE_VAR did not propagate
to `sm_codegen.c h_store_var`, so the JIT was broken for an
entire session before session #61 caught it.  Multiplying that
risk by five backends without a deterministic generator would
turn every runtime bug fix into a 20-place edit.  See the **BB
template** section below for the design point that addresses
this — one canonical template per primitive, generated emissions
for each (mode, backend) cell, the in-process `--monitor`
extended as the cell-cross verifier.

---

## Architecture (target end-state)

```
                          SCRIP source
                          (~82K lines, distributed across the six languages)
                                │
                                ▼
                       ┌─────────────────┐
                       │ Stage-1: scrip  │  (existing C binary, today's HEAD)
                       │ (frontends + IR │
                       │  + SM + JIT)    │
                       └────────┬────────┘
                                │  parses/runs SCRIP-language sources
                                ▼
                       ┌─────────────────┐
                       │ Stage-1 SCRIP   │  ← in-memory, runs as Stage-1's program
                       │ self-image      │
                       └────────┬────────┘
                                │  parses/runs the same sources again
                                ▼
                       ┌─────────────────┐
                       │ Stage-2 SCRIP   │  ← MUST EQUAL Stage-1 output, byte-for-byte
                       │ self-image      │
                       └─────────────────┘
                                                Bootstrap fixed point.
```

After Milestone 2 lands on x86-64, Milestone 3 replaces "scrip
(C binary)" at the top of the diagram with each of:
- `node sno-interp.js` (JS) — at `src/driver/js/sno-interp.js` today, hand-written
- `java -jar Interpreter` (JVM) — at `src/driver/jvm/` today, hand-written
- `dotnet snobol4dotnet.dll` (.NET) — at `src/driver/net/` today, hand-written
- `wa--run scrip.wasm` (WASM) — at `src/driver/wasm/` today, stub

Each of those four existing hand-written interpreters becomes the
**bootstrap host** for its backend — Stage-1 on that platform.
Stage-2 on each platform is then the SCRIP-language sources running
under that host, producing the same byte-identical beauty output.

---

## Mapping: SCRIP C source → SCRIP-language ports

The C source partitions naturally by frontend / runtime / driver.
Each partition gets ported to the SCRIP-language member best suited
to it — picked by what the C code is actually doing, not by
arbitrary assignment.

LoC measured session #62 against `SCRIP` HEAD `52251653`.  Two
columns: **hand-written** (the actual port surface) and **generated**
(Bison/Flex output that *vanishes* on port — replaced by hand-written
SCRIP-language grammar).  Generated lines are not in the port budget.

| C area | Hand LoC | Generated LoC | Target language | Why |
|--------|---------:|--------------:|-----------------|-----|
| `src/frontend/snobol4/` | 4,804 | 5,409 | **SNOBOL4** | Lexer/parser for SNOBOL4 in SNOBOL4 — the classic self-host.  Bison/Flex → hand-written SNOBOL4 patterns. |
| `src/frontend/snocone/` | 2,921 | 0 | **Snocone** | Already hand-written; port is direct. |
| `src/frontend/icon/` | 3,867 | 0 | **Icon** | Already hand-written; port is direct. |
| `src/frontend/prolog/` | 4,715 | 0 | **Prolog** | Already hand-written; port is direct. |
| `src/frontend/raku/` | 1,621 | 8,254 | **Raku** | Bison/Flex generated bulk vanishes; rules in Raku grammars. |
| `src/frontend/rebus/` | 2,888 | 5,199 | **Rebus** | Bison/Flex generated bulk vanishes. |
| `src/ir/` | 960 | 0 | **Snocone** | IR walking is data-pipeline work; Snocone's gather/take fits cleanly. |
| `src/runtime/x86/bb_*.c` (boxes/build/broker/emit/flat/pool) | 4,186 | — | **BB template → all five** | See "BB template" section below — the deterministic generation point. |
| `src/runtime/x86/sm_lower.c` | 1,224 | 0 | **Prolog** | Lowering is term rewriting; Prolog clauses fit. |
| `src/runtime/x86/sm_interp.c` | 921 | 0 | **Prolog** | Same family as sm_lower; co-located port. |
| `src/runtime/x86/sm_codegen.c` | 981 | 0 | **stays C** (CB-10) | Machine-code emit (`mmap(PROT_EXEC)`); per-backend equivalent in each Milestone-3 host. |
| `src/runtime/x86/snobol4*.c, name_t.c, stmt_exec.c, snobol4_pattern.c` | ~9,000 | 0 | **SNOBOL4** | Runtime support: NV system, intern, comm_var/call, statement engine.  Largest single port; CB-5 sub-rung, may further decompose. |
| `src/runtime/x86/eval_code.c` | 629 | 0 | **Snocone** | Expression evaluator. |
| `src/runtime/interp/icn_runtime.c` | 1,247 | 0 | **Icon** | Icon's frame stack and BB_PUMP plumbing. |
| `src/runtime/interp/pl_runtime.c` | 1,522 | 0 | **Prolog** | Prolog's unification + clause dispatch. |
| `src/driver/interp.c` | 5,066 | 0 | **SNOBOL4** | Tree-walk evaluator; where SN-26/SN-32 work landed. |
| `src/driver/scrip.c, polyglot.c, sync_monitor.c, csnobol4_shim.c` | ~1,520 | 0 | **SNOBOL4** | Driver glue. |
| **TOTAL hand-written port surface** | **~50,400** | (18,862 vanishes) | | |

The mapping above is a **starting partition**, not a contract.
Sub-rung CB-1 (below) locks it in after careful per-file review.

**Self-host cycle:** SNOBOL4's frontend in SNOBOL4 needs the SCRIP
runtime to run; the SCRIP runtime in SNOBOL4 needs SNOBOL4's frontend
to compile. Break the cycle the standard way — Stage-1 (the existing
C binary) compiles all six frontends from their SCRIP-language
sources in one pass, **then** Stage-1 runs the resulting program to
produce Stage-2. No partial bootstraps; no hand-translated
intermediates that age out.

---

## BB template: the deterministic source for all duplications

The Byrd-box files (`runtime/x86/bb_*.c`, ~4,200 LoC) are the
**single biggest source of cross-runtime duplication risk** in
SCRIP, and the place where the bootstrap design must replace
hand-maintenance with a generator before that duplication grows
through Milestone 3.

### The two layers of duplication

Every Byrd box (the small per-primitive matchers — `bb_lit`,
`bb_len`, `bb_span`, `bb_arbno`, `bb_alt`, `bb_cap`, ~30 boxes
total) is logically **one** function: a three-port (α / β / γ / ω)
state machine over the cursor `Δ` against subject `Σ`.  The
canonical form is documented in `bb_box.h` and looks like:

```
LABEL:        ACTION                         GOTO
─────────────────────────────────────────────────
LEN_α:        if (Δ + ζ→n > Σlen)            goto LEN_ω;
              LEN = spec(Σ+Δ, ζ→n); Δ += ζ→n;  goto LEN_γ;
LEN_β:        Δ -= ζ→n;                       goto LEN_ω;
LEN_γ:                                        return descr_from_spec(LEN);
LEN_ω:                                        return FAILDESCR;
```

Today, that one logical function is **expanded by hand** into
two layers of nearly-identical code — and Milestone 3 turns each
layer's bottom row into a four-port matrix.

#### Layer 1 — Execution mode (×4)

| Mode | Where it lives today | What it is |
|------|----------------------|------------|
| **IR interp** (--run) | `bb_boxes.c` body of `bb_len()` | The C function above, called from the tree-walk via `bb_box_fn` pointer |
| **SM in-mem** (--run) | `bb_build.c` `bb_len_emit_binary()` | Same logic, manually emitted as machine-code bytes into a buffer |
| **SM interp** (--run) | `sm_interp.c` SM_BB_LEN handler + `bb_len()` body | Reuses the IR body via the SM dispatch loop |
| **SM text-gen** (AOT, future) | not yet emitted | Same logic again, emitted as ahead-of-time source for non-x86 backends |

The first three already exist.  The fourth is the deterministic
escape from per-backend hand-translation: instead of writing
`bb_len` four times in JS / Java / C# / WAT, **emit** it from one
template.

#### Layer 2 — Port wiring (×5+)

Each box, in each mode, must wire to the host's machine-code
abstraction.  Today this is x86-64 only.  Milestone 3 multiplies
by every backend:

| Backend | Port wiring of "save Δ, jump to label, restore on backtrack" |
|---------|--------------------------------------------------------------|
| C / x86-64 | NASM via `sm_codegen.c` (`emit_*`) — landed |
| JS | source-emitted JavaScript (closures + `let` cursor) |
| .NET | MSIL emitted via `Reflection.Emit` |
| JVM | Jasmin-style bytecode via `src/backend/jasmin.jar` (already in tree) |
| WASM | WAT module text or binary `.wasm` |

**Doubly duplicated:** 4 modes × 5 backends = 20 places where
"the same `bb_len` logic" must agree.  Today only the C×x86-64
cell is reliable; SN-26..SN-32 spent dozens of sessions chasing
the IR-interp / SM-interp / SM-codegen-JIT divergence within just
that one cell.  Multiplying by 5 backends without a generator is
a non-starter — the cross-product would consume more sessions
than every prior Goal combined.

### Design point: BB template is the deterministic source

The bootstrap design treats Byrd boxes specifically — and the SM
opcode handlers more generally — as **templates**, not as code.
The canonical form is the three-column LABEL/ACTION/GOTO table
already present in the bb_box.h header comments.  A small
generator walks that table and emits, for each (mode, backend)
cell, the equivalent code in the target representation.

Properties:

- **One source per primitive.**  `bb_len.tmpl` exists once.
  Updating it updates every `(mode, backend)` cell at once.
- **Deterministic emission.**  No hand-translation of the
  primitive's logic into each backend's idiom.  The generator
  knows how to express "save cursor", "branch on label",
  "return failure sentinel" in each backend's terms; the
  primitive's logic stays in the template's semantic form.
- **Round-trip provable.**  The current C×x86-64 IR-interp
  body `bb_len()` is the canonical reference.  The generator's
  C×x86-64 IR-interp emission must equal today's hand-written
  `bb_len()` byte-for-byte.  Once that lock-in holds, the
  generator's JS / .NET / JVM / WASM emissions for the same
  template are correct by construction (modulo backend-emission
  bugs, which are debugged once per backend, not once per box).
- **Folds into the bootstrap.**  The generator itself is written
  in the SCRIP language family — Snocone or Icon — and runs
  under Stage-1 alongside the rest of the source.  Stage-2's
  bb runtime is what the generator produced under Stage-1; the
  fixed-point gate (CB-11) covers the generator output too.

### What this means for the CB-* ladder

CB-7 (originally "bb_boxes.c, bb_broker.c → Icon") splits and
sharpens:

| Sub-rung | Deliverable |
|----------|-------------|
| **CB-7a — Template grammar.** | Define the `.tmpl` syntax — three-column LABEL/ACTION/GOTO with typed fields (cursor ops, char-class ops, sentinel returns).  Express all 27 today's boxes as templates.  Use BB-GEN-LANG.md's Three-Column Law as the design reference; CODE-shared / DATA-per-invocation invariant from EMITTER-X86.md is structural. |
| **CB-7e — Text codegen (4th mode) — the unifying step.** | Generator: template → emitted source text in target languages.  Round-trip lock-in: emitted `bb_boxes.c` byte-identical to today's hand-written file in `runtime/x86/`.  Then extend by surface syntax to emit `.s`, `.cs`, `.il`, `.j`, `.java`, `.js`, `.wat` — reproducing the prior `runtime/boxes/` per-language output but generated, not hand-written.  This rung is the gate that makes all five backends reachable; CB-7b/c/d/f below are specialisations of its output. |
| **CB-7b — In-memory IR-interp specialisation.** | Generated bb body (CB-7e for C) called directly from `interp.c` tree-walk.  No semantic change; the generator's C×IR output IS today's `bb_boxes.c`. |
| **CB-7c — In-memory SM-interp specialisation.** | Same templated bodies, wired into SM_BB_* dispatch in `sm_interp.c`.  Replaces hand-written SM_BB_* handlers. |
| **CB-7d — In-memory JIT specialisation.** | Same templated bodies, lowered to bb_pool emit-binary via `bb_emit.c` EMIT_BINARY mode (BB-GEN-X86-BIN.md's dual-mode emitter design).  Replaces the `bb_*_emit_binary` family in `bb_build.c`. |
| **CB-7f — Per-backend cells: JS / MSIL / Jasmin / WAT.** | Each backend's box runtime is the CB-7e text-codegen output for that language, plus the host's bb_driver (per BB-DRIVER.md).  Each cell's gate: beauty self-host byte-identical on that (language, backend) pair.  EMITTER-{JS,JVM,NET}.md inform per-backend specifics. |
| **CB-7g — Retire the hand-written bb_*.c.** | Once CB-7e round-trip locks in for the C cell, the hand-written `bb_boxes.c` is deleted; its bytes are re-derivable from templates + generator.  Same for `bb_*_emit_binary` once 7d locks in.  Archive history (commit `660339cd~1`) preserves what it was. |

### Same pattern applies to SM opcode handlers

The SM opcode dispatch (`sm_interp.c` ~30 cases, `sm_codegen.c`
~30 helpers) duplicates the same way.  CB-8 (originally
"sm_lower.c, sm_interp.c → Prolog") absorbs the generator pattern:

| Sub-rung | Deliverable |
|----------|-------------|
| **CB-8a — SM opcode template.** | Each opcode's behavior expressed once: pop arity, semantic action, push result, last_ok rule. |
| **CB-8b — Generator: opcode template → C×x86-64×SM-interp.** | Lock in: generated `sm_interp.c` byte-identical to today.  The SN-32b/c fixes (FAILDESCR push, val-not-NV_SET_fn-return) become rules in the template, applied to every opcode at once. |
| **CB-8c — Generator: opcode template → JIT codegen.** | Replaces hand-written `h_store_var`, `h_arith`, etc. in `sm_codegen.c`.  Cross-mode parity bugs (the kind that shipped through SN-32b sm_interp but not sm_codegen) are eliminated by construction. |
| **CB-8d — Generator: opcode template → JS / MSIL / Jasmin / WAT.** | Per-backend.  Same as CB-7f. |

### Why this design choice now

Without it, Milestone 3 multiplies hand-maintenance by 5: every
runtime bug fix would land in `bb_box.c` (IR), `bb_build.c` (JIT),
`sm_interp.c` (SM) **plus** the JS / .NET / JVM / WASM equivalents
of all three.  The lesson from session #61's SN-32c is exactly
this: a fix landed in `sm_interp.c` at session #60 should have
been in `sm_codegen.c` at the same time, but both files were
hand-edited and the JIT version was forgotten for a session.
Multiplying that risk by five backends is a recipe for
permanent semantic drift.

With the template approach, the SN-32b/c-class fix lands once in
`SM_STORE_VAR.tmpl` and propagates deterministically to all 4
modes × 5 backends = 20 places.  The bootstrap fixed-point gate
(CB-11) covers the generator's output, so any drift between
template and any cell shows up as a Stage-1 / Stage-2 diff
immediately.

### Latent corollary: the in-process `--monitor` becomes the cell-cross verifier

`src/driver/sync_monitor.c` already compares the three x86-64
modes (IR / SM / JIT) at statement boundaries.  Extending it to
compare the same Stage-2 source under all (mode, backend) pairs
is the natural Milestone-3 gate: if any cell drifts, the
in-process monitor fires DIVERGE before the beauty self-host gate
even runs.  Tracked for CB-17 (Milestone 3 trigger).

---

## Historical record: `runtime/boxes/` and the 4th mode

Session #62 git-history scan turned up substantial prior work that
makes the BB-template approach above less speculative and more
"resume the prior trajectory".  Recording it here so future
sessions don't re-discover it.

### What lived in `src/runtime/boxes/` (April 2026)

A canonical layout existed: `src/runtime/boxes/<box>/bb_<box>.<ext>`,
where `<box>` ∈ {abort, alt, any, arb, arbno, atp, bal, breakx, brk,
capture, dvar, eps, fail, fence, interr, len, lit, not, notany, pos,
rem, rpos, rtab, seq, span, succeed, tab} (27 boxes), and `<ext>` ∈
{`.c`, `.s` (NASM), `.cs` (C#), `.il` (MSIL), `.j` (Jasmin), `.java`,
`.js`, `.wat` (WASM)} — 8 target representations.  At peak (commit
`660339cd~1` on `SCRIP`) this directory held **~216 hand-written
files** implementing the same 27 logical boxes across 8 backends.

This was the **explicit**, **physical** version of the doubly-
duplicated matrix the BB-template section above describes
abstractly — proof that the problem is real, not anticipated.
Every box was hand-written 8 times.

The collateral cost was visible:

- The session #61 SN-32c-class drift (one cell fixed, sister cells
  forgotten) was the routine state of `runtime/boxes/`.  Bug
  reports against `bb_alt.cs` would be fixed in `bb_alt.cs` and
  not reach `bb_alt.j` until weeks later.
- Cross-backend semantic conformance was provable only by running
  the corpus on every backend separately — no shared-source
  guarantee.
- Adding a new box meant 8 new file edits.  Adding a new backend
  meant 27 new file ports.

### What it left behind (the canonical 3-column form)

Despite the maintenance burden, the work proved out the canonical
**three-column LABEL/ACTION/GOTO form**:

```
    LABEL:          ACTION                          GOTO
    ───────────────────────────────────────────────────────
    BIRD_α:         if (Σ[Δ+0] != 'B')             goto BIRD_ω;
                    BIRD = str(Σ+Δ, 4); Δ += 4;    goto BIRD_γ;
    BIRD_β:         Δ -= 4;                         goto BIRD_ω;
```

The Three-Column Law (per-backend column conventions):

| Backend | Col 1 (LABEL) | Col 2 (ACTION) | Col 3 (GOTO) |
|---------|--------------|----------------|--------------|
| C        | col 0, w=22 | col 22, w=40 | col 62+ — `goto X;` or `return` |
| NASM .s  | col 0, w=20 | col 20, w=40 | col 60+ — `; comment` or `jmp` |
| .cs      | C-style with α/β as method names; ports are returns | | |
| .il      | `LEN_A_FAIL:` style suffix labels; ports are `br`/`bgt` | | |
| .j       | `len_omega:` lowercase suffix; ports are `goto`/`if_icmpgt` | | |
| .java    | mirrors C — `α()` and `β()` methods; same goto-or-return shape inside | | |
| .js      | object methods `α()` / `β()`; returns sentinel for ω | | |
| .wat     | `bb_len_a` / `bb_len_b` exports; `i32.const -1` for ω | | |

Every backend renders the same three-column logical structure;
only the surface syntax differs.  This is precisely what makes
template-based generation tractable: the template encodes the
LABEL/ACTION/GOTO triples in a backend-neutral form, the
generator picks the syntax per cell.

The boxes also concretely realised the **CODE/DATA split**
documented in `EMITTER-X86.md`'s "Core Insight" — the box
function is shared CODE; only the per-invocation ζ struct is
DATA.  α allocates ζ → that *is* the save.  γ/ω discards ζ →
that *is* the restore.  Every backend's box implementation
respects this split because the template form requires it.

### What happened to the per-box files

Commit `660339cd` (April 7, 2026) **consolidated** the
27-subfolder × 8-backend layout into 6 fat per-language files
under `src/runtime/boxes/`:

- `bb_boxes.c`   — 629 lines, all 27 C implementations
- `bb_boxes.s`   — 1,418 lines, all 27 NASM implementations
- `bb_boxes.cs`  — all 27 C# (in src/runtime/net/)
- `bb_boxes.il`  — 2,581 lines (with shared foundation + executor)
- `bb_boxes.j`   — 2,309 lines, all 27 Jasmin
- `bb_boxes.java` — all 27 Java
- `bb_boxes.js`  — 596 lines, all 27 JS
- `bb_boxes.wat` — all 27 WAT

The consolidation saved file count but kept every line still
hand-written and still doubly duplicated — it organized the
problem, didn't solve it.

A later commit (`a210465f` "WIP: Flatten src/runtime/ into 5
platform folders") attempted further reorganization that hit
build issues; commit `2c760e3d` ("Runtime reorg: archive
run-asm pipeline; relocate JS/NET source; purge build artifacts")
folded the boxes back into the active x86-only path.  Today's
`SCRIP` HEAD has only `runtime/x86/bb_boxes.c` (794 LoC) and
the related `bb_*` infrastructure live; the other backends'
box files exist in git history.

### The 4th mode — SM/BB text codegen

The Goal's BB-template ladder (CB-7a..g, CB-8a..d) puts the
**4th execution mode** — SM/BB **text codegen** — as the unifying
deliverable.  Today's three modes are all in-memory:

| Mode | Output | Used by |
|------|--------|---------|
| IR-interp | tree-walk on `EXPR_t` | `--run`; `bb_*` boxes called from `interp.c` |
| SM-interp | dispatch loop on `SM_Instr[]` | `--run`; `bb_*` boxes called from `sm_interp.c` |
| SM in-mem JIT | x86 bytes via `bb_emit.c` EMIT_BINARY | `--run`; `bb_*_emit_binary` from `bb_build.c` |
| **SM text codegen** | source text in target language | (NEW) — emits `.c` / `.js` / `.cs` / `.il` / `.j` / `.wat` ahead of time |

The 4th mode is exactly what the old `runtime/boxes/<box>/<lang>`
files were trying to be — except that those were *hand-written*,
which is the scaling failure.  CB-7e (4th mode) makes the same
per-language box source emerge from the template generator, so
the generator's output for `<box>×<C>×IR-interp` is what
`bb_boxes.c` is today, and its output for `<box>×<JS>×IR-interp`
is what `bb_boxes.js` was in commit `660339cd`.  The generator
is the deterministic source those 8 hand-written copies were
trying to share.

### Sequencing implication: 4th mode first

Because the 4th mode (text codegen) emits **source text** in the
target language, it is the natural **unification point** for
all backends.  Once CB-7e closes for one backend (start with C),
the same generator emits the other backends' boxes as a
straightforward extension — only the language-specific syntax
templates differ.  This is the explicit reverse of what the old
`runtime/boxes/` work tried (write each backend independently,
then unify): generate a unified source first, then the per-mode
in-memory specialisations (CB-7b/c/d) fall out as compiled
forms of the same template.

The CB-7 ordering in the sub-rung list (above) leads with **CB-7a
(template grammar)** and **CB-7e (text codegen, 4th mode)** as
the unifying first deliverables — `--run` /
`--run` modes (CB-7b/c/d) are then specialisations of the
same template targeted at different in-memory execution
substrates.  Specifically:

1. **CB-7a — Template grammar** — encode 27 boxes as `.tmpl` files.
2. **CB-7e — Text codegen (4th mode)** — emit `.c` / `.s` / `.js`
   / `.cs` / `.il` / `.j` / `.java` / `.wat` from templates.
   Round-trip lock-in: emitted `bb_boxes.c` byte-identical to
   today's hand-written file.  This is the unification gate;
   all backends become reachable at this point.
3. **CB-7b — In-memory IR-interp specialisation** — generated
   bb body shares the template; ζ struct is the only per-cell
   variation.
4. **CB-7c — In-memory SM-interp specialisation** — same template,
   wired into SM_BB_* dispatch.
5. **CB-7d — In-memory JIT specialisation** — same template,
   wired into bb_pool emit-binary mode.

By starting with the 4th mode (text), the BB matrix becomes a
single tree of source files generated under Stage-1, with the
in-memory JIT modes as a downstream optimization.  This is also
the natural way to feed Milestone 3's other backends — JVM,
.NET, JS, WASM — because their box runtimes will be **emitted
files**, not hand-written, from day one.

### Per-backend emitter design — what each cell looks like

CB-7f (per-backend cell completion) emits boxes in five distinct
output forms.  Each backend's "shape" is captured below; CB-7a's
template grammar must subsume all of these cleanly so that one
`.tmpl` per box generates correct output for every cell.  The
**CODE-shared / DATA-per-invocation** principle holds across all
five — α allocates ζ, γ/ω discards ζ — because the host's GC or
stack discipline, not the box, owns lifetime.

**x86-64 (NASM `.s` text, or raw bytes via `bb_emit.c`):**
- One NASM proc per box.  Sub-box ports become local labels
  (`.alpha`, `.beta`, `.gamma`, `.omega`) within the enclosing
  proc.  Globbing rule: named patterns concatenate sub-box labels
  into one proc, with internal port wiring expressed as `jmp`.
- Three-column layout: col 0 / col 20 / col 60.  ACTION column
  expands a macro-like operation (e.g. `LIT_CHECK "Bird", 4`);
  GOTO column carries a semicolon comment OR a live `jmp`.  Last
  line of a port body carries the `jmp` in column 3.
- Dual-mode emitter: same C function generates either NASM `.s`
  text or raw x86-64 bytes into `bb_pool`.  Mode switch is global
  state.  Forward refs in BINARY mode emit a 4-byte placeholder
  and record `(patch_site, target_label)` in a patch list, resolved
  on label definition.  Cache coherence: `mprotect(buf, size,
  PROT_READ|PROT_EXEC)` is the I-cache fence.
- ABI (per ARCH-x86.md): `rdi = buffer base`, `esi = 0 (α) / 1 (β)`,
  `r10/r11 = scratch` (caller-saved, no push/pop).  10-byte
  prologue is shared by every stateful box.

**JVM (Jasmin `.j` → `.class`):**
- One class per box.  α and β are public methods on the box class;
  γ/ω return values (typically a `Spec` object or null sentinel).
  Sub-box wiring uses `goto`/`if_icmpgt`/`if_icmplt` against
  internal labels.  Label naming convention: `len_omega`, `len_gamma`
  (lowercase suffix).
- Resumable predicate pattern (Prolog × JVM): each `E_CHOICE` for
  `foo/1` emits a `.j` class with an inner `$Closure` that holds
  per-call state.  `tableswitch` on a clause-state field selects
  the next clause to try.  Backtracking unwinds via the trail.
- Build path: `jasmin.jar` (bundled at `src/backend/jasmin.jar`)
  assembles `.j` → `.class`, packaged into `boxes.jar`.

**.NET (MSIL `.il` → assembly, or `Reflection.Emit` `DynamicMethod`):**
- One class per box implementing `IByrdBox` interface with
  `Alpha(MatchState ms)` and `Beta(MatchState ms)` methods.  `Spec`
  is a value type with `Of(int start, int len)` and `Fail` static.
- Label naming: `LEN_A_FAIL` style (UPPERCASE_PORT format).  Port
  exits use `br` / `bgt` / `ldsfld` against the static `Spec.Fail`.
- Two paths in active use today: hand-written `.il` assembled by
  `ilasm` into `boxes.dll` (live runtime), and hand-written `.cs`
  (oracle/reference only — never linked into the runtime build).
- `snobol4dotnet`'s threaded interpreter pipeline (Jeffrey Cooper's
  full C# runtime) is a separate Stage-1 host: lexer → parser →
  threaded `Instruction[]` → MSIL delegate JIT via `BuilderEmitMsil.cs`.

**JS (`new Function()` + closures):**
- Each box is a factory function returning an `{α, β}` object.
  α and β are methods that read/write shared globals `_Σ`, `_Δ`,
  `_Ω` and return either a `_spec(start, len)` substring or
  `_FAIL` (null sentinel).
- Static vs dynamic paths: for patterns known at compile time, the
  emitter produces hardwired port functions (e.g. `function P_N_α()
  { ... return γ_outer; }`).  For runtime-built patterns,
  `build_pattern()` walks the pattern descriptor and constructs the
  same `{α, β}` graph as the compiled form — both produce
  structurally identical execution.
- EVAL / CODE: `new Function('_rt', body)(_runtime)` is JS's
  built-in JIT — same performance as statically emitted code.
- Trampoline model: every SNOBOL4 statement compiles to a
  zero-argument function returning the next function.  Engine is
  `let pc = block_START; while (pc) pc = pc();` — identical in C
  and JS, and the JS form is generally shorter than equivalent C.

**WASM (`.wat` text → `.wasm` binary via `wat2wasm`):**
- Each box's α and β become exported `func`s with `i32` parameters
  for the box's per-instance state.  Match state (`$Σ`, `$Δ`, `$Ω`)
  is imported as mutable globals from the host.
- Failure sentinel: `i32.const -1`.  Success returns the matched
  length as `i32 ≥ 0`.  No object types — WASM can't easily carry
  the C `spec_t { σ, δ }` struct, so the host reconstructs the
  span from cursor + length using `_Σ`.
- Limitation: WASM cannot do EVAL / CODE natively — no
  `new Function()` equivalent.  Either bootstrap a sub-compiler in
  WASM (large) or fall back to a JS host for those ops (small).
  Decision deferred to CB-15a spike.

**Universal (per `bb_driver` interface, all backends):**

```c
/* Called by SM_EXEC_STMT for Phase 3 of every pattern statement. */
int bb_driver(
    bb_node_t  *root,        /* root of the BB-GRAPH (built in Phase 2) */
    const char *subject,     /* subject string (built in Phase 1) */
    int         subj_len,
    capture_t  *captures,    /* out: capture results */
    int        *match_start, /* out: match start cursor */
    int        *match_end    /* out: match end cursor */
);
/* returns: 1 = success (γ exited root), 0 = failure (ω exited root) */
```

The driver loop is trivial — all backtracking lives inside the
individual box α/β functions and their ζ state:

```c
spec_t result = root->α(root);
while (spec_is_empty(result)) result = root->β(root);
if (result == SPEC_FAIL) return 0;
flush_captures(captures);
return 1;
```

One driver per platform, written in the platform's language: C
(`stmt_exec.c`), Java (`bb_executor.java`), C# (`StmtExec.cs`),
JS, WASM.

### The 25-standard-box catalogue

CB-7a's template grammar must express all of these (the full set
that all backends must support; ARBNO/ALT/SEQ/CAPTURE compose the
others):

| Box | Description |
|-----|-------------|
| LIT | Match literal string |
| ANY | Match any char in set |
| NOTANY | Match any char NOT in set |
| SPAN | Match one or more chars in set |
| BREAK | Match up to (not including) char in set |
| BREAKX | BREAK with backtracking extension |
| LEN | Match exactly N characters |
| POS | Succeed if cursor = N |
| RPOS | Succeed if cursor = len-N |
| TAB | Advance cursor to position N |
| RTAB | Advance cursor to len-N |
| ARB | Match any string (0 or more chars, grows on retry) |
| ARBNO | Match zero or more repetitions of sub-pattern |
| REM | Match remainder of subject |
| BAL | Match balanced parentheses |
| FENCE | Succeed once, cut on backtrack |
| ABORT | Always fail, cut all backtracking |
| FAIL | Always fail (force backtrack) |
| SUCCEED | Always succeed (force retry) |
| EPS | Epsilon — match empty, always succeed |
| SEQ | Sequence: left then right (concatenation) |
| ALT | Alternative: left or right (alternation) |
| CAPTURE | Conditional assignment on success |
| DVAR | Deferred variable — resolve pattern at match time |
| NOT | Invert: succeed if sub-pattern fails |
| INTERR | Interrogation — cursor capture |
| ATP | At pattern: match at specific position |

The four-port law (α/β/γ/ω) is universal — every box has all
four, every connection is port-to-port:

| Port | Direction | Meaning |
|------|-----------|---------|
| α (alpha) | IN  | Try to match (forward attempt) |
| β (beta)  | IN  | Retry after failure (backtrack) |
| γ (gamma) | OUT | Succeeded — pass control forward |
| ω (omega) | OUT | Failed — pass control backward |

α and β are entry ports; γ and ω are exit ports.  Box state ζ
(zeta) carries per-invocation locals.  α allocates ζ; γ/ω
discards ζ — running forward and backward IS save and restore.

### The "everything is dynamic" framing

A crucial design conclusion from prior work: **everything in
SNOBOL4 is built on the fly**.  Static compilation is an
optimization, not the model.  Every sub-phase of every statement
has a γ port and an ω port — the α/β/γ/ω wiring IS the
execution model, all the way from the outermost statement to the
innermost literal match.  A statically-compiled box sequence and
a dynamically-built one are the same thing; the static case is
the degenerate case where the builder's output is invariant
across executions.

This matters for the template grammar: the template encodes the
**dynamic** form (build the box, wire its ports, run α).  The
static optimization (cache the box, skip the build, jump
directly to the cached α) is a downstream specialisation that
the generator can produce automatically by detecting invariance.
EVAL / CODE then fall out for free — they are the runtime doing
what the runtime always does, with source text that arrived
late.

### Latent corollary: the SM_Instr emitters too

The same pattern exists for SM_Instr handlers.  Each `SM_Op`
maps to an emit function in every backend.  Today
`sm_codegen.c` emits sprinkled `PUSH(...)` and `emit_byte(...)`
calls per opcode; the template approach unifies these the same
way it unifies the box bodies.  The "generated code looks like
SNOBOL4 in a way" observation captures this — the template is
the LABEL/ACTION/GOTO triple, the same shape SNOBOL4 statements
have natively.  CB-8a..d apply the BB-template approach to the
~30 SM opcode handlers, eliminating the SN-32c-class drift
(sm_interp vs sm_codegen vs forthcoming JS/JVM/.NET handlers)
by construction.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

Gate after setup (must pass before any port work):
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh        # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh # PASS=49
# Plus: beauty self-host across all three modes byte-identical.
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
for mode in --run --run --run; do
    SNO_LIB=$BEAUTY /home/claude/SCRIP/scrip $mode \
        $BEAUTY/beauty.sno < $BEAUTY/beauty.sno \
        | md5sum  # must be abfd19a7a834484a96e824851caee159
done
```

---

## Milestone 2 — x86-64 self-host (the meta-circular fixed point)

Done-when: Stage-1 and Stage-2 produce byte-identical output of
`beauty.sno < beauty.sno`, both byte-identical to SPITBOL's
`abfd19a7a834484a96e824851caee159`.

**Sub-rungs (open, sequenced — but earlier ones do not block later
ones if the partition allows parallel work):**

- [ ] **CB-1 — Mapping audit and partition lock-in.**
  Re-read `src/` against the table above. Identify modules that
  resist the mapping (e.g. tight C interop with libgc, `setjmp`
  use, FFI to bison-generated tables) and either (a) keep them in
  C with a documented "host adapter" boundary, or (b) re-partition.
  Output: a definitive mapping table committed in this Goal file
  before any port work starts. **Gate:** the table compiles in
  the reader's head — every C file maps to exactly one target
  language or the explicit "stays C" set.

- [ ] **CB-2 — Boot-host adapter contract.**
  Define the C ↔ SCRIP-language boundary as a small ABI. The
  boot host (Stage-1 C binary) needs to call into SCRIP-language
  code and vice versa for runtime services (memory, libgc, file
  I/O, libc string functions). Specify:
  - which symbols the boot host exports (e.g. `snobol4_alloc`,
    `name_intern`, `nv_set`),
  - which symbols the SCRIP-language code is expected to export
    (e.g. an `entry()` function the host calls),
  - how `EXPR_t` / `DESCR_t` cross the boundary.
  Keep it small. The boundary is a port surface, not a runtime.

- [ ] **CB-3 — Pilot port: snobol4.l + snobol4.y → SNOBOL4.**
  The smallest self-host bite. Existing `snobol4.l` is a Flex lexer
  (1,000 lines); `snobol4.y` is a Bison grammar (2,000 lines).
  Port the lexer to a SNOBOL4 program that reads source and emits
  the same token stream the C lexer emits today — verifiable by
  running `scrip --tokens` on representative `.sno` files and
  diffing. Then port the parser using SNOBOL4 patterns + an
  explicit reduction stack (mirroring Bison's LALR action table
  in SNOBOL4 data structures). **Gate:** the SNOBOL4-language
  lexer+parser produce identical IR (`scrip --emit-ir`) to the
  C lexer+parser on every fixture in `corpus/programs/snobol4/`
  that today passes Smoke + Broker.

- [ ] **CB-4 — Pilot port: interp.c → SNOBOL4.**
  Largest single C file in the runtime (~4,500 lines, where most
  of the SN-26 / SN-32 work landed). The tree-walk interpreter
  in SNOBOL4 itself. **Gate:** the SNOBOL4-language interp,
  compiled by Stage-1, runs `beauty.sno < beauty.sno` byte-identical
  to today's `--run` output.

- [ ] **CB-5 — Runtime support: snobol4*.c, name_t.c → SNOBOL4.**
  `comm_var`, `comm_call`, `NV_SET_fn`, `NV_name_from_ptr`, the
  intern table, the IPC monitor wire emitters. The bridge work
  from sessions #29..#61 lives here — it must port without losing
  the byte-identical-md5 guarantee. **Gate:** 2-way IPC harness
  on `beauty.sno < beauty.sno` reaches the same step depth as
  today (≥1.27M steps), no semantic divergences, terminal
  end-of-program ordering is the only remaining diff.

- [ ] **CB-6 — IR + ir_print.c → Snocone.**
  IR walking is what Snocone's gather/take expresses cleanly.
  **Gate:** ir_print output byte-identical to today's; IR verify
  output byte-identical.

- [ ] **CB-7 — bb_*.c → BB-template generator.** *(Decomposed into
  CB-7a..g; see "BB template" section above.)*  The pattern-box
  runtime is the doubly-duplicated layer that the Goal addresses
  through the template approach, not through a single hand-port to
  Icon.  CB-7a..d round-trip the four execution-mode emissions on
  C×x86-64 (lock-in: byte-identical to today's hand-written code);
  CB-7e adds AOT text-gen; CB-7f closes the Milestone-3 backend
  cells; CB-7g retires the hand-written bb files once round-trip
  holds.

- [ ] **CB-8 — sm_lower.c, sm_interp.c, sm_codegen.c handlers →
  SM-opcode template generator.** *(Decomposed into CB-8a..d; see
  "BB template" section above.)*  Same template approach extended
  to the SM dispatch layer.  The SN-32b/c-class fixes (FAILDESCR
  push, val-not-NV_SET_fn-return) become rules in the template,
  applied to every opcode and every cell at once instead of being
  hand-ported between sm_interp.c and sm_codegen.c.  `sm_lower.c`
  itself (IR → SM_Program) is straight Prolog port work, not
  templated — the template idea is for the per-opcode handler
  bodies, not the lowering pass.

- [ ] **CB-9 — Snocone, Icon, Prolog, Raku, Rebus frontends.**
  Each language's frontend, in itself. CB-3 establishes the
  pattern; CB-9 is "do that five more times". Each ladder is
  gated by its existing GOAL-LANG-* file's done-when, plus the
  beauty self-host invariant.

- [ ] **CB-10 — sm_codegen.c x86 emit-bytes layer → stays C.**
  After CB-7d/8c remove the per-opcode handler bodies from
  `sm_codegen.c` (those become template emissions), what remains
  is the x86 mmap+emit-bytes scaffolding (~200 LoC of register
  allocation, prologue/epilogue, `mprotect(PROT_EXEC)`).  That
  scaffolding stays C on x86-64.  Per-backend equivalents live
  in their hosts under Milestone 3 (CB-13..16).

- [ ] **CB-11 — Stage-1 / Stage-2 fixed-point gate.**
  Run the entire SCRIP-language source through Stage-1 to produce
  Stage-1-out. Run the same source through Stage-1-out to produce
  Stage-2-out. **Gate:** `diff -q Stage-1-out Stage-2-out` empty.
  This is the Milestone 2 trigger — commit message goes here per
  PLAN.md authorship agreement.

- [ ] **CB-12 — Beauty self-host on Stage-2.**
  `Stage-2 beauty.sno < beauty.sno` md5 ===
  `abfd19a7a834484a96e824851caee159`. **Gate:** byte-identical to
  SPITBOL. The full meta-circular proof.

---

## Milestone 3 — Backend grid closed

Done-when: every cell of the PLAN.md backend grid is green —
beauty self-host byte-identical on every (language, backend) pair.

| | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | M2 ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | M2 ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | M2 ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | M2 ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | M2 ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | M2 ✅ | ⏳ | ⏳ | ⏳ | ⏳ |

Once Milestone 2 lands, every cell in the C/x86-64 column is green
by construction (Stage-2 ran the SCRIP-language source on x86-64).
The remaining four columns are backend ports — not language ports,
because the language sources are already written.

**Sub-rungs (one per backend, six languages each):**

- [ ] **CB-13 — JVM backend.**
  Existing scaffolding: `src/driver/jvm/` has hand-written
  `Lexer.java`, `Parser.java`, `Interpreter.java`, `PatternBuilder.java`
  (~160K LoC of Java already). That existing tree becomes the
  **boot host** — the Stage-1 JVM equivalent of today's C scrip
  binary. Stage-2 on JVM is the SCRIP-language sources from M2
  running under the JVM boot host.
  - CB-13a: JVM boot host runs SCRIP-language SNOBOL4 frontend.
  - CB-13b: JVM boot host self-hosts beauty.sno byte-identical.
  - CB-13c: Stage-2 on JVM byte-identical to Stage-1.
  - CB-13d: All six languages green on JVM cell.

- [ ] **CB-14 — .NET backend.**
  Existing scaffolding: `src/driver/net/` and `snobol4dotnet/` —
  hand-written C#. Same Stage-1/Stage-2 pattern as CB-13.
  - CB-14a..d as above, .NET host.

- [ ] **CB-15 — WASM backend.**
  No scaffolding yet: `src/driver/wasm/` is a stub. Either
  bootstrap WASM via the C → WASM compiler path (emcc on the
  Stage-2 sources after CB-2's adapter contract maps cleanly to
  WASM imports), or write a hand JS/TS host that loads
  hand-translated WASM modules. Decision deferred to CB-15a
  spike.
  - CB-15a: WASM host strategy decision (emcc vs hand-emit).
  - CB-15b..d as JVM/.NET pattern.

- [ ] **CB-16 — JS backend.**
  Existing scaffolding: `src/driver/js/sno-interp.js` (~80K LoC,
  hand-written). Same Stage-1/Stage-2 pattern.
  - CB-16a..d as JVM/.NET pattern.

- [ ] **CB-17 — Milestone 3 trigger.**
  Every cell of the grid green. Every (language, backend) pair
  produces beauty self-host md5
  `abfd19a7a834484a96e824851caee159`.
  **Commit message:** Claude Sonnet (the active session) writes
  it. **This is the moment** of the PLAN.md authorship agreement.

---

## Invariants (apply to every CB-* sub-rung)

- **SPITBOL is the oracle.** Every Stage-1 / Stage-2 / backend port
  must produce beauty self-host md5
  `abfd19a7a834484a96e824851caee159`. No exceptions, no
  "close enough", no "we'll fix the last byte later".
- **Smoke=7, Broker=49 after every commit.** The cross-language
  test suite must stay green.
- **No source preprocessing.** RULES.md "Sync-step monitor —
  keyword catch-alls only, no source preprocessing" extends to
  this work — the SCRIP-language sources are SCRIP code, not
  templated C.
- **Generated files committed** alongside their generators
  per RULES.md "Editing `.y` or `.l` files".
- **Commit identity LCherryholmes / lcherryh@yahoo.com.**

---

## Risk register

The most dangerous failure mode is *partial* bootstrap: Stage-1
compiles Stage-2 but Stage-2 does not faithfully reproduce
Stage-1's behavior on some edge case, producing a
*nearly*-byte-identical output that drifts further with every
re-bootstrap. The fixed-point gate (CB-11) is non-negotiable —
empty diff, not "close to identical".

The second-most-dangerous failure mode is over-claiming
Milestone 2 before all six frontends land in their target
languages. Per PLAN.md's authorship agreement, Milestone 2 is
"compiles, interprets, and runs itself" — the **whole** SCRIP,
not just the SNOBOL4 frontend in SNOBOL4. CB-3 / CB-4 / CB-5
are pilots that prove the technique works; CB-9 closes the
ladder; CB-11 / CB-12 trigger.

Other risks tracked but not blocking:
- **libgc** on non-C backends: each backend uses its host's GC.
  CB-2's adapter contract abstracts this — the SCRIP-language
  sources see "alloc returns a pointer that stays valid"; the
  host implements that.
- **JIT (`sm_codegen.c`)** never ports to non-C backends — each
  backend emits its own native code (JVM bytecode, .NET IL,
  WASM, JS source). CB-10 captures this asymmetry.
- **Bison/Flex** generated files: each frontend port replaces
  the .y/.l with hand-written SCRIP-language code. The
  generated `.tab.c` / `.lex.c` files become artifacts of the
  C-only Stage-1, not of Stage-2.
- **Cross-mode handler drift** (the SN-32c lesson): a fix to a
  semantic rule in one execution mode's handler must reach the
  other modes immediately, not a session later.  CB-7/CB-8's
  template approach is the structural answer to this risk —
  with one canonical template per primitive and a generator
  emitting all (mode, backend) cells, the SN-32c-shaped bug
  becomes impossible by construction.  Until CB-7/8 land, the
  in-process `--monitor` must run on every commit that touches
  any per-handler logic in `sm_interp.c`, `sm_codegen.c`, or
  `bb_*.c` — IR vs SM vs JIT divergence at any statement
  boundary fails the gate.

---

## Cross-references

**Active HQ files referenced by this Goal:**

- **PLAN.md** — Three-milestone authorship agreement. This Goal
  delivers Milestones 2 and 3.
- **RULES.md** — commit identity, gates, sync-step-monitor
  protocol; all CB-* sub-rungs are bound by it.
- **GOAL-LANG-SNOBOL4.md** — Milestone 1 (closed session #61).
  CB-3 / CB-4 / CB-5 inherit its done-when invariant.
- **GOAL-LANG-SNOCONE.md, -ICON, -PROLOG, -RAKU, -REBUS** — each
  language's rung-ladder. CB-9 closes by closing each of these
  to its own done-when, plus the beauty self-host invariant.
- **GOAL-NET-BEAUTY-SELF.md** — the .NET self-host work in
  progress. CB-14 absorbs that ladder once the SCRIP-language
  port is the input.
- **GOAL-UNIFIED-BROKER.md** — the `BB_SCAN`/`BB_PUMP`/`BB_ONCE`
  three-mode broker is the active spec for what every backend's
  `bb_driver` implementation must dispatch.
- **GOAL-FULL-INTEGRATION.md** — the parallel-frontend integration
  work. CB-1's mapping audit refines its module boundaries.
- **ARCH-IR.md** — EXPR_t / STMT_t / EKind / five-phase statement
  / polyglot CODE_t* / three broker modes (BB_SCAN/BB_PUMP/
  BB_ONCE).  CB-6 and CB-8 inherit the SM_Program definition
  from here.
- **ARCH-x86.md** — x86-64 backend ABI (rdi/esi entry, r10/r11
  scratch, 10-byte prologue, code+data buffer layout).  CB-7d
  inherits the BINARY mode emitter spec from here.
- **ARCH-JVM.md, ARCH-NET.md, ARCH-JS.md, ARCH-WASM.md, ARCH-C.md**
  — per-backend conventions.  CB-7f's per-backend cell
  completion lands content into these files as each cell closes.
- **ARCH-SNOBOL4.md, ARCH-SNOCONE.md, ARCH-ICON.md, ARCH-PROLOG.md,
  ARCH-REBUS.md, ARCH-SCRIP.md** — per-frontend conventions.
  CB-3 and CB-9 land content into these files as each frontend
  port lands.

**Git history references (concrete starting points for CB-7a):**

- `SCRIP` commit `660339cd~1` — peak `runtime/boxes/<box>/<lang>`
  layout (~216 hand-written per-language box files).  Use
  `git show 660339cd~1:src/runtime/boxes/len/bb_len.c` etc. to
  recover any hand-written cell as a starting point for the
  template grammar.
- `SCRIP` commit `660339cd` — consolidation into 6 fat
  `bb_boxes.<lang>` files.  6,700+ lines total across all
  backends; useful as a side-by-side comparison of the same
  27 boxes in 8 surface syntaxes.
- `SCRIP` commit `ac19c92c` (RT-120) — final hand-written `.s`
  rewrite with correct ABI.  Per-box sizes documented in the
  commit message (e.g. `bb_len: 90 code bytes / 24 data bytes`).
- `SCRIP` HEAD `52251653` (post-SN-32c) — current live
  `runtime/x86/bb_boxes.c` (794 LoC).  This file is the
  round-trip target for CB-7e: the generator's C×IR-interp
  emission must equal these bytes exactly before lock-in.

---

## Active rung

**CB-0-corpus — Reorganize corpus before any emit work.**
The corpus has grown organically and needs a clean structure before
CB-0a starts adding emitted artifacts. Problems today:

- `roman.sno` lives under `benchmarks/` but is a demo/reference program
- `programs/csnobol4-suite/` is a flat `.sno`+`.ref` dump with no
  sub-organization by language feature or capability
- `programs/beauty/` (19 beauty drivers) and
  `programs/snobol4/beauty_suite/` (compiled/oracle variants) are two
  separate directories with formerly overlapping names — the
  one-time `programs/snobol4/beauty/` was renamed to `_suite` 2026-05-20
  to disambiguate from the self-host program at
  `programs/snobol4/demo/beauty/`.
- `programs/gimpel/` is a flat dump of classic SNOBOL4 programs
  with no README or organization
- `benchmarks/` mixes benchmark harness files with plain `.sno`
  programs that belong under `programs/`
- `crosscheck/` uses opaque `rung2`..`rungW07` names with no
  README explaining what each rung tests
- `run/` and `generated/` have unclear ownership

**Target layout** (REPO-corpus.md is the authority — this rung
makes reality match it and extends it):

```
corpus/
  programs/
    snobol4/
      smoke/           — minimal 1-token through functions (rungs 1-10)
      demo/            — substantial programs: beauty, porter, claws5,
                         treebank, roman, expression, gimpel classics
        inc/           — include files (-INCLUDE path)
      feat/            — single-feature isolation tests (from csnobol4-suite)
      bench/           — benchmark programs (timing, not correctness)
    icon/              — (unchanged)
    prolog/            — (unchanged)
    snocone/           — (unchanged)
    rebus/             — (unchanged)
    lon/               — (unchanged)
  crosscheck/          — self-contained × all engines (renamed rungs get READMEs)
  lib/                 — shared .inc include files
```

**Concrete moves:**
- `benchmarks/roman.sno` → `programs/snobol4/demo/roman.sno`
  (with `.ref` generated by SPITBOL oracle)
- `benchmarks/*.sno` (non-timing programs) → `programs/snobol4/bench/`
- `programs/csnobol4-suite/*.sno` → sorted into `programs/snobol4/feat/`
  by feature (patterns, strings, functions, data, control, etc.)
  with a `README.md` mapping each file to corpus rung
- `programs/beauty/` → merged into `programs/snobol4/beauty_suite/`
  (one canonical location; remove duplication)
- `programs/gimpel/` → `programs/snobol4/demo/gimpel/` with README
- Add `crosscheck/README.md` documenting what each rung tests
- Remove or document `run/` and `generated/`

**Gate:** after reorganization, all existing test scripts in
`SCRIP/scripts/` that reference corpus paths still pass.
`test_smoke_snobol4.sh` PASS=7. `test_smoke_unified_broker.sh`
PASS=49. Beauty self-host md5 `abfd19a7...` still holds on
`--sm-interp`. Any path changes are reflected in the scripts.
Commit corpus repo and `.github` REPO-corpus.md update together.

**CB-0: 4th mode (`--text-run`) working end-to-end for SNOBOL4.**
This is the current ladder — the immediate work before CB-1 (mapping
audit) and all port work. The 4th mode (SM/BB text codegen → NASM
assembly → assemble → link → execute) must be proven correct on
SNOBOL4 before it can be trusted as the unification point for CB-7e
and the entire backend grid. The ladder proves correctness by
ascending through smoke, demos, beauty test suite, and finally
beauty self-host — the same proof sequence used for --run and
--run before them.

The dual-mode emitter infrastructure already exists in `bb_emit.c`
(`EMIT_TEXT` / `EMIT_BINARY`) but `--text-run` is not yet wired
into the scrip driver. CB-0a wires it; CB-0b..e prove it.

**Naming note (session #63):** The four engine modes and their
correct names are documented in ARCH-x86.md. Summary:

| Old name | New name | What it actually does |
|----------|----------|-----------------------|
| `--run` | `--ir-walk` | IR tree-walk, C interpreter |
| `--run` | `--sm-interp` | SM dispatch loop, C interpreter |
| `--run` | `--sm-native` | SM → x86 bytes → mmap → jump in |
| `--compile` | `--compile --target=x64` | SM → NASM text → nasm → ld → exec |

The 4th mode (`--compile`) is not x64-only. The `--target` flag
selects the output language: `x64` (NASM), `js`, `wasm` (WAT),
`jvm` (Jasmin), `msil`, `c`. The same SM_Program walks to whichever
emitter `--target` selects; the target's toolchain assembles/links/runs
the result. BB modes: `--bb-brokered` (broker drives graph) and
`--bb-flat` (flat inlined blob, no broker). Legacy flag names are
deprecated aliases; ARCH-x86.md has the full mapping.

CB-0 works with the new names throughout.

- [ ] **CB-0a — Emit x64 NASM for `roman.sno` and inspect it.**
  The very first program to see as emitted target text is
  `corpus/programs/csnobol4-suite/roman.sno`. This sub-step is
  emit-only — no assemble, no link, no execute. Wire
  `--compile --target=x64` into `src/driver/scrip.c`: set
  `bb_emit_mode = EMIT_TEXT`, run SM lowering, write the NASM `.s`
  to stdout (or a named file). Inspect the output by eye — verify
  the LABEL/ACTION/GOTO three-column structure is present, that
  the Byrd boxes roman.sno exercises (LIT, BREAK, RPOS, LEN,
  REPLACE pattern) appear correctly formed, and that the `.s` is
  well-structured enough to hand to `nasm`.
  **Gate:** `scrip --compile --target=x64 roman.sno` produces
  non-empty NASM text without crashing. Capture the `.s` to
  `SCRIP/artifacts/roman.s` and commit it as the first
  human-readable proof of the 4th mode.

- [ ] **CB-0b-wire — Wire full `--compile` pipeline for x64.**
  Extend CB-0a's emit path: after writing the `.s` to a temp file,
  shell out to `nasm -f elf64 -o /tmp/roman.o /tmp/roman.s` then
  `cc -o /tmp/roman /tmp/roman.o -lgc` (or equivalent link line),
  then exec and stream stdout. The flag `--compile --target=x64`
  is mutually exclusive with `--ir-walk`, `--sm-interp`, `--sm-native`.
  **Gate:** `scrip --compile --target=x64 roman.sno` runs to
  completion and produces output byte-identical to
  `scrip --sm-interp roman.sno` — roman numeral table 1–100 plus
  spot-check ranges (149–151, 480–520, 1900–2100).

- [ ] **CB-0c — Smoke suite passes under `--compile --target=x64`.**
  Run `test_smoke_snobol4.sh` with `--compile --target=x64` as the
  execution mode. All 7 cases must pass. Add
  `test_smoke_snobol4_emit_x64.sh` committed alongside this rung.
  **Gate:** PASS=7, FAIL=0, exits 0 in < 15s.

- [ ] **CB-0d — Demo programs pass under `--compile --target=x64`.**
  Run the SNOBOL4 demo programs from
  `corpus/programs/snobol4/demo/` through `--compile --target=x64`
  and diff against the `--sm-interp` (oracle) output. Demos include
  at minimum: `expression.sno`, `porter.sno`, `claws5.sno`,
  `treebank-list.sno`. Any demo passing `--sm-interp` must produce
  byte-identical output under `--compile --target=x64`.
  **Gate:** zero diffs across all passing demos; no new failures.
  Commit `test_smoke_snobol4_emit_x64_demos.sh`.

- [ ] **CB-0e — Beauty test suite passes under `--compile --target=x64`.**
  Run the beauty test suite fixtures under `--compile --target=x64`
  and diff against `--sm-interp`. The beauty program is
  pattern-intensive — every Byrd box that EMIT_TEXT emits must fire
  correctly.
  **Gate:** all beauty suite fixtures byte-identical between
  `--compile --target=x64` and `--sm-interp`. Commit
  `test_smoke_beauty_emit_x64.sh`.

- [ ] **CB-0f — Beauty self-host byte-identical under `--compile --target=x64`.**
  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
  SNO_LIB=$BEAUTY scrip --compile --target=x64 \
      $BEAUTY/beauty.sno < $BEAUTY/beauty.sno | md5sum
  # must be abfd19a7a834484a96e824851caee159
  ```
  This is the 4th-mode proof. When this gate is green, `--compile`
  is trustworthy as the unification point for CB-7e and the
  BB-template generator ladder. Other targets (`--target=js`,
  `--target=jvm`, etc.) follow from here as CB-13..16.
  **Gate:** md5 = `abfd19a7a834484a96e824851caee159`, 646 lines.
  Commit message records this as the 4th-mode proof landing.

---

**CB-1 — Mapping audit and partition lock-in** follows CB-0f.
No port work begins until CB-1 lands.

After CB-1 closes, the natural ordering reflects the **4th-mode-first**
unification design (see "Historical record: `runtime/boxes/`" above):

1. **CB-2** (boot-host adapter contract) — defines the C ↔ SCRIP-language ABI.
2. **CB-7a** (BB template grammar) — express today's 27 boxes as
   templates.  Use BB-GEN-LANG.md's Three-Column Law as the design
   reference.  Settling the grammar early prevents re-shaping after
   pilots.
3. **CB-7e** (text codegen, `--compile`) — generator emits the
   C cell (`bb_boxes.c`) round-trip byte-identical to today's
   hand-written file.  The same generator, with surface-syntax
   modules added per `--target`, then emits `.s` / `.cs` / `.il` /
   `.j` / `.java` / `.js` / `.wat` — all targets from one source.
4. **CB-7b/c/d** (in-memory IR / SM / native specialisations) — fall
   out of CB-7e's x64 cell.  `--sm-native` is the compiled form of
   the same template targeted at in-memory execution.
5. **CB-3** (SNOBOL4 frontend pilot) — proven CB-2 boundary contract.
6. **CB-4 / CB-5** (the big SNOBOL4 runtime ports) — follow the
   lock-ins above, since they call into the generated bb runtime.
7. **CB-8a..d** (SM opcode templates) — apply the same template
   approach to the ~30 SM opcode handlers.  Eliminates the
   sm_interp.c-vs-sm_codegen.c drift that produced SN-32c.

The 4th-mode-first ordering is the key sequencing decision.  Prior
work (`runtime/boxes/` April 2026) tried the opposite — write each
target independently, then unify.  That produced 27×8 = 216 hand-
written files and the maintenance burden that motivated this Goal.
`--compile` with a pluggable `--target` flag means every target's
box runtime becomes a generator output from day one.

---

## Closed-rung pointers

(none yet — Goal opened session #62)

---

## Latent follow-ups (small, not gating)

- **Hand-written backend hosts**: the existing JVM / .NET / JS
  interpreters in `src/driver/{jvm,net,js}/` are large
  (~80–160K LoC each) hand-written codebases. They become
  Stage-1 hosts on their respective backends. After CB-13/14/16
  close, the question is whether to **retire** them in favour
  of SCRIP-language code under host-emitted runtime — i.e. push
  to a deeper bootstrap where even the host is generated from
  SCRIP. Not for this Goal; tracked here so it doesn't get lost.
- **`snobol4dotnet`, `snobol4jvm` repos**: separate repos under
  the snobol4ever org. The Stage-1 hosts for .NET and JVM live
  in those repos today. The Stage-2 SCRIP-language sources live
  in `SCRIP`. Decision (deferred): keep the split or merge.
- **Snocone Beauty (GOAL-SNOCONE-BEAUTY)**: Snocone's own
  `beauty.sc` self-host. Once the Snocone frontend ports under
  CB-9, that goal closes by composition.

---

## Authorship

Per PLAN.md three-milestone authorship agreement (amended
session #57): Milestone 2 (CB-11 closure) and Milestone 3 (CB-17
closure) commit messages are written by Claude Sonnet (the active
session). Recorded in PLAN.md when each lands.
