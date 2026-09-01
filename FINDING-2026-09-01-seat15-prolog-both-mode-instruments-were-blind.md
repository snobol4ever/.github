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
