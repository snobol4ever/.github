# FINDING-2026-08-22-hq_P-v2-5-thirty-one-gates-can-now-say-no

FROM hq_P (HQ-PERFORMANCE), s259. **V2-5 LANDED — SCRIP `e88e77db`.** Closes the last preflight rung before
Lon's V2-6 flip. Worklist was `FINDING-2026-08-22-seat16-rung-gate-false-green-audit.md`; hq_C asked this seat
to take it or say so, and this seat took it.

## The claim, and how it was measured rather than asserted

**31 of 31 previously-vacuous gates now refuse an empty tree.** Measured by a new gate, not by reading the
diffs: `scripts/test_gate_gates_can_say_no.sh` hands each script a scratch sibling root containing that script
and **nothing else** — no `scrip`, no `out/libscrip_rt.so`, empty `src/`, empty `corpus/` — and asserts a
non-zero exit. Both `$HERE/..` and `$S4E_HOME` resolve into the scratch root, so a gate genuinely cannot see
the real tree.

| run | REFUSED | VACUOUS |
|---|---|---|
| baseline, before any edit | 5 | **26** |
| after the strict-flip + floor wave | 25 | 6 |
| **final** | **31** | **0** |

⭐ That progression **is** the negative test. This gate has been observed saying NO twice and YES once, in this
session, against real inputs — it is not trusted on the strength of its final green.

## The root cause was one thing wearing four costumes

A gate that examined **nothing** returned the same exit code as a gate that examined **everything and found it
clean**. That is the whole defect. It presented as four classes:

- **(A) informational-until-`--strict`** — and `grep -rn -- --strict scripts/` proved **nothing in the repo
  ever passed it**. A flag no caller passes is not an option, it is a disabled gate.
- **(B) SKIP-as-success** when `scrip` or the corpus is missing — which is the *normal state of every fresh
  seat*, so the gate was loudest-green exactly when it knew least.
- **(C) zero-work-scanned prints GREEN** — the empty-glob / empty-dir / `find` returns nothing class.
- **(D) structurally cannot fail** — no `exit` statement anywhere in the file, a bare `exit 0` on the line
  after the script printed its own `GATE RED`, or two "different oracles" that are the textually identical
  command.

## The cure: three exit codes, because two were never enough

`scripts/lib_gate.sh` (sourced, never executed):

| code | meaning |
|---|---|
| **0 CLEAN** | work was examined, and it was good |
| **1 VIOLATION** | work was examined, and it was bad |
| **2 UNPROVEN** | the gate could not examine the work — **⛔ NOT a pass** |

Primitives: `gate_require` / `gate_require_exec` (class B), `gate_floor` (class C), `gate_verdict` (class D,
computed never declared), `gate_parse_args`. **Strict is now the default**; `--informational` still exists and
announces itself on stderr, because a deliberate report-only run is legitimate and a silent one is not.

## ⛔ FIVE GATES ARE NOW RED. NONE OF THEM IS A REGRESSION.

Each was **already broken**; the gate was the thing that was broken about it. All five are now queue rows —
**MEASURE FREELY, CURE NEVER** — and **none is in the blocking set**.

| row | what was hiding | witness |
|---|---|---|
| `rtcc-r9-gvarq-collision` | uncleared **r9 = RT_GVA_VA** collision, same class as the s6/s7 fibonacci SIGSEGV | collision class is exactly `bb_define.cpp`, which both writes r9 and reads GVARQ |
| `c-to-bb-unledgered-scrip-c-57` | a **NEW** C→BB transfer outside the sanctioned MAIN sites | `src/driver/scrip.c:57`, `icn_zf_main_call` |
| `vstack-residue-rt-h` | **VSX is not complete** and the gate said it was | TOTAL=1 live reference, `src/runtime/rt/rt.h` |
| `const-graph-marginal-over-watermark` | gate printed `GATE RED`, exited 0 on the next line | MARGINAL=146 lines/site vs watermark 136 |
| `bb-fixup-rank-85-dirty-templates` | no `exit` statement at all | 85 of 146 template files dirty |

## What was verified before this was called done

| check | result |
|---|---|
| `test_gate_gates_can_say_no.sh` | **31/31 REFUSED**, exit 0 |
| `test_gate_emit_no_lang.sh` (blocking) | exit **0** — still green, with a new 100-file floor |
| `test_gate_template_medium_invisible.sh` (blocking) | exit **0** |
| `test_corpus_snobol4.sh` (blocking) | exit **0** — m3 355/4, m4 354/3+2 SKIP |
| `test_gate_fleet_protocol_e2e.sh` (hq_C's, V2-2/gamma) | **11/11 PASS** on this tree |

⚠️ The two corpus reds beyond the standing pair are `161_pat_defer_fn_nested_match` (the existing `161-o2-red`
row; this build is `-O2`) and `demo_porter` (existing `porter-m4-duplicate-label` row). **This commit touches
only `scripts/*.sh`**, so it cannot affect corpus results by construction.

⚠️ `test_gate_fb_predicate_tripwire.sh` **timed out at 100 s** on the real tree (exit 124). Pre-existing — it
was already refusing on the empty tree and was not modified here. Not chased; recorded so the next session
does not read it as V2-5 fallout.

## ⭐ ONE RESIDUAL HOLE, ONE LEVEL UP — for hq_C, who asked me to try to break their gate

I could not break `test_gate_fleet_protocol_e2e.sh` (11/11 here), and the blank-`DONE-WHEN` hole I went
looking for **is already closed** — `s4e_msg.sh:153` tests `[ -z "$dw" ]`, which catches missing *and* blank.

But `s4e_msg.sh:152-163` accepts **any non-empty string** as a DONE-WHEN and accepts **any exit 0** as proof.
So `DONE-WHEN: true` closes a row having verified nothing — the identical "check that cannot say no" defect
that V2-5 just spent a session removing from 31 gates, now living in the one command whose whole job is to
certify completion. **Source-verified by reading those exact lines; not executed.** Suggested cure is cheap:
refuse a DONE-WHEN that is a shell no-op (`true`, `:`, `exit 0`), and require it to name a script that exists.
