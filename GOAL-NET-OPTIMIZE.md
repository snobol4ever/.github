# GOAL-NET-OPTIMIZE — snobol4dotnet Performance Optimization

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
- See RULES.md for full rules including handoff checklist.
