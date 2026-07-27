# FINDING-2026-07-27c — SN4-RTX-4 SLICE 2: the slim landings in asm, the slice-1 debt discharged, and a THIRD member of the vacuous-evidence family

**Session s187 (2026-07-27, Claude + Lon).** RTX **UNPARKED** by Lon directive (*"Replace SCRIP SNOBOL4 runtime C with asm. Continue."*), parked since s171.
**SCRIP commits:** `881ea03d` (slice 2), `f1262de7` (gate default ON).
**Watermark, re-proven live at session start BEFORE any edit: m3 314/1 · m4 312/1 · DIVERGE=0**, single fail `test_case` both modes. Held at every gate below.

---

## 1. THE OWED DEBT, DISCHARGED FIRST — AND IT PAID FOR ITSELF

s186 landed slice 1's canary and then said, correctly and against its own interest, that **ON==OFF proves nothing**: it is exactly what a gate that never engages also looks like. It named the falsification probe as *the first act of the next session*. That was done before anything else was touched:

| build | gate | m3 | m4 |
|---|---|---|---|
| broken classic asm | **ON** | 310/5 | 308/5 |
| broken classic asm | **OFF** | 314/1 | 312/1 = watermark |

The asm executes; the switch switches. **And the probe repaid its cost immediately** — it independently re-derived the coverage set as *exactly* the four EVAL/defer programs s186 named (`expr_eval`, `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno`, `161_pat_defer_fn_nested_match`), from the tree rather than from prose. Two sessions had now asserted that set; this is the first time it was **measured**.

---

## 2. ⭐⭐ THE NEW LESSON: A BREAK THAT IS A NO-OP IS NOT A PROBE

Slice 2 ports **two** landings, γ and ω. Breaking γ moved 18 programs — done, proven. The obvious symmetric break for ω was to make it return `DT_FAIL`.

**That break would have proven exactly nothing, and it would have LOOKED like a clean pass.** `rt_proc_call_epilogue_slim_ω` is the FRETURN landing: it already returns `FAILDESCR`. Forcing `DT_FAIL` there is a **no-op**. The battery would have sat at 314/1, and the honest-looking reading of that — "ω isn't reached by any corpus program" — would have been **false**, and would have shipped an unexercised asm landing under a green board.

The break has to **invert** the meaning, not merely corrupt it: returning `DT_SNUL` makes FRETURN signal *success*. Then:

| landing | break | m3 | movers |
|---|---|---|---|
| slim γ | result → DT_FAIL | 296/19 | **18** |
| slim ω | FRETURN → DT_SNUL (inverted) | 310/5 | **4** |

Both landings are independently exercised. ω is real.

**⚠ THIS IS THE THIRD MEMBER OF ONE FAMILY, AND IT SHOULD BE NAMED AS A FAMILY:**
- **s184** — the FC gate scored a *failed compile* as a clean 0.
- **s186** — `expr_eval` reads stdin; run without `< expr_eval.input` it emits ZERO bytes and the comparison passes **vacuously**.
- **s187 (this)** — a falsification break that is semantically a **no-op at the site it breaks**.

The common shape is not "the test was wrong." It is: **the instrument was incapable of registering the failure it was pointed at, and incapability is indistinguishable from success in the output.** Hence the standing check, which costs seconds:
> **Before quoting any probe, state what the output would look like if the thing under test did not exist at all. If that is the same as the passing output, the probe is vacuous — redesign it before quoting it.**

For a falsification break specifically: **verify the break changes the function's OBSERVABLE CONTRACT, not just its instructions.** At a landing whose whole job is to return a constant, only an inversion qualifies.

---

## 3. THE RUNG'S FLAGGED PRINCIPAL RISK WAS ALREADY SOLVED — BY SLICE 1, IN SHIPPING CODE

s186 flagged `(char *)__builtin_frame_address(0) + 16` as "the rung's principal risk," to be *measured, never guessed*, on the grounds that the asm has a different frame than the -O0 C.

**The premise is true and the conclusion does not follow.** The bound is not frame-*size* dependent. Under the standard prologue (`push rbp; mov rbp,rsp`) gcc's `__builtin_frame_address(0)` **is** rbp, and `[rbp+0]`=saved rbp, `[rbp+8]`=return address, so **`rbp+16` is the caller's rsp immediately before its `call`** — the first byte above this activation, no matter what `sub rsp,N` follows. `lea rdx,[rbp+16]` is byte-exact for any frame size.

Slice 1 has shipped exactly that since s165, with the reasoning written in its own header comment (`rtx_call.S:78-80`) — **the answer was already in the tree while the cursor was calling it an open risk.** What was genuinely missing was proof that the code *runs*, and §1's probe supplies it: the tidy call fed by that very `lea` executes on all four covering programs, which still match their oracles.

**Transferable:** s186's own rule was *"a comment about a field's value is evidence about the moment it was written, never the moment it is read."* Its dual is now also earned: **a risk recorded in a cursor is a claim about the moment it was written, too.** Re-read the implementation before re-litigating a flagged risk; the previous slice may have retired it and only told the source file.

---

## 4. NEW HAZARD — THE LINKAGE SPLIT, WHICH SLICE 1 STRUCTURALLY COULD NOT MEET

Slice 2's landings are **self-contained** (no `rt_proc_epilogue_body` call), which is what makes them the better target — and it is also what exposes a hazard slice 1 was immune to. Slice 1 never touched `Σ`, `Σlen`, or `g_monitor_bin` because they live *inside* the body it calls. A self-contained port must reach them directly, and:

| symbol | `nm` | linkage | asm form |
|---|---|---|---|
| `Σ`, `Σlen`, `g_monitor_bin` | **`B`** | exported ⇒ **preemptible** | **`[rip + sym@GOTPCREL]`** |
| `g_pcall`, `g_pcall_top`, `rt_k_level` | `b`/`d` | hidden ⇒ linker-localised in the `.so` | `[rip + sym]` direct |

This is the identical failure class RTX-2 hit on `g_hp_fr`. It is a **link error, not a silent bug** — but only because the split was checked with `nm` instead of inferred from the C, where all six look alike. **Add the `nm` linkage check to §7 step 0 for any self-contained port.**

---

## 5. LINE NUMBERS ROTTED AGAIN — AND THE FIX IS TO STOP CITING THEM

s186 corrected `rt_nret_fix` from `:598` to `:631` and warned that a `file:line` is a hint. Confirmed and extended: `rt_nret_fix` **held** at `:631`, but the slim landings are at **`rt.c:1156/1168`**, not where s186's prose implied, and `rt.c` is now **1734** lines, not 1667.

Rather than correct numbers that will rot again, the baked facts are now **locked into the build**. `rt.c` carries `_Static_assert`s on `sizeof(rt_pcall_t)==64` and on `p/save_Σ/save_Σlen/wn/fb/vtmark`, plus `rt_proc_t.name==0` and `is_generator==0x4c`. **A layout change now fails the COMPILE instead of silently shearing `rtx_call.S`.** Offsets were measured with an `offsetof` probe, not hand-computed.

---

## 6. WHAT LANDED

**`rtx_call.S`** — `rt_proc_call_epilogue_slim_γ/ω` behind `rtx_gate_call`; C bodies → `c_*` same commit. The whole epilogue is subsumed: k_level, the pop (64-byte private copy as 4 SSE moves, not 16 scalar ops — the copy is **not** redundant, see slice 1's header), the tidy, the Σ restore, `rt_nret_fix`, the monitor event.
**`rt.c`** — `rt_nret_fix` de-`static`'d + hidden (the rung's sole named blocker; `rt_value_trail_tidy_dead_window` was already reachable, and s186's warning that the prereq list was incomplete was correct but not a blocker).

**SIZE (proxy only, `RT_OPT=-O0`, ⛔ NO SPEED CLAIM — no rail run):** slim γ **93 → 63** insns · slim ω **98 → 61**.

**GATES:** watermark held at default-ON *and* under `SCRIP_RTX_CALL=0` · kill-switch **byte-identical over all 315 programs** (md5 `47a7895e1ab57293b9dd7a3a05f1cdc7`, both arms same sweep method — **not** comparable to the s163/s164 hash, the tree has moved) · RTX unit 21/21 + alloc 36/36 + str 8404/0 · smokes 7/7×2 · Prolog 189/0 · Icon 4/0 · Snocone 8/0.
⚠ **The three cross-language batteries are NO-REGRESSION evidence for the shared `rt.c` edit ONLY. They do not move under the probe and citing them as asm evidence would be a false claim** (ARCH §7 step 2b).
✅ **Zero template/emitter edits — `.s` regen not owed by construction**, and the emitted call site is unchanged: the template still calls `rt_proc_call_epilogue_slim_γ` *by name*; the asm merely takes the symbol over. Concurrency-safe against the ζ ladder.

**GATE DEFAULT FLIPPED OFF → ON** (`f1262de7`). Per ARCH §4 (default ON once gates are green), now satisfied two-sided on both landings. Rationale worth keeping: **a gate that never opens gives the asm zero real exercise, so latent defects survive untouched until RTX-12 deletes the C fallback — i.e. they surface exactly when the safety net is gone.** Turning it on while `c_*` still exists and one env var reverts is the cheap moment to find them.

**⚠ RESIDUAL RISK, NAMED:** the monitor arm (`g_monitor_bin`) is **untaken in every battery** — the monitor has been dark since s158 — so the green board says *nothing* about that branch. It is a faithful transliteration including the C's **unguarded `c.p->name` deref**, which is asymmetric with the tidy arm two lines above that *does* guard `c.p`. MON-RE must re-gate this family.

---

## 7. NEXT

**RTX-4 SLICE 3 — the rest of the CALL surface:** `rt_proc_call_open(_slim)` · `rt_proc_open_fn` · `rt_call_arr` (**232 static refs, #1 in the whole runtime**) · `rt_call_named_proc` · `rt_arg_stage` + the proc_set family. `rt_call_arr` is the single biggest remaining lever and deserves its own slice.
**Then RTX-5 AGG.** ⛔ RTX-11/12 stay serialized with Lon (templates + `.s` regen ×3).
**Still owed by the family:** a CALL **differential unit battery**. MISC/ALLOC/STR each have one under `test_rtx_unit.sh`; CALL has none, so its evidence rests entirely on corpus movement. Building one needs a synthetic `g_pcall` record — fiddly but tractable, and it is the only way to reach the monitor branch while the monitor is dark.
