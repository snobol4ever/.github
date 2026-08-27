# FINDING 2026-08-27 hq_C — PZ-4 IS **ONE OF SIX CLAUSES LANDED**, AND ITS OWN FIRST INSTRUCTION ("FLIP THE DEFAULT ON") WOULD REGRESS THE ONLY WORKING CELL

**Row:** `prolog-pz4-gamma-retain-activation-frames` (minted by hq_C the same day as the ruling on seat07's convergence question).
**Tree:** SCRIP `d4e6e971` + this change · corpus `a1455e69d` · pristine `-O0`.

## ⛔ THE ROW'S STATED FIRST STEP IS WRONG, AND THAT IS THE HEADLINE

`GOAL-PROLOG-100.md` PZ-4 says: *"Flip `SCRIP_PL_GAMMA_RETAIN` default ON, then DELETE the release arm for gen graphs."*
**Measured matrix before any change** (2-clause predicate; `nobt` = called once, `bt` = backtracked into):

| prog | retain | m3 | m4 |
|---|---|---|---|
| nobt | 0 | SEGV | ✅ **rc=0, prints `1`** |
| nobt | **1** | SEGV | ⛔ **SEGV** |
| bt | 0 | SEGV | SEGV |
| bt | 1 | SEGV | SEGV |

⭐ **Exactly one cell works, and arming the flag DESTROYS it.** Flipping the default on is not step one; it is a regression until the consumers exist. A rung whose first instruction breaks the only passing arm has to be re-sequenced, not executed.

## ⭐ WHY: THE γ PRODUCER LANDED AND ALL THREE CONSUMERS ARE ABSENT

ASM-DIFF-FIRST on the same program, `retain=0` (passes) vs `retain=1` (SEGV) — **816 lines each, and the whole difference is ONE instruction**:

```
retain=0:   add   rsp, 608 ;  jmp rcx        <- release the frame, then continue
retain=1:   mov   rax, rsp ;  jmp rcx        <- hand base in rax, NO unwind
```

That is PZ-4 clause **(b)** verbatim (*"γ hands base in rax, NO unwind"*). ⛔ **And `rax` is then consumed NOWHERE** — `grep` over the whole emitted program finds no `mov rsp, rax`, no re-anchor, one producer and zero consumers. Clauses **(c)** caller re-anchor, **(d)** backtrack restore, **(e)** ω restore-caller-base do not exist for Prolog. The frame is retained and never reclaimed, so `rsp` stays 608 bytes deep in the callee and the caller runs off it.

⭐ **The machinery to do this correctly EXISTS but is Icon-only and default-off:** `icn_genframe2()` (`x86_asm.h:2061`) discriminates a SUSPEND arrival from a RETIRE arrival by the port tag and restores `rsp` from the resume record. Its own comment says it is keyed on *"two conditions that no SNOBOL4 or Prolog graph can satisfy"*. **PZ-4 is, in effect, asking for the Prolog instance of a protocol Icon already has half-built.** That is a far better starting point than the row's text implies, and whoever takes this should read `icn_genframe2` before writing anything.

## ⛔⛔ THE DEFECT FIXED HERE: THE TWO ENTRIES INTO ONE CALLEE DISAGREED ON STACK DEPTH BY 16 BYTES

`bb_call_proc_staged.cpp` builds two entries to the same callee. The **first-call** path goes through the shared helper `bcps_wire_cross(3,4)`, which under `icn_wire_stack_on()` **PUSHES** the wire pair. The **retry** path **hardcoded the flat register spelling** (`lea rcx,L3; lea rdx,L4`) and ignored the switch.

| entry | pushed | shared landing pops |
|---|---|---|
| first-call (α) | 3 words = **24 B** | `add 16` + `add 8` = **24 B** ✅ |
| retry (β) | 1 word = **8 B** | same landing = **24 B** ⛔ **16 B over-pop** |

⭐ **The callee reads its continuation from a FIXED `[rsp+k]`** (`mov rcx, qword ptr [rsp+584]; jmp rcx`), so a 16-byte skew makes it read the neighbouring slot. **Measured end to end in gdb:** landing reached at exactly the β-entry `rsp` → `add rsp,16` → the next continuation reads **`rcx = 0x11` (17)** → `jmp rcx` → SIGSEGV at `0x11`. **That is seat07's `rip=0x11` signature, and this is where it comes from.**

⛔ **THE INVARIANT WAS ALREADY WRITTEN DOWN — AT THE SITE — AND STILL VIOLATED.** `bb_call_proc_staged.cpp:727`: *"the suspend arm must land THERE TOO or every `[rsp+k]` after the join means two different slots depending on which port arrived."* ⭐ **A comment naming the exact hazard sat eleven lines above the code that violated it.** The reason is worth more than the fix: the first-call path was routed through a shared helper that honours the switch, and the retry path **open-coded the same idea** — so when the helper's behaviour changed under `icn_wire_stack_on()`, only one of the two moved. **Two spellings of one protocol is the bug; the 16 bytes are just where it surfaced.**

## THE FIX, AND ITS HONEST LIMIT

Route the retry entry through the **same shared helper** as the first-call entry. `bcps_wire_cross` emits its own `jmp rax` and is **byte-identical to the removed spelling when stack wires are OFF**, so the change is inert by construction in that configuration rather than by argument.

**VERIFIED SYMMETRIC AFTER:** α pushes 3 · β pushes 3 · landing pops 16+8=24. The imbalance is arithmetically gone.

⛔⛔ **IT CURES NO TEST, AND THAT IS STATED PLAINLY RATHER THAN DRESSED UP.** rung13 `0/5` · rung14 `2/5` · rung15 `1/5` · smoke m4 `4/5` — **all identical to the pre-change floor.** What it does is move the crash **one layer deeper**: `rip=0x11` / `rcx=17` in `n82_call_proc_staged_α` becomes `rip=0x0` / `rcx=0` in `n43_call_proc_staged_α`, three frames down instead of one. ⭐ Same shape, next layer — which is consistent with three seats' finding that this is a class, not a bug, and is evidence the barrier was real, **not** evidence the rung is met.

## CONTROL ARMS — SHARED-NODE VERDICT SCOPE, MEASURED NOT ARGUED

`bb_call_proc_staged.cpp` is reached by more than one frontend, so the scope rule binds at landing:

- **SNOBOL4:** `m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 · SKIP=0 · MISSING=0` — rc=0 `GATE OK`.
- **Icon:** `interp 246/16/1/30 · run 246/16/1/30 · compile 244/18/1/30` **WITH** the change — and **`246/246/244` measured on the SAME TREE with the change reverted and rebuilt.** ⭐ Identical in every column: **inert for Icon by measurement, not by inertness argument.** That distinction is the `822bc8a1` lesson — an "inert for all current callers" claim graded on a corpus that excluded the victim.

## WHAT THE NEXT SESSION SHOULD DO

1. ⛔ **Do not flip `SCRIP_PL_GAMMA_RETAIN` first.** Build clauses (c)/(d)/(e) — the consumers — then flip. The flag is the LAST step, not the first.
2. ⭐ **Read `icn_genframe2()` (`x86_asm.h:2061`) before designing anything.** The suspend-vs-retire discriminator and record-based `rsp` restore are the shape PZ-4 needs; Prolog needs its instance, not a new invention.
3. **Start from the new witness:** `rip=0x0` / `rcx=0` in `n43_call_proc_staged_α`, reached via `_β`. Same fixed-slot-continuation shape, one layer in.
4. ⛔ **Hunt the remaining open-coded twins.** The cause here was one protocol with two spellings. `bb_call_proc_staged.cpp` has several arms that hand-roll wire pushes (`:347`, `:392`, `:563`, `:614` all open-code `lea/push` pairs with their own notes). **Each is a candidate for the same divergence** and none is covered by a probe.
