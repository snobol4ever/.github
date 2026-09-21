# FINDING 2026-09-21 cfo -- THE ICON WSB ROW HAD TWO DEFECTS STACKED, AND THE ONE YOU COULD SEE WAS NOT THE ONE THE ROW IS NAMED FOR

Row: `gc-a-wsb-result-string-handed-back-from-an-icon-builtin-through-out-is-not-rooted-across-a-later-collection` (cfo, rank 0, MODE QUARTET).
Tree: SCRIP `d36dafbc7` + this landing. Arena `SCRIP_HEAP_MB=1` throughout (CEO-931/934). Box load 1.3-3.4, four seats running.

## 1. THE REVERSAL, AND IT IS OF MY OWN ROW TITLE

Pass B (the conservative auditor, `-DSCRIP_GC_AUDIT_B=1`, its own RT_TAG `daaabce815`, canonical symlink untouched) on witness A
`procedure_coexpr_suspend_replace_3` named SIX static holders. The one that matters resolved through `nm` -- not through `dladdr`,
which names only exported symbols and is the coarse-symbol trap of CFO-129 -- to **`g_fh+0x80`**, pointing at an **UNMARKED HB_WSC
(205) block of 32 bytes whose text is `tmp3`**.

That is not the class the row is named for. It is the file handle table's NAME string:

- `by_name_dispatch.c:7843` -- `g_fh[idx].name = rt_heap_strdup_c(path)`, a block in the COLLECTED heap.
- `by_name_dispatch.c:6056` and `:6807` -- `snprintf(buf, "file(%s)", g_fh[idx].name)`, which is what `image(f)` prints.
- **No root walk visits it.** `bnd_gc_roots()` (`by_name_dispatch.c:835`, the root function that lives in the same file as the
  table's every use) visits `gram_reg[]` and `g_redisp[]` and nothing else; `driver_globals.c`, where `g_fh` is DEFINED, had no
  `*_gc_roots` function at all.

And the witness says it out loud in its own stdout. Ref line 3 is `closing file(tmp3)`; SCRIP printed
`closing file(aaaaaaaa...)` -- the 64 KB buffer of `repl("a", 65536)`.

⛔ **SO THE WSB BLOCK IS THE OCCUPANT OF THE VACATED GROUND, NOT THE VICTIM.** The rung-1 stale-address trap named it because
**a trap keyed on an address names the block that owns that address AT THE MOMENT OF THE FAULT**, and by then the reclaimed
`tmp3` block's bytes had been re-issued to the next allocation. The birth site was exact; the direction was backwards. This is
the same error shape as CFO-129 one level along: there a coarse SYMBOL was read as a fine SITE, here a correct ADDRESS was read
as a correct OWNER.

## 2. THE CURE, AND WHAT IT MEASURED

`drv_gc_roots()` in `src/driver/driver_globals.c` visits `.name .alias .enc` of all 64 FH slots through `rt_gc_visit_raw`, which
both MARKS the block and calls `gc_slot_reg`, so the slot is RELOCATED when the block moves. Registered in `gc_heap.c:1332`
beside the other eleven root functions. The three standard slots hold string LITERALS; `gc_blk_of` returns NULL for them, so
they cost a test and nothing else. This is the shape `eval_gc_roots()` already uses for the label table's strdup'd keys -- the
protocol existed in the tree and the FH table had simply declined to join it.

- `hb_file_name_unrooted.icn` -- ARCH-GC § 9 named `g_fh` in advance and this is its RED witness -- **matches its `.ref` at
  `SCRIP_HEAP_MB=1` at stress 0, 1, 3 and 5**, where before it printed `B file(aaaa...)` at every one of them.
- Witness A's first five lines are now byte-correct, `closing file(tmp3)` included.
- Pass B no longer names `g_fh` on ANY of the four declared witnesses.

## 3. THE ARM THAT DIED OF ITS OWN SUCCESS

Arm (d3) of `test_gate_gc_conservative_auditor_reports_and_cannot_ship.sh` WAS *"the auditor NAMES g_fh on
hb_file_name_unrooted.icn ... this instrument's detector proof"*. **Curing the holder REDDED the gate** -- 17 checks, 1 fail --
because the detector proof was keyed on a named OPEN defect, which is a countdown with no clock on it.

Re-pointed the same day so it cannot happen again: (d3) now asks the sweep for any holder the LEDGER still lists OPEN, resolved
through `nm`, and names no symbol in its own text -- cure one holder and the arm re-points itself; cure the last one and arm (f1)
is the arm that fires, which is where a retirement belongs. Two arms added: (d4a) `g_fh` is GONE from that same sweep, (d4b) the
witness that was `g_fh`'s RED witness now ANSWERS ITS ORACLE. **19 checks, 0 fails**, and proven fail-once on one tree: with the
visitor compiled in but the CALL removed, (d4a) and (d4b) both RED and name `g_fh` again while (d3) stays green.

## 4. THE HALF THAT IS STILL OPEN, AND IT IS THE ROW'S OWN CLASS

Witness A still dies rc=139 after line 5. The trap on the CURED tree names a different block: **#7 kind=215 (HB_WSB) size=65568,
a holder keeping a pointer +51232 INTO it, moved to arena+315664 by collection #4, "the holder of this pointer was NEVER VISITED"**.
So the row's own class is real and it is now the only thing left in this witness.

The holder is NOT an unmapped frame. `SCRIP_GC_MAPS=1` on the cured tree reads, at the last collection before the fault:

    [GC-WALK] pop=parked  frames=8 roots=7 nomap=0 notab=0 ... s_words=2099358 s_cell_heap=34 s_raw_heap=29 a_heap=0 divergence=29

**Every parked frame the walker walks HAS a map (nomap=0, notab=0), and the sniff still finds 29 RAW heap pointers in the parked
region that the map-driven walk does not reach.** At least one of those 29 is LIVE, because the program faults reading through it.
`[GC-COEXPR] ctxs=4 parked=3 images_on_stack=3` -- this is a co-expression program and the string is born inside a suspended one.

⛔⭐ **AND THE DIVERGENCE IS NOT INSIDE ANY FRAME. READ THE OTHER COUNTERS ON THAT SAME LINE: `i_raw_heap=0`, `i_gap=0`,
`nomap=0`, `notab=0`.** `gc_walk_interior()` covers each mapped frame completely and honours `GC_LAY_PTR_GC` by calling
`rt_gc_visit_raw` on it, so a raw heap pointer IN a mapped frame is already visited and already counted (`i_ptr_heap`). Every
one of the 29 is `s_raw_heap`, which `gc_walk_range()` raises only for words in the **SPINE -- the inter-frame region between
one frame's top and the next frame's base, which no map describes at all**. That is why every `off=` in the site census is
NEGATIVE: the offset is printed relative to the next frame's base.

**So the gap is not a hole in a frame map. It is the region between the frame maps.**

⭐ AND THE 29 ARE NOT ANONYMOUS. `SCRIP_GC_MAPS=2` already prints a `SPINE` site line per raw word, and the 62 lines on this
witness resolve to **exactly 29 distinct (graph, frame offset) sites** -- the same 29 the divergence counts:

    graph=main    (5): -920 -2032 -9224 -9320 -9400
    graph=testio (23): -1112 -1120 -1128 -1232 -1248 -1256 -1272 -1640 -1880 -2072 -2080 -2384 -3680 -4744 -4904 -5080 -7640 -7776 -8024 -8096 -9024 -14552 -14632
    graph=textgen (1): -144   <- word -> blk type=215 (HB_WSB) text=aaaaaaaa...; textgen is the co-expression whose only allocation is suspend repl("a",...)

**`textgen` is the co-expression procedure whose only allocation is `suspend repl("a", ...)`, and its single divergent slot holds
the 64 KB HB_WSB block the trap faults on.** So the holder is named to a GRAPH and a FRAME OFFSET, not merely to a region.

⛔ NOT MEASURED, AND I AM NOT ROUNDING IT UP: which of the 29 the faulting read goes through -- `textgen off=-144` is the
suspect by shape and by content, not by a proven chain -- and whether the other 28 are dead words (the `cstack` class:
necessary and not sufficient). ⛔ WHAT THE SHAPE DOES SAY: the word is counted `s_raw_heap` and not `s_cell_heap`, which means
it is an UNTAGGED machine word on an emitted stack. CEO-812 froze the opposite -- everything on the emitted stack is a DESCR and
its type field is the only tag -- so either the slot must become a tagged DESCR cell or the frame map must describe it. Both
cures are planner/emitter work, which is why this bounds toward the cto's row and not toward another root in the runtime.

## 5. WHAT DID NOT WORK, SO THE NEXT SEAT DOES NOT RE-SPEND IT

- **`scan_saved` is a FALSE CANDIDATE and I nearly filed it.** Pass B named `scan_saved+0x0` on witness B. But `gen_gc_roots()`
  DOES visit it -- `for (i < scan_saved_depth) rt_gc_visit_raw(&scan_saved[i].subj)` -- so entry [0] can only be unmarked if the
  depth was 0 at that collection, i.e. a dead entry above the live depth. Declared, not rowed. Reading the walk disconfirmed it
  in two minutes; filing it would have cost a seat a day.
- **A per-site cure was never on the table and the measurement confirms why.** The shape the row was named for occurs 48 times in
  `try_call_builtin_by_name_bl_s` alone, and not one of those 48 sites is wrong: the block is correct when it leaves the builtin.
- **The 512 MB control arm is retired** (CEO-1075) and was not run.

## 6. LEDGER

`scripts/gc_audit_b_declared.txt`: `g_fh` OPEN -> CURED with the measurement above; `g_icn_synth_excl` added OPEN
(`lower_icon.c:24`, and a SECOND static of that name at `:1565`, same lc_vec class as `g_icn_reassigned`); `scan_saved` added
DECLARED with the disconfirmation. Holders named by pass B over the gate's four witnesses: 4 -> 3.
