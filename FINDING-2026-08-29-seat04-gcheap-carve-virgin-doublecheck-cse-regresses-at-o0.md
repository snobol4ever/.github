# FINDING 2026-08-29 (seat04) — the double `at >= g_hp_virgin` check in `rt_gcheap_carve` looks like free CSE but REGRESSES at this project's pinned -O0

**Context:** `perf-match-begin-beta-cure`, direct follow-up to today's
`FINDING-2026-08-29-seat04-gcheap-dynamic-per-call-cost-113-not-406-instructions.md`, which established
`rt_gcheap_carve`'s not-fresh path (69 instructions) as one of the two components of the GC-heap slow path's
113-instruction/call cost, and left open whether that 69-instruction path is itself compressible. This checks
one specific candidate inside it — NOT the memset-compression question that FINDING flagged (that still needs
design-level care) — and finds it does not pan out. **No cure landed; zero source changes remain in the tree.**

## Hypothesis: `at >= g_hp_virgin` is evaluated twice in source, and this project builds at pinned -O0 (no CSE)

`gc_heap.c:136-137` (pre-fix line numbers):
```c
int fresh = !zfull && at >= g_hp_virgin;
if (at >= g_hp_virgin && at + total > g_hp_virgin) g_hp_virgin = at + total;
```
Confirmed via `objdump -dSl` against the live `.so`: this compiles to the exact same 3-instruction `mov`/`mov`/
`cmp` sequence (two GOT-style indirections to reach `g_hp_virgin`, then a compare against `at`) twice, byte-for-
byte identical apart from the `(%rip)` displacement and the branch target. Since `RT_OPT` is pinned at `-O0`
(RULES.md § NO -O2 BUILDS) and is never getting lifted, the compiler will never CSE this on its own — a
source-level fix looked like the only way to remove it. Applied the obvious one: hoist the comparison into a
local, `int past_virgin = at >= g_hp_virgin;`, reused at both sites.

## Measurement: paired mode-4 + real-`perf` on `table_access` N=15000, this row's own established anti-contention methodology

Built two isolated `.so` copies (stable, non-clobberable paths — not the mutable `out/libscrip_rt.so` symlink,
the exact clobber bug this row already found and fixed for the `NV_SET_fn` measurement) from the same tree,
differing only in this one hoist. Linked each against the SAME compiled `.s` (`--compile` on `bench_wrap.sh`'s
`table_access --mode=iter --n=15000` output — the emitted code is compiler/emitter output, provably identical
either way since this change touches only the runtime library, not codegen). Correctness: both binaries print
`check: 250500` (matches this row's own previously-recorded value for this exact workload), byte-identical.

`perf` binary: `/usr/lib/linux-tools-6.8.0-138/perf` (this row's own established kernel-version-mismatch-but-
works finding). System under heavy load at measurement time (`load1=19.29`, 16 cores, 5 concurrent `scrip`
processes from other seats) — exactly the FLEET-16 contention regime this row already found corrupts
`perf stat -r N` aggregates — so 5 **individual**, interleaved invocations of `perf stat -e instructions:u` per
side, not `-r N`:

```
trial   baseline        fixed           delta (baseline-fixed)
1       5,788,596,658   5,791,412,467   -2,815,809
2       5,788,570,162   5,791,429,578   -2,859,416
3       5,788,580,548   5,791,395,398   -2,814,850
4       5,788,580,986   5,791,411,400   -2,830,414
5       5,788,564,894   5,791,411,815   -2,846,921
```
Tight spread on both sides (<0.0006% each) — a real, reproducible, deterministic difference, not noise.
**The sign is the opposite of the prediction: "fixed" costs ~2.83M MORE instructions**, not fewer (avg delta
-2,833,482, ≈0.049% of the ~5.79B-instruction total; ≈0.6 more instructions per allocation call across this
workload's 4,731,308 total allocations — count from the `gcheap-slow-path-is-30-percent` FINDING).

Confirmed statically too, independent of any sampling concern: `objdump -d` on the two isolated `.so` files,
counting real instruction lines in `rt_gcheap_carve`'s body: **baseline 111, fixed 113** — a plain +2
instruction regression, no branch-resolution ambiguity needed to see it.

## Why: at -O0, a named local is not free — it costs a stack round-trip a duplicated comparison doesn't

A normalized instruction diff (mnemonics only, addresses stripped) shows exactly what changed: baseline
evaluates `at >= g_hp_virgin` twice, materializing it into `fresh` with a branchy `jb`/`mov $1`/`jmp`/`mov $0`
sequence the first time, then re-evaluating it inline (2 loads + `cmp` + a direct `jb`, no materialization
needed) for the `if`. The fix instead computes it **once** — but gcc at `-O0` gives every local its own stack
slot, so "reuse" means: `setae`+`movzbl` to materialize `past_virgin` (cheaper than baseline's branchy version,
by itself a small win) plus a **store** to its slot, then a **reload** for the `fresh` use and a **second
reload** for the `if` use. The extra store and two reloads cost more than the second comparison they replace,
because the "redundant" comparison being removed was already cheap: a compare feeding a conditional jump
directly, not a value that needed to survive a statement boundary — there was no register pressure or expensive
recomputation being amortized. **Same lesson as `rt_anchor_g` (measured 0.00%) and the earlier `NV_SET_fn`
unpaired-sampling artifact already on record in this row**: a plausible, "obviously correct" cut that -O0's
lack of cross-statement register allocation defeats — or in this case, inverts.

## Disposition

**Reverted, not committed** — `git checkout -- src/runtime/rt/gc_heap.c` before writing this up; the tree
carries zero source changes from this exploration. **Established:** the double comparison is real, but a
source-level named-local CSE makes it worse, not better, at this project's pinned -O0; do not re-derive this
exact fix. **Not examined:** whether some other restructuring (e.g. reordering so the `if`'s own branch
computes `fresh` as a side effect, avoiding a second named local entirely) could do better — genuinely
unstarted, and marginal at best given the whole effect sits under 0.05% of the program either way, likely not
worth the design attention relative to the two bigger items already on record (the GC index/fwd redesign, or
the still-unexamined `rt_gcheap_carve` memset-compression question). **This closes seat04's own candidate
search for a free ceremony cut in the GC-heap slow path** — none found; the remaining levers in this thread are
the ones already on record (design sign-off for the compacting-GC redesign, or memset compression for the two
uniform aggregate types), not more of this kind of look.
