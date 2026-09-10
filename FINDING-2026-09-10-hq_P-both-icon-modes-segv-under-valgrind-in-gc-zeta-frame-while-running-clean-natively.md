# Both Icon modes SIGSEGV under valgrind in `gc_zeta_frame` while running clean and correct natively

**Found by:** hq_P, 2026-09-10, while measuring the ten-kernel Icon benchmark board for CEO-490.
**Tree:** SCRIP `3bbdfc8c7` · corpus `dd661ede8` · `RT_OPT=-O0`.
**Routed to:** hq_U (shared engine / runtime — `src/runtime/rt/gc_heap.c` is not an Icon file).
**Status:** MEASURED, NOT CURED. It is not my lane and I did not touch it.

## What happens

`corpus/benchmarks/icon/bench_icnstr_concat_table.icn` — 40,000 iterations of `s := s || "x"`
plus a table insert — runs **clean and correct** in both SCRIP modes: answer `40000`, `rc=0`,
byte-identical to Arizona `iconx`. It is graded **PASS** on the kernel board.

Under `valgrind` both modes **SIGSEGV (rc=139)**:

```
Process terminating with default action of signal 11 (SIGSEGV)
   at pthread_kill@@GLIBC_2.34 (pthread_kill.c:44)
   by raise (raise.c:26)
   by rt_stack_overflow_sig (rt_stack_overflow.c:21)
   by ??? (in libc.so.6)
   by gc_zeta_frame (gc_heap.c:557)
```

The fault is taken inside `gc_zeta_frame` (`src/runtime/rt/gc_heap.c:557`). Our own unconditional
SIGSEGV handler (`src/runtime/rt/rt_stack_overflow.c:31`, `sigaction(SIGSEGV,…)`) then classifies
it as a stack-guard-page fault and re-raises it. **m3 and m4 both do it**, so it is not a mode
artefact; `iconx` runs the same program under valgrind without complaint.

`valgrind` also reports **169,570 errors from 138 contexts** and 610 MB allocated for a program
whose visible data is a 40,000-character string and a small table. ⚠️ That count is reported as
measured and is **not** a claim of 169,570 bugs — a GC with tagged pointers and its own stacks
draws legitimate memcheck complaints. It is a number worth someone's attention, not a verdict.

## Why it mattered to the board, and the trap inside it

⛔ **callgrind still prints an `Ir` total for the crashed run.** That total is not marked, not
malformed and not obviously wrong — it is the same shape as every other cell on the board. And it
is **not even deterministic**: two runs gave 330,078,095 and 330,079,909, where the entire `Ir`
instrument rests on the property that a fixed argv and environment reproduce byte-identically
(measured 3/3 elsewhere on this board).

⭐ So the danger is not the crash, which is loud. It is that a **number survives the crash** and
would have published as a normal reading. The harness now voids it and prints `REFUSED(rc=139)`
with its reason, because "not measured" and "measured and thrown away" must never look the same.

⛔ **The first version of the harness printed a bare `NA` here and no warning at all**, because the
status was carried out of `ir_one` in a global that could not survive the command substitution
calling it. A crashed arm and an unmeasured arm were indistinguishable on the board for one run.

## What is and is not established

- ✅ Both modes fault under valgrind in `gc_zeta_frame`; reproduced repeatedly.
- ✅ Both modes are correct natively on this program; the board grades it PASS on the answer.
- ❓ **Unknown whether this is a latent bug that valgrind's stricter layout exposes, or an
  interaction with valgrind's own stack handling.** Deciding that is the cure's first step, not
  something this measurement settled. The `gc_zeta_frame` frame is the place to start; the
  `rt_stack_overflow` classification in the trace is our handler *reacting*, so it is a
  consequence and probably not the origin.
- ⛔ Do not read "runs clean natively" as "safe": the same fault under a different heap layout is
  what a native crash would look like, and `geddump` on the classic set already SIGSEGVs natively
  in both modes (hq_C's rank-0 row) — whether the two share a cause is **open and untested**.

## Reproduce

```bash
cd /home/claude_P/corpus/benchmarks/icon
/home/claude_P/SCRIP/scrip --compile --target=x86 bench_icnstr_concat_table.icn > ct.s
gcc -no-pie ct.s -L/home/claude_P/SCRIP/out -lscrip_rt -Wl,-rpath,/home/claude_P/SCRIP/out -lm -lpthread -o ct.bin
./ct.bin                                  # 40000, rc=0 -- clean
valgrind --tool=callgrind ./ct.bin        # SIGSEGV in gc_zeta_frame, rc=139
```

Board and machine record: `scripts/bench_icon_kernels.sh`,
`corpus/benchmarks/icon/bench_kernels_board.tsv` (row `bench_icnstr_concat_table`).
