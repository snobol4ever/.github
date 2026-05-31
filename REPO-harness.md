# REPO-harness.md — harness

**What:** Test infrastructure. Double-trace monitor, cross-engine oracle harness,
benchmark pipeline. Shared across all repos.
**Clone:** `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/harness.git /home/claude/harness`
**Path:** `/home/claude/harness`

---

## Session Start

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/harness /home/claude/harness
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus /home/claude/corpus
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4 /home/claude/csnobol4
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64 /home/claude/x64
```

**Build:**
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh   # second oracle
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh    # primary oracle
```

## Key adapters

```
harness/adapters/dotnet/run_crosscheck_dotnet.sh   — snobol4dotnet crosscheck
harness/adapters/SCRIP/                          — SCRIP frontend × backend adapters
```

## snobol4dotnet crosscheck

```bash
DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
DOTNET_ROOT=/usr/local/dotnet10 \
bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
```

## Monitor

The sync-step monitor lives in `SCRIP/test/monitor/`. The harness provides
adapters for running cross-engine comparisons.
