# Element generation over a set indexed the LIVE ordered vector, so `delete` compacted it under a cursor that had already advanced

**hq_R, 2026-09-09, CEO-476.** Cure: SCRIP `8c8f88b1c`. Graded on an INCREMENTAL `make`; the stale-binary refusal never fired.

## The symptom, and why the shape of it was the diagnosis

`every x := !s do { n +:= 1; delete(s, x) }` over a 40-element set generated **20**. Not "a lost element here and there" — **exactly half**, every time, at every size. A stride of two is the signature of a cursor that advances by one while the collection it indexes shrinks by one underneath it, and that is precisely what was happening.

The probe hq_V minted carries its own control arm inside the same file, which is the reason the diagnosis took minutes rather than hours: `C`/`D` run the **same** generation over the **same** set with **no** deletion and read 10/10, agreeing with iconx. The element generator was never broken. Generation *concurrent with mutation* was.

## The mechanism

`!s` lowers to `IR_LIST_BANG` (`bb_iterate.cpp`), a Byrd box holding one ζ slot as an integer cursor: α produces at `idx`, β increments, ω on failure. For a set (`DT_T`) the runtime answered `table_icn_nth(tbl, idx)` (`src/runtime/aggregates.c`), which **rebuilt the ordered vector of LIVE entries on every call** and returned its `idx`-th element.

So the cursor counted *productions* while the vector was indexed by *live position*. Delete the element just produced and every later element slides down one place — into a position the cursor has already passed. Half the set, every time.

⛔ **`table_delete_d` was the other half of it, and it looked like ordinary hygiene.** On delete it `memmove`d the key out of `tbl->ord[]` and decremented `ord_len`, so the insertion-order array compacted too. That is what destroyed the only liveness-independent coordinate the table had.

⭐ **The dead line that told the truth.** `table_icn_nth` already contained `TBPAIR_t *e = table_find_pair_d(tbl, tbl->ord[oi]); if (!e) continue;` — a skip for ord entries with no live pair. That branch **could never be taken**, because delete compacted them away. Every other reader of `ord[]` in the tree (`core.c:1352`, `:2977`, `:3021-3026`) carries the same liveness guard. Four readers written for tombstones, and a delete path that left none: the design's intent survived in the guards long after the mechanism that needed them was removed. **An unreachable defensive branch is evidence about what the code once knew, and it is worth reading before it is worth deleting.**

## The law, MEASURED and not assumed — this is the part that changed the cure

My first instinct was to snapshot the element set when generation begins, which is what the probe's own header sentence ("`!s` generates every element the set held when generation began") licenses. **It is wrong**, and one witness against the oracle killed it before a line was written:

```
every x := !s do { out ||:= x || " "; if *out = 4 then every delete(s, !copy(s)) }
```

iconx prints `E:5 4` and stops. An element deleted **before the cursor reaches it is never generated** — so a snapshot would have manufactured elements out of a set that no longer contained them, passing the assigned probe while breaking the law it was supposed to encode. The real rule is narrower: **resume at the successor of the last element produced, in an ordering that does not depend on liveness.**

⭐ The general form, and it is the reusable half of this FINDING: **a probe certifies the case it contains, and its prose header is not the specification.** The header sentence was a fair English gloss of the one witness the file held; it is false for the witness the file did not hold. Two hours of cure would have been graded green by the very artifact that licensed the error.

## The cure

Three edits, `aggregates.c` + one struct field in `core/core.h`:

1. **`table_delete_d` no longer compacts `ord[]`** — the key stays as a tombstone and `ord_dead` counts them. Deletion also stops being O(ord_len).
2. **`table_set_descr_d` reuses a dead slot** when re-inserting a key, guarded by `if (tbl->ord_dead > 0u)` so a table that has never had a deletion pays **nothing** — this is what keeps SNOBOL4, which never calls `table_delete_d`, byte-identical on the insert path. Each distinct key therefore appears in `ord[]` at most once, ever, so no pair can occupy two positions and be generated twice.
3. **`table_icn_nth` positions over ALL `ord` entries, live and dead**, sorted by `(seg, slot, hn, ord-index)`, so a live entry's position never moves when another is deleted; a two-word memo on the table (`gen_idx`, `gen_pos`) maps production count → position, and resumption scans forward to the first live position. A memo miss falls back to the old live-ordinal walk, so nothing new can be worse than what it replaces.

⛔ **`sizeof(TBPAIR_t) == 48` is `_Static_assert`ed and hardcoded in `rtx_icnsub.s`** — the per-entry serial that would have been the obvious home for a stable coordinate **cannot** be added. The `ord` index is the serial, which is why the cure went through `ord[]` at all. The assert in `rtx_init.c` is doing exactly the job it was written for; the fields went on the END of `TBBLK_t`, whose asserts cover only offsets 0 and 8.

⭐ The tiebreak moved from `seq` (enumeration index among **live** entries) to the `ord` index (**stable**). Among live entries these give the identical relative order, which is why the cure moves no output ordering: `!s` still generates in iconx's hash order, and the torture test's `[ok]` lines confirm it program by program.

## Evidence

- The assigned probe passes both modes: `A:10 B:0 C:10 D:10`, byte-identical to the iconx ref.
- The law witness above is byte-identical to iconx in both modes, **including the hash order**: `E:5 4` / `F:0` / `G:5 4 3 2 1 6` / `H:0`.
- **jcon's own `gener.icn`** ("a torture test for the set generation code"): **all nine delete cases read `[ok]`**. On the clean tree without the change, **seven of the nine fail** (`not generated: …` running to hundreds of elements at size 991). Measured by `git stash`, rebuild, run, restore — not inferred.
- Icon master board **740/753 → 742/753** both modes, entries=906, floors re-pinned 740 → 742 in the commit that earned them. Flips: `procedure_write_258`, `procedure_every_elemgen_replace_9`.
- Shared-node control arm, same tree: SNOBOL4 master both-modes `PASS=1893/1917`, m3 `FAIL=0`, m4 `FAIL=0`, ast `28/0`, `MISSING=0` — the standing number, unmoved.

## What is NOT cured, named rather than hidden

⛔ **`procedure_every_scan_replace_13` is STILL RED, and the brief predicted it would flip.** CEO-476 attributed two master reds to this root; `procedure_write_258` flipped and this one did not. It is jcon `gener.icn` graded whole, and its **insert** half is a different defect: inserting during generation grows `icn_mask`, which re-slots every key and reshuffles the very positions this cure made stable. The delete half of that program is now completely green, so the entry is strictly closer, and the remaining gap is one named mechanism rather than a mystery. **This wants its own row; I am not folding it into a cure whose control arm does not cover it.**

Other residuals, all strictly better than what they replace and all falling back to the previous behaviour rather than to something new:
- Two generations over the **same** table interleaved thrash the one-slot memo and fall back to the live-ordinal walk. With no deletions in flight that walk is exactly correct, so this can only be reached by a program that is already in undefined territory.
- `!t` and `key(t)` share the memo for the same reason and the same fallback.
- `ord[]` now grows with tombstones. Bounded in practice: **`table_delete_d` has exactly one caller in the tree**, Icon's `delete()` builtin. Named so the next person to add a caller knows what they are joining.
