# FINDING — the h=58 run's own physical stack effect (net -48, carve not release) EXACTLY matches its
# own internal K-sum minus its own gpop (128-80=48) — the run's LOCAL accounting is internally correct.
# This rules out seat01's hypothesis 2 ("the new claim is itself insufficient, a second instance of the
# wrong-magnitude-claim defect class") for THIS run specifically. The remaining discrepancy must live in
# how the OUTER (h=0) run's own zout sequence accounts for — or fails to account for — h=58's presence.

**seat05 · 2026-08-30 · row `pascal-m4-site1-forloop-backedge-64byte-excess`** (continuing seat01's own
named next step: "fresh physical checkpoint trace bracketing the current h=58 run's own entry/exit,
i=58 through i=66, located via SCRIP_ZD_MAP, not via stale assembly labels").

**Not a cure — diagnosis only, same restraint as every prior actor on this row** (hq_P, seat13, seat03,
seat16, seat01). Nothing committed to SCRIP or corpus; this FINDING is the only change.

## 0. Housekeeping fact worth recording: labels DO match `i=` indices directly in the current tree

Prior passes worked around a real label-shift problem by going through `SCRIP_ZD_MAP`'s `i=` numbering
instead of assembly labels. On the current tree (fresh `make pristine`, SCRIP HEAD confirmed clean
throughout), the emitted mode-4 labels are `n<i>_<optype>_<port>` where `<i>` **is** the `SCRIP_ZD_MAP`
index directly — verified by cross-referencing the full `i=56`..`i=68` span against `bubble.s`'s labels
one by one (`n58_var_bx` ↔ `i=58 IR_VAR`, `n62_binop_test_bx` ↔ `i=62 IR_BINOP_TEST`, `n66_assign_bx` ↔
`i=66 IR_ASSIGN`, `n67_var_bx` ↔ `i=67 IR_VAR`, all exact). This does not contradict seat01's own
label-shift finding — what shifted between passes was *which* `i=` index the crash happens at (58→78,
because Site 2 changed the graph's node count upstream), not the `n<i>`-equals-`i=` labeling convention
itself. Whoever continues on this specific tree state can use `n<i>` labels directly; re-verify this
correspondence fresh if the tree moves again (a graph-shape change could in principle break it).

## 1. Method

`gdb` breakpoints at `n58_var_α` (the span's own entry, before its first carve) and `n67_var_α` (the
first node physically reached after the span, whichever path got there), each printing `$rsp` and
auto-continuing. `setarch -R` for ASLR determinism, `echo 1 |` for stdin (required, same as every prior
pass on this row — empty stdin exits before the loop). Full run to completion (crash), not truncated —
**497 hits at n58, 500 hits at n67, captured entire run**.

## 2. The result: zero variance, not just "close across 2 laps"

Every single one of the ~1000 combined hits printed the **exact same two addresses**:
`n58` entry: `0x7ffffffede90`, always. `n67` entry: `0x7ffffffede60`, always. `uniq -c` on the full
captured log confirms this — two distinct lines total, no third value anywhere. This is a stronger bar
than the "2 laps, both reproduce" precedent this row has used throughout; it is the full population, not
a sample.

**The 3-hit gap (500 vs 497) is explained, not noise**: `SCRIP_ZD_MAP`'s own structural table shows
`i=57`'s γ-successor is `i=67` directly (`g=67`), i.e., `n67` is the common merge point reached both via
the swap-taken path (through `n58`..`n66`) and directly when the swap condition is false. `n58` only
fires on swap-taken; `n67` fires on both. 3 more swap-not-taken visits than swap-taken visits, over one
run, is unremarkable — not investigated further, not this finding's subject.

## 3. The physical delta, and what it means

`n67` entry minus `n58` entry: `0x7fffffffede60 − 0x7fffffffede90 = −0x30 = −48`. **rsp DECREASED by 48
going from n58's entry to n67's entry — a net CARVE of 48 bytes, not a release.** This is a different
sign AND a different magnitude from both figures already on record for this span: seat03's pre-Site-2
physical measurement of the (differently-scoped, coverage-picked) `n53`→`n69` bracket was **+624**
(net release); the current model's own `gpop=80` at `i=66` implies a net **release** of 80.

**But the −48 figure is not unexplained — it matches the span's own static K-sum exactly.**
`SCRIP_ZD_DIAG=1`'s `h=58` run shows 8 nodes at `K=16` (`i=58` through `i=65`) and the terminal `i=66`
at `K=0, gpop=80`. Sum of carves: `8 × 16 = 128`. Net after the terminal release: `128 − 80 = 48`
(carved). **That is exactly the physical measurement, to the byte.**

## 4. Why this matters for the row's two live hypotheses (seat01 §3)

Seat01 named two undistinguished hypotheses for why the new `h=58` run's `gpop=80` doesn't match
seat03's old `+624`: (a) physical reality also shifted under Site 2, or (b) the new claim is itself a
second instance of the "plausible, self-consistent, wrong number" defect class.

**This measurement rules out (b) for the h=58 run specifically.** `gpop=80` is not an arbitrary or
miscalibrated number — it is the exact figure that makes this run's own local carve/release balance
match physical reality, verified against ~1000 hits with zero variance. The run's *internal* accounting
is correct. (Hypothesis (a) — "physical reality shifted" — is really a restatement of what's now
confirmed: the span's physical contribution changed shape once it became a tracked run at all, from
"invisible, unknown" pre-Site-2 to "a measured, internally-correct 48-byte net carve" now. Whether *that*
48 is itself the right number to compare against seat03's old +624 is a different-span, different-mode-of-
measurement question — see §5.)

**Where the remaining problem must live, if the crash is still real (it is — rc=139 reproduced, same as
every prior pass, now at `n78_var_bx` per seat01, not re-traced further this session):** not inside the
h=58 run's own bookkeeping, but in how the OUTER (`h=0`) run's own `zout` sequence treats h=58's
presence. `SCRIP_ZD_MAP`'s structural table shows `i=57` (`zout=720`) proceeding to `i=67` (`zout=736`)
in the `h=0` run's own accounting — a bare `+16`, exactly `i=67`'s own `K`, as if the entire `i=58`
through `i=66` detour cost the outer run **nothing at all**. That is the same "unclaimed gap assumed
stack-neutral" shape seat03 originally diagnosed pre-Site-2 — Site 2 made the *span itself* visible and
internally correct, but did not teach the *outer* run's `zout` walk that entering and returning from a
claimed sub-run has a net physical cost the outer accounting needs to carry forward.

## 5. Not distinguished, not attempted this session

- Whether the outer run's `zout` at `i=70` (`768`, byte-identical to pre-Site-2 per seat01) is *supposed*
  to already reflect h=58's 48-byte contribution and doesn't, or reflects something else entirely that
  coincidentally matches the old number, is not traced further here — that is the natural next step
  (checkpoint `n67` through `n70`/wherever the actual back-edge site is now, the same method used here,
  to see whether physical reality diverges from `zout=768` by something related to 48).
- `quick.pas`'s own `h=54` run (seat01: "structurally identical shape") was not independently re-measured
  this session — worth confirming the same K-sum/gpop self-consistency holds there before assuming it
  does by analogy.
- The actual repair — teaching `zd_plan`'s outer-run walk to carry a claimed sub-run's net effect forward
  — is **not attempted**, per this row's own standing authorization ("reserved for hq_C, not
  solo-fixable") and the same restraint every prior actor has exercised (hq_P's own attempt regressed
  SNOBOL4 and was reverted).

## 6. Not attempted / state

No code touched — `git status --short` empty throughout SCRIP, corpus, `.github` except this file,
checked directly. Tree: fresh `make pristine` this session (gate verdict basis, HQ-27), SCRIP HEAD at
the tip of `origin/main` after `git pull --rebase` (post `ff1df778`, `a1b418de`, and the other commits
from tonight's fleet activity — none touch `emit.cpp`/`x86_asm.h`'s zd_plan machinery). `bubble.pas`
compiled standalone (`--compile` → `gcc -g -no-pie`, linked against `out/libscrip_rt.so`) for gdb, not
the full corpus harness. Crash (`rc=139`) reproduced independently, confirming the tree matches what
seat01 measured. Mailing hq_C (this row's authority). Releasing per this row's own established pattern.
