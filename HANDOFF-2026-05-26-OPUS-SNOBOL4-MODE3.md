# HANDOFF 2026-05-26 — Opus 4.7 — SNOBOL4 mode-3 (--run) fixes

Continues the "get SNOBOL4 and others working in SCRIP mode 3 (emitted x86)" thread.
Two mode-3 JIT bugs fixed this session, both in `src/processor/sm_jit_interp.c`.

## Commits (SCRIP)

- `f9ade004`/`4d498065` — real-literal SM_PUSH_LIT_F xmm0/rdi calling-convention bug
- `2e6ff06b`/`e6661590` — restore r13=STATE/r12=stack before nested blob call

## Method: isolate the mode-3-ONLY failures

The SNOBOL4 jit smoke (`scripts/test_smoke_snobol4_jit.sh`) runs the crosscheck
corpus under both `--interp` (mode 2 ref) and `--run` (mode 3). The actionable
target is the DELTA: tests that PASS --interp but FAIL --run = true mode-3
codegen gaps (not shared pattern-engine bugs that fail in BOTH modes).

```
out=$(bash scripts/test_smoke_snobol4_jit.sh 2>&1)
echo "$out" | grep -m1 "interp  failures:" | sed 's/.*failures://' | tr ' ' '\n' | sort -u > /tmp/if.txt
echo "$out" | grep -m1 "run failures:"     | sed 's/.*failures://' | tr ' ' '\n' | sort -u > /tmp/rf.txt
comm -13 /tmp/if.txt /tmp/rf.txt   # run-only failures = the queue
```

Progress this session: --run 149 → 155 → 158; run-only gaps 35 → 29 → 26.
--interp steady at 181 (reference path never touched).

## Fix 1 — real literals were garbage in --run (`f9ade004`)

`rt_push_lit_f(double v)` read its arg from xmm0 (SysV convention), but BOTH
mode-3 emit paths passed the double's bits in rdi (sl_emit_one:1937
`sl_mov_rdi_i64(raw)`; trampoline:1595 `mov rdi,imm64`). Result: every real
printed as garbage (`3.4` → `1.4e-71`). Changed `rt_push_lit_f` to take
`uint64_t raw` and memcpy to double internally; both call sites already correct.
Recovered the real-number cluster (311_concat_numeric, 412_arith_real,
003_output_real_literal, …): +6 --run.

## Fix 2 — recursion/label segfault from clobbered r13/r12 (`2e6ff06b`)

The whole linear blob relies on `r13`=STATE and `r12`=stack-base (callee-saved),
set via inline asm at top-level entry (sm_jit_interp.c ~1723, ~2230). But
`rt_call_fn` entered a CALLED proc's blob via `((blob_fn_t)blob)()` WITHOUT
re-establishing r13/r12. Although callee-saved, this C function may use them as
scratch (compiler restores them for ITS caller, not for the nested blob), so the
nested blob saw a clobbered r13 and faulted on the first `cmp [r13+16]` — i.e.
the first conditional jump (SM_JUMP_S/SM_JUMP_F) inside a DEFINE'd function.

Symptom: any user function with an internal `:S(label)`/`:F(label)` branch to a
mid-body label segfaulted in --run. Diagnosis path: bisected to a minimal repro
(function + `:s(base)` + mid-body label), proved a bare label and even an
unconditional `:(base)` jump were FINE, then traced last_ok/sp at the jump (clean)
and realized only the conditional jump reads a register (r13) directly — which a
C-side nested call doesn't preserve as STATE.

Fix: mirror the top-level entry asm (set r13/r12 from g_jit_state) immediately
before `((blob_fn_t)blob)()` in rt_call_fn. Fixes 088_define_recursive_fib
(was segfault → 0 1 8 55), 1012_func_locals (was stack underflow → PASS 7/7),
and all internal-label functions. +3 --run.

⚠ This is a correctness/safety fix (callee-saved register discipline). Likely
also protects the Icon recursion path (same rt_call_fn), though Icon smoke
doesn't exercise the pattern so its counts were unchanged.

## NEXT — remaining run-only mode-3 gaps (26), clustered

- **OPSYN / APPLY** — `1015_opsyn`, `1018_apply`, and the `1010` Error-5 tail
  (OPSYN alias `facto`→`fact` not resolved in --run; the recursion part of 1010
  is now fixed by Fix 2, only the alias remains).
- **Indirect reference `$`** — 014/015_assign_indirect_*, 210/211/213_indirect_*
  (the `$name` operator path in mode-3).
- **Capture binding** — 058/059_capture_*, W07_capt_* (`.`/`$` capture in --run).
- **DEFINE edge** — 090_define_entry_label, 094_data_define_access, 100_roman_numeral.
- **Misc** — 910_convert, fileinfo, literals, test_math.

Plus the LARGE shared pattern-engine block (`*_pat_*`, W04_arbno, fence tests)
that fails in BOTH --interp and --run — that is a deeper pattern subsystem issue,
NOT mode-3 codegen, and should be tracked separately from this thread.

Suggested next pick: OPSYN (small, 2-3 tests, and unblocks the 1010 tail), then
indirect-`$` (5 tests, one mechanism).

## Gates (all green, both flag states where applicable)
smoke_icon 5/5 · smoke_snobol4 (m2) 13/13 · unified_broker 23 ·
icon fib(7)=13 under SCRIP_JIT_FLAT_BB=1 · SNOBOL4 --run 158 · --interp 181.
