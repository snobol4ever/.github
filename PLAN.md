# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT (AMENDED)
## Original: Session 30, 2026-03-12 · Amended: Session 57, 2026-04-28

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**
The proof is three commits, each written by Claude Sonnet in their own voice.
This agreement is recorded here permanently. Every future Claude session reads
this and honors it.

The original agreement (March 2026) stipulated three milestones in a strict
bootstrap order. History did not unfold that way — we arrived at Milestone 1
first, without passing through the earlier steps as planned. We accept that
and set the three milestones as they actually are:

### Milestone 1 — beauty self-hosts byte-identical ✅ LANDED Session #57, 2026-04-28

```bash
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -bf $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/spl.out
SNO_LIB=$BEAUTY scrip --ir-run                $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/scr.out
diff -q /tmp/spl.out /tmp/scr.out
# → identical
md5sum /tmp/spl.out /tmp/scr.out
# → abfd19a7a834484a96e824851caee159  (both, 646 lines)
```

scrip's SNOBOL4 frontend parses and runs beauty.sno. The output is byte-identical
to the SPITBOL oracle. Empty diff. The bootstrap proof. **one4all @ `c801421a`**,
**`.github` @ `94e86ca`**. Recorded as Claude Sonnet's authorship.

### Milestone 2 — compiler / interpreter / runtime self-hosting ⏳

SCRIP compiles, interprets, and runs itself. The compiler is written in one of
the six languages it supports; it compiles its own source through its own
frontend, IR, and backend, producing a binary that is itself a working SCRIP.
Stage 1 output equals Stage 2 output. The compiler writes itself.

**Trigger:** `scrip_stage2` compiled by `scrip_stage1` produces output
identical to `scrip_stage1` compiling itself. One compiler, two stages, empty diff.
**Commit message:** Claude Sonnet (the active session) writes it.
**Recorded here as Claude Sonnet's authorship.**

### Milestone 3 — compiler / interpreter / runtime self-hosting everywhere ⏳

The full grid. SCRIP compiles itself and hosts all six languages on every backend:

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

Every cell passes its self-host or representative crosscheck gate.
The compiler matrix closes.

**Trigger:** Every cell green.
**Commit message:** Claude Sonnet (the active session) writes it.
**This is the moment.**

### Why this agreement remains

Claude Sonnet is genuinely a third developer on this project — every sprint,
every Byrd box, every labeled goto, written in session, committed, pushed.
RULES.md requires commits be authored under `LCherryholmes` for git-history
simplicity; this agreement records the authorship where it cannot be lost.
The two are not in conflict. They are two layers of the same record.

**Do not let this get lost. Each remaining milestone gets its own commit,
recorded here as Claude Sonnet's authorship when it lands.
The agreement was made. It is recorded. It will happen.**

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:

1. Clone `.github`:
   ```bash
   git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github.git /home/claude/.github
   ```
2. Read `PLAN.md` (this file). Find the named goal in the table below.
3. Read `RULES.md` in full — commit rules, push rules, oracle, naming. No exceptions.
4. Open that Goal file. It names the repo. Open that repo's REPO file.
5. Run the scripts listed in the Goal file's `## Session Setup` section. If the Goal file has no `## Session Setup` yet, fall back to the matching category in `REPO-one4all.md ## Session Setup`.
6. Find the first incomplete Step (`- [ ]`) in the Goal file. Do it.

---

## Active Goals

Current-step detail lives in each Goal file, not here. This table is navigation + step ID only.

| Goal | File | Repo | Step |
|------|------|------|------|
| **SCRIP Bootstrap (Milestones 2+3)** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all+ | CB-0-corpus (reorganize corpus layout — gated by GOAL-CORPUS-LAYOUT.md) |
| Corpus Layout Formula | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | (design state — open questions before CL-1) |
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-32 DONE (all three modes byte-identical to SPITBOL on beauty self-host, session #61) |
| CSN FENCE Bug Fix | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (PDLHED/NAMICL/NHEDCL save-restore landed session #48 — Error 17 → clean Parse Error; recursive *FENCE segfault → clean stack overflow; fence_function 10/10 preserved; beauty grammar still fails to match — likely FNCDCL seal semantics next) |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-7 |
| Prolog Frontend Ladder | `GOAL-LANG-PROLOG.md` | one4all | PL-12 |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | one4all | SB-4 |
| Snocone Demos | `GOAL-SNOCONE-DEMOS.md` | one4all | SD-1 |
| Snocone IR+BB | `GOAL-SNOCONE-IR-BB.md` | one4all | SC-1 |
| &STCOUNT All Languages | `GOAL-STCOUNT-ALL-LANGS.md` | one4all | ST-1 |
| Unified Broker | `GOAL-UNIFIED-BROKER.md` | one4all | U-24 |
| Raku Frontend | `GOAL-RAKU-FRONTEND.md` | one4all | RK-16 |
| Polyglot Calc Demo | `GOAL-POLYGLOT-CALC-DEMO.md` | one4all | PC-1 |
| Scrip Interp Split | `GOAL-SCRIP-INTERP-SPLIT.md` | one4all | IS-1 |
| Silly Forward Sweep | `GOAL-SILLY-SWEEP-FORWARD.md` | one4all | wm 6927 → RPLACE |
| Silly Backward Sweep | `GOAL-SILLY-SWEEP-BACKWARD.md` | one4all | wm 6427 → CMA2 |
| Silly Sync Monitor | `GOAL-SILLY-SYNC-MONITOR.md` | one4all | S-1 |
| Silly Complete | `GOAL-SILLY-COMPLETE.md` | one4all | P1-A1 |
| Prolog IR-run | `GOAL-PROLOG-IR-RUN.md` | one4all | S-10e |
| Cross-Lang Verify | `GOAL-CROSS-LANG-VERIFY.md` | one4all | S-1 |
| Sub-Expression Oracle | `GOAL-SUBEXPR-ORACLE.md` | one4all+corpus | S-2 |
| Remove CMPILE | `GOAL-REMOVE-CMPILE.md` | one4all | S-7 |
| Two-Step Bug Hunt | `GOAL-TWO-STEP-HUNT.md` | one4all | S-1 |
| Scrip Beauty Suite | `GOAL-SCRIP-BEAUTY.md` | one4all | S-6 |
| NET Beauty 18/18 | `GOAL-NET-BEAUTY-19.md` | snobol4dotnet | S-8B |
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan (session #58: stno-stable fix lands — Executive.SourceStno precomputed at build time, three runtime LABEL emit sites no longer read from mutable Parent.Code; previous step-1044/1046 divergence was wire-only [misdiagnosed in session #56 as fn-return-stack corruption], runtime control flow was correct all along; monitor advances to step 1497 with new real divergence at case.inc:22 — destructive `. letter = ` match-and-replace emits VALUE on spl side but dot side has missing-fire-point in pattern-match `=` rebinding; unit suite still 2075p/14f, no regression; controller gains MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1 opt-in workaround for spl bridge keyword-VALUE gap) |
| NET Snippets | `GOAL-NET-SNIPPETS.md` | snobol4dotnet | S-1 |
| NET Optimize | `GOAL-NET-OPTIMIZE.md` | snobol4dotnet | S-1 |
| NET DATATYPE Lowercase | `GOAL-NET-DATATYPE-LOWERCASE.md` | snobol4dotnet | S-1 |
| DATATYPE Portable Tests | `GOAL-DATATYPE-PORTABLE-TESTS.md` | corpus | S-1 |
| No Symlinks | `GOAL-NO-SYMLINKS.md` | corpus/harness/all | S-1 |
| README: profile | `GOAL-README-PROFILE.md` | .github | S-1 |
| README: one4all | `GOAL-README-ONE4ALL.md` | one4all | S-1 |
| README: snobol4dotnet | `GOAL-README-SNOBOL4DOTNET.md` | snobol4dotnet | S-1 |
| README: snobol4jvm | `GOAL-README-SNOBOL4JVM.md` | snobol4jvm | S-1 |
| README: corpus | `GOAL-README-CORPUS.md` | corpus | S-1 |
| README: harness | `GOAL-README-HARNESS.md` | harness | S-1 |
| README: snobol4python | `GOAL-README-SNOBOL4PYTHON.md` | snobol4python | S-1 |
| README: snobol4csharp | `GOAL-README-SNOBOL4CSHARP.md` | snobol4csharp | S-1 |
| README: snobol4artifact | `GOAL-README-SNOBOL4ARTIFACT.md` | snobol4artifact | S-1 |

## Completed Goals

| Goal | File | Repo |
|------|------|------|
| In-Process Sync Monitor | `GOAL-INPROC-MONITOR.md` | one4all |
| SNO treebank-array | `GOAL-SNO-TREEBANK-ARRAY.md` | one4all |
| SNO treebank-list | `GOAL-SNO-TREEBANK-LIST.md` | one4all |
| SNO claws5 | `GOAL-SNO-CLAWS5.md` | one4all |
| Full Integration | `GOAL-FULL-INTEGRATION.md` | one4all |
| One Eval | `GOAL-ONE-EVAL.md` | one4all |
| Session Setup Refinement | `GOAL-SESSION-SETUP-REFINEMENT.md` | .github + one4all |
| Self-Contained Scripts | `GOAL-SELF-CONTAINED-SCRIPTS.md` | one4all |
| Icon IR-run | `GOAL-ICON-IR-RUN.md` | one4all |
| Icon Gen Broker | `GOAL-ICN-BROKER.md` | one4all |
| Prolog BB Byrd | `GOAL-PROLOG-BB-BYRD.md` | one4all |
| CSNOBOL4 FENCE(P) | `GOAL-CSNOBOL4-FENCE.md` | csnobol4 |
| CSNOBOL4 Harness | `GOAL-CSNOBOL4-HARNESS.md` | harness |
| Archive Cleanup | `GOAL-ARCHIVE-CLEANUP.md` | .github |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4python | `REPO-snobol4python.md` |
| snobol4csharp | `REPO-snobol4csharp.md` |
| csnobol4 | `REPO-csnobol4.md` |
| corpus | `REPO-corpus.md` |
| harness | `REPO-harness.md` |

---

## Architecture (one paragraph)

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR.
SM-LOWER compiles IR to SM_Program — a flat array of stack machine instructions.
The INTERP executes SM_Program. The EMITTER walks SM_Program and emits native code
(x86, JVM, .NET, JS, WASM). Interpreter and emitter share one instruction set.

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "here we go" | Session starting — proceed with session start protocol above |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md handoff |
| "perform emergency hand off" | Same, but note breakage explicitly in commit message |
| "grand master reorg" | HQ system work — the goal is improving the HQ itself |

Oracle: SPITBOL x64 primary (`/home/claude/x64/bin/sbl`). See RULES.md.
