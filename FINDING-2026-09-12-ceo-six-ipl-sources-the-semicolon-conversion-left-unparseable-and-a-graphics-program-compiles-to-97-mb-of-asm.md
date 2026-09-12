# FINDING 2026-09-12 14:46 CDT (ceo) — six IPL sources the semicolon conversion left unparseable, and a graphics program compiles to 97 MB of asm

**Tree:** corpus `96feb9df5` (cure) over SCRIP `b35ed8e2a` · seat ceo (MODE TRIO, lane ICON TO 100%) · cursor CEO-628.

## Measurement

A private compile probe over all 851 IPL `.icn` (no board, no row) with the runner's `ICONPATH` reproduces the IPL compile tier's
`parseerr=8` exactly: `gincl/maccolor`, `incl/lshade` (include fragments — `icont -c` refuses them too: *"map16": invalid declaration*;
already UNGRADABLE rows) and six conversion residues, each confirmed against the upstream drop `/home/resources/icon-master/ipl`:

| file | residue | fix |
|---|---|---|
| gprogs/breakout.icn:60,66 | `;` appended inside the trailing comment after a continued string (`#black sphere;;`) | `";  #comment` |
| gprogs/penelope.icn:619 | same | same |
| gprogs/dlgvu.icn:1323 | `n +:= 1 / 7200.` — a real literal ending in `.` took no terminator | `7200.;` (both engines accept it) |
| progs/proto.icn:199,201 | bare literal statements before a continued literal (`"abc"`, `'abc'`) | terminated |
| progs/shar.icn:32 | `;;` spliced INSIDE a string literal (`\n;;  # 3. Execute…`) — the archive banner was corrupted, not only unterminated | upstream text restored, `);` |
| progs/xtable.icn | converted on 3 of 138 lines only | converted by hand in full |

Every one compiles rc=0 under `scrip --compile` with the runner's ICONPATH and under `icont -s -c`. The package's `ALL.icn` container
(built `3b3b5b874`, 2026-09-05, ignored by the runner's `! -name ALL.icn`) still carries the pre-fix text, including shar's corrupted
string, and no script grades it — a rebuild is owed by whoever next runs `util_build_package_suite.py` on ipl. None of the six has a
`.std`; xtable sits in UNGRADED as NEEDS_ARGV_FIXTURE.

## Surfaced, not cured

`gprogs/dlgvu.icn` (1900 lines) compiles rc=0 in 8.06 s to a 97 MB `.s` (1.38 M lines: 682 K `mov`, 62 K `.type`/`.size` pairs);
`gprogs/penelope.icn` (1256 lines) 6.34 s, 82 MB. The graphics programs link the whole gprocs library and every linked procedure is
emitted. Under the IPL runner's 8 s compile timeout dlgvu now reads TIMEOUT at fleet load — a compile-time class, not a parse red.

## Probe hazard (mine)

Without `ICONPATH` the same probe reads 165 gprogs link gaps: the driver's search list is IPATH/ICONPATH, then `…/ipl/procs`, then
the program's own directory — never `gprocs`. The runner exports ICONPATH at line 95; a by-hand compile of a gprogs program must too.
