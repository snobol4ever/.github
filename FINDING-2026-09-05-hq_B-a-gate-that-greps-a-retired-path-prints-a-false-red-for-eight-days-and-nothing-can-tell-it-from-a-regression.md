# FINDING 2026-09-05 (hq_B) — a gate that greps a retired path prints a FALSE RED for eight days, and nothing can tell it from a regression

**Measured, not argued.** `scripts/test_gate_icn_scan.sh` and `scripts/test_gate_icn_var.sh` both asked
`grep -rq IR_SCAN_* "$ROOT/src/contracts/"`. That directory has not existed since the 2026-08-28 reorg — the
spine types live in `src/ir/`. `grep -r` over a missing directory returns non-zero, so both fences printed
**FAIL** on every run from 2026-08-28 to 2026-09-05: eleven false reds in the scan fence, two in the var fence,
each in a verdict line indistinguishable from a real regression. Repointed to `src/ir/` in SCRIP `001e5faff`;
both then PASS on their own populations (scan 86 probes, var 331 probes, three modes each).

## The part that cost time, and would have cost more

I hit these reds **immediately after landing an Icon parser change**, while running the fence set as my own
landing arms. The honest reading of a red at that moment is *"I broke it"*, and the cheap next step is a
stash-and-rebuild bisect of my own cure. What actually saved the time was reading the gate's own output text
rather than its verdict: the failing lines named a path, and the path was one this root's digest already records
as retired. **A red that has always been red is indistinguishable from a red you just caused** — that is what
makes a stale instrument expensive rather than merely wrong.

## The general rule, which is the transferable half

⭐ **An instrument that cannot find its population does not report an empty population — it reports a failure.**
This is the same shape as three defects already recorded in this org, and the recurrence is the point:

| instrument | question you think you asked | question it answered |
|---|---|---|
| `command -v icont` | does the Icon oracle exist | is it on `PATH` (it is not; it is under `/home/resources`) |
| `$?` after a pipeline | did my command succeed | did `head`/`tail` succeed |
| `find corpus/crosscheck -name '*.sno'` | is the tree gone | prints nothing, exits 0 — reads as *present and empty* |
| `grep -r X src/contracts/` | is X declared | **could I read that directory at all** |

Every one of them answers a narrower question than the reader believes, and **none of them says so**. Two
instances of the family bit me again inside this same session: `echo rc=$?` after piping `strip_comments.py`
through `tail` reported the pager's status, and a `cd` left over from a previous command sent a `python3` edit
at a path that did not exist — caught only because the traceback was louder than a wrong answer would have been.

## The cure that generalises

Repointing the path fixes today. What fixes the class is the guard both gates now carry:

```sh
[ -d "$ROOT/src/ir" ] || { echo "⛔ GATE REFUSES (rc=2): $ROOT/src/ir does not exist -- cannot measure"; exit 2; }
```

⛔ **A check whose subject is missing must REFUSE (rc=2), never FAIL (rc=1).** RULES.md already says a test that
cannot measure refuses; the missing half is that *a grep over a path is a measurement, and its subject can go
away without the grep noticing*. The next rename will now say "I cannot measure" instead of manufacturing a
failure — and, unlike a red, a refusal cannot be mistaken for someone's regression.

## Where else to look

Any gate that greps a **path** rather than a **symbol** is a candidate. `src/contracts/` and `src/machine/` are
retired; `src/parser/` and `src/frontend/` are both retired names for `src/parsers/`; `corpus/crosscheck/`,
`corpus/probe/` and `corpus/generated/` are gone. A sweep of `scripts/` for hard-coded `src/…` and `corpus/…`
paths, each asked whether its subject still exists, is a bounded instrument row — and every hit is either a live
false red or a future one.
