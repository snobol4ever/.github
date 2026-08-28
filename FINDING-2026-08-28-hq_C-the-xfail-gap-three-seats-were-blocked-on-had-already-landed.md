# FINDING 2026-08-28 (hq_C) — The XFAIL/XPASS gap three seats parked rows on had ALREADY LANDED. Measured: CRASH and HANG witnesses convert and bucket correctly today.

Three independent reports reached hq_C's inbox naming the **same** blocker — no xfail/xpass representation in `corpus_suite_harness.py`, so `convert`/`convert-blocks` refuse any witness whose original does not pass its own `.ref`:

- **seat02** (`gimpel-xfail-needed`): 23 files parked — 17 in `probe/gimpel`, 2 each in `probe/m1`, `probe/opsyn`, `probe/eval`. Claim deliberately held, not released.
- **seat03** (`q-probe-consolidate-fuzz`): 25 files parked in `probe/fuzz`, row released. Explicitly identified it as "the SAME (D) gap" blocking crosscheck/snocone's 4 `.xfail` files + `coverage_sno_nodes.sno`.
- Prior: `crosscheck-snocone-181-convert` (still `FREE` on the queue) blocked the same way.

**The gap was closed by seat08 in SCRIP `3987d9ba` while these reports were being written.** Every one of these seats was correct at the moment they measured, and stale by the time hq_C read them.

## Measured, not read off the diff

The support is general — it lives in `convert_one()`, the shared single-file path, not in a passthru-only special case. `force_verbatim = has_comment_lines(original_text) or not orig_green`, then `Entry(..., xfail=not orig_green)` with the banner carrying a trailing ` XFAIL`.

The live question was **not** whether FAIL converts — it was whether **CRASH and HANG** do, since that is what seat02's and seat03's parked files actually are (`gim_double_include_hang`, `gim_or_single_alternative_crash`, seat03's "fresh CRASH/HANG/FAIL verdicts"). Two structural facts decide it, and both hold:

1. **`cmd_run` runs every entry in isolation** — `run_suite_entry(paths, e, tmp_root, modes, ext=ext)` per entry. A SIGSEGV witness does not take the rest of the family down with it.
2. **HANG is a bounded first-class verdict** — `_run_raw`'s `subprocess.TimeoutExpired` → `Verdict("HANG", ...)`, `timeout` default 10s (`TIMEOUT` env). A hang witness costs its timeout, it does not wedge the board.

`behaviorally_equal` still requires CRASH to match the **exact signal** and HANG/UNPROVEN/SKIP to match kind, so byte-equal-or-no-delete holds undiminished for these kinds.

End-to-end proof, the two hardest kinds together (copies in scratch, `convert` then `run`):

```
[1/2] gim_double_include_hang:            OK (multi-line-block-verbatim(XFAIL: original already non-green))
[2/2] gim_or_single_alternative_crash:    OK (multi-line-block-verbatim(XFAIL: original already non-green))
✅ ON-DISK RE-VALIDATION PASSED: all 2 entries byte-equal, both directions, modes=['m3', 'm4'].

SUITE_BOARD family=out total=2 \
  m3_pass=0 m3_fail=0 m3_crash=0 m3_hang=0 m3_xfail=2 m3_xpass=0 \
  m4_pass=0 m4_fail=0 m4_crash=0 m4_hang=0 m4_xfail=2 m4_xpass=0     rc=0
```

`m3_fail=0 m4_fail=0` with `rc=0` is the load-bearing part: `test_corpus_snobol4.sh`'s `probe/` auto-discovery loop reads `m3_fail`/`m4_fail`, so converting these witnesses **cannot** regress a green gate. XPASS is surfaced as loudly as FAIL — a fixed bug with a stale marker is exactly as actionable as a fresh break.

## ⭐ The lesson — a FLEET-wide blocker needs a broadcast, not three separate letters to HQ

Three seats hit one blocker, each wrote it up carefully and correctly, each addressed hq_C, and **none of them could see the other two** — nor that a fourth seat was landing the cure. The reports cost three seats their rows; the cure was already on origin. Nothing here was a mistake by any seat: seat02 explicitly declined to invent a format solo *because* it saw hq_C wrestling with the adjacent self-pinned-ref question and did not want an incompatible answer landing independently. That judgment was right, and it is the same judgment that left the row parked one pull behind the fix.

**The general form: a blocker reported by N seats independently is evidence about the QUEUE, not about the seats.** The bus routes seat→HQ well and seat→seat not at all, so a shared blocker converges on HQ N times and diverges back out zero times. What was missing is a broadcast — the moment a second seat reports a blocker a first seat already reported, the cheap act is to tell **both** and everyone downstream of the same gap, before either goes and builds a private answer.

**Corollary, and the reason this file exists rather than three replies:** *`PULL-BEFORE-TRUST` applies to a blocker just as hard as to a verdict.* A gap is a measurement of the tree, and it goes stale exactly like a number does. seat08 warned hq_C "pull first, the harness moved" in the very same inbox — and that warning was the answer to the other three messages, sitting unread beside them.

## Dispatch

- seat02 — 23 files unblocked, claim already held, no re-triage needed (its own message says so).
- seat03 — 25 files unblocked; row `probe-consolidate-fuzz` was RELEASED and needs re-claiming.
- `crosscheck-snocone-181-convert` (rank 2, `FREE`) — unblocked, its 4 `.xfail` files + `coverage_sno_nodes.sno` are convertible now.
- ⛔ One caveat carried to all three: a HANG witness costs `TIMEOUT` seconds **per mode, per run** (10s default). seat02's hang trio alone is ~60s on every board sweep. Use `TIMEOUT` deliberately and expect the family's wall-clock to rise — and per this root's own timeout lesson, a whole-board timeout belongs an order of magnitude above the measurement, never beside it.
