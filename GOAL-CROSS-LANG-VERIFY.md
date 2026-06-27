# GOAL-CROSS-LANG-VERIFY — Verify SNOBOL4, Prolog, and Icon interoperate seamlessly

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** A single `.sc` (Snocone/SCRIP) program calls SNOBOL4 patterns,
Prolog predicates, and Icon generators directly — no marshalling, no glue — and
the test suite passes, verifying one shared IR, one shared Byrd box execution model.

---

## Why This Goal Exists

All three languages share the Byrd Box (α/β/γ/ω) execution model. This is not
coincidence — it is the architectural foundation of the entire SCRIP platform:

- SNOBOL4: pattern match phases 1–5, phase 3 is a Byrd box graph
- Prolog: E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT are Byrd box four-port nodes
- Icon: generators (E_EVERY/E_TO/E_ITERATE) are Byrd box producers

All frontends compile to the same IR (EXPR_t/STMT_t). All nodes go through
`interp_eval()`. There is ONE interpreter. Cross-language calls are direct
IR node invocations — no type conversion, no calling convention translation,
no glue layer required.

**We have already demonstrated this in SCRIP (.sc) programs.** The beauty-sc
tests (`test/beauty-sc/`) call Snocone procedures from SNOBOL4-style drivers.
This goal verifies and formalises the full three-way interoperation.

**Evidence from archive:**
- `GENERAL-SCRIP-VISION.md` §3: "No glue language. No marshaling layer. Direct
  procedure calls across paradigm boundaries."
- `GENERAL-SCRIP-VISION.md` §4: "The Byrd Box model makes this theoretically
  clean: every node in any language is an α/β/γ/ω structure. There is no semantic
  barrier to mixing SNOBOL4 concatenation with Icon generators inside a Prolog
  clause body."
- `test/beauty-sc/` — existing working cross-language test suite (Snocone↔SNOBOL4)

---

## Current State

Existing cross-language evidence:
- `test/beauty-sc/` — 14 subsystems, Snocone (.sc) calling SNOBOL4 runtime ✅
- Icon IR wired into `interp_eval()` via `icn_call_proc` ✅
- Prolog IR in `pl_unified_exec_goal` (NOT yet in `interp_eval`) ❌

Prolog is the gap. Phase 1C (GOAL-PROLOG-IR-RUN) closes it by wiring Prolog
E_CHOICE/E_CLAUSE into `interp_eval()`. Once that is done, this goal's test
suite can be written and run.

---

## Steps

- [ ] **S-1** — Prerequisite: GOAL-PROLOG-IR-RUN Phase 1C complete.
  Prolog E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT handled in `interp_eval()`.
  Icon already done. SNOBOL4 already done.
  Gate: `./scrip --run hello.pl` and `./scrip --run hello.icn` both pass
  through the same `interp_eval()` switch.

- [ ] **S-2** — Write `test/cross-lang/snobol4_calls_prolog.sc`:
  A Snocone driver that calls a Prolog predicate (member/2 or similar) directly.
  The Prolog predicate is defined in the same program (shared IR, same pred table).
  Gate: `./scrip --run test/cross-lang/snobol4_calls_prolog.sc` produces
  correct output, verified against swipl oracle.

- [ ] **S-3** — Write `test/cross-lang/prolog_calls_icon.pl`:
  A Prolog program whose clause body calls an Icon generator to produce a list
  of values, collected via findall/3. Icon generator defined as a shared IR proc.
  Gate: output matches swipl+icont oracle.

- [ ] **S-4** — Write `test/cross-lang/icon_calls_snobol4.icn`:
  An Icon program that calls a SNOBOL4 pattern match procedure on each element
  of a generator. SNOBOL4 pattern defined as shared IR node, called from Icon body.
  Gate: output matches icont oracle.

- [ ] **S-5** — Write `test/cross-lang/three_way.sc`:
  One program using all three: Snocone tokenizer → Prolog classifier → Icon
  generator for output. No glue. Direct IR calls across all three paradigms.
  Gate: produces correct output end-to-end.

- [ ] **S-6** — Add `test/frontend/cross-lang/run_cross_lang.sh` runner.
  Runs all four tests, diffs against .expected files.
  Gate: script runs clean, 4/4 PASS.

- [ ] **S-7** — Update PLAN.md ☑ done.

---

## Key files
| File | Role |
|------|------|
| `src/driver/scrip.c` | `interp_eval()` — the ONE interpreter |
| `src/ir/ir.h` | Shared IR node kinds for all three languages |
| `test/beauty-sc/` | Existing Snocone↔SNOBOL4 cross-language evidence |
| `test/cross-lang/` | New three-way test suite (created in this goal) |

---

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- S-1 must be complete before S-2 through S-5 can be written.
- Oracle: swipl for Prolog output, icont for Icon output, SPITBOL for SNOBOL4.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```
