# GOAL-SNOCONE-DEMOS — treebank and claws5 in SNOBOL4 and Snocone

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
**Done when:** all four programs pass oracle diff under --run, --run, --run.

---

## Design Principle

Both programs derive from Python originals using SNOBOL4python pattern combinators.
The correct structure is ONE pattern per program: `POS(0) ... RPOS(0)` with
side-effect procedures called via `*proc()` inline, ARBNO for iteration.
No imperative loops replacing pattern structure.

Python → SNOBOL4/Snocone mapping:
  λ("stmt")        →  *do_func()       (procedure, NRETURN, zero-length side-effect)
  ζ(lambda: group) →  *group           (deferred global pattern variable reference)
  P % "var"        →  P . var          (immediate capture into global)
  ARBNO(P)         →  ARBNO(*P)        (zero-or-more)

Side-effect procedures read captured globals directly (no args) — same as claws5.sno.
-INCLUDE stack.sno and counter.sno (the .sno files, not .sc).
For .sc versions: pass include-sc/ files on command line.

CRITICAL BUG TO FIX: In treebank.sno, `group` references `*group` recursively
inside its own definition. At the time that line executes, `group` is still
uninitialized, so `*group` captures empty string at build time.
Fix: define a stub first, or use unevaluated expression form.
See how beauty.sno handles recursive pattern references.

---

## Programs

### SD-1: treebank.sno (rewrite) — IN PROGRESS, BROKEN
- One pattern POS(0)...RPOS(0), group as global pattern var, side-effects read globals.
- BUG: *group self-reference does not defer correctly.
- Must use -INCLUDE 'stack.sno' and -INCLUDE 'counter.sno' (not inline).
- Input:  corpus/programs/snobol4/demo/treebank.input
- Ref:    corpus/programs/snobol4/demo/treebank.ref
- Output: test/demo/treebank.sno

### SD-2: treebank.sc — NOT STARTED
- Snocone port of SD-1. Pass include-sc/stack.sc, include-sc/counter.sc on cmdline.
- Output: test/demo/treebank.sc

### SD-3: claws5.sno — verify passes oracle
- Current claws5.sno correct structure. Verify, fix if needed.
- Input:  corpus/programs/snobol4/demo/CLAWS5inTASA.dat
- Ref:    corpus/programs/snobol4/demo/claws5.ref

### SD-4: claws5.sc — NOT STARTED
- Snocone port. Pass include-sc files on cmdline.
- Output: test/demo/claws5.sc

---

## Steps

- [ ] **SD-1** — Fix treebank.sno: -INCLUDE stack.sno/counter.sno, fix *group recursion.
  Gate: scrip --run treebank.sno < treebank.input matches treebank.ref.

- [ ] **SD-2** — Write treebank.sc.
  Gate: scrip --run stack.sc counter.sc treebank.sc < treebank.input matches ref.

- [ ] **SD-3** — Verify claws5.sno passes oracle.

- [ ] **SD-4** — Write claws5.sc.

- [ ] **SD-5** — Test scripts, update PLAN.md. Commit. Push.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

## Invariants

- Gate = PASS=48 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- SPITBOL oracle: /home/claude/x64/bin/sbl (run from corpus/programs/snobol4/beauty_suite/ so -INCLUDEs resolve)
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
