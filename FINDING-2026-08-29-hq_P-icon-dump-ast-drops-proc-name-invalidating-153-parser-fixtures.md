# FINDING: `--dump-ast` drops the procedure NAME from `TT_PROC_DECL`, invalidating all 153 Icon parser fixtures at once

**Seat:** hq_P (TRIO) · **Date:** 2026-08-29 · **Found while:** building the Icon master (`tests-consolidate-icon`
lane, ceo consolidation priority 1) · **Status:** ⛔ NOT CURED — measured, isolated to one token, routed.

## THE DEFECT
`scrip --dump-ast` on any Icon procedure emits `TT_PROC_DECL` **without the procedure's name**:

```
committed .ref :  (STMT :subj (TT_PROC_DECL main
today          :  (STMT :subj (TT_PROC_DECL
```

Everything else in the dump is byte-identical — the `TT_VAR main`, the `TT_VLIST`, the whole `TT_PROGRAM`
subtree. One token, on the first line, in **every** fixture.

## SCALE — ONE REGRESSION, 153 FILES
`corpus/tests/icon/parser/` holds 153 fixture pairs and every `.ref` carries that token, so a single dropped
name makes the entire parser corpus red. Graded through the new Icon master: **`ast_pass=0` of 415**.

⭐ **THE 0/415 IS WHY THIS IS WRITTEN UP AS A COMPILER DEFECT AND NOT A MASTER DEFECT.** A census finding 100%
of its population guilty is normally the instrument indicting itself (hq_B's tell, `RULES.md` § INSTRUMENT LAWS
SIXTH BATCH clause 3) — so the master was **not** trusted. The check that settled it was to grade the ORIGINAL
pair, which still exists precisely because byte-equal-or-no-delete kept it:
`scrip --dump-ast corpus/tests/icon/parser/alt_arith.icn` vs its own committed `alt_arith.ref` → **already
differs**, with no master involved anywhere. The master reproduces a red that was there before it existed.
⛔ Three separate 100%-failure readings were investigated before this one was believed; the first two were my
own invocation errors (grading a dialect master without `--lang`, and grading rung families in `ast`). **A
self-indicting census is a reason to check the instrument, not a licence to disbelieve every red forever** —
the discipline is to keep checking until the instrument is exonerated by an independent path, which the
original-pair diff is.

## WHAT IT IS NOT
- **Not the master's absorption.** Verified independently of the master, above.
- **Not the m3/m4 half.** The Icon rung families grade `m3 pass=274 · m4 pass=274` on the same master and same
  build; only the ast-graded parser half is red.
- **Not a `.ref` staleness question that can be settled by regenerating.** ⛔ Regenerating the refs from today's
  compiler would turn 153 red fixtures green **by writing the defect into the oracle** — the refs are the record
  of what the AST is supposed to look like. Whether `TT_PROC_DECL` should carry the name is a question for
  whoever owns the Icon AST shape; until that is ruled, the refs stand and the fixtures stay red.

## WHY IT WAS INVISIBLE UNTIL A MASTER EXISTED
The only runner found over `tests/icon/parser/` is `SCRIP/scripts/test_corpus_icon_parser.sh`, and it does not
diff against the `.ref` at all: it pipes each `.icn` through the `icon_parser`/`icon_recognizer` binaries and
scores PASS purely for **non-empty** output (`[ -z "$OUT" ] || [ "$OUT" = '(compiland "")' ]` → EMPTY, else
PASS, lines 43-58). ⭐ **That is this project's own "non-empty is not alive" class:** it proves the parser
emitted something, never that it emitted the right thing. 153 graded reference files sat beside a runner that
could not have detected any change to their content. The master's `ast` mode is the first instrument that
actually compares them — which is the concrete answer to "what is a master FOR": it did not find a new bug so
much as make an old one **countable**.

## NEXT ACTOR
1. Rule on the AST shape: should `TT_PROC_DECL` carry the procedure name? The refs say yes and were generated
   when it did. If yes, this is a straightforward emitter regression; bisect `--dump-ast`'s `TT_PROC_DECL` site.
2. Do **not** regenerate the refs to clear the red before (1) is ruled.
3. `test_corpus_icon_parser.sh` needs the same treatment as the SKIP→FAIL board issue in the sibling FINDING:
   a runner that cannot fail is not evidence. Both are the vacuous-test class Lon flagged.
