# FINDING 2026-09-12 (ceo) — Raku scoped: a frontend build, one HQ; Prolog sized by Logtalk family, two HQs (CEO-649)

Measured 2026-09-12 19:21 CDT on SCRIP `3a510fa4e` · corpus `48bd46258` · RT_OPT=-O0, on Lon's ask.

## Raku

| Instrument | Reading |
|---|---|
| Frontend size | raku.y 1,940 · raku.l 300 · lower_raku.c 1,205 lines; no Raku-own runtime file |
| `test_smoke_raku.sh` | 10/10 both modes |
| `test_raku_ladder.sh --to 16` | PASS 92 / FAIL 44 of 136 witness×mode; red from rung 2 |
| RakM (SCORE.md, coo 09-12 `55aaa01ad`) | 680/880, 156 xfail (142 in the `smoke` family) |
| Roast parse census (`--dump-ast`, 1,058 files after the scoreboard's directory exclusions) | 19 parse · 1,004 bison "syntax error" · 35 lex error |

Red rungs: 2 arithmetic (integer_div, negative_operands) · 4 arrays (slice, out_of_bounds) · 5 hashes (missing_key, keys_values, exists_delete) · 8 for_with_index · 9 split_method · 12 (8 of 10) · 13 classes_private_attribute · 14 roles_attributes, roles_smartmatch (13–14 NOBUILD in m4).

Roast failing-line position: lines 1–3: 84 · 4–10: 454 · 11–30: 440 · later: 61 — not a prologue blocker. Leading token of the failing line: `my` 203 (`.map({...})`, `1 ... 10`, `:shape(2;2)`, `open(..., :w)`) · `ok`/`is` 204 (mostly `~~ m/.../` regexes) · `use` 80 (`use lib $*PROGRAM.parent(2).add: '...'` 42, `use v6.e.PREVIEW` 30) · `sub`/`multi`/`method` 123 (traits, signatures) · `throws-like`/`subtest`/`is-deeply`/`lives-ok`/`isa-ok`/`dies-ok` 150 (Test.pm6 forms). Bison's bare "syntax error" carries no class, so any real census must key on the failing construct, as this one does.

**Verdict.** Raku is a frontend build (regexes/grammars, adverbs, sequences, signatures and traits, the object model), not a cure lane. One HQ — hq_T, whose named lane already holds Raku — with the ceo as its HQ. Order: ladder rungs 2→16 green in both modes; the 156 xfails, each deleted as a faulty test or rowed as a defect; then roast parse classes, largest first. Escaping closures and the object model reach the shared engine: asks, not landings. Boards (RakM, roast) by the coo only. Existing rows: 37 `raku-*`, 5 at rank 0.

## Prolog

From the cto's Logtalk pass on `34a80e981` (progress DB, 7,234 case×mode rows at 23:41Z), FAIL by group:

| Family | FAIL | PASS |
|---|---|---|
| format | 720 | 104 |
| write / writeq | 284 | 6 |
| stream I/O (get 138, peek 130, put 98, stream 78, open 66, read 64) | 574 | 126 |
| builtins (lgt) | 206 | 42 |
| unbounded integers (bignum) | 164 | 58 |
| encodings | 98 | 0 |
| operators + op | 148 | 34 |
| setof | 60 | 36 |
| number | 58 | 136 |
| clause | 54 | 24 |

**Verdict.** Two HQs: hq_R (Prolog builtins) takes format/write/writeq and the stream I/O family; hq_C (correctness/Prolog) takes operators/op, setof/bagof, clause/assert, number, encodings. The cto keeps the ISO ladder rungs (control constructs, exceptions, the frame), rules the unbounded-integer class through Lon, and is both HQs' HQ. Prolog-own files only; a shared-node change is an ask. One row per family, DONE-WHEN that family's Logtalk cases both modes over the printed denominator.

Three HQs in all, Opus 5, the coo the one runner. No MODE change until Lon's word.
