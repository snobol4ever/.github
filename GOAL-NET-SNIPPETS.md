# GOAL-NET-SNIPPETS — snobol4dotnet Snippet Test Factory

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

**Repo:** snobol4dotnet
**Done when:** 80/80 crosscheck clean, all coverage gaps filled in TestSnobol4/

## Baseline

- Crosscheck: 79/80 (1 fail: @N cursor capture — strings/cross)
- Unit tests: 2375p/0f/2s

## Crosscheck command

```bash
DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
DOTNET_ROOT=/usr/local/dotnet10 \
bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
```

## Steps

- [ ] **S-1** — Fix @N Phase 3/5 capture clobber: `X ? @N ANY('B')` writes cursor correctly in `AtSign.Scan` but something overwrites N after the statement. Suspects: `CheckGotoFailure.cs` or post-match cleanup in `ThreadedExecuteLoop.cs`. Gate: crosscheck 80/80.

- [ ] **S-2** — Gimpel snippet factory: systematic coverage of `corpus/programs/gimpel/` programs. Add `CorpusRef_GimpelBits.cs` test class. Gate: all Gimpel programs produce output matching SPITBOL oracle.

- [ ] **S-3** — Corpus snippet factory: fill remaining coverage gaps in `TestSnobol4/` identified by S-2 audit. Gate: ≥ 2400 passed, 0 failed.

- [ ] **S-4** — Full gate: crosscheck 80/80 + unit tests ≥ 2400p/0f. ✅

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`. This bit us in bc19645 (200+ Windows test failures). Every string built with newlines must use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.
