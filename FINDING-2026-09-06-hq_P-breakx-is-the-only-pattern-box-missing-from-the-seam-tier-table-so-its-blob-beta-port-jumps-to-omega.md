# FINDING — BREAKX is the only pattern box missing from `zdp_seam_tier`, so its blob β port is wired to ω and the pattern never extends

**hq_P · 2026-09-06 · MODE OCTET · row `flip-gimpel-RWORD` · cure SCRIP `b5313ff2d` · corpus `999270288` · RT_OPT `-O0` · incremental `make` · oracle `/home/resources/x64/bin/sbl -bf`**

⛔ **Every board below is re-measured on the MERGED tree.** The first reading was taken on `30c5fa8da` and nine commits landed under it during the sitting (two of them SNOBOL4-touching, `ece36b4cb` ARBNO and `7338727e0` csnobol4 error types), so that reading described a tree that no longer existed — FETCH-IS-NOT-CHECKOUT, paid once more.

## The defect in one line

`src/ir/zeta_depth.c:21` `zdp_seam_tier()` enumerates every pattern box that owns a live β; **`IR_MATCH_BREAKX` is absent from the enumeration and falls through to `default: return 0`**. `resume_carrier_ok()` (`src/emitter/emit.cpp:2464`) therefore refuses BREAKX as a resume carrier, and the emitted pattern blob wires `PAT$n_β` straight to `PAT$n_ω` — so a BREAKX that must EXTEND (its `ARBNO(LEN(1) BREAK(S))` half) never gets a second attempt.

## The seven-line witness (m3 and m4, both wrong the same way)

```
	&ANCHOR = 1
	R = 'ab cd ef'
	B1 = BREAKX(' ')
	B2 = B1
	R  B2 ' ef'		:S(S1)F(F1)
S1	OUTPUT = 'MATCH'	:(END)
F1	OUTPUT = 'FAIL'
END
```
`sbl -bf` prints `MATCH`; SCRIP printed `FAIL`. With `B1` in place of `B2` SCRIP printed `MATCH` — **one variable of indirection is fine, two are not**, because the second assignment is what forces the pattern through a blob of its own.

## The asm diff that named the cause (ASM-DIFF-FIRST step 2, one line)

`./scrip --compile -o w.s w.sno`, then the same program with the BREAKX swapped for each other pattern kind — `PAT$0_β`'s single instruction:

```diff
+ ARB             jmp n0_match_arb_β
+ BAL             jmp n0_match_bal_β
+ ARBNO(LEN(1))   jmp n0_match_arbno_β
+ SPAN(' ')       jmp n0_match_span_β
+ 'ab' | 'ab cd'  jmp n0_match_alternate_β
- BREAKX(' ')     jmp PAT$0_ω
```
⭐ **Every other kind routes the blob's β into its own β arm; BREAKX alone bypasses it.** The BREAKX β arm is emitted, correct, and unreachable — `n0_match_breakx_β` sits in the blob as dead code. That is why the bug reads as "BREAKX does not backtrack" rather than as a wiring fault.

## Why the omission is an omission and not a ruling

The two neighbouring classifiers in the same file already treat BREAKX as a multi-result box, and they disagree with `zdp_seam_tier` in exactly the direction that makes it a slip:
- `zdp_scratch_cell()` (`zeta_depth.c:16`) **lists** `IR_MATCH_BREAKX` beside SPAN/BREAK/ARB/BAL.
- `zdp_scan_pure()` (`zeta_depth.c:17`) **excludes** `IR_MATCH_BREAKX` while listing `IR_MATCH_BREAK` and `IR_MATCH_SPAN` — i.e. it already records the one fact that matters, that BREAKX is not a deterministic scan.

## The cure — one line

```diff
-case IR_MATCH_ARBNO: case IR_MATCH_ARB: case IR_MATCH_BAL: return 1;
+case IR_MATCH_ARBNO: case IR_MATCH_ARB: case IR_MATCH_BAL: case IR_MATCH_BREAKX: return 1;
```
Tier 1 is the multi-result group (ARB · ARBNO · BAL), which is what BREAKX is. After the cure `PAT$0_β` reads `jmp n0_match_breakx_β`, the same shape as every peer.

## Census of the rest of the table — the neighbours are NOT the same gap (measured, not assumed)

Of the 32 `IR_MATCH_*` ops, those still absent from `zdp_seam_tier` after the cure are `ABORT BEGIN END FENCE0 FENCE1 REPLACE RETRY CALLOUT LAMBDA VALUE`. None is a live second gap of this class: FENCE0/FENCE1 block recede **by definition** (tier 0 is their correct answer), ABORT/BEGIN/END/REPLACE/RETRY are not multi-result, and `IR_MATCH_VALUE` is only reachable with `SCRIP_PAT_EAGER_CALL=0` (`lower_snobol4.c:1868–1873`) — the default path builds `IR_MATCH_DEFER`, which is tier 2 and already correct. ⚠️ `IR_MATCH_LAMBDA` (`lower_snobol4.c:1858`) is **NOT measured here** — whether a lambda pattern can yield more than one result is an open question, named so the next reader does not mistake this census for a clean bill.

## Scope — the shared-node duty, discharged

`grep -c IR_MATCH_BREAKX src/lower/lower_*.c` → `lower_snobol4.c:1`, every other lowerer `0`; `zdp_seam_tier` is called from `lower_snobol4.c` and from the emitter's language-blind `resume_carrier_ok`. So only frontends that lower through `lower_snobol4.c` can move: SNOBOL4 and **Snocone**. Snocone smoke re-run as the control arm: `PASS=5 FAIL=0`.

## Control arms

- ✅ Minimal witness and ten ablation witnesses (`BREAKX`/`ARB`/`ARBNO`/`BAL`/`SPAN`/alternation × 1, 2, 3 levels of pattern-value indirection; `POS(0)` vs `&ANCHOR = 1`; literal vs variable cset) — **byte-identical to `sbl -bf` on every one** after the cure.
- ✅ `SPAN` stays RED in both SCRIP and the oracle at 2 levels — the control that proves the sweep is not just turning everything green: SPAN genuinely does not backtrack in SPITBOL.
- ✅ `RWORD_driver` (gimpel): `m3=DIFF m4=DIFF` → `m3=PASS m4=PASS`, output byte-identical to its oracle-cut `.ref`.
- ✅ **Gimpel board on the merged tree: `total=144 scored=126 unscr=18 m3_pass=97 m3_fail=29 m4_pass=97 m4_fail=29`** — 96/126 → **97/126** in both modes, and no program lost. ⭐ The board is also the CURE'S OWN GUARD: `RWORD_driver` is a live suite program, so a regression re-reds it without any new witness having to be added to a shared denominator mid-announcement.
- ✅ Snocone smoke `PASS=5 FAIL=0`.
- ⭐ **The 2 SNOBOL4 ladder reds at rung 14 (`ladder__rung14_fnclevel_rtntype`) are PRE-EXISTING, proven not asserted**: `git stash` → rebuild → `--only 14` printed the identical `PASS=16 FAIL=2` on the pre-cure binary. They belong to row `conform-fnclevel-not-tracked`.

## The method note worth keeping

The trigger looked like `POS(0)` for three witnesses running, because `POS(0)` was the ingredient present in every failing case. It is not the cause — `&ANCHOR = 1` reproduces the same failure with no `POS` anywhere. `POS(0)` was merely the cheapest way to make the extension NECESSARY, by forbidding the unanchored scan from starting at a position where BREAKX's first attempt already succeeds. ⭐ **An ingredient that makes a defect VISIBLE reads exactly like the ingredient that CAUSES it, and the difference costs one ablation to settle.**
