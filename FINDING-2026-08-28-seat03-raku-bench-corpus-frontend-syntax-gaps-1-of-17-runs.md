# FINDING 2026-08-28 (seat03): the raku-bench correctness floor is 1/17, not "presumably fine" — SCRIP's raku frontend rejects most real-world Raku syntax despite a green 51/51 crosscheck suite

**Build:** SCRIP `b6d11a09`, `make pristine`, `RT_OPT=-O0`. corpus `1606d8fc`. Load 2.37/1 at measure time (correctness pass; no timing quoted — this finding is upstream of any timing work). Row: `bench-rivals-raku-pascal`.

## The one cause

`corpus-import-raku-bench` landed 17 license-vetted, `.ref`-verified kernels (corpus `4d4efe0f6`) on 2026-08-27, correctly unblocking this row's stated RAKU blocker ("corpus not imported"). But nobody had yet run those 17 kernels through SCRIP itself — the row's own NEXT still read "RAKU — still hard-blocked... this row's gate will keep refusing raku until [the corpus] lands," which is now STALE in its *reason* even though the *conclusion* (gate still refuses) happens to still hold. Measured this pass, pristine build, real (empty, correctly so per the corpus README) stdin: **16 of 17 kernels fail to PARSE** — not a runtime defect, a frontend one. `send-more-money-loops` is the only kernel that runs and matches `.ref`, in both m3 and m4.

This is the same shape of trap RULES.md keeps re-finding — SCRIP's own `test_crosscheck_raku.sh` is **51/51 PASS**, and that suite is real and passing, but it is not the *populator* for what real Raku programs contain. A green feature-test suite answered "does SCRIP's raku frontend handle the constructs *we already wrote tests for*", which is a narrower question than "can SCRIP's raku frontend parse Raku code nobody at this project wrote" — and the difference between those two questions is exactly the gap this finding measures.

## Measured state of the 17 kernels (pristine, m3; m4 confirmed mode-independent, see below)

| kernel | m3 | first blocking construct |
|---|---|---|
| send-more-money-loops | **PASS** (m4 also verified PASS) | — |
| divide-and-conquer | parse-fail | sigil-less `my \SCALE = 10;` |
| pi-sequential-iteration | parse-fail | sigil-less `my \SCALE = 1000000;` |
| merge-sort | parse-fail | sigil-less params `sub merge(@a, \p, \z, \r)` |
| insertion-sort | parse-fail | hyphenated sub name `sub insertion-sort(@a)` |
| rc-perfect-shuffle | parse-fail | hyphenated sub name `sub perfect-shuffle (@deck)` |
| rc-forest-fire-stringify | parse-fail | hyphenated type name `enum Cell-State <Empty Tree Burning>;` |
| point_class_add1 | parse-fail | colon-pair `:x($!x + $b.x)` |
| point_class_add | parse-fail | colon-pair `:x($!x + $b.x)` |
| point_class_add2 | parse-fail | `nqp::create` (MoarVM-internals call — see note) |
| rc-mandelbrot | parse-fail | typed defaulted param `sub MAIN(Int $w = 31, ...)` |
| spinner | parse-fail | typed defaulted param `sub MAIN(Int $h = 64, ...)` |
| rc-man-or-boy-test | parse-fail | parameter trait `sub A ($k is copy, ...)` |
| rc-self-describing-numbers | parse-fail | hyperoperator `+«$s.comb` |
| rc-9-billion-names | parse-fail | itemized-array composer `my @todo = $[1];` |
| rc-dragon-curve | parse-fail | chained `+&`/`+<` bitwise ops feeding `?? !!` |
| string-escape | parse-fail | multi-line array-literal argument (least characterized, see below) |

**⚠️ This table names only the FIRST error SCRIP's parser reports per kernel.** Bison/flex parsers stop at the first syntax error, so a kernel may hit a *second*, still-uncatalogued gap once its first one is fixed — do not assume fixing the listed construct is sufficient to turn a row green; re-measure after each fix.

## m4 confirmed mode-independent (spot-checked, not exhaustive)

`insertion-sort` gives the byte-identical parse error under `--compile` as under `--run` — expected and architecturally guaranteed (CLAUDE.md: parsing happens once per the extension dispatch, before the m3/m4 branch), not re-verified per-kernel. `send-more-money-loops` was verified end-to-end in **both** modes: m4 `--compile` → `as`/`gcc -no-pie` link against `out/libscrip_rt.so` → binary output byte-matches `.ref`.

## Not the Pascal defect — a different, upstream mechanism

`pascal-m4-for-spine-leak-64b-per-iter`'s open NEXT (seat07/hq_C, same day) flags that Pascal's `if`/`elseif` and **"Raku's `if`"** both build `IR_BINOP_TEST`, raising a live question of whether the same `zd_omega_head()`-only-matches-`IR_CMP_TEST` gap reaches Raku's m4 arm too. **This finding does not test that question** — every failure here is a **parse-stage** rejection (7-16ms, rc=1, "raku parse/lex error"), never reaching LOWER/emit at all, so none of these 16 kernels exercise the zd_plan mechanism seat07 described. Whether Raku m4 has its own copy of that spine-leak once parsing is fixed is **still open** and cannot be measured until enough of the table above is cured to produce a kernel that parses, uses `if` inside a loop, and reaches m4 codegen. Flagging so the next seat on either row does not conflate the two.

## `string-escape` — least characterized, flagging rather than guessing

```raku
my $s = $d.trans(   ['"',  '\\',   "\b", "\f", "\n", "\r", "\t"]
```
Reported error is a generic "syntax error" at this line, not a lex error on a specific character — could be the multi-line array-literal-as-call-argument shape, could be something on a continuation line not shown here. Did not narrow further (would need bisection inside the parser grammar, which is language-frontend work, not this row's lane — see next section).

## `point_class_add2` / `nqp::create` — separate note, lower priority

Already flagged in `corpus/benchmarks/raku/README.md` as a Rakudo-version bit-rot fix (`nqp::create` needing an explicit `use nqp;` on current Rakudo that upstream's 2013-vintage code didn't need) — this is a call into MoarVM implementation internals, not idiomatic Raku surface syntax. Lowest-value item in this list to chase; the other 15 gaps are ordinary, common Raku constructs (sigil-less bindings, kebab-case identifiers, colon-pairs, typed signatures, hyperoperators — all core-language, all likely to recur in any future Raku corpus, not just this one).

## Duty this creates

- **This row (`bench-rivals-raku-pascal`) stays correctly BLOCKED on raku, same shape as the pascal arm, for a corrected reason: not "corpus missing" (cured) but "frontend cannot parse the corpus that exists."** `test_gate_bench_rivals_coverage.sh raku` continues to REFUSE (rc=2) honestly — 16 of 17 kernels have no committed triangulation row and none belongs in `EXCLUDED.tsv` (that file is for kernels the *timing angle* structurally cannot bracket, e.g. `.input`-driven; a parser gap is a real defect to fix, not a permanent design exclusion — writing these 16 into `EXCLUDED.tsv` would misrepresent a bug as a decision).
- **A new row is needed to close the parser gaps** — this is language-frontend grammar/lexer work (bison/flex, `raku.tab.*`/`raku.lex.*` per the build), squarely outside this benchmarking row's lane and outside any GOAL file this seat was dispatched to read. Minting `raku-frontend-real-world-syntax-gaps` with this table as its starting brief rather than attempting any of the ~9 independent grammar features blind, in one session, un-reviewed.
- **The crosscheck suite's blind spot is itself worth a line to whoever owns raku frontend health:** 51/51 green did not predict this. Not filing a separate row for that alone — the new frontend row's own DONE-WHEN (get real kernels parsing) will organically grow crosscheck coverage for whichever constructs it adds support for; a seat chasing "make the crosscheck suite representative" as its own goal would be optimizing the wrong thing before the underlying gap closes.
