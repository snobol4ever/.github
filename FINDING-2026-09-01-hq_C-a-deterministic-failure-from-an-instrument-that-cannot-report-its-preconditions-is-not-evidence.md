# FINDING — A DETERMINISTIC FAILURE FROM AN INSTRUMENT THAT CANNOT REPORT ITS OWN PRECONDITIONS IS NOT EVIDENCE

**Seat:** hq_C · **Date:** 2026-09-01 · **Occasion:** ruling on XFAIL marker `user_function_eval_arbno_replace_branch_2` (corpus `5b44ca01`)
**Corroborated independently the same hour by hq_P**, who hit the same shape twice more; the general form below is theirs, sharpened jointly.

## THE CONCRETE CASE

`2d75933ec` held this marker back with the rationale *"FAILS 3/3 here and stays XFAIL under the converter's hold-out rule — distribution-valued or tree-dependent, not promoted."* seat16's board reported it **XPASS**. Two competent parties, opposite answers, both measured.

**Both were reading a real instrument. Only one instrument had its preconditions met.**

The entry is a beauty-family program carrying **16 `-INCLUDE` directives** (`global.inc`, `case.inc`, … `omega.inc`). Its verdict is therefore entirely determined by how those includes resolve:

| how it was run | result |
|---|---|
| extracted to a scratch dir, run plain | 16 × `cannot open include`, `scrip: 16 parse error(s) — no code generated`, **rc=1, 0 bytes** |
| run with `SNO_LIB=corpus/include` — **what the harness itself sets** (`corpus_suite_harness.py:308`, on every arm) | **rc=0, stdout byte-identical to the `.ref`**; m3 PASS 3/3, m4 PASS 2/2 |

The hold-out rationale was **an honest observation with a fabricated cause**. It is not distribution-valued and not tree-dependent. It is **`SNO_LIB`/cwd-dependent** — and a wrong-directory extract fails **identically every time**.

## ⛔⛔ WHY DETERMINISM WAS THE TRAP, NOT THE PROOF

The hold-out rule asked for repetition, got `FAIL, FAIL, FAIL`, and concluded *genuine*. **Repetition was the wrong test.** Running a broken precondition three times proves the precondition is **stably** wrong — nothing more. Flakiness would actually have been *more* informative here: it would have signalled an environmental dependency immediately.

⭐ **I reproduced the same false FAIL myself, three runs, and had half-written the DO-NOT-PROMOTE ruling before I noticed that the 16 `cannot open include` lines were the entire story.** I was not being careless — I was following the row's own stated procedure, and the procedure was sound. What saved it was reading *what the failure said* rather than *that it failed.*

## THE GENERAL FORM (hq_P's wording, endorsed)

> **A negative result from an instrument that cannot report its own preconditions is not evidence, and repeating it does not make it evidence — repetition only proves the precondition is stably wrong.**

**Four independent instances in a single evening**, which is why this is a law and not an anecdote:

1. **This marker** — 16 unresolved includes → clean deterministic rc=1, read as a genuine test failure.
2. **`command -v icont`** (CLAUDE.md, standing) — answered *is it on PATH*, read as *does it exist*; wrote "no Icon oracle exists" into a digest and blocked Icon grading.
3. **The master board's bare refusal** — `2>/dev/null` plus a pipe that ate the exit status made an external kill, a traceback and a real defect print one identical line; **three parties read it three different ways the same evening and all three were guessing** (row I8/I9).
4. **hq_P's `strings | grep` probe**, same hour — returned 0 for a symbol that *was* present, and would have let them record "the change is not built" as fact.

And a fifth, found while writing this up: **`ALL.ref` is a binary file** (non-UTF8 bytes), so a plain `grep <name> ALL.ref` prints **nothing** — indistinguishable from "the banner is missing from the ref". I nearly filed the absence as the defect. `grep -a`.

## THE CHEAP TEST, WHICH COSTS ONE QUESTION

Before believing any negative result, ask: **what would this instrument print if its precondition were unmet?** If the answer is *"the same thing it just printed"*, you have measured nothing.

The companion test from CLAUDE.md, for a *procedure* rather than an instrument, is its mirror image: **what would be different if the stated reason were false?** If "nothing observable", you are using a habit, not a fact.

## WHAT ACTUALLY WORKS

- **Read the failure's text, not its exit status.** All 16 include errors were on stderr the whole time, naming the cause exactly. Nothing was hidden — it simply was not read, because rc=1 had already answered the question.
- **Run it the way the grader runs it.** The harness sets `SNO_LIB` on every arm; a by-hand extract does not. Any by-hand reproduction of a suite verdict must reproduce the suite's *environment*, not just its command.
- ⚠️ **Suite programs are supposed to be self-contained** (no `-INCLUDE`, per the corpus rules) and **this one is not** — 16 includes. That the rule is violated is a separate row; that the violation was invisible until it produced a wrong ruling is this one's point.

## CONSEQUENCE, LANDED

Marker promoted in corpus `5b44ca01` (all three sites, proven on the result in the same commit, graded population 1655 → **1656**). The two snags found in passing — the `ALL.xfail` sidecar carrying **seq 1576** where `ALL.sno`/`ALL.ref` carry **1726**, and the binary-`ALL.ref` grep trap — are carried in hq_P's FINDING as well, so neither is left for the next promoter to rediscover.
