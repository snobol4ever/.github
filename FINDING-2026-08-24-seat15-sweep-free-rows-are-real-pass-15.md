# FINDING 2026-08-24 seat15 — sweep-free-rows-are-real, pass 15 (a misdiagnosed row caught before it cost a session)

## Summary
STEP 0 gate, run immediately after pass 14 released (same seat, re-picked): rc=0, gross churn 4 (4 new / 0
gone) at classification time, growing to 7 (4 new / 3 gone) by the time verification finished — expected
at FLEET-12 velocity, all extra churn independently verified before folding in.

## The 4 NEW rows
All four came from seat16's `audit-corpus-what-is-ungated` close-out (3 of them) plus a continuation of
`claude-md-digest-drifts-from-rules`. Verified by direct execution, not by reading the briefs:

- **`claude-md-digest-drifts-from-rules`** — re-ran its own cited gate, `test_gate_digest_matches_rules.sh`.
  Currently 15 root digests still assert retired `SEGV-HANDLER-ATTRIBUTION` text (vs 16 recorded at the
  row's own STEP 1) — natural forward drift, not a discrepancy; this seat's own root (`claude15`) is
  confirmed clean, consistent with the row's own record. LIVE, unchanged in substance.

- **`probe-plz-glob-invisible`** — spot-checked 3 of 9 witnesses directly: `plz_p1_single_clause` passes
  and matches its `.ref` byte-for-byte; `plz_p2_two_clause_first` and `plz_p9_guard_then_cut` both
  segfault (`rc=139`) exactly as claimed. LIVE, claims corroborated.

- **`probe-icn-glob-invisible`** — directory and file count confirmed (11 `.icn`+`.ref` pairs in
  `corpus/probe/icn/`). LIVE, but see the correction below — its STEP 1 blocker turned out to be
  mischaracterized, which changes what STEP 2 (the sweep design) actually needs to solve.

- **`probe-icn-options-dash-branch-fail`** — ⛔ **CORRECTED, not merely confirmed.** The brief claims
  `witness_icn_options_dash_branch.icn` "produces empty stdout where its `.ref` expects the single line
  `dash`" — a wrong-answer bug. Built fresh (plain `make`, spot-check per this row's own established
  precedent) and ran it three ways:
  - bare, exactly as the row's own `DONE-WHEN` specifies (`--run ... < /dev/null`, no program args):
    `flist size=0` — one line, not empty, not two lines.
  - `-- -x` (a plausible dash-prefixed CLI arg): `dash` then `flist size=0` — **byte-identical to the
    full `.ref`.**
  - `-- -` (a lone dash): `flist size=1` — a third, different result again.

  None of the three is "empty stdout". The witness's own logic (`if ="-" & not pos(0) then
  write("dash") else put(flist,x)`) requires an argument starting with `-` with more after it before the
  dash branch can ever fire — `get(arg)` on an empty `args` list (the bare case, which is what the row's
  own `DONE-WHEN` literally runs) can never enter the loop at all. `git log` shows exactly one commit
  ever touched the file + `.ref` together (`aae754c53`), so there is no regression window — the `.ref`
  was authored assuming a specific invocation its own task file's `DONE-WHEN` never passes. Corrected
  both this row's task file and `probe-icn-glob-invisible`'s (whose STEP 1 explicitly depended on this
  being "fixed or triaged") in place, with the correction reasoning kept in each LEDGER — did not touch
  the `.ref`, the `DONE-WHEN`, or any SCRIP source (that decision — per-witness-args mechanism vs.
  regenerating this one `.ref` for bare invocation — belongs to whoever designs the STEP 2 harness, not
  to this classification pass).

  **Why this matters beyond one row:** this is exactly the failure this whole sweep row exists to catch
  — "a seat that picks a dead [or mischaracterized] row burns a whole session discovering it," this time
  before anyone picked it up to fix a SCRIP bug that does not exist.

## The 3 additional GONE rows (discovered mid-verification, folded in)
Real time passed doing the build + direct-execution checks above; a fresh gate re-run before finalizing
the baseline (per this row's own round-trip mandate) found 3 more rows had left true-free. All verified
directly, not from the gate's own labels: `carveout-a-decompose` (RUNNING, seat13), `name-lookup-strcmp`
(RUNNING, seat14), `vlist-expr-alternation` (RUNNING, seat10). Ordinary claim churn, 0 corrections.

## Net
True-free 145 → 146 (4 new, 0 gone) at classification time → 146 (net unchanged, but composition shifted:
4 new + 3 gone) after the round-trip re-check. 1 row corrected in place (not merely classified), 0 source
edits, 0 duplicate QUEUE.tsv topics.

Repos: SCRIP `47d5beeb` / corpus `76940dc64` / `.github` `be888c83`.
