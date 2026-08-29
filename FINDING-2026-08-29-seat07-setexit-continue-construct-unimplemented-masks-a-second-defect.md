# FINDING: `:(CONTINUE)` is not implemented as SPITBOL's special construct — masks a documented, unrelated defect

**Who/when:** seat07, 2026-08-29, discovered surveying `corpus/probe/csnobol4_triage/` for the
`corpus-crosscheck-probe-total-conversion` postoffice row (deciding whether `setexit_label_pruned.sno`
was safe to convert into suite format — it is not, see that directory's own `KEEP.md`).

## The witness

```snobol4
	SETEXIT(.eh35)
	:(CONTINUE)
eh35	OUTPUT = 'S' &LASTNO
END
```

Written to isolate a DIFFERENT, already-documented defect: a label reached only via `SETEXIT(.label)` gets
pruned from emission as unreachable, but mode-4's `__gva_names` address table still references it, so
`gcc`/`ld` fails to link (`undefined reference to LBL__eh35`) — an m3-vs-m4 divergence, mode-3's
in-process binary papering over the missing symbol. That part is real and reconfirmed current.

`:(CONTINUE)` deliberately fires with no error in flight — the witness's own header comment says the
oracle should report exactly that ("a different, unrelated runtime error fires... ERROR 037").

## What's actually happening

`:(CONTINUE)` is SPITBOL's construct for "resume execution from the statement after the one where the
last error occurred" — meaningful only while handling an error, and SPITBOL correctly reports it as
invalid otherwise:

```
$ sbl -bf setexit_label_pruned.sno
ERROR 037 -- goto continue with no preceding error
rc=0 (soft failure, stats trailer printed)
```

scrip does not recognize `:(CONTINUE)` as this special form at all — it lowers it as an ordinary `GOTO`
to a label literally spelled `CONTINUE`:

```
$ ./scrip setexit_label_pruned.sno < /dev/null

** Error 38 in statement 0
   transfer to undefined label: CONTINUE
rc=1
```

Since no label named `CONTINUE` exists anywhere in the program, this fires immediately and mode-3 never
reaches the `eh35` label at all — meaning mode-3 does not "paper over" the label-pruning bug the witness
exists to test; it dies for a completely unrelated reason before that code path is ever exercised. The
witness's own header comment (written when it was created) describes the two divergences as compatible
with each other; they aren't — `:(CONTINUE)` failing first hides whether the documented pruning bug would
otherwise reproduce in mode-3 at all.

## Two separate, real defects, not one

1. **`:(CONTINUE)` unimplemented as a special construct** (this finding) — scrip treats it as a bare label
   reference instead of SPITBOL's error-resume mechanism. Unknown scope: whether `SETEXIT`+`:(CONTINUE)`
   is used anywhere else in the corpus, or how big an undertaking real support would be, was not
   investigated here — out of scope for a probe-consolidation survey.
2. **SETEXIT-only-reached labels get pruned from emission but stay referenced in mode-4's address table**
   (the witness's original, documented target) — still real, still reproduces at the `gcc`/`ld` stage,
   unaffected by this finding; just currently unreachable from mode-3 because of defect 1.

## Why this matters beyond this one witness

The witness's header comment was written as if both facts were established and compatible — a stale
characterization by a session that (reasonably) never re-ran it after `:(CONTINUE)`'s behavior was written
down. Nobody re-verified it against live behavior until this survey. Converting it into suite format as-is
would have pinned defect 1's error text under a name and comment describing defect 2 — technically
byte-equal-reproducible, but misleading about what's actually being regression-tested.

## Not attempted here

No fix, no scope investigation of `:(CONTINUE)`'s other uses, no attempt to rewrite the witness to reach
`eh35` some other way. This is a probe-directory survey finding, routed as a FINDING rather than acted on,
per this project's standing "report, don't guess" discipline for anything beyond the reporting row's own
lane.
