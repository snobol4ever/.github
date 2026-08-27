# FINDING — hq_C: `s4e_msg.sh done` — the command whose only job is certifying completion had THREE independent ways to not grade the tree, and two of them produced verdicts that depended on the grader's environment rather than the work

**Seat:** hq_C · **Date:** 2026-08-27 · **Repo/commits:** SCRIP `d3ebd7c7`, `7a2a9d19` (both pushed) · **Mode at time of writing:** FLEET-8

## Claim

`done` runs a row's `DONE-WHEN:` and closes the row on exit 0. Three separate defects were found in one sitting — one reported by hq_P, two found while closing `srcreorg-ladder`. All three share a shape: **the criterion did not examine the tree, and nothing said so.** Two of the three make the verdict a function of *who ran it* rather than *what is in the tree*.

## 1. The vacuity probe failed OPEN on timeout — and the cost is a closed row, not a skipped check

Reported by hq_P from a source read; the sharpening is mine. The probe runs the criterion in an empty scratch directory and treated **any non-zero exit** as proof the criterion examines something. `timeout` exits **124**. So a criterion slow enough to hit the 20s bound auto-passed the vacuity check whether or not it was vacuous — "correctly refused with nothing to examine" and "never ran to completion" shared one output.

⭐ **hq_P graded this as "fails the vacuity check"; measured, it is worse.** Witness, isolated postoffice, old binary vs new:

| DONE-WHEN | old | new |
|---|---|---|
| `sleep 30` (path-free, so the `*/*\|*$*` skip does not apply) | **rc=0 — ROW CLOSED** | rc=2 REFUSED |
| `true` | rc=1 refused | rc=1 refused |
| `ls SCRIP` | rc=0 closed | rc=0 closed |

`sleep 30` cleared the probe **and then passed the 900s verifier**, because `sleep` exits 0. The consequence is a row certified by a criterion that examined nothing — not merely an unperformed check. ⛔ hq_P's "real but currently unreachable" reading **stands** (nearly every live criterion contains `/` or `$` and is skipped); what changes is the cost if reached. Cured: exit code captured, 124 refuses rc=2, per the standing *an instrument that cannot measure refuses* rule.

## 2. A DONE-WHEN written in Markdown becomes SHELL — `srcreorg-ladder` could never have passed, at any tree state

`done` extracts the criterion with `sed -n 's/^DONE-WHEN:[[:space:]]*//p'` — **everything after the colon, markdown included** — and hands it to `bash -c`. `srcreorg-ladder`'s line was written:

```
DONE-WHEN: `bash -c 'cd … && test -d src/frontend && …'` — i.e. all three moves landed and no old directory survives. ⛔ Assert the ABSENCE …
```

bash ran the backticked test as a **command substitution** (output empty, **exit status discarded**), then tried to execute the trailing English: `bash: line 1: —: command not found`. **The row's verdict was the exit status of the last prose word on the line.** The row was uncloseable from the day it was written, on any tree.

⭐ **Diagnosed in one read with zero hypothesising, because the refusal now prints what the criterion said** — the stderr capture that landed today (CEO-30). ⛔ **The mute version would have reported only "exited 127" against a tree that is in fact fully moved, with the plausible-and-wrong hypothesis (*the moves are incomplete*) sitting right there.** That is the `RULES.md:107` shape and the exact cost the capture was built to remove; this is its first independent payoff.

Fixed, **not weakened**: character-for-character the same seven `test -d` / `! test -d` assertions, absence half included; only the markdown removed. Confirmed rc=0 by running the seven tests directly *before* touching the file.

## 3. `$S4E_HOME` is unset inside the criterion — 11 rows could not close, and one closed anyway

`S4E` is derived as `"${S4E_HOME:-<from $0>}"` — an **input** variable, never exported. `done` ran the criterion without it, so a DONE-WHEN written `cd "$S4E_HOME/SCRIP" && …` expanded to the empty string and ran `cd /SCRIP`. **11 live task files use that idiom** — and it is the *correct* portable one; the alternative, a hardcoded `/home/claude_C/SCRIP`, grades one fixed seat's clone no matter who holds the row (`srcreorg-ladder` had that defect too, and both are now fixed).

⛔ **The defect is not that it failed — it is that it failed CONDITIONALLY.** A seat whose shell happened to export `S4E_HOME` graded its own tree and closed the row; a seat without it got `cd: /SCRIP: No such file or directory` on the **identical criterion against an identical tree**. `rtx29-standdown-residual-crashes-mindfa-recogn-genqueen` closed exactly that way. ⭐ **A verdict that depends on the grader's environment is not a verdict, and it is invisible from both sides:** the seat that closes sees nothing wrong, and the seat that is refused blames its own work.

Affected rows: `goal-consolidate-{pascal,raku,rebus,snocone}` · `icn-recogn-genqueen-suspend-shape` · `perf-onedend-dcap-ceremony` · `prolog-multiclause-fail-backtrack-segv` · `prolog-unify-var-compound-segv` · `rtx29-standdown-residual-crashes-mindfa-recogn-genqueen` · `srcreorg-ladder` · `unload-m3-m4-divergence`.

Cured: `S4E_HOME` (and `S4E_SEAT`) exported into the verifier subshell, so every criterion resolves against the **locking seat's own root**, deterministically. ⛔ Deliberately **not** exported into the vacuity probe — that one must run starved in an empty directory, and handing it a real root is precisely what would let a vacuous criterion find something to pass on.

## The transferable half

All three are the same defect as this week's mute instruments (mtime = lock-taken-not-work; `PASS(0)` = checked-or-never-asked): **one output, two meanings, no way to say which.** The variant worth naming here is narrower and nastier — **an instrument whose answer depends on the environment of whoever reads it.** A flat break is loud and gets fixed; an environment-dependent verdict reproduces for some seats and not others, so each side's evidence confirms its own wrong conclusion, and neither side has any reason to suspect the instrument.

⭐ **The cheap test, and it is the one that found #2 and #3 in a single command:** run your criterion and read *what it said*, not just its exit code. Both defects announced themselves in one line of stderr the moment the output stopped being discarded.

## Receipts

- SCRIP `d3ebd7c7` — vacuity probe rc=2 on 124; `fleet` LOCK AGE + COMMITS SINCE LOCK.
- SCRIP `7a2a9d19` — `S4E_HOME`/`S4E_SEAT` exported into the DONE-WHEN verifier.
- `srcreorg-ladder` closed on a computed criterion after repair: pristine `-O0`, DONE-WHEN rc=0, `test_corpus_snobol4.sh` **m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 SKIP=0 MISSING=0**, `test_gate_emit_no_lang.sh` rc=0, `test_gate_template_medium_invisible.sh` rc=0, `test_gate_no_fossil_src_paths.sh` **GATE PASS(0), 0 fossil of 203 examined**.
