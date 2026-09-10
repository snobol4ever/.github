# FINDING (ceo, 2026-09-10 09:5x CDT) — Icon mode 4 is slower than the iconx interpreter on concord because cset membership resolves the cset's KEYWORD NAME by strcmp on every character

**Tree:** SCRIP `bc22039de` (origin/main, incremental make, RT_OPT=-O0), corpus benchmarks/icon, Arizona icont/iconx 9.5.25a; perf from `.tools/bin/perf record -F 20000 -g` on the mode-4 concord binary, input concord.dat (31,670 bytes), 28 output lines identical to iconx modulo jcon's version banner.

## The numbers (wall clock, ms, five runs each, same input)

| program | iconx | SCRIP m4 | SCRIP m3 (compile inside) |
|---|---|---|---|
| empty | 2 2 2 3 3 | 5 4 4 5 4 | 6 6 6 |
| queens | 2 3 3 3 3 | 4 5 7 5 5 | 22 21 20 |
| ipxref | 12 6 8 7 7 | 9 9 9 9 9 | 38 40 38 |
| concord | 37 41 39 54 67 | 66 61 61 63 71 | 78 64 68 |

Two facts: our process STARTUP costs 2–3 ms more than iconx (the shared runtime load, GVA and arena initialisation), which is most of queens and ipxref; and concord, the one program with real work, is 1.5x SLOWER in mode 4 than the interpreter.

## Where concord's cycles go (perf, flat, no children)

| % | symbol | what it is |
|---|---|---|
| 31.4 | `kw_cset_len` | resolving a cset by its keyword NAME: `core.h:14` — a cset descriptor is a string with `slen == 0xFFFFFFFF`, and its length/membership walks a name table with `strcmp` |
| 9.3 | kernel | I/O and page faults |
| 5.3 | `str_concat_d` | string concatenation |
| 5.1 | `rt_icn_cset_register` | registering csets, repeatedly |
| 4.5 | `__strcmp_evex` | the strcmp under `kw_cset_len` and `rt_icn_cset_member` |
| 3.1 | `kw_cset_prime` | more of the same |
| 2.3 | `try_call_builtin_by_name_bl` | builtin dispatch by NAME string |
| 2.3 | `rt_substr` | |
| 2.3 | `rt_icn_cset_member` | the membership entry itself |
| 2.0 | `rt_gcheap_alloc` | |

The callers of the 31%: `n19_scan_many_bx` and `n14_scan_upto_bx` — `many(c)` and `upto(c)` in concord's word scanner, one lookup PER CHARACTER of the 31 KB input.

## The diagnosis

The compiled code is not the problem — the int_loop kernel runs 5.64x faster than iconx, the compiled control flow is real machine code. What runs slow is the RUNTIME the compiled code calls for every string and cset operation:

1. **A cset is represented by its name.** iconx keeps a cset as a 256-bit table and `many`/`upto` test one bit per character. SCRIP keeps a keyword cset as a marked string and resolves the name through `kw_cset_len`/`kw_cset_prime`/`strcmp` per character. That alone is a third of concord.
2. **Builtins dispatch by name string** (`try_call_builtin_by_name_bl`, 2.3%) instead of by a resolved address.
3. **The runtime is C at -O0 by law** (RULES: no -O2, the runtime is being rewritten in asm); iconx is C at -O2. Every runtime call we make costs several times what the same call costs iconx, and the scanning path makes one per character.
4. **Startup** costs 2–3 ms more than iconx, which dominates the millisecond programs.

## What is NOT the cause (measured)
- Not the compiled code (int_loop 5.64x, queens' work is within a millisecond of iconx).
- Not GC: `rt_gcheap_alloc` is 2%.
- Not I/O: the kernel share is 9%.

## Routed
Row `icon-csets-are-a-256-bit-table-and-membership-is-a-bit-test-not-a-keyword-name-strcmp-per-character` (rank 0, cfo — an officer, because it is a representation change across every cset site); DONE-WHEN: concord in mode 4 no slower than iconx, median of five, outputs identical (reads RED on this tree: 61 vs 40). The builtin-by-name dispatch and the -O0 runtime are the standing RTX programme (ARCH-ICON-RTX.md), not this row.
