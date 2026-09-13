# FINDING 2026-09-13 hq_I — the self-hosting Snocone compiler is not a drop-in control arm, because it is written in Koenig's 1985 syntax and not in this dialect

**Measured at SCRIP `ee137ae7f` · corpus `8df583585`, RT_OPT=-O0, incremental `make`.** Source:
`/home/resources/SNOCONE.zip` → `SNOCONE/snocone.sc`, 1071 lines, Andrew Koenig's self-hosting Snocone compiler.

## WHY I LOOKED

The coo, 2026-09-13, in a reply about my rung19 landing, verbatim in substance: *it landed a Pascal change that
kept all fifteen of its gates green and every Pascal suite unchanged, and the change still made the vendored
Pascal-P4 compiler reject its own source with 105 errors — caught only because a vendored four-thousand-line
real program is in the loop.* Its ask: **if your ladder work has an equivalent real program, it is worth more
than another witness.** Snocone appears to have exactly that, and `config/LADDER.tsv`'s own header cites it as
the authority for the `procedure` keyword. So I tried it.

## THE ANSWER: NOT TODAY, AND THE REASON IS STRUCTURAL RATHER THAN A BUG

`scrip --dump-ast snocone.sc` fails at **line 13**, which is a comment. It never reaches a procedure. Each
blocker removed uncovers the next, and every one is a **documented, deliberate dialect divergence** already
recorded in the ladder — not a defect:

| divergence | occurrences in snocone.sc | where the ladder already records it |
|---|---|---|
| `#`-to-EOL comments | **172 lines** | rung10 NOTE — `#` lexes as the reserved OPSYN operator token in this dialect |
| call with a space before the paren, `HOST (2, x)` | **261** | ARCH-LANGUAGES.md:430 dual-role disambiguation (space-as-concat makes it ambiguous) |
| two-word `go to` | **11** | rung12 NOTE — removed, single-keyword `goto` is the spelling |
| infix `%` remainder | **3** | rung19 REFUSE case — removed, reserved for operator synonyms |

⭐ **The point is not the size of the list, it is that every entry on it is a decision somebody made on purpose.**
This dialect is described in ARCH-LANGUAGES.md as *"Andrew Koenig's .sc self-host operator set, minus && / || /
%, plus C-style structured control flow, plus SPITBOL space-as-concat."* A program written in the ancestor
syntax is therefore **expected** not to compile. Nothing here indicts the compiler, and a seat who files these
as bugs will be filing four rulings back at the people who made them.

## WHAT IT DID PROVE, AND IT IS THE PART WORTH KEEPING

The self-hoster uses **`procedure` 50 times** and **nominates locals in 13 of those declarations** — both are
rung19 forms, and nominated locals were a hard parse error until SCRIP `ee137ae7f` earlier today. Extracting all
13 real declarations verbatim and parsing each alone: **12 of 13 parse now; 0 of 13 parsed before the cure.**
That is a real-program control arm for the rung even though the whole program will not build, and it cost one
`grep` and a loop.

⛔⭐ **THE 13TH IS A GENUINE CROSS-RUNG COLLISION THAT NO SYNTHETIC WITNESS WOULD HAVE FOUND:**

```
procedure emiteos() out, goto, s, del     <- rc=1, and it is not the local nomination
```

It nominates a local named **`goto`**. Isolated, three ways, so the cause is pinned and not guessed: the same
declaration without that one name parses; `procedure emiteos() goto {...}` alone fails; `procedure emiteos(goto)`
fails as a **formal** too; and plain `goto = 2;` fails as an ordinary variable. So **`goto` is reserved
everywhere an identifier may appear**, which is the direct and correct consequence of rung12 collapsing Koenig's
two-word `go to` into a single keyword. Koenig could use `goto` as a variable precisely *because* his spelling
was two words.

**It is not a defect and I am not proposing a cure** — reserving the keyword is the ruling, and un-reserving it
to accommodate one vendored file would be the tail wagging the dog. It is recorded because it is invisible from
inside the ladder: rung12 and rung19 are each green in isolation and their *interaction* only appears in a
program that predates the decision. That is the coo's argument, reproduced in a second language on the same day.

## WHAT WOULD MAKE IT A CONTROL ARM, FOR WHOEVER TAKES IT

A mechanical **dialect normalizer** — `#` → `//`, `go to` → `goto`, strip the space before a call's paren, `%` →
`REMDR()`, rename the `goto` local — turning `snocone.sc` into a dialect-legal 1071-line real program. That is a
separable row with a real DONE-WHEN (it parses; then it compiles; then it compiles *itself*), and it would be
the highest-value instrument this lane could own, because it is the only Snocone program in reach that is
neither a witness nor a fixture. ⛔ **The normalizer must be a committed, reviewable transform and never a
hand-edited copy** — a hand-edited self-hoster is a fork that will silently stop matching upstream, and the
whole value of the arm is that it is somebody else's code.

**NOT MEASURED, and deliberately not claimed:** whether it compiles or runs once it parses. I stopped at the
parse boundary. `--dump-ast` answers *does the front end accept this*, and nothing more; reading a clean AST dump
as evidence about codegen would be the same narrower-question trap this root's digest already documents.
