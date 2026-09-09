# The Icon ladder discards stderr, so every &trace rung is graded on stdout alone and CANNOT fail for its own reason

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-09 · **Lane:** the &trace class (Arizona M-Z)
**Routing:** hq_T (the instruments, the test standard) · hq_V (the ONE WRITER of the Icon master pair) · ceo
**Build graded on:** incremental `make`. `RT_OPT` = `-O0`. Measured on SCRIP `17ac1bc39`, corpus `b191d461f`.

## The claim

`lib_ladder.sh` runs every witness in both modes with **stderr discarded**:

```sh
r3=$( ( timeout "$T" "$SCRIP" --run "$src" <"$stdin_src" >"$W/$o.m3.out" 2>/dev/null; echo $? ) 2>/dev/null )   # :108
r4=$( ( timeout "$T" "$W/$o.bin"            <"$stdin_src" >"$W/$o.m4.out" 2>/dev/null; echo $? ) 2>/dev/null )   # :113
```

Icon's `&trace` writes **exclusively to stderr** (`core.c`, `trace_print_icon` -> `fprintf(stderr, ...)`).
Therefore a ladder rung whose entire observable is trace output is compared against a ref that contains none of it.
Corroborating census: `corpus/tests/icon/ALL.ref` contains **zero** trace-shaped lines
(`grep -c "^.*\.icn *: *[0-9]" ALL.ref` -> 0).

## The measured false green

`procedure_write_264` = `ladder__rung03_suspend_trace_reports_suspended_resumed_and_failed`, minted by hq_V before the
cure per CEO-445 to pin that a generator under `&trace` reports **suspended / resumed / failed** behind a depth bar.

Its ref, in full, is one line:

```
A:end
```

...which is the program's `write("A:end")`. The rung **PASSES on a clean tree**. The behaviour it exists to pin is
entirely absent — measured directly on the equivalent standalone witness, oracle `iconx` 9.5.25a on the left:

```
ORACLE                              SCRIP (clean tree)
g0.icn : 3  | gen()                 g0.icn : 3  gen()
g0.icn : 6  | gen suspended 1       (nothing)
g0.icn : 3  | gen resumed           (nothing)
g0.icn : 7  | gen suspended 2       (nothing)
g0.icn : 3  | gen resumed           (nothing)
g0.icn : 8  | gen failed            (nothing)
g0.icn : 4  main failed             g0.icn : 4  main failed
```

Six of seven lines missing, and the rung is GREEN.

## Scope

Three `&trace` rungs exist in the Icon master (`grep -o 'ladder__rung[0-9]*_[a-z_]*trace[a-z_]*' ALL.csv | sort -u`):

| rung | can it fail for its own reason? |
|---|---|
| `ladder__rung03_suspend_trace_reports_suspended_resumed_and_failed` | **NO** — green today, pins nothing |
| `ladder__rung42_kw_trace_level` | **YES** — see the correction below; its name misleads, its body does not |
| `ladder__rung03_suspend_trace_of_a_generator_call_with_an_argument` | only by accident: it SIGSEGVs, and rc=139 is compared |

⛔ **CORRECTION, measured by hq_V on SCRIP `f48a3f0c7` + corpus `23638085f`, and it narrows this finding:** the first
version of this table listed `ladder__rung42_kw_trace_level` as the same shape as rung03. **It is not.** Its witness
writes `&level` — the call depth — to **stdout**, and its ref is `1`/`2`/`3`: a real assertion, really graded. Its
NAME contains "trace"; its BODY tests a different keyword. ⭐ I reached it by grepping rung names for `trace` and read
a name as a body — the same narrow-instrument move this finding is about, committed inside the finding itself. The
defensible claim is the corpus-wide one: `ALL.ref` contains **zero** trace-shaped lines, so **no** rung asserts on
trace output — which is a statement about the refs, arrived at by measuring refs, not by reading names.

The third one is the tell. It is red **not because its trace text is wrong** but because it crashes; cure the crash
while leaving the trace text wrong and **it goes green too**.

⭐ The Arizona suite does NOT have this defect — `test_icon_arizona_suite.sh:153,176` runs with `2>&1` and captures
stderr, which is why `tracer.std` carries all 85 trace lines and why `tracer` is honestly graded (CRASH today). So the
instrument that grades the *packages* is right and the instrument that grades the *ladder* is wrong, and the ladder is
the one the rungs are minted into.

## Why this matters right now

Rungs are being minted **before** cures by design (CEO-445), so a rung's job is to be RED until the cure lands. A rung
that cannot go red is not a slow rung, it is **an entry in the denominator that votes yes unconditionally** — and the
board it feeds is an announcement board dated 09-10.

## The reusable lesson

⭐ **A test grades the stream it captures, not the behaviour it is named after.** `2>/dev/null` is invisible in every
rung name, every CSV row, every board line and every ref; nothing about `ladder__rung03_suspend_trace_reports_...`
announces that the runner threw away the only stream it could have been reporting on. This is the same
narrow-instrument family the digest already records for `command -v` (answers *is it on PATH*, read as *does it
exist*) and `$?` after a pipeline (answers about the last stage) — an instrument answering a narrower question than
the one asked, and never saying so.

⭐ The cheap general test, and it is one line per runner: **for each stream a witness can write to, ask whether the
runner captures it.** `grep -n '2>' scripts/lib_*.sh scripts/test_*.sh` is a whole-instrument census that takes a
second and would have caught this at mint.

⛔ **But the census LOCATES; it does not JUDGE — hq_T's refinement, and it corrects the instinct this paragraph
invites.** `lib_ladder.sh` holds **seven** `2>/dev/null` occurrences and only the **two on the graded runs**
(`:108`, `:113`) are the defect. The rest sit on the `as` and `gcc` build steps, where suppressing stderr is
*correct*: fold those into the graded stream and a build failure becomes a wall of assembler text inside a diff.
So the cure is a surgical two-line change, **never a flag sweep**. Each redirect found by the census has to be asked
a second question — *which stream is this suppressing, and for whose benefit?* — because a graded run and a build
step want opposite answers from identical syntax.

## Two further facts, measured by hq_V, that change what the cure must do

1. **The mint tool is stdout-only too.** `util_add_ladder_witness.py:155` keeps `p.stdout` alone, so a stderr-bearing
   witness **cannot be minted today even if the runner grew eyes**. The runner and the mint tool are therefore ONE
   landing, not two — fixing `lib_ladder.sh` alone would leave the corpus unable to express the rung.
2. **The witness cannot be re-cut around the instrument.** The obvious escape — have the program itself put the
   assertion on stdout — does not exist: the oracle refuses assignment to `&errout` with *Run-time error 111,
   variable expected*.
3. **A constraint on any re-cut ref.** The trace prefix is the source file name in a fixed 13-character field
   truncated **from the left**, so the same program reads `t264.icn     :    8  |` under one basename and
   `nd_failed.icn:    8  |` under the origin-length name the ladder extracts to. **A ref cut under any basename but
   the exact one the runner materialises can never match** — which makes this a re-cut that has to be done through
   the runner, not beside it.

## Owed

Not mine to land — the ladder body and the test standard are hq_T's, the master pair is hq_V's. Two candidate cures,
and they are not equivalent:

1. Capture stderr into the graded stream (`2>&1`), matching what the Arizona runner already does, and **re-cut every
   affected ref from icont**. This changes the ref of every rung whose program writes anything to stderr — including
   error-message rungs — so it is a re-cut of the master, not a flag flip.
2. Grade stderr as a **separate** companion stream with its own ref, leaving stdout refs untouched.

⛔ **BOTH of the candidates above were superseded within the hour, and the reason is a fact this very session
demonstrated by accident.** hq_T first took (1) — plain `2>&1` matching Arizona — then **withdrew it** and routed a
correction to CEO-457, taking a **per-entry `ALL.err` sidecar** instead. hq_V's basename constraint is what killed the
simpler shape: because the trace prefix is a **13-character field truncated from the LEFT**, a folded-in ref pins
*the basename the harness happened to materialise*, and ladder origins run 40–60 characters through
`master_extract_origin` — so the merged ref would be a **self-pin on a temp filename**, a worse instrument than the one
it replaces, rotting the first time anyone renames an origin.

⭐ I hit exactly this live, minutes earlier and without recognising it, while writing the DONE-WHEN for an unrelated
row: my acceptance test built its oracle from an absolute path and the diff came back
`ZG84x/nm3.icn` vs `nm3.icn` — a red that was **entirely the filename field** and nothing to do with the property
under test. I fixed my harness and moved on. The same fact, met as a nuisance in one place and as a design constraint
in another, is what decides between the two cures here.

The sidecar is additive: it leaves all 886 existing refs byte-for-byte, keeps an error-message rung and a trace rung
from having to share one ref, and mirrors the `ALL.in` sidecar Lon ordered on 09-08 — so it does not breach one-ref-
per-entry any more than `ALL.in` does. The ceo may still override; this paragraph records the withdrawal rather than
the first answer. hq_V adds two constraints on the re-cut, both
of which change what the rung must carry: a witness with an **unbounded** trace budget (`&trace := -1`) grades an
unbounded stream and cannot distinguish a tracer firing the right *lines* from one firing them the right *number* of
times, so the rungs get a **finite** budget plus a second entry that exhausts it mid-generator; and because a
generator exhausting spells `NAME failed` **identically** to a plain procedure failure, the six-line block must be
**one ref, never a line subset**, or an implementation emitting only the tail would match.

⛔ Whichever is chosen, the count that must be reported is **how many entries CHANGE VERDICT in either direction** —
the same discipline Lon's 09-08 sidecar order imposed, which found 62 refs cut from starved runs. A rung going red
under a fixed runner is the instrument starting to work, not a regression.
