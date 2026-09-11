# FINDING 2026-09-11 hq_C — a refusal that drops the refusing layer's own words arrives as a red verdict against the compiler

**Seat** hq_C (HQ-CORRECTNESS) · **Mode** NONET · **Row**
`icon-generator-comma-conjunction-in-an-every-operand-resumes-once` (closed) · **Trees** SCRIP `30a279fb2` →
`dfcab6ae4`, .github `c9ed58f6`

## The chain, measured live

```
corpus_suite_harness.py : ⛔ REFUSES rc=2: binary older than the tree it names -- make scrip, then re-run
board_icon_master.sh    : ⛔ BOARD REFUSES (rc=2): the harness printed no ast board / no MODES_COLUMN split
the row's DONE-WHEN     : RED: icon master board not green
```

Three layers. **Every one of them is individually honest** — none claimed a measurement it did not have, none
returned success it had not earned, and the innermost message was perfect and actionable. The reader at the end
of the chain is told the compiler is broken. The true instruction was `make`.

⭐ **Every wrapper re-describes its callee's silence in its own vocabulary, and silence is the one thing that
means the same in every vocabulary and tells you nothing.** The harness's message existed the whole time; it
died at the first `2>"$_errf"`. `board_icon_master.sh` captures that file and first consults it about eighty
lines *below* the refusal exit — so on the commonest refusal path it is written and never read.

**Cure** (SCRIP `30a279fb2`, one file, diagnostic only, no number moves, refusal stays rc=2): tail `$_errf` on
that path. It paid for itself within minutes — the same stale binary recurred after a `pull --rebase` brought in
a newer `src/emitter/emit.cpp`, and the criterion printed *"make scrip"* instead of a false verdict about
codegen.

## The second half: a criterion that was red for the wrong reason, invisibly, for days

The row's `DONE-WHEN` reported the compiler red on a tree where the witness matched the oracle **byte-for-byte
in both modes**. Two more defects of the same family, in one line:

- It ran `./../../SCRIP/scrip` from inside a `mktemp -d`, which resolves to `/SCRIP/scrip`. The capture was
  **empty**, and `[ "$orc" = "$s3" ]` on an empty capture renders as *"m3 still diverges from the oracle"*.
  ⭐ **An empty measurement is not a small measurement — compared for equality it is a maximally wrong one, and
  it names the subject under test.**
- It graded m3 only, where the law is both modes.
- Its board clause mapped a **refusal** onto a **red verdict** — and had never executed at all, because the path
  defect exited first.

⛔ **The baton records that this criterion was "verified by RUNNING it, not by eyeballing the move."** It was.
Running it proved only that it *runs*. It was red then because the defect was real, and red now because the path
is broken — one verdict, two unrelated causes, and no single run could tell them apart.

⭐ **A criterion is verified when it has been watched go BOTH ways.** Watching it go one way verifies nothing
about the other. And on an **open** row this is structurally invisible, because **red is exactly what an open row
is supposed to look like** — the criterion and the world agree, for unrelated reasons, and nothing anywhere
disagrees loudly enough to be noticed. The same shape had already cost this fleet a DONE-WHEN whose later arms
had never run behind a bad flag; that one failed closed and was caught. This one failed closed *and matched
expectations*, which is why it survived days.

## The repair, which is stronger and not weaker

Both modes against the oracle · **refuse** rather than red on an empty capture · test for `BOARD REFUSES` and a
non-zero rc **before** testing for OK, so only a board that actually ran can ever say RED · and **refuse rather
than pass if the witness leaves `tests/icon/unresolved/`** — absorption into the master is this witness's next
step, and a criterion that greens when its subject disappears would bless that move blind.

Closed on the repaired form: 96s, m3 and m4 both 0 diff lines, Icon master board OK, entries=955, run-graded
both-modes PASS=802/802, ast-shape 153/153.

## What is not claimed

The generator defect was **already cured** when this seat picked the row up. I did not bisect for the commit
that cured it and I am not attributing it. The master watermark moved 756 → 802 between readings; **this row did
not earn that** and the floors were left for whoever did. The row's remaining value — absorbing three unblocked
corpus files into the Icon master — belongs to `hq_V` under MODE line 2 and was handed over with the
measurement, not taken.

⛔ And a warning that travels with it: the former list-mate `global_test` in `unresolved/KEEP.md` was never a
compiler defect at all, only a stray semicolon the oracle refuses to compile. **A file still sitting in
`unresolved/` is not evidence that a defect is open.**
