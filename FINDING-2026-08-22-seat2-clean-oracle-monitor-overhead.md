# FINDING seat2 (this session) — CLEAN SPITBOL ORACLE BUILT, AND THE MONITOR BRIDGE COSTS ~2.2-2.3x INSTRUCTIONS, NOT "NEGLIGIBLE"

**Session:** seat2 (`/home/claude2`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `clean-oracle-build` (rank 0)
**Tree:** SCRIP unchanged except `scripts/lib_oracle_flags.sh` (additive); `.github` this file + ARCH-PERF-TOOLING.md note. No `x64`/`corpus` edits — the whole row lives in a build outside the workspace root.

⛔ **THIS CONTRADICTS A STANDING RETRACTION IN THE ROW'S OWN BRIEF: "HQ reproduced NO penalty multiple; an earlier 2.4x was flag-mismatched and is WITHDRAWN — do not quote it."** My independently cross-validated number is **2.30x** on call-dense code and **2.22x** on arithmetic-only code — landing almost exactly on the withdrawn figure. I cannot see what the original 2.4x measurement's flag mismatch was, so I cannot say whether it was the same bug reproduced or a coincidence. I can say my own methodology matched flags/toolchain throughout and reproduced deterministically two independent ways. **Read §4 before deciding what to do with this.**

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

**Why this may matter beyond this row:** ARCH-PERF-TOOLING.md §7 bases the entire current queue-priority policy (48 performance rows ranked above 81 others) on FINDING s251's conclusion that "SCRIP already beats SPITBOL on every microarchitectural axis... it is instruction-count bound... capped near 1.4x." If s251's SPITBOL-side numbers (810M instructions on beauty self-host, IPC 2.33, mispredicts 0.83%, frontend idle 22.70%) were measured against the instrumented oracle — which is the only oracle that has existed until this session — and if the ~2.2-2.3x instruction multiplier found here generalizes to that workload, a clean re-measurement could put SPITBOL meaningfully lower on instructions and could change its IPC/branch-miss/frontend-idle profile too (I could not check the last three directly: `perf stat` is unusable in this container for kernel `6.17.0-1032-oem` — "perf not found for kernel," and I did not chase installing a kernel-matched `linux-tools` package, which is out of scope for this row and not authorized by `install_system_packages.sh`). **I have not re-run beauty self-host or any full benchmark suite against the clean oracle — that is a much larger undertaking than this row's DONE-WHEN, and I did not want to overreach a rank-0 "does it build and run correctly" row into re-litigating a foundational finding on my own authority.** I am flagging it as the single highest-priority open question this row surfaces, not answering it.

---

## 5. DONE-WHEN CHECKLIST

- [x] Clean uninstrumented binary exists; `nm`/`strings` show zero occurrences of `sysmc`/`sysml`/`sysmv`/`monitor_init`/`MONITOR_READY_PIPE` (also checked `sysmr`/`sysmw`/`pmcll`/`pmext`/`pmred`/`pmfal`/`MONITOR_GO_PIPE` — all zero).
- [x] Answers the case-sensitivity witness correctly — with a documented, intentional flip side: the clean build (uppercase-canonical, matching SCRIP) now requires `END` not `end` under `-bf`, and **the checked-in instrumented oracle requires exactly the same thing** (verified side by side) — this is the patch working as designed, not a regression.
- [x] Runs all 15 `corpus/benchmarks/snobol4/*.sno` kernels to the same **deterministic** output as today's oracle — every `check:` line matches exactly. The `iters:`/`ns:`/`ms:` fields differ between runs, **including between two consecutive runs of the identical current-oracle binary** (verified) — these are self-calibrating wall-clock fields by harness design, not a correctness signal.
- [x] Path is the one authority in `scripts/lib_oracle_flags.sh` (`sbl_clean_bin()`). Script adoption (switching callers over) is a separate follow-on, not this row.
- [x] This FINDING states the measured instrumented-vs-clean delta on call-dense code with matched flags (§4).

## 6. WHAT'S NOT DONE, ON PURPOSE

- `LOAD`/`UNLOAD` external-function ABI: clean binary behaves like stock upstream (its own incomplete stub), not the fork's rewrite. No corpus program among the 15 kernels needs it; flagged in §2 for a real Class A/C ruling if ever needed.
- No script has been rewired to call `sbl_clean_bin()` yet.
- No full-corpus or full-benchmark-suite run against the clean oracle — only the 15 top-level kernels (DONE-WHEN's own scope) plus two hand-written measurement witnesses.
- `perf`-based IPC/branch-miss/frontend-idle cross-check: blocked by a kernel/tool version mismatch in this container, not attempted further.

**Recommend to HQ:** treat §4's implication for FINDING s251 as the actual headline here, not the build itself — the build succeeding was expected; the 2.2-2.3x number contradicting a "do not quote" retraction was not.
