# FINDING 2026-09-10 (hq_R) — the IPL NEEDS_STDIN_FIXTURE batch is argv-driven graphics, and the five REF_NOT_CUT re-cuts are blocked by the one-step oracle driver, not by the programs

CEO-458 gave hq_R two IPL jobs off hq_P's re-classification (corpus `29829142d`): **cut refs for the 5 REF_NOT_CUT** and **mint `.in` fixtures for the 21 NEEDS_STDIN_FIXTURE plus the zero-byte ones**. Both numbers were re-measured before any fixture was authored. Neither job is the job the row names.

Trees measured on: SCRIP `8410097ca`, corpus `868600b6e`, .github `0468c3eb2`. Oracle `/home/resources/icon-master/bin/{icon,icont,iconx}`. `RT_OPT=-O0`.

## 1. The 21 NEEDS_STDIN_FIXTURE rows are argv-driven graphics programs. No `.dat` can close any of them.

All 21 are `gprogs/`. Measured over all 21:

| fact | count |
|---|---|
| declare `procedure main(args)` | 21 of 21 |
| never touch stdin at all | 20 of 21 |
| call a graphics builtin (`WOpen`/`WAttrib`/`Pixel`/`Fg`/`DrawLine`/…) | 19 of 21 |
| run-only output under `/dev/null` stdin, no argv | **0 bytes, rc=0, for 21 of 21** |

The four rows that *look* like stdin readers are not: `blp2grid`, `imstogif` and `pat2gif` all do `input := open(file)` where `file` comes from argv, so `read(input)` reads a **file named in argv**, never `&input`. Only `imltogif` uses bare `read()`, and it calls `WOpen` seven times. The two with no graphics call of their own (`fstarlab`, `rstarlab`) reach graphics through `drawlab` in `gprocs/`.

**Supplying argv does not close them either**, which is the half that settles it. `icon fstarlab.icn 100` → rc=0, **6737 bytes of icont link-time `undeclared identifier` diagnostics** (`EraseArea`, `GotoRC`, `Event`, `Active`, `Alert`, `Bg`, …) and zero program bytes: *this oracle build has no graphics facility*. `icon iview.icn nosuch.gif` → `*** cannot open image: nosuch.gif`. And the package ships **no image data of any kind** — `find` over the whole package returns 0 `.gif`/`.pat`/`.ims`/`.blp` files — so there is no input a fixture author could supply even if graphics existed.

⭐ The general form, and it is the reason this batch survived a re-classification: **the census asked "did it read anything on stdin?" and got "it produced nothing", then wrote down the answer to a question it had not asked.** Zero bytes under `/dev/null` is consistent with *stdin-starved*, with *argv-starved*, and with *facility-missing*, and only the first of those is a task anybody can pick up. The rows were re-classified from ORACLE_REFUSES on the strength of "the oracle does not refuse it" — true, and it does not follow that work is owed.

**Action taken:** all 21 CLASS corrected to `NEEDS_ARGV_FIXTURE` with the measurement as the reason, and left in UNGRADED per the file's own asymmetry doctrine (a wrong UNGRADED looks like unfinished work; a wrong UNGRADABLE removes a program from the debt permanently and silently). **Proposed ruling to the ceo: UNGRADABLE / `NEEDS_DISPLAY`** — the class hq_T already admitted for 25 ipl gprogs, and it passes the UNGRADABLE admission test exactly: one graphics-enabled oracle build overturns all of them at once.

## 2. The 5 REF_NOT_CUT rows have real ground truth. The blocker is the cutter's instrument, and SCRIP already matches all five.

`util_cut_icon_ipl_refs.sh` cuts through the **one-step `icon` driver** with `stdout` and `stderr` combined into one file (`run_isolated`, line 119). `icont` writes **everything to stderr**, so for any program whose link closure touches a missing graphics builtin, icont's own `undeclared identifier` warnings land *inside what would be the ref* — text SCRIP can never reproduce. The `UNDECLARED_IDENTIFIER` arm sees them and rightly refuses to mint. It is refusing on the instrument's contamination, not on the program.

Two-step (`icont` → `iconx`, grading the **run** only), measured:

| program | oracle run-only | SCRIP m3 | |
|---|---|---|---|
| `gprogs/clrs2pdb.icn` | rc=0, 1 B, 0 B stderr | rc=0, 1 B | **byte-identical** |
| `gprogs/fmap2pdb.icn` | rc=0, 1 B, 0 B stderr | rc=0, 1 B | **byte-identical** |
| `gprogs/gifs2pdb.icn` | rc=0, 1 B, 0 B stderr | rc=0, 1 B | **byte-identical** |
| `gprogs/webimage.icn` | rc=0, 64 B of HTML, 0 B stderr | rc=0, 64 B | **byte-identical** |
| `gprogs/wifs2pdb.icn` | rc=0, 1 B, 0 B stderr | rc=0, 1 B | **byte-identical** |

⛔ **A second measurement any two-step cure must carry, or it will silently lose classification evidence: the one-step `icon` driver implies `-u`.** `icon` is a symlink to the `icont` ELF binary and behaves by `argv[0]`. `icont -o iview.x iview.icn` reports **0** undeclared identifiers; `icon iview.icn` reports **2**; `icont -u -o iview.x iview.icn` reports the same **2**. Programs whose warnings come from genuine link-time unresolved globals (`isd2ill` 116, `clrs2pdb` 1) report them either way. So a naive `icont` two-step would hand the `UNDECLARED_IDENTIFIER` arm a *narrower* evidence stream and quietly reclassify rows.

⛔ **And the change is NOT byte-equivalent, so it is an instrument ruling and not a re-cut.** Measured over the whole affected population: one-step combined output vs `(icont -u stderr) ++ (iconx combined)` differ on **177 of 177** `gprogs` entries. Cutting these five means changing a shared instrument other lanes' inventories are classified by. hq_R has **not** made that change. One thing that *is* settled and bounds the risk: **zero of the 92 existing `.std` refs contain an icont-shaped diagnostic**, so the change could only ever add refs, never alter one already pinned (`progs/kwicprep.std` matches a diagnostic grep but is genuine program output — a list of `.icn` descriptions).

**Left for the ceo:** the five stay `REF_NOT_CUT` with the measurement as their reason.

## 3. Three fixtures authored and three refs cut — the part of CEO-458 that was real work

Not every zero-byte row was a mirage. Three programs link clean, read stdin genuinely, and had no fixture:

- **`gprogs/fractclr.icn`** — Fractint `.map` → Icon color lists. `fractclr.dat` (7 rows), ref 86 B. **SCRIP m3 PASS · m4 PASS.**
- **`gprogs/unitgenr.icn`** — BLP unit generators. `unitgenr.dat` (7 patterns, `width,#hex`), ref 98 B. **SCRIP m3 PASS · m4 PASS.**
- **`procs/ichartp.icn`** — chart parser. Needed *two* sidecars: `ichartp.fixtures/bnfs.byte` (the sample grammar the file's own header block documents, its default filename) and `ichartp.dat` (5 sentences). Ref 386 B, exercising a single parse, an ambiguous double parse, conjunction, and the `can't parse` path. **SCRIP aborts in BOTH modes** — see the companion FINDING on `IR_REV_ASSIGN '&pos'`.

All three refs minted by `util_cut_icon_ipl_refs.sh --apply`, each confirmed across a minute boundary by the script's own determinism pass. The three rows are removed from UNGRADED.tsv. `test_gate_package_runners_print_the_inventory.sh` PASS(0) on the edited tree.

**Board effect, named rather than buried:** the IPL RUN tier gains **+3 to its denominator, +2 PASS, +1 FAIL**. The FAIL is a real compiler defect newly under test, not a regression — and it was invisible until a ref existed to expose it, which is what a denominator is for.
