# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
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
1. **Read `GOAL-ICON-BB.md` (the live ground-zero goal) before anything else.** The former `GOAL-LANG-INDEPENDENT-RENAME.md` was deleted 2026-05-31 (bogus per Lon); its only valid residue — the icn-derived `gen_` rascal strip — is done and folded into Ground Zero.
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
| **SRC REORG** ⬅ #0 (Lon 2026-06-02) | `GOAL-SRC-REORG.md` | Physical re-partition of `src/` by pipeline role — kill the `include/` grab-bag, rename `runtime/interp/`→`builtins/` (it is NOT the interpreter), move the real mode-2 interpreter `lower/bb_exec.c`→`interp/`, give the contract types (DESCR/AST/IR/stage2) one home beside their allocators. 9-rung gated ladder (GMR-1a…GMR-FENCE). **ALL OTHER SESSIONS ON HOLD.** Next: GMR-1a. |
| **SCRIP RENAME** (Lon 2026-05-30) | `GOAL-SCRIP-RENAME.md` | Eradicate "SCRIP" everywhere — product is now SCRIP; SCRIP → private → deleted. 522 files / ~2482 occurrences across SCRIP + .github + corpus, plus 2 literally-named files (`REPO-SCRIP.md`, `GOAL-README-SCRIP.md`). 7-slice gated rung (RN-1 build scripts → RN-7 zero-check). `grand master reorg`: PLAN Repos table + clone scripts get updated. Next: RN-1 (fix `build_scrip.sh` $ROOT/SCRIP breakage). |
| **Ground Zero (Icon-BB)** ⬅ #1 | `GOAL-ICON-BB.md` | Icon-only, 100% Byrd Boxes, stackless. 2026-05-31: icn-derived `gen_` rascals stripped (prefix + `g_gen_`/`lower_gen_`/`rt_gen_` infixes); all comments + blank lines purged from `src` (.c/.h/.y/.l) with 200-char separators. Seed: `scrip --interp` → `hello`. `GOAL-LANG-INDEPENDENT-RENAME.md` deleted. |
| **ICON-BB** | `GOAL-ICON-BB.md` | See goal file for live state. *(corpus 93 PASS; next: `bb_call` builtins + generator re-pumping)* |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | See goal file for live state. *(GATE-3 m2/m3 **109/111**; retract/abolish/DCG/phrase/ITE landed `5c97162`. mode-4 prereq (GCONJ goals sidecar) landed → follow Icon/SNOBOL `codegen_flat_build` pattern at `scrip.c:532`; next: PLG-9a hello + PL-RT-ASSERTZ + 0'-char/atom_codes)* |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | See goal file for live state. *(ACTIVE 2026-05-31: ground-zero unified four-port AST→IR lower rewrite — `lower2.c` foundation laid + proven vs Proebsting Figs 1&2; SNOBOL pattern lowering = the PATTERN role. Prior pattern-BB-template track (native broad 255; deferred capture-commit, mode-2 DEFER, SPAN/ARBNO/FENCE) remains valid below it.)* |
| **Raku BB** | `GOAL-RAKU-BB.md` | ⏸ **ON HOLD** (2026-05-30). Raku development paused indefinitely. Grammar/subrule BB-generator tier deferred. SM-0+SM-1 clean; SM-2 diagnosed (BB_ITERATE/SM_CALL_FN mode-4 crash); resume when Raku is re-prioritized. |
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

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles AST to SM_Program. INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
