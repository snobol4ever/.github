# RUNG 5 — if-then-else lands on a gate pair that was dead code, and a construct that must UNDO must first BE a choice

**Seat** hq_C (HQ-COMPLETE) · **2026-09-03** · row `prolog-rung-5-if-then-else-negation-once-forall-ignore-and-the-plain-directive-goal`
**Law** `RULES.md` § THE PROLOG REBUILD GATE · **Sovereign** `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E row 5, § B.7, § B.8, § B.17
**Started from origin** SCRIP `8d9809e5` · corpus `3a40f8e3` (hq_C rung 4 + hq_P rung 7)

## 1. Fail-once, pass-once

| arm | tree | result |
|---|---|---|
| fail-once | clean origin `8d9809e5` | `--to 5` **rc=1**, rung 5 PASS=0 FAIL=10 |
| pass-once | this landing, `make pristine` | § 6 |

## 2. What landed

`pl_lower_ite` is Proebsting's `ifstmt` on the **shared gate pair** — `IR_INDIRECT_GOTO` owns the gate slot, one
`IR_MOVE_LABEL` per arm banks it — with **no new box**. C is lowered INTO arm 0's entry (`C.γ → T`, `C.ω → E`);
each arm is lowered with `γ →` its own `MOVE_LABEL`. The four reductions § B.8 already ruled correct land on it:
`\+`/`not` → `ITE(G, fail, true)`, `once` → `ITE(G, true, fail)`, `ignore` → `ITE(G, true, true)`,
`forall(C,A)` → `\+ (C, \+ A)`, and `\=` → `\+ (X = Y)`. `forall` moved out of the rung-8 refusal list.

Plus ceo's re-labelling (CEO-151): **plain directive goals** — `:- Goal.` now runs in **file order, before** the
initialization goals, wrapped as `ignore/1`, so a failing directive does not abort the load. Measured against
swipl on a program mixing succeeding, failing and undefined directives: identical stdout.

## 3. The gate pair was DEAD CODE, and four things were wrong with it

`bb_indirect_goto.cpp` and `bb_move_label.cpp` shipped, compiled, and were reachable from no lowerer — the
pre-cut Prolog machine had been their only user. Reviving them cost four fixes, all in shared machinery, none of
which any existing test could have caught:

1. **`IR_INDIRECT_GOTO` had no drive case at all** — it hit the universal driver's FATAL (`op=39 has no template`).
2. **It was granted no slot for the gate word.** Both templates had *always* addressed `[op_off+16]`; the kind fell
   through `zls_grant_locals`' `default:` and received only its 16-byte result, so the gate write landed 8 bytes
   past the grant. ⭐ **Harmless with one gate box live and a core dump with two**, because the second box's region
   began where the first's gate was still being written — so the defect was invisible until an ITE appeared inside
   another ITE's condition. Same class as the `op_off+24`/`to.limit` hazard hq_C flagged to hq_P at rung 7, in the
   opposite direction: there a box read a word the map gave to something else; here a box wrote a word the map
   never gave it at all.
3. **The RPO walk never pushed an `IR_INDIRECT_GOTO`'s ω target**, so an ITE used as another ITE's *condition* left
   the outer else-arm unreachable, and it silently resolved to the graph ω.
4. **Its ports were inverted for this use.** **α must CONCEDE** and **β must RESUME**, because goals to the right of
   the ITE wire their ω to β while arm tails concede through α. And a **deterministic arm must bank the CONCEDE
   port as its gate (`wantb = 0`)** — banking its own resume port makes the gate jump to itself, which is an
   infinite loop that prints correct output forever.

A fifth, in the emitter: `IR_MOVE_LABEL` inherits its γ from the gate box's γ **node** but read only the *β* marker
off it, dropping σ/φ — so an ITE inside a disjunction branch re-entered the disjunction's α forever. It now
honours σ/φ exactly as the main resolver does.

## 4. THE ONE THAT MATTERED — a construct that must UNDO must first BE a choice

`q(1).  main :- ( \+ q(X) -> write(none) ; write(some) ), nl, ( var(X) -> write(unbound) ; write(bound) ).`
printed **`some bound`**; swipl prints **`some unbound`**.

`q(X)` succeeds and binds `X`; `\+` then fails. **No enclosing choice ever backtracks past that binding** — the
outer ITE simply takes its else arm — so nothing undoes it. § B.8 (iii) states the requirement exactly: *"the undo
on `G.γ` is the one place a SUCCESSFUL goal's bindings are undone."*

Cure: the ITE carries an `IR_BOUND` mark at its entry and two `IR_UNMARK` landings — one on C's failure path, one
on the arms' concede path — pairing by operand exactly as Icon's loop marks already do, and `bb_bound` gains a
pinned arm that banks `r12` instead of `rsp`.

⭐ **And the mark was USELESS on its own.** With the mark banked and the unwind wired, the witness stayed red:
with no live choice `pl_tr_needs_log` returns 0 for every cell, so **the unwind was walking an empty suffix**. The
pinned arm therefore also calls `rt_pl_disj_open(H, fb)`. That is the **third** construct to need it — rung 3's
disjunction, rung 7's generator, now rung 5's ITE. **A construct that must undo must first be a choice.** It is now
a rule rather than three coincidences, and § B.7 says so.

## 5. `ite_condition_throws` is re-filed to rung 9

Flagged at mint as a thing to measure and rule, and measured: the witness needs `throw/1`, a rung-9 builtin that
refuses at **compile** time, so it emits no stdout and cannot pass at rung 5 however good the ITE is. Re-filed in
`ALL.csv` — the same shape as § E row 4's 10⁶ criterion belonging to row 11.

⛔ **What it tests is a real rung-5 property and is NOT lost with the re-file: an ITE must not SWALLOW an
exception.** In the landed shape `C.ω` goes straight to the else-arm entry, so a ball in flight *would* run the
else arm. The cure is § A.1 review C9's `test r15, r15 ; jnz <own ω>` at the else-arm entry — **deliberately not
added here**, because § A.1 measured that `r15` holds a driver mmap address at every Prolog ω today, so the guard
would fire unconditionally. Rung 9 zeroes `r15` and is the first rung that can both add the guard and witness it.
That obligation is written into § B.7 and carried on the re-filed witness.

## 6. Verdict arms — `make pristine` first (HQ-27)

Landed at SCRIP `54536fbf` · corpus `33944ab1`. `make pristine` rc=0, DONE-WHEN **rc=0**.

| arm | reading |
|---|---|
| `test_prolog_ladder.sh --to 5` | ✅ **PASS 22/22** (11 witnesses × 2 modes); rung 5 PASS=8 FAIL=0 |
| `--only 6` · `--only 7` | ✅ **20/20** · ✅ **4/4** — rungs 6 and 7 unmoved |
| `test_gate_pl_port_trace.sh --to 5` | ✅ **GATE PASS(0)**, 22 checks; the four rung-5 blocks cut, rungs 0–4 byte-identical, 66 → 66 blocks |
| `nm -D` · `strip_comments --check` | ✅ 0 · ✅ rc=0 |
| `test_smoke_icon.sh` | ✅ 14/14 both modes |
| `make test` | ✅ rc=0 — SNOBOL4 **m3 1679/0 · m4 1679/0 SKIP=0** |
| **Icon STRICT rung suite** (control arm) | ✅ **264/6/1/27 of 298 in all three modes — UNCHANGED** |
| ITE · cut · disjunction batteries | ✅ **10/10** · ✅ **10/10** · ✅ **12/12** |

⭐ The corpus push hit the same whole-file CSV conflict as rung 4 — the master was regenerated under me again —
and was resolved the same deterministic way: take origin's file, re-apply the one cell, `newline=''` on both ends.
`--numstat` reads **1 1**, which is the check the rung-4 FINDING put in place after shipping `401 401` at rung 3.

## 7. Batteries, both modes, stdout diffed against swipl

**ITE battery 10/10** — resumable then-arm · resumable else-arm · no else · condition commits (a 3-clause
condition yields once) · nested ITE · ITE inside a disjunction · negation leaving its variable unbound · `once`
over a generator · `\=` both ways · backtracking into a goal left of the ITE.
**Rung-4 cut battery 10/10 and rung-3 disjunction battery 12/12 re-run as regression arms**, plus rung 7's ladder
`--only 7` 4/4 — the ITE rides `IR_DISJUNCTION`'s neighbours and hq_P's generator shares the frame regime.
