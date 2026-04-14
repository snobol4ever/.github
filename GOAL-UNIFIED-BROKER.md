# GOAL-UNIFIED-BROKER.md — One Byrd Box Broker for All Five Languages

**Repo:** one4all
**Done when:** All five language frontends (SNOBOL4, Icon, Prolog, Snocone, Rebus) share
a single universal Byrd box type (`univ_box_fn` returning `DESCR_t`), a single box node
type (`bb_node_t`), and a single broker entry point (`bb_broker`), with three drive modes
(SCAN, PUMP, ONCE). Cross-language calls work at the IR level. All existing test gates pass.

---

## Motivation

Three brokers exist today, evolved separately:

| Language | Broker | Value type | Box fn type | Drive mode |
|----------|--------|------------|-------------|------------|
| SNOBOL4 | `stmt_exec.c` Phase 3 | `spec_t` (16 bytes) | `bb_box_fn` = `spec_t(*)(void*,int)` | SCAN: try positions 0..Ω |
| Icon | `icon_gen.c` `icn_broker` | `DESCR_t` (16 bytes) | `icn_box_fn` = `DESCR_t(*)(void*,int)` | PUMP: call body_fn per value |
| Prolog | `pl_broker.c` `pl_exec_goal` | `spec_t` (boolean only) | `bb_box_fn` | ONCE: α only, OR-box retries |

Key facts:
- `spec_t` and `DESCR_t` are both 16 bytes — same ABI, same registers (rax:rdx).
- The four-signal model (α/β/γ/ω) is identical across all three.
- `DESCR_t` strictly subsumes `spec_t`: a substring match is `DT_S` with `.s`/`.slen`.
- Unifying to one type dissolves the language boundary: a SNOBOL4 pattern box and an
  Icon generator box are the same thing to the broker. Cross-language calls fall out
  naturally once the type barrier is gone.

Target architecture:

```
                    ┌─────────────────────────────────────┐
                    │           bb_broker()                │
                    │  mode: BB_SCAN | BB_PUMP | BB_ONCE  │
                    └──────────────┬──────────────────────┘
                                   │  univ_box_fn: DESCR_t(*)(void*, int)
                    ┌──────────────┼──────────────────────┐
                    │              │                       │
              SNOBOL4 boxes   Icon boxes            Prolog boxes
              (27 bb_* fns)   (icn_bb_* fns)        (pl_box_* fns)
```

---

## Steps

### Phase 1 — Define the universal type in bb_box.h (no code changes yet)

- [x] **U-1** — Add `univ_box_fn` typedef and `BrokerMode` enum to `bb_box.h`. DONE.

- [x] **U-2** — Add converters `descr_from_spec` / `spec_from_descr` in `bb_convert.h`. DONE.

---

### Phase 2 — Implement `bb_broker` alongside the three existing brokers

- [x] **U-3** — `bb_broker()` implemented in `src/runtime/x86/bb_broker.c`. DONE.

- [x] **U-4** — Unit test `test/test_bb_broker.c` — 22/22 PASS all three modes. DONE.

---

### Phase 3 — Convert SNOBOL4 boxes to return DESCR_t

- [x] **U-5** — All 27 C boxes return DESCR_t. new descr.h breaks circular include.
  stmt_exec.c, pl_broker.c updated. regression PASS=49/149 vs baseline 41. DONE.

- [ ] **U-6** — Update `bb_boxes.s` assembly boxes to return `DESCR_t`. PARTIAL.
  DONE: 26 ω failure returns: xor eax,eax → mov eax,99 (DT_FAIL=99). rdx already 0.
  REMAINING: 27 γ success returns still use spec_t packing (rax=σ ptr, rdx=δ int).
  Must repack to DESCR_t: rax=low qword {DT_S=1 in bits 0-31, slen=δ in bits 32-63},
  rdx=high qword {s=σ ptr}. Each box has unique stack layout — do one at a time.
  Only affects --bb-live x86 path (pre-existing failure). Interpreter unaffected.
  Gate: make scrip clean; smoke + regression non-regressing.

---

### Phase 4 — Unify icn_box_fn and Pl_GoalBox into bb_node_t

- [x] **U-7** — Retire `icn_box_fn` / `icn_gen_t` — replace with `bb_box_fn` / `bb_node_t`. DONE.
  In `icon_gen.h`: `icn_box_fn` → `bb_box_fn`; `icn_gen_t` → `bb_node_t`.
  In `icon_gen.c`: update all box constructors to return `bb_node_t`.
  `icn_broker` now calls `bb_broker(root, BB_PUMP, body_fn, arg)` internally — or is
  replaced by a thin wrapper around `bb_broker`.
  Gate: `make scrip` clean; Icon rung01-11 59/59 PASS.

- [x] **U-8** — Retire `Pl_GoalBox` — replace with `bb_node_t`. DONE.
  In `pl_broker.h`: `Pl_GoalBox` → `bb_node_t`; `.fn`/`.zeta` field names already match.
  `pl_exec_goal` now calls `bb_broker(root, BB_ONCE, NULL, NULL)` — returns 1 if ticks>0.
  Gate: `make scrip` clean; Prolog regression non-regressing.

---

### Phase 5 — Wire `bb_broker` as the single call site in all three paths

- [x] **U-9** — Replace Phase 3 in `stmt_exec.c` with `bb_broker(root, BB_SCAN, ...)`. DONE.
  The scan body_fn extracts match start/end from the `DESCR_t` val via `spec_from_descr`.
  Remove the inline scan loop from `stmt_exec.c`.
  Gate: `make scrip` clean; full regression non-regressing; crosscheck passes.

- [x] **U-10** — Replace `icn_broker` call sites in `scrip.c`/`icon_gen.c` with `bb_broker(..., BB_PUMP, ...)`.
  Remove `icn_broker` function entirely. DONE.
  Gate: make scrip clean; Icon ir-run PASS=48/59 (non-regressing). ✅

- [x] **U-11** — Replace `pl_exec_goal` call sites with `bb_broker(..., BB_ONCE, ...)`.
  Remove `pl_exec_goal` function entirely. DONE.
  Gate: make scrip clean; smoke PASS=2 FAIL=0; csnobol4-suite PASS=34 non-regressing. commit 74cef6a5.

---

### Phase 6 — One SM, one BB, three languages simultaneously

**The unifying insight:** SM and BB are already one abstraction.
`SM_EXEC_STMT` → `exec_stmt` → `bb_broker(BB_SCAN)`.
Icon `every` → `bb_broker(BB_PUMP)`.
Prolog clause → `bb_broker(BB_ONCE)`.

Three broker modes × one DESCR_t value type × one stack = one machine for all languages.
The steps below build toward that incrementally — always green, always runnable.

---

- [x] **U-12** — Add `lang` field to `STMT_t`. *(Additive. Zero behaviour change.)* DONE.
  In `scrip_cc.h`: add `LANG_SNO=0 LANG_ICN=1 LANG_PL=2` constants above STMT_t.
  STMT_t gains `int lang`. SNOBOL4 gets LANG_SNO=0 free from calloc.
  icon_driver.c: `st->lang = LANG_ICN`. prolog_lower.c: `s->lang = LANG_PL` (both sites).
  Gate: `make scrip` clean; smoke PASS=2.

- [x] **U-13** — Polyglot parser: `.scrip` fenced file → one `Program*`. DONE.
  Add `parse_scrip_polyglot(src, filename) → Program*` in `scrip.c`.
  Scans ` ```SNOBOL4 ` / ` ```Icon ` / ` ```Prolog ` fenced blocks; compiles each with
  its frontend; sets `st->lang`; appends all `STMT_t` chains in source order into one
  `Program*`. Wire `main()`: `.scrip` or `.md` extension → `parse_scrip_polyglot`.
  Execution dispatch: `lang_polyglot` → `execute_program` (SNO path for now; U-15 fixes).
  Gate: `make scrip` clean; smoke PASS=2.

- [x] **U-14** — Unified init: `polyglot_init(prog)`. DONE.
  Single walk over `prog->head` populates all three runtime tables at once:
    SNO: `label_table_build` + `prescan_defines`.
    ICN: zero icn_* state; collect E_FNC subjects (lang==LANG_ICN) → `icn_proc_table`.
    PL:  `prolog_atom_init`; `trail_init`; collect E_CHOICE/E_CLAUSE (lang==LANG_PL)
         → `g_pl_pred_table`; `g_pl_active=1` if any PL stmts present.
  All three entry points call `polyglot_init` — their individual init sequences removed.
  Gate: `make scrip` clean; smoke PASS=2.

- [x] **U-15** — `--ir-run` per-statement dispatch by `st->lang`. DONE.
  In `execute_program`'s statement loop, replaced E_CHOICE/E_CLAUSE skip guard with:
    `LANG_SNO`: existing path (subject / pattern / replacement / goto).
    `LANG_ICN`: skip inline (E_FNC defs registered by polyglot_init); call icn_call_proc(main) post-loop.
    `LANG_PL`:  call `interp_eval(st->subject)` with `g_pl_active=1`.
  Also fixed `sno_parse_string` to use `lex_open_str_initial` (INITIAL start state) so
  indented/labelled SNOBOL4 blocks parse correctly in polyglot context.
  Gate: SNO wordcount outputs 9; smoke PASS=2. one4all HEAD 5a6d8124.

- [x] **U-16** — Add `SM_BB_PUMP` and `SM_BB_ONCE` opcodes to SM. DONE. one4all HEAD 886aa7d0.
  `sm_prog.h`: SM_BB_PUMP and SM_BB_ONCE added after SM_EXEC_STMT with full comment.
  `sm_interp.c`: stub handlers (set last_ok=0); unused until U-18.
  Gate: make scrip clean; smoke PASS=2.

- [x] **U-17** — Implement `icn_eval_gen` in `scrip.c` (B-8 stub in `icon_gen.h`).
  `icn_eval_gen(EXPR_t *e) → bb_node_t`: walk Icon IR, return a drivable `bb_node_t`.
  E_TO → `{icn_bb_to, alloc icn_to_state_t}`.
  E_TO_BY → `{icn_bb_to_by, alloc icn_to_by_state_t}`.
  E_ITERATE → `{icn_bb_iterate, alloc icn_iterate_state_t}`.
  E_FNC (user proc) → `{icn_bb_suspend, coroutine wrapping icn_call_proc}`.
  Fallback: one-shot box wrapping `icn_interp_eval` result.
  Gate: `make scrip` clean; smoke PASS; Icon rung01-11 59/59; regression non-regressing.

- [x] **U-18** — Polyglot --ir-run: Icon section of wordcount.md now outputs 9/9. DONE.
  Pivoted from --sm-run to --ir-run: static linkage of interp_eval/icn_interp_eval/
  g_pl_active in scrip.c blocks extern access from sm_interp.c.
  Four fixes in icn_interp_eval (scrip.c):
    (a) E_VAR &-keyword handler: &letters/&pos/&ucase/&lcase/&digits/&null/&fail.
    (b) upto() fixed: no longer advances icn_scan_pos (tab() does the advance).
    (c) tab() fixed: propagates FAILDESCR from argument (allows while-loop exit).
    (d) E_SEQ_EXPR added: multi-statement brace blocks had no handler — now evaluates
        all children in order.
  Gate: scrip --ir-run demo/scrip/demo2/wordcount.md → 9 (SNO) + 9 (Icon).
  Prolog section silent (phrase/3, char_type/2 pre-existing gaps).
  smoke PASS=2; unified_broker PASS=12. one4all HEAD bb780157.

- [x] **U-19** — Cross-language `.scrip` test. *(Proof of concept end-to-end.)* DONE.
  `test/cross_lang.scrip`: SNO section (BB_SCAN counter loop prints `SNO: 3`), Icon section
  (`1 to 3` generator via icn_eval_gen+BB_PUMP prints `ICN: 1/2/3`), Prolog section
  (color facts via BB_ONCE fail-loop prints `PL: red/green/blue`). `.ref` generated.
  Root cause fixed: missing closing ``` fence in polyglot block caused prolog_compile to
  never run. Also fixed: post-loop Prolog main/0 dispatch in execute_program (U-19 analogue
  of U-15 Icon post-loop). Gate: unified_broker PASS=13; smoke PASS=2. --sm-run pivot: gate
  is --ir-run only per U-18 note (--sm-run polyglot blocked by static linkage).
  Also: demo/scrip/*.md → *.scrip rename (git mv all 10); scripts/test_scrip_demos.sh added.

- [x] **U-20** — Documentation. DONE.
  `ARCH-IR.md`: document polyglot `Program*`, `STMT_t.lang`, `polyglot_init`,
  `SM_BB_PUMP`/`SM_BB_ONCE` as the three broker modes in one SM.
  Update PLAN.md. Gate: none.

---

### Phase 7 — Module System (future, post U-20)

**Brainstorm captured 2026-04-13.**

The polyglot `.scrip` file already has the structure of a module system:
each fenced block is a module with a language tag. The missing pieces:

**The key architectural insight (2026-04-13):**
The module boundary IS the link unit — one-to-one with what would be
assembled and linked in the output-file path. This unifies all three
execution modes under one model:

```
.scrip file
├── ```SNOBOL4  →  one_module.sno.o   (x86 asm → as → .o)
├── ```Icon     →  one_module.icn.o   (x86 asm → as → .o)
└── ```Prolog   →  one_module.pl.o    (x86 asm → as → .o)
                     └── ld → one_module   (linked binary)

Same module boundaries for --ir-run (in-memory interp) and emit paths.
ScripModuleRegistry in-memory = the linker symbol table on disk.
```

The three interpreter modes (--ir-run, --sm-run, --bb-live) all load
all modules into the same registry simultaneously — matching what the
linker does when combining .o files. Cross-module calls work the same
way in all modes: look up the symbol in the registry, dispatch.

**Entry point rule:** whichever module defines `main` is the start point.
Single `main` across all modules — linker error if more than one (or:
explicit `-e module_name` flag to select, like ld).

---

**U-21** — Formal module concept in-memory. DONE. one4all HEAD 7fd3135d.
  `ScripModule`/`ScripModuleRegistry` added to scrip.c; `g_registry` populated
  by `polyglot_init` in same pass as flat tables. Additive — zero behaviour change.
  Gate: unified_broker PASS=13 FAIL=0.
  Each fenced block = a `ScripModule`:
  ```c
  typedef struct {
      int          lang;          /* LANG_SNO / LANG_ICN / LANG_PL */
      const char  *name;          /* optional: ```Icon "mymod" */
      Program     *prog;          /* compiled IR */
      /* symbol tables populated by polyglot_init: */
      /* SNO: label_table slice */
      /* ICN: icn_proc_table slice */
      /* PL:  pl_pred_table slice */
  } ScripModule;

  typedef struct {
      ScripModule  mods[SCRIP_MOD_MAX];
      int          nmod;
      int          main_mod;      /* index of module owning main */
  } ScripModuleRegistry;
  ```
  `polyglot_init` populates `ScripModuleRegistry` instead of three
  parallel flat tables. All existing code continues to work via the
  same flat table views — registry is additive.
  Gate: make scrip clean; smoke PASS=2; unified_broker PASS=13.

- [x] **U-22** — Cross-call hook: SNO → ICN/PL. DONE. one4all HEAD 78e2c8f0.
  `_usercall_hook` extended: if name not found in SNO label table, checks
  `icn_proc_table` (calls `icn_call_proc`) then `g_pl_pred_table` (calls
  `bb_broker(BB_ONCE)`). SNOBOL4 source can now call Icon/Prolog procs directly.
  Two bugs fixed this session: (1) `args[_i].type` → `args[_i].v` (DESCR_t field
  name); (2) stray `printf("DBG: registering ICN proc...")` removed from
  `polyglot_init` (was contaminating test output → 5 gate failures).
  Icon-first polyglot ordering also confirmed working.
  Proof: `test/test_crosscall.scrip` — SNO calls Icon `double(21)` → `CROSSCALL: 42`.
  Gate: unified_broker PASS=13 FAIL=0; smoke PASS=2 FAIL=0.

**U-23** — Shared constant space.
  SNO NV store (the global variable table) is already shared across all
  sections at the C level. Expose it: Icon `E_VAR` handler checks SNO NV
  store for names not found in `icn_env`. Prolog can read/write NV via a
  builtin. A ```SCRIP fenced block (language-agnostic) defines shared
  constants visible to all modules — equivalent to a linker common section.

**U-24** — `test/family.scrip` — first true cross-call demo.
  SNO parses family.csv, calls PL predicates to assert facts, Icon iterates
  query results. Uses U-22 cross-call hook. Recovers the family tree demo
  from archive (MISC-SCRIP-CONCEPTS.md / SCRIP_DEMO.md). demo11.
  This is the proof that the module/link-unit model works end-to-end.

---

## Key files

| File | Role |
|------|------|
| `src/runtime/x86/bb_box.h` | `univ_box_fn`, `BrokerMode`, `bb_node_t`, converters — extended |
| `src/runtime/x86/bb_broker.c` | NEW — `bb_broker()` implementation |
| `src/runtime/x86/bb_boxes.c` | 27 SNOBOL4 boxes — return type `spec_t` → `DESCR_t` |
| `src/runtime/x86/bb_boxes.s` | Assembly boxes — return layout updated |
| `src/runtime/x86/stmt_exec.c` | Phase 3 → calls `bb_broker(..., BB_SCAN, ...)` |
| `src/frontend/icon/icon_gen.h` | `icn_gen_t` → `bb_node_t`; `icn_box_fn` → `bb_box_fn` |
| `src/frontend/icon/icon_gen.c` | `icn_broker` → thin wrapper or removed |
| `src/frontend/prolog/pl_broker.h` | `Pl_GoalBox` → `bb_node_t` |
| `src/frontend/prolog/pl_broker.c` | `pl_exec_goal` → calls `bb_broker(..., BB_ONCE, ...)` |
| `test/test_bb_broker.c` | NEW — unit test for bb_broker all three modes |
| `test/test_cross_lang.c` | NEW — cross-language box composition tests |

---

## Invariants — never break these

- Every step must leave `make scrip` clean (zero errors, zero warnings).
- Smoke gate (`bash test/smoke.sh`) must pass after every step.
- Regression score must not drop after U-5 (the breaking change).
- Internal box state (`seq_t.matched`, `arbno_frame_t.matched`, etc.) may stay `spec_t` — these are private. Only return values and the broker ABI change.
- `Σ/Δ/Ω` globals are unchanged — SNOBOL4 cursor arithmetic is internal to boxes and Phase 3.
- Assembly boxes (bb_boxes.s) must be updated in the same commit as bb_boxes.c (U-6 comes immediately after U-5).

---

## Rules
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Build gate: `make scrip` clean + smoke + regression non-regressing after every step.
- One step per commit. Gate before committing.
- Follow RULES.md naming conventions: new C functions in `snake_case`, new types `Xxxx_yyy`.

---

## Current state (session 2026-04-14, one4all HEAD 78e2c8f0)

U-1 through U-22 complete. Next step: U-23 (shared constant space).

**U-22 done** (one4all HEAD 78e2c8f0):
Cross-call SNO->ICN/PL working. Two bugs fixed: .type->.v in _usercall_hook;
stray DBG printf removed from polyglot_init. Icon-first polyglot ordering
confirmed working. Proof: test/test_crosscall.scrip -> CROSSCALL: 42.
Gate: unified_broker PASS=13 FAIL=0; smoke PASS=2 FAIL=0.

U-6 gamma repack deferred (--bb-live x86 path only -- pre-existing failure).
Phase 7 (module system, U-23..U-24) next.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```
