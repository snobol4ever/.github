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
5. ⛔ MANDATORY — NO EXCEPTIONS — update watermark in THIS FILE and push .github before touching next block:
   - Change the "Current watermark" line below to the line number of the block just verified
   - Change the "Next block" line to the block found by the grep command
   - `git add MILESTONE-SS-BLOCK-BACKWARD.md && git commit -m "SSB-N watermark→LINENUM (BLOCKNAME)" && git push`
   - If you skip this step you are broken. The next session will start at the wrong place.

---

⚠️ **Watermark lives in SESSION-silly-snobol4.md §NOW — one place only. Do not add it here.**

---

## Completed blocks (this pass, newest first)

| Block | Line | Result |
|-------|------|--------|
| OTLIST | 10617 | 🐛 fixed — missing entirely (self-ref TTL header) |
| INLIST | 10612 | 🐛 fixed — missing entirely (self-ref TTL header) [PLB36] |
| KVEND | 10610 | ✅ clean — LHERE sentinel, no C equivalent needed |
| FATLCL | 10608 | ✅ clean — value cell D(0,0,I) correct; name-spec slot is systemic KVLIST gap |
| CSTNCL | 10606 | 🐛 fixed — D0→D(0,0,I) missing integer type tag |
| GCTTTL | 10602 | 🐛 fixed — real-type slot + MAXICL cell absent + dead GCTTTL_val removed |
| EXN2CL | 10600 | ✅ clean — D(0,0,I) correct; name-spec is systemic KVLIST gap |
| DIGSVL | 10596 | 🐛 fixed — PI_val dead real_t→PIVCL DESCR_t with .v=R |
| PARMVL | 10594 | ✅ clean — D(0,0,S) correct |
| UCASVL | 10592 | ✅ clean — D0 correct |
| LCASVL | 10590 | ✅ clean — D0 correct |
| FNCLKY | 10589 | 🐛 fixed — missing definition added (extern-only→D0) |
| LVLCL | 10588 | ✅ clean — D(0,0,I) correct |
| STCTKY+cluster | 10587 | 🐛 fixed — TTL|MARK→0 on all 10 _KY name-spec DESCRs |
| EXNOCL | 10586 | ✅ clean — D(0,0,I) correct |
| ALPHVL | 10584 | ✅ clean — D0 correct |
| STNOKY | 10583 | ✅ clean (covered by cluster fix) |
| STNOCL/LNNOCL/FILENM | 10582 | 🐛 fixed — D0→D(0,0,I/I/S) missing type tags |
| RETPCL | 10580 | ✅ clean — D(0,0,S) correct |
| LSTNCL | 10578 | ✅ clean — D(0,0,I) correct |
| FALCL | 10576 | ✅ clean |
| FALKY | 10577 | ✅ clean (cluster fix) |
| SUCPAT+PAT cluster | 10574 | 🐛 fixed — D0→D(0,0,P) on 7 PAT cells |
| SUCCKY | 10575 | ✅ clean (cluster fix) |
| REMPAT | 10572 | ✅ clean |
| REMKY | 10573 | ✅ clean (cluster fix) |
| LSLNCL | 10570 | ✅ clean |
| LSFLNM | 10568 | ✅ clean |
| LNNOCL | 10566 | ✅ clean (fixed earlier) |
| FILENM | 10564 | ✅ clean (fixed earlier) |
| FNCPAT–FAILKY cluster | 10558–63 | ✅ clean |
| ARBPAT–BALKY | 10554–57 | ✅ clean |
| ERRTXT | 10552 | ✅ clean |
| ETXTKY | 10553 | 🐛 fixed — missing definition added |
| ERRTKY | 10551 | ✅ clean (cluster fix) |
| ERRTYP | 10550 | ✅ clean — D(0,0,I) |
| KVLIST | 10549 | ⚠️ systemic TTL header gap — noted |
| KNEND | 10547 | ✅ clean — LHERE sentinel |
| ERRLCL–ABNDCL | 10535–45 | ✅ clean (batch) |
| OUTSW/MLENCL/INSW/GCTRCL | 10517–23 | ✅ clean |
| TRACL/FTLLCL | 10527–33 | ✅ clean |
| DTLIST | 10482 | 🐛 fixed — arena pair list built; ARRSP/ASSCSP added; header .a/.v wired; DTATL wired |
| DTLEND | 10507 | ✅ LHERE sentinel |
| KNLIST header | 10510 | 🐛 noted — BUG-KNLIST-PAIRLIST (header .a/.v=0; pairs absent; KNATL.a=0) |
| EXLMCL–ABNDCL (13 blocks) | 10515–10545 | ✅ all value cells correct; name-spec companions systemic KNLIST gap |
| FULLCL | 10525 | 🐛 fixed — D0→D(0,0,I) |
| BKGNCL | 10530 | 🐛 fixed — missing entirely |
| OTSATL | 10622 | 🐛 fixed — missing entirely (self-ref TTL header) |
| OUTPUT | 10623 | 🐛 fixed — 1-slot→2-slot; slot[1].a=OUTPSP |
| PUNCH | 10625 | 🐛 fixed — .a was 0, now D(UNITP,0,I) |
| PCHFST | 10626 | 🐛 fixed — missing entirely |
| INSATL | 10627 | 🐛 fixed — missing entirely (self-ref TTL header) |
| INPUT | 10628 | 🐛 fixed — .a was 0, now D(UNITI,0,I) |
| DFLSIZ | 10629 | 🐛 fixed — .a was 0, now D(VLRECL,0,I) |
| TERMIN | 10630 | 🐛 fixed — 1-slot→2-slot; slot[1]=VLRECL,0,I |
| TRLIST | 10633 | 🐛 fixed — missing entirely (2-slot self-ref+TVALL) |
| VALTRS | 10635 | 🐛 fixed — missing entirely (3-slot block) |
| TFNCLP | 10638 | 🐛 fixed — extern-only→2-slot array; both .a wired |
| TFNRLP | 10640 | 🐛 fixed — extern-only→14-slot array; all .a wired |
| TRCBLK | 10656 | 🐛 fixed — slot[0].a self-ref was 0 |
| LIT1CL | 10658 | 🐛 fixed — 1-slot→4-slot; .a[0],[2]=P2A(&LITFN) |
| ATRHD | 10663 | 🐛 fixed — missing entirely |
| ATPRCL | 10664 | 🐛 fixed — missing entirely (3-slot block) |
| ATEXCL | 10667 | 🐛 fixed — missing entirely |
| ATDTP/IIDTP–PVDTP | 10671–10678 | ✅ clean |
| RIDTP–VVDTP/ARTHCL/RSTAT/SCNCL/WSTAT | 10679–10694 | ✅ clean |
| TIMECL–FNVLCL cluster (10 blocks) | 10695–10707 | ✅ clean |
| HIDECL/INICOM/LENFCL/LISTCL | 10708–10711 | ✅ clean |
| LLIST | 10712 | ✅ clean |
| NAMGCL/NERRCL/SCERCL/SPITCL/STATCL | 10713–10717 | ✅ clean |
| BLOKCL | 10719 | 🐛 fixed — missing entirely, added D(0,0,I) + extern [PLB117] |
| CHARCL/ARBSIZ | 10724–10725 | ✅ clean |
| EXTVAL | 10731 | 🐛 fixed — wrong name EXTVSL→EXTVAL |
| CNDSIZ/CODELT/DSCRTW/EOSCL/ESALIM | 10726–10730 | ✅ clean |
| LNODSZ/IOBLSZ/INCLSZ/GTOCL/GOBRCL/FBLKRQ | 10732–10737 | ✅ clean |
| NODSIZ/OBEND/OCALIM/ONECL/OUTBLK/ERRBLK | 10738–10744 | ✅ clean |
| STARSZ/SNODSZ/SIZLMT | 10745–10747 | ✅ clean |
| ZEROCL | 10748 | ✅ clean |
| TRSKEL | 10749 | 🐛 fixed — wrong name TRSKELS→TRSKEL + .a=P2A(TRCBLK) missing |
| COMDCT | 10750 | ✅ clean |
| COMREG | 10751 | 🐛 fixed — .a=P2A(&ELEMND) missing |
| ARBACK/ARHEAD/ARTAIL | 10757–10759 | 🐛 fixed — .a.i and .v=P both missing on ARHEAD/ARTAIL; .a.i=0 on ARBACK |
| STRPAT | 10760 | 🐛 fixed — .v=P missing |
| ANYCCL + fn-descriptor cluster | 10764–12119 | 🐛 fixed — 14 fn-descriptor bugs (SSB-1–3) |
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
Next backward session: **SSB-5**.
