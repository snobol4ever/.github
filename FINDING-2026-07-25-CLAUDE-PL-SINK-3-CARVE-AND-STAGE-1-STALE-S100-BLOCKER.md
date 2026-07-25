# FINDING 2026-07-25 — PL-SINK-3 CARVE LANDED + PL-STAGE-1 UNBLOCKED BY A STALE s100 NOTE; THE COST HAS MOVED TO THE CALL SPINE

**Session:** s145 · **Goal:** GOAL-PROLOG-BB.md · **Directive:** "Improve Prolog speed performance. We want faster than SWI and GNU."

---

## 0. HEADLINE — HONEST

Measured on a failure-driven `nrev(30)` x2000 (contract §9 shape), mode-4, runtime `.so` at **`-O0`** (FACT-RULE default; no `-O2` directed this session), same container, same run block:

| engine | wall | ratio |
|---|---|---|
| gprolog 1.4.5 | 0.071s | 1.00x |
| swipl 9.0.4 | 0.100s | 1.41x |
| SCRIP m4 **before** this session | 0.595s | **8.4x** |
| SCRIP m4 **after** (SINK-3 + STAGE-1) | **0.471s** | **6.5x** |

Session delta **1.26x**. Whole sink family off-vs-on is now **1.47x** (0.696 -> 0.471).

**WE DID NOT BEAT gprolog OR SWI AND IT IS NOT CLOSE.** Closing 6.5x is a multi-rung ladder (REGAIN-1 direct-call spine + DET delivery + first-arg indexing), not a session. What this session buys is two landed rungs, one unblocked rung, and a MEASURED map of where the remaining 6.5x actually is (§4). Do not let a future cursor round this to "nearly parity."

---

## 1. TWO BENCH-METHODOLOGY CORRECTIONS (bank these; they invalidate older numbers)

**(a) `gprolog` SILENTLY IGNORES A USER `append/3`.** `error: native code procedure append/3 cannot be redefined (ignored)` — gprolog then runs its OWN native `append/3`. Any nrev/qsort comparison that defined `append/3` measured **gprolog's compiled builtin against SCRIP's interpreted user predicate**. Every bench here renames to `app/3`. Re-read any historical gprolog ratio in this goal file with that in mind.

**(b) corpus `benchmarks/prolog/vanroy/nrev.pl` DOES I/O INSIDE THE LOOP** (`bench__main :- data(L), nrev(L,R), write(R), nl.` under `between(1,65536,_)`). That measures the term writer, not nrev. Use a quiet failure-driven loop with a single terminal `write(done)`.

Also: gprolog batch invocation needs an explicit `halt` (`main :- bench(N), halt.`) or it drops to the interactive top level and a timing harness hangs on stdin.

---

## 2. RUNG PL-SINK-3 — THE CARVE (LANDED, 1.26x)

**What:** the `$unify_lst(S,H,T)` WRITE arm (unbound subject) — nrev's O(n^2) OUTPUT construction, the half SINK-2 explicitly deferred.

**Frontier export (`src/runtime/rt/gc_heap.c`).** `rt_gcheap_alloc`'s DETAX fast path (`armed && top + total <= end -> carve, bump, return`) is the exact idiom to inline, but `g_hp_top`/`g_hp_end`/`g_hp_blocks` were **file-static** — unreachable from emitted code. Moved into ONE exported `rt_hp_fr_t g_hp_fr {top@0, end@8, blocks@16, armed@24}` with `#define g_hp_top (g_hp_fr.top)` etc., so every existing reference in the TU compiles unchanged. Four `_Static_assert` layout anchors (contract §6). `armed` mirrors `(g_alloc_detax == 1 && g_ah_on <= 0)` so the inline tests one byte. **ONE new exported symbol.** Grep confirmed ZERO external references to the three former statics before the change.

**Contract §3 honesty:** `gc_heap.c` is OUTSIDE `test_gate_pl_no_new_global.sh`'s policed set (which is `unification.c`, `arithmetic.c`, `resolution.c`, `lower_prolog.c`, `parser/prolog/*.c`, `bb_cell_*`, `bb_det_*`, `bb_query_frame`, `bb_callee_frame`), so the floor is untouched — declared here on purpose rather than discovered later.

**Template (`src/templates/bb_call_fn.cpp`, labels 80..94).** `sink_carve48` / `sink_carve48_take` / `sink_kid` / `sink_tp_nc`. Order: ALL FOUR deferral tests first (dot_sl interned; carve armed + 48B room; trail live + room for **THREE** entries), THEN mutate. Nothing after the first write can reach SLOW.

**⭐ THE ALIASING RESULT — BETTER THAN THE RUNG SPEC.** SINK-2 had to defer H/T aliasing because it pre-derefed BOTH before binding either. In WRITE mode the C (`plw_mkc_kids`) derefs each kid **immediately before its own bind**, so emitting the same sequential order makes aliasing correct FOR FREE: the second deref observes the first bind and chases into `kids[0]`, producing the C's chain instead of a double bind. Verified: `X = [Y|Y]` gives `[_G0|_G0]`, gprolog gives `[_250|_250]`. **This is why contract §1's pre-classify requirement did not apply — both kid arms are TOTAL (unbound -> seed+bind; bound -> copy), so there is no sub-arm that can defer after the alloc.**

**Zeroing skip is sound here.** `rt_gcheap_carve` memsets the 32B payload for HB_PLJ; the WRITE arm overwrites all 32 bytes unconditionally (each kid arm writes a full 16-byte DESCR). Bit-identical, and it is the one per-alloc lever s141 measured as noise that pays here — precisely because we are the sole writer. (s141's cons-zeroing experiment was UNSAFE because 2 of 6 `rt_plj_alloc` callers leave a cell unwritten; that does not apply to a caller that writes every byte.)

**`sink_tp_nc`** = `sink_trailpush` minus the base-null and room tests. Dominance proof: the WRITE arm reserves all three worst-case entries in ONE pre-check before any mutation, and the inline path is the sole mutator between check and pushes, so the per-push tests are provably dead. Re-emitting them would be dead hot-path code.

**Header write** avoids `movabs`: `[at+0]` qword 0, `dword [at+8] = 48` (total), `dword [at+12] = 209 | (1<<16)` (HB_PLJ | HBF_TTL packed as one dword — there is no 16-bit store encoder).

---

## 3. RUNG PL-STAGE-1 — INLINE ARG INSTALL (LANDED, ~6%) — **AND THE s100 BLOCKER WAS STALE**

`rt_arg_stage(idx,v)` is `rt_gc_point(&v,0); g_call_args[idx] = v;`, and `rt_gc_point_arr`'s FIRST act is `if (!g_gc_pending) return;`. So on every call with no collection pending — nearly all of them — the runtime burns **THREE nested `-O0` call frames to perform ONE 16-byte store**. nrev stages ~25M args.

Now emitted inline (`src/templates/bb_call_proc_staged.cpp`, `stage_arg_inline`, labels 20..35, three call sites): test `g_gc_pending`; zero -> two-qword store into `g_call_args[i]`; non-zero -> the untouched C leaf (there the collector may adjust `v` under the shield, so the leaf must own it). Bounds test `0 <= idx < CALL_ARGS_MAX` is decided at EMIT time. Capped at 8 args.

**⚠ THE FINDING THAT MATTERS MOST IN THIS DOCUMENT.** `bb_call_proc_staged.cpp:227-228` had parked this exact optimization since s100:

> *"Inline arg install (kills rt_arg_stage) ... **B blocked on g_call_args residency (.so data, movabs-forbidden; needs slab home or register-arg ABI, Lon design call)**"*

That blocker was dissolved by **SINK-1 in s142** and nobody noticed the dependency. The dual-medium RIPSEAL load — `x86("lea", r, "[rip + __]", (uint64_t)&sym, "sym")`, TEXT emits a rip-relative symbol, BINARY emits the live address — is EXACTLY the ".so data reached from emitted code" primitive that was declared missing. It had already been in the tree for three sessions, used for `g_pl_trail` (also `.so` data), when this note was still being read as authoritative.

**ACTION FOR THE NEXT SESSION: audit every other parked note whose stated blocker is "cannot address .so data / movabs-forbidden / needs slab home."** The primitive exists. `grep -rn "movabs-forbidden\|residency\|slab home" src/templates/`.

---

## 4. WHERE THE REMAINING 6.5x IS (45 gdb samples, mode-4 binary, GC-corrected)

Method per s141: sample the MODE-4 binary (`gdb -p PID -batch -ex "bt 4"`), never mode-3 (JIT blob has no symbols and mis-attributes).

| bucket | share (non-GC) | who |
|---|---|---|
| **PROC-CALL SPINE** | **~36%** | `rt_proc_call_open`, `rt_frame_bind_args`, `rt_proc_call_prologue_lex`, `rt_proc_call_epilogue_γ`, `rt_arg_stage`, `rt_proc_hash_lookup`/`rt_proc_find` |
| EMITTED (`xchain*_α/β`) | ~24% | our own boxes — this is the number that should GROW |
| `rt_jmp_frame_lexprep2` | ~20% | per-activation frame seed + `rt_frame_bind_args` |
| `rt_pl_dop_trail_mark` | ~12% | SINK-8 |
| unify family | ~4% | **SINK-1/2/3 did their job — the data plane has gone quiet** |

At 40k iterations GC additionally takes ~24% (`gc_collect_ex` + `rt_gc_point*`); at the 2k headline size it does not fire. Report GC honestly per bench size.

**THE SPINE IS THE LEVER.** Args are staged into a C-side buffer (`g_call_args`) and then copied AGAIN into the callee frame (`rt_frame_bind_args`) — a double copy per call, ~10M calls in this bench. That is **REGAIN-1 slice C** (emit-time-resolved `call procN_α`, arg cell-pointers in SysV regs, status in eax), which needs the driver-minted proc-entry `bb_label_t` table + one new in-band 'E'/'F' record. **NEXT RUNG.** SINK-8 (`$trail_mark`, ~12%, trivial leaf) is the cheap one to take alongside it.

---

## 5. MEASURED ZERO — REVERTED (PL-FILL-1)

`rt_jmp_frame_lexprep2`'s seed loop is `for (zi..) zf[zi] = NULVCL;` — a 16-byte struct assignment per slot which at `-O0` re-materializes the compound literal every iteration. Rewrote it as a hoisted two-qword splat. **Measured 0.471 -> 0.472 = ZERO.** Reverted per the s141 precedent (the per-alloc INIT-CONSTANT revert). The `lexprep2` samples are call overhead and `rt_frame_bind_args`, **not** the fill loop — do not re-litigate this.

---

## 6. GATES

- Prolog rung suite **164/164 x3 modes (interp/run/compile), run TWICE** (after SINK-3, and again on the final tree).
- **A/B byte-identical** vs `SCRIP_NO_SINK=1`, both binaries mode-4 with the sink baked at compile time, on a 10-case smoke: WRITE-mode nrev, H/T aliasing (`[Y|Y]`, `[Q|Q]` then `Q=[]`), backtrack-across-inline-binds via findall, mixed bound/unbound kids, open-then-closed tails, READ-after-WRITE, backtrack-heavy findall+nrev, double nrev. **All 10 also match gprolog 1.4.5 output.**
- fib / tak / deriv / qsort unregressed (rc=0, correct results).
- `test_gate_pl_no_value_stack.sh` PASS. `test_gate_pl_no_new_global.sh` fails ONLY on pre-existing `g_pl_disj_ctr` — **verified pre-existing by `git stash` + re-run**, and recorded as the same single failure in the s126 cursor; doomed-ratchet 14 / floor 14 PASS.
- `util_regen_prolog_bench_s_artifacts.sh`: emitted=22 changed=14 fenced=0 rejected=0 timedout=0 errored=0.

**Emitted `.s` was eyeballed instruction-by-instruction** before trusting any number — the SINK-2 lesson (`cmp reg, [mem]` is not an encoder form and emits NOTHING without a bomb). Every instruction of the WRITE arm is present in the artifact. `lea reg,[reg+disp]` IS supported (XK_REGDISP); note `lea reg,reg` silently maps to `x86_lea_subj_cursor` — avoid it.

---

## 7. FILES

- `src/runtime/rt/gc_heap.c` — `g_hp_fr` export + 4 `_Static_assert` + `armed` wiring.
- `src/templates/bb_call_fn.cpp` — `sink_tp_nc`, `sink_carve48`, `sink_carve48_take`, `sink_kid`, WRITE arm in `sink_unify_lst_str` (labels 80..94).
- `src/templates/bb_call_proc_staged.cpp` — `stage_arg_inline` + 3 call sites (labels 20..35).
- corpus: 14 regenerated bench `.s`.

Label decades now in use: SINK-1 40–58 · SINK-2 60–77 · **SINK-3 80–94** · STAGE-1 (bb_call_proc_staged) 20–35.
