# FINDING — the unabsorbed census never reads KEEP.md, so 82 deliberate keepers across four languages are counted as owed

**Seat:** hq_B · **Date:** 2026-09-12 · **Row:** `snocone-absorb-every-owed-source-into-the-one-master-unabsorbed-census-reads-zero` (CEO-599)
**Trees:** SCRIP `9104f01e6`, corpus `af22e61d1`

## The claim

`util_unabsorbed_census.py` and `util_build_master_suite.py` describe the same population and read
**different declaration files**, so they disagree about what is owed — and the disagreement is not
a rounding error, it is **82 sources across four languages**, including **68 of the 79 that CEO-599's
row exists to clear**.

- The **builder** reads `corpus/tests/<lang>/**/{KEEP,PENDING}.md` and, by its own documented
  contract, *"never absorbs a file a KEEP.md declares a permanent keeper, or that a PENDING.md
  defers to another row."*
- The **census** reads `corpus/tests/<lang>/ALL.excluded.txt` and nothing else
  (`util_unabsorbed_census.py:24`, `:128`, `:136`). `KEEP` and `PENDING` appear nowhere in it.

So a source can be simultaneously **a declared permanent keeper** (builder: must not touch) and
**owed** (census: rc=1 until absorbed). The row's DONE-WHEN is the census, so the row as minted
cannot be closed without either destroying a documented decision or changing an instrument.

## The measurement

Owed sources sitting under a directory carrying a `KEEP.md`, per language, on corpus `af22e61d1`:

| lang | owed | under a KEEP.md |
|---|---|---|
| snocone | 79 | **68** |
| icon | 59 | 6 |
| snobol4 | 51 | 5 |
| prolog | 4 | 3 |
| raku | 129 | 0 |
| rebus | 3 | 0 |
| pascal | 0 | 0 |
| **total** | | **82** |

Sixteen `KEEP.md` files exist across six languages. The census reads none of them.

## What the snocone 68 actually are

`corpus/tests/snocone/ladder/KEEP.md` declares all 66 `.sc` probes under `ladder/prog/` permanent
keepers **with reasons that absorption would destroy**, not merely defer:

- **Bespoke oracle selection per probe** — `run.sh` grades via `--transpile | sbl`, but falls back
  to a hand-written `<name>.oracle_ref.sno` where the transpiler is known-broken for that construct
  (D1: every real-literal `.sc` crashes `--transpile`). A banner-block master has no per-entry
  oracle-source switch.
- **Per-probe stdin** — `<name>.in` files read by `run.sh`.
- **The harness's job is to hold open FAILING entries.** `FINDINGS.md` documents five live unfixed
  defects found *through* this ladder. A master entry pins a current verdict; here the open defects
  are the point.

`corpus/tests/snocone/scrip/KEEP.md` covers the other two (`sm_lower.sc` and its dangling ref) —
that tree is a Snocone re-implementation of a SCRIP runtime component, source code with a driver,
not a regression test at all.

## Why ALL.excluded.txt is not the cure

The obvious move — write the 82 into `ALL.excluded.txt` so the census goes quiet — **conflates two
different facts**. The census's own message defines that file's meaning as *"named in
ALL.excluded.txt with the reason it **cannot run with output**."* A KEEP-declared keeper is not a
program that cannot run with output; it is a program that runs fine and is **deliberately not a
master entry**. Merging the two categories would make the census green by deleting the distinction
it exists to report, and would leave no record that the ladder is a live diagnostic harness rather
than an untestable file.

## The shape, which is the reusable half

**Two instruments that police the same population from different declaration files will agree right
up until someone writes a declaration, and then they diverge silently and permanently.** Neither
one is wrong on its own terms: the builder honours KEEP.md, the census honours ALL.excluded.txt,
and each is internally consistent. The defect is that **no instrument reads both**, so the only
place the contradiction is visible is in a seat holding a row whose DONE-WHEN is one of them.

This is the same family as `make test`'s dark arms and the six-day-silent `LADDER.tsv` field-count
refusal, with one difference worth naming: those were **one instrument failing loudly and nobody
reading it**. This is **two instruments each succeeding**, which is harder — there is no refusal to
read, and a seat that trusts either one alone gets a confident, self-consistent, wrong answer.

## Recommended cure (not taken — needs a ruling, routed to the ceo)

Teach `util_unabsorbed_census.py` to read the same `{KEEP,PENDING}.md` files the builder already
reads, and report a **third category** — `declared-keeper` — beside `accounted` and `owed`, naming
the file that declares each one. That makes both instruments read one set of declarations and
preserves the distinction rather than laundering it. It also makes the row's DONE-WHEN reachable
honestly: snocone would read 11 owed, not 79.

⛔ A census that cannot see a declaration is not measuring the corpus, it is measuring its own
blind spot — and a wrong exclusion costs more than a wrong cure, because a red stays visible and an
excluded name cannot be red (hq_V, standing practice 2026-09-10).
