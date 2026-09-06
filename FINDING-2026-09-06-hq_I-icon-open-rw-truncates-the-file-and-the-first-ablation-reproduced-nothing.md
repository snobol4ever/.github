# Icon `open(f,"rw")` truncates the file it was asked to update — and the first ablation reproduced nothing

**hq_I, 2026-09-06. SCRIP `1d8f6e068`, corpus `34560ec05`. Incremental `make`, `RT_OPT=-O0`.**

## The defect

`open(path,"rw")` and `open(path,"rwu")` **truncate the file to zero bytes**. The oracle opens it for
update and preserves every byte. Measured on a 12-byte file, both engines, mode by mode:

| mode | scrip leaves | oracle leaves | |
|---|---:|---:|---|
| `rw`  | **0** | 12 | ⛔ destroys data |
| `rwu` | **0** | 12 | ⛔ destroys data |
| `ru`  | 12 | 12 | ok |
| `r`   | 12 | 12 | ok |
| `a`   | 12 | 12 | ok |

Read-only and append are correct; the defect is specifically the read+write path.

The site is three lines, `src/runtime/by_name_dispatch.c:2940-2942`:

```c
if (strstr(ms, ":w") || strstr(ms, "w")) mode = "w";
else if (strstr(ms, ":a") || strstr(ms, "a")) mode = "a";
```

Any mode string containing a `w` becomes C `"w"`, which truncates on open. **There is no `"r+"` arm at
all**, so Icon read+write cannot be expressed. (The `":w"`/`":a"` tests are dead code — any string
containing `":w"` already contains `"w"` — which reads as though a second mode syntax were supported.)

⛔ **This is data loss that reports itself as a program error.** The file is destroyed at `open`, so the
program then behaves as though it had always been empty and complains about *that*. Nothing anywhere says
"your file was overwritten". `fixpath.icn` prints `fixpath.in: empty file` — a true statement about a file
that was not empty until SCRIP opened it.

## The part worth keeping: the first ablation reproduced nothing, and that was the signal

`fixpath` failed with `empty file` where the oracle printed `replaced 1 occurrence`. `fixpath` reads its
target with `while pgm ||:= reads(f, 8192)`, so the obvious hypothesis was `reads()` on a binary handle.

That hypothesis was **tested and came back clean**: five probes — `reads(f,8192)` under `"r"`, `"ru"`,
`"rwu"`, a NUL-bearing file, and the accumulate loop — and **SCRIP and the oracle agreed on every one**,
including both returning `&null` for `"rwu"`. 

⭐ **An ablation that reproduces nothing has told you something: the cause is not where you are standing.**
The temptation at that moment is to write up the plausible story anyway — "`reads()` mishandles binary
handles" — because it fits the symptom, names a real function, and would have been entirely wrong. The
defect was one layer earlier: the file was already empty because `open` had truncated it, so *of course*
`reads` returned nothing, and every direct probe of `reads` was innocent because `reads` is innocent.

The cure for the reasoning was to stop asking "which call returned the wrong value" and ask "what is
different about the FILE" — one `wc -c` before and after, which is the measurement that settles it in
seconds. Same family as this lane's standing rule that a correct procedure can carry a false explanation:
here a false explanation was available, fit the evidence, and had to be actively refused.

## Where it came from

`fixpath.icn` had **never been graded** until this sitting authored its argv fixture. It is one of nine
reds that appeared the moment sixteen previously-ungraded IPL programs were given fixtures and refs — the
package lockdown finding defects by the only method that finds them, which is grading the programs.

## Not done here

The cure needs one measurement this finding deliberately does not guess: **`"r+"` fails on a nonexistent
file where `"w+"` creates one, and which of those matches `icont` is a question for `iconx`.** And
`by_name_dispatch.c` is reached by more than one frontend, so the change is authored by hq_I (Icon exposed
it) and **co-signed by hq_U** per RULES § shared nodes. Row:
`icon-open-rw-truncates-the-file-and-destroys-its-contents`, rank 1, DONE-WHEN proven RED across all five
modes and runnable from a bare clone.
