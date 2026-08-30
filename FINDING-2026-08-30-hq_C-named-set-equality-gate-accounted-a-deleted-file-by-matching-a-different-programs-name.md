# FINDING 2026-08-30 hq_C — the named-set equality gate accounted for a deleted file by matching a DIFFERENT program's name

**Tree:** SCRIP `ae078681` · corpus `108afa29` · .github `26af1640` · measured 2026-08-30, seat `hq_C` (`/home/claude_C`).
**Row:** `snobol4-floor-cutover-to-the-one-flat-suite-board-equality-first` (hq_C lane). Found during closure review, not during the build of the instrument.

## The claim, in one line

`scripts/test_gate_snobol4_master_named_set_equality.sh` — the instrument two independent sessions cited as
proving the SNOBOL4 correctness floor lost nothing in the flat-suite cutover — tested its category (a) with a
**substring** match while its own header promises an **ends-with** match, and that gap was not theoretical:
one genuinely retired, uncited file was being reported accounted-for on the strength of a *different*
program's name.

## The disagreement, in two lines

```
# header, line 13:
#   (a) some origin in ALL.csv ends with "__<basename>"            -- leaf program, absorbed directly
# code, line 71:
    if grep -qF "__${base}" "$ORIGINS"; then accounted_a=$((accounted_a+1))
```

`grep -F` matches anywhere in the line. So a deleted leaf whose basename is a **prefix** of a surviving
sibling's basename is accounted for by the sibling.

## Evidence: the one file this actually hid

`probe/m1/m1_include_sort_loop.{sno,ref,inc}` — a gradable `.sno`+`.ref` pair, deleted in corpus `a1d01ace`.

```
$ grep -n "__m1_include_sort_loop" ORIGINS
798:probe_m1__m1_include_sort_loop_inline        <- a DIFFERENT program (the `_inline` twin)
$ grep -cE "__m1_include_sort_loop$" ORIGINS
0                                                <- nothing actually ends with it
$ grep -c "m1_include_sort_loop" tests/snobol4/ALL.excluded.txt
0                                                <- and it was in no exclusion list
```

The deletion is **legitimate and was documented — in the commit message only.** `a1d01ace`, verbatim:
*"probe/m1/m1_include_sort_loop.{sno,ref,inc}: -INCLUDE-dependent, no suite-format representation; inline
twin already converted, -INCLUDE mechanism covered elsewhere"*. So this is not a lost program. It is a
**retirement that never reached `ALL.excluded.txt`** — the identical shape seat06 had cured hours earlier for
`crosscheck/library/test_{case,math,stack,string}`, which the same gate had correctly caught as GAPs. This one
was the fifth instance, and the loose match is the entire reason it did not surface with the other four.

## Scale: measured both ways on the same tree, same commit set

```
loose (contains):  1457 pairs = 1370 (a) + 83 (b) +  4 (c) + 0 GAP
strict (ends-with):1457 pairs = 1322 (a) +130 (b) +  4 (c) + 1 GAP   <- probe/m1/m1_include_sort_loop
```

48 of the 1370 (a)-matches held **only** under the loose reading. 47 of those were genuine intermediate suite
files that category (b) catches anyway — so the looseness was harmless for 47 and load-bearing for exactly 1.
⭐ That ratio is the trap: an over-permissive check is *right almost every time*, which is precisely why the
one case it is wrong about rides through unnoticed.

## Why this is a general class, not a one-file typo

⭐ **A gate's header comment is an unversioned digest of the code beneath it, and rots the same way any
digest does** — the same lesson CLAUDE.md already records for `test_gate_no_handencoded_bytes.sh`, whose
header still describes informational-by-default behaviour over code that sets `STRICT=1`. Here the drift ran
the other direction: **the header was right and the code was wrong**, so reading the header — the thing a
reviewer does — actively concealed the defect. Both directions are the same failure: *two statements of one
rule, only one of them executable.*

⛔ **And it is this project's own named class**: an instrument that answers a **broader** question than the one
asked of it will never say so. RULES.md § A CORRECT PROCEDURE WITH A FALSE EXPLANATION and CLAUDE.md's
`command -v` lesson both cover the narrower-question direction; this is the mirror image, and it is more
dangerous, because a broader question returns **more** greens, and greens are what nobody re-derives.

## The cheap general test

For any accounted-for / allowlist / exclusion check: **would this predicate still pass if the thing it is
looking for were deleted and only a near-neighbour remained?** If yes, it is matching the neighbourhood, not
the name. Anchor it.

## Cured in the same close

- SCRIP: category (a) now uses `origin_suffix_match`, an **exact fixed-string suffix compare** in `awk` — not
  `grep -E "…$"`, so a basename carrying regex metacharacters cannot silently re-widen the test.
- corpus: `m1_include_sort_loop` added to `ALL.excluded.txt` with its commit citation and the verbatim reason.
- Re-run after both: `1457 = 1322 (a) + 130 (b) + 5 (c) + 0 GAP`, `✅ NAMED-SET EQUALITY HOLDS` — the same
  verdict the gate gave before, now **earned under the stricter predicate instead of granted by the looser one.**

⭐ The row's own standing discipline is what produced this: it demands re-running instruments rather than
citing them. Two sessions ran this gate honestly and got a true verdict; the defect was in what the verdict
was *made of*, which only reading the instrument reveals. **Re-running an instrument tests the tree. Reading
it tests the instrument.** A closure sign-off is the right moment to do the second one, and the only moment
anybody is likely to.

## Blast radius: swept, and it is one file

Every other `grep -qF` in `scripts/` was checked (`grep -ln 'grep -qF' *.sh`, excluding the anchored
`grep -qxF`). All of them are **content-presence** tests — *does this log/ref/sidecar contain these bytes* —
where substring matching is the correct semantic, not name-membership tests where it is not
(`test_gate_capture_stdin_and_red_exit.sh`, `test_gate_out_sweep_flaky.sh`, the four `test_smoke_sn26_*bridge*`,
`test_postoffice_clear_archives_not_destroys.sh`, `util_postoffice_protocol_sync.sh`). **The defect was
confined to this one call site.** Recorded so the next reader does not re-run the sweep to find that out.
