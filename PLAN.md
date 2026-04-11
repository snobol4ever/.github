# PLAN.md — snobol4ever / SCRIP HQ Plan

## ⚠️ ARCHITECTURE RESET — 2026-04-04
## The interpreter must execute SM_Program (stack machine instructions), NOT tree-walk IR.
## Read SCRIP-SM.md FIRST every session. See Component Map below.

**Product:** SCRIP — Snobol4, SnoCone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes (arch), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (co-author).

---

## ⛔ SESSION START — every session, no exceptions

**Step 0 — Check NOW table first (one grep, 10 seconds):**
```
grep -A2 "^| \*\*Silly SNOBOL4\*\*\|^| \*\*RUNTIME\|^| \*\*SNOBOL4 × x86" /home/claude/.github/PLAN.md
```
If the NOW row tells you exactly what to do next (HEAD + next action), **skip Steps 1–3 and start working immediately.**
Only read Steps 1–3 if the NOW row is ambiguous or you need broader context.

**Step 1 — Orientation only (3 reads max, SKIP if Step 0 was sufficient):**
```
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # sprint handoff state
grep "^## " /home/claude/.github/GENERAL-RULES.md    # rules headers only — ⛔ includes HANDOFF rule
cat /home/claude/.github/PLAN.md                      # this file (NOW table + routing)
```

**Step 2 — Read your component doc (session-specific, ONE doc):**
```
Track C  scrip / SIL  →  cat MILESTONE-RT-RUNTIME.md   (RUNTIME-3 section only — grep "^## RUNTIME-3" and read to next "^## RT-")
Track A  sno4parse            →  cat MILESTONE-SN4PARSE-VALIDATE.md
Track B  emitter x86          →  cat EMITTER-X86.md
Track BB Byrd box / SM        →  cat SCRIP-SM.md + BB-GRAPH.md + BB-DRIVER.md + IR.md
```
⚠️ BB-GRAPH.md, BB-DRIVER.md, SCRIP-SM.md, IR.md are ONLY for Track BB (emitter/SM work).
Do NOT read them for Track C (scrip / RT milestone work).

**Step 3 — Read SESSION-<frontend>-<backend>.md §INFO + §NOW only**
```
cat /home/claude/.github/SESSION-<frontend>-<backend>.md
```
The SESSION doc has two mandatory sections:
- `## ⛔ §INFO` — session invariants (tool locations, oracle setup, baselines,
  don't-do-X warnings). Append-only. Read before touching anything.
- `## §NOW` — current sprint, HEAD hashes, next milestone, first actions.

---

## The Architecture in One Paragraph

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared IR
(Program* of STMT_t/EXPR_t). SM-LOWER compiles IR to SM_Program — a flat array of stack
machine instructions. The INTERP executes SM_Program by dispatching instructions. When it
hits SM_EXEC_STMT, it calls BB-DRIVER which runs the BB-GRAPH built by preceding SM_PAT_*
instructions. The EMITTER walks the same SM_Program and emits native code (x86, JVM, .NET,
JS, WASM). Interpreter and emitter share one instruction set. When the interpreter passes
the corpus, the emitter is correct by construction.

---

## The 6 Frontends × 6 Backends

| | x86 | JVM | .NET | JS | WASM | C |
|--|:---:|:---:|:----:|:--:|:----:|:-:|
| SNOBOL4 | DYN | J | D | SJ | ⛔ | — |
| Icon | IX | IJ | — | IJJ | ⛔ | — |
| Prolog | PX | PJ | — | PJJ | ⛔ | — |
| Snocone | SC | — | — | — | — | — |
| Rebus | — | — | — | — | — | — |
| **SCRIP** | — | SD | — | — | — | — |

---

## Component Map — one doc per component

| Component | Doc | Status |
|-----------|-----|--------|
| **⭐ NET — Beauty Suite 19/19** | `MILESTONE-NET-BEAUTY-19.md` | ⚠️ **CURRENT PRIORITY #1** — snobol4dotnet passes all 19 beauty drivers. Baseline D-214b established. Session D-215. |
| **⭐ NET — Beauty Self-Hosting** | `MILESTONE-NET-BEAUTY-SELF.md` | ⚠️ **CURRENT PRIORITY #2** — beauty.sno self-beautifies via snobol4dotnet. Gates on MILESTONE-NET-BEAUTY-19 (19/19). |
| **⭐ SNOBOL4 × x86 — SCRIP TRACE/MONITOR** | `MILESTONE-SN4X86-SCRIP-TRACE.md` | ⚠️ **CURRENT** — Wire TRACE/STOPTR/DUMP/comm_var/monitor into scrip --ir-run. T-0: set_and_trace(). T-1: comm_stno(). T-2: CALL/RETURN hooks. T-3: run_monitor_2way.sh. T-4: monitor 5 failing beauty drivers. Gate: beauty 19/19 → B-3. |
| **SCRIP Unified Executable** | `SCRIP-UNIFIED.md` | ✅ designed · U0 complete (2026-04-07) · binary=`scrip` · default=`--sm-run` |
| **SCRIP Stack Machine** | `SCRIP-SM.md` | ✅ designed · ⬜ SM-LOWER not written |
| **IR** | `IR.md` | ✅ complete |
| **BB-GRAPH** | `BB-GRAPH.md` | ✅ 25 boxes complete |
| **BB-DRIVER** | `BB-DRIVER.md` | ✅ correct (in stmt_exec.c) |
| BB-GEN x86 binary | `BB-GEN-X86-BIN.md` | ✅ M-DYN-B0–B13 complete (2026-04-08) · next: M-DYN-BENCH-X86 (already have results in HQ) |
| BB-GEN x86 text (.s) | `BB-GEN-X86-TEXT.md` | ✅ boxes exist as .s |
| BB-GEN languages | `BB-GEN-LANG.md` | ✅ C+Java done · others stub |
| **INTERP x86 (C)** | `INTERP-X86.md` | ⚠️ tree-walks IR — needs SM_Program |
| INTERP JVM (Java) | `INTERP-JVM.md` | ⬜ in progress |
| INTERP .NET (C#) | `INTERP-NET.md` | ⬜ in progress |
| INTERP JS | `INTERP-JS.md` | ⬜ in progress |
| INTERP WASM | `INTERP-WASM.md` | ⛔ parked |
| EMITTER x86 | `EMITTER-X86.md` | ⬜ needs SM_Program input |
| EMITTER JVM | `EMITTER-JVM.md` | ⬜ in progress |
| EMITTER .NET | `EMITTER-NET.md` | ⬜ in progress |
| EMITTER JS | `EMITTER-JS.md` | ⬜ in progress |
| LINKER | `LINKER.md` | ⬜ in progress |
| LEXER / PARSER (6× each) | `LEXER-*.md` / `PARSER-*.md` | ⬜ stubs needed |
| **SN4PARSE oracle** | `MILESTONE-SN4PARSE.md` | ⚠️ in progress — DYN-85 |
| **SN4PARSE validation** | `MILESTONE-SN4PARSE-VALIDATE.md` | ⬜ next after M-SN4PARSE |
| **RUNTIME** | `RUNTIME.md` | ✅ E=mc² model, EVAL/CODE/EXPRESSION/NAME |
| **Silly SNOBOL4 — faithful C rewrite of v311.sil** | `MILESTONE-SILLY-SNOBOL4.md` · `SESSION-silly-snobol4.md` | ⚠️ SS-39 — M-SS-BLOCK-FORWARD: watermark 3222 → 12293 · M-SS-BLOCK-BACKWARD: watermark 6438 → 1 · both run independently to completion |
| **M-SS-WARNINGS** | `MILESTONE-SS-WARNINGS.md` | ✅ **DONE** `98a5c215` — zero warnings: INTR1_fn/chk_break decls, FRZNSTR removed, DESCR_t initialisers explicit |
| **M-SS-COMPLETE** | `MILESTONE-SS-COMPLETE.md` | ⚠️ **#1 PRIORITY** — A1 ✅ A2 ✅ `ec9b1fb0` · **A3 NEXT: RECOMJ+CODER+CONVE+CONVEX in func.c** · A4: DEFFNC_fn · BLOCKS last (after FWD+BWD done) |
| **M-SS-BLOCK-BACKWARD** | `MILESTONE-SS-BLOCK-BACKWARD.md` | ⚠️ watermark 6438 (COPY) — next: COLECT (6427) — runs to line 1 |
| **M-SS-BLOCK-FORWARD** | `MILESTONE-SS-BLOCK-FORWARD.md` | ⚠️ watermark 3222 — next: NAM (line 3223) — runs to 12293 |
| **Silly SNOBOL4 × CSNOBOL4 Sync-Step Monitor** ⚠️ CSNOBOL4 is oracle here by construction | `MILESTONE-SS-MONITOR.md` · `SESSION-silly-snobol4.md` | ⚠️ in progress — M-SS-MON-0..4 complete · M-SS-MON-5 (hello world passes) next |
| **SIL MACRO MAP** | `MILESTONE-RT-SIL-MACROS.md` | ✅ classified — 12 new SM ops, sil_macros.h design |
| **RUNTIME / RUNTIME-1** | `MILESTONE-RT-RUNTIME.md` | ✅ INVOKE_fn + ARGVAL_fn — done |
| **RUNTIME / RUNTIME-2** | `MILESTONE-RT-RUNTIME.md` | ✅ VARVAL/INTVAL/PATVAL/VARVUP — done |
| **RUNTIME / RUNTIME-3** | `MILESTONE-RT-RUNTIME.md` | ✅ NAME_fn + ASGNIC_fn + DT_N/DT_K — done |
| **RUNTIME / RUNTIME-4** | `MILESTONE-RT-RUNTIME.md` | ✅ NAM_push/commit/discard (snobol4_nmd.c) — done |
| **RUNTIME / RUNTIME-5** | `MILESTONE-RT-RUNTIME.md` | ⚠️ **CURRENT PRIORITY** — NV_SET_fn→DESCR_t + OUTPUT/TRACE hooks |
| **RUNTIME / RUNTIME-6** | `MILESTONE-RT-RUNTIME.md` | ⚠️ **CURRENT PRIORITY** — EXPVAL_fn / EXPEVL_fn (declared, not implemented) |
| **RUNTIME / RUNTIME-7** | `MILESTONE-RT-RUNTIME.md` | ⚠️ **CURRENT PRIORITY** — CONVE_fn + CODE_fn + CONVERT_fn full matrix |
| **RUNTIME / RUNTIME-8** | `MILESTONE-RT-RUNTIME.md` | ⚠️ **CURRENT PRIORITY** — EVAL_fn full dispatch → PASS=178 gate |
| **RUNTIME / RUNTIME-9** | `MILESTONE-RT-RUNTIME.md` | ⬜ INTERP/INIT/GOTO SM_Program loop (depends RT-5–8) |
| **CMPILE MERGE** | `MILESTONE-CMPILE-MERGE.md` | ✅ Phases 0-2 COMPLETE — Phase 3 (--parser switch) pending |
| CORPUS | `CORPUS.md` | ✅ |
| HARNESS | `HARNESS.md` | ✅ |
| MONITOR | `MONITOR.md` | ✅ |
| **CSNOBOL4 FENCE** | `MILESTONE-CSNOBOL4-FENCE.md` | ⬜ add FENCE() to CSNOBOL4 using SPITBOL as semantic guide |
| BENCHMARK-GRID | `BENCHMARK-GRID.md` | ⬜ placeholders |
| **CMPILE ONE-PASS** | `MILESTONE-CMPILE-ONEPASS.md` | ⬜ LOWEST PRIORITY — do not begin until all other milestones complete |

---

## ⚡ NOW

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **SNOBOL4 × x86** | BEAUTY | one4all `f23ef24c` · corpus `3fd44d0` · INTERP=./scrip --ir-run PASS=193/203 · beauty suite 14/19 | **CURRENT: MILESTONE-SN4X86-SCRIP-TRACE** — Wire TRACE/STOPTR/DUMP/SETEXIT + sync-step 2-way monitor (SPITBOL vs scrip --ir-run) into ir-run path. T-0: `set_and_trace()` helper at all NV_SET sites in scrip.c. T-1: replace manual stcount/stlimit with `comm_stno()`. T-2: CALL/RETURN hooks in call_user_function(). T-3: `run_monitor_2way.sh`. T-4: run monitor on 5 failing beauty drivers → first diverging event names each bug. Gate: all 5 EXIT 0 → beauty 19/19 → B-3. See MILESTONE-SN4X86-SCRIP-TRACE.md. |
| **one4all-SNOBOL4-NET** | D-215 | snobol4dotnet `b280881` · corpus `5c8aa22` · **2375p/0f/2s** | **NEXT: MILESTONE-NET-BEAUTY-19** (7/19 → 19/19) · then MILESTONE-NET-BEAUTY-SELF |
| **RUNTIME (SCRIP unified)** | RT-139 | one4all `bc310aa6` · corpus `3fd44d0` · --sm-run PASS=163 / --ir-run PASS=178 | **CURRENT PRIORITY: RUNTIME-5 → RUNTIME-8 in order.** RT-5: `NV_SET_fn` → `DESCR_t` + OUTPUT/TRACE hook tables. RT-6: implement `EXPVAL_fn`/`EXPEVL_fn` in `eval_code.c`. RT-7: `CONVE_fn` + `CODE_fn` + full `CONVERT_fn` matrix. RT-8: `EVAL_fn` full DT_E/DT_S/DT_I/DT_R dispatch → PASS=178 gate. Then: field mutator LHS fix (`lson(b) = a`). |
| **Silly SNOBOL4** | SS-39 | one4all `ec9b1fb0` | **#1: M-SS-COMPLETE** — A2 ✅ · **A3 NEXT: RECOMJ cluster in func.c** (v311.sil 6492–6551) · A4: DEFFNC_fn · then FWD+BWD · BLOCKS last |
| **Snocone x86** | SC-14 | `05a50e8` one4all · `7729763` corpus | M-SC-SELFTEST |
| **TINY JVM** | J-233 | one4all `b8560bb` | J-234: 1011_func_redefine + 1017_arg_local → ≥165p |
| **SNOBOL4 JS** | SJ-26 | one4all `d7cf03e` | 174p/4f · SJ-27: engine re-entrancy fix → ≥175p |

---

## File Taxonomy

| Prefix | Purpose |
|--------|---------|
| `SCRIP-SM.md` | Stack machine — THE central design doc |
| `BB-*.md` | Byrd Box components |
| `IR.md` | Shared intermediate representation |
| `INTERP-*.md` | Per-platform interpreters |
| `EMITTER-*.md` | Per-platform emitters |
| `LEXER-*.md` | Per-language lexers |
| `PARSER-*.md` | Per-language parsers |
| `LINKER.md` | Linker |
| `CORPUS.md` / `HARNESS.md` / `MONITOR.md` / `TESTING.md` | Test infrastructure |
| `BENCHMARK-GRID.md` | Benchmark results |
| `GENERAL-*.md` | Cross-cutting reference (decisions, rules, vision, ABI) |
| `ARCHIVE-*.md` | Completed or parked work |
| `MISC-*.md` | Background, reference, one-off docs |
| `SESSION-*.md` | Per-session operational state |
| `MILESTONE-*.md` | Milestone ladders |
| `SESSIONS_ARCHIVE.md` | Append-only session log |

---

*PLAN.md = routing + NOW + component map. No sprint content. No completed milestones.*
*Architecture reset: DYN-82 session, 2026-04-04, Lon Jones Cherryholmes + Claude Sonnet 4.6.*
