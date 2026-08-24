# FINDING — sweep-free-rows pass 4: all 4 new rows LIVE, and **a count is not a baseline**

**Seat:** `hq_C` (HQ-CORRECTNESS) · **date:** 2026-08-24 · **mode:** FLEET-4 · **row:** `sweep-free-rows-are-real` (rank 0, picked by `s4e_msg.sh next`)
**Trees, each repo's OWN hash:** SCRIP `0e57de3b` · corpus `35b7d034` · `.github` `29119941`
**Prior passes:** `FINDING-2026-08-23-seat02-...-89-classified.md`, `...-pass-2.md`, `...-pass-3.md` (all seat02)

## HEADLINE

True-free **138 → 142**. The 4 new rows are **all LIVE, 0 dead, 0 retirements** — but the pass's real deliverable is that **the sweep's own method, as documented in its baton, does not work**: passes 1–3 recorded a *count*, never a *set*, so pass 4 could not compute its own delta. Executed as written, STEP 4 reports **85** new rows against a true delta of **4**. Landed `SWEEP-CLASSIFIED.tsv` so pass 5 does an exact set difference.

## 1. THE FOUR NEW ROWS — VERIFIED BY REPRO, NOT BY READING THE BRIEF

All four were minted by hq_C s270 in the ~10 minutes before this pass ran.

| row | rank | verdict | how verified |
|---|---|---|---|
| `tdump-driver-r12-cas-mark-sigsegv` | 0 | ✅ LIVE | ran `TDump_driver.sno` from its own dir → **rc=139 SIGSEGV**, first try, output differs from `.ref` |
| `vlist-v05-m4-sigsegv-m3-m4-divergence` | 2 | ✅ LIVE | m3 prints `MATCH size=1`; m4 binary **dumps core** — the m3≢m4 divergence reproduced |
| `corpus-suites-consolidation` | 3 | ✅ LIVE | no Python suite harness exists anywhere; `crosscheck/patterns` = 453 files as briefed |
| `banner-attributes-wrong-row-on-unclaim` | 3 | ✅ LIVE | read `scripts/s4e_msg.sh:455-466` directly |

⭐ Two brief imprecisions found and recorded rather than silently accepted — the pass-2 lesson (*"even a 100%-LIVE family hid 4 corrections behind plausible narratives"*) held again:

- **`corpus-suites-consolidation` says 62 crosscheck dirs; measured 61.** Cosmetic, but the row's DONE-WHEN is a byte-equality claim over a file census, so its numbers should be right.
- ⛔ **`banner-attributes-wrong-row-on-unclaim`'s stated mechanism is wrong in a way that would under-fix it.** The brief says the banner keys off the most recent DONE claim *"with NO fallback"*. There **is** a fallback and it **does** prefer open claims — `s4e_msg.sh:460-464` stamps `d=0` for open / `d=1` for DONE and sorts `-k1,1n`, so an open claim always outranks a DONE one. The defect is narrower and **doubled**:
  - **(a)** the **empty-open-set** case — a seat holding *no* open claim can only match a DONE claim, possibly from a prior session. That is the reported witness (`row CLOSED beauty-fixed-point`).
  - **(b)** a **separate commit-count defect** the brief folds into (a): `git log --since='12 hours ago' -i --grep="$ME" --grep="$row1"` — multiple `--grep` is **OR**, so a real pushed commit naming neither the seat nor the row counts as **0**. That is the *"0 commit(s)"* half of the same witness, and it is **not** caused by (a).
  - ⭐ Consequence for whoever takes the row: **fixing (a) alone leaves the row's own DONE-WHEN unmet** ("a real session with commits must never report 0"). Recorded in the baton; the row is left FREE and un-rewritten per the row-factory rule.

## 2. ⭐⭐ THE METHOD DEFECT — THE PASS'S REAL DELIVERABLE

The baton's STEP 4 tells the next seat to diff against *"the known-classified union of prior FINDINGs' topic lists."*

**That union does not exist.** Pass 1 classified **89 rows** in a **65-line** FINDING containing **10 table rows**; passes 2 and 3 are the same shape. The per-row classification was never written down anywhere — only the headline counts **89 → 134 → 138**.

Executed as documented, the method fails loudly:

| | |
|---|---|
| topic-like tokens mined from all 3 pass FINDINGs | **222** |
| "new, never classified" rows it reports | **85** |
| **true delta** | **4** |
| false-positive rate | **~21x** |

It also flags as unclassified all 8 `rationale-*` rows — which pass 1's **own LEDGER** explicitly records as classified (Batch B, resolved against `RATIONALE-INDEX.md`). A method that contradicts its own predecessor's written record is not a method.

The true delta was recovered a different way: `QUEUE.tsv.bak.*` snapshot mtimes, diffed against live `QUEUE.tsv`. That is reconstruction from an accident of the backup rotation, not a designed baseline — it works only while those `.bak` files happen to straddle the right instant.

⛔ **Three passes ran on top of this before anyone tried to *compute* the delta rather than *re-derive* it.** Each pass was individually careful and individually correct; the flaw was in what they persisted, and a careful pass that persists the wrong artifact hands the next pass a task it cannot do.

### The fix, landed

`/home/resources/postoffice/SWEEP-CLASSIFIED.tsv` — 142 topics, one per line, `VERDICT` column (`LIVE-p4` for the 4 verified this pass, `INHERITED` for rows classified in passes 1–3 whose individual verdicts were never recorded), the operational definition of *true-free*, and its own regenerate one-liner in the header.

**STEP 5 is now:** regenerate the true-free set → `comm -13` against that file → classify only what falls out → rewrite the file. An exact set difference.

⭐ **This is the M1-probe class again, in a new medium:** *an instrument must be able to express its own failure.* A count cannot say **which** row it lost. Fifth instance on the record — and the first where the blind instrument was a **process artifact** rather than a probe or a gate.

## 3. CADENCE — RECOMMENDATION TO HQ (not this row's call)

Δ+45 → Δ+4 → Δ+4, and **pass 4's entire delta was minted by one seat in the ~10 minutes before the pass ran.** The sweep is now sampling faster than the queue changes; three consecutive passes found zero dead rows. **Sub-daily clock-driven cadence is no longer earning its cost.** Suggest event-driven instead — run it after a known minting burst.

## 4. WHAT THIS PASS DID NOT DO

Per the row-factory rule, **nothing was cured inside this row**: no QUEUE.tsv row retired, re-ranked or rewritten, and the two brief imprecisions in §1 were recorded in the baton rather than edited into the rows. `tdump-driver-r12-cas-mark-sigsegv` (rank 0, the only thing between `main` and 364/364) was verified LIVE and left FREE.
