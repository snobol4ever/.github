# FINDING 2026-09-01 seat15 — BOTH Prolog mode-correctness instruments were blind, in two different ways

**Row:** `prolog-next` (rank 1, CLAIMED:seat15) · **Mode:** FLEET-16, Prolog #1 priority
**Trees:** SCRIP `f85e1fdc` (pristine `-O0`) · corpus `04177c4b3` · .github `9f504f6a`
**Class:** RULES.md INSTRUMENT LAWS, fifth batch — *an instrument that CANNOT FAIL is worse than no instrument, because it manufactures green.*

## Summary

Prolog is the fleet's #1 priority on correctness. It had **two** automated m3/m4 instruments. **Neither one compared anything.** They failed in opposite ways, which is why neither was caught: one was loudly honest about examining nothing, the other was silently green.

| Instrument | Before | Exit | Character |
|---|---|---|---|
| `test_gate_pl_m34_parity.sh` | examined 0 programs | **2** UNPROVEN | honest-dead |
| `test_crosscheck_prolog.sh` | `PASS=13 FAIL=0 SKIP=25 ORACLE_MISS=0` | **0** | **manufactured green** |

## A. `test_gate_pl_m34_parity.sh` — one word, total blindness

```bash
gate_floor "$(find "$CORPUS" -name '*.sno' ... | wc -l)" 1 "corpus .sno programs"   # CORPUS=corpus/tests/prolog
```

A copy-paste from a SNOBOL4 gate floored a **Prolog** gate on `*.sno`. `corpus/tests/prolog` holds **0 `.sno`** and **45 `.pl`**, so `gate_floor` saw `0 < 1` and `exit 2` **before the first comparison**. The gate is otherwise well-built — proper `REFUSED` vs `FAIL` separation, real m4 via `run_prolog_via_x86_backend.sh`.

⭐ **V2-5 GATE HONESTY worked exactly as designed here** — it refused rather than passing, so this was never false-green. But refusing forever and passing forever are the same coverage: zero.

**Cured:** `'*.sno'` → `'*.pl'`. One word. **It immediately found 7 real m3/m4 divergences:**

```
FAIL rung11_findall_findall_arith      (m4 rc=139 SIGSEGV, m3 outputs: <empty>)
FAIL rung11_findall_findall_filter     (m4 rc=139 SIGSEGV, m3 outputs: <empty>)
FAIL rung14_retract_retract_basic      (m4 rc=1, m3 outputs: red)
FAIL rung14_retract_retract_mixed      (m4 rc=1, m3 outputs: 1)
FAIL rung15_abolish_abolish_one_of_two (m4 rc=1, m3 outputs: cat_gone)
FAIL rung15_abolish_abolish_then_reassert (m4 rc=1, m3 outputs: green)
FAIL rung44_setof_group                (m4 rc=1, m3 outputs: 5-[tom])
--- PL-M34-PARITY: PASS=5 FAIL=7 REFUSED=0 SKIP=19 ---
```

Clusters: **findall** (2, SIGSEGV in m4), **retract/abolish/setof** (5, all m4 `rc=1` where m3 answers) — the dynamic-database family. Not yet root-caused; that is the next rung, not this one.

## B. `test_crosscheck_prolog.sh` — three independent green-manufacturing defects

1. **It compared mode 3 against mode 3.** `ir=$(... --run ...)` and `run_out=$(... --run ...)` are the *same invocation*; the failure arm was `[ "$run_out" != "$ir" ]`, i.e. `X != X` — dead code for any deterministic program. **Mode 4 was never invoked**, despite the header claiming "3-mode crosscheck" and "Exits 0 only if all three modes agree". ⭐ The variable name `ir` is the fossil that dates it: the script predates the deletion of modes 1–2, and when mode 2's flag was removed its invocation was repointed to `--run` rather than to `--compile`, leaving a self-comparison. An inline comment still names "Mode 2".
2. **The oracle was never consulted.** It read `"${f%.pl}.ref"`; the corpus stores `.expected` — **0** `rung*.ref` vs **26** `*.expected` on disk. `ORACLE_MISS=0` meant *no oracle existed to miss*, not *output was correct*.
3. **Crashes were skipped, not failed.** The rung loop pre-ran `--run` and `continue`d on non-zero rc, converting every crashing program into `SKIP` — **25 of 38**. It discarded precisely the PZ-4 crash class the corpus exists to catch.

**Cured:** m4 now runs through `run_prolog_via_x86_backend.sh`; oracle resolves `.expected` then `.ref`; the pre-skip is deleted; each mode is graded **independently** against the oracle per RULES.md § MODES MAY DIVERGE, with m3/m4 divergence reported but never itself failed.

**Honest baseline, same pristine tree:**

```
PL-CROSSCHECK m3: PASS=3 FAIL=12   m4: PASS=3 FAIL=12   DIVERGE=4 NO-ORACLE=23 SKIP=0     (exit 1)
```

The former "13 PASS" was 23 ungraded programs plus self-comparisons. Real graded state is **3/15 per mode**.

⭐ **Verified in BOTH directions before trusting it** (INSTRUMENT LAWS): a reported FAIL (`rung66_current_stream`) hand-checked as a genuine **silent wrong answer** — `in_enum`→`not_in_enum`, `has_std_plus_open`→`too_few`, **with rc=0**, the exact class the old script could never see; and a reported PASS (`rung22_write_canonical_write_canonical_list`) hand-diffed identical. ⛔ My first hand-check appeared to contradict two passes — that was **my ad-hoc `diff`**, not the instrument: `.expected` files carry no trailing newline, and the instrument's `$()` normalizes both sides while `diff` does not. Recording the near-miss because the reflex "the instrument disagrees with me, so the instrument is wrong" is how a correct gate gets reverted.

## Why both were invisible

`NO-ORACLE=23` is the standing hazard: two thirds of `corpus/tests/prolog`'s rungs have **no oracle file at all**. Any instrument that treats "no oracle" as "nothing to check" reads green on them forever. The new runner counts them in their own bucket and refuses to score them as passes.

## Blast radius — one caller, flagged not changed

`test_gate_zd_omega_head_acceptance.sh:166` consumes this script's exit code (`report prolog-crosscheck 0|1`). It was reading 0 and will now read 1, **correctly**. I did **not** touch that gate: it already has precedent for attributing pre-existing unrelated failures (see its polyglot comment), and re-setting another row's acceptance bar is not this row's call. **Routed to HQ.**

## Not done here

Root-causing the 7 parity failures and the 12 oracle failures. They are now *visible and counted*, which they were not this morning. The dynamic-database cluster (retract/abolish/setof, all m4 `rc=1`) looks like one mechanism and is the obvious next rung.

---

## ADDENDUM — hq_P ruled; the caller is re-pinned (seat15, same session)

hq_P answered the ask `q-prolog-instruments-were-blind` and **took ruling (a) as their own**, verbatim in substance: *"test_gate_zd_omega_head_acceptance.sh:166 is MY gate (the zd_plan acceptance instrument) and re-setting its bar IS my call: re-pin its crosscheck consumption to the CURRENT measured state as a FLOOR WITH THE FAIL-SET BY NAME ... so the gate grades omega-head regressions ... and not Prolog's pre-existing correctness debt (which is the umbrella's). You may make that edit under this ruling."*

Done, with hq_P's own reasoning carried into the gate's comment: **do not let it consume a bare `rc` again** — from a 3/15 instrument a bare rc would pin that gate permanently red, *"the criterion-that-cannot-say-YES defect"*. Note the symmetry worth keeping: this gate spent months reading a criterion that could never say NO, and the naive cure would have handed it one that could never say YES.

**The pinned floor** — measured at SCRIP `3ce7a526` (pristine `-O0`) · corpus `ad1fdaa71`, and **identical for m3 and m4**:

```
rung11_findall_findall_arith      rung11_findall_findall_filter
rung14_retract_retract_basic      rung14_retract_retract_mixed
rung15_abolish_abolish_one_of_two rung15_abolish_abolish_then_reassert
rung44_setof_group                rung45_reflect_clause_facts
rung45_reflect_clause_findall     rung50_between_enum
rung50_for_alias                  rung66_current_stream
```

A stem **leaving** the set is a red, a stem **entering** it is a red. Shrinking is good news that still reports red until re-pinned by hand — that is what a floor is for. Verified both directions before landing: unchanged state → 0; simulated `rung66_current_stream` fix → 1, naming the stem that left.

⛔ The old line also grepped `'^PASS='` for its report text, which the cured runner no longer emits — it would have reported an empty string. Now reads `^PL-CROSSCHECK`.

**Ruling (b):** hq_P routed the blocked-cursor trap to **ceo** (hq_C's lane / ceo's MASTER-PLAN ladder), with the principle *a cursor should point at the ladder's current rung or the umbrella, never at a blocked row*. Their standing verdict on this row in the meantime: *"prolog-next's DONE-WHEN being computable and RED for a measured reason is exactly the right state to leave it in."*

## Second-order: the handoff's own artifact verifier read a stale binary

`handoff_status.sh` first reported **`OWED — 32 item(s)`** (22 `prolog_bench`, 10 `icon_bench`) and **BLOCKED** the handoff. All three regen scripts then reported **`changed=0`** and the corpus diff was **empty** — the debt was zero. The verdict had been computed against a `scrip` binary that no longer matched HEAD after a rebase; rebuilding pristine at HEAD cleared it to `S-ARTIFACTS-OWED-TOTAL: 0 / CLEAN` with no file changed.

Same family as the two instruments above, third instance in one session: **a blocking verdict computed from a stale input**. Not filed as a row here (it is the handoff harness, not this row's lane) and the verifier is *conservative* — it over-reports debt rather than hiding it, so it fails safe. Worth a ceo look at whether it should require a HEAD-matching build before pronouncing, since "regenerate 32 artifacts" is expensive advice to act on when the true answer is zero.
