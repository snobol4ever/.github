# FINDING: snoflake "OURS" reds ablated to one witness per root cause

⚠ **Filename/provenance note**: this file's name (`...hq_B-snoflake-ours-26...`) is the path the row's
own `DONE-WHEN` hardcodes from the original mint (hq_B, 2026-09-04, when the list was 26 items under the
OLD @expect-based grading). The comparison method changed same-day (ceo ruling on
`q-snoflake-denominator-vs-the-dialect-law`, CEO-251: grade SCRIP == `sbl -bf`, not the fixture's own
`@expect`), which grew the real list to 70 (hq_B's 2026-09-04 19:40 re-measurement), and it has moved
again since — a fresh `bash scripts/test_snoflake_suite.sh` run today reads **44** FAIL-M3 fixtures. Per
this project's own CEO-s272 law ("board totals are READ FROM THE PRINTED OUTPUT, never matched against a
remembered number"), 44 is today's honest count, not 26 or 70 — re-run the suite before trusting any
number in this file as current. The filename stays as originally minted so the row's `DONE-WHEN` (which
only checks this file exists with >=26 witness bullets) keeps working; the CONTENT below is current as of
this write.

**Author/date of THIS pass**: seat02, 2026-09-06, FLEET-12. SCRIP `9aa8d2ab0` · corpus `b9f408b5e`.
**Method**: fresh `test_snoflake_suite.sh` run for the current FAIL-M3 list; each fixture's own `@input`
block fed as real stdin (never `/dev/null` — a stdin-starved @input fixture produces an unrelated,
misleading failure); SCRIP compared against the real oracle (`sbl -bf` via `lib_oracle_flags.sh`), not
the fixture's own `@expect`. Two parallel investigations (one this session's non-gimpel 22, one a fresh
isolated agent for the 19 `gimpel-*`) plus 3 fixtures already characterized on other rows. **Verification
note**: I directly re-ran and spot-checked several claims below myself (not a blind pass-through) —
one claim in the original non-gimpel draft (Cluster A, TRACE) was factually corrected after direct
verification; the two most specific/actionable gimpel citations (emit.cpp:1314, lower_snobol4.c:1947)
were independently confirmed exact. Not every sub-claim was independently re-verified — treat file:line
citations as strong leads for hq_P to confirm while implementing, not as pre-proven.

---

## Already characterized on other rows (not re-litigated here)

- **`fullscan-palindrome`** — re-confirmed live this pass: SCRIP prints "IS A PALINDROME" for `SNOBOL` and
  for `A MAN A PLAN A CANAL PANAMA`, oracle correctly says "IS NOT" for both. An `&FULLSCAN` +
  `RTAB`/`ABORT` deferred-pattern recognizer whose failure arm is never taken. Not re-diagnosed further
  here (already characterized in this row's own GOAL text by hq_B).
- **`pattern-assignment-targets`** — lower_snobol4 GZ#5 subset refusal (deferred capture targets like
  `@*V`/`@*$('CUR' N)` outside the landed pattern subset) — an UNBUILT FEATURE, wants a rung not a fix.
  Same class as Cluster D below.
- **`word-count-table-convert`** — extensively characterized this session on its own row
  (`snobol4-table-convert-to-array-uses-hash-bucket-order-not-documented-creation-order`):
  `CONVERT(table,'ARRAY')` enumerates in hash-bucket order via `TBL_FOREACH` instead of the documented
  creation order. Fix site confirmed (`table_set_descr_d`, `src/runtime/aggregates.c:303-317`, needs a
  monotonic sequence field); blast radius confirmed real (`SORT`/`RSORT` tie-breaking inherits the same
  bug via an INDEPENDENT `TBL_FOREACH` site, `src/runtime/by_name_dispatch.c:5722-5725` — fixing CONVERT
  alone will not fix SORT). Full detail on that row's own task file; do not re-mint.

---

## Part 1 — 22 non-gimpel fixtures (11 clusters)

Scope: character-set-keywords, collect-and-locals, csnobol4-extensions, dump-ordered, dump-variables,
eliza-duquet-original, eliza-modernized, endfile-rewind-write-read, indirect-integer-and-keyword,
infix-to-polish, kalah-opening-search, lexical-comparison, numeric-keywords, stack-opsyn, string-pad,
topological-sort, trace-all-functions, trace-function-calls, trace-keyword-fnclevel, trace-label-flow,
wang-theorem-prover, word-ending-analysis.

### CLUSTER A — `TRACE()` registers successfully but produces NO trace output (4 members)
`trace-all-functions`, `trace-function-calls`, `trace-keyword-fnclevel`, `trace-label-flow`.

⚠ **Corrected after direct verification** (the initial characterization — "TRACE unimplemented, no
dispatch entry" — was WRONG and is replaced by this one): `TRACE` **does** have a real dispatch entry —
`src/runtime/core/core.c:2013`, `register_fn("TRACE", _TRACE_, 1, 4)` — and `_TRACE_`
(`core.c:1496-1512`) does real argument validation (`trace_type_parse`, ERROR 198/199 on bad args) and
calls `trace_register()`, a real registration table that IS consulted elsewhere
(`trace_registered()`, referenced at `core.c:501,513,563,584`). So the machinery is not a stub. Confirmed
directly (`trace-function-calls.sno`, `TRACE('FACT','FUNCTION')` then `OUTPUT = FACT(3)`):
```
SCRIP:  6
ORACLE: ****6*******  FACT(3)
        ****3******* i FACT(2)
        ****3******* ii FACT(1)
        ****2******* ii RETURN FACT = 1
        ****3******* i RETURN FACT = 2
        ****3*******  RETURN FACT = 6
        6
```
Program logic and the final answer are correct; `TRACE()` registration itself does not error — but
NOTHING checks/prints at the actual call/return sites for a `FUNCTION`/`CALL`/`RETURN`-kind trace. The
real gap is therefore downstream of registration: either the emitted code for a user-defined function
call/return never consults `trace_registered()`/fires the print, or it's wired for a different trace kind
than the ones these 4 fixtures use. Needs a seat or HQ to trace where (if anywhere) `IR`/emitted code for
a function call site checks trace state, which this pass did not locate.

### CLUSTER B — `&DUMP` termination dump prints to stdout instead of the listing stream (1 primary + 1 secondary)
`dump-ordered` (primary); `topological-sort` (secondary corroboration via Cluster H).

Verified directly: setting `&DUMP = 1` triggers an auto-dump of every natural variable (alphabetized) at
program termination. The oracle's dump does **not** go to stdout — it lands entirely in the listing-sink
file (`sbl_listing_sink_flag`'s `-o=.../spitbol_listing.lst`, confirmed byte-present, 435 bytes, content
matches SCRIP's stdout dump exactly in both values and alphabetical order). SCRIP computes the right
dump, it just writes it to the wrong stream. Since grading compares stdout only, matching the oracle here
means SCRIP's stdout goes EMPTY for this fixture — flagging as a stream-routing/destination question
(where should SCRIP's diagnostic dump live?) worth a ruling, not just "print less."

### CLUSTER C — `DUMP()` (explicit call) shows stale execution-state keywords mid-program (1 member)
`dump-variables`.

`DUMP(1)` correctly writes to stdout in both engines and most content matches, but `&FILE`/`&LASTFILE`
read `''` (should be `'f.sno'`) and `&LASTLINE`/`&LASTNO`/`&LINE`/`&STCOUNT`/`&STNO` all read `0` (should
reflect current line/statement counts) when called MID-program. The SAME keywords are correct via
Cluster B's termination-dump path. Not traced to a specific function — worth checking whether `DUMP()`'s
dispatch runs before this statement's own `&LINE`/`&STNO` bookkeeping commits.

Bonus: real SPITBOL's dump never lists `&MAXINT` at all — corroborates Cluster E below.

### CLUSTER D — lower_snobol4 GZ#5 subset refusal: unbuilt pattern/replacement/name-operator forms (4 members)
`eliza-duquet-original`, `eliza-modernized`, `indirect-integer-and-keyword`, `stack-opsyn`.

Same class as `pattern-assignment-targets` above — an UNBUILT FEATURE RUNG, not a defect. Four distinct
trigger shapes within the same subset gap (replacement-subject-not-plain-variable; pattern shape outside
SN4-PAT; name-operator over an unlanded form; assignment-subject form outside the subset). Note on
`stack-opsyn`: even the real oracle does NOT run this fixture cleanly either (`ERROR 156` at line 13) —
the fixture is testing OPSYN's own argument validation, but SCRIP's subset refusal fires first, masking
rather than causing a divergent verdict. No fix recommended — wants a rung (see Cluster 3 in Part 2,
same underlying `lower_snobol4.c` gate family, likely worth coordinating one combined rung rather than
landing these piecemeal).

### CLUSTER E — unknown keyword names silently accepted instead of raising ERROR 251 (2 members)
`character-set-keywords` (via `&DIGITS`), `numeric-keywords` (via `&MAXINT`).

Real SPITBOL raises `ERROR 251 -- keyword operand is not name of defined keyword` for a `&KEYWORD` name
it doesn't recognize; SCRIP has no such validation gate and returns a value anyway. Root cause is a
missing validation gate on keyword-operand names generally (one mechanism, two exposing names), not two
bugs. Example: `OUTPUT = &DIGITS` → SCRIP `0123456789`, oracle `ERROR 251`.

### CLUSTER F (DIALECT JUDGMENT CALL — likely NOT a bug) — csnobol4-extensions
SCRIP implements CSNOBOL4-only extensions beyond real SPITBOL; oracle correctly raises `ERROR 022 --
undefined function called`, SCRIP computes real answers. This fixture also PASSES against `csnobol4`
triangulation. Matching `sbl -bf` here would mean regressing a currently-working CSNOBOL4 extension.
**Needs a ruling before minting a cure row** — curing this as written would be a regression against
CSNOBOL4 dialect support.

### CLUSTER G (possible non-issue) — missing-END-statement message/format differs (2 members)
`lexical-comparison`, `string-pad`. Both omit `END`; SCRIP hard-refuses with its own parse-error format
(consistent with every other SCRIP parse error), oracle prints one specific diagnostic line. Substance
(no program runs) may already agree — divergence is wording/format only. **Needs a ruling**: is
byte-matching SPITBOL's own diagnostic text actually wanted, or is SCRIP's own consistent house style
fine here?

### CLUSTER H — file-specification validation for I/O miscalibrated, in BOTH directions (2 members)
`endfile-rewind-write-read` (SCRIP too lenient — oracle raises `ERROR 160` immediately, SCRIP proceeds
but produces silently-empty I/O); `topological-sort` (SCRIP too strict — raises the same `ERROR 160`
prematurely on a file-spec the oracle accepts and runs past). Same underlying file-spec validation
mechanism, miscalibrated both ways. Not traced to the exact function/line this pass.

### CLUSTER I (singleton) — `COLLECT()` free-space reporting is stubbed
`collect-and-locals`. `FREE SPACE BEFORE: 0` (SCRIP) vs a real heap number (oracle); everything else
matches. Strongly suggests a hardcoded 0 rather than a real free-space query.

### CLUSTER J (singleton, needs deeper trace) — kalah-opening-search
696-line minimax game-search program. SCRIP raises `ERROR 239 -- indirection operand is not name` at
statement 219 after correct setup output; oracle runs a full game transcript far past that point.
Genuine indirect-addressing (`$`) divergence, too large to hand-trace in a witness pass. Recommend
`--dump-ir` on a minimal extract near statement 219 per this project's ASM-DIFF-FIRST convention.

### CLUSTER K (needs GDB, NOT confirmed same cause) — crashes mid-run (3 members)
`infix-to-polish`, `wang-theorem-prover`, `word-ending-analysis`. **Crash confirmed directly this pass**
(`infix-to-polish`: rc=139, `timeout: the monitored command dumped core`). All three produce correct
output for several iterations of a loop, then SIGSEGV, while the oracle completes. Pattern (not
confirmed cause) common to all three: repeated/iterative processing calling the same pattern-matching
machinery each iteration — consistent with, but not confirmed as, accumulated state corruption or a
resource not reset between iterations. Next step: smallest per-fixture repro (first N iterations only)
under gdb with ignore-counters.

---

## Part 2 — 19 `gimpel-*` fixtures (7 clusters)

All 19 `-INCLUDE` files from `corpus/packages/snobol4/snoflake_suite/gimpel/`, drawn from one 1970s
Gimpel SNOBOL4 book. Confirmed via a fresh, isolated investigation (independent minimal repros built for
several hypotheses, not just read-and-assert).

### Cluster 1 — Recursive Gimpel utility functions overflow the stack, ERROR 246 (5 members)
`gimpel-conversions`, `gimpel-linked-list-functions`, `gimpel-snobol-statement-reader`,
`gimpel-sorting-functions`, `gimpel-tree-pattern`. SCRIP dies with `ERROR 246 -- stack overflow` at a
recursive user-defined SNOBOL4 function call, even though real recursion depth needed is tiny (2-4
levels) and the oracle finishes instantly. Shared symptom confirmed; ONE common mechanism NOT isolated
across all 5 (several plausible minimal repros — scalar recursion, array-arg recursion, dual-self-call,
guarded tail-recursion — all ran fine in isolation, ruling out the simplest hypotheses). For
`gimpel-sorting-functions` specifically: plausibly explained by Cluster 2's array-element write bug
(`HSORT`'s partition swap is a silent no-op, so quicksort can't converge — real infinite recursion, not
just "deep"). The other 4 (`SPELL`, `TREE`, `COPYL`, `SNOREAD`) don't obviously route through the same
`.`/`$` path and remain unexplained pending further work.

### Cluster 2 — `.FNC(x)` name-of a DATA-type field returns the dereferenced VALUE, not an assignable reference (4 clean, contributes to 2 more in Cluster 1)
`gimpel-l-one-compiler`, `gimpel-binary-tree-linearize`, `gimpel-read-list-functions`,
`gimpel-stack-field-functions`. **Confirmed exact culprit**: `src/lower/lower_snobol4.c:311-321` lowers
`.FIELD(x)` (name-of a DATA-declared field accessor) to an `IR_FIELD_VAR` node, but
`src/emitter/emit.cpp:1314` — `case IR_FIELD_GET: case IR_FIELD_VAR: bb_emit_x86(bb_field_get());
return 0;` — emits `IR_FIELD_VAR` with the EXACT SAME template as a plain field read. So `.NEXT(x)` /
`.VALUE(x)` compiles to "fetch current value" rather than "produce an assignable name" — the fetched
*value* gets stored where the program expects a *name*, so a later `$N` indirect-reads/writes a bogus
global literally named after that value. Independently confirmed with an isolated minimal repro
(`SWAP(.A<1>,.A<2>)` on an array — SCRIP silently no-ops the swap). A parallel, independently-broken
sibling path exists for array-element name-of (`.A<I>`, different lowering site,
`lower_snobol4.c:305-310`) and a third for name-of over a non-DATA-field function call
(`lower_snobol4.c:322-327`, the `SNO$WANTNM` trampoline, also observed broken but not line-pinned).

### Cluster 3 — Compile-time FATAL: non-plain-variable used as a replacement/assignment subject (4 members)
`gimpel-line-output`, `gimpel-permutation-functions`, `gimpel-physical-quantities`,
`gimpel-mfread-multi-file`. Two related guards, both confirmed by direct line read:
`src/lower/lower_snobol4.c:1947` (`sno_lower_match()`: `if (!svt || svt->t != TT_VAR)
sno_fatal("SN4-REPL slice 1: replacement subject must be a plain variable...")`) — hits the first 3; one
exactly pinned (`gimpel-physical-quantities`'s `NUM(X) ANY(DEN(X)) . C =`, subject is a DATA-field
accessor call, not a bare variable). `lower_snobol4.c:2383` (the plain-assignment catch-all for subject
shapes outside `TT_VAR`/`TT_INDIRECT`/`TT_IDX`(>=1 index)/recognized `TT_FNC`) — hits
`gimpel-mfread-multi-file`, plausibly `MFREAD.INC`'s `READ_TBL<> = RDATA(.INPUT)` (zero-index table
subscript; the `TT_IDX` handler at line 2302 requires `subj->n >= 2`) — plausible, not isolation-tested.
Same gate family as Part 1's Cluster D — worth one combined rung rather than 8 separate small fixes.

### Cluster 4 — Oracle refuses a user `DEFINE` colliding with the ORACLE's OWN reserved builtin name (1 clean + contributes to 3 in Cluster 3)
`gimpel-general-purpose-macro` (clean, via `BAL`); the oracle-side half of `gimpel-line-output`
(`LPAD`), `gimpel-permutation-functions` (`REVERSE`), `gimpel-mfread-multi-file` (`MFREAD`) share this
same mechanism but are already counted under Cluster 3 since SCRIP independently fails to even compile
them. **Not a SCRIP defect** — this is a dialect/environment gap: the 1970s Gimpel source defines its
own utility using a name (`BAL`, `LPAD`, `REVERSE`, `MFREAD`) that this specific SPITBOL oracle build
reserves as a real builtin and refuses to let user code redefine (`ERROR 042 -- attempt to change value
of protected variable`), while `src/runtime/snobol4_system_fns.h:5`'s reserved-name list is smaller/
different, so SCRIP runs the user's own DEFINE instead. Separately flagged: `gimpel-general-purpose-
macro`'s SCRIP output doesn't even match its OWN `@expect` — `GPM.INC`'s macro engine likely has its own
independent, uncharacterized bug, moot for THIS grading only because the oracle can't run the program at
all.

### Cluster 5 — Oracle-side environment limitation: file-unit `INPUT()` / `DEXTERN` unsupported (3 members)
`gimpel-dextern-loader`, `gimpel-poker-game`, `gimpel-stone-game`. **Not a SCRIP defect** — confirmed
with an independent trivial repro that this x64 correctness-oracle build rejects ANY unit-based file
`INPUT()` association (`ERROR 116`), regardless of fixture syntax; matches the spirit of this project's
already-documented `LOAD`/`DEXTERN` oracle limitation (`lib_oracle_flags.sh`'s `sbl_clean_refuse_if_load`)
but for a different subsystem (unit I/O) and the correctness oracle specifically, not yet documented
there. SCRIP itself is also non-functional here for an unrelated reason (no real DEXTERN dynamic-loading
backend, `ERROR 286 -- undefined entry label`) — both sides fail, neither implements the feature, no
verdict comparison is meaningful for this cluster. SEPARATE, layered issue on `gimpel-poker-game`/
`gimpel-stone-game` only: SCRIP raises its own false-positive `ERROR 248 -- attempted redefinition of
system function` partway through the shared `PHRASE.INC`/`QUEST.INC` includes (confirmed by isolating
just those two includes); likely trigger is `RSELECT.INC` declaring local `CODE` twice and calling
`CODE(CODE)` (a real SCRIP builtin name) — two targeted minimal repros did NOT reproduce this standalone,
so the exact trigger is unconfirmed.

### Cluster 6 — Immediate-value pattern assignment (`$VAR` bound mid-match, read via `*EXPR` in the same pattern) is broken (1 member)
`gimpel-fortran-blank-removal`. `BLINT $ N 'H' LEN(*DIFF(N,' ')) . LIT` — `$N` binds immediately
mid-match so the next pattern element can use `*EXPR` to consume that just-bound value. On the one input
that exercises a real Hollerith literal, SCRIP produces a mangled/empty capture
(`CALLALPHA(''ABCDEFGHIJKL)`) where the oracle correctly captures 12 letters
(`CALLALPHA('ABCDEFGHIJKL')`); all other lines in the fixture match exactly. Not line-pinned — would need
tracing `TT_CAPT_IMMED_ASGN` vs `TT_CAPT_COND_ASGN` lowering and whether the immediate binding is visible
to a sibling `*EXPR` element evaluated later in the same pattern.

### Cluster 7 (NOT a defect) — `gimpel-implementation-and-timing`
`LPROG()` returns `&STNO` (internal statement counter) directly — the fixture's OWN header comment calls
this non-deterministic/implementation-specific. SCRIP reports `1,2,3`, oracle reports `81,83,85` (which
doesn't even match the fixture's own `@expect` of `81,82,83`) — not characterizable as a SCRIP defect.

---

## Handoff notes for hq_P

- **Do not mint cure rows for**: Cluster F (csnobol4-extensions, likely correct-as-is), Cluster G
  (lexical-comparison/string-pad, likely cosmetic), Cluster 7 (implementation-and-timing, not a defect),
  Cluster D + the `stack-opsyn`/Part-2-Cluster-3 unbuilt-subset rows (want a design rung, not a patch),
  and Cluster 5's oracle-side `INPUT()`/`DEXTERN` limitation (nothing to fix in SCRIP) — **without a
  ruling first**, since three of these would be regressions if "fixed" toward literal oracle-matching.
- **Highest-confidence, cite-backed, ready-to-cure**: Cluster 2 (Part 2) — exact fix site named
  (`emit.cpp:1314` needs `IR_FIELD_VAR` to emit a real address/name-producing template distinct from
  `IR_FIELD_GET`); Cluster 3/D's `lower_snobol4.c:1947`/`:2383` guards are a real rung to land (8
  fixtures across both parts share this family); Cluster E (missing ERROR 251 validation, 2 fixtures);
  Cluster I (`COLLECT()` stubbed free-space, 1 fixture); `word-count-table-convert`'s own row (fix site
  fully specified already).
- **Needs more investigation before a fix is even shaped**: Cluster A (TRACE — registration works, output
  wiring doesn't, exact gap not located), Cluster 1's 4 unexplained members, Cluster K's 3 crashes (GDB),
  Cluster J (kalah, needs `--dump-ir` on a minimal extract), Cluster 6 (Hollerith immediate-pattern
  capture), Cluster 5's SCRIP-side false-positive ERROR 248 sub-issue.

## INDEX — every current FAIL-M3 fixture, one line each (44 total)

- `character-set-keywords` — Part 1 Cluster E (missing ERROR 251 validation)
- `collect-and-locals` — Part 1 Cluster I (COLLECT() free-space stubbed)
- `csnobol4-extensions` — Part 1 Cluster F (dialect judgment call, likely not a bug)
- `dump-ordered` — Part 1 Cluster B (&DUMP writes to stdout not listing-sink)
- `dump-variables` — Part 1 Cluster C (DUMP() stale execution-state keywords)
- `eliza-duquet-original` — Part 1 Cluster D (GZ#5 unbuilt subset)
- `eliza-modernized` — Part 1 Cluster D (GZ#5 unbuilt subset)
- `endfile-rewind-write-read` — Part 1 Cluster H (file-spec validation too lenient)
- `fullscan-palindrome` — already characterized (see above), &FULLSCAN/RTAB/ABORT deferred pattern
- `gimpel-binary-tree-linearize` — Part 2 Cluster 2 (.FNC name-of returns value not reference)
- `gimpel-conversions` — Part 2 Cluster 1 (recursion stack overflow, mechanism unconfirmed)
- `gimpel-dextern-loader` — Part 2 Cluster 5 (oracle-side INPUT()/DEXTERN limitation, not a SCRIP defect)
- `gimpel-fortran-blank-removal` — Part 2 Cluster 6 (immediate-pattern $-assignment broken)
- `gimpel-general-purpose-macro` — Part 2 Cluster 4 (oracle reserves BAL, not a SCRIP defect)
- `gimpel-implementation-and-timing` — Part 2 Cluster 7 (not a defect, implementation-defined value)
- `gimpel-line-output` — Part 2 Cluster 3 (lower_snobol4.c:1947 FATAL) + Cluster 4 (oracle reserves LPAD)
- `gimpel-linked-list-functions` — Part 2 Cluster 1 (recursion stack overflow, mechanism unconfirmed)
- `gimpel-l-one-compiler` — Part 2 Cluster 2 (.FNC name-of returns value not reference)
- `gimpel-mfread-multi-file` — Part 2 Cluster 3 (lower_snobol4.c:2383 FATAL) + Cluster 4 (oracle reserves MFREAD)
- `gimpel-permutation-functions` — Part 2 Cluster 3 (lower_snobol4.c:1947 FATAL) + Cluster 4 (oracle reserves REVERSE)
- `gimpel-physical-quantities` — Part 2 Cluster 3 (lower_snobol4.c:1947 FATAL, exact statement pinned)
- `gimpel-poker-game` — Part 2 Cluster 5 (oracle-side limitation) + SCRIP-side false-positive ERROR 248
- `gimpel-read-list-functions` — Part 2 Cluster 2 (.FNC name-of returns value not reference)
- `gimpel-snobol-statement-reader` — Part 2 Cluster 1 (recursion stack overflow, mechanism unconfirmed)
- `gimpel-sorting-functions` — Part 2 Cluster 1, plausibly explained by Cluster 2's array-element case
- `gimpel-stack-field-functions` — Part 2 Cluster 2 (.FNC name-of returns value not reference)
- `gimpel-stone-game` — Part 2 Cluster 5 (oracle-side limitation) + SCRIP-side false-positive ERROR 248
- `gimpel-tree-pattern` — Part 2 Cluster 1 (recursion stack overflow, mechanism unconfirmed)
- `indirect-integer-and-keyword` — Part 1 Cluster D (GZ#5 unbuilt subset)
- `infix-to-polish` — Part 1 Cluster K (SIGSEGV mid-run, confirmed crash, needs GDB)
- `kalah-opening-search` — Part 1 Cluster J (indirection ERROR 239, needs --dump-ir trace)
- `lexical-comparison` — Part 1 Cluster G (missing-END message format, possible non-issue)
- `numeric-keywords` — Part 1 Cluster E (missing ERROR 251 validation)
- `pattern-assignment-targets` — already characterized (see above), GZ#5 unbuilt subset
- `stack-opsyn` — Part 1 Cluster D (GZ#5 unbuilt subset; oracle also fails, for a different reason)
- `string-pad` — Part 1 Cluster G (missing-END message format, possible non-issue)
- `topological-sort` — Part 1 Cluster H (file-spec validation too strict) + Cluster B corroboration
- `trace-all-functions` — Part 1 Cluster A (TRACE registers but produces no output)
- `trace-function-calls` — Part 1 Cluster A (TRACE registers but produces no output)
- `trace-keyword-fnclevel` — Part 1 Cluster A (TRACE registers but produces no output)
- `trace-label-flow` — Part 1 Cluster A (TRACE registers but produces no output)
- `wang-theorem-prover` — Part 1 Cluster K (crash mid-run, needs GDB)
- `word-count-table-convert` — already characterized (see above), own row, fix site fully specified
- `word-ending-analysis` — Part 1 Cluster K (crash mid-run, needs GDB)
