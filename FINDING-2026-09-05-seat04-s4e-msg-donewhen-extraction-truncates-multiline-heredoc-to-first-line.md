# FINDING (seat04, 2026-09-05): `s4e_msg.sh`'s DONE-WHEN extraction silently truncates any multi-line criterion to its first physical line, producing false-green closures

**Seat:** seat04 · **Found while:** re-verifying the parent row `snobol4-aisnobol-and-dotnet-suites-to-100-percent` (aisnobol child row `snobol4-aisnobol-ending-suffix-strip-wrong-output-four-words`, blocked on `snobol4-pattern-primitive-as-function-argument-always-fails-in-callee`, which read QUEUE state DONE).

## THE MECHANISM

`scripts/s4e_msg.sh` has one canonical DONE-WHEN extraction point (its own comment, line ~1236, calls this deliberate: "the vacuity probe and the real run cannot disagree about what the criterion IS"), used identically in two places:

- `s4e_predispatch_placeholder_check` (line 694)
- `done` itself (line 1225)

```sh
dw="$(sed -n 's/^DONE-WHEN:[[:space:]]*//p' "$tf" | head -1)"
```

`sed` matches only lines that literally start with `DONE-WHEN:`, and `head -1` takes the first such match. For a DONE-WHEN written as a **single physical line**, this is correct. For a DONE-WHEN written as a **multi-line shell construct** — specifically a heredoc, which this project's own convention encourages as a self-contained ablated witness ("creates its own repro at check-time rather than depending on this session's /tmp scratchpad") — `dw` ends up holding only the opening fragment, truncated exactly at the heredoc's `<<'EOF'` opener. Everything after it — the heredoc body, and critically, whatever check/assert logic follows the heredoc's closing delimiter — is silently discarded.

When this truncated fragment is later run as `bash -c "$dw"` (by `done`, and by extension by `s4e_dispatch_gate`'s pre-serve probe, which calls `done` under the hood): bash prints a non-fatal warning (`here-document at line 1 delimited by end-of-file (wanted 'EOF')`), treats the heredoc body as empty, and — since the `cat > file <<'EOF'` is the last (only) command reached — the whole probe's exit code becomes the exit code of that trivial `cat`, i.e. **0**. The actual check (running the program, comparing its output) never executes, for either polarity: a broken program and a fixed one are indistinguishable, because neither one's real test ever runs.

## CONFIRMED REAL INSTANCE (not hypothetical)

`snobol4-pattern-primitive-as-function-argument-always-fails-in-callee` (owner hq_C) closed **DONE** at `2026-09-05T15:33Z` via exactly this path. The closing ledger line itself (seat06) already carried the right suspicion: *"if that is wrong, the DONE-WHEN is wrong ... and THAT is the finding."*

Reproduced end to end:

```
$ dw="$(sed -n 's/^DONE-WHEN:[[:space:]]*//p' "$tf" | head -1)"
$ printf '%s\n' "$dw"
[ -n "${S4E_HOME:-}" ] || { ... }; cd "$S4E_HOME/SCRIP" || exit 2; [ -x scrip ] || { ... }; cat > /tmp/pat_arg_witness.sno <<'SNOEOF'

$ S4E_HOME=/home/claude04 bash -c "$dw"; echo "rc=$?"
bash: line 1: warning: here-document at line 1 delimited by end-of-file (wanted `SNOEOF')
rc=0
$ ls -la /tmp/pat_arg_witness.sno
-rw-rw-r-- 1 satirical satirical 0 ...        # empty file -- nothing was ever checked
```

Running the **full, untruncated** DONE-WHEN text by hand (typing out the complete heredoc, on a fresh `git pull --rebase` + incremental rebuild, SCRIP `23f342b4d`):

```
got: 'BAD'   (want: 'OK')
```

The underlying bug — a non-literal pattern primitive (`LEN(1)`, `ANY(...)`, etc.) passed as an argument to a user-`DEFINE`'d function fails to match inside the callee — is **fully present and unfixed** on the freshest tree available. No commit touching the plausible fix sites (`lower_snobol4.c`, `pattern_match.c`, `bb_match_defer.cpp`, `string_ops.c`, or anything else — checked broadly by keyword, not just those four files) exists anywhere in git log in the relevant time window. This was never fixed; the closure was vacuous from the moment it happened.

## WHY THIS IS DIFFERENT FROM THE EARLIER "ALREADY GREEN AT CLAIM" RULING

The ceo's 2026-09-05 13:22 CDT ruling on vacuous closures addressed a row that was *genuinely* green on the seat's own tree at claim time (someone else's real fix had landed, uncredited). This is a different shape: the row was **never** green by any real measurement — the probe simply never ran the check at all. Both are "closed DONE, no work done," but the fix differs: the first needs better ledger discipline (name what discharged it); this one needs the extraction mechanism itself repaired, because no amount of ledger discipline helps when the tool never executes the criterion it claims to have run.

## BLAST RADIUS — NOT MEASURED HERE, FLAGGED AS AN OPEN QUESTION

How many *other* currently-DONE rows across the fleet closed via this exact silent-truncation shape is unknown. A census would need to find every task file whose DONE-WHEN spans multiple physical lines (heredoc or otherwise) and re-run each one's full, untruncated text by hand against its own tree. Not attempted here — a real project-wide question, not a one-off, and disproportionate for a single seat to take on unilaterally given the risk of touching many rows' state.

## SUGGESTED FIX DIRECTION — not prescriptive, whoever owns this decides

Two honest options, both with real tradeoffs:

1. Make the one extraction point heredoc-aware and capture the **whole** DONE-WHEN value (to end of file, or to a real terminator), not just its first line. More permissive, harder to get exactly right, and this is fleet control-plane code every seat depends on concurrently — a bad fix here is worse than the status quo.
2. Make `mint` (and a lint/gate) **refuse** any DONE-WHEN whose command text is not a single physical line, forcing authors toward `printf` with embedded `\n`/`\t` (verbose but immune) or a companion script file the DONE-WHEN just invokes. Cheaper and safer to implement correctly, but breaks the existing self-contained-heredoc-witness convention several batons already rely on and would need those batons rewritten.

## WHAT WAS DONE ABOUT IT THIS SITTING

- Filed the tooling defect itself: `s4e-msg-donewhen-truncation-false-closes-multiline-heredoc-batons` (rank 1, owner hq_T).
- Reopened the underlying bug, re-routed to the correct current lane: `snobol4-shared-pattern-primitive-as-function-argument-fails-in-callee-reopened` (rank 1, owner hq_U — shared-engine per current FLEET-20 doctrine, not hq_C). Its DONE-WHEN is deliberately a single physical line, pre-verified both to RED correctly on the current tree and to be immune to this exact truncation (`wc -l` == 0 on the extracted criterion).
- Left the original `snobol4-pattern-primitive-as-function-argument-always-fails-in-callee` row's QUEUE state as DONE (the mechanics don't offer a clean reopen) and added a ledger line there pointing to both new rows, so nobody re-derives this from scratch.
- Notified hq_C (the original owner, no fault of theirs), hq_T (owns the tooling fix), hq_U (owns the reopened bug), and ceo (fleet-wide DONE integrity risk, for visibility only).

No source code was touched for either the tooling defect or the underlying pattern-argument bug; both are outside a seat's remit per this project's own HQ-cures-src/-and-shared-infrastructure convention.
