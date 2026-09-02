# FINDING — `pl_cell_to_term` (as opposed to `pl_cell_copy_walk`, the rung-1 FINDING's subject) never
# memoises variables at all, so every `*_cell` service that still round-trips through it — `rt_pl_sort_cell`
# was the instance found here — silently converts SHARED variable occurrences into INDEPENDENT ones. Binding
# one occurrence after msort/sort does not bind the others. Cured in this slice, not just diagnosed.

**seat07 · 2026-09-02 · row `prolog-term-descr-s2-compare-sort-pairs`** (slice s2 of the umbrella;
`rt_pl_keysort_cell`, `rt_pl_bag_prep_cell`, `rt_pl_group_pairs_by_key_cell`, `rt_pl_pairs_keys_values_cell`
and `rt_pl_bag_group_gen` — the rest of this slice's sort/bag family — go through the same
`pl_cell_to_term`/`pb_pairs_extract` surface and inherit the identical defect until converted).

**Cured in the slice that found it** — SCRIP (this rung, `rt_pl_sort_cell` on cells): sharing preserved,
verified both directions, floors green. This FINDING exists because the defect is a DIFFERENT mechanism
than rung 1's (a different converter function entirely, not a variant of the same one), it is INVISIBLE to
`write/1` alone (see §1), and every remaining function in this slice's sort/bag family shares the exposure.

## 0. Answer

`pl_cell_to_term` (`pl_cell_conv.h:11-27`, distinct from `pl_cell_copy_walk`, the rung-1 FINDING's subject,
and distinct from `pl_cell_to_term_named`/`pl_cell_to_term_named_r`, which DO memoise via a `pl_v2t_map`)
mints a brand-new heap `Term` on every single call:

    if (pl_cell_unbound(d)) return term_new_var((int)((t == DT_PLVAR) ? d->slen : 0));

`rt_pl_sort_cell` called it exactly ONCE, on the whole list (`pl_cell_to_term((pl_cell_t *)list_cell)`), but
that one call recurses per list element and per compound argument — so two occurrences of the SAME source
variable cell, reached via two different recursive branches of that one walk, each get their OWN fresh
`term_new_var` result. `rt_pl_term_compare`'s `TERM_VAR` case is a raw pointer test (`a == b`), so two
occurrences of one variable compare as **two distinct, never-equal, address-ordered objects** — the sharing
is gone before comparison even begins. It does not come back on the way out either: `pl_term_to_cell_word_m`
(the cell-conversion for the OUTPUT list) memoises correctly by `Term *` pointer identity, but by then there
is nothing to find — the two occurrences were already two unrelated pointers going in.

Net effect, MEASURED on the pre-change binary (SCRIP `6ede7c31`): `msort([X,a,X,b], L)` then `X = hello` —

    before(L) = [_G0,_G1,a,b]
    after(L)  = [_G0,_G1,a,b]      <- UNCHANGED. binding X did not reach either output slot.

After this rung's rewrite (same binary line, cell-native):

    before(L) = [_G0,_G0,a,b]      <- both slots print the SAME fresh label, because they ARE the same cell
    after(L)  = [hello,hello,a,b]  <- binding X correctly reaches both

## 1. Why `write/1` alone does not catch it

**MEASURED — an unbound variable's printed label is assigned at PRINT time, from the cell being printed,
not carried over from any upstream Term.** So a naive witness that only calls `write/1` on ground terms (or
even on a list containing a lone unbound variable) cannot distinguish "two independent fresh cells" from
"one shared cell, printed twice" — both print SOME `_G<n>` label per slot, and nothing in a single `write/1`
call reveals whether the two labels denote the same storage. The only way to observe the defect is to BIND
one occurrence after the fact and re-print, which is exactly what corpus goals built around `msort`/`sort`
essentially never do (sort-then-print is the natural idiom; sort-then-bind-then-reinspect is not).
**MEASURED — the corpus does not exercise this.** The `.pl` suite's `msort`/`sort` goals (grep for
`msort\(|sort\(` in `corpus/tests/prolog/ALL.pl`) all sort GROUND lists; none sorts a list containing a
variable that is bound again afterward. Length-only or ground-content assertions (as this row's own earlier
rung-2 witness did for `msort([Z,f(Z),a,Z,1], M1), show_len(M1)` — length is 5 either way, sharing or not)
pass identically regardless of which behaviour is present, which is exactly how this stayed unnoticed.

## 2. The witness

    sort([X,X], L1), write(L1), nl.                        % expect [_Gn]  (ISO: sort/2 removes duplicates,
                                                             %  and two occurrences of ONE variable ARE a
                                                             %  duplicate of each other)
    msort([Y,X2,X2,Y], L2), write(L2), nl.                  % expect [_Ga,_Ga,_Gb,_Gb] -- Y encountered
                                                             %  first (list order), so Y's class-0 vord index
                                                             %  is lower and its pair sorts first; consistent
                                                             %  with the rung-1/rung-2 first-encounter law.
    msort([X3,a,X3,b], L3), write(before(L3)), nl,
    X3 = hello, write(after(L3)), nl.                       % after: BOTH X3 slots become hello

MEASURED on this rung's binary, both m3 and m4: `sort([X,X],L1)` -> `[_G0]` (deduped -- see §3 for why this
is a second, correct, consequence of the same fix, not a separate change); `msort([Y,X2,X2,Y],L2)` ->
`[_G0,_G0,_G1,_G1]`; the bind-after case matches the `## 0` transcript above exactly.

## 3. The shape that is correct, and the second consequence worth naming explicitly

Hold `pl_cell_t *` pointers to the ORIGINAL element cells throughout (never convert to `Term`), build the
shared `pl_vord_t` used for comparison ordering by walking every element ONCE up front in list order (the
rung-1/2 law: first encounter, not address), sort with `rt_pl_cell_compare` against that one map, and build
the output list with `pl_make_ref` to the ORIGINAL cells (the same idiom `rt_pl_term_variables_cell` already
uses) rather than allocating independent fresh ones. `pl_deref` transparently follows the resulting ref
chain at every future read, which is what makes a later binding visible through every alias.

⭐ **A second, correct consequence falls out of the SAME fix, not a separate decision:** `rt_pl_cell_compare`'s
class-0 (variable) arm compares by `pl_vord_t` index, and two occurrences of the literal same cell now
correctly get the SAME index (they are, after all, the same cell) — so `sort/2`'s adjacent-duplicate removal,
which was already keying off exactly this comparator, now also removes a variable that is duplicated with
itself: `sort([X,X], L)` goes from the old `[_G0,_G1]` (two independent, un-deduped fresh vars) to `[_G0]`
(one, correctly deduped). This is not a separate bug fix layered on top — it is the SAME underlying identity
correction, observed through `sort/2`'s existing dedup step rather than through a direct rebind.

## 4. Scope: who else inherits this until converted

Every remaining function in this slice's sort/bag family reaches the list contents through `pl_cell_to_term`
or `pb_pairs_extract` (which itself calls `pl_cell_to_term` at `unification.c`, non-memoising, same shape):
`rt_pl_keysort_cell`, `rt_pl_bag_prep_cell`, `rt_pl_group_pairs_by_key_cell`, `rt_pl_pairs_keys_values_cell`,
`rt_pl_bag_group_gen`. None of them is fixed by this rung; each inherits the identical exposure until its
own turn, and whoever converts them should reach for `pl_make_ref` on the ORIGINAL cells the same way,
not re-derive this from scratch. `pb_canon_walk` is the one exception worth flagging rather than assuming:
it explicitly MUTATES `Term` nodes in place for `bagof`/`setof` free-variable canonicalisation (rewrites
`TERM_VAR` to `TERM_REF`), which is a different mechanism again and deserves its own scrutiny, not a
mechanical port of this rung's pattern.

## 5. Chain of custody

- Baseline measured on SCRIP `6ede7c31` (this row's own rung-2 commit, pre-rung-3): `before/after` transcript
  in `## 0` is the exact, unedited program output, both m3 and m4.
- Byte-identity on GROUND terms (the part of the bar that must hold): stash/make/capture, restore/make/capture,
  RT_OPT=-O0, seven-goal ground-term witness (empty list, singleton, ints, nested compounds, pre-existing
  ground dedup) — identical pre/post, both modes.
- The sharing fix and its dedup consequence are DELIBERATE, MEASURED, NOT byte-identical by design (§0, §3) —
  flagged here rather than silently shipped, per this umbrella's own standing practice (rung 1's FINDING did
  the same for a different pair of degenerate behaviours it chose NOT to preserve).
- Floors: `test_smoke_prolog` 5/5 m3 AND 5/5 m4 · `test_gate_pl_coupling` PASS · `test_corpus_prolog_parser`
  RESULT: PASS. SNOBOL4 control arm and umbrella ratchet recorded in the row's own commit/LEDGER, not here.
- SWI-Prolog (`/usr/bin/swipl`) cross-check on the §3 dedup consequence: `sort([X,X], L)` -> a ONE-element
  list (`[_8202]`), confirming a self-repeated variable is ISO-conformant to dedup, independent of this
  runtime's own reasoning about `pl_vord_t` — the same cross-check discipline the rung-1 FINDING used.
