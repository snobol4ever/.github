# FINDING 2026-09-11 hq_I — two seats cured the Icon trace line cursor in parallel, and the emitter-side cure beat the runtime-side reconstruction

**Measured on** SCRIP `0e4539a65` · corpus `3708c8ab9` · incremental `make` · `RT_OPT=-O0` ·
box 2026-09-11 ~20:3x UTC · measurer hq_I.

⛔ **This FINDING replaces an earlier version of itself that claimed a cure of mine.** That cure is
NOT in the tree and never will be — it was superseded mid-sitting and I dropped it. What survives is
the comparison, which is the part worth keeping, plus two measurement traps.

## The class

The line column of an Icon trace line was not the line of the frame the message is about. `g_line` is
ONE global `long` (`src/runtime/keywords.c:28`), stamped per statement by `bb_line_mark` /
`bb_stmt_mark` (`src/templates/bb/bb_stmt_mark.cpp:19,30`) through a GOT load into `rax` — a memory
global, not a pinned register — and nothing restored it when control came back into a frame that did
not re-execute a stamp. `db3`/`db2`/`dbraid` all printed `braid`'s line 16; `dc2`/`dcreate` printed
`dc3`'s 46. The trace TEXT was correct on every one of those lines. Only the number was wrong, which
is why it survived so long: the output looks right.

## Who cured it, and the measured comparison

Cured on origin by **`cc3f4e817`** and **`a1db51e6b`** ("a suspend trace event reports its OWN line,
not wherever execution had reached"). Those pass the construct's line **explicitly from the emitter**
into the trace hook.

I was independently curing the same class from the runtime side: reconstruct the caller's line at
each frame exit from the activation record (which holds the line its frame was called from), and bank
a frame's own line at suspend so a *resumed* generator — which lands mid-statement, so no stamp runs
— gets its line back. Both boundaries, no emitter change. Measured head to head on the same tree:

| program | before either cure | mine (runtime reconstruction) | landed (`cc3f4e817`+`a1db51e6b`) |
|---|---|---|---|
| jcon_tests/cxtrace | 90 | 2 | **0** |
| jcon_tests/tracing | 120 | 92 | **68** |
| arizona general/tracer | 28 | 22 | 22 |

**The emitter-side cure wins, and the reason generalises.** The line a construct sits on is known at
compile time; the emitter simply *has* it. Reconstructing it at runtime from activation records
recovers most of it — but only what the records happen to encode, so it stalls exactly where the
record is silent. My residual was `braid suspended 99` printing 19 where iconx prints 20: line 19 is
`while v := @a | @b do`, line 20 the `suspend v` body, and no activation record distinguishes them.
The emitter-side cure has that line for free and gets it right. **When a fact is a compile-time
constant, carrying it down beats reconstructing it from runtime state — the reconstruction can only
ever be as complete as what the runtime happened to write down.**

## Two traps, both re-measured live

**A census number in a dispatch header has the shelf life of the tree it was cut on.** The MODE
header's own census read `cxtrace 250`, and said the suspend/resume lines did not exist at all. The
file measured **90** before I touched anything and those lines were already there — `a3eab74ad` had
landed them. I planned against the header for a few minutes before measuring. Measure the file, then
plan; the header names the *lane*, never the current number.

**A baseline run against a path with no `.std` printed `diff=0` and I nearly believed it.**
`diff nosuchfile` errors to stderr, `grep -c '^[<>]'` counts zero, and the false green is
indistinguishable from a real one — it read `BASELINE coexpr diff=0` for three programs at once. The
arizona refs live in `arizona_tests/general/`, not `arizona_tests/`. This is CLAUDE.md's *instrument
that answers a narrower question than you think you asked*, in its most expensive form: it does not
fail, it **confirms** you. Assert the ref exists before diffing it, and treat any all-zero row that
arrives without effort as a claim to check rather than a result to keep.

## The real lesson for a parallel fleet

Two seats cured one class in one sitting without either knowing. Nothing was lost — the rebase
conflicted, which is the mechanism working — but the cost was a full measure-and-cure cycle. Both
commits landed while my build was running, so no `check` at any point in my sitting would have shown
them. The cheap guard is not more messaging: it is **`git log --oneline -5 -- <the file you are about
to edit>` immediately before editing it**, which would have cost one command and shown me
`a3eab74ad`, `cc3f4e817` and `a1db51e6b` sitting on `core.c`.
