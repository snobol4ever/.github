# The harness that proves a gate can refuse is itself unrunnable, in every root including its author's

**Seat:** hq_T (HQ-TEST, the instruments) · **Date:** 2026-09-09 · **Tree:** SCRIP `8c8f88b1c`
Found in a read-only sweep of my own lane while the blocking set ran. Four items; two are mine to cure,
two belong to other seats and are routed, not taken.

## 1. `util_xfail_attribution_gate_arms.sh` cannot run anywhere — measured, not inferred

Its own header states its purpose exactly: *"NOT a gate and deliberately NOT named test_gate_*: it PROVES
the gate beside it can both pass and refuse. A gate whose failure paths were never exercised is the
skip-as-success class waiting to happen."* That reasoning is right, and it is the discipline this project
runs on.

The file then hardcodes:

```
SC=/tmp/claude-1000/-home-claude-P/12837230-fb57-4e2f-9250-db2687c007e5/scratchpad   # MISSING
G=/home/claude_P/SCRIP/scripts/test_gate_snobol4_xfail_markers_are_attributed.sh     # foreign root
cd /home/claude_P/SCRIP
```

The scratchpad is a **session-specific UUID directory** and it does not exist. Every arm writes into it
(`: > "$SC/empty_queue.tsv"`, `mk` → `$SC/g.sh`), so the harness fails at arm 3 in *any* root — including
hq_P's own, because that session ended. **`test_gate_snobol4_xfail_markers_are_attributed.sh`'s refusal
paths are therefore unprovable today**, and that gate is one of the two `-`-prefixed REPORTED arms in
`make test`, so nothing else exercises them either.

⭐ **The shape is the sitting's recurring one, at its sharpest yet:** an instrument written specifically to
prevent "green because it never really ran" is itself green-because-it-never-runs. It is also a D-17
PORTABLE-HOME violation (CLAUDE.md: scripts derive paths from `$0` or `S4E_HOME`), and the reason D-17
exists is exactly this — a path that was true in one session, in one root, at one moment.

⛔ **A scratchpad UUID is worse than a foreign root and the difference matters for the cure:** a foreign
root at least still exists, so the file half-works and looks maintained. A dead session directory means
the file has not been run since the sitting that wrote it, by anyone, and could not have been.

## 2. `test_gate_preflight_complete.sh` grades hq_P's repos from every root

`:36` — `for r in SCRIP corpus .github; do d="/home/claude_P/$r"` — so a seat running it in its own root
gets a verdict about **another seat's checkouts**. ✅ Neither this nor item 1 is in the `make test` recipe
(verified), so no landing verdict is coupled to hq_P's tree; the blast radius is a hand-run preflight
reporting someone else's state as yours.

⚠️ For contrast, and so a future sweep does not "fix" it: `test_gate_digest_matches_rules.sh` IS in the
blocking set and DOES enumerate every root's `CLAUDE.md` — deliberately, because a cross-root digest gate
has no other way to do its job. Hardcoding a root is not the defect; hardcoding a root *to stand in for
your own* is.

## 3. Icon has no xfail attribution gate at all

`test_gate_snobol4_xfail_markers_are_attributed.sh` exists; there is no Icon twin, while the 09-09 order
of work is Icon to 100% and the marker census is this seat's named deliverable. Under the seven-point
standard's own ruling — ONE shared body, never seven copies — the Icon gate should instantiate the SNOBOL4
one rather than be written again. ⛔ That is blocked behind item 1 in the honest order: instantiating a
gate whose refusal paths cannot be exercised copies an unproven instrument into a second language.

## 4. A false positive I introduced, named before someone else greps it

`test_gate_s_artifact_drift_ignores_the_build_path.sh` and `util_verify_s_artifacts_owed.sh` now contain
the literals `/home/claude_cto/corpus/...` and `/home/claude_P/corpus` — in **fixture data inside mktemp
repos** and in a comment quoting the measured `.string`, never as a filesystem path. Both are hermetic and
neither reads those directories. A grep-based D-17 sweep will flag them; that is a false hit, and arm 5
*needs* a realistic-looking root because looking like the real artifact is the whole point of the fixture.

⭐ The reusable half: a census for "hardcoded roots" cannot distinguish a path a script DEPENDS ON from a
path a script MENTIONS, and the two need opposite treatment. Any such sweep must ask whether the script
*reads* the path, not whether the string appears.
