# FINDING 2026-09-04 hq_B — a "permanent" icon compiler defect was a stray semicolon the real oracle refuses to compile

**Row:** `icon-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`
**Tree at measurement:** SCRIP `ae9ebfc20` · corpus `a0bc89d89` · oracle `/home/resources/icon-master/bin/icon`

## The recorded claim

`corpus/tests/icon/unresolved/KEEP.md` held five files as permanent residue:

> These 5 files stay loose, permanently, on purpose — they are NOT candidates for master absorption and
> never will be until the underlying SCRIP compiler defects they expose are fixed. […] these 5 disagree
> with the real oracle (m3 and m4 agree with *each other*, but not with ground truth), so no `.ref` was
> ever written […] each is a genuine scrip-vs-oracle output mismatch, real compiler defects.

## What is actually there

`global_test.icn` is two lines. Line 1 is `global counter, message, total;`.

The real Icon oracle **refuses to compile it**: `File t.icn; Line 1 # ";": invalid declaration`. SCRIP
accepts the trailing semicolon. A refusing oracle emits no stdout — so the comparison that was actually
performed was *SCRIP's three lines* against *nothing*, and it was recorded as a computed-output mismatch.

Delete that one byte and the two agree exactly:

```
$ icon global_test.icn      →  1 / hello / 42        (rc=0)
$ scrip global_test.icn     →  1 / hello / 42        (rc=0)
```

`capture-oracle-refs --lang icon` — which mints a `.ref` **only** when a live scrip run agrees with a live
oracle run in *both* m3 and m4 — then wrote the ref that "was never written", on the first try. Absorbed;
the master is 751 entries, FAIL=0 both modes.

## Why the file was wrong and nobody was careless

Nothing in the original procedure was skipped. The oracle was real, the run was live, m3 and m4 were both
checked, and the conclusion was recorded with its evidence. ⭐ **The instrument answered *did the oracle
produce matching output*, and the answer was read as *does SCRIP compute the wrong answer*.** Those differ
by exactly one case — the one where the oracle never ran — and that case is silent, because a compile
refusal and a wrong answer both arrive as "output does not match".

⛔ **The cheap discriminator, and it costs one line:** capture the oracle's **rc and stderr**, not just its
stdout. `rc=1` with `invalid declaration` on stderr is not a disagreement about semantics; it is the
oracle declining to participate. Any harness that files scrip-vs-oracle mismatches should refuse to
classify a mismatch at all when the oracle's own rc is non-zero.

## The sibling is NOT this class — re-measured, not assumed

`unresolved/generators.icn` sits in the same list and under the same sentence. It is a **real** defect: the
oracle compiles it fine (rc=0) and the two genuinely differ.

```
oracle:  2 3 5 7 11 13 17 19 23 29 31 37 41 43 47
scrip :  2
```

Filed as its own row. The point of measuring it separately is that "the recorded reason is wrong for one
file in this list" is not evidence about the other four, and a sweep that assumed otherwise would have
deleted a live defect witness.

## Also repaired, same class, same session

`corpus/tests/icon/meander.icn` (a `#SRC: V9SAM` sample) and its byte-identical twin
`samples/meander.icn` carried semicolons mechanically appended at three line ends, splitting
`if …; then …; else …` into fragments the oracle rejects (`Line 20 # "else": invalid expression`). With
those three bytes removed the oracle runs it and SCRIP m3 and m4 both reproduce its output byte-for-byte
(`aacccbccacbbcbacabcaabbbabaaa` for stdin `abc:3`).

⛔ Both meander copies remain **excluded, correctly**: they read stdin, and a loose pair with a stdin
sidecar is deferred by the builder until the stdin-sections format extension lands. They are now excluded
*with a reason and a valid oracle ref* rather than being invisible to the census — which is the whole
distinction the GOAL draws between an exclusion and a silent skip.

⭐ These sources are corpus data, not compiler evidence, and a mechanical edit pass damaged them into
looking like compiler evidence. The tell is generic: **a source our own tooling rewrote, which the
upstream oracle then refuses to parse, is a corpus defect until proven otherwise** — the oracle is the
one party in the loop that never edited the file.
