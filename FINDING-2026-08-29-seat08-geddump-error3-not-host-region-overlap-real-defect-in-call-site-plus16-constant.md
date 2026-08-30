# FINDING: geddump's Error-3 is NOT a host/N-2-region overlap (disproven numerically); a real, independent
# call-site address bug exists in `bb_call_proc_staged.cpp`, but is not yet proven sufficient to explain it

**Who/when:** seat08, 2026-08-29, `icon-n2-recursive-generator-per-activation-storage` row. Answers this row's
own live `## NEXT` item 1 (dump `icn_gen_host_slice`'s computed offsets for a host's locals vs. its N-2 region
and check additive-vs-overlapping), extending seat07's `FINDING-2026-08-29-seat07-geddump-error3-arr-corruption-
traced-to-stack-slot-collision-not-random-garbage.md`.

## Re-verified fresh first (this row's own repeatedly-learned lesson)

`make pristine` at SCRIP `211bd8e93c` / corpus `49a4cfff71` / `.github` `ec5e07360c`. Unchanged from the task
file's last record: unarmed `geddump.icn` refuses rc=134/526B (`[GENHOST]` cycle bomb); `SCRIP_ICN_N2_SELFREC=1`
reaches rc=1/65B `** Error 3 -- Erroneous array or table reference`, on both the full `.dat` and seat16's
200-line truncation.

## Part 1 — item 1 answered directly: the host/N-2 boundary is NOT overlapping (checked twice, independently)

`SCRIP_N2_OFFSET_SELFTEST=1` on `geddump.icn` prints `host=proc_gedload calls=1 total=21504 expect_sum=21504
AGREE` -- the transitive-reserve arithmetic is internally self-consistent (two independent derivations agree),
so the RESERVE TOTAL is not the defect. `gedload`'s emitted prologue is `sub rsp, 24448`. Since
`icn_gen_host_reserve_offset()`'s `base_out` for a `flat_lcl_proc` host is `flat_frame_bytes +
(nparams+nlocals)*16` (`x86_asm.h:958`) and the N-2 region is `[base_out, base_out+reserve)` sitting at the TOP
of the frame (`emit.cpp:2922`'s own comment), **base_out = 24448 - 21504 = 2944.** Seat07's observed collision
site, `[rsp+384]`/`[rsp+392]`, is deep inside `gedload`'s OWN protected `[0, 2944)` zone -- nowhere near the N-2
region. **The composability question this row's GOAL poses ("does the region carve land inside/adjacent to a
host local") has a clean, checkable, NEGATIVE answer for the flat_lcl_proc case: it does not overlap.**

Confirmed a second, fully independent way with a new minimal witness (Part 2): `main`'s frame there is `sub
rsp, 44560`, N-2 total (2 calls to `walk`) is 43008, so `base_out = 1552`; the corrupted local (`id`) lives at
`rsp+1440`, again strictly below the boundary.

**This redirects the row's own working hypothesis.** GOAL speculated this might be "a concrete, checkable
INSTANCE of the general storage-composition question." It is not that question -- the boundary arithmetic
between a host's own locals and its N-2 reservation is provably correct and non-overlapping. Something else is
corrupting a host local from inside its own protected zone.

## Part 2 — a new minimal, corpus-free reproducer (much cheaper than geddump.dat)

```icon
record node(sub, data, ref)

procedure walk(r)
    suspend r | walk(!r.sub);
end

procedure main()
    local id, root, r;
    id := table();
    id["a"] := 111;
    id["b"] := 222;
    id["root"] := 999;
    root := node([node([], "a", &null), node([], "b", &null)], "root", &null);
    every r := walk(root) do r.ref := id[r.data];
    every r := walk(root) do write(r.data, " -> ", r.ref);
end
```

Real oracle (`icont`/`iconx`): correct, `root -> 999 / a -> 111 / b -> 222`, rc=0. Unarmed SCRIP: rc=134,
`[GENHOST] host=pat_flat` cycle bomb (same shape as gedload's). Armed (`SCRIP_ICN_N2_SELFREC=1`): rc=1, `Error 3
-- Erroneous array or table reference` -- **the exact same failure signature as geddump.icn**, on 15 lines with
no corpus dependency. 200x+ cheaper to iterate on than the truncated `.dat`.

**Two control variants, both CORRECT, isolating that this needs genuine self-recursion:**
1. `every r := !recs do r.ref := id[r.data]` (plain list generator, no suspend at all) -- matches oracle.
2. A hand-written NON-recursive suspending generator (`every x := !lst do suspend x`) hosting the identical
   `r.ref := id[r.data]` shape -- also matches oracle.

Only the self-recursive generator (`walk` calling itself) breaks. This rules out a general N-2/host-suspend
bug (unlike the already-filed `bb_call_value.cpp` apply-call gap) and confirms the defect is genuinely scoped
to `SCRIP_ICN_N2_SELFREC`, matching this row's intended boundary.

## Part 3 — what's actually corrupted, gdb-confirmed on the minimal repro

The crash fires on **statement 0** -- the very FIRST generator activation (`r=root`), before any actual
recursive call into `walk(!r.sub)` happens at all.

Checked the mode-4 `.s`: `id := table()`'s `ASSIGN` writes the table value to `[rsp+1440]`/`[rsp+1448]`
(`n21_assign_α`). Later, the `r.ref := id[r.data]` statement's `VAR_REF` for `id` computes `lea rdx,[rsp+1440]`
-- **the identical address.** So, unlike geddump's read-side operand-slot-collision framing, in this repro the
addressing agrees: both writer and reader of `id`'s reference point at the same, correct slot. This is not a
slot-numbering disagreement.

gdb at `subscript_get` (breaking on the runtime C function, frame 2 = the JIT'd caller) confirms `arr`'s two
qwords, `{0x00007fff8b3fe040, 0x0}`, are exactly what's stored AT `[[caller rsp]+1440]` -- i.e. `id`'s own,
correctly-addressed slot has been **overwritten between initialization and use** with an unrelated
address-shaped value. (Caution, stated plainly rather than overclaimed: I have not independently proven this
specific bit pattern IS a saved-rbp/region value from this run, only that it looks address-shaped and that
`id`'s slot demonstrably no longer holds the table value it was assigned. Do not cite it as a confirmed saved-
rbp value without checking.)

## Part 4 — a real, confirmed, independent defect found by reading the source (NOT yet proven sufficient)

`bb_call_proc_staged.cpp:791-793`, the N-2 STEP 3 region hand-off, computes the region pointer for a
`flat_lcl_proc` host as:
```cpp
x86("lea", "rcx", RDQ("rsp", n2_base + n2_off + 16))
```
The comment justifying `+16` states plainly: *"pad+L7 = 16 bytes are already down since the carve."* But the
PRECEDING code (lines 766-780) pushes only **ONE** 8-byte word (`push rax`, the depth value) when the callee is
a self-recursive generator with `SCRIP_ICN_N2_SELFREC` armed (both its "I am the recursive call" arm, lines
769-777, AND its "first (non-recursive) call" arm, lines 778-779) -- versus **TWO** words (`sub rsp,8` + `push`,
16 bytes total) on the normal, non-self-rec path (line 780). **The `+16` constant is provably wrong for every
call from a flat_lcl_proc host into a self-recursive generator: only 8 bytes are actually down, not 16.**

Confirmed the exact call this affects via the existing `SEAT01_N2_STEP3_DBG=1` diagnostic on the minimal repro:
the crashing call (`main`'s first `walk(root)`) reports `off=0 base=1552`. Recomputing by hand: the LEA's actual
`rsp` at that point is `rsp0-8` (one word down, self-rec path); the buggy formula computes `R = (rsp0-8) + 1552
+ 0 + 16 = rsp0+1560`; the CORRECT value (had the constant tracked the true 8 bytes down) would be `rsp0+1552`.
**An 8-byte overshoot, deeper INTO the already-reserved `[1552, 44560)` region -- not reaching anywhere near
`id`'s slot at `rsp0+1440`, which sits BEFORE that region entirely.**

⭐ **So: this is a real, independently-confirmed, second instance of genqueen's Root-Cause-1 defect class**
(seat12's FINDING: the self-rec branch's push is narrower than what shared downstream arithmetic assumes) --
here in the CALL-SITE's region-address computation rather than the CALLEE-prologue depth readback seat12 found
-- **but by my own arithmetic it is not, by itself, large enough to explain landing all the way back at `id`'s
slot.** I am flagging it as confirmed-but-not-yet-sufficient rather than closing the loop, per this row's own
FACT RULE against a correct-looking mechanism standing in for a proven one.

**One more thread, NOT chased down, flagged only:** `walk`'s own compiled prologue does `mov rax,[rsp+16]; mov
[rax+288],rbp` -- writing the saved caller `rbp` at offset **+288** from the region pointer it receives, not
+0. 288 is exactly one self-rec slot's size (`align16(fb_walk)+48` for this repro). This suggests the first
activation may be landing in slot index 1 of the 64-slot table rather than slot 0, or that the region pointer
callers push is already meant to be pre-offset by one slot and something upstream double-counts it -- worth
checking directly, not verified this pass.

## Not attempted

No fix landed, no source touched. Root cause 2 (genqueen's sibling-generator reservation formula) and mutual
recursion (c) remain untouched and are still explicitly Lon/hq design territory per this row's GOAL. The Part 4
defect looks narrow/mechanical (matching an already-agreed contract) rather than a new design question, similar
in kind to genqueen's Root Cause 1 -- but per this row's own standing discipline (every prior session
characterized rather than landed a fix solo on this shared arithmetic), and since my own hand arithmetic in
Part 4 already shows the effect is NOT large enough to be sufficient by itself, I did not patch and rebuild to
test it further this pass -- that is next actor item 1 below, done for real rather than by hand.

## Suggested next step, not decided here

1. **Cheapest next move**: fix the confirmed `+16`-assumes-16-bytes-pushed defect at `bb_call_proc_staged.cpp:
   791-793` to reflect the true byte count (8 for the self-rec branches, 16 for the normal branch -- the same
   boolean condition already computed at line 767 is available at line 793) and re-run the minimal `vsr3.icn`
   repro above (no corpus dependency, seconds to iterate). If it now matches the oracle, this was sufficient
   and the fix needs the full-rigor treatment (gdb end-to-end, dedicated bound witness, full regression) before
   landing, per this row's standing rule. If it still fails, the corruption has a second, independent cause --
   the `walk` prologue's `+288` offset (Part 4, last paragraph) is the next concrete thing to check.
2. Root cause 2 (reservation formula) and mutual recursion (c): unchanged, still Lon/hq territory.
