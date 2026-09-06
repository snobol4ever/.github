# FINDING — two owed synthetic witnesses built (`toktab`, `lisp`), and `lisp`'s root cause traced past the
# Lisp-interpreter framing to a general defect: SCRIP's `bal()` generator yields exactly one result instead
# of backtracking through successive longer balanced-substring endpoints. New class minted, not cured.

**seat07 · 2026-09-06 · row `icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class`** (own row's
STILL-OWED item (b): "Synthetic `util_icn_class_witness.sh` entries for toktab/lisp/op122").

## Housekeeping note before the findings: a stale-binary near miss, self-caught

Session start pulled fresh `origin/main` into all three repos but the existing `./scrip` binary was ~2.5
hours stale relative to the new HEAD. Early probing against that stale binary produced a run of alarming,
seemingly show-stopping parse errors on the most basic multi-statement Icon (`local x; x := 5; write(x)`
shape, written without semicolons). Traced to two independent non-findings before any of it was reported:
(1) the binary was stale — `make` (incremental) rebuilt clean; (2) even post-rebuild, terse semicolon-free
Icon still parse-errored, which is **documented, intentional, gated behavior** (this CLAUDE.md's own "SCRIP
Icon is semicolon-required — zero newline processing, no icont-style Beginner/Ender insertion", gate
`test_gate_icn_semicolon_required.sh`), not a regression. Writing this up only so the near-miss shape is on
record, matching this lane's own convention of naming self-caught mistakes rather than discarding them
quietly. No src/ change, no class filed for either — both are already correctly documented/gated.

## Witness 1: `icon-ipl-toktab-default-options-invalid-sort-order` — CONFIRMED, witness added

`showtbl.icn`'s `sort_order := case sort_order of { "incr" | &null: "incr"; "decr": "decr"; default: stop(...) }`
must match the `&null` alternative when `sort_order` is an omitted (hence `&null`-defaulted) parameter.
Minimal witness (14 lines, `scripts/util_icn_class_witness.sh`, proven against the real icont oracle):

```
procedure main()
   local r;
   r := f();
   write(r);
end
procedure f(x)
   local s;
   s := case x of {
      "incr" | &null: "matched-null-or-incr";
      "decr": "matched-decr";
      default: "NO-MATCH"
   };
   return s;
end
```

oracle: `matched-null-or-incr` — SCRIP m3 and m4 both: `NO-MATCH` (rc=0 both sides — grade by value, this is
not a crash). Isolation notes for whoever cures it:
  - `case &null of {...}` used **directly** (no omitted-parameter indirection) matches correctly on SCRIP —
    the defect needs the control value to arrive via an omitted argument, not a literal `&null`.
  - `return case x of {...}` used **directly** as the return expression (rather than assigned to a local
    first, then returned) produces a *different* wrong answer: total silent failure (empty output, both
    modes) rather than the `default` arm's value — the case expression appears not to match ANY arm,
    including `default`, in that shape. Flagging both shapes rather than picking one, since they may be the
    same underlying defect manifesting through two lowering paths, or two defects; not bisected further
    (src/-level, hq_I's call per this row's own division of labor).
  - `s4e_msg.sh` DONE-WHEN for this row is unaffected by this finding — it was already the correct interim
    proof-of-life; this is the promised, previously-missing synthetic witness only.

## Witness 2 / new class: `icon-bal-generator-yields-one-result-not-a-backtracking-sequence` — MINTED

`lisp.icn`'s `(CAR (QUOTE (A B C)))` evaluates wrong. Traced the ~300-line Lisp-in-Icon interpreter's own
EVAL/apply/CAR/QUOTE logic by hand first (procedure by procedure) — it is correct, assuming its tokenizer
(`bstol`/`balstr`/`checkbal`, all built on `s ? tab(bal())`-style balanced-substring scanning) hands it a
correctly-parsed list. It does not. Isolated with a sequence of ablations, from the full `checkbal`-shaped
expression down to this 4-line witness:

```
procedure main()
   local s;
   s := "(AB) ";
   s ? every write(image(tab(bal())));
end
```

oracle (`every` over the `tab(bal())` generator, resuming on backtrack):
```
""
"(AB)"
```
(bal() first yields the shortest — empty — balance point, then on resumption yields the full `(AB)`.)

SCRIP m3 and m4, both: only
```
""
```
— `bal()` never produces the second, longer alternative; the generator is exhausted after one result. This
is the mechanism `checkbal`/`balstr` depend on (`tab(bal()) & pos(-1)`, or the equivalent
`1(tab(bal()), pos(-1))` integer-invocation form lisp.icn itself uses): both require `bal()` to backtrack
through progressively longer matches until a downstream conjunct is satisfied. With only one match ever
offered, any such conjunction that isn't satisfied by the *shortest* balance point fails outright — which is
exactly `lisp.icn`'s symptom (the `> (NIL)` / `ill-formed expression` shape reported in that row's own GOAL
is `balstr`'s own failure branch firing because `checkbal` never finds its balance point).

**Distinct from the existing `icon-bal-missing-cset-type-check` class**
(`FINDING-2026-09-04-seat01-icon-bal-missing-cset-type-check.md`): that one is bal() not validating its
argument *type* (a `list` where a `cset` is required). This one is bal() with entirely valid default
arguments not behaving as a generator at all past its first result. Checked before minting — no existing
row covers this; confirmed via `s4e_msg.sh mint icon-bal-generator-yields-one-result-not-a-backtracking-
sequence 1 --owner hq_I`.

**Why this might be higher-leverage than either the `toktab` or `lisp` rows individually name**: `bal()`'s
generator behavior is core Icon scanning machinery, not IPL- or lisp.icn-specific. Any other program (in
`ipl/`, `arizona/`, or corpus generally) that scans balanced expressions via backtracking over `bal()` is a
candidate to be silently affected the same way — this was not surveyed this session (out of scope: census,
not cure), but is worth hq_I/hq_B checking the existing FAIL census for other victims before assuming this
class's blast radius is just `lisp.icn`.

## Not done this session (real, substantial, unchanged)

Per this row's own STILL-OWED list: `op122` witness (needs a gdb backtrace at the FATAL site — not
attempted, and it is rank 6 per THE FLEET-12 PLAN's rank re-cut, HQ-only territory regardless); the
fixture-file harness extension for filecnvt/gediff/huffstuf/iiencode; `press.icn` (896 lines, never
investigated); the file-output-not-stdout design gap (versum/iidecode/iplweb). None of this session's two
witnesses are cured — both rows' own DONE-WHENs stay red on that basis alone.

## Repo state

SCRIP: `scripts/util_icn_class_witness.sh` gained two entries (toktab, the new bal class) — this file only,
no other src/ change. `.github`: this FINDING, the new task file via `mint`, SEE ALSO the enrichment notes
left in `icon-ipl-toktab-default-options-invalid-sort-order.task.md` and
`icon-ipl-lisp-icn-car-quote-wrong-result.task.md`'s own `## NEXT` blocks. No corpus change.
