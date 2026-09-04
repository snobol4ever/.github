# FINDING 2026-09-04 seat08: csnobol4_suite's last 6 untraced names — 3 new classes, 2 resolved as not-bugs

## Headline

Row `snobol4-csnobol4-suite-non-pass-censused-by-class-and-cured` (hq_P assigned, released from seat09 at
the FLEET-16 restart) left 7 names fully untraced: `alis convert err float setexit2 setexit4` (+ `genc`,
deferred — 1729 lines, needs `global.procs` and other external resources, still not attempted). All 6
non-`genc` names traced this sitting, each to a minimal witness, each checked against **both** real
oracles (csnobol4 AND SPITBOL `sbl -bf`) wherever the vendored `.ref` alone left the "is this actually a
SCRIP defect, or a dialect difference SCRIP is right to not match" question open — SCRIP's semantic
authority is SPITBOL (CLAUDE.md), not csnobol4, so a csnobol4-only `.ref` mismatch is not by itself
evidence of a bug. That check reversed one of the two closable names outright (§2).

Two names are dialect gaps, not SCRIP bugs (§1, §2) — resolved, not minted. Three names census into three
new defect classes, two of which turn out to be **the same mechanism already characterized from a
different corpus** by an earlier seat08 session's `FINDING-2026-09-03-seat08-snobol4-master-xfails-...`
(§3, §4) and were never actually minted into the queue (that FINDING's own §7: "ready to mint... NOT
filed as queue rows" — hq_P had not yet ranked them). This sitting's csnobol4_suite witnesses are
independent, cross-corpus confirmation, so those two are minted now rather than left pending further.

## Method

For each name: read the `.sno` source, run it through SCRIP `--run` (harness-faithful invocation — cwd
inside a scratch copy of the suite, matching `test_snobol4_csnobol4_suite.sh`'s own convention, since
`&LASTFILE`-dependent output is invocation-path-sensitive — see §5), diff against `.ref`. Where the
mechanism was unclear or the `.ref`-vs-SCRIP disagreement might be dialect rather than defect, built a
**minimal ablated witness** (not the vendored program) and ran it against **both** oracles directly:
`/home/resources/csnobol4/snobol4 -b` (this suite's own oracle) and `/home/resources/x64/bin/sbl -bf`
(SPITBOL, SCRIP's actual semantic authority). Where SCRIP matches SPITBOL but not csnobol4, that is a
dialect difference and SCRIP is correct; where SCRIP matches neither, that is a real defect regardless of
which exact error code/message each dialect uses (the two dialects routinely disagree on the *number* and
*text* while agreeing that *some* error is correct — csnobol4 and SPITBOL never share error-code numbering,
so "same behavior class, different code" across the two oracles is itself confirming evidence, not a
contradiction).

## 1. `alis` — NOT a SCRIP defect. CSNOBOL4-only `\` operator; SPITBOL rejects it too.

`alis.sno` (a linked-list arbitrary-precision integer type via `OPSYN`) fails to parse at lines 57/59:
`LINK LINK = \INTEGER(I) L(I) :(RETURN)`. SCRIP: `unexpected char '\''`. Minimal witness
(`X=5; OUTPUT=\INTEGER(X)`) against SPITBOL: **`ERROR 230 -- syntax error: illegal character`** at the
same `\`. SPITBOL rejects the backslash operator exactly as SCRIP does — it is a CSNOBOL4-only extension,
not standard/SPITBOL syntax, matching the already-established "CSNOBOL4-only builtins/operators" dialect
class (RULES.md; `FINDING-2026-08-27-seat06-csnobol4_suite-triage-eight-classes-three-are-not-scrip-bugs.md`).
Not a defect. Not minted.

## 2. `float` — NOT a SCRIP defect. SCRIP's float formatting matches SPITBOL exactly; csnobol4 differs.

`float.sno` prints `1.0/1000`, `1.0/1000000`, `1.0/1000000000`. SCRIP: `0.1e-2` / `0.1e-5` / `0.1e-8`.
`.ref` (csnobol4): `0.001` / `1e-06` / `1e-09`. **This looked like a SCRIP formatting bug** (wrong
decimal/scientific threshold, denormalized mantissa, unpadded exponent) until checked against SPITBOL —
which prints **`0.1e-2` / `0.1e-5` / `0.1e-8`, byte-identical to SCRIP's current output**, on the identical
minimal witness. SCRIP already matches its actual semantic authority; it is csnobol4 that formats floats
differently (earlier decimal/scientific cutover, normalized mantissa, zero-padded 2-digit exponent) — a
dialect difference, not a defect, and "fixing" this to match csnobol4 would make SCRIP diverge from
SPITBOL, which is the wrong direction per CLAUDE.md's stated semantic authority. Not a defect. Not minted.
**Only checked because this row's own method requires the second-oracle check before closing any name as
a bug** — the `.ref`-only read would have shipped a wrong classification here.

## 3. SETEXIT's registered trap is never invoked — TWO independent triggers, likely one root cause

`setexit2.sno` (`SETEXIT(.xxx)` then falls off the end of the statement list, no error, no explicit
`:(END)`) — SCRIP prints nothing at all; the trap body never runs. Live csnobol4, invoked the same
harness-faithful way, DOES fire the trap (matches `.ref`'s structure exactly; the `.ref` vs. live-oracle
byte mismatch that flags this name REGEN-CANDIDATE in the suite board is a **separate, unrelated**
`&LASTFILE`-is-invocation-path-dependent fixture nuance — see §5 — not evidence against this finding).
`setexit4.sno` (`SETEXIT(.f)` at top, plus `TRACE`/`&Z=1`/errors later) — SCRIP prints only the 3 literal
top-level `OUTPUT` lines (`a`/`b`/`c`); no trap output, no trace output, confirming the same non-firing
with a structurally different (and much noisier) witness. A minimal ablation stripping setexit4 down to
just `SETEXIT(.f)` + two `OUTPUT`s + `:(END)` (no TRACE, no keyword assignment) reproduces the same
zero-output result, isolating "trap never fires" from every other ingredient in setexit4.

**This is very likely the same mechanism as `FINDING-2026-09-03-seat08-snobol4-master-xfails-...`'s class
#1, `setexit-not-invoked-under-errlimit-survival`** (witnesses `keyword_replace_1/2`,
`keyword_replace_branch_10/11`, from the unrelated `ALL.sno` master-xfail corpus): "when `&ERRLIMIT` is set
nonzero and survives an arithmetic runtime error (division by zero), an armed `SETEXIT(.H)` handler is
never invoked." That FINDING's own §7 says all 14 of its classes were "ready to mint... NOT filed as queue
rows" pending hq_P's ranking — this one never was. The two triggers differ (this sitting: **normal
termination**, no error at all; that FINDING: **surviving a runtime error under ERRLIMIT**), so they are
kept as two witness sets under **one class row**, not silently merged into one claim, in case the two
triggers turn out to route through different code paths — but the natural hypothesis, worth stating for
whoever cures it, is that SETEXIT's trap registration/dispatch simply is not wired to ANY invocation site
yet, and one fix (wiring the dispatch itself) likely closes both trigger shapes at once.

`setexit4` additionally cannot even reach ITS error-triggered path today, because of §4 below — the
`&Z=1` that is supposed to raise the error setexit4's trap would catch never raises anything in the first
place. Noted so whoever cures SETEXIT doesn't chase a red that is actually gated behind a different,
already-separately-classified defect.

Minted: `snobol4-setexit-trap-never-invoked` (this sitting's two witnesses + cross-reference to class #1's
four witnesses; DONE-WHEN covers the confound-free minimal ablation, not the noisier vendored programs).

## 4. Subscripting an undeclared/non-array/table operand raises no error — confirmed against both oracles

`err.sno`: `&ERRLIMIT=2; a[1]=; OUTPUT=&ERRTYPE; OUTPUT=&ERRTEXT; OUTPUT=&ERRTYPE` on a completely fresh
`a` (never `ARRAY()`/`TABLE()`-declared). Expected (csnobol4 `.ref` and live-oracle-confirmed):
`3 / Erroneous array or table reference / 3` (the SAME value both times — reading `&ERRTEXT` does not
clear the error state, which is *also* proven by this same witness and worth preserving in whatever
witness carries the cure). SCRIP: `0 / (empty) / 0` — no error raised at all; the subscript-assignment
silently succeeds as a no-op.

**Isolated the `[...]` vs `<...>` question directly, since SCRIP's lexer treats `[`/`]` as ordinary
characters inside a quoted string** (initially suspected `[...]` might not be recognized as subscript
syntax at all — WRONG: `A=ARRAY(3); A[1]=99; OUTPUT=A[1]` **works correctly** in SCRIP, `[...]` IS valid
subscript syntax on an already-valid array, matching SPITBOL — `A[1]=99; OUTPUT=A[1]` on SPITBOL also
gives `99`). So this is not a bracket-parsing gap; the defect is specifically that subscripting an operand
that is **not a declared array/table** (regardless of which bracket syntax) is silently accepted rather
than raising an error, confirmed with a clean `<1>`-only minimal witness (no brackets at all) against BOTH
oracles: csnobol4 gives `3 / Erroneous array or table reference / 3` (matches `err.ref` exactly);
SPITBOL gives `235 / subscripted operand is not table or array / 235` — different code and text (the two
dialects never share error numbering) but the SAME underlying behavior: both real implementations treat
this as an error, SCRIP treats it as silently valid.

This is the same defect `FINDING-2026-09-03-seat08-...`'s §5 names in passing: `user_function_array_-
replace_branch_1` — "RED ON ARRIVAL per its own header, tracked under queue row `subscript-silent-accept`"
— which, like class #1, was never actually minted (no such row exists in QUEUE.tsv or postoffice/tasks/,
checked directly). This sitting's `err`/csnobol4_suite witness is independent, cross-oracle-confirmed
evidence for the same mechanism from a different corpus.

Minted: `snobol4-subscript-undeclared-operand-not-detected` (cross-referencing `subscript-silent-accept`'s
prior informal name and `user_function_array_replace_branch_1` as the sibling master-corpus witness).

## 5. Unknown-keyword assignment (`&Z = ...`) raises no error — confirmed against both oracles, NEW class

Surfaced inside `setexit4.sno`'s `&Z = 1` (`&Z` is not a defined SPITBOL/CSNOBOL4 keyword). Minimal
witness: `&ERRLIMIT=10; &Z=1; OUTPUT=&ERRTYPE ' ' &ERRTEXT`. SCRIP: `0 ` (no error). csnobol4 oracle:
`7 Unknown keyword`. SPITBOL oracle: `251 keyword operand is not name of defined keyword`. Same shape as
§4 — both real dialects raise an error (different code/text, same behavior class), SCRIP silently accepts
an assignment to an undefined keyword name instead.

Grepped `.github` for any existing characterization of this specific mechanism ("unknown keyword",
"not.*defined keyword") — the only near-hits are about specific VALID keywords once missing from a lookup
table (`FINDING-2026-08-27-hq_C-line-lastline-were-absent-from-the-keyword-table-not-broken.md`, a
different mechanism: keywords that should exist and didn't, not detection of keywords that shouldn't).
This looks genuinely new, not previously characterized anywhere found.

**Worth flagging together with §4 for whoever ranks/cures these**: SCRIP now has two independently-found
instances of the same shape — "an operation on an invalid operand that both real dialects reject as a
runtime `&ERRTYPE` error is instead silently accepted" (undeclared-array-subscript, unknown-keyword). That
might mean SCRIP has no general-purpose facility for raising a recoverable, catchable `&ERRTYPE`/`&ERRTEXT`
runtime error at all yet (each site needs one built), or that a handful of specific checks are each
individually missing — worth deciding which before scoping either cure, since it changes whether these are
one row's work or two's.

Minted: `snobol4-unknown-keyword-assignment-not-detected`.

## 6. `setexit2`'s `.ref` carries a fixture nuance, unrelated to the SETEXIT finding (§3)

`setexit2.sno` is flagged `REGEN-CANDIDATE` by the suite board (live csnobol4 disagrees with `.ref` too).
Traced: NOT a SCRIP-relevant disagreement. `&LASTFILE` reflects however the program was actually invoked
(confirmed: invoking the same file two different ways, live csnobol4 printed two different `&LASTFILE`
values). `.ref` was seemingly captured under an invocation convention (bare relative filename) that
doesn't match the harness's own scratch-copy-with-absolute-path convention, so `&LASTFILE`'s value can
never byte-match `.ref` today regardless of which engine is asked — a harness/fixture path-dependence, not
a defect in either engine. **Out of scope for this row on purpose**: at least 30 names carry the
REGEN-CANDIDATE flag for reasons not yet individually triaged; whether they share this exact cause is a
separate census, not attempted here (this row's brief was the 6 explicitly-named untraced classes, not the
REGEN-CANDIDATE bucket as a whole). Noted so nobody reads SETEXIT's cure as needing to also fix `&LASTFILE`
path-independence — it doesn't; the two are unrelated and the SETEXIT finding stands on its own
zero-output-at-all witnesses (§3), never on `setexit2.sno`'s specific byte-for-byte match.

## 7. `convert` — REAL defect, but it folds into an EXISTING cross-language row, not a new one

`convert.sno`: builds a `TABLE()`, inserts keys `'A' 'B' 'C' 'D'` in that order, `CONVERT(A,'ARRAY')`,
prints `B<I,1>: B<I,2>` for `I=1..4`. Expected (and both oracles agree, see below): `A:1 / B:2 / C:3 /
D:4` — insertion order. SCRIP: `A:1 / D:4 / B:2 / C:3` — hash-bucket order. Checked against both oracles
(the `.ref`-only read would have been sufficient here too, but §2 just showed why that's not safe to
assume in general): csnobol4 AND SPITBOL (`sbl -bf`) both print `A:1 / B:2 / C:3 / D:4` on the identical
minimal witness — unambiguously a real defect, not a dialect difference.

**Not minted as a new SNOBOL4-specific row.** An existing, already-scoped row —
`icon-arizona-class-table-iteration-order-not-insertion` (seat04, 2026-09-04) — already names this exact
shape for Icon (`key(table)`/`every` walk hash-bucket order instead of insertion order) and explicitly
scopes it to "the shared TBBLK_t/table iteration machinery used by every language that has tables (Icon,
Snocone)" — SNOBOL4 was simply not yet listed, even though `TABLE()`/`CONVERT` are core SNOBOL4 builtins
over the same IR-level table type. Added this sitting's both-oracle-confirmed SNOBOL4 evidence to that
row's LEDGER rather than mint a duplicate — CONVERT is presumably the SNOBOL4-side caller of the same
iteration path Icon's `every`/`key()` uses, though that is not independently confirmed at the source level
this sitting (census/witness role, not root-cause tracing). Worth noting the OTHER similarly-named row,
`icon-key-table-iteration-order-differs-from-arizona-oracle`, hedges that Icon's `key()` order is
UNSPECIFIED by the language and this may not even be a bug for Icon specifically (only a byte-identity gap
against one demo) — that hedge does not extend to SNOBOL4: `CONVERT`'s insertion-order behavior is
confirmed by two INDEPENDENT real SNOBOL4 implementations agreeing with each other, so for SNOBOL4 this is
unambiguously the specified behavior, not a matter of convention. That distinction is worth whoever
reconciles the two Icon-named rows keeping in mind, but reconciling them is out of scope here.

## 8. `genc` — ADDENDUM (same sitting, second pass): NOT "needs external resources", needs a real
   multi-file invocation the generic harness cannot give it, AND surfaced a genuine SCRIP defect

Every prior session on this row (three, going back to the 2026-08-27 triage) deferred `genc.sno` as
"needs `global.procs` and other external resources, not a quick trace" and moved on. That framing turned
out to be imprecise in a way worth correcting for whoever next has to decide whether it's worth chasing:
the resources are NOT actually missing, and going one level deeper surfaced a real, cleanly-isolated SCRIP
defect independent of genc itself.

**genc.sno is a real, faithfully-vendored Budne test with a genuinely different SHAPE from the other 117
members**, confirmed against `/home/resources/csnobol4` (a proper snobol4ever-lineaged clone of Phil
Budne's own upstream, already present on this box — not fetched or vendored new this sitting):
- Its real invocation, per Budne's own `test/test.genc.sh`: `$SNOBOL genc.sno v311.sil`, comparing FOUR
  output files, not one — stdout vs `genc.ref` (the only one this suite vendors), PLUS three side-effect
  files genc.sno writes itself: `proc.h2`/`callgraph`/`static.h2` vs `proc.h.ref`/`callgraph.ref`/
  `static.h.ref` (present at `/home/resources/csnobol4/test/`, none vendored into
  `corpus/packages/snobol4/csnobol4_suite/`).
- Its error message "`FATAL: could not open global.procs`" is NOT naming a real file — genc.sno's own
  source (lines 597, 615) opens two SEPARATE files, `"globals"` and `"procs"` (944 and 1607 bytes,
  present at `/home/resources/csnobol4/{globals,procs}`), and the message is just descriptive prose. A
  concatenated `global.procs` (my first, wrong guess) does not satisfy it; the two separate files do.
- `v311.sil` (Budne's own SIL bootstrap source, the actual input genc.sno compiles) is at
  `/home/resources/csnobol4/test/v311.sil`, also not vendored into the corpus suite.

None of `v311.sil`/`globals`/`procs`/the three extra `.ref` files are exotic or hard to obtain — they are
sitting on this exact box, in a repo CLAUDE.md already documents. The real reason genc has never been
graded is that `test_snobol4_csnobol4_suite.sh`'s generic per-`.sno`-file loop (one stdin, one stdout
capture, one `.ref` diff) cannot express "one extra CLI arg plus three side-output-file comparisons" for
a single suite member without a special case — the same reason Budne's OWN suite gives genc a dedicated
driver script instead of folding it into the generic one. That is a harness-SHAPE gap, not a missing-file
gap, and fixing it (vendor the four extra fixtures, special-case genc's invocation the way `DUMP_TESTS`/
`TRACE_TESTS`/`STDIN_TESTS` already special-case by name in the same file) is a real but separate,
larger undertaking than this row's own census scope — noted here, not attempted.

**Supplying the correct arguments by hand surfaced something more valuable than genc itself**: with
`globals`/`procs`/`v311.sil` all present and `v311.sil` passed as `-- v311.sil`, genc.sno still produced
only `FATAL: EOF on  before END op` — and its own `SILPATH` variable (read from `HOST(2,N)`) printed
EMPTY throughout, meaning the `--` argument was not reaching the program at all. Isolated with a two-line
witness with no `DEFINE`, no function, nothing genc-specific: `OUTPUT=HOST(3); OUTPUT=HOST(2,1)` invoked
as `./scrip --run w.sno -- v311.sil` prints `argc=0` / `arg1=` (empty) instead of `argc=1` /
`arg1=v311.sil`. Read `src/driver/scrip.c` directly rather than guess further: `g_prog_argv`/
`g_prog_argc` ARE correctly captured from `--` (~line 952), but the call that stages them for `HOST()` to
read, `rt_main_args_stage(g_prog_argv, g_prog_argc)`, is gated behind `nparams >= 1` on the entry graph at
BOTH its call sites (~1751, ~1850) — a condition about whether the SNOBOL4 source happens to define its
top level as a parameterized function, which has nothing to do with whether `--` arguments were passed at
all. A plain top-level program (genc.sno's own shape, and most programs') can never see its own argv.

Minted `snobol4-host-argv-not-staged-for-zero-param-entry` (rank 2, owner hq_P) for this — checked it is
not already covered by the two closest-sounding existing rows (`icon-suite-format-has-no-argv-sidecar-...`,
`suite-harness-argv-echoes-a-mktemp-path-...`), both different mechanisms (suite/grading-format concerns,
not whether `HOST()` itself observes passed args). Fixing it is very likely necessary, but NOT
independently confirmed sufficient, to get genc.sno reading its real input at all — the harness-shape gap
above still blocks a byte-match against `genc.ref` regardless.

`genc` is therefore best read as: BLOCKED on a real, now-precisely-diagnosed SCRIP defect (minted, hq_P's
to cure) plus a separate, larger harness-shape gap (documented, not minted as its own row — see the
parent task's own ledger) — not "untraced," and not a quick win either. That is a more useful state to
leave it in than either label alone.

## Control arm

`bash scripts/test_snobol4_csnobol4_suite.sh` before this sitting's tracing began: `total=118 m3
PASS=55 FAIL=23 REJECT=39 CRASH=1` — exact match to seat09's last-recorded state (SCRIP `83208099`), so
nothing drifted between sessions. No `src/` files touched this sitting (role is census/classify/witness
only, per this row's own brief; class cure is hq_P's). Re-ran after minting to confirm the board is
unchanged (minting a class row does not itself change suite output): same `total=118 m3 PASS=55 FAIL=23
REJECT=39 CRASH=1` on SCRIP `fc4d4326c`. The genc.sno/HOST() investigation (§8) used scratch witnesses
outside the suite tree throughout and touched no suite fixtures or `src/` files either.
