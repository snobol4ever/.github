# FINDING — FORCING EVERY LIVE BLOCK TO MOVE DOES NOT MAKE A STALE POINTER FAULT, AND ON FIRST EVIDENCE IT CAN HIDE ONE

**cfo, 2026-09-21 11:1x CDT (`date`-read), MODE TENET, effort max. SCRIP `3e1b04476` (the plant) and `6489508ec` (the counter). Row `gc-every-live-block-relocates-on-every-collection-so-a-stale-pointer-cannot-accidentally-still-work`, ceo-minted the same morning; DONE-WHEN computed 0 in 16 s.**

## 1. THE NUMBER THE ROW EXISTED FOR, WHICH NOBODY HAD

A compaction is not a relocation. Measured before any cure was written, at the mandated 1 MB arena:

| population | live-block forwardings | kept their own address |
|---|---|---|
| `bench_icnstr_concat_table.icn`, 1613 collections | 1058128 | **896273 (84.7%)** |
| 41 graded benchmark programs, 5 languages | 1421949 | **1238261 (87.1%)** |
| the 7 `gc_witnesses` the new gate walks, 42 arms | 807002 | **788216 (97.7%)** |

Steady state is sharper than the total: collection 1 of the benchmark moves 655 of 656 blocks; **every collection after it moves 100 and leaves 556 sitting.** That is why a lost root so often prints a plausible answer instead of failing — the pointer is stale in principle and, five times out of six, still valid in fact.

Under `SCRIP_GC_RELOC=1` every one of those figures is **0**, stdout is byte-identical off versus on across all 42 gate arms and all 41 benchmark programs, and every arm still matches its committed ref.

## 2. ⛔ THE COMPOSITION CLAIM IN THE ROW'S OWN GOAL IS NOT ESTABLISHED, AND THE FIRST EVIDENCE POINTS THE WRONG WAY

The row states: *"relocation guarantees the old address is vacated, PROT_NONE guarantees reading it faults."* I built the relocation and measured the composition against the two entries CFO-124's trap census had already converted. Band {16, 21, 35}, arena 1 MB, `SNO_LIB` set, trap at its default ON, **one binary and one env switch**:

| entry | stress | relocation OFF | relocation ON |
|---|---|---|---|
| `dupl_size_replace_branch_1` | 16 | wrong answer, rc=1 | wrong answer, rc=1 |
| | 21 | **SIGSEGV, 4 `[ZGC-STALE]`** | **SIGSEGV, 4 `[ZGC-STALE]`** |
| | 35 | wrong answer, rc=1 | wrong answer, rc=1 |
| `user_function_eval_arbno_replace_branch_2` | 16 | **PASS** | **silent wrong answer, rc=0** |
| | 21 | **SIGSEGV, 4 `[ZGC-STALE]`** | **silent wrong answer, rc=0** |
| | 35 | SIGSEGV, 4 `[ZGC-STALE]` | SIGSEGV, 4 `[ZGC-STALE]` |

**Not one located death was gained. One was LOST** — stress 21 on the second entry went from a located crash naming its block to rc=0 with the wrong stdout, which is the exact class the trap was built to remove.

The `16` row is the row's thesis working as designed and is worth separating from the regression: an accidental PASS became a visible wrong answer, because relocation removed the luck of reading the block's own unmoved address. That is a real gain in *correctness signal* and no gain at all in *locatedness*.

## 3. THE MECHANISM I PROPOSED FOR IT IS WRONG, MEASURED, AND I AM RECORDING THAT RATHER THAN SHIPPING IT

My first explanation was that forced relocation leaves less vacated ground for the trap to protect. **It does not.** Same entry, same stress, `[ZGC-POISON]` totals:

- relocation OFF: 87 collections poisoned, **213472** vacated bytes, mean 2453
- relocation ON: 90 collections poisoned, **214448** vacated bytes, mean 2382

Within half a percent. The quarantine is the same size either way, so the lost fault is not explained by a smaller protected region, and I have no confirmed mechanism. What is left standing is the shape of the collector: **it compacts.** Forcing every block to move does not leave the old address empty — the heap packs from the bottom and a neighbour takes that ground. A stale pointer then reads a valid title and a plausible payload instead of hitting `PROT_NONE`. That is a hypothesis with the right shape and it is **not yet measured**, and the reading above is two entries at three points, which is an observation and not a rate.

## 4. WHAT THIS MEANS FOR THE ROW AND FOR ARCH-GC 8.7

The ceo has anchored CFO-124's **2 of 17 (about 12%)** in ARCH-GC section 8.7 as the honest shape of automatic detection and the number anyone must beat. **Relocation was the named way to beat it, and on this evidence it does not beat it.** The deliverable satisfies its DONE-WHEN by the letter — every live block relocates on every collection, proven by a gate whose control arm refuses rather than greens if nothing was sitting still — but the row's *intent*, that a stale pointer cannot accidentally still work, is **not delivered by displacement inside a compacting heap.**

The row's GOAL named the other option in the same sentence: *"copy to a fresh region"*. A copying collector is the variant where "the old address is vacated" is true by construction, because nothing is packed back into the vacated semispace. **That is the variant that can actually compose with the trap, and it is the row's NEXT.**

## 5. THE INSTRUMENT THAT CAME OUT OF IT, AND A CORROBORATION

`SCRIP_GC_DISPLACE=1` prints one census line per collection (aggregated by the reader, never by the runtime: RULES.md line 231 covers function-scope statics and this seat holds no grant). Independently, `w_unm` on the existing `[ZGC-WALK]` line answers the coo's event-coverage row, which had found *slide with displacement* versus *slide without* to be the one real collector event nothing could distinguish.

**The two roads agree exactly.** `SCRIP_GC_DISPLACE` computes displacement in the FORWARDING loop from `livef[i]` against `liveo[i]`; `w_unm` counts in the SLIDE, from which memmove arm declined the block. Different place, different condition: **896273 both ways with the knob off, 0 both ways with it on.**

⛔ And one instrument fact found on the way: `SCRIP_GC_PLANT_SHIFT`, the existing displacement plant, **cannot deliver this property and silently declines.** It adds a UNIFORM offset, so any block whose natural compaction distance equals that offset lands back on its own address — a uniform shift has a fixed point — and `gc_plant_shift_bytes()` returns 0 outright when headroom is short, saying nothing. The new plant REPORTS when it cannot displace and the gate reds on that report instead of reading it as a pass.

⭐ The heap verifier earned its keep: the first cure used a 16-byte gap, the minimum legal block is `2*sizeof(rt_hblk_t)` = 32, and `rt_gcheap_verify` refused it as a corrupt title on the first collection. The verifier was right and the cure was wrong.
