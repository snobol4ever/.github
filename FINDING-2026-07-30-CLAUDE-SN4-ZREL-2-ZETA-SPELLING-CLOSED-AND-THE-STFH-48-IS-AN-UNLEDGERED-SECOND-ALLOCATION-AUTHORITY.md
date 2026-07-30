# FINDING 2026-07-30 (s21x-q) — ZREL-2: the ζ-cell SPELLING retirement is CLOSED (44→41, all 41 classified NOT-ζ), and the STF defect is NOT a missing release arm — it is the stfh 48 carving OUTSIDE the grant, where `op_zdepth` cannot see it

**Session:** s21x-q. **Directive (Lon):** "Complete the ZETA CELLS on the RSP stack."
**Landed:** three sites converted to `x86_zclaim`/`x86_zrelease`, **byte-identical over 317 crosscheck programs** + all three `.s` regen scripts reporting zero changed artifacts.
**Watermark re-derived at start AND close — UNCHANGED.**

---

## 1. WHAT LANDED (ZREL-2)

ZREL-1 (s21x-p) minted `x86_zclaim`/`x86_zrelease` and converted 9 sites. ZREL-2 finishes the sweep:

| File | Site | Was | Now | Role |
|---|---|---|---|---|
| `bb_match_head.cpp` | ~40 | `x86("sub","rsp",(long)32)` | `x86_zclaim(32)` | FORTH-cell window carve, non-RSP arm (`hfc()`) |
| `bb_match_head.cpp` | ~54 | `x86("sub","rsp",(long)32)` | `x86_zclaim(32)` | FORTH-cell window carve, RSP arm (`hfc()`) |
| `bb_match_defer.cpp` | ~168 | `x86("add","rsp",(long)_.op_defer_leaf_susp)` | `x86_zrelease((long)_.op_defer_leaf_susp)` | ε-resume zero-guard leaf SUSP pop |

`x86_zclaim(b)` is literally `x86("sub","rsp",b)`, so this is an exact spelling retirement — proven, not assumed:
**317/317 `--compile` artifacts byte-identical**, and `util_regen_{benchmark,feature,demo}_s_artifacts.sh` all committed nothing.

## 2. ⭐ THE CLOSING LEDGER — the remaining 41 are ALL NOT-ζ (this closes the directive)

The census went 44 → 41. **Every one of the 41 is classified not-a-ζ-cell**, so the sweep is CLOSED, not merely paused. Do not "finish" it by converting these — naming them ζ would lie (ZREL-1's own words).

| File | N | Class | Why it is not a ζ cell |
|---|---|---|---|
| `bb_match_capture` | 3 | CSTACK swap arm | `push zr; sub rsp,8` … `mov rsp,zr; add rsp,8; pop zr` — the 8 is C-ABI 16-align pad **paired with a register save**, and the whole arm is dead under the default (`zc_frame != RSP` only). |
| `bb_match_defer` | 3 | CSTACK swap arm (`!dswap()`) | identical shape |
| `bb_match_release` | 3 | CSTACK swap arm | identical shape |
| `bb_arith` | 1 | C-ABI alignment dance | ZREL-1 named this exclusion explicitly |
| `bb_call_proc_staged` | 9 | call frame dance / pcall record | law 7; the FUNCTION construct's own rung |
| `bb_glue_flat` | 2 | **THE GLUE PAIR** | role-distinct **by design**: glue brackets the box's OWN GRANTED cell (K = `op_fc_bytes`) at the ports; zclaim/zrelease are the MID-BODY verbs. Converting would erase a distinction the design draws deliberately. |
| `bb_glue_framed` | 1 | THE GLUE PAIR | as above |
| `bb_match_arbno` | 10 | ARBNO housekeeping | one of the four RBP constructs; the ARBNO rung (variable-extent anchor) rewrites this file |
| `xa_flat` | 9 | prologue / frame establishment + ICNBENCH C-ABI align | not mid-body cells |

**LAW (new, cheap to check):** the ζ-spelling gate is not "zero `rsp` in templates" — it is "**zero rsp in templates that is a mid-body cell**". The four legitimate raw-rsp classes are: GLUE (granted cell), C-ABI ALIGN, CSTACK SWAP ARM, PROLOGUE. A future site outside those four is a defect.

## 3. ⭐⭐ THE STF DEFECT, RE-DIAGNOSED — s21x-p's characterization is HALF RIGHT and the half that is wrong is the actionable half

s21x-p wrote: *"`bb_match_release` never got the matching arm — its fixed `[rsp+16/24/32/96/120]` head-cell reads land inside the bracket slots."*

**MEASURED AT HEAD, THIS IS NOT WHAT THE SOURCE SAYS.** `bb_match_release.cpp` **already** carries `#define stfh() (_.flat_stmt_frame)` and its own `HKQ(k)` = `qword ptr [rbp + (-48+8k)]`, and it **already** reads all five head fields through it (lines ~73/74/75/78/80: r13←HKQ(1), r14←HKQ(2), r15←HKQ(3), rdx←HKQ(4), rbp←HKQ(0)). The five-field bracket map **is welded on both sides.** A session that goes looking for "the missing release arm" will find it already there and burn the budget.

**THE REAL MECHANISM — one level deeper, and it is structural:**

1. `x86_frame_off(off)` (x86_asm.h:373) compensates rsp-based refs as `off + _.op_flat_disp + _.op_zdepth`.
2. `op_zdepth` is set at exactly ONE place — `emit.cpp:820`: `g_emit.op_zdepth = x86_fc_on() ? (int)g_emit.op_fc_bytes : 0;` — i.e. **the box's GRANTED extent, and nothing else.**
3. `IR_MATCH_HEAD` is **excluded by kind** from the universal carve (`emit.cpp:811` — the four-construct family HEAD/FENCE1/SAVE_RESTORE/CALL, "self-managed windows and the frame dance"), so its `op_fc_bytes` is never set by that path ⇒ **`op_zdepth` = 0 for the head.**
4. But under `stfh()`, `bb_match_head.cpp:32` fires **`x86_zclaim(48)`** — a self-managed window **outside the grant**.
5. ⇒ The 48 bytes move rsp while being **structurally invisible to every `[rsp+off]` reference in the statement.** Non-HKQ refs (`FRQ(_.op_off + 8/16/24)`, live in BOTH head and release) are displaced by exactly 48.

This is not a new law — it is **emit.cpp:808's own law firing**: *"a BB may be armed once ALL of its consumers speak the live-depth authority (ZTOS/op_zdepth); arming it while a consumer still speaks the static authority (FRQ/op_flat_disp) displaces that consumer by exactly the new carve."* The head's stfh carve **is** such an arming. It is the s21x-o root cause ("allocator and operand address were two authorities that could not see each other") reappearing one level out, in the one kind that was excluded from the ledger precisely because it is "self-managed".

**Why `n7_match_release_α` is byte-identical between regimes** (s21x-p's own static proof, now explained): release's rsp-based reads compensate by `op_flat_disp + op_zdepth`, and BOTH are regime-invariant for this kind — `op_zdepth` is 0 either way because the 48 never entered `op_fc_bytes`. The reads did not "fail to learn about the carve"; **there was nothing in the ledger for them to learn.**

## 4. THE WELD, RESPECIFIED (next rung — do this, not the missing-arm hunt)

Per s21x-c law 1 ("ONE instruction: `sub rsp, K`") and Lon's roman directive ("There should be ONE RSP decrement"), the 48 should **not be a second self-managed carve at all**:

> **Move the head's 48 into the STATEMENT's framed-glue grant** — `bb_glue_framed_enter` at **K=48** instead of K=0 — so it is ledgered once through the same `op_fc_bytes` the accessor already reads via `op_zdepth`, addressed through rbp exactly as `HKQ` already does, and released by the matching glue leave.

One decrement · one authority · one predicate (`stfh`) · one layout map (`[rbp−48+8k]`). GLUE-4 already wired STATEMENT as the framed glue's first customer at K=0, so this is a K change plus deleting the `x86_zclaim(48)` at `bb_match_head.cpp:32` — **not** new machinery.

⚠ **VERIFY WITH THE MONITOR, NOT BY READING** (RULES monitor-first): the gated regime heap-exhausts (`rt_dcap_pump` on garbage), so the reproducer is s21x-p's 5-line probe (`DEFINE('F(N)T')` + capture match + one call; oracle `"A"`) under `SCRIP_STMT_FRAME=1`, bracketed by `test_monitor_2way_sync_step_bin.sh`. Commit the probe into corpus with its ref in the same slice.

## 5. WATERMARK — re-derived at START and CLOSE, UNCHANGED

| Arm | Start of s21x-q | Close of s21x-q | Recorded (s21x-p) |
|---|---|---|---|
| m3 `--run` | 265/51 | **264/52** | 264/52 *(±1 flap, documented)* |
| m4 `--compile` | **264/50 SKIP=2** | **264/50 SKIP=2** | 264/50/2 — **EXACT** |
| DIVERGE | 3 | 3 | 3 |
| killswitch `SCRIP_BB_ALLOC=0` | — | **m3 312/4 · m4 312/2/2 · DIV=2** | EXACT |

⭐ **DIVERGE MEMBERSHIP CAPTURED** (s21x-p closed with "membership not re-captured — re-derive"; it is now derived):
**{`140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`, `W04_arbno_basic`}**.
Killswitch DIV=2 = {140, 141} — so **`W04_arbno_basic` is the one divergence the killswitch removes**, i.e. it is allocator-induced, unlike 140/141 which survive into the killswitch baseline. That is a free bisect hint for the residual-spine rung (NEXT 4) and it is not recorded anywhere prior.

## 6. HONEST LIMITS OF THIS SESSION

- The weld itself is **NOT landed** — only respecified. §4 is a design claim derived from reading `emit.cpp:811/820` + `x86_asm.h:373` + `bb_match_head.cpp:32`; it has **not** been confirmed by running the gated regime under the monitor. Treat it as the strongest available hypothesis with a named falsifier, not as a measured fact.
- ZREL-2's byte-identity is measured (317/317 + three regen scripts). The §2 ledger is a **classification**, i.e. a judgement about intent per site, and is reviewable — the four legitimate classes are the reviewable claim.
- The SPITBOL manual was not available this session (upload did not attach), so no construct's semantics were checked against it. Nothing in ZREL-2 is semantic — it is a pure spelling retirement — but §4's weld touches the match family's storage protocol and **should** be checked against the manual's Ch.18 scan/unwind text before landing.
