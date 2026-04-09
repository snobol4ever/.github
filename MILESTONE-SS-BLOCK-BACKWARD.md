# MILESTONE-SS-BLOCK-BACKWARD.md — M-SS-BLOCK Backward Pass (§6 UNOPB→TREPU5)

**Track:** Silly SNOBOL4 M-SS-BLOCK  
**Direction:** BACKWARD — start at UNOPB (last block of §6), work toward watermark  
**Partner:** MILESTONE-SS-BLOCK-FORWARD.md (starts at TREPUB, moves forward)  
**Meet-in-middle target:** TREPU3/TREPU5 boundary (~v311.sil line 2481)

---

## Context

M-SS-BLOCK verifies each labeled SIL block against the oracle (snobol4.c generated C)
and our Silly C translation, one label at a time. This session starts at the END of
§6 and works backward — each session verifies the block just before the previous one.

**Source oracle:** `/home/claude/work/snobol4-2.3.3/snobol4.c`  
**SIL source:** `/home/claude/work/snobol4-2.3.3/v311.sil`  
**Silly source:** `/home/claude/one4all/src/silly/`

---

## Remaining §6 Blocks — Backward Order

Work these in reverse order (bottom to top):

| Block | SIL line | File | Status |
|-------|----------|------|--------|
| UNOPB | 2516 | expr.c | ⬜ **← START HERE** |
| UNOPA | 2510 | expr.c | ⬜ |
| UNOP  | 2506 | expr.c | ⬜ |
| TREPU6 | 2490 | trepub.c | ⬜ |
| TREPU5 | 2485 | trepub.c | ⬜ **← MEET POINT** |

Stop at TREPU5. Forward session covers TREPU3 and earlier.

---

## Protocol

```bash
# Setup every session
cd /home/claude/work/snobol4-2.3.3   # oracle lives here
cd /home/claude/one4all               # our code

# For each block (going backward through the list above):
# 1. Extract SIL block: sed -n 'START,ENDp' v311.sil
# 2. Find oracle: grep -n "^L_BLOCKNAME\b" snobol4.c → sed -n
# 3. Find ours: grep -rn "BLOCKNAME\|blockname" src/silly/
# 4. Sync-step line by line
# 5. Fix any bug, build clean, commit:
#    git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" \
#        commit -m "M-SS-BLOCK-BWD BLOCKNAME: <description>"
# 6. Push, update watermark here
```

---

## Watermark (update after each block — counts DOWN)

**Current:** v311.sil line 2524 — first block to verify: UNOPB (2516)

---

## Commit naming

`M-SS-BLOCK-BWD UNOPB: <fix or "verified clean">` — use `-BWD` suffix to distinguish from forward session commits.

---

## How to find SIL blocks working backward

```bash
# Find the block boundaries for the block at line N:
# Block starts at line N (the label line)
# Block ends at the line BEFORE the next label

# Example: UNOPB at line 2516, next label BASE at 2524
# So UNOPB block = lines 2516..2523
sed -n '2516,2523p' /home/claude/work/snobol4-2.3.3/v311.sil

# Find in oracle:
grep -n "L_UNOPB\|^UNOP\b" /home/claude/work/snobol4-2.3.3/snobol4.c
```
