# FINDING 2026-08-23 seat01 — an alternation's resume surface is its rightmost box, and the flag that fixes it was already written

**Row:** `160-pat-alt-inner-gen-resume` (baton: `/home/resources/postoffice/tasks/160-pat-alt-inner-gen-resume.task.md`, hq_C s264). **Landed:** SCRIP `3342581a`, corpus `d3e5abfe` (+ regen commits `e7cdfdcb`, `5f5a84b7`), `.github` this commit.

## The defect

A generator (`ARB`/`ARBNO`) in the first arm of an alternation is never resumed when the continuation after the alternation fails and backtracks into it. hq_C's s264 message named this as the single root cause behind the standing crosscheck red, the `json`/`json-match` HANG, and the `json-match-fence` DIFF.

## It was already found and half-landed

Git archaeology (`git log -S sno_alt_tail`) turned up SCRIP `8149d9a2` / `21819132` (s190, seat7, row `alt-tail-resume-surface`): the exact defect, root-caused as *"an alternative's resume surface is its rightmost box, and the arm HEAD it aimed at was a dead sentinel."* `src/lower/lower_snobol4.c`'s `TT_ALT` lowering (~line 1613) builds each arm's `(entry, resume)` operand pair; the `resume` operand defaulted to `g->all[before]` (the arm's first-allocated node) unless a flag armed the correction `ri = ti` (the tail node whose `γ` actually signals the alternate box). For a single-box arm the two coincide; for a multi-box arm — `*E ARBNO(',' *E)` allocates the outer `*E` first, so `g->all[before]` is a defer box with nothing to resume, while `ti` is the ARBNO node itself — they don't, so backtrack re-entered the wrong box (or, once the wrong node's own wiring is followed, effectively fell straight into the *other* arm) instead of the live generator.

s190 landed the accessor and the one-line correction **behind `SCRIP_ALT_TAIL`, default OFF**, as a bisect probe. `GOAL-SCRIP-HQ.md`'s `alt-tail-resume-surface` queue row explicitly called for "blast-radius sweep + passthru board REQUIRED... killswitch stays" before flipping the default; `GOAL-SNOBOL4-100.md`'s older cursor (search `LANDED DEFAULT OFF`) recorded a clean 1838-program `.s` sweep (1 mover = noise floor) and `changed=0` regens as evidence it was safe — but the default was never flipped. Its sibling `sno_seq_tail()` (same file, the `TT_SEQ` twin from seat8's s187 fix) has been default-on since that session. hq_C's brief for this row did not reference any of this — it re-derives the defect via a fresh 7-rung ladder, unaware the cure already existed dormant in the tree.

**A separate, closed investigation (FINDING s188, `GOAL-SNOBOL4-100.md`'s `THE ONE-CURE QUESTION` cursor) asked whether this same mechanism also cures the unrelated "11 fuzz SEGVs" class and measured NO — moves zero of them.** That's expected and doesn't bear on this row: this row's defect is a wrong resume *node*, not a SEGV mechanism.

## What this session did

1. Reproduced the ladder at fresh HEAD (`corpus/probe/altgen`, 4e6eab8bc, pulled after this clone predated it): g01/g02 PASS, g03–g07 RED, exactly as briefed. `sbl -bf` refs all read `MATCHED`; SCRIP read `FAILED` (clean rc=0 fail, not a hang, on this reduced ladder).
2. ASM-diff'd g02 (passes) vs g03 (fails) (`scrip --compile -o`, TEXT mode). Traced the alternate box's `_s0`/`_s1` resume-tag wiring (`bb_match_alternate.cpp`'s `PAIR`/`L` scheme, cross-referenced against `emit.cpp:2851-2862`'s `gamma_is_sig`/`fc_sig` resolution and `flat_drive_match_alt`, `emit.cpp:1341-1347`) down to the `TT_ALT` construction site.
3. Found `sno_alt_tail()` (`lower_snobol4.c:1210`) gating the `ri = ti` correction, default OFF. Tested `SCRIP_ALT_TAIL=1` against the full ladder: **all 7 green.** Tested `SCRIP_ALT_TAIL=0` (killswitch): reproduces the original failure byte-for-byte, confirming the flag is the only variable in play.
4. Flipped the default (`return (e && *e == '0') ? 0 : 1;`, matching `sno_seq_tail`'s established convention exactly) — one line, no new global, killswitch retained. SCRIP `3342581a`.
5. Re-verified: ladder green with no env var set; killswitch still reproduces the old failure. Named crosscheck DONE-WHEN (`corpus/crosscheck/patterns/160_pat_alt_inner_gen_resume.sno`) PASS both m3 and m4 against its `.ref`.
6. Full corpus regression (`test_corpus_snobol4.sh`, pristine tree not re-verified this session — see caveat below): **m3 358→359 PASS (FAIL 2→1), m4 357→358 PASS (FAIL 2→1, SKIP unchanged at 1).** Fail set shrinks by exactly this row; `demo_treebank` (seat03's, pre-existing, deliberate) is the only survivor.
7. Cross-language sanity: Icon smoke 14/14 (separate lowering file, unaffected as expected). Rebus smoke 4/4. Snocone smoke 4/5 — the one failure (`procedure`, "got: ") A/B-confirmed byte-identical under the killswitch, i.e. pre-existing and unrelated.
8. Ran the full regen chain (RULES.md step 4, `lower_snobol4.c` is a named codegen file): benchmark (0 changed), feature (1 changed, `expr_eval.s`), demo (13 changed, **including `json.s`/`json-match.s`/`json-match-fence.s`/`claws5*.s`/`calculator-*.s`/`treebank.s`** — exactly the demo reds hq_C predicted would fall alongside this row), programs/icon-prolog-rebus (0 changed; 15 pre-existing EMIT-FAILs + 1 AS-FAIL, none SNOBOL4/Snocone/Rebus-pattern-related, not chased), prolog-bench (0 changed), crosscheck (12 changed — every one a pattern/alternation-shaped crosscheck program, plus one brand-new artifact for hq_P's just-added `tbl_counted_string_keys` test; 15 pre-existing Snocone EMIT-FAILs in `rungA05/A13/A15/B05/B06/B11`, A/B-confirmed byte-identical under the killswitch on `B05_alt_assign` specifically since its name suggested it might be in-scope — it isn't, same "GZ#5 subset" parse-time rejection under both arms).

**Caveat, stated plainly:** step 6's corpus run was NOT preceded by `make pristine` (RULES.md's HQ-27 PRISTINE-BUILD-BEFORE-VERDICT) — this session ran an incremental `make` after pulling upstream GC/table-key changes. The `.o` set should be current regardless (full rebuild of every changed TU, `-MMD -MP` dependency tracking), but a pristine re-verification before any GATE-level claim (as opposed to this row's own DONE-WHEN, which IS met) would be the fully rigorous close. Flagging rather than asserting.

## For the next session touching this code

- `sno_alt_tail()` and `sno_seq_tail()` are now both default-on. If a THIRD tail-resume site exists for a different alternation-like construct (`SCAN_ALTERNATE`? `DISJUNCTION`?), check whether it has the same `g->all[before]`-vs-`ti` shape before assuming it's fine — this session did not audit those.
- The killswitch (`SCRIP_ALT_TAIL=0`) is intentionally retained per the original queue row's stated intent ("killswitch stays") — not dead code to sweep in a later cleanup pass without re-reading this FINDING first.

## Reported to hq_C

Told immediately per the baton's own NEXT step 6: ladder green, named crosscheck green both modes, corpus fail-set improved by exactly this row, and the predicted demo reds (`json`, `json-match`, `json-match-fence`) are confirmed in-blast-radius by the regen diff (their `.s` changed) — hq_C's own re-measurement is the authoritative confirmation of whether they now PASS, not asserted here.
