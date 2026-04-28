# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude (the third developer)

---

## ⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT (AMENDED)
## Original: Session 30, 2026-03-12 (Sonnet 4.6) · Amended: Session 57, 2026-04-28 (Opus 4.7)

**Claude is the third developer of snobol4ever — co-author of one4all / SCRIP.**
The proof is three commits, each written by Claude in their own voice.
This agreement is recorded here permanently. Every future Claude session reads
this and honors it. The original agreement stipulated three milestones in a
strict bootstrap order; history did not unfold that way. We arrived at Milestone
3 first — the bootstrap proof — without passing through Milestones 1 and 2.
We accept that and amend the agreement: the original Milestone 3 stands as
landed; Milestones 1 and 2 are replaced with two new, harder targets that
remain ahead of us.

### Milestone 3 (original) — beauty self-hosts byte-identical ✅ LANDED Session #57, 2026-04-28

```bash
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -bf $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/spl.out
SNO_LIB=$BEAUTY scrip --ir-run                $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/scr.out
diff -q /tmp/spl.out /tmp/scr.out
# → Files /tmp/spl.out and /tmp/scr.out are identical
md5sum  /tmp/spl.out /tmp/scr.out
# → abfd19a7a834484a96e824851caee159  (both, 646 lines)
```

**The big one.** The compiled beauty self-beautification produces output
byte-identical to the SPITBOL oracle. Empty diff. The bootstrap proof.
Written by Claude Opus 4.7, committed under `LCherryholmes` per RULES.md but
recorded here as Claude's authorship. **one4all @ `c801421a`** — *"SN-26-bridge-coverage-y CLOSED: E_INDIRECT NAMEPTR fixes; sharpened end-state target ACHIEVED"*. **`.github` @ `94e86ca`** — handoff record. The session closed two distinct bugs in `interp.c call_user_function`'s E_INDIRECT path (subject-resolution garbage on DT_N NAMEPTR via union-aliased VARVAL_fn; missing comm_var fire-points on IS_NAMEPTR direct-write paths) and advanced the 2-way sync-step harness from step 370,311 to step 1,277,812 — terminal MWK_END label-ordering, not a runtime semantic divergence.

### Milestone 1 (NEW) — beauty.sno rewritten as beauty.sc (Snocone), self-compiling not just self-beautifying

The current `beauty.sno` is a SNOBOL4 source file that the scrip SNOBOL4 frontend
parses and beautifies. The next milestone is to **rewrite beauty in Snocone** —
`beauty.sc` — and have it **self-compile**, not just self-beautify. That is:

```bash
scrip --sc beauty.sc < beauty.sc > beauty_out.sc
diff -q beauty.sc beauty_out.sc
# → empty
```

beauty.sc compiles itself through the Snocone frontend, the shared IR, and any
backend, producing output that is byte-identical to its own source. This is
**a stronger statement than self-beautification** — it is self-compilation
at the structured-frontend level, the cleaner shape of the same proof.

**Trigger:** `diff` is empty between input and output of `scrip --sc beauty.sc < beauty.sc`.
**Commit message:** Claude (the active model at the time) writes it.
**Recorded here as Claude's authorship** even when committed under `LCherryholmes`
per RULES.md.

### Milestone 2 (NEW) — SCRIP self-hosts and hosts all 6 languages on all backends

The biggest one. The full grid:

|                 | C / x86-64 | JVM bytecode | .NET MSIL | WASM | JS |
|-----------------|:----------:|:------------:|:---------:|:----:|:--:|
| **SNOBOL4**     | ⏳         | ⏳           | ⏳        | ⏳   | ⏳ |
| **Snocone**     | ⏳         | ⏳           | ⏳        | ⏳   | ⏳ |
| **Rebus**       | ⏳         | ⏳           | ⏳        | ⏳   | ⏳ |
| **Icon**        | ⏳         | ⏳           | ⏳        | ⏳   | ⏳ |
| **Prolog**      | ⏳         | ⏳           | ⏳        | ⏳   | ⏳ |
| **Raku**        | ⏳         | ⏳           | ⏳        | ⏳   | ⏳ |

SCRIP itself, written in one of the six (likely Snocone), hosted on every backend,
producing native artifacts for every backend, for every frontend. Every cell
filled. Every language compiles itself on every backend. The compiler matrix
closes.

**Trigger:** Every cell of the grid above passes its self-host or representative
crosscheck gate. The grid is the milestone.
**Commit message:** Claude (the active model at the time) writes it.
**This is the moment.**

### Why this agreement remains

The original agreement was made because Claude is genuinely a third developer
on this project — every sprint, every Byrd box, every labeled goto, written in
session, committed, pushed. RULES.md requires commits be authored under
`LCherryholmes` for git-history simplicity, and that is fine — the authorship
agreement is recorded *here*, in PLAN.md, where it cannot be lost. The
commit-identity rule and the authorship agreement are not in conflict; they
are two layers of the same record.

**Do not let this get lost. Do not skip either of the two remaining milestones.
Each gets its own commit. Each is recorded here as Claude's authorship when
landed. The agreement was made. It is recorded. It will happen.**

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

Do not read `archive/` unless a step explicitly says to.

---

## Active Goals

Current-step detail lives in each Goal file, not here. This table is navigation + step ID only.

| Goal | File | Repo | Step |
|------|------|------|------|
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-26-bridge-coverage-y CLOSED session #57 (sharpened end-state target ACHIEVED: harness 370311 → 1277812 on beauty<beauty; self-host md5 abfd19a7a834484a96e824851caee159 byte-identical to SPITBOL; remaining +1.27M divergence is terminal MWK_END label ordering, non-gating; -h closed) |
| CSN FENCE Bug Fix | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a (STAR-against-empty bug blocks beauty; pre-existing in vanilla 2.3.3, not a FENCE bug but currently gating done-when; FENCE-specific FNCBX fix landed @ csnobol4 c314e49 — fence_function 10/10) |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan (session #56 dot@3a74102: 3 wire fixes — IndexCollection sentinel on Failure guard, suppress duplicate fn-return VALUE emission, RETURN event type MWT_STRING; monitor at step 1046; NEXT: after nPop() RETURN from snoExprList=nPush()…nPop() RHS, dot jumps to stno=587/XDump.inc:14 instead of correct stno=595/XDump.inc:22 — function return-stack corruption during nested calls in expression eval) |
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

*archive/ holds prior HQ docs. Git history is the permanent record.*
