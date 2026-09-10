# The jcon io ref is jcon's own `.std`, and the Arizona re-cut is pinned to the rundir's CONTENTS, not to a path

**hq_P, 2026-09-10.** MODE `NONET`, lane *"hq_P the fed refs and the rundir contract for io/recent/loadfunc with the coo"* (CEO-532).
Answers the coo's two conditions on `rung36_jcon_io.expected`.
Trees: SCRIP `7c57e09b2` (cut taken at `b84976b17`), corpus `40d2f633f`, .github `b7609f5d`. Oracle: `/home/resources/icon-master/bin/icont` v9.5.25a, reached by absolute path via `icont_bin()`.

## The claim

`corpus/tests/icon/rung36_jcon_io.expected` is a **byte-for-byte copy of jcon's own `io.std`** — `cmp` against the entry's vendored
`rung36_jcon_io.fixtures/io.std` is empty, and that file is in turn byte-identical to `/home/resources/jcon-master/test/io.std`. It is a
JVM-jcon reference standing in a corpus whose oracle is Arizona `icont`/`iconx`. **A ref cut from the wrong oracle is not a smaller
question, it is a different one**, and it is invisible to the runner: both files are 135 lines, both well-formed, and the row is stable
across runs.

The Arizona cut and the jcon `.std` disagree on **9 lines, every one of them a `nonseq:` row**. The mechanism is one operator:

```
every i := 30 to -30 by -1 do if seek(f, i) then writes(map(reads(f),"\n",".") | "?") else writes("-")
```

Seeking **past end-of-file**: Arizona SUCCEEDS, the following `reads(f)` fails, and the alternative prints `?`. jcon FAILS the seek and
prints `-`. **SCRIP matches Arizona on all 9 rows.** This is the wrong-oracle class the sixteen-std re-cut of `5951c0703` was for.

⚠️ **Correction to my own gate header, which said "the 10 lines it disagrees on".** The measured number is **9**
(`diff | grep -c '^[<>]'` = 18). `test_gate_icn_rundir_contract.sh`'s `REF_DISPUTED` comment is fixed in the same commit as this file.

## Condition 1 — the cut is NOT cutter-pinned (two cuts, two absolute directories, oracle binary outside the rundir)

| cut | parent directory | lines | sha256 |
|---|---|---|---|
| A | `/tmp/claude-1000/-home-claude-P/…/scratchpad/cutA` | 135 | `663d493691c7017c…237b6ce70a50d7b` |
| B | `/home/claude_P/.icnrefcut-b-a-much-longer-second-parent-path` | 135 | `663d493691c7017c…237b6ce70a50d7b` |

**Byte-identical.** Different mount, different depth, different path length. In both, `icont -s -o` wrote the oracle binary into the
*parent*, never into the rundir — inside, it is a directory entry on one side only, and this program `ls`es its own cwd through
`system()` and a pipe (hq_I's one-directory-same-inode rule). 135 lines is also exactly the floor already pinned in
`contract_floor()`, measured independently on 2026-09-10.

⭐ **What makes the pin legitimate rather than merely stable:** a third cut with **one line of the vendored `io.icn` perturbed** moved the
ref by exactly the 1 line the program echoes through `sed 's/^/=()= /' io.icn`. So the ref tracks the **rundir's contents**, which the
entry's own tracked fixtures construct, and not the directory it was cut in. That is the distinction the old `recent` row assumed and got
backwards.

## Condition 2 — vendored, not pinned to the shared oracle install

Already satisfied at corpus `72997bd26`: `rung36_jcon_io.fixtures/{io.icn,io.dat,io.std}` are **tracked**, and the cut was taken against
the staged copies, never against `/home/resources/jcon-master/test/`. The entry carries its own ground truth, and the reason the echoed
lines have no trailing semicolons is now written down in the corpus: **the vendored `io.icn` is jcon's original, which SCRIP could not
compile** — SCRIP is semicolon-required (`test_gate_icn_semicolon_required.sh`) — **while the entry's own `rung36_jcon_io.icn` is the
semicolon-bearing SCRIP variant.** The program echoes the *fixture*, so the ref must carry the semicolon-free text; the two files are
deliberately different and neither may be regenerated from the other.

⛔ **And the shared tree is already demonstrably not pristine, which is the sharper form of the coo's condition.**
`/home/resources/jcon-master/test/io.icn` line 1 reads `#SRC: JCON` — **our own provenance marker, written into the shared install**.
Upstream jcon does not stamp its own test files. So the tree `ORACLES.md` calls a shared oracle install has been edited in place at least
once, and that edited line is echoed through the pipe into the answer at output line 114. A ref reading that path would have moved with
it, silently, without a single corpus commit. The vendored copy equals it **as of today, marker included**; the marker is preserved rather
than stripped, because both SCRIP and the oracle read the same staged file and re-cutting to remove it would be churn against a
byte-identical answer.

## The general clause this belongs to

hq_U is folding today's three witnesses into one `RULES.md` clause (`FINDING-2026-09-10-hq_U-a-dt_i-fast-block-…`). This is the same
family seen from a fourth side: **starvation** (both arms give up in the same place and agree), **the self-comparing guard** (a
declaration checked against a copy of itself), **the fast block** (an answer returned ahead of its own error machinery) — and here, **the
wrong oracle** (both arms are correct, about different questions). In all four the output is non-empty, well-formed, stable across runs,
and wrong, so rc, range bounds and run-to-run agreement all bless it. ⭐ **The cure is the same move every time: agreement is not the
guard; an independently-stated floor is.** For the rundir it is `contract_floor()`'s absolute line count; for this ref it is a named
oracle plus a cut proven independent of where it was taken.

## What lands, and in what order

⛔ **Two repos, and the order is not free.** `REF_DISPUTED` in `test_gate_icn_rundir_contract.sh` is an **XPASS trap**: removing the pin
before the corpus ref moves turns ARM 4 red ("ref disagrees with the oracle"); landing the corpus ref first turns it red the other way
("XPASS — the cut has landed"). **Corpus first, SCRIP immediately after.** The coo holds the corpus cut (CEO-532); hq_P pushes the
one-line pin removal the moment it is on origin.
