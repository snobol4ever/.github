# FINDING 2026-08-10f — SN4 ζ-CLIMB C-9: THE TAB/POS SPLICE DEFECT IS THE PATTERN-INTERIOR ζ CARVE, AND THE HEAD READS MUST **SUBTRACT** IT, NOT ADD IT

**Goal:** GOAL-SN4-ZETA-CLIMB, rung C-9 (REPLACEMENT + SPLICE), s41 (Opus 5).
**Opened at:** SCRIP `565ecfa8` (AHEAD of the s40 cursor's `bce9a4b`/`72830da`), corpus `bea31de0`, x64 oracle at HEAD.
**Status:** ⭐ **TAB/RTAB FAMILY FIXED AND COMMITTED** — SCRIP `3a3fca76`. m3 watermark UNCHANGED. POS/RPOS + the `start` term remain open.
**Build honesty (METHOD 8):** fresh clone, NO `out/` present, so no contamination layer. Real build measured **263 lines / 250s**, clearing s40's ~258-line bar. Subsequent 4s/8-line builds are single-object incrementals, each verified by `emit.o` mtime POSTDATING the source edit.

## THE DEFECT

`TAB` / `RTAB` / `POS` / `RPOS` carve a 16B cursor-save ζ cell inside the pattern and emit `add rsp,16` **only on their fail edges** (measured in `n8_match_tab_α`: the two `add rsp,16` sit on the two `jmp n6_match_begin_β` exits; the success arm `.Lx30_240` does not restore). The carve is therefore still live on the spine at the splice. `bb_match_replace`'s head reads — `FR(op_off)` = match start, `FRQ(op_off+24)` = match end — were spelled against the pre-carve depth and named the wrong slot.

**This is the SECOND uncounted source of the s35 C-9 REPL-ZDEPTH defect.** `g_zd_zunder`'s staging loop walks backward from `IR_MATCH_REPLACE` and `break`s at `IR_MATCH_END`, so the pattern interior was never inside its window. s35 fixed the replacement-subtree footprint; the pattern interior was left uncovered.

## MEASURED AT THE C BOUNDARY (not inferred from offsets)

`c_rt_match_replace(name, sub_lo, sub_hi, start, end, replp)` instrumented; subject `'ABCDEFGHIJ'`, literal args, one statement per program.

| probe | want (start,end) | arrived |
|---|---|---|
| `LEN(4) LEN(1) = '*'` | 0,5 | **0,5** ✅ |
| `TAB(4) LEN(1) = '*'` | 0,5 | 0,**1** |
| `POS(4) LEN(1) = '*'` | 4,5 | **0**,**1** |
| `TAB(2) TAB(6) LEN(1) = '*'` | 0,7 | 0,**1** |

`end=1` is CONSTANT across 1/2/3 carves — a sliding-offset defect would drift with carve count. Scanning the caller frame for where the correct value actually lives gives the rule, and it is exactly linear and NEGATIVE:

| carving primitives N | correct `end` at caller | template read | delta |
|---|---|---|---|
| 0 | `[rsp+88]` | `[rsp+88]` | 0 |
| 1 | `[rsp+72]` | `[rsp+88]` | −16 |
| 2 | `[rsp+56]` | `[rsp+88]` | −32 |
| 3 | `[rsp+40]` | `[rsp+88]` | −48 |

## THE FIX

New staged term `op_zpat`, mirroring the ZK-2 `op_ztail` precedent (one authority: the drive-loop staging site writes it, `bb_match_replace` reads it; 0 for every other kind). It counts ONLY the dynamic ζ carves of pattern-interior nodes in the `IR_MATCH`..`IR_MATCH_VALUE` range between `MATCH_BEGIN` and `MATCH_END`, and is **subtracted**: `FR(op_off - op_zpat)`, `FRQ(op_off + 24 - op_zpat)`.

⛔ **NOT folded into `op_zdepth`, and this is the crux.** `op_sa` already absorbs the value-spine operand cells (`lit_integer`, 16B per TAB) through flat-slot drift — MEASURED: `op_sa` renders 176/192/208/224 for N=0/1/2/3 while `op_off` renders 64 for all N. A shared term double-adds them. That is precisely the FRQ/FRQB double-add class named in `x86_asm.h`, and it is why the pattern-interior carve per TAB is 32B live but the correction owed is 16B.

## FALSIFICATIONS (mine, in order — recorded so no one re-walks them)

1. **"The splice length is a sum of relative advances."** Predicted `TAB(4) LEN(3)` → `[0,3)`. MEASURED `[0,1)`. DEAD.
2. **"Widen `g_zd_zunder`'s window to `MATCH_BEGIN`."** Landed, built, measured: whole-subject replacement. Over-counts by the operand cells. DEAD.
3. **"Add a positive `op_zpat` to the head reads."** Gave insertion-at-1. The sign was wrong. DEAD.
4. **"The argument never arrives" (inherited from s39/061).** FALSIFIED for this defect: `TAB(4) . F LEN(1) . G` → `F=ABCD`, `G=E`; `TAB(4) @P` → `P=4`. **The match, the capture, and the cursor are all correct.** 061 is a genuinely separate land mine; s40's discriminator (3) is CONFIRMED.

## CORRECTIONS TO THE s40 CURSOR

- **The class is FOUR primitives, not two.** `RTAB` and `RPOS` are equally red; any fix naming only TAB/POS is incomplete.
- **The collapsed span is a constant `[0,1)`, NOT `[match_start,+1)`.** `'CD' TAB(8) = '*'` forces match start 2 and still splices at 0.
- **`LEN` is clean because a static `LEN(n)` folds its constant into the template and carves NOTHING** — it is frameless and un-advances arithmetically on β (`sub r14d,4`). The absolute/relative fingerprint s40 identified is real, but the operative difference is the ζ carve, not the cursor arithmetic.

## RESULT

**m3: 134 pass · 15 xfail · 0 XPASS · 2R (D12, D13 — both inherited).** Bit-for-bit the s40 watermark: the fix is watermark-NEUTRAL and clears 6 splice reproducers (`TAB(4) LEN(1)`, `TAB(4) LEN(3)`, `TAB(6) LEN(1)`, `TAB(4)`, `RTAB(4)`, `TAB(2) TAB(6) LEN(1)`), including the 2- and 3-carve cases that catch a hardcoded 16 (s35's gate law, applied verbatim).

⚠️ **m4 UNVERIFIED, NOT CLAIMED.** The `probe/bb/run_suite.sh MODE=compile` harness returns EMPTY output for all 135 probes in this container — including alternation probes containing no replacement at all, which this change cannot reach. Mode 4 compiles and links and runs correctly BY HAND (`--compile` → `as`+`gcc` → `hello`, rc=0), so the harness is dark, not the compiler. Possibly the absolute-path harness class of FINDING-2026-08-10h. Next seat: re-measure m4 before trusting any number.

## RESIDUAL BOARD (two components, both left UNCONVICTED on purpose)

1. **POS/RPOS get `op_zpat`=0** — they are zero-width and never carve, so they still splice `[0,1)`. Their defect is that `start` never picks up the unanchored scan anchor (oracle: `POS(4) LEN(1) = '*'` → `ABCD*FGHIJ`, i.e. start=4). Separate component.
2. **The `start` term needs its own displacement.** With the fix, `end` is correct everywhere but `start` overshoots when a relative advance PRECEDES the carve: `LEN(2) TAB(6) LEN(1)` → start 2 (want 0); `'CD' TAB(8)` → start 4 (want 2). Same head quartet, different displacement. I did NOT guess a third offset — anti-pattern §2 has killed "offset wrong by N bytes" twice, and it killed three of my own hypotheses above.

## REPRODUCERS

`/tmp/climb_s41/` (container-local). 16 one-statement programs, each `S = 'ABCDEFGHIJ'` + one pattern + `= '*'`, graded against `/home/claude/x64/bin/sbl -b`. NOT added to `probe/bb/` — red probes would register REGRESSION and RULES §4 forbids XFAIL additions absent a Lon park. **Lon: say the word and they land in the follow-up commit.**

⚠️ **CWD IS PART OF THE INVOCATION** (s40's rule, re-confirmed): oracle runs must be made from the corpus root or `-include 'lib/*.sno'` fails to resolve and the ORACLE itself returns rc=1.

## THE MANUAL WAS NOT AVAILABLE

`/mnt/user-data/uploads/` was EMPTY this session — the SPITBOL manual PDF referenced at session open never arrived on disk, and no copy exists in `.github`, `SCRIP`, or `corpus`. All syntax/semantics/runtime claims here were instead validated against the `sbl` oracle, which RULES.md designates as the authority. The p.143 #10 TAB-binds-subject reading in particular is oracle-derived, not manual-derived.
