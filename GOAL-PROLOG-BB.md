# GOAL-PROLOG-BB.md — Prolog Byrd-Box templates, hello-world → algorithms, one rung at a time

**Repo:** one4all + corpus + .github
**Sister docs:** `GOAL-HEADQUARTERS.md` (the template system), `GOAL-ICON-BB.md` (mirror), `GOAL-BB-TEMPLATE-LADDER.md`, `GOAL-LANG-PROLOG.md`
**Prereq:** PJ-1..PJ-9d ✅ (registry + Mode-4 simple-body recursion working). **Rewritten as a template-construction ladder:** 2026-05-25

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ READ FIRST — THE ONLY LEGAL WAY TO MAKE A BYRD BOX EXIST                                     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A Byrd box is x86 ASSEMBLY TEXT returned by a C++ template function. It is NOT a C function.    ║
║                                                                                                  ║
║  FORBIDDEN — instant rejection (RULES.md, HQ Invariant #2 + #16):                               ║
║    DESCR_t foo(void *zeta, int entry) { ...α/β/γ/ω logic... }   ← NEVER write this              ║
║    Any new function that emits code without carrying a BB / SM / XA opcode.                     ║
║    NOTE: the `pl_bb_dcg` C-function sketch from old versions of this file is NOT the work        ║
║    pattern — `pl_bb_dcg` is the ONE exempt infrastructure shim (twin of `icn_bb_dcg`). Do not   ║
║    write any OTHER four-port C function. Predicate bodies are IR_block_t graphs + BB templates.  ║
║                                                                                                  ║
║  REQUIRED — every Byrd box is born exactly these six steps:                                     ║
║    1. A `BB_PL_<KIND>` enum value (already in the IR — see ir.h).                                ║
║    2. A template file `src/emitter/BB_templates/bb_pl_<kind>.cpp` whose body is a pure           ║
║       `std::string bb_pl_<kind>_str(BB_t * pBB, bb_bin_t & bin)` returning                       ║
║         IF(MEDIUM_MACRO_DEF, …) + IF(MEDIUM_BINARY, …) + IF(MEDIUM_TEXT, …);                     ║
║       guarded by `if (PLATFORM_X86)`. JVM/JS/NET/WASM arms `return std::string();`.             ║
║    3. A case in `walk_bb_node` (src/emitter/emit_core.c) routing the kind → `bb_pl_<kind>(nd)`. ║
║    4. A forward decl in `BB_templates/bb_templates.h`.                                           ║
║    5. TWO Makefile edits: add to the BB_SRCS list AND add an explicit `.o` rule.                ║
║    6. The SM root hook `SM_BB_ONCE_PROC` already drives all Prolog BBs (see §"The SM→BB hook"). ║
║                                                                                                  ║
║  Good news: steps 1–6 are ALREADY DONE for six Prolog kinds. You COPY them. See "Current        ║
║  reality" — bb_pl_atom/arith/unify/builtin/seq/var are real, fleshed-out templates.            ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 (RULES.md). Mode 1 is the DELETED reference. `--interp`=mode 2.║
║  No `tree_t*` deref in sm_interp.c, sm_jit_interp.c, or src/emitter/*. `[NO-AST] <opcode>` =     ║
║  honest tripwire. PJ-8 already stubbed the `_usercall_hook` Prolog AST branch under SM dispatch. ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

## Port semantics (Prolog differs from Icon — never cross the wires)

| Port | Icon | Prolog |
|---|---|---|
| α | enter generator, first attempt | enter predicate, first clause, `trail_mark` |
| β | resume, advance generator | retry: `trail_unwind`, advance to next clause |
| γ | success (yield value) | success (head unified/bound) |
| ω | failure (exhausted) | failure (no more clauses) |

`proc_table` (Icon) ↔ `dcg_table`/predicate registry (Prolog); `icn_bb_dcg` ↔ `pl_bb_dcg`; `SM_BB_PUMP_PROC` ↔ `SM_BB_ONCE_PROC`. Never invoke language-A's SM-bridge handler with language-B's BB object.

---

## Current reality (verified 2026-05-25 — READ before starting)

**Prolog templates ALREADY EXIST and are real — this is your copy-me set:**

- `BB_templates/bb_pl_atom.cpp` (44 LOC) — atom literal, full MACRO_DEF+BINARY+TEXT, `rt_pl_atom_push@PLT`.
- `BB_templates/bb_pl_arith.cpp` (72) — `Y is X+N`.
- `BB_templates/bb_pl_unify.cpp` (111) — `X = Y`.
- `BB_templates/bb_pl_builtin.cpp` (103) — write/nl/halt/etc.
- `BB_templates/bb_pl_seq.cpp` (47) — conjunction `A,B,C`.
- `BB_templates/bb_pl_var.cpp` (34) — variable slot read.
- `BB_templates/bb_pl.cpp` (19) — CALL/CHOICE/CUT/ALT entry.

All are wired in `walk_bb_node` (most via `bb_prepare_pl(nd)` first, which interns operand labels into distinct `g_emit` fields — see HQ LOCAL-PURGE-6), declared in `bb_templates.h`, and in the Makefile (SRCS + `.o` rule). The SM root hook `SM_BB_ONCE_PROC` is wired in mode 2 (`sm_interp.c`), mode 3 (`sm_jit_interp.c`, PJ-9a), and mode 4 (`emit_sm.c` → `rt_bb_once_proc`, PJ-9c). The Mode-4 predicate REGISTRY emit exists (PJ-9d: `rt_register_predicates_pl` + `xa_pl_*` builder templates).

**What is NOT done (the remaining ladder):**
- **Mode-4 multi-clause bodies** (PJ-9e, OPEN): per-clause sub-cfg bodies stored in `IR_SUCCEED.opaque` are not all emitted into the standalone binary's builder. Factorial recursion prints in modes 1/2/3 but NOT mode 4. Sub-builder mechanism landed (`a02efe54`); three open items below.
- **Higher rungs** (lists, findall/bagof/setof, cut-heavy, term inspection, arithmetic edges, ISO errors) — corpus rung16..rung39 exist but BB coverage thins out past the basics.

**Exemplars beyond Prolog (for richer port shapes):** `bb_pat_span.cpp` (Icon/SNOBOL generator with α/β + back-label + FOR(0,2,…) over ports) when a Prolog construct needs a multi-port generator beyond simple once/retry.

---

## The SM→BB hook (how a Prolog goal reaches a template)

```
.pl → pl_parse() → AST_t*
   lower.c + lower_pl.c   build per-predicate IR_block_t graphs, register them, and for each
             top-level goal (`:- initialization(G).`) emit  SM_BB_ONCE_PROC name/arity.
   ── mode 2 (--interp)   sm_interp.c case SM_BB_ONCE_PROC → pl_bb_once_proc_by_name + bb_broker
   ── mode 3 (--run)      sm_jit_interp.c h_bb_once_proc → same (PJ-9a)
   ── mode 4 (--compile)  emit_sm.c → emits BB_ONCE_PROC; rt.c rt_bb_once_proc drives it;
             rt_register_predicates_pl rebuilds the IR_block_t graphs at binary startup
             (xa_pl_builder / xa_pl_sub_builder / xa_pl_registry_table / xa_pl_kids_rodata).
   bb_broker walks each IR_block_t node → walk_bb_node(nd) → bb_pl_<kind>(nd) → template asm.
```

BB executor cases (in `src/lower/bb_exec.c` — renamed from `ir_exec.c` at PJ-8837b2b1) the BBs lean on: `BB_UNIFY`, `BB_CALL`, `BB_CHOICE`/`BB_ALT`, `BB_SEQ`, `BB_CUT`, `BB_BUILTIN`, `BB_ARITH`, `BB_VAR`, `BB_ATOM`. (The `IR_PL_*`/`IR_LANG_*` prefixes were dropped tree-wide at PJ-10/PJ-T-7; `IR_block_t` graphs are now `BB_graph_t`.)

⛔ **Cheating tripwire.** `SCRIP_NO_AST_WALK=1` must not change `--interp` output. PJ-8 closed the `_usercall_hook` AST back-door; keep it closed.

---

## Session Setup

```bash
cd /home/claude/one4all
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
bash scripts/build_scrip.sh                 # builds scrip + out/libscrip_rt.so
make libscrip_rt                            # if Mode-4 runner reports it missing
```

Optional oracles: `bash scripts/install_swi_prolog_tests.sh` / `install_gnu_prolog_tests.sh`.

### Baseline gates — capture BEFORE touching anything; must not regress

```bash
bash scripts/test_smoke_prolog.sh            # 5/5 (write_atom, unify, arith, clause, recursion)
bash scripts/test_crosscheck_prolog.sh       # mode-consistency across ir/sm/jit (128/0 at PJ-9d)
bash scripts/test_prolog_bb_honest.sh        # honest dial 124/0/0
bash scripts/test_smoke_unified_broker.sh    # broker, Prolog rows non-regressive (20/49 at PJ-9d)
```

For Mode-4 end-to-end on one file:
```bash
bash scripts/run_prolog_via_x86_backend.sh /home/claude/corpus/programs/prolog/rung01_hello_hello.pl
```

---

## The corpus ladder (already on disk — `/home/claude/corpus/programs/prolog/`)

`rungNN_*.pl` with `.expected`. rung01..rung39 present. Climb hello-world → algorithms, making the BB/template machinery PASS each rung honestly across modes.

```bash
bash scripts/test_prolog_rung12.sh                              # a specific rung script
bash scripts/util_crosscheck_3mode.sh <file.pl> [oracle.ref]    # one file, all 3 modes
```

Run `ls /home/claude/corpus/programs/prolog/rungNN_*` for exact files.

| Rung | Theme | BB kinds / executor cases |
|------|-------|---------------------------|
| 01 | hello | `write/1`, `nl/0`, `halt/0` — `BB_PL_BUILTIN`, `SM_BB_ONCE_PROC` ✅ |
| 02 | facts + backtracking | fact lookup, `fail`/`;`, `BB_PL_CHOICE`/`ALT` ✅ |
| 03 | unification | head unify, compound terms — `BB_PL_UNIFY` ✅ |
| 04–05 | arithmetic | `is/2`, comparison — `BB_PL_ARITH` ✅ |
| 06–08 | recursion | recursive predicates, accumulator pattern (Mode-4 OPEN past simple bodies) |
| 09–11 | lists | `[H|T]`, member, append — list term BBs |
| 12–15 | cut + control | `!`, `->`/`;`, `\+` negation — `BB_PL_CUT` + barrier |
| 16–20 | term inspection | `functor/3`, `arg/3`, `=..`, `copy_term` |
| 21–25 | findall family | `findall/3`, `bagof/3`, `setof/3` |
| 26–30 | strings/atoms | `atom_codes`, `atom_length`, `sub_atom` |
| 31–35 | bridges | catch/throw, negation, `call/N`, setof bridge |
| 36–39 | ISO edges + algorithms | arith edge cases, term ops, ISO errors, atom ISO; queens/roman/palindrome-scale |

---

## Rung procedure — DO THIS for every rung (do not skip, do not batch)

1. **Pick the lowest red rung** across modes. Run its rung script (or `test_prolog_bb_honest.sh`) and the Mode-4 runner on its files. Read each failing `.pl` and `.expected`.
2. **Identify goal → IR cases → BB kinds.** Dump the SM/IR. Confirm `SM_BB_ONCE_PROC` is emitted for the entry goal. Note which `BB_PL_*` kinds the clause bodies lower to and whether each has a non-stub template.
3. **Extend lowering if needed.** `src/lower/lower_pl.c` turns a clause into the `BB_graph_t` graph; `src/lower/bb_exec.c` executes each `BB_*` node. Add/extend the executor case AND the lowering for any new construct. (Backtracking/resume lives here — `BB_CHOICE.state`, `BB_CALL` resumability, `BB_SEQ` leftward rescan — see PJ-7. Resume entry is `bb_exec_resume`.)
4. **Fill/extend the BB template.** For each `BB_PL_*` kind that is stubbed or missing:
   - Copy the closest live one (`bb_pl_arith.cpp` for compute, `bb_pl_unify.cpp` for unify, `bb_pl_builtin.cpp` for a runtime call, `bb_pl_atom.cpp` for a leaf).
   - `bb_pl_<kind>_str(BB_t*, bb_bin_t&)` returning `IF(MEDIUM_MACRO_DEF,…)+IF(MEDIUM_BINARY,…)+IF(MEDIUM_TEXT,…)`, x86-only, EVERY medium slot present even if empty.
   - If operand labels are needed, lift them in `bb_prepare_pl` (emit_bb.c) into distinct `g_emit` fields and read them in the body — DO NOT call `emit_intern_str` inside the body (it returns a SHARED static buffer; aliasing bug — see HQ LOCAL-PURGE-6).
   - Runtime help = a PLAIN `rt_pl_<thing>` callee in `rt.c`, never a four-port C box.
5. **Wire it.** `walk_bb_node` case → `bb_prepare_pl(nd); bb_pl_<kind>(nd);`; forward decl in `bb_templates.h`; Makefile SRCS line + `.o` rule.
6. **Build + gate.** `bash scripts/build_scrip.sh && make libscrip_rt`, then:
   - rung script → green; `util_crosscheck_3mode.sh <file.pl>` → ir == sm == jit.
   - `run_prolog_via_x86_backend.sh <file.pl>` → matches `.expected` (Mode-4 honest).
   - `test_smoke_prolog.sh` 5/5, `test_prolog_bb_honest.sh` non-regressive, `test_crosscheck_prolog.sh` non-regressive, `test_smoke_unified_broker.sh` Prolog rows non-regressive.
7. **Commit one rung.** `git add -A && git commit -m "PL-BB rungNN <construct>: bb_pl_<kind> + bb_exec case (mode-4 N/M)"`. Update watermark. Next red rung.

---

## Mode-4 items (PJ-9e — status as of handoff 2026-05-25)

1. ~~**`sm_bb_calls.c`: `IS_MACRO_DEF` ordering**~~ — **RESOLVED (PJ-10/f9cda41a).** `IS_MACRO_DEF` moved before `IS_X86`; it is a sub-mode of X86, not separate.
2. ~~**`xa_macro_library` DOUBLE-DEFINITION**~~ — **RESOLVED via Option B (PJ-10 + PJ-T-7).** The session took inline-only: dropped the `.include "sm_macros.s"` / `.include "bb_macros.s"` lines and now emits `.intel_syntax` + the macro library directly, so each `.s` is self-contained. (This was the cause of the 280-SKIP `test_mode4_broad_corpus_snobol4` run earlier — re-run that suite to confirm it now lights up.)
3. **Multi-clause sub-cfg emit (STILL OPEN)** — per-clause `BB_graph_t*` bodies live in the wrapper `BB_SUCCEED` node's `opaque` (consumed by `bb_exec.c`), separate allocations NOT in `cfg->all[]`. The builder must recurse into each sub-cfg. Sub-builder helpers landed (`rt_pl_b_sub_*`, `emit_pl_sub_builder_fn`); the Mode-4 factorial **segfault was fixed at PJ-9e/1a65b62b** (`trail_init` moved into `rt_init`; Icon BB templates added to `RT_PIC_SRCS`). Re-verify factorial prints `120` end-to-end after any builder change.

---

## Done when

`SM_BB_ONCE_PROC` routes through the predicate registry + BB templates ✅. PJ-8 AST back-door stays closed ✅. The three Mode-4 items above closed (factorial=120 in mode 4). Each corpus rung PASSes honestly across modes 2/3/4. ZERO `DESCR_t foo(void*,int)` added beyond the exempt `pl_bb_dcg` shim.

---

## File ownership

| Path | Role in a rung |
|------|----------------|
| `src/emitter/BB_templates/bb_pl_*.cpp` | BB templates (copy/extend; one file per kind) |
| `src/emitter/BB_templates/bb_templates.h` | Forward decls |
| `src/emitter/emit_core.c` (`walk_bb_node`) | Route `BB_PL_*` → template (via `bb_prepare_pl`) |
| `src/emitter/emit_bb.c` (`bb_prepare_pl`) | Lift operand labels into `g_emit` fields |
| `src/emitter/emit_sm.c` | `SM_BB_ONCE_PROC` mode-4 dispatch + predicate registry emit |
| `src/emitter/XA_templates/xa_pl_*.cpp` | Mode-4 predicate-registry builder templates |
| `src/lower/lower_pl.c` | Clause → BB_graph_t graph |
| `src/lower/bb_exec.c` | `BB_*` executor cases (backtracking lives here; renamed from `ir_exec.c`) |
| `src/runtime/x86/sm_interp.c` / `sm_jit_interp.c` | Mode 2/3 `SM_BB_ONCE_PROC` |
| `src/runtime/rt/rt.c` / `rt.h` | `rt_pl_*` callees + registry helpers (NOT four-port boxes) |
| `Makefile` | SRCS line + explicit `.o` rule per new template |

---

## Closed steps (PJ ladder — substrate for the rung work)

| Step | Commit | Result |
|---|---|---|
| PJ-1 | `e6af028c` | `pl_bb_dcg` shim + registry skeleton |
| PJ-4 | `cb1417a5` | write/unify/arith executors — smoke 3/5 |
| PJ-5a | — | entry-point fix + IR_PL_SEQ + cut barrier — smoke 4/5 |
| PJ-7 | — | backtracking pump (CHOICE/CALL/SEQ resumable) — smoke 5/5 |
| PJ-8 | — | `_usercall_hook` AST branch `[NO-AST]`-stubbed under SM dispatch |
| PJ-9a | — | Mode-3 JIT `h_bb_once_proc` wired — crosscheck 4/4 |
| PJ-9b | — | stub fingerprints aligned to opcode names — crosscheck 128/0 |
| PJ-9c | — | Mode-4 `SM_BB_ONCE_PROC` dispatch → `rt_bb_once_proc` |
| PJ-9d | — | Mode-4 predicate registry emit; simple bodies + cross-pred calls run |
| PJ-9e | `a02efe54` | sub-builder mechanism (partial — 3 open items above) |

---

## Watermark

```
one4all: 6f4996f7      corpus: 1fe096c       (handoff verified 2026-05-25)
smoke_prolog: 5/5 ✅      crosscheck_prolog: 128/0 (4 skip, 11 oracle-miss) ✅      honest_prolog: non-regressive
GATE-PK: 513/0/602  NEW=0 GONE=0 ✅      unified_broker: 23/49 (was 20)
Renames since last doc: ir_exec.c→bb_exec.c; IR_PL_*/IR_LANG_*→BB_*/BB_LANG_*; IR_block_t→BB_graph_t;
  lbl_back/succ/fail→lbl_β/γ/ω (PJ-13, 505 files, GATE-PK byte-identical through it)
Mode-4: items 1 (IS_MACRO_DEF order) + 2 (macro double-def, Option B) RESOLVED; factorial segfault fixed (1a65b62b)
Current rung: <rungNN — construct — which BB_* kinds + bb_exec cases>
STILL OPEN: item 3 multi-clause sub-cfg emit (verify factorial=120 mode-4 end-to-end);
  re-run test_mode4_broad_corpus_snobol4 to confirm Option-B fix cleared the 280-SKIP
```
