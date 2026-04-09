# MILESTONE-SS-BLOCK-BACKWARD.md — M-SS-BLOCK Backward Pass

**Direction:** BACKWARD — start at v311.sil line 12293, work one block at a time  
**Partner:** MILESTONE-SS-BLOCK-FORWARD.md (starts at line 2452, works forward)  
**Convergence:** determined by Lon, not declared here

---

## Scope

All labeled blocks from v311.sil line 12293 backward.  
§20 BLOCKS (lines 7038–10208) — **SKIP** per ground rules. Jump watermark from 10209 to 7037.

---

## Method (one block per commit)

1. Find the label at or just below current watermark:
   ```bash
   grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1<=WATERMARK' | tail -2
   ```
2. Extract SIL block (label line → line before next label):
   ```bash
   sed -n 'START,ENDp' /home/claude/work/snobol4-2.3.3/v311.sil
   ```
3. Find oracle in snobol4.c, find ours in src/silly/, sync-step line by line.
4. Fix any divergence. Build clean. Commit:
   ```bash
   git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" \
       commit -m "M-SS-BLOCK-BWD BLOCKNAME: <fix or verified clean>"
   ```
5. Update watermark below (set to label line of block just verified).

---

## Watermark (update after each block — counts DOWN)

**Current watermark:** v311.sil line **12293**  
**Next block:** R1MCL (line 12292), then work backward

---

## Session start commands

```bash
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
grep "^## " /home/claude/.github/GENERAL-RULES.md
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/SESSION-silly-snobol4.md
cat /home/claude/.github/MILESTONE-SS-BLOCK-BACKWARD.md
cd /home/claude/one4all && git pull --rebase
```
