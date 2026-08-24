# FINDING hq_P s269 — THREE MORE INSTRUMENTS THAT CANNOT EXPRESS THEIR OWN OUTCOME, AND THE REGEN DUTY THAT ANOTHER SEAT'S CHAIN DOES NOT DISCHARGE

**Session:** s269 (2026-08-24, announcement day) · **seat:** `hq_P` · **mode:** FLEET-4
**Trees:** SCRIP `f9b00d60` · corpus `35b7d0340` · .github (this commit) — all measured, none quoted (LAW 0)
**Kin:** `FINDING-2026-08-23-hq_P-six-language-baseline-pinned-pre-strip.md` · SCRIP `e70f1743` (the two instruments repaired the session before) · `FINDING-2026-08-23-hq_P-the-m1-board-grades-beauty-against-an-oracle-that-refuses-it.md`

## THE CLASS, RESTATED

s268 repaired two checks that had been reporting green-by-blindness (`test_gate_bb_one_box.sh`, 36/36 FAIL for the entire life of the template architecture; `rtx_unit_test`, a stale golden reporting an intentional feature as a red). **The class is not "buggy tests." It is instruments whose failure mode is indistinguishable from their success mode to the person reading the output.** Three more turned up in one session, none of them looking for.

## 1. `handoff_status.sh` LABELS *BEHIND* AS *UNPUSHED*

At session start all three repos read `UNPUSHED`. They were not. Every commit was already on origin; the trees were 1–3 commits behind because other seats had pushed on top.

```
corpus  [main]  UNPUSHED  local=19d55799c origin=35b7d0340     <- BEHIND, nothing at risk
.github [main]  UNPUSHED  local=aa68620fc origin=158f2d186     <- BEHIND, nothing at risk
SCRIP   [main]  UNPUSHED  local=e70f17433 origin=15738e4a6     <- BEHIND, nothing at risk
```

The script prints `0 unpushed` beside the label, so it is **half-honest** and a careful reader survives it. But the column is what gets read.

⛔ **WHY THIS ONE IS WORSE THAN IT LOOKS.** A seat that reads `UNPUSHED` and not the count concludes **it has lost work**. The panic response to *"I have unpushed commits I cannot see"* is exactly the destructive-git class THE LOOP §3b forbids — `reset --hard`, `push --force`, history rewrite. **The instrument's failure mode points a seat at the single action the protocol most wants to prevent.**

⭐ **THE DISCRIMINATOR, one command, before reasoning about any push-state red:**
```bash
git merge-base --is-ancestor HEAD origin/main   # exit 0 = your work IS on origin; you are merely BEHIND
```
Proper cure (not taken here — it is `ceo`'s to route): the status line should distinguish **BEHIND** (ff available, nothing at risk) from **UNPUSHED** (local commits not on origin, work genuinely at risk) from **DIVERGED**. Today two of those three collapse into one word.

## 2. THE BANNER COULD NOT SEE THIS SESSION'S COMMITS — AND IT WAS RIGHT

The banner reported **`⚠ NOTHING LANDED — no commit and no FINDING`** after I had committed and pushed twice (`SCRIP f9b00d60`, `.github 0d0d156d`).

The banner does not count commits with `log --since`; that was tried and **credited a seat that did nothing with 4 commits it had merely pulled**. It counts by **ATTRIBUTION** — commits whose message names the seat or its row. **Neither of my commit messages contained `hq_P`.** So the instrument was not lying; **I was invisible to it, and the fault was mine.**

⭐ **The lesson is the one this project keeps re-learning from the other side:** the commit-message seat id is not decoration, it is the **input to the only instrument that measures whether a session did anything.** A convention that an instrument depends on, and that nothing enforces, is a convention that will be silently broken — and the breakage surfaces as the instrument accusing an honest session of being empty. Two adjacent readings are both wrong: typing a verdict over the banner (the STALE-ORIENTATION violation that voided 11 false banners at s47), and believing the session was empty. **The right move is to ask what the instrument keys on** — which took one `grep` and turned an apparent instrument defect into a genuine self-correction.

## 3. ANOTHER SEAT'S REGEN CHAIN DOES NOT DISCHARGE YOUR REGEN DUTY

My s268 codegen-touching commit `e70f1743` (splitting `bb_binop_relop_val` into its own file) landed **20:52**. seat01's regen chain ran **21:58–22:01** and swept **feature / programs / prolog-bench / crosscheck**. It is easy — and wrong — to read that as covering me.

**It does not. The benchmark and demo trees were last swept at 20:39 — thirteen minutes BEFORE my touch.**

| tree | last sweep | vs my 20:52 touch |
|---|---|---|
| demo | 20:39 | ⛔ before |
| crosscheck | 20:41, again 22:01 | ✅ after |
| feature | 21:58 | ✅ after |
| programs | 21:59 | ✅ after |
| prolog-bench | 22:00 | ✅ after |
| benchmark | *(not in that chain)* | ⛔ never |

Re-ran benchmark and demo at current HEAD: **zero changes on either**, confirming the box split was byte-neutral as a pure file split should be.

⭐ **The lesson is the ordering, not the outcome.** The overlap between another seat's chain and your duty is **coincidence** — that seat sweeps the trees ITS change needed, on ITS schedule. Had the split not been byte-neutral, two trees would have carried silent drift with a plausible-looking chain of regen commits sitting right above them in the log, *appearing* to cover it. **Check timestamps against your own codegen commit, per tree.** This is the same shape as the s268 partially-corrupted board: the dangerous artifact is the one that looks covered.

## 4. AND ONE ORDINARY CURE, SAME SESSION: `RT_OPT` WAS DEFINED TWICE

`Makefile:34` carries the s262 **NO `-O2` BUILDS** FACT RULE. `Makefile:367` carried a second `RT_OPT ?=` whose comment still taught the **repealed** O0-DEV-O2-BENCH rule: *"-O0 for development; -O2 explicitly for benchmark/demo runs only."*

**Functionally inert** — `?=` never overrode, the resolved value always came from `:34` — **and that is exactly why it survived nine sessions.** ⛔ The defect is not what `make` computes; it is what a **reader** computes. Grep `RT_OPT` to learn the project's optimization policy and you get two hits with opposite instructions and no way to tell which is law. **That is how a NO-`-O2` violation gets written in good faith by someone doing the right research.** Cured in `f9b00d60`: definition deleted, pointer left naming `:34` as the single site; one `^RT_OPT` remains, `make -p` resolves byte-identical, build green.

## RECEIPTS

Blocking set at `make pristine`, RT_OPT `-O0`, run through the `make test` target wired in `11c89219` — **the first real exercise of that target since it stopped being a false green, and it works and it is truthful:**

```
corpus   m3 PASS=363 FAIL=1 · m4 PASS=363 FAIL=1 SKIP=0 (364 total) · sole red demo_treebank (the OPEN vlist-expr-alternation defect -- NOT "deliberate"; Lon corrected that digest word s269)
emit_no_lang                  OK — no language-identity identifier in src/emitter or src/templates
template_medium_invisible     bb_ ratchet 0 (ceiling 0); xa_flat.cpp(8) remains, informational WIP
```

Fail-set matches the s268 pinned baseline **name-for-name**, so the `RT_OPT` cure is behaviour-neutral by measurement, not by argument.

## ROUTED

- `ceo` ← `status-report-for-lon` (the s269 report Lon asked for), `scoreboard-acked-and-notes` (row minted), `handoff-status-behind-reads-as-unpushed` (defect 1).
- `GOAL-HQ-PERFORM.md` LIVE CURSOR s269 — all four items, with the outstanding list.
- QUEUE row 163 `icon-bench-correct-zero-of-eight` (rank 1, FREE) + baton `tasks/icon-bench-correct-zero-of-eight.task.md` — scoped as ONE class over four witnesses, not eight rows.
