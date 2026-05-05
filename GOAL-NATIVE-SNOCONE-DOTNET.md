# GOAL-NATIVE-SNOCONE-DOTNET.md — extend the in-tree .NET host to run Snocone

**Repo:** one4all (only) — code lives in `src/driver/net/`
**Branch:** TBD (likely a feature branch off `main` until M3-DOTNET ships)
**Tracker:** brand-new sub-goal carved out of GOAL-CHUNKS.md
Step 9 (session #62, 2026-05-05).

**Done when:** the in-tree .NET SNOBOL4 host (`src/driver/net/`,
the C# `scrip-interp` project) parses and runs Snocone source
files (`.sc`). `scrip.sc` runs end-to-end on the .NET interpreter
and produces output matching `scrip --sm-run scrip.sc` against
the same input. Provides **bootstrap path B** for `scrip.sc` —
independent of the SCRIP host process.

---

## Where the code is — verified session #62

The .NET tree-walk SNOBOL4 host already exists inside one4all:

```
one4all/src/driver/net/
    Program.cs           — entry point; usage: dotnet run -- <file.sno>
    Snobol4Parser.cs     — parses .sno into an IR tree
    Ast.cs / IrNode.cs   — IR shape (matches scrip-cc IR)
    Executor.cs          — tree-walk interpreter
    PatternBuilder.cs    — builds Byrd-box patterns
    BoxFactory.cs        — Reflection.Emit-time box compilation
    SnobolEnv.cs         — runtime environment / NV table
    scrip-interp.csproj  — project file
```

Compiled-target runtime in `src/runtime/net/` (different thing —
that's what `scrip-cc -net` emitted binaries link against; this
goal does NOT touch that).

⛔ **This is not the same as the separate `snobol4dotnet` org
repo.** That repo is Jeffrey Cooper's standalone C# SNOBOL4/SPITBOL
runtime. This goal is exclusively about `one4all/src/driver/net/`.

---

## Why this file exists

GOAL-CHUNKS.md Step 9 (M3) calls for extending the .NET native
SNOBOL4 host to handle Snocone, providing one of three
independent bootstrap paths for `scrip.sc`. Sister files:
GOAL-NATIVE-SNOCONE-JVM.md (`src/driver/jvm/`),
GOAL-NATIVE-SNOCONE-JS.md (`src/driver/js/`).

---

## Architectural target

**Snocone is a SNOBOL4 superset** in pattern-matching idiom and
runtime semantics, but adds Snocone-specific syntax (the
`Tree(...)`, `Shift(...)`, `Reduce(...)` family, `.` vs `$`
capture rules formalized in SNOBOL4-SNOCONE-PRIMER.md, plus
function/struct/operator definitions). The key insight: Snocone
programs lower to the same IR shape as SNOBOL4 — `polyglot.c`'s
fence parser tags Snocone statements as `LANG_SNO`, and
`sm_lower`'s LANG_SNO entry already handles them.

**For `src/driver/net/`, this means:** the existing C# tree-walk
runtime (Executor.cs, BoxFactory.cs, SnobolEnv.cs) needs no
semantic changes. What's needed is a Snocone parser path that
produces the same IR shape `Executor.cs` already consumes.

**Two viable paths:**

1. **Port `parser_snocone.sc` to C#.** Direct port of the parser
   currently being landed in GOAL-PARSER-SNOCONE into idiomatic
   C#, alongside `Snobol4Parser.cs`. Pros: self-contained, no
   SCRIP runtime dependency. Cons: must keep the C# parser in
   sync with the SNOBOL4-source-of-truth `parser_snocone.sc`.

2. **Run `parser_snocone.sc` itself on this .NET host.** The .NET
   host already runs SNOBOL4; if `parser_snocone.sc` runs
   correctly on it, the parser is a single artifact across all
   bootstrap paths. Pros: single source of truth. Cons: depends
   on `parser_snocone.sc` being SNOBOL4-only, and on this host's
   SNOBOL4 conformance covering everything the parser uses.

**Recommendation:** path 2, deferring to path 1 only if specific
SNOBOL4 conformance gaps surface. Lon decides in DN-1.

---

## Prerequisite

⛔ **Do not start this goal until GOAL-PARSER-SNOCONE has reached
the beauty.sc crosscheck (PARSER-SC-6b).** Without a working
`parser_snocone.sc`, this goal has nothing to port or run.

This goal is **independent of GOAL-CHUNKS** — `src/driver/net/`
is its own tree-walk runtime and isn't touched by the
SM_PUSH_EXPR migration. M3-DOTNET can run in parallel with
CHUNKS M2/M4/M5 or ahead of M2.

---

## Migration strategy

**Sequential rungs, scoped from smallest Snocone program to
`scrip.sc` itself.** Each rung adds Snocone surface-area coverage
and re-runs the matching corpus subset.

**Per-rung gates** (apply unless the step says otherwise):

```
existing src/driver/net/ tests PASS
SNOBOL4 conformance: existing .sno corpus subset that runs on
                     this host today must keep running
Snocone smoke ×5  (initially failing; passes incrementally)
Snocone corpus subset PASS for the rung's coverage
```

⛔ The SNOBOL4 conformance gate must remain green throughout.

---

## Steps (execute one per session, sequentially)

- [ ] **Step DN-1 — Survey + parser-path decision.**
  Read every file in `src/driver/net/`. Confirm: how does
  Executor.cs walk IR? what does Snobol4Parser.cs emit? where
  is the entry point that decides what file extension routes
  through which parser? Decide path 1 vs path 2. Document in
  `docs/NATIVE-SNOCONE-DOTNET-step01-survey.md`. No code change.

- [ ] **Step DN-2 — Wire `.sc` extension recognition.**
  Smallest change: Program.cs accepts `.sc` files and routes them
  through whatever Snocone path DN-1 chose. For path 2, this rung
  also validates that `parser_snocone.sc` runs on this host
  without crashing — it may legitimately fail to parse Snocone
  yet, but it must not crash. Gate: a smallest-Snocone program
  parses to the right IR shape.

- [ ] **Step DN-3 — Tree-shape parity gate vs SCRIP host.**
  Run the parser-Snocone tree-shape oracle on this host's parser
  output. Gate: tree shapes match for the PARSER-SC corpus subset
  (currently PASS=46 per PLAN.md).

- [ ] **Step DN-4 — Snocone smoke 5/5.**  The five smoke_snocone
  programs run end-to-end on `src/driver/net/`. Output matches
  `scrip --sm-run` exactly.

- [ ] **Step DN-5 — Snocone corpus subset.**  Pick a curated
  subset of corpus Snocone programs (~10–20) that exercise the
  Snocone surface area `scrip.sc` itself uses. All pass.
  Document in `docs/NATIVE-SNOCONE-DOTNET-step05-corpus.md`.
  Use the same subset as JV-5 / JS-5 wherever possible — the
  three M3 hosts should converge on a single bootstrap-coverage
  suite.

- [ ] **Step DN-6 — `scrip.sc` runs end-to-end.**
  `dotnet run --project src/driver/net -- scrip.sc < beauty.sno`
  produces output identical to `scrip --sm-run scrip.sc <
  beauty.sno`. M3-DOTNET milestone close.

- [ ] **Step DN-7 — Package + docs.**
  Document the .NET bootstrap path. Update REPO-one4all.md if it
  surveys the driver subtrees. Update GOAL-CHUNKS.md Step 9 to
  `[x]`. Update PLAN.md current step.

---

## Closed steps

(none yet — this goal is brand new)

---

## Definitions

- **bootstrap path B** — running `scrip.sc` on the in-tree .NET
  SNOBOL4 host (`src/driver/net/`), independent of the SCRIP
  host process. Path A is scrip-on-scrip (after CHUNKS M1).
  Paths C and D are JVM and JS in their respective goal files.

- **the in-tree .NET host** — `src/driver/net/` inside one4all.
  Distinct from the standalone `snobol4dotnet` org repo, which
  is Jeffrey Cooper's separate C# SNOBOL4 implementation.

- **path 1 / path 2** — parser-implementation choices in DN-1.
  Path 1 ports `parser_snocone.sc` to C#; path 2 runs the
  `.sc` parser on the existing C# SNOBOL4 host.

---

## Watermark

Goal stub written 2026-05-05 in session #62, lifted from
GOAL-CHUNKS.md Step 9. No rungs started yet. Awaiting
GOAL-PARSER-SNOCONE PARSER-SC-6b close before DN-1 may begin.
