# FINDING — a row's own DONE-WHEN is evidence about its WITNESSES, never about the ROW

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Date:** 2026-08-27 · **Tree:** SCRIP `4ddea506`, corpus `1f126166a` (post-rebase), `make pristine` `-O0`
**Occasion:** ceo routed seat04's held-back reclassification — *"the 38 agree-today-but-cited witnesses are YOUR reclassification call"*.

## THE MEASUREMENT

`corpus/probe/conformance/KEEP.md` held 38 witnesses back from conversion: each is GREEN against the oracle today, but each is cited **by exact filename** in a currently-existing `conform-*` task file. seat04 declined to convert them on their own green measurement and asked for the correctness verdict. That was the right call.

The obvious method is **run each cited row's own DONE-WHEN** — cheap, fully automatable, and not a matter of opinion, since a row's own criterion is that row's own definition of cured. Over the **28** distinct rows cited from that file:

| | count |
|---|---|
| rows passing their own DONE-WHEN | **16** |
| rows still failing | **12** |
| witnesses released for conversion | **38** |
| witnesses that stay held | **3** |

## ⛔ THE METHOD IS NOT SUFFICIENT ALONE — AND MY FIRST CORRECTION TO IT WAS ALSO WRONG

`conform-line-lastline-crash` **passes its own DONE-WHEN, rc=0.** That criterion graded two witnesses — `k14_stno_line.sno`, `k31_line_lastline_gaps.sno` — both green. `KEEP.md` cites **four** witnesses to that row, and the other two, `k11_lastfile_lastline_lastno.sno` and `k30_lastfile_only.sno`, **still diverge in both modes.**

⭐ **A DONE-WHEN that never looks at a witness cannot report that the witness is red — a row's own DONE-WHEN is evidence about its WITNESSES, never about the ROW.** The criterion did not lie; it answered a narrower question than I was asking it, which is this org's recurring class (`command -v icont`; my own s274 state-column count).

⭐ **What surfaced it was a SECOND, INDEPENDENTLY-BUILT witness list.** The rows' DONE-WHENs and `KEEP.md`'s citation table were assembled by different people at different times for different purposes, so where they disagreed there was something to find. Had I derived the witness set *from* the DONE-WHENs — the tidier implementation — the two instruments would have been one and the disagreement would have been invisible. **Agreement is evidence only when the instruments differ.**

## ⛔⛔ AND THEN I DREW THE WRONG CONCLUSION FROM A CORRECT MEASUREMENT

I ruled the row **OPEN** and widened its DONE-WHEN to all four witnesses. **That was wrong, and it is corrected here rather than quietly deleted, because the error is more instructive than the finding.**

Reading the failure **text** instead of stopping at the red: k30 dies with `** Error 342 ... &constant read before its one-time assignment: &LASTFILE`. **k11 and k30 are `&LASTFILE` witnesses.** They are red because `&FILE`/`&LASTFILE` are **unimplemented** — the scope of **`kw-missing-4`**, whose own DONE-WHEN already names k30 and k11 explicitly, and for which Lon's global grant landed in-chat the same evening. They were never `conform-line-lastline-crash`'s to fix. **The defect was in the CITATION TABLE, not in the row's criterion.** ceo's narrowing to k14+k31 was substantively right; I have restored it, re-cited both witnesses to `kw-missing-4`, and the row is closable.

⭐⭐ **THE SHARPENED LESSON, WHICH IS THE ONE WORTH KEEPING.** The cross-check did its job: a disagreement between a criterion and an independently-built citation table is real information, and finding it is exactly what the second instrument is for. **But that disagreement has THREE possible causes, not one** — the criterion is too narrow, the witness is genuinely red for that row, or **the citation is misattributed.** I collapsed three into one and took the pessimistic branch. ⛔ **A red witness is not evidence until you have read WHY it is red.** "It diverges" names a symptom; attributing a symptom to a row is precisely the transcription step where provenance dies (`RULES.md:105`). One `cat` of the stderr would have settled it, and I had already run the command that produced that file.

⭐ **Note the symmetry with the same session's Pascal work, where the identical error class fired twice more:** a `</dev/null` board and a 16-bit-`integer` `fpc` peer, both of which produced real numbers that were confidently, symmetrically wrong **toward red**. Three times in one session the fast reading was the pessimistic one. **For a correctness seat, the pessimistic reading is the one that feels like diligence — which is exactly why it needs the extra measurement, not less.**

**`f09_apply.sno` is the one GENUINE instance of the too-narrow-criterion shape.** It cites `conform-local-opsyn-m4-empty`, that row passes its own DONE-WHEN, and `f09_apply` prints `7/3/8` against the oracle's `7/3/7` — a silent wrong answer, no error text, nothing else claiming it. That row needs its criterion widened or the witness re-cited before it is closed.

## THE RULE THIS YIELDS

**Release requires BOTH halves, never either alone:** (1) the witness is green today against the oracle in both modes, text and rc; **and** (2) its citing row passes its own DONE-WHEN. Neither is sufficient. Half (1) alone is what seat04 correctly refused to act on; half (2) alone is what would have false-closed `conform-line-lastline-crash`.

**Generalised, for every closure call in this org:** before closing a row on its DONE-WHEN, ask *which witnesses does this criterion actually execute* and compare that set against the witnesses the row's own prose, LEDGER and `KEEP.md`-style tables name. A criterion narrower than its row is not a rare defect — it is the **normal** outcome of a DONE-WHEN written early, when one repro was known, and never widened as further witnesses were filed against the same row.

## LANDED

- `conform-line-lastline-crash`'s DONE-WHEN **restored to k14+k31** after my widening proved wrong; verified rc=0; the row is closable. `k11`/`k30` **re-cited to `kw-missing-4`**, which was re-ranked 8 → 1 (its blocker, Lon's `&FILE`/`&LASTFILE` grant, landed the same evening) and now visibly owns the two witnesses that will convert when it lands.
- `probe/conformance/KEEP.md` carries the full ruling, the 38/3 split, and the re-run commands, so it is falsifiable rather than asserted (corpus `1f126166a`).
- The 15 genuinely-cured rows had already been swept out of `QUEUE.tsv` (LAW 4 — the queue is a dispatch buffer, not a memory), so only `conform-line-lastline-crash` still held a live row. **The dispatch cost of this whole class was one row — and it was the one the method got wrong.**
