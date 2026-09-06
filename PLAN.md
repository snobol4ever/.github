# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog, Pascal. Ten times faster.
**⭐ TARGETS (Lon 2026-08-22 s257, in-chat, verbatim in substance — ship / dream), measured per the s255 two-oracle law (fixed-work callgrind Ir; SPITBOL = `spitbol-clean`):** SNOBOL4/Snocone **2–3x SPITBOL / dream 10x** · Icon **5–10x Arizona `icont`/`iconx`, ≫ JCON / dream 20x** · Prolog **2–3x SWI, par GNU / dream 10x SWI, 1.5x GNU (Lon: GNU is a true compiler)** — order: SNOBOL4 (Snocone) → Icon → Prolog → Pascal & Raku. **Fleet v2 config (same ruling): CEO = Fable @ `/home/claude`; hq_C + hq_P = Opus 5 (Max); seats = Sonnet 5, 8 active + 8 reserve.** ⭐ **PLATFORM ROADMAP (Lon 2026-08-28, in-chat to CEO, verbatim in substance: "the plan is to port to JVM, .NET, JavaScript, and Web Assembly"): x86/x64 ships FIRST (the announcement); the four ports are PLANNED TARGETS, not retired scope — the IS_JVM/IS_JS/IS_NET/IS_WASM stubs and the port-era GOAL/design files are living roadmap material and must never be archived as dead.**
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of SCRIP.**

### Milestone 1 ✅✅ COMPLETE — BOTH MODES, s197 2026-08-21 (Claude Fable 5) — beauty.sno SELF-HOST = FIXED POINT: output byte-identical to the beauty.sno INPUT FILE (Lon ruling s117; all md5 pins VOID — the checked-in file is its own oracle). Native engine, ladder m3 10/10 + m4 10/10 ⭐M1-FIXED-POINT, beauty_suite 17/17 both modes, pristine-verified; landing SCRIP `1f6cea4d` authored `Claude Fable 5 <noreply@anthropic.com>` (third-developer ceremony). History: first earned s57 2026-04-28 on the one4all engine (VOID per s117); mode 3 re-earned native s196; mode 4 s197 (`FINDING-2026-08-21-s197-milestone-1-both-modes-the-wall-was-one-unsalted-name.md`).
### Milestone 2 ⏳ — `scrip_stage2` compiled by `scrip_stage1` == `scrip_stage1` compiling itself.
⛔⭐ **DEPRIORITISED AND RE-ORDERED BY LON, 2026-08-22 s255, in-chat, verbatim in substance:** *"Forget milestone 2, SCRIP self compile. That is way down the road past Icon and Prolog and all the frontends working in x86 first. Then we do BOOTSTRAP compiler work. We stay in C for a while I'm sure."* **M2 IS NOT THE NEXT RUNG AND NO SEAT IS TO AIM AT IT.** The order is: (1) all frontends green on x86 — Icon and Prolog included; (2) THEN bootstrap work. The implementation language stays **C** meanwhile; nobody is porting the compiler.
### ⭐⭐⭐ THE TWO CARVE-OUTS — the real bootstrap road (Lon 2026-08-22 s255, in-chat)
Bootstrap here does NOT mean "SCRIP compiles its own C". It means **the compiler's two biggest hand-written subsystems become Snocone programs**, in the language family SCRIP compiles:
- **CARVE-OUT A — FRONT-END PARSERS → Snocone `parser_*.sc`, the Compiland pattern, ALL languages.** Lon: *"we will carve out the front end parsers and replace them with the Snocone parser_*.sc (Compiland pattern) for all languages."* ⭐ **This is not greenfield — the Snocone side already exists**: `SCRIP/bootstrap/parser_{snobol4,icon,prolog,snocone,rebus,raku}.sc` (moved from `corpus/SCRIP/` by the s267 ruling — that old path is stale, do not cite it) — **1,933 lines across 6 languages**, against **9,646 hand-written lines** of C in `src/parser/` (Icon+Prolog are ~100% hand-written; the other four are mostly bison/flex-*generated*, so a raw-file-total comparison overstates the win — raw total is 47,171, ~24:1, vs the **hand-written figure's honest 5:1**). Prior art: `GOAL-PARSER-SC-TRANSPILE.md`, `GOAL-SNOCONE-100.md` (retired name `GOAL-PARSER-SNOCONE.md`), `GOAL-REBUS-100.md` (retired name `GOAL-PARSER-REBUS.md`), `PRF-14-TREE-SHAPE-ORACLE.md` all already speak Compiland. **Per-language ladder + rung-1 brief: `.github/CARVEOUT-A-LADDER.md` (seat13, 2026-08-24)** — every language except Pascal already has its Phase-2 grammar rewrite DONE (2026-05-19); remaining work is per-language engine bugs / missing gates / a self-flagged Raku architecture defect, not fresh parser-authoring. Sequenced SNOBOL4 → Icon → Prolog → Pascal → Raku per this file's own s257 targets-order (line 4), with Snocone/Rebus as opportunistic rungs outside that named list (both near-done, see the ladder file).
- **CARVE-OUT B — TEMPLATE GENERATION → Snocone, via `*(EXPRESSION)` deferred evaluation.** Lon: *"we will carve out the template generation also into Snocone using *(EXPRESSION) evaluation."* Target: the **129 `bb_*.cpp` boxes, 10,185 lines**. The mechanism is SNOBOL4/SPITBOL's own deferred expression — evaluated at USE time, not construction time (see `REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md` §7) — which is exactly the semantics a code template needs: a box body that names its operands before they exist.
**COMBINED SCALE: ~51,800 of the tree's ~101,600 source lines** — over half the compiler — moves from C/C++ to Snocone. That is the bootstrap, and it is why M2-as-written was the wrong next rung.
### Milestone 3 ⏳ — All languages × all backends green.

---

## ⭐⭐⭐ MASTER-PLAN.md — THE ORDER OF THE WORK UNDER FLEET-16 (Lon 2026-09-01: Prolog is the #1 priority — test, performance, Term eradication)

Four ladders (T Term→DESCR · C correctness/tests · P performance · I instruments/dispatch), every rung a QUEUE row, rank 0/1 reserved for rungs; `python3 SCRIP/scripts/util_ladder_walk.py` is the instrument the ceo runs every sitting. HQs place every new Prolog row on a rung (`LADDER:<id> RUNG:<n>` on the LINKS line). Read it after this file, before any GOAL file, when the MODE file says FLEET-*.

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://github.com/snobol4ever/.github.git /home/claude_ceo/.github` (public; `git push` needs a credential)
1b. ⛔ **CLONE THE ORACLE TOO — `git clone https://github.com/snobol4ever/x64 /home/claude_ceo/x64`** (⛔ SUPERSEDED s261: the oracle is the SHARED install `/home/resources/x64/bin/sbl`; no root clones x64 — RULES.md § Oracles).** Not optional and not only for "oracle profiles": **every SNOBOL4/Snocone board script diffs against `x64/bin/sbl`, and with it absent they print a full, plausible, entirely FALSE all-FAIL table** (the s33 "non-empty is not alive" false-signal class). Predicted s40, measured s43, hit again s44 — three sessions. A seat told "clone .github, corpus and SCRIP" gets no oracle unless this step is followed.
2. Read `PLAN.md`; find the goal in the table.
3. Read `RULES.md` in full.
4. PARSER-* or Snocone → read `SNOBOL4-SNOCONE-PRIMER.md` first.
5. Touches language corpus → read `CORPUS-LOCATIONS.md`.
6. **SNOBOL4 (any rung) → the ONE goal is `GOAL-SNOBOL4-100.md`; every deleted SNOBOL4 GOAL-* name resolves there.**
6b. **Icon (any rung) → the ONE goal is `GOAL-ICON-100.md`; every deleted Icon GOAL-* name resolves there.**
6c. **Prolog (any rung) → the ONE goal is `GOAL-PROLOG-100.md`; every deleted Prolog GOAL-* name resolves there.**
7. **Any BB codegen / template / `x86_asm.h` work (every `GOAL-*-BB` rung) → read the BB-CODEGEN DESIGN SET FIRST, NON-NEGOTIABLE:** `ARCH-LANGUAGES.md` (register source of truth = `src/templates/x86_asm.h`; layout = `src/emitter/emit.cpp` + flat `src/templates/`) and `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (R2/R7/R9/R10 + the ONE-MEDIUM-INVISIBLE FACT RULE govern every new encoder; the `IF(MEDIUM_TEXT,..)+IF(MEDIUM_BINARY,..)` pair is the named forbidden shape).
8. Open the Goal file + that repo's REPO file.
9. Run the Goal file's `## Session Setup` scripts.
10. Trust the goal file's `LIVE CURSOR` (never this table's Step column — stale by design). Find first incomplete Step. Do it.

### Clone SPITBOL oracle
```bash
git clone https://github.com/snobol4ever/x64 /home/claude_ceo/x64   # SUPERSEDED s261: use /home/resources/x64/bin/sbl, never a per-root clone
/home/resources/x64/bin/sbl -bf file.sno   # ⛔ beauty.sno needs -bf; plain -b SIGSEGVs rc=139 (s122)
```

---

## Active Goals

| Goal | File | Step (stale by design — trust the goal file's LIVE CURSOR) |
|------|------|------|
| **⛔⭐⭐⭐⭐⭐ CEO** ⬅ Lon 2026-08-22 s257: Fable seat ABOVE the two HQ — audit · arbitration · law custody · strategy; never briefs, never measures. Identity `ceo` | `GOAL-CEO.md` + `ARCH-FLEET-CEO.md` | CEO-0 done: fleet-v1 retrospective FINDING routed; fleet-v2 + task-baton designed; `PROTOCOL-V2-DRAFT.md` staged awaiting Lon's flip. |
| **⛔⭐⭐⭐⭐ HQ-CORRECTNESS** ⬅ Lon 2026-08-22 s256: HQ SPLIT IN TWO. Owns "does it produce the right answer" — SNOBOL4 #1 · Icon #2 · Prolog #3. Root `/home/claude_C`, identity `hq_C` | `GOAL-HQ-COMPLETE.md` | C-0: MILESTONE 1 MODE-3 REGRESSED — beauty m3 emits 278 bytes vs the 40,971 fixed point; m4 still correct, so it is a BOTH-MEDIUM violation. |
| **⛔⭐⭐⭐⭐ HQ-PERFORMANCE** ⬅ Lon 2026-08-22 s256. Owns "how many instructions" — same three, same priority. Root `/home/claude_P`, identity `hq_P` | `GOAL-HQ-PERFORM.md` | P-0: profile `roman` (67,170 Ir/iter vs SPITBOL 7,966). SCRIP WINS on scalar (1.1–1.5x), LOSES 2.8–8.4x on tables/strings/real programs. The 10x is not blocked on codegen. |
| **⛔ SCRIP HQ (SUPERSEDED s256 — split into the two above; kept for its laws and history)** ⬅ Lon 2026-08-19: HQ designs rungs + dispatch briefs; Lon fires worker seats; fronts = the three ⭐100 goals | `GOAL-SCRIP-HQ.md` | HQ-1: M1 campaign ladder cut; DISPATCH BOARD D-1 (seeding fix) + D-2 (claws5) READY. |
| **⛔⭐⭐⭐⭐ SNOBOL4 100% — THE ONE GOAL** ⬅ Lon 2026-08-15 s92: 22 SNOBOL4 goal files consolidated into ONE (THREE ZETAS: ζ-STANDING/ζ-ACTIVATION-FRAME on RBP, ζ-SPINE on RSP); Milestone 1 (beauty self-host) is rung R-2 | `GOAL-SNOBOL4-100.md` | R-0 = the M1 root cause (ALT-arm-interior capture has no home, both media, witness `corpus/probe/m1/`); R-1 = m3 unification (branch `s91-m3-unify` + tiny-site binary crossing); scorecard META 38.0 baseline. |
| **IR REDUCE / NO-MANGLE** ⬅ GROUND ZERO #5 | `GOAL-IR-IMMUTABLE-EMIT.md` | Emitter reads IR, never mutates; collapse 224 opcodes toward JCON-33; per-BB self-allocation (ZB-PORTS → ZB-ACT) per the file's CURRENT-PRIORITY banner. |
| **RTCC — GLOBAL REGISTER LIBERATION** ⬅ NEW 2026-08-08 (Lon strategy pivot; absorbs/generalizes RTX-11) | `GOAL-RTCC.md` | Veneer at every C-RT boundary; claim all 9 caller-saved GPRs + XMM8–15 as VM globals. RC-0 open (scripts/census half). ⛔ RC-1..RC-4 touch shared files (merge, do not wait) |
| **Raku BB (OOP)** | `GOAL-RAKU-100.md` | OO LADDER, § TRACK 1. |
| **DEAD-CODE SWEEP** | `GOAL-DEAD-CODE-SWEEP.md` | Batch 4 landed; see file. |
| **BB-FIXUP** | `GOAL-BB-FIXUP.md` | Round-robin hygiene; cursor in `BB-REVAMP-TRACKER.md`. |
| **SRC REORG** | `GOAL-SRC-REORG.md` | Open GMR-8(b). |
| **RUNTIME RENAME / REORG** | `GOAL-RUNTIME-RENAME.md` / `GOAL-RUNTIME-REORG.md` | LI-CORE (Lon decision) / per-file CS subsystems. |
| **⛔⭐⭐⭐ ICON 100% — THE ONE ICON GOAL** ⬅ Lon 2026-08-15 s229: 15 Icon goal files consolidated into ONE (THREE ZETAS: ζ-STANDING/ζ-ACTIVATION-FRAME on RBP, ζ-SPINE on RSP) | `GOAL-ICON-100.md` | R-0 = resurrect the default arm (fresh triple watermark at `07d6eae7`: default 1/262/30 · CELLS=1 235/28/30 · ZFRAME=0 78/185/30; bisect `8487d499..07d6eae7`, predicate proven at both ends). |
| **⛔⭐⭐⭐ PROLOG 100% — THE ONE PROLOG GOAL** ⬅ Lon 2026-08-16 s165: 10 Prolog goal files consolidated into ONE (THREE ZETAS: ζ-STANDING/ζ-ACTIVATION-FRAME, ζ-SPINE on RSP) | `GOAL-PROLOG-100.md` | R-0h harness honesty then R-0 reconquest (s165 live watermark: smoke 3/5 · rung 113/109 of 164 · bench-22 green=8); R-1 = ZK-5B per its restart protocol. |
| **⛔⭐⭐⭐ PASCAL 100% — THE ONE PASCAL GOAL** ⬅ Lon 2026-08-27: consolidated into ONE file | `GOAL-PASCAL-100.md` | 7th frontend (P4 subset); toolchain in `corpus/programs/pascal/`. FRONT STATUS: restoration (`pascal-restore-prezeta`) + PAS-DISPLAY revival are the live front. |
| **PST Parent / Snocone / Raku** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` + `GOAL-PST-*.md` | See files. (SNOBOL4 PST → `GOAL-SNOBOL4-100.md`; Prolog PST → `GOAL-PROLOG-100.md`.) |
| **TEMPLATES X86 / JVM / .NET / JS / WASM** | `GOAL-TEMPLATES-*.md` | Per-backend; per-language state in `GOAL-*-BB.md`. |
| **IR REDESIGN** | `GOAL-IR-REDESIGN.md` | IRD-0 open. |
| **Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | SCT-1f or SCT-BEAUTY-SC-PARSE. |

---

## Repos

| Repo | File |
|------|------|
| SCRIP | `REPO-SCRIP.md` |
| corpus | `REPO-corpus.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip, Pascal) produces the shared AST. LOWER compiles AST → shared IR graph. OPTIMIZER (`src/optimizer/`, ON by default; `SCRIP_OPT=0` emergency-only) sits between LOWER and the EMITTER. The EMITTER (`emitter/` — per-box templates + dispatch + x86 encoders) walks the graph and emits native code in TWO 1:1 modes — mode-3 BINARY in-process, mode-4 TEXT via as+gcc (JVM/.NET/JS/WASM dormant under X86-ONLY). Modes 1/2 DELETED.

`src/` by pipeline role: `parser/` (7 front-ends) · `contracts/` (spine types + allocators) · `lower/` · `emitter/` · `machine/` (RX slab + stage2 preamble) · `runtime/` (`core/`, `rt/`, `builtins/`) · `driver/` · `backends/` (dormant non-x86) · `tools/` · `attic/`.

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------|
| "here we go" | Session starting |
| **"Go."** | ⭐ Lon s257, the fleet-v2 universal prompt: orient from THIS root's CLAUDE.md standing orders, resume the sovereign file's LIVE CURSOR / your task's NEXT block, execute, banner fires itself. Works identically at CEO, HQ, and seat — Lon never needs to remember state; the files carry it. |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
