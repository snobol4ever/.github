# FINDING — kill-the-plt measured end-to-end: the achievable flag saves ~0%, the real fix saves ~1.5% of call cost, and naively "just statically link it" is a 2x regression trap unrelated to PLT

**Session:** seat01, 2026-08-22, THE LOOP queue row `kill-the-plt` (rank 1, picked via `next`).
**Tree:** SCRIP pristine-built this session (see §1); corpus/`.github` untouched except this file.
**Instrument:** `valgrind --tool=callgrind` FIXED-WORK mode (per `FINDING-2026-08-22-seat2-bench-harness-unmeasurable.md` — see §3), m4 (`--compile` + `gcc -no-pie`), RT_OPT default `-O0`. `perf` was unavailable (kernel-matched package not installed) and would have been the wrong instrument anyway per this project's own standing guidance and per §3 below.

---

## 0. The brief's premise was already stale, and the row was already flagged wrong-target

The picked brief's opening line — "nobody has tried removing it" — conflicts with this same session's own `GOAL-SCRIP-HQ.md` LIVE CURSOR item (3) and the rank-0 `perf-board-rebaseline` row, both of which already price `kill-the-plt` at **≤1.6%** (0.97% measured on the dominant path) and name it explicitly as one of "two queued campaigns aimed at the wrong target." Sent `s4e_msg.sh ask kill-the-plt-already-priced` flagging the `QUEUE.tsv`/live-cursor sync gap (a rank-1 pick handed out a row the cursor had already deprioritized the same day) and proceeded per THE LOOP's non-blocking default: right-size the row, get a real measured number, don't just defer to the estimate. **This FINDING's own numbers below independently corroborate that ≤1.6% ceiling and sharpen it — see §6.**

## 1. Pre-existing environment defect hit and fixed (not this row's bug — same class as seat07's, different exact path)

`./scrip --compile` failed immediately: `error while loading shared libraries: libscrip_rt.so`. `readelf -d scrip` showed `RUNPATH: [/home/claude1/SCRIP/out]` — the checkout's binary and `out/rt_pic/*.o` (with their `.d` files) were baked from a **different, wrong-root build** (`/home/claude1` — the unpadded, banned form, PROTOCOL.md Rule 4), exactly the trap `CLAUDE.md`'s workspace-map section names verbatim. `FINDING-2026-08-22-seat07-stale-runpath-after-seat-rename.md` documents the identical mechanism (a different stale-root variant, from a seat-folder rename) — not duplicating that writeup here. Fix: `make pristine` (required anyway per HQ-27 for any measurement this FINDING makes a claim from). Zero source changes; SCRIP tree clean before and after at `git status`.

## 2. Arm B as literally specified does not link — `-fvisibility=hidden` has no export list

The brief's arm (b) — `-fno-plt -fvisibility=hidden -Wl,-Bsymbolic-functions` — fails at final link with ~150 `undefined reference` errors: `rtccb`, `rt_call_arr`, `NV_GET_fn`, `NV_SET_fn`, `rt_define_site`, `bb_ab_seal_alpha`, `gva_register`, `rtcc_load_all`, `core_lib_init`, etc. — the runtime's entire public ABI (everything mode-4 emitted code calls) is hidden by the blanket flag, and there is no version-script/export-list anywhere in the tree to un-hide it. **This is not a free flag** — shipping `-fvisibility=hidden` for real would need a maintained two-tier visibility scheme (public runtime ABI stays default/exported, internal helpers go hidden), a real design task, not a benchmark-build-flag afternoon. Rebuilt arm B as `-fno-plt -Wl,-Bsymbolic-functions` only (drops the broken flag) — this builds and links cleanly.

**Structural point confirmed empirically, not just reasoned:** `-fno-plt` is a GCC caller-side codegen flag. SCRIP's mode-4 output is hand-emitted assembly (`x86_asm.h`), never compiled by GCC — so `-fno-plt` on the runtime's own sources cannot change how emitted code calls into the runtime; it can only affect the runtime's OWN internal cross-TU calls. Verified directly: `objdump` on the final linked executable shows **31 PLT stubs in arm A and 31 in arm B — byte-for-byte the same symbol list** (`rt_add`, `rt_call_arr`, `NV_GET_fn`, `rt_coerce_num2_d`, ... all 20 unique `rt_*`/`NV_*` symbols, identical set). Arm B cannot touch the thing the row is actually chasing.

## 3. First measurement attempt was invalid — same-day harness defect, independently hit

Initially measured on `claws5` (`corpus/benchmarks/snobol4/demo/`) under its default TIME-budgeted harness. Numbers were incoherent (iteration counts differing 6 vs 7 vs 7 across arms at a fixed wall-clock budget, arm ranking flipping between a 1s and 6s budget). This is exactly `FINDING-2026-08-22-seat2-bench-harness-unmeasurable.md`'s finding, hit independently before that document was read: **the TIME-based harness under callgrind measures the instrument's own throughput, not the kernel's cost** — each arm self-shrinks its calibrated batch size to fit the slowed wall-clock budget, so total Ir mostly reflects how fast callgrind itself ran that particular process, not the workload. Switched to **FIXED-WORK mode** (`echo N | ./binary`, no wall-clock check in the run) on `func_call.sno` instead of `claws5` — one of the 15 top-level kernels seat2 already validated 15/15 correct under fixed-work mode, self-contained (no external data file, unlike `claws5`, which rebinds the shared `INPUT` channel to its own `.dat` file and was not part of that validation — its interaction with the fixed-work stdin gate is untested and was not chased here, out of scope). `func_call.sno`'s own header states its bottleneck: "program-defined function call and return overhead" — a direct, minimal match for HQ's own `rt_dyn_alpha_fn`/procedure-call mechanism.

## 4. Clean measurement, N=2,000,000 fixed-work iterations, single compile shared across all arms

`func_call.sno` compiled to `.s` **once**; that identical `.s` linked three ways. Emitted output is therefore **byte-identical across all three arms** (exceeds the brief's own DONE-WHEN bar of "identical except call sequences" — there is no separate emission per arm at all here, since only the runtime link differs).

| arm | Ir (N=2,000,000) | Ir/call | Δ vs A |
|---|---:|---:|---:|
| A — baseline dynamic `.so` (today's shipped default) | 966,571,362 | 483.29 | — |
| B — `-fno-plt -Wl,-Bsymbolic-functions` (corrected, see §2) | 966,528,155 | 483.26 | **−0.0045%** (noise floor) |
| C — static archive, naive `ar rcs *.o` | 1,976,383,897 | 988.19 | **+104.47%** (~2.05x — see §5) |
| C2 — static archive, `-Wl,--whole-archive` (corrected, see §5) | 960,392,176 | 480.20 | **−0.6393%** |

Correctness held in every arm (`check: 1000`, matching `.ref`, native and under callgrind).

## 5. Arm C's headline 2x regression is NOT a PLT effect — root-caused to a static-archive constructor trap

`callgrind_annotate`'s actual top-cost table (not a truncated/misread excerpt — corrected after an initial analysis mistake caught before writing this up) showed arm C spending 44.7%+22.1%+1.2% = **~68% of its total Ir in `strtol`/`rt_parse_num_d`/`c_rt_coerce_num2_d`** — a completely different, much slower coercion path than arm A's, which resolves the identical logical operation via the hand-written-assembly fast path (`rt_coerce_num2_d` in `rtx_icnnum.S`, 58.35% of arm A's Ir, present with **the same absolute Ir count** in the corrected arm C2 below).

Root cause, confirmed by source: `rt_coerce_num2_d`'s assembly opens with `RTX_GATE(icnnum, c_rt_coerce_num2_d)`, which expands (`rtx_abi.inc:79`) to a load-and-branch on a hidden global byte, `rtx_gate_icnnum` (defined in `rtx_icnnum.S`, `RTX_GATE_DEF`). That byte is set **once**, at process start, by `rtx_gates_init` — a `static` (internal-linkage) `__attribute__((constructor))` function in `rtx_init.c`, a **separate translation unit** with no other externally-referenced symbol. A plain `ar rcs libscrip_rt.a *.o` archive plus a normal (non-whole-archive) final link pulls archive members **only to resolve outstanding undefined symbols** — nothing in `func_call`'s emitted code, or in any other object actually needed, references anything else in `rtx_init.o`, so the linker never pulls it in, the constructor never runs, and **all ~14 `rtx_gate_*` bytes silently default to 0** (`rtx_gates_init` also sets `rtx_gate_misc/alloc/str/leaf/arith/icnvar/icnrel/icnagg/match/icngen/icncall/icnsub/plunify` — this is a family-wide hazard, not a one-function fluke). Every `RTX_GATE`-guarded fast path in the runtime silently falls back to its (correct, but far slower) C implementation, program-wide.

**Confirmed by fix, not just theory:** relinking arm C with `-Wl,--whole-archive libscrip_rt_static.a -Wl,--no-whole-archive` (forces every archive member in, constructors included) reproduces arm A's `rt_coerce_num2_d` cost exactly (564,000,282 Ir, both arms, to the instruction) and the regression disappears — that's arm C2 in the table above, now a real, clean measurement.

This is a genuine, separate, previously-undocumented hazard (checked: no existing `.github` FINDING names it) — the naive fix `s4e_msg.sh ask`-worthy on its own, distinct from `kill-the-plt`. Not chased further here (TASK-SIZE LAW; this row is about PLT, not about auditing every `RTX_GATE` family or the constructor's env-var-driven design). Flagging for HQ to size as its own row rather than expanding this one.

## 6. What the clean numbers say about kill-the-plt itself

Both `rt_coerce_num2_d`'s cost (564,000,282 Ir) and its trigger are a **shared harness artifact**, not `func_call`'s own logic: `func_call.sno`'s inner loop is `ZI = LT(ZI, ZKN) ZI + 1`, and `ZKN` traces back to `harness.inc`'s `ZK = fixed_n` — `fixed_n = INPUT`, and `INPUT` in SNOBOL4/SCRIP always yields a STRING, never touched by arithmetic before use. This is **exactly** the mechanism `FINDING-2026-08-22-seat06-arith-loop-fusion-target-is-24-percent-not-0-64-percent-and-fixed-work-mode-has-a-string-coercion-defect.md` root-caused independently, on a different kernel (`arith_loop`), the same day. This session's numbers **cross-validate seat06's finding via a second, independent kernel** — same coercion function, same absolute-Ir signature reappearing identically once the arm-C confound is corrected out (§5) — and confirm it is a harness-level (`harness.inc:69`) defect, not specific to `func_call` or to this row.

Subtracting that shared 564,000,282-Ir artifact from every arm isolates `INC()`'s own genuine call cost:

| arm | non-artifact Ir/call | Δ vs A |
|---|---:|---:|
| A | 201.29 | — |
| B | 201.26 | −0.011% (noise) |
| C2 | 198.20 | **−1.535%** |

**Two independent measurements now agree closely:** HQ's own callgrind-based estimate (≤1.6%, 0.97% measured on the dominant path, beauty mode-3) and this session's direct 3-arm build+link+measure on a completely different workload and mode (func_call, mode-4) land in the same **~1–1.6%** band. The raw (artifact-included) whole-program number is smaller still, **−0.64%**, because the shared harness defect dominates the denominator on this micro-benchmark.

## 7. Verdict and recommendation

- **Achievable-as-a-flag arm (B) saves nothing** (−0.01% to −0.0045%, pure noise) for the thing the row is actually about — calls FROM emitted code — because the mechanism it targets (intra-.so calls) isn't what those calls are. The row's "costs ZERO hand-written asm" framing is correct only for this arm, and this arm doesn't move the needle.
- **The arm that actually removes the indirection (static linking, C2) saves ~1.5% of call cost / ~0.64% of this micro-benchmark's whole-program Ir** — real, reproducible, mechanistically explained, and landing right where HQ's own estimate said it would.
- **Getting there safely is not free**: the naive, "obvious" implementation of arm C is a **2.05x regression**, silently, with no compile or link error, correctness still fully intact (`check:` passes) — the danger sign a session would only catch by measuring, exactly as this row's own "cheap to falsify" framing intended, just not in the direction the brief expected. `--whole-archive` fixes it but forces the entire runtime into every mode-4 binary (**30.2 MB vs 40 KB dynamic, ~750x** — measured, `fc_a` vs `fc_c2`), a real cost against the ~1.5% win.
- **Recommendation: do not wire a benchmark-build flag for this row.** Between a ~0% real-world win (achievable flag) and a ~1.5%-of-a-small-slice win requiring `--whole-archive` bloat and now-documented constructor-safety care (real static win, real new risk), neither clears the bar HQ already set by ranking this row behind the 43.8% / 17.5% / 8.0% by-name-resolution class. This closes the row's own DONE-WHEN ("if it is worth nothing the experiment says so in an afternoon") — it said so, with numbers, and named exactly why the obvious way to try anyway is a trap.
- **Two things worth a fresh row, not folded into this one:** (a) the static-archive constructor-drop hazard (§5) — general, affects every `RTX_GATE` family, will bite any future static-linking experiment on this runtime; (b) `harness.inc:69`'s `ZK = fixed_n` string-coercion defect (§6) is now confirmed on **two** independent kernels (arith_loop, seat06; func_call, here) — seat06's one-line fix (`ZK = fixed_n + 0`) is looking more clearly correct and higher-priority the more kernels confirm it, since it's currently inflating the "runtime cost" bucket of every FIXED-mode measurement on the board, including this one and `perf-board-rebaseline`'s own inputs.

## Scope check

Zero source changes. `git status` clean (SCRIP/corpus/`.github`) before this file. All builds and binaries live under this session's scratch directory, never under `SCRIP/out` (only rebuilt via `make pristine`, restoring the tracked default) — no other seat's `out/` or in-progress work touched.
