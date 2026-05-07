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
| **CHUNKS — Eliminate SM_PUSH_EXPR** | `GOAL-CHUNKS.md` | one4all+.github | M1 CLOSED. **CH-15a LANDED sess #73, 2026-05-07** (E_TO + E_TO_BY producer migration — SM_ICMP_GT/SM_ICMP_LT opcodes added; first producer for SM_BB_PUMP_SM; gen-locals 0=lo, 1=hi, 2=cur, 3=step; E_TO_BY dispatches on step-sign each iteration; chunk emission verified via Raku `say 1..3` audit `SM_PUSH_CHUNK=1, SM_PUSH_EXPR=0`). **Next inline: CH-15b** (likely E_EVERY + E_SUSPEND bundle — both have minimal internal state; remaining kinds in Step 15: E_EVERY, E_SUSPEND, E_BANG_BINARY, E_LCONCAT, E_LIMIT, E_RANDOM, E_SECTION, E_SECTION_PLUS, E_SECTION_MINUS). Step 8 (mode-4 x86 emitter) carved to `GOAL-MODE4-EMIT.md` — runs in PARALLEL with M4, file-disjoint. Don't confuse them: a session "doing GOAL-CHUNKS" defaults to its inline next rung (CH-15b), NOT the carved sub-goal. |
| Mode-4 x86 Emitter (CHUNKS Steps 8 + 19) | `GOAL-MODE4-EMIT.md` | one4all | **EM-7b LANDED sess #75, 2026-05-07** — `bb_flat.c` EMIT_TEXT parity + externally-visible α/β/γ/ω labels (`_pat_inv_<pid>_<sid>_alpha/_beta/_gamma/_omega`).  Path 1 from the audit: `bb_emit_byte` dual-mode emits `.byte 0xNN` lines, jumps go through dual-mode `bb_insn_*` helpers (added `bb_insn_jg_rel32`).  Refactored `bb_build_flat()` body into shared `flat_emit_body()`; added `bb_build_flat_text()` TEXT entry.  Unit test PASS=15.  Gates: smoke ×6 PASS, EM PASS=11 (was 10), isolation PASS, gcc -c on emitted .s clean, 4/4 globals visible.  Tracked artifacts unchanged. ⛔ Course-correction filed for next: **EM-7b'** (sess #75, Lon's call) — refactor emit layer to `emitter_v *` vtable.  EM-7b's factoring smears the TEXT/BINARY discrimination across every leaf (44 raw `bb_emit_byte` sites, 25 `bb_insn_*` if/else branches).  Right shape: one vtable, two implementations, walker takes `emitter_v *e`.  Same shape we need for Snocone bootstrap (EXPRESSION as templates) and for the PLAN.md Milestone-3 matrix (JVM/.NET/JS/WASM columns each = one `emitter_v` instance).  See EM-7b' rung body in GOAL file for migration steps.  Then EM-7c.  Prior closed: EM-7-emit-determinism + EM-7a sess #74 — strdup fix + Phase-2 SM simulator + per-node invariance partition primitives. |
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
| **PARSER-SNOCONE (pattern frontend)** | `GOAL-PARSER-SNOCONE.md` | corpus+one4all | PARSER-SC-10 ✅ LANDED (sess 11, 2026-05-07) — switch/case/default. PASS=67 FAIL=0. Next: **SC-11** (define next rung with Lon). |
| **PARSER-REBUS (pattern frontend)** | `GOAL-PARSER-REBUS.md` | corpus+one4all | GOAL PIVOTED 2026-05-07 — new goal: full Rebus program parsing with simplified trees. RB-FULL-1 next. corpus@dac6db3 |
| **PARSER-ICON (pattern frontend)** | `GOAL-PARSER-ICON.md` | corpus+one4all | IC-22 LANDED PASS=143 — rung36 gprocs 2/2 PASS, 100% oracle coverage confirmed; RS-28 cross-pollination deferred; next: IC-23 |
| **PARSER-PROLOG (pattern frontend)** | `GOAL-PARSER-PROLOG.md` | corpus+one4all | **GOAL PIVOTED 2026-05-07** -- 100% parse coverage on 677 .pl files (SWI+GNU+corpus). PR-17 PARTIAL: recovery+\+prefix+div/rdiv landed corpus@2a9d6a0. Next: single-char SY atoms in op/3, *-> soft cut, coverage measurement. |
| **PARSER-RAKU (pattern frontend)** | `GOAL-PARSER-RAKU.md` | corpus+one4all | RK-27 LANDED PASS=147 FAIL=0 — nested call fname fix (v(kids[1])); NewCallName→capclsf/capclsr. Next: RK-28. |
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
