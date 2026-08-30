# FINDING 2026-08-30 hq_C — bison was on PATH and could not generate; every parser regen silently did nothing

**Tree:** SCRIP `ead6fa89` (baseline) → `d3c7dc90` · measured 2026-08-30, seat `hq_C`, row
`raku-roast-100-percent-compile`. Cured in `32f41604`.

## The claim

`scripts/regenerate_parser_and_lexer_from_sources.sh` — the ONE sanctioned path for turning a `.y`/`.l`
edit into the committed `.tab.c`/`.lex.c` — **regenerated nothing, for any language**, and its own
prerequisite check could not detect that.

```
bison: /usr/share/bison/m4sugar/m4sugar.m4: cannot open: No such file or directory
```

`bison` 3.8.2 was on PATH at `/home/satirical/.local/bin/bison`. Its `--print-datadir` named
`/usr/share/bison`, **which did not exist** — the entire install lived under `/tmp/flexbison/root/`
(the PATH entry is a symlink into it) and nothing set `BISON_PKGDATADIR`.

## ⭐⭐ Why nobody caught it — three independent disguises

1. **The prereq check asked a narrower question than it appeared to.** It ran `command -v bison`, which
   answers *is it on PATH*, and was read as *can it generate*. Exactly the `command -v icont` family
   already recorded in CLAUDE.md — **an instrument that answers a narrower question than you think you
   asked will never say so.**
2. **bison printed a plausible, correct-looking analysis before dying.** It emits the grammar's
   conflict summary (`115 shift/reduce conflicts`) and *then* fails on the skeleton. A reader watching
   the output sees the number they expected scroll past. I measured the conflict counts of two grammar
   revisions this way and got correct answers from a bison that could not write a single output file.
3. **The failure was invisible through a pipe.** `bash scripts/regenerate…sh 2>&1 | tail -25` reports
   `$?` of `tail`. I read `RC=0` off that pipeline myself before re-measuring the script alone at
   **rc=1** — the verdict-line law in CLAUDE.md, hit live, in the act of investigating this very bug.

## Corroboration: the breakage had already silently swallowed edits

Regenerating each committed `.y` with a working bison and diffing against the committed `.tab.c`
(`#line` directives excluded, since the script `cd`s into each dir):

| parser | differing lines | **parse-table lines differing** |
|---|---|---|
| snocone | 189 | **0** |
| rebus | 71 | **0** |
| snobol4 | 36 | **0** |
| pascal | 34 | **0** |
| **raku** | **0** | **0** |

⛔ **State the severity precisely — the tables are IDENTICAL in all four.** The drift is confined to the
`%{…%}` prologue that bison copies verbatim. Concretely, `rebus.y` says `#include "../../ast/ast.h"`
while the committed `rebus.tab.c` still carries `#include "ast.h"`, plus stale comments in pascal and
snocone. **No grammar is wrong today and no build is broken** — the stale generated files compile.

⭐ But that is exactly what makes it dangerous rather than harmless: the mechanism that swallowed a
prologue edit harmlessly would swallow a **production** edit silently, and the author would see their
new grammar rule simply not take effect while every test still passed on the old tables. My own first
Raku fix did exactly this — I edited `raku.l`, "regenerated", rebuilt rc=0, and the witnesses still
failed byte-identically. Only `git status` showing an unmodified `raku.lex.c` gave it away.

## The cure

`32f41604` replaces the presence check with a **generation** check: resolve a usable skeleton dir
(`BISON_PKGDATADIR` fallback chain: `$HOME/.local/share/bison`, `/tmp/flexbison/…`,
`/usr/local/share/bison`), then prove it on a throwaway grammar and fail loudly naming the cause.
The skeleton tree was also copied out of `/tmp` to `$HOME/.local/share/bison` so it survives a
`/tmp` sweep — **the whole fleet's bison lived in `/tmp`.**

## The generalizable rule

**A prerequisite check must exercise the capability it is gating, not the artifact it is named after.**
`command -v X` is never evidence that X works; the only evidence is X doing, once, the smallest real
instance of the thing you are about to ask it for.

⚠️ **Left for the owning lanes, deliberately not done here:** re-running the regen for snocone/rebus/
snobol4/pascal is a cross-language change under SHARED-NODE VERDICT SCOPE and would require grading
every frontend that reaches them. The four prologue drifts are recorded above so whoever holds those
lanes can land them with the grading their own law requires.
