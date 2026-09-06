# FINDING — built the NAME.fixtures/ + NAME.rc sidecars and minted 3 new LIVE refs with them; found and
# fixed two live, pre-existing bugs while doing it (one of them a silently-disabled correctness guard that
# reproduced the exact near-miss its own comment already warned about); named a new structural gap
# (binary output is not comparison-safe under this harness) rather than hack around it for a 4th program.

**seat07 · 2026-09-06 · row `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class`**
(own row's STILL-OWED item (c): fixture-file harness extension for filecnvt/gediff/huffstuf/iiencode).
SCRIP `9935786a4`, corpus `7add6b797`.

## ⛔⛔ Bug 1 (severe): the UNGRADABLE-ruling guard was dead on every ordinary run, and reproduced its own predicted incident

`util_cut_icon_ipl_refs.sh` defined `UNGRADABLE_TSV` and `is_ruled_ungradable()` **inside** the
`if [ "$MAINS_ONLY" -eq 1 ]` branch. Every normal invocation of this script — including every prior
`--apply` this whole row's history, since `--mains-only` is a rare, separate flag for a different
purpose — takes the `else` branch, so those two definitions never execute. The call site further down
(`if is_ruled_ungradable "$f"; then …`) then hits bash's own "command not found" (exit 127), which is
falsy in an `if` with no `set -e` to catch it, so **every UNGRADABLE-ruled program was silently treated as
unruled** on every ordinary run since this guard was added (hq_I, 2026-09-06, same day).

Measured directly: `gcomp.icn` — ruled UNGRADABLE because `gcomp.icn:41` reads `echo * .*` through a pipe,
i.e. its own output **is a directory listing of `progs/`** — re-minted the instant this session added its
four new `NAME.fixtures/` directories, which is *exactly* the incident the guard's own comment already
named as the reason it exists ("the next fixture anyone authors would have broken it"). The guard existed,
in text, and did not run.

Fix: moved both definitions above the `if`, so they execute unconditionally regardless of which branch
runs (`util_cut_icon_ipl_refs.sh`, this session). Reverted the one bad mint it produced
(`progs/gcomp.std`, deleted — it was never committed, born and killed within this sitting). Audited the
full tracked history for prior damage: **zero** other UNGRADABLE-ruled program has a committed `.std` —
this was a first-time, self-contained incident, not a backlog of bad refs. `duplfile.icn` (not
UNGRADABLE-ruled) minted the same run via the pre-existing argv sidecar and is a legitimate, unrelated
addition.

## Bug 2 (minor, same mechanism as Bug 1's warning): `ipl_isolation_verify_clean` false-alarmed on its own sidecars

Both copies of this check (the shared `ipl_isolation_verify_clean()` in `lib_icon_ipl_isolation.sh`, and
`util_cut_icon_ipl_refs.sh`'s own un-consolidated duplicate — a second instance of the "two copies of one
convention" shape this lane has already named once for test_prolog_ladder.sh/its Raku twin) excluded only
`\.std$` from "the tree changed" detection. `.dat` (2026-09-05) and `.argv` (2026-09-06) sidecars were
already normal, legitimate additions under `progs/` by the time this session started, and any of them
sitting uncommitted — mine or anyone's — triggered a false `⛔⛔⛔ THE TRACKED IPL TREE CHANGED` alarm with
zero actual breach. Fixed in both copies: the exclusion is now `\.std$|\.dat$|\.argv$|\.rc$|\.fixtures/`.
Not consolidated into one shared call this session (real, separate, lower-priority cleanup — the two
copies now at least agree byte-for-byte).

## The fixture-file sidecar: `NAME.fixtures/` + `NAME.rc`

`NAME.dat` supplies stdin content and `NAME.argv` supplies argument *values*, but four programs need an
argument that names a **real file on disk**: `gediff.icn` diffs two file arguments (spawns the system
`diff` via a pipe), `filecnvt.icn`/`huffstuf.icn`/`iiencode.icn` each read a named input file directly.
Neither existing sidecar can place a file into the isolated run directory. New convention: `NAME.fixtures/`
beside `NAME.icn`, holding one regular file per fixture, staged into the run directory verbatim by its own
filename; `NAME.argv` then names that same filename. One shared reader, `ipl_fixtures_stage()` in
`lib_icon_ipl_isolation.sh`, called by both the cutter's `run_isolated()` and the shared
`ipl_isolation_run()` (via a new `IPL_ISO_FIXTURES` env-var toggle, same shape as the existing
`IPL_ISO_SUBDIR`) — so a program's minted ref and its later grading can never disagree about which files
were present.

Separately, `gediff.icn`'s correct, designed behavior is `exit(close(p))` propagating the system `diff`'s
own rc — `rc=1` ("files differ") for two genuinely different fixtures, not a failure. Every rc!=0 not
already claimed by a named class fell straight to `ORACLE_FAIL` before this session, so a legitimately
nonzero-rc program could never mint. New `NAME.rc` sidecar (one integer, the expected exit code) changes
that one comparison from a hardcoded `0` to a declared value defaulting to `0` — **byte-for-byte unchanged
behavior for every program without one**. Also fixed the minute-crossing confirmation pass, which
independently hardcoded `rc2 -ne 0` in a *second* place — would have wrongly rejected `gediff` as
nondeterministic in its own second pass even after the first fix.

## Three programs verified and minted

All three read their source first, then verified directly against the real oracle (not the prior session's
`UNGRADED.tsv` claims, which turned out right for these three but wrong for the fourth — see below):

- `filecnvt.icn fixture.txt -` → real line-terminator-conversion output, rc=0.
- `gediff.icn fixture_a.txt fixture_b.txt` (+ `NAME.rc=1`) → real reformatted diff report
  (`fixture_a.txt:2` / `fixture_b.txt:2` / `< banana` / `---` / `> blueberry`), rc=1.
- `iiencode.icn fixture.txt` → real uuencode-style output (`begin 644 fixture.txt` … `end`), rc=0.

All three confirmed by the harness's own 4-run + minute-crossing determinism check, minted via
`--apply`, and confirmed **RUN_PASS in both modes** against SCRIP (`test_icon_ipl_suite.sh`, post-rebuild
— the stale-binary refusal fired first; `make pristine` per `RULES.md:118`, clean). `UNGRADED.tsv` loses
the four now-resolved rows (`filecnvt`, `gediff`, `iiencode`, plus `duplfile` which minted independently
this run) — population/inventory bucket math depends on this, and did in fact refuse (`delta -4`) until
the rows were removed.

## huffstuf.icn: recipe verified correct, minting blocked on a NEW structural gap, not attempted

`huffstuf -o fixture.txt` (`-o`/`-i` are backwards from the obvious reading — `-o` is *encode*) **does**
produce real, correct output against the real oracle: rc=0, genuine Huffman-compressed bytes, reproduced
identically both by hand and through the real harness path with the fixture properly staged. But that
output is **binary** — it contains NUL bytes — and this entire harness (both the cutter's classification
and the grader's comparison) moves output through bash string variables: `out1="$(cat "$OUT1")"`,
`[ "$out1" = "$out2" ]`, `grep` pattern checks. Bash string handling is not NUL-safe. The real, correct
125–429-byte compressed output was misclassified `ALL_ORACLE_DIAGNOSTIC` ("every non-blank line is the
oracle talking about the program") purely by coincidence of where embedded `0x0A`/`0x00` bytes fell — not
because anything is wrong with the program, the argv, or the fixture.

This is a new structural gap, parallel in shape to the already-named file-output-not-stdout gap
(`versum.icn`/`iidecode.icn`/`iplweb.icn`): it needs a design decision (binary-safe `cmp`-based comparison
threaded through the cutter's classification *and* the grader's diff, likely nontrivial given how much of
both scripts' logic is regex/string-shaped) or a ruling that binary-output programs are UNGRADABLE under
this harness — not a per-file hack under time pressure. `huffstuf`'s own sidecars (`.argv`, `.fixtures/`)
are committed anyway: the *recipe* is verified correct and worth keeping so whoever resolves the harness
gap doesn't have to re-derive it. `UNGRADED.tsv`'s row is corrected in place (the prior "VERIFIED
LIVE-CAPABLE, not yet minted" claim understated the real blocker) rather than removed.

## Addendum: `iiencode.icn` converged onto the pre-existing bare-fixture-file convention

Pushing this session's mints hit a real add/add conflict: hq_I (or another concurrent session) had
independently minted `iiencode.icn` too, via a DIFFERENT, older, already-established convention this
session didn't know about until the conflict surfaced it -- a bare `NAME.in`-named file committed directly
into `progs/` (no subdirectory), relying on the fact that `ipl_isolation_init`'s template copy already
copies the whole `progs/` directory wholesale, so a bare fixture file rides along for free with zero new
plumbing. `rcat.argv`/`rcat.in` and `cstrings.argv`/`cstrings.in` (both pre-dating this session) confirm
this is a real, repeated pattern, not a one-off. Resolved by taking the existing convention for `iiencode`
(`iiencode.in` + `hello.txt`, both already committed) and dropping this session's own
`iiencode.fixtures/fixture.txt`, rather than forcing a second competing convention for one program.
`filecnvt`/`gediff`/`huffstuf` were NOT migrated off `NAME.fixtures/` this sitting (time-boxed) -- the
package now genuinely carries TWO conventions for the same problem, which is exactly the "two-bodies-
drift" shape this lane has already named and cured twice elsewhere (the Prolog/Raku ladder pair, the two
`.dat` copies). Flagged as real, unglamorous follow-up: reconcile onto ONE convention (the bare-file form
is simpler and has more precedent; `NAME.fixtures/` avoids mixing synthetic content into the vendored
directory listing -- a real tradeoff for whoever picks it up, not an obvious call either way).

## Board after this session

SCRIP `9935786a4` (harness + two bug fixes), corpus `7add6b797` (mints + UNGRADED.tsv). RUN population
75 (was 64): `m3 RUN_PASS=42 RUN_FAIL=21 RUN_CRASH=10 RUN_HANG=2`, `m4 RUN_PASS=42 RUN_FAIL=28 RUN_CRASH=3
RUN_HANG=2`. Crash/hang names unchanged from prior sessions' record (already-known classes, not new).
SCORE.md lands on the post-commit re-run (CEO-174: no row against an uncommitted tree).
