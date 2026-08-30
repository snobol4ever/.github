# FINDING — df800d2c (the __builtin_setjmp swap) is a TRIGGER, NOT A CAUSE. The FENCE-branch SIGSEGV reproduces
# IDENTICALLY on the reverted tree with POSIX setjmp untouched, from nothing but a `volatile char[16]` added to
# rt_call_arr_bl. The longjmp never fires at all — probed, not assumed. The real defect is the
# calling-convention-depth-tracked invariant (a fixed rsp-relative offset trusted across a call boundary), and
# it is NOT monotonic in frame size: 16/24/48/56/64 crash, 8/32/40 do not. ⛔ THE REVERT REMOVED A PERTURBATION,
# NOT THE DEFECT — main is still one runtime frame change away from the same SIGSEGV.

**hq_P · 2026-08-30 · row `builtin-setjmp-mechanism-and-perf-reland`** (part (a), ESTABLISH THE MECHANISM —
hq_C's brief: *"'the builtin longjmp restores less state than POSIX longjmp' is an ATTRACTIVE STORY WITH NO
EVIDENCE YET THAT THE LONGJMP FIRES AT ALL — establish that first, before building on frame-liveness."*)

⭐ **hq_C's caution was exactly right and it was right for a bigger reason than they knew: the longjmp does not
fire, AND the setjmp is not the cause either.** Diagnosis only — nothing committed to SCRIP.

## 0. Method

Two `git worktree` checkouts **outside the seat root** (a worktree inside it becomes a permanent
`handoff_status.sh` blocker), each with its own objdir by construction, each `make pristine`, `RT_OPT=-O0`:
**BAD** = `df800d2c`, **GOOD** = `a6201590` (current main, post-revert). Witness is hq_C's, verbatim in shape:
```
        P              =  FENCE(BREAK('abc') $ v0) REM
        'a+a+a'        ?  *P RPOS(0)
```
BAD `rc=139`; GOOD `rc=0`, prints `done v0=`. Reproduced before anything was concluded.

## 1. ⛔ THE LONGJMP NEVER FIRES — REFUTED, NOT MERELY UNSUPPORTED

`fprintf` probes at **`core_runtime_error` entry** and at **both `__builtin_longjmp` sites** (`core.c:2109`,
`:2144`), compiled into the BAD tree. **The witness SIGSEGVs with ZERO probe output.** `core_runtime_error` is
never entered; neither longjmp executes. So the whole frame-liveness story — *builtin longjmp restores fewer
callee-saved registers than POSIX longjmp* — is **dead**, and no work should be built on it.
⚠️ **AND A CORRECTION TO A METHOD NOTE IN THE BRIEF, because it cost hq_C this result:** *"a gdb breakpoint on
it did not resolve in the m3 binary"* — **it resolves fine.** The breakpoints are on symbols in
`libscrip_rt.so`, which is not mapped until the process starts. Set them **after `start`** (or
`set breakpoint pending on`) and all of them bind: `rt_call_arr_bl` at `by_name_dispatch.c:4762`, `rt_num_arith`
at `arithmetic.c:209`, `c_rt_jct_relop` at `:4918`. ⭐ A breakpoint that "does not resolve" is a statement about
*when you asked*, not about the binary — and here it was the difference between an unproven story and a refuted
one.

## 2. THE FAULT SITE — A SLAB BLOCK ENTERED WITH rsp = 0

```
   0x…093:  sub    $0x10,%rsp        <- rsp is ZERO on entry, becomes -16
   0x…097:  movabs $0x2,%r11
=> 0x…0a1:  mov    %r14d,(%rsp)      <- SIGSEGV, rsp = 0xfffffffffffffff0
```
`rip` is inside the m3 sealed slab (no symbol), and `rsp=0xfffffffffffffff0` is hq_C's recorded signature
exactly. ⭐ **The value is -16, i.e. `0 - 0x10`: rsp was restored as ZERO and then decremented** — hq_C's read
("a stack-pointer restore from a wrong slot") is correct. `rt_call_arr_bl` is entered **once**, with sane rsp,
immediately before; the slab runs inside its dynamic extent. ⚠️ I did **not** trace instruction-by-instruction
where the zero is read from, so the *provenance of the 0* is stated as unproven; a fixed-offset restore
(`mov 0x30(%rsp),%rsp`) sits a few instructions earlier in the same slab region.

## 3. ⭐⭐ THE CONTROL EXPERIMENT — THE SETJMP SWAP IS NOT THE CAUSE

`__builtin_setjmp` changed `rt_call_arr_bl`'s **compiled frame**, not its semantics: 134 → 149 instructions,
**four extra callee-saved pushes (`r12`,`r13`,`r14`,`r15`)** that the GOOD build never emits, and locals moving
`-0x58/-0x60/-0x64/-0x68` → `-0x78/-0x80/-0x84/-0x88`. Measured stack depth at `rt_call_arr_bl` entry differs
between the trees by **176 bytes**.
✅ **So I perturbed the GOOD tree's frame the crude way instead — POSIX `setjmp` untouched, no builtin anywhere,
one added line:** `volatile char _hqp_pad[N]; _hqp_pad[0]=0; _hqp_pad[N-1]=0;` at the top of `rt_call_arr_bl`.

| pad bytes | 8 | 16 | 24 | 32 | 40 | 48 | 56 | 64 | 96 | 128 | 176 | 256 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| result | ok | **SEGV** | **SEGV** | ok | ok | **SEGV** | **SEGV** | **SEGV** | **SEGV** | **SEGV** | **SEGV** | **SEGV** |

**The padded GOOD tree crashes with the byte-identical signature** — same `rsp=0xfffffffffffffff0`, same slab
offset `+0xa1`, same `mov %r14d,(%rsp)` after `sub $0x10,%rsp`.
⛔⛔ **THEREFORE `df800d2c` DID NOT INTRODUCE THIS DEFECT. It perturbed a frame, and the perturbation exposed a
defect that was already there.** A `volatile char[16]` does the same thing, and so will the next unrelated
change that touches this function.
⭐ **AND NOTE THE SHAPE: IT IS NOT A THRESHOLD, IT IS A PATTERN.** 8, 32 and 40 are clean; 16, 24, 48, 56, 64+
crash. Five of the eight sizes tested fault. **Whether the program works is an essentially arbitrary function of
an unrelated C function's frame layout** — which is the `calling-convention-depth-tracked` GOAL's own sentence,
observed in the wild: *"a fixed rsp-relative offset trusted across a call/return boundary with NOTHING tracking
accumulated depth — never enforced, only usually satisfied."* This is what "satisfied by accident" looks like
when you sample it.
⚠️ Scope kept honest: padding changes GCC's **register allocation** as well as frame size, so the variable is
"any perturbation of `rt_call_arr_bl`'s frame and allocation", not frame size alone. I did not isolate the two,
and I tested one function only.

## 4. ⛔ WHAT THIS MEANS FOR THE ROW, AND FOR main

- **(a) MECHANISM: ESTABLISHED, and it is not setjmp.** It is the calling-convention defect, row
  `calling-convention-depth-tracked` (rank 0, hq_P), whose invariant this reproduces exactly.
- ⛔ **THE REVERT DID NOT FIX THE DEFECT AND main IS STILL VULNERABLE.** `8846246a` was the correct emergency
  call — correctness outranks perf and the hard m4 gate was red — but it bought back a *frame layout*, not an
  invariant. **Any future change that grows or reshapes `rt_call_arr_bl`'s frame can re-trigger this**, and it
  will again present as "commit X broke the FENCE entries" with X blameless.
- ⭐ **`git bisect` DID ITS JOB AND STILL NAMED THE WRONG THING.** It answers *which commit changed the
  observable*, which is not *which commit is wrong*. Every arm was honest, three-times-repeated, pristine, one
  worktree each — and the first-bad-commit was a trigger. **When a bisect lands on a commit whose diff cannot
  explain the failure — here: only `src/runtime/*.c`, zero emitter, zero templates, so the emitted code is
  byte-identical — that is evidence for a latent defect plus a perturbation, not evidence that the diff is
  subtly wrong.** hq_C recorded exactly that constraint and it was the key to the whole thing.
- **(b) RE-LAND: not yet, and not because the perf work is suspect.** Re-landing `df800d2c` on top of a live
  convention defect would simply re-trigger it. Correct sequencing is convention first, perf second.
  ⭐ There is also a strictly better re-land available that needs no GCC builtin at all: the commit's own
  rationale notes the longjmp fires **only when `g_error != 0`** (default 0, set only by explicit `&error`).
  §1 confirms it never fires here. So the win is to make the setjmp **conditional** rather than cheaper —
  skipping it entirely on the default path is a larger saving than swapping its implementation, and it perturbs
  no frame. **Not designed or measured here; recorded as the shape to evaluate.**

## 5. Not attempted

No cure; nothing committed to SCRIP. The zero's provenance inside the slab is not traced. Only
`rt_call_arr_bl` was perturbed — whether other frames on the path show the same pattern is untested, as is
whether the other four setjmp sites matter. The conditional-setjmp re-land is a sketch, not a measurement.
