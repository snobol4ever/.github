# FINDING 2026-09-04 (seat02, FLEET-16, hq_B lane) — Icon Arizona suite: `char()`/`integer()` radix-string coercion shared and cured, `image()`'s embedded-NUL string truncation cured, cset-of-NUL split into its own row as a representation defect, not a read-site bug

**Row:** `icon-arizona-suite-49-reds-censused-by-class-and-cured`. **Trees:** measured on SCRIP `57ebba8a` → merged to `bfa1ea95` (pull mid-session, 7 upstream commits), corpus `e351e9a4c`, RT_OPT=-O0. **Oracle:** `/home/resources/icon-master/bin/icon` v9.5. **Witness:** `corpus/packages/icon/arizona_tests/general/cset.icn`.

## What was diagnosed vs. what was actually true

`icon-arizona-class-radix-notation-wrong-value` (seat04, 2026-09-04T01:58) claimed a source-level lexer bug: `write(16r2D)` printing 16 instead of 45. Re-tested directly against the current tree and against icont — it does not reproduce; `16r2D`/`32rU`/`8r113` as literal tokens already lex and evaluate correctly (45/30/75, matching icont). The lexer was never the problem.

What actually fails is one layer down: `cset.icn` line 55 calls `char(s)` where `s` is a *string* (`"32rU"`, from an array literal), not a numeric token. `char()` coerces a non-integer argument to an integer at *runtime*, and that path is separate code from the lexer. Re-diagnosing against the real failing witness (`diff` against `cset.std`) rather than trusting the original single-line repro is what found the real site.

## Root cause 1 (cured): `char()`/`chr()` had no radix-string coercion; `integer()` already did, unshared

`src/runtime/by_name_dispatch.c`, `BID_char`/`BID_chr` (~line 4580, pre-fix):
```c
int n = (int)(IS_INT_fn(av) ? av.i : (long long)strtol(VARVAL_fn(av)?VARVAL_fn(av):"0",NULL,10));
```
`strtol(s, NULL, 10)` stops at the first non-base-10-digit character. `strtol("32rU", NULL, 10)` = 32, discarding everything from `r` onward — the exact "evaluates to just the base" symptom originally attributed to the lexer.

`BID_integer` (~line 4493) already had a complete, correct Icon-numeral parser (optional sign, `BASErDIGITS` with base 2–36, real fallback) written inline — verified `integer("32rU")` = 30 and `integer("16r2D")` = 45 were **already right** before this fix. Two builtins, one needing radix support and already lacking it, the other having it and not sharing it — the textbook shape this project calls a class defect once you look, not two unrelated bugs.

**Cure:** extracted `integer()`'s radix-recognition block verbatim into a new static helper `icon_radix_int(const char *s, long long *out)` (returns 1 + value on a full-string match, 0 otherwise — same recognition rules as before, byte-for-byte), refactored `integer()` to call it (pure behavior-preserving refactor — confirmed via before/after on `integer("32rU")`/`integer("16r2D")`), and wired `char()`/`chr()` to try the helper first, falling back to the original `strtol` for non-radix strings (unchanged behavior there).

**Verified:** `write(16r2D); write(32rU); write(8r113)` via `char()`-on-string in the actual witness path now = icont exactly.

## Root cause 2 (cured, string case only): `image()`'s default string branch used `strlen()`, not `.slen`

`src/runtime/by_name_dispatch.c`'s `BID_image` (nargs==1) default-string branch computed display length via `strlen(s)`, stopping at an embedded NUL byte. The correct idiom already exists twice in `src/runtime/pattern_match.c` (`(arr.slen && arr.slen != 0xFFFFFFFFu) ? (int)arr.slen : (int)strlen(s)`) — `image()` just wasn't using it. One-line cure, same idiom.

**Verified:** `write(image("a" || char(0) || "b"))` now prints `"a\x00b"` matching icont exactly (was `""`).

**Checked, not chased:** `write()` is also named in the original GOAL text. Every failing line in `cset.icn` passes a raw string through `image()` first (which now correctly escapes an embedded NUL into safe printable text) before it ever reaches `write()`, so `write()`'s own raw-string path (`out_write_str`, no length parameter at all) is never exercised with an unescaped NUL by this witness. A real, separate concern — not fixed here because nothing currently measured requires it.

**Audited, not swept:** ~15 other bare `strlen(s)`-on-descriptor call sites exist across `by_name_dispatch.c` (repl/center/detab/entab/trim/scan builtins), `pattern_match.c`, and `rt_runtime.c`. None is what's failing in the confirmed witness. Named in `icon-arizona-class-string-embedded-nul-truncated`'s own QA section rather than patched blind — each would need its own oracle-verified witness first, and "the census found N sites" is not the same claim as "N sites are bugs."

## Root cause 3 (found, NOT cured — split into its own row): csets cannot represent byte value 0 as a member at all

The same `image()` handler's cset branch calls `cset_canonical()` (`src/parsers/icon/icon_runtime.c:54`), whose representation is a plain NUL-terminated C string where each member byte (0–255) is encoded as one raw byte. A cset containing byte value 0 as a member is indistinguishable from "end of buffer" to `cset_canonical()`'s own scan (`for (const unsigned char *p = ...; *p; p++)`) — it can never even see that member, let alone canonicalize it. `CSETVAL` hardcodes `.slen = 0xFFFFFFFFu` (the project's own "not tracked" sentinel) for every cset, so there is no fallback length field to consult the way there is for plain strings.

This is a representation defect (needs an explicit length carried beside the canonical buffer, or a fixed-size bitmap, i.e. a real design decision) — not a `strlen`-vs-`.slen` read-site swap. Split out of `icon-arizona-class-string-embedded-nul-truncated` (whose GOAL only ever described the string case) into a new row, `icon-arizona-class-cset-cannot-represent-nul-member`, deliberately left uncured with the precise blocker named rather than patched around.

## Verdicts, verified

- Minimal witnesses (both roots): scrip = icont exactly, both roots.
- `integer()` unaffected (regression-checked): `integer("32rU")`=30, `integer("16r2D")`=45, unchanged.
- Full `cset.icn` diff against its `.std` oracle: shrank from ~11 differing lines to 2, both now attributable solely to the split-off cset-NUL row (re-diffed after each fix landed to confirm attribution, not assumed).
- `strip_comments.py --check`: 0 (see driveby fix below).
- Style gate driveby: an upstream commit (`589b0c78`, landed mid-session via `git pull --rebase`) had added four `/* */` comments to this same file, violating the project's zero-comments-in-src rule and redding `make test`'s style gate for anyone who pulled it — not this row's defect, but blocking a clean push for the next puller regardless. Cured (comments deleted, zero behavior change — comments do not compile) rather than left red.
- Arizona suite total: m3_pass/m4_pass unchanged at 43/89 — both fixed files (`cset.icn`, `radix.icn`) have other, independent, already-tracked failures beyond what this session touched, so neither flips to a full byte-exact PASS. Consistent with every prior session on this row's own accounting.
- STRICT rung suite: found reading TOTAL=105 (PASS=73 FAIL=7 BADEXIT=1 XFAIL=24 MISSING=2), not the row's stale TOTAL=298 literal. Confirmed via a control-arm re-run (`git stash`, rebuild, re-run) that reproduced 105 identically with this session's fix absent — a pre-existing, structural denominator shift from today's FLEET-16 RE-CUT corpus reorganization (`tests/icon/config/LADDER.tsv`, `tests/icon/ALL.xfail` both changed in the same pull), not caused by this session's work. Re-cut in the row's own DONE-WHEN.
- Icon master board: GREEN, entries=731, run-graded m3/m4 PASS=577/577, ast-graded PASS=153/153 (watermarks held).

## Population and limits

Two builtins share one new helper (`char`/`chr`, `integer`); one builtin gains one corrected length check (`image()`'s string branch). No template, emitter, or lowerer file touched — pure runtime (`src/runtime/by_name_dispatch.c`). No new globals. The cset representation gap is real, confirmed, and intentionally left open with its exact blocker named.
