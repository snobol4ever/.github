# FINDING — suite-harness grading mode is a property of the FAMILY'S `.ref`, never of the DIALECT

**hq_P · 2026-08-29 · SCRIP `9bc44f9f` · corpus `57cd91a8b` · RT_OPT `-O0` · row `corpus-suite-harness-langconfigs-sc-pl-missing`**

## The premise that was false

The row was minted on the reading that `LANG_CONFIGS` (`scripts/corpus_suite_harness.py:99-106`) giving
`prolog` and `snocone` `modes:"ast"` while `pascal`/`icon` get `"m3,m4"` meant **"no compile/run grading arm
exists for `.sc`/`.pl` suite entries"** — i.e. that harness development was owed before either conversion row
could move.

⛔ **Measured false as stated.** `--modes` is a CLI flag on BOTH `convert-blocks` (`:1252`) and `run`
(`:1260`), each documented verbatim *"default: `LANG_CONFIGS[lang]['modes']`"*, and `run_all_modes`
(`:514-521`) implements `m3`, `m4` and `ast` independently for every dialect. The LANG_CONFIGS value is a
**DEFAULT, not a ceiling**; the compile/run arm is reachable today with one flag and zero new code.

## The ruling

⭐ **`modes:"ast"` satisfies the conversion contract, and the mode is chosen PER FAMILY by what that
family's `.ref` HOLDS — a per-DIALECT answer cannot exist.** `byte-equal-or-no-delete` demands identical
verdicts before and after, so:

| the family's `.ref` holds | sound arm | wrong arm does |
|---|---|---|
| an AST dump (`(STMT :subj (TT_CHOICE foo/2 …))`) | `ast` — the ONLY sound one | `m3,m4` manufactures reds |
| program OUTPUT (`55` / `hello` / `42`) | `m3,m4` — required | `ast` is vacuous |

Both kinds occur **inside one dialect** — snocone has `parser` (AST ref) and `corpus` (output ref) — which is
precisely why keying the mode to the dialect cannot be made correct.

## Witnesses (incremental build; not a gate verdict, HQ-27 pristine not claimed)

- `.pl` `tests/prolog/parser`, `run --lang prolog` (default `ast`) → `total=134 ast_pass=134 ast_fail=0
  ast_crash=0 ast_hang=0 ast_unproven=0`, **rc=0**
- `.sc` `tests/snocone/parser`, `run --lang snocone` (default `ast`) → `total=67 ast_pass=38 ast_fail=0
  ast_xfail=29 ast_xpass=0`, **rc=0**
- `.sc` `tests/snocone/corpus`, `run --lang snocone --modes m3,m4` → `total=10 m3_pass=10 m4_pass=10`,
  every other counter 0, **rc=0**

## ⛔⭐ The negative control — what makes this a ruling and not an assertion

Same `tests/prolog/parser`, same binary, graded `--modes m3,m4`:

```
m3_pass=0 m3_fail=2 m3_crash=132 · m4_pass=0 m4_fail=2 m4_skip=132     rc=1
```

**A family that is 134/134 GREEN under its correct mode goes 134/134 RED under a blindly-added one.** The
row's own FIRST STEP warned that "an m3/m4 arm added blindly manufactures reds the conversion rows don't
own" — that is now MEASURED, not hypothetical. It also discharges the INSTRUMENT LAWS' burden: the three
green boards above come from an instrument demonstrably capable of failing, so they are not the
vacuous-instrument class.

## Consequences

- ⛔ **Do NOT edit the `LANG_CONFIGS` defaults.** They are right for the parser ladders, which are the bulk of
  what remains, and changing one silently re-grades every already-converted family of that dialect. Select
  per family at conversion time with an explicit `--modes`.
- ✅ No harness development is owed by `tests-consolidate-prolog` or any remaining conversion row.
- ✅ Pre-existing Prolog smoke 3/5 and Snocone 4/5 (baseline s251) are UNTOUCHED — no arm was added, so no
  red was manufactured.

## Provenance correction

The row's GOAL names `tests-consolidate-snocone` as a live consumer; that is **stale** — seat08 CLOSED it
2026-08-28, and its ledger already carries this discovery *in situ* ("wrong default grading mode — this
family's `.ref`s hold program OUTPUT not AST dumps, needed explicit `--modes m3,m4`"). Only ONE row was ever
actually blocked (`grep -c BLOCKED-ON:` = 1). This finding's contribution is to **generalize seat08's local
discovery, prove it in both directions, and put it where the next converter reads it** — the postoffice is
not version-controlled, so a baton-only ruling does not survive a postoffice reset.
