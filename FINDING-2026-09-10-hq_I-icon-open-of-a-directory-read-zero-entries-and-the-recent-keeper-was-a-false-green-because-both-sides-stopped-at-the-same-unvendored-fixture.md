# Icon `open(<directory>)` read ZERO entries, and `rung36_jcon_recent` was a false green because both sides stopped at the same un-vendored fixture

**hq_I, 2026-09-10.** SCRIP at the commit landing this, corpus `91160ee6a`+, `RT_OPT=-O0`, graded on an
incremental `make`. Raised under **CEO-516 item 2** (absorb `misc`/`sorting`/`struct`, hold `io`/`others`/
`recent` for fed refs and report the count that changes verdict).

## The verdict-change count the ruling asked for: 1 of 3

| held witness | dependency | starved | fed | verdict change |
|---|---|---|---|---|
| `rung36_jcon_io` | stdin | 116 lines | 124 lines | none — PASS both ways, **+8 lines of real coverage** |
| `rung36_jcon_others` | stdin | 130 lines | 183 lines | none — PASS both ways, **+53 lines of real coverage** |
| `rung36_jcon_recent` | **a fixture in cwd, not stdin** | 313 lines | 443 lines | ⛔ **PASS → FAIL → cured → PASS** |

`io` and `others` were already right; feeding them only widens what they test. **`recent` is the one that
changed verdict**, and it changed twice: it was a false green, feeding it made it a true red, and the red
turned out to be a real defect which is now cured and gated.

## `recent` was the purest form of the starvation class

Graded the way the corpus grades it today — no `recent.dat`, stdin `/dev/null` — the oracle and SCRIP are
**byte-identical at 313 lines**, and the last line of both is `can't open recent.dat`. Agreeing about where
you both gave up is not agreement about the program. With the fixture present the oracle answers 443 lines.

⛔ **My own earlier claim was wrong in the direction that mattered.** `FINDING-…-three-of-the-six-rung36-keepers-pass-only-because-the-oracle-was-starved…`
called `recent.dat` *"not in the corpus at all — that one is a missing fixture, not a re-cut"*. True about the
corpus, and it reads as **unavailable**, which is what parked it. The file exists upstream at
`/home/resources/jcon-master/test/recent.dat` (1213 bytes), and so do `io.dat` and `others.dat`. "Not
vendored" and "does not exist" are one `ls` apart and they license opposite decisions.

⭐ **And the invocation was recoverable too, from jcon's own driver rather than by inference.**
`/home/resources/jcon-master/test/runtest` says:

```sh
if [ -r $BASE.dat ]; then ./$BASE $BASE.dat <$BASE.dat >$BASE.out
else ./$BASE </dev/null >$BASE.out ; fi
```

So a `.dat` is fed **as `argv[1]` and on stdin, both** — which is Lon's 2026-09-08 20:22 sidecar order
(argv *and* an input file) already specified upstream, for every jcon entry that has a `.dat`. I recovered
`io`'s stdin from its `.expected` before finding this; the driver is the better authority and it was there
the whole time.

## The defect the fixture exposed, in two parts

Fed, `recent` diverged. The class is `open(<directory>)`, and it has two independent halves:

1. **`open(".")` SUCCEEDED and yielded NOTHING.** `fopen()` on a directory succeeds on Linux, so `open()`
   returned a healthy handle with `type(f) == "file"` and every read off it failed. No diagnostic anywhere —
   the program simply found no files. A probe read **0 entries where iconx reads 5**.
2. **`reads(f, n)` on a directory returns ONE ENTRY truncated to `n`, not `n` raw bytes.** My first cure
   snapshotted the entries into a `tmpfile()`, which fixed (1) and left (2) wrong: `reads(f,25)` then spanned
   entry boundaries and returned `"Makefile\nrecent.dat\nrecen"`, so a name-membership test found 3 of 5
   names. `recent` reads in a `read`/`!f`/`reads` rotation and is exactly what caught it — and the upstream
   author says so in a comment, `# assumes no name longer than 25`, which only makes sense if `reads()`
   returns one name.

⭐ **Part (2) is invisible to part (1)'s witness**, which is why the gate has two arms and why each was
negative-tested separately rather than together.

## The measurement trap I walked into and had to back out of

`recent` lists its own cwd with a byte-offset-sensitive read, and **readdir order is per-directory**. Grading
the oracle in one temp directory against SCRIP in another reported **3 missing lines that were not a defect
at all** — two directories holding the same *names* can enumerate in a different *order*. The fix is to run
every arm in **one directory, same inode**, with the oracle's compiled binary kept **outside** it (it would
otherwise be an entry on one side only — the same confound wearing a smaller face). Only after that did the
remaining difference turn out to be real, and it was part (2).

⭐ **The general form:** when a program's output depends on its environment, an oracle diff measures the
difference in environments *and reports it as a difference in programs*. The two arms must differ in exactly
one thing — the implementation.

## Why the cure is its own translation unit

`<dirent.h>` declares an enum `DT_UNKNOWN..DT_WHT`, and SCRIP's descriptor tags are an enum of the **same
`DT_*` names**, so any file including both fails with `redeclaration of enumerator 'DT_BLK'`. It cannot be
worked around with `#undef` because both are enumerators, not macros. `src/runtime/rt_dir_snapshot.c` isolates
`dirent.h` behind `FILE *rt_dir_snapshot(const char *)`; the snapshot is taken at `open()` time into a
`tmpfile()`, so `read`/`!f`/`where`/`seek`/`close` all work through the ordinary `FILE*` path. **No new global
variable**: directory handles are marked in the existing `fh_type[]` array as `'d'`, and only `reads()` reads
that mark. ⛔ **`open` is implemented TWICE** in `by_name_dispatch.c` — a by-name path and a `BID_open`
fast path — and Icon uses the second. Curing the first alone changed nothing observable, which is why the
probe still read 0 entries after a build that had compiled the fix.

## Results

- `recent` **PASSES both modes fed, byte-identical to a live icont cut at 443 lines**, in a shared-inode cwd.
- `io` and `others` **PASS both modes fed**, byte-identical to live icont cuts (124 and 183 lines). `others`'
  shipped `.expected` **equals the fed icont cut exactly**, an independent corroboration that the fed run is
  the right expectation; `io`'s differs by 35 lines and its ref must be the icont cut, not jcon's `.std`.
- `misc`, `sorting`, `struct` re-verified byte-identical to live iconx in both modes after the runtime change;
  absorbed by hq_V at corpus `a5c202f58` per CEO-452.
- `test_gate_icn_open_directory_reads_entries.sh` — 1.19s, 4 graded runs, **wired into `make test` in the
  same landing as the gate** and adopted (wired 164 → 165). Negative-tested both parts separately.
