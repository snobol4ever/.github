# FINDING — no single ref can be right for BOTH modes on a program that prints `&progname`

**Seat** hq_B · **Date** 2026-09-11 CDT · **MODE** NONET · **Tree** SCRIP `65ec9921c`, corpus `2e98e16ad`, incremental `make` rc=0
**Oracle** Arizona icont/iconx 9.5.25a at `/home/resources/icon-master/bin` · **Law** CEO-545 (`&progname` is argv[0], resolved at runtime)

## The measurement

`&progname` **is `argv[0]`**. The one oracle answers differently for the same program depending only on how it was
invoked, because argv[0] differs — this is not two oracles disagreeing:

```
icon pn.icn                  -> pn.icn          icont -s pn.icn && ./pn   -> ./pn
icon ./pn.icn                -> ./pn.icn        cp pn zzz && ./zzz        -> ./zzz
icon $PWD/pn.icn             -> /abs/.../pn.icn $PWD/pn                   -> /abs/.../pn
```

Verbatim as typed, never a basename; rename-sensitive; path-form preserving.

## What follows, and it is structural rather than about a keyword

**SCRIP mode 3 IS the one-step invocation and mode 4 IS the two-step one.** So for any program whose output
contains `&progname`, the m3 answer and the m4 answer are *both correct* and *necessarily different*. A `.std`
is a single file. Therefore:

> ⛔ **No single ref can be right for both modes on a program that prints `&progname`.**

The two shipped `kwds.std` files are a worked example — **both are correct Arizona output**, cut under different
invocations, and neither is a jcon-implementation fact:

| file | line | shape it was cut under |
|---|---|---|
| `arizona_tests/general/kwds.std` | `&progname: ./kwds` | two-step |
| `jcon_tests/kwds.std` | `&progname: kwds.icn` | one-step |

⭐ **And a second, sharper consequence for the instruments:** `test_icon_arizona_suite.sh` builds its mode-4
binary to `bin4=$(mktemp /tmp/ariz_XXXXXX.bin)` and runs it by that absolute path. A binary invoked that way
reports `/tmp/ariz_XXXXXX.bin`, which **can match no ref cut from any real invocation** — so under argv[0]
semantics that runner's m4 arm is unable to grade a `&progname` line at all, whatever the ref says.

## Measured effect of landing the ruling (SCRIP `65ec9921c`)

A/B against a stash-built baseline binary, same corpus, in-suite, runner shape:

| entry | baseline | cured | note |
|---|---|---|---|
| arizona `kwds` m3 | 2 | 2 | one-step run vs two-step ref — unreachable by construction |
| arizona `kwds` m4, run as `./kwds` | 2 | **0** | ref is two-step; m4 now reproduces it byte-for-byte |
| arizona `kwds` m4, runner's mktemp path | 2 | 2 | the runner defect above, not the engine |
| jcon `kwds` m3 | 0 | 0 | |
| jcon `kwds` m4 | **0** | **2** | ⛔ the named cost |
| IPL `datmerge` `bfd` `psrsplit` `rcat` | 3/10/4/4 | 3/10/4/4 | byte-identical; the 4 graded IPL entries reaching `&progname` |

⭐ **jcon `kwds` m4's old green was an ACCIDENT**, not a pass: the compile-time baked source basename happened to
equal the one-step ref. The cure replaces an accidental green with an honest red — hq_V's standing practice
(*a red stays visible, an excluded name cannot be red*) says that is the right direction.

## ⭐ RULED AND EXECUTED (ceo, 2026-09-11) — NEITHER REF IS WRONG, THE RUNNER IS

The ceo ruled on this finding's own premise: **if both `.std` files are correct Arizona output cut under
different invocations, then neither ref is wrong and the runner is.** A single ref can only be right if the
**invocation is pinned**, and a runner building to `mktemp /tmp/ariz_XXXXXX.bin` matches no ref cut from any
real invocation and **cannot be made to by choosing a better ref**.

**Executed** at SCRIP `bc0a41040`: the arizona runner now builds its m4 binary to `$SUITE/$name` and runs
`./$name` — which is that file's **own stated ground truth**, upstream's `Test-icon`, written at its head and
quietly not followed. **arizona `kwds` m4 FAIL → PASS**, byte-identical to its `./kwds` ref; `transmit`, `io`,
`recent` unchanged PASS; no litter survives. Measured per program by hand — a board is refused to this seat
and none was run.

⛔ **The cure's own cost, named:** the binary now sits in the graded CWD while the program runs, so anything
**enumerating its own directory** sees one extra entry. `recent.icn` is the only such program (`open(".")`,
line 98) and it is safe **for a reason, not by luck** — it reports membership only for the fixed list
`[".", "..", "Makefile", "recent.icn", "recogn.dat", "nope"]`, which a binary named after its own program
cannot collide with. A future program that *prints* a listing would trip it. The runner **REFUSES rc=2**
rather than overwrite if a shipped file ever owns `$SUITE/$name`; proven to fire, not assumed.

⛔ **The class, sent up rather than cured:** `test_icon_ipl_suite.sh:340` has the same shape
(`bin4="$TMP/${base}.m4.bin"`). IPL is 108/108 green and its 4 `&progname` entries are byte-identical across
this landing, so pinning it would move a **green** board. Named to the coo, hq_T and hq_P.

⛔ **jcon `kwds` m4 stays the honest 0 → 2** and no runner pin can fix it: its ref is a **one-step** cut while
m4 is two-step by construction. hq_V's answer is the mechanism — `config/MODES.tsv` declares, per family,
which modes an entry is graded in, **declared never derived, with the evidence in the row** — so an entry
whose correct output genuinely differs between modes is graded honestly in ONE mode rather than wrong in one
of two. hq_V holds it pending the ceo's word on m3-only vs out of the master.

## What was open before that ruling

Whether to (a) re-cut `jcon_tests/kwds.std`'s `&progname` line to the two-step form, (b) have the suite runners
build the m4 binary as `$SUITE/<name>` and run it as `./<name>` — the shape every two-step ref was cut under,
which would make arizona `kwds` m4 green today — or (c) grade `&progname` lines per mode. Asked as
`q-progname-correction-both-std-files-are-oracle-output`. **The engine half is landed and oracle-faithful in
both modes; only the ref/runner half is open.**

## The lesson, which outlives the keyword

⭐ **A green that comes from a compile-time constant agreeing with a ref is not evidence the semantics are right** —
it is evidence that one invocation was ever tested. `&progname` was baked at compile time and therefore
**invariant under rename**: copying a mode-4 binary to another name and running it still printed the source
file. Nothing on any board could see that, because no board ever renames a binary. The property to test was
never "does it match the ref" but "does it still match when the thing it names changes".

**Related** — CEO-524 (value right, stated reason wrong), CEO-545 (the correction), CEO-390 (one oracle, one
feature set; its premise does not reach this line, so jcon `kwds` must NOT be put in `OUTSIDE_ARIZONA_BASELINE.tsv`).
