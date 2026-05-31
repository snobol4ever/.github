# GOAL-NO-SYMLINKS — Remove symlinks from all shell scripts

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

**Repo:** corpus, harness, snobol4dotnet, SCRIP (any repo with shell scripts)
**Done when:** No shell script, Makefile, or CI file in any repo creates symlinks via `ln -s`.

## Why

Session 4 of BEAUTY-19 revealed that corpus commit `fbab26b` used `ln -s` to resolve
a deduplication — creating symlinks from `beauty/` into `demo/inc/` which was then deleted.
The result: 18 broken symlinks that silently killed the entire beauty suite (0/18).
Symlinks break when targets move or are deleted. Real files do not.

## Rule

See RULES.md: "No symlinks in shell scripts."

## Steps

- [ ] **S-1** — Audit all shell scripts in corpus for `ln -s` usage. Replace with `cp` or
      direct path references. Gate: `grep -r "ln -s" corpus/` returns nothing.

- [ ] **S-2** — Audit all shell scripts in harness for `ln -s` usage. Replace with `cp` or
      direct path references. Gate: `grep -r "ln -s" harness/` returns nothing.

- [ ] **S-3** — Audit all shell scripts in snobol4dotnet for `ln -s` usage.
      Gate: `grep -r "ln -s" snobol4dotnet/` returns nothing.

- [ ] **S-4** — Audit SCRIP and any other active repos.
      Gate: clean grep across all repos.

- [ ] **S-5** — Verify no symlinks exist anywhere in corpus source tree.
      Gate: `find corpus/ -type l` returns nothing (or only intentional non-source symlinks,
      documented here explicitly).
