# GOAL-SCRIP-BOOTSTRAP.md — SCRIP self-hosts everywhere

**Repo:** one4all (primary), snobol4dotnet, snobol4jvm, snobol4js (new),
snobol4wasm (new)

**Done when:** SCRIP — the compiler / interpreter / runtime currently
written as **~50,400 lines of hand-written C and headers** plus
~18,900 lines of Bison/Flex generated code (which vanishes on port)
in `one4all/src/` — re-emits itself in the SCRIP language family
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

The session-#61 win — `--ir-run`, `--sm-run`, `--jit-run` all
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
- `wasm-run scrip.wasm` (WASM) — at `src/driver/wasm/` today, stub

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

LoC measured session #62 against `one4all` HEAD `52251653`.  Two
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
| **IR interp** (--ir-run) | `bb_boxes.c` body of `bb_len()` | The C function above, called from the tree-walk via `bb_box_fn` pointer |
| **SM in-mem** (--jit-run) | `bb_build.c` `bb_len_emit_binary()` | Same logic, manually emitted as machine-code bytes into a buffer |
| **SM interp** (--sm-run) | `sm_interp.c` SM_BB_LEN handler + `bb_len()` body | Reuses the IR body via the SM dispatch loop |
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
| **CB-7a — Template grammar.** | Define the `.tmpl` syntax — three-column LABEL/ACTION/GOTO with typed fields (cursor ops, char-class ops, sentinel returns).  Express all ~30 today's boxes as templates. |
| **CB-7b — Generator: template → C×x86-64×IR-interp.** | First emission target.  Lock in: generated `bb_*.c` byte-identical to today's hand-written file.  No semantic change; this is the round-trip proof. |
| **CB-7c — Generator: template → C×x86-64×SM-interp.** | Second cell.  Replaces the SM_BB_* handlers in `sm_interp.c`. |
| **CB-7d — Generator: template → C×x86-64×SM-codegen (JIT).** | Third cell.  Replaces the `bb_*_emit_binary` family in `bb_build.c`. |
| **CB-7e — Generator: template → C×x86-64×SM-text-gen (AOT).** | Fourth cell — the new mode.  Emits ahead-of-time C that other backends can adapt. |
| **CB-7f — Generator: template → JS / MSIL / Jasmin / WAT.** | Per-backend emitters, one cell at a time.  Each cell's gate: beauty self-host byte-identical on that (language, backend) pair. |
| **CB-7g — Retire the hand-written bb_*.c.** | Once CB-7b round-trip locks in, the hand-written bb files are deleted; their bytes are re-derivable from templates + generator.  Same for `bb_*_emit_binary` once 7d locks in. |

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

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup (must pass before any port work):
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh        # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh # PASS=49
# Plus: beauty self-host across all three modes byte-identical.
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
for mode in --ir-run --sm-run --jit-run; do
    SNO_LIB=$BEAUTY /home/claude/one4all/scrip $mode \
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
  to today's `--ir-run` output.

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

- **PLAN.md** — Three-milestone authorship agreement. This Goal
  delivers Milestones 2 and 3.
- **GOAL-LANG-SNOBOL4.md** — Milestone 1 (closed session #61).
  CB-3 / CB-4 / CB-5 inherit its done-when invariant.
- **GOAL-LANG-SNOCONE.md, -ICON, -PROLOG, -RAKU, -REBUS** — each
  language's rung-ladder. CB-9 closes by closing each of these
  to its own done-when, plus the beauty self-host invariant.
- **GOAL-NET-BEAUTY-SELF.md** — the .NET self-host work in
  progress. CB-14 absorbs that ladder once the SCRIP-language
  port is the input.
- **GOAL-FULL-INTEGRATION.md** — the parallel-frontend integration
  work. CB-1's mapping audit refines its module boundaries.

---

## Active rung

CB-1 — mapping audit. Output is the lock-in table replacing the
"starting partition" above. Until CB-1 lands, no port work begins.

After CB-1 closes, the natural ordering is:

- CB-2 (boot-host adapter contract) — defines the C ↔ SCRIP-language ABI
- **CB-7a (BB template grammar)** — express today's ~30 boxes as
  templates, before any port begins.  The template grammar is the
  spec for cells CB-7b..g and CB-8a..d; settling it early prevents
  re-shaping after pilots.
- CB-3 (SNOBOL4 frontend pilot) — proven CB-2 boundary contract.
- CB-7b (template → C×x86-64×IR-interp round-trip) — first lock-in
  of the generator.

CB-4 / CB-5 (the big SNOBOL4 runtime ports) follow the lock-ins
above, since they call into the generated bb runtime.

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
  in `one4all`. Decision (deferred): keep the split or merge.
- **Snocone Beauty (GOAL-SNOCONE-BEAUTY)**: Snocone's own
  `beauty.sc` self-host. Once the Snocone frontend ports under
  CB-9, that goal closes by composition.

---

## Authorship

Per PLAN.md three-milestone authorship agreement (amended
session #57): Milestone 2 (CB-11 closure) and Milestone 3 (CB-17
closure) commit messages are written by Claude Sonnet (the active
session). Recorded in PLAN.md when each lands.
