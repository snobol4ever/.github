# GOAL-SCRIP-BOOTSTRAP.md — SCRIP self-hosts everywhere

**Repo:** one4all (primary), snobol4dotnet, snobol4jvm, snobol4js (new),
snobol4wasm (new)

**Done when:** SCRIP — the compiler / interpreter / runtime currently
written as ~82,000 lines of C and headers in `one4all/src/` —
re-emits itself in the SCRIP language family (SNOBOL4, Snocone, Icon,
Prolog, Raku, Rebus) such that:

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

| C area | LoC | Target language | Why |
|--------|----:|-----------------|-----|
| `src/frontend/snobol4/` | 9,339 | **SNOBOL4** | Lexer/parser for SNOBOL4 in SNOBOL4 — the classic self-host. Bison/Flex → hand-written SNOBOL4 patterns. |
| `src/frontend/snocone/` | 2,921 | **Snocone** | Frontend in its own language (boot via SNOBOL4 if cyclic). |
| `src/frontend/icon/` | 3,867 | **Icon** | Same self-pattern. |
| `src/frontend/prolog/` | 4,715 | **Prolog** | Same self-pattern. |
| `src/frontend/raku/` | 8,912 | **Raku** | Same self-pattern. |
| `src/frontend/rebus/` | 7,176 | **Rebus** | Same self-pattern. |
| `src/ir/` | 960 | **Snocone** | IR walking is data-pipeline work; Snocone's gather/take fits cleanly. |
| `src/runtime/x86/bb_*.c` | ~7,000 | **Icon** | Pattern boxes are Icon's BB_PUMP generators in essence. |
| `src/runtime/x86/sm_lower.c, sm_interp.c` | ~3,000 | **Prolog** | Stack-machine lowering is term rewriting; Prolog clauses fit. |
| `src/runtime/x86/sm_codegen.c` | ~2,000 | **C / Raku** | Codegen stays C on x86-64 (machine-code emit); future backends emit their host's bytecode/IR. |
| `src/runtime/x86/snobol4*.c, name_t.c` | ~6,000 | **SNOBOL4** | Runtime support for SNOBOL4 in SNOBOL4. |
| `src/runtime/x86/eval_code.c` | ~900 | **Snocone** | Expression evaluator. |
| `src/driver/interp.c` | 4,500+ | **SNOBOL4** | Top-level tree-walk; biggest single piece. |
| `src/driver/scrip.c, polyglot.c, sync_monitor.c` | ~2,300 | **SNOBOL4** | Driver glue. |

The mapping above is a **starting partition**, not a contract.
Sub-rung CB-1 (below) revisits it after the first frontend port lands
and we have data on which boundaries hold up under real porting.

**Self-host cycle:** SNOBOL4's frontend in SNOBOL4 needs the SCRIP
runtime to run; the SCRIP runtime in SNOBOL4 needs SNOBOL4's frontend
to compile. Break the cycle the standard way — Stage-1 (the existing
C binary) compiles all six frontends from their SCRIP-language
sources in one pass, **then** Stage-1 runs the resulting program to
produce Stage-2. No partial bootstraps; no hand-translated
intermediates that age out.

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

- [ ] **CB-7 — bb_boxes.c, bb_broker.c → Icon.**
  Pattern boxes ARE Icon generators. The mapping is the most
  natural in the table. **Gate:** every bb_* unit test passes
  with the Icon-language box implementations replacing the C ones.
  Smoke=7, Broker=49 invariant.

- [ ] **CB-8 — sm_lower.c, sm_interp.c → Prolog.**
  Stack-machine lowering as term rewriting. **Gate:** `--sm-run`
  byte-identical to today.

- [ ] **CB-9 — Snocone, Icon, Prolog, Raku, Rebus frontends.**
  Each language's frontend, in itself. CB-3 establishes the
  pattern; CB-9 is "do that five more times". Each ladder is
  gated by its existing GOAL-LANG-* file's done-when, plus the
  beauty self-host invariant.

- [ ] **CB-10 — sm_codegen.c → C (kept) / Raku (planned).**
  Machine-code emission stays C on x86-64 because libgc and
  `mmap(PROT_EXEC)` are C calls; the Raku port is for Milestone 3
  (other backends, where "machine code" is JVM bytecode / .NET
  IL / WASM / JS). On x86-64 this rung's Done-when is just "the
  C remains, cleanly bounded by CB-2's adapter contract".

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
