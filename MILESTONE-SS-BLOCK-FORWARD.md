# MILESTONE-SS-BLOCK-FORWARD.md — M-SS-BLOCK Forward Pass

**Direction:** FORWARD — start at v311.sil line ~2452, advance one block at a time toward line 12293  
**Partner:** MILESTONE-SS-BLOCK-BACKWARD.md (starts at line 12293, works backward)  
**Meet-in-middle:** somewhere around line 7000–8000 (to be declared when both sessions converge)

---

## Scope

All labeled blocks from v311.sil line 2452 onward through line 12293, one label at a time.  
§20 BLOCKS (lines 7038–10208, 328 labels) — **SKIP entirely** per ground rules.  
Everything else is in scope: §6 remainder, §7–§19, §21–§24.

**Approximate block count remaining forward:** ~1,100 (excluding §20)

---

## Method (one block per commit)

1. Find next label at or after watermark:
   ```bash
   grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1>WATERMARK' | head -2
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
7. Commit: `git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" commit -m "M-SS-BLOCK-FWD BLOCKNAME: <fix or verified clean>"`
8. Update watermark below.

---

## Skip rule for §20 BLOCKS

When watermark reaches line 7038, jump directly to 10209:
```bash
# v311.sil line 7038 = start of BLOCKS section — SKIP
# Resume at line 10209 (§21 Common Code)
```

---

## Watermark (update after each block)

**Current watermark:** v311.sil line **2452**  
**Next block:** TREPUB (line 2466)

---

## Session start commands

```bash
tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md
grep "^## " /home/claude/.github/GENERAL-RULES.md
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/SESSION-silly-snobol4.md
cat /home/claude/.github/MILESTONE-SS-BLOCK-FORWARD.md   # this file — get watermark
cd /home/claude/one4all && git pull --rebase
# Then: next block = first label after watermark line
```
