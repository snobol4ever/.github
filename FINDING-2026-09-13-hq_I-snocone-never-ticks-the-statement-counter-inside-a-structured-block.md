# FINDING 2026-09-13 hq_I — Snocone never ticks the statement counter inside a structured block

**Measured** while walking Snocone ladder rung23 (keyword_and_system_variables) under MODE NONET.
Tree: SCRIP=e62070ca8, corpus=682cd2f34. Oracle: `/home/resources/x64/bin/sbl -bf`.

## The claim

The Snocone path emits a statement-count hook for each **top-level** statement only. Statements
nested inside a structured body (a `while`/`if` block) are never marked. Therefore `&STCOUNT`
under-counts by exactly the nested executions, and **`&STLIMIT` cannot fire on a runaway loop** —
which is the one thing `&STLIMIT` exists for.

## The measurements

| program | scrip `.sc` | oracle (SPITBOL twin) |
|---|---|---|
| flat: 4 top-level statements between two `&STCOUNT` reads | delta **4** | delta **4** ✅ agree |
| `while (i < 10) { i = i + 1; }` between two reads | delta **3** | delta **13** ⛔ |
| `&STLIMIT = 50` + 1000-iteration `while` | prints `done`, **rc=0** | `ERROR 244`, halts ⛔ |
| `&STLIMIT = 3` + 4 flat statements | `error 244` at statement 4 | `ERROR 244` at statement 4 ✅ |

The flat cases agree with the oracle **exactly**, which is what localises the defect: this is not an
interpreter-bookkeeping mismatch, it is a missing tick.

## It is the Snocone path alone

The same three programs written as `.sno` are **correct under scrip**: delta 13, and `error 244` at
rc=1. So the runtime machinery (`rt_stmt_enter`, `kw_stlimit`, `g_stcount` in
`src/runtime/keywords.c:532-543`) works. Only the Snocone lowering loses it.

## Cause (read, not inferred)

`src/lower/lower_snobol4.c:2544` emits one `SNO$STMT` hook per entry of the **top-level** statement
array `st[]`. Snocone's structured bodies are nested children of a single top-level statement, so
they are never visited by that loop. SNOBOL4 is unaffected because it has no nested blocks and
builds its loops from gotos back to marked statements — each iteration re-executes a marked
statement.

## Not cured here

`lower_snobol4.c` is reached by the SNOBOL4 and Rebus frontends as well as Snocone, so it is a
shared node: **an ASK, never a ladder seat's landing** (same ruling as rung20's `TT_AUGOP` and
rung21's `TT_VLIST`). Asked to the ceo 2026-09-13.

## ⛔ The dangerous direction

A program the oracle **halts** produces a plausible answer under scrip at rc=0. A runaway loop that
SPITBOL stops at the limit the author set runs to completion here and prints a result the author
never authorised.

## ⭐ A false negative met on the way, worth more than the defect

`grep -c rt_stmt_enter` over the emitted `.s` returns **0** for a program that demonstrably ticks
the counter four times. The hook is dispatched **by name** as a string operand — `.string "SNO$STMT"`
— so the C symbol cannot appear in the emitted asm by construction. The zero is false.

This is the mirror image of the warning the root digests already carry (*a global read only by
EMITTED code is invisible to a grep of the compiler's own sources*). That warns about grepping the
**compiler** for a name the **emitted code** uses; this is grepping the **emitted code** for a name
the **compiler** uses. One boundary, two directions, and the filed lesson only covered one of them.
**Anything dispatched by string name across that boundary is unfindable from whichever side you are
standing on** — the only instrument that crosses it honestly is a behavioural number.
