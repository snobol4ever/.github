# FINDING: denominator audit of the six non-Prolog consolidated families — **eight false greens, four refusals, exactly one real coverage hole (181 entries)**, and the discriminator that tells a hole from a redundancy

**Seat:** hq_B (TRIO) · **Date:** 2026-08-30 · **Row:** `graders-denominator-audit-six-families` (rank 2, ceo-assigned) · **Follows:** `FINDING-2026-08-30-hq_B-24-prolog-rung-graders-refused-rc2-over-143-gradable-entries-hiding-three-segvs.md`, and the ranked-cover law now in RULES.md.

## THE HEADLINE IS A CORRECTION, NOT AN ESCALATION

The Prolog round found 143 gradable entries hidden behind refusals and three SIGSEGVs among them. The obvious expectation was more of the same across the other six families. **That expectation is wrong, and checking it was the most valuable thing in this audit.**

Of the eight false greens and four refusals found here, **only one is a real coverage hole.** Every other one is *duplicate* coverage lost — the content is still graded, by a different script, on every run. Reporting them as hidden populations would have been a false alarm of exactly the shape hq_C caught me in on rung13.

**The discriminator, measured per family:**

> **Does a master board grade that family's whole `ALL.*` set?**

```
snobol4   test_corpus_snobol4.sh          grades ALL 1726     -> refusals are REDUNDANT
pascal    test_gate_pascal_m3/m4.sh       grades the set      -> clean
icon      NOTHING grades ALL.icn ...      but test_icon_all_rungs.sh grades the same
                                          families as SUITE pairs -> REDUNDANT
snocone   test_snocone_corpus_suite.sh    grades TEN of 273   -> REAL HOLE
raku      parser fixtures only (total=97) -> clean, nothing refusing
rebus     parser fixtures only (total=15) -> clean, nothing refusing
prolog    NOTHING grades ALL.pl at all    -> which is exactly why 143 were lost there
```

It must be checked **per family** and never inferred from another family's result. Two identical-looking refusals in this audit needed opposite dispositions for precisely this reason.

## POPULATION AND CENSUS

55 graders reference the six families' corpus directories — **icon 22 · snobol4 23 · snocone 4 · pascal 4 · raku 1 · rebus 1** (of 381 `test_*.sh` in the tree). Each was run and its `rc` captured **directly, never through a pipeline** (`$?` after a pipe reports the pager — this tree's own documented trap).

```
family    green  green-ZERO  red  REFUSE  green-no-denominator
icon        2        7        9     0            4
snocone     2        0        0     1            1
raku        1        0        0     0            0
pascal      1        0        3     0            0
snobol4     5        0        5     3           10
rebus       1        0        0     0            0
TOTAL      12        7       17     4           15
```

A ninth false green — `test_beauty_snocone_all_modes.sh` — sits **outside** this population (it names no `corpus/tests/<lang>` path) and was found by sweeping every script mentioning snocone. That is worth stating: **the census key itself under-reported, which is the same wrong-key defect this audit is about.**

## SHAPE (a) — `rc=0` HAVING GRADED ZERO: EIGHT FOUND, ALL CURED

**Seven in icon** — `test_icon_ir_rung_30..35.sh` (32 named witnesses, **all 32 absorbed into `ALL.icn`**, zero retaining a per-entry `.expected`) and `test_icon_mode4_rung.sh` (a hardcoded `rung01_paper_*` seed set, all five files consolidated away, all five present in `ALL.csv` by origin).

**One in snocone** — `test_beauty_snocone_all_modes.sh`, whose `BEAUTY_DIR` points at `corpus/snocone/demo/...`, a path that **predates the corpus re-grid**; no beauty `test_*.sc` witness exists anywhere under corpus.

⛔ **These are worse than rung13's empty glob.** rung13's loop never ran. These **name** their witnesses, **detect** that each is missing, print `SKIP`, and count it as neither pass nor fail — skip-as-success, which RULES.md calls the same defect with better manners.

⭐ **And every one of them declared its own denominator in a header comment** — `# Gate: PASS=5 FAIL=0`, `# Gate: 14 PASS + 1 SKIP per mode` — which nothing ever compared against. **A declared expectation that no code reads is a comment, not a gate.** That is the cheapest available cure for this whole class and it was sitting in the files the entire time.

**Cures, chosen to match the disposition rather than to maximize the diff** (SCRIP `056e34c9`, `df5e84ce`):
- `rung_30..35` → **REFUSE rc=2** on zero graded. **Not re-pointed on purpose:** `test_icon_all_rungs.sh` already grades these families as suite pairs (measured: `SUITE rung30_builtins_misc: pass=5`, likewise 31–35, 33 entries). Re-pointing would duplicate the aggregate.
- `test_icon_mode4_rung.sh` → **exit code left alone.** Its `exit 0` is deliberate and documented (the ICN-G-1 contract), and that contract is not this row's to overturn — but it was argued for a run that *grades and does not pass*, and says nothing about a run that graded *nothing because its inputs moved*. The code is untouched; the silence is not. A zero total now says so loudly on stderr.
- `test_beauty_snocone_all_modes.sh` → **REFUSE rc=2**, agreeing with its sibling `test_gate_sn7_beauty_self_host.sh` instead of contradicting it with a green.

## SHAPE (b) — PERMANENT REFUSALS: FOUR FOUND, EACH DISPOSITIONED

**1. `test_snocone_crosscheck_suites.sh` — THE ONE REAL HOLE. Re-pointed.**
It refused *"no crosscheck_\*.sc suites"* because those pairs were consolidated into the flat set. **181 of snocone's 273 `ALL.csv` entries carry a crosscheck origin, across 30 families** — and the only other grader over `ALL.sc` covers **ten**. So ~181 entries were graded by nothing at all, behind a verdict nobody re-examines.

Re-pointed with an absorbed fallback keyed on the **`origin`** column, materializing each family so the existing loop, labels, `m3,m4` modes and xfail accounting run unchanged. **Now grading: `entries=181, 30 families, PASS=326 (both modes), XFAIL=18 (per mode), FAIL=0, GATE OK.`** No hidden defects — but the coverage is real and it is back (SCRIP `5ed08adc`).

**2. `test_conformance_spitbol_manual.sh` — redundant. Refusal stands, reason recorded at the site.**
It asks *"has the conformance sweep ever minted a witness?"* — **yes, 132**, absorbed by `corpus 11a36c87` (Lon's ZERO-SUBFOLDERS ruling, which deleted `probe_loose/`). But all 132 carry a conformance origin/family in `ALL.csv`, **none is in `ALL.excluded.txt`**, and `test_corpus_snobol4.sh` grades the whole set (`total=1726`). Re-pointing would duplicate the master board. The answer to its own question is now written into the script so nobody re-investigates.

**3. `test_gate_sn7_beauty_self_host.sh` — stands, already owned.** Refuses because `tests/snobol4/beauty_suite/` no longer exists after a corpus reorg; ceo has it riding the beauty rows.

**4. `test_gate_suite_conversion_complete.sh` — stands, and is correct.** It refuses without a `<lang>` argument. A parameterized gate that refuses rather than defaulting to "measure nothing" is the *right* behaviour, and it is the model the `RUNG=""` case in `test_icon_mode4_rung.sh` fails to follow.

## WHAT I DID NOT DO

The **17 red** graders are genuinely failing and were left alone — they are triaged work in the correctness lane, not this row's class. The **15 green-with-no-denominator** are mostly invariant gates that legitimately have no denominator (a gate asserting "zero `MEDIUM_*` in `bb_*.cpp`" has nothing to count); I did not convert them, and flag only that "no denominator" and "zero denominator" must not be conflated when someone automates this check.

`ALL.icn` (534 entries) is graded by no single master board. That is **not** a hole today — `test_icon_all_rungs.sh` covers the same families as suite pairs — but icon is the one family where the safety margin is a naming convention rather than a set-level guarantee, and it is the place this class will recur.

## THE LESSON, STATED FOR THE POOL

hq_C's ranked cover holds: green gets audited, red gets triaged, a refusal gets neither. This audit adds the counterweight that keeps it honest:

> **A refusal is the best hiding place, but most refusals are not hiding anything.** Finding one costs a measurement, not an alarm. The question that separates them is never "does this grader run?" — it is **"is this content graded by anything else?"**

Eleven of the twelve findings here were redundancies. Reporting them as lost coverage would have been the wrong-key false alarm one level up, and the one that mattered — 181 snocone entries — would have been buried in the noise.
