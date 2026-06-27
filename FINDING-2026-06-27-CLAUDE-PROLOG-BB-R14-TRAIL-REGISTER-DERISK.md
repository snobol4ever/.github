# FINDING — PL-AREAS R14=TR de-risk PASSED; representation resolved; atomic wiring is a fresh-session job

**Session:** 2026-06-27 · Claude (3rd dev) · GOAL-PROLOG-BB · PL-AREAS-2 (R14 register-residency, the deferred half)
**Outcome:** the global-register-variable mechanism for putting the trail TOP in R14 is **proven in isolation** and `-ffixed-r14` is **proven benign across the whole runtime + floor**. The open int-index-vs-pointer representation is **resolved (int-index first)**. The full wiring is a coherent **multi-part atomic change** deliberately NOT started this session (context budget + it invites a MONITOR-FIRST pass). **Nothing committed; tree clean.**

---

## 1. The register-CLASS question — R14 (callee-saved) is correct, R10 (caller-saved) is wrong. RESOLVED.

The question raised: since the trail helper must MODIFY the top (pushes happen in C, ~50 sites in `unification.c`), wouldn't a caller-saved register (R10) have the "right polarity"? **No** — the intuition points at the wrong boundary. There are two boundaries with opposite needs:

- **our-template ↔ our-C-helper** — the helper must modify the shared top and that modification must persist to the box. This is solved by the **global register variable + `-ffixed`** (it pins the register and overrides the ABI's automatic save/restore *within our code*), and is therefore **independent of caller/callee class**. R10 buys nothing here.
- **our-C-helper ↔ the libraries** (`GC_malloc`/`memcpy`/libc — called all through unification) — THIS boundary fixes the class. A **callee-saved** register (R13/R14/R15) is preserved by every library call automatically, so the trail top survives `GC_malloc` for free. A **caller-saved** register (R10) is *clobbered* by those calls — we'd have to spill/reload R10 around every `GC_malloc`, the exact overhead we are deleting.

This is also why the string languages carry Σ/δ/Δ in the callee-saved trio and survive `rt_*` calls. The trail is the one case that *additionally* needs the global register variable, because — uniquely — its helper modifies the top rather than only reading it. **Verdict: R14, callee-saved, + global register variable + `-ffixed-r14`.**

## 2. All-three-registers — R14 ready now; R13/R15 gated on PL-AREAS-4. RESOLVED.

Only **R14 (trail) is behavior-neutral to wire now**, because the trail *already has its reclamation* (mark/unwind) — moving the top into a register changes only WHERE it lives, not semantics. **R13 (heap)** and **R15 (env)** are different: their *win* is the reclamation, that reclamation is the escape-blocked PL-AREAS-4 work (see `FINDING-...-PL-AREAS-3B-ESCAPE.md`), and a bump-WITHOUT-reclamation **regresses** (PL-AREAS-0's neutral-to-harmful result). So R13/R15 land WITH PL-AREAS-4's escape-copy, never in isolation. The ratified all-three end state is unchanged; the sequencing is R14 → (PL-AREAS-4: R13+R15).

## 3. De-risk results — PROVEN (reversible; nothing committed).

- **`-ffixed-r14` is benign across the entire runtime AND holds the floor.** Rebuilt all 237 `libscrip_rt` TUs with `-ffixed-r14` (`.so` 18,603,240 vs baseline 18,602,368 bytes — an 872-byte delta from one fewer GP register at `-O0`; rc=0, only pre-existing `snobol4_error` warnings). Swapped it in: **smoke 5/5, rungs 115/115 in all three modes.** Reserving r14 from the C compiler's pool costs nothing measurable at `-O0`.
- **The global-register-variable mechanism works in isolation** — PASS at `-O0` and `-O2`, both properties the wiring depends on:
  1. **persist** — a C helper's `g_trail_top++` survives the return to its caller (the push-persists property).
  2. **libc-survive** — the value is intact after a `memset` call (the callee-saved property; 10 `r14` refs in the emitted asm confirm GCC genuinely pins it to r14, not a relocated stand-in). This is the empirical proof of §1: R14 survives the library call *because* it is callee-saved.

  De-risk source (recreate in seconds; do NOT need to keep):
  ```c
  register long g_trail_top asm("r14");
  __attribute__((noinline)) void helper_push(int n){ for(int i=0;i<n;i++) g_trail_top++; }
  __attribute__((noinline)) long helper_with_libc(void){ char b[128]; memset(b,0,sizeof b); volatile long s=g_trail_top; return s; }
  int main(void){ g_trail_top=0; helper_push(5); if(g_trail_top!=5) return 1;
                  long a=helper_with_libc(); if(a!=5||g_trail_top!=5) return 1;
                  printf("PASS persist=5 libc-survive=%ld\n", g_trail_top); return 0; }
  /* gcc -O0 -ffixed-r14 ... && gcc -O2 -ffixed-r14 ...  → both PASS */
  ```

## 4. The mode-3 atomicity finding (why this is multi-part, not a one-file edit).

`resolution.c`, `unification.c`, `rt_runtime.c` all include `pl_cell.h` (where the trail lives) and are linked into **BOTH** the compiler binary `scrip` (mode-3, in-process) **and** `libscrip_rt.so` (mode-4). So:
- `-ffixed-r14` + the global register variable must apply to those TUs in **both** builds (not just the `.so`).
- The mode-3 slab entry (`bb_query_frame` α) must **bracket r14** (`push r14` on entry / `pop r14` on exit) so the host compiler's r14 survives the jump into emitted code, AND establish `r14 = trail top` inside the slab. (Mode-4 is a standalone binary — preamble setup only, no host to preserve.)
- The trail is **lazily mmap'd on first push**, so at slab entry `area.base` may be NULL → the preamble must force the trail's allocation (or fold a `rt_trail_ensure` into init) before loading the top into r14.

These parts must land **together** to stay behavior-neutral; a half-wired ABI change is worse than none.

## 5. Representation — RESOLVED: int-index first (frozen ABI), pointer is a later non-neutral optimization.

The frozen constraint (PL-AREAS-2): the MARK saved in the choice-box frame cells and the `rt_trail_mark`/`rt_trail_unwind` ABI is a **32-bit int INDEX**.
- **DO FIRST — r14 = int index, base stays in memory.** `mark = (read r14)` — int index, **ABI byte-for-byte unchanged, zero choice-box change**. push/unwind still load `area.base` from memory for the indexed `ents[r14]` access, but the moving `top` is now register-resident (saves its load/store per op). Behavior-neutral. This is the correct first step.
- **LATER (separate, non-neutral rung) — r14 = pointer** (`base + index*stride`): a full register bump (`mov [r14]; add r14,stride`, no base load) — bigger per-push win, but `mark` becomes `(r14-base)/stride` (a divide, since `sizeof(pl_trail_ent_t)`≈24 isn't a shift) or a byte-offset that **changes the meaning of the choice-box mark cell** and `rt_trail_unwind`'s loop. Touches `bb_cell_choice`; do it only if profiling shows the base-load is hot, and gate it as its own non-neutral rung.

## 6. Atomic wiring plan for the dedicated next session (MONITOR-on-standby).

1. Global register variable `register long g_pl_trail_top asm("r14")` in a **runtime-only header** included by the three TUs (NOT in `pl_cell.h` broadly — keep the compiler's non-runtime TUs off it; verified the compiler only pulls `pl_cell.h` via those three runtime TUs).
2. `-ffixed-r14` in **both** Makefile build rules for those TUs (the `scrip` link and `out/libscrip_rt.so`).
3. `bb_query_frame` α preamble: `push r14`, ensure-trail + load `r14 = top` (int index, §5 option A), and the matching `pop r14` on the γ/ω exit edges (mode-3 host bracket).
4. Re-point `rt_trail_mark` (`= read r14`), `rt_trail_unwind`, and `pl_trail_push` onto `g_pl_trail_top`, keeping the int-index ABI frozen (§5). The choice box is **untouched**.
5. Gate after each sub-step (floor 115/115 m3+m4 + bench 22 HARD; `.s` byte-identical where dormant proves neutrality). The instant any rung/bench diverges, bracket it with the 2-way sync-step monitor BEFORE reading code — a register-ABI change is exactly that silent-corruption class.

**Expected payoff (honest):** R14-residency is the *second-order* shave (removes the `top` load/store per trail op); it does NOT touch the `GC_malloc` traffic that is the 2.5–4× gap (that's the escape-blocked env/heap reclamation, PL-AREAS-4). The value here is the *architectural completion* — the ratified mapping realized, r14 no longer idle (the completion-test grep satisfied) — plus a modest real shave. The big number lives in PL-AREAS-4.

## 7. At the next handoff
Fold §5's resolution + §3's de-risk-proven note into the goal file's **PL-AREAS-2** entry (currently it only says "R14 register-top NOT wired … the remaining half"). Left untouched this session (not a handoff; live tracker not restructured mid-session).

## 8. Tree state
Clean. `-ffixed-r14` runtime + the de-risk binary live only in `/tmp` (reversible). Baseline `out/libscrip_rt.so` restored. Floor verified green this session: smoke 5/5, rungs 115/115 (m2+m3+m4), bench 22/0/0, no-new-global PASS (doomed 14), no-vstack 0. **Nothing committed.**
