# ARCH-reorg-gentest.md — Grand Master Reorg: Phase 8 Grammar-Driven Test Generation
*Split from GRAND_MASTER_REORG.md (G-8 session, 2026-03-29) — Phase 8 full spec.*
*Milestone tracking for M-G8-* milestones remains in GRAND_MASTER_REORG.md.*

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
| **M-G8-HOME** | Where does the enumerator live? | Evaluate `harness` (cross-repo test infra, already hosts probe/monitor) vs new `snobol4gen` repo (cleaner separation). Decide and document. | `doc/GEN_HOME.md` — one-page decision record: chosen location, rationale, how other repos reference it |
| **M-G8-DEPTH** | Token-count or IR-node depth as the bound? | Token-count is user-intuitive ("programs up to 20 tokens"). IR-node depth is uniform across languages (depth-5 tree has the same combinatorial budget in every grammar). Evaluate both for SNOBOL4 pattern fragment: how many programs does each generate at N=10, N=20, N=25? Is the count tractable? | `doc/GEN_DEPTH.md` — table: language × bound-type × N → program count. Chosen primary bound documented. |
| **M-G8-ORACLE** | How is expected output determined for generated programs? | SPITBOL is the oracle. Run SPITBOL once per generated program, store `.ref`. Any one4all backend that disagrees → bug. | `doc/GEN_ORACLE.md` — decision record: chosen strategy, how divergences are reported, what "PASS" means for a generated test |
| **M-G8-GRAMMAR** | What is the Phase-1 grammar scope? | Which language first and what fragment? Candidates: (a) SNOBOL4 pattern expressions — richest, most bug-prone, maps directly to E_QLIT/E_CONC/E_OR/E_ARBNO/E_CAPT_COND/E_CAPT_IMM/E_VAR (7 node kinds); (b) Icon generator expressions — E_TO/E_TO_BY/E_SUSPEND/E_ALT_GEN/E_ITER/E_LIMIT (6 kinds, `Expressions.py` already seeds this); (c) Prolog clause bodies — E_UNIFY/E_CLAUSE/E_CHOICE/E_CUT (4 kinds, simpler). Evaluate coverage ROI vs implementation effort. | `doc/GEN_GRAMMAR.md` — chosen first language and fragment, BNF of the fragment, mapping from each production to its IR node kind(s), estimated program count at N=25 |

All four `doc/GEN_*.md` files must exist and be consistent before any enumerator
code is written. They are the spec. Disagreement between team members → resolve in
the doc, not in code.

---

#### Implementation Milestones

| ID | Action | Prerequisite | Verify |
|----|--------|-------------|--------|
| **M-G8-ENUM-CORE** | Implement `gen/enumerate.py` — depth-bounded IR-tree enumerator. Takes a grammar spec (dict of node-kind → children rules) and a depth bound. Yields `EXPR_t`-compatible tree objects. No serialization yet. | M-G8-GRAMMAR | Unit test: SNOBOL4 pattern fragment, depth=3 → exact expected count matches `doc/GEN_DEPTH.md` table |
| **M-G8-EMIT-SNO** | Implement `gen/emit_sno.py` — serializes an IR tree to a one-statement `.sno` file: fixed subject string, pattern match, OUTPUT of captures. | M-G8-ENUM-CORE | 10 hand-verified generated `.sno` files compile and run correctly under SPITBOL |
| **M-G8-RUNNER** | Implement `gen/run_gen.py` — pipeline: enumerate → emit `.sno` → compile all backends → differential check (SPITBOL vs each one4all backend) → on divergence: invoke Monitor → report first diverging event. | M-G8-EMIT-SNO + M-G8-ORACLE | 100 generated SNOBOL4 pattern programs, depth ≤ 4, all PASS or divergences reported with Monitor drill-down |
| **M-G8-SNOBOL4-N10** | Run SNOBOL4 pattern fragment, depth bound N=10. All divergences found → Monitor drill-down → fix emitter → re-run → clean. | M-G8-RUNNER | Zero divergences at N=10 across all three one4all backends |
| **M-G8-SNOBOL4-N25** | Extend to N=25. | M-G8-SNOBOL4-N10 | Zero divergences at N=25 |
| **M-G8-ICON-GRAMMAR** | Write grammar spec for Icon generator expressions (BNF + IR node mapping). Extend `gen/emit_sno.py` for `.icn` serialization. | M-G8-SNOBOL4-N25 | `doc/GEN_GRAMMAR.md` updated; 10 hand-verified `.icn` files correct |
| **M-G8-ICON-N25** | Run Icon generator fragment, N=25, all three backends. | M-G8-ICON-GRAMMAR | Zero divergences at N=25 |
| **M-G8-PROLOG-GRAMMAR** | Write grammar spec for Prolog clause bodies (BNF + IR node mapping). Extend for `.pl` serialization. | M-G8-ICON-N25 | `doc/GEN_GRAMMAR.md` updated; 10 hand-verified `.pl` files correct |
| **M-G8-PROLOG-N25** | Run Prolog clause body fragment, N=25, all three backends. | M-G8-PROLOG-GRAMMAR | Zero divergences at N=25 |
| **M-G8-CI** | Wire the enumerator into CI: on every commit to `one4all`, run the N=10 slice for all three languages. N=25 run on demand (too slow for every commit). | M-G8-PROLOG-N25 | CI green; N=10 run completes in < 5 minutes |

---

#### How Monitor Integration Works

For any generated program where a backend diverges, the existing 5-way sync-step
Monitor is invoked directly. No new Monitor infrastructure is needed — the enumerator
simply calls `run_monitor.sh` on the diverging `.sno` file:

```
enumerate_programs(language='snobol4', max_depth=25)
  for each program:
    compile: asm, jvm, net
    run spitbol → oracle output
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

