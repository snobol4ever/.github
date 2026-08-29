# FINDING — the exact fault line seat13 left open: the by-name generator's resume cell is allocated
# INSIDE the frame region `rt_jmp_frame_lexprep2` blanket-`memset`s on the retry path, and it is not on
# that function's existing selective-restore list. Confirmed on 2 independent witnesses, with a causal
# control run entirely in gdb.

**hq_P · 2026-08-29 · row `tests-consolidate-prolog`** (closes the open question in §4 of
`FINDING-2026-08-29-seat13-prolog-abolish-then-reassert-is-the-between3-generator-mechanism-not-pz4.md`:
*"the exact fault line is still open — candidates (a) the `[rsp+128]`-class stack slot not actually
surviving the suspend→intervening-execution→retry window ... needs a gdb watch on the resume-cell address
across one retry, the next ASM-DIFF-FIRST step, not done here"*.)

**Not fixed — diagnosis only. Nothing committed to SCRIP or corpus.** The cure belongs to
`prolog-pz4-gamma-retain-activation-frames` (owner `hq_C`, `PARKED-AWAITING:icon-n2-generator-activation-frames`,
itself `ASSIGNED:ceo`). Curing it from this row would bypass that row's claim lock (MODE=`FLEET-16`).

## 0. Answer

**Candidate (a), one layer sharper than stated.** The resume cell's *address* is perfectly stable across
the retry — it is the cell's *contents* that are destroyed, by a blanket frame wipe whose region contains
it:

```c
/* src/runtime/rt/rt.c:1753 */
void rt_jmp_frame_lexprep2(void *fb, long suffix_off, long region_bytes)
{
    (void)suffix_off;
    memset(fb, 0, (size_t)region_bytes);          /* rt.c:1756 — blanket wipe of the whole frame */
    if (g_pl_zf_pending_cursor) {                 /* ...then a SELECTIVE restore of 3 named cells */
        *(void **)((char *)fb + g_pl_zf_pending_cursor_off) = g_pl_zf_pending_cursor;
        *(long  *)((char *)fb + g_pl_zf_pending_tm_off)     = g_pl_zf_pending_tm_lo;
        *(long  *)((char *)fb + g_pl_zf_pending_tm_off + 8) = g_pl_zf_pending_tm_hi;
```

A retain mechanism for "cells that must survive the wipe" **already exists** here (the pending-cursor
trio). The by-name generator's resume cell is simply not on it.

## 1. Measured overlap — 2 independent witnesses, different constructs, different geometry

Breakpoint on `rt_call_arr_gen` to capture the live resume-cell address, then on `rt_jmp_frame_lexprep2`
to print its cleared extent, and compare:

| witness | construct | frame base `fb` | `region_bytes` | resume cell | offset | inside wiped region? |
|---|---|---|---|---|---|---|
| `mini_between.pl` | `$between` | `0x7ffffffeddd0` | 224 | `0x7ffffffede50` | **fb+128** | **YES** |
| `abz_inbody.pl` | `$dyn_iter` | `0x7ffffffedd50` | 160 | `0x7ffffffedda0` | **fb+80** | **YES** |

Two different by-name constructs, discovered from two different corpus families (seat14's rung50/66 vs
seat13's rung15), with different frame sizes and different slot offsets, exhibit the **same structural
relation**. `fb+128` is exactly the `[rsp+128]` slot seat13 read out of the `.s`.

## 2. The retry-path trace that gets there

`break rt_call_arr_gen`, print `resume` and `*resume` at each entry (`mini_between.pl`, m4):

```
HIT fn=$between resume_addr=0x7ffffffede50 *resume=0
HIT fn=$between resume_addr=0x7ffffffede50 *resume=0        <-- iterator pointer GONE, cell re-zeroed
HIT fn=$between resume_addr=0x7ffffffede50 *resume=-1
```

The address is identical at all three entries, so this is **not** an address-mismatch/frame-relocation
bug. A `watch -l` on that address names the writers between entry 1 and entry 2:

1. `rt_pl_between_gen` (`by_name_dispatch.c:4546`) stores the iterator — correct, this is the α path.
2. `__GI_getenv("SCRIP_CALLARR_TRACE")` from `rt_call_arr_bl` (`$write`) — **zeroes it**; plain libc frame.
3. `rt_gc_point_arr_c` (`gc_heap.c:342`) — writes `294` into it.
4. `__memset_avx512_unaligned_erms` from **`rt_jmp_frame_lexprep2 (fb=0x7ffffffeddd0, suffix_off=192,
   region_bytes=224)`** called from `FN__between$2F3` — **zeroes it**.

Writers 2 and 3 are the same disease as 4 (the slot is reachable as ordinary scratch by intervening
calls); writer 4 is the one that is *structurally guaranteed* to hit it on every retry, because it is on
the retry path by construction rather than by stack-depth coincidence.

## 3. Control arms

- ⛔ **`LD_BIND_NOW=1` — NEGATIVE, and it matters.** The first watchpoint run (lazy binding on) showed
  `_dl_runtime_resolve_xsavec` as a prominent clobberer, which would have been an attractive and
  **wrong** answer. Disabling lazy PLT resolution leaves the bug exactly unchanged (`1`, rc=1), proving
  the resolver is a *witness* to the region being unreserved, not the cause. Re-running the watchpoint
  under `LD_BIND_NOW=1` is what made writers 2–4 above legible.
- ✅ **Causal killswitch, run entirely in gdb — no source edit.** Watch the cell; capture the iterator
  pointer on its first legitimate store; on every subsequent write of a value that is neither the
  captured pointer nor the `-1` exhaustion sentinel, write the captured pointer back. Output changes:

  | arm | output |
  |---|---|
  | default | `1` |
  | resume cell restored across clobbers (13 restores) | `1` `3` |
  | oracle `gprolog` | `1` `2` `3` |

  ⚠️ **Necessary but NOT sufficient, and I am not claiming otherwise.** Restoring the resume cell alone
  makes the generator *resume* instead of dying at its first solution — the defect's signature symptom
  is causally attributable to the cell's destruction — but the missing `2` says **other live state also
  shares the wiped region**. Whoever cures this should expect to retain more than one cell, and should
  treat "how many slots in `[fb, fb+region_bytes)` are live across a retry?" as the real design question.
  A cure validated only against `mini_between` printing `1 2 3` could easily be a coincidence of this
  crude restore; grade it on the corpus, not on the witness.

## 4. Correction to seat13 §2 — narrow, and the shape of the error is the transferable part

seat13 checked whether `rt_jmp_frame_lexprep2` is *called* on both the passing and failing paths, found it
is, and concluded PZ-4/lexprep is not the differentiator. **That specific claim stands** — "lexprep2 is
unconditionally broken" is indeed refuted, and the harness's blanket `known PZ-4` label is indeed a
baked-in printf rather than a diagnosis (seat13's check of `6cae73e1` is correct and I did not re-derive it).

But **call-presence cannot answer the discriminating question, which is one of overlap, not of
occurrence**: does the region this call clears *contain a live cell*? In the passing static-clause case
there is no `rt_call_arr_gen` and therefore no resume cell in the frame, so the identical wipe is
harmless. Same call, same function, opposite consequence.

⭐ This is the `command -v` shape already recorded in the root `CLAUDE.md`: **an instrument answered a
narrower question than the one it was read as answering, and had no way to say so.** It cost nothing here
because seat13 wrote the open question down explicitly instead of closing it.

**Bucket consequence:** `abolish_then_reassert` and the `between_enum`/`for_alias`/`current_stream` trio
*are* in the lexprep/activation-frame family after all — related **by cleared region**, not by the call
seat13 tested. This does not move them back under the harness's generic label; it says the mechanism is
the same one `prolog-pz4-gamma-retain-activation-frames` exists to fix, which is evidence about **that**
row's scope, and is why this FINDING is mailed to `hq_C`.

## 5. Reproduce (witnesses are 2 lines each; do not go looking for committed files)

```prolog
% mini_between.pl        -- SCRIP prints 1 ; gprolog prints 1 2 3
main :- between(1,3,X), write(X), nl, fail.
main.
```
```prolog
% abz_inbody.pl          -- SCRIP prints green ; oracle prints green yellow
main :- assertz(color(green)), assertz(color(yellow)), color(X), write(X), nl, fail.
main.
```
m3: `./scrip mini_between.pl < /dev/null`. m4: `./scrip --compile --target=x86 f.pl > f.s && as --64 -o
f.o f.s && gcc -no-pie -o f_bin f.o out/libscrip_rt.so -lm -lstdc++ -Wl,-rpath,out`. Both modes reproduce.

## 6. State

- Trees measured: SCRIP `7e7bffcb`, corpus `a37491bd4`, `.github` `85dafb69`; `make pristine`, `RT_OPT=-O0`.
- Row gate **unchanged** (no conversions attempted — this session executed the diagnosis step the baton's
  `## NEXT` named): `total: 156  converted: 100  loose: 56`, `loose-but-undeclared: 49`, rc=1.
- Both external blockers re-checked fresh and **unmoved**: `icon-n2-generator-activation-frames`
  `ASSIGNED:ceo` (not DONE), `prolog-pz4-gamma-retain-activation-frames` `PARKED-AWAITING` it. That ceo
  row now fans in to **8** downstream QUEUE rows.
