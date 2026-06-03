# HANDOFF 2026-06-03 OPUS48 — Pascal BB: PB-9 designed (mode-3/4 entry), build held

**Goal:** `GOAL-PASCAL-BB.md`. **Repos:** SCRIP (`1d92abc`), corpus (`58a7174`, untouched), `.github` (watermark +
PB-8 marked `[x]` + this file). PLAN.md untouched (routine handoff).

No functional code landed. The deliverable is **`SCRIP/PB-9-DESIGN.md`** — a verified, turn-key plan for crossing
Pascal onto compiled BBs, produced by tracing the mode-3/4 path end-to-end rather than from the goal doc's
assumptions. PB-8 is marked complete (the rung-ladder checkbox was stale; the watermark already said COMPLETE).

---

## Why this is a design handoff, not a code one

PB-9 looked like "rebase onto `x86_asm.h` and start." Tracing `hello.pas` through `--run`/`--compile` showed three
things that reshape it, and showed that the seed grew from an apparent one-line gate change into a JIT
byte-encoding arm that deserves a fresh context budget (a wrong byte there is a silent segfault, not a compile
error, so it needs a clean build + 2-mode test + full cross-language regression + commit in one pass). Per the
no-broken-commits rule, I designed to turn-key fidelity and held the build — the PB-7 model.

## The three findings (all verified by running it)

1. **The wiring already exists.** Pascal rides the SNOBOL4 flat chain (the `:subj` proc envelope), so the driver
   routes `.pas` into both compiled paths with **no `is_pascal` flag**: `--run` enters via the `!is_icon &&
   !is_prolog` branch's `gvar_flat_chain_build`/`bb_build_flat`; `--compile` emits a real `main:`/`sno_flat_α`
   prologue. Both reach `bb_call` and abort with `unsupported call shape fn='__pas_writeln'`. The runtime
   trampoline `rt_call_arr(fn,args,nargs)` (`by_name_dispatch.c:1828`) is implemented and reaches
   `try_call_builtin_by_name`, where `__pas_writeln`'s interleaved (value,width) loop already lives.

2. **The seed's one-liner is a trap.** `rt_builtin_is_known` (the `int` gate, `by_name_dispatch.c:705`) omits the
   `__pas_*` family — but routing them to the existing `bb_call_builtin_str` is a dead end, because that arm calls
   `rt_call_builtin`, which is a **`STACKLESS_ABORT` stub** (`rt/rt.c:529`) left behind by the stackless
   conversion. The live path is `rt_call_arr` with a marshalled args array (the `dval==2.0` arr path's mechanism).

3. **One primitive is missing.** There is no frame-ADDRESS helper (`lea reg,[r12+off]`) in `x86_asm.h` — only
   `x86_frame_load64`/`store64`, which `mov` values. The Pascal arm needs the *address* of an N-slot args array in
   `rsi` for `rt_call_arr`. Add `x86_frame_lea` (opcode `0x8D`, same modrm/SIB/disp32 as the `mov` load). It is
   reusable by every later rung that needs a frame address, so not throwaway.

## Pascal IR_CALL shape (`v_det_call`, `lower.c:591`)

`sval`=builtin name · `ival`=nargs · `dval`=**3.0** · `counter`=`IR_graph_t**` arg subgraphs. `writeln('Hello')`
→ parser emits `__pas_writeln('Hello World!', -1)` (width sentinel) → nargs=2, args `IR_LIT_S` then `IR_LIT_I`.
`marshal_call_arg` already marshals `IR_LIT_S/I/F/NUL` + var slots in both TEXT and BINARY forms — sufficient for
the seed and `writeln(intvar)`; expression args need general subgraph eval (PB-9b).

## PB-9a — the seed. FORKLESS. (Full recipe + arm sketch in `SCRIP/PB-9-DESIGN.md`.)

1. Add `x86_frame_lea(reg, off)` to `x86_asm.h` (the one missing primitive).
2. Add a `__pas_*`-prefix-guarded arm in `bb_call_str` BEFORE the abort: allocate `narg` 16-byte slots + a result
   slot; `marshal_call_arg` each `subs[j]->entry`; then `mov rdi,fn` / `x86_frame_lea rsi,base` / `mov32 edx,narg`
   / `call rt_call_arr` / store rax:rdx to the result slot / `jmp PORT_GAMMA` (writeln cannot fail). Mirror in
   MEDIUM_TEXT. No grammar change.
3. `make -j4 scrip`; `scrip --run hello.pas` and the `--compile` link must both print `Hello World!`
   byte-identical to `pint`. Change is `__pas_*`-guarded + one isolated helper ⇒ cross-language regression is safe
   by construction, but PROVE it (stash→rebuild→diff): Pascal 33/0/1, Icon 130/117/36, Prolog 0/0, SNOBOL4 2/0.

## Ladder above the seed

- **PB-9b** int arith + assign + `writeln(int/expr)` — `IR_BINOP`/`IR_VAR`/`IR_ASSIGN` templates exist; needs
  general arg-subgraph eval in the PB-9a arm + the IS_FAIL γ/ω branch.
- **PB-9c** control flow — **`IR_IF`/`IR_WHILE`/`IR_FOR`/`IR_REPEAT` have NO emitter templates** (not in
  `emit_core.c` dispatch). Author each per FACT RULES (one `x86(...)` concat, via `emit_core` dispatch only). The
  four-port wiring is already correct in the IR; the work is the x86 branch/loop encoding. `sieve.pas` is the gate.
- **PB-9d** flat procs/functions + value/`var` params — `bb_call_proc_staged_str` already stages user-proc calls;
  verify Pascal frame-slot seating + the `SlotRef` `var`-reference model survive the crossing. `recursion.pas`.
- **PB-9e** nested procs = **the representation FORK (Lon's call).** Mode-2 uses a `GenFrame` C struct +
  `static_link` pointer; Invariants 2 & 4 forbid that for compiled BBs ("a Pascal frame is a BB, not a C
  function," static link "riding the parent-port thread"). How does the static chain become BB topology in
  mode-3/4 — a parent-port thread through the activation BBs, no C struct, no display? Recommend at PB-9e, not
  before; the PB-7 precedent is the model (design, surface fork, hold for the one-word go).

Aggregates (record/set/pointer) ride their existing builtin/array/bitmask/NV-heap rails — they come along once
`IR_CALL` (PB-9a) and `IR_IDX` (PB-9b/c) emit; no dedicated aggregate rung expected unless a probe forces one.

## Regression evidence (this session, direct rebuild + suites)

Pascal **33/0/1** (the `recursion`/`fact(8)` 16-bit-overflow XFAIL is the documented deferral); Icon `--interp`
**130/117/36** identical baseline; Prolog honest mode-2 **133/0/0** (0 fail / 0 abort — the invariant; the script's
PASS denominator differs from prior watermarks' 132, both honest counts of different coverage); SNOBOL4 smoke
**2/0**. The oracle (`pcom`+`pint`) rebuilds clean with `fpc -Ci -Co -Cr -gl`.

## Gotchas for the next session

- `corpus` build artifacts (`pcom`/`pint`/`*.o`/`prr`/`prd`) are now clean in `git status` (gitignored) — but
  still do not `git add -A` blind; this session corpus was left entirely untouched.
- Parser regen workaround unchanged (full regen script aborts at the snobol4 flex step; regen Pascal directly with
  `bison -d -o pascal.tab.c pascal.y`). No grammar change for PB-9a anyway.
- Two pre-existing cross-language borrows remain logged-and-deferred (Raku-named `v_raku_det_call`/
  `v_raku_mutate_writeback`; the SNOBOL4-style `:subj` proc envelope — which is exactly what gives Pascal its free
  ride into the mode-3/4 flat chain, so do NOT drop it before PB-9 crosses).
- `test/raku/rk_array_literal.raku` fails on the clean baseline (pre-existing).

## Build / verify

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
# seed check (PB-9a target): scrip --run hello.pas  AND  scrip --compile hello.pas (linked)  vs  pint
```
