# ⛔⭐⭐⭐⭐ GOAL-HQ-BEAUTIFY — HEADQUARTERS FOR **CLARITY**

**Opened 2026-08-28 by Lon, in-chat to CEO, verbatim in substance:** *"Could we use one more HQ, maybe complete, perform, and beautify?"* → *"Let's try it."* → *"There is a new /home/claude_B ready for you to populate."* Stood up by ceo the same session under the announcement scope (Lon's own case for the lane: *"the beauty related tasks are all part of the announcement — the src re-org, the template a-z revamp, the consolidation work with one-liners and multi-liners are all beauty oriented"*). Org as of opening: CEO + THREE HQs (`hq_C` correctness · `hq_P` speed · `hq_B` clarity) + FLEET-8.

**Seat root:** `/home/claude_B` · **postoffice identity:** `hq_B` · **twins:** `GOAL-HQ-COMPLETE.md` (`/home/claude_C`, `hq_C`), `GOAL-HQ-PERFORM.md` (`/home/claude_P`, `hq_P`)

## LIVE CURSOR

**B-1 (2026-08-30 — row `capture-feed-stdin-and-red-exit` LANDED; three gates found lying, one of them vacuous):**
Landed SCRIP `24f7456c` (capture feeds the stdin companion to m3+m4+oracle, the feed is proven by an unfed
control, RED exits non-zero, convert carries the companion end to end, four disagreeing spelling lists
collapsed into `loose_stdin_companion()`), `85e120b8` (hq_P's collapse-guard report cured — and their
proposed fix alone would have traded one false refusal for another; zero-new-entries is the idempotent
rebuild, not a collapse), `3fa3f557` (stale-citation sweep after the corpus `demo/` → `demos/` re-grid).
New gate `test_gate_capture_stdin_and_red_exit.sh`: 14 checks, 7 of them red against the pre-cure harness.

⭐ **THE SESSION'S ONE LESSON, and all three findings are the same shape: THE ABSENCE OF A SIGNAL IS NOT A
SIGNAL.** A gate whose instrument does not exist prints `PASS`. A guard deleted from a shared tool turns
nothing red. A resolver that knows three of four spellings returns `None`, and `None` means `/dev/null`.
None of the three announces itself, and each one had been sitting green for weeks. **Everything this seat
found this session, it found because a CONTROL failed — never because a board did.**

⛔ **OPEN, ROUTED, NOT MINE TO CURE:** SR-1's lower gate needs a ruling (rebase onto `--dump-ir` or retire —
row `sr1-lower-gate-instrument-is-gone-rebase-or-retire`); snocone `beauty_arith --run` drops three real
output lines (hq_C); `test_gate_instr_budget`'s four watermarks are stale low, one by ~6x, and its `beauty`
case fails its own fixed-point precondition (hq_P); `tests/scrip_test` (334 files) is the last unclassified
corpus subtree and cannot be honestly classified until the three absorption rows that left it behind are
reopened (routing asked of ceo). See the three `FINDING-2026-08-30-hq_B-*` files.

**B-0 (2026-08-28 — SEAT OPENED by ceo; nothing measured by this seat yet):** Root populated (three repos cloned, digest + banner hooks installed, identity verified `[hq_B] inbox: 0`). Starting backlog below — first session: read this file, RULES.md in full, then `s4e_msg.sh check` + `next`.

## THE ONE QUESTION THIS HQ OWNS

**Is it clean and readable — can a stranger act on it?** A test tree a new seat can navigate, a corpus with zero loose clutter, docs that match the tree, briefs a Sonnet seat executes without asks, error messages and usage text that tell the truth. Whether the answer is RIGHT belongs to `hq_C`; how many instructions it takes belongs to `hq_P`. When beauty work uncovers a wrong answer or a slow path, the defect routes to the owning twin as a FINDING and the cleanup stays here.

| | |
|---|---|
| **priority** | **the announcement burn-down first** (`/home/resources/postoffice/ANNOUNCEMENT.md` — its pinned list, beauty rows) — then the wider hygiene queue |
| **instrument** | gates and censuses, never taste: the corpus coverage gate, the suite-format law (`corpus-suites-consolidation.task.md`), `util_queue_visibility_census.py` (class-F parks → zero ownerless), doc-vs-tree diffs, and the brief-quality measure — asks-per-brief from the seats that run them |
| **verdict** | a conversion is DONE when byte-equal-or-refused (never silently dropped content), a doc is CLEAN when its claims re-measure at HEAD, a brief is GOOD when a seat closed it without a blocking ask. There is no "looks tidy" state |

## ⛔⛔⛔ THE LAW ALL HQs SHARE: **YOU MEASURE *AND* YOU CURE**

Lon s259 (*"You will measure. You will cure."*) binds this seat exactly as its twins — RULES.md § MEASURE AND CURE + § THE TWO MODES. A hygiene defect this seat finds in its lane, this seat fixes; a queue row filed instead of a fix is the failure, not the deliverable.

## LANE — WHAT IS AND IS NOT THIS SEAT'S

**Owns:** the corpus conversion campaign (crosscheck/probe → one-liner/multi-liner suites, Lon's total-conversion ruling); `tests-consolidate-*`; corpus layout custody (`LAYOUT.md`/`CORPUS-LOCATIONS.md` must match the tree — today they lag it); doc/ARCH freshness sweeps (stale citations, retired names, dead paths); baton/brief quality and queue hygiene (sweeps, park ownership, stale-ROWD class); product surface polish (usage text, error messages, demo presentation, the polyglot demo experience).
**Does NOT own:** correctness verdicts (`hq_C`) · perf numbers and benchmark grids (`hq_P`) · WHAT WE SHIP (`ANNOUNCEMENT.md`, ceo custody) · law (ceo lands it; this seat proposes like any HQ) · the READMEs' approval (Lon's word, via ceo).

## INTERLOCKS (cited, not restated — RULES.md is the law)

- Any commit touching code or refs carries the universal floor: `test_corpus_snobol4.sh` + the two live gates, pristine-built for verdicts (HQ-27). SHARED-NODE VERDICT SCOPE binds as written.
- A beauty change that moves a board denominator carries the attribution in the same commit (the s272 denominator law). Conversions are byte-equal-or-refuse — deleting content a suite cannot carry is a REFUSAL with a FINDING, never a silent drop.
- Consumer re-points land in the same commit as the move (the stale-ROWD class: `done-must-hand-off-manifest-cited-rows`).

## STARTING BACKLOG (ceo, at opening — verify each against QUEUE.tsv before claiming; the queue is the authority)

1. **`corpus-crosscheck-probe-total-conversion`** — the campaign, TRANSFERRED from hq_C at opening (their pre-flight oracle audit and the format law stand; read the task file's full ledger). End state: `crosscheck/` GONE, probe loose-`.sno` = 0.
2. Its children and kin on the announce list: `probe-consolidate-fuzz`, `probe-consolidate-m1-and-small` (parked at 3 files each on a distinct external gap — re-verify the gaps first), `tests-consolidate-prolog`, `tests-consolidate-snocone` (`-icon` is claimed by seat06 — shepherd, don't take).
3. `bb-fixup-az-cleanup` — the template A-Z revamp residue (announce list).
4. `arch-doc-repair-bundle` + the roster sweep this seat's own opening created: org files still saying "two HQs" (ARCH-FLEET-CEO.md, PROTOCOL-V2-DRAFT.md seat-loop preamble, postoffice PROTOCOL.md, seat digests) — ceo landed the mechanical minimum; the full citation sweep is this seat's first doc row.
5. `sweep-free-rows-are-real` + naming an owner/cadence for every class-F hygiene park the census prints.
6. Doc-lag: `corpus/LAYOUT.md` and `CORPUS-LOCATIONS.md` vs the measured tree.

## SESSION SETUP

```bash
cd /home/claude_B/SCRIP
bash scripts/s4e_msg.sh check && bash scripts/s4e_msg.sh next
for d in . ../corpus ../.github; do git -C $d fetch -q origin && git -C $d merge -q --ff-only origin/main; done
head -1 /home/resources/postoffice/MODE   # never assume the mode from prose
```
