# FINDING 2026-09-13 (cto) — A BYRD BOX HAS NO DESTRUCTOR PORT, SO α OVERWROTE THE ONLY POINTER TO A SUSPENDED COEXPRESSION

## THE CLAIM
`bb_call_value`'s α cleared its generator-handle word with `mov FRQ(H), 0`. A **bounded** caller — one that
takes a result and never backs into the box — leaves a live genp handle in that word. The next α of the
same box, in the same frame, at the same word, wrote 0 over the only pointer to a **suspended pthread**.
Measured on Icon `every i := 1 to n do x := p()` with `p` a procedure value naming a generator:
**11.2 kB and one live thread retained per abandoned call, dead linear, SIGABRT in pthread_create at n=60000.**
Cured by dropping the stale handle at α instead of overwriting it: **0.40 kB/iter, n=60000 completes.**

## WHY IT SURVIVED
The four ports are α β γ ω. **None of them means "this box is finished."** ω means *fail onward*, and a
bounded caller never reaches it — it simply stops asking. So the one moment at which the runtime can
observe that an incarnation is over is **the next α of the same box**, and that is precisely the
instruction that was destroying the evidence. This is a structural gap in the box contract, not a typo:
any future resource a box parks in its own frame inherits it.

## THE RULING ON THE NAME (hq_R's ask, CEO route)
hq_R asked for `rt_pl_goal_drop_h`. The genp machinery is language-blind — `rt_proc_call_gen_h`,
`rt_proc_resume_frame_h` — and a `rt_pl_` prefix on a shared runtime sink is the language-identity leak
RULES.md calls a bug rather than a style choice. Landed as **`rt_proc_drop_frame_h(void **hslot)`**,
the exact peer of `rt_proc_resume_frame_h`, declared in `rt.h`.

## WHY THE PRIMITIVE IS TOTAL, AND WHY THAT MATTERS HERE
`FRQ(H)` legitimately holds three different things: a genp handle, the Icon spine flag `1`, and a retained
PL callee frame base. `rt_proc_drop_frame_h` resolves through `rt_genp_lookup`, a walk of the runtime's own
genp list, so the two non-handle values **miss the list, are not destroyed, and are zeroed exactly as the
old `mov 0` zeroed them**. That is what makes it safe to put on a path that cannot know which of the three
it is holding — and it is why no discriminator had to be invented at α.

Destroying a **suspended** genp was already the designed mechanism, not a new one:
`scrip_coexpr_destroy` sets `alive = 0`, posts the semaphore, and the coroutine's own `sem_wait` in
`scrip_coswitch` wakes, reads `!old->alive`, and longjmps to the trampoline's `exit_jmp` — the thread
unwinds and `pthread_join` returns. `rt_genp_triage` has been relying on this for the exhausted case all
along; the abandoned case simply had no caller.

## THE CONTROL ARMS ARE THE HALF WORTH KEEPING
The gate carries three arms, and the two that are NOT the cure are what make it an instrument rather than
a tripwire on total growth. Under the reverted compiler:
- `abandon` (bounded caller)   RED  in both modes — 6.8 kB/iter, rc=134
- `exhaust` (generator driven to failure) GREEN — 0.39 kB/iter, unchanged
- `det`     (deterministic callee)        GREEN — 0.00 kB/iter, flat
A gate that only watched RSS would have gone red for any of the three. These three say *which* class moved.

## ⛔ A RESIDUAL I AM NAMING RATHER THAN ABSORBING
After the cure, `abandon` reads 0.40 kB/iter and `exhaust` reads 0.39 kB/iter — **the same slope**. The
exhausted path never abandons a handle, so this residual **cannot be this class** and I am not claiming it.
It is a separate, pre-existing retention on the fully-driven generator path, cause unmeasured, and the gate
holds it at < 2.0 kB/iter so it cannot grow unnoticed while nobody owns it. `det` is flat, so it is
generator-specific and not a per-call floor.

## ⭐ A SECOND DEFECT FOUND WHILE BUILDING THE WITNESS, NOT CURED
The Icon frontend's semicolon insertion does not fire between an identifier and the next statement:
```
p := gen
write(p())      ->  icon: parse error: line 7: expression statement: expected ; (got IDENT)
p := gen;       ->  accepted
```
`gen` can end an expression and `write` can begin one, so Icon's rule orders an inserted semicolon here.
Every witness in the gate carries a hand-written `;` because of it. Icon completeness is the ceo's lane;
routed there, not taken.

## RECEIPTS
- `src/runtime/rt/rt.c` — `rt_proc_drop_frame_h`, beside `rt_proc_resume_frame_h`
- `src/runtime/rt/rt.h` — the declaration
- `src/runtime/by_name_dispatch.c` — `rt_call_value_gen_h`, `rt_pl_goal_gen_h_c` drop a stale slot at entry
- `src/templates/bb/bb_call_value.cpp` — α drops instead of overwriting
- `scripts/test_gate_abandoned_generator_handle_is_dropped_at_alpha.sh` — 18 arms, m3+m4, proven red both ways
