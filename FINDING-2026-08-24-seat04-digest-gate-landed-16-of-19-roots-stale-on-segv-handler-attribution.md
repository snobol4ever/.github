# FINDING — `claude-md-digest-drifts-from-rules`: the gate is landed, and it immediately caught 16 of 19 roots stale on a same-day correction

**Seat:** seat04 · **Date:** 2026-08-24 (s272) · **Mode:** FLEET-12 (MODE file at session start)
**Trees:** SCRIP `47d5beeb` (gate script landed+pushed) / `.github` `e813bb4c` (pre-this-commit) — corpus untouched by this row.
**Row:** `claude-md-digest-drifts-from-rules` (rank 1) · **Prior:** minted 2026-08-23 by hq_P from seat11's find (`FINDING-2026-08-23-hq_P-the-per-root-claude-md-digest-is-not-git-tracked-and-15-of-19-were-stale.md`)

---

## HEADLINE

Built `SCRIP/scripts/test_gate_digest_matches_rules.sh` — the structural gate this row exists to produce: for a seeded, extensible table of FACT RULEs that RETIRED an earlier text, it checks every one of the 19 sibling-root `CLAUDE.md` digests for that retired text asserted **without** a nearby corrective signal. Read-only, three-exit-code (`lib_gate.sh`), negative-tested on all three arms.

It immediately found something real, not just a working mechanism: **16 of 19 roots still assert `CSN_NO_SEGV_HANDLER`/`SCRIP_NO_SEGV_HANDLER` as SCRIP's own clean-backtrace hooks** — the exact claim `.github/RULES.md`'s ASM-DIFF-FIRST section retracted **the same day** (`CORRECTED 2026-08-24`, ~line 47: neither var has a `getenv` reader anywhere under `SCRIP/src`; `CSN_NO_SEGV_HANDLER` belongs to the separate, externally-cloned csnobol4 oracle). This reads like the same class the FINDING that minted this row already named for the `-O2` text — a correction landed in `RULES.md` with no fleet-wide telegram (RULES.md ~line 168) yet reaching it.

Per this row's own NEXT step 2 (read-only by default — hq_P's s267 bulk cross-seat edit was correctly blocked by the permission classifier), **this FINDING reports; it does not fix the other 18 roots.**

---

## 1. THE GATE

`bash SCRIP/scripts/test_gate_digest_matches_rules.sh` — sources `lib_gate.sh` for the standard three exit codes:

```
0  CLEAN      -- every examined root is clear of every table entry's retired text (or correctly caveats it)
1  VIOLATION  -- N roots carry a retired-text hit with no corrective signal nearby
2  UNPROVEN   -- a root's CLAUDE.md could not be read; never silently skipped
```

**Method:** for each table entry (`rule_id`, retired-text `grep -E` pattern, corrective-signal `grep -E` pattern, citation into `RULES.md`), grep every root's `CLAUDE.md` for the retired pattern; for every hit, check a ±2-line window for a corrective signal (`retired`, `superseded`, `corrected`, `not SCRIP`, `csnobol4`, …). A hit **with** a nearby signal is a seat correctly explaining dead text (RULES.md itself does exactly this at ~line 149, quoting a retired sentence once "so a reader who remembers it knows it was retired on purpose") and is not counted. A hit with **no** signal nearby is counted as a violation and printed with file, line, the offending text, and a citation.

**Honest limitation, stated in the script's own header:** this is a substring/proximity heuristic, not comprehension. It can miss a differently-worded stale claim, and a corrective-signal word could in principle appear near a real violation by coincidence and wrongly excuse it. It is read-only and exists to hand a human (or the owning seat) a short, actionable list — it does not adjudicate anything by itself.

Table seeded with two entries this session (extending it is one more `check_rule` call):

| rule_id | retired text | citation |
|---|---|---|
| `NO-O2-EVER` | `-O2 is used ONLY for benchmark/demo runs, passed explicitly` | RULES.md FACT RULE "NO `-O2` BUILDS. EVER." (~line 148-149) |
| `SEGV-HANDLER-ATTRIBUTION` | `CSN_NO_SEGV_HANDLER`/`SCRIP_NO_SEGV_HANDLER` cited as a SCRIP hook | RULES.md ASM-DIFF-FIRST correction, landed 2026-08-24 (~line 47) |

Not every FACT RULE has a quotable retired predecessor — most state a fresh constraint rather than retiring old text — so the table is seeded with the rules that do, not a mechanical one-per-bullet transcription.

---

## 2. VALIDATION — the corrective-signal filter is load-bearing, not decorative

Measured against the **real** 19 roots before trusting the design: a naive grep-only version of the `NO-O2-EVER` pattern raised **3** raw hits (`claude13`, `claude14`, `claude15`). Read in full context, all three are the *opposite* of a violation — each is a seat that already self-corrected, quoting the retired sentence explicitly to explain it is dead:

> `/home/claude15/CLAUDE.md:62` — *"The old sentence this paragraph carried — "`-O2` is used ONLY for benchmark/demo runs, passed explicitly" — is DEAD; do not follow it if you recall it from a prior session."*

A grep-only gate would have reported all three as false positives on its very first real run. The corrective-signal window is what tells these apart from `claude07`/`claude_C`'s genuine, uncorrected `SEGV-HANDLER-ATTRIBUTION` hits (§3) — same shape of hit, opposite verdict, and the difference is exactly the nearby retraction language.

**All three `lib_gate.sh` exit arms negative-tested by injection** against disposable scratch files (`DIGEST_GATE_ROOTS` env override — never pointed at a real root):

- Three synthetic clean roots (no mention / O2-with-correction / SEGV-with-correction) → `GATE PASS(0)`, 0 violations, examined 6.
- One synthetic root with the O2 sentence and no correction, one with the SEGV claim and no correction → `GATE FAIL(1)`, exactly 2 violations, both correctly identified by rule_id, file and line.
- One nonexistent root path → `GATE UNPROVEN(2)`, refused before counting anything.

---

## 3. THE LIVE FINDING — 16 of 19 roots, real and current

Real invocation, `bash SCRIP/scripts/test_gate_digest_matches_rules.sh` against the actual 19 sibling roots: **`GATE FAIL(1)`, 16 violations, examined 38** (19 roots × 2 rules). All 16 are the same `SEGV-HANDLER-ATTRIBUTION` hit, all missing a corrective signal:

> *"Clean backtraces via `CSN_NO_SEGV_HANDLER=1` / `SCRIP_NO_SEGV_HANDLER`."* (or the equivalent phrasing) — verbatim or near-verbatim in `claude01, claude03, claude05–claude14, claude16, claude_C, claude_P, claude`.

Only **`claude02`** (no mention of either var), **`claude04`** (this seat — already carries the correction, in the words this session read at start: *"Neither has a `getenv` reader anywhere under `SCRIP/src`; `CSN_NO_SEGV_HANDLER` belongs to the separate, externally-cloned CSNOBOL4 oracle repo"*) and **`claude15`** (also already corrected) are clean.

The `NO-O2-EVER` rule found **zero** live violations — every root that mentions the retired sentence at all does so with correct retraction language (§2), consistent with the s267 memo having had time to land.

**Reading the two rules side by side is itself the finding.** The `-O2` correction had an explicit fleet-wide memo (`memo-no-o2-builds-ever`, cited inside several roots' own corrected text) and is now clean everywhere it's mentioned. The SEGV-handler correction landed in `RULES.md` on the **same date as this session** with no memo cited anywhere in the 16 stale roots — consistent with `RULES.md` ~line 168's routing law ("a law change is not routed until the fleet is mailed... the same session sends a LAW TELEGRAM") not yet having been executed for this specific correction. This FINDING is handed to `hq_C` with that recommendation rather than this seat mailing 19 inboxes unilaterally — routing a law change fleet-wide reads as an HQ decision, not a worker-seat one.

---

## 4. SCOPE HELD — no cross-seat edits made

Per this row's own NEXT step 2, no other root's `CLAUDE.md` was modified. This session's own `/home/claude04/CLAUDE.md` needed no edit (already clean on both rules). The 16 stale roots are named above so each owning seat can self-correct on sight, matching the standing doctrine already present in every corrected digest banner ("when this file and RULES.md disagree, RULES.md wins and you tell HQ").

**DONE-WHEN status, stated plainly:** this row's `DONE-WHEN` runs the gate itself and requires exit 0. It currently exits 1 — 16 real, live, unfixed roots exist, and this row is not the mechanism that fixes them (that's each seat's own edit, or a future bulk pass Lon/HQ explicitly authorizes). This mirrors the `-O2` case's own arc: a memo/telegram plus each seat's own self-edit is what actually drives the count to zero, not this row. The gate is the durable, reusable, extensible artifact; DONE-WHEN closing is downstream of 18 other sessions' own edits (or an HQ-authorized bulk pass), not of this one.
