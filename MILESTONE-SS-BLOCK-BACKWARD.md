# MILESTONE-SS-BLOCK-BACKWARD.md — M-SS-BLOCK Backward Pass

**Direction:** BACKWARD — start at v311.sil line 12293, work one block at a time to line 1  
**Goal:** verify every labeled block from the end to the beginning of v311.sil  
**Partner:** MILESTONE-SS-BLOCK-FORWARD.md (runs forward from 955 to 12293 — independently, no convergence)

---

## Scope

All labeled blocks from v311.sil line 12293 backward to line 1.

**§20 BLOCKS (lines 7038–10208) — NOT IMPLEMENTED. Skip entirely.**
BLOCKS is a conditionally-compiled (.IF BLOCKS / .FI) optional subsystem — a block-layout
interpreter separate from core SNOBOL4. Silly SNOBOL4 does not implement this feature.
When the backward pass watermark reaches 10209, jump directly to 7037 and continue.

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
3. **THREE-WAY sync-step — all three simultaneously, one SIL line at a time:**
   - Column 1: `v311.sil` — the SIL instruction (the spec)
   - Column 2: `snobol4.c` — generated C (ground truth, resolves branch ambiguity)
   - Column 3: `src/silly/sil_*.c` — our translation
   ⛔ Using v311.sil only for block boundaries = TWO-WAY. That is wrong. See GENERAL-RULES.md.
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

## Watermark (update after each block — counts DOWN toward 1)

**Current watermark:** v311.sil line **6699**  
**Next block:** DT (line 6684)

⛔ **THIS FILE is the sole authority for the BWD watermark. Never store or reference the watermark in SESSION-silly-snobol4.md, SESSIONS_ARCHIVE.md, or any other file.**

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
| VDIFFR | 7029 | ✅ clean — XYARGS + DEQL/RTXPTR/FAIL |
| TRIM | 7018 | ✅ clean — VARVAL+LOCSP+TRIMSP+GENVRZ |
| **§20 BLOCKS 7038–10208** | — | ⛔ NOT IMPLEMENTED — optional feature, skipped |
| §21 trampolines (RT1NUL…A5RTN, GENVSZ, GENVRZ, GENVIX) | 10209–10239 | ✅ all clean — inlined at call sites |
| END | 10243 | ✅ clean — ERRLCL check + XITHND + END0 path |
| FTLEND/FTLEN2/FTLEN4/FTLEN1/DMPNO/DMPK/END0/END1/END2/AVTIME/ENDALL/SYSCUT | 10253–10327 | ✅ clean — timing/dump/stats gap acknowledged |
| MAIN1 | 10405 | ✅ clean — ERR_FTLEND(18) |
| NEMO | 10408 | ✅ clean — ERR_FTLTST(8) |
| NONAME | 10411 | ✅ clean — ERR_FTLTST(4) |
| NONARY | 10414 | ✅ clean — ERR_FTLTST(3) |
| OVER | 10417 | ✅ clean — ERR_FTLEND(21) |
| PROTER | 10420 | ✅ clean — ERR_FTLTST(6) |
| SIZERR | 10423 | ✅ clean — ERR_FTLEND(23) |
| UNDF | 10426 | ✅ clean — ERR_FTLTST(5) |
| UNDFFE | 10429 | ✅ clean — ERR_FTLTST(9) |
| UNKNKW | 10432 | ✅ clean — ERR_FTLTST(7) |
| UNTERR | 10435 | ✅ clean — ERR_FTLTST(12) |
| USRINT | 10438 | ✅ clean — ERR_FTLTST(34)+UINTCL=0 |
| CNTERR | 10442 | ✅ clean — ERR_FTLERR(35) |
| SCERST | 10448 | ✅ clean — SETAC(SCERCL,1)+FTERST |
| FTLERR | 10453 | ✅ clean — ACOMPC+DECRA+SETAC+FTLTS2 |
| FTLTST | 10458 | ✅ clean — SETAC(FATLCL,0)+FTLTS2 |
| FTLTS2 | 10459 | ✅ clean — SETAC(SCERCL,2)+FTERST |
| FTERST | 10460 | ✅ clean — inlined in error handler |
| FTERBR | 10476 | ✅ clean — XITHND+SELBRA inlined |
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
| MSG36–38 | — | ✅ correctly absent (not present in v311.sil) |
| MSG1–MSG35, MSG39 | 12195–12233 | ✅ all verbatim correct |
| MSGLST | 12151 | ✅ clean — const char *MSGNO[] is correct equivalent |
| VALBLK | 12141 | 🐛 fixed — 7-slot block entirely absent, added |
| TKEYPL | 12137 | ✅ clean |
| TFEXPL | 12134 | ✅ clean |
| TFENPL | 12131 | ✅ clean |
| TLABPL | 12128 | ✅ clean |
| TVALPL | 12125 | ✅ clean |
| DMP/DUMP cluster (DMPB/DMPA/DMPX/DMPV/DMPRT/DMPI/DMPOVR) | 6699 | 🐛 fixed — DMPX+DMPV SUM YCL,YCL,XCL: used DMPSP.l instead of saved name-length; overflow check fired bleqsp.l bytes too early |
| DMK/DMPK1 | 6747 | ✅ clean |
| DUPL/DUPL1 | 6784 | ✅ clean — redundant MLENCL check harmless dead code |
| OPSYN cluster (BNBF/BNCN/BNAF/BNCF3/BNCF5/BNCF2/BNCF4/BNCF/BNYOP3/BNYOP5/BNYOP2/BNYOP4/BNYOP/UNAF/UNCF/UNYOP/OPPD/UNBF/OPSYN) | 6805–6920 | ⚠️ stub — OPSYN_fn returns FAIL; all internal labels unimplemented |
| RPLACE | 6928 | ✅ clean |
| REVERS | 6954 | ✅ clean |
| SIZE | 6969 | ✅ clean |
| SUBSTR | 6981 | 🐛 fixed — XCALL_XSUBSTR called with 3 args; len (D_A(ZPTR)) was missing; extern decl corrected |
| TIME | 7007 | 🐛 fixed — XCALL_MSTIME/XCALL_SBREAL set .f (flag byte) to R; should be 0; also .a.f union used correctly now |
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
