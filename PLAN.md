# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog, Pascal. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of SCRIP / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`).

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself.

### Milestone 3 ⏳
All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. **Read `GOAL-ICON-BB.md` (the live ground-zero goal) before anything else.**
2. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
3. Read `PLAN.md`. Find goal in table below.
4. Read `RULES.md` in full.
5. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
6. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
7. **If MODE3-EMIT or MODE4-EMIT — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.**
8. Open Goal file. Open that repo's REPO file.
9. Run Goal file's `## Session Setup` scripts.
10. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **DE-INTERP** ⬅ NEW (Lon 2026-06-15) | `GOAL-DE-INTERP.md` | Interpreter is DELETED → eradicate the `interp` misnomer from every live file/dir/symbol/guard/Makefile target; relocate survivors to their true-role files. RUNG + 8 STEPS + true-role map in goal file. Step 1 (baseline) open. |
| **DEAD-CODE SWEEP** ⬅ NEW (Sonnet 2026-06-14) | `GOAL-DEAD-CODE-SWEEP.md` | GC oracle identified 601 dead functions; pass 1 done (10 symbols removed). ~585 remaining. See goal file for full list + attic policy. |
| **BB-FIXUP** ⬅ NEW (Lon 2026-06-04) | `GOAL-BB-FIXUP.md` | Attended round-robin hygiene sweep; cursor in `.github/BB-REVAMP-TRACKER.md`. See goal file. |
| **SRC REORG** ⬅ #0 (Lon 2026-06-02) | `GOAL-SRC-REORG.md` | Re-partition `src/` by pipeline role. Open: GMR-8(b). See goal file. |
| **RUNTIME RENAME** (Lon 2026-06-02) | `GOAL-RUNTIME-RENAME.md` | DE-NAME emitter/runtime. Open: LI-CORE (Lon decision). See goal file. |
| **RUNTIME REORG** (Lon 2026-06-02) | `GOAL-RUNTIME-REORG.md` | Each runtime FILE → CS subsystem. See goal file. |
| **SCRIP RENAME** (Lon 2026-05-30) | `GOAL-SCRIP-RENAME.md` | 7-slice gated rename rung. See goal file. |
| **Ground Zero (Icon-BB)** ⬅ #1 | `GOAL-ICON-BB.md` | Icon-only, 100% Byrd Boxes, stackless. See goal file for live state. |
| **ICON-BB** | `GOAL-ICON-BB.md` | See goal file for live state. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | See goal file for live state. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | See goal file for live state. |
| **Raku BB** | `GOAL-RAKU-BB.md` | ⏸ ON HOLD (2026-05-30); resume on Lon's word. See goal file. |
| **Pascal BB** | `GOAL-PASCAL-BB.md` | 7th frontend (P4 subset); reference toolchain in `corpus/programs/pascal/`. See goal file. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **PST Parent** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | Stage 2 PST-LR-0 bulk rename. |
| **PST SNOBOL4** | `GOAL-PST-SNOBOL4.md` | SN4-SC-6 smoke blocked by EC-3* regression. |
| **PST Snocone** | `GOAL-PST-SNOCONE.md` | MIRROR-GAP-SC-SC-5: XDSAR in bb_build_brokered. |
| **PST Raku** | `GOAL-PST-RAKU.md` | PRF-14-6 OPEN — leaf-pushers misuse shift. |
| **PST Prolog** | `GOAL-PST-PROLOG.md` | PST-PL-SC — delete ~64 helpers, rewrite grammar. |
| **TEMPLATES x86** | `GOAL-TEMPLATES-X86.md` | Backend: x86 (mode-3 native + mode-4 compile), all languages. Per-language state in `GOAL-*-BB.md`. |
| **TEMPLATES JVM** | `GOAL-TEMPLATES-JVM.md` | Backend: JVM (Jasmin → .class), all languages. |
| **TEMPLATES .NET** | `GOAL-TEMPLATES-NET.md` | Backend: SCRIP MSIL emitter (≠ snobol4dotnet repo), all languages. |
| **TEMPLATES JS** | `GOAL-TEMPLATES-JS.md` | Backend: JavaScript (node), all languages. |
| **TEMPLATES WASM** | `GOAL-TEMPLATES-WASM.md` | Backend: WebAssembly (WAT → node host), all languages. |
| **IR REDESIGN** ⬅ NEW (Lon 2026-06-07) | `GOAL-IR-REDESIGN.md` | Slim IR_t: drop value/counter/state; rename α→a β→b; exec state → parallel array. IRD-0 open. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed; IEP-5/6/7/9 blocked on CHUNKS. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2 — delete bb_node_t path. |
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

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. LOWER compiles AST to the shared IR graph. From the IR graph there are two consumers: the mode-2 INTERP (`interp/IR_interp.c`, the IR-graph interpreter — formerly mis-named `bb_exec.c`) executes it in software; the EMITTER (`emitter/`, the per-box templates + dispatch + x86 encoders) walks it and emits native code (mode-3 BINARY in-process / mode-4 TEXT via as+gcc; JVM/.NET/JS/WASM arms dormant under X86-ONLY).

`src/` layout by pipeline role: `parser/` (the 6 language front-ends) · `contracts/` (the spine types beside their allocators: descr, ast, ir, stage2, SM opcode enum) · `lower/` (AST→IR only) · `interp/` (the mode-2 IR-graph interpreter + its execution-state structs) · `emitter/` (BB/XA templates + dispatch, serves mode-3 and mode-4) · `machine/` (the RX slab + stage2 preamble) · `runtime/` (the library: `core/` SNOBOL model, `rt/` shared low-level helpers, `builtins/` generator/scanner/resolver/builtin tables) · `driver/` (CLI + A/B/C mode selector) · `backends/` (dormant non-x86: driver+runtime sides + jasmin.jar) · `tools/` (proof/scaffolding harnesses) · `attic/` (dead Stack-Machine residue).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
