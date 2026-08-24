# FINDING 2026-08-24 (seat02) — ifunc-phantom-attribution generalizes to a second kernel; two new blind spots found alongside it

**Context:** `perf-string-runtime` STEP 4 (row-factory continuation), executing the alternative STEP 4 the task file itself names: *"check whether the `callgrind-ifunc-phantom-attribution` mechanism affects other already-profiled kernels' citations before trusting any of them further."* This doc is also the receipt for `callgrind-ifunc-phantom-attribution`'s own STEP 1 (all three of its sub-questions), and feeds two sibling rows. **No cure attempted anywhere. Zero edits to any `.c`/`.h`/`.S`/`.cpp` source in SCRIP.**

Trees: SCRIP `1a9cc1bc`, corpus `1de0caa`, .github `89f899b0` (all `main == origin/main`, clean, at session start). Toolchain: `valgrind-3.22.0`, glibc `2.39` (Ubuntu GLIBC 2.39-0ubuntu8.8) — pins STEP 1 item 3 of `callgrind-ifunc-phantom-attribution`.

⚠️ **Aside, not part of this row's own investigation:** `perf-string-runtime`'s STEP 3 receipt, `.github/FINDING-2026-08-24-seat04-bn-replace-translate-loop-and-strchr-phantom-attribution.md`, cited by both this umbrella's LEDGER and `callgrind-ifunc-phantom-attribution`'s own LINKS line as "all pushed," **does not exist anywhere in `.github`'s git history** (checked: full `ls FINDING-2026-08-24*.md`, `git log --all --diff-filter=A --name-only`, `git log --all` grepped for `strchr`/`translate-loop`/`phantom`/`ifunc` — zero hits, tree otherwise clean and current). Flagged to hq_C via `ask missing-step3-phantom-finding-receipt`, non-blocking — the LEDGER prose in `perf-string-runtime.task.md` preserves the substance (numbers + method), so this FINDING proceeds on that basis and independently re-derives the strchr mechanism below anyway.

## Method

`bench_wrap.sh --mode=iter --n=20000` on four corpus kernels (`table_access`, `roman`, `array_sum`, `string_manip` — the last as a fresh cross-check of STEP 3's own numbers), compiled mode-4 `-O0` (`./scrip --compile --target=x86 f.sno > f.s && as f.s -o f.o && gcc -no-pie f.o -Lout -lscrip_rt -Wl,-rpath,out -Wl,--allow-shlib-undefined -lm -o f.bin`), all four confirmed correct natively first (`check:` values: table_access 250500, roman 1102, array_sum 250500, string_manip 43 — the last matches STEP 1–3's own citation exactly).

**gdb verification recipe** (per STEP 3's own hard-won correction — a breakpoint on a libc symbol set *before* `main` is hit is PENDING and silently never resolves against a not-yet-loaded `.so`):
```
gdb -batch -nx -ex "break main" -ex "run < /dev/null" -ex "break <symbol>" -ex "continue" -ex "bt 8" -ex "continue" <binary>
```
A REAL hit shows a `Breakpoint N, <symbol> (...)` line and a backtrace into a genuine SCRIP runtime caller. A PHANTOM shows the breakpoint set successfully at a resolved address, then the program's own `check:`/`iters:`/`ns:`/`ms:` output, then `No stack. / The program is not being run.` — i.e. it ran to completion and exited without ever hitting a breakpoint that gdb confirms is armed at a real, resolved, loaded address.

**Positive control**, run before trusting any PHANTOM verdict: `__sigsetjmp` on `roman_n20000.bin` — HITS, with backtrace `__GI___sigsetjmp → rt_call_arr_bl (by_name_dispatch.c:4644, fn="REPLACE") → n43_call_α`, matching the independently-known `setjmp-per-builtin-call` row exactly. This confirms the recipe correctly distinguishes real calls from phantoms; it is not simply that breakpoints never fire in this environment.

## Result 1 — STEP 1 item 1: YES, the pattern generalizes (5 phantoms now confirmed, 2 kernels)

`roman_n20000.bin` (SCRIP, mode-4, `-O0`, N=20000): `callgrind_annotate` flat profile TOTAL_Ir = 376,704,822 (BLOB `???` 174,803,903 / 46.40% — the `callgrind-opaque-bb-labels` mechanism, already a separate row, not re-investigated here beyond noting it's present in every kernel checked, not just string_manip). Four glibc AVX2-multiarch symbols appear in its top-30:

| symbol | Ir cited | % of kernel | gdb verdict |
|---|---:|---:|---|
| `__strcmp_avx2` | 9,000,586 | 2.39% | **PHANTOM** — breakpoint armed at `0x7ffff3b8b190`, never hit |
| `__memcmp_avx2_movbe` | 5,617,448 | 1.49% | **PHANTOM** — armed at `0x7ffff3b884a0`, never hit |
| `__memcpy_avx_unaligned_erms` | 5,574,417 | 1.48% | **PHANTOM** — armed at `0x7ffff3b88c00`, never hit |
| `__strlen_avx2` | 2,141,790 | 0.57% | **PHANTOM** — armed at `0x7ffff3b8b940`, never hit |

Sum: 22,334,241 Ir / **5.93% of roman's entire kernel** attributed to functions that provably never execute — on top of STEP 3's own `__strchr_avx2` finding on a *different* kernel (`string_manip`). Two kernels, five confirmed phantom citations, zero surviving the gdb check. **This is not a one-off** — it is, as `callgrind-ifunc-phantom-attribution`'s own STEP 1 warned, "a standing tax on every existing 'X% remainder, not chased further' citation" that used a raw flat-profile name without a native cross-check. `table_access`'s (crashed, see Result 2) partial profile also cited `__memcpy_avx_unaligned_erms` at 0.60% — plausible given `_tbl_grow` sits nearby in its profile, but **not gdb-verified this pass** (the run's own truncation already makes that citation suspect on other grounds; flagged, not chased).

## Result 2 — a SEPARATE, real bug: `table_access` reproduces the known `array-sum-valgrind-segv` crash

`table_access_n20000.bin` and `array_sum_n20000.bin` both **SIGSEGV under valgrind/callgrind while running correctly natively** (`table_access` native: `check: 250500` clean; `array_sum` native: `check: 250500` clean). This is `array-sum-valgrind-segv.task.md`'s exact defect, previously known only on `array_sum`, now confirmed on a second kernel:

```
Process terminating with default action of signal 11 (SIGSEGV)
 Access not within mapped region at address 0x1FFF001000
   at 0x4B81B57: gc_zeta_frame (gc_heap.c:564)
   by 0x4B829EA: gc_collect_ex (gc_heap.c:637)
   by 0x4B80528: rt_gc_point_arr_c (gc_heap.c:327)
   by 0x4EBBEA2: rt_gc_point_arr (rt_asm_helpers.S:113)
   by 0x4F5F5B8: rt_call_arr_bl (by_name_dispatch.c:4646)
```
Identical crash SITE (`gc_zeta_frame:564`) and identical call chain shape on both kernels — both are aggregate-heavy (TABLE / ARRAY) and both exercise the by-name-array-call GC-point path. Consequence for THIS row: `table_access`'s callgrind citations above (BLOB 38.74%, `table_set_descr_d` 19.98%, etc.) are from a **truncated** run — real code paths, but not the full N=20000 the fixed-work methodology asked for, and the 60.17%/51.61% "events annotated" lines in both crashed runs are the tell (a clean run should annotate ~100% minus the opaque-label blob, not fail to annotate 40-48%). Fed to `array-sum-valgrind-segv.task.md`'s LEDGER as a generalization; not cured (that row already has its own scoped STEP 1 — `memcheck --track-origins=yes` — and this is squarely inside its lane, not this row's).

## Result 3 — STEP 1 item 2, answered: SPITBOL does NOT carry the same artifact, but carries a WORSE, different one

Ran the identical `roman_n20000.sno` under `sbl_clean_bin()` (`/home/resources/spitbol-bench-oracle/sbl -bf`, confirmed `check: 1102` matching SCRIP) under callgrind directly (⚠️ `profile_callgrind.sh`'s `<binary> <input-file>` signature assumes the input arrives via stdin — SPITBOL takes its source as a CLI arg, so a first attempt through that script silently fed `sbl` zero arguments, producing a bogus 195,282-Ir total that was 100% dynamic-linker startup cost; caught by sanity-checking the number against STEP 2's own ~13-51M-Ir citations for a same-shape kernel, not assumed). Correct invocation: `valgrind --tool=callgrind ... "$SBL" -bf roman_n20000.sno < /dev/null`, TOTAL_Ir = 156,056,575.

**No glibc multiarch symbol appears anywhere in SPITBOL's own top-30** — not as a real cost, not as a phantom. `sbl` is dynamically linked against `libc.so.6` (`ldd` confirms), so this isn't a static-linking non-answer; for this kernel it simply doesn't route hot-path string work through the affected libc entry points enough to surface. **STEP 1 item 2's literal question is answered: the SAME mechanism does not reproduce on SPITBOL, at least not for roman.**

But `callgrind_annotate` on SPITBOL's own binary is **99.1% unattributed** (154,614,358 / 156,056,575 Ir as `???:0x... [sbl]` — all addresses inside `sbl`'s own text, confirmed by the bracket-tagged object path, not `libc.so.6`). That is an order of magnitude worse than SCRIP's 30-60% NOTYPE-label blob. `nm sbl | grep ' [Tt] '` shows why: large stretches of `sbl`'s hottest addresses (`0x406946`, `0x407217`, `0x408277`) have **no covering symbol at all** — the nearest preceding one for three of the four hot addresses is `sysbs` at `0x4032ba`, a gap of many KB with nothing named inside it. This is architecturally consistent with SPITBOL's classic SIL/MINIMAL-derived implementation style (a large hand-assembled interpreter dispatch core), and it is a **third, distinct** blind-spot mechanism — not `callgrind-ifunc-phantom-attribution` (that's third-party-symbol misattribution; this is zero symbol coverage of `sbl`'s *own* code) and not quite `callgrind-opaque-bb-labels` either (that's OUR compiler emitting untyped labels we can fix with `.type`/`.size`; `sbl` is a third-party, ORACLE-SWAP-PROCEDURE-protected binary we cannot patch beyond the two approved class-A compatibility hunks — this is very likely a **permanent** measurement limitation, not a fixable one).

**Practical resolution of the concern STEP 1 item 2 raised** ("if SPITBOL does NOT carry the artifact... every ratio... is asymmetrically inflated"): it does not, for the deeper reason that `callgrind`'s `PROGRAM TOTALS` is computed independent of symbolization — the ifunc-phantom mechanism **relabels which named bucket gets credit for real, already-executed instructions; it does not fabricate extra Ir events**. (Concretely: `PROGRAM TOTALS` is a straight sum of collected Ir events, computed before any per-symbol attribution step; mislabeling an event's owner cannot change that sum.) So **SPITBOL/SCRIP Ir-total ratios — the headline numbers this whole row exists to defend — are NOT corrupted by ifunc-phantom-attribution**, on either side. What IS at risk, only on the SCRIP side (since that's where the phantoms were found) and only within a single engine's own profile, is any "X% is caused by glibc function Y" sub-citation used to justify *where* to aim a cure — exactly the kind of citation `perf-string-runtime`'s own BRIEF originally used (`memcmp family 5.99`, `strcmp under rt_call_arr_impl 1.96`) before the s262/s265 `-O0` re-baseline superseded those `-O2` numbers anyway.

Incidental, freshly-measured, fully-labeled data point (not this row's headline, offered since it fell out of the method for free): roman, mode-4, `-O0`, N=20000, `sbl_clean_bin()` vs current-HEAD SCRIP, same source both engines — **SPITBOL/SCRIP Ir = 156,056,575 / 376,704,822 = 0.4143x** (FACT RULE format, SPITBOL/SCRIP; this is an Ir-cost ratio, not a speed ratio — SCRIP spends ~2.41x the instructions SPITBOL does on this kernel at this N). Not cross-validated against any prior roman citation this pass; offered as a labeled, reproducible number for whoever picks up roman next, not as a claim about trend.

## Row-factory actions taken this pass

1. **`callgrind-ifunc-phantom-attribution`**: STEP 1, all three sub-questions answered (broad/real; SPITBOL does not share the mechanism but has its own worse one; toolchain pinned). LEDGER + NEXT updated to open STEP 2 (methodology note + optional `util_*.sh` automation script — **deliberately left undone**: STEP 2's methodology-note half reads as a RULES.md-level change, which feels like it wants HQ/CEO judgment on wording and placement rather than a single worker session's call, and the automation-script half is real but separable work; leaving both as a clean, well-evidenced STEP 2 for the next session or HQ).
2. **`array-sum-valgrind-segv`**: LEDGER updated — the `gc_zeta_frame:564` crash is not array_sum-specific, `table_access` reproduces it identically at N=20000. Not cured (in that row's lane, has its own scoped STEP 1).
3. **Minted `callgrind-sbl-opaque-core`**: new row for the 99.1%-unattributed SPITBOL-binary finding — distinct mechanism from both existing opacity rows, likely permanent (third-party oracle), but worth a session confirming that and deciding whether it's worth even a `nm`-based manual address-range annotation workaround for future SPITBOL-side investigations.

No cure attempted. Zero edits to any SCRIP/corpus source file this session.
