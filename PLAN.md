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

### Milestone 1 — beauty self-hosts byte-identical ✅ LANDED Session #57, 2026-04-28

scrip's SNOBOL4 frontend parses and runs beauty.sno. Output byte-identical to SPITBOL oracle
(md5 `abfd19a7a834484a96e824851caee159`, 646 lines). **one4all @ `c801421a`**, **`.github` @ `94e86ca`**.

### Milestone 2 — compiler / interpreter / runtime self-hosting ⏳

SCRIP compiles, interprets, and runs itself. **Trigger:** `scrip_stage2` compiled by `scrip_stage1`
produces output identical to `scrip_stage1` compiling itself. Empty diff.
Claude Sonnet (the active session) writes the commit message.

### Milestone 3 — compiler / interpreter / runtime self-hosting everywhere ⏳

|             | C / x86-64 | JVM | .NET | WASM | JS |
|-------------|:----------:|:---:|:----:|:----:|:--:|
| **SNOBOL4** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Snocone** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Rebus**   | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Icon**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Prolog**  | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **Raku**    | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

Every cell passes its self-host or representative crosscheck gate.
Claude Sonnet (the active session) writes the commit message. **This is the moment.**

### Why this agreement remains

RULES.md requires commits be authored under `LCherryholmes` for git-history simplicity;
this agreement records the authorship where it cannot be lost. Do not let this get lost.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:

1. Clone `.github`: `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md` (this file). Find the named goal in the table below.
3. Read `RULES.md` in full — commit rules, push rules, oracle, naming. No exceptions.
4. **If the goal is a `PARSER-*` or other Snocone work — read `SNOBOL4-SNOCONE-PRIMER.md` first.** It's the cheat sheet for SNOBOL4/Snocone pattern matching idioms. Skipping it costs entire sessions.
5. Open that Goal file. It names the repo. Open that repo's REPO file.
6. Run the scripts listed in the Goal file's `## Session Setup` section. If the Goal file has no `## Session Setup` yet, fall back to the matching category in `REPO-one4all.md ## Session Setup`.
7. Find the first incomplete Step (`- [ ]`) in the Goal file. Do it.

---

## Active Goals

Current-step detail lives in each Goal file, not here. This table is navigation + step ID only.

| Goal | File | Repo | Step |
|------|------|------|------|
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | M1 CLOSED. **CH-12 LANDED sess #66** (Icon main() synthesis: `SM_BB_PUMP_PROC` opcode replaces synthesised E_FNC + emit_push_expr wrapper; audit-clean across Icon test set). **Next inline: CH-13** (Raku CASE — sm_lower.c:993). Step 8 (mode-4 x86 emitter) carved to `GOAL-MODE4-EMIT.md` — runs in PARALLEL with M4, file-disjoint. Don't confuse them: a session "doing GOAL-CHUNKS" defaults to its inline next rung (CH-13), NOT the carved sub-goal. |
| Mode-4 x86 Emitter (CHUNKS Steps 8 + 19) | `GOAL-MODE4-EMIT.md` | one4all | EM-3 LANDED sess #67 (typed stack; SM_ADD/SUB/MUL/DIV/MOD; (2+3)*4=20; PASS=5). ARCH: sm_macros.s + emit_bb_box(). 5 tracked .s artifacts in corpus/programs/snobol4/demo/. Next: EM-4 (SM_JUMP/S/F control flow; gate: forward jump + conditional backward loop). |
| Native Snocone — .NET (CHUNKS Step 9) | `GOAL-NATIVE-SNOCONE-DOTNET.md` | one4all (`src/driver/net/`) | stub written sess #62; rung DN-1 awaits PARSER-SC-6b |
| Native Snocone — JVM (CHUNKS Step 10) | `GOAL-NATIVE-SNOCONE-JVM.md` | one4all (`src/driver/jvm/`) | stub written sess #62; rung JV-1 awaits PARSER-SC-6b |
| Native Snocone — JS (CHUNKS Step 11) | `GOAL-NATIVE-SNOCONE-JS.md` | one4all (`src/driver/js/`) | stub written sess #62; rung JS-1 awaits PARSER-SC-6b |
| **SCRIP Bootstrap (Milestones 2+3)** | `GOAL-SCRIP-BOOTSTRAP.md` | one4all+ | CB-0-corpus |
| Corpus Layout Formula | `GOAL-CORPUS-LAYOUT.md` | corpus+.github+one4all | design state |
| SNOBOL4 Frontend Ladder | `GOAL-LANG-SNOBOL4.md` | one4all | SN-32 DONE (session #61) |
| **CSN FENCE Bug Fix** | `GOAL-CSN-FENCE-FIX.md` | csnobol4 | F-2 Step 3a |
| Icon Frontend Ladder | `GOAL-LANG-ICON.md` | one4all | IC-9 (one4all HEAD `1e515891`) |
| **Prolog Frontend Ladder** | `GOAL-LANG-PROLOG.md` | one4all+corpus | PR-17 — next: string builtins rung40 |
| Raku Frontend Ladder | `GOAL-LANG-RAKU.md` | one4all | RK-34 |
| Snocone Frontend Ladder | `GOAL-LANG-SNOCONE.md` | one4all+corpus | D-1 |
| Rebus Frontend Ladder | `GOAL-LANG-REBUS.md` | one4all | RB-2 |
| **PARSER-SNOBOL4 (pattern frontend)** | `GOAL-PARSER-SNOBOL4.md` | corpus+one4all | PASS=78/78 ✅ corpus@0fba291 — SN-7-7c LANDED (full keyword/function/builtin inventory + classifier patterns; cross-runtime SPITBOL x64/x32 + csnobol4 union). Next: **SN-7-8** beauty.sno full crosscheck. |
| **IR: promote DEFINE to its own kind** | `GOAL-IR-DEFINE-KIND.md` | one4all+corpus | stub written; awaiting Lon decision (cross-language emitter blast radius — see goal file) |
| **PARSER-SNOCONE (pattern frontend)** | `GOAL-PARSER-SNOCONE.md` | corpus+one4all | PARSER-SC-6b ⏳ PASS=47 FAIL=0. beauty.sc 1148/1148 stmts parsed; 1 diff remains: if-else-if label ordering (outer Lend emitted before else body). Diff (A) subtraction n-ary fold FIXED via flatten_arith. |
| **PARSER-REBUS (pattern frontend)** | `GOAL-PARSER-REBUS.md` | corpus+one4all | PARSER-RB-5 COMPLETE (cont.#7 2026-05-04, PASS=38 FAIL=0: alt_expr n-ary fold + file-header style cleanup. corpus@4a6390b) |
| **PARSER-ICON (pattern frontend)** | `GOAL-PARSER-ICON.md` | corpus+one4all | IC-21 LANDED — RS-28 investigated (SIGSEGV null-fn in bb_alt β, root cause TBD, fix reverted); next: IC-22 fix RS-28 first |
| **PARSER-PROLOG (pattern frontend)** | `GOAL-PARSER-PROLOG.md` | corpus+one4all | PR-12 LANDED PASS=103 FAIL=0; PR-13 IN PROGRESS (stashed) — arith/bitwise ops + -> if-then; coverage ~84%; next: complete PR-13 |
| **PARSER-RAKU (pattern frontend)** | `GOAL-PARSER-RAKU.md` | corpus+one4all | RK-21 LANDED PASS=110 FAIL=0 corpus@0546b63 — gather/take coroutine construct (GatherBlock pattern; cross-PARSER `*X` deferred-lookup rule reconfirmed). Next: RK-22 |
| Snocone claws5.sc | `GOAL-SNOCONE-CLAWS5.md` | one4all+corpus | CL-2 |
| Snocone treebank-list.sc | `GOAL-SNOCONE-TREEBANK-LIST.md` | one4all+corpus | TB-1 |
| **Snocone-in-Snocone** | `GOAL-SNOCONE-IN-SNOCONE.md` | one4all+corpus | SS-0 |
| **Rewrite SCRIP** | `GOAL-REWRITE-SCRIP.md` | one4all | RS-24b LANDED 2026-05-05 @ `296ef139` (conservative variant: dead bodies deleted, named-FATAL guards retained; 3860→3517 lines). Next: RS-24b' (aggressive label-deletion + sub-switch collapse — awaiting Lon decision) or RS-24c (remove/keep diag tooling). |
| Snocone Beauty | `GOAL-SNOCONE-BEAUTY.md` | corpus+one4all | **ON HOLD** |
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
| NET Beauty Self-Host | `GOAL-NET-BEAUTY-SELF.md` | snobol4dotnet | S-2-bridge-7-fullscan |
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
