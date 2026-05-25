# GOAL-ICON-BB.md — Icon Byrd-Box templates, hello-world → algorithms, one rung at a time

**Repo:** one4all + corpus + .github
**Sister docs:** `GOAL-HEADQUARTERS.md` (the template system), `GOAL-PROLOG-BB.md` (mirror), `GOAL-BB-TEMPLATE-LADDER.md`, `GOAL-LANG-ICON.md`
**Carved:** 2026-05-10 · **Rewritten as a template-construction ladder:** 2026-05-25

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ READ FIRST — THE ONLY LEGAL WAY TO MAKE A BYRD BOX EXIST                                     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A Byrd box is x86 ASSEMBLY TEXT returned by a C++ template function. It is NOT a C function.    ║
║                                                                                                  ║
║  FORBIDDEN — instant rejection (RULES.md, HQ Invariant #2 + #16):                               ║
║    DESCR_t foo(void *zeta, int entry) { ...four-port logic... }   ← NEVER write this            ║
║    Any new function that emits code without carrying a BB / SM / XA opcode.                     ║
║                                                                                                  ║
║  REQUIRED — every Byrd box is born exactly these six steps:                                     ║
║    1. A `BB_<KIND>` enum value (already in the IR — see ir.h).                                   ║
║    2. A template file `src/emitter/BB_templates/bb_<kind>.cpp` whose body is a pure              ║
║       `std::string bb_<kind>_str(BB_t * pBB)` returning                                          ║
║         IF(MEDIUM_MACRO_DEF, …) + IF(MEDIUM_BINARY, …) + IF(MEDIUM_TEXT, …);                     ║
║       guarded by `if (PLATFORM_X86)`. JVM/JS/NET/WASM arms `return std::string();`.             ║
║    3. A case in `walk_bb_node` (src/emitter/emit_core.c) routing the kind → `bb_<kind>(nd)`.    ║
║    4. A forward decl in `BB_templates/bb_templates.h`.                                           ║
║    5. TWO Makefile edits: add to the BB_SRCS list AND add an explicit `.o` rule.                ║
║    6. An SM root hook that emits the opcode driving this BB (see §"The SM→BB hook").             ║
║                                                                                                  ║
║  If you just wrote `DESCR_t foo(void *zeta, int entry)` — DELETE IT and do the six steps.        ║
║  The ONLY exempt C function with that signature is `icn_bb_dcg` (infrastructure DCG driver).    ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 (RULES.md). Mode 1 is DELETED. `--interp` = mode 2 (SM).      ║
║  No `tree_t*` deref (`->t/->c[]/->n/->v`) in sm_interp.c, sm_jit_interp.c, or src/emitter/*.    ║
║  A `[NO-AST] <opcode>` print + `last_ok=0` is the honest tripwire. Fix = write SM/BB lowering.  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

---

## Current reality (verified 2026-05-25 — READ before starting)

**Icon BB templates are STUBS today. This is the work.**

- `BB_templates/bb_icn_to.cpp` and `bb_icn_to_by.cpp` exist but their bodies are `return std::string();` — they emit NOTHING.
- `walk_bb_node` routes ~30 Icon BB kinds (`BB_ICN_UPTO`, `BB_ICN_ALTERNATE`, `BB_ICN_LIMIT`, `BB_ICN_SCAN`, `BB_ICN_SECTION`, `BB_ICN_ITERATE`, …) to `bb_icn_stub` / `bb_cset`, which are placeholders.
- Upstream, the SM root hooks `SM_BB_EVAL`, `SM_BB_PUMP_EVERY`, `SM_BB_PUMP_CASE` are **emitted by `lower.c` but have NO x86 dispatch case** — they fall through `codegen_sm_dispatch` `default: return 0` and VANISH silently. That is the cause of widespread Icon mode-3/4 segfaults/aborts. (Simple every-loops route through `SM_BB_PUMP_PROC`, which IS wired and works — that is your starting exemplar on the SM side.)

**Your job:** fill the stub template bodies AND wire their SM root hooks, one rung at a time, copying the live patterns that already work. You are NOT inventing the system — you are extending it.

**Exemplars to copy (REAL fully-fleshed templates — open them before writing a line):**
- Generator-shaped BB with α/β ports + back-label: `BB_templates/bb_pat_span.cpp` (FOR(0,2,…) over ports, `_.lbl_succ`/`_.lbl_back`/`_.lbl_fail`, BINARY rel32 patch slots, TEXT gas).
- Scalar/leaf BB: `BB_templates/bb_lit_scalar.cpp`.
- SM root hook that drives a BB by name: `SM_templates/sm_bb_calls.cpp` (`sm_bb_once_proc` / `sm_bb_pump_proc` — the MACRO_DEF+BINARY+TEXT shape every SM root hook follows).
- Structural mirror in another language (further along): `bb_pl_atom.cpp` / `bb_pl_arith.cpp` — the `IF(MEDIUM_*)`-concat idiom outside SNOBOL4.

---

## The SM→BB hook (how an Icon construct reaches a template)

```
.icn → icon_parse() → AST_t*
   lower.c   walks AST, emits SM_Program. For a generator/every/case construct it emits
             ONE Icon SM ROOT HOOK:  SM_BB_EVAL / SM_BB_PUMP_EVERY / SM_BB_PUMP_CASE
             (today: emitted but UNWIRED). Simple every → SM_BB_PUMP_PROC (wired, works).
   ── mode 2 (--interp)   sm_interp.c       dispatches the opcode → drives the BB via bb_broker
   ── mode 3 (--run)      sm_jit_interp.c   same, JIT
   ── mode 4 (--compile)  src/emitter/emit_sm.c   emits the opcode's x86; that x86 calls the
             runtime BB driver, which per BB node calls walk_bb_node(nd) → bb_<kind>(nd)
             → your template's assembly text.
```

A rung is complete only when ALL FOUR exist: (a) `lower.c` emits the SM root hook; (b) the hook has an `emit_sm.c` x86 case (mode 4) + interp/jit cases (modes 2/3); (c) every BB kind the construct lowers to has a non-stub `bb_<kind>.cpp` wired in `walk_bb_node`; (d) gates green across modes.

⛔ **Cheating tripwire.** `SCRIP_NO_AST_WALK=1 ./scrip --interp` MUST equal `./scrip --interp`. If a construct silently falls back to `coro_eval`/AST interp, the NO_AST run aborts or diverges. Output equality alone is NOT sufficient.

---

## Session Setup

```bash
cd /home/claude/one4all
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh                 # builds scrip + libscrip_rt.so
```

Optional Icon oracle (validate/regenerate `.expected`): `/home/claude/icon-master/bin/{icont,iconx}` if present.

### Baseline gates — capture BEFORE touching anything; must not regress

```bash
bash scripts/test_smoke_icon.sh                              # inline smokes
bash scripts/test_icon_all_rungs.sh                          # --interp ladder rung01..rung37
bash scripts/test_crosscheck_icon.sh                         # 3-mode (ir/sm/jit) consistency
bash scripts/test_smoke_unified_broker.sh                    # cross-language broker, Icon rows
SCRIP_NO_AST_WALK=1 bash scripts/test_icon_all_rungs.sh      # the HONEST dial
```

Record the four numbers (smoke / --interp / crosscheck / honest) in the watermark.

---

## The corpus ladder (already on disk — `/home/claude/corpus/programs/icon/`)

Each rung is `rungNN_*.icn` files with `.expected` (and optional `.stdin`, `.xfail`). The ladder already climbs hello-world → algorithms; you make the BB/template machinery PASS each rung honestly, in order.

```bash
bash scripts/test_icon_all_rungs.sh --rung rung04               # one rung, --interp
bash scripts/util_crosscheck_3mode.sh <file.icn> [oracle.ref]   # one file, all 3 modes
```

Run `ls /home/claude/corpus/programs/icon/rungNN_*` to see exact files per rung.

| Rung | Theme | First constructs that must lower to non-stub BBs |
|------|-------|--------------------------------------------------|
| 01 | paper §2 generators | `i to j`, `*`, `<`, nested `to`, `every write(...)` — `BB_ICN_TO`, `SM_BB_PUMP_EVERY` |
| 02 | arith + proc | binops as generators, user `procedure` call |
| 03 | conditionals | `if/then/else`, comparison generators |
| 04 | strings | `||` concat, string scalars |
| 05–07 | control flow | `while`/`until`/`repeat`, `every`, conjunction `&` |
| 08 | string builtins | size/find/etc. |
| 09 | loops | nested loops, `break`/`next` |
| 10–12 | relops + size | string relops, `*x` size |
| 13 | gen in value context | `BB_ICN_ALTERNATE`, conjunction-in-generator |
| 14 | limit | `\` limit — `BB_ICN_LIMIT` |
| 15 | iterate | `!E` bang — `BB_ICN_ITERATE`, `BB_ICN_LIST_BANG` |
| 16–20 | scan / section / seqexpr | `? {…}`, `s[i:j]`, `(e;e)` |
| 21–24 | globals / records / fields | `initial{}`, record def, field get/set |
| 25–35 | tables, csets, real arith, key-gen, augops | richer generator contexts |
| 36 | JCON-scale programs | full algorithms (timeout 30s) |
| 37 | extended | additional algorithm set |

JCON gold for port semantics: `/home/claude/jcon-extract/jcon-master/tran/irgen.icn` (`ir_a_<Construct>` procedures). Icon four-port = Proebsting start/resume/succeed/fail.

---

## Rung procedure — DO THIS for every rung (do not skip ahead, do not batch)

1. **Pick the lowest red rung.** `bash scripts/test_icon_all_rungs.sh --rung rungNN`. Read each failing `.icn` and its `.expected`.
2. **Identify construct → SM root hook → BB kinds.** Dump the SM (`./scrip --emit-sm file.icn` or the available SM-dump mode). Note which `SM_BB_*` opcode `lower.c` emits and which `BB_*` kinds appear. A `[NO-AST] SM_BB_EVAL/PUMP_EVERY/PUMP_CASE` print = that hook is unwired = your target.
3. **Wire the SM root hook (if unwired).** Add the x86 dispatch case in `src/emitter/emit_sm.c` (copy `emit_sm_bb_once_proc_dispatch` / the `sm_bb_pump_proc` shape) and the mode-2/3 cases in `sm_interp.c` / `sm_jit_interp.c` (copy the live `SM_BB_PUMP_PROC` handler). The hook looks up the IR block and drives it via `bb_broker`.
4. **Fill the BB template(s).** For each stubbed `BB_*` kind the rung needs:
   - Open the closest live exemplar (`bb_pat_span.cpp` generator, `bb_lit_scalar.cpp` leaf).
   - Write `bb_<kind>_str(BB_t*)` returning `IF(MEDIUM_MACRO_DEF,…)+IF(MEDIUM_BINARY,…)+IF(MEDIUM_TEXT,…)`, x86-only. Keep EVERY medium's `IF()` slot even if empty (`IF(MEDIUM_BINARY, std::string())`) — a missing slot turns the three-section AUDIT red.
   - TEXT arm: readable gas, `_.lbl_succ`/`_.lbl_back`/`_.lbl_fail`, `call rt_<helper>@PLT`. BINARY arm: same bytes + rel32 patch slots. MACRO_DEF arm: `.macro`/`.endm` form or `# no macro form` comment.
   - **No runtime C Byrd box.** If the BB needs runtime help, add a PLAIN helper to `src/runtime/rt/rt.c` (e.g. `rt_bb_icn_to`) that the emitted asm CALLS — a callee, not a four-port box.
5. **Wire it.** Replace `bb_icn_stub(nd)` for that kind in `walk_bb_node` with `bb_<kind>(nd)`; add forward decl in `bb_templates.h`; add the SRCS line AND the explicit `.o` rule in the Makefile.
6. **Build + gate.** `bash scripts/build_scrip.sh`, then:
   - `bash scripts/test_icon_all_rungs.sh --rung rungNN` → was red, now green.
   - `bash scripts/util_crosscheck_3mode.sh <file.icn>` → ir == sm == jit.
   - `SCRIP_NO_AST_WALK=1 bash scripts/test_icon_all_rungs.sh --rung rungNN` → still green (HONEST).
   - Full `test_icon_all_rungs.sh` + `test_smoke_icon.sh` + `test_smoke_unified_broker.sh` → no regression.
7. **Commit one rung.** `git add -A && git commit -m "ICN-BB rungNN <construct>: <BB kinds> templates + SM_BB_* hook (honest N→M)"`. Update watermark. Next red rung.

A rung is **honestly complete** iff: (a) output matches `--interp`; (b) passes under `SCRIP_NO_AST_WALK=1`; (c) the construct's `[NO-AST]` tripwire never fires; (d) all smokes unchanged; (e) ≥1 program flipped honest.

---

## Done when

1. Every construct reachable from a `--interp` PASS Icon program lowers to non-stub BB templates driven by a wired SM root hook — no `bb_icn_stub` fallthrough and no `[NO-AST] SM_BB_*` for a PASS program.
2. `SCRIP_NO_AST_WALK=1 ./scrip --interp` == `./scrip --interp` for every program in the `--interp` PASS set.
3. `test_crosscheck_icon.sh` green (ir == sm == jit) across the corpus.
4. Mode 4 (`--compile --target=x86`) assembles, links, and runs each rung's programs producing `.expected`.
5. Every `SM_BB_*` opcode emitted by Icon lowering has an `emit_sm.c` x86 case AND interp/jit handlers.
6. ZERO `DESCR_t foo(void *zeta, int entry)` added (only `icn_bb_dcg` exempt).

---

## File ownership

| Path | Role in a rung |
|------|----------------|
| `src/emitter/BB_templates/bb_icn_*.cpp` | BB templates you FILL (one file per kind) |
| `src/emitter/BB_templates/bb_templates.h` | Forward decls — add yours |
| `src/emitter/emit_core.c` (`walk_bb_node`) | Route `BB_ICN_*` → your template |
| `src/emitter/emit_sm.c` | x86 dispatch for `SM_BB_EVAL`/`PUMP_EVERY`/`PUMP_CASE` (mode 4) |
| `src/emitter/SM_templates/sm_bb_calls.cpp` | SM root hook templates (exemplar + extend) |
| `src/runtime/x86/lower.c` | Emits the SM root hook for the construct |
| `src/runtime/x86/sm_interp.c` / `sm_jit_interp.c` | Mode 2/3 dispatch of the SM root hook |
| `src/runtime/rt/rt.c` / `rt.h` | Plain runtime helpers the emitted asm CALLs (NOT four-port boxes) |
| `Makefile` | SRCS line + explicit `.o` rule per new template |
| `baselines/icon-bb/` | Honest-mode md5 baselines |

---

## Invariants

1. `--interp` (mode 2) reference output is byte-identical across a rung — you add capability, never change semantics.
2. No `EXPR_t*`/`tree_t*` in SM bytecode — BB hooks take integer/string registry operands.
3. Each new generative kind adds its OWN lowering + template — no shared catch-all.
4. `is_suspendable` stays in sync with which kinds have generator templates.
5. Every medium arm (`MACRO_DEF`/`BINARY`/`TEXT`) present in every template, even if empty.

---

## Closed rungs (historical SM-lowering work — pre-template-ladder)

These landed SM-side lowering before the template system was the law; they are the substrate
the template rungs build on. (honest dial reached 277/0/0 at the PJ-9d cross-audit.)

| Rung | Commit | Honest gain | Notes |
|------|--------|-------------|-------|
| CH-17g-smcall-proc | `60656fce` | 126→130 | `SM_CALL_FN` scans `proc_table` |
| CH-17g-augop-inline | `bb6d4ee7` | 130→140 | `AST_AUGOP` inline read-compute-writeback |
| CH-17g-scan | `d8760856` | 143→152 | `AST_CSET`→string; `AST_SCAN`→`ICN_SCAN_PUSH/POP` |
| CH-17g-builtin-batch | `c95eb2bd` | 141→167 | SIZE/NONNULL/NULL/FIELD/MAKELIST/RECORD_MAKE |
| CH-17g-case-swap-null | `7adfdc20` | 167→174 | `AST_CASE`/`AST_SWAP`/`AST_NULL` |
| rung13 conjunction-in-gen | `fa8bd48f` | 208→211 | SM_GEN_TICK + IcnFrame.every_gen[] |
| rung14 limit-in-gen | `554aa38f` | 212→213 | lower_limit_every nested SM_GEN_TICK |
| ICN-T-1 | `43b873a1` | — | `BB_ICN_TO` template FILE created (still stub body) |

---

## Watermark

```
one4all: 6f4996f7      corpus: 1fe096c       (handoff verified 2026-05-25)
smoke_icon: 5/5 ✅      crosscheck_icon (3-mode): 4/0 ✅
GATE-PK: 513/0/602  NEW=0 GONE=0 ✅  (+9 PASS from bb_upto/bb_iterate/bb_to_by/bb_binop_gen fills)
unified_broker Icon rows: SHARED_VAL read still empty (SM_BB_EVAL path) — expected, in progress
FILLED this session (ICN-T-*): bb_upto.cpp, bb_iterate.cpp, bb_to_by.cpp, bb_binop_gen.cpp
  — real inline x86 MEDIUM_BINARY bytes (Invariant 0/8), with rt_*/icon_box_rt callees
STILL STUB: bb_proc_gen, bb_gen_alt, bb_limit, bb_gen_scan, bb_keyword (ICN-T-4/6/7/9/10)
Renames since last doc: BB_ICN_*→BB_* (collisions → BB_GEN_ALT/BB_GEN_BINOP/BB_GEN_SCAN);
  BB_ICN_TO_BY+BB_ICN_LIMIT merged into BB_TO_BY+BB_LIMIT; ir_exec.c→bb_exec.c;
  lbl_back/succ/fail→lbl_β/γ/ω (PJ-13)
Current rung: <rungNN — construct — which BB kinds + SM hook>
SM root hooks: SM_BB_EVAL/PUMP_EVERY/PUMP_CASE — verify wiring state in emit_sm.c before next rung
```
