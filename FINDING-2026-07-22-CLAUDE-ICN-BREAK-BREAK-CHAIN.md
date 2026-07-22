# FINDING 2026-07-22 — Icon `break break` (nested-loop break chain) lowering bug — FIXED

**Author:** Claude
**Area:** SCRIP Icon front-end / lowering (`src/lower/lower_icon.c`)
**Goal context:** GOAL-JCON-IN-SCRIP (get JCON's Icon compiler `jtran` to run under SCRIP, including self-host)
**Status:** Fix landed and verified; Icon corpus board unchanged (241 PASS / 20 FAIL / 32 XFAIL). A *separate*, still-open scan-register bug (below) continues to block the preprocessor self-host.

---

## 1. The bug (FIXED)

Icon's `break expr` transfers control out of the current loop and evaluates `expr` **in the enclosing loop's context**, so a chain of bare breaks — `break break`, `break break break`, … — exits that many nested loops. SCRIP lowered a `break` node by emitting `IR_GOTO cx->loop_exit` (the *current* loop's exit) and **ignored the child expression entirely**. Result: `break break` behaved exactly like `break` — it exited only the innermost loop, and control fell through into the enclosing loop, which then looped forever (or fell through incorrectly).

### Minimal reproducer (no co-expressions, no scanning)
```icon
procedure main()
    repeat {
        while 1 = 1 do {
            write("in while")
            break break
        }
        write("BUG: reached after inner while")
    }
    write("correct: exited repeat")
end
```
- **icont/iconx (oracle):** `in while` / `correct: exited repeat`
- **SCRIP (before fix):** `in while` / `BUG: reached after inner while` / … **infinite loop**

### AST shape
`icon_parse.c` (~line 173) parses `break` as `TT_LOOP_BREAK`, and if an expression follows it pushes that expression as a **child**. So `break break` is a `TT_LOOP_BREAK` whose `c[0]` is another `TT_LOOP_BREAK` (recursively for deeper chains). The lowering discarded `c[0]`.

## 2. The fix

`src/lower/lower_icon.c`:

1. **`icx_t` gains a loop-context stack** (memset-zero-initialized with the struct):
   ```c
   IR_t * loop_stk_exit[64]; IR_t * loop_stk_next[64]; int loop_sp;
   #define ICN_LOOP_STK_MAX 64
   ```
2. **Each loop body is bracketed by a push/pop** of the current `(loop_exit, loop_next)` — at all four loop-lowering sites: `lower_while`, `lower_until`, `lower_repeat`, and the bounded body in `lower_every` (push only when a do-body exists). `cx->loop_exit`/`loop_next` keep their existing meaning ("current loop"); the stack records every enclosing level so the break site can reach outward.
3. **`case TT_LOOP_BREAK:` rewritten.** Walk the leading bare-break chain to get depth `k` (`break`=1, `break break`=2, …). If the chain is pure (no trailing non-break expr), jump to `loop_stk_exit[loop_sp - k]` — the exit of the k-th enclosing loop. If the innermost break carries a non-break expr (e.g. `break next`, `break <value>` — **not used by jtran**), lower that expr in the enclosing loop context (`loop_sp - 2`) then GOTO the current loop's exit as a best-effort fallback.

`AST field reminder:` `t->t` = tag, `t->n` = child count, `t->c[i]` = children.

## 3. Verification

Rebuilt `scrip` (lowering runs inside the compiler) and, for mode-4, recompiled the target. `break break` now matches the oracle across:
- **depth 1** (`break`), **depth 2** (`break break`), **depth 3** (`break break break`) — exits exactly the right number of loops and lands in the right place;
- **mode 3** (`scrip --run`) **and mode 4** (`scrip --compile` + link);
- **no regression** on the previously-working case-alternation reproducers (`caseAlt.icn` → `1/2/3 MATCH`) and the quote-scan idiom reproducers.
- **Icon corpus regression** (`scripts/test_icon_all_rungs.sh`, `--run`): **PASS=241 FAIL=20 XFAIL=32 TOTAL=293** — identical to the pre-change board.

## 4. Where it bites in jtran

`corpus/programs/icon/jcon-compiler/preprocessor.icn` (`preproc_scan_text`, string-literal / quote path, ~line 305) uses `break break` to exit both the inner `while tab(upto(iq))` and the enclosing `repeat` when it reaches a closing quote. Before this fix, `break break` there exited only the inner `while`, dropping into the `repeat` body's `suspend preproc_sync_lines(); suspend .&subject` — i.e. suspending from *inside* the repeat and (as a co-expression) re-scanning on resume. The fix makes `break break` exit correctly to the outer scan level.

---

## 5. SEPARATE, STILL-OPEN BUG — scan-register disturbance blocking preproc self-host

The `break break` fix did **not** by itself terminate `SCRIP-jtran preproc hw.icn : stdout`; it still loops, re-emitting the one line that contains a string literal. This is a **second, independent defect** (the one the jcon-compiler README calls "disturbs the scan registers").

### Ground-truth evidence (runtime scan-state trace, since removed)
Instrumenting `rt_scan_state_capture/apply/reset` (`gen_runtime.c`) and `scrip_coswitch` (`rt_coexpr.c`) with an env-guarded trace showed, on the producer (`preproc`) co-expression:
- working line `procedure main()` → captured `pos=10 depth=1 saved=0` (advances, completes, loop advances);
- looping line `   write("hello,` → captured **5362× always `pos=1 depth=1 saved=1`** — the scan never advances, and `saved=1` (a parked `scan_saved` entry) appears **only** for the line that goes through the `case move(1) of { "\"" | "'": … }` quote path.

The trace is **byte-identical before and after the `break break` fix**, confirming the two bugs are distinct.

### Isolation status (NOT yet minimally reproduced)
Nine reproducers (reproA–I, in `/tmp` during the session) each faithfully mirror pieces of the real path and **all work under SCRIP post-fix**, including: cross-co-expression scan isolation (verified correct — `&subject`/`&pos` *are* per-co-expression in SCRIP, matching the oracle); the quote-scan idiom (`case move(1)` + `"\"" | "'"` alternation label + `break break`) inside a suspending co-expression; the scan+suspend done in a *called* procedure (mirroring `preproc_scan_text`); reading lines from a *file* inside the scan; and an extra `suspend wrapper()` generator level (mirroring `preproc` → `suspend preprocessor(…)`). None reproduce the loop, so the full preprocessor has an additional trigger not yet captured.

### Leading hypothesis / next diagnostic
`saved=1` means one `rt_scan_leave` (push to `scan_saved`) without a matching `rt_scan_reenter` at suspend time, and `pos` is stuck at 1 — i.e. the active scan's cursor register is being reset. Candidates still to bisect: the `initial { interesting_chars := … }` static; the *present-but-untaken-for-hw.icn* recursive `value ? value := preproc_scan_text(…)` nested scan (line ~331) changing how the (recursive) procedure is compiled; or scan-register (r14 = δ cursor) corruption specific to the `case`-with-scanning-selector arm when the enclosing procedure is large/recursive. Recommended next step: add env-guarded tracing to `rt_scan_enter/leave/reenter` in `gen_runtime.c` and watch exactly where `scan_saved_depth` goes 0→1 and `pos` is reset for the write line in the *real* jtran run, then narrow a reproducer from there.

### Key source locations (for the next session)
- scan-state globals + `rt_scan_enter/leave/reenter`: `src/runtime/builtins/gen_runtime.c` (~lines 20–116)
- co-expression scan save/restore: `src/runtime/rt/rt_coexpr.c` `scrip_coswitch` (~lines 45–83; `first = target->alive` so `first=1`=resume, `first=0`=first activation)
- the offending Icon idiom: `preprocessor.icn` `preproc_scan_text` first branch (~lines 288–343), quote path ~298–320
