# GOAL-NATIVE-SNOCONE-JVM.md — extend the in-tree JVM host to run Snocone

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

**Repo:** one4all (only) — code lives in `src/driver/jvm/`
**Branch:** TBD (likely a feature branch off `main` until M3-JVM ships)
**Tracker:** brand-new sub-goal carved out of GOAL-CHUNKS.md
Step 10 (session #62, 2026-05-05).

**Done when:** the in-tree JVM SNOBOL4 host (`src/driver/jvm/`,
written in **Java**) parses and runs Snocone source files
(`.sc`). `scrip.sc` runs end-to-end on the JVM interpreter and
produces output matching `scrip --interp scrip.sc` against the
same input. Provides **bootstrap path C** for `scrip.sc` —
independent of the SCRIP host process and of the in-tree .NET / JS
hosts.

---

## Where the code is — verified session #62

The JVM tree-walk SNOBOL4 host already exists inside one4all,
written in **Java** (not Clojure or Kotlin):

```
one4all/src/driver/jvm/
    Lexer.java           — single-pass lexer
    Parser.java          — recursive-descent parser → IR
    Interpreter.java     — tree-walk interpreter (1575 lines)
    PatternBuilder.java  — builds Byrd-box patterns
    TestLexer.java       — lexer test harness
    TestParser.java      — parser test harness
```

Compiled-target Jasmin runtime in `src/runtime/jvm/`
(`bb_boxes.j`, `jvm_linkage.j`) — different thing, that's what
`scrip-cc -jvm` emitted code links against. This goal does NOT
touch that.

⛔ **This is not the same as the separate `snobol4jvm` org
repo.** That repo is a Clojure-based SNOBOL4/SPITBOL host. This
goal is exclusively about `one4all/src/driver/jvm/`, which is
Java.

---

## Why this file exists

GOAL-CHUNKS.md Step 10 (M3) calls for extending the JVM native
SNOBOL4 host to handle Snocone, providing one of three
independent bootstrap paths for `scrip.sc`. Sister files:
GOAL-NATIVE-SNOCONE-DOTNET.md (`src/driver/net/`),
GOAL-NATIVE-SNOCONE-JS.md (`src/driver/js/`).

---

## Architectural target

Same architectural framing as GOAL-NATIVE-SNOCONE-DOTNET.md —
Snocone is a SNOBOL4 superset that lowers to the same IR shape
SNOBOL4 does, so the JVM host's runtime needs no semantic
changes; what's needed is a Snocone parser path that produces
the IR shape `Interpreter.java` already consumes.

**Two viable paths** (mirror of DOTNET):

1. **Port `parser_snocone.sc` to Java.** Direct port alongside
   `Parser.java`. Pros: self-contained. Cons: parallel parser
   to keep in sync.

2. **Run `parser_snocone.sc` itself on this JVM host.** Single
   source of truth across bootstrap paths. Cons: depends on
   `parser_snocone.sc` being SNOBOL4-only, and on this host's
   SNOBOL4 conformance covering everything the parser uses.

**Recommendation:** path 2, deferring to path 1 only if specific
SNOBOL4 conformance gaps surface. Lon decides in JV-1.

---

## Prerequisite

⛔ **Do not start this goal until GOAL-PARSER-SNOCONE has reached
the beauty.sc crosscheck (PARSER-SC-6b).** Without a working
`parser_snocone.sc`, this goal has nothing to port or run.

This goal is **independent of GOAL-CHUNKS** — `src/driver/jvm/`
is its own tree-walk runtime and isn't touched by the
SM_PUSH_EXPR migration. M3-JVM can run in parallel with CHUNKS
M2/M4/M5 or ahead of M2, and in parallel with M3-DOTNET / M3-JS.

---

## Migration strategy

**Sequential rungs, scoped from smallest Snocone program to
`scrip.sc` itself.** Each rung adds Snocone surface-area coverage
and re-runs the matching corpus subset.

**Per-rung gates** (apply unless the step says otherwise):

```
existing src/driver/jvm/ tests PASS (TestLexer + TestParser at
                                     minimum)
SNOBOL4 conformance: existing .sno corpus subset that runs on
                     this host today must keep running
Snocone smoke ×5  (initially failing; passes incrementally)
Snocone corpus subset PASS for the rung's coverage
```

⛔ The SNOBOL4 conformance gate must remain green throughout.

---

## Steps (execute one per session, sequentially)

- [ ] **Step JV-1 — Survey + parser-path decision.**
  Read every file in `src/driver/jvm/`. Confirm: how does
  Interpreter.java walk IR? what does Parser.java emit? where
  is the entry point? Survey the build pipeline (Maven? Gradle?
  raw javac?). Decide path 1 vs path 2. Document in
  `docs/NATIVE-SNOCONE-JVM-step01-survey.md`. No code change.

- [ ] **Step JV-2 — Wire `.sc` extension recognition.**
  Smallest change: the Java entry point accepts `.sc` files and
  routes them through whatever Snocone path JV-1 chose. For path
  2, validate that `parser_snocone.sc` runs on this host without
  crashing — it may legitimately fail to parse Snocone yet, but
  must not crash. Gate: smallest-Snocone program parses to the
  right IR shape.

- [ ] **Step JV-3 — Tree-shape parity gate vs SCRIP host.**
  Run the parser-Snocone tree-shape oracle on this host's
  parser output. Gate: tree shapes match for the PARSER-SC
  corpus subset (currently PASS=46 per PLAN.md).

- [ ] **Step JV-4 — Snocone smoke 5/5.**  Five smoke_snocone
  programs run end-to-end on `src/driver/jvm/`. Output matches
  `scrip --interp` exactly.

- [ ] **Step JV-5 — Snocone corpus subset.**  Same curated
  subset as DN-5 / JS-5 wherever possible. All pass. Document
  in `docs/NATIVE-SNOCONE-JVM-step05-corpus.md`.

- [ ] **Step JV-6 — `scrip.sc` runs end-to-end.**
  Invoking the JVM host on `scrip.sc` produces output identical
  to `scrip --interp scrip.sc < beauty.sno`. M3-JVM milestone
  close.

- [ ] **Step JV-7 — Package + docs.**
  Document the JVM bootstrap path: how to build, how to invoke,
  Java version support. Update REPO-one4all.md if it surveys
  the driver subtrees. Update GOAL-CHUNKS.md Step 10 to `[x]`.
  Update PLAN.md current step.

---

## Closed steps

(none yet — this goal is brand new)

---

## Definitions

- **bootstrap path C** — running `scrip.sc` on the in-tree JVM
  SNOBOL4 host (`src/driver/jvm/`), independent of the SCRIP
  host process. Path A is scrip-on-scrip (after CHUNKS M1).
  Paths B and D are .NET and JS in their respective goal files.

- **the in-tree JVM host** — `src/driver/jvm/` inside one4all,
  written in Java. Distinct from the standalone `snobol4jvm`
  org repo, which is Clojure.

- **path 1 / path 2** — parser-implementation choices in JV-1.
  Path 1 ports `parser_snocone.sc` to Java; path 2 runs the
  `.sc` parser on the existing Java SNOBOL4 host.

---

## Watermark

Goal stub written 2026-05-05 in session #62, lifted from
GOAL-CHUNKS.md Step 10. No rungs started yet. Awaiting
GOAL-PARSER-SNOCONE PARSER-SC-6b close before JV-1 may begin.
