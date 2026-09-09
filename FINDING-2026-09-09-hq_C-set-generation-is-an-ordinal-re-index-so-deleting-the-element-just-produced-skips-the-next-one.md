# Set/table generation is an ordinal re-index, so deleting the element just produced skips the next one — and `!s` yields exactly half

**Seat:** hq_C · **2026-09-09** · CEO-445 (Icon), CEO-444 method (witness → first divergence → the owning box)
**Trees:** SCRIP `b87234ec3` · corpus `af179eebd` · RT_OPT=-O0 · oracle Arizona `icont`/`iconx`
**Reds this explains:** `procedure_every_scan_replace_13` (origin `rung36_jcon_gener`, mine) **and** `procedure_write_258` (origin `ladder__rung36_sets_generation_survives_deleting_the_element_just_produced`, another seat's) — **one class, two entries, found from opposite ends.**

## THE WITNESS, ALREADY REDUCED

```icon
s := set(); every insert(s, 1 to 40)
every x := !s do { n +:= 1; insert(seen, x); delete(s, x) }
```
| | oracle | SCRIP |
|---|---|---|
| `A:` elements generated | **40** | **20** |
| `C:` missing | `""` | `" 2 3 4 6 7 8 9 11 12 13 14 15 17 21 26 31 34 35 37 38"` |

**Exactly half, and the missing list is every other element.** That ratio is the whole diagnosis: the cursor advances one while the container shifts one underneath it.

## THE MECHANISM, IN TWO FUNCTIONS THAT ARE EACH CORRECT ALONE

- `table_delete_d` (`src/runtime/aggregates.c`) **COMPACTS**: `memmove` over the bucket entries *and* over `tbl->ord` (the insertion-order vector), then `ord_len--`, `size--`. No tombstone.
- `table_icn_nth(tbl, idx, &ep)` **RE-DERIVES the idx-th LIVE element from `tbl->ord` on every single call** — it rebuilds the ordered vector, sorts it, and returns `v[idx]`.

So `!s` is a *stateless ordinal re-index*: the box (`src/templates/bb/bb_iterate.cpp` → `rt_list_bang_at`, whose sole spelling is the asm twin in `rtx_icnagg.s`) asks for 0, 1, 2, … Delete the element returned at ordinal 0 and everything shifts down one, so ordinal 1 now names what used to be ordinal 2. **Neither function is wrong by itself; the generator protocol is.** Icon's own implementation walks the element, not the position, which is precisely why the language guarantees generation survives deleting the element just produced.

## ⛔ THE TWO OBVIOUS FIXES ARE BOTH WRONG, AND THAT IS THE USEFUL PART

1. **Snapshot the set when generation starts.** Passes this witness and is semantically WRONG: Icon does not generate an element deleted *before* it is reached, and a snapshot would produce it. The witness cannot tell the two apart — `gener` deletes ahead of the cursor as well, which is what makes it the honest grader here. **A fix validated only on the reduced witness would ship this.**
2. **Tombstone `ord` and let `nth(idx)` index positions instead of live elements.** Fixes the shift, then dies on the next case: a position that is dead needs to be SKIPPED, and a stateless `nth` has no way to say "skip, ask again" — `list_bang_at` returns 0/1, where 0 means *end of generation*. Returning the first live position `>= idx` re-introduces the shift by another route.

**Both fail for the same reason: the cursor lives in the caller and the truth lives in the callee.** The fix is to let `nth` advance the cursor — pass `int64_t *idx` so the runtime can skip dead positions and write back the position it actually consumed, with `ord` no longer compacting.

## ⚠ SCOPE, WHICH IS WHY I AM FILING RATHER THAN LANDING

`bb_iterate.cpp` serves **every** `!x` — lists, tables, sets, strings and files — and `rt_list_bang_at`'s only spelling is hand-written assembly (`rtx_icnagg.s`, the C original is a `rt_bomb` stub since s196). Changing the signature is an ABI change across a template, an asm twin and the runtime, on a SHARED node: it needs the full control-arm bar, not a one-file edit. ⭐ It is also **exactly the shape hq_U measured this morning** in *a hand-written asm twin drops a guard its C original has* — the twin is where a protocol change silently half-lands.

**Not claimed:** no cure attempted, nothing landed for it. The `gener` entry stays red and is now in the denominator (corpus `af179eebd`) rather than behind the `.xfail` marker that hid it. **The class is one bug behind at least two graded entries and one of them is not mine**, so it wants a single owner rather than two seats converging on it the way this one already was.
