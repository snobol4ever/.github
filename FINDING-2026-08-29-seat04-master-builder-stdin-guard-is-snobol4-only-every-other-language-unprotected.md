# FINDING 2026-08-29 seat04: `util_build_master_suite.py`'s entire stdin/companion exclusion system, and its
# `ALL.in` stdin-sidecar writer, are gated behind `if lang == "snobol4":` — every other language absorption
# (icon, prolog, raku, rebus, snocone, pascal) has zero stdin protection, and can silently absorb a
# stdin-reading program as if it takes no input.

Row: `pascal-master-flatten-and-scrip-test-pas` (seat04+hq_P). Found while verifying the pascal master before
deleting any loose sources — not this row's bug to fix, routing it because it is cross-cutting and live right
now across multiple seats' concurrent absorptions under the all-hands consolidation.

## Concrete instance that surfaced it
`corpus/tests/pascal/{read1,read2,read3,read4}.pas` are genuine stdin-reading programs (`read`/`readln`/`eof`/
`eoln` on standard input, no filename argument), each with a matching `read{1,2,3,4}.in` sidecar at the same
top-level path. All four are already absorbed into `corpus/tests/pascal/master/ALL.csv` (origins `read1__read1`,
`read2__read2`, `read3__read3`, `read4__read4`, rows 4/12/65/108) — but `master/ALL.excluded.txt` is 0 bytes
(nothing excluded) and there is **no `master/ALL.in`** at all. If `test_gate_pascal_m3.sh`/`_m4.sh` were
repointed to grade from the master (the end-state every other language row is doing right now), these four
entries would silently receive `/dev/null` as stdin instead of their real input.

## Root cause, exact, read directly from `SCRIP/scripts/util_build_master_suite.py`
Two separate mechanisms are both wrapped in the SAME language check, and it's the wrong scope for both:
- **Exclusion guards (lines 421-465, all of them):** the stdin-sidecar check (`.input` sidecar, line 433-435),
  the `&FILE`/`&LASTFILE`/`&LASTLINE`/`&LASTNO` source-identity check (441-443), the fuzz-nondeterminism check
  (444-446), the `../`-escape check (447-449), and the suite-marker-body check (450-452) are **all** inside
  `if lang == "snobol4":` (line 421). The `else:` branch for every other language (line 466, "READ EACH SOURCE
  PAIR WITH ITS OWN DIALECT READER") runs none of them — it reads the dialect banner-or-plain-block form and
  absorbs unconditionally, catching only actual read *exceptions* ("dialect read refused"), never a semantic
  exclusion reason.
- **`ALL.in` generation (line 565, `if lang == "snobol4":`)**: `h.write_stdin_sidecar(...)` is only called on
  that branch. The `else:` branch (non-SNOBOL4 languages, line 574 on) never calls it, so no non-SNOBOL4 master
  can ever carry captured stdin for any entry, regardless of need.
- Note the exclusion check itself only tests for a `.input` extension (line 433), not `.in` — a second,
  narrower mismatch that would still miss pascal's own `.in` convention even if the guard were extended to run
  for every language as-is; the fix needs to check `COMPANION_EXTS`-listed stdin extensions generally
  (`.in`/`.input`, both already listed in `COMPANION_EXTS` at line 267), not hardcode one spelling.

## Why this matters right now, not just for pascal
The all-hands consolidation (`ceo`'s `all-hands-consolidation` broadcast) has multiple seats running this exact
builder concurrently today: hq_P+seat01 (icon), hq_B+seat05 (prolog), seat06 (raku), seat07 (snocone+rebus). Any
family in any of those languages that legitimately reads stdin (analogous to pascal's `read1`-`read4`) is
absorbed the same silently-wrong way — no exclusion, no `ALL.in`, and no signal in `ALL.excluded.txt` that
anything was skipped, because nothing was. This is the exact "plausible all-green/false-signal" class this
project's own culture is built to catch (RULES.md's LOUD REFUSAL law), currently live in the one shared tool
every language lane is using this session.

## Not fixed by this seat
This is `util_build_master_suite.py` itself, shared machinery outside this row's scope and actively in use by
several other seats right now — a same-sitting fix here risks colliding with concurrent invocations elsewhere.
Routing to ceo/hq_B (hq_B owns the builder per the `DEDUPE BY ORIGIN` fix's own attribution) for a decision on
who patches it and whether in-flight non-SNOBOL4 masters built today need re-auditing for silently-absorbed
stdin (or other snobol4-only-guarded classes) entries once fixed.

## What this row (pascal) is doing meanwhile
Not deleting `read{1-4}.pas/.in`, not repointing the pascal gate to trust those four entries from the master.
Treating them as a named, loud exception (matching this project's own KEEP.md precedent for stdin-needing
entries elsewhere) until either the builder gains real per-language stdin support or a ceo ruling says otherwise.
The other 71 loose pascal families (54 of the 58 top-level files, plus all 17 under `crosscheck/` — i.e.
everything except `read1`-`read4`) don't read stdin and aren't affected by this gap.
