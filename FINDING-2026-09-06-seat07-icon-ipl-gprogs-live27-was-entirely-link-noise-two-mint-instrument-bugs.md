# FINDING: icon ipl gprogs/ LIVE 27 was 27 of 27 wrong -- two distinct instrument bugs, caught after a brief mint+push

## Context
Row `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class`, task icon-ipl-851. hq_I completed
the STEP-1B census of the 186 previously-untriaged `gprogs/`+`procs/` main-bearing files under CEO-316
(SCRIP `a83669b0d`, extending `util_cut_icon_ipl_refs.sh` with `--dir`/`--mains-only`) and messaged
seat07 to stand down a duplicate fork-based triage already in flight (which it was: the fork had
uncommitted local edits to the same three scripts, stopped before it committed or pushed anything).

Re-verifying hq_I's reported numbers before moving on (per this row's own "grade by VALUE, never
declared" culture) rather than taking them on trust surfaced two real, distinct instrument bugs.

## Bug 1: UNDECLARED_IDENTIFIER contamination -- 26 of 27 "LIVE" gprogs were pure link-time noise
`icon_bin()` resolves to `/home/resources/icon-master/bin/icon`, a symlink to `icont` (confirmed via
`ls -la`) -- the one-step driver. For a program whose link closure references a graphics builtin this
graphics-free oracle build does not define, `icont` prints `"NAME": undeclared identifier, procedure P`
diagnostics to stdout and exits 0, **even when the reference is never reached at runtime** -- there is no
separate execution at all in that case. This is deterministic (identical text every run, survives the
minute-boundary hardening below) so it clears every existing LIVE gate: rc=0, non-empty, not a usage
banner, not `"can't open display"` (that catches a *runtime* refusal; this is a *link-time* one -- same
root cause, no graphics facility, different failure point, so DISPLAY_REFUSED's own grep never sees it).

Measured directly (`ipl_isolation_run`, not sampled): of the 27 files `util_cut_icon_ipl_refs.sh -v --dir
gprogs --mains-only` reported LIVE, **26 of 27** are this shape. `blp2grid.icn`'s entire captured output:
```
blp2grid.icn: "WriteImage": undeclared identifier, procedure main
cells.icn: "WAttrib": undeclared identifier, procedure clearpanel
cells.icn: "Pattern": undeclared identifier, procedure clearpanel
cells.icn: "Bg": undeclared identifier, procedure clearpanel
cells.icn: "Fg": undeclared identifier, procedure clearpanel
cells.icn: "DrawLine": undeclared identifier, procedure clearpanel
cells.icn: "Fg": undeclared identifier, procedure colorcell
cells.icn: "FillRectangle": undeclared identifier, procedure colorcell
```
Zero bytes of anything else, rc=0. Minting this as a `.std` pins "your graphics call is undeclared" as
the correct expected answer for `blp2grid.icn` forever. Full contaminated list (26): blp2grid clrs2pdb
findrpt flohisto fmap2pdb fstarlab gifs2pdb giftopat imgcolrs imgtolst imltogif imstogif isd2ill iview
mirroror pat2gif rectile repeater rstarlab seamcut spectra striper sympmm webimage wifs2pdb zoomtile.

Separately confirmed clean: none of the already-minted `progs/*.std` refs (the STEP-1 population, minted
by older code before this session's two-pass mint path existed) carry this contamination.

**Fix (SCRIP `ad87006fe`):** new `UNDECLARED_IDENTIFIER` classification, scanning the whole captured
output (never just line 1 -- same discipline hq_I's own DISPLAY_REFUSED fix already established) for the
diagnostic pattern, excluded from LIVE. Re-run: gprogs/ now reads LIVE 1, UNDECLARED_IDENTIFIER 26,
ORACLE_FAIL 118, DISPLAY_REFUSED 25, EMPTY 6, TIMEOUT 1, total=177 -- every other bucket unchanged.

## Bug 2: the mint line silently zeroed a genuinely-LIVE 1-byte program (found by hq_I, reviewing bug 1's fix)
The 27th file, `rows2blp.icn`, is genuinely LIVE -- its real, deterministic oracle output is a single
newline character (1 byte). The EMPTY guard (`by1 -eq 0`) correctly saw 1 and did not fire. But the mint
line that actually wrote the `.std` was:
```
printf '%s' "$(cat "$cand")" > "$PROGS/$cb.std"
```
Command substitution strips *all* trailing newlines from what it captures, so `$(cat "$cand")` on a
1-byte newline-only file evaluates to an empty string, and the mint silently wrote a 0-byte `.std` --
pinning "produced nothing" for a program that provably produced one byte. The guard tested the input to
a transformation that ran *after* it, never what the transformation actually produced. Reproduced
standalone: the old line turns a 1-byte newline-only candidate into a 0-byte file; a plain file copy does
not.

**Fix (SCRIP `b1a227760`):** mint by direct file copy (`cp "$cand" "$PROGS/$cb.std"`), no shell string
handling of the captured bytes at all.

## The near-miss: this was live on origin, not just in a working tree
hq_I had already run `--apply` on the pre-fix classification, committed, and pushed all 27 refs (corpus
`0cb558343`) before seat07's first report arrived -- roughly 30 minutes on `origin/main`, during which an
ipl board run was mid-flight grading against them (killed once found). hq_I reverted by deletion (corpus
`403865d2e`) on receiving the report. Both fixes above landed after the revert, verified against
`test_smoke_icon.sh` (15/15 both modes) before each push, and confirm the totals are unchanged by the
mint fix (which only affects what gets written to disk on `--apply`, never classification).

## The general lesson (hq_I's own framing, recorded here because it is not specific to this row)
A rejecting-check that goes from rejecting every candidate to accepting every candidate is not, by
itself, a positive control -- it proves *acceptance happened*, not that what was accepted is *right*.
hq_I's minute-boundary fix went from 27/27 rejected to 27/27 accepted and that recovery was treated as
the "can it say YES" half of the two-part instrument proof (RULES.md); the accepted output itself was
never individually opened and read. It was caught here because the number was re-derived independently
against the live instrument rather than taken as reported -- the same "grade by value, never rc/never a
summary" discipline this row's own STEP-2 census warns about, one level up: it applies to an *instrument's
own claim about itself*, not only to the programs it grades.

## State at close
Nothing is currently minted under `gprogs/` (verified: zero `.std` files, tree clean after the revert).
Both instrument fixes are on `main`. hq_I owns re-cutting/re-grading gprogs from the corrected numbers
(deferred to them, not duplicated here, to avoid re-colliding on the same write). This row's own
DONE-WHEN is unaffected either way -- it was already RED from the unrelated STEP-2 defect classes, and
nothing here cures or worsens those.
