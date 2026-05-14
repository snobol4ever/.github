# GOAL-NET-OPTIMIZE — snobol4dotnet Performance Optimization

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
**Done when:** full corpus runs via emitted IL, 142/142

## What this is

Three-phase optimization of the snobol4dotnet execution engine:
1. Cache compiled pattern graphs (avoid rebuild on repeat execution)
2. Emit hot paths as IL delegates via `BuilderEmitMsil.cs`
3. Full AOT IL emission for entire corpus

## Status

Never started. All three phases are future work.

## Steps

- [ ] **S-1** — `ExecutionCache.cs`: cache compiled pattern graphs. Avoid rebuilding the same pattern graph on repeated execution of the same statement. Gate: ≥ 2× throughput on loop-heavy corpus benchmarks.

- [ ] **S-2** — `BuilderEmitMsil.cs`: emit hot execution paths as `DynamicMethod` IL delegates. Selected corpus tests pass via emitted IL path. Gate: at least the arithmetic and string-heavy corpus tests run via emitted IL.

- [ ] **S-3** — Full AOT IL emission: entire corpus runs via emitted IL delegates. Gate: 142/142 corpus via emitted IL. ✅

## Benchmark baseline (pre-optimization)

Run before S-1 to establish baseline:
```bash
export PATH=/usr/local/dotnet10:$PATH
cd /home/claude/snobol4dotnet
dotnet run --project Benchmarks/Benchmarks.csproj -c Release
```

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`. This bit us in bc19645 (200+ Windows test failures). Every string built with newlines must use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.
