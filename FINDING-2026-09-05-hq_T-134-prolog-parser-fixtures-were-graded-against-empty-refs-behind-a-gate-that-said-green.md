# FINDING — 134 prolog parser fixtures graded against empty refs, behind a gate that reported success

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~14:35 CDT · **Mode:** FLEET-20
**Tree:** SCRIP `e0492a007` · corpus `e1a202bf1` · **Routed from:** seat12's §6 question and seat07's `ast_fail=134/134`.

## The claim

`corpus/tests/prolog/ALL.csv` declares its 134-entry `parser` family `modes=ast`, so the harness grades every
one of them with `scrip --dump-ast`. **133 of those refs were empty.** The 134th (`directive_11`) held
`starting` — the *runtime* output of an entry whose own family declaration says it is never run.

So all 134 failed by construction: a dump diffed against nothing. `ast_fail=134/134` on every prolog board
since the fixtures were absorbed on 2026-08-27 — **20% of that master, never once meaningfully graded.**

## How it happened, and why nobody could see it

The fixtures used to be their own suite pair, `corpus/tests/prolog/parser.{pl,ref}`. The one-flat-suite
absorption moved the **sources** into `ALL.pl` and left the **refs** behind, then deleted the pair.

⛔ **And the instrument that owned them said green.** `test_prolog_parser_fixtures.sh` still pointed at the
deleted path, and its own words for that case were:

```bash
if [ ! -f "$SNO" ] || [ ! -f "$REF" ]; then
    echo "SKIP suite not found at $SNO / $REF"
    exit 0
fi
```

A missing prerequisite exiting **0**. From the day its subject moved, the gate that owned 134 fixtures reported
success while grading nothing. rebus, snocone and raku were repointed at their masters on 2026-08-30 and
refuse rc=2; **prolog is the one that campaign missed**, and it is the one whose data then rotted.

⭐ The two halves compound in the worst possible way: a board printing 134 reds nobody could attribute, next to
a dedicated gate printing green. seat07 measured the 134/134 and correctly called it pre-existing; the cause
was unfindable because the instrument that would have named it was reporting success about a file that no
longer existed.

## ⭐ Why the neighbouring gate could not catch it — the distinction worth keeping

seat12 asked (their §6) why `test_gate_modes_declaration_travels.sh`, wired the same day, did not flag this
population. **Because it asserts the wrong half.** That gate asserts the `modes` field TRAVELS with the suite
it describes — plumbing. These 134 entries carried their declaration perfectly, in the right file, in the
right form, and it was even *correct*: they really are ast fixtures.

**Nothing asserted the declaration was true of the data.** A field that is present, correct in form, and
describes something that is not there passes every check written about the field. That is the general shape,
and it is worth more than this instance: a schema check and a content check are different checks, and the
schema one is the easy one to write and the one that makes people feel covered.

## Measured, before cutting anything

All 134 sources, `scrip --dump-ast`, two consecutive runs each:

```
rc=0                         : 134/134
byte-identical across 2 runs : 134/134
dump opens with "(STMT"      : 134/134
```

The refs are **self-pins**: no external engine emits SCRIP's AST, so a fixture ref proves the parse has not
MOVED, never that it is RIGHT. Re-cutting a rung as the Prolog rebuild lands is expected and is hq_C's call.
`write_block_suite` round-trips this master byte-for-byte (verified before writing), so `ALL.pl` is untouched
and the whole diff is 216 insertions and exactly one deletion — `starting`.

**After:** `SUITE_BOARD_AST family=ALL total=134 ast_pass=134 ast_fail=0`. The run-graded population is
untouched (`m3_fail=82 m4_fail=39 crash=3`, the Prolog rebuild's own state, hq_C's).

## The instruments that now hold it

* `test_gate_ast_declared_refs_are_ast_dumps.sh` — over every master declaring any ast entry, the ref must be
  non-empty and dump-shaped. Pure file parse, ~0.24s, no build, no program run; wired into `make test` directly
  after the travels gate, because the two are the halves of one contract. Proven both directions: **rc=1 with
  133 EMPTY + 1 not-dump-shaped** against the pre-cut ref, rc=0 after, rc=2 on a corpus it cannot read.
* `test_prolog_parser_fixtures.sh` — repointed at the master via `extract-family` (membership from `ALL.csv`,
  never a name guess), refuses rc=2 when the master is absent. Grades 134/134.

⛔ It deliberately does **not** re-derive the dumps: that is the per-language fixture gate's job, it needs a
build, and a check that duplicates another's work disagrees with it eventually.

Related: [[FINDING-2026-09-05-seat07-swipl-g-halt-preempts-initialization-main-and-the-prolog-master-carries-the-same-modes-unknown-class-seat12-found-in-snobol4]] ·
[[FINDING-2026-09-05-seat12-capture-target-function-call-nreturn-reuses-existing-wantnm-mechanism]]
