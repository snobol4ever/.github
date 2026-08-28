# FINDING — GOAL-file consolidation: graded census, 71 inputs, 8 clusters, target reachable

Row `goal-files-major-consolidation` · hq_B · survey pass · 2026-08-28

⛔ **This commit deletes nothing and merges nothing.** It is Lon's step (1) — grade every RUNG/STEP
against LIVE source — plus the clustering proposal for steps (2)/(3). Per-cluster landings follow as
their own commits, each carrying its RETIRED NAMES map.

## The instrument, and what it can and cannot say

Every backticked identifier in each GOAL file is checked against an index of **38158** identifiers
extracted from the live tree (`SCRIP/src/**` sources+headers+grammars, `SCRIP/scripts/**`). A cited symbol
absent from that index is counted GONE. Filter: only tokens that look like code (contain `_`, or are
ALL-CAPS, or are camelCase) are counted, so ordinary backticked prose is not scored.

✅ **Validated before use, on three samples.** It discriminates *within* a single file — in `GOAL-CHUNKS.md`
it flags the retired `E_CHOICE`/`E_CUT`/`E_SUSPEND` vocabulary while correctly leaving `SM_ACOMP`,
`SM_PUSH_EXPR`, `EXPR_t` alone as live. That is the behaviour a useful staleness grade needs.

⚠️ **Two limits, stated so nobody over-reads the number.** (1) It conflates *our symbol was retired* with
*never was our symbol* — `ArgumentOutOfRangeException` in the .NET-era files scores GONE, which is true and
is the right conclusion (the doc does not describe this tree) but not a rename. (2) A file citing few
symbols gets a high-variance percentage: 3-of-3 is 100% on a sample of three. **Read `gone` beside `syms`,**
never the percentage alone. Sort order below is percentage, so the small-sample files ride high — that is a
property of the sort, not a finding.

## Census

- GOAL files total: **83**
- Excluded as TARGETS-not-inputs: **5** org + **7** ⭐100 = **12**
- Consolidation INPUTS: **71**
- Inputs whose cited symbols are ≥50% gone: **17** · ≥25% gone: **42**
- Inputs citing ZERO code symbols (pure process/prose): **16**

## Graded census by cluster

### A · the four ports (LIVING roadmap) — 15 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-NET-DATATYPE-LOWERCASE.md` | 54 | 0 | 2 | 2 | 100% |
| `GOAL-NET-OPTIMIZE.md` | 65 | 0 | 1 | 1 | 100% |
| `GOAL-NET-BEAUTY-19.md` | 613 | 0 | 39 | 36 | 92% |
| `GOAL-NET-BEAUTY-SELF.md` | 4967 | 8 | 202 | 162 | 80% |
| `GOAL-TEMPLATES-WASM.md` | 46 | 0 | 5 | 2 | 40% |
| `GOAL-TEMPLATES-NET.md` | 51 | 0 | 3 | 1 | 33% |
| `GOAL-TEMPLATES-JS.md` | 49 | 0 | 4 | 1 | 25% |
| `GOAL-NET-OPSYN-248.md` | 70 | 0 | 0 | 0 | — |
| `GOAL-NET-SNIPPETS.md` | 60 | 0 | 0 | 0 | — |
| `GOAL-README-SNOBOL4ARTIFACT.md` | 79 | 0 | 0 | 0 | — |
| `GOAL-README-SNOBOL4CSHARP.md` | 73 | 0 | 0 | 0 | — |
| `GOAL-README-SNOBOL4DOTNET.md` | 87 | 0 | 0 | 0 | — |
| `GOAL-README-SNOBOL4JVM.md` | 85 | 0 | 0 | 0 | — |
| `GOAL-README-SNOBOL4PYTHON.md` | 73 | 0 | 0 | 0 | — |
| `GOAL-TEMPLATES-JVM.md` | 48 | 0 | 1 | 0 | 0% |

### B · IR/lower redesigns — 12 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-AST-RENAME.md` | 34 | 0 | 4 | 3 | 75% |
| `GOAL-PARSER-PURE-SYNTAX-TREE.md` | 286 | 0 | 16 | 11 | 69% |
| `GOAL-DE-INTERP.md` | 141 | 0 | 35 | 19 | 54% |
| `GOAL-SCRIP-INTERP-SPLIT.md` | 151 | 0 | 46 | 22 | 48% |
| `GOAL-IR-EMITTER-PREREQ.md` | 163 | 0 | 19 | 9 | 47% |
| `GOAL-IR-DEFINE-KIND.md` | 184 | 0 | 13 | 6 | 46% |
| `GOAL-LOWER-REDESIGN.md` | 936 | 0 | 63 | 29 | 46% |
| `GOAL-PARSER-SC-TRANSPILE.md` | 516 | 0 | 57 | 26 | 46% |
| `GOAL-SM-LOWER-REFACTOR.md` | 240 | 0 | 30 | 13 | 43% |
| `GOAL-UNIFIED-BROKER.md` | 380 | 0 | 50 | 20 | 40% |
| `GOAL-IR-IMMUTABLE-EMIT.md` | 1128 | 2 | 342 | 111 | 32% |
| `GOAL-IR-REDESIGN.md` | 213 | 0 | 19 | 5 | 26% |

### C · reorg hygiene — 10 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-SCRIP-RENAME.md` | 136 | 0 | 2 | 1 | 50% |
| `GOAL-RUNTIME-RENAME.md` | 134 | 0 | 58 | 22 | 38% |
| `GOAL-DEAD-CODE-SWEEP.md` | 314 | 0 | 52 | 17 | 33% |
| `GOAL-SRC-REORG.md` | 252 | 0 | 31 | 10 | 32% |
| `GOAL-RUNTIME-REORG.md` | 262 | 0 | 165 | 28 | 17% |
| `GOAL-ARCHIVE-CLEANUP.md` | 233 | 0 | 0 | 0 | — |
| `GOAL-CORPUS-LAYOUT.md` | 1028 | 1 | 3 | 0 | 0% |
| `GOAL-NO-SYMLINKS.md` | 58 | 0 | 0 | 0 | — |
| `GOAL-SELF-CONTAINED-SCRIPTS.md` | 131 | 0 | 11 | 0 | 0% |
| `GOAL-SESSION-SETUP-REFINEMENT.md` | 145 | 1 | 0 | 0 | — |

### D · monitor / SILly — 6 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-SILLY-COMPLETE.md` | 298 | 0 | 69 | 64 | 93% |
| `GOAL-INPROC-MONITOR.md` | 380 | 0 | 25 | 8 | 32% |
| `GOAL-MONITOR-REINSTATE.md` | 36 | 0 | 10 | 0 | 0% |
| `GOAL-SILLY-SWEEP-BACKWARD.md` | 122 | 0 | 0 | 0 | — |
| `GOAL-SILLY-SWEEP-FORWARD.md` | 112 | 0 | 0 | 0 | — |
| `GOAL-SILLY-SYNC-MONITOR.md` | 142 | 0 | 1 | 0 | 0% |

### E · live announce READMEs — 4 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-README-CORPUS.md` | 87 | 0 | 0 | 0 | — |
| `GOAL-README-HARNESS.md` | 88 | 0 | 0 | 0 | — |
| `GOAL-README-PROFILE.md` | 105 | 0 | 0 | 0 | — |
| `GOAL-README-SCRIP.md` | 88 | 0 | 0 | 0 | — |

### F · templates / BB — 4 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-BB-FIXUP.md` | 141 | 0 | 29 | 15 | 52% |
| `GOAL-BB-TEMPLATE-LADDER.md` | 424 | 0 | 109 | 44 | 40% |
| `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` | 43 | 0 | 8 | 0 | 0% |
| `GOAL-TEMPLATES-X86.md` | 52 | 0 | 5 | 0 | 0% |

### G · legacy rewrite era — 8 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-ONE-EVAL.md` | 368 | 0 | 59 | 49 | 83% |
| `GOAL-CHUNKS.md` | 980 | 10 | 78 | 50 | 64% |
| `GOAL-REWRITE-SCRIP.md` | 774 | 0 | 127 | 73 | 57% |
| `GOAL-CHUNKS-STEP17.md` | 1685 | 4 | 150 | 86 | 57% |
| `GOAL-FULL-INTEGRATION.md` | 317 | 0 | 40 | 21 | 52% |
| `GOAL-COMMAND-CENTRAL.md` | 410 | 0 | 148 | 68 | 46% |
| `GOAL-SCRIP-BOOTSTRAP.md` | 1273 | 0 | 42 | 19 | 45% |
| `GOAL-REMOVE-CMPILE.md` | 189 | 0 | 25 | 11 | 44% |

### H · unclustered (per-file calls) — 12 files

| file | lines | RUNG/STEP | syms | gone | %gone |
|---|--:|--:|--:|--:|--:|
| `GOAL-CROSS-LANG-VERIFY.md` | 138 | 0 | 3 | 3 | 100% |
| `GOAL-POLYGLOT-CALC-DEMO.md` | 186 | 0 | 1 | 1 | 100% |
| `GOAL-TEXTF-TEMPLATES.md` | 173 | 0 | 54 | 26 | 48% |
| `GOAL-JCON-IN-SCRIP.md` | 345 | 0 | 113 | 40 | 35% |
| `GOAL-CLI-3MODE.md` | 30 | 0 | 3 | 1 | 33% |
| `GOAL-STCOUNT-ALL-LANGS.md` | 233 | 0 | 12 | 4 | 33% |
| `GOAL-TWO-STEP-HUNT.md` | 156 | 0 | 6 | 2 | 33% |
| `GOAL-RTCC.md` | 146 | 0 | 45 | 10 | 22% |
| `GOAL-MODE34-IDENTICAL.md` | 93 | 0 | 19 | 4 | 21% |
| `GOAL-STYLE-200COL.md` | 179 | 0 | 17 | 3 | 18% |
| `GOAL-OPTIMIZER.md` | 66 | 0 | 11 | 1 | 9% |
| `GOAL-DESCR-TAG-ENCODING.md` | 86 | 1 | 16 | 0 | 0% |

## Arithmetic against the DONE-WHEN bound (≤25)

5 org + 7 ⭐100 = 12 kept by interlock (a). Eight clusters landing as one file each = 8.
Interlock (e) protects the live announce rows `GOAL-README-CORPUS` and `GOAL-README-SCRIP` from absorption, so
cluster E lands as 2 protected + 1 merged rather than 1. **12 + 8 + 2 = 22 ≤ 25.** The mint-time bound is
reachable without forcing a merge that interlock (e) forbids; I am not amending it.

## Dispositions proposed (per-cluster landings, each its own commit)

- **A · the four ports** — ⛔⭐ **CORRECTED 2026-08-28, SAME DAY, BEFORE ANY LANDING: THIS IS LIVING
  ROADMAP, NOT A DORMANT ERA.** Lon, in-chat to CEO: *"the plan is to port to JVM, .NET, JavaScript, and
  Web Assembly."* My first pass proposed one archive landing "under the x86-only ruling" and that
  disposition is **VOID** — as was the mint's identical wording. Surviving port design content routes to a
  **LIVING ⭐100 home** (`GOAL-PORTS-100` suggested), never the archive. ⭐ The staleness numbers below are
  unchanged and still honest — these files DO cite symbols absent from this tree — but **high staleness in a
  roadmap means the design was never built, not that it was abandoned.** That is the second inversion in
  this census, and it is the more dangerous one: the first (a reorg doc naming what it killed) makes a live
  doc look dead; this one would have let a measured number retire a plan Lon had just affirmed. **A
  staleness grade measures distance from the tree, never intent** — and only a human pass can tell which
  direction that distance points.
- **B · IR/lower redesigns** — mixed: living design ideas here route INTO the owning ⭐100 files per step (2)
  before the remainder archives. ⛔ Merit calls that touch semantics are the reserved class — ASSIGNED asks,
  never dropped, per the reserved-question law.
- **C · reorg hygiene** — mostly LANDED work describing completed moves. ⚠️ `GOAL-SRC-REORG.md` carries the
  most retired-home citations in the corpus (11) and that is CORRECT: it documents the move that retired
  them. **Do not grade a reorg doc stale for naming what it retired** — this is the one place the
  instrument's signal inverts, and it is why the survey is a human pass and not a script.
- **D · monitor / SILly** — the monitor is not deprecated as a tool but is no longer a mandated step;
  consolidate to one file recording what survives.
- **E · live announce READMEs** — `CORPUS` and `SCRIP` are NOT absorbed (interlock e).
- **F · templates / BB** · **G · legacy rewrite era** · **H · unclustered** — H is deliberately not forced
  into a cluster; each is a per-file call in its own landing.

## What this survey does NOT settle

Per-file merit calls inside clusters B/F/G/H. Those are step (2) and they are the slow half. Nothing in
this document authorizes a deletion; every landing needs its RETIRED NAMES map and the same-landing citation
sweep across RULES.md, PLAN.md, the CLAUDE.md digests and the postoffice task files (interlocks b and c).
