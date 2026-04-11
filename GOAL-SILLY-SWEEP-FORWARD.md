# GOAL-SILLY-SWEEP-FORWARD — Silly Forward Sweep

**Repo:** one4all (`src/silly/`)
**Done when:** Forward watermark reaches v311.sil line 12293 (or 7037→10209 jump over BLOCKS)

## What this is

Three-way sync-step walk of every labeled SIL block from line 955 (BEGIN) forward to
line 12293. Three columns simultaneous for every SIL instruction:
1. `v311.sil` — the spec
2. `snobol4.c` — generated C ground truth
3. `src/silly/sil_*.c` — our translation

⛔ Two-way (SIL + ours only) is wrong. All three, every line, no exceptions.

**Skip:** §20 BLOCKS (lines 7038–10208) — jump watermark from 7037 → 10209.

## Setup (extract only — do NOT build CSNOBOL4)

Lon supplies `snobol4-2_3_3_tar.gz`. Extract, then stop — no `./configure`, no `make`:
```bash
apt-get install -y m4
mkdir -p /home/claude/work
tar -xzf snobol4-2_3_3_tar.gz -C /home/claude/work
# Done. v311.sil and snobol4.c are the only files needed.
```

## Key paths

```
/home/claude/work/snobol4-2.3.3/v311.sil      # SIL spec (12293 lines)
/home/claude/work/snobol4-2.3.3/snobol4.c     # generated C ground truth
/home/claude/one4all/src/silly/                # our translation
```

## Build gate (every step)

```bash
cd /home/claude/one4all && git pull --rebase
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
# must be clean
```

## Watermark — THE ONLY AUTHORITY

**Current watermark:** v311.sil line **6749**
**Next block:** DMPK1 (line 6750)

⛔ This file is the sole authority. SESSION files, SESSIONS_ARCHIVE — all stale. This wins.

To find next block:
```bash
grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1>6749' | head -1
```

## Steps

Each step = one labeled SIL block verified and committed. Steps are not pre-enumerated —
the blocks are the steps. Work one block per commit:

```bash
git -c user.name="LCherryholmes" -c user.email="lcherryh@yahoo.com" \
    commit -m "SILLY-FWD BLOCKNAME: <fix or verified clean>"
```

After each commit: update watermark in THIS FILE. Push .github. Then next block.

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

## Rules

- Three-way diff: v311.sil + snobol4.c + ours, all three simultaneously, every SIL line. Never two-way.
- Watermark in THIS file is sole authority. All other sources are stale.
- Build gate clean before every commit: zero errors, zero warnings.
- One block per commit. Update watermark and push .github before next block.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`. See RULES.md for full rules.
