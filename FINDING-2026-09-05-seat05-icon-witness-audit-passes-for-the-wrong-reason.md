# FINDING 2026-09-05 — seat05 — Icon isolation-ladder witness audit: PASSES-FOR-THE-WRONG-REASON census

Context: FLEET-12, seat05, hq_B lane. Brief: hq_B mail `next-is-the-isolation-audit-hunt-witnesses-that-
pass-for-the-wrong-reason`, task `icon-witness-audit-passes-for-the-wrong-reason`. Population: all 270
Icon ladder witnesses (`corpus/tests/icon/ALL.csv` origin `ladder__rung*`, rungs 0-42), matching
`util_ladder_forms_check.py`'s own **269/269 declared forms witnessed** (270 physical witnesses map to
269 declared FORMS — one form carries two witnesses; both denominators are real, neither is an error).
Method: extracted every witness's source + `.ref` + `.wantrc` out of the marker-delimited masters by
`origin` (never by filename), read all 270 by hand, then verified every non-obvious call empirically
against the built `scrip` binary and the real oracle (`/home/resources/icon-master/bin/{icont,iconx}`)
before writing anything down. Tree at measurement: SCRIP `75e5b6f5f`, corpus `590684477` (base, dirty
with this session's own strengthenings below).

## The defect class, precisely stated

A witness PASSES FOR THE WRONG REASON when its `.ref` (stdout) would be **byte-identical** under two
different underlying realities: "the feature is implemented and this specific check is correct" vs. "the
feature does not exist / does nothing observable at this point." The harness grades stdout + rc only;
Icon's own runtime-error detail (the specific error number/text) is stderr-only, so any witness whose
PASS condition reduces to "the program stopped producing output around here" cannot tell the two apart.

## CLASS A — REFUSAL INDISTINGUISHABLE FROM UNIMPLEMENTED (the seed class, `loadfunc_refusal`)

Shape: witness declares a nonzero `wantrc` (a deliberate refusal), and every line of its `.ref` is
printed **before** the call under test. Population: every witness with a nonzero `ALL.wantrc` entry (18
total; `wantrc` defaults to 0 and is only ever listed as an override, so this file IS the complete
candidate list — no scan of it can under-count).

**Ablation, minimal, three-way (proves the mechanism, not just asserts it):**
```
p1 (loadfunc, /no/such/lib.so)      -> stdout "calling",  stderr "ERROR 022 -- Undefined function called", rc=1
p3 (getch(), independently unimplemented per rung41's own finding) -> stdout "before", SAME error 022, rc=1
p4 (thisFunctionDefinitelyDoesNotExistAnywhere123())                -> stdout "before", SAME error 022, rc=1
p2 (any([1,2]), a REAL wrong-type refusal)  -> stdout "before", stderr "Run-time error 104 cset expected", rc=1
```
Three completely unrelated "the symbol doesn't exist at all" cases (p1/p3/p4) and one genuine "the
feature correctly detected misuse" case (p2) all produce **rc=1** and a stdout that is nothing but the
witness's own pre-call print. The distinguishing detail lives only on stderr, which nothing here grades.

**Disposition of all 18 (excludes nothing — every nonzero-`wantrc` entry is accounted for):**

| # | witness | real oracle code | disposition |
|---|---|---|---|
| 1 | `ladder_rung01_paper_by_zero` | 211 by-value-zero | **NOT strengthened — see companion FINDING, cheap fix currently hangs SCRIP** |
| 2-4 | `ladder_rung06_cset_scan_refuse_{any,many,upto}` | 104 cset expected | **STRENGTHENED, verified PASS both modes** |
| 5-8 | `ladder_rung08_strbuiltins_scan_refuse_{find,match,move,tab}` | 103/103/101/101 | **STRENGTHENED, verified PASS both modes** |
| 9-10 | `ladder_rung14_limit_limit_refuse_{neg,type}` | 205/101 | **STRENGTHENED, verified PASS both modes** |
| 11-12 | `ladder_rung26_pow_pow_{negbase_real,zero_negexp}` | 206/204 | **NOT touched — hq_B's live cure target.** ⚠ FORWARD RISK: these are currently RED for the real, already-filed reason (silently compute a wrong value instead of erroring); the instant hq_B's cure lands, THIS SAME witness shape (`ref="before"` only) will pass **vacuously** — indistinguishable from "still broken but now happens to abort at the right spot." Recommend hq_B apply the identical strengthening recipe below as part of landing the cure, not after. |
| 13 | `ladder_rung36_sets_refusal` | 122 set-or-table expected | **STRENGTHENED, verified PASS both modes** |
| 14-15 | `ladder_rung37_bal_{refusal,scan_refuse}` | 104 cset expected | **STRENGTHENED, verified PASS both modes** |
| 16 | `ladder_rung41_rt_loadfunc_refusal` | **216** external-function-not-found | **STRENGTHENED — now correctly RED.** SCRIP currently reports code 22 (genuinely unimplemented, per rung41's own standing FINDING); the strengthened `.ref` is oracle-cut (216), so this witness now tells the truth instead of passing by coincidence. This is the fix working as designed, not a regression — the underlying defect was already known and filed; it was simply invisible to this specific witness before. |
| 17 | `ladder_rung41_rt_runerr` | 205 invalid value | **NOT strengthened — see companion FINDING, `&error` does not catch `runerr()` in SCRIP** |
| 18 | `ladder_rung41_rt_system_exit_stop` | n/a (wantrc=42) | **NOT a class member — see "positive pattern" below.** |

**The cure, generalized and oracle-verified as a recipe:** wrap the call in `&error := 1; CALL;
write("num=", &errornumber, " text=", &errortext);` and cut the `.ref` from **icont/iconx, never SCRIP**
(confirmed empirically: `&error`-trapping a real refusal in SCRIP reproduces the oracle's exact
number+text, e.g. `any([1,2])` → `num=104 text=cset expected` on both SCRIP and iconx). This turns an
absence-based pass into a value-based one: an unimplemented callee reports 22 every time, a real refusal
reports its own specific code, and the two can no longer collide. 12 of the 15 currently-passing members
were strengthened this way this session (corpus `ALL.icn`/`ALL.ref`/`ALL.wantrc`, all committed with this
FINDING); ladder board before → after: `510/540` → `508/540` (**intentional**: 2 fewer PASS, 2 more FAIL,
both from `loadfunc_refusal`'s single now-correct exposure across m3+m4 — every other touched witness
stayed green, now for a provable reason instead of a coincidental one).

## CLASS B — UNTESTED COMPLEMENT (one branch of a two-way construct exercised, the other never is)

Unlike Class A, these witnesses are not wrong — the compiler is correct and the tests pass for the
*right* reason today. The gap is that the SIBLING behavior (the branch that should be suppressed) has no
witness anywhere in the ladder, so a hypothetical regression to "this construct always succeeds" (or
"always fails") would pass every existing witness undetected.

**Instance 1 — `not()`, rung07.** Both existing witnesses (`procedure_write_152`, `procedure_write_153`)
test only `not(a FAILING condition) -> succeeds -> prints`. Neither tests `not(a SUCCEEDING condition) ->
should FAIL -> should NOT print`. A `not()` that always succeeds regardless of its operand would pass
both existing witnesses. Verified empirically that SCRIP does **not** have this bug (`p5_not_gap.icn`:
`if not(1<2) then write("BUG...") else write("done1"); if not(2<1) then write("done2") else
write("BUG...")` → SCRIP prints `done1\ndone2` rc=0, **byte-identical to icont/iconx**) — this is a real,
currently-unexploited coverage hole, not a live defect.

**Instance 2 — `/` (null-value test), rung34.** LADDER.tsv declares five forms including `null_succeeds`,
but neither existing witness that touches `/` constructs a genuine null value: `procedure_write_199`
tests `/` on a non-null value (correctly fails), `procedure_write_200` tests `/` on an **already-failing**
expression (never actually exercises the null-vs-non-null branch at all, since `1 > 2` produces no value
for `/` to examine). The "succeeds when its operand really is `&null`" half of `/`'s contract — the
declared `null_succeeds` form — has no witness that can prove it, despite BUILT/green status. Verified:
`p6_slash_gap.icn` (`local x; write(if /x then "isnull-ok" else "BUG..."); x:=5; write(if /x then "BUG..."
else "notnull-ok")`, x starts genuinely null via an uninitialized local) → SCRIP prints
`isnull-ok\nnotnull-ok` rc=0, **byte-identical to icont/iconx**. Again: not a live defect, a coverage hole.

**Disposition:** NOT applied to the corpus this session — deliberately. Adding a brand-new `ALL.csv` row
(vs. editing an existing one, which is all Class A required) touches the ~70-column feature-flag schema
that three separate prior sessions on this exact task file flagged as having no documented, sanctioned
minting process (see this task's own `## SUPERSEDED-NEXT` history). Rather than guess at a schema I can't
verify, the two witness bodies above are already written, already oracle-cut, and already proven
byte-identical against both SCRIP and the real oracle — whoever next mints against LADDER.tsv's FORMS
column (this row's own sibling audit, or hq_T's forms tooling) can drop them in directly.

## CLASS C — UNCHECKED SIDE-EFFECT MARKER (minor, lower confidence)

`ladder_rung42_kw_dump`: `write(type(&dump)); &dump := 0; write("after-set")`. The `"after-set"` marker
proves the assignment didn't crash, not that it took effect — a silently-ignored `&dump` assignment would
print the same thing. Did not chase this further (the underlying tracing side-effect isn't independently
observable via stdout anyway, similar to `delay()`'s timing — see below), flagging at lower confidence
rather than omitting it.

**Also noted, not a defect:** `ladder_rung41_rt_delay` (`delay(1); write("after-delay")`) distinguishes
"delay exists as a callable" from "delay doesn't exist" (a crash would suppress the print) but not
"delay actually waited ~1ms" from "delay is a callable no-op" — timing isn't stdout-observable, so this
is likely the ceiling of what this construct can assert without a wall-clock harness, not a cheap fix.

## POSITIVE PATTERNS — the cure shape, named as hq_B asked

1. **A specific, arbitrary expected value beats a generic one**, even for a "does this fail correctly"
   test: `ladder_rung41_rt_system_exit_stop` expects **rc=42** (not the generic rc=1 every other refusal
   in this population uses) from `exit(42)`. An unimplemented `exit()` would not coincidentally produce
   42, so this witness — despite being shaped exactly like the vacuous Class A members on the surface —
   is NOT one. This is the single cheapest possible cure whenever the real API accepts an
   attacker-chosen/arbitrary discriminating value.
2. **Relational-operator right-operand echo, for genuinely non-deterministic/implementation-identity
   values.** `ladder_rung42_kw_collections_storage_regions_allocated` and siblings print
   `(&collections >= 0)`, which — because Icon relational operators return their RIGHT operand on success
   — prints a fixed `0` regardless of the real (legitimately implementation-specific) count, while still
   failing loudly if the keyword doesn't exist, isn't an integer, or is negative. hq_B named this pattern
   directly (date/clock/host/version family); it generalizes to any keyword whose *existence and type*
   are portable but whose *exact value* is not.
3. **`image()` around a possibly-empty result**, so "prints nothing" (ambiguous — crash? empty string?
   silently skipped?) becomes `""` (unambiguous). `ladder_rung40_strfn_repl`'s `image(repl("x", 0))` is
   the existing example; worth citing as the general answer to "how do I assert an empty string cheaply."

## Corpus changes this session

`corpus/tests/icon/ALL.icn`, `ALL.ref`: 13 witness bodies replaced in place (marker-anchored, by
`origin`, never by line position) — 12 per the strengthening recipe above, plus `loadfunc_refusal`.
`ALL.wantrc`: 13 now-unneeded nonzero-rc overrides removed (new expected rc is 0, the default; grading
moved from rc-only to value comparison). No `ALL.csv` row added, removed, or renumbered; `n_lines` is
unchanged for all 13 (both old and new bodies are 5 lines). Forms-check unaffected (`269/269`, unchanged
— no form gained or lost a witness, existing ones were only made stricter). Full ladder `--to 42`:
`510/540` → `508/540`, entirely explained by `loadfunc_refusal`'s intentional exposure (see table above).

## What this audit did NOT do, named precisely

Did not re-litigate any of the 6 already-filed rung38/39/41/42 defects (hq_B's own instruction: don't
re-file rung42's `error_keywords` red, and by the same logic the other five stay hq_B's as filed). Did
not touch rung26 (hq_B's live cure). Did not mint the two Class-B witnesses into the corpus (schema risk,
see above — content is ready). Did not exhaustively re-derive every one of the ~250 non-refusal witnesses'
Icon semantics from the language spec — applied the "would a trivial always-succeed/always-fail/no-op
stub also produce this exact `.ref`" test to all of them, which is what actually caught both Class A and
Class B; a witness that survives that test is not guaranteed correct, only not vacuous.
