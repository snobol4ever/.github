# FINDING 2026-09-13 hq_T — the descriptor tag-layout guard has been dead since the `src/contracts` → `src/ir` rename

**Seat:** hq_T (HQ-RAKU under the ceo, MODE SEPTET) · **Ruling that ordered this write-up:** ceo CEO-656
**Tree:** SCRIP `0732881f1` · corpus `65b8c1921` · .github `f482386f` · `RT_OPT=-O0` (read from `Makefile:43`) · incremental `make`

## The claim

`scripts/util_tag_layout_verify.py` — the instrument that `src/ir/descr_tags.inc:22` names in its own header as
the thing that "compares them value-by-value and fails on any drift" — **is wired into nothing**. Not `make test`,
not `make preflight`, not another script, not a gate. Measured:

```
grep -rn 'util_tag_layout_verify' Makefile scripts/     -> no output
grep -n  'util_tag_layout_verify' src/ir/descr_tags.inc -> 1 hit, the prose header that names it as the guard
```

It is not broken. Run it by hand and it passes in 0.05s over 13 checks, offline, with no build:

```
GATE PASS   (rc=0, 0.06/0.05/0.05s over three runs)
```

So the file that declares the descriptor tag layout points at a guard that has not run in any automated
context since the layout moved. `src/contracts/` → `src/ir/` (2026-08-28) is where the wiring was lost: the
digest-level record of that rename already exists, and this is a second casualty of it that nobody counted.

## Why it matters, measured rather than argued

This is not a hypothetical. The reason it surfaced is that a tag needed a **human ruling instead of a gate**.

`DT_BOOL = 0x88` was added for Raku (ceo CEO-654). Deciding which coercion sites had to learn the new tag
was done by reading code and asking the ceo twice (CEO-654, then CEO-656 granting `to_real`'s
`case DT_BOOL` and `to_cstring`'s `DT_BOOL -> True/False`). **That is what a dead guard costs**: the question
"does this tag behave correctly under every inline predicate and every coercion" had to be answered by
correspondence, over two sittings, because the instrument that answers part of it mechanically was not running.

⭐ **The general form, which is the reusable half:** a guard named in prose by the file it guards reads, to
every subsequent seat, exactly like a guard that runs. Nothing about `descr_tags.inc`'s header is false — the
script exists, it does what the header says, and it passes. The only untrue thing is an implication nobody
wrote down: that something invokes it. **A capability nobody exercises is not a capability anybody has**, and
the sentence naming it is what stops anyone from checking.

This is the same class as `test_gate_parser_generated_files_in_sync.sh`'s own note — the regen path sat dead
ten days without a board going red — and it was found the same way: by needing the thing, not by auditing for it.

## The cure, landed with this FINDING

`scripts/util_tag_layout_verify.py` is now an arm of **`make preflight`** (declared in
`scripts/preflight_arms.txt`, which is that target's population of record). It meets all four membership
clauses: seconds-cheap (0.05s measured three times, against a 0.5s bar), hermetic, **needs no build**, and is
not a live postoffice read. Preflight goes 33 arms → **34 arms, 0 red**, and
`test_gate_preflight_arms_stay_cheap.sh` re-passes at `GATE PASS(0) … examined 34`, total 5.68s.

**FAILED ONCE, PASSED ONCE** (instrument law), on the real subject rather than a mock:

| arm | action | result |
|---|---|---|
| drift | `DT_BOOL 0x88` → `0x89` in `descr_tags.inc` | `rc=1`, `mismatched=['DT_BOOL']`, `GATE FAIL: ['descr.h == descr_tags.inc']` |
| restore | file restored byte-for-byte (`git diff --stat` empty) | `rc=0` |

The drift it caught is precisely the drift that would have made the CEO-654/656 correspondence unnecessary
to conduct by hand — the guard names the mismatched tag, which is the one fact the reader needs.

## What this FINDING does NOT claim

- It does **not** claim the guard would have answered the coercion question. It checks tag *layout* — the
  inline predicates and `descr.h` ↔ `descr_tags.inc` agreement — not whether every coercion function has an
  arm for a new tag. Those are different questions and the second one is still unguarded; it is the subject
  of hq_T's open ask to the ceo (three further coercion sites: `is_numeric_like` `core.c:981`,
  `to_int_slow` `core.c`, `rt_concat_parts_d` `pattern_match.c:923`).
- It does **not** claim anyone was careless. The rename moved a directory; the Makefile had no rule naming
  this script, so nothing could break and nothing could warn.

## Reproduce

```bash
cd SCRIP
grep -rn 'util_tag_layout_verify' Makefile scripts/    # before this landing: nothing
python3 scripts/util_tag_layout_verify.py; echo rc=$?  # GATE PASS, rc=0, ~0.05s
make preflight                                         # 34 arm(s), 0 red
bash scripts/test_gate_preflight_arms_stay_cheap.sh    # GATE PASS(0), examined 34
```
