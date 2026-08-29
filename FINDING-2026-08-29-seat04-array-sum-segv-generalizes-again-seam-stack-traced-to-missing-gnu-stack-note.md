# FINDING 2026-08-29 (seat04) — `array-sum-valgrind-segv` still live on a third kernel/N; sigaltstack hypothesis ruled out; the mystery executable seam-stack traced to a missing `.note.GNU-stack`

**Context:** side-discovery while working `perf-match-begin-beta-cure`'s GC+alloc attribution thread (attempting to attribute `rt_gcheap_carve`/`c_rt_gcheap_alloc` via callgrind on `table_access.sno --n=15000`). That row's own task file already records hitting this SIGSEGV and recommends it become its own row — **it does not need one: it is `array-sum-valgrind-segv`, already open (rank 2, unassigned, FREE), already root-caused by seat02 on 2026-08-24** (`.github/FINDING-2026-08-24-seat02-array-sum-valgrind-segv-root-caused-alternate-stack-seam-scan.md`) and already known to generalize to `table_access` at N=20000 (`.github/FINDING-2026-08-24-seat02-ifunc-phantom-generalizes-plus-gc-crash-and-sbl-opacity.md`). This FINDING is a fresh, independent re-reproduction (a third kernel/N combination) plus two new, source-and-readelf-confirmed facts toward that row's own STEP 2 ("identify the alternate-stack owner definitively"). **No cure attempted. Zero edits to any `.c`/`.h`/`.S`/`.cpp` source in SCRIP** — read-only investigation plus one disposable scratch `.sno`/log pair, neither committed.

Trees: SCRIP `2bae6ff5`, corpus `8938ce076`, `.github` `96fc614a` (all clean at write time). Toolchain: `valgrind-3.22.0`. Build: existing `./scrip` binary (`RT_OPT=-O0`, the pinned default — not rebuilt this session).

## 1. Fresh, independent reproduction — `table_access` at N=15000 (neither prior witness's N)

`bash scripts/bench_wrap.sh corpus/benchmarks/snobol4/table_access.sno -o <scratch>.sno --mode=iter --n=15000` (fixed_n=15000 confirmed baked in). Native, twice: clean both times, `check: 250500` / `iters: 15000` identical both runs (only wall-clock jitter differs). Under `valgrind --tool=memcheck`:

```
$ valgrind --tool=memcheck ./scrip <scratch>.sno < /dev/null
...
==467279== ERROR SUMMARY: 10000000 errors from 36 contexts (suppressed: 0 from 0)
$ echo $?
139
```

SIGSEGV, deterministic, exit 139 — a third kernel/N combination confirming the defect array-sum-valgrind-segv tracks is **still live, unfixed, 5 days after root-cause.**

## 2. Same defect, not a new one — the terminating backtrace lands in `gc_zeta_frame` via SCRIP's own stack-overflow handler

The warning volume (10,000,000-error cap hit) is concentrated exactly where seat02's array_sum/table_access witnesses put it — `table_set_descr_d`/`_tbl_lower`/`_tbl_grow` (`aggregates.c:341,356,432-436`), `memmove` called from inside them, and `table_find_pair_d` (`rtx_table.s:274-328`), all under `c_rt_table_assign_fast` (`pattern_match.c:1532`). Per seat02's own root-cause, these are the *conservative scanner's expected noise*, not the defect. The actual process-terminating trace, captured for the first time with this level of detail in this thread:

```
==467279== Process terminating with default action of signal 11 (SIGSEGV)
==467279==    at 0x8656C0C: __pthread_kill_implementation (pthread_kill.c:44)
==467279==    by 0x8656C0C: __pthread_kill_internal (pthread_kill.c:78)
==467279==    by 0x8656C0C: pthread_kill@@GLIBC_2.34 (pthread_kill.c:89)
==467279==    by 0x85FD27D: raise (raise.c:26)
==467279==    by 0x48CD332: rt_stack_overflow_sig (rt_stack_overflow.c:21)
==467279==    by 0x85FD32F: ??? (in /usr/lib/x86_64-linux-gnu/libc.so.6)
==467279==    by 0x48C7ADC: gc_zeta_frame (gc_heap.c:591)
```

Read against `rt_stack_overflow_sig`'s actual source (`src/runtime/rt/rt_stack_overflow.c:10-22`, installed unconditionally on a `sigaltstack` via an `__attribute__((constructor))`): the handler computes the CURRENT THREAD's real OS stack bounds via `pthread_getattr_np`/`pthread_attr_getstack`, and only prints its own "ERROR 246 — stack overflow" diagnostic and `_exit(1)`s cleanly if the fault address is within 16MB of that thread's own low stack bound *and* RSP is in range (`rt_stack_overflow.c:16-19`). **Any other SIGSEGV falls through to `signal(sig,SIG_DFL); raise(sig)` — line 21, exactly the frame in the trace above.** So this backtrace is not a raw, unhandled crash: SCRIP's own handler caught the original fault (inside `gc_zeta_frame`, consistent with seat02's exact crash site `gc_heap.c:564`, now `:591` after intervening line drift), correctly determined it does **not** match an ordinary same-thread call-stack overflow, and deliberately let it fall through to a real crash rather than mislabel it — which is exactly what you'd expect if the true fault is `gc_zeta_frame` walking off the end of some *other*, smaller memory region (seat02's finding) rather than exhausting the calling thread's actual stack. This is confirmation of seat02's mechanism from a different angle, not a competing one. (The individual "Invalid read ... not within mapped region" line for this specific run's fatal access was not captured — valgrind's own 10,000,000-error cap was hit one line earlier in the log, which suppresses further individual error reports but not the final termination report.)

Also re-confirmed, unchanged: the separate, unrelated `scrip.c` IR-teardown invalid-read (now at `scrip.c:1868`/`:1871`, reading into a block freed via `IR_free`←`bb_program_free`←`ir_delete_all` at `scrip.c:1864`, block allocated by `sno_build_graph`/`lower_sno_stage2`/`sm_preamble` at `scrip.c:1730`) — same defect seat02 already flagged as incidental and separate on 2026-08-24 (then at `scrip.c:1719`/`:1722`; line numbers drift, mechanism doesn't). And the `rt_outer_call` (`core.h:53`) invalid-write-of-size-8, immediately preceded in this run's log by valgrind's own `Warning: client switching stacks? SP change: 0x1ffeffb3a0 --> 0x1ffebfb398` — direct, in-log evidence (not just plausibility) for the existing "valgrind stack-tracking artifact from SCRIP's own custom stack switching" reading; still not chased further, still not this thread's concern.

## 3. New: the sigaltstack hypothesis for the mystery ~16KB executable region is RULED OUT

`array-sum-valgrind-segv.task.md`'s STEP 2 named two candidate owners for the ~16KB `rwxp` VMA seat02 found `lo0` inside: a `pthread_create` stack (16384 = `PTHREAD_STACK_MIN`, "a suspiciously exact match") or a `sigaltstack` sized for this host's AVX-512 signal frames. Reading `rt_stack_overflow.c:26-29` (the only `sigaltstack` call anywhere in this handler, and the handler this whole crash chain runs through): `malloc(65536)`, `ss.ss_size = 65536`. **65536 (64KB) ≠ 16384 (16KB)** — the sizes don't match, and ordinary `malloc`'d heap memory isn't intrinsically executable on this toolchain regardless of size. This rules out `rt_stack_overflow_sig`'s own altstack as the mystery region, leaving the `pthread_create`-stack candidate as the sole surviving one of the two originally named (not yet *confirmed* — see §5).

## 4. New: the RWX-ness is now mechanistically explained, confirmed via `readelf`

Independently, `rtx_table.o`'s missing `.note.GNU-stack` was already on record in `perf-match-begin-beta-cure.task.md`'s own LEDGER (dismissed there as "a pre-existing unrelated linker warning") — it is not unrelated:

```
$ readelf -S SCRIP/out/rt_pic-f65f143e2f/rtx_table.o | grep -i "note.gnu-stack"
(no output — the section is absent)

$ readelf -lW SCRIP/out/libscrip_rt.so | grep GNU_STACK
  GNU_STACK      0x000000 0x0000000000000000 0x0000000000000000 0x000000 0x000000 RWE 0x10

$ readelf -lW SCRIP/scrip | grep GNU_STACK
  GNU_STACK      0x000000 0x0000000000000000 0x0000000000000000 0x000000 0x000000 RW  0x10
```

`rtx_table.o` genuinely lacks a `.note.GNU-stack` section, and the shared runtime library it links into, `libscrip_rt.so`, has a resulting `GNU_STACK` program header of **RWE** (the linker's standard conservative behavior when any input object doesn't declare its stack requirements) — while the main `scrip` driver binary's own `GNU_STACK` is plain `RW`. **This is a well-known, standard glibc/NPTL mechanism** (not independently re-verified against this exact glibc's source this session, flagged as the one remaining inferential step) **by which a process that loads a shared object with an executable-stack requirement can end up creating new `pthread_create` stacks with `PROT_EXEC` too**, to stay consistent with the loaded object's declared needs. This is a plausible, concrete, and now source-grounded explanation for why seat02's mystery 16KB region showed up `rwxp` — a property that was otherwise unexplained for either of the two original candidates (a plain `pthread_create` stack is ordinarily `rw-p`, not `rwxp`).

## 5. What is still NOT established — the actual next step for `array-sum-valgrind-segv`'s STEP 2

**Not confirmed:** that the specific crashing 16KB VMA is in fact a `pthread_create`-allocated worker-thread stack (as opposed to some other allocation that also inherited the process's executable-stack attribute). The RWE finding above narrows *why an executable small region would exist at all* and rules out one of two named candidates for it — it does not, by itself, prove which allocation *is* the one `gc_zeta_frame` walked off the end of. The fastest confirming check for whoever picks this up: reproduce with the existing (reverted) `gc_zeta_frame` diagnostic instrument seat02 used, and additionally dump `/proc/self/maps` alongside a listing of live thread stacks (e.g. `pthread_getattr_np` on each live thread, or watch `pthread_create`/`clone` via strace) at the moment of the first `gc_zeta_frame` call, to directly match the crashing VMA's address range to a specific thread's stack. Separately, fixing the missing `.note.GNU-stack` on `rtx_table.o` (a one-line assembly addition, `.section .note.GNU-stack,"",@progbits`, or an equivalent link-time `-z noexecstack`) is a small, low-risk, independently-justifiable hygiene fix regardless of whether it turns out to be load-bearing for this crash — it would remove the executable-stack requirement this library currently imposes on the whole process, which is worth doing on general security-hygiene grounds alone, but **does not by itself fix `gc_zeta_frame`'s actual bound-provenance bug** (per seat02's finding, `hi0`/`lo0` describing two different regions is the real defect; removing stack executability would only make the resulting bad read non-executable-but-still-invalid, not stop it happening) — recorded as a candidate low-risk follow-up, not proposed as the cure for the main defect.

**Disposition:** `array-sum-valgrind-segv`'s own STEP 2 remains open and unclaimed (QUEUE.tsv: rank 2, `unassigned`, `FREE`, confirmed live at write time) — this FINDING narrows one of its two named candidates and explains a previously-unexplained property of the other, and is routed there via that task file's own LEDGER (append, not a claim — this session's actual claimed row is `perf-match-begin-beta-cure`, unrelated). No cure attempted anywhere this session.
