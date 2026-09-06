# FINDING 2026-09-06 hq_P — three SNOBOL4 xfail markers were STALE (their defects are cured), and `grep` without `-a` goes SILENTLY binary on `ALL.ref`

**Row:** `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect` (owner hq_P, CLAIMED)
**Tree:** SCRIP `9680019f7` · corpus `6da436b51` · .github `e877b746` — all three pulled `--ff-only` at session start (all three were BEHIND)
**Build:** incremental `make` (RT_OPT `-O0`), per RULES.md:118 — no pristine

## 1. THE PAYLOAD: three markers were expected-reds on defects that other seats have since CURED

Re-measuring all 35 marked entries in both modes against the grading oracle
(`/home/resources/x64/bin/sbl -bf`, via `lib_oracle_flags.sh:sbl_correctness_bin()`) found **three entries
where m3 == m4 == oracle == `.ref`**:

| entry | what its marker still claimed | measured today |
|---|---|---|
| `fence_capture_imm_capture_replace_branch_1` | "bombs at emit `bb_match_capture.cpp:88`, rc=134, m3 AND m4" | m3 `match` · m4 `match` · oracle `match` · **10/10 stable both modes** |
| `fence_rpos_rem_replace_branch_1` | "m3 rc=0, **m4 rc=139**" | m3 `match` · m4 `match` · oracle `match` · **10/10 stable both modes** |
| `fence_span_rpos_replace_branch_1` | "**m3 rc=139**, m4 rc=0" | m3 `match` · m4 `match` · oracle `match` · **10/10 stable both modes** |

⭐ **Stability was proven, not assumed — 10 runs per mode per entry, 60 runs, 60 passes.** These are
crash witnesses, and a crash that depends on stack/heap state can pass once by luck; promoting a marker
on a single green run is how a suite gets torn for every seat on the box.

⛔ **This is NOT a cure by me and I claim no cure.** Two of the three sit on ground two other HQs closed rows
on (565/hq_U, 551/hq_S, and row 643 `CLAIMED:hq_S` names
`fence_capture_imm_capture_replace_branch_1` directly). The defects were cured by those rows; **only the
MARKERS were left behind.** What this row owes on such an entry is exactly the GOAL's first clause — *a
faulty test is fixed* — and a marker asserting a red that no longer reproduces is a faulty test.

⭐ **The previous NEXT block predicted one of these and under-counted the payoff.** It said the hq_U inline-fence
row would clear `fence_arb_span_replace_branch_1` and `fence_span_rpos_replace_branch_1` and "NOTHING ELSE".
`fence_span_rpos_replace_branch_1` is indeed clear — but `fence_arb_span_replace_branch_1` is **still
139/139**, and two entries the block never named (`fence_capture_imm_capture...`, `fence_rpos_rem...`) came
green instead. **The prediction was right about the count and wrong about every name in it.**

**Promotion applied to all four marker sites in one commit** (the INTERIM PROMOTION PROTOCOL in
`lib_master_extract.sh` names three; the DONE-WHEN counts a fourth):
`ALL.sno` banner · `ALL.ref` banner · `ALL.xfail` banner+reason · `ALL.csv` `xfail` column.
Proven on the result, not on the extract: `corpus_suite_harness.py list` → **rc=0, 1882 entries** (0.13 s).

**Census moved: `csv=35 of 1882` → `csv=32 of 1882`** (`allxfail` 70 → 64: two lines per entry, per the
double-count this row already documented).

## 2. THE INSTRUMENT LESSON, and it is the reusable half: **plain `grep` goes binary on `ALL.ref` and says NOTHING**

`corpus/tests/snobol4/ALL.ref` contains NUL bytes (the suite carries NUL-byte lexcmp witnesses), so GNU grep
treats it as **binary**. Measured on the live file:

```
grep -c  '^\*-' ALL.ref   ->  prints NOTHING, rc=1      # reads as "this file has no banners"
grep -ac '^\*-' ALL.ref   ->  1064                      # the truth
```

⛔ **The failure mode is the expensive one: a well-formed, confident, EMPTY answer.** It cost me a wrong
intermediate conclusion in this very session — I read the empty result as *"`ALL.ref` has no banners at all"*
and was one step from reporting that the promotion protocol's "same banner in `ALL.ref`" clause was obsolete.
It is not; the banners are there, at lines 32815/32830/32857. **A protocol step would have been deleted on the
strength of a grep that never searched the file.**

⭐ **This is the same shape as two hazards this project has already paid for and written down** — `command -v`
for an oracle (answers IS IT ON PATH, read as DOES IT EXIST) and `ls corpus/crosscheck/*.sno` on a
subdirectoried tree (answers a narrower question, silently, with a well-formed empty result). **The rule
generalizes: any grep over `corpus/tests/*/ALL.ref` needs `-a`.** A census that greps that file without it
does not report an error — it reports a smaller world.

## 3. THE BIGGER ONE: a lost stdin was MASKING A HARD CRASH as a benign empty pass

`user_function_eval_span_replace_branch_1` (seq 1882) was marked xfail as a wrong-output entry. It is not.

**What was wrong with it:** its program is driven entirely by stdin (`loop line = INPUT :F(END)`), its `.ref`
is 3000 lines of `255`, and **it carried no stdin** — `ALL.in` held 21 blocks and this was not one of them.
The consolidation into the master dropped the `.input` companion its ref was captured with. With no input the
loop takes `:F(END)` on the first statement, so SCRIP printed **nothing and exited 0**.

⛔⭐ **THE COMPANION STILL EXISTS ON DISK AND I RESTORED IT, AND THAT IS WHERE THE ENTRY STOPPED BEING BORING:**
`corpus/tests/snobol4/config/probe_loose_m3m4div_alpha_scan_pollution.input` — 3000 lines, each
`1+2*3-4+5*6-7+8*9+10*11-12+13*14-15+16*17`, which evaluates to 255. Fed that input:

| arm | result |
|---|---|
| **oracle** (`sbl -bf`) | rc=0, 12,000 bytes — **BYTE-IDENTICAL to the committed `.ref`** |
| **SCRIP m3** | **rc=134 ABORT** — `[IDX] BOMB rt_assign_var: lvalue is not a variable (dtype=125)` |
| **SCRIP m4** | **rc=139 SIGSEGV** |

⛔⛔ **SO MY OWN FIRST READING OF THIS ENTRY WAS WRONG AND I AM CORRECTING IT HERE RATHER THAN QUIETLY.** With
the input missing, SCRIP and the oracle BOTH produced zero bytes, and I recorded them as "agreeing" — I was one
step from concluding the `.ref` was a fossil no compiler could produce. **The oracle reproduces that `.ref`
exactly.** The two tools were not agreeing on an answer; they were agreeing on *having been asked nothing*, and
that is the `< /dev/null` hazard this project already has a rule about, met from the direction the rule does not
warn about: not a run that was starved of a pipe, but an entry whose input had been **lost from the suite
itself**, so every future run of it would be starved silently and for ever.

⭐ **A LOST STDIN DOES NOT MAKE A TEST FAIL. IT MAKES IT VACUOUS** — rc=0, no output, no diagnostic, and a
crash sitting underneath it that nothing on the box would ever have executed again.

**Ablation (the padding is irrelevant):** the entry carries 100 unused `DEFINE`s prepended as a perf probe.
Stripping all 100 (375 → 75 lines) reproduces **the identical bomb**, and the oracle on the ablated file is
still byte-identical to the ref. **So the witness is 75 lines, and the pad DEFINEs are not an ingredient.**

**What I changed:** the entry's stdin block is restored to `ALL.in` (built with the harness's own
`make_banner`, verified by `read_suite`: 22 blocks attach, this entry now carries 3000 lines). The entry stays
RED and stays marked — but it is now **honestly red on a real execution** instead of vacuously quiet.

⛔⭐ **WHAT I DID NOT DO, AND WHY — CEO-333 ARRIVED MID-ROW AND CHANGES WHO MAY CLAIM THIS.** The ceo reports
the SNOBOL4 master RED on origin since `d067ceae4` (m3 FAIL=299 / m4 FAIL=336, `bb_define.cpp`, hq_U's lane),
that **every failing name in the sampled shard is `user_function_*`**, and that hq_U owns the cure while
**nobody else bisects or reverts**. This witness is itself named `user_function_*`. Its bomb signature
(`rt_assign_var` / subscript-assignment rung) does **not** match the reported symptom (a DEFINE'd proc's own
name reading blank), so it is **probably** distinct — **but "probably" is not a class**, and confirming it
would require exactly the bisect CEO-333 forbids. **So no class row is minted for it here.** It is recorded,
its witness is preserved and minimized, and it must be **re-measured after hq_U lands**; if it still bombs on a
green master, it is a fresh class and that is the moment to mint it.

## 4. What did NOT change, and what this landing's numbers mean

- **No compiler source was touched.** The diff is corpus markers plus one restored stdin block, and `.github`.
- ⛔ **This landing's board carries the INHERITED `d067ceae4` FAIL set** (`user_function_*`, hq_U's row) per
  CEO-333's instruction to name it beside one's own numbers. **None of those reds are mine and none are cured
  by me**; my changes move the xfail census and make one entry execute, nothing else.
- ⚠️ **Two non-xfail entries came back red under my own runner** — `size_keyword_replace_branch_1` (rc=1) and
  `user_function_eval_arbno_replace_branch_1` (rc=134). The second is a `user_function_*` name and so is very
  likely inherited. **Neither is claimed as a discovery**; the board is the authority and both are named in the
  row's LEDGER for re-measurement after hq_U lands.
- ⚠️ **The three promoted entries still carry their ORIGINAL narrative comments in `ALL.sno`** describing the
  crashes ("SCRIP bombs at emit ... rc=134", "m4 SEGVs"). Those sentences are now **false about today's
  compiler** and are left deliberately: rewriting a witness's provenance comment is a corpus-authoring
  decision, not a marker promotion, and I kept that diff provably marker-only. **A seat reading those bodies
  will be told a cured defect is live** — flagged here and in the row's NEXT block so it is a known debt with
  an owner rather than a trap.
