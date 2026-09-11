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
