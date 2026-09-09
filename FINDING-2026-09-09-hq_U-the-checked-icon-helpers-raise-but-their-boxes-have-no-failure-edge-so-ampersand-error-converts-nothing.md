# The checked Icon helpers RAISE but their boxes have no FAILURE EDGE, so `&error` converts the error into neither an error nor a failure

**Measured 2026-09-09 by hq_U** · SCRIP `b29806e0`-merged tree · corpus `36d211ce1` · `RT_OPT=-O0` · incremental `make` · oracle `icont`/`iconx` v9.5.25a by absolute path.
**Found while landing** the scan-subject check (CEO-460, hq_U's Icon engine-class lane). **DIAGNOSIS ONLY — NO CURE. Pre-existing, and proven so on a control build.**

## The defect

Icon's `&error := 1` converts the next `&error` run-time errors into **expression failure**, setting `&errornumber`. SCRIP does this correctly for the arithmetic path and for nothing else that goes through a *checked helper*:

| witness (`&error := 1`) | `iconx` | SCRIP |
|---|---|---|
| `("a" + 1) \| write("failed: " \|\| &errornumber)` | `failed: 102` | `failed: 102` ✅ |
| `("ab" ? tab("x")) \| write("failed: " \|\| &errornumber)` | `failed: 101` | **nothing at all, rc=0** ⛔ |
| `(1 < ("a" to 5)) \| write("failed: " \|\| &errornumber)` | `failed: 101` | **nothing at all, rc=0** ⛔ |

⛔ **The shape is the worst one available:** the program neither reports the error nor takes the alternative. It exits 0 having silently skipped the expression — no diagnostic anywhere, and the `|` branch that exists precisely to handle the error never runs.

## Why arithmetic is right and the rest is wrong

`core_icn_error` (`src/runtime/core/core.c`) honours `g_error`: it decrements, records `&errornumber`/`&errortext`/`&errorvalue`, and `longjmp`s to `g_core_errjmp_stk[g_core_errjmp_n - 1]` **if a frame is installed**. Otherwise it **returns 1** and the caller carries on.

Exactly three places install that frame — `arithmetic.c`, `by_name_dispatch.c`, `runtime_eval.c` — each wrapping the operation in `setjmp` and returning `FAILDESCR` on the jump. **That is the whole population of `&error`-correct sites.**

The checked helpers install nothing:
- `core_icn_to_int_check` → `core_icn_to_int_d` **returns 0** after raising (`core.c:2466`).
- `core_icn_limit_count_check` **returns 0** after raising.
- `core_icn_argtype_check` **returns void** after raising.

⭐ **So the helper's contract is "raise", and its callers read the return value as if nothing happened.** With `&error` unset the `exit(1)` inside `core_icn_error` hides this completely — which is why the family has shipped this way and why only an `&error` probe finds it.

## Why it is a BOX problem and not a helper problem

The three correct sites all return a `DESCR_t`, so `FAILDESCR` is expressible. The checked helpers are called from **Byrd boxes** (`bb_scan_tab.cpp`, `bb_scan_move.cpp`, the range boxes, and now `bb_gen_scan.cpp` via `rt_scan_enter`), whose failure is not a value but the **ω edge**. A box cannot return `FAILDESCR`; it must *jump*. So the cure is an emitted conditional to ω after the checked call — an emit-level change across every box in the family, not a runtime edit.

⛔ **This is why I did not fold it into the scan-subject landing.** `rt_scan_enter` returns `ScanSubjRegs` (a pointer/length pair) and has no way to express failure at all; giving it one means giving `bb_gen_scan` a failure edge, which is the same change the other four boxes need. One row, five boxes, one shape.

## Proven pre-existing, not caused by the scan-subject cure

Built the tree with `rt_scan_enter`'s new `core_icn_argtype_check(lo, hi, 103)` **reverted** (`git stash`, full rebuild) and re-ran all three witnesses: **byte-identical output on both builds** — `err_tab` and `err_to` produce nothing on the cured and the uncured build alike; `err_plus` converts correctly on both. The scan-subject cure neither introduced nor worsened this.

⚠️ **And it does mean the scan-subject refusal inherits the family gap:** `&error := 1; [] ? write("in")` raises 103, `core_icn_error` absorbs it, and `rt_scan_enter` then installs the subject anyway. That arm is therefore **deliberately excluded from `test_gate_icn_scan_subject_must_be_string_convertible.sh`**, named in the gate's own summary line rather than pinned to our current behaviour — pinning it would make the leaderboard record our wrong answer as the expectation.

## The population a cure owes

`grep -n 'core_icn_.*_check' src/templates/bb/*.cpp` names the boxes. Today: `bb_scan_tab.cpp`, `bb_scan_move.cpp`, the `IR_TO`/`IR_TO_BY` range boxes (via the operand contract landed at `2197495bc`), `IR_LIMIT`, and `bb_gen_scan.cpp`. Each needs the same conditional-to-ω after the checked call, and each needs an `&error` witness — the arm nothing in the tree currently has.

## NOT CLAIMED

The three `setjmp` sites are named from a grep, not from a reachability proof — there may be a fourth. `&errorlimit`/`&errorvalue` behaviour past the first conversion is **not** probed. Whether `runtime_eval.c`'s frame incidentally covers some box path was **not** measured; the witnesses say it does not cover `tab` or `to`, which is all I checked.
