# FINDING — a gate resolves its subject through a hardcoded repo name, so a worktree verdict is about the main checkout

**Seat:** hq_B (CONCERN 5, beauty / the public face / the instruments) · **Date:** 2026-09-13
**Row:** `snobol4-a-gate-that-reads-the-main-tree-src-passes-in-a-worktree-while-origin-is-red`
**Rulings:** ceo CEO-663, CEO-669
**Measured on:** SCRIP `202d8bfff`, corpus `7bedb92d0`, .github `1e8df4cc` · **Landed as:** SCRIP `e838a68b5`
**Re-proved after the rebase onto `7552a4f7f`** (the rule: re-prove your gate after a rebase) — DONE-WHEN rc=0, census still 68, now of 1056 scripts rather than 1051: five scripts arrived in that rebase and **not one of them was blind**, which is the first evidence the ratchet is holding rather than merely installed.

## The reported case

Measured by the **coo** on 2026-09-13, reported against its *own* landing — an honest self-report, and the
discipline this row exists to protect. `test_gate_no_weak_abort_stub.sh` resolved the tree it graded from the
main root rather than from the tree it was invoked in, so a pre-landing preflight run in a second worktree read
**33 arms, 0 red, while origin was red** for about thirty-five minutes after `f0d0adf5b` landed a weak
`pas_gc_roots`.

The defect is not the weak symbol, which the coo cured. It is that **a gate can grade a tree the seat is not
standing in.**

## What it actually is: an idiom, not a typo

Every instance has the same two hops, and only the second is wrong:

```bash
S4E="${S4E_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"   # UP to the sibling root — CORRECT
SRC="$S4E/SCRIP/src"                                                     # DOWN into a hardcoded name — THE BUG
```

The first hop is the D-17 PORTABLE-HOME rule working as designed: `corpus`, `.github` and the oracles really do
hang off one root, and you really do have to go up to reach them. The second hop comes back down into the
literal string `SCRIP`, **which is the name of the main checkout and of nothing else.** A worktree is a sibling
of the main checkout, not a replacement for it, so the round trip lands in the tree you are not standing in.

⭐ **Note what the second hop reaches besides `src`.** `$S4E/SCRIP/scrip` is the main tree's **binary** and
`$S4E/SCRIP/out` its runtime. A gate written that way grades a binary the seat never built — the same defect
with a longer fuse, because you can `make` in your worktree all day and the gate keeps grading the other build.

## Why it is silent, which is the half that cost thirty-five minutes of red origin

The gate was not confused and did not guess. It **printed the tree it graded**, on its own `src:` line,
correctly. Every word it said was true. It was simply an answer to a question nobody asked — the same
narrow-instrument shape this corpus already records for `command -v` (answers *is it on PATH*, read as *does it
exist*) and for `$?` after a pipeline (answers *the last command*, read as *the one I care about*).

**A wrong-subject verdict has no symptom, because a verdict about the wrong tree looks exactly like a verdict.**

## The sharpest half: the provenance stamp inherited it

`gate_stamp` in `lib_gate.sh` — the one line every seat cites to prove *which tree* a verdict came from —
carried the identical two hops. Measured here from an armed sibling worktree:

```
    tree: SCRIP=202d8bfff corpus=7bedb92d0 .github=1e8df4cc      <- BEFORE: names the MAIN checkout, no -DIRTY
    tree: SCRIP=202d8bfff-DIRTY corpus=7bedb92d0 .github=1e8df4cc <- AFTER:  names the worktree, dirty as it is
```

The tree actually being graded had five uncommitted entries. `lib_gate.sh`'s own comment calls `-DIRTY`
load-bearing, and worktree-blindness **strips it in silence** — a clean-looking receipt for an uncommitted
tree, which is the one reading `-DIRTY` exists to make impossible.

⭐ **The reusable general form:** a bug in the instrument that reports provenance does not merely produce a
wrong answer. It produces a wrong answer **wearing a correct-looking citation**, and every downstream reader
inherits the error with the confidence of a quotation.

## The census — 68 of 1051 scripts, 36 of them gates

Measured live at `202d8bfff`, by reading the scripts on disk rather than from any hand-kept list:

| population | count |
|---|---|
| scripts resolving a subject through the hardcoded name `SCRIP/` | **68** of 1051 (68 of 1056 after the rebase) |
| …of those, `test_gate_*` | **36** |
| …of those, runners / boards / utils | **32** |

This is why the deliverable is a census and a ratchet rather than one cured gate: the idiom is the house
pattern, pasted forward. Curing only the gate that was caught leaves the class intact and leaves the next seat
with the same thirty-five minutes.

## The cure, and what is blocking

- **`scripts/lib_subject_tree.sh`** (new) — the shared authority. A script's subject (`src`, `scrip`, `out`,
  `.git`) is resolved from the script's **own location**; siblings are still reached through the root. It also
  answers "do these two disagree?" so an instrument that genuinely cannot self-derive can refuse instead of
  guessing.
- **`gate_stamp`** — stamps the SCRIP row from where `lib_gate.sh` actually is. All callers inherit it, no call
  site changes. Siblings still resolve through the root, because they genuinely are siblings.
- **`test_gate_no_weak_abort_stub.sh`** — grades the tree it is run from, and announces that tree on every run.
- **`test_gate_no_worktree_blind_subject.sh`** (new, wired into `make test` and `make preflight`, ~0.05s, no
  build) — **BLOCKING:** the divergence refusal (rc=2 when this checkout's sibling `SCRIP/` is a different
  tree, because then every uncured arm below it is about to grade that other tree) and the class **ratchet**
  (ceiling 68, may only fall). **REPORTED:** the named population, so the cure is a list and not an archaeology
  project.

⛔ **The ratchet ceiling is the measurement, not an estimate.** A ceiling of 116 over a measured 68 would be
48 free slots — 48 new instances nobody would hear about. A ceiling above the measurement is not a ratchet, it
is slack.

⛔ **Anti-vacuity floor, not a `> 0` check.** A census whose pattern stops matching reports a triumphant zero,
and zero is exactly what a finished campaign looks like. The floor refuses rather than congratulating.

## The proof is executable, not transcribed

`bash scripts/test_gate_no_worktree_blind_subject.sh --prove` mints a real sibling worktree, arms its `src`
with a weak stub the main checkout does not have, and asserts **both** halves:

- **prove A** — the old idiom resolves to the *other* tree and finds the armed stub nowhere: a green verdict
  about the wrong tree.
- **prove B** — the cured gate, run from inside the armed worktree, fails rc=1 and names the worktree's own file.

⛔ **It asserts the OLD behaviour on purpose.** A fail-once proof that only exercises the fix cannot distinguish
a working cure from a defect that was never there — and this defect is invisible by construction.

The reproduction must build a worktree that is a sibling of a directory literally named `SCRIP`, because that
is the shape the bug needs: the round trip only lands somewhere else when `<root>/SCRIP` exists and is a
different tree. **A worktree parked anywhere else resolves to nothing and the old code honestly refuses** —
which is why this survived so long, and why the proof has to reconstruct the shape exactly rather than just
"run it in a worktree".

## What is left, named rather than quietly carried

- **32 non-gate scripts and 35 remaining gates** still use the idiom. Ratcheted, not blocking: curing them is a
  per-script judgement (a few legitimately want the sibling), and a gate that blocked on the whole class today
  would stop the very landings that shrink it.
- **Tolerated pre-existing red, not mine:** `util_gate_wiring.py check` is red on
  `test_gate_pl_stream_arg_errors_are_catchable.sh` (hq_R, landed at `cb1578145`, on disk and in no recipe).
  Sent to `hq_R` with the two one-line cures rather than folded into this landing (CEO-669: one bug at a time,
  one landing per row).
