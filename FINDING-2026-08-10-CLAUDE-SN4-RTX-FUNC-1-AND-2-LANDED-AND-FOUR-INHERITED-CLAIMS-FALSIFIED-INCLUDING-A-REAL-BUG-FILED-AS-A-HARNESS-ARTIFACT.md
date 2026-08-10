# FINDING 2026-08-10 — RTX-FUNC-1 + RTX-FUNC-2 LANDED (both C crossings off the DEFINE hot path), AND FOUR INHERITED CLAIMS FALSIFIED — ONE OF THEM HIDING A REAL BUG INSIDE A "KNOWN HARMLESS" BUCKET

SCRIP `5416ed56`.  Seat: GOAL-SNOBOL4-RTX, RTX-FUNC ladder.  m3 AB=1, RT_OPT=-O0.

## 1. WHAT LANDED

**RTX-FUNC-1** — `rt_ab_enter_env`'s five operations emitted inline at α (Σ/Σlen snapshot, wn snapshot-and-clear, vtmark from `g_pl_trail.top`, `rt_k_level++`, `kw_fnclevel`).  Emitted `call rt_ab_enter_env` → **0**, which is the rung's own stated acceptance.

**RTX-FUNC-2** — `rt_ab_leave_env` guarded fast path at the RETURN/NRETURN landing.  Both guards are **proven no-op conditions read out of the C**, not heuristics:
- `g_pl_trail.top == [rbp+AB_OFF_VTMARK]` ⇒ `rt_value_trail_tidy_dead_window` is structurally nothing: its loop is `for (r = mark; r < top; r++)` which never iterates when `mark == top`, and its only store is then `top = w = mark`, rewriting the value already there.
- `rt_g_ret_by_name == 0` ⇒ `rt_nret_fix` (rt.c:755) collapses to `rt_g_want_name = wn; return r`.

Either guard failing takes the untouched C call, so the C body stays fallback **and** bisection oracle per ARCH ruling 3.  This is the 0(f-pre) shape: falsifiability knowable from the source before the asm exists.

`x86_asm.h` **untouched** (NOT-CONCURRENCY-SAFE) — every instruction through existing `x86()` arms.

## 2. MEASURED — like-for-like, min-of-7, control from a FRESHNESS-VERIFIED pristine build

| bench | pristine | ported | Δ | SPITBOL | ratio before → after |
|---|---|---|---|---|---|
| func_call | 1500 | **1299** | −13.4% | 1514 | 1.01× → **1.17×** |
| func_call_overhead | 1529 | **1274** | −16.7% | 1472 | 0.96× → **1.16×** |
| fibonacci | 409 | **360** | −12.0% | 234 | 0.57× → **0.65×** |

⚠ The control was verified pristine by checking the **emitted `.s` for the RTX-FUNC-1 marker**, not by trusting `make`.  Twice this session a rebuild reported success while the tree was not in the state I believed: once because a 3 s build looked too fast to be real (it was real), and once because I ran `git stash` on an already-committed tree, so the "pristine" arm was my own port measured twice.  **The marker check caught the second one; nothing else would have.**  Stale-build is this project's documented trap and the instrument against it must be the artifact, never the build log.

## 3. ⭐⭐ fibonacci's RESIDUAL GAP IS ARITHMETIC, NOT CALL PROTOCOL — THE DIRECTIVE'S MODEL OF IT IS FALSIFIED

The Lon directive models `fibonacci` as "same cost × recursion depth" and predicts it "follows proportionally" once the call path is fixed.  With **both** crossings gone it moved only 409→360 and sits at 0.65×, short of the 0.80× acceptance.  Emitted-call census on `fibonacci.s` at HEAD+port:

`rt_flat_ret_snap` ×6 · `rt_sub` ×5 · `str_concat_d` ×4 · `rt_coerce_num2_d` ×4 · `rt_call_arr` ×4 · `rt_cmp_d` ×2 · `rt_add` ×2

⇒ what remains per activation is **ARITH + `rt_flat_ret_snap`**, i.e. RTX-6 territory, not RTX-FUNC.  **RTX-FUNC cannot deliver fibonacci ≥0.80× and no further work on this ladder should be justified by that number.**  RTX-6's own row already records the honest floor it must beat (`arith_loop` 0.64×, `arith_mixed` 0.80×) and the free ~11.3 ns/call from the `rt_<op>`→`rt_num_arith` hop.

## 4. FOUR INHERITED CLAIMS FALSIFIED

**(a) RTX-FUNC-3's prescription is backwards, and it is the m4-breaking direction.**  The rung says promote `rt_value_trail_mark` to `visibility("hidden")` and inline as `[rip+sym]`.  For any symbol EMITTED CODE must reach, hidden is the **disqualifier**: hidden ⇒ absent from `libscrip_rt.so`'s `.dynsym` ⇒ m4 link failure.  That is the `g_cap_gen` class ARCH already records (173/316).  Verified: `rt_k_level` is `HIDDEN` and **absent from dynsym**; the other five globals are DEFAULT and present.  The rung's premise that `rt_k_level` *and* `kw_fnclevel` are "already hidden (rt.c:396)" is half wrong — `kw_fnclevel` is DEFAULT and lives in `core.o`.  RTX-FUNC-3 is DISCHARGED with correction: `g_pl_trail` was already reachable, no promotion was ever needed.

**(b) …AND THE OPPOSITE FIX IS ALSO WRONG — THE TWO CONSTRAINTS ARE OPPOSED.**  Promoting `rt_k_level` to DEFAULT fails the `.so` link outright: `relocation R_X86_64_PC32 against symbol rt_k_level can not be used when making a shared object`.  `rtx_call.S`/`rtx_plcall.S` reach it with direct PC32, legal only while non-preemptible.  **Its hidden visibility is load-bearing for the runtime's own asm.**  Resolution: cell stays hidden; new exported `int * const rt_k_level_p` carries it across the boundary; emitted code pays one extra load, both media identical.  ⚠ A future seat reading the rung will try promotion first, as I did — the failure is instant and loud, but the *reason* is not guessable from the rung text.

**(c) ARCH §7 step 0(c) ROUTES YOU TO AN INSTRUMENT THAT CANNOT ANSWER ITS OWN QUESTION.**  It orders `nm` on the **object file** (correct, and for good reason) then infers "capital `B`/`D` ⇒ exported ⇒ preemptible ⇒ `@GOTPCREL`".  **That inference is invalid on a `.o`:** a `visibility("hidden")` global prints capital `D` there exactly like a default-visibility one, because the letter encodes *linkability*, not *visibility*.  My first pass read all seven globals as exported and was wrong about `rt_k_level`.  The instrument that separates them is `readelf -sW` (BIND + VIS columns), or `readelf --dyn-syms` on the `.so` for the question that actually matters ("can emitted code name this?").  ⭐ Same "two things identical through the instrument you happened to pick" class the doc keeps warning about — one level further down, and this time **inside the check written to prevent it.**  PROPOSED AMENDMENT: step 0(c) reads `readelf -sW <obj>` for BIND+VIS, and `readelf --dyn-syms <.so>` for emitted-code reach.

**(d) ⛔⛔ A REAL BUG WAS FILED AS A HARNESS ARTIFACT.**  The prior cursor records "9 DEFINE-bearing corpus programs mismatch `.ref` **identically in both arms** = harness artifact, not a regression."  Measured: **8 of the 9 are arms-identical; `roman.sno` is NOT.**  Under AB=1 it prints `1I`, `2II`, `3III` — the Roman numerals are CORRECT and the caller's statement literal `' -> '` is **destroyed**.  Under AB=0 and in the `.ref`: `1 -> I`.  Proven **PRE-EXISTING** against a true pristine control (parent commit restored to `src/`, marker check 0), so it is not from this port — but it is a live AB-path defect, not a harness artifact, and the arms-identical criterion the cursor itself supplies is what distinguishes them.  ⭐ **The bucket was right about 8 and wrong about 1, and being in the bucket is why nobody looked.**  This is also direct corroboration of the s_this+1 seat's falsified claim (a): *"the damage is everything live across the call, not save-set-shaped"* — that defect is STILL LIVE at HEAD, which contradicts the s_this+2 cursor's "BOTH REMAINING REDS CLOSED".  `roman.sno` is now the cheap 3-line repro for it.

## 5. ⭐ THIRD INSTANCE OF THE SILENT-DROP CLASS IN ONE FILE — AND THE FIX WAS APPLIED PER-MNEMONIC

`x86("sub", RDD(base,off), imm)` has **no `XK_REGDISP32`/`XK_IMM` dispatch arm** and returns the **empty string**.  My β fast path used it for `rt_k_level--`; the decrement vanished from BOTH media.  The benchmarks stayed oracle-exact throughout — only the `&FNCLEVEL` witness caught it (`0/1/2,3/3` instead of `0/1/1,2/0`).

This is the **third** instance in this one file's history: `x86("leave")` (prior seat, no arm at all), `x86("mov", RDD, imm)` (2026-07-08, documented in `x86_asm.h`'s own comment), now `x86("sub", RDD, imm)`.  ⭐⭐ **`mov` and `cmp` were each given loud bombs AFTER their own incident; `sub` still falls through silently.  The remedy has been applied per-mnemonic, so the class keeps recurring in whichever mnemonic has not been bitten yet.**  `add` happens to HAVE the arm, which is exactly why α worked and β did not.  PROPOSED: a family-wide fall-through bomb, or a build-time assert that every dispatcher's tail aborts.  Worked around here without touching `x86_asm.h` (register round-trip, proven arms only).

⭐ The accidental bug doubles as the 0(f) proof the fast arm **executes**: had the slow C arm been taken, `rt_ab_leave_env` would have decremented correctly and `&FNCLEVEL` would have been right.  It was wrong ⇒ the fast arm ran.

## 6. FALSIFICATION PROBE OF RECORD — `kwitness.sno`

`&FNCLEVEL` is `kw_fnclevel`, the cell α now writes.  m3 AB=1 → `0 / 1 / 1,2 / 0`, **byte-identical to the SPITBOL oracle**.  m3 AB=0 → `0 / 0 / 0,0 / 0`.  The arms differ ⇒ **not vacuous** (ARCH §7 0(f)).  ⭐ Side finding: **the legacy AB=0 path never maintained `&FNCLEVEL` at all** — a pre-existing defect no existing test covers, since no corpus program reads the keyword inside a function.

## 7. m4 AB=1 STILL SEGVs — PRE-EXISTING, PROVEN, AND THE PRIOR CURSOR'S "UNBLOCKED" IS FALSIFIED

m4 AB=1 SEGVs on both `fibonacci` and the witness; assembly and link are **clean** (empty `as`/`ld` stderr) so it is purely runtime.  m4 AB=0 is GREEN (`fibonacci` → 832040).  Proven pre-existing by pristine control.  The s_this+2 cursor claimed the `leave` fix made m4 AB=1 "now unblocked — the teardown was why it SEGV'd"; **it is not unblocked and was never run.**  ⚠ This keeps m4 unavailable as the both-medium oracle, which matters more now than before: RTX-FUNC-1/-2 are the FIRST emitted code in this template to reach runtime globals directly, i.e. exactly the exported/hidden data-symbol class mode 3 is structurally blind to.  The TEXT side is verified only by **emission inspection** (GOTPCREL forms present, `call rt_ab_enter_env` = 0), never by execution.

## 8. OWED

- **m4 AB=1 SEGV** — now the top blocker for this ladder; it gates the both-medium proof of these two rungs.  No gdb in this container.
- **`roman.sno` live-across-call literal destruction** (§4d) — real defect, cheap repro, wrongly bucketed.
- Kill-switch CALL gate N≥4 both modes; full crosscheck at watermark; `.s` regen ×3 (**now genuinely owed by this seat** — templates changed, unlike phase-1 rungs).
- RTX-FUNC-4/-5 untouched.  ⛔ RTX-FUNC-5's target (`fibonacci` ≥0.80×) is **unreachable on this ladder** per §3 — re-scope it or route it to RTX-6.

`handoff_status.sh` is the push truth — NOT this document.
