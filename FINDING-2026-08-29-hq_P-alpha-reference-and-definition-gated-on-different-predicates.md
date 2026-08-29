# FINDING: a mode-4 alpha REFERENCE and its DEFINITION were gated on different predicates — 9 link failures, reported as SKIP

**Seat:** hq_P (TRIO) · **Date:** 2026-08-29 · **Row:** `pascal-restore-prezeta` (served by `next`; this was its
`## NEXT` block's named NEXT-ACTOR item) · **Cure:** SCRIP `cb7dc6cf`, rebased to **`c894e6da`** · **Tree:** SCRIP `110b84a5`+cure, corpus
`bd555f8c2`, .github `63529f69` · **Build:** pristine, `RT_OPT` `-O0`.

## THE DEFECT
A DEFINE'd SNOBOL4 procedure whose body **calls `INPUT(...)` or `OUTPUT(...)`** compiled to an object that could
not be linked in mode-4:

```
ld: relocation R_X86_64_PC32 against undefined symbol `Read_α' can not be used when making a PIE object
```

`bb_define_bind()` (`src/templates/bb/bb_define.cpp`) emitted `lea r9, [rip + <fname>_α]` whenever `_.lbl_t0` was
non-null. But `<fname>_α` is **defined** only when the body qualifies as a tiny shim —
`!bb_ab_cell_addr(fname) && bb_tiny_shim_ok(fname, 0)`, the identical test the alpha-seal ten lines below already
used. **A reference gated on one predicate and its definition on another.** `rt_define_tiny_ok` rejects a body
containing an `INPUT`/`OUTPUT` call, so exactly those procedures referenced a label nobody emitted.

⭐ **The driver's own seal site had it right the whole time and is untouched:** it emits `.weak <fname>_α` plus
`@GOTPCREL` (`scrip.c:770`), which is PIE-safe against an undefined weak symbol. Two sites in one compiler
referenced the same possibly-undefined label in two different relocation forms; only one of them was correct.

## PROVENANCE — THE COMMENT PREDICTED IT
Introduced by the `_direct_alpha` change (row `m3-passes-m4-fails-three-polyglot-demos`), which switched `blbl`
from `_.lbl_t0` to `fname + "_α"`. Its own comment, still in the file, says verbatim: *"Un-tested against every
DEFINE role (0-6) this function serves; verify broadly before trusting."* ⭐ **The warning was accurate, specific,
and correctly placed — and it was still load-bearing months later, because a comment cannot fail a build.** That
fix was right about the polyglot case and is PRESERVED wherever the label exists; the cure only narrows *when* the
direct form is used.

## WHY IT SURVIVED: THE INSTRUMENT COUNTED IT AS `SKIP`
`test_corpus_snobol4.sh:127` folds a mode-4 **compile-or-link failure** into `SKIP4`, not `FAIL4`:
```
if ! compile_mode4 "$sno" "$bin"; then SKIP4=$((SKIP4+1)); ...; return; fi
```
So a program that stopped linking left `FAIL=0` intact and moved a counter nobody gates on. ⛔ **This is the
skip-as-success class Lon flagged, in the SNOBOL4 blocking board itself.** It was noticed only because seat14 saw
the *denominator* move (1377→1376) after an unrelated rebase — i.e. by a side effect, not by the signal. A link
failure is a defect, not an abstention: the program was not "unmeasurable", it was **broken**.

## MINIMAL WITNESS AND DISCRIMINATORS (all measured, not reasoned)
```
        DEFINE('helper()instream')                :(helperEnd)
helper  INPUT(.instream, 8)
        helper = 'ok'                             :(RETURN)
helperEnd
        OUTPUT = helper()
END
```
| witness | shape | result |
|---|---|---|
| `INPUT(...)` **call inside** a DEFINE'd proc | the defect | ⛔ `helper_α` undefined → unlinkable |
| `INPUT` read as a **variable** in a proc | control | ✅ links |
| `INPUT(...)` call at **top level** | control | ✅ links |
| `ENDFILE(8)` in a proc | control | ✅ links |
| DEFINE with continuation lines / `SETEXIT` / `:F(FRETURN)` | controls | ✅ link |

⭐ **Mode-3 always ran the witness correctly.** This was an m3/m4 divergence in which m4 emitted an object that
could not link — the class `CLAUDE.md` calls out as carrying its own differential witness.

**Positive control:** `SCRIP_NO_TINY=1` forces `bb_tiny_shim_ok` to 0 and **induces the identical failure on the
passing witness** — the predicate is confirmed by construction, not inferred. `SCRIP_M4_ALPHA_SEAL=0` leaves the
label defined, which is why `_m4seal` is deliberately **not** part of the cure's predicate. Existing killswitch
`SCRIP_DEFINE_FN_DIRECT_ALPHA=0` unchanged (and, before the cure, it alone made the witness link and print `ok`).

## MEASURED — CONTROL ARM AND CURED ARM, SAME PRISTINE TREE
| instrument | control (HEAD) | cured |
|---|---|---|
| master `ALL.sno` m4_pass | 1380 | **1389** |
| master `ALL.sno` m4_skip | 9 | **0** |
| master `ALL.sno` m3_pass / m3_fail | 1389 / 9 | 1389 / 9 (identical) |
| master `ALL.sno` m4_fail | 9 | 9 (identical — pre-existing) |
| blocking board | — | m3 PASS=1442 FAIL=0 · m4 PASS=1442 FAIL=0 **SKIP=0** · MISSING=0, rc=0 |
| smokes | — | icon 14/14 FAIL=0 · prolog 5/5 FAIL=0 · snocone 5/5 · rebus 4/4 |

`ReadWrite_driver` (the named witness) now links and byte-matches its `.ref` in **both** modes.

⭐ **RE-PROVEN AFTER REBASE (the rule that exists because a rebase grades a tree that no longer exists).** The
push rebased this commit onto six others, including the one-flat-suite cutover that repointed the floor runner at
the master pair. Re-ran pristine on the landed tree — SCRIP `c894e6da`, corpus `dd5822de1`:
`m3 PASS=1444 FAIL=0 · m4 PASS=1444 FAIL=0 SKIP=0 · MISSING=0`, rc=0, master total=1495. Of the six commits that
landed under this one, **none touches `src/`** — the only codegen delta in the range is this cure's own 9 lines.
**Shared-node scope:** `IR_DEFINE` is lowered to by `lower_snobol4.c` only (9 sites; every other lowerer 0), so
SNOBOL4 is the graded scope; sibling smokes were run anyway as control arms and are unmoved.

## BLAST RADIUS
17 corpus files carry the shape (a labelled `INPUT(`/`OUTPUT(` call inside a DEFINE'd body), including
`corpus/tests/snobol4/master/ALL.sno` itself, `programs/TZ/TZdef.inc`, `probe/conformance.sno`,
`packages/snobol4/csnobol4_suite/{genc,bench}.sno` and nine `programs/lon_cherryholmes/` files.
`demo/` and `benchmarks/` contain **zero** — which is why the `.s` artifact regen this session shows no change
attributable to this cure (its churn is older drift: a `match_begin` label rename, and define sites still carrying
the *pre*-`_direct_alpha` form, i.e. artifacts stale since before that change landed).

## THE TRANSFERABLE LESSON
⭐⭐ **A REFERENCE AND ITS DEFINITION MUST BE GATED ON THE SAME PREDICATE — and where they cannot be, the
reference must use the form that tolerates absence.** Both halves are present in this one compiler: the driver's
seal site emits `.weak` + `@GOTPCREL` and is correct for a symbol that may not exist; the define site emitted a
direct `lea` and is correct only for one that must. The bug was not either form — it was **two sites disagreeing
about which world they were in.**
⛔ Worth sweeping for: any `x86("lea", ...)` of a `_α`/`_bx` label whose emission is conditional. The grep that
found this one is two lines — take the defined set and the referenced set out of an emitted `.s` and `comm -13`
them. **That check is cheap enough to be a gate and does not exist as one.**
