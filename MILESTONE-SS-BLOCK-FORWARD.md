# MILESTONE-SS-BLOCK-FORWARD.md — M-SS-BLOCK Forward Pass (§6 TREPUB→TREPU3)

**Track:** Silly SNOBOL4 M-SS-BLOCK  
**Direction:** FORWARD — start at watermark, advance one block at a time  
**Partner:** MILESTONE-SS-BLOCK-BACKWARD.md (starts at UNOPB, moves backward)  
**Meet-in-middle target:** TREPU3/TREPU5 boundary (~v311.sil line 2481)

---

## Context

M-SS-BLOCK verifies each labeled SIL block against the oracle (snobol4.c generated C)
and our Silly C translation, one label at a time. Method: extract the SIL block
(label line → next label), find it in snobol4.c, find our equivalent in src/silly/,
sync-step instruction by instruction, fix any divergence.

**Watermark going in:** v311.sil line 2452 (CTLADV verified ✅, NEWCRD complete)  
**Source oracle:** `/home/claude/work/snobol4-2.3.3/snobol4.c`  
**SIL source:** `/home/claude/work/snobol4-2.3.3/v311.sil`  
**Silly source:** `/home/claude/one4all/src/silly/`

---

## Remaining §6 Blocks — Forward Order

| Block | SIL line | File | Status |
|-------|----------|------|--------|
| TREPUB | 2466 | trepub.c | ⬜ |
| TREPU1 | 2468 | trepub.c | ⬜ |
| TREPU4 | 2473 | trepub.c | ⬜ |
| TREPU2 | 2477 | trepub.c | ⬜ |
| TREPU3 | 2481 | trepub.c | ⬜ **← MEET POINT** |

Stop at TREPU3. Backward session covers TREPU5 and later.

---

## Protocol

```bash
# Setup every session
cd /home/claude/work/snobol4-2.3.3   # oracle lives here
cd /home/claude/one4all               # our code

# For each block:
# 1. Extract SIL block: sed -n 'START,ENDp' v311.sil
# 2. Find oracle: grep -n "^L_BLOCKNAME\b" snobol4.c → sed -n
# 3. Find ours: grep -rn "BLOCKNAME\|blockname" src/silly/
# 4. Sync-step line by line
# 5. Fix any bug, build clean, commit:
#    git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" \
#        commit -m "M-SS-BLOCK BLOCKNAME: <description>"
# 6. Push, update watermark here
```

---

## Watermark (update after each block)

**Current:** v311.sil line 2452 — next block TREPUB (2466)

---

## Commit naming

`M-SS-BLOCK-FWD TREPUB: <fix or "verified clean">` — use `-FWD` suffix to distinguish from backward session commits on same blocks.
