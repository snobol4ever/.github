# REPO-harness.md — harness

**What:** Test infrastructure. Double-trace monitor, cross-engine oracle harness,
benchmark pipeline. Shared across all repos.
**Clone:** `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/harness.git /home/claude/harness`
**Path:** `/home/claude/harness`

---

## Key adapters

```
harness/adapters/dotnet/run_crosscheck_dotnet.sh   — snobol4dotnet crosscheck
harness/adapters/one4all/                          — one4all frontend × backend adapters
```

## snobol4dotnet crosscheck

```bash
DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
DOTNET_ROOT=/usr/local/dotnet10 \
bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
```

## Monitor

The sync-step monitor lives in `one4all/test/monitor/`. The harness provides
adapters for running cross-engine comparisons.
