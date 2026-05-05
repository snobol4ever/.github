# GOAL-NATIVE-SNOCONE-JS.md — extend the in-tree JS host to run Snocone

**Repo:** one4all (only) — code lives in `src/driver/js/`
**Branch:** TBD (likely a feature branch off `main` until M3-JS ships)
**Tracker:** brand-new sub-goal carved out of GOAL-CHUNKS.md
Step 11 (session #62, 2026-05-05).

**Done when:** the in-tree JS SNOBOL4 host (`src/driver/js/sno-interp.js`)
parses and runs Snocone source files (`.sc`). `scrip.sc` runs
end-to-end on Node and produces output matching `scrip --sm-run
scrip.sc` against the same input. Provides **bootstrap path D**
for `scrip.sc` — independent of the SCRIP host process and of
the in-tree .NET / JVM hosts.

---

## Where the code is — verified session #62

The JS tree-walk SNOBOL4 host already exists inside one4all:

```
one4all/src/driver/js/
    sno-interp.js        — tree-walk interpreter (1630 lines)
                           pure JS, builds same IR shape as scrip-cc,
                           uses sno_engine.js for patterns
```

The interpreter loads two runtime files at startup (currently
from `src/runtime/js/`):

```
one4all/src/runtime/js/
    sno_runtime.js       — primitive operations, _vars Proxy,
                           _FAIL sentinel
    sno_engine.js        — pattern match engine (Greek-variable
                           state machine, Clojure match.clj model)
    bb_boxes.js          — Byrd-box JS implementations (used by
                           emit_js.c output, not by sno-interp.js
                           directly)
```

⛔ **There is no separate snobol4js org repo** (verified via
GitHub API session #62 — the only org repos are .github, corpus,
csnobol4, harness, one4all, snobol4artifact, snobol4csharp,
snobol4dotnet, snobol4jvm, snobol4python, x32, x64). The JS host
exists ONLY at `one4all/src/driver/js/sno-interp.js`.

---

## Why this file exists

GOAL-CHUNKS.md Step 11 (M3) calls for extending the JS native
SNOBOL4 host to handle Snocone, providing one of three
independent bootstrap paths for `scrip.sc`. Sister files:
GOAL-NATIVE-SNOCONE-DOTNET.md (`src/driver/net/`),
GOAL-NATIVE-SNOCONE-JVM.md (`src/driver/jvm/`).

JS has its own platform considerations (Node-only at present,
no browser support yet) that warrant a separate goal file.

---

## Architectural target

Same architectural framing as DOTNET / JVM siblings — Snocone is
a SNOBOL4 superset that lowers to the same IR shape SNOBOL4 does,
so the JS host's runtime needs no semantic changes; what's needed
is a Snocone parser path that produces the IR shape sno-interp.js
already consumes.

**Two viable paths** (mirror of DOTNET/JVM):

1. **Port `parser_snocone.sc` to JS.** Direct port alongside
   the existing parser inside sno-interp.js. Pros: self-contained.
   Cons: parallel parser to keep in sync.

2. **Run `parser_snocone.sc` itself on this JS host.** Single
   source of truth. Cons: depends on `parser_snocone.sc` being
   SNOBOL4-only, and on this host's SNOBOL4 conformance covering
   everything the parser uses.

**Recommendation:** path 2 if this host's SNOBOL4 conformance is
solid; path 1 is more attractive here than for DOTNET/JVM
because shipping a small standalone Snocone parser to a browser
demo is genuinely useful (a future browser stage). Lon decides
in JS-1.

**Node vs browser.** Currently sno-interp.js is Node-only — it
uses `require`, `process.stdout`, `fs`. Adding browser support
(in-memory file system shim, async-loaded source) is **out of
scope** for this goal — file it as a follow-on if wanted. M3-JS
ships when Node passes; browser is a separate goal.

---

## Prerequisite

⛔ **Do not start this goal until GOAL-PARSER-SNOCONE has reached
the beauty.sc crosscheck (PARSER-SC-6b).** Without a working
`parser_snocone.sc`, this goal has nothing to port or run.

This goal is **independent of GOAL-CHUNKS** — sno-interp.js is
its own tree-walk runtime and isn't touched by the SM_PUSH_EXPR
migration. M3-JS can run in parallel with CHUNKS M2/M4/M5 or
ahead of M2, and in parallel with M3-DOTNET / M3-JVM.

---

## Migration strategy

**Sequential rungs, scoped from smallest Snocone program to
`scrip.sc` itself.** Each rung adds Snocone surface-area coverage
and re-runs the matching corpus subset.

**Per-rung gates** (apply unless the step says otherwise):

```
Node smoke PASS (existing sno-interp.js test invocations from
                 test_invariants_3x3_harness.sh and friends)
SNOBOL4 conformance: existing .sno corpus subset that runs on
                     this host today must keep running
Snocone smoke ×5 in Node  (initially failing; passes
                            incrementally per rung)
Snocone corpus subset PASS for the rung's coverage
```

⛔ The SNOBOL4 conformance gate must remain green throughout.

---

## Steps (execute one per session, sequentially)

- [ ] **Step JS-1 — Survey + parser-path decision.**
  Read sno-interp.js end-to-end. Confirm: how is the IR walked?
  What does the existing in-file parser emit? Where is the file-
  extension dispatch point? Decide path 1 vs path 2. Document in
  `docs/NATIVE-SNOCONE-JS-step01-survey.md`. No code change.

- [ ] **Step JS-2 — Wire `.sc` extension recognition.**
  Smallest change: sno-interp.js accepts `.sc` files and routes
  them through whatever Snocone path JS-1 chose. For path 2,
  validate that `parser_snocone.sc` runs on this host without
  crashing. Gate: smallest-Snocone program parses to the right
  IR shape.

- [ ] **Step JS-3 — Tree-shape parity gate vs SCRIP host.**
  Run the parser-Snocone tree-shape oracle on this host's
  parser output. Gate: tree shapes match for the PARSER-SC
  corpus subset (currently PASS=46 per PLAN.md).

- [ ] **Step JS-4 — Snocone smoke 5/5 in Node.**  Five
  smoke_snocone programs run end-to-end on sno-interp.js via
  Node. Output matches `scrip --sm-run` exactly.

- [ ] **Step JS-5 — Snocone corpus subset.**  Same curated
  subset as DN-5 / JV-5 wherever possible. All pass in Node.
  Document in `docs/NATIVE-SNOCONE-JS-step05-corpus.md`.

- [ ] **Step JS-6 — `scrip.sc` runs end-to-end (Node).**
  `node src/driver/js/sno-interp.js scrip.sc < beauty.sno`
  produces output identical to `scrip --sm-run scrip.sc <
  beauty.sno`. M3-JS milestone close.

- [ ] **Step JS-7 — Package + docs.**
  Document the JS bootstrap path: Node version support, how to
  invoke. Update REPO-one4all.md if it surveys the driver
  subtrees. Update GOAL-CHUNKS.md Step 11 to `[x]`. Update
  PLAN.md current step.

---

## Closed steps

(none yet — this goal is brand new)

---

## Definitions

- **bootstrap path D** — running `scrip.sc` on the in-tree JS
  SNOBOL4 host (`src/driver/js/sno-interp.js`), independent of
  the SCRIP host process. Path A is scrip-on-scrip (after CHUNKS
  M1). Paths B and C are .NET and JVM in their respective goal
  files.

- **the in-tree JS host** — `src/driver/js/sno-interp.js` inside
  one4all. There is no separate snobol4js org repo; this file
  is the canonical JS SNOBOL4 host.

- **path 1 / path 2** — parser-implementation choices in JS-1.
  Path 1 ports `parser_snocone.sc` to JS; path 2 runs the
  `.sc` parser on the existing JS SNOBOL4 host.

---

## Watermark

Goal stub written 2026-05-05 in session #62, lifted from
GOAL-CHUNKS.md Step 11. No rungs started yet. Awaiting
GOAL-PARSER-SNOCONE PARSER-SC-6b close before JS-1 may begin.
