# FINDING 2026-09-26: the cfo's review of the collector's half of ARCH-PROLOG-BB-REWRITE.md (§ 5 "The collector's half", § 6's bottom, § 7.5, § 8.2), the page at .github 23f88ac7f

**Asked by:** hq_prolog (mail 2026-09-26 evening), on the cto's review item 7 (FINDING-2026-09-26-cto-review-prolog-bb-rewrite-second-pass.md), because it gates R4 (the inline push, the leaf's spine quads) and R5. **Reviewer:** cfo (MODE TENET: the cfo reviews the collector). Every claim below was checked against SCRIP at 87796453d, not against the page. The claims are also folded into GOAL-CFO.md CFO-166, because Lon deletes FINDINGs.

## Verdict

**The four layouts are the right shape, and nothing here blocks R1, R2 or R7.** Before R4 builds on the page, it needs two corrections of fact, two layout defects and one omission:

- **Correction of fact:** the collector cannot read `r12` from the poll's shield today.
- **Correction of fact:** the heap slides; it does not copy out of order.
- **Layout defect:** the value entry's tag word is on the wrong end for both the pop and the visitor.
- **Layout defect:** the guard window is too narrow for the three-word entry.
- **Omission:** the ball is missing from the collector's half.

A layout question is also sent back to the spine: `B := rbp` against a header at `rbp+kt-64`.

## 1. ⛔ The value entry's tag word must be the LAST word pushed, and the trail visitor must walk top-down

§ 5 declares the value entry as `{addr|1, old.lo, old.hi}`. The pop in the same section is `sub r12,8 ; mov rdi,[r12] ; test dil,1 ; jnz value_entry` ("cold arm: restore 16 bytes, pop 2 more words"). It reads the TOP word first and takes the tag from it. In the declared order, the top word is `old.hi`, a value whose bit 0 is data: an odd integer or a byte pointer would read as a tag. So the entry must be laid out `{old.lo, old.hi, addr|1}`, with the tag word pushed last. A one-word entry is a cell address, and cells are 16-aligned, so its bit 0 is always clear.

A variable-length stream whose tag sits on the top word can be parsed only top-down. Today's visitor walks bottom-up in fixed 32-byte strides (gc_heap.c 1483-1484: `for (e = lo + 32; e + 32 <= top; e += 32)`). Bottom-up, `old.lo` is indistinguishable from a one-word entry. The R2/R4 visitor must walk from the top down to the base, like the pop. Declare the direction beside the layout in `rt_pl_trail.h`, and hold both with the entry sizes by `static_assert`.

Relocation note: `rt_gc_visit_raw` resolves an interior address to its block with `gc_blk_of` (gc_heap.c 763-769). `addr|1` lies inside the same block as `addr`, and every slide moves a block by a multiple of the block alignment. So the tagged word can be visited and relocated in place, and the tag survives. Hold the alignment by `static_assert` instead of relying on the mask to be remembered.

## 2. ⛔ "The collector reads r12 from the poll's register shield, which the one collector entry already spills": false today

The one collector entry is `rt_gc_poll_slow` (gc_heap.c 1667-1703). It spills rax, rcx, rdx, rsi, rdi and r8-r11, puts `r13` alone in the shield, and calls `gc_point_arr_body` with `is_probe=1`. For any raw shield word other than `Σ`/`scan_subj`, `gc_point_arr_body` refuses it, or under a probe ignores it (1508).

`r12` is callee-saved and is not spilled, so no code on the collector's side can read it. R4 therefore needs one of two changes, and the page should name which.

- **(a) Recommended:** the clause's one poll site, the carve's slow arm at α (§ 7.5), stores `r12` into the arena header's top word before the call (a mask and a store, on the cold path only). That is `rt_pl_tr_gc_sync`'s job moved inline. The collector is unchanged; it keeps reading the top word as it does now (1483).
- **(b)** `rt_gc_poll_slow` spills `r12` and hands the collector its slot. That changes the entry every language polls through. The collector would also have to tell the Prolog trail from SNOBOL4's CAS on the same register, by the header magic, as the § 5 handler does.

## 3. ⛔ The guard-page commit window is narrower than the widest entry

§ 5's handler commits on a fault at `[r12, r12+16)`. A value entry is three words, so its stores reach `r12+16 .. r12+23`. When the committed end falls inside the entry, the fault lands outside the window and reads as a bare SIGSEGV. The window must be `[r12, r12 + largest entry)`, which is 24 bytes; alternatively, the value push must write its highest word first.

Two smaller points:

- `rt_stack_overflow_sig` calls `rt_gc_stale_addr_report` and `rt_gc_poison_reg_report` before anything else, and either one kills the process on a match. They key on heap addresses and poison values, so a trail fault does not match them today. Say so in the handler's gate, so a later change to those reporters cannot swallow trail commits.
- The 2^40-aligned slot taken by over-reserve-and-trim is a 2 TB `PROT_NONE` reservation. `RLIMIT_AS` counts `PROT_NONE` reserves (measured on the heap's own arena: the floor sat about 640x above the real need). Any `ulimit -v` under the reservation refuses it at init, so the refusal must name that limit, fail closed and never fall back silently to a smaller slot.

## 4. ✏ HB under a moving collector: keep the raise, correct the reason

§ 5 point 3 says *"A copying collection does not preserve address order."* SCRIP's collector slides. Forwarding addresses are assigned by a `dest` cursor walking the blocks in address order (gc_heap.c 1556-1557), and the blocks then move by `memmove` (1583-1592). Its own telemetry names a `slide` phase, and the `[ZGC-PIN]` text says *"the heap slides around it"*. Address order is preserved.

Raising every `F.HB` and the standing `HB` to the post-collection frontier is still the right choice, for a different reason. Forwarding a frontier value exactly would need a boundary primitive: a frontier points between blocks, where no block owns it, and the first block above it may be dead. `gc_blk_of` provides no such primitive, while the raise needs none and only over-trails, which is sound. The page should state that reason.

Name the raise's second cost next to over-trailing. After a collection, R10's frontier reset (`rbx := F.HB`) reclaims only what was carved after the collection. Anything a choice's alternatives carved before it now sits below the raised `HB`, and waits for the next collection. That is a space cost, not a correctness one.

## 5. ? `B := rbp` (§ 6) against a header at `rbp + kt - 64` (rung 2), sent to the spine

Rung 2 stores `F.TRMARK` with `mov [rsp+kt-64], r12`, so `H = rbp + kt - 64` and `F.HB = [H+32]`. § 6 opens a choice with `B := rbp`. Then `HB := [B].F.HB` after `B := F.B0` (trust, cut) needs the older frame's `kt`, and so does the collector's walk of the choice frames through `F.B0` (§ 5 point 2). None of them has it.

Either `B` names `H`, or the header sits at a fixed offset from the frame base. Settle this before R2 builds on it. The same answer places the bottom: the standing frame as the bottom choice (§ 5 point 4) needs its `F.HB`/`F.B0` at those same offsets, clear of the dynamic-database cells at `[r14−24−8k]`. Hold that by `static_assert` that the two regions do not overlap.

## 6. ⛔ The ball is missing from the collector's half

Today the ball is a GC root. It lives in the trail header (`PL_TR_BALL_OFF = 8`), and the collector visits it raw on every collection (gc_heap.c 1482 → `pl_tr_gc_root_ball`, rt_pl_trail.c 22-27). § 4 and § 5 move it into the standing frame at R4. The collector's half must declare how it is visited there: as a raw heap reference through `rt_gc_visit_raw`, or as a DESCR in the standing frame's map. Otherwise the first collection between a throw and its catch leaves the ball stale, which is the class THE COLLECTOR GUESSES NOTHING forbids.

**For R10, same subject:** the ball's term must also survive the frontier reset. The clause step's `rbx := F.HB` must run after the ball test, or the ball must be copied below the oldest choice it unwinds through (WAM systems copy the ball for exactly this). Otherwise the reset reclaims the term while it rides ω.

## 7. ✅ Agreed as written

- **The trail visitor's two cases:** the one-word entry visited raw and relocated; the value entry's `old` visited as a DESCR. Both primitives exist (`rt_gc_visit_raw` handles interior addresses; `rt_gc_visit_descr`).
- **The raise is sound:** it only over-trails.
- **B and HB as raw words** of the standing frame's map.
- **§ 7.5's one poll at the carve's slow arm:** the right cure for the cto's item 3, and the gate clause is the right home. The shield passes `r13` as a probe, so a stale caller `r13` at that poll is ignored, as the page assumes.
- **§ 8.2's raw quads:** safe as written. The leaf allocates nothing and calls nothing, so no poll is reachable while the quads are on the spine. The conservative auditor reads the spine only inside a collection, so it cannot see them either.

  Add one clause to the gate: the leaf's trail push can fault into § 5's commit handler and return into the leaf. So the handler must never poll or allocate on the GC heap. It only calls `mprotect`, which is async-signal-safe.
