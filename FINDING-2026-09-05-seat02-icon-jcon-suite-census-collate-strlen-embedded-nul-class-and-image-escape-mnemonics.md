# FINDING (seat02, 2026-09-05): jcon's `collate` cured — a nine-function strlen-on-embedded-NUL class, plus a second layer at STRVAL(), plus a missing image() escape set

**Seat:** seat02 · **Mode at measurement:** FLEET-16 · **Tree:** SCRIP `0679df433`, corpus `911c49b77`, RT_OPT=`-O0`, incremental `make`
**Row:** `icon-jcon-suite-39-non-pass-censused-by-class-and-cured` (this row's own established diff-size-sweep methodology, 8th pass)

## METHOD (unchanged from the 7 prior passes on this row)

Fresh board, then a diff-size sweep of the m3 FAIL bucket (`diff <(./scrip --run) .std | wc -l`, sorted)
to find the smallest untried gap. `lists` (6) is the already-known oracle-disagreement class (not a bug).
`collate` (10) had never been examined by any of the 7 prior passes — picked as the target.

## THE SYMPTOM, ISOLATED

`collate.icn`'s output has 126 lines: the first 4 (from `collate()`/`decollate()` on `&cset`-derived
strings) were empty (`""`), the remaining 120 (an unrelated `permute()`/`sort()` block with zero cset
interaction) were byte-perfect. A minimal repro narrowed it in two calls:

```
write(image(left(&cset,3)))     -- got "   " (three pad spaces, as if given "")
write(image(reverse(&cset[1:4]))) -- got ""
```

Direct indexing (`&cset[1:4]`) and `string()` coercion both return `&cset`'s content correctly
(`"\x00\x01\x02"`); only a specific family of BUILTIN FUNCTIONS mishandled it.

## ROOT CAUSE, LAYER 1: strlen() on a string that legitimately starts with byte 0

`&cset` is Icon's 256-byte "every possible character" string, byte-value-ordered — its first character
IS byte 0. `src/runtime/by_name_dispatch.c` implements nine related builtins (`left right center reverse
map trim repl detab entab` — literally the one alphabetized family this file's own two builtin-name
tables list together) by materializing the subject via `VARVAL_fn()`/`icn_pad_str()` (both return a raw
`const char *`, discarding the descriptor's own length) and then computing the subject's length via
plain `strlen()`. `strlen("\x00...")` is 0. Every one of the nine treated `&cset`, or any string derived
from it, as empty.

This is the SAME class as the cset-type fix two days ago (FINDING-2026-08-19-...-cset-canonical..., and
more recently the trace-dispatch case-folding finding this same morning) — a NUL-terminated-C-string
assumption meeting a value that is not conceptually NUL-terminated at all. That fix covered the `cset`
TYPE's own construction/read primitives; this is a sibling family of plain STRING builtins that never
got the same treatment.

**Fix:** a new `icn_true_len(DESCR_t d, const char *materialized)` helper — `descr_slen(d)` (already used
elsewhere for exactly this reason, immune to embedded NULs) when `d.v == DT_S`, else `strlen(materialized)`
(safe: a coerced int/real string can never contain an embedded NUL). Applied at all nine call sites'
length computation (`repl`'s replication count, `reverse`'s loop bound, `map`'s subject AND its two
mapping-table lengths, `trim`'s truncation boundary, `left`/`right`/`center`'s source length, `detab`'s
loop bound — rewritten from an implicit NUL-scanning `for (int i=0; s[i]; i++)` to an explicit bound,
`entab`'s explicit `strlen`).

## ROOT CAUSE, LAYER 2: STRVAL() ALSO derives its length via strlen()

Fixing layer 1 alone was insufficient — `left(&cset,3)` then computed the CORRECT 3-byte content but
still displayed as `""`. `#define STRVAL(s_) ... .slen = descr_cstrlen(_sv_) ...` and `descr_cstrlen` is
`strlen()`. So a freshly-built, byte-correct output buffer that itself happens to start with (`left`) or
end with (`reverse`, on this specific witness) a `\x00` byte gets silently re-truncated on the way OUT,
independent of whether the computation that built it was correct. This codebase already carries the
fix for this exact shape elsewhere — `BSTRVAL(buf, explicit_len)`, used by `bn_trim`/`bn_dupl`/`bn_replace`
(SNOBOL4-side sibling functions, unrelated to this row, already correct) — so this is not a new pattern,
just one that never got propagated to these nine Icon builtins. Switched all nine output sites from
`STRVAL(buf)` to `BSTRVAL(buf, <the already-known correct length>)`.

**Both layers were necessary and neither alone was sufficient** — layer 1 without layer 2 still shows
`left(&cset,3)` as `""` (computed right, displayed wrong); layer 2 without layer 1 never gets a correct
length to pass to BSTRVAL in the first place.

## A THIRD, SEPARATE GAP FOUND ALONG THE WAY: image()'s missing escape mnemonics

After both layers, `collate.icn`'s diff was reduced from "wrong content" to a pure escape-spelling
mismatch: every byte value already agreed with the oracle, but SCRIP's `image()` rendered `\x08 \x0b \x0c
\x1b \x7f` as hex escapes where real Icon uses the short mnemonics `\b \v \f \e \d`. Confirmed against
`collate.std`'s own 256-byte cset dump byte-for-byte (`\n \t \r` were already handled; `\x07`/BEL is
genuinely `\x07` in the oracle too, not `\a` — checked directly, not assumed). Added the five missing
`case` arms to `image()`'s string-quoting branch. `image()`'s CSET-typed branch (a separate code path,
`IS_CSET_fn`) has NO short mnemonics at all and is very likely the same gap — NOT fixed here, no failing
witness exercises it in this suite, flagged rather than guessed at.

## VERIFICATION

- `collate.icn`: byte-identical against oracle, both modes (was empty-output FAIL, both modes).
- Icon smoke: 15/15 both modes (unchanged, control arm).
- SNOBOL4 smoke: 7/7 both modes (unchanged, control arm — this file is shared runtime infrastructure
  across all seven languages).
- Full SNOBOL4 corpus gate (the real regression arm, given the shared file): **m3 PASS=1801 FAIL=0,
  m4 PASS=1801 FAIL=0 SKIP=0, ast 28/28, MISSING=0, GATE OK** — zero movement anywhere outside `collate`.
- Full JCON board: **m3 PASS 43→44, m4 PASS 40→41** (`collate` only; grepped both FAIL/CRASH/HANG name
  lists before and after — no other entry's bucket changed in either mode). DONE-WHEN still far from met
  (m3_pass=44 of the row's own `>=50` floor).

## BLAST RADIUS NOT CHASED HERE

`by_name_dispatch.c`'s builtin-ID dispatch (`BID_left` etc.) is a SHARED mechanism keyed on the function
NAME's numeric id, not on language — whether Raku, Pascal, Snocone, or Prolog ever reach these same nine
arms (as opposed to their own separately-implemented same-named builtins, e.g. the file's OTHER, unrelated
`reverse` at a different dispatch point that appears to be Raku's list-reverse) is unconfirmed. The full
SNOBOL4 corpus gate (which shares this file) is clean, which is meaningful control-arm evidence, but the
other five languages' own suites were not individually re-run — a fresh `make test` before the next
cross-language landing would close this gap cheaply if anyone needs the assurance sooner than that.

## WHOEVER RESUMES THIS ROW

`collate` is closed. Per this row's own established practice (re-diff fresh, never trust a prior pass's
size list without re-measuring): the current m3 FAIL bucket, smallest-first, no longer contains `collate`
or `lists`(oracle-disagreement, not a bug) — re-run the sweep from the current board before picking the
next target. `image()`'s CSET-branch escape gap (above) is a small, well-scoped, likely-quick next lead if
a failing witness for it turns up.
