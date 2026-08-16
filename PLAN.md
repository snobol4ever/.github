# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog, Pascal. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28 — beauty.sno SELF-HOST = FIXED POINT: output byte-identical to the beauty.sno INPUT FILE (Lon ruling s117; all md5 pins VOID — the checked-in file is its own oracle) — ⛔ TO BE RE-EARNED ON THE NATIVE ENGINE (BOTH MODES): `GOAL-SNOBOL4-100.md` R-2; measured 0/2 modes at s91.
### Milestone 2 ⏳ — `scrip_stage2` compiled by `scrip_stage1` == `scrip_stage1` compiling itself.
### Milestone 3 ⏳ — All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://github.com/snobol4ever/.github.git /home/claude/.github` (public; `git push` needs a credential)
1b. ⛔ **CLONE THE ORACLE TOO — `git clone https://github.com/snobol4ever/x64 /home/claude/x64`.** Not optional and not only for "oracle profiles": **every SNOBOL4/Snocone board script diffs against `x64/bin/sbl`, and with it absent they print a full, plausible, entirely FALSE all-FAIL table** (the s33 "non-empty is not alive" false-signal class). Predicted s40, measured s43, hit again s44 — three sessions. A seat told "clone .github, corpus and SCRIP" gets no oracle unless this step is followed.
2. Read `PLAN.md`; find the goal in the table.
3. Read `RULES.md` in full.
4. PARSER-* or Snocone → read `SNOBOL4-SNOCONE-PRIMER.md` first.
5. Touches language corpus → read `CORPUS-LOCATIONS.md`.
6. **SNOBOL4 (any rung) → the ONE goal is `GOAL-SNOBOL4-100.md`; every deleted SNOBOL4 GOAL-* name resolves there.**
6b. **Icon (any rung) → the ONE goal is `GOAL-ICON-100.md`; every deleted Icon GOAL-* name resolves there.**
7. **Any BB codegen / template / `x86_asm.h` work (every `GOAL-*-BB` rung) → read the BB-CODEGEN DESIGN SET FIRST, NON-NEGOTIABLE:** `ARCH-ICON.md` (register source of truth = `src/templates/x86_asm.h`; layout = `src/emitter/emit.cpp` + flat `src/templates/`) and `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (R2/R7/R9/R10 + the ONE-MEDIUM-INVISIBLE FACT RULE govern every new encoder; the `IF(MEDIUM_TEXT,..)+IF(MEDIUM_BINARY,..)` pair is the named forbidden shape).
8. Open the Goal file + that repo's REPO file.
9. Run the Goal file's `## Session Setup` scripts.
10. Trust the goal file's `LIVE CURSOR` (never this table's Step column — stale by design). Find first incomplete Step. Do it.

### Clone SPITBOL oracle
```bash
git clone https://github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step (stale by design — trust the goal file's LIVE CURSOR) |
|------|------|------|
| **⛔⭐⭐⭐⭐ SNOBOL4 100% — THE ONE GOAL** ⬅ Lon 2026-08-15 s92: 22 SNOBOL4 goal files consolidated into ONE (THREE ZETAS: ζ-STANDING/ζ-ACTIVATION-FRAME on RBP, ζ-SPINE on RSP); Milestone 1 (beauty self-host) is rung R-2 | `GOAL-SNOBOL4-100.md` | R-0 = the M1 root cause (ALT-arm-interior capture has no home, both media, witness `corpus/probe/m1/`); R-1 = m3 unification (branch `s91-m3-unify` + tiny-site binary crossing); scorecard META 38.0 baseline. |
| **IR REDUCE / NO-MANGLE** ⬅ GROUND ZERO #5 | `GOAL-IR-IMMUTABLE-EMIT.md` | Emitter reads IR, never mutates; collapse 224 opcodes toward JCON-33; per-BB self-allocation (ZB-PORTS → ZB-ACT) per the file's CURRENT-PRIORITY banner. |
| **RTCC — GLOBAL REGISTER LIBERATION** ⬅ NEW 2026-08-08 (Lon strategy pivot; absorbs/generalizes RTX-11) | `GOAL-RTCC.md` | Veneer at every C-RT boundary; claim all 9 caller-saved GPRs + XMM8–15 as VM globals. RC-0 open (scripts/census half). ⛔ RC-1..RC-4 touch shared files (merge, do not wait) |
| **Raku BB (OOP)** | `GOAL-RAKU-BB.md` | OO LADDER top of file. |
| **DEAD-CODE SWEEP** | `GOAL-DEAD-CODE-SWEEP.md` | Batch 4 landed; see file. |
| **BB-FIXUP** | `GOAL-BB-FIXUP.md` | Round-robin hygiene; cursor in `BB-REVAMP-TRACKER.md`. |
| **SRC REORG** | `GOAL-SRC-REORG.md` | Open GMR-8(b). |
| **RUNTIME RENAME / REORG** | `GOAL-RUNTIME-RENAME.md` / `GOAL-RUNTIME-REORG.md` | LI-CORE (Lon decision) / per-file CS subsystems. |
| **SCRIP RENAME** | `GOAL-SCRIP-RENAME.md` | 7-slice gated rename. |
| **⛔⭐⭐⭐ ICON 100% — THE ONE ICON GOAL** ⬅ Lon 2026-08-15 s229: 15 Icon goal files consolidated into ONE (THREE ZETAS: ζ-STANDING/ζ-ACTIVATION-FRAME on RBP, ζ-SPINE on RSP) | `GOAL-ICON-100.md` | R-0 = resurrect the default arm (fresh triple watermark at `07d6eae7`: default 1/262/30 · CELLS=1 235/28/30 · ZFRAME=0 78/185/30; bisect `8487d499..07d6eae7`, predicate proven at both ends). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | See file. |
| **Pascal BB** | `GOAL-PASCAL-BB.md` | 7th frontend (P4 subset); toolchain in `corpus/programs/pascal/`. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **PST Parent / SNOBOL4 / Snocone / Raku / Prolog** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` + `GOAL-PST-*.md` | See files. |
| **TEMPLATES X86 / JVM / .NET / JS / WASM** | `GOAL-TEMPLATES-*.md` | Per-backend; per-language state in `GOAL-*-BB.md`. |
| **IR REDESIGN** | `GOAL-IR-REDESIGN.md` | IRD-0 open. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2. |
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
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
