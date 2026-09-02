# FINDING: `prolog-builtins-wired-at-compile-time-not-dispatched-by-name` (P6) — `dop_ax`/`dop_cmp` called directly, correctness proven, measured win on available witnesses is real but tiny — and the reason why is the actual deliverable

**Row:** `prolog-builtins-wired-at-compile-time-not-dispatched-by-name` (P6, rank 1, minted by hq_P 2026-09-01, deliberately not blocked on P5).
**Session:** seat05, 2026-09-02, FLEET-16 mode.

## Terrain at claim time

P5 (`prolog-hot-services-by-ir-with-owning-slice`, the row meant to name which service to wire first) is **PARKED `BLOCKED-ON:prolog-term-to-descr-eradication`** — 0/21 van Roy kernels ran crash-free at seat06's last check (T9 big-bang mid-flight). This row is not blocked on P5 per its own text, so proceeded independently. Pulled fresh (SCRIP `c9e9473f→73bcbd5a`, 33 commits) before doing anything — the terrain had moved since P5's check: on the fresh build, **3 of 21 van Roy kernels now run crash-free** (`deriv`, `fib`, `tak`; `nrev`/`nreverse` still fail — pre-existing stack-smashing/trail-corruption, reproduced identically with the change stashed out, not this row's doing). All three are output-exact against a freshly-invoked real `swipl` oracle (via `prelude_swipl.pl`) and against the pre-existing `.expected` files.

## The cited line numbers had already drifted (expected under FLEET-16, 16 concurrent seats on this file)

`by_name_dispatch.c:5454/:5456` (the GOAL's citation) now land on unrelated code. Re-derived the real call graph instead of trusting the citation:
- `try_call_builtin_by_name`/`_bl` (bidlen mechanism, `builtin_ids.h`, STEP2/STEP3 fast path) — this is **SNOBOL4/Icon-only**. Confirmed by exhaustive grep: `builtin_ids.h` contains **zero** entries whose name starts with a bare `$` (SNOBOL4-internal names use `SNO$...`, never bare `$...`). Every Prolog-internal dispatch name (`$ax_*`, `$cmp_*`, `$dyn_*`, …) is therefore a **guaranteed miss** in `bid_of()` — the bidlen machinery structurally cannot help these names without first registering ~135 new entries in a shared emitter/runtime table (a materially bigger, riskier change than this row's own "wiring not design" framing invites).
- The actual Prolog `$`-name entry point is a **different, 2500-line function**, `script_try_call_builtin_by_name` (`:1688`–`:4229`) — a giant `strcmp`/`strncmp` cascade covering everything from `"where"`/`"seek"` to `"__rk_*"` to the Prolog `$`-names. `$ax_*` and `$cmp_*` are matched near its top (`:1753`, `:1762`) and forwarded verbatim: `return dop_ax(fn+4, args, nargs, out);` / `return dop_cmp(fn+5, args, nargs, out);`.
- `dop_ax`/`dop_cmp` (`:1327`, `:1415`) are plain `static` functions in the same file, already taking the bare suffix `rt_pl_ax_suffix()`/`rt_pl_cmp_suffix()` return. `plc_eval` (`:4544`,`:4554`) and `plc_det_exec`'s `case 'c'` (`:4565`) build `"$ax_%s"`/`"$cmp_%s"` via `snprintf` for the **sole purpose** of having `script_try_call_builtin_by_name` strip that exact prefix back off two lines later.

## The cure

Call `dop_ax`/`dop_cmp` directly with the suffix these three call sites already have in hand — no `snprintf`, no round trip through ~15–20 dead `strcmp`/`strncmp` checks. Hazard check (STEP1-style, matching `perf-dispatch-fastpath-name-indirect`'s precedent): both functions are pure w.r.t. `args`/`out`, always return 1 (Prolog-level failure signalled via `*out=FAILDESCR`, the exact convention the three call sites already check) — no `longjmp`, no allocation beyond what the callee already did identically today. No `rt_dtax_gen` gating needed: unlike SNOBOL4's OPSYN/DEFINE, nothing in Prolog can redefine what `"add"`/`"lt"` mean to `dop_ax`/`dop_cmp`. **Killswitch, no new global:** reused the pre-existing memoized `dtax_off()`/`SCRIP_DTAX_OFF` (STEP3's own escape hatch) rather than minting a second flag — documented inline as a deliberate scope extension of that flag's purpose. SCRIP diff: `src/runtime/by_name_dispatch.c`, three call sites, +21/−6 lines.

## Correctness

Byte-identical stdout, both the new default path and `SCRIP_DTAX_OFF=1`, vs. the pre-change (`git stash`) binary, on `deriv`/`fib`/`tak`/`nrev`(crashes identically before and after)/`nreverse`(same). All three working kernels independently re-verified output-exact against a fresh `swipl` invocation and the pre-existing `.expected` files.

## Measurement — and why it is small, honestly reported per the FACT RULE

`valgrind --tool=callgrind`, `RT_OPT=-O0`, mode-3, `setarch -R` (Ir is not reproducible without it — first pass without `setarch -R` showed a 43,577-Ir "regression" on `tak` that vanished to a 14-Ir *improvement* once ASLR was pinned; recorded as a live witness of RULES.md's own instrument-noise law, not silently corrected away). `git stash`-based A/B, both arms on a fresh `make pristine` (HQ-27).

| kernel | control Ir | treatment Ir | Δ | multiple (ref/ours) |
|---|---:|---:|---:|---:|
| fib(20) | 113,547,501 | 113,547,462 | −39 | 1.0000x |
| tak(18,12,6) | 380,691,081 | 380,691,067 | −14 | 1.0000x |

Killswitch (`SCRIP_DTAX_OFF=1` on the treatment binary) reproduces the **old code path and old output** exactly, but not the old binary's exact Ir count (fib +30,182 Ir, tak +33,503 Ir over true control) — it pays the new `dtax_off()` check at every call without recovering the round-trip savings, the same structural property STEP3's own killswitch has relative to a hypothetical pre-STEP3 binary. Noted rather than hidden.

**Why the win is this small — the actual finding, and the reason P5's "which service first" question matters:** `callgrind_annotate` on the treatment run shows `script_try_call_builtin_by_name` called **7 times total** across fib(20)'s entire ~114M-Ir execution (0.04%). The reason: `src/templates/bb/bb_call.cpp` (an **emitter** template, not the interpreter) already carries a direct-dispatch table — `{"$ax_add", …, rt_pl_dop_ax_add}` etc., 21 names (`$ax_add/sub/mul/div/idiv/mod`, `$cmp_lt/gt/le/ge/eq/ne`, `$is_v`, `$ix_g`, `$mkc`, `$def`, `$unify`, `$unify_lst`, `$trail_mark`, `$trail_unwind`, `$unwind_nothrow`) — that the lowering pass already resolves to a **literal x86 `call` to a known function address** for any clause body the compiler can see statically. `fib`/`tak`/`deriv` are exactly that shape (plain recursive predicates, no meta-call, no dynamic assert), so their arithmetic and comparisons were **already wired at compile time**, by prior work this row's own GOAL text did not know about. `plc_build`/`plc_eval`/`plc_det_exec` — the tree-walking solver this row's fix targets — is the fallback for goal shapes the lowering pass cannot resolve statically, and none of the three available crash-free witnesses substantially exercise that fallback.

**What is still genuinely by-name, unmeasured, and NOT this session's cure:** `rt_pl_det_builtin_target`'s ~99-entry table (`assert`/`retract`/`sort`/`functor`/`format`/`write`/…, `plc_det_exec` `case 'd'`, `:4571`) has **zero** `bb_call.cpp` coverage — confirmed by grep, none of its targets appear in that emitter table. This is the real remaining "resolved by name at run time" surface. It is cold in all three working van Roy kernels (none call assert/sort/format), so a real Ir measurement needs a different witness — none of the currently crash-free kernels serve; the natural next step is either finding/fixing one, or waiting on more van Roy kernels to clear the T9 big-bang (`nrev`, `meta_qsort`, `query` would be natural candidates once they stop crashing).

## Gates (fresh `make pristine`, HQ-27)

`make test` (SNOBOL4 blocking set, shared-node control arm) + `test_smoke_prolog.sh` + `test_smoke_icon.sh` — results appended below once the background run completes; not claiming DONE-WHEN until they read FAIL=0 / unmoved.

## Row disposition

Landed, small, correct, honestly-measured cure. Did **not** close the row: DONE-WHEN's own Ir-witness requirement is satisfiable today only at a magnitude too small to be the row's real deliverable, and the row's actual remaining scope (the 99-entry `case 'd'` table) needs a witness this session doesn't have. Rewrote `## NEXT` rather than claiming `done`, per "a corrected number IS a deliverable" — the corrected understanding of *where* the by-name cost actually lives is worth more than the 39 Ir cured today.
