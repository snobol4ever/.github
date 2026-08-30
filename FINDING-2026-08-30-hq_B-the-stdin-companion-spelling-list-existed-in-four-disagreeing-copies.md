# FINDING 2026-08-30 hq_B — the stdin-companion spelling list existed in four copies and no two agreed

**Tree:** SCRIP `3fa3f557` (cure `24f7456c`) · corpus `2f552159` · measured 2026-08-30, seat `hq_B`.

## The four copies

A loose corpus program's stdin companion is spelled `<stem>.stdin`, `<stem>.in`, or `<stem>.input`.
`corpus_suite_harness.py` held **four independent lists** of which spellings exist:

| site | knew | consequence |
|---|---|---|
| `sidecar_in_path()` (suite level) | `.in`, `.input` | blind to `.stdin` |
| `cmd_convert_blocks()` (loose level) | `.stdin` only | a loose `.in`/`.input` never reached an entry |
| `cmd_capture_oracle_refs()` | all three | but only in order to **refuse** on them |
| `cmd_convert_blocks()` **re-validation** | `.stdin` only | a private fourth copy |

All three spellings are live in the corpus: `corpus/tests/icon/rung36_jcon_*.stdin` (8 files) and 46
`.in`/`.input` companions under `demos/`, `benchmarks/`, `packages/`, `tests/`. Every one of those
resolvers was blind to real files the others could see.

## ⭐ Why a partial resolver is worse than a missing one

**It never says so.** It resolves to `None`, `None` means `/dev/null`, the program runs **with the wrong
input**, and its output is then scored as a genuine verdict. Nothing errors; a wrong answer arrives
wearing the same clothes as a right one. `sidecar_in_path`'s own `.input` amendment records exactly this
("a WRONG ANSWER wearing a verdict, not a failure") — and the amendment fixed one copy, because nobody
knew there were four.

## ⭐⭐ The fourth copy was found only because a control FAILED

Copies 1–3 were found by reading. Copy 4 — the one inside `convert_blocks`' on-disk re-validation — was
invisible to reading, because it is *deliberately* independent: hq_C's design has the re-validation
re-derive the original's stdin from the loose file rather than from `written.stdin`, so a round-trip that
lost the sidecar produces a real behavioral mismatch instead of two coincidentally-identical verdicts.
That design is correct and was kept.

What it did in practice, once `.input` entries could convert at all:

```
[1/2] e1_dot_stdin: OK (stdin)
[2/2] e2_dot_input: OK (stdin)
✅ wrote OUT.icn / OUT.ref / OUT.in: 2 entries
⛔ ON-DISK RE-VALIDATION FAILED for 1 entries -- the WRITTEN suite files diverge...
   e2_dot_input: orig={m3: FAIL, m4: FAIL} suite={m3: PASS, m4: PASS}
```

The conversion was **correct**; the check was wrong. It ran the *original* unfed and the *suite entry*
fed, and reported the disagreement as "the written suite diverges from a fresh re-read".

⛔ **A false ⛔ is not the harmless direction of this bug.** It tells a seat to distrust a good conversion
and go re-derive a correct `.ref` — destructive work on a healthy file, which is precisely the failure
`cmd_extract`'s own banner warns about for a different two-cause error message.

Independence is preserved in the cure by reading the loose file **fresh** through the one resolver — not
by keeping a private list. Independence of *data*, not duplication of *logic*.

## Cure

One resolver, `loose_stdin_companion()`, used by all four sites. It also refuses three things no copy
handled: two companions beside one stem (ambiguity — picking the first is the vacuous-ref failure with an
extra step), non-UTF-8, and a `<family>.in` that is really a converted suite's **banner-keyed sidecar**
rather than raw stdin. That last one is not hypothetical: six live in the corpus
(`tests/{snobol4,icon,snocone}/ALL.in`, `icon/rung36_all.in`, `icon/rung27_read.in`,
`snocone/crosscheck_rungA14.in`), and feeding one would push banner lines into a program and grade the
result.

**Corpus-wide control:** 6/6 suite sidecars refused, 48/48 real loose companions fed, **0 false
refusals**, and 0 stems carrying more than one companion — so the ambiguity arm cannot fire on today's
tree. It is a guard for tomorrow, not a live behaviour change.

## The general form

A constant duplicated across N call sites is an ordinary maintenance smell. A constant duplicated across
N call sites **where being wrong produces silence rather than an error** is a different animal: the
copies drift, three of them are wrong, and the system reports full confidence throughout. Census before
you add the fifth: `grep -n 'with_suffix("\.stdin")\|\.input\|loose_stdin_companion' scripts/corpus_suite_harness.py`.

Related: `FINDING-2026-08-30-hq_B-a-deleted-guard-has-no-failing-test-two-were-removed-unmentioned.md`;
`corpus-suites-consolidation.task.md` FOUR LAWS (Law 1 round-trip, Law 4 arms-can-disagree).
