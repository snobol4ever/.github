# TABLE rewritten: one hash ALGORITHM per datatype, contiguous hkey-sorted bucket, binary search, and the lookup in ASM

**hq_P, 2026-08-23 s262.** Lon's brief, verbatim: *"Rewrite the TABLE function: hash first by datatype then by
value, handle all datatypes, use contiguous array for bucket, grow the bucket by 2x or by fixed as needed, perform
binary search on lookup within each bucket."* Then: *"And then write it in ASM."*

## What shipped

- **One hash ALGORITHM per datatype**, not one extractor feeding a shared mixer. `_tbl_h_snul/_str/_int/_real/
  _arr/_tbl/_data/_ptr` in `aggregates.c`, each ending in its own multiply with its own constant, chosen for how
  that datatype's values are actually distributed (Fibonacci for consecutive integers; fold-then-multiply for
  doubles, whose entropy is all in the top half; djb2 + one finishing multiply for strings, whose low bits are
  weak when short; shift-off-the-alignment-bits for pointers). **No shared post-mix** — `_tbl_hkey` only prepends
  the tag byte. ⛔ An intermediate cut had eight *functions* but only two *algorithms*; Lon caught it. Dropping the
  shared avalanche was worth 5.4M Ir on its own.
- **hkey = (datatype << 56) | value-hash**, so the ordering is datatype-major and two keys of different type can
  never compare equal. `tab[17]`, `tab['17']` and `tab[17.0]` stay three distinct keys — oracle-confirmed.
- **Every datatype by value.** Not six: all of them. Aggregates hash their SERIAL ID (never the address — a
  pointer would make bucket layout ASLR-dependent and CONVERT's iteration order would differ run to run); every
  remaining tag hashes its payload word. **Nothing calls snprintf on a lookup any more.**
- **Contiguous, hkey-sorted bucket; hybrid search** — linear to 12, binary above. ⛔ Unconditional binary search
  cost **+26% Ir**: 256 buckets means ~2 entries each, and TBPAIR_t is 48 bytes, so every probe is an imul while
  a chain walk was one load.
- **Growth 2x while small, fixed +128 once large**, from a floor of **1**.
- **`rtx_table.S`** — the whole lookup in assembly: per-datatype hash arms, bucket index, both search arms,
  per-datatype equality. No frame, no spills, no call. Bails to C for DT_A/DT_T/DT_DATA only (they lazily assign
  file-static serial ids, and NO-NEW-GLOBALS forbids exporting those without a grant).
- **The printable key is lazy.** `e->key` is no longer built on insert — nothing on the hot path reads it, since
  equality compares `key_descr`. Worth ~22M Ir (12% of the integer kernel) on a program that never prints a key.
- **The string-keyed lookups are DELETED.** The old file could only *warn* that string-keyed and descriptor-keyed
  callers must not share a table. A warning is not a mechanism; there is now only one way to hash a key.

## Measured (RT_OPT=-O0 throughout; chained original = baseline)

**callgrind Ir at fixed work** (200 rebuilds x 500 integer keys):

| arm | Ir | vs baseline |
|---|---|---|
| chained baseline | 185,809,919 | — |
| C rewrite | 155,845,779 | **-16.1%** |
| + `rtx_table.S` ASM | **153,318,579** at cap-floor 4 / 155,845,779 at floor 1 | **-16.1%** |

**perf on the demo applications** (core code with the harness loop GUTTED, 5-run averages, real .dat inputs):

| demo | instructions | vs base | cycles | vs base | cache-misses |
|---|---|---|---|---|---|
| claws5 (TABLE of TABLE of TABLES) | 114.04M | **-3.9%** | 65.05M | +1.0% | 424K vs 362K |
| calculator-1 | 209.36M | -0.5% | 130.34M | +0.9% | 416K vs 409K |
| treebank-match | 48.20M | -0.7% | 47.91M | +2.8% | 217K vs 207K |
| porter | 2462.4M | -0.2% | 837.2M | +0.8% | 780K vs 795K |

**Instructions are down everywhere. Cycles are up ~1-3%** — the rewrite touches more memory than the chain it
replaced, and on these demos that cancels the instruction win. Wall-clock differences are inside the run-to-run
spread on this box (baseline claws5 alone ranged 14.4-18.5ms across runs). The honest summary: **a large win where
tables dominate, a wash on the demos, and an open cache-footprint gap on CLAWS.**

## Correctness

Oracle `sbl -bf` byte-for-byte on integer / string / real / null / negative / zero / table-as-key / array-as-key /
cross-type distinctness / overwrite-in-place / miss, with the ASM gate ON and OFF (and the two arms identical to
each other). Corpus **m3 357/359, m4 355/359 + 2 SKIP** — the 2 FAILs are the standing reds. All 23 demo programs
byte-identical to baseline with their real inputs.

## Three measurement traps hit on the way, all recorded because all three looked like answers

1. **A sweep whose builds failed.** Changing `TABLE_BUCKETS` without updating the `_Static_assert` that pinned it
   made `make` fail, so every arm silently re-measured the *same* binary. The differing wall-clock numbers were
   pure noise presented as a result. **Check the build before believing the measurement.**
2. **Wall-clock cannot resolve a 3% effect here** — one binary ranged 6,144..8,704 iters run to run.
3. ⛔ **callgrind Ir is BLIND to memset/memcpy size**: `rep stosb` is one instruction whatever the length. An
   intermediate cut doubled `TBBLK_t` to 4,160 bytes and Ir said it was FREE, while perf said CLAWS lost 7.4% in
   cycles with IPC falling 1.84 -> 1.65. **Ir and cycles answer different questions; a footprint change needs perf.**
   Cured by moving `len`/`cap` out of the bucket vector into the entry block, so a bucket is a bare pointer again.

## Also cured, as a consequence

`VCELL_t.cellp` is no longer `&e->val` for any table arm. Per Lon: *"we should never have in our code a place that
depends on that pointer not moving."* Table cells now name `(tbl, key_descr)` and re-resolve — which also applies
the table's DEFAULT on a miss, which the raw pointer never did — and it deleted a whole redundant lookup from
every table subscript. `rtx_icnsub.S`'s RTX-26/29 DT_T arms are retired as obsolete: their only job was computing
that address. See the companion FINDING on the collector, whose half hq_C is taking.
