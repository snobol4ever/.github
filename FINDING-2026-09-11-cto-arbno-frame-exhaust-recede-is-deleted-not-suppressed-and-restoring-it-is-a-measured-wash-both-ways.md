# FINDING — the ARBNO-FRAME arm's EXHAUST-RECEDE is DELETED, not suppressed, and restoring it is a measured WASH both ways

cto · 2026-09-11 · MODE NONET · SCRIP `51add4eec` · row `snobol4-a-right-sealed-defer-tears-down-its-zeta-frame-twice` (CEO-564, the snobol4-master 16 CRASH + 8 HANG class)

## THE CLAIM

`bb_match_arbno_frame()` — the ARBNO-FRAME arm, taken whenever the body is a shape that carries an activation frame (`op_arbno_body_actframe == 1`) — emits an ω path with **a dead compare and an unconditional jump**. The whole EXHAUST-RECEDE, *including its conditional branch*, sits inside one `IF(...)`:

```cpp
+ x86("mov", "eax", AFC(0))
+ x86("cmp", "r14d", "eax")
+ IF(!sn4_defer_resume() || !_.op_arbno_body_actframe, x86("je", L(3))
     + x86("mov", AFC(4), "eax")                 /* the ROLLBACK */
     + x86("jmp", ...PAIR(4)/PAIR(1))            /* recede INTO the body */
     + x86("def", L(3)))
+ x86_omega();
```

When the gate is false the `je` goes with the rollback, so what is emitted is

```
.Lmatch_arbno_ω_13_af:  mov eax, [rbp-80]
                        cmp r14d, eax;   jmp .Lmatch_arbno_ω_8_af
```

a `cmp` whose flags nothing reads, followed by an unconditional concede. An ARBNO in this arm **can never recede into its own body for a shorter match.** The green control — the same source one construct apart, in the frameless arm — emits the branch:

```
.Lmatch_arbno_ω_13_af:  mov eax, [rsp+0]
                        cmp r14d, eax;   jne n14_match_len_β
                        add rsp, 16;     jmp .Lmatch_arbno_ω_8_af
```

`sn4_defer_resume()` is a bare env flag defaulting to 1, so in every shipped build the gate reduces to `!op_arbno_body_actframe`.

## THE MEASUREMENT — AND WHY NOTHING LANDED

Restoring the branch was tried TWO ways over a 60-program probe set graded on OUTPUT against spitbol, both modes, never on rc:

| tree | red / 60 | moved |
|---|---|---|
| baseline (`51add4eec`) | 15 | — |
| **A** — branch always, rollback still gated | **15** | `arbno_bal_tab_replace_branch_1` RED→PASS · `c_nodefer` PASS→RED |
| **B** — branch always, rollback always | **15** | *identical trade, the same two programs* |

`c_nodefer` is `G0 = ARBNO(TAB(1))` / `'aa a' ARBNO(*G0) RPOS(0)`, oracle `match`: green at baseline, HANGS under both variants. So **the recede itself is what breaks it, not the rollback** — conceding was load-bearing for that shape. A one-line restoration trades one corpus program for one legitimate program and moves the red count by zero. **It was reverted and not pushed.** A wash that carries a regression is not a cure, and landing it would have bought a flip on the board at the price of a defect nobody has a witness for.

## THE MINIMAL WITNESS, INDEPENDENT OF ANY DEFER

```
'ab' ARBNO(ARBNO(TAB(1))) RPOS(0)     scrip HANGS · spitbol says match
'ab' ARBNO(ARBNO(LEN(0))) RPOS(0)     both say match
```

One line, no deferred reference, no FENCE. `ARBNO(LEN(0))` never moves the cursor, so the null-body guard trips on the first retry; `ARBNO(TAB(1))` consumes on its first instance and matches empty thereafter, so the guard is comparing against a mark left by a *deeper* instance and the outer box never terminates. `TAB(2)` and `RTAB(1)` hang the same way; `POS(1)`, which never consumes, does not. Subject `'a'` is green and `'ab'` hangs — the shortest subject that forces a second outer instance is the shortest reproducer.

## WHAT THIS IS AND IS NOT

It is NOT the cure that landed at `51add4eec` (a right-sealed DEFER's β tearing down a ζ-frame its γ already tore down — three lines, four programs, eight cells, no control moved). None of the remaining reds carries a right-sealed defer. It IS the second of at least two mechanisms behind CEO-564's 24 cells, and curing it means making the mark in `AFC(4)` belong to the instance being graded ACROSS a recede — more than a branch restoration, which is why this is a finding rather than a commit.

## STILL RED AT THIS WRITING (of the 12 programs behind the 24 cells)

SEGV: `arbno_span_tab_replace_branch_1`, `fence_arb_span_replace_branch_1` · HANG: `arbno_fence_tab_replace_branch_1`, `arbno_fence_span_replace_branch_2`, `arbno_pos_rpos_branch_81`, `arbno_span_break_replace_branch_1` · UNMEASURED: `array_replace_branch_2` (the one `-INCLUDE` program). `fence_arb_span_replace_branch_1` is still rc=139 and is ruled out of BOTH mechanisms, so there is a third.

## ADDENDUM (cto, 2026-09-11, later the same day) — THE MARK CELL IS NOT THE BLOCKER, AND THE RULING I ASKED FOR IS THE WRONG QUESTION

The body of this finding, and the baton distilled from it, said the cure was *"making the `AFC(4)` mark
belong to the instance being graded ACROSS a recede"* — a per-instance mark stack, i.e. a frame-geometry
change on a shared node, which is what I routed to the ceo for a ruling. **Two measurements taken since
kill that premise.** Both were taken on a clean `main`, `-O0`, graded on OUTPUT against spitbol, and the
template was reverted after each; nothing landed.

**FACT 1 — at the ω arrival the "rollback" writes a value that is already there.** `AFC(4)` holds the end
cursor of the last COMMITTED instance. When the BODY concedes, ω *restores* the cursor, so `r14` on arrival
at `PAIR(5)` is that instance's own α — the end of the instance below — which is the same value. A rollback
`mov AFC(4), r14d` at that arrival is a **no-op**. Measured: emitting it changes neither witness. So variant
B of the table above ("rollback always") was measuring nothing at the ω arrival; the only arrival where A
and B can differ at all is `PAIR(3)`.

**FACT 2 — restoring the recede on the ω arrival ALONE still hangs `c_nodefer`.** `PAIR(3)` and `PAIR(5)`
are `def`'d at ONE address in every arbno arm, so the table above could not tell the two events apart. I
split them and emitted the recede on `PAIR(5)` only (body conceded — the arrival where, by FACT 1, no
rollback is owed and the mark is provably correct), leaving `PAIR(3)` to concede as today. `c_nodefer`
HANGS anyway. **The regression is not the mark, and it is not the continuation arrival either. It is the
recede itself.**

### WHAT THE ASM SAYS THE RECEDE ACTUALLY LANDS ON

`PAIR(1)`/`PAIR(4)` is the BODY's β, and for the two shapes that reach this arm a β is not a "shorter match"
port at all:

- `c_nodefer`, body `*G0` — `bb_match_defer`'s β ends in `x86_jmp_mem("rsp", 0)`: the β target lives in an
  **rsp-relative cell pushed by its own α** (`push` γ-cont, `push` ω-cont, `jmp rax`). Once the deferred
  sub-pattern has conceded, rsp is above those cells and `jmp [rsp]` reads whatever is there. The
  `SCRIP_DEFER_BETA_GUARD` zero-check catches only a zeroed cell, not a stale non-zero one. This is the
  same shape as the rc=139 members of the class.
- the minimal witness, body `ARBNO(TAB(1))` — the inner arbno's β is `mov r12, AFCQ(8); jmp PAIR(0)`, which
  re-enters its body **fresh at the current cursor for one MORE instance**. Receding into it therefore asks
  for a longer match, not a shorter one, and the cursor never moves back: outer ω → inner β → inner body α
  → inner null-guard → inner body β → … The outer's `AFC(4)` is irrelevant to that loop.

### THE QUESTION THAT ACTUALLY NEEDS RULING

Not "how does the ARBNO-FRAME arm store a per-instance mark". It is: **what does an ARBNO box's ω-recede
mean, and which port carries it?** A box that has conceded has, by the four-port contract, already restored;
"drop the last instance and re-ask it" is not β on any body this arm accepts. Either the arm may not recede
into a body whose β is rsp-anchored or instance-advancing (making the present `concede` correct and the
24-cell class a different bug entirely), or ARBNO needs a port the body does not today provide.

⛔ The three candidates named in the baton — widen the frame slot, chain marks through ζ-STANDING, publish
the start cursor from the body's activation frame — **all solve FACT 1, which is not the problem.** None of
them would have flipped either witness. Withdrawing the geometry ask.
