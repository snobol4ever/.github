# MILESTONE-SS-BLOCK-BACKWARD.md — M-SS-BLOCK Backward Pass

**Direction:** BACKWARD — start at v311.sil line 12293, work one block at a time to line 1  
**Goal:** verify every labeled block from the end to the beginning of v311.sil  
**Partner:** MILESTONE-SS-BLOCK-FORWARD.md (runs forward from 955 to 12293 — independently, no convergence)

---

## Scope

All labeled blocks from v311.sil line 12293 backward to line 1.  
§20 BLOCKS (lines 7038–10208) — **SKIP** per ground rules. Jump watermark from 10209 to 7037 when reached.

---

## Method (one block per commit)

1. Find next label below current watermark:
   ```bash
   grep -n "^[A-Z][A-Z0-9]*\b" /home/claude/work/snobol4-2.3.3/v311.sil | awk -F: '$1<WATERMARK' | tail -1
   ```
2. Extract SIL block (label line → line before next label):
   ```bash
   sed -n 'START,ENDp' /home/claude/work/snobol4-2.3.3/v311.sil
   ```
3. Find oracle in snobol4.c or data_init.h, find ours in src/silly/, sync-step line by line.
4. Fix any divergence. Build clean. Commit:
   ```bash
   git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" \
       commit -m "M-SS-BLOCK-BWD BLOCKNAME: <fix or verified clean>"
   ```
5. Update watermark below (set to label line of block just verified).

---

## Watermark (update after each block — counts DOWN toward 1)

**Current watermark:** v311.sil line **12120** (SUCCPT verified ✅)  
**Next block:** STARPT (line 12107)

---

## Completed blocks (this pass, newest first)

| Block | Line | Result |
|-------|------|--------|
| R1MCL | 12292 | ✅ fixed — real_t→DESCR_t with .v=R |
| RZERCL | 12291 | ✅ fixed — real_t→DESCR_t with .v=R |
| FORMAT blocks (ALOCFL–WRITNO) | 12254–12288 | ✅ clean — %D/%F→printf intentional PLB10 |
| EMSG1–EMSG3, EMSG14, ILCHAR–OPNLIT | 12238–12248 | ✅ clean |
| MSG36–38 | — | ✅ correctly absent (BLOCKS skipped) |
| MSG1–MSG35, MSG39 | 12195–12233 | ✅ all verbatim correct |
| MSGLST | 12151 | ✅ clean — const char *MSGNO[] is correct equivalent |
| VALBLK | 12141 | 🐛 fixed — 7-slot block entirely absent, added |
| TKEYPL | 12137 | ✅ clean |
| TFEXPL | 12134 | ✅ clean |
| TFENPL | 12131 | ✅ clean |
| TLABPL | 12128 | ✅ clean |
| TVALPL | 12125 | ✅ clean |
| SUCCPT | 12120 | ✅ clean |

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

---

## Session numbering (2026-04-09l)

Backward sessions use **SSB-N** series (SSB-1, SSB-2, SSB-3, SSB-4, ...) to avoid
collision with Forward sessions (SS-47, SS-48, SS-49, SS-50, SS-51, ...).
Next backward session: **SSB-4**.
