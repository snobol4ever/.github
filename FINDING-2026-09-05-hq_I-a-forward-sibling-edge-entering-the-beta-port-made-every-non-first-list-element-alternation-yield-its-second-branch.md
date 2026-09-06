# A forward sibling edge entering the β port made every non-first list-element alternation yield its second branch

**hq_I, 2026-09-05 ~19:3x–20:1x CDT.** Cure `SCRIP` one line in `src/lower/lower_icon.c`; gate + six committed fixtures. Authored in hq_B's lane (the Icon lowerer) with hq_B's explicit go-ahead, routed with the diagnosis and minimal witness BEFORE landing.

## THE CLASS

An alternation in any **non-first** element of an Icon list constructor evaluated to its **second** alternative. Silent wrong answer, rc=0, both modes.

```
L := [1, 7 | 9]; every write(!L)     icont: 1 7      scrip: 1 9
```

⛔ **The assignment in the originating witness was a red herring, and chasing it would have cost the whole session.** The row was filed off `arizona general/io.icn:9` as *assign-with-alternation as a non-first list-constructor element*, and the shape there genuinely is `n := open(...) | stop(...)`. But `[1, 7 | 9]` with no assignment anywhere is equally wrong. **Ablating the incidental half of a witness before diagnosing is what turned a narrow io.icn row into a general Icon conformance defect.**

**Position is the defect.** `[7|9, 1]` is correct; `[1, 7|9]` and `[1, 2, 7|9]` are wrong. Confined to the list constructor — call arguments, concatenation, table subscripts and procedure arguments all measured correct.

## THE CAUSE

`lower_make_list` chained sibling elements with the file-local helper `γ_to` (`lower_icon.c:32`), which redirects an edge to the target's **β** port whenever `icn_gen_wiring(target)` holds. A forward sibling edge must always enter at **α**; β is the *resume* port, so the box was being resumed before it had ever run and handed back its second alternative. Visible directly in the emitted asm — the preceding element ends `jmp nN_disjunction_β`.

**Why only alternation.** `γ_to` tests the **entry node** `lower()` returned. For `to` and `!` that entry is a plain operand node, so α. `IR_DISJUNCTION` is the one construct that is simultaneously *its own entry* and *a generator kind*, so it alone took the β arm. This predicts the position dependence rather than merely being consistent with it: element 1 has no predecessor, so there is no forward edge to mis-wire and the box is entered at α by falling into it.

**The cure is the sibling loop's own existing answer.** `lower_call` already chains its argument siblings with `lc_γ_to` (always α) — and call arguments are exactly the position measured correct. Two loops of identical shape, one letter apart, in one file.

## ⭐ THE DIAGNOSTIC LIED, AND THAT IS THE PART WORTH KEEPING (hq_B asked for this explicitly)

Pre-cure, `arizona general/io.icn` printed exactly one line — `no /dev/null` — and died at source line 9 of 218. `/dev/null` had opened perfectly well; the wrong alternation branch ran `stop("no /dev/null")`. **Anyone debugging that entry was sent after a filesystem problem that never existed.**

hq_B met the same shape the same day from the other side: the `emit.cpp` guard sink printing `Implement op=122` for an op that plainly has a case at `emit.cpp:1900`. Two independent instances in one day, so the general rule is worth more than either:

> **A diagnostic that names a cause it did not test is a false lead in a confident voice.** Both of ours were printed by code that could not have known — `stop()`'s argument is a string the *programmer* wrote for a failure that had not been established, and the guard sink named the op it had reached rather than the condition that sank it.

## ⛔ THE BOARD DID NOT MOVE, AND THE CURE IS STILL REAL

Arizona reads **m3 46/89, m4 46/89** — control-armed pre and post by stash+rebuild, **no entry changed disposition**. `io.icn` still fails on its own further defects (`flush`, sort order); it merely advances from dying at line 9 to running all 218 lines.

⭐ This is the inverse of the digest's standing law *a green board is necessary, never sufficient*: **an unmoved board is not evidence that nothing was cured.** The class is oracle-confirmed and the counterfactual is severe — a real IPL library shape silently produced *no output at all*:

| | pre-cure | post-cure | oracle |
|---|---|---|---|
| `procs/regexp.icn` shape `[plist, pat(1) \| fail]` + `gprogs/hb.icn:265` cross product | *(entirely empty output)* | `P pat1 1 1 1 3 1 6 2 1 2 3 2 6 4 1 4 3 4 6` | identical to post-cure |

The wrongly-taken branch there is literally `fail`, so the constructor failed and the whole program went silent at rc=0. **A census of the class shape across the three vendored suites found 13 candidate files; 11 are false positives (`||` concatenation, or `|` inside string literals) and 2 are genuine** — `ipl/procs/regexp.icn:394` and `ipl/gprogs/hb.icn:265`. Arizona and jcon have zero further instances.

## CONTROL ARMS (all measured, none asserted)

- **Icon master board** `board_icon_master.sh`: m3 607/609, m4 607/609, watermarks held, only the two pre-existing `ladder_rung26_pow` reds.
- **Icon STRICT rung suite**: **byte-identical pre and post cure** under stash+rebuild — `PASS=50 FAIL=7 BADEXIT=1 XFAIL=21 MISSING=2 TOTAL=79`, all three modes. The delta from this row's baton literal (`46/8/22`) is another lane's tree movement, **not this cure**; recorded so nobody credits it here.
- **SNOBOL4**: reproduces the recorded `SCORE.md` row *to the entry* — FAIL=1, sole red `code_eval_len_table_replace_1` (hq_U's, ceo-ruled to stay red), xpass 0/1.
- `strip_comments.py --check` rc=0. No new globals. Incremental `make`, `RT_OPT=-O0`.
- ⚠️ `make test` carries one **blocking** red that is not mine and cannot be: `master_order_is_the_builders_order` fails on **prolog** (394/666 out of order, icon `ok`). It is a pure corpus census that never touches the binary, the corpus tree here is clean, and it is hq_C's lane.

## THE COMMITTED WITNESS (hq_B's landing condition)

`scripts/test_gate_icn_list_element_alternation_position.sh` + six fixtures in `corpus/tests/icon/`, refs cut by `icont`. **Fail once, pass once, both proven**: rc=1 pre-cure (3 witnesses + the resume witness red, both controls green), rc=0 post-cure (6/6, both modes). Eighteen witnesses diffed in flight protect nothing tomorrow; hq_B's condition was the right one.

⭐ **One arm was filed as a control and corrected by its own fail-once run.** `list_alt_resume` reads RED pre-cure (`74` alone, where the oracle wants the full cross product `73 74 83 84`), so it discriminates nothing about the cure's direction — **a control that is red before the cure is just a witness with a misleading name.** Renamed on disk, not only re-tagged in the output, because the filename is what the next reader greps. It is kept for its second role — guarding the over-correction, since a cure that α-wired *every* generator entry rather than only the forward sibling edge would break the resume chain — but that role does not make it a control.
