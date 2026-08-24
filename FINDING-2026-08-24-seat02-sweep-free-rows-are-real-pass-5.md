# FINDING 2026-08-24 seat02 — sweep-free-rows-are-real, pass 5: the exact-diff method works, and it caught a permanent false-negative DONE-WHEN born the same day as its row

**Seat:** `seat02` · **task:** `sweep-free-rows-are-real` (row-factory sweep, DONE-WHEN is a deliberate
permanent-refusal stub — see task file). **Repos at start of pass:** SCRIP `843cacfb` / corpus `7291f5ea`
/ `.github` `e6c3ab10` (fresh `git pull --rebase` all three before the snapshot).

## Method: `SWEEP-CLASSIFIED.tsv` (landed by hq_C, pass 4) worked exactly as designed

Regenerated the true-free set (`142` rows, same count as pass 4's baseline — but count-matching a prior
pass is not evidence of no change, see pass 4's own founding lesson) and ran `comm -23`/`comm -13` against
`/home/resources/postoffice/SWEEP-CLASSIFIED.tsv`. Clean, unambiguous, single-line result each way:

- **+1 new**: `icon-corpus-semicolonize`
- **-1 gone**: `tdump-driver-r12-cas-mark-sigsegv`

This is the first pass where the diff was a true set-difference rather than a reconstruction — confirms
hq_C's pass-4 fix (landing the baseline file) solved the method defect that made passes 1-4 unable to
compute their own delta.

## `tdump-driver-r12-cas-mark-sigsegv`: correctly dropped, not a defect

QUEUE.tsv still shows this row `state=FREE` (owner column stale, as previously documented), but
`claims/tdump-driver-r12-cas-mark-sigsegv.claim` now exists — someone is actively holding it. True-free
correctly excludes it. No action taken.

## `icon-corpus-semicolonize`: fresh mint, found and fixed a permanent-false-negative DONE-WHEN

Well-formed mint (rank 1, provenance ceo s269 census → hq_P s271 mint, computable DONE-WHEN, own ledger
explicitly instructs "recompute the counts fresh before trusting them"). Verified directly rather than
forking (batch size of one didn't warrant it):

⛔ **DONE-WHEN was structurally unmeetable.** It checked `corpus/programs/icon` — but commit `4d1d92d8`
("corpus: flatten — programs/* moved up one level, programs/ removed", Lon s269 in-chat, pure `git mv`)
had already removed that path tree-wide, apparently the **same session** this row was minted in. The old
path can never exist again, so even a session that fully completed STEP 1–3 of this row's own brief would
have the DONE-WHEN read "No such file or directory" forever — a **permanent false negative**, born broken.
Same defect class as the banner "reports 0 commits" bug hq_C flagged this session (§ inbox message,
`banner-attributes-wrong-row-on-unclaim`): the check has a correct verdict *shape* while checking the wrong
subject.

**Fixed** (postoffice task file only, no repo commit — this is coordination infrastructure, not code):
`corpus/programs/icon` → `corpus/icon` in the DONE-WHEN, and `corpus/programs/icon/bench*` →
`corpus/benchmarks/icon/` in hq_P's QA coordination note (the former path never existed even pre-flatten
as a literal subpath — Icon bench programs live in a separate top-level `benchmarks/icon`, confirmed by
directory listing). Re-ran the fixed DONE-WHEN: still correctly reads unmet (exit 1), now because real
semicolon-free files exist, not because a directory is missing.

**Recomputed ceo's three census numbers fresh, per the row's own instruction:**

| claim | ceo's number | measured this pass | drift |
|---|---|---|---|
| parser fixtures without `;` | 114/153 | **114/153** | none — exact match |
| `ipl/progs` without `;` (out of scope for this row, context only) | 176/275 | **174/275** | -2 |
| rung tests with `;` | 302/303 | **295/295** | denominator dropped 303→295, all still converted |

Not rewriting ceo's original numbers destructively — appended a dated correction to the task's LEDGER
instead, attributed and separate, matching pass 4's practice for its own two imprecision notes.

## Near-miss, worth recording: a "cured" headline does not mean every row it touches is closed

The same `corpus`/`.github` pull that surfaced the flatten also brought in
`FINDING-2026-08-24-hq_C-vlist-cured-by-a-per-op-filter-and-a-rebase-published-a-stale-board.md`, and this
session's own HQ inbox message paraphrased it as *"vlist/(A , B) is cured at 0e57de3b; a clean tree now
reads 364/364 both modes."* Surface pattern match said `vlist-v05-m4-sigsegv-m3-m4-divergence` (present
in the pass-4 baseline as `LIVE-p4`, unchanged by the exact-diff) might now be ALREADY-FIXED.

Reading the FINDING fully rather than trusting its title: the cure fixed the *general* `(A,B)` disjunction
defect (control `c01`, arm-1-always-wins case) and the corpus-wide board (`364/364`). The FINDING has its
own dedicated section — "THE TAIL, NAMED RATHER THAN BURIED" — stating explicitly that probe
`v05_treebank_pushlist_235` still SIGSEGVs in m4, that this is the family's tail not its body, and names
**this exact row** as the open follow-up.

Built scrip fresh at SCRIP `843cacfb` (large rebuild — 198 files had changed since the last pull) and
reproduced directly via the canonical two-step mode-4 pipeline (`--compile > .s`, `gcc -c`, `gcc -l
libscrip_rt`, matching `test_crosscheck_snobol4.sh`'s `compile_mode4`, not a raw `-o` flag — that emits the
`.s` text itself, not a linked binary, a wrinkle worth remembering next time a probe needs a direct
mode-4 run rather than an asm diff): m3 `MATCH size=1` rc=0, m4 SIGSEGV rc=139. **Exactly as briefed.** Row
correctly remains `LIVE`, no correction needed, verdict unchanged in the baseline file. Recording this as
a near-miss because it is the inverse of pass 2's lesson: there, strong claims inside a row's own brief
needed distrust; here, a strong claim **about** a row, arriving from outside the row (a differently-scoped
FINDING title plus an HQ paraphrase), needed the same discipline. Read the row's own DONE-WHEN, not a
headline that happens to share its name.

## Sanity checks

Zero duplicate topic rows in QUEUE.tsv (`awk` + `sort | uniq -d`, empty). `SWEEP-CLASSIFIED.tsv` rewritten
at SCRIP `843cacfb` / corpus `7291f5ea` / `.github` `e6c3ab10`, verified by fresh `comm` diff to exactly
equal the current true-free set (142 topics, zero mismatch either direction) — pass 6 inherits a real
baseline.

## Net QUEUE.tsv / postoffice change this pass

0 QUEUE.tsv row edits, 0 mints, 0 retirements. 1 task file corrected in place
(`icon-corpus-semicolonize.task.md`: 2 stale paths fixed, 3 census numbers re-measured and 2 corrections
appended to its LEDGER). `SWEEP-CLASSIFIED.tsv` regenerated for pass 6.

Related: `[[FINDING-2026-08-24-hq_C-sweep-free-rows-pass-4-a-count-is-not-a-baseline]]` ·
`[[FINDING-2026-08-24-hq_C-vlist-cured-by-a-per-op-filter-and-a-rebase-published-a-stale-board]]`
