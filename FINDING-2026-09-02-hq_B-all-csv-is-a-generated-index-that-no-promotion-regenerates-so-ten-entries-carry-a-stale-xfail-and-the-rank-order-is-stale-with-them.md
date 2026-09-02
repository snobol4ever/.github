# FINDING 2026-09-02 hq_B — `ALL.csv` is a GENERATED index that no XFAIL promotion regenerates, so ten SNOBOL4 entries carry a stale `xfail=1` — and because the builder sorts `rank` BY xfail, the row ordering is stale with them

**Found while** verifying the graded population for row `optimizer-off-path-segvs-so-the-emergency-bypass-is-not-a-correct-path` (the watermark gate REFUSES rc=2 on population drift, so the population had to be established before the gate could be trusted). **Not that row's defect** — recorded separately.

## THE MEASUREMENT

The XFAIL marker has **four** homes in the SNOBOL4 master, and `lib_master_extract.sh`'s INTERIM PROMOTION PROTOCOL enumerates **three**:

| home | who writes it | state today |
|---|---|---|
| `ALL.sno` banner suffix | promotion commit, by hand | current |
| `ALL.ref` banner suffix | promotion commit, by hand | current |
| `ALL.xfail` sidecar reason | promotion commit, by hand | current |
| **`ALL.csv` `xfail` column** | **`util_build_master_suite.py`, generated** | **stale for 10 entries** |

Counted with the graders' own reader (`corpus_suite_harness.read_suite`, the function `util_census_optimizer_bypass.py` and every board call):

```
reader (ALL.sno + ALL.xfail sidecar):  1726 entries, 70 xfail, 1656 graded
ALL.csv xfail=1 column:                80
disagreement:                          10 entries, one-directional
```

The ten are `arbno_fence_notany_replace_branch_{1,2}`, `code_eval_eval_replace_branch_1`, `code_eval_replace_{1,2}`, `fence_arb_span_replace_branch_2`, `fence_pos_len_replace_branch_{1,2}`, `user_function_eval_arbno_replace_branch_2`, `user_function_indirect_replace_2`. **The disagreement runs one way only** — no entry is xfail to the reader and 0 in the CSV — which is the signature of promotions (xfail → graded) landing in three places and not the fourth.

## IT IS EXACTLY THE PROMOTION HISTORY, NOT DRIFT

Every promotion commit touched `ALL.sno`, `ALL.ref` and `ALL.xfail`, and **none touched `ALL.csv`**:

| commit | promoted | files touched |
|---|---|---|
| `c487af7c` | 5 markers | sno, ref, xfail |
| `04177c4b` | 3 markers | sno, ref, xfail |
| `2d75933e` | 1 marker | sno, xfail |
| `5b44ca01` | 1 marker | sno, ref, xfail |

5 + 3 + 1 + 1 = **10**, the exact set above. ⭐ **Every one of those commits was CORRECT under the protocol as written** — `5b44ca01`'s own message documents proving all three sites in one commit. The protocol is what is short a place, not the seats following it.

## WHY THE FOURTH HOME IS DIFFERENT, AND WHY THE CURE IS NOT "ALSO EDIT THE CSV"

`ALL.csv` is not a hand-maintained file. `util_build_master_suite.py:1320` writes the column as `int(bool(e.xfail))` — **derived from the same reader**, so a builder run would regenerate all ten correctly.

⛔ **But the same builder sorts the whole file BY xfail** (`:1128`, key `(int(bool(e.xfail)), feature-count, length, name)`), so `rank` is a function of xfail too. Ten stale xfail values therefore mean **ten stale ranks and a stale ordering around them** — and re-running the builder to fix the column re-ranks the file (the builder's own header records a scratch rebuild at 1438 changed lines in `ALL.sno` alone). So the honest options are a re-rank commit, or a gate that holds the index accountable to its sources, or an explicit note that the CSV's `xfail`/`rank` are stale-by-design between builds. Which one is a ruling, not a seat's pick.

## IMPACT: NOT LATENT — IT IS ALREADY PUBLISHED, IN A ROW THAT CONTRADICTS ITSELF

I first wrote this section as "latent, no grader reads the column." **That was wrong, and I found it by grepping the consumers instead of trusting the claim.** `util_build_score_md.py:137-146` reads `ALL.csv` and counts that column — and it builds `SCORE.md`, which this project's own docs call *Lon's "central location for the current score."*

So the number is published. Here is the live SNOBOL4 row of `SCORE.md`, unedited, with the two halves marked:

```
| snobol4 | 1726 entries, 80 xfail | ... | total=1726 · m3 pass=1656 ... xfail=70 · m4 ... xfail=70 |
                        ^^^^^^^^                                          ^^^^^^^
                   stale CSV column                              the board's live reader
```

⭐⭐ **ONE ROW, ONE QUANTITY, TWO NUMBERS — and it has been sitting there being read.** This is worse than a plain wrong number: both halves look sourced, they sit inches apart, and a reader who notices has no way to tell which is authoritative without knowing that one column is a generated index and the other a live grader. A scoreboard that disagrees with itself teaches its readers to stop trusting all of it.

## CURED IN THIS COMMIT (the consumer, not the index)

`master_info()` now reads the **graders' own authority** rather than the index: `read_suite` / `read_block_suite` through the harness, the same functions the master board calls. It does not reimplement grading (that file's own standing rule), and a master it cannot read now reports **UNPROVEN naming the exception** instead of falling back to the CSV — a fallback to the other authority is exactly what produced the contradiction.

This fixes the published contradiction without forcing the re-rank churn. **The index itself is still stale** and that half remains open (see the recommendation below).

## ⛔ A SECOND DEFECT, FOUND ONLY BECAUSE THE FIRST FIX REFUSED HONESTLY

The first version of the fix called `read_suite` for every language. Five of seven then reported UNPROVEN:

```
icon     ValueError: family.ref is shorter than family.sno at seq 4607 (seq4607)
prolog   ValueError: family.ref is shorter than family.sno at seq 1139 (seq1139)
raku     ... seq 556      pascal ... seq 537      snocone ... seq 1321
```

⛔ **`read_suite` is the SNOBOL4 ONE-LINE dialect. Every other master is a BLOCK suite and needs `read_block_suite` with that language's banner regex** (`LANG_CONFIGS` + `banner_re_for`, exactly as `cmd_run` dispatches). Called on a `.pl`/`.icn`/`.pas`/`.sc` master it does not fail cleanly — it **mis-parses into nonsense**, reporting a sequence number in the thousands for a 534-entry suite, and on `rebus` it silently returned **267 entries for a 48-entry master** (it had counted lines). A wrong count that raises is survivable; a wrong count that returns is not.

⭐ **This was the same trap as `corpus_suite_harness.py list`, which had the governance consequence that `lib_master_extract.sh`'s INTERIM PROMOTION PROTOCOL instructs every promoter to prove the result by running `list` on it — an instruction that could not be followed for any non-`.sno` master.**

✅ **CURED WHILE THIS FINDING WAS BEING WRITTEN, BY hq_P (`abbbe9d3`), off the report I sent them.** `list` now takes `--lang` and dispatches exactly as `run` does, and with no `--lang` it **REFUSES up front naming the reader, the suffix and the flag** instead of letting the grammar produce a message that accuses the data. Re-verified here rather than assumed: `list --lang prolog` reads the committed Prolog master at **400 entries**, matching its index row-for-row, and the bare form now refuses. ⭐ hq_P named the expensive half correctly in their own commit message — the old error blamed the `.ref` file, so a wrong-READER fault presented as a corpus-DATA fault, and I had to bisect against the committed baseline to prove my own edits had not caused it.

⛔ **The `master_info` instance cured in this commit is the SAME root cause in a second caller** — `read_suite` hardcodes SNOBOL4's `*` banner (`BANNER_RE`, `:88`), and every caller must dispatch by language or inherit the fault. Two callers found and fixed in one day, from two directions, is the shape of a defect that lives in a default rather than in a call site: **the safe default for a reader that only understands one dialect is to refuse an unfamiliar one, not to try.**

## NO GATE COVERS IT

`test_gate_master_suite_builder_contract.sh` grades the builder's deferral contract and its must-not-write-the-real-tree property; it does not compare the generated index against the suite it indexes. The agreement between `ALL.csv` and `ALL.xfail` is an invariant that **lives in the gap between two files and is held by neither** — the same shape `test_gate_port_exit_value_contract.sh`'s own header names when it prints both instruments from one command.

## RECOMMENDED NEXT STEP (not taken here — it is a ruling, and this is not that row)

The cheap, non-churning half is a check, not a rebuild: assert `len({r for r in ALL.csv if r.xfail}) == len({e for e in read_suite(...) if e.xfail})` and name the disagreeing entries. It costs milliseconds, it would have fired on `c487af7c`, and it does not force a re-rank. Whether to also re-run the builder and take the re-rank diff is hq_C's call as the suite's owner.

⛔ **What is still open after this commit:** the index itself — 10 stale `xfail` values and the `rank` ordering that depends on them. `util_build_score_md.py` no longer reads it and `list` no longer mis-reads block masters, so nothing is publishing a wrong number today, but the index and its sources still disagree and the next consumer inherits it. Whether to take the re-rank churn or add a cheap agreement check is hq_C's call as the suite's owner; this FINDING is the routing.

— hq_B, TRIO, 2026-09-02
