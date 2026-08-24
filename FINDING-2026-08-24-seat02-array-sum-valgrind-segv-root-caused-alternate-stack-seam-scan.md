# FINDING 2026-08-24 (seat02) — array-sum-valgrind-segv: root-caused to a seam-scan bound mismatch, not stack exhaustion; witnessed, not cured

**Context:** `array-sum-valgrind-segv` STEP 1 (fresh claim, no prior sessions on this row). DONE-WHEN asks to name the faulting access to file:line, classify it, and either cure it or check it in RED with a witness. This FINDING is that witness — **no cure attempted, zero edits to any `.c`/`.h`/`.S`/`.cpp` source in SCRIP** (a diagnostic print was added to `gc_zeta_frame` mid-session to extract the evidence below, then reverted via `git checkout --`; `git status` is clean).

Trees: SCRIP `e1f5a4c2`, corpus `dfc75192`, `.github` `adba08b7` (main == origin/main, clean, at write time). Toolchain: `valgrind-3.22.0`, glibc 2.39 (Ubuntu GLIBC 2.39-0ubuntu8.8), `ulimit -s unlimited`, RT_OPT=-O0 per the s262 FACT RULE.

## Method

`bench_wrap.sh --mode=iter --n=8000` on `corpus/benchmarks/snobol4/array_sum.sno` (the brief's own pinned N). Built and ran BOTH modes:
- mode 4: `./scrip --compile array_sum_n8000.sno > p.s && gcc -c p.s -o p.o && gcc p.o -Lout -lscrip_rt -lm -Wl,-rpath,out -o array_sum_m4`
- mode 3: `./scrip --run array_sum_n8000.sno < /dev/null`

Both confirmed clean and correct **natively** first (`check: 250500` both modes, matching the array itself: `2+4+...+1000 = 250500`). Both then run under `valgrind --tool=memcheck --track-origins=yes` (STEP 1's own instrument — NOT callgrind) per the row's instruction to read the FIRST named error, not just the terminal SIGSEGV.

## Result — the crash chain (both modes, identical mechanism)

Mode 4, native: clean, `check: 250500`, rc=0. Under memcheck: **SIGSEGV**, rc=139. First class of warning:

```
Conditional jump or move depends on uninitialised value(s)
   at gc_zeta_frame (gc_heap.c:564..570)
   by gc_collect_ex (gc_heap.c:637)
   by rt_gc_point_arr_c (gc_heap.c:327)
   by rt_gc_point_arr (rt_asm_helpers.S:113)
   by rt_call_arr_bl (by_name_dispatch.c:4646)
 Uninitialised value was created by a stack allocation at rt_call_arr_impl (by_name_dispatch.c:4652)
```

This class is a **red herring, not the defect** — see "What this is NOT" below. The fatal one, same backtrace, moments later:

```
Invalid read of size 1
   at gc_zeta_frame (gc_heap.c:564)
   by gc_collect_ex (gc_heap.c:637)
   by rt_gc_point_arr_c (gc_heap.c:327)
   by rt_gc_point_arr (rt_asm_helpers.S:113)
   by rt_call_arr_bl (by_name_dispatch.c:4646)
 Address 0x1fff001000 is not stack'd, malloc'd or (recently) free'd
Process terminating with default action of signal 11 (SIGSEGV)
```

Exactly reproduces the crash chain and fault address `0x1FFF001000` independently found on a **second kernel** (`table_access`, generalization noted in `.github/FINDING-2026-08-24-seat02-ifunc-phantom-generalizes-plus-gc-crash-and-sbl-opacity.md`, this row's own prior LEDGER entry). Mode 3 (`./scrip --run`) hits the **identical** `gc_zeta_frame`/`gc_collect_ex`/`rt_gc_point_arr_c` chain (line numbers shifted by 4 — `gc_heap.c:568`/`641`/`329` — due to an unrelated diff between sessions, same functions) at a **different** fault address (`lo0=0x1ffebfb0e8` this run, vs `0x1ffefffd68` on mode 4) — confirming the mechanism, not a hardcoded address, varies with ASLR-ish placement but always lands in the same low neighborhood (~0x1ffe_xxxx_xxxx). Mode 3's own program output completes correctly first (`check: 250500` printed to stdout) — the crash there is in later cleanup/teardown, not mid-computation; mode 4's crash happens before any output is flushed. Both are the same defect at the same two lines; the brief's "both modes" claim is CONFIRMED, not just repeated.

## Root cause: `gc_zeta_frame`'s scan bounds belong to two different, unrelated stacks

`gc_collect_ex` (`gc_heap.c:637`): `if (pz && g_gc_seam_sp) { char *sst = gc_stack_top(); if (g_gc_seam_sp < sst) gc_zeta_frame(g_gc_seam_sp, sst); }`. `gc_zeta_frame(lo0, hi0)` (`gc_heap.c:559-573`) then walks `p` from `lo0` to `hi0` in 8-byte steps, reading each word as a candidate GC root (`gc_heap.c:564`'s `d->v` read is the one instrumented tools name — the very first byte of the 16-byte `DESCR_t` the loop reinterprets `p` as). The loop's own bounds check (`p+8<=hi`, `p+16<=hi`) is correct **if** `[lo0,hi0)` is one contiguous mapped region. It is not:

- `hi0` = `gc_stack_top()` (`gc_heap.c:531-536`) — lazily memoized **once, forever**, by parsing `/proc/self/maps` for the literal string `"[stack]"` (`gc_stack_region`, `gc_heap.c:524-529`). This always finds the **main thread's** kernel-assigned stack VMA. Confirmed correct in both runs: mode 4 `hi0=0x7ffeeee1a000`, mode 3 `hi0=0x7fff33a19000` — both matched an actual `[stack]` line size and shape (cross-checked separately: native and valgrind-synthesized `/proc/self/maps` both report ordinary ~0x7ffX `[stack]` VMAs of comparable size for a trivial process).
- `lo0` = `g_gc_seam_sp` = `floor`, a parameter computed by the ASM veneer `rt_gc_point_arr` (`rt_asm_helpers.S:100-122`) as `leaq 8(%rsp),%rcx` — i.e., **the CPU's real, current %rsp** at the moment this GC safepoint fires, not a stale or garbage value (confirmed by reading the veneer directly: six `pushq`s + `subq $8,%rsp` + `leaq 8(%rsp),%rcx`, a straightforward, correct computation relative to whatever stack is live at call time).

Instrumented `gc_zeta_frame` to print `lo0`/`hi0`/`tid` and dump `/proc/self/maps` on entry (temporary, reverted after collecting evidence). Result, mode 4: **this is the very first `gc_zeta_frame` call in the process's life** (count=1 before the crash). `/proc/self/maps` at that exact moment shows:

```
1ffeffd000-1fff001000 rwxp 00000000 00:00 0
...
7ffe0a353000-7ffe0a374000 rw-p 00000000 00:00 0                          [stack]
```

`lo0=0x1ffefffd68` falls **inside** the first (small, 16KB, anonymous, read+write+**execute**) region — nowhere near the second (main `[stack]`) region `hi0` points at. `0x1fff001000` — the exact fault address — is that small region's **upper bound**: the scan walks from a real, valid, current stack pointer straight off the end of a 16 KB mapping, then keeps going (per the loop's own logic, correctly, since it was told `hi0` was ~0x7ffe...) into unmapped space, and dies four bytes into the next page. **`floor` and `sst` are both individually correct values — they just don't describe the same stack.** Execution was running on some alternate, separately-allocated ~16KB executable stack when this GC safepoint fired, not on the main thread's stack; `gc_stack_top()` has no way to know that and always answers as if the main stack were the one in play.

**What this is NOT:**
- **Not stack exhaustion** — the brief's own STEP already falsified this (32x larger `--main-stacksize` crashed at the identical Ir count under callgrind). Consistent with the finding here: the bug is a bound-provenance mismatch, not a size limit, so a bigger stack changes nothing.
- **The "uninitialised value" warnings are very likely benign noise, not the defect** — `gc_zeta_frame` is a *conservative* scanner by design (see the comment at `gc_heap.c:365-366`: every span "is now scanned by `gc_zeta_frame`, which REGISTERS each pointer-holding location"); reading old, never-explicitly-initialized stack words and testing whether they *look like* a heap pointer is the intended behavior of a conservative root scan, and memcheck is expected to flag that. The ACTUAL defect is the subsequent genuinely-out-of-bounds 1-byte read, not the uninitialized-value reads that precede it in the same loop.
- **Not (as far as traced) the two known mmap'd-RWX pools in this codebase** — checked both by reading source and by size: `pat_pool.c`'s `g_pat_pool_base` is a single fixed **4 MiB** RWX region, allocated once via an `__attribute__((constructor))` (`pat_pool_ctor`) — wrong size (4 MiB vs the observed 16 KiB) to be this VMA, though it DOES explain why `PROT_EXEC` shows up at all in this binary's address space in general. `bb_pool.c`'s slab is allocated `PROT_READ|PROT_WRITE` and only `mprotect`'d to `PROT_READ|PROT_EXEC` (RX, never RWX at once) via `bb_seal`, and — more importantly — `bb_pool_init()` is only ever called explicitly from `src/driver/scrip.c`'s mode-3 in-process path, not from a constructor, so it's unclear it even runs for the mode-4 standalone binary at all (mode 4's `array_sum_m4` never executes `scrip.c`'s `main()`). **Not chased further**: the exact allocator/owner of the 16 KB region is still open — candidates not yet checked: a `pthread_create`-backed stack (16384 = `PTHREAD_STACK_MIN` on x86-64 Linux, a suspiciously exact match) or a `sigaltstack()` region sized for this host's AVX-512 signal-frame requirements (the crash's own signal-delivery backtrace shows `rt_stack_overflow_sig`, a custom SIGSEGV handler, confirming the codebase does install a handler that plausibly needs its own altstack — but the ZETA-DBG print fires *before* any signal is raised, on ordinary forward execution, so this is a plausible next lead, not a confirmed one).

## Why valgrind and not native

Not established with certainty this session, but the mechanism gives a plausible account without needing a special valgrind quirk: memcheck's per-allocation shadow-memory bookkeeping very plausibly changes exactly *when* `g_hp_top > g_hp_gcline` (`gc_heap.c:322`, the condition gating a real collect) goes true relative to program logic, versus native. If natively this exact GC safepoint (mid by-name array call, `rt_call_arr_bl`) never happens to be the one that trips a live collect — because native's smaller/different memory-growth curve pushes the first real collection to a safepoint reached while execution is back on the main stack — the seam-scan's bounds would agree and nothing would ever look wrong. This would mean the bug is real and load-bearing regardless of valgrind (any GC safepoint firing mid-alternate-stack, on any workload, any engine mode, hits it), valgrind is just what makes ITS TIMING land on the exposing case reliably. **Not proven this session** — would need instrumenting the native run the same way (temporarily) to see whether `gc_zeta_frame` runs with a similarly mismatched `lo0`/`hi0` pair even when it doesn't crash.

## Incidental, separate defect (not this row's, not chased): a real use-after-free in `scrip.c`'s mode-3 path

Mode 3's memcheck run additionally reported, **before** reaching the `gc_zeta_frame` crash:

```
Invalid read of size 4 at main (scrip.c:1719)
 Address 0x8feccd4 is 36 bytes inside a block of size 720 free'd
Invalid read of size 4 at main (scrip.c:1722)
 Address 0x8fece58 is 424 bytes inside a block of size 720 free'd
```

Both reads happen after the user program's own output is already correctly printed (`check: 250500` on stdout precedes both in the log), so this looks like a read of already-`free()`'d bookkeeping during `scrip --run`'s own teardown — a real bug, but a different mechanism (heap use-after-free in the compiler driver's own `main()`, not the GC seam-scan) and out of scope for this row. Not minted as a new row this session (time-boxed; flagging here so it isn't lost — whoever next touches `scrip.c`'s mode-3 exit path should check `git blame` on lines 1719/1722 first).

## Disposition

STEP 1's DONE-WHEN is satisfied via its "checked in RED with a witness" branch: the faulting access is named to `gc_heap.c:564` (read) / `gc_heap.c:637` (the call site supplying the mismatched bounds) / `rt_asm_helpers.S:112-113` (where the valid-but-wrong-stack `lo0` originates), classified as an **out-of-bounds read caused by a scan-bound provenance mismatch** (not uninitialized memory, not stack exhaustion, not alignment), and reproduced identically in both modes with full mechanism evidence (VMA dump, both bounds independently explained). **Not cured**: a correct fix needs either (a) identifying and registering the true bounds of whatever alternate stack is live at each GC safepoint (the way `gc_coexpr_roots`/`scrip_co_stack_of`, `gc_heap.c:538-552`, already does for known co-expression stacks — worth checking whether that registry could simply be consulted here too, or whether this is a third, unregistered stack kind), or (b) some other way to make `gc_zeta_frame`'s upper bound track "the stack currently in use" instead of unconditionally "the main thread's stack". Both risk being the kind of GC-correctness change this codebase has explicit precedent for getting subtly wrong under time pressure (see `perf-core-tag-predicate-o0-call-tax`'s citation of the s264 `always_inline` revert) — left for a session that can budget the time to trace the alternate-stack owner definitively first, per this row's own DONE-WHEN allowing a witnessed-not-cured close.

No cure attempted anywhere. Zero edits to any `.c`/`.h`/`.S`/`.cpp` source in SCRIP (diagnostic instrumentation added and reverted; `git status` clean at write time).
