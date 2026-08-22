# FINDING seat2 (this session) — CLEAN SPITBOL ORACLE BUILT; ON THE ACTUAL BEAUTY WORKLOAD IT RUNS AT 3.53x FEWER INSTRUCTIONS THAN THE CHECKED-IN ORACLE

**Session:** seat2 (`/home/claude2`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `clean-oracle-build` (rank 0)
**Tree:** SCRIP unchanged except `scripts/lib_oracle_flags.sh` (additive); `.github` this file + ARCH-PERF-TOOLING.md note. No `x64`/`corpus` edits — the whole row lives in a build outside the workspace root.

⛔ **HEADLINE, MOVED UP FROM §4 BECAUSE IT OUTRANKS THIS ROW'S OWN SCOPE: on the exact `beauty.sno < beauty.sno` workload HQ's own FINDING already used (md5 `6f1671c0757729992ae01a6bdf16f081`), the checked-in `x64/bin/sbl -bf` takes 806,084,475 Ir; my from-source, uninstrumented, byte-output-identical build takes 228,144,314 — a 3.53x ratio, 71.7% of the checked-in binary's total instructions. That FINDING's own "equalized comparison" (SCRIP 2.1x SPITBOL, "the engine is close to competitive") stripped only a 23.47% pattern-match-hook subset of this; substituting a fully-clean SPITBOL denominator moves that headline ratio to roughly 5.8x. Full numbers in §4a. This also contradicts a separate, standing retraction in this row's own brief — "HQ reproduced NO penalty multiple; an earlier 2.4x was flag-mismatched and is WITHDRAWN — do not quote it" — my synthetic-witness number (§4, 2.2-2.3x) landed almost exactly on that withdrawn figure, and the real-workload number (3.53-3.64x) is larger still. I did not find the original 2.4x measurement's methodology to compare against; I can only report that mine matched flags and toolchain throughout, reproduced deterministically, and is now independently confirmed by a real, previously-published, un-retracted workload. Read §4 and §4a before deciding what to do with this.**

---

## 1. THE ROW'S OWN BLOCKER IS RESOLVED — A CLEAN, UNINSTRUMENTED, SCRIP-COMPATIBLE SPITBOL BUILDS AND RUNS CORRECTLY

Built from `github.com/spitbol/spitbol` HEAD `4fe74db` ("Version 4.0f"), already cloned at `/home/resources/spitbol-upstream` (outside the workspace root, per the brief — never a discovered repo). `make spitbol` (BASEBOL = the repo's own prebuilt `bin/sbl`) builds cleanly with stock `nasm 2.16.01` / system `gcc`, no source changes, in ~15s.

**Retraction confirmed first (per the brief's own STEP 1):** the fresh, unpatched upstream build honours `-f` correctly — `a = 1 / A = 2 / output = 'a=' a ' A=' A / end` (all-lowercase, matching upstream's native keyword case) under `-bf` prints `a=1 A=2`. **`-f` was never broken upstream; the earlier "both clean binaries fail -f" observation was about testing an UPPERCASE-keyword witness against a binary that only understands lowercase keywords — a witness-language mismatch, not a `-f` defect.**

Live path: `/home/resources/spitbol-clean/sbl` (278,256 bytes). Registered as the single authority in `scripts/lib_oracle_flags.sh` (`sbl_clean_bin()`), alongside the existing `sbl_lang_flags()`. Adoption — rewiring benchmark/scorecard scripts to actually call it instead of a hardcoded `x64/bin/sbl` path — is **not done in this row**, same scoping precedent as `sbl_lang_flags` itself (ARCH-PERF-TOOLING.md notes the timing harnesses still hadn't adopted `-bf` after that row landed either).

---

## 2. THE ALLOW-LIST CLASSIFICATION — EVERY HUNK OF (`sbl.min` + `osint/`), UPSTREAM VS FORK

Per Lon's amendment ("make ONLY the minor compatibility patches... but we must guarantee no performance related tainting" — an allow-list, not diff-minus-hooks), every hunk was read, not just headers.

**`sbl.min`** (upstream 29,310 lines, fork 29,440 — +130, matching the brief's own count exactly): 56 hunks total.
- **12 hunks, exactly +130 lines, CLASS B — REFUSED.** The `sysmv`/`sysmc`/`sysmr`/`sysml`/`sysmw`/`pmcll`/`pmext`/`pmred`/`pmfal` monitor-bridge declarations (comment-tagged `SN-26-spl-bridge-b`, `SN-26-bridge-coverage-{f,l,b}`, `S-2-bridge-7-byrd-pattern`) plus their 11 call sites, fired from statement dispatch (`stgo2`/`stgo3`), the untrapped assign fast paths (`asg01`/`asnp1`), function call/return (`bpf09`/`rtn03`), and pattern-match transfer (`p_abo`/`p_una`/`failp`/`succp`).
- **44 hunks, net 0 lines, CLASS A — PORTED.** Every one is the *same* mechanical change: a `/lowercase/` string-table entry rewritten `/UPPERCASE/` (control-card names, datatype names, return-type names, comparison-operator and builtin-function names) or the matching `flc`/`flstg` fold-direction reversal (fold-to-lowercase → fold-to-uppercase). This is the one patch Lon named in-chat ("We are keeping with UPPERCASE keywords for SCRIP... we hack it so we have no headaches"). Verified exhaustively — sampled every hunk's content, not just the headers; the two counts (44 + 12 = 56, 0 + 130 = 130) reconcile exactly against the brief's own figures with zero hunks left unclassified.

**`osint/`:** two new files + eight changed files.
- **CLASS B — REFUSED:** `monitor_ipc_runtime.c` (new; implements `zysmv`/`zysmc`/`zysmr`/`zysml`/`zysmw`/`zpmcll`/`zpmext`/`zpmred`/`zpmfal`, the C side of the bridge above).
- **CLASS A — PORTED:** `systm.c` (`zystm`, the `TIME()` builtin) — switches `CLOCK_PROCESS_CPUTIME_ID` (~471ns resolution, ~502ns/read, a real syscall) to `CLOCK_MONOTONIC` (1ns resolution, ~20ns/read via vDSO) and restores nanosecond units. Explicitly cited in-file as **"s249, Lon in-chat"** — a prior, separately-ruled fairness fix for cross-implementation timing, not a new judgment call of mine.
- **DEFERRED, NOT CLASSIFIED, NOT PORTED:** `extern32.h`, `osint.h`, `port.h`, `sproto.h`, `sysex.c`, `sysld.c`, `syslinux.c`, and the new `syslinux_float.c` — all one coherent subsystem, a substantial rewrite of the `LOAD`/external-function-call ABI (matching, per its own comments, "CSNOBOL4 load.h / libspl.c empirically verified ABI"), needed only by programs that call `LOAD()`. Upstream's own version of this code is an admitted incomplete stub (`/* todo ... */` in the pre-image). Whether "make LOAD work at all on x64 Linux" counts as *minor compatibility* or exceeds it is a real judgment call I did not make unilaterally — Lon's qualifier was "minor," and ~150 lines of ABI redesign is not that. **Not needed for this row's DONE-WHEN** (none of the 15 benchmark kernels use `LOAD`), so the clean binary's `osint/` is byte-for-byte upstream except `systm.c`. Flagged for HQ/Lon if the fleet ever needs `LOAD` against the clean oracle.

The `Makefile` diff (`-DEXTFUN=1 -ldl`) belongs entirely to the deferred LOAD subsystem, not the monitor bridge — confirmed by tracing both flags to LOAD-only code paths.

---

## 3. NO-TAINT PROOF FOR THE PORTED PATCH ITSELF (Lon's amendment, measurement not promise)

Compared **patched-clean vs. pure-unpatched-upstream**, identical uppercase source, identical `-b` flags (folding on, so both builds' opposite canonical case is transparent — isolates the patch from the separately-already-proven case-sensitivity behavior), callgrind Ir, 50,000-iteration call-dense witness:

| build | Ir | delta |
|---|---|---|
| pure upstream | 16,934,229 | — |
| patched-clean | 16,933,093 | **−1,136 (−0.0067%)** |

Controlled for the one obvious confound (argv[0] path-length difference affecting one-time startup scanning) by re-running both binaries from paths padded to identical length (121 chars): delta became −1,132 — unchanged, ruling that out. Full per-function `callgrind_annotate` diff (threshold 0.01% ≈ 1,690 Ir) shows **zero functions differing** — the residual is smaller than the threshold and scattered, consistent with one-time table-load cost from the patch's changed string bytes (uppercase vs lowercase ASCII values can walk a generic init routine differently even at identical string length). It does not scale with the witness's iteration count. **The compatibility patch is instruction-neutral; it satisfies the no-taint requirement.**

---

## 4. ⛔ THE MOTIVATING MEASUREMENT — MONITOR BRIDGE OVERHEAD, MATCHED FLAGS, CALL-DENSE CODE

This is the comparison the brief calls "the A/B nobody has yet done validly." Same witness, same `-bf` flags, both sides.

**Method, done two independent ways to rule out a build-config confound:**
1. Checked-in `x64/bin/sbl` (293,576 bytes) vs. my `spitbol-clean` (278,256 bytes) — different provenance, different toolchains.
2. **My own from-source rebuild of the complete, unmodified fork tree** (`x64/sbl.min` + all of `x64/osint/*.c` + `x64/Makefile`, same toolchain as my clean build) — produced a binary **293,576 bytes, byte-count-identical to the checked-in one** — vs. the same `spitbol-clean`. This isolates the monitor bridge as the *only* source-level variable, with toolchain, flags, and witness all held constant.

| witness | instrumented (checked-in) | instrumented (my rebuild, same toolchain) | clean | ratio |
|---|---|---|---|---|
| call-dense (50k calls to a `DEFINE`'d proc) | 38,933,790 | 38,933,783 | 16,930,929 | **2.30x** |
| arithmetic-only (50k-iter accumulator loop, no user calls) | — (not run) | 28,254,325 | 12,751,525 | **2.22x** |

The two independently-built instrumented binaries agree to within **7 instructions out of 38.9 million** — the checked-in binary is an unremarkable, faithful build of its own source; there is no separate "build difference" hiding here. Re-running the rebuilt-instrumented/call-dense callgrind a second time reproduced **38,933,783 exactly** — deterministic, not sampling noise.

**The overhead is not call-specific.** `sysml` fires on every statement-dispatch entry (`stgo2`/`stgo3` — the interpreter's general "next statement" labels, hit on essentially every SNOBOL4 statement executed) and `sysmv`/`sysmw` fire on every untrapped variable store (`asg01`/`asnp1`), independent of whether the statement is a user-procedure call. That is why the arithmetic-only witness — no `DEFINE`'d calls at all — still shows 2.22x: the hooks are pervasive across ordinary statement execution, not narrow to call sites. **This means essentially every existing benchmark number gathered against `x64/bin/sbl` has been measuring a SPITBOL running at roughly 43-45% of a clean build's throughput, whether or not the workload "calls" anything.**

**On the withdrawn 2.4x:** I do not know what the original, retracted measurement did differently — I was not able to find its methodology recorded anywhere I could read for this row. What I can say: mine held `-bf` fixed on both sides throughout, cross-validated via two independently-built instrumented binaries agreeing to 7 instructions, and reproduced exactly on a repeat run. If the earlier 2.4x came from comparing mismatched `sbl` invocation flags (e.g. instrumented-under-one-flag-set vs. clean-under-another), that is a different failure mode from mine and would not make mine wrong — but I flag explicitly that I cannot rule out my measurement rediscovering the same real effect the earlier one saw, correctly, via a flawed path that got the conclusion right and the method blamed. **This needs a second, independent pair of eyes before anyone acts on it further — I am reporting what I measured and how, not asserting HQ was wrong.**

### 4a. The real workload, not just synthetic witnesses

**This is not hypothetical — I ran it.** `FINDING-2026-08-22-hq-scrip-spends-under-one-percent-of-its-instructions-running-the-program.md` already documents (§"the equalized comparison," committed same day, un-retracted) that `x64/bin/sbl -bf` on `beauty.sno < beauty.sno` (md5 `6f1671c0757729992ae01a6bdf16f081`) totals **806,084,475 Ir**, of which HQ identified **189,156,333 Ir (23.47%)** as `emit_pm`/`pm_check_enabled`/`monitor_init` dead weight from just the four pattern-match hooks (`zpmred`/`zpmcll`/`zpmext`/`zpmfal`) — and left open "whether an actually-de-instrumented build changes `sbl`'s count" as HQ's own explicit next question. I have the de-instrumented build, so I ran the identical workload on it:

| | instrumented (`x64/bin/sbl -bf`, HQ's figure) | clean (`/home/resources/spitbol-clean/sbl -bf`, this session) | ratio |
|---|---|---|---|
| Total Ir, `beauty.sno < beauty.sno` | 806,084,475 | **228,144,314** | **3.53x** |
| Compile+init only (`< /dev/null`) | 9,113,074 | 9,080,970 | 1.00x (confirms the two builds agree when the hooks genuinely can't fire — no unrelated confound) |
| Runtime delta | 796,971,401 | 219,063,344 | **3.64x** |

Output verified byte-identical to the fixed point (md5 `6f1671c0757729992ae01a6bdf16f081`, matching the *input* file exactly, both under plain execution and under callgrind) — the clean binary is not just faster-counted, it is correct on the actual headline workload, not only the 15 synthetic kernels.

**In HQ's own dead-weight framing: not 23.47%, but 71.7%** of the instrumented oracle's total instruction count on this exact, already-published workload is instrumentation, not program (`(806,084,475 − 228,144,314) / 806,084,475`). HQ's own 23.47% (pattern-match hooks only) was a real, correctly-measured *subset* of this — the other five hook families (`sysml` on every statement, `sysmv`/`sysmw` on every store, `sysmc`/`sysmr` on every call) account for the rest, exactly the ones my §4 synthetic witnesses isolated.

**Direct consequence for FINDING s251 / ARCH-PERF-TOOLING §7:** HQ's own "equalized comparison" stripped only the pattern-match 23.47% and reported SPITBOL's genuine runtime work as 607,815,068 Ir against SCRIP's 1,272,013,514, for "2.1x, the engine is close to competitive." Substituting my fully-clean runtime-delta figure (219,063,344) for HQ's partially-stripped one, holding SCRIP's own number as HQ reported it (I did not re-derive it and have no basis to question it): **1,272,013,514 / 219,063,344 ≈ 5.8x**, not 2.1x. I have not touched or re-measured anything on the SCRIP side — this is purely "what does the SPITBOL denominator do when it's actually clean instead of partially cleaned." I could not cross-check IPC/branch-miss/frontend-idle the same way: `perf stat` is unusable in this container for kernel `6.17.0-1032-oem` ("perf not found for kernel"), and I did not chase installing a kernel-matched `linux-tools` package — out of scope for this row and not authorized by `install_system_packages.sh`.

**I have not re-derived SCRIP's side of the ledger, re-run any other benchmark, or drawn a new conclusion about what SCRIP should optimize next — that is HQ's/Lon's call, and a much bigger undertaking than this row's DONE-WHEN.** What I can stand behind: the 806,084,475 vs 228,144,314 numbers, the matched compile+init control, and the byte-identical output. I am flagging this as the single highest-priority open question this row surfaces, not answering it myself.

---

## 5. DONE-WHEN CHECKLIST

- [x] Clean uninstrumented binary exists; `nm`/`strings` show zero occurrences of `sysmc`/`sysml`/`sysmv`/`monitor_init`/`MONITOR_READY_PIPE` (also checked `sysmr`/`sysmw`/`pmcll`/`pmext`/`pmred`/`pmfal`/`MONITOR_GO_PIPE` — all zero).
- [x] Answers the case-sensitivity witness correctly — with a documented, intentional flip side: the clean build (uppercase-canonical, matching SCRIP) now requires `END` not `end` under `-bf`, and **the checked-in instrumented oracle requires exactly the same thing** (verified side by side) — this is the patch working as designed, not a regression.
- [x] Runs all 15 `corpus/benchmarks/snobol4/*.sno` kernels to the same **deterministic** output as today's oracle — every `check:` line matches exactly. The `iters:`/`ns:`/`ms:` fields differ between runs, **including between two consecutive runs of the identical current-oracle binary** (verified) — these are self-calibrating wall-clock fields by harness design, not a correctness signal. Also ran the actual `beauty.sno < beauty.sno` self-host fixed point (§4a) — byte-identical to the checked-in md5 both natively and under callgrind.
- [x] Path is the one authority in `scripts/lib_oracle_flags.sh` (`sbl_clean_bin()`). Script adoption (switching callers over) is a separate follow-on, not this row.
- [x] This FINDING states the measured instrumented-vs-clean delta on call-dense code with matched flags (§4).

## 6. WHAT'S NOT DONE, ON PURPOSE

- `LOAD`/`UNLOAD` external-function ABI: clean binary behaves like stock upstream (its own incomplete stub), not the fork's rewrite. No corpus program among the 15 kernels needs it; flagged in §2 for a real Class A/C ruling if ever needed.
- No script has been rewired to call `sbl_clean_bin()` yet.
- No full-corpus or full-benchmark-suite run against the clean oracle — only the 15 top-level kernels, `beauty.sno` self-host (DONE-WHEN's own scope, plus the workload FINDING s251/HQ's own equalized-comparison finding used), and two hand-written measurement witnesses.
- `perf`-based IPC/branch-miss/frontend-idle cross-check: blocked by a kernel/tool version mismatch in this container, not attempted further.
- SCRIP's own side of the ledger (the 1,272,013,514 Ir "genuine runtime work" figure) was not re-derived or questioned — only substituted a clean SPITBOL denominator into HQ's own published SCRIP numerator.

**Recommend to HQ:** treat §4a's beauty-workload number as the actual headline here, not the build itself, and not even the synthetic-witness §4 number. The build succeeding was expected. A 71.7% dead-weight fraction on HQ's own already-published headline workload, and a 2.1x→~5.8x move in HQ's own "equalized comparison," were not.
