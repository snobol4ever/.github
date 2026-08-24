# FINDING 2026-08-24 — seat04 — `perf-string-runtime` STEP 6: `bn_size`'s remaining 3.77% fully accounted; the strchr "phantom" was misattributed and has a precise mechanism

## Scope and comparability

`perf-string-runtime`'s own STEP 5 (seat07) left one explicit open thread: *"Not chased (honest boundary, out of this session's three-symbol brief): `bn_size`'s own remaining ~3.77%-of-kernel breakdown beyond its two `IS_CSET_fn` calls."* This session chases exactly that, on the same kernel (`string_manip.sno`), same recipe as every prior STEP.

- SCRIP `0f4231f8` (2 commits past seat07's `447faf10`; `git log 447faf10..HEAD -- src/runtime/by_name_dispatch.c src/runtime/core src/contracts/core.h` empty — directly comparable, confirmed before measuring).
- corpus `63d60ae1` (pulled fresh — 13 commits behind at session start, a large `benchmarks/`/`demo/` reorg, `string_manip.sno` unaffected: same path, same bytes).
- Fresh own-build (`make`, RT_OPT=`-O0` per the s262 NO-`-O2` FACT RULE), fresh `bench_wrap.sh --mode=iter --n=20000` twin, mode-4 (`scrip --compile -o file.s`, then `gcc -no-pie file.s -L out -lscrip_rt -Wl,-rpath,out -o file.bin` — `scrip` itself never invokes an assembler or linker; every script that produces a runnable m4 binary does this two-step outside the driver, confirmed by grep across `src/` finding zero `system()`/`popen()`/`execve` in the unified driver).
- `check: 43` — matches seat04's STEP 2/3 and seat07's STEP 5 citations exactly.
- `callgrind --smc-check=all-non-file`: `TOTAL_Ir=51,186,163` (seat07 cited `51,186,375`/`51,121,149` variants across runs; this is 0.0004%/0.13% drift, noise not regression, same disposition every prior session has recorded).
- `bn_size` flat self-cost: **1,932,004 Ir (3.77%)** — byte-identical to seat07's own citation. Tree is confirmed comparable before any of the analysis below.

## A. Exact line-by-line accounting of `bn_size`'s self-cost (source-line `callgrind_annotate`, same technique STEP 3 used on `bn_replace`)

`by_name_dispatch.c:5024-5050`. Self-cost sum below equals **1,932,004 — exact arithmetic match to the flat citation**, not eyeballed:

| line | code | self-cost Ir | % of kernel |
|---|---|---:|---:|
| 5024 | function prologue | 168,000 | 0.33% |
| 5025 | `if (nargs != 1) return -1;` | 42,000 | 0.08% |
| 5026 | `DESCR_t v = args[0];` (16-byte struct copy) | 189,000 | 0.37% |
| 5027 | `if (IS_FAIL_fn(v))...` | 42,000 | 0.08% |
| 5028 | `if (v.v == DT_T)...` | 63,000 | 0.12% |
| 5029 | `if (v.v == DT_A)...` | 63,000 | 0.12% |
| 5030 | `if (v.v == DT_DATA)...` | 63,000 | 0.12% |
| 5036 | `if (IS_INT_fn(v))` call site | 147,000 | 0.29% |
| 5037 | `if (IS_REAL_fn(v))` call site | 147,000 | 0.29% |
| 5038 | `if (IS_CSET_fn(v))` call site **[#1]** | 147,000 | 0.29% |
| 5043 | `s = VARVAL_fn(v); if (!s)...` | 189,004 | 0.37% |
| 5044 | `if (strchr(s,'\x01'))` call site | 126,000 | 0.25% |
| 5048 | `len = IS_CSET_fn(v) ? ... : ...` call site **[#2]** | 294,000 | 0.57% |
| 5049 | `*out = INTVAL(len); return 1;` | 189,000 | 0.37% |
| 5050 | function epilogue (`}`) | 63,000 | 0.12% |
| | **sum** | **1,932,004** | **3.77%** |

(Line numbers here are the statement's own line inside the function; `callgrind_annotate`'s printed offsets in the raw transcript are these ±0, cross-checked directly against `Read` of the source.)

Plus callee edges hanging off those call sites (separately bucketed by `callgrind_annotate`, standard flat-profile behavior — self-cost of the *called* function, not `bn_size`'s):
`IS_INT_fn` 273,000 (21,000×) · `IS_REAL_fn` 273,000 (21,000×) · `IS_CSET_fn` **twice**, 336,000 (21,000×) each · `VARVAL_fn` 189,000 (21,000×) + 603 one-time `_dl_runtime_resolve_xsave` · strchr-edge 651,000 (21,000×, address discussed in §C).

A **second**, separately-keyed citation — `descr.h:bn_size`, 84,000 Ir (0.16%) — is also part of `bn_size`'s real physical instruction stream, not a distinct cost center: `FAILDESCR`/`INTVAL` are compound-literal macros (`contracts/descr.h:73`, `contracts/IR.h:12`), and at `-O0` GCC's DWARF line-table for a compound-literal temporary's construction sometimes resolves to the **struct type's declaration file** (`DESCR_t` is declared at `descr.h:52-67`) rather than the macro's use site. Cross-check: `bn_size`'s full inclusive cost as seen from its caller (`try_call_builtin_by_name_bl`'s own `=> bn_size (20,999×)` edge) is 4,073,806 Ir; self (1,932,004) + all callee edges above (2,058,603) + this 84,000 = 4,074,607 — matches to within 801 Ir (0.02%), fully explained by the 20,999-vs-21,000 call-count difference between the two views. Not a new cost center, not worth its own row; noted here only so the accounting is honest and closed.

## B. Line 5048's `IS_CSET_fn(v)` re-check is provably dead code (new, small, zero-risk finding)

`IS_CSET_fn` (`core.h:32`) is `static inline int IS_CSET_fn(DESCR_t v) { return v.v == DT_S && v.slen == 0xFFFFFFFFu; }` — takes `v` **by value**, reads only its own copy of two fields, no globals, no side effects: a pure function of its argument.

`v` (the local declared at line 5026) is **never reassigned** anywhere between line 5038 and line 5048 — every statement in between either returns or touches a *different* local (`s`, derived from `VARVAL_fn(v)`, not `v` itself). Control can only *reach* line 5048 by falling through the `if (IS_CSET_fn(v)) { ...; return 1; }` at line 5038 without taking it — i.e. by `IS_CSET_fn(v)` having already evaluated **false**. Since the function is pure and `v` is unchanged, `IS_CSET_fn(v)` at line 5048 is **guaranteed to re-evaluate to the same false** it produced nine lines earlier. The ternary's true-branch (`(long)strlen(s)`) is unreachable for every possible input — this isn't specific to `string_manip.sno`'s workload, it's a control-flow tautology.

Cost paid for nothing: the callee edge alone is 336,000 Ir (21,000 real out-of-line calls, since `static inline` isn't honored at the mandatory `-O0` — same fact STEP 5 established for the family). Line 5048's own self-cost (294,000) is *not* entirely attributable to the redundant test — that line also evaluates the ternary's real (false-branch) work, `v.slen > 0 ? v.slen : (long)strlen(s)`. Line 5038, which does the *identical* `IS_CSET_fn(v)` call in the identical single-`if` shape with no additional work, costs 147,000 self — using that as the call-only baseline, line 5048's redundant-check overhead is **≈147,000 self + 336,000 callee ≈ 483,000 Ir (0.94% of kernel)** recoverable by replacing line 5048 with simply `long len = v.slen > 0 ? v.slen : (long)strlen(s);` — same output for every input, by the proof above.

This is a **different, safer class of cure** than either option `perf-core-tag-predicate-o0-call-tax` currently lists (the reverted `always_inline` attribute, or `patv_slot`-style call-site duplication of a *needed* check): here the check itself is logically redundant, so the fix is deletion, not inlining — zero interaction with the s264 GC/register-residency mechanism, since no call is being turned into an inline expression, an already-proven-dead call is just being removed. Fed to that row's LEDGER (§ below); not applied here (row-factory: mint, don't cure).

## C. The `__strchr_avx2` "phantom" citation's true caller is `bn_size`, not `bn_replace` — STEP 3's attribution needs correcting

STEP 3 (seat04) found callgrind citing `__strchr_avx2` at 635,418 Ir / 21,258 calls, proved via gdb that address is never entered natively, and — because `bn_replace` was the function under investigation and a direct source read of `bn_replace` and its callees found zero `strchr` calls — concluded the citation was a pure phantom "refuting... this row's own prior REPLACE cset/pattern-machinery hypothesis." That refutation of the REPLACE hypothesis is correct. But nothing in that STEP, or in STEP 4's generalization pass, checked whether the citation belonged to some *other* real caller instead of nowhere — and `bn_size` (a completely different builtin, `SIZE`, also called once per iteration by this same kernel) has a genuine, unhypothetical source-level call at line 5044: `if (strchr(s,'\x01'))`.

Raw call-graph check (`callgrind_annotate --tree=caller`, the caller-tree view, not the flat self-cost view):
```
   635,418 ( 1.24%)  < ???:0x0000000004b70e70 (21,258x) [???]
   635,418 ( 1.24%)  *  .../strchr-avx2.S:__strchr_avx2 [libc.so.6]
```
`__strchr_avx2`'s **only** incoming call-graph edge, across the entire kernel, is this one unresolved-address caller — `bn_replace` never appears anywhere as a caller of it. And `0x0000000004b70e70` is the *exact same address* `bn_size`'s own line-5044 call site cites as its callee edge (`=> ???:0x0000000004b70e70 (21,000x)`, §A). This is the same edge viewed from both ends. The ~0.9% count difference (21,258 vs 21,000) is unexplained and small — not chased further, flagged honestly rather than force-reconciled.

So: the citation is real cost, tied to a real call site (`bn_size`, not `bn_replace`), and the caller-side symbol is simply unresolved by callgrind's annotator (a PLT/ifunc-indirection artifact, not "nothing called this"). STEP 3's "phantom" verdict on the *named symbol never being entered* is correct and still gdb-verified below; its implicit attribution to `bn_replace`'s pattern/cset machinery was never actually supported by the call-graph and should be treated as superseded.

## D. Root mechanism, precisely identified: Valgrind hides AVX-512 from the guest's CPUID, so glibc's ifunc resolver picks a *different, sibling* implementation under callgrind than the one that runs natively

This machine has full AVX-512 (`/proc/cpuinfo`: avx512f/bw/cd/dq/vl/vnni/bitalg/vbmi2/... all present). glibc ships multiple ISA-tiered implementations of `strchr`/`memcmp`/`strcmp`/etc. (sse2, avx2, avx2_rtm, evex, evex512) selected once at load time by an ifunc resolver reading CPUID.

**Native execution** (`gdb -batch -ex "break main" -ex run -ex "break <symbol>"` on *every* multiarch sibling at once, after `main` so all shared libs are resolved — this generalizes the row's existing PROVEN RECIPE, which only ever checked the one named symbol):
```
__strchr_evex        hit 21,258 times   __strchr_avx2/_rtm/_sse2   hit 0 times
__memcmp_evex_movbe  hit 83,997 times   __memcmp_avx2_movbe/_sse2  hit 0 times
__strcmp_evex        hit 21,942 times   __strcmp_avx2/_sse2        hit 0 times
```
**The exact same binary, run live under Valgrind** (`valgrind --tool=callgrind --vgdb-error=0`, then `gdb -batch -ex "target remote | vgdb --pid=..."`, break past `main`, arm all four `strchr` siblings, `continue` to completion):
```
__strchr_avx2   hit 21,258 times   __strchr_avx2_rtm/_evex/_sse2   hit 0 times
```
**21,258 — the exact native EVEX hit count — reappears as the AVX2 hit count under Valgrind.** This is reciprocal, not coincidental: on this host, under Valgrind, the *same call sites* that select EVEX natively select AVX2 instead. Toolchain: valgrind-3.22.0 (matches the row's own pinned toolchain note), glibc 2.39. Mechanism (consistent with Valgrind's long-documented incomplete AVX-512 instruction decoding): Valgrind's simulated CPU does not report the AVX-512 feature bits glibc's resolver checks for, so the ifunc resolver — running for real, inside the guest, exactly the way it would on real AVX2-only hardware — falls back one tier. **It is not a callgrind attribution bug in the usual sense; it is Valgrind presenting a different CPU to the program than the one actually running it**, one tier down, for every glibc string/mem function that ships a multiarch dispatch.

Independent cross-check, same kernel: the flat profile's unexplained `83,997 Ir` blob at `???:0x0000000004b70ea0` (0x30 past the strchr address, §A/top-functions listing) — `83,997` is the *exact* native `__memcmp_evex_movbe` hit count. `memcmp`'s caller was already correctly attributed to `bn_replace`'s map-cache by STEP 1 (`perf-replace-map-cache-revalidation`, call-count-verified) — so this mechanism doesn't just explain a misattributed citation, it also means an *already-correctly-attributed* citation (`__memcmp_avx2_movbe`, `__strcmp_avx2`) is still measuring the wrong SIMD tier relative to native.

**Open, not chased — flagged honestly as a boundary:** whether AVX2 vs EVEX actually costs a *different number of instructions* for these input sizes (44-byte string scans), which would mean callgrind's Ir isn't just mislabeled but quantitatively off from true native cost. Attempted two ways this session, both dead-ended on this container: `perf stat -e instructions:u` — binary present but the kernel's perf module isn't installed (`WARNING: perf not found for kernel 6.17.0-1032`); `GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX512F` to force AVX2 natively for an A/B — masking `AVX512F` alone was insufficient, `__strchr_evex` was still selected (the resolver likely also checks BW/VL, not chased further to find the right combination). Left for whoever has a `perf`-capable host or the right tunables combination.

## E. A live, apparently-safe `always_inline` precedent for `DESCR_t` tag predicates already exists in-tree — complicates `perf-core-tag-predicate-o0-call-tax`'s "known dead end" framing

While confirming why `bn_size`'s line 5027 (`IS_FAIL_fn`) shows **no** separate callee edge — unlike `IS_INT_fn`/`IS_REAL_fn`/`IS_CSET_fn`, which all do — found: `IS_FAIL_fn` is **not** one of `core.h`'s six-member family (`core.h:28-33`). It's declared separately, in `contracts/descr.h:77`:
```c
/* always_inline, NOT bare `static inline`.  RT_OPT IS -O0 ... every one of these one-instruction
   tag tests was emitted as a real CALL ... Do not relax these back to plain `static inline` --
   at -O0 that silently reintroduces the call. */
static inline __attribute__((always_inline)) int IS_FAIL_fn(DESCR_t v) { return v.v == DT_FAIL; }
```
Same file, same comment block, also covers `IS_VARREF_fn` and `IS_NAMETRAP_fn` (a three-member trio, all `always_inline`, all live). `GOAL-HQ-PERFORM.md:157`'s s264 revert is specifically about **"the 14 `core/core.h` tag predicates + `dtax_off`"** — a different file, a different (larger) named set. This descr.h trio was never claimed reverted anywhere I could find, and the comment's imperative tone ("do not relax") reads as settled, shipped state, not an open experiment.

This doesn't contradict `perf-core-tag-predicate-o0-call-tax`'s citation — the s264 revert of the `core.h` family for breaking 3 deferred-capture tests is real and well-evidenced (GOAL-HQ-PERFORM.md's own words: *"it changes where descriptors live (register vs memory), which is the signature of a value the GC's stack scan can no longer see or repair"*). But it **does mean the danger is call-site-specific (whether a value must stay stack-visible for the GC across that particular call boundary), not a blanket property of "any one-line DESCR_t tag predicate."** `IS_FAIL_fn`/`IS_VARREF_fn`/`IS_NAMETRAP_fn` are `descr.h:76`'s own citation of hot call sites — `IS_VARREF_fn` 116,442 calls, `IS_FAIL_fn` 58,223, `IS_NAMETRAP_fn` 36,767, "32.7 calls per token" — sound like parser/token-processing paths, plausibly *before* values become GC-observable variable bindings, unlike `core.h`'s family reached from `by_name_dispatch.c`/pattern-capture-adjacent call sites. Nobody has yet compared the two populations' call sites to find the actual dividing line. That comparison — not another blanket attribute flip — is the concrete next step this row is missing, and it's exactly the kind of thing that could turn "known dead end" into "known dead end for these call sites, safe for those."

## What this feeds

- **`perf-string-runtime`** (this row): STEP 6 = the assigned thread, closed. §A is the complete, exact-arithmetic answer to "bn_size's remaining 3.77%." Everything below is what fell out of chasing it.
- **`callgrind-ifunc-phantom-attribution`**: §C corrects the STEP-3-era caller attribution (bn_replace → bn_size) using data the row's own STEP 2(c) marked optional/not-required; §D answers STEP 2(c) in full (mechanism identified, not just "a real caller exists somewhere") and generalizes the "PROVEN RECIPE" to check *all* multiarch siblings, not just the one named symbol, plus a live-under-Valgrind vgdb cross-check technique. The magnitude question in §D is new and unresolved — added as a new STEP.
- **`perf-core-tag-predicate-o0-call-tax`**: §B is a new, independent, zero-risk cure candidate (delete provably-dead code, not inline anything) worth landing on its own regardless of the bigger family's fate. §E is a new investigative angle (the safety boundary is call-site GC-liveness, not predicate shape) that could unblock the row's main ask.

No cure applied anywhere in this pass. Zero edits to any `.c`/`.h`/`.S`/`.cpp` source this session (row-factory duty, same as every prior STEP on this row).
