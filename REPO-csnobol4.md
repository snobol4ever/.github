# REPO-csnobol4.md

**GitHub:** `snobol4ever/csnobol4`
**Clone:** `https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4`

## What it is

CSNOBOL4 2.3.3 — Philip L. Budne's C port of the original Bell Labs SIL macro SNOBOL4.
Forked here as the base for snobol4ever SNOBOL4 compatibility work.

Key files:
- `v311.sil` — SIL source, the canonical spec (12293 lines)
- `snobol4.c` — main interpreter (generated C + hand-edited, ~14000 lines)
- `isnobol4.c` — instrumented variant
- `data_init.c` — runtime initialization
- `test/fence_function/` — FENCE(P) test suite (10 tests)

## Session Start

```bash
git config --global --add safe.directory /home/claude/csnobol4
cd /home/claude
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4
cd csnobol4
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
git log --oneline -3
```

⛔ Do NOT run `./configure` or `make`. See RULES.md.

Oracle (clone separately if not present):
```bash
cd /home/claude && git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64
# binary at /home/claude/x64/bin/sbl
```

## Run fence tests

```bash
cd /home/claude/csnobol4/test/fence_function
make spitbol   # oracle — should be 10/10
make csnobol4  # our build — target 10/10
make diff      # side-by-side comparison
```

## Active goals using this repo

- GOAL-CSNOBOL4-FENCE.md — implement FENCE(P) 1-argument function
