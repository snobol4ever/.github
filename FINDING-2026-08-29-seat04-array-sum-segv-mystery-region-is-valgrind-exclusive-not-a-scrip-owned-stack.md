# FINDING 2026-08-29 (seat04) — the mystery RWX region is absent from the native process entirely; both of STEP 2's named candidates are dead; leading hypothesis changes from "an unregistered SCRIP stack" to "a valgrind-internal artifact"

**Context:** `array-sum-valgrind-segv`, STEP 2 (identify the alternate-stack region's owner). Continues directly from
seat02's 2026-08-24 root-cause and this seat's own 2026-08-29 earlier-today narrowing (which traced the region's
RWX-ness to `rtx_table.o` missing `.note.GNU-stack`, and ruled out `sigaltstack` as a candidate by size). **No cure
attempted. One temporary diagnostic added and fully reverted (`git checkout --`) before this FINDING was written;
tree confirmed clean (`git status --short` empty) both before writing and after rebuilding.**

## Both of STEP 2's own named candidates are now dead, not just narrowed

The task file named two candidates for the mystery region: a `pthread_create` stack, and `sigaltstack`.
`sigaltstack` was already ruled out earlier today (`rt_stack_overflow_sig`'s altstack is `malloc(65536)` = 64KB).
This pass:

- **Grepped every `sigaltstack` call in the entire `src/` tree** (not just the one already checked): there is
  exactly one other, `bbprof.c:73` — its altstack is `static char g_altstack[65536]`, **also 64KB**, and it's
  gated behind `SCRIP_BBPROF`/`bbprof_on()`, off by default. Neither `sigaltstack` call site in the whole codebase
  is anywhere near 16KB. This candidate is now exhaustively dead, not just the one instance already checked.
- **Read `rt_coexpr.c`'s `pthread_create` call (the only one in the entire codebase, `rt_coexpr.c:70`,
  used solely for coexpression creation) end to end.** Its stack is explicitly sized via
  `pthread_attr_setstack(&attribs, lo, sz)` where `sz` derives from `g_coexp_stksize`, **default 8MB**
  (`rt_coexpr.c:18`, overridable only via `SCRIP_COEXP_STACK`, not set here). `array_sum`/`table_access` never
  create a coexpression in the first place (no `&`/`CREATE` in either program), so this call site never even
  fires for these witnesses — but even if it did, the resulting stack is explicitly 8MB, never near 16KB. This
  candidate is dead independent of whether coexpressions are used at all.
- **Grepped every `PROT_EXEC` mapping in the entire `src/` tree**: only two exist — `bb_pool.c:45`
  (`PROT_READ|PROT_EXEC`, mode-3-only, already ruled out by seat02) and `pat_pool.c:13` (`PROT_READ|PROT_WRITE|
  PROT_EXEC`, `PAT_POOL_SIZE` = 4MB, already ruled out by seat02). **There is no other executable-memory-allocation
  mechanism anywhere in SCRIP's own source.** Whatever creates the mystery region, it is not an intentional SCRIP
  allocation of any kind — every candidate the codebase itself could produce has now been checked.

## Direct empirical test: does the region exist natively at all?

Added the same kind of temporary, env-gated diagnostic seat02 already used successfully on this exact row (a
one-time `/proc/self/maps` dump plus `lo`/`hi`/thread-identity print, gated behind a new `SCRIP_SEAM_DUMP` env
check, inserted at `gc_heap.c`'s actual crash-triggering call site — `gc_collect_ex`'s `if (cons_stack) { ...
gc_zeta_frame(lo, hi); }` line, the one that produces the `lo=g_gc_seam_sp`/`hi=gc_stack_top()` pairing the
root-cause names). Built the row's own pinned witness (`array_sum`, `bench_wrap.sh --mode=iter --n=8000`, mode-4
standalone binary, this row and the perf rows' shared established recipe) and ran it two ways with the identical
binary and identical diagnostic armed:

**Native** (`SCRIP_SEAM_DUMP=1 ./bin`, exit 0, `check: 250500` correct):
```
[SEAM-DUMP 0] lo=0x7ffc94259ff8 hi=0x7ffc9426b000 (chi=(nil) stacktop=0x7ffc9426b000) ismain=-1 self=133810731513664
```
`lo` and `hi` are both ordinary, close-together addresses inside the real stack. The full native `/proc/self/maps`
dump captured at this exact point contains **no mapping anywhere in the `0x1ffe.../0x1fff...` range at all** — not
narrowly missed, genuinely absent from the whole 54-line map.

**Under valgrind** (`SCRIP_SEAM_DUMP=1 valgrind --tool=memcheck ./bin`, crashes identically to every prior
reproduction — `check: 250500` never prints, exit via SIGSEGV, same fault address `0x1fff001000` seat02 and this
seat's earlier `table_access` witnesses already documented):
```
[SEAM-DUMP 0] lo=0x1ffefefe08 hi=0x7ffe53899000 (chi=(nil) stacktop=0x7ffe53899000) ismain=-1 self=146335552
```
— on the **first occurrence of this code path**, before anything crashes. The maps dump captured at this same
point shows:
```
1ffefed000-1fff001000 rwxp 00000000 00:00 0
...
7ffe53878000-7ffe53899000 rw-p 00000000 00:00 0                          [stack]
```

Three things this settles directly, verified with a calculator rather than by-hand hex arithmetic:

1. **`hi` is correct in both runs.** `hi=0x7ffe53899000` is not just "a plausible stack-shaped address" — it is
   the *exact* upper bound of the real `[stack]` mapping valgrind itself reports. `gc_stack_top()` is not the bug.
2. **`lo` is the one reading a foreign value, and only under valgrind.** `0x1ffefefe08` sits squarely inside the
   `1ffefed000-1fff001000` mapping (11,784 bytes in from its start), and the scan's fault address (`0x1fff001000`)
   is *exactly* that mapping's upper bound — the scan walks from a real address in this region toward `hi` and
   dies the instant it steps one byte past this region's own end, before ever getting anywhere near the real stack.
3. **The region itself does not exist in the native process.** Not "native doesn't reach it" — native's own
   `/proc/self/maps`, read at the equivalent point in execution, has no mapping in this address range at all.

## This changes the shape of what STEP 2 is even looking for

The task file's framing — "identify the alternate-stack owner... likely either registering that stack's true
bounds somewhere `gc_collect_ex` can consult, or extending the existing co-expression-stack registry" — assumes
there **is** a legitimate second SCRIP-owned stack somewhere that just isn't registered yet. Every mechanism that
could produce such a stack has now been checked and is either the wrong size or provably not invoked by these
witnesses. Combined with the region's total absence from the native address space, the more consistent
explanation is that **this 16-80KB region (see discrepancy below) is not a SCRIP-owned stack at all — it is
something valgrind's own instrumentation places into the guest's address space**, and the raw `mov %rsp, ...`
read inside SCRIP's hand-written ASM veneer (`rt_gc_point_arr`, the thing that produces `g_gc_seam_sp`) is, under
valgrind specifically, observing that region's address rather than the guest program's true stack pointer. **Not
confirmed as to mechanism** — this would need either reading Valgrind's own source for how it handles raw
register-capture instructions in translated code, or a diagnostic capability (e.g. Valgrind's own
`--sim-hints`/core-instrumentation internals) this sandbox wasn't used to check. Recorded as the leading
hypothesis, not a diagnosis.

## An honest discrepancy, not silently reconciled: region size measured at 80KB here, 16KB in the original finding

Seat02's original finding (same witness, `array_sum` N=8000, same `--tool=memcheck`) measured the region at
16KB and flagged it as "suspicious" for exactly matching `PTHREAD_STACK_MIN`. This pass's own direct measurement
of the identical mapping (`1ffefed000` to `1fff001000`, verified with `python3`, not hand arithmetic) is
**81,920 bytes = 80KB — five times larger**, not 16KB. The one procedural difference found: seat02's own LEDGER
entry specifies `valgrind --tool=memcheck --track-origins=yes`; this pass used bare `--tool=memcheck` (no
`--track-origins`). **Not confirmed, but the most obvious candidate explanation**: `--track-origins=yes` adds
substantial extra memcheck-internal bookkeeping, which could plausibly change the size of whatever internal
buffer this is, if it's sized in proportion to enabled instrumentation. **Concrete, cheap next check for whoever
continues:** re-run this exact same diagnostic with `--track-origins=yes` added and see whether the region
reports back at 16KB — a single valgrind invocation, no new instrumentation needed, the `SCRIP_SEAM_DUMP` env var
and patch shape are fully described above for whoever wants to re-apply them (temporarily, same as both prior
passes on this row).

## Disposition

**Established:** both STEP 2 candidates are dead (not narrowed — exhaustively checked against every matching
mechanism in the codebase); the region is absent from the native address space entirely; `hi`/`gc_stack_top()`
is correct in both runs, `lo`/`g_gc_seam_sp` is the value that goes wrong, only under valgrind, from the very
first occurrence. **New leading hypothesis, not confirmed:** a valgrind-internal artifact, not an unregistered
SCRIP stack — which would mean STEP 2's original "register the stack's bounds" cure shape is aimed at the wrong
target. **Open, flagged not chased:** the exact region-size discrepancy (16KB vs. 80KB) between this pass and
seat02's, with a concrete, cheap next check named above. **Not started, deliberately:** any cure. If the
valgrind-artifact hypothesis holds up, the real fix direction is likely making the `%rsp` capture (or the scan
that trusts it) robust to this specific value being untrustworthy under instrumentation, rather than registering
a stack that may not actually exist as a distinct SCRIP-owned entity — but that is a design decision for this
row's own `## NEXT`/a ceo ruling, not something to rush per this row's own standing caution about GC-correctness
changes.
