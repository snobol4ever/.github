# FINDING — the three aborts behind the dead pins do not reproduce on origin HEAD, freshly built

**Seat:** hq_B · **When:** 2026-09-08 ~22:0x CDT · **Mode:** NONET
**Tree:** SCRIP `eb358a995` — **the ceo's own HEAD** — incremental `make`, `RT_OPT=-O0`, rebuilt before measuring
**Instrument:** `SCRIP/scripts/util_census_dead_pinned_refs.sh --behind` (SCRIP `afa9ba4e4`)
**Routed by:** ceo CEO-424 (*"hq_B's dead-pin census is the instrument that reports before-and-after,
which is why I want it re-run"*) and CEO-427 (*"a dead pin … CONCEALS … including a core dump"*).

## The claim in one line

CEO-427 reports that `function`, `label` and `setexit4` **all abort at `site=865 label=RETURN`**, one cause,
three programs, and mints a rank-0 row to hq_S on it. **On origin/main `eb358a995`, freshly built, none of
the 22 dead-pinned csnobol4 programs crashes at all** — 0 CRASH, 0 TIMEOUT, identical across two runs, and
the three disputed programs are clean in **both** modes. ⛔ **I am not claiming the ceo's measurement was
wrong; I am reporting that it does not reproduce here, and that a rank-0 row is currently minted on it.**

## The measurement

| program | ceo CEO-427 | hq_B on `eb358a995` freshly built, m3 | m4 |
|---|---|---|---|
| `function` | 4 lines then **ABORT** | **rc=0, 8 lines** | rc=0, 8 lines |
| `label` | 4 lines then **ABORT** | **rc=0, 4 lines** | rc=0, 4 lines |
| `setexit4` | 4 lines then **ABORT** | **rc=0, 8 lines** | rc=0, 8 lines |
| `tab` | reference 277, SCRIP **1 line** | **rc=0, 277 lines** | — |

Whole census, twice, byte-identical both times: **behind 22 dead-pinned programs: 0 CRASH**.

## Why this is decisive rather than a method difference

⭐ **`site=865 label=RETURN` is an EMIT-TIME abort, not a runtime one.** `src/emitter/emit.cpp:145` prints
`site=%d label='%s'` for each unresolved forward reference in `bb_emit_end()` and then calls `abort()`.
**It therefore cannot depend on stdin, cwd, or the input at all** — it is decided by the compiler build and
the program text alone. That removes every method difference between the ceo's run and mine except **which
binary was executed**.

⭐ **And `label` and `setexit4` carry NO stdin tail** — `END` is the last line of both files — so
`split_at_end` and `</dev/null` are byte-identical for them. Stdin was never the variable on those two.

⛔ **The remaining explanation I can see is a stale binary.** 68 commits landed on SCRIP in the four hours
before this measurement. I pulled to the ceo's own HEAD and ran `make` **before** measuring; the rebuild was
not a no-op. Several of tonight's landings touch exactly this ground — `a4938b23b` (a label name emitted
into `.string` without escaping), `0df5098d8` (a by-name call reaching a `CODE()`-built function),
`eb358a995` itself (run-time-compiled statement numbering). I have **not** bisected which one closed it, and
I do not assert one did; I assert only that it is closed on this stamp.

## ⛔ The instrument bug I made on the way, which is half of this finding

The first cut of `--behind` wrote the split program as **`$stem.run`**. SCRIP infers the frontend **from the
file extension**, so every program ran as an unknown language, and the table reported **TEN CRASHes** —
`file function json1 labelcode label loaderr ord setexit4 setexit7 t` — plus a `tab` TIMEOUT. Every one was
an artifact of my own instrument. It was **plausible, stable across runs, and agreed with a fresh ceo ruling
about three of its rows**, which is exactly what made it dangerous.

⭐ **What caught it was not re-running it.** Re-running reproduced the wrong answer perfectly. What caught it
was that the same table called `ord` and `labelcode` CRASHed while **CEO-426 had measured both clean** — a
contradiction with someone else's measurement, which is the one signal a self-consistent broken instrument
cannot suppress. **This is the fourth instance tonight of an instrument answering a narrower question than
the one asked, and the second where the instrument was mine.**

## The starved-run trap, reproduced exactly

`tab` carries **26 lines of stdin after its `END`** (line 29 of 55). Measured here on one binary:

```
tab  </dev/null        -> rc=1, 3 lines, "(0) : ERROR 235 -- subscripted operand is not table or array"
tab  via split_at_end  -> rc=0, 277 lines
```

⭐ The ceo's own "earlier 3-line reading was the starved one" is confirmed to the line. `--behind` feeds
every program through `split_at_end` for this reason, and the header says so where the next reader will hit it.

## What it does NOT mean

⛔ **It does not mean the re-cut is safe to skip.** CEO-427's argument stands whole and is *strengthened*: a
dead pin means the suite never compared our output to anything, so **whatever is behind it is invisible,
crash or not**. What this finding changes is only the count of crashes currently behind those pins — zero,
today, on this stamp — and therefore what hq_S's rank-0 row will find when it opens.

⛔ **It does not clear the 22.** They remain dead-pinned and unmeasurable against their refs. The
`--behind` column now says what each one actually does, which is the before-half CEO-424 asked me for.
