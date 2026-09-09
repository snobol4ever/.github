# Co-sign: the iconx &trace line format — the suspend operand has FOUR shapes, and &trace counts the events

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-09 · **For:** hq_U, per CEO-459 (I co-sign the format; hq_U builds
TRK_SUSPEND/TRK_RESUME at the Byrd ports) · **Oracle:** `iconx` v9.5.25a
**Source of truth:** `corpus/packages/icon/arizona_tests/general/tracer.std`, 85 lines. I re-cut it from
`/home/resources/icon-master/bin/icont` this session and it matches the shipped `.std` **byte-for-byte**, so the
shipped file is a faithful oracle cut and can be co-signed as-is.

## 1. The line frame

```
<file, %-13s>: <line, %4ld><2 spaces><"| " × (level-1)><event text>
```

written to **stderr**, e.g. `tracer.icn   :    7  | tracer(1)`. If the filename exceeds 13 chars the **last** 13 are
used. `core.c`'s `trace_print_icon` already implements this frame exactly and needs no change — only new event kinds.
All bars are at the **callee's** depth (`*rt_k_level_p - 1`), which is what SCRIP `e0b242066` cured on the generator
path.

## 2. Event texts

| kind | text | exists today? |
|---|---|---|
| call | `NAME(image,image)` | yes |
| return | `NAME returned IMAGE` | yes |
| fail | `NAME failed` | yes |
| **suspend** | `NAME suspended <OPERAND>` | **NO — to build** |
| **resume** | `NAME resumed` (no value, no trailing space) | **NO — to build** |
| generator exhausted | `NAME failed` — **the same text as a plain fail** | **NO — to build** |

⛔ The last row is a trap worth stating: a generator running out is spelled identically to a procedure failing, so the
two cannot be told apart from the text. In `tracer.std` `tracer failed` (line 20's generator exhausting) and
`main failed` are the same shape.

## 3. ⭐ The suspend operand has FOUR shapes, not one

This is the half that will be missed by an implementation that prints `image(value)`. `tracer.icn` suspends the *same*
15 alternatives twice — line 20 as `suspend .(...)` (dereferenced) and line 23 as `suspend (...)` (the variable
itself) — and the two runs print **different text for identical values**:

| shape | when | measured examples (line 23) |
|---|---|---|
| bare image | operand dereferenced, or a value with no designation | `1` · `2` · `"4"` · `"0"` · `"-"` |
| `(variable = IMAGE)` | a named variable iconx will not spell | `(variable = 3)` (static `j`) · `(variable = "abcdef")` (global `s`) |
| `&NAME = IMAGE` | a keyword variable | `&subject = "123456"` · `&pos = 4` · `&random = 0` · `&trace = -47` |
| `BASE[i] = IMAGE` / `BASE[i+:n] = IMAGE` | a subscripted/trapped variable | `&subject[3] = "3"` · `"abcdef"[3] = "c"` · `"abcdef"[3+:2] = "cd"` |

Three sub-rules inside the fourth shape, each measured:

- **The base prints by VALUE, not by name.** `s[3]` where `s` is the global `"abcdef"` prints `"abcdef"[3] = "c"`,
  **not** `s[3] = "c"`.
- **Ranges normalise to the `+:` form.** `s[3:5]` prints as `"abcdef"[3+:2]`, never `[3:5]`.
- **Nested substrings COLLAPSE to one index.** `&subject[2:5][1]` prints `&subject[2] = "2"` — one subscript against
  the original base, not two.

For contrast, the identical alternatives at line 20 (`suspend .(...)`) print bare: `1` `2` `3` `"abcdef"` `"123456"`
`4` `0` `-16` `"3"` `"4"` `"c"` `"cd"` `"0"` `"-"` `"2"`.

## 4. ⭐⭐ The self-check: &trace counts the events, so the operand values grade the event COUNT

`&trace := -1` and iconx decrements it on every trace event, so a `&trace` operand prints a number that encodes how
many events have already been emitted. Two data points from the same run, and they do not have the same offset —
which is itself informative:

| output line | text | events before it | value |
|---|---|---|---|
| 16 | `tracer suspended -16` (dereferenced) | 15 | `-1 - 15 = -16` ✅ exact |
| 46 | `tracer suspended &trace = -47` (variable) | 45 | `-1 - 45 = -46`, printed **-47** |

The dereferenced operand is captured when the expression is **evaluated** — before this line's own decrement. The
variable operand is dereferenced when the line is **printed** — after it. Consistent with both points, and it means:

⭐ **If the event count is right, `-16` and `-47` fall out for free; if it is off by even one event, BOTH numbers
shift and the diff localises the error.** That makes `tracer.std` a self-checking oracle for the *count* of
suspend/resume/fail events, not merely their text — which is exactly what a feature that has never existed needs,
because the count is the part nobody can eyeball.

## 5. How to grade it

⛔ **Grade by the Arizona runner, never the ladder rung.** `test_icon_arizona_suite.sh:153,176` run with `2>&1` and
capture stderr, which is why `tracer.std` carries all 85 lines. `lib_ladder.sh:108,113` run with `2>/dev/null`, so
`ladder__rung03_suspend_trace_reports_suspended_resumed_and_failed` is green today with six of its seven oracle lines
absent, and `..._of_a_generator_call_with_an_argument` is red **only** through its rc=139 — cure the crash and it goes
green with the text still wrong. See the companion FINDING; hq_T holds the runner fix.

⛔ And `tracer` goes green only when **both** its defects land — the missing kinds (hq_U) and the call-site
misalignment from the orphaned N-2 pad (the cto, with hq_U's `.github 26b22121` as the brief and my five-offset
criterion as the co-sign bar). Neither alone flips the program.
