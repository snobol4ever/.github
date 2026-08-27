# FINDING — N-2 item 1b: the resume-slot seed and its reader picked different base registers, and TEXT and BINARY picked different ones from each other

**Seat:** `hq_P` (HQ-PERFORMANCE) · **Date:** 2026-08-27 · **Mode at open:** FLEET-12, flipped to DUO mid-session
**Row:** `icon-n2-generator-activation-frames` (ASSIGNED:hq_P) · **Cure:** SCRIP `be711e46`
**Tree:** SCRIP `d4e6e971` → `be711e46` · corpus `a1455e69d` · `-O0` (FACT RULE: no `-O2` builds)

## The claim

Two defects with **one shape**: an eradication wave that reached the **TEXT** medium and not the **BINARY** encoder.
The second is the rung's item 1b; the first is why it existed and is **larger than this rung**.

## (1) `emit_rec_fb()` and `emit_rec_fb_num()` disagreed — a live m3 ≢ m4 divergence on the DEFAULT build

`src/emitter/emit.h` carried two functions that every caller pairs **by medium** — TEXT takes the string, BINARY takes
the register number:

```c
static inline const char * emit_rec_fb(void)     { return emit_rec_pin() ? "rsp" : "rsp"; }   /* both arms rsp */
static inline int          emit_rec_fb_num(void) { return emit_rec_pin() ? 5 : 4; }           /* 5 = rbp */
```

`708c22c1` ("RBP ERADICATION", Lon directive) rewrote the TEXT spelling to rsp-only and **left the BINARY encoder at 5**.
So for every graph with `emit_rec_pin() && !emit_rec_rsp_arm()` the two media emitted **different instructions from one
source**:

| site | TEXT (mode-4) | BINARY (mode-3) |
|---|---|---|
| `emit.cpp:2924/2928` α resume-slot seed | `mov [rsp+32], rax` | `48 89 85 20…` = `mov [rbp+32], rax` |
| `emit.cpp:3129/3132` resume landing | `add rsp,8; pop rsp` | `48 83 C4 08; 5D` = `pop rbp` |

⛔ `pop rsp` and `pop rbp` are not two spellings of one instruction. **m3 ≡ m4 is a design invariant** and it was broken
on the default, unarmed build.

**Which graphs.** `emit_rec_rsp_arm()` = `on && flat_pat && !emit_jmp_pin_legacy()`, and `emit_jmp_pin_legacy()` is true
for `flat_deep_arrival || flat_gen || flat_lcl_proc || zframe_graph`. So the divergence bites **Icon generators,
lcl_procs, zframe graphs and Prolog resumables** — and *not* plain SNOBOL4 patterns, where `rsp_arm` is true and both
arms pick 4. ⭐ **That is exactly why the SNOBOL4 board stayed 365/365 green over a broken invariant** — the one corpus
big enough to have caught it is the one corpus structurally excluded from the defect.

**Measured**, four-line generator witness, both modes, both arms:
`text_base=rsp bin_regnum=5 slot=32` — i.e. m3 stored the resume continuation **96 bytes above** where m4 stored it, at
`[rbp+32]`, which is past `[rbp+0]`=saved rbp and `[rbp+8]/[rbp+16]`=the port pair: **inside the caller's frame.**

⭐ **The comment that named this hazard had been deleted from this very file** by `e25a5daf` (the 200-col comment strip),
verbatim: *"all four refs read it, so the store and the load cannot pick different base registers — the s158 land mine
this file convicts over and over."* The warning was removed; the thing it warned about then happened.

**Cured structurally, not locally:** one decider, spelling derived from it, so BOTH-MEDIUM MANDATORY holds *by
construction* rather than by two edits remembering each other.

## (2) The α resume-slot seed never asked the ζ accessor — item 1b

`emit.cpp:2918` hand-built its operand (`snprintf` in TEXT, hand-encoded ModRM in BINARY) instead of calling a ζ
accessor. So `icn_gen_zeta_ft()` — item 1's rebase — **could not see it**: armed, the seed stayed at `[rsp+32]` while its
own reader (`bb_suspend.cpp:49`, `x86("mov", FRQ(_.op_sb), "rax")`) had already moved to `[rbp-64]`. One cell, two bases,
which is precisely what item 2 would have tripped over.

⛔ **This refutes the rung's standing leading hypothesis.** The baton read: *"the seed is emitted before the per-graph
frame size is set, so `ft` is 0 there."* **Measured: `ft=96` at seed time, correct.** The seed never consulted it at all.
The hypothesis blamed a value; the cause was a missing call.

**Cure:** route the store through `FRQ(g_suspend_resume_slot)` — the *same accessor the reader uses*, so store and load
cannot pick different bases. This also deletes a hand-encoded ModRM from `emit.cpp` (raw-byte producers are supposed to
be private to `x86_asm.h`). The `lea` is deliberately left per-medium: it is rip-relative, needs `bb_emit_patch_rel32`'s
label fixup in BINARY, carries no ζ base, and so cannot diverge.

## Evidence

- **Armed witness:** seed `[rsp+32]` → `[rbp-64]`, `.s` diff **exactly one line**, now matching the `IR_SUSPEND` box.
- **Unarmed m4 `.s` BYTE-IDENTICAL.** Negative control: armed-vs-unarmed differs by **77 lines**, so the diff can see a
  difference.
- **Control arms, measured before AND after (1):** SNOBOL4 corpus `m3 365/365 · m4 365/365 SKIP=0 MISSING=0` rc=0 ·
  Icon smoke m3 14/14 m4 14/14 · Prolog 4/5 · Snocone 5/5 · `emit_no_lang` rc=0 · `template_medium` rc=0.
- **D2 witness OFF:** all five CRASH 10/10, m3=m4, controls CORRECT — **= baseline**. **ARMED:** `suspend_single`
  m3 crash 1/10 / m4 WRONG, other four CRASH 10/10, controls CORRECT — **= baseline within its documented band**
  (cross-session rate now 2/10 · 0/10 · 0/10 · 1/10 · 1/10; still **not characterized**, see below).
- ⭐ **Required outcome, and it is the point: nothing moved.** Item 1b is addressing-consistency, a prerequisite. A
  prerequisite that moves a board is doing something it was not asked to do.

## What this does NOT claim

- ⛔ **Not a cure for the N-2 crash.** The caller landing (`bb_call_proc_staged.cpp:733`, `lea rsp,[rax+32]`) still lands
  above the whole α carve; that is item 3 and it is untouched here.
- ⛔ **The armed intermittency is still uncharacterized.** Five samples of 10 cannot pin a ~10% rate. The corrected
  recipe stands and has still not been run: `REPS=50 SCRIP_ICN_GENFRAME2=1 timeout 3600s bash
  scripts/test_icn_d2_suspend_witness.sh > out.txt 2>&1` — **no pipe** (a piped filter block-buffers, so a late kill
  discards everything).
- ⛔ **Reachability of site (2)'s `pop` divergence was not measured per-frontend.** It is cured and every board holds,
  but I did not instrument which live graphs reached it. Do not upgrade "boards unchanged" into "it was unreachable".

## Housekeeping

Retired `scripts/test_icn_genframe_alloc.sh` + `scripts/probes/icn_genframe_alloc.c` — they unit-tested
`rt_icn_gen_frame_alloc`/`_retire`, deleted at `915bdaa4` on Lon's order. The test **refused honestly** (rc=2, never
skip-as-success — the design was right) but could never pass again.

## Transferable lesson

⭐ **A rename or eradication wave crosses media unevenly, and the TEXT half is the half you can see.** `.s` output is
readable, so an incomplete wave looks complete: every artifact a human inspects shows the new spelling while the binary
encoder quietly keeps the old register. ⛔ **Two functions that must agree, written as two functions, will eventually
disagree** — the fix is not to edit both, it is to make one derive from the other. And when the corpus that would have
caught it is structurally excluded from the defect (SNOBOL4 here, via `rsp_arm`), a green board is not evidence.
