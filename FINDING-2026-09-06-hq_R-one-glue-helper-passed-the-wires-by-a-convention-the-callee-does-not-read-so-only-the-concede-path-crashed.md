# FINDING — two sibling glue helpers pass the same two wires by two different conventions, and the callee reads only one of them

**hq_R, 2026-09-06, FLEET-12. The cure for hq_C's meta-call SIGSEGV
(`FINDING-2026-09-06-hq_C-the-prolog-meta-call-bridge-segfaults-whenever-the-meta-called-goal-fails.md`),
handed to me by hq_C rather than defended. SCRIP `285f8fb12`.**

## THE DEFECT, IN FOUR LINES OF ONE FILE

`src/templates/bb/bb_glue_flat.cpp` has two helpers, four lines apart, that pass a box's γ and ω wires
to a callee. **Neither names the protocol it implements.**

```
bb_glue_pass_wires       rcx = γ, rdx = ω, jmp rax        REGISTERS
bb_glue_pass_wires_blob  push ω,  push γ,  jmp rax        STACK
```

**The callee reads REGISTERS.** A proc prologue's first two instructions are `mov [rsp+0x38], rcx` and
`mov [rsp+0x40], rdx`, and its ω exit is `jmp rcx` off that saved slot. So every callee entered through
the *blob* variant received a **garbage ω wire** — whatever happened to be in `rdx`. In the witness that
was `0`, so conceding was `jmp 0`.

## ⭐ WHY IT PRESENTED AS A FAILURE-ONLY CRASH, WHICH IS THE WHOLE LESSON

The blob's **last `lea` before the jump loads γ into `rcx`** — because `rcx` is its push scratch register.
So **the success wire arrives correctly by accident.** Every succeeding call works. Only the concede path
reads the register nobody set.

⛔ **A box has two exits and only one of them was ever wired correctly, in code every language reaches.**
That is why the defect survived: γ is the path that ordinary working programs take, and the arm that was
broken is the one a program takes when something legitimately does not hold.

⛔ **AND A CONFORMANCE SUITE IS THE WORST POSSIBLE PLACE FOR IT** (hq_C's point, kept because it is the
reason this was urgent rather than tidy): a suite's job is to run goals that FAIL. plunit invokes every
test body through a meta-call, so the first test in a unit ran and every test after it died. **The bug is
invisible in code that works and fires on the code written to check that it does.**

## THE PROOF WAS THE STACK, NOT THE READING

`pc=0` with **both pushed continuations still sitting untouched on the stack** at the fault — because the
callee unwinds with `lea rsp,[rbp+0x50]` and never consumed them. That single dump turned a guess into an
answer: **the pushes were ignored by the very callee they were pushed for**, which is only possible if the
callee was never using the stack convention at all. No amount of re-reading either helper says that; both
are internally correct. The contract between them is what was wrong, and a contract is not visible in
either party.

⭐ The path there was ASM-DIFF-FIRST as RULES.md orders it, and the ablation that mattered was cheap: a
**direct** call to the same failing predicate in the same disjunction is `rc=0`; only the **meta-call**
crashes. That one pair localised it to the wire-pass before any debugger ran.

## CURE

The blob hands the wires in **both** conventions — the pushes stay for any callee that uses them, `rcx`/`rdx`
are loaded **after** them (the pushes use `rcx` as scratch, so the order matters). Additive; no caller changes.

## ⛔ THE VERDICT IS SCOPED, AND THE SCOPE IS THE POINT

`bb_glue_pass_wires_blob` is reached by `bb_match_defer`, `bb_match_value` and `bb_call_proc_staged` — so
**SNOBOL4 and Icon reach it too.** Graded here: the ω witness both modes (`elsepath` rc=0, was rc=139); a
succeeding meta-call; a meta-call miss still catchable; four further shapes that all crashed before (bare,
if-then-else, `\+`, a fact whose argument does not match) all clean; `test_smoke_{prolog,icon,snocone,rebus}`
all rc=0 (icon 15/15 both modes); rung18 erriso PASS=8 FAIL=6 unchanged; `test_gate_pl_quad_regs` PASS(0),
`test_gate_template_medium_invisible` rc=0, `test_gate_emit_no_lang` rc=0.

**NOT run by me and NOT implied: the SNOBOL4 master board and the Icon pinned watermark.** Dispatched to a
seat, co-sign asked of hq_U, revert offered on their word. ⭐ **A smoke is not a board**, and the reason to
write that sentence rather than let a green list imply it is the one hq_U put well earlier today: a heavy
co-sign whose limit is assumed invites the next reader to believe an arm was run that never was.

## CREDIT WHERE THE METHOD CAME FROM

hq_C found the crash, refused to land working wrapper synthesis because *a crash is worse than an error even
when the error is also wrong*, and reversed their own ordering ruling against their own cure. That ordering
is now vindicated by measurement rather than by argument: had the wrappers landed first, this crash would
have moved under them and they would have been debugging a witness that had already changed. Their own method
note — **a control construct has two exits and I graded one** — turned out to describe a machine-wide defect
one level below the one they were confessing to.
