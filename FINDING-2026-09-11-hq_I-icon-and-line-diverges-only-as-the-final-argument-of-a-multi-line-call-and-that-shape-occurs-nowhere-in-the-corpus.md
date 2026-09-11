# FINDING 2026-09-11 hq_I — Icon `&line` diverges only as the final argument of a multi-line call, and that shape occurs nowhere in the corpus

**Measured on** SCRIP `0e4539a65` (clean, no local change) · corpus `3708c8ab9` · `RT_OPT=-O0` ·
oracle `icont`/`iconx` Icon v9.5.25a at `/home/resources/icon-master/bin` · measurer hq_I,
2026-09-11 ~21:0x UTC.

**Verdict up front: real divergence, precisely characterised, and NOT worth a row today.** It is
reachable only by a source shape that appears zero times in the Icon corpus. Recorded so the next
seat who trips it does not re-derive it, and so nobody "fixes" it the way I first tried to.

## What `&line` actually is in SCRIP

Not a `g_line` reader at all. `lower_icon.c:439` already lowers `&line` to an `IR_LIT_INTEGER`
holding the token's line — it is **already emitter-carried**, a compile-time constant. This matters
for the g_line-removal work (CEO-551): the Icon `&line` route is *done*, and the remaining `g_line`
readers are the trace and run-time-error paths plus the SNOBOL4 statement machinery.

## The divergence, minimal pair

```icon
procedure main()
   write("P ",          # line 2 — invocation starts here
         &line);        # line 3 — &line is the LAST argument
   write("Q ",          # line 4
         &line,         # line 5 — &line is a MIDDLE argument
         "");           # line 6
end
```

| shape | `&line` token line | iconx | SCRIP |
|---|---|---|---|
| final argument of a multi-line call | 3 | **2** (the invocation's line) | 3 |
| middle argument of a multi-line call | 5 | 5 | 5 |
| any argument on the invocation's own line | 10 | 10 | 10 |

So the rule is exactly: **when `&line` is the final argument of an invocation whose argument list
spans more than one line, iconx reports the invocation's line; in every other position both agree.**
Reproduced on four independent shapes (`write` 2-arg, `write` 3-arg, `write` 4-arg, nested
`g(h(), &line)`), and in the then-branch of an `if`, which behaves the same way. Both modes m3 and
m4 diverge identically, so this is a lowering fact, not a mode fact.

## Incidence in the corpus: zero

`&line` appears 1176 times across `corpus/packages/icon/` and `corpus/tests/icon/`. A grep for the
triggering shape — a continuation line whose content is the `&line` token closing the argument list —
returns **nothing**. In `arizona_tests/general/errors.icn`, the file with the densest `&line` use and
the largest single remaining Icon problem, every occurrence is `monitor(&line)` written entirely on
one line, so the quirk cannot fire. **No board moves if this is cured, and none moves if it is not.**

## ⛔ The cure I tried, why it was worse, and the trap in it

I hypothesised "`&line` is the enclosing STATEMENT's line" off two data points, added a `stmt_line`
field to `icx_t`, and had `lc_key` prefer it. It made the two-point probe read 0 — and a richer
nested probe went from **2 diff lines to 20**, because `&line` then reported the enclosing *control
header* (`every`/`if`/`while`/`repeat`) instead of the inner statement. I dropped it.

⭐ **The trap is not the wrong hypothesis, it is the probe that confirmed it.** My first probe
contained only shapes where "statement line" and the truth coincide, so it returned a clean 0 and
read as proof. The baseline I had not yet measured was already closer to the oracle than my cure —
**2 wrong lines against my 20** — and I would have landed a 10x regression believing I had a green
witness. Two disciplines this earns, both cheap:

- **Measure the baseline before writing the cure, not after.** A cure's diff count means nothing
  without the number it replaced. Mine looked like 0-is-perfect; it was 20-replacing-2.
- **A probe you wrote to confirm a hypothesis is not evidence for it.** Build the probe to *separate*
  the candidate rules — here, one line with `&line` last and one with it in the middle, which is what
  finally killed the hypothesis in a single run.

And the incidence check belongs before the cure too: had I grepped the corpus first, I would have
known there was no row here at all before spending a build on it.

## If someone does cure it

It is `src/lower/lower_icon.c` — **hq_B's lane**, Icon lowering. `lc_key` would need to know it is
lowering the final argument of a multi-line invocation and reach that invocation's line; the other
positions must keep the token's line, which is what they already do. Encoding what is very likely an
icont code-generation artifact as a lowering special case is the cost, and the benefit measured above
is zero programs, so my recommendation is to leave it and keep this note.
