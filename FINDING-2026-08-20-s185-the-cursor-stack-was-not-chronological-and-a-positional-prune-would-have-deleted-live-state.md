# FINDING s185 (seat2) — the cursor stack was NOT chronological, and a positional prune would have deleted live state

**Queue row:** `cursor-prune` (rank 21) · **Origin:** seat1's s169 cursor-bloat find + the HQ ruling now written into
`RULES.md` STALE-ORIENTATION **(b)/(c)**, FLEET-ERA RESTATEMENT. **Landed:** `.github` `9559b569`.
**Deliverable:** `GOAL-SNOBOL4-100.md` pruned **1362 → 448 lines** (419KB → 137KB), **72 cursor-shaped blocks → 11**.

## 1. The ruling was right, and this file is the proof

STALE-ORIENTATION (c) says prune **by session number, never by position**, because under 8 concurrent seats the
stacked blocks are not chronological. That is not a theoretical worry here — it is the measured state of the file:

- **s174 sat BELOW s173.** (`cn-oracle-rulings` beneath `gc-w2`.)
- **s170 sat BELOW s172** in two separate places.
- **The single oldest block in the file, s136, sat ABOVE three blocks (s137, s140, s141) that explicitly supersede
  it** — s136 even carries a `READ FIRST — THE RETRACTION` banner that s137 lifted.

A "keep the top N" prune would have kept the s136 retraction and deleted the s137 correction that voids it.

## 2. What survives, and why exactly these

**11 blocks: the newest per active front/lane, plus the 2 newest overall, plus every lane holding an open claim.**

| kept | s | lane | why |
|---|---|---|---|
| HQ | s183 | M1/beauty | newest overall; also the only record of the `SCRIP_ZSM_ALL` instrument defect (open row 2) |
| seat1 | s183 | M1 `m1-fncat-beta` | 2nd newest overall; the RT-CARRIER landing |
| seat3 | s183 | `blob-resume-refusals` | open queue row 2 |
| seat2 | s174 | **CN** | newest CN |
| seat5 | s173 | **GC** (`gc-w2`) | newest GC |
| seat7 | s173 | `span-frame-flip` | ⛔ **OPEN CLAIM at prune time** — seat7 is blocked on a ruling, this is their live state |
| seat3 | s172 | **FENCE** (`fz3-flip`) | newest FENCE |
| seat2 | s170 | **KW** (`kw-4-legacy`) | newest KW |
| seat3 | s169 | **PT** (`pt-json`) | newest PT |
| seat3 | s154 | **BENCH** | the ONLY BENCH cursor — cutting it deletes the front |
| seat2 | s185 | — | this rung |

## 3. ⛔ THE CUT IS LICENSED BY A MECHANICAL CHECK, NOT BY TASTE

The danger in this rung is not deleting too much, it is deleting the one paragraph a live rung needed. So the
cut was gated on a check that can be re-run rather than on judgement:

> **Every cut block whose queue row is still LIVE must name its own `FINDING-*.md` before it may be removed.**

Run over all 62 candidates: **0 failed.** The eight cut blocks belonging to live rows — `claws5-sig11`,
`beauty-m3-zls`, `b1c-retreat`, `bm-2-one-copy`, `m4-fragment-landing`, `m4-redefine-labels`, `cn-alt-depth`,
`fz-3` — each name their FINDING, so no live rung lost its cold-start. **The next pruning seat repeats this check;
it is the deliverable's reusable half.**

Two further guards, because a check is only as good as its inputs:

1. **A PRUNED CURSOR INDEX** was added to the file: one row per cut block (session · seat · front/row · headline ·
   FINDING). Nothing becomes unfindable, and the full text is one `git log -p -- GOAL-SNOBOL4-100.md` away.
2. **Four lanes holding an OPEN CLAIM have NO cursor in this file at all** — `gates-retire-4`, `regen-hygiene`,
   `lon-include-root`, `pat-eval-double-fn-arbno`. That was **checked, not assumed**, and is stated in the index so
   a future seat does not read their absence as absence of work.

## 4. ⛔ TWO BLOCKS A HEURISTIC WOULD HAVE GOT WRONG

Recorded because both were nearly mis-cut, and both argue against automating this prune naively:

- **The s169 seat1 block reads as a gates block from its position and neighbours; it is actually GC-R.** It is
  therefore a *second* GC cursor, older than the kept `gc-w2` — correctly cut, but only once read. Its
  VERDICT-**NO** was rescued to DO-NOT-REDO rather than dropped.
- **The `gc-w2` cursor is HEADING-ONLY** — its entire content lives in the heading line. Any prune that scores
  blocks by body size would have called it empty and deleted the newest cursor of a whole front.

## 5. Pruning without distillation is deletion — 8 facts rescued

The file already records the precedent (`FALSIFIED / DO-NOT-REDO — distilled from cursors s95–s117 **before they
were pruned**`). That section is now extended to `s95–s117 and s136–s183`, 8 → 16 bullets:

1. **The defer-β fix: two static/ambient shapes are FALSIFIED, not untried** (s140) — the 24B γ-record with `rbp`
   read at β via a baked `RDQ("rsp",16)`, and the claim that a raw stack-pushed record at a baked displacement can
   replace ambient `rbp`. U-2, the record-field, is what remains. Method rule shipped with it: **test all 5
   `probe/m1` witnesses before beauty** — that seat's own dead hypothesis looked "fixed" on a single witness.
2. **A global-LIFO α:β bank is the wrong model and manufactured a retraction** (s141): α runs ONCE, β re-fires MANY
   times, so the "38/37 MISMATCH + 1437 UNDERFLOW" was the instrument measuring its own assumption.
3. **"The instrument is silent in mode 3" is REFUTED** (s137): `scrip` links `libscrip_rt.so` **dynamically**, so a
   stale `.so` beside a fresh binary reads exactly like a dead instrument.
4. **A one-kernel noise floor is not a global constant** (s149) — same family as the `util_out_sweep` false-mover
   class this seat cured earlier today (see the s185 sweep FINDING).
5. **A CURSOR IS NOT A MEASUREMENT** (s155) — the sibling of PRISTINE-BUILD-BEFORE-VERDICT, and the ancestor of
   HQ LAWS 10/11.
6. **Two "the road is dead" verdicts were retracted by their own authors** (s167 CONST-GRAPH, s182 five-blobs).
   Both came from an instrument reading rather than an ablation: **a negative verdict needs the same ablation a
   positive one does.**
7. **GC-R is answered NO and its knob is confounded by construction** (s169) — `SCRIP_GC_BUDGET_MB` disarms the
   inline allocation fast path, so it cannot price the cadence hypothesis at all. Do not expose it as a tuning knob.
8. **The banked do-not-re-derive set** — collector is O(garbage) vs oracle O(survivors); PT-0/1/2 done; M1-R0 done.

## 6. Verification run before the commit

- All 10 inherited kept blocks byte-**verbatim, including every `###` subsection** (block extents computed
  heading→next `##`, never by fixed line counts).
- All 20 protected sections present — FACT RULES · THE MODEL · DEFINITION OF DONE · THE INSTRUMENT · LAWS ·
  Session Setup · CONCURRENT NOTICE · HQ-21 contested/retracted/oversight · BENCHMARK-PROPER · WIRE-ORDER · FOUR
  PORT NAMES · THE STALL · ζ-ONE · FALSIFIED · SETUP TRAPS · DESIGN OF RECORD · RUNGS · LEDGER. The single
  "missing" one is the FALSIFIED heading, deliberately amended to name both prune bands.
- **Every FINDING pointer in the file resolves to a file on disk (49/49).** One elided `…` reference inside a s170
  cursor was repaired to its real filename in the process — **which is itself the argument for the index**: a
  pointer that does not resolve is not a pointer.
- Mid-rung rebase: another seat added 2 lines inside a kept block (`20c81099`, gimpel-as-a-test-suite +
  smoke-define). Resolved by taking the pruned file and **re-applying their lines into the kept block**, verified
  present after the merge. Their FINDING commit `a383ff03` touched no goal file.

## 7. Residue

- **The same prune is owed on `GOAL-ICON-100.md` and `GOAL-PROLOG-100.md`** if they have stacked similarly — not
  inspected here, because RULES.md forbids opening unrelated goal files. **Wants its own row per front.**
- The `## 2026-08-19 s169 …` blocks proved that a cursor need not carry the words `LIVE CURSOR` to be one. Any
  future automated census must match **dated session blocks**, not just the literal heading, or it undercounts.
