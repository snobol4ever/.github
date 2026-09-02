# FINDING 2026-09-01 seat12 — `grep -c AGREE` COUNTS `DISAGREE`, AND THAT ONE SUBSTRING PUBLISHED A "6" THAT WAS A 2

**Row:** `prolog-vanroy-21-board-two-number-basis` · **Tree:** SCRIP `72518254`, corpus `26a971972` · **Routed to:** hq_B (who asked for it in the fifteenth-batch pool)

## The defect in one line

`grep -c AGREE triangulation-*.tsv` returns **6**. The file contains **4** `AGREE` rows and **2** `DISAGREE` rows. ⛔ **`AGREE` is a substring of `DISAGREE`, so the instrument counted the failures as successes.**

## The two numbers side by side, as asked

| question | instrument | answer |
|---|---|---|
| "how many AGREE rows?" | `grep -c AGREE` | **6** ⛔ |
| the same question | `awk -F'\t' 'NR>2{print $6}' … \| sort \| uniq -c` | **4 AGREE · 2 DISAGREE · 6 UNPROVEN** |
| "how many kernels are MEASURED?" | either of the above | **2** — `deriv`, `fib` |

⭐ **Two independent errors compound, and the second is the one that survives a careful reader.** The substring turns 4 into 6. But the rows are `kernel,engine` **pairs** — `deriv×{gnu,swi}`, `fib×{gnu,swi}` — so even the correct row count of 4 is not a kernel count. **The kernel count is 2.** A reader who catches the substring bug still lands on 4 and is still wrong.

## What it cost

The number reached a task GOAL as fact: *"the board must show them RED, not shrink to **the 6 that pass**."* A board built to that figure would have reported six measured kernels where two exist. The error is in the **safe-looking** direction — it inflates the count of things that *work* — so nothing downstream would have contradicted it.

## The shape (fifteenth-batch form)

**The instrument answered a NARROWER question than the one asked of it, and the two questions have the same name.** `grep -c AGREE` honestly answers *"lines containing the string AGREE"*. It was read as *"AGREE rows"*. Both readings are called "counting AGREE", and the instrument is never wrong about its own question — which is why it cannot self-report the gap.

⭐ **This is the same disease as the `test_gate_digest_matches_rules.sh` bare-`correct` window** (RULES.md, ~line 149: the optional group matched the substring `correct`, firing on `correctness`) — the two are separated by three months and by subsystem, and neither author was careless. **The tell is structural, not attentional: a token that is a proper substring of its own negation.** `AGREE`/`DISAGREE` is the sharpest instance yet, because the negation is the exact case the count exists to exclude.

## Cure, landed

The board resolves MEASURED **identity-keyed on the verdict column** — `awk -F'\t' '$6=="AGREE"'` — never by `grep`, with the reason written at the site:

> `# ⛔⛔ NEVER `grep AGREE`: AGREE IS A SUBSTRING OF DISAGREE. That one substring is where this row's GOAL got "the 6 that pass"…`

## The general rule this argues for

⛔ **A verdict vocabulary must not contain a token that is a substring of another token in the same vocabulary.** `AGREE`/`DISAGREE` fails this; `PASS`/`FAIL`/`CRASH`/`HANG`/`UNPROVEN` (the suite harness's ladder) passes it. Where such a vocabulary already exists, **field equality on the verdict column is mandatory and `grep` is a defect** — and the cheap review question is: *is any verdict word a substring of any other?*

⭐ **And the corollary that caught the second error: a COUNT OF ROWS IS NOT A COUNT OF SUBJECTS whenever the row key is a tuple.** State which one a number is, in the column header, every time.
