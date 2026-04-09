# MILESTONE-SS-BLOCK-BACKWARD.md — M-SS-BLOCK Backward Pass

**Direction:** BACKWARD — start at v311.sil line 12293, work one block at a time toward line ~2452  
**Partner:** MILESTONE-SS-BLOCK-FORWARD.md (starts at line 2452, works forward)  
**Meet-in-middle:** somewhere around line 7000–8000 (to be declared when both sessions converge)

---

## Scope

All labeled blocks from v311.sil line 12293 back to where the forward pass reaches, one label at a time.  
§20 BLOCKS (lines 7038–10208, 328 labels) — **SKIP entirely** per ground rules.  
Everything else is in scope: §24 Data, §23 Errors, §22 Termination, §21 Common Code, §19–§7.

**Approximate block count remaining backward:** ~1,100 (excluding §20)

---

## Method (one block per commit)

1. Find the block whose label line is the highest line number not yet verified:
   ```bash
   # Get all labels, find the one just at or below current backward watermark
   grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1<=WATERMARK' | tail -2
   ```
2. Extract SIL block (label line → line before next label):
   ```bash
   sed -n 'START,ENDp' /home/claude/work/snobol4-2.3.3/v311.sil
   ```
3. Find oracle block in snobol4.c:
   ```bash
   grep -n "L_BLOCKNAME\|^BLOCKNAME(" /home/claude/work/snobol4-2.3.3/snobol4.c
   ```
4. Find our Silly equivalent:
   ```bash
   grep -rn "BLOCKNAME" /home/claude/one4all/src/silly/
   ```
5. Sync-step instruction by instruction. Fix any divergence.
6. Build clean: `gcc -Wall -Wextra -std=c99 -g -O0 $(find src/silly -name "*.c") -lm -o /tmp/silly-check -I src/silly`
7. Commit: `git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" commit -m "M-SS-BLOCK-BWD BLOCKNAME: <fix or verified clean>"`
8. Update watermark below (watermark = label line of block just verified).

---

## Skip rule for §20 BLOCKS

When backward watermark reaches line 10208, jump directly to 7037:
```bash
# v311.sil lines 7038–10208 = BLOCKS section — SKIP
# Resume backward from line 7037 (end of §19)
```

---

## Watermark (update after each block — counts DOWN)

**Current watermark:** v311.sil line **12293** (end of file)  
**Next block to verify:** last label in file = R1MCL (line 12292) — then work backward

---

## Nature of §24 Data blocks

Most blocks from ~10209 to 12293 are data definitions (FORMAT strings, REAL constants,
DESCR initializers) — not executable logic. They verify quickly: check the C global
declaration in `src/silly/data.h` / `sil_data.c` matches the SIL type and initial value.
The executable logic blocks (§21 Common Code, §22 Termination, §23 Errors) are at
lines 10209–10480 and are the meaty ones going backward.

---

## Session start commands

```bash
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
grep "^## " /home/claude/.github/GENERAL-RULES.md
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/SESSION-silly-snobol4.md
cat /home/claude/.github/MILESTONE-SS-BLOCK-BACKWARD.md   # this file — get watermark
cd /home/claude/one4all && git pull --rebase
# Then: next block = last label at or below watermark line
```
