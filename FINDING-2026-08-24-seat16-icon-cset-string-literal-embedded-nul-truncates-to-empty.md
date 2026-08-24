# FINDING 2026-08-24 (seat16) — ICN: A CSET/STRING LITERAL WITH AN EMBEDDED `\x00` TRUNCATES TO EMPTY

**Status: ROOT-CAUSED TO A 2-LINE REPRO. NOT FIXED. Not this session's rung (GOAL-ICON-100.md N-3,
scan depth-authority) — surfaced while diagnosing `rung36_jcon_scan1`'s residual divergence, reported
here rather than chased, since the defect is in literal construction, not the scan mechanism.**

## THE DEFECT, IN TWO LINES

```icon
procedure main(); local skips; skips := '\x00ab'; write(*skips); write(skips ? upto('a')); end
```

SCRIP (`--run`) → `0` then the program fails after (the `*skips` size). Arizona `icont -s ... -x`
→ `3` then `2` (`upto('a')` finds `a` at position 2, correctly counting the embedded NUL as member 1
of the 3-member cset `{\x00, a, b}`).

A cset (or string) literal whose ESCAPE SEQUENCE puts a literal `\x00` byte anywhere in it — not
necessarily first — evaluates to an EMPTY value at SCRIP, while Arizona correctly keeps all bytes
including the NUL. `*skips` (the size operator) is the cleanest witness: 0 vs the true member count.

## WHY THIS IS A LITERAL-CONSTRUCTION BUG, NOT A SCAN BUG

The runtime already has a NUL-safe length accessor for csets — `rt_scan_enter` (`gen_runtime.c`) calls
`kw_cset_len(sv.s)` rather than `strlen(s)` specifically for `IS_CSET_fn` subjects, which is exactly
the accommodation a NUL-aware cset needs. That the SIZE (`*skips`) is already wrong before any scan
machinery runs means the value is broken at the point of CONSTRUCTION — somewhere between the lexer's
escape-sequence handling and whatever builds the runtime cset/string object, a NUL-terminated C-string
assumption truncates the content. This is unrelated to GOAL-ICON-100.md N-3's scan-cursor depth
authority (the C-global `scan_stack`/`scan_subj`/`scan_pos` mechanism, `bb_gen_scan.cpp`) which is
what this session's rung actually touched.

## BLAST RADIUS OBSERVED

`rung36_jcon_scan1.icn`'s final section builds several csets this way, including
`skips := '\x00\x0f\x1e-<KZix\x87\x96\xa5\xb4\xc3\xd2\xe1\xf0\xff'` (18 members, `\x00` first). Every
`upto()` call in that test using `skips` as EITHER the subject or the needle cset comes back empty or
wrong against the Arizona oracle — `ascii?skips`, `letts?skips`, `vowls?skips`, and all five
`skips?*` lines (`skips` as subject). This one bug likely accounts for most, but probably not all, of
`jcon_scan1`'s residual divergence — `ascii?vowls` (a cset with no embedded NUL) is ALSO off by one
with a spurious trailing value in the same run, not obviously explained by this defect alone and not
investigated further this session.

## NOT INVESTIGATED (left for whoever takes this)

Where the truncation actually happens — lexer escape-sequence decoding (`src/parser/icon/`), the
runtime cset-construction path, or an intermediate C-string copy — was not traced. `kw_cset_len`'s
existence suggests someone already anticipated NUL-safe csets needing to work at the point of USE;
this defect is upstream of that, at the point of BUILD.

## REPRO FILE

`/tmp/cset_nul_repro.icn` on seat16's box this session (not committed to any repo — recreate from the
2-line source above, `--run` needs no input file).
