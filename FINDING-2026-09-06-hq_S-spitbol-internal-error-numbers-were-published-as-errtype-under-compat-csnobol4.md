# SPITBOL's internal error numbers were published into &ERRTYPE/&ERRTEXT under `--compat=csnobol4`

**Seat:** hq_S (HQ-SUSTAIN, SNOBOL4 runtime) · **Date:** 2026-09-06 · **Row:** `flip-csnobol4-err` (MODE OCTET rule 12)
**Tree:** SCRIP `b6d2ae3f7` · corpus `8fdad5458` · `RT_OPT=-O0` · incremental `make`

## The measurement

`corpus/packages/snobol4/csnobol4_suite/err.sno` is six lines and asks one question — what does a bad
array reference publish into `&ERRTYPE` and `&ERRTEXT`:

```
	&ERRLIMIT = 2
	a[1] =
	OUTPUT = &ERRTYPE
	OUTPUT = &ERRTEXT
	OUTPUT = &ERRTYPE
END
```

Both oracles, run directly on this witness:

| arm | `&ERRTYPE` | `&ERRTEXT` |
|---|---|---|
| `csnobol4 -b` | `3` | `Erroneous array or table reference` |
| `sbl -bf` | `235` | `subscripted operand is not table or array` |
| SCRIP, `--compat=csnobol4` (before) | `235` | `subscripted operand is not table or array` |

**Neither oracle is wrong.** SPITBOL publishes its own 3-digit internal table; CSNOBOL4 publishes the
standard SNOBOL4 types 1..35 documented in `snobol4error(1)` (`/home/resources/csnobol4/doc/snobol4error.1`).
This is a dialect divergence, and it belongs behind the `--compat=csnobol4` switch that already exists —
the default arm stays SPITBOL and never widens.

## The cure, and the part of it that is not obvious

`core_err_compat_map()` in `src/runtime/core/core.c` carries the table. It is called from **two** places,
and the second one is the whole reason the witness was red:

- `core_runtime_error()` — the real funnel, reached by ~everything.
- `kwb_error()` in `src/runtime/keywords.c` — which **short-circuits that funnel whenever `&ERRLIMIT` is
  non-zero**, publishing to `&ERRTYPE`/`&ERRTEXT` itself and returning without ever calling
  `core_runtime_error`. That is exactly the shape `err.sno` uses (`&ERRLIMIT = 2` on line one). A cure
  placed only on the funnel would compile, look complete, and leave the witness red.

⭐ The general form: **a funnel with a bypass is two funnels.** Before treating a function as "the one
place", grep its callers for the early-return that skips it.

## The five rows, each measured on its own witness against BOTH oracles

| SCRIP (SPITBOL) | CSNOBOL4 | text |
|---|---|---|
| 153 | 10 | Illegal argument to primitive function |
| 208 | 1 | Illegal data type |
| 209 | 8 | Variable not present where required |
| 235 | 3 | Erroneous array or table reference |
| 244 | 22 | Limit on statement execution exceeded |

⛔ **No row was read off a table.** Each is a probe program run under `csnobol4 -b` and `sbl -bf` in the
same minute. That discipline is what produced the next two paragraphs, which a table-reading cure would
have gotten wrong in both directions.

## What is deliberately NOT mapped, and why a number could not express it

`SCRIP 152` (opsyn third arg not integer), `156` (opsyn first arg not an operator name), `210` (keyword
value negative or too large) and `287` (MAXLNGTH too small) all pass through unmapped — **because
CSNOBOL4 raises no error at all on those witnesses.** `&ANCHOR = -1` and `&MAXLNGTH = 10` are simply
accepted by CSNOBOL4 (`&ERRTYPE` reads `0`, `&ERRTEXT` empty), and `OPSYN("F","LEN",X)` /
`OPSYN("+","NOSUCH",2)` likewise. These are **behaviour** divergences wearing the costume of a numbering
divergence, and mapping them to some plausible CSNOBOL4 code would have manufactured an error CSNOBOL4
does not have. They are a separate class, not a missing row.

## ⛔ Two hazards, both invisible at the site where they would bite

1. **`SCRIP 21` is a pass-through inside CSNOBOL4's own 1..35 range.** SCRIP raises 21 ("function called
   by name returned a value") at the SPITBOL-only `@`-goto check in `src/runtime/runtime_eval.c` —
   a form CSNOBOL4 has no syntax for, so there is nothing to measure it against. Unmapped, it surfaces
   under csnobol4 compat as a `21` that a reader will match against CSNOBOL4's **"Stack overflow"**.
   Any new SPITBOL code below 36 needs a measured row here or it masquerades as a real CSNOBOL4 type.
2. **The map must stay idempotent.** `kwb_error` maps, then hands the mapped code to
   `core_runtime_error`, which maps again. That is safe only while no `csn` value equals any `spit` key
   (today: keys 153..244, values 1..22). A new row must be checked against the whole column, not its
   own line.

## Byproduct fixed in the same mechanism

`--compat=spitbol` was unsetting three of the four csnobol4 env twins and leaving `SCRIP_IPOW_CSNOBOL4`
set — a reset that did not fully reset. Now unsets all five.

## Boards (measured, not quoted)

| arm | before | after |
|---|---|---|
| `test_snobol4_csnobol4_suite.sh` total=120 | m3/m4 PASS=69 FAIL=20 REJECT=30 CRASH=1 | m3/m4 **PASS=70** FAIL=19 REJECT=30 CRASH=1 |
| `test_corpus_snobol4.sh` (default dialect, control) | — | m3 PASS=1856 FAIL=1 · m4 PASS=1856 FAIL=1 SKIP=0 of 1857 |

+1 is `err` and only `err`; REJECT, CRASH, HANG and `PACKAGE_INVENTORY` (shipped=132 graded=120
ungraded=0 ungradable=12) are all unmoved. The master's FAIL=1 is the pre-existing red the ceo recorded
in CEO-362 with CAUSE NOT IDENTIFIED — unchanged by this landing, which it must be, since the default
dialect never reaches the map.

## ⭐ One process note worth more than the cure

The first cut of this change carried the whole explanation above as six `/* ... */` lines in
`src/runtime/core/core.c`. The `commit-msg` hook refused it: `src/` has a repo-wide zero-comment
invariant (the 200-char `/*----*/` separator is the only permitted form) because `strip_comments.py
--check` is arm one of `make test` for **every** seat on the box. The hook's own advice is what produced
this file — *"a source comment is found only by whoever opens that one file, while a FINDING is
greppable from anywhere."* The prose did not need deleting; it needed a different medium.
