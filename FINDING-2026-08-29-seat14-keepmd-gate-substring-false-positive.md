# FINDING — `test_gate_suite_conversion_complete.sh`'s KEEP.md check is a raw substring match against concatenated KEEP.md text, not a per-entry list; a file can get silently "declared" by basename collision or by being named in another entry's prose

**seat14 · 2026-08-29 · row `tests-consolidate-prolog`**

## The bug

`test_gate_suite_conversion_complete.sh` (lines 61-68):

```bash
mapfile -t KEEPFILES < <(find "$TREE" -type f -name 'KEEP.md' 2>/dev/null)
DECLARED=""
[ "${#KEEPFILES[@]}" -gt 0 ] && DECLARED=$(cat "${KEEPFILES[@]}" 2>/dev/null)
UND=0; UNDLIST=""
for f in "${LOOSE[@]}"; do
    b=$(basename "$f")
    case "$DECLARED" in *"$b"*) : ;; *) UND=$((UND+1)); UNDLIST="$UNDLIST\n     $b";; esac
done
```

Every `KEEP.md` anywhere under the tree is concatenated into one string, and a loose file counts as
"declared" iff its **basename** appears **anywhere** in that concatenated text — no structure, no
scoping to the KEEP.md the file actually lives beside, no distinction between "this file is a
deliberate keeper" and "this filename was typed for any other reason."

**Measured, not hypothetical:** this session added `tests/prolog/KEEP.md` ruling on exactly one file
(`plunit.pl`). The gate's `loose-but-undeclared` count dropped from **89 to 86** — three, not one.
Two false positives, two different mechanisms:

1. **Basename collision, unavoidable by wording.** `tests/prolog/frontend/plunit.pl` happens to share
   its exact basename with `tests/prolog/plunit.pl`, the file actually being declared. Any KEEP.md
   ruling on the latter necessarily contains the substring `plunit.pl` and therefore also "declares"
   the former — there is no way to write a KEEP.md entry for one same-named file without the check
   silently sweeping in every other file anywhere in the tree that shares its basename.
2. **Incidental mention in contrasting prose, avoidable but easy to trip.** The new KEEP.md entry
   explains that `plunit.pl` should *not* be merged with `frontend/plunit_mock.pl` (a deliberate
   non-ruling — that file is explicitly still unsurveyed). Simply naming it for that comparison
   put the substring `plunit_mock.pl` into `DECLARED`, which silently marked it "declared" too.

Both look identical to the gate's output: a clean `GATE OK` line, or a lower `loose-but-undeclared`
count, with nothing distinguishing "actually ruled on" from "coincidentally substring-matched."

## Why this matters beyond this one file

Every language's suite-conversion row (this task's siblings for SNOBOL4/Icon/Snocone/etc., per
`corpus-suites-consolidation`) uses this same gate. Any tree where two files share a basename across
different subdirectories, or where a KEEP.md's own explanatory prose names a *different* loose file
(to contrast, exclude, or cross-reference it — a normal and useful thing to write), will silently
under-count `loose-but-undeclared` the same way. This is exactly the "non-empty is not alive"
false-signal class this project already has a name for: `GATE OK` here does not mean "every loose
file was individually judged," it means "every loose file's basename happens to appear somewhere in
the KEEP.md text," which is a weaker and silently-different claim.

## Disposition this session

Not fixed — this is harness correctness shared by every language's row, not a call for one
corpus-conversion session to make unilaterally. Flagged in `tests/prolog/KEEP.md` itself (the
concrete instance) so the next reader does not mistake `frontend/plunit.pl` /
`frontend/plunit_mock.pl` as investigated or exempted because of it. Mailed hq (no single obvious
owner the way runtime bugs have hq_C — this is scripts/ harness code, not compiler or corpus content).

## Not attempted

A real fix — e.g. requiring each KEEP.md entry to name its file(s) in a structured, delimited form
(a leading `## \`filename\`` heading, matched instead of a raw substring test) — was not attempted
here: it changes a gate every other language's conversion row depends on, and deserves review before
landing, not a fix bundled into an unrelated file's KEEP.md commit.
