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

---

## ⛔⭐ CORRECTION AND CLOSE (hq_B, 2026-09-12, at the landing — SCRIP `74e41757a` + `51799f462`)

**THE 82 IN THIS FILE'S OWN TITLE IS A PROXY, AND THE MATCHER-EXACT ANSWER IS 72.** The table above
counted *"owed sources sitting under a directory carrying a `KEEP.md`"* — a directory-level
approximation of the question, standing in for the declaration matcher itself. With
`util_build_master_suite.py`'s `_declared_in_keep`/`_pending_deferral` actually imported and run, the
population is:

| measure | count |
|---|---|
| declared keepers, total | **409** |
| of those, previously counted as OWED (the real debt correction) | **72** |
| of those, already carrying a reason in `ALL.excluded.txt` (reclassified for reporting only) | **337** |
| directory-proxy count from the table above | 79 (+3 dangling rows quoted as 82) |
| proxy files the matcher does **not** declare | **8** |

The eight the proxy over-counted: `benchmarks/rebus/{arith_loop,fib_recur,string_concat}.reb`, which
sit under a `benchmarks/rebus/KEEP.md` that **no instrument reads** (the builder's `ROOT` is
`corpus/tests/<lang>/`, so that file describes a kernel tree and is honoured by nothing — CEO-609
places kernel trees outside absorption debt anyway, so nothing turned on it); and
`tests/snobol4/config/{BALREV,BLANKS,DIFF,OR,REVERSE}.sno`, which are under a directory holding two
`*KEEP.md` files that declare *other* sources.

⭐ **THE CORRECTION IS THE FINDING AGAIN, ONE LEVEL UP.** This file's own thesis is that two
instruments each succeeding on their own terms give a confident, self-consistent, wrong answer. The
number in its title was produced by a *third* instrument — a proxy predicate invented for the
measurement — and it was wrong in the same shape and for the same reason, by eight. A proxy that
answers a narrower question than the matcher will never say so. **Measure with the instrument that
will act on the answer, or the number is about a different question than the fix.**

## A second class this landing found, routed and not cured here

`tests/snobol4/config/{BALREV,BLANKS,DIFF,OR,REVERSE}.sno` read **OWED** while
`_additive_walk_tests` **structurally cannot absorb anything under a `config/` directory** — five
sources of hq_U's snobol4 51 that no number of absorption runs could ever move, because running the
tool again re-makes the same skip. Identical shape to the deferral gap this file names, and to hq_S's
extra-test-tree deferral (SCRIP `8efb91b86`). The builder's own comment already prescribes the cure:
name them in `ALL.excluded.txt` with a reason, rather than widening the walk. **Routed to hq_U with
the snobol4 absorption row; not cured here.**

## Status

**CLOSED by the landing.** The census imports the builder's matchers rather than porting a third
copy, and REFUSES rc=2 rather than reporting zero keepers when it cannot read the declarations.
Corpus-wide `OWED` 190 → 106; snocone 79 → 10, icon 57 → 45, raku/prolog/pascal/rebus 0, snobol4 51.
