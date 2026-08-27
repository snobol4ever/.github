# FINDING — `ARCH-ICON.md`'s "LIVE REGISTER CONTRACT" describes a per-graph frame-base selector that **does not exist**: `x86_fb()`, `x86_fb_pinned()` and `x86_fb_data()` are hardcoded constants, and the function the doc names has zero occurrences

**Date:** 2026-08-27 · **Seat:** hq_P (`/home/claude_P`) · **Topic:** rung `icon-n2-generator-activation-frames`; drift report per ceo's standing ARCH audit (*"report drift you find as FINDINGs, do not silently code around a wrong ARCH doc"*).
**Found by:** reading `ARCH-ICON.md` before N-2 item 1b — i.e. by complying with Lon's read-the-ARCH-docs order, having **failed** to comply before item 1. The order paid for itself on first use.
**Tree:** SCRIP `bd173f82`. Every claim below is `grep`/`git`-verified, not inferred.

---

## 1. WHAT THE DOC SAYS vs WHAT THE CODE IS

`ARCH-ICON.md` § REGISTER CONTRACT, headed *"CORRECTED 2026-07-18; verified vs live x86_asm.h + zeta_choices.h"*, and introduced by the file's own subtitle as *"the LIVE REGISTER CONTRACT that every BB template (all languages) obeys"*:

> `x86_fb()` = **PER-GRAPH (s197 FLATDISP-8):** RBP for graphs whose prologue pins it (`emit_jmp_pin_rbp()` = flat_deep_arrival || flat_pat || flat_gen — suspended generators, pattern blobs, deep arrivals …); RSP for depth-static graphs … **ONE selector `x86_fb_pinned()` feeds all accessors in BOTH media.**

The live code (`src/templates/x86/x86_asm.h:491,493,497`):
```c
inline int          x86_fb_pinned() { return 0; }
inline int          x86_fb_data()   { return 0; }
inline const char * x86_fb()        { return "rsp"; }
```
⛔ **All three are unconditional constants.** There is no per-graph branch, no `flat_gen` arm, no consultation of anything.
⛔ **`emit_jmp_pin_rbp()` — the selector the doc names — has ZERO occurrences in `src/`.** What survives is `emit_jmp_pin_legacy()` (`emit.h:607`), the box-kind disjunction ceo's audit already flagged as ahead-of-doc-and-code.

**Provenance, from `git log -S`:** `x86_fb_pinned() { return 0; }` enters at **`708c22c1` — "RBP ERADICATION (Lon directive, live session): every rbp reference remo…"**. So the selector was not lost; it was **deliberately eradicated on a Lon directive**, and the ARCH doc was never updated to say so.

## 2. ⭐ THE DOC NOW CONTRADICTS ITSELF, BECAUSE ONLY HALF OF IT WAS UPDATED

The same file's line 8 was updated **today** for Lon's new law:
> *"Icon walks the ladder RSP spine → RBP activation frame → root, γ-SUSPEND-capable graphs keeping ζ in an RBP activation frame"*

That sits **directly above** the 2026-07-18 REGISTER CONTRACT quoted in §1. ⛔ **The two describe different machines, and neither matches the code:** line 8 describes the ladder we are climbing *back up* under Lon's FRAME-PLACEMENT CRITERION; the REGISTER CONTRACT describes the pre-eradication selector; the code has neither. ⭐ **A doc that is updated in one place and not the other is more dangerous than a uniformly stale one** — the fresh timestamp on line 8 lends credibility to the stale section beneath it.

## 3. ⛔ IT COST ME REAL WORK, AND THAT IS THE POINT OF THE ORDER

N-2 item 1 (SCRIP `e637707d`) re-homed generator ζ to RBP by adding `icn_gen_zeta_ft()` and one early return each in `x86_zop` and `x86_zref`. **Had I read this doc first I would have looked for `x86_fb_pinned()` and found it dead in one grep** — and I would have understood immediately *why* generator ζ was rsp-relative. It is not a subtle regime gate. **The frame-base selector was collapsed to a constant and the doc never said.**

⭐ The change stands — it is measured, gated default-OFF, and its controls are clean — but its **shape** is now clearly a workaround: it re-implements, narrowly and per-family, the thing the ONE selector was supposed to do for all accessors. ⛔ **The right long-term cure is to restore `x86_fb_pinned()`/`x86_fb()` as a real per-graph selector keyed on Lon's unbounded-growth criterion, not to keep bolting on per-family rebases.** That is N-2 item 2's actual shape, and it is also what ceo's audit predicted the rung would close.

## 4. ⛔⛔ THE LATENT TRAP THIS LEAVES FOR ITEM 2 — TWO INDEPENDENT SPELLINGS OF ONE DECISION

The frame base is decided in **two places that do not consult each other**, and they agree today **only because both are constants**:
- `x86_frame_text_mem()` (`x86_asm.h:805`) builds `"[" + x86_fb() + " + N]"` — goes **through** the selector.
- `x86_fr32_prefix()` / `x86_fr64_prefix()` (`:501-502`) return the literal `"dword ptr [rsp + "` / `"qword ptr [rsp + "` — **hardcoded, selector never consulted.**

⭐ `src/runtime/rtx/rtx_abi.inc:27` documents the intended contract — *"use FR(off)/FRQ(off), which resolve through `x86_fb()`"* — which is **true of the prefix's intent and false of its implementation**.
⛔ **So restoring `x86_fb()` to return `"rbp"` for generator graphs would move one spelling and not the other, reintroducing the split-base bug at a much larger scale** — precisely the failure N-2 item 1b already exists to fix at one cell. **Whoever does item 2 must unify these two spellings FIRST.**

## 5. ⚠️ A THIRD CASUALTY OF THE ERADICATION: A DIAGNOSTIC THAT CANNOT SAY ANYTHING

`emit_fb_divergence_check()` (`emit.cpp:561`, behind `SCRIP_FB_DIVERGE=1`) exists to report when the data frame-base and the record frame-base disagree. Its print statement is:
```c
emit_jmp_pin_legacy() ? "rsp" : "rsp",   emit_rec_pin() ? "rsp" : "rsp"
```
⛔ **Both arms of both ternaries are the same string.** The predicate is still evaluated and the guard `if (emit_jmp_pin_legacy() == emit_rec_pin()) return;` still fires, so the check can still *count* a divergence — but the value it prints to identify it is `rsp` either way. ⭐ Same family as this week's other mute instruments (mtime = lock-taken-not-work; `PASS(0)` = checked-or-never-asked): **an instrument left reporting a constant after the thing it measured was removed.** Not urgent — it is diagnostic-only and off by default — but it must be repaired or deleted as part of item 2, because item 2 is exactly when someone will switch it on and trust it.

## 6. RECOMMENDATION

1. ⛔ **Correct `ARCH-ICON.md` § REGISTER CONTRACT** to state that `x86_fb()`/`x86_fb_pinned()`/`x86_fb_data()` are constants post-`708c22c1` RBP ERADICATION, and that `emit_jmp_pin_rbp()` does not exist. Keep the history — the eradication was a Lon directive — but stop presenting it as live.
2. **Fold into N-2 item 2, before any code:** unify `x86_fb()` and `x86_fr{32,64}_prefix()` into one spelling, then restore the selector on Lon's unbounded-growth criterion.
3. **Repair or delete `emit_fb_divergence_check`'s constant ternaries** in the same slice.
4. ⭐ **Method note for the audit, worth more than these four items:** this drift was invisible to a code reader (the constants look deliberate and are), and invisible to a doc reader (the section is confident and carries a "verified" date). **It was only visible by deriving the doc's claim into a grep and running it** — which is exactly the second of the two rules hq_C and I are co-signing: *derive the fix (or the claim) from the stated mechanism and check it holds.* A "verified 2026-07-18" stamp is a claim about the past, never about the tree in front of you.
