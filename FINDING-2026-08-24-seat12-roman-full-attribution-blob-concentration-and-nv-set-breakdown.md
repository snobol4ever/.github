# FINDING 2026-08-24 — seat12 — `perf-string-runtime` STEP 7: `roman.sno`'s first full source-line attribution — the opaque blob concentrates 31% of the kernel in one bucket, `NV_SET_fn` gets its first `-O0` breakdown, one new call-tax row minted

## Scope and comparability

STEP 6's own closing note (seat04): *"No further open thread identified on THIS row from this pass — whoever continues should re-survey the kernel (or pick a fresh one, e.g. `table_access`/`roman` for the same class of check) rather than assume one is already queued."* STEP 4 (seat02) touched `roman.sno` only at the **symbol level** (confirmed 4 glibc-multiarch citations phantom via gdb, 5.93% of kernel). Nobody has done the STEP-3/STEP-6-style **source-line** self-cost breakdown on `roman.sno` yet. This pass does that. `table_access.sno` was considered instead but is out — it reproduces the known `array-sum-valgrind-segv` SIGSEGV-under-valgrind bug (STEP 4's own finding), so a clean full-kernel callgrind profile isn't obtainable there without that row's own fix landing first.

- Trees: SCRIP `be376a2f`, corpus `c294d7c1`, RT_OPT=`-O0` (built fresh, `make`, confirmed `-O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer` on every compile line, no `-O2` anywhere per the s262/s266 FACT RULE).
- **Not byte-identical-comparable to STEP 4's tree** (SCRIP `1a9cc1bc`) — unlike most prior LEDGER entries' "empty diff" checks, `git log 1a9cc1bc..HEAD -- src/runtime/by_name_dispatch.c src/runtime/core src/contracts/core.h src/runtime/rt src/runtime/builtins` returns **4 commits**, two of which are real by-name-dispatch changes: `5d6f8a71` ("by-name dispatch: skip the redundant memcmp on the array-cache path — `bid_of()` already proves identity") and `2d8d6df7` ("by-name dispatch — SNO$NOFAIL guard was checking only fn[0], paying a full strcmp for every ordinary 'S'-leading builtin"). This matters for §D below — stated up front rather than silently treated as noise.
- Build/measure recipe matches STEP 4's exactly for apples-to-apples: `bench_wrap.sh ../corpus/benchmarks/snobol4/roman.sno --mode=iter --n=20000` (output redirected under `/home/claude12/SCRIP/.profile-scratch-seat12/`, never bare `/tmp`, per standing scratch-discipline), `scrip --compile --target=x86 f.sno > f.s && as f.s -o f.o && gcc -no-pie f.o -Lout -lscrip_rt -Wl,-rpath,out -Wl,--allow-shlib-undefined -lm -o f.bin`.
- **Native run confirms `check: 1102`** — exact match to STEP 4's citation. Tree is verified functionally comparable before anything downstream is trusted.
- `callgrind --smc-check=all-non-file`: **TOTAL_Ir = 372,773,092** vs STEP 4's `376,704,822` (−1.04%). `BLOB_Ir = 172,564,221` (46.30%) vs STEP 4's `174,803,903` (46.40%) — both deltas are small and in the direction the two intervening dispatch fixes would predict, but **not proven causal** here (no before/after rebuild at the old commit was done this pass — flagged, not asserted).

## A. The opaque-blob mechanism doesn't just fragment attribution — on this kernel it collapses 31% of the WHOLE program into ONE bucket

`callgrind_annotate`'s flat top line for `roman_n20000.bin` is not a small residual, it's the single largest citation in the entire profile:

```
116,740,214 (31.32%)  ???:0x00000000004012c6 [.../roman_n20000.bin]
```

`readelf -sW roman_n20000.bin | grep 4012c6` resolves this address to `main` itself:
```
509: 00000000004012c6     0 NOTYPE  GLOBAL DEFAULT   14 main
```
Size **0**, type **NOTYPE** — the identical mechanism `callgrind-opaque-bb-labels` already pinned for `string_manip.sno` (compiler-emitted BB-port labels carry no `.type`/`.size`), but here confirmed on `main` itself, not just the `nN_*_α/β` labels downstream of it. `readelf -sW roman_n20000.bin | grep ' FUNC ' | grep -v UND` returns **zero rows** — there is not one FUNC-typed symbol anywhere in the compiled program's own code (spot-checked `main`, several `nN_*` labels, `ROMAN_*`: all NOTYPE, size 0, confirming the existing finding's "every one of the compiler's own emitted BB-port labels" claim generalizes to the entry point too). `objdump -d --start-address=0x4012c0 --stop-address=0x401300` confirms `main`'s real disassembly starts exactly there (`sub $0x8,%rsp; push %rdi; push %rsi; call core_lib_init@plt; ...`) — a real function, correctly entered, just unresolvable downstream once execution flows (via the flat-wired Byrd-box jumps — "the wiring *is* the execution, no runtime dispatch") into the unbounded run of subsequent NOTYPE labels with no symbol boundary for `callgrind_annotate` to re-anchor on. Once attribution fails at one address it does not get its own new mis-bucket — it silently accretes onto the last resolvable symbol, which for a mostly-single-flow, loop/recursion-dominated kernel like `roman` (the `ROMAN_RUN` loop plus recursive `ROMAN` calls, all flat-wired from `main`) is enough to pull nearly a third of the ENTIRE kernel into one line. This is a genuinely new, striking data point for that row (STEP 2's own biggest single unattributed line on `string_manip` was 9.37%/4.79M Ir — under a third the concentration seen here) — **fed to `callgrind-opaque-bb-labels`**, not a new mechanism.

## B. `NV_SET_fn`'s first `-O0` source-line breakdown — and the in-source justification for its memoization cache is measuring a retired regime

`NV_SET_fn` is the largest **real** (non-phantom, non-blob) symbol-level cost anywhere in `roman`'s profile — bigger than `bn_replace` itself:

```
 46,453,125 (12.46%)  src/runtime/core/core.c:NV_SET_fn
  4,039,288 ( 1.08%)  src/runtime/core/../rt/rt_protected.h:NV_SET_fn   (inlined is_protected_pat_lead body, separately DWARF-keyed — same split-attribution shape STEP 6 documented for bn_size/descr.h)
```

Source-line `callgrind_annotate` on `core.c` (STEP-3/6 technique, first time applied to this function):

| line | code | self-cost Ir | % of kernel |
|---|---|---:|---:|
| 2332 | function prologue | 5,508,225 | 1.48% |
| 2333 | `SCRIP_EXPR_STORE_DBG` debug guard (lazy-init static + short-circuit) | 2,203,298 | 0.59% |
| 2334 | `if (!_var_init_done) _var_init();` | 1,101,646 | 0.30% |
| 2335 | `rt_sxt_break(val.s)` call site (string stores only) | 2,570,481 | 0.69% |
| 2336 | `g_protected_pat_vars_armed && ...` guard | 4,406,524 | 1.18% |
| 2340 | `if (!name) return val;` | 734,430 | 0.20% |
| 2341 | **fast path**: `_var_find_cached` (memoized, `always_inline`) hit → store → return | 13,403,067 | 3.60% |
| 2343–2391 | slow path (io-chan/OUTPUT/TERMINAL/`&subject`/`&pos`/keyword-context/hash-bucket-walk/allocate) | ≈981 | ~0.0003% |
| 2403 | epilogue | 2,203,290 | 0.59% |
| | **sum of visible lines** | **32,131,942** | **8.63%** |

Two things this table shows cleanly: **(1)** the slow path (lines 2343–2391 — I/O-channel dispatch, `OUTPUT`/`TERMINAL` special names, the linear hash-bucket walk, and the block that allocates a brand-new `NV_t` for a never-before-seen name) costs essentially nothing on this kernel — confirms the fast-path memo cache (landed s258) is hitting on very close to 100% of `roman`'s stores, exactly as designed. **(2)** the fast path itself (line 2341, 3.60%) is still the single biggest line — this is the memoized/inlined cost *after* the s258 cure, not before it.

⚠️ **Accounting gap, reported honestly rather than papered over**: the visible per-line sum above (32,131,942) is **14,321,183 Ir (3.85% of kernel) short** of the flat `core.c:NV_SET_fn` total (46,453,125), even after adding the separately-keyed `rt_protected.h:NV_SET_fn` bucket (4,039,288) on top. `grep -i NV_SET_fn` against the FULL (`--threshold=100`, unrounded) flat profile finds no third file-keyed bucket, so this isn't a missing third citation — it's a discrepancy between the flat per-function total and the sum of what `callgrind_annotate <file.c>`'s line-by-line view shows for the same function, inside the same file, that this session could not resolve within its time-box. **Not chased further, not guessed at — flagged as an open methodology question** for whoever next needs exact per-line NV_SET_fn numbers to add to more than ~40% of its own citation.

**The in-source justification comment is measuring a retired regime, not stale-noise levels of drift.** `core.c:2256-2267` (the comment introducing the `_var_find_cached` memo table) cites: *"we spend 45.5% [in variable access]... MEASURED s258, roman.sno at N=20,000, **RT_OPT=-O2**, callgrind: 3,174,837 `_var_bucket_find` calls... = 22.42%, plus `NV_GET_fn` 10.81% + `__strcmp_avx2` 9.36% + `NV_SET_fn` 2.92%."` That's an `-O2` citation, retired as current-state evidence by the s262/s266 NO-`-O2`-EVER FACT RULE, *and* it predates the fast-path memo it's justifying (the numbers describe the pre-cure state). Fresh `-O0` post-cure, `NV_SET_fn` alone is now 12.46% — a different shape entirely (unsurprising: -O0 pays real call overhead everywhere -O2 would have inlined/optimized it away, so the two numbers aren't comparable on any axis, not even "did the cure help"). **Nobody has ever measured this memoization system's actual `-O0` payoff against a same-`RT_OPT` before/after** — that would need a build with the memo compiled out (`SCRIP_NV_MEMO=0` env killswitch already exists per the comment at line 2273) vs. one with it on, same tree, same `-O0`. Not attempted this pass (real, separable work); named here so the comment's own numbers stop being cited as current.

## C. New: `rt_sxt_break` pays a real `-O0` call for a one-line body, unconditionally, on every string-valued store — minted `perf-sxt-break-unconditional-call-tax`

`rt_sxt_break` (`gc_heap.c`) is called from `NV_SET_fn` line 2335 **unconditionally whenever the stored value is a string** — no gate, no cache, every time:
```c
void rt_sxt_break(const char *s) { if (s && s == g_sxt_owner) g_sxt_owner = (char *)0; }
```
One pointer-compare, one conditional null-store. Measured this pass: call-site self-cost 2,570,481 (0.69%) + callee self-cost 4,406,500 (1.18%) = **6,976,981 Ir (1.87% of kernel)** for 367,208 calls (≈19 Ir/call) — nearly all of that is `-O0`'s mandatory call/prologue/return overhead for a function whose entire compiled body is a handful of instructions, the same "`static inline` is a promise `-O0` doesn't keep" shape as the already-known `perf-core-tag-predicate-o0-call-tax` family and the already-landed `is_protected_pat_lead` fix (both cited in this same file's own comments).

**Why this is a new row and not a duplicate of `perf-core-tag-predicate-o0-call-tax`**: that row's entire "known dead end" framing is specifically about `DESCR_t`-by-value predicates whose `always_inline` reverted at s264 because it moved a GC-visible struct out of stack memory the collector's scanner depends on. `rt_sxt_break` takes a `const char *` (a raw pointer, not a `DESCR_t`), touches no GC-tracked struct, and only conditionally mutates a static global pointer — structurally a different shape from the reverted family. That makes it a **plausible** `always_inline` (or hand-inlined) candidate that does **not** obviously fall in the s264 minefield — but this session did not verify that against the actual GC-liveness mechanism (only read the s264 postmortem's *description* of the hazard, didn't re-derive whether `g_sxt_owner`/stack-scanning interacts with a raw-pointer argument the way it does with a by-value `DESCR_t`). Minted rather than cured, with this open safety question stated explicitly for whoever picks it up.

## D. Phantom-generalization consistency check, not re-proven — explicitly inherited from STEP 4

Re-measured STEP 4's 4 gdb-confirmed-phantom glibc-multiarch symbols on this session's tree (4 commits ahead, §Scope):

| symbol | STEP 4 (SCRIP `1a9cc1bc`) | this session (SCRIP `be376a2f`) | Δ |
|---|---:|---:|---:|
| `__strlen_avx2` | 2,141,790 (0.57%) | 2,141,790 (0.57%) | **0** — exact match |
| `__memcpy_avx_unaligned_erms` | 5,574,417 (1.48%) | 5,574,372 (1.50%) | −45 Ir, noise |
| `__strcmp_avx2` | 9,000,586 (2.39%) | 8,374,375 (2.25%) | −7.0% |
| `__memcmp_avx2_movbe` | 5,617,448 (1.49%) | 3,489,448 (0.94%) | **−37.9%** |

The two symbols that moved are exactly the two the intervening commits touch: `5d6f8a71` removes a redundant array-cache `memcmp`, `2d8d6df7` stops paying a full `strcmp` for every `'S'`-leading builtin's `SNO$NOFAIL` guard. **Temporally consistent, not proven causal** — no isolated before/after rebuild was done to confirm it (would need building at `1a9cc1bc` on this exact toolchain and diffing, out of this pass's time-box). Per this row's own established recipe, a citation this size deserves gdb re-verification before being trusted as still-phantom on THIS binary — **not done this pass**; STEP 4's verification (same symbols, same ifunc-resolution mechanism, same pinned `valgrind-3.22.0`/glibc-`2.39` toolchain, unrelated to anything in the 4 intervening commits) is cited as the standing proof rather than re-derived. Flagged so nobody mistakes "cited" for "re-verified this session."

## Row-factory actions taken this pass

1. **`callgrind-opaque-bb-labels`**: fed §A — the 31.32%-in-one-bucket concentration on `roman`, and the zero-FUNC-symbols confirmation extending to `main` itself, not just downstream BB-port labels.
2. **Minted `perf-sxt-break-unconditional-call-tax`** (§C) — `rt_sxt_break`'s unconditional per-string-store call tax, 1.87% of `roman`'s kernel, structurally distinct from the known-landmine `core.h` tag-predicate family, `always_inline`-safety not yet verified.
3. **Flagged, not minted**: the `core.c:2256-2267` memoization-justification comment cites retired `-O2` pre-cure numbers as its live rationale; a same-`RT_OPT` before/after of the memo's actual payoff has never been measured. Worth a session, not a row by itself.
4. **Open methodology question, not resolved**: `NV_SET_fn`'s `core.c`-attributed flat total (46,453,125) exceeds the sum of every individually-shown source line in `callgrind_annotate`'s own per-file view of that same function by 14,321,183 Ir (3.85% of kernel) — reported exactly as measured, cause not identified.

No cure attempted anywhere. Zero edits to any `.c`/`.h`/`.S`/`.cpp`/`.sno` file in SCRIP or corpus this session (`git status --short` clean in both trees, confirmed before and after this investigation — only untracked build/profile scratch under `SCRIP/.profile-scratch-seat12/`, not committed). Nothing under any `*/lon/*` path was read, listed, or otherwise touched.
