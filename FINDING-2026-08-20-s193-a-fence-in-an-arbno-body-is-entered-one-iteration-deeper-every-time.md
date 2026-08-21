# FINDING s193 — A FENCE IN AN ARBNO BODY IS ENTERED ONE ITERATION DEEPER EVERY TIME, AND ITS STATIC SLOT LANDED ON THE BLOB'S OWN OPERAND CELL

**2026-08-20 · seat2 `/home/claude2` · Claude Opus 5 · queue row `rty-fence-arbno-stored` (rank 1) · SCRIP base `c512089a` · RT_OPT `-O0`**

## THE DEFECT IN ONE LOAD

`s192 FENCE-RTAIL` cured the carrier *selection* (a blob is entered from the right) and left one red standing — `145_pat_left_assoc_via_arbno_fence`, **the row's own headline DONE-WHEN** — with the residual named but not rooted: *"what the blob's beta does AFTER it lands a correctly published ARBNO beta."*

It does this:

```
n5_match_fence1_α:   mov  qword ptr [rsp + 176], rsp
n5_match_fence1_as:  mov  rsp, qword ptr [rsp + 176]
```

`IR_MATCH_FENCE1` banks its watermark at a **static RSP-relative offset**. That offset is a claim about depth — and a FENCE1 inside an ARBNO body is **re-entered at a new depth on every iteration**, because the retreat arrives through `PAT$N_β → n_match_arbno_β → n_match_fence1_α` with the previous instance's growth still on the stack.

Measured with gdb ignore-counters on the row's minimal witness `probe/retry/rty_fence_capdefer_plainleft` (`expr = LEN(1) ARBNO(FENCE('+') num . LAST)`):

| iteration | rsp | `[rsp+176]` resolves to | what `IR_MATCH_DEFER` then loads from `[rbp-24]` |
|---|---|---|---|
| 1 | `0x7fffffffe000` | `rbp+104` — above the frame, harmless | `0x7fffb20056f0` — the real pattern descriptor |
| 2 | `0x7fffffffdf80` | **`rbp-24`** | `0x7fffffffdf80` — **the fence's own saved rsp** |

`rbp-24` is not scratch. `blob_head_bytes()` names the layout: `-8 r10 · -16 r11 · **-24 rdx (DTP)** · -32 r12`. It is the deferred-pattern operand cell, and `n7_match_defer_α: mov rdi, qword ptr [rbp + -24]` is the instruction that reads it. On iteration 2 the fence overwrites the pattern with a stack address, the SPAN matches against garbage and fails, the ARBNO can never extend, and the match answers `fail`.

## THE ABLATION THAT FOUND IT — A 2×2, AND EVERY CELL MATTERS

The red needs **three** ingredients at once; remove any one and it goes green.

| body element after `FENCE('+')` | no capture | with capture |
|---|---|---|
| `LEN(1)` / `ANY(...)` (fixed width) | GREEN | GREEN |
| `num` = `SPAN(...)` (defer box) | GREEN | **RED** |

and `'+' num . LAST` without the fence is GREEN. `$` immediate assignment fails identically to `.`, so it is not conditional-assignment-specific; a trailing `LEN(0)` does not rescue it, so it is not about being last. What the three ingredients jointly buy is simply **enough per-iteration stack growth to walk `+176` onto `rbp-24`** — the capture and the defer box each contribute, the fixed-width matchers do not.

⛔ **The `.s` diff at the top of this hunt was 398 lines and said nothing** — a capture renumbers every node. The 2×2 was what made the pair tight enough to read, and the trace instrument that broke it open was the manual's own idiom (v3.7 p.140), immediate assignment to `OUTPUT`: the red prints `2` and stops, the green prints `2` then `3`. One ARBNO iteration, never a second.

## WHY THE DEPTH-SAFE ARM WAS NEVER REACHED

The cure already existed. `R-4(f) SLICE 3` (s96) built exactly this: when `op_fence_frame_off != -1` the watermark rides an **activation-frame slot** `[rbp+off]` and *"no RSP-relative offset is involved at any depth."* `frame_slot_scan` even supports the stored-blob class (`R-4(b)`, s97, rc=2, slots off the blob's own rbp frame).

`fence_frame_candidate()` never asked for it, because it asks exactly one question:

> does **MY BODY SPAN** `[operands[0]..operands[1]]` hold a container/transfer member?

Here P is `'+'` — a bare literal. Body static ⇒ not a candidate ⇒ the RSP arm. But the hazard was never in the fence's body; it was in the fence's **enclosing context**. The predicate asks whether *I* move the frontier and never asks whether *I am entered at a moving depth*.

⛔ **And this is why the inline control was green while the stored road was red** — the fact the original brief opened with (*"inline is green, so the tree contains its own reference implementation"*). Both roads take the **same** RSP arm (`[rsp+320]` inline, `[rsp+176]` stored); the inline graph simply never re-enters the fence at a shifted depth. Stored-vs-inline was never the arm selection. It was the depth.

## THE CURE — ONE LINE, AND THE MARKER ALREADY EXISTED

The lowerer has stamped this exact class since s42+1 — `lower_snobol4.c:1695`, `IR_LIT(F).ival = 2`, *"FENCE1-in-ARBNO"* — and used it only to suppress the U-2 frame:

```c
if (IR_LIT(nd).ival == 2) return 1;   /* DYNAMIC ENTRY DEPTH */
```

**1 insertion, 0 deletions, one file** (`src/emitter/emit.cpp`, `fence_frame_candidate`). The watermark moves to `[rbp-80]`, *below* the blob head where it can never reach the DTP cell; the blob frame grows 72 → 88 to host it; all three release sites read the same slot at any depth.

⛔ **Keyed on ENTRY DEPTH, never on an op** (FACT RULE NO-PER-OP-FILTER): every FENCE1 in every ARBNO body is admitted identically, no member named. **NO new global, NO new killswitch** (`getenv` count unchanged), **NO new opcode, NO template touched** — the cure re-uses a mechanism three other customers already share.

## MEASURED

**A/B on ONE tree at `c512089a`, patch stashed vs applied, each arm its own rebuild:**

| arm | m3 | m4 |
|---|---|---|
| control | 335 / **2** | 328 / **8** SKIP 1 |
| patched | 336 / **1** | 329 / **7** SKIP 1 |

Δ = **exactly `145_pat_left_assoc_via_arbno_fence` FAIL→PASS in BOTH modes**; every other failure identical **by name**. Oracle-exact at `sbl -bf`: `first=1 last=5`.

**BLAST RADIUS, 1872 SNOBOL4 programs** (compile-time `.s` md5; `programs/lon/` and `programs/include/` excluded **by construction**, `find … -prune`): **14 rows differ, 13 are the cure.**

⛔ **THE NOISE FLOOR WAS MEASURED FIRST AND IT IS NOT ZERO.** The control arm self-diffed against **itself** (same binary, two runs) gives **1 row** — `programs/snobol4/parser/unary_not.sno`, whose `.S0` rodata is nondeterministic (s147's named class, re-confirmed by seat3 at s192). It is in the mover list; quoting 14 without the self-diff would have published a phantom.

**All 13 real movers are FENCE1-in-ARBNO programs and all 13 are behaviour-verified in BOTH modes: 13/13 PASS, 13/13 AGREE.** Of them, **3 are REPAIRS** — `145_pat_left_assoc_via_arbno_fence`, `rty_fence_capdefer_plainleft` (the residual), and `rty_fence_capdefer_both_segv`, **which was an m3 SIGSEGV *and* a mode divergence and is now PASS/PASS/AGREE** — and 10 are bytes-only movers that were green and stayed green.

Gates green ×4: `emit_no_lang` · `template_medium_invisible` (0, ceiling 0) · `icn_no_stack` · `icn_one_reg_frame`.

⭐ **ZERO movers outside SNOBOL4.** The predicate is reached only through `IR_MATCH_FENCE1` with `ival==2`, which only `lower_snobol4.c` stamps — so no scoping conjunct was needed and **none was invented**.

## THE GENERALISABLE MOVE

**A static offset is a claim about depth, and a box that can be re-entered has no single depth to make it about.** The predicate that granted the safe slot was written to detect *"my body will move the frontier"*, and it was right about every witness that had one; it never considered that the frontier could move *underneath it* between one entry and the next. Same family as s192's `k > r` (*a guard correct only because no input has exercised it is not correct — it is unexercised*) and s189's `default: return 0`.

⭐ **And the evidence was in the tree the whole time, twice.** The s192 header on `rty_fence_capdefer_both_segv` predicted the mechanism verbatim — *"that box stores/restores rsp through a STATIC-DEPTH slot, a premise the lowerer itself records as violated inside an ARBNO body ('rsp moves per iteration, Tier D')"* — and the FENCE1 template's own `fence_whack_commit` note carries the witness `mov rsp,[rsp+176]` in its H14 line. **Two comments named the offset and neither was wired to a predicate.** A comment that knows the bug is not a guard; the fix is to make the predicate ask the question the comment already answered.
