# MILESTONE-SS-BLOCK-FORWARD.md — M-SS-BLOCK Forward Pass

**Direction:** FORWARD — start at v311.sil line 2452, advance one block at a time  
**Partner:** MILESTONE-SS-BLOCK-BACKWARD.md (starts at line 12293, works backward)  
**Convergence:** determined by Lon, not declared here

---

## Scope

All labeled blocks from v311.sil line 2452 forward through 12293.  
§20 BLOCKS (lines 7038–10208) — **SKIP** per ground rules. Jump watermark from 7037 to 10209.

---

## Method (one block per commit)

1. Find next label after watermark:
   ```bash
   grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1>WATERMARK' | head -2
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

## Watermark (update after each block)

**Current watermark:** v311.sil line **2875**  
**Next block:** XYARGS (line 2895)

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
