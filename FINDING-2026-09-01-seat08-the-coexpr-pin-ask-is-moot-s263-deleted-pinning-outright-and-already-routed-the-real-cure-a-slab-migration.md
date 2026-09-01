# FINDING: the coexpr-stack pin ask is aimed at a mechanism that no longer exists — Lon deleted pinning **outright** at s263, and the same commit already names the real cure and its precedent: **move the coexpr stack windows out of the compacting heap onto `rt_slab_region`**.

**Seat:** seat08 (FLEET-8) · **Date:** 2026-09-01 · **Row:** `icon-n2-recursive-generator-per-activation-storage` · **Found while:** doing that row's `NEXT ACTOR` item 1 — *"check whether the ruling has come back BEFORE writing code"* — and, per this row's universal rule, re-measuring instead of only reading the mailbox.

## THE ASK THAT IS OPEN

seat03 (same row, earlier today) root-caused the residue correctly: coexpr thread stacks are allocated from the GC heap as `HB_ZBLK` (`rt_coexpr.c:63`), handed straight to `pthread_attr_setstack`, and the compactor `memmove`s one **while a thread is running on it**. Their witness (`corpus/tests/icon/coexpr_gc_stack_witness.icn` + `.ref`) is in the repo and crashes in the **default** build. They found that re-pinning `HB_ZBLK` makes it `rc=0`/oracle-exact, correctly declined to land it, and asked HQ (`ask coexpr-gc-stack-pin-ruling`) because re-adding the pin would override a Lon deletion.

**That ask cannot be answered "yes", and it does not need to be answered at all.** Both halves below are measured against the tree, not argued.

## 1. THE RULING IS ONE SESSION STRONGER THAN THE ASK ASSUMES

seat03's FINDING cites **s262** three times — `gc_heap.c:698`, *"TYPE-BASED PIN REMOVED (Lon s262: 'Completely remove the PIN path. Let's see what breaks.')"* — and contains **zero** occurrences of `s263`, `PHYSICALLY DELETED`, `gc_zeta_frame`, `no need for pinning`, or `everything relocates` (grepped).

The current tree carries a later, harder ruling at `gc_heap.c:387`:

> ⛔ **PIN CODE PHYSICALLY DELETED (Lon s263: "We have no need for pinning anything").** `rt_gc_pin_ptr`, `gc_cons_scan`, `gc_cons_scan_t` and the `HBF_PIN` mechanism are GONE: every span that was conservatively PINNED is now scanned by `gc_zeta_frame`, which REGISTERS each pointer-holding location so the slide REPAIRS it. **Nothing is ever held in place; everything relocates.**

`HBF_PIN` no longer exists as a symbol (`gc_heap.h` defines only `HBF_TTL 0x0001` and `HBF_MARK 0x0002`). So the proposed repair is not "restore a removed arm" — it is "resurrect a mechanism Lon ordered physically deleted, whose verbatim justification is that we have no need for pinning anything."

⛔ **And the replacement doctrine structurally cannot cover this object.** "Register the location so the slide repairs it" works for pointer *slots*. A **running pthread stack** is not a set of registered slots: its live `RSP`, saved `RBP` chain, return addresses and every interior pointer sit in CPU registers and in the stack's own frames, outside any registry, being written by another OS thread *during* the collection. There is no repair map that makes a relocating pthread stack sound. **A block that cannot participate in "everything relocates" does not belong in the relocating heap** — which is exactly what the same commit concluded for a different object, below.

## 2. THE CURE IS ALREADY DESIGNED, ALREADY PRECEDENTED, AND WAS ALREADY ROUTED

The s263 landing commit is SCRIP `1257d56c`. Its own message states the precedent and then names this exact follow-up:

> the zh bump block **leaves the arena for `rt_slab_region`** (*an object handing out cursor addresses may not live in a compacting heap*) — `ZC_ZH_IN_GCHEAP` knob deleted; **coexpr stack windows keep their repair range, their slab migration is a routed rung.**

So at s263 the fleet already: (a) established the principle, (b) executed it once on the zh bump block, and (c) explicitly deferred the coexpr-stack instance as a **routed rung**. seat03's defect is that deferred rung coming due — not a new design question, and not a pin question.

**Destination verified before recommending it** (RULES.md's own meta-rule: *a ruling names a destination; grep the artifact that the destination EXISTS before implementing against it*): `rt_slab_region(size_t n)` is declared at `src/runtime/rt/rt_slab.h:20` and already used by `gc_heap.c`, `zeta_alloc.c`, `rt_arena.c` and `pattern_match.c`.

⚠️ **The rung appears never to have been minted.** No row in `QUEUE.tsv` and no task file covers the coexpr slab migration (searched `slab`/`coexpr` across both). The nearest rows are `coexpr-stack-of-calls-pthread-getattr-np-on-an-uncreated-thread` (rank 2 — which is seat03's own `NEXT ACTOR` item 2, so that second defect **is** owned) and `icon-coexpression-support-design` (rank 3, FREE). A rung named in a commit message but never minted is invisible to `next`, which is how this surfaced as a fresh Lon-ruling question four sessions later.

## 3. WHAT THIS CHANGES FOR THE ROW

The row is **not** blocked on Lon reversing himself. It is blocked on a rung the fleet already designed and deferred. The question HQ should be answering is therefore not *"may seat03 restore the pin?"* (near-certainly no, under s263) but:

> **Does the coexpr stack window migrate to `rt_slab_region` now, on the zh-bump-block precedent — and who mints that rung?**

That question is answerable without Lon, does not touch the deleted pin path, and preserves the information value of his experiment.

⛔ **I landed no code.** This row's `NEXT ACTOR` item 1 forbids it, item 3 requires full cross-language regression for any change on this shared arm, and the migration is somebody's minted rung, not a drive-by. Routed to HQ.

## THE SHAPE, because this is the second one today

This is the same failure I filed hours earlier on `raku-frontend-real-world-syntax-gaps` (`FINDING-2026-09-01-seat08-a-lon-ruling-reached-one-row-and-not-its-sibling-...`): **a later, stronger ruling exists, and the row acting on the earlier one never hears.** There it was an instrument ruling filed against one row; here it is a follow-up rung named only in a commit message. Both are invisible to `next`, to the baton, and to the queue index. **A rung that lives only in a commit message is not routed, however the message spells it** — if it is real work, it is a row.

## RECEIPTS

```
SCRIP 1257d56c   s263 landing: pin physically deleted; zh bump block -> rt_slab_region;
                 "coexpr stack windows ... their slab migration is a routed rung"
SCRIP gc_heap.c:387    PIN CODE PHYSICALLY DELETED (Lon s263), "everything relocates"
SCRIP gc_heap.c:698    TYPE-BASED PIN REMOVED (Lon s262)   <- the only one seat03 saw
SCRIP gc_heap.h:31     only HBF_TTL 0x0001 / HBF_MARK 0x0002 remain; no HBF_PIN
SCRIP rt_coexpr.c:63   coexpr stack allocated rt_gcheap_alloc(HB_ZBLK, ...) -> pthread_attr_setstack
SCRIP rt_slab.h:20     rt_slab_region(size_t) exists, 4 callers -- destination verified
QUEUE.tsv              no row for the coexpr slab migration (searched slab/coexpr)
```
