# MILESTONE-SS-BLOCK-FORWARD.md — M-SS-BLOCK Forward Pass

**Direction:** FORWARD — start at v311.sil line 955 (BEGIN), advance one block at a time to line 12293  
**Goal:** verify every labeled block from the beginning to the end of v311.sil  
**Partner:** MILESTONE-SS-BLOCK-BACKWARD.md (runs backward from 12293 to line 1 — independently, no convergence)

---

## Scope

All labeled blocks from v311.sil line 955 forward through line 12293.  
§20 BLOCKS (lines 7038–10208) — **SKIP** per ground rules. Jump watermark from 7037 to 10209 when reached.

---

## Method (one block per commit)

1. Find next label after watermark:
   ```bash
   grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1>WATERMARK' | head -1
   ```
2. Extract SIL block (label line → line before next label):
   ```bash
   sed -n 'START,ENDp' /home/claude/work/snobol4-2.3.3/v311.sil
   ```
3. Find oracle in snobol4.c, find ours in src/silly/, sync-step line by line.
4. Fix any divergence. Build clean. Commit:
   ```bash
   git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" \
       commit -m "M-SS-BLOCK-FWD BLOCKNAME: <fix or verified clean>"
   ```
5. Update watermark below.

---

## Watermark (update after each block — counts UP toward 12293)

**Current watermark:** v311.sil line **5271**  
**Next block:** READ (line 5272)

---

## Session start commands

```bash
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
grep "^## " /home/claude/.github/GENERAL-RULES.md
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/SESSION-silly-snobol4.md
cat /home/claude/.github/MILESTONE-SS-BLOCK-FORWARD.md
cd /home/claude/one4all && git pull --rebase
```

---

## Session numbering (2026-04-09l)

Forward sessions use **SSF-N** series (SSF-47, SSF-48, SSF-49, SSF-50, ...) symmetric with
Backward sessions (**SSB-N** series). Next forward session: **SSF-51**.

---

## ⛔ WATERMARK RULE — READ THIS FIRST, EVERY SESSION

**THE ONLY AUTHORITATIVE WATERMARK IS THE `## Watermark` SECTION ABOVE IN THIS FILE.**

- `SESSION-silly-snobol4.md §NOW` is STALE. Do NOT use it for the watermark.
- `SESSIONS_ARCHIVE.md` may also be stale. Do NOT use it for the watermark.
- THIS FILE (`MILESTONE-SS-BLOCK-FORWARD.md`) is updated after every block commit.
- First command every session: `grep -A2 "^## Watermark" /home/claude/.github/MILESTONE-SS-BLOCK-FORWARD.md`
- If you read any other watermark and it disagrees with this file — THIS FILE WINS.
