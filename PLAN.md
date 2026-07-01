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
1. **Read `GOAL-ICON-BB.md` (the live ground-zero goal — the generator/four-port model every BB language reuses) before anything else.**
2. Clone `.github`: `git clone https://github.com/snobol4ever/.github.git /home/claude/.github` (public,
   no token needed — verified by direct clone test, 2026-07-01; `git push` still needs a credential)
3. Read `PLAN.md`. Find goal in table below.
4. Read `RULES.md` in full.
5. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
6. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
7. **If MODE3-EMIT or MODE4-EMIT, or ANY Byrd-box codegen / template / BB-LOCAL-STORAGE work (every `GOAL-*-BB` rung qualifies) — read the BB-CODEGEN DESIGN SET first, NON-NEGOTIABLE:**
   - ⛔ **CORRECTED 2026-06-30 (Claude Sonnet 4.6) — every path below was checked against the actual repo this date and several were stale/wrong; do not trust this list at face value again without re-checking `find`/`grep` first, the same caution `GOAL-IR-IMMUTABLE-EMIT.md`'s own ORIENTATION SYNOPSIS demands.**
   - `ARCH-x86.md` — **STALE.** Describes a `BB_templates/`/`XA_templates/`/`emit_core.c`/`emit_bb.c`/`bb_pool` file layout and a 6-target/4-mode CLI (`--sm-interp`/`--sm-native`/`--bb-brokered`/`--target=`) that **do not exist in the current tree** (verified: `find . -iname BB_templates -o -iname XA_templates` empty; `scrip.c` parses exactly two mode flags, `--run` and `--compile`). The general "boxes are stackless, four ports, fresh DATA per α-entry" CONCEPTS are still the live design intent — only the concrete file/CLI claims are wrong. Current layout: `src/emitter/emit.cpp`+`emit.h` (the one driver) + flat `src/templates/*.cpp` (161 files, no subdirs).
   - `ARCH-ICON.md` — §"register contract" mostly holds (r13/r14/r15/rbx as stated) but its own text flags an internal disagreement with REGISTER-LAYOUT.md over what rbx means; that disagreement is resolved below.
   - `REGISTER-LAYOUT.md` — repeatedly cites `src/emitter/bb_regs.h` as "the single source of truth" even in its own "live" banner table. **That file does not exist** (verified: no `bb_regs.h` anywhere under `src/`). The register ROLES it states (r12=ζ frame, r13=Σ, r14=δ, r15=Δ, rbx=DESCR base, rbp=NV hash, r10 retired) are independently confirmed correct against `src/templates/x86_asm.h` (the actual current source of truth for the encoding); only the file-pointer is dead, not the convention.
   - `src/emitter/bb_regs.h` — **DOES NOT EXIST.** (Confirmed dead by `emit.h`'s own top-of-file comment: "bb_regs.h + emit_defs.h were dead and dropped".) The register convention's actual current source of truth is **`src/templates/x86_asm.h`** (`FR`/`FRQ` helpers, `x86_r12_modrm`, the `"r12"`/`"r13"`/`"r14"`/`"r15"` string literals) — r12=ζ RW frame `[r12+off]`, r13=Σ subject, r14=δ cursor, r15=Δ length, rbx=DESCR base, rbp=NV hash, r10 RETIRED, exactly as the roles above state; just read it from `x86_asm.h`, not `bb_regs.h`.
   - `src/emitter/XA_templates/xa_flat.cpp` — **DOES NOT EXIST** (`XA_templates/` directory is gone). The glob-preamble/r12-establishment logic now lives in `src/templates/xa_flat.cpp` (flat `src/templates/`, no `XA_templates/` subdirectory).
   - `ARCH-SCRIP.md` — **STALE.** Describes a 3-mode system (mode 2 `--run`/SM-interp, mode 3 `--run`/SM-JIT, mode 4 `--compile`) built on `sm_lower`→`sm_interp_run`/`sm_jit_run`. Verified: `sm_interp_run` and `sm_jit_run` do not exist anywhere in `src/` (`grep -rn` empty); only `sm_lower` survives, as a bare failure-message reference in `scrip_sm.c`. Current reality (confirmed via `scrip.c`'s argv parser): exactly two modes, `--run` (native x86 binary in-process) and `--compile` (x86 text asm → gcc → exec).
   - **For Icon-only BB/codegen work, also read `GOAL-IR-IMMUTABLE-EMIT.md`'s own "ORIENTATION SYNOPSIS" section** — it supplements the six docs above with verified current detail (build commands, corpus paths, register table with conflicts resolved). Read the six docs first; then read the SYNOPSIS. Do NOT substitute the SYNOPSIS for the six docs — it is additive, not a replacement.
   A `GOAL-*-BB` rung ASSUMES you have read these. If a rung touches per-box state and does not link here, that rung is defective — fix the rung's pointer before coding.
8. Open Goal file. Open that repo's REPO file.
9. Run Goal file's `## Session Setup` scripts.
10. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```
(Public, no token needed — verified by direct clone test, 2026-07-01.)

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **IR REDUCE / NO-MANGLE** ⬅ GROUND ZERO #5 (Lon 2026-06-27) | `GOAL-IR-IMMUTABLE-EMIT.md` | Emitter READS IR, never mutates it (45 mangle sites in emit_bb.c → 0) + collapse 224 IR opcodes toward the canonical JCON-33 reduced set, ONE BB per instruction. IRM-0 gate landed. **[CORRECTED 2026-07-01: the `operand_aux` deletion this row previously claimed as landed is NOT true — `bb_operand_aux_set` has 5 live call sites (lower_icon.c ×2, lower_prolog.c, lower_pascal.c ×2) and `bb_operand_aux_get` 3 (emit.cpp, scrip.c ×2), grep-verified; RULES.md's PEERS RULE remains the accurate description.]** **All 5 language BB sessions build on this clean spine — do FIRST.** |
| **Raku BB (OOP)** | `GOAL-RAKU-BB.md` | OO LADDER at the TOP of `GOAL-RAKU-BB.md`, top-to-bottom (first `- [ ]` rung). See goal file. |
| **DE-INTERP** ✅ DONE (Claude 2026-06-15) | `GOAL-DE-INTERP.md` | ✅ CLOSED — all 8 steps landed (SCRIP `1d113eb`/`f60bb08`/`4c9b6bd`). `interp` misnomer eradicated; completion grep = only the 4 legitimate survivors. No `src/interp` dir, no `interp.h`/`pl_interp.h`, no `scrip-interp`. Behavior-neutral. Goal file CLOSED. |
| **DEAD-CODE SWEEP** ⬅ (Sonnet 2026-06-14) | `GOAL-DEAD-CODE-SWEEP.md` | Batch 4 landed (`5e483bf`): documented-20 RESOLVED (19 cut + 1 closed-subgraph non-removable). Oracle 59→43 dead. Fixpoint surfaced (rt_in_native_chunk + other-lexer input/yyunput). See goal file batch-4 handoff. |
| **BB-FIXUP** ⬅ NEW (Lon 2026-06-04) | `GOAL-BB-FIXUP.md` | Attended round-robin hygiene sweep; cursor in `.github/BB-REVAMP-TRACKER.md`. See goal file. |
| **SRC REORG** ⬅ #0 (Lon 2026-06-02) | `GOAL-SRC-REORG.md` | Re-partition `src/` by pipeline role. Open: GMR-8(b). See goal file. |
| **RUNTIME RENAME** (Lon 2026-06-02) | `GOAL-RUNTIME-RENAME.md` | DE-NAME emitter/runtime. Open: LI-CORE (Lon decision). See goal file. |
| **RUNTIME REORG** (Lon 2026-06-02) | `GOAL-RUNTIME-REORG.md` | Each runtime FILE → CS subsystem. See goal file. |
| **SCRIP RENAME** (Lon 2026-05-30) | `GOAL-SCRIP-RENAME.md` | 7-slice gated rename rung. See goal file. |
| **Ground Zero (Icon-BB)** ⬅ #1 | `GOAL-ICON-BB.md` | Icon-only, 100% Byrd Boxes, stackless. See goal file for live state. |
| **ICN-GVA-M3** | `GOAL-ICN-GVA-M3.md` | Extend Icon globals to `[rbx+k*16]` in mode-3 (in-process RX slab). 4 steps: M3-ARENA-1/2/3/4. Prereq: ICN-GVA (mode-4) DONE. |
| **ICON-BB** | `GOAL-ICON-BB.md` | See goal file for live state. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | See goal file for live state. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | See goal file for live state. |
| **Raku BB** | `GOAL-RAKU-BB.md` | See the Raku BB (OOP) row above and the OO LADDER in the goal file. |
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

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. LOWER compiles AST to the shared IR graph **[CORRECTED 2026-07-01: an OPTIMIZER stage now sits between LOWER and the EMITTER — `src/optimizer/`, `optimizer_run(g)` before both `ir_drive_slot_assign` sites, env-gated `SCRIP_OPT` (OFF by default), per GOAL-IR-IMMUTABLE-EMIT.md's 2026-07-01 OPTIMIZER session close]**. The IR graph's consumer is the EMITTER (`emitter/`, the per-box templates + dispatch + x86 encoders) walks it and emits native code in TWO 1:1-corresponding modes — mode-3 BINARY in-process / mode-4 TEXT via as+gcc (JVM/.NET/JS/WASM arms dormant under X86-ONLY). Modes 1 and 2 are DELETED (no AST-walk evaluator, no IR-graph software interpreter); see GOAL-MODE34-IDENTICAL.md.

`src/` layout by pipeline role: `parser/` (the 6 language front-ends) · `contracts/` (the spine types beside their allocators: descr, ast, ir, stage2, SM opcode enum) · `lower/` (AST→IR only) · `emitter/` (BB/XA templates + dispatch, serves mode-3 and mode-4) · `machine/` (the RX slab + stage2 preamble) · `runtime/` (the library: `core/` SNOBOL model, `rt/` shared low-level helpers, `builtins/` generator/scanner/resolver/builtin tables) · `driver/` (CLI + mode-3/mode-4 selector) · `backends/` (dormant non-x86: driver+runtime sides + jasmin.jar) · `tools/` (proof/scaffolding harnesses) · `attic/` (dead Stack-Machine residue).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
